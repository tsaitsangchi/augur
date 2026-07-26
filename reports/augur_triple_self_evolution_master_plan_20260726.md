# 三軸自進化總控計畫（RAWEVO × TWEVO × LAIEVO）[I]（2026-07-26）

> **採納狀態**：APPROVED-NO-EXEC 2026-07-26 → `audits/TRI-SELF-EVO-PLANS-APPROVED-NO-EXEC-20260726.md`（`TRI-P-yes`＋`TRI-IFACE-yes`＋三軸 `*-P-yes`＋`FZ-keep`＋`GATE-keep`；**未開執行**）
> **性質**：[I] plan-first 總控／交互計畫書（CLAUDE #16／#20；領域大憲章第六部計畫完整性 v1.39.0）——**不創設 [N]**、**拍板前零實作**、零市場 API（FZ-keep）、不降閘（GATE-keep）。
> **定位**：`augur_dual_self_evolution_interface_20260726.md`（DUAL-IFACE）之**升格版**——雙軸 → **三軸**；本檔取代該短檔成為介面契約 SSOT。
> **本檔管什麼**：三軸之間的**命名、契約、節奏、通知、儀表、拍板碼**。
> **本檔不管什麼**：任一軸的內部細節——**各軸子計畫仍為該軸 SSOT**（見 §0.2）。**衝突時以「更嚴邊界」為準**（§0.3）。

---

## 0. 一句總覽與位階

### 0.1 一句總覽

**三軸自進化＝一個地基、兩個上層閉環，三本帳、三組閘、一張節奏表**：

**RAWEVO（資料地基：raw／覆蓋／缺口／欄位交互）→ 只出「事實帳＋人閘前假說提示」→ 上餵 TWEVO（預測模擬：假說 map→候選→local-gates→雙綠→人開 APPLY→重訓→arena paper→回饋）與 LAIEVO（本地 advisor LLM：gold→prompt-pack→可測增益→人簽 serving→回饋）；三軸只共享唯讀摘要契約、跨軸通知、單機重活錯峰，不共享帳本、不共享晉升閘、不互為前提。**

### 0.2 各軸 SSOT（本檔一律引用、不複印）

| 軸 | 標的 | 子計畫（SSOT） | 拍板碼族 |
|---|---|---|---|
| **RAWEVO** | 全庫 84 張 raw 表：覆蓋／freshness／缺口分類／欄位交互假說 | `reports/augur_raw_data_self_evolution_loop_plan_20260726.md` | `RAWEVO-*` |
| **TWEVO** | 台股**預測模擬**：特徵／prodset／模型／arena paper | `reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md` | `TWEVO-*` |
| **LAIEVO** | 本地 advisor／MCP LLM：gold／prompt-pack／可選 LoRA | `reports/augur_local_ai_route_b_no_gpu_plan_20260726.md` | `LAIEVO-*`（舊別名 `ROUTEB-*`） |
| **介面** | 三軸交互（本檔） | 本檔（升格自 `augur_dual_self_evolution_interface_20260726.md`） | `TRI-*` |

**承接關係（只標關係、不重述內容）**：PME 母計畫＝`reports/augur_philosophy_market_evolution_loop_plan_20260724.md`（TWEVO 的閘／佇列／AUTO-B 出處，已拍板已開）；本地 AI 進化終稿＝`reports/augur_local_ai_evolution_loop_plan_20260725.md`（LAIEVO 的 Tier1／Tier2 出處，自對弈永動機與 4b GPU QLoRA **已擊倒、不重提**）。

### 0.3 衝突裁決句

> 本檔與任一子計畫敘述衝突時：**取更嚴的邊界**（更晚放行、更少自動、更小輸出面）；若「更嚴」不可判定 → **停下問 Steward**，不由 AI 自選寬鬆解。本檔**不得**被引為放寬任一軸原有硬邊界之依據。

---

## 1. 「已讀記住」摘要表（三軸錨點）

| | **RAWEVO** | **TWEVO** | **LAIEVO** |
|---|---|---|---|
| **閉環一句** | 盤點 profile → 覆蓋／freshness 對帳 → 缺口分類（真缺／凍結致缺／schema／語意）→ 欄位交互假說候選 → **人閘分流** → 回寫帳本 | 假說 map → 候選建值（隔離表）→ local-gates → 雙綠 → **人開本輪 APPLY** → prodset 重訓 → as-of 模擬／arena → 結算 → 證據回饋 | gold／題庫累積 → `evolve_cycle` prompt-pack → 可測增益 → **人簽 serving** →（可選）1.7b QLoRA／CPU LoRA → 驗證／回滾 → 回饋下一輪 |
| **現況錨（2026-07-26）** | 248 表／**84 張 raw** 100% 登錄 `dataset_catalog`；多數 max(date)=07-23/24；`ExchangeRate` 停在 2020-11-13、`USStockPrice`／`GovernmentBondsYield` 落後、`TaiwanFutOptTickInfo` date 為字串、`TaiwanStockDividend` 2,411 列（G-DIV 另帳） | prodset **active n=2**；雙綠僅 `inst_cumflow_position_120d`／`volume_gini_60d`；MAP-E012 CLOSED（17→35）未跑 S3；G-PROM-D2 借券真窗第一關過（multi-seed／G-ECON SKIP）；P2H DONE；`direction_gate.evaluated_pass=0` | Ollama 0.32.1 **單實例**：advisor `qwen3:8b`、MCP `qwen3:4b`、`nomic-embed-text`；GTX 1650 **4GB**（idle free ~2.7GB）；蒸餾 pilot 171 條（drop 37.6%）；Tier1 prompt-pack 已落地於 `evolve_cycle.py` |
| **新表／driver** | `raw_table_coverage_snapshot`＋`raw_evolution_iteration_ledger`；`scripts/run_raw_evolution_iteration.py`（R0–R5） | `evolution_iteration_ledger`（＋可選 `evolution_iteration_step`）；`scripts/run_evolution_iteration.py`（I0–I9） | `local_ai_iteration_ledger`＋`lora_training_run`；`scripts/close_local_ai_iteration.py`＋（B2/B3）`train_qlora_small.py`／`train_lora_cpu.py` |
| **晉升閘** | **無晉升閘**（只出帳與提示） | PME 雙綠 ∧ kill=clear ∧ **本輪 `apply_allowed`** | `local_model_version` candidate → **人簽** `promoted_by` → serving |
| **停損 N** | N=2（`RAWEVO-STOP-N=k`） | N=3（`TWEVO-N=3`） | N=2（`LAIEVO-STOP-N=k`） |
| **拍板碼前綴** | `RAWEVO-` | `TWEVO-` | `LAIEVO-`／`ROUTEB-` |
| **硬邊界（軸內最嚴句）** | 零 API；發現缺口只**記帳不補**；raw 不升格靈魂；不寫 `feature_values`／prodset／gold | GATE-keep 不降閾；SKIP≠PASS；APPLY≠交易；`evaluated_pass=0` 禁確立級；候選只寫 `feature_candidate_values` | 權重／SFT／帳本 `owned_local` 不入 git；只本機 Ollama；4GB 硬限（禁 >~2.5GB 配方）；**訓過≠變聰明**；禁自動 cutover |

