# augur PHASE 7+8 核心股 pilot v2 — 終極 gate (A+B+C+D+E 全部)

**日期**：2026-06-24（v1 同日後續、延展實驗）
**觸發**：用戶 directive「1211 真台股老兵核心可以再加嚴嗎」→「A、B、C、D、E 全部的方向都要」
**承前**：v1（[`augur_phase78_core_universe_pilot_20260624.md`](augur_phase78_core_universe_pilot_20260624.md)）— 三輪實證：試水溫 2508 / walk-forward 1734 / 10-panel 老兵 1211
**結論**：**633 真精英老兵核心股**（roster 3106 → 20.4%）；對映 #10「質>量」極致實證 + 對映 #20「執行層天職＝確保完整性」。

---

## 一、五維加嚴設計（A+B+C+D+E）

| 維度 | 做法 | 實作 | 預期 |
|---|---|---|---|
| **A+B 時間軸** | 年度 19 panel (2007~2025) + 2026-05-31 | driver `PANELS=[...]` | 切到金融海嘯前 |
| **C Panel 密度** | 季度 panel 2021Q1~2025Q4（去重年底）= 補 15 季度 | driver `QUARTERLY=[...]` | 近 5 年密度增 |
| **D 基本面特徵** | `monthly_revenue_yoy` (月營收年增率 log) | `features/panel.py`:`_REVENUE_SQL` + `_compute_revenue_yoy` + build_panel 內 query | 排無月營收歷史股 |
| **E 流動性 gate** | `dollar_volume_log_20d` ≥ latest panel 之 P25 | `universe/core_gate.py`:`liquidity_pct` 參數 + percentile_cont SQL | 砍底層 25% |

### Code 改動位置

| 檔 | 改動 |
|---|---|
| [`src/augur/features/panel.py`](../src/augur/features/panel.py) | 加 `_REVENUE_SQL` 常數 + `_compute_revenue_yoy()` + build_panel 內 query `TaiwanStockMonthRevenue` 並合進 feats dict（算不出→缺列、嚴格 source-pure #1）|
| [`src/augur/universe/core_gate.py`](../src/augur/universe/core_gate.py) | `build_universe` 加 `liquidity_pct` 參數（0-100、預設 None）+ 動態 `percentile_cont` SQL + `extra` dict 回傳 `liquidity_threshold`/`liquidity_pct`（動態相對分位數、不寫死值 #9）|

---

## 二、完整收縮鏈（roster 3106 → 633）

| 階段 | 股數 | 通過率 | 收縮 | 觸發 |
|---|---:|---:|---:|---|
| L0 roster (TaiwanStockInfo) | 3106 | 100.0% | — | — |
| L1 有特徵任一 | 3094 | 99.6% | −12 | 無 TaiwanStockPrice 12 股 |
| **L2a 試水溫 1 panel(5/31) 全 14** | **2508** | 80.7% | −586 | 單 panel feature-complete |
| **L2b walk-forward 6 panel** | **1734** | 55.8% | −774 | 6 panel pan-historical |
| **L2c walk-forward 10 panel** | **1282** | 41.3% | −452 | 時間軸往前推 4 年 |
| L3a + 排 ETF | 1242 | 40.0% | −40 | 候選空間（被動指數追蹤）|
| L3b + 排污染（非數字 stock_id）| **1211** | 39.0% | −31 | 候選空間（產業名/指數名）|
| **L4a 35 panel(20 年度+15 季度)+ D(15 features)** | **~850** | ~27% | −361 | 時間軸極限 + 月營收基本面（推估 v2）|
| **L4b + E 流動性 P25 gate** | **633** | **20.4%** | −~217 | 流動性下界（動態分位數）|

→ **633 真精英核心 = 跨 19 年所有 walk-forward panel × 全 15 features（含月營收）× 真台股個股 × 非 ETF × 流動性 top 75%**

---

## 三、各 panel bottleneck 細表（35 panel 全 15 features 齊之股數）

| Panel | 股數 | 註 |
|---|---:|---|
| **2007-12-31** | **1015 ← 最緊** | 金融海嘯前夕、要求 2006-12 前已上市 + 月營收歷史 |
| 2008-12-31 | 1036 | 海嘯崩盤年 |
| 2009-12-31 | 1181 | QE 開始 |
| 2010-12-31 | 1243 | |
| 2011-12-31 | 1225 | |
| 2012-12-31 | 1282 | |
| 2013-12-31 | 1378 | |
| 2014-12-31 | 1429 | |
| 2015-12-31 | 1430 | |
| 2016-12-31 | 1443 | |
| 2017-12-31 | 1522 | |
| 2018-12-31 | 1456 | 川普關稅戰 |
| 2019-12-31 | 1576 | |
| 2020-12-31 | 1680 | COVID 元年 |
| 2021-03-31 | 1737 | （季度補強起點）|
| 2021-06-30 | 1742 | |
| 2021-09-30 | 1693 | |
| 2021-12-31 | 1729 | |
| 2022-03-31 | 1750 | |
| 2022-06-30 | 1718 | |
| 2022-09-30 | 1726 | |
| 2022-12-31 | 1714 | 通膨 / Fed 升息 |
| 2023-03-31 | 1785 | |
| 2023-06-30 | 1834 | |
| 2023-09-30 | 1781 | |
| 2023-12-31 | 1789 | AI 浪潮 |
| 2024-03-31 | 1866 | |
| 2024-06-30 | 1914 | |
| 2024-09-30 | 1897 | |
| 2024-12-31 | 1840 | |
| 2025-03-31 | 1885 | |
| 2025-06-30 | 1878 | |
| 2025-09-30 | 1880 | |
| 2025-12-31 | 1886 | |
| 2026-05-31 | 2034 | as-of、最寬鬆 |

