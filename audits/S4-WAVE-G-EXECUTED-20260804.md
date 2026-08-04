# S4-WAVE-G 執行帳 [I]（2026-08-04）— EXECUTED（partial 文件化＋誠實 SKIP；S4 A–G 收官）

> **位階**：[I] 執行留痕（非 META [N]）  
> **GO**：`audits/S4-WAVE-G-GO-20260804.md`（Steward 原文 `S4-WAVE-G-go | FZ/GATE-keep | no-SIM-apply | skip-sync`）  
> **SSOT**：`reports/augur_s4_market_model_families_opt_plan_20260804.md` §Wave G  
> **前置**：`audits/S4-WAVE-F-EXECUTED-20260804.md`  
> **logs**：`/tmp/s4-wave-g-20260804/`（見 §2 inline 指令；無長跑，皆秒級盤點）  
> **self-reported（#32a）**：**≠**確立級／可交易／sim-apply；advisor／LLM **非**價預測器

---

## 1. 約束遵守

| 約束 | 本窗 |
|---|---|
| skip-sync | **守** |
| no-SIM-apply | **守** |
| FZ／GATE-keep | **守** |
| 未授權全文擷取／embedding 加權 runtime | **未做**——本窗僅讀既有狀態，零新 acquire |
| advisor／LLM 冒充價預測器 | **禁止已守**——明文標註 partial／非 Verified |

---

## 2. Wave G 結果總表（含既有證據路徑）

| ID | 變體族 | adapter | 本窗裁決 | 依據 |
|---|---|---|---|---|
| **G-9a** | ML+DL stacking | **partial**（`DirStackM`＝Logit 元學習器，已於 Wave A A-D2 落地） | **既有**（不重訓）；Logit **無隨機性**→seed 記 0（`train_direction_stack.py:10`，明文 #11 判準） | `scripts/train_direction_stack.py` |
| **G-9b** | GBDT+LSTM | **missing** | **SKIP** | 承 Wave C：無 LSTM adapter |
| **G-9c** | blending／ensemble（多模型**預測層**融合） | **missing**（區分澄清：`threelens`＝**特徵層**融合 44 特徵單模型，非多模型預測融合） | **SKIP**（真 ensemble 缺）；`threelens` 已於 Wave A 文件化，不重算 | `train_direction_threelens.py:2-7` docstring 自陳「工程冒煙≠gate」 |
| **G-10a** | 新聞／社群情緒 | **partial**（knowledge 管線存在；**無**預測頭） | **SKIP** | 無 sentiment→predict 連接碼（inventory `(none)`） |
| **G-10b** | 事件抽取→預測頭 | **missing** | **SKIP** | 同上 |
| **G-10c** | 主題模型＋下游頭 | **missing** | **SKIP** | 同上 |
| **G-11a** | LLM 特徵／情緒 | **partial**（`src/augur/advisor/ollama.py` 存在；**非**價預測器） | **SKIP（預測）**；輔助流程另帳 | advisor 未接 `feature_values`；`migrate_advisor_distill_ddl.py:5` 明文「蒸餾產物零落 `knowledge_*/philosophy_*/feature_values`」——**邊界已守** |
| **G-11b** | RAG 假說／agentic 研究 | **partial**（advisor 存在） | **SKIP（預測）**；不加權 runtime | 同上邊界 |
| **G-12a** | 貝氏層級 | **missing** | **SKIP** | 無 `pymc`／貝氏 hierarchical 碼 |
| **G-12b** | GP（Gaussian Process） | **missing** | **SKIP** | 無 `GaussianProcess`／`gpytorch` |
| **G-12c** | 遺傳規劃／符號回歸 | **missing**（澄清：`src/augur/evolution/` 僅 `behavior_rubric.py`——**行為評分**，非 GP／符號回歸模型族） | **SKIP**；**未**把 TWEVO／進化側晉升機制誤稱為本族 pass | `ls src/augur/evolution/` 僅 2 檔；無 GP／symbolic regression 碼 |

**LOB Level-2**：taxonomy 通用邊界——DB 無 L2 → 沿用 SKIP（與 Wave C/D 同因）。

---

## 3. 誤配字面澄清（誠實核實；避免 #35 型字面斷言）

| 初篩命中 | 核實結果 |
|---|---|
| `ollama.py:154` `num_predict` | Ollama **生成參數**（LLM token 數），**非**股價預測；假警報已排除 |
| `migrate_advisor_distill_ddl.py:5` | 反向證據——**明文禁止**蒸餾產物流入 `feature_values`，**強化**邊界而非違反 |

---

## 4. 最低完成定義對照

| # | 定義 | 本窗 |
|---|---|---|
| 1 | 既有 partial（stacking／threelens／advisor）**文件化**、不重訓 | **滿足** |
| 2 | 真缺族（GBDT+LSTM／news-head／Bayesian／GP／符號回歸）**誠實 SKIP** | **滿足**（8 族） |
| 3 | LLM／advisor **不得**自稱價預測 Verified | **滿足**（G-11a/b 明註） |
| 4 | 不把 TWEVO 誤稱 GP 族 pass | **滿足**（§2 G-12c 澄清） |

---

## 5. 硬禁未觸

無 sync · 無 sim `--apply` · 無假訓 · 無 LLM／advisor 冒充預測 · 無未授權全文擷取 · 無確立級。

---

## 6. S4 A–G 收官總覽（本波為收口）

| Wave | 涵蓋 | 狀態 |
|---|---|---|
| A | tabular／ranker／direction | **EXECUTED**（近滿；5 架構臂落地＋8 SKIP） |
| B | classical TS | **EXECUTED**（5 SKIP／n-a-sim） |
| C | sequence DL | **EXECUTED**（5 SKIP；缺序列窗） |
| D | Transformer TS | **EXECUTED**（3 SKIP；同缺口） |
| E | 圖／關係 | **EXECUTED**（2 SKIP；KH 圖≠股票圖） |
| F | RL（另尺） | **EXECUTED**（3 SKIP／defer；禁自動下單） |
| G | 混合／另類／NLP／LLM／貝氏 | **EXECUTED**（本帳；2 partial 既有＋8 SKIP） |

**taxonomy ≈12 大類／≈35 變體族——A–G 波次全數 EXECUTED**：多為誠實 SKIP／partial 列帳，**非**全族訓練；生產熱路徑仍＝Wave A 之 RankRidge／RankGBDT／direction 三臂。**IC／SKIP 普查 ≠ 可交易／確立級**（dgate pass=0 仍在）。

---

## 7. 下一刀（另句；S4 taxonomy 已收口後）

S4 波次無下一 Wave（G 為末波）。可選方向（**各需另句**）：

```text
LOOP-S5-TO-S4-OPT-go + GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply + skip-sync
```

（消費 S5 OOS 分數回饋，重選族／horizon；**非**開新 Wave）

或回 S3 契約缺口（序列窗；解 C／D 之根因）：

```text
S3-WAVE-D-go | FZ/GATE-keep | skip-sync | no-SIM-apply
```

或 direction_gate 正式評估（**人裁**；現 hit≈0.52 **≠** pass）：

```text
evaluate_direction_gate（另句；非本 GO 默授）
```

---

*完。EXECUTED＝Wave G **partial 文件化＋誠實 SKIP**（2 partial／8 SKIP）。**S4 taxonomy A–G 全波次收口**。self-reported（#32a）。*
