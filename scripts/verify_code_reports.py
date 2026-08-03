#!/usr/bin/env python
"""augur 程式 + reports 結構驗證 — 全 .py 編譯 + docstring 一致性、reports 清點(已驗結構基礎)。

🎯 這支在做什麼(白話):把「懂全部」擴到 code+reports 之**可機械驗部分**:
- 全 src/scripts .py:能否 import-compile(無語法錯)+ 有無 module docstring(CLAUDE #18 要 🎯)+ 首行主旨
- reports/*.md:清點 + 各首標題
這驗的是**結構/一致性/可文件性**(非深層語意理解——深層靠人讀 + spot 驗、誠實標)。

唯讀、本地、零 usage(#28)。守 #15(機械驗結構、誠實標未深讀者)、#12(路徑推導單一住所)。

## 掃描根：兩尺並列（M-N18，2026-08-03）

病:舊碼 `ROOT = pathlib.Path("/home/hugo/project/augur")` 為**硬編絕對路徑**——在 worktree
內跑本支,印出的是**主庫**的數字(2026-08-03 親驗:worktree 實有 301 scripts/275 reports,
舊碼卻報主庫的 329/304)。使用者以為驗了自己正在編輯的那棵樹,其實沒有;且該數字會被下游
(M-N17 報告索引)當成本樹口徑,是「一個數字冒充另一把尺」之型。

修:兩把尺各自具名、並列印出,誰也不冒充誰——
  · **掃描尺** `scan_root()`＝本檔所在工作樹(`Path(__file__).resolve().parents[1]`);
    寫法同源 `scripts/check_vendor_binding.py:47`。本支要驗的是「你正在編輯的這棵樹」,故掃它。
  · **主庫尺** `main_repo_root()`＝`git rev-parse --git-common-dir` 之父層(worktree 亦指回主庫);
    推導式**同源 `ops/githooks/pre-commit`**(M-G1 同日修;#12 同一式只有一種寫法)。該 hook 取
    主庫是因為 venv 只在主庫;本支不取它當掃描根,只用來標示「你現在不在主庫」。
  兩尺相異時大聲標示 `⚠ worktree`,使 worktree 的數字永遠不會被誤讀為主庫的數字。

執行指令矩陣
------------
    python scripts/verify_code_reports.py             # 無參數＝掃本檔所在工作樹(唯讀報表)
    python scripts/verify_code_reports.py --selftest  # 紅綠自測(fixture 樹驅動;免 DB 免 API 免 git 寫入)
"""
import argparse
import ast
import os
import pathlib
import py_compile
import subprocess
import sys
import tempfile

PY_GLOBS = (("src/augur", "src/augur/**/*.py"), ("scripts", "scripts/*.py"))
REPORT_GLOB = "reports/*.md"


def scan_root(script_path=__file__):
    """掃描根＝本檔所在工作樹(worktree 跑就掃 worktree、主庫跑就掃主庫)。

    不硬編絕對路徑;寫法同源 scripts/check_vendor_binding.py:47。
    """
    return pathlib.Path(script_path).resolve().parents[1]


def main_repo_root(start=None):
    """主庫根(`git rev-parse --git-common-dir` 之父層;worktree 亦指回主庫)。

    推導式同源 ops/githooks/pre-commit(#12)。非 git 樹/無 git 可執行檔時回 None
    ——僅使兩尺並列少一把,不致命、不擲例外。
    """
    cwd = pathlib.Path(start) if start else scan_root()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(cwd), capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    common = pathlib.Path(out.stdout.strip())
    if not common.is_absolute():
        common = cwd / common
    return common.parent.resolve()


def scan_tree(root):
    """列舉受掃檔案(main() 與 --selftest 走同一條路徑,自測才咬得到真行為 #35)。

    回 {label: [Path,…]};排除 `__pycache__` 與 `__init__.py`(同舊碼口徑)。
    """
    found = {}
    for label, globpat in PY_GLOBS:
        found[label] = sorted(
            p for p in root.glob(globpat) if "__pycache__" not in str(p) and p.name != "__init__.py"
        )
    found["reports"] = sorted(root.glob(REPORT_GLOB))
    return found


