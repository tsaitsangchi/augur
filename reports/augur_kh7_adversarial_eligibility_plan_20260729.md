# KH7 對抗可答性（Adversarial Eligibility）最小計畫 [I]

> **日期**：2026-07-29  
> **位階**：[I] 執行／架構計畫；**不創設 [N]**  
> **拍板句（已採）**：`KNI-S3 + KH7-PLAN + KH7-S1 + RKI-keep + NHC-keep + FZ-keep + HUMAN-APPROVE-keep`  
> **別名**：本 slice＝**KH10-S1 對抗層最小**（十層架構之 KH7 近程落地）  
> **母計畫**：[`augur_ten_layer_knowhow_architecture_plan_20260728.md`](augur_ten_layer_knowhow_architecture_plan_20260728.md) §KH7  
> **上游**：KNI-S2 runner（`run_knowhow_interaction_probes.py`／`interaction_probe.py`）；KNI-S3 評測（同拍板並行）

---

## 1. What／Why／Non-goals

### 1.1 What

建立 **KH7**：對 KH6 探針結果（及可選 KH4 作答材料）做**機械對抗可答性**裁決，狀態閉集：

| status | 含義 |
|---|---|
| `unchecked` | 尚未裁 |
| `eligibility_pass` | 機械可過（仍≠答案 SSOT／≠可交易） |
| `eligibility_fail` | 機械否決（缺料／假相關過高／缺軸） |
| `contradiction_found` | 預留（S1 **不實作**矛盾模板） |
| `needs_human_review` | 灰區，升人審佇列 |

### 1.2 Why

KNI-S2 live 已證明：多軸＋RRF 會撈到哲學雜訊／ERP 投影片等；僅有 `spurious_risk` 旗標不夠——需要**可帳本化的 eligibility**，才能標「可答但不可信／需人審」，並餵後續 KH8／EVAL。

### 1.3 Non-goals

| 不做 | 理由 |
|---|---|
| 自動 `approve`／`activate` | `HUMAN-APPROVE-keep`；入憲自動入庫另案 |
| 領域專答樹／hardcode 太陽能答案 | NHC-keep |
| FinMind／FRED | FZ-keep |
| 完整矛盾模板／LLM 對抗辯論 | 屬 KH7 後續；S1 僅機械子集 |
| KH8 權重／KH9 合成／PME 灌因子 | 另層 |

---

## 2. 對應 table schema

### 2.1 新表 `knowhow_kh7_eligibility`

```sql
CREATE TABLE IF NOT EXISTS knowhow_kh7_eligibility (
  eligibility_id   BIGSERIAL PRIMARY KEY,
  run_id           BIGINT REFERENCES knowhow_interaction_probe_run(run_id) ON DELETE SET NULL,
  probe_id         TEXT NOT NULL,
  status           TEXT NOT NULL
                   CHECK (status IN (
                     'unchecked','eligibility_pass','eligibility_fail',
                     'contradiction_found','needs_human_review')),
  reasons          JSONB NOT NULL DEFAULT '[]'::jsonb,
  evidence         JSONB NOT NULL DEFAULT '{}'::jsonb,  -- gap／spurious／hit 摘要
  decided_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  script           TEXT NOT NULL DEFAULT 'run_kh7_eligibility.py',
  note             TEXT
);
CREATE INDEX IF NOT EXISTS idx_kh7_elig_probe_time
  ON knowhow_kh7_eligibility (probe_id, decided_at DESC);
COMMENT ON TABLE knowhow_kh7_eligibility IS
  'KH7-S1: 探針對抗可答性帳本（非答案 SSOT；不改 approval_status）';
```

### 2.2 消費既有表（唯讀）

| 表 | 角色 |
|---|---|
| `knowhow_interaction_probe_run`／`_result` | KH6 跑批輸入 |
| `knowhow_interaction_probe` | probe 元資料 |
| `knowledge_kh4_state` | **可選**附註 `evidence.kh7_last`；**禁止**改 `answer_status` |

### 2.3 KNI-S3 評測表（同拍板）

