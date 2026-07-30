# 留痕 — 原則精華 #1 去供應商依賴（乙-2）：v1.10.0 → v1.11.0

* **性質**：領域治權檔修訂之執行留痕（[I] 記錄；判準內涵零變動）
* **拍板**：hugo 對話拍板 2026-07-30，一字「**乙-2**」（回應計畫書 `reports/augur_treaty_core_alignment_plan_20260730.md` §四 乙-2 所列之措辭與影響檔）
* **繕打**：claude（Fable 5）——**不冒充親簽**（`AUGUR-MC v1.6 §8.1`）；本檔未代填任何 approved_by／decided_by 欄位
* **層級**：領域治權檔（Layer 4 登錄）；**MC／PA／五原則 [N] 零觸**；非 Steward RULING，故不佔 AL 號（同 v1.9.1 對話拍板先例）

## 一、修訂內容（逐字對照）

| | 文字 |
|---|---|
| **原（v1.10.0 #1 WHAT）** | 任一特徵值必須是「真實 FinMind/FRED API 值經數學轉換」而得；… |
| **新（v1.11.0 #1 WHAT）** | 任一特徵值必須是「**經登錄觀測通道之真實值**經數學轉換」而得；…**真實性繫於通道之登錄、不繫於供應商名**（過 `AUGUR-KS v1.1 §KS.4` 刪名測試）——**現行通道清單 [I]**：FinMind／FRED；新增通道須經 World Concept Registry 登錄（`AUGUR-WM v1.0 §WM.35–36`）後，其值方為本條所稱之真實值。 |

**WHY／ENFORCE 一字未動**；`imputed / zero-fill / hardcoded / 推估 = 幻像`、`算不出真實值即不寫入（缺列）`、completeness gate 全部原樣。

## 二、缺陷根據（親驗）

- `AUGUR-KS v1.1 §KS.4` 刪名測試：刪去產品／供應商名後條款概念內涵須不變方為合法指名。原 #1 刪名後「真實 API 值」失所指——以供應商定義「何謂真實」。
- 覆蓋落差：新登錄域之觀測值若非由該二通道供應，原條文**字面不覆蓋**（而 #1 為 ★ 三大命脈，覆蓋落差不可留）。
- 對照組：#17 原已寫「對 FinMind／FRED（**及任何 API**）」＝合法例示，**不需動**；#18 之 `/datalist` 為現行通道之取得程序（[I] 操作指引），非「真實」之定義依據，**不需動**。→ 本次僅改 #1（最小邊界 CLAUDE #3）。

## 三、跨檔級聯（#19 一致性；共 11 行 ＋ 2 檔更名）

| 檔 | 動作 |
|---|---|
| `docs/原則精華_v1.10.0.md` | → `docs/原則精華_v1.11.0.md`（git mv 保譜系）；標題／合規指向／演進記錄新增 v1.11.0 條目；順修內文「憲章 v1.48.0」幽靈版 → v1.49.0 |
| `docs/compliance/CS-原則精華_v1.10.0.md` | → `CS-原則精華_v1.11.0.md`；正文 SSOT／spec-version／archive-path／date／author 更新；新增「本版增量」與「刪名測試自陳」二欄 |
| `README.md`／`HANDOFF.md`／`CLAUDE.md`／`docs/系統架構大憲章_v1.49.0.md`／`constitution/GOVERNANCE-MAP.md`／`docs/remediation/AUD-02-raw-supersede-log.md` | 指向與版本字串級聯（11 行） |
| **未動（刻意）** | `docs/系統架構大憲章_v1.47.0.md`（SUPERSEDED 凍結史料，改之即竄改記錄）、`constitution/AMENDMENT-LOG.md`（該簿記 Steward RULING）、`RULING-2026-041`、`audits/*`、`reports/*`、`handoff_memory/*`（皆為當時記錄） |

## 四、機械驗證

- `python3 scripts/check_treaty_refs.py` → **全綠**（級聯後零死指標；本 lint 於同日新建，本案為其首次實戰，並據本案結果加一條「SUPERSEDED 凍結檔豁免 dead_ref」之設計修正）
- `python3 scripts/check_cmd_matrix.py` → 425 支全通過
- 升版級別說明：按本檔升版哲學，此類措辭對齊亦可歸「純文字微修正（不升版）」（先例 v1.7.1）；本次**依 Steward 拍板之計畫書所列軌別**執行為 minor 升版，並於演進記錄中誠實載明此判斷。

## 五、殘餘（不假關）

- 乙-1（靈魂定義句 vs WM.7）、乙-3（一條路總則）、乙-4（replay 作用域入憲）、乙-5（KH10 vs P2.E1）、乙-6（CLAUDE L6 標注）**均未拍板、未執行**，仍列計畫書 §四待裁。
- 12-agent 治權對抗稽核（`wf_175c81eb-c2c`）尚在執行，其發現未併入本案。
