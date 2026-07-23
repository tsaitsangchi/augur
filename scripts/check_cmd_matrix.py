#!/usr/bin/env python
"""執行指令矩陣稽核器 — 掃全 repo `.py`，查缺 canonical「執行指令矩陣」之可執行入口（RULING-2026-026）。

🎯 這支在做什麼（白話）：Steward 裁決第 2026-026 號（AL-2026-029；§8.1 解釋）要求凡 `scripts/` CLI，
   或具 `if __name__ == "__main__"` 之 library／tools／ops 模組，其 docstring 一律須載明 canonical
   標題「執行指令矩陣」——缺矩陣之入口不得充作「已個別驗證／合規稽核通過」之依據。本器把此義務
   機械化為可重跑之本地稽核：全 repo 唯讀掃描（不動任何檔），列出缺漏並以 exit code 是否為 0 表示
   通過／未通過，供隨時自跑或掛 CI／pre-commit（零 Claude usage，#28 本地優先）。

掃描範圍：
  (1) `scripts/`（含 `_bootstrap.py`）——每支 `.py` 均須具矩陣字串（此目錄不論有無 `__main__`）。
  (2) `src/`／`tools/`／`ops/`／`augur_proxy/`／`tests/` 內具 `if __name__ == "__main__"` 之模組
      （純 pytest 測試檔——即 `tests/` 內無 `__main__` 者——依既定個別執行協定 `pytest x.py -v`，
      非本裁決「可執行入口」範疇，不強制）。
  (3) `__main__.py`／`selftest.py`／`measure.py` 等套件入口名（即便判準 (1)(2) 未觸及）。

跳過：`.venv`／`venv`／`__pycache__`／`.git`；純 `__init__.py` 與已於本檔 `EXEMPT` 登錄之薄
re-export（登錄需附理由，不得靜默略過）。

守 #7（實測）· #15（無幻像：缺漏清單為程式掃描所得，非人工估算）· #18／#29（矩陣義務）·
守 RULING-2026-026（本器即該裁決之落地工具）。

執行指令矩陣：
  python scripts/check_cmd_matrix.py              # 全量掃描、印缺漏清單＋統計；有缺漏 → exit 1
  python scripts/check_cmd_matrix.py --quiet       # 僅印統計摘要（供 CI 精簡輸出）
  python scripts/check_cmd_matrix.py --selftest    # 對合成暫存檔跑判準紅綠自測（零外部依賴）
"""
import argparse
import ast
import os
import pathlib
import sys

import _bootstrap  # noqa: F401

REPO = pathlib.Path(__file__).resolve().parent.parent
MATRIX_STR = "執行指令矩陣"
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules",
             ".mypy_cache", ".pytest_cache", ".idea", ".cache"}
SCAN_TOP_DIRS = ("scripts", "src", "tools", "ops", "augur_proxy", "tests")
NAMED_ENTRY_FILES = {"__main__.py", "selftest.py", "measure.py"}

# 薄 re-export／無 CLI 意義之豁免（附理由；新增豁免須在此登錄，不得程式外靜默略過）。
EXEMPT = {
    # 範例登錄格式（目前無豁免項目——純 __init__.py 已由 is_init 邏輯自動排除，無須登錄）：
    # "path/relative/to/repo.py": "理由",
}


def _iter_py_files():
    for top in SCAN_TOP_DIRS:
        root = REPO / top
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".py"):
                    yield pathlib.Path(dirpath) / fn


def _has_main(src: str) -> bool:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return '__name__ == "__main__"' in src or "__name__ == '__main__'" in src
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"):
                return True
    return False


def scan():
    """回 (checked:list[dict], missing:list[dict], exempt:list[dict])。"""
    checked, missing, exempt = [], [], []
    for f in sorted(_iter_py_files()):
        rel = str(f.relative_to(REPO))
        top = rel.split(os.sep)[0]
        fn = f.name
        if fn == "__init__.py":
            continue  # 純套件標記，非 CLI 入口
        if rel in EXEMPT:
            exempt.append({"path": rel, "reason": EXEMPT[rel]})
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            missing.append({"path": rel, "reason": f"無法讀取：{exc}"})
            continue

        in_scope = (
            top == "scripts"
            or fn in NAMED_ENTRY_FILES
            or _has_main(src)
        )
        if not in_scope:
            continue
        checked.append({"path": rel})
        if MATRIX_STR not in src:
            missing.append({"path": rel, "reason": "缺 canonical「執行指令矩陣」字串"})
    return checked, missing, exempt


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--quiet", action="store_true", help="僅印統計摘要")
    p.add_argument("--selftest", action="store_true", help="紅綠自測（零外部依賴）")
    args = p.parse_args(argv)

    if args.selftest:
        return _selftest()

    checked, missing, exempt = scan()
    if not args.quiet:
        for m in missing:
            print(f"  ✗ NEED  {m['path']}：{m['reason']}")
        for e in exempt:
            print(f"  ⊘ 豁免  {e['path']}：{e['reason']}")
    print(f"── 執行指令矩陣稽核：受檢 {len(checked)} 支／缺漏 {len(missing)} 支／豁免 {len(exempt)} 支")
    if missing:
        print("  未通過。補齊方式見 CLAUDE.md #18／#29；裁決依據 constitution/RULING-2026-026-CMD-MATRIX.md")
        return 1
    print("  ✓ 全數通過（NEED=0）")
    return 0


def _selftest() -> int:
    import tempfile

    ok = _has_main('if __name__ == "__main__":\n    pass\n')
    ok = ok and not _has_main("x = 1\n")
    ok = ok and _has_main("if __name__=='__main__':\n    pass\n")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td) / "scripts"
        root.mkdir()
        (root / "good.py").write_text(
            '"""示範。\n\n執行指令矩陣：\n  python scripts/good.py\n"""\n', encoding="utf-8"
        )
        (root / "bad.py").write_text('"""缺矩陣。"""\n', encoding="utf-8")

        global SCAN_TOP_DIRS, REPO
        prev_repo, prev_dirs = REPO, SCAN_TOP_DIRS
        REPO = pathlib.Path(td)
        SCAN_TOP_DIRS = ("scripts",)
        try:
            checked, missing, exempt = scan()
            ok = ok and len(checked) == 2 and len(missing) == 1
            ok = ok and missing[0]["path"] == "scripts/bad.py"
        finally:
            REPO, SCAN_TOP_DIRS = prev_repo, prev_dirs

    print("check_cmd_matrix selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
