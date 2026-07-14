"""後台 SFTP 遠端瀏覽/取檔（admin 控制台，SSH 金鑰認證）— 遠端資料夾入知識庫之傳輸層。

🎯 這支在做什麼（白話）：讓 admin 用 SSH 金鑰連到遠端主機、瀏覽遠端目錄樹、把選定的遠端資料夾/檔
   下載到本地暫存夾，再交既有入庫引擎（acquire_local_files）逐字解析入知識層。**連線設定住 config**
   （~/.config/augur-sftp.json，chmod 600、不進 git）——只存 host/port/user/金鑰路徑（**私鑰不複製、只引用路徑；
   絕不存密碼**）。paramiko API 化操作（無 shell 注入）。
安全（#5）：SSH 金鑰認證（key_filename/ssh-agent）、config 0600、每檔大小上限、遞迴檔數上限（防超大樹）、
   host key 首次以 AutoAdd 信任（連自有主機之務實取捨，MITM 風險見 docstring）。入庫仍過 license DB CHECK。
守 #1（逐字入庫、可溯源）· #5（金鑰不外洩/大小上限）· #18（sftpbrowse=領域名詞）· #28（本地觸發零 Claude usage）。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.sftpbrowse              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.sftpbrowse --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import json
import os
import posixpath
import stat

from augur.knowledge import fileparse, webupload

CONFIG = os.path.join(os.path.expanduser("~"), ".config", "augur-sftp.json")
MAX_TREE_FILES = 5000          # 單次下載遞迴檔數上限（防超大樹）
MAX_TREE_DEPTH = 40            # 目錄下降深度上限（R6:防惡意 server 純目錄無限遞迴撞 RecursionError）
CONNECT_TIMEOUT = 15


def load_config():
    try:
        with open(CONFIG) as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {"connections": []}
    except (OSError, ValueError):
        return {"connections": []}


def connection_names():
    return [c.get("name") for c in load_config().get("connections", []) if c.get("name")]


def _find(name):
    for c in load_config().get("connections", []):
        if c.get("name") == name:
            return c
    return None


def save_connection(name, host, port, user, key_path):
    """新增/更新一筆連線設定（只存非機密：host/user/金鑰路徑）；config 強制 0600。回連線名清單。"""
    name = (name or "").strip()
    if not (name and host and user):
        raise ValueError("name/host/user 必填")
    cfg = load_config()
    conns = [c for c in cfg.get("connections", []) if c.get("name") != name]
    conns.append({"name": name, "host": host.strip(), "port": int(port or 22),
                  "user": user.strip(), "key_path": (key_path or "").strip()})
    cfg["connections"] = conns
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    fd = os.open(CONFIG, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.chmod(CONFIG, 0o600)
    return [c["name"] for c in conns]


def open_client(conn, *, strict=False):
    """開 paramiko SSH 連線。strict=True(headless/timer;件 A2):**RejectPolicy + known_hosts pinning + 關
    agent/look_for_keys**(只用顯式 key_path)——防 MITM 靜默信任與金鑰枚舉(對抗審查 #5;無人看顧通道尤須);
    strict=False(admin 互動、人看顧):沿用 AutoAdd 務實取捨(既有行為不變)。"""
    import paramiko
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    kf = os.path.expanduser(conn["key_path"]) if conn.get("key_path") else None
    c.set_missing_host_key_policy(paramiko.RejectPolicy() if strict else paramiko.AutoAddPolicy())
    c.connect(conn["host"], port=int(conn.get("port", 22)), username=conn["user"], key_filename=kf,
              timeout=CONNECT_TIMEOUT,
              allow_agent=(not strict), look_for_keys=(not strict))
    return c


_client = open_client   # 別名:既有 list_dir/download_tree 呼叫不破(#12;預設 strict=False=原行為)


def _safe_local(base, name):
    """防 tar-slip path traversal(對抗審查 blocker):遠端回傳之 filename 不得含分隔/`..`/絕對路徑,
    且組出之 local path 須在 base 內。回安全 local path;越界回 None(呼叫端 skip 計數)。"""
    if not name or name in (".", "..") or "/" in name or "\\" in name or os.path.isabs(name):
        return None
    lp = os.path.join(base, name)
    base_r = os.path.abspath(base)
    if os.path.commonpath([base_r, os.path.abspath(lp)]) != base_r:
        return None
    return lp


def list_dir(conn_name, path="."):
    """瀏覽遠端一層目錄。回 {ok, path, parent, dirs[], file_count, samples[]}；失敗誠實回 {ok:False,error}。"""
    conn = _find(conn_name)
    if not conn:
        return {"ok": False, "error": f"連線設定「{conn_name}」不存在（先新增連線）"}
    try:
        c = _client(conn)
        try:
            sftp = c.open_sftp()
            p = sftp.normalize(path or ".")
            dirs, files, samples = [], 0, []
            for e in sftp.listdir_attr(p):
                if stat.S_ISDIR(e.st_mode):
                    dirs.append({"name": e.filename, "path": posixpath.join(p, e.filename)})
                elif stat.S_ISREG(e.st_mode):
                    files += 1
                    if len(samples) < 8:
                        samples.append(e.filename)
            dirs.sort(key=lambda d: d["name"].lower())
            parent = posixpath.dirname(p.rstrip("/")) or "/"
            return {"ok": True, "path": p, "parent": (parent if parent != p else None),
                    "dirs": dirs, "file_count": files, "samples": samples}
        finally:
            c.close()
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def download_tree(conn_name, path, dest_dir):
    """把遠端 path（資料夾遞迴或單檔）下載到本地 dest_dir。回 {saved, bytes, skipped_big, truncated}。"""
    conn = _find(conn_name)
    if not conn:
        raise ValueError(f"連線設定「{conn_name}」不存在")
    c = _client(conn)
    stats = {"saved": 0, "bytes": 0, "skipped_big": 0, "truncated": False}
    try:
        sftp = c.open_sftp()
        p = sftp.normalize(path or ".")
        st = sftp.stat(p)

        def _walk(remote, local, depth=0):
            # R6:深度上限——防惡意 server 純目錄無限遞迴(檔額度不涵蓋純目錄樹)撞 RecursionError
            if stats["saved"] >= MAX_TREE_FILES or depth > MAX_TREE_DEPTH:
                stats["truncated"] = True
                return
            os.makedirs(local, exist_ok=True)
            for e in sftp.listdir_attr(remote):
                lp = _safe_local(local, e.filename)       # 對抗審查:遠端 filename path-traversal 圍欄(惡意 server)
                if lp is None:
                    stats["skipped_big"] = stats.get("skipped_big", 0)   # 保欄位
                    stats["skipped_unsafe"] = stats.get("skipped_unsafe", 0) + 1
                    continue
                rp = posixpath.join(remote, e.filename)
                if stat.S_ISDIR(e.st_mode):
                    _walk(rp, lp, depth + 1)
                elif stat.S_ISREG(e.st_mode):
                    if stats["saved"] >= MAX_TREE_FILES:
                        stats["truncated"] = True
                        return
                    if (e.st_size or 0) > fileparse.MAX_BYTES:
                        stats["skipped_big"] += 1
                        continue
                    sftp.get(rp, lp)
                    stats["saved"] += 1
                    stats["bytes"] += e.st_size or 0

        if stat.S_ISDIR(st.st_mode):
            _walk(p, dest_dir)
        else:
            if (st.st_size or 0) > fileparse.MAX_BYTES:
                stats["skipped_big"] += 1
            else:
                os.makedirs(dest_dir, exist_ok=True)
                sftp.get(p, os.path.join(dest_dir, posixpath.basename(p)))
                stats["saved"], stats["bytes"] = 1, st.st_size or 0
        return stats
    finally:
        c.close()


def fetch_to_upload(conn_name, path):
    """下載遠端 path 到 webupload 暫存夾（供 acquire_local_files 入庫）。回 (updir, stats)。"""
    import secrets
    updir = os.path.join(webupload.UPLOAD_ROOT, "sftp_" + secrets.token_hex(6))
    stats = download_tree(conn_name, path, updir)
    return updir, stats


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # _safe_local path-traversal 圍欄（純字串/路徑運算、零 IO；固化對抗審查 blocker 不變式）
    base = "/tmp/aug_selftest_base"
    chk("正常檔名回 base 內路徑", _safe_local(base, "a.txt") == os.path.join(base, "a.txt"))
    chk("`..` 拒（回 None）", _safe_local(base, "..") is None)
    chk("`.` 拒", _safe_local(base, ".") is None)
    chk("含 / 拒", _safe_local(base, "a/b") is None)
    chk("含反斜線拒", _safe_local(base, "a\\b") is None)
    chk("絕對路徑拒", _safe_local(base, "/etc/passwd") is None)
    chk("空名拒", _safe_local(base, "") is None)
    # 常數合理性
    chk("MAX_TREE_FILES>0", MAX_TREE_FILES > 0)
    chk("MAX_TREE_DEPTH>0", MAX_TREE_DEPTH > 0)
    chk("CONNECT_TIMEOUT>0", CONNECT_TIMEOUT > 0)
    # import-smoke：公開入口皆在（IO-bound 部分不觸網/DB，僅結構斷言）
    import sys
    mod = sys.modules[__name__]
    for n in ("load_config", "connection_names", "save_connection", "open_client",
              "list_dir", "download_tree", "fetch_to_upload"):
        chk(f"公開入口 {n} 存在", hasattr(mod, n) and callable(getattr(mod, n)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.sftpbrowse --selftest;免 DB 免 API)")
