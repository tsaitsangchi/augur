# Fixture：front-matter scalar 空值（red）

反例⑤（MUST-FIX B 回歸鎖）：front-matter 欄位齊全但 `spec-version`/`mc-version`/`date` 值留空 →
WM.40 空值 error（缺載視同無聲明），且空 mc-version 不得逃過版本檢查。

```
compliance-statement:
  spec: Fixture Empty Value Spec
  spec-version:
  layer: 2
  mc-version:
  upper-specs: [AUGUR-WM v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: none
  defers-in: []
  defers-out: []
  date:
  author: fixture
  archive-path: tools/constitution_lint/fixtures/bad_empty_value.md
```

## PA
* 所引條款：`AUGUR-MC v1.3 §1.1`。合規模式：滿足。論證：略但足量文句以過本文檢查。判準揭示：無。

## P1
* 所引條款：`AUGUR-MC v1.3 §P1.E1`。合規模式：滿足。論證：略但足量文句以過本文檢查。判準揭示：無。

## P2
* 所引條款：`AUGUR-MC v1.3 §P2.E1`。合規模式：滿足。論證：略但足量文句以過本文檢查。判準揭示：無。

## P3
* 所引條款：`AUGUR-MC v1.3 §P3.E1`。合規模式：DEFER。論證：略但足量文句以過本文檢查。判準揭示：無。

## P4
* 所引條款：`AUGUR-MC v1.3 §P4.E1`。合規模式：承接。論證：略但足量文句以過本文檢查。判準揭示：無。

## P5
* 所引條款：`AUGUR-MC v1.3 §P5.E1`。合規模式：不適用。論證：略但足量文句以過本文檢查。判準揭示：無。

## §4 canonical chain
* 所引條款：`AUGUR-MC v1.3 §4`。合規模式：滿足。論證：略但足量文句以過本文檢查。判準揭示：無。

## 已知緊張關係
none
