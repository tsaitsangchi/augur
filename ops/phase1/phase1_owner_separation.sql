-- Phase 1(d) owner 分離：生產施工腳本
-- 前提：(1) 生產備份已完成且經還原演練確認可用（L7.25 精神：未經實測之備份推定不存在）
--       (2) P5 書面核准在案（呈核單見 PHASE1-OWNER-SEPARATION-PACKAGE.md）
--       (3) 沙盒同構實測已通過（2026-07-18，證據見同目錄）
-- 冪等：可重跑。於 augur 資料庫執行：psql -U postgres -d augur -f phase1_owner_separation.sql

-- ═══ 1. 角色（叢集級；沙盒實測時已建，此段冪等跳過）═══
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='augur_owner') THEN CREATE ROLE augur_owner NOLOGIN; END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='augur_app')   THEN CREATE ROLE augur_app LOGIN;    END IF;
END $$;
-- ⚠ 密碼由施工者於 TTY 另行設定（不入版控）：ALTER ROLE augur_app PASSWORD '<新密碼>';

-- ═══ 2. 十張憲章表＋兩個 SECURITY DEFINER 函式改隸 augur_owner ═══
ALTER TABLE raw_supersede_log        OWNER TO augur_owner;
ALTER TABLE entity_type_catalog      OWNER TO augur_owner;
ALTER TABLE entity_registry          OWNER TO augur_owner;
ALTER TABLE entity_alias             OWNER TO augur_owner;
ALTER TABLE identity_claim           OWNER TO augur_owner;
ALTER TABLE identity_lifecycle_event OWNER TO augur_owner;
ALTER TABLE entity_attribute_version OWNER TO augur_owner;
ALTER TABLE authorization_grant      OWNER TO augur_owner;
ALTER TABLE automation_action_log    OWNER TO augur_owner;
ALTER TABLE prediction_serving_log   OWNER TO augur_owner;
ALTER FUNCTION raw_supersede_tombstone(bigint, text, text) OWNER TO augur_owner;
ALTER FUNCTION identity_de_identify(text, text, text)      OWNER TO augur_owner;

-- ═══ 3. augur_app：schema 使用＋建表（generic_schema 動態建 raw 表）＋零回歸廣域 DML ═══
GRANT USAGE, CREATE ON SCHEMA public TO augur_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO augur_app;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO augur_app;
GRANT EXECUTE                        ON ALL FUNCTIONS IN SCHEMA public TO augur_app;

-- ═══ 4. 憲章十表：append-only 由 ACL＋守衛 trigger 雙層強制（augur_app 與過渡期之 augur 一體適用）═══
REVOKE UPDATE, DELETE ON raw_supersede_log, entity_type_catalog, entity_registry, entity_alias,
  identity_claim, identity_lifecycle_event, entity_attribute_version, authorization_grant,
  automation_action_log, prediction_serving_log FROM augur_app;
GRANT SELECT, INSERT ON raw_supersede_log, entity_type_catalog, entity_registry, entity_alias,
  identity_claim, identity_lifecycle_event, entity_attribute_version, authorization_grant,
  automation_action_log, prediction_serving_log TO augur;      -- 過渡橋：.env 切換前 heal/mint 不斷線
REVOKE UPDATE, DELETE ON raw_supersede_log, entity_type_catalog, entity_registry, entity_alias,
  identity_claim, identity_lifecycle_event, entity_attribute_version, authorization_grant,
  automation_action_log, prediction_serving_log FROM augur;    -- 原 owner 的旁路一併關閉
GRANT UPDATE (superseded_by) ON prediction_serving_log TO augur_app, augur;  -- serving 標記例外（計畫明定）

-- ═══ 5. 未來新表之預設權限（過渡期雙向互通）═══
ALTER DEFAULT PRIVILEGES FOR ROLE augur     IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES    TO augur_app;
ALTER DEFAULT PRIVILEGES FOR ROLE augur     IN SCHEMA public GRANT USAGE, SELECT                  ON SEQUENCES TO augur_app;
ALTER DEFAULT PRIVILEGES FOR ROLE augur_app IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES    TO augur;
ALTER DEFAULT PRIVILEGES FOR ROLE augur_app IN SCHEMA public GRANT USAGE, SELECT                  ON SEQUENCES TO augur;

-- ═══ 6. 驗收（施工後立即執行；任一不符即回退）═══
-- (a) SELECT tablename, tableowner FROM pg_tables WHERE tablename='raw_supersede_log';       → augur_owner
-- (b) SET ROLE augur_app; BEGIN; INSERT INTO raw_supersede_log ("table",pk,old_row,new_row,reason)
--     VALUES ('_verify','{}','{}','{}','value_mismatch:verify'); ROLLBACK; RESET ROLE;       → 成功
-- (c) SET ROLE augur; DELETE FROM raw_supersede_log WHERE id=0; RESET ROLE;                  → 42501 權限拒
-- (d) 應用以 augur_app 連線後跑一輪唯讀健檢＋heal dry-run                                    → 綠
