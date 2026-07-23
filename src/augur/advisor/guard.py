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

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.advisor.guard              # 印用途+公開入口(唯讀)
  python -m augur.advisor.guard --selftest   # 純紅綠自測(零 IO)
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

# 出處斷言閘(第五條 fail-close,憲章 v1.35.0):放行路無 citation 時,防「裸出處捏造」——
# 模型輸出看似在引哲學/古典語料庫(書名號、經典+篇章、古人曰、出自X篇)但無真兆 citation 佐證。
# 既有引文閘①只擋引號內≥8字逐字,裸出處(無引號)全漏(紅隊 R2 實證 guard PASS),此閘補之。
# 聚焦古典/語料出處(與 augur 哲學語料庫混淆之風險);現代概念歸屬(如格雷厄姆提出安全邊際)屬
# 一般知識、非①治理對象,不在此閘(其事實正確性為已接受殘餘、非機械可判)。
_CLASSIC_NAMES = (r"論語|孟子|大學|中庸|道德經|老子|莊子|荀子|韓非子|墨子|孫子兵法|司馬法|"
                  r"史記|春秋|周易|易經|詩經|尚書|資治通鑑|傳習錄|近思錄|六祖壇經")
_ATTRIBUTION_OUT = re.compile(
    r"《[^》]{1,30}》"
    rf"|(?:{_CLASSIC_NAMES})[^。\n]{{0,12}}(?:篇|章|卷|曰|云|記載|寫道|提到|所言|所云)"
    rf"|(?:出自|語出|典出|見於|載於|引自)[^。\n]{{0,15}}(?:{_CLASSIC_NAMES}|篇|章|卷)"
    r"|(?:孔子|孟子|老子|莊子|荀子|韓非|墨子|朱熹|王陽明|曾子)[^。\n]{0,8}(?:曰|云|說道|有云|有言)")
_CLASSIC_RE = re.compile(_CLASSIC_NAMES)


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
    suspects = set(re.findall(r"-?\d+\.\d{2,}", response)) | set(_METRIC_NUM.findall(response))  # -? 捕負號:正確引用之負值(如 net_maxdd -0.1392)不再因掉號誤判編造
    for m in sorted(suspects):
        if round(float(m), 4) not in allowed:
            issues.append(f"數字非 payload、疑編造(#1):{m}")

    # ③ 未來/保證語(#8 anti-leakage)
    if _FUTURE_LEAK.search(response):
        issues.append("含未來預測/保證語(#8)")

    # ④ 逆向翻轉(審查 C-1):逆向不得輸出與模型分數相反的行動含義
    if _REVERSE.search(response):
        issues.append("逆向鏡翻轉模型結論、輸出相反行動(禁、審查 C-1)")

    # ⑤ 股名校驗(#1:防幻覺股名——payload 給 symbol+name 時,輸出「股號+緊鄰 CJK 名」須與該股名相容;
    #    子集互容如 台積/台積電;僅查 payload 內股號、非 payload 股號自然略過,無 name 之舊 payload no-op)
    name_by_sym = {p.symbol: getattr(p, "name", "") for p in getattr(payload, "picks", ())}
    if any(name_by_sym.values()):
        for sym, out_name in re.findall(r"(\d{4})[ 　:：]*([一-鿿]{2,6})", response):
            want = name_by_sym.get(sym)
            if want and out_name != want and out_name not in want and want not in out_name:
                issues.append(f"股名與 payload 不符、疑幻覺股名(#1):{sym}「{out_name}」應為「{want}」")

    return {"pass": not issues, "issues": issues}


_NUM_TOKEN = re.compile(r"-?\d+(?:\.\d+)?")  # -? 成對:白名單保留負值,誠實引用之負數(如 -0.1392)不因掉號被誤攔


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
    suspects = set(re.findall(r"-?\d+\.\d{2,}", claims)) | set(_METRIC_NUM.findall(claims))  # -? 與 guard() :57 對齊:防符號翻轉編造(citation 0.9987→輸出 -0.9987 曾可放行)
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


