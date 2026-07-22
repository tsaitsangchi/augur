"""local-llm-mcp 工具實作：本地小模型之「濃縮型」子任務（大進小出）。

紀律（見 reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md §4.3、§二之二）：
  1. 來源標記強制 —— 每筆輸出前置 `(local model: ...)` 與治理警告。
  2. 失敗發聲 —— Ollama 不可達/空回應一律拋 LocalLLMError，不靜默回 stub。
  3. 路徑封閉 —— 檔案輸入僅允許 repo 根以內之相對路徑。
  4. 唯讀 —— 不提供任何寫入工具；對 Ollama 僅為唯讀推論呼叫。
  5. 治理語料排除 —— 對治理權威語料（constitution/、生效 specs/*-SPECIFICATION.md）
     之路徑拒絕執行並發聲，導向 constitution-mcp（非治理輔助專用之硬邊界）。

OLLAMA_URL / OLLAMA_MODEL 之預設與 augur_proxy.local_llm 一致（同一顆本地模型）。
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

_REPO = pathlib.Path(__file__).resolve().parents[2]

_PROVENANCE = "(local model: {model} @ {backend}:{host})"
_GOVERNANCE_WARNING = (
    "⚠ 本輸出為本地小模型生成，屬 [I] 輔助，不得原文貼入任何 [N] 治理文書。"
)


class LocalLLMError(Exception):
    """工具層錯誤——經協定層須帶 isError: true，不得偽裝成正常結果。"""


def _is_governance_path(resolved: pathlib.Path) -> bool:
    """治理權威語料判定（路徑前綴）。

    範圍：constitution/ 全域（MC、RULING-*、AMENDMENT-LOG.md、adoption-drafts）；
    specs/ 下之生效規格（檔名含 SPECIFICATION 且不含 -draft）。
    草案（-draft）屬非治理輔助語料，不在此列。
    """
    try:
        rel = resolved.relative_to(_REPO)
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return False
    if parts[0] == "constitution":
        return True
    if parts[0] == "specs":
        name = parts[-1]
        if "SPECIFICATION" in name.upper() and "-draft" not in name.lower():
            return True
    return False


def _llm_backend() -> str:
    """ollama（預設）｜openai（vLLM 等 OpenAI 相容）。"""
    raw = (os.getenv("LLM_BACKEND") or "ollama").strip().lower()
    if raw in ("openai", "vllm"):
        return "openai"
    return "ollama"


def _ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


def _openai_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")


def _openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "EMPTY")


def _default_model_for_host() -> str:
    """兩機硬體不同：依 hostname 選預設模型（可被 OLLAMA_MODEL／LLM_MODEL 覆寫）。

    aitopatom-b96e（GB10）→ qwen3-coder-next；DESKTOP-8MQPFS8（GTX1650）→ qwen3:4b。
    """
    import socket
    host = socket.gethostname()
    if host == "aitopatom-b96e":
        return "qwen3-coder-next"
    if host == "DESKTOP-8MQPFS8":
        return "qwen3:4b"
    return "qwen3:4b"


def _llm_model() -> str:
    """推論模型名：LLM_MODEL > OLLAMA_MODEL > hostname 預設。"""
    return os.getenv("LLM_MODEL") or os.getenv("OLLAMA_MODEL") or _default_model_for_host()


def _ollama_model() -> str:
    """相容舊名：同 _llm_model。"""
    return _llm_model()


def _endpoint_label() -> str:
    if _llm_backend() == "openai":
        return _openai_base_url()
    return _ollama_url()


def _default_num_ctx() -> int:
    """GB10 統一記憶體可容較大 KV；他機保守預設。可被 OLLAMA_NUM_CTX 覆寫。"""
    import socket
    host = socket.gethostname()
    if host == "aitopatom-b96e":
        return 32768
    return 8192


def _num_ctx() -> int:
    raw = os.getenv("OLLAMA_NUM_CTX")
    if raw is None or not str(raw).strip():
        return _default_num_ctx()
    try:
        return max(2048, min(int(raw), 131072))
    except (TypeError, ValueError):
        return _default_num_ctx()


def _stub_enabled() -> bool:
    return os.getenv("LOCAL_LLM_MCP_STUB", "").lower() in ("1", "true", "yes")


def _temperature() -> float | None:
    temp = os.getenv("OLLAMA_TEMPERATURE")
    if temp is None or not str(temp).strip():
        return None
    try:
        return float(temp)
    except (TypeError, ValueError):
        return None


def _generate_ollama(prompt: str, timeout: int) -> str:
    url = _ollama_url() + "/api/generate"
    options = {"num_ctx": _num_ctx()}
    t = _temperature()
    if t is not None:
        options["temperature"] = t
    body = json.dumps(
        {
            "model": _llm_model(),
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode(errors="replace")[:200]
        except Exception:
            pass
        raise LocalLLMError(
            f"Ollama 回 HTTP {exc.code}（模型是否已 pull？model={_llm_model()}）：{detail}"
        ) from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise LocalLLMError(f"Ollama 不可達（{_ollama_url()}）：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise LocalLLMError(f"Ollama 回應非 JSON：{exc}") from exc

    text = (data.get("response") or "").strip()
    if not text:
        raise LocalLLMError("Ollama 回應為空")
    return text


def _generate_openai(prompt: str, timeout: int) -> str:
    """vLLM 等 OpenAI 相容：POST /v1/chat/completions。"""
    url = _openai_base_url() + "/chat/completions"
    # 粗估：濃縮任務短輸出；可用 OPENAI_MAX_TOKENS 覆寫
    try:
        max_tokens = max(16, min(int(os.getenv("OPENAI_MAX_TOKENS", "1024")), 8192))
    except (TypeError, ValueError):
        max_tokens = 1024
    payload = {
        "model": _llm_model(),
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": max_tokens,
    }
    t = _temperature()
    if t is not None:
        payload["temperature"] = t
    body = json.dumps(payload).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_openai_api_key()}",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode(errors="replace")[:200]
        except Exception:
            pass
        raise LocalLLMError(
            f"OpenAI 相容後端回 HTTP {exc.code}（{_openai_base_url()} model={_llm_model()}）：{detail}"
        ) from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise LocalLLMError(
            f"OpenAI 相容後端不可達（{_openai_base_url()}）：{exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise LocalLLMError(f"OpenAI 相容回應非 JSON：{exc}") from exc

    try:
        text = (data["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LocalLLMError(f"OpenAI 相容回應缺 choices/message/content：{exc}") from exc
    if not text:
        raise LocalLLMError("OpenAI 相容回應為空")
    return text


def _generate(prompt: str, timeout: int = 180) -> str:
    """依 LLM_BACKEND 送一趟推論。失敗發聲，不靜默降級。"""
    if _stub_enabled():
        return "STUB:" + prompt[:200].replace("\n", " ")
    if _llm_backend() == "openai":
        return _generate_openai(prompt, timeout=timeout)
    return _generate_ollama(prompt, timeout=timeout)


def _decorate(text: str) -> str:
    prov = _PROVENANCE.format(
        model=_llm_model(),
        backend=_llm_backend(),
        host=_endpoint_label(),
    )
    return f"{prov}\n{_GOVERNANCE_WARNING}\n\n{text}"


def _resolve_source(text, path) -> str:
    """回傳待處理文本。text/path 需且僅需其一；path 封閉於 repo 內。"""
    if (text is None) == (path is None):
        raise LocalLLMError("需且僅需提供 text 或 path 其一")
    if text is not None:
        if not isinstance(text, str) or not text.strip():
            raise LocalLLMError("text 不可為空")
        return text

    if not isinstance(path, str) or not path.strip():
        raise LocalLLMError("path 不可為空")
    resolved = (_REPO / path).resolve()
    if not str(resolved).startswith(str(_REPO) + os.sep):
        raise LocalLLMError(f"路徑越界（僅允許 repo 內相對路徑）：{path}")
    if _is_governance_path(resolved):
        raise LocalLLMError(
            f"治理權威語料不做 LLM 濃縮（{path}）："
            "請經 constitution-mcp（get_clause／get_spec_clause）取精確原文。"
        )
    if not resolved.is_file():
        raise LocalLLMError(f"檔案不存在：{path}")
    return resolved.read_text(encoding="utf-8", errors="replace")


def local_summarize(text=None, path=None, max_sentences=5) -> str:
    """把長文/檔案濃縮成至多 N 句重點。大進小出。"""
    src = _resolve_source(text, path)
    try:
        n = max(1, min(int(max_sentences), 20))
    except (TypeError, ValueError):
        raise LocalLLMError("max_sentences 須為整數")
    prompt = (
        f"請用繁體中文，最多 {n} 句，精簡摘要以下內容的重點，只輸出摘要本身，"
        f"不要前言或結語：\n\n{src}"
    )
    return _decorate(_generate(prompt))


def local_extract(instruction, text=None, path=None) -> str:
    """依指示從長文/檔案抽取精簡結果（清單/欄位）。大進小出。"""
    if not isinstance(instruction, str) or not instruction.strip():
        raise LocalLLMError("instruction 不可為空")
    src = _resolve_source(text, path)
    prompt = (
        "依下列指示從內容中抽取資訊，只輸出抽取結果、不要多餘說明：\n"
        f"指示：{instruction}\n\n內容：\n{src}"
    )
    return _decorate(_generate(prompt))


def local_ask(prompt, max_words=200) -> str:
    """一般本地小模型問答，強制短輸出。適合可容忍小模型品質之輔助查詢。"""
    if not isinstance(prompt, str) or not prompt.strip():
        raise LocalLLMError("prompt 不可為空")
    try:
        w = max(1, min(int(max_words), 1000))
    except (TypeError, ValueError):
        raise LocalLLMError("max_words 須為整數")
    wrapped = f"請用繁體中文於 {w} 字以內回答，力求精簡：\n\n{prompt}"
    return _decorate(_generate(wrapped))


def local_research(
    query: str,
    k: int = 5,
    hops: int = 2,
    scope=None,
    max_sentences: int = 8,
) -> str:
    """多跳：project-memory hybrid recall → 擴 query 再檢 → 本地濃縮。

    跨包僅呼叫 recall_hits（唯讀）；不觸碰 index 寫入端。
    """
    if not isinstance(query, str) or not query.strip():
        raise LocalLLMError("query 不可為空")
    try:
        k = max(1, min(int(k), 20))
        hops = max(1, min(int(hops), 3))
        n = max(1, min(int(max_sentences), 20))
    except (TypeError, ValueError):
        raise LocalLLMError("k／hops／max_sentences 須為整數")

    try:
        from tools.project_memory_mcp import recall as mem_recall
    except ImportError as exc:
        raise LocalLLMError(f"無法載入 project_memory_mcp.recall：{exc}") from exc

    seen_ids = set()
    accumulated = []
    q = query.strip()
    try:
        for hop in range(hops):
            hits = mem_recall.recall_hits(q, k=k, scope=scope, mode="hybrid")
            new_hits = []
            for h in hits:
                # 縱深：治理 path 一律拒絕整次研究（不半套）
                resolved = (_REPO / h["path"]).resolve()
                if _is_governance_path(resolved):
                    raise LocalLLMError(
                        f"治理權威語料不得經 local_research 濃縮（{h['path']}）："
                        "請經 constitution-mcp 取精確原文。"
                    )
                cid = h.get("id")
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                new_hits.append(h)
                accumulated.append(h)
            if hop + 1 < hops and new_hits:
                q = mem_recall.expand_query_from_hits(query, new_hits)
            elif not new_hits and hop == 0 and not accumulated:
                break
    except mem_recall.RecallError as exc:
        raise LocalLLMError(f"project-memory 檢索失敗：{exc}") from exc

    if not accumulated:
        return _decorate(f"（local_research 查無相關片段；query={query!r} scope={scope!r}）")

    blocks = []
    for h in accumulated:
        loc = f"{h['path']}:{h['start_line']}-{h['end_line']}"
        body = (h.get("summary") or h.get("text") or "").strip()
        if len(body) > 800:
            body = body[:800] + " …"
        blocks.append(f"【{loc}】\n{body}")
    corpus = "\n\n".join(blocks)
    prompt = (
        f"你是程式庫研究助理。根據下列檢索片段，用繁體中文最多 {n} 句回答問題。"
        f"必須點名相關 path；不要臆造片段中沒有的事實。\n"
        f"問題：{query}\n\n片段：\n{corpus}"
    )
    body = _generate(prompt, timeout=300)
    header = f"[local_research hops={hops} k={k} hits={len(accumulated)}]"
    return _decorate(f"{header}\n{body}")


def local_map_reduce(paths, instruction: str, max_sentences: int = 8) -> str:
    """多檔 map-reduce 濃縮：每檔短摘要 → 依 instruction 合併。

    paths 上限 12；任一 path 越界／治理／缺失 → 整次失敗。
    """
    if not isinstance(instruction, str) or not instruction.strip():
        raise LocalLLMError("instruction 不可為空")
    if not isinstance(paths, (list, tuple)) or not paths:
        raise LocalLLMError("paths 須為非空陣列")
    if len(paths) > 12:
        raise LocalLLMError("paths 上限 12")
    try:
        n = max(1, min(int(max_sentences), 20))
    except (TypeError, ValueError):
        raise LocalLLMError("max_sentences 須為整數")

    map_parts = []
    for p in paths:
        if not isinstance(p, str) or not p.strip():
            raise LocalLLMError("paths 內每一項須為非空字串")
        src = _resolve_source(None, p.strip())
        # 過長檔截斷，避免單次 map 爆 context（仍受 num_ctx 保護）
        if len(src) > 24000:
            src = src[:24000] + "\n…(truncated)"
        map_prompt = (
            f"請用繁體中文最多 3 句摘要下列檔案重點，只輸出摘要：\n"
            f"檔案：{p}\n\n{src}"
        )
        summary = _generate(map_prompt, timeout=300)
        map_parts.append(f"### {p}\n{summary}")

    joined = "\n\n".join(map_parts)
    reduce_prompt = (
        f"依下列指示，把多檔 map 摘要合併成繁體中文最多 {n} 句，只輸出結果：\n"
        f"指示：{instruction}\n\n各檔摘要：\n{joined}"
    )
    reduced = _generate(reduce_prompt, timeout=300)
    header = f"[local_map_reduce files={len(paths)}]"
    return _decorate(f"{header}\n{reduced}")
