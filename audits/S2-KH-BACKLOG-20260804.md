# S2-KH BACKLOG（L1 · live 刷新）· 2026-08-04

> **位階**：[I] C1·Arc A 產出（L1）  
> **GO**：`audits/S2-KH-OPT-AFTER-S3-GO-20260804.md`  
> **輸入**：S3-WAVE-A EXECUTED（38 feat／組 1–7 have）；prodset active=3；D-KH 地板 probe **active=15**／run≤7  
> **硬守**：KH≠raw dump；不加權 runtime；**本檔零 INSERT／零 acquire**（L2／L3 另句）  
> **self-reported（#32a）**：狀態刷新＝呈案；probe 列＝(b) DB

---

## 0. LIVE 錨（本窗）

| 錨 | 值 | 出處 |
|---|---|---|
| `feature_values` | 38 distinct；panel→2026-06-30 | S3-WAVE-A／DB |
| prodset active | `cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d` | `evolution_production_feature_set` |
| core 最新 | 225 @ 2026-06-30 | S1-CORE EXECUTED |
| RKI probes | **15／15 active**；run_id max=7；results=38 | `knowhow_interaction_probe*` |
| knowledge_source | 3605 | DB count |

**探針族現況（誠實）**：既有 active 多為 **哲學／太陽能／AI×預測元層**（RKI-FP-*／RKI-AI-*／RKI-PARETO-SOLAR 等）——**幾乎沒有**「價量×風險／截面相對化／股級 macro／圖邊」之 **市場特徵組交互** 探針。故 S3 組 1–7 特徵 **have** ≠ S2 市場 KH 交互帳已滿。

---

## 1. 優先序（開 L2 時）

1. **P0** 組 **8** 截面相對化／產業中性（S3-B 前置概念）  
2. **P0** 組 **9** Macro／FRED PIT→截面（概念＋PIT 紀律；**不解凍**）  
3. **P1** 組 **2×7** 相位／循環 × 籌碼流（對齊 prodset 三顆）  
4. **P1** 組 **1×2** 動能 × 波動聚集  
5. **P2** 組 **12／13** 序列／圖邊（概念先；builder＝S3-D）  
6. **defer／gated** 組 14–16；LOB N/A

---

## 2. 十六組刷新表

| # | feature_group | S3 LIVE | interaction_concept（應有） | corr_hypothesis（一句） | kh_status | probe 對齊 | action（L2+） | spurious |
|---|---|---|---|---|---|---|---|---|
| 1 | Price／mom | **have** | 動能／均值回歸 vs 隨機遊走 | 多窗 momentum 交互後報酬非獨立 | have_feat／**gap_probe** | 無專支市場動能探針 | INSERT `RKI-MOM-RISK` 類（動能×波動） | med |
| 2 | Vol／cycle | **have**（含 cycle_position） | 波動聚集、循環相位 | 相位×後續報酬可分 regime | have_feat／**gap_probe** | prodset 有 cycle；無 RKI 相位×報酬 | INSERT 相位×報酬；連三鏡頭史料 | med |
| 3 | Liquidity／八二 | **have**（gini 多 removed） | 流動性溢價、量能集中 | 集中度↑→後續報酬？假相關高 | have_feat／**gap_probe** | RKI-PARETO-SOLAR≠價量八二 | INSERT 八二×台股價量（非太陽能） | **high** |
| 4 | Path shape | have（扁） | 形狀資訊 vs 過擬合 | 技術形狀增量≤噪音 | partial | 無 | 走 RKI template；禁答案樹 | high |
| 5 | Valuation | **have** | 價值／成長跨期 | 估值分位×報酬均值回歸 | have_feat／**gap_probe** | 無 | INSERT 估值×報酬；橋組 8 | med |
| 6 | Fundamentals | **have** | 品質／毛利循環 | 毛利循環×估值 | have_feat／**gap_probe** | 無 | INSERT 循環×估值 | med |
| 7 | Flow／chip | **have**（lending_fee active） | 籌碼擁擠、融券費 | 累計流／借券費×後續 | have_feat／**gap_probe** | prodset 有 cumflow／lending；無 RKI | INSERT 籌碼×報酬；名實債誠實 | med |
| 8 | Xsec／industry | **partial**（S3-B） | 相對價值、產業中性 | 相對化＞raw 水準 | **gap_concept** | 無 | **P0** 概念卡＋probe；特徵 build 另 `S3-WAVE-B-go` | med |
| 9 | Macro PIT | **partial／missing** 股級 | 利差／風險偏好→截面 | macro 衝擊非均勻 | **gap_concept／corpus** | 無 | **P0** 概念＋PIT；**禁**當解凍藉口 | med |
| 10 | Regime／direction | partial 旁路表 | 政權／市場狀態 | 狀態切換改變截面斜率 | partial | RKI-AI-PREDICT-* 偏流程非市場狀態 | 概念橋 direction↔ranker；分尺 | med |
| 11 | Interaction／composite | partial | 交互≠因果 | 跨鏡交互須提拔閘 | partial | RKI 元層有；市場交互缺 | 擴市場軸 INSERT | high |
| 12 | Sequence／tensor | gap 契約 | 序依賴／長記憶 | 長窗依賴＞扁平 | **gap_concept** | 無 | 概念先；S3-D 另授 | med |
| 13 | Graph | **missing** 邊 | 同業連動／擴散 | 邊結構解釋殘差 | **gap_concept** | 無 | 概念先；邊產物缺→SKIP 特徵 | med |
| 14 | Alt／NLP／LLM | **gated** | 情緒／事件（時點） | — | gated | 無 | 僅明示＋提拔；KH≠embedding 特徵 | — |
| 15 | LOB L2 | **N/A** | — | — | gated／N/A | — | 不造欄、不開假 KH | — |
| 16 | RL state | missing | 約束下狀態（另尺） | — | gap_concept | — | 與 #14 經濟尺分尺 | — |

