# Constitutional Compliance Statement — 系統架構大憲章 v1.49.0

* **性質**：領域治權檔之 Constitutional Compliance Statement（[N] 聲明；**不上收** docs 進 META）
* **依據**：`AUGUR-MC v1.6 §8.3`；`AUGUR-WM v1.0 §WM.39–45`；RULING-2026-002 主文二（補正期至 **2026-10-14**）
* **登錄 Layer**：7（Infrastructure／領域架構承載；涉 L4–6 由本聲明逐節標注）
* **正文 SSOT**：`docs/系統架構大憲章_v1.49.0.md`
* **誠實界限**：履行本檔補正；不假關 039／025／029 等其他 10-14 項。
* **本版增量**：v1.49.0 第一部補「策展映射住 PostgreSQL（curated-mapping SSOT）」——策展映射／詞表／別名 runtime SSOT＝PG、know-how 產生禁領域 hardcode、明示豁免清單；知識層表 roster 加 `retrieve_glossary`／`advisor_distill_seed_topic`（見 `audits/NHC-CONSTITUTE-CLOSED-20260729.md`）。

```
compliance-statement:
  spec: Augur Domain Architecture Charter（系統架構大憲章）
  spec-version: v1.49.0
  layer: 7
  mc-version: AUGUR-MC v1.6
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1, AUGUR-L5 v1.0, AUGUR-L6 v1.2]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: []
  defers-in: []
  defers-out: [D-CHARTER-1]
  date: 2026-07-29
  author: Steward 授權（KH10-AUTO-ADMIT 入憲）
  archive-path: docs/compliance/CS-系統架構大憲章_v1.49.0.md
```

## CS.1 逐原則論證（七節）[N]

> **CS.1-PA**〔細化〕  
> 引 `AUGUR-MC v1.6 §1.1`。三敵人×管線＝PA 可追溯／可修正之領域架構敘事。v1.48.0 准入改機械＋硬閘，仍可修正（suspend／負面清單）。

> **CS.1-P1**〔細化〕  
> 引 `§P1`、`§2.1`。PG＝唯一系統記錄。知識一律准入仍落地 PG；原文 source-pure（#1）不變。

> **CS.1-P2**〔細化〕  
> 引 `§P2.E4`、`WM.9`。權威三分；禁稱 PG 為 Reality。

> **CS.1-P3**〔不適用〕  
> Identity 屬 AUGUR-ID／L6。

> **CS.1-P4**〔細化〕  
> 知識准入改機械不改預測閘；PME／可交易仍另閘。

> **CS.1-P5**〔細化〕  
> 硬閘（license／負面清單）與 KPI 不凌駕仍守。

> **CS.1-EV**〔細化〕  
> 漸進 KH update 可帳本複現；review_log 留機械 actor。

## CS.2 誠實界限

本 CS 僅覆蓋領域憲章 v1.48.0；不關閉 META 其他 10-14 日曆項。
