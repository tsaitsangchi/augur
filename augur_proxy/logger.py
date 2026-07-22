"""Audit logger for MCP invocations — JSON lines, prompt hash only."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
from datetime import datetime, timezone

_REPO = pathlib.Path(__file__).resolve().parents[1]
_DEFAULT_LOG = _REPO / "logs" / "mcp_audit.log"


def _log_path() -> pathlib.Path:
    return pathlib.Path(os.getenv("MCP_AUDIT_LOG", str(_DEFAULT_LOG)))


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def log_request(
    *,
    req_type: str,
    prompt: str,
    backend: str,
    tokens: int,
    cache_hit: bool = False,
) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": req_type,
        "prompt_hash": prompt_hash(prompt),
        "backend": backend,
        "tokens": tokens,
        "cache_hit": cache_hit,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
