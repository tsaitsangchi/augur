---
title: KH8 路徑 A1 · 擴薄項母體 go-plan
subtitle: 權重覆蓋未齊備項以破選擇效應；plan-only
status: plan
date: 2026-08-08
viewpoint: 2026-08-08T21:30+08:00
layer: "[I]"
parent_a: reports/augur_kh8_discrim_a_score_go_plan_20260808.md
a2_adopt: audits/KH8-DISCRIM-A2-ADOPTED-20260808.md
a2_sim: audits/KH8-DISCRIM-A2-SIM-EXECUTED-20260808.md
e_adopted: audits/KH8-DISCRIM-E-ADOPTED-20260808.md
paste: "KH8-DISCRIM-A1-thin-pop-go-plan | FZ/GATE-keep | no-fake-depth8 | E-keep | A2-compatible | hold-#1 | plan-only"
self_reported: true
---

# KH8-DISCRIM · A1 · 擴薄項母體 go-plan（2026-08-08）

> **一句**：現權重只落在「已句切＋已嵌＋eligible」→ terminal 恆 1、disc 結構失敗；A1＝**把薄項納入計分母體**（诚实低分），與 A2 改公式互補。  
> **本窗**＝plan-only；不寫庫。  
> **繼承**：E stop-at-7；A2 主軸已採納；A2-sim 全庫投影 minority≈2.4% 仍不足。

## §0 為何要 A1

| 現況 | 後果 |
|---|---|
| `knowhow_evidence_weight` n≈146k ≈ 可答齊備池 | 母體選擇效應（C-2） |
| terminal 分量 **146808/146808 = 1.0** | 判準(2′) 永難靠 terminal |
| 未入表：大量 depth0 標題件／無句／無嵌 | 從不進入 disc 分母 |
| A2 只重映射**已在表內**分數 | 可展開 band，但分量源不變 → 仍可能卡質量門 |

## §1 納入誰（建議分層）

| 層 | 條件 | 預期 band | 優先 |
|---|---|---|---|
| **T1** | 有 `item_text`、無 sentence 或無 embedding | low／absent | **先** |
| **T2** | 僅標題可理解（KH0 標題件）、無全文 | absent／low | 次（量大） |
| **T3** | kh4 ≠ eligible 但仍有文 | low＋risk_flags | 有界 |
| **不納** | 無 title 且無文 | — | 無從理解 |

禁：把薄項標成 high；禁為過 θ 而捏造 cite。

## §2 與 A2 關係

| | |
|---|---|
| **並行** | A1 擴分母／A2 改齊備牆——建議 **先 A1 試點寫影子表** 再套 A2 公式投影 |
| **成功** | 全庫（主表或宣佈全集）disc ok＝True **且** 人工抽樣 high≠僅齊備 |
| **證偽** | 灌大量 absent 只為堆 minority，答池／排序被垃圾淹沒 |

## §3 執行波（另 GO）

| 波 | 內容 |
|---|---|
| **A1-0** | 本 plan |
| **A1-1** | 計數缺口：有文未入 weight、標題件未入 weight（唯讀 SQL） |
| **A1-2** | 影子表／dry-run 插入 T1≤N（如 5k）＋disc 投影 |
| **A1-3** | Steward 裁是否併入主表；併入後仍 **E** 直到 ok |

## §4 Paste

```text
KH8-DISCRIM-A1-thin-pop-go-plan | FZ/GATE-keep | no-fake-depth8 | E-keep | A2-compatible | hold-#1 | plan-only
# 下一刀候選: KH8-DISCRIM-A1-gap-count | read-only
```

*完。[I] plan-only。*
