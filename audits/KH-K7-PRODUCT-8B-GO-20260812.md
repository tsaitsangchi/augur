# K7 產品預設 8b · GO

date: 2026-08-12  
kind: ops_go  
status: GO  
open: kh_opt_stepwise **K7**  
prior: `audits/KH-K7-STEPWISE-TONE-EXECUTED-20260812.md`

## 授權
1. 緊湊路徑產品預設 `AUGUR_COMPACT_NUM_PREDICT=960`（對齊 8b 達標帳）  
2. 步驟／操作題若落在 **4b** → 機械升同 effort **8b**（`AUGUR_STEPWISE_FORCE_8B` 預設開；可 =0 關）  
3. 維持 `frontend_tiers.default_tier=augur-8b-fast`；不刪 4b 檔位  

## 禁
默改 ultra `engine_model`；無尺抬 KH8；假 B3。
