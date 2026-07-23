"""Rule-based request classifier for MCP routing.

執行指令矩陣：
  python -m augur_proxy.classifier              # 印用途（唯讀、免外部服務）
  python -m augur_proxy.classifier --selftest    # 規則分類紅綠自測（零外部依賴）
"""
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


def _selftest() -> int:
    ok = (
        classify("explain L2 MD-X") == "quick"
        and classify("check WM.44 compliance") == "compliance"
        and classify("audit ruling §8.2") == "audit"
        and backend_for("compliance") == "claude"
        and backend_for("quick") == "local"
    )
    print("classifier selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
