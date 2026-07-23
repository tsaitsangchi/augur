# Augur Steward 裁決第 2026-032 號

**L2（AUGUR-ONT v1.0）單層 ultracode findings 處置——T.28 矛盾句統一措辭＋CS.8 OT-5 揭露、TR.2 機械析出改標、T.6 判準補實質要素（合併版 findings：1 medium＋3 minor，同案）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.2`（較嚴格解讀之解消）、`§8.1`（解釋之界線，v1.5）；findings 冊 `audits/L2-ONT-ULTRACODE-20260723.md`；RULING-2026-021（CS.10／TR.2 補列先例）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-030（L1 同體例一攬子）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **登錄**：Amendment Log **AL-2026-036**
* **性質**：minor／patch 執行層施作（第一至三點）；**不動 parent 歸類、不觸 MC、PA／五原則 byte 級零改、ONT 版本維持 v1.0**——所涉變更為 [N] 判準句措辭統一、CS.8 揭露增列、TR.2 [I] 矩陣標記更正、T.6 判準補實質要素（邊緣 minor，Steward 定級 minor）
* **分級登錄（Steward 2026-07-23）**：**F-L2-1**＝ **medium**（處置採甲案 patch／minor）；**F-L2-2／3／4**＝ **minor**。零 major；**不動搖 L2 蓋章**（findings 冊結論）

## 一、擬裁一〔T.28 GATE 歸類揭露＋矛盾句——F-L2-1，medium〕（甲案）✅

採 findings 冊建議**甲案**（**不採乙案**——GATE 不析出改 parent DynamicEntity）：

1. **T.28 判準句改寫**：刪除同條內「GATE…為…DynamicEntity」與 parent 句「非第二 parent」之字面衝突；統一為「GATE 兼具 DynamicEntity 之生命週期／審批狀態面向，**以屬性表徵，非第二 parent**」之體例（比照 T.5／T.35）。
2. **parent 維持 AgentiveEntity**——本裁決不變更 GATE 之 parent 歸類；`§A.19` [N]「一級 Dynamic Entity」與本層重分類之偏離，依 OT-1 先例以 CS.8 揭露處置，非以改 parent 消弭。
3. **CS.8 增 OT-5**：揭露 GATE（及 CoreUniverse 歸 Agentive 之論證缺口）對 `AUGUR-WM v1.0 §A.19`／`§A.14` 之 Layer 2 重分類偏離；front-matter `open-tensions` 同步增列 OT-5。
4. RULING-2026-028 第 1 點（v1.5 §8.1 解釋之界線）自檢：本處置為**措辭統一＋如實揭露**——不課新類型義務、不解鎖、不除制衡；(a)(b)(c) 均不該當，得以 patch 為之。

## 二、擬裁二〔TR.2 機械析出改標——F-L2-2／3，minor〕✅

同案 [I] 矩陣機械施作（零 [N] 義務變更）：

1. **F-L2-2（WM.53）**：自 TR.2「WM.49–WM.53｜不觸及」列**析出** `WM.53` 獨列——模式改為「**承接（【地位】節準用 `§WM.53`）**」；WM.49–WM.52 維持原「不觸及＋Domain Profile 框架」理由。
2. **F-L2-3（Annex A 區塊）**：自「Annex A（A.0–A.59）→逐條型別化」共享標記**析出分列**——①部封閉集（A.0–A.30、A.57、A.58）維持「逐條型別化／細化」；A.31–A.32→封印素材（ONT.20–21）；A.33→ONT.22（DI 節已承接 [N]）；A.34–A.44→不觸及（時間／通道宣告）；A.45–A.53→不觸及（⑤部評價性謂詞）；A.54→T.90；A.55–A.56／A.59→不觸及（非①部型別化對象，依條款異質處置）。

## 三、擬裁三〔T.6 判準補實質要素——F-L2-4，minor〕✅

1. **T.6 ForeignSecurity 判準句**：由「同一 iff〔外部識別體系…之 identity claim〕」之機制迴指，改為獨立可判定條件式——**同一 iff〔外部識別碼體系（如 ISIN／exchange ticker）× 代碼值 × 有效期間〕**；跨體系同一仍以 identity claim（ONT.22）表達，判準採認 DEFER Layer 3（DO.1），與 T.1 體例對齊。
2. **定級**：Steward 定級 **minor**（判準內容補實質要素、邊緣 ONT.60；封印保守預設（ONT.21）已擋住消費實害；非 parent 變更、非型別體系骨架變更）。

## 四、明示不為

* 不採 F-L2-1 **乙案**（GATE 析出改 parent DynamicEntity）——本裁決不觸 T.28 parent。
* 不動 `AUGUR-WM v1.0` 任何條文；不動 MC；PA／五原則 byte 級零改。
* 不重新裁決 CS.10 形式充分性（RULING-2026-021 已結）；本案僅 TR.2 標記更正，不改 CS.10 狀態陳述。
* L3–L7 各層 ultracode 不併本案。

## 五、驗證

* `python3 -m tools.constitution_lint report`：PASS 不退轉。
* `ULTRACODE-SCHEDULE.md` L2 列更新＋Amendment Log 登錄 AL-2026-036 於簽核生效時一併辦理。

## 六、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/ONTOLOGY-SPECIFICATION.md` | T.28 矛盾句統一＋OT-5 引註；CS.8 OT-5 增列；front-matter `open-tensions` 增 OT-5；TR.2 WM.53 析出＋Annex A 分列；T.6 判準補實質三要素 |
| `constitution/RULING-2026-032-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-036 |
| `ULTRACODE-SCHEDULE.md` | L2 列閉環 |
| `audits/L2-ONT-ULTRACODE-20260723.md` | 呈核段更新 |

## 七、待獨立核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 前**須經非施作者**確認之核驗清單。**獨立對抗核驗已完成**（2026-07-23；核驗者＝Cursor 獨立核驗 agent；方法＝逐項檔案原文／`git show 369cdef`／親跑 lint；非施作者 a8a425f5）。

| # | 核驗項 | 範圍 | 狀態 |
|---|---|---|---|
| 1 | **T.28 矛盾解消**：判準句無「為…DynamicEntity」與「非第二 parent」同條衝突；parent 仍 AgentiveEntity | T.28 | ✅ 獨立核驗 PASS（2026-07-23；`:317` 原文＋矛盾句 grep 零命中） |
| 2 | **OT-5 揭露完備**：GATE／CoreUniverse 偏離 §A.19／§A.14 已如實記載；front-matter 與 CS.8 一致 | CS.8、front-matter | ✅ 獨立核驗 PASS（2026-07-23；`:513`／`:581` 一致） |
| 3 | **TR.2 WM.53**：自 WM.49–52 列析出、改標「承接（【地位】節準用）」 | TR.2 | ✅ 獨立核驗 PASS（2026-07-23；`:484` 獨列） |
| 4 | **TR.2 Annex A 分列**：①部 32 條仍逐條型別化；A.31–A.59 異質處置分列、無共享失準標 | TR.2 | ✅ 獨立核驗 PASS（2026-07-23；`:485`–`:491` 七列分列） |
| 5 | **T.6 判準非迴指**：含外部識別碼體系×代碼值×有效期間之獨立 iff；claim 降為跨體系表達機制 | T.6 | ✅ 獨立核驗 PASS（2026-07-23；`:293` 三要素＋claim 降格） |
| 6 | **[N] 零逾越**：diff 限本裁決核示之 patch；無 parent 變更、無義務擴張 | ONT 全 diff | ✅ 獨立核驗 PASS（2026-07-23；369cdef 限 5 檔、ONT +18/-7） |
| 7 | **lint 基線**：`python3 -m tools.constitution_lint report` error 0／warning 0 | 全 corpus | ✅ 獨立核驗 PASS（2026-07-23；PASS 7／7 親跑） |
| 8 | **PA／五原則 byte 零改** | `constitution/` 五原則檔 | ✅ 獨立核驗 PASS（2026-07-23；369cdef 五原則檔零 diff） |

**誠實揭露**：上列八項均經獨立 agent 逐項原文／diff／lint 覆核，與施作者同輪機械簡核結論一致；零殘留阻塞項。

**Steward 2026-07-23：**接受 032**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；F-L2-1 採甲案；F-L2-2／3 同案機械施作；F-L2-4 minor 補判準）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-L2-1＝medium；F-L2-2／3／4＝minor；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 032**）。L2 ultracode 處置閉環；蓋章不動搖。第七節獨立對抗核驗已完成（2026-07-23；八項全 ✅）。*
