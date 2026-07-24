# 預測 ↔ FinMind／FRED 正交 — Steward 正式定義＋追溯效力 [I]（2026-07-24）

> **位階**：[I] 工具 rule＋HANDOFF＋audits · **非** META-CONSTITUTION [N]（入憲另開案）  
> **碼**：`PREDICT-ORTHOGONAL` · 追溯表＝`audits/PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md`

## Steward 定錨（原文要旨）

**所有的預測都與 FinMind 及 FRED 沒有關係**——就算沒有現在最新的資料，過去已存在資料庫內的資料仍可拿來做**資料切分**並進行**預測推估**。

**此定義可以追溯過去因需 FinMind API 及 FRED API 不能拍板的所有文件**，都依此原則進行拍板，**效力邊界為 yes**。

## 效力邊界

| | |
|---|---|
| **yes** | 允許依庫內已落地資料 **plan／實作／驗收**（train／backtest／as-of 切分／predict／相對強度 hotpath 等） |
| **仍否** | 放量 sync、解凍取數、假稱資料洞已補、Dividend 缺股已滿、可交易／確立級（除非原計畫另有閘且已過） |
| **仍 API 門** | 不屬預測、真需外部 API 補洞（Dividend resume、FRED 新 series、正典 attestation heal、全量 catalog API 等）→ **不得**假追溯 yes |

## 落地

| 產物 | path |
|---|---|
| alwaysApply rule | `.cursor/rules/predict-vs-market-api.mdc` |
| 凍結交叉（取數仍凍） | `.cursor/rules/finmind-fred-api-freeze.mdc`（允許段＋交叉一句；**未**解凍） |
| HANDOFF | `HANDOFF.md` §4.0「預測↔API」＋ prodset→熱路徑 |
| 追溯總表 | `audits/PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md` |
| P2H 正式拍板 | `audits/P2H-PLAN-APPROVED-20260724.md`（Steward「回拍板碼」；執行未開） |
| 本留痕 | 本檔 |

## 與凍結正交

- **凍結仍有效於取數**（sync／probe／放量／Dividend／FRED）。
- **預測拍板／執行不因凍結而否決**。
- 「可以預測」**≠**「可以再開 API」。

## 不做（本輪）

- 未改 `constitution/`／META-CONSTITUTION [N]
- 未解凍 FinMind／FRED；未開外部 API
- 未假稱確立級／可交易／Dividend 完備
