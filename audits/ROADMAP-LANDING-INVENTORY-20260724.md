# 憲章→實作路線圖落地盤點（文件）[I]（2026-07-24）

* **性質**：[I] 文件盤點／呈核（**零實作**、**零改 [N]**、**零 FinMind／FRED**、**不解凍**）
* **觸發**：Steward 明示「**路線圖落地盤點（文件）**」
* **SSOT**：`reports/augur_constitution_to_implementation_roadmap_20260724.md`（R0–R7、U*、凍結條件）
* **交叉**：HANDOFF §4.0／§4.4；PME／P2H／資料地基／predict-orthogonal 相關 audits
* **凍結護欄**：`.cursor/rules/finmind-fred-api-freeze.mdc`（全部落地＋明示解凍；**近程／局部 ≠ 解凍**）
* **正交**：`.cursor/rules/predict-vs-market-api.mdc`（**預測 ≠ 解凍**）

---

## 0. 一句結論（給 Steward）

**近程授權範圍內的 R0–R7／U3–U7／PME／P2H 機械閉合大致齊——但「憲章→實作全部落地」若讀成產品完備或可解凍，則尚未全綠。禁止以本盤點假關解凍。**

| 判定軸 | 結論 |
|---|---|
| **機械近程完備**（各階段當日授權範圍＋哨兵／audit） | **大致 YES**（見 §1；殘留標 **partial** 者不假關） |
| **產品完備**（路線圖大標：universe→econ 全綠／可答完備／產品艦隊出貨／確立級） | **NO** |
| **可解凍 FinMind／FRED** | **NO**（缺：明示解凍句＋對「全部落地」的 Steward 定義；API 洞 G-CAT／G-DIV／G-ATTEST 仍 partial；預測正交**不**滿足解凍） |

---

## 1. 總表：R／U／獨立計畫

> **狀態碼**：`DONE`＝該列**授權範圍**已閉合有 audit｜`partial`＝近程閉、大標／殘留未閉｜`pending`＝未開或未授權｜`blocked`＝卡 API 凍／日曆／決策｜`deferred`＝Steward 明示跳過

### 1.1 路線圖階段 R0–R7

| ID | 名稱 | 狀態 | 授權範圍內證據 | 誠實殘留（不假關） |
|---|---|---|---|---|
| **R0** | 認知對齊 | **DONE** | `audits/ROADMAP-R0-CLOSED-20260724.md`；〔A〕〔U-defer〕〔S1〕 | — |
| **R1** | 環境可運作 | **DONE** | `audits/ROADMAP-R1-ENV-STATUS-20260724.md`；`db.ping()`／pytest | — |
| **R2** | 治權衛生／10-14 誠實 | **DONE** | `ROADMAP-R2-1014-CHECKLIST-STATUS`＋`ROADMAP-R2-CLOSED` | 七項 checklist 仍 calendar／deferred／observation（**零結清**） |
| **R3** | Gap 帳本 | **DONE** | `reports/augur_roadmap_r3_gap_ledger_20260724.md`；`ROADMAP-R3-CLOSED` | 帳本內多列仍 partial／calendar（帳本 DONE ≠ gap 清零） |
| **R4** | 資料地基 | **DONE**（近程）／產品視角 **partial** | `ROADMAP-R4-CLOSED`；`augur_roadmap_r4_data_foundation`；db_only | **G-CAT-1／G-DIV-1／G-ATTEST = partial**；API 洞另帳 |
| **R5** | 預測半系統 | **DONE**（近程）／大標 **partial** | S12＋S3＋U5；`R5-S3-STATUS`；計畫 §7 A* | ≠ universe→model→econ 全綠；`direction_gate.evaluated_pass=0`；≠確立級／可交易 |
| **R6** | 素養／顧問 | **partial** | S1＋S2＋U6 DONE（`R6-S12-CLOSED`／`U6`） | **S3a／HAR-ext pending**；**G-HAR-1 partial**；≠可答完備／≠全域 harvest |
| **R7** | 產品閘＋ultracode | **partial** | S1＋S2＋U7 DONE；首掛 P-PME | ≠產品全量出貨；G-R7-1 doc-only；其餘產品計畫多數未過閘 |

### 1.2 Ultracode 插入點 U*

