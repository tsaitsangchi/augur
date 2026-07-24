# PME 擴大假說／map 覆蓋計畫 [I]（2026-07-24）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；憲章第六部計畫完整性 v1.39.0）— **不創設 [N] 義務**
* **授權觸發**：Steward「**開擴大假說／map 覆蓋計畫**」＝plan-first ✅；拍板＋「**開 MAP-E012**」＝S0–S2 已開（S3／S4／U 另令）
* **閉合目標**：在 **零 FinMind／FRED**、維持 **P2H／AUTO-B** 紀律下，擴大 `principle_factor_map` 覆蓋與**可過 G-PROM／G-ECON 雙綠**之路徑，使 prodset `active`／熱路徑 `n_feats` 能**誠實成長**（現況再晉升後仍僅 2）
* **前置**：PME ✅ `PME-Efull-yes`（機械完備）；PRODSET／S4／SOUL CLOSED；P2H S123＋U DONE（熱路徑真讀 prodset）；本地再晉升 run6＋重訓（`audits/PME-LOCAL-REPROMOTE-20260724.md`／`PME-REPROMOTE-RETRAIN-20260724.md`）— **active／n_feats 未擴大**
* **範式**：`reports/augur_prodset_predict_hotpath_plan_20260724.md`／`reports/augur_roadmap_r5_plan_20260724.md`／`reports/augur_roadmap_r6_plan_20260724.md`
* **硬邊界**：FZ-keep；不改 [N]；≠可交易／≠確立級；≠偷放寬閘；≠以解凍補 Dividend 當主路徑；≠ AI 造原則／假說入庫；AUTO-B 七閘全綠才 APPLY

### Steward 已拍板（2026-07-24）

| 欄 | 內容 |
|---|---|
| **日期** | 2026-07-24 |
| **狀態** | ✅ **已拍板**＋✅ **MAP-E012 CLOSED**（S0＋S1＋S2；S3／S4／U 另令） |
| **四碼** | `MAP-P-yes` ＋ `MAP-E012` ＋ `FZ-keep` ＋ `GATE-keep`（已採納） |
| **效力** | 計畫＝執行藍圖；近程授權＝S0–S2（庫內可建）；執行令＝「開 MAP-E012」 |
| **解凍邊界** | **擴大 map ≠ 解凍 API**（FZ-keep）；Dividend／blocked_div 另帳（見 §5） |
| **GATE 邊界** | GATE-keep：不降閾；ECON-only 不晉升；SKIP≠PASS；本輪不跑閘 |
| **留痕** | `audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md`；執行 CLOSED＝`audits/PME-MAP-E012-CLOSED-20260724.md` |

---

## 0. 一句結論

再晉升／重訓已證明：**同一 mapped 集合下雙綠仍僅 2**——擴大 `n_feats` 的瓶頸不在熱路徑 wiring，而在 **假說↔特徵覆蓋不足＋既有 mapped 多數不過 G-PROM 三關**。本計畫以 **人＋文獻策展**擴大／精煉 `principle_factor_map`，只對**庫內可算**特徵建值，再跑 local-gates／APPLY／重訓；**誠實預期：多數候選仍可能不過閘**，成功＝可追溯路徑＋零假綠，非保證全綠。

---

## 1. What／Why／非目標

### 1.1 What

| 義務 | 現況（2026-07-24 live／run_id=6） | 本計畫目標 |
|---|---|---|
| 覆蓋快照 | **mapped=17**／**missing=5**／**blocked_div=1**（`evolution_coverage_snapshot`；distinct feature） | S0 診斷帳＋S1 策展後覆蓋**可解釋成長**（新 map／可建特徵） |
| `principle_factor_map` | **42** 列／**23** distinct feature（含 5 missing＋1 blocked） | 擴大**有文獻依據**之 map；禁 AI 造列 |
| G-PROM（42 map 列） | **PASS=2／FAIL=34／SKIP=6** | 不降閾；靠新／精煉假說＋庫內可建特徵爭取**真雙綠** |
| G-ECON（42 map 列） | **PASS=15／FAIL=21／SKIP=6** | 維持 #14；ECON-only **不得**晉升 |
| 雙綠→APPLY | 僅 `inst_cumflow_position_120d`、`volume_gini_60d` | 若有新雙綠→AUTO-B APPLY→prodset active 誠實↑ |
| 熱路徑 | P2H 真讀 prodset；**n_feats=2** | S4 僅在 active 變動後重訓；FC-empty 不變 |

