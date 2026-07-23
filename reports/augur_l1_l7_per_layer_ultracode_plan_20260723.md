# L1–L7 各別（單層）ultracode 優化——可行性評估＋計畫草稿

**日期**: 2026-07-23 ｜ **性質**: plan-first（CLAUDE.md #20，本輪僅評估＋草案，**不開跑**）
**觸發**: 用戶「可以進行 L1 到 L7 各別的 ultracode 優化嗎？」
**方法 SSOT**: [`ULTRACODE-SCHEDULE.md`](../ULTRACODE-SCHEDULE.md)（單層 6–8 維窮盡攻擊排程）；區別於已執行完之 [`LAYER-SEALING-SCHEDULE.md`](../LAYER-SEALING-SCHEDULE.md) 第三階段（跨層交互檢查，3a／3b）
**本輪產出**: 只讀評估＋計畫草稿；**未**開跑任何一層真正 ultracode、**未**改 `[N]`、**未** commit／push

---

## 0. 一句 Verdict

**有條件可行**——排程／方法骨架已備（`ULTRACODE-SCHEDULE.md`）、八層皆已 G5 蓋章（前置齊），但需先處理下列 4 項條件（見 §1），且**不建議七層一次性齊發**，應**依規格依賴鏈循序**、每層走完整 Find→Verify→Critic→Synthesize→Steward 呈核才進下一層（比照 `LAYER-SEALING-SCHEDULE.md` 既定紀律與 CLAUDE.md #19）。

---

## 1. 前置條件清單

| # | 條件 | 現況 | 是否已足 |
|---|---|---|---|
| **C1** | 八層須先 G5 蓋章（避免對未定案文本做深度攻擊） | `LAYER-SEALING-SCHEDULE.md`：L0–L7 皆 ✅ 已蓋章（L5＝v1.0 provisional·§8.2 延後、L7＝§8.2 條件通過，二者為「有條件」蓋章，非瑕疵） | ✅ 齊（含二層條件蓋章之揭露） |
| **C2** | 交互 ultracode（3a／3b）之 major 應先落地，避免單層審查與交互審查互相踩腳 | 3a（RULING-2026-022，4 major）已裁決；3b（本日，M-IX-1／M-IX-2）**已修但尚未 commit**（工作樹 untracked：`audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md`／`constitution/RULING-2026-027-*.md`／`reports/augur_l0_l7_interaction_ultracode_plan_20260723.md`；已改動 `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md`／`specs/COGNITIVE-KERNEL-SPECIFICATION.md`） | ⚠️ **語意已足（KS／CK 現行內容已含修正），但 git 未收斂**——建議先請用戶確認/commit 這批，取得乾淨 HEAD 作各層 ultracode 之審計基線（各層報告慣例會記錄 `git HEAD`） |
| **C3** | 另一批進行中的「執行指令矩陣全量補齊」（RULING-2026-026／AL-2026-029）不得與規格文本審查混淆 | 工作樹另有 26 檔未提交改動，多數為 `augur_proxy/*`、`tools/constitution_lint/*`、`tools/constitution_mcp/*`、`tools/local_llm_mcp/*`、`ops/gpu-verify/*` 之 docstring 補「執行指令矩陣」——**範圍是 Python 執行入口，不觸 `specs/*.md`／`META-CONSTITUTION.md`**，與 ultracode 攻擊面（規格文本語意）不重疊 | ✅ **不構成硬性阻擋**（不同檔案集合），但屬同時進行中的重大改動——建議依 CLAUDE.md #19「一支一支檢視、用戶過目再進下一」，先收斂此波再開新的七層審查，避免工作樹同時掛兩條大改動、事後難以歸因 diff |
| **C4** | L0 之定位——用戶問句只提「L1 到 L7」，未含 L0 | `ULTRACODE-SCHEDULE.md` 現況（**2026-07-23 更新，見 §9**）：L0 已有產出——`audits/MC-ULTRACODE-L0-20260723.md`（L0 單層 ultracode 呈核報告，8 維，2 major＋2 minor 存活）**已於本日產出**，非空轉；L1 仍標「🔄 執行中」、至今無產出。L0 為 meta-constitution，L1–L7 之定義／投影／§8.3 判準皆以 L0 為源；L0 報告已翻出 `GOV`（治理自封性，GOV-1／GOV-3 major）疑問，可能回頭影響解讀 L1–L7 之基準——**但尚未經 Steward 裁決**，L0 蓋章地位本身未動搖（該報告 §五結論） | ⚠️ **需用戶澄清**：L0 之 2 項 major 如何處置（RULING）？是否要與 L1 同批起跑／L1 是否現在開跑？見 §4 建議、§9 拍板紀錄 |

