"""local-llm-mcp 進入點。

  執行指令矩陣：
  python3 -m tools.local_llm_mcp             # 起 stdio server（供 .cursor/mcp.json 呼叫）
  python3 -m tools.local_llm_mcp selftest    # 跑 selftest（stub 模式，無須 Ollama）
"""
import sys

from . import selftest as selftest_mod, server

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("selftest", "--selftest"):
        sys.exit(selftest_mod.run())
    sys.exit(server.serve())
