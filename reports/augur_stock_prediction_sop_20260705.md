# augur 股市預測系統整體做法 SOP（端到端可執行版）

**🎯 白話**：這份是把 augur「怎麼做股市預測」從資料到上線串成一條**可照序執行、每步有門檻、每步能防三敵人**的作業手冊。augur 不是神諭，是**橫斷面相對強弱顧問（long-only top-decile）**——只給排序＋機率＋可信度，人決策、不下單、不動錢。目前手上是一個**溫和的真邊際**（B2_ridge long-only top10%/equal，扣 0.585% 來回成本後 net Sharpe 1.23、CAGR +19.2%、勝率 78%，vs 等權基準 net Sharpe 0.94 / +14.8%，21 非重疊 panel、h=60、as-of purged walk-forward），本 SOP 的全部工作就是**用機器閘持續檢驗這個小贏是真的、可重跑、非自欺**，而不是把它吹成必勝。凡本檔標「待建缺口」者＝經實測 repo 現在確實沒有、不佯稱已存在。

**守原則 #1（source-pure 零假資料）#8（anti-leakage 零偷看未來）#15（誠實零自我欺騙）**

**日期**：2026-07-05 ｜ **性質**：系統層做法 SOP（半衰期隨工具演進更新）｜ **位階**：靈魂 `docs/系統核心思想_v1.4.0.md` → `docs/原則精華_v1.7.1.md` → 憲章 `docs/系統架構大憲章_v1.25.0.md` → 特徵法 `reports/augur_feature_discovery_methodology_20260626.md` §四。本檔為**操作串接**，判準衝突一律以上述 SSOT 為準。

---

## 0. 定位與誠實前提

### 0.1 augur 是什麼、不是什麼

- **是**：橫斷面相對強弱排序顧問——對一組 as-of 核心宇宙，輸出「哪些股相對強」的排序＋可信度＋逐字引文。成功定義（靈魂）＝**可溯源 × out-of-sample 撐住 × 半年重跑一致 × 有真經濟價值（非 IC）**。
- **不是**：不是神諭（不測大盤方向/時機/點位）、不是自動駕駛（系統建議、人決策）、不是下單機器人（不動錢）。

### 0.2 headline 錨點的誠實揭露（吸收紅隊 blocker：錨點選擇偏誤）

本 SOP 反覆引用的 **net Sharpe 1.23 不是一個乾淨數字，是一條選擇路徑的終點**。它是 `run_economic_eval.py` 迴圈印出 12 個組態（`top_frac ∈ {.1,.2,.3}` × `{equal, pred}` × `{B2_ridge, M1_gbdt}`）後，由人「看 net 挑最佳」得到的**極值**——選擇偏誤已內建於錨點。因此：

1. **凡引用 1.23 當比較基準的段落，一律加註「12 選 1 之後、多重比較 deflation 之前、單 seed、僅比例成本口徑」**（下游 D3 的試驗數 N 必須 ≥ 這 12，不得只算 D3 當次新試的）。
2. **headline 分位/加權的選擇本身尚未走 out-of-sample**（現況在同一 21-panel 全樣本上挑最佳 net）。目標口徑（見 §3.3）：用前段折選 `top_frac`/加權、對後段折凍結再報。在此改造完成前，1.23 一律標「in-sample 選出的組態」。
3. 這是「溫和真邊際、非造神諭」在統計上的第一道自律：**我們知道 1.23 被選擇偏誤抬高，SOP 的存在就是把它扣回真值**。

### 0.3 可證偽紀律（本 SOP 的靈魂）

每個 headline 結論都事前登記「什麼結果會推翻它」（降級 D1–D6）與「什麼結果讓它變硬」（升級 U1–U5），做成 §4 的例行檢查表。北極星自檢＝寫任何結論前問「**這是真兆還是假兆？**」（真實 API 源①／決策當下真看得到②／out-of-sample 撐住③，三個都「是」才寫）。

### 0.4 三敵人（貫穿全檔零容忍）

① 假資料（imputed/zero-fill/placeholder/推估）｜② 偷看未來（用 as-of≤t 尚未公開的資訊）｜③ 自我欺騙（把打算做的當成果、單次極值當定論、報喜不報憂、多試幾次總有一次好看）。**三敵人不是試錯對象**——試的是方法與參數，不是資料真假。

---

## 1. 現狀 → 目標藍圖（端到端）

```
[FinMind/FRED API]
   │  ingestion/{finmind,fred}.py（限速三層防護：_pace / _quota_gate / QUOTA_COOLDOWN）
   ▼
(1) RAW  84 表全市場全史 as-of 2026-05-31   ✅已定案
   │  daily_maintenance.py（by-date 日頻增量，✅已建）+ reconcile_audit.py（DB↔API 對帳）
   │  ⚠缺：cron 排程自動化、as-of 前推決策層拍板
   ▼
(2) FEATURE  feature_values(panel_date, stock_id, feature, value)  35 特徵   ✅已建
   │  features/{panel,chip,valuation,concentration,phase,margin_cycle,release_lag}.py
   │  source-pure（算不出即缺列）+ release-lag gate（#8）+ recency gate(45d)
   │  ⚠缺：imputed 稽核、統一 as-of 口徑登記、FRED vintage 接線、release-lag 回歸測試
   ▼
(3) UNIVERSE  core_universe_asof（point-in-time、消 survivorship）   ✅已建
   │  universe/core_gate.py（純完整度 gate，無評分）
   │  ⚠缺：headline gate 參數決策層釘死、survivorship 覆蓋率自檢
   ▼
(4) MODEL  evaluation/baseline.py:run_ladder（B0/B1/B2_ridge/M1_gbdt 內嵌 fit-predict）   ⚠半成品
   │  無 models/ 生產 package、無 artifact 持久化
   ▼
(5) WALK-FORWARD  walkforward.py（expanding + purge + embargo）+ metrics.py（rank IC + HAC-t）  ✅已建
   ▼
(6) ECONOMIC  portfolio.py:run_backtest + run_economic_eval.py（net Sharpe/Calmar，比例成本 0.585%）  ✅已建
   │  ⚠缺：多 seed 彙總、deflated Sharpe、風格歸因、真實衝擊/容量成本、可成交性 gate、風控上限
   ▼
━━━━━━━━━━━━━━━ ✂ 最大生產斷點：(6)→(7) 之間無「凍結預測快照 writer」 ━━━━━━━━━━━━━━━
   ▼
(7) SERVING/ADVISOR  advisor/{advise,guard,payload,answer}.py   ✅消費端已建、上線
   │  唯讀 payload + 機械 guard 鏈（數字白名單/引文子集/未來洩漏 regex/誠實閉集）
   │  ⚠缺：生產快照 writer（現吃 example_payload 示範資料）、前瞻追蹤 ledger、kill-switch、監看面板
```

