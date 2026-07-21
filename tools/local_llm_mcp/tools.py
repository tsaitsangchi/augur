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

_PROVENANCE = "(local model: {model} @ {host})"
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


def _ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen3:4b")


def _stub_enabled() -> bool:
    return os.getenv("LOCAL_LLM_MCP_STUB", "").lower() in ("1", "true", "yes")


def _generate(prompt: str) -> str:
    """對 Ollama 送一趟推論。失敗發聲（拋 LocalLLMError），不靜默降級。"""
    if _stub_enabled():
        return "STUB:" + prompt[:200].replace("\n", " ")

    url = _ollama_url() + "/api/generate"
    body = json.dumps(
        {"model": _ollama_model(), "prompt": prompt, "stream": False}
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:  # 可達但回錯（如 404 模型不存在）——須與「不可達」區分
        detail = ""
        try:
            detail = exc.read().decode(errors="replace")[:200]
        except Exception:
            pass
        raise LocalLLMError(
            f"Ollama 回 HTTP {exc.code}（模型是否已 pull？OLLAMA_MODEL={_ollama_model()}）：{detail}"
        ) from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise LocalLLMError(f"Ollama 不可達（{_ollama_url()}）：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise LocalLLMError(f"Ollama 回應非 JSON：{exc}") from exc

    text = (data.get("response") or "").strip()
    if not text:
        raise LocalLLMError("Ollama 回應為空")
    return text


def _decorate(text: str) -> str:
    prov = _PROVENANCE.format(model=_ollama_model(), host=_ollama_url())
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
