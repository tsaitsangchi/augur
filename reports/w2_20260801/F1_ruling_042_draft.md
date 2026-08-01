# [DRAFT 呈案] F1｜RULING-2026-042 草稿——L7.16 與單一角色部署之正面衝突登錄

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（`AUGUR-L6 v1.2` L6.18(c)）**：本呈案由 AI 起草，而其標的（L7.16 owner 分離之衝突登錄、回歸鎖之恢復）正是對 AI 自身 DB 操作權能之監督機制；故本案一律附機械可判驗收與證偽條件，不以「相信起草者」為據，且 AI 不得為本案之核准主體。
> **產製**：2026-08-01 15:1x，HEAD `e00135c`，全部現況數字為本日唯讀親驗（§2 附指令）。零 DDL、零 code 落地——落地唯待 Steward 簽核後同 commit 施作。
> **設計 SSOT**：`reports/augur_problem_solution_register_20260801.md` §3-F1（含 CR2 糾正「DRAFT 與施作同 commit」）＋`reports/augur_steward_adjudication_sheet_20260801.md` §六-F1。

---

## §1 問題與授權鏈

**問題（r3 §七，2026-08-01）**：2026-07-31「augur＝全部」單一化整併後，`AUGUR-L7 v1.0` **L7.16**（受保護儲存物件之 owner ≠ 應用運行角色；[N]）之物理前提**消滅**——單一角色 `augur`（superuser）擁有全部表、同時是一切服務與 AI 之應用運行角色。整併程序上人類權威成立（四項不可逆變更皆 Steward 親跑、OCV 四項對照留痕），**但 L7 spec 未動、Amendment Log 零登錄、大憲章與 CS 零命中＝治權文件與物理現實正面衝突而零登錄**，漂移入常態（r3 §八 #11「不修會怎樣」）。

**授權鏈**：
- Steward 指示「記錄所有問題的解決方式，之後依記錄逐項展開解決」→ 登錄冊 F1 列 W2 呈案批（草擬=AI／簽=Steward）。
- Steward 指示「碰到標 Steward，請列出最佳解」→ 呈案單 §六-F1 建議案（本檔 §4 承接）。
- critic CR2 糾正：原「先入 repo 必紅測試」**否決**，改為**測試與 RULING 同 commit**（否則落地前對一切測試輪常紅＝狼來了）；CR3 記「F1 已糾正」。
- 裁決權專屬 Constitution Steward（`AUGUR-MC v1.6 §8.1`；`AUGUR-L6 v1.2` L6.18(a)）；本檔僅草擬與證據整備。

---

## §2 現況親驗（2026-08-01 執行；引用前可重跑）

**(1) 號碼空缺確認——042／AL-046 仍空缺** ✅

```
ls constitution/*RULING*.md | tail -1
→ constitution/RULING-2026-041-PRIN7-P4E5-DISPOSITION.md          # 最新裁決＝041
grep -rn "RULING-2026-042" constitution/          → 零命中（僅 AL-2026-042 為 Amendment Log 另一序列之既有號，非裁決號）
grep -n "^## AL-" constitution/AMENDMENT-LOG.md | tail -1
→ ## AL-2026-045                                                   # 最新登錄＝045（2026-07-23）
grep -rn "AL-2026-046" constitution/              → 零命中
```
⇒ **下一裁決號＝2026-042、下一登錄號＝AL-2026-046**，與登錄冊 F1 所載一致。

**(2) pg_roles 現況——單一角色既成事實** ✅

```
psql -tAc "SELECT rolname||'|'||rolsuper||'|'||rolcanlogin FROM pg_roles
           WHERE rolname NOT LIKE 'pg\_%' ORDER BY rolname;"
→ augur|true|true
  postgres|true|true
psql -tAc "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY datname;"
→ augur
  postgres
```
⇒ 非系統角色僅 `augur`（**superuser**）＋`postgres`；`augur_predict`／`augur_owner`／`augur_app`／`ttai`／`rdai`／`stock` 皆不存在。庫僅 `augur`＋`postgres`。

**(3) 殘餘強制機制盤點（衝突登錄之「現行承載」證據）** ✅

