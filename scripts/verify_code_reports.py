#!/usr/bin/env python
"""augur 程式 + reports 結構驗證 — 全 .py 編譯 + docstring 一致性、reports 清點(已驗結構基礎)。

🎯 這支在做什麼(白話):把「懂全部」擴到 code+reports 之**可機械驗部分**:
- 全 src/scripts .py:能否 import-compile(無語法錯)+ 有無 module docstring(CLAUDE #18 要 🎯)+ 首行主旨
- reports/*.md:清點 + 各首標題
這驗的是**結構/一致性/可文件性**(非深層語意理解——深層靠人讀 + spot 驗、誠實標)。

唯讀、本地、零 usage(#28)。守 #15(機械驗結構、誠實標未深讀者)。
執行指令矩陣:python scripts/verify_code_reports.py
"""
import ast
import pathlib
import py_compile

ROOT = pathlib.Path("/home/hugo/project/augur")


def doc1(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        d = ast.get_docstring(tree)
        return d.strip().splitlines()[0][:70] if d else None
    except Exception:
        return None


def main():
    for label, globpat in (("src/augur", "src/augur/**/*.py"), ("scripts", "scripts/*.py")):
        files = sorted(p for p in ROOT.glob(globpat) if "__pycache__" not in str(p) and p.name != "__init__.py")
        ok = nodoc = fail = 0
        print(f"\n══ {label}（{len(files)} .py）══")
        for p in files:
            try:
                py_compile.compile(str(p), doraise=True)
                ce = "✅"
                ok += 1
            except py_compile.PyCompileError:
                ce = "❌編譯"
                fail += 1
            d = doc1(p)
            if d is None:
                nodoc += 1
            print(f"  {ce} {p.relative_to(ROOT).as_posix():46s} {d or '⚠️ 無 docstring'}")
        print(f"  → 編譯 {ok}✅/{fail}❌、無 docstring {nodoc}")

    reps = sorted(ROOT.glob("reports/*.md"))
    print(f"\n══ reports（{len(reps)} 份）══")
    for p in reps:
        first = next((ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("#")), "(無標題)")
        print(f"  {p.name:54s} {first[:60]}")


if __name__ == "__main__":
    main()
