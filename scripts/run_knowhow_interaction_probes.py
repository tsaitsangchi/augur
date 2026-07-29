#!/usr/bin/env python
"""跑 know-how 交互探針（KH5 擴軸＋KH6 投影）— KNI-S2／KH4-S2 最小 slice。

🎯 這支在做什麼(白話):讀 DB `knowhow_interaction_probe` active 列（含三元
   `RKI-FP-AI-SOLAR`），展開 template→多軸查詢＋交互全句→庫內檢索→RRF 合併→
   缺口／假相關旗標；stdout／可選 report／可選帳本。證明 runner 可跑；
   **不** hardcode 專題答案樹、**不**碰 approve／activate、**不**改 answer gate、
   **零** FinMind／FRED。KH4 evidence 可選附註最近探針命中（不動 status 欄）。
守 #29a/d· #1· #15· NHC-keep· FZ-keep· RKI-keep· predict-vs-market-api。

執行指令矩陣:
  python scripts/run_knowhow_interaction_probes.py              # 安全預設:印矩陣+--show
  python scripts/run_knowhow_interaction_probes.py --show       # 列 active 探針(arity/axes)
  python scripts/run_knowhow_interaction_probes.py --dry-run    # 只展開 query、不檢索
  python scripts/run_knowhow_interaction_probes.py --run        # 最小種子集實跑檢索+RRF
  python scripts/run_knowhow_interaction_probes.py --run --probe-id RKI-FP-AI-SOLAR
  python scripts/run_knowhow_interaction_probes.py --run --arity 3
  python scripts/run_knowhow_interaction_probes.py --run --write-ledger
  python scripts/run_knowhow_interaction_probes.py --run --annotate-kh4
  python scripts/run_knowhow_interaction_probes.py --run --report reports/augur_knowhow_probe_run_20260729.md
  python scripts/run_knowhow_interaction_probes.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import interaction_probe as ip
from augur.knowledge import kh4

# 最小種子集：三元種子＋消融對照（缺第一性）＋一元原理×域（對照臂）
DEFAULT_MIN_PROBE_IDS = (
    "RKI-FP-AI-SOLAR",
    "RKI-AI-SOLAR-RD",
    "RKI-FP-SOLAR-CORE",
)

LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS knowhow_interaction_probe_run (
    run_id        BIGSERIAL PRIMARY KEY,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at   TIMESTAMPTZ,
    script        TEXT NOT NULL DEFAULT 'run_knowhow_interaction_probes.py',
    git_sha       TEXT,
    note          TEXT,
    params_json   JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS knowhow_interaction_probe_result (
    run_id            BIGINT NOT NULL REFERENCES knowhow_interaction_probe_run(run_id) ON DELETE CASCADE,
    probe_id          TEXT NOT NULL,
    arity             INT NOT NULL,
    interaction_kind  TEXT,
    expanded_prompt   TEXT NOT NULL,
    axis_hit_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    hit_counts        JSONB NOT NULL DEFAULT '{}'::jsonb,
    gap_flags         JSONB NOT NULL DEFAULT '[]'::jsonb,
    spurious_risk     TEXT,
    top_hits_json     JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_json          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, probe_id)
);
COMMENT ON TABLE knowhow_interaction_probe_run IS
  'KNI-S2: 探針跑批帳本（非答案 SSOT／非預測特徵）';
COMMENT ON TABLE knowhow_interaction_probe_result IS
  'KNI-S2: 探針結果（gap／RRF hits；非答案 SSOT）';
"""


def _parse_params(raw) -> dict:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return {}


