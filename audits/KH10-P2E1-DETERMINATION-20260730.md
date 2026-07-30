# P8 結案 — KH10 一律准入 vs `§P2.E1`／`§P5.W5`：Steward 認定（甲）＋當日補正

* **Steward 裁示（逐字）**：「**甲成立**」（hugo，2026-07-30）；自毀條款期限「**改今天**」（hugo，2026-07-30）
* **選案**：**A｜補正形式、保留機制**（非 B 收窄、非 C 明記缺口）
* **繕打**：claude（Fable 5）〔不冒充親簽 `AUGUR-MC v1.6 §8.1`；本檔未代填任何 approved_by／decided_by〕
* **分析底稿**：`reports/augur_kh10_p2e1_constitutionality_20260730.md`（含爭點界定、消解論據、殘餘 C-1～C-3、A／B／C 三案）
* **變更等級**：本批之機制變更為**緊縮類**（增加義務、fail-closed），依大憲章 v1.51.0 第六部通則二 (b) 得為 patch

---

## 一、認定內容（甲）

**§P5.W5 認定**：KH10 一律准入所移除者為 **item 層**之 `approve`／`activate`（`curation.HUMAN_ONLY = set()` 實查為空集）。經實查，**來源層人簽仍由 DB CHECK `chk_ks_active_needs_approval` 機械強制**（`knowledge_source` 具 `approval_status`／`approved_by`／`approved_at` 三欄），且**每一 item 必經一個已核可之來源**（active 才能抓、active 需核可）。故**介入點之覆蓋完整性未降，僅粒度由 item 移至 source**。

**核心解釋（Steward 之裁示，非 Agent 之判斷）**：**OCV D 分量（逐案可介入點密度）之量測以介入點之有效性與覆蓋完整性為準，不以件數計。** 據此，本機制不構成 `§P5.W5` 意義下之弱化。

> **本認定不可豁免之背景**：`§P5.W5` 屬 `§8.4` **不可豁免核心**（連履行時程亦不得豁免）——故原「走豁免」之路徑（我先前隱含之乙案）**憲法上不成立**，真實選擇僅甲（不弱化說）或 B（收窄機制）。此點於呈簽時已更正。

## 二、附條件：自毀條款（期限＝**當日**，已履行）

Steward 將補正時程由建議之 2026-08-31 **改為當日（2026-07-30）**——即**不給緩衝**：C 類缺口當日補正，否則認定失效、機制自動退回 depth 3。以下為當日施作與實測。

### C-3｜`require_kh8`／`require_kh9` 空轉閘 → 真要件 ✅

**病灶**（分析 F7）：二旗標經 `load_gate()` 讀入後**無任何決策路徑消費**（全 repo grep 僅命中 DDL／migration／`load_gate` 自身）。**更深的洞（本次施作時查獲，分析未載）**：`advance()` 之推進迴圈對 `skipped` 是 `continue`——故 KH8 若因「表未建」回 `skipped`，迴圈**繼續往上推**，depth 9 一過即升至 9＝**證據要件被整層繞過**。

**處置**（`src/augur/knowledge/auto_admit.py`）：該層若被 gate 要求（`require_kh8`／`require_kh9` 為真），`skipped` **視同 fail、不得繞過**（fail-closed），並記 `action=require_kh{d}_fail_closed`。

### C-2｜`confidence_band` 零變異 → 鑑別力檢定 fail-closed ✅

**病灶**（分析 F9）：`knowhow_evidence_weight` **145,949 列 100% `band='high'`**。

**根因（本次實查，與分析之推測不同）**：**並非寫死**——公式為真（`0.35*cite_norm+0.25*terminal+0.25*embed+0.15*kh4_ok-0.40*contra`）且 `evidence_score` 確有變異（**0.72–1.0**）。真因是**母體選擇效應**：權重只算在「已終態＋已嵌入＋已 eligible」之 item 上，致 `terminal`／`embed`／`kh4_ok` 三分量**對全母體恆 1.0**（實查分量組合：136,554 列為 `cite_norm=0.2, terminal=1.0, embed=1.0, kh4_ok=1.0, contra=0.0`），故 score 底線恆 `0.72` → **必落 high**。結論：**本指標結構上不可能鑑別**。

**處置**（`src/augur/knowledge/evidence.py`）：新增 `population_discriminates(cur)`——band 種類 < 2 即判無鑑別力；`evaluate_item_evidence()` 於回 pass 前先過此檢，不通過則回 `verdict=fail, action=kh8_non_discriminating`（**帳仍寫、可溯源**，但不得回 pass）。原則：**零變異之量測不得充當證據**（承 `§P4.E7`／KS 反自我背書之精神）。

**實測（live，非自測）**：
```
鑑別力檢定: {'ok': False, 'bands': ['high'], 'n': 145949}
depth-8 實測(item=278017): verdict=fail action=kh8_non_discriminating
  （該 item band=high score=1.0 cite=5 —— 修前必 pass）
```
`python -m augur.knowledge.evidence --selftest` 與 `python -m augur.knowledge.auto_admit --selftest` 皆全通過。

### C-1｜可答性升格構成權威性宣稱、以自身產出為唯一依據

由 §一之甲認定處理：**代償介入點＝來源層人簽（機械強制）**，故升格所依非「僅自身產出」——每件 item 之可答性上溯必達一個人類核可之來源。

## 三、本批之實質後果（誠實揭露，不粉飾）

**新閘使 depth-8 以上之新推進實質停止**，直到 KH8 母體具鑑別力（須擴大加權母體至含未終態／未嵌入／未 eligible 者，使三分量產生變異）。

- **不影響**既有已升格之 state（不回溯、不刪列）。
- **影響** advisor 可答面之**成長**（新 item 停在 depth 7）。
- **這不是 B 案**（未將 `max_auto_depth` 由 9 降至 3、未使 145,949 件退出可答空間），但**確實是實質收緊**——依通則二 (b) 屬緊縮類、得為 patch。
- **解除條件**：KH8 加權母體擴大並實測 band 出現 ≥2 種後，`population_discriminates` 自動回 ok=True，閘自行解除——**無須再開一次會**（自癒式閘，非人工旗標）。

## 四、未辦與待議（不假關）

| 項 | 狀態 |
|---|---|
| KH8 加權母體擴大（使指標真有鑑別力） | **未辦**——屬 KH8 之實作工作，非本認定之條件；已列為閘之自動解除條件 |
| 分析呈報之併案：KH 十層計畫書 L66／L592–593 仍寫「approve／activate 仍唯人」，與大憲章 v1.51.0 L186 及 `curation.HUMAN_ONLY=set()` **直接矛盾** | **未辦**——該檔非本批範圍，呈報待處置（不論 A／B／C 皆須修） |
| 三帳本表皆無 Confidence 槽（分析 F11） | **未辦**——結構性缺口，須另案 |

## 五、程序合規自陳

- 本檔之**核心解釋**（OCV D 分量之量測基準）為 Steward 裁示「甲成立」所採，**非 Agent 之判斷**（`§8.1`）。
- 本批之 code 變更為**緊縮類**（增 fail-closed 檢），未放寬任何義務，故不觸發通則二 (a) 之 OCV 前後對照要求；惟本檔已載其實質後果。
- **未第二次獨立核驗**——依 RULING-2026-028 第 3 點，本批 code 變更之獨立核驗待排（前一批 specs patch 之核驗即判 FAIL 並查獲 10 則，故此處不以自測綠燈自稱已驗）。
