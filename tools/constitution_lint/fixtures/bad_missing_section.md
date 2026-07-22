# Fixture：本文缺原則節（red）

本檔為 compliance_lint selftest 之**反例③**：front-matter 完整，但本文**缺 P3 論證節**（七節不齊）→
WM.41 error。

```
compliance-statement:
  spec: Fixture Missing Section Spec
  spec-version: v0.1
  layer: 4
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
  archive-path: tools/constitution_lint/fixtures/bad_missing_section.md
```

## PA
* 所引條款：`AUGUR-MC v1.3 §1.1`。合規模式：滿足。論證：略。判準揭示：無。

## P1
* 所引條款：`AUGUR-MC v1.3 §P1.E1`。合規模式：滿足。論證：略。判準揭示：無。

## P2
* 所引條款：`AUGUR-MC v1.3 §P2.E1`。合規模式：滿足。論證：略。判準揭示：無。

（**故意缺 P3 節**——反例③聚焦 WM.41 七節不齊）

## P4
* 所引條款：`AUGUR-MC v1.3 §P4.E1`。合規模式：滿足。論證：略。判準揭示：無。

## P5
* 所引條款：`AUGUR-MC v1.3 §P5.E1`。合規模式：不適用（附理由）。論證：略。判準揭示：無。

## §4 canonical chain
* 所引條款：`AUGUR-MC v1.3 §4`。合規模式：滿足。論證：略。判準揭示：無。

## 已知緊張關係
none
