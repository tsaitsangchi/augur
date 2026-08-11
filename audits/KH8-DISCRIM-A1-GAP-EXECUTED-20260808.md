---
status: executed
series: local_ai_kh
kind: kh8_a1_gap_count
date: 2026-08-08
viewpoint: 2026-08-08T21:36+08:00
go: audits/KH8-DISCRIM-A1-GAP-GO-20260808.md
log: /tmp/kh8-a1-gap/run.log
paste: "KH8-DISCRIM-A1-gap-count-EXECUTED | read-only | T1≈2 | T2≈139k | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A1-1 缺口計數 · 2026-08-08

```text
KH8-DISCRIM-A1-gap-count | T1_text_no_w≈2 | T2_title_only≈139,043 | no-write
```

## 數字

| 池 | n |
|---|---:|
| `knowledge_item` | 285,444 |
| 有全文 | 146,401 |
| `knowhow_evidence_weight` | 146,808 |
| **T1 有文未入 weight** | **2**（皆 `smoke_test`／kh4 eligible） |
| **T2 僅標題未入 weight** | **139,043** |
| weight 覆蓋／有文 | ≈**100%**（齊備池已滿） |

T2 域頭：quant_finance 15.5k · medicine 12.3k · social_sciences 12.3k · …（學術標題海）

## 判讀

1. **A1「有文薄項」幾乎無缺口**——選擇效應不在「漏算有文」，而在「只對齊備池計分」。  
2. **槓杆在 T2 標題件**：若诚实以 absent／low 納入母體，band／terminal 非眾數質量可大幅上升（紙上估可過 0.05）——**但**須防答池／排序被標題海污染（計畫證偽條件）。  
3. 與 **A2** 仍互補：T2 解分量扁平；A2 解齊備牆。  
4. **E／hold-#1** 不變；未寫庫。

## 下一刀候選

```text
KH8-DISCRIM-A1-T2-shadow-go | title-only≤N | shadow-table | no-main-swap | no-fake-depth8
```

*完。*
