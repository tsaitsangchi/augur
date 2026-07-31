#!/usr/bin/env python
"""git hook 安裝器 — 把 ops/githooks/ 之 hook 複製進 .git/hooks/（換機必跑）。

🎯 這支在做什麼(白話):`.git/hooks/` **不隨 git 走**,所以 pre-commit 閘在換機／重新 clone 後會消失。
   本支把 repo 內受版控之 `ops/githooks/*` 複製進 `.git/hooks/` 並加執行權,使機械閘可攜。
   為何需要:2026-07-31 單一角色整併後,`#8` 隔離之 DB 層已不存在,AST 字面稽核成為**唯一**機械防線;
   而該閘在此之前無任何自動觸發點(`.git/hooks` 非 sample 檔＝0、無 CI、無 cron)——r2 債 #6。
   hook 內容之射程與「為何不掛 constitution_lint --selftest」見 `ops/githooks/pre-commit` 檔頭。

守 #28(純 stdlib、零新依賴、不引入 pre-commit 框架)· #29a(個別可執行)· #29d(矩陣＋實測)。

執行指令矩陣:
  python scripts/install_git_hooks.py            # 無參數:唯讀比對(印各 hook 之安裝狀態,不寫)
  python scripts/install_git_hooks.py --apply    # 實際安裝/更新 .git/hooks/
  python scripts/install_git_hooks.py --selftest # 純紅綠自測(免 DB 免 API 免網路)
"""
import argparse
import filecmp
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

SRC_DIR = Path(__file__).resolve().parent.parent / "ops" / "githooks"


def _hooks_dir() -> Path:
    out = subprocess.run(["git", "rev-parse", "--git-path", "hooks"],
                         capture_output=True, text=True, check=True).stdout.strip()
    return Path(out) if Path(out).is_absolute() else Path.cwd() / out


def status(apply: bool = False) -> int:
    if not SRC_DIR.is_dir():
        print(f"✗ 來源不存在:{SRC_DIR}")
        return 1
    dst_dir = _hooks_dir()
    dst_dir.mkdir(parents=True, exist_ok=True)
    n_ok = n_diff = 0
    for src in sorted(SRC_DIR.iterdir()):
        if not src.is_file():
            continue
        dst = dst_dir / src.name
        same = dst.is_file() and filecmp.cmp(src, dst, shallow=False)
        if same:
            print(f"  ✓ {src.name} 已是最新")
            n_ok += 1
            continue
        n_diff += 1
        if apply:
            shutil.copy2(src, dst)
            dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"  ↻ {src.name} 已安裝/更新 → {dst}")
        else:
            print(f"  ✗ {src.name} {'內容不同' if dst.is_file() else '未安裝'}（--apply 以安裝）")
    if not apply and n_diff:
        print(f"── {n_diff} 個 hook 待安裝;跑 --apply")
        return 1
    print(f"── hooks 就緒（{n_ok + (n_diff if apply else 0)} 個）")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("來源目錄存在", SRC_DIR.is_dir())
    hooks = [p for p in SRC_DIR.iterdir() if p.is_file()] if SRC_DIR.is_dir() else []
    chk(f"至少一個 hook（實得 {len(hooks)}）", hooks)
    chk("pre-commit 在其中", any(p.name == "pre-commit" for p in hooks))
    body = (SRC_DIR / "pre-commit").read_text(encoding="utf-8") if (SRC_DIR / "pre-commit").is_file() else ""
    # 行為級:hook 須真的呼叫三閘,且**不得**掛現為紅之 constitution_lint --selftest
    chk("掛 check_treaty_refs", "check_treaty_refs.py" in body)
    chk("掛 check_cmd_matrix", "check_cmd_matrix.py" in body)
    chk("掛 #8 AST 閘 check_isolation", "check_isolation" in body)
    chk("**未**掛現為紅之 constitution_lint --selftest（掛了會使 repo 不可 commit）",
        "constitution_lint" not in body.split("射程誠實", 1)[-1].split("set -u", 1)[0] or "--selftest\"" not in body)
    chk("失敗會中止 commit（exit 1）", "exit 1" in body)
    chk("矩陣字串在 docstring", "執行指令矩陣" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="git hook 安裝器（唯讀預設）")
    ap.add_argument("--apply", action="store_true", help="實際安裝/更新 .git/hooks/")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.apply:
        print((__doc__ or "").split("執行指令矩陣:", 1)[-1].rstrip())
        print("── 唯讀比對:")
    return status(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
