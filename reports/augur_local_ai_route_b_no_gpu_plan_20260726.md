# 本地 AI（advisor）自進化迭代學習計畫——路線 B（不換卡／4GB VRAM）

> **SSOT 已移轉（V2-P-yes，2026-07-26 hugo 拍板、登錄 `audits/V2-ADOPTED-SUNSET-20260726.md`）**：本檔之總控／介面契約 SSOT＝`augur_self_evolution_master_plan_v2_20260726.md`；本檔降為前身史料，衝突時以 v2 為準；v2 §0.6 明列本檔哪些段落作廢／修訂／撤回。

> **性質**：[I] 工具層計畫（#20 計畫先行／憲章 v1.39.0 計畫完整性）  
> **日期**：2026-07-26｜**機器**：DESKTOP-8MQPFS8（GTX 1650 4GB／Ryzen 5 3600／~24GB RAM／WSL2）  
> **狀態**：計畫書已升格為「自進化迭代學習」語意；**本計畫書拍板後才動工**（尚未授權實作）  
> **檔名保留**：`augur_local_ai_route_b_no_gpu_plan_20260726.md`（原「路線 B 不換卡」專篇升格；避免雙檔）  
> **承接**：`reports/augur_local_ai_evolution_loop_plan_20260725.md`（進化閉環終稿）之 **Tier1＝本線主力**、Tier2＝本機階梯實驗；**不重複**該檔已被擊倒的自對弈永動機／4b GPU QLoRA／夜間全自動 cutover  
> **蒸餾先例**：`reports/augur_advisor_distill_pilot_20260706.md`（171 條 SFT pilot、drop 37.6%＜40% GATE）  
> **正交姊妹檔**：`reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md`（台股**預測系統**自進化；拍板碼 **`TWEVO-*`**）——結構可對齊（閉環／迭代帳本／停損／拍板碼），**內容系統正交**；本檔＝advisor／本地 LLM；彼檔＝預測管線。**勿混成一個系統**（見 §〇.1／§十二）。協作介面可選短檔：`reports/augur_dual_self_evolution_interface_20260726.md`。

---

## 〇、一句定錨

在 **不換 GPU 卡（4GB VRAM 硬限）** 前提下，讓本機 advisor／MCP 本地 LLM **有紀律地自進化**：

**gold／題庫累積 → `evolve_cycle` prompt-pack → 可測增益 → 人閘晉升 `local_model_version` →（可選）1.7b QLoRA／CPU LoRA 實驗 → 驗證／回滾 → 回饋下一輪 gold／pack → 迭代帳本。**

四軸仍是手段，不是並列口號：**(B1)** 零訓練 prompt-pack 主線 → **(B4)** 持續累積可重用 gold（耐久資產）→ **(B2)** 4GB 可塞的 1.7b QLoRA 窄任務特化 → **(B3)** 4b CPU LoRA 過夜實驗。  
**訓過 ≠ 變聰明**：每一軸都以部署域金標／held-out 實測為驗收；晉升永遠人閘；無增益則停損、不硬晉升。

### 〇.1 與台股預測自進化的正交聲明（必讀）

| | **本檔＝本地 AI（advisor）自進化** | **姊妹檔＝台股預測自進化（TWEVO）** |
|---|---|---|
| **進化對象** | Ollama 本地 LLM（advisor／MCP：prompt-pack、蒸餾 gold、可選 LoRA） | 預測系統（特徵／模型／切分／經濟驗證／arena 等） |
| **消費資料** | `local_model_gold_sample`／`advisor_distill_*`／serving pack；**可選**消費 TWEVO **唯讀 brief**（§十二.2） | 庫內 raw→features→panel（as-of）；**預測 ⊥ 市場 API** |
| **成功定義** | 部署域（MCP summarize／extract／DECLINE 誠實性）金標升、錨集不退 | 經濟價值／閘內 paper（非裸 IC；**≠**可交易／確立級） |
| **禁混** | 不把預測 IC／Sharpe 當 LLM 增益；不把 LoRA 權重當特徵；**禁**輸出直接 APPLY／改 prodset | 不把 prompt-pack／teacher 答當預測特徵或治權 [N] |
| **拍板碼族** | `LAIEVO-*`（舊別名 `ROUTEB-*`） | **`TWEVO-*`**；**不得共用 go 碼開工**（§十二.5） |

> **一句**：兩邊都可「迭代學習」，但是 **兩個閉環、兩本帳、兩組停損**；共享的只有治權精神（#1／#15／人閘／owned_local）、FZ-keep、以及 §十二 的**唯讀摘要＋通知＋錯峰**——**不是同一條管線**。

---

## 一、背景與既成事實（引用結論，不抄全文）

| 項 | 現況結論 |
|---|---|
| 硬體 | GTX 1650 **4GB VRAM** 硬限；idle free VRAM 常落 ~2.7GB（進化計畫實測反證：4b NF4 GPU QLoRA **塞不進**） |
| Ollama 0.32.1 | advisor=`qwen3:8b`、MCP=`qwen3:4b`、embed=`nomic-embed-text`；**只本機** |
| 進化閉環（2026-07-25） | Tier1 prompt-pack **已落地**於 `evolve_cycle.py`＋`migrate_ai_evolution_ddl.py`；晉升人簽；外部教師除役（本地 8b 教本地） |
| 蒸餾 pilot（2026-07-06） | 274 題→**171** 乾淨 SFT；界線 A/B/C；S6 訓練因無適配 GPU **deferred** |
| 訓練腳本缺口 | repo **無**現成 LLM LoRA／QLoRA 訓練腳本（僅有預測側 `train_*`——**不得挪用當本閉環入口**）→ B2/B3 **須新增**可執行入口 |
| 耐久資產 | LoRA 隨 base 換代歸零；**gold 帳本跨 base 永存**（進化計畫成敗判準） |
| 台股自進化檔 | `augur_tw_prediction_self_evolution_loop_plan_20260726.md`（**已存在**；§8 對偶介面）——內容正交；本檔 §十二對齊 |

**本計畫＝本地 AI 自進化（路線 B 硬體約束）專篇**：把昨日 Tier1／Tier2 本機階梯改寫成可驗收的**迭代閉環**，並補齊 (a) schema／(b) 程式規畫。**路線 A（換卡／12GB+）不在本檔範圍**。

