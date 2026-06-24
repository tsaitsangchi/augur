# augur PHASE 7+8 核心股 pilot — 三輪 walk-forward 實證 + ETF/污染過濾入 universe layer

**日期**：2026-06-24
**觸發**：用戶 directive「先用 as-of 2026-05-31 單一 panel + roster 全部當候選做一次」→「跑更嚴 gate」→「ETF 全排除在核心之外」→「ETF 過濾 + 污染過濾正式入 universe layer」
**前置**：as-of 2026-05-31 84/84 完整(2026-06-24)、9 對帳 FAIL 全閉環、F2/F3 凍結解除
**結論**：**1211 純真台股老兵核心股**(roster 3106 → 39.0%)；ETF/污染過濾入 [`src/augur/universe/core_gate.py`](../src/augur/universe/core_gate.py)；對映 #10「質>量」全鏈實證。

---

## 一、三輪實證收縮鏈

| 階段 | gate 條件 | 核心股 | 通過率 | 收縮 |
|---|---|---:|---:|---:|
| L0 roster | TaiwanStockInfo 全 | 3106 | 100.0% | — |
| L1 有特徵(任一) | 至少 1 個 feature 算得出 | 3094 | 99.6% | −12 |
| **L2a 試水溫** | 單 panel 2026-05-31 全 14 features | **2508** | 80.7% | −586 |
| **L2b walk-forward** | 6-panel (2021/12 ~ 2026/5) 全 14 features 全 panel | **1734** | 55.8% | −774 |
| **L2c 更嚴 gate** | 10-panel (2017/12 ~ 2026/5) 全 14 features 全 panel | **1282** | 41.3% | −452 |
| L3a + 排 ETF | industry_category 屬 ETF 類 | 1242 | 40.0% | −40 |
| L3b + 排 roster 污染 | stock_id 非數字開頭(產業名/指數名) | **1211** | **39.0%** | −31 |

→ **F3 model training 用 1211 老兵核心**。

## 二、各 panel bottleneck（10-panel 實證）

| Panel | 全 14 features 之股數 |
|---|---:|
| 2017-12-31 ← **最緊** | 1630 |
| 2018-12-31 | 1604 |
| 2019-12-31 | 1768 |
| 2020-12-31 | 1966 |
| 2021-12-31 | 2028 |
| 2022-12-31 | 2057 |
| 2023-12-31 | 2173 |
| 2024-12-31 | 2278 |
| 2025-12-31 | 2342 |
| 2026-05-31 | 2508 |

**單調遞增** → 時間越早、可算特徵之股數越少（要求 252 日 ≈ 1 年價量序列）。pan-historical 1282 ≤ min(1604) − 322 為交集效應（某股能在 panel A 通過但 panel B 缺）。

## 三、Canonical features 分布（試水溫 panel 2026-05-31 之 14 features）

| Feature | 算得出之股數 | 通過率 |
|---|---:|---:|
| turnover_mean_20d | 3084 | 99.3% |
| dollar_volume_log_20d | 3059 | 98.5% |
| range_mean_20d | 3059 | 98.5% |
| volume_surge_5_60 | 3059 | 98.5% |
| return_1d | 2989 | 96.2% |
| momentum_5d | 2974 | 95.7% |
| momentum_20d | 2963 | 95.4% |
| cycle_position_252d | 2946 | 94.8% |
| price_to_252d_high | 2946 | 94.8% |
| momentum_60d | 2943 | 94.7% |
| momentum_120d | 2870 | 92.4% |
| momentum_252d | 2813 | 90.6% |
| volatility_20d | 2802 | 90.2% |
| **volatility_60d** | **2631** | **84.7%** ← 單 panel 最緊 |

最緊單一 feature gate = `volatility_60d`（要求 ≥60 日連續價格資料）；但 single-panel 交集後核心 2508 仍小於 2631（因不同股缺不同 feature）。

## 四、ETF + 污染過濾入 universe layer

### 4.1 設計理由（非判準變更、屬「候選空間定義」）

- **ETF 排除**：被動指數追蹤（持有其他股之組合）非個股預測對象；augur 的橫斷面相對強弱排序對 ETF 之間比較無實質意義（ETF return = 成分股 weighted return 之投射）。
- **roster 污染排除**：`TaiwanStockInfo.stock_id` 欄混入非股票項——產業分類名（`Automobile` / `Tourism` / `Textiles` 等 28 個）+ 指數代號（`TAIEX` / `TPEx`）+ 其他（`Other`）= 31 個污染項，竟通過完整度 gate（因它們在 `TaiwanStockPrice` 也有「資料」可算特徵）。結構性排除。