```
psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public';"   → 323
  # ⚠ 與 07-31 終態快照 322 差 1（其後新增一表）；與 D13 呈案「306」為不同時點快照，皆屬史述不改
psql -tAc "SELECT tgfoid::regproc::text, count(DISTINCT tgrelid) FROM pg_trigger
           WHERE NOT tgisinternal GROUP BY 1 ORDER BY 2 DESC;"
→ honesty_delete_only_guard|23、honesty_ledger_guard|5、src_whitelist_guard|3、
  direction_product_gate_guard|2、其餘 26 種各 1 表（含 fv_guard／*_no_goalpost／
  governance_proposal_immutable／raw_supersede_log_append_only 等）——共 30 種 guard trigger 函式
```
code 層：`src/augur/audit/import_isolation.py` AST／字面稽核在（射程 7 package＋core；`execution`／`arena`／`identity`／`deliberation` 不在集合、**擋不到動態 SQL**）。

**(4) 唯一機械紅燈已刪之留痕** ✅

`tests/test_raw_supersede_log.py:232-238`（親讀）：`test_db_tombstone_controlled_erasure` 已依 Steward 拍板（丙案）整格刪除、原位留說明段——「抹除函式仍為 SECURITY DEFINER，但已無 DB 層之角色阻擋」。⇒ **superuser 這件事在 repo 內現無任何自動紅燈，只剩文件留痕**（記憶 `augur-single-role-consolidation-20260731` 同載）。

**(5) 決定留痕與 OCV 對照已在（本裁引為依據）** ✅

- `reports/augur_db_role_architecture_submission_20260731.md` §6（Steward 逐項決定 D13-1 乙／D13-2／D13-3 乙）＋§6.2（OCV 四項對照：人類介入點 −1、揭露比例下降、否決可達性不變、自動鏈長不變——「確屬治權變更；已由 Steward 拍板，本節即其留痕」）＋§6.3（隨之消失的保證四項誠實列示）。
- `reports/augur_single_role_consolidation_plan_20260731.md` §0（D-1…D-7）＋§0.5（S9🔒/S10🔒/S11🔒 皆 Steward 親跑；全套驗收 256 passed／14 skipped）。
- `GROUNDING-MAP.md:3`（07-31 全域補註）＋`:176`（WM.35 舊證據永久失效＋S22 新證據＝code 層 AST 稽核，Steward 拍板同日辦理）——**WM.35 部分已有 Steward 認定，本裁不重複、僅引用**。

**(6) L7.16 條文現況** ✅：`specs/INFRASTRUCTURE-SPECIFICATION.md`（AUGUR-L7 v1.0）L7.16 [N] 全文在、未動；其 (e) 逐字：「**強制機制與其可解除者同屬一權限主體時，該不變式在憲章意義上不成立**——存疑即推定不成立（`§8.3`）」。RULING-2026-039 八.2 曾裁 L7.16 全棧矩陣**觸發＝雙角色部署議程或 2026-10-14 併審**。

**與登錄冊不符者**：無（號碼、既成事實、殘餘機制皆與登錄冊／r3 一致）。僅補充兩點時點漂移：public 表數今 **323**（07-31 快照 322）；假斷言掃描今 ERROR **20**（r3 記 33、C3 修 7 誤報後基線化）——皆不影響本案結構。

---

## §3 方案（RULING 全文＋AL 條目全文＋同 commit 測試全文；零 DDL）

### §3.1 新檔 `constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md`（全文）

```markdown
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
* 先驗紅證據：施作時於本裁決檔尚未加入 working tree 前先跑該測試取得 FAIL 輸出，存 `audits/L716-RULING-042-REDRUN-<date>.md`（CLAUDE 回歸鎖紀律「凡新回歸鎖必先驗紅」）。
* `git diff --stat` 範圍限五、施作紀錄所列檔；`specs/` 零 diff。

## 五、施作紀錄（簽核後同 commit）

| 檔案 | 摘要 |
|---|---|
| `constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md` | 本檔 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-046 新列 |
| `tests/test_l716_conflict_registered.py` | 條件式紅燈（新檔；同 commit 故即綠） |
| `audits/L716-RULING-042-REDRUN-<date>.md` | 先驗紅留痕 |

> **簽核欄（Steward）**
> - [ ] **准：L7.16 衝突登錄＋適用性註記（spec 零改；殘餘風險明載）**（簽：＿＿＿＿，日期：＿＿＿＿）

*本裁決於 Steward 簽核時生效。*
```

### §3.2 `constitution/AMENDMENT-LOG.md` 新列（全文；append 於 AL-2026-045 之後）

