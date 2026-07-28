"""N9 檢索用查詢翻譯 — CJK 問句 → 英文檢索 query(translate-for-RETRIEVAL,非譯給閘)。

🎯 這支在做什麼(白話):augur 技術/財經文獻多為英文(solar_materials/chemistry/…),e5-small 對中文
   問句的跨語 kNN 會把英文正解沉在哲學/ERP 雜訊裡撈不上來。本檔先以**確定性 CJK→EN 詞表**
   （零 Ollama）組檢索 query；詞表未命中才用**本地 qwen3:4b**（非顧問 8b）譯一句英文檢索 query。
   呼叫端拿它另跑一趟英文嵌入檢索(見 advise():CJK 原文檢索無相關時才 fallback 到英文)。
   **譯文只作用於「檢索用哪個 query」**——不入庫、不當 citation、不進答案內容、不進 guard 誠實閘(命門)。

   **詞表 SSOT＝PostgreSQL `retrieve_glossary`(#29b)**：runtime 只讀表；新增詞對＝admin INSERT、零改碼。
   進程內 lru／列表快取；表空／連線失敗 → fail-closed 跳過詞表(走 LLM／None)。selftest 注入 fixture、零 IO。

   **failsafe 全程 fail-closed(#15):** 詞表未命中 ∧ (qwen3 OOM/逾時/回空/例外) → 回 None
   (絕不 raise、絕不讓翻譯失敗炸掉問答)。呼叫端收到 None → 只有原查詢結果(=誠實基線,多半 decline)。
   **無 CJK 的 query → 直接回 None**(英文問句本就英文檢索、不呼叫 qwen3、省 #28)。

   **know-how 產生禁領域 hardcode**：太陽能／第一性原理／物理／化學等變體一律走本通用路徑＋
   跨域檢索＋LLM 組答；不得為單題寫死 Q&A／if-domain 專支(NHC-PLAN／A0 驗收尺)。

守 #1(譯文非真兆、不入庫不入 citation)· #15(失敗誠實回 None、不佯稱)· #28(本地優先、零 usage)·
   #29b(策展映射住 DB)· #18(query_translation=領域名詞)。

執行指令矩陣(library;主路徑經 advise() 呼叫):
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \\
    print(t('太陽能電池導電漿料'))"              # → 詞表路徑 'conductive paste solar cell'(零 Ollama)
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \\
    print(t('what is margin of safety'))"        # → None(無 CJK,不譯)

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.query_translation              # 印用途+公開入口（唯讀）
  python -m augur.advisor.query_translation --selftest   # 純紅綠自測（零 IO;fixture 詞表）
"""
import os
from functools import lru_cache

from augur.advisor import ollama

_MAX_LEN = 200

# 進程快取：list[(src_cjk, tgt_en, require_cooccur)]；None＝尚未載入；()＝已載但空／失敗
_glossary_rows_cache = None

_PROMPT = (
    "You are a search-query translator. Translate the following Chinese search query "
    "into ONE concise, natural English search query suitable for retrieving academic and "
    "technical documents. Preserve technical terms and proper nouns. "
    "Output ONLY the English query on a single line — no quotes, no explanation, no preamble.\n\n"
    "Chinese: {q}\nEnglish:")


def _has_cjk(text):
    """含任一 CJK 字元 → True(確定性、零 ML;無 CJK 的 query 不需翻譯)。"""
    return any("一" <= ch <= "鿿" or "㐀" <= ch <= "䶿" for ch in text or "")


def _clean(out):
    """取模型輸出首個非空行、剝引號框、截長;空/過長/仍含 CJK(未真譯)→ None(fail-closed)。"""
    if not out:
        return None
    line = next((ln.strip() for ln in out.splitlines() if ln.strip()), "")
    line = line.strip("\"'“”「」『』 ")
    if not line or len(line) > _MAX_LEN or _has_cjk(line):
        return None
    return line


def reload_glossary(rows=None):
    """重載詞表快取。rows=None→下次從 DB 拉；rows=可迭代 fixture(零 IO selftest)。"""
    global _glossary_rows_cache
    translate_for_retrieval.cache_clear()
    if rows is None:
        _glossary_rows_cache = None
        return
    _glossary_rows_cache = tuple(
        (str(src), str(tgt), bool(co)) for src, tgt, co in rows
    )


def _fetch_glossary_from_db():
    """讀 active 列；失敗／無表 → ()(fail-closed)。"""
    try:
        from augur.core import db
        with db.connect() as conn:
            with db.transaction(conn) as cur:
                cur.execute(
                    "SELECT src_cjk, tgt_en, require_cooccur "
                    "FROM retrieve_glossary WHERE active "
                    "ORDER BY priority DESC, char_length(src_cjk) DESC"
                )
                return tuple((r[0], r[1], bool(r[2])) for r in cur.fetchall())
    except Exception:
        return ()


def _glossary_rows():
    """回 active 詞對 tuple；優先進程快取。"""
    global _glossary_rows_cache
    if _glossary_rows_cache is not None:
        return _glossary_rows_cache
    _glossary_rows_cache = _fetch_glossary_from_db()
    return _glossary_rows_cache


