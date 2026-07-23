# AUGUR-CK v1.0 單層 ultracode 窮盡對抗檢驗報告 [I]（L5）

## 一、元資料

* **日期**：2026-07-23
* **攻擊標的**：`specs/COGNITIVE-KERNEL-SPECIFICATION.md`（AUGUR-L5 **v1.0**，545 行，正文 L5.1–L5.10＋L5.90–L5.92＋Annex LDI/LDO/L46/TR/CS/EO）
* **git HEAD**：`1b050374696f95551159321ffca67c435b88323f`
* **方法**：`ULTRACODE-SCHEDULE.md` L5 六維（ASF｜TRM｜FLG｜TER｜EXP｜PRV）× Find→Verify→Critic→Synthesize；三鏡反駁紀律同 L0–L4（預設 refuted=true、逐字＋行號、≥2 鏡出局）。
* **對照卷宗**：RULING-2026-029（§8.2 條件通過、PRV／ASF 複核條件）、RULING-2026-030（L5 D19/D23/D25／FM D12–D28 簿記）、RULING-2026-027（M-IX-2 L5.10 編號地圖）、RULING-2026-034（KS.34 推理規則 Confidence 缺省——**L5.3 meet 上游已癒合**）、`audits/L4-KS-ULTRACODE-20260723.md`（L5.3 消費對照）。
* **lint 基線（親跑）**：`python3 -m tools.constitution_lint compliance specs/COGNITIVE-KERNEL-SPECIFICATION.md` → **✅ PASS（error 0 / warning 0 / info 3）**——僅作對照物，非合憲依據；info 含 mc-version v1.4→v1.5 換發提醒、WM.44 骨架覆蓋、TR 標籤 125 筆比對。
* **鐵律聲明**：[I] 審查素材；零規格修改；不採信自陳（TR.F 16 區塊、D19/D23/D25、provisional 解除均親讀）；處置權專屬 Steward。
* **執行形態誠實揭露**：單代理 ultracode（同 L1–L4 輪）；獨立性弱於 2026-07-18 首審之多代理形態。
* **029／030 已癒合項覆核（不重打）**：D19 空集揭露／D23 不觸及／D25 不觸及（TR.C `:378-383` 與 030 第三點一致）；front-matter `defers-in` 已含 WM.D12/D13/D22/D28（030 §四(e)）；L5.10 真落點（LDI.5／L5.10／TR.A §P4.E2）；T-L5-6 已裁（029 (vii)）；KS.34 `Conf(推理規則)` 缺省 STRONG＋EO.1（034 甲案——L5.3 meet 可機械計算）；F-IX-4／F-IX-6（LDO.3／LDO.4 多目標欄）仍列 029 簿記另案 minor——本輪僅覆核在卷、不另開 finding。

---

## 二、逐維 Find（全部候選，含事後出局者）

severity：major／**medium**／minor／info。

### ASF — L5.10 新增後之全域一致性（stale footer／EO.1／CS front-matter）

**正面清點（親讀）**：
* **L5.10 正文與 LDI.5／LDO.5／TR.A §P4.E2／WM.30–31／HOOK-01 對齊**：`:164-169` 三翼 (a)(b)(c) 在卷；as-of 消費非幽靈（019 幽靈→L5.10 已解）。
* **文末尾註／目錄已納 L5.10**：`:39`、`:543` 計入 L5.10；027 M-IX-2 編號地圖一致。
* **front-matter defers-in（030 後）**：`:467` 含 `WM.D12, WM.D13, WM.D22, WM.D28` ＋ KDO 家族——與 CS.3(a) `:505` 三向一致（D19 空集僅 TR 揭露、非 defers-in 掛鉤，030 設計如此）。

