# 預測正交 — code 補正留痕 [I]（2026-07-24）

> **位階**：[I] 工具／接續記憶 · **非** META-CONSTITUTION [N]  
> **依據**：Steward 定義擴充——預測與 FinMind／FRED 無關；**可追溯過去因需 API 之程式修改**  
> **交叉**：`.cursor/rules/predict-vs-market-api.mdc`（code 段）· `audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md` · 追溯總表 `PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md` · P2H `audits/P2H-S123-CLOSED-20260724.md`  
> **凍結**：FinMind／FRED **仍凍**（`finmind-fred-api-freeze.mdc`）；本輪**未**解凍、**未**打 API、**未**假關 Dividend 缺股

---

## 1. Steward 定錨（code 效力）

**所有的預測都與 FinMind／FRED 沒有關係**——庫內既有資料可切分並預測推估。

**此定義可追溯過去因需 FinMind／FRED API 的所有程式修改**——屬預測範圍者依此原則**修改**，效力邊界成立。

| | |
|---|---|
| **yes（code）** | 預測／train／切分／推估／evaluation／baseline／arena 對局本體：讀 DB as-of；缺最新增量→告警續跑；取數與預測入口分離 |
| **仍否** | 放量 sync、解凍取數、假稱資料洞已補、Dividend 缺股已滿、可交易／確立級 |
| **仍 API 門** | ingestion／sync／Dividend resume／FRED 新抓／catalog API／attestation heal 等真取數路徑——**保留**、不改成假本地抓外網 |

---

## 2. 盤點摘要（`src/augur/` · `scripts/`）

### 2.1 預測熱路徑（已是庫內／零 live API import）

| 區 | path（代表） | 盤點結果 |
|---|---|---|
| train／predict | `scripts/train_ranker.py` · `scripts/predict_asof.py` · `scripts/train_*direction*.py` | AST **零** `augur.ingestion`／`finmind`／`fred.fetch`；讀 DB panel／registry |
| evaluation | `src/augur/evaluation/{baseline,walkforward,metrics,portfolio,label}.py` · `scripts/run_evaluation.py` · `scripts/run_economic_eval.py` | 同上；切分／IC／經濟終關純庫內 |
| P2H 契約 | `src/augur/core/prodset_contract.py` · `scripts/verify_prodset_hotpath.py` | 零 API；與本輪正交對齊（S1–S3 已 CLOSED） |
| models／advisor | `src/augur/models/*` · `src/augur/advisor/*` · `src/augur/arena/*` | 無 finmind／fred fetch import |
| feature 消費 | `scripts/build_market_direction_features.py` | 讀庫內 `fred_series` via `macro_vintage.as_of`（**DB PIT**，非 live FRED fetch） |

### 2.2 發現並修正之錯誤依賴

| # | path | 錯誤形態 | 修正 | 落地 |
|---|---|---|---|---|
| 1 | `scripts/run_arena_round.py` | live 對局：`(today - as_of).days > 7` → **exit 1** 且訊息「先跑每日管線 sync」＝以 live sync 為預測硬前提 | 改為 **告警＋以 DB as-of 續跑**；無 PriceAdj 列才拒；docstring 對齊 PREDICT-ORTHOGONAL | 已入 `06adfa9`（與 P2H 同日） |
| 2 | `scripts/run_arena_daily_pipeline.py` | 編排強制 ①FinMind sync + ②FRED sync 後才進對局；取數與預測綁死 | 新增 **`--skip-sync`**（跳過 API 門步驟）；`--skip-sync` 且無 `--date` → as-of＝庫內 PriceAdj max；全鏈 `--run` 明示含 sync＝API 門／凍結下勿開 | 本封存 |
| 3 | `.cursor/rules/predict-vs-market-api.mdc` | 先前僅計畫／拍板效力 | **強化 code 段**：禁 live API 硬前提、缺增量用 DB as-of、取數／預測分離、禁 quota gate 擋 train | 已入 `06adfa9` |
| 4 | `HANDOFF.md` §4.0「預測↔API」 | 未鏈 code 補正 | 補鏈本 audit＋明示 code 效力 | 本封存 |
| 5 | `audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md` | 僅文件追溯 | 補 code 效力一句＋鏈本 audit | 本封存 |

### 2.3 未改——仍 API 門（保留真取數路徑）

| # | path／標的 | 理由 |
|---|---|---|
| 1 | `src/augur/ingestion/{finmind,fred,sync,ingest}.py` | 真取數葉端／編排 |
| 2 | `scripts/{full_market_sync,daily_maintenance,sync_macro,refetch_fixed_tables,repair_priceadj_basis}.py` | 打 FinMind／FRED |
| 3 | `scripts/build_catalog.py` · `src/augur/catalog/*`（probe） | API 探測／登錄 |
| 4 | `src/augur/audit/reconcile.py` · `scripts/reconcile_audit.py` · attestation heal | DB↔API 對帳／heal |
| 5 | Dividend resume／G-DIV-1 | 缺股補抓＝取數洞；**PAUSED**；不得假關 |
| 6 | `run_arena_daily_pipeline.py` **未加 `--skip-sync` 之全鏈 `--run`** | 仍含 sync＝**API 門**（刻意保留；凍結下應走 `--skip-sync`） |

---

## 3. 與 P2H 熱路徑對齊

| 項 | 狀態 |
|---|---|
| P2H S1–S3 | **CLOSED**（`audits/P2H-S123-CLOSED-20260724.md`；commit `06adfa9`） |
| 本輪 | **不衝突**：不改 `prodset_contract`／`baseline.resolve_train_feats`／train／predict 契約；僅補強正交 rule＋arena 取數／預測分離 |
| 熱路徑一句 | **已可庫內 prodset train／predict**（active n=2、as-of 2026-05-31）；**≠**可交易／確立級；**≠**解凍 |

---

## 4. 效力邊界（再述）

- **yes**：預測 code 不得再以「必須 live FinMind／FRED／先 sync」為硬閘；缺增量→DB as-of。
- **仍否**：解凍、放量、假稱 Dividend／洞已補、確立級／可交易。
- **仍 API 門**：上表 2.3；編排全鏈 sync 路徑。
- **未改** `[N]`（constitution／META-CONSTITUTION）。

---

## 5. 不做（本輪）

- 未呼叫 FinMind／FRED；未解凍
- 未假關 Dividend 缺股／G-DIV-1
- 未宣稱可交易／確立級
- 未改治權 [N]

---

## 6. 封存

- slug：`predict-orthogonal-code-remediation`
- 指令：`bash scripts/archive_push.sh --slug predict-orthogonal-code-remediation`
