---
status: current
series: optimization_master_plan
round: r2
supersedes:
  - reports/augur_optimization_master_plan_20260803.md
related_understanding: reports/augur_deep_understanding_r5_20260803.md
related_step_plan: reports/augur_optimization_step_plan_20260803.md
---
# Augur 優化執行總計畫 r2（2026-08-03 夜）——後續優化之執行 SSOT

> **性質**：[I] 執行 SSOT（CLAUDE #16／#20）。**不創設治權判準**；不解凍 API；不降閘；不代簽。  
> **理解基座**：`reports/augur_deep_understanding_r5_20260803.md`。  
> **繼承**：舊檔 `reports/augur_optimization_master_plan_20260803.md`（晨版；**自 r2 起降為史料**——編號 M-*／證據／覆核指令仍可引用，**優先級與「最佳下一步」以本檔為準**）。  
> **step plan**：`reports/augur_optimization_step_plan_20260803.md` 仍可作當日操作備忘；與本檔衝突時以 **r2** 為準。  
> **self-reported（#32a）**。  
> **今夜**：M-T5 **純守**——本計畫**不得**在夜窗被执行成「搶 slot／改 driver／allow-apply／手動 TWEVO／--morning」。可做＝寫本檔／唯讀觀察。  
> **KPI**：無本輪 live DB 數字不造假；U1／覆蓋引用 cut card＋EXECUTE audits；其餘引既有 landing／r4／stdout 路徑或標 **待測**。

### Steward 已拍板（約 2026-08-03 21:54+08）

| 項 | 裁 |
|---|---|
| **SSOT** | **拍板**——本檔 r2 ＋ `reports/augur_deep_understanding_r5_20260803.md` 為後續優化理解／執行 SSOT（舊 master／舊 r4→史料） |
| **夜班後 Phase** | **開 65 triage（唯讀分流）**＝**夜班後第一刀**；**今夜不開**（純守至 run22；不生成 triage 報告、不搶 `heavy_slot`） |
| **honesty** | **維持一証一批、用完作廢** |
| **N7／043** | **本週裁**（P1-N7／P1-043） |

| 欄 | 內容 |
|---|---|
| **效力** | 執行藍圖 **採納**；P0-A **已排程（待夜班後退場）**、**非已執行** |
| **拍板碼** | `OPT-MASTER-R2-20260803` ＋ `FZ-keep` ＋ `GATE-keep` ＋ `M-T5-watch` ＋ `W2-65-PHASE-open`（夜班後） |
| **留痕** | `audits/OPT-R5-R2-SSOT-APPROVED-20260803.md` |

---

## §0 三問直答（r2）

### 0.1 【問一】下一季／下一批最槓桿切口是什麼？

> **W2 概念覆蓋軌道——「65 無概念 triage」為母体槓桿；並行「草案殘 20 之乾淨子集」為低摩擦增量。**  
> **禁止**把槓桿讀成「把 source_column 填滿 98」或「造 65 個假 concept」。

**判決理由（鏈）**

1. **M-W2 已回答單位成本問題**（抽樣報告落地）：機械可對率低的根因常是**沒有可映概念／結構待裁**，不是缺正規式。  
2. **U1（31／62／93）已證明**：Q-R1(a)＋W2-1(a)＋親簽 honesty 窗可走通；mapped **10→13**、sc **0→3**。試點**關閉**——重複做同構三條邊際下降。  
3. **母体仍是 (13 mapped, 20 draft, 65 none)**：欄位級對帳在 65 上「沒東西可對」——解阻計畫原判仍成立。  
4. 晨版 master 之 **M-G1 最佳下一步已 closed**；繼續以 worktree 為 P0＝打已死之蠅。  
5. **10-14／WM.36** 硬期限仍在：無概念覆蓋則七欄完成無來源。

**證偽條件**：若 Steward 裁「65 整袋 out_of_scope／永不登錄」→槓桿改為草案 20＋N7＋權威採認；若夜班 run22 爆出進化鏈紅且阻塞概念弧→插入 P0-hotfix（仍不開 API）。

### 0.2 【問二】可先做／可同步／禁做

