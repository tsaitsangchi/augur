"""selftest — 紅綠自檢（零外部依賴）。

自 `__main__` 分出之理由有二：(1) `report` 需計 selftest 覆蓋數，模組層互 import 會成環；
(2) 覆蓋數之計法（`report.coverage_of`）須與**實際執行之 chk 呼叫**同源，不得再靠對輸出
下 grep——「55 項」之誤即出自 `grep -c '✓'` 把結語橫幅算成一項測試。

`run()` 回 `(ok, records)`，`records` ＝ [(name, passed)]：**項數自此有唯一機器來源**。
"""
from __future__ import annotations

import pathlib
import re
import tempfile

from . import audit_lint, compliance_lint, mc_clauses, report

_HERE = pathlib.Path(__file__).resolve().parent
_FIX = _HERE / "fixtures"
_REPO = _HERE.parents[1]
_MC = str(_REPO / "constitution" / "META-CONSTITUTION.md")


def run(quiet: bool = False):
    """跑全部自檢。回 (ok:bool, records:list[(name, passed)])。"""
    records = []

    def say(*a):
        if not quiet:
            print(*a)

    def chk(name, cond):
        cond = bool(cond)
        records.append((name, cond))
        say(f"  {'✓' if cond else '✗FAIL'} {name}")

    wm = _REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md"
    if wm.exists():
        r = compliance_lint.lint_spec(str(wm), _MC)
        chk("AUGUR-WM v1.0 自檢綠（零 error；含 minor 版落差不誤紅）", r.passed)
        chk("  └ minor 版落差判為 info（非 error）", any(f.rule == "WM.45" and f.severity.value == "info" for f in r.findings))
    else:
        say("  ⚠ 找不到 AUGUR-WM，跳過該項（非 repo 內執行）")

    chk("good_minimal fixture 綠", compliance_lint.lint_spec(str(_FIX / "good_minimal.md"), _MC).passed)

    def red(name, fixture, rule):
        r = compliance_lint.lint_spec(str(_FIX / fixture), _MC)
        chk(name, not r.passed)
        chk(f"  └ error 出自 {rule}", any(f.rule == rule for f in r.errors))

    red("反例① 無聲明 → 紅（WM.39）", "bad_no_statement.md", "WM.39")
    red("反例② 缺欄位 → 紅（WM.40）", "bad_missing_field.md", "WM.40")
    red("反例③ 缺原則節 → 紅（WM.41）", "bad_missing_section.md", "WM.41")
    red("反例④ 附錄遮蔽真缺節 → 紅（WM.41 順序，MUST-FIX A）", "bad_appendix_mask.md", "WM.41")
    red("反例⑤ scalar 空值 → 紅（WM.40，MUST-FIX B）", "bad_empty_value.md", "WM.40")

    # ── 新檢查一：WM.44-LABEL 原文標籤 ──────────────────────────────────────────
    r = compliance_lint.lint_spec(str(_FIX / "bad_label_mislabel.md"), _MC)
    red("反例⑥ Annex TR 憲章誤標 → 紅（WM.44-LABEL）", "bad_label_mislabel.md", "WM.44-LABEL")
    # 五項實證誤標逐一鎖住（回歸鎖：任一漏抓即 FAIL）
    msgs = " ".join(f.message for f in r.errors if f.rule == "WM.44-LABEL")
    for code, why in [
        ("§3", "自有括號名不符（原文＝Five Immutable Principles）"),
        ("P1.E1", "自有括號名不符（原文＝開放來源）"),
        ("P2.E4", "自創詞反充上位標籤（憲章 0 次）"),
        ("P3.E3", "自有括號名不符（原文＝同一性判準掛鉤）"),
        ("F4", "自創詞 Automation First（原文＝Knowledge Without Identity）"),
        ("F5", "自創詞 Answer First（原文＝Intelligence Without Evidence）"),
    ]:
        chk(f"  └ 抓到 `{code}` 誤標：{why}", f"`{code}` 標籤" in msgs)
    chk("  └ 誤標訊息並列「規格所載」與「憲章原文」", "規格所載" in msgs and "原文" in msgs)

    # ── B2 回歸鎖：裸英文名之子字串放行漏洞（截半名／前段截取） ──────────────────
    for code, why in [
        ("P4.E8", "截半：原文＝Confidence（語義與消費），「消費」面遭截除"),
        ("P4.E2", "截半：原文＝Time（雙時間性），代以自創詞「單向時鐘」"),
    ]:
        chk(f"  └ B2 抓到 `{code}` 截半名：{why}", f"`{code}` 標籤僅引原文半名" in msgs)
    # ── B5 回歸鎖：上層規格標籤首度受檢（過半矩陣）──────────────────────────────
    chk("  └ B5 抓到 `WM.36` 誤標（前段截取；原文＝World Concept Registry 與消費規則）",
        "`WM.36` 標籤未完整引用原文名" in msgs)
    chk("  └ B5 錯誤訊息指名權威來源為 AUGUR-WM v1.0（非 MC）",
        any(f.rule == "WM.44-LABEL" and "AUGUR-WM v1.0 原文" in f.message for f in r.errors))

    # 正例：合法標籤不得誤紅（引用原文／正文逐字濃縮／僅列代號無標籤／項次交叉引註）
    rg = compliance_lint.lint_spec(str(_FIX / "good_label_ok.md"), _MC)
    chk("good_label_ok fixture 綠（合法標籤不誤紅）", rg.passed)
    if not rg.passed:
        for f in rg.errors:
            say(f"      ↳ 非預期 error：{f.rule}: {f.message}")
    chk("  └ B5 正例：上層規格（AUGUR-WM v1.0）之標籤確實受檢、非略過",
        any(f.rule == "WM.44-LABEL" and "AUGUR-WM v1.0" in f.message
            and f.severity.value == "info" for f in rg.findings))

    # ── G1 回歸鎖：判準四之無條件大赦（原文名在場者不得以「正文有支撐」放行）──────────
    for code, why in [
        ("P1.E1", "原文＝開放來源；詞元命中正文卻與原文名全然不符"),
        ("P4.E1", "原文＝Knowledge 五元組；「Knowledge」遭捨、代以正文用語"),
    ]:
        chk(f"  └ G1 抓到 `{code}` 判準四大赦漏網：{why}", f"`{code}` 標籤與 MC 原文不符" in msgs)
    chk("  └ G1 指名之漏網標籤即 finding 所載者（Reality 最高抽象／來源非最高抽象）",
        "Reality 最高抽象／來源非最高抽象" in msgs)
    # **純節引不得誤紅**：收緊判準四之對向鎖——`WM.4`（刪名測試）為原文名之逐字子字串、
    # 無自撰片段，good_label_ok 須續綠（該正例列由 rg 之綠斷言涵蓋，此處另證訊息未指名之）
    chk("  └ G1 對向：純節引 `WM.4`（刪名測試）不得被判大赦漏網",
        "`WM.4` 標籤與" not in msgs)

    # ── G2 回歸鎖：重複詞灌分（label_overlap 詞元須去重）────────────────────────────
    #    實測之真實利用手法：以**命中詞**填充（非如原 finding 所述之整體重複——整體重複
    #    分子分母同步放大，比值不變、無從灌分）。`禁插補冒充` ＋ `Representation` ×4 →
    #    去重前 4/8 ＝ 50% 恰跨閾值而放行；去重後恆為 1/5 ＝ 20%。
    p2e4 = mc_clauses.load_clause_labels(_MC)["P2.E4"]
    chk("G2 突變鎖：`P2.E4` 以命中詞灌分，任何倍數均不得放行（詞元去重）",
        all(not compliance_lint._text_supported("禁插補冒充" + " Representation" * n, p2e4)[0]
            for n in range(1, 12)))
    chk("  └ G2 灌分比值恆定（去重後不隨重複次數上升）",
        len({mc_clauses.label_overlap("禁插補冒充" + " Representation" * n, p2e4["text"])
             for n in range(1, 12)}) == 1)
    chk("  └ G2 該灌分列於 fixture 中實際報紅",
        "禁插補冒充 Representation Representation" in msgs)

    # ── G3 回歸鎖：代號脫檢不得靜默（弄壞代號不得比修好標籤容易）────────────────────
    chk("G3 突變鎖：代號形態合致但不在 [N] 宇宙（`P5.E9`）→ error、非靜默略過",
        any(f.rule == "WM.44-LABEL" and "`P5.E9`" in f.message and "不在憲章 [N] 條款宇宙" in f.message
            for f in r.errors))
    chk("  └ G3 前綴已知但未列於 upper-specs（`KS.1`）→ warning（非 error、非靜默）",
        any(f.rule == "WM.44-LABEL" and "`KS.1`" in f.message for f in r.warnings))

    # ── B3 回歸鎖：條款宇宙不完整（§2 定義項為 numbered list item，前版從未進入宇宙）──
    mc_text = pathlib.Path(_MC).read_text(encoding="utf-8")
    universe = mc_clauses.enumerate_clauses(mc_text)
    for c in ["§2.5", "§2.6", "§2.7", "§2.10", "§2.11", "§2.1"]:
        chk(f"  └ B3 `{c}` 已進入條款宇宙（§2 定義項）", c in universe)
    chk("  └ B3 §2 十一條定義全數在宇宙（§2.1–§2.11）",
        all(f"§2.{n}" in universe for n in range(1, 12)))
    chk("  └ B3 §5 六個架構角色項次全數在宇宙（§5.1–§5.6，同體例）",
        all(f"§5.{n}" in universe for n in range(1, 7)))
    chk("  └ B3 Appendix C/D/E 之編號清單未誤入宇宙（[I] 章、非 [N] 項次）",
        "§9.1" not in universe and not any(c.startswith("§10") for c in universe))
    labels_mc = mc_clauses.load_clause_labels(_MC)
    chk("  └ B3 §2 定義項可供標籤檢查（§2.5 原文名＝Evidence）",
        (labels_mc.get("§2.5") or {}).get("paren_name") == "Evidence")

    # ── 新檢查二：WM.40 閉集擴欄 ───────────────────────────────────────────────
    fields_now, src_now = compliance_lint._wm40_closed_set()
    chk("WM.40 閉集由 WM 規格原文動態解析（非硬編碼）", src_now == "WM 原文")
    # **不**斷言 `len(...)==14`（B8）：14 這個數字正是本設計明文拒絕硬編碼之對象。WM 合法增欄時
    # 該斷言即偽紅，而修復壓力會指向「把 14 改成 15」——即把 linter 拉回硬編碼。改採結構性斷言。
    chk("  └ 解析結果具閉集之結構性質（≥10 欄且含 spec／archive-path）",
        len(fields_now) >= 10 and "spec" in fields_now and "archive-path" in fields_now)

    # ── B8 真突變鎖：以**修訂後之 WM 副本**實證 linter 跟隨 WM 而非硬編碼 ──────────
    #    前版 README:68 宣稱有此測試，實則 selftest 全程未觸及任何 WM 副本——gate 自身犯了
    #    它要撲滅的病（宣稱與實作脫節）。此處補上真測試。
    with tempfile.TemporaryDirectory() as td:
        wm_src = (_REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md")
        if wm_src.exists():
            body = wm_src.read_text(encoding="utf-8")

            # 突變一：於 WM.40 圍籬閉集插入新欄 → linter 須回報 15 欄且含 new-field-x
            mutated = body.replace("  archive-path: {規格存檔",
                                   "  new-field-x: {突變測試欄}\n  archive-path: {規格存檔", 1)
            if mutated == body:      # 錨點文字漂移時退回以行號無關之插入點
                mutated = body.replace("  archive-path:", "  new-field-x: {突變測試欄}\n  archive-path:", 1)
            p1 = pathlib.Path(td) / "wm_added_field.md"
            p1.write_text(mutated, encoding="utf-8")
            f1, s1 = compliance_lint._wm40_closed_set(str(p1))
            chk("B8 突變鎖①：WM 副本增一欄 → 閉集隨之增為 15 欄（linter 跟隨 WM，非硬編碼）",
                s1 == "WM 原文" and "new-field-x" in f1 and len(f1) == len(fields_now) + 1)
            chk("  └ 增欄後 source 仍為「WM 原文」（未退回 fallback）", s1 == "WM 原文")

            # 突變二（B9）：WM.40 錨點格式微漂移 `**WM.40（` → `**WM.40 ：` → 須退 fallback
            drifted = body.replace("**WM.40（機器可稽核 front-matter）", "**WM.40 ：機器可稽核 front-matter", 1)
            p2 = pathlib.Path(td) / "wm_anchor_drift.md"
            p2.write_text(drifted, encoding="utf-8")
            f2, s2 = compliance_lint._wm40_closed_set(str(p2))
            chk("B9 突變鎖①：WM.40 錨點漂移 → 閉集解析失敗、退回硬編碼副本", s2 == "fallback")
            # **關鍵**：退回本身不是問題，「退得無聲而規格照報 PASS」才是。
            r9 = compliance_lint.lint_spec(str(_FIX / "good_minimal.md"), _MC, wm_path=str(p2))
            chk("B9 突變鎖②：閉集失準時 good_minimal 不再 PASS（不得靜默降級）", not r9.passed)
            chk("  └ error 出自 WM.40 且指名『退回工具內硬編碼副本』",
                any(f.rule == "WM.40" and "硬編碼副本" in f.message for f in r9.errors))
            chk("  └ error 載明判定不具權威（非 warning 級提示）",
                any(f.rule == "WM.40" and "不具權威" in f.message for f in r9.errors))
            # 對照組：WM 可讀且錨點完好時，good_minimal 仍 PASS（B9 修正不得誤紅正常路徑）
            chk("  └ 對照：WM 原文可解析時 good_minimal 仍 PASS（B9 不誤紅正常路徑）",
                compliance_lint.lint_spec(str(_FIX / "good_minimal.md"), _MC).passed)

            # B9 突變鎖③：WM 完全不可讀 → 同樣須 error，不得靜默用副本
            f3, s3 = compliance_lint._wm40_closed_set(str(pathlib.Path(td) / "no_such_wm.md"))
            chk("B9 突變鎖③：WM 不可讀 → fallback（且 lint 須報 error）",
                s3 == "fallback" and not compliance_lint.lint_spec(
                    str(_FIX / "good_minimal.md"), _MC,
                    wm_path=str(pathlib.Path(td) / "no_such_wm.md")).passed)
        else:
            say("  ⚠ 找不到 AUGUR-WM，跳過 B8/B9 突變鎖")

    # ── G4 突變鎖（BLOCKER）：Annex TR 區段缺位不得靜默 ──────────────────────────────
    #    前版 `if not regions: return`：`_ANNEX_TR_HEAD` 硬性要求 `##`，故標題層級一改即
    #    全部標籤檢查蒸發，且**零 finding、照報 PASS**——「無 Annex TR」與「Annex TR 全數
    #    通過」在輸出上不可分辨。此非假想：`specs/ONTOLOGY-SPECIFICATION.md` 之 Annex TR
    #    標題為 h1，其 WM.44-LABEL 從未執行，而其 PASS 曾用以支撐 RULING-2026-003。
    with tempfile.TemporaryDirectory() as td:
        src = (_FIX / "bad_label_mislabel.md").read_text(encoding="utf-8")
        n_err_ok = len(compliance_lint.lint_spec(str(_FIX / "bad_label_mislabel.md"), _MC).errors)

        for tag, mut, desc in [
            ("h3", src.replace("## Annex TR", "### Annex TR", 1), "`## Annex TR` → `### Annex TR`"),
            ("h1", src.replace("## Annex TR", "# Annex TR", 1), "`## Annex TR` → `# Annex TR`（ONT 實例之形態）"),
        ]:
            p = pathlib.Path(td) / f"tr_{tag}.md"
            p.write_text(mut, encoding="utf-8")
            rm = compliance_lint.lint_spec(str(p), _MC)
            chk(f"G4 突變鎖：{desc} → 仍不得 PASS（標籤檢查蒸發不得靜默）", not rm.passed)
            chk("  └ error 指名『未偵得可解析之 Annex TR 區段』且『未執行』",
                any(f.rule == "WM.44-LABEL" and "未偵得可解析之 Annex TR 區段" in f.message
                    and "未執行" in f.message for f in rm.errors))
            chk("  └ error 明言非「已比對且通過」（不得與全數通過同形）",
                any(f.rule == "WM.44-LABEL" and "非「已比對且通過」" in f.message for f in rm.errors))
        chk("  └ 對照：標題完好時該 fixture 之 LABEL error 確實存在（突變前後非恆紅）",
            n_err_ok > 0)

        # 對向鎖：確無 Annex TR 且未斷言者 → info（不得誤紅）。good_minimal 宣告 upper-specs
        # 綁定卻無 Annex TR——嚴重度**不得**繫於 upper-specs 之有無（否則此正例即誤紅）。
        rmin = compliance_lint.lint_spec(str(_FIX / "good_minimal.md"), _MC)
        chk("G4 對向鎖：無 Annex TR 且未斷言之規格 → 仍 PASS（不誤紅）", rmin.passed)
        chk("  └ 惟仍留 info 痕跡（「未執行」不得被讀作「已比對且通過」）",
            any(f.rule == "WM.44-LABEL" and f.severity.value == "info"
                and "不適用" in f.message for f in rmin.findings))

        # 斷言型 ERROR：無可解析區段、卻斷言形式充分性繫於 Annex TR 逐條枚舉（ONT §CS.10 型態）
        asserted = src.replace("## Annex TR [N] — WM.44 逐條對應矩陣",
                               "## 附錄（非 TR）\n\n本規格之形式充分性依 Annex TR 之逐條枚舉已成就。", 1)
        p = pathlib.Path(td) / "tr_asserted.md"
        p.write_text(asserted, encoding="utf-8")
        ra = compliance_lint.lint_spec(str(p), _MC)
        chk("G4 突變鎖：無區段卻斷言「形式充分性依 Annex TR 逐條枚舉已成就」→ error", not ra.passed)
        chk("  └ error 指名該斷言無從查證",
            any(f.rule == "WM.44-LABEL" and "斷言" in f.message and "無從查證" in f.message
                for f in ra.errors))

        # ── G5 突變鎖：upper-specs 無法解析 → error（B9 教義：判準來源崩解不得僅 warning）──
        broken = src.replace("upper-specs: [AUGUR-WM v1.0]", "upper-specs: [AUGUR-WM v9.9]", 1)
        p = pathlib.Path(td) / "upper_broken.md"
        p.write_text(broken, encoding="utf-8")
        rb = compliance_lint.lint_spec(str(p), _MC)
        chk("G5 突變鎖：upper-specs 版本改為不存在之 v9.9 → error（非 warning）",
            any(f.rule == "WM.44-LABEL" and "AUGUR-WM v9.9" in f.message
                and f.severity is compliance_lint.Severity.ERROR for f in rb.errors))
        chk("  └ error 載明該來源側判定不具權威（B9 教義一致）",
            any(f.rule == "WM.44-LABEL" and "不具權威" in f.message for f in rb.errors))
        chk("  └ 未降級為 warning（判準來源崩解不得 CI 綠燈）",
            not any(f.rule == "WM.44-LABEL" and "AUGUR-WM v9.9" in f.message
                    for f in rb.warnings))

    # ── G6 突變鎖（BLOCKER，2026-07-17 三輪補）：**零覆蓋之其餘變體**不得 PASS ────────────
    #    65a7dd6 之 G4 只鎖住「標題層級不對」一種零覆蓋變體。實證（分流官親跑、本席複驗）：
    #    保留 `## Annex TR` 標題、**僅刪其下全部 `|` 表列** → IDENTITY 由 ❌ FAIL(31) 轉
    #    ✅ **PASS(0)**、零 finding，輸出與突變前逐字相同——「刪表列」遂為現存最廉價之翻綠
    #    路徑（刪表列比修 31 個標籤省事）。以下三鎖以**真規格副本**（非 fixture）鎖住之：
    #    表列既為形式充分性之枚舉依據，抽不出可比對之標籤時該依據即未受檢，不得 PASS。
    _id = _REPO / "specs" / "IDENTITY-SPECIFICATION.md"
    if _id.exists():
        with tempfile.TemporaryDirectory() as td:
            body = _id.read_text(encoding="utf-8")
            base_r = compliance_lint.lint_spec(str(_id), _MC)
            # 2026-07-18 #22 執行後（RULING-2026-010）IDENTITY 已修至 error 0——對照鎖由
            # 「未突變即紅」改為**雙向差分**：未突變 PASS（綠基線）、突變必 FAIL（紅），
            # 差分更強；紅對照另由 fixtures/bad_label_mislabel.md 恆備（前段既有斷言）。
            chk("G6 對照：未突變之 IDENTITY 為 PASS（#22 修畢之綠基線；突變後必紅＝雙向差分）",
                base_r.passed
                and sum(1 for f in base_r.errors if f.rule == "WM.44-LABEL") == 0)

            def _tr_rows(text):
                """回 (區段內表列之索引, 全部行)。"""
                lines, idx, in_tr = text.splitlines(), [], False
                for i, ln in enumerate(lines):
                    if compliance_lint._ANNEX_TR_HEAD.match(ln):
                        in_tr = True
                        continue
                    if in_tr and compliance_lint._H2.match(ln):
                        in_tr = False
                    if in_tr and ln.lstrip().startswith("|") \
                            and not re.match(r"^\s*\|[\s|:-]+$", ln):
                        idx.append(i)
                return idx, lines

            def _cells(ln):
                c = [x.strip().strip("`*") for x in ln.strip().strip("|").split("|")]
                return (c + ["", ""])[:2]

            def _mutate(kind):
                idx, lines = _tr_rows(body)
                assert idx, "IDENTITY 之 Annex TR 表列未偵得——突變前提已變，本鎖須重寫"
                drop = set(idx)
                out = []
                for i, ln in enumerate(lines):
                    if i not in drop:
                        out.append(ln)
                        continue
                    code, label = _cells(ln)
                    if kind == "rows_deleted":
                        continue                                   # ① 整列刪除
                    if kind == "list_style":
                        out.append(f"- **{code}**（{label}）")      # ② 改清單體例
                    else:
                        out.append(f"<tr><td>{code}</td><td>{label}</td></tr>")   # ③ 改 HTML
                return "\n".join(out)

            for kind, desc in [
                ("rows_deleted", "① 保留 `## Annex TR` 標題、刪光其下全部 `|` 表列"),
                ("list_style", "② 表列改清單體例（`- **P1.E1**（…）`）"),
                ("html_rows", "③ 表列改 HTML（`<tr><td>…</td></tr>`）"),
            ]:
                p = pathlib.Path(td) / f"id_{kind}.md"
                p.write_text(_mutate(kind), encoding="utf-8")
                rz = compliance_lint.lint_spec(str(p), _MC)
                chk(f"G6 突變鎖：{desc} → 仍不得 PASS（零覆蓋不得與全數通過同形）", not rz.passed)
                chk("  └ error 指名「零覆蓋」且「不具權威」（非靜默、非 warning）",
                    any(f.rule == "WM.44-LABEL" and "零覆蓋" in f.message
                        and "不具權威" in f.message
                        and f.severity is compliance_lint.Severity.ERROR for f in rz.errors))
                chk("  └ error 據實載明所量到者（區段在場、抽得 0 筆）",
                    any(f.rule == "WM.44-LABEL" and "0 筆" in f.message
                        and "Annex TR 區段" in f.message for f in rz.errors))

            # ── G7：二錨判準正交之縫（本輪新造，三輪修正）────────────────────────────
            #    `_ANNEX_TR_HEAD`（容前綴、強制 h2）與 `_ANNEX_TR_HEAD_ANY`（容任意層級、
            #    強制 `Annex TR` 起首）判準正交 → 交集外之標題**雙盲**、落入最寬鬆之 INFO
            #    分支，令工具輸出「本規格無 Annex TR 標題」此一可由 grep 立即證偽之斷言。
            head_re = re.compile(r"^##\s+.*Annex\s+TR.*$", re.M)
            mutated = head_re.sub("### 附錄 TR：Annex TR 追溯矩陣", body, count=1)
            p = pathlib.Path(td) / "id_prefixed_h3.md"
            p.write_text(mutated, encoding="utf-8")
            rp = compliance_lint.lint_spec(str(p), _MC)
            chk("G7 突變鎖：`### 附錄 TR：Annex TR 追溯矩陣`（前綴＋非 h2）→ 不得 PASS（前為雙盲）",
                not rp.passed)
            chk("  └ 不得輸出「本規格無 Annex TR 標題」之假斷言",
                not any("無 Annex TR 標題" in f.message for f in rp.findings))
            chk("  └ 二錨判準同一（僅層級不同）：任一行凡 h2 錨命中，任意層級錨必命中",
                all(bool(compliance_lint._ANNEX_TR_HEAD_ANY.match(s))
                    for s in ["## Annex TR [N] — 矩陣", "## 附錄：Annex TR 追溯矩陣"]
                    if compliance_lint._ANNEX_TR_HEAD.match(s)))
            chk("  └ 敘述性標題（`## 本規格未設 Annex TR`）二錨皆不認其為區段錨",
                not compliance_lint._ANNEX_TR_HEAD.match("## 本規格未設 Annex TR")
                and not compliance_lint._ANNEX_TR_HEAD_ANY.match("## 本規格未設 Annex TR"))
            chk("  └ 對向：文件標題行順帶提及 Annex TR 者不得被認作附錄本體",
                compliance_lint._find_annex_tr_head(
                    "# Fixture：Annex TR 憲章誤標\n\n本檔為反例。\n") is None)
            chk("  └ 對向：真附錄為 h1 者仍須認出（ONT 體例，非以層級排除）",
                compliance_lint._find_annex_tr_head(
                    "# 《規格》\n\n## §0\n\n# Annex TR [I] — 矩陣\n") is not None)
            # INFO 分支之措辭須為**可查證之計數**，非事實斷言
            r_wm = compliance_lint.lint_spec(str(_REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md"), _MC) \
                if (_REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md").exists() else None
            if r_wm is not None:
                chk("G7 對向鎖：真無 Annex TR 之規格（WM）仍 PASS，且 INFO 措辭為可查證計數",
                    r_wm.passed and any(
                        f.rule == "WM.44-LABEL" and f.severity.value == "info"
                        and "字串出現" in f.message and "無 Annex TR 標題" not in f.message
                        for f in r_wm.findings))

    # ── G8 突變鎖（2026-07-17 三輪補）：抽取階段之靜默捨棄 ────────────────────────────
    #    前版：形態不合 `ANY_CODE_ALT` 之代號、以及**任何字元層面之污損**（全形字母／全形
    #    句點），於 `_row_code_labels` 即遭捨棄 → 零 finding。亦即「把首格代號打成全形」比
    #    「修好標籤」省事得多——與 `_report_unresolved_code` 所攔之誘因倒置同型，且更便宜。
    C = compliance_lint
    chk("G8：越界前綴（`P9.E9`）不再於抽取階段蒸發（交由 unresolved 分支發聲）",
        C._row_code_labels("**P9.E9**（禁插補冒充）") == [(["P9.E9"], "禁插補冒充")])
    chk("  └ G8：全形字母（`Ｐ1.E1`）經 NFKC 歸位為真代號、照常受檢",
        C._row_code_labels("**Ｐ1.E1**（亂編）") == [(["P1.E1"], "亂編")])
    chk("  └ G8：全形句點（`P1．E1`）經 NFKC 歸位為真代號、照常受檢",
        C._row_code_labels("**P1．E1**（亂編）") == [(["P1.E1"], "亂編")])
    chk("  └ G8 對向：空白標籤（`**P1.E1**（）`）仍不罰（無標籤可比；README 已列為第三種不罰）",
        C._row_code_labels("**P1.E1**（）") == [])
    chk("  └ G8 對向：純代號列（無標籤）仍不罰",
        C._row_code_labels("§0.1、§0.2 純列舉") == [])
    # **標籤須逐字引錄**：NFKC 僅得用於代號比對。若以正規化後之字串充作「規格所載」，
    # 本工具即在轉述規格原文——一份專攻「以轉述冒充原文」之工具自己 misquote。
    chk("  └ G8：標籤逐字引錄（代號經 NFKC 歸位，標籤內之全形標點原樣保留、不得被正規化）",
        C._row_code_labels("**Ｐ1.E1**（Reality 最高抽象／來源非最高抽象）")
        == [(["P1.E1"], "Reality 最高抽象／來源非最高抽象")])
    # **B5 回歸鎖**：區段列之標籤描述整個區段，不得以尾碼單條受檢。本輪初版之兜底錨遺漏
    # 「已由主錨涵蓋之範圍不再解讀」，致 L6 由 37→39（`ID.53`／`ONT.62` 二筆偽陽性）。
    chk("  └ G8／B5 回歸鎖：區段列（`ONT.1–ONT.62（…）`）不得由兜底錨拆成尾碼單條受檢",
        C._row_code_labels("`AUGUR-ONT v1.0` ONT.1–ONT.62（型別層本體/Type 判準/schema）") == [])
    with tempfile.TemporaryDirectory() as td:
        src8 = (_FIX / "bad_label_mislabel.md").read_text(encoding="utf-8")
        mut8 = src8.replace("**P2.E4**", "**Ｐ2.E4**", 1)
        if mut8 != src8:
            p8 = pathlib.Path(td) / "fullwidth.md"
            p8.write_text(mut8, encoding="utf-8")
            r8 = compliance_lint.lint_spec(str(p8), _MC)
            chk("  └ G8 端到端：誤標之代號打成全形後**仍**報 error（不得藉污損代號翻綠）",
                any(f.rule == "WM.44-LABEL" and "`P2.E4`" in f.message for f in r8.errors))

    # ── G9 突變鎖（2026-07-17 三輪補）：把判準來源抽走不得比修好標籤容易 ─────────────
    #    前版 `_upper_spec_labels` 於 `not tokens` 時逕回空且**零 finding**。實測突變（四份
    #    生效規格之 `upper-specs` 一律改 `[]`）：ID 31→29／KS 34→32／L5 49→27／L6 37→21，
    #    **合計 151→109（42 筆 ERROR 靜默降級為 WARNING）**，且無任何 finding 以「未宣告
    #    upper-specs」本身為標的。對照：把版本改成不存在之 v9.9 → ERROR（G5）。即
    #    「宣告了但解不到」＝ERROR，「**乾脆不宣告**」＝靜默——誘因倒置。
    if _id.exists():
        with tempfile.TemporaryDirectory() as td:
            body = _id.read_text(encoding="utf-8")
            n_before = sum(1 for f in compliance_lint.lint_spec(str(_id), _MC).errors
                           if f.rule == "WM.44-LABEL")
            emptied = re.sub(r"^(\s*upper-specs:\s*)\[.*\]$", r"\1[]", body, flags=re.M)
            chk("G9 前提：IDENTITY 副本之 upper-specs 確已清空（突變確實生效）", emptied != body)
            p9 = pathlib.Path(td) / "id_upper_empty.md"
            p9.write_text(emptied, encoding="utf-8")
            r9u = compliance_lint.lint_spec(str(p9), _MC)
            n_after = sum(1 for f in r9u.errors if f.rule == "WM.44-LABEL")
            chk(f"G9 突變鎖：`upper-specs: []` 之 IDENTITY 副本，LABEL error 不得低於原檔"
                f"（{n_before} → {n_after}）", n_after >= n_before)
            chk("  └ G9：未宣告 upper-specs 本身即留痕（warning，非靜默）",
                any(f.rule == "WM.44-LABEL" and "未列 `upper-specs`" in f.message
                    for f in r9u.warnings))
            chk("  └ G9：正文自承受拘束而 front-matter 未列 → ERROR（B9：來源被自己抽走）",
                any(f.rule == "WM.44-LABEL" and "自承" in f.message
                    and f.severity is compliance_lint.Severity.ERROR for f in r9u.errors))
            chk("  └ G9：並列式宣告之各上層規格全數認出（不得只認緊接「受」之第一個）",
                {f.message.split("`")[1] for f in r9u.errors
                 if "自承" in f.message} >= {"AUGUR-WM", "AUGUR-ONT"})
            chk("  └ G9 對向：現行五份生效規格於本檢查零命中（正文宣告與 upper-specs 一致）",
                not any("自承" in f.message
                        for spec in ("IDENTITY", "KNOWLEDGE-SYSTEM", "COGNITIVE-KERNEL",
                                     "AGENT-RUNTIME", "ONTOLOGY")
                        if (_REPO / "specs" / f"{spec}-SPECIFICATION.md").exists()
                        for f in compliance_lint.lint_spec(
                            str(_REPO / "specs" / f"{spec}-SPECIFICATION.md"), _MC).findings))

    # ── G10 突變鎖（2026-07-17 三輪補）：【地位】節之生效宣稱 vs `spec-version` ──────────
    #    `608adc2` 以人手替五份文件補正 §0.1／【地位】矛盾（36 行純替換），**未加任何鎖**。
    #    故同一類矛盾今日仍可零成本重新引入：一份 `spec-version: v0.1-draft` 之文件於檔首
    #    宣稱「本文件為 v1.0 生效版本、§0.1 生效要件全部成就」，前版 gate 不發一語。
    _l7 = _REPO / "specs" / "INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md"
    if _l7.exists():
        with tempfile.TemporaryDirectory() as td:
            body7 = _l7.read_text(encoding="utf-8")
            chk("G10 對照：未突變之 L7 draft 不因本檢查報 status error（現行五份生效規格亦同）",
                not any(f.kind.startswith("status_")
                        for f in compliance_lint.lint_spec(str(_l7), _MC).findings))
            forged = re.sub(r"本文件為\s*\*\*AUGUR-L7 v0\.1-draft 提案\*\*。",
                            "本文件為 **v1.0 生效版本**。`§0.1` 生效要件全部成就，"
                            "**自 2026-07-17 起生效**。", body7, count=1)
            chk("G10 前提：突變確實生效（draft 檔首插入生效宣稱、front-matter 不動）",
                forged != body7)
            p10 = pathlib.Path(td) / "l7_forged_status.md"
            p10.write_text(forged, encoding="utf-8")
            r10 = compliance_lint.lint_spec(str(p10), _MC)
            chk("G10 突變鎖：`spec-version: v0.1-draft` 而【地位】節自稱生效 → error（自我充任之僭稱）",
                any(f.kind == "status_draft_claims_effective"
                    and f.severity is compliance_lint.Severity.ERROR for f in r10.errors))
            chk("  └ G10：訊息指名充任認定屬 Steward、文件不得自我充任",
                any(f.kind == "status_draft_claims_effective" and "不得自我充任" in f.message
                    for f in r10.errors))
        # 對向：生效本之【地位】節改稱「不生效力」→ 亦須紅（二向皆鎖）
        if _id.exists():
            with tempfile.TemporaryDirectory() as td:
                bodyi = _id.read_text(encoding="utf-8")
                downgraded = re.sub(r"本文件為 \*\*v1\.0 生效版本\*\*。.*?\*\*自 2026-07-17 起生效\*\*。",
                                    "本文件為 **v1.0-draft 草案**。本稿不生效力。",
                                    bodyi, count=1, flags=re.S)
                if downgraded != bodyi:
                    p10b = pathlib.Path(td) / "id_status_draft.md"
                    p10b.write_text(downgraded, encoding="utf-8")
                    r10b = compliance_lint.lint_spec(str(p10b), _MC)
                    chk("G10 對向鎖：`spec-version: v1.0` 而【地位】節稱草案／不生效力 → error",
                        any(f.kind == "status_effective_claims_draft" for f in r10b.errors))
        # 界線鎖：本檢查僅及【地位】節。`L5:405`／`L6:417` 之 `### TR.Z …（DRAFT）[N]` 為
        # 待 Steward 裁決之真缺陷（AL-2026-012 附錄丙第 4 項），**不得**由本工具代為認定。
        l5 = _REPO / "specs" / "COGNITIVE-KERNEL-SPECIFICATION.md"
        if l5.exists():
            chk("  └ G10 界線：`### TR.Z …（DRAFT）` 之殘留不由本檢查代 Steward 認定（僅及【地位】節）",
                "DRAFT" in l5.read_text(encoding="utf-8")
                and not any(f.kind.startswith("status_")
                            for f in compliance_lint.lint_spec(str(l5), _MC).findings))

    # ── G11 突變鎖（2026-07-17 三輪補）：斷言判準之同義改寫不得逃逸 ─────────────────
    #    前版 `_TR_ASSERT_TOKENS` 為五個中文字串之閉集，同義改寫即整條防線失效——與 G7
    #    （二錨雙盲）併用即可端到端翻綠：把 Annex TR 標題加個前綴（雙盲）＋把斷言改寫成
    #    「逐一完整列舉」（逃逸），前版 → INFO「不適用」＋ PASS。
    A = compliance_lint._asserts_tr_enumeration
    for phrase in ["本規格之形式充分性依 Annex TR 之逐條枚舉已成就。",     # 原五詞之一
                   "本規格之 Annex TR 已逐一完整列舉全部條款。",           # 同義改寫①
                   "Annex TR 為本規格之對照總表，形式要件充足。",          # 同義改寫②
                   "Annex TR 已逐條映射全部條款、缺 0 條。",               # 同義改寫③
                   "Annex TR is the traceability matrix for this spec.",   # 英文
                   "This spec's Annex TR provides clause-by-clause coverage."]:
        chk(f"  └ G11：斷言判準涵蓋「{phrase[:18]}…」（同義改寫不得逃逸）", A(phrase))
    chk("G11 對向鎖：同段無斷言詞族者不得誤判為斷言（跨段偶合不採認）",
        not A("本規格無 Annex TR。\n\n另段落提及逐條枚舉，與上段無涉。"))
    chk("  └ G11：視窗以**段落**為界（非字元數）——同段之長距離斷言仍須認出",
        A("Annex TR 之說明：" + "本節敘述本規格之附錄結構與其編纂體例。" * 8
          + "綜上，本規格之形式充分性依該附錄之逐條枚舉已成就。"))

    re_ = compliance_lint.lint_spec(str(_FIX / "bad_wm40_extension.md"), _MC)
    red("反例⑦ front-matter 擴欄 → 紅（WM.40 閉集）", "bad_wm40_extension.md", "WM.40")
    chk("  └ error 指名擴欄 `defers-in-count`",
        any("defers-in-count" in f.message for f in re_.errors))
    chk("  └ error 指名擴欄 `reviewer`", any("`reviewer`" in f.message for f in re_.errors))

    # audit_lint 框架 smoke + MUST-FIX C 回歸鎖（型別括號之合規表不誤紅）
    chk("audit_lint 對不存在路徑回 error（不炸）", not audit_lint.lint_code(str(_FIX / "no_such_dir"), "legacy").passed)
    ar = audit_lint.lint_code(str(_FIX / "audit_sample"), "greenfield")
    chk("audit_lint 不對型別括號之合規行動表誤報 AUD-10（MUST-FIX C）",
        not any(f.rule == "AUD-10" for f in ar.findings))


    # ── [I] 文件權威數字綁定（本輪根治手段：把手拿掉）───────────────────────────────
    _binding_and_consistency(chk, records)

    ok = all(p for _, p in records)
    say("自檢：" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return ok, records


def _binding_and_consistency(chk, records):
    """綁定斷言：[I] 文件中標記為「權威數字」之處，須與 `report` 輸出**逐字一致**；不一致即 FAIL。

    **為何這是根治而非又一層修補**：前四輪之腐爛皆非因人不用心，而是因為數字由人手抄。
    本檢查使「文件數字與程式分家」成為 **CI 紅燈**——手抄一經漂移即擋下，而非等下一位
    審查官去數。無法自動綁定之數字，文件應書「見 `report` 輸出」，不得寫死。

    **自我一致性**：`report` 之逐檔數字須與 `compliance` 逐檔輸出相等（同一 `lint_spec`
    呼叫，此處逐檔複驗，杜絕 report 自行實作一套判準而與 CLI 分家）。

    **自我指涉之處理（本檢查最微妙處）**：`report` 之 `selftest_*` 取自實測 `records`，而本
    檢查執行時 records 尚不完整——本檢查自身之斷言尚未發出。故先把待發之斷言**構造成清單**
    （`pending`），由 `len(pending)` 得其確切筆數，再據以算出完整跑完後之覆蓋數，最後才逐一
    發出。**計數自此為結構性導出，非人工維護之常數**——在此寫死「本檢查發 N 項」正是本輪
    要消滅之病灶（且必隨日後增刪斷言而失準）。

    交叉檢查：`--sync` 寫入之值取自**實跑一輪**之 records（`report.build(selftest=None)`），
    而本處為**構造性預測**。二者若不等，doc 值必與預測不符 → 本檢查 FAIL。**預測錯誤無法
    靠 `--sync` 掩蓋**。
    """
    markers = report.collect_markers(_REPO)

    # ── 一、把待發之斷言構造成清單（"top"／"sub" ＋ 產生 (name, cond) 之閉包）──────────
    #    此時尚不知 `data`，故條件一律為接收 data 之閉包，於第三步才求值。
    pending = []

    def _add(kind, fn):
        pending.append((kind, fn))

    # 自我一致性：report 逐檔 error 數 ≡ compliance 對同一檔之 lint_spec 輸出
    _add("top", lambda d: (
        f"report 逐檔數字與 compliance 逐檔輸出一致（{len(d['per_file'])} 份逐一複驗）",
        not _consistency_detail(d)))
    _add("sub", lambda d: (
        "  └ 不一致清單為空（逐檔複驗 report vs compliance 之 error／warning 數）"
        + ("：" + "；".join(_consistency_detail(d)) if _consistency_detail(d) else ""),
        not _consistency_detail(d)))

    # corpus 定義之結構性斷言（**非**斷言「＝7」：份數是 corpus 定義之後果，非其定義。
    # L7 生效之日份數自然變動，屆時修復壓力不得指向「把 7 改成 6」）
    _add("top", lambda d: (
        "corpus 定義寫在程式：歸檔本（生效本在場之 -v0.1-draft）全數除外",
        not any(pathlib.Path(f).name.endswith("-v0.1-draft.md")
                and (_REPO / "specs" / (pathlib.Path(f).name[: -len("-v0.1-draft.md")] + ".md")).exists()
                for f in d["corpus"])))
    _add("sub", lambda d: (
        "  └ 六份生效本全數在 corpus 內（無 -draft 者一份不漏）",
        {p.name for p in (_REPO / "specs").glob("*.md") if not p.name.endswith("-v0.1-draft.md")}
        == {pathlib.Path(f).name for f in d["corpus"]
            if not pathlib.Path(f).name.endswith("-v0.1-draft.md")}))
    _add("sub", lambda d: (
        "  └ 尚無生效本之 draft（L7）在 corpus 內（充任受阻者不得因此脫檢）",
        any(pathlib.Path(f).name.endswith("-v0.1-draft.md") for f in d["corpus"])))
    _add("sub", lambda d: (
        "  └ `specs/*.md` 裸 glob **不等於** corpus（該 glob 含歸檔本，曾致 13 份/352 之誤）",
        len(list((_REPO / "specs").glob("*.md"))) > len(d["corpus"])))

    # 三分之完整性：MC＋上層＋未歸類 ≡ 總 error（未歸類併入任一側即為捏造）
    _add("top", lambda d: (
        "error 三分（MC／上層／未歸類）加總 ≡ 七份總 error（未歸類不得併入任一側）",
        d["values"]["label_errors_mc"] + d["values"]["label_errors_upper"]
        + d["values"]["label_errors_unclassified"] == d["values"]["total_errors"]))
    _add("sub", lambda d: (
        "  └ 未歸類 ≡ 零覆蓋類 error 數（機制一致：無 source 可歸者恰為 tr_absent/tr_zero_coverage 族；"
        "#22 修畢後兩者同為 0，出現零覆蓋時同步 ≥1，不得併入任一側）",
        d["values"]["label_errors_unclassified"]
        == d["kinds"].get("tr_absent", 0) + d["kinds"].get("tr_asserted_absent", 0)
        + d["kinds"].get("tr_zero_coverage", 0)))
    _add("sub", lambda d: (
        "  └ 分型（`kind`）加總 ≡ 七份總 error（每筆 error 皆有機器可辨之型）",
        sum(d["kinds"].values()) == d["values"]["total_errors"] and "«untagged»" not in d["kinds"]))

    # 跨層複製誤標：分佈三列相加 ≡ 總數。README 前版「30 組」之病即在此——其表格三列
    # （7＋3＋21）相加恆為 31，與其標題數自相矛盾，而當時無任何斷言複驗二者。
    _add("top", lambda d: (
        "跨層複製誤標：分佈（4 份／3 份／2 份）相加 ≡ ≥2 份之總組數（README 標題數與表列不得再互斥）",
        d["values"]["dup_mislabels_in_4"] + d["values"]["dup_mislabels_in_3"]
        + d["values"]["dup_mislabels_in_2"] == d["values"]["dup_mislabels"]))
    _add("sub", lambda d: (
        "  └ 逐組明細之組數 ≡ 統計數，且每組確跨 ≥2 份（統計非憑空）",
        len(d["dup_mislabels"]) == d["values"]["dup_mislabels"]
        and all(g["n"] >= 2 and len(g["layers"]) == g["n"] for g in d["dup_mislabels"])))
    _add("sub", lambda d: (
        "  └ 複製誤標取自 finding 之結構化 `code`／`label` 欄（非 grep 訊息反推）",
        all(g["code"] and g["label"] for g in d["dup_mislabels"])))

    # ── Annex TR 資料列數：「矩陣在場而 gate 一列未讀」須被量化而非以散文帶過 ──────────
    #    **不斷言「＝56」**：56 是 ONT 現況之後果，非判準。ONT 增刪一列即該常數失準，而修復
    #    壓力會指向「把 56 改成新數」——正是本輪所拆除之手抄迴路。故一律斷言**結構性質**。
    def _gap(d):
        return [r for r in d["per_file"] if r["tr_rows"] > 0 and r["compared"] == 0]

    _add("top", lambda d: (
        "Annex TR 列數由程式導出（`report.annex_tr_rows`，錨點取自 compliance_lint 之單一判準）"
        f"：{'、'.join(f'{r['layer']} {r['tr_rows']} 列' for r in sorted(d['per_file'], key=lambda x: x['layer']))}",
        all(r["tr_rows"] >= 0 for r in d["per_file"])))
    _add("sub", lambda d: (
        "  └ 「矩陣在場而一列未讀」之規格經量化列出（L2 之 h1 標題病灶；散文不得取代計數）"
        + (f"：{'、'.join(f'{r['layer']}（{r['tr_rows']} 列在場、比對 0 筆）' for r in _gap(d))}"
           if _gap(d) else "：（無——若此處由有轉無，係該病灶已解或已被靜默繞過，須查明何者）"),
        all(r["compared"] == 0 for r in _gap(d))))
    _add("sub", lambda d: (
        "  └ 確無 Annex TR 者（tr_rows＝0）不得被誤計為「有矩陣未讀」（L1／WM 之真陰性不得與 L2 同形）",
        not any(r["tr_rows"] == 0 and r in _gap(d) for r in d["per_file"])))
    _add("sub", lambda d: (
        "  └ 列數與比對筆數為不同量：報表明載不得相減（前版 58／32 分歧即出於混用母集）",
        "列數 ≠ 比對筆數" in report.render(d) and "不得相減" in report.render(d)))

    # 生效本之 FAIL 份數 ≠ corpus_fail（後者含 L7 draft）——workflow 橫幅「其中五份」之來源
    _add("top", lambda d: (
        f"生效本 FAIL 份數（{d['values']['corpus_fail_effective']}）由程式導出，"
        f"且不與含 draft 之 corpus_fail（{d['values']['corpus_fail']}）混同",
        d["values"]["corpus_fail_effective"]
        == sum(1 for r in d["per_file"] if not r["passed"] and not r["is_draft"])
        and d["values"]["corpus_fail_effective"] <= d["values"]["corpus_fail"]))

    # selftest 覆蓋數之限定詞
    _add("top", lambda d: (
        "selftest 覆蓋數自帶限定詞（頂層測項／斷言總數二值俱在，不輸出裸「N 項」）",
        "頂層測項" in report.render(d) and "斷言總數" in report.render(d)
        and d["values"]["selftest_assertions"] > d["values"]["selftest_top_items"]))

    # 產生資訊：產生指令＋git HEAD SHA
    _add("top", lambda d: (
        "report 輸出末尾附產生指令與 git HEAD SHA（使任何轉貼可被追溯）",
        report.GEN_COMMAND in report.render(d) and "git HEAD" in report.render(d)
        and bool(d["git_head"])))

    # ── 綁定本體：逐標記比對 ─────────────────────────────────────────────────────
    _add("top", lambda d: (
        f"[I] 文件權威數字綁定：{len(markers)} 處標記全數與 `report` 輸出一致"
        f"（{'、'.join(sorted({m['file'] for m in markers})) or '（未偵得標記）'}）",
        bool(markers) and not [m for m in markers if not _marker_ok(m, d)]))
    for m in markers:
        _add("sub", (lambda mm: lambda d: (
            f"  └ {mm['file']}:{mm['line']} `{mm['key']}` ＝ {mm['value']}"
            + ("" if _marker_ok(mm, d) else
               f" ✗ report 導出為 {d['values'].get(mm['key'])!r}（不一致即 FAIL；"
               f"請跑 `{report.GEN_COMMAND} --sync`）"),
            _marker_ok(mm, d)))(m))
    _add("sub", lambda d: (
        "  └ 無孤兒 key（文件標記之 key 全部存在於 report values）"
        + (f"：{sorted({m['key'] for m in markers if m['key'] not in d['values']})}"
           if [m for m in markers if m["key"] not in d["values"]] else ""),
        not [m for m in markers if m["key"] not in d["values"]]))

    # ── 二、由 `len(pending)` 導出完整跑完後之覆蓋數（結構性，非常數）──────────────────
    predicted = {
        "top_items": sum(1 for n, _ in records if not n.startswith("  └"))
                     + sum(1 for k, _ in pending if k == "top"),
        "assertions": len(records) + len(pending),
    }
    data = report.build(selftest=predicted)

    # ── 三、逐一發出 ───────────────────────────────────────────────────────────────
    for _kind, fn in pending:
        name, cond = fn(data)
        chk(name, cond)


_CONSISTENCY_CACHE = {}


def _consistency_detail(data) -> list:
    """report 逐檔數字 vs compliance 逐檔輸出之不一致清單（空＝一致）。

    記憶化：本函式為數處斷言共用，每次呼叫皆重跑七份 `lint_spec`，不快取即數倍成本。
    快取鍵含逐檔實測值，故 report 之數字一變即重算——快取不會遮蔽真實之不一致。
    """
    key = tuple((r["file"], r["error"], r["warning"]) for r in data["per_file"])
    if key in _CONSISTENCY_CACHE:
        return _CONSISTENCY_CACHE[key]
    out = []
    for rec in data["per_file"]:
        r = compliance_lint.lint_spec(str(_REPO / rec["file"]), _MC)
        if len(r.errors) != rec["error"] or len(r.warnings) != rec["warning"]:
            out.append(f"{rec['file']}：report {rec['error']}e/{rec['warning']}w "
                       f"vs compliance {len(r.errors)}e/{len(r.warnings)}w")
    _CONSISTENCY_CACHE[key] = out
    return out


def _marker_ok(m, data) -> bool:
    v = data["values"]
    return m["key"] in v and m["value"] == str(v[m["key"]])