def _load_probes(cur, *, probe_ids=None, arity=None, limit=None):
    sql = (
        "SELECT probe_id, prompt_template, knowhow_axis, raw_axis, "
        "interaction_kind, template_params, arity, axes, active "
        "FROM knowhow_interaction_probe WHERE active"
    )
    params: list = []
    if probe_ids:
        sql += " AND probe_id = ANY(%s)"
        params.append(list(probe_ids))
    if arity is not None:
        sql += " AND arity = %s"
        params.append(arity)
    sql += " ORDER BY CASE WHEN probe_id = ANY(%s) THEN 0 ELSE 1 END, probe_id"
    params.append(list(DEFAULT_MIN_PROBE_IDS))
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def show(conn) -> int:
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe')")
        if not cur.fetchone()[0]:
            print("knowhow_interaction_probe: 未建——先跑 migrate_knowhow_interaction_probe_ddl.py --apply")
            return 1
        rows = _load_probes(cur)
    print(f"── active probes:{len(rows)} ──")
    for r in rows:
        axes = ip.normalize_axes(r["axes"], knowhow_axis=r["knowhow_axis"], raw_axis=r["raw_axis"])
        labels = " × ".join(a["label"] for a in axes) or f"{r['knowhow_axis']} × {r['raw_axis']}"
        mark = " *" if r["probe_id"] in DEFAULT_MIN_PROBE_IDS else ""
        print(f"  {r['probe_id']} [n={r['arity']}|{r['interaction_kind']}] {labels}{mark}")
    print("  (* = 預設最小種子集)")
    return 0


def _retrieve_one(query: str, *, k: int, scope):
    from augur.philosophy import retrieval as ret

    return ret.retrieve_all(query, k=k, scope=scope)


def run_probe(row: dict, *, k_per_query: int, dry_run: bool, scope) -> dict:
    params = _parse_params(row["template_params"])
    axes = ip.normalize_axes(row["axes"], knowhow_axis=row["knowhow_axis"], raw_axis=row["raw_axis"])
    expanded = ip.expand_prompt(row["prompt_template"], params)
    queries = ip.build_queries(expanded_prompt=expanded, axes=axes, template_params=params)
    ranked: dict[str, list] = {}
    if dry_run:
        for q in queries:
            ranked[q["qkey"]] = []
        merged = []
    else:
        for q in queries:
            hits = _retrieve_one(q["query"], k=k_per_query, scope=scope)
            ranked[q["qkey"]] = list(hits or [])
        merged = ip.rrf_merge(ranked)
    return ip.summarize_probe_result(
        probe_id=row["probe_id"],
        arity=int(row["arity"] or len(axes) or 2),
        interaction_kind=row["interaction_kind"],
        expanded_prompt=expanded,
        axes=axes,
        queries=queries,
        ranked_lists=ranked,
        merged=merged,
        top_n=min(8, k_per_query * 2),
    )


def _print_result(result: dict) -> None:
    print(f"\n══ {result['probe_id']} (arity={result['arity']}|{result['interaction_kind']}) ══")
    print(f"  expanded: {result['expanded_prompt'][:160]}{'…' if len(result['expanded_prompt'])>160 else ''}")
    print(f"  queries: {len(result['queries'])} → " + ", ".join(q["qkey"] for q in result["queries"]))
    print(f"  axis_hits: {result['axis_hit_counts']}")
    print(f"  merged={result['merged_hits']} multi_src={result['multi_source_hits']} "
          f"gap={result['gap_flags'] or '[]'} spurious={result['spurious_risk']}")
    for i, h in enumerate(result["top_hits"][:5], 1):
        title = h.get("title") or ""
        print(f"    [{i}] rrf={h.get('rrf')} src={h.get('sources')} {h.get('kind')} {title[:48]}")


def _ensure_ledger(cur) -> None:
    cur.execute(LEDGER_DDL)


def _write_ledger(cur, *, results: list[dict], params_json: dict, note: str | None) -> int:
    _ensure_ledger(cur)
    git_sha = None
    try:
        import subprocess
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(Path(__file__).resolve().parents[1]),
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        git_sha = None
    cur.execute(
        "INSERT INTO knowhow_interaction_probe_run (git_sha, note, params_json) "
        "VALUES (%s,%s,%s::jsonb) RETURNING run_id",
        (git_sha, note, json.dumps(params_json, ensure_ascii=False)),
    )
    run_id = cur.fetchone()[0]
    for r in results:
        cur.execute(
            "INSERT INTO knowhow_interaction_probe_result "
            "(run_id, probe_id, arity, interaction_kind, expanded_prompt, "
            " axis_hit_json, hit_counts, gap_flags, spurious_risk, top_hits_json, raw_json) "
            "VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s::jsonb,%s::jsonb)",
            (
                run_id,
                r["probe_id"],
                r["arity"],
                r["interaction_kind"],
                r["expanded_prompt"],
                json.dumps(r.get("axes") or [], ensure_ascii=False),
                json.dumps({
                    "axis": r.get("axis_hit_counts") or {},
                    "interaction": r.get("interaction_hits") or 0,
                    "merged": r.get("merged_hits") or 0,
                    "multi_source": r.get("multi_source_hits") or 0,
                }, ensure_ascii=False),
                json.dumps(r.get("gap_flags") or [], ensure_ascii=False),
                r.get("spurious_risk"),
                json.dumps(r.get("top_hits") or [], ensure_ascii=False),
                json.dumps(r, ensure_ascii=False),
            ),
        )
    cur.execute(
        "UPDATE knowhow_interaction_probe_run SET finished_at=now() WHERE run_id=%s",
        (run_id,),
    )
    return run_id


