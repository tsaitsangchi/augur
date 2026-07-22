# L3（Layer 3 Identity 規格 v1.0）三鏡對抗審查——findings 冊 [I]

* **日期**：2026-07-18｜**性質**：[I] 審查報告——**本冊不修改規格一字**；任何規格變更屬 §8.6（Steward）／§8.1 解釋，一律 Steward 專屬。
* **執行**：三鏡（coherence／rigor／reality，xhigh）＋每一 major 候選雙反駁（refutes≥2 即出局）＋完備性批評。工作流 wf_5335a68e-191（Opus 4.8 完跑，112/112）。
* **意義**：L3 係弱 linter 時期充任、**內容此前從未受對抗審查**，本次為其首次內容審。

## 一、三鏡總判：coherence NO-GO／rigor NO-GO／reality NO-GO

三鏡**全部 NO-GO**。major 候選 9：**雙反駁後存活 1**／出局 8；minors 22；observations 27；完備性 gaps 11。

## 二、雙反駁後存活之 major（1 項——處置權保留 Steward）

### M1（coherence 鏡｜refutes 1/2）Annex TR（TR.0、TR.C、TR.D、TR.Z）＋【地位】＋CS.4——「三上層全部 [N] 條款逐條完整枚舉、缺 0 條」之宣稱
- **缺陷**：計數與實列不符（WM.44 生效要件層級）：TR.C 僅枚舉「WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28」，漏列 AUGUR-WM v1.0 之 [N] 條款 Annex E §E1 與 Annex C §C.1–C.10；TR.D 僅枚舉「ONT.1–62＋Annex T」，漏列 AUGUR-ONT 之 [N] 條款 DI.0–DI.3、DO.0–DO.4、TM.0、EO.1、Annex L3、Annex CS（DO.0 且被 ID.3 引為錨定，卻仍無矩陣列）。全文對 DI.{n}／EO.{n}／TM.{n}／§E1／§C.{n} 零提及、零處置（無對應、無 DEFER、無「不觸及＋理由」）。而 WM.44 明文要求「並及其各適用上層規格之全部 [N] 條款」逐條處置，且 WM §0.3、ONT §0.3 均將上開前綴列為正式條款編號系統。「缺 0 條」之機器可判宣稱為偽。
- **證據**：IDENTITY-SPECIFICATION.md L17：「Annex TR（TR.A–TR.Z）就三上層…全部 [N] 條款逐條完整枚舉、缺 0 條」；L406（TR.0）：「本矩陣已就三上層規格全部條款逐條完整枚舉…TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28 逐條）、TR.D（`AUGUR-ONT v0.1-draft` ONT.1–62＋Annex T T.0–T.91 逐條）」。對照 WORLD-MODEL-SPECIFICATION.md L907–909：「# Annex E [N] — 自創評價性謂詞判準彙整表／**E1（收錄義務）[N]**」、L773：「# Annex C [N] — 本規格之 Constitutional Compliance Statement」（C.1–C.10，L795–863）、L59（§0.3）：「Annex 條款編號採…**E{n}**（Annex E）；Annex C 各節採 **C.{n}**」；ONTOLOGY-SPECIFICATION.md L56（§0.3）：「Annex 條款編號採 **T.{n}**…**DI.{n}**…**DO.{n}**…**EO.{n}**…**TM.{n}**」、L223（DI.0 [N]）、L242（DO.0 [N]）、L375（TM.0 [N]）、L607（EO.1 [N]）、L631：「本規格計：…Annex DI（DI.0–DI.3）、Annex DO（DO.0–DO.4）、Annex T-Map（TM.0）、Annex EO（EO.1）、Annex CS 合規聲明 [N]」。WM.44（WORLD-MODEL L432）：「並及其各適用上層規格之全部 [N] 條款，均須對應…任一條款無對應且無明記者，聲明不完整，規格不生效力」。grep 驗證 identity 全文無任何 DI.{n}／EO.{n}／TM.{n}／§E1／§C.{n} 之列或處置。
- **建議 remedy**：於 Annex TR 增補 TR.C(4)（WM Annex E、Annex C、WM §0.1–0.5／【地位】）與 TR.D(3)（ONT DI.0–DI.3、DO.0–DO.4、TM.0、EO.1、Annex L3、Annex CS）逐條列，各予「承接／DEFER／不觸及＋理由」處置（DO.1–DO.4 可直指 ID.3／CS.3 既有承接、Annex L3 指 §1.1／ID.71）；同步修正【地位】L17、TR.0、TR.Z、CS.4 之「缺 0 條」敘述；此為 patch/minor 級補正並應登錄 Amendment Log。

