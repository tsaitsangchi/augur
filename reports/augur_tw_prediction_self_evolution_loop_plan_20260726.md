# 台股預測模擬模型自進化迭代學習計畫 [I]（2026-07-26）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；領域大憲章第六部計畫完整性 v1.39.0）— **不創設 [N] 義務**；**拍板前不實作**
* **授權觸發**：Steward「採納 TWEVO 計畫」＝只採本檔；「開 TWEVO-S*」＝分階實作（見 §10）
* **一句定錨**：**價值＝把既有進化零件串成可重複的自進化迭代閉環**（假說 map → 候選建值 → local-gates → 雙綠 → APPLY → prodset 重訓 → as-of 模擬／arena 對局 → 結算 → 證據回饋 → 下一輪），**非發明新輪子**
* **對齊既有**（引用、不重寫）：PME＝`reports/augur_philosophy_market_evolution_loop_plan_20260724.md`；MAP 擴大＝`reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md`；P2H＝`reports/augur_prodset_predict_hotpath_plan_20260724.md`；arena＝`reports/augur_direction_live_arena_plan_20260711.md`；方法論 §四＝`reports/augur_feature_discovery_methodology_20260626.md`；預測正交＝`.cursor/rules/predict-vs-market-api.mdc`
* **正交**：路線 B（本地 LLM 變聰明）＝`reports/augur_local_ai_route_b_no_gpu_plan_20260726.md`／`reports/augur_local_ai_evolution_loop_plan_20260725.md` — **本計畫只動預測系統進化，不動 advisor／MCP LLM**；協作介面＝本檔 **§8**＋可選 `reports/augur_dual_self_evolution_interface_20260726.md`
* **現況錨（HANDOFF §4／audits／診斷；#15 待執行時重查）**：

| 項 | 現況（2026-07-24～26） | 出處 |
|---|---|---|
| prodset → 熱路徑 | ✅ P2H S1–S3＋U-P2H DONE；**active n=2**（誠實極窄） | HANDOFF §4.0；`audits/P2H-*` |
| 雙綠特徵 | 僅 **`inst_cumflow_position_120d`**、**`volume_gini_60d`** | E123／repromote；`PME-E123-STATUS` |
| local-gates 真跑 | `run_id=5`（E123）／`run_id=6`（再晉升）；診斷帳另有早期 **`run_id=1`** 快照 | audits／`augur_pme_gate_diagnosis_*` |
| MAP | **MAP-E012 CLOSED**（mapped 17→35）；**未**跑 S3 local-gates／S4 重訓 | `PME-MAP-E012-CLOSED` |
| G-PROM-D2 | 借券**真窗**候選 `|hac_t|≥2` 已過**第一關**（例：`lending_fee_rate_mean_20d` 2.63、`lending_fee_vw_mean_20d` 2.94）；multi-seed／G-ECON 仍 SKIP；**本腳本不 APPLY** | `reports/augur_gprom_d2_probe_20260724.md` |
| API | **FZ-keep** 仍凍；預測＝庫內 as-of | `finmind-fred-api-freeze`／`predict-vs-market-api` |
| 確立級 | `direction_gate.evaluated_pass=0` → **禁確立級／可交易宣稱** | HANDOFF 紅線 |

---

## 0. 結論（先讀這段即可）

已有 PME 閘／佇列／prodset、P2H 熱路徑、MAP 策展、候選隔離表、arena 對局與結算、revalidation／trial ledger、train／predict。**缺的是「一輪迭代」的編排帳本＋driver**：把上述步驟編成 **resume-safe、可 dry-run、可停損** 的閉環，並把模擬對局結果**回饋假說地圖**（非只停在雙綠 APPLY）。

成功定義＝**可重複、可驗、可停**的迭代機器；**≠** n_feats 保證成長、**≠** 可交易、**≠** 解凍 API。無增益 N 輪 → 停損；kill-switch → 拒 APPLY。

---

## 1. What／Why／非目標／與既有關係

### 1.1 What

| 面向 | 定義 |
|---|---|
| **標的** | 台股**預測模擬**模型的自進化迭代（paper／閘內；庫內 as-of） |
| **閉環** | 假說 map 擴充 → 候選建值（隔離表）→ local-gates（GATE-keep）→ 雙綠 → **人開本輪 APPLY** → prodset 重訓 → as-of 模擬／arena 對局 → 結算 label → 證據回饋（gap ledger／map curate）→ 下一輪 |
| **新交付（拍板後）** | (1) 迭代帳本表 `evolution_iteration_ledger`；(2) 一輪 driver `scripts/run_evolution_iteration.py`；(3) 可選 migrate／verify 哨兵 |
| **人** | 拍板開階／開本輪 APPLY；監控；kill-switch；治權變更。**不做**自動下單 |

### 1.2 Why（缺口，非重複發明）

