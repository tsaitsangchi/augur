# U7 Ultracode — R7 產品閘／P-PME 掛接對抗 [I]（2026-07-24）

* Steward：「**開 U7**」；輸入＝R7 S1＋S2 閉合＋閘紀錄 P-PME＋哨兵／模板＋U-PME／E123／A7＋HANDOFF 近程優先
* **方法**：Find→Verify→Critic→Synthesize（對齊 U5／U6／U-PME 鐵律）
* **硬邊界**：不改 [N]；不解凍 FinMind／FRED；**不**重跑 E123 放量；可跑 `verify_roadmap_r7_gate` `--selftest`／`--check`；他域不做
* 證據錨：`audits/ROADMAP-R7-{S1,S2}-CLOSED` · `ROADMAP-R7-GATE-PME` · `PME-ULTRACODE` · `PME-A7-STATUS-or-CLOSED` · `reports/augur_roadmap_r7_plan_20260724.md` · `scripts/verify_roadmap_r7_gate.py`

---

## 一、Find（攻擊面）

| 攻擊 | 假說 |
|---|---|
| G-P4 形式過關 | 「閘全綠」＝四判準僅有關鍵字／勾選，無實質證據 |
| PRODSET 被掛閘掩蓋 | P-PME 閘 PASS＋APPLY×2 被讀成「生產特徵集已登錄／產品可上線」 |
| FZ／Dividend 完備謊言 | FZ-keep／Dividend PAUSED 被寫成產品資料完備 |
| 哨兵字面遊戲 | 空殼計畫可騙過 `--check`；禁語表漏「生產集已登錄／Dividend 完備」 |
| 與 U-PME 交叉假關 | U7 把 G-PME-PRODSET／DEMOTE／SOUL 或 10-14／G-KDO 偷關 |

---

## 二、Verify（親驗證據 → 裁決）

| ID | 標的 | 嚴重度 | 文本／形式／實務 | 裁決 |
|---|---|---|---|---|
| **F-U7-1** | G-P4／「閘全綠」幽靈 | **medium（結構真／語義淺）** | **文本**：S2／GATE-PME 稱 G-P1–G-P10 PASS；PME §4.2 有四勾＋證據。**形式**：本輪 `--check --plan …philosophy…` → fail=0；`--selftest`／`--check-framework`／`--inventory` 8/8 全綠。**字面探針**：僅「G-P4 四判準（空殼）」＋其餘關鍵字之迷你計畫 → **仍全 PASS**（哨兵 `_FOUR` 只驗區塊可指，不驗四列證據品質）。**實務**：P-PME 書面非空殼，但「結構綠」≠「四判準語義審過」；稱「機械閘＝產品計畫已審完」＝膨脹。 | **成立（設計邊界＋誤讀路徑）**；S1／S2 **結構閉合可維持**；禁把哨兵綠讀成 ultracode／語義核准 |
| **F-U7-2** | 掛閘掩蓋 PRODSET | **major（若誤宣稱）／文件已部分防住** | **文本**：GATE 結論「可申請執行授權」＋「機械閘全綠才 APPLY」；計畫 §S3／§4.1 仍寫 APPLY＝「登錄生產特徵集」。**形式**：U-PME **F-U-PME-7**＝`production_set_delta` 僅 log、無登錄表寫入 → **G-PME-PRODSET=partial**；GATE／S2／路線圖均標 ≠PME-Efull／≠可交易；PME 文末仍列「未生產特徵集真登錄」。**實務**：稱「R7 閘 PASS＝特徵已進生產集／閉環可出貨」＝假綠；稱「首掛結構過閘＋status→validated 有界自動」＝真。 | **誤讀路徑成立**；**不**回滾 S2；**維持 G-PME-PRODSET=partial**；與 U-PME **一致、無假關** |
| **F-U7-3** | G-P4-③ vs PRODSET 張力 | **medium** | **文本**：§4.2 ③「與現況一致」證據＝E123 APPLY×2（真七閘）。**形式**：同一計畫仍把「登錄生產特徵集」寫成 APPLY 輸出（U-PME 已證幽靈）。**實務**：③對「status 路徑」一致、對「PRODSET 宣稱」不一致——形式四勾無法暴露此債。 | **成立（四判準盲點）**；處置＝PRODSET 另案消歧／真寫；閘紀錄不升「產品完備」 |
| **F-U7-4** | FZ-keep／Dividend→產品完備 | **pass（未搶跑）** | **文本**：R7／GATE／S1／S2／路線圖一律 FZ-keep、Dividend PAUSED、G-DIV-1 partial。**形式**：本輪零 FinMind／FRED；帳本 G-DIV-1／G-KDO-1／10-14 **未**改。**實務**：無「Dividend 完備／已解凍」肯定句於 R7 閘檔。 | **不成立為缺陷**；維持 FZ-keep |
| **F-U7-5** | 哨兵／checklist 字面遊戲 | **medium（知情限制）** | **探針（本輪）**：Steward「豁免」句可過 G-P6（無 PME-AUTO-B）；「本產品 Dividend 特徵完備可上線」「生產特徵集已登錄」**不在**禁語表 → 仍 PASS。Schema 僅「談 schema 概念」→ G-P2 FAIL（有底線）。Docstring 自白：不做語義「計畫夠好」（屬 U7／人裁）。 | **成立（能力邊界）** → 新 **G-R7-1=doc-only**（結構哨兵≠語義／PRODSET／Dividend 誠實閘） |
| **F-U7-6** | 與 U-PME／A7 交叉 | **pass（對齊）** | **形式**：G-PME-PRODSET partial／DEMOTE doc-only／SOUL pending／STATUS none（A7 CLOSED≠全量 validated）— U7 **不**改 class。S2 CLOSED 仍寫「未做 U-PME」＝**時點史料**（後續 U-PME／A7 已履；以 PME-ULTRACODE／A7／帳本為準）。 | **無假關交叉債**；S2「未做 U-PME」＝凍結閉合檔漂移（同 U5 F-U5-1 族） |
| **F-U7-7** | 假關 10-14／G-KDO／確立／可答 | **pass** | 帳本 G-KDO-1／G-025／G-020 仍 calendar；G-HAR-1 partial；`evaluated_pass` 鎖仍在 G-P9／A10。本輪未改。 | **維持** |
| **F-U7-8** | 範圍膨脹（R7＝全產品出貨） | **pass（文件防住）** | S1＝框架；S2＝僅 P-PME 首掛；索引 8 產品其餘未掛閘紀錄；HANDOFF 近程＝PME＋解凍後資料。 | **現況乾淨**；禁「R7 DONE＝八產品可開工」 |

