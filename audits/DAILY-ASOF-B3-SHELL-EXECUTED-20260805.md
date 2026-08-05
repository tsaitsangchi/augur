---
status: executed
series: daily_asof_ops
go: audits/DAILY-ASOF-B3-SHELL-GO-20260805.md
plan: reports/augur_daily_asof_b3_orchestrator_plan_20260805.md
impl: bash_shell
self_reported: true
---

# EXECUTED｜DAILY-ASOF-B3-SHELL · 2026-08-05

> **GO**：`DAILY-ASOF-B3-SHELL-go`（Steward；`impl=bash_shell`）  
> **deliverable**：`scripts/run_daily_asof_predict.sh` ＋ `--dry-plan`／`--selftest`  
> **非 cron** · FZ/GATE-keep · skip-sync · no-SIM-apply  
> **self-reported（#32a）**

## 1. 殼能力

| 旗標 | 行為 |
|---|---|
| `--date D` | 顯式 D；省略＝TAIEX `max(date)`（必印） |
| `--dry-plan` | 只印步驟／完整 CLI；**零寫庫** |
| `--horizons 20,60` | predict＋emit 迴圈 |
| `--skip-feat`／`--skip-core` | 跳過 |
| `--force-feat`／`--force-core` | 已有 D 仍重跑 |
| `--core-full` | 全量 `--full-rebuild`（非預設） |
| 預設 core | B1 `--incremental --asof-date D --skip-pan-hist` |
| 價閘 | `PriceAdj TAIEX max < D` → exit **3** 整鏈 SKIP |
| 驗收 | `build_single_ticker_rel_payload(2330,20).as_of == D` |

## 2. 煙測

| 測 | RC | 註 |
|---|---|---|
| `--selftest` | **0** | 路徑＋錨 |
| `--date 2026-08-04 --dry-plan` | **0** | feat/core **SKIP**（已有）；印 predict／emit／accept |
| `--dry-plan`（預設 D） | **0** | D 解析＝08-04 |
| `--date 2099-01-01 --dry-plan` | **3** | 價閘整鏈 SKIP |
| `--force-feat --force-core --dry-plan` | **0** | 印出 `build_feature_panel`＋`core-incr` CLI |

**本帳未**去 `--dry-plan` 真跑全鏈（P2 可另觸；08-04 熱路徑已齊）。

## 3. 文件同步

| 檔 | 變更 |
|---|---|
| runbook | 頭註 B3 殼入口 |
| standing ADOPTED／ops design paste | B 鏈 core＝**B1 incremental**＋編排句 |

## 4. 用法

```bash
bash scripts/run_daily_asof_predict.sh --dry-plan
bash scripts/run_daily_asof_predict.sh --date <D>
bash scripts/run_daily_asof_predict.sh --date <D> --force-core   # 刷新 core＠D
```

## 5. 不做

cron／systemd／`install_cron.sh` · 殼內 sync · P6 fit · sim-apply · 默授真跑本 GO

*完。P1＝殼＋dry-plan EXECUTED。*

## 6. P2 LIVE（Steward 手跑）

見 `audits/DAILY-ASOF-B3-P2-LIVE-20260804-EXECUTED-20260805.md`（D=2026-08-04 真跑＋force-core 皆完成）。
