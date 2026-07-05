"""後台 SFTP 遠端瀏覽/取檔（admin 控制台，SSH 金鑰認證）— 遠端資料夾入知識庫之傳輸層。

🎯 這支在做什麼（白話）：讓 admin 用 SSH 金鑰連到遠端主機、瀏覽遠端目錄樹、把選定的遠端資料夾/檔
   下載到本地暫存夾，再交既有入庫引擎（acquire_local_files）逐字解析入知識層。**連線設定住 config**
   （~/.config/augur-sftp.json，chmod 600、不進 git）——只存 host/port/user/金鑰路徑（**私鑰不複製、只引用路徑；
   絕不存密碼**）。paramiko API 化操作（無 shell 注入）。
安全（#5）：SSH 金鑰認證（key_filename/ssh-agent）、config 0600、每檔大小上限、遞迴檔數上限（防超大樹）、
   host key 首次以 AutoAdd 信任（連自有主機之務實取捨，MITM 風險見 docstring）。入庫仍過 license DB CHECK。
守 #1（逐字入庫、可溯源）· #5（金鑰不外洩/大小上限）· #18（sftpbrowse=領域名詞）· #28（本地觸發零 Claude usage）。
"""
from __future__ import annotations

import json
import os
import posixpath
import stat

from augur.knowledge import fileparse, webupload

CONFIG = os.path.join(os.path.expanduser("~"), ".config", "augur-sftp.json")
MAX_TREE_FILES = 5000          # 單次下載遞迴檔數上限（防超大樹）
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


def _client(conn):
    import paramiko
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # 首次信任（連自有主機務實取捨；正式環境宜預置 known_hosts）
    kf = os.path.expanduser(conn["key_path"]) if conn.get("key_path") else None
    c.connect(conn["host"], port=int(conn.get("port", 22)), username=conn["user"],
              key_filename=kf, timeout=CONNECT_TIMEOUT, allow_agent=True, look_for_keys=True)
    return c


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

        def _walk(remote, local):
            if stats["saved"] >= MAX_TREE_FILES:
                stats["truncated"] = True
                return
            os.makedirs(local, exist_ok=True)
            for e in sftp.listdir_attr(remote):
                rp, lp = posixpath.join(remote, e.filename), os.path.join(local, e.filename)
                if stat.S_ISDIR(e.st_mode):
                    _walk(rp, lp)
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
