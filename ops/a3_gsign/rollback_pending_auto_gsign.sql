-- A3 乙案遷移之回滾（標記唯一可辨識，可全量還原；呈案 §4.2 原文）
-- 只還原「由 gate_set_migration_gsign 遷移、且未被 APPLY 消費（apply_log_id IS NULL）」之列。
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL augur.honesty_write = 'on';  -- 誠實帳本閘通行證(B4-P2a:promotion_queue 升 UPDATE-GUC 後必要)
UPDATE promotion_queue
   SET queue_status = 'pending_auto', decided_at = NULL, decided_by = 'evolution_engine'
 WHERE decided_by = 'gate_set_migration_gsign'
   AND queue_status = 'rejected_gate' AND apply_log_id IS NULL;
COMMIT;
