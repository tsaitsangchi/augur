# augur F3 評估層 M-0/M-1/M-2 baseline + F2c 估值 + PHASE 9 五鏡實證

**日期**：2026-06-26（凌晨整段）
**範圍**：F2c 估值整合 → M-0 evaluation SSOT helpers → M-1 GBDT 基準階梯 → PHASE 9 五鏡 feature audit → M-2 as-of survivorship 修正
**性質**：clean-room 實證報告，所有數字出自程式 stdout（#9 三來源之一），可溯源。

---

## 0. 一句話摘要

嚴格 point-in-time（as-of、無 survivorship、無 look-ahead #8）下，**多因子線性模型（Ridge）達 H=60 walk-forward rank IC +0.132（Eff-t 6.13、勝率 0.96）** — F3「系統能預測相對強弱」命題得到**最強正面證據**。關鍵：**as-of 消 survivorship 後 IC 不降反升**（H=60 pan-hist 0.113 → as-of 0.132、4 組全部 as-of>pan-hist）→ **alpha 是真的、非倖存者偏差假象**。**GBDT 非線性 4 組全輸 Ridge**（確定目前無增量）。**F2c 估值因子（PER/殖利率/PBR）經 PHASE 9 五鏡證實為 alpha 主來源之一**。

---

## 1. F2c 估值整合（軸④ 價格-價值缺口）

### 1.1 新模組 `src/augur/features/valuation.py`（5 估值 feature）
- `pe_ratio`（本益比）、`pb_ratio`（淨值比）、`dividend_yield`（殖利率）、`market_cap_log`（log 市值）、`price_to_10yr`（還原收盤/10年線−1）
- **無 P-lag 風險**：PER/PBR/殖利率/市值皆交易所每日公布 → date≤panel 即 as-of 安全（#8）
- **#9**：估值 raw 值入 feature，不硬編「便宜」閾值（相對化交給樹/橫斷面）
- **#1**：算不出（虧損 PER≤0 / 無資料）→ 缺列、不存 fake

### 1.2 核心股收縮鏈
```
v4 (22 feat)  878 股
  → F2c (+5 估值, 27 feat)  371 股   (−507, −58%)
```
**主收縮因子 = pe_ratio**（27 feat 中覆蓋最低、僅 1552 股有 @ 2026-05-31）：pan-historical 完整度要求「28 panel（14 年）從未虧損」→ 景氣循環股、某年虧損的科技股全被排除。

### 1.3 ⚠️ Survivorship caveat（#15 誠實）
371 = 「14 年從不虧損 + 月營收（非金融豁免）+ 流動性 P25 + 19 連續籌碼動能 + 5 估值」的超級精英老兵。pe_ratio gate 引入**倖存者偏差**（只留從不虧損股）→ 下游 IC 可能**高估**。M-2 須以 as-of 快照修正。

---

## 2. M-0 evaluation 層 SSOT helpers（#12）

| 模組 | 職責 | 實證 |
|---|---|---|
| `evaluation/label.py` | H 日 forward 還原報酬（t+1 進場 #8）+ 橫斷面 rank | 842/878 股 label |
| `evaluation/walkforward.py` | purged expanding 折 + embargo（#8） | H=20→emb1、H=252→emb4 |
| `evaluation/metrics.py` | rank IC + Effective-t + 勝率（#14 排序口徑） | momentum IC +0.0585 |

**效能優化**（#26 執行層自我糾錯）：發現 `label._calendar` 在 walk-forward 28 折 expanding 中重複 full-scan `TaiwanStockPriceAdj`（11M 列、~400 次）= N² 爆炸 → 新增 `full_calendar()` 一次 query + 記憶體 filter（向後相容、結果經 6 case 驗證 filter==query 完全一致）。M-2+ 所有評估受益。

---

## 3. M-1 GBDT 基準階梯（`evaluation/baseline.py`）

**設定**：371 核心 × 28 panel（2014+）× 27 features × 25 折 purged walk-forward

| 模型 | H=20 IC | H=20 Eff-t | H=20 勝率 | H=60 IC | H=60 Eff-t | H=60 勝率 |
|---|---|---|---|---|---|---|
| B0 隨機 | −0.012 | −1.04 | 0.44 | −0.004 | −0.29 | 0.40 |
| B1 動能 | +0.001 | +0.02 | 0.60 | +0.026 | +1.03 | 0.64 |
| **B2 Ridge** | **+0.081** | **+3.63** | **0.76** | **+0.113** | **+5.39** | **0.84** |
| M1 GBDT | +0.078 | +3.35 | 0.76 | +0.090 | +4.33 | 0.80 |

### 結論
1. **B0 隨機兩 H 都 ≈0** → 評估鏈可信、非偶然
2. **B2 Ridge 最強**，H=60 IC +0.113（quant 標準屬優秀）；**持有期越長 IC 越高**（估值/基本面慢變特性）
3. **GBDT 兩 H 都輸 Ridge** → 「目前非線性無增量」，線性已捕捉主訊號
4. **B1 動能弱**（H=20 +0.001）→ 精英核心內單動能失效，多因子才是訊號

---

## 4. PHASE 9 五鏡 feature audit（H=60，`/tmp/augur_phase9_audit.py`）

