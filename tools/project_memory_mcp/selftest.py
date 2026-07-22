"""project-memory-mcp selftest —— 純 stdlib，stub 嵌入（無須 Ollama）即可跑。

比照 constitution-mcp/local-llm-mcp 之紀律：凡計畫所宣稱之性質，皆有對應斷言。
涵蓋：協定層、切塊、治理排除判準、should_index denylist、讀寫分離（AST/文本掃描：
唯讀模組無寫入 SQL/檔案寫入、寫入僅在 index.py）、端到端建索引→recall→memory_status、
陳舊發聲、失敗發聲（索引不存在）。
"""
from __future__ import annotations

import ast
import os
import pathlib
import re
import tempfile
from contextlib import contextmanager

from . import chunk, govern, recall, server, store

_PKG = pathlib.Path(__file__).resolve().parent

_READONLY_MODULES = {
    "__init__.py", "server.py", "recall.py", "store.py",
    "embed.py", "chunk.py", "govern.py",
}
_WRITER_MODULE = "index.py"

_WRITE_SQL = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|REPLACE|ALTER)\b")
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
    _assert(names == ["recall", "memory_status"], f"工具清單不符：{names}")
    _assert(server.handle({"method": "notifications/initialized"}) is None, "通知不回應")
    err = server.handle({"jsonrpc": "2.0", "id": 3, "method": "nope"})
    _assert(err["error"]["code"] == -32601, "未知方法回 -32601")


def _test_chunk() -> None:
    text = "# A\nline a1\nline a2\n\n# B\nline b1\n"
    pieces = chunk.chunk_text(text)
    _assert(len(pieces) == 2, f"應切成 2 塊（依標題），得 {len(pieces)}")
    (s1, e1, b1), (s2, e2, b2) = pieces
    _assert(s1 == 1 and "A" in b1, "第一塊起於第 1 行且含標題 A")
    _assert(s2 == 5, f"第二塊應起於第 5 行，得 {s2}")


def _test_governance_exclusion() -> None:
    R = govern.REPO
    _assert(govern.is_governance_path(R / "constitution/META-CONSTITUTION.md"), "MC 為治理")
    _assert(govern.is_governance_path(R / "constitution/RULING-2026-010-x.md"), "RULING 為治理")
    _assert(govern.is_governance_path(R / "specs/IDENTITY-SPECIFICATION.md"), "生效規格為治理")
    _assert(not govern.is_governance_path(R / "specs/IDENTITY-SPECIFICATION-v0.1-draft.md"), "草案非治理")
    _assert(not govern.is_governance_path(R / "reports/PROJECT-MEMORY-MCP-PLAN.md"), "reports 非治理")
    # should_index：治理權威語料一律不索引
    _assert(not govern.should_index(R / "constitution/META-CONSTITUTION.md"), "治理不索引")
    _assert(not govern.should_index(R / "specs/IDENTITY-SPECIFICATION.md"), "生效規格不索引")


def _test_should_index_denylist() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "a.md").write_text("hi", encoding="utf-8")
        (root / ".env").write_text("SECRET=1", encoding="utf-8")
        (root / "b.bin").write_text("x", encoding="utf-8")
        (root / ".git").mkdir()
        (root / ".git" / "c.md").write_text("hidden", encoding="utf-8")
        _assert(govern.should_index(root / "a.md", root=root), ".md 應索引")
        _assert(not govern.should_index(root / ".env", root=root), ".env 不索引")
        _assert(not govern.should_index(root / "b.bin", root=root), "二進位副檔名不索引")
        _assert(not govern.should_index(root / ".git" / "c.md", root=root), ".git 內不索引")


def _test_read_write_separation() -> None:
    """讀寫分離：唯讀模組無寫入 SQL/檔案寫入；寫入僅存在於 index.py（正控）。"""
    for py in _PKG.glob("*.py"):
        if py.name not in _READONLY_MODULES:
            continue
        src = py.read_text(encoding="utf-8")
        m = _WRITE_SQL.search(src)
        _assert(m is None, f"唯讀模組 {py.name} 出現寫入 SQL：{m.group(0) if m else ''}")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in _WRITE_ATTRS:
                    raise AssertionError(f"{py.name} 出現檔案寫入呼叫：.{func.attr}(")
                if isinstance(func, ast.Name) and func.id == "open":
                    mode = ""
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        mode = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                    if any(c in mode for c in "wax+"):
                        raise AssertionError(f"{py.name} 出現寫入 open(mode={mode!r})")
    # 正控：寫入端確實含寫入 SQL（否則掃描形同虛設）
    idx_src = (_PKG / _WRITER_MODULE).read_text(encoding="utf-8")
    _assert(_WRITE_SQL.search(idx_src) is not None, "index.py 應含寫入 SQL（正控）")
    # server 不得匯入 index（讀寫分離之靜態保證）
    srv_src = (_PKG / "server.py").read_text(encoding="utf-8")
    _assert("import index" not in srv_src and "from . import index" not in srv_src, "server 不得匯入 index")
    # store 以唯讀模式開連線
    _assert("mode=ro" in (_PKG / "store.py").read_text(encoding="utf-8"), "store 應以 mode=ro 連線")