| 類 | 內容 |
|---|---|
| **可先做（夜班後；零假概念；FZ-keep）** | 65 通道**唯讀**分流表（消費／草案撞車／infra／B0 標記）；草案 **86／35／70** dry SQL 備料（**不寫庫**直至親簽）；假綠探針殘項；N7 呈案一頁；M-T6 結輪觀察腳本複跑；DB 復通後 `--survey` 複核 |
| **可同步** | 文件／探針／lint（輕量）‖ 65 唯讀 SQL；**不可**與 TWEVO 重寫同檔 driver；重活仍受 RAM／Ollama 約束（舊 master §0.3 框架有效，**數字待重測**） |
| **禁做** | FinMind／FRED 放量／補洞；造假 `world_concept`；未裁形制大批 UPDATE；搶 `heavy_slot`；`--allow-apply`；夜窗改 evolution driver；AI 代簽 `decided_by`；把 UK 改豁免關紅燈 |

### 0.3 【問三】夜班後第一刀（已排程 · 非執行）

| 欄 | 狀態 |
|---|---|
| **第一刀** | **P0-A：65 triage**（唯讀報告＋分流表） |
| **排程狀態** | **已排程**——Steward 已裁「夜班後開」（約 21:54+08）；**今夜不開**、**尚未執行** |
| **執行門檻** | M-T5 守夜／run22 窗退場後；DB 復通；才生成 `reports/augur_w2_65_triage_*.md` |
| **同日可選第二刀** | P0-B：86／35／70 dry propose 三份（不 COMMIT）——另排，不搶第一刀 |
| **觀察刀（不佔第一）** | P0-OBS：run22／I5B superseded 驗收寫入 audit |

---

## §1 相對舊 master：closed／carry／drop

> 舊 master 晨點 HEAD≈`f7c7c68`；本檔對齊當日落地至 HEAD **`66b001e`**（U1 docs）。完整 100+ 項不逐條抄寫——**規則**：closed＝勿再派同工；carry＝保留意圖改序；drop＝前提消滅或併入他項。

### 1.1 closed（代表；已有落地／封存）

| ID | 結果 | 證據 |
|---|---|---|
| **X1** | sim q_grid | `36c69cc` |
| **X2** | I5B 施作 | `2b6350d`；剩餘觀察→M-T6 |
| **X3 本體** | RULING-043 檔＋AL-047 | `c9575f3`；**簽核仍 carry→M-P16** |
| **M-G1 S1–S3** | fail-closed hook | `d27e797`；pre-commit 字面 |
| **M-T1** | sim ledger FK | 階段0；RUNBOOK |
| **M-T2** | cleared_at 謂詞 | 階段0 |
| **M-T3** | 人裁→改自動 supersede 建議 | mt3 證據 |
| **M-T4** | watchdog 發車誤判 | RUNBOOK 更正；log 冷却 |
| **M-T7** | 20:00≠自動首格 | 事實更正 commit |
| **M-G2／M-G3** | 掃描器地板／reconcile | 階段0 |
| **M-G9** | 新鮮度哨兵 | MG9-MG10 landing |
| **M-G10 wiring** | dim-sync 接線＋dry | 同上；**補抓未閉** |
| **M-W2** | 欄位級抽樣 | `augur_w2_source_column_reconcile_sampling_*` |
| **U1 31／62／93** | 親簽 mapped | W2-U1 EXECUTE×3；cut card |
| **M-N1／N2** | 探針骨架 | MN1-MN2 landing |
| **M-M5／M-O9** | sim 判決／並行容量 | ARCHIVE landing |
| **M-T5（今夜）** | 純守紀律 | NIGHT-GUARD（**持續生效**至退場） |

### 1.2 carry（意圖保留；優先級依本檔重排）

| ID／簇 | r2 位置 | 註 |
|---|---|---|
| **M-W3／W4／W5** | P2 | 欄位級與權威採認；需人簽 |
| **M-N7** | P1 | vendor 尺——硬期限輸入 |
| **M-N5／N* 過期族** | P1–P2 | 部分依賴 N7 |
| **M-G10 補抓** | Pn-FZ | 另授＋FZ |
| **M-G11–16** 殘 | P1 | 假綠／GUC |
| **M-K\*／M-G14–15** | P1–P2 | 知識誠實 |
| **M-T6** | P0-OBS | run22 |
| **M-P16** | P1 | 043 簽 |
| **M-G1-S4** | P3 | 不阻塞 |
| **假綠主序哲學** | 全域 | 「先讓紅燈會亮」仍有效，但**P0 讓位給概念覆蓋母体** |
| 舊「55 可先做」清單 | 素材 | 執行前對本檔禁做表過濾 |

### 1.3 drop／勿再催

| 項 | 理由 |
|---|---|
| 再催 I5B 施作授權 | 已落地 |
| 以 M-G1 為唯一 P0 | 已修 |
| 「M-W2 單位成本未知故不能排程」 | 抽樣已做 |
| U1 三條重跑試點 | 窗關閉；改下一批 |
| 宣稱 execution plan W0 整波仍關鍵路徑 | 前提失效（舊 master 已自白） |

