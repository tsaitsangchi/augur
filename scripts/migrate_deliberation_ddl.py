#!/usr/bin/env python
"""本地審議引擎 schema 收編 — deliberation_* 5 表冪等固化(前身計畫 W1 之 DDL 住所補課)。

🎯 這支在做什麼(白話):把「本地審議引擎」的 5 張帳表——session(一次審議)/claim(qwen 提出的
   待驗宣稱,**只准帶錨點+指定確定性 verifier**)/verdict(裁決;**status='confirmed' 唯確定性
   verdict 可寫**=機械鎖,CHECK: verdict≠undecidable 則 evidence 必填)/escalation(無 oracle 可驗
   →強制升級人裁,不得 LLM 自判)/redline_trigger(治權檔/anti-leakage 欄觸線清單)——之 DDL 收編
   進 git 住所。**這 5 表先前手動 psql 建立、無 migrate script**(換機/重建即失);本支逐字固化
   DB 現行 DDL(pg_dump 抽取 2026-07-10)+ 冪等 IF NOT EXISTS,新機一鍵重建。
   審議產物=工作帳,與 knowledge_* 嚴格分離(獨立表名前綴;禁 AI 生成內容入知識庫不變式無涉)。

守 #6(冪等)· #12(DDL 單一住所;本支=deliberation_* 唯一建表處)· #15(status 機械鎖:confirmed 必有
   is_deterministic verdict 佐證——engine 層強制,表層 CHECK 承載閉集)· CLAUDE #29a。
   SSOT=reports/augur_deliberation_orchestrator_plan_20260709.md §5(前身)+ 本地審議引擎計畫 v1(2026-07-10)。

執行指令矩陣:
  python scripts/migrate_deliberation_ddl.py            # 無參數:印本矩陣+5 表現況(唯讀)
  python scripts/migrate_deliberation_ddl.py --run      # 冪等建 5 表+index(既有不動)
  python scripts/migrate_deliberation_ddl.py --verify   # 斷言 5 表+CHECK/FK/UNIQUE 就位(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

TABLES = ("deliberation_session", "deliberation_claim", "deliberation_verdict",
          "deliberation_escalation", "deliberation_redline_trigger", "deliberation_benchmark")

DDL = [
    ("table deliberation_session", """
        CREATE TABLE IF NOT EXISTS deliberation_session (
          session_id text PRIMARY KEY,
          topic      text NOT NULL,
          draft_path text,
          as_of      date,
          status     text NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open','adjudicating','escalated','closed')),
          coverage   jsonb NOT NULL DEFAULT '{}'::jsonb,
          model_tag  text,
          created_at timestamptz NOT NULL DEFAULT now()
        )"""),
    ("table deliberation_claim", """
        CREATE TABLE IF NOT EXISTS deliberation_claim (
          claim_id          bigserial PRIMARY KEY,
          session_id        text NOT NULL REFERENCES deliberation_session(session_id) ON DELETE CASCADE,
          perspective       text NOT NULL,
          category          text NOT NULL
                              CHECK (category IN ('schema','program','isolation','doctrine',
                                                  'antileakage','truesign','coverage','other')),
          claim_text        text NOT NULL,
          anchor            text NOT NULL CHECK (btrim(anchor) <> ''),
          assigned_verifier text NOT NULL
                              CHECK (assigned_verifier IN ('information_schema','import_isolation',
                                                           'file_grep','db_query','human_claude','none')),
          status            text NOT NULL DEFAULT 'pending'
                              CHECK (status IN ('pending','confirmed','refuted','undecidable','escalated')),
          provenance        jsonb NOT NULL,
          created_at        timestamptz NOT NULL DEFAULT now()
        )"""),
    ("index ix_delib_claim_session", """
        CREATE INDEX IF NOT EXISTS ix_delib_claim_session ON deliberation_claim (session_id, status)"""),
    ("table deliberation_verdict", """
        CREATE TABLE IF NOT EXISTS deliberation_verdict (
          verdict_id       bigserial PRIMARY KEY,
          claim_id         bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
          verifier         text NOT NULL,
          verdict          text NOT NULL CHECK (verdict IN ('confirmed','refuted','undecidable')),
          evidence         text,
          is_deterministic boolean NOT NULL DEFAULT true,
          ran_at           timestamptz NOT NULL DEFAULT now(),
          CHECK (verdict = 'undecidable' OR evidence IS NOT NULL)
        )"""),
    ("index ix_delib_verdict_claim", """
        CREATE INDEX IF NOT EXISTS ix_delib_verdict_claim ON deliberation_verdict (claim_id, ran_at)"""),
    ("table deliberation_escalation", """
        CREATE TABLE IF NOT EXISTS deliberation_escalation (
          escalation_id bigserial PRIMARY KEY,
          claim_id      bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
          reason        text NOT NULL
                          CHECK (reason IN ('no_oracle','undecidable','red_line_category','verifier_none')),
          payload       jsonb NOT NULL,
          resolved      boolean NOT NULL DEFAULT false,
          resolution    text,
          resolved_at   timestamptz,
          created_at    timestamptz NOT NULL DEFAULT now()
        )"""),
    ("index ix_delib_esc_open", """
        CREATE INDEX IF NOT EXISTS ix_delib_esc_open ON deliberation_escalation (resolved, created_at)"""),
    ("table deliberation_redline_trigger", """
        CREATE TABLE IF NOT EXISTS deliberation_redline_trigger (
          trigger_id bigserial PRIMARY KEY,
          kind       text NOT NULL CHECK (kind IN ('doctrine_file','antileakage_column')),
          pattern    text NOT NULL,
          source     text NOT NULL,
          note       text,
          created_at timestamptz NOT NULL DEFAULT now(),
          UNIQUE (kind, pattern)
        )"""),
    ("table deliberation_benchmark", """
        CREATE TABLE IF NOT EXISTS deliberation_benchmark (
          bench_id      bigserial PRIMARY KEY,
          run_at        timestamptz NOT NULL DEFAULT now(),
          arm           text NOT NULL CHECK (arm IN ('single_shot','engine')),
          model_tag     text NOT NULL,
          task_class    text NOT NULL CHECK (task_class IN ('schema','quant','doc')),
          n_tasks       int  NOT NULL,
          n_correct     int  NOT NULL,          -- 裁決且判對
          n_false_confirm int NOT NULL,         -- 假宣稱被判真(殺手指標)
          n_abstain     int  NOT NULL,          -- 棄權(engine=escalate/undecidable;single=無此路)
          detail        jsonb NOT NULL,          -- 逐題(claim, truth, verdict)可重現(#10)
          git_sha       text NOT NULL
        )"""),
    ("comment deliberation_session", """
        COMMENT ON TABLE deliberation_session IS
        '本地審議引擎工作帳(與 knowledge_* 嚴格分離;審議產物非知識、禁 AI 生成入庫不變式無涉);status=confirmed 唯確定性 verdict 可寫(機械鎖在 engine 層強制)'"""),
]


def _existing(cur):
    cur.execute("SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name = ANY(%s)", (list(TABLES),))
    return {r[0] for r in cur.fetchall()}


def status():
    with db.connect() as conn:
        cur = conn.cursor()
        have = _existing(cur)
        for t in TABLES:
            n = "-"
            if t in have:
                cur.execute(f"SELECT count(*) FROM {t}")
                n = cur.fetchone()[0]
            print(f"  {'✓' if t in have else '✗ 未建'} {t}(rows={n})")


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        for name, sql in DDL:
            cur.execute(sql)
            print(f"  ✓ {name}")
        conn.commit()
    print("✓ --run 完成(冪等;既有表不動)")


def verify() -> int:
    ok = True
    with db.connect() as conn:
        cur = conn.cursor()
        have = _existing(cur)
        for t in TABLES:
            if t not in have:
                print(f"✗ 缺表 {t}"); ok = False
        cur.execute("""SELECT conrelid::regclass::text, contype, count(*) FROM pg_constraint
                       WHERE conrelid::regclass::text = ANY(%s) GROUP BY 1,2""", (list(TABLES),))
        cons = {(r[0], r[1]): r[2] for r in cur.fetchall()}
        expect = [("deliberation_session", "c", 1), ("deliberation_claim", "c", 4),
                  ("deliberation_claim", "f", 1), ("deliberation_verdict", "c", 2),
                  ("deliberation_verdict", "f", 1), ("deliberation_escalation", "c", 1),
                  ("deliberation_escalation", "f", 1), ("deliberation_redline_trigger", "c", 1),
                  ("deliberation_redline_trigger", "u", 1)]
        for t, ctype, n_min in expect:
            if cons.get((t, ctype), 0) < n_min:
                print(f"✗ {t} 約束 {ctype} 數 {cons.get((t, ctype), 0)} < {n_min}"); ok = False
    print("✓ --verify 全綠" if ok else "✗ --verify 失敗")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.run:
        run(); return 0
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    print("5 表現況(唯讀):")
    status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
