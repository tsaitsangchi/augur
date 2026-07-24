# Roadmap R3 — 規格→實作 Gap 帳本 [I]（2026-07-24）

* **性質**：[I] 對帳帳本（不創設義務；不改 [N]）
* **拍板**：Steward「**開 R3**」（R0／R1／R2 DONE；〔A〕〔U-defer〕〔S1〕）
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.4
* **種子**：construction v4 §1.4／§2.2／§11；AUD-02；R2 10-14 表；L7.16；原則 #7／P4.E5
* **Ultracode**：U3 已跑（`audits/ROADMAP-U3-…`）；**U4 已跑**（2026-07-24；`audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`）——G-CAT／G-DIV／G-ATTEST evidence 經 U4 補正如下。
* **DB-only 地基（2026-07-24）**：Steward「開資料地基（僅庫內／零 API）」→ `reports/augur_data_foundation_db_only_20260724.md`；三 Gap **仍 partial**（evidence 已刷新）。

## 0. 使用規則

1. `obligation_summary` 只引義務代號，**不另寫第二套法律**。  
2. `gap_class`：`none`＝親驗落地｜`partial`＝局部｜`missing`＝無落點｜`doc-only`＝僅文件｜`conflict`＝宣稱與證據衝突｜`calendar`＝日曆未結（R2）。  
3. 「已落地」列必須有 `actual_evidence`（path／DB／測試結果）；無則不得標 `none`。  
4. major／假關 → 另案，不在本表偷改 [N]。

## 1. 承重義務集合（路線圖驗收最小集）

| ID | layer / clause | obligation_summary | claimed_landing | actual_evidence | gap_class | next |
|---|---|---|---|---|---|---|
| G-ISO-1 | 原則 #1／#8；大憲章隔離命門 | 預測管線不得 import 素養／顧問／knowledge | AST 雙閘＋predict role | `tests/test_philosophy_isolation.py` **9 passed**（R6-S12 2026-07-24 再親驗）；`src/augur/audit/import_isolation.py`；哨兵 A4＝`scripts/verify_roadmap_r6_s12.py` | **none** | 維持 CI／換機重跑 |
| G-ISO-2 | 同左；setup_predict_role | 動態閘＝預測連線走 `augur_predict` | role／GRANT 已 provision＋runtime 接線 | **R5-S12** 接線＋GRANT；**R5-PREDICT-PING**＋**R5-S3 2026-07-24 再親驗**：`ping_predict()=True`；`connect_predict`→`augur_predict`；`pytest tests/test_predict_role_isolation.py` **5 passed**；素養表 SELECT＝false（≥5）。見 `audits/ROADMAP-R5-S3-STATUS-20260724.md`（S12 檔內「partial」＝時點史料） | **none** | 維持；換機還原後重跑 setup＋對齊密碼 |
| G-OUT-1 | 大憲章輸出契約 v1.45；方向產物 | direction 產物 fail-closed：gate≠`evaluated_pass` 拒寫 | DB trigger `trg_*dirprob*_gate_guard` | **code 落點**：`scripts/migrate_direction_product_gate_ddl.py:27-43`。**本機親驗**：U3-DB-VERIFY＋**R5-S3 再跑 `--verify` exit 0**；`evaluated_pass=0`；triggers 在。見 `audits/ROADMAP-R5-S3-STATUS-20260724.md` | **none** | 維持；正向 `evaluated_pass` 路徑俟首個 pass 門 |
| G-OUT-2 | 同左；幅度軸 | 幅度產物**無**等價 DB fail-closed（與方向軸不對稱） | 展示層把關（設計） | construction／輸出契約明文只強制方向軸；**非**「無 gap」 | **doc-only** | 知情；勿讀成 none＝已機械滿足 |
| G-ATT-1 | P4.E5／原則 #7；AUD-02 | heal 覆寫前留 pre-image；禁靜默 LWW | `raw_supersede_log`＋snapshot gate | 表／trigger／tombstone：Steward superuser migrate **全 ✓**；pytest **15 passed**；`reconcile.heal_by_date`→`heal_by_date`；`daily_maintenance --heal`→`daily_heal` | **none** | 維持；生產首遇 value_mismatch 觀察首列 |
| G-OWN-1 | L7.16；AUD-02 owner 殘餘 | 受保護物件 owner≠app；拒絕可測 | Phase 1 owner 分離＋局部測試 | HANDOFF Phase 1；`tests/test_raw_supersede_log.py` 局部；L7.16 明示「全矩陣俟擴充」；R2 #4 deferred | **partial** | 擴全受保護物件矩陣（另案）；不假關 L7.16 |
| G-FT-1 | 憲章全文三軌；knowledge | 全文僅公版／CC／owned_local；owned_local⇒local_private | promote／fetch 閘＋CHECK | **U3 更正**：`migrate_text_understanding_ddl.py:153-157` **已含** CHECK。**R6-S12 再親驗 2026-07-24**：`chk_itext_owned_local_private`＋admission health；哨兵 A1。見 `audits/ROADMAP-R6-S12-CLOSED-20260724.md` | **none** | 換機靠該 migrate 重套；維持 |
| G-ATTEST | L7／attestation | attestation／audit log 可溯 | INFRA_DDL attestation_* | **R4／U4** 同上。**DB-only 2026-07-24**：`schema --selftest` INFRA ✓；四表在；`attestation_result` 3 列；id=4 仍 True／VM0/EX0（史料）；`data_audit_log`=261163；當日 e2e／heal **SKIP**（API 凍）。見 `reports/augur_data_foundation_db_only_20260724.md` · `audits/ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md` | **partial** | 解凍＋授權窄窗／正典 audit 刷新 freshness；或明示接受史料至下輪 |

