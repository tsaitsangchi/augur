#!/usr/bin/env python
"""augur 特徵五鏡 audit run — 呼叫 audit.feature_diagnostics 跑 PHASE 9 特徵分診（#11 五鏡合判）。

🎯 這支在做什麼（白話）：對核心股 × feature_values 特徵，跑五鏡（單因子有號 IC / 共線群 / leave-one-out /
SHAP / purged）→ 印每特徵之 IC、SHAP、是否共線、（可選）LOO Δ、合判裁定（drop?/collinear/keep）。
裁定供人合判、非自動刪（#11）。純 DB 計算、不放 API。leave-one-out 重（跑 N+1 次 ladder）、以 --loo 控。

組合根：把 audit 層接上薄 CLI；口徑 reuse evaluation helper（#12 可比）。

守 #11（五鏡合判、不單指標）· #8（purged/as-of）· #12（單一 helper）· #15（誠實揭露）· #18。

執行指令矩陣:python scripts/run_feature_audit.py --since 2014-01-01 --h 60 --asof          （四鏡、快）
      python scripts/run_feature_audit.py --since 2014-01-01 --h 60 --asof --loo    （含 LOO、慢）
"""
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_diagnostics as fd
from augur.core import db


def _panels(cur, since):
    sql = "SELECT DISTINCT panel_date FROM feature_values"
    params = ()
    if since:
        sql += " WHERE panel_date >= %s"
        params = (since,)
    cur.execute(sql + " ORDER BY panel_date", params)
    return [r[0] for r in cur.fetchall()]


def _core(cur):
    cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
    return [r[0] for r in cur.fetchall()]


def _feats(cur, panels):
    cur.execute("SELECT DISTINCT feature FROM feature_values WHERE panel_date = ANY(%s) ORDER BY 1", (panels,))
    return [r[0] for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(description="run 五鏡特徵 audit（#11）")
    ap.add_argument("--since", default="2014-01-01", help="面板起始日（預設 2014-01-01）")
    ap.add_argument("--h", type=int, default=60, help="forward horizon 交易日（預設 60）")
    ap.add_argument("--asof", action="store_true", help="as-of point-in-time 口徑（消 survivorship）")
    ap.add_argument("--loo", action="store_true", help="跑 leave-one-out 必要性（重、N+1 次 ladder）")
    args = ap.parse_args()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            panels = _panels(cur, args.since)
            core = _core(cur)
            feats = _feats(cur, panels)
        if not panels or not core:
            print("無面板或無核心股（先跑 build_feature_panel / build_core_universe）")
            return
        print(f"五鏡 audit：{len(panels)} 面板 × {len(core)} 核心股 × {len(feats)} 特徵 / H={args.h}"
              f" / asof={args.asof} / loo={args.loo}")
        res = fd.five_mirror(conn, panels, args.h, core, feats, asof=args.asof, loo=args.loo)
        pf = res["per_feature"]
        order = sorted(feats, key=lambda f: -(abs(pf[f]["ic"]) if pf[f]["ic"] is not None else 0))
        print(f"\n{'feature':28s} {'IC':>8s} {'HAC-t':>7s} {'SHAP':>9s} {'共線':>4s} {'LOOΔ':>8s}  裁定")
        for f in order:
            d = pf[f]
            ic = f"{d['ic']:+.3f}" if d["ic"] is not None else "  n/a"
            tt = f"{d['ic_eff_t_hac']:.2f}" if d["ic_eff_t_hac"] else "  -"
            sh = f"{d['shap']:.4f}" if d["shap"] is not None else "   n/a"
            co = "✓" if d["in_collinear_group"] else " "
            lo = f"{d['loo_delta']:+.4f}" if d["loo_delta"] is not None else "   -"
            print(f"{f:28s} {ic:>8s} {tt:>7s} {sh:>9s} {co:>4s} {lo:>8s}  {d['verdict']}")
        if res["high_pairs"]:
            print("\n高相關對（|r|≥0.9、共線群）：")
            for a, b, r in res["high_pairs"][:12]:
                print(f"  {a} ~ {b}: {r:+.3f}")


if __name__ == "__main__":
    main()