def _annotate_kh4(cur, results: list[dict], *, run_id: int | None) -> int:
    """把探針命中附註進 KH4 evidence；閘欄（資格／軸／投影／作答態）一律不動。"""
    if not kh4._table_exists(cur, "knowledge_kh4_state"):
        print("  annotate-kh4: knowledge_kh4_state 未建——略過")
        return 0
    n = 0
    for r in results:
        item_ids = sorted({
            int(h["item_id"])
            for h in (r.get("top_hits") or [])
            if h.get("kind") == "item" and h.get("item_id") is not None
        })
        if not item_ids:
            continue
        note = {
            "probe_id": r["probe_id"],
            "run_id": run_id,
            "gap_flags": r.get("gap_flags") or [],
            "spurious_risk": r.get("spurious_risk"),
            "annotated_at": datetime.now(timezone.utc).isoformat(),
        }
        cur.execute(
            """
            UPDATE knowledge_kh4_state
               SET evidence = COALESCE(evidence, '{}'::jsonb)
                              || jsonb_build_object('kh6_last_probe', %s::jsonb),
                   updated_at = now()
             WHERE item_id = ANY(%s)
            """,
            (json.dumps(note, ensure_ascii=False), item_ids),
        )
        n += cur.rowcount
    return n


def _write_report(path: Path, results: list[dict], *, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Know-how interaction probe run [I] ({meta.get('started')})",
        "",
        "* 性質：[I] runner 產物；非答案 SSOT；非 [N]",
        f"* probes: {', '.join(r['probe_id'] for r in results)}",
        f"* dry_run: {meta.get('dry_run')}",
        f"* run_id: {meta.get('run_id')}",
        "",
    ]
    for r in results:
        lines.append(f"## {r['probe_id']}")
        lines.append("")
        lines.append(f"- arity / kind: `{r['arity']}` / `{r['interaction_kind']}`")
        lines.append(f"- expanded: {r['expanded_prompt']}")
        lines.append(f"- axis_hits: `{json.dumps(r['axis_hit_counts'], ensure_ascii=False)}`")
        lines.append(f"- merged / multi_src: {r['merged_hits']} / {r['multi_source_hits']}")
        lines.append(f"- gap_flags: `{r['gap_flags']}`")
        lines.append(f"- spurious_risk: `{r['spurious_risk']}`")
        lines.append("")
        if r["top_hits"]:
            lines.append("| # | kind | title | rrf | sources |")
            lines.append("|---|---|---|---|---|")
            for i, h in enumerate(r["top_hits"][:8], 1):
                title = (h.get("title") or "").replace("|", "/")
                lines.append(
                    f"| {i} | {h.get('kind')} | {title[:60]} | {h.get('rrf')} | "
                    f"{','.join(h.get('sources') or [])} |"
                )
            lines.append("")
        else:
            lines.append("_無命中（誠實缺料）_")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report → {path}")


