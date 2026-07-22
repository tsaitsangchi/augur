# Fixture：附錄巧合標題遮蔽真缺節（red）

反例④（MUST-FIX A 回歸鎖）：本文**真缺 P3 論證節**，但尾端有一個含 `P3` token 的附錄背景標題。
舊版�pytest偵測會被該附錄遮蔽而誤綠；順序檢查（P3 首見於 EV-chain 之後→非單調）使其正確判紅。

```
compliance-statement:
  spec: Fixture Appendix Mask Spec
  spec-version: v0.1
  layer: 3
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
  archive-path: tools/constitution_lint/fixtures/bad_appendix_mask.md
```

## PA
* 所引條款：`AUGUR-MC v1.3 §1.1`。合規模式：滿足。論證：測試世界忠實表徵之論證文句足量。判準揭示：無評價謂詞。

## P1
* 所引條款：`AUGUR-MC v1.3 §P1.E1`。合規模式：滿足。論證：測試世界優先之論證文句足量。判準揭示：無評價謂詞。

## P2
* 所引條款：`AUGUR-MC v1.3 §P2.E1`。合規模式：滿足。論證：表徵先於智慧之論證文句足量。判準揭示：無評價謂詞。

（**故意缺 P3 論證節**）

## P4
* 所引條款：`AUGUR-MC v1.3 §P4.E1`。合規模式：承接。論證：證據先於結論之論證文句足量。判準揭示：無評價謂詞。

## P5
* 所引條款：`AUGUR-MC v1.3 §P5.E1`。合規模式：不適用（附理由）。論證：無行動面之論證文句足量。判準揭示：無評價謂詞。

## §4 canonical chain
* 所引條款：`AUGUR-MC v1.3 §4`。合規模式：滿足。論證：承接演化鏈之論證文句足量。判準揭示：無評價謂詞。

## 已知緊張關係
none

## 附錄 X：P3 相關背景資料
（此為巧合含 P3 token 之背景標題，不應被認作 P3 論證節。）
