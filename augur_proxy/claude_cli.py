"""Claude backend — CLI subprocess when available, otherwise stub.

執行指令矩陣：
  python -m augur_proxy.claude_cli              # 印用途（唯讀、免外部服務）
  python -m augur_proxy.claude_cli --selftest    # 強制 MCP_CLAUDE_STUB=1 走 stub 自測（零外部依賴）
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess


def ask(prompt: str) -> tuple[str, int]:
    """Return (response, tokens)."""
    if os.getenv("MCP_CLAUDE_STUB", "").lower() in ("1", "true", "yes"):
        return _stub_response(prompt), 0

    cli = shutil.which("claude")
    if cli is None:
        return _stub_response(prompt), 0

    try:
        proc = subprocess.run(
            [cli, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"(claude error) {exc}", 0

    output = (proc.stdout or proc.stderr or "").strip()
    if proc.returncode != 0 and not output:
        return _stub_response(prompt), 0

    tokens = _parse_tokens(output)
    return output, tokens


def _parse_tokens(text: str) -> int:
    m = re.search(r"(\d+)\s+tokens?", text, re.I)
    return int(m.group(1)) if m else 0


def _stub_response(prompt: str) -> str:
    preview = prompt[:120].replace("\n", " ")
    return (
        "(claude stub) Claude CLI unavailable — set MCP_CLAUDE_STUB=0 and install "
        f"`claude` CLI for live calls. Preview: {preview}"
    )


def _selftest() -> int:
    prev = os.environ.get("MCP_CLAUDE_STUB")
    os.environ["MCP_CLAUDE_STUB"] = "1"
    try:
        response, tokens = ask("hello world")
        ok = response.startswith("(claude stub)") and tokens == 0
    finally:
        if prev is None:
            os.environ.pop("MCP_CLAUDE_STUB", None)
        else:
            os.environ["MCP_CLAUDE_STUB"] = prev
    print("claude_cli selftest:" + (" OK" if ok else " FAIL") + " (stub path only, 不呼叫 claude CLI)")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
