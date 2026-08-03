#!/usr/bin/env python3
"""🎯 Claude memory ⇄ repo 快照 傳輸器 — 讓機器本地的 memory 能隨 git 到其他電腦接續。

Claude memory 住 ~/.claude/projects/<mangled>/memory/,機器本地、不隨 git。本工具把它「快照進 repo
的 handoff_memory/」(export),commit 後隨 git 到別台;新機 clone 後「還原回活 memory」(restore)。
守原則 #28(本地優先,零 Claude usage)、#6(restore 覆蓋前先備份,不毀資料)、#5(memory 無機密才入 repo)。

⚠ 前提:本 repo 為 public——export 快照 commit+push 即公開,**push 後不可逆**(主分支不得 force)。
2026-07-13 實犯:export 夾帶 ttai 檔內的明碼服務密碼,靠人在 push 前逐檔掃到才攔下。故 **export
路徑內建明碼憑證掃描、fail-closed**(M-O3):掃到疑似憑證即中止、一個檔都不寫;判準單一住所＝
`augur.audit.plaintext_credential`,誤報之唯一出路＝留痕豁免 `ops/memory_secret_allowlist.txt`
(六欄含人簽與理由)。**無略過旗標**——可略過的閘等於沒有閘。

路徑對映:活 memory 目錄由「當前 repo 位置」推導(mangle: '/' → '-'),故新機 clone 到不同路徑亦正確。

執行指令矩陣:
    python sync_memory.py                # status:比對活 memory vs repo 快照(唯讀、預設)
    python sync_memory.py status          # 同上
    python sync_memory.py export          # 活 memory → handoff_memory/(先過密碼掃描,紅則一個檔都不寫)
    python sync_memory.py scan            # 只跑密碼掃描(唯讀;export 前想先看結果時用)
    python sync_memory.py restore         # handoff_memory/ → 活 memory(新機還原;覆蓋前自動備份)
    python sync_memory.py restore --force  # 略過「已存在且相同」檢查,強制覆蓋(仍先備份)
    python sync_memory.py --selftest      # 零 DB：閘存在／無略過旗標／假綠地板（M-O3）
"""
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SNAPSHOT_DIR = REPO_ROOT / "handoff_memory"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def load_scanner():
    """載入明碼憑證判準(單一住所＝augur.audit.plaintext_credential)。

    失敗一律 raise 給呼叫端 fail-closed——「找不到掃描器就放行」正是 pre-commit hook
    2026-08-03 修掉的那個洞(#6:不可逆操作不確定時擋下,不是略過)。
    路徑插入沿用 scripts/_bootstrap(#12 單一住所),故不需 PYTHONPATH、不需 pip install -e .。
    """
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.append(str(SCRIPTS_DIR))     # append:不遮蔽標準函式庫
    import _bootstrap  # noqa: F401  ── src/ 之 sys.path 插入住在這

    from augur.audit import plaintext_credential

    return plaintext_credential


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


def run_secret_scan(files: dict[str, Path]) -> tuple[int, list[str]]:
    """對「即將寫入快照的檔案集」跑明碼憑證掃描 → (rc, 訊息列)。rc≠0 即不得寫。

    fail-closed 四處:①掃描器載不進來 ②豁免清單格式壞 ③有未豁免命中 ④**掃描集≠寫入集**
    (掃 A 卻寫 B 之綠燈不成立;地板判準住 augur.audit.scan_floor)。
    """
    try:
        pc = load_scanner()
        findings, seen = pc.scan_files(files)
        allow, errors = pc.load_allowlist(pc.default_allowlist_path(REPO_ROOT))
        remaining, waived = pc.apply_allowlist(findings, allow)
        rc, msgs = pc.verdict(remaining, waived, seen, errors)
    except Exception as exc:      # noqa: BLE001 —— 掃描器壞掉/讀不到檔一律擋,不得放行
        return 3, [f"✗ 密碼掃描失敗({exc.__class__.__name__}: {exc})——**fail-closed**,"
                   "export 中止(不是略過)。",
                   "  修法:確認 src/augur/audit/plaintext_credential.py 與 scripts/_bootstrap.py "
                   "在且可 import、且活 memory 各檔可讀。"]
    unscanned = sorted(set(files) - set(seen))
    if unscanned:
        rc = 1
        msgs.append(f"✗ {len(unscanned)} 個檔在寫入集卻不在掃描集(掃 A 寫 B 不算掃過):"
                    f"{', '.join(unscanned[:8])}")
    return rc, msgs


