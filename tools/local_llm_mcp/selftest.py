"""local-llm-mcp selftest —— 純 stdlib，stub 模式（無須 Ollama）即可跑。

比照 constitution-mcp 之紀律：凡 README/計畫所宣稱之性質，皆有對應斷言。
涵蓋：協定層、三工具功能面與錯誤面、四項治理紀律（來源標記、失敗發聲、
路徑封閉、唯讀），其中「唯讀」以 AST 掃描實作層為權威判準。
"""
from __future__ import annotations

import ast
import os
import pathlib
from contextlib import contextmanager

from . import server, tools

_PKG = pathlib.Path(__file__).resolve().parent

# 明確的檔案系統寫入呼叫（stdout.write 串流寫入、str.replace 等非檔案系統副作用不列入，
# 以免誤報；os.rename/os.replace 之破壞性已由 remove/unlink/rmtree 等主要向量涵蓋）。
_WRITE_ATTRS = {
    "write_text", "write_bytes", "unlink", "rmtree", "remove", "rmdir",
    "mkdir", "makedirs", "touch",
}


@contextmanager
def _env(**kv):
    old = {k: os.environ.get(k) for k in kv}
    try:
        for k, v in kv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _test_protocol() -> None:
    init = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    _assert(init["result"]["protocolVersion"] == server.PROTOCOL_VERSION, "initialize 協定版本")

    listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = [t["name"] for t in listed["result"]["tools"]]
    _assert(names == ["local_summarize", "local_extract", "local_ask"], f"工具清單不符：{names}")
    _assert(all(n.startswith("local_") for n in names), "工具名前綴")

    _assert(server.handle({"method": "notifications/initialized"}) is None, "通知不回應")
    err = server.handle({"jsonrpc": "2.0", "id": 3, "method": "nope"})
    _assert(err["error"]["code"] == -32601, "未知方法回 -32601")


def _test_no_write_tool() -> None:
    """唯讀紀律：schema 無寫入工具，且實作層無檔案系統寫入呼叫（AST 權威判準）。"""
    for name in server._DISPATCH:
        _assert(name.startswith("local_"), f"非唯讀語義之工具名：{name}")

    for py in _PKG.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in _WRITE_ATTRS:
                    raise AssertionError(f"{py.name} 出現寫入呼叫：.{func.attr}(")
                if isinstance(func, ast.Name) and func.id == "open":
                    mode = ""
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        mode = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                    if any(c in mode for c in "wax+"):
                        raise AssertionError(f"{py.name} 出現寫入 open(mode={mode!r})")


def _test_provenance_and_governance() -> None:
    with _env(LOCAL_LLM_MCP_STUB="1"):
        out = tools.local_ask("測試", max_words=50)
    _assert("(local model:" in out, "缺來源標記")
    _assert("[N] 治理文書" in out, "缺治理警告")
    _assert("STUB:" in out, "stub 內容")


def _test_tools_stub() -> None:
    with _env(LOCAL_LLM_MCP_STUB="1"):
        s = tools.local_summarize(text="很長的一段內容。" * 20, max_sentences=3)
        _assert("(local model:" in s, "summarize 來源標記")

        r = server.call_tool("local_summarize", {"path": "README.md", "max_sentences": 2})
        _assert(not r.get("isError"), "以 repo 內檔案摘要應成功")

        e = server.call_tool("local_extract", {"instruction": "列出重點", "text": "abc"})
        _assert(not e.get("isError"), "extract 應成功")


def _test_error_faces() -> None:
    with _env(LOCAL_LLM_MCP_STUB="1"):
        # 路徑封閉：越界
        r = server.call_tool("local_summarize", {"path": "../etc/passwd"})
        _assert(r.get("isError"), "越界路徑應 isError")
        # text 與 path 同時給
        r = server.call_tool("local_summarize", {"text": "x", "path": "README.md"})
        _assert(r.get("isError"), "text/path 同時給應 isError")
        # 空 prompt
        r = server.call_tool("local_ask", {"prompt": "   "})
        _assert(r.get("isError"), "空 prompt 應 isError")
        # 不存在檔案
        r = server.call_tool("local_extract", {"instruction": "x", "path": "no_such_file.xyz"})
        _assert(r.get("isError"), "不存在檔案應 isError")


def _test_fail_loud() -> None:
    """失敗發聲：Ollama 不可達須拋錯（isError），不靜默回 stub。"""
    with _env(LOCAL_LLM_MCP_STUB=None, OLLAMA_URL="http://127.0.0.1:1"):
        r = server.call_tool("local_ask", {"prompt": "hi", "max_words": 10})
    _assert(r.get("isError"), "Ollama 不可達應 isError")
    _assert("不可達" in r["content"][0]["text"], "錯誤訊息應指明不可達")


def run() -> int:
    _test_protocol()
    _test_no_write_tool()
    _test_provenance_and_governance()
    _test_tools_stub()
    _test_error_faces()
    _test_fail_loud()
    print("local-llm-mcp selftest: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
