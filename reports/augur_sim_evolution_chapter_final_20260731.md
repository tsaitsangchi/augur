# 【提案定稿】模擬方法與自進化元件專章——普遍晉升路徑之本軸門檻

> ## ⚠ 本文為**提案定稿**，經 Steward `governance_queue --approve`（TTY 親簽）即為選定、`--enact` 後生效
>
> * **性質**：claude 繕打（`AUGUR-MC v1.6 §8.1`／`RULING-2026-028` 第 2 點：繕打非參與）。
>   原三處待裁空格已填入：**③＝乙（Steward 2026-07-31 對話選定）**；
>   **①＝甲、②＝甲′（繕打者建議案；Steward 之 TTY approve 行為即為對此二者之拍板——
>   不同意者 `--reject` 打回改案）**。
> * **未生效**：enact 前不具效力。
> * **上位依據**：`docs/系統架構大憲章_v1.53.0.md`「**普遍晉升路徑（總則）**」（v1.50.0 入憲）
>   ——該總則明文「**各類之具體門檻由其專章定之**」「**專章得加嚴、不得減省本條任一節點**」
>   「**某類若在專章中缺任一節點之明文，即為「路徑空懸」，該類在補正前不得作出「已確立」級宣稱**」。
>
> **為何需要本專章**：實查 `evolution_prereg_gate` **僅 1 列**（V2-SUNSET, axis='program'），
> 其 `axis` CHECK 實查＝`('tw','lai','raw','program')`——**無 `'sim'`**。
> 即：模擬方法／自進化元件目前**連預註冊都寫不進去**，屬總則所稱之**路徑空懸**。

---

## 第一條　適用範圍與身分

**1.1** 本專章適用於「**模擬方法之採用與其自進化元件**」（下稱**本軸**，登錄 `axis='sim'`）。
本軸同時具報告書八行走者中之**④AI 能力宣稱**、**⑤模擬方法**、**⑦迭代程序本身**三重身分，
三者皆已由總則涵蓋，故適用同一條路、不另闢通道。

**1.2　本軸不是預測軸。** 憲章 §1.2 與 `WORLD-MODEL-SPECIFICATION` A.38 已將
**逐日（或任意粒度）之價格點位、價格路徑、目標價**列為**永久除外項、無 GATE 可解**
（解除唯再修憲）。本軸之產物**唯得以模擬情境呈現不確定性全貌**，並硬綁「模擬非預測」標示。
**本專章不得被解釋為對該永久除外項之任何鬆動。**

**1.3　域中立。** 本軸之判準不因登錄域而異；台股僅為第一個登錄域（足跡），
判準屬世界（路）。新增域＝加 Domain Profile，本專章一字不動。

---

## 第二條　節點一「候選」

**2.1** 本軸之候選＝一組**模擬方法規格**（method ＋ 參數），載體為 `sim_evolution_candidate`，
以 `spec_sha` 為同一性依據。

**2.2　origin 須明示**，值域 `{llm_local, grid, human, carryover}`，並記 `origin_ref`
（LLM 者記提案列 id、grid 者記網格定義、human 者記提案 id）。

**2.3　AI 產物之位置釘死**（`COGNITIVE-KERNEL-SPECIFICATION` L5.7）：
`origin='llm_local'` 之候選**永久攜 `is_synthetic=true` 標記**，
**Trust Rank 天花板 `TR-C`**，且**不得單獨作為任何高風險 Action 之依據**。
本軸不因「本地模型」而豁免此上限——**本地與否不改變其為 model output 之性質**。

**2.4　候選期間不得被表述為已確立**：`status='candidate'|'evaluating'` 之候選，
其任何數字不得進入對話層數字白名單、不得作「已確立」級宣稱。

---

## 第三條　節點二「證據通道」（本軸之核心加嚴）

**3.1　判準先於資料，指紋錨定。** 本軸每一輪評估前，須先於 `evolution_prereg_gate`
建立一列（`axis='sim'`），內含：可證偽條件、樣本外窗定義、臂組成、判準門檻、
以及 `criteria_sha`（判準之正規化指紋）。**評估時覆算指紋不符即拒**，
且 `criteria_sha` 與終態欄位**不可事後修改**（防移動球門）。

