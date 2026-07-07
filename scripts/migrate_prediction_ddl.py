#!/usr/bin/env python
"""預測層 schema 遷移 — model_registry + prediction_values 兩表冪等落地(SOP 計劃階段 A)。

🎯 這支在做什麼(白話):建立「模型登錄 + 預測產物」兩張表——
   model_registry(每個 fit 好的模型身分證:family/horizon/train_span/asof/feats_hash/seed/
   metrics/artifact_path/git_sha,#15 可重現 + resume 帳本);
   prediction_values(as-of 預測產物:panel_date/model_id/stock_id/score/rank,靈魂產品輸出口)。
   **隔離不變式**:兩表禁被預測 7 package 回讀當特徵(AST import_isolation + DB GRANT 雙閘為
   建表前置驗收;COMMENT 明載)。全部 IF NOT EXISTS,重跑零副作用。
守 #6(冪等重跑安全)· #12(DDL 單一住所)· #15(metrics 真兆可重現)· 隔離不變式 · CLAUDE #29 ·
   SSOT=reports/augur_prediction_sop_plan_20260705.md §10。

執行指令矩陣:
  python scripts/migrate_prediction_ddl.py           # 冪等執行 DDL + 印驗證清單(安全預設)
  python scripts/migrate_prediction_ddl.py --check   # 唯讀:只印驗證清單、不執行 DDL
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DDL = [
    ("table model_registry", """
        CREATE TABLE IF NOT EXISTS model_registry (
          model_id      text PRIMARY KEY,
          family        text NOT NULL,
          horizon       int  NOT NULL,
          train_span    daterange NOT NULL,
          asof_snapshot date NOT NULL,
          feats_hash    text NOT NULL,
          seed          int  NOT NULL,
          metrics       jsonb,
          artifact_path text NOT NULL,
          git_sha       text NOT NULL,
          created_at    timestamptz NOT NULL DEFAULT now(),
          CONSTRAINT model_family_chk CHECK (family IN ('RankRidge','RankGBDT'))
        )"""),
    ("table prediction_values", """
        CREATE TABLE IF NOT EXISTS prediction_values (
          panel_date date NOT NULL,
          model_id   text NOT NULL REFERENCES model_registry(model_id),
          stock_id   text NOT NULL,
          score      double precision NOT NULL,
          rank       int  NOT NULL,
          PRIMARY KEY (panel_date, model_id, stock_id)
        )"""),
    ("column prediction_values.in_portfolio", """
        ALTER TABLE prediction_values ADD COLUMN IF NOT EXISTS in_portfolio boolean NOT NULL DEFAULT false"""),
    ("column prediction_values.weight", """
        ALTER TABLE prediction_values ADD COLUMN IF NOT EXISTS weight double precision NOT NULL DEFAULT 0.0"""),
    ("index ix_pred_panel_model", """
        CREATE INDEX IF NOT EXISTS ix_pred_panel_model ON prediction_values (panel_date, model_id)"""),
    ("comment prediction_values", """
        COMMENT ON TABLE prediction_values IS
        '預測產物;禁被預測 7 package(features/models/universe/evaluation/ingestion/audit/catalog)回讀當特徵——AST import_isolation + DB GRANT 雙閘強制(隔離不變式)'"""),
    ("comment model_registry", """
        COMMENT ON TABLE model_registry IS
        '模型登錄;#15 可重現(git_sha/feats_hash 凍結)+ resume 帳本;非預測輸入表'"""),
]

VERIFY = [
    ("model_registry 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='model_registry'"),
    ("prediction_values 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='prediction_values'"),
    ("family CHECK", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='model_family_chk'"),
    ("prediction_values COMMENT", "SELECT obj_description('prediction_values'::regclass)"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        cur.execute(sql)
        row = cur.fetchone()
        print(f"  {label}: {(row[0] if row and row[0] else '(無)')}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="預測層 DDL 遷移(model_registry+prediction_values;冪等)")
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
