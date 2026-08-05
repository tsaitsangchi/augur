---
title: B3｜日更 as-of 編排薄殼 plan-first
status: shell_executed
acked: audits/DAILY-ASOF-B3-PLAN-ACK-20260805.md
shell: audits/DAILY-ASOF-B3-SHELL-EXECUTED-20260805.md
date: 2026-08-05
layer: "[I]"
series: daily_asof_ops
depends_on:
  - reports/augur_post_close_daily_asof_ops_design_20260805.md
  - reports/augur_daily_asof_predict_emit_runbook_20260805.md
  - audits/POST-CLOSE-DAILY-ASOF-standing-go-ADOPTED-20260805.md
  - audits/CORE-B1-INCREMENTAL-EXECUTED-20260805.md
self_reported: true
---

# B3 日更編排薄殼｜plan-first（2026-08-05）

> **性質**：[I] plan-first。**plan 原文為零腳本；殼已落地**（`scripts/run_daily_asof_predict.sh`）。**仍禁 cron／自動 timer。**  
> **觸發**：開問題「1＋2」→ 重刀選 `b3_plan`；B1 incremental **已** EXECUTED，編排可把 core 步從全量改增量。  
> **父**：ops design §3 候選 B3。

## 0. 一句話

**一個顯式 `D` 的薄殼：依序叫 runbook 各步、匯總 RC、失敗即停——人／半自動觸發，不是 timer。**

## 1. 為何現在

| 項 | 狀態 |
|---|---|
| standing GO | 已採；禁 systemd／`install_cron.sh` |
| B1 | ✅ upsert-D ~12s；日更 core 不再必付 10–15 min |
| 痛點 | 人手複製多段 CLI 易漏 `--incremental`／漏 H60／RC 未匯總 |
| 非目標 | 默設 cron（仍屬另句） |

## 2. 建議產物（解鎖後）

| 檔 | 職責 |
|---|---|
| `scripts/run_daily_asof_predict.sh`（或 `.py` 薄編排） | 解析 `D`；逐步呼叫；`set -e`／逐步 RC；寫 `/tmp` 或 `audits/` 一行摘要 |
| （可選）`--dry-plan` | 只印將跑指令、零寫庫 |

**不**新建業務邏輯；**不**繞過 `build_feature_panel`／`build_core_universe`／`predict_asof`／`calibrate_relative_probability`。

## 3. 標準日步驟（編排內容＝runbook 固化）

設 `D`＝參數；預設可讀 TAIEX `max(date)` 但**必須印出並可覆寫**。

| # | 條件 | 指令要旨 | 失敗 |
|---|---|---|---|
| 0 | 永遠 | 唯讀：PriceAdj／fv／core／pp | 價 `<D` → **整鏈 skip**＋告警字 |
| 1 | fv 無 `D` | `build_feature_panel.py --panels D --asof` | RC≠0 停 |
| 2 | core 無 `D` **或** 強制刷新 | `build_core_universe.py … --asof --incremental --asof-date D --skip-pan-hist` | 缺史／缺中間 → 明示改 full-rebuild 選項（旗標 `--core-full`） |
| 3–4 | 總跑 | `predict_asof.py --run --horizon {20,60} --asof D` | 停 |
| 5–6 | 總跑 | `calibrate_relative_probability.py --emit --horizon {20,60} --asof D` | 停 |
| 7 | 永遠 | `build_single_ticker_rel_payload("2330",20).as_of == D` | 非 D → 失敗 |

**standing 字面同步**：B 鏈 core 步由「since2014 全量 `--asof`」改為「**incremental＠D**（B1）」；全量僅 `--core-full`／週修。

## 4. CLI 草案

```text
scripts/run_daily_asof_predict.sh --date YYYY-MM-DD
  [--skip-feat] [--skip-core] [--core-full]
  [--horizons 20,60] [--dry-plan]
```

硬碼：`FZ` 語意＝本殼 **不**呼叫 sync／FinMind；呼叫端 A 車道另做。

## 5. 分階段

| 階段 | 產出 | 授權 |
|---|---|---|
| **P0（本檔）** | 契約＋步驟表 | Steward ack |
| **P1** | 實作薄殼＋`--dry-plan` selfsmoke | `DAILY-ASOF-B3-SHELL-go` |
| **P2** | 真跑一日（`D`=已有價日）＋ EXECUTED 摘要 | 同 GO 或另句；錯峰 heavy |
| **P3** | 更新 standing 貼文 core 步措辭 | 書面 |
| **P4** | timer／cron | **明示另授**；本 plan 永不默授 |

## 6. 硬禁

- 掛 systemd／改 `install_cron.sh`  
- 殼內 `P6 --fit`／OOS 全量／撤 NF／β5／sim `--apply`  
- 價未到仍 emit 昨日冒充 `D`  
- 默認全量 DELETE core（除非 `--core-full`）

## 7. Paste-ready

```text
DAILY-ASOF-B3-PLAN-ack
# 下一步實作：
DAILY-ASOF-B3-SHELL-go | FZ/GATE-keep | skip-sync | no-SIM-apply | no-cron
# deliverable: scripts/run_daily_asof_predict.sh + dry-plan; wire B1 incremental
```

## 8. 驗收（plan）

1. 步驟＝runbook 一一對應，core＝B1。  
2. 失敗閘與 standing 一致。  
3. 明文「非 cron」。

*完。[I] self-reported（#32a）。*
