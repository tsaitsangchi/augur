# KH-INGEST-TRIGGER-C-GO · 2026-08-12

date: 2026-08-12  
kind: code_go  
phase: **C**（碼／hook／可選輪詢）  
status: GO  
prior: `audits/KH-INGEST-TRIGGER-B-ADOPTED-20260812.md`  
plan: `reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md` §4

## 授權範圍
1. `src/augur/knowledge/ingest_triggers.py` — 量 S*、優先序、輕量建議／有界 apply  
2. `scripts/kh_ingest_trigger.py` — `--check`／`--dry-run`／`--apply`／`--selftest`  
3. `acquire_local_files` 成功後 **hook**：預設只 `--check`（日誌）；`AUGUR_KH_INGEST_TRIGGER_APPLY=1` 才有界 apply  
4. 可選 `scripts/kh_ingest_trigger_watch.sh`（訊號輪詢；**不**經 install_cron／install_services 默裝）

## 硬禁
- 無訊號仍全庫進化；日曆「進化日」timer 默裝  
- timer／hook **默開** AUTO-LIFT  
- 每檔全鏈 KH3–9；搶 B3 時硬跑重 LLM  

## 驗收
- `--selftest` 綠  
- `--check` 印 S*＋建議；無 P0／P1 時 apply＝no-op  
- S0>0＋`--apply` → 僅有界 `--phase advance --up-to 0`（limit 封頂）  
- GO／EXECUTED 帳＋r14 #29 C 更新  
