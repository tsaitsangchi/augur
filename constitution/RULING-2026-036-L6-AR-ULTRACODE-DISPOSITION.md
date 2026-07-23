# Augur Steward 裁決第 2026-036 號

**L6（AUGUR-AR v1.2）單層 ultracode findings 處置——EO.1 收 016 謂詞、v1.2 版本锚点同步、DRAFT／TR 历史语 minor×4（合併版 findings：2 medium＋4 minor，同案）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.2`（較嚴格解讀之解消）、`§8.1`（解釋之界線）；findings 冊 `audits/L6-AR-ULTRACODE-20260723.md`；RULING-2026-007（§8.2 已作成、L6.18(b-1) 硬化、T-L6-5 residual 保留）；RULING-2026-016（D13/D15/D17/D22/D28 五增補款 v1.2）；RULING-2026-020（M1 defers-in／M2 幽靈下放甲案收窄）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-035（L5 同體例一攬子）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **登錄**：Amendment Log **AL-2026-040**
* **性質**：minor／patch 執行層施作（第一至七點）；**不動 parent 歸類、不觸 MC、PA／五原則 byte 級零改、AR 版本維持 v1.2**——所涉變更為 [N] EO 完備性／版本自洽補全、[I] DRAFT 殘留／TR 歷史語機械修正
* **分級登錄（Steward 2026-07-23）**：**F-L6-1／2**＝ **medium**（處置採 patch／minor）；**F-L6-3–6**＝ **minor**。零 major；**不動搖 L6 蓋章**（findings 冊結論）

## 一、擬裁一〔Annex EO.1 收 v1.1/v1.2 新增謂詞——F-L6-1，medium〕✅

1. **EO.1 增列 016 五增補對應謂詞**（對齊 L6.9(d)／L6.11 增補／L6.19 增補／L6.21 增補）：
   - 「自然人法規對應表合規」（natural-person-regulatory-table-compliant）——四欄登錄完備、未登錄即不允許（L6.9(d)）；
   - 「核心宇宙 gate 參數採認」（core-universe-gate-parameter-adopted）——gate 門檻值／流動性分位值／產業豁免之採認變更須人類核准留痕（L6.11 增補）；
   - 「Planning 已解析 Identity 引用」（planning-resolved-identity-referenced）——Plan／Goal／Constraint／Capability 指涉世界實體須引用已解析 Identity（L6.19 增補）；
   - 「誠實輸出契約合規」（honest-output-contract-compliant）——產物閉集／硬綁揭露五項／展示分級／fail-closed 四驗證全成立（L6.21 增補）。
2. **定級**：Steward 定級 **medium**（§8.3 掃描—完備性義務；016 增補 [N] 判準已生效卻未收錄→可判定性缺口）。

## 二、擬裁二〔v1.2 生效本版本锚点同步——F-L6-2＋F-L6-6，medium〕✅

1. **§0.1 版本欄**：v1.0 → **v1.2**（前版鏈 v1.1／v1.0 充任記錄保留）。
2. **Annex CS front-matter `spec-version`**：v1.0 → **v1.2**。
3. **CS.4／TR.Z 生效敘事**：與 v1.2 生效本一致（充任 v1.0 歷史保留、現行版本 v1.2）。
4. **【地位】引用格式**：下層依 `AUGUR-L6 v1.2 §{條款}` 引用。
5. **【地位】「变更仅限」**：修正為 v1.0 draft→充任、v1.1（013 D24）、v1.2（016 五增補）之實質升版史實，刪「無 [N] 條款實質變更」不實宣稱。
6. **定級**：Steward 定級 **medium**（[N] 文件内部版本敘事不一致→引用效力不确定）。

## 三、擬裁三〔TR.Z DRAFT 章标——F-L6-3，minor〕✅

1. **TR.Z markdown 章标**：刪「（DRAFT）」——正文已充任認定＋§8.2 已作成。

## 四、擬裁四〔CS.2 T-L6-1…6 DRAFT 殘留——F-L6-4，minor〕✅

1. **CS.2 六列緩解欄**：「DRAFT。」→「已核定（007 §8.2）。」
2. **T-L6-5 例外**：維持 OCV 維度充分性 **residual open-tension** 句（007:43 保留權），不關閉、不翻 major。

## 五、擬裁五〔TR.D D28 物理下放語 stale——F-L6-5，minor〕✅

1. **TR.D D28 列**：「產物表 trigger 級機械強制與閉集枚舉登錄」改述為「DB 機械強制（trigger 級）俟 L7 §8.2（020 M2 甲案收窄）」——與 L6.21 正文一致。

## 六、擬裁六〔【地位】变更仅限不實——F-L6-6，minor〕✅

1. **併入擬裁二**——【地位】升版史實與引用格式同案 patch。

## 七、T-L6-5 與 007 residual

1. **T-L6-5 OCV 維度充分性**：**維持 open-tension**（RULING-2026-007:43 保留權）；本裁決**不關閉**、不翻 major、不重開 §8.2。

## 八、明示不為

* 不動 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.1`／`AUGUR-L5 v1.0` 任何條文；不動 MC；PA／五原則 byte 級零改。
* L7 仍引 `AUGUR-L6 v1.0` 之 cross-layer stale——**不併本案**、留 L7 ultracode 议程。
* L6→L7 runtime 物理面是否真满足 L6.21 fail-closed——**不併本案**（执行层稽核，L7 provisional）。

