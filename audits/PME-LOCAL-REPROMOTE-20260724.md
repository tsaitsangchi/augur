# PME 本地再晉升 [I]（2026-07-24）

* Steward 明示：**PME 本地再晉升**
* 目標：零 FinMind／FRED 下再跑 G-PROM／G-ECON → 真綠 AUTO-B APPLY → 擴大 `evolution_production_feature_set` active（熱路徑 n_feats）
* 前輪：E123 `run_id=5` APPLY×2（`audits/PME-E123-CLOSED-20260724.md`）
* 硬邊界：FZ-keep；不假綠；不改 [N]；≠可交易／確立級；不改 P2H 熱路徑核心

---

## 結果（一句）

**再晉升可驗完成，但 active／n_feats 未擴大**——庫內同一 mapped 集合下雙綠仍僅 `inst_cumflow_position_120d`、`volume_gini_60d`（與 E123 同集合）。

---

## 執行

| 步 | 指令／動作 | 結果 |
|---|---|---|
| 1 | `set_evolution_kill_switch.py --status` | **effective=clear**（env halt=False） |
| 2 | `run_philosophy_evolution.py --local-gates` | **run_id=6** `succeeded`；elapsed≈**29m07s**（15:44→16:13） |
| 3 | `apply_evolution_promotions.py --run-id 6` | **applied=2**（僅 pending_auto 真綠）；validated→validated 冪等再登錄 |
| 4 | log | `/tmp/augur_logs/pme_repromote_local_gates.log`／`pme_repromote_apply.log` |

---

## 前後對照

| 項 | 前（E123／run5） | 後（本輪／run6） |
|---|---|---|
| kill-switch | clear | clear |
| active 數 | **2** | **2**（未擴大） |
| active 清單 | `inst_cumflow_position_120d`、`volume_gini_60d`（source_run_id=5） | 同二特徵（source_run_id=**6**；apply_log 3／4） |
| principle | untested=24／validated=2 | 同 |
| G-PROM（42 map） | PASS=2／FAIL=34／SKIP=6 | **PASS=2／FAIL=34／SKIP=6** |
| G-ECON（42 map） | PASS=15／FAIL=21／SKIP=6 | **PASS=15／FAIL=21／SKIP=6** |
| queue | applied=2／rejected_gate=40 | applied=**2**／rejected_gate=**40** |
| 雙綠特徵 | cumflow／volume_gini | **同** |

### SKIP（誠實，非假綠）

| feature | coverage_class |
|---|---|
| `dividend_yield` | **blocked_div** |
| `debt_ratio`／`macro_regime`／`peg_ratio`／`piotroski_fscore`／`roe` | **missing** |

### 雙綠交叉（map 列）

| G-PROM＼G-ECON | PASS | FAIL | SKIP |
|---|---|---|---|
| PASS | **2** | 0 | 0 |
| FAIL | 13 | 21 | 0 |
| SKIP | 0 | 0 | **6** |

→ 僅 **2** 列七閘可全綠 → APPLY；G-ECON 單綠≠晉升（G-PROM 仍紅）。

---

## 驗收邊界

| 項 | 本輪 |
|---|---|
| 零市場 API | ✅ 無 FinMind／FRED；庫內 feature_values／panel |
| 不假綠 | ✅ FAIL／SKIP 維持；無降閾／無跳閘 |
| APPLY 僅真綠 | ✅ pending_auto=2 → applied=2 |
| ≠可交易／確立級 | ✅ 僅 prodset 狀態再登錄 |
| n_feats 擴大 | ❌ **未達成**（庫內閘結果無新雙綠） |
| P2H 熱路徑核心 | ✅ 未改 code；僅 prodset 表寫入 |

---

## Gap 建議

| ID | 建議 | 說明 |
|---|---|---|
| **G-PME-PROM**／**G-PME-ECON** | 維持 **partial** | 再跑可驗、統計與 E123 同；無新 PASS |
| **G-PME-HOTPATH** | 維持 **none**（n_feats=2 誠實極窄） | 再晉升**未**擴大 active；擴大需新特徵／新 map／資料洞補齊（缺股仍 FZ-keep）後再閘 |

---

## 封存

* `bash scripts/archive_push.sh --slug philosophy-market-evolution-repromote`
* HEAD／tag：見封存 stdout（本檔撰寫時工作樹 HEAD 見 git）
