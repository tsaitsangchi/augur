"""constitution_lint CLI。

  python -m tools.constitution_lint compliance <spec.md> [<spec2.md> …]   # 規格生效 lint
  python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]  # code 合憲 lint
  python -m tools.constitution_lint report [--json|--sync|--files]        # 全 corpus 權威數字
  python -m tools.constitution_lint --selftest                            # 紅綠自檢（零外部依賴）

`report` 為**全 corpus 權威數字之單一產生點**（machine-readable ＋ human-readable）：受檢
corpus 之定義寫在程式（`report.corpus_files`）而非文件；`--sync` 將數字寫回 [I] 文件之
`<!--lint:KEY-->…<!--/lint-->` 標記——**數字不再經人手轉錄**。selftest 另設綁定斷言：文件
標記與 `report` 輸出不一致即 FAIL。

退出碼：任一目標有 error → 1；否則 0。治權自動化止於判定與阻擋（P5.W2）。
"""
from __future__ import annotations

import json
import pathlib
import sys

from . import audit_lint, compliance_lint, report as report_mod, selftest as selftest_mod

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parents[1]   # tools/constitution_lint → repo 根
_MC = str(_REPO / "constitution" / "META-CONSTITUTION.md")


def _selftest() -> int:
    ok, _records = selftest_mod.run()
    return 0 if ok else 1


def _report(rest) -> int:
    """全 corpus 權威數字。`--json` 僅印 JSON；`--sync` 將數字寫回 [I] 文件標記。

    **退出碼恆為 0**（除非自身炸掉）：`report` 是**度量**，不是**判定**。以 corpus 有無
    error 決定其退出碼，會使 CI 之紅綠繫於報表指令而非 `compliance`——判定與阻擋之權責
    屬 `compliance`／`audit`，度量指令不得越俎代庖。
    """
    if "--files" in rest:
        # 受檢 corpus 之檔案清單（一行一路徑）。CI 與本表自此**共用同一定義**——前版 CI job
        # 以 `find specs -name '*.md'` 列舉（13 份，含歸檔本），與其自身橫幅之七份/200 不符。
        for f in report_mod.corpus_files():
            print(f)
        return 0
    data = report_mod.build()
    if "--sync" in rest:
        changes = report_mod.sync(data)
        if changes:
            print(f"── 已同步 {len(changes)} 處 [I] 文件標記（數字由 `{report_mod.GEN_COMMAND}` 導出，非手抄）")
            for f, k, old, new in changes:
                print(f"  {f}: `{k}` {old} → {new}")
        else:
            print("── [I] 文件標記已與 report 輸出一致，無須變更")
        return 0
    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
          if "--json" in rest else report_mod.render(data))
    return 0
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
    elif cmd == "report":
        return _report(rest)
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
        print(f"未知子命令：{cmd}（compliance | audit | report | --selftest）")
        return 2
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
