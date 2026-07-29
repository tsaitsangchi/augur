# PME-XDOM-SOLAR S0 範圍裁切／三桶診斷 [I]（2026-07-29）

* **性質**：[I] 診斷帳；**零寫 DB**（本檔僅書面）。  
* **授權**：Steward `開 PME-XDOM-SOLAR-S0`＋`GATE-keep`＋`FZ-keep` → `audits/THREE-FOLLOWUPS-APPROVED-20260729.md`  
* **計畫**：`reports/augur_pme_xdom_solar_plan_20260729.md` §S0；PLAN 登錄＝`audits/PME-XDOM-SOLAR-PLAN-APPROVED-20260729.md`  
* **DB 親驗時點**：2026-07-29（Asia/Taipei ≈16:15；`feature_values`／`philosophy_*`／`principle_factor_map`；readonly）  
* **庫況摘要**：`feature_values` distinct feature＝**38**；總列≈**6,120,489**；`principle_factor_map`＝**89**（`xdom_loop=solar`＝**0**；`ai_predict`＝10；`sunzi_mgmt`＝9）；`solar*`／`solar_supply*` school＝**0**；statement/hypothesis 含 solar／太陽能／漿料之 principle＝**0**

---

## 1. 近程範圍（釘死）

| 項 | 決定 |
|---|---|
| **閉環** | 太陽能材料／電池／漿料／模組**供應鏈公開文獻可溯源概念** → 人撰 `investment` school（建議名 `solar_supply_invest`）原則 → `principle_factor_map` → 台股庫內 `feature_values` |
| **進** | 品質穩定性／產能週期／原物料成本敏感／下游電子・綠能資本支出**代理**等可證偽投資假說；citation 可核；provenance 建議 `xdom_loop=solar` |
| **不進** | 漿料配方／專利全文當 feature；RKI AI×solar probe 命中當資格；knowledge／advisor embedding；AI-PREDICT（OOS／正則／集成）混軸 SEED；NHC 太陽能專答 hardcode；ERP dump |
| **閘** | 本輪**不跑** S1／S3／APPLY；S1／S3 須另令 |
| **對照** | ≠材料 R&D 進化閉環本身；≠「探針綠＝過閘」 |

---

## 2. 候選假說（7 條活＋1 條拒；假說≠真兆）

| ID | 文獻／概念錨（可核方向） | 投資假說（人撰） | 建議市場對映 | 可否證條件 |
|---|---|---|---|---|
| H1 | 製程／品質穩定性 → 毛利緩衝（供應鏈品質文獻常見代理） | 品質穩的供應商較能撑毛利分位、壓低無謂振幅 | `gross_margin_pctile`（＋）／`range_mean_20d`（−）／`volatility_60d`（−） | 閘後 IC 方向與假說同號且雙綠才算活；否則誠實 FAIL |
| H2 | 產能／需求週期 → 營收成長 | 產能爬坡／訂單好轉反映於營收 YoY 與中期動能 | `monthly_revenue_yoy`（＋）／`momentum_60d`（＋） | 同上 |
| H3 | 原物料成本敏感 → 估值／資產負債緩衝 | 成本衝擊期，低槓桿與合理估值較耐震 | `debt_ratio`（−）／`pe_ratio`（−）／`pb_ratio`（−） | 同上 |
| H4 | 下游電子／綠能資本支出代理 → 籌碼認可 | 供應鏈贏家漸獲機構／外資持股認可 | `institutional_net_buy_ratio_20d`（＋）／`foreign_holding_pct`（＋） | 同上 |
| H5 | 擴產後資產效率／獲利能力 | 過擴產壓力下，ROE 與估值需同時成立才活 | `roe`（＋）／`pe_ratio`（−） | 同上 |
| H6 | 週期高點回落／過熱 | 位置過高後均值回歸風險 | `range_position_120d`（−）／`days_since_high_252d`（＋）／`momentum_20d`（弱／對照） | 同上 |
| H7 | 庫存週轉／CapEx 強度／族群相對動能 | （概念相關） | — | **缺特徵**→桶 B；本輪不 SEED；S2 另估零 API 可建 |
| H8 | RKI probe／embedding／漿料配方／AI-PREDICT 混軸 | （靈感-only 或錯軸） | — | **近程不可對映**——拒 SEED（桶 C） |

---

## 3. 三桶（對 `feature_values`；親驗真數）

### A. 可對映（庫內已有序列 → S1 可 SEED）

> 列數＝`COUNT(*)`；窗＝`MIN/MAX(panel_date)`；股數＝`COUNT(DISTINCT stock_id)`。親驗 2026-07-29。