---

## 二、硬邊界（寫進計畫＝執行時不可逾）

1. **權重／私有語料 `owned_local` 不出本機**：LoRA 檔、SFT jsonl、evolution／distill 帳本、訓練 run artifact、迭代帳本匯出 **不入 git／不公開 repo**；跨機僅私有通道。  
2. **advisor／MCP 只本機 Ollama**：教師預設 `DISTILL_TEACHER_MODEL=qwen3:8b`；評測預設 `qwen3:4b`；**外部 token 歸零**（進化 v3 拍板）。  
3. **FinMind／FRED 凍結正交**：全程 **零市場 API**；本計畫不觸 sync／probe；與預測熱路徑正交（預測可另跑庫內 as-of——**不解凍本閉環去打 API**）。  
4. **蒸餾／evolution 表不進** `knowledge_*`／`philosophy_*`／`feature_values`／預測 7 package；不成 citation（界線-A；`augur_predict` REVOKE 既有閘續守）。  
5. **晉升人閘（P5.W2）**：`local_model_version` candidate→serving **須** `promoted_by`＋`promoted_at`；`evolve_cycle` **永不**自動 UPDATE serving。  
6. **三敵零容忍**：#1 source-pure／anti-hallucination 同精神／#15 凡數字與分數須 trace 回程式輸出或 DB；**訓過≠變聰明**。  
7. **4GB VRAM 硬限**：禁止規劃／執行會穩態佔用 ＞~2.5GB 訓練顯存之配方（含 4b GPU QLoRA）；OOM＝配方失敗、誠實留檔，不硬衝。  
8. **P4.E7 NoLaundering**：gold／LoRA 產物 `is_synthetic`／synthetic 標記恆真；不得洗成「真人知識」。  
9. **新增腳本紀律**：B2/B3 訓練腳本屬**新增可執行入口**，**首次提交即須含執行指令矩陣**（CLAUDE #18/#29）；無參數 graceful；`--selftest` 零外部依賴路徑。  
10. **停損優先於執念**：連續 **N=2** 輪（可拍板改 N）部署域無增益 → 該軸停損；不為「有跑訓練」而晉升（見 §六.1）。

---

## 三、自進化閉環（本地 LLM 軸）與四軸資料流

### 3.1 閉環主敘事（必須可指到帳本列）

```
┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ B4 gold／題庫 │──►│ B1 evolve_cycle │──►│ 可測增益？        │──►│ 人閘晉升         │
│ 累積／校驗    │   │ prompt-pack     │   │ held-out／部署域  │   │ local_model_    │
└──────┬───────┘   └────────┬────────┘   └────────┬─────────┘   │ version→serving │
       │                    │                     │否＝不晉升    └────────┬────────┘
       │                    │                     ▼                       │
       │                    │              迭代帳本記「無增益輪」          │
       │                    │              N 輪→停損（§六.1）             │
       │                    │                     │                       │
       │                    ▼                     ▼                       ▼
       │            （可選）B2 1.7b QLoRA／B3 CPU LoRA 實驗                │
       │                    │ 驗證／回滾（retire／卸 tag）                 │
       │                    └──────────────┬──────────────────────────────┘
       │                                   ▼
       └──────────────────── 回饋下一輪 gold／pack／題庫 ─────────────────┘
                              ＋ iteration_ledger 記一輪結案
```

**每輪最低交付物（機械可查）**  
1. 本輪新增／沿用的 gold／manifest hash（或「零新 gold、只重排 pack」誠實註記）  
2. `local_model_version` candidate（B1 必；B2/B3 若有訓）＋`eval_result`  
3. 增益判定：有／無／不可比（不可比≠有增益）  
4. 人簽結果：晉升／拒晉升／軸停損  
5. 回饋：下一輪題庫／pack 種子從哪來  

### 3.2 四軸總覽（手段層；納入閉環）

```
┌─────────────────────────────────────────────────────────────────────────┐
│ B4 資料先決（持續／可與 B1 並行）——閉環入口燃料                            │
│  bridge_deliberation → generate_questions → build_context               │
│       → teacher(本地 8b) → validate → sft.jsonl / gold 匯入              │
│  耐久：advisor_distill_* ＋ local_model_gold_sample（跨 base 可重用）     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ gold / SFT manifest
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   ┌──────────────┐    ┌────────────────┐    ┌────────────────┐
   │ B1 prompt-pack│    │ B2 QLoRA 1.7b  │    │ B3 CPU LoRA 4b │
   │ evolve_cycle  │    │ 窄任務特化工具 │    │ 過夜實驗       │
   │ 零訓練主線    │    │ ≠取代 8b      │    │ resume-safe    │
   └──────┬───────┘    └───────┬────────┘    └───────┬────────┘
          │                    │                     │
          └──────────┬─────────┴──────────┬──────────┘
                     ▼                    ▼
            local_model_version     lora_training_run（新）
            (candidate→人簽→serving)  artifact 路徑／checkpoint
                     │
                     ▼
              部署消費：serving_pack 快取／Ollama 特化 tag（B2）
              回滾：換 hash／retire／卸 LoRA tag
              帳本：local_ai_iteration_ledger（新；見 §四.4）
```

| 軸 | 在閉環中的角色 | 取代誰？ | 主要成本 |
|---|---|---|---|
| **B4** | **燃料**：累積／校驗 gold | 資料地基 | 本地 teacher 時間 |
| **B1** | **主迭代**：few-shot／系統提示包 | 不取代模型；改 serving pack | CPU＋短評測 |
| **B2** | **可選特化**：`qwen3:1.7b` 窄工具 | **不**取代 8b advisor | 4GB QLoRA＋權重鏈 |
| **B3** | **可選實驗**：4b 權重適配 | 失敗則停損轉 B1/B4 | 過夜 CPU、RAM 擠壓 |

**建議節奏（可並行處已標）**：  
拍板 `LAIEVO-P-yes`（＝舊 `ROUTEB-P-yes`）後 → **B1 立即可 go**（既有碼）∥ **B4 持續累積** → B2 **環境 spike 過關**才訓 → B3 **僅小集實驗**（可與 B2 spike 錯開，避免雙重吃 RAM）→ 每輪結案寫迭代帳本。

---

## 四、(a) 對應 table schema

