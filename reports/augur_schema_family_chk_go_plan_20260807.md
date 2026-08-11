---
title: SCHEMA-FAMILY-CHK · model_registry family 白名單 plan-first
status: plan_first
series: schema
open_problem: "r12 #19"
date: 2026-08-07
viewpoint: 2026-08-07T14:12+08:00
paste: "SCHEMA-FAMILY-CHK-go-plan | FZ/GATE-keep | no-promote"
role: 挑戰族字面補入 CHECK 之計畫；本檔≠ DDL；≠升格／serve
depends_on:
  - reports/augur_opt_stepwise_best_next_plan_r12_20260807.md
  - audits/WAVE-A-BOUNDED-CLOSE-EXECUTED-20260807.md
probe_log: /tmp/schema-family-chk-20260807/probe.log
self_reported: true
---

# SCHEMA-FAMILY-CHK-go-plan｜`model_family_chk` · 2026-08-07

> **一句**：Wave-A 挑戰族可訓出 orphan joblib，但 **`model_family_chk` 擋 registry 寫入**——本檔把「僅補挑戰字面」做成 plan＋唯讀探針；**≠** ALTER 執行、**≠** promote、**≠** 換 LIVE serve。  
> **Hard doors**：`FZ/GATE-keep` · `no-promote` · `hold-#1` · `NF-pause keep` · `no-SIM-apply` · **勿重掃假綠**。

---

## §0 現況探針（唯讀 · 2026-08-07）

**現行 CHECK**：

```text
family = ANY (ARRAY[
  'RankRidge','RankGBDT','MktLogit','DirStack','DailyLogit',
  'DailyGBDT','DailyGBDT_cal','MktGBDT','DirStackM'
])
```

| family | CHK | code | registry n | joblib | 判讀 |
|---|:---:|:---:|---:|---:|---|
| RankRidge | ✅ | ✅ | 20 | 16 | LIVE 主族 |
| RankGBDT | ✅ | ✅ | 6 | 6 | 已允許 |
| RankXGB／Cat／RF／SVM／KNN／MLP | ❌ | ✅ | 0 | 3 each | **orphan**：CHK 擋 registry |
| Mkt*／Daily*／Dir* | ✅ | （direction 臂） | 有／空 | — | 保留；本刀**不刪** |

---

## §1 準許範圍（本計畫）

| 准 | 禁 |
|---|---|
| 文件化缺口；提議 **ADD ONLY** 六字面 | 本 paste 執行 `ALTER TABLE` |
| 後續另句 `SCHEMA-FAMILY-CHK-alter-go` 才 DDL | 升格／`prodset` 換挑戰族／SERVE-SWAP 到挑戰 |
| 登錄 orphan 路徑可溯 | 撤 NF-pause；同尺重掃假綠 |
| hold-#1；與日更正交 | 刪既有允許族；改 dgate；sim-apply |

**提議 ADD（草案，待 alter-go）**：

`RankXGB` · `RankCat` · `RankRF` · `RankSVM` · `RankKNN` · `RankMLP`

DDL 形（**僅草案**；未執行）：

```sql
ALTER TABLE model_registry DROP CONSTRAINT model_family_chk;
ALTER TABLE model_registry ADD CONSTRAINT model_family_chk
  CHECK (family = ANY (ARRAY[
    'RankRidge','RankGBDT','MktLogit','DirStack','DailyLogit',
    'DailyGBDT','DailyGBDT_cal','MktGBDT','DirStackM',
    'RankXGB','RankCat','RankRF','RankSVM','RankKNN','RankMLP'
  ]));
```

**之後仍須**：各族另有 `register`／artifact 入庫步驟（若 train 管線未自動 insert）——CHK 開≠自動入庫≠可交易。

---

## §2 為何現在只 plan＋probe

1. Wave-A 已 **STOP promote**（經濟未過門）——開 CHK 只是消「碼可訓、庫不可登」的**帳務洞**，不是翻案升格。  
2. Steward `no-promote` 釘死：字面入白名單 ≠ 挑戰變 LIVE。  
3. #1 候 A→B3：DDL 另窗、可回滾腳本、與日更錯開。

---

## §3 下一步 paste

採納本計畫（本窗已含）：

```text
SCHEMA-FAMILY-CHK-go-plan | FZ/GATE-keep | no-promote
```

真 DDL（另明示；本檔不授）：

```text
SCHEMA-FAMILY-CHK-alter-go | FZ/GATE-keep | no-promote | hold-#1 | ADD-only=RankXGB,RankCat,RankRF,RankSVM,RankKNN,RankMLP
```

入庫 orphan（再另句；可選）：

```text
SCHEMA-FAMILY-CHK-register-orphans-go | … | no-promote | no-serve-swap
```

---

## §4 驗收（本窗）

- [x] CHECK 全文＋ gap matrix 可溯（`/tmp/schema-family-chk-20260807/probe.log`）  
- [x] ADD-only 六字面寫死；保留既有九字面  
- [x] 明文 **no-promote／≠ serve／≠ 本窗 DDL**  
- [ ] ALTER → 須 `alter-go`  

*完。[I] plan-first · self-reported。*
