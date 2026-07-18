# AUGUR-WM v1.0（L1 World Model）三鏡對抗審查——findings 冊 [I]（概念層首份受審）

* **日期**：2026-07-18｜**性質**：[I] 審查報告——不修改 WM 一字；WM 之變更屬 §8.5/§8.6（Steward 專屬）。
* **執行**：5 代理（三鏡 xhigh＋旗艦 major 雙反駁）；判例庫＝26 發現審計＋15 裁決＋Phase 1-2 施工＋40 檔直綁＋CODE-MIGRATION-PLAN
* **意義**：L1 於 RULING-2026-002 期以硬化前弱 linter 充任，僅 #22 校標籤，內容首次受對抗審查。

## 一、總判：規範核心穩固，零 major 存活（強過關）

| 鏡 | go | 要旨 |
|---|---|---|
| 內部一致性 | ✅ | 編號零缺零重、交互參照零懸空、canonical chain 投影自洽、WM.2 十一概念對 MC §2 逐一相符 |
| 上游保真＋概念層獨立性 | ✅ | 忠實 refines MC、七新造術語皆錨 §2、§0.6(b) 以 WM.4 刪名測試落實、L5–7 名詞全為 [I]/Channel/DEFER、DEFER 鏈 D1–28 全承接無孤兒 |
| 現實與下放 | ❌→淨零 | 唯一 major（WM.36 權威表徵 vs 還原價）**經雙反駁官雙殺**（誤讀 WM.14 解析域）——淨零 major 存活 |

**關鍵**：現實鏡 go=false 係其旗艦 major 所致，惟該 major 被兩位反駁官一致 refuted（WM.14 第4欄解析域為「每一世界概念」非「每一供應商表」；還原價/原始價為互補通道非同一事實雙權威）。審查官評語：**「WM 規範核心無恙、非弱 linter 綠燈式假象」**。

## 二、殘餘 findings（全數 minor/patch）

### [minor] §0.3（line 62）、WM.1、WM.44（line 432）、Annex C front-matter（line（coherence鏡｜remedy spec_amendment_8_6）
**版本錨定凍結於 AUGUR-MC v1.2；L1 為七規格中唯一未隨 v1.3 者，且 §0.3 以 MUST 永久凍結、WM.44『現行版/v1.2』用語自相張力**

WM 全文 195 處引用 AUGUR-MC v1.2、0 處 v1.3；現行元憲章已為 v1.3（2026-07-16、AL-2026-006），其餘六份生效規格（L2–L7）之內文與 mc-version 欄一律 v1.3，L1 為唯一例外，形成任務所指之『版本一致性斷鏈』。三處逾越單純陳舊、屬規範性凍結：(a) §0.3 以 MUST 規則『本規格引用憲章一律採 AUGUR-MC v1.2 §{條款編號} 格式』永久凍結引用版號，與 RULING-2026-002 主文五命五份治權檔改採『AUGUR-MC v1.3 §{條款}』及全體 L2–L7 慣例相左；(b) WM.44 自述以『AUGUR-MC 現行版全部 [N] 條款』為對象，卻『以 AUGUR-MC v1.2 §0.3 枚舉』——而 linter（mc_clauses.py 第 3 行、current_mc_version 讀 MC §0.1 版本欄）實以現行 v1.3 §0.3 枚舉，WM.44 所述枚舉基準與『現行版』／linter 基準名義背離；(c) Annex C mc-version: AUGUR-MC v1.2 對比六份下游規格 mc-version: AUGUR-MC v1.3，構成 L1 斷鏈。緩解甚強：RULING-2026-002 主文一明白裁示 v1.2→v1.3 為 minor、WM 所引各條編號與內容不變、『其合規聲明無須重作』，故 mc-version 停留 v1.2 屬 Steward 認可之現狀，非未察之錯。惟裁決未觸及 §0.3 永久凍結 MUST 與 WM.44『現行版/v1.2』張力：WM.48 僅於 MC major 觸發重認證，MC 日後任何 minor 都將令 §0.3 命令引用一個過時版號、並使 WM.44『現行版』與其自訂 v1.2 枚舉基準持續發散。文件本身於 line 5、122、853（T-6）已承認 v1.3 存在生效，凸顯此凍結為刻意但未貫通之選

