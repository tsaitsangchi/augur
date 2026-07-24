# Roadmap R6 S1＋S2 閉合 [I]（2026-07-24）

* Steward「**開 R6**」＋預選 `R6-E12`＋`HAR-local`＋`FZ-keep`
* 計畫：`reports/augur_roadmap_r6_plan_20260724.md`；拍板：`audits/ROADMAP-R6-PLAN-APPROVED-20260724.md`
* **本檔＝S1＋S2 閉合**（≠ 全量 R6 DONE／≠ 可答完備；**U6／S3a／HAR-ext pending**；禁 metadata 當可答；禁假關 G-KDO-1）

## 做了什麼

| 階段 | 內容 |
|---|---|
| **S1** | 終態詞彙鎖 `TERMINAL_VOCAB`；統一哨兵 `scripts/verify_roadmap_r6_s12.py`（A1–A5／A7／A8／A10）；G-FT-1／fulltext_status／隔離／advisor≠predict／本機 LLM 焊點親驗 |
| **S2** | `verify_knowledge_e2e_smoke --run` 暢通親驗；`refresh_knowledge_pipeline --status` 債冊（殭屍否、鎖無） |
| **最小 wiring** | 修 `acquire_local_files`：CLI 明示 `access_scope` 優先於源 cfg（原「預設 local_private」被源 `public` 靜默蓋掉→假私有實公開）；煙測明示 `--access-scope local_private` |
| **未做** | U6 對抗、S3a 外部 harvest、HAR-ext、FinMind／FRED、Dividend、改 [N]、假關 G-KDO-1 |

## 驗收表（A1–A10）

| ID | 結果 | 證據 |
|---|---|---|
| **A1** | **PASS** | `chk_itext_owned_local_private` 在 `knowledge_item_text`；admission health schema ✓ |
| **A2** | **PASS** | `knowledge_fulltext_status`＋status CHECK；`migrate_fulltext_status_ddl.py --check` ✓；終態帳非空（含 skip_no_oa／skip_license 等） |
| **A3** | **PASS** | 哨兵掃 HANDOFF／路線圖／R6 計畫／Gap／R6 audits：抽樣無半套完成／可答肯定宣稱（禁 metadata 當可答） |
| **A4** | **PASS** | `pytest tests/test_philosophy_isolation.py` → **9 passed** |
| **A5** | **PASS** | app session ≠ `augur_predict`；predict 對 knowledge／philosophy SELECT＝false（3/3） |
| **A6** | **PASS** | `verify_knowledge_e2e_smoke.py --run` exit 0（含 private 反向零外洩＋隔離斷言）；經 `verify_roadmap_r6_s12.py --with-smoke` |
| **A7** | **PASS** | `serve_advisor_openai`→ollama；`_assert_local_host` 拒公網；`python -m augur.advisor.ollama --selftest` ✓ |
| **A8** | **PASS** | 無 FinMind／FRED 放量進程；本輪未觸市場 API／未續 Dividend |
| **A9** | **SKIP** | U6 **不**自動開 → pending；**不**稱可答完備／全量 R6 DONE |
| **A10** | **PASS** | G-ISO-1／G-FT-1 維持 **none**；G-KDO-1 仍 **calendar**／DEFER（未假關） |

**近程 R6-E12 定義**＝A1–A8＋A10 PASS 且 A9 SKIP 誠實 — ✅ 本檔滿足。

> **A3 復驗（同日）**：閉合檔曾以「零「僅 metadata＝…」」點名禁句觸發哨兵假陽性；已改敘述＋哨兵 `_A3_NEG` 納入審計點名免誤抓；`verify_roadmap_r6_s12.py --with-smoke` 再親驗綠。

## Gap

| ID | 前 | 後 | 說明 |
|---|---|---|---|
| **G-ISO-1** | none | **none** | R6 再親驗 AST／pytest 9 passed；哨兵 A4 |
| **G-FT-1** | none | **none** | R6 再親驗 CHECK＋admission health；哨兵 A1 |
| **G-KDO-1** | calendar | **calendar** | **未**改；禁假關 |

## 殘留／下一步

* **U6**：另待 Steward「開 U6」（攻擊 metadata 當可答／反向污染／role 虛報）
* **S3a／HAR-ext**：外部 knowledge 窄窗另碼；**≠** FinMind／FRED 解凍
* **S3b**：owned_local dump 保命可選（HAR-local 已授權、本輪未跑）
* FinMind／FRED **FZ-keep** 仍有效；Dividend API 線 PAUSED
* 全量 R6 DONE ≠ 本檔（須 U6＋計畫門柱；≠ 全域 harvest 放量完成）

## 建議下一句

**開 U6**（可答／完成宣稱前對抗）或 **開 R7 計畫**（產品閘；各活躍產品計畫仍須獨立 plan-first）。
