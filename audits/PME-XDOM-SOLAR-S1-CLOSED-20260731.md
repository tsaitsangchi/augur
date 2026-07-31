# PME-XDOM-SOLAR S1 CLOSED — KH10 curate（2026-07-31）

> **拍板**：`audits/PME-XDOM-SOLAR-PLAN-APPROVED-20260731.md`  
> **腳本**：`scripts/curate_pme_xdom_solar_map.py`  
> **SEED**：`reports/augur_pme_xdom_solar_from_kh10_plan_20260731.md` §三

## 結果（`--apply` stdout）

| 項 | 值 |
|---|---|
| school | `solar_supply_invest`（既有，未新建） |
| sources_new | 2（ESL／AFML） |
| principles_new | 3（K1–K3） |
| maps_new | 7 |
| domain_notes_new | 3 |
| ledger_links | 4（candidate 2／3／9／18） |

## Selftest

`python scripts/curate_pme_xdom_solar_map.py --selftest` → 全通過。

## 明確未做

- 未解凍 API；未 APPLY prodset；未把 defer 16／19–23 入庫。
