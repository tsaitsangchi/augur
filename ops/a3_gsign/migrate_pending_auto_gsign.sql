-- A3 乙案遷移（Steward 拍板 2026-08-01：77 筆採乙案「重評＋遷移」）
-- 把舊閘集（七鍵、無 G-SIGN）之 pending_auto 一次收斂為 rejected_gate——
-- 死因如實＝「閘集遷移」非「閘判不過」（decided_by 機器標記、非人簽，不觸「不代打人簽」）。
-- DML 非 DDL；gate_json 一字不碰（證據禁事後改寫）。
-- 前置：於 A3 四件套 commit 之後執行；執行者＝主 session（本檔只備妥）。
-- 冪等：謂詞只收「無 G-SIGN 鍵之 pending_auto」——重跑零效果。
-- 呈案時點目標列數=77（2026-08-01 親驗；執行當下以 NOTICE 印出之現數為準）。
-- 回滾：ops/a3_gsign/rollback_pending_auto_gsign.sql
BEGIN;
SET LOCAL lock_timeout = '5s';

-- 斷言一：目標列不得帶 apply_log_id（pending_auto 本不該有；有＝帳本異常，中止人查）
-- 斷言二：印出目標列數（0＝已遷移過，冪等重跑屬正常）
DO $$
DECLARE
  n_bad int;
  n_target int;
BEGIN
  SELECT count(*) INTO n_bad FROM promotion_queue
   WHERE queue_status = 'pending_auto'
     AND NOT (gate_json ? 'G-SIGN')
     AND apply_log_id IS NOT NULL;
  IF n_bad > 0 THEN
    RAISE EXCEPTION 'A3 遷移中止：% 列 pending_auto 竟帶 apply_log_id（帳本異常，人查）', n_bad;
  END IF;
  SELECT count(*) INTO n_target FROM promotion_queue
   WHERE queue_status = 'pending_auto'
     AND NOT (gate_json ? 'G-SIGN');
  RAISE NOTICE 'A3 遷移目標列數=%（呈案時點=77；冪等重跑=0 屬正常）', n_target;
END $$;

UPDATE promotion_queue
   SET queue_status = 'rejected_gate',
       decided_at   = now(),
       decided_by   = 'gate_set_migration_gsign'
 WHERE queue_status = 'pending_auto'
   AND NOT (gate_json ? 'G-SIGN');
-- 預期 UPDATE 77（執行當下以上方 NOTICE 現數為準；V5 驗收＝遷移後
-- SELECT count(*) FROM promotion_queue WHERE queue_status='pending_auto' AND NOT (gate_json ? 'G-SIGN') → 0）

COMMIT;
