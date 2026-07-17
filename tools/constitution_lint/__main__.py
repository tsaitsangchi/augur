"""constitution_lint CLI。

  python -m tools.constitution_lint compliance <spec.md> [<spec2.md> …]   # 規格生效 lint
  python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]  # code 合憲 lint
  python -m tools.constitution_lint --selftest                            # 紅綠自檢（零外部依賴）

退出碼：任一目標有 error → 1；否則 0。治權自動化止於判定與阻擋（P5.W2）。
"""
from __future__ import annotations

import pathlib
import sys

from . import audit_lint, compliance_lint

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
    chk("  └ 誤標訊息並列「規格所載」與「憲章原文」", "規格所載" in msgs and "憲章原文" in msgs)

    # 正例：合法標籤不得誤紅（引用原文／正文逐字濃縮／僅列代號無標籤／非 MC 代號）
    rg = compliance_lint.lint_spec(str(_FIX / "good_label_ok.md"), _MC)
    chk("good_label_ok fixture 綠（合法標籤不誤紅）", rg.passed)
    if not rg.passed:
        for f in rg.errors:
            print(f"      ↳ 非預期 error：{f.rule}: {f.message}")

    # ── 新檢查二：WM.40 閉集擴欄 ───────────────────────────────────────────────
    chk("WM.40 閉集由 WM 規格原文動態解析（非硬編碼）",
        compliance_lint._wm40_closed_set()[1] == "WM 原文")
    chk("  └ 解析出 14 欄", len(compliance_lint._wm40_closed_set()[0]) == 14)
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