| 既有零件 | 能做什麼 | **閉環缺口** |
|---|---|---|
| `run_philosophy_evolution.py --local-gates` | 一輪閘裁決 → `evolution_run`／`promotion_queue` | 不串 map 建值、不串重訓、不串 arena、無「第 N 輪」帳本 |
| `apply_evolution_promotions.py` | PME-AUTO-B：雙綠∧kill=clear → APPLY＋prodset | 無「本輪迭代授權」語意；不觸發下游重訓／對局 |
| `curate_pme_map_expand.py`／MAP 計畫 | 策展 map | MAP-E012 停在 S2；S3／回饋未閉 |
| `feature_candidate_values`＋漏斗工具 | 隔離候選＋HAC／增量 | 與 PME queue／iteration 無統一 driver |
| `train_ranker`／`predict_asof`／`verify_prodset_hotpath` | prodset 熱路徑訓練／預測 | 手動接在 APPLY 後；無迭代 ID 掛鉤 |
| arena 日管線／settle／scoreboard | 方向軸對局＋結算 | 與 PME 晉升迴路**未機械串接**；凍結下須 `--skip-sync` |
| `run_revalidation_cycle`／`trial_ledger` | 再驗證／deflation N | 非每輪 iteration 強制掛載 |
| gap ledger／gate diagnosis | 人工診斷帳 | 無「上一輪證據 → 下一輪假說」自動帳本列 |

### 1.3 明確不做

| 不做 | 理由 |
|---|---|
| 降 G-PROM／G-ECON 閾值／ECON-only APPLY | **GATE-keep** |
| FinMind／FRED sync／probe／解凍 | **FZ-keep**；預測正交 ≠ 解凍 |
| 自動下單／券商執行 | 靈魂「扣扳機的是人」；PME-AUTO-B 僅特徵／原則**狀態** |
| 宣稱可交易／確立級 | `evaluated_pass=0`；迭代≠變準 |
| AI 生成原則入庫／哲學 runtime 加權 | #1／隔離／A.16 |
| 改 advisor／路線 B LLM 權重或 prompt-pack | **正交**；另案 |
| 無雙綠手改 `evolution_production_feature_set` | #15／Goodhart |
| 把整庫 raw 寫進靈魂 | `soul-vs-raw-correlation` |

### 1.4 與 PME／AUTO-B 相容句

* **PME-AUTO-B 不變**：引擎在閘全綠∧kill=clear 時**可以** APPLY（無人逐特徵簽名）。
* **本計畫加一層「迭代人閘」**：**開本輪 driver 的 APPLY 步**須 Steward 明示（如 `TWEVO-APPLY-go` 或 driver `--allow-apply` 僅在已拍板輪次），避免無人看顧連跑 APPLY→重訓→對局。
* **kill-switch**（`evolution_kill_switch`）仍凌駕一切 APPLY。

---

## 2. 硬邊界（寫進計畫＝執行時不可逾）

1. **GATE-keep**：不降 `DEFAULT_GATE_CONFIG`（`min_abs_hac_t=2`／`min_seeds=3`／`min_delta_ic=0`；G-ECON cost=0.00585、MaxDD 地板）；SKIP≠PASS；ECON-only 禁晉升。  
2. **FZ-keep**：全程**庫內 DB as-of**；零 FinMind／FRED；arena／日管線一律 `--skip-sync`（或等價庫內路徑）。  
3. **自動下單禁**：APPLY＝狀態晉升；**≠**交易執行。  
4. **≠可交易／≠確立級**：即使雙綠↑、arena paper 綠，仍禁確立級宣稱，除非另案過方向軸門二。  
5. **#1 source-pure／#8 anti-leakage／#11 多 seed／#14 經濟終關**：迭代不得繞過；禁裸 iid Eff-t。  
6. **三敵零容忍**：迭代≠變準；增益須 out-of-sample／可重現證據；禁手改 validated_*／假綠。  
7. **預測正交**：缺最新增量 → DB as-of 續跑；不得因「API 凍」拒絕庫內 train／predict。  
8. **隔離**：預測 7 package 不 import `philosophy`／`advisor`／`knowledge`；候選只寫 `feature_candidate_values`，晉升後才入 `feature_values`／prodset。

---

## 3. 閉環流程（一輪＝一個 `iteration_id`）

```
┌─────────────────────────────────────────────────────────────────┐
│  I0  假說 map 擴充／精煉（人＋文獻；curate／MAP；禁 AI 入庫）      │
│       ↓                                                          │
│  I1  候選建值 → feature_candidate_values（隔離；真窗／as-of）     │
│       ↓                                                          │
│  I2  漏斗預篩（可選：HAC 第一關／去相關／增量）→ 合格才 map 或晉升路徑 │
│       ↓                                                          │
│  I3  local-gates（run_philosophy_evolution --local-gates）         │
│       → evolution_run + promotion_queue + coverage_snapshot        │
│       ↓                                                          │
│  I4  雙綠？ 否 → 寫 gap／iteration 結案（no_promote）→ I8 回饋     │
│       是 → Steward 開本輪 APPLY（TWEVO-APPLY）                     │
│       ↓                                                          │
│  I5  apply_evolution_promotions（kill=clear；閘全綠）             │
│       → philosophy status + evolution_production_feature_set       │
│       ↓                                                          │
│  I6  prodset 重訓 train_ranker + verify_prodset_hotpath            │
│       + predict_asof（dry-run／寫 prediction_values 依旗標）       │
│       ↓                                                          │
│  I7  模擬對局：arena --skip-sync（paper）± revalidation_cycle      │
│       → settle_arena_labels → scoreboard（可選）                   │
│       ↓                                                          │
│  I8  證據回饋：gap ledger 列 + map curate 建議 + iteration 結算    │
│       ↓                                                          │
│  I9  停損判準？ 是 → halt／freeze 迭代；否 → 下一輪 I0             │
└─────────────────────────────────────────────────────────────────┘
```

