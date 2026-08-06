---
title: KH0→KH9 專案計畫書｜全資料至少入 KH0＋逐層推進
subtitle: 對齊 gov 治權／IMPORT-QUAL／FT-COV／admit_depth；KH10 明確不納入
status: plan_first
date: 2026-08-06
viewpoint: 2026-08-06T09:15+08:00
layer: "[I]"
role: KH0–KH9 執行專案 SSOT（補憲章底線＋runtime 水印＋gov 真相對照）
ssot_code: KH0-KH9-PROJECT-PLAN-20260806
sole_steward: true
self_reported: true
depends_on:
  - docs/系統架構大憲章_v1.54.0.md
  - reports/augur_ten_layer_knowhow_architecture_plan_20260728.md
  - reports/augur_kh0_understanding_quality_20260730.md
  - scripts/run_kh_chain.py
  - src/augur/knowledge/auto_admit.py
  - audits/IMPORT-QUAL-GATE-S2-CLOSED-20260729.md
  - audits/KH8-KH9-MIN-LAND-CLOSED-20260729.md
gov_map: audits/GOV-TO-KH0-KH9-MAP-20260806.md
inherits_boundaries:
  - approve／activate 唯人（TTY+superuser／CLI）
  - AI assist ≠ 放行
  - FZ/GATE-keep · skip-sync-B · no-SIM-apply
  - hold Phase1 A→B3（市場日更軸正交）
  - KH10 不納入本計畫天花板（自我背書）
---

# KH0→KH9 專案計畫書（2026-08-06）

> **一句**：凡已入庫／可理解之資料，**一律至少達 KH0**；再依 `admit_depth` 0→9 推進至可權衡／合成的紀律智慧線。本檔＝該專案的執行藍圖（[I]），對齊 `http://localhost:8500/gov` 唯讀真相與 `run_kh_chain.py`。  
> **性質**：plan-first；**不創 [N]**；不代簽 approve／activate；不因本檔自動全庫 `--run`。  
> **與既有十層架構**：`augur_ten_layer_knowhow_architecture_plan_20260728.md`＝能力語義藍圖；**本檔＝憲章底線＋runtime 水印＋gov 對照＋波次 GO**。兩者疊用，不互廢。

---

## 0. Steward 任務定錨

```
所有的資料至少都能入 KH0
→ 寫出詳細專案計畫書規畫 KH0 到 KH9
```

| 是 | 不是 |
|---|---|
| 普遍口徑：**全部** `knowledge_item` 為 KH0 分母（標題即語意；無原文不豁免） | 只量「有全文者」再宣稱破口 0（窄口徑假綠） |
| 逐層可機械驗收的推進計畫（0→9） | 默授 KH10／自我背書進化 |
| 對齊 gov：治權覆蓋、IMPORT-QUAL、KIP、FT-COV、assist | web／AI 觸發 approve／activate |
| 與市場 S1→S5 日更軸**正交**（∥ hold #1+#2+#10） | 把 KH 全庫推進塞進 B3 standing |

---

## 1. 名詞對齊（必讀）

### 1.1 三套層號 · 本檔裁決

| 符號 | 來源 | 本檔用法 |
|---|---|---|
| **憲章 KH0** | 大憲章 v1.52–v1.54 | **底線義務**：「凡有可理解內容 → 至少被理解一次」 |
| **runtime depth 0…9** | `auto_admit.LAYER_NAMES`／`evaluate_layer` | **水印**：`knowhow_auto_admit_state.admit_depth` |
| **十層藍圖 KH1…KH10** | ten-layer 計畫 | 能力敘事；映射見 §2 |

**裁決**：本專案計畫書的主軸＝**runtime KH0→KH9**（`CEILING=9`），並把**憲章 KH0**落成 depth-0 的**強化驗收**（覆蓋＋品質路徑，見 §3.0），不是另開平行宇宙。

| depth | `LAYER_NAMES` | 一句 |
|---:|---|---|
| 0 | RAW／憲章 KH0 落點 | 内容可理解且已評（目標：標題或全文皆可） |
| 1 | Qualification | IMPORT-QUAL 合格或誠實旁路正名 |
| 2 | Admission Assist | 預審／來源就緒；**不**改審批終態 |
| 3 | Terminal | 終態材料就緒（text／sentence） |
| 4 | Retrieval-Answer | KH4 eligible／可檢索可答基線 |
| 5 | Axis | 逐 item `kh_axis_state=ready` |
| 6 | Interaction | 逐 item `interaction_state=ready` |
| 7 | Adversarial | KH7 eligibility（現行庫級；待收緊） |
| 8 | Evidence | 證據權衡（現行**不具鑑別力→一律 fail**） |
| 9 | Synthesis | 合成／回放（min-LAND；現況極薄） |
| 10 | Governance | **本計畫不納入**（`run_kh_chain` 硬頂 9） |