def _glossary_en_query(query, rows=None):
    """CJK 詞表 → 英文檢索 query;無夠強命中 → None。

    長詞優先、短詞不重複覆蓋；require_cooccur 列若為本輪唯一命中集合 → None(裸漿料)。
    rows 顯式傳入時不碰快取／DB(selftest／單元)。
    """
    q = query or ""
    glossary = list(rows) if rows is not None else list(_glossary_rows())
    if not glossary:
        return None
    # 長詞優先(同 priority 時以字長；DB 已 ORDER BY 但仍再排一次以支援 fixture)
    glossary.sort(key=lambda x: -len(x[0]))
    matched_zh, ens, co_flags = [], [], []
    for zh, en, co in glossary:
        if zh not in q:
            continue
        if any(zh in m for m in matched_zh):
            continue
        matched_zh.append(zh)
        ens.append(en)
        co_flags.append(co)
    if not ens:
        return None
    # 唯一命中集合 ⊆ require_cooccur → 過寬、不開英文檢索
    if all(co_flags):
        return None
    return " ".join(ens)


@lru_cache(maxsize=512)
def translate_for_retrieval(query, model=None, timeout=None):
    """CJK 檢索 query → 英文 query 字串(供嵌入檢索);無 CJK 或任何失敗 → None。

    query:   用戶問句(原文)
    model:   Ollama model tag(預設 OLLAMA_TRANSLATE_MODEL → qwen3:4b;勿預設顧問 8b)
    timeout: 單次翻譯秒數上限(預設 OLLAMA_TRANSLATE_TIMEOUT env → 60;譯句短、不需 900s)
    回:      英文 query(str)或 None(無 CJK / 詞表未中且 LLM 失敗——一律 fail-closed 回 None,絕不 raise)
    """
    q = (query or "").strip()
    if not q or not _has_cjk(q):
        return None
    gloss = _glossary_en_query(q)
    if gloss:
        return gloss
    tag = model or os.environ.get("OLLAMA_TRANSLATE_MODEL", "qwen3:4b")
    limit = float(timeout if timeout is not None
                  else os.environ.get("OLLAMA_TRANSLATE_TIMEOUT", 60.0))
    llm = ollama.make_llm_fn(model=tag, timeout=limit, retries=0, think=False,
                             options={"temperature": 0, "num_predict": 64})
    try:
        out = llm(_PROMPT.format(q=q))
    except Exception:
        return None
    return _clean(out)


# selftest 用種子(與 migrate SEED 對齊;僅 fixture、非 runtime SSOT)
_SELFTEST_SEED = (
    ("導電漿料", "conductive paste", False),
    ("正面銀漿", "front silver paste", False),
    ("背面鋁漿", "rear aluminum paste", False),
    ("銀漿", "silver paste", False),
    ("鋁漿", "aluminum paste", False),
    ("金屬化", "metallization", False),
    ("太陽能電池", "solar cell", False),
    ("多主柵", "multi busbar", False),
    ("鈣鈦礦", "perovskite", False),
    ("光伏", "photovoltaic", False),
    ("半導體", "semiconductor", False),
    ("矽晶", "silicon wafer", False),
    ("漿料", "paste", True),
)


def _selftest():
    """自測（零 IO：fixture 詞表；不連 DB、不觸 qwen3）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    reload_glossary(_SELFTEST_SEED)
    try:
        chk("_has_cjk 認 CJK / 拒英文", _has_cjk("鈣鈦礦") and not _has_cjk("perovskite"))
        chk("_has_cjk 空/None→False", not _has_cjk("") and not _has_cjk(None))
        chk("_clean 取首行剝引號", _clean('"Efficiency of perovskite"\n\n') == "Efficiency of perovskite")
        chk("_clean 空/含CJK/過長→None(fail-closed)",
            _clean("") is None and _clean("still 中文") is None and _clean("x" * (_MAX_LEN + 1)) is None)
        g_paste = _glossary_en_query("太陽能電池導電漿料")
        chk("詞表:導電漿料+太陽能電池",
            g_paste is not None and set(g_paste.split()) == {"conductive", "paste", "solar", "cell"})
        chk("詞表:裸漿料→None", _glossary_en_query("漿料是什麼") is None)
        g_ag = _glossary_en_query("正面銀漿金屬化") or ""
        chk("詞表:銀漿+金屬化", "silver paste" in g_ag and "metallization" in g_ag)
        import augur.advisor.query_translation as qt
        chk("模組無 _GLOSSARY SSOT", not hasattr(qt, "_GLOSSARY"))
        chk("空 fixture→None", _glossary_en_query("太陽能電池導電漿料", rows=()) is None)
        chk("translate 無 CJK→None(不觸 qwen3)",
            translate_for_retrieval("what is margin of safety") is None)
        chk("translate 空字串→None", translate_for_retrieval("") is None)
        t_paste = translate_for_retrieval("太陽能電池導電漿料")
        chk("translate 詞表路徑零 Ollama",
            t_paste is not None and set(t_paste.split()) == {"conductive", "paste", "solar", "cell"})
        # A0 探針：詞表未必命中；_glossary_en_query 不得 raise；不為探針加專支
        a0s = (
            "第一性原理在太陽能材料研發如何應用？",
            "依第一性原理列出在太陽能材料研發技術核心？",
            "依第一性原理列出在太陽能材料研發物理學技術核心？",
            "依第一性原理列出在太陽能材料研發在化學上技術核心？",
        )
        for a0 in a0s:
            try:
                _glossary_en_query(a0)
                a0_ok = True
            except Exception:
                a0_ok = False
            chk(f"A0 不崩:{a0[:12]}…", a0_ok)
        print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
        return 0 if ok else 1
    finally:
        reload_glossary(None)


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.query_translation --selftest;免 DB 免 API)")