```markdown
## AL-2026-046

* **日期**：<簽核日>
* **事項**：Steward 裁決第 2026-042 號——**L7.16 與單一角色部署之正面衝突登錄**：(1) 2026-07-31「augur＝全部」單一化整併認定為 Steward 裁決之既成事實（OCV 對照留痕 D13 §6.2）；(2) L7.16 適用性註記——DB 權限層強制依 L7.16(e) 於現行部署**在憲章意義上不成立**，現行承載＝trigger＋AST 稽核＋紀律（補償控制），**殘餘風險明載：superuser 可 DISABLE TRIGGER，不粉飾**；(3) L7.16 全棧矩陣觸發唯餘 **2026-10-14 併審**（039 八.2 之「雙角色部署議程」臂消滅）；(4) 同 commit 恢復條件式機械紅燈 `tests/test_l716_conflict_registered.py`。**spec 零改、L7 版本不升、不豁免、不假關 10-14 各項、MC／PA 零觸**
* **文件**：[RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md](RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md)；呈案 `reports/`（自 scratchpad 移入之本檔）；留痕 `reports/augur_db_role_architecture_submission_20260731.md` §6、`reports/augur_single_role_consolidation_plan_20260731.md`
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：`pytest tests/test_l716_conflict_registered.py` passed（同 commit）；先驗紅留痕 `audits/L716-RULING-042-REDRUN-<date>.md`
* **定案**：Steward <簽核日> 簽核生效
```

### §3.3 新檔 `tests/test_l716_conflict_registered.py`（全文；同 commit）

```python
"""🎯 L7.16 衝突登錄之條件式紅燈：live 仍為單一角色 ⇒ RULING-2026-042 與 AL-2026-046 必須在。

守原則 #15（機制壞了不得安靜變綠燈）、#9（憲法層宣稱可溯源）。
恢復 2026-07-31 刪除 test_db_tombstone_controlled_erasure 後「superuser 零自動紅燈」之缺口：
非斷言角色分離（前提已消滅），而是斷言「既成事實必須保持已登錄」。
若日後恢復角色分離（出現獨立 app 角色），條件不成立、本鎖自然靜默——屬設計而非假綠。
先驗紅：RULING 檔不在 working tree 時本檔必 FAIL（施作留痕 audits/L716-RULING-042-REDRUN-*.md）。
"""
from pathlib import Path

import psycopg2
import pytest

REPO = Path(__file__).resolve().parent.parent
RULING = REPO / "constitution" / "RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md"
AMENDMENT_LOG = REPO / "constitution" / "AMENDMENT-LOG.md"


def is_single_role_state(role_names: set[str]) -> bool:
    """純函式：非系統角色扣除 postgres 後只剩 augur ⇒ 單一角色狀態（L7.16 前提消滅）。"""
    app_like = {r for r in role_names if r != "postgres"}
    return app_like == {"augur"}


def _live_roles() -> set[str]:
    from augur.core.config import DB_PARAMS  # noqa: PLC0415

    with psycopg2.connect(**DB_PARAMS) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT rolname FROM pg_roles WHERE rolname NOT LIKE 'pg\\_%'")
        return {r[0] for r in cur.fetchall()}


def test_single_role_predicate_red_green():
    """純函式餵已知輸入：整併後真形（紅綠雙向）。"""
    assert is_single_role_state({"augur", "postgres"})
    assert not is_single_role_state({"augur", "augur_predict", "postgres"})
    assert not is_single_role_state({"augur", "augur_owner", "postgres"})


def test_l716_conflict_must_stay_registered():
    """live 單一角色 ⇒ 042 裁決檔與 AL-2026-046 皆必須在（缺任一即紅）。"""
    try:
        roles = _live_roles()
    except Exception as exc:  # DB 不可達＝誠實 skip，非假 pass
        pytest.skip(f"DB unreachable: {exc}")
    if not is_single_role_state(roles):
        pytest.skip(f"role separation restored ({sorted(roles)}); L7.16 premise back, lock dormant")
    assert RULING.exists(), (
        "live 為單一角色但 RULING-2026-042 不在——治權登錄被移除或尚未落地，"
        "衝突回到零登錄狀態（r3 §七）")
    text = RULING.read_text(encoding="utf-8")
    assert "L7.16" in text and "AL-2026-046" in text
    assert "## AL-2026-046" in AMENDMENT_LOG.read_text(encoding="utf-8")
```

