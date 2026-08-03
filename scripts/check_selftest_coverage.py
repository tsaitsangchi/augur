#!/usr/bin/env python3
"""🎯 selftest／pytest 排程覆蓋探針——288 有自測僅 3 入排程之可見載體（M-O4）。

白話:週一 08:40 現只跑三支 MCP＋gpu。本支度量「含 --selftest 之檔」與
 「crontab／install_cron 已掛者」之差，並可供掛既有 08:40 班次（零新排程）。

門檻:已排程 selftest 入口 < min_scheduled（預設 8）⇒ 紅；pytest 排程數=0 ⇒ 紅。
今日 live 預期紅（先驗紅）。

守原則 #15 · #29 · #35 · master 第 24 步（零新排程）。

執行指令矩陣
------------
    python3 scripts/check_selftest_coverage.py              # 無參數＝--check
    python3 scripts/check_selftest_coverage.py --check      # 覆蓋不足 → rc=1
    python3 scripts/check_selftest_coverage.py --check --json
    python3 scripts/check_selftest_coverage.py --selftest
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
INSTALL_CRON = REPO / "install_cron.sh"
# master：288／僅 3 入排程 → 今日必紅。占比門檻保守（≥5% 才不紅），逐步拉高排程後才綠。
MIN_COVERAGE_RATIO = 0.05


def files_with_selftest(root: Path) -> list[str]:
    """掃描 scripts/、tools/、src/ 內宣告 --selftest 之入口。純函式式掃檔。"""
    out = []
    for base in ("scripts", "tools", "src"):
        d = root / base
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.py")):
            if any(x in str(p) for x in ("/venv/", "__pycache__", "/.git/")):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "--selftest" in text and (
                "add_argument" in text or "argv" in text or "__main__" in text
            ):
                out.append(str(p.relative_to(root)))
    return out


def pytest_files(root: Path) -> list[str]:
    d = root / "tests"
    if not d.exists():
        return []
    return sorted(str(p.relative_to(root)) for p in d.rglob("test_*.py"))


def scheduled_selftest_entrypoints(cron_text: str) -> set[str]:
    """從 crontab／install_cron 抓**真入口**（MCP 模組名／scripts/*.py --selftest）。純函式。"""
    hits = set()
    for mod in ("constitution_mcp", "local_llm_mcp", "project_memory_mcp"):
        if re.search(rf"{re.escape(mod)}[^\n]*--selftest", cron_text):
            hits.add(f"mcp:{mod}")
    for m in re.finditer(r"(scripts/[\w./-]+\.py)\s+[^\n]*--selftest", cron_text):
        hits.add(m.group(1))
    for m in re.finditer(r"python3\s+([\w./-]+\.py)\s+[^\n]*--selftest", cron_text):
        hits.add(m.group(1))
    if "check_selftest_coverage" in cron_text:
        hits.add("scripts/check_selftest_coverage.py")
    return hits


def scheduled_pytest_files(cron_text: str) -> set[str]:
    """cron 正文明確點名的 tests/…。純函式。"""
    return set(re.findall(r"tests/[\w./-]+\.py", cron_text))


def coverage_rc(*, n_with_selftest: int, n_scheduled: int,
                n_pytest_files: int, n_pytest_scheduled: int,
                min_ratio: float = MIN_COVERAGE_RATIO) -> int:
    """selftest 排程占比過低、或有 pytest 檔卻零排程 → 紅。純函式。"""
    if n_pytest_files > 0 and n_pytest_scheduled < 1:
        return 1
    if n_with_selftest <= 0:
        return 0
    if (n_scheduled / n_with_selftest) < min_ratio:
        return 1
    return 0


def _cron_blob() -> str:
    parts = []
    if INSTALL_CRON.exists():
        parts.append(INSTALL_CRON.read_text(encoding="utf-8"))
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout:
            parts.append(r.stdout)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "\n".join(parts)


def _check(*, as_json=False) -> int:
    selftests = files_with_selftest(REPO)
    pytests = pytest_files(REPO)
    blob = _cron_blob()
    scheduled = scheduled_selftest_entrypoints(blob)
    pytest_sched = scheduled_pytest_files(blob)
    ratio = (len(scheduled) / len(selftests)) if selftests else 1.0
    rc = coverage_rc(
        n_with_selftest=len(selftests),
        n_scheduled=len(scheduled),
        n_pytest_files=len(pytests),
        n_pytest_scheduled=len(pytest_sched),
    )
    out = {
        "n_files_with_selftest": len(selftests),
        "n_pytest_files": len(pytests),
        "scheduled_entrypoints": sorted(scheduled),
        "n_scheduled_entrypoints": len(scheduled),
        "coverage_ratio": round(ratio, 6),
        "min_coverage_ratio": MIN_COVERAGE_RATIO,
        "scheduled_pytest_files": sorted(pytest_sched),
        "rc": rc,
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return rc
    print("── selftest／pytest 排程覆蓋（M-O4）──")
    print(f"  含 --selftest 檔={len(selftests)}  pytest 檔={len(pytests)}")
    print(f"  已排程入口={len(scheduled)} {sorted(scheduled)}")
    print(f"  已排程 pytest 檔={sorted(pytest_sched)}  ratio={ratio:.4f} "
          f"(門檻≥{MIN_COVERAGE_RATIO})  → rc={rc}"
          + (" 🔴" if rc else " 🟢"))
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # 先驗紅：303 檔只排 3（≈0.01）≪ 5%
    chk("先驗紅：3/303 + 有 pytest 檔卻零點名 ⇒ rc=1",
        coverage_rc(n_with_selftest=303, n_scheduled=3,
                    n_pytest_files=30, n_pytest_scheduled=0) == 1)
    chk("先驗紅：占比不足（10/303）即便有 pytest 點名",
        coverage_rc(n_with_selftest=303, n_scheduled=10,
                    n_pytest_files=30, n_pytest_scheduled=2) == 1)
    chk("綠：占比達門檻且 pytest 有排",
        coverage_rc(n_with_selftest=100, n_scheduled=5,
                    n_pytest_files=10, n_pytest_scheduled=1) == 0)
    sample = (
        "40 8 * * 1 python3 -m tools.constitution_mcp --selftest; "
        "pytest tests/test_philosophy_isolation.py"
    )
    m = scheduled_selftest_entrypoints(sample)
    p = scheduled_pytest_files(sample)
    chk("解析 mcp", "mcp:constitution_mcp" in m)
    chk("解析 pytest 檔", "tests/test_philosophy_isolation.py" in p)

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="selftest 排程覆蓋探針（M-O4）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check(as_json=a.json)


if __name__ == "__main__":
    sys.exit(main())