### 1.2 Why

* `PME-REPROMOTE-RETRAIN` 明示：擴大 n_feats 需 **新假說／map 覆蓋**或資料洞補齊——**非**再跑同一閘可解。
* Gap：**G-PME-PROM／G-PME-ECON＝partial**（`reports/augur_pme_gap_ledger_20260724.md`）；**G-PME-COV＝none**（覆蓋可重跑）≠ 覆蓋已「夠」。
* 靈魂↔raw（`.cursor/rules/soul-vs-raw-correlation.mdc`）：升格路徑＝raw **交互**抽象出的**概念／可證偽假說**→map→特徵→閘；**不是**整庫 raw、**不是** API 解凍。
* 預測↔API（`.cursor/rules/predict-vs-market-api.mdc`）：庫內 as-of 可訓／推估；本計畫主路徑**零市場 API**。

### 1.3 明確非目標

| 非目標 | 理由 |
|---|---|
| ≠解凍 FinMind／FRED 當主路徑 | FZ-keep；補 Dividend **另帳**，不得寫成擴大 map 的前置 |
| ≠偷放寬 G-PROM／G-ECON 閾值 | AUTO-B／GATE-keep；降閾＝假綠 |
| ≠可交易／≠確立級 | `direction_gate.evaluated_pass` 門二未過；prodset≠門二 |
| ≠ AI 造原則／假說／citation 入庫 | 憲章 philosophy：禁 `ai_generated`；策展＝人＋可溯源文獻 |
| ≠ runtime 原則文本加權 | 熱路徑只吃 prodset 特徵名；隔離 FORBIDDEN 不變 |
| ≠自動下單 | G-NOEXEC |
| ≠改 [N]／MC 條文 | [I] 計畫＋執行層 |
| ≠把 ECON-only 當可晉升 | 七閘 AND；見 §2.2 |
| ≠保證多數特徵變綠 | 誠實預期見 §8 |

### 1.4 零 API／庫內 as-of（必須）

| 不變式 | 含義 |
|---|---|
| 本計畫實作／驗收**零依賴**市場 API | 不呼叫 FinMind／FRED；不因缺增量 sync 阻塞 |
| 特徵建值僅用庫內已落地 raw | as-of／anti-leakage（#8）；算不出→缺列（#1） |
| Dividend／blocked_div | 標 **blocked**／另帳；**不**標 validated；解凍前不重驗股息族完備 |
| 凍結維持 ≠ 否決本計畫 | 擴大 map／庫內可建特徵／再閘／重訓皆可在 FZ-keep 下進行 |

---

## 2. 診斷（為何卡在 2）

> 數字來源：live DB `evolution_coverage_snapshot`／`promotion_queue` **run_id=6**（2026-07-24；與 `PME-LOCAL-REPROMOTE` 一致）。

### 2.1 覆蓋三桶（distinct feature）

| coverage_class | n | 成員 |
|---|---|---|
| **mapped** | **17** | `cycle_position_252d`、`days_since_high_252d`、`foreign_holding_pct`、`gross_margin_pctile`、`inst_cumflow_position_120d`、`institutional_net_buy_ratio_20d`、`market_cap_log`、`momentum_{60,120,252}d`、`monthly_revenue_yoy`、`pb_ratio`、`pe_ratio`、`price_to_10yr`、`range_position_120d`、`volatility_60d`、`volume_gini_60d` |
| **missing** | **5** | `debt_ratio`、`macro_regime`、`peg_ratio`、`piotroski_fscore`、`roe` |
| **blocked_div** | **1** | `dividend_yield`（G-DIV-1／FZ-keep；有 `feature_values` 仍 **不得**當完備重驗） |

另：`feature_values` 全庫 **35** distinct；其中 **17** 已在 map 且非 blocked／missing 路徑可用；**另 17** 已在庫、**尚未**任何 `principle_factor_map` 列——S1 策展的主彈藥（見 §3 S1）。

### 2.2 為何 34 FAIL（map 列級）

閘按 **map 列**（42）裁決，非按 distinct feature：