### 4.1 既有——AI evolution（SSOT＝`scripts/migrate_ai_evolution_ddl.py`）

**`governance_proposal`**（人閘提案佇列；本路線 B 主線少用，保留）  
`proposal_id, kind, title, diff_text, evidence_refs, proposed_by, status∈{pending,approved,rejected,enacted,withdrawn}, decided_*, created_at`  
Trigger：內容送出即凍結；終態不可改。

**`local_model_gold_sample`**（append-only 金標帳本＝**耐久資產**）  

| 欄 | 型別／約束 | 用途 |
|---|---|---|
| `sample_id` | bigserial PK | |
| `prompt` / `gold_answer` | text | Q/A |
| `verdict` | `oracle_pass`／`teacher_gold`／`human_ruled`／`rejected` | 僅前三者入訓練視圖 |
| `teacher` | jsonb | 教師 provenance |
| `trigger_event` | jsonb NOT NULL | 「因為什麼事」 |
| `contains_private` | boolean NOT NULL | true→禁送外部（本路線本就本地） |
| `is_synthetic` | true CHECK | P4.E7 |
| `provenance` | jsonb | |
| `created_at` | timestamptz | |

Trigger：UPDATE/DELETE 全拒（P4.E3）。

**`local_model_version`**（版本註冊：prompt-pack **與** LoRA 共用）  

| 欄 | 用途 |
|---|---|
| `version_id` | PK |
| `base_model` | 如 `qwen3:4b`／`qwen3:1.7b`／`prompt_pack` 錨 |
| `lora_path` | B2/B3 權重路徑；B1 可 NULL |
| `train_sample_manifest_hash` / `anchor_hash` / `eval_code_hash` | 三 hash 釘死防挪門柱 |
| `gate_id` / `eval_result` | 閘與分數（jsonb；B1 含 `kind=prompt_pack`） |
| `status` | `candidate`／`serving`／`retired` |
| `promoted_by` / `promoted_at` | **晉升人簽** |

Trigger：非 candidate 不可改 hash／gate；晉升 serving 須人簽；禁 DELETE（退役＝retired）。

**結果落點**：B1 候選／評測 → `local_model_version`＋`eval_result`；serving pack 匯出 → `~/.cache/augur/serving_pack.txt`（非 DB）。Gold 新增 → `local_model_gold_sample`。

### 4.2 既有——advisor distill（SSOT＝`scripts/migrate_advisor_distill_ddl.py`）

**`advisor_distill_question`**  
`question_id, question UNIQUE, situation_label∈{1,2,3}, expected∈{ANSWER,DECLINE,REFUSE}, domain, topic_source, topic_ref, batch_tag, context_built, created_at`

**`advisor_distill_context`**（界線-B：真實檢索與 teacher 分欄）  
`context_id, question_id UNIQUE FK, context jsonb, n_citations, relevant, retrieval_scope, target_response, teacher_model, teacher_at, validated, validate_verdict, built_at`

**結果落點**：S5 通過 → `data/distill/sft*.jsonl`（gitignore）＋可選擇匯入 `local_model_gold_sample`（B4→B1/B2/B3 共用）。  
**隔離**：表前綴 `advisor_distill_*`；不落 knowledge／不進預測。

### 4.3 新表（B2/B3 需要）——`lora_training_run` 訓練 run 帳本

> 動機：`local_model_version` 記「產品候選版本」；訓練過程（checkpoint、OOM、resume、壁鐘）需 **append-friendly run 帳本**，避免把半成品塞進 version 列。  
> DDL 單一住所建議新腳本：`scripts/migrate_lora_training_ddl.py`（#12；拍板後才建）。

```sql
CREATE TABLE IF NOT EXISTS lora_training_run (
  run_id            text PRIMARY KEY,                 -- 如 lora-20260726T1530-1p7b-qlora
  kind              text NOT NULL CHECK (kind IN ('qlora_gpu_1p7b','lora_cpu_4b')),
  base_model        text NOT NULL,                    -- HF id 或 ollama tag 錨
  status            text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','running','paused','succeeded','failed','aborted')),
  sample_manifest_hash text NOT NULL,                -- 訓練樣本清單 hash（對齊 version）
  n_samples         int  NOT NULL CHECK (n_samples > 0),
  hyperparams       jsonb NOT NULL DEFAULT '{}',      -- lr/epochs/rank/seq/batch/...
  artifact_dir      text,                             -- 本機絕對路徑（owned_local）
  checkpoint_path   text,                             -- resume 點
  metrics           jsonb NOT NULL DEFAULT '{}',      -- loss／eval 片段（#15 可溯）
  error_text        text,
  version_id        text REFERENCES local_model_version(version_id),  -- 成功後掛候選；可先 NULL
  started_at        timestamptz,
  finished_at       timestamptz,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now()
);

-- 半成品可更新（與 gold append-only 不同）；禁刪（留失敗史）
CREATE OR REPLACE FUNCTION lora_run_no_delete() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'lora_training_run % 不得刪(失敗亦留檔)', OLD.run_id;
END $$ LANGUAGE plpgsql;
-- BEFORE DELETE → lora_run_no_delete

CREATE INDEX IF NOT EXISTS idx_lora_run_status ON lora_training_run (status, kind);
```

**結果落點對照**

| 產出 | 落哪 |
|---|---|
| 訓練過程／resume | `lora_training_run` |
| 成功候選（含 eval） | `local_model_version`（`lora_path`＋三 hash＋`eval_result`） |
| 晉升後服務 | Ollama 本地 tag **或** serving pack（B1）；DB status=`serving` |
| SFT 檔 | `data/distill/` 或 `~/.cache/augur/lora/`（gitignore／本機） |

**不新建**：不把 LoRA 權重 byte 存進 PG；不新建 knowledge 表。

### 4.4 新表（自進化迭代帳本）——`local_ai_iteration_ledger`

> 動機：閉環「學了什麼／何時／因為什麼／有無增益／是否停損」須 **可 SQL 直查**，不靠敘事；與預測自進化帳本**分表**（禁共用 iteration id 命名空間混淆）。  
> DDL 建議併入 `scripts/migrate_ai_evolution_ddl.py` 冪等擴充，或新腳本 `scripts/migrate_local_ai_iteration_ddl.py`（拍板後定單一住所）。

