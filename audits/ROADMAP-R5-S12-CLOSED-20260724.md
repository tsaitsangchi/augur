# Roadmap R5 S1＋S2 閉合 [I]（2026-07-24）

* Steward「**開 R5**」＋確認零 FinMind／FRED → 授權範圍 `R5-E12`＋`PV-α`＋`PAR`
* 計畫：`reports/augur_roadmap_r5_plan_20260724.md`；拍板：`audits/ROADMAP-R5-PLAN-APPROVED-20260724.md`
* **本檔＝S1＋S2 閉合**（≠ 全量 R5 DONE；S3／U5 仍 pending；禁確立級／可交易宣稱）

## 做了什麼

| 階段 | 內容 |
|---|---|
| **S1** | `config.DB_PARAMS_PREDICT`；`db.connect(params=…)`／`connect_predict()`／`ping_predict()`；`scripts/predict_asof.py` 改 `connect_predict`；pytest 擴充 |
| **S2 PV-α** | `import_isolation.PRODUCT_LITERALS` 掃 `PREDICT_CONSUMERS`；COMMENT 對齊（禁謊稱 GRANT 雙閘）；`migrate_prediction_ddl` 已套 COMMENT |
| **未做** | S3 全哨兵敘事閉合、U5 對抗、β REVOKE SELECT、FinMind／FRED、Dividend、確立級 |

## 驗收表（A1–A10）

| ID | 結果 | 證據 |
|---|---|---|
| **A1** | **PASS** | `python -m augur.core.config --selftest` exit 0（含 `DB_PARAMS_PREDICT` 五鍵＋`user=augur_predict`） |
| **A2** | **PASS**（privilege）／**SKIP**（live login） | `tests/test_predict_role_isolation.py`：素養表 SELECT＝false（≥3）；`prediction_values` INSERT＝true。**誠實**：`connect_predict()` 現況 `password authentication failed`（`.env` `DB_PREDICT_PASSWORD` 與 role 密碼漂移）→ 未實連 session；code 接線在、密碼對齊＝ops follow-up（**未**擅自 `--apply`） |
| **A3** | **PASS** | `scripts/predict_asof.py:112` → `db.connect_predict()` |
| **A4** | **PASS** | `python -m augur.audit.import_isolation` exit 0；`PRODUCT_LITERALS`；pytest 紅測抓植入字面 |
| **A5** | **PASS** | `pytest tests/test_philosophy_isolation.py` → **9 passed** |
| **A6** | **PASS** | `migrate_direction_product_gate_ddl.py --verify` exit 0 |
| **A7** | **PASS** | 本輪 audits／閉合敘事**無**新增「確立級／可交易」宣稱（門二 `evaluated_pass` 仍 0） |
| **A8** | **PASS** | 無 FinMind／FRED 呼叫；無 Dividend DROP |
| **A9** | **SKIP** | U5 不在 `R5-E12` 範圍 → 仍 pending；**不**稱全量 R5 DONE |
| **A10** | **PASS** | Gap 帳本 G-ISO-2／G-PV-1 回寫本檔＋帳本列 |

## Gap

| ID | 前 | 後 | 說明 |
|---|---|---|---|
| **G-ISO-2** | partial | **partial** | code＋GRANT 親驗綠；live `connect_predict` 密碼失敗 → **不能** none（「能 none 才 none」） |
| **G-PV-1** | conflict | **none** | PV-α AST 字面禁＋COMMENT 誠實對齊；β 未做且未宣稱 |

## 殘留／下一步

* **S3**／**U5**：仍 pending（另授權）
* **G-ISO-2 ops**：對齊 `DB_PREDICT_PASSWORD` 或經授權 `setup_predict_role.py --apply --confirm` 後重驗 `ping_predict()`／`test_connect_predict_session_user`
* FinMind／FRED 凍結仍有效；Dividend API 線 PAUSED
* 全量 R5 DONE ≠ 本檔（須 A9 U5＋門柱條件）