---

## 2. 升格介面：dual → triple

### 2.1 三方正交矩陣（誰能碰誰）

| 寫入端 ↓／目標 → | raw 表／catalog | `feature_values`／prodset／`promotion_queue` | `local_model_version`／gold／pack | 三軸各自 ledger |
|---|---|---|---|---|
| **RAWEVO** | **唯讀**（快照落自己的表；catalog 回填須人閘） | ❌ 禁 | ❌ 禁 | 只寫 `raw_*` |
| **TWEVO** | 唯讀消費 panel／features | ✅ 職權（閘內＋人開輪） | ❌ 禁 | 只寫 `evolution_iteration_ledger` |
| **LAIEVO** | ❌ 不消費 raw 列 | ❌ 禁 | ✅ 職權（人簽 serving） | 只寫 `local_ai_iteration_ledger` |

### 2.2 允許流向（三邊）

| 方向 | 允許內容 | 入口／落點 | 閘 |
|---|---|---|---|
| **RAW→TW** | 缺口帳結論句（「X 表凍結致缺至 D 日」＝I1 建值窗依據）；R4 **已批**假說提示（欄位對＋方向＋出處＋n_obs） | `hint/1` → TWEVO ledger `hints_in`（新欄，§4.2）→ 人 → `curate_pme_map_expand` | **R4 人閘**；無自動橋 |
| **RAW→LAI** | 覆蓋結論句／語意缺口（`dirty_value` 候選）作 gold **情境註記** | `brief/1`（kind=`rawevo_brief`）→ LAIEVO `consumed_briefs` | 人審選材；P4.E7 標 synthetic |
| **TW→LAI** | ledger 結論欄、閘失敗**近失特徵名**、已 settle scoreboard 公開數（標 as-of＋出處） | `brief/1`（kind=`prediction_brief`）→ LAIEVO `consumed_briefs` | export allowlist；禁 panel |
| **LAI→TW** | 假說文字／建議 map 對（文獻錨） | `hint/1` → 人閘 → `curate_pme_map_expand` | **Steward 人閘**；無自動橋 |
| **TW／LAI→RAW** | 「缺資料」訴求 → 下輪 R1 加掃該表 | RAWEVO ledger `notes`／開輪參數 | 無 |
| **任一→全體** | 停損／kill／defer 告警 | `xnotify/1` → `evolution_cross_notify`（新輕量表，§4.3） | **只讀告警，不連鎖自動閘** |
| **儀表** | 三 ledger **並列** | `scripts/report_triple_evolution_week.py`（唯讀） | 不合併成業務 SSOT |

### 2.3 禁項清單（三軸共同紅線；違反即停手問）

1. **混帳本**：三 ledger 不得合併、不得共用 iteration id 命名空間、不得以 UNION 結果當業務 SSOT（唯讀儀表 view 例外且不可被寫入路徑 join）。
2. **直 APPLY**：任何非 TWEVO 職權者（含 advisor／teacher／LoRA 輸出、RAWEVO hint、LLM 分數）**不得**直接寫 `evolution_production_feature_set`／`promotion_queue`／呼叫 `apply_evolution_promotions`。
3. **降閾／挪門柱**：不降 `DEFAULT_GATE_CONFIG`（`min_abs_hac_t=2`／`min_seeds=3`／`min_delta_ic=0`／G-ECON cost=0.00585／MaxDD 地板）；不改 LAIEVO 三 hash 錨；SKIP≠PASS；ECON-only 禁晉升。
4. **raw 灌靈魂**：整庫 raw／全市場列舉／快照列**不得**寫進靈魂、原則精華或任何 [N]；可升格者唯「交互抽象出的概念與可證偽關係」，且走人閘。
5. **解凍 API**：三軸皆零 FinMind／FRED；缺口帳、假說燃料、預測需求**均不得**作為解凍論據（INV2 仍須 Steward 明示）。
6. **跨軸連鎖自動化**：一軸 kill／停損**不得**自動改對偶的 serving／prodset／開輪；只寫通知。**唯一例外**＝人發的 `TRI-HALT`（§3.4），且機械上只擋「開新輪」，不改任何既有狀態。
7. **假增益**：hint 數／brief 數／gold 條數／輪次數**不是**增益；各軸 gain 只能由自己的 `gain_basis` 白名單裁定，儀表禁自算。
8. **自動下單**：靈魂紅線，三軸皆禁。

---

## 3. 細化與交互優化（相對三份子計畫的**增量**）

> 本節是本檔存在的理由：以下 7 項在任一子計畫中**都不存在或不一致**，屬三軸並存後才浮現的問題。

### 3.1 統一 iteration 命名（增量：三軸 uid 對不上）

**問題（M0 實錄）**：TWEVO `iteration_id BIGSERIAL`（純整數）／LAIEVO `text 'laievo-20260726-r03'`／RAWEVO `varchar 'rawevo_0001'` — 三者型別與格式皆異，**跨軸引用一個整數 3 無法判斷是哪軸**，brief／hint／notify 全部失去可溯性。

**契約**：三 ledger 各**新增一欄** `iteration_uid TEXT NOT NULL UNIQUE`（不改各自 PK，零遷移風險）：

