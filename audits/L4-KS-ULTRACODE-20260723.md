# AUGUR-KS v1.1 單層 ultracode 窮盡對抗檢驗報告 [I]（L4）

## 一、元資料

* **日期**：2026-07-23
* **攻擊標的**：`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md`（AUGUR-KS **v1.1**，1066 行，正文 KS.1–KS.111＋Annex CM/EV/CL/DI/DO/L3U/L56/TR/CS/EO）
* **git HEAD**：`3ef5c252e8ea1547c7f776210709e31f6ea60292`
* **方法**：`ULTRACODE-SCHEDULE.md` L4 七維（LAT｜MEET｜MAP｜CL｜ASF｜SUP｜SPL）× Find→Verify→Critic→Synthesize；三鏡反駁紀律同 L0–L3（預設 refuted=true、逐字＋行號、≥2 鏡出局）。
* **對照卷宗**：`audits/L3-ID-ULTRACODE-20260723.md`（KS.23↔ID.50 下游）、RULING-2026-016／AL-2026-019（KDI.18／KS.80／KS.81(f)）、RULING-2026-027 M-IX-1（KDI.18 front-matter 簿記，**已癒合**）、RULING-2026-033（ID.50 乙案，**本輪覆核 KS.23 同步缺口**）、`audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md`（T-KS-6 先例）。
* **lint 基線（親跑）**：`python3 -m tools.constitution_lint compliance specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` → **✅ PASS（error 0 / warning 0 / info 3）**——僅作對照物，非合憲依據；info 含 mc-version v1.4→v1.5 換發提醒、WM.44 骨架覆蓋、TR 標籤 214 筆比對。
* **鐵律聲明**：[I] 審查素材；零規格修改；不採信自陳（TR.Y「缺 0 條」更正、KDI.18 承接、T-KS-6 三方文本均親讀）；處置權專屬 Steward。
* **執行形態誠實揭露**：單代理 ultracode（同 L1–L3 輪）；獨立性弱於 2026-07-18 首審之多代理形態。
* **已癒合項覆核（不重打）**：KDI.18→KS.80 增補款／KS.81(f) 正文在卷；Annex CS front-matter `defers-in` 已含 `WM.D22`（RULING-027 M-IX-1）；KDI.13／CS.3(a)／L3U provisional 列與 KS.83(i) 三向一致。

---

## 二、逐維 Find（全部候選，含事後出局者）

severity：major／**medium**／minor／info。

### LAT — L_C 偏序格形式完備性（極性非維度、DETERMINISTIC vs 禁隱含 1.0）

**正面清點（親讀）**：
* **KS.31 有界偏序格結構完備**：底錨 `INSUF`、核心全序鏈 `LOW ⊏ MODERATE ⊏ STRONG`、頂錨 `DETERMINISTIC` 逐字在（`:236-238`）；任兩值 ⊑ 可判定（`:241`）。
* **極性非 L_C 第二格軸**：`:239` 明文「refuted 純屬命題層機制，不引入 L_C 之額外維度」——與 `§P4.E8` 單一可比較性一致。
* **DETERMINISTIC vs 禁隱含 1.0**：`:238` 頂錨須可重放依據、非預設、仍 defeasible；T-KS-3（`:1019`）已誠實揭露並給緩解——非未披露張力。

**零 finding**（LAT 維）。

### MEET — meet 代數與 NoLaundering 是否真等價（多層鏈 meet、推理規則 Confidence）

**正面清點**：
* **KS.34 meet 公式與 KS.73／EV.3 雙重約束互證**：`:252-258`（Confidence meet）＋`:481`（Trust Rank meet ＋ KS.34 雙重約束）＋`:523-524`（CL.1 完備性 meet）——多層鏈遞迴 meet 精神貫穿。
* **L5 消費對齊**：`specs/COGNITIVE-KERNEL-SPECIFICATION.md` L5.3 明示聚合不得逾 meet 上限（已讀對照，非幽靈）。

