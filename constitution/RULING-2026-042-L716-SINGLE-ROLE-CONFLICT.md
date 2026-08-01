# Augur Steward 裁決第 2026-042 號

**L7.16 與單一角色部署之正面衝突登錄——既成事實認定＋適用性註記（spec 零改；殘餘風險明載、不粉飾）**

* **依據**：`AUGUR-MC v1.6 §0.6`（lex superior）；`§8.3`（存疑保守）；`AUGUR-L7 v1.0` L7.16（[N]）、L7.18(b)；`RULING-2026-039` 八.2（L7.16 觸發＝雙角色部署議程或 2026-10-14 併審）；決定留痕 `reports/augur_db_role_architecture_submission_20260731.md` §6（含 §6.2 OCV 四項對照、§6.3 消失保證列示）；執行留痕 `reports/augur_single_role_consolidation_plan_20260731.md`；WM.35 新證據認定 `GROUNDING-MAP.md`「2026-07-31 S22 定案」段
* **裁決人**：Constitution Steward（tsaitsangchi）
* **登錄**：Amendment Log **AL-2026-046**
* **性質**：**衝突登錄＋適用性註記**——**不觸** L7 [N] 本文、**不豁免** L7.16 義務、**不假關** 2026-10-14 各項、**不重開** §8.2；零 DDL、零行為碼變更

## 〇、衝突摘要與位階

| 側 | 內容 | 位階 |
|---|---|---|
| `L7.16` | 受保護儲存物件之 owner ≠ 應用運行角色；(e) 同屬一權限主體者，該不變式**在憲章意義上不成立** | **L7 [N]**（carries `§P4.E3`／`§P3.E2`／`§P5.W4`／`§8.3`） |
| 物理現實（2026-07-31 起） | 單一角色 `augur`（superuser）＝owner ＝應用運行角色＝AI 操作角色；`augur_predict` 退役、owner 分離設計放棄（D13-3 乙） | 部署既成事實（Steward 親跑，程序上人類權威成立） |

**衝突點**：L7.16(a)(b)(c) 之角色二分於現行部署**物理上不存在**；而 spec 未動、AL 零登錄＝治權文件與物理現實漂移。
**本裁性質**：**登錄與註記**，非修法、非豁免——L7.16 [N] 本文一字不動；依 §8.3 存疑保守，衝突範圍內之認定從嚴（見主文二 2）。

## 一、採案

**採甲案（登錄＋註記）**：認定既成事實＋L7.16 適用性註記，spec 零改；同 commit 恢復一盞條件式機械紅燈（主文二 5）。
* **不採**修 L7 [N] 本文（乙案）——動 [N] 屬 major、且會為遷就現況弱化義務文字，違 §P5.W5 方向。
* **不採**不登錄（丙案）——漂移入常態、新讀者持續誤信文件，腐爛型。

## 二、主文

1. **既成事實認定**：2026-07-31「augur＝全部」單一化整併（D-1…D-7；S9／S10／S11 Steward 親跑）為 **Steward 裁決之既成事實**——決定留痕＝D13 呈案 §6、OCV 四項對照＝§6.2（人類介入點 −1、揭露比例下降；「確屬治權變更、已由 Steward 拍板」）、執行留痕＝整併計畫書 §0.5。本裁將該既成事實**正式登錄入憲法層帳簿**（AL-2026-046），補足「治權變更已拍板但 AL 零登錄」之簿記缺口。
2. **L7.16 適用性註記**：於現行單一角色部署下，依 L7.16(e) 逐字判準，受保護儲存物件之 append-only／只失效不刪除等不變式之 **DB 權限層強制「在憲章意義上不成立」**（存疑即推定不成立，§8.3）。其**現行實際承載**＝① **trigger 閘**（2026-08-01 親驗：30 種 guard trigger 函式；`honesty_delete_only_guard` 23 表＋`honesty_ledger_guard` 5 表等）＋② **code 層 AST／字面稽核**（`src/augur/audit/import_isolation.py`；射程 7 package＋core，**擋不到動態 SQL**）＋③ **紀律**（CLAUDE.md #6／#12／#14 等）。**殘餘風險明載、不粉飾**：`augur` 為 superuser 且為全表 owner，得 `ALTER TABLE … DISABLE TRIGGER` 卸除任一 guard、且繞過一切 GRANT 檢查——①②③ 均非 L7.16 意義上之權限錨定，僅為**偵測與紀律層之補償控制**。
3. **10-14 併審觸發之更新**：RULING-2026-039 八.2 所設雙觸發之一「雙角色部署議程」因 D13-3 乙（放棄 owner 分離設計）而消滅 ⇒ L7.16 全棧矩陣之觸發**唯餘 2026-10-14 併審**；屆時依 L7.18(b) 處置順序審視（補強選型、或依 §8.2／§8.4 就履行時程為有到期日之處置——**核心義務本身不得豁免**）。**本裁不預斷 10-14 結論**。
4. **禁止假關**：本裁不解讀為 L7.16 已合規、不假關 WM.35／36、025、029 等 2026-10-14 日曆項；WM.35 新證據（code 層稽核）之認定係 GROUNDING-MAP S22 段既有 Steward 拍板，本裁僅引用不重複、亦不擴張其射程。
5. **條件式紅燈恢復（與本裁同 commit）**：新增 `tests/test_l716_conflict_registered.py`——凡 live 仍為單一角色狀態，本裁決檔與 AL-2026-046 即必須在（缺任一即紅）；若日後恢復角色分離，該條件自然失效不再約束。以此恢復「superuser 事實在 repo 內有自動紅燈」（取代已刪之 `test_db_tombstone_controlled_erasure` 之留痕功能，非取代其原斷言——原斷言之前提已消滅）。

## 三、明示不為

* 不改 `specs/INFRASTRUCTURE-SPECIFICATION.md` 任何 [N]／[I] 文字；不升 L7 版本號。
* 不豁免 L7.16；不重開 §8.2；不動 MC／PA。
* 不代 10-14 併審預斷；不假關任何日曆項。
* 不重建 owner 分離（D13-3 乙已拍板放棄；如日後重議屬新案）。
* 不動既有整併留痕文件（史述凍結）。

## 四、驗證

* `ls constitution/*RULING*.md | tail -1` → 本檔；`grep -c "AL-2026-046" constitution/AMENDMENT-LOG.md` ≥ 1。
* `pytest tests/test_l716_conflict_registered.py` → 全 passed（同 commit 內，無常紅窗口）。
* 先驗紅證據：`audits/L716-RULING-042-REDRUN-20260801.md`（RULING 檔未入樹前實跑 FAIL 原文；CLAUDE.md #35「凡新回歸鎖必先驗紅」）。
* `git diff --stat` 範圍限五、施作紀錄所列檔；`specs/` 零 diff。

## 五、施作紀錄（簽核後同 commit）

| 檔案 | 摘要 |
|---|---|
| `constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md` | 本檔 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-046 新列 |
| `tests/test_l716_conflict_registered.py` | 條件式紅燈（新檔；同 commit 故即綠） |
| `audits/L716-RULING-042-REDRUN-20260801.md` | 先驗紅留痕 |

> **簽核欄（Steward）**
> - [ ] **准：L7.16 衝突登錄＋適用性註記（spec 零改；殘餘風險明載）**（簽：＿＿＿＿，日期：＿＿＿＿）

*本裁決於 Steward 簽核時生效。*