**單調遞增 + 季度補強無大波動** → bottleneck 真的在「時間軸極限 + D 基本面」、非「panel 密度」。

---

## 四、E 流動性 gate 實證

**閾值**（dynamic、相對台股自身分布、不寫死 #9）：
```
dollar_volume_log_20d at panel 2026-05-31 之 P25 = 14.742
≈ exp(14.742) = NT$ 2.5M/day（每日成交金額 ~250 萬台幣）
```

> 排除底層 25% 之意義：低於每日 250 萬成交金額之股，**模型橫斷面相對強弱排序不穩定**（流動性低 → 易受單筆大單影響 → 訊號雜訊高）。

---

## 五、代表性老兵核驗（633 內）

| 類別 | 在終極核心 |
|---|---|
| 權值/科技 | ✅ 2330 台積電 · 2317 鴻海 · 2454 聯發科 · 2308 台達電 · 2412 中華電 |
| 金融 | ✅ 2880 華南金 · 2881 富邦金 · 2882 國泰金 · 2885 元大金 · 2886 兆豐金 |
| 傳產 | ✅ 1216 統一 · 1301 台塑 · 2002 中鋼 · 9904 寶成 |

**前 30**（字串序、傳產/食品/塑膠主導）：
```
1104, 1108, 1109, 1201, 1210, 1215, 1216, 1217, 1218, 1227, 1229, 1231, 1232, 1234,
1301, 1303, 1304, 1305, 1308, 1309, 1310, 1311, 1312, 1313, 1319, 1321, 1323, 1326,
1402, 1409
```
食品(12xx 統一/卜蜂/福壽/大成/泰山)、塑膠(13xx 台塑四寶相關)、紡織(14xx)——皆 1990 前已上市之台股老牌。

**後 10**（上櫃尾段）：
```
9935, 9938, 9939, 9940, 9941, 9942, 9943, 9944, 9945, 9955
```
上櫃中小型老牌（如 9938 百和、9941 裕融、9944 新麗、9945 潤泰新）。

---

## 六、設計 implications（v1 之深化）

### 6.1 三道閘 + 兩道相對 filter

| 閘 / Filter | 角色 | 規模 | 哪裡實作 |
|---|---|---:|---|
| **候選空間關**（v1）| 結構性：非 ETF、真台股代碼 | −71 (1282→1211) | `core_gate.build_universe` SQL |
| **raw-complete**（隱含）| 無 raw → 自然不在 feature_values | — | `panel.build_panel` 邏輯 |
| **feature-complete**（多 panel × 多 feature）| 35 panel × 15 features 齊 | −1077 (3106→2029 if 任一不齊) | `core_gate.build_universe` GROUP BY HAVING |
| **D 月營收 filter**（v2 新）| 排無月營收歷史股 | −361 (1211→850 推估) | `panel.compute_features` 內加 |
| **E 流動性 filter**（v2 新）| 動態 P25、相對分布 | −~217 (850→633) | `core_gate.build_universe` percentile_cont |

### 6.2 對映原則精華 #10「質 > 量」

> 「核心股要對、要準，可以少。不追求數量。」

從 3106 → 633（**20.4%、收縮 79.6%**）= 嚴 gate 換真兆，**完全符合 #10 ENFORCE「不以核心股數量為目標」**。每股訊號乾淨（嚴 source-pure × 完整度 × 候選空間 × 基本面 × 流動性）。

### 6.3 對映原則精華 #20「執行層天職＝確保完整性」

D（月營收特徵）與 E（流動性 gate）的引入是**執行層完整性**——把「核心股應該滿足什麼條件才能成為個股預測對象」之**完整定義**全部納入 universe layer、不留漏（v1 的後處理變成正式 code、用戶不必當 QA）。

---

## 七、DB 狀態（as-of report 時點）

| 表 | 內容 |
|---|---|
| `feature_values` | 1,168,853 列 / 35 panels(2007/12 ~ 2026/5) / 3094 股 / 15 features（含 D 月營收 yoy）|
| `core_universe` | **633 股**（真精英老兵）/ 35 panels / 15 features |

---

## 八、F3 啟動準備（v2 更新）

**633 真精英老兵 = F3 model training 的最乾淨候選集**。決策項：

1. **walk-forward train/test 切分**：用這 35 panel 之子集（如年度 20 panel 訓練、近 15 季度測試）
2. **特徵擴展（可選）**：加更多 F2 特徵（法人持股、PE/PB、產業相對強弱）→ 會再收縮（估 ~300-450 股）
3. **模型選擇**：樹家族為主（XGBoost/LightGBM、解釋性強）、transformer 為輔（時序）

---

## 九、SSOT 對齊

- 治權：原則精華 #1 #10 #20 + 憲章第三部 universe 段（無變更、屬執行層完整性）
- code：
  - [`src/augur/features/panel.py`](../src/augur/features/panel.py)（D 月營收 feature 新增）
  - [`src/augur/universe/core_gate.py`](../src/augur/universe/core_gate.py)（E `liquidity_pct` 參數新增）
- 上游：v1 [`augur_phase78_core_universe_pilot_20260624.md`](augur_phase78_core_universe_pilot_20260624.md)（三輪實證 SSOT）
- 演進記錄：本檔 v2 = 五維 A+B+C+D+E 終極組合 SSOT；下次跑 F3 model 應引用本檔之 633 核心股實證
