# augur_portfolio_risk_sim_plan_20260725 — 組合層前瞻風險模擬（A 軌縮版）＋CPCV/PBO 不做決定（B 軌）

> **性質**：#20 計畫書；三視角對抗審查完畢（誠實鎖×機械可行×反方，3 agents／242k tokens／機械鏡含 live DB 實查與 runtime 實測）。**結論：A 軌經反方瘦身後 GO（等你終核）、B 軌 NO-GO（條件觸發後再議）**。
> v1.39.0：(a) **零新表**——複用 `mc_simulation_run`（欄：run_id/target_id/horizon_td/method/n_paths/seed/git_sha/summary jsonb/is_simulation CHECK true）；讀 `prediction_values`（panel_date/model_id/stock_id/in_portfolio/weight）、`TaiwanStockPriceAdj`、`risk_policy`（dd_circuit 閾值）。(b) 程式：一支新 CLI `scripts/simulate_portfolio_risk.py`（函式與簽名見 §三）。

## 一、審查發現表（摘錄；全文 JSON 於 workflow 留檔）

| # | 鏡 | 級 | 發現 → 處置 |
|---|---|---|---|
| 1 | 機械+反方 | blocker | 「165 檔投組」實為 **5 個 horizon 模型×各 33 檔等權**（distinct 52 檔）——照原設計會模擬權重和=5.0 的無意義混血投組 → **改：單一部署 cell `RankRidge_H60`（33 檔）**，逐 cell 可另跑 |
| 2 | 反方 | major | 固定權重下「日期聯合重抽」**數學上≡對聚合後投組日報酬單序列做既有 bootstrap**——新引擎＋新表是重造（#3/#12）→ **改：聚合成單序列、複用 `simulate_mc_paths` 引擎與 `mc_simulation_run` 表**（`target_id='PORT_RankRidge_H60_<panel>'`；scripts 互 import 有 revalidate←migrate_trial_ledger 先例） |
| 3 | 反方 | major | **756td 窗偏差＝安心感假兆**：窗內（≈2023-07 起）無 -20% 級聯合回檔 → bootstrap 機械回報 P≈0，是窗的性質非安全證據 → **改：episode 確定性重放（2008/2020/2022）為主結論、bootstrap 分布退居參考**；summary 硬印窗內實際最深回檔錨＋窗偏差 caveat |
| 4 | 機械 | major | 熔斷閾值 -10%/-15% 不存在——`risk_policy` 實值 **H60=-0.20／H120=-0.25**（reduce_half）→ 閾值經 `risk_control.load_policies()` 讀表（#29b），額外分位標「資訊性」 |
| 5 | 誠實鎖 | major×6 | 全採加嚴：P(MaxDD<閾) 逐項硬綁「模擬統計非預測、非熔斷預告、與方向軸/risk_control 實際判定分欄永不混排」；閾值單向唯讀（模擬不回寫不觸發）；as-of 機械綁權重 panel_date 入 run_id；缺值禁 0 填（共同覆蓋窗＋剔除日數揭露＋<252td fail-closed 拒跑）；`in_portfolio`＝**候選組合**非部署（predict_asof 明文）；episode 綁覆蓋率＋存活者偏誤＋「單一情境非機率」三揭露；固定權重無風控 overlay＝保守口徑須明標 |
| 6 | 資料 | info | PriceAdj 覆蓋實測良好：H60 33 檔僅 1 檔缺 7 天（共同日交集即可、零補值）；episode 全員有價（51/52 檔有 2008 史＝倖存者視角、已入揭露） |

## 二、B 軌（CPCV/PBO）NO-GO 決定與復活條件

三鏡合力擊倒：①**#8 衝突**（CPCV 固有「未來組訓練」牴觸 expanding 鐵律，至多降純診斷）②**統計效力真空**（混頻 panel＋122td purge → 每條 OOS 路徑僅 ~7-8 點，16 配置 rank 近噪音，PBO 無法區分 0.2 與 0.5）③**反成危險品**（trial_ledger 16 族 ≪ 真實搜尋史 → N 系統性低估 → 偏低 PBO 會變成對沖 DSR 判決的翻案素材——誠實機器最不該自產可被樂觀誤讀的數字）④機械面 `run_backtest` 無折注入參數＋feats_hash 是標籤非雜湊（重跑實測 1.1881 vs ledger 1.2654 對不上）。
**復活條件（預註冊、不寫 code）**：季頻 panel 累積使 H60 非重疊 OOS 期 ≥60 且 `run_backtest` 已因他案增加折注入時，再以「CPCV(N,2)-PBO 變體」誠實命名重議；屆時 PBO 仍為診斷、永不對沖 DSR。

## 三、A 軌縮版實作規畫

**`scripts/simulate_portfolio_risk.py`**（#18/#29 全矩陣＋selftest）：
- `_load_cell_portfolio(conn, cell='RankRidge_H60', panel=None) -> (panel_date, [(sid, w)])`：讀 prediction_values 單 cell in_portfolio 33 檔；權重和斷言=1
- `_aggregate_returns(conn, members, panel_date, window_td=756) -> (series, effective_td, dropped_dates)`：PriceAdj 共同覆蓋日交集聚合；<252td fail-closed
- 重抽：`from simulate_mc_paths import` 既有 iid/block 引擎（單序列）；episode 模式＝確定性視窗重放（2008-09~2009-03／2020-01~2020-04／2022 全年）
- `_summarize()`：h 日累積報酬分位＋MaxDD 分布（複用 `portfolio.drawdown_series`）＋P(MaxDD<policy 閾)＋窗內實際 MaxDD 錨＋§一#5 全部硬綁 note → 寫 `mc_simulation_run`（`target_id='PORT_<cell>_<panel>'`）
- `--selftest` 零 DB：聚合數學、MaxDD 與 drawdown_series 一致性、缺值剔除不變式、note 欄全存在紅綠鎖
- 執行矩陣：無參數=現況唯讀／`--run [--cell RankRidge_H60] [--episode 2008|2020|2022|all] [--n-paths 10000 --seed 42]`

**驗收**：selftest 全綠；凍結 panel（2026-05-31）實跑一輪（bootstrap＋三 episode）；summary 逐 note 欄 grep 驗在；chat payload 白名單零擴（不入對話）。**runtime**：單序列 bootstrap 秒級、全套 <5 分鐘、本地零 usage。

## 四、成本與定位（誠實）

縮版後＝一支薄 script、零新表、零治權變更、<半天工。它補的是「前瞻觸發機率分布＋歷史情境重放」這塊真缺席（既有 verify_risk_overlay 只有歷史單一路徑）；但依 #3 誠實標定：**主結論是 episode 重放，bootstrap 是參考**——模擬給的從來不是預測，是「地板要防的原始風險長什麼樣」。
