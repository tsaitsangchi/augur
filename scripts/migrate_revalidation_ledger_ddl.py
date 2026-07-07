#!/usr/bin/env python
"""持續再驗證帳本 schema 遷移 — revalidation_ledger 一表冪等落地(部署計劃階段 D5)。

🎯 這支在做什麼(白話):建立「持續再驗證帳本」——每次 `revalidate.py` 對某 as-of 上界重跑
   STAGE B(as-of IC + HAC-t)/C(經濟價值 net Sharpe/Calmar/MaxDD)/D(H120 vs H60 風險調整)驗證後,
   把每個 (stage, horizon, model, config, metric) 之機械 N(`n_periods`)與指標值逐列記錄下來,
   供追蹤「指標隨 as-of 前推 / 資料累積如何變化」——尤其消解 STAGE D「H120 近期 n=8 小樣本」caveat:
   as-of 前推、n 變大後 H120 近期優勢才能定論。
   全部 IF NOT EXISTS,重跑零副作用。**唯記錄面**:不改判準、不進預測管線(純追蹤帳本)。

守 #6(冪等重跑安全)· #12(DDL 單一住所、指標由既有 evaluation helper 產)· #15(每列 trace 回 run_at/config)·
   CLAUDE #29(個別可執行 + 指令矩陣)· SSOT=reports/augur_prediction_deployment_plan_20260707.md §8 階段 D5。

執行指令矩陣:
  python scripts/migrate_revalidation_ledger_ddl.py           # 冪等執行 DDL + 印驗證清單(安全預設)
  python scripts/migrate_revalidation_ledger_ddl.py --check   # 唯讀:只印驗證清單、不執行 DDL
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DDL = [
    ("table revalidation_ledger", """
        CREATE TABLE IF NOT EXISTS revalidation_ledger (
          run_at        timestamptz NOT NULL DEFAULT now(),
          as_of_date    date NOT NULL,
          stage         text NOT NULL,
          horizon       int  NOT NULL,
          model         text NOT NULL,
          config        text NOT NULL,
          metric_name   text NOT NULL,
          metric_value  double precision,
          n_periods     int,
          hac_t         double precision,
          note          text,
          CONSTRAINT revalidation_stage_chk CHECK (stage IN ('B','C','D'))
        )"""),
    ("index ix_reval_asof_stage", """
        CREATE INDEX IF NOT EXISTS ix_reval_asof_stage
          ON revalidation_ledger (as_of_date, stage, horizon)"""),
    ("index ix_reval_metric_time", """
        CREATE INDEX IF NOT EXISTS ix_reval_metric_time
          ON revalidation_ledger (stage, horizon, model, config, metric_name, as_of_date)"""),
    ("comment revalidation_ledger", """
        COMMENT ON TABLE revalidation_ledger IS
        '持續再驗證帳本(D5);每次 revalidate.py 重跑 B/C/D 之機械 N 與指標逐列記錄,追蹤隨 as-of 前推之趨勢;唯記錄面、不進預測管線(隔離不變式外)、不改判準'"""),
    ("comment col n_periods", """
        COMMENT ON COLUMN revalidation_ledger.n_periods IS
        '本次驗證該 (stage,horizon,config) 之機械有效期數(折/panel 數);H120 近期 n 何時 ≥20 可定論即由此欄追蹤'"""),
    ("comment col hac_t", """
        COMMENT ON COLUMN revalidation_ledger.hac_t IS
        'STAGE B IC 序列之 Newey-West HAC 去相關 t-stat(metrics.effective_t_hac、#11);C/D 之非 IC 指標為 NULL'"""),
]

VERIFY = [
    ("revalidation_ledger 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='revalidation_ledger'"),
    ("stage CHECK", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='revalidation_stage_chk'"),
    ("索引", "SELECT string_agg(indexname,', ' ORDER BY indexname) FROM pg_indexes WHERE tablename='revalidation_ledger'"),
    ("表 COMMENT", "SELECT obj_description('revalidation_ledger'::regclass)"),
    ("現有列數", "SELECT count(*) FROM revalidation_ledger"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001  表未建時 count/comment 會失敗 → 誠實印,不中斷
            print(f"  {label}: (查詢失敗:{e})")


def main(argv=None):
    ap = argparse.ArgumentParser(description="持續再驗證帳本 DDL 遷移(revalidation_ledger;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
