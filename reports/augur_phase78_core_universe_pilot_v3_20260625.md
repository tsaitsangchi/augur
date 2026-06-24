# augur PHASE 7+8 核心股 pilot v3 — F2b 籌碼整合 + P/E 類教訓

**日期**：2026-06-25（v2 同夜後續、F2b 籌碼擴展）
**觸發**：用戶 directive「寫 chip.py 籌碼模組 + 整合 build_panel + 重跑 35 panel × 22 features」
**承前**：v2（[`augur_phase78_core_universe_pilot_v2_20260624.md`](augur_phase78_core_universe_pilot_v2_20260624.md)）— 終極 633 精英（35 panel × 15 features + 流動性）
**結論**：v3 原版（35 panel 含 2007 × 22 features 含稀疏籌碼）= **0 股**（負面結果、過嚴）；**正解 v3-fixed（2014+ × 19 連續 features）= 742 真精英含籌碼面**。揭露核心 gate 對「異質起始日 + 稀疏事件特徵」的設計限制。

---

## 一、F2b 籌碼 7 features（[`src/augur/features/chip.py`](../src/augur/features/chip.py) 新增）

對應 F2 roadmap F2b 期、特徵設計第一性七軸之軸②（資金流/籌碼）+ Pareto 軸 P1（持股集中）：

| feature | 來源表 | 軸 | 類型 |
|---|---|---|---|
| `institutional_net_buy_ratio_20d` | InstitutionalInvestorsBuySell | ② 資金流 | **P 連續** |
| `margin_usage_ratio` | MarginPurchaseShortSale | ② 槓桿 | **P 連續** |
| `foreign_holding_pct` | Shareholding | ② 籌碼 | **P 連續** |
| `top_holders_pct` | HoldingSharesPer | Pareto P1 | **P 連續** |
| `sbl_short_balance_log` | DailyShortSaleBalances | ② 空方 | **E 稀疏** ⚠️ |
| `lending_fee_rate_mean_30d` | SecuritiesLending | ② 放空成本 | **E 稀疏** ⚠️ |
| `gov_bank_net_buy_60d` | GovernmentBankBuySell | ⑤ 護盤 | **E 稀疏** ⚠️ |

整合：`panel.build_panel` 內同 transaction query（`chip.compute_chip_features(cur, sid, panel_date)`）、217ms/股實證。

---

## 二、完整收縮鏈

| 階段 | 核心股 | 說明 |
|---|---:|---|
| roster | 3106 | |
| v1 10-panel 老兵 | 1211 | 價量 14 |
| v2 終極(35panel+D+E) | 633 | +月營收+流動性 |
| **v3 原版**（35panel 含2007 × 22 含稀疏籌碼）| **0** | ❌ 雙重過嚴 |
| **v3-fixed**（2014+ × 19 連續 features + 流動性 P25）| **742** | ✅ 正解（23.9%）|

---

## 三、v3 = 0 的兩個根因（實證、非 bug）

### 根因① 時間軸錯配（異質起始日）

各 chip 表最早資料日（實證）：

| 表 | 最早日 |
|---|---|
| MarginPurchase（融資）| 2001-01-05 |
| SecuritiesLending（借券費率）| 2003-11-11 |
| Shareholding（外資持股）| 2004-02-12 |
| DailyShortSaleBalances（借券餘額）| 2005-07-01 |
| **InstitutionalInvestors（法人）** | **2012-05-02** |

→ 2007-2011 panel 的 `institutional_net_buy_ratio_20d` = **0 股**（法人表那年不存在）→ 任何含早期 panel 的「全 feature 齊」gate **必然 = 0**。價量特徵 2003+ 有、籌碼特徵 2012+ 才有，放同一含早期 panel 的 gate → 0。

### 根因② 稀疏事件特徵當 P 類

`lending_fee_rate_mean_30d` 在 2014-12-31 panel 只 **762 股**（借券是動態事件、僅熱門股當期被借）。單 panel 有 ~1080-1152 股齊 22 features，但**跨 28 panel 交集 = 0**——因借券標的每期變動，「同股跨 28 panel 每期都有借券費率」≈ 0。

borrow/官股/借券餘額都是 **E 類事件型**（F2 roadmap 定義），把它們當 P 類「算不出即缺列」→ 變成過嚴排除器。

---

## 四、正解（v3-fixed 742 股）

兩個修正：