**機械掛鉤**：每步寫入 `evolution_iteration_ledger.steps_json`（狀態／script／exit／產物 path／關聯 `run_id`／`model_id`／arena as-of）；失敗不半套前進（fail-closed）。

---

## 4. (a) Table schema

### 4.1 所讀既有表（摘要；DDL 住所不變）

| 表 | 角色 | 本閉環讀／寫 | DDL／SSOT |
|---|---|---|---|
| `principle_factor_map`／`philosophy_principle` | 假說↔特徵；status | I0 寫 map；I5 翻 status | `framework.py`／PME 計畫 |
| `feature_values` | 生產特徵面板 | I3 讀；晉升後 builder 寫 | features／panel |
| `feature_candidate_values` | 候選隔離 staging | I1 寫；漏斗讀；禁污染 canonical | `audit/feature_candidate.py` |
| `evolution_run` | 一趟 local-gates／skeleton 跑 | I3 寫 | `philosophy/evolution.py` EVOLUTION_DDL |
| `evolution_coverage_snapshot` | mapped／missing／blocked_div | I3 寫 | 同上 |
| `promotion_queue` | pending_auto／applied／rejected_gate／halted | I3 寫；I5 消費 | 同上 |
| `evolution_apply_log` | APPLY 前後＋prodset delta | I5 寫 | 同上 |
| `evolution_kill_switch` | clear／halt | 每步讀；人設 | 同上 |
| `evolution_production_feature_set` | prodset active／removed | I5 寫；I6 讀 | 同上；P2H |
| `model_registry`／`prediction_values` | 訓練產物／預測 | I6 寫 | `migrate_prediction_ddl.py` |
| `trial_ledger`／`revalidation_ledger`／baseline | deflation N／再驗證 | I7 可寫／讀 | `migrate_trial_ledger_ddl.py` 等 |
| `direction_arena_*` | 對局候選／預測／policy／verdict | I7 | `migrate_direction_arena_ddl.py` |
| `arena_admission_gate`／`direction_gate` | G1–G5；G1-PIN as-of **2026-06-30**；門二 | I7 閘讀 | arena G1–G5 計畫 |
| `core_universe_asof`／panel 相關 | as-of 宇宙 | I6／I7 讀 | 既有 |

**既有 evolution 核心 DDL（引用，不重定義）** — 見 `src/augur/philosophy/evolution.py`：`evolution_run`、`evolution_coverage_snapshot`、`promotion_queue`、`evolution_apply_log`、`evolution_kill_switch`、`evolution_production_feature_set`。

**候選表（引用）**：

```sql
-- audit/feature_candidate.py::ensure_candidate_table（同構於 feature_values）
CREATE TABLE IF NOT EXISTS feature_candidate_values (
  panel_date date NOT NULL,
  stock_id   varchar NOT NULL,
  feature    varchar NOT NULL,
  value      double precision,
  PRIMARY KEY (panel_date, stock_id, feature)
);
```

### 4.2 新表：`evolution_iteration_ledger`（建議完整 DDL）

**結果落點**：每輪迭代一列（或一步一列由 `steps_json` 承載）；**不**進預測特徵；**不**取代 `evolution_run`（一 iteration 可含 0..n 個 evolution_run）。

