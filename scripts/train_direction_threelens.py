#!/usr/bin/env python
"""own_threelens_interact 工程冒煙 trainer(候選計畫 T2;非 gate、不入庫、一次跑不迭代)。

🎯 這支在做什麼(白話):44 特徵(35 三鏡頭直餵+9 交互)月頻面板,年塊 walk-forward(purge:訓練面板
   之標籤結算日 < 測試年首面板日)、HistGBM 3-seed 平均+isotonic 校準(訓練尾 20% 面板 fit 校準器),
   對 H20/40/82 印 OOS 工程數字(n/hit/Brier)——**僅機械驗收「出得了 p_up、校準器有 provenance」,
   不以此調參、不作 gate 宣稱**(防偷跑 v3;性能裁決權 100% 在真未來 A3 家族)。

守 #8(purge)· #9(數字出自程式輸出)· #15(工程冒煙≠效力宣稱)· 候選計畫 §5(先凍後跑)。

執行指令矩陣:
  python scripts/train_direction_threelens.py                  # 全 horizons 冒煙(分鐘級)
  python scripts/train_direction_threelens.py --horizon 40     # 單 horizon
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd

from augur.core import db

SEEDS = (7, 42, 2026)
HORIZONS = (20, 40, 82)


def load(cur):
    cur.execute("SELECT panel_date, stock_id, feature, value FROM direction_threelens_feature_monthly")
    f = pd.DataFrame(cur.fetchall(), columns=["panel_date", "stock_id", "feature", "value"])
    X = f.pivot_table(index=["panel_date", "stock_id"], columns="feature", values="value").reset_index()
    sids = sorted(X["stock_id"].unique())
    cur.execute('SELECT stock_id, date, close FROM "TaiwanStockPriceAdj" '
                "WHERE stock_id = ANY(%s) AND date >= '2016-06-01' ORDER BY stock_id, date", (sids,))
    px = pd.DataFrame(cur.fetchall(), columns=["stock_id", "date", "close"])
    return X, px


def labels(X, px, h):
    out = []
    for sid, g in px.groupby("stock_id", sort=False):
        dates = g["date"].to_numpy()
        close = g["close"].to_numpy(dtype=float)
        pos = {d: i for i, d in enumerate(dates)}
        for pd_ in X.loc[X.stock_id == sid, "panel_date"]:
            i = pos.get(pd_)
            if i is None:                       # panel 日非該股交易日 → 取 ≤panel 最近一日
                j = np.searchsorted(dates, pd_, side="right") - 1
                if j < 0:
                    continue
                i = j
            if i + h < len(dates) and close[i] > 0:
                out.append((pd_, sid, float(close[i + h] / close[i] - 1) > 0, dates[i + h]))
    return pd.DataFrame(out, columns=["panel_date", "stock_id", "y", "settle_date"])


def run(X, px, h):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.isotonic import IsotonicRegression
    lab = labels(X, px, h)
    d = X.merge(lab, on=["panel_date", "stock_id"])
    feats = [c for c in d.columns if c not in ("panel_date", "stock_id", "y", "settle_date")]
    years = sorted({p.year for p in d.panel_date})
    rows = []
    for ty in [y for y in years if y >= years[0] + 2]:
        test = d[d.panel_date.map(lambda p: p.year) == ty]
        t0 = test.panel_date.min()
        train = d[d.settle_date < t0]           # purge:標籤結算 < 測試首面板(#8)
        if len(train) < 2000 or test.empty:
            continue
        tr_p = sorted(train.panel_date.unique())
        fit_p, cal_p = set(tr_p[: int(len(tr_p) * 0.8)]), set(tr_p[int(len(tr_p) * 0.8):])
        fit, cal = train[train.panel_date.isin(fit_p)], train[train.panel_date.isin(cal_p)]
        if len(fit) < 500 or len(cal) < 100 or fit.y.nunique() < 2:
            print(f"  [{ty}] 跳過:fit={len(fit)} cal={len(cal)}(樣本不足)")
            continue
        feats_f = [c for c in feats if fit[c].notna().any()]   # 早年全缺特徵逐折剔除(sklearn binning 對全 NaN 欄會炸)
        p_cal = np.zeros(len(cal)); p_test = np.zeros(len(test))
        for s in SEEDS:
            clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05, random_state=s)
            clf.fit(fit[feats_f], fit.y)
            p_cal += clf.predict_proba(cal[feats_f])[:, 1] / len(SEEDS)
            p_test += clf.predict_proba(test[feats_f])[:, 1] / len(SEEDS)
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.01, y_max=0.99)
        iso.fit(p_cal, cal.y)
        p = iso.predict(p_test)
        rows.append((ty, len(test), float(((p > 0.5) == test.y).mean()), float(np.mean((p - test.y) ** 2))))
    n = sum(r[1] for r in rows)
    hit = sum(r[1] * r[2] for r in rows) / n if n else float("nan")
    brier = sum(r[1] * r[3] for r in rows) / n if n else float("nan")
    print(f"H{h}: OOS n={n:,} hit={hit:.4f} brier={brier:.4f} "
          f"(年塊 {len(rows)};校準=isotonic fit 於訓練尾 20% 面板;3-seed 平均)")
    print(f"  ⚠ 工程冒煙數字,非 gate 宣稱;效力唯 A3 真未來家族裁決(no-v3 紀律)")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--horizon", type=int)
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        X, px = load(cur)
    print(f"面板:{X.panel_date.nunique()} × 特徵 {X.shape[1]-2} × 列 {len(X):,}")
    for h in ([args.horizon] if args.horizon else HORIZONS):
        run(X, px, h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