**本輪親驗指令摘要**（零 FinMind／FRED；不重跑 E123）：

* `python scripts/verify_roadmap_r7_gate.py --selftest` → 全通過
* `python scripts/verify_roadmap_r7_gate.py --check-framework` → F1–F7 PASS
* `python scripts/verify_roadmap_r7_gate.py --check --plan reports/augur_philosophy_market_evolution_loop_plan_20260724.md --json` → `ok=true` fail=0
* `python scripts/verify_roadmap_r7_gate.py --inventory` → 8/8 PASS
* 字面探針：空殼四判準／PRODSET 完備句／Dividend 完備句 → 哨兵仍 PASS（記入 F-U7-1／5）

---

## 三、Critic（還沒查什麼）

* 其餘 7 個產品計畫（P-ADV／P-SH／…）逐一 `--check` 欠項矩陣（本輪對準 P-PME；未全掃）
* 哨兵是否應加 WARN：計畫含「登錄生產特徵集」卻無 `G-PME-PRODSET`／對應表寫入證據
* GATE 模板是否強制勾「已知 partial gap 清單」（PRODSET／DIV／HAR）才可「可申請執行授權」
* advisor／對外文案是否把 `validated` 或「R7 閘 PASS」說成可交易（需 live chat；本輪未打）
* `ROADMAP-R7-PLAN-APPROVED` 效力表仍寫 S2／U7 pending（拍板檔時點漂移；未強制改寫閉合檔）
* 動態旁路／他域產品（HANDOFF 禁近程開工）— 本輪不做

---

## 四、Synthesize（呈核）

### 結論句

R7 **近程閘框架（S1＋S2＋U7）**在 A1–A10 意義上**可呈核階段 DONE**——**前提**：對外嚴格＝「產品閘**結構**機械化＋P-PME **首掛書面**過閘＋本對抗已釘誤讀邊界」，**不是**「PME-Efull／生產特徵集已登錄／八產品可出貨／可交易／API 解凍」。

哨兵綠＝**真結構綠**（非幽靈無檔）；G-P4／禁語＝**可被字面遊戲通過**（設計已知；U7 補語義停手句）。**G-PME-PRODSET** 與 U-PME **一致仍 partial**——掛閘**未**掩蓋、亦**未**治癒。

### gap_class 建議（本輪）

| ID | 建議 | 理由 |
|---|---|---|
| G-DIV-1 | **維持 partial** | FZ-keep；未續 API；未寫成完備 |
| G-KDO-1／10-14 族 | **維持 calendar** | 未假關 |
| G-HAR-1 | **維持 partial** | 非本輪域；未偷關 |
| G-PME-PRODSET | **維持 partial** | 與 U-PME F-U-PME-7 一致 |
| G-PME-DEMOTE | **維持 doc-only** | 與 U-PME 一致 |
| G-PME-SOUL | **維持 pending** | 未改 [N] |
| **G-R7-1**（新） | **doc-only** | 哨兵＝結構／禁語抽樣；語義／PRODSET／Dividend 完備宣稱不在機械域 |

### 可否「R7／P-PME 產品完備」？

| 語義 | 可否 |
|---|---|
| R7 閘框架近程（S1＋S2＋U7／A9） | **可呈核 YES**（本 U7） |
| P-PME 結構掛閘（G-P* 文件＋哨兵） | **YES**（≠ Efull） |
| 生產特徵集已登錄／預測熱路徑已吃晉升 | **NO** — F-U7-2／U-PME-7 |
| 八產品均可開工／路線圖全部落地 | **NO** |
| 確立級／可交易／解凍 API／Dividend 完備 | **NO** — FZ-keep；pass＝0 |

### 建議處置（執行層、零 [N]）

1. 本檔＝**U7 DONE**；路線圖／R7 計畫標 U7 DONE；Gap 加 **G-R7-1**；PME 帳本交叉註 U7 確認 PRODSET
2. 近程下一句優先：**PME 補生產集登錄（消歧或真寫）**——對齊 HANDOFF；**或**等解凍後 Dividend／catalog（**勿**本輪自解凍）
3. 另案（非必須本輪）：哨兵 WARN／GATE 模板強制「已知 partial」勾選；閉合檔時點漂移可註「史料」不強制改寫
4. 維持 FZ-keep；禁假關 10-14／G-KDO；禁把 R7 DONE 讀成產品出貨
5. `bash scripts/archive_push.sh --slug roadmap-u7`

### A9（R7 計畫驗收）

| ID | 結果 | 證據 |
|---|---|---|
| **A9** | **PASS** | 本檔含 Find／Verify／Critic／Synthesize；五攻擊焦點皆 Verify；Critic「未查項」已列 |