| id | severity | 主張 | 證據（path:line＋逐字） |
|---|---|---|---|
| **F-L5-1** | **medium** | **Annex EO.1 未收錄 L5.10 自創／操作化謂詞**：L5.10 `:164-169` 定義 as-of T 推理之時間邊界、anti-leakage 入口過濾、能力等級透明三組可判定判準，惟 EO.1（`:526-537`）僅列 L5.1–L5.9 謂詞，**無**「as-of 合規／anti-leakage 過濾／vintage≤T」等 L5.10 謂詞。`:538` 掃描—完備性義務要求正文新增謂詞**必須**同步 EO.1——L5.10 已生效 [N] 卻未收錄→§8.3 可判定性缺口（保守解釋下 as-of 相關宣稱不可機械對表）。 | `:164-169`；`:526-537`；`:538-539` |
| F-L5-2 | minor | **LDI.6／TR.B／CS.3 職掌範圍 enumeration 仍寫 L5.1–L5.9、未納 L5.10**：LDI.6 `:200`「§3–§8（**L5.1–L5.9**）」；TR.B §5 角色四 `:282`「§3–§8（**L5.1–L5.9**）」；CS.3(a) `:505`「角色四→§3–§8」——L5.10 已為 §8 [N] 核心 as-of 條款，enumeration 字面未同步（LDI.5 另列 KDO.6→L5.10，非幽靈，惟盤點表不一致）。 | `:200`；`:282`；`:505` |
| F-L5-3 | minor | **L5.90 仍標 CS 生效要件含「DRAFT」**：`:172` 書「front-matter…俱全為機器可判生效要件（惟 Steward 充任認定另為裁決要件，**DRAFT**）」——與【地位】`:13-16`、§0.1 `:60`、TR.Z `:447` 之 **v1.0 §8.2 條件通過** 現況矛盾（029 已解除 provisional、作成 §8.2）。 | `:172`；`:13-16`；`:447` |
| F-L5-4 | minor | **CS.2 T-L5-1…T-L5-5 狀態欄仍裸「DRAFT。」**：`:494-498` 五列緩解欄末「非豁免事項。**DRAFT。**」——029 (vii) 已核定六緊張＋T-L5-6 追認；DRAFT 字樣為 029 可選順修 residual，與 v1.0 生效敘事不一致（T-L5-6 `:499` 已更新為已裁，其餘五列未同步）。 | `:494-499` |

**出局候選**：「front-matter 未更新 L5.10」——3/3 出局（030 FM 補 D12/D13/D22/D28；KDO.6 本已在 FM；L5.10 非 WM.D 掛鉤）。

### TRM — TR.F 16 區塊補列之真實性（親自清點 KS 全部 [N]）

**正面清點**：
* **TR.F 列數＝16**：`rg -c '^\| KS '` → **16** 列（`:428-443`），覆蓋 KS §0.6–§12 ＋ Annex DI/DO/L3U/TR·CS·EO。
* **KS 正文 [N] 章節對照**：§0.6 KS.1–5、§1 KS.6–11、§3 KS.20–26、§4 KS.30–39+CM、§5 KS.40–46、§6 KS.50–55、§7 KS.60–63、§8 KS.70–79+EV、§9 KS.80–84+CL、§10 KS.90–92、§11 KS.100–102+L56、§12 KS.110–111——與 TR.F 區塊一一對應。
* **L5 核心消費非幽靈**：KS.34/L5.3、KS.70/L5.2、KS.90–92/L5.9 等 TR.F 敘述與正文 L5.1–L5.10 交叉可讀。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L5-5 | minor | **TR.F 若干列仍留重作前歷史語（「現全缺／卻於矩陣零列／最尖銳之矛盾」）**：列已存在，惟 `:430-431`「卻整區塊缺席」、`:438`「卻於矩陣零列——最尖銳之矛盾」、`:441`「卻於矩陣零列——與正文/LDI 表自相矛盾」與現況（16 列在卷、LDI 表 `:193-201` 對齊）**字面矛盾**——[I] 可讀性／稽核误导風險（HON 族，同 L4 F-L4-7）。 | `:430-431`；`:438`；`:441` |

**出局候選**：「TR.F 仍缺 KS 整份」——3/3 出局（16 列在卷；019 決策二重作已補；`grep '^| KS'` 非零）。

### FLG — D19/D23/D25 未驗證旗標（逐列分析供裁決）

**030 覆核（不重打）**：

| 列 | TR.C 現況 | 030 裁決 | 本輪 |
|---|---|---|---|
| **D19** | `:378` **承接（空集揭露）**——rg「唯一真相」CK 全文 1 筆（本列自述） | 空集揭露 | ✅ 一致 |
| **D23** | `:381` **不觸及＋理由**（通道防護 L4/L7；L5 不觸供應商通道） | 不觸及 | ✅ 一致 |
| **D25** | `:383` **不觸及＋理由**（強制落點 L6 guard／L7.33） | 甲案 | ✅ 一致 |

**零 finding**（FLG 維；旗標已收束，非 open）。

### TER — 雙合法終點之窮盡互斥（第三終止型態攻擊）