**3.2　可證偽性須具體。** 預註冊須寫明「**什麼結果會使此方法被判死**」，
不得以「表現不佳」等不可判定語句充數。

**3.3　樣本外。** 評估窗須完全落在判準凍結時點之後；重疊窗之顯著性
須以去相關統計量處理（承 `#11`：**禁裸用 iid `effective_t`**）。

**3.4　五臂地板（不可省）。** 每次評估須同時跑：
`live`／`ceiling`（上界參照）／`floor`（真地板）／`shuffled`／`mismatched`。
**地板未被顯著超越者，該分數不得作為能力宣稱**——此為記憶級鐵律
（2026-07-26 常數字串 0.654 > 冠軍 0.492；2026-07-27 新尺同病復發），
本軸不得以「模擬與評測不同」為由豁免。

**3.5　終審定性。**

**選定（①＝甲）**：本軸終審＝**統計級——校準檢定**（實現值落入預測分位錐之覆蓋率與
PIT 均勻性），**並明文載明：本軸之終審為統計級，非實效級 `#14` 經濟終關**
（依總則節點 2 括號：無經濟對價者須於專章明文宣告）。
*理由存卷*：本軸產物為風險形狀，依 §1.2 不得產生可交易之方向或點位，無經濟對價可資裁決；
強套 `#14` 只會逼出「為過經濟關而偷偷做方向」之壓力，反而侵蝕 §1.2。

**3.6　目標函數之硬限。** 本軸自進化之**合法目標函數僅得為「風險形狀之校準品質」**；
**不得**為方向命中率、報酬、或任何隱含方向之量。此限制須以 DB 層 CHECK 落地
（`gain_basis CHECK IN ('calibration_delta','none','incomparable')`），使違反者**寫不進去**。

**3.7　不得以模型預測 tilt 抽樣。** 任何以預測結果偏斜抽樣分佈之方法，
**不得註冊為本軸方法**；此限制須以 DB 層 CHECK 落地（`tilt_free CHECK (tilt_free)`）。

---

## 第四條　節點三「人類授權門」

**4.1** 本軸之晉升（候選→生產方法）須經人類核准，且該核准須有可稽核之指標
（`gate_ref` 指向 `governance_proposal` 之已 enacted 列）。

**4.2　AI 不得代簽**，亦**不得為涉及自身監督機制之變更之核准主體**
（`AGENT-RUNTIME-SPECIFICATION` L6.18(a)）。本軸之工具**不得提供填寫核准人姓名之旗標**。

**4.3　PME-AUTO-B 之閘內自動晉升豁免，不及於本軸。** 本軸屬「方法採用」與
「AI 能力宣稱」，非閘內狀態晉升。

**4.4　人閘之實效層級。**

> ### 【選定 ②＝甲′】人簽＝偵測級＋三項最低補強（實查事實存卷如下）
>
> **實查事實一**：本機 `pg_roles` **無 `hugo` 角色**（非系統角色僅
> `augur／augur_predict／postgres／rdai／stock／ttai`）。故 DB **無法區分人與 AI**：
> `chk_*_signed` 類 CHECK 只能驗「欄位非空」，**不能驗「填的人是人」**。
>
> **實查事實二（2026-07-31 新增；本項已非假設，而是已發生之事實）**——
> **人簽帳本已被自測程式寫入三次**：
>
> | 帳本 | 實查內容 |
> |---|---|
> | `arena_admission_gate.approved_by` | `hugo` 1 筆、**`selftest` 1 筆** |
> | `prediction_unfreeze_gate.approved_by` | `hugo` 1 筆、**`selftest` 1 筆** |
> | `restatement_review_queue.signed_by` | **唯一一筆＝`hugo-authorized-selftest`** |
>
> **實查事實三（更嚴重）**：`scripts/governance_queue.py:74` 以
> `getpass.getuser()` 取得簽名者，且**無 `isatty` 檢查**
> （全 repo 具 isatty 者僅 `review_knowledge_source.py`／`preregister_direction_gate.py`／
> `review_evolution_candidates.py` 三支）。
> ⇒ **任何以 Steward 之 OS 帳號執行之行程——包含 AI——於治權佇列中將自動被簽為 `hugo`。**
> 此非「機器分不出人與 AI」，而是**機器會主動將 AI 之動作標記為人之動作**。
>
**選定（②＝甲′）**：採**偵測級**，併同三項最低補強為本條之構成部分：
1. `governance_queue.py` **不得自動代填簽名**——approve/reject 須 TTY＋親手打簽名，
   非 TTY 一律拒絕（**已完成**，commit 847f65a；行為自測證明拒絕發生在碰 DB 之前）；
