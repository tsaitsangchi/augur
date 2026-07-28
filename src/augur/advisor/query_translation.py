"""N9 檢索用查詢翻譯 — CJK 問句 → 英文檢索 query(translate-for-RETRIEVAL,非譯給閘)。

🎯 這支在做什麼(白話):augur 技術/財經文獻多為英文(solar_materials/chemistry/…),e5-small 對中文
   問句的跨語 kNN 會把英文正解沉在哲學/ERP 雜訊裡撈不上來。本檔先以**確定性 CJK→EN 詞表**
   （零 Ollama）組檢索 query；詞表未命中才用**本地 qwen3:4b**（非顧問 8b）譯一句英文檢索 query。
   呼叫端拿它另跑一趟英文嵌入檢索(見 advise():CJK 原文檢索無相關時才 fallback 到英文)。
   **譯文只作用於「檢索用哪個 query」**——不入庫、不當 citation、不進答案內容、不進 guard 誠實閘(命門)。

   **failsafe 全程 fail-closed(#15):** 詞表未命中 ∧ (qwen3 OOM/逾時/回空/例外) → 回 None
   (絕不 raise、絕不讓翻譯失敗炸掉問答)。呼叫端收到 None → 只有原查詢結果(=誠實基線,多半 decline)。
   **無 CJK 的 query → 直接回 None**(英文問句本就英文檢索、不呼叫 qwen3、省 #28)。

   **為何詞表優先＋4b**:弱機單飛時顧問 8b 佔滿 GPU，翻譯預設 8b＋60s 常逾時 → 假陰性 decline
   （庫內已有 silver paste／metallization 英文句卻回「知識庫中無此內容」）。詞表＝執行層品質工程
   （比照 relevance._EN_GENERIC／safe_general；安全仍繫於 relevance＋guard，非詞表鎖）。

   **確定性(#7):** lru_cache 快取譯文——同進程同 query 不重譯；詞表路徑本身確定性。

守 #1(譯文非真兆、不入庫不入 citation)· #15(失敗誠實回 None、不佯稱)· #28(本地優先、零 usage、
   無 CJK 不呼叫、僅 CJK 原文檢索失敗才觸發)· #18(query_translation=領域名詞)。

執行指令矩陣(library;主路徑經 advise() 呼叫):
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \
    print(t('太陽能電池導電漿料'))"              # → 詞表路徑 'conductive paste solar cell'(零 Ollama)
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \
    print(t('what is margin of safety'))"        # → None(無 CJK,不譯)

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.query_translation              # 印用途+公開入口（唯讀）
  python -m augur.advisor.query_translation --selftest   # 純紅綠自測（零 IO;無 CJK／詞表不觸 qwen3）
"""
import os
from functools import lru_cache

from augur.advisor import ollama

# 譯詞上限:檢索 query 不需長句;過長多為模型解釋離題(failsafe 一環,截斷而非放行)
_MAX_LEN = 200

# 確定性 CJK→EN 檢索詞(長詞優先;執行層品質工程、非 #29b 資料鎖)。只服務 retrieve query。
_GLOSSARY = (
    ("導電漿料", "conductive paste"),
    ("正面銀漿", "front silver paste"),
    ("背面鋁漿", "rear aluminum paste"),
    ("銀漿", "silver paste"),
    ("鋁漿", "aluminum paste"),
    ("金屬化", "metallization"),
    ("太陽能電池", "solar cell"),
    ("多主柵", "multi busbar"),
    ("鈣鈦礦", "perovskite"),
    ("光伏", "photovoltaic"),
    ("半導體", "semiconductor"),
    ("矽晶", "silicon wafer"),
    ("漿料", "paste"),  # 過寬:僅與其他域詞共現時才入組(見 _glossary_en_query)
)

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


def _glossary_en_query(query):
    """CJK 詞表 → 英文檢索 query;無夠強命中 → None(零 IO)。長詞優先、短詞不重複覆蓋。"""
    q = query or ""
    matched_zh, ens = [], []
    for zh, en in sorted(_GLOSSARY, key=lambda x: -len(x[0])):
        if zh not in q:
            continue
        if any(zh in m for m in matched_zh):          # 已被更長詞覆蓋(如 漿料⊂導電漿料)
            continue
        matched_zh.append(zh)
        ens.append(en)
    if not ens:
        return None
    if ens == ["paste"]:                              # 裸「漿料」過寬、不足單獨開英文檢索
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
        return None                                  # 無 CJK → 不呼叫 qwen3(省、#28)
    gloss = _glossary_en_query(q)
    if gloss:
        return gloss                                 # 詞表命中 → 零 Ollama、確定性(#28/#7)
    tag = model or os.environ.get("OLLAMA_TRANSLATE_MODEL", "qwen3:4b")
    limit = float(timeout if timeout is not None
                  else os.environ.get("OLLAMA_TRANSLATE_TIMEOUT", 60.0))
    # think=False:關 qwen3 推理段(弱機提速);temp=0:近確定;num_predict 小:譯句短、有界輸出
    llm = ollama.make_llm_fn(model=tag, timeout=limit, retries=0, think=False,
                             options={"temperature": 0, "num_predict": 64})
    try:
        out = llm(_PROMPT.format(q=q))
    except Exception:
        return None                                  # OOM(HTTP500/killed)/逾時/連線 → fail-closed(#15)
    return _clean(out)


def _selftest():
    """自測（零 IO：純測 _has_cjk/_clean/詞表與「無 CJK 早退回 None」不呼叫 qwen3 之不變式）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

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
    chk("translate 無 CJK→None(不觸 qwen3、零 IO 不變式)",
        translate_for_retrieval("what is margin of safety") is None)
    chk("translate 空字串→None", translate_for_retrieval("") is None)
    t_paste = translate_for_retrieval("太陽能電池導電漿料")
    chk("translate 詞表路徑零 Ollama",
        t_paste is not None and set(t_paste.split()) == {"conductive", "paste", "solar", "cell"})
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.query_translation --selftest;免 DB 免 API)")
