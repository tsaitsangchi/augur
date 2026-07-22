"""索引儲存——唯讀存取層（SELECT only；連線以 mode=ro 開啟）。

讀寫分離之「讀」端：本模組僅查詢，不含任何寫入 SQL。所有建表/寫入隔離於
index.py（不被 server 匯入）。selftest 以 AST/文本掃描斷言本模組無寫入 SQL。

向量以 float32 bytes 存於 BLOB；此處解碼為 list[float]。
"""
from __future__ import annotations

import array
import math
import os
import re
import sqlite3
from typing import Dict, List, Optional, Tuple

from . import govern

DEFAULT_DB = str(govern.REPO / ".project_memory" / "index.db")

# FTS5 查詢用：英數／底線／CJK 連續字元
_FTS_TOKEN = re.compile(r"[A-Za-z0-9_\u4e00-\u9fff]+")


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


# 行程內 load_all 快取（多跳 research／連續 recall 免重解碼 ~9k 向量）
_load_all_cache: Dict[tuple, List[dict]] = {}
_cache_stats = {"hits": 0, "misses": 0}


def clear_cache() -> None:
    """清空 load_all 快取（selftest／重建索引後可呼叫）。"""
    _load_all_cache.clear()
    _cache_stats["hits"] = 0
    _cache_stats["misses"] = 0


def cache_stats() -> Dict[str, int]:
    return dict(_cache_stats)


def _db_fingerprint(path: str) -> tuple:
    abspath = os.path.abspath(path)
    st = os.stat(abspath)
    return (abspath, int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))), int(st.st_size))


def has_fts(path: str) -> bool:
    """索引是否含 FTS5 表（中期強化後必備；舊索引需重建）。"""
    conn = _connect(path)
    try:
        row = conn.execute(
            "SELECT 1 AS ok FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def require_fts(path: str) -> None:
    if not has_fts(path):
        raise MemoryStoreError(
            f"索引缺 FTS5（chunks_fts @ {path}）：請重建 "
            "`python3 -m tools.project_memory_mcp index`（不靜默退回純語意）。"
        )


def load_all(path: str) -> List[dict]:
    """載入全部 chunk（含解碼向量）。行程內依 (abspath,mtime,size) 快取。"""
    key = _db_fingerprint(path)
    cached = _load_all_cache.get(key)
    if cached is not None:
        _cache_stats["hits"] += 1
        return cached

    _cache_stats["misses"] += 1
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
    _load_all_cache[key] = out
    # 同 abspath 舊 fingerprint 清掉，避免重建後殘留多份
    stale_keys = [k for k in _load_all_cache if k[0] == key[0] and k != key]
    for k in stale_keys:
        del _load_all_cache[k]
    return out


def load_by_ids(path: str, ids: List[int]) -> Dict[int, dict]:
    """依 id 批次載入 chunk（含向量）。"""
    if not ids:
        return {}
    conn = _connect(path)
    try:
        # 僅允許整數 id，防注入
        clean = [int(i) for i in ids]
        placeholders = ",".join("?" * len(clean))
        rows = conn.execute(
            f"SELECT id, path, start_line, end_line, text, summary, vector FROM chunks "
            f"WHERE id IN ({placeholders})",
            clean,
        ).fetchall()
    finally:
        conn.close()
    out: Dict[int, dict] = {}
    for r in rows:
        out[int(r["id"])] = {
            "id": r["id"],
            "path": r["path"],
            "start_line": r["start_line"],
            "end_line": r["end_line"],
            "text": r["text"],
            "summary": r["summary"],
            "vector": _decode_vec(r["vector"]),
        }
    return out


def fts_query_from_text(query: str) -> Optional[str]:
    """把自然語言轉成安全的 FTS5 MATCH 字串（token OR）；無可用 token 回 None。"""
    if not isinstance(query, str) or not query.strip():
        return None
    tokens: List[str] = []
    for raw in _FTS_TOKEN.findall(query):
        t = raw.strip()
        if len(t) < 2:
            continue
        # 雙引號包住，並去掉內部雙引號，避免 MATCH 語法注入
        safe = t.replace('"', "")
        if len(safe) < 2:
            continue
        tokens.append(f'"{safe}"')
        if len(tokens) >= 12:
            break
    if not tokens:
        return None
    return " OR ".join(tokens)


def fts_search(path: str, query: str, limit: int = 30) -> List[Tuple[int, float]]:
    """FTS5 關鍵字搜尋。回 [(chunk_id, bm25_rank_score)]，分數愈高愈相關。

    SQLite bm25() 愈小愈好；此處轉成 -bm25 以便與「愈高愈好」一致。
    """
    require_fts(path)
    match = fts_query_from_text(query)
    if not match:
        return []
    try:
        lim = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        lim = 30

    conn = _connect(path)
    try:
        rows = conn.execute(
            "SELECT rowid AS id, bm25(chunks_fts) AS rank "
            "FROM chunks_fts WHERE chunks_fts MATCH ? "
            "ORDER BY rank LIMIT ?",
            (match, lim),
        ).fetchall()
    except sqlite3.OperationalError as exc:
        raise MemoryStoreError(f"FTS5 查詢失敗：{exc}") from exc
    finally:
        conn.close()

    out: List[Tuple[int, float]] = []
    for r in rows:
        # bm25 愈小愈好 → 取負值當「相關分」
        out.append((int(r["id"]), float(-r["rank"])))
    return out


def counts(path: str) -> Dict[str, object]:
    conn = _connect(path)
    try:
        n_chunks = conn.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()["c"]
        n_files = conn.execute("SELECT COUNT(*) AS c FROM files").fetchone()["c"]
        meta = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM meta")}
        has = conn.execute(
            "SELECT 1 AS ok FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
        ).fetchone()
    finally:
        conn.close()
    return {
        "files": n_files,
        "chunks": n_chunks,
        "embed_model": meta.get("embed_model", "?"),
        "built_at": meta.get("built_at", "?"),
        "search_schema": meta.get("search_schema", "legacy" if not has else "fts5?"),
        "has_fts": bool(has),
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