| id | severity | 主張 | 證據（path:line＋逐字） |
|---|---|---|---|
| **F-L4-2** | **medium** | **KS.34 meet 公式含 `Conf(推理規則)` 但 L4 未定義推理規則之 Confidence 賦值／缺省**：`:252-255` 要求 `Conf(結論) ⊑ ⊓{ Conf(前提_i) } ⊓ Conf(推理規則)`，惟全檔無「推理規則」之 Confidence 定義、缺省值或 Grading Method 要求；Annex EO.1（`:1047-1057`）亦未收錄該謂詞。→ meet 公式**不可自足機械執行**（推理規則無 Confidence 時 meet 第二項無定義）。 | `:252-255`；`:1047-1057`（EO.1 缺列） |

**出局候選**：「多層 meet 不等價 NoLaundering」——3/3 出局（KS.34＋KS.73＋EV.3＋CL.1 同族 meet 精神；CM.2 遞迴一致性 `:323` 兜底）。

### MAP — CM 官方映射之單一輸出與洩漏（扮攻擊者找洗白路徑）

**攻擊路徑清點（構造反例）**：
* **無 Confidence→INSUF 洗白**：CM.1(a) 末列＋註②（`:299-304`）——「無原生信度類」不得逕賦高於 INSUF；註② 杜「以 TR-B 升至 STRONG」。
* **refuted 雙側**：註①（`:303`）——無否定命題裁決 Evidence 時映 `INSUF`；有則雙側處理，單一輸入單一輸出條件在卷。
* **banding 未定 L6 閾值**：CM.0（`:283`）保守解釋取 `INSUF`——攻擊者不能藉未定閾值洗白。

**零 finding**（MAP 維；CM.1 映射衝突已由註①② 機械消解）。

### CL — CL.0 vs EV.2 序方向記法相反（L6.11 序異常之源頭）

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L4-4 | minor | **Annex CL 與 Annex EV 之閉集序記法不一致**：CL.0 完備性等級用 `<` 表述由弱至強（「`E0`…＜`E1`…＜`E2`…＜`E3`」，`:520`）；KS.41 As-of Tier 同體例（`:337-342`「由弱至強」＋ A0–A3 序）。惟 EV.2 Trust Rank 序用 `⊐`（「`TR-A ⊐ TR-B ⊐ TR-C ⊐ TR-D ⊐ TR-⊥`」，`:471`）——同為「由強至弱／高至低」之單調閉集，符號不統一；L6／L7 消費雙軸時增加機械解析歧義風險（非方向相反，惟記法分裂）。 | `:520`；`:471`；`:337-342` |

**正面確認**：CL.0 四級閉集與 KS.81 六維（含 (f) 產業豁免）對映在卷；L7.45(f) 消費 `E0`–`E3` 不重定義語義——ASF 與 CL 本體一致。

### ASF — A0–A3 閉集與表級宣告

**正面清點**：
* **KS.41 A0–A3 閉集**：`:337-344` 四級＋ A0 禁止型態；`:346-348` 表級 `(a)(b)` 分類義務（KS.42）。
* **L7.20(f) 下游承接**（幽靈查證）：`specs/INFRASTRUCTURE-SPECIFICATION.md` L7.20(f) 逐字承接 KS.41／KS.42 表級宣告——非幽靈。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L4-3** | **medium** | **KS.83(i)「納入語義」自指合格、實質未定**：`:505` 稱 ID.51 三指標「本層定其於完備性等級之**納入語義**」，惟正文僅標為「完備性之個體層輸入指標」，**未**規定 unresolved backlog／latency／顯式待決存量如何映射至 E0–E3 或 KS.81(a)–(f) 維度（例：高 backlog 是否降級、是否僅 gate 消費）。可判定判準（`:507`）僅要求「納入語義**存在**」——自指循環，不可機械執行完備性合成。 | `:503-507`；`:495-497`（KS.81 維度未含 ID.51 指標） |

**info**：KS.9 §2.1 承接表（`:147-164`）未列 D12／D14／D15／D19／D22／D23，惟 KDI.0–KDI.22 與 CS front-matter 已完整——見 F-L4-5。

