"""索引儲存——唯讀存取層（SELECT only；連線以 mode=ro 開啟）。

讀寫分離之「讀」端：本模組僅查詢，不含任何寫入 SQL。所有建表/寫入隔離於
index.py（不被 server 匯入）。selftest 以 AST/文本掃描斷言本模組無寫入 SQL。

向量以 float32 bytes 存於 BLOB；此處解碼為 list[float]。
"""
from __future__ import annotations

import array
import math
import os
import sqlite3
from typing import Dict, List

from . import govern

DEFAULT_DB = str(govern.REPO / ".project_memory" / "index.db")


class MemoryStoreError(Exception):
    """儲存層錯誤——索引不存在/不可讀時發聲，不靜默回空。"""


def db_path(explicit: str | None = None) -> str:
    return explicit or os.getenv("MEMORY_DB") or DEFAULT_DB


def _connect(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        raise MemoryStoreError(
            f"索引不存在（{path}）：請先執行 `python3 -m tools.project_memory_mcp index` 建索引。"
        )
    try:
        abspath = os.path.abspath(path)
        conn = sqlite3.connect(f"file:{abspath}?mode=ro", uri=True)
    except sqlite3.OperationalError as exc:
        raise MemoryStoreError(f"索引不可讀（{path}）：{exc}") from exc
    conn.row_factory = sqlite3.Row
    return conn


def _decode_vec(blob: bytes) -> List[float]:
    a = array.array("f")
    a.frombytes(blob)
    return a.tolist()


def load_all(path: str) -> List[dict]:
    """載入全部 chunk（含解碼向量）。規模數千列，暴力載入即可。"""
    conn = _connect(path)
    try:
        rows = conn.execute(
            "SELECT id, path, start_line, end_line, text, summary, vector FROM chunks"
        ).fetchall()
    finally:
        conn.close()
    out: List[dict] = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "path": r["path"],
                "start_line": r["start_line"],
                "end_line": r["end_line"],
                "text": r["text"],
                "summary": r["summary"],
                "vector": _decode_vec(r["vector"]),
            }
        )
    return out


def counts(path: str) -> Dict[str, object]:
    conn = _connect(path)
    try:
        n_chunks = conn.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()["c"]
        n_files = conn.execute("SELECT COUNT(*) AS c FROM files").fetchone()["c"]
        meta = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM meta")}
    finally:
        conn.close()
    return {
        "files": n_files,
        "chunks": n_chunks,
        "embed_model": meta.get("embed_model", "?"),
        "built_at": meta.get("built_at", "?"),
    }


def file_hashes(path: str) -> Dict[str, dict]:
    """回 {相對路徑: {hash, mtime}}，供陳舊偵測。"""
    conn = _connect(path)
    try:
        rows = conn.execute("SELECT path, hash, mtime FROM files").fetchall()
    finally:
        conn.close()
    return {r["path"]: {"hash": r["hash"], "mtime": r["mtime"]} for r in rows}


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot / (na * nb)
