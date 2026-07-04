"""本機檔多格式文字抽取器(admin 控制台 `+資料夾` 核心,計畫 §三)— 純規則、零 LLM/零 API。

🎯 這支在做什麼(白話):把本機任意副檔名檔案抽出**逐字文字**(不摘要、不改寫、不杜撰),
   供知識層切句/嵌入/檢索。每格式一個抽取器;抽不出(未知/二進位/損壞/加密/超大)= **誠實跳過並分類記數**,
   絕不硬湊內容(#1 逐字 · #15 誠實)。惡意檔防護:大小上限(防 OOM)、符號連結不跟(防逃逸)、
   解析例外吞為 skip(防單檔崩整批)。
守 #1(逐字、禁 AI 生成/改寫)· #15(抽不出誠實跳過、不杜撰)· #5(惡意檔/大小/符號連結防護)· #29。

執行指令矩陣(本檔=library;CLI 見 scripts/acquire_local_files.py):
  python -c "from augur.knowledge.fileparse import extract_text; print(extract_text('X.pdf'))"
"""
from __future__ import annotations

import os

MAX_BYTES = 50 * 1024 * 1024      # 單檔上限 50MB(防 OOM/zip bomb 解壓;超過=oversize skip)
_TEXT_EXT = {".txt", ".md", ".markdown", ".csv", ".tsv", ".log", ".json", ".xml",
             ".yaml", ".yml", ".rst", ".ini", ".toml",
             ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".sh", ".sql", ".r"}
# skip 分類(誠實記數,計畫 §三):
SKIP = ("oversize", "symlink", "empty", "decode_error", "parse_error", "encrypted", "unknown_ext", "no_text")


def _read_text(path):
    """純文字檔:chardet 偵編碼、errors='replace' 兜底(仿 fetch_oa_fulltext 慣例)。"""
    raw = open(path, "rb").read()
    if not raw:
        return None, "empty"
    enc = "utf-8"
    try:
        import chardet
        d = chardet.detect(raw[:65536])
        enc = d.get("encoding") or "utf-8"
    except Exception:
        pass
    try:
        return raw.decode(enc, errors="replace"), "text"
    except Exception:
        return raw.decode("utf-8", errors="replace"), "text"


def _read_pdf(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    if getattr(r, "is_encrypted", False):
        return None, "encrypted"
    txt = "\n".join((p.extract_text() or "") for p in r.pages)
    return (txt, "pdf") if txt.strip() else (None, "no_text")   # 掃描檔無文字層 → no_text(P5 OCR)


def _read_docx(path):
    import docx
    d = docx.Document(path)
    txt = "\n".join(p.text for p in d.paragraphs)
    return (txt, "docx") if txt.strip() else (None, "no_text")


def extract_text(path):
    """回 (text|None, method_or_skipreason)。text 非 None = 抽取成功;None = 跳過(reason ∈ SKIP)。

    純規則、逐字;任何解析例外 → ('parse_error') 不外拋(單檔不崩整批,#5/#15)。"""
    try:
        if os.path.islink(path):
            return None, "symlink"                 # 不跟符號連結(防逃逸/迴圈)
        size = os.path.getsize(path)
        if size == 0:
            return None, "empty"
        if size > MAX_BYTES:
            return None, "oversize"
        ext = os.path.splitext(path)[1].lower()
        if ext in _TEXT_EXT:
            return _read_text(path)
        if ext == ".pdf":
            return _read_pdf(path)
        if ext == ".docx":
            return _read_docx(path)
        if ext in (".html", ".htm"):
            raw, st = _read_text(path)
            if not raw:
                return None, st
            try:
                import re
                import html as _html
                # stdlib 剝標(與 fetch_oa_fulltext.strip_html 同法、零依賴)
                t = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
                t = re.sub(r"(?s)<[^>]+>", " ", t)
                t = _html.unescape(t)
                t = re.sub(r"\s+\n", "\n", t)
                return (t, "html") if t.strip() else (None, "no_text")
            except Exception:
                return None, "parse_error"
        return None, "unknown_ext"                 # 二進位/未支援 → 誠實跳過(不杜撰)
    except Exception:
        return None, "parse_error"                 # 損壞/權限/解析崩 → skip(不崩整批)
