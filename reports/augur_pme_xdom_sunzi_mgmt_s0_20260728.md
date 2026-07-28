# PME-XDOM-SUNZI-MGMT S0 範圍裁切／三桶診斷 [I]（2026-07-28）

* **性質**：[I] 診斷帳；**零寫 DB**（本檔僅書面）。  
* **授權**：`PME-XDOM-YES`＋`PME-XDOM-SUNZI-MGMT`＋`GATE-keep`＋`FZ-keep` → `audits/PME-XDOM-PLAN-APPROVED-20260728.md`  
* **計畫**：`reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md` §3 S0  
* **DB 親驗時點**：2026-07-28（`feature_values`／`philosophy_*`／`principle_factor_map`）

---

## 1. 近程範圍（釘死）

| 項 | 決定 |
|---|---|
| **閉環** | 孫子×企管**文獻橋**（investment school 載體＝既有 `sun_tzu`，`domain='investment'`） |
| **進** | 可核 citation 之人撰原則 → `principle_factor_map`（庫內已有／可對映 feature） |
| **不進** | ERP／Tiptop dump 自動 SEED；太陽能材料閉環（另拍 `PME-XDOM-SOLAR`）；顧問 cite 率當過閘 |
| **閘** | 本輪**不跑** S3；標待開 `PME-XDOM-S3` |

---

## 2. 候選假說（6 條；假說≠真兆）

| ID | 古典錨（可核） | 企管橋假說（人撰） | 建議市場對映 | 可否證條件（一句） |
|---|---|---|---|---|
| H1 | 「知彼知己，百戰不殆」 | 情報／對手動向優勢 → 機構／官股籌碼代理 | `gov_bank_net_buy_60d`／`top_holders_pct`／`inst_cumflow_position_60d`（＋既有 `institutional_net_buy_ratio_20d`／`foreign_holding_pct`） | 閘後 IC 方向與假說同號且雙綠才算活；否則誠實 FAIL |
| H2 | 「先為不可勝」「先勝而後求戰」 | 先立財務／品質緩衝再求戰 | `debt_ratio`（−）／`roe`（＋）／`range_mean_20d`（−） | 同上 |
| H3 | 「避實而擊虛」 | 避高估實、擊低估虛 | 既有 `pe_ratio`（−）；擴 `pb_ratio`（−） | 同上 |
| H4 | 「兵貴神速」／勢節 | 節奏／時點優勢 | 既有 `momentum_60d`／`range_position_120d`；擴 `momentum_20d`（＋） | 同上 |
| H5 | 「不戰而屈人之兵」 | 品質壁壘使對手不戰自屈 | `gross_margin_pctile`（＋）；既有 `volatility_60d`（−） | 同上 |
| H6 | ERP 操作語意／4gl | （靈感-only） | — | **近程不可對映**——無市場觀測定義則拒 SEED |

既有 DB：`sun_tzu` school_id=83；原則 4 條；map 6 列（皆已有 `feature_values`）。S1 在此基底上**加**文獻橋原則／map，不手改既有 `validated_*`。

---

## 3. 三桶（對 `feature_values`；親驗）

### A. 可對映（庫內已有序列 → S1 可 SEED）

| feature | FV 列數（約） | panel 窗 | 既有他校 map？ | S1 動作 |
|---|---|---|---|---|
| `institutional_net_buy_ratio_20d` | 67472 | 2012–2026-06-30 | sun_tzu 已有 | 保留；provenance 不改舊列 |
| `foreign_holding_pct` | 68839 | 2007–2026-06-30 | sun_tzu 已有 | 同上 |
| `pe_ratio` | 46889 | 2007–2026-06-30 | sun_tzu 已有 | 同上 |
| `momentum_60d` | 78958 | 2007–2026-06-30 | sun_tzu 已有 | 同上 |
| `range_position_120d` | 78042 | 2007–2026-06-30 | sun_tzu 已有 | 同上 |
| `volatility_60d` | 78957 | 2007–2026-06-30 | sun_tzu 已有 | 同上 |
| `gov_bank_net_buy_60d` | 50594 | 2021–2026-06-30 | smart_money | **新**掛 sun_tzu×企管橋原則 |
| `top_holders_pct` | 68304 | 2010–2026-06-30 | smart_money | 新 |
| `inst_cumflow_position_60d` | 64812 | 2012–2026-06-30 | cycle | 新 |
| `debt_ratio` | 16140 | 2021–2026-06-30 | quality_qmj | 新 |
| `roe` | 16182 | 2021–2026-06-30 | quality_qmj | 新 |
| `range_mean_20d` | 79637 | 2007–2026-06-30 | low_vol | 新 |
| `pb_ratio` | 60838 | 2007–2026-06-30 | value | 新 |
| `momentum_20d` | 79627 | 2007–2026-06-30 | momentum | 新 |
| `gross_margin_pctile` | 61333 | （庫內有） | quality／quality_qmj | 新 |

### B. 缺特徵（概念相關、庫內無／不足 → S2 候選；本輪不建）

| 概念代理 | 缺 feature | 備註 |
|---|---|---|
| 流動性緩衝 | `current_ratio`／`cash_ratio` | 零 API 可建與否另估；**本輪不標 validated** |
| 毛利水準（非分位） | `gross_margin`／`operating_margin` | 有 `gross_margin_pctile` 可暫代；raw 缺 |

### C. 不可對映（近程拒 SEED）

| 概念 | 理由 |
|---|---|
| ERP／Tiptop 表欄、4gl 操作步驟 | 無台股可觀測對映；`PME-XDOM-SUNZI-MGMT` 明示排除 dump 自動灌 |
| 太陽能漿料製程 know-how | 範圍外（次條 `PME-XDOM-SOLAR`） |
| knowledge／advisor embedding | A.16；永不作 feature |

---

## 4. 驗收錨（S0）

| ID | 結果 |
|---|---|
| 範圍書面可複現 | ✅ 本檔 |
| 三桶可複現 | ✅ §3；SQL＝`feature_values`／`principle_factor_map` |
| 零寫 DB | ✅ |
| ERP／solar 明示排除 | ✅ |

**下一步**：S1＝`scripts/curate_pme_xdom_map.py --apply`；**不**跑閘。
