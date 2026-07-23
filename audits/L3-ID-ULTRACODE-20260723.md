# AUGUR-ID v1.0 單層 ultracode 窮盡對抗檢驗報告 [I]（L3）

## 一、元資料

* **日期**：2026-07-23
* **攻擊標的**：`specs/IDENTITY-SPECIFICATION.md`（AUGUR-ID **v1.0**，799 行，正文 ID.1–ID.81＋Annex O／DO／L4／TR／CS）
* **git HEAD**：`0ae274396ef164beab2e8dba2b75578e2d4e2614`
* **方法**：`ULTRACODE-SCHEDULE.md` L3 六維（ADP｜REV｜LFC｜RSV｜ASF｜MTX）× Find→Verify→Critic→Synthesize；三鏡反駁紀律同 L0／L1／L2（預設 refuted=true、逐字＋行號、≥2 鏡出局）。
* **對照卷宗**：`audits/L1-WM-ULTRACODE-20260723.md`（CSV-2／T-ID-3 跨層）、`audits/L2-ONT-ULTRACODE-20260723.md`（封印鏈下游）、RULING-2026-004（ID 充任）、RULING-2026-009（§0.1 殘留真空）、RULING-2026-014（Security／Index／FredSeries 判準採認）、RULING-2026-019（TR.Y 補列）、RULING-2026-030（T-ID-3 部分解消措辭）、`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md`（IDO.4 下游幽靈查證）、`specs/ONTOLOGY-SPECIFICATION.md` Annex L3（分界鏡像）。
* **lint 基線（親跑）**：`python3 -m tools.constitution_lint compliance specs/IDENTITY-SPECIFICATION.md` → **✅ PASS（error 0 / warning 0 / info 3）**——僅作對照物，非合憲依據；info 含 mc-version v1.4→v1.5 換發提醒、WM.44 骨架覆蓋、TR 標籤 193 筆比對。
* **鐵律聲明**：[I] 審查素材；零規格修改；不採信自陳（13 事件 Evidence 覆蓋、OPEN-1 採認狀態、TR 矩陣完備性均親讀）；處置權專屬 Steward。
* **執行形態誠實揭露**：單代理 ultracode（同 L0／L1／L2 輪）；獨立性弱於 2026-07-18 首審之多代理形態。
* **L0 界限**：本輪未重跑 L0 本體攻擊；L0→L3 投影依現行 MC v1.5 文本，非窮盡覆核。

---

## 二、逐維 Find（全部候選，含事後出局者）

severity：major／**medium**／minor／info。

### ADP — 採認五要素效力鏈（OPEN-1 未拍板下是否空轉）

**正面清點（親讀，非採信）**：
* **ID.20 五要素閉集**〔目標 Type、L2 條款引用、生效時點、Evidence 引用、作成者〕逐字在（`:172-173`）；缺任一「不生效力」可機械判。
* **封印鏈四環貫穿**：ONT.20（制定）→ ONT.21（採認封印＋T.0 總括句）→ ID.20（採認機制）→ AO.1–AO.4（OPEN-1 具名落點）——與 L2 ultracode SEAL 維結論一致；**採認前 resolution 效力零洩漏**（ID.21 `:178`）。
* **RULING-2026-014 已作 ID.20 路徑之實質採認**：T.1 Security／T.2 Index／FredSeries 操作化判準追認（2026-07-18）——OPEN-1 **非空轉**；機制（ID.20）＋裁決（014）＋DB 載體（`identity_criteria`）三件套在卷。
* **Issuer（T.20）採認路徑**：AO.4 具名落點（`:364-366`）＋ DO.1 雙 Type 列——Security 已採認、Issuer 仍待採認屬**可判定分轨**，非死鎖。

| id | severity | 主張 | 證據（path:line＋逐字） |
|---|---|---|---|
| **F-L3-1** | **medium** | **AO.2 正文與 T-ID-3／RULING-2026-014 現況不同步**：AO.2 仍書「OPEN-1 之正式判準採認**待 Steward／決策層拍板**」（`:357`）及可判定判準「**無採認紀錄時**將 Security 引用視為已解析者違反」（`:358`）——而 CS.2 T-ID-3（`:748`）已載「〔部分解消〕RULING-2026-014 已採認 Security／Index／FredSeries」；L1 CSV-2／030 亦同族同步。AO.2 **未**依 T-4/T-6 體例加部分解消；Security 面已失真（過保守方向），Issuer（T.20）面仍確實待採認（014 未含 T.20）。 | `:356-358`（AO.2）；`:748`（T-ID-3）；`constitution/RULING-2026-014-ONT20-CRITERIA.md:11` |

