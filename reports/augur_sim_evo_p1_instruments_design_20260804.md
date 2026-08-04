---
title: sim 自進化 P1 儀器設計（共槽／時鐘／假兆／檔位）
status: draft
date: 2026-08-04
viewpoint: 2026-08-04T08:20+08:00
ssot_parent: OPT-SIM-EVO-20260804-go
based_on:
  - reports/augur_local_ai_sim_evolution_plan_20260804.md
  - audits/OPT-SIM-EVO-P0-OBS-20260804.md
  - reports/augur_optimization_step_plan_r2_20260804.md
layer: "[I]"
fz: keep
gate: keep
m_t5: watch
self_reported: true
implements: P1-1..P1-4（設計；本檔不實作大碼）
---

# sim 自進化 P1 儀器設計（2026-08-04）

> **性質**：[I] 儀器設計——落地計畫書 P1（共槽儀表／時鐘看板／假兆探針／模型檔位卡）。  
> **父 SSOT**：`reports/augur_local_ai_sim_evolution_plan_20260804.md`（`OPT-SIM-EVO-20260804-go`）。  
> **前置觀測**：`audits/OPT-SIM-EVO-P0-OBS-20260804.md`（selftest 9/9 綠；DB 拒連；run22 仍 running；P0 整綠未達）。  
> **硬紀律（本寫作窗）**：不搶 `heavy_slot`；不 `--allow-apply`；不改 evolution driver；FZ-keep；**不 commit／push**；本檔＝純設計（**不**實作 `report_slot_and_sim_dashboard.py` 大碼，除非 Steward 另裁「最小探針骨架」）。  
> **#32a**：self-reported；live 數字引用 P0 audit／計畫視點，本檔不重查 DB。

---

## §0 一頁摘要

| 項 | 內容 |
|---|---|
| **what** | 四件儀器的**契約**：輸入／輸出／驗收／可跑條件／禁做 |
| **why** | L1（缺共槽一頁）＋L3（敘事假兆）＋B2（DB 抖動下仍誠實）——儀表必須在「鎖不可讀」時**降級而非假綠** |
| **本檔交付** | 設計＝可拍板實作序；**零寫庫**；可選最小探針骨架另裁 |
| **與 P0** | P0-C／P0-D 仍卡終態＋DB；P1 設計可與 run22 **並行**（Lane-SIM-DOC） |
| **與 Step1** | **不搶**結輪後「第一執行刀」＝65 triage；儀表實作錯峰於 Lane-R 重 SQL |

**一句**：儀器量的是「誰佔槽、時鐘走到哪、有沒有假兆詞、模型檔位有沒有混」——**不是**校準綠燈、**不是**可交易、**不是** run22 終態代理。

---

## §1 儀器總表（觀測／閘）

> 欄位說明：**可現跑**＝run22 running＋DB 拒連仍可；**須結輪＋DB**＝P0-C／P0-D 語意或 live 水位。

| ID | 名稱 | 主要產物 | 可現跑？ | 須結輪＋DB？ | Steward |
|---|---|---|---|---|---|
| **P1-1** | 共槽儀表 | 唯讀 script＋一頁 stdout／可選 md audit | **部分**（ps／load／禁忌句） | slot 真鎖態、evolution_run 水位 | 否（唯讀） |
| **P1-2** | 時鐘看板 | 包 `check_sim_clock`＋settle／K 進度解讀 | `--selftest` 可；`--check` **否**（今） | live 週報行／K／pending | 否 |
| **P1-3** | 假兆探針 | 靜態／純函式斷言（報告詞＋synthetic） | **是**（零 DB、免重訓） | 可選：DB 列抽樣驗 `is_synthetic` | 升嚴需裁 |
| **P1-4** | 模型檔位卡 | 文件釘死（本檔 §5＋交叉引用） | **是**（文件） | 否 | 否 |

---

## §2 P1-1｜共槽儀表（`report_slot_and_sim_dashboard`）

### 2.1 定位

計畫 §7.2 可選新 script：`scripts/report_slot_and_sim_dashboard.py`  
＝把既有碎片（`check_parallel_capacity`／`heavy_slot.holder_status`／`ps`／禁忌）收成**一頁**，服務 L1＋step Lane-R 監看敘事。

**角色**：觀測儀——**永不** `HeavySlot.acquire()`／`defer()`／寫 `evolution_deferred_work`／寫任何 sim 生產表。

