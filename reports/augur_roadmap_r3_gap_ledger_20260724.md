# Roadmap R3 — 規格→實作 Gap 帳本 [I]（2026-07-24）

* **性質**：[I] 對帳帳本（不創設義務；不改 [N]）
* **拍板**：Steward「**開 R3**」（R0／R1／R2 DONE；〔A〕〔U-defer〕〔S1〕）
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.4
* **種子**：construction v4 §1.4／§2.2／§11；AUD-02；R2 10-14 表；L7.16；原則 #7／P4.E5
* **Ultracode**：U3 已跑（`audits/ROADMAP-U3-…`）；**U4 已跑**（2026-07-24；`audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`）——G-CAT／G-DIV／G-ATTEST evidence 經 U4 補正如下。

## 0. 使用規則

1. `obligation_summary` 只引義務代號，**不另寫第二套法律**。  
2. `gap_class`：`none`＝親驗落地｜`partial`＝局部｜`missing`＝無落點｜`doc-only`＝僅文件｜`conflict`＝宣稱與證據衝突｜`calendar`＝日曆未結（R2）。  
3. 「已落地」列必須有 `actual_evidence`（path／DB／測試結果）；無則不得標 `none`。  
4. major／假關 → 另案，不在本表偷改 [N]。

## 1. 承重義務集合（路線圖驗收最小集）

| ID | layer / clause | obligation_summary | claimed_landing | actual_evidence | gap_class | next |
|---|---|---|---|---|---|---|
| G-ISO-1 | 原則 #1／#8；大憲章隔離命門 | 預測管線不得 import 素養／顧問／knowledge | AST 雙閘＋predict role | `tests/test_philosophy_isolation.py` **8 passed**（2026-07-24）；`src/augur/audit/import_isolation.py` | **none** | 維持 CI／換機重跑 |
| G-ISO-2 | 同左；setup_predict_role | 動態閘＝預測連線走 `augur_predict` | role／GRANT 已 provision | `scripts/setup_predict_role.py:19` 自陳「`DB_PARAMS_PREDICT` 為另一步」；`config.py` **無** `DB_PARAMS_PREDICT`；`db.connect()` 單一 `DB_PARAMS` | **partial** | R5／另案：接線 predict role 進 runtime（plan-first） |
| G-OUT-1 | 大憲章輸出契約 v1.45；方向產物 | direction 產物 fail-closed：gate≠`evaluated_pass` 拒寫 | DB trigger `trg_*dirprob*_gate_guard` | **code 落點**：`scripts/migrate_direction_product_gate_ddl.py:27-43`。**本機親驗 2026-07-24**：`./venv/bin/python scripts/migrate_direction_product_gate_ddl.py --verify` → exit 0；`evaluated_fail`／不存在門皆 trigger 拒寫；`pg_trigger` 有 `trg_dirprob_gate_guard`／`trg_ddirprob_gate_guard`。見 `audits/ROADMAP-U3-DB-VERIFY-20260724.md` | **none** | 維持；正向 `evaluated_pass` 路徑俟首個 pass 門 |
| G-OUT-2 | 同左；幅度軸 | 幅度產物**無**等價 DB fail-closed（與方向軸不對稱） | 展示層把關（設計） | construction／輸出契約明文只強制方向軸；**非**「無 gap」 | **doc-only** | 知情；勿讀成 none＝已機械滿足 |
| G-ATT-1 | P4.E5／原則 #7；AUD-02 | heal 覆寫前留 pre-image；禁靜默 LWW | `raw_supersede_log`＋snapshot gate | 表／trigger／tombstone：Steward superuser migrate **全 ✓**；pytest **15 passed**；`reconcile.heal_by_date`→`heal_by_date`；`daily_maintenance --heal`→`daily_heal` | **none** | 維持；生產首遇 value_mismatch 觀察首列 |
| G-OWN-1 | L7.16；AUD-02 owner 殘餘 | 受保護物件 owner≠app；拒絕可測 | Phase 1 owner 分離＋局部測試 | HANDOFF Phase 1；`tests/test_raw_supersede_log.py` 局部；L7.16 明示「全矩陣俟擴充」；R2 #4 deferred | **partial** | 擴全受保護物件矩陣（另案）；不假關 L7.16 |
| G-FT-1 | 憲章全文三軌；knowledge | 全文僅公版／CC／owned_local；owned_local⇒local_private | promote／fetch 閘＋CHECK | **U3 更正**：`migrate_text_understanding_ddl.py:153-157` **已含** CHECK。**本機親驗 2026-07-24**：`pg_constraint` 存在於 `knowledge_item_text`；`CHECK ((((license)::text <> 'owned_local'::text) OR ((access_scope)::text = 'local_private'::text)))`。見 `audits/ROADMAP-U3-DB-VERIFY-20260724.md` | **none** | 換機靠該 migrate 重套；維持 |
| G-ATTEST | L7／attestation | attestation／audit log 可溯 | INFRA_DDL attestation_* | **R4**：INFRA selftest ✓；id=4 `2026-07-16` PASS＝**史料**；當日 e2e **SKIP**。**U4 2026-07-24**：SELECT 確認 id=4 仍 True／VM0/EX0；**禁**把史料 PASS 讀成當日 e2e 或「今日可開賽」；arena G1 用 id=4＝G1-PIN 凍結段≠ live freshness。見 `audits/ROADMAP-U4-R4-ULTRACODE-20260724.md` F-U4-3 | **partial** | 授權窄窗／正典 audit 刷新 freshness；或明示接受史料至下輪 |

