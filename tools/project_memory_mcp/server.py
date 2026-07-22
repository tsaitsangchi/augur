"""project-memory-mcp：MCP stdio server（JSON-RPC 2.0，純 stdlib，唯讀）。

比照 tools/local_llm_mcp/server.py 之體例。僅暴露 recall／memory_status 兩支
唯讀工具；建索引為 CLI（index.py），不經 MCP。本模組**不匯入 index**（讀寫分離）。
"""
from __future__ import annotations

import json
import sys
import traceback

from . import recall

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "project-memory", "version": "0.1.0"}

TOOLS = [
    {
        "name": "recall",
        "description": (
            "在全 repo 非治理輔助語料的語意索引中，找出與 query 最相關的 top-k 片段"
            "（附 path:line 出處，省 Cursor context）。結果為 [I] 輔助；治理條款精確原文請經 "
            "constitution-mcp。索引不存在或嵌入服務不可達時回錯誤，不靜默回空。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "自然語言查詢"},
                "k": {"type": "integer", "description": "回傳片段數（預設 5，上限 20）"},
                "scope": {"type": "string", "description": "可選：限定相對路徑前綴，如 reports/"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "memory_status",
        "description": (
            "回索引現況：檔數、chunk 數、嵌入模型、建立時間，並列出來源檔已變更/刪除者"
            "（陳舊發聲）。索引不存在時回錯誤。"
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]

_DISPATCH = {
    "recall": lambda a: recall.recall(
        a["query"], k=a.get("k", 5), scope=a.get("scope")
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
