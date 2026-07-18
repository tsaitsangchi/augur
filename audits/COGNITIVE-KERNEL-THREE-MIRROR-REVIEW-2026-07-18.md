# L5（Layer 5 Cognitive Kernel 規格 v1.0（provisional））三鏡對抗審查——findings 冊 [I]

* **日期**：2026-07-18｜**性質**：[I] 審查報告——**本冊不修改規格一字**；任何規格變更屬 §8.6（Steward）／§8.1 解釋，一律 Steward 專屬。
* **執行**：三鏡（coherence／rigor／reality，xhigh）＋每一 major 候選雙反駁（refutes≥2 即出局）＋完備性批評。工作流 wf_5335a68e-191（Opus 4.8 完跑，112/112）。
* **意義**：L5 係弱 linter 時期充任、**內容此前從未受對抗審查**，本次為其首次內容審。

## 一、三鏡總判：coherence NO-GO／rigor NO-GO／reality NO-GO

三鏡**全部 NO-GO**。major 候選 11：**雙反駁後存活 6**／出局 5；minors 25；observations 19；完備性 gaps 9。

## 二、雙反駁後存活之 major（6 項——處置權保留 Steward）

### M1（coherence 鏡｜refutes 1/2）Annex TR TR.0／TR.C(3)（WM Annex D 覆蓋）
- **缺陷**：TR.C(3) 完全缺漏 WM Annex D 之 D1–D6 六列（無任何承接／DEFER／不觸及＋理由之處置），與 TR.0 宣稱之「Annex D D0–D28…逐條枚舉」及【地位】充任基礎「Annex TR 逐條完整枚舉、缺 0 條」直接矛盾；§WM.44 形式充分性——本次充任之唯一形式基礎——實際上缺 6 條，且此缺漏在 v0.1-draft 即存在（非 RULING-2026-016 補丁引入）。
- **證據**：L5 spec L229（TR.0）：「TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28＋HOOK-01/02/03，以十位制區塊逐條枚舉）」；L14（【地位】）：「本充任僅就 **`§WM.44` 形式充分性**（Annex TR 逐條完整枚舉、缺 0 條）」。TR.C(3) 表（L359–L370）之列僅為 D0、D7–D11、D12、D13、D14–D17、D18、D19–D21/D23–D25、D22、D26–D27、D28——D1–D6 無列。WORLD-MODEL-SPECIFICATION.md L876–L881 實有：「| D1 | Identity 實體類型完整分類體系 | L2 | WM.23 |…」「| D2 |…| L2/L3 |…」「| D3 |…| L3 |…」「| D4 |…| L3 |…」「| D5 |…| L3 |…」「| D6 |…| L3 |…」。
- **建議 remedy**：於 TR.C(3) 補列 D1–D6（處置可為「不觸及＋理由：目標 L2/L3，已由 AUGUR-ONT／AUGUR-ID 承接」，比照 D7–D11 體例），並更正【地位】「缺 0 條」敘述或由 Steward 重為形式充分性認定；依 L5.91 作 minor 升版。

### M2（rigor 鏡｜refutes 0/2）Annex TR.C(3)／TR.0／TR.Z／【地位】
- **缺陷**：TR.C(3) 表完全缺 WM Annex D 之 D1–D6 六列（表僅列 D0、D7–D28 各列），而 TR.0 自稱枚舉「Annex D D0–D28」、TR.Z 自稱「已就五上層全部 [N] 條款給出落點」、【地位】自稱「缺 0 條」。WM D0 明定「本表每列為規範性掛鉤條款」，故 D1–D6 為須有落點之 [N] 條款；WM.44 對應完備性之機器檢查即不成立，充任認定之形式基礎自陳失實。
- **證據**：L5 specs/COGNITIVE-KERNEL-SPECIFICATION.md:359-370 之 TR.C(3) 表行依序僅「D0…D7–D11…D12…D13…D14–D17…D18…D19–D21、D23–D25…D22…D26–D27…D28」，無任何 D1–D6 列；:229 TR.0「TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28＋HOOK-01/02/03，以十位制區塊逐條枚舉）」；:409「上開逐條／區塊枚舉已就五上層全部 [N] 條款給出落點」；:14「Annex TR 逐條完整枚舉、缺 0 條」。對端：specs/WORLD-MODEL-SPECIFICATION.md:876-881 存在 D1–D6（「D1｜Identity 實體類型完整分類體系｜L2…D6｜本域證券代碼身份假設之判準採認…｜L3」）、:871 D0「本表每列為**規範性掛鉤條款**」。
- **建議 remedy**：增列 D1–D6 六列（處置可為「不觸及＋理由：目標 L2/L3，已由 AUGUR-ONT／AUGUR-ID 承接」並引對方條款），同步更正 TR.Z／【地位】之完備性自陳；依 L5.91 以 minor 升版報請 Steward 補正。