### 1.2 入口底線（憲章 · 不可刪）

1. 已入 staging → **不得**因 metadata 缺漏 `rejected`；判死唯一理由＝**無可理解內容**。  
2. 凡有內容（含**僅標題**）→ **一律至少 KH0**。  
3. license／OA 阻擋＝誠實 `terminal_blocked`／`fulltext_blocked`，**≠** 豁免理解。  
4. approve／activate＝**唯人**（CLI＋TTY＋superuser）；gov 頁**零寫**。

---

## 2. gov → KH0–KH9 對照（摘要）

完整表見 `audits/GOV-TO-KH0-KH9-MAP-20260806.md`。

| gov 區塊（Steward 貼頁） | 主對層 | 立刻讀出的事實 |
|---|---|---|
| 治理覆蓋 96/97（98%）· ⚠ bulk-seed 無真人 approve 升級留痕 | KH2／治權 | active≠人簽軌完整；AI／web **不能** approve |
| IMPORT-QUAL-S2：jobs=14 · quals=1061 · verdict pass=1061 | **KH1** | 合格帳在；ingest 多 duplicate／skip（誠實） |
| KIP runs 14（2 failed 史料） | KH1→KH3 管線 | local_files 通道強制收束 |
| 審批：proposed=3504 · active=97 · approved=3 · suspended=1 | KH2 入口 | 大量仍 proposed；人簽稀缺 |
| FT-COV：erp 100%可答；quant／medicine…大量 pending | **KH3** | 可答≠全庫；blocked 為終態非漏做 |
| Fulltext：unattempted≈121k | KH3 前置 | 最大「資料製造」池 |
| ADM-AI-ASSIST：score 排隊 · audit=assist | **KH2** | 唯讀建議；非放行 |
| （鏈外）`run_kh_chain --check` LIVE | **KH0–KH9** | 見 §3 LIVE |

---

## 3. LIVE 基線（2026-08-06 · self-reported）

來源：`python scripts/run_kh_chain.py --check` ＋ Steward 貼 gov 頁。

| 指標 | 值 | 含義 |
|---|---|---|
| `knowledge_item` 總數 | **285,351** | 普遍口徑分母 |
| **KH0 破口** | **138,999（48.7%）** | 憲章底線**未滿**——本專案第一優先 |
| 其中無原文 | ~138,950 | 標題語意必須進 KH0；現行 depth0 多認 `item_text` → **語義落差**（§3.0） |
| staging | promoted 291k／pending **128,486**／rejected 2,180 | 資料製造仍有大 pending |
| admit_depth 分佈 | d3=396 · d4=2 · **d7=145,952** · d9=2 | 多數卡在 **≤7** |
| 可推進池（有原文且 d&lt;9） | 146,399 | 上層推進量大 |
| KH8 鑑別力 | **ok=False** | 推進實務**止於 7**（誠實） |
| gate | enabled · progressive · max_auto_depth=9 · require_kh8/9 | 配置求 9；尺不足則 fail-closed |

**一句診斷**：gov 顯示「匯入合格／erp 可答」健康；**普遍 KH0 仍半庫破口**；深度水印則「能到 7、難到 8/9」。

---

## 3.0 KH0 雙軸（覆蓋 × 品質）

| 軸 | 定義 | 現況 | 本計畫 |
|---|---|---|---|
| **覆蓋（憲章硬）** | 每 item 有 depth≥0 評定軌跡；破口→0 | **48.7% 破口** | **Wave A 必達** |
| **品質（Steward 已揭）** | 理解數字／表結構正確（見 `augur_kh0_understanding_quality`） | 覆蓋≠正確（ERP 實例） | Wave A′：錨題／矛盾標記；**須另裁方向**才改判準 |
| **runtime 落差** | `evaluate_layer(0)` 今＝`has_text`→pass | 無全文標題件 **進不了** 真·憲章 KH0 | Wave A.1：**標題／衍生標題亦可 pass KH0**（fail-closed：無任何可理解欄才 fail） |

> 未完成 A.1 前，不得宣稱「已符合 v1.53 普遍 KH0」——即便有原文子集覆蓋 100%。

---

## 4. 逐層規格（KH0→KH9）

每層固定五欄：**義務／輸入／輸出／gov 或機械證據／本波缺口→下一步**。

### KH0 · 基礎理解（普遍底線）

