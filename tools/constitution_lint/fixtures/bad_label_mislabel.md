# Fixture：Annex TR 憲章誤標（red）

本檔為 WM.44-LABEL 之**反例**：front-matter／七節／緊張節全齊（既有檢查全綠），
但 Annex TR 之條款標籤係起草者憑記憶轉述、或自創詞反充作上位標籤 → 應 FAIL。

此即「linter 綠燈但實質錯誤」之病灶本體：代號都在（WM.44 覆蓋通過），標籤卻不是憲章的話。

```
compliance-statement:
  spec: Fixture Mislabel Spec
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
  archive-path: tools/constitution_lint/fixtures/bad_label_mislabel.md
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

### TR.A — 誤標列（全部應紅）

| MC 條款 | 落點／處置 | 模式 |
|---|---|---|
| `§3`（公理金字塔／演化鏈總述） | FX.1 | 承接 |
| `P1.E1`（Reality 為唯一權威來源） | FX.2 | 承接 |
| `P2.E4`（禁插補冒充） | FX.3 | 承接 |
| `P3.E3`（identity claim 之 Evidence 要求） | 不觸及＋理由：屬 L3／L4 語義 | 不觸及 |
| `F4`（Automation First） | FX.4 | 承接 |
| `F5`（Answer First） | FX.5 | 承接 |