### [minor] Annex C C.10（line 865）對比 WM.47（line 447）、WM.48（line 451）（coherence鏡｜remedy spec_amendment_8_6）
**§8.1 同時被列為 carries（WM.47/48 三態錨定）與『不觸及』（C.10 形式充分性自查）——違反 WM.44 三分互斥**

WM.44 之覆蓋三分（對應至本規格條款／DEFER 掛鉤／明記『不觸及』+理由）要求每一 MC [N] 條款落入單一桶。C.10 將 §8.1 與 §8.5 並列為『未觸及之 [N] 條款…明記不觸及』，卻於同句補述『本規格於 WM.47–48 承接其對規格之效力面』；而 WM.47 之三態標籤即 [N｜carries｜…§8.2、§8.4、§8.1]、WM.48 為 [N｜carries｜§8.6、§8.1]——以『承接（carries＝WM.44 對應模式之一）』正式收錄 §8.1。故 §8.1 被同時歸為『已對應（WM.47/48 carries）』與『不觸及』，二桶互斥卻並存。§8.5 無此問題：未見於任何 carries 標籤，僅 C.1（line 799）以『§8.5(d) 之尊重』作不違反式引用，與『不觸及』相容。此非覆蓋缺口（§8.1 兩路皆已涵蓋），而為形式充分性帳目之分類矛盾；恰為弱 linter／自查（gate 綠）未攔之治理裂縫。正解：C.10 應將 §8.1 由『不觸及』改列『對應至 WM.47、WM.48（效力面承接）』，僅保留 §8.5 於『不觸及』。

### [observation] Annex B B.1 MC-34（line 726）對比 WM.32／WM.33 §0.5 三態標籤（coherence鏡｜remedy informative_patch）
**B.1 資訊性模式彙總（MC-34＝hooks）與 WM.32/WM.33 之 carries 三態標籤字面不一（可調和、低度）**

B.1 將 MC-34（P4.W1、P4.E3、P4.E7 → WM.32、WM.33、D10）之『模式』欄標為 hooks，而 WM.32、WM.33 之 §0.5 三態標籤皆為 carries。二者可調和：B.1 之 hooks 係把該需求列所含 D10 之 DEFER 併入彙總，clause 之 carries 則反映承接不變式面；且 B.1 明載為資訊性（line 687，規範效力悉依所引條款本文）。惟供讀者以 B.1 模式欄對表 clause 三態標籤時，同一條款字面落差可能造成誤讀。建議（非阻斷）於 B.1 對 MC-34 標『承接＋hooks』或加註，使模式彙總與條款三態一致。

### [minor] WM.38（及 Annex D D17、B.1 MC-16、C.2）（fidelity鏡｜remedy informative_patch）
**WM.38 承接 P1.E3 卻以泛稱「下層」下放、條頭型態僅標 carries——P1.E3「唯一未點名層」之 WM 側同型模糊**

WM.38 條頭為「[N｜carries｜AUGUR-MC v1.2 §P1.E3]」，正文末句為「具體法規對應 DEFER 下層（Annex D D17）」。此違反本文件自身慣例：所有含 DEFER 之條款（WM.21/WM.23/WM.28/WM.29）條頭一律標「hooks」並於條頭載明「目標 Layer X」，唯 WM.38 一面執行 DEFER（D17）、一面型態僅標 carries、且正文以泛稱『下層』而不點名目標層——恰複製 MC P1.E3『具體法規對應由下層規格定義』之未點名措辭。目標層 L3/L6 僅見於 Annex D D17，未見於條款本體；而 B.1 MC-16 與 C.2 又把 WM.38 歸為『承接＋DEFER』，與條頭『carries』單值不一致。§0.5 要求每一 [N] 條款標三態型態、WM.41(b) 明定複合模式以「＋」表記、WM.3/WM.5 要求 DEFER 掛鉤明載目標 Layer——三者於 WM.38 條頭/正文層次未滿足。實質已於 Annex D D17（L3/L6）具體化且被下層承接，故屬條頭/正文標示瑕疵而非鏈斷。這正是委辦所問『P1.E3 未點名層在 WM 側是否有同型模糊』之明確答案：有，存於條款本體，但已於 Annex D 治癒。

### [observation] WM.34（fidelity鏡｜remedy informative_patch）
**WM.34「稽核機制之實作 DEFER 下層」亦以未點名層下放，且未登錄於 Annex D 總表**

