"""嵌入：經本機 Ollama /api/embed 產生向量（純 stdlib urllib）。

失敗發聲：嵌入服務不可達/回應異常一律拋 EmbedError，不靜默回零向量。
stub 模式（PROJECT_MEMORY_MCP_STUB=1）以確定性雜湊產生向量，供 selftest 無 Ollama 亦可跑。

執行指令矩陣：
  python -m tools.project_memory_mcp.embed              # 印用途（唯讀、免外部服務）
  python -m tools.project_memory_mcp.embed --selftest    # PROJECT_MEMORY_MCP_STUB=1 走 stub 向量紅綠自測
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.error
import urllib.request
from typing import List

_STUB_DIM = 64


class EmbedError(Exception):
    """嵌入層錯誤——須經協定層帶 isError，不得偽裝成正常結果。"""


def _stub_enabled() -> bool:
    return os.getenv("PROJECT_MEMORY_MCP_STUB", "").lower() in ("1", "true", "yes")


def _ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


def embed_model() -> str:
    return os.getenv("EMBED_MODEL", "nomic-embed-text")


def _stub_vec(text: str) -> List[float]:
    """確定性向量：由 SHA256 展開為 _STUB_DIM 維並正規化（同文→同向量）。"""
    vec: List[float] = []
    counter = 0
    while len(vec) < _STUB_DIM:
        h = hashlib.sha256(f"{counter}:{text}".encode("utf-8")).digest()
        for b in h:
            vec.append((b / 255.0) * 2.0 - 1.0)
            if len(vec) >= _STUB_DIM:
                break
        counter += 1
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def embed(texts: List[str]) -> List[List[float]]:
    """對一批文本回向量清單。空清單回空。"""
    if not texts:
        return []
    if _stub_enabled():
        return [_stub_vec(t) for t in texts]

    url = _ollama_url() + "/api/embed"
    body = json.dumps({"model": embed_model(), "input": texts}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode(errors="replace")[:200]
        except Exception:
            pass
        raise EmbedError(
            f"Ollama 嵌入回 HTTP {exc.code}（模型是否已 pull？EMBED_MODEL={embed_model()}）：{detail}"
        ) from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise EmbedError(f"Ollama 不可達（{_ollama_url()}）：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise EmbedError(f"Ollama 嵌入回應非 JSON：{exc}") from exc

    embeddings = data.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        got = str(embeddings)[:80]
        raise EmbedError(f"嵌入回應筆數不符：期望 {len(texts)}，得 {got}")
    return embeddings


def embed_one(text: str) -> List[float]:
    return embed([text])[0]


def _selftest() -> int:
    prev = os.environ.get("PROJECT_MEMORY_MCP_STUB")
    os.environ["PROJECT_MEMORY_MCP_STUB"] = "1"
    try:
        v1 = embed_one("hello")
        v2 = embed_one("hello")
        v3 = embed_one("world")
        ok = len(v1) == _STUB_DIM and v1 == v2 and v1 != v3
        ok = ok and embed([]) == []
    finally:
        if prev is None:
            os.environ.pop("PROJECT_MEMORY_MCP_STUB", None)
        else:
            os.environ["PROJECT_MEMORY_MCP_STUB"] = prev
    print("embed selftest:" + (" OK" if ok else " FAIL") + "（stub 向量，不連 Ollama）")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
