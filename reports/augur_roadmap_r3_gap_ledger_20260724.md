# Roadmap R3 — 規格→實作 Gap 帳本 [I]（2026-07-24）

* **性質**：[I] 對帳帳本（不創設義務；不改 [N]）
* **拍板**：Steward「**開 R3**」（R0／R1／R2 DONE；〔A〕〔U-defer〕〔S1〕）
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.4
* **種子**：construction v4 §1.4／§2.2／§11；AUD-02；R2 10-14 表；L7.16；原則 #7／P4.E5
* **Ultracode**：本帳本＝U3 輸入；**本輪未跑 U3**（〔U-defer〕＝R3 後另開）

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
| G-OUT-1 | 大憲章輸出契約 v1.45；方向產物 | direction 產物 fail-closed：gate≠`evaluated_pass` 拒寫 | DB trigger `trg_*dirprob*_gate_guard` | construction v4 §1.4／§2.2 記述＋migrate 腳本家族；本輪未重查 DB trigger 清單 | **partial** | R5 親驗 `pg_trigger`；未 pass 前禁「確立級」宣稱 |
| G-OUT-2 | 同左；幅度軸 | 幅度產物無等價 DB fail-closed | 設計不對稱（展示層） | construction §2.2：`prediction_probability` 無同型 trigger | **none**（設計）／知情 | 勿宣稱與方向軸同強度 |
| G-ATT-1 | P4.E5／原則 #7；AUD-02 | heal 覆寫前留 pre-image；禁靜默 LWW | `raw_supersede_log`＋snapshot gate | 表／trigger／tombstone：Steward superuser migrate **全 ✓**；pytest **15 passed**；wiring：`generic_schema._snapshot_superseded`、`reconcile`／`sync` `snapshot_reason` | **none** | 維持；生產首遇 value_mismatch 觀察首列 |
| G-OWN-1 | L7.16；AUD-02 owner 殘餘 | 受保護物件 owner≠app；拒絕可測 | Phase 1 owner 分離＋局部測試 | HANDOFF Phase 1；`tests/test_raw_supersede_log.py` 局部；L7.16 明示「全矩陣俟擴充」；R2 #4 deferred | **partial** | 擴全受保護物件矩陣（另案）；不假關 L7.16 |
| G-FT-1 | 憲章全文三軌；knowledge | 全文僅公版／CC／owned_local；owned_local⇒local_private | promote／fetch 閘＋CHECK | construction §3.2：`chk_itext_owned_local_private` **live 有、遷移無**→clean-room 重建可能丟約束 | **conflict**／**partial** | 遷移補 DDL 入 repo（機械修正計畫）或證實 Python 護欄為唯一可攜強制並改規格敘事 |
| G-ATTEST | L7／attestation | attestation／audit log 可溯 | INFRA_DDL attestation_* | `schema.INFRA_DDL` 含相關表；本輪未做端到端 attestation 綠哨兵 | **partial** | R4 對齊哨兵句親驗 |

## 2. 擴充種子（高槓桿／已知債；非完整宇宙）

| ID | layer / clause | obligation_summary | claimed_landing | actual_evidence | gap_class | next |
|---|---|---|---|---|---|---|
| G-PV-1 | 隔離／COMMENT | `prediction_values` 禁回讀當特徵 | COMMENT「AST+GRANT」 | construction：無 AST／GRANT 真閘；predict role **可讀寫** | **conflict** | 另案機械閘或降級敘事 |
| G-MIG-1 | #12／換機 | migrate 無參數＝建表 | `import_database.sh` 迴圈 ✓ | 15 支需 `--run` 被無參數假 ✓（construction §3.2 陷阱） | **conflict** | 修腳本／文件；換機腳本分 gated |
| G-CAT-1 | catalog／#15 | catalog 反映 DB 真值 | build 後真值 | provenance 多卡 `probe`；n_stocks 低估（v4） | **partial** | R4：`build(db_only=True)` 或全量 rebuild |
| G-DIV-1 | raw／#15 | Dividend 全史可用 | writer 已 require date | PK 塌列未 DROP+re-sync（v4） | **partial** | R4 資料修復工單 |
| G-KDO-1 | KS KDO.1／4 | 聚合語義／量測門檻 | DEFER L5／實作 | RULING-039：概念閉／量測仍 DEFER；R2 #5 | **calendar**／DEFER | 10-14 或實作觸發 |
| G-020 | L6.21／L7；020 M2 | 產品表 DB trigger | honest deferred | R2 #6；INF／AR 敘事 | **calendar**／deferred | 不虛假下放 |
| G-025 | L7；025 residual | kill-switch 等分階段① | 日曆至 10-14 | R2 #1–3 族 | **calendar** | 10-14 併結 |
| G-ROLE | L7.16 擴 | owner 全棧矩陣 | AUD-02 局部 | R2 #4 | **partial** | 同 G-OWN-1 |

## 3. 覆蓋自檢（路線圖驗收）

| 承重主題 | 帳本列 | 狀態 |
|---|---|---|
| 三敵人／隔離機械閘 | G-ISO-1／2、G-PV-1 | 靜態閘綠；runtime predict 未接線 |
| 輸出契約 | G-OUT-1／2 | 方向軸有 trigger 敘事；本輪未重查 DB |
| attestation | G-ATTEST | 表在；端到端哨兵待 R4 |
| owner／app | G-OWN-1、G-ROLE | 局部綠；全矩陣 partial |
| 全文三軌 | G-FT-1 | 有落點＋遷移漂移 conflict |
| P4.E5／#7 supersede | G-ATT-1 | **none**（本機硬化＋pytest） |

## 4. R3 驗收判定

| # | 驗收項 | 結果 |
|---|---|---|
| 1 | 帳本覆蓋承重義務集合 | ✅ |
| 2 | 「已落地」有親驗證據 | ✅（G-ISO-1、G-ATT-1 當日親驗；其餘標 partial／calendar／conflict 不冒充 none） |
| 3 | 未偷改 [N]／未假關 10-14 | ✅ |
| 4 | U3 | ⏭ deferred（另指令「開 U3」） |

**R3 = DONE**（帳本交付完成 ≠ Gap 清零）。

## 5. 建議下一句

* **開 U3**：對抗本帳本幽靈落點（高槓桿）  
* **開 R4**：資料地基（catalog／Dividend／attestation 哨兵）  
* 單點修：`DB_PARAMS_PREDICT` 接線計畫／owned_local CHECK 遷移補檔