### 2.2 組裝既有（優先複用，禁重造鎖邏輯）

| 來源 | 複用什麼 | 本儀表如何用 |
|---|---|---|
| `scripts/check_parallel_capacity.py` | `snapshot()`／`advise_lanes`／`format_week_line`／DB 掛時 holders 降級註記 | 容量段＋建議並行上限 |
| `augur.core.heavy_slot` | `holder_status()` **唯讀** | slot 段；例外→印 `pg_unreachable`，**不得**印「空槽可搶」 |
| `ps`／`/proc` | TWEVO／sim／arena／ollama 進程樣式 | 進程段（對齊 P0-A） |
| `check_sim_clock` | 可選子呼叫 `--week-line` | 時鐘一行（DB 通才有真數） |
| 計畫 §5／§6 | 禁忌句模板 | 固定 stderr／stdout 尾段 |

### 2.3 CLI 契約（#29 矩陣草案）

```
python3 scripts/report_slot_and_sim_dashboard.py           # 無參數＝--check（唯讀）
python3 scripts/report_slot_and_sim_dashboard.py --check
python3 scripts/report_slot_and_sim_dashboard.py --json
python3 scripts/report_slot_and_sim_dashboard.py --week-line   # 單行：容量＋slot 降級態＋禁忌碼
python3 scripts/report_slot_and_sim_dashboard.py --selftest    # 零 DB 純函式；含先驗紅（§6）
```

### 2.4 輸入／輸出

| 輸入 | 來源 | 缺則 |
|---|---|---|
| nproc／loadavg／MemAvailable | `/proc` | 印 0／未知＋rc 不因缺欄假裝綠（沿用 capacity 紅門檻） |
| llama／ollama RSS | `/proc` cmdline 掃描 | 0 MB |
| heavy_slot holders | `holder_status()` | **`slot_status=unreachable`**（字面必現）；holders=[] **不得**解讀為 idle |
| 進程分類 | `pgrep`／cmdline 啟發式 | 該類＝none（誠實） |
| sim 週報行（可選） | `check_sim_clock` 邏輯或子進程 | `clock=deferred_pg` |

**stdout 建議區塊（一頁）**：

1. **SLOT** — `reachable|unreachable`；holders／orphans；禁忌碼 `NO_ACQUIRE`  
2. **PROCS** — `twevo_parent`／`twevo_i3`／`sim_*`／`arena_*`／`ollama|llama`（pid＋elapsed 若可得）  
3. **CAP** — 與 `check_parallel_capacity` week_line 同形  
4. **CLOCK** — 有 DB：`sim 時鐘：K=…`；無 DB：`sim 時鐘：unavailable (pg)`  
5. **TABOO** — 固定句：「禁搶 heavy_slot／禁 --allow-apply／禁殺 run22／FZ-keep／sim 校準≠可交易≠確立級」

**rc 語義（防假綠）**：

| 條件 | rc | 意義 |
|---|---|---|
| selftest 全過 | 0 | 純函式鎖 |
| `--check` 且 PG 拒連 | **0 或 2（建議 2＝降級完成）** | **不得**當「槽空」；文件宣稱「降級成功≠slot 空」 |
| capacity 硬紅（available／load） | 1 | 沿用既有 |
| 偵測到 sim `--apply` 活進程且 slot 他持 | 1＋WARNING | 撞車哨（唯讀告警，不殺） |

> **設計裁決（建議預設）**：`--check` 在 `slot_status=unreachable` 時 **rc=2**（明確降級），避免與「全綠 idle」混讀；若現有腳本慣例忌非 0/1，則改 **rc=0＋stdout 必含 `UNREACHABLE` 字面**，selftest 斷言該字面在假 PG 路徑必現（#35 禁只測「沒炸」）。

### 2.5 驗收

1. `#29` 矩陣＋無參數 graceful。  
2. `--selftest` 零 DB；**先驗紅**（§6.2）。  
3. DB 拒連路徑：stdout 含明確 `unreachable`／`UNREACHABLE`；**不得**出現「heavy_slot 持有者=無」而無 unreachable 註記（P0 教訓）。  
4. 全檔 grep：無 `acquire(`／`--allow-apply`／FinMind fetch。  
5. 實測：run22 期間跑 `--check` 不得抬 CPU 至干擾 I3（單次彙總、禁忙等迴圈；承 #33）。

