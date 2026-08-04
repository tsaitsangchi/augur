#!/usr/bin/env python
"""augur 經濟價值評估 run(Track D 深化)— 回測生產模型之經濟指標 + 交易成本/換手率(#14 誠實終測)。

🎯 這支在做什麼(白話):把 headline IC 轉成靈魂真度量(#14)——Ridge/GBDT walk-forward 預測組 long-only 投組,
算 CAGR/Sharpe/MaxDD/Calmar,並**扣交易成本(換手×來回成本)算淨值**、掃 top 分位 + 加權,對比等權基準(亦扣成本)。
答:**邊際扛得住成本嗎?最佳 top 分位/加權?**(空方 Track D 已證無效 → 專注 long-only)。

守 #8 · #12 · #14 · #15(gross/net 雙報、換手揭露)· #28(本地零 usage)。
執行指令矩陣:
  python scripts/run_economic_eval.py --since 2021-01-01 --h 60 --cost 0.00585
  python scripts/run_economic_eval.py --since 2021-01-01 --until 2026-06-30 --h 60 --feature-source=prodset  # PME 現役集終關
  python scripts/run_economic_eval.py --since 2021-04-01 --h 60 --add-features lending_fee_rate_mean_20d  # A2 終關:同 --since 兩跑(有/無候選)同尺互比
"""
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.core.prodset_contract import (
    FEATURE_SOURCE_CANONICAL,
    FEATURE_SOURCE_PRODSET,
    FEATURE_SOURCES,
    ProdsetEmptyError,
)
from augur.evaluation import portfolio

COST_TW = 0.00585   # 台股來回:手續費 2×0.1425% + 證交稅 0.3%(保守、未計折讓)


def _nonoverlap(panels, h):
    """貪婪挑非重疊再平衡 panel(持有 h 交易日 ≈ h×1.45 日曆日)——長 horizon 經濟回測免重疊雙計。"""
    need = h * 1.45 * 0.9                                  # h 交易日轉日曆、留 10% 容差
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def _fmt(m):
    if not m:
        return "(n<3)"
    s = m["sharpe"]; c = m["calmar"]
    return (f"CAGR {m['cagr']:>+6.1%} | Sharpe {('%.2f' % s) if s is not None else ' n/a':>5} | "
            f"MaxDD {m['max_drawdown']:>+6.1%} | Calmar {('%.2f' % c) if c is not None else ' n/a':>5} | 勝率 {m['hit_rate']:>4.0%}")


