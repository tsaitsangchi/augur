# Augur 優化——逐步執行計畫書 r3（待辦／可先做／可同步）

> **性質**：[I] **step／runbook 執行序**（CLAUDE #16／#20）。後續優化依本檔開工。  
> **寫入**：2026-08-04 ≈10:10+08 · `PC002-S1800`／WSL · HEAD `0287a25`  
> **位階**：非 [N]；不代簽；Sole Steward（無公示要件）。  
> **self-reported**：優先序判讀為 AI 呈案；可機械覆核者附指令。

| 角色 | 路徑 |
|---|---|
| 決策導覽（地基） | `reports/augur_project_optimization_plan_20260804.md` |
| 理解 SSOT | `reports/augur_deep_understanding_r5_20260803.md` |
| 執行 master | `reports/augur_optimization_master_plan_r2_20260803.md` |
| **本檔（step r3）** | `reports/augur_optimization_step_plan_r3_20260804.md` |
| 前 step（史料／細節仍可引） | `reports/augur_optimization_step_plan_r2_20260804.md`（Step1=`wait_done` **已由今日甲案超車**） |
| API 解凍判定 | `audits/API-THAW-20260804.md`（INV1∧INV2 ✅） |

**與既有 SSOT 關係**：本檔＝**今日落地後**之操作序。細節註冊仍讀 master r2；衝突時以 Steward 明示碼為準。r2 之「等結輪再開 triage」敘事對**已完成項**作廢，對**未開項**之護欄（GATE／NHC／不代簽）仍有效。

**拍板碼（已填 · Steward 甲 · ≈10:12+08）**：

```text
OPT-STEP-R3-20260804-go + W1-go + GATE-keep + NHC-keep + API-THAW-bounded
```

audit＝`audits/OPT-STEP-R3-20260804-GO.md`；Wave-1 落地＝`audits/OPT-STEP-R3-W1-LANDING-20260804.md`。  
（`API-THAW-bounded`＝取數僅日頻／明示白名單；≠放量／≠Dividend rebuild／≠假關另帳。）
---

## 0. 一句現況（2026-08-04 上午）

P0 主刀（甲案）**已落地**：morning 五驗綠、65 triage 分類完、熱路徑 39＋Gold 50 **已進 Registry**（mapped **15／98**、sc **5／98**）。API **已解凍（有界）**。下一步不是再掃一遍 P0，而是：**收殘概念批／解直綁／草案殘／治權尺** 與 **預測·sim·日頻取數** 分車道推進。

---

## 1. 今日已關閉（勿重開當「下一步」）

| ID | 項 | 證據 | 狀態 |
|---|---|---|---|
| **D0** | morning ④ 假紅 | 探針改讀 `gain_basis`；`audits/OPT-W0-RUN22-FINAL-20260804.md` | ✅ 五驗綠 |
| **D1** | 65 唯讀 triage | `reports/augur_w2_65_triage_20260804.md`（65/65） | ✅ 分類完≠WM.36 完 |
| **D2** | CIRCLE 圈選＋提案批准 | HP-39＋U0-3；其餘 U0 俟 Q-R* | ✅ 提案層 |
| **D3** | Registry 寫庫 39／50 | `REGISTRY-GO`；EXECUTED×2；`--check` ✓✓ | ✅ mapped 15／sc 5 |
| **D4** | API 解凍判定 | `audits/API-THAW-20260804.md` | ✅ 有界准取數 |

