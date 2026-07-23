"""Audit logger for MCP invocations — JSON lines, prompt hash only.

執行指令矩陣：
  python -m augur_proxy.logger              # 印用途（唯讀、免外部服務）
  python -m augur_proxy.logger --selftest    # 寫一筆記錄到暫存檔並讀回驗證（零外部依賴）
"""
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


def _selftest() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["MCP_AUDIT_LOG"] = str(pathlib.Path(tmp) / "audit.log")
        log_request(req_type="quick", prompt="selftest", backend="local", tokens=0)
        lines = _log_path().read_text(encoding="utf-8").strip().splitlines()
        rec = json.loads(lines[-1])
        ok = rec["type"] == "quick" and rec["prompt_hash"] == prompt_hash("selftest")
        os.environ.pop("MCP_AUDIT_LOG", None)
    print("logger selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
