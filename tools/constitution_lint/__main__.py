"""constitution_lint CLI。

  python -m tools.constitution_lint compliance <spec.md> [<spec2.md> …]   # 規格生效 lint
  python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]  # code 合憲 lint
  python -m tools.constitution_lint --selftest                            # 紅綠自檢（零外部依賴）

退出碼：任一目標有 error → 1；否則 0。治權自動化止於判定與阻擋（P5.W2）。
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

from . import audit_lint, compliance_lint, mc_clauses

_HERE = pathlib.Path(__file__).resolve().parent
_FIX = _HERE / "fixtures"
_REPO = _HERE.parents[1]   # tools/constitution_lint → repo 根
_MC = str(_REPO / "constitution" / "META-CONSTITUTION.md")


def _selftest() -> int:
    """紅綠自檢：AUGUR-WM v1.0 綠、good fixture 綠、三反例紅。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    wm = _REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md"
    if wm.exists():
        r = compliance_lint.lint_spec(str(wm), _MC)
        chk("AUGUR-WM v1.0 自檢綠（零 error；含 minor 版落差不誤紅）", r.passed)
        chk("  └ minor 版落差判為 info（非 error）", any(f.rule == "WM.45" and f.severity.value == "info" for f in r.findings))
    else:
        print("  ⚠ 找不到 AUGUR-WM，跳過該項（非 repo 內執行）")

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
            print(f"      ↳ 非預期 error：{f.rule}: {f.message}")
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
            print("  ⚠ 找不到 AUGUR-WM，跳過 B8/B9 突變鎖")

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

    print("自檢：" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] in ("--selftest", "selftest"):
        return _selftest()

    cmd, rest = argv[0], argv[1:]
    any_error = False
    if cmd == "compliance":
        if not rest:
            print("用法：compliance <spec.md> [<spec2.md> …]")
            return 2
        for spec in rest:
            r = compliance_lint.lint_spec(spec, _MC)
            print(r.report())
            any_error = any_error or not r.passed
    elif cmd == "audit":
        policy = "legacy"
        paths = []
        i = 0
        while i < len(rest):
            if rest[i] == "--policy":
                policy = rest[i + 1]
                i += 2
            else:
                paths.append(rest[i])
                i += 1
        if not paths:
            print("用法：audit <code-dir> [--policy legacy|greenfield]")
            return 2
        for p in paths:
            r = audit_lint.lint_code(p, policy)
            print(r.report())
            any_error = any_error or not r.passed
    else:
        print(f"未知子命令：{cmd}（compliance | audit | --selftest）")
        return 2
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
