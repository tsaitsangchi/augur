"""建索引（admin CLI 寫入端）——讀寫分離之「寫」端，唯一含寫入 SQL 之模組。

刻意不暴露為 MCP 工具、且不被 server.py 匯入：agent 無法經 MCP 觸發寫入。
預設增量（檔案 SHA256）；`--full` 刪 DB 全量重建。
"""
from __future__ import annotations

import argparse
import array
import hashlib
import os
import pathlib
import sqlite3
import sys
import time
from typing import Dict, List, Optional, Tuple

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
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    path,
    text,
    content='chunks',
    content_rowid='id'
);
"""


def _file_sha(abspath: str) -> str:
    h = hashlib.sha256()
    with open(abspath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if "pyvenv.cfg" in filenames:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in govern._EXCLUDE_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def _has_fts_table(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 AS ok FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
    ).fetchone()
    return row is not None


def _meta_get(conn: sqlite3.Connection, key: str) -> Optional[str]:
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def _delete_path(conn: sqlite3.Connection, rel: str) -> int:
    """刪除某 path 的 chunks + FTS + files 列。回刪除的 chunk 數。

    FTS5 external-content：刪除前須對 FTS 下 delete（含舊欄位值），再刪 content 表。
    """
    rows = conn.execute(
        "SELECT id, path, text FROM chunks WHERE path=?", (rel,)
    ).fetchall()
    for cid, path, text in rows:
        conn.execute(
            "INSERT INTO chunks_fts(chunks_fts, rowid, path, text) VALUES('delete', ?, ?, ?)",
            (int(cid), path, text),
        )
    conn.execute("DELETE FROM chunks WHERE path=?", (rel,))
    conn.execute("DELETE FROM files WHERE path=?", (rel,))
    return len(rows)


def _load_file_hashes(conn: sqlite3.Connection) -> Dict[str, str]:
    return {
        r[0]: r[1]
        for r in conn.execute("SELECT path, hash FROM files").fetchall()
    }


def _flush_pending(
    conn: sqlite3.Connection,
    pending_text: List[str],
    pending_meta: List[Tuple],
) -> int:
    """寫入 pending chunks；回新增 chunk 數。"""
    if not pending_text:
        return 0
    n = 0
    vectors = embed.embed(pending_text)
    for (rel, s, e, chash, text, mt), vec in zip(pending_meta, vectors):
        blob = array.array("f", vec).tobytes()
        cur = conn.execute(
            "INSERT INTO chunks(path,start_line,end_line,hash,text,summary,vector,dim,model,mtime)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (rel, s, e, chash, text, None, blob, len(vec), embed.embed_model(), mt),
        )
        conn.execute(
            "INSERT INTO chunks_fts(rowid, path, text) VALUES (?,?,?)",
            (cur.lastrowid, rel, text),
        )
        n += 1
    pending_text.clear()
    pending_meta.clear()
    return n


def _index_one_file(
    conn: sqlite3.Connection,
    rel: str,
    text: str,
    fhash: str,
    mt: float,
    batch: int,
    pending_text: List[str],
    pending_meta: List[Tuple],
) -> int:
    """將單檔切塊加入 pending，必要時 flush；回本檔 chunk 數（切塊數）。"""
    pieces = chunk.chunk_text(text)
    for (s, e, body) in pieces:
        chash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        pending_text.append(body)
        pending_meta.append((rel, s, e, chash, body, mt))
        if len(pending_text) >= batch:
            _flush_pending(conn, pending_text, pending_meta)
    conn.execute(
        "INSERT OR REPLACE INTO files(path,hash,mtime,chunk_count) VALUES(?,?,?,?)",
        (rel, fhash, mt, len(pieces)),
    )
    return len(pieces)


def _write_meta(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('embed_model',?)",
        (embed.embed_model(),),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('built_at',?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S%z"),),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('search_schema',?)",
        ("fts5-v1",),
    )


def _should_full(
    db_file: str,
    full: bool,
    log,
) -> bool:
    if full:
        return True
    if not os.path.exists(db_file):
        log("[project-memory] 無既有索引 → 全量建庫")
        return True
    try:
        conn = sqlite3.connect(db_file)
        try:
            if not _has_fts_table(conn):
                log("[project-memory] 缺 chunks_fts → 強制全量")
                return True
            stored_model = _meta_get(conn, "embed_model")
            current = embed.embed_model()
            if stored_model and stored_model != current:
                log(
                    f"[project-memory] embed_model 變更（{stored_model} → {current}）→ 強制全量"
                )
                return True
        finally:
            conn.close()
    except sqlite3.Error as exc:
        log(f"[project-memory] 既有 DB 不可讀（{exc}）→ 強制全量")
        return True
    return False


def _build_full(
    root_path: pathlib.Path,
    db_file: str,
    batch: int,
    log,
) -> dict:
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    n_files = 0
    n_chunks = 0
    pending_text: List[str] = []
    pending_meta: List[Tuple] = []
    try:
        _ensure_schema(conn)
        log(f"[project-memory] 全量掃描 {root_path}（embed={embed.embed_model()}）…")
        for abspath in _iter_files(root_path):
            resolved = pathlib.Path(abspath).resolve()
            if not govern.should_index(resolved, root=root_path):
                continue
            try:
                text = resolved.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(resolved.relative_to(root_path))
            log(f"[project-memory] ({n_files + 1}) 索引 {rel} …")
            fhash = _file_sha(abspath)
            mt = os.path.getmtime(abspath)
            n_pieces = _index_one_file(
                conn, rel, text, fhash, mt, batch, pending_text, pending_meta
            )
            n_files += 1
            # chunk 計數在 flush 後才準；先累切塊數於 files；最終用 COUNT
            _ = n_pieces
        n_chunks += _flush_pending(conn, pending_text, pending_meta)
        # 補上未計入 flush 前的：以 DB COUNT 為準
        n_chunks = int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        _write_meta(conn)
        conn.commit()
    finally:
        conn.close()

    store.clear_cache()
    return {
        "mode": "full",
        "files": n_files,
        "chunks": n_chunks,
        "added": n_files,
        "updated": 0,
        "removed": 0,
        "skipped": 0,
        "db": db_file,
        "embed_model": embed.embed_model(),
    }


def _build_incremental(
    root_path: pathlib.Path,
    db_file: str,
    batch: int,
    log,
) -> dict:
    conn = sqlite3.connect(db_file)
    added = updated = removed = skipped = 0
    pending_text: List[str] = []
    pending_meta: List[Tuple] = []
    seen: set = set()
    try:
        _ensure_schema(conn)
        if not _has_fts_table(conn):
            raise RuntimeError("incremental 需要 chunks_fts")
        old_hashes = _load_file_hashes(conn)
        log(
            f"[project-memory] 增量掃描 {root_path} "
            f"（既有 {len(old_hashes)} 檔，embed={embed.embed_model()}）…"
        )

        for abspath in _iter_files(root_path):
            resolved = pathlib.Path(abspath).resolve()
            if not govern.should_index(resolved, root=root_path):
                continue
            try:
                text = resolved.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(resolved.relative_to(root_path))
            seen.add(rel)
            fhash = _file_sha(abspath)
            mt = os.path.getmtime(abspath)
            prev = old_hashes.get(rel)
            if prev == fhash:
                skipped += 1
                continue

            # 每檔提交一次，避免長鎖；不用顯式 BEGIN（與 sqlite3 隱式交易衝突易毀庫）
            try:
                is_new = prev is None
                if not is_new:
                    _delete_path(conn, rel)
                _index_one_file(
                    conn, rel, text, fhash, mt, batch, pending_text, pending_meta
                )
                _flush_pending(conn, pending_text, pending_meta)
                conn.commit()
                if is_new:
                    log(f"[project-memory] + 新增 {rel}")
                    added += 1
                else:
                    log(f"[project-memory] ~ 更新 {rel}")
                    updated += 1
            except Exception:
                conn.rollback()
                pending_text.clear()
                pending_meta.clear()
                raise

        # 刪除：DB 有、本次未見
        for rel in list(old_hashes.keys()):
            if rel in seen:
                continue
            try:
                _delete_path(conn, rel)
                conn.commit()
                log(f"[project-memory] - 移除 {rel}")
                removed += 1
            except Exception:
                conn.rollback()
                raise

        _flush_pending(conn, pending_text, pending_meta)
        n_files = int(conn.execute("SELECT COUNT(*) FROM files").fetchone()[0])
        n_chunks = int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        _write_meta(conn)
        conn.commit()
    finally:
        conn.close()

    store.clear_cache()
    return {
        "mode": "incremental",
        "files": n_files,
        "chunks": n_chunks,
        "added": added,
        "updated": updated,
        "removed": removed,
        "skipped": skipped,
        "db": db_file,
        "embed_model": embed.embed_model(),
    }


def build(
    root: Optional[str] = None,
    db: Optional[str] = None,
    batch: int = 32,
    verbose: bool = False,
    full: bool = False,
) -> dict:
    """建索引。預設增量；full=True 或無可用 DB／embed 變更時全量。"""

    def _log(msg: str) -> None:
        if verbose:
            print(msg, file=sys.stderr, flush=True)

    root_path = pathlib.Path(root).resolve() if root else govern.REPO
    db_file = store.db_path(db)
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)

    if _should_full(db_file, full, _log):
        return _build_full(root_path, db_file, batch, _log)
    return _build_incremental(root_path, db_file, batch, _log)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="project-memory 建索引（預設增量）")
    p.add_argument(
        "--full",
        action="store_true",
        help="刪除既有 DB 後全量重建",
    )
    p.add_argument("--db", default=None, help="索引 DB 路徑（預設 MEMORY_DB／.project_memory）")
    p.add_argument("--root", default=None, help="掃描根目錄（預設 repo 根）")
    p.add_argument("--batch", type=int, default=32, help="嵌入 batch 大小")
    args = p.parse_args(argv)

    stats = build(
        root=args.root,
        db=args.db,
        batch=args.batch,
        verbose=True,
        full=args.full,
    )
    print(
        f"project-memory index [{stats['mode']}]: "
        f"{stats['files']} 檔 / {stats['chunks']} chunk "
        f"（+{stats['added']} ~{stats['updated']} -{stats['removed']} "
        f"skip={stats['skipped']}）"
        f" → {stats['db']}（embed={stats['embed_model']}）"
    )
    return 0
