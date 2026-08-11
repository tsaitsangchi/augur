---
title: KH8 A1-T2 · 標題件影子表 go-plan
subtitle: 139k 僅標題納入 disc 母體之影子實驗；不换主表
status: plan
date: 2026-08-08
viewpoint: 2026-08-08T21:40+08:00
layer: "[I]"
gap: audits/KH8-DISCRIM-A1-GAP-EXECUTED-20260808.md
a1_adopt: audits/KH8-DISCRIM-A1-ADOPTED-20260808.md
paste: "KH8-DISCRIM-A1-T2-shadow-go-plan | title-only | shadow-only | no-main-swap | E-keep | hold-#1 | plan-only"
self_reported: true
---

# KH8-DISCRIM · A1-T2-shadow go-plan（2026-08-08）

> **一句**：T2≈**139,043** 僅標題未入 weight——用**影子表**诚实低分納入 disc 投影，**禁止**默默換主表／汙染答池。  
> 依 `A1-GAP-EXECUTED`：T1≈2 可忽略；槓杆＝T2。

## §0 目標／非目標

| 目標 | 非目標 |
|---|---|
| 影子母體 = 主 weight ∪ T2 低分列 | 主表 `knowhow_evidence_weight` 一次灌滿 |
| 量 disc（band／分量少數質量） | 宣佈 KH8 全庫綠、抬 depth≥8 |
| 隔離：advisor 排序**不**讀影子 | 標題海進入 cite 熱路徑 |

## §1 影子列定義（草案）

對每個 T2 item（無 `item_text`、有 title／title_zh、無主 weight）：

```text
citation_count=0
has_text=False  → terminal=0
has_sentence=False
has_embedding=False → embed=0
kh4_ok=0（或依實況；無 kh4→0）
contra=0
→ 走 A2 草案或 legacy compute → 預期 band=absent／low
risk_flags += title_only_no_fulltext
```

表名建議：`knowhow_evidence_weight_shadow_t2`（或 `…_a1t2`）· **TTL／批次 id** · 可 DROP。

## §2 波次（另 GO 才建表）

| 波 | 內容 | 禁 |
|---|---|---|
| **S0** | 本 plan | — |
| **S1** | DDL 影子表＋`N=5000` 抽樣填入＋disc(主∪影) | 主表寫 |
| **S2** | `N=全 T2` 影子填入＋disc；對照污染指標（答池命中 rate） | 熱路徑讀影 |
| **S3** | Steward 裁是否 **有界合併主表**（須双明示＋E 複核） | 默併；假綠 |

## §3 成功／證偽

| 成功 | 證偽 |
|---|---|
| 影子∪主 → `population_discriminates` 質量門過；抽樣 band 與「僅標題」一致 | 只為過 θ 灌列；或影子洩進 retrieve／AUTO-LIFT |
| 顧問 cite 抽測仍只打有文／原主表 eligible | 國碩錨題變差 |

## §4 與 A2／E／hold

- **A2**：影子列建議直接用 A2 草案公式（與主列投影同尺）。  
- **E**：合併主表前仍 stop-at-7。  
- **hold-#1**：不搶 B3。

## §5 Paste

```text
KH8-DISCRIM-A1-T2-shadow-go-plan | title-only | shadow-only | no-main-swap | E-keep | hold-#1 | plan-only
# 下一刀: KH8-DISCRIM-A1-T2-shadow-S1-go | N=5000 | no-main-swap
```

*完。[I] plan-only。*