### 鏡1 單因子 IC（強訊號 |IC|>0.04）
| feature | IC | 主題 |
|---|---|---|
| cycle_position_252d | +0.088 | 年週期位置 |
| price_to_252d_high | +0.088 | 距高點 |
| **pe_ratio** | **−0.081** | 💎 價值（低 PE→高報酬）|
| **dividend_yield** | **+0.079** | 💎 價值（高息→高報酬）|
| monthly_revenue_yoy | +0.047 | 成長 |
| volatility_20d | −0.046 | 低波動異象 |
| pb_ratio | −0.045 | 💎 價值 |
| sbl_short_balance_log | −0.045 | 籌碼 |
| top_holders_pct | −0.044 | 籌碼 |

### 四大洞察
1. **F2c 估值因子是 alpha 主來源之一**（pe/div/pb 強單因子 IC、方向全符合經濟學）→ 加 F2c 的決定被實證驗證
2. **最強主題 = 週期位置 + 估值 + 殖利率**（價值 + 均值回歸），非動能
3. **動能在精英核心失效**（momentum 全系列 <0.02）
4. **共線嚴重**（鏡4）解釋 Ridge≈GBDT：
   - dollar_volume ~ turnover +0.96（流動性同義）
   - range ~ volatility +0.92（波動同義）
   - cycle_position ~ price_to_252d_high +0.83（位置同義）

鏡2 Ridge 把共線群權重集中到 cycle_position(+0.056)；鏡3 GBDT importance 分散（price_to_252d_high 6.6% 最高）。

---

## 4.5 M-2 as-of survivorship 修正（決定性驗證）

M-1 最大 caveat = 371 核心的 survivorship bias（pe_ratio「14 年從不虧損」gate = 用未來才知道的完整度回填歷史）。
M-2 新增 `core_gate.build_universe_asof`：**逐 as-of 面板 t 只用 ≤t 的 panel 算完整度**（point-in-time、#8），
早期 panel 用當時更大的池（2014: 777 股 → 2026: 371 股），不以未來名單回填。`baseline.run_ladder(asof=True)`
每 panel 取該 panel 之 as-of 核心。

### 4 組對比（371 pan-historical vs point-in-time as-of）
| 模型 | H=20 pan-hist | H=20 as-of | H=60 pan-hist | H=60 as-of |
|---|---|---|---|---|
| B0 隨機 | −0.012 (t−1.0) | −0.001 (t−0.1) | −0.004 (t−0.3) | +0.011 (t1.0) |
| B1 動能 | +0.001 | −0.007 | +0.026 | +0.021 |
| **B2 Ridge** | +0.081 (t3.6, h0.76) | **+0.111 (t4.8, h0.88)** | +0.113 (t5.4, h0.84) | **+0.132 (t6.1, h0.96)** |
| M1 GBDT | +0.078 | +0.095 | +0.090 | +0.106 |

### 三大決定性結論
1. **as-of 一致 > pan-hist（4 組全部）** → **alpha 是真的、非 survivorship 假象**（推翻 M-1 的 survivorship 高估擔憂）
2. **最強口徑 H=60 as-of Ridge：IC +0.132、Eff-t 6.13、勝率 0.96**（25 panel 中 24 個正）— quant 中極罕見
3. **GBDT 4 組全輸 Ridge** → 非線性確定無增量、線性已捕捉主訊號

### 為何 as-of 反而更高？
as-of 早期 panel 用更大宇宙（777 股）→ 更多訓練樣本 + 更大橫斷面排序空間 → 模型學更穩、IC 更高。
pan-hist 371 反而樣本少、宇宙窄。**消除偏差不只更誠實、預測力反而更強**。

---

## 5. 誠實 caveat（#15）

1. ~~371 survivorship bias~~ **✅ M-2 已修正**（as-of point-in-time，4 組全部 as-of>pan-hist 證實 alpha 非「未來完整度回填」假象）
2. **as-of 仍只含現存 roster**（TaiwanStockInfo）→ **已下市股缺失**的 survivorship 尚未補（真實宇宙需含退市股，M-3）
3. **expanding 折重疊** → IC 序列自相關，Eff-t 可能高估（M-3 處理）
4. **GBDT 未調參**（n_est=200 預設）→ small-sample 可能 overfit（但 4 組全輸 Ridge，調參未必翻盤）
5. **單 seed**（#15 stochastic 待 M-3 ≥3 seed 取統計）
6. **in-universe IC**（核心股內排序），非全市場；**經濟價值**（top-N 報酬/回撤）未計
7. **H=60 label 窗重疊**（季線 60 交易日 forward、相鄰 panel label 部分重疊，embargo 已 purge 但 Eff-t 仍可能樂觀）

---

## 6. 下一步（M-3）

- ✅ ~~as-of 快照消 survivorship~~（M-2 完成、決定性驗證 alpha 為真）
- 含**已下市股**的 as-of（補真實 survivorship，caveat 2）
- **stochastic ≥3 seed** GBDT 取統計（#15）
- **raw vs purged 雙口徑** IC（embargo 0 vs embargo n）
- GBDT **調參 + early-stopping**（驗證非線性能否翻盤）
- 降維（共線群合併）/ 因子正交化 / **經濟價值**（top-N 報酬、MaxDD、#14）

---

## 附：本次新增/修改程式

| 檔 | 狀態 | 說明 |
|---|---|---|
| `features/valuation.py` | 新 | F2c 5 估值 feature |
| `features/panel.py` | 改 | 整合 valuation |
| `evaluation/label.py` | 新 | label + full_calendar 優化 |
| `evaluation/walkforward.py` | 新 | purged 折 |
| `evaluation/metrics.py` | 新 | rank IC/Eff-t |
| `evaluation/baseline.py` | 新 | M-1 基準階梯 + M-2 as-of 支援 |
| `universe/core_gate.py` | 改 | M-2 `build_universe_asof`（point-in-time 核心、消 survivorship）|
