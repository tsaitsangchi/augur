#!/usr/bin/env python
"""三鏡頭月頻特徵表(擂台候選 own_threelens_interact;計畫 §3)。

🎯 這支在做什麼(白話):direction_threelens_feature_monthly——35 三鏡頭特徵+9 交互項之月頻面板,
   鏡射 direction_stack_feature_monthly 的 panel 窗與宇宙;欄名用 stock_id(=沿用 panel.build_panel
   寫入器零複製邏輯,與計畫 target_id 命名差異已留痕)。

守 #6(冪等)· #12(DDL 單一住所)。

執行指令矩陣:
  python scripts/migrate_threelens_ddl.py           # 現況(唯讀)
  python scripts/migrate_threelens_ddl.py --run     # 冪等建表
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS direction_threelens_feature_monthly (
  panel_date date NOT NULL,
  stock_id   text NOT NULL,
  feature    text NOT NULL,
  value      double precision,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, stock_id, feature));
COMMENT ON TABLE direction_threelens_feature_monthly IS
  'own_threelens_interact 候選之月頻特徵(35 三鏡頭直餵+9 交互 interact__ 前綴);宇宙=stack 表同 panel 同 target';
"""


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.run:
            cur.execute(DDL)
            conn.commit()
            print("✓ direction_threelens_feature_monthly 就位(冪等)")
            return 0
        cur.execute("SELECT to_regclass('direction_threelens_feature_monthly')")
        if cur.fetchone()[0]:
            cur.execute("SELECT count(DISTINCT panel_date), count(*) FROM direction_threelens_feature_monthly")
            p, n = cur.fetchone()
            print(f"panels={p} 值={n:,}")
        else:
            print("(未建;--run)")
        print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