def doc1(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        d = ast.get_docstring(tree)
        return d.strip().splitlines()[0][:70] if d else None
    except Exception:
        return None


def _print_rulers(root):
    main_root = main_repo_root()
    print(f"── 掃描尺(本檔所在工作樹)：{root}")
    if main_root is None:
        print("── 主庫尺：(不可得——非 git 樹或無 git)")
    elif main_root == root:
        print(f"── 主庫尺：{main_root}　(＝掃描尺，本次跑在主庫)")
    else:
        print(f"── 主庫尺：{main_root}")
        print("   ⚠ worktree：以下數字屬**本工作樹**，不是主庫的數字，勿互相引用。")


def run_scan():
    root = scan_root()
    _print_rulers(root)
    found = scan_tree(root)

    for label, _ in PY_GLOBS:
        files = found[label]
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
            print(f"  {ce} {p.relative_to(root).as_posix():46s} {d or '⚠️ 無 docstring'}")
        print(f"  → 編譯 {ok}✅/{fail}❌、無 docstring {nodoc}")

    reps = found["reports"]
    print(f"\n══ reports（{len(reps)} 份）══")
    for p in reps:
        first = next((ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("#")), "(無標題)")
        print(f"  {p.name:54s} {first[:60]}")
    return 0


def _build_fixture(base):
    """造一棵**真的**假工作樹(非手寫形狀);回 (root, script_path)。"""
    root = pathlib.Path(base) / "fake_tree"
    (root / "scripts").mkdir(parents=True)
    (root / "src" / "augur" / "pkg" / "__pycache__").mkdir(parents=True)
    (root / "reports").mkdir()
    script = root / "scripts" / "verify_code_reports.py"
    script.write_text('"""🎯 fixture 本體。"""\n', encoding="utf-8")
    (root / "scripts" / "zz_fixture_sentinel.py").write_text(
        '"""🎯 fixture 哨兵——只存在於本次 fixture。"""\n', encoding="utf-8"
    )
    (root / "scripts" / "zz_fixture_nodoc.py").write_text("x = 1\n", encoding="utf-8")
    (root / "src" / "augur" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "augur" / "pkg" / "zz_fixture_mod.py").write_text('"""🎯 fixture 模組。"""\n', encoding="utf-8")
    (root / "src" / "augur" / "pkg" / "__pycache__" / "zz_fixture_cached.py").write_text("y = 2\n", encoding="utf-8")
    (root / "reports" / "zz_fixture_report.md").write_text("# fixture 報告\n", encoding="utf-8")
    return root, script


def _walk_names(root, subdir, suffix):
    """獨立列舉(不呼叫 scan_tree),供比對——避免拿被測物自證。"""
    names = set()
    for dirpath, _dirnames, filenames in os.walk(root / subdir):
        for fn in filenames:
            if fn.endswith(suffix):
                names.add(pathlib.Path(dirpath, fn).relative_to(root).as_posix())
    return names


def selftest():
    """紅綠自測:餵真 fixture 樹,咬「掃描根不得跑到別棵樹去」這條不變式。"""
    fails = []

    def chk(name, cond, detail=""):
        print(f"  {'✅' if cond else '❌'} {name}{('：' + detail) if detail else ''}")
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory(prefix="vcr_selftest_") as tmp:
        fx_root, fx_script = _build_fixture(tmp)
        fx_root_real = fx_root.resolve()

        derived = scan_root(fx_script)
        chk("掃描根＝被測檔所在樹(非硬編)", derived == fx_root_real, f"{derived}")

        found = scan_tree(derived)

        def rel_in_tree(paths):
            # 只映射落在被測樹內者——樹外檔(＝掃錯樹)由下一條絆線點名，不在此靜默丟例外
            return {p.relative_to(fx_root_real).as_posix() for p in paths if p.is_relative_to(fx_root_real)}

        got_scripts = rel_in_tree(found["scripts"])
        got_src = rel_in_tree(found["src/augur"])
        got_reports = rel_in_tree(found["reports"])

        # 下游絆線:掃描結果必須**全部**落在 fixture 樹內(退回硬編即整批落在主庫 ⇒ 這幾條全紅)
        all_paths = [p for v in found.values() for p in v]
        chk("受掃檔全數落在被測樹內", bool(all_paths) and all(p.is_relative_to(fx_root_real) for p in all_paths),
            f"{len(all_paths)} 檔")

        # 與獨立列舉(os.walk)對帳,而非與寫死的數字對帳
        want_scripts = _walk_names(fx_root_real, "scripts", ".py")
        want_reports = _walk_names(fx_root_real, "reports", ".md")
        chk("scripts 清單＝獨立列舉", got_scripts == want_scripts, f"{sorted(got_scripts)}")
        chk("reports 清單＝獨立列舉", got_reports == want_reports, f"{sorted(got_reports)}")

        # 口徑不變式:排除 __init__.py 與 __pycache__
        chk("排除 __init__.py", all(not n.endswith("__init__.py") for n in got_src), f"{sorted(got_src)}")
        chk("排除 __pycache__", all("__pycache__" not in n for n in got_src))
        chk("src 仍收到一般模組", "src/augur/pkg/zz_fixture_mod.py" in got_src)

        # doc1 之紅綠雙向
        d_ok = doc1(fx_root_real / "scripts" / "zz_fixture_sentinel.py")
        d_no = doc1(fx_root_real / "scripts" / "zz_fixture_nodoc.py")
        chk("doc1 取到首行主旨", bool(d_ok) and d_ok.startswith("🎯 fixture 哨兵"), f"{d_ok!r}")
        chk("doc1 對無 docstring 回 None", d_no is None, f"{d_no!r}")

        # 主庫尺:非 git 樹須 graceful 回 None(不擲例外、不誤把 tmp 當主庫)
        chk("主庫尺於非 git 樹回 None", main_repo_root(fx_root_real) is None, f"{main_repo_root(fx_root_real)}")

    # 本樹之主庫尺:條件依「本檔所在樹是不是 git 樹」而定(主庫為 .git 目錄、worktree 為 .git 檔,
    # 皆 exists();落在 /tmp 之複本則否)——使自測結果不隨執行位置漂移。
    here_root = scan_root()
    here = main_repo_root()
    if (here_root / ".git").exists():
        chk("主庫尺於 git 樹可得且存在", here is not None and here.is_dir(), f"{here}")
    else:
        chk("非 git 樹之複本:主庫尺 graceful 回 None", here is None, f"{here}")

    print(f"── selftest：{'PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="augur 程式 + reports 結構驗證(唯讀)")
    ap.add_argument("--selftest", action="store_true", help="紅綠自測(fixture 樹驅動;免 DB 免 API)")
    args = ap.parse_args(argv)
    return selftest() if args.selftest else run_scan()


if __name__ == "__main__":
    sys.exit(main())
