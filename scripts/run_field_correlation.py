#!/usr/bin/env python
"""augur 核心股 raw 欄位相關性 run — 對核心股算各 raw 欄位兩兩相關、寫 field_correlation、印跨股聚合報告。

🎯 這支在做什麼（白話）：對 `core_universe` 核心股，逐股建每日對齊面板（價量/籌碼/估值/月營收 ~22 欄）、
算欄位兩兩 Pearson+Spearman 相關（level+change basis）寫進 `field_correlation`；再跨股聚合，印出
「在多股一致正/負相關」的欄位對（中位 corr、正向率、強相關率、股數）。純本地 DB/Python、零 Claude usage（#28）。

組合根：把 audit 層（field_correlation）接上薄 CLI；邏輯在 src、入口不放邏輯。

守 #1（真值、缺即 NaN）· #6（冪等可重跑）· #15（n_obs/股數揭露）· #28（本地批量、不 fan-out）。

執行指令矩陣:python scripts/run_field_correlation.py                    （全核心 + 報告）
      python scripts/run_field_correlation.py --stocks 2330,2317  （子集測試）
      python scripts/run_field_correlation.py --report-only       （跳過計算、只印報告）
"""
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import field_correlation as fc
from augur.core import db


def _core_stocks(cur, explicit):
    if explicit:
        return [s.strip() for s in explicit.split(",")]
    cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
    return [r[0] for r in cur.fetchall()]


def _print_report(conn):
    """跨股聚合報告:cross-field 相關 + lead-lag(可預測)欄位。"""
    print("\n— A. 跨欄相關(contemporaneous,非預測)—")
    for method in ("spearman", "pearson"):
        for basis in ("change", "level"):
            df = fc.cross_stock_summary(conn, method=method, basis=basis)
            if df.empty:
                continue
            print(f"\n══ {method} × {basis}（{len(df)} 對、≥30 股）══")
            print(f"{'field_a':18s} {'field_b':18s} {'中位corr':>8s} {'正向率':>6s} {'強相關率':>7s} {'股數':>5s}")
            for _, r in df.head(12).iterrows():
                print(f"{r.field_a:18s} {r.field_b:18s} {r.median_corr:>+8.3f} {r.pct_pos:>6.0%} {r.pct_strong:>7.0%} {int(r.n_stocks):>5d}")

    print("\n\n— B. lead-lag(predictive:X_t vs t+1 進場未來報酬,#8 安全)→ alpha 候選 —")
    for h in fc.LEADLAG_HORIZONS:
        for basis in ("change", "level"):
            df = fc.cross_stock_leadlag_summary(conn, method="spearman", basis=basis, horizon=h)
            if df.empty:
                continue
            print(f"\n══ spearman × {basis} × H={h} 日（{len(df)} 欄、≥30 股）══")
            print(f"{'field':20s} {'中位corr':>8s} {'正向率':>6s} {'有訊號率(|c|≥.03)':>14s} {'股數':>5s}")
            for _, r in df.head(10).iterrows():
                print(f"{r.field:20s} {r.median_corr:>+8.4f} {r.pct_pos:>6.0%} {r.pct_signal:>14.0%} {int(r.n_stocks):>5d}")


def main():
    ap = argparse.ArgumentParser(description="核心股 raw 欄位相關性 + 跨股聚合報告")
    ap.add_argument("--stocks", help="逗號分隔子集（預設全 core_universe）")
    ap.add_argument("--report-only", action="store_true", help="跳過計算、只印既有 field_correlation 之報告")
    args = ap.parse_args()

    with db.connect() as conn:
        if not args.report_only:
            with db.transaction(conn) as cur:
                stocks = _core_stocks(cur, args.stocks)
            print(f"算相關性：{len(stocks)} 股 × ~22 欄（level+change × pearson+spearman）…")
            total = ll_total = done = skipped = 0
            for i, sid in enumerate(stocks, 1):
                n = fc.analyze_stock(conn, sid)                     # 跨欄相關
                ll = fc.analyze_stock_leadlag(conn, sid)           # lead-lag 可預測
                if n:
                    total += n; ll_total += ll; done += 1
                else:
                    skipped += 1
                if i % 50 == 0:
                    print(f"  {i}/{len(stocks)} 股、跨欄 {total:,} + lead-lag {ll_total:,} 列（{skipped} 略過）")
            print(f"完成：{done} 股、跨欄 {total:,} 列 + lead-lag {ll_total:,} 列、{skipped} 略過")
        print("\n" + "=" * 70 + "\n跨股聚合報告:最一致之正/負相關欄位對")
        _print_report(conn)


if __name__ == "__main__":
    main()
