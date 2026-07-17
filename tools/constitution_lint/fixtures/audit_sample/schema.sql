-- audit_lint fixture（MUST-FIX C 回歸鎖）：合規之行動留痕表——欄位含型別括號 VARCHAR(64)/NUMERIC(10,2)，
-- 且具 actor_identity 與 authorization_ref 欄。audit_lint 不得因型別括號誤截表身而誤報 AUD-10。
CREATE TABLE IF NOT EXISTS pipeline_execution_log (
    id                 BIGSERIAL PRIMARY KEY,
    task               VARCHAR(255) NOT NULL,
    amount             NUMERIC(10,2),
    started_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_identity     VARCHAR(64) NOT NULL,
    authorization_ref  TEXT
);
