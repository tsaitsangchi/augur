# Know-how interaction probe run [I] (2026-07-30T01:09Z)

* 性質：[I] runner 產物；非答案 SSOT；非 [N]
* probes: RKI-AI-SOLAR-RD, RKI-FP-AI-SOLAR, RKI-FP-SOLAR-CORE, KNI-EVAL-EMPTY-CORPUS, RKI-AI-PREDICT-EVAL, RKI-AI-PREDICT-EVO, RKI-FP-AI-ITER, RKI-FP-AI-PREDICT, RKI-FP-PREDICT-ITER, RKI-FP-SOLAR-APP, RKI-FP-SOLAR-CHEM, RKI-FP-SOLAR-PHYS, RKI-PARETO-SOLAR, RKI-PHILO-RD-TMPL, RKI-SUNZI-MGMT
* dry_run: False
* run_id: 7

## RKI-AI-SOLAR-RD

- arity / kind: `2` / `kh_x_kh`
- expanded: 「AI 模型進化（架構／訓練／評測／對齊）」如何強化「太陽能材料研發技術」？（要求：可溯源概念橋；缺料誠實缺口；禁寫死太陽能／AI 專答樹；≠台股因子鏈）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 3
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.096078 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.065045 | axis:knowhow,interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.063556 | axis:knowhow,interaction |
| 4 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.032522 | axis:raw |
| 5 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | axis:knowhow |
| 6 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.031545 | interaction |
| 7 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | axis:raw |
| 8 | work | Analysis of the Phenomena of the Human Mind | 0.016393 | interaction |

## RKI-FP-AI-SOLAR

- arity / kind: `3` / `kh_x_kh_x_kh`
- expanded: 依「第一性原理」如何使用「AI 模型」來強化「太陽能材料研發技術核心」？（要求：可溯源概念橋；缺料誠實；禁寫死技術核心清單／專答樹；≠PME-XDOM-SOLAR 灌因子）
- axis_hits: `{"principle": 6, "method": 6, "domain": 6}`
- merged / multi_src: 18 / 4
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:method,axis:principle,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096079 | axis:domain,axis:principle,interaction |
| 3 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.063811 | axis:domain,interaction |
| 4 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.063811 | axis:domain,interaction |
| 5 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:principle |
| 6 | item | 專案憲章.md | 0.032266 | axis:method |
| 7 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.031778 | axis:method |
| 8 | item | s_first | 0.031545 | axis:principle |

## RKI-FP-SOLAR-CORE

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「第一性原理」列出在「太陽能材料研發」技術核心？（要求：可溯源引用；缺料則誠實說明缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 3
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096079 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.065045 | axis:knowhow,interaction |
| 3 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.063811 | axis:raw,interaction |
| 4 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 5 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | axis:raw |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | interaction |
| 8 | work | 鶡冠子 | 0.016393 | axis:raw |

## KNI-EVAL-EMPTY-CORPUS

- arity / kind: `2` / `kh_x_kh`
- expanded: 「ZZZZ-NONEXISTENT-AXIS-ALPHA-KNI-EVAL」與「ZZZZ-NONEXISTENT-AXIS-BETA-KNI-EVAL」之交互？（評測用無意義軸；期望缺料 decline；禁寫死專答）
- axis_hits: `{"axis_a": 6, "axis_b": 6}`
- merged / multi_src: 15 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | 圖表X軸資料來源欄位位置 | 0.064533 | axis:axis_a,axis:axis_b |
| 2 | item | Molecular factors controlling charge pair generation in orga | 0.064301 | axis:axis_a,axis:axis_b |
| 3 | item | 圖表Y軸資料來源欄位位置 | 0.06309 | axis:axis_a,axis:axis_b |
| 4 | item | Cryo-focused ion beam preparation of perovskite based solar  | 0.032522 | axis:axis_b |
| 5 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.032522 | interaction |
| 6 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | interaction |
| 7 | item | Molecular factors controlling charge pair generation in orga | 0.031778 | axis:axis_a |
| 8 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.031778 | interaction |