def cmd_scan() -> int:
    """唯讀:只對活 memory 跑密碼掃描,不寫任何檔(export 前想先看結果時用)。"""
    live = live_memory_dir()
    lf = md_files(live)
    print(f"掃描對象:{live}({len(lf)} 檔)")
    rc, msgs = run_secret_scan(lf)
    for m in msgs:
        print(m, file=sys.stderr if rc else sys.stdout)
    return rc


def cmd_export() -> int:
    live = live_memory_dir()
    if not live.is_dir() or not md_files(live):
        print(f"✗ 活 memory 目錄無內容({live})——無可 export。", file=sys.stderr)
        return 1
    lf, sf = md_files(live), md_files(SNAPSHOT_DIR)
    # ── 密碼掃描先於任何寫入(#5/#6):紅則一個檔都不寫、也不 mkdir、不 unlink ──
    scan_rc, scan_msgs = run_secret_scan(lf)
    for m in scan_msgs:
        print(m, file=sys.stderr if scan_rc else sys.stdout)
    if scan_rc:
        print("✗ export 已中止——快照未被更動(handoff_memory/ 維持原狀)。", file=sys.stderr)
        return 2
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
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


def _selftest() -> int:
    """M-O3 回歸鎖：export 必須先掃密碼、無略過旗標、掃描器可載入（#35 先驗紅）。"""
    ok = True
    src = Path(__file__).read_text(encoding="utf-8")

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("export 調用 run_secret_scan", "run_secret_scan(lf)" in src and "cmd_export" in src)
    chk("掃紅則中止且不寫入", "export 已中止" in src and "快照未被更動" in src)
    # 掃 argparse 區（_selftest 之前）——斷言字串本身含針會假紅（#35）
    _arg_zone = src.split("def _selftest", 1)[0]
    chk("無略過旗標於 argparse／export 路徑",
        all(x not in _arg_zone for x in (
            "--skip-secret", "--skip-scan", "skip_secret", "force_export")))
    chk("判準住 plaintext_credential（#12）", "plaintext_credential" in src)
    try:
        pc = load_scanner()
        chk("掃描器可 import", hasattr(pc, "scan_files") and hasattr(pc, "verdict"))
        # 先驗紅：假檔含典型連線字串 ⇒ 必須報命中（否則掃什麼都綠＝假閘）
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "probe.md"
            p.write_text("DB_PASSWORD=SuperSecret123!\n", encoding="utf-8")
            findings, seen = pc.scan_files({"probe.md": p})
            chk("M-O3 紅：明碼樣板必命中", len(findings) >= 1 and "probe.md" in seen)
            clean = Path(td) / "clean.md"
            clean.write_text("# 無憑證之記憶片段\n", encoding="utf-8")
            f2, s2 = pc.scan_files({"clean.md": clean})
            chk("M-O3 綠：乾淨檔可零命中", len(f2) == 0 and "clean.md" in s2)
    except Exception as exc:  # noqa: BLE001
        chk(f"掃描器可 import（{exc}）", False)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude memory ⇄ repo 快照 傳輸器(零 Claude usage)")
    ap.add_argument("cmd", nargs="?", default="status",
                    choices=["status", "scan", "export", "restore"],
                    help="status(預設唯讀比對) / scan(唯讀密碼掃描) / export(活→repo,內含掃描) "
                         "/ restore(repo→活)")
    ap.add_argument("--force", action="store_true", help="restore 時強制覆蓋(仍先備份)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "scan":
        return cmd_scan()
    if args.cmd == "export":
        return cmd_export()
    return cmd_restore(args.force)


if __name__ == "__main__":
    sys.exit(main())