## 三、雙反駁出局之 major 候選（8 項，存查）

- ~~[coherence｜refutes 2/2]~~ Annex TR 資料列與上層條文實質不符：TR.B「§6 F1–F6」列（L483）＋TR.C(3)「D16」列（L592）：矩陣誤映使機器稽核產出錯誤結論：(a) TR.B 將 F4（Knowledge Without Identity——本層核心憲章禁令，違反 P3.E1）標為「不觸及＋理由：屬 Layer 4–6 之禁止型態」，卻將 F2…
- ~~[rigor｜refutes 2/2]~~ ID.40：義務文句與可判定判準之事件型別集不合致（雙向斷裂）：MUST 句課 Evidence 義務於 {merge, split, retire, relist, 更正(correct)}，可判定判準卻測 {merge, spl…
- ~~[rigor｜refutes 2/2]~~ ID.50：「已解析」本層自足定義之判定程序缺失（懸空引用）：resolved iff〔採認生效 ∧「provisional 狀態旗標已依 ID.51(a) 清除」〕，但 ID.51(a) 僅定「未解析存量之基數必須可盤點」之指標，…
- ~~[rigor｜refutes 2/2]~~ ID.10（＋CS.2 T-ID-2）：跨部署對齊規則未明文，規格依其自身可判定判準即不合規：ID.10 判準要求「本規格所定之任一命名空間，其 identifier 之跨部署對齊規則已明文且可機械判定者為合規；未明文…違反本條」，惟 §3 全章（ID.11–…
- ~~[rigor｜refutes 2/2]~~ AO.3 ↔ ID.30(a)：「provisional alias」承重而未定義＋「identity claim」一詞多義之條款衝突：AO.3 稱「供應商證券代碼降格為 provisional alias（identity claim，§WM.21(…
- ~~[reality｜refutes 2/2]~~ ID.40（§6.1，specs/IDENTITY-SPECIFICATION.md:234-237）：ID.40 之可判定判準與其自身規範句互相矛盾（判準列 redirect、漏 correct；規範句列「與更正」、無 redirect），且已被主線實作證偽——機器稽核依判準會將主線程式與 DB CHECK 判為違規，依…
- ~~[reality｜refutes 2/2]~~ ID.20 五要素／ID.22 採認鏈重建（§4，specs/IDENTITY-SPECIFICATION.md:171-185）＋Annex DO 掛鉤缺列（:375-384）：判準採認紀錄之載體無任何 DEFER 掛鉤（IDO.1–8 涵蓋 claim／lifecycle／resolution／命名空間／as-of／法規表／權威表徵，獨漏採認紀錄），致現實（裁②→RULING-2026-014…
- ~~[reality｜refutes 2/2]~~ ID.42(b)＋ID.40 事件序（§6.3，specs/IDENTITY-SPECIFICATION.md:247-250、234-237）：唯一經授權之去識別化路徑 identity_de_identify()（SECURITY DEFINER、唯一得繞過 append-only）不寫入任何 lifecycle 事件——ID.40「系統必須維持一概念 lif…

## 四、完備性批評 gaps（下一輪工作來源）

- **DEFER-out 鏈端點版號失效（L4 承接指向已歸檔 draft）**：三鏡 coverage 自陳「grep 逐掛鉤驗 KS KDI.10–15 至條款行號、四規格 IDO 承接欄」，但只驗掛鉤『存在』未驗『版號』。實查：specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md 對 IDO.1/2/3/4/6/8 之承接（KDI.10-15 @L602-607、KS.83 @L503、KS.90-91 @L530-534、defers-in @L991、front-matter @L953）全部標 `AUGUR-ID v0.1-draft`（49 處），僅 5 處 `AUGUR-ID v1.0`；反觀 L5/L6/L7（COGNITIVE-KERNEL 16、AGENT-RUNTIME 19、INFRASTRUCTURE 35 處 v1.0，draft 0 處）已全數遷移。ID 之主 DEFER-out 端點（Confidence 語義 IDO.1、五元組欄位 IDO.2、as-of 重建 IDO.6、唯一權威指定 IDO.8）於 L4 全部解析至已歸檔草稿，違 ID.10 跨部署對齊、CS.2、WM.44/CS.3 雙向可解析，且違 RULING-2026-018『全艦引用版號齊一』之處置。此端點失效未被任一鏡列為 finding。
- **ID 本體上游 ONT 錨定系統性指向 draft（分級可能過輕）**：specs/IDENTITY-SPECIFICATION.md 全文引 `AUGUR-ONT v0.1-draft` 62 處、`AUGUR-ONT v1.0` 僅 5 處。幾乎全部規範 carries 句（ID.1 @L90、ID.3 @L104、ONT.22/ONT.31 @L143/150、Annex O AO.1/AO.3/AO.4 引 T.1/T.20/T.90/DO.1 @L350-366、Annex L3 承接、TR.D 表頭『AUGUR-ONT v0.1-draft ONT.1–62』@L407）皆錨定已歸檔草稿，卻與【地位】L14/TR.0 L406『上層 AUGUR-ONT v1.0 已先行生效』抵觸。三鏡僅以 minor『AUGUR-ONT 版本雙態』列 §0.1 L55／§0.5 L75／【地位】L18 三點，未枚舉此 62 處系統性錯錨，亦未評估其對 WM.44『缺 0 條』基準之影響：TR.D 逐條矩陣係就 ONT v0.1-draft 之條款集建立，非生效之 ONT v1.0——RULING-2026-003 雖稱 draft→v1.0『無實質變更、不重排』，但完備性基準版本本身系統性錯置未被獨立確認。
- **現實面：as-of 屬性繫結主管線 sync_attribute_versions.py 未讀**：三鏡 coverage 明列 augur-code/scripts/sync_attribute_versions.py『未讀』。此腳本正是 ID.60（身份屬性須 as-of 繫結）之現實落地：TaiwanStockInfo 快照差異偵測→entity_attribute_version SCD-2 append（守 ID.60、AUD-07）。§8（ID.60/ID.61）之現實對應僅在 src/augur/identity/attribute_version.py 模組層被讀，未追至實際 roster→版本差異→append 之管線（含 max(date) 現值口徑、多值 sorted DISTINCT 聚合、valid_from 語義）。§8 as-of 義務之現實兌現面未親驗。
- **現實面：identity_de_identify() 不寫 lifecycle 事件、且零測試覆蓋**：ID.42(b) major（去識別化路徑不寫 lifecycle 事件、破 ID.40『維持概念 lifecycle 事件序』）已被鏡列。實查 scripts/migrate_identity_ddl.py:306-331 之 identity_de_identify()：僅 UPDATE entity_attribute_version SET attribute_value='_redacted' + UPDATE entity_registry SET status='tombstoned'，全無 INSERT INTO identity_lifecycle_event、亦不呼叫 lifecycle.record_event——現實面『破事件序』屬 CONFIRMED。但鏡未指出：tests/test_phase2_identity.py 對 identity_de_identify **零測試**（grep 無任一 de_identify 案例），故此破口從未被執行/回歸驗證，僅靜態讀出；ID.42 唯一授權去識別化路徑之現實行為未經跑動確認。
- **現實面：lifecycle 事件型別測試僅覆蓋 4/13，merge/split/relist/redirect/correct/de_identify/DynamicEntity 終結全未測**：lifecycle.py 定 event_type ∈ {mint,merge,split,retire,relist,redirect,correct,tombstone,de_identify,settle,expire,convert,redeem}（L4）。但 tests/test_phase2_identity.py 僅測 fresh_mint、single_live_resolved、code_reuse_provisional_mint(retire)、ambiguous、attribute_version_append_scd2——merge/split/relist/redirect/correct 及 ID.44 之 settle/expire/convert/redeem、de_identify **均無測試**。ID.40/ID.44 事件集正是兩條 major 之標的（義務句 vs 可判定判準 vs DDL CHECK @migrate_identity_ddl.py:124-125 之三方不合致），其現實兌現對 9 個事件型別完全未驗。coverage 明列此測試檔『未讀』。
- **現實面：未併分支 remediation/phase2-retire-backfill 之腳本未查**：git branch 顯示本機存在 remediation/phase2-retire-backfill（有別於已併之 phase2-identity），三鏡 coverage 明列『未併分支 phase2-retire-backfill 之腳本內容』未讀。retire/relist/backfill 正是 §6 lifecycle 與 ID.43 代碼重用存續邊界之現實施工面；此分支未檢視，§6/ID.43 之退市回填現實對應面留白（backfill_entity_registry.py:61-193 亦僅標頭被讀，run_backfill/mint_batch/_check 主體 coverage 標未逐行）。
- **審計交叉核對缺口：無 ID 專屬三鏡/code-compliance，完備性依規格自陳**：audits/ 僅有 WM-THREE-MIRROR、MC-THREE-MIRROR、L7-REREVIEW，**無 ID-THREE-MIRROR、無 identity 專屬 code-compliance**。CODE-COMPLIANCE-AUDIT-2026-07-16.md 之 identity 條目（AUD-04/05/06/07）成於 v1.0 生效前，未與 v1.0 定稿逐條 diff。REMEDIATION-ROADMAP.md:26-27、L46-47 將 identity『缺 0 條』『✅ 已解』直接引 IDENTITY-SPECIFICATION.md:17 之【地位】自陳為據——即完備性由建造者自陳背書，未獨立重算（違本審鐵律『永不採信建造者自陳』）。coverage 亦承認『audits/ 各審計全文』未讀。
- **Annex TR 逐格『缺 0 條』完備性未獨立重算（含補正自陳未親驗）**：三鏡 coverage 明言『Annex TR 逐條矩陣缺 0 條完備性自陳僅抽驗（P3/P4/WM.20-22/ONT 核心列與 D 表、A 表逐列掃讀）未逐格重算』。已知 major：TR.C 漏列 AUGUR-WM 之 [N] Annex E §E1 與 Annex C（survives=true）。但【地位】L17 自陳『對抗審查查出之 §0.2／§1.2／§1.3／§7／§8.5 缺列已補正』——此『已補正』從未對三上層實際 [N] 條款清單逐格重驗；TR.A–TR.D 對 MC v1.4／WM v1.0／ONT v1.0 真實 [N] 條款盤存之逐格完整性仍為自陳。WM.44 生效要件之形式充分性根基未經獨立枚舉。
- **接縫：L5 COGNITIVE-KERNEL 對 IDO.7 之『不觸及』理由誤標目標層**：specs/COGNITIVE-KERNEL-SPECIFICATION.md:404 將『IDO.7–IDO.8（唯一權威 Representation 指定→L4）』整組標『不觸及＋理由：目標 L4』。但 ID Annex DO IDO.7（@IDENTITY:383）目標為 **L6**（自然人法規對應表本體與授權），主題為法規對應非『唯一權威 Representation』；『唯一權威 Representation→L4』係 IDO.8 之主題。L5 之 disclaimer 以 IDO.8 主題與錯誤目標（標 L4，實 L6）涵蓋 IDO.7。處置（不觸及）雖因 L5 非二者目標而結論無害，但非目標層對 IDO.7 之特徵化錯誤；三鏡只驗『IDO.7 於正確目標 AGENT-RUNTIME(L6) 有承接』（19 處），未查非目標層 disclaimer 是否正確標定 IDO.7 之目標與主題。
- **未連資料庫：ID.50/ID.51 provisional 清除、ID.10 跨部署對齊之生產現實未驗**：coverage 明言『未連任何資料庫——生產數字一律轉引 P5 呈核單／裁決文並標為預告值』。ID.50 major（resolved iff provisional 旗標依 ID.51(a) 清除，但無條文規定旗標清除程序）為規格文本缺陷；其現實面——entity_alias.alias_status（provisional/adopted/retired，DDL @migrate_identity_ddl.py:88）於生產中『provisional→adopted』轉換是否真發生、未解析存量基數是否可盤點——未對 55GB 生產庫或沙盒實測。ID.10 跨部署 identifier 對齊規則之機械可判定性亦僅文本審，無生產命名空間互斥實測。
- **上游全文未親讀之殘留：WM Annex A/B/F、MC §5/§7/§8、ONT Annex T-Map/CS 全文**：三鏡 coverage 一致承認：WM Annex A A.0–A.59 全文（僅節選）、WM Annex B/F、MC §5/§7/§8 全文（僅所引小節）、ONT Annex T-Map 資料列與 Annex CS 全文『未逐字全讀』。ID Annex TR.C(2) 對 WM Annex A 之『領域實例／不觸及』逐列歸類（@IDENTITY:552-557 起）、TR.D 對 ONT Annex T 逐型別列，其正確性依賴這些上游全文；未親讀上游即無從獨立否證 TR 各列之『承接／不觸及＋理由』是否與上游條文實質相符（已知 TR.B F2/F3/F4 誤映之 major 即屬此類，且該 major survives=false 之判定本身亦建立在未全讀 MC §6 F 家族全文之上）。

## 五、minors／observations 摘要

- [minor｜coherence] §0.1（L55）、§0.5（L75）、CS.4（L724）vs 引言（L8）、【地位】（L18）、Annex CS front-matter（L671）——AUGUR-ONT 版本雙態：版本敘述與現況不符＋Annex 與正文不一致：同一 [N] 文件同時宣稱 Layer 2 為「v0.1-draft（草案）」與「v1.0 已於 2026-07-17 先行生效」。§0.5 更指示引用時…
- [minor｜coherence] 【地位】（L14）draft→v1.0 變更範圍自陳：版本敘述與現況不符：自陳「變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version」，但與歸檔 draft 之實際 diff 尚含：§0.1 生效要…
- [minor｜coherence] CS.4（L726–727）vs TR.B（L483）／TR.C（L521–523、L526、L546–550）——「不觸及」條款群歸納互斥：Annex 內部處置矛盾：CS.4 將「§6 F5–F6」「WM.24–29」「WM.49–53（Domain Profile 框架）」歸入明記「不觸及」之條款群；但 TR.B 標 F1／F4／F5／…
- [minor｜coherence] ID.50（L275–276）→ ID.51(a)（L282）之內部引用：引用語義錯位：ID.50 之「已解析」機器可判定代理第二要件為「provisional 狀態旗標已依 ID.51(a) 清除」，但 ID.51(a) 僅定義未解析存量之基數「必須可盤點」，全條無任何旗…
- [minor｜coherence] CS.1-P2（L689）、CS.1-P3（L696）vs ID.50（L275）——「已解析」操作化不一致：Annex 與正文不一致：CS.1-P2 稱「『已解析』以採認紀錄存在（ID.20）操作化」、CS.1-P3 亦僅附 ID.20，均省略 ID.50 定義之第二要件（provisional 旗標清除）…
- [minor｜coherence] §0.5（L76）三態標注義務 vs Annex [N] 條款（AO.1–AO.4 L352 起、IDO.0 L372、L4.0 L390、TR.0 L406、TR.Z L656、CS.1–CS.4）：自違三態標注義務（三分互斥標注之缺漏）：§0.5 課「每一 [N] 條款標注其憲章／上層錨定與三態型態（refines／carries／hooks）」，正文 ID 條款均帶「[N｜模式｜錨定]」括號，…
- [minor｜coherence] TR.D（L638）「逐號涵蓋」清單——幽靈條號 T.7–T.13、T.62：計數與實列不符（枚舉不存在之上層條款）：TR.D 自稱逐號涵蓋 T.0–T.91 並列出「T.7、T.8、T.9、T.10、T.11、T.12、T.13」與「T.62」，但 AUGUR-ONT 實際條…
- [minor｜coherence] ID.32 錨定（L222）vs TR.C WM.10 列（L507）：正文與矩陣處置互斥：ID.32 將 `AUGUR-WM v1.0 §WM.10` 列為 carries 錨定之一，TR.C 卻標「WM.10（Observation Store 宣告）｜不觸及＋理由：…
- [minor｜rigor] §0.1／§0.5 ↔【地位】／Annex CS front-matter：ONT 版號正文內部矛盾：【地位】宣告 AUGUR-ONT v1.0 已於 2026-07-17 先行生效、且「正文對 AUGUR-ONT 之引用之版本標注由 v0.1-draft 更新為 v1.0 …
- [minor｜rigor] ID.43：紅旗判準以 retire 事件先存為觸發前提，RULING-2026-015 裁③「retire 先行」順序義務未規格化：亂序到達（重用碼先現於名冊、retire 事件後補登）時「同一外部代碼於 re…
- [minor｜rigor] ID.24：可判定判準未測其自課義務且雙機制關係含混：條文既定「§ONT.40 效力封印於各端點 Type 判準經採認時解除」，又課「關係之判準採認**準用** ID.20」，二者為充分／必要或並行要件未明——端…
- [minor｜rigor] ID.40（開放集）：事件型別枚舉宣告為開放集但無封閉化紀律：擴充僅「得依其型別語義擴充」、無具名治理行為／論證義務；「未列名之終結型別於 DynamicEntity 語境準用其對應終結事件」之「對應」無映射判準。TR.D…
- [minor｜rigor] ID.11／ID.50：「首次意圖進入 Reasoning／Planning」觸發分支無可判定判準：二條之可判定判準均僅測 Knowledge 升級分支（ID.11「任一升級為 Knowledge 之世界個體參照…」、ID.…
- [minor｜rigor] ID.22 ↔ §0.5／IDO.0：下放未入 Annex DO：ID.22 將 fail-safe 重評估之「受影響範圍界定 DEFER Layer 4–6」，惟 §0.5 明定「其執行層落實一律下放（Annex DO）」、IDO.0 …
- [minor｜rigor] §0.5 ↔ Annex O／DO／L4／TR：「每一 [N] 條款標注憲章／上層錨定與三態型態」之自課未於 Annex 條款落實：AO.1–AO.4、IDO.0、L4.0、TR.0、TR.Z 均為 [N] 條款而無｜refines/carries…
- [minor｜rigor] ID.32：「權威表徵之錨點」承重未定義：可判定判準以「identifier 對可解析至**恰一權威表徵之錨點**」為合規測試，惟「錨點」全文無定義（是系統 identifier 本身？merge 後存續者？Re…
- [minor｜reality] §0.1／§0.5 vs 【地位】／Annex CS front-matter（specs/IDENTITY-SPECIFICATION.md:55、75 vs 18、671）：上層 ONT 版本自述內部矛盾：§0.1 列「AUGUR-ONT v0.1-draft（Layer 2，草案）」、§0.5 稱「Layer 2 現為 v0.1-draft」，而【地位】明載「AUGUR…
- [minor｜reality] CS.4 vs Annex TR.C（specs/IDENTITY-SPECIFICATION.md:727 vs 521-526、546-550）：CS.4「明記不觸及之主要條款群」把 WM.24–29 與 WM.49–53 整段歸入不觸及，且把 WM.49–53 誤稱「Domain Profile 框架」——與逐條權威之 TR.C 自相矛盾：T…
- [minor｜reality] ID.11／§7（specs/IDENTITY-SPECIFICATION.md:142-145）——並發准入語彙缺口：「恰一系統 identifier」不變式對並發准入無任何原子性義務或重複鑄造偵測語彙；現實親測雙鑄成立（雙連線同碼各鑄一枚），Steward 須以裁決在規格外發明教義（advisory lock 前置…
- [minor｜reality] §6／ID.43（specs/IDENTITY-SPECIFICATION.md:254-257）——存量回填順序語彙缺口：ID.43 紅旗判準（「同一外部代碼於 retire 事件後再現」）預設 retire 事件已在序；對既有 55GB 生產庫之存量鑄造，規格無「歷史 lifecycle 事件回填先行」之順序義務——現…
- [minor｜reality] ID.50／ID.51(b)（specs/IDENTITY-SPECIFICATION.md:275-286）——provisional 清除無留痕義務：ID.50 以「provisional 狀態旗標已依 ID.51(a) 清除」定義已解析、ID.51(b) 課解析時效「必須可量測」，但規格對旗標清除行為本身無留痕（時點＋作成者）義務；落地載體 en…
- [minor｜reality] ID.23／Annex DO IDO.4（specs/IDENTITY-SPECIFICATION.md:187-189、380）——目標層定性被下游改判：IDO.4 將「resolution 演算實作」與「未解析存量量測」捆綁單一目標 L4；下游 KS 拒收演算半項並改定性為 L5 inference（KDO.1→L5.9 承接），量測經 KDO.4 …

- [obs] DEFER 鏈雙向皆閉合、無跨層斷鏈：上行——WM Annex D 目標含 L3 之全部列（D2 L2/L3、D3、D4、D5、D6、D17 L3/L6，WORLD-MODEL L884–893）與 ONT Annex DO 全部列（DO.1–DO.4 均目標 Layer 3，O
- [obs] IDO.4 之「resolution 演算實作」在本規格標目標 L4，但下游已雙重重定性：KS.83(ii)（KNOWLEDGE-SYSTEM L504–506）讀為 L5 推論並列緊張 T-KS-6，L5.9（COGNITIVE-KERNEL L156–157）承接並載「此定性
- [obs] 規格與 Phase 2 已落地機制在概念層一致：RULING-2026-015 裁①「UNIQUE 不可行——ID.43 合法同碼二列」與 ID.43 存續邊界截斷（跨 retire/relist 邊界解析為不同存續個體）語義吻合；「~235 枚 provisional 重用碼正
- [obs] ID.3 表 D2 列落點記「§4（ID.20–ID.23）」而目錄／附表記 §4 為 ID.20–ID.24：ID.24 錨於 ONT.40／T.50／T.51（非 D2 下放），窄列應屬有意，非缺陷。
- [obs] TR.D 具名列之 T.42、T.43 括注採面向描述而非 ONT 條題（T.42 實為 HoldingStructureState〔持股結構〕、T.43 實為 UniverseMembership，ONTOLOGY L343、L345）；映射本身可解析且 ID.60 正文錨定 
- [obs] 【地位】L17 所稱對抗審查補列之 §0.2／§1.2／§1.3／§7／§8.5 五列已親驗存在（TR.B L471、L429、L430、L484、L489），該補正屬實。
- [obs] MC §9（Final Statement）為 [I]，TR.B 無列不構成缺漏；MC §1.2／§1.3／§2.4／§4 EV.1–EV.12／P 家族各 E/W 條之錨定內容均與 META-CONSTITUTION.md 現行文句逐一相符（§2.4「兩個 identifier
- [obs] 下行鏈全數親驗存在：IDO.1→KS KDI.10/KS.90、IDO.2→KDI.11/KS.91、IDO.3→KS KDI.12＋L7 LDI.21（L7.16/21/22）、IDO.4→KS.83＋L5.9＋L7.26、IDO.5→L7.23（LDI.22）、IDO.6→K
- [obs] IDO.4 目標層定性分歧已於下游登錄：ID 標 resolution 演算目標 L4，KS.83(ii) 讀為 L5 inference（T-KS-6）、L5.9 承接並提解消案「推論歸 L5、claim 信度欄位歸 L4」待 Steward 裁定——裁定後 ID Annex 
- [obs] L4 規格（KNOWLEDGE-SYSTEM-SPECIFICATION.md）全篇仍引「AUGUR-ID v0.1-draft」，而 ID 已 v1.0 生效——KS 側版號滯後（非本規格缺陷，與 minors 之 ONT 版號矛盾同病、宜同批 patch）。
- [obs] RULING-2026-014 追認之「操作化判準」文句（如 T.1 Security＝stock_id ~ '^[0-9]'）與 ONT T.1 制定之判準內容（同一 iff 繫結同一 Issuer × instrument class × 發行序、不跨 retire/reli
- [obs] resolve.py 無採認閘：action='resolved' 不驗該 Type 判準採認紀錄之存在（ID.21／AO.2「無採認紀錄時視為已解析者違反本條」）；現因 RULING-2026-014 已採認三型別而暫無實害，但入口為 code_system 泛用——未採認新型
- [obs] identifier.py 標頭誠實揭露 ID.11 義務「機制就位、義務未結」（mint 尚無攝取端呼叫、外部碼仍直充身份）——與規格一致之過渡狀態，follow-up Phase 5 攝取准入強制 resolve_or_mint＋稽核閘。
- [obs] ID.42(b) 抹除事件 provenance 三要件（作成者、法源依據引用、生效時點）：落地事件表無法源依據專用槽、de_identify/tombstone 非 Evidence 硬義務（lifecycle.py L109-110）——provenance 完備性現無機器強
- [obs] ID.51(c)「疑似同一」複述 WM.15 時落「有事證顯示」限定（WM.15 L190 原文「有事證顯示兩通道疑似描述同一世界事實」）——登錄義務觸發門檻弱於上游、可判定性降低，patch 補四字即齊。
- [obs] RULING-2026-015 裁①親測雙鑄成立（並發下同一外部碼二枚 augur_id）：規格以結果判準（恰一 identifier）＋merge 機制涵蓋補救、並發防護屬 L7 落地（advisory lock 為接線前置）——概念層無需增條，惟「重複鑄造之發現→merge 
- [obs] lifecycle.resolve_as_of 環偵測（_depth>64 回當前節點之 fail-safe）與 INFRA L7.22「拒斥環」語義不同（靜默回退 vs 拒絕）——L7 審時宜對齊。
- [obs] ID.43「合法同碼二列」教義（UNIQUE 不可行）與 entity_alias 非唯一索引落地一致；重用碼 provisional 不縫合教義與 resolution_action provisional_mint 路徑一致——此二項規格－實作對應良好。
- [obs] DEFER 鏈條八掛鉤端點全數親驗有著落：IDO.1→KS KDI.10/KS.90、IDO.2→KDI.11/KS.91/KS.26、IDO.3→KDI.12（L4 概念槽）＋L7 LDI.21/L7.21-22/L7.16、IDO.4→KDI.13/KS.83＋L5.9/LD
- [obs] ID.43 教義與現實一致確認（正面發現）：resolve.py 五動作判準（resolution_action:27-50）忠實落地「重用碼 provisional 不縫合」；「entity_alias 無 UNIQUE 係 ID.43 合法同碼二列之正確結果」經 RULING
- [obs] ID.11 runtime 義務未結、誠實揭露在案：ingestion/ 零 resolve_or_mint／augur_id 引用（grep 親驗），identifier.py:15-19 ⚠ 誠實揭露「機制就位、義務未結」——惟其中「mint 尚無任一呼叫端」一句已因 Pha
- [obs] 生產 backfill 尚未施作：retire-backfill 腳本（backfill_lifecycle_retire.py）僅存在於未併分支 remediation/phase2-retire-backfill（b5b19f1），main 無此檔；P5-SUBMISSION
- [obs] AO.4 Issuer（T.20）判準採認尚無紀錄：RULING-2026-014 僅採認 T.1 Security／T.2 Index／FredSeries 三判準；Issuer 引用依 AO.2/AO.4 保守解釋維持未解析——規格與現實一致、非缺陷，但為 Layer 4+ 
- [obs] 追認（retroactive adoption）語彙不在規格中：裁②揭露 3,149 枚 alias 生而 adopted 而無 ID.20 採認紀錄（「憲章上 3,149 待採認、機械上 0」之盤點失真），Steward 以 RULING-2026-014「追認」治癒；ID.2
- [obs] ID.60 消費側切換未完成：SCD-2 機制與 sync_attribute_versions 已落地，但 core_gate 產業判定尚未改讀 as-of 屬性（attribute_version.py:5 自標 follow-up；P5 known-note 1 列為 Ph
- [obs] resolution_action 之 ambiguous 動作回傳最新 augur_id（零寫入、待人解析）：ID.51(c) 待決不得合併消費之保守性完全繫於呼叫端遵守 action 旗標；規格對解析入口於待決時之回傳語義無明文（演算 DEFER L4）——建議 L4 承接 
- [obs] attribute_version.get_asof 單點近似之雙時間軸未分離邊界（date 傳入致當日事後修正不可見）已於 docstring 誠實揭露並明示 DEFER L4 KS.40-46（attribute_version.py:43-46）——與 ID.61 分界一致

## 六、對「L3 完成」之判定

**L3 首次對抗審查未通過（三鏡皆 NO-GO）。** 存活 major 1 項集中於 WM.44 形式充分性矩陣（Annex TR）之枚舉缺口——【地位】宣稱『五上層全部 [N] 逐條枚舉、缺 0 條、形式充分性已成就』與 grep 實測矛盾，屬**生效要件級**斷點。 本層之形式充分性自證既受質疑，**其充任生效記錄宜提請 Steward 依 §8.2 覆核**；remedy 多為 patch–minor 級文本修繕，惟修繕前『形式充分性已成就』之陳述不成立。

*配套草案：RULING-2026-019-DRAFT（呈 Steward 就 L2–L6 首審 findings 一次處置）。*