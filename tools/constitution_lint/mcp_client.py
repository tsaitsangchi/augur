"""HTTP client for Augur MCP Router.

執行指令矩陣：
  python -m tools.constitution_lint.mcp_client              # 印用途（唯讀、免外部服務）
  python -m tools.constitution_lint.mcp_client --selftest    # 嘗試連線 MCP_URL；router 未啟動則 graceful SKIP（非 FAIL）
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/invoke")


def invoke_mcp(prompt: str, req_type: Optional[str] = None, *, timeout: int = 120) -> dict:
    """POST to MCP router. Returns parsed JSON response."""
    body = {"prompt": prompt}
    if req_type is not None:
        body["type"] = req_type
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _selftest() -> int:
    try:
        invoke_mcp("selftest ping", timeout=3)
        print("mcp_client selftest: OK（router 已連線）")
        return 0
    except (urllib.error.URLError, OSError) as exc:
        print(f"mcp_client selftest: SKIP（MCP router 未啟動，非本模組故障）— {exc}")
        return 0


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
