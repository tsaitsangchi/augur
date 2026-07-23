# Augur Steward 裁決第 2026-035 號

**L5（AUGUR-CK v1.0）單層 ultracode findings 處置——EO.1 收 L5.10 謂詞、L5.6(iii) Computational 路徑可判定性、enumeration／DRAFT／TR.F 歷史語 minor×4（合併版 findings：2 medium＋4 minor，同案）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.2`（較嚴格解讀之解消）、`§8.1`（解釋之界線，v1.5）；findings 冊 `audits/L5-CK-ULTRACODE-20260723.md`；RULING-2026-029（§8.2 條件通過、附條件 PRV／ASF 複核）；RULING-2026-030（D19/D23/D25 覆核 PASS）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-034（L4 同體例一攬子）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **登錄**：Amendment Log **AL-2026-039**
* **性質**：minor／patch 執行層施作（第一至七點）；**不動 parent 歸類、不觸 MC、PA／五原則 byte 級零改、CK 版本維持 v1.0**——所涉變更為 [N] EO 完備性／EXP 可判定性補全、[I] enumeration／DRAFT 殘留／TR.F 歷史語機械修正
* **分級登錄（Steward 2026-07-23）**：**F-L5-1／6**＝ **medium**（處置採 patch／minor）；**F-L5-2–5**＝ **minor**。零 major；**不動搖 L5 蓋章**（findings 冊結論）

## 一、擬裁一〔Annex EO.1 收 L5.10 謂詞——F-L5-1，medium〕✅

1. **EO.1 增列 L5.10 三翼對應謂詞**（對齊 L5.10(a)(b)(c)）：
   - 「as-of 推理合規」（as-of-inference-compliant）——vintage≤T、禁 lookahead；
   - 「anti-leakage 入口過濾」（anti-leakage-entry-filtered）——推理入口經 KS §5 as-of gate 過濾；
   - 「as-of 能力等級透明」（as-of-capability-transparent）——結論標示 A0–A3 能力等級、不足則降級或 provisional。
2. **定級**：Steward 定級 **medium**（§8.3 掃描—完備性義務；L5.10 已生效 [N] 卻未收錄→可判定性缺口）。

## 二、擬裁二〔L5.6(iii) Computational 路徑可判定性——F-L5-6，medium〕✅

1. **L5.6 增 Computational Evidence 路徑 (iii) 最低滿足**（L5.7／KS.71 路徑）：可重放之輸入→輸出映射（含推理時輸入 Evidence 集識別）＋所用 model／演算法版本（與 (iv) Grading Method provenance 對齊，但 (iii) 須可機械盤點「自何輸入得何輸出」，不得以 (iv) 單獨替代 (iii) 之存在性）；attention／權重等不可讀內部狀態**不**構成本層 (iii) 必要內容——feature attribution 之呈現 DEFER Layer 7（LDO.3 延伸）。
2. **定級**：Steward 定級 **medium**（029 (v) 條件通過之 EXP 複核議題；**不升格 major**）。

## 三、擬裁三〔LDI.6／TR.B／CS.3 enumeration 納 L5.10——F-L5-2，minor〕✅

1. **LDI.6、TR.B §5 角色四、CS.3(a) MC.role4**：「§3–§8（L5.1–L5.9）」→「§3–§8（L5.1–L5.10）」或等價「含 L5.10」表述。

## 四、擬裁四〔L5.90 DRAFT 殘留——F-L5-3，minor〕✅

1. **L5.90**：刪「DRAFT」或改述為 v1.0 生效（RULING-2026-029）。

## 五、擬裁五〔CS.2 T-L5-1…5 DRAFT 殘留——F-L5-4，minor〕✅

1. **CS.2 五列緩解欄**：「DRAFT。」→「已核定（029）。」（同 T-L5-6 體例）。

## 六、擬裁六〔TR.F 歷史語——F-L5-5，minor〕✅

1. **TR.F 若干列**：「現全缺／卻整區塊缺席／零列——最尖銳之矛盾」等重作前歷史語改述為「已補列（019 重作）」——與 16 列在卷之現況一致。

## 七、RULING-2026-029 附條件之程序性閉合

1. **PRV／ASF 複核（029 附條件 (v)(viii)）**：本 ultracode 已執行 PRV／ASF 維度對抗審查——**未翻 major**（findings 冊 PRV 零 finding、ASF medium×1＋minor×4 均 patch 可癒）。
2. **程序性閉合**：Steward 登錄 029 附條件 PRV／ASF **程序性閉合**（2026-07-23）——**不重開 §8.2**、不續延 provisional；029 (v)(viii) 之 ultracode 義務視為履行完畢。
3. **仍另案**：**F-IX-4**（LDO.3 目標欄）、**F-IX-6**（LDO.4 同層 DEFER）——承 RULING-2026-027／029 簿記，**不併本案**、維持 minor 另案。

## 八、明示不為

* 不動 `AUGUR-KS v1.1`／`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0` 任何條文；不動 MC；PA／五原則 byte 級零改。
* **F-IX-4／F-IX-6 不併本案**——留另案 minor。
* L6–L7 各層 ultracode 不併本案。

## 九、驗證

* `python3 -m tools.constitution_lint report`：PASS 不退轉。
* `ULTRACODE-SCHEDULE.md` L5 列更新＋Amendment Log 登錄 AL-2026-039 於簽核生效時一併辦理。

## 十、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | F-L5-1～6 全覆蓋：EO.1 L5.10 謂詞；L5.6(iii) Computational 最低滿足；LDI.6／TR.B／CS.3；L5.90；CS.2；TR.F 歷史語；【地位】／尾註 029 ultracode 閉合 |
| `constitution/RULING-2026-035-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-039 |
| `ULTRACODE-SCHEDULE.md` | L5 列閉環 |
| `audits/L5-CK-ULTRACODE-20260723.md` | 呈核段更新 |