---

## §2 分階段 P0–P4

### P0｜概念覆蓋儀器＋夜班收斂（夜後 1–3 日）

| 子項 | 做什麼 | 驗收 | 依賴 | schema／script | Steward |
|---|---|---|---|---|---|
| **P0-OBS** | run22／I5B：pending→superseded；twevo 健康 | audit 記 superseded 計數／異常；對照 `prerun22_pending_snapshot_*.csv` | cron 結輪 | 既有 `report_applygo_readiness.py`；新 audit 檔 | 否（觀察） |
| **P0-A** | **65 triage 唯讀**：每通道→{已被草案／mapped 消費, B0/infra 緩登, 需新概念卡, out_of_scope 候補} | 報告＋機械可重跑 SQL；**零 INSERT concept** | DB 復通；解阻 §1.2 1-C；**夜班後退場** | `reports/augur_w2_65_triage_*.md`；可選腳本 `scripts/survey_unmapped_concept_gaps.py`（若新寫須 #29 矩陣＋`--selftest`） | **已排程開報告窗**（`W2-65-PHASE-open`／夜班後）；寫入／概念 INSERT **仍須另裁**；**今夜＝未執行** |
| **P0-B** | 草案乾淨三條 **86／35／70** dry SQL／propose | 三份 reports；明示不 COMMIT | cut card 形制 (a)/(a) 沿用假設 | 比照 `augur_w2_u1_binding*_dry_sql_propose_*` | 圈選＋親簽句才寫庫 |
| **P0-C** | `--survey` 複核覆蓋 | 印出 mapped／sc 填；與 13／3 差分說明 | DB | `reconcile_channel_columns.py --survey` | 否 |

**禁做**：批次登錄 65；假 key；FZ 補抓；搶 slot。

### P1｜紅燈會亮＋尺（約一週，可與 P0-B 人裁交錯）

| 子項 | 內容 | 驗收 | Steward |
|---|---|---|---|
| **P1-N7** | vendor 四尺→一權威尺呈案 | 一頁 decision；baseline 對齊計画 | **必裁** |
| **P1-G** | M-G11–16／殘假綠探針（可先做部分） | 探針紅可復現；#35 先驗紅留痕 | G16／部分需裁 |
| **P1-043** | M-P16 簽核或明示「圈選即裁決」收束 | 簽核欄或 AL  clarifying | **必裁** |
| **P1-K** | M-G14／K 正名（消費側） | 閘與排序／權重敘事一致 | 旁路存廢或需裁 |
| **P1-DOC** | HANDOFF／step 指針改 r5／r2 | 讀序不打架 | 否 |

### P2｜WM.36 欄位級與權威（兩～四週；人簽驅動）

| 子項 | schema／資料 | script | 驗收 | Steward |
|---|---|---|---|---|
| 概念批量（經 triage） | `world_concept`＋`world_concept_version` INSERT | dry→親簽執行包 | 每批 audit；mapped 遞增；**K1 分母不含強求 98** | 每批圈選 |
| `source_column` | 依 W2-1(a) 分隔字串；多值通道 | reconcile／propose | sc 填↑；非法空白不灌 | W2-3／殘 Q-R |
| 權威採認 | `authoritative_binding_id`／`decided_by` | Annex F 備料已有 | 七欄可解析項集非空 | **親簽** |
| M-W3 絞殺 | 直綁清冊 | check_vendor_binding | 與 N7 尺一致 | 節奏裁 |

### P3｜預測／sim／進化品質（與 P2 可交錯；不阻 Registry）

| 子項 | 註 |
|---|---|
| sim 首格／settle／M-M\* | 人工節奏；不排進搶 slot 夜窗 |
| 週報 digest 漏晉升 | r4 Z8 carry |
| direction_gate／確立級 | **不**因 Registry 進度假過門 |
| 備份異地紅燈 | 承舊 master 異地決策 |

### P4｜治權自洽與長期債

CS 漂移、雙現行、AL 分家、worktree S4、10-14 日曆（禁假關）、LAIEVO 尺與能力宣稱、G-CAT／G-DIV 另帳等——**排在母体覆蓋與紅燈族之後**，除非 Steward 插隊。

### Pn｜FZ 閘後（明示解凍句之前不做）

TRI／dim-sync 實跑、Dividend rebuild、寬窗 probe、放量 audit heal——**保持冷凍**；白名單日頻除外。