```sql
CREATE TABLE IF NOT EXISTS local_ai_iteration_ledger (
  iteration_id      text PRIMARY KEY,                 -- 如 laievo-20260726-r03
  axis              text NOT NULL
    CHECK (axis IN ('B1','B2','B3','B4','mixed')),
  status            text NOT NULL DEFAULT 'open'
    CHECK (status IN ('open','closed_gain','closed_no_gain','stopped','aborted')),
  trigger_code      text,                             -- 例 LAIEVO-B1-go
  gold_delta        jsonb NOT NULL DEFAULT '{}',      -- 新增 sample_ids／manifest_hash／n
  candidate_version_id text REFERENCES local_model_version(version_id),
  serving_before    text,                             -- 晉升前 serving version_id（可空）
  serving_after     text,                             -- 晉升後；未晉升則＝before 或 NULL
  eval_summary      jsonb NOT NULL DEFAULT '{}',      -- 分數差分；#15 可溯 stdout／DB
  gain              boolean,                          -- NULL＝不可比；true/false＝裁決
  stop_loss_hit     boolean NOT NULL DEFAULT false,   -- 本輪是否觸發軸停損
  consecutive_no_gain int NOT NULL DEFAULT 0,         -- 結案時該軸累計無增益輪
  steps_json        jsonb NOT NULL DEFAULT '[]',      -- [{step,script,rc,artifacts}] 機械步
  consumed_briefs   jsonb NOT NULL DEFAULT '[]',
  -- [{path,iteration_id,kind:prediction_brief}] 僅 TWEVO 唯讀摘要 refs；禁 panel
  hypothesis_hints_out jsonb NOT NULL DEFAULT '[]',
  -- [{hint_text,suggested_map,provenance}] 假說文字→人閘→PME curate；禁直寫 prodset
  feedback_next     jsonb NOT NULL DEFAULT '{}',      -- 回饋下一輪：題庫／pack 種子指針
  cross_notify_json jsonb NOT NULL DEFAULT '{}',      -- kill/stop 共享通知（非合併表）
  notes             text,
  opened_at         timestamptz NOT NULL DEFAULT now(),
  closed_at         timestamptz,
  closed_by         text                              -- 人簽結案者；禁腳本自填 hugo
);

-- 結案後禁改增益裁決欄（防事後美化）；開輪可補 notes
-- 禁 DELETE（失敗輪亦留檔；對齊 P4.E3 精神）

CREATE INDEX IF NOT EXISTS idx_laievo_ledger_axis_status
  ON local_ai_iteration_ledger (axis, status, opened_at DESC);
```

**與演化史呈現**：既有構想 `evolve_history_report.py`（進化計畫 §五）可讀本表＋`local_model_version` 產年表；本檔不強制先寫報告腳本——**帳本列優先於漂亮報告**。

---

## 五、(b) 對應 python 程式規畫

### 5.1 既有腳本——消費方式（本路線直接用）

| 腳本 | 職責 | 本路線怎用 | 主要 I/O 表 |
|---|---|---|---|
| `migrate_ai_evolution_ddl.py` | 三表＋trigger 冪等 | B1 前置 `--check`／必要時 `--apply`；可擴 `local_ai_iteration_ledger` | evolution 表＋ledger |
| `evolve_cycle.py` | insight→semantics→promptpack→eval | **B1 主入口**／閉環核心迭代 | 讀 catalog／correlation／knowledge_item；寫 gold＋version |
| `migrate_advisor_distill_ddl.py` | distill 兩表 | B4 前置 | `advisor_distill_*` |
| `advisor_distill_generate_questions.py` | S2 生題 | B4 | → `advisor_distill_question` |
| `advisor_distill_build_context.py` | S3 真檢索 | B4 | → `advisor_distill_context` |
| `advisor_distill_teacher.py` | S4 本地 8b teacher | B4（`DISTILL_TEACHER_MODEL=qwen3:8b`，`--run --confirm`） | 更新 `target_response` |
| `advisor_distill_validate.py` | S5 硬校驗→jsonl | B4；GATE drop≤40% | 讀 context；→ `data/distill/sft*.jsonl` |
| `bridge_deliberation_distill.py` | 審議→DECLINE 題 | B4 橋接題庫 | → `advisor_distill_question`（`topic_source=deliberation`） |

**既有 CLI 矩陣（摘要，完整見各檔標頭）**

```
# B1（閉環主輪）
python scripts/evolve_cycle.py                 # 唯讀現況
python scripts/evolve_cycle.py --cycle         # 一輪
python scripts/evolve_cycle.py --search-packs  # 選材搜尋
python scripts/evolve_cycle.py --eval-all
python scripts/evolve_cycle.py --export-pack
python scripts/evolve_cycle.py --selftest

# B4（燃料）
python scripts/bridge_deliberation_distill.py --run --batch-tag delib_laievo
python scripts/advisor_distill_generate_questions.py --pilot|--n-incorpus N --batch-tag ...
python scripts/advisor_distill_build_context.py --run [--limit N]
python scripts/advisor_distill_teacher.py --run --confirm
python scripts/advisor_distill_validate.py --run --out data/distill/sft_laievo.jsonl
```

**晉升（人，非腳本自動）**——`evolve_cycle` 印出的 SQL 形：  
`UPDATE local_model_version SET status='serving', promoted_by='hugo', promoted_at=now() WHERE version_id='…';`  
然後 `--export-pack`。退役＝`status='retired'`＋清 serving pack＝回滾基線。  
**結案**：同步寫／更新 `local_ai_iteration_ledger`（`closed_by` 人填；腳本可 `--close-iteration` 僅在人提供簽名旗標後寫入）。

### 5.2 新腳本（拍板後才寫；首次提交即須矩陣）

命名慣例：`scripts/`＝**動作動詞片語**（#18）。

#### (0) `scripts/close_local_ai_iteration.py`（帳本結案／停損計數）

- **職責**：開輪／結案 `local_ai_iteration_ledger`；依軸累計 `consecutive_no_gain`；達 **N** → 建議 `stopped`（**不**自動改 serving）；可寫 `cross_notify_json`；可登錄 `consumed_briefs`／`hypothesis_hints_out`。  
- **簽名草案**：`--open --axis B1 [--trigger LAIEVO-B1-go]`｜`--close --iteration-id … --gain yes|no|na --promoted-by hugo`｜`--status`｜`--emit-hypothesis-hints PATH`｜`--selftest`。  
- **I/O**：讀 `local_model_version`／eval；寫 ledger。