## 十一、獨立對抗核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 後**須經非施作者**確認之核驗清單。**獨立對抗核驗已完成**（2026-07-23；核驗者＝Cursor 獨立核驗 agent；方法＝逐項檔案原文／`git show 15f3ef1`／親跑 lint；非施作者 15f3ef1）。

| # | 核驗項 | 範圍 | 狀態 |
|---|---|---|---|
| 1 | **EO.1 L5.10 謂詞**：三翼 as-of／anti-leakage／能力透明已收錄 | EO.1 | ✅ 獨立核驗 PASS（2026-07-23；`:537-539` 三謂詞對齊 L5.10(a)(b)(c)） |
| 2 | **L5.6(iii) Computational 最低滿足**：可重放映射＋model 版本；feature attribution DEFER L7 | L5.6 | ✅ 獨立核驗 PASS（2026-07-23；`:140` 可重放映射＋model 版本；feature attribution DEFER L7／LDO.3） |
| 3 | **enumeration 納 L5.10**：LDI.6／TR.B／CS.3(a) 一致 | LDI.6、TR.B、CS.3 | ✅ 獨立核驗 PASS（2026-07-23；`:201`、`:283`、`:506` 均 L5.1–L5.10） |
| 4 | **L5.90 無 DRAFT**：與 v1.0 生效敘事一致 | L5.90 | ✅ 獨立核驗 PASS（2026-07-23；`:173` v1.0 生效 RULING-2026-029；全檔零裸 DRAFT） |
| 5 | **CS.2 T-L5-1…5**：無裸 DRAFT、已核定（029） | CS.2 | ✅ 獨立核驗 PASS（2026-07-23；`:494-498` 五列均「已核定（029）」） |
| 6 | **TR.F 歷史語**：無「零列／現全缺」與 16 列在卷矛盾 | TR.F | ✅ 獨立核驗 PASS（2026-07-23；`:428-443` 16 列在卷；歷史語改「已補列（019 重作）」） |
| 7 | **029 PRV／ASF 程序性閉合**：035 §七登錄、不重開 §8.2 | RULING-029／035 | ✅ 獨立核驗 PASS（2026-07-23；findings 冊 PRV 零 finding、ASF 未翻 major；035 §七程序性閉合、F-IX-4／6 仍另案） |
| 8 | **[N] 零逾越**：diff 限本裁決核示之 patch | CK 全 diff | ✅ 獨立核驗 PASS（2026-07-23；15f3ef1 限 5 檔、CK +40/-17，僅 F-L5-1～6 授權範圍） |
| 9 | **lint 基線**：`python3 -m tools.constitution_lint report` error 0／warning 0 | 全 corpus | ✅ 獨立核驗 PASS（2026-07-23；PASS 7／7 親跑；error 0／warning 0） |
| 10 | **PA／五原則 byte 零改** | `constitution/` 五原則檔 | ✅ 獨立核驗 PASS（2026-07-23；15f3ef1 MC／PA 檔零 diff） |
| 11 | **F-IX-4／6 仍另案**：未併入本案 diff | LDO.3／LDO.4 | ✅ 獨立核驗 PASS（2026-07-23；LDO.3／LDO.4 目標欄未改；035 §七／§八仍列另案） |
| 12 | **蓋章不動搖**：零 major、CK v1.0 維持 | 全案 | ✅ 獨立核驗 PASS（2026-07-23；零 major；【地位】v1.0 生效維持） |

**誠實揭露**：上列十二項均經獨立 agent 逐項原文／diff／lint 覆核，與施作者機械簡核結論一致；零殘留阻塞項。

**Steward 2026-07-23：**接受 L5 ultracode 呈核、同案 035**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；F-L5-1 EO.1 收 L5.10 謂詞；F-L5-6 L5.6(iii) Computational 最低滿足；F-L5-2–5 同案機械施作；029 PRV／ASF 程序性閉合；F-IX-4／6 仍另案）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-L5-1／6＝medium；F-L5-2–5＝minor；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 L5 ultracode 呈核、同案 035**）。L5 ultracode 處置閉環；蓋章不動搖。第十一節獨立對抗核驗已完成（2026-07-23；十二項全 ✅）。*
