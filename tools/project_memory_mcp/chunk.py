"""切塊：依標題/段落邊界把文本切成帶行號的片段（純 stdlib，唯讀）。

每片段回 (start_line, end_line, text)，行號 1-based，供 recall 附 `path:line` 出處。
"""
from __future__ import annotations

from typing import List, Tuple

Chunk = Tuple[int, int, str]


def chunk_text(text: str, max_chars: int = 1500) -> List[Chunk]:
    """把 text 切成片段：遇 markdown 標題或累積超過 max_chars 即斷開。"""
    lines = text.splitlines()
    chunks: List[Chunk] = []
    cur: List[str] = []
    cur_start = 1

    def flush(end_line: int) -> None:
        if cur and any(ln.strip() for ln in cur):
            body = "\n".join(cur).strip()
            if body:
                chunks.append((cur_start, end_line, body))

    for i, line in enumerate(lines, start=1):
        heading = line.lstrip().startswith("#")
        cur_len = sum(len(ln) + 1 for ln in cur)
        if cur and (heading or cur_len >= max_chars):
            flush(i - 1)
            cur = []
            cur_start = i
        cur.append(line)
    flush(len(lines) if lines else 1)
    return chunks
