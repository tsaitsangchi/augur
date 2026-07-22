"""Rule-based request classifier for MCP routing."""
from __future__ import annotations

import re
from typing import Literal

RequestType = Literal["quick", "static", "compliance", "audit"]

RULES: list[tuple[str, RequestType]] = [
    (r"compliance|合規|lint|WM\.\d+|L7\.\d+|constitution_lint", "compliance"),
    (r"audit|審計|裁決|ruling|§8\.\d|Steward", "audit"),
    (r"explain|解釋|什麼是|overview|概覽|describe", "quick"),
    (r"summary|摘要|白話|plain.?language", "quick"),
]

BACKEND_MAP: dict[RequestType, str] = {
    "quick": "local",
    "static": "cache",
    "compliance": "claude",
    "audit": "claude",
}


def classify(prompt: str) -> RequestType:
    """Classify a prompt into a routing category. Defaults to quick (local)."""
    for pattern, req_type in RULES:
        if re.search(pattern, prompt, re.I):
            return req_type
    return "quick"


def backend_for(req_type: RequestType) -> str:
    return BACKEND_MAP[req_type]
