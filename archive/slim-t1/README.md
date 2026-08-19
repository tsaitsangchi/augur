# slim-t1 封存（2026-08-19）

Steward GO＝`audits/SLIM-T1-GO-20260819.md`。規則見 `reports/augur_repo_slim_opt_plan_r20_20260819.md` §4 T1。

本目錄＝從 `scripts/` **git mv** 進來的五支（雙零入鏈審視名單）。不是刪除。要重啟：`git mv` 回 `scripts/`。

| 檔 | 原路徑 |
|---|---|
| `build_item_text_from_payload.py` | `scripts/` |
| `check_isolation_outer_pkgs.py` | `scripts/` |
| `enrich_re3data_sources.py` | `scripts/` |
| `report_principle_candidates.py` | `scripts/` |
| `report_term_coverage.py` | `scripts/` |

隔離閘本體仍在 `src/augur/audit/import_isolation.py` ＋週一 pytest；本支只是配線探針。

JSON 去別名不在本目錄：`audits/RIDGE-THEN-PB-0818.json` 改指針，內容在 `audits/RIDGE-THEN-PB-LS-0818.json`。
