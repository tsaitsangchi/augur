# Augur Steward 裁決第 2026-038 號

**Phase 3b 接受＋F-IX-3…6 一攬子 minor 處置（L5–L7 執行層交互專項覆核殘留 medium×4）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.1`（解釋之界線）；findings 冊 `audits/L5-L7-INTERACTION-ULTRACODE-20260723.md`（Phase 3b 專項覆核）；RULING-2026-027（M-IX-1／2 已閉、F-IX-3…6 明示另案）；RULING-2026-029（F-IX-4／6 簿記另案；L5 §8.2 復審 **2026-10-14**）；RULING-2026-025（(iii)(iv)(vi) residual 分階段① 復審 **2026-10-14**）；RULING-2026-020（M2 甲案）；RULING-2026-035／036／037（單層 ultracode 定案）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-027／037 體例
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核（Sole Steward 拍板「接受 Phase 3b ＋ RULING-2026-038」）
* **登錄**：Amendment Log **AL-2026-042**
* **性質**：minor／patch 執行層簿記／體例施作；**不動 parent 歸類、不觸 MC [N] 本文、PA／五原則 byte 級零改**；CK／AR／INF **版本維持** v1.0／v1.2／v1.0；**零 major**；**不動搖 L5–L7 蓋章**
* **分級登錄（Steward 2026-07-23）**：**F-IX-3…6**＝ **medium**（處置採 minor／patch 簿記）；零 major

## 〇、接受 Phase 3b 專項覆核 ✅

1. **接受** `audits/L5-L7-INTERACTION-ULTRACODE-20260723.md`：零新 major；RULING-2026-027 兩 major **仍閉**；020 M2／F-L7-8 **維持 honest deferred**；025／029 日曆復審 **2026-10-14**（本裁決**不**結清）；L5–L7 單層蓋章 **不動搖**。
2. 排程：`ULTRACODE-SCHEDULE.md`／`LAYER-SEALING-SCHEDULE.md` §3b 登錄「已接受＋038 閉 F-IX-3…6」。

## 一、擬裁一〔F-IX-3——L6 CS.3 措辭；不另增 LDI 專列〕✅

1. **現況**：FM `defers-in` 已列 `WM.D13`／`D15`／`D22`／`D24`／`D28`；正文 L6.19／L6.20／L6.11／L6.15／L6.21 真承接；Annex LDI **無**該五碼專列（D16／D17 已入 LDI.2–4／LDI.7）。
2. **處置（採 CS.3 措辭案，不補 LDI 列）**：於 L6 CS.3(a) 增明示——上開五碼正文落點已具名；**Annex LDI 不另設專列**；LDI.0 可判定判準為「本表每列→FM／CS.3 三向可解析」（**單向**），**非**「FM 每碼必有 LDI 專列」。
3. **定級**：medium（簿記不對稱；義務非幽靈）。

## 二、擬裁二〔F-IX-4——L5 LDO.3 目標改「L7（L6 僅監督 UI）」〕✅

1. **LDO.3 目標欄**：`L6／L7` → **`L7（L6 僅監督 UI）`**。
2. **同案對齊**（最小）：L5.6 下放括注、Annex L46 Explanation 列、CS.3(b) LDO.3 索引、T-L5-4 呈現面措辭、L7 LDI.30 來源括注——凡寫「LDO.3→L6／L7」處改與目標欄一致。
3. **不改**：L5.6 解釋**內容**義務本文；L7.43 承接句；L6 對 L5.6「不觸及＋理由」矩陣列。
4. **定級**：medium（029 (v)／027 明示另案）。

## 三、擬裁三〔F-IX-5——L7 MC 覆蓋清單補誠實界限句〕✅

1. **CS.4 MC [N] 條款覆蓋清單**末：補與 L6／L5 同型 **誠實界限**句——「本清單＝機器盤點之字面具名；語意承接仍以 Annex TR 為權威，不因本清單宣稱新建語意矩陣或完成『決策四第二輪』嚴格強制」。
2. **定級**：medium（體例；易被誤讀為決策四完成）。

## 四、擬裁四〔F-IX-6——L5 LDO.4 目標改純 L7〕✅

1. **LDO.4 目標欄**：`L5／L7` → **`L7`**。
2. **同案對齊**（最小）：CS.3(b) LDO.4 索引、L5.9 量測落地括注、L7 LDI.31 來源括注——去掉「同層再 DEFER」氣味；**LDI.4→L5.9（定性）**與 **LDO.4→L7（量測實作）** 分工維持。
3. **定級**：medium／minor（029 另案）。

## 五、日曆義務（明示維持）

1. **RULING-2026-025** residual (iii)(iv)(vi)：維持分階段①至 **2026-10-14**——**不關閉**、不翻 major、不重開 §8.2。
2. **RULING-2026-029**／L5 §8.2 復審日：**2026-10-14**——**不假裝結案**（035 已程序性閉合 PRV／ASF；日曆復審仍在卷）。
3. **RULING-2026-020 M2**／037 F-L7-8：維持 **honest deferred**——**禁止假關**、不虛假下放 trigger。

## 六、明示不為

* 不動 MC [N] 本文；PA／五原則 byte 級零改。
* 不重開 §8.2；不翻 L5／L6／L7 蓋章；不升版 CK／AR／INF。
* **不**實施 020 M2 產物表 trigger；**不**結清 025／029 日曆義務。
* 不重跑全棧 3b；不改 L1–L4 規格。

## 七、驗證

* `python3 -m tools.constitution_lint report`：須 **PASS 7／7**（error 0／warning 0）。
* `ULTRACODE-SCHEDULE.md`／`LAYER-SEALING-SCHEDULE.md` §3b 更新＋Amendment Log **AL-2026-042** 於簽核生效時一併辦理。

## 八、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/AGENT-RUNTIME-SPECIFICATION.md` | F-IX-3：CS.3(a) 增 LDI 不另設專列／單向判準措辭 |
| `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | F-IX-4／6：LDO.3／LDO.4 目標欄＋最小對齊句 |
| `specs/INFRASTRUCTURE-SPECIFICATION.md` | F-IX-5：CS.4 覆蓋清單誠實界限；LDI.30／31 來源括注對齊 |
| `constitution/RULING-2026-038-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-042 |
| `ULTRACODE-SCHEDULE.md`／`LAYER-SEALING-SCHEDULE.md` | 3b 接受＋038 閉環 |
| `audits/L5-L7-INTERACTION-ULTRACODE-20260723.md` | 呈核段：Steward 接受＋038 |