### 2.6 何時可跑

| 模式 | run22 running | DB 拒連 | 說明 |
|---|---|---|---|
| `--selftest` | ✅ | ✅ | 今即可（對齊 P0） |
| `--check` 進程＋CAP＋TABOO | ✅ | ✅ | 今即可（部分頁） |
| `--check` 完整 SLOT＋CLOCK | ✅ | ❌ | DB 復通後；**仍禁 acquire** |
| 結輪後 morning 替代 | — | — | **不**取代 `observe_twevo_run22 --morning`（P0-C 另軌） |

---

## §3 P1-2｜時鐘看板

### 3.1 定位

**不新造第二套時鐘**：SSOT 邏輯＝`scripts/check_sim_clock.py`（閘 `SIM-CAL-R1`、`K_TARGET=3`、`H_TD=21`、`arm=live`）。  
P1-2＝「看板契約」：儀表如何呈現＋與 settle／evaluate 節奏的**解讀欄**（文件／可選 dashboard 子段）。

### 3.2 輸入／輸出（既有）

| 指令 | 輸入 | 輸出 | 依賴 |
|---|---|---|---|
| `--selftest` | 純函式 fixture | 紅綠 | 零 DB — **可現跑** |
| `--check`／預設 | `evolution_prereg_gate`＋`sim_run_link`⋈`mc_simulation_run`＋`sim_realized_outcome`＋交易日曆 | 詳情＋週報行 | **DB** |
| `--week-line` | 同上 | `sim 時鐘：K=n/3，下一格 …，待結算 n 列` | **DB** |
| `--json` | 同上 | snapshot dict | **DB** |

### 3.3 看板解讀欄（文件義務；數字仍出 DB）

| 欄 | 意義 | 假綠禁 |
|---|---|---|
| `K=n/3` | 校準窗格點進度；n&lt;3 ⇒ **不得**催 `decide` 當完成 | 禁把 K=0 寫成「尚未需要首格」而不對帳 `sim_run_link` |
| `下一格` | `未實現`／具體日／`無門` | 禁猜未來交易日（#8；函式已不猜） |
| `待結算` | 有 link、無 `sim_realized_outcome` | 禁把 pending=0 當「回路完成」（可能根本無首格） |
| `gate/status` | SIM-CAL-R1 | `無門`≠時鐘壞，是門未就緒 |

### 3.4 與 P0-D／P2 接口

- P0-D 首格盤點：**獨立 audit**（已落地／未落地／undecidable）；時鐘看板**引用**該結論，不代裁 `--apply`。  
- P2-2 settle：看板只提示「label／pending」；apply 仍須人工節奏＋明示。  
- P2-3 evaluate：K&lt;3 ⇒ 看板註「五臂前提未滿」——探針可另斷言（P1-3）。

### 3.5 驗收

1. 不複製 `next_grid_asof`／`k_progress` 第二份邏輯；dashboard 若需要則 **import 同模組純函式** 或子呼叫。  
2. DB 掛：儀表 CLOCK 段降級，**不得**用 selftest 綠充當 live K。  
3. P0 已證 `--selftest` rc=0；live `--check` **列入「DB 復通後」清單**，本設計波不強制跑。

---

## §4 P1-3｜假兆探針

### 4.1 定位

靜態／純函式閘——抓住「把 sim 校準／LLM 提案寫成可交易或確立級」「LLM 提案未標 synthetic」之類敘事與契約違規。  
**Lane-G 友好**：零重訓、零寫庫、可與 I3 輕並行（短跑）。

### 4.2 探針清單（建議一支或多支；預設新檔名）

