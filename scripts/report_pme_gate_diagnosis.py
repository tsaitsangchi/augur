#!/usr/bin/env python
"""PME 閘診斷帳 — MAP-E012 S0（唯讀 DB、零市場 API）。

🎯 這支在做什麼（白話）：交叉 principle_factor_map × feature_values × 最近 evolution
   promotion_queue gate_json，產出可重跑診斷：coverage（mapped／missing／blocked_div）、
   G-PROM／G-ECON verdict、ECON-only、unmapped-in-fv、missing 可建性標籤。寫 reports/ 或 stdout。
   不改閾值、不手改 validated_*、不跑閘。

守 #1 #15 #29；計畫 MAP §3 S0／§6 A1；FZ-keep／GATE-keep。

執行指令矩陣:
  python scripts/report_pme_gate_diagnosis.py              # 印診斷＋寫 reports/
  python scripts/report_pme_gate_diagnosis.py --stdout-only  # 只印不寫檔
  python scripts/report_pme_gate_diagnosis.py --run-id 6    # 指定 run（預設 max）
  python scripts/report_pme_gate_diagnosis.py --selftest    # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import BLOCKED_DIV_FEATURES, classify_coverage

# S0 可建性：庫內 raw 探針標籤（非閘結果；#1 算不出仍缺列）
BUILDABILITY = {
    "roe": "db_buildable",          # FS NetIncome + BS Equity + release_lag
    "debt_ratio": "db_buildable",   # BS Liabilities / TotalAssets + release_lag
    "peg_ratio": "deferred_growth", # 需成長代理；本輪不硬建
    "piotroski_fscore": "deferred_complex",  # 9 訊號；禁一次幻造
    "macro_regime": "blocked_fz",   # FZ-keep／常涉 FRED
}


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("blocked_div", classify_coverage("dividend_yield", in_feature_values=True) == "blocked_div")
    chk("missing", classify_coverage("roe", in_feature_values=False) == "missing")
    chk("mapped", classify_coverage("pe_ratio", in_feature_values=True) == "mapped")
    chk("buildability roe", BUILDABILITY["roe"] == "db_buildable")
    chk("buildability macro blocked", BUILDABILITY["macro_regime"] == "blocked_fz")
    # ECON-only helper
    rows = [
        {"feature": "a", "g_prom": "FAIL", "g_econ": "PASS"},
        {"feature": "b", "g_prom": "PASS", "g_econ": "PASS"},
    ]
    econ_only = [r["feature"] for r in rows if r["g_prom"] == "FAIL" and r["g_econ"] == "PASS"]
    chk("econ_only extract", econ_only == ["a"])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _verdict(gj: dict | None, gate: str) -> str:
    if not gj or not isinstance(gj, dict):
        return "ABSENT"
    g = gj.get(gate) or {}
    if isinstance(g, str):
        return g
    return str(g.get("verdict") or "ABSENT")


def _reason(gj: dict | None, gate: str) -> str:
    if not gj or not isinstance(gj, dict):
        return ""
    g = gj.get(gate) or {}
    if not isinstance(g, dict):
        return ""
    return str(g.get("reason") or g.get("detail") or "")[:200]


def diagnose(cur, run_id: int | None) -> dict:
    if run_id is None:
        cur.execute("SELECT max(run_id) FROM evolution_run")
        run_id = cur.fetchone()[0]
    out: dict = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": run_id,
        "boundaries": {
            "fz_keep": True,
            "gate_keep": True,
            "tradable": False,
            "established_grade": False,
        },
    }

    cur.execute(
        """
        SELECT m.feature, count(*) AS map_count,
               EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature = m.feature) AS in_fv
        FROM principle_factor_map m
        GROUP BY m.feature
        ORDER BY m.feature
        """
    )
    cov_rows = []
    for feature, map_count, in_fv in cur.fetchall():
        cls = classify_coverage(feature, in_feature_values=bool(in_fv))
        cov_rows.append({
            "feature": feature,
            "map_count": int(map_count),
            "in_feature_values": bool(in_fv),
            "coverage_class": cls,
            "buildability": BUILDABILITY.get(feature, "n/a" if cls == "mapped" else "unknown"),
        })
    out["coverage"] = cov_rows
    out["coverage_tallies"] = dict(Counter(r["coverage_class"] for r in cov_rows))

    cur.execute(
        """
        SELECT DISTINCT fv.feature
        FROM feature_values fv
        WHERE NOT EXISTS (
          SELECT 1 FROM principle_factor_map m WHERE m.feature = fv.feature
        )
        ORDER BY 1
        """
    )
    out["unmapped_in_fv"] = [r[0] for r in cur.fetchall()]

    gate_rows = []
    cross: Counter[tuple[str, str]] = Counter()
    econ_only_feats: set[str] = set()
    if run_id is not None:
        cur.execute(
            """
            SELECT principle_id, feature, gate_json, queue_status
            FROM promotion_queue WHERE run_id=%s
            ORDER BY feature, principle_id
            """,
            (run_id,),
        )
        for pid, feature, gj, qstatus in cur.fetchall():
            if isinstance(gj, str):
                gj = json.loads(gj)
            gp, ge = _verdict(gj, "G-PROM"), _verdict(gj, "G-ECON")
            cross[(gp, ge)] += 1
            if gp == "FAIL" and ge == "PASS":
                econ_only_feats.add(feature)
            gate_rows.append({
                "principle_id": int(pid),
                "feature": feature,
                "queue_status": qstatus,
                "g_prom": gp,
                "g_econ": ge,
                "g_prom_reason": _reason(gj, "G-PROM"),
                "g_econ_reason": _reason(gj, "G-ECON"),
                "econ_only": gp == "FAIL" and ge == "PASS",
            })
    out["gate_rows"] = gate_rows
    out["gate_cross"] = {f"{a}×{b}": n for (a, b), n in sorted(cross.items())}
    out["econ_only_features"] = sorted(econ_only_feats)
    out["blocked_div_const"] = sorted(BLOCKED_DIV_FEATURES)
    out["missing_buildability"] = {
        r["feature"]: r["buildability"]
        for r in cov_rows
        if r["coverage_class"] == "missing"
    }
    return out


def render_markdown(d: dict) -> str:
    lines = [
        f"# PME 閘診斷帳 [I]（{date.today().isoformat()}）",
        "",
        f"* run_id={d.get('run_id')} · as_of={d.get('as_of')} · 唯讀 · FZ-keep／GATE-keep",
        f"* coverage_tallies={d.get('coverage_tallies')}",
        f"* gate_cross={d.get('gate_cross')}",
        f"* unmapped_in_fv n={len(d.get('unmapped_in_fv') or [])}",
        f"* econ_only_features={d.get('econ_only_features')}",
        f"* missing_buildability={d.get('missing_buildability')}",
        "",
        "## 邊界",
        "",
        "- ≠可交易／≠確立級；本檔不跑閘、不降閾、不手改 validated_*",
        "- blocked_div／Dividend 另帳；macro_regime＝blocked_fz",
        "",
        "## Coverage（map 特徵級）",
        "",
        "| feature | class | maps | in_fv | buildability |",
        "|---|---|---|---|---|",
    ]
    for r in d.get("coverage") or []:
        lines.append(
            f"| `{r['feature']}` | {r['coverage_class']} | {r['map_count']} | "
            f"{r['in_feature_values']} | {r['buildability']} |"
        )
    lines += [
        "",
        "## Unmapped-in-fv（S1 主彈藥）",
        "",
    ]
    for f in d.get("unmapped_in_fv") or []:
        lines.append(f"- `{f}`")
    lines += ["", "## ECON-only 特徵（禁 APPLY）", ""]
    for f in d.get("econ_only_features") or []:
        lines.append(f"- `{f}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PME MAP-E012 S0 閘診斷帳")
    ap.add_argument("--run-id", type=int, default=None)
    ap.add_argument("--stdout-only", action="store_true")
    ap.add_argument("--json", action="store_true", help="stdout JSON（可與寫檔並存）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    from augur.core import db

    if not db.ping():
        print("SKIP: DB 不可達（誠實；非 PASS）", file=sys.stderr)
        return 2

    with db.connect() as conn, db.transaction(conn) as cur:
        d = diagnose(cur, args.run_id)

    md = render_markdown(d)
    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    else:
        print(md)

    if not args.stdout_only:
        root = Path(__file__).resolve().parent.parent
        reports = root / "reports"
        reports.mkdir(exist_ok=True)
        stamp = date.today().strftime("%Y%m%d")
        md_path = reports / f"augur_pme_gate_diagnosis_{stamp}.md"
        js_path = reports / f"augur_pme_gate_diagnosis_{stamp}.json"
        md_path.write_text(md, encoding="utf-8")
        js_path.write_text(json.dumps(d, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"\n✓ wrote {md_path.relative_to(root)} + {js_path.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