---

## 3. 建議 L2 probe 種子差（**未 INSERT**）

| 建議 probe_id | axes（概念） | 對組 | 註 |
|---|---|---|---|
| `RKI-MOM-VOL-TW` | 動能路徑 × 波動聚集 | 1×2 | 市場軸；NHC-keep |
| `RKI-CYCLE-RET-TW` | 循環／相位 × 後續報酬 | 2 | 對齊 prodset cycle |
| `RKI-CHIP-CROWD-TW` | 法人累計流／借券 × 擁擠 | 7 | 對齊 cumflow／lending |
| `RKI-XSEC-RELVAL-TW` | 截面相對價值 × 產業中性 | **8** | P0 |
| `RKI-MACRO-PIT-XSEC` | FRED PIT 概念 × 截面異質 | **9** | P0；不解凍 |
| `RKI-PARETO-TW-VOLUME` | 八二 × 台股量能集中 | 3 | 與 SOLAR 臂分域 |

既有 15 支：**保留**；不因本波 deactivate 元層探針。

---

## 4. acquire／promote 路徑（L3 預註；本窗不做）

| 缺口 | knowledge_source？ | 建議 |
|---|---|---|
| 市場交互語料（動能／估值／籌碼） | 3605 sources 在；**未**本窗逐列對帳 | L3 前：對 P0 概念做 source／query 存在性盤點 |
| Macro 概念語料 | FRED raw≠KH | 先概念卡；全文 license-gated |
| 圖／序列 | 缺 | defer 至概念＋S3-D／E |

---

## 5. 非本檔

- mass INSERT probes／glossary  
- harvest／acquire 放量  
- PME map 自動灌  
- FinMind／FRED 新抓  
- 特徵 rebuild／sim-apply  

下一貼（可選）：

```text
S2-KH-L2-go + GATE-keep + NHC-keep + API-THAW-bounded
```

✅ **L2 GO＋EXECUTED** 2026-08-04 → `audits/S2-KH-L2-GO-20260804.md`／`audits/S2-KH-L2-EXECUTED-20260804.md`（＋6 probes；active 21；dry-run `no_corpus`→催 L3）。

```text
S2-KH-L3-go + GATE-keep + NHC-keep + API-THAW-bounded
```

✅ **L3 GO＋EXECUTED** 2026-08-04 → `audits/S2-KH-L3-GO-20260804.md`／`audits/S2-KH-L3-EXECUTED-20260804.md`（promote 19；OA 全文阻擋 19；探針 spurious 仍高）。

---

*完。L1 backlog。self-reported（#32a）。*