**回歸鎖三規則自評（誠實）**：(1) 純函式 `is_single_role_state` 餵真形輸入紅綠雙向；(2) 本鎖即「登錄消失」之下游絆線；(3) 檔案存在＋關鍵字斷言屬字面檢查，但**標的本身是文件**（登錄之存在即行為），且與 live pg_roles 條件合取、非孤立字面；先驗紅＝施作時 RULING 檔未入樹前實跑 FAIL 留檔。

### §3.4 施作清單（Steward 簽核後，**單一 commit**；CR2）

| # | 動作 | 檔 |
|---|---|---|
| 1 | 新增裁決檔（§3.1 全文，簽核欄勾選） | `constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md` |
| 2 | append AL-2026-046（§3.2 全文，填日期） | `constitution/AMENDMENT-LOG.md` |
| 3 | 新增條件式紅燈（§3.3 全文） | `tests/test_l716_conflict_registered.py` |
| 4 | 先驗紅留痕（施作時先跑 3、於 1 未入樹前取 FAIL 輸出） | `audits/L716-RULING-042-REDRUN-<date>.md` |
| 5 | 本呈案自 scratchpad 移入 | `reports/`（#16 命名） |

不動：`specs/`（零 diff）、`GROUNDING-MAP.md`（S22 段已載，不重複）、既有整併留痕（史述凍結）、`GOVERNANCE-MAP.md`（其裁決引用為擇要非全列，042 非其現載主題；若 Steward 欲補列屬任意項）。commit 授權依 CLAUDE #14 另行明示。

---

## §4 選項與建議案

| 案 | 內容 | 代價 |
|---|---|---|
| **甲【建議】** | 登錄＋註記（§3 全案）：既成事實認定＋L7.16 適用性註記（spec 零改、殘餘風險明載）＋同 commit 條件式紅燈 | 憲章意義上之不成立被白紙黑字承認（誠實成本，非缺點） |
| 乙 | 修 L7.16 [N] 本文遷就現況 | 動 [N]＝major、為現況弱化義務文字，違 §P5.W5 方向；不建議 |
| 丙 | 不登錄、維持現狀 | 漂移入常態、r3 §八 #11 持續 open；腐爛型 |
| 丁 | 甲但不含測試（純文件） | 「superuser 零自動紅燈」缺口持續；違三規則精神 |

**建議＝甲**（與呈案單 §六-F1 一致）。**證偽條件（呈案單原文）**：若 2026-10-14 復審時 L5／L6 任何條款因此連鎖失效，代表註記範圍畫小了——屆時擴充註記或另裁。

---

## §5 風險與回滾

- **零 DDL、零行為碼、零服務重啟**；唯一 code＝一支新測試（唯讀查 pg_roles＋讀兩檔案；DB 不可達誠實 skip）。
- **簽核前**：本呈案僅 scratchpad／reports 文件，git revert 即淨。
- **簽核後**：AL 為 append-only 帳簿——撤回不刪列，須新裁決 supersede（與既有 AL 慣例一致；「回滾不對稱」r3 §七認知錨）。
- **測試誤紅情境**：未來若有人於本機外新建任何非 postgres 角色（如恢復 `augur_predict`），`is_single_role_state` 轉 false → 測試 skip（非紅）；若 DB 全不可達 → skip 並印原因。**不存在「環境變化導致常紅」路徑**。
- **測試誤綠情境（誠實）**：RULING 檔在而內容被掏空至仍含關鍵字——字面殘餘風險；補償＝AL 帳簿同查＋人讀。

## §6 驗收判準（機械可判）

1. `ls constitution/*RULING*.md | tail -1` 輸出含 `RULING-2026-042`。
2. `grep -c "## AL-2026-046" constitution/AMENDMENT-LOG.md` → `1`，且位於 `## AL-2026-045` 之後。
3. `python3 -m pytest tests/test_l716_conflict_registered.py -q` → `2 passed`（或 1 passed＋1 skipped 於 DB 不可達機）。
4. `audits/L716-RULING-042-REDRUN-*.md` 存在且含 pytest FAIL 原文（先驗紅證據）。
5. `git show --stat HEAD` 該 commit 僅含 §3.4 表列五類檔；`git diff HEAD~1 HEAD -- specs/` 空輸出。
6. 裁決檔簽核欄為勾選狀態＋日期非佔位符。

## §7 Steward 決定欄

（留白——`F1-同意` 或 `F1-改採<其他案>`；簽核日期一併示知以填入 §3.1／§3.2 佔位符。）