**結論**：C1 已足；C2／C3 建議「先收斂、非強制阻擋」；C4 是唯一**須用戶明確表態**才能定案順序的項目。

---

## 2. 是否與「交互 ultracode」衝突

**不衝突，互補**（`ULTRACODE-SCHEDULE.md` 明文：「單層 ultracode 與跨層交互檢查為互補而非替代」）。細節：

- **3a（概念層 L1–4，RULING-2026-022）**與**3b（執行層 L5–7，RULING-2026-027）**查的是「接縫」——層與層之間、貫穿層帶之不變式；**單層 ultracode** 查的是「某一層本體」6–8 維窮盡攻擊（該層規格自身之定義閉環、可判定性、幽靈落點等）。攻擊面不同、方法骨架相同（Find→Verify→Critic→Synthesize）。
- **重疊風險（非衝突，屬正常查核）**：單層 L4(KS)／L5(CK) ultracode 親讀 `KDI.18`／`L5.10` 等剛被 3b 修正之落點時，會再次讀到（已修正後的）文本——這是正常覆核，不會重複開 major（因缺陷已消除），但**執行前務必先讓 C2 的修正落入 git 基線**，否則審查代理讀到的「當前檔案內容」與稽核報告記錄的 `git HEAD` 對不上，事後難以複核。
- **既定處置模式一致**：3a／3b 皆遵守「只讀→呈核→Steward RULING→執行層落地 patch」四步，單層 ultracode 應延用同一模式（見 §5）。

---

## 3. L0 是否須先完成／先收斂

**建議：L0 應與 L1 同批起跑或至少先於 L2–L7**，理由：

1. **依賴鏈方向**：`AUGUR-MC §0.6` lex superior——L0 是所有下層規格之解釋基準；L1–L7 之定義／§8.3 判準／102 母集計數皆「投影」自 L0。若 L0 之 `DEF`（定義閉包）／`GOV`（治理自封性）／`PRJ`（向下投影完整性）三維翻出問題，可能改變下層某些條款的可判定判準，屆時 L2–L7 之審查結論需要**部分重做**，非僅補丁。
2. **排程本身之設計**：`ULTRACODE-SCHEDULE.md` 現況欄把 L0、L1 標為**同批**「🔄 執行中」，L2–L7 才是「⏳ 排定」——暗示原始設計意圖是 L0／L1 先行，L2–L7 待其後。
3. **現況是空轉**：L0、L1 這兩個「執行中」狀態自 2026-07-19 建檔以來**無任何產出**（`audits/` 下無對應單層報告），應視為「尚未真正開始」而非「已有初步結論可延用」。

**若用戶堅持只做 L1–L7、L0 另案或暫緩**：技術上可行（L1–L7 各層審查方法本身不依賴 L0 審查結果才能啟動），但需在每層報告「誠實界限」節載明「本輪未含 L0 本體攻擊，L0→本層投影僅按現行文本抽樣，非窮盡覆核」——比照 3b 報告已有的揭露慣例。

---

## 4. 建議順序

**不建議七層同時全開**（違 CLAUDE.md #28「非必要不 fan-out」與 #19「一支一支檢視」；且 `LAYER-SEALING-SCHEDULE.md` 之既定紀律亦是逐層而非齊發）。建議：

