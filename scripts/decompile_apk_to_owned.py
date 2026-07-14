#!/usr/bin/env python
"""件 A 類A·apk 反組譯 → owned_local 逐字入庫(薄 wrapper;R-A1;#3 不改 acquire_local_files/fileparse)。

🎯 這支在做什麼(白話):對**自有 app 之 apk**,用 jadx 反組譯(dalvik bytecode→java,規則式確定性、非 AI)→
   **分段邊界 allowlist 只留自有 package 前綴之 .java**(default-deny;排 androidx/com.google/kotlin 等第三方
   ——不以 owned_local 洗他人版權,對抗審查修正:分段邊界比對防 com.example 誤命中 com.example2)→ 交
   acquire_local_files 以 --source-type apk_decompile --license owned_local --access-scope local_private 入庫。

治權:owned_local=自有 app 碼(admin 誠信宣告自有前綴,同 --license 責任);第三方 lib default-deny 硬排除;
   jadx 反組譯確定性零 AI(#1)、逐字無摘要;抽不出誠實跳過(#15,fileparse)。⚠ jadx+JRE 為 OS 前置(#23、
   非 pip、GitHub release);入 HANDOFF #31 換機人工前置清單。source_key 須指向已 active 之本機源(admission 閘)。

守 #1· #3(最小邊界、複用既有引擎、不建第二入庫鏈 #12)· #5(apk 二進位不可信→subprocess timeout)· #15· #23· #29a/d。

執行指令矩陣:
  python scripts/decompile_apk_to_owned.py                                   # 無參數:印矩陣+已入 apk 統計
  python scripts/decompile_apk_to_owned.py --apk app.apk --list-packages    # 先看 package 樹(挑自有前綴)
  python scripts/decompile_apk_to_owned.py --apk app.apk --include-package com.myco --source-key local_files_apk --owner-user-id 1
  python scripts/decompile_apk_to_owned.py --apk app.apk --include-package com.myco --dry-run   # 只反組譯+濾、不入庫
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db

APK_SOURCE_TYPE = "apk_decompile"


def _check_jadx(jadx_bin):
    try:
        r = subprocess.run([jadx_bin, "--version"], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _run_jadx(apk, out_dir, jadx_bin, no_res):
    cmd = [jadx_bin, "-d", out_dir] + (["--no-res"] if no_res else []) + [apk]
    subprocess.run(cmd, capture_output=True, text=True, timeout=600)   # 確定性、二進位不可信→timeout(#5)
    return os.path.join(out_dir, "sources")


def _list_packages(sources_dir):
    counts = {}
    for dp, _, fns in os.walk(sources_dir):
        rel = os.path.relpath(dp, sources_dir)
        pkg = rel.replace(os.sep, ".")[:40] if rel != "." else "(root)"
        java = sum(1 for f in fns if f.endswith(".java"))
        if java:
            top2 = ".".join(pkg.split(".")[:2])
            counts[top2] = counts.get(top2, 0) + java
    print("package 前綴(top-2 層)× .java 檔數(挑自有前綴給 --include-package;排 androidx/com.google/kotlin 等第三方):")
    for p, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {p:40} {n}")


def _filter_allowlist(sources_dir, prefixes, staging):
    """default-deny:只複製 relpath 命中任一自有前綴(**分段邊界**)之 .java 真檔到 staging。回複製檔數。"""
    if not prefixes:
        sys.exit("--include-package 必填(default-deny;不指定自有前綴=拒,避免第三方版權碼混入 owned_local)")
    pref_paths = [p.replace(".", os.sep).rstrip(os.sep) + os.sep for p in prefixes]   # 'com.myco'→'com/myco/'
    n = 0
    for dp, _, fns in os.walk(sources_dir):
        for f in fns:
            if not f.endswith(".java"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), sources_dir)
            # 分段邊界比對(對抗審查):'com/myco/' 匹配 'com/myco/X.java',不誤中 'com/myco2/X.java'
            if not any(rel.startswith(pp) or rel == pp.rstrip(os.sep) + ".java" for pp in pref_paths):
                continue
            dest = os.path.join(staging, rel.replace(os.sep, "__"))   # 攤平避碰撞、保 .java 副檔名
            shutil.copy2(os.path.join(dp, f), dest)                    # 真檔複製(非 symlink;fileparse 跳 symlink)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--apk")
    ap.add_argument("--include-package", action="append", default=[], help="自有 package 前綴(可重複;default-deny)")
    ap.add_argument("--source-key", help="已 active 之本機源 key(admission 閘;apk 入庫掛此源)")
    ap.add_argument("--owner-user-id", type=int, default=None)
    ap.add_argument("--domain", default="local")
    ap.add_argument("--jadx-bin", default="jadx")
    ap.add_argument("--out-dir", default=None, help="反組譯落點(預設依 apk sha1 之穩定路徑,source_url 可溯源)")
    ap.add_argument("--list-packages", action="store_true")
    ap.add_argument("--keep-resources", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args, _ = ap.parse_known_args()

    if not args.apk:
        print(__doc__.split("執行指令矩陣:")[1])
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT count(DISTINCT item_id) FROM knowledge_item_text WHERE source_type=%s",
                        (APK_SOURCE_TYPE,))
            print(f"  已入 apk_decompile:{cur.fetchone()[0]} item")
        return 0
    if not os.path.isfile(args.apk):
        sys.exit(f"apk 不存在:{args.apk}")
    ver = _check_jadx(args.jadx_bin)
    if not ver:
        sys.exit(f"jadx 未裝或不可執行('{args.jadx_bin}')——OS 前置(#23):下載 skylot/jadx release 解壓、"
                 "bin/jadx 入 PATH(需 JRE);見 HANDOFF §3 換機人工前置。")
    print(f"jadx: {ver}")
    apk_sha1 = hashlib.sha1(open(args.apk, "rb").read()).hexdigest()[:16]
    out_dir = args.out_dir or os.path.join(os.path.expanduser("~"), ".augur_apk", apk_sha1)
    os.makedirs(out_dir, exist_ok=True)
    sources = _run_jadx(args.apk, out_dir, args.jadx_bin, not args.keep_resources)
    if not os.path.isdir(sources):
        sys.exit(f"jadx 反組譯無 sources 輸出({sources})——apk 可能加殼/損毀;誠實停(#15)")
    if args.list_packages:
        _list_packages(sources)
        return 0
    staging = os.path.join(out_dir, "_owned_staging")
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging, exist_ok=True)
    n = _filter_allowlist(sources, args.include_package, staging)
    print(f"allowlist 命中自有 .java:{n} 檔(前綴 {args.include_package};第三方 default-deny 排除)")
    if n == 0:
        sys.exit("0 檔命中自有前綴——確認 --include-package(先 --list-packages 看樹);混淆碼(ProGuard/R8)前綴可能失效須逐案確認")
    if args.dry_run:
        print(f"[dry-run] 已反組譯+濾至 {staging};未入庫。")
        return 0
    if not args.source_key:
        sys.exit("入庫須 --source-key(指向已 active 本機源;admission 閘)")
    # 交既有引擎入庫(#3/#12 複用;--acquire-only 不自鏈下游 C3)
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "acquire_local_files.py"),
           "--dir", staging, "--source-key", args.source_key, "--source-type", APK_SOURCE_TYPE,
           "--license", "owned_local", "--access-scope", "local_private", "--domain", args.domain,
           "--acquire-only"]
    if args.owner_user_id is not None:
        cmd += ["--owner-user-id", str(args.owner_user_id)]
    print("→ 交 acquire_local_files 入庫(owned_local/local_private/apk_decompile)…")
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
