"""local-llm-mcp：MCP stdio server（JSON-RPC 2.0，純 stdlib）。

比照 tools/constitution_mcp/server.py 之體例：line-delimited JSON-RPC 2.0 over
stdin/stdout；實作 initialize／tools/list／tools/call；notifications/* 不回應。

本 server 唯一副作用為對 Ollama 之唯讀推論呼叫；不提供任何寫入工具。
"""
from __future__ import annotations

import json
import sys
import traceback

from . import tools

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "local-llm", "version": "0.1.0"}

TOOLS = [
    {
        "name": "local_summarize",
        "description": (
            "以本地小模型把長文或 repo 內檔案濃縮成至多 N 句重點（大進小出，省 Cursor context）。"
            "text 與 path 二選一。輸出附本地來源標記，僅供 [I] 輔助、不得入治理文書。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待摘要文本（與 path 二選一）"},
                "path": {"type": "string", "description": "repo 內相對路徑（與 text 二選一）"},
                "max_sentences": {"type": "integer", "description": "摘要句數上限（預設 5，上限 20）"},
            },
        },
    },
    {
        "name": "local_extract",
        "description": (
            "以本地小模型依指示，從長文或 repo 內檔案抽取精簡結果（清單/欄位）。"
            "text 與 path 二選一。輸出附本地來源標記，僅供 [I] 輔助。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {"type": "string", "description": "抽取指示，如「列出所有條款代號」"},
                "text": {"type": "string", "description": "待抽取文本（與 path 二選一）"},
                "path": {"type": "string", "description": "repo 內相對路徑（與 text 二選一）"},
            },
            "required": ["instruction"],
        },
    },
    {
        "name": "local_ask",
        "description": (
            "以本地小模型回答，強制短輸出（省 token）。適合可容忍小模型品質之輔助查詢；"
            "深度推理與最終判斷請交回 Cursor。輸出附本地來源標記。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "問題"},
                "max_words": {"type": "integer", "description": "回答字數上限（預設 200，上限 1000）"},
            },
            "required": ["prompt"],
        },
    },
]

_DISPATCH = {
    "local_summarize": lambda a: tools.local_summarize(
        text=a.get("text"), path=a.get("path"), max_sentences=a.get("max_sentences", 5)
    ),
    "local_extract": lambda a: tools.local_extract(
        a["instruction"], text=a.get("text"), path=a.get("path")
    ),
    "local_ask": lambda a: tools.local_ask(a["prompt"], max_words=a.get("max_words", 200)),
}


def call_tool(name: str, args: dict) -> dict:
    """執行工具。錯誤一律以 isError 回報——不靜默回近似答案。"""
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"content": [{"type": "text", "text": f"未知工具：{name}"}], "isError": True}
    try:
        return {"content": [{"type": "text", "text": fn(args or {})}]}
    except tools.LocalLLMError as e:
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
    """回傳 response dict；通知（無 id）回 None。"""
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