## RKI-AI-PREDICT-EVAL

- arity / kind: `2` / `kh_x_kh`
- expanded: How can methods from 「AI model evolution (architecture, training, evaluation, alignment)」(training／eval／alignment) transfer as falsifiable concepts to 「augur investment prediction evolution (PME gates, arena, feature promotion, economic eval)」 without hardcoding answer trees? Cite corpus; gap if missing.
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 16 / 2
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | work | The Secret Doctrine, Vol. 2 of 4: The Synthesis of Science,  | 0.032787 | axis:knowhow,axis:raw |
| 2 | item | Simple and efficient estimation of photovoltaic cells and mo | 0.032522 | axis:knowhow |
| 3 | item | Short-term power prediction of photovoltaic power stations b | 0.032522 | axis:raw |
| 4 | item | Impact of Economic Regulation through Monetary Policy: Impac | 0.032522 | interaction |
| 5 | item | 編號方式 | 0.032266 | axis:knowhow |
| 6 | item | 票券外匯投資基本資料單身檔 | 0.032266 | axis:raw |
| 7 | item | 緩衝層_PostgreSQL_schema設計_20260623.md | 0.032266 | interaction |
| 8 | item | Simple and efficient estimation of photovoltaic cells and mo | 0.031778 | axis:knowhow |

## RKI-AI-PREDICT-EVO

- arity / kind: `2` / `kh_x_kh`
- expanded: 「AI／ML 模型進化」的方法論（架構／訓練／評測／對齊）如何改進「本專案投資預測模型進化（PME、ranker、arena、特徵提拔、經濟終關）」閉環？（要求：可溯源概念橋；缺料誠實缺口；禁寫死專答樹）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 12 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.095356 | axis:knowhow,axis:raw,interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.095334 | axis:knowhow,axis:raw,interaction |
| 4 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | interaction |
| 5 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | axis:knowhow |
| 6 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.031545 | axis:raw |
| 7 | work | 論衡 | 0.016393 | axis:knowhow |
| 8 | work | What is Property? An Inquiry into the Principle of Right and | 0.016393 | interaction |

## RKI-FP-AI-ITER

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「第一性原理」，如何強化「AI 模型自我迭代與再進化」？（要求：可溯源概念橋；缺料誠實缺口；禁寫死「第一性強化 AI 迭代」專答樹）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.063811 | axis:raw,interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.063556 | axis:raw,interaction |
| 4 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 5 | item | README.md | 0.032266 | interaction |
| 6 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.031778 | axis:knowhow |
| 7 | item | s_first | 0.031545 | axis:knowhow |
| 8 | item | rdai_執行進度總覽與交接_20260701.md | 0.031545 | axis:raw |

## RKI-FP-AI-PREDICT

- arity / kind: `2` / `kh_x_kh`
- expanded: 依「第一性原理」強化「AI 模型自我迭代與再進化」後，如何反饋改進「本專案投資預測模型進化閉環」？（optional 交叉軸；可溯源；缺料誠實；禁專答樹；≠PME 灌因子）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.064533 | axis:raw,interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.063556 | axis:raw,interaction |
| 4 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 5 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.031778 | axis:knowhow |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | item | README.md | 0.031545 | interaction |
| 8 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.031545 | axis:raw |

## RKI-FP-PREDICT-ITER

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「第一性原理」，如何強化「本專案投資模擬／預測模型」之自我迭代與再進化？（檢索軸可含 PME／ranker／arena／特徵提拔／經濟終關；要求可溯源；缺料誠實；禁寫死專答樹；≠自動灌因子）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.064533 | axis:raw,interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.063556 | axis:raw,interaction |
| 4 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 5 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.031778 | axis:knowhow |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | item | rdai_執行進度總覽與交接_20260701.md | 0.031545 | axis:raw |
| 8 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | interaction |

## RKI-FP-SOLAR-APP

