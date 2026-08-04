---
title: S3 特徵後回頭優化 S2（KH）計畫
status: Steward-approved 2026-08-04（S2-KH-OPT-AFTER-S3-go）；L1 EXECUTED；L2／L3 另句
date: 2026-08-04
layer: "[I]"
role: 閉環 C1·Arc A — S3→S2 PME 式回饋／KH 缺口→S2 優化波 SSOT
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
closed_loop_c1: reports/augur_s1_s2_s3_closed_loop_plan_20260804.md
s3_features: reports/augur_s3_features_for_market_model_families_20260804.md
rki: reports/augur_raw_knowhow_interaction_probe_plan_20260728.md
audit: audits/S2-KH-AFTER-S3-LOOP-20260804.md
go_audit: audits/S2-KH-OPT-AFTER-S3-GO-20260804.md
l1_executed: audits/S2-KH-OPT-AFTER-S3-EXECUTED-20260804.md
l2_go: audits/S2-KH-L2-GO-20260804.md
l2_executed: audits/S2-KH-L2-EXECUTED-20260804.md
l3_go: audits/S2-KH-L3-GO-20260804.md
l3_executed: audits/S2-KH-L3-EXECUTED-20260804.md
backlog: audits/S2-KH-BACKLOG-20260804.md
c2_loop: reports/augur_s4_s5_closed_loop_plan_20260804.md
self_reported: true
---

# S3 特徵後回頭優化 S2（KH）計畫 · C1·Arc A · 2026-08-04

> **位階**：[I] 計畫書（CLAUDE #16／#20）。**不創設治權判準**；不改 [N]；不代簽。  
> **本輪**：plan-first——**零 KH mass ingest**、**零 FinMind／FRED**、**零 feature build**、**零 sim `--apply`**。  
> **角色**：閉環 **C1·Arc A**；全弧（含 Arc B 擴大 S1／Arc C 重驗）＝`reports/augur_s1_s2_s3_closed_loop_plan_20260804.md`。  
> **parent**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.6 **C1**／§1.2／§7.2c（rev `approved+c1-full`）。  
> **對偶**：**C2**＝`reports/augur_s4_s5_closed_loop_plan_20260804.md`；全鏈＝parent §0.8 **C0**。

---

## 0. Steward mandate（要旨）

```
S3特徵值產生後，重新回頭去看此專案需要哪些KH，再優化S2
```

**解讀**

| 是 | 不是 |
|---|---|
| S3 特徵庫存／提拔結果 → 重估所需 **KH（交互概念／關係）** → 開 S2 優化波 | 單向 S2→S3 做完即停 |
| PME 式：人策展候選＋閘；假說指導下一輪特徵 | 自動灌 `principle_factor_map`／prodset |
| 對齊 RKI／`knowhow_interaction_probe`／S0 **D-KH** 地板 | D-KH「可引用」＝本迴路已完成 |
| license-gated acquire→promote→（允許時）embed | 整庫 raw dump 入靈魂／knowledge＝預測特徵 |

---

## 1. Doctrine（釘死）

繼承 parent §1.2 與 `.cursor/rules/soul-vs-raw-correlation.mdc`：

1. **raw**＝觀測呈現；**KH**＝raw **交互**抽象出的概念與可證偽關係（相關／結構假說作概念載體）。  
2. **禁**整庫 raw／API 列貼進靈魂／原則精華／[N]。  
3. KH／靈魂／原則**指導假說與判準**——**不加權**預測 runtime（不作特徵權重、不作交易信號權重）。  
4. RKI 探針＝測與帳交互；**≠**答案 SSOT；**≠** G-PROM／可交易憑據。  
5. 預測熱路徑 ⊥ live API；本計畫路徑**零** FinMind／FRED 放量。

---

## 2. 觸發條件

下列**任一**成立即可開帳（仍須 `S2-KH-OPT-AFTER-S3-go` 才寫庫／ingest）：

| 觸發 | 證據例 |
|---|---|
| **T1** | `S3-FEATURES-PLAN-go` 已採納，且特徵組矩陣可引用（本檔寫作時報告已落地） |
| **T2** | 任一 `S3-WAVE-A…E` 收口 audit（have／partial／SKIP 誠實） |
| **T3** | 特徵庫存／提拔結果可核（`feature_values`／candidates／verify_* stdout；prodset 變更） |

**未觸發**：僅維持 S2 衛生（D-KH 地板）；不得宣稱「S2 已依 S3 優化」。

**本輪狀態**：T1／T2／T3 **已成立**；L1／**L2**／**L3 EXECUTED**（OpenAlex→promote 19；finance OA 全文 **0**／阻擋 **19**；六針 `no_corpus` 解除但 **spurious／ungrounded** 仍高）。**L4** 人裁 PME 另句。

---

## 3. 方法：S3 feature group → raw → KH 缺口

### 3.1 對映模板（每組一列）

