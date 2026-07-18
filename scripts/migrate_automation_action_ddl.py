#!/usr/bin/env python
"""自動行動授權/留痕 schema 遷移 — authorization_grant + automation_action_log(AUD-10/11)。

🎯 這支在做什麼(白話):落地兩張新增表,把「會改變 Reality 的自動行動」結構化——
   authorization_grant(機讀授權登錄:授權人已解析 Identity、scope_params 參數邊界、生效日、依據文件引用;
   將現存 shell 註解「hugo YYYY-MM-DD 拍板」逐筆遷入為結構化授權——遷入本身列 follow-up Phase 5)、
   automation_action_log(P5.E1 **六元組**留痕:Actor Identity/Authorization/Knowledge Basis/Timestamp/
   Expected Effect/Observed Effect〔FK→attestation_result〕,取代家目錄純文字 log)。
   **與既有 pipeline_execution_log / data_audit_log 並存、不改既有表**。permanence 硬化:
   BEFORE DELETE|TRUNCATE RAISE(允 UPDATE 供 action 收尾填 ended_at/observed_effect)+ REVOKE FROM PUBLIC。
   全部 IF NOT EXISTS / CREATE OR REPLACE,非破壞新表型、重跑零副作用。

守 #6(冪等)· #12(DDL 單一住所)· #29(個別可執行 + 指令矩陣 + graceful)· P5.E1(Action 六元組)· P4.E3/E6。
   單一寫入源=src/augur/execution/action_log.py。

執行指令矩陣:
  python scripts/migrate_automation_action_ddl.py            # 冪等執行 DDL + 印驗證清單
  python scripts/migrate_automation_action_ddl.py --check    # 唯讀:只印驗證清單、不執行 DDL
  python scripts/migrate_automation_action_ddl.py --selftest  # 紅綠鎖(DDL 結構不變式;免 DB 免 API)

⚠ **前置**:automation_action_log.observed_effect_ref FK→attestation_result(由 core/schema.py INFRA_DDL
   之 bootstrap_infra 建),故本遷移**須在 bootstrap_infra 之後執行**;未建 attestation_result 時 main() 先
   fail-fast 印明確提示(『先跑 bootstrap_infra』),不讓 FK 建表報 relation does not exist、不留半殘交易。
⚠ 未 apply 生產 DB:須經人類 #7 實測、#19 檢視、P5 拍板後 apply、併 main。owner 殘餘風險同 raw_supersede。
"""
import argparse
import sys

import _bootstrap  # noqa: F401

# `from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest 零依賴可個別跑(#29)。

