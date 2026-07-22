"""recall / memory_status —— MCP 唯讀工具邏輯。

僅匯入唯讀模組（store/embed/govern）；不匯入 index（寫入端）。
治理防線（縱深）：即便索引誤含治理片段，recall 於回傳前再過濾一次。

中期強化：hybrid（語意 + FTS5 RRF）、結構化 recall_hits() 供 local_research。
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
from typing import Dict, List, Optional, Tuple

from . import embed, govern, store

_II_NOTE = "⚠ [I] 輔助片段；治理原文請經 constitution-mcp。"

_VALID_MODES = ("hybrid", "semantic", "keyword")
_RRF_K = 60
_EXPAND_TOKEN = re.compile(r"[A-Za-z0-9_\u4e00-\u9fff]{2,}")


class RecallError(Exception):
    """recall 層錯誤——經協定層帶 isError，不靜默回空/近似。"""


def _file_sha(abspath: str) -> str:
    h = hashlib.sha256()
    with open(abspath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _pass_filters(row: dict, scope: Optional[str]) -> bool:
    if govern.is_governance_path(govern.REPO / row["path"]):
        return False
    if scope and not row["path"].startswith(scope):
        return False
    return True


def _rrf_fuse(
    semantic_ids: List[int], keyword_ids: List[int], rrf_k: int = _RRF_K
) -> List[Tuple[int, float]]:
    """Reciprocal Rank Fusion。回 [(id, rrf_score)] 降序。"""
    scores: Dict[int, float] = {}
    for rank, cid in enumerate(semantic_ids):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank + 1)
    for rank, cid in enumerate(keyword_ids):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank + 1)
    return sorted(scores.items(), key=lambda t: t[1], reverse=True)


def expand_query_from_hits(query: str, hits: List[dict], max_extra: int = 8) -> str:
    """從命中片段抽 path basename／關鍵 token，擴充下一跳 query。"""
    seen = set()
    extras: List[str] = []
    for h in hits:
        base = pathlib.Path(h.get("path", "")).stem
        for tok in _EXPAND_TOKEN.findall(base):
            low = tok.lower()
            if low not in seen and len(tok) >= 2:
                seen.add(low)
                extras.append(tok)
                if len(extras) >= max_extra:
                    break
        if len(extras) >= max_extra:
            break
        body = (h.get("summary") or h.get("text") or "")[:400]
        for tok in _EXPAND_TOKEN.findall(body):
            low = tok.lower()
            if low in seen or len(tok) < 3:
                continue
            # 略過過短英文停用常見詞
            if low in {"the", "and", "for", "with", "from", "this", "that", "path"}:
                continue
            seen.add(low)
            extras.append(tok)
            if len(extras) >= max_extra:
                break
    if not extras:
        return query
    return query.strip() + " " + " ".join(extras)


def recall_hits(
    query: str,
    k: int = 5,
    scope: Optional[str] = None,
    db: Optional[str] = None,
    mode: str = "hybrid",
) -> List[dict]:
    """結構化檢索（供 MCP 格式化與 local_research）。

    每筆：id, path, start_line, end_line, text, summary, score, score_kind, mode
    """
    if not isinstance(query, str) or not query.strip():
        raise RecallError("query 不可為空")
    try:
        k = max(1, min(int(k), 20))
    except (TypeError, ValueError):
        raise RecallError("k 須為整數")

    mode_l = (mode or "hybrid").strip().lower()
    if mode_l not in _VALID_MODES:
        raise RecallError(f"mode 須為 {_VALID_MODES} 之一，得 {mode!r}")

    path = store.db_path(db)
    pool = max(k * 3, 30)

    try:
        if mode_l in ("hybrid", "keyword"):
            store.require_fts(path)

        if mode_l == "keyword":
            kw = store.fts_search(path, query, limit=pool)
            if not kw:
                return []
            by_id = store.load_by_ids(path, [cid for cid, _ in kw])
            hits: List[dict] = []
            for cid, raw_score in kw:
                row = by_id.get(cid)
                if not row or not _pass_filters(row, scope):
                    continue
                hits.append(
                    {
                        **{kk: row[kk] for kk in (
                            "id", "path", "start_line", "end_line", "text", "summary"
                        )},
                        "score": float(raw_score),
                        "score_kind": "kw",
                        "mode": mode_l,
                    }
                )
                if len(hits) >= k:
                    break
            return hits

        # semantic 或 hybrid：需嵌入 + 全表向量
        rows = store.load_all(path)
        qv = embed.embed_one(query)
    except (store.MemoryStoreError, embed.EmbedError) as exc:
        raise RecallError(str(exc)) from exc

    sem_scored: List[Tuple[float, dict]] = []
    for r in rows:
        if not _pass_filters(r, scope):
            continue
        sem_scored.append((store.cosine(qv, r["vector"]), r))
    sem_scored.sort(key=lambda t: t[0], reverse=True)
    sem_top = sem_scored[:pool]

    if mode_l == "semantic":
        out: List[dict] = []
        for score, r in sem_top[:k]:
            out.append(
                {
                    "id": r["id"],
                    "path": r["path"],
                    "start_line": r["start_line"],
                    "end_line": r["end_line"],
                    "text": r["text"],
                    "summary": r["summary"],
                    "score": float(score),
                    "score_kind": "sem",
                    "mode": mode_l,
                }
            )
        return out

    # hybrid：RRF(semantic ranks, keyword ranks)
    try:
        kw_pairs = store.fts_search(path, query, limit=pool)
    except store.MemoryStoreError as exc:
        raise RecallError(str(exc)) from exc

    # keyword 端也套 scope／governance（需載入 path）
    kw_ids_ordered: List[int] = []
    if kw_pairs:
        by_id = store.load_by_ids(path, [cid for cid, _ in kw_pairs])
        for cid, _ in kw_pairs:
            row = by_id.get(cid)
            if row and _pass_filters(row, scope):
                kw_ids_ordered.append(cid)

    sem_ids = [r["id"] for _, r in sem_top]
    fused = _rrf_fuse(sem_ids, kw_ids_ordered)

    # 建立 id → row／sem 分查找
    sem_map = {r["id"]: (score, r) for score, r in sem_top}
    # 補齊只出現在 keyword 的列
    missing = [cid for cid, _ in fused if cid not in sem_map]
    if missing:
        extra = store.load_by_ids(path, missing)
        for cid, row in extra.items():
            if _pass_filters(row, scope):
                sem_map[cid] = (-1.0, row)

    hits = []
    for cid, rrf in fused:
        pair = sem_map.get(cid)
        if not pair:
            continue
        score_sem, r = pair
        if not _pass_filters(r, scope):
            continue
        hits.append(
            {
                "id": r["id"],
                "path": r["path"],
                "start_line": r["start_line"],
                "end_line": r["end_line"],
                "text": r["text"],
                "summary": r["summary"],
                "score": float(rrf),
                "score_kind": "rrf",
                "sem": float(score_sem),
                "mode": mode_l,
            }
        )
        if len(hits) >= k:
            break
    return hits


def _snippet_chars() -> int:
    raw = os.getenv("MEMORY_SNIPPET_CHARS")
    if raw is None or not str(raw).strip():
        return 500
    try:
        return max(100, min(int(raw), 800))
    except (TypeError, ValueError):
        return 500


def _format_hits(hits: List[dict], mode: str, scope: Optional[str]) -> str:
    if not hits:
        return f"{_II_NOTE}\n（查無相關片段；mode={mode} scope={scope!r}）"

    limit = _snippet_chars()
    lines: List[str] = [f"{_II_NOTE} mode={mode}", ""]
    for h in hits:
        loc = f"{h['path']}:{h['start_line']}-{h['end_line']}"
        kind = h.get("score_kind", "?")
        score = h.get("score", 0.0)
        extra = ""
        if kind == "rrf" and "sem" in h and h["sem"] >= 0:
            extra = f"｜sem={h['sem']:.3f}"
        body = (h.get("summary") or h.get("text") or "").strip()
        if len(body) > limit:
            body = body[:limit] + " …"
        lines.append(f"【{loc}｜{kind}={score:.4f}{extra}】\n{body}\n")
    return "\n".join(lines)


def recall(
    query: str,
    k: int = 5,
    scope: Optional[str] = None,
    db: Optional[str] = None,
    mode: str = "hybrid",
) -> str:
    hits = recall_hits(query, k=k, scope=scope, db=db, mode=mode)
    mode_l = (mode or "hybrid").strip().lower()
    return _format_hits(hits, mode_l, scope)


def memory_status(db: Optional[str] = None, root: Optional[str] = None) -> str:
    path = store.db_path(db)
    base = pathlib.Path(root).resolve() if root else govern.REPO
    try:
        c = store.counts(path)
        stored = store.file_hashes(path)
    except store.MemoryStoreError as exc:
        raise RecallError(str(exc)) from exc

    stale: List[str] = []
    missing: List[str] = []
    for rel, meta in stored.items():
        abspath = base / rel
        if not abspath.is_file():
            missing.append(rel)
            continue
        if _file_sha(str(abspath)) != meta["hash"]:
            stale.append(rel)

    lines = [
        f"檔數：{c['files']}｜chunk 數：{c['chunks']}｜embed：{c['embed_model']}｜"
        f"built_at：{c['built_at']}｜search_schema：{c.get('search_schema', '?')}｜"
        f"fts：{'yes' if c.get('has_fts') else 'NO'}",
    ]
    if not stale and not missing:
        lines.append("狀態：新鮮（來源檔 hash 與索引一致）。")
    else:
        if stale:
            lines.append("狀態：過時 —— 來源已變更：")
            lines.extend(f"  - {p}" for p in stale[:50])
        if missing:
            lines.append("來源已刪除（仍殘於索引）：")
            lines.extend(f"  - {p}" for p in missing[:50])
        lines.append(
            "請執行 `python3 -m tools.project_memory_mcp index`（增量）；"
            "必要時 `index --full` 全量重建。"
        )
    return "\n".join(lines)
