"""BC shim — Ollama LLM 工廠 SSOT 已遷 `augur.llm.ollama`（STRUCT advisor↔deliberation）。

本檔再匯出全部公開／測試入口，既有 `from augur.advisor.ollama import …` 不變。

執行指令矩陣:
  python -m augur.advisor.ollama --selftest   # 轉呼叫 llm.ollama
"""
from augur.llm.ollama import (  # noqa: F401
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    _assert_local_host,
    _selftest,
    base_url,
    chat_with_stats,
    make_llm_fn,
    make_structured_llm_fn,
    strip_quote_marks,
    strip_think,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "DEFAULT_TIMEOUT",
    "base_url",
    "chat_with_stats",
    "make_llm_fn",
    "make_structured_llm_fn",
    "strip_quote_marks",
    "strip_think",
]


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
    print("(自測:python -m augur.advisor.ollama --selftest → augur.llm.ollama)")