```sql
CREATE TABLE IF NOT EXISTS evolution_iteration_ledger (
  iteration_id      BIGSERIAL PRIMARY KEY,
  started_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at       TIMESTAMPTZ,
  status            VARCHAR(32) NOT NULL,
  -- planned|running|succeeded|failed|halted|stopped_no_gain
  trigger_code      VARCHAR(64) NOT NULL,  -- 例 TWEVO-S2-go / TWEVO-APPLY-go
  asof_snapshot     DATE,                 -- 本輪庫內 as-of（FZ-keep）
  horizon_h         INTEGER NOT NULL DEFAULT 60,
  since_date        DATE NOT NULL DEFAULT DATE '2021-01-01',
  kill_switch_at_start VARCHAR(16) NOT NULL,
  evolution_run_id  BIGINT REFERENCES evolution_run(run_id),
  apply_allowed     BOOLEAN NOT NULL DEFAULT false,  -- 人閘：本輪是否允許 APPLY
  dual_green_n      INTEGER,              -- 本輪雙綠特徵數
  dual_green_names  TEXT[] NOT NULL DEFAULT '{}',  -- 雙綠 feature 名（可溯 queue）
  near_miss_json    JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- [{feature,gate,reason}] 閘失敗近失：僅名＋閘碼＋理由；禁 raw／IC 確立級措辭
  prodset_active_n  INTEGER,              -- APPLY 後 active 數
  model_id          TEXT REFERENCES model_registry(model_id),
  arena_asof        DATE,
  gain_json         JSONB,                -- 相對上輪：Δactive、ΔIC、#14、arena metrics（可空）
  gain_basis        VARCHAR(32),          -- dual_green_delta|prodset_delta|arena_prereg|none|incomparable
  consecutive_no_gain INTEGER NOT NULL DEFAULT 0,  -- 結案時累計無增益輪（停損計數）
  steps_json        JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- [{step,script,argv,rc,started,finished,artifacts,notes}, ...]
  stop_reason       TEXT,                 -- 停損／halt／無雙綠等
  advisor_brief_path TEXT,                -- 可選：I8 匯出唯讀摘要 path（§8.2；禁 panel）
  cross_notify_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  -- {kill_halt?, stop_no_gain?, notified_at, twin_ack?} 與 LAIEVO 共享通知語意（非合併表）
  notes             TEXT,
  code_sha          VARCHAR(64),
  config_json       JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (status IN (
    'planned','running','succeeded','failed','halted','stopped_no_gain'
  )),
  CHECK (kill_switch_at_start IN ('clear','halt')),
  CHECK (gain_basis IS NULL OR gain_basis IN (
    'dual_green_delta','prodset_delta','arena_prereg','none','incomparable'
  ))
);

CREATE INDEX IF NOT EXISTS ix_evo_iter_started
  ON evolution_iteration_ledger (started_at DESC);

COMMENT ON TABLE evolution_iteration_ledger IS
  'TWEVO 自進化迭代帳本 [I]；串 PME/P2H/arena 一輪閉環；≠可交易/確立級；禁進預測特徵';
```

**可選附表**（若要一步一列查詢；非必須，可用 `steps_json` 先上）：

```sql
CREATE TABLE IF NOT EXISTS evolution_iteration_step (
  iteration_id  BIGINT NOT NULL REFERENCES evolution_iteration_ledger(iteration_id)
                ON DELETE CASCADE,
  step_ord      SMALLINT NOT NULL,
  step_key      VARCHAR(32) NOT NULL,  -- I0..I9
  rc            INTEGER,
  detail        JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (iteration_id, step_ord)
);
```

**Migrate 入口（拍板後）**：`scripts/migrate_evolution_iteration_ddl.py`（`--run`／`--check`／`--selftest`；#18／#29 指令矩陣）。

---

## 5. (b) Python 程式規畫

### 5.1 既有 script 對映（簽名／I-O 摘要）

| 階段 | Script | 主要 CLI | 輸入表 | 輸出表／產物 |
|---|---|---|---|---|
| I0 | `scripts/curate_pme_map_expand.py`；`report_pme_gate_diagnosis.py` | curate／診斷唯讀 | map／fv／queue | map 列；`reports/*diagnosis*` |
| I1 | 特徵 builder／audit 候選路徑（既有 `features/*`＋`feature_candidate.py`）；D2 probe 產物參考 `augur_gprom_d2_probe_*` | 各 builder 自有矩陣 | raw／panel | **`feature_candidate_values`** |
| I2 | `verify_candidate_promotion.py`／漏斗家族；G-PROM-D2 probe 報告 | 依各檔 | candidate＋label | stdout／reports；**不 APPLY** |
| I3 | **`run_philosophy_evolution.py --local-gates`** | `--local-gates [--dry-run] [--skip-multi-seed] --since --h --selftest` | fv／map／panel | **`evolution_run`／`promotion_queue`／snapshot** |
| I4 | （邏輯在 driver）讀 queue gate_json | — | queue | 雙綠清單 |
| I5 | **`apply_evolution_promotions.py`** | `[--dry-run] --run-id N`；`--selftest` | queue／kill | status／**prodset**／apply_log |
| I5b | `set_evolution_kill_switch.py` | `--status`／set halt\|clear | kill 表 | kill 表 |
| I6 | **`train_ranker.py --run`**；**`verify_prodset_hotpath.py --check`**；**`predict_asof.py --run [--dry-run]`** | 見各檔矩陣；asof 釘庫內 | prodset／panel | **model_registry**／artifact／prediction_values |
| I7a | **`run_arena_daily_pipeline.py --run --skip-sync [--date]`** 或 **`run_arena_round.py --run`** | 凍結下**禁**無 skip-sync 全鏈 | 閘＋方向特徵 | arena_prediction |
| I7b | **`settle_arena_labels.py --run`**；**`arena_scoreboard.py`** | `--run`／`--judge` | prediction | 結算欄／verdict |
| I7c | **`run_revalidation_cycle.py`**；`revalidate_baseline.py` | `--dry-run` 等 | ledger | revalidation／trial |
| I8 | `report_pme_gate_diagnosis.py`；更新 `reports/augur_pme_gap_ledger_*.md`（人審）；可選 curate；**可選** `export_evolution_advisor_brief.py`（§8.2） | 唯讀為主 | run／queue／ledger | reports／下一輪 map 清單／`advisor_brief_path` |
| 哨兵 | `evaluate_arena_admission.py --check GATE_ID` | G1-PIN 等 | admission | rc |
| 週儀表 | `report_dual_evolution_week.py`（可選；§8.4） | 並列讀兩 ledger | 兩帳本 | stdout／reports；**不合併表** |

