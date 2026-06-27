# 八二法則研究報告 — 冪律 × 集中度 × 市場報酬分布(2026-06-27)

> **性質**:外部文獻研究彙整(web research、2026-06-27 擷取)。**參考層、非成果**:供 augur「八二法則鏡頭」(三鏡頭之二、分布形狀)深化思想材料。
> **治權邊界(#16/#17)**:**思想可入、數字不回流**——觀念可啟發特徵設計,但**任何具體數值/切點(`0.8/0.2`、decile、「大戶=N 張」)不得移植入 code**(承憲章附錄 B + 八二設計報告紅線 #9)。本檔不改 code、不入生產。
> **augur 既有對應檔**:`reports/augur_feature_design_pareto_thought_20260612.md`(六軸 P1-P6 落地)+ `src/augur/features/concentration.py`(已實作 P1-P4 cutoff-free 泛函)。本報告補其**數學根源、生成機制、市場文獻脈絡**。

---

## 一、思想本質:八二法則不是「0.8/0.2」

八二法則(Pareto principle / 80-20 rule)的本質**不是數字 80 或 20**,而是「**少數輸入造就多數結果、分布天然不均**」之**形狀**。其四個可量化「思想不變量」(augur 八二設計報告萃取):

1. **不均勻是常態**——結果分布天然偏斜/重尾,少數單位貢獻多數結果。
2. **少數關鍵 vs 多數平庸**——資本/成交/報酬集中在少數。
3. **支配地位有慣性(馬太效應 Matthew effect)**——強者恆強;領先者 rank 有持續性。
4. **集中度本身會變**——集中⇄分散之「變化方向」是資訊(籌碼收斂=有人在收貨)。

> **方法論轉譯**:思想 → **無切點分布泛函**。不問「前 20% 是誰」(要切點、禁),改測「**分布有多不均、往哪變**」(連續值、合法)。

---

## 二、起源與數學基礎

### 2.1 起源
- **Vilfredo Pareto(1896)**:義大利經濟學家,觀察到**義大利 80% 土地由 20% 人口持有**;並見其花園 **20% 植株結 80% 果實**。
- **Joseph M. Juran(1941)**:管理顧問讀 Pareto 後,將之用於**品質管制**(「關鍵少數 vs 瑣碎多數」),命名為 Pareto principle。

### 2.2 數學:冪律 = Pareto 分布
80/20 在數學上對應**冪律分布(power-law / Pareto distribution)**:一量變化對應另一量之冪次變化。Pareto 分布由兩參數定義:
- **α(shape,形狀參數)**:決定下滑陡度。
- **x_m(scale,尺度/最小值)**。

**關鍵洞察(數字不是固定的!)**:**80/20 只是 α≈1.16 的特例**——
> 「'80-20 法則' 對應 α≈1.16 之分布」(α≈1.16 時約 20% 人口持 80% 財富)。**不同 α 給不同集中比**(可能 90/10、70/30…);**「80/20」是觀察到的一個點、非定律**。這正是 #9 紅線之數學依據:**不該把 0.8/0.2 寫死**,集中度是連續譜。

### 2.3 普遍性(同一形狀,跨域出現)
冪律出現於:財富、公司規模、城市人口、語言詞頻、網路流量、科學論文引用、書籍銷量、軟體缺陷……——**「分布形狀」是跨域不變量**。

### 2.4 Zipf 律與重尾
- **Zipf 律**:財富 × 其排名 ≈ 定值;為 **Pareto 分布之特例**。公司規模之重尾分布(Zipf 1949)是經濟學最穩固的實證事實之一(Gabaix)。
- **重尾(heavy tail)**:冪律使**機率高度集中於尾部**——極端值(極富者/極端報酬)**非指數壓抑**,出現機率遠高於常態/指數分布。
- **尾指數 < 2 → 幾乎全部質量在尾部**(財富上尾實證 α≈1.3–1.57)。對市場:**少數極端贏家主宰長期總報酬**。

---

## 三、測量工具(cutoff-free 集中度泛函)

| 泛函 | 測什麼 | augur concentration.py |
|---|---|---|
| **Gini 係數**(Lorenz 曲線面積) | 不均度(0=全均、1=極端集中) | `holding_gini`、`return_gini_60d`、`volume_gini` |
| **HHI**(Σshare²) | 集中度/支配度 | `holding_hhi`、`inst_flow_hhi_20d` |
| **Shannon entropy**(−Σp·ln p) | 分散度(集中的反面) | `holding_entropy` |
| **max-share**(max/Σ) | 最大單一貢獻者佔比 | `inst_flow_max_share`、`volume_max_share` |
| **skew / kurtosis** | 偏斜 / 重尾(動差) | `return_skew_60d`、`return_kurt_60d` |
| **rank / Δrank / rank 自相關** | 支配慣性(馬太效應) | (P6 待 phase 2) |
| **尾指數 α 估計** | 冪律陡度(學術用 MLE,Clauset 法) | — |

> 全為**連續泛函、無切點**——這是把「八二思想」紀律化入 code 的合法形式(#9)。

---

## 四、生成機制:冪律從何而來?

冪律非巧合,有可重複之生成機制:
1. **優先連結 / 富者愈富(preferential attachment / rich-get-richer)**——已領先者更易獲得新增量(馬太效應之動態形式)。市場:大型股獲更多被動資金流入 → 更大。
2. **指數之組合(combination of exponentials)**——多個指數過程疊加可生冪律。
3. **比例成長 + 下界(Gibrat + reflecting barrier)**——隨機比例成長加最小規模約束 → Zipf。

> **對 augur 的意義**:馬太效應(機制 1)= 八二設計之「支配慣性」軸——可量化為 **rank 自相關 / rank 動能**(領先地位之慣性與衰變速度),是結構性 alpha 候選。

---

## 五、在金融 / 市場的應用

### 5.1 報酬集中(最震撼之實證)
- **Bessembinder 研究**:**僅約 4% 個股創造市場幾乎全部淨財富**;「**96% 個股是死重(dead weight)**」——少數極端贏家主宰長期總報酬。
- **指數集中**:VTI(持 ~4000 股)前 10 大股佔指數 **24%**。
- **意涵**:市場報酬本身是 Pareto 分布;**選股的本質是找尾部少數贏家**——但伴隨**集中風險**,需謹慎管理。

### 5.2 財富 / 公司規模
財富比勞動所得更不均(Gini、分位不均、尾冪律皆顯示);公司規模 Zipf;billionaire 上尾實證冪律(2010-20)。

### 5.3 量價 / 籌碼集中(augur 直接應用)
- **持股集中**:少數大戶持多數股(holding HHI/Gini)→ 籌碼結構。
- **資金流集中**:流向由單一法人主導(inst_flow HHI/max-share)。
- **量能時間集中**:量集中少數日(事件/主力)vs 均勻吸納。
- **報酬集中**:動能由少數跳躍 vs 平穩漂移(return skew/kurt/Gini)——跳躍型與漂移型動能後續行為不同之假說。

---

## 六、侷限與批判

1. **80/20 非自然律**——是啟發、不是定理;**實際比例隨 α 變**,硬套「正好 80/20」是誤用(§2.2)。
2. **冪律常被過度宣稱**——學術界(Clauset/Shalizi/Newman)指出:許多「冪律」未經嚴格估計與假設檢定,**對數-對數圖近直線 ≠ 真冪律**(lognormal 等也像);須 MLE + goodness-of-fit 才能定論。
   > **augur 之防呆**:不宣稱「這是冪律」,只**連續測集中度**(Gini/HHI/熵)餵模型——避開「誤把噪音當冪律」之陷阱(對齊 #15 誠實、不過度宣稱)。
3. **集中風險**——「重押少數贏家」事後看對、事前選錯尾部即重傷;Pareto 報酬分布**也意味多數個股落後**。
4. **倖存者偏誤**——回看「少數股造就全部報酬」易高估可選性;事前辨識尾部贏家極難。
5. **切點誘惑**——「前 20%」「大戶=千張」等切點直覺,違 #9(分界應由樹/橫斷面學)。

---

## 七、對 augur 的啟示(連回八二法則鏡頭)

| 八二通則 | augur 落地 |
|---|---|
| 形狀(不均度)本身是資訊 | concentration.py:同一批 raw 欄位換「集中度/不均度」鏡頭(P1-P4 已實作) |
| 數字不固定(α 連續) | **禁 0.8/0.2/decile 入公式**;只用連續泛函(#9 紅線) |
| 馬太效應(支配慣性) | rank 自相關 / rank 動能(P6,phase 2) |
| 集中度會變(收斂方向) | `holding_hhi_chg_60d`(籌碼收/放方向) |
| 報酬重尾(少數跳躍) | `return_skew/kurt/gini_60d`(跳躍型 vs 漂移型動能) |
| 不過度宣稱冪律 | 連續測集中度、過五鏡+提拔關卡裁決,不靠「這看起來很 Pareto」(#11/#15) |

**三鏡頭分工再確認**:第一性原理(資訊內容)× **八二法則(分布形狀/多不均、誰支配)** × 康波(時間結構)——同批 raw、三族 transform、過同一漏斗。八二法則回答「**分布形狀本身是不是資訊**」。

---

## 來源(2026-06-27 web research)

- [Pareto principle — Wikipedia](https://en.wikipedia.org/wiki/Pareto_principle)
- [Pareto distribution — Wikipedia](https://en.wikipedia.org/wiki/Pareto_distribution)
- [Explaining the 80-20 Rule with the Pareto Distribution — UC Berkeley D-Lab](https://dlab.berkeley.edu/news/explaining-80-20-rule-pareto-distribution)
- [Power Laws, Pareto Distributions and Zipf's Law — M.E.J. Newman (Cornell)](https://www.cs.cornell.edu/courses/cs6241/2019sp/readings/Newman-2005-distributions.pdf)
- [Power Laws in Economics and Finance — Xavier Gabaix (NYU Stern)](https://pages.stern.nyu.edu/~xgabaix/papers/pl-ar.pdf)
- [Professor Zipf Goes to Wall Street — Malevergne et al. (NBER w15295)](https://www.nber.org/system/files/working_papers/w15295/w15295.pdf)
- [Why 96% of Stocks Are Dead Weight (Bessembinder) — The Pareto Investor](https://paretoinvestor.substack.com/p/why-96-of-stocks-are-dead-weight)
- [A statistical evidence of power law in world billionaires' data 2010–20 — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378437121004714)
- [Earnings growth and the wealth distribution — PNAS](https://www.pnas.org/doi/10.1073/pnas.2025368118)
- [Pareto Principle Definition: How to Use the 80/20 Rule — MasterClass](https://www.masterclass.com/articles/pareto-principle-explained)
