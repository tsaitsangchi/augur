# Fixture：Annex TR 標籤正確（green）

本檔為 WM.44-LABEL 之**正例**：Annex TR 之標籤或引用憲章自有標籤（`P1.E1`（開放來源）、
`F4`（Knowledge Without Identity）），或為條款正文之逐字濃縮（`P4.E1`（五元組最低不變式）），
或僅列代號而不加標籤（合法，不罰）→ 應 PASS。

本 fixture 同時鎖住三類**不得誤紅**之合法體例，防檢查過嚴反噬。

```
compliance-statement:
  spec: Fixture Good Label Spec
  spec-version: v1.0
  layer: 7
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: none
  defers-in: []
  defers-out: []
  date: 2026-07-17
  author: fixture
  archive-path: tools/constitution_lint/fixtures/good_label_ok.md
```

## PA（Prime Axiom）
* 所引條款：`AUGUR-MC v1.3 §1.1`。
* 合規模式：滿足。
* 論證：本 fixture 忠實表徵測試世界。
* 判準揭示：不使用自創評價謂詞。

## P1（Reality First）
* 所引條款：`AUGUR-MC v1.3 §P1.E1`。
* 合規模式：滿足。
* 論證：測試世界優先。
* 判準揭示：無評價謂詞。

## P2（Representation Before Intelligence）
* 所引條款：`AUGUR-MC v1.3 §P2.E1`。
* 合規模式：滿足。
* 論證：表徵先於智慧。
* 判準揭示：無評價謂詞。

## P3（Identity Before Knowledge）
* 所引條款：`AUGUR-MC v1.3 §P3.E1`。
* 合規模式：DEFER。
* 論證：下放 Layer 3。
* 判準揭示：無評價謂詞。

## P4（Evidence Before Conclusion）
* 所引條款：`AUGUR-MC v1.3 §P4.E1`。
* 合規模式：承接。
* 論證：證據先於結論。
* 判準揭示：無評價謂詞。

## P5（Accountability Before Action）
* 所引條款：`AUGUR-MC v1.3 §P5.E1`。
* 合規模式：不適用（附理由：本 fixture 無 Action）。
* 論證：無行動面。
* 判準揭示：無評價謂詞。

## §4 canonical chain（EV-chain）
* 所引條款：`AUGUR-MC v1.3 §4`。
* 合規模式：滿足。
* 論證：承接 EV.1–EV.12 演化鏈。
* 判準揭示：無評價謂詞。

## 已知緊張關係
none

## Annex TR [N] — WM.44 逐條對應矩陣

### TR.A — 合法標籤列（全部應綠）

| MC 條款 | 落點／處置 | 模式 |
|---|---|---|
| `§3`（Five Immutable Principles） | FX.1 | 承接 |
| `§3`（五大不可違反原則） | FX.1 | 承接 |
| `P1.E1`（開放來源） | FX.2 | 承接 |
| `P3.E3`（同一性判準掛鉤） | FX.3 | 承接 |
| `F4`（**Knowledge Without Identity**） | FX.4 | 承接 |
| `F5`（Intelligence Without Evidence） | FX.5 | 承接 |
| `P4.E1`（Knowledge 五元組） | FX.6 | 承接（原文括號名整體在場 → 綠） |
| `P4.E2`（雙時間性） | FX.7 | 承接（B2 正例：擇一引用半名、未添附自撰片段 → 綠） |
| `§P5.W2`（授權鏈根為人類權威、隨時否決／暫停／中止）**〔核心〕** | FX.8 | 承接（附加限定語不構成誤標） |
| `P5.E2`（行動風險分級） | FX.9 | 細化（含憲章原文「風險分級」） |
| `EV.9`（Human Authority Gate） | FX.10 | 承接 |
| `P2.E1`／`P2.E2`／`P2.E3` | FX.11 | 承接（僅列代號、無標籤 → 不罰） |
| `P4.E8`（Confidence（語義與消費）） | FX.13 | 承接（B2 正例：括號名整體現於標籤 → 綠） |
| `P4.E8`（語義與消費） | FX.14 | 承接（B2 正例：擇一引用半名、未添附自撰片段 → 綠） |
| `§2.5`（Evidence） | FX.15 | 承接（B3：§2 定義項進入宇宙後仍不得誤紅合法引用） |
| `§2.10`（Confidence 之可量化表述） | FX.16 | 承接（B3：定義項括號名整體在場 → 綠） |
| `WM.36`（World Concept Registry 與消費規則） | FX.17 | 承接（B5 正例：上層規格原文標籤 → 綠） |
| `WM.4`（刪名測試） | FX.18 | 承接（純節引正例：標籤為原文名「概念層獨立性＋刪名測試」之逐字子字串、無自撰片段 → 綠） |
| `ID.30(c)` | FX.19 | 承接（項次交叉引註，非標籤宣稱 → 不罰） |