**DEFAULT_GATE_CONFIG**（GATE-keep 釘死；改閾＝治權案）：`src/augur/philosophy/evolution.py` — G-PROM `min_abs_hac_t=2`、`min_seeds=3`、`min_delta_ic=0`；G-ECON `cost=0.00585`、`max_dd_floor=-0.60`。

### 5.2 新編排：`scripts/run_evolution_iteration.py`（草案）

**職責**：一輪閉環 driver — 建／更新 `evolution_iteration_ledger`；依 `--steps` subprocess 呼叫既有 script；**resume-safe**（已成功 step 跳過）；讀 kill-switch；**預設不 APPLY**（需 `--allow-apply` 且 ledger.`apply_allowed` 經拍板寫入）；全程零市場 API。

**CLI 草案**：

```text
python scripts/run_evolution_iteration.py
  # 安全預設：印指令矩陣＋最近 iteration 摘要（不跑）

python scripts/run_evolution_iteration.py --selftest
  # 免 DB：步驟圖／狀態機／禁 sync 字串鎖

python scripts/run_evolution_iteration.py --dry-run [--steps I0,I3,I4]
  # 印將執行之 argv；可寫 status=planned 列（可選 --persist-plan）

python scripts/run_evolution_iteration.py --run --trigger TWEVO-S2-go \
  --asof 2026-06-30 --steps I0,I1,I2,I3,I4,I8
  # 一輪至閘／回饋；無 APPLY

python scripts/run_evolution_iteration.py --run --trigger TWEVO-APPLY-go \
  --iteration-id N --allow-apply --steps I5,I6,I7,I8
  # 人拍板後續跑 APPLY→重訓→arena（內部 arena 強制 --skip-sync）

python scripts/run_evolution_iteration.py --resume --iteration-id N
  # 自失敗／中斷 step 續跑
```

**不變式（selftest 鎖）**：

* argv 不得含未跳過之 FinMind／FRED sync 入口（FZ-keep）。  
* `--allow-apply` 缺省 false；無雙綠不得呼叫 apply。  
* kill≠clear → 跳過 I5、iteration → `halted`。  
* 新增入口**首次提交即含執行指令矩陣**（#18／#29）。

### 5.3 其他新檔（拍板後、最小集）

| 檔 | 角色 |
|---|---|
| `scripts/migrate_evolution_iteration_ddl.py` | 冪等 DDL＋`--check`／`--selftest` |
| `scripts/verify_evolution_iteration.py`（可選） | 哨兵：ledger 與 run／prodset／model_id 一致性；V2–V5 SQL 鎖 |
| `scripts/export_evolution_advisor_brief.py`（可選；§8.2） | 自 ledger／queue／scoreboard **唯讀**匯出 advisor 可檢索摘要（禁 panel／禁未過閘確立級） |
| `scripts/report_dual_evolution_week.py`（可選；§8.4） | 並列讀 `evolution_iteration_ledger`＋`local_ai_iteration_ledger`；共享停損／kill 通知；**不合併表** |
| `src/augur/philosophy/iteration.py`（可選 library） | 純函式：step 圖、停損、gain 比較；`--selftest` |

**不新建**：G-PROM／G-ECON 裁決、APPLY 寫 prodset、train／predict、arena settle（一律呼叫既有）。

---

## 6. 迭代節奏與停損

### 6.1 建議節奏

| 節奏 | 內容 | 備註 |
|---|---|---|
| **每輪（人開）** | I0→I8 子集；耗時主幹≈ local-gates 25–35 min（現況經驗） | 背景跑＋ledger；#21 回報 |
| **APPLY 子輪** | 僅當雙綠＞上輪已 APPLY 集合或有新雙綠 | 須 `TWEVO-APPLY-go` |
| **arena 子輪** | 庫內 `--skip-sync`；G1-PIN 地基仍釘 **2026-06-30** 語意不滾動偷改 | 對局 paper |
| **回饋** | 每輪更新 gap／診斷；MAP 策展累積到下輪 I0 | 禁無證據刷 map 列（Goodhart） |

### 6.2 每輪驗收判準（機械可驗）

