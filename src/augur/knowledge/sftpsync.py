"""SFTP 增量傳輸層(件 A2 headless)— 遞迴遠端樹、mtime/size 增量比對、只抓變更/新增、path-traversal 圍欄。

🎯 這支在做什麼(白話):給定 paramiko 連線 + 遠端根 + glob + 本地暫存夾 + 上輪帳本(prior_state),
   遞迴遠端樹逐檔:(a) glob 過濾 (b) 與 prior_state 比對 remote_mtime+size——**未變即不重抓(收斂 #6)**
   (c) 新增/變更 → 下載至暫存(path-traversal 圍欄 sftpbrowse._safe_local)→ 算 content_sha1 → yield;
   (d) oversize → yield change='skip'(local_path=None,供 CLI 記帳使下輪不重抓,對抗審查收斂修正)。
   **純傳輸、不碰 DB**(DB I/O 留給 scripts/acquire_remote_files.py);連線由呼叫端 open_client(strict=True) 開。

守 #6(增量冪等、未變不重抓)· #5(不碰憑證;path 圍欄防惡意 server tar-slip)· #18(領域名詞)· #28(本地零 usage)·
   #24(不高併發;單連線循序)。
"""
from __future__ import annotations

import fnmatch
import hashlib
import os
import posixpath
import stat
from dataclasses import dataclass

from augur.knowledge import fileparse, sftpbrowse


@dataclass
class SyncedFile:
    remote_host: str
    remote_path: str
    remote_mtime: int
    size_bytes: int
    content_sha1: str | None      # 下載檔內容 sha1(skip/oversize 時 None)
    local_path: str | None        # 下載落點(skip/oversize/dry 時 None)
    change: str                   # 'new' | 'changed' | 'skip'(oversize/不可抓)


def iter_changed_files(client, remote_host, base_path, glob_pat, dest_dir, prior_state, *,
                       download=True, max_files=5000, max_bytes=None):
    """遞迴遠端樹 → yield 新增/變更/skip 之 SyncedFile(未變者不 yield=收斂)。
    prior_state:{remote_path:(mtime,size)}(CLI 由 sftp_sync_state 預載);glob_pat:fnmatch basename(None=全收)。
    max_files:單輪檢視上限(#25/防超大樹);已在 prior_state 且未變者**不計入額度**(對抗審查:否則不可抓檔佔滿額度→死循環)。"""
    max_bytes = max_bytes or fileparse.MAX_BYTES
    sftp = client.open_sftp()
    root = sftp.normalize(base_path or ".")
    budget = {"n": 0}

    def walk(remote):
        if budget["n"] >= max_files:
            return
        for e in sftp.listdir_attr(remote):
            rp = posixpath.join(remote, e.filename)
            if stat.S_ISDIR(e.st_mode):
                yield from walk(rp)
                continue
            if not stat.S_ISREG(e.st_mode):
                continue
            if glob_pat and not fnmatch.fnmatch(e.filename, glob_pat):
                continue
            mtime, size = int(e.st_mtime or 0), int(e.st_size or 0)
            prev = prior_state.get(rp)
            if prev and int(prev[0]) == mtime and int(prev[1]) == size:
                continue                              # 未變:不重抓、不佔額度(收斂 #6)
            if budget["n"] >= max_files:
                return
            budget["n"] += 1
            change = "changed" if prev else "new"
            if size > max_bytes:                       # oversize:記帳(skip)不下載,下輪未變即不再 yield(收斂)
                yield SyncedFile(remote_host, rp, mtime, size, None, None, "skip")
                continue
            if _safe_local(dest_dir, e.filename) is None:   # path-traversal 圍欄(惡意 server basename)
                yield SyncedFile(remote_host, rp, mtime, size, None, None, "skip")
                continue
            if not download:                           # dry-run:只列不抓
                yield SyncedFile(remote_host, rp, mtime, size, None, None, change)
                continue
            lp = os.path.join(dest_dir, f"{budget['n']}_{e.filename}")   # 計數前綴防 basename 碰撞;副檔名保留供 fileparse
            os.makedirs(dest_dir, exist_ok=True)
            sftp.get(rp, lp)
            with open(lp, "rb") as fh:
                sha1 = hashlib.sha1(fh.read()).hexdigest()
            yield SyncedFile(remote_host, rp, mtime, size, sha1, lp, change)

    yield from walk(root)


_safe_local = sftpbrowse._safe_local   # 圍欄復用單一住所(#12)
