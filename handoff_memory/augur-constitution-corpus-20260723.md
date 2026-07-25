---
name: augur-constitution-corpus-20260723
description: "2026-07-23 monorepo 憲章 corpus 已入本倉：L0 AUGUR-MC v1.6＋L1–L7 生效規格＋領域治權；統一入口 GOVERNANCE-MAP；#7↔P4.E5 規範已閉（RULING-041）；2026-10-14 日曆項勿假關"
metadata:
  node_type: memory
  type: project
---

# Augur 憲章 corpus（本機會話已讀 · 2026-07-23）

## 統一入口（先讀）

* SSOT 導航＝`constitution/GOVERNANCE-MAP.md`（[I]；**不創設義務**；docs **不上收** L0）
* 義務查找序：MC [N] → 生效 Layer 規格 [N] → 領域檔現行義務句 → 地圖/HANDOFF 僅導航
* **禁止雙寫**；衝突時下層牴觸 MC 之部分無效（§0.6）

## L0 — AUGUR-MC v1.6（`constitution/META-CONSTITUTION.md`）

* 生效 2026-07-23；母集 102＝97 [N]＋5 [I] WHY（RULING-040）
* **PA（永恆）**：faithfully represent reality through persistent identity and traceable evidence → trustworthy intelligence
* **五原則**：P1 Reality First｜P2 Representation Before Intelligence｜P3 Identity Before Knowledge｜P4 Evidence Before Conclusion｜P5 Accountability Before Action
* **標準鏈 EV.1–12**：Reality→Observation→Representation→Identity→Evidence→Knowledge→Reasoning→Planning→Human Authority Gate→Action→Feedback→Learning（雙迴路：因果＝Action 改 Reality；認知＝Learning 只改表徵且仍走 Evidence 通道）
* **禁模式 F1–F6**：Data/Model/Agent First；Knowledge Without Identity；Intelligence Without Evidence；Unaccountable Action
* **關鍵 ENFORCE**：P4.E3 只失效不刪除；**P4.E5 禁 last-write-wins／矛盾共存**；P4.E7 信任不可洗白；P5.W2/W5＋P4.E1/E6＝§8.4 不可豁免核心
* **治理**：Sole Steward＝人類；Agent 不得參與修憲／解釋；§8.1「解釋之界線」（v1.5）；引用格式 `AUGUR-MC v{ver} §{id}`
* Appendix A 選型 [I]：PG／Neo4j／Vector／自研 L5/L6／MCP

## L1–L7 規格（`specs/*-SPECIFICATION.md`；現行正式檔非 *-draft）

| Layer | 縮寫 | 版本 | 充任／狀態 |
|---|---|---|---|
| L1 WM | AUGUR-WM | v1.0 | RULING-002 |
| L2 ONT | AUGUR-ONT | v1.0 | RULING-003 |
| L3 ID | AUGUR-ID | v1.0 | RULING-004 |
| L4 KS | AUGUR-KS | **v1.1** | RULING-005＋016 |
| L5 CK | AUGUR-L5 | v1.0 | 029 條件通過、provisional 解除 |
| L6 AR | AUGUR-L6 | **v1.2** | RULING-007＋013＋016；人類權威落地 |
| L7 INF | AUGUR-L7 | v1.0 | RULING-011；025 §8.2 條件通過 |

* 規格檔頭常仍寫「受 MC v1.4」——簿記／引用版；**現行 lex superior 文本＝MC v1.6**（GOVERNANCE-MAP）
* §0.6(b)：概念層 L1–4 **不得**用 L5–7 構件當定義依據
* lint：`python3 -m tools.constitution_lint report`

## 領域治權（義務住原檔；§0.5 登錄）

| 檔 | Layer | 現行版 |
|---|---|---|
| `docs/系統核心思想_v1.8.0.md` | L1 前身 | 靈魂：真兆／相對強弱＋方向機率軸；三敵；Source-Pure；系統建議人決策 |
| `docs/原則精華_v1.10.0.md` | L4（跨層） | 20 條；★#1/#8/#15；**#7 已改條對齊 P4.E3/E5**（RULING-041；AUD-02 code 仍受閘） |
| `docs/系統架構大憲章_v1.46.0.md` | L7 | 管線×三敵、12-PHASE、計畫先行 |
| `CLAUDE.md` | L6 | AI 工具規則；執行指令矩陣（RULING-026） |
| `docs/compliance/CS-*.md` | — | 五檔合規聲明已存（P2／2026-07-23；mc-version＝v1.6） |

## 領域靈魂濃縮（產品面）

* 一句話：只用真實資料、誠實預測台股
* 三敵：假資料／偷看未來／自我欺騙 → Source-Pure／Anti-Leakage／誠實
* 北極星：「真兆還是假兆？」（API 來源 × as-of 可見 × OOS 撐住）
* live：解凍後增量；確立級宣稱須 `direction_gate`；arena G1-G5；歷史 as-of 完整性釘 2026-05-31
* clean-room：禁 stock_backend code 回流

## 裁決／修訂索引

* RULING：`constitution/RULING-2026-002`…`041`
* 日誌：`constitution/AMENDMENT-LOG.md`
* 近期閉合：041＝#7↔P4.E5 規範緊張；040＝MC v1.6 最小；039＝L0–L7 residual omnibus（**2026-10-14 殘留勿假關**）
* 交接：`HANDOFF.md`／`HANDOFF-governance.md`（後者部分數字為 lint 標記／較舊敘事，**版本以 GOVERNANCE-MAP＋META 為準**）

## How to apply

改判準／升版／合規宣稱 → 先對 MC [N] 與對應 Layer；判準變更＝Steward 事項。查義務勿只信 handoff 轉述——**原文在 monorepo `constitution/`＋`specs/`**。關聯 [[augur-mc-upper-governance]] [[augur-project-map]]。