| G-PROM＼G-ECON | PASS | FAIL | SKIP |
|---|---|---|---|
| **PASS** | **2** | 0 | 0 |
| **FAIL** | **13** | **21** | 0 |
| **SKIP** | 0 | 0 | **6** |

* **SKIP=6**：5×`missing`＋1×`blocked_div`——**誠實不評**（≠ FAIL、≠ PASS）。
* **FAIL=34**：同一特徵可對多原則重複列（例 `momentum_60d`×4）→ 特徵級失敗少於 34，但 APPLY 以列／特徵雙綠為準，**重複列不創造新 active**。
* **主因（G-PROM 三關，方法論 §四）**——live `gate_json` 理由分布（特徵級摘要）：
  * **`|hac_t| < 2.0`**（HAC Eff-t 未過）— 多數
  * **multi-seed Δ 不穩定**（`seed Δ mean ≤ 0` 或非全 seed＞0）— 次多
  * 少數僅 HAC 或僅 seed 單關紅
* **雙綠僅 2**：`inst_cumflow_position_120d`、`volume_gini_60d`（與 E123／run5／run6 同集合）。

### 2.3 為何 ECON-only 不能晉升

* AUTO-B：**七閘 AND**（G-ISO／G-MAP／G-PROM／G-ECON／G-ATTEST／G-KILL／G-NOEXEC）；`may_apply` 任一非 PASS → 拒絕。
* run6：**13** map 列＝`G-ECON=PASS` ∧ `G-PROM=FAIL`（交叉表 FAIL×PASS）。
* 特徵級 ECON-only 例：`cycle_position_252d`、`days_since_high_252d`、`institutional_net_buy_ratio_20d`、`range_position_120d`（G-PROM 敗在 seed Δ 或 `|hac_t|`）。
* **經濟價值 #14 撐住 ≠ 提拔關卡過**——靈魂／原則精華：IC／提拔與 #14 **雙軌**；晉升需雙綠。**禁止**「ECON 綠就 APPLY」捷徑。

### 2.4 missing 五特徵

| feature | 假說狀態 | 為何 SKIP | 本計畫路徑 |
|---|---|---|---|
| `roe` | SEED／map 已登錄 | 無 `feature_values` | S2：**僅當**庫內財報 raw 可 as-of 算出才建；否則維持 missing |
| `debt_ratio` | 同上 | 同上 | 同上 |
| `piotroski_fscore` | 同上（9 訊號綜合） | 同上 | 同上；複雜度高→可分項特徵＋文獻 map，禁一次幻造完備 |
| `peg_ratio` | 同上 | 同上 | 需成長／盈餘預期類 raw；缺則 missing |
| `macro_regime` | 同上 | 同上 | 常涉 FRED／總經；**FZ-keep 下預設不建**；若純庫內代理須人裁可證偽定義 |

### 2.5 blocked_div

* `BLOCKED_DIV_FEATURES`（`evolution.py`）含 `dividend_yield` 等；`classify_coverage` → **blocked_div**。
* G-DIV-1：Dividend 重建 **PAUSED**（API 凍結）；即使庫內有殖利率列，**覆蓋／重驗／上線不得標完備**。
* 本計畫：**不**以解凍補 Dividend 當擴大 n_feats 主路徑；股息族維持 freeze／SKIP。

### 2.6 瓶頸一句

```text
熱路徑已接 prodset（P2H）──OK
再跑同一 mapped 集合（run6）──雙綠仍 2
    │
    ├─ missing×5／blocked_div×1 → SKIP（無證據可晉升）
    ├─ mapped 多數 → G-PROM 三關紅（HAC-t／seed Δ）
    └─ ECON-only×13 列 → 禁 APPLY
擴大 n_feats ⇒ 新／精煉假說·map ＋ 庫內可建特徵 ＋ 真雙綠
              （非降閘、非解凍當主路徑）
```

---

## 3. 分階段