#### (0b) `scripts/report_dual_evolution_week.py`（可選；與 TWEVO 共用規畫）

- **職責**：並列讀 `local_ai_iteration_ledger`＋`evolution_iteration_ledger`；印本週狀態／停損／brief path；**不合併表、不跨閘晉升**。  
- **簽名草案**：`--week`｜`--selftest`。

#### (1) `scripts/migrate_lora_training_ddl.py`

- **職責**：冪等落地 `lora_training_run`＋禁刪 trigger；`--check`／`--apply`／`--selftest`。  
- **簽名草案**：`--check`｜`--apply`｜`--selftest`；無參數＝印矩陣＋`--check`。  
- **I/O**：寫 catalog；不寫業務列。

#### (2) `scripts/export_evolution_sft.py`（B4→B2/B3 橋）

- **職責**：自 `local_model_gold_sample`（verdict∈可訓）∪／或 distill 通過集，匯出訓練 jsonl＋`sample_manifest_hash`；標 `contains_private` 過濾策略。  
- **簽名草案**：  
  `--from gold|distill|both`  
  `--out PATH`  
  `--min-verdict oracle_pass,teacher_gold,human_ruled`  
  `--limit N`  
  `--dry-run`｜`--selftest`  
- **I/O**：讀 gold／distill；寫本機 jsonl（gitignore）；stdout 印 hash。

#### (3) `scripts/train_qlora_small.py`（**B2**）

- **職責**：在 4GB 上對 **~1.7B** base 做 QLoRA（分類／改寫／extract 窄任務）；寫 checkpoint；成功則註冊 `local_model_version` candidate＋更新 `lora_training_run`。  
- **不**：改 8b advisor 權重；不自動 serving。  
- **簽名草案**：  
  ```
  python scripts/train_qlora_small.py              # 矩陣＋VRAM／依賴偵測（安全）
  python scripts/train_qlora_small.py --spike      # 環境鏈：import peft/bnb、估顯存、單 step dry
  python scripts/train_qlora_small.py --run --data PATH --epochs 1 --rank 8 --run-id ...
  python scripts/train_qlora_small.py --resume --run-id ...
  python scripts/train_qlora_small.py --register-only --run-id ...  # 已有 artifact 只註冊 candidate
  python scripts/train_qlora_small.py --selftest
  ```  
- **I/O**：讀 SFT 檔；寫 `lora_training_run`、artifact_dir、（成功）`local_model_version`。  
- **硬限**：啟動前查 free VRAM；＜門檻或 OOM → `status=failed`、exit≠0、**不重試風暴**。

#### (4) `scripts/train_lora_cpu.py`（**B3**）

- **職責**：`qwen3:4b` 級 **CPU LoRA**；小資料集（建議先 ≤171／或 ≤500）；多 checkpoint；**resume-safe** 必備。  
- **簽名草案**：  
  ```
  python scripts/train_lora_cpu.py                 # 矩陣＋RAM 警告
  python scripts/train_lora_cpu.py --run --data PATH --epochs 1 --run-id ...
  python scripts/train_lora_cpu.py --resume --run-id ...
  python scripts/train_lora_cpu.py --selftest
  ```  
- **I/O**：同 B2 帳本；`kind='lora_cpu_4b'`。  
- **操作約束**：訓練窗建議降 PG `shared_buffers` 或錯開重查詢（進化計畫已警告互擠）；壁鐘預期 **天級**。

#### (5) `scripts/publish_lora_ollama.py`（B2/B3 權重鏈尾段）

- **職責**：PEFT adapter →（可選 merge）→ GGUF／Modelfile → `ollama create` 本地 tag；**不推遠端**。  
- **簽名草案**：`--from-run RUN_ID`｜`--adapter PATH`｜`--tag NAME`｜`--dry-run`｜`--selftest`。  
- **I/O**：讀 artifact；寫本地 Ollama；更新 `local_model_version.lora_path`／eval 附註。

#### (6) （可選）`scripts/eval_local_model_deploy.py`

- **職責**：部署域迷你金標（MCP summarize／extract／DECLINE 誠實性）＋171 錨集回歸；寫入 `eval_result`；錨 `eval_code_hash`。  
- **用途**：B1/B2/B3 晉升前同一把尺（進化計畫「補部署工作域評測」）；帳本 `eval_summary` 引用同一輸出。  
- 若 B1 既有 held-out 已夠第一輪，本檔可 **P1.5 再補**，不阻塞 B1 go。

### 5.3 元件圖（執行層）

```
[DB gold/distill]──export_evolution_sft──►[jsonl+manifest_hash]
        │                                      │
        │                              ┌───────┴────────┐
        │                              ▼                ▼
        │                     train_qlora_small   train_lora_cpu
        │                              │                │
        │                              └───────┬────────┘
        │                                      ▼
        │                            lora_training_run
        │                                      │
        │                            publish_lora_ollama
        │                                      ▼
evolve_cycle ──► local_model_version(candidate) ──人簽──► serving
        │                                      │
        └──► serving_pack.txt / Ollama tag ◄────┘
                         │
                         ▼
              local_ai_iteration_ledger（開輪／結案／停損計數）
                         │
                         └──► 回饋下一輪 gold／pack（B4／B1）
```

---

## 六、分階段、迭代節奏、停損、驗收與回滾

> **總閘**：`LAIEVO-P-yes`（別名 `ROUTEB-P-yes`）＝採納本計畫書；各軸另需 go 碼才動工。  
> **明示**：本計畫書拍板後才動工；B2/B3 訓練腳本屬新增可執行入口，**首次提交即須含執行指令矩陣（#18/#29）**。

### 6.1 迭代節奏與停損（自進化核心）