**一句話目標**：把已驗證的一次 as-of 邊際，**安全地凍結（快照）→ 如實揭露（guard）→ 持續監看衰減（前瞻 ledger）→ 假兆現形時果斷降級（kill-switch）**——並在此之前，先用「現在就能查、最可能翻案」的現查支線（D2/D3/D4）把 1.23 扣到真值。

---

## 2. 分階段路線圖（Phase 化）

> **排序原則（吸收紅隊 feasibility blocker：優先序倒置）**：把「**現在就能查、最可能翻案**」的 D2 風格歸因、D4 成本敏感度、D3 deflation 排最前（可用現有 21 panel + `feature_values` 立即回頭現查，是最可能推翻 1.23 的三項）；D1 真前瞻需 6–8 個 h=60 panel 兌現＝約 1.5–2 真實年才出第一判定，改為**背景長線項**、不佔第一批關鍵路徑。

### 缺口依賴拓撲（關鍵路徑，吸收紅隊 feasibility major：依賴不清）

```
獨立可平行的現查支線（不依賴 P-1，第一批）：
   D4-比例（現成 --cost 掃描）──┐
   D2 風格歸因（attribution.py）─┼─→ 立即扣 1.23 到真值
   D3 deflated Sharpe（+試驗ledger）┘

生產骨架關鍵路徑（背景鋪設）：
   P-1 快照 writer ──→ P-2 前瞻 ledger ──→ {D1 前瞻判定, P-5 監看面板, P-9 kill-switch}
                                              （判定順延 1.5–2 年）
```

### Phase 0 — 凍結 headline 口徑（隱性前置，吸收紅隊 feasibility major：拍板成阻塞）
- **目標**：決策層一次性凍結 headline 口徑（as-of 日、liquidity-pct、核心規模、model、h、top_frac、加權），寫入 `core_universe_build_meta` provenance。
- **里程碑**：一組拍板參數入憲；所有下游封存/追蹤/降級 ledger 的比較基準固定，不再浮動。
- **退場條件**：拍板前**不啟動**任何封存/前瞻/降級 ledger（否則在流沙上蓋樓）。

### Phase A — 現查支線（現成工具即可跑，數天～數週）
- **目標**：用現有工具對 1.23 做最可能翻案的三項現查。
- **里程碑**：
  1. **D4-比例成本掃描**（現成 `run_economic_eval.py --cost` 迴圈 `{.00585,.008,.010,.012,.015}`）→ 找盈虧平衡成本、標破口點（數天）。
  2. **D2 風格歸因**（新建 `evaluation/attribution.py`）→ 對現有 21 panel 剝 beta 看純 α（數週）。
  3. **D3 deflated Sharpe**（新建 `metrics.deflated_sharpe` + 試驗計數 ledger）→ 對 headline 立即扣多重比較血。
- **退場條件**：任一項使 headline 降級（α 被 beta 解釋 / deflated 後不顯著 / 保守成本吃掉邊際）→ headline 立即改標「探索中、不對外」。

### Phase B — 生產骨架（背景鋪設，關鍵路徑）
- **目標**：補 (6)→(7) 斷點，讓 serving 吃真實預測。
- **里程碑**：P-1 快照 writer + 表 → P-2 前瞻追蹤 ledger → P-9 kill-switch 狀態機 → P-5 監看面板。
- **退場條件**：P-1/P-2 建成前，serving 只能標「示範態」；前瞻機制**須有 as-of 之後的真實 raw 增量到位**才能運轉（見 §7 待辦：資料凍結＝前瞻空轉風險）。

### Phase C — 補完降級關與樣本
- **目標**：D2/D3/D4 全部程式化並納例行；補 h=20 增 panel 數提升 D3/regime 統計效力。
- **里程碑**：`run_regime_breakdown.py`（U3 分段，非既有 regime 擇時器）、`evaluation/impact_cost.py`（D4 衝擊，視 ADV 資料可得性）、可成交性/風控上限模組。
- **退場條件**：任一模組上線後**重跑 `run_economic_eval` 驗證 net 仍優於基準**（風控上限會犧牲集中收益，須確認邊際仍在）。

---

## 3. 七軸 SOP

每軸格式：**step → gate 門檻 → 真實工具 → 待建缺口 → 防三敵**。

### 軸一 · 資料（防 D6 假資料 / D5 偷看未來）

| 項 | 內容 |
|---|---|
| **step** | ①取數前最小單位探測（單股單日 ~1 列，#25）確認 IP 健康→②放量走 `full_market_sync.py`（全史）或 `daily_maintenance.py`（by-date 日頻增量），一律經 `finmind.py` 內建防護、不自寫 fetch→③sync 後跑 `reconcile_audit.py` 逐表 DB↔API byte 對帳→④source-pure 落 `feature_values`（`build_feature_panel.py` 冪等 ON CONFLICT） |
| **gate** | 限速 `MIN_INTERVAL=0.9s`（實驗值、重啟讀錶驗 #27）；額度一律問 `/user_info` 錶不本地推算；403→`QUOTA_COOLDOWN=1800s` 停不硬衝；對帳 attestation `value_mismatch=0 ∧ extra_in_db=0`（精華 #7）；recency `MAX_STALE_CALENDAR_DAYS=45`（超過即缺列） |
| **工具** | `ingestion/{finmind,fred,sync}.py`、`scripts/{full_market_sync,daily_maintenance,sync_macro,reconcile_audit,build_feature_panel}.py`、`core/generic_schema.py` |
| **待建缺口** | ①**增量 cron 排程**（`daily_maintenance.py` 已能跑，但**未自動化排程**——需一支配額感知 wrapper，且 **as-of 前推屬決策層拍板**）；②imputed/source-purity 偵測稽核（`verify_hygiene/units` 未涵蓋，且須與既有 `reexam_sparse_candidates.py` 的 audit-impute 口徑**區隔**——後者僅供公平比較不入庫）；③對帳 attestation ledger 落表 |
| **防三敵** | ①取數唯一經 `finmind.py`、值皆 API 可 trace；缺列鐵律不 zero-fill。②洩漏防線**下推到 feature 層 gate**，ingestion 只落 raw 不做 as-of 判斷。③撞 403 不謊稱「短測過了」（2026-06-09 假信心教訓）；未過對帳不報完成 |

