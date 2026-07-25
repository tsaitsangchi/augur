#!/usr/bin/env python
"""演化基礎建設 DDL — 人閘提案佇列 + 本地模型演化帳本三表冪等落地(P0;hugo 2026-07-25 拍板 P0-P3)。
🎯 這支在做什麼(白話):建「能力自動演化、判準人閘一鍵化」的機械底座三表——
   ①`governance_proposal` 判準/治權變更提案佇列:AI 投遞提案(diff 全文+證據包指針),**內容送出即凍結**
     (防竄改 trigger:pending 後 payload 不可改、你核可的必是我提交的那份);status 轉移=pending→approved/
     rejected→enacted,approve 動作唯人(CLI 留 actor+時戳);P5.W2 人閘的 DB 落點。
   ②`local_model_gold_sample` 訓練金標帳本(append-only):每條 gold 帶 verdict(oracle_pass/teacher_gold/
     human_ruled 才可入訓練視圖)+teacher provenance+**trigger_event**(hugo 三問:因為什麼事)+synthetic
     標記恆真(MC P4.E7 NoLaundering)+**隱私欄 contains_private**(true 者禁送外部教師,DB 級非腳本自律)。
   ③`local_model_version` 模型版本註冊:訓練 manifest hash+錨集 hash+評測程式 hash(三 hash 釘死=防從
     分布側挪門柱)+gate 指針+promoted_by 人簽;挪門柱式 trigger(serving 列不可改 hash 類欄)。
   隔離不變式:三表俱非知識層(不成 citation、不進預測管線);樣本/權重=owned_local 級管制(不入 git)。
守 #6(冪等)· #12(DDL 單一住所=本檔)· #15(selftest 紅綠鎖)· P4.E3(append-only)· P5.W2(人簽)· CLAUDE #29。
   SSOT=reports/augur_local_ai_evolution_loop_plan_20260725.md。
執行指令矩陣:
  python scripts/migrate_ai_evolution_ddl.py            # 安全預設:印本矩陣+--check
  python scripts/migrate_ai_evolution_ddl.py --check    # 唯讀:三表/trigger 現況
  python scripts/migrate_ai_evolution_ddl.py --apply    # 冪等建三表+trigger
  python scripts/migrate_ai_evolution_ddl.py --selftest # 零 DB 紅綠(SQL 不變式)
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = [
    ("governance_proposal", """
        CREATE TABLE IF NOT EXISTS governance_proposal (
          proposal_id text PRIMARY KEY,
          kind text NOT NULL CHECK (kind IN ('criteria_change','treaty_text','soul_amendment','gate_freeze','other')),
          title text NOT NULL,
          diff_text text NOT NULL,
          evidence_refs jsonb NOT NULL DEFAULT '[]',
          proposed_by text NOT NULL,
          status text NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending','approved','rejected','enacted','withdrawn')),
          decided_by text, decided_at timestamptz, decision_note text,
          created_at timestamptz NOT NULL DEFAULT now())"""),
    ("local_model_gold_sample", """
        CREATE TABLE IF NOT EXISTS local_model_gold_sample (
          sample_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
          prompt text NOT NULL, gold_answer text NOT NULL,
          verdict text NOT NULL CHECK (verdict IN ('oracle_pass','teacher_gold','human_ruled','rejected')),
          teacher jsonb,
          trigger_event jsonb NOT NULL,
          contains_private boolean NOT NULL,
          is_synthetic boolean NOT NULL DEFAULT true CHECK (is_synthetic),
          provenance jsonb NOT NULL DEFAULT '{}',
          created_at timestamptz NOT NULL DEFAULT now())"""),
    ("local_model_version", """
        CREATE TABLE IF NOT EXISTS local_model_version (
          version_id text PRIMARY KEY,
          base_model text NOT NULL, lora_path text,
          train_sample_manifest_hash text, anchor_hash text, eval_code_hash text,
          gate_id text, eval_result jsonb,
          status text NOT NULL DEFAULT 'candidate' CHECK (status IN ('candidate','serving','retired')),
          promoted_by text, promoted_at timestamptz,
          created_at timestamptz NOT NULL DEFAULT now())"""),
]

TRIGGERS = """
CREATE OR REPLACE FUNCTION governance_proposal_immutable() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'proposal % 不得刪(留痕;撤回=status withdrawn)', OLD.proposal_id;
  END IF;
  IF NEW.diff_text IS DISTINCT FROM OLD.diff_text
     OR NEW.evidence_refs::text IS DISTINCT FROM OLD.evidence_refs::text
     OR NEW.kind IS DISTINCT FROM OLD.kind THEN
    RAISE EXCEPTION 'proposal % 內容送出即凍結:不得改 diff/證據/類型(核可的必是提交的那份)', OLD.proposal_id;
  END IF;
  IF OLD.status IN ('rejected','enacted') THEN
    RAISE EXCEPTION 'proposal % 已終態(%)', OLD.proposal_id, OLD.status;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_gov_proposal_immutable ON governance_proposal;
