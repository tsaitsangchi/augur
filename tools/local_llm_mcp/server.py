"""local-llm-mcp：MCP stdio server（JSON-RPC 2.0，純 stdlib）。

比照 tools/constitution_mcp/server.py 之體例：line-delimited JSON-RPC 2.0 over
stdin/stdout；實作 initialize／tools/list／tools/call；notifications/* 不回應。

本 server 唯一副作用為對 Ollama 之唯讀推論呼叫；不提供任何寫入工具。

執行指令矩陣（實際啟動走 `python -m tools.local_llm_mcp`；完整回歸鎖見同套件 `selftest.py`）：
  python -m tools.local_llm_mcp.server              # 印用途（唯讀、免外部依賴）
  python -m tools.local_llm_mcp.server --selftest    # 記憶體內 stdio 協定往返紅綠自測（零外部依賴）
"""
from __future__ import annotations

import json
import sys
import traceback

from . import tools

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "local-llm", "version": "0.2.1"}

TOOLS = [
    {
        "name": "local_summarize",
        "description": (
            "優先用於：已知單一 path 或已有長 text，要≤N句摘要。"
            "跨檔不知路徑請改 local_research；已知多 path 請改 local_map_reduce。"
            "text 與 path 二選一。[I] 輔助，不得入治理文書。"
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
            "優先用於：已知單一來源，要依指示抽清單／欄位（大進小出）。"
            "勿用於治理權威路徑（改 constitution-mcp）。[I] 輔助。"
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
            "優先用於：短問短答且可容忍本地模型品質；不要拿來做全庫探查。"
            "跨檔探問用 local_research。強制短輸出。[I]。"
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
    {
        "name": "local_research",
        "description": (
            "優先用於：跨檔／不知路徑、要短結論——hybrid 多跳檢索後本地濃縮。"
            "只要片段出處請用 recall；已知單檔用 summarize；治理原文用 constitution-mcp。"
            "輸出 [I]。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "研究問題"},
                "k": {"type": "integer", "description": "每跳取回片段數（預設 5，上限 20）"},
                "hops": {"type": "integer", "description": "跳數（預設 2，上限 3）"},
                "scope": {"type": "string", "description": "可選路徑前綴，如 ops/"},
                "max_sentences": {"type": "integer", "description": "濃縮句數上限（預設 8）"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "local_map_reduce",
        "description": (
            "優先用於：已知多個具體 paths（≤12）要合併摘要；不知路徑請用 local_research。"
            "任一治理／越界／缺失 path → 整次 isError。[I]。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "repo 內相對路徑陣列（上限 12）",
                },
                "instruction": {"type": "string", "description": "合併指示"},
                "max_sentences": {"type": "integer", "description": "合併輸出句數上限（預設 8）"},
            },
            "required": ["paths", "instruction"],
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
    "local_research": lambda a: tools.local_research(
        a["query"],
        k=a.get("k", 5),
        hops=a.get("hops", 2),
        scope=a.get("scope"),
        max_sentences=a.get("max_sentences", 8),
    ),
    "local_map_reduce": lambda a: tools.local_map_reduce(
        a["paths"], a["instruction"], max_sentences=a.get("max_sentences", 8)
    ),
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
    print("local_llm_mcp.server selftest:" + (" OK" if ok else " FAIL")
          + "（完整回歸鎖見 `python -m tools.local_llm_mcp --selftest`）")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
