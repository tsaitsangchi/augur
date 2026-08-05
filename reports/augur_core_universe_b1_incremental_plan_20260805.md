---
title: S3／日更 · core_universe_asof B1 增量（禁全表 DELETE）plan-first
status: executed
acked: audits/LIGHT-PARALLEL-PLANS-ACK-20260805.md
executed: audits/CORE-B1-INCREMENTAL-EXECUTED-20260805.md
date: 2026-08-05
layer: "[I]"
series: daily_asof_ops
open_problem: "#7"
depends_on:
  - reports/augur_post_close_daily_asof_ops_design_20260805.md
  - reports/augur_daily_asof_predict_emit_runbook_20260805.md
  - audits/POST-CLOSE-DAILY-ASOF-standing-go-ADOPTED-20260805.md
  - src/augur/universe/core_gate.py
self_reported: true
---

# core B1 增量｜plan-first（2026-08-05）

> **性質**：[I] plan-first（CLAUDE #20）。**本檔零改碼、零跑重建、零 cron。**  
> **開項**：開問題清單 **#7**（日更最貴步＝`build_universe_asof` 全表 DELETE）。  
> **觸發**：standing GO 已採（B 車道可手跑）；B1 列為「另 GO」候選——本檔＝那份 plan。

## 0. 一句話

**日更只要補 `as_of_date=D` 一層快照；不應為了多一天而 `DELETE` 整張 `core_universe_asof` 再重算 ≥2014 全史。**

## 1. 現況真兆（碼＋Ops）

| 錨 | 值 |
|---|---|
| 實作 | `core_gate.build_universe_asof`：`DELETE FROM core_universe_asof` 後對 `panel_dates` **逐 t** `_select_core`＋INSERT（`src/augur/universe/core_gate.py` ≈L206–233） |
| CLI | `scripts/build_core_universe.py … --asof`（runbook §2） |
| 估時 | 設計帳 ~**10–15 min**/日（ops design §1）；預測／emit 各 &lt;1 min |
| LIVE 對齊（2026-08-05 探針） | TAIEX／fv／core／pp **皆 max=2026-08-04**；core＠D **n≈204** |
| standing | B 車道**不含** B1；失敗閘＝PriceAdj&lt;D 跳過 |

**不變式（今日必須守住）**：asof 核心＝只用 ≤t 之 panels（消 survivorship #8）；canonical feats 跨全窗固定；liquidity 分位 point-in-time；金融月營收 conditional 豁免參數與現 CLI 一致。

## 2. 問題精確化

| 不是 | 是 |
|---|---|
| 「core 定義錯了」 | **計算正確但工程成本錯配**：每日全史重算 |
| 默授改 `--since D` | runbook §7 **禁**只重建 since D（會抹歷史 asof） |
| 默授 cron | standing＝手跑／半自動；timer **另授** |

## 3. 設計選項（擇一實作；本檔不選死）

| 代號 | 行為 | 效益 | 風險／需證 |
|---|---|---|---|
| **B1a upsert-D** | 若表已有歷史：只對 **新 panel `D`** 跑 `_select_core(≤D)` → `DELETE WHERE as_of_date=D`（若有）＋INSERT；**禁止**全表 DELETE | 日更 core → 秒～分 | 須證明與全量重算＠D **逐股一致**；缺中間 panel 時 fail-closed |
| **B1b since-last** | 自 `max(as_of_date)` 次日→D 逐日補 | 多日落後可補 | 同 B1a；落後日曆須完整 |
| **B1c dual-path** | `--incremental` 預設日更；`--full-rebuild` 保留現行為（週／破損修復） | 可逆 | CLI 旗標＋audit 分型 |
| **B1-defer** | 暫不改碼 | 零風險 | 日更續付 10–15 min |

**推薦實作序（拍板後）**：先 **B1c**（旗標護欄）落地 **B1a**；全量路徑保留作對照臂。

## 4. (a)(b) schema／python（解鎖後才寫）

| 層 | 內容 |
|---|---|
| schema | **無新表**；沿用 `core_universe_asof`／build meta |
| python | `core_gate.build_universe_asof_incremental(conn, d, …)` 或 `build_universe_asof(..., mode=)`；CLI `--incremental --asof-date D` |
| 不變式自測 | 零 DB：旗標互斥／空 D fail；有 DB 對照：同 D 上 incremental vs full 的 `stock_id` 集合 **差分＝∅**（抽樣＋全量各一 audit） |
| runbook | §2 增「日更偏好 `--incremental`」；§7 仍禁錯誤 since |

## 5. 分階段

| 階段 | 產出 | 授權 |
|---|---|---|
| **P0（本檔）** | Steward 知瓶頸＋選項 | 無碼 |
| **P1** | 不變式／對照臂設計記入 GO | `CORE-B1-INCREMENTAL-go`（仍可零碼） |
| **P2** | 實作＋selftest＋同 D 對照 EXECUTED | 另 GO；FZ/GATE-keep；skip-sync |
| **P3** | 改日更 runbook 預設 incremental | 書面 |
| **P4** | B3 薄殼編排／timer | **另句**；非本 plan |

## 6. 硬禁

- 改 core **定義**偷過完整度／流動性  
- 把 pan-historical `core_universe` 回填歷史 asof  
- FinMind 放量、sim `--apply`、撤 NF／β5  
- 未對照臂就刪全量路徑  

## 7. Paste-ready（候裁）

```text
CORE-B1-INCREMENTAL-PLAN-ack
# 或下一步（仍建議零碼先）：
CORE-B1-INCREMENTAL-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# scope: B1a+B1c design→code; full-rebuild retained; no cron
```

## 8. 驗收（plan 本身）

1. 痛點釘到 `DELETE FROM core_universe_asof` 一行級。  
2. 選項表含對照臂與 fail-closed。  
3. 明示與 standing GO／runbook 正交（日更可先不改碼繼續跑）。

*完。[I] self-reported（#32a）。*
