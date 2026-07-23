"""constitution-mcp selftest（純 stdlib）。

比照 tools/constitution_lint 之慣例：凡宣稱之性質皆須有**可執行**斷言。
特別鎖住四項設計紀律——唯讀、不快取、附出處、失敗發聲。

執行指令矩陣：
  python -m tools.constitution_mcp --selftest
  python -c "from tools.constitution_mcp.selftest import run; raise SystemExit(run())"
"""
from __future__ import annotations

import io
import json

from . import server, tools

_FAILS = []


def _ok(cond, msg):
    if not cond:
        _FAILS.append(msg)


def _rpc(payload: list) -> list:
    """以 stdio 實跑 server，回 response 清單。"""
    inp = io.StringIO("\n".join(json.dumps(m) for m in payload) + "\n")
    out = io.StringIO()
    server.serve(inp, out)
    return [json.loads(ln) for ln in out.getvalue().splitlines() if ln.strip()]


def run() -> int:
    _FAILS.clear()

    # ── 協定層 ──────────────────────────────────────────────────────────
    r = _rpc([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}])
    _ok(len(r) == 1 and r[0]["result"]["protocolVersion"] == server.PROTOCOL_VERSION,
        "initialize 未回正確 protocolVersion")

    # 通知無 id → 不得有回應（JSON-RPC）
    r = _rpc([{"jsonrpc": "2.0", "method": "notifications/initialized"}])
    _ok(r == [], "通知不應產生回應")

    r = _rpc([{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}])
    names = {t["name"] for t in r[0]["result"]["tools"]}
    _ok(names == set(server._DISPATCH), f"tools/list 與 _DISPATCH 不一致：{names ^ set(server._DISPATCH)}")
    _ok(all(t.get("inputSchema", {}).get("type") == "object" for t in r[0]["result"]["tools"]),
        "有工具缺 inputSchema")

    # 壞 JSON → 回 parse error 而非崩潰
    out = io.StringIO()
    server.serve(io.StringIO("{not json}\n"), out)
    _ok("-32700" in out.getvalue(), "壞 JSON 未回 parse error")

    # ── 紀律一：唯讀 ───────────────────────────────────────────────────
    # 以動詞**前綴**判名（`list_amendments` 之 "amend" 為名詞，非寫入意圖——
    # 名稱子字串比對會誤殺，此即本專案 gate 反覆踩過之偽陽性型態）。
    write_verbs = ("write_", "edit_", "set_", "update_", "delete_", "patch_",
                   "apply_", "create_", "remove_", "amend_")
    _ok(not [n for n in server._DISPATCH if n.lower().startswith(write_verbs)],
        "出現疑似寫入類工具名——違反唯讀紀律")
    # 名稱不足為憑，另查實作層是否真有寫入操作（此為權威判準）。
    import ast
    tree = ast.parse(open(tools.__file__, encoding="utf-8").read())
    writes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if fname == "open":
            mode = next((kw.value for kw in node.keywords if kw.arg == "mode"), None)
            pos = node.args[1] if len(node.args) > 1 else None
            for m in (mode, pos):
                if isinstance(m, ast.Constant) and any(c in str(m.value) for c in "wax+"):
                    writes.append(f"open(mode={m.value!r}) @ line {node.lineno}")
        elif fname in ("remove", "unlink", "rmtree", "rename", "replace", "mkdir",
                       "makedirs", "chmod", "rmdir"):
            # 須為 os.*／shutil.* 之模組限定呼叫——`str.replace()` 為字串方法，
            # 以裸名比對即誤殺（本檢查初版即栽於此）。
            mod = getattr(getattr(node.func, "value", None), "id", None)
            if mod in ("os", "shutil", "pathlib"):
                writes.append(f"{mod}.{fname}() @ line {node.lineno}")
    _ok(not writes, f"tools.py 含寫入操作——違反唯讀紀律：{writes}")

    # ── 紀律二：合規檢查不快取（同檔連跑二次須各自實跑）──────────────
    calls = []
    orig = tools.compliance_lint.lint_spec

    def _spy(*a, **k):
        calls.append(a[0])
        return orig(*a, **k)

    tools.compliance_lint.lint_spec = _spy
    try:
        tools.lint_compliance("specs/AGENT-RUNTIME-SPECIFICATION.md")
        tools.lint_compliance("specs/AGENT-RUNTIME-SPECIFICATION.md")
    finally:
        tools.compliance_lint.lint_spec = orig
    _ok(len(calls) == 2, f"lint_compliance 疑似快取——二次呼叫僅實跑 {len(calls)} 次")

    # ── 紀律三：附出處（file:line）──────────────────────────────────────
    t = tools.get_clause("P4.E1")
    _ok("META-CONSTITUTION.md:" in t, "get_clause 未附 file:line 出處")
    _ok("Knowledge 五元組" in t, "get_clause 未回原文括號名")
    t = tools.get_spec_clause("WM.44")
    _ok(".md:" in t and "specs/" in t, "get_spec_clause 未附出處")

    # 憲章條款宇宙補齊之四核心定義須可取（B3 教訓）
    for code in ("§2.5", "§2.6", "§2.7", "§2.10"):
        try:
            tools.get_clause(code)
        except tools.ToolError:
            _FAILS.append(f"核心定義 {code} 不在條款宇宙——B3 迴歸")

    # ── 紀律四：失敗發聲（不靜默回近似答案）────────────────────────────
    for bad, fn in (("P9.E9", tools.get_clause), ("ZZ.99", tools.get_spec_clause)):
        try:
            fn(bad)
            _FAILS.append(f"{fn.__name__}({bad}) 未發聲即回值")
        except tools.ToolError:
            pass
    try:
        tools.lint_compliance("specs/NO-SUCH-FILE.md")
        _FAILS.append("lint_compliance 對不存在檔案未發聲")
    except tools.ToolError:
        pass

    # 經協定層之錯誤須帶 isError（非偽裝成正常結果）
    r = _rpc([{"jsonrpc": "2.0", "id": 3, "method": "tools/call",
               "params": {"name": "get_clause", "arguments": {"code": "P9.E9"}}}])
    _ok(r[0]["result"].get("isError") is True, "工具錯誤未標 isError")
    r = _rpc([{"jsonrpc": "2.0", "id": 4, "method": "tools/call",
               "params": {"name": "no_such_tool", "arguments": {}}}])
    _ok(r[0]["result"].get("isError") is True, "未知工具未標 isError")

    # ── 功能面 ──────────────────────────────────────────────────────────
    s = tools.search_clauses("Evidence", 5)
    _ok("命中" in s, "search_clauses 未回命中摘要")
    try:
        tools.search_clauses("zzz不存在之詞zzz")
        _FAILS.append("search_clauses 無命中時未發聲")
    except tools.ToolError:
        pass

    st = tools.layer_status()
    _ok(st.count("| ") >= 7, "layer_status 未列滿七份生效規格")
    _ok("META-CONSTITUTION.md" in st, "layer_status 未載 MC")

    _ok("出處：" in tools.get_ruling("2026-002"), "get_ruling 未附出處")
    try:
        tools.get_ruling("2099-999")
        _FAILS.append("get_ruling 對不存在裁決未發聲")
    except tools.ToolError:
        pass
    _ok("AL-" in tools.list_amendments(3), "list_amendments 未回 AL 條目")

    if _FAILS:
        print(f"constitution-mcp selftest: FAIL（{len(_FAILS)}）")
        for m in _FAILS:
            print(f"  ✗ {m}")
        return 1
    print("constitution-mcp selftest: OK")
    return 0
