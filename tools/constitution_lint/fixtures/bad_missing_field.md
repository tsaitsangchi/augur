# Fixture：front-matter 缺欄位（red）

本檔為 compliance_lint selftest 之**反例②**：front-matter 缺 `waivers` 與 `open-tensions` 欄 →
WM.40 error（缺欄視同無聲明）。

```
compliance-statement:
  spec: Fixture Missing Field Spec
  spec-version: v0.1
  layer: 3
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  defers-in: []
  defers-out: []
  date: 2026-07-17
  author: fixture
  archive-path: tools/constitution_lint/fixtures/bad_missing_field.md
```

## PA
* 所引條款：`AUGUR-MC v1.3 §1.1`。合規模式：滿足。論證：略。判準揭示：無。

（其餘從略——本反例聚焦 front-matter 缺欄）