1. **panel 窗落在所有 P 類特徵共同資料窗**：法人 2012-05 起 → panel ≥2014（年度 2014-2025 + 季度 2021-2025 + as-of = 28 panel）
2. **籌碼分 P/E 類**：
   - **連續 P 類入 gate**（4 個）：`foreign_holding_pct`/`margin_usage_ratio`/`institutional_net_buy_ratio_20d`/`top_holders_pct`（活躍股每期有）
   - **稀疏 E 類不入必齊 gate**（3 個）：`lending_fee_rate_mean_30d`/`sbl_short_balance_log`/`gov_bank_net_buy_60d`（待改真零語意）

→ 19 features（14 價量 + 月營收 + 4 連續籌碼）× 28 panel × 流動性 P25 = **742 真精英（含籌碼面）**

代表性權值股在核心：2330 台積電 · 2454 聯發科 · 2882 國泰金 · 1216 統一 · 1301 台塑 · 2002 中鋼。

---

## 五、教訓 + 待辦（P/E 重構）

### 核心教訓
**核心股 gate 對「異質起始日 + 稀疏事件」特徵需區別處理**——不能把所有特徵塞進同一個「全 panel 全 feature 齊」：
- **時間軸**：walk-forward panel 窗必須在所有必齊特徵的**共同資料窗**內（最晚起始的特徵決定下界）
- **稀疏度**：事件型（E 類）特徵應**真零語意**（無事件=0、不缺列），非「算不出即缺列」（後者使其變排除器）

### 待辦（P/E 重構、明日清醒做）
1. **chip.py E 類改真零**：`lending_fee_rate`/`sbl_short_balance`/`gov_bank_net_buy` 無資料時填 0（代表無放空壓力/無官股介入），對應 F2 roadmap E 類「真零語意（#7 PASS 前提下無列=真 0）」——但需先確認該表 #7 對帳 PASS（否則「未抓」≠0）
2. **core_gate panel 窗 as-of 感知**：或 build_universe 加參數標明「各 feature 最早可用 panel」、自動落在共同窗
3. **重跑驗證**：E 類真零 + 全 35 panel → 應比 742 多（早期 panel 因法人表 2012 限制仍卡 2007-2011，故實務 panel 窗仍宜 2014+）

---

## 六、DB 狀態（as-of report 時點）

| 表 | 內容 |
|---|---|
| `feature_values` | ~1,595,238 列 / 35 panels(2007/12 ~ 2026/5) / 3096 股 / 22 features（含 7 籌碼）|
| `core_universe` | **742 股**（v3-fixed:2014+ × 19 連續 features、最後 build_universe 寫入）|

---

## 七、22 features 覆蓋分布（panel 2026-05-31、單 panel）

| feature | 股數 | 類 |
|---|---:|---|
| turnover_mean_20d | 3084 | 價量 |
| dollar_volume_log_20d / range_mean_20d / volume_surge_5_60 | 3059 | 價量 |
| top_holders_pct | 2925 | 籌碼 P |
| institutional_net_buy_ratio_20d | 2912 | 籌碼 P |
| volatility_60d | 2631 | 價量 |
| foreign_holding_pct | 2619 | 籌碼 P |
| sbl_short_balance_log | 2446 | 籌碼 E ⚠️ |
| monthly_revenue_yoy | 2288 | 基本面 |
| margin_usage_ratio | 2136 | 籌碼 P |
| **lending_fee_rate_mean_30d** | **1851** | 籌碼 E ⚠️ 最稀疏 |

（gov_bank_net_buy_60d 2781、其餘價量 momentum/cycle 2813-2989）

---

## 八、SSOT 對齊

- 治權：原則精華 #1 #10 #20 + 憲章第三部 universe/feature 段（無變更）
- code：
  - [`src/augur/features/chip.py`](../src/augur/features/chip.py)（F2b 籌碼 7 features、docstring 標 P/E 限制）
  - [`src/augur/features/panel.py`](../src/augur/features/panel.py)（chip 整合 build_panel）
- 上游：v2 [`augur_phase78_core_universe_pilot_v2_20260624.md`](augur_phase78_core_universe_pilot_v2_20260624.md)
- F2 roadmap：[`augur_f2_feature_expansion_roadmap_20260612.md`](augur_f2_feature_expansion_roadmap_20260612.md)（E 類真零定義）
- 演進記錄：本檔 v3 = F2b 籌碼整合 + P/E 教訓 SSOT；P/E 重構後出 v4
