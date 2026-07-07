"""N9 檢索用查詢翻譯 — CJK 問句 → 英文檢索 query(translate-for-RETRIEVAL,非譯給閘)。

🎯 這支在做什麼(白話):augur 技術/財經文獻多為英文(solar_materials/chemistry/…),e5-small 對中文
   問句的跨語 kNN 會把英文正解沉在哲學/ERP 雜訊裡撈不上來。本檔用**本地 qwen3** 把 CJK 問句譯成
   一句自然英文檢索 query,呼叫端拿它另跑一趟英文嵌入檢索(見 advise():CJK 原文檢索無相關時才 fallback
   到英文)。**譯文只作用於「檢索用哪個 query」**——不入庫、不當 citation、不進答案內容、不進 guard 誠實閘(命門)。

   **failsafe 全程 fail-closed(#15):** qwen3 OOM(HTTP500/signal:killed)/逾時/回空/任何例外 → 回 None
   (絕不 raise、絕不讓翻譯失敗炸掉問答)。呼叫端收到 None → 只有原查詢結果(=誠實基線,多半 decline)。
   **無 CJK 的 query → 直接回 None**(英文問句本就英文檢索、不呼叫 qwen3、省 #28)。

   **確定性(#7):** lru_cache 快取譯文——同進程同 query 不重譯 → 結果一致(qwen3 溫度 0 本已近確定,
   快取再消弭記憶體壓力下的非確定翻覆風險;7.7GB 機 qwen3:8b temp=0 三跑一致實測,快取為確定性機械保證)。

守 #1(譯文非真兆、不入庫不入 citation)· #15(失敗誠實回 None、不佯稱)· #28(本地 qwen3、零 usage、
   無 CJK 不呼叫、僅 CJK 原文檢索失敗才觸發)· #18(query_translation=領域名詞)。

執行指令矩陣(library;主路徑經 advise() 呼叫):
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \
    print(t('鈣鈦礦太陽能電池的效率'))"          # → 'Efficiency of perovskite solar cells'(或近義)
  python -c "from augur.advisor.query_translation import translate_for_retrieval as t; \
    print(t('what is margin of safety'))"        # → None(無 CJK,不譯)
"""
import os
from functools import lru_cache

from augur.advisor import ollama

# 譯詞上限:檢索 query 不需長句;過長多為模型解釋離題(failsafe 一環,截斷而非放行)
_MAX_LEN = 200

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


@lru_cache(maxsize=512)
def translate_for_retrieval(query, model=None, timeout=None):
    """CJK 檢索 query → 英文 query 字串(供嵌入檢索);無 CJK 或任何失敗 → None。

    query:   用戶問句(原文)
    model:   Ollama model tag(預設 OLLAMA_MODEL env → qwen3:8b;操作值不寫死)
    timeout: 單次翻譯秒數上限(預設 OLLAMA_TRANSLATE_TIMEOUT env → 60;譯句短、不需 900s)
    回:      英文 query(str)或 None(無 CJK / OOM / 逾時 / 空 / 例外——一律 fail-closed 回 None,絕不 raise)
    """
    q = (query or "").strip()
    if not q or not _has_cjk(q):
        return None                                  # 無 CJK → 不呼叫 qwen3(省、#28)
    limit = float(timeout if timeout is not None
                  else os.environ.get("OLLAMA_TRANSLATE_TIMEOUT", 60.0))
    # think=False:關 qwen3 推理段(弱機提速);temp=0:近確定;num_predict 小:譯句短、有界輸出
    llm = ollama.make_llm_fn(model=model, timeout=limit, retries=0, think=False,
                             options={"temperature": 0, "num_predict": 64})
    try:
        out = llm(_PROMPT.format(q=q))
    except Exception:
        return None                                  # OOM(HTTP500/killed)/逾時/連線 → fail-closed(#15)
    return _clean(out)
