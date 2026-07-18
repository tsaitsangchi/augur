-- Phase 1(d) 回退腳本：恢復施工前狀態（十表回隸 augur、augur 恢復完整 DML）
-- 於 augur 資料庫執行。角色保留（惰性）：斷登入用 ALTER ROLE augur_app NOLOGIN;
ALTER TABLE raw_supersede_log        OWNER TO augur;
ALTER TABLE entity_type_catalog      OWNER TO augur;
ALTER TABLE entity_registry          OWNER TO augur;
ALTER TABLE entity_alias             OWNER TO augur;
ALTER TABLE identity_claim           OWNER TO augur;
ALTER TABLE identity_lifecycle_event OWNER TO augur;
ALTER TABLE entity_attribute_version OWNER TO augur;
ALTER TABLE authorization_grant      OWNER TO augur;
ALTER TABLE automation_action_log    OWNER TO augur;
ALTER TABLE prediction_serving_log   OWNER TO augur;
ALTER FUNCTION raw_supersede_tombstone(bigint, text, text) OWNER TO augur;
ALTER FUNCTION identity_de_identify(text, text, text)      OWNER TO augur;
ALTER DEFAULT PRIVILEGES FOR ROLE augur     IN SCHEMA public REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES    FROM augur_app;
ALTER DEFAULT PRIVILEGES FOR ROLE augur     IN SCHEMA public REVOKE USAGE, SELECT                  ON SEQUENCES FROM augur_app;
ALTER DEFAULT PRIVILEGES FOR ROLE augur_app IN SCHEMA public REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES    FROM augur;
ALTER DEFAULT PRIVILEGES FOR ROLE augur_app IN SCHEMA public REVOKE USAGE, SELECT                  ON SEQUENCES FROM augur;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM augur_app;
REVOKE ALL ON SCHEMA public FROM augur_app;
ALTER ROLE augur_app NOLOGIN;
-- .env DB_USER 若已切換，改回 augur 並重啟服務