| 探針 ID | 斷言 | 建議入口 | 輸入 | 先驗紅（#35） |
|---|---|---|---|---|
| **FP-A** | 指定 path 集合（`reports/*sim*`／`audits/OPT-SIM*`／本專項）不得含裸宣稱詞：`可交易`、`確立級`（允許「≠可交易／禁確立級」否定位） | `scripts/probe_sim_false_signal_lexicon.py`（草案） | 檔列表或 stdin | 餵含「sim 校準通過故可交易」之 fixture → 必紅 |
| **FP-B** | `gain_basis` 合法集 ⊆ `{calibration_delta,none,incomparable}`（對齊計畫 §1）；報告禁把 #14 經濟綠與 sim 校準綠並列為同一「過門」 | 同支或 `probe_sim_ruler_mix.py` | 字串／md | 混尺句 fixture → 紅 |
| **FP-C** | `origin=llm_local` 列／提案路徑：**必** `is_synthetic=true` 且 `trust_rank=TR-C`（專章 §2.3；`propose_sim_candidate` carryover 路徑不適用強制式，探針須分 origin） | 純函式＋可選 DB | fixture row dict；DB 可選 | 假列 `llm_local`＋`is_synthetic=false` → 紅 |
| **FP-D** | `decide_sim_verdict`：`promoted_eligible` ⇒ `write_allowed=false`（既有 selftest；探針可再掛「字面／行為」雙向，但**禁**只 grep 字串當唯一鎖——#35(3)） | 呼叫既有 `--selftest` 或 import 判決純函式 | — | 弄壞 `write_allowed` → 紅（突變／注入） |
| **FP-E**（#32 銜接） | 任何「本地 AI／sim LLM 有能力」宣稱 → 須見三臂語境（地板／上限／錯配）或標 `self-reported`＋「無證據」；探針只做**文件面**詞＋標記，不代替 `eval_local_model` | 文件掃描 | md | 單臂誇功句 → 紅 |

### 4.3 可現跑 vs 須 DB

| 探針 | 可現跑 | 須 DB |
|---|---|---|
| FP-A／B／E | ✅ | — |
| FP-C 純函式 | ✅ | 列抽樣可選（復通後） |
| FP-D | ✅（既有 selftest） | — |

### 4.4 驗收

1. **凡新回歸鎖必先驗紅**（#35）——紅證寫入 commit 訊息或 `audits/`（實作波）；設計波先把「怎麼弄紅」寫死於上表。  
2. **禁字面斷言當唯一證明**：例如「源碼含 `write_allowed`」≠機制在；優先餵真決策 dict。  
3. 探針自身 rc=0 **不得**被敘述成「sim 軸已上膛／首格已落地」（P0-D 仍可能未知）。  
4. 部分升嚴（把否定位白名單收窄、擴大掃描 glob）→ Steward 裁。

### 4.5 與 `check_false_assertions.py`

- 全庫 `#35` 靜態基線仍走既有 `scripts/check_false_assertions.py --gate`。  
- P1-3＝**領域詞＋sim 契約**；不重複造通用 false-assertion 引擎。  
- 新增探針若含 `__main__` → 須指令矩陣＋`--selftest`（#18／#29）。

---

## §5 P1-4｜模型檔位卡（文件釘死）

> 本節＝儀器「卡」本身；交叉引用以本檔＋父計畫為準，**不改** MCP 環境變數實值（除非另案）。

| 用途 | 模型 | 釘死處 | 禁 |
|---|---|---|---|
| MCP 濃縮／檢索（`local-llm`） | **qwen3:4b** | `.cursor/rules/local-mcp-routing.mdc`；父計畫 §2.4 | 把 **8b** 寫進 MCP `LLM_MODEL` |
| advisor／主 UI | **qwen3:8b** | HANDOFF／常駐服務 | 與 MCP 混檔當「同一個本地腦」敘事 |
| sim LLM 候選（若開 P2-5） | **4b**＋日預算／Ollama 單模型串行鎖 | 07-31 H-11；本專項 L4 | run22／I3／LAIEVO 佔槽時開候選窗 |
| LAIEVO | `eval_local_model`（三臂+） | CLAUDE #32；與 heavy 互斥 | 單臂分數誇能力 |

**儀表銜接**：P1-1 PROCS 段若見 `ollama`／`llama-server`，TABOO 附註「檔位卡：MCP≠advisor；sim 候選須 slot 空」。

**驗收**：HANDOFF／本專項／本設計三處交叉引用一致；無「MCP 已升 8b」類漂移句。

---

## §6 假綠防呆總則（#35／#32）

### 6.1 適用判斷句

1. 「這個綠燈量的是不是它宣稱在量的東西？」  
2. 「這機制若壞了，會不會安靜變綠燈？」  

任一言不出 → 重寫探針／儀表 rc 語義。

### 6.2 P1-1 selftest 先驗紅劇本（設計義務）

