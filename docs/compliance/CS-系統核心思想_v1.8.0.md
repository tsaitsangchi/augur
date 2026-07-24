# Constitutional Compliance Statement — 系統核心思想 v1.8.0

* **性質**：領域治權檔之 Constitutional Compliance Statement（[N] 聲明文件；非把本檔正文上收為 Layer 0／非實質併憲）
* **依據**：`AUGUR-MC v1.6 §8.3`；`AUGUR-WM v1.0 §WM.39–45`（§11 正式格式）；RULING-2026-002 主文二（五檔補正；期限至 **2026-10-14**）
* **登錄 Layer**：1（World Model 領域前身；`AUGUR-WM v1.0 §WM.6`：[I] 引註，**非**定義依據）
* **正文 SSOT**：`docs/系統核心思想_v1.8.0.md`
* **誠實界限**：本聲明履行 RULING-2026-002 主文二之**本檔**補正義務；**不**假關 RULING-2026-039 殘留或其他 2026-10-14 日曆項。

```
compliance-statement:
  spec: Augur Domain Soul（系統核心思想）
  spec-version: v1.8.0
  layer: 1
  mc-version: AUGUR-MC v1.6
  upper-specs: []
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: []
  defers-in: []
  defers-out: [D-SOUL-1]
  date: 2026-07-23
  author: Steward 授權執行層（P2；計畫 reports/augur_docs_into_mc_initial_constitution_plan_20260723.md）
  archive-path: docs/compliance/CS-系統核心思想_v1.8.0.md
```

## CS.1 逐原則論證（七節）[N]

> **CS.1-PA**〔細化〕
> 引 `AUGUR-MC v1.6 §1.1`、`§P5.D`。靈魂敘事錨定「只讀真兆、可修正錯誤、不確定性須可追溯」——與 PA 三性同向。合規模式＝細化（領域敘事）。判準揭示：「真兆」＝有真實 API／DB／程式輸出來源（原則精華 #1／#15）；本檔不另立評價謂詞而不附判準。

> **CS.1-P1**〔細化＋不觸及〕
> 引 `§P1.E1`–`§P1.E3`、`§2.1`。Reality＝市場／API 觀測；系統只讀、不造 Reality。自然人／法規對應面屬 Layer 規格落點，本檔不觸及。判準揭示：無 API 來源之值不得入庫（對映原則精華 #1）。

> **CS.1-P2**〔細化〕
> 引 `§P2.E1`、`§P2.E4`、`§P2.W1`。表徵（特徵／分數／機率）不得被誤稱為 Reality；「不是造假兆」＝Representation 紀律之領域敘事。判準揭示：產物須標為預測／機率／分數，不得宣稱已實現世界事實。

> **CS.1-P3**〔不適用〕
> 引 `§P3.E1`。Identity 解析屬 AUGUR-ID／L6；本檔為 WHAT／WHY 敘事，不定義 Identity 型別。理由：義務落點在 L3／L6 規格。

> **CS.1-P4**〔細化〕
> 引 `§P4.E1`、`§P4.E2`、`§P4.E6`、`§P4.W1`。三敵人（假資料／偷看未來／自我欺騙）＝ Evidence／anti-leakage／誠實回報之領域敘事對映；輸出契約三產物須經可證偽 GATE。判準揭示：未過 GATE 不得宣稱產品輸出（正文輸出契約鎖；細節 SSOT＝領域大憲章／原則精華）。

> **CS.1-P5**〔細化〕
> 引 `§P5.W2`、`§P5.W5`。「系統建議、人決策」＝人類權威根；AI 為有紀律顧問。**顧問≠禁閘內自動晉升**；**不是自動駕駛**＝禁改治權判準／禁自動下單／人得緊急停（PME-AUTO-B；G-PME-SOUL closed；P5.W5 §8.1 認定見 `audits/G-PME-SOUL-CLOSED-20260724.md`）。判準揭示：治權判準與閘閾值變更須人拍板（對映 CLAUDE #26／原則 #20）。

> **CS.1-EV-chain**〔細化＋不觸及〕
> 引 `AUGUR-MC v1.6 §4` EV.1–EV.12。本檔敘事涵蓋觀測→表徵→預測→驗證之領域意圖；節點形式定義與 Action 迴路屬 Layer 規格。判準揭示：不跳過「可證偽驗證」宣稱產品（對映 EV.11／誠實鎖）。

## CS.2 已知緊張關係 [N]

`none`（open-tensions: []）。本檔與 MC 無已登錄未解緊張。豁免：`none`（waivers: []）。

## CS.3 雙向 DEFER 表 [N]

* **(a) defers-in**：`[]`——本檔為領域前身敘事，不承接 WM Annex D 掛鉤（WM 為正式 L1）。
* **(b) defers-out**：
  | d-id | 本檔事項 | 目標 | 說明 |
  |---|---|---|---|
  | D-SOUL-1 | 世界模型形式定義／權威三分 | Layer 1 `AUGUR-WM` | 規範承接以 WM／Annex A 為準（WM.6） |

## CS.4 形式充分性（WM.44）[N]

本檔**非** Layer 規格正文；MC 全部 [N] 之機器可執落點以已生效 `specs/*-SPECIFICATION.md` 為權威。本聲明就本檔實際觸及者論證如上；其餘 MC [N] 一律 **不觸及**，理由＝「義務落點在已生效 Layer 規格；本檔僅領域 WHAT／WHY，不重定義」。

**MC [N] 覆蓋骨架（字面具名；語意以 CS.1 為準）**：PA；P1–P5 家族；EV.1–EV.12；F1–F6；§0–§8——本檔觸及者見 CS.1；其餘＝不觸及＋上開理由。Pn.Y＝[I]，不觸及。

**跨層標注**：本檔整體登錄 **Layer 1**；無跨層條款需逐條改標（內容為靈魂敘事，不設 Layer 4–7 義務句）。