| | |
|---|---|
| **義務** | 全部 item 至少被評一次（標題或全文）；破口計數≡0 才得宣稱底線滿 |
| **輸入** | `knowledge_item`（title／衍生標題／`knowledge_item_text`） |
| **輸出** | `knowhow_auto_admit_state` depth≥0；可選理解摘要帳（品質軸另 GO） |
| **證據** | `run_kh_chain --check` 之 `kh0_breach`；gov 不直接顯示此數——**必須鏈檢查** |
| **缺口→步** | 破口 139k → **Wave A**：`--phase advance` 補 depth0＋**A.1** 擴 evaluate_layer(0) 接受標題 |

### KH1 · Qualification

| | |
|---|---|
| **義務** | 新進路徑落 `knowledge_import_qualification`；禁 silent drop |
| **輸入** | local_files／harvest／staging |
| **輸出** | job／qual 列；verdict／reason／ingest |
| **證據** | gov IMPORT-QUAL：jobs=14 · quals=1061 · pass=1061 |
| **缺口→步** | 歷史公版 item 多走 **KH1_BYPASS**（須正名、不得當獨立證據）→ Wave B 抽樣標註旁路率；新 local 必須走真 qual |

### KH2 · Admission Assist（非放行）

| | |
|---|---|
| **義務** | 預審排隊；**永不**改 `approval_status` |
| **輸入** | proposed source／staging |
| **輸出** | `knowledge_admission_assist`；review_log action=assist |
| **證據** | gov：assist 表 · score≈0.45 hold · 近軌皆 assist；active 96/97 ⚠ 無人簽升級留痕 |
| **缺口→步** | 本地 LLM 逾時→heuristic（KH0 品質檔）→ Wave B：timeout／think 參數（執行層）；人簽升級仍 **Steward CLI** |

### KH3 · Terminal Readiness

| | |
|---|---|
| **義務** | 推到 answerable **或** 誠實 terminal_blocked；pending 可量 |
| **輸入** | item／text／fulltext_status |
| **輸出** | sentences／embeddings／FT 終態 |
| **證據** | gov FT-COV：erp_tiptop 100%；quant pending≈15k；unattempted≈121k |
| **缺口→步** | Wave C：按 domain 排程 ATA／fulltext（license 終態保留）；**優先**降低「有標題未評 KH0」與「有全文未切句」雙池 |

### KH4 · Retrieval-Answer Baseline

| | |
|---|---|
| **義務** | 可檢索／可引用／誠實 decline |
| **輸入** | embeddings＋query |
| **輸出** | `knowledge_kh4_state.answer_status` |
| **證據** | depth 分佈已有大量 ≥4／7；advisor 熱路徑 |
| **缺口→步** | Wave D：KH4 heal／殘差（已有 closure 史料）；禁止為單題 hardcode |

### KH5 · Axis Expansion

| | |
|---|---|
| **義務** | 逐 item `kh_axis_state=ready`（fail-closed） |
| **輸入** | KH4 state |
| **輸出** | 軸就緒旗標 |
| **證據** | evaluate_layer(5) |
| **缺口→步** | Wave D：軸材料不足者 batch 補；禁「有 domain 就全庫 pass」復辟 |

### KH6 · Interaction Projection

| | |
|---|---|
| **義務** | 逐 item `interaction_state=ready` |
| **輸入** | RKI／KNI／interaction 證據 |
| **輸出** | interaction_state |
| **證據** | evaluate_layer(6) |
| **缺口→步** | Wave E：與 S2-after-S3／RKI 對齊；probe≠答案 SSOT |

### KH7 · Adversarial Eligibility

| | |
|---|---|
| **義務** | 可答性／矛盾／反例審核 |
| **輸入** | probe eligibility |
| **輸出** | `knowhow_kh7_eligibility` |
| **證據** | 現多 depth=7；**庫級** pass（已知誠實債） |
| **缺口→步** | Wave E′：建 **item 級** KH7 模型（大改；須明示 GO）；未做前顧問排序不得把 d7 當「對抗已過」級宣稱 |

### KH8 · Evidence Weighting

| | |
|---|---|
| **義務** | 證據厚度／來源／風險／時點權衡且**具鑑別力** |
| **輸入** | evidence 模組 |
| **輸出** | evaluate_item_evidence |
| **證據** | LIVE：`KH8 鑑別力 ok=False` → **一律 fail** |
| **缺口→步** | Wave F：**先修鑑別力判準**（V-3 族；屬判準層須 Steward 裁）→ 再允許抬到 8 |

### KH9 · Synthesis & Replay

| | |
|---|---|
| **義務** | 紀律合成＋過程回放入帳 |
| **輸入** | KH8 通過者 |
| **輸出** | synthesis 評價；depth=9 |
| **證據** | LIVE：depth9 **僅 2** |
| **缺口→步** | Wave F 後置；advisor `kh9_first_rank` 僅對真過門者 |

---

## 5. 波次路線圖（可先／∥）

