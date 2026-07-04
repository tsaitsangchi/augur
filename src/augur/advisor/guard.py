"""P6 生成後防幻覺閘 — 把三敵防護從 prompt 自律變成機械 gate。

🎯 顧問輸出送出前的最後守門:數字 ∈ payload、引號 ⊂ 檢索原文、無未來洩漏語、逆向不翻轉。
   任一不過 → 標記(供攔截/重生成)。這是 #1/#8/#15 在對話層的唯一可靠落地(無「哲學專屬豁免」)。
   L5 擴充(text 計畫 v1.6):定義引用必附 source_locator(guard_definition)+
   檢索空必回固定誠實句「知識庫中無此內容」(guard_empty_retrieval;誠實率 100% 之機制保證非自律)。
   P8 知識域條款(已拍板 2026-07-04,計畫 §3-S7 N6/§8 拍板紀錄):guard_knowledge 數字雙源白名單
   (payload.numbers() ∪ 檢索真兆數字集 citation_numbers)+已驗引文段豁免②③+無 picks ④ no-op;
   接線=advise() 依 payload 型別分派(oai_compat 唯一出口=advise(),同路生效);誠實句閉集不變。
守 #1(數字/引文不編、定義出處可溯)· #8(anti-leakage)· #15(誠實)·
   憲章 v1.17.0(哲學不凌駕數據、審查 C-1)。
"""
import re

NO_KNOWLEDGE_RESPONSE = "知識庫中無此內容"   # (i) 檢索空之固定句(#15 機制保證)
# 三級誠實固定句閉集第二句(憲章 v1.25.0/拍板3):庫存著作但歸屬未驗(review_flag=true 隔離館藏旁查
# 命中而主檢索 CLEAN 述詞排除)。閉集僅此二句;機械分級器(哪句/何時)住 answer.py(W8 落地)。
# 閉集或分級判準之變更=憲章判準變更(v1.25.0 line 137),不得執行層自改。
UNVERIFIED_ATTRIBUTION_RESPONSE = "知識庫存有此著作但歸屬未驗證,不予引用"
HONESTY_CLOSED_SET = (NO_KNOWLEDGE_RESPONSE, UNVERIFIED_ATTRIBUTION_RESPONSE)

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


_NUM_TOKEN = re.compile(r"\d+(?:\.\d+)?")


def citation_numbers(citations):
    """檢索真兆數字集(P8 數字雙源之二):本回合檢索結果(真兆 SQL 查詢結果列,advise 已先過
    verify_verbatim)原文內全部數字 token,round 口徑同閘 ②——每值可 trace 回某 citation 列(#15)。"""
    return {round(float(n), 4) for c in citations for n in _NUM_TOKEN.findall(c.text)}


def guard_knowledge(response, payload, citations, sql_numbers=()):
    """知識域 guard 條款(P8 已拍板 2026-07-04,計畫 §3-S7 N6/§8 拍板紀錄;已接線——
    advise() 依 payload 型別分派本閘,oai_compat 唯一出口=advise() 故同路生效)。
    與 guard() 之差=P8 ②③④:

    ② 數字白名單雙源=payload.numbers() ∪ sql_numbers(本回合真兆 SQL 結果集;接線端傳
      citation_numbers(citations)=檢索真兆數字集,round 口徑一致、可溯源 #15);
      且**已過 ① 逐字驗證之引文段內數字豁免 ②**(引文=文獻原文非系統宣稱,如 114.32 g/mol)。
    ③ _FUTURE_LEAK 對已驗逐字引文段豁免(科學文本 "pressure will rise" 非投資建議)。
    ④ 逆向閘於無 picks 之知識 payload 自然 no-op(無模型結論可翻轉)。
    ① 引文逐字閘不變(與 guard() 同判準);誠實句閉集不變(P8 拍板明文)。
    回 {'pass': bool, 'issues': [str]}。
    """
    issues = []
    cite_texts = [c.text for c in citations]

    # ① 引文逐字(同 guard());並記下「已驗證段」供 ②③ 豁免
    verified = []
    for quote in re.findall(r'[「『"]([^」』"]{8,})[」』"]', response):
        if any(quote in t for t in cite_texts):
            verified.append(quote)
        else:
            issues.append(f"引文非逐字或非庫內(#1):{quote[:40]!r}")

    claims = response                      # 系統宣稱文本=回覆剔除已驗逐字引文段(豁免只給過①者,fail-closed)
    for q in verified:
        claims = claims.replace(q, "")

    # ② 數字 ∈ 雙源白名單(payload.numbers() ∪ 本回合真兆 SQL 結果集);已驗引文段內數字已豁免
    allowed = set(payload.numbers()) | {round(float(n), 4) for n in sql_numbers}
    suspects = set(re.findall(r"\d+\.\d{2,}", claims)) | set(_METRIC_NUM.findall(claims))
    for m in sorted(suspects):
        if round(float(m), 4) not in allowed:
            issues.append(f"數字非雙源白名單、疑編造(#1):{m}")

    # ③ 未來/保證語(#8);已驗引文段豁免
    if _FUTURE_LEAK.search(claims):
        issues.append("含未來預測/保證語(#8)")

    # ④ 逆向翻轉:無 picks(知識 payload)→ 自然 no-op
    if getattr(payload, "picks", ()) and _REVERSE.search(response):
        issues.append("逆向鏡翻轉模型結論、輸出相反行動(禁、審查 C-1)")

    return {"pass": not issues, "issues": issues}


def guard_empty_retrieval(response, results):
    """檢索空之誠實閘(#15):檢索結果全空時,回覆必須為**三級誠實固定句閉集**之一
    (HONESTY_CLOSED_SET:(i)庫中確無 或 (ii)庫存未驗歸屬;憲章 v1.25.0/拍板3)——
    不得即興發揮、不得從模型記憶補答(庫外/未驗=不引用)。閉集分級由 answer.honesty_level 決。回 {'pass','issues'}。"""
    issues = []
    if not results and response.strip() not in HONESTY_CLOSED_SET:
        issues.append(f"檢索空但回覆非誠實句閉集{HONESTY_CLOSED_SET}(#15)")
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