| 規則 | 內容 |
|---|---|
| **一輪定義** | 自 ledger `--open` 起，至增益裁決＋（可選）人簽晉升／拒晉升＋`--close` |
| **建議 cadence** | B1／B4：有新 gold 或 pack 搜尋結果即可開輪（可週內多輪）；B2／B3：spike／訓完才算一輪（週～月級） |
| **增益定義** | 部署域金標或 held-out：**pack-on／適配後 ≥ 基線**，且錨集無嚴重退步；分數須 trace 程式／DB（#15） |
| **無增益** | 不晉升；`gain=false`；`consecutive_no_gain += 1` |
| **停損 N** | 預設 **N=2**（同軸連續無增益輪）；達 N → `stop_loss_hit=true`、軸建議 `stopped`；資源回 B4 累積或改題庫／改評測尺，**不**空轉同配方 |
| **不可比** | `gain=NULL`：**不**計入停損累計，亦**不**算有增益；須補評測尺後重開 |
| **回滾** | serving→retired；清 pack／卸 tag；ledger 記 `serving_after` 與回滾註記 |
| **禁** | 自動 cutover；為消化 GPU 時間而晉升；把「loss 下降」當部署增益；advisor 輸出直接改 prodset／降閾／APPLY |

### 6.2 每輪驗收判準（機械可驗；對齊 TWEVO V 風格）

| ID | 判準 | 驗法（機械） |
|---|---|---|
| **L-V0** | FZ-keep／零市場 API | 本輪 `steps_json`／指令清單無 FinMind／FRED；不呼叫預測 `sync_*` |
| **L-V1** | 晉升人閘 | DB 無「無 `promoted_by` 的 serving 新列」；`evolve_cycle` 源碼無自動 `status='serving'` UPDATE（`--selftest`／rg 鎖） |
| **L-V2** | 帳本完整 | ledger 終態；`closed_at`／`closed_by`（人簽）；`steps_json` 每步有 `rc`；`consecutive_no_gain` 可重算 |
| **L-V3** | 增益誠實 | `gain=true` ⇒ `eval_summary` 含可溯分數差分；`gain=NULL` 不計停損亦不晉升 |
| **L-V4** | owned_local | LoRA／jsonl path 落本機 gitignore；`contains_private` 策略遵守；不入公開 repo |
| **L-V5** | 隔離 | 本輪無寫入 `feature_values`／`evolution_production_feature_set`／`knowledge_*`（SQL／REVOKE） |
| **L-V6** | brief 契約 | `consumed_briefs` 僅 path／iteration refs；檔內無 panel 陣列；provenance 標 `prediction_brief` |
| **L-V7** | 假說出口紀律 | `hypothesis_hints_out` 若非空 → **無**對應自動 APPLY／prodset delta；僅人審 curate 路徑 |
| **L-V8** | 停損 | 達 N → `stop_loss_hit=true`∧`status=stopped`∧`cross_notify_json ? 'stop_no_gain'`；**不**改 serving |
| **L-V9** | 4GB／錯峰 | B2：spike／run 記錄 peak VRAM；與 TWEVO I3／I6 重疊時有 defer 註記或錯峰證據 |

### 階段 B0｜前置核對（0.5 日，機械）

| 項 | 驗收（可機械） |
|---|---|
| DDL | `migrate_ai_evolution_ddl.py --check` 三表＋trigger 在；`migrate_advisor_distill_ddl.py --check` 兩表在 |
| Ollama | `qwen3:8b`／`qwen3:4b`／`nomic-embed-text` 可 `api/tags` 見 |
| 隔離 | 確認無計畫把 distill 寫入 knowledge_*（code review／既有 REVOKE） |
| 凍結 | 本階段指令清單含 **零** FinMind／FRED |
| 正交 | 確認不呼叫預測 `train_*`／不寫 `feature_values` 作為本閉環產出；知悉 TWEVO 對偶 §8／本檔 §十二 |
| 對偶現況 | 可唯讀知：prodset n=2、MAP-E012 CLOSED、D2 第一關、`evaluated_pass=0`（HANDOFF；**不**當 LLM 增益） |

### 階段 B1｜prompt-pack 主線（優先；既有碼＝閉環主輪）

**內容**：開 ledger → 跑 `evolve_cycle --cycle`／`--search-packs`；檢視 candidate `eval_result`；hugo 人簽晉升或拒；`--export-pack`；結案 ledger。

**驗收**  
1. 新 `local_model_version` 列 `eval_result.kind=prompt_pack`，含 sample_ids／分數。  
2. held-out 或 `--eval-all`：**pack-on ≥ pack-off**（或誠實記錄無增益則不晉升）。  
3. 晉升後 `~/.cache/augur/serving_pack.txt` 存在且對應 serving `version_id`。  
4. `evolve_cycle --selftest` 綠；程式內無自動 `status='serving'` UPDATE。  
5. 對應 `local_ai_iteration_ledger` 列已 `closed_*`（拍板後有帳本 DDL 起強制）。

**回滾**：serving→retired；`--export-pack` 刪快取＝MCP 回基線。

**拍板碼**：`LAIEVO-B1-go`（＝`ROUTEB-B1-go`）

### 階段 B4｜資料先決（與 B1 並行；閉環燃料；B2/B3 品質前置）

**內容**：bridge →（可選 generate）→ build_context → teacher(本地) → validate；將通過樣本匯入 gold 或供 export；可單獨開 B4 輪（累積無評測亦可 `gain=NULL` 結案，註明「燃料輪」）。

**驗收**  
1. `advisor_distill_validate --run`：**drop rate ≤ 40%**（pilot 先例 37.6%）。  
2. 產出 jsonl 列數與 DB `validated=true` 可對上（#15）。  
3. bridge 題 `expected=DECLINE`（「2改」不變）。  
4. 抽樣：ANSWER 含可溯 context；禁無據數字（guard 路徑）。  
5. **不**要求一次到 3k；以「可訓小集＋持續累積」為成功（171 可作 B3 起點）。

**回滾**：拒絕批次不晉升即可；append-only gold 用 `verdict=rejected` 策略（若僅 distill 檔則刪檔不入 gold）。

**拍板碼**：`LAIEVO-B4-go`（＝`ROUTEB-B4-go`；可與 B1 同批）

### 階段 B2a｜QLoRA 環境 spike（先於真訓）

**內容**：裝依賴；`ollama pull` 或 HF 下載 **1.7b** 權重（本地下載≠API 解凍）；`train_qlora_small --spike`。