### SUP — Supersede 形式化與 AUD-02（KS.51 快照與 upsert 原子性）

**正面清點**：
* **KS.51 Supersede Relation 六元組結構**：`:377` 〔superseding、superseded、失效類型、Evidence、transaction time、Identity〕完備。
* **heal 覆寫語義**：`:377`「**必須**於覆寫前快照舊值並建立 Supersede Relation」——AUD-02 核心補正已形式化。
* **T-KS-4**（`:1020`）已揭露 heal／只失效不刪除張力並給 Supersede 緩解。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| F-L4-8 | minor | **KS.51 未形式化「快照＋upsert」之原子序／一致性**：`:377` 要求覆寫前快照＋Supersede Relation，惟「主路徑 upsert 不動」與快照之**先後序、失敗回滾、並發下舊值可重建**未給概念層判準——概念層可辯称執行層（L7）落地，但 `:377` 可判定判準僅「舊值可 as-of 重建」，未排除「快照失敗仍 upsert」之窗口。危害＝AUD-02 復現邊緣，非日常路徑。 | `:377-378` |

### SPL — KS.83 二事項與 T-KS-6 三方文本一致性

**正面清點（三方親讀）**：
* **KS.83 二事項分轨**：(i) 完備性輸入＋KDO.4；(ii) L5 inference＋KDO.1（`:504-506`）。
* **ID IDO.4**：仍標目標 L4（`specs/IDENTITY-SPECIFICATION.md:380`）——與 KS 定性分歧。
* **T-KS-6**（`:1022`）已列 open-tension、非豁免；KDI.13／CS.3(a)／L3U `:644` 三向一致。
* **RULING-027 M-IX-1 覆核**：WM.D22 已入 front-matter `:989`；KDI.18 `:610` 與 KS.80 增補款 `:492` 非幽靈。

| id | severity | 主張 | 證據 |
|---|---|---|---|
| **F-L4-1** | **medium** | **KS.23 仍引用 ID.50 已廢止之「provisional 旗標已清除」語義（L3 RULING-033 乙案後未同步）**：KS.23 `:208` 書「已解析 Identity（Layer 3 意義：涉該 Type 判準採認已生效 **∧ provisional 旗標已清除**，`AUGUR-ID v1.0 §ID.50`）」——ID.50 現行（post-033）逐字為「已解析」iff〔ID.20 採認已生效 **∧ 該引用非 ID.21 provisional 態〕（`specs/IDENTITY-SPECIFICATION.md:275`），**無**「旗標已清除」語。→ L4 Identity 槽「已解析」判準與 L3 權威定義**字面不同步**（雖實務近似，不可機械等同）。 | KS `:208`；ID `:275-276` |
| F-L4-5 | minor | **KS.9 §2.1 承接表為 KDI.0–KDI.22 之真子集**：`:147-164` 表缺 D12／D14／D15／D19／D22／D23（後者已於 KDI.17–KDI.22 與 CS `:989` 承接）；KS.9 判準要求「上表每列…雙向可解析」——表與 KDI.0 義務**字面不一致**（承接事實在卷，瑕在盤點表不完整）。 | `:147-164`；`:588-614`（KDI 全表） |
| F-L4-6 | minor | **TR.C Annex D 主題列文字截斷**：D4「（含 WM.3（L3）」、D6「拍板後承（L3）」、D8「embargo、p（L4）」括號未閉合（`:835-839`）——[I] 矩陣可讀性；CS.3(a) 完整。 | `:835-839` |
| F-L4-7 | minor | **§0.1／TR.Z／CS.4 仍留未 inline 修正之「形式充分性已成就／缺 0 條」字樣**：【地位】`:17` 已有 TR.Y footnote，惟 §0.1 `:68`、TR.Z `:969`、CS.4 `:1041`、尾註 `:1064` 仍裸宣「形式充分性已成就／殘餘生效阻卻已解消」——與 TR.Y `:955`「缺 0 條宣稱不實」並存；已知手工維護風險（HON 族，同 L2 CS.10 先例）。 | `:68`；`:955`；`:969`；`:1041`；`:1064` |

