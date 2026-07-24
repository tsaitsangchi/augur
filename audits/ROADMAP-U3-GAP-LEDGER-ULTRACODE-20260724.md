# U3 Ultracode — Gap 帳本對抗審查 [I]（2026-07-24）

* **輸入**：`reports/augur_roadmap_r3_gap_ledger_20260724.md`
* **方法**：ULTRACODE-SCHEDULE 鐵律（幽靈落點／不實宣稱／親驗證據）；Find→Verify→Critic→Synthesize
* **範圍**：攻擊帳本本身，不改 [N]；major → 建議另案
* **代理環境**：`db.ping()` 於此環境仍 False → **live DB trigger 清單未親查**（誠實界限）

---

## 一、誠實界限

1. 未在本代理環境重查 `pg_trigger`／`direction_gate` 列數（與 Steward 本機 PG 命名空間分離）。  
2. 未重跑 FinMind／放量 sync。  
3. construction v4（07-13）敘事僅作線索，**不得**單獨充當「DB 已 armed」證據。

---

## 二、Find × Verify（對帳本列）

| Finding | 目標列 | 嚴重度 | 三鏡摘要 | 判定 |
|---|---|---|---|---|
| **F-U3-1** | G-FT-1 | **major（帳本錯）** | 帳本稱 `chk_itext_owned_local_private`「live 有、遷移無」。**反證**：`scripts/migrate_text_understanding_ddl.py:153-157` 已 codify（註明 2026-07-14 對抗審查補入）。幽靈＝**負向幽靈**（宣稱缺遷移，實際已有）。 | **成立** → 帳本須改 |
| **F-U3-2** | G-OUT-2 | medium | `gap_class=none（設計）` 把「幅度軸無 DB fail-closed」軟關為 none，易被讀成「無 gap」。設計不對稱≠義務已機械滿足。 | **成立** → 改 `doc-only` 或拆列 |
| **F-U3-3** | G-OUT-1 | medium | 證據只引 construction 敘事；真落點在 `migrate_direction_product_gate_ddl.py:27-43`（函式＋`trg_dirprob_gate_guard`／`trg_ddirprob_gate_guard`）。未附 path:line＋未 DB 親驗＝**近幽靈落地宣稱**。 | **成立** → 補強證據；DB 親驗仍 pending |
| **F-U3-4** | G-PV-1 | 維持 | COMMENT 自稱「AST+GRANT 雙閘」；`setup_predict_role.WRITABLE` **含** `prediction_values`；AST FORBIDDEN **不**擋讀該表。帳本 `conflict` **正確**，非幽靈。 | **維持 conflict** |
| **F-U3-5** | G-ATT-1 | 維持 none | `heal_by_date`→`snapshot_reason="heal_by_date"`（`reconcile.py:242`）；`daily_maintenance --heal`→`daily_heal`（`:122-123`）；預設 None 僅主路徑。pytest 15／harden 已綠。 | **維持 none** |
| **F-U3-6** | G-ISO-1 | 維持 none | 當日 `test_philosophy_isolation` 綠；FORBIDDEN／PIPELINE 與帳本一致。 | **維持 none** |
| **F-U3-7** | G-ISO-2 | 維持 partial | `DB_PARAMS_PREDICT` 仍不存在；setup 自陳另一步。 | **維持 partial** |
| **F-U3-8** | G-MIG-1 | low／更新 | construction「無參數假 ✓」部分過時：`import_database.sh:158-167` 已 `--migrate`→`--run`→裸呼。但裸呼 exit 0 仍可能印 ✓（gated no-op）。 | **降為 partial**（腳本已緩解、未根除） |
| **F-U3-9** | 覆蓋自檢 | low | 「承重覆蓋 ✅」＝欄位覆蓋，**≠** gap 清零；帳本 §4 已聲明。無假「缺 0 條」。 | **OK** |

---

## 三、Critic（還沒查什麼）

* Steward 本機：`psql` 列出 direction／supersede triggers 是否與 migrate 一致  
* `migrate_direction_product_gate_ddl.py --verify`（交易內負向＋ROLLBACK）  
* `prediction_values` 是否被任一 features SQL 字面選取（字面旁路，非 AST import）  
* G-ATTEST 端到端哨兵句（R4）  
* L7.16 受保護物件清單 vs 實際 owner 分離表集合差集

---

## 四、Synthesize（呈核）

### 總評
R3 帳本**整體方向正確**（未假關 10-14；G-ATT-1／G-ISO-1 可守）。U3 打出 **1 major 帳本錯（G-FT-1）**＋數項證據／分類 sharpen。**無新治權 [N] defect**；屬帳本 [I] 品質。

### 處置（本輪已／應落地）
1. 補正 Gap 帳本：G-FT-1、G-OUT-1／2、G-MIG-1（見同日帳本 diff）。  
2. G-OUT-1 DB 親驗、G-PV-1 機械閘 → 另案／R4–R5，不在 U3 偷關。  
3. 〔U-defer〕解除：U3 **已跑**。

### Steward 拍板句（可選）
> 接受 U3；採納帳本補正；G-OUT-1 本機 `--verify` 另工；不開新 RULING。