> **釐清（吸收紅隊 completeness minor：catalog 增量空白）**：raw 增量**不是「只有全史重跑」**——`daily_maintenance.py` 已提供 by-date 日頻增量（`ingestion.sync` + `audit.reconcile`），`build_catalog.py`/`refresh_knowledge_pipeline.py` 另管 catalog/知識層。真正缺的是「**排程自動化**（cron/watchdog）與 as-of 定案日的決策層前推」，非增量能力本身。

### 軸二 · 特徵（防三敵，SSOT＝方法論 §四）

| 項 | 內容 |
|---|---|
| **step** | ①探索（`run_field_correlation.py`/`run_lens_correlation.py`）→②立候選寫 `feature_candidate_values`（**與生產表隔離**）→③四道漏斗（見 gate）→④提拔屬決策層拍板→加入 `features/*` + 重建→⑤實驗完 `clear_candidates` 清列 |
| **gate（四道漏斗，任一不過即止）** | **漏斗1 紀律閘**：source-pure ∧ anti-leakage ∧ 不硬編切點（禁 0.80/0.20、decile、康波 40-60 年）；**漏斗2 五鏡**（`run_feature_audit.py --asof --loo`）：有號IC/共線群/LOO/SHAP/purged-CV 合看，「SHAP≈0 且 ablation-safe」必移；**漏斗3 out-of-sample**（`run_ladder`）：as-of purged walk-forward IC 撐住、半年重跑一致；**漏斗4 提拔關卡**（`verify_candidate_promotion.py --h 20,60 --seeds 3`）：as-of 口徑 ∧ **`|HAC-t|≥2`** ∧ 多 seed 增量 `Δ>0` 且跨 seed 穩定 |
| **工具** | `scripts/{run_field_correlation,run_lens_correlation,validate_feature_candidates,run_feature_audit,verify_candidate_promotion,scan_coverage,verify_stability,reexam_sparse_candidates}.py`、`audit/{feature_candidate,feature_diagnostics}.py`、`metrics.py:effective_t_hac` |
| **待建缺口** | ①**候選＋淘汰登記帳本**（結構化表，取代散落報告；狀態 exploring/in_funnel/promoted/rejected + reason + source_ref + **覆蓋率必填欄**）；②`verify_candidate_promotion` 的 `--candidates` 參數化（現 `CANDS` 硬寫）；③`check_feature_coverage`（覆蓋率低於門檻擋提拔）；④**`monitor_feature_drift`**（生產特徵分布漂移 + IC 衰變 + sign-flip 警示，repo **無此工具**）；⑤`verify_*` 候選審查引擎收斂為單一參數化工具（#29c） |
| **防三敵** | ①候選走 source-pure 缺列、候選表隔離、驗後清列不回流。②`--asof` 綁 `core_universe_asof`、embargo 剔 test label 窗、發布日 gate。③五鏡合判杜絕單看 gain；淘汰理由必寫帳本（source-traceable） |

> **audit-impute 迂迴污染防線（吸收紅隊 blocker：假資料的結論入決策）**：`reexam_sparse_candidates.py` 對稀疏候選補中位「翻案」時，**補值 Δ 只能用於排除冤殺、不能用於證明有增量**。翻案須**同時報生產（缺列不補）口徑的實際覆蓋率與 Δ**；覆蓋率須 ≥ 決策層拍板下限（對齊現有 35 特徵覆蓋分布），否則即使補值 `Δ>+0.002` 也**不提拔**——因為它入生產後就是靠半個宇宙撐 IC。覆蓋率列為登記帳本必填欄。

### 軸三 · 建模（防三敵，SSOT＝`evaluation/`）

| 項 | 內容 |
|---|---|
| **step** | ①一律跑完整階梯 `run_ladder(asof=True, seed=...)`：B0_random→B1_momentum→B2_ridge→M1_gbdt（**禁跳階直接報最強**）→②讀每階 `{mean_ic, effective_t_hac, hit_rate, n_panels}`→③裁決：必贏 B0、再贏 B1；GBDT 不贏 Ridge → **選 Ridge**（越簡單越不易過擬） |
| **gate** | 上 GBDT 門檻：`M1.mean_ic − B2.mean_ic > 0` 且**多 seed 方向一致**；顯著性**唯一合法口徑＝HAC-t**，`|effective_t_hac|≥2`（**禁裸用 iid `effective_t`**，重疊窗高估 G8）；`n<3` 或 `LRV≤0`→`None`（判「不足以下結論」，不得用 iid 頂替）；**超參固定保守值**（Ridge alpha=1.0；LGBM n_est=200/lr=.05/leaves=15）**不在 test 折調參**（結構性杜絕 test 回流） |
| **工具** | `evaluation/{baseline,walkforward,metrics,label,cross_section}.py`、`scripts/{run_evaluation,verify_candidate_promotion}.py` |
| **待建缺口** | ①**`src/augur/models/` 生產 package 不存在**（`ls` 確認 No such file）——模型只活在 eval 內嵌 fit-predict；②**多 seed 經濟彙總器**（`run_economic_eval.py` **無 `--seeds`**，經濟指標結構上單 seed——見下方修正）；③raw-vs-purged 雙口徑輸出（現標「待 M-2」）；④巢狀 inner-CV（僅在要調參時）；⑤ensemble 組合器（僅在證明正增量時） |
| **防三敵** | ①模型只吃 source-pure `feature_values`，`_panel_matrix` 要求全 feats 齊。②階梯全走 `asof=True`。③強制跑完 B0/B1、GBDT 不贏 Ridge 就誠實選 Ridge |

> **多 seed 誠實修正（吸收紅隊 completeness/feasibility major：臆造既有能力）**：`run_economic_eval.py` 的 argparse **只有 `--since/--h/--cost/--interactions`，無 `--seeds`、無 seed 迴圈**（實測 grep 零命中）。多 seed 只在 `run_evaluation.py`（**IC 層**）與 `run_ladder`/`verify_candidate_promotion` 可用。**經濟 headline（net Sharpe 1.23）目前結構上是單 seed**，U4「net Sharpe ≥3 seed 取 min/median/max/mean」**現成工具跑不出來**——列為**待建外層彙總器**（迴圈多 seed `run_backtest` → 聚 min/median/max/mean），非現成。在建成前 headline 經濟指標須誠實標「單 seed、未過 U4」。
>
> **確定性模型多 seed 空轉（吸收紅隊 minor）**：headline 是 **B2_ridge（確定性、無隨機）**，對它跑「3 seed」得 3 個相同數字（min=median=max），**不得作為 U4 通過依據**。Ridge headline 的 U4 穩健須改測**其他隨機/選擇來源**（top_frac 選擇、宇宙 gate 參數擾動、子期 bootstrap）；多 seed 只對 GBDT/ensemble 有意義。

