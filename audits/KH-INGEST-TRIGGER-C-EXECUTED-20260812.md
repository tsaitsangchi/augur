# KH-INGEST-TRIGGER-C-EXECUTED · 2026-08-12

date: 2026-08-12  
kind: code_executed  
phase: **C**  
status: EXECUTED  
go: `audits/KH-INGEST-TRIGGER-C-GO-20260812.md`  
prior_b: `audits/KH-INGEST-TRIGGER-B-ADOPTED-20260812.md`

## 落地
| 件 | 路徑 |
|---|---|
| 訊號庫 | `src/augur/knowledge/ingest_triggers.py` |
| CLI | `scripts/kh_ingest_trigger.py` |
| 可選輪詢 | `scripts/kh_ingest_trigger_watch.sh`（**未**默裝 systemd／cron） |
| hook | `scripts/acquire_local_files.py` 入庫後 `hook_after_ingress` |

## 行為
- 預設：`--check`／hook **只量測＋建議**；寫 `~/.augur/kh_ingest_trigger_state.json` baseline  
- 有界 apply：`--apply` 或 `AUGUR_KH_INGEST_TRIGGER_APPLY=1` → **一次一槍**（優先 S0 drain `up_to=0` cap 500，或 S3 conc limit 200）  
- 關 hook：`AUGUR_KH_INGEST_TRIGGER=0`  
- **不**默開 AUTO-LIFT；**不**經 `install_cron`／`install_services` 安裝 timer  

## 驗收（本機）
- [x] `--selftest` PASS  
- [x] `--check` 印 S*；LIVE 見 S0=`kh0_breach=285`、S3 cursor lag（誠實；本帳**未**自動 `--apply` 全量清）  
- [x] `--dry-run` 預覽 argv＝`run_kh_chain --phase advance --up-to 0`（S0 優先）  
- [x] GO＋本 EXECUTED；r14 #29／readout 階 C 更新  

## paste
```text
KH-INGEST-TRIGGER-C-EXECUTED | check-default | apply=opt-in
| hook=acquire_local_files | no-default-timer | no-autolift-from-C
```
