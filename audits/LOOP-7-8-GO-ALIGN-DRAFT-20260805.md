---
status: draft_align
series: s1_s5_closed_loop
depends_on:
  - reports/augur_s4_s5_closed_loop_plan_20260804.md
  - reports/augur_s1_s2_s3_closed_loop_plan_20260804.md
  - audits/LOOP-S4-S5-FULL-GO-20260804.md
  - audits/SIM-S1-S2-S3-CLOSED-LOOP-20260804.md
---

# DRAFT｜LOOP 項 7／8 GO 對齊（零重訓）· 2026-08-05

> **授權**：Steward `docs_first`——**只對齊計畫／paste-ready GO，不開 train／OOS 寫庫**。  
> **對應清單**：#7＝C2 LOOP-S4↔S5；#8＝C1 LOOP-S3→S2。  
> **self-reported（#32a）**。

## 1. 現況（已落地，勿重跑當「默認下一步」）

| 弧 | GO／執行 | 狀態 |
|---|---|---|
| **#7 C2** S4→S5＋S5→S4-OPT | `audits/LOOP-S4-S5-FULL-GO-20260804.md` → EXECUTED | 首輪已跑；再輪須**新 artifact 可引用**＋新句 |
| **#8 C1** S3→S2 | `S2-KH-OPT-AFTER-S3-go`／`LOOP-S3-TO-S2-go` → L1 EXECUTED | L2／L3 **另句**；本 draft 不默授 |

## 2. Paste-ready（Steward 若要「下一輪」再貼）

### #7 — 單格 OOS／再評（僅 dry／唯讀為預設）

```
LOOP-S4-TO-S5-cell-go + GATE-keep + skip-sync + no-SIM-apply
# 指定: model_id=… horizon=… asof=…（須寫明可引用 artifact）
```

S5→S4 優化建議輪：

```
LOOP-S5-TO-S4-OPT-R2-go + GATE-keep + skip-sync + no-SIM-apply
```

### #8 — S3→S2 續弧

```
LOOP-S3-TO-S2-L2-go + GATE-keep + API-THAW-bounded + skip-sync
# 或 L3:
LOOP-S3-TO-S2-L3-go + GATE-keep + skip-sync
```

（≡ 延續 `S2-KH-OPT-AFTER-S3`；ingest 邊界仍見原 SIM 登錄，不因本 draft 放寬。）

## 3. 與 docs_first 交界

| 本輪做了 | 本輪不做 |
|---|---|
| 對齊 GO 句／勿誤以為「選 7／8＝立刻重訓」 | 任何 S4 train、S5 OOS 寫、S2 KH L2／L3 |
| 指向既有 EXECUTED／計畫路徑 | 撤 NF-pause、開 β2 `#11` |

## 4. 建議實際「可先做」順序（仍須各 GO）

1. 聊天／顧問路徑穩定（picks_skip 已落地）  
2. WM36 P1（本輪碼改）煙測通過  
3. 有新 S4 artifact 再說 #7 cell  
4. #8 L2 僅在 S3 側有新可引用命題後  

*定版草稿；執行須 Steward 貼上 §2 句之一。*
