#!/usr/bin/env python
"""三鏡頭月頻特徵鏈 builder(擂台候選 T1;計畫 §4)。

🎯 這支在做什麼(白話):對 direction_stack_feature_monthly 的每個月頻 panel(同 panel 同 target 宇宙),
   以**同一套** feature generator(augur.features.panel.build_panel,僅換目的表=零複製零口徑漂移)
   算 35 三鏡頭特徵落 direction_threelens_feature_monthly;再以 SQL 補 9 對跨鏡頭交互項
   (interact__ 前綴:每 panel 橫斷面 z-score 後乘積;對清單=計畫 §2 先驗凍結,拍板後不得增刪)。

守 #6(冪等 resume:已建 panel 跳過)· #8(as-of 同 build_panel 口徑)· #12(generator 單一住所)· #15(同碼同值)。

執行指令矩陣:
  python scripts/build_threelens_monthly.py                 # 現況:待建 panel 數(唯讀)
  python scripts/build_threelens_monthly.py --run           # 全量(resume-safe,約數小時,建議背景)
  python scripts/build_threelens_monthly.py --run --limit 2 # 最小單位試跑(#25)
  python scripts/build_threelens_monthly.py --interact-only # 只補交互項(基礎特徵已建時)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.features import panel

TABLE = "direction_threelens_feature_monthly"

# 計畫 §2 先驗凍結之 9 對跨鏡頭交互(T0 拍板 2026-07-12;凍結後不得增刪改)
INTERACT_PAIRS = (
    ("cycle_position_252d", "volume_gini_60d"),
    ("price_to_10yr", "top_holders_pct"),
    ("gross_margin_pctile", "momentum_60d"),
    ("cycle_position_252d", "volatility_60d"),
    ("range_position_120d", "momentum_120d"),
    ("volume_gini_20d", "momentum_20d"),
    ("top_holders_pct", "institutional_net_buy_ratio_20d"),
    ("volume_max_share_20d", "turnover_mean_20d"),
    ("inst_cumflow_position_120d", "cycle_position_252d"),
)

INTERACT_SQL = f"""
WITH z AS (
  SELECT panel_date, stock_id, feature,
         (value - avg(value) OVER w) / NULLIF(stddev_samp(value) OVER w, 0) AS zv
  FROM {TABLE}
  WHERE panel_date = %s AND feature IN %s
  WINDOW w AS (PARTITION BY panel_date, feature)
)
INSERT INTO {TABLE} (panel_date, stock_id, feature, value)
SELECT a.panel_date, a.stock_id, 'interact__' || a.feature || '__x__' || b.feature, a.zv * b.zv
FROM z a JOIN z b ON b.panel_date = a.panel_date AND b.stock_id = a.stock_id
WHERE (a.feature, b.feature) IN %s AND a.zv IS NOT NULL AND b.zv IS NOT NULL
ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value = EXCLUDED.value
"""


def interact(cur, pd_):
    base = tuple(sorted({f for p in INTERACT_PAIRS for f in p}))
    cur.execute(INTERACT_SQL, (pd_, base, tuple(INTERACT_PAIRS)))
    return cur.rowcount


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--interact-only", action="store_true", dest="ionly")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    panel.FEATURE_TABLE = TABLE  # 換目的表(generator 邏輯零複製;f-string 於執行期查模組常數)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT panel_date FROM direction_stack_feature_monthly ORDER BY panel_date")
        panels = [r[0] for r in cur.fetchall()]
        cur.execute(f"SELECT DISTINCT panel_date FROM {TABLE} WHERE feature NOT LIKE 'interact__%%'")
        done = {r[0] for r in cur.fetchall()}
        todo = [p for p in panels if p not in done]
        if not (args.run or args.ionly):
            print(f"panel 窗:{len(panels)}(stack 表)| 已建 {len(done)} | 待建 {len(todo)}")
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        if args.limit:
            todo = todo[: args.limit]
        if not args.ionly:
            for i, pd_ in enumerate(todo, 1):
                cur.execute("SELECT DISTINCT target_id FROM direction_stack_feature_monthly WHERE panel_date=%s", (pd_,))
                ids = sorted(r[0] for r in cur.fetchall())
                res = panel.build_panel(conn, pd_, ids, progress=None)
                with db.transaction(conn) as c2:
                    n_int = interact(c2, pd_)
                print(f"[{i}/{len(todo)}] {pd_}: {res} +交互 {n_int}", flush=True)
        else:
            for pd_ in panels:
                with db.transaction(conn) as c2:
                    n_int = interact(c2, pd_)
                print(f"{pd_}: 交互 {n_int}", flush=True)
        print("✓ 完成(冪等)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
