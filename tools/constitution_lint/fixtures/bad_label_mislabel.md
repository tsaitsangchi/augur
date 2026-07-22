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

### TR.B — 截半名列（B2：裸英文名之子字串放行漏洞，全部應紅）

「裸英文名為標籤之子字串即放行」之後果：起草者引原文半名、另半代以自己的話，
被截除之面即靜默落空——`P4.E8` 之「消費」面正是下層之義務所在。

| MC 條款 | 落點／處置 | 模式 |
|---|---|---|
| `P4.E8`（Confidence 單一形式化） | FX.6 | 承接（原文＝`Confidence（語義與消費）`；「消費」面遭截除） |
| `P4.E2`（Time 單向時鐘） | FX.7 | 承接（原文＝`Time（雙時間性）`；「雙時間性」代以自創詞） |

### TR.C — 上層規格誤標列（B5：過半矩陣首度受檢，應紅）

| 上層條款 | 落點／處置 | 模式 |
|---|---|---|
| `WM.36`（World Concept Registry 七欄） | FX.8 | 細化（原文＝`World Concept Registry 與消費規則`；「消費規則」面遭截除） |

### TR.D — 判準四大赦列（原文名在場者不得以「正文有支撐」放行，全部應紅）

前版對**全部**條款跑 `_text_supported`，`ok` 即放行，致判準四成為判準一之無條件大赦：條款正文
本就富含該條用語，故「詞元半數命中正文」幾近恆真，縱標籤與原文括號名全然不符亦綠。下列各列
之標籤詞元均**大量命中正文**，卻無一引用原文括號名。

| MC 條款 | 落點／處置 | 模式 |
|---|---|---|
| `P1.E1`（Reality 最高抽象／來源非最高抽象） | FX.9 | 承接（原文＝`開放來源`；判準四大赦之實證漏網例） |
| `P4.E1`（五元組最低不變式） | FX.10 | 承接（原文＝`Knowledge 五元組`；「Knowledge」遭捨、代以正文用語「最低不變式」） |
| `P4.E2`（雙時間、as-of 重建） | FX.11 | 承接（原文＝`Time（雙時間性）`；兩半皆未逐字引用，代以自撰片段） |

### TR.E — 重複詞灌分列（詞元去重前可推過閾值，應紅）

`label_overlap` 前版以詞元**清單**計數，故重複一個命中詞即同時墊高分子：`禁插補冒充` 加
`Representation` ×4 → 4/8 ＝ 50%，恰跨過閾值而放行，誤標之標籤原封不動。去重後恆為 1/5 ＝ 20%。

| MC 條款 | 落點／處置 | 模式 |
|---|---|---|
| `P2.E4`（禁插補冒充 Representation Representation Representation Representation） | FX.12 | 承接（灌分後仍須紅） |

### TR.F — 代號脫檢列（弄壞代號不得比修好標籤容易）

前版 `clause is None → continue` 靜默略過：把紅牌列之代號改寫為不存在之代號，即可令該列
連同其誤標一併消失於輸出。代號合憲章編號形態而不在 [N] 條款宇宙者＝誤植或杜撰 → error；
前綴屬已知規格但未列於 `upper-specs` 者 → warning。

**注意（殘留缺口，非本列所能鎖）**：`P9.E9` 這類**連代號形態都不合**者（`ANY_CODE_ALT` 僅容
`P[1-5]`），於更上游之 `_row_code_labels` 即遭捨棄，**根本到不了** `clause is None` 分支，故
本節之鎖攔不到它。此缺口仍在，見 README 之「已知邊界」。下列採 `P5.E9`（形態合致、不在宇宙）
方能實測本分支。

| 條款 | 落點／處置 | 模式 |
|---|---|---|
| `P5.E9`（禁插補冒充） | FX.13 | 承接（代號形態合致但不在 MC [N] 條款宇宙 → error） |
| `KS.1`（知識系統條款） | FX.14 | 承接（前綴已知但未列於 upper-specs → warning） |