## 九、獨立對抗核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 後**須經非施作者**確認之核驗清單。**獨立對抗核驗已完成**（2026-07-23；核驗者＝Cursor 獨立核驗 agent；方法＝逐項檔案原文／`git show b68d96f`／親跑 lint；非施作者 b68d96f）。詳 `audits/RULING-2026-038-INDEPENDENT-VERIFY-20260723.md`。

| # | 核驗項 | 範圍 | 狀態 |
|---|---|---|---|
| 1 | **F-IX-3**：CS.3(a) 明示 D13/15/22/24/28 不另設 LDI 專列＋LDI.0 單向 | L6 CS.3 | ✅ 獨立核驗 PASS（2026-07-23；AR `:502` F-IX-3 段；Annex LDI 無五碼專列） |
| 2 | **F-IX-4**：LDO.3 目標＝`L7（L6 僅監督 UI）`；無殘留「LDO.3→L6／L7」目標欄 | L5 LDO／CS／L46 | ✅ 獨立核驗 PASS（2026-07-23；CK LDO `:215`、L5.6 `:140`、L46 `:232`、T-L5-4 `:498`、INF LDI.30 `:652`） |
| 3 | **F-IX-5**：L7 CS.4 覆蓋清單含誠實界限句（對齊 L6） | L7 CS.4 | ✅ 獨立核驗 PASS（2026-07-23；INF `:1071` 誠實界限句） |
| 4 | **F-IX-6**：LDO.4 目標＝純 `L7`；無「L5／L7」目標欄 | L5 LDO／CS | ✅ 獨立核驗 PASS（2026-07-23；CK LDO `:216`、L5.9 `:160`、INF LDI.31 `:653`） |
| 5 | **020 M2 未假關**：L7／L6 仍 honest deferred | 020／037 | ✅ 獨立核驗 PASS（2026-07-23；AR L6.21 `:211`、INF CS.4 `:1073` cross-layer 誠實未承接） |
| 6 | **025／029 復審日仍 2026-10-14** | 025／029 | ✅ 獨立核驗 PASS（2026-07-23；CK【地位】`:16`、INF `:570`；025／029 原文未改） |
| 7 | **lint PASS 7／7** | corpus | ✅ 獨立核驗 PASS（2026-07-23；PASS 7/7、error 0／warning 0 親跑；git HEAD b68d96f） |
| 8 | **蓋章不動搖**：零 major；CK／AR／INF 版本未升 | 全案 | ✅ 獨立核驗 PASS（2026-07-23；零 major；CK v1.0／AR v1.2／INF v1.0 維持） |
| 9 | **PA／五原則／MC [N] byte 零改** | `constitution/` | ✅ 獨立核驗 PASS（2026-07-23；b68d96f MC／PA／五原則檔零 diff） |
| 10 | **超 scope 零**：diff 限本裁決核示之 patch | git diff | ✅ 獨立核驗 PASS（2026-07-23；b68d96f 限 8 檔、+129/-23，F-IX-3…6 授權範圍） |

**Steward 2026-07-23：接受 Phase 3b 專項覆核、同案 038**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；接受 3b；F-IX-3 CS.3 措辭；F-IX-4 LDO.3→L7（L6 僅監督 UI）；F-IX-5 L7 誠實界限；F-IX-6 LDO.4→純 L7；020 M2 維持 deferred；025／029 復審維持 2026-10-14）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-IX-3…6＝medium；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 Phase 3b ＋ RULING-2026-038**）。F-IX-3…6 處置閉環；蓋章不動搖。第九節獨立對抗核驗已完成（2026-07-23；十項全 ✅）。*