### 軸四 · 驗證（walk-forward 骨架，防 D5）

| 項 | 內容 |
|---|---|
| **step** | ①一律用 `walkforward.splits(panel_dates, h)`（`embargo=None`→自動 `embargo_panels_for`）產折，**禁別處手寫切分**（#12 切分唯一住此）→②label `label.forward_returns` **t+1 進場**、還原價 log return、橫斷面 rank→③IC `metrics.rank_ic` + `summarize` + `effective_t_hac`→④經濟回測挑非重疊 panel |
| **gate** | expanding + purge：train＝test 之前、剔最近 embargo 個 panel；`embargo ≥ ceil(h/panel間距)` 且 ≥1；折有效性：train<50 跳折、共同股<5 跳折；`H=252` purge 後獨立觀測少→標**探索性** |
| **工具** | `evaluation/{walkforward,label,metrics}.py`、`scripts/run_evaluation.py` |
| **待建缺口** | ①raw-vs-purged 雙口徑對照輸出（揭露 purge 縮水幅度）；②**`_nonoverlap` 精確化**（見下方修正） |
| **防三敵** | ②本軸即 #8 紅線機器實作（expanding+purge+embargo+t+1+asof 五重）。③雙口徑強制暴露不 purge 虛高多少。①切分層純索引邏輯無從引入幻值 |

> **`_nonoverlap` heuristic 修正（吸收紅隊 major：偷看未來殘留）**：`run_economic_eval._nonoverlap` 用 `need = h*1.45*0.9` 把交易日換算日曆日挑非重疊 panel。`1.45` 是粗略係數，遇農曆新年長假/颱風假會偏離真實交易日密度；若某段真實交易日跨度 < h，兩個被判「非重疊」的 panel label 窗其實重疊、forward return 被**雙計**→Sharpe 與前瞻超額系統性高估（HAC 也修不乾淨殘留重疊）。**修**：改為用 `full_calendar` 精確數 h 個交易日的實際日期位移（已在庫），消 1.45 近似；並補一支稽核逐對驗證相鄰「非重疊」panel 的 label 持有窗確實不相交（用交易日曆）——列為 **D5 例行機器檢查一項**。前瞻 ledger 結算亦須用同一精確窗。

### 軸五 · 投組（防三敵，SSOT＝`portfolio.py`）

| 項 | 內容 |
|---|---|
| **step** | ①as-of 宇宙（`_asof_stocks`，point-in-time 含下市股）→②t+1 進場、非重疊再平衡→③`argsort(pred)` 降序取 `top_frac` 分位、`equal`/`pred` 加權、**long-only**（空方 Track D 已證無效）→④成本 gate→⑤可成交性 gate→⑥風控上限→⑦凍結快照 |
| **gate** | 有效股<10 跳過該 panel；`top_frac` 掃 `{.1,.2,.3}` **以 net（非 gross）選最佳**；**D4 通過**：`portfolio_net` 之 Sharpe **且** Calmar > `benchmark_net`（成本套換手率、基準亦計宇宙換手以公平比） |
| **工具** | `evaluation/portfolio.py:run_backtest`（`top_frac`/`weight`/`long_short`/`seed`）、`scripts/run_economic_eval.py`（`COST_TW=0.00585`/`_nonoverlap`/top 掃描）、`evaluation/{baseline,label}.py` |
| **待建缺口** | ①**衝擊/容量成本模型** `evaluation/impact_cost.py`（現僅固定比例，D4 衝擊部分答不了）；②**可成交性 gate** `evaluation/tradability.py`（漲跌停/停牌，現假設每檔皆能 t+1 成交）；③**風控上限** `evaluation/allocation.py`（單股/產業上限，現僅 equal/pred 無 cap）；④`_turnover` 計入權重變動（現僅算成分進出，pred 加權再平衡成本被低估） |
| **防三敵** | ②as-of + t+1 + 非重疊。③以 net 非 gross 選分位、多 seed（僅 GBDT）；風控上限防集中度自欺。①衝擊模型 k 須真實成交校準、禁臆造 |

> **成本樂觀修正（吸收紅隊 major：成本/容量偏樂觀）**：在 `impact_cost` 模組上線前，任何「net Sharpe > 基準 = 可交易」結論**一律加註「僅比例成本口徑、對小型股/大額偏樂觀、未過 D4 衝擊關」**，不得作為對外 headline。D4 成本網格上界**不憑空乘 2**——應由 top-decile 實際 ADV 分布反推「若按 √(部位/ADV) 衝擊、此組合在 X 資金規模的隱含成本」，讓成本 source-traceable。
>
> **可成交性 gate 可執行化（吸收紅隊 minor：不可執行）**：漲停判定須**資料驅動**——以 `TaiwanStockPrice` 前收計算當日理論漲停價（考慮 2015 前後 7%/10% 制度變遷、興櫃/新股例外），比對 t+1 high/close 是否觸及且成交量 < 個股近 20 日中位 X%（X 待拍板）；不用硬編「+9.9%」近似。此為 `tradability` 模組落地時才能精確實作，SOP 不給無法執行的近似口徑。

### 軸六 · serving（防三敵，消費端已建）

| 項 | 內容 |
|---|---|
| **step** | ①凍結 as-of 預測快照（**與 walk-forward 同一 pipeline**，禁另寫生產專用平行預測碼）→②快照組 `PredictionPayload`（數字帶 `source_ref`）→③advisor 唯一出口 `advise()`：檢索⊕唯讀payload⊕lexicon→prompt→llm_fn→**機械 guard 鏈**→④過期 payload 拒答 |
| **gate** | 凍結一致性：快照 `feature_panel_version`/`universe_build_id` 可反查 `core_universe_build_meta` 同組拍板參數；**guard 硬 gate**（全過才放行）：數字∈`payload.numbers()` 白名單／引號⊂檢索原文／`_FUTURE_LEAK`&`_REVERSE` regex 攔／檢索空→三級誠實閉集；隔離 gate：advisor↔evaluation import 圖零邊（AST） |
| **工具** | `advisor/{advise,guard,payload,answer,prompt,oai_compat}.py`、`scripts/{serve_advisor_openai,serve_chat_ui,serve_admin_console}.py` |
| **待建缺口** | ①**生產預測快照 writer**（現 `PredictionPayload` 只有 `example_payload()` 示範資料、無生產 writer——最大斷點）；②前瞻追蹤 ledger；③serving 契約靜態檢查（AST 掃無旁路繞過 `advise()`）；④**紅隊問句集 + guard 回歸測試**（`verify_advisor_guard.py`，凍結誘導下單/誘導擇時/誘導引用不存在數字之 case，通過率門檻 100%）；⑤kill-switch 狀態機；⑥唯讀監看面板 |
| **防三敵** | ①guard 數字白名單=機械攔幻覺數字。②`_FUTURE_LEAK` regex + payload as_of 凍結 + 過期拒答。③guard 是**機械防線非 prompt 自律**；檢索空即誠實閉集 |