**出局候選**：「T-KS-6 三方文本矛盾＝漏承」——3/3 出局（T-KS-6 已登 open-tensions；KS.83(ii) DEFER KDO.1 理由在卷；ID Annex L4 `:396` 與 KS 分歧屬已揭露定性分歧，非 silent drop）。

---

## 三、Verify — 三鏡獨立反駁結果

### 存活（8）

**F-L4-1【medium·存活 3/3】KS.23 ↔ ID.50 不同步**
* 文本體系鏡：**未能反駁**。KS `:208`「旗標已清除」vs ID `:275`「非 ID.21 provisional 態」逐字不互換；033 乙案已改 ID 側。
* 形式邏輯鏡：**未能反駁**。引用 ID.50 之 KS 判準與被引條文字面矛盾→可判定性缺陷。
* 實務規避鏡：**未能反駁（惟界定危害）**。實務上近似，但稽核腳本依字面會分歧；sync patch 可癒。不足以降 minor——Identity 槽為五元組核心 gate。

**F-L4-2【medium·存活 3/3】Conf(推理規則) 未定義**
* 文本體系鏡：**未能反駁**。公式含未定義項；EO.1 無兜底。
* 形式邏輯鏡：**未能反駁**。meet 第二項無值→上限不可算。
* 實務規避鏡：**未能反駁**。L5 可能實作預設，但 L4 可判定判準要求 L4 層可解析（KS.34 `:259`「可機器稽核」）。

**F-L4-3【medium·存活 3/3】KS.83(i) 納入語義空殼**
* 文本體系鏡：**未能反駁**。`:505` 承諾「納入語義」而 `:507` 判準僅查存在性；KS.81 維度列未收 ID.51 三指標。
* 形式邏輯鏡：**未能反駁**。自指合格≠實質定義。
* 實務規避鏡：**未能反駁**。KDO.4 量測落地不能替代「指標如何影響 E 階」之 L4 語義。

**F-L4-4【minor·存活 2/3】CL／EV 序記法不一致**
* 文本體系鏡：**未能反駁**（`<` vs `⊐` 並存）。
* 形式邏輯鏡：**未能反駁**（同為全序閉集，符號不統一）。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。方向一致（弱→強／高信任→低信任），L6 已分軸消費；harm＝parser 歧義。維持 minor。

**F-L4-5【minor·存活 2/3】KS.9 表為 KDI 真子集**
* 三鏡同 F-L4-4 模式——承接在 KDI／CS，瑕在 §2.1 盤點表。維持 minor。

**F-L4-6【minor·存活 2/3】TR.C D 列截斷**
* 三鏡同 L3 F-L3-7 模式——[I] 可讀性。維持 minor。

**F-L4-7【minor·存活 2/3】「缺 0 條」裸宣稱**
* 文本體系鏡：**未能反駁**（`:68` vs TR.Y `:955`）。
* 形式邏輯鏡：**未能反駁**。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。【地位】footnote 已揭露；義務未落空。維持 minor（HON 族）。

**F-L4-8【minor·存活 2/3】KS.51 原子序未形式化**
* 文本體系鏡：**部分反駁不成立**——「覆寫前快照」已給序義務。
* 形式邏輯鏡：**未能反駁**（失敗路徑未排除）。
* 實務規避鏡：**反駁成立（僅及嚴重度）**。L7 慣例可補；概念層邊緣。維持 minor。

### 出局（3，counter_evidence 留卷）

| id | 出局鏡數 | 反駁 counter_evidence |
|---|---|---|
| LAT「L_C 非格／DETERMINISTIC 隱含 1.0」 | 3/3 | KS.31 `:236-239` 有界偏序格＋極性非維度；`:238` 非預設／defeasible；T-KS-3 揭露。 |
| MAP「CM 洗白路徑存在」 | 3/3 | CM.1 註② `:304`；KS.20 `:196` 無 Confidence→INSUF；EV.3 `:481` 雙重 meet。 |
| SPL「T-KS-6＝幽靈／KDI.18 未承」 | 3/3 | T-KS-6 `:1022`；KDI.18 `:610`＋KS.80 `:492`；front-matter `:989` WM.D22（027 已修）。 |

