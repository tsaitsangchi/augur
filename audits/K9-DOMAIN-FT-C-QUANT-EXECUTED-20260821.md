---
status: executed
series: local_ai_kh
track: K9
squad: C
date: 2026-08-21
viewpoint: 2026-08-21T16:38+08:00
go: audits/K9-DOMAIN-FT-C-QUANT-GO-20260821.md
fired: audits/K9-DOMAIN-FT-C-QUANT-FIRED-20260821.md
layer: "[I]"
self_reported: true
paste: "K9-DOMAIN-FT-C-quant-executed | domain=quant_finance | limit=1000 | no-fake-green | stop-at-7-keep"
---

# EXECUTED｜K9 C 隊 quant_finance 有界 FT

`limit=?` 收成 **1000**。掃完。kip `--admit-up-to 7`。未抬 ≥8。未改 θ。

## 掃批（fetch_oa_fulltext）

| 尺 | 值 |
|---|---:|
| 掃 DOI | 1000 |
| 全文落地 | **42**（item_text +287 段） |
| 終態阻擋 | **950**（下輪不重問） |
| error（可再試） | 8 |
| skip_no_oa | 165 |
| skip_license | 331 |
| skip_pdf | 149 |
| skip_ctype | 2 |
| skip_short | 11 |

950 阻擋＝license／OA／PDF 現實，**不是綠**。

## 新 42 件 kip（run 45）

sentences 16 517 → embed 15 285（junk 1 232）→ kh4 **eligible 42** → admit **42 件 depth=7**（cap=7）。來源 `approval_status=active`，非對話 approve。

## C 隊 before → after

| 尺 | 前 | 後 |
|---|---:|---:|
| items | 15 552 | 15 552 |
| 有全文 | 49 | **91** |
| DOI 待抓 | 7 424 | **6 432** |
| kh4 eligible | 49 | **91** |
| admit_depth=7 | 49 | **91** |
| depth≥8（本槍新） | — | **0** |

殘池仍大（待抓 6.4k）。再灌須另貼 limit。不把 eligible 91 當 KH8 過。
