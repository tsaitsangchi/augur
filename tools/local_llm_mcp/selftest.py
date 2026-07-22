"""local-llm-mcp selftest —— 純 stdlib，stub 模式（無須 Ollama）即可跑。

比照 constitution-mcp 之紀律：凡 README/計畫所宣稱之性質，皆有對應斷言。
涵蓋：協定層、三工具功能面與錯誤面、五項治理紀律（來源標記、失敗發聲、
路徑封閉、唯讀、治理語料排除），其中「唯讀」以 AST 掃描實作層為權威判準。
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
    expect = [
        "local_summarize",
        "local_extract",
        "local_ask",
        "local_research",
        "local_map_reduce",
    ]
    _assert(names == expect, f"工具清單不符：{names}")
    _assert(all(n.startswith("local_") for n in names), "工具名前綴")

    _assert(server.handle({"method": "notifications/initialized"}) is None, "通知不回應")
    err = server.handle({"jsonrpc": "2.0", "id": 3, "method": "nope"})
    _assert(err["error"]["code"] == -32601, "未知方法回 -32601")


def _test_no_write_tool() -> None:
    """唯讀紀律：schema 無寫入工具，且實作層無檔案系統寫入呼叫（AST 權威判準）。"""
    for name in server._DISPATCH:
        _assert(name.startswith("local_"), f"非唯讀語義之工具名：{name}")

    skip = {"selftest.py"}  # 測試夾具可寫暫存；不屬實作層
    for py in _PKG.glob("*.py"):
        if py.name in skip:
            continue
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


def _test_host_default_model() -> None:
    """兩機模型預設：依 hostname（可被 LLM_MODEL／OLLAMA_MODEL 覆寫）。"""
    with _env(OLLAMA_MODEL=None, LLM_MODEL=None):
        m = tools._ollama_model()
        _assert(isinstance(m, str) and len(m) > 0, "預設模型應非空")
    with _env(OLLAMA_MODEL="explicit-test-model", LLM_MODEL=None):
        _assert(tools._ollama_model() == "explicit-test-model", "OLLAMA_MODEL 應覆寫 hostname 預設")
    with _env(OLLAMA_MODEL="ollama-fallback", LLM_MODEL="llm-wins"):
        _assert(tools._llm_model() == "llm-wins", "LLM_MODEL 應優先於 OLLAMA_MODEL")
    with _env(OLLAMA_NUM_CTX="4096"):
        _assert(tools._num_ctx() == 4096, "OLLAMA_NUM_CTX 應覆寫")
    with _env(OLLAMA_NUM_CTX=None):
        ctx = tools._num_ctx()
        _assert(isinstance(ctx, int) and ctx >= 2048, f"預設 num_ctx 應合理：{ctx}")
    with _env(LLM_BACKEND=None):
        _assert(tools._llm_backend() == "ollama", "LLM_BACKEND 預設 ollama")
    with _env(LLM_BACKEND="vllm"):
        _assert(tools._llm_backend() == "openai", "vllm 別名應正規化為 openai")


def _test_dual_backend_stub() -> None:
    """stub 下兩後端皆不碰網；provenance 含 backend:host。"""
    with _env(
        LOCAL_LLM_MCP_STUB="1",
        LLM_BACKEND="ollama",
        OLLAMA_URL="http://127.0.0.1:11434",
        LLM_MODEL="stub-ollama-model",
    ):
        out = tools.local_ask("測試 ollama", max_words=50)
        _assert("(local model: stub-ollama-model @ ollama:http://127.0.0.1:11434)" in out, f"ollama provenance：\n{out}")
        _assert("STUB:" in out, "ollama stub 不應碰網")

    with _env(
        LOCAL_LLM_MCP_STUB="1",
        LLM_BACKEND="openai",
        OPENAI_BASE_URL="http://127.0.0.1:8000/v1",
        LLM_MODEL="stub-openai-model",
    ):
        out2 = tools.local_ask("測試 openai", max_words=50)
        _assert(
            "(local model: stub-openai-model @ openai:http://127.0.0.1:8000/v1)" in out2,
            f"openai provenance：\n{out2}",
        )
        _assert("STUB:" in out2, "openai stub 不應碰網")


def _test_provenance_and_governance() -> None:
    with _env(LOCAL_LLM_MCP_STUB="1", LLM_BACKEND="ollama"):
        out = tools.local_ask("測試", max_words=50)
    _assert("(local model:" in out, "缺來源標記")
    _assert(" @ ollama:" in out, "provenance 缺 backend:host")
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


def _test_map_reduce_and_research_stub() -> None:
    """map-reduce／research：stub 下功能面 + 治理拒絕。"""
    import tempfile
    from tools.project_memory_mcp import index as mem_index

    with _env(LOCAL_LLM_MCP_STUB="1"):
        mr = server.call_tool(
            "local_map_reduce",
            {
                "paths": ["README.md", "tools/local_llm_mcp/README.md"],
                "instruction": "各一句總結",
                "max_sentences": 4,
            },
        )
        _assert(not mr.get("isError"), f"map_reduce 應成功：{mr}")
        text = mr["content"][0]["text"]
        _assert("(local model:" in text and "local_map_reduce" in text, f"map_reduce 標記：\n{text}")

        bad = server.call_tool(
            "local_map_reduce",
            {
                "paths": ["constitution/META-CONSTITUTION.md", "README.md"],
                "instruction": "x",
            },
        )
        _assert(bad.get("isError"), "含治理 path 之 map_reduce 應 isError")
        _assert("constitution-mcp" in bad["content"][0]["text"], "應導向 constitution-mcp")

    # 臨時 root 建索引：path 為相對名；governance 以 REPO/rel 判定，一般非治理。
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "notes.md").write_text(
            "# Research\nentity registry backfill lifecycle retire\n",
            encoding="utf-8",
        )
        dbp = str(root / "idx.db")
        with _env(
            LOCAL_LLM_MCP_STUB="1",
            PROJECT_MEMORY_MCP_STUB="1",
            MEMORY_DB=dbp,
        ):
            mem_index.build(root=str(root), db=dbp)
            out = tools.local_research(
                "entity registry backfill", k=3, hops=2, max_sentences=5
            )
            _assert("(local model:" in out, "research 來源標記")
            _assert("local_research" in out, "research 標頭")
            _assert(
                "STUB:" in out or "查無相關" in out or "notes.md" in out,
                f"research 內容：\n{out}",
            )

            r = server.call_tool(
                "local_research",
                {"query": "entity registry", "k": 2, "hops": 1},
            )
            _assert(not r.get("isError"), f"local_research server 應成功：{r}")


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


def _test_governance_exclusion() -> None:
    """治理語料排除：治理權威路徑拒絕並發聲；非治理路徑不被誤擋（路徑前綴判準）。"""
    _REPO = pathlib.Path(tools.__file__).resolve().parents[2]

    # 判準單元：正例（治理權威）
    _assert(tools._is_governance_path(_REPO / "constitution/META-CONSTITUTION.md"), "MC 應判為治理")
    _assert(tools._is_governance_path(_REPO / "constitution/RULING-2026-010-x.md"), "RULING 應判為治理")
    _assert(tools._is_governance_path(_REPO / "specs/IDENTITY-SPECIFICATION.md"), "生效規格應判為治理")
    # 判準單元：反例（非治理輔助）
    _assert(not tools._is_governance_path(_REPO / "specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md"), "草案非治理")
    _assert(not tools._is_governance_path(_REPO / "reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md"), "reports 非治理")
    _assert(not tools._is_governance_path(_REPO / "README.md"), "README 非治理")

    # 整合面：治理路徑經工具呼叫須 isError 並導向 constitution-mcp
    with _env(LOCAL_LLM_MCP_STUB="1"):
        r = server.call_tool("local_summarize", {"path": "constitution/META-CONSTITUTION.md"})
    _assert(r.get("isError"), "治理路徑應 isError")
    _assert("constitution-mcp" in r["content"][0]["text"], "錯誤訊息應導向 constitution-mcp")


def _test_fail_loud() -> None:
    """失敗發聲：Ollama／openai 不可達須拋錯（isError），不靜默回 stub。"""
    with _env(LOCAL_LLM_MCP_STUB=None, LLM_BACKEND="ollama", OLLAMA_URL="http://127.0.0.1:1"):
        r = server.call_tool("local_ask", {"prompt": "hi", "max_words": 10})
    _assert(r.get("isError"), "Ollama 不可達應 isError")
    _assert("不可達" in r["content"][0]["text"], "錯誤訊息應指明不可達")

    with _env(
        LOCAL_LLM_MCP_STUB=None,
        LLM_BACKEND="openai",
        OPENAI_BASE_URL="http://127.0.0.1:1/v1",
    ):
        r2 = server.call_tool("local_ask", {"prompt": "hi", "max_words": 10})
    _assert(r2.get("isError"), "openai 死埠應 isError")
    _assert("不可達" in r2["content"][0]["text"], "openai 錯誤應指明不可達")


def run() -> int:
    _test_protocol()
    _test_no_write_tool()
    _test_host_default_model()
    _test_dual_backend_stub()
    _test_provenance_and_governance()
    _test_tools_stub()
    _test_map_reduce_and_research_stub()
    _test_error_faces()
    _test_governance_exclusion()
    _test_fail_loud()
    print("local-llm-mcp selftest: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