### 4.2 ETF 識別（實證 TaiwanStockInfo）

```sql
industry_category IN ('ETF', '上櫃指數股票型基金(ETF)', '上櫃ETF')
-- 上市 ETF: 261 檔; 上櫃 ETF 主分類: 125 檔; 上櫃 ETF 別分類: 119 檔; 全集 505 檔
```

### 4.3 真股票代碼識別

```sql
stock_id ~ '^[0-9]'   -- 數字開頭
-- 通過: 1101 / 00631L / 01005T / 2882B 等
-- 排除: 'Automobile' / 'TAIEX' / 'Tourism' 等純字母開頭
```

### 4.4 Code 改動

[`src/augur/universe/core_gate.py`](../src/augur/universe/core_gate.py)：
- docstring 加「候選空間關」說明
- 加 `ETF_INDUSTRY` 常數 + `_REAL_STOCK_PREDICATE` SQL predicate
- `build_universe` SQL 加 `NOT EXISTS (SELECT 1 FROM TaiwanStockInfo si WHERE si.stock_id=fv.stock_id AND si.industry_category IN ETF_INDUSTRY)` + `AND stock_id ~ '^[0-9]'`

### 4.5 驗證

重跑 `build_universe(conn, 10_panels)` 後：
- 核心 = **1211 股**（與後處理結果一致）
- 含 ETF = 0
- 含污染 = 0

## 五、代表性老兵全在核心（實證 1211 內）

| 類別 | 樣本 |
|---|---|
| 權值/科技 | 2330 台積電 · 2317 鴻海 · 2454 聯發科 · 2308 台達電 · 2412 中華電 |
| 金融 | 2880 華南金 · 2881 富邦金 · 2882 國泰金 · 2885 元大金 · 2886 兆豐金 |
| 傳產老牌 | 1101 台泥 · 1216 統一 · 1301 台塑 · 1303 南亞 · 2002 中鋼 |
| 上櫃尾段樣本 | 9946 · 9951 · 9955 · 9957 · 9958 |

**前 30 真核心股**（字串序）：
```
01005T, 01008T, 1101, 1102, 1103, 1104, 1107, 1108, 1109,
1201, 1210, 1215, 1216, 1217, 1218, 1220, 1227, 1229, 1231, 1232, 1234, 1236,
1301, 1303, 1304, 1305, 1307, 1308, 1309, 1310
```

## 六、設計 implications

### 對映原則精華 #10「質 > 量」

> 「核心股要對、要準，可以少。不追求數量。」

從 roster 3106 → 1211（39%）= 嚴 gate 換真兆，完全符合 #10 ENFORCE「不以核心股數量為目標」。

### 三道閘的分工

| 閘 | 角色 | 哪裡實作 |
|---|---|---|
| **候選空間關** | 結構性定義「什麼才是個股預測對象」（非 ETF、真股票） | `core_gate.build_universe` SQL filter（本次新增） |
| **raw-complete 關** | 隱含——無 TaiwanStockPrice 資料 → 算不出特徵 → 自然不入 feature_values | `panel.build_panel` 邏輯（既有） |
| **feature-complete 關** | 在所有 panel 都備齊全部 canonical features | `core_gate.build_universe` GROUP BY HAVING（既有） |

候選空間關 = PHASE 6「核心候選（raw 完整）」之**結構性補強**——之前 PHASE 6 隱含為「roster ∩ raw 有資料」、未排 ETF / 污染；本次將「真台股個股」之語義明確化。

### F3 啟動準備

**1211 老兵核心股就是 F3 model training 的乾淨候選集**。下一階段需決策：
1. walk-forward 設計（panel_date 集合、間隔、train/test split）
2. 是否加 F2 特徵（籌碼 / 基本面 / 總經 lag）→ 會再收縮核心股
3. 模型選擇（樹家族為主、transformer 為輔，#10 設計）

## 七、DB 狀態（as-of report 時點）

| 表 | 內容 |
|---|---|
| `feature_values` | 224,667 列 / 10 panels(2017/12 ~ 2026/5) / 3094 股 / 14 features |
| `core_universe` | **1211 股**（真台股老兵）/ 10 panels / 14 features |

## 八、SSOT 對齊

- 治權：原則精華 #1 #10 + 憲章第三部 universe 段（無變更）
- code：[`src/augur/universe/core_gate.py`](../src/augur/universe/core_gate.py)（本次改、加候選空間關）
- 上游依賴：[`features/panel.py`](../src/augur/features/panel.py) compute_features 14 features（既有）
- 演進記錄：本檔 = 三輪實證 SSOT；下次跑 F3 model 應引用本檔之 1211 核心股實證
