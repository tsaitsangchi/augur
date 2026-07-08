#!/usr/bin/env python
"""兩軌三態判停器(harness P2)— 讀 ledger + 凍結 baseline,機械算 deploying/suspected/confirmed 裁決。

🎯 這支在做什麼(白話):對部署 cell(ridge_H60_LO、asof_incumbent 全史齊口徑),比對本輪 revalidation_ledger
   vs 凍結 revalidation_baseline,出**兩軌三態**裁決(no-AI 機械閾值比對、寫 revalidation_verdict)——
   - **軌A 地板監測(絕對門檻 → 只標註、永不判停)**:DSR<95%=標註「未達統計確立(薄edge常態)」。
     **DSR 絕不入判停**(headline 現就<95%,入判停=首輪誤殺,5 鏡對抗審查釘死)。
   - **軌B 衰減告警(相對凍結 baseline 顯著劣化 → 才判停)**:net 從曾勝基準轉輸(超額≤0)∨ 超額相對基線
     下滑>閾值 ∨ HAC-t 從>2 掉破 ∨ deflated 地板轉負。**HAC-t=None(小樣本)不觸發、同宇宙鎖、連續 k 輪
     才 confirmed(單點不判)**。
   三態:**deploying_unestablished**(部署中-未確立、常態、無衰減)/ **suspected_decay_review**(疑似衰減-人審)
   / **confirmed_decay_stop**(連續 k 輪衰減-建議停,人決策)。

   閾值全讀 judgestop_threshold(#29b);裁決寫 revalidation_verdict(provenance)。**靈魂:判停=系統建議、
   人決策**(confirmed 亦只出旗標+證據、不自動下架部署)。

守 #12 · #15(判停≠失敗、DSR 不入判停、宇宙鎖防誤歸)· #29b(閾值住 DB)· 隔離不變式(禁 import 素養/
   advisor、禁回讀 prediction_values;唯讀 ledger/baseline/threshold、寫 verdict)· SSOT=harness plan §0/P2。

執行指令矩陣:
  python scripts/revalidate_verdict.py            # 對最新 as_of 之部署 cell 出裁決 + 寫 revalidation_verdict
  python scripts/revalidate_verdict.py --dry-run  # 只算+印、不寫
  python scripts/revalidate_verdict.py --cell ridge_H60_LO --stage C --config 'LO|since2014'  # 明示部署 cell
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DEPLOY_CELL = "ridge_H60_LO"
DEPLOY_UNIVERSE = "asof_incumbent"
DEPLOY_STAGE = "C"                 # C 核心 = 2014起 ridge H60 long-only(部署主投組)
DEPLOY_HORIZON = 60
DEPLOY_CONFIG = "LO|since2014"


def evaluate(baseline, current, thr, prior_streak):
    """兩軌三態判停核心(純函式、可測)。
    baseline={net_excess, hac_t, deflated_ann};current={net_sharpe,bench,net_excess,hac_t,dsr,deflated_ann,n};
    thr={policy_key: threshold};prior_streak=先前連續衰減輪數。回 dict(a_annotations,b_signals,b_conds,state,streak)。"""
    # ── 軌A:絕對門檻、只標註、永不判停 ──
    a = []
    if current.get("dsr") is not None and current["dsr"] < thr["dsr_annotate"]:
        a.append(f"DSR {current['dsr']*100:.1f}% < {thr['dsr_annotate']*100:.0f}% = 未達統計確立(薄edge常態、非崩)")
    # ── 軌B:相對凍結 baseline 衰減、才判停(同宇宙鎖、HAC-t None 不觸發)──
    b, conds = [], []
    ne = current.get("net_excess")
    if ne is not None and ne <= thr["net_excess_zero"]:
        b.append(f"net 從勝基準轉輸(超額 {ne:+.3f} ≤ 0)"); conds.append("net_excess_zero")
    bne = baseline.get("net_excess")
    if bne and bne > 0 and ne is not None and ne < bne * (1 - thr["net_excess_rel_drop"]):
        b.append(f"超額 {ne:.3f} 相對凍結基線 {bne:.3f} 下滑>{thr['net_excess_rel_drop']*100:.0f}%")
        conds.append("net_excess_rel_drop")
    ht = current.get("hac_t")
    if ht is not None and ht < thr["hac_t_floor"]:                 # None(小樣本)→ 不觸發
        b.append(f"IC HAC-t {ht:.2f} < {thr['hac_t_floor']:.0f} = 顯著性崩"); conds.append("hac_t_floor")
    da = current.get("deflated_ann")
    if da is not None and da <= thr["deflated_floor_zero"]:
        b.append(f"deflated 年化有效 Sharpe {da:+.3f} ≤ 0 = 地板轉負"); conds.append("deflated_floor_zero")
    # ── 三態(連續 k 輪)──
    k = int(thr.get("consecutive_k", 2))
    if not b:
        streak, state = 0, "deploying_unestablished"
    else:
        streak = prior_streak + 1
        state = "confirmed_decay_stop" if streak >= k else "suspected_decay_review"
    return {"a_annotations": a, "b_signals": b, "b_conds": conds, "state": state, "streak": streak}


def _load_thresholds(cur):
    cur.execute("SELECT policy_key, threshold FROM judgestop_threshold WHERE horizon=0")
    return {k: float(v) for k, v in cur.fetchall()}


def _latest_current(cur, stage, horizon, config, as_of):
    """部署 cell 本輪指標(net/bench/dsr/deflated + HAC-t 自 stage B asof_ic)。"""
    def _m(metric, st=stage, mdl="ridge", cfg=config):
        cur.execute("SELECT metric_value, hac_t FROM revalidation_ledger WHERE as_of_date=%s AND stage=%s "
                    "AND horizon=%s AND model=%s AND config=%s AND metric_name=%s",
                    (as_of, st, horizon, mdl, cfg, metric))
        r = cur.fetchone()
        return (r[0], r[1]) if r else (None, None)
    net = _m("net_sharpe")[0]
    bench = _m("bench_sharpe")[0]
    dsr = _m("dsr")[0]
    defl = _m("deflated_sharpe_ann")[0]
    hac = _m("mean_ic", st="B", mdl="B2_ridge", cfg="asof_ic")[1]     # HAC-t 自 B asof_ic
    ne = (net - bench) if (net is not None and bench is not None) else None
    return {"net_sharpe": net, "bench": bench, "net_excess": ne, "hac_t": hac,
            "dsr": dsr, "deflated_ann": defl}


def _prior_streak(cur, cell, as_of):
    """先前連續衰減輪數(revalidation_verdict 軌B、< as_of 最近若干輪連續非 deploying)。"""
    cur.execute("SELECT as_of_date, state FROM revalidation_verdict WHERE cell=%s AND track='B_decay' "
                "AND as_of_date < %s ORDER BY as_of_date DESC", (cell, as_of))
    streak = 0
    for _d, st in cur.fetchall():
        if st in ("suspected_decay_review", "confirmed_decay_stop"):
            streak += 1
        else:
            break
    return streak


def main(argv=None):
    ap = argparse.ArgumentParser(description="兩軌三態判停器(P2)")
    ap.add_argument("--cell", default=DEPLOY_CELL)
    ap.add_argument("--universe", default=DEPLOY_UNIVERSE)
    ap.add_argument("--stage", default=DEPLOY_STAGE)
    ap.add_argument("--horizon", type=int, default=DEPLOY_HORIZON)
    ap.add_argument("--config", default=DEPLOY_CONFIG)
    ap.add_argument("--as-of", dest="as_of", default=None, help="預設=revalidation_ledger 最新 as_of")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT max(as_of_date) FROM revalidation_ledger")
        as_of = args.as_of or cur.fetchone()[0]
        if as_of is None:
            sys.exit("revalidation_ledger 無資料;先 python scripts/revalidate.py --run")
        thr = _load_thresholds(cur)
        if not thr:
            sys.exit("judgestop_threshold 無閾值;先 python scripts/migrate_judgestop_ddl.py")
        cur.execute("SELECT net_excess, hac_t, deflated_ann FROM revalidation_baseline WHERE cell=%s AND universe=%s",
                    (args.cell, args.universe))
        br = cur.fetchone()
        if not br:
            sys.exit(f"revalidation_baseline 無 {args.cell}/{args.universe} 錨;先 python scripts/revalidate_baseline.py")
        baseline = {"net_excess": br[0], "hac_t": br[1], "deflated_ann": br[2]}
        current = _latest_current(cur, args.stage, args.horizon, args.config, as_of)
        if current["net_sharpe"] is None:   # 部署 cell 本輪無 ledger 資料 → 不假裝 deploying(無資料偽裝常態、#15)
            sys.exit(f"✗ 部署 cell {args.cell}({args.stage}/H{args.horizon}/{args.config})於 as_of {as_of} "
                     f"無 net_sharpe 列;先跑 revalidate.py --run 補該輪、再裁決(不對缺資料出常態裁決)。")
        prior = _prior_streak(cur, args.cell, as_of)
        res = evaluate(baseline, current, thr, prior)

    STATE_ZH = {"deploying_unestablished": "部署中-未確立(常態)",
                "suspected_decay_review": "疑似衰減-人審",
                "confirmed_decay_stop": "確認衰減-建議停(人決策)"}
    print("=" * 76)
    print(f"兩軌三態判停裁決 — cell={args.cell} universe={args.universe} as_of={as_of}")
    print("=" * 76)
    print(f"凍結 baseline:超額={baseline['net_excess']}  deflated={baseline['deflated_ann']}")
    print(f"本輪 current :net={current['net_sharpe']} bench={current['bench']} 超額={current['net_excess']} "
          f"HAC-t={current['hac_t']} DSR={current['dsr']} deflated={current['deflated_ann']}")
    print(f"\n【軌A 地板監測(絕對門檻、只標註、永不判停)】")
    for x in res["a_annotations"]:
        print(f"   ⓘ {x}")
    if not res["a_annotations"]:
        print("   (無;DSR≥門檻或缺)")
    print(f"【軌B 衰減告警(相對凍結 baseline、才判停;prior_streak={prior}、k={int(thr.get('consecutive_k',2))})】")
    for x in res["b_signals"]:
        print(f"   ⚠ {x}")
    if not res["b_signals"]:
        print("   ✓ 無衰減訊號(超額未轉負、未顯著下滑、HAC-t 未破 2、地板未轉負)")
    print(f"\n▶ 狀態:{res['state']} = {STATE_ZH[res['state']]}(streak={res['streak']})")
    if res["state"] == "deploying_unestablished":
        print("   → 常態:薄 edge 部署中、未達統計確立但無衰減;continue 追蹤(#15 判停≠失敗)")

    if args.dry_run:
        print("\n[dry-run] 不寫 revalidation_verdict。")
        return 0
    snap = json.dumps({k: current[k] for k in current}, default=float)
    with db.connect() as conn, db.transaction(conn) as cur:
        for track, note in (("A_annotate", "; ".join(res["a_annotations"]) or "無"),
                            ("B_decay", "; ".join(res["b_signals"]) or "無衰減訊號")):
            cur.execute(
                "INSERT INTO revalidation_verdict "
                "(as_of_date, cell, universe, track, state, triggered_cond, metric_snapshot, baseline_ref, threshold_source, note) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (as_of_date, cell, track) DO UPDATE SET "
                "verdict_at=now(), state=EXCLUDED.state, triggered_cond=EXCLUDED.triggered_cond, "
                "metric_snapshot=EXCLUDED.metric_snapshot, note=EXCLUDED.note",
                (as_of, args.cell, args.universe, track,
                 res["state"] if track == "B_decay" else "deploying_unestablished",
                 ",".join(res["b_conds"]) if track == "B_decay" else None,
                 snap, f"revalidation_baseline/{args.universe}",
                 ",".join(res["b_conds"]) if track == "B_decay" else "dsr_annotate", note))
    print(f"\n✓ 寫入 revalidation_verdict(as_of {as_of}、cell {args.cell}、兩軌)。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
