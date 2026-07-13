"""🎯 dataset_catalog 加 aggregate_daily_method 欄＋以 ingest seed 回填——#29b 整改(2026-07-13 拍板 1+2):
intraday-source 日級聚合法('close'/'all')從 code dict 遷 DB 為 runtime SSOT;欄建成後
ingest.aggregate_method() 即以 DB 為權威(欄未建前自動退 code seed,過渡零風險)。

守原則 #29(b)(策展資料住 DB)· #12(單一 SSOT 交棒)· #6(冪等)。

執行指令矩陣:
  python scripts/migrate_catalog_aggregate_ddl.py            # 印現況(欄存在否/現值),不動 DB
  python scripts/migrate_catalog_aggregate_ddl.py --migrate  # 冪等建欄+seed 回填(ADD COLUMN IF NOT EXISTS)
  python scripts/migrate_catalog_aggregate_ddl.py --check    # 同無參數(唯讀)
⚠ DDL 於 audit/長跑對帳進行中勿跑(#30 鎖風暴);audit 綠後執行。
"""
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.ingestion.ingest import _AGGREGATE_DAILY


def status(cur):
    cur.execute("SELECT 1 FROM information_schema.columns "
                "WHERE table_name='dataset_catalog' AND column_name='aggregate_daily_method'")
    has = bool(cur.fetchone())
    vals = {}
    if has:
        cur.execute("SELECT dataset, aggregate_daily_method FROM dataset_catalog "
                    "WHERE aggregate_daily_method IS NOT NULL ORDER BY dataset")
        vals = dict(cur.fetchall())
    return has, vals


def main():
    migrate = "--migrate" in sys.argv or "--run" in sys.argv
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            has, vals = status(cur)
            print(f"aggregate_daily_method 欄: {'存在' if has else '未建'}; 現值: {vals or '(無)'}")
            print(f"code seed: {_AGGREGATE_DAILY}")
            if not migrate:
                print("(唯讀;--migrate 才建欄+回填)")
                return 0
            cur.execute("ALTER TABLE dataset_catalog ADD COLUMN IF NOT EXISTS aggregate_daily_method varchar(8)")
            for ds, m in _AGGREGATE_DAILY.items():
                cur.execute("UPDATE dataset_catalog SET aggregate_daily_method=%s WHERE dataset=%s", (m, ds))
                print(f"  seed {ds}={m} ({cur.rowcount} 列)")
        with db.transaction(conn) as cur:
            has, vals = status(cur)
            print(f"完成:欄={'存在' if has else '未建'}; 值={vals}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