**出局候選**：「OPEN-1 未拍板→本層採認機制空轉」——3/3 出局（014 採認在卷、ID.20 五要素＋AO.4 Issuer 落點完備、保守預設非停擺）。

### REV — ID.32「做多了也違憲」之界線可判定性

**正面清點**：
* **雙向判準成對**：ID.32 可判定判準明定**正向**（claim 繫結→恰一錨點）與**負向**（「本層對權威 Representation 作可被 L4 直接消費之**實際指定**（而非僅結構前提）者，反為**下侵**、違 ID.2／ID.70」）（`:224`）——「做多了」邊界字面可解析。
* **三件套互證**：ID.70 列舉 L4 專屬清單（`:322-328`）＋ Annex L4 分界表五面向兩欄無交集（`:393-400`）＋ IDO.8 下放掛鉤（`:384`）——與 L2 BND 維「零下侵」鏡像一致。
* **下游幽靈查證（IDO.8 樣本）**：KS 側 IDO.8→KDI 承接在卷（`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` KS 矩陣 IDO.8 列）——非幽靈。

**零 finding**（REV 維）。

### LFC — lifecycle 13 事件與 Evidence 強制覆蓋（mint／correct／tombstone／de-identify）

**正面清點**：
* **ID.40 事件枚舉 13 型**（含 mint、correct、tombstone、de-identify）＋每一事件 schema 均含「Evidence 引用、作成者」（`:235`）。
* **de-identify 專條**：ID.42 可判定判準三元（tombstone 存續／provenance／lineage）（`:248-250`）——獨立可機械判。
* **mint 前置**：ID.11 鑄造義務＋ ID.14「lifecycle 事件是否具備 Evidence 引用（依 ID.40）」（`:161`）——間接覆蓋 mint。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L3-3 | minor | **ID.40 可判定判準窄於自身事件枚舉**：schema 列 13 型（含 mint、correct、tombstone、de-identify），惟可判定判準僅書「任一 **merge／split／retire／relist／redirect** 事件缺 Evidence 引用者違反本條」（`:237`）——mint／correct 缺 Evidence 依 ID.40 字面**不可機械判違規**（de-identify 有 ID.42 兜底、tombstone 嵌於 ID.42(a)）。 | `:235-237` |

### RSV — ID.50 合取式與 provisional 解析

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L3-2** | **medium** | **ID.50「已解析」合取式第二 conjunct 跨引錯誤＋同檔內部不一致**：ID.50 定義「已解析」iff〔判準採認已生效（ID.20）**∧** 該引用之 provisional 狀態旗標已依 **ID.51(a) 清除**〕（`:275`）；可判定判準同引（`:276`）。惟 ID.51(a) 逐字僅定義「**未解析存量**（unresolved backlog）……處於 provisional 狀態之 Observation 指涉集合之基數，**必須**可盤點」（`:282`）——**指標定義，非旗標清除機制**；全檔無「provisional 狀態旗標清除」之獨立定義。另 CS.1-P2 判準揭示將「已解析」「以採認紀錄存在（ID.20）操作化」（`:727`），與 ID.50 合取式**矛盾**。→ ID.50 核心可判定判準**不可自足機械執行**。 | `:275-276`、`:282`、`:727` |

**正面清點（合取第一項）**：ID.20 採認＋ ID.21 未採認即 provisional——第一 conjunct 可判；問題集中在第二 conjunct 與 CS 不一致。

### ASF — as-of 法源收斂（§P4.E2 單軸）

**正面確認（info）**：
* §8 引言明書「法源收斂……**P4.E2 單軸**，P3.E3 為誤引；本章**不引** `§P3.E3` 為義務錨」（`:302`）。
* ID.60 錨定 `§P4.E2`（`:306-307`）；ID.61 重建引擎 DEFER L4（`:312-313`）——與 AUD-07 裁註一致。
* **零 finding**。

### MTX — TR 矩陣完整性與 P5 家族理由欄