| 階段 | 名稱 | 產出 | 停手 |
|---|---|---|---|
| **S0** | 診斷帳 | 每 map 列／特徵：coverage、G-PROM／ECON verdict＋reason、是否 ECON-only；unmapped-in-fv 清單；missing 可建性（庫內 raw 探針，零 API） | 把 SKIP／FAIL 改寫成 PASS；改閾值 |
| **S1** | 假說／map 策展 | 人＋文獻：新／修 `philosophy_principle`＋`principle_factor_map`＋`philosophy_source`；優先把 **已有 fv 未 map** 的 17 特徵對上可溯源假說；方向＝文獻預期 IC | AI 生成 statement／citation；無來源 INSERT |
| **S2** | 可建特徵 | **僅** S0 標「庫內可算」者：寫 builder→`feature_values`（候選表紀律若適用）；更新 coverage | 為建特徵打 FinMind／FRED；假值補洞 |
| **S3** | 再跑 local-gates | `run_philosophy_evolution.py --local-gates`→APPLY 僅真雙綠；prodset active 對照 | skeleton 當綠；ECON-only APPLY；kill=halt 仍衝 |
| **S4** | 熱路徑重訓 | 僅當 active **集合變更**後：`train_ranker`／`predict_asof`（庫內 as-of；預設 prodset） | active 未變卻宣稱 n_feats 成長 |
| **U** | 對抗／ultracode | 假綠／降閾／AI 入庫／解凍偷渡／隔離破口 | 無 U 稱 MAP DONE |

**建議近程授權**：`MAP-E012`＝S0＋S1＋S2（庫內可建子集）— 見 §10；S3／S4／U 另令。

---

## 4. Schema／Python 規畫

### 4.1 (a) Table schema

| 表 | 本計畫 | 說明 |
|---|---|---|
| `philosophy_school`／`philosophy_principle`／`philosophy_source` | **讀＋策展寫** | 新原則／來源；`source_type` CHECK 禁 `ai_generated` |
| `principle_factor_map` | **讀＋策展寫** | `(principle_id, feature, direction±1)`；`validated_*` **僅**閘後回填，禁手改當綠 |
| `evolution_coverage_snapshot` | **寫（審計）** | S0／S3 重跑覆蓋；class∈{mapped,missing,retired,blocked_div} |
| `evolution_run`／`promotion_queue`／`evolution_apply_log` | **S3 寫** | 既有 PME；config_json 閾值釘死 |
| `evolution_production_feature_set` | **S3 APPLY 寫** | active｜removed；熱路徑 SSOT |
| `feature_values`／（若用）`feature_candidate_values` | **S2 寫** | 候選紀律承 alpha 計畫：禁未晉升直污染生產交集 |
| `evolution_kill_switch` | **讀** | APPLY 前 clear |
| **新表** | **預設無** | S0 診斷可落 `reports/`＋可選 JSON 工件；若需 DB 診斷帳另提案，不本輪偷加 |

既有 DDL 權威：`src/augur/philosophy/framework.py`（philosophy_*）、`evolution.py`（evolution_*）。本計畫**不**改閘閾值欄位語意。

### 4.2 (b) Python 程式規畫

| 檔／入口 | 角色 | 階段 | 讀寫邊界 |
|---|---|---|---|
| `scripts/audit_philosophy_feature_coverage.py` | 覆蓋審計 | S0／S3 | 讀 map×fv；可寫 snapshot |
| **新建建議** `scripts/report_pme_gate_diagnosis.py` | 診斷帳（map×gate_json 交叉、ECON-only、unmapped-fv） | S0 | **唯讀** DB；出 `reports/` 或 stdout |
| `src/augur/philosophy/framework.py` | SEED／DDL；策展 upsert 路徑 | S1 | 寫 philosophy_*／map；禁 AI seed |
| `scripts/verify_philosophy_factors.py` | 假說驗證／回填輔助 | S1–S3 | 庫內；零 API |
| `scripts/verify_candidate_promotion.py` | G-PROM 三關證據 | S2–S3 | 庫內 panel／fv |
| `scripts/run_economic_eval.py`／`evaluation/portfolio.py` | G-ECON #14 | S3 | 庫內 |
| `scripts/run_philosophy_evolution.py --local-gates` | 編排重驗 | S3 | 寫 run／queue／snapshot |
| `scripts/apply_evolution_promotions.py` | AUTO-B APPLY | S3 | 僅 pending_auto 真綠 |
| 既有／新 `src/augur/features/*.py`＋對應 `scripts/build_*` | 庫內可建特徵 | S2 | 只讀 raw；寫 fv／candidate |
| `scripts/train_ranker.py`／`predict_asof.py` | 熱路徑 | S4 | 讀 prodset（P2H）；零 sync |
| `augur.audit.import_isolation` | G-ISO | 全程 | PIPELINE 禁 philosophy import |
| `scripts/check_cmd_matrix.py` | 新入口矩陣稽核 | 新增 script 時 | #18／#29 |