**驗收**  
1. `--spike` 單 step 不 OOM；記錄 peak VRAM（stdout／`metrics`）。  
2. `peft`／量化後端 import 成功；版本釘在 requirements 片段或計畫附錄鎖定策略。  
3. 失敗則 **B2 停損**，資源回 B1/B4（誠實留 `lora_training_run.status=failed`）。

**拍板碼**：`LAIEVO-B2-spike-go` → 過關後另下 `LAIEVO-B2-train-go`（＝舊 `ROUTEB-B2-*`）

### 階段 B2b｜1.7b 窄任務真訓＋註冊

**內容**：小集 QLoRA → publish 本地 tag → 部署域評測 → candidate；**不**自動替換 8b；結案 ledger。

**驗收**  
1. `lora_training_run.status=succeeded`＋`sample_manifest_hash` 可重算一致。  
2. `local_model_version` candidate 三 hash 齊；`lora_path` 指向本機。  
3. **窄任務金標**優於同任務上未適配 1.7b；且 **8b advisor 行為回歸不變**（對照測）。  
4. 通用錨集（若有）零嚴重退步——若 1.7b 只當工具呼叫，則驗「路由仍走 8b 主答」。  
5. 無增益 → 不晉升；計入 B2 停損累計。

**回滾**：不晉升；刪 Ollama tag；version=`retired`。

### 階段 B3｜CPU LoRA 過夜實驗

**內容**：≤171（或明示上限）×少量 epoch；checkpoint 每 N step；可 `--resume`；結案 ledger。

**驗收**  
1. 殺進程後 `--resume` 自 checkpoint 續跑（至少實證一次）。  
2. 跑完有 `metrics`（train loss 曲線片段）寫入 DB。  
3. 部署域評測：**無增益 → 停損計數**；連續 N=2 → 軸停；有增益才進人簽討論。  
4. 不拖垮 WSL：記錄 RAM；必要時文件化「訓練窗停重查詢」。

**拍板碼**：`LAIEVO-B3-go`（＝`ROUTEB-B3-go`；建議 B2 spike 結論出來後再開，避免雙重吃 RAM）

### 階段總序建議

```
LAIEVO-P-yes  （＝ ROUTEB-P-yes）＋可選 DUAL-IFACE-yes
   ├─ LAIEVO-B0-go          ▸ 前置核對（可與 TWEVO-S0 同批）
   ├─ LAIEVO-B1-go          ▸ 立即（閉環主線；錯峰 embed）
   ├─ LAIEVO-B4-go          ▸ 並行累積 gold（燃料）
   ├─ LAIEVO-B2-spike-go    ▸ 依賴安裝＋VRAM 實證
   │     └─ LAIEVO-B2-train-go
   └─ LAIEVO-B3-go          ▸ 錯開；小集實驗
每輪 ──► local_ai_iteration_ledger 結案；無增益×N ──► 軸停損
```

---

## 七、誠實依賴與版本策略

| 依賴 | 用途 | 策略 |
|---|---|---|
| **PyTorch** | 訓練 runtime | 釘 CUDA 版與驅動相容；CPU 輪可另用 CPU wheel |
| **transformers** | 載入 Qwen3 | 與模型卡要求對齊；升級須重跑 spike |
| **peft** | LoRA／QLoRA | 主依賴；API 穩定後鎖次要版 |
| **bitsandbytes** | NF4 量化（B2） | **需要 CUDA 建置**；spike 失敗則 B2 配方改「非 bnb」備案或停損——**不假裝 CPU 可替** |
| **unsloth**（可選） | 加速／省顯存 | **可選**；若與 1650／驅動不合則 **跳過**，走 peft 原味；不設為硬依賴 |
| **llama.cpp / convert 工具** | GGUF | `publish_lora_ollama` 鏈；版本與 Ollama 0.32.x 相容性須 spike |
| **qwen3:1.7b** | B2 base | `ollama pull qwen3:1.7b` **或** HF 權重本地下載；屬模型檔取得，**非** FinMind／FRED 解凍問題 |
| **accelerate** | 裝置編排 | 建議與 transformers 同鎖 |

**安裝落點**：建議 `requirements-lora.txt`（與主 `requirements` 分離），避免預測／DB 環境被 CUDA 輪汙染；文件註明「僅 B2/B3 機器環境」。

**磁碟**：HF 快取與 adapter 預估數 GB；路徑建議 `~/.cache/augur/lora/`（owned_local）。

---

## 八、風險登記

| 風險 | 後果 | 緩解 |
|---|---|---|
| 4GB OOM | B2 不可行 | spike 門；失敗轉 B1 |
| CPU LoRA 過慢／RAM 擠 PG | 機器不可用 | 小集、錯開、resume、可 abort |
| 訓出幻覺 | 部署變差 | S5 guard＋部署域金標；無增益不晉升；停損 N |
| 權重外洩 | 私有語料回吐 | owned_local；不入 git；contains_private |
| 自動晉升誘惑 | 監督空洞 | 碼與 trigger 雙鎖；P5.W5 未裁決前禁止排程 cutover |
| 依賴地獄 | 環境壞 | 分離 requirements；spike 先行 |
| 把 1.7b 當 8b 用 | 主答品質崩 | 架構上 **工具分流**；8b 仍為 advisor |
| 與預測自進化混帳 | 假兆／錯晉升 | §〇.1 正交；分表分碼；禁共用 go |

---

## 九、與昨日進化計畫的邊界（防重複／防復辟）

| 昨日結論 | 本路線 B／自進化態度 |
|---|---|
| 自對弈永動機已擊倒 | **不重提、不做** |
| 4b GPU QLoRA 已反證 | **不做**；改 1.7b QLoRA（B2） |
| Tier1 prompt-pack | **＝B1 主線＝閉環主輪** |
| Tier2 CPU LoRA／1.7b | **＝B3／B2**，本檔補 schema＋腳本規畫＋迭代帳本 |
| 外部教師除役 | 維持；B4 teacher＝本地 8b |
| 自動夜間 cutover | **不做**；晉升人簽 |
| 換 12GB 卡 | 屬路線 A，本檔僅一句對照 |
| 「無窮」飛輪 | 降格為：**有新 gold／可測尺才開輪**；速率由真實教師訊號決定 |

---

## 十、待用戶拍板碼（自進化語意＋舊別名）

### 10.1 主碼（建議使用）

