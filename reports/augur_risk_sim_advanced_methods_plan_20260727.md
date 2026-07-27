# 風險模擬進階三法計畫——③copula-t／EVT／跨市場類比（預註冊凍結）

> **性質**：[I] 計畫（#20；hugo 2026-07-27 拍板「把③copula/DCC＋EVT＋跨市場類比三個包成一份計畫段」）。
> **紀律同②**：方法白名單 migration、參數與窗**本檔 commit 即凍結**（不得因結果回改；要改＝新名另註冊）、**episode 重放（台股）主結論地位不動**、analog 強制標示。
> **資料實查（2026-07-27）**：US 1928-02～（11,677 檔、2008-10 月 3,021 檔/日）；UK 1968-01～（1,815 檔/日@2008-10）；JP 僅 1999-05～ → **日本 1990 泡沫崩資料不可及、誠實排除**。

## 層級聲明（新增「類比層」，主結論不挪）

```
主結論   episode 重放(台股 6 窗)              ← 地位不動
類比層   episode_analog_*(他市場真實路徑)     ← 新;輸出硬綁「analog:非台股歷史」標示
參考層   bootstrap 四法 + copula_t_garch + evt_pot_hybrid
```

## M1｜跨市場類比 episode（六窗凍結；先做——零參數估計、最對齊誠實哲學）

**機制**：取類比市場窗內**等權跨檔日報酬**（當日有價全股等權、日再平衡、橫斷面 winsorize 1%/99%）＝「當時當地一個等權分散組合的實際路徑」，對本組合整體重放。**不做個股映射**（映射任意性＝自我欺騙）。

| method（白名單名） | 窗 | 危機錨 |
|---|---|---|
| `episode_analog_us1929` | 1929-09-01 → 1932-07-31 | 大蕭條全段（最極端歷史壓力） |
| `episode_analog_us1973` | 1973-01-01 → 1974-12-31 | 石油危機熊市 |
| `episode_analog_us1987` | 1987-08-01 → 1987-12-31 | 黑色星期一 |
| `episode_analog_us2000` | 2000-03-01 → 2002-10-31 | dot-com 完整熊市（台股版覆蓋拒答、美版補上） |
| `episode_analog_us2008` | 2008-09-01 → 2009-03-31 | **校準錨**：與台股 2008 重放（-37.9%）對照＝類比法失真度的量尺 |
| `episode_analog_uk1973` | 1973-01-01 → 1975-01-31 | 英國史上最深熊市 |

**誠實閘**：日覆蓋 <100 檔 → 該窗拒答（1929 年代可能觸發＝合法結果）；倖存者偏誤（來源含否下市股未證實）硬綁揭露欄；輸出/summary 一律帶 `analog` 字樣＋「非台股歷史、等權市場路徑、組合視同 β=1 承受」三句。

## M2｜EVT 極值理論（`evt_pot_hybrid`；參數凍結）

**機制**：組合日報酬（756td 窗）左尾 POT——門檻 u＝經驗 5% 分位；GPD MLE（scipy `genpareto`）；**混合重抽**＝主體經驗分布＋尾部 GPD（iid）→ 10,000×h60 路徑 → MaxDD 分布。
**凍結參數**：u=5%｜n_paths=10,000｜h=60｜seed=42｜shape ξ 之 95% CI 以 200 次 refit bootstrap 附報。
**誠實閘**：尾部樣本 n_tail<20 → 拒答；揭露「結構假設同 iid（僅尾部校正）——時序相依請看 block/stationary 與 episode」。

## M3｜Copula-t＋GARCH 邊際（`copula_t_garch`；參數凍結；最重、最後做）

**機制**：33 檔各配 GARCH(1,1)-t 邊際（`arch`，已入 venv）→ 標準化殘差 Pearson 相關 ＋ t-copula 自由度 MLE（格點 3..30）→ 模擬聯合路徑 10,000×h60 → 等權聚合 → MaxDD 分布。**補的洞＝相關性趨一**：bootstrap 整列重抽鎖死當日相關結構，模不出相關性惡化路徑；t-copula 的尾部相依係數一併揭露。
**凍結參數**：窗 756td｜GARCH(1,1)-t｜dof 格點 3..30｜n_paths=10,000｜seed=42。
**誠實閘**：任一邊際不收斂 → 剔除該股並揭露；存活 <25/33 → 整法拒答。**不做 DCC**（手刻 ~百行估計碼＝實作錯誤風險 > 增量價值；無成熟維護套件前不碰——列復活條件）。

## Schema／程式（v1.39.0）

- **零新表**；`migrate_mc_method_check_ddl.py` 白名單 12→**20 值**（+2 法+6 類比；typo 仍擋）。
- `scripts/simulate_portfolio_risk.py`：`ANALOG_EPISODES` dict（窗值逐字＝本檔）＋市場表映射（US/UK Price 表）＋`_analog_market_path()`／`_evt_engine()`／`_copula_engine()`；CLI 增 `--analog <名>`／`--method evt|copula`；各引擎 `--selftest` 純紅綠（合成資料驗數學：GPD 擬合還原已知 ξ、copula 還原已知相關、winsorize 邊界）。
- 揭露欄：沿用 `mc_simulation_run.detail` JSONB（analog 三句/ξ CI/邊際存活數/尾部相依係數）。

## 分階段・驗收・停損（執行序 M1→M2→M3）

| 階段 | 驗收（精準） | 停損 |
|---|---|---|
| E0 白名單+窗凍結 | constraint def 實查 20 值；本檔 commit 即窗凍 | — |
| E1 M1 類比六窗 | 各窗落庫或誠實拒答；`us2008` 與台股 2008 對照差寫入 detail（校準錨） | 覆蓋閘觸發＝合法 |
| E2 M2 EVT | ξ＋95% CI 落庫；n_tail 揭露；selftest 還原合成 ξ 誤差<10% | n_tail<20 拒答 |
| E3 M3 copula | 邊際存活數/dof/尾部相依落庫；selftest 還原合成相關誤差<0.05 | 邊際收斂失敗>25% → 停手報告不硬出 |

**回滾**：全部為新增 method 之新列（append-only）；不動既有 run、不動主結論層。