def _test_end_to_end_stub() -> None:
    from . import index  # 寫入端；僅測試/CLI 匯入，不被 server 匯入
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "notes.md").write_text(
            "# Alpha\nquick brown fox\n\n# Beta\ndatabase migration plan for postgres\n",
            encoding="utf-8",
        )
        (root / "exact.md").write_text("unique marker sentence zzz", encoding="utf-8")
        (root / ".env").write_text("SECRET=nope", encoding="utf-8")
        dbp = str(root / "idx.db")

        with _env(PROJECT_MEMORY_MCP_STUB="1", MEMORY_DB=dbp):
            stats = index.build(root=str(root), db=dbp)
            _assert(stats["mode"] == "full", f"首次無 DB 應全量，得 {stats['mode']}")
            _assert(stats["files"] == 2, f"應索引 2 檔（.env 排除），得 {stats['files']}")
            _assert(stats["chunks"] >= 3, f"chunk 數應 >=3，得 {stats['chunks']}")
            _assert(store.has_fts(dbp), "新建索引應含 FTS5")

            # semantic：以與某 chunk 完全相同之字串查詢 → stub 向量相同 → cosine≈1、居首
            out = recall.recall("unique marker sentence zzz", k=3, db=dbp, mode="semantic")
            _assert("exact.md" in out, "recall 應命中 exact.md")
            _assert("[I]" in out, "recall 結果應標 [I]")
            _assert("sem=1.000" in out, f"完全相同查詢應 sem=1.000：\n{out}")

            # keyword：精確 token 應靠 FTS 命中
            kw = recall.recall("zzz", k=3, db=dbp, mode="keyword")
            _assert("exact.md" in kw, f"keyword 應命中 exact.md：\n{kw}")
            _assert("kw=" in kw, f"keyword 模式應標 kw=：\n{kw}")

            # hybrid 預設 + 結構化 API
            hits = recall.recall_hits("unique marker sentence zzz", k=3, db=dbp, mode="hybrid")
            _assert(hits and hits[0]["path"] == "exact.md", f"hybrid hits 應以 exact.md 居首：{hits}")
            _assert(hits[0]["score_kind"] == "rrf", "hybrid score_kind 應為 rrf")
            hyb = recall.recall("unique marker sentence zzz", k=3, db=dbp)
            _assert("mode=hybrid" in hyb and "rrf=" in hyb, f"預設 hybrid 格式：\n{hyb}")
            _assert("[I]" in hyb, "瘦身後仍須保留 [I]")

            # load_all 行程內快取：連續兩次 semantic hits → 第二次 hit
            store.clear_cache()
            _ = recall.recall_hits("unique marker sentence zzz", k=2, db=dbp, mode="semantic")
            miss1 = store.cache_stats()["misses"]
            hit0 = store.cache_stats()["hits"]
            _ = recall.recall_hits("unique marker sentence zzz", k=2, db=dbp, mode="semantic")
            _assert(store.cache_stats()["misses"] == miss1, "第二次不應再 miss")
            _assert(store.cache_stats()["hits"] == hit0 + 1, "第二次應 cache hit")

            # mtime 變更後失效：touch DB 檔
            import time
            os.utime(dbp, None)
            time.sleep(0.01)
            os.utime(dbp, (time.time() + 1, time.time() + 1))
            _ = recall.recall_hits("unique marker sentence zzz", k=1, db=dbp, mode="semantic")
            _assert(store.cache_stats()["misses"] == miss1 + 1, "mtime 變後應 miss")

            # scope 過濾
            scoped = recall.recall("quick brown fox", k=5, scope="notes", db=dbp, mode="semantic")
            _assert("exact.md" not in scoped, "scope=notes 應排除 exact.md")

            # memory_status：新鮮
            st = recall.memory_status(db=dbp, root=str(root))
            _assert("chunk 數：" in st and "新鮮" in st, f"應報新鮮：\n{st}")
            _assert("fts：yes" in st, f"應報 fts：yes：\n{st}")

            # 陳舊發聲：改動來源檔後應偵測
            (root / "exact.md").write_text("changed content now", encoding="utf-8")
            st2 = recall.memory_status(db=dbp, root=str(root))
            _assert("過時" in st2 and "exact.md" in st2, f"應偵測 exact.md 過時：\n{st2}")


