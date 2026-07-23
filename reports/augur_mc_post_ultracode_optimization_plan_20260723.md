# 元憲章優化評估與計畫（L0–L7 ultracode 後｜2026-07-23）

* **性質**：[I] 計畫報告（憲章第六部計畫先行）；**本輪不改 `META-CONSTITUTION.md` 任何 [N] 一字**。
* **問題**：依 L0–L7 ultracode 全鏈結果——**可以進行元憲章優化嗎？**
* **一句結論**：**可以但須拍板**（窄帶 editorial／[I]／工具層／觀察觸發之 clarification；**不建議**無 Evidence 再開原則級動 [N]）。
* **權威依據**：constitution-mcp `layer_status`（MC **v1.5**；L1–L7 皆依 v1.5）；`audits/MC-ULTRACODE-L0-20260723.md`；RULING-028…039；`ULTRACODE-SCHEDULE.md` residual；`python3 -m tools.constitution_lint report` **PASS 7／7**（本計畫撰寫當次）。
* **schema／程式對映**：純治理文書計畫——**不產表、不讀表、不涉 DB schema**；驗證觸點僅既有 `tools.constitution_lint`（零新程式義務）。若後續選「工具層」路徑，沿用既有 `mc_clauses.py`／README 措辭，不新增義務類型。

---

## 〇、一句答覆（呈核用）

**可以但須拍板。**  
L0–L7 ultracode 與 028–039 一攬子已把治理元層 **major 缺口根治或明示閉合**；此刻「優化」＝**整理剩餘 editorial／clarification／觀察觸發項**，不是再開一輪原則級大修。任何動到 MC [N]／§8／102 母集／PA 者，須 Steward 明示路徑＋Evidence，不得默示授權。

---

## 一、現況盤點（為何「可以」而非「必須立刻改 [N]」）

| 軸 | 狀態 | 出處 |
|---|---|---|
| MC 版本 | **v1.5**（§8.1「解釋之界線」已落地） | `layer_status`；AL-2026-035 |
| L0 major | **GOV-1 已閉**（原則級根治）；**GOV-3 已閉**（028 第 2–3 點；B＝觀察觸發）；**GOV-4 反向閉合**（031） | MC-ULTRACODE-L0；028／031／PROPOSAL-001 |
| L0 minor XRF-1 | **工具層操作閉**（97[N]+5[I]）；歷史裁決「§8.3 之 102」**不改本文** | 039 §一；ULTRACODE-SCHEDULE residual |
| L1–L7 單層＋3b | 全數定案；**零存活 major 待開 MC**；蓋章不動搖 | RULING-030…038；SCHEDULE |
| Residual omnibus | **039 全拍板**；禁止假關六項維持；**MC／PA 零觸** | RULING-039；AL-2026-043 |
| 日曆 | **2026-10-14** 併結 checklist（無 Evidence 不提早結清） | SCHEDULE residual；039 §九 |
| Lint | PASS 7／7 | 本輪親跑 |

**解讀**：優化空間存在，但落在「收斂措辭／簿記／觀察升格條件」——不是「憲章本體仍有未處置 major」。

---

## 二、建議優化清單（3–7 條｜標級＋來源）

> 分級：**editorial**＝措辭／[I]／工具文件；**clarification**＝§8.1 解釋或附則 minor（不改既有 [N] 義務外延）；**實質變更**＝改 MC [N]／擴母集／原則級。

| # | 建議項 | 級 | 內容（一句） | 來源 | 建議時機 |
|---|---|---|---|---|---|
| **1** | **GOV-3 B 觀察觸發維持＋升格條件寫死** | clarification（現行）→ **實質變更**（僅觸發時） | 「參與」判準已由 028 第 2–3 點承載；**禁令射程入 §8.1 [N]** 僅於再現越權或判準不敷用時升格——本輪**不升** | MC-ULTRACODE GOV-3；028 明示不為；039 §一 L0 | 即刻：再確認；升格：觸發後另開原則級 |
| **2** | **XRF-1 措辭衛生（後續裁決／工具）** | editorial | 新裁決引用母集時統一寫「**WM.44／RULING-017 §0.3 之 102 條條款宇宙（97[N]+5[I] WHY）**」；**不改**017／026 歷史本文；工具層已閉 | XRF-1；039 §一；MC-ULTRACODE §五 | 即刻可做（無 MC diff） |
| **3** | **§0.3／[I] 母集誠實註（可選）** | editorial（[I]） | 於 §0.3 或 Appendix 增一句 [I]：「102＝枚舉宇宙，含五條 Pn.Y [I]；義務僅由 [N] 產生」——**不改計數、不改 [N]** | XRF-1 緩解建議；§0.3 既有「WHY＝[I]」 | 須拍板後 patch／minor |
| **4** | **DEF-2「世界模型」邊界（綁 GOV-3）** | clarification | §2.8「世界模型」未定義致 Agent 射程浮動——028 已以**行為態樣**繞開；若 GOV-3 B 觸發，一併釐清定義或 DEFER 指名 | MC-ULTRACODE DEF-2／GOV-3 | **DEFER** 至 GOV-3 B 觸發 |
| **5** | **v1.5 後簿記對齊（§0.5／附則引用）** | editorial | 確認 CLAUDE.md／附則／下層 FM 引用「AUGUR-MC v1.5」一致（039 已做 L1–L6 `mc-version`）；剩餘跨 repo 引用掃一次 | 039 §十；AL-035 | 工具／文件層即可 |
| **6** | **RUL-2／026 射程（史料＋先例）** | clarification（不重開） | 026 指令矩陣義務已落 L6／CLAUDE；作 GOV-1 實例證據已保全；**不**為「優化」回頭改 §8.3 [N] | MC-ULTRACODE RUL-2；026；028 界線 | 維持現狀 |
| **7** | **2026-10-14 併結前 GOV-3 B Evidence 盤點** | clarification（程序） | checklist 既列「有無新越權 Evidence」——併審日一併決定「維持觀察／升格 [N]」 | SCHEDULE residual；039 §九 | **2026-10-14** |