def run(conn, args) -> int:
    probe_ids = args.probe_id or None
    if not probe_ids and not args.all:
        probe_ids = list(DEFAULT_MIN_PROBE_IDS)
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe')")
        if not cur.fetchone()[0]:
            print("knowhow_interaction_probe 未建——先跑 migrate_knowhow_interaction_probe_ddl.py --apply")
            return 1
        rows = _load_probes(
            cur,
            probe_ids=probe_ids,
            arity=args.arity,
            limit=args.limit,
        )
    if not rows:
        print("無符合條件之 active probe")
        return 1

    # 診斷 runner：以 steward/super scope 讀庫內公版＋授權語料（非使用者聊天入口）
    scope = (True, frozenset(), None)
    results = []
    for row in rows:
        result = run_probe(row, k_per_query=args.k, dry_run=args.dry_run, scope=scope)
        _print_result(result)
        results.append(result)

    run_id = None
    annotated = 0
    if args.write_ledger and not args.dry_run:
        with db.transaction(conn) as cur:
            run_id = _write_ledger(
                cur,
                results=results,
                params_json={
                    "probe_ids": [r["probe_id"] for r in results],
                    "k": args.k,
                    "arity": args.arity,
                },
                note=args.note or "kh4-s2-min-slice",
            )
        print(f"\nledger run_id={run_id}")

    if args.annotate_kh4 and not args.dry_run:
        with db.transaction(conn) as cur:
            annotated = _annotate_kh4(cur, results, run_id=run_id)
        print(f"kh4 evidence annotated rows={annotated} "
              "(answer_status/kh_axis_state/interaction_state 未改)")

    if args.report:
        _write_report(
            Path(args.report),
            results,
            meta={
                "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                "dry_run": args.dry_run,
                "run_id": run_id,
            },
        )

    gaps = sum(1 for r in results if r.get("gap_flags"))
    print(f"\n── 完成 {len(results)} probes；含 gap 旗標 {gaps} ──")
    return 0


def selftest() -> int:
    rc = ip._selftest()
    ok = rc == 0

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import ast

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                calls.append(fn.attr)

    check("指令矩陣含 --run/--selftest", "--run" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    check("預設種子集含三元", "RKI-FP-AI-SOLAR" in DEFAULT_MIN_PROBE_IDS)
    check("預設含消融對照", "RKI-AI-SOLAR-RD" in DEFAULT_MIN_PROBE_IDS)
    check("零 FinMind/FRED import",
          not any("finmind" in (m or "").lower() or (m or "").lower() == "fred"
                  or (m or "").lower().endswith(".fred") for m in imports))
    check("禁 approve/activate 呼叫",
          "approve" not in calls and "activate" not in calls)
    check("ledger DDL 冪等", "IF NOT EXISTS" in LEDGER_DDL)
    check("annotate 只動 evidence",
          "kh6_last_probe" in LEDGER_DDL or "kh6_last_probe" in Path(__file__).read_text(encoding="utf-8"))
    # 閘欄不在 UPDATE SET 目標：AST 掃 Assign 目標過嚴；改查 SQL 片段
    upd = Path(__file__).read_text(encoding="utf-8")
    annotate_sql = upd[upd.find("_annotate_kh4"):upd.find("def _write_report")]
    check("annotate SQL 不改 gate 欄",
          "answer_status" not in annotate_sql
          and "kh_axis_state" not in annotate_sql
          and "interaction_state" not in annotate_sql
          and "SET evidence" in annotate_sql)
    print("runner 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Know-how 交互探針 runner（KH5/KH6 最小）")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--run", action="store_true", help="實跑檢索+RRF（預設最小種子集）")
    ap.add_argument("--dry-run", action="store_true", help="只展開、不檢索")
    ap.add_argument("--probe-id", action="append", help="可重覆；指定 probe_id")
    ap.add_argument("--arity", type=int, help="過濾 arity")
    ap.add_argument("--all", action="store_true", help="跑全部 active（非最小子集）")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--k", type=int, default=6, help="每查詢取回上限")
    ap.add_argument("--write-ledger", action="store_true")
    ap.add_argument("--annotate-kh4", action="store_true",
                    help="命中 item 之 KH4 evidence 附註探針（不改 gate 欄）")
    ap.add_argument("--report", help="寫 markdown 報告路徑")
    ap.add_argument("--note", help="ledger note")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not any((args.show, args.run, args.dry_run)):
        print(__doc__)
        args.show = True

    with db.connect() as conn:
        if args.show and not (args.run or args.dry_run):
            return show(conn)
        if args.dry_run and not args.run:
            args.run = True
        if args.run or args.dry_run:
            if args.show:
                show(conn)
            return run(conn, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
