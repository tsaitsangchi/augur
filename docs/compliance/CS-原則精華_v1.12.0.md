# Constitutional Compliance Statement — 原則精華 v1.12.0

* **性質**：領域治權檔之 Constitutional Compliance Statement（[N] 聲明；**不上收** docs 進 META）
* **依據**：`AUGUR-MC v1.6 §8.3`；`AUGUR-WM v1.0 §WM.39–45`；RULING-2026-002 主文二（補正期至 **2026-10-14**）；§0.5（跨層條款由本聲明逐條標注）；**RULING-2026-041**（P3／#7↔P4.E5）
* **登錄 Layer**：4（Knowledge System 領域治權）
* **正文 SSOT**：`docs/原則精華_v1.12.0.md`
* **誠實界限**：履行本檔補正義務；**不**假關 039 殘留；**T-PRIN-7-P4E5 規範緊張已閉**（RULING-2026-041）；AUD-02 **code** 操作閉合仍 defer（非豁免 P4.E5）。
* **本版增量（v1.12.0）**：(a) **P9**＝升版哲學增「修法權唯 Steward 親簽（`§8.1`）／證據先於結論（`§8.5(a)`）／被退回提案須留檔」三行；(b) **P3**＝FREEZE→解凍子條之權威凍結值由 DB 單列 id 改角色語義＋不變式、具名降 [I]（過 `§KS.4`、不違 `§0.6(b)`）；(c) **P1**＝新增「普遍晉升路徑（總則從屬）」段（從屬大憲章 v1.50.0 總則五節點、得加嚴不得減省）。判準內涵：(a)(c) 收緊、(b) 零變動。依據＝hugo 對話拍板 2026-07-30「P1,P4,P9-照案」／「P3 一次修四處」／「P11 先修三則 high」〔claude 繕打，不冒充親簽 `§8.1`〕；SSOT＝`reports/augur_treaty_core_alignment_plan_20260730.md` §九；留痕 `audits/TREATY-P1P3P4P9P11-20260730.md`。
* **open-tension（新增，不假關）**：**T-PRIN-20-VERSIONING**＝2026-07-24 commit `8c028ce` 對 #20 ENFORCE 之實質改寫當時未升版亦無演進記錄，已於 v1.11.0 補記列如實載明；**其等級認定（重大判準修正 vs 文字澄清）仍待 Steward**，本檔不代為認定。
* **本版增量（v1.11.0）**：#1 WHAT 去供應商依賴——「真實 FinMind/FRED API 值」→「經登錄觀測通道之真實值」＋「真實性繫於通道之登錄、不繫於供應商名」＋現行通道清單降 [I]＋新通道經 World Concept Registry 登錄（`§WM.35–36`）。**判準內涵零變動、ENFORCE 一字未動**；目的＝使 #1 過 `AUGUR-KS v1.1 §KS.4` 刪名測試，並使本條不因新登錄域之值非由該二通道供應而字面失覆蓋。依據：hugo 對話拍板 2026-07-30「乙-2」〔claude 繕打，不冒充親簽 `§8.1`〕；計畫書 `reports/augur_treaty_core_alignment_plan_20260730.md` §四 乙-2；留痕 `audits/PRIN-B2-DENAME-20260730.md`。
* **刪名測試（`§KS.4`）自陳**：#1 刪去「FinMind／FRED」後條款內涵不變（所指為「經登錄觀測通道之真實值」）＝合法指名；#17 原已寫「（及任何 API）」＝合法例示；#18 之 `/datalist` 為 [I] 操作指引（現行通道之取得程序），非「真實」之定義依據。**本次僅改 #1，其餘不動**（最小邊界）。

```
compliance-statement:
  spec: Augur Domain Principles（原則精華）
  spec-version: v1.12.0
  layer: 4
  mc-version: AUGUR-MC v1.6
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: []
  defers-in: []
  defers-out: [D-PRIN-1, D-PRIN-2]
  date: 2026-07-30
  author: Steward 授權執行層（v1.11.0＝hugo 對話拍板「乙-2」繕打；前版 P3／RULING-2026-041）
  archive-path: docs/compliance/CS-原則精華_v1.12.0.md
```

## CS.1 逐原則論證（七節）[N]

> **CS.1-PA**〔細化〕
> 引 `AUGUR-MC v1.6 §1.1`。20 條不可違反法律＝領域對 PA「可追溯／可修正／不確定性可追溯」之操作化。判準揭示：違反任一條＝治權違規（正文）。

> **CS.1-P1**〔細化〕
> 引 `§P1.E1`、`§2.1`。#1 零幻像／#2 API 即權威＝Reality 觀測優先於手維臆測。判準揭示：特徵值須可溯 API／數學轉換；算不出＝缺列。

