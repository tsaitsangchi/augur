---
title: GRAPH-CONSUME plan-first｜圖邊消費端契約（∥ Phase1 · 零改碼）
status: plan_first
series: s3_graph / s4_consume
open_problem: "r10 #7"
role: Phase 2.1 選刀交付（文件）；不撤 NF-pause；不搶 B3
date: 2026-08-06
viewpoint: 2026-08-06T08:46+08:00
layer: "[I]"
depends_on:
  - reports/augur_opt_stepwise_best_next_plan_r10_20260806.md
  - reports/augur_s4_seq_graph_consume_draft_20260805.md
  - audits/GRAPH-REBUILD-20260805-EXECUTED-20260806.md
  - audits/S4-NF-PAUSE-ACCEPTED-20260805.md
  - audits/OPT-R10-AFFIRM-HOLD1-P6-P10-P2TO7-20260806.md
supersedes_as_consume_plan:
  - reports/augur_s4_seq_graph_consume_draft_20260805.md
inherits_boundaries:
  - FZ/GATE-keep
  - NF-pause
  - skip-sync-B / no-SIM-apply / no-cron-B3
  - hold Phase 1 A→B3＠08-06
self_reported: true
---

# GRAPH-CONSUME plan-first · 2026-08-06

> **一句**：供给侧 `stock_graph_edge` 已有 **多 asof**（含 08-05）；**缺的是消費契約**——誰讀、讀哪個 asof、過期怎麼 SKIP——本檔只把契約寫死。  
> **性質**：[I] **plan-first · 零業務碼 · 零寫庫 · 零解凍 · 不搶 #1 B3**。  
> **對映**：r10 **#7**／Phase **2.1**；刷新並收斂 `augur_s4_seq_graph_consume_draft_20260805.md`（該稿 #4 狀態與「僅 06-30」供給敘事已過時）。

---

## §0 護欄

```text
GRAPH-CONSUME-plan-first | FZ/GATE-keep | NF-pause | skip-sync-B | no-SIM-apply | no-cron-B3 | hold-#1
# 本檔＝契約；≠ adapter GO；≠ GNN/Seq train；≠ 日更 graph rebuild 掛進 B3
```

| 可做（本檔效力） | 不可做 |
|---|---|
| 寫／修契約、貼 paste-ready、登錄 audit | 改 `ranker`／新 adapter／改 prodset |
| 標明未來唯讀探針大綱（另 GO 才跑） | 撤 NF-pause；開 NF-E／SeqLSTM 0b |
| ∥ 與 Phase 1 watcher 並存 | 把 rebuild／consume 塞進 B3 standing |

---

## §1 為何開這刀（相對 draft 08-05）

| 軸 | draft＠08-05 | 本檔＠08-06 LIVE 敘事 |
|---|---|---|
| 供給 asof | 敘事＝**僅 06-30**（13,021） | **多快照**：06-30／08-04／**08-05**（頂；`GRAPH-REBUILD-*-EXECUTED`） |
| r10 #3 錯位 | 開 | **寫側**與價／core 頂對齊→🟢；**讀側未證**→本刀 |
| 消費端 | 熱路徑不讀圖 | **仍成立**（見 §2）——have 邊 ≠ 有讀者 |
| NF | pause | **維持**；本檔不訓 |

**缺口精準句**：R8-03／rebuild 關閉的是「邊表有沒有跟日更 D」；#7 問的是「**既有／未來讀碼會不會鎖死舊 asof 或默用 max 而無契約**」。

---

## §2 現況板（self-reported · 無本輪改碼探針）

| 角色 | 路徑／證據 | 消費？ |
|---|---|---|
| **寫** | `scripts/build_stock_graph_edges.py`（`--asof`／`--commit`） | n/a（供給） |
| **DDL** | `scripts/migrate_stock_graph_edge_ddl.py`（`stock_graph_edge`） | n/a |
| **熱路徑 RankRidge／B3** | `feature_values` 扁平；standing 日更 | **不**讀 `stock_graph_edge`（誠實） |
| **src 內讀者** | 截至本檔：無業務模組 `SELECT` 該表（僅 scripts） | **無生產消費** |
| **顧問／S5** | 相對機率／econ | **不得**把圖邊當方向確立 |
| **序列窗** | S3-D library（與圖正交） | 另約；本檔主軸＝**圖邊** |

→ 今日風險**不是**「正在用錯 asof」；而是「**下一個 adapter 若無契約，會靜默 `ORDER BY as_of DESC LIMIT 1` 或硬編碼 06-30**」。本檔先封死那條路。

---

## §3 消費契約卡（強制）

### 3.1 鍵與形

| 項 | 契約 |
|---|---|
| 表 | `stock_graph_edge` |
| 鍵 | `(as_of_date, source_stock_id, target_stock_id, edge_type)` |
| 邊型（供給已知） | `industry_same`／`corr_60`／`corr_120`（寫入腳本語意；adapter 須顯式聲明消費哪幾型） |
| 宇宙 | 僅 core＠**同一**（或契約允許之）asof；禁默默跨宇宙拼邊 |
| 張量形（未來） | COO／CSR：`(row=src_ix, col=dst_ix, weight)`；無向邊不得雙計除非契約寫明 |

