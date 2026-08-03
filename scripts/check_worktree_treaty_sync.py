#!/usr/bin/env python3
"""🎯 worktree 治權檔同步哨——防「agent 讀到過期規則卻無人察覺」（M-G1 S2）。

守原則 #15（不同步就要看得見，不得靜默）· #19（治權檔一處改、全鏈對齊）· #29a/d。

起因（2026-08-03 r4 對抗核驗＋主 session 親驗）：Claude Code 為每個 session 建 git
worktree，而 worktree 停在建立當時的 commit。實測：本機三個 worktree 之 CLAUDE.md 分別為
v1.31／v1.32／v1.31，主庫已是 **v1.35**——缺 #33/#34/#35，且仍載已被 #34 反向廢止之
「非必要不 fan-out」為生效條文。凡以相對路徑讀治權檔之 agent，拿到的是舊法。
同一批 worktree 亦使 pre-commit 靜默 rc=0（該病已由 M-G1 S1 之 fail-closed 修補）。

本支只做一件事：**比對主庫與各 worktree 之治權檔版本，不同步即大聲**（rc=1）。
不自動同步——worktree 之 git 狀態屬環境級變更（#6），須人決定 merge／清理／忽略。

執行指令矩陣
------------
    python3 scripts/check_worktree_treaty_sync.py            # 無參數＝--check（唯讀）
    python3 scripts/check_worktree_treaty_sync.py --check    # 逐 worktree 比對，不同步 rc=1
    python3 scripts/check_worktree_treaty_sync.py --quiet    # 只印結論（供 hook/cron）
    python3 scripts/check_worktree_treaty_sync.py --selftest # 紅綠自測（免 git 免 DB）
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

# 受監治權檔＝改了就會改變 agent 行為者（版本行可機械抽取）
WATCHED = ("CLAUDE.md",)
_VER = re.compile(r"v(\d+\.\d+)")


def parse_version(first_line: str):
    """自檔首行抽版本號（如 '# CLAUDE.md — … v1.35（…）' → '1.35'）。純函式；抽不到回 None。"""
    m = _VER.search(first_line or "")
    return m.group(1) if m else None


def compare(main_ver, wt_ver):
    """比對結論。純函式——**抽不到版本一律判不同步**（fail-closed：讀不到≠一致）。"""
    if main_ver is None or wt_ver is None:
        return "UNKNOWN"
    return "SYNCED" if main_ver == wt_ver else "STALE"


def _first_line(path: Path):
    try:
        with path.open(encoding="utf-8") as fh:
            return fh.readline().strip()
    except OSError:
        return None


def _worktrees(main_root: Path):
    """git worktree list --porcelain → [(path, head)]；主庫本身排除。"""
    out = subprocess.run(["git", "worktree", "list", "--porcelain"],
                         capture_output=True, text=True, cwd=str(main_root))
    trees, cur = [], {}
    for line in (out.stdout or "").splitlines():
        if line.startswith("worktree "):
            if cur:
                trees.append(cur)
            cur = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            cur["head"] = line.split(" ", 1)[1][:7]
    if cur:
        trees.append(cur)
    return [t for t in trees if Path(t["path"]).resolve() != main_root.resolve()]


def _check(quiet=False) -> int:
    main_root = Path(__file__).resolve().parents[1]
    trees = _worktrees(main_root)
    if not trees:
        print("✓ 無 worktree（僅主庫）——無同步風險")
        return 0
    bad = 0
    for t in trees:
        wt = Path(t["path"])
        for name in WATCHED:
            mv = parse_version(_first_line(main_root / name))
            wv = parse_version(_first_line(wt / name))
            verdict = compare(mv, wv)
            if verdict != "SYNCED":
                bad += 1
            if not quiet or verdict != "SYNCED":
                mark = {"SYNCED": "✓", "STALE": "✗", "UNKNOWN": "✗"}[verdict]
                print(f"  {mark} {wt.name}／{name}: 主庫 v{mv or '?'} vs worktree v{wv or '?'}"
                      f"（HEAD {t.get('head', '?')}）")
    if bad:
        print(f"✗ {bad} 處治權檔不同步——以相對路徑讀該檔之 agent 會拿到**舊法**。")
        print("  處置屬環境級（#6 不自動改）：清理無用 worktree／同步至主庫／"
              "或於 agent prompt 直接注入現行條文並給絕對路徑。")
    else:
        print(f"✓ {len(trees)} 個 worktree 之治權檔皆與主庫同版")
    return 1 if bad else 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("抽版本：真首行（v1.35）", parse_version("# CLAUDE.md — Augur AI 協作工具規則 v1.35（#35 …）") == "1.35")
    chk("抽版本：舊首行（v1.32）", parse_version("# CLAUDE.md — Augur AI 協作工具規則 v1.32（含 P11 續批）") == "1.32")
    chk("抽版本：無版本號回 None", parse_version("# 隨便一行") is None)
    chk("同版 → SYNCED", compare("1.35", "1.35") == "SYNCED")
    chk("異版 → STALE（本案實形：主 1.35／worktree 1.32）", compare("1.35", "1.32") == "STALE")
    chk("**讀不到一律不判同步**（fail-closed：None≠一致）", compare("1.35", None) == "UNKNOWN")
    chk("主庫讀不到亦 fail-closed", compare(None, "1.35") == "UNKNOWN")
    chk("兩側皆讀不到仍 fail-closed", compare(None, None) == "UNKNOWN")
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="worktree 治權檔同步哨（M-G1 S2）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.quiet):
        print(__doc__.split("執行指令矩陣")[1].split("-----\n")[-1])
    return _check(quiet=a.quiet)


if __name__ == "__main__":
    sys.exit(main())
