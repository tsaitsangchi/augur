# 交互候選值建置計畫（INTERACT-BUILD）——7 掛向交互特徵之逐欄 as-of 派生

> [I] 計畫書（#20 計畫先行；拍板前零實作）。動因：燃料線 7 顆交互特徵已具 map 方向列（hugo 2026-07-29 核）但**無值**——它們是 (b) 線下一批彈藥；值派生先前**有意識延後**正因逐欄 as-of 設計未做（本檔補齊）。

## 一、目標與邊界

把 7 顆交互特徵材料化進 `feature_candidate_values`（staging、非生產），供四關漏斗（第 1 關 HAC-IC → 第 2 關增量 → 符號尺〔方向列已備〕→ 經濟終關）。**不動生產表、不入模**；失敗即 staging 清場。

## 二、承重事實（親讀 code）

- **hint 語意 SSOT**＝`audit/field_correlation.py`：日頻對齊面板（PriceAdj 交易日基準）、level＝原始水位／change＝日一階差；模組自宣「**探索性、非 as-of**；用於特徵須另過 #8」——本計畫即該條款的兌現。
- **配方 ≠ 相關結構**（誠實界定）：hint 只證兩欄**相關結構存在**（跨股中位 .62–.82）；把它變成月頻可交易特徵是**特徵化決策**（見 §三），非 hint 自帶。

## 三、特徵配方（設計決策，拍板標的）

月頻 `panel_date`、as-of 宇宙（`core_universe_asof`），對每股：

```
parent_A = 20 交易日窗聚合(欄 A;level=窗內日值均值 / change=窗內日差均值)
interaction = z_cs(parent_A) × z_cs(parent_B)     ← 同 panel 橫斷面 z(as-of,僅用 ≤t)
```

- z 積為標準交互構造（尺度可比、防 raw 乘積量綱爆炸）；20d 窗與生產特徵慣例一致；
- **revenue 特例**：取「panel 日已發布之最近月營收」——**15 日發布閘**（panel 日 <16 號→用前前月；≥16 號→可用前月），不 ffill 日頻（探索面板的 ffill 不進生產派生）；
- 7 顆逐欄可見性規則：

| 欄 | 源表(面板欄) | 可見規則 | 查核項 |
|---|---|---|---|
| close/volume/money/turnover | PriceAdj | 交易日收盤即知（T+0） | — |
| inst_gross | 三大法人聚合 | 盤後公布＝T+0 晚（panel 月末收盤後計算→可用） | ⚠實作時 probe 公布 lag 親驗 |
| sbl_balance | 借券表 | 盤後 T+0/T+1 | ⚠同上親驗 |
| market_value | 市值日表 | T+0 | — |
| revenue | 月營收（元） | **15 日閘**如上 | 申報遲交列以 raw `date` 欄實際值為準 |

## 四、(a) schema：零新表

寫入＝既有 `feature_candidate_values(panel_date, stock_id, feature, value)`（`fc.FEATURE_TABLE`）；讀＝上表 raw 源＋`core_universe_asof`。7 特徵名逐字＝map 列名（符號尺對齊）。

## 五、(b) 程式規畫

| 檔 | 職責 |
|---|---|
| `scripts/build_interaction_candidates.py`（新） | `--features`（預設 7 顆）`--dry-run`（單 panel 單股印中間量）`--run`（全 panel 材料化、冪等 upsert）`--audit-visibility`（逐欄洩漏自稽：revenue 用月 ≤ 閘允許月之斷言全掃）`--clear`（staging 清場）`--selftest`（z 積數學／15 日閘 fixture／change 定義鎖） |
| `verify_candidate_promotion.py`（既有） | 零改動——`--features` 直接吃新候選 |
| `verify_sign_consistency.py`（既有） | 零改動——map 列已備 |

## 六、驗收（機械）＋停損

1. selftest 全綠；`--audit-visibility` 零違例；
2. 抽 3 股 × 3 panel 人工對帳 raw 中間量（#15 實證非我以為）；
3. 材料化後四關照跑（A2-wave-2）；任一步失敗→`--clear` 退場，生產零污染。
4. **不做**：不改 field_correlation（探索歸探索）；不派生 defer 中的 #13/14/15；revenue 不 ffill。

**待一字**：`INTERACT-BUILD-go`（§三配方一併核；要改窗口/z 構造請註明）。
