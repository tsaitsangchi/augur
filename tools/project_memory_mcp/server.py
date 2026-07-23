"""project-memory-mcp：MCP stdio server（JSON-RPC 2.0，純 stdlib，唯讀）。

比照 tools/local_llm_mcp/server.py 之體例。僅暴露 recall／memory_status 兩支
唯讀工具；建索引為 CLI（index.py），不經 MCP。本模組**不匯入 index**（讀寫分離）。

執行指令矩陣（實際啟動走 `python -m tools.project_memory_mcp`；完整回歸鎖見同套件 `selftest.py`）：
  python -m tools.project_memory_mcp.server              # 印用途（唯讀、免外部依賴）
  python -m tools.project_memory_mcp.server --selftest    # 記憶體內 stdio 協定往返紅綠自測（零外部依賴）
"""
from __future__ import annotations

import json
import sys
import traceback

from . import recall

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "project-memory", "version": "0.2.0"}

TOOLS = [
    {
        "name": "recall",
        "description": (
            "優先用於：只要相關片段＋path:line 出處、尚未要濃縮結論時。"
            "勿與 local_research 搶活（跨檔要短答請用 local_research）。"
            "預設 hybrid＝語意+FTS5 RRF；結果為 [I]。治理精確原文請經 constitution-mcp。"
            "缺索引／缺 FTS／嵌入不可達 → isError，不靜默回空。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "自然語言查詢"},
                "k": {"type": "integer", "description": "回傳片段數（預設 5，上限 20）"},
                "scope": {"type": "string", "description": "可選：限定相對路徑前綴，如 reports/"},
                "mode": {
                    "type": "string",
                    "description": "hybrid（預設）｜semantic｜keyword",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "memory_status",
        "description": (
            "優先用於：懷疑索引陳舊或缺 FTS 時先查現況。"
            "回檔數／chunk／embed／built_at／FTS，並列出過時或已刪來源。"
            "索引不存在 → isError。"
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]

_DISPATCH = {
    "recall": lambda a: recall.recall(
        a["query"],
        k=a.get("k", 5),
        scope=a.get("scope"),
        mode=a.get("mode", "hybrid"),
    ),
    "memory_status": lambda a: recall.memory_status(),
}


def call_tool(name: str, args: dict) -> dict:
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"content": [{"type": "text", "text": f"未知工具：{name}"}], "isError": True}
    try:
        return {"content": [{"type": "text", "text": fn(args or {})}]}
    except recall.RecallError as e:
        return {"content": [{"type": "text", "text": f"錯誤：{e}"}], "isError": True}
    except KeyError as e:
        return {"content": [{"type": "text", "text": f"缺必要參數：{e}"}], "isError": True}
    except Exception:
        return {
            "content": [
                {"type": "text", "text": f"工具內部錯誤（本結果不具權威）：\n{traceback.format_exc()}"}
            ],
            "isError": True,
        }


def handle(msg: dict):
    method, mid = msg.get("method"), msg.get("id")

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        }
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        p = msg.get("params") or {}
        result = call_tool(p.get("name", ""), p.get("arguments") or {})
    elif method == "ping":
        result = {}
    elif method and method.startswith("notifications/"):
        return None
    else:
        if mid is None:
            return None
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"Method not found: {method}"}}

    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(stdin=None, stdout=None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            stdout.write(json.dumps({"jsonrpc": "2.0", "id": None,
                                     "error": {"code": -32700,
                                               "message": f"Parse error: {e}"}}) + "\n")
            stdout.flush()
            continue
        resp = handle(msg)
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


def _selftest() -> int:
    import io

    inp = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n")
    out = io.StringIO()
    serve(inp, out)
    resp = json.loads(out.getvalue().splitlines()[0])
    ok = resp.get("result", {}).get("protocolVersion") == PROTOCOL_VERSION

    inp2 = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n")
    out2 = io.StringIO()
    serve(inp2, out2)
    resp2 = json.loads(out2.getvalue().splitlines()[0])
    ok = ok and len(resp2.get("result", {}).get("tools", [])) == len(TOOLS)
    print("project_memory_mcp.server selftest:" + (" OK" if ok else " FAIL")
          + "（完整回歸鎖見 `python -m tools.project_memory_mcp selftest`）")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