**正面清點**：
* TR.Y（2026-07-18）已補列 15 組漏列、誠實更正「缺 0 條」不實（`:674`）；linter TR 標籤 193 筆比對 PASS。
* TR.A §P3 家族核心細化落點逐條在卷。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L3-4 | minor | **§0.1 上層規格列 ONT 仍標「草案」**（RULING-009 已知真空未閉）：`§0.1` 書「`AUGUR-ONT v1.0`（Layer 2，**草案**）」（`:55`），與【地位】「`AUGUR-ONT v1.0` 已於 2026-07-17 先行生效」（`:18`）及 Annex CS `upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0]`（`:709`）矛盾。 | `:55`、`:18`、`:709` |
| F-L3-5 | minor | **TR.Y 補列表 MC §2.8（Agent 定義）落點誤植 P5.D**：TR.Y 列「MC §2.8（Agent 定義）｜**P5.D**／P5.E1、ID.11」（`:682`）——P5.D 為 **Action** 定義（TR.B `:462`），非 Agent；應為 ID.11（Agent identifier 型別化）或 §2.8 專列，不應混引 P5.D。 | `:682`；`:462` |
| F-L3-6 | minor | **TR.B P5 家族「理由欄」格式位移**：P5.D–P5.Y 各列將完整「不觸及＋理由：……」填入「ID 落點」欄、第三欄「模式」僅餘「不觸及＋理由」無理由正文（例 P5.E1 `:463`）——與 TR.A／TR.C 三欄慣例不一致，機器抽取「模式」欄將丟失理由正文。 | `:461-470` |
| F-L3-7 | minor | **TR.C Annex D 表部分主題列文字截斷**：D4「（含 WM.3（L3）」、D6「拍板後承（L3）」、D8「embargo、p（L4）」等括號／字串未閉合（`:595-599`）——[I] 矩陣可讀性缺陷，不影響 defers-in 雙向對表（CS.3 `:757` 完整）。 | `:595-599` |

**info（觀察，不入處置佇列）**：
* 【地位】`:17` 已載 TR.Y 更正 footnote（「缺 0 條」應連同 TR.Y 讀）——誠實揭露在卷；惟 TR.0／TR.Z 正文仍保留未 inline 修正之「缺 0 條」字樣，屬已知手工維護風險（TR.Y `:674` 已明說）。

---

## 三、Verify — 三鏡獨立反駁結果

### 存活（7）

**F-L3-1【medium·存活 3/3】AO.2 與 014／T-ID-3 不同步**
* 文本體系鏡：**未能反駁**。AO.2 `:357-358` 逐字與 T-ID-3 `:748`、RULING-014 主文逐字衝突（Security 面）；無 expressio 可调和讀法。
* 形式邏輯鏡：**未能反駁**。同一規格內 [N] 節（AO.2）與 CS.2  tension 表對同一事實作相反陳述→文件缺陷。
* 實務規避鏡：**未能反駁（惟界定危害）**。危害＝過保守（Security 已採認仍讀為全待拍板），非放行；sync patch 即可癒。不足以降 minor——因涉 OPEN-1 治理敘事與 L1 CSV-2 同族已裁先例。

**F-L3-2【medium·存活 3/3】ID.50 ↔ ID.51(a) 跨引錯誤**
* 文本體系鏡：**未能反駁**。ID.51(a) 逐字無「清除／旗標」語；ID.50 引用 ID.51(a) 為假引。
* 形式邏輯鏡：**未能反駁**。合取式第二項無定義→「已解析」不可判定；CS.1-P2 僅 ID.20 加劇內部不一致。
* 實務規避鏡：**未能反駁**。消費者若依 CS.1-P2 單 conjunct 操作 vs 依 ID.50 字面→稽核結論分歧；非單純 editorial。

**F-L3-3【minor·存活 2/3】ID.40 可判定判準窄於枚舉**
* 文本體系鏡：**未能反駁**（`:235` vs `:237` 字面差集非空）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。ID.14＋ID.42 部分兜底；mint 事件 Evidence 缺口實害低（mint 為入場非升級 Knowledge 之直接 gate）。維持 minor。

**F-L3-4【minor·存活 2/3】§0.1 ONT「草案」**
* 文本體系鏡：**未能反駁**（`:55` vs `:18` 矛盾）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。RULING-009 已登記真空、全體以 v1.0 運作；一句刪「草案」即癒。維持 minor。

**F-L3-5【minor·存活 2/3】TR.Y §2.8→P5.D 誤植**
* 文本體系鏡：**未能反駁**（P5.D＝Action，非 Agent）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。[I] 矩陣列、ID.11 正文承載 Agent identifier 義務未落空。維持 minor。