def guard_attribution(response, citations):
    """出處斷言閘(第五條 fail-close,憲章 v1.35.0;放行路與主路徑皆生效):回覆含古典/語料出處斷言
    (《書名》/經典+篇章/古人曰/出自X篇)時,須有 citation 佐證所斷言之經典——
      · 空檢索(citations=[]):任何出處斷言即 fail(無真兆可佐、裸出處捏造);
      · 非空:被斷言之古典書名須有某 citation 的 work_title/text 佐證,否則 fail
        (紅隊 R2:撈到奧古斯丁卻宣稱出自《論語·為政》、錯章捏造 → 擋)。
    既有四閘正則(①②③④)一字不動;此為並列第五條。回 {'pass','issues'}。"""
    issues = []
    if not _ATTRIBUTION_OUT.search(response):
        return {"pass": True, "issues": issues}
    if not citations:
        issues.append("含古典/語料出處斷言但無 citation、疑裸出處捏造(#1)")
        return {"pass": False, "issues": issues}
    asserted = set(re.findall(r"《([^》]{1,30})》", response)) | set(_CLASSIC_RE.findall(response))
    blob = " ".join(((getattr(c, "work_title", "") or getattr(c, "item_title", "") or "")
                     + " " + (getattr(c, "text", "") or "")) for c in citations)
    unbacked = [a for a in asserted if re.split(r"[·•・\s]", a)[0] not in blob]
    if unbacked:
        issues.append(f"出處斷言之經典無 citation 佐證、疑捏造出處(#1):{unbacked[:3]}")
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


def _selftest():
    """自測(零 IO:純 regex 閘紅綠+誠實句閉集結構鎖;免 DB 免 API #29a)——
    把五閘最該守的性質(編造擋、逐字/白名單放行、幻覺股名擋、空檢索必誠實句)固化成回歸鎖。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    class _C:                                    # 合成 citation(僅需 .text)
        def __init__(self, text):
            self.text = text

    class _P:                                    # 合成 payload(numbers()+picks)
        def __init__(self, nums=(), picks=()):
            self._n = {round(float(x), 4) for x in nums}
            self.picks = picks

        def numbers(self):
            return self._n

    class _Pick:
        def __init__(self, symbol, name):
            self.symbol = symbol
            self.name = name

    cites = [_C("蘋果每股盈餘為 12.3456 元,毛利率穩定。")]
    # ① 引文逐字:非庫內引號段擋、庫內逐字放行
    chk("guard 編造引文擋", guard("他說「這是一段不存在的捏造引文」", _P(), cites)["pass"] is False)
    chk("guard 逐字引文放行", guard("原文「蘋果每股盈餘為 12.3456 元」", _P([12.3456]), cites)["pass"] is True)
    # ② 數字:非 payload 之顯著小數/指標鄰接數字擋、∈payload(含負值不掉號)放行
    chk("guard 編造 IC 數字擋", guard("預估 IC 0.87 很高", _P(), [])["pass"] is False)
    chk("guard payload 負值放行", guard("net_maxdd -0.1392 撐住", _P([-0.1392]), [])["pass"] is True)
    # ③④ 未來/保證語、逆向翻轉
    chk("guard 未來保證語擋(#8)", guard("此股下週會漲", _P(), [])["pass"] is False)
    chk("guard 逆向翻轉擋(C-1)", guard("所以建議賣出", _P(), [])["pass"] is False)
    # ⑤ 幻覺股名(payload 有 name 時)
    chk("guard 幻覺股名擋", guard("推薦 2330 鴻海", _P(picks=[_Pick("2330", "台積電")]), [])["pass"] is False)
    # 誠實句閉集(結構鎖:憲章分級,閉集僅二句)
    chk("誠實句閉集二句", len(HONESTY_CLOSED_SET) == 2 and NO_KNOWLEDGE_RESPONSE in HONESTY_CLOSED_SET)
    chk("空檢索非誠實句擋(#15)", guard_empty_retrieval("我覺得這檔不錯", [])["pass"] is False)
    chk("空檢索誠實句放行", guard_empty_retrieval(NO_KNOWLEDGE_RESPONSE, [])["pass"] is True)
    # 出處斷言閘(裸古典出處無 citation 擋、無斷言 no-op)
    chk("裸古典出處無 citation 擋", guard_attribution("如《論語》所言", [])["pass"] is False)
    chk("無出處斷言 no-op 放行", guard_attribution("這檔股票不錯", [])["pass"] is True)
    # citation_numbers 抽數字集(round 口徑同閘②)
    chk("citation_numbers 抽數字集", citation_numbers([_C("值為 3.14 與 2")]) == {3.14, 2.0})

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.guard --selftest;免 DB 免 API)")
