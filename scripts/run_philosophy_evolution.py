#!/usr/bin/env python
"""哲學↔市場進化編排 — PME S2 骨架：寫 evolution_run＋閘證據＋promotion_queue（零市場 API）。

🎯 這支在做什麼（白話）：一鍵建立可重現 run 帳本、覆蓋快照、逐 map 組 gate_json，並寫入
   晉升佇列。預設 **skeleton**：G-PROM／G-ECON 誠實 SKIP（FZ-keep／未跑重驗 ≠ PASS），
   故不會誤自動上線。加 --with-local-evidence 時僅讀既有 validated_*（仍零 API）；
   完整 verify／#14 重算另走既有腳本（本輪不強制放量）。禁 FinMind／FRED。

守 #1 #14 #15 #29；計畫 §4 S2／§4.1；PME-AUTO-B＋FZ-keep。

執行指令矩陣:
  python scripts/run_philosophy_evolution.py                 # 印用途（安全預設）
  python scripts/run_philosophy_evolution.py --skeleton      # S2 骨架：run＋coverage＋queue（SKIP 重閘）
  python scripts/run_philosophy_evolution.py --skeleton --with-local-evidence
  python scripts/run_philosophy_evolution.py --dry-run       # 只印、不寫 DB
  python scripts/run_philosophy_evolution.py --selftest      # 免 DB
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    DEFAULT_GATE_CONFIG,
    KILL_CLEAR,
    KILL_HALT,
    attest_complete,
    build_gate_json,
    classify_coverage,
    decide_queue_status,
    map_action_from_evidence,
    normalize_kill_state,
    scan_noexec_text,
)


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # 本腳本自身 G-NOEXEC
    text = Path(__file__).read_text(encoding="utf-8")
    chk("script G-NOEXEC clean", scan_noexec_text(text) == [])
    chk("skeleton SKIP ≠ enqueue promote green", True)  # 語意鎖：見 decide
    g = build_gate_json(
        g_iso={"verdict": "PASS"},
        g_map={"verdict": "PASS"},
        g_prom={"verdict": "SKIP", "reason": "skeleton"},
        g_econ={"verdict": "SKIP", "reason": "FZ-keep"},
        g_attest={"verdict": "PASS"},
        g_kill={"verdict": "PASS"},
        g_noexec={"verdict": "PASS"},
    )
    chk("skeleton → rejected_gate", decide_queue_status(g, KILL_CLEAR) == "rejected_gate")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _code_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:64]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def _g_iso() -> dict:
    from augur.audit.import_isolation import check_isolation

    v = check_isolation()
    return {"verdict": "PASS" if not v else "FAIL", "n_violations": len(v)}


def _g_noexec() -> dict:
    """掃 APPLY／編排入口；evolution.py 為偵測器本體、不掃（對齊 import_isolation 自排除）。"""
    root = Path(__file__).resolve().parents[1]
    targets = [
        root / "scripts" / "apply_evolution_promotions.py",
        root / "scripts" / "run_philosophy_evolution.py",
        root / "scripts" / "set_evolution_kill_switch.py",
    ]
    hits = []
    for p in targets:
        if p.exists():
            hits.extend(scan_noexec_text(p.read_text(encoding="utf-8")))
    return {"verdict": "PASS" if not hits else "FAIL", "hits": hits}


def _load_maps(cur):
    cur.execute(
        """
        SELECT m.map_id, m.principle_id, m.feature, m.direction,
               m.validated_ic, m.validated_econ,
               EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature = m.feature) AS in_fv
        FROM principle_factor_map m
        ORDER BY m.feature, m.principle_id
        """
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _prom_econ_evidence(row: dict, *, with_local: bool) -> tuple[dict, dict]:
    """G-PROM／G-ECON：skeleton 預設 SKIP；--with-local-evidence 僅看既有 validated_*。"""
    if not with_local:
        return (
            {"verdict": "SKIP", "reason": "skeleton; run verify_candidate_promotion for PASS"},
            {"verdict": "SKIP", "reason": "FZ-keep/skeleton; run_economic_eval for PASS"},
        )
    # 本地已有回填：有數字≠提拔三關全過——仍標 SKIP 並附證據，禁謊稱 G-PROM PASS
    prom = {
        "verdict": "SKIP",
        "reason": "local validated_ic present but promotion triad not re-run this pass",
        "validated_ic": row.get("validated_ic"),
    }
    econ = {
        "verdict": "SKIP",
        "reason": "local validated_econ present but #14 gate thresholds not re-eval this pass",
        "validated_econ": row.get("validated_econ"),
    }
    if row.get("validated_ic") is None:
        prom = {"verdict": "SKIP", "reason": "no validated_ic; blocked or never verified"}
    if row.get("validated_econ") is None:
        econ = {"verdict": "SKIP", "reason": "no validated_econ; FZ-keep or never verified"}
    return prom, econ


def run_skeleton(
    *,
    since: str,
    horizon_h: int,
    dry_run: bool,
    with_local: bool,
) -> int:
    from augur.core import db

    cfg = dict(DEFAULT_GATE_CONFIG)
    cfg["mode"] = "skeleton"
    cfg["with_local_evidence"] = with_local
    cfg["since"] = since
    cfg["horizon_h"] = horizon_h
    sha = _code_sha()
    g_iso = _g_iso()
    g_noexec = _g_noexec()
    attest_ok = attest_complete(
        code_sha=sha, since_date=since, horizon_h=horizon_h, config_json=cfg
    )
    g_attest = {
        "verdict": "PASS" if attest_ok else "FAIL",
        "code_sha": sha,
        "since": since,
        "horizon_h": horizon_h,
    }

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_run')")
        if cur.fetchone()[0] is None:
            print("✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id=1")
        row = cur.fetchone()
        kill_db = row[0] if row else KILL_CLEAR
        kill_eff = normalize_kill_state(kill_db, env_halt=_env_halt())
        g_kill = {
            "verdict": "PASS" if kill_eff == KILL_CLEAR else "FAIL",
            "state": kill_eff,
            "db": kill_db,
        }
        maps = _load_maps(cur)

    # 覆蓋彙總（寫入前先算）
    feat_class: dict[str, str] = {}
    for m in maps:
        feat_class[m["feature"]] = classify_coverage(
            m["feature"], in_feature_values=bool(m["in_fv"])
        )

    print("── PME S2 skeleton ──")
    print(f"  maps={len(maps)} kill={kill_eff} G-ISO={g_iso['verdict']} G-NOEXEC={g_noexec['verdict']}")
    print(f"  G-ATTEST={g_attest['verdict']} dry_run={dry_run} with_local={with_local}")
    print("  ⚠ G-PROM／G-ECON=SKIP（skeleton／FZ-keep）→ 不會 pending_auto 上線")

    if dry_run:
        sample = maps[:3]
        for m in sample:
            cls = feat_class[m["feature"]]
            g_map = {
                "verdict": "PASS" if cls == "mapped" else "FAIL",
                "coverage_class": cls,
            }
            g_prom, g_econ = _prom_econ_evidence(m, with_local=with_local)
            gj = build_gate_json(
                g_iso=g_iso,
                g_map=g_map,
                g_prom=g_prom,
                g_econ=g_econ,
                g_attest=g_attest,
                g_kill=g_kill,
                g_noexec=g_noexec,
            )
            qs = decide_queue_status(gj, kill_eff)
            print(f"  dry {m['feature']}: class={cls} queue→{qs}")
        return 0

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            """
            INSERT INTO evolution_run
              (since_date, horizon_h, code_sha, config_json, status, kill_switch_at_start, notes)
            VALUES (%s, %s, %s, %s::jsonb, 'running', %s, %s)
            RETURNING run_id
            """,
            (date.fromisoformat(since), horizon_h, sha, json.dumps(cfg), kill_eff, "S2 skeleton"),
        )
        run_id = cur.fetchone()[0]

        # coverage distinct features
        seen = set()
        for m in maps:
            f = m["feature"]
            if f in seen:
                continue
            seen.add(f)
            cls = feat_class[f]
            n_maps = sum(1 for x in maps if x["feature"] == f)
            cur.execute(
                """
                INSERT INTO evolution_coverage_snapshot
                  (run_id, feature, map_count, in_feature_values, coverage_class, detail)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    run_id,
                    f,
                    n_maps,
                    bool(m["in_fv"]),
                    cls,
                    json.dumps({"phase": "S2-skeleton"}),
                ),
            )

        n_pending = n_rej = n_halt = 0
        for m in maps:
            cls = feat_class[m["feature"]]
            g_map = {
                "verdict": "PASS" if cls == "mapped" else "FAIL",
                "coverage_class": cls,
                "in_feature_values": bool(m["in_fv"]),
            }
            g_prom, g_econ = _prom_econ_evidence(m, with_local=with_local)
            gj = build_gate_json(
                g_iso=g_iso,
                g_map=g_map,
                g_prom=g_prom,
                g_econ=g_econ,
                g_attest=g_attest,
                g_kill=g_kill,
                g_noexec=g_noexec,
            )
            qs = decide_queue_status(gj, kill_eff)
            action = map_action_from_evidence(
                coverage_class=cls,
                g_prom_pass=g_prom.get("verdict") == "PASS",
                g_econ_pass=g_econ.get("verdict") == "PASS",
            )
            cur.execute(
                """
                INSERT INTO promotion_queue
                  (run_id, principle_id, feature, action, gate_json, queue_status, decided_by)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s,'evolution_engine')
                """,
                (run_id, m["principle_id"], m["feature"], action, json.dumps(gj), qs),
            )
            if qs == "pending_auto":
                n_pending += 1
            elif qs == "halted":
                n_halt += 1
            else:
                n_rej += 1

        final = "halted" if kill_eff == KILL_HALT else "succeeded"
        cur.execute(
            "UPDATE evolution_run SET finished_at=now(), status=%s WHERE run_id=%s",
            (final, run_id),
        )

    print(f"✓ run_id={run_id} status={final} queue pending={n_pending} rejected={n_rej} halted={n_halt}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--skeleton", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--with-local-evidence", action="store_true")
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.skeleton and not args.dry_run:
        print((__doc__ or "").split("🎯")[0].strip())
        print("安全預設：請顯式 --skeleton 或 --dry-run（或 --selftest）")
        print("例: python scripts/run_philosophy_evolution.py --skeleton")
        return 0
    return run_skeleton(
        since=args.since,
        horizon_h=args.h,
        dry_run=bool(args.dry_run),
        with_local=args.with_local_evidence,
    )


if __name__ == "__main__":
    raise SystemExit(main())
