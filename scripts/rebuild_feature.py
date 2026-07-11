#!/usr/bin/env python
"""重建單一特徵 — 特徵 writer 碼修正後之針對性重算(通用、registry 驅動;#29c 取代逐特徵專用檔)。

🎯 這支在做什麼(白話):某特徵的 writer 碼修正後(如修 #8 洩漏/#15 陳舊),用**修正後的 compute 函式**
   重算 feature_values 中該特徵每個既有 (panel_date, stock_id) 之值,冪等替換——**改 writer 碼+重建、
   不手 UPDATE 補值(#12)**;修正後算不出者誠實刪列(#1 缺列)。只碰指定 feature 一欄(#3 最小邊界)。
   擴新特徵＝ registry 加一列 (feature→module.func),零改邏輯(#29c)。

registry 之 compute 函式簽名一律 (cur, sid, panel_date) → {feature: value, ...};本工具取 dict[feature]。

守 #12(改 writer 重建非手 patch)· #1(算不出即缺列)· #3(最小邊界)· #29a/c(個別可執行、參數化通用)。

執行指令矩陣:
  python scripts/rebuild_feature.py                                  # 無參數:印矩陣 + 可重建 feature 清單(唯讀)
  python scripts/rebuild_feature.py --feature price_to_10yr          # 印該 feature 現況統計(唯讀)
  python scripts/rebuild_feature.py --feature price_to_10yr --run    # 重算並冪等替換(逐 panel 交易)
  python scripts/rebuild_feature.py --feature gross_margin_pctile --run
"""
import argparse
import importlib
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# feature → (module, compute_func);compute 簽名 (cur, sid, panel_date) → {feature: value}
_REBUILDERS = {
    "price_to_10yr": ("augur.features.valuation", "compute_valuation_features"),
    "gross_margin_pctile": ("augur.features.margin_cycle", "compute_margin_cycle_features"),
}


def _compute_fn(feature):
    mod, fn = _REBUILDERS[feature]
    return getattr(importlib.import_module(mod), fn)


def _stats(cur, feature):
    cur.execute("SELECT count(*), count(DISTINCT stock_id), count(DISTINCT panel_date), "
                "min(value), max(value), round(avg(value)::numeric,4) "
                "FROM feature_values WHERE feature=%s", (feature,))
    return cur.fetchone()


def _run(feature):
    compute = _compute_fn(feature)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE feature=%s ORDER BY panel_date", (feature,))
        panels = [r[0] for r in cur.fetchall()]
    print(f"重算 {feature}:{len(panels)} 個 panel(逐 panel 交易、冪等)")
    tot_upd = tot_del = 0
    for pd in panels:
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT stock_id FROM feature_values WHERE feature=%s AND panel_date=%s", (feature, pd))
            sids = [r[0] for r in cur.fetchall()]
            upd = dele = 0
            for sid in sids:
                v = compute(cur, sid, pd).get(feature)               # 修正後 writer 碼
                if v is None:                                        # 算不出 → 誠實刪列(#1)
                    cur.execute("DELETE FROM feature_values WHERE feature=%s AND panel_date=%s AND stock_id=%s",
                                (feature, pd, sid)); dele += 1
                else:
                    cur.execute("UPDATE feature_values SET value=%s WHERE feature=%s AND panel_date=%s AND stock_id=%s",
                                (v, feature, pd, sid)); upd += 1
            conn.commit()
            tot_upd += upd; tot_del += dele
            print(f"  {pd}: 重算 {len(sids)} → UPDATE {upd} / DELETE {dele}")
    print(f"✓ 完成 {feature}:UPDATE {tot_upd} / DELETE {tot_del}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--feature", choices=sorted(_REBUILDERS))
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if not args.feature:
        print(__doc__.split("執行指令矩陣:")[1])
        print("可重建 feature:", ", ".join(sorted(_REBUILDERS)))
        return 0
    if args.run:
        _run(args.feature); return 0
    with db.connect() as conn:
        print(f"{args.feature} 現況 (count, stocks, panels, min, max, mean):", _stats(conn.cursor(), args.feature))
    return 0


if __name__ == "__main__":
    sys.exit(main())
