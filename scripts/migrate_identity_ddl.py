#!/usr/bin/env python
"""Layer 3 identity 表集 schema 遷移 — 六表冪等落地 + append-only 硬化(結構補正 AUD-04/05/06/07)。

🎯 這支在做什麼(白話):一次落地身份側六張新增表——
   entity_type_catalog(型別值域字典;#29b 型別值域住 DB)、entity_registry(系統鑄造之永久 augur_id)、
   entity_alias(外部碼降格 provisional alias)、identity_claim(跨來源同一性四要件 claim)、
   identity_lifecycle_event(mint/merge/split/retire/relist/redirect…事件序)、
   entity_attribute_version(身份屬性 as-of 雙時間 SCD-2)——**全部新增式、零既有消費者觸動**。
   **本腳本為表集 DDL 單一權威**(#12,內聯 CREATE TABLE;比照 migrate_prediction_ddl.py;identity package
   模組僅經 information_schema 消費、不重維 DDL)。
   **append-only 硬化**(比照 raw_supersede_log 之 trigger+REVOKE+SECURITY DEFINER 模式):
     · identity_claim / identity_lifecycle_event / entity_attribute_version → 嚴格 append-only
       (BEFORE UPDATE|DELETE RAISE,唯 de_identify 受控函式得繞過)+ BEFORE TRUNCATE RAISE;
     · entity_registry / entity_alias → 永久參照(BEFORE DELETE|TRUNCATE RAISE、允 UPDATE 供 status/alias 轉換);
     · REVOKE UPDATE/DELETE/TRUNCATE FROM PUBLIC(縱深);
     · identity_de_identify() SECURITY DEFINER(ID.42,唯一得繞過 append-only 之受控去識別化路徑,
       抹除自然人屬性內容本體但留骨架 + 標 entity_registry status=tombstoned)。
   全部 IF NOT EXISTS / CREATE OR REPLACE,非破壞新表型、重跑零副作用。

守 #6(冪等重跑安全、破壞性 DDL 非本表〔新表型〕)· #12(DDL 單一住所)· #29(個別可執行 + 指令矩陣 + graceful)·
   憲章 ID.11-61 · P4.E3/E5/E6。SSOT=結構補正設計卷宗(步 11)。

執行指令矩陣:
  python scripts/migrate_identity_ddl.py            # 冪等執行 DDL(表+index+trigger+de_identify)+ 印驗證清單
  python scripts/migrate_identity_ddl.py --check    # 唯讀:只印驗證清單、不執行 DDL
  python scripts/migrate_identity_ddl.py --selftest  # 紅綠鎖(DDL 結構不變式;免 DB 免 API;DB 相關者標注需 PG)

⚠ 未 apply 生產 DB:須於備援環境或人類本機跑 --check ＋ --selftest,經人類 #7 實測、#19 檢視、P5 拍板後
   apply 生產 DB、併 main。**殘餘風險**(比照 raw_supersede):表 owner 隱含保有全 DML、可 DISABLE/DROP
   TRIGGER;append-only 縱深只擋非 owner 角色,須部署層「表 owner ≠ 應用角色」方為完整機器保證。
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

# 注:`from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest(純 DDL 字串不變式)
#     零依賴可個別跑(#29 graceful;無 psycopg2/DB 亦驗結構鎖)。

# ── DDL。順序:表(FK 依賴序:catalog→registry→alias/claim/lifecycle/attr) → index → comment →
#    REVOKE → append-only 硬化 → TRUNCATE 堵 → de_identify 受控路徑 ──
DDL = [
    # 1) 型別值域字典(#29b 住 DB 非寫死 CHECK):新增型別=INSERT 一列;binding_kind_default 標 instance/type,
    #    type 節點(如 T.24 Automobile)不得鑄造為個體(identifier.mint 校驗)。
    #    namespace_key UNIQUE(ID.12 命名空間互斥之結構不變式:namespace_key↔entity_type 單射,同一 identifier
    #    不得解析至二 Type);immutable 硬化見 trg_type_catalog_immutable(已有 registry 參照即禁改寫)。
    ("table entity_type_catalog", """
        CREATE TABLE IF NOT EXISTS entity_type_catalog (
            entity_type          text PRIMARY KEY,
            ont_type_ref         text,
            top_category         text NOT NULL,
            namespace_key        text NOT NULL UNIQUE,
            binding_kind_default text NOT NULL DEFAULT 'instance',
            note                 text,
            created_at           timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT etc_top_category_chk
                CHECK (top_category IN ('Entity','Event','State','Relation','Quantity')),
            CONSTRAINT etc_binding_chk
                CHECK (binding_kind_default IN ('instance','type'))
        )"""),
    # 2) 系統鑄造之永久參照:每一世界個體恰一枚 augur_id,繫恰一 entity_type;永不刪除,下市/去識別化以
    #    status=tombstoned 標記(ID.13)。minted_by=P4.E6 斷言主體。
    ("table entity_registry", """
        CREATE TABLE IF NOT EXISTS entity_registry (
            augur_id     text PRIMARY KEY,
            entity_type  text NOT NULL REFERENCES entity_type_catalog(entity_type),
            minted_at    timestamptz NOT NULL DEFAULT now(),
            minted_by    text NOT NULL,
            evidence_ref text,
            status       text NOT NULL DEFAULT 'active',
            note         text,
            CONSTRAINT er_status_chk CHECK (status IN ('active','tombstoned'))
        )"""),
    # 3) 外部識別碼降格為 provisional alias(ID.30a):finmind stock_id/fred series_id/ISIN/統編… 繫 augur_id,
    #    供 resolution;非 identity claim 端點、不得逕充 identifier。雙時間 + alias_status(provisional/adopted/retired)。
    ("table entity_alias", """
        CREATE TABLE IF NOT EXISTS entity_alias (
            alias_id         bigserial PRIMARY KEY,
            augur_id         text NOT NULL REFERENCES entity_registry(augur_id),
            code_system      text NOT NULL,
            external_code    text NOT NULL,
            alias_status     text NOT NULL DEFAULT 'provisional',
            valid_from       date,
            valid_to         date,
            transaction_time timestamptz NOT NULL DEFAULT now(),
            evidence_ref     text,
            note             text,
            CONSTRAINT ea_status_chk CHECK (alias_status IN ('provisional','adopted','retired'))
        )"""),
    # 4) 跨來源同一性 claim 一級介面(ID.30 四要件):端點對(a<>b) + criterion_ref + evidence_ref + confidence
    #    槽位。**confidence_level 為 nullable 不透明槽位**——值域/語義權威住 L4(KS.31),L3 不寫 CHECK pin L4
    #    值域(避免單一權威漂移:L4 增級不致 L3 INSERT 失敗;issue ID.30(d))。append-only、衝突並存(禁 last-write-wins)。
    ("table identity_claim", """
        CREATE TABLE IF NOT EXISTS identity_claim (
            claim_id              bigserial PRIMARY KEY,
            augur_id_a            text NOT NULL REFERENCES entity_registry(augur_id),
            augur_id_b            text NOT NULL REFERENCES entity_registry(augur_id),
            criterion_ref         text NOT NULL,
            evidence_ref          text NOT NULL,
            confidence_level      text,
            confidence_method_ref text,
            asserted_by           text NOT NULL,
            valid_time            daterange,
            transaction_time      timestamptz NOT NULL DEFAULT now(),
            note                  text,
            CONSTRAINT ic_endpoints_distinct CHECK (augur_id_a <> augur_id_b)
        )"""),
    # 5) lifecycle 事件序(ID.40-44):event_type 為**開放集**(不寫死值域 CHECK);merge/split/retire/relist/
    #    correct(ID.40 含更正)+ settle/expire/convert/redeem(ID.44 DynamicEntity 終結)之 evidence_ref 為 NOT NULL
    #    硬義務(partial CHECK 表達,不鎖全型別值域)。lineage_parent FK→entity_registry(ID.41 lineage 參照完整、
    #    可重建;identifier 永不刪除故 FK 恆可滿足,對齊 redirect_target)。
    ("table identity_lifecycle_event", """
        CREATE TABLE IF NOT EXISTS identity_lifecycle_event (
            event_id         bigserial PRIMARY KEY,
            augur_id         text NOT NULL REFERENCES entity_registry(augur_id),
            event_type       text NOT NULL,
            redirect_target  text REFERENCES entity_registry(augur_id),
            lineage_parent   text REFERENCES entity_registry(augur_id),
            valid_time       timestamptz,
            transaction_time timestamptz NOT NULL DEFAULT now(),
            evidence_ref     text,
            actor            text NOT NULL,
            note             text,
            CONSTRAINT ile_evidence_chk CHECK (
                event_type NOT IN ('merge','split','retire','relist','correct',
                                   'settle','expire','convert','redeem')
                OR evidence_ref IS NOT NULL)
        )"""),
    # 6) 身份屬性 as-of 雙時間 SCD-2(ID.60):複合 PK 含 transaction_time;預設 clock_timestamp() 使同交易
    #    多次 put 之 transaction_time 相異、不撞 PK(now() 交易內恆等會撞)。禁原地覆蓋。
    ("table entity_attribute_version", """
        CREATE TABLE IF NOT EXISTS entity_attribute_version (
            augur_id         text NOT NULL REFERENCES entity_registry(augur_id),
            attribute_name   text NOT NULL,
            valid_from       date NOT NULL,
            transaction_time timestamptz NOT NULL DEFAULT clock_timestamp(),
            attribute_value  text,
            valid_to         date,
            source_ref       text,
            evidence_ref     text,
            PRIMARY KEY (augur_id, attribute_name, valid_from, transaction_time)
        )"""),
    # ── index ──
    ("index ix_alias_code", """
        CREATE INDEX IF NOT EXISTS ix_alias_code
          ON entity_alias (code_system, external_code)"""),
    ("index ix_alias_augur", """
        CREATE INDEX IF NOT EXISTS ix_alias_augur ON entity_alias (augur_id)"""),
    ("index ix_claim_a", """
        CREATE INDEX IF NOT EXISTS ix_claim_a ON identity_claim (augur_id_a)"""),
    ("index ix_claim_b", """
        CREATE INDEX IF NOT EXISTS ix_claim_b ON identity_claim (augur_id_b)"""),
    ("index ix_lifecycle_augur_time", """
        CREATE INDEX IF NOT EXISTS ix_lifecycle_augur_time
          ON identity_lifecycle_event (augur_id, transaction_time)"""),
    ("index ix_attr_asof", """
        CREATE INDEX IF NOT EXISTS ix_attr_asof
          ON entity_attribute_version (augur_id, attribute_name, valid_from)"""),
    # ── comment ──
    ("comment entity_registry", """
        COMMENT ON TABLE entity_registry IS
        '系統鑄造之永久 augur_id 參照(AUD-04;ID.11-14);永不刪除,下市/去識別化以 status=tombstoned 標記(非 DELETE);identifier 本身為具 Identity 地位之一級物件'"""),
    ("comment entity_alias", """
        COMMENT ON TABLE entity_alias IS
        '外部識別碼降格為 provisional alias(AUD-04/06;ID.30a);finmind stock_id/fred series_id/ISIN/統編 繫 augur_id,供 resolution、非 identity claim 端點、不得逕充 identifier'"""),
    ("comment identity_claim", """
        COMMENT ON TABLE identity_claim IS
        '跨來源同一性 claim 一級介面(AUD-06;ID.30-32 四要件);端點對 a<>b;append-only、衝突並存(禁 last-write-wins);confidence_level 為 nullable 不透明槽位(值域/語義權威住 L4 KS.31,L3 不 pin L4 值域);禁裸字串 join/欄位字面相等推定跨體系同一'"""),
    ("comment identity_lifecycle_event", """
        COMMENT ON TABLE identity_lifecycle_event IS
        'lifecycle 事件序(AUD-05;ID.40-44);event_type 開放集;merge/split/retire/relist/correct(ID.40 含更正)+ settle/expire/convert/redeem(ID.44 終結)之 evidence_ref 為 NOT NULL 硬義務;lineage_parent FK→entity_registry(ID.41 可重建);append-only(只失效不刪除);使 as-of 指向之存續個體可重建'"""),
    ("comment entity_attribute_version", """
        COMMENT ON TABLE entity_attribute_version IS
        '身份屬性 as-of 雙時間 SCD-2(AUD-07;ID.60-61);禁原地覆蓋(last-write-wins 為禁止型態);繫結存在為本層義務、as-of 重建引擎 DEFER Layer 4'"""),
    # ── 縱深防禦:REVOKE mutate FROM PUBLIC ──
    #   嚴格 append-only 三表:REVOKE UPDATE/DELETE/TRUNCATE;永久參照二表:REVOKE DELETE/TRUNCATE(允 UPDATE)。
    ("revoke mutate identity_claim", """
        REVOKE UPDATE, DELETE, TRUNCATE ON identity_claim FROM PUBLIC"""),
    ("revoke mutate identity_lifecycle_event", """
        REVOKE UPDATE, DELETE, TRUNCATE ON identity_lifecycle_event FROM PUBLIC"""),
    ("revoke mutate entity_attribute_version", """
        REVOKE UPDATE, DELETE, TRUNCATE ON entity_attribute_version FROM PUBLIC"""),
    ("revoke delete entity_registry", """
        REVOKE DELETE, TRUNCATE ON entity_registry FROM PUBLIC"""),
    ("revoke delete entity_alias", """
        REVOKE DELETE, TRUNCATE ON entity_alias FROM PUBLIC"""),
    # ── append-only 硬化:嚴格三表(BEFORE UPDATE|DELETE;唯 de_identify GUC 得繞過)──
    ("function identity_append_only", """
        CREATE OR REPLACE FUNCTION identity_append_only()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            IF current_setting('augur.identity_erase', true) IS DISTINCT FROM 'on' THEN
                RAISE EXCEPTION
                  'identity 表為 append-only(ID.31/ID.40/ID.60):%.% 之 % 遭拒;去識別化須經 identity_de_identify() 受控路徑',
                  TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP
                  USING ERRCODE = 'raise_exception';
            END IF;
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION
                  'identity 表不許實體 DELETE(即使去識別化):僅得 UPDATE 為 redacted 骨架(保留 augur_id/attribute_name/valid_from/transaction_time)'
                  USING ERRCODE = 'raise_exception';
            END IF;
            RETURN NEW;
        END;
        $fn$"""),
    ("trigger trg_claim_append_only", """
        DROP TRIGGER IF EXISTS trg_claim_append_only ON identity_claim;
        CREATE TRIGGER trg_claim_append_only
            BEFORE UPDATE OR DELETE ON identity_claim
            FOR EACH ROW EXECUTE FUNCTION identity_append_only()"""),
    ("trigger trg_lifecycle_append_only", """
        DROP TRIGGER IF EXISTS trg_lifecycle_append_only ON identity_lifecycle_event;
        CREATE TRIGGER trg_lifecycle_append_only
            BEFORE UPDATE OR DELETE ON identity_lifecycle_event
            FOR EACH ROW EXECUTE FUNCTION identity_append_only()"""),
    ("trigger trg_attr_append_only", """
        DROP TRIGGER IF EXISTS trg_attr_append_only ON entity_attribute_version;
        CREATE TRIGGER trg_attr_append_only
            BEFORE UPDATE OR DELETE ON entity_attribute_version
            FOR EACH ROW EXECUTE FUNCTION identity_append_only()"""),
    # ── permanence 硬化:永久參照二表(BEFORE DELETE 一律 RAISE;無 GUC 繞過——tombstone 走 UPDATE status)──
    ("function identity_no_delete", """
        CREATE OR REPLACE FUNCTION identity_no_delete()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              '%.% 為永久參照(ID.13):DELETE 一律禁止;下市/去識別化以 UPDATE status=tombstoned 標記',
              TG_TABLE_SCHEMA, TG_TABLE_NAME
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("trigger trg_registry_no_delete", """
        DROP TRIGGER IF EXISTS trg_registry_no_delete ON entity_registry;
        CREATE TRIGGER trg_registry_no_delete
            BEFORE DELETE ON entity_registry
            FOR EACH ROW EXECUTE FUNCTION identity_no_delete()"""),
    ("trigger trg_alias_no_delete", """
        DROP TRIGGER IF EXISTS trg_alias_no_delete ON entity_alias;
        CREATE TRIGGER trg_alias_no_delete
            BEFORE DELETE ON entity_alias
            FOR EACH ROW EXECUTE FUNCTION identity_no_delete()"""),
    # ── entity_type_catalog 型別/命名空間根之回溯不變式(ID.12):namespace_key/binding_kind_default/top_category
    #    一旦有 entity_registry 參照即不可原地改寫(回溯改寫使既有 augur_id 之 namespace_ok 失效、或改標已鑄 instance
    #    之型別 → 破 ID.12);新語義須 append 新 entity_type 列。seed UPSERT 亦僅補 ont_type_ref/note(見 seed 腳本)。──
    ("function identity_type_catalog_immutable", """
        CREATE OR REPLACE FUNCTION identity_type_catalog_immutable()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            IF (NEW.namespace_key        IS DISTINCT FROM OLD.namespace_key
                OR NEW.binding_kind_default IS DISTINCT FROM OLD.binding_kind_default
                OR NEW.top_category      IS DISTINCT FROM OLD.top_category)
               AND EXISTS (SELECT 1 FROM entity_registry WHERE entity_type = OLD.entity_type) THEN
                RAISE EXCEPTION
                  'entity_type=% 已有 entity_registry 參照:namespace_key/binding_kind_default/top_category 不可原地改寫(ID.12 命名空間互斥回溯不變式);新語義須 append 新 entity_type 列',
                  OLD.entity_type
                  USING ERRCODE = 'raise_exception';
            END IF;
            RETURN NEW;
        END;
        $fn$"""),
    ("trigger trg_type_catalog_immutable", """
        DROP TRIGGER IF EXISTS trg_type_catalog_immutable ON entity_type_catalog;
        CREATE TRIGGER trg_type_catalog_immutable
            BEFORE UPDATE ON entity_type_catalog
            FOR EACH ROW EXECUTE FUNCTION identity_type_catalog_immutable()"""),
    # ── TRUNCATE 堵:row-level trigger 攔不到 TRUNCATE → statement-level BEFORE TRUNCATE 一律 RAISE(五表) ──
    ("function identity_no_truncate", """
        CREATE OR REPLACE FUNCTION identity_no_truncate()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              '%.% 為 identity 帳表:TRUNCATE 一律禁止(整表抹除身份/證據);去識別化須逐列經 identity_de_identify()',
              TG_TABLE_SCHEMA, TG_TABLE_NAME
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("trigger trg_registry_no_truncate", """
        DROP TRIGGER IF EXISTS trg_registry_no_truncate ON entity_registry;
        CREATE TRIGGER trg_registry_no_truncate
            BEFORE TRUNCATE ON entity_registry
            FOR EACH STATEMENT EXECUTE FUNCTION identity_no_truncate()"""),
    ("trigger trg_alias_no_truncate", """
        DROP TRIGGER IF EXISTS trg_alias_no_truncate ON entity_alias;
        CREATE TRIGGER trg_alias_no_truncate
            BEFORE TRUNCATE ON entity_alias
            FOR EACH STATEMENT EXECUTE FUNCTION identity_no_truncate()"""),
    ("trigger trg_claim_no_truncate", """
        DROP TRIGGER IF EXISTS trg_claim_no_truncate ON identity_claim;
        CREATE TRIGGER trg_claim_no_truncate
            BEFORE TRUNCATE ON identity_claim
            FOR EACH STATEMENT EXECUTE FUNCTION identity_no_truncate()"""),
    ("trigger trg_lifecycle_no_truncate", """
        DROP TRIGGER IF EXISTS trg_lifecycle_no_truncate ON identity_lifecycle_event;
        CREATE TRIGGER trg_lifecycle_no_truncate
            BEFORE TRUNCATE ON identity_lifecycle_event
            FOR EACH STATEMENT EXECUTE FUNCTION identity_no_truncate()"""),
    ("trigger trg_attr_no_truncate", """
        DROP TRIGGER IF EXISTS trg_attr_no_truncate ON entity_attribute_version;
        CREATE TRIGGER trg_attr_no_truncate
            BEFORE TRUNCATE ON entity_attribute_version
            FOR EACH STATEMENT EXECUTE FUNCTION identity_no_truncate()"""),
    # ── ID.42 唯一得繞過 append-only 之受控去識別化路徑(SECURITY DEFINER;比照 raw_supersede_tombstone)──
    #    抹除自然人身份屬性內容本體(entity_attribute_version.attribute_value → '_redacted')但留骨架 + provenance;
    #    並標 entity_registry status=tombstoned。search_path 釘死(SECURITY DEFINER 安全慣例)。
    #    ⚠ 法規對應表本體與法源授權(自然人去識別化)DEFER Layer 6 IDO.7;本函式僅提供受控抹除骨架。
    ("function identity_de_identify", """
        CREATE OR REPLACE FUNCTION identity_de_identify(
            p_augur_id TEXT, p_reason TEXT, p_actor TEXT DEFAULT current_user)
        RETURNS void LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = pg_catalog, public AS $fn$
        BEGIN
            IF p_reason IS NULL OR btrim(p_reason) = '' THEN
                RAISE EXCEPTION 'identity_de_identify:去識別化須具明確 reason(ID.42 例外須留 provenance/法源對應)';
            END IF;
            -- 存在性檢查(比照姊妹函式 raw_supersede_tombstone,不對不存在 augur_id 靜默成功);置於 GUC 前故 not-found 分支無須還原
            IF NOT EXISTS (SELECT 1 FROM entity_registry WHERE augur_id = p_augur_id) THEN
                RAISE EXCEPTION 'identity_de_identify:augur_id=% 不存在(不靜默成功;呼叫端須先 mint/確認)', p_augur_id;
            END IF;
            PERFORM set_config('augur.identity_erase', 'on', true);   -- 僅本交易繞過 append-only
            UPDATE entity_attribute_version
               SET attribute_value = '_redacted',
                   source_ref = format('DE_IDENTIFY|erased_at=%s|actor=%s|reason=%s|prev=%s',
                                        now(), p_actor, p_reason, COALESCE(source_ref, ''))
             WHERE augur_id = p_augur_id;
            UPDATE entity_registry SET status = 'tombstoned' WHERE augur_id = p_augur_id;
            PERFORM set_config('augur.identity_erase', 'off', true);
        EXCEPTION WHEN OTHERS THEN
            PERFORM set_config('augur.identity_erase', 'off', true);   -- 失敗還原 GUC(比照姊妹函式;縱 is_local 交易 abort 亦不外洩,語義一致)
            RAISE;
        END;
        $fn$"""),
    ("revoke de_identify execute from public", """
        REVOKE EXECUTE ON FUNCTION identity_de_identify(TEXT, TEXT, TEXT) FROM PUBLIC"""),
    ("comment identity_de_identify", """
        COMMENT ON FUNCTION identity_de_identify(TEXT, TEXT, TEXT) IS
        'ID.42 唯一得繞過 append-only 之受控去識別化(SECURITY DEFINER、EXECUTE 須授權);抹除自然人屬性內容本體但留骨架＋provenance、標 registry status=tombstoned;法規對應表/法源 DEFER Layer 6 IDO.7'"""),
]

VERIFY = [
    ("entity_type_catalog 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='entity_type_catalog'"),
    ("entity_registry 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='entity_registry'"),
    ("entity_alias 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='entity_alias'"),
    ("identity_claim 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='identity_claim'"),
    ("identity_lifecycle_event 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='identity_lifecycle_event'"),
    ("entity_attribute_version 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='entity_attribute_version'"),
    ("FK 總覽(6 表)", "SELECT string_agg(conrelid::regclass||'→'||confrelid::regclass, ', ' ORDER BY conrelid::regclass::text) FROM pg_constraint WHERE contype='f' AND conrelid::regclass::text IN ('entity_registry','entity_alias','identity_claim','identity_lifecycle_event','entity_attribute_version')"),
    ("append-only/permanence triggers", "SELECT string_agg(tgrelid::regclass||'.'||tgname, ', ' ORDER BY tgrelid::regclass::text) FROM pg_trigger WHERE NOT tgisinternal AND tgrelid::regclass::text IN ('entity_registry','entity_alias','identity_claim','identity_lifecycle_event','entity_attribute_version')"),
    ("de_identify 受控函式(SECURITY DEFINER?)", "SELECT proname || CASE WHEN prosecdef THEN '(SECURITY DEFINER✓)' ELSE '(⚠非 DEFINER)' END FROM pg_proc WHERE proname='identity_de_identify'"),
    ("evidence 硬義務 CHECK(lifecycle)", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='ile_evidence_chk'"),
    ("PUBLIC 對 identity_claim 殘餘 mutate(應無 UPDATE/DELETE/TRUNCATE)", "SELECT COALESCE(string_agg(privilege_type,', '),'(無)') FROM information_schema.role_table_grants WHERE table_name='identity_claim' AND grantee='PUBLIC'"),
    ("entity_registry 現有列數", "SELECT count(*) FROM entity_registry"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001  表未建時 count 等會失敗 → 誠實印,不中斷
            print(f"  {label}: (查詢失敗:{e})")


def _selftest():
    """紅綠鎖(DDL 結構不變式;免 DB 免 API、零 usage)。DB 語義(trigger RAISE/回滾)需 PG,此處僅標注。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    labels = [lbl for lbl, _ in DDL]
    blob = "\n".join(sql for _, sql in DDL)
    # 六表皆有 CREATE TABLE IF NOT EXISTS(冪等新表型)
    tables = ("entity_type_catalog", "entity_registry", "entity_alias",
              "identity_claim", "identity_lifecycle_event", "entity_attribute_version")
    chk("六表皆 CREATE TABLE IF NOT EXISTS",
        all(f"CREATE TABLE IF NOT EXISTS {t}" in blob for t in tables))
    # FK 建表序:catalog 早於 registry、registry 早於 alias/claim/lifecycle/attr
    ci = labels.index("table entity_type_catalog")
    ri = labels.index("table entity_registry")
    chk("catalog 先於 registry(FK 序)", ci < ri)
    chk("registry 先於 alias/claim/lifecycle/attr(FK 序)",
        all(ri < labels.index(f"table {t}") for t in
            ("entity_alias", "identity_claim", "identity_lifecycle_event", "entity_attribute_version")))
    # event_type 開放集:lifecycle DDL 不得含 event_type 之 IN(...) 值域 CHECK(僅 evidence partial CHECK)
    lifecycle_ddl = dict(DDL)["table identity_lifecycle_event"]
    chk("event_type 為開放集(無值域 CHECK)",
        "event_type IN (" not in lifecycle_ddl and "ile_evidence_chk" in lifecycle_ddl)
    chk("evidence 硬義務 partial CHECK 含 ID.40 更正 + ID.44 終結型(非僅四型別)",
        "'merge','split','retire','relist','correct'" in lifecycle_ddl
        and "'settle','expire','convert','redeem'" in lifecycle_ddl
        and "evidence_ref IS NOT NULL" in lifecycle_ddl)
    chk("lineage_parent FK→entity_registry(ID.41 lineage 參照完整)",
        "lineage_parent   text REFERENCES entity_registry(augur_id)" in lifecycle_ddl)
    # ID.12:namespace_key UNIQUE(命名空間互斥單射)+ catalog immutable trigger(回溯不變式)
    catalog_ddl = dict(DDL)["table entity_type_catalog"]
    chk("entity_type_catalog.namespace_key UNIQUE(ID.12 命名空間互斥)",
        "namespace_key        text NOT NULL UNIQUE" in catalog_ddl)
    chk("entity_type_catalog immutable trigger(namespace_key/binding 有參照即禁改寫)",
        "trigger trg_type_catalog_immutable" in labels)
    # ID.30(a):端點對 a<>b;ID.30(d):L3 不 pin L4 confidence 值域(移除 ic_confidence_chk)
    claim_ddl = dict(DDL)["table identity_claim"]
    chk("identity_claim 端點對 a<>b(ID.30(a))",
        "CONSTRAINT ic_endpoints_distinct CHECK (augur_id_a <> augur_id_b)" in claim_ddl)
    chk("identity_claim 不 pin L4 confidence 值域(無 ic_confidence_chk;ID.30(d))",
        "ic_confidence_chk" not in claim_ddl and "'INSUF','LOW','MODERATE','STRONG','DETERMINISTIC'" not in claim_ddl)
    # 嚴格 append-only 三表皆掛 append_only trigger + no_truncate
    chk("三表掛 append-only trigger",
        all(f"trigger trg_{n}_append_only" in labels for n in ("claim", "lifecycle", "attr")))
    chk("五表皆掛 no_truncate trigger",
        all(f"trigger trg_{n}_no_truncate" in labels for n in
            ("registry", "alias", "claim", "lifecycle", "attr")))
    # 永久參照二表掛 no_delete
    chk("registry/alias 掛 no_delete trigger",
        all(f"trigger trg_{n}_no_delete" in labels for n in ("registry", "alias")))
    # REVOKE 縱深
    chk("三表 REVOKE UPDATE/DELETE/TRUNCATE FROM PUBLIC",
        all("REVOKE UPDATE, DELETE, TRUNCATE" in dict(DDL)[f"revoke mutate {t}"]
            for t in ("identity_claim", "identity_lifecycle_event", "entity_attribute_version")))
    # de_identify 為 SECURITY DEFINER + search_path 釘死 + REVOKE EXECUTE
    dei = dict(DDL)["function identity_de_identify"]
    chk("de_identify SECURITY DEFINER + search_path 釘死",
        "SECURITY DEFINER" in dei and "SET search_path = pg_catalog, public" in dei)
    chk("de_identify 抹除留骨架(_redacted)+ 標 tombstoned",
        "_redacted" in dei and "status = 'tombstoned'" in dei)
    chk("de_identify 存在性檢查 + EXCEPTION 還原 GUC(比照姊妹函式、不靜默成功)",
        "不存在" in dei and "EXCEPTION WHEN OTHERS" in dei)
    chk("de_identify REVOKE EXECUTE FROM PUBLIC",
        "REVOKE EXECUTE ON FUNCTION identity_de_identify" in blob)
    # attribute_version 複合 PK 含 transaction_time + clock_timestamp() 預設(同交易多 put 不撞 PK)
    attr = dict(DDL)["table entity_attribute_version"]
    chk("attr 複合 PK 含 transaction_time",
        "PRIMARY KEY (augur_id, attribute_name, valid_from, transaction_time)" in attr)
    chk("attr transaction_time 預設 clock_timestamp()",
        "transaction_time timestamptz NOT NULL DEFAULT clock_timestamp()" in attr)
    print("  DB 語義(trigger RAISE UPDATE/DELETE、no_delete/no_truncate、de_identify 受控繞過、同交易回滾):"
          "需 PG——備援環境 --check 驗存在 + 實測非 owner 角色 mutate/TRUNCATE 遭拒")
    print("自測:" + ("全通過 ✓(DDL 結構不變式綠;DB 語義需 PG)" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Layer 3 identity 表集 DDL 遷移(六表冪等 + append-only 硬化 + de_identify;內聯 DDL 單一權威)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(DDL 結構不變式;免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    from augur.core import db  # 延遲載入(psycopg2 僅 DDL 執行/--check 需要)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
