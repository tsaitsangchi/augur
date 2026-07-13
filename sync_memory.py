#!/usr/bin/env python3
"""🎯 Claude memory ⇄ repo 快照 傳輸器 — 讓機器本地的 memory 能隨 git 到其他電腦接續。

Claude memory 住 ~/.claude/projects/<mangled>/memory/,機器本地、不隨 git。本工具把它「快照進 repo
的 handoff_memory/」(export),commit 後隨 git 到別台;新機 clone 後「還原回活 memory」(restore)。
守原則 #28(本地優先,零 Claude usage)、#6(restore 覆蓋前先備份,不毀資料)、#5(memory 無機密才入 repo)。

⚠ 前提:本 repo 為 public——export 快照 commit+push 即公開。memory 內容為 reports/docs 之濃縮
(方法論/特徵/教訓,無 token 密碼),與既有公開內容同級;仍請有意識地選擇公開。

路徑對映:活 memory 目錄由「當前 repo 位置」推導(mangle: '/' → '-'),故新機 clone 到不同路徑亦正確。

執行指令矩陣:
    python sync_memory.py                # status:比對活 memory vs repo 快照(唯讀、預設)
    python sync_memory.py status          # 同上
    python sync_memory.py export          # 活 memory → handoff_memory/(快照進 repo,待 commit)
    python sync_memory.py restore         # handoff_memory/ → 活 memory(新機還原;覆蓋前自動備份)
    python sync_memory.py restore --force  # 略過「已存在且相同」檢查,強制覆蓋(仍先備份)
"""
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SNAPSHOT_DIR = REPO_ROOT / "handoff_memory"


def live_memory_dir() -> Path:
    """由當前 repo 位置推導 Claude Code 的 per-project memory 目錄。"""
    # Claude Code 把路徑中所有非字母數字字元換 '-'(實證:.claude-worktrees→--claude-worktrees、stock_backend→stock-backend);只換 '/' 會在含 . _ 路徑分岔指錯目錄
    mangled = re.sub(r"[^A-Za-z0-9]", "-", str(REPO_ROOT))
    return Path.home() / ".claude" / "projects" / mangled / "memory"


def md_files(d: Path) -> dict[str, Path]:
    return {p.name: p for p in sorted(d.glob("*.md"))} if d.is_dir() else {}


def _classify(src: dict[str, Path], dst: dict[str, Path]) -> tuple[list, list, list]:
    """回 (added, updated, removed):src 相對 dst 之新增/內容不同/多餘。"""
    added, updated, removed = [], [], []
    for name, sp in src.items():
        if name not in dst:
            added.append(name)
        elif sp.read_bytes() != dst[name].read_bytes():
            updated.append(name)
    for name in dst:
        if name not in src:
            removed.append(name)
    return added, updated, removed


def cmd_status() -> int:
    live, snap = live_memory_dir(), SNAPSHOT_DIR
    print(f"活 memory : {live}  ({'存在' if live.is_dir() else '不存在'})")
    print(f"repo 快照 : {snap}  ({'存在' if snap.is_dir() else '不存在'})")
    lf, sf = md_files(live), md_files(snap)
    print(f"活 memory {len(lf)} 檔 / repo 快照 {len(sf)} 檔")
    if not lf and not sf:
        print("兩邊皆空。")
        return 0
    a, u, r = _classify(lf, sf)  # 活相對快照
    if not (a or u or r):
        print("✓ 一致:活 memory 與 repo 快照內容相同。")
    else:
        if a:
            print(f"  活有、快照無(export 會新增): {', '.join(a)}")
        if u:
            print(f"  兩邊內容不同(export 會更新): {', '.join(u)}")
        if r:
            print(f"  快照有、活無(export 會移除 / restore 會帶回): {', '.join(r)}")
    return 0


def cmd_export() -> int:
    live = live_memory_dir()
    if not live.is_dir() or not md_files(live):
        print(f"✗ 活 memory 目錄無內容({live})——無可 export。", file=sys.stderr)
        return 1
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    lf, sf = md_files(live), md_files(SNAPSHOT_DIR)
    a, u, r = _classify(lf, sf)
    for name, sp in lf.items():
        shutil.copy2(sp, SNAPSHOT_DIR / name)
    for name in r:  # 活已刪 → 快照同步移除,保持忠實
        (SNAPSHOT_DIR / name).unlink()
    print(f"✓ export 完成:{len(lf)} 檔快照到 {SNAPSHOT_DIR.relative_to(REPO_ROOT)}/")
    print(f"  新增 {len(a)} · 更新 {len(u)} · 移除 {len(r)}")
    print("  下一步:git add handoff_memory/ && commit + push(對外公開,需你授權)。")
    return 0


def cmd_restore(force: bool) -> int:
    snap = SNAPSHOT_DIR
    if not snap.is_dir() or not md_files(snap):
        print(f"✗ repo 快照無內容({snap})——無可 restore。", file=sys.stderr)
        return 1
    live = live_memory_dir()
    live.mkdir(parents=True, exist_ok=True)
    sf, lf = md_files(snap), md_files(live)
    a, u, r = _classify(sf, lf)  # 快照相對活:新增 / 內容不同 / 活多餘(快照沒有)
    at_risk = u  # 只有「兩邊都有且內容不同」的活檔才會被覆蓋 → 先備份(#6 不毀資料);r 保留未動、不需備份
    to_write = list(sf) if force else (a + u)
    if at_risk:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = live.parent / f"memory_backup_{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        for name in at_risk:
            shutil.copy2(lf[name], backup / name)
        print(f"  已備份 {len(at_risk)} 個將被覆蓋的活檔 → {backup}")
    for name in to_write:
        shutil.copy2(sf[name], live / name)
    if not (a or u) and not force:
        print("✓ 活 memory 已與快照一致,無需還原。")
    else:
        print(f"✓ restore 完成:寫入 {live}")
        print(f"  新增 {len(a)} · 更新 {len(u)}(被覆蓋的已先備份)")
    if r:
        print(f"  ⚠ 活 memory 另有快照沒有的檔(保留未動): {', '.join(r)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude memory ⇄ repo 快照 傳輸器(零 Claude usage)")
    ap.add_argument("cmd", nargs="?", default="status", choices=["status", "export", "restore"],
                    help="status(預設唯讀比對) / export(活→repo) / restore(repo→活)")
    ap.add_argument("--force", action="store_true", help="restore 時強制覆蓋(仍先備份)")
    args = ap.parse_args()
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "export":
        return cmd_export()
    return cmd_restore(args.force)


if __name__ == "__main__":
    sys.exit(main())