| 欄 | 含義 |
|---|---|
| `feature_group` | S3 master list 組號／名（見 S3 特徵報告 §3） |
| `raw_tables` | 底層真來源表族（概念級；禁臆造欄） |
| `interaction_concept` | 應具備之交互**概念**（非 raw dump） |
| `corr_hypothesis` | 可證偽相關／結構假說一句 |
| `kh_status` | `have_probe`／`have_corpus`／`gap_concept`／`gap_corpus`／`gated` |
| `action` | INSERT probe／acquire 路徑／promote／PME 人候選／defer |
| `spurious_risk` | low／med／high（字面共現高、概念橋弱→高） |

### 3.2 種子對映（16 組｜計畫級；執行時以 live 刷新）

> **self-reported**：下列為對映草圖，供 backlog 開工；**非** live DB 普查。狀態對齊 S3 特徵報告 §3。

| # | feature_group | raw_tables（概念） | 缺／優化之 KH 概念（例） | kh_status 初判 | action 建議 |
|---|---|---|---|---|---|
| 1 | Price／return／momentum | PriceAdj／價序列 | 動能／均值回歸／路徑依賴 vs 隨機遊走 | have_corpus 偏 | probe：動能×風險；勿灌 raw 列 |
| 2 | Volatility／range／cycle | 同價量＋高低窗 | 波動聚集、循環相位（康波鏡頭＝假說） | have_probe 偏（三鏡頭史料） | 補相位×報酬交互探針 |
| 3 | Liquidity／volume／concentration | 成交／量能 | 流動性溢價、量能集中（八二） | have 偏 | 探針：集中度×後續報酬（假相關高警） |
| 4 | Technical／path shape | 價量 | 形狀特徵資訊含量 vs 過度擬合 | partial | 禁專支答案樹；走 RKI template |
| 5 | Valuation | 財務／市值／殖利率 | 價值／成長／均值回歸跨期 | have 偏 | 截面相對化概念橋（對組 8） |
| 6 | Fundamentals／quality／margin | 財報閘後 | 品質因子、毛利循環 | have 偏 | 循環×估值交互 |
| 7 | Flow／chip／short／lending | 法人／融資券／借券 | 籌碼擁擠、融券費訊號 | have 偏 | 名實／覆蓋債＝語料缺口誠實 |
| 8 | Cross-section ranks／industry | 同日截面＋產業 | 相對價值、產業中性 | **gap_concept** 偏 | **優先**：相對化概念＋probe |
| 9 | Macro／FRED PIT | `fred_series`／vintage | 利差／風險偏好→截面 | **gap_corpus／概念** | 股級 macro 特徵缺≠解凍；先概念＋PIT 紀律 |
| 10 | Market／regime／direction | 大盤／選擇權／燈號 | 政權切換、市場狀態 | partial（旁路表） | 與 ranker 契約分離之概念橋 |
| 11 | Interaction／composite | 跨鏡候選 | 交互項≠因果；提拔閘對齊 | partial | RKI／KNI 擴題 INSERT |
| 12 | Sequence／tensor windows | 多通道價量窗 | 序依賴／長記憶假說 | **gap_concept** | 先概念；builder 另屬 S3-D |
| 13 | Graph inputs | 產業／相關邊 | 關係擴散、同業連動 | **gap_concept** | 邊產物缺→概念先、圖特徵 SKIP |
| 14 | Alt／NLP／LLM-derived | 文本（license） | 情緒／事件強度（時點） | **gated** | 僅 Steward 明示＋提拔；KH≠embedding 特徵 |
| 15 | LOB L2 | （無基建） | — | **gated／N/A** | 不造欄；不開 KH 假補 |
| 16 | RL state／portfolio | 部位／成本 | 約束下決策狀態（另尺） | **gap_concept** | 與 #14 經濟尺分尺；禁可交易混稱 |

### 3.3 與 RKI／D-KH／知識管線對齊

| 既有 | 本計畫角色 |
|---|---|
| **D-KH**（S0） | 地板：probe active=15／run≤7 **可引用**；本迴路在其上開**優化波** |
| **RKI**／`knowhow_interaction_probe` | 擴題＝INSERT 零改碼；runner／ledger 既有；S3 缺口→新 probe 列 |
| **KNI**（arity≥3） | 可選：多軸假說（例：宏觀×籌碼×估值）；另令 `KNI-S2` 不因本檔默授 |
| **acquire→staging→promote→全文／embed** | license-gated 終態；harvest≠只抓 metadata 假完成 |
| **PME map** | 僅人標候選；異域灌因子另拍（`PME-XDOM-*`） |

---

## 4. 產出物