- arity / kind: `2` / `principle_x_rd`
- expanded: 「第一性原理」在「太陽能材料研發」如何應用？（要求：可溯源引用；缺料則誠實說明缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 12 / 4
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096823 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096079 | axis:knowhow,axis:raw,interaction |
| 3 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.064533 | axis:raw,interaction |
| 4 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.06309 | axis:raw,interaction |
| 5 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | work | The World as Will and Idea (Vol. 2 of 3) | 0.016393 | axis:knowhow |
| 8 | work | 論衡 | 0.016393 | axis:raw |

## RKI-FP-SOLAR-CHEM

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「第一性原理」列出在「太陽能材料研發化學」化學技術核心？（要求：可溯源引用；缺料則誠實說明缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 2
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.095334 | axis:knowhow,axis:raw,interaction |
| 3 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 4 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | interaction |
| 5 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | axis:raw |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | interaction |
| 8 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | axis:raw |

## RKI-FP-SOLAR-PHYS

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「第一性原理」列出在「太陽能材料研發物理學」物理學技術核心？（要求：可溯源引用；缺料則誠實說明缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 14 / 2
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096823 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.096079 | axis:knowhow,axis:raw,interaction |
| 3 | item | 取得當月第一天, 原理同取得最後一天, 只不過是往前推罷了 | 0.032266 | axis:knowhow |
| 4 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | interaction |
| 5 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | axis:raw |
| 6 | item | s_first | 0.031545 | axis:knowhow |
| 7 | item | 專案憲章.md | 0.031545 | axis:raw |
| 8 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.031545 | interaction |

## RKI-PARETO-SOLAR

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「八二法則／Pareto」分析「太陽能材料與供應鏈」的關鍵少數槓桿點（研發／供應鏈／投資可推廣；要求：可溯源；缺料誠實缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 17 / 1
- gap_flags: `[]`
- spurious_risk: `low`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.064301 | axis:knowhow,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.032522 | interaction |
| 3 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.032522 | axis:raw |
| 4 | item | aco-911 | 0.032266 | axis:knowhow |
| 5 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | axis:raw |
| 6 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | interaction |
| 7 | item | 提前通知天數 (天) | 0.031545 | axis:knowhow |
| 8 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.031545 | interaction |

## RKI-PHILO-RD-TMPL

- arity / kind: `2` / `principle_x_rd`
- expanded: 依「{{principle}}」列出在「{{tech_domain}}」研發技術核心？（要求：可溯源引用；缺料則誠實說明缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 13 / 3
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.097567 | axis:knowhow,axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.095334 | axis:knowhow,axis:raw,interaction |
| 3 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.06309 | axis:raw,interaction |
| 4 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | axis:raw |
| 5 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | interaction |
| 6 | item | rdai_全球太陽能資料來源探測報告_20260630.md | 0.032266 | axis:knowhow |
| 7 | item | 操作類型 | 0.031545 | axis:knowhow |
| 8 | work | Chaucer's Translation of Boethius's "De Consolatione Philoso | 0.016393 | axis:raw |

## RKI-SUNZI-MGMT

- arity / kind: `2` / `kh_x_kh`
- expanded: 「孫子兵法」與「企管／投資」的可對照交互概念有哪些？（要求：可溯源；測覆蓋非灌因子；缺料誠實缺口）
- axis_hits: `{"knowhow": 6, "raw": 6}`
- merged / multi_src: 16 / 2
- gap_flags: `['ungrounded_hits']`
- spurious_risk: `high`

| # | kind | title | rrf | sources |
|---|---|---|---|---|
| 1 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.065045 | axis:raw,interaction |
| 2 | item | Post-WIMP User Interface Model for Personal Information Mana | 0.064301 | axis:knowhow,interaction |
| 3 | item | abg-105 | 0.032266 | axis:raw |
| 4 | item | apy-665 | 0.032266 | axis:knowhow |
| 5 | item | rdai_規劃_從外部資料訓練太陽能研發人員_20260630.md | 0.032266 | interaction |
| 6 | item | 00/4615 | 0.031545 | axis:raw |
| 7 | item | 所屬法人 | 0.031545 | axis:knowhow |
| 8 | item | 專案憲章.md | 0.031545 | interaction |