> **CS.1-P2**〔細化〕
> 引 `§P2.E4`、`§P2.W1`。#12 SSOT／#9 思想≠特定值＝禁把 Representation／思想常數誤當 Reality。判準揭示：feature 禁 hardcoded 知識字典／閾值入公式。

> **CS.1-P3**〔不適用〕
> Identity 型別／解析屬 AUGUR-ID。理由：本檔不定義 Identity。

> **CS.1-P4**〔細化〕
> 引 `§P4.E1`–`§P4.E8`、`§P4.W1`。#1／#7／#8／#15 對映 Evidence／對帳／anti-leakage／誠實回報。**#7（v1.10.0）**：live＝當前 API ＋舊觀測 append-only superseded（對齊 `§P4.E3`／`§P4.E5`；RULING-2026-041）。判準揭示：對帳 attestation 四類可機器盤點；anti-leakage 須 purged 口徑；supersede 機器落點＝AUD-02（code 受閘）。

> **CS.1-P5**〔細化〕
> 引 `§P5.W2`、`§P5.W4`。#20 自驅動×實證＋人決策；#16 clean-room。判準揭示：治權判準變更／破壞性操作須人確認。

> **CS.1-EV-chain**〔細化＋不觸及〕
> 引 `§4`。資料→特徵→宇宙→模型→驗證之領域法律支撐 EV 鏈消費面；Action／Gate 形式屬 L5–L6。判準揭示：經濟終關／GATE 未過不得確立級宣稱（#14／解凍子條）。

## CS.2 已知緊張關係 [N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| ~~T-PRIN-7-P4E5~~ | 原則精華 #7；`§P4.E5` | （史料）舊 #7 覆蓋語意 vs 禁 LWW | **已閉（2026-07-23）**。RULING-2026-041：#7→supersede；**非豁免**。操作／code＝D-PRIN-2。 |

豁免登記：`none`（waivers: []）。`open-tensions: []`。

## CS.3 雙向 DEFER 表 [N]

* **(a) defers-in**：`[]`（本檔不承接 WM Annex D 編號掛鉤；領域法律由正文自足）。
* **(b) defers-out**：
  | d-id | 事項 | 目標 | 說明 |
  |---|---|---|---|
  | D-PRIN-1 | Knowledge／Evidence 形式型別 | Layer 4 `AUGUR-KS` | 正式規格為權威 |
  | D-PRIN-2 | AUD-02 `raw_supersede_log` **code**／migration 操作閉合 | remediation／Phase 7 窗 | 規範已對齊（041）；**非** P4.E5 豁免；至遲併 **2026-10-14** 補正／Phase 7 節奏（RULING-012）；**不**假關 039 其他項 |

## CS.4 形式充分性＋跨層標注 [N]

MC [N] 機器落點以 `specs/` 為權威；本檔觸及者見 CS.1；其餘＝**不觸及**（理由：領域法律，不重定義 Layer 規格）。覆蓋骨架同靈魂 CS.4 字面具名慣例。

### 跨層逐條標注（RULING-2026-002／§0.5）[N]

登錄重心＝**Layer 4**；下列為各條主要消費／執法層（得跨層；非拆檔）：

| 條 | 標題（短） | 主要 Layer | 備註 |
|---|---|---|---|
| #1 | 零幻像 | L4＋L7（ingestion） | 三基石★ |
| #2 | API 即權威 | L4＋L7 | |
| #3 | 純通用 Ingestion | L7 | |
| #4 | 日為最小單位 | L7 | |
| #5 | 型別紀律 | L7 | |
| #6 | 冪等＋續傳 | L7 | |
| #7 | DB↔API 對帳 | L4＋L7 | supersede（041）；AUD-02 code＝D-PRIN-2 |
| #8 | Anti-Leakage | L4＋L5 | 三基石★ |
| #9 | 思想≠特定值 | L4＋L5 | |
| #10 | 核心股質>量 | L4＋L5 | |
| #11 | 五鏡特徵 | L5 | |
| #12 | SSOT | L4＋L5＋L6 | |
| #13 | 空頭規則地板 | L5＋L7 | |
| #14 | 經濟價值 | L5 | |
| #15 | 誠實回報 | L4＋L6 | 三基石★ |
| #16 | Clean-Room | L6 | |
| #17 | API 速率公民 | L7 | |
| #18 | API-Driven Fetch | L7 | |
| #19 | 可控試錯 | L6＋L7 | |
| #20 | 自驅動×實證 | L6 | |
| as-of／FREEZE 子條 | 完整性判準 | L4（治權參數） | 更新須人拍板入憲 |
