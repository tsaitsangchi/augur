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
          "deliberation_escalation", "deliberation_redline_trigger", "deliberation_benchmark", "deliberation_lens",
          "deliberation_engine_config", "deliberation_bench_batch", "deliberation_run", "deliberation_task",
          "deliberation_proposal", "deliberation_panel_score", "deliberation_model_probe",
          "deliberation_model_agreement")

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
    ("table deliberation_lens", """
        CREATE TABLE IF NOT EXISTS deliberation_lens (
          lens_key    text PRIMARY KEY,
          prompt      text NOT NULL,
          enabled     boolean NOT NULL DEFAULT true,
          created_at  timestamptz NOT NULL DEFAULT now()
        )"""),
    ("seed lens", """
        INSERT INTO deliberation_lens (lens_key, prompt) VALUES
          ('skeptic','你是對抗性懷疑者:假設題目中的宣稱可能是錯的,提出能「證偽」它的檢查點。'),
          ('complete','你是完整性稽核者:找出題目範圍內「應存在而可能缺漏」的東西,逐一提出存在性檢查。'),
          ('doctrine','你是治權稽核者:檢查是否違反 anti-leakage/隔離/誠實紀律,提出可機驗的違規探測。')
        ON CONFLICT (lens_key) DO NOTHING"""),
    ("migrate verifier check +pytest", """
        DO $$ BEGIN
          ALTER TABLE deliberation_claim DROP CONSTRAINT IF EXISTS deliberation_claim_assigned_verifier_check;
          ALTER TABLE deliberation_claim ADD CONSTRAINT deliberation_claim_assigned_verifier_check
            CHECK (assigned_verifier IN ('information_schema','import_isolation','file_grep',
                                         'db_query','pytest','human_claude','none'));
        END $$"""),
    ("comment deliberation_session", """
        COMMENT ON TABLE deliberation_session IS
        '本地審議引擎工作帳(與 knowledge_* 嚴格分離;審議產物非知識、禁 AI 生成入庫不變式無涉);status=confirmed 唯確定性 verdict 可寫(機械鎖在 engine 層強制)'"""),
    # ── P0-B1/B3(補完計畫 §2.1/§2.3,2026-07-11 拍板)──
    ("alter claim +semantic_bound (B1)", """
        ALTER TABLE deliberation_claim
          ADD COLUMN IF NOT EXISTS semantic_bound boolean NOT NULL DEFAULT false"""),
    ("comment semantic_bound", """
        COMMENT ON COLUMN deliberation_claim.semantic_bound IS
        '錨可自 claim_text 確定性導出/反抽取全命中=true;false 之 confirmed 僅表「錨成立」,報表以 anchor 為主體(B1 封閉)'"""),
    ("table deliberation_engine_config (B3)", """
        CREATE TABLE IF NOT EXISTS deliberation_engine_config (
          config_key text PRIMARY KEY,
          config     jsonb NOT NULL,
          config_sha text NOT NULL,
          updated_at timestamptz NOT NULL DEFAULT now()
        )"""),
    ("seed fast_anchor_rules (L6_pytest 預設關;L6_isolation 固定錨零參數故開)", """
        INSERT INTO deliberation_engine_config (config_key, config, config_sha) VALUES
          ('fast_anchor_rules',
           '{"L4_db_query":true,"L4_information_schema":true,"L5_file_grep":true,"L6_pytest":false,"L6_isolation":true}',
           '78d2a81d63204531')
        ON CONFLICT (config_key) DO NOTHING"""),
    # ── P0-B2 GATE-lite(§2.2)+ P1 模式 10 run/task(§3.1;GATE/D3/D4 依賴,最先建)──
    ("table deliberation_bench_batch (B2)", """
        CREATE TABLE IF NOT EXISTS deliberation_bench_batch (
          batch_id         text PRIMARY KEY,
          purpose          text NOT NULL CHECK (purpose IN ('gate','adhoc')),
          arm_config       jsonb NOT NULL,
          preregistered_at timestamptz NOT NULL DEFAULT now(),
          git_sha          text NOT NULL,
          note             text
        )"""),
    ("alter benchmark +batch_id +seed (B2)", """
        DO $$ BEGIN
          ALTER TABLE deliberation_benchmark ADD COLUMN IF NOT EXISTS batch_id text
            REFERENCES deliberation_bench_batch(batch_id);
          ALTER TABLE deliberation_benchmark ADD COLUMN IF NOT EXISTS seed int;
        END $$"""),
    ("table deliberation_run (模式10)", """
        CREATE TABLE IF NOT EXISTS deliberation_run (
          run_id          text PRIMARY KEY,
          idempotency_key text NOT NULL UNIQUE,
          plan            jsonb NOT NULL,
          status          text NOT NULL DEFAULT 'running' CHECK (status IN ('running','completed','failed')),
          created_at      timestamptz NOT NULL DEFAULT now(),
          finished_at     timestamptz
        )"""),
    ("table deliberation_task (模式10)", """
        CREATE TABLE IF NOT EXISTS deliberation_task (
          task_id    bigserial PRIMARY KEY,
          run_id     text NOT NULL REFERENCES deliberation_run(run_id) ON DELETE CASCADE,
          seq        int  NOT NULL,
          payload    jsonb NOT NULL,
          status     text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','done','failed')),
          attempt    int  NOT NULL DEFAULT 0,
          session_id text REFERENCES deliberation_session(session_id),
          updated_at timestamptz NOT NULL DEFAULT now(),
          UNIQUE (run_id, seq)
        )"""),
    # ── P1 模式 9 自我迭代(§3.2)+ 模式 4 judge panel(§3.3)──
    ("table deliberation_proposal (模式9)", """
        CREATE TABLE IF NOT EXISTS deliberation_proposal (
          proposal_id bigserial PRIMARY KEY,
          session_id  text NOT NULL REFERENCES deliberation_session(session_id),
          parent_id   bigint REFERENCES deliberation_proposal(proposal_id),
          stage       text NOT NULL CHECK (stage IN ('draft','attack','refine','final')),
          round       int  NOT NULL DEFAULT 1,
          content     jsonb NOT NULL,
          critique    jsonb,
          claim_ids   bigint[],
          created_at  timestamptz NOT NULL DEFAULT now()
        )"""),
    ("table deliberation_panel_score (模式4;soft 排序權、零 confirmed 權)", """
        CREATE TABLE IF NOT EXISTS deliberation_panel_score (
          score_id    bigserial PRIMARY KEY,
          proposal_id bigint NOT NULL REFERENCES deliberation_proposal(proposal_id),
          judge_model text NOT NULL,
          judge_lens  text REFERENCES deliberation_lens(lens_key),
          rubric      jsonb NOT NULL,
          score       numeric NOT NULL,
          rationale   text,
          created_at  timestamptz NOT NULL DEFAULT now()
        )"""),
    # ── P2 量測維度(§4):D1 效能 probe / D3 heartbeat / D7 跨模一致 ──
    ("table deliberation_model_probe (D1)", """
        CREATE TABLE IF NOT EXISTS deliberation_model_probe (
          probe_id          bigserial PRIMARY KEY,
          run_at            timestamptz NOT NULL DEFAULT now(),
          model_tag         text NOT NULL,
          task_kind         text NOT NULL CHECK (task_kind IN ('propose','anchor','structured_json')),
          prompt_chars      int  NOT NULL,
          prompt_eval_count int, eval_count int,
          load_ms bigint, prompt_eval_ms bigint, eval_ms bigint, total_ms bigint NOT NULL,
          tok_per_s         numeric,
          gpu_mem_used_mb   int,
          note              text,
          git_sha           text NOT NULL
        )"""),
    ("alter session +heartbeat/finished/duration (D3)", """
        DO $$ BEGIN
          ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS heartbeat_at timestamptz;
          ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS finished_at  timestamptz;
          ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS duration_s   numeric;
        END $$"""),
    ("table deliberation_model_agreement (D7)", """
        CREATE TABLE IF NOT EXISTS deliberation_model_agreement (
          agree_id    bigserial PRIMARY KEY,
          run_at      timestamptz NOT NULL DEFAULT now(),
          topic       text NOT NULL,
          seed        int,
          model_a     text NOT NULL, model_b text NOT NULL,
          session_a   text REFERENCES deliberation_session(session_id),
          session_b   text REFERENCES deliberation_session(session_id),
          n_a int NOT NULL, n_b int NOT NULL, n_common int NOT NULL,
          jaccard     numeric NOT NULL,
          n_agree     int NOT NULL,
          escalate_rate_a numeric, escalate_rate_b numeric,
          detail      jsonb NOT NULL,
          git_sha     text NOT NULL
        )"""),
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