### 軸七 · 治理（防三敵 + 資本紀律）

| 項 | 內容 |
|---|---|
| **step** | ①每任務啟動過**決策層閘表**（命中即停待拍板）→②未命中屬執行層 AI 自駕、做完呈過目→③混合任務切兩段（#28 裁決句：搞錯會沉默污染下游→理解軸窮盡；僅慢→執行軸省） |
| **gate（決策層閘表，永遠人拍板）** | as-of 定案日變更／universe gate 參數／特徵升降級最終裁定／真兆最終確認／資本紀律參數／commit-push-PR／API 放量／破壞性操作／資料真假定義（三敵人零容忍非試錯對象） |
| **工具** | 治權檔（靈魂/精華/憲章/CLAUDE.md）、`reconcile_audit.py`、`verify_{stability,hygiene,units}.py`、`portfolio.py`（MaxDD/Calmar 事後指標） |
| **待建缺口** | ①`docs/治理決策層閘表.md`（決策 vs 執行閉集清單）；②資本紀律模組（部位上限/產業曝險/滾動 MaxDD 停損觸發器——`portfolio.py` 現皆無，僅事後 MaxDD）；③`verify_headline_signal.py`（真兆確認 checklist 執行體）；④封存 ledger + `verify_forward_tracking.py`（依賴尚未建的快照 writer） |
| **防三敵** | 分界本身防③（逐出「我以為可自己決定」灰色地帶）；資料真假明列決策層零容忍防「為推進自我授權放鬆口徑」 |

> **資本紀律誠實**：回撤停損**非自動平倉**（顧問不動錢）——滾動 MaxDD 超閾只觸發「降級檢視」（回真兆確認 + D1 崩塌檢查）。在部位上限/產業曝險/衝擊成本模組建成前，SOP 誠實標「**資本紀律為半成品、部位建議須人工套上限**」，不佯稱有完整風控。

---

## 4. 反自欺驗證軸（D1–D6 / U1–U5 例行檢查表）

> **例行節奏（吸收紅隊 minor：節奏與 panel 頻率錯配）**：headline 再平衡是**季度**（h=60，21 panel≈季度），故 D1 前瞻結算**對齊季度兌現週期**，非月度空轉。**月度輕檢**只保留每日/每月真有新輸入者：D5/D6 洩漏假資料機器守門 + 限速額度讀錶。**U4 改為「每次重跑/變更時觸發」**，非固定月度。**每次特徵/模型變更即觸發**：D3 + U4 + 收尾經濟關。

**⚠ 未建關空轉警示（吸收紅隊 major：降級 gate 自證循環）**：下表凡標 🔴**未建**者，**目前空轉、headline 尚未過此關**。只要有任一降級關處於未建狀態，headline **一律只能標「探索中/未過完整降級關」，不得對外稱「已通過可證偽登記全套」**。此狀態行為每次 SOP 輸出必附，不藏於附註。

| 檢查 | 觸發**降級**門檻 | 觸發**升級**門檻 | 主要工具 | 狀態 |
|---|---|---|---|---|
| **D1/U1 真前瞻** | 盲測 6+ 批超額中位≤0 或勝率<50% | 未來 6–8 panel 超額>0 且 HAC-t≥2 | 新 `prediction_ledger` + `portfolio.run_backtest` | 🔴未建 |
| **D2/U2 風格歸因** | 中性後 α HAC-t<2 或 α≤0 | 中性後 α HAC-t≥2 且>0 | 新 `evaluation/attribution.py` + `effective_t_hac` | 🔴未建（Phase A 首批） |
| **D3 deflated Sharpe** | PSR<0.95（校正後不顯著）**[探索性]** | PSR≥0.95 且 deflated>0 | 新 `metrics.deflated_sharpe` + 試驗 ledger | 🔴未建（Phase A 首批） |
| **D4 成本敏感度** | 保守成本(1.0–1.2%)下 net≤基準 | 盈虧平衡成本≥現值 2 倍 | **現成** `run_economic_eval --cost`（比例）+ 掃描 wrapper；衝擊模型未建 | 🟡比例部分現成 |
| **U3 cross-regime** | 某主 regime 顯著負/集中單段>70% | 每 regime 方向一致正 | 新 `run_regime_breakdown.py`（**非**既有 `verify_regime_*`） | 🔴未建 |
| **U4 多 seed** | seed 間 sign 翻轉/全距跨0 | ≥3 seed 一致、中位 HAC-t≥2 | IC 層 **現成** `run_evaluation --seeds`；經濟層彙總器未建 | 🟡IC 現成、經濟未建 |
| **U5 機制審** | 頂級特徵講不通/方向相反 | 機制方向性預測未被推翻 | `run_feature_audit` + 機制登記（人審） | 🟡半人審 |
| **D5 洩漏** | 再現任一偷看未來口徑洞（含 `_nonoverlap` 重疊、release-lag 晚報股） | — | `walkforward`/`build_universe_asof`/`release_lag` + 新 nonoverlap 稽核 | 🟢機器化（`_nonoverlap` 稽核待補） |
| **D6 假資料** | 任一非 point-in-time/補值/audit-impute 迂迴入決策 | — | `core_gate` completeness + source-pure | 🟢機器化 |

**降級後動作（統一）**：headline 立即改標「探索中／僅特定條件有效／不對外顧問」；advisor 因 AST 零 import 隔離不受污染，但 `PredictionPayload.validation` 欄須反映降級狀態。**升級須 ≥2 個 U 條同時滿足才動 headline 位階**（單條升級不足以造神諭）。**D5/D6 坐實→自動置紅（零容忍不緩衝）**；D1–D4 降級→降黃 + 具體警語。kill-switch 亦可人手動拉閘（決策層）。

**樣本量誠實閘（吸收紅隊 major：空中樓閣）**：經濟回測僅 **21 個非重疊 panel**（h=60）。在此樣本上：(a) Deflated/Probabilistic Sharpe 對 21 obs 估偏度/峰度**極不穩**、PSR≥0.95 硬門檻過度敏感；(b) 再按 regime 切 4 子期→每子期 ~5 panel，`effective_t_hac` 內建 `n<3→None`、5 obs 的 HAC-t 無意義。故 **D3/U3 一律標「探索性、不下強結論」**（比照 H=252 處理）；D3 不用硬 PSR<0.95 一刀切，改「DSR 顯著下滑即列警示」；**補 h=20 增 panel 數**作為 D3/regime 統計效力前置。