**複核（隨時可重跑）**：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/observe_twevo_run22.py --morning          # 預期 rc=0
venv/bin/python -m augur.catalog.world_concept --check            # 39／50 ✓
venv/bin/python scripts/reconcile_channel_columns.py --survey     # mapped 15／sc 5
```

---

## 2. 待辦全景（問題 → 車道）

> 來源：地基計畫 P0–Pn＋triage 殘＋今日未做。**不**把已關閉項再列待辦。

| 車道 | 代號 | 待辦摘要 | 阻塞？ |
|---|---|---|---|
| **R｜Registry／WM.36** | R1–R6 | 解直綁 39；U0 五卡結構債；out8；草案殘 20；緩登 13；權威採認舊六概念 | 多項需裁／新 honesty |
| **G｜閘與尺** | G1–G4 | N7 vendor 尺；043 簽核；假綠探針；HANDOFF 指針對齊解凍＋r3 | N7／043＝Steward |
| **P｜預測／經濟** | P1–P3 | 庫內 predict／符號尺；dgate 呈案（不擅改門檻）；確立級仍 pass=0 誠實 | 預測⊥必須 sync |
| **S｜sim／進化** | S1–S3 | sim 觀測／selftest；首格 apply **另句**；符號／TWEVO 日班紀律 | 不搶 night slot |
| **A｜取數（已解凍有界）** | A1–A4 | 日頻 `daily_maintenance`；`sync_macro --no-catalog`；**禁** Dividend rebuild／放量除非另授 | #24／#25／403 即停 |
| **K｜知識／顧問** | K1 | 消費正名（非權重） | 低急 |
| **T｜治權自洽** | T1–T3 | 10-14 禁假關；備份異地住所；worktree／CS 漂移 | 低吞吐 |
| **N｜另帳（不解凍假關）** | N1 | G-CAT／G-DIV／G-ATTEST／HAR… | 產品另帳 |

---

## 3. 可先做／可同步／須裁／禁做

### 3.1 決策矩陣

| 類 | 判準 | 本波例子 |
|---|---|---|
| **可先做（建議下一刀）** | 零／低 Steward 新裁；護欄內；驗收機械 | 見 §4 Wave-1 |
| **可同步** | 不同檔／不同鎖；不互搶 `heavy_slot`；不與 Registry COMMIT 同交易 | 文件／探針／sim 觀測 ‖ 日頻 sync ‖ dry SQL 備料 |
| **須 Steward 裁／新證** | Q-R*／honesty 新批／親簽／APPLY／放量 | U0 結構債、out8、解直綁改碼授權、sim `--apply` |
| **禁做** | 假綠、假關另帳、代簽、放量 rebuild、降閘 | 見 §8 |

### 3.2 平行度示意（誰可同時開）

```
                    ┌─ Wave-1a  Registry 殘（dry／呈裁）─────┐
今日基線 ─────────┼─ Wave-1b  文件＋假綠探針（零 DB）──────┼─→ Wave-2（裁後寫庫／解直綁）
 (D0–D4 已關)     ├─ Wave-1c  sim 觀測／selftest ──────────┤
                    └─ Wave-1d  有界日頻取數（A1）───────────┘
                              ↑ 四者可同步；互斥點見下