| 產出 | 說明 | 落點 |
|---|---|---|
| **KH backlog** | §3 模板填滿（可核來源）；優先序（組 8／9／12／13 先於 gated） | `reports/` 或 `audits/S2-KH-BACKLOG-<date>.md`（執行波另寫） |
| **acquire／promote 路徑** | 每缺口：`knowledge_source`／query 是否已有；無則策展 INSERT（#29b）；禁硬编码 dict | 既有 knowledge 管線 scripts |
| **probe 種子差** | 建議新增／升級之 `probe_id` 清單（template＋axes） | `knowhow_interaction_probe`（授權後） |
| **Steward GO** | 見 §6 | 本檔＋parent §7.2c |

**非產出**：自動 APPLY 因子、放量 sync、特徵 rebuild、確立級宣稱。

---

## 5. 分階（授權後）

| 階 | 內容 | 依賴 | 驗收 |
|---|---|---|---|
| **L0** | 本計畫＋parent §0.6＋audit 指針 | — | 本輪 **DONE（plan）** |
| **L1** | 填 §3.2 backlog（對 live feature／probe 刷新狀態） | `S2-KH-OPT-AFTER-S3-go` | backlog 可複現；零寫或僅診斷 JSON |
| **L2** | INSERT probes／glossary（零改碼）＋可選 runner | L1；`NHC-keep` | `--show`／ledger；V-SOUL |
| **L3** | license-gated acquire→promote→終態 | L1；來源列齊 | 終態或誠實 `fulltext_blocked` |
| **L4** | 人裁 PME 候選（可選） | L2／L3；另拍 map | 候選≠過閘；禁 cite 率當 G-PROM |

---

## 6. Paste-ready GO

採納本迴路計畫（**不**默授 mass ingest）：

```text
LOOP-S3-TO-S2-go + GATE-keep + NHC-keep + API-THAW-bounded
```

（≡／可連書）

```text
S2-KH-OPT-AFTER-S3-go + GATE-keep + NHC-keep + API-THAW-bounded
```

若僅 ack 地圖、不開工 L1：

```text
S2-KH-AFTER-S3-PLAN-ack + FZ-keep + NHC-keep
```

與 S3 連書示例：

```text
S3-FEATURES-PLAN-go + S2-KH-OPT-AFTER-S3-go + GATE-keep + NHC-keep + API-THAW-bounded
```

（第二句仍**不含** `S3-WAVE-*-go` build；ingest 細句可另加 `S2-KH-L2-go`／`S2-KH-L3-go`——本檔不預設。）

---

## 7. 風險

| 風險 | 緩解 |
|---|---|
| 把 raw 表 dump 當 KH | doctrine §1；backlog 欄強制 `interaction_concept` |
| 假相關當真兆 | `spurious_risk`＋人裁；KH7／RKI gap_flags |
| 未觸發即灌庫 | 觸發表 §2；GO 分離 |
| 與 S4 搶刀／混尺 | KH≠模型通過；S4 SKIP 仍可因特徵缺 |
| API 解凍誘惑 | `FZ-keep`／THAW-bounded；macro 缺口先概念 |
| 探針變第二答案 SSOT | RKI 非目標句不變 |

---

## 8. 交叉連結

| 檔 | 關係 |
|---|---|
| `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` | parent §0.6／§7.2c |
| `reports/augur_s1_s2_s3_closed_loop_plan_20260804.md` | **C1 全弧**；本檔＝Arc A；接 Arc B／C |
| `reports/augur_s3_features_for_market_model_families_20260804.md` | 觸發輸入：16 feature groups |
| `reports/augur_s4_market_model_families_opt_plan_20260804.md` | S4 消費特徵；本迴路不替代 S4 |
| `reports/augur_market_stock_predict_model_taxonomy_20260804.md` | 12 大類版圖 |
| `reports/augur_s4_s5_closed_loop_plan_20260804.md` | **C2**；S5 可選下鑽可觸發 C1 |
| `reports/augur_raw_knowhow_interaction_probe_plan_20260728.md` | RKI 探針／種子機制 |
| `audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md` | D-KH 地板 |
| `audits/S2-KH-AFTER-S3-LOOP-20260804.md` | 本計畫登錄（C1·Arc A） |
| `audits/SIM-S1-S2-S3-CLOSED-LOOP-20260804.md` | C1 全弧登錄 |
| `audits/SIM-S4-S5-CLOSED-LOOP-20260804.md` | C2／C0 登錄 |
| `audits/S3-FEATURES-MARKET-FAMILIES-20260804.md` | S3 特徵計畫登錄 |

---

## 9. 變更紀錄

| 日 | 內容 |
|---|---|
| 2026-08-04 | 初版：觸發／對映模板／16 組種子 backlog／L0–L4／GO；零 ingest 零 API 零 build |
| 2026-08-04 | 交叉：parent 升格本迴路＝**C1**；連書 C2／C0 指針 |
| 2026-08-04 | 標為 **C1·Arc A**；鏈全弧計畫＋`LOOP-S3-TO-S2-go` |

*完。self-reported（#32a）。*