| # | 弄壞方式 | 期望 |
|---|---|---|
| R1 | mock `holder_status` 拋 `OperationalError` | 輸出必含 unreachable；**且**不得格式化成「持有者=無」而無註記 |
| R2 | 注入 holders 非空但故意把 `slot_status` 標 idle | 組合器純函式拒／紅 |
| R3 | 輸出遺漏 TABOO 句 | 結構斷言紅 |
| R4 | 程式路徑呼叫到 `acquire` | 靜態或下游絆線紅（寧可 import 禁名單） |

### 6.3 與 #32

- 儀表／探針輸出一律可標 `self_reported`（觀測敘事）。  
- **不得**用儀表綠宣稱「本地 AI 有校準能力／有預測能力」。  
- 能力宣稱仍走 `eval_local_model` 三臂；P1-3 FP-E 只擋文件面偷渡。

### 6.4 已知假綠陷阱（本專項）

| 陷阱 | 對策 |
|---|---|
| selftest 9/9 綠 ⇒ P0 整綠 | P0 audit 已駁；儀表 TOC 重申 |
| DB 拒連＋holders=[] ⇒ 槽空 | unreachable 強制字面 |
| K 進度未知 ⇒ 時鐘未上膛可忽略 | P0-D 三擇一必填 |
| 校準／判決 selftest 綠 ⇒ 可交易 | FP-A／TABOO |
| morning 未跑卻寫 I5B 收口 | P0-C 專軌；儀表不代 observe |

---

## §7 schema／表消費

### 7.1 本波原則

父計畫 §7：**預設無新表**；儀器結果落 **stdout／reports／audits**。  
下列皆為**消費（讀）**；P1 實作波仍 **零寫**（除未來 Steward 明示之 audit md）。

| 表／來源 | P1 誰讀 | 寫？ | 備註 |
|---|---|---|---|
| `heavy_slot_holder_log`＋`pg_locks` | P1-1 via `holder_status` | 否 | 不可達→降級 |
| `evolution_run`／ledger | P1-1 可選摘要 | 否 | **不**取代 observe morning |
| `evolution_prereg_gate` | P1-2 | 否 | gate_id=`SIM-CAL-R1` |
| `sim_run_link`／`mc_simulation_run`／`sim_realized_outcome` | P1-2 | 否 | K／pending |
| 交易日曆（`tw.daily_bar` via registry） | P1-2 | 否 | 禁 vendor 直綁 |
| `sim_evolution_candidate`／`sim_llm_proposal` | P1-3 FP-C（可選） | 否 | llm_local 抽樣 |
| `sim_calibration_eval`／`sim_evolution_verdict` | 不在 P1 熱路徑 | 否 | P2 |
| `risk_policy` | **不讀作儀表綠** | **禁寫** | 父計畫正交 |
| `promotion_queue` | 可選交叉提示「≠ sim」 | 否 | 防敘事混軸 |

DDL SSOT 仍＝`scripts/migrate_sim_evolution_ddl.py`（P0 selftest 已綠；**本波不 `--apply` migrate**）。

### 7.2 新表草案（僅引用父計畫——**預設不建**）

僅當「進程態無法綴合 audit」且 Steward 要持久化哨兵時，父計畫 §7.3：

```sql
-- DRAFT ONLY — 非本波義務；不得擅自 --apply
CREATE TABLE IF NOT EXISTS ops_runtime_heartbeat (
    observed_at   timestamptz PRIMARY KEY DEFAULT now(),
    channel       text NOT NULL CHECK (channel IN ('twevo','sim','arena','ollama','pg')),
    pid           int,
    detail_json   jsonb NOT NULL,
    source        text NOT NULL  -- 'ps'|'log'|'db'
);
```

**P1 裁決**：先靠 stdout＋audit md；**心跳表不列入 P1 實作序**。若日後建表→另開案＋migrate `--apply` 明示＋append-only 紀律。

---

## §8 與 heavy_slot／TWEVO／Step1 65 的隔離

### 8.1 資源互斥（執行）

| 行動 | run22 `running` | Step1 65 triage 窗 | 註 |
|---|---|---|---|
| 本設計文件／audit md | ✅ | ✅ | Lane-SIM-DOC |
| P1 `--selftest`／假兆靜態探針 | ✅（輕） | ✅ | 勿滿載 |
| P1-1 `--check` 完整 DB | ⚠ DB 通才有意義；**仍禁 acquire** | 錯峰重 SQL | |
| Lane-SIM-APPLY／首格 | ❌ | 錯峰（第二曲） | 另裁 |
| 殺 run22／縮 I3 逾時 | ❌ | ❌ | 父計畫 §6 |
| 宣稱「第一刀＝sim 儀表實作」蓋過 65 | ❌ | ❌ | step SSOT 優先 |

