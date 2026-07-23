"""constitution-mcp：MCP stdio server（JSON-RPC 2.0，純 stdlib）。

不依賴官方 `mcp` SDK——本 repo 之治權工具鏈以「純 stdlib、無外部相依」為紀律
（見 tools/constitution_lint/README.md），且 `.mcp.json` 因此無須綁定 venv。

協定：line-delimited JSON-RPC 2.0 over stdin/stdout。實作 `initialize`／
`tools/list`／`tools/call`；`notifications/*` 不回應（依 JSON-RPC，通知無 id 亦無回應）。

執行指令矩陣（實際啟動走 `python -m tools.constitution_mcp`；完整回歸鎖見同套件 `selftest.py`）：
  python -m tools.constitution_mcp.server              # 印用途（唯讀、免外部依賴）
  python -m tools.constitution_mcp.server --selftest    # 記憶體內 stdio 協定往返紅綠自測（零外部依賴）
"""
from __future__ import annotations

import json
import sys
import traceback

from . import tools

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "constitution", "version": "0.1.0"}

TOOLS = [
    {
        "name": "get_clause",
        "description": (
            "取單一**元憲章**條款（AUGUR-MC）之原文、自有括號名與行號。"
            "代號如 P4.E1、§2.5、F4、EV.9、PA。"
            "用於核對條款原文，取代整檔讀入 META-CONSTITUTION.md。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "條款代號，如 P4.E1、§2.5、F4"}},
            "required": ["code"],
        },
    },
    {
        "name": "get_spec_clause",
        "description": (
            "取單一**下層生效規格**條款之原文（WM./ONT./ID./IDO./KS./KDO./L5./L6./L7./LDO. 開頭）。"
            "用於核對規格條款，取代整檔讀入動輒 100–270KB 之 specs/*.md。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "條款代號，如 WM.44、KS.42、L7.21"}},
            "required": ["code"],
        },
    },
    {
        "name": "search_clauses",
        "description": (
            "以關鍵詞檢索憲章與生效規格之條款，回代號＋標籤＋摘句（不回全文）。"
            "先用本工具定位，再以 get_clause／get_spec_clause 取全文。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "關鍵詞"},
                "limit": {"type": "integer", "description": "回傳筆數上限（預設 12）"},
                "scope": {"type": "string", "enum": ["all", "mc", "specs"],
                          "description": "檢索範圍（預設 all）"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "lint_compliance",
        "description": (
            "對規格檔實跑 §8.3 compliance lint，回結構化結果。"
            "**每次實跑，不快取**——本專案已三度實證『陳舊綠燈』之害。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"spec_path": {"type": "string",
                                         "description": "規格檔路徑（相對 repo 根或絕對）"}},
            "required": ["spec_path"],
        },
    },
    {
        "name": "layer_status",
        "description": (
            "回八層治權現況：各層規格版本、所依 MC 版本、檔案路徑，並標示 mc-version 落差。"
            "由 front-matter 實地解析，非硬編碼。新 session 開場摸底用。"
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_ruling",
        "description": "取 Steward 裁決之主文與依據（如 2026-025 或 025）。",
        "inputSchema": {
            "type": "object",
            "properties": {"number": {"type": "string", "description": "裁決號，如 2026-025"}},
            "required": ["number"],
        },
    },
    {
        "name": "list_amendments",
        "description": "回修訂登錄簿（AMENDMENT-LOG）最近 N 筆之摘要。",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "筆數（預設 10）"}},
        },
    },
]

_DISPATCH = {
    "get_clause": lambda a: tools.get_clause(a["code"]),
    "get_spec_clause": lambda a: tools.get_spec_clause(a["code"]),
    "search_clauses": lambda a: tools.search_clauses(
        a["query"], int(a.get("limit", 12)), a.get("scope", "all")),
    "lint_compliance": lambda a: tools.lint_compliance(a["spec_path"]),
    "layer_status": lambda a: tools.layer_status(),
    "get_ruling": lambda a: tools.get_ruling(a["number"]),
    "list_amendments": lambda a: tools.list_amendments(int(a.get("limit", 10))),
}


def call_tool(name: str, args: dict) -> dict:
    """執行工具。錯誤一律以 isError 回報——不靜默回近似答案。"""
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"content": [{"type": "text", "text": f"未知工具：{name}"}], "isError": True}
    try:
        return {"content": [{"type": "text", "text": fn(args or {})}]}
    except tools.ToolError as e:
        return {"content": [{"type": "text", "text": f"錯誤：{e}"}], "isError": True}
    except KeyError as e:
        return {"content": [{"type": "text", "text": f"缺必要參數：{e}"}], "isError": True}
    except Exception:
        return {"content": [{"type": "text",
                             "text": f"工具內部錯誤（本結果不具權威）：\n{traceback.format_exc()}"}],
                "isError": True}


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
    print("constitution_mcp.server selftest:" + (" OK" if ok else " FAIL")
          + "（完整回歸鎖見 `python -m tools.constitution_mcp --selftest`）")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