```sql
CREATE TABLE IF NOT EXISTS knowhow_eval_suite_case (
  case_id          TEXT PRIMARY KEY,
  probe_id         TEXT NOT NULL REFERENCES knowhow_interaction_probe(probe_id),
  role             TEXT NOT NULL,  -- full_triple|ablation_no_principle|ablation_no_ai|expect_decline
  expect_json      JSONB NOT NULL DEFAULT '{}'::jsonb,  -- 機械期望旗，非答案正文
  active           BOOLEAN NOT NULL DEFAULT true,
  note             TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE knowhow_eval_suite_case IS
  'KNI-S3: 固定評測題組（策展列；禁答案樹 SSOT）';
```

種子（INSERT 策展，非 code 寫死答案）：

| case_id | probe_id | role |
|---|---|---|
| `KNI-S3-FULL-FP-AI-SOLAR` | `RKI-FP-AI-SOLAR` | `full_triple` |
| `KNI-S3-ABL-NO-FP` | `RKI-AI-SOLAR-RD` | `ablation_no_principle` |
| `KNI-S3-ABL-NO-AI` | `RKI-FP-SOLAR-CORE` | `ablation_no_ai` |
| `KNI-S3-EXPECT-DECLINE` | `KNI-EVAL-EMPTY-CORPUS`（新種子探針：無意義軸） | `expect_decline` |

> **Live 教訓（2026-07-29）**：語意檢索對任意 query 仍回 top‑k 近鄰 → 無意義軸仍 `merged>0`／`gap=[]`，**不能**期望裸 `no_corpus`。  
> **修訂期望（待 Agent 改 code）**：decline 機械斷言改為下列 **任一** 成立即 PASS：  
> 1. `no_corpus`∈gap 或 `merged_hits=0`；或  
> 2. 新旗標 `ungrounded_hits`：任一軸 label **皆未**出現於 top hits 之 title／snippet（確定性字串包含）；或  
> 3. KH7 對該結果裁 `eligibility_fail`（在引入 ungrounded 規則後）。  
> 禁止靠「撈不到任何向量鄰居」當 decline 判準（e5 top‑k 幾乎永有鄰居）。

---

## 3. Python／程式規畫

| 檔 | 角色 | 階段 |
|---|---|---|
| `src/augur/knowledge/kh7_eligibility.py` | `decide_eligibility`／`batch_decide`；`--selftest` | KH7-S1 |
| `scripts/migrate_kh7_eligibility_ddl.py` | 冪等 DDL＋`--check`／`--apply`／`--selftest` | KH7-S1 |
| `scripts/run_kh7_eligibility.py` | 讀最近 probe_run 或 stdin JSON → 裁決 → 寫帳本；可選 annotate KH4 evidence | KH7-S1 |
| `scripts/migrate_knowhow_eval_suite_ddl.py` | eval suite＋decline 探針種子 | KNI-S3 |
| `scripts/eval_knowhow_interaction_probes.py` | 跑 suite → 指標表／報告；呼叫既有 `run_probe` | KNI-S3 |
| 既有 `run_knowhow_interaction_probes.py` | 檢索／RRF 引擎（不改閘語意） | 消費 |

### 3.1 KH7-S1 機械規則（閉集、可複現）

輸入＝單探針 `summarize_probe_result` 形狀：

0. **（修訂 2026-07-29 live）** 若任一軸 `label`（或 query 字串）**皆未**出現於任何 top-hit 的 `title`／`snippet` → 加 `ungrounded_hits`，並 **`eligibility_fail`**（理由 `ungrounded_axis_labels`）。  
   - Live 反例：`KNI-EVAL-EMPTY-CORPUS` 在修訂前被誤判 `eligibility_pass`（`multi_src=2`＋`spurious=low`），實為哲學近鄰假命中。  