### M3（rigor 鏡｜refutes 1/2）Annex TR.C(3) D14–D17 列、D19–D21／D23–D25 列
- **缺陷**：目標含 Layer 5 之 WM Annex D 列未獲 WM.44 三種合法處置（承接／DEFER／不觸及＋理由）之一：D14（WM 原文目標 L4–L5）被概括標「不觸及＋理由：各列依 Annex D 原文之目標 Layer 由對應層承接」——對 D14 而言「對應層」即本層自身，理由自我指涉、且全規格無 D14 之 L5 落點；D19／D23／D25（目標各為 L4–L7、L4–L7、L5–L7，均含 L5）明文承認「L5 承接與否未經逐列驗證」僅設旗標——旗標待裁非三種合法處置之一，矩陣就此四列不完備。
- **證據**：L5 :365「D14–D17（表徵治理下放其餘列）｜不觸及＋理由：各列依 Annex D 原文之目標 Layer 由對應層承接（原概括「目標 L2–L4」為誤植，RULING-2026-016 更正…）」；:367「D19（L4–L7 治權文件唯一真相收斂）／D23（L4–L7 供應商防護額度）／D25（L5–L7 語料隔離部署面）目標含本層——其 L5 承接與否**未經逐列驗證**（逾 016 之六列範圍），〔**旗標**：提請 Steward 另案逐列裁決…〕」。對端：WM :889「D14｜確立程序與候選斷言工作流｜L4–L5」、:894 D19「L4–L7」、:898 D23「L4–L7」、:900 D25「L5–L7」。
- **建議 remedy**：D14 比照 D13/D22/D28 體例析出改列（L5 側落點可指 L5.1 候選斷言紀律，否則載明不觸及之真實理由）；D19/D23/D25 逐列驗證後給出確定處置，未裁前於 CS.2 登錄為開放緊張關係而非僅 TR 內旗標。

### M4（reality 鏡｜refutes 0/2）Annex TR（TR.0／TR.A–TR.E）＋ CS.4 ＋【地位】
- **缺陷**：WM.44 逐條矩陣整冊漏列直接上層 AUGUR-KS：TR.0 自承五上層（含 AUGUR-KS v1.0）全部 [N] 條款均須對應，但矩陣僅有 TR.A/TR.B（MC）、TR.C（WM）、TR.D（ONT）、TR.E（ID），全文無任何 KS 逐條枚舉節或枚舉列（grep '^| KS' 零命中）；Annex TR 章題與目錄列自書「MC＋WM＋ONT＋ID → L5」。充任基礎「缺 0 條」被規格自身文本證偽——WM.44 明定「任一條款無對應且無明記者，聲明不完整，規格不生效力」。艦隊體例對照：AUGUR-L6 同型矩陣即設「### TR.E — AUGUR-KS v1.0（全部 [N]，十位制區塊）」與「### TR.F — AUGUR-L5 v1.0（全部 [N]，逐條）」（AGENT-RUNTIME-SPECIFICATION.md:395、415），證明 KS 枚舉為必備而非可省。KS 之 [N] 條款逾 60 條（KS.1–KS.111 已啟用者＋CM/CL/EV/L56/KDI/KDO 各 Annex），L5 僅經 Annex LDI 承接其中約 7 項掛鉤，其餘（如 KS.20、KS.34、KS.101、KS.102、CM.1、CL.1、EV.1–3）於 L5 無處置記錄。歷次審計（AL-2026-013 之 155 筆標籤更正、三鏡審查）均未查獲此節——linter 偽陰性先例之再現。
- **證據**：specs/COGNITIVE-KERNEL-SPECIFICATION.md:229「依 `AUGUR-WM v1.0 §WM.44`：`AUGUR-MC v1.4`、`AUGUR-WM v1.0`、`AUGUR-ONT v1.0`、`AUGUR-ID v1.0`、`AUGUR-KS v1.0` 全部 [N] 條款均須對應至本規格至少一 [N] 條款……本矩陣：TR.A（……）、TR.B（……）、TR.C（`AUGUR-WM v1.0`……）、TR.D（`AUGUR-ONT v1.0`……）、TR.E（`AUGUR-ID v1.0` ID.1–81＋IDO.0–8）」——五者名單含 KS 而節清單止於 TR.E(ID)；同檔:227「## Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT＋ID → L5）」、:42 目錄列「WM.44 逐條對應矩陣（MC＋WM＋ONT＋ID → L5）」、:476「**WM／ONT／ID 條款**：Annex TR.C／TR.D／TR.E 以十位制區塊逐條枚舉落點」（CS.4 枚舉 bullet 無 KS）、:14「Annex TR 逐條完整枚舉、缺 0 條」、:409「上開逐條／區塊枚舉已就五上層全部 [N] 條款給出落點」。WORLD-MODEL-SPECIFICATION.md:432「`AUGUR-MC` 現行版全部 [N] 條款（……Layer 2–7 規格並及其各適用上層規格之全部 [N] 條款），均須對應至作成聲明之規格至少一條 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由……任一條款無對應且無明記者，聲明不完整，規格不生效力」。AGENT-RUNTIME-SPECIFICATION.md:395「### TR.E — `AUGUR-KS v1.0`（全部 [N]，十位制區塊）[N]」、:415「### TR.F — `AUGUR-L5 v1.0`（全部 [N]，逐條）[N]」。
- **建議 remedy**：比照 L6 TR.E 體例增補「TR.F — AUGUR-KS（全部 [N]，十位制區塊逐條）」節（minor 升版、Steward 裁決）；增補前，TR.Z／CS.4／【地位】之「五上層缺 0 條」宣稱應加限定註記；並建議 tools.constitution_lint 之 WM.44 覆蓋檢查納入「各適用上層逐冊在場」之結構性斷言，堵此類整冊缺節之偽陰性。