```
iteration_uid ::= <axis>-<YYYYMMDD>-r<NN>
axis ∈ {tw, lai, raw}          NN ∈ 01..99（該日該軸序號，零填）
regex: ^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$
```

**規則**：(a) 跨軸引用**一律**用 `iteration_uid`，禁用裸 PK；(b) 三軸命名空間互斥由 regex 前綴保證，可 SQL 機械驗（T-V1）；(c) 同日重開輪遞增 NN，不重用。

### 3.2 三份最小 JSON 契約（增量：三檔各自散寫欄位語意，無 schema 版本）

**共同規則**：每份契約首欄 `schema` 帶版本；未知欄位**拒絕**（fail-closed，非忽略）；產生端與消費端共用同一 validator（§5.3）；三契約皆**禁**內含 panel／raw 列陣列。

**(1) `xnotify/1` — 跨軸通知**

```json
{
  "schema": "xnotify/1",
  "from_axis": "TW",
  "from_iteration_uid": "tw-20260729-r01",
  "scope": "axis",
  "event": "stop_no_gain",
  "severity": "warn",
  "raised_at": "2026-07-29T18:04:11+08:00",
  "raised_by": null,
  "detail": {"reason": "連續 3 輪無雙綠", "evidence_ref": "reports/augur_pme_gap_ledger_20260724.md"}
}
```
`event ∈ {kill_halt, stop_no_gain, halted, defer_heavy, resumed, tri_halt}`；`severity ∈ {info, warn, halt}`；`scope ∈ {axis, global}`；`tri_halt` 必為 `scope=global` ∧ `severity=halt` ∧ `raised_by` 非空（人）。

**(2) `brief/1` — 唯讀摘要（RAW→LAI／TW→LAI／RAW→TW 結論句）**

```json
{
  "schema": "brief/1",
  "kind": "prediction_brief",
  "source_iteration_uid": "tw-20260729-r01",
  "as_of": "2026-06-30",
  "generated_at": "2026-07-29T18:10:00+08:00",
  "claims": [
    {"text": "本輪 local-gates 無新雙綠；prodset active 維持 2",
     "claim_level": "ledger_fact",
     "evidence": {"table": "promotion_queue", "run_id": 7, "script": "run_philosophy_evolution.py"}}
  ],
  "names_only": ["lending_fee_rate_mean_20d"],
  "sha256": "…"
}
```
`kind ∈ {prediction_brief, rawevo_brief}`；`claim_level ∈ {ledger_fact, paper, gap_debt}` — **無** `established`／`tradable` 值（措辭閘由型別鎖，不靠自律）；`claims ≤ 20`；`names_only` 只放名稱字串；**禁**數值陣列、禁 `feature_values`／快照列。

**(3) `hint/1` — 假說提示（RAW→TW／LAI→TW）**

```json
{
  "schema": "hint/1",
  "hint_id": "raw-20260727-r01#h03",
  "from_axis": "RAW",
  "from_iteration_uid": "raw-20260727-r01",
  "hint_text": "借券費率與法人買賣超於 T+1 呈負向 lead-lag，建議檢視為『擁擠度』假說載體",
  "suggested_map": {"principle": null, "fields": ["lending_fee_rate", "inst_net_buy"]},
  "provenance": {"kind": "field_correlation_diff", "refs": ["field_return_leadlag"], "n_obs": 12843},
  "dedup_key": "lending_fee_rate|inst_net_buy|neg|leadlag",
  "human_gate": {"decision": "pending", "by": null, "at": null, "code": null}
}
```
**閘規則**：`human_gate.decision ∈ {pending, approved, data_debt_only, rejected}`；**只有 `approved`** 方可進 `curate_pme_map_expand`；`by`／`code` 由人填（`RAWEVO-HINT-approve <ids>`／Steward 句），**腳本禁自填**。
**去重（增量）**：`dedup_key` 跨軸唯一——防 RAWEVO R3 與 LAIEVO `hypothesis_hints_out` 產出同一組欄位對，造成「hint 變多＝有進展」的 Goodhart 假增益。

### 3.3 建議執行節奏（增量：三軸各自寫 cadence，未對單機資源做全域排程）

**單機事實**：一台 WSL2（Ryzen 5 3600／24GB／GTX 1650 4GB／單一 Ollama 實例／同一 PostgreSQL）。三軸「重活」互斥：

| 重活 slot | 屬軸 | 典型壁鐘 | 資源 |
|---|---|---|---|
| `R3` field_correlation 全量 | RAW | ~30 分鐘級 | CPU＋PG |
| `I3` local-gates | TW | 25–35 分 | CPU＋PG |
| `I6` train_ranker | TW | 分鐘～十分鐘級 | CPU＋PG |
| `embed`／B2 QLoRA／B3 CPU LoRA | LAI | 分鐘～**天**級 | Ollama／GPU／RAM |

**週節拍建議（可 `TRI-CADENCE-yes` 採納，或維持全手動）**

| 日 | 內容 | 重活 | 產出 |
|---|---|---|---|
| 一 | RAWEVO `R0–R2`（庫內唯讀 ~10 分） | 否 | 覆蓋快照＋缺口分類 |
| 二 | RAWEVO `R3` → hints → **R4 人閘** | ✅ RAW | `hint/1`（approved 子集）＋`brief/1` |
| 三 | TWEVO 一輪 `I0–I4, I8`（吃週二 approved hints） | ✅ TW `I3` | ledger 列＋近失＋`brief/1` |
| 四 | 有雙綠且已拍板 → TWEVO `I5–I7` APPLY 子輪；否則空出給 LAI | ✅ TW `I6` | prodset delta／model_id／arena paper |
| 五 | LAIEVO `B1`／`B4`（pack／gold；embed 重活） | ✅ LAI | candidate version＋eval |
| 六～日 | LAIEVO `B2`／`B3` 長窗（僅在該週無 TW APPLY 子輪時）；週日跑週儀表 | ✅ LAI | 訓練 run＋週報 |

