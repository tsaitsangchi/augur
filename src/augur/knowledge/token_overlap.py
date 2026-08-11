"""知庫／相關度共用：內容詞與辨識性專詞（STRUCT：自 advisor.relevance 抽出）。

🎯 零 ML 詞形／CJK 窗／泛用字剔除——供 relevance 閘與 answer_auto_lift R-cite 共用，
   使 knowledge 不須 import advisor。

執行指令矩陣:
  python -m augur.knowledge.token_overlap --selftest
"""
from __future__ import annotations

import re

from augur.knowledge import textnorm

_STOP = set(
    "的是了而之也其以於与與為爲在有無不人上下這那我你他它們就都會要說到得着着過"
    "麼嗎呢吧啊哦且或如何個把被讓從向對比很更最只還又再"
)

_EN_GENERIC = set(
    """
system analysi analyz research studi method process design approach result review paper articl
chapter section develop applic use base gener overview introduct report perform problem solut
effect factor field level type form framework structur function theori scienc main core master
multi whether energi effici technologi innov optim advantag technic benefit product manag manufactur qualiti industri
techniqu materi properti characterist paramet condit measur estim comput simul evalu impact
influenc relationship compar improv enhanc model data valu case work part number general
there ani ar on of the a an in to for and or with by is at about into over under between within
what how whi where when who which do doe did can could would should mean definit concept
topic subject question relat relev exist avail""".split()
)


def content_tokens(text):
    """內容詞集合:textnorm zh ∪ en；剔單字虛詞、剔未切斷長 token(>12)。"""
    zh = {t for t, _ in textnorm.tokenize(text, "zh")}
    en = {t for t, _ in textnorm.tokenize(text, "en")}
    return {t for t in (zh | en) if len(t) <= 12 and not (len(t) == 1 and t in _STOP)}


def is_strong(tok):
    """辨識性專詞是否夠強（見 advisor.relevance 史料註）。"""
    if tok.isascii():
        return len(tok) >= 2
    return 2 <= len(tok) <= 8


def cjk_ngrams(text, lo=2, hi=4):
    """連續 CJK 段之 2..hi 字窗。"""
    out = set()
    for m in re.finditer(r"[\u4e00-\u9fff]+", text or ""):
        s = m.group(0)
        n = len(s)
        for length in range(lo, min(hi, n) + 1):
            for i in range(n - length + 1):
                out.add(s[i : i + length])
    return out


def strong_distinctive(text):
    """夠強辨識性專詞集 ∪ CJK 2..4 字窗。"""
    toks = {t for t in (content_tokens(text) - _EN_GENERIC) if is_strong(t)}
    toks |= {t for t in cjk_ngrams(text) if is_strong(t)}
    return toks


def cite_text(cite):
    """citation 可比對內容:原文 + 著作名 + thinker/domain。"""
    parts = [
        getattr(cite, "text", "") or "",
        getattr(cite, "work_title", "") or getattr(cite, "item_title", "") or "",
        getattr(cite, "thinker", "") or getattr(cite, "domain", "") or "",
    ]
    return " ".join(parts)


# BC 底線名（舊 _ 前綴呼叫點）
_content_tokens = content_tokens
_is_strong = is_strong
_cjk_ngrams = cjk_ngrams
_strong_distinctive = strong_distinctive
_cite_text = cite_text


def _selftest() -> bool:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("✓" if cond else "✗"), name)

    class C:
        text = "知行合一"
        work_title = "傳習錄"
        thinker = "王陽明"

    chk("strong 含多字", "知行" in strong_distinctive("知行合一") or "知行合一" in strong_distinctive("知行合一"))
    chk("cite joins", "傳習錄" in cite_text(C()) and "王陽明" in cite_text(C()))
    chk("generic excluded", "research" not in strong_distinctive("research overview study"))
    return ok


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        raise SystemExit(0 if _selftest() else 1)
    print(__doc__)