### M5（reality 鏡｜refutes 1/2）LDI.5／L5.2（KDO.6 之 L5 面向——as-of 推理消費）
- **缺陷**：跨層承接為幽靈落點：KS KDO.6 明示將「as-of gate／purged／embargo 實作、雙時間查詢操作化」下放 L5/L7，L5 以 LDI.5 宣稱承接並指落點 L5.2「（as-of 推理消費）」，但 L5.2 之 [N] 本文全部內容為 Evidence 引用鏈雙合法終點與禁循環（DAG），零字提及 as-of／gate／purged／embargo／雙時間；L5.1–L5.9 全部條款本文亦無任何 as-of 消費義務句。MC §P4.E2（雙時間性）之 L5 處置（TR.A 列）與 WM.30–31／HOOK-01 之 L5 處置（TR.C 列）均繫於同一空落點。即「代號在場≠義務對應」之 D3 型缺陷（RULING-2026-010 主文三所名之幽靈引用）再現於本層最安全關鍵之防洩漏（anti-leakage）紀律：推理側「僅得消費 as-of ≤ t 已知 Knowledge」之義務於 L5 無任何可稽核條款，L7.20 僅承物理查詢引擎面，推理消費面全鏈懸空。
- **證據**：specs/COGNITIVE-KERNEL-SPECIFICATION.md:109 L5.2 全文「每一 Inference 結論**必**產生（或引用）一 Evidence 節點；其引用鏈**必**遞迴終止於二合法終點之一：**對 Reality 之 Observation**，或**明示宣告之假設**……**禁循環引證**……」（無任何 as-of 內容）；:189「**LDI.5** | `AUGUR-KS v1.0` KDO.6 | as-of gate／purged／embargo 之查詢引擎操作化（L5 面向） | L5.2（as-of 推理消費）（＋轉 LDO.5 之 L7 面向）」；:239「§P4.E2（Time（雙時間性）） | L5.2（as-of 推理消費）；查詢引擎操作化 DEFER（LDO.5） | 承接＋DEFER」；:353「HOOK-01（anti-leakage……） | L5.2（as-of 推理消費）……—承接＋DEFER」。KNOWLEDGE-SYSTEM-SPECIFICATION.md:623「**KDO.6** | KS.44 | as-of gate／purged／embargo 實作、雙時間查詢操作化 | L5/L7 | `§P4.E2`」、:355「發布日 gate、purged／embargo、point-in-time 取版為其**實作機制**，DEFER Layer 5/7（KDO.6）；本層定判準與能力等級，不定實作」。
- **建議 remedy**：於 L5.2 增列（或新啟用保留號如 L5.10）一款 [N] 義務：Inference 於回溯／as-of 脈絡僅得消費該 as-of 時點合法可知之 Knowledge（承 KS.44 判準、KS.41 能力等級），附義務主體與可判定判準（結論之 Evidence 鏈上任一節點之可知時點晚於宣告 as-of 時點者違反）；LDI.5／TR.A §P4.E2／TR.C HOOK-01 各列落點隨改。屬 minor 升版、Steward 裁決。

### M6（reality 鏡｜refutes 1/2）Annex TR.C(3) D19／D23／D25 列 vs TR.Z／CS.4／【地位】
- **缺陷**：三列 WM Annex D 掛鉤（D19 目標 L4–L7、D23 目標 L4–L7、D25 目標 L5–L7——目標均含本層）現行處置為「承接與否未經逐列驗證＋旗標提請 Steward 另案裁決」，此非 WM.44 三種合法處置（承接／DEFER／不觸及＋理由）之任一；尤其 D25（語料隔離之機器強制，WM A.16/A.44 明文 DEFER Layer 5–6）於 L5 全文無「語料」「隔離」任何落點。同檔 TR.Z 卻宣稱「已就五上層全部 [N] 條款給出落點」、【地位】稱「缺 0 條」——同一生效文本內自相矛盾，WM.44 完備性之機器稽核於此三列必 FAIL。旗標雖屬誠實揭露（RULING-2026-016 界外登錄），但完備性宣稱未同步加限定，且另案裁決迄今（2026-07-18）未作成。
- **證據**：specs/COGNITIVE-KERNEL-SPECIFICATION.md:367「**D19（L4–L7 治權文件唯一真相收斂）／D23（L4–L7 供應商防護額度）／D25（L5–L7 語料隔離部署面）目標含本層**——其 L5 承接與否**未經逐列驗證**（逾 016 之六列範圍），〔**旗標**：提請 Steward 另案逐列裁決，比照 D13/D22/D28 體例〕」；同檔:409「上開逐條／區塊枚舉已就五上層全部 [N] 條款給出落點（承接／細化／DEFER／不觸及＋理由）」、:14「Annex TR 逐條完整枚舉、缺 0 條」。WORLD-MODEL-SPECIFICATION.md:894（D19，目標 L4–L7）、:898（D23，目標 L4–L7）、:900「| D25 | 語料隔離之機器強制；自有私有內容授權邊界之部署落實（含本地部署拓撲） | L5–L7 | A.16、A.44 | `AUGUR-MC v1.4 §P4.E7` |」；A.16:532「隔離之機器強制機制 DEFER Layer 5–6」。grep 證：L5 全文零命中「語料」「隔離」。
- **建議 remedy**：Steward 依旗標所請另案逐列裁決 D19/D23/D25 之 L5 面（比照 RULING-2026-016 六列體例）；裁決作成前，TR.Z／CS.4／【地位】之完備宣稱加限定註記（「除 D19/D23/D25 待裁三列外」）。D25 之 L5 面（推理側不得消費隔離語料為 Evidence）預期需實質條款，非純文書。