```text
Wave A   普遍 KH0 破口→0（含 A.1 標題語意）     【主軸 · 阻塞上層宣稱】
Wave A′  KH0 品質軸（錨題／矛盾）              【∥文件；改判準另裁】
Wave B   KH1 旁路正名＋KH2 assist 可用性       【∥ A；零 approve】
Wave C   KH3 資料製造（pending／unattempted） 【∥；domain 分隊】
Wave D   KH4–KH6 逐 item 補齊                 【A 破口下降後加大】
Wave E   KH7 item 化設計                      【plan-first 可∥】
Wave F   KH8 鑑別力→KH9                       【判準 GO 後】
KH10     不在本檔                              【另案＋反自我背書】
```

### 可先做／可同步（對照市場軸）

| 動作 | 與 Phase1 #1+#2+#10 |
|---|---|
| 寫本計畫＋gov map（本輪） | **∥** 文件 |
| Wave A `--check` 週頻監視 | **∥** 零搶 B3 |
| Wave A `--run --phase advance`（限量） | **可∥** 若 CPU／LLM lock 不撞收盤 B3；收盤窗讓 #1 |
| A.1 改 `evaluate_layer(0)` | **另碼 GO**；計劃已寫≠已改 |
| Wave C fulltext 大掃 | **夜間／週末**；避 B3 |
| approve 人簽 CLI | **唯 Steward**；AI 不代跑 |
| Wave F KH8 判準 | **須 Steward 裁** 後方碼 |

### 明示禁止

- web／AI approve／activate  
- 把 license blocked 洗成 answerable  
- 窄口徑「有原文覆蓋 100%」冒充普遍 KH0  
- KH10 自我背書抬升  
- sim `--apply`／解凍 FinMind 放量當 KH 手段  
- 未授判準下宣稱 KH8／KH9「已確立」

---

## 6. 建議執行序列（最小可驗）

| 步 | 指令／產物 | 驗收 |
|---|---|---|
| S0 | 本檔＋`GOV-TO-KH0-KH9-MAP` REGISTER | Steward 可復述「破口 48.7%＝主軸」 |
| S1 | 另 GO：`KH0-UNIVERSAL-A1-go`（標題可理解→depth0） | evaluate_layer(0) 行為＋自測 |
| S2 | `KH0-BREACH-DRAIN-go`：`run_kh_chain --run --phase advance --limit N` 循環 | `kh0_breach→0` |
| S3 | `KH1-KH2-HYGIENE-go`（旁路標註／assist timeout） | gov 措辭＋assist 真模型率↑ |
| S4 | `KH3-FT-DOMAIN-go`（按 domain 隊列） | pending↓；blocked 理由保留 |
| S5 | `KH4-6-ITEM-go` | axis／interaction ready 率↑ |
| S6 | `KH7-ITEM-MODEL-plan`→go | 不再僅庫級 |
| S7 | `KH8-DISCRIM-go`（Steward 裁後） | `KH8 鑑別力 ok=True` 後方抬 depth |
| S8 | `KH9-SYNTH-go` | depth9 有意義人群；advisor 排序誠實 |

---

## 7. Paste-ready（分句；勿混貼）

採納本專案計畫（文件）：

```text
KH0-KH9-PROJECT-PLAN-adopt | FZ/GATE-keep | no-approve-by-AI | hold-#1
# 讀: reports/augur_kh0_to_kh9_project_plan_20260806.md
# 主軸: 普遍 KH0 破口→0；天花板=9；KH10 不納
```

Wave A.1（改 depth0 接受標題 · **另授**）：

```text
KH0-UNIVERSAL-A1-go | FZ/GATE-keep | skip-sync | no-SIM-apply
```

破口排泄（限量推進 · **另授**）：

```text
KH0-BREACH-DRAIN-go | FZ/GATE-keep | --phase advance | limit-bounded
```

KH8 鑑別力（判準 · **另裁**）：

```text
KH8-DISCRIM-go-plan
```

---

## 8. 驗收（計畫書本身）

1. Steward 能指出：**gov 匯入合格綠 ≠ 普遍 KH0 已滿**。  
2. 寫明 runtime depth0 與憲章 KH0 的落差與 A.1。  
3. KH8 無鑑別力→止於 7 寫成硬事實。  
4. approve 唯人；本檔零寫審批。  
5. 與市場日更軸正交句存在。

---

## 9. 讀序

1. 大憲章 v1.54 KH0／入口底線  
2. **本檔**  
3. `audits/GOV-TO-KH0-KH9-MAP-20260806.md`  
4. `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md`（能力語義）  
5. `scripts/run_kh_chain.py --check`（每次開波前）

*完。[I] self-reported（#32a）。*