**試驗數 N 機械化（吸收紅隊 blocker：N 靠自報）**：D3 的核心輸入「有效試驗數 N」**不得靠人/AI 自報**（跨 session 幾乎必然低報，與「guard 是機械防線非自律」第一原則矛盾）。**修**：凡呼叫 `run_ladder`/`run_backtest`/`verify_candidate_promotion` 者一律經 wrapper，把 `(model,top,weight,seed,feats_hash,cost,as_of)` 每組態 **append-only 落 `trial_ledger`**（與 §2 候選登記帳本合一）；**N 由 DB query 該表得出、不由人填**。DSR 取 N 只接受 ledger query 值；人手填 N 一律視為未驗證、不放行 headline。ledger 建成前 D3 標「尚不可信、暫用保守上調門檻」，不佯稱可跑。

**風格因子循環性（吸收紅隊 minor：D2 口徑）**：D2 用生產特徵當 factor-mimicking 剝 beta 存在共線循環（用同一批 valuation/momentum 構造風格因子去解釋用同批特徵訓練的模型超額，會把真 α 也吸進「風格 beta」）。**修**：風格因子盡量用**與 headline 訓練特徵正交/獨立來源**的標準學術風格（純市值分組、純產業中性），並**同時報「獨立因子」與「生產特徵因子」兩種 α** 揭露口徑敏感度，不單報一個 α 就下 D2 結論。此關屬理解軸，須決策層審口徑。

---

## 5. 三敵人防線總表（一表對應每道機器閘）

| 敵人 | 定義 | 機器閘（工具:常數/函式） | 治權條 |
|---|---|---|---|
| **①假資料** | imputed/zero-fill/placeholder/推估 | source-pure 缺列鐵律（`panel.py`：算不出即缺列，無 NULL 佔位）｜recency gate（`MAX_STALE_CALENDAR_DAYS=45`）｜completeness gate（`core_gate.py`）｜DB↔API attestation（`reconcile_audit.py`：`value_mismatch=0 ∧ extra_in_db=0`）｜guard 數字白名單（`payload.numbers()`）｜audit-impute 不入生產決策（覆蓋率必填） | 精華 #1 |
| **②偷看未來** | 用 as-of≤t 尚未公開資訊 | 發布日 gate（`release_lag.py`：`REVENUE_DAY=15`/`FIN_LAG_QUARTER=45`/`FIN_LAG_ANNUAL=90`）｜t+1 進場（`label.py`）｜purge+embargo（`walkforward.py:splits/embargo_panels_for`）｜as-of 名單消 survivorship（`build_universe_asof`→`core_universe_asof`）｜FRED vintage｜`_nonoverlap` 精確交易日窗（待修）｜`_FUTURE_LEAK` regex（`guard.py`） | 精華 #8 |
| **③自我欺騙** | 打算當成果/單次極值/多試幾次總有一次好看 | HAC-t（`metrics.effective_t_hac`：`|t|≥2`、禁裸 iid、`n<3→None`）｜多 seed ≥3（僅隨機模型）｜deflated Sharpe + 試驗 ledger（待建）｜風格歸因剝 beta（待建）｜net 非 gross 選分位｜經濟價值非 IC（`run_economic_eval`）｜真前瞻 ledger（待建）｜guard 機械防線非自律｜報 min/median/max/mean 揭全距 | 精華 #15/#19 |

> **release-lag 晚報股殘留（吸收紅隊 major：#8 命門殘留）**：`revenue_release_date` 回硬編「公告月 15 日」近似全市場真實公告日，對 10–15 日之間才公告、或 15 日後補公告的公司仍是偷看未來（gate 判 True 但當下未公開）。D3 稽核（2026-07-04）修的是「方向錯一個月」的粗誤，未解此殘留。**修**：(1) 若 FinMind 月營收帶真實公告日/發布時戳欄，改用真實公告日 gate；(2) 若確無，buffer 放大到涵蓋歷史最晚公告分位（95/99 分位延遲天數）並標「15 日為近似、對晚報公司有殘留 look-ahead」，**不宣稱已完全消除 D5**；(3) 補 vintage/快照稽核抽驗歷史上是否存在「營收在其 release_date 當日 panel 尚無法從當時 API 快照取得」的案例。

---

## 6. 工具鏈對映（真實檔案，絕對路徑）

**已建可直接用（非缺口，實讀確認）**：
- 資料：`src/augur/ingestion/{finmind,fred,sync}.py`、`scripts/{full_market_sync,daily_maintenance,sync_macro,reconcile_audit,build_feature_panel,build_core_universe}.py`、`src/augur/core/generic_schema.py`
- 特徵：`src/augur/features/{panel,chip,valuation,concentration,phase,margin_cycle,release_lag}.py`、`src/augur/audit/{feature_candidate,feature_diagnostics,field_correlation}.py`、`scripts/{run_field_correlation,run_lens_correlation,validate_feature_candidates,run_feature_audit,scan_coverage,verify_stability,verify_hygiene,verify_units,reexam_sparse_candidates,verify_candidate_promotion}.py`
- 宇宙：`src/augur/universe/core_gate.py`（`build_universe_asof`→`core_universe_asof`、`core_universe_build_meta`）
- 建模/驗證：`src/augur/evaluation/{baseline,walkforward,metrics,label,cross_section}.py`（`run_ladder`／`splits`+`embargo_panels_for`／`rank_ic`+`summarize`+**`effective_t_hac`**（Newey-West/Bartlett、`|t|≥2`、`n<3`或`LRV≤0`→None、lag=`floor(4·(n/100)^(2/9))`）／`forward_returns`）、`scripts/{run_evaluation,verify_candidate_promotion}.py`
- 經濟：`src/augur/evaluation/portfolio.py`（`run_backtest`/`_turnover`/`_metrics`）、`scripts/run_economic_eval.py`（`COST_TW=0.00585`/`_nonoverlap`）
- serving：`src/augur/advisor/{advise,guard,payload,answer,prompt,oai_compat}.py`、`scripts/{serve_advisor_openai,serve_chat_ui,serve_admin_console}.py`

**工具語意校正（勿誤用）**：
- `run_economic_eval.py` **無 `--seeds`**（只 `--since/--h/--cost/--interactions`）——經濟指標多 seed 須新建外層彙總器。
- `verify_regime_portfolio.py`/`verify_regime_timing.py` **是 C1 商業指標 regime 擇時疊加**（regime-on 持投組、off 持現金），**不是** headline 依市場 regime 分段的 alpha breakdown——U3 須新建 `run_regime_breakdown.py`。
- `daily_maintenance.py` **已提供 by-date 日頻增量**——缺的是排程自動化，非增量能力。

