"""project-memory-mcp 進入點。

  執行指令矩陣：
  python3 -m tools.project_memory_mcp             # 起 stdio server（供 .cursor/mcp.json）
  python3 -m tools.project_memory_mcp index       # 增量索引（無 DB／缺 FTS／embed 變更則全量）
  python3 -m tools.project_memory_mcp index --full  # 刪 DB 全量重建
  python3 -m tools.project_memory_mcp memory_status  # 印索引現況
  python3 -m tools.project_memory_mcp selftest    # selftest（stub 嵌入，無須 Ollama）
"""
import sys

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg in ("selftest", "--selftest"):
        from . import selftest as selftest_mod
        sys.exit(selftest_mod.run())
    if arg == "index":
        from . import index
        sys.exit(index.main(sys.argv[2:]))
    if arg == "memory_status":
        from . import recall
        print(recall.memory_status())
        sys.exit(0)
    from . import server
    sys.exit(server.serve())