def _test_incremental_stub() -> None:
    """增量：改檔 updated、刪檔 removed、--full 仍可用。"""
    from . import index

    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "keep.md").write_text("alpha keep content stable", encoding="utf-8")
        (root / "edit.md").write_text("beta original wording", encoding="utf-8")
        (root / "gone.md").write_text("gamma will be deleted", encoding="utf-8")
        dbp = str(root / "idx.db")

        with _env(PROJECT_MEMORY_MCP_STUB="1", MEMORY_DB=dbp):
            s0 = index.build(root=str(root), db=dbp)
            _assert(s0["mode"] == "full" and s0["files"] == 3, f"首次全量 3 檔：{s0}")

            # 無變更 → 全 skip
            s1 = index.build(root=str(root), db=dbp)
            _assert(s1["mode"] == "incremental", f"應增量：{s1}")
            _assert(s1["skipped"] == 3 and s1["updated"] == 0 and s1["added"] == 0, f"全 skip：{s1}")

            # 改一檔
            (root / "edit.md").write_text(
                "beta revised uniquephrase999 wording", encoding="utf-8"
            )
            s2 = index.build(root=str(root), db=dbp)
            _assert(s2["updated"] == 1 and s2["skipped"] == 2, f"更新一檔：{s2}")
            out = recall.recall("uniquephrase999", k=3, db=dbp, mode="keyword")
            _assert("edit.md" in out, f"增量後 keyword 應命中新內容：\n{out}")

            # 刪一檔
            (root / "gone.md").unlink()
            s3 = index.build(root=str(root), db=dbp)
            _assert(s3["removed"] == 1 and s3["files"] == 2, f"刪檔：{s3}")
            gone = recall.recall("gamma will be deleted", k=5, db=dbp, mode="keyword")
            _assert("gone.md" not in gone, f"刪後不應命中 gone.md：\n{gone}")

            # full 重建
            s4 = index.build(root=str(root), db=dbp, full=True)
            _assert(s4["mode"] == "full" and s4["files"] == 2, f"full：{s4}")
            _assert(store.has_fts(dbp), "full 後仍有 FTS")


def _test_fail_loud_missing_fts() -> None:
    """缺 FTS 的舊索引：hybrid/keyword 須 fail-loud，不靜默退回 semantic。"""
    import sqlite3

    with tempfile.TemporaryDirectory() as d:
        dbp = str(pathlib.Path(d) / "legacy.db")
        conn = sqlite3.connect(dbp)
        conn.executescript(
            """
            CREATE TABLE chunks (
                id INTEGER PRIMARY KEY, path TEXT, start_line INTEGER, end_line INTEGER,
                hash TEXT, text TEXT, summary TEXT, vector BLOB, dim INTEGER, model TEXT, mtime REAL
            );
            CREATE TABLE files (path TEXT PRIMARY KEY, hash TEXT, mtime REAL, chunk_count INTEGER);
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
            """
        )
        conn.close()
        try:
            recall.recall("x", db=dbp, mode="hybrid")
            raise AssertionError("缺 FTS 之 hybrid 應拋 RecallError")
        except recall.RecallError as exc:
            _assert("FTS5" in str(exc) or "chunks_fts" in str(exc), f"錯誤應點名 FTS：{exc}")


def _test_fail_loud_missing_index() -> None:
    """失敗發聲：索引不存在 → RecallError / isError，不靜默回空。"""
    missing = "/nonexistent/__no_such_index__.db"
    try:
        recall.recall("x", db=missing)
        raise AssertionError("索引不存在應拋 RecallError")
    except recall.RecallError:
        pass
    with _env(MEMORY_DB=missing, PROJECT_MEMORY_MCP_STUB="1"):
        r = server.call_tool("recall", {"query": "x"})
        _assert(r.get("isError"), "索引不存在經 server 應 isError")
        r2 = server.call_tool("memory_status", {})
        _assert(r2.get("isError"), "memory_status 索引不存在應 isError")


def run() -> int:
    _test_protocol()
    _test_chunk()
    _test_governance_exclusion()
    _test_should_index_denylist()
    _test_read_write_separation()
    _test_end_to_end_stub()
    _test_incremental_stub()
    _test_fail_loud_missing_index()
    _test_fail_loud_missing_fts()
    print("project-memory-mcp selftest: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