1. `no_corpus` 或 `merged_hits<=0` → `eligibility_fail`  
2. 任一 `no_axis:*` → `eligibility_fail`  
3. `spurious_risk=high` **或** `ungrounded_hits`∈gap → `eligibility_fail`  
4. `single_axis_only` → `needs_human_review`  
5. `covered>=2` ∧ `multi_source>=1` ∧ `spurious=low` ∧ **無 ungrounded** → `eligibility_pass`  
6. 其餘灰區 → `needs_human_review`  

**禁止**：依 domain／題目寫死「太陽能應答內容」。  
**禁止**：僅憑 `multi_source`＋`spurious=low` 升格 pass（缺落地字串校驗＝假綠）。

### 3.1.1 Live 回放（run_id=2，修訂前規則）

| probe | 舊裁決 | 問題 |
|---|---|---|
| `KNI-EVAL-EMPTY-CORPUS` | `eligibility_pass` | **假綠**——應 fail（ungrounded） |
| `RKI-AI-SOLAR-RD` | `needs_human_review` | 合理灰區（multi=0／spur=medium） |
| `RKI-FP-AI-SOLAR` | `eligibility_pass` | 待 ungrounded 複核後再定 |
| `RKI-FP-SOLAR-CORE` | `eligibility_pass` | 同上（命中含 Genero／鶡冠子，宜複核） |

### 3.2 KNI-S3 評測指標（真兆）

每 case 記錄（stdout／JSON／report，禁估算）：

- `merged_hits`／`multi_source_hits`／`spurious_risk`／`gap_flags`  
- 消融對照表：full vs no-FP vs no-AI 之 multi_src／spurious 差  
- `expect_decline`：機械斷言 `no_corpus`∈gap 或 KH7=`eligibility_fail`  
- 可選 KH7 裁決欄（若已跑）

報告：`reports/augur_kni_s3_eval_20260729.md`

---

## 4. 分階與驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| **KNI-S3** | suite DDL＋eval CLI＋報告 | 四 case 跑完；消融表有數；decline case 機械綠；V-TRACE／V-NHC／V-FZ |
| **KH7-PLAN** | 本檔 | Steward 已拍 `KH7-PLAN` |
| **KH7-S1** | library＋migrate＋runner；寫 `knowhow_kh7_eligibility` | selftest 綠；對 `run_id≥1` 可回放裁決；**approval_status 零變** |
| **U** | isolation／cmd_matrix | predict 隔離綠；缺矩陣＝0 |

---

## 5. 與「過 KH10 自動入庫入憲」之關係

本拍板（KH7）**明示不入憲、不自動 approve**。  

**另案已開**：[`augur_kh10_auto_admit_plan_20260729.md`](augur_kh10_auto_admit_plan_20260729.md)（`KH10-AUTO-ADMIT`；預設 C＋X＋**RAW-FLOOR**；升格 gate 預設關）。  
KH7 為**升格層**前置之一（ungrounded→擋 eligible／activate，**不**擋原文入庫）；升格 overall pass 尚需 KH8／KH9／ENABLE。

---

## 6. 風險

| 風險 | 緩解 |
|---|---|
| 把 eligibility_pass 當成「答對了」 | 文件＋audit 明文：非答案 SSOT |
| 規則過嚴全 fail | S1 灰區走 human；後續可調、調參須留痕 |
| 與 ADM-AI-ASSIST 混淆 | 本層不碰 source 審批表 |
| 平行 agent 搶工作樹 | archive 時 scoped slug；不強塞無關 diff |

---

## 7. 建議執行序（開工後）

1. `migrate_knowhow_eval_suite_ddl.py --apply`（含 decline 探針種子）  
2. `eval_knowhow_interaction_probes.py --run --report …` → KNI-S3 CLOSED audit  
3. `migrate_kh7_eligibility_ddl.py --apply`  
4. `run_kh7_eligibility.py --from-run <id> --apply` → KH7-S1 CLOSED audit  
5. `archive_push.sh --slug kni-s3-kh7-s1`

---

## 8. 拍板登錄（建議 audit 標題）

- `audits/KH7-PLAN-APPROVED-20260729.md`  
- `audits/KNI-S3-CLOSED-20260729.md`  
- `audits/KH7-S1-CLOSED-20260729.md`