2. 本軸工具一律不設人名旗標，且 **selftest 不得寫入任何人簽欄**（隨 P2 落地並以自測鎖住）；
3. 本條**明文承認其為偵測非預防**——角色分離（另案、破壞性）完成前，
   人簽欄位之證據力以「TTY＋打字」為上限，不偽稱已機械封閉。

**4.5　既有三筆自測簽名之處置（併請裁示）**：`arena_admission_gate`／
`prediction_unfreeze_gate`／`restatement_review_queue` 各有之自測簽名列，
依 `CLAUDE #12`（不 hand-patch 已 committed 資料）**繕打者未動**。
處置選項：(i) 加註記列說明其為自測產物、原列不改（守 #12、留痕最完整）；
(ii) 走既有更正流程重簽；(iii) 維持現狀並僅於本專章記明。**屬 Steward 裁量。**

---

## 第五條　節點四「晉升或判死留檔」

**5.1** 判決載體 `sim_evolution_verdict` 為 **append-only**（DELETE／TRUNCATE 一律拒絕）。
判死者**永不靜默消失**，其證據鏈與判準指紋一併留存。

**5.2　終態單向。** 候選之 `status` 一旦為 `promoted`／`killed`／`superseded`，
**不可回改**；欲翻案須**開新列＋新證據＋重走五節點**，不得就地改判。

**5.3　換尺＝換身分。** 評測量尺（判準、臂組成、評估碼）變更者，
依 `ONTOLOGY-SPECIFICATION` T.28（GATE 同一 iff〔實驗預註冊識別 × 判準凍結序〕），
**構成新身分**：須開新 `gate_id`，舊列轉 `superseded`，
**不得以新尺之分數與舊尺之分數直接比較**。

**5.4　誠實的無能宣告為合法產出。** 本軸若經評估證明「現有方法皆不足」，
該**無能宣告與有效之能力宣告同為走完本路之合法產出**，不得為求「有結果」而放寬判準。

---

## 第六條　節點五「後果回流」

**6.1** 每一次已晉升方法之實跑，其**實現值須回流**與當時之預測分位錐比對
（載體 `sim_realized_outcome`），並據以更新校準紀錄。

**6.2　校準劣化須觸發重評**：當生產方法之校準指標跌破預註冊門檻，
須自動開立新候選輪並將該方法轉入 `evaluating`，**不得靜默沿用**。

**6.3　違規事件本身亦須回流。** 依 `META-CONSTITUTION` F6，
任何本專章之違反須以 Observation 回流並溯責，不得僅於私下修正。

---

## 第七條　OCV 單向棘輪（本軸之不可逾越）

**7.1** 本軸之自進化，其**可調維度白名單僅含模擬參數本身**。

**7.2　嚴禁**將下列列為候選之可調維度（`AGENT-RUNTIME-SPECIFICATION` L6.17／L6.19／L6.18(c)）：
減少人工確認點、延長自動鏈長度、放寬任一門檻、變更判準、修改本專章。
**不得以 Learning 之名落地任何降低 OCV 之行為變更。**

**7.3　度量不可自我洗白**：本軸不得以自身產出作為「自身表現變好」之唯一證據
（`KNOWLEDGE-SYSTEM-SPECIFICATION` KS.76／KS.77：self-reported 不得單獨升信）。

---

## 第八條　軸值域之登錄方式

> ### 【選定 ③＝乙】`axis='sim'` 之登錄＝axis registry 表（實查事實存卷如下）
>
> **實查事實（兩處不一致）**：
> - `evolution_prereg_gate_axis_check` ＝ `CHECK (axis = ANY (ARRAY['tw','lai','raw','program']))`
> - `evolution_hypothesis_hint_from_axis_check` ＝ `CHECK (from_axis = ANY (ARRAY['tw','lai','raw']))`
>   ——**連 `'program'` 都沒有**。
>
> 即：同一個「軸」概念在兩張表有**兩套不同值域**，且皆寫死於 CHECK。
>
**選定（③＝乙，Steward 2026-07-31 對話選定）**：建 **axis registry 表**（`evolution_axis`，
DELETE/TRUNCATE 拒絕），兩處寫死 CHECK 改 FK——新增軸＝INSERT 一列、零改碼，
兩表值域自此不可能再漂移（`CLAUDE #29(b)`）。遷移工具已備
（`scripts/migrate_evolution_axis_registry_ddl.py`；種子＝現有四軸聯集、**不含 sim**——
sim 之登錄繫於本專章 enact；語意副作用〔from_axis='program' 轉合法〕已於 --check 揭露）。