| ID | 狀態 | 證據／備註 |
|---|---|---|
| **U0** | **deferred** | Steward 〔U-defer〕；未開、不計「缺 ultracode」 |
| **U2** | **pending** | 路線圖有插入點；**未**見獨立「開 U2」閉合 audit（R2 本身 DONE＝誠實狀態表，≠ U2 對抗跑完） |
| **U3** | **DONE** | `audits/ROADMAP-U3-GAP-LEDGER-ULTRACODE-20260724.md` |
| **U4** | **DONE** | `audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`（零 API） |
| **U5** | **DONE** | `audits/ROADMAP-U5-R5-ULTRACODE-20260724.md` |
| **U6** | **DONE** | `audits/ROADMAP-U6-R6-ULTRACODE-20260724.md` |
| **U7** | **DONE** | `audits/ROADMAP-U7-R7-ULTRACODE-20260724.md` |
| **U-PME** | **DONE** | `audits/PME-ULTRACODE-20260724.md` |
| **U-P2H** | **DONE** | `audits/P2H-ULTRACODE-20260724.md` |

### 1.3 獨立計畫／裁決（與路線圖交叉）

| 計畫／裁決 | 狀態 | 證據 | 禁讀成 |
|---|---|---|---|
| **PME**（哲學↔市場） | **DONE**（機械完備） | `PME-EFULL-APPROVED`；PRODSET／S4／SOUL CLOSED；Gap ledger | ≠可交易；≠確立級；≠API 解凍；G-PROM／G-ECON 仍 partial |
| **P2H**（prodset→熱路徑） | **DONE** | `P2H-S123-CLOSED`＋`P2H-ULTRACODE`；G-PME-HOTPATH=none | n_feats=2 誠實極窄 ≠ 可交易 |
| **predict-orthogonal** | **DONE**［I］ | `PREDICT-ORTHOGONAL-API-RULING`＋追溯＋code 補正 | **預測可跑 ≠ 解凍** |
| **soul↔raw** | **DONE**［I］ | `SOUL-VS-RAW-CORRELATION`＋rule | 未改 META [N] |
| **資料地基 db_only** | **DONE**（庫內段） | `ROADMAP-DATA-FOUNDATION-DB-ONLY`；報告同日 | ≠ catalog 表級清零／Dividend 滿／當日 attest e2e |
| **Dividend 重建** | **blocked**（API） | live partial＋roster PAUSED；FZ-keep | 解凍＋明示 resume 前不得續打 API |
| **R6 S3a／HAR-ext** | **pending** | 路線圖 §3.7／§9 明示未開 | 非 FinMind 解凍前提，但是 R6 產品完備缺口 |
| **2026-10-14 checklist** | **blocked**（日曆） | R2 狀態表七項未結清 | 假關＝違 039 |

---

## 2. 解凍 FinMind／FRED：還缺什麼

### 2.1 現行前提（凍結 rule／HANDOFF §4.4）

兩者**皆須**：

1. **憲章→實作路線圖全部階段落地完成**
2. 用戶**明示**解凍（「解凍 FinMind／FRED」等）

明文排除：「計畫落地」／「近程 R5 DONE」／「局部階段完成」≠ 解凍。

### 2.2 本盤點對前提 (1) 的誠實讀法

| 讀法 | 是否成立 | 說明 |
|---|---|---|
| A. 近程授權機械閉合＝「全部落地」 | **爭議／不建議自動成立** | R0–R7 近程多標 DONE，但 R5／R6／R7 **自承**≠大標全綠；R4 殘留 API 洞 |
| B. 產品完備＝「全部落地」 | **否** | evaluated_pass=0；G-HAR partial；S3a pending；產品艦隊未出貨 |
| C. API 洞閉合後才算可解凍前置 | **仍否（缺明示）** | G-CAT／G-DIV／G-ATTEST partial——且這些**正是**解凍後要做的事，不能倒果為因自稱已落地 |

**建議 Steward 採納句（擇一寫入凍結條件或 HANDOFF，本檔不擅改 [N]／rule）**：

> 「全部落地」＝**機械近程完備 ∧ Steward 書面接受殘留 partial 另帳** ∧ **明示解凍**；  
> **或**更嚴：「全部落地」＝產品大標閉合（含方向確立／可答終態政策）——**現行證據下後者未達**。

### 2.3 解凍後仍 API 門（與預測正交）

即使日後解凍，下列**不得**因 predict-orthogonal／P2H／PME-Efull 假稱已補：

| 項 | 現況 | 門 |
|---|---|---|
| Dividend 缺股／resume | live 9721／588；roster PAUSED | **仍 API 門** |
| 全量 `build_catalog`（表級 STALE） | db_only 欄級綠、表級 STALE | **仍 API 門**（或另授權非 db-only） |
| 當日 attestation audit／heal | 史料 id=4 PASS；e2e SKIP | **仍 API 門** |
| FRED 新 series | 未開 | **仍 API 門** |
| 庫內 train／predict／as-of | 可跑 | **非**解凍條件；**正交** |

**明示**：**預測正交 ≠ 解凍**；缺股 Dividend 等 **仍 API 門**。

---

## 3. 「全部落地」判定建議（勿假關）