| ID | 判準 | 驗法（機械） |
|---|---|---|
| **V0** | FZ-keep | `rg -n 'finmind\.fetch|fred\.fetch|sync_finmind' steps_json／log`＝0；arena argv 含 `--skip-sync`；`config_json->>'api' IS DISTINCT FROM 'live'` |
| **V1** | GATE-keep | `config_json->'gates'` 等於 `DEFAULT_GATE_CONFIG` 序列化；queue 無 `applied` 且僅 ECON PASS／G-PROM SKIP |
| **V2** | 帳本完整 | `status∈終態`；`finished_at NOT NULL`；`jsonb_array_length(steps_json)=完成步數`；每步 `rc` 鍵存在；`consecutive_no_gain` 與前輪 SQL 可重算一致 |
| **V3** | 雙綠誠實 | `dual_green_names ⊆` queue 中同 `evolution_run_id` 且 G-PROM∧G-ECON＝PASS 之 feature 集；`dual_green_n = cardinality(dual_green_names)` |
| **V4** | APPLY 紀律 | `apply_allowed=false` → `evolution_apply_log` 本輪無新列；kill=halt → 無新 `applied`；無 `TWEVO-APPLY-go` 不得 `--allow-apply` |
| **V5** | 熱路徑 | APPLY 後 `verify_prodset_hotpath.py --check` rc=0；`model_id` 非空且 `model_registry` 可 join；`prodset_active_n`＝active 計數 |
| **V6** | 隔離 | `import_isolation`／philosophy isolation 綠；driver／brief **不** import `advisor`／`knowledge` 寫路徑 |
| **V7** | 非宣稱越界 | `notes`／brief／reports：`rg '可交易|確立級|已解凍'`＝0（允許「禁確立級」否定句）；`gain_basis≠` 把未過閘 IC 標為確立 |
| **V8** | 近失可溯 | `near_miss_json` 每元素含 `feature,gate,reason`；**無** panel 列／整庫 dump；brief 若匯出則 path＝`advisor_brief_path` 且檔內無 raw 陣列 |
| **V9** | 停損觸發 | 達 N 無增益 → `status=stopped_no_gain` ∧ `stop_reason` 非空 ∧ `cross_notify_json ? 'stop_no_gain'`；kill→`halted` |

**哨兵一鍵（拍板後）**：`python scripts/verify_evolution_iteration.py --iteration-id N --check` 對 V0–V9 出綠／紅表。

### 6.3 停損與 kill

| 機制 | 規則 |
|---|---|
| **無增益停損** | 連續 **N=3** 輪（`TWEVO-N=3` 可改）：`gain_basis∈{none}` 或（無新雙綠 ∧ prodset active 未增 ∧ 無預註冊 arena／revalidation 正向）→ `consecutive_no_gain+=1`；達 N → `stopped_no_gain`；停自動開下一輪；寫 `cross_notify_json` |
| **假說耗盡** | missing／D2 候選皆評完且無雙綠 → 同停損；改人工 MAP／另案（**禁止**降閾當彈藥） |
| **kill-switch** | `evolution_kill_switch.state=halt` 或 `AUGUR_EVOLUTION_KILL_SWITCH=halt` → 拒 I5；iteration=`halted`；**同時**寫共享通知（§8.3）——LAIEVO 側僅告警、**不**自動改 serving |
| **閘紅風暴** | 單輪 rejected_gate 全數且無雙綠＝**實驗成功定義**（否證），寫入 gap＋`near_miss_json`，**不**降閾重跑 |
| **VRAM／主機擠壓** | 若同機偵測 LAIEVO B2/B3 訓練窗（§8.4 錯峰）→ driver 可 `--defer-heavy` 跳過 I6 重訓至錯峰窗；**不**算增益 |
| **回滾** | APPLY 誤傷：`demote`／prodset `removed`＋重訓回上一個 model_id（artifact 保留）；ledger 留痕；**不**手 UPDATE 生產特徵值 |

---

## 7. 分階段落地＋驗收＋回滾

| 階段 | 內容 | 驗收 | 回滾 |
|---|---|---|---|
| **S0** | 盤點：對照本檔 §1.2 缺口；確認 prodset n、最新 evolution_run、D2 候選狀態 | 現況表寫入 audit／本檔附錄更新；V0／V6 | 無碼可回 |
| **S1** | DDL：`migrate_evolution_iteration_ddl.py` | `\d` 表存在；`--selftest` 綠 | DROP 新表（無業務依賴時） |
| **S2** | driver：`run_evolution_iteration.py` 實作 I3／I4／I8＋dry-run／resume／selftest（**無 APPLY**） | 一輪 dry＋一輪真實 local-gates 寫入 ledger；V0–V3 | 停用 script；ledger 保留 |
| **S3** | 接 I5–I6：`--allow-apply` 路徑＋train＋hotpath 哨兵 | 人造／真雙綠路徑：APPLY 後 n_feats 可解釋；V4／V5 | demote＋重訓舊 model |
| **S4** | 接 I7：arena `--skip-sync`＋settle（± revalidation） | 結算列可溯 iteration_id；V0／V7 | 停 arena 步；不改 PME 表 |
| **S5** | 停損／gain_json／N 輪自動停；gap 回饋模板 | 連續無增益模擬→`stopped_no_gain` | 調 N 須人拍 |
| **U** | 對抗：假 APPLY、偷 sync、降閾、無雙綠改 prodset、路線 B 誤接、brief 灌 panel、advisor 直改 prodset | 攻擊表全擋 | 修 driver／export allowlist |

**近程建議開工序**：S0→S1→S2（先有帳本＋閘輪）→（有新雙綠或開 MAP-S3 後）S3→S4。

**與 MAP／D2 銜接（彈藥，非本計畫重做）**：

* 開 **MAP-S3**（另令）：對 MAP-E012 新 map 跑 local-gates／APPLY。  
* **G-PROM-D2** 真窗借券：第一關已過者 → 補 multi-seed＋G-ECON → 過則 map＋納入某輪 I3；**禁止** probe 直接 APPLY。