```
（先定案 C4）
  ├─ 若 L0 同批 → L0 ∥ L1 → 待雙方 Steward 呈核裁決 → L2 → L3 → L4 → L5 → L6 → L7
  └─ 若 L0 另案暫緩 → L1 → L2 → L3 → L4 → L5 → L6 → L7（各層報告揭露「未含 L0 窮盡覆核」）
```

**循序理由**（依風險與依賴鏈，非任意）：

| 順位 | 層 | 為何排此處 |
|---|---|---|
| 1 | **L1 WM** | 全域最高槓桿（`FMT` §11 合規聲明格式定義權自洽；102 母集授權來源）；下層 L2–L7 之覆蓋清單／defers 機制皆從此層定義衍生，先查最能早發現連鎖問題 |
| 2 | **L2 ONT** | 型別體系為 L3–L7 之 Entity／型別解析基礎 |
| 3 | **L3 ID** | lifecycle／Evidence 覆蓋為 L4 KS 之上游 |
| 4 | **L4 KS** | 剛被 3b 動過（M-IX-1），適合趁記憶新鮮覆核；且是 L5 CK 之直接上游（KDO→LDI） |
| 5 | **L5 CK** | 剛被 3b 動過（M-IX-2）＋仍 provisional（§8.2 延後，復審 2026-10-14）——單層 ultracode 之 `PRV` 維度正好呼應此地位之實質後果 |
| 6 | **L6 AR** | 已無待決 major（僅 2 minor 順修），風險相對低 |
| 7 | **L7 Infra** | §8.2 條件通過、residual (iii)(iv)(vi) 分階段中；留最後，累積前六層之校準經驗再攻最複雜之權限/物理層 |

每層跑完後**須先经 Steward 呈核裁決（major→RULING）**，才進下一層——不因「排程已列好順序」而搶跑，比照 `LAYER-SEALING-SCHEDULE.md` §執行順序之既定模式。

---

## 5. 每層交付物路徑慣例

| 產物 | 路徑慣例 | 先例 |
|---|---|---|
| 呈核報告（findings） | `audits/L{n}-{SPEC縮寫}-ULTRACODE-{YYYYMMDD}.md`（如 `audits/L1-WM-ULTRACODE-20260723.md`） | 命名比照既有 `audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md`、`*-THREE-MIRROR-REVIEW-2026-07-18.md` |
| 計畫（如該層規模需個別 plan） | `reports/augur_l{n}_{spec}_ultracode_plan_{YYYYMMDD}.md` | 比照 `reports/augur_l0_l7_interaction_ultracode_plan_20260723.md`；若沿用本檔＋`ULTRACODE-SCHEDULE.md` 已足以交代方法，可不逐層另開一份 plan |
| RULING（major 處置） | `constitution/RULING-2026-0XX-L{n}-ULTRACODE-DISPOSITION.md` | 比照 `RULING-2026-020`／`022`／`027` |
| Amendment Log | `constitution/AMENDMENT-LOG.md` 新增 `AL-2026-0XX` | 既定慣例 |
| 排程狀態更新 | `ULTRACODE-SCHEDULE.md` 該層狀態欄 🔄／✅＋「產出」欄補連結 | 既定表格結構 |

---

## 6. 只讀審計 vs 允許修 medium／editorial——邊界釐清

**對齊既定慣例：預設全程只讀，不因 severity 而有例外。**

- `ULTRACODE-SCHEDULE.md` 共用鐵律 #1 明文：「審查官不得修改任何檔案一字元——只讀、只分析、只回報」。此鐵律**未以 severity 分級**，即 medium／editorial 亦不在審查輪次中直接改。
- 3b 的實際處置示範了正確流程：major（M-IX-1／M-IX-2）經 Steward「核示『修這兩項』」→ 另開 RULING-2026-027（§8.6 patch）→ 執行層才落地；4 項 medium（F-IX-3…6）**明文留待另案或例行編輯週期**，未在同輪順手修。
- 因此 L1–L7 單層 ultracode 應延用此模式：**呈核報告只列 findings＋severity＋雙反駁結果，不在報告產出的同一輪次修改任何 `[N]`**；後續由 Steward 决定 (a) major→開 RULING，(b) medium/editorial→是否同案順修或延後。