WM.34 條頭為 carries，末句『本規格及下層任何細化不得使 (a)(b) 不可機器稽核；稽核機制之實作 DEFER 下層。』此為 WM.38 之外第二處泛稱『下層』之下放：未點名目標 Layer，亦未列入 Annex D（D0 宣示 Annex D 為 DEFER 總表、WM.3 要求 DEFER 掛鉤明載目標 Layer）。實務衝擊低——機器稽核不變式 (a)(b) 已由全體下層 TR 矩陣承接，非孤兒；但與 Finding 1 同型，暴露正文尚有兩處未貫徹「DEFER 必具名層＋入 Annex D」之紀律。

### [observation] WM.9（對照 WM.2、Annex E）（fidelity鏡｜remedy informative_patch）
**WM.9 之權威三分新造位置名『形權威／結構權威』未納入 WM.2 新造術語清單**

WM.2 以定義式破折號枚舉本規格新造術語（World Concept、World Concept Registry、Observation Channel、Observation Store、Domain Profile、世界關係、世界量），並課『同一新造概念全文採單一名稱、不另創異名』之紀律。WM.9 另創『形權威（Observation 層）』『結構權威（世界結構層）』二位置名（『系統記錄』尚可視為 §5 角色一之中譯），此二詞為 WM 自造、於 WM.9 內定義並錨定，卻未收入 WM.2 之新造術語枚舉。若 WM.2 之清單解為窮舉（其破折號句式讀來如是），即為術語登錄完整性缺口；若解為例示則無礙。因二詞已於 WM.9(a)(b) 就地定義並錨定 Observation／世界結構，實質紀律已達，風險低。

### [observation] WM.31(b)（對照 WM.30、MC §P4.E2）（fidelity鏡｜remedy downstream_flag）
**WM.31『可知規則（可知或公開可得）』於 refines P4.E2 標籤下引入逾越雙時間軸之第三概念**

MC P4.E2 明定恰兩時間軸：valid time（何時為真）與 transaction time（系統何時得知）。WM.30 忠實 carries 之。WM.31(b) 另立『可知規則：該 Observation 自何時起為系統可知或公開可得之推導規則』——『公開可得』異於『系統得知』（來源公開之時點 ≠ 系統攝入之時點），此為 anti-leakage/as-of 所需之第三性質。WM.31 條頭標 refines｜P4.E2，且自承『可知性之座標化（如以第三時間軸建模）…屬 Layer 4 之設計空間（D8）』。此屬服務 P4.E2『任一過去時刻認識狀態可稽核』之細化、且已於 Annex C T-1、A.36 顯式揭露時間模型不對稱、並下放 L4/D8——非逾越，惟『可知/公開可得』之語彙擴張建議由 L4 明文與雙時間軸調和，以免下層將其誤植為 transaction time。

### [minor] WM.15「衍生調整觀測」（併 WM.10、A.34、§P4.E6、A.58、Annex F 第1條）（reality鏡｜remedy interpretation_8_1）
**「衍生調整觀測」語彙不辨衍生地點（來源端衍生＝Observation vs 系統端衍生＝Representation）；還原價一旦改由系統自建，A.58／Annex F #1 之 Observation Channel 登錄即與 WM.10/A.34 自相牴觸**

本鏡職掌(3)『raw 鏡像層 vs Observation Store 之邊界』與『雙副本版本錨定』。WM.15 以『衍生調整觀測』一詞把還原價定性為 Observation（Annex F #1 登錄其時間戳語義=交易日、可知規則=收盤後當日可得，即當作來源通道）。此定性隱含還原價由『來源（供應商）』計算供應——今日屬實（FinMind TaiwanStockPriceAdj）。但判例庫載明現實已規畫將調整計算移入系統：repair_priceadj_basis.py 結構性註記『長期正解＝庫內以 raw+除權息事件自建調整序列（arena plan §5 已規畫用於結算標籤）』。一旦移入系統，依 WM 自身 A.34『系統自算之…值…否則不得存為 Observation（§P4.E6 引用鏈終止要求）』與 WM.10 二特徵（逐值可追溯至某次來源回應），系統自建之還原價非 Observation、而係引用鏈終止於 raw+CorporateAction 之衍生 Representation/世界量（WM.8）。屆時 A.58／Annex F #1 把它登錄為『Observation Channel』即內部牴觸。可涵攝性判斷：WM 已有處理該表徵之語彙（WM.10/A.34/§P4.E6/WM.8 世界量），故非缺口，而係 WM.15『衍生調整觀測』措辭與 Annex F 首條預先鎖定 Observation 地位、未標注『衍生地點依存』，形成潛伏誤登錄。屬 §8.1 解釋（釐清『衍生調整觀測』僅涵蓋來源端供應之衍生；系統端衍生歸 Representation）＋ Phase 2/6 下放時 Annex F #1 需複核之下游旗標。

