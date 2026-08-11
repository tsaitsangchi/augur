---
status: go
series: local_ai_kh
kind: pdf_bounded_ingest
date: 2026-08-11
viewpoint: 2026-08-11T08:53+08:00
gap: audits/PDF-DIFF-GAP-INVENTORY-20260811.md
paste: "PDF-BOUNDED-1-go | p_cron..pdf | owned_local | dry→apply | ≠full-acquire | hold-#1"
self_reported: true
layer: "[I]"
---

# GO｜有界补入 1 档 PDF（差异唯一缺口）

```text
PDF-BOUNDED-1-go | basename=tiptop gp 5.0背景作業進階功能設定 p_cron..pdf | ≠full-acquire
```

## 准

1.  staging 单档目录 → `acquire_local_files --dry-run`  
2. 通过则 `--license owned_local`（ERP 自有私有轨）＋ domain 适切（`local` 或 `erp_tiptop` 按既有 uploads）  
3. 必要时 `--ocr`（弱字层）  
4. 写 EXECUTED（item_id／ok|dup|skip）

## 禁

全量扫 `~/.augur_uploads` · 改市场 hold · 抬 KH8 depth

*go → EXECUTED。*