**F-L3-6【minor·存活 2/3】P5 理由欄位移**
* 文本體系鏡：**未能反駁**（`:463` 等逐字在卷）。
* 形式邏輯鏡：**未能反駁**（模式欄資訊熵低於他族）。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。CS.1-P5 含完整理由；義務未失守。維持 minor。

**F-L3-7【minor·存活 2/3】Annex D 表截斷**
* 三鏡同 F-L3-6 模式——[I] 可讀性、CS.3 完整。維持 minor。

### 出局（2，counter_evidence 留卷）

| id | 出局鏡數 | 反駁 counter_evidence |
|---|---|---|
| 「OPEN-1 未拍板→採認五要素鏈空轉」 | 3/3 | 文本：`constitution/RULING-2026-014-ONT20-CRITERIA.md:11` 主文一（ID.20 採認）＋ ID.20 `:172-173` 五要素；形式：AO.4 Issuer 分轨可判；實務：014 已 DB 施作、T-ID-3 部分解消。 |
| 「IDO.4 resolution 下放無下游承接＝幽靈」 | 3/3 | 文本：`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:503-507` KS.83 分 (i)(ii) 承接 ID.51／IDO.4；形式：KDI.13 雙向索引；實務：T-KS-6  tension 誠實揭露 L4/L5 定性分歧非漏承。 |

---

## 四、Critic — 完整性批評與抽查

**「什麼還沒被檢查」（誠實清點）**：

1. **Annex T 全 34 型別判準之領域正確性**未攻擊——屬 L2 制定內容；本層僅查採認／機制化路徑。
2. **IDO.1–IDO.8 八掛鉤僅抽樣 IDO.4／IDO.8**（L4 側）；IDO.5→L7、IDO.7→L6 未逐層掃描——留 L4／L6／L7 各層 ultracode。
3. **執行層是否真的 mint-before-upgrade／provisional 保守處理**屬 runtime 稽核，非文本審查所及。
4. **RULING-009 §0.1 四行真空**（ID:55／75 等）本輪僅就 ID:55「草案」一項開列；`:75` 引用格式行未獨立開 finding（同族、可併 F-L3-4 同案）。
5. **WM.44 matrix-coverage 機械強制**（019 決策四第二輪）仍未建置——TR.Y 已誠實揭露；本輪未重跑窮舉腳本驗 15 組補列後零漏。

**抽查推翻理由**：F-L3-3／4／5 之實務鏡降 minor 理由經查各該兜底條文（ID.14／ID.42、【地位】、ID.11）實存，維持。**F-L3-2 不可降級**——ID.50 為 L3 核心閘，合取式不可判＝可稽核性缺陷，非單純 TR 標記問題。

**方法界限**：單代理分節；lint PASS 不阻斷 F-L3-2（語意 cross-ref 超出 linter 骨架）。

---

## 五、Steward 呈核摘要

### 存活清單（medium×2＋minor×5）

| id | severity | 一句主張 | 建議處置與門檻 |
|---|---|---|---|
| **F-L3-1** | **medium** | AO.2 仍寫 OPEN-1 全待拍板，與 RULING-2026-014／T-ID-3 部分解消矛盾；Security 面過保守、Issuer（T.20）面仍確實待採認 | 同案 minor／editorial（030 CSV-2 同體例）：AO.2 加部分解消註記（014：Security／Index／FredSeries；改名／借殼＋Issuer 殘留面續保守）＋可判定判準改「無**該 Type** 採認紀錄時……」；**Issuer 是否另開採認屬 Steward 裁量** |
| **F-L3-2** | **medium** | ID.50「已解析」合取式引用 ID.51(a) 假引（(a) 僅 backlog 指標）；CS.1-P2 僅 ID.20 與 ID.50 矛盾→核心閘不可自足判定 | 同案 patch／minor：二擇——**(甲)** ID.50 第二 conjunct 改引新 ID.51(d)「provisional 清除判準」或 ID.53／WM.18 既有機制；**(乙)** 刪除第二 conjunct、明定「已解析＝該 Type 採認已生效（ID.20）且該引用非 ID.21 provisional 態」；同步 CS.1-P2 `:727` |
| F-L3-3 | minor | ID.40 可判定判準未覆 mint／correct 之 Evidence 檢查 | 同案：`:237` 擴為「任一 lifecycle 事件（`:235` 枚舉閉集）缺 Evidence……」或明確「mint／correct 準用 ID.14」 |
| F-L3-4 | minor | §0.1 `:55` ONT 仍標「草案」 | 同案 mechanical：刪「草案」；可併 RULING-009 真空同案（`:75` 引用格式行） |
| F-L3-5 | minor | TR.Y §2.8 落點誤引 P5.D | 同案 [I]：改「ID.11、CS.1-P5（Agent identifier）」 |
| F-L3-6 | minor | TR.B P5 列理由欄位移 | 同案 [I]：理由併入模式欄或模式欄改「不觸及」＋理由入第三欄（同 TR.C 慣例） |
| F-L3-7 | minor | TR.C Annex D 主題列截斷 | 同案 [I] mechanical 補全 D4/D6/D8 括號 |

