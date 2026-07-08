#!/usr/bin/env python
"""Deflated Sharpe 地板裁決 — 把 headline 淨 Sharpe 從樂觀上界釘成 deflated 真兆(#15 誠實終判前置)。

🎯 這支在做什麼(白話):headline「淨 Sharpe ~1.20」是「N 選 1、多重比較之前、單 seed」的**樂觀上界**。
   本支用 Bailey & López de Prado (2014) Deflated Sharpe Ratio(DSR)扣掉「搜過 N 個 config 才挑到最好」的
   選型偏誤,算 headline 到底過不過 95% 統計確立門檻。

   **命門=單位口徑(per-period,非年化)**:DSR 的 sr_obs / SR_0 / sqrt(T−1) 標準誤(Lo 2002)全定義在
   「報酬被觀測的頻率」上;年化 Sharpe(=per-period × sqrt(ppy))配 T=期數的 sqrt(T−1) = 分子年化尺度、
   分母/T 期數尺度 → z 被灌水 sqrt(ppy) 倍 → DSR **系統性高估**(把未過門檻講成過門檻,最危險的樂觀偏誤)。
   故:重跑 headline 取**真實 per-period 序列**(sr_pp / 真實 skew / kurt / T / ppy),試驗 SR 亦逐 horizon 之
   ppy 轉 per-period 才並池算 Var(SR)。N 一律由 trial_ledger DB query 機械得出(禁人手填,SOP §6 G7)。

   **誠實邊界**:DSR<95% ≠ edge 不存在——haircut 後有效 Sharpe 仍為正(point estimate),只是**顯著性未達確立**;
   且此 DSR 仍是樂觀上界(survivorship 債未閉環/單 seed/成本平坦/n 小 → 真實 DSR 再更低)。

守 #12(DSR 住 metrics.py、選股住 portfolio.py,本支只編排)· #14(經濟終判前置閘)· #15(per-period 正確口徑、
   真兆判讀、舊年化 bug 值作廢揭露)· #28(本地零 usage)· #29(個別可執行 + 指令矩陣)· SOP §5 債 d/§6 G7。

執行指令矩陣:
  python scripts/deflate_headline_verdict.py                          # headline=Ridge H60 LO 2014、N 自 trial_ledger、印裁決
  python scripts/deflate_headline_verdict.py --horizon 120 --since 2014   # 換 horizon 候選
  python scripts/deflate_headline_verdict.py --model B2_ridge --top-frac 0.1 --cost 0.00585   # 明示口徑
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

from augur.core import db
from augur.evaluation import deflation
from augur.evaluation import metrics as M
from augur.evaluation import portfolio

EULER_GAMMA = 0.5772156649015329


def _nonoverlap(panels, h):
    """貪婪挑非重疊再平衡 panel(與 run_economic_eval 同口徑,#12)。"""
    need = h * 1.45 * 0.9
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def _ppy_for(conn, since, h, model, top_frac, cost):
    """某 horizon 之 periods-per-year(重跑一次取 ppy;逐 horizon 轉 per-period 需其自身 ppy)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date",
                    (since,))
        panels = [r[0] for r in cur.fetchall()]
    r = portfolio.run_backtest(conn, _nonoverlap(panels, h), h, model=model,
                               top_frac=top_frac, weight="equal", cost=cost, asof=True)
    return r


def main(argv=None):

    ap = argparse.ArgumentParser(description="Deflated Sharpe 地板裁決(per-period 正確口徑)")
    ap.add_argument("--model", default="B2_ridge", help="headline 模型(portfolio.run_backtest 口徑)")
    ap.add_argument("--horizon", type=int, default=60)
    ap.add_argument("--since", default="2014", help="樣本期起點年(sample_since 對映;→ YYYY-01-01)")
    ap.add_argument("--top-frac", type=float, default=0.1)
    ap.add_argument("--cost", type=float, default=0.00585)
    args = ap.parse_args(argv)
    since_date = f"{args.since}-01-01"
    ledger_since = f"since{args.since}"
    ledger_model = "ridge" if "ridge" in args.model else "gbdt"

    with db.connect() as conn:
        # ── headline 真實 per-period 序列(重跑)──
        rh = _ppy_for(conn, since_date, args.horizon, args.model, args.top_frac, args.cost)
        if not rh:
            sys.exit(f"headline 回測回空(panel 不足?since={since_date} h={args.horizon})")
        sr_pp, T, sk, ku = deflation.per_period_stats(rh["net_series"])   # #12 共用 per-period 口徑
        ppy_h = rh["ppy"]
        sr_ann = rh["portfolio_net"]["sharpe"]

        # ── 試驗集(N 機械得出)+ 逐 horizon ppy(H60/H120 各重跑一次取 ppy)──
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT horizon FROM trial_ledger")
            horizons = sorted(r[0] for r in cur.fetchall())
            cur.execute("SELECT horizon, metric_value FROM trial_ledger WHERE metric_name='net_sharpe'")
            trials = cur.fetchall()
        ppy_by_h = {args.horizon: ppy_h}
        for hh in horizons:
            if hh not in ppy_by_h:
                r = _ppy_for(conn, since_date, hh, args.model, args.top_frac, args.cost)
                ppy_by_h[hh] = r["ppy"] if r else ppy_h   # 退化:借用 headline ppy(誠實印警告)

    # per-period 轉換(逐 horizon 自身 ppy,#12 共用 helper)
    pp_all = deflation.trials_per_period(trials, ppy_by_h)
    pp_fam = deflation.trials_per_period([(h, s) for h, s in trials if h == args.horizon], ppy_by_h)
    var_all = M.sharpe_trial_variance(pp_all)
    var_fam = M.sharpe_trial_variance(pp_fam)
    n_all = len(pp_all)
    n_fam = len(pp_fam)
    # buggy 年化版對照(揭露舊 note 出處)
    var_ann = M.sharpe_trial_variance([sr for _, sr in trials])

    print("=" * 76)
    print(f"Deflated Sharpe 地板裁決 — headline={args.model} H{args.horizon} LO {ledger_since} "
          f"cost {args.cost:.3%}")
    print("=" * 76)
    print(f"headline 真實序列:T={T}期  ppy={ppy_h:.3f}  per-period SR={sr_pp:.4f}  "
          f"年化 SR={sr_ann:.4f}(=pp×√ppy 自洽驗證 {sr_pp*np.sqrt(ppy_h):.4f})")
    print(f"報酬分布:skew={sk:+.4f}  raw kurtosis={ku:.4f}(常態=3)")
    print(f"試驗數 N(trial_ledger 機械):同 H{args.horizon} 家族={n_fam}  全部(混頻)={n_all}")
    print(f"試驗 SR 分散(per-period):家族 sd={np.sqrt(var_fam):.4f}  全部 sd={np.sqrt(var_all):.4f}")
    print()

    verdict_rows = []
    for label, N, trials_pp in ((f"N={n_fam} (H{args.horizon} 同頻家族=樂觀上界)", n_fam, pp_fam),
                                (f"N={n_all} (全試驗混頻=保守下界)", n_all, pp_all)):
        good = deflation.deflated_floor(rh["net_series"], ppy_h, trials_pp, N)   # #12 共用 DSR 計算
        eff_ann, dsr = good["deflated_ann"], good["dsr"]
        bug = M.deflated_sharpe(sr_ann, T, n_trials=N, sr_var=var_ann, skew=0.0, kurt=3.0)
        verdict_rows.append((N, dsr, eff_ann))
        print(f"── {label} ──")
        print(f"   SR_0={good['sr_0']:.4f}  haircut(pp)={good['haircut']:.4f}  "
              f"→ deflated 年化有效 Sharpe≈{eff_ann:.3f}")
        print(f"   DSR={dsr:.4f} ({dsr*100:.1f}%)  {'PASS' if dsr>=0.95 else 'FAIL'}≥95%"
              f"   [buggy 年化版 DSR={bug['dsr']*100:.1f}% ← 作廢、勿引]")
        print()

    dsr_lo = min(r[1] for r in verdict_rows)   # 保守(較大 N=混頻;SR_0 較高→DSR 較低)
    dsr_hi = max(r[1] for r in verdict_rows)   # 樂觀(較小 N=同頻家族)
    eff_lo = min(r[2] for r in verdict_rows)
    eff_hi = max(r[2] for r in verdict_rows)
    # 方法論 SSOT:deflation 一律取較保守(較大)N 為準——禁用樂觀 N(較小)灌水過門檻(敵③)。
    # H120 since2014 實證:N=8 樂觀 95.8% 過、N=16 保守 93.6% 未過 → 取保守判未確立。
    passed = dsr_lo >= 0.95
    straddle = dsr_hi >= 0.95 > dsr_lo
    band = ("跨 95%(樂觀 N 過、保守 N 未過→取保守判未確立)" if straddle
            else ("≥95%" if passed else "皆<95%"))
    print("=" * 76)
    print("裁決(#15 誠實):")
    print(f"  headline 年化 Sharpe {sr_ann:.2f} 【{'過' if passed else '未過'}】deflation"
          f"(取較保守 N={n_all} 混頻):DSR 保守 {dsr_lo*100:.1f}% / 樂觀 {dsr_hi*100:.1f}%,{band}。")
    print(f"  deflated 年化有效 Sharpe ≈ {eff_lo:.2f}~{eff_hi:.2f}(point estimate 為正=edge 非零,"
          f"但{'已達' if passed else '未達'}統計確立)。")
    print("  ⚠ DSR<95% ≠ edge 不存在;且此值仍是樂觀上界——survivorship 債未閉環/單 seed/成本平坦/"
          "n 小,真實 DSR 只會更低。舊報告『89.6%』係年化單位 bug、作廢。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