### 3.2 asof 選擇規則（核心 · #7 答題）

讀者**禁止**下列默認：

1. 硬編碼 `as_of_date = '2026-06-30'`  
2. 無聲明之 `MAX(as_of_date)` 當「永遠最新＝正確」  
3. 價／fv／predict 的 `D` 與圖 asof **不等**卻繼續 forward（假綠）

**允許的選擇策略**（adapter 須在 GO 文選一並寫進 audit）：

| 策略 ID | 規則 | 失敗行為 |
|---|---|---|
| **S-EQ** | 要求存在 `as_of_date = D`（predict／train asof）整表快照 | 無列 → **族級 SKIP**（理由＝`graph_asof_missing`） |
| **S-LAG-k** | 允許 `as_of_date ∈ [D−k, D]` 取 **最大且 ≤D**；k 須在 GO 寫死（建議起步 k=0≡S-EQ） | 窗外／空 → SKIP 同左 |
| **S-PIN** | 研究釘死單一歷史 asof（僅 explore／OOS 標註） | 不得進產線 prodset |

**站位建議（本檔推薦，非自動生效）**：產線／B 閉環周邊＝**S-EQ**；研究報告可 S-PIN；**在日更 graph 未進 standing 前，禁止把 GNN 掛 B3**。

### 3.3 新鮮度與日更正交

| 題 | 裁判 |
|---|---|
| 寫側 rebuild＠D | **另句** `GRAPH-REBUILD-D-go`（已示範 08-04／08-05）；**≠**本消費契約 GO |
| 讀側 | 即使表有 D′＞D，train／predict＠D 仍只可用 **≤D** 的策略結果（anti-leakage） |
| B3 standing | **不**因本檔自動加 graph rebuild 或 graph feature |

### 3.4 失敗字句（必註冊）

| 碼 | 何時 | 行為 |
|---|---|---|
| `graph_asof_missing` | 策略選不到合法 asof | SKIP 族／該折；禁 fill |
| `graph_edge_empty` | 有 asof 但邊數=0 或 core 覆蓋過低（閾值另 GO） | SKIP |
| `graph_type_undeclared` | 讀了未在契約聲明的 `edge_type` | FAIL-closed 開發期；產線禁 |
| `graph_leakage_suspect` | 讀到 `as_of_date > D` | **硬 FAIL** |

禁止：median-fill 邊權、用 `knowledge_edge` 冒充股圖、把 SKIP 塗成 pass。

---

## §4 與 NF-pause／序列窗的邊界

| 議題 | 本檔 |
|---|---|
| NF-pause | **維持**；本檔 **≠** `NF-E-go-plan` |
| Seq 窗消費 | draft §5.1 仍有效；**另刀**（可∥文件）；不阻塞本圖契約 |
| 解凍後 0a／0b | 仍要獨立 GO；本契約＝前置條件 checklist 一條 |

---

## §5 分階段（本檔只交給 G0）

| 階 | 交付 | 要另 GO？ | 搶 #1？ |
|---|---|---|---|
| **G0** | 本 plan-first＋REGISTER（本輪） | Steward 採納句 | 否 |
| **G1** | 唯讀探針（count by asof；確認無 src reader） | `GRAPH-CONSUME-probe-go` | 否（秒級∥） |
| **G2** | adapter stub＋契約測試（仍不訓） | `GRAPH-CONSUME-adapter-stub-go`＋仍受 NF-pause | 否 |
| **G3** | 真訓／晉升 | **須** `NF-*-go-plan` 或等價解凍＋八閘 | 與日更互斥時讓 #1 |
| **G-rebuild** | 日更寫邊＠新 D | `GRAPH-REBUILD-D-go`（與消費正交） | 可排在 B3 後，不塞進 B3 內 |

---

## §6 Paste-ready

採納本契約（文件）：

```text
GRAPH-CONSUME-plan-first-adopt | FZ/GATE-keep | NF-pause | hold-#1
# 讀: reports/augur_graph_consume_plan_first_20260806.md
# 產線策略預設意向=S-EQ；≠ train；≠ 改 B3
```

下一步探針（**勿**與上句混貼）：

```text
GRAPH-CONSUME-probe-go | FZ/GATE-keep | skip-sync | read-only
```

解凍／訓（更遠；**勿**與本採納混貼）：

```text
NF-E-go-plan
# 或其它族；須另承認本契約 §3
```

---

## §7 驗收（G0 本身）

1. Steward 能復述：**有多 asof 邊表 ≠ 已有讀者；讀者必須顯式 asof 策略**。  
2. 明文禁止硬編碼 06-30／無聲明 MAX／`asof>D`。  
3. NF-pause 未撤；#1 watcher 未改；無業務碼 diff。  
4. draft＠08-05 降為史料；消費選刀以**本檔**為準。

---

## §8 對 r10 板之建議狀態（採納後由執行帳改色）

| # | 建議 |
|---|---|
| **7** | 🔴→📄 **plan sealed**（碼／adapter 仍 🔴 至 G2＋解凍） |
| **3** | 維持 🟢（寫側） |
| **10** NF | 維持 ❄；本刀不衝突 |

*完。[I] self-reported（#32a）。*
