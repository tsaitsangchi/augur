"""Local LLM backend via Ollama. Falls back to stub when Ollama is unavailable.

執行指令矩陣：
  python -m augur_proxy.local_llm              # 印用途（唯讀、免外部服務）
  python -m augur_proxy.local_llm --selftest    # 純 stub fallback 自測（不連 Ollama、零外部依賴）
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")


def ask(prompt: str) -> tuple[str, int]:
    """Return (response, tokens). Local backend always reports 0 API tokens."""
    try:
        return _ask_ollama(prompt), 0
    except Exception:
        return _stub_response(prompt), 0


def _ask_ollama(prompt: str) -> str:
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    body = json.dumps(
        {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    text = data.get("response", "").strip()
    if not text:
        raise RuntimeError("empty ollama response")
    return text


def _stub_response(prompt: str) -> str:
    preview = prompt[:120].replace("\n", " ")
    return f"(local stub) Ollama unavailable — echo preview: {preview}"


def _selftest() -> int:
    resp = _stub_response("hello world")
    ok = resp.startswith("(local stub)") and "hello world" in resp
    print("local_llm selftest:" + (" OK" if ok else " FAIL") + " (stub path only, 不連 Ollama)")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