**攻擊路徑清點**：
* **Knowledge 作終點**：L5.2 `:111-112` 判準明禁「終止於…另一未溯源結論」；KS.70 DAG＋§8.3 要求 Knowledge→Evidence→Observation／assumption 遞迴——Knowledge 非合法終點。
* **inference rule 作終點**：`:111`「推論規則…為證據鏈之一環，須可溯源」——非終點集成員。
* **Computational Evidence／model output 作終點**：L5.7 `:147-148` 要求 synthetic＋通道；須溯源至 Grading Method，非第三終點型。
* **refuted／INSUF 作終點**：屬 L_C 值域，非引用鏈終止型；CM.1 註① 雙側處理，仍掛 Evidence 鏈。
* **Observation 與 assumption 同鏈互斥**：「窮盡且互斥」指合法終點**型態集**僅二種，非禁止同 DAG 多葉各落不同型——`:112` 逐路徑判定可機械執行。

**零 finding**（TER 維；029 (ii) 核定照收，本輪未翻案）。

### EXP — L5.6 四要素與禁事後編造（神經網路情境 (iii) 推理規則）

**正面清點**：
* **四要素字面完備**：L5.6 `:139` (i)–(iv) ＋「個體層」粒度＋「不得…事後編造」。
* **L5.2 推理規則溯源**：`:111` 要求版本／產生活動／上游依據——符號推理可滿足。
* **L5.7 對 model 路徑之天花板**：TR-C／synthetic 永久——與 (ii)(iv) 銜接。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L5-6** | **medium** | **L5.6(iii)「推理規則」對非符號推理（神經網路／embedding 检索）之可判定性空檔**：`:139`(iii) 要求「所據**推理規則**（推論如何自前提得出結論）」可解析；`:111` 將 inference rule 定為可溯源之一環（版本、活動、依據）。惟 L5.7 將 NN 輸出定為 **Computational Evidence**（`:147`），未定义「權重／attention 不可讀」時何者滿足 (iii) 而**不**與 (iv) Grading Method（模型版本＋校準 provenance）**坍缩為同一項**——實務上僅能答「model X vY + 分數」，(iii) 對 NN 路徑**不可區分於**方法層，與「解釋粒度必達個體層」及 AUD-18 精神在概念層形成**可判定性张力**（029 (v) 條件通過之本輪 EXP 複核議題）。 | `:139`；(iii)；`:111`；`:147-148`；L5.7 判準 |

**出局候選**：「L5.6 完全無法解釋 NN 結論」——3/3 出局（(i)(ii)(iv) 仍可滿足；LDO.3 下放呈現；問題是 (iii) 粒度非全面落空）。

### PRV — provisional 地位之實質後果（非 provisional 下層引 provisional 上層）

**正面清點**：
* **029 解除 provisional**：【地位】`:13-16`、§0.1 `:60`、TR.Z `:447`、尾註 `:543` 一致「provisional 已解除／v1.0 生效」。
* **下游引用**：`specs/AGENT-RUNTIME-SPECIFICATION.md` 引 `AUGUR-L5 v1.0`（非 provisional 標記）——`:197` 區段親抽樣。
* **L5.10(c)「标 provisional」**：`:168` 指 as-of **宣稱**降級，非規格 provisional 態——語境不同，無冲突。
* **【地位】歷史段落**：`:14-15` 撤回／重採認史實保留——誠實揭露，非現行效力声明。

**零 finding**（PRV 維；029 條件之 ASF/PRV 複核：**未翻 major**）。

---

## 三、Verify — 三鏡獨立反駁結果

### 存活（6）

**F-L5-1【medium·存活 3/3】EO.1 缺 L5.10 謂詞**
* 文本體系鏡：**未能反駁**。L5.10 三翼判準在正文；EO.1 表無對應列；`:538` 掃描義務明確。
* 形式邏輯鏡：**未能反駁**。缺表項→as-of 相關評價句不可 EO 對表。
* 實務規避鏡：**未能反駁**。L7 as-of gate 實作不能替代 L5 概念層謂詞收錄。

**F-L5-6【medium·存活 3/3】L5.6(iii) NN 路徑粒度**
* 文本體系鏡：**未能反駁**。L5.6 要求 (iii) 可解析；L5.7 未定义 NN 之 (iii) 独立内容。
* 形式邏輯鏡：**未能反駁**。(iii) 与 (iv) 在 NN 路径可合并→四要素退化风险。
* 實務規避鏡：**未能反駁（惟界定危害）**。危害＝F5/AUD-18 在 NN-heavy 路径解释 audit 分歧；patch 可癒（概念层增「Computational 路径 (iii) 最低满足」或 defer feature attribution L7）。不足以降 minor——涉 029 (v) 条件通过核心。