| feature | FV 列數 | panel 窗 | 股數 | 他校已有 map？ | S1 動作 |
|---|---|---|---|---|---|
| `monthly_revenue_yoy` | **155430** | 2007-12-31–2026-06-30 | 2320 | 是（含 ai_predict） | **新**掛 solar school＋`xdom_loop=solar` |
| `gross_margin_pctile` | **146745** | 2008-12-31–2026-06-30 | 2187 | 是 | 新 |
| `debt_ratio` | **98092** | 2018-01-31–2026-06-30 | 2101 | 是 | 新 |
| `roe` | **98236** | 2018-01-31–2026-06-30 | 2094 | 是 | 新 |
| `pe_ratio` | **111580** | 2007-12-31–2026-06-30 | 2071 | 是 | 新 |
| `pb_ratio` | **144027** | 2007-12-31–2026-06-30 | 2115 | 是 | 新 |
| `momentum_20d` | **187316** | 2007-12-31–2026-06-30 | 3082 | 是 | 新（對照／弱） |
| `momentum_60d` | **185811** | 2007-12-31–2026-06-30 | 3059 | 是 | 新 |
| `volatility_60d` | **185812** | 2007-12-31–2026-06-30 | 3059 | 是 | 新 |
| `range_mean_20d` | **187356** | 2007-12-31–2026-06-30 | 3082 | 是 | 新 |
| `range_position_120d` | **183606** | 2007-12-31–2026-06-30 | 3020 | 是 | 新 |
| `institutional_net_buy_ratio_20d` | **167822** | 2012-12-31–2026-06-30 | 2917 | 是 | 新 |
| `foreign_holding_pct` | **163442** | 2007-12-31–2026-06-30 | 2617 | 是 | 新 |
| `days_since_high_252d` | **178665** | 2007-12-31–2026-06-30 | 2945 | 是 | 新 |

**刻意不進桶 A（防名衝突）**

| 名稱 | 理由 |
|---|---|
| `turnover_mean_20d`（庫內有 **187364** 列） | ＝**股價週轉／成交量週轉**，**不是**庫存週轉；不得掛「庫存健康」假說 |
| `margin_usage_ratio`（庫內有） | ＝**融資使用率**，**不是**毛利率 |

### B. 缺特徵（概念相關、庫內無 → S2 候選；本輪不建；FZ-keep）

| 概念代理 | 缺 feature | miss 親驗 `COUNT(*)` | 備註 |
|---|---|---|---|
| 庫存週轉／庫存天數 | `inventory_turnover`／`inventory_days` | **0**／**0** | H7；零 API 可建與否另估 |
| 毛利／營業利益**水準**（非分位） | `gross_margin`／`operating_margin` | **0**／**0** | 有 pctile 可暫代品質軸 |
| 資本支出強度 | `capex`／`capex_to_sales`／`capex_intensity` | **0** | 下游 CapEx 代理近程缺硬指標 |
| 資產週轉 | `asset_turnover` | **0** | |
| 族群／產業相對動能 | `sector_momentum`／相對 strength | **0** | 不得幻造產業標籤列 |
| 模型閘分數類（錯軸） | `model_ic_stability_*` 等 | **0** | 屬 AI-PREDICT／閘內部，**不**當 solar feature |

### C. 不可對映（近程拒 SEED）

| 概念 | 理由 |
|---|---|
| 漿料／銀漿配方、製程專利全文、know-how 原文 | soul-vs-raw；配方≠可交易觀測代理 |
| RKI AI×solar／`knowhow_interaction_probe` 命中率 | V-ORTH；探針≠ map 資格 ≠ G-PROM 憑據 |
| knowledge／advisor embedding 向量 | A.16；永不作 feature |
| AI-PREDICT 混軸 SEED（OOS／正則／集成／purged CV 假說） | ≠ `PME-XDOM-SOLAR`；禁共用 SEED 無分流 |
| NHC 太陽能領域專答 hardcode／顧問 cite 率 | 答得出 ≠ 過閘 |
| ERP／Tiptop dump | 仍鎖；無市場觀測定義 |
| 多晶矽等商品價「靠 FinMind／FRED 新抓」 | **FZ-keep**；缺列誠實，不解凍補洞 |

---

## 4. 拒 SEED 清單（明示；S1 腳本須機械對齊）

1. RKI／探針列、`probe_id` 寫進 map  
2. embedding／sentence vector 當 feature  
3. AI-PREDICT school／`xdom_loop=ai_predict` 假說複用為 solar  
4. 漿料配方／專利全文／顧問專答樹  
5. 把 `turnover_mean_20d`／`margin_usage_ratio` 誤當庫存／毛利  

---

## 5. 驗收錨（S0）

| ID | 結果 |
|---|---|
| 範圍書面可複現 | ✅ 本檔 §1 |
| 假說 3–8 | ✅ §2（H1–H6 活；H7 缺；H8 拒） |
| 三桶真數可複現 | ✅ §3；SQL＝`feature_values` GROUP／WHERE feature＝… |
| 零寫 DB／零 map INSERT／零閘／零 APPLY | ✅ |
| 拒 RKI／embedding／AI-PREDICT 混軸 | ✅ §4 |
| GATE-keep／FZ-keep | ✅ |

**下一步（人）**：`開 PME-XDOM-SOLAR-S1 + GATE-keep + FZ-keep`（策展；**仍禁**急開 S3）。