CREATE TRIGGER trg_gov_proposal_immutable BEFORE UPDATE OR DELETE ON governance_proposal
  FOR EACH ROW EXECUTE FUNCTION governance_proposal_immutable();

CREATE OR REPLACE FUNCTION gold_sample_append_only() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'gold_sample append-only:% 不允許(演化史不剪輯,P4.E3)', TG_OP;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_gold_sample_append_only ON local_model_gold_sample;
CREATE TRIGGER trg_gold_sample_append_only BEFORE UPDATE OR DELETE ON local_model_gold_sample
  FOR EACH ROW EXECUTE FUNCTION gold_sample_append_only();

CREATE OR REPLACE FUNCTION model_version_no_goalpost() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'model_version % 不得刪(退役=status retired)', OLD.version_id;
  END IF;
  IF OLD.status <> 'candidate'
     AND (NEW.train_sample_manifest_hash IS DISTINCT FROM OLD.train_sample_manifest_hash
          OR NEW.anchor_hash IS DISTINCT FROM OLD.anchor_hash
          OR NEW.eval_code_hash IS DISTINCT FROM OLD.eval_code_hash
          OR NEW.gate_id IS DISTINCT FROM OLD.gate_id) THEN
    RAISE EXCEPTION 'model_version % 非 candidate 不得改 hash/gate 錨(挪門柱)', OLD.version_id;
  END IF;
  IF NEW.status = 'serving' AND OLD.status = 'candidate'
     AND (NEW.promoted_by IS NULL OR NEW.promoted_at IS NULL) THEN
    RAISE EXCEPTION 'model_version % 晉升 serving 須 promoted_by 人簽+時戳(P5.W2)', OLD.version_id;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_model_version_no_goalpost ON local_model_version;
CREATE TRIGGER trg_model_version_no_goalpost BEFORE UPDATE OR DELETE ON local_model_version
  FOR EACH ROW EXECUTE FUNCTION model_version_no_goalpost();
"""


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute("""SELECT c.relname, coalesce(string_agg(t.tgname, ', ' ORDER BY t.tgname), '(無)')
            FROM pg_class c LEFT JOIN pg_trigger t ON t.tgrelid=c.oid AND NOT t.tgisinternal
            WHERE c.relname IN ('governance_proposal','local_model_gold_sample','local_model_version')
            GROUP BY c.relname ORDER BY c.relname""")
        rows = cur.fetchall()
    if not rows:
        print("  (三表皆未建;--apply 建立)")
    for name, trgs in rows:
        print(f"  {name}: {trgs}")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        for label, ddl in DDL:
            cur.execute(ddl)
            print(f"✓ {label}")
        cur.execute(TRIGGERS)
        print("✓ triggers(提案凍結/gold append-only/版本挪門柱+人簽)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    ddl_all = " ".join(d for _, d in DDL)
    chk("提案內容凍結(diff/證據/類型不可改)", "內容送出即凍結" in TRIGGERS and "diff_text IS DISTINCT" in TRIGGERS)
    chk("gold append-only(UPDATE/DELETE 全拒)", "gold_sample_append_only" in TRIGGERS)
    chk("晉升須人簽(promoted_by+時戳)", "promoted_by IS NULL" in TRIGGERS and "P5.W2" in TRIGGERS)
    chk("三 hash 挪門柱鎖", all(h in TRIGGERS for h in ("train_sample_manifest_hash", "anchor_hash", "eval_code_hash")))
    chk("synthetic 恆真(P4.E7)", "CHECK (is_synthetic)" in ddl_all)
    chk("隱私欄 NOT NULL(禁送外部教師之機械依據)", "contains_private boolean NOT NULL" in ddl_all)
    chk("verdict 封閉集", "oracle_pass" in ddl_all and "human_ruled" in ddl_all)
    chk("冪等(IF NOT EXISTS×3+DROP TRIGGER IF EXISTS×3)",
        ddl_all.count("IF NOT EXISTS") == 3 and TRIGGERS.count("DROP TRIGGER IF EXISTS") == 3)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        print("現況(--check):")
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