### [observation] 【地位】節／§0.1／Annex C compliance-statement front-matter（mc-vers（reality鏡｜remedy informative_patch）
**WM 全文版本錨定凍結於 AUGUR-MC v1.2，而生效憲章已為 v1.3——潛伏之雙副本版本斷鏈（WM.44 形式充分性係對 v1.2 條款宇宙自查）**

MC 三鏡審查獨立列出『§8.6 版本錨定未涵蓋規格版本錨定於檔名/行號之靜默斷鏈（雙副本現實）』。於 WM 具體化：WM 全文引用一律 AUGUR-MC v1.2，Annex C front-matter『mc-version: AUGUR-MC v1.2』，C.10 形式充分性自查係對 v1.2『全部 [N] 條款』枚舉。生效憲章現為 v1.3（constitution/META-CONSTITUTION.md）。WM【地位】節已作緩解宣告（v1.3 為 §0.5 對照表 minor 增列、所引條款編號不變、規範內容除 §0.5 增列外均不變），此宣告就 WM 既登錄事項可辯護；惟緩解僅及『既引條款不變』，未涵蓋 v1.3 新增素材（§0.5 五治權檔登錄、Appendix E）是否觸及 WM.44『現行版全部 [N] 條款須逐條對應』之覆蓋完備性——若 v1.3 新增任一 [N] 條款進入母集，WM 之 v1.2 基準自查即非對『現行版』。屬 [I] patch 或 §8.1（釐清 WM.44『現行版』於 minor 升版時之錨定基準）；非實質違憲，WM【地位】已部分關閉。

### [observation] WM.35 [I] 條文註記（錨 §P2.E2）（reality鏡｜remedy informative_patch）
**WM.35 [I] 註記引 §P2.E2 為『通用擷取零重構落地＝合法觀測行為』之依據，然 §P2.E2 字面規範 Model output，非來源擷取；§P2.E4／§2.2 為更貼近之錨點**

本鏡職掌(2)WM.35 對 code 先行之描述力。WM.35 正文（設閘於消費資格、不阻斷落地）對判例庫之 generic_schema 零重構落地（ingest.py／generic_schema.py）描述力極佳，且 [I] 註記明點『每新增一來源即豐富而非稀釋世界模型（負向棘輪之反轉）』正面回應 AUD-25。惟該 [I] 註記以『§P2.E2 語境下合法之觀測行為』為擷取落地正當性之依據；§P2.E2 字面為『Model output 不得未經 Evidence 通道直接成為權威 World Representation 或 Knowledge』，其規範對象為 AI/Model 輸出，非來源資料擷取。以其『閘設於取得權威地位處、非入口處』之結構型態作類比雖成理，但落地擷取之正當性更直接源於 §2.2 Observation 定義與 §P2.E4（Representation 保留 Observation 來源）。屬 [I] 措辭精度事項，不影響 WM.35 規範效力（該註記為 [I]）。

## 三、對 L1「完成」之意涵

**L1 首次對抗審查強過關——零 major 存活、規範核心經證穩固、無一發現觸憲或要求停用。** 三處可處置項：(1) 195 v1.2 版本斷鏈＋§0.3 永久凍結 MUST＋WM.44「現行版/v1.2」自相張力（**MC 剛升 v1.4 後更急迫**）；(2) C.10 §8.1 雙歸類矛盾（carries＋不觸及並存、違 WM.44 三分互斥——弱 linter 未攔之治理裂縫）；(3) WM.38/WM.34 泛稱「下層」DEFER 之條頭精度（P1.E3 同型、已於 Annex D 治癒）。配套：RULING-2026-018-DRAFT。