## 三、雙反駁出局之 major 候選（5 項，存查）

- ~~[coherence｜refutes 2/2]~~ L5.2／Annex LDI LDI.5／Annex LDO LDO.5／TR.A §P4.E2 列／TR.C WM.30–31 列／HOOK-01 列：KS KDO.6（as-of gate／purged／embargo 實作、雙時間查詢操作化，目標 L5/L7）之 L5 面向宣稱承接於「L5.2（as-of 推理消費）」，但 L5.2 全文為引用鏈雙合法終點與 DAG…
- ~~[coherence｜refutes 2/2]~~ 【地位】節（變更範圍自陳）／TR.0 更正記錄／版本欄：【地位】宣稱 draft→v1.0 變更僅限三項且「無任何 [N] 條款實質變更」，但實際 diff（扣除 MC v1.3→v1.4 版號替換後仍 119 行）含：§0.1 生效要件改寫、TR.A／TR.B／TR.C(1…
- ~~[rigor｜refutes 2/2]~~ Annex LDI LDI.5／L5.2／TR.A §P4.E2 列（暨 TR.C WM.30–31、HOOK-01、D22 列）：KDO.6 下放之「as-of gate／purged／embargo 查詢引擎操作化（L5 面向）」承接名實不符：全文六處皆稱落點為「L5.2（as-of 推理消費）」，但 L5.2 正文（引用鏈雙終點／DAG／最弱環…
- ~~[rigor｜refutes 2/2]~~ L5.6／Annex EO EO.1：「不得由生成模型事後編造」為 MUST NOT 而無判定程序：L5.6 自附判準僅測「可解析至四要素」與個體層粒度，未測解釋與該結論實際留痕推導鏈之綁定——生成模型可編造出形式上可解析至四要素之解釋而非真實依據；「真實依…
- ~~[rigor｜refutes 2/2]~~ Annex LDO LDO.4／LDO.0／L5.9／Annex LDI LDI.4：defers-out 自指：LDO.4 目標 Layer 欄為「L5／L7」，而 LDO.0 定義下放為「本層明示不定義該實作事項，授權並要求目標 Layer 定義之」——本層宣告不定義並授權自己定義，自相矛盾；KDO.…

## 四、完備性批評 gaps（下一輪工作來源）

- **未讀檔案 · L5.6【承接審計 AUD-18】之現實對應面（audits/VERIFICATION-2026-07-16-wf_94841fac.json）**：三鏡 coverage 僅列讀 CODE-COMPLIANCE-AUDIT 內 AUD-18 條目，無一鏡讀該對抗驗證卷宗。JSON 內 AUD-18（id:301/:573；overall:642）之驗後裁斷為：per-pick 特徵貢獻分解『為 MC 全文未課予之義務』、『P4.E1 五元組與 P4.E6 四要件均不含內部歸因分解要件』、AUD-18『近於無違反、僅為防護性缺口』；audit 本身(:535)亦定『F5/P4.E6 構成要件未該當，應改寫為解釋粒度未操作化之缺口而非違反語氣』。而 L5.6(:137-138) 將此降級發現硬化為 [N] MUST（『解釋粒度必達個體層…僅止於方法層者違反本條』），並以『承接審計 AUD-18』為憲章錨。L5.6 核心義務所據之審計，已被同倉對抗驗證判為非憲章義務，此對應面全未比對，屬可升 major 之落點（憲章據不成立而課 MUST）。
- **版本接縫 · L5 綁定 AUGUR-KS v1.0，但 D22 承接端點 KS.80 增補款／KS.81(f) 僅存在於 KS v1.1**：L5 檔頭(:7)、§0.1(:57)、CS front-matter upper-specs(:424) 皆綁定 AUGUR-KS v1.0；但 TR.C(3) D22 列(:368) 承接（計算面）明引『承 AUGUR-KS v1.1 KS.80 增補款下放』。KS 檔頭(:5)載 KS.80 增補款＋KS.81(f) 係 v1.1（RULING-2026-016）新增、v1.0 不存在。RULING-2026-016(:46) 已親認此為『時代錯置』並改 D22 列版號為 v1.1，卻未同步 L5 之 upper-specs／檔頭綁定版本——故 L5 承接一個不在其所綁定 KS 版本內之下位條款。三鏡以『版號依 RULING-2026-018 齊一、非 finding』略過，未辨識此具體懸空跨版承接（下放實體 KS:490 確在，唯 L5 綁定版本與承接端點版本不一致，為可稽核 diff 缺陷）。
- **充任基礎未驗 · 實跑 linter 揭 PASS 為偽充分（三鏡自陳未讀 linter／report 輸出）**：本席 read-only 跑 tools.constitution_lint compliance 於 L5：✅PASS（error 0/warning 17）。但此 PASS 恰不覆蓋 L5 核心承接鏈：(a) linter 解析 AUGUR-WM 29/ONT 6/ID 10/MC 55＝100 筆標籤，AUGUR-KS 0 筆——因 TR 矩陣根本無 KS 區塊（印證『漏列 KS 整欄』major），linter 對此為 false-negative、不報 error；(b) IDO.1–IDO.8（含核心 IDO.4→L5.9）全標『本次未受檢——AUGUR-IDO 未見於 upper-specs 可解析清單』；(c) WM.44 warning『16/102 條 MC [N] 條款未於聲明文本出現（樣本 §2.1/§2.2/§2.3/§2.4/§2.10…）』僅 WARNING 不阻斷。故【地位】(:14) 所據充任要件『§WM.40–43 linter PASS、error 0』其覆蓋面正好排除 L5 賴以成立之 KS KDO／IDO.4 承接——linter 偽陰性使充任形式關卡形同虛設；三鏡未執行工具故未觸及此空洞（且 linter 訊息仍引 AUGUR-MC v1.3，工具未同步 v1.4）。
- **治權記錄未採信 · AL-2026-019 附錄乙對【地位】『變更僅限』虛假性之權威認定**：三鏡其一 coverage 讀『AMENDMENT-LOG AL-2026-019 相關段』，但未引附錄乙認定（constitution/AMENDMENT-LOG.md:157）：該處逐字親查五份【地位】『變更僅限三項』清單，明認『因本次執行而變為不實…§0.1／檔頭從屬聲明／TR.0／TR.Z／Annex CS 前言／CS front-matter upper-specs／CS.4 自查段／文末總計段均另改，故僅限三項之陳述已為偽』。此為治權記錄對 L5【地位】(:15) 虛假性之獨立、非版號理由之坐實。三鏡將『變更僅限 vs 實際 diff』major 之一裁 survives:false（歸因 MC v1.3→v1.4 版號替換），未據附錄乙復核——欠驗，該 major 實有權威記錄支撐、不應被駁。
- **TR.E 標籤失真 · IDO.7 目標實為 L6，L5 列誤標為 L4（linter 已標此列未受檢）**：L5 TR.E(:404) 將『IDO.7–IDO.8（唯一權威 Representation 指定→L4）』併列，處置『不觸及＋理由：目標 L4』。但 ID Annex DO 原文：IDO.7(:383)＝自然人法規對應表本體與其授權、**目標 L6**；IDO.8(:384)＝唯一權威 Representation 指定、目標 L4。L5 之併列標籤取 IDO.8 內容與目標(L4) 蓋住 IDO.7，使 IDO.7『目標 L4』理由為假（實 L6）。此與六列案(:135) 已就 L6 TR.D 更正之同型誤述（『原列理由對 IDO.7 為誤述』）完全同病，但 L5 TR.E 之同誤未獲更正；linter 因 IDO 列『未受檢』無法捕獲。WM.44 要求『不觸及＋理由』須機器可判為真，IDO.7 之假理由使該列不合格——與 D19/D23/D25、D14–D17 假概括理由 major 同類，三鏡之 majors 未將此延伸至 TR.E。
- **D22 計算面軟落點未逐列驗 · 『不另立新條』泛引 L5.2／L5.3 與 as-of 幽靈落點同型**：TR.C(3) D22 列(:368) 承接（計算面）稱『成員資格衍生計算為本層 inference…受 L5.2（as-of 消費）、L5.3（Confidence 傳播）既有紀律約束，不另立新條』。但 L5.2 正文(:108-110) 為引用鏈雙終點/DAG、L5.3(:117) 為 Confidence meet 上限，皆無一字及『成員資格／完整性 gate／流動性分位地板』之衍生計算——與已 survives 之 KDO.6→L5.2『as-of 推理消費』幽靈落點同型（承接名實、落點為泛引非專條）。ops/ANNEXD-SIX-ROWS-CASE(:5) 明載 D22 義務『活在 code(core_gate) 而概念層無落點——實作先行於規格之反向缺口』；L5 側僅以泛引兜底、無專條承接，此反向缺口在 L5 面未被三鏡逐列驗證。
- **現實對應面（augur-code）未比對 · L5.1/L5.6 MUST vs 生產碼、waivers:[] 無過渡條款**：任務明列之 /home/giga/augur/augur-code 在場（src/augur/models/ranker.py、evaluation/deflation.py 均實存）。VERIFICATION(:307) 親測 AUD-18『於現行 HEAD 仍然成立』（ranker.py:8『SHAP/可解釋明訂不在此層』逐字重現），AUD-03 五元組系統性缺陷為 critical。L5 以 waivers:[]（CS:427）、無任何過渡條款、【地位】(:16) 自生效日即對 L6–7 生規範效力，而生產碼現不滿足 L5.1 五元組／L5.6 per-個體層解釋 MUST。三鏡僅一鏡淺 grep deflation.py，未比對 ranker.py:8 與 L5.6 MUST 之直接衝突；此『概念層即時 MUST vs 生產不合規且無過渡』縫僅被列為 minor 未展開，屬現實對應面欠比對。
- **下位 DEFER 端點三鏡全未追（本席補驗：除 LDO.4 自指外皆成立）——coverage 空白補實**：三鏡 coverage 均未含 L5 defers-out（LDO.1/2/3/4/5/6）向 L6/L7 承接端點之親驗。本席補驗：L7.11(:147)/L7.30(:320)/L7.50(:506) 承接 LDO.1；L7.20(:224) 承接 LDO.5；L7.26(:294) 承接 LDO.4 之 L7 面；L7.43(:414) 承接 LDO.3；L6 LDI.1(:251)/LDI.2(:252) 承接 LDO.6/LDO.2——向下鏈完整成立。唯一殘缺為 LDO.4 目標欄含『L5』之自指（已知 major），其 L7 面已由 L7.26 正確承接、L5 面自指仍懸。此項非新缺陷，但補實三鏡未驗之向下 DEFER 覆蓋空白。
- **上層本體語義未讀 · TR.D/TR.E『不觸及＋理由』僅驗編號完整、未驗語義正確**：本席已驗 TR.D/TR.E 之區塊枚舉數字完整（ONT.1-13/20-22/30-31/40-41/50/60-62、T.0-6/20-36/40-44/50-53/60-61/90-91、ID.1-4/10-14/20-24/30-32/40-44/50-53/60-61/70-71/80-81、IDO.0-8 全數落入 L5 區塊，無漏號）；但三鏡自陳『ONT/ID 正文語義細節未讀，僅以條款號存在性驗落點自洽』。故各區塊『不觸及＋理由：屬型別層／個體層本體、L5 消費不重定義』之語義正確性（是否確無以 L5 為落點之隱藏承接）未經逐條語義親驗——此範圍內若有以 L5 為落點之條款被概括『不觸及』誤蓋（如 IDO.7 之例已證同型錯誤存在），三鏡無法排除。

## 五、minors／observations 摘要

- [minor｜coherence] 檔頭／§0.1／§0.5／Annex CS front-matter vs TR.C(3) D22 列：全文綁定與引用格式均釘死「AUGUR-KS v1.0」（upper-specs 欄同），但 D22 列之承接依據為「AUGUR-KS v1.1 KS.80 增補款」——同一文件內 KS 版號兩用；KS…
- [minor｜coherence] TR.C(3) D22 列 vs Annex LDI／CS.3(a)／front-matter defers-in：D22 之「承接（計算面）」為對 KS v1.1 新下放之承接，但 Annex LDI 無對應列、CS.3(a) 未列、front-matter defers-in 欄未列——違 LDI.0「本表每列…
- [minor｜coherence] Annex LDI LDI.4 vs front-matter defers-in／AUGUR-ID IDO.4 目標欄：LDI.4 承接來源並列「AUGUR-ID v1.0 IDO.4」，但 (a) front-matter defers-in 與 CS.3(a) 均無 ID.IDO.4，三向可解析（LDI.0）破；(…
- [minor｜coherence] Annex LDO LDO.4（目標 Layer 欄）：defers-out 表（「下放**下層** DEFER 掛鉤」）之 LDO.4 目標 Layer 為「L5／L7」——含本層自身之自指下放，與 LDO.0「授權並要求目標 Layer 定義之；目標 …
- [minor｜coherence] TR.C(3) D14–D17 列（三分互斥）：D14–D17 整列標「不觸及」，但 WM D14 目標為 L4–L5、D15 目標為 L4–L6——均含本層；且 D14 之 L5 面向實際上經 KS KDO.3（授權欄明列 §D14）由 L5.5…
- [minor｜coherence] L5.90／L5.9／CS.2／TR.Z 節標題（殘留 DRAFT 標記）：v1.0 已生效文件內殘留多處 DRAFT 標記，與【地位】生效敘述及 CS.4「殘餘生效阻卻已解消」矛盾；TR.Z 節標題「殘餘生效阻卻（DRAFT）」更與其條款標題「充任認定已成就」同節互斥。…
- [minor｜coherence] TR.A §P4.E3 列（L5.5(c) 懸空引用）：引用「L5.5(c)」，但 L5.5 全文無 (a)/(b)/(c) 子款編制——子款引用懸空。…
- [minor｜coherence] L5.9／CS.2 T-L5-6 vs RULING-2026-006：L5.9 載「此定性待 Steward 於充任認定時一併裁定」，惟充任裁決（RULING-2026-006）並未裁定 T-L5-6，反而明文將其保留於嗣後 §8.2 審查——條款預設之裁定時點已過而未…
- [minor｜coherence] Annex EO EO.1（掃描—完備性義務）：「刪名測試」為本層操作化之評價性謂詞（【地位】以其為全文合規宣稱、T-L5-1 以其為緩解判準），惟未收錄於 EO.1 表；依 EO.1 自身判準（未收錄且未附表列判準者採保守解釋）表列完備性不成立。…
- [minor｜rigor] §0.1／【地位】／Annex CS front-matter vs TR.C(3) D22 列；L5.91：上層版本基礎不一致：受約束宣告與 upper-specs 欄均為 AUGUR-KS v1.0，但 D22 之承接依據為僅存在於 v1.1 之「KS.80 增補款」——承接依據落在本規格宣告拘束範圍之外…
- [minor｜rigor] Annex CS front-matter defers-in／LDI.0／CS.3(a)：DEFER 簿記三向可解析失敗：LDI.4 承接來源含 AUGUR-ID IDO.4、TR-D13 列宣稱部分承接（落點 L5.1/L5.6）、TR-D22 列宣稱承接（計算面）——三者均不見於 fr…
- [minor｜rigor] Annex TR.A §P4.E3 列：懸空內部引用：引「本層 L5.5(c)」，但 L5.5 為單段條文、無 (a)(b)(c) 分項（(a)(b)(c) 結構存在於 AUGUR-KS KS.84）；該列之機器對表無從解析。…
- [minor｜rigor] L5.5／Annex EO EO.1「無證升級」列：「經濟裁決」承重而無判準：L5.5 與 EO.1 以「GATE 成就（OOS＋經濟裁決／預註冊可證偽）」為升級禁令之機器判準要件，惟「經濟裁決」於本層未定義、未收錄 EO.1、亦未顯式 DEFER（W…
- [minor｜rigor] TR.Z／L5.90／L5.9／CS.2：生效地位標記自相矛盾（stale DRAFT）：TR.Z 標題仍稱「殘餘生效阻卻（DRAFT）」而其本文與 CS.4 稱「殘餘生效阻卻已解消」；L5.90 仍載「惟 Steward 充任認定另為裁決要…
- [minor｜rigor] §0.5 三態標注 vs L5.1／L5.4／L5.6 條頭：標注體例不合自訂規則：§0.5 定「承接」僅用於標「Layer 4（AUGUR-KS）明示下放本層之掛鉤」，然 L5.1「承接｜KS.20、KS.30」（KS.20 之 hook 目標 L7 非本層）…
- [minor｜rigor] L5.3：KDO.1 聚合語義承接名實部分不符：條頭與正文自稱「定義 Confidence 傳播之具體**聚合語義與推論實作**（含多獨立證據之增強等聚合算子）」，但全條僅載 meet 上限與 Grading …
- [minor｜reality] Annex LDI／CS.3(a)／CS front-matter defers-in vs TR.C(3) D13／D22／D28：RULING-2026-016 於 TR.C(3) 改列 D13（承接（部分））、D22（承接（計算面））、D28（承接界分）後，未同步於 Annex LDI 增列對應承接列、未鏡射於 CS.3(a)…
- [minor｜reality] 檔頭第 7 行／§0.1／CS front-matter upper-specs vs TR.C(3) D22 列：上層 KS 版號失同步且同檔自相矛盾：檔頭、§0.1、CS front-matter 均載 AUGUR-KS v1.0，而 TR.C(3) D22 列自引「AUGUR-KS v1.1 KS.80 增補…
- [minor｜reality] L5.9／L5.90／TR.Z 章標／CS.2 各列（DRAFT 殘留族）：生效本 [N] 區段殘留 9 處「DRAFT」現時態記述，與 v1.0 生效地位矛盾（§8.2 較嚴格解讀將以 DRAFT 勝出）；其中 L5.9「此定性待 Steward 於充任認定時一併裁定」之條…
- [minor｜reality] TR.A §P4.E3 列：引用不存在之條款分款「L5.5(c)」：L5.5 為單一段落、無 (a)/(b)/(c) 分款，機器解析該落點必失敗（懸空內部引用）。…
- [minor｜reality] TR.C(3) D14–D17 概括列（就 D14 部分）：D14（確立程序與候選斷言工作流）之 WM 原文目標為 L4–L5——L5 本身即目標層，概括列仍標「不觸及＋理由：各列依 Annex D 原文之目標 Layer 由對應層承接」，對 D14 而言此理…
- [minor｜reality] LDI.4 vs CS front-matter defers-in／CS.3(a)：LDI.0 自訂之三向可解析判準對 LDI.4 失敗：LDI.4 承接來源欄含 AUGUR-ID v1.0 IDO.4，但 front-matter defers-in 與 CS.3(a) 均無 ID…
- [minor｜reality] L5 全文 vs AUGUR-KS CM.0（Layer 5 審議 verdict 之映入）：跨層期待懸空且現實已露裂：KS CM.0 明文「Layer 5 於其規格承接後，自行將其 verdict 依 CM.1(a) 抽象類映入本層 L_C」，L5 規格全文無任何審議 verdict→L_C…
- [minor｜reality] §0.1 版本欄 vs RULING-2026-016／AL-2026-019 之 TR 補正：同一裁決（RULING-2026-016）使 KS 升 v1.1、L6 升 v1.2 並均於版本欄記載沿革，L5 之 TR.C(3) 同案受實質補正（D13/D22/D28 改列、D19–D25 拆分…
- [minor｜reality] L5.1／L5.3／L5.6 可判定判準 vs 現行生產現實（無過渡條款、waivers: []）：義務即日全面 FAIL 而無治癒路徑之明文：L5.6 判準（每一結論可解析四要素、可逐筆機器盤點）對現行生產為全數違反（AUD-18：per-pick 解釋面缺席、誠實答案僅「模型分數高」）；L5.3…

- [obs] TR.C(3) D19/D23/D25 列自承「其 L5 承接與否**未經逐列驗證**（逾 016 之六列範圍），〔旗標：提請 Steward 另案逐列裁決〕」（L367）——誠實揭露值得肯定，但這意味生效版 WM.44 矩陣對三列無定論處置，與「缺 0 條」宣稱進一步不符；應併
- [obs] L5 自我定性為「概念層與執行層之交界」並引 `AUGUR-MC v1.4 §0.6(b)` 為據（L21、L80），但 MC §0.6(b) 原文為二分：「Layer 1–4（概念層）之規格不得引用 Layer 5–7（執行層）之構件作為定義依據」（MC L65）——L5 依 
- [obs] KS CM.0 明文預期「Layer 5 於其規格承接後，自行將其 verdict 依 CM.1(a) 抽象類映入本層 L_C」（KS L277），惟 L5 全文無任何條款處理 L5 審議 verdict（如 GATE verdict 具名狀態）→L_C 之映射義務；L5.3 之
- [obs] 查核為真之項目（防重複誤報）：L5.6／TR.A 之「§P4.E1 五問」引用正確——MC P4.E1 原文確含「此為任何 Knowledge 必須能回答之五個問題（來源為何／何時成立／關於哪個 Identity／依據為何／多可信）」（MC L309）；TR.D 區塊範圍與 ON
- [obs] RULING-2026-016 對本規格之補丁品質整體良好（D13/D22/D28 析出改列與 WM 原文目標欄逐一吻合、AUGUR-L6 L6.19/L6.21 增補款經親驗存在且實質承接 D13/D28），缺陷集中在版本紀律（major#3）而非補丁內容。
- [obs] TR.E 以區塊過度枚舉不存在之條款號：AUGUR-ID 實無 ID.5、ID.15、ID.25、ID.45（實際為 ID.1–4、10–14、20–24、40–44），TR.E 列「ID.1–ID.5」「ID.10–ID.15」「ID.20–ID.25」「ID.40–ID.45
- [obs] CS.4 MC 覆蓋清單（:478）粒度不一：§0.1–§0.6、§8.1–§8.6 逐一具名，而 §2.1–§2.11 僅以章級「§2」概括（TR.B 另列 §2.5/2.6/2.7/2.10/2.11）；依 MC §0.3 條款編號系統 §2.{n} 為獨立條款編號，宜補齊具
- [obs] 「由本層落地」「僅實作演算」語式（L5.5 :129、LDI.3 :187）將規格規範義務與 runtime 行為混同——概念層規格文件無從『實作演算』；GATE 統計計算之規範內容實際僅餘「載明多重比較調整」一項判準（家族錯誤率演算、二次證偽封鎖演算之合法性判準均未見），與 §
- [obs] L5.7 之「高風險 Action」判準鏈已驗證閉合：EO.1 末列誠實標「DEFER Layer 6 風險分級表（LDO.2）；本層不判定」，且 AUGUR-L6 v1.2 L6.10 已定 RT-0–RT-4 分級表並經 LDI.2 承接 L5 LDO.2——此為正常 DEF
- [obs] L5.7 天花板引用與 KS 一致（EV.2：TR-C 校準模型輸出→至 MODERATE），惟其判準「映入 L_C 逾 TR-C 天花板…違反」對『無校準 provenance 之 model output』偏寬——依 KS EV.2 該類落 TR-D（至 LOW），L5.7 
- [obs] L5.2 將 MC §P4.E6 之二終點細化為「窮盡且互斥」——MC 原文未言窮盡互斥，此為向嚴細化（許可較少），方向合法。
- [obs] 本審依指示為唯讀：未執行 linter、未驗證【地位】所稱「linter 結構關卡 PASS、error 0」之工具面自陳。
- [obs] 現實承載正向確認：LDI.3（GATE 統計計算實作）於實作 repo 已有真實著落——augur-code/src/augur/evaluation/deflation.py 實作 Deflated Sharpe（Bailey-LdP 2014 口徑、per-period、N 
- [obs] L5.6 對 AUD-18 之轉述與審計原文相符（audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md:351–359 逐字核對：per-pick 解釋面缺席、ranker.py:8「SHAP/可解釋明訂不在此層」、RankRidge 係數分解零推
- [obs] LDO 下放鏈端點多數健在：LDO.1→L7.30（INFRASTRUCTURE:320–321 明文承接）、LDO.2→L6 LDI.2/LDI.3（AGENT-RUNTIME:252–253）、LDO.4→L7.26、LDO.5→L7.20、LDO.6→L6 LDI.1（AG
- [obs] LDO.4 目標欄「L5／L7」以本層為自身下放目標（specs/COGNITIVE-KERNEL-SPECIFICATION.md:205），承 KS KDO.4 同字樣（KNOWLEDGE-SYSTEM:621）——自我下放於 LDO.0 語義（授權並要求目標 Layer 定
- [obs] MC 逐字引文抽核全數屬實：§2.7「產生新斷言或行動方案之任何過程」（META-CONSTITUTION:143）、§2.11 EV.2–EV.5 通道（:147）、P4.E6 雙合法終點（:315）、§8.3 末項引用鏈可機器稽核句（:506）、§5 角色四（:421）、§0
- [obs] RULING-2026-006 為形式關卡充任、§8.2 延後，其保留清單明列 L5.1/L5.2/L5.3/L5.4/L5.6/L5.7 與 CS.2 六緊張（尤 T-L5-6）——本審即 §8.2 深度實質審查之償還；majors 第 1、2 項均屬形式綠燈與實質缺口並存之型
- [obs] ops/phase1（owner separation SQL 與執行記錄）與 ops/phase2（P5 送件）均屬 L6/L7 域施工，經檢視無 L5 規格斷言之證偽或承接事項；audits/MC-THREE-MIRROR、WM-THREE-MIRROR、L7-REREVIE

## 六、對「L5 完成」之判定

**L5 首次對抗審查未通過（三鏡皆 NO-GO）。** 存活 major 6 項集中於 WM.44 形式充分性矩陣（Annex TR）之枚舉缺口——【地位】宣稱『五上層全部 [N] 逐條枚舉、缺 0 條、形式充分性已成就』與 grep 實測矛盾，屬**生效要件級**斷點。 本層之形式充分性自證既受質疑，**其充任生效記錄宜提請 Steward 依 §8.2 覆核**；remedy 多為 patch–minor 級文本修繕，惟修繕前『形式充分性已成就』之陳述不成立。

*配套草案：RULING-2026-019-DRAFT（呈 Steward 就 L2–L6 首審 findings 一次處置）。*