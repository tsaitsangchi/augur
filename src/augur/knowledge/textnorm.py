"""term 正規化契約(SSOT)— L2 concordance / L3 lexicon / L5 advisor 三方共用 JOIN 鍵。

🎯 這支在做什麼(白話):把「字/詞/詞條」變成唯一且可重現的正規化形,讓 knowledge_concordance、
   knowledge_lexicon、advisor 檢索三方用**同一個函式**產 term——同輸入必同輸出,才 JOIN 得起來。

契約(text 計畫 v1.6 §二6;改此檔=改契約,T2/T4/L5 三方同步):
- normalize(name_or_term):NFC + 去首尾空白;不改大小寫、**不繁簡互轉**(原貌入庫,查詢層可雙查繁簡)。
- tokenize(text, language) -> [(term, position)]:
  - 中文(language 以 'zh' 開頭):**逐字** = U+4E00–U+9FFF 每字一 token;**詞** = jieba
    `tokenize(HMM=False)`(詞典驅動、確定性),僅取長度 ≥2 且全 CJK 之詞(單字詞已由逐字涵蓋,不重複);
  - 西文(其餘 language):`\w+` token → lowercase → 內建 Porter stemmer(1980 原版、純規則,不引 nltk);
  - position = token 於**輸入字串原樣**之 0-based char offset(呼叫端存句建議先 normalize,
    C2 char_range 才可逐字回溯);term 一律 NFC;輸出按 (position, term) 排序。
- norm_headword(s, language):lexicon 詞條頭字——中文 = normalize 原貌;
  西文 = 逐 `\w+` lowercase+stem 後以單一空白連接(與 concordance term 同形可 JOIN)。
- 確定性(#15):零 ML 黑箱——jieba HMM=False 詞典驅動、Porter 純規則;同輸入必同輸出、半年重跑一致
  (jieba 版本釘於 pyproject;換版本=換詞典,須重建 concordance 才可宣稱一致)。

守 #1(只正規化、不生成內容)· #12(單一住所:三方 import 這裡、不各自實作)· #15(確定性可重現)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.textnorm              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.textnorm --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import re
import unicodedata

_CJK_LO, _CJK_HI = "一", "鿿"
_WORD_RE = re.compile(r"\w+")
_jieba_mod = None


def _jieba():
    """jieba 延遲載入(西文路徑不需要;未裝時錯誤訊息明確)。"""
    global _jieba_mod
    if _jieba_mod is None:
        try:
            import jieba
        except ImportError as e:
            raise ImportError("jieba 未安裝(中文分詞依賴):pip install jieba;已列入 pyproject dependencies") from e
        jieba.setLogLevel(60)  # 靜默 prefix dict 建置訊息(CLI 輸出確定性)
        _jieba_mod = jieba
    return _jieba_mod


def _is_zh(language) -> bool:
    return str(language).lower().startswith("zh")


def _is_cjk(ch: str) -> bool:
    return _CJK_LO <= ch <= _CJK_HI


def normalize(name_or_term: str) -> str:
    """NFC 正規化 + 去首尾空白;不改大小寫、不繁簡互轉。"""
    return unicodedata.normalize("NFC", str(name_or_term)).strip()


# ── Porter stemmer(1980 原版,純 Python、零外部依賴)────────────────────
def _cons(w: str, i: int) -> bool:
    ch = w[i]
    if ch in "aeiou":
        return False
    if ch == "y":
        return i == 0 or not _cons(w, i - 1)
    return True


def _m(w: str) -> int:
    """measure:[C](VC)^m[V] 之 m(VC 交替段數)。"""
    n = i = 0
    length = len(w)
    while i < length and _cons(w, i):
        i += 1
    while True:
        while i < length and not _cons(w, i):
            i += 1
        if i >= length:
            return n
        n += 1
        while i < length and _cons(w, i):
            i += 1


def _has_vowel(w: str) -> bool:
    return any(not _cons(w, i) for i in range(len(w)))


def _dbl_cons(w: str) -> bool:
    return len(w) >= 2 and w[-1] == w[-2] and _cons(w, len(w) - 1)


def _cvc(w: str) -> bool:
    return (len(w) >= 3 and _cons(w, len(w) - 3) and not _cons(w, len(w) - 2)
            and _cons(w, len(w) - 1) and w[-1] not in "wxy")


_STEP2 = (("ational", "ate"), ("tional", "tion"), ("enci", "ence"), ("anci", "ance"),
          ("izer", "ize"), ("abli", "able"), ("alli", "al"), ("entli", "ent"), ("eli", "e"),
          ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"), ("ator", "ate"),
          ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"), ("ousness", "ous"),
          ("aliti", "al"), ("iviti", "ive"), ("biliti", "ble"))
_STEP3 = (("icate", "ic"), ("ative", ""), ("alize", "al"), ("iciti", "ic"),
          ("ical", "ic"), ("ful", ""), ("ness", ""))
_STEP4 = ("al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement", "ment",
          "ent", "ion", "ou", "ism", "ate", "iti", "ous", "ive", "ize")


def porter_stem(word: str) -> str:
    """標準 Porter stemmer(Porter 1980 原版規則);長度 ≤2 原樣返回。輸入內部先 lowercase。"""
    w = word.lower()
    if len(w) <= 2:
        return w
    # step 1a
    if w.endswith("sses") or w.endswith("ies"):
        w = w[:-2]
    elif not w.endswith("ss") and w.endswith("s"):
        w = w[:-1]
    # step 1b
    if w.endswith("eed"):
        if _m(w[:-3]) > 0:
            w = w[:-1]
    else:
        stripped = False
        if w.endswith("ed") and _has_vowel(w[:-2]):
            w, stripped = w[:-2], True
        elif w.endswith("ing") and _has_vowel(w[:-3]):
            w, stripped = w[:-3], True
        if stripped:
            if w.endswith(("at", "bl", "iz")):
                w += "e"
            elif _dbl_cons(w) and w[-1] not in "lsz":
                w = w[:-1]
            elif _m(w) == 1 and _cvc(w):
                w += "e"
    # step 1c
    if w.endswith("y") and _has_vowel(w[:-1]):
        w = w[:-1] + "i"
    # step 2(m>0;僅試最長相符一條=原演算法「單步一規則」)
    for suf, rep in _STEP2:
        if w.endswith(suf):
            if _m(w[: -len(suf)]) > 0:
                w = w[: -len(suf)] + rep
            break
    # step 3(m>0)
    for suf, rep in _STEP3:
        if w.endswith(suf):
            if _m(w[: -len(suf)]) > 0:
                w = w[: -len(suf)] + rep
            break
    # step 4(m>1;ion 須 stem 尾 s/t)
    for suf in _STEP4:
        if w.endswith(suf):
            stem = w[: -len(suf)]
            if _m(stem) > 1 and (suf != "ion" or (stem and stem[-1] in "st")):
                w = stem
            break
    # step 5a
    if w.endswith("e"):
        m = _m(w[:-1])
        if m > 1 or (m == 1 and not _cvc(w[:-1])):
            w = w[:-1]
    # step 5b
    if _m(w) > 1 and _dbl_cons(w) and w.endswith("l"):
        w = w[:-1]
    return w


# ── tokenize / headword(契約入口)─────────────────────────────────────
def tokenize(text: str, language) -> list[tuple[str, int]]:
    """逐字/詞 token 化(契約見模組 docstring);回傳 [(term, position)],按 (position, term) 排序。"""
    if _is_zh(language):
        out = [(unicodedata.normalize("NFC", ch), i) for i, ch in enumerate(text) if _is_cjk(ch)]
        for word, start, _end in _jieba().tokenize(text, HMM=False):
            w = unicodedata.normalize("NFC", word)
            if len(w) >= 2 and all(_is_cjk(c) for c in w):
                out.append((w, start))
        out.sort(key=lambda t: (t[1], t[0]))
        return out
    return [(porter_stem(unicodedata.normalize("NFC", m.group(0)).lower()), m.start())
            for m in _WORD_RE.finditer(text)]


def norm_headword(s: str, language) -> str:
    """lexicon 詞條頭字正規化(與 concordance term 同形可 JOIN);西文空 token 回空字串,呼叫端跳過。"""
    s = normalize(s)
    if _is_zh(language):
        return s
    return " ".join(porter_stem(w.lower()) for w in _WORD_RE.findall(s))


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # normalize:去首尾空白、NFC、不改大小寫、冪等
    chk("normalize 去空白不改大小寫", normalize("  Hello 世界  ") == "Hello 世界")
    chk("normalize 冪等", normalize(normalize("  ABC  ")) == "ABC")
    # Porter stemmer 標準向量(#15 確定性回歸鎖)
    chk("stem caresses->caress", porter_stem("caresses") == "caress")
    chk("stem ponies->poni", porter_stem("ponies") == "poni")
    chk("stem running->run", porter_stem("running") == "run")
    chk("stem 短字原樣", porter_stem("go") == "go")
    # tokenize 西文:stem+lowercase+char offset
    chk("tokenize 西文", tokenize("Cats running", "en") == [("cat", 0), ("run", 5)])
    # norm_headword:西文同 concordance 形、中文原貌
    chk("headword 西文", norm_headword("Running Cats", "en") == "run cat")
    chk("headword 中文原貌", norm_headword(" 台積電 ", "zh") == "台積電")
    # 語言/字元判定
    chk("_is_zh", _is_zh("zh-TW") and not _is_zh("en"))
    chk("_is_cjk", _is_cjk("世") and not _is_cjk("a"))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.textnorm --selftest;免 DB 免 API)")