**機械互斥（增量，取代「讀對方 ledger status」的競態作法）**：所有重活 step 進入前取 **PostgreSQL advisory lock**
`SELECT pg_try_advisory_lock(hashtext('augur_evolution_heavy_slot'))` — 取不到 → 寫 `xnotify/1{event:defer_heavy}` 並依旗標 `--defer-heavy` 跳過該 step（**不算無增益輪**，承 TWEVO §6.3／RAWEVO §7.3），或 `--wait-heavy N` 等待。鎖釋放於 step 結束（含失敗路徑）。
**與 MCP 的銜接一句**：heavy slot 期間 Ollama 單實例吞吐被佔，`local-llm` MCP（`qwen3:4b`）回應會顯著變慢——該窗內 agent 側應改走 `constitution-mcp`／直接讀檔，勿以 `local_research` 反覆重試（`.cursor/rules/local-mcp-routing.mdc` 之實務補充）。

### 3.4 跨軸 kill 語意分層（增量：三軸各有停，無總停）

| 層 | 機制 | 效力 | 誰能發 |
|---|---|---|---|
| 軸內 kill | TW＝`evolution_kill_switch=halt`（拒 I5）；LAI＝拒晉升／`status=stopped`；RAW＝driver `halted` | 只影響該軸 | 人／該軸機械條件 |
| 跨軸告警 | `xnotify/1`（`severity∈{info,warn}`） | **僅告警**，對偶只讀 | 任一軸 driver |
| **`TRI-HALT`（新）** | 人寫入 `evolution_cross_notify`（`event=tri_halt`, `scope=global`, `raised_by=<人>`）；三軸 driver 啟動前檢查未 `cleared_at` 的 global halt → **拒開新輪**（rc≠0，graceful 訊息） | 擋新輪；**不**改 serving／prodset／既有 run | **只有 Steward**（腳本禁寫） |

`TRI-HALT` 不違反「禁跨軸自動連鎖」：源頭是人，機械只做最小面（擋開輪）。解除＝人填 `cleared_by`／`cleared_at`。

### 3.5 三 ledger 欄位對齊建議（增量：同構不同名，先對齊再落地＝零成本）

三軸新表**皆未實作**，現在對齊成本為零；落地後再改＝遷移債。

| 語意 | TWEVO 現規劃 | LAIEVO 現規劃 | RAWEVO 現規劃 | **本檔建議** |
|---|---|---|---|---|
| 跨軸識別 | （無） | （無） | （無） | **三軸皆加 `iteration_uid`**（§3.1） |
| 停損計數 | `consecutive_no_gain` | `consecutive_no_gain` | `no_gain_streak` | RAWEVO 改名 **`consecutive_no_gain`** |
| 收到的摘要 | （無，只有 `advisor_brief_path`） | `consumed_briefs` | （無） | 三軸皆備 **`briefs_in JSONB`**（`brief/1` 陣列）；TWEVO 需要它才收得到 RAWEVO 缺口帳 |
| 送出的摘要 | `advisor_brief_path`（單值） | （無） | `briefs_out` | 三軸皆備 **`briefs_out JSONB`**；TWEVO 保留 `advisor_brief_path` 為冗餘便利欄 |
| 收到的假說 | （無） | （無） | （無） | **TWEVO 加 `hints_in JSONB`**（記本輪 I0 採用之 approved `hint_id`）——否則「假說從哪來」斷鏈，三軸因果不可溯 |
| 送出的假說 | （無） | `hypothesis_hints_out` | `hypothesis_hints_out` | 維持同名 |
| 跨軸通知 | `cross_notify_json` | `cross_notify_json` | `cross_notify_json` | 維持（各軸本地鏡射）＋**共用佈告欄表**（§4.3） |
| 終態語彙 | `planned/running/succeeded/failed/halted/stopped_no_gain` | `open/closed_gain/closed_no_gain/stopped/aborted` | `running/closed_no_finding/closed_findings/halted` | **不強行合併**（各軸語意真的不同）；改以唯讀 view 映射（§4.4） |

> **注意**：以上為**建議**，各軸 DDL 之最終文字仍由各軸子計畫 SSOT 定案；本檔只要求「M1 前完成對齊或明示拒絕理由」。

### 3.6 與現況的銜接（三句，避免總檔與地面脫節）

* **G-PROM-D2**：借券真窗候選（`lending_fee_rate_mean_20d` 2.63／`lending_fee_vw_mean_20d` 2.94）第一關已過、multi-seed／G-ECON 仍 SKIP → 屬 **TWEVO I2 既有彈藥**；RAWEVO R3 若產出同組欄位對，須以 `dedup_key` 命中既有帳、標 `duplicate_of`，**不得**當本輪新發現。
* **prodset n=2**：三軸首季**誠實預期 n 仍可能＝2**；週儀表「增益」欄只鏡射各軸 `gain`／`gain_basis`，禁以輪數／hint 數／gold 數充數（§2.3.7）。
* **Ollama 單實例**：advisor 8b 與 MCP 4b 共用同一 Ollama；LAIEVO 重活期間 advisor 變慢屬預期並須在週報標註，**不得**以「advisor 變慢」為由關閉 LAIEVO 帳本紀律或跳過評測。

### 3.7 合併拍板碼建議（見 §7 完整表）

`TRI-P-yes`（採納本總控檔）＋`TRI-IFACE-yes`（三軸介面契約生效，`DUAL-IFACE-yes` 視為其前身／等價舊別名）＋三軸 `*-P-yes`＋`FZ-keep`＋`GATE-keep` 可**同批**；任何 `*-go`（實作／跑輪）與人簽晉升類**分開**。

---

## 4. (a) Table schema

### 4.1 所讀既有表（唯讀；DDL 住所不變）

| 表群 | 住所／SSOT | 本檔角色 |
|---|---|---|
| `evolution_run`／`promotion_queue`／`evolution_apply_log`／`evolution_kill_switch`／`evolution_production_feature_set`／`evolution_coverage_snapshot` | `src/augur/philosophy/evolution.py` | 唯讀（週儀表／契約驗證） |
| `feature_values`／`feature_candidate_values`／`model_registry`／`prediction_values`／`direction_arena_*`／`trial_ledger` | 既有 migrate 腳本 | 唯讀 |
| `dataset_catalog`／`column_catalog`／`attestation_result`／`field_correlation`／`field_return_leadlag`／`field_lens_map` | 既有 | 唯讀（RAWEVO 附錄 A 為本檔引用之現況來源，本檔**不重掃** 248 表） |
| `local_model_version`／`local_model_gold_sample`／`advisor_distill_*` | `scripts/migrate_ai_evolution_ddl.py`／`migrate_advisor_distill_ddl.py` | 唯讀 |