**本清單故意不含**：GOV-1 再修、GOV-4 再錨公示、GOV-2 復活、DEF-1／DEF-4／ENF-1／CHN-2 出局項翻案——見第三節。

---

## 三、不建議動的（硬邊界）

| 項 | 理由 | 權威 |
|---|---|---|
| **PA／五原則 [N] 本文** | L0 零 finding；永恆／核心 | MC-ULTRACODE 正面確認；全程 PA 零觸慣例 |
| **§8 其餘 [N]（除已落地之「解釋之界線」）** | self-entrenchment；無新失效 Evidence 不開原則級 | §8.5(b)；028／035 |
| **102 母集計數本身** | 計數正確；問題在宣稱字面／幽靈溯源措辭 | XRF-1；017 §0.3 |
| **歷史裁決本文改字**（017／026「§8.3 之 102」） | 史料；權威落點改指即可 | 039 明示 |
| **GOV-2 復活** | Steward 已裁維持出局、不列待辦 | MC-ULTRACODE §五；Steward 2026-07-23 |
| **出局項翻案**（DEF-1／4、ENF-1、CHN-2） | 三鏡≥2 反駁堅實；Critic 抽查維持 | MC-ULTRACODE Verify／Critic |
| **假關 open-tension**（OT-5／T-KS-6／T-L6-5／025／020 M2／無 Evidence 10-14） | 屬下層／日曆，**非** MC 優化載體；039 禁止假關 | RULING-039 |
| **為「優化」重開 §8.2／重採認任一下層** | L1–L7 蓋章不動搖；無 MC 側 major 要求停用 | 各層 ultracode 呈核；030–038 |
| **本輪直接改 MC [N]** | 用戶／本計畫鐵律；039 亦 MC 零觸 | 本檔性質句 |

---

## 四、路徑比較（v1.6 最小升版 vs 僅 RULING vs 工具層）

| 路徑 | 做什麼 | 門檻 | 優點 | 風險 | 推薦度 |
|---|---|---|---|---|---|
| **A. 工具層／文件層（預設）** | 新裁決措辭衛生（#2）；引用掃 v1.5（#5）；lint 維持綠 | patch／慣行 | **零 MC diff**；與 039 一致；立即可做 | 無 | **★★★ 推薦即行** |
| **B. 僅 RULING／附則 minor** | 可選：新 RULING 重申 GOV-3 B 觸發條件＋10-14 盤點義務；或 §0.3 [I] 誠實註走附則／[I] 補正 | §8.1 解釋或 annex minor／[I] | 不觸 [N] 義務外延；可登錄 AL | 解釋通道須守 v1.5「解釋之界線」——不得課新義務類型 | **★★ 若需「有裁可引」** |
| **C. MC v1.6 最小升版** | 例如：§0.3 [I] 母集誠實句；或（觸發後）GOV-3 B 判準入 §8.1 [N] | [I]/附則＝minor／patch；**§8.1 [N]＝原則級** | 文本自足、減少「裁決考古」 | 剛完成 v1.5；無新 Evidence 開原則級＝程序浪費＋self-entrenchment 噪音；下層 `mc-version` 又要掃 | **★ 僅 Steward 明示要文本自足／GOV-3 B 已觸發時** |

**路徑選擇建議（幕僚）**：

1. **現在 → 2026-10-14**：走 **A**（必要時加 **B** 一句再確認），**不**開 v1.6。  
2. **2026-10-14 併結**：依 GOV-3 B Evidence 二擇一——無 Evidence → 維持 A／B；有 Evidence → 再開 **C（原則級）** 提案，不得用解釋冒充。  
3. **§0.3 [I] 誠實註**：屬 C 之最輕量分支（非整包原則級）；若 Steward 要「打開 META 只改 [I]」，標 **patch／minor**，仍須拍板句，且 **本輪仍不施作**。

---