---

## 7. 待建缺口與優先序

| 缺口 | 為何需要 | 優先 | 工作量 | 對映 |
|---|---|---|---|---|
| Phase 0 headline 口徑凍結（決策層拍板 + `core_universe_build_meta`） | 所有下游比較基準的地基，未凍結=流沙蓋樓 | **P0 前置** | 決策層拍板 | 全案 |
| `trial_ledger` 試驗計數（與候選登記帳本合一，自動 append） | D3 的 N 機械化、防低報自欺（不靠人報） | **P1** | 小-中 | D3/§2 |
| `evaluation/attribution.py` 風格歸因 | 現查最可能翻案：賺的是不是 beta（現無任何風格回歸） | **P1** | 中 | D2/U2 |
| `metrics.deflated_sharpe` + PSR | 對 1.23 立即扣多重比較血（現無系統級 deflation） | **P1** | 中 | D3 |
| `scan_cost_sensitivity.py`（wrapper 迴圈 `--cost`） | 現查最快：比例成本會否吃邊際（工具現成、數天） | **P1** | 小 | D4 |
| `_nonoverlap` 精確交易日窗 + 重疊稽核 | 消 1.45 近似的雙計高估（Sharpe/前瞻皆依賴） | **P1** | 小 | D5 |
| P-1 生產預測快照 writer + 不可變表 | (6)→(7) 最大斷點，serving 現吃 example_payload | **P2** | 中 | 軸六 |
| P-2 前瞻追蹤 ledger + 結算腳本 | D1/U1 載體（連帶解生產預測斷點） | **P2** | 中 | D1/U1 |
| release-lag 真實公告日 gate + 回歸測試 | 晚報股殘留 look-ahead（現硬編 15 日近似） | **P2** | 中 | D5 |
| 多 seed 經濟彙總器（迴圈 `run_backtest`） | U4 經濟指標（`run_economic_eval` 無 seed） | **P2** | 小 | U4 |
| `check_feature_coverage` + `monitor_feature_drift` | 覆蓋假象擋提拔 + 生產特徵漂移（現無） | **P2** | 中 | 軸二 |
| `run_regime_breakdown.py`（動態分位分段） | U3 分段（既有 regime 腳本是擇時器、口徑不符） | **P3** | 中 | U3 |
| `evaluation/{impact_cost,tradability,allocation}.py` | D4 衝擊/可成交性/風控上限（視 ADV 資料可得性） | **P3** | 大 | D4/軸五 |
| `verify_advisor_guard.py` 紅隊回歸 + serving 契約 AST 檢查 | guard 上線前 100% 攔截驗收 | **P3** | 小-中 | 軸六 |
| `docs/治理決策層閘表.md` + `verify_headline_signal.py` | 決策清單閉集 + 真兆確認 checklist 執行體 | **P3** | 小 | 軸七 |
| 增量 cron 排程 wrapper（配額感知） | `daily_maintenance` 已建、須自動化 + as-of 前推拍板 | **P3** | 小 | 軸一 |

> **前瞻空轉風險（吸收紅隊 minor：有機制無燃料）**：D1/U1 前瞻結算**須有 as_of 之後的真實 raw 增量到位**。現 as-of 凍結於 2026-05-31、增量未排程，若長期不推進，前瞻 ledger **無新 forward return 可結算、U1 永遠湊不齊**——「前瞻驗證」看似最抗自欺卻因上游凍結而空轉。**修**：把「raw 增量落後於今日 > N 日」列為**降級/告警條件**（資料陳舊=前瞻機制失效）；增量排程建成前誠實標「前瞻追蹤目前無法運轉、U1 不可主張」。

---

## 8. 風險與「不做什麼」

### 禁項閉集（紅線清單，違反即停）

| 禁項 | 判準 | 治權條 |
|---|---|---|
| 不下單、不動錢、不替用戶執行交易 | 顧問只給排序/機率/可信度 | 靈魂 |
| 不測大盤方向/時機/點位（不造神諭承諾） | 橫斷面相對強弱，非擇時神諭 | 靈魂 |
| 不 zero-fill / 不補值 / 不 placeholder | 算不出即缺列 | 精華 #1 |
| 不裸報 raw IC / 不裸用 iid effective_t | 須 as-of + `|HAC-t|≥2` | 精華 #8、CLAUDE #11 |
| 不拿 audit-impute 結論證明有增量（只可排除冤殺） | 補值不入生產決策，須生產口徑實測 | 精華 #1 |
| 不 hand-patch 已 committed 資料/凍結快照 | 改 writer + 重建 | CLAUDE #12 |
| 不 hardcode 特定值（0.80/0.20、decile、康波 40-60 年、情緒字典切點） | 動態分位/連續泛函 | 精華 #9 |
| 不移植 stock_backend code/資料/數字/設定 | clean-room 只依 5 治權檔+schema+live API | 精華 #16、CLAUDE #17 |
| 不拿單次極值當定論 / 不報喜不報憂 | ≥3 seed（僅隨機模型）、誠實揭露 | 精華 #15 |
| 不把三敵人當試錯對象 | 試方法/參數，不試資料真假 | 精華 #19 |
| 不自 commit/push/建關 PR、不 API 放量 | 明示授權；限速受控 dry-run 除外 | CLAUDE #14/#24 |
| **不宣稱「已過可證偽全套」當任一降級關未建** | D2/D3/D4 未建即空轉，headline 只能標探索中 | 本 SOP §4 |

### 已知風險（修不進 SOP、明列不藏）

1. **錨點選擇偏誤未根除**：1.23 是 12 選 1 極值；even after D3 deflation，分位/加權選擇本身尚未走 out-of-sample（§0.2、§3.3）。在 top_frac 選擇改 walk-forward 折凍結前，此偏誤僅被揭露、未消除。
2. **樣本天花板**：21 非重疊 panel 使 D3 deflated Sharpe 與 regime 分段在現況下**只能是探索性**，補 h=20 增 panel 前不能當硬降級閘。
3. **成本口徑偏樂觀**：固定比例 0.585% 對小型股/大額系統性低估真實衝擊；`impact_cost` 未建前「可交易」結論一律加註「未過 D4 衝擊關」。
4. **release-lag 晚報股殘留 look-ahead**：硬編 15 日近似無法涵蓋全市場真實公告日分布，對晚報公司有殘留 D5，未宣稱完全消除。
5. **前瞻機制依賴資料推進**：as-of 凍結 + 增量未排程時，D1/U1 前瞻 ledger 空轉（有機制無燃料）。
6. **生產斷點**：`models/` package 不存在、無快照 writer，serving 現吃示範資料；P-1/P-2 建成前「serving/監看 alpha 衰減」是示範態。
7. **審查者自報後門**：試驗數 N、機制解釋、gate 參數在 `trial_ledger`/獨立因子/決策層拍板機械化之前，仍部分依賴被稽核者自報——與「機械防線非自律」原則有殘留張力。

