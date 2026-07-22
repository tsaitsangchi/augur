"""recall / memory_status —— MCP 唯讀工具邏輯。

僅匯入唯讀模組（store/embed/govern）；不匯入 index（寫入端）。
治理防線（縱深）：即便索引誤含治理片段，recall 於回傳前再過濾一次。
"""
from __future__ import annotations

import hashlib
import os
import pathlib
from typing import List, Optional

from . import embed, govern, store

_II_NOTE = (
    "⚠ 語意檢索結果為 [I] 輔助；精確原文請經 constitution-mcp（治理條款）或讀原檔，"
    "不得原文貼入任何 [N] 治理文書。"
)


class RecallError(Exception):
    """recall 層錯誤——經協定層帶 isError，不靜默回空/近似。"""


def _file_sha(abspath: str) -> str:
    h = hashlib.sha256()
    with open(abspath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def recall(query: str, k: int = 5, scope: Optional[str] = None, db: Optional[str] = None) -> str:
    if not isinstance(query, str) or not query.strip():
        raise RecallError("query 不可為空")
    try:
        k = max(1, min(int(k), 20))
    except (TypeError, ValueError):
        raise RecallError("k 須為整數")

    path = store.db_path(db)
    try:
        rows = store.load_all(path)  # 索引不存在→MemoryStoreError（失敗發聲）
        qv = embed.embed_one(query)  # 嵌入不可達→EmbedError（失敗發聲）
    except (store.MemoryStoreError, embed.EmbedError) as exc:
        raise RecallError(str(exc)) from exc

    scored = []
    for r in rows:
        # 縱深治理防線：任何落入治理權威語料之片段一律不回
        if govern.is_governance_path(govern.REPO / r["path"]):
            continue
        if scope and not r["path"].startswith(scope):
            continue
        scored.append((store.cosine(qv, r["vector"]), r))

    if not scored:
        return f"{_II_NOTE}\n\n（查無相關片段；scope={scope!r}）"

    scored.sort(key=lambda t: t[0], reverse=True)
    top = scored[:k]

    lines: List[str] = [_II_NOTE, ""]
    for score, r in top:
        loc = f"{r['path']}:{r['start_line']}-{r['end_line']}"
        body = (r["summary"] or r["text"]).strip()
        if len(body) > 800:
            body = body[:800] + " …"
        lines.append(f"【{loc}｜sim={score:.3f}】\n{body}\n")
    return "\n".join(lines)


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
        abspath = str(base / rel)
        if not os.path.isfile(abspath):
            missing.append(rel)
            continue
        try:
            if _file_sha(abspath) != meta["hash"]:
                stale.append(rel)
        except OSError:
            stale.append(rel)

    out = [
        f"索引：{path}",
        f"嵌入模型：{c['embed_model']}｜建立時間：{c['built_at']}",
        f"檔數：{c['files']}｜chunk 數：{c['chunks']}",
    ]
    if stale or missing:
        out.append("")
        out.append("⚠ 索引可能過時，建議重建（python3 -m tools.project_memory_mcp index）：")
        if stale:
            out.append(f"  已變更 {len(stale)} 檔：" + ", ".join(sorted(stale)[:20]))
        if missing:
            out.append(f"  已刪除 {len(missing)} 檔：" + ", ".join(sorted(missing)[:20]))
    else:
        out.append("狀態：新鮮（來源檔 hash 與索引一致）。")
    return "\n".join(out)
