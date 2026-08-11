---
title: KH8 影子→主表合併 · 裁決 go-plan（高門檻）
subtitle: 實驗綠如何（或不）成為生產綠；本檔不施作合併
status: plan
date: 2026-08-08
viewpoint: 2026-08-08T21:40+08:00
layer: "[I]"
s2: audits/KH8-DISCRIM-A1-T2-SHADOW-S2-EXECUTED-20260808.md
e_adopted: audits/KH8-DISCRIM-E-ADOPTED-20260808.md
paste: "KH8-DISCRIM-merge-adjudication-go-plan | high-bar | no-merge-yet | E-keep | hold-#1 | plan-only"
self_reported: true
---

# KH8-DISCRIM · 影子→主表合併裁決 go-plan（2026-08-08）

> **一句**：主∪全 T2 影已 **ok=True**，但那是**實驗母體**；併入生產主表會改變 `population_discriminates`、排序閘與答池風險——**須 Steward 書面裁**，本檔只列條件。  
> **本窗**＝plan-only；**不** MERGE、**不**改 advise 讀徑。

## §0 現況（裁奪輸入）

| 母體 | disc | 說明 |
|---|---|---|
| 主 `knowhow_evidence_weight` | **ok=False** | 生产 SSOT 仍此 |
| 主∪`shadow_t2`（139,043 absent） | **ok=True** · minority≈0.49 | 實驗 |
| E 採納 | stop-at-7 直至**生产** disc 真綠 | `KH8-DISCRIM-E-ADOPTED` |
| A2 | 公式主軸已採納、**碼未落地** | 影列用草案；主列仍舊公式 |

## §1 合併選項（擇一；不代選生效）

| ID | 內容 | 影响 | 風險 |
|---|---|---|---|
| **M0 永不併** | 影只作研究／回歸基線；生产永遠主表 | 零生产变盘 | 低；disc 生产续红 |
| **M1 有界併** | 只併 T2 的 **域子集**（如 `local`∪哲學）或 cap≤N | 局部盘可能綠 | 中 |
| **M2 全量併** | 139k 標題列寫入主表（absent／low） | **生产 disc 預期轉綠** | **高**：答池／ANN／KH8 消费若誤讀權重 |
| **M3 併＋切讀** | M2 + 硬碼「權重≠可答」；retrieve 仍要求 has_text | 降污染 | 中高；要碼闸 |
| **M4 先 A2 碼再併** | 主列改 A2 後再決定是否併 T2 | 尺一致 | 中；工期 |

**建議討論預設（非自動）**：**M0 或 M3**；**不薦裸 M2**（無答池闸）。

## §2 若裁「准合併」之強制閘（缺一不可）

1. **双明示 paste**（本 plan 不足）：含 M-id、N、域、回滚。  
2. **答池闸**：`retrieve`／readout／AUTO-LIFT **不得**仅因 weight 列命中標題件；须 `has_text` 或等价。  
3. **回归锁**：合并前后國碩錨 277948＋N 条随机有文题；不得变「无此内容」或乱 cite 标题海。  
4. **E 复验**：仅当**主表** `population_discriminates` ok=True **且** 闸2通过，方可议「撤 stop-at-7」——**另裁**，非自动。  
5. **可回滚**：批次 `batch_id`、DELETE 脚本、主表备份点。  
6. **hold-#1**：合并窗口让日更（勿与 B3 抢盘）。

## §3 明确禁

- 静默 MERGE；影子表挂到 advise 默认检索  
- 因实验 ok=True 宣告 depth≥8／KH8 进化成功  
- 只为过 θ 灌标题又不设答池闸（证伪条件）

## §4 Paste

```text
KH8-DISCRIM-merge-adjudication-go-plan | high-bar | no-merge-yet | E-keep | hold-#1 | plan-only
# 待裁: M0|M1|M3|M4 （不薦裸 M2）
# 准合併另贴: KH8-DISCRIM-merge-M?-go | dual-explicit | pool-gate | rollback
```

*完。[I] plan-only。*
