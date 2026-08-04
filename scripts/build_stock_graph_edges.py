#!/usr/bin/env python
"""augur 股票圖邊建構 — 產業共群＋報酬相關性邊（S3-WAVE-D Phase 2b／2c；表＝`stock_graph_edge`）。

🎯 這支在做什麼（白話）：給定 as-of，(a) **產業共群邊**＝核心股依 `TaiwanStockInfo.industry_category`
（取每股最新一列，對齊既有 `universe/core_gate.py` 對此欄之既有慣例——**非**嚴格 as-of 版本化，因該表對
多數股僅有單一「最近同步」列，見 §已知限制）兩兩配對，`weight=1.0`；(b) **報酬相關性邊**＝核心股
`TaiwanStockPriceAdj.close` 之日報酬，過去 60／120 交易日 Pearson 相關（嚴格 as-of：只用 `date<=as_of`
之收盤價），`|corr|>=閾值` 且 `n_obs>=門檻` 才存邊——門檻沿用 `audit.field_correlation.MIN_OBS`（60）之
慣例。**預設 `--dry-run`（唯讀，只印統計，不寫庫）**；`--commit` 才真寫入 `stock_graph_edge`（S3-WAVE-D
Phase 2c，本波 GO 若未涵蓋 2c，`--commit` 須待另一次明示）。

已知限制（誠實揭露、非隱藏）：`TaiwanStockInfo.industry_category` 對多數股票僅有單一「最近同步」列
（非完整 SCD 歷史），故 `industry_same` 邊之產業別＝**目前最新分類**，非嚴格 `as_of` 當時分類——與
`core_gate.py` 既有作法一致；因產業分類變動極慢，短期 as-of 誤差風險低，但**不宣稱**此邊型別為
anti-leakage 嚴格意義下之 point-in-time（`return_corr_*` 邊則嚴格 as-of，兩者風險層級不同、分別標示）。

守 #1（`n_obs`／`source_table` 溯源，門檻不足不寫）· #8（`return_corr_*` 嚴格 `date<=as_of`）·
#12（複用既有慣例，不建第二套產業分類邏輯）。

執行指令矩陣:
  python scripts/build_stock_graph_edges.py --asof 2026-06-30                      （預設 dry-run，印統計）
  python scripts/build_stock_graph_edges.py --asof 2026-06-30 --corr-threshold 0.3 --min-obs 60
  python scripts/build_stock_graph_edges.py --asof 2026-06-30 --commit             （Phase 2c，須另行明示才可執行）
"""
import argparse
import datetime as dt

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from augur.core import db
from migrate_stock_graph_edge_ddl import TABLE, bootstrap  # noqa: E402  同目錄 sibling script（scripts/ 非套件，見 #18 CLI 慣例）

MIN_OBS_DEFAULT = 60          # 沿用 audit.field_correlation.MIN_OBS 慣例
CORR_THRESHOLD_DEFAULT = 0.3  # operational、非治權值；未重覆驗證前不寫死進治權檔（CLAUDE #27）
RETURN_LOOKBACK_BUFFER = 150  # 抓價格列數上限（含緩衝，供 60/120 兩窗共用一次查詢）


def _core_stock_ids(cur, as_of):
    cur.execute(
        "SELECT stock_id FROM core_universe_asof "
        "WHERE as_of_date = (SELECT max(as_of_date) FROM core_universe_asof WHERE as_of_date <= %s) "
        "ORDER BY stock_id", (as_of,))
    return [r[0] for r in cur.fetchall()]


def industry_same_edges(cur, stock_ids, as_of):
    """產業共群邊（純查詢＋純配對邏輯）：每股最新 `industry_category`（對齊 core_gate.py 既有慣例）→
    同產業兩兩配對，`(source<target, weight=1.0)`。回 list[(source, target, weight, n_obs, source_table)]。"""
    cur.execute(
        """SELECT DISTINCT ON (stock_id) stock_id, industry_category
           FROM "TaiwanStockInfo" WHERE stock_id = ANY(%s) ORDER BY stock_id, date DESC""",
        (stock_ids,))
    cat_of = {sid: cat for sid, cat in cur.fetchall() if cat}
    by_cat: dict[str, list[str]] = {}
    for sid, cat in cat_of.items():
        by_cat.setdefault(cat, []).append(sid)
    edges = []
    for cat, sids in by_cat.items():
        sids = sorted(sids)
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                edges.append((sids[i], sids[j], 1.0, None, "TaiwanStockInfo"))
    return edges, cat_of


def _fetch_returns(cur, stock_ids, as_of, lookback=RETURN_LOOKBACK_BUFFER):
    """逐股抓 `date<=as_of` 之最近 `lookback` 個收盤價 → 日報酬（pct_change）；回寬表 DataFrame（index=date, col=stock_id）。

    嚴格 as-of：SQL 篩 `date<=%s`，不看未來（#8）。
    """
    series = {}
    for sid in stock_ids:
        cur.execute(
            'SELECT date, close FROM "TaiwanStockPriceAdj" '
            'WHERE stock_id=%s AND date<=%s AND close>0 ORDER BY date DESC LIMIT %s',
            (sid, as_of, lookback))
        rows = cur.fetchall()
        if len(rows) < 2:
            continue
        rows.reverse()
        s = pd.Series({d: float(c) for d, c in rows}).sort_index()
        series[sid] = s.pct_change().dropna()
    if not series:
        return pd.DataFrame()
    return pd.DataFrame(series)