---

## §3 每階段驗收總表（滾動）

| 階段 | 綠燈定義（誠實） |
|---|---|
| P0 | triage 報告可重跑；OBS audit 存在；dry 三份就位；**DB 無未授權寫入** |
| P1 | N7 有裁示字面；至少一支新假綠探針「壞了會紅」；043 敘事收束或登錄待簽狀態 |
| P2 | 存在≥1 個「七欄俱全可解析」登錄完成項（WM.36 判準）**或**書面豁免清單；sc 填顯著＞3 且可追溯批號 |
| P3 | sim／進化觀察數字出自 stdout／DB，非估 |
| Pn | 僅在解凍句後出現 API 落地 |

---

## §4 KPI（勿造假）

| KPI | 現值來源 | 目標意識 | 禁讀法 |
|---|---|---|---|
| mapped／98 | **13**（cut card 21:18+08） | 随批次遞增 | ≠ WM.36 完成 |
| source_column 已填／98 | **3** | 随欄位批遞增 | ≠ 機械配對率 |
| 草案殘 | **20** | 降或轉 mapped／廢案 | |
| 無概念 | **65** | triage 後「待提案／緩登／out」分類覆蓋率→100%（分類，非登錄） | ≠ 65 概念已建 |
| 機械配對率 | 9.2%（抽樣日） | **待測** | ≠ 對帳成功率 |
| vendor 尺數 | 4 把並存（r4） | →1（N7） | |
| freshness E10 | **red**（MG9） | 哨兵保持紅直至補抓／裁示 | 禁關哨兵假綠 |
| prodset active | 3（r4） | 進化觀察 | ≠ 可交易 |
| evaluated_pass | 0（r4） | 方向機另軌 | |

**覆核指令（DB 復通後）**

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/reconcile_channel_columns.py --survey | head -30
# 期望知情：mapped／source_column 已填 與 13／3 對照或附差分
```

---

## §5 資源互斥與夜／日邊界

| 資源 | 規則 |
|---|---|
| **heavy_slot** | 僅 TWEVO／eval_local；夜窗 AI **不取** |
| **FZ** | 零例外放量；arena 白名單≠解凍 |
| **honesty_write** | 僅 Steward 發證批次；U1 窗**已消費完**——下批須**新證** |
| **hugo TTY** | 圈選／親簽／N7／043／解凍——不可并行假多人 |
| **RAM／Ollama** | 排班前 `free -m`；不引用晨版 MB 數 |

---

## §6 排序主尺（r2 修訂）

```
能讓「沒東西可對」變「有概念可映／明示不映」 ＞
能安靜讓錯通過的紅燈 ＞
能让對的東西被誤讀的口徑 ＞
效能與體積
```

對晨版「M-G1＝問一」：感謝其當日價值；**r2 問一改掛 W2 母体**。  
「先讓紅燈會亮」降至 **P1 主航道**，不廢除。

---

## §7 AskQuestion（呈 Steward）——**已裁（約 21:54+08）**

| # | 題 | Steward 裁 |
|---|---|---|
| 1 | 是否拍板 r5＋r2 為後續優化理解／執行 **SSOT**？ | **拍板**（舊 r4／舊 master→史料） |
| 2 | 夜班後是否開門 Phase：65 triage（P0-A）？ | **(a) 開**＝唯讀分流；**明示今夜不開**／夜班後首刀 |
| 3 | 下一批 honesty：「一証一批、用完作廢」？ | **維持** |
| 4 | N7／043 簽：本週裁窗還是掛 10-14 備料捆綁？ | **本週裁** |

（原空白勾選表作廢；留痕見文首「Steward 已拍板」＋ `audits/OPT-R5-R2-SSOT-APPROVED-20260803.md`。）

---

## §8 誠實邊界

- 本檔**不是**全 repo 優化完備集合；未重測舊 master 容量數字。  
- 寫作時 **DB 拒連**——覆蓋 KPI 以 08-03 晚 audit／cut card 為準。  
- step plan 午後「最佳＝M-G1」對**當日午後**成立；對**夜後續跑**以本檔為準。  
- 本地 LLM 本輪 timeout——綜述判斷在本 agent，非本地模型。  
- **P0-A 已排程≠已執行**：本拍板**不**授權今夜生成 65 triage 報告。

---

**拍板碼（已填）**：`OPT-MASTER-R2-20260803` ＋ `FZ-keep` ＋ `GATE-keep` ＋ `M-T5-watch` ＋ `W2-65-PHASE-open`（**夜班後**生效）
