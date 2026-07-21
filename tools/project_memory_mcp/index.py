"""建索引（admin CLI 寫入端）——讀寫分離之「寫」端，唯一含寫入 SQL 之模組。

刻意不暴露為 MCP 工具、且不被 server.py 匯入：agent 無法經 MCP 觸發寫入。
走訪 root 內非治理輔助語料 → 切塊 → 嵌入 → 寫 SQLite。
"""
from __future__ import annotations

import array
import hashlib
import os
import sqlite3
import sys
import time
from typing import Optional

from . import chunk, embed, govern, store

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    hash TEXT NOT NULL,
    text TEXT NOT NULL,
    summary TEXT,
    vector BLOB NOT NULL,
    dim INTEGER NOT NULL,
    model TEXT NOT NULL,
    mtime REAL
);
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    hash TEXT NOT NULL,
    mtime REAL,
    chunk_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE INDEX IF NOT EXISTS idx_chunks_path ON chunks(path);
"""


def _file_sha(abspath: str) -> str:
    h = hashlib.sha256()
    with open(abspath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # 通用 venv 偵測：含 pyvenv.cfg 之目錄為虛擬環境根，整枝剪除（不論其命名）
        if "pyvenv.cfg" in filenames:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in govern._EXCLUDE_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def build(root: Optional[str] = None, db: Optional[str] = None, batch: int = 32,
          verbose: bool = False) -> dict:
    """建/重建索引。回統計 dict。verbose=True 時印逐檔進度到 stderr。"""
    import pathlib

    def _log(msg: str) -> None:
        if verbose:
            print(msg, file=sys.stderr, flush=True)

    root_path = pathlib.Path(root).resolve() if root else govern.REPO
    db_file = store.db_path(db)
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)

    # 全量重建：刪舊 DB 檔，確保無殘留
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    try:
        conn.executescript(_SCHEMA)

        pending_text = []
        pending_meta = []  # (path_rel, start, end, chunk_hash, text, mtime)
        n_files = 0
        n_chunks = 0

        def flush_batch():
            nonlocal n_chunks
            if not pending_text:
                return
            vectors = embed.embed(pending_text)
            for (rel, s, e, chash, text, mt), vec in zip(pending_meta, vectors):
                blob = array.array("f", vec).tobytes()
                conn.execute(
                    "INSERT INTO chunks(path,start_line,end_line,hash,text,summary,vector,dim,model,mtime)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (rel, s, e, chash, text, None, blob, len(vec), embed.embed_model(), mt),
                )
                n_chunks += 1
            pending_text.clear()
            pending_meta.clear()

        _log(f"[project-memory] 掃描 {root_path}（embed={embed.embed_model()}）…")
        for abspath in _iter_files(root_path):
            resolved = pathlib.Path(abspath).resolve()
            if not govern.should_index(resolved, root=root_path):
                continue
            try:
                text = resolved.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(resolved.relative_to(root_path))
            _log(f"[project-memory] ({n_files + 1}) 索引 {rel} …")
            fhash = _file_sha(abspath)
            mt = os.path.getmtime(abspath)
            pieces = chunk.chunk_text(text)
            for (s, e, body) in pieces:
                chash = hashlib.sha256(body.encode("utf-8")).hexdigest()
                pending_text.append(body)
                pending_meta.append((rel, s, e, chash, body, mt))
                if len(pending_text) >= batch:
                    flush_batch()
            conn.execute(
                "INSERT OR REPLACE INTO files(path,hash,mtime,chunk_count) VALUES(?,?,?,?)",
                (rel, fhash, mt, len(pieces)),
            )
            n_files += 1

        flush_batch()
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('embed_model',?)", (embed.embed_model(),))
        conn.execute(
            "INSERT OR REPLACE INTO meta(key,value) VALUES('built_at',?)",
            (time.strftime("%Y-%m-%dT%H:%M:%S%z"),),
        )
        conn.commit()
    finally:
        conn.close()

    return {"files": n_files, "chunks": n_chunks, "db": db_file, "embed_model": embed.embed_model()}


def main(argv=None) -> int:
    stats = build(verbose=True)
    print(
        f"project-memory index: {stats['files']} 檔 / {stats['chunks']} chunk "
        f"→ {stats['db']}（embed={stats['embed_model']}）"
    )
    return 0