| 軸 | 定義 | 2026-07-24 判定 | 可寫入解凍？ |
|---|---|---|---|
| **機械完備** | 各 R 當日授權範圍＋對應 U*（U0 defer／U2 可另開）＋PME／P2H 機械閉 | **大致 YES** | **否**（凍結文已排除近程／局部） |
| **產品完備** | 路線圖大標＋確立級／可交易／可答完備／產品艦隊 | **NO** | **否** |
| **可解凍** | 機械或產品（Steward 定義）全綠 **＋** 明示解凍句 | **NO** | — |

**禁止句**：

- 「R0–R7 都 DONE 了 → 可以解凍」
- 「PME-Efull-yes／P2H DONE → 資料洞已補」
- 「可以預測 → 可以開 FinMind／FRED」

---

## 4. Steward 可勾選下一步（文件／決策；本輪不實作）

### 4.1 解凍定義（決策層——建議先勾）

- [ ] **INV-1** 書面定義「全部落地」＝機械近程接受殘留另帳 **或** 產品大標（二擇一）
- [ ] **INV-2** 若採機械近程：明示接受 G-CAT／G-DIV／G-ATTEST／G-HAR／10-14 **另帳**後，是否仍要求第二句「解凍 FinMind／FRED」
- [ ] **INV-3** 維持現行：**不解凍**直至 INV-1 定義下全綠＋明示句（**預設建議**）

### 4.2 近程優先對齊（執行層——FZ-keep）

- [ ] **INV-4** 繼續 **PME／資料地基庫內段**（HANDOFF §4.0）；API 洞暫不排
- [ ] **INV-5** 擴大 map 覆蓋計畫（可並行；**勿**與本盤點搶改 WIP）——擴大 n_feats／假說，仍 FZ-keep
- [ ] **INV-6** 可選：開 **U2**（10-14 假關對抗）——非解凍前提
- [ ] **INV-7** 可選：開 **R6 S3a／HAR-ext**（清 G-HAR 庫存）——**非** FinMind 解凍

### 4.3 解凍＋明示後才開（blocked 直到那時）

- [ ] **INV-8** Dividend resume（勿 DROP；接 PAUSED roster）
- [ ] **INV-9** 全量／表級 `build_catalog`
- [ ] **INV-10** 正典 attestation 窄窗 audit／heal

### 4.4 永不因本盤點自動勾

- [ ] ~~解凍 FinMind／FRED~~ ← **本檔不授權**
- [ ] ~~確立級／可交易~~ ← evaluated_pass=0；禁假關
- [ ] ~~10-14 七項結清~~ ← 日曆未到＋無 Evidence

---

## 5. 證據索引（最短）

| 主題 | path |
|---|---|
| 路線圖 SSOT | `reports/augur_constitution_to_implementation_roadmap_20260724.md` |
| Gap 帳本 | `reports/augur_roadmap_r3_gap_ledger_20260724.md` |
| R2 10-14 | `audits/ROADMAP-R2-1014-CHECKLIST-STATUS-20260724.md` |
| R4／db_only | `audits/ROADMAP-R4-CLOSED-20260724.md` · `ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md` |
| R5 近程 | `ROADMAP-R5-S3-STATUS` · `ROADMAP-U5-R5-ULTRACODE` |
| R6／U6 | `ROADMAP-R6-S12-CLOSED` · `ROADMAP-U6-R6-ULTRACODE` |
| R7／U7 | `ROADMAP-R7-S2-CLOSED` · `ROADMAP-U7-R7-ULTRACODE` |
| PME | `PME-EFULL-APPROVED` · `G-PME-SOUL-CLOSED` |
| P2H | `P2H-S123-CLOSED` · `P2H-ULTRACODE` |
| 預測正交 | `PREDICT-ORTHOGONAL-API-RULING-20260724.md` |
| HANDOFF 近程 | `HANDOFF.md` §4.0／§4.4 |

---

## 6. 本輪邊界

* ✅ 產出本盤點表（文件）
* ✅ 路線圖 §9／HANDOFF 一句「落地盤點已出」（同案回寫）
* ✅ `archive_push.sh --slug roadmap-landing-inventory`
* ❌ 未實作 code；未改 [N]；未解凍；未宣稱可解凍
* ⚠ 可與「擴大 map 覆蓋」並行；本檔不改其 WIP 大段

**建議下一句（Steward）**：「**維持 FZ-keep；勾 INV-1（定義全部落地）或續 INV-4／INV-5（PME／map）**」——**勿**「解凍 FinMind／FRED」除非 INV-1＋明示句齊備。

---

*盤點日：2026-07-24。狀態以當日 audits／路線圖 §9 為準；過期請重跑親驗（#15）。*