**需用戶再拍板之處**：是否要**預先**授權「本輪 medium／editorial 若證據確鑿可與 major 同案一次 RULING 處置」（如 3b 的模式），或維持**逐案**（每次呈核後才個別決定）。此為決策層事項，本評估不代為拍板。

---

## 7. 誠實界限

- 本檔為**評估＋計畫草稿**，非已執行之審查；C4（L0 定位）待用戶表態，其餘結論以現有 git 工作樹與治權文件現況為據（`git log`／`git status`／`git diff --stat` 已核實，非推測）。
- 「L0、L1 現況🔄執行中」之研判為**狀態解讀**（無對應產出檔＝疑似空轉），非對 L0/L1 本體之攻擊性審查結論；**此研判於 L1 仍適用，於 L0 已被 2026-07-23 之後續產出取代**（見 §9：`audits/MC-ULTRACODE-L0-20260723.md` 已產出，非空轉）。
- 本輪未讀 `META-CONSTITUTION.md`／`specs/*.md` 全文逐字（依 local-mcp-routing 規則，僅抽樣既有審計/排程文件之摘要與 git 事實），若後續實際開跑某層，該層審查代理仍須親讀正文（非本評估之抽樣可替代）。

---

## 8. 產物索引

| 產物 | 路徑 |
|---|---|
| 本計畫 | `reports/augur_l1_l7_per_layer_ultracode_plan_20260723.md` |
| 方法 SSOT | `ULTRACODE-SCHEDULE.md` |
| 交互檢查對照 | `LAYER-SEALING-SCHEDULE.md` §第三階段 |
| 交互審查先例 | `audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md`、`constitution/RULING-2026-027-L5-L7-INTERACTION-DISPOSITION.md` |
| L0 單層 ultracode 呈核報告 | `audits/MC-ULTRACODE-L0-20260723.md`（§9 更新） |

---

## 9. Steward 拍板紀錄（2026-07-23）

回應本檔 §6 末段所留之待拍板事項：

**拍板文案**：「允許 medium 與 major 同案順修。」

- **授權範圍**：ultracode 呈核後，同一處置案（同一 RULING／同一執行波次）得將 **major 與 medium 一併順修**——**仍須 RULING／Amendment Log 登錄，不因 severity（medium）而跳過呈核**。此為對 §6 所留選項（「逐案」vs「預先」）之**預先**授權，但範圍限於「同案（同一 RULING）」，非全面豁免呈核步驟。
- **明確未授權事項**：本拍板**未**授權略過「只讀 Find→Verify→Critic→Synthesize」呈核步驟；流程仍是「只讀發現 → 呈核 → 同案 RULING（含 major＋medium）→ 執行層落地 patch」——`ULTRACODE-SCHEDULE.md` 共用鐵律 #1（「審查官不得修改任何檔案一字元」）不受本拍板影響、繼續適用於呈核輪次本身。
- **對 §1 C4 之更正**：本檔原載「L0、L1……至今無任一產出」已不實——`audits/MC-ULTRACODE-L0-20260723.md`（L0 單層呈核報告）已於本日產出，詳見已更新之 §1 C4 表格列。本更正僅訂正事實描述，**不代表**該報告之 2 項 major（GOV-1、GOV-3）已經 RULING 裁決。
- **本輪仍待用戶另句拍板、未定案之事項**：**是否自 L1 開始開跑單層 ultracode**（或 L0 之 major 如何處置）。本次拍板僅登錄「(2) 同案順修授權範圍」，**不構成**開跑 L1（或任何一層）之授權；§1 C4／§4 建議順序之選擇仍待用戶明示。
