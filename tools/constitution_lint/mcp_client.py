"""HTTP client for Augur MCP Router."""
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