## 2. 擴充種子（高槓桿／已知債；非完整宇宙）

| ID | layer / clause | obligation_summary | claimed_landing | actual_evidence | gap_class | next |
|---|---|---|---|---|---|---|
| G-PV-1 | 隔離／COMMENT | `prediction_values` 禁回讀當特徵 | AST PV-α（PREDICT_CONSUMERS） | **R5-S12**＋**R5-S3 2026-07-24**：`PRODUCT_LITERALS`；`import_isolation` exit 0；`test_philosophy_isolation` **9 passed**；COMMENT 誠實（β 未做）。**U5 F-U5-2**：勿把 none 讀成「雙閘／β 已做」（SELECT 仍 true）。見 `audits/ROADMAP-R5-S3-STATUS-20260724.md` · `ROADMAP-U5-R5-ULTRACODE-20260724.md` | **none** | 維持 α；β REVOKE SELECT 另授權（須證明 writer 零自讀） |
| G-MIG-1 | #12／換機 | migrate 無參數＝建表 | `import_database.sh` 迴圈 ✓ | **U3**：`import_database.sh:158-167` 已試 `--migrate`→`--run`→裸呼（緩解 v4 假 ✓）；裸呼 exit 0 仍可能印 ✓ | **partial** | 根除：gated 裸呼勿印 ✓；或強制 `--run` |
| G-CAT-1 | catalog／#15 | catalog 反映 DB 真值 | build 後真值 | **R4／U4** 表級 STALE。**DB-only 2026-07-24**：`build_catalog --db-only` exit 0（84 datasets）；欄 mismatch／landed orphan **0**；表級**未動**——Price catalog `n_stocks=3102`／`probe`／`last_verified≈2026-06-16` vs DB DISTINCT **55121**；landed／landed_probe＝**84／82**／97。見 `reports/augur_data_foundation_db_only_20260724.md` | **partial** | 授權全量 `build_catalog`（非 db-only；需解凍 API）刷新表級；欄級維持 db-only 即可 |
| G-DIV-1 | raw／#15 | Dividend 全史可用 | writer 已 require date | **重建 partial＋API 凍結**；**DB-only 2026-07-24 庫內斷點複驗**：live PK=`(stock_id,date)`；列 **9721**／股 **588**／2330=**42**；bak 2411／舊 PK；Result 30973／2369；roster **800/3123 PAUSED**；窄窗 audit **SKIP**；本輪零 sync。見 `reports/augur_dividend_rebuild_20260724.md` · `augur_data_foundation_db_only_20260724.md` | **partial** | 解凍後 resume `_per_stock_sync`（勿再 DROP）；再窄窗 audit；勿把 R4 塌列數字當 live |
| G-KDO-1 | KS KDO.1／4 | 聚合語義／量測門檻 | DEFER L5／實作 | RULING-039：概念閉／量測仍 DEFER；R2 #5 | **calendar**／DEFER | 10-14 或實作觸發 |
| G-HAR-1 | CLAUDE #29b；R6 TERMINAL_VOCAB | harvest「完成／可答」須終態；禁程序結束語意冒充 | R6-E12 哨兵＋詞彙鎖 | **U6 2026-07-24**：哨兵 A3 乾淨、A9＝U6 本檔；admin `_DONE_MARKS` 字串與 `acquire_topic` 終行**漂移**＋UI「✓ 完成」≠終態；live **91933** item 無全文且無 `knowledge_fulltext_status`（DOI 形≈75373）。見 `audits/ROADMAP-U6-R6-ULTRACODE-20260724.md` F-U6-2／3 | **partial** | UI／sentinel 對齊另案；清庫存 pending＝HAR-ext／refresh 另授權（≠解凍 FinMind／FRED） |
| G-R7-1 | R7 §4.1／U7 | 產品閘哨兵＝結構／禁語抽樣；≠語義核准／空殼四判準 | `verify_roadmap_r7_gate.py` | **U7**：結構綠≠語義。**PRODSET 2026-07-24**：禁語已補「生產特徵集已登錄」「Dividend…完備」→ G-P9 可抓（selftest）；殘留＝G-P4 空殼仍可 PASS（F-U7-1）。PRODSET 真寫另見 G-PME-PRODSET=none | **doc-only** | 知情；勿讀成 none＝計畫語義已審完 |
| G-020 | L6.21／L7；020 M2 | 產品表 DB trigger | honest deferred | R2 #6；INF／AR 敘事 | **calendar**／deferred | 不虛假下放 |
| G-025 | L7；025 residual | kill-switch 等分階段① | 日曆至 10-14 | R2 #1–3 族 | **calendar** | 10-14 併結 |
| G-ROLE | L7.16 擴 | owner 全棧矩陣 | AUD-02 局部 | R2 #4 | **partial** | 同 G-OWN-1 |

