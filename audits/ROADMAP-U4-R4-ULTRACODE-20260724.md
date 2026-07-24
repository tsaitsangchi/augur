# U4 Ultracode — R4 假綠／ban／attestation 對抗審查 [I]（2026-07-24）

* **輸入**：R4 執行報告／閉合、`reports/augur_roadmap_r3_gap_ledger_20260724.md`（G-CAT-1／G-DIV-1／G-ATTEST）、路線圖 U4 插入點
* **方法**：ULTRACODE-SCHEDULE 鐵律（幽靈落點／不實宣稱／親驗證據）；Find→Verify→Critic→Synthesize
* **硬邊界（Steward「開 U4（零 API）」）**：禁 FinMind／FRED／外部 HTTP；禁 `daily_maintenance` 放量；禁觸發 sync。允許 repo／audits／reports／script 原文、免 DB／免網 pytest、`db.ping`＋唯讀 SQL（本輪可連）。
* **對照**：U3＝`audits/ROADMAP-U3-GAP-LEDGER-ULTRACODE-20260724.md`

---

## 一、誠實界限

1. **零 API**：未跑 `build_catalog`（非 db-only）、未跑 Dividend sync、未跑 `daily_maintenance --audit-only/--heal`。  
2. **唯讀親驗**：本輪 `db.ping()=True`；對 `dataset_catalog`／`TaiwanStockPrice`／Dividend*／`attestation_result`／`arena_admission_gate` 做 SELECT。  
3. **未改** [N]、未假關 calendar、**未大改** `reports/augur_dividend_rebuild_20260724.md`（他代理 IN PROGRESS；僅引用狀態）。  
4. `schema --selftest`／`finmind --selftest` 綠＝**結構／常數**哨兵，**≠** live 對帳 PASS、≠ IP 健康。

---

## 二、Find × Verify（專打）

| Finding | 目標 | 嚴重度 | 三鏡摘要 | 判定 |
|---|---|---|---|---|
| **F-U4-1** | G-CAT-1／R4「db_only 綠」 | **medium（假綠風險）** | **文本**：R4 驗收 A=`PASS`（exit 0）與 A3=`FAIL（已知債）`並陳；閉合句亦寫 partial。**形式**：`catalog.build(db_only=True)` docstring／`:331-351` **故意不動** `dataset_catalog` 表級（`n_stocks`／`source_provenance`）。**實務規避**：只讀「exit 0／欄 mismatch 0」可把表級 STALE 讀成「catalog 完備」。 | **成立（風險）**；R4／帳本 **未**把表級寫成清零。`gap_class` **維持 partial**。U4 親驗：`TaiwanStockPrice` catalog `n_stocks=3102`／`probe`／`last_verified≈2026-06-16` vs DB `COUNT(DISTINCT stock_id)=55121`；非 excluded landed／landed_probe≈**83／81**（R4 寫 86／82；Dividend 表離線致 landed 下修，屬現況漂移非 R4 造假）。 |
| **F-U4-2** | G-DIV-1 證據 | **major（帳本幽靈）** | **文本**：帳本仍寫「親驗 PK=`(stock_id)`；2411 列＝live」。**形式**：他代理工單已 `RENAME`→`TaiwanStockDividend_collapsed_bak_20260724`；live `"TaiwanStockDividend"` **不存在**。**實務**：把 R4 當日診斷當永真＝幽靈落地。 | **成立** → 帳本 evidence **須更新**；`gap_class` **仍 partial**（資料未修／重建未完成；勿改 none）。bak 親驗：2411／2411、PK=`(stock_id)`；`DividendResult` 仍 30973／2369。索引名 `TaiwanStockDividend_pk` 現掛在 bak（rename 殘名，非「無表索引」）。 |
| **F-U4-3** | G-ATTEST／開賽宣稱 | **medium** | **文本**：R4 C3=`PASS（史料）`、C2=`SKIP`；HANDOFF 綠哨兵句＝「attestation：✅ PASS」＋ E1 freshness「最近 PASS ≤2 日」→ id=4 相對 07-24 **已陳舊**。**形式**：`attestation_result` id=4 `2026-07-16` `passed=True` VM0/EX0 **仍在**（本輪 SELECT 確認）。**實務**：把史料 PASS 當「當日 e2e／今日可開賽證明」＝假綠；arena **已**開賽之 G1 段證據用 id=4 屬 **G1-PIN 凍結段**，≠ live attestation freshness。 | **成立（誤讀路徑）**；R4／帳本已標 partial／SKIP，**非**帳本謊稱當日 e2e。`gap_class` **維持 partial**。 |
| **F-U4-4** | G1-PIN 被滾動敘事 | **low／維持** | **文本**：HANDOFF 同頁有 G1-PIN「釘 06-30」與 #7「滾動安全邊緣＝today−lag」（attestation 窗）。**形式**：`PIN_ASOF="2026-06-30"`（`preregister_arena_admission_gate.py:34`）；live gate `arena_adm_5305655ad1cd` `evaluated_pass` 之 `criteria.g1_pin.asof=2026-06-30`。**實務**：把 attestation lag 滾動誤讀成「G1 地基 as-of 可滾」→ 敘事風險；**本輪未見 PIN 被改碼／改庫**。 | **不成立為 PIN 滾動**；記敘事衛生。R4 項 D 親驗方向正確。 |
| **F-U4-5** | IP ban「停手」 | **medium（落點不全）** | **文本**：CLAUDE #24／重建報告「見 403／ban → 停、不重試風暴」。**形式**：`finmind._protected_get` 對 403＝`QUOTA_COOLDOWN`（1800s）×`max_retries`（預設 4）後 `raise FinMindError`——防的是**短退避風暴**，不是 job 級立刻 abort。`full_market_sync` catch `FinMindError` 後 **記 issue 並續下一 dataset**（`:190-192`）；per-stock 失敗進 `failed_ids` 仍掃完 roster。**實務**：操作員「見訊號即停」多半在報告／人停；code **無**「首個 IP-ban 403 → 全管線 exit」機械閘。 | **成立**：停手條件 **部分**落 code（長冷卻＋額度閘），**完整「停手」仍偏 [I]／操作**。不改 [N]；建議另案（非本輪放量）。 |

