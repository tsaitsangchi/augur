---
status: inventory
series: local_ai_kh
kind: pdf_diff_gap
date: 2026-08-11
viewpoint: 2026-08-11T08:52+08:00
probe: /tmp/kh-pdf-diff-20260811.json
log: /tmp/kh-pdf-diff-20260811.log
board: audits/KH-LOOP-BOARD-REFRESH-20260811.md
paste: "PDF-DIFF-gap | disk∖DB | gap=1 | no-mass-ingest | hold-#1"
self_reported: true
layer: "[I]"
---

# INVENTORY｜PDF 差異（disk∖庫）· 2026-08-11

| 尺 | 值 |
|---|---|
| 磁碟 PDF 檔 | **306** |
| 獨一份 basename | **105** |
| 庫內 PDF basename | **113** |
| 交集 | **104** |
| **缺口（在碟無庫）** | **1** |
| 庫有碟無（樣本） | 9（多為路徑／命名變體或非 uploads 來源） |

## 唯一缺口

| basename | copies | 例路徑 |
|---|---:|---|
| `tiptop gp 5.0背景作業進階功能設定 p_cron..pdf` | 3 | `~/.augur_uploads/{af9…,0b6…,fb63…}/…/TIPTOP GP 5.0背景作業進階功能設定 p_cron..pdf` |

注：檔名含 **雙點 `..pdf`**，易與正規 `.pdf` 題名失配；可能庫內已有近似題（另核 `p_cron`）。

## 裁決含義

- **不必全量 re-ingest**（歷史 job 累計 skip／dup 高）。  
- 補豐＝**有界 1 檔（或 1 題）ingest GO**，非「讀入所有」。

```text
PDF-DIFF-gap | gap=1 | bounded-ingest-candidate | ≠full-acquire
```

*完。*