## 3. 覆蓋自檢（路線圖驗收）

| 承重主題 | 帳本列 | 狀態 |
|---|---|---|
| 三敵人／隔離機械閘 | G-ISO-1／2、G-PV-1 | 靜態閘綠；G-PV-1 **none**（PV-α；U5 誤讀路徑知情）；G-ISO-2 **none**（S3 再親驗） |
| 輸出契約 | G-OUT-1／2 | G-OUT-1 **none**（S3 `--verify` 再綠）；幅度軸＝doc-only |
| attestation | G-ATTEST | infra＋史料 PASS（id=4）；當日 e2e SKIP；U4 誤讀路徑；**DB-only 2026-07-24** 再複驗仍 partial |
| owner／app | G-OWN-1、G-ROLE | 局部綠；全矩陣 partial |
| 全文三軌 | G-FT-1 | **none**（live CHECK 本機親驗 2026-07-24；U6 再確認 owned_leak=0） |
| harvest 終態誠實（庫存／UI） | G-HAR-1 | **partial**（U6：程序「完成」≠可答；91k pending 知情） |
| R7 產品閘哨兵能力邊界 | G-R7-1 | **doc-only**（U7：結構綠≠語義；幽靈詞已補禁；空殼四判準殘留） |
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

* ✅ **S3＋U5 已跑**（2026-07-24；`audits/ROADMAP-R5-S3-STATUS-20260724.md` · `ROADMAP-U5-R5-ULTRACODE-20260724.md`）——近程 R5 DONE **待 Steward 採納呈核**；禁確立級／可交易
* ✅ **R6 S1＋S2 已閉**（2026-07-24；`audits/ROADMAP-R6-S12-CLOSED-20260724.md`）
* ✅ **U6 已跑**（2026-07-24；`audits/ROADMAP-U6-R6-ULTRACODE-20260724.md`）——近程 R6-E12＋U6 可呈核；**禁**可答完備／全域 harvest；新列 **G-HAR-1 partial**；G-ISO-1／G-FT-1 維持 none；G-KDO-1 仍 calendar
* ✅ **U7 已跑**（2026-07-24；`audits/ROADMAP-U7-R7-ULTRACODE-20260724.md`）——R7 S1＋S2＋U7 可呈核；**禁** PME-Efull／八產品出貨／可交易；**G-R7-1 doc-only**（幽靈詞已補禁）
* ✅ **PME PRODSET 真寫**（2026-07-24；`audits/PME-PRODSET-CLOSED-20260724.md`）——**G-PME-PRODSET=none**；≠可交易／確立級
* Dividend：解凍＋明示後 resume G-DIV-1；或授權全量 `build_catalog`／正典 attestation
* Steward 本機補（G-OUT-1／G-FT-1）：**已做** 2026-07-24（見 `audits/ROADMAP-U3-DB-VERIFY-20260724.md`）
* 單點修：admin 完成詞／`_DONE_MARKS`（U6 F-U6-2）；IP ban job-abort（U4 F-U4-5）；β REVOKE（G-PV-1）另授權