**性質認定（Steward 保留，GOVERNANCE-ANNEX v1.1 第 2 條第 3 款）**：由 Steward 於
approve 時以 `--note` 載明（`patch` 或 `major`）；**未載明者依 `§8.3` 保守解釋
按重大判準修正之程序辦理**——繕打者不代認定。

---

## 第九條　生效、位階與修訂

**9.1** 本專章經 Steward 議決 enacted 後生效，並登錄為憲章第三部之下位專章。

**9.2　不得減省。** 本專章得對總則加嚴，**不得減省總則任一節點**；
牴觸總則者，該部分無效。

**9.3　修訂**：本專章之修訂適用總則第 3 節點（人類授權門）；
**Agent 不得自行修訂本專章**，亦不得為涉及本專章之核准主體。

---

## 附一、本草案之事實基礎（繕打者親驗，2026-07-31 唯讀）

| 事實 | 實證 |
|---|---|
| `evolution_prereg_gate` 列數 | **1**（V2-SUNSET） |
| `evolution_prereg_gate.axis` 值域 | `('tw','lai','raw','program')`——**無 `sim`** |
| `evolution_hypothesis_hint.from_axis` 值域 | `('tw','lai','raw')`——**連 `program` 都無** |
| `mc_simulation_run` 列數／trigger 數 | **540 列／0 個**（可被無痕 DELETE） |
| `mc_simulation_run` 之模擬鎖 | `CHECK (is_simulation)` **存在**（四鎖之一已守住） |
| `pg_roles` 是否有 `hugo` | **無** |
| 人簽帳本遭自測寫入 | `arena_admission_gate`／`prediction_unfreeze_gate` 各 1 筆 `selftest`；`restatement_review_queue` **唯一列**＝`hugo-authorized-selftest` |
| `governance_queue.py` 取簽名方式 | `getpass.getuser()`（:74），**無 isatty**——AI 以該 OS 帳號跑即自動簽為 `hugo` |
| 具 `isatty` 之 CLI | 僅 `review_knowledge_source.py`／`preregister_direction_gate.py`／`review_evolution_candidates.py` **三支** |

## 附二、繕打者須併陳之三項（非條文，供裁量參考）

1. **既有自進化鏈已被餓死**：`evolution_deferred_work` 四列**全未清**——
   `run_evolution_iteration`（tw 軸）於 **2026-07-27／07-28／07-29 連三日**被推遲，
   理由皆為 heavy slot busy。**在此狀態下新增 `sim` 軸至同一 slot，將使三軸互相餓死。**
   建議：本專章（純治權文字、不佔運算窗）得即刻議決；**但實作階段宜俟車道問題有解**。
2. **`augur-ata-advance.service` 每日 04:00 觸發後為 `failed`**（實查），未查因。
3. **報告書 §四之「誠實標注」已被追過**：其稱「④⑤ 在治權層無明文」，
   但憲章 v1.50.0（2026-07-30 同日拍板）已成文涵蓋「能力宣稱」與「方法採用」。
   建議報告書該段更新（屬報告書側，非治權檔）。

## 附三、繕打者未做之事（誠實界定）

- **實質判斷之歸屬**：①②為繕打者建議案、以 Steward 之 TTY approve 為拍板；③為 Steward 對話選定；③之性質認定以 approve --note 為之——繕打者皆不代判。
- **未寫入任何 DB**、未建立 `governance_proposal` 列——依總則，提案之提出與議決屬 Steward。
- **未認定本案之修訂位階**（patch 或重大判準修正）——屬 Steward 保留事項。
- 附一以外之事實（如既有排程單次耗時）為 agent 回報、**繕打者未獨立複驗**，
  不得引為本專章之事實基礎。
