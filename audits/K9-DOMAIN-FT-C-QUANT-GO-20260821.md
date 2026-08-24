---
status: go
series: local_ai_kh
track: K9
squad: C
date: 2026-08-21
viewpoint: 2026-08-21T15:39+08:00
plan: reports/augur_k9_domain_ft_go_plan_20260813.md
adopted: audits/K9-DOMAIN-FT-PLAN-ADOPTED-20260821.md
layer: "[I]"
self_reported: true
paste: "K9-DOMAIN-FT-C-quant-go | domain=quant_finance | limit=1000 | no-fake-green | stop-at-7-keep"
---

# GO｜K9 C 隊 quant_finance 有界 FT（KH3 全文終態）

Steward 貼計畫 §4 模板（含 `limit=?`）。本槍把 `?` 收成 **LIVE 有界**：

```text
limit = min(oa_pending_doi, 1000) = min(7424, 1000) = 1000
```

1000＝`run_kh_chain`／矩陣文件化範例；**不**灌 15 552／不灌 7 424。

## LIVE 前（2026-08-21 15:39）

| 尺 | 值 |
|---|---:|
| items | 15 552 |
| 已有全文 | 49 |
| DOI 待抓（PENDING_WHERE） | **7 424** |
| kh4 eligible | 49 |
| kh4 其餘 | provisional 12 414 · ineligible 2 433 · blocked 471 · no_kh4 185 |
| admit_depth | 0:15 502 · 2:1 · **7:49** |
| ft 終態 | unattempted 14 938 · skip_* 565 · none 49 |

## 做

```text
python scripts/fetch_oa_fulltext.py --domain quant_finance --limit 1000
# 若本槍有全文落地：對新 item_id
#   run_knowledge_ingress_kip.py --channel manual_cli --item-ids … \
#     --apply --skip-qdrant --admit-up-to 7
```

## 不做

- `run_kh_chain --phase all`／預設 `--up-to 9`（advance **全庫**）
- kip 預設 `--admit-up-to 9`
- harvest 新網頁源；改 KH8 θ；撤 E；抬 depth≥8
- 把 skip_license／skip_no_oa／skip_pdf 寫成綠

*go。*