---

## 四、Critic — 完整性批評與抽查

**「什麼還沒被檢查」（誠實清點）**：

1. **CM.1(a) 逐列映射之領域正確性**（如「三值驗證類」映射 STRONG/MODERATE/INSUF）未做市場實務攻擊——屬領域 Profile／執行層。
2. **L5 傳播聚合算子是否真不超 meet**屬 L5 ultracode／runtime 稽核，本輪僅讀 CK 條文對照。
3. **WM.44 matrix-coverage 機械強制**（019 決策四第二輪）仍未建——TR.Y 已誠實揭露；本輪未重跑窮舉腳本。
4. **KS.84 GATE 統計治理**與 L5 provisional 交互未逐條掃描——留 L5 ultracode。
5. **Annex TR.E ID 全量**僅抽樣 ID.50／IDO.4／Annex L4 鏡像；linter 214 標籤 PASS 作骨架對照。

**抽查推翻理由**：F-L4-4／5／6／7／8 之實務鏡降 minor 理由經查兜底條文（KDI、CS footnote、L7 慣例）實存。**F-L4-1／2／3 不可降級**——分別觸 Identity 槽、NoLaundering 核心代數、完備性輸入語義，屬可判定性／同步缺陷。

**方法界限**：單代理分節；lint PASS 不阻斷 F-L4-1（跨層引用同步超出 linter）。

---

## 五、Steward 呈核摘要

### 存活清單（medium×3＋minor×5）

| id | severity | 一句主張 | 建議處置與門檻 |
|---|---|---|---|
| **F-L4-1** | **medium** | KS.23 仍寫 ID.50「provisional 旗標已清除」，與 RULING-033 乙案後 ID.50「非 ID.21 provisional 態」不同步 | 同案 patch／minor：KS.23 `:208` 改引 ID.50 現行合取式（採認生效且非 provisional 態）；可併 L3 033 後續 sync 議程 |
| **F-L4-2** | **medium** | KS.34 meet 含 `Conf(推理規則)` 但 L4 無推理規則 Confidence 定義／EO 未收錄 | 同案 patch：**(甲)** KS.34 增「推理規則 Confidence 預設＝STRONG 且須攜 Grading Method」或 **(乙)** 改公式為僅前提 meet＋明定推理規則 Confidence 由 L5 KDO.1 定義後回指；同步 EO.1 收錄 |
| **F-L4-3** | **medium** | KS.83(i)「納入語義」自指合格、未規定 ID.51 三指標如何影響 E0–E3／KS.81 維度 | 同案 patch：KS.83(i) 增 1–2 句可判定映射（例：unresolved backlog＞0 時相關 Knowledge 完備性不得高于 E1；或列為 KS.81 新維 (g)）——**數值門檻仍 DEFER KDO.4** |
| F-L4-4 | minor | CL.0 用 `<`、EV.2 用 `⊐` 記法不統一 | 同案 [I] mechanical：EV.2 改「由强至弱序 `<`」或加 cross-ref「序方向同 CL.0」 |
| F-L4-5 | minor | KS.9 §2.1 表缺 D12／D14／D15／D19／D22／D23 六列 | 同案：§2.1 表補列或改判準為「以 KDI.0 為準、本表為摘要」 |
| F-L4-6 | minor | TR.C Annex D D4/D6/D8 括號截斷 | 同案 [I] mechanical 補全 |
| F-L4-7 | minor | §0.1／TR.Z／CS.4／尾註裸「形式充分性已成就」未 inline TR.Y | 同案 [I]：加「連同 TR.Y 讀」 footnote（同【地位】`:17` 體例） |
| F-L4-8 | minor | KS.51 快照＋upsert 原子序未形式化 | 同案：KS.51 可判定判準增「快照失敗則禁止 upsert」或 DEFER L7 並 hooks 明示 |