### 4.2 三 ledger（各軸 DDL 為 SSOT；本檔只給統一欄位對照）

完整 DDL 見：TWEVO §4.2（`evolution_iteration_ledger`）／LAIEVO §4.4（`local_ai_iteration_ledger`）／RAWEVO §4.3（`raw_evolution_iteration_ledger`）。本檔要求之**增補欄位**（M1 前併入各軸 migrate 腳本，不另開表）：

```sql
-- 三軸各自的 migrate 腳本內冪等追加（示意；axis 表名依各軸 SSOT）
ALTER TABLE <axis_ledger> ADD COLUMN IF NOT EXISTS iteration_uid TEXT;
ALTER TABLE <axis_ledger> ADD COLUMN IF NOT EXISTS briefs_in  JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE <axis_ledger> ADD COLUMN IF NOT EXISTS briefs_out JSONB NOT NULL DEFAULT '[]'::jsonb;
-- TWEVO 專屬：假說來源可溯
ALTER TABLE evolution_iteration_ledger ADD COLUMN IF NOT EXISTS hints_in JSONB NOT NULL DEFAULT '[]'::jsonb;
-- 命名空間鎖（三軸皆加）
ALTER TABLE <axis_ledger> ADD CONSTRAINT <axis>_uid_fmt
  CHECK (iteration_uid ~ '^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$');
CREATE UNIQUE INDEX IF NOT EXISTS ux_<axis>_iteration_uid ON <axis_ledger> (iteration_uid);
```

### 4.3 新表（本檔唯一新增）：`evolution_cross_notify`

**角色**：三軸唯一**佈告欄**——只增不改業務語意；**不得**由本表自動觸發任何狀態變更（唯一機械效力＝`tri_halt` 擋開新輪，§3.4）。各軸 ledger 的 `cross_notify_json` 保留為本地鏡射，便於單軸自查。

```sql
CREATE TABLE IF NOT EXISTS evolution_cross_notify (
  notify_id          BIGSERIAL PRIMARY KEY,
  schema_version     VARCHAR(16) NOT NULL DEFAULT 'xnotify/1',
  from_axis          VARCHAR(8)  NOT NULL,          -- TW|LAI|RAW|HUMAN
  from_iteration_uid TEXT,                          -- regex 同 §3.1；HUMAN 可空
  scope              VARCHAR(16) NOT NULL DEFAULT 'axis',   -- axis|global
  event              VARCHAR(32) NOT NULL,          -- kill_halt|stop_no_gain|halted|defer_heavy|resumed|tri_halt
  severity           VARCHAR(8)  NOT NULL,          -- info|warn|halt
  detail             JSONB NOT NULL DEFAULT '{}'::jsonb,   -- {reason, evidence_ref, ...}
  raised_by          VARCHAR(64),                   -- 人發（tri_halt）必填；腳本發為 NULL
  raised_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  acked_json         JSONB NOT NULL DEFAULT '[]'::jsonb,   -- [{axis, at, action:noted|deferred}]
  cleared_at         TIMESTAMPTZ,
  cleared_by         VARCHAR(64),
  CHECK (from_axis IN ('TW','LAI','RAW','HUMAN')),
  CHECK (scope IN ('axis','global')),
  CHECK (severity IN ('info','warn','halt')),
  CHECK (event IN ('kill_halt','stop_no_gain','halted','defer_heavy','resumed','tri_halt')),
  CHECK (from_iteration_uid IS NULL
         OR from_iteration_uid ~ '^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$'),
  -- 全域停機只能是人發的 halt
  CHECK (event <> 'tri_halt'
         OR (scope = 'global' AND severity = 'halt' AND raised_by IS NOT NULL)),
  CHECK ((cleared_at IS NULL) = (cleared_by IS NULL))
);

CREATE INDEX IF NOT EXISTS ix_xnotify_open
  ON evolution_cross_notify (severity, raised_at DESC) WHERE cleared_at IS NULL;
CREATE INDEX IF NOT EXISTS ix_xnotify_axis
  ON evolution_cross_notify (from_axis, raised_at DESC);

COMMENT ON TABLE evolution_cross_notify IS
  '三軸自進化跨軸佈告欄 [I]；只讀告警＋人發 tri_halt 擋開輪；禁自動連鎖改 serving/prodset/APPLY';
```

**Migrate 入口（拍板後）**：`scripts/migrate_evolution_cross_notify_ddl.py`（`--check`／`--apply`／`--dry-run`／`--selftest`；#18／#29 矩陣）。
**禁刪語意**：與 gold／`lora_training_run` 同精神——失敗與告警留檔；清除＝填 `cleared_*`，不 DELETE（trigger 於 migrate 腳本內落地）。

### 4.4 唯讀儀表 view（可選，M1 尾）：`v_evolution_iteration_unified`

**只給週儀表用；非 SSOT；禁任何寫入路徑 join。** 三表皆存在才建（migrate 腳本內以 `to_regclass` 三判）。

```sql
CREATE OR REPLACE VIEW v_evolution_iteration_unified AS
SELECT 'TW'::text AS axis, iteration_uid, started_at AS opened_at, finished_at AS closed_at,
       CASE status WHEN 'running' THEN 'running' WHEN 'planned' THEN 'running'
                   WHEN 'succeeded' THEN 'closed' WHEN 'failed' THEN 'closed'
                   WHEN 'halted' THEN 'halted' ELSE 'stopped' END AS status_canon,
       trigger_code, consecutive_no_gain, cross_notify_json
FROM evolution_iteration_ledger
UNION ALL
SELECT 'LAI', iteration_uid, opened_at, closed_at,
       CASE status WHEN 'open' THEN 'running' WHEN 'stopped' THEN 'stopped'
                   WHEN 'aborted' THEN 'halted' ELSE 'closed' END,
       trigger_code, consecutive_no_gain, cross_notify_json
FROM local_ai_iteration_ledger
UNION ALL
SELECT 'RAW', iteration_uid, opened_at, closed_at,
       CASE status WHEN 'running' THEN 'running' WHEN 'halted' THEN 'halted' ELSE 'closed' END,
       approved_by, consecutive_no_gain, cross_notify_json
FROM raw_evolution_iteration_ledger;

COMMENT ON VIEW v_evolution_iteration_unified IS
  '三軸並列唯讀儀表 view [I]；status_canon 為展示映射，非各軸真狀態；禁作業務判斷';
```