```

| 互斥／串行點 | 說明 |
|---|---|
| Registry COMMIT | 一批一證；39／50 證**已消費**→下批須**新** honesty |
| `heavy_slot` | TWEVO 夜窗 vs sim apply／重活——**不搶** |
| 放量 sync | 與限速／403；**不**與「只為刷綠」並行硬衝 |
| 治權門檻文案 | dgate≥60 等——呈案另開，不塞進執行刀 |

---

## 4. Wave-1｜最佳下一步（建議預設開工包）

> **目標**：在不大開新裁的前提下，把「問題處理」推進到**可驗收的下一階**。  
> **預設採納句**（Steward 可改）：`OPT-STEP-R3-W1-go`＝下列 1a–1d **可同步開**；寫庫／apply／放量**不含**。

### 4.1 Wave-1a｜Registry 殘——**可先做（備料）**

| 步 | 項 | 可先做？ | 產物 | 驗收 | 不做 |
|---|---|---|---|---|---|
| **R1** | **解直綁呈案**（39）：`field_correlation` `block_money` → 經 `resolve('tw.block_trade.print')` 之改碼計畫＋影子比對要點 | ✅ 文件／diff 草案 | `reports/augur_w2_unbind_block_trade_plan_YYYYMMDD.md` | 計畫含前後 SQL／風險；**零改碼直到另句** | 未授權改 production 消費 |
| **R2** | **P0-C 草案殘 dry**（優先 86／35／70＝最乾淨三者） | ✅ dry 報告 | 三份 `*_dry_sql_propose_*` | 明示須新 honesty＋親簽 | COMMIT |
| **R3** | **out 候補 8 呈裁單**（踢出 K1 分母？） | ✅ 一頁勾選 | 併入或新 `audits/…-OUT8-…` | Steward 勾選 | 自動踢出 |
| **R4** | **U0 五卡結構債清單**（7／37／65／80／97）對 W2-1／3／5／6／Q-R8 | ✅ 對照表 | 更新 concept cards 或短報告 | 每卡「可登／俟／不登」 | 強登假概念 |

**本波不產新表**；沿用 `world_concept`／`world_concept_version`／`world_channel_binding`。

### 4.2 Wave-1b｜閘與文件——**可同步（零 DB 寫）**

| 步 | 項 | 產物 | 驗收 |
|---|---|---|---|
| **G4** | HANDOFF／freeze 指針：解凍已成立＋step 改讀 r3 | 最小 diff（另授 commit） | 讀序不與「仍全凍」打架 |
| **G3** | 假綠探針增量（CLAUDE #35；先驗紅） | 探針或 `check_false_assertions` 基線不動增列 | 壞了會紅 |
| **G1／G2** | N7 尺＋043：**呈裁卡**（不代裁） | 一頁 decision card | Steward 字面入 audit |

### 4.3 Wave-1c｜sim／預測儀器——**可同步（輕）**

| 步 | 項 | 可先做？ | 入口 | 不做 |
|---|---|---|---|---|
| **S1** | sim 觀測＋既有 `--selftest` | ✅ | `OPT-SIM-EVO` 專項；P1 儀器設計已有稿 | `--apply`／搶 slot |
| **P1** | 庫內 predict／train **as-of** dry（`--skip-sync`） | ✅ | 既有 `train_*`／`predict_*` | live API 硬前提；宣稱可交易 |
| **P2** | 符號尺三顆 `--record`（若環境允） | ✅ 有界 | `verify_sign_consistency.py` | 假設舊特徵現役 |

### 4.4 Wave-1d｜有界取數——**可同步（與 Registry 正交）**

| 步 | 項 | 可先做？ | 指令意向 | 硬禁 |
|---|---|---|---|---|
| **A1** | 日頻增量 audit+heal | ✅（解凍後白名單＋THAW） | `daily_maintenance.py --end <當日>` | 403→停 |
| **A2** | FRED 日更 | ✅ | `sync_macro.py --no-catalog` | 新 series 狂拉 |
| **A3** | Dividend rebuild／寬窗／放量 | ❌ 須**另授** | — | 本 r3 預設禁 |
| **A4** | MC cone 重跑（庫內 as-of 08-03） | ✅ 可先（**零 API**） | 既有 MC 管線 | 與「必先 sync」綁死 |

---

## 5. Wave-2｜裁後串行（不與 Wave-1 備料混淆）

> 僅當 Steward 發新證／勾選後啟動。

| 序 | 項 | 依賴 | 程式／動作 | 驗收 |
|---|---|---|---|---|
| **W2-1** | 草案殘 86／35／70 **COMMIT** | 新 honesty＋`decided_by=hugo`＋`REGISTRY-GO-…` | 比照 CIRCLE 39／50 | mapped↑；`--check` ✓ |
| **W2-2** | 解直綁 **改碼＋測** | R1 計畫拍板 | 改 `field_correlation.py`（或抽取 resolve 助手）；單測／影子 | 無字面 `FROM "TaiwanStockBlockTrade"` 於該消費點；行為對照 |
| **W2-3** | out8 分母調整 | R3 勾選 | 文件＋K1 口徑腳本（若有） | 分母敘事一致 |
| **W2-4** | U0 可登子集寫庫 | 結構裁＋新證 | dry→COMMIT | 逐卡 EXECUTED |
| **W2-5** | sim 首格 `--apply` | 明示 `SIM-FIRST-CELL-go` | runner 鏈 | ledger／eval 列可溯；非 cron 自動 |
| **W2-6** | 權威採認舊六概念 | Annex F／親簽 | version 補 `authoritative_binding_id` | `--check` ✗→✓ 遞減 |

---

## 6. Wave-3｜中遠程（不阻 Wave-1）

| 項 | 說明 |
|---|---|
| 其餘需新卡 37 | P3 用量→P4；禁空殼 |
| B0／infra 緩登 13 | W2-2 射程裁前不造 concept |
| dgate／確立級 | `evaluated_pass=0` 誠實；改門檻＝治權案 |
| 10-14／G-* 另帳 | 禁假關；取數洞走 A 車道另授 |
| LAIEVO／備份異地 | T 車道低吞吐 |

---

## 7. (a) Schema／(b) 程式規畫（本計畫範圍）

### 7.1 Schema

| 表 | 本 r3 |
|---|---|
| `world_concept`／`world_concept_version`／`world_channel_binding` | **消費既有**；Wave-2 才寫；**不新遷 DDL** |
| `evolution_*`／sim 表 | 觀測／既有列；apply 另授 |
| 取數 raw | A1／A2 增量；禁假稱洞已補 |
| **本計畫不產新表** | 若解直綁需 helper 表→另開 #20 |

### 7.2 程式（檔／角色）

| 檔／模組 | Wave | 角色 |
|---|---|---|
| `scripts/observe_twevo_run22.py` | 已關 D0 | 回歸鎖保留 |
| `scripts/reconcile_channel_columns.py` | 全程 | survey／驗收 |
| `augur.catalog.world_concept` | R／W2 | `--check`／resolve |
| `src/augur/audit/field_correlation.py` | R1→W2-2 | 解直綁目標 |
| dry SQL 報告（新建） | 1a／W2-1 | 比照 U1／CIRCLE 形制 |
| `scripts/daily_maintenance.py`／`sync_macro.py` | 1d | 有界取數 |
| sim runner／`verify_sign_consistency.py` | 1c | 輕量儀器 |
| `scripts/check_false_assertions.py` | 1b | 假綠閘 |
| **禁**另寫第二套 Registry writer | — | 沿用既有形制 |

---

## 8. 護欄（繼承＋今日增量）

| 禁 | 說明 |
|---|---|
| 代簽 `decided_by` | 須 Steward 明示字串（REGISTRY-GO 形） |
| 複用已消費 honesty | 39／50 證作廢；U1 證作廢 |
| 造假 concept／灌 sc | #1／WM.36 |
| Dividend rebuild／寬窗放量 | 須另授（THAW 明文仍否） |
| 假關 `evaluated_pass`／10-14／G-* | 另帳 |
| 預測硬綁 live API | predict⊥API 仍成立 |
| 搶 `heavy_slot`／偷 APPLY | GATE／NHC |
| 繞 morning 假綠 | 已修探針；禁回退 |

---

## 9. 建議 Steward 拍板（三選一＋可加料）

### 甲｜Wave-1 全開（建議預設）

```text
OPT-STEP-R3-20260804-go + W1-go + GATE-keep + NHC-keep + API-THAW-bounded
```

- **同步**：1a 備料（R1–R4）‖ 1b 文件／探針／呈裁卡 ‖ 1c sim／predict 輕量 ‖ 1d 日頻 A1／A2（可選）  
- **不含**：任何新 Registry COMMIT、解直綁改碼、sim apply、放量  

### 乙｜只 Registry 殘（文件刀）

```text
OPT-STEP-R3-W1a-only-go + GATE-keep + NHC-keep
```

- 只做 R1–R4；取數／sim 不動  

### 丙｜取數優先（有界）

```text
OPT-STEP-R3-A1A2-go + API-THAW-bounded + GATE-keep
```

- 先 A1／A2；Registry 殘延後  

**加料（可與甲／乙並書）**：

- `UNBIND-39-plan-go` → 只准 R1 計畫（仍不准改碼）  
- `UNBIND-39-code-go` → Wave-2-2  
- `OUT8-kick-go` / `OUT8-keep-go`  
- `SIM-FIRST-CELL-go` → W2-5  
- `PREP-SQL-draft8670-go` → R2  

---

## 10. 執行檢查清單（開工後每刀）

1. 本刀屬 Wave-1 備料還是 Wave-2 寫庫？寫庫→有新 REGISTRY-GO／honesty 嗎？  
2. 與 `heavy_slot`／夜窗衝突嗎？  
3. 數字是否 (a)(b)(c) 可溯？  
4. 驗收指令寫進 audit 了嗎？  
5. 有沒有假稱「mapped↑＝可交易／確立級」？

---

## 11. 附錄｜證據索引

| 主題 | 路徑 |
|---|---|
| 地基優化計畫 | `reports/augur_project_optimization_plan_20260804.md` |
| 65 triage | `reports/augur_w2_65_triage_20260804.md` |
| 概念卡／圈選 | `reports/augur_w2_concept_cards_hot39_u0_20260804.md` |
| dry＋EXECUTED 39／50 | `reports/augur_w2_circle_hot39_u03_dry_sql_propose_20260804.md`；`audits/W2-CIRCLE-BINDING{39,50}-EXECUTED-20260804.md` |
| 甲案 P0 帳 | `audits/OPT-P0-TRIAGE65-20260804.md`；`audits/OPT-P0-CONCEPT-CARDS-39-U0-20260804.md` |
| API 解凍 | `audits/API-THAW-20260804.md` |
| sim 專項 | `reports/augur_local_ai_sim_evolution_plan_20260804.md` |

### 未在本檔重查之項（標明）

- live `min_clusters`／經濟終關最新值  
- 日頻 A1 是否今日已跑過（THAW 後）——開工 A1 前先查 cron／log  
- memory 索引是否過舊  

---

*完。本檔＝計畫；零業務碼改動、零 Registry 新寫、零放量。待 Steward 回甲／乙／丙（可加料）。*