---

## 8. 與對偶計畫交互（路線 B／LAIEVO；正交＋協作介面）

> **對偶檔**：`reports/augur_local_ai_route_b_no_gpu_plan_20260726.md`（§十二）  
> **可選矩陣短檔**：`reports/augur_dual_self_evolution_interface_20260726.md`  
> **一句**：兩個閉環、兩本帳、兩組晉升閘；**只共享通知與唯讀摘要契約**——不混管線、不共享 APPLY／serving 閘、禁 LLM 權重進預測特徵。

### 8.1 正交矩陣（禁混）

| | 本計畫（TWEVO） | 路線 B（LAIEVO） |
|---|---|---|
| 進化對象 | **預測特徵／prodset／模型／arena paper** | advisor／MCP **LLM** prompt-pack／蒸餾 |
| 表 | `evolution_*`／`feature_*`／`model_registry`／arena | `local_model_*`／`advisor_distill_*`／`lora_*`／`local_ai_iteration_ledger` |
| 晉升閘 | PME 雙綠＋kill＋**TWEVO-APPLY** 人開 | `local_model_version` **人簽** serving；`evolve_cycle` 永不自晉升 |
| 禁入對方 | LLM 權重、SFT jsonl、teacher 答 | `feature_values`／prodset／預測 7 package／未過閘 IC |
| 可並行 | ✅ 同機可並行 | ✅ 須錯峰（§8.4） |

兩案**不得**互相當依賴：預測閉環不因「8b 變聰明」放行；LLM 進化不因雙綠↑而寫入特徵。

### 8.2 預測 → advisor（只讀摘要契約）

| 允許進 advisor 檢索／few-shot | 禁止 |
|---|---|
| **iteration ledger 結論文**：`status`／`stop_reason`／`gain_basis`／`dual_green_n`／`prodset_active_n`／`trigger_code`（#15 溯 ledger 列） | 整段 `feature_values`／`feature_candidate_values`／raw panel |
| **閘失敗近失候選名**：`near_miss_json[].feature`＋gate／reason（名級） | 未過閘 IC／Sharpe／「即將晉升」話術當確立級 |
| **arena scoreboard 公開數字**：已 settle 之 paper 指標＋as-of＋出處 script（真兆） | 把 scoreboard 說成可交易／門二已過（`evaluated_pass=0` 仍禁） |
| **gap／診斷報告路徑**（人審後 markdown） | 整庫列舉、靈魂文書灌 raw（`soul-vs-raw-correlation`） |
| **MAP／D2 狀態一句**：如「MAP-E012 CLOSED；D2 第一關過、multi-seed SKIP」 | probe 數字當雙綠／可 APPLY |

**匯出入口（拍板後）**：`export_evolution_advisor_brief.py --iteration-id N --out PATH` → 寫 `advisor_brief_path`；產物可進 advisor 檢索 scope（**非** knowledge 晉升、**非** citation 權威）。  
**消費端（LAIEVO）**：僅允許 brief／報告 path 進 gold 題庫或 pack 選材之**情境註記**；`is_synthetic`／provenance 須標 `prediction_brief`；**不得**洗成真人知識（P4.E7）。

### 8.3 advisor／蒸餾 → 預測（假說文字 only）

| 允許 | 禁止 |
|---|---|
| **假說文字**／哲學 map **curate 提示**（列建議原則↔特徵名、文獻錨） | advisor／teacher／LoRA **輸出直接**改 `evolution_production_feature_set` |
| 人審後走既有 `curate_pme_map_expand.py`／MAP 計畫入 `principle_factor_map` | 降 G-PROM／G-ECON 閾、ECON-only APPLY、手改 validated_* |
| | 以 LLM 分數當 G-PROM／#14 證據；權重／embedding 當特徵 |

**路徑**：LAIEVO `hypothesis_hints_out` → Steward 人閘 →（可選）`TWEVO` I0 curate → 再進 I3 local-gates。**無跳閘捷徑**。

### 8.4 共享節奏／kill 通知／本週儀表

| 機制 | 規則 |
|---|---|
| **錯峰** | 重負載互斥建議窗：TWEVO `I3 local-gates`／`I6 train_ranker` **∥** LAIEVO `embed`／B2 QLoRA／B3 CPU LoRA——同機不同時滿載；driver 可讀對方 ledger `status=running`＋`axis` 決定 `--defer-heavy` |
| **共享 kill／停損通知** | 各方寫自己的 `cross_notify_json`；對偶側 **只讀告警**（stdout／週報），**不**連鎖自動 halt serving 或自動 APPLY。PME `evolution_kill_switch=halt` → TWEVO 拒 I5；LAIEVO 可選人工暫停 B2/B3（預設不自動） |
| **本週迭代儀表** | `report_dual_evolution_week.py`：**並列**最近 TWEVO／LAIEVO ledger 列（狀態／增益／停損／brief path）；**禁** UNION 成單表業務 SSOT |

### 8.5 拍板碼交叉（何時同批／何時分開）