> **注意**：`status_canon` 是**展示**映射——「closed」不區分有無增益（增益一律讀各軸原欄）。此設計刻意犧牲精度換一致性，故禁作業務判斷。

---

## 5. (b) Python 程式規畫

### 5.1 既有腳本（三軸共同消費；本檔零改動）

| 群 | 腳本 | 本總控用途 |
|---|---|---|
| TW 閉環 | `run_philosophy_evolution.py`／`apply_evolution_promotions.py`／`set_evolution_kill_switch.py`／`train_ranker.py`／`predict_asof.py`／`verify_prodset_hotpath.py`／`run_arena_daily_pipeline.py`／`settle_arena_labels.py`／`arena_scoreboard.py`／`run_revalidation_cycle.py`／`curate_pme_map_expand.py`／`verify_candidate_promotion.py` | 唯讀引用（週儀表溯源）；**不由本檔呼叫** |
| LAI 閉環 | `evolve_cycle.py`／`migrate_ai_evolution_ddl.py`／`advisor_distill_*.py`／`bridge_deliberation_distill.py` | 同上 |
| RAW 地基 | `profile_raw_data.py`／`scan_coverage.py`／`run_field_correlation.py`／`build_field_lens_map.py`／`build_catalog.py --db-only` | 同上 |
| 稽核 | `check_cmd_matrix.py`／`deliberate.py`／`evaluate_arena_admission.py` | M0／M1 驗收 |
| **API 門（凍結中不跑）** | `reconcile_audit.py`／`daily_maintenance.py`／`sync_finmind*` | 只讀其歷史結果 |

### 5.2 各軸已規劃、尚未實作之腳本（角色總表；歸屬各軸拍板碼）

| 腳本 | 軸 | 角色 | 何時可寫 |
|---|---|---|---|
| `migrate_evolution_iteration_ddl.py` | TW | `evolution_iteration_ledger`（＋本檔增補欄） | `TWEVO-S1-go` |
| `run_evolution_iteration.py` | TW | I0–I9 driver（預設不 APPLY） | `TWEVO-S2-go` |
| `export_evolution_advisor_brief.py` | TW | 產 `brief/1`（kind=prediction_brief） | `TWEVO-S2-go`（可選） |
| `verify_evolution_iteration.py` | TW | V0–V9 哨兵 | `TWEVO-S2-go`（可選） |
| `migrate_local_ai_iteration_ddl.py`（或併 `migrate_ai_evolution_ddl.py`） | LAI | `local_ai_iteration_ledger`（＋增補欄） | `LAIEVO-B1-go` |
| `close_local_ai_iteration.py` | LAI | 開輪／結案／停損計數／寫 hints_out | `LAIEVO-B1-go` |
| `migrate_lora_training_ddl.py`／`export_evolution_sft.py`／`train_qlora_small.py`／`train_lora_cpu.py`／`publish_lora_ollama.py`／`eval_local_model_deploy.py` | LAI | B2／B3 權重鏈 | `LAIEVO-B2-*`／`B3-go` |
| `migrate_raw_evolution_ddl.py` | RAW | 兩表 DDL（＋增補欄） | `RAWEVO-S0-go` |
| `run_raw_evolution_iteration.py` | RAW | R0–R5 driver | `RAWEVO-S0-go` 起 |

**取消（增量決議）**：`report_dual_evolution_week.py`（TWEVO §5.3／LAIEVO §5.2(0b)／RAWEVO §7.2 三處提及）**不另寫雙軸版**——直接實作三軸版 §5.3；三份子計畫中的 dual 檔名視為本檔 `report_triple_evolution_week.py` 之**別名**（避免雙檔，對齊 LAIEVO「檔名保留避免雙檔」慣例）。

### 5.3 新編排（本檔新增，屬 `TRI-M1-go`）

#### (1) `scripts/report_triple_evolution_week.py`

* **職責**：**唯讀**並列三軸本週 ledger 列（狀態／增益／停損計數／briefs／hints／未清 `xnotify`），輸出 stdout 或 markdown；**不寫任何業務表**、**不合併帳本**、**不自算增益**。
* **缺表容忍（graceful）**：任一 ledger 未建 → 該軸列印 `not_provisioned`，rc=0（不 traceback，#29(a)）。
* **執行指令矩陣（首次提交即含；#18／#29）**：

```text
python scripts/report_triple_evolution_week.py
  # 安全預設：印指令矩陣＋本週三軸摘要（唯讀，缺表 graceful）

python scripts/report_triple_evolution_week.py --week 2026-W31
python scripts/report_triple_evolution_week.py --since 2026-07-20 --until 2026-07-26
python scripts/report_triple_evolution_week.py --out reports/augur_triple_evolution_week_20260726.md
  # 寫報告檔（#16 命名）；內容仍唯讀來源

python scripts/report_triple_evolution_week.py --check
  # 只跑機械驗收 T-V1/T-V2/T-V7（命名／契約／措辭），紅則 rc≠0；供 pre-commit／CI

python scripts/report_triple_evolution_week.py --selftest
  # 免 DB：狀態映射表、週界計算、措辭黑名單、契約 validator 紅綠
```

* **I/O**：讀三 ledger（或 `v_evolution_iteration_unified`）＋`evolution_cross_notify`；寫 stdout／`reports/*.md`。

#### (2) `scripts/validate_evolution_contract.py`