**強制關係**：S1 策展 → S0／S3 覆蓋重分類 → S3 閘證據 → APPLY → prodset → S4 消費；**禁**倒序「先重訓再補假說」。

---

## 5. 與 API：庫內可做 vs 真需 API

| 類 | 例 | 本計畫 |
|---|---|---|
| **庫內可做** | 對 **已有** `feature_values` 的 17 unmapped 特徵做文獻 map；對既有 mapped 精煉原則／方向；S0 診斷；S3 local-gates；S4 重訓；部分財報衍生（**若** raw 表已在庫且 as-of 可證） | **主路徑** |
| **庫內探針後決定** | `roe`／`debt_ratio`／F-Score 分項—查 schema／列數／發布滯後 | S0 標可建／不可建；不可建→維持 missing |
| **真需 API（另帳）** | Dividend 缺股補洞／G-DIV-1 完備；FRED 總經→`macro_regime`；正典 attestation heal 放量 | **FZ-keep**；不本計畫主路徑；解凍＋明示後另開 |

**交叉一句**：擴大假說／map **≠** 解凍；預測熱路徑 **≠** 解凍（P2H／predict-vs-market-api 已釘）。

---

## 6. 驗收表（機械 PASS／FAIL）

| ID | 驗收項 | PASS | FAIL |
|---|---|---|---|
| A0 | 本計畫存在且含 what／why／非目標／診斷／分階／schema／python／API 分界／拍板碼／誠實預期 | 本檔齊 | 缺塊 |
| A1 | S0 診斷帳可重跑；數字 trace 至 DB／stdout | 可複現 | 只敘事無指令 |
| A2 | S1 每筆新 map 有可溯源 `philosophy_source`；無 `ai_generated` | CHECK＋抽樣 | AI 摘要冒充原典 |
| A3 | S2 僅庫內可建；零 FinMind／FRED 進程／log | A8 式乾淨 | 有放量／probe |
| A4 | S3：`GATE-keep`—閾值與 DEFAULT_GATE_CONFIG 一致；SKIP≠PASS | config_json 釘死 | 降 `|hac_t|`／少 seed |
| A5 | APPLY 僅雙綠；ECON-only 仍 rejected_gate | queue 可證 | ECON-only applied |
| A6 | blocked_div／missing 不標 validated／不進 active | coverage＋prodset | dividend 假完備 |
| A7 | S4：active 變→n_feats 與名單一致；未變→不宣稱成長 | train metrics | 假擴大 |
| A8 | 隔離：`check_isolation()`＝0；熱路徑不 import philosophy | 綠 | 破隔離 |
| A9 | ≠可交易／確立級對外句 | 本輪報告零出現 | 出現＝FAIL |
| A10 | U 呈核含「多數仍可能不過閘」未查項 | audits 存在 | 無對抗稱 DONE |

**階段 DONE（建議）**＝授權範圍內 A* 機械 PASS；**≠** G-PROM 多數綠、**≠**可交易、**≠**解凍。

---

## 7. 風險與停手

| 風險 | 緩解 | 停手訊號 |
|---|---|---|
| 為成長降閘 | GATE-keep；U 打閾值字面 | config 改 min_abs_hac_t／min_seeds |
| AI 造原則 | source CHECK＋人審清單 | citation 無 DOI／ISBN／可核頁 |
| 解凍偷渡 | FZ-keep；Dividend 另帳 | sync／Dividend resume 進程 |
| Goodhart 刷 map 列 | 診斷以**特徵級雙綠→active**為成功；禁無文獻重複刷列 | 42→200 列但 active 仍 2 卻稱成功 |
| missing 假建 | #1 缺列；S0 可建性 | 無 raw 仍寫 fv |
| 破 P2H／FC-empty | 不改熱路徑契約 | 空 active 回退 canonical |

---

## 8. 誠實預期