**收束精神**：溫和真邊際、非造神諭。headline 1.23 是「扣比例成本仍小贏」的溫和邊際；本 SOP 每道 gate 都在確保這個小贏是真的、可重跑、非自欺——**寧可少賺、不可自欺；寧報探索中、不報必勝**。

---

## 附錄 D：新增表 schema（DDL）與對應 Python〔治權要求：計畫須明確寫 schema＋Python〕

§7 點名之三張新表，其完整 DDL 與對應 Python 明列於此（欄型/約束對齊 RBAC 計畫嚴謹度；DDL 住遷移器、非散落；GENERATED ALWAYS AS IDENTITY、timestamptz DEFAULT now() 對齊既有慣例）。**皆設計交付、尚未在 DB 執行**（拍板前 #19）。

### D.1 `trial_ledger` — 試驗計數帳本（D3 有效試驗數 N 機械化）

```sql
CREATE TABLE IF NOT EXISTS trial_ledger (
    trial_id    bigint       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    as_of       date         NOT NULL,          -- 該次回測之 as-of 凍結點
    model       varchar(32)  NOT NULL,          -- 'B2_ridge' / 'M1_gbdt' …
    top_frac    numeric(5,4) NOT NULL,          -- top 分位 (0.10/0.20/0.30)
    weight      varchar(16)  NOT NULL,          -- 'equal' / 'pred'
    seed        integer,                         -- 隨機模型 seed；確定性模型 NULL
    feats_hash  char(64)     NOT NULL,          -- 特徵集 sha256（同集去重）
    cost        numeric(6,5) NOT NULL,          -- 來回成本
    horizon     integer      NOT NULL,          -- 預測期 H
    net_sharpe  numeric(8,4),                    -- 該組態結果（供 DSR 取極值分布）
    created_at  timestamptz  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_trial_ledger_config ON trial_ledger (model, feats_hash, cost, horizon);
-- append-only（禁 UPDATE/DELETE）；有效試驗數 N = count(DISTINCT (model,top_frac,weight,feats_hash,cost,horizon))
```
- **建/寫**：`src/augur/evaluation/trial_ledger.py:record_trial(cfg)`（wrapper——凡呼叫 `run_ladder`/`run_backtest`/`verify_candidate_promotion` 者一律經此 append-only 落帳）；DDL 住 `scripts/migrate_eval_ledger_ddl.py`（沿用 `migrate_text_understanding_ddl.py:ensure_constraint()` 之 `pg_constraint` 冪等 guard 慣例）。
- **讀/用**：`src/augur/evaluation/metrics.py:deflated_sharpe(sharpe, n)`——N 由 `SELECT count(DISTINCT …) FROM trial_ledger` 得出、**不由人填**（吸收紅隊「N 自報後門」§8-7）。

### D.2 `prediction_ledger` — 生產預測不可變快照 ＋ 前瞻結算（P-1/P-2、D1/U1 載體）

```sql
CREATE TABLE IF NOT EXISTS prediction_ledger (
    pred_id     bigint        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    as_of       date          NOT NULL,          -- 預測時點（凍結、不可變）
    model       varchar(32)   NOT NULL,
    horizon     integer       NOT NULL,
    symbol      varchar(16)   NOT NULL,
    rank        integer       NOT NULL,          -- 橫斷面排名
    score       numeric(10,6) NOT NULL,          -- 模型分數（可溯源 #1）
    source_ref  text          NOT NULL,          -- trace 回真實模型 run
    made_at     timestamptz   NOT NULL DEFAULT now(),
    fwd_return  numeric(12,6),                    -- 前瞻結算（P-2 事後回填；未結算 NULL）
    settled_at  timestamptz,
    CONSTRAINT uq_pred UNIQUE (as_of, model, horizon, symbol)
);
CREATE INDEX IF NOT EXISTS idx_pred_asof ON prediction_ledger (as_of, model, horizon);
```
- **寫（P-1）**：`scripts/write_prediction_snapshot.py`——as-of 凍結、寫後不可變（改 writer 重建、禁 hand-patch #12）。
- **結算（P-2）**：`scripts/settle_prediction_ledger.py`——`as_of + H` 之真實 raw 到位才回填 `fwd_return`（無燃料不結算，誠實標「前瞻無法運轉、U1 不可主張」§8-5）。
- **讀/用**：`src/augur/evaluation/forward_test.py`——D1/U1 未來超額中位/勝率/HAC-t。

### D.3 `core_universe_build_meta` — Phase 0 headline 口徑凍結（防流沙蓋樓）

```sql
CREATE TABLE IF NOT EXISTS core_universe_build_meta (
    build_id     bigint       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    as_of        date         NOT NULL,          -- 凍結之 as-of
    horizon      integer      NOT NULL,          -- headline H
    cost         numeric(6,5) NOT NULL,          -- headline 成本口徑
    panel_def    jsonb        NOT NULL,          -- 非重疊 panel 定義（起點/步長/交易日窗）
    universe_def jsonb        NOT NULL,          -- 核心股 gate 定義
    n_panels     integer      NOT NULL,
    frozen_by    varchar(16)  NOT NULL,          -- 決策層拍板者
    frozen_at    timestamptz  NOT NULL DEFAULT now(),
    note         text
);
```
- **寫**：`scripts/freeze_headline_config.py`——Phase 0 決策層拍板後凍結一次（as-of/H/成本/panel/universe gate）。
- **讀/用**：`src/augur/evaluation/run_economic_eval.py` 與 `portfolio.py`——所有下游比較讀同一凍結口徑（單一比較地基 #12，防「流沙蓋樓」§7-P0）。

> **其餘新 Python（無新表、純計算/驗證程式）**：§7 之 `attribution.py`／`scan_cost_sensitivity.py`／`impact_cost.py`／`tradability.py`／`allocation.py`／`run_regime_breakdown.py`／`verify_advisor_guard.py`／`check_feature_coverage`／`monitor_feature_drift` 皆不產生資料表——結果落既有 `feature_values`／報表／上述三帳本。`metrics.deflated_sharpe`＝`metrics.py` 內新函式（無新表）。
