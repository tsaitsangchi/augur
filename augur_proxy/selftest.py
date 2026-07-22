"""Selftest for Augur MCP P0 — no external deps except stdlib for core tests."""
from __future__ import annotations

import sys

from augur_proxy import cache, classifier


def _test_classifier() -> None:
    assert classifier.classify("explain L2 MD-X") == "quick"
    assert classifier.classify("check WM.44 compliance") == "compliance"
    assert classifier.classify("audit ruling §8.2") == "audit"
    assert classifier.backend_for("compliance") == "claude"
    assert classifier.backend_for("quick") == "local"


def _test_cache() -> None:
    cache.flush()
    cache.set("hello", "quick", "world")
    assert cache.get("hello", "quick") == "world"
    assert cache.get("hello", "audit") is None
    cache.flush()
    assert cache.get("hello", "quick") is None


def main() -> int:
    _test_classifier()
    _test_cache()
    print("mcp selftest: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