**F-L5-2【minor·存活 2/3】L5.1–L5.9 enumeration 未纳 L5.10**
* 文本體系鏡：**未能反駁**（`:200` vs `:164-169` 字面差）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。LDI.5 已单列 L5.10；义务未落空。维持 minor。

**F-L5-3【minor·存活 2/3】L5.90 DRAFT**
* 三鏡同 F-L5-2 模式——v1.0 现况矛盾，一句删除「DRAFT」即癒。维持 minor。

**F-L5-4【minor·存活 2/3】CS.2 五列 DRAFT**
* 三鏡同 L4 F-L4-7 模式——029 可选顺修 residual；T-L5-6 已更新。维持 minor。

**F-L5-5【minor·存活 2/3】TR.F 历史语**
* 文本體系鏡：**未能反駁**（「零列」与 16 列并存）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。[I] 误导；[N] 义务在 TR.F 列处置本身。维持 minor。

### 出局（4，counter_evidence 留卷）

| id | 出局鏡數 | 反駁 counter_evidence |
|---|---|---|
| ASF「FM 未更新 L5.10／030 未完成」 | 3/3 | `:467` WM.D12/D13/D22/D28；LDI.5 `:199`；030 §四(e) 已施作。 |
| TRM「TR.F 仍缺 KS」 | 3/3 | 16 列 `:428-443`；KS 各 § 区块逐一覆盖。 |
| FLG「D19/D23/D25 仍 open」 | 3/3 | TR.C `:378-383` 与 030 第三点 verbatim 一致；030 已定案。 |
| PRV「下游仍引 provisional L5」 | 3/3 | L6 引 `AUGUR-L5 v1.0`；029 `:16` provisional 已解除。 |

---

## 四、Critic — 完整性批評與抽查

**「什麼還沒被檢查」（誠實清點）**：

1. **L5→L6→L7 runtime 是否真满足 L5.3 meet／L5.10 gate**——属执行层稽核，非文本 ultracode。
2. **WM.44 matrix-coverage 机械强制**（决策四第二轮）仍未建——TR.F 区块列在卷、030 D0 linter 已落地；本轮未穷举脚本。
3. **Annex TR.C WM 全块**仅 spot-check D19/D23/D25；linter 125 标签 PASS 作骨架对照。
4. **KS.83(i) 纳入语义**（L4 F-L4-3）对 L5.9 量测消费之交互——留 cross-layer 后续，本层未重开。
5. **MC v1.5 换发**——L5 mc-version 仍 v1.4（lint info）；属升版议程，非 L5 本体 defect。

**抽查推翻理由**：F-L5-2/3/4/5 之实务镜降 minor 理由经查兜底（LDI.5、029 地位、T-L5-6 已裁）实存。**F-L5-1／6 不可降级**——分别触 §8.3 EO 完备性与 029 (v) 条件通过之 EXP 复核。

**方法界限**：单代理分节；lint PASS 不阻断 F-L5-1（EO 语义超出 linter）。

---

## 五、Steward 呈核摘要

### 存活清单（medium×2＋minor×4）

| id | severity | 一句主张 | 建议处置与门槛 |
|---|---|---|---|
| **F-L5-1** | **medium** | L5.10 三翼 as-of 判准未收入 Annex EO.1，违反 `:538` 扫描完备性 | 同案 patch／minor：EO.1 增「as-of 推理合規」等 1–3 谓词（vintage≤T／入口 gate／能力等級透明），判准对齐 L5.10(a)(b)(c) |
| **F-L5-6** | **medium** | L5.6(iii) 对 NN/Computational 路径未定义可判定「推理规则」内容，(iii) 与 (iv) 可坍缩 | 同案 patch：L5.6 增Computational 路径 (iii) 最低满足（如：可重放之输入→输出映射＋模型版本，或 DEFER L7 feature attribution 并 hooks 明示）——**不升格 major**（029 (v) 已条件核定） |
| F-L5-2 | minor | LDI.6/TR.B/CS.3 仍写 L5.1–L5.9 未纳 L5.10 | 同案 [I] mechanical：改「§3–§8（L5.1–L5.10）」或「§3–§8 含 L5.10」 |
| F-L5-3 | minor | L5.90 仍标 CS 要件 DRAFT | 同案：删 `:172`「DRAFT」或改「v1.0 生效（RULING-2026-029）」 |
| F-L5-4 | minor | CS.2 T-L5-1…5 仍裸 DRAFT | 同案：状态改「已核定（029）」或删 DRAFT（同 029 (vii) 可选顺修） |
| F-L5-5 | minor | TR.F 列内「现全缺/零列」历史语与现况矛盾 | 同案 [I]：删或改述为「已补列（019 重作）」 |

