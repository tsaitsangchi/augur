"""Prompt cache with per-type TTL. In-memory by default; Redis optional via REDIS_URL.

執行指令矩陣：
  python -m augur_proxy.cache              # 印用途（唯讀、免外部服務）
  python -m augur_proxy.cache --selftest   # get/set/flush 純記憶體紅綠自測（零外部依賴）
"""
from __future__ import annotations

import hashlib
import os
import time
from typing import Optional

TTL_SECONDS: dict[str, int] = {
    "quick": 7 * 86400,
    "static": 7 * 86400,
    "compliance": 24 * 3600,
    "audit": 3600,
}

_memory: dict[str, tuple[str, float]] = {}
_redis = None


def _cache_key(prompt: str, req_type: str) -> str:
    digest = hashlib.sha256(f"{req_type}:{prompt}".encode()).hexdigest()
    return f"augur:mcp:{digest}"


def _redis_client():
    global _redis
    if _redis is not None:
        return _redis
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        return None
    try:
        import redis  # type: ignore

        _redis = redis.from_url(url, decode_responses=True)
        _redis.ping()
        return _redis
    except Exception:
        return None


def get(prompt: str, req_type: str) -> Optional[str]:
    key = _cache_key(prompt, req_type)
    client = _redis_client()
    if client is not None:
        return client.get(key)

    entry = _memory.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.time() >= expires_at:
        del _memory[key]
        return None
    return value


def set(prompt: str, req_type: str, response: str) -> None:
    key = _cache_key(prompt, req_type)
    ttl = TTL_SECONDS.get(req_type, 3600)
    client = _redis_client()
    if client is not None:
        client.setex(key, ttl, response)
        return
    _memory[key] = (response, time.time() + ttl)


def flush() -> int:
    """Clear all cached entries. Returns number of keys removed (memory only)."""
    global _memory
    count = len(_memory)
    _memory = {}
    client = _redis_client()
    if client is not None:
        keys = client.keys("augur:mcp:*")
        if keys:
            client.delete(*keys)
            count = max(count, len(keys))
    return count


def _selftest() -> int:
    flush()
    set("hello", "quick", "world")
    ok = get("hello", "quick") == "world" and get("hello", "audit") is None
    flush()
    ok = ok and get("hello", "quick") is None
    print("cache selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