## 2. 擴充種子（高槓桿／已知債；非完整宇宙）

| ID | layer / clause | obligation_summary | claimed_landing | actual_evidence | gap_class | next |
|---|---|---|---|---|---|---|
| G-PV-1 | 隔離／COMMENT | `prediction_values` 禁回讀當特徵 | COMMENT「AST+GRANT」 | construction：無 AST／GRANT 真閘；predict role **可讀寫** | **conflict** | 另案機械閘或降級敘事 |
| G-MIG-1 | #12／換機 | migrate 無參數＝建表 | `import_database.sh` 迴圈 ✓ | **U3**：`import_database.sh:158-167` 已試 `--migrate`→`--run`→裸呼（緩解 v4 假 ✓）；裸呼 exit 0 仍可能印 ✓ | **partial** | 根除：gated 裸呼勿印 ✓；或強制 `--run` |
| G-CAT-1 | catalog／#15 | catalog 反映 DB 真值 | build 後真值 | **R4**：`db_only` exit 0＝欄級；表級 STALE。**U4 親驗 2026-07-24**：Price catalog `n_stocks=3102`／`probe` vs DB **55121**；landed／landed_probe≈**83／81**（Dividend live 表離線致較 R4 86／82 下修）。`build(db_only=True)` **不動表級**（`catalog/__init__.py:323-331`）。見 U4 F-U4-1 | **partial** | 授權全量 `build_catalog`（非 db-only）刷新表級；欄級維持 db-only 即可 |
| G-DIV-1 | raw／#15 | Dividend 全史可用 | writer 已 require date | **R4 診斷（已過時）**：live PK=`(stock_id)`／2411。**U4 2026-07-24**：live `"TaiwanStockDividend"` **不存在**；塌列在 `"TaiwanStockDividend_collapsed_bak_20260724"`（2411／PK=`stock_id`）；`DividendResult` 30973／2369。重建 **IN PROGRESS**（`reports/augur_dividend_rebuild_20260724.md`；U4 不搶寫）。writer 已 `require_keys=("date",)`。見 U4 F-U4-2 | **partial** | 等重建代理 after＋窄窗 audit；勿把 R4 live 數字當現況 |
| G-KDO-1 | KS KDO.1／4 | 聚合語義／量測門檻 | DEFER L5／實作 | RULING-039：概念閉／量測仍 DEFER；R2 #5 | **calendar**／DEFER | 10-14 或實作觸發 |
| G-020 | L6.21／L7；020 M2 | 產品表 DB trigger | honest deferred | R2 #6；INF／AR 敘事 | **calendar**／deferred | 不虛假下放 |
| G-025 | L7；025 residual | kill-switch 等分階段① | 日曆至 10-14 | R2 #1–3 族 | **calendar** | 10-14 併結 |
| G-ROLE | L7.16 擴 | owner 全棧矩陣 | AUD-02 局部 | R2 #4 | **partial** | 同 G-OWN-1 |

## 3. 覆蓋自檢（路線圖驗收）

| 承重主題 | 帳本列 | 狀態 |
|---|---|---|
| 三敵人／隔離機械閘 | G-ISO-1／2、G-PV-1 | 靜態閘綠；runtime predict 未接線 |
| 輸出契約 | G-OUT-1／2 | G-OUT-1 **none**（本機 `--verify` 2026-07-24）；幅度軸＝doc-only |
| attestation | G-ATTEST | infra＋史料 PASS（id=4）；當日 e2e SKIP（R4）；U4 確認誤讀路徑 |
| owner／app | G-OWN-1、G-ROLE | 局部綠；全矩陣 partial |
| 全文三軌 | G-FT-1 | **none**（live CHECK 本機親驗 2026-07-24） |
| P4.E5／#7 supersede | G-ATT-1 | **none**（本機硬化＋pytest；U3 維持） |

## 4. R3 驗收判定

| # | 驗收項 | 結果 |
|---|---|---|
| 1 | 帳本覆蓋承重義務集合 | ✅ |
| 2 | 「已落地」有親驗證據 | ✅（G-ISO-1、G-ATT-1、G-OUT-1、G-FT-1；U3-DB-VERIFY 2026-07-24） |
| 3 | 未偷改 [N]／未假關 10-14 | ✅ |
| 4 | U3 | ✅ **DONE**（2026-07-24；見 `audits/ROADMAP-U3-GAP-LEDGER-ULTRACODE-20260724.md`） |

**R3 = DONE**（帳本交付完成 ≠ Gap 清零）。**U3 = DONE**（對抗補正已回寫帳本）。

## 5. 建議下一句

* **開 R5 執行**／**開 U5**（U4 DONE 2026-07-24；見 `audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`）  
* Dividend 重建代理收口後再裁 G-DIV-1；或授權全量 `build_catalog`／正典 attestation  
* Steward 本機補（G-OUT-1／G-FT-1）：**已做** 2026-07-24（見 `audits/ROADMAP-U3-DB-VERIFY-20260724.md`）  
* 單點修：`DB_PARAMS_PREDICT` 接線計畫／G-PV-1 機械閘；IP ban job-abort（U4 F-U4-5）另案