def main():
    ap = argparse.ArgumentParser(description="經濟價值回測 + 交易成本(#14)")
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--until", default=None, help="panel 上限(釘網格;防建置中網格飄移=2026-07-29 雙跑作廢教訓)")
    ap.add_argument("--panels-list", default=None, dest="panels_list",
                    help="顯式 panel 清單(逗號日期)——覆蓋稀疏特徵之同尺比較用(如 lending 22 枚)")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--cost", type=float, default=COST_TW, help="來回交易成本(預設台股 0.585%%)")
    ap.add_argument("--interactions", default=None, help="加入交互特徵（逗號分隔、如 inter_fh_x_p10yr；eval 層橫斷面 z 乘積、見 cross_section.INTERACTIONS）")
    ap.add_argument("--add-features", default=None, dest="add_feats",
                    help="生產集外加候選特徵(逗號分隔;讀 staged 值,A2 經濟終關用——同 --since 兩跑同尺互比)")
    ap.add_argument("--drop-features", default=None, dest="drop_feats",
                    help="自 canonical 剔除特徵(逗號分隔)——已入 canonical 之成員做終關對照時用(vs 全集兩跑)")
    ap.add_argument(
        "--feature-source",
        default=FEATURE_SOURCE_CANONICAL,
        choices=list(FEATURE_SOURCES),
        dest="feature_source",
        help="特徵來源:canonical=預設研究尺;prodset=PME 現役 active∩覆蓋(P1-DRIFT C 終關)",
    )
    ap.add_argument("--seed", type=int, default=42, help="M1_gbdt random_state(B2_ridge 無視;多 seed 請外層重跑)")
    args = ap.parse_args()
    inter = [s.strip() for s in args.interactions.split(",")] if args.interactions else None
    adds = [s.strip() for s in args.add_feats.split(",")] if args.add_feats else None
    drops = set(s.strip() for s in args.drop_feats.split(",")) if args.drop_feats else None
    src = (args.feature_source or FEATURE_SOURCE_CANONICAL).strip().lower()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.panels_list:
                cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date = ANY(%s::date[]) ORDER BY panel_date",
                            ([s.strip() for s in args.panels_list.split(",")],))
            elif args.until:
                cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s AND panel_date<=%s ORDER BY panel_date",
                            (args.since, args.until))
            else:
                cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (args.since,))
            panels = [r[0] for r in cur.fetchall()]
        panels = _nonoverlap(panels, args.h)              # 非重疊再平衡(h=60 季度為 no-op、h=120/252 抽半年/年)
        import hashlib as _hl
        print(f"panel 清單 hash={_hl.sha256(','.join(map(str, panels)).encode()).hexdigest()[:10]}"
              f"(兩跑同 hash=同尺自證)")
        from augur.evaluation import baseline
        feats = None
        if src == FEATURE_SOURCE_PRODSET:
            if adds or drops:
                print("✗ --feature-source=prodset 不可併用 --add-features/--drop-features;中止。")
                return 1
            try:
                feats = baseline.resolve_train_feats(conn, panels, source=FEATURE_SOURCE_PRODSET)
            except ProdsetEmptyError as e:
                print(f"✗ prodset empty (FC-empty): {e};中止。")
                return 1
            if not feats:
                print("✗ prodset 特徵集為空;中止。")
                return 1
        elif adds or drops:
            feats = baseline.canonical_features(conn, panels)
            if drops:
                feats = [f for f in feats if f not in drops]
            if adds:
                feats = feats + [a for a in adds if a not in feats]   # 防重名(2026-07-29 齊=0 教訓)
        print(f"經濟回測:{len(panels)} 非重疊 panel（{args.since}+）× h={args.h} × 來回成本 {args.cost:.3%}（as-of、purged walk-forward）"
              + f" / feature_source={src}"
              + (f" feats={feats}" if feats is not None else "")
              + (f" / interactions={inter}" if inter else "") + (f" / +候選={adds}" if adds else "")
              + f" / seed={args.seed}")
        for model in ("B2_ridge", "M1_gbdt"):
            print(f"\n══ {model}（long-only）══")
            for top in (0.1, 0.2, 0.3):
                for wt in ("equal", "pred"):
                    r = portfolio.run_backtest(conn, panels, args.h, feats=feats, model=model, top_frac=top, weight=wt, cost=args.cost, interactions=inter, seed=args.seed)
                    if not r:
                        continue
                    tag = f"top{top:.0%}/{wt}"
                    print(f"  {tag:12s} 換手 {r['avg_turnover']:>4.0%} | gross[{_fmt(r['portfolio_gross'])}]")
                    print(f"  {'':12s}            | net  [{_fmt(r['portfolio_net'])}]")
            rb = portfolio.run_backtest(conn, panels, args.h, feats=feats, model=model, top_frac=0.2, cost=args.cost, interactions=inter, seed=args.seed)
            if rb:
                print(f"  {'基準(淨)':12s} 換手 {rb['bench_turnover']:>4.0%} | net  [{_fmt(rb['benchmark_net'])}]  ({rb['n_periods']}期/{rb['periods_per_year']}per-yr)")
        print("\n判讀(#14):net(扣成本)Sharpe/Calmar 仍優於基準 net → 真可交易;若成本吃掉邊際 → IC 非真 alpha。最佳 top/加權看 net。")
        print("≠確立級／可交易宣稱——本輸出僅經濟尺；direction_gate／人裁另層。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
