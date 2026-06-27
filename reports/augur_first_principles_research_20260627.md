# 第一性原理研究報告 — 思想史 × 方法 × 量化投資應用(2026-06-27)

> **性質**:外部文獻研究彙整(web research、2026-06-27 擷取)。**參考層、非成果**:供 augur「第一性原理鏡頭」(三鏡頭之一)深化思想材料。
> **治權邊界(#16/#17)**:**思想可入、數字不回流**——本報告之觀念可啟發特徵設計思路,但**任何具體數值/閾值不得移植入 code**(承憲章附錄 B 紀律化)。本檔不改 code、不入生產;僅作 doctrine-adjacent 參考。
> **augur 既有對應檔**:`reports/augur_feature_design_first_principles_20260612.md`(七軸落地設計)。本報告補其**思想根源、方法論框架、量化投資文獻脈絡**。

---

## 一、思想本質:什麼是第一性原理?

**第一性原理(First Principles)** = 把問題拆解到**不可再分、無法證明亦無須證明的基本真理(irreducible truths)**,再從這些地基**往上重建**,而非從慣例、權威或類比出發。

### 1.1 兩種思考的對立(核心)
| | 第一性原理 | 類比推理(reasoning by analogy)|
|---|---|---|
| 起點 | 基本真理(raw ingredients) | 既有先例(別人怎麼做、過去怎麼做) |
| 過程 | 拆解 → 質疑假設 → 從基本重建 | 在既有版本上「微調主題」(slight iterations) |
| 產出 | 創新解、突破性方案 | 漸進改良 |
| 成本 | 費神、耗時、需深厚基礎知識 | 省力、快速 |

**主廚 vs 廚師隱喻(chef vs cook)**:主廚懂**生食材**與如何組合(從基本構件往上建);廚師照**食譜**(別人試過喜歡的版本)做。第一性原理者是主廚——重視**功能(function)勝於形式(form)**:多數人優化既有形式(做更好的袋子),第一性原理者問底層目的(更有效率的儲存與移動)。

> Musk:「我傾向用**物理框架**思考。物理教你**從第一性原理推理、而非類比**。」

---

## 二、思想史與邏輯結構

### 2.1 系譜
- **Aristotle(亞里斯多德)**:詞源與方法源頭。《後分析篇(Posterior Analytics)》定義第一性原理為「一個領域中所有其他知識所由生的基礎命題」——**你無法證明第一性原理,只能辨識何者不可再分地為真、以之為起點**。他區分**演繹(deductive,由基本規則推出結論)**與**歸納(inductive,由觀察外推出規則)**。
- **Descartes(笛卡兒,17C)**:**徹底懷疑法(radical doubt)**——剝除一切可被質疑者,直到觸及無法否認之物,再重建;得其第一性原理「**我思故我在(Cogito, ergo sum)**」。將**基礎主義(foundationalism)**引入西方知識論。
- **Bacon(培根)**:歸納法之倡——「**逐級從一公理到另一公理**」,每步徹底檢驗才前進。
- **Peirce(皮爾士)**:補上**溯因推理(abductive)**——從有限資訊產生**假說**;邏輯上最不穩固,但能推斷「最佳可能解釋」。

### 2.2 第一性原理 × 科學方法(三步閉環)
| 步驟 | 推理類型 | 作用 |
|---|---|---|
| 1. 假說生成 | **溯因(Abduction)** | 從現象產生可檢驗命題 |
| 2. 假說檢驗 | **演繹(Deduction)** | 驗證與第一性原理之邏輯一致性 |
| 3. 理論泛化 | **歸納(Induction)** | 把通過者泛化為普適框架 |

> **對 augur 的直接映射**:此三步即 augur 特徵漏斗之骨架——溯因(三鏡頭生成候選假說)→ 演繹(紀律閘 #1/#8/#9 檢驗邏輯一致)→ 歸納(五鏡 + walk-forward 泛化為「有用特徵」)。詳見第六節。

---

## 三、實踐框架(如何真的拆到第一性)

### 3.1 蘇格拉底式提問(Socratic questioning,六步)
1. **澄清思考**——解釋想法從何而來
2. **挑戰假設**——反問憑什麼如此
3. **尋找證據與來源**
4. **考慮替代觀點**
5. **檢視後果與蘊含**
6. **質疑原本的提問本身**
> 作用:阻止「靠直覺」、限制強情緒反應。

### 3.2 五個為什麼(Five Whys)
反覆問「為什麼」穿透表層解釋。**三四個「為什麼」後人常變得不安/防衛——因為「我們其實不知道為什麼」**(暴露未經檢驗的信念)。

### 3.3 Musk 三步(SpaceX 火箭/電池實例)
1. 從**目標結果**出發(更便宜的火箭)
2. 辨識**基本材料/構件**(航太級鋁合金 + 鈦 + 銅 + 碳纖維)
3. 查**原物料真實市價**(發現原料僅佔火箭典型售價 **~2%**)→ 自建重構 → 發射成本降近 **10×**
> 電池同法:「以材料為基礎拆解;若在倫敦金屬交易所買,各項各值多少?」

### 3.4 Munger 多元思維模型(mental models)
從多學科基本原理(物理、生物、經濟、心理)交叉檢驗——**避免「拿錘子的人看什麼都像釘子」**之單一視角偏誤。

---

## 四、第一性原理在量化投資 / 因子研究的應用

### 4.1 因子(alpha factor)= 從市場第一性原理導出之顯式函數
**alpha 因子**:把歷史市場特徵(價、量…)映射到未來報酬預測之**明確函數**。傳統因子研究**從市場邏輯(market logic)出發**,把**經濟規律(economic regularities)蒸餾成結構化數學形式**(如 Alpha191 內嵌之動能、反轉、波動、量價交互等可解釋推理)。

### 4.2 傳統路徑(第一性原理之古典實踐)
**經濟學家/金融工程師提理論假說 → 轉成數學公式 → 歷史資料驗證**。此類人工建構之 alpha **可解釋性與穩定性強**(因根植於經濟第一性原理,非資料挖掘巧合)。

### 4.3 核心張力(因子研究之中心難題)
**可規模化生成 ⇄ 可解釋市場邏輯 ⇄ 跨週期穩健**三者之取捨,是量化金融的中心挑戰。alpha 發現本質是「在嚴苛組合約束下,找出**既有預測力又可解釋**之符號函數」之機器學習難題。

### 4.4 現代演進(AI 時代之第一性原理)
近年研究探索**市場邏輯驅動之多代理系統**做因子挖掘——把「市場邏輯」當作**顯式且可迭代改進之對象**(如 AlphaLogics、Alpha-GPT、grammar-guided / 演化式 alpha mining)。精神仍是第一性原理:不盲挖資料,而是**從可解釋的市場機制出發**生成候選、再嚴格驗證。

### 4.5 量化價值投資之第一性原理(行為 + 結構)
系統化/量化勝過裁量式之第一性論據:**人有系統性行為偏誤**(過度反應、錨定、處置效應…)→ 紀律化流程能**移除情緒、貫徹過程一致性**;**重過程勝於重結果**(單次結果含運氣,長期靠正確過程)。

---

## 五、侷限與批判(何時**不該**用第一性原理)

1. **耗時費神**——需大量心力,且**需深厚基礎知識**才能正確辨識「什麼才是第一性」。
2. **過度分析風險(overanalysis)**——拆解本身可能變成拖延。
3. **非總是實用**——對**已被充分研究/理解之問題**,靠既有知識與類比往往更有效率;**危機/需即時行動時**,深度分析不切實際,成熟方案更佳。
4. **辨識第一性本身困難**——複雜/高度技術領域尤難,易把「自以為的基本」當成真基本(自我欺騙)。
5. **文化阻力**——逆慣例而行需勇氣;從眾是人性。

> **對 augur 的警示**:第一性原理**不是萬靈丹**。augur 的紀律是「**思想負責生成、市場負責裁決**」——第一性原理只在「生成候選假說」階段主導;是否有用,**由 out-of-sample 驗證(漏斗)決定**,不由「我覺得這個第一性很對」決定(防三敵之「自我欺騙」)。

---

## 六、對 augur 的啟示(連回第一性原理鏡頭)

| 第一性原理通則 | augur 既有落地 |
|---|---|
| 拆到不可再分之基本真理 | 七資訊軸(水位/動能/缺口/品質/籌碼…)= 把「股票會漲」拆成可量測之**資訊內容**基本面 |
| 功能勝於形式 | 不硬編「PER<15 便宜」(形式),供「估值水位連續量」(功能)、分界交給樹/橫斷面(#9) |
| 溯因→演繹→歸納三步 | 三鏡頭生成 → 紀律閘檢驗 → 五鏡+walk-forward 泛化(§2.2 映射) |
| 質疑假設、市場裁決 | 「設計階段一律以假說自居」「是市場、不是我,決定哪個特徵有用」(#11/#15) |
| 第一性之侷限(自我欺騙) | 提拔關卡(as-of + 去相關 Eff-t + 多因子增量)擋掉「看似第一性其實冗餘/假陽」之候選 |

**三鏡頭分工再確認**:第一性原理(資訊內容/有什麼訊息)× 八二法則(分布形狀/多不均)× 康波(時間結構/在循環哪裡)——同一批 raw 欄位、三族 transform、過同一漏斗。第一性原理是**生成的根**,另二鏡是其旋轉視角。

---

## 來源(2026-06-27 web research)

- [What is First Principles Thinking? — Farnam Street (fs.blog)](https://fs.blog/first-principles/)
- [First Principles: Elon Musk on the Power of Thinking for Yourself — James Clear](https://jamesclear.com/first-principles)
- [From First Principles to Theories: Revisiting the Scientific Method (Abductive/Deductive/Inductive)](https://www.innovativepolicysolutions.org/articles/from-first-principles-to-theories-revisiting-the-scientific-method-through-abductive-deductive-and-inductive-reasoning)
- [Who Uses First Principles Thinking and Why](https://www.innovativepolicysolutions.org/articles/who-uses-first-principles-thinking-and-why-you-should-become-one-of-them)
- [Aristotle and the Importance of First Principles — Medium/The Startup](https://medium.com/swlh/aristotle-and-the-importance-of-first-principles-9431aa60a7d1)
- [First-Principles Thinking vs Reasoning by Analogy — Ahmad Fahmy](https://www.ahmadfahmy.com/blog/2020/7/10/first-principles-thinking-vs-reasoning-by-analogy)
- [What Musk, Bezos, Thiel and Feynman teach us about First Principles — Medium](https://medium.com/@ameet/what-musk-bezos-thiel-and-feynman-teach-us-about-first-principles-261967d3e347)
- [The Quantitative Value Investing Philosophy — Alpha Architect](https://alphaarchitect.com/the-quantitative-value-investing-philosophy/)
- [AlphaLogics: Market Logic-Driven Multi-Agent System for Alpha Factor Generation — arXiv](https://arxiv.org/pdf/2603.20247)
- [Alpha-GPT: Human-AI Interactive Alpha Mining — arXiv](https://arxiv.org/html/2308.00016v2)
- [Understanding Alpha Factors — PyQuantLab/Medium](https://pyquantlab.medium.com/understanding-alpha-factors-the-foundation-of-quantitative-trading-strategies-9b5604e7581c)