## 五、分階段與驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| **P0（本輪）** | 僅產出本計畫；**零 MC [N] diff** | 本檔入 `reports/`；lint 仍 PASS 7／7 |
| **P1（拍板後·可選）** | 路徑 A：裁決模板／內部引用衛生；必要時 B | 抽查新 RULING 母集措辭；無歷史檔改字 |
| **P2（2026-10-14）** | checklist 含 GOV-3 B；決定維持觀察或開原則級 | 有／無 Evidence 書面登錄；禁假關其餘五項仍 open／deferred |
| **P3（僅觸發）** | GOV-3 B → PROPOSAL → 原則級 → 可能 v1.6 | §8.5(b) 二要件＋獨立核驗（028 第 3 點） |

**程式／表**：無。回歸＝`python3 -m tools.constitution_lint report`。

---

## 六、Steward 拍板句（請擇一或改寫簽核）

### 推薦拍板句（預設路徑 A）

> **採納** `reports/augur_mc_post_ultracode_optimization_plan_20260723.md`：**可以但須拍板**之結論成立。授權後續僅走**工具層／文件層措辭衛生**（計畫 §二 #2、#5）；**GOV-3 B 維持觀察觸發**（#1、#7）；**本輪暨至 2026-10-14 前不改 MC [N]、不開 v1.6、不复活出局項、不假關 039 禁止假關項**。§0.3 [I] 誠實註（#3）與 GOV-3 B 入 [N] **另案拍板**。

### 備選拍板句（若要文本自足）

> 採納本計畫，並**另行授權** MC **patch／minor**：僅於 §0.3 或 Appendix 增 [I] 母集誠實句（97[N]+5[I]）；**仍禁止**原則級／§8 [N]／PA／母集計數變更。施作須獨立對抗核驗。

### 備選拍板句（暫緩一切）

> **暫緩**元憲章優化施作；本計畫僅備查。至 2026-10-14 併結再議。

---

## 七、明示本輪不為

* 不修改 `constitution/META-CONSTITUTION.md` 任何 [N]／不升 v1.6。  
* 不開新原則級提案、不改 PA／五原則、不改 102 計數。  
* 不改寫 RULING-017／026 歷史本文。  
* 不把 OT-5／T-KS-6／T-L6-5／025／020 M2／10-14 無 Evidence 項「優化掉」。  
* 可選 commit **僅本計畫檔**（須用戶另授權 git）。

---

## 八、證據索引（精簡）

| 文件 | 用途 |
|---|---|
| `audits/MC-ULTRACODE-L0-20260723.md` | L0 存活／出局／已閉 |
| `audits/L{1–7}-*-ULTRACODE-20260723.md`＋`L5-L7-INTERACTION-*` | 下層無 MC 待開 major |
| `constitution/RULING-2026-028`…`039` | 處置＋禁止假關＋MC 零觸 |
| `ULTRACODE-SCHEDULE.md` residual | 10-14 checklist |
| `reports/augur_l0_gov1_gov3_disposition_plan_20260723.md` | GOV 路徑先例 |
| `reports/augur_l0_l7_residual_omnibus_disposition_plan_20260723.md` | 039 底稿 |

---

*本報告為 [I]；處置權專屬 Constitution Steward。撰寫時 lint PASS 7／7；Ollama 本地濃縮逾時，結論改由 constitution-mcp＋親讀 audit／RULING／排程合成。*

---

## Steward 採納＋工具層已執行（2026-07-23）

* **拍板**：採納本計畫；**授權僅工具層／文件層措辭衛生**（§二 #2、#5）；GOV-3 B 維持觀察；至 2026-10-14 前不改 MC [N]、不開 v1.6、不假關 039 項；§0.3 [I] 與 GOV-3 B 入 [N] **另案**。
* **執行留痕**：`audits/MC-TOOL-HYGIENE-20260723.md`
* **新裁決用語範本**：`constitution/adoption-drafts/RULING-PHRASEOLOGY.md`
* **本輪未動**：`constitution/AUGUR-MC*`／META [N]；規格 [N] 原則條文；RULING-017／026 歷史本文；AL（無新 [N] 義務）。

---

## Steward 新拍板＋MC v1.6 最小優化落地（2026-07-23）

* **覆蓋**：Sole Steward **授權開 MC v1.6 最小優化**——覆蓋上節「10-14 前不開 v1.6」限縮。
* **採路徑**：計畫 §四 **C 最輕量分支**（§二 #3）＋歧義採更小集合。
* **實際納入**：
  1. §0.1 版本 **v1.5→v1.6**
  2. §0.3 **[I] 母集誠實註**（102＝97 [N]＋5 [I] WHY）——**不改** §0.3 [N] 四 bullet、不改計數
  3. Appendix I；RULING-2026-040；AL-2026-044
  4. 已定案程序澄清入 Appendix I [I]（028 第 2–3 點持續；GOV-3 B **維持觀察**）
  5. L1–L7 CS `mc-version`→v1.6；CLAUDE／lint 引用掃齊
* **刻意排除**：GOV-3 B 升 [N]；DEF-2；原則級／§8 [N]／PA；017／026 歷史改字；假關 OT-5／T-KS-6／T-L6-5／025／020 M2／無 Evidence 10-14
* **升版說明**：`audits/MC-V1.6-MINIMAL-20260723.md`
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7；獨立核驗＝RULING-040 §七（待非施作者）
