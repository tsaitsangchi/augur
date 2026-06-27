# 康波週期研究報告 — 長波 × 巢狀循環 × 相位思想(2026-06-27)

> **性質**:外部文獻研究彙整(web research、2026-06-27 擷取)。**參考層、非成果**:供 augur「康波鏡頭」(三鏡頭之三、時間結構)深化思想材料。
> **治權邊界(#16/#17)**:**思想可入、數字不回流**——循環「思想」(相位/巢狀/轉折前兆)可啟發特徵,但**任何固定週期值(40-60 年、42 個月、「N 年循環」)絕不得移植入 code**(承憲章附錄 B + 康波設計報告紅線 #9)。本檔不改 code、不入生產。
> **augur 既有對應檔**:`reports/augur_feature_design_cycle_thought_20260612.md`(六軸 C1-C6 落地)+ `src/augur/features/phase.py`(已實作 C2/C4 data-driven 相位)。本報告補其**理論根源、巢狀週期分類、學界批判脈絡**。
> **⚠️ 特別注意**:康波是三鏡頭中**學界爭議最大、實證最弱**者——故 augur 之「思想可入、數字不回流」紀律在此**最關鍵**(詳見第六節)。

---

## 一、思想本質:康波鏡頭不是「40-60 年」

康波(Kondratiev wave / long wave)原指 **45-60 年之長期經濟循環**。但 augur 取的**不是週期長度**,而是循環之五個「思想不變量」(康波設計報告萃取):

1. **循環是常態**——景氣/資金/盈餘/情緒以擴張⇄收縮往復,且**多尺度嵌套**(庫存/資本支出/信用/情緒循環同時進行、互相疊加)。
2. **位置決定行為**——同一資訊在循環不同相位意義不同;**相位(phase)比水位(level)重要**。
3. **領先-同時-落後結構**——指標對循環有時序角色;領先者轉向=轉折前兆。
4. **轉折有前兆**——減速先於下降(二階導)、背離先於反轉(領先 vs 同時分歧)。
5. **多尺度共振**——週/月/季/年同向則行情放大,互斥則震盪。

> **方法論轉譯**:不假設「循環多長」(禁),改測「**現在在自身循環的哪裡、往哪走、各尺度是否同向**」——相位/歷時/共振/背離全由**資料自身極值**定義,零固定週期。

---

## 二、起源與理論

### 2.1 系譜
- **Nikolai Kondratiev(蘇聯經濟學家,1920s)**:研究經濟成長與衰退,提出 **45-60 年長波**;以 1920s 資料辨識三波:**1790-1849(轉折 1815)、1850-1896(轉折 1873)、1896 起新波**。
- **Joseph Schumpeter(1939 正式命名)**:以**創造性破壞(creative destruction)** 與**技術創新之「成簇(bunching)」** 解釋長波——蕭條期創業家更積極投入突破式創新,成為下一上升波之基礎。
- 後續:Mandel(馬克思學派,1964 復興)、Carlota Perez / Christopher Freeman / Korotayev(現代技術-經濟典範研究)。

### 2.2 四相位 + 「四季」隱喻
- **四相位**:繁榮(prosperity/expansion)→ 衰退(recession/stagnation)→ 蕭條(depression/crisis)→ 復甦(recovery/renewal)。
- **四季隱喻(通俗化)**:春(復甦)、夏(繁榮頂)、秋(高原/投機泡沫)、冬(去槓桿蕭條)。*(註:四季是普及說法、非學術嚴格定義。)*

### 2.3 提出之成因(多元、無共識)
技術創新成簇 · 信用/債務循環(債務通縮)· 資本投資波 · 人口結構(嬰兒潮) · 土地投機 · 戰爭。**成因至今無學界共識**(§五)。

---

## 三、巢狀週期分類(augur 多尺度之理論根據)

經濟循環非單一,而是**多尺度嵌套**——這正是 augur「多尺度相位向量 + 共振」之理論根:

| 循環 | 週期 | 機制 | augur 對應(資料定義、非固定期) |
|---|---|---|---|
| **Kitchin** | 3-5 年 | **庫存**(存貨波動) | C3 庫存循環(存貨/營收比 Δ,phase 2) |
| **Juglar** | 8-11 年 | **固定投資 / 資本支出** | C3 資本支出循環(capex 強度相位,phase 2) |
| **Kuznets** | 15-25 年 | **基礎建設 / 建築** | (長尺度 context) |
| **Kondratiev** | 45-60 年 | **技術創新成簇** | C2 最長可觀察尺度(price_to_10yr) |

**巢狀關係(光譜分析)**:2 個 Kitchin ≈ 1 Juglar;**Kondratiev ≈ 5 個 Juglar**;Kuznets = Kondratiev 之**第三諧波**(非獨立循環)。
**Minsky 金融不穩定**:短「基本循環」(避險→投機→龐氏融資轉變)+ 長「超級循環」(法規鬆綁/制度侵蝕逐步放大金融脆弱性直至危機)——**信用循環之相位**(對映 augur 個股槓桿循環、融資餘額相位)。
**其他**:Goodwin(就業-工資分配衝突生內生循環)、Kalecki(投資決策與執行之延遲生振盪)、Kaldor(投資-儲蓄非線性 limit cycle)。

---

## 四、相位思想之操作化(augur phase.py 對應)

| 循環思想工具 | augur phase.py |
|---|---|
| **range-position**(x−rollmin)/(rollmax−rollmin) — 自身循環相位(0=谷/1=峰) | `range_position_60d/120d`(+既有 cycle_position_252d) |
| **距 rolling 峰/谷歷時** — 循環齡(資料事件定義) | `days_since_high_252d`、`days_since_low_252d` |
| **drawdown/runup 深度** — 收縮/擴張段深度 | `max_drawdown_252d` |
| **動能二階導(減速度)** — 轉折前兆 | `momentum_accel_60d` |
| **多尺度同向計分** — 共振 vs 互斥 | `momentum_resonance` |
| **vol 期限結構**(短/長窗 vol) — 風險循環相位 | `vol_term_structure` |
| **累計流相位** — 吸籌/派發 | `inst_cumflow_position_60d/120d` |
| **背離量**(價 vs 量/流之分歧) | C5 跨域背離(phase 2) |

---

## 五、批判與侷限(三鏡頭中最嚴重)

1. **學界多不接受**——「長波理論不被多數學院派經濟學家接受」;接受者**對成因與起訖年份亦無共識**。
2. **Apophenia(妄見模式)**——批評者指這是「**辨識出根本不存在的模式**」(在隨機中見規律)。
3. **實證薄弱**——西方經濟學家認為「無足夠統計證據支持任何規律性/週期性」;長波**因頻率低、資料有限**而**特別難實證驗證**。
4. **證據之證據也被批**——Mensch(1980s)提出約 50 年創新節律之證據,但**被批缺乏實證支持**;Kuznets 早已批評創新成簇說。
5. **無固定週期**——即使存在,長度/相位浮動,**硬編「54 年」「sell-in-May」必錯**。

> **這正是 augur 紀律最關鍵之處**:康波理論可能**根本不是真的**(或至少未證實)。但 augur **不賭「有一個 54 年循環」**——它只測「**這支股在自身資料定義的區間裡的哪個位置、多尺度是否同向**」。**此測量無論長波是否為真都成立**(range-position 是純資料事實)。把爭議理論之**思想**(相位/巢狀/轉折前兆)紀律化為 data-driven 泛函、過漏斗裁決——**既取其啟發,又免其妄見(apophenia)之坑**(對齊 #9 數字不回流、#15 不過度宣稱)。

---

## 六、對 augur 的啟示(連回康波鏡頭)

| 康波通則 | augur 落地 |
|---|---|
| 相位比水位重要 | range-position / 累計流相位(測「在哪」非「多少」) |
| 多尺度嵌套(Kitchin/Juglar/…) | 多尺度 range-position 向量 + `momentum_resonance`(共振) |
| 轉折有前兆(減速/背離) | `momentum_accel_60d`(二階導)、C5 背離電池(phase 2) |
| 信用循環(Minsky) | 個股槓桿循環(融資餘額相位,既有 margin_usage) |
| 無固定週期(學界批判) | **禁 40-60 年入公式**;一切相位由資料自身極值定義(#9) |
| 不過度宣稱循環(apophenia) | 不宣稱「有 X 年循環」,只測 data-driven 相位、過五鏡+提拔關卡裁決(#11/#15) |

**三鏡頭分工完成**:第一性原理(資訊內容/有什麼訊息)× 八二法則(分布形狀/多不均、誰支配)× **康波(時間結構/在循環哪裡、是否共振)**——同批 raw、三族 transform、過同一漏斗。康波回答「**時間結構/相位本身是不是資訊**」,且是三者中**最需紀律防妄見**者。

> **三份研究報告成套**:`augur_first_principles_research`(第一性)+ `augur_pareto_principle_research`(八二)+ 本檔(康波)= 三鏡頭思想根源、方法、文獻、批判之完整參考層。

---

## 來源(2026-06-27 web research)

- [Kondratiev wave — Wikipedia](https://en.wikipedia.org/wiki/Kondratiev_wave)
- [Long-Wave Economic Cycles: Kondratieff, Kuznets, Schumpeter, Kalecki, Goodwin, Kaldor, Minsky — Sociostudies](https://www.sociostudies.org/almanac/articles/long-wave_economic/)
- [Economic Cycles: Juglar, Kitchin, Kondratiev, and Kuznets Waves — Spotlight Labs](https://spotlightlabs.blogspot.com/2025/01/economic-cycles-juglar-kitchin.html)
- [A Spectral Analysis of World GDP Dynamics: Kondratieff Cycles — eScholarship (UC)](https://escholarship.org/content/qt9jv108xp/qt9jv108xp.pdf)
- [Kondratieff Waves in global invention activity (1900–2008) — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0040162511000503)
- [Kondratieff Waves: The Spectrum of Opinions (2019) — IssueLab](https://www.issuelab.org/resources/36240/36240.pdf)
- [The development of Kondratieff's theory of long waves (AI economy) — Nature HSS Communications](https://www.nature.com/articles/s41599-022-01434-8)
- [A Hard-Science Approach to Kondratieff's Economic Cycle — arXiv 2410.05285](https://arxiv.org/pdf/2410.05285)
- [Understanding and Value of the Kondratiev Cycle — EBC Financial Group](https://www.ebc.com/forex/definition-and-value-of-the-kondratiev-cycle)