### 建議同案 RULING 要點（本輪僅呈核，不開正式檔）

1. **一攬子標題**：`RULING-2026-0XX-L3-ID-ULTRACODE-DISPOSITION`（號碼由 Steward 次序分配）
2. **major**：**零**——不建議升格；F-L3-1／2 均為 patch／minor 可癒之可判定性／同步缺陷
3. **medium 同案順修**（用戶已預授）：F-L3-1＋F-L3-2 必含；F-L3-3–7 併入同一 RULING §patch 清單
4. **Issuer 裁量項**：F-L3-1 處置時請 Steward **明示** T.20 Issuer 是否隨 014 追認或另開採認——本 ultracode 不代裁
5. **獨立核驗**：依 RULING-2026-028 第 3 點，處置施作後交獨立 agent 八項核驗＋lint 親跑
6. **Amendment Log**：`AL-2026-037` 登錄 ultracode 處置

### 正面確認（強化蓋章之證據）

* **ADP**：採認五要素＋014 實例＋AO.4 Issuer 分轨——**非空轉**；OPEN-1 機制鏈完整。
* **REV**：ID.32／ID.70／Annex L4／IDO.8 四重下侵封印；「做多了也違憲」負向判準字面可執行。
* **LFC**：13 事件 schema 含 Evidence；ID.42 去識別化三元完備；AUD-05 存續邊界（ID.43）可機械紅旗。
* **RSV**：ID.50 第一 conjunct（ID.20）＋ ID.21 保守預設鏈清楚；問題 isolated 於第二 conjunct。
* **ASF**：P4.E2 單軸、P3.E3 誤引已剔除——AUD-07 法源收斂正確。
* **MTX**：TR.Y 15 組補列屬實；linter 193 標籤 PASS；P5 全族有 CS.1-P5 總綱兜底。
* **defers-in/out**：ID.3 十列承接盤點＋ Annex DO 八掛鉤＋ CS front-matter 雙向一致（`:757-758`）。

### 是否動搖 L3 蓋章

**否——不動搖**。零 major；2 medium 均為**可判定性／文件同步**缺陷（非採認機制骨架、非 lifecycle 語義、非 as-of 法源錯位）；5 minor 為 [I] 矩陣／§0.1 殘留／判準 enumerate 缺口。**動搖程度定級：僅需 patch／minor 同案處置**（非重採認、非 §8.2 補審）。

### Steward 簽核（2026-07-23）

* **拍板**：接受 L3 ultracode 呈核（零 major、medium×2＋minor×5）；同案 **RULING-2026-033** 順修 F-L3-1（AO.2／T-ID-3 同步，**Issuer T.20 不另採認**）＋F-L3-2（**乙案**——ID.50 已解析／CS.1-P2 對齊）及 minor×5；蓋章不動搖。
* **F-L3-2 採案**：**乙案**（刪第二 conjunct；已解析＝採認生效且非 ID.21 provisional）。
* **定案**：Steward 2026-07-23 **接受 033**（`constitution/RULING-2026-033-L3-ID-ULTRACODE-DISPOSITION.md`；**AL-2026-037**；**獨立對抗核驗 PASS** 2026-07-23）。

---

*本報告為 [I] 審查素材，全程零規格修改（審計交付物除外）。攻擊官／反駁官／批評官：ultracode-L3 代理（單代理分節），2026-07-23；lint PASS 7/7 親跑對照。**L3 定案**：`constitution/RULING-2026-033-L3-ID-ULTRACODE-DISPOSITION.md`（2026-07-23 Steward **接受 033**；**AL-2026-037**；獨立對抗核驗 PASS 2026-07-23）。*