DDL = [
    # 機讀授權登錄(AUD-10):P5.E1 六元組之 Authorization 落地。scope_params=jsonb 參數邊界(如 {"targets":["augur-chat"],
    # "max_relaunch":3});basis_doc_ref=依據文件引用(拍板卷宗/handoff 段落)。
    ("table authorization_grant", """
        CREATE TABLE IF NOT EXISTS authorization_grant (
            authorization_id bigserial PRIMARY KEY,
            grantor_identity text NOT NULL,
            scope_params     jsonb NOT NULL DEFAULT '{}'::jsonb,
            effective_from   date NOT NULL,
            basis_doc_ref    text NOT NULL,
            created_at       timestamptz NOT NULL DEFAULT now(),
            note             text
        )"""),
    # P5.E1 六元組留痕(AUD-10/11):observed_effect_ref FK→attestation_result(既有 INFRA 表,故本 FK 依賴其存在;
    # bootstrap_infra 已建 attestation_result)。knowledge_basis/expected_effect=jsonb。status:started/completed/failed。
    ("table automation_action_log", """
        CREATE TABLE IF NOT EXISTS automation_action_log (
            action_id           bigserial PRIMARY KEY,
            actor_identity      text NOT NULL,
            authorization_ref   bigint REFERENCES authorization_grant(authorization_id),
            knowledge_basis     jsonb,
            action_type         text NOT NULL,
            target              text,
            expected_effect     jsonb,
            observed_effect_ref bigint REFERENCES attestation_result(id),
            started_at          timestamptz NOT NULL DEFAULT now(),
            ended_at            timestamptz,
            status              text NOT NULL DEFAULT 'started',
            CONSTRAINT aal_status_chk CHECK (status IN ('started','completed','failed'))
        )"""),
    ("index ix_action_actor_time", """
        CREATE INDEX IF NOT EXISTS ix_action_actor_time
          ON automation_action_log (actor_identity, started_at)"""),
    ("index ix_action_auth", """
        CREATE INDEX IF NOT EXISTS ix_action_auth
          ON automation_action_log (authorization_ref)"""),
    ("comment authorization_grant", """
        COMMENT ON TABLE authorization_grant IS
        '自動行動之機讀授權登錄(AUD-10;P5.E1 Authorization);將 shell 註解 hugo 拍板遷入為結構化授權(遷入列 follow-up Phase 5);MC §8.3 Identity 歸因可機器稽核'"""),
    ("comment automation_action_log", """
        COMMENT ON TABLE automation_action_log IS
        '自動行動 P5.E1 六元組留痕(AUD-10/11):Actor/Authorization/Knowledge Basis/Timestamp/Expected/Observed(FK→attestation_result);承接 watchdog/selfheal kill/relaunch、heal 放量重抓;取代家目錄純文字 log;permanence(no-DELETE/no-TRUNCATE、允 UPDATE 收尾)'"""),
    # permanence 硬化:no-DELETE/no-TRUNCATE(留痕不可抹除;允 UPDATE 供 link_observed_effect 收尾)+ REVOKE。
    ("revoke delete authorization_grant", """
        REVOKE DELETE, TRUNCATE ON authorization_grant FROM PUBLIC"""),
    ("revoke delete automation_action_log", """
        REVOKE DELETE, TRUNCATE ON automation_action_log FROM PUBLIC"""),
    ("function automation_no_delete", """
        CREATE OR REPLACE FUNCTION automation_no_delete()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              '%.% 為行動留痕帳表(P4.E3/P5.E1):DELETE 一律禁止(行動記錄不可抹除);收尾以 UPDATE 填 ended_at/observed_effect',
              TG_TABLE_SCHEMA, TG_TABLE_NAME
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("function automation_no_truncate", """
        CREATE OR REPLACE FUNCTION automation_no_truncate()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              '%.% 為行動留痕帳表(P4.E3/P5.E1):TRUNCATE 一律禁止(整表抹除行動記錄)',
              TG_TABLE_SCHEMA, TG_TABLE_NAME
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("trigger trg_authz_no_delete", """
        DROP TRIGGER IF EXISTS trg_authz_no_delete ON authorization_grant;
        CREATE TRIGGER trg_authz_no_delete
            BEFORE DELETE ON authorization_grant
            FOR EACH ROW EXECUTE FUNCTION automation_no_delete()"""),
    ("trigger trg_action_no_delete", """
        DROP TRIGGER IF EXISTS trg_action_no_delete ON automation_action_log;
        CREATE TRIGGER trg_action_no_delete
            BEFORE DELETE ON automation_action_log
            FOR EACH ROW EXECUTE FUNCTION automation_no_delete()"""),
    ("trigger trg_authz_no_truncate", """
        DROP TRIGGER IF EXISTS trg_authz_no_truncate ON authorization_grant;
        CREATE TRIGGER trg_authz_no_truncate
            BEFORE TRUNCATE ON authorization_grant
            FOR EACH STATEMENT EXECUTE FUNCTION automation_no_truncate()"""),
    ("trigger trg_action_no_truncate", """
        DROP TRIGGER IF EXISTS trg_action_no_truncate ON automation_action_log;
        CREATE TRIGGER trg_action_no_truncate
            BEFORE TRUNCATE ON automation_action_log
            FOR EACH STATEMENT EXECUTE FUNCTION automation_no_truncate()"""),
]

VERIFY = [
    ("authorization_grant 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='authorization_grant'"),
    ("automation_action_log 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='automation_action_log'"),
    ("FK(action→authz / action→attestation_result)", "SELECT string_agg(pg_get_constraintdef(oid),' | ') FROM pg_constraint WHERE conrelid='automation_action_log'::regclass AND contype='f'"),
    ("permanence triggers", "SELECT string_agg(tgrelid::regclass||'.'||tgname, ', ' ORDER BY tgname) FROM pg_trigger WHERE NOT tgisinternal AND tgrelid::regclass::text IN ('authorization_grant','automation_action_log')"),
    ("PUBLIC 對 automation_action_log 殘餘 mutate(應無 DELETE/TRUNCATE)", "SELECT COALESCE(string_agg(privilege_type,', '),'(無)') FROM information_schema.role_table_grants WHERE table_name='automation_action_log' AND grantee='PUBLIC'"),
    ("既有 pipeline_execution_log 仍在(不改既有表)", "SELECT to_regclass('pipeline_execution_log') IS NOT NULL"),
    ("automation_action_log 現有列數", "SELECT count(*) FROM automation_action_log"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001
            print(f"  {label}: (查詢失敗:{e})")


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    labels = [lbl for lbl, _ in DDL]
    blob = "\n".join(sql for _, sql in DDL)
    chk("兩表皆 CREATE TABLE IF NOT EXISTS(冪等新表型)",
        "CREATE TABLE IF NOT EXISTS authorization_grant" in blob
        and "CREATE TABLE IF NOT EXISTS automation_action_log" in blob)
    chk("authz 先於 action(FK 建表序)",
        labels.index("table authorization_grant") < labels.index("table automation_action_log"))
    chk("action FK→authorization_grant + attestation_result",
        "REFERENCES authorization_grant(authorization_id)" in blob
        and "REFERENCES attestation_result(id)" in blob)
    chk("六元組欄齊(actor/auth/knowledge/expected/observed/timestamp)",
        all(c in blob for c in ("actor_identity", "authorization_ref", "knowledge_basis",
                                "expected_effect", "observed_effect_ref", "started_at", "ended_at")))
    chk("permanence:兩表皆掛 no_delete + no_truncate",
        all(f"trigger trg_{n}_no_delete" in labels and f"trigger trg_{n}_no_truncate" in labels
            for n in ("authz", "action")))
    chk("REVOKE DELETE/TRUNCATE FROM PUBLIC(兩表)",
        "REVOKE DELETE, TRUNCATE ON authorization_grant FROM PUBLIC" in blob
        and "REVOKE DELETE, TRUNCATE ON automation_action_log FROM PUBLIC" in blob)
    chk("允 UPDATE(收尾 link_observed_effect):no_delete trigger 僅 BEFORE DELETE、非 UPDATE",
        "BEFORE DELETE ON automation_action_log" in blob
        and "BEFORE UPDATE" not in blob)
    print("  DB 語義(DELETE/TRUNCATE RAISE、UPDATE 收尾放行):需 PG——備援環境 --check + 實測")
    print("自測:" + ("全通過 ✓(DDL 結構不變式綠;DB 語義需 PG)" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="自動行動授權/留痕 DDL 遷移(authorization_grant + automation_action_log;冪等 + permanence 硬化)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(DDL 結構不變式;免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    from augur.core import db  # 延遲載入(psycopg2 僅 DDL 執行/--check 需要)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            cur.execute("SELECT to_regclass('attestation_result')")
            if cur.fetchone()[0] is None:
                sys.exit("✗ 前置缺 attestation_result(observed_effect_ref FK 依賴);先跑 bootstrap_infra"
                         "(core/schema.py INFRA_DDL)建 attestation_result 再重跑本遷移")
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
