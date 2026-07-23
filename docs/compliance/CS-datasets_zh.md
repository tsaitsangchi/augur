# Constitutional Compliance Statement — datasets 參考文件（L7）

* **性質**：領域參考文件之 Constitutional Compliance Statement（[N] 聲明；**非**精神／原則 SSOT）
* **涵蓋**（RULING-2026-002 主文二同一列）：`docs/datasets_zh.md` **及** `docs/finmind-references/`（現況含 `datasets.md`）
* **依據**：`AUGUR-MC v1.6 §8.3`；`AUGUR-WM v1.0 §WM.39–45`；RULING-2026-002 主文二（補正期至 **2026-10-14**）
* **登錄 Layer**：7（External Interface／Infrastructure — 資料來源參考）
* **誠實界限**：履行本列補正；不假關 039 殘留；本檔**不**創設預測／特徵義務。

```
compliance-statement:
  spec: Augur Domain Dataset References（datasets_zh＋finmind-references）
  spec-version: 2026-06-15
  layer: 7
  mc-version: AUGUR-MC v1.6
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1, AUGUR-L5 v1.0, AUGUR-L6 v1.2]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: []
  defers-in: []
  defers-out: [D-DATAREF-1]
  date: 2026-07-23
  author: Steward 授權執行層（P2）
  archive-path: docs/compliance/CS-datasets_zh.md
```

## CS.1 逐原則論證（七節）[N]

> **CS.1-PA**〔細化〕
> 引 `AUGUR-MC v1.6 §1.1`。欄位中文／來源／型別族＝可追溯資料字典，支撐「可追溯 Evidence」。判準揭示：中文名來源規則（官方 FM／金融／派生）寫明於正文。

> **CS.1-P1**〔細化〕
> 引 `§P1.E1`。欄位以 API／DB 實證為準；官方取不到才用慣用詞並標來源。判準揭示：已落地讀 DB `information_schema`；未落地以 probe 取真實欄。

> **CS.1-P2**〔細化〕
> 引 `§P2`。本檔為 Representation 輔助索引，**非** Reality；不得替代 live API／PG。判準揭示：與 live 衝突時以 API／DB 為準（原則 #2）。

> **CS.1-P3**〔不適用〕
> 不涉及 Identity。理由：參考表無 Actor／主體解析義務。

> **CS.1-P4**〔細化＋不觸及〕
> 引 `§P4.E1`。溯源至 FinMind／FRED dataset／欄位；不產生 Knowledge 結論。判準揭示：本檔無置信度／GATE 產出。

> **CS.1-P5**〔不適用〕
> 無 Action 授權鏈。理由：靜態參考文件。

> **CS.1-EV-chain**〔不適用〕
> 不實作 EV 迴路。理由：資料字典，非執行規格。

## CS.2 已知緊張關係 [N]

`none`。豁免：`none`。

## CS.3 雙向 DEFER 表 [N]

* **(a) defers-in**：`[]`
* **(b) defers-out**：
  | d-id | 事項 | 目標 | 說明 |
  |---|---|---|---|
  | D-DATAREF-1 | 介面／ingestion 形式義務 | Layer 7 `AUGUR-INF`＋領域 ingestion | 本檔僅參考；抓取義務在 code／原則／INF |

## CS.4 形式充分性＋跨層標注 [N]

MC [N] 落點以 `specs/` 為權威；本檔僅觸及 P1／P2／P4 之資料字典面向；其餘＝**不觸及**。

**跨層標注**：整體 **Layer 7** 參考文件；不含 L4–6 義務句。`finmind-references/` 與 `datasets_zh.md` 同列、共用本聲明（RULING-2026-002）。