def return_corr_edges(returns_wide: pd.DataFrame, window: int, *,
                       min_obs: int = MIN_OBS_DEFAULT, threshold: float = CORR_THRESHOLD_DEFAULT):
    """純函式：寬表日報酬（可能長度不一、以 NaN 對齊）→ 過去 `window` 個交易日之 pairwise Pearson，
    `n_obs>=min_obs` 且 `|corr|>=threshold` 才收邊。回 list[(source, target, weight, n_obs, source_table)]。

    `n_obs` 逐對真算（非 window 常數）——資料尾端不齊之股會有較少共同觀測，如实揭露（#1）。
    """
    if returns_wide.empty:
        return []
    sub = returns_wide.tail(window)
    mask = sub.notna().astype(int)
    n_obs_mat = mask.T.values @ mask.values
    corr_mat = sub.corr(min_periods=min_obs)
    cols = list(sub.columns)
    edges = []
    for i, a in enumerate(cols):
        for j in range(i + 1, len(cols)):
            b = cols[j]
            c = corr_mat.iloc[i, j]
            n = int(n_obs_mat[i, j])
            if pd.isna(c) or n < min_obs or abs(c) < threshold:
                continue
            lo, hi = sorted((a, b))
            edges.append((lo, hi, float(c), n, "TaiwanStockPriceAdj"))
    return edges


def main():
    ap = argparse.ArgumentParser(description="stock_graph_edge 建構（產業共群＋報酬相關性；預設 dry-run）")
    ap.add_argument("--asof", required=True, help="as-of 日期 YYYY-MM-DD")
    ap.add_argument("--corr-threshold", type=float, default=CORR_THRESHOLD_DEFAULT,
                    help=f"相關邊 |corr| 下界（預設 {CORR_THRESHOLD_DEFAULT}，operational 非治權值）")
    ap.add_argument("--min-obs", type=int, default=MIN_OBS_DEFAULT,
                    help=f"最少共同觀測數（預設 {MIN_OBS_DEFAULT}，沿用 field_correlation.MIN_OBS 慣例）")
    ap.add_argument("--commit", action="store_true",
                    help="真寫入 stock_graph_edge（Phase 2c；預設 dry-run 唯讀，須另行明示才可用）")
    args = ap.parse_args()
    as_of = dt.date.fromisoformat(args.asof)

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            stock_ids = _core_stock_ids(cur, as_of)
        if not stock_ids:
            print(f"as_of={as_of} 無核心股快照")
            return
        print(f"as_of={as_of}｜核心股 {len(stock_ids)} 支｜corr_threshold={args.corr_threshold}｜min_obs={args.min_obs}")

        with db.transaction(conn) as cur:
            ind_edges, cat_of = industry_same_edges(cur, stock_ids, as_of)
        print(f"\n── industry_same ──")
        print(f"  產業分類數：{len(set(cat_of.values()))}｜覆蓋股數：{len(cat_of)}/{len(stock_ids)}｜邊數：{len(ind_edges)}")

        with db.transaction(conn) as cur:
            returns_wide = _fetch_returns(cur, stock_ids, as_of)
        print(f"\n── 日報酬序列 ──　取得 {returns_wide.shape[1]}/{len(stock_ids)} 支股票之序列"
              f"（缺者：價格史 <2 列，直接排除、不補值）")

        all_edges = [(s, t, w, n, src, "industry_same") for s, t, w, n, src in ind_edges]
        for window, edge_type in ((60, "return_corr_60d"), (120, "return_corr_120d")):
            edges = return_corr_edges(returns_wide, window,
                                       min_obs=args.min_obs, threshold=args.corr_threshold)
            print(f"\n── {edge_type} ──")
            print(f"  過門檻邊數：{len(edges)}（|corr|>={args.corr_threshold}, n_obs>={args.min_obs}）")
            if edges:
                w = [e[2] for e in edges]
                print(f"  weight 分布：min={min(w):.3f} median={sorted(w)[len(w)//2]:.3f} max={max(w):.3f}")
            all_edges += [(s, t, w, n, src, edge_type) for s, t, w, n, src in edges]

        print(f"\n合計邊數（{len(all_edges)}）｜dry-run={'否（將寫庫）' if args.commit else '是（未寫庫）'}")

        if not args.commit:
            print("\n（--dry-run 預設：以上為統計，未執行任何寫入；--commit 才真寫入 stock_graph_edge，Phase 2c 另行明示）")
            return

        with db.transaction(conn) as cur:
            bootstrap(cur)
            cur.execute(f"DELETE FROM {TABLE} WHERE as_of_date=%s", (as_of,))  # 同 as_of 冪等覆寫
            if all_edges:
                execute_values(
                    cur,
                    f"INSERT INTO {TABLE} (source_stock_id, target_stock_id, weight, n_obs, source_table, edge_type, as_of_date) VALUES %s",
                    [(s, t, w, n, src, et, as_of) for s, t, w, n, src, et in all_edges])
        print(f"✓ 已寫入 {len(all_edges)} 列 @ as_of={as_of}")


if __name__ == "__main__":
    main()
