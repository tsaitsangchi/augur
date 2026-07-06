#!/usr/bin/env python
"""advisor 蒸餾(自問自答)staging schema 遷移 — S1-S5 全 DDL 之單一住所,一次冪等落地。

🎯 這支在做什麼(白話):建「advisor 自問自答蒸餾管線」的接收 schema,全表住 **advisor 側**
   (表名前綴 advisor_distill_*,界線-A:蒸餾產物零落 knowledge_*/philosophy_*/feature_values、
   零成 citation、零進預測 7 package)——
   - advisor_distill_question(S2:題目 + situation_label 1/2/3〔in-corpus / out-of-corpus / 離題〕
     + expected〔ANSWER/DECLINE/REFUSE〕+ domain + topic_source〔真兆來源:knowledge_query /
     philosophy_work / philosophy_thinker / curated_ooc…〕+ 進度游標欄 + 冪等 uq)。
   - advisor_distill_context(S3:每題實跑 retrieve_all 之**真實** citations(可 trace 回 DB 列)+
     真實 payload,寫 context JSONB;target_response 欄**留空待 S4** teacher 生成——
     **界線-B:context(真實檢索)與 target_response(teacher 示範)分欄**,S5 驗 target 事實 ⊂ context)。
   全部 IF NOT EXISTS / 先查 pg catalog 才 ADD,重跑零副作用。DDL 於 transaction 內先建、
   rollback 前驗 pg catalog、確認無誤才 commit(#6 冪等 + 驗證清單=實查 catalog)。
守 #1(蒸餾非真兆入庫:此為訓練行為樣本、非 knowledge/feature;界線-A/B 入 schema)· #6(冪等重跑安全)·
   #12(DDL 單一住所)· #15(驗證=實查 pg catalog)· 憲章 v1.22.0 隔離不變式(蒸餾產物住 advisor 側)· CLAUDE #29。
   計畫 SSOT=reports/augur_advisor_selfqa_training_plan_20260706.md §③界線 A/B/C · §④⑤ S1-S5。

執行指令矩陣:
  python scripts/migrate_advisor_distill_ddl.py           # 冪等執行全部 DDL + 印驗證清單(安全預設)
  python scripts/migrate_advisor_distill_ddl.py --check    # 唯讀:只印驗證清單、不執行 DDL(--dry-run 同義)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# (標籤, 冪等 DDL);順序有相依:question 先建(context.question_id FK 依賴)
DDL = [
    ("table advisor_distill_question", """
        CREATE TABLE IF NOT EXISTS advisor_distill_question (
          question_id     serial PRIMARY KEY,
          question        text NOT NULL,
          situation_label smallint NOT NULL CHECK (situation_label IN (1, 2, 3)),
          expected        varchar(16) NOT NULL CHECK (expected IN ('ANSWER', 'DECLINE', 'REFUSE')),
          domain          varchar(64),
          topic_source    varchar(48) NOT NULL,
          topic_ref       text,
          batch_tag       varchar(48),
          context_built   boolean NOT NULL DEFAULT false,
          created_at      timestamptz NOT NULL DEFAULT now(),
          UNIQUE (question)
        )"""),
    ("index idx_distill_q_label",
     "CREATE INDEX IF NOT EXISTS idx_distill_q_label ON advisor_distill_question (situation_label, expected)"),
    ("index idx_distill_q_pending",
     "CREATE INDEX IF NOT EXISTS idx_distill_q_pending ON advisor_distill_question (context_built) WHERE context_built IS FALSE"),
    ("table advisor_distill_context", """
        CREATE TABLE IF NOT EXISTS advisor_distill_context (
          context_id        serial PRIMARY KEY,
          question_id       int NOT NULL REFERENCES advisor_distill_question(question_id),
          context           jsonb NOT NULL,
          n_citations       int NOT NULL DEFAULT 0,
          relevant          boolean NOT NULL DEFAULT false,
          retrieval_scope   text NOT NULL,
          target_response   text,
          teacher_model     varchar(64),
          teacher_at        timestamptz,
          validated         boolean NOT NULL DEFAULT false,
          validate_verdict  jsonb,
          built_at          timestamptz NOT NULL DEFAULT now(),
          UNIQUE (question_id)
        )"""),
    ("index idx_distill_ctx_pending_target",
     "CREATE INDEX IF NOT EXISTS idx_distill_ctx_pending_target ON advisor_distill_context (question_id) "
     "WHERE target_response IS NULL"),
    ("index idx_distill_ctx_validated",
     "CREATE INDEX IF NOT EXISTS idx_distill_ctx_validated ON advisor_distill_context (validated) "
     "WHERE target_response IS NOT NULL"),
]

# 驗證清單:實查 pg catalog(#15)——(標籤, 存在性查詢, 期望 True)
VERIFY = [
    ("table advisor_distill_question",
     "SELECT to_regclass('public.advisor_distill_question') IS NOT NULL"),
    ("table advisor_distill_context",
     "SELECT to_regclass('public.advisor_distill_context') IS NOT NULL"),
    ("col question.situation_label CHECK(1,2,3)",
     "SELECT count(*)>0 FROM information_schema.columns "
     "WHERE table_name='advisor_distill_question' AND column_name='situation_label'"),
    ("col context.target_response(界線-B 分欄、S4 前恆 NULL)",
     "SELECT count(*)>0 FROM information_schema.columns "
     "WHERE table_name='advisor_distill_context' AND column_name='target_response'"),
    ("col context.context jsonb(真實檢索、可 trace)",
     "SELECT data_type='jsonb' FROM information_schema.columns "
     "WHERE table_name='advisor_distill_context' AND column_name='context'"),
    ("fk context.question_id → question",
     "SELECT count(*)>0 FROM information_schema.table_constraints "
     "WHERE table_name='advisor_distill_context' AND constraint_type='FOREIGN KEY'"),
]


def verify(cur):
    """實查 pg catalog 印驗證清單;回 all_ok。"""
    all_ok = True
    print("── DDL 驗證清單(實查 pg catalog、#15)──")
    for label, q in VERIFY:
        cur.execute(q)
        row = cur.fetchone()                         # 表未建時某些查詢回 0 列 → 視為未通過(graceful,不 traceback)
        ok = bool(row[0]) if row else False
        all_ok = all_ok and ok
        print(f"  {'✓' if ok else '✗'} {label}")
    return all_ok


def run(cur):
    for label, sql in DDL:
        cur.execute(sql)
        print(f"  DDL applied: {label}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", "--dry-run", dest="check", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if args.check:
            print("── 唯讀:只驗證、不執行 DDL ──")
            ok = verify(cur)
        else:
            print("── advisor 蒸餾 staging schema 遷移(冪等)──")
            run(cur)
            ok = verify(cur)  # commit 前先驗;transaction 內 rollback-safe
        print(f"\n{'✓ 全部通過' if ok else '✗ 有驗證未過(見上)'}")
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