### 8.2 敘事隔離（產物）

| 軸 | 合法目標敘事 | 儀表禁寫成 |
|---|---|---|
| TWEVO／PME | G-PROM／G-ECON；queue／prodset | sim 校準進度 |
| Step1 65 | world_concept triage（唯讀報告） | sim K／slot |
| sim | 風險形狀校準；K／pending／verdict | 可交易／確立級／evaluated_pass |
| arena | 方向／隊伍；白名單≠解凍 | sim 首格自動產 |

### 8.3 優先序衝突

`step r2`（`OPT-STEP-R2-20260804-go`）**>** 本專項。  
結輪後：**先** Step1 65 triage；sim 儀器**實作**可後接或輕並行，**不**申請插隊為「夜班後第一刀」。

---

## §9 實作序（仍偏設計／小步——本檔不開工大碼）

> 優先**純設計已滿足 P1 文件義務**。下列＝Steward 裁「實作」後之建議序。

| 序 | 項 | 估量 | 前置 | 產出 |
|---|---|---|---|---|
| **0** | （本檔）設計拍板／小修 | 文件 | — | `status: draft→current`（人裁） |
| **1** | P1-4 交叉引用掃一遍（HANDOFF 一句鏈到本檔） | 極小 md | 否 | 文件一致 |
| **2** | P1-3 FP-A／B 最小探針骨架＋`--selftest`＋先驗紅證 | 小 script | 否 | 可現跑 |
| **3** | P1-1 dashboard：**先**純函式組裝器＋selftest（mock PG），再接 live `--check` | 中 | 建議等 DB 復通再標「完整頁驗收」 | script |
| **4** | P1-2：dashboard 接 clock week_line；無新邏輯 | 小 | DB | 一頁 CLOCK 段 |
| **5** | FP-C／E 擴充；可選 DB 抽樣 | 小 | 可選 DB | 探針 |
| **6** | 實作波 audit（指令／rc／先驗紅） | audit md | 2–5 | `audits/OPT-SIM-EVO-P1-…` |

**本波不做**：driver 改動、`--apply`、心跳新表、接 cron、TWEVO `--allow-apply`、65 triage SQL。

**最小探針骨架**：計畫 P1 **未**強制本刀交付 code；預設＝**僅本設計檔**。若 Steward 選「先做 FP-A 骨架」→ 只動探針小檔＋selftest，仍不搶 slot。

---

## §10 與 P0 狀態對照（誠實窗）

| P0 項 | 狀態（引 P0 OBS ≈08:12） | 對 P1 |
|---|---|---|
| B1 run22 | 仍 running | P1 僅 DOC／selftest／輕 check |
| B2 PG | 拒連 | 完整 SLOT／CLOCK 驗收推遲 |
| P0-C／D | 不可驗收 | 儀表不代決 |
| selftest 9/9 | 綠 | 可當「純函式地板」，非階段綠 |

---

## §11 AskQuestion（請 Steward 裁）

1. **實作最小探針**：是否現在開 FP-A（假兆詞）骨架＋`--selftest`（仍零 DB、不搶 slot）？  
2. **等結輪**：是否維持僅文件＋P0-A 監看，待 run22 終態＋DB 復通再做 P1-1 live 頁＋P0-C／D？  
3. **commit**：是否 commit（另問 push）本設計＋`audits/OPT-SIM-EVO-P0-OBS-20260804.md`（及是否連同計畫／GO audit）？

---

## §12 回報摘要

| 項 | 內容 |
|---|---|
| **路徑** | `reports/augur_sim_evo_p1_instruments_design_20260804.md` |
| **狀態** | `draft`（待 Steward 升 current／開實作） |
| **覆蓋** | P1-1～P1-4 契約；schema 只讀；隔離；#35／#32；實作序 |
| **未做** | 大碼 dashboard；不搶 slot；不 apply；不 commit |
| **父碼** | `OPT-SIM-EVO-20260804-go` · FZ-keep · GATE-keep · M-T5-watch |

---

*完。self-reported（#32a）。*
