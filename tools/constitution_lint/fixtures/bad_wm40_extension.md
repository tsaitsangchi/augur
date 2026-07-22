# Fixture：WM.40 front-matter 擴欄（red）

本檔為 WM.40 閉集擴欄之**反例**：14 欄全在（存在性檢查全綠），但另增 `defers-in-count`
與 `reviewer` 二欄 → 應 FAIL。

聲明格式之定義權由 `AUGUR-MC §8.3` 授予 Layer 1；下層規格自行擴欄即以末層之作為擴充
Layer 1 之格式定義，違 `§0.6(a)` lex superior。**存在性檢查抓不到此類缺陷**——欄位全在，
只是多了不該有的。

```
compliance-statement:
  spec: Fixture Extension Spec
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
  archive-path: tools/constitution_lint/fixtures/bad_wm40_extension.md
  defers-in-count: 0
  reviewer: nobody
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