* **職責**：`xnotify/1`／`brief/1`／`hint/1` 之單一 validator（產生端與消費端共用，防兩邊各寫一份而漂移）；未知欄位 fail-closed；措辭黑名單（`可交易`／`確立級`／`已解凍`，允許否定句白名單）；`brief.claims` 上限與型別檢查；`hint.human_gate.decision≠approved` → 標記不可進 curate。
* **矩陣**：

```text
python scripts/validate_evolution_contract.py            # 矩陣＋內建範例三契約驗證（零 DB）
python scripts/validate_evolution_contract.py --file PATH [--kind brief|hint|xnotify]
python scripts/validate_evolution_contract.py --scan-ledgers   # 掃三 ledger JSONB 欄＋cross_notify 表
python scripts/validate_evolution_contract.py --selftest
```

#### (3) `scripts/migrate_evolution_cross_notify_ddl.py`

* **職責**：§4.3 表＋禁刪 trigger＋（三 ledger 皆在時）§4.4 view 之冪等 DDL。
* **矩陣**：`--check`｜`--apply`｜`--dry-run`｜`--selftest`；無參數＝印矩陣＋`--check`。

#### (4)（可選 library）`src/augur/audit/evolution_contract.py`

* 純函式：三契約 dataclass／驗證／`iteration_uid` regex／status 映射；`python -m augur.audit.evolution_contract --selftest`（免 DB 免 API，#18 library 矩陣義務）。腳本 (1)(2) 皆 import 之，單一住所（#12）。

---

## 6. 分階段落地＋機械驗收＋回滾

### 6.1 階段

| 階段 | 內容 | 機械驗收 | 回滾 |
|---|---|---|---|
| **M0 對齊核對**（唯讀，零 code） | 逐項核對三子計畫與本檔：命名衝突、欄位不一致（§3.5）、dual 週報重複、hint 去重鍵缺漏、`TRI-HALT` 語意是否與各軸 kill 相容；產出 `audits/TRI-ALIGN-<date>.md` 紀錄「已對齊／各軸拒絕並附理由」 | 對照表逐列有結論；`rg 'report_dual_evolution_week' reports/` 之三處已標別名；零檔案被實作 | 無 code 可回；audit 檔留痕 |
| **M1 介面契約落地** | (a) `migrate_evolution_cross_notify_ddl.py`＋表＋trigger；(b) `evolution_contract.py`＋`validate_evolution_contract.py`；(c) `report_triple_evolution_week.py` 骨架（缺表 graceful）；(d) 三軸 migrate 腳本併入增補欄（**與各軸 S1／B1／S0 同批或先行皆可，但不得先於該軸拍板碼實作該軸業務邏輯**） | `--selftest` 三綠；`check_cmd_matrix.py` 過；`--check` 在零 ledger 情境 rc=0；契約 validator 對三份內建範例紅綠正確 | DROP `evolution_cross_notify`（無業務依賴）；刪三新檔；增補欄為 `ADD COLUMN IF NOT EXISTS`，可 DROP COLUMN |
| **M2 分軸開工** | 依各軸拍板碼：**RAWEVO S0**（地基先行，供 hints）→ **TWEVO S0/S1/S2**（帳本＋閘輪，無 APPLY）→ **LAIEVO B0/B1**（pack 主線）；此後依 §3.3 週節拍運行 | 各軸自有驗收（RAWEVO S0–S5／TWEVO V0–V9／LAIEVO L-V0–L-V9）＋本檔 T-V0–T-V9 | 各軸自有回滾；介面層不回滾 |

**開工序理由**：RAWEVO 先行＝其產出（缺口帳／hints）是 TWEVO I0 的燃料，且全程唯讀零風險；TWEVO 次之（帳本先於 APPLY）；LAIEVO 可與前二並行但錯峰（重活與 Ollama 佔用）。

### 6.2 本檔機械驗收（T-V0–T-V9；介面層，不取代各軸 V／L-V／S 驗收）

| ID | 判準 | 驗法（機械） |
|---|---|---|
| **T-V0** | FZ-keep（三軸） | 三 ledger `steps_json`／週報／brief 檔：`rg -n 'finmind\.fetch\|fred\.fetch\|sync_finmind'`＝0；arena argv 含 `--skip-sync` |
| **T-V1** | 命名唯一 | 三表 `iteration_uid` 皆過 regex；`SELECT count(*)=count(DISTINCT iteration_uid)` 於三表 UNION 成立；前綴與 axis 相符 |
| **T-V2** | 契約合法 | `validate_evolution_contract.py --scan-ledgers` rc=0（含 schema 欄存在、未知欄位為 0、`claims≤20`、無數值陣列） |
| **T-V3** | 通知不連鎖 | 每筆 `xnotify`（非 `tri_halt`）之後 5 分鐘內，對偶軸無自動 `evolution_apply_log` 新列／無 serving 變更／無 curate 寫入（SQL 時間窗比對） |
| **T-V4** | 人閘完整 | `hints_in` 之每個 `hint_id` 於來源 ledger 皆 `human_gate.decision='approved'` ∧ `by` 非空；`local_model_version.status='serving'` 皆有 `promoted_by`；`apply_allowed=false` 之輪無 APPLY 列 |
| **T-V5** | 重活互斥 | 同一時間窗內 heavy step 重疊數 ≤1（由 `steps_json` 時戳算）；重疊者須有 `defer_heavy` 通知或 advisory lock 等待紀錄 |
| **T-V6** | 三軸隔離 | RAW／LAI 本週無寫入 `feature_values`／`evolution_production_feature_set`／`promotion_queue`；LAI 無寫 raw 表；RAW 無寫 gold／`local_model_version`（SQL＋REVOKE） |
| **T-V7** | 措辭 | brief／hint／週報：`rg '可交易\|確立級\|已解凍'`＝0（否定句白名單除外）；`claim_level` 僅白名單值 |
| **T-V8** | 儀表唯讀 | 週報執行前後三 ledger 與 `evolution_cross_notify` 之 `count`／`max(updated)` 不變；view 無寫入路徑引用（`rg` code 檢查） |
| **T-V9** | 停損各自 | 三軸 `consecutive_no_gain` 只由自軸 driver 更新（來源腳本比對）；一軸停損不改對偶計數；`TRI-HALT` 期間無新輪 `opened_at` |

