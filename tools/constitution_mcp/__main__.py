"""constitution-mcp 進入點。

  執行指令矩陣：
  python3 -m tools.constitution_mcp             # 起 stdio server（供 .mcp.json 呼叫）
  python3 -m tools.constitution_mcp selftest    # 跑 selftest
"""
import sys

from . import selftest as selftest_mod, server

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("selftest", "--selftest"):
        sys.exit(selftest_mod.run())
    sys.exit(server.serve())
