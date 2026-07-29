# KH8-KH9-min-LAND CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md`（`KH8-KH9-min-LAND`＋`FZ-keep`）  
> **母計畫**：`reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` §KH8／§KH9／§5.2–5.3  
> **接續**：`reports/augur_kh10_auto_admit_plan_20260729.md` S2 註（抬 `max_auto_depth`）  
> **不含**：自動 approve／activate／PME APPLY／可交易宣稱／FinMind／FRED／KH10 進化寫側

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| DDL | ✅ | `knowhow_evidence_weight`＋`knowhow_synthesis_run`（冪等；含 `item_id`） |
| Library | ✅ | `evidence.py`／`synthesis.py`；`--selftest` 綠 |
| `evaluate_layer(8)` | ✅ | 算權＋寫帳；`confidence_band∈{high,medium,low}`→pass；`absent`→fail |
| `evaluate_layer(9)` | ✅ | 讀最新 KH8 權重→寫 replay；`replay_logged`／`synthesized`→pass；`postmortem_needed`→fail |
| `UNBUILT_LAYERS` | ✅ | `{8,9}` → `∅` |
| Gate | ✅ | `max_auto_depth`：**7→9**（`migrate_kh8_kh9_min_ddl.py --apply`） |
| CLI | ✅ | `compute_knowhow_evidence_weight.py`／`replay_knowhow_run.py`；薄 runner |
| 指令矩陣 | ✅ | `check_cmd_matrix.py` NEED=0 |

## 二、誠實公式（可複現；非發明「神奇 metric」）

**輸入（皆庫內可數／既有字面）**：`citation_count`（句數）、`has_text`／`has_sentence`／`has_embedding`、`knowledge_kh4_state.answer_status`。

```
cite_norm = min(citation_count/5, 1)
terminal  = 1 if sentence else (0.5 if text else 0)
embed     = 1 if embedding else 0
kh4_ok    = 1 if answer_status=='eligible' else 0
contra    = 1 if answer_status in {ineligible,blocked,ungrounded,declined,fail,failed} else 0
evidence_score = clamp(
  0.35*cite_norm + 0.25*terminal + 0.25*embed + 0.15*kh4_ok - 0.40*contra, 0, 1)
band = high≥0.70 / medium≥0.40 / low≥0.15 / else absent
```

- **pass ≠ approve ≠ tradable**；replay 帳本寫明 `boundaries`。
- 薄輸入（僅 text、無句／無 embed）→ `absent` → **fail**（單元自測鎖定；本庫目前無此類殘列可 live 抽樣）。

## 三、Live 抽樣（`--apply-up-to 9 --min-depth 7 --limit 3`）

| item_id | before→after | KH8 | KH9 | admit run_id |
|---|---|---|---|---|
| 4 | 7→9 | high／score=1.0 | replay_logged | 353743 |
| 7 | 7→9 | high／score=1.0 | replay_logged | 353744 |
| 8 | 7→9 | high／score=1.0 | replay_logged | 353745 |

**庫況（抽樣後）**：`state buckets` 含 `{7:145770, 9:3}`（另有 depth 3 殘列未動）；`knowhow_evidence_weight` rows=3；`knowhow_synthesis_run` rows=3。

**明文**：抬 depth 至 9 **≠** 可交易、**≠** PME solar gates、**≠** 人裁放行；FZ-keep。

## 四、驗證

| 檢查 | 結果 |
|---|---|
| `python -m augur.knowledge.evidence --selftest` | ✅ |
| `python -m augur.knowledge.synthesis --selftest` | ✅ |
| `python -m augur.knowledge.auto_admit --selftest` | ✅（UNBUILT=∅；表未建→skipped） |
| `migrate_kh8_kh9_min_ddl.py --selftest`／`--apply` | ✅ |
| `run_knowhow_auto_admit.py --check` | ✅ `max_auto_depth=9` |
| dry-run＋apply `--apply-up-to 9 --min-depth 7 --limit 3` | ✅ |
| `check_cmd_matrix.py` | ✅ NEED=0 |

## 五、變更檔

- `src/augur/knowledge/evidence.py` — **新**
- `src/augur/knowledge/synthesis.py` — **新**
- `src/augur/knowledge/auto_admit.py` — evaluate 8／9；UNBUILT 清空；預設 cap 9
- `scripts/migrate_kh8_kh9_min_ddl.py` — **新**
- `scripts/compute_knowhow_evidence_weight.py` — **新**
- `scripts/replay_knowhow_run.py` — **新**
- `scripts/run_knowhow_auto_admit.py` — 天花板註記／until-empty cap→9
- 本 CLOSED；WAVE2 §三 回填

## 六、硬邊界

| 項 | 結果 |
|---|---|
| FZ-keep | ✅ 零 FinMind／FRED |
| eligibility_pass≠approve≠tradable | ✅ |
| 無 PME solar gates | ✅ |
| 不 invent metrics | ✅ 僅可數輸入＋公開權重式 |
| 不改 [N] | ✅ |