---

## 三、Critic（還沒查什麼）

* Dividend 重建 runner／log 進度與 after 指標（他代理 SSOT；U4 不搶寫）。  
* 窄窗 `daily_maintenance --datasets TaiwanStockDividend` 實跑結果（零 API 禁）。  
* 全量 `build_catalog` 後表級 provenance 是否真變 `DB`（需 API）。  
* IP ban vs 額度 403 之回應 body 是否可程式區分（現碼同一路徑）。  
* `audit_selfheal`／watchdog 對「最後 attestation 行」與 E1 freshness 的機械耦合是否在本機 timer 活著（未查 systemd）。

---

## 四、Synthesize（呈核）

### 總評

R4 **階段 DONE**（親驗＋工單）**≠** catalog 表級／Dividend 全史／當日 attestation e2e 清零——R4 原文與閉合檔整體誠實。U4 打出：**(1) G-DIV-1 帳本證據已幽靈**（live 表離線、bak 承載 R4 數字）；**(2) db_only 綠／史料 attestation 的誤讀假綠路徑**；（3）**IP ban 停手未完整機械化**。無新治權 [N] defect；屬帳本 [I] 時效＋操作落點。

### 處置（本輪）

1. 寫本對抗報告。  
2. Gap 帳本最小 diff：G-DIV-1／G-CAT-1／G-ATTEST evidence 補 U4 親驗（**不改** gap_class：皆仍 **partial**）。  
3. 路線圖標 **U4 DONE**。  
4. `archive_push.sh --slug roadmap-u4`。

### Steward 拍板句（可選）

> 接受 U4；採納帳本幽靈補正；Dividend／窄窗 audit 續由重建代理收口；IP ban job-abort 另案；不開新 RULING。

### 建議下一句

* 等 Dividend 重建代理回填 after＋窄窗 audit → 再裁 G-DIV-1  
* 或 **開 R5 執行**（計畫已出）／**開 U5**（確立級／Goodhart）  
* 單點（另授權）：全量 `build_catalog`；正典 attestation 刷新 freshness  