### 6.3 回滾總則

介面層回滾**不得**倒改任一軸既有業務狀態：DROP 新表／新檔／新欄即可，三軸 ledger 歷史列一律保留（失敗與告警留檔精神，對齊 P4.E3／`lora_training_run` 禁刪）。

---

## 7. 建議拍板碼

### 7.1 本檔新碼

| 碼 | 含義 |
|---|---|
| **`TRI-P-yes`** | 採納本總控計畫為三軸交互 SSOT（仍不自動開工） |
| **`TRI-IFACE-yes`** | 三軸介面契約（§3 命名／JSON／錯峰／通知）生效；**`DUAL-IFACE-yes` 視為其前身**，既拍者自動涵蓋 |
| **`TRI-M0-go`** | 開 M0 對齊核對（唯讀，產 audit） |
| **`TRI-M1-go`** | 開 M1 介面契約落地（新表＋validator＋週報骨架＋三軸增補欄） |
| **`TRI-CADENCE-yes`** | （可選）採納 §3.3 週節拍為預設節奏（未拍＝全手動開輪） |
| **`TRI-HALT`／`TRI-RESUME`** | Steward 全域停機／解除（擋開新輪；不改既有狀態） |
| **`TRI-P-no`／`TRI-Mx-hold`** | 否決／暫緩 |

### 7.2 同批 vs 分開

| **可同批** | **必須分開** |
|---|---|
| `TRI-P-yes`＋`TRI-IFACE-yes`＋`RAWEVO-P-yes`＋`TWEVO-P-yes`＋`LAIEVO-P-yes`＋`FZ-keep`＋`GATE-keep` | `TWEVO-APPLY-go` ≠ LAIEVO 人簽 serving ≠ `RAWEVO-HINT-approve`（三種人閘各簽各的） |
| `TRI-M0-go`＋`TRI-M1-go`（介面層零業務風險） | `RAWEVO-S2`（R3 重掃）／`TWEVO-S3/S4`（APPLY／arena）／`LAIEVO-B2-train`／`B3`（訓權重）**兩兩不同批**（單機重活互斥） |
| `RAWEVO-S0-go`＋`TWEVO-S0/S1-go`＋`LAIEVO-B0-go`（盤點／DDL／唯讀核對） | 停損 N：`RAWEVO-STOP-N`／`TWEVO-N`／`LAIEVO-STOP-N` 各改各的 |
| `TWEVO-S2`（無 APPLY）∥ `LAIEVO-B1`／`B4`（錯峰 embed） | 任一軸降閾／改判準 → 一律另案（治權層） |

### 7.3 建議首批（一次拍完、可立即分軸推進）

```
TRI-P-yes ＋ TRI-IFACE-yes ＋ RAWEVO-P-yes ＋ TWEVO-P-yes ＋ LAIEVO-P-yes ＋ FZ-keep ＋ GATE-keep
    → 次批：TRI-M0-go ＋ TRI-M1-go
        → 再分軸：RAWEVO-S0-go → TWEVO-S0-go/S1-go/S2-go → LAIEVO-B0-go/B1-go
```

---

## 8. 風險與誠實預期

* **三帳本維護債**：以「同構不同帳」換正交清晰是刻意取捨；欄位漂移風險由 §3.5 對齊＋T-V1／T-V2 機械鎖控管；若一年後仍證明維護成本 > 正交收益 → S5／回顧另案提合併（**不在本檔授權範圍**）。
* **總控檔本身可能變成第四個要維護的東西**：緩解＝本檔只寫「軸與軸之間」，任何軸內細節一律引用不複印；本檔若與子計畫重複超過一段，即為腐化訊號。
* **節奏表落地難**：單機、單人、週節拍會被現實打斷（長跑、配額、睡眠）；故 §3.3 為**建議**且需 `TRI-CADENCE-yes` 才成預設，未拍＝手動開輪，不視為違規。
* **三軸都可能長期無增益**：prodset 可能仍 n=2、LAI 可能連續無增益停損、RAW 缺口在凍結下不會變少——這是**誠實預期**而非失敗；成功定義＝三本帳可查、可否證、可停，不是數字變好看。
* **交互面反而是最大假兆風險**：brief／hint 是唯一「軟資訊」通道，最容易夾帶未過閘結論；防線＝`claim_level` 型別鎖＋validator＋T-V7 措辭掃描＋人閘，三層任一失守即停手問。

---

## 9. 執行前四判準（G-P4 自檢；開 `TRI-M1-go` 前勾）

| # | 判準 | 本檔 |
|---|---|---|
| ① 完整 | §4 schema（新表 DDL＋增補欄＋view）＋§5 python（總表＋三新檔矩陣）＋§2 正交／禁項＋§3 契約／節奏＋§6 分階／T-V／回滾＋§7 拍板碼 | ✅ |
| ② 內部一致 | `TRI-HALT` 與「禁跨軸自動連鎖」已釐清（源頭是人、效力只擋開輪）；三軸停損互不覆寫；view 明示非 SSOT | ✅ |
| ③ 與現況一致 | 引用 prodset n=2、雙綠 2 檔、MAP-E012 CLOSED、G-PROM-D2 第一關、`evaluated_pass=0`、84 raw 表／`ExchangeRate` 2020-11-13、Ollama 單實例 4GB；三新腳本經確認**皆尚未存在** | ✅ |
| ④ 可實作 | 新增面＝一張輕量表＋一個 validator＋一支唯讀週報＋三軸各加 3–4 欄；無新 package、無 DDL 於拍板前執行 | ✅ |

---

## 10. 30 分鐘閱讀地圖

§0（總覽／SSOT／衝突裁決）→ §1（三軸摘要表）→ §2.3（禁項清單）→ §3（增量：命名／契約／節奏／kill／欄位對齊）→ §6.1 分階＋§7.3 首批碼 → 需實作時再讀 §4／§5。

---

**本檔完。位階 [I]；拍板前零實作；全程零 FinMind／FRED；不降閘；raw 不升格靈魂；三本帳、三組人閘、一張節奏表。各軸細節以三份子計畫為 SSOT；衝突時取更嚴邊界。**
