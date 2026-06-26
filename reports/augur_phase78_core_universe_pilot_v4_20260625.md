# augur PHASE 7+8 核心股 pilot v4 — volatility 對停牌 robust + conditional gate 月營收豁免金融（742→875）

**日期**：2026-06-25（v3 同期、兩個 gate 正確性修正）
**性質**：實證報告（#15：數字皆 source-traceable，出自 rebuild stdout + DB query）。
**承前**：v3（[`augur_phase78_core_universe_pilot_v3_20260625.md`](augur_phase78_core_universe_pilot_v3_20260625.md)）— 742 真精英（28 panel × 19 連續特徵 + 流動性 P25）。
**觸發**：742 代表權值股核驗發現 **2/10 不在**（鴻海 2317、富邦金 2881）→ 逐股查根因 → 兩個 gate 正確性 bug。
**結論**：兩修正後核心 **742 → 875**，**代表權值股 10/10 全納入**；揭露 volatility 對停牌的敏感性誤排除 ~126 股。

---

## 一、兩個 gate 正確性修正

### 修正 1：volatility 對停牌 robust（[`features/panel.py`](../src/augur/features/panel.py)）

**根因**（實證）：鴻海 2317 在 panel 2025-09-30 缺 `volatility_60d` → 查得 **2025-07-30 close=0**（DB=API 全 0、真停牌、source-pure），致 `log(0/前)=-inf`、`log(後/0)=+inf`；`ret.notna()` **擋不住 inf**（62/60 過門檻），但 `std` 含 inf → 被末端 `isfinite` 濾掉 → 缺列。**1 天停牌就讓整個 volatility 算不出**。

**正解**：volatility 改用「最近 w 個 **finite** 報酬」之 std：
```python
fin_ret = ret[np.isfinite(ret)]          # 剔停牌致之 ±inf/nan
for w in (20, 60):
    if len(fin_ret) >= w:
        out[f"volatility_{w}d"] = fin_ret.iloc[-w:].std()
```
對停牌 robust（往前補足）、**無 magic number**（不引入容忍比例、不違 #9）、無停牌股行為不變。

### 修正 2：conditional gate 月營收豁免金融（[`universe/core_gate.py`](../src/augur/universe/core_gate.py)）

**根因**（實證）：富邦金 2881 等金融股缺 `monthly_revenue_yoy` → **金融保險業無月營收申報制度**（靠財報），卻被放進「所有股必齊」的完整度 gate → 結構性誤排除金融股（金融保險 70 檔僅 46 有月營收）。

**正解**：`build_universe` 加 `conditional={feature: (豁免產業,)}` 參數——月營收對 `金融保險` 豁免完整度要求（非金融仍要求）。向後相容（不傳則行為不變）。

---

## 二、完整收縮鏈（實證）

| 階段 | 核心股 | 觸發 |
|---|---:|---|
| v3 walk-forward（28 panel × 19 連續特徵 + 流動性 P25）| 742 | pan-historical 完整度 |
| + conditional gate（月營收豁免金融保險）| 745 | +金融股（富邦金等）|
| **+ volatility robust（finite 報酬）** | **875** | **+~126 偶發停牌股（鴻海等）** |

→ 兩修正後 **875 核心股**（28 panel × 19 features、流動性閾值 14.742、全重算 236min）。

## 三、兩修正效果拆解

| 修正 | 納入 | 代表 |
|---|---:|---|
| conditional gate | +7 | 富邦金 2881、中信金 2891（金融保險 26→33）|
| **volatility robust** | **+~126** | 鴻海 2317 及眾多偶發停牌大股 |

## 四、重要發現（#20 實證價值）

**volatility 對停牌的敏感性影響極廣**——不只鴻海，**~126 股**因 28 panel 中**某一天偶發停牌**（台股處置/減資/變更交易方法/股東會等常見）就被 `volatility_60d` 算不出而誤排除。此 latent bug 唯有實跑 walk-forward + 逐股查根因才現形。對映「算不出即缺列」的雙面性：對 P 類單日特徵正確，對**窗口特徵**（volatility）卻因 1 點停牌誤殺整窗 → 須對窗口內少量無效值 robust。

## 五、代表權值股核驗（實證 875 內，10/10）

✅ 台積電 2330 · 聯發科 2454 · **鴻海 2317** · 台達電 2308 · 中華電 2412 · **富邦金 2881** · 國泰金 2882 · 中信金 2891 · 統一 1216 · 中鋼 2002

（v3 為 8/10；兩修正後鴻海、富邦金納入 → 10/10。污染殘留 0、非數字代碼 0。）

## 六、DB 狀態（as-of report 時點）

| 表 | 內容 |
|---|---|
| `feature_values` | 28 panels（2014-2025 年度+季度 + as-of 2026-05-31）/ 3096 股 / 22 features（volatility 全重算）|
| `core_universe` | **875 股** / 28 panels / 19 連續特徵（兩修正）|

## 七、SSOT 對齊

- 治權：原則精華 #1 #9 #10 #20 + 憲章第三部 universe/feature 段（無變更、屬執行層正確性修正）。
- code：[`features/panel.py`](../src/augur/features/panel.py)（volatility finite 報酬）+ [`universe/core_gate.py`](../src/augur/universe/core_gate.py)（conditional gate）；commit `1a8fe01`、tag `gate-fixes-20260625`。
- 上游：v3 [`augur_phase78_core_universe_pilot_v3_20260625.md`](augur_phase78_core_universe_pilot_v3_20260625.md)（742 籌碼 + P/E 教訓）。
- 下游：F2c 估值 + F3 M-0/M-1/M-2 evaluation（另機並行、基於本修正 commit `1a8fe01` → `08cfda0`，as-of Ridge H60 rank IC+0.132）。
- 演進記錄：本檔 v4 = 兩 gate 正確性修正 SSOT；DB 成果（875）跨機獨立、不入 git。

## 八、待辦 / 後續

- volatility 修正後 875 為 **pan-historical 單名單**；F3 嚴格 walk-forward 已改用 `build_universe_asof`（point-in-time、消 survivorship #8、另機 08cfda0 加入）。
- 順帶發現未改（#3 最小邊界）：`lending_fee_rate_mean_30d` 命名「30d」但 SQL 為 `LIMIT 100`（最近 100 筆借券、不限 30 日）——窗口語意待修。
- ETN/DR/受益證券等類證券商品目前被月營收 gate 意外排除（結果對：非個股對象，但宜由候選空間關處理、非月營收 gate）。