| 碼 | 含義 |
|---|---|
| `LAIEVO-P-yes` | 採納本計畫書為**本地 AI 自進化（路線 B）** SSOT；**仍不自動開工各軸** |
| `DUAL-IFACE-yes` | （可選）採納與 TWEVO 之協作介面（本檔 §十二／短檔） |
| `LAIEVO-B0-go` | （可選明示）前置核對 B0；可與 `TWEVO-S0` 同批 |
| `LAIEVO-B1-go` | 授權跑既有 `evolve_cycle` 主線並可人簽晉升＋開／結迭代帳本 |
| `LAIEVO-B4-go` | 授權蒸餾／bridge 累積（本地 teacher；注意壁鐘） |
| `LAIEVO-B2-spike-go` | 授權寫依賴＋`train_qlora_small --spike`（含 pull 1.7b） |
| `LAIEVO-B2-train-go` | spike 通過後授權真訓＋publish 本地 tag |
| `LAIEVO-B3-go` | 授權 CPU LoRA 小集過夜實驗 |
| `LAIEVO-P-no`／`LAIEVO-Bx-hold` | 否決或暫緩該軸 |
| `LAIEVO-STOP-N=k` | （可選）改停損連續無增益輪數為 k；未拍則 **N=2** |

### 10.2 舊別名對照（防混淆；等價有效）

| 舊碼（路線 B） | 等價新碼（自進化） |
|---|---|
| `ROUTEB-P-yes` | `LAIEVO-P-yes` |
| `ROUTEB-B1-go` | `LAIEVO-B1-go` |
| `ROUTEB-B4-go` | `LAIEVO-B4-go` |
| `ROUTEB-B2-spike-go` | `LAIEVO-B2-spike-go` |
| `ROUTEB-B2-train-go` | `LAIEVO-B2-train-go` |
| `ROUTEB-B3-go` | `LAIEVO-B3-go` |
| `ROUTEB-P-no`／`ROUTEB-Bx-hold` | `LAIEVO-P-no`／`LAIEVO-Bx-hold` |

> 對話中打出舊碼 **視為同意對應新碼**；新文件與帳本列優先寫 `LAIEVO-*`。  
> **勿**與台股預測自進化拍板碼（`TWEVO-*`）混用（見 §十二.5）。

### 10.3 與 TWEVO 同批／分批建議

| 可同批 | 必須分開 |
|---|---|
| `LAIEVO-P-yes`＋`TWEVO-P-yes`＋`DUAL-IFACE-yes`＋`FZ-keep`＋`GATE-keep` | 人簽 serving ≠ `TWEVO-APPLY-go` |
| `LAIEVO-B0`／`B1`／`B4` ∥ `TWEVO-S0`／`S1`／`S2`（無 APPLY；錯峰 embed） | `LAIEVO-B2-train`／`B3` ≠ `TWEVO-S3`／`S4`（重訓／arena） |
| | 停損 N：`LAIEVO-STOP-N` 與 `TWEVO-N` 各改各的 |

**建議首批**：`TWEVO-P-yes`＋`LAIEVO-P-yes`＋`DUAL-IFACE-yes`＋`FZ-keep`＋`GATE-keep` → 再分軸 `LAIEVO-B1-go`／`B4-go` 與 `TWEVO-S0-go`。

---

## 十一、30 分鐘閱讀地圖

1. §〇–§〇.1（定錨＋與台股正交）＋§二（硬邊界）＋§十二（對偶介面，可掃）  
2. §三 閉環圖＋四軸  
3. §六 迭代／停損／L-V*＋階段驗收＋拍板碼  
4. 需要實作時再讀 §四 schema、§五 腳本、§七 依賴  

---

## 十二、與對偶計畫交互（TWEVO；正交＋協作介面）

> **對偶檔**：`reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md`（§8）  
> **可選矩陣短檔**：`reports/augur_dual_self_evolution_interface_20260726.md`

### 12.1 正交重申

兩個閉環、兩本帳（`local_ai_iteration_ledger` ≠ `evolution_iteration_ledger`）、兩組晉升閘（人簽 serving ≠ PME APPLY）。共享紅線：FZ-keep、#1／#15、owned_local、禁自動下單、訓過≠變聰明。

### 12.2 預測 → advisor（本閉環如何消費）

| 可消費 | 禁止 |
|---|---|
| TWEVO `export_evolution_advisor_brief` 產物／gap 報告 path（登錄 `consumed_briefs`） | raw panel／整庫特徵列 |
| ledger 結論級欄位、近失**特徵名**、已 settle scoreboard 公開數字（標 as-of＋出處） | 未過閘 IC 當「確立級」教材；把 paper arena 說成可交易 |
| MAP／D2 **狀態句**（人審）作題情境 | 把 probe 當雙綠成功故事灌 gold |

消費後：可進 gold／pack 選材之**情境註記**；`provenance` 標 `prediction_brief`；**P4.E7** 不得洗成真人知識。

### 12.3 advisor → 預測（本閉環可輸出什麼）

| 可輸出 | 禁止 |
|---|---|
| `hypothesis_hints_out`：假說文字／建議 map 對（文獻錨） | 直接 UPDATE prodset／queue／降閾／呼叫 `apply_evolution_promotions` |
| 匯出給 Steward 的 curate 提示檔 | LoRA／embedding／teacher 答當特徵權重 |

人閘後才進 PME `curate_pme_map_expand`／MAP——**無自動橋**。

### 12.4 錯峰／kill 通知／週儀表

* **錯峰**：B4 embed／B2／B3 **避開** TWEVO I3 local-gates（~25–35min）與 I6 `train_ranker`；`close_local_ai_iteration`／訓練腳本可偵測對偶 `status=running` 後 `--defer-heavy`（V2 C8 統一名；原文裸 `--defer` 與 TRI 契約名歧異、2026-07-26 更正）。  
* **通知**：本側停損或讀到 PME `kill=halt` → 寫 `cross_notify_json`；**不**自動 halt 對方 APPLY／serving。  
* **週儀表**：`report_dual_evolution_week.py` 並列兩 ledger。

### 12.5 拍板交叉

見 §10.3；與 TWEVO §8.5 對稱。

---

**本檔完。標 [I]。實作零授權直至對應 go 碼。全程零市場 API；advisor 只本機 Ollama；owned_local；訓過≠變聰明；與 TWEVO 正交協作。**
