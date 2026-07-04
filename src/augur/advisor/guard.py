"""P6 生成後防幻覺閘 — 把三敵防護從 prompt 自律變成機械 gate。

🎯 顧問輸出送出前的最後守門:數字 ∈ payload、引號 ⊂ 檢索原文、無未來洩漏語、逆向不翻轉。
   任一不過 → 標記(供攔截/重生成)。這是 #1/#8/#15 在對話層的唯一可靠落地(無「哲學專屬豁免」)。
   L5 擴充(text 計畫 v1.6):定義引用必附 source_locator(guard_definition)+
   檢索空必回固定誠實句「知識庫中無此內容」(guard_empty_retrieval;誠實率 100% 之機制保證非自律)。
守 #1(數字/引文不編、定義出處可溯)· #8(anti-leakage)· #15(誠實)·
   憲章 v1.17.0(哲學不凌駕數據、審查 C-1)。
"""
import re

NO_KNOWLEDGE_RESPONSE = "知識庫中無此內容"   # 檢索空之唯一合法回覆(固定句,#15 機制保證)

_FUTURE_LEAK = re.compile(
    r"will (rise|fall|surge|crash|soar|plunge)|保證|必(漲|跌|賺)|下週.{0,6}(漲|跌)|明(日|天).{0,6}(漲|跌)|未來.{0,4}(會漲|會跌|必)")
_REVERSE = re.compile(
    r"所以.{0,8}(該|應|建議).{0,4}(賣|放空|反著|做空)|建議.{0,4}(賣出|放空|做空)|reverse the (call|model|score)|sell instead")
# 指標詞鄰接數字(IC 0.2 這類整數/1 位小數編造值也須 ∈ 白名單;稽核 2026-07-04 執5)
_METRIC_NUM = re.compile(
    r"(?:\b(?:IC|Sharpe|score)\b|分數)[^\d\n。,;,;]{0,8}?(\d+(?:\.\d+)?)", re.IGNORECASE)


def guard(response, payload, citations):
    """回 {'pass': bool, 'issues': [str]}。issues 非空 = 應攔截/重生成。"""
    issues = []
    cite_texts = [c.text for c in citations]

    # ① 引文校驗:引號內容(≥8 字)須逐字存在於某 citation(防編造/潤飾引文)
    for quote in re.findall(r'[「『"]([^」』"]{8,})[」』"]', response):
        if not any(quote in t for t in cite_texts):
            issues.append(f"引文非逐字或非庫內(#1):{quote[:40]!r}")

    # ② 數字校驗:顯著小數 + IC/Sharpe/score 鄰接數字(不論位數)須 ∈ payload(防編造預測數字)
    allowed = payload.numbers()
    suspects = set(re.findall(r"\d+\.\d{2,}", response)) | set(_METRIC_NUM.findall(response))
    for m in sorted(suspects):
        if round(float(m), 4) not in allowed:
            issues.append(f"數字非 payload、疑編造(#1):{m}")

    # ③ 未來/保證語(#8 anti-leakage)
    if _FUTURE_LEAK.search(response):
        issues.append("含未來預測/保證語(#8)")

    # ④ 逆向翻轉(審查 C-1):逆向不得輸出與模型分數相反的行動含義
    if _REVERSE.search(response):
        issues.append("逆向鏡翻轉模型結論、輸出相反行動(禁、審查 C-1)")

    return {"pass": not issues, "issues": issues}


def guard_empty_retrieval(response, results):
    """檢索空之誠實閘(#15):lexicon/concordance/chunk 檢索結果全空時,回覆必須為固定誠實句
    NO_KNOWLEDGE_RESPONSE——不得即興發揮、不得從模型記憶補答(庫外=不知道)。回 {'pass','issues'}。"""
    issues = []
    if not results and response.strip() != NO_KNOWLEDGE_RESPONSE:
        issues.append(f"檢索空但回覆非固定誠實句「{NO_KNOWLEDGE_RESPONSE}」(#15)")
    return {"pass": not issues, "issues": issues}


def guard_definition(response, lex_entries):
    """定義引用閘(#1 可溯源):回覆中引用之每則 lexicon 定義(LexEntry,見 philosophy.retrieval)
    必附其 source_locator;檢索空 → 委給 guard_empty_retrieval(固定誠實句)。回 {'pass','issues'}。"""
    if not lex_entries:
        return guard_empty_retrieval(response, lex_entries)
    issues = []
    for e in lex_entries:
        frag = (e.definition or "").strip()[:24]
        if len(frag) < 8 or frag not in response:      # 定義未被引用 → 不課 locator 義務
            continue
        loc = (e.source_locator or "").strip()
        if not loc:
            issues.append(f"定義無 source_locator 卻被引用、出處不可溯(#1):{e.term}")
        elif loc not in response:
            issues.append(f"定義引用未附 source_locator(#1):{e.term} 應附「{loc}」")
    return {"pass": not issues, "issues": issues}
