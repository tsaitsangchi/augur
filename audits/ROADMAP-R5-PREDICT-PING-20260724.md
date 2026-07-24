# Roadmap R5 — predict ping 閉合 [I]（2026-07-24）

* Steward 明示授權：`setup_predict_role --apply`（對齊 `.env` `DB_PREDICT_PASSWORD` 與 DB role）
* 前置：`audits/ROADMAP-R5-S12-CLOSED-20260724.md`（S1＋S2；G-ISO-2 曾 **partial**＝live 密碼漂移）
* **零** FinMind／FRED；本檔**不**含任何密碼／secret

## 做了什麼

| 步 | 結果 |
|---|---|
| `setup_predict_role.py --apply --confirm` | **exit 0**；role 已存在 → refresh GRANT（REVOKE 79／GRANT 160）；腳本預設**不**改既有 role 密碼 |
| Superuser `ALTER ROLE augur_predict`（`DB_SUPERUSER_*`） | **OK**——對齊 env `DB_PREDICT_PASSWORD`（授權範圍內；值不入檔） |
| `db.ping_predict()` | **True**／**PASS** |
| `pytest tests/test_predict_role_isolation.py` | **5 passed**（含 `test_connect_predict_session_user`） |

## Gap

| ID | 前 | 後 | 說明 |
|---|---|---|---|
| **G-ISO-2** | partial | **none** | runtime 接線＋GRANT＋**live** `connect_predict`／`ping_predict` 親驗綠 |

## 殘留

* **S3**／**U5**／全量 R5 DONE 仍 pending（另授權）
* FinMind／FRED 操作凍結仍有效；Dividend API 線 PAUSED