### 建議同案 RULING 要點（本輪僅呈核，不開正式檔）

1. **一攬子標題**：`RULING-2026-0XX-L4-KS-ULTRACODE-DISPOSITION`（號碼由 Steward 次序分配）
2. **major**：**零**——L_C 骨架、CM 映射、KDI.18 承接、T-KS-6 揭露均穩；3 medium 均 patch／minor 可癒
3. **medium 同案順修**（用戶已預授）：F-L4-1＋F-L4-2＋F-L4-3 必含；F-L4-4–8 併入同一 RULING §patch 清單
4. **T-KS-6**：本 ultracode **不建議**另開 major——維持 open-tension；ID／KS 升版時對齊 IDO.4 目標 Layer 標籤屬 Steward 裁量
5. **獨立核驗**：依 RULING-2026-028 第 3 點，處置施作後交獨立 agent 八項核驗＋lint 親跑
6. **Amendment Log**：`AL-2026-038`（建議序號，由 Steward 確認）

### 正面確認（強化蓋章之證據）

* **LAT**：KS.31 有界偏序格＋極性命題層機制；DETERMINISTIC 解 AUD-03／§P4.E4 在卷。
* **MEET**：KS.34／KS.73／EV.3／CL.1 四重 meet 同族；L5.3 消費對齊（非幽靈）。
* **MAP**：CM.1(a)＋註①②；洗白攻擊路徑未存活。
* **ASF**：A0–A3 閉集＋KS.42 表級宣告；L7.20(f) 下游親讀承接。
* **SUP**：KS.51 Supersede Relation 六元組＋heal 快照義務；AUD-02 核心已形式化。
* **SPL**：KS.83(i)(ii) 分轨；T-KS-6 誠實揭露；KDI.18／027 M-IX-1 覆核 PASS。
* **defers-in/out**：KDI 18 列＋KDO 7 列＋CS front-matter 三向一致（含 WM.D22）。

### 是否動搖 L4 蓋章

**否——不動搖**。零 major；3 medium 均為**跨層同步／可判定性／語義空殼**缺陷（非 L_C 骨架、非 CM 映射、非 KDI.18 承接）；5 minor 為 [I] 記法／盤點表／TR 裸宣稱。**動搖程度定級：僅需 patch／minor 同案處置**（非重採認、非 §8.2 補審）。

### 蓋章 verdict

**L4（AUGUR-KS v1.1）ultracode 呈核：零 major；medium×3＋minor×5 存活；KDI.18／M-IX-1 已癒合項覆核 PASS；lint PASS 7/7 親跑對照。建議 Steward 接受呈核並同案 RULING 順修 F-L4-1–8。**

### 建議拍板句（供 Steward）

> **接受 L4 ultracode 呈核（零 major、medium×3＋minor×5）；同案 RULING-2026-034 順修 F-L4-1（KS.23 同步 ID.50 乙案）＋F-L4-2（KS.34 推理規則 Confidence／EO.1）＋F-L4-3（KS.83(i) 納入語義具體化）及 minor×5；T-KS-6 維持 open-tension 不另開 major；蓋章不動搖。**

### Steward 定案（2026-07-23）

**Steward 接受 034**——`constitution/RULING-2026-034-L4-KS-ULTRACODE-DISPOSITION.md` 生效；Amendment Log **AL-2026-038**；KS 規格 F-L4-1～8 同案落地；T-KS-6 維持 open-tension；蓋章不動搖。**獨立對抗核驗 PASS**（2026-07-23；RULING-034 第十二節十二項全 ✅；非施作者 3793c37）。

---

*本報告為 [I] 審查素材；ultracode 呈核段已閉環（2026-07-23）。攻擊官／反駁官／批評官：ultracode-L4 代理（單代理分節），2026-07-23；lint PASS 7/7 親跑對照（施作後複核）。**L4 定案**：`constitution/RULING-2026-034-L4-KS-ULTRACODE-DISPOSITION.md`（2026-07-23 Steward **接受 034**；**AL-2026-038**；獨立對抗核驗 PASS 2026-07-23）。*