| 可同批拍 | 必須分開 |
|---|---|
| `TWEVO-P-yes`＋`LAIEVO-P-yes`（＋可選介面採納） | `TWEVO-APPLY-go` ≠ 任何 `LAIEVO-*-go` |
| `FZ-keep`＋`GATE-keep`（兩軸共用紅線重申） | `TWEVO-S3/S4`（突變 prodset／arena）≠ `LAIEVO-B2-train`／`B3`（訓權重） |
| `TWEVO-S0/S1`＋`LAIEVO-B0`（盤點／DDL 唯讀核對） | 人簽 serving（LAIEVO）≠ PME APPLY（TWEVO） |
| `TWEVO-S2`（無 APPLY）∥ `LAIEVO-B1`／`B4`（pack／gold；錯峰 embed） | 任一方停損 N 改碼（`TWEVO-N`／`LAIEVO-STOP-N`）各改各的 |

**建議首批（雙軸）**：`TWEVO-P-yes`＋`LAIEVO-P-yes`＋`FZ-keep`＋`GATE-keep` → 再分軸 `TWEVO-S0-go`／`LAIEVO-B0`（或 B1）。

---

## 9. 風險與誠實預期

* **雙綠仍可能長期＝2**：MAP 擴大與 D2 第一關≠雙綠；成功＝可追溯否證＋零假綠。  
* **arena paper ≠ 經濟可交易**：#14／門二另算。  
* **local-gates 壁鐘長**：driver 須 resume；勿於 session 內輪詢耗 usage（#28）。  
* **名實不符債**：`lending_fee_rate_mean_30d`（非真 30d） vs D2 真窗候選 — 回饋 map 時須標窗口語意，避免假對齊。
* **對偶洩漏風險**：brief 寫太肥 → 變相灌 panel；緩解＝V8＋export allowlist 欄位鎖。

---

## 10. 建議拍板碼

| 碼 | 含義 |
|---|---|
| **`TWEVO-P-yes`** | 採納本計畫為執行藍圖（仍不自動開工） |
| **`TWEVO-S0-go`** | 開盤點 |
| **`TWEVO-S1-go`** | 開 DDL migrate |
| **`TWEVO-S2-go`** | 開 driver（至閘／回饋；無 APPLY） |
| **`TWEVO-S3-go`** | 開 APPLY＋重訓掛接 |
| **`TWEVO-S4-go`** | 開 arena／settle 掛接 |
| **`TWEVO-S5-go`** | 開停損／gain 自動化 |
| **`TWEVO-APPLY-go`** | 允許**指定 iteration** 執行 I5（可與 S3 同令或分令） |
| **`TWEVO-U-go`** | 開對抗審查 |
| **`FZ-keep`** | 維持 API 凍結（建議與上列同批重申） |
| **`GATE-keep`** | 不降閘（建議同批重申） |
| **`TWEVO-N=3`** | 無增益停損輪數（可改數字） |
| **`DUAL-IFACE-yes`** | （可選）採納 §8／雙軸介面短檔為協作契約 |

**建議首批**：`TWEVO-P-yes` ＋ `LAIEVO-P-yes` ＋ `DUAL-IFACE-yes` ＋ `FZ-keep` ＋ `GATE-keep`；實作碼逐步分軸開（§8.5）。

---

## 11. 執行前四判準（G-P4 自檢；開 S1 碼前勾）

| # | 判準 | 本檔 |
|---|---|---|
| ① 完整 | §4 schema＋§5 python＋§3 流程＋§6 停損＋§7 分階＋§2 硬邊界＋§8 對偶介面 | ✅ |
| ② 內部一致 | AUTO-B 與「人開 APPLY 步」已相容說明；FZ／GATE 無矛盾；對偶不共享晉升閘 | ✅ |
| ③ 與現況一致 | 引用 prodset n=2、MAP-E012、D2 第一關、P2H DONE、`evaluated_pass=0` | ✅ |
| ④ 可實作 | driver＝subprocess 編排既有 script；新表一張為主；brief／週報可選 | ✅ |

---

## 12. 參考索引（精簡）

* HANDOFF.md §4.0（PME／P2H／MAP／凍結）  
* `reports/augur_philosophy_market_evolution_loop_plan_20260724.md`  
* `reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md`  
* `reports/augur_gprom_d2_probe_20260724.md`  
* `reports/augur_pme_gap_ledger_20260724.md`  
* `reports/augur_local_ai_route_b_no_gpu_plan_20260726.md`（對偶；§十二）  
* `reports/augur_dual_self_evolution_interface_20260726.md`（可選介面矩陣）  
* `scripts/run_philosophy_evolution.py`／`apply_evolution_promotions.py`／`train_ranker.py`／`predict_asof.py`／`verify_prodset_hotpath.py`／`run_arena_daily_pipeline.py`／`settle_arena_labels.py`／`run_revalidation_cycle.py`／`evolve_cycle.py`（對偶；禁混入口）  
* `src/augur/philosophy/evolution.py`（DDL＋DEFAULT_GATE_CONFIG）  
* `.cursor/rules/predict-vs-market-api.mdc`／`finmind-fred-api-freeze.mdc`／`soul-vs-raw-correlation.mdc`

---

*本檔完。拍板前不實作；位階 [I]。*