### 建议同案 RULING 要点（本轮仅呈核，不开正式档）

1. **一揽子标题**：`RULING-2026-035-L5-CK-ULTRACODE-DISPOSITION`（次号 **035**；Amendment Log 建议 **AL-2026-039**——查实况：AL-038＝034、次序递增）
2. **major**：**零**——L5.10 落点、TR.F 16 块、D19/D23/D25、provisional 解除、T-L5-6 均稳；2 medium 均 patch／minor 可癒
3. **029 条件闭合**：本 ultracode 执行 PRV／ASF 复核——**未翻 major**；建议 Steward 接受呈核后 029 附条件 (v)(viii) **程序性闭合**（F-IX-4／F-IX-6 仍另案 minor，不并入本案 major）
4. **medium 同案顺修**：F-L5-1＋F-L5-6 必含；F-L5-2–5 并入同一 RULING §patch 清单
5. **独立核验**：依 RULING-2026-028 第 3 点，处置施作后交独立 agent 八项核验＋lint 亲跑
6. **Amendment Log**：`AL-2026-039`（建议序号，由 Steward 确认）

### 正面确认（强化盖章之证据）

* **ASF**：L5.10↔LDI.5↔TR.A §P4.E2↔030 FM 三向；027 编号地图 PASS。
* **TRM**：TR.F **16/16** 块在卷；KS §0.6–§12＋Annex 全覆盖。
* **FLG**：D19/D23/D25 与 030  verbatim 一致——**覆核 PASS**。
* **TER**：双合法终点＋DAG；第三终止型攻击未存活；029 (ii) 维持。
* **EXP**：四要素骨架＋禁事后编造；F-L5-6 为 NN 路径 (iii) 粒度缺口，非全面 F5 落空。
* **PRV**：provisional 已解除；L6 引 v1.0；029 PRV 条件**未翻 major**。
* **cross-layer**：KS.34 推理规则 Confidence 缺省（034）——L5.3 meet **上游已癒合**。

### 是否动摇 L5 盖章

**否——不動搖**。零 major；2 medium 均为 **EO 完备性／EXP 可判定性**（非 L5.1–L5.2 骨架、非 TR.F 缺席、非 provisional 效力）；4 minor 为 [I] enumeration／DRAFT 残留／TR.F 历史语。**動搖程度定級：僅需 patch／minor 同案處置**（非重採認、非 §8.2 补审——029 已作成）。

### 盖章 verdict

**L5（AUGUR-CK v1.0）ultracode 呈核：零 major；medium×2＋minor×4 存活；029／030 已癒合项覆核 PASS；029 PRV／ASF 条件未翻 major；lint PASS 7/7 亲跑对照。建议 Steward 接受呈核并同案 RULING-2026-035 顺修 F-L5-1–6。**

### 建议拍板句（供 Steward）

> **接受 L5 ultracode 呈核（零 major、medium×2＋minor×4）；同案 RULING-2026-035 顺修 F-L5-1（EO.1 收 L5.10 谓词）＋F-L5-6（L5.6(iii) Computational 路径可判定性）及 minor×4；029 附条件 PRV／ASF 程序性闭合（未翻 major）；F-IX-4／F-IX-6 仍另案 minor；盖章不動搖。**

### Steward 定案（2026-07-23）

**Steward 接受 L5 ultracode 呈核、同案 035**——`constitution/RULING-2026-035-L5-CK-ULTRACODE-DISPOSITION.md` 生效；Amendment Log **AL-2026-039**；CK 規格 F-L5-1～6 同案落地；029 PRV／ASF **程序性閉合**（未翻 major）；F-IX-4／F-IX-6 仍另案 minor；蓋章不動搖。**獨立對抗核驗 PASS**（2026-07-23；RULING-035 第十一節十二項全 ✅；非施作者 15f3ef1）。

---

*本報告為 [I] 審查素材；ultracode 呈核段已閉環（2026-07-23）。攻擊官／反駁官／批評官：ultracode-L5 代理（單代理分節），2026-07-23；lint PASS 7/7 親跑對照（施作後複核）。**L5 定案**：`constitution/RULING-2026-035-L5-CK-ULTRACODE-DISPOSITION.md`（2026-07-23 Steward **接受 035**；**AL-2026-039**；獨立對抗核驗 PASS 2026-07-23）。*