* **可能仍多數不過閘**：HAC-t／多 seed 增量是硬門檻；新 map 若只是「文獻有、訊號弱」，G-PROM 仍 FAIL。
* **ECON PASS 增多 ≠ active 增多**。
* **建齊 missing 五特徵 ≠ 五條雙綠**（建值後才有資格被評，評完仍可能紅）。
* **blocked_div 在解凍前不貢獻 active**。
* **成功定義**：可追溯策展＋庫內可建路徑＋真雙綠才成長 n_feats；**失敗可接受**＝診斷帳證明「試過、沒過、沒假綠」。

---

## 9. 明確不在範圍（再聲明）

1. 解凍／放量 FinMind／FRED  
2. Dividend DROP＋re-sync／宣稱 G-DIV-1 閉合  
3. 放寬或跳過 G-PROM／G-ECON  
4. AI 生成原則／假說入 DB  
5. 改 [N]／自動下單／確立級宣稱  
6. 他域進化閉環灌台股因子  
7. 無雙綠時手改 `evolution_production_feature_set`  

---

## 10. Steward 拍板句（請擇一或組合回覆）

> 回覆字串即可登錄為本計畫授權（**不**自動等於開實作，除非含執行項）。

### 10.1 計畫採納（必選）

- **〔MAP-P-yes〕** 採納本計畫為「擴大假說／map 覆蓋」藍圖；實作另待分階令。  
- **〔MAP-P-rev〕** 須修訂後再呈（請註條款）。  
- **〔MAP-P-no〕** 否決。

### 10.2 執行範圍（採納後、開實作時）

- **〔MAP-E0〕** 只做 S0 診斷帳。  
- **〔MAP-E012〕** S0＋S1＋S2（庫內可建子集）— **建議近程**。  
- **〔MAP-E0123〕** 至 S3 local-gates＋APPLY（仍 GATE-keep／FZ-keep）。  
- **〔MAP-Efull〕** S0–S4＋U（仍≠可交易／≠解凍）。

### 10.3 硬邊界碼（建議與採納同掛）

- **〔FZ-keep〕** 維持 API 凍結；擴大 map ≠ 解凍；Dividend 另帳。  
- **〔GATE-keep〕** 不降 G-PROM／G-ECON 閾值；ECON-only 不晉升；SKIP≠PASS。

### 10.4 明確不授權（預設）

- 不放量 API；不假關 Dividend；不 AI 入庫；不改 [N]；不無雙綠改 prodset；不無 U 稱產品完備。

**建議拍板組合**：`MAP-P-yes` ＋ `MAP-E012` ＋ `FZ-keep` ＋ `GATE-keep`。

> **✅ 已登錄（2026-07-24）**：`MAP-P-yes`＋`MAP-E012`＋`FZ-keep`＋`GATE-keep` — 見文首「Steward 已拍板」。  
> **✅ 執行已開（2026-07-24）**：Steward「**開 MAP-E012**」→ S0＋S1＋S2（庫內可建）；`audits/PME-MAP-E012-CLOSED-20260724.md`。  
> 留痕：`audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md`。**不改 [N]**；S3／S4／U 另令。

---

## 11. 產物與下一步

| 產物 | 路徑 |
|---|---|
| **本計畫** | `reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md` |
| 上游 PME 計畫 | `reports/augur_philosophy_market_evolution_loop_plan_20260724.md` |
| Gap 帳本 | `reports/augur_pme_gap_ledger_20260724.md` |
| 再晉升／重訓 | `audits/PME-LOCAL-REPROMOTE-20260724.md`／`PME-REPROMOTE-RETRAIN-20260724.md` |
| P2H | `reports/augur_prodset_predict_hotpath_plan_20260724.md` |
| 拍板後 audit | ✅ `audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md` |
| 執行（MAP-E012） | `audits/PME-MAP-E012-CLOSED-20260724.md`（或 STATUS） |
| 路線圖／HANDOFF | §4.0 已掛接 |

**下一步（人）**：S0–S2 收尾後，若要再閘／APPLY →「**開 MAP-S3**」（仍 GATE-keep／FZ-keep）。

---

*計畫完整性：§4 schema＋python；§3 分階；§6 驗收；§10 拍板。30 分鐘可讀：§0–§2＋§3 表＋§10。*