## 九、驗證

* `python3 -m tools.constitution_lint report`：PASS 不退轉。
* `ULTRACODE-SCHEDULE.md` L6 列更新＋Amendment Log 登錄 AL-2026-040 於簽核生效時一併辦理。

## 十、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/AGENT-RUNTIME-SPECIFICATION.md` | F-L6-1～6 全覆蓋：EO.1 四謂詞；§0.1／CS spec-version／CS.4／TR.Z；【地位】v1.2 引用＋升版史實；CS.2 DRAFT→已核定（T-L6-5 residual 保留）；TR.D D28 020 M2 語 |
| `constitution/RULING-2026-036-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-040 |
| `ULTRACODE-SCHEDULE.md` | L6 列閉環 |
| `audits/L6-AR-ULTRACODE-20260723.md` | 呈核段更新 |

## 十一、獨立對抗核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 後**須經非施作者**確認之核驗清單。**獨立對抗核驗待辦**（另輪；非本 commit 施作者）。

| # | 核驗項 | 範圍 | 狀態 |
|---|---|---|---|
| 1 | **EO.1 016 謂詞**：自然人法規表／核心宇宙 gate／Planning 引用／誠實輸出四驗證已收錄 | EO.1 | ⏳ 待獨立核驗 |
| 2 | **v1.2 版本锚点**：§0.1／CS spec-version／CS.4／TR.Z／【地位】引用一致 v1.2 | §0.1、CS、TR.Z、【地位】 | ⏳ 待獨立核驗 |
| 3 | **TR.Z 無 DRAFT 章标** | TR.Z | ⏳ 待獨立核驗 |
| 4 | **CS.2 T-L6-1…6**：無裸 DRAFT、已核定（007 §8.2） | CS.2 | ⏳ 待獨立核驗 |
| 5 | **T-L6-5 仍 open**：OCV 維度充分性 residual 保留、未關閉 | CS.2 T-L6-5 | ⏳ 待獨立核驗 |
| 6 | **TR.D D28 語**：與 L6.21／020 M2 一致、無 trigger 級已下放误导 | TR.D | ⏳ 待獨立核驗 |
| 7 | **020／016／007 已癒合项**：四處「或」硬锁、OCV 反 Goodhart、b-1 定義窄化仍稳 | L6.10–18 | ⏳ 待獨立核驗 |
| 8 | **[N] 零逾越**：diff 限本裁決核示之 patch | AR 全 diff | ⏳ 待獨立核驗 |
| 9 | **lint 基線**：`python3 -m tools.constitution_lint report` error 0／warning 0 | 全 corpus | ⏳ 待獨立核驗 |
| 10 | **PA／五原則 byte 零改** | `constitution/` 五原則檔 | ⏳ 待獨立核驗 |
| 11 | **蓋章不動搖**：零 major、AR v1.2 維持 | 全案 | ⏳ 待獨立核驗 |

**Steward 2026-07-23：**接受 L6 ultracode 呈核、同案 036**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；F-L6-1 EO.1 收 016 謂詞；F-L6-2 v1.2 版本锚点同步；F-L6-3–6 同案機械施作；T-L6-5 維持 007 residual open-tension）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-L6-1／2＝medium；F-L6-3–6＝minor；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 L6 ultracode 呈核、同案 036**）。L6 ultracode 處置施作完成；蓋章不動搖。第十一節獨立對抗核驗待另輪（028 §3）。*
