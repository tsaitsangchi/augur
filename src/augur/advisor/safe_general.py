"""空檢索安全通識放行判定 — 誠實保守白名單(fail-closed;憲章 v1.35.0/計畫 W2b·Phase2)。

🎯 這支在做什麼(白話):對話「語料檢索 0 命中」時,決定「這題能不能安全交 LLM 用一般常識白話答」。
   純正則、零 LLM、零 DB、可離線稽核。判準=三閘 AND、有疑一律偏保守(回 False→固定誠實句):
   (a) 正面命中封閉 B 通識概念/風險原則白名單;
   (b) 不命中任一 A 類「需真實資料」訊號(股號/財務數值/模型輸出/出處歸屬/時效);
   (c) 結構乾淨(≤60 字、無《》書名號、無經典引文樣態)。
   誤分類 fail-safe:漏放一個需 citation 題=踩三敵①、誤攔一個定義題=僅不助人 → 成本不對稱、寧攔。
   放行僅是「有資格交 LLM」;LLM 輸出仍全程過 guard(四閘+出處斷言閘),guard fail 即退回固定句。
守 #1(不編真兆:此層只判「可否放行」、真正防捏造在 guard)· #15(誠實:有疑偏 NO_KNOWLEDGE)·
   憲章 v1.35.0(誠實保守白名單=判準;詞表增刪屬執行層品質工程、guard 機械下限不變)。

執行指令矩陣(library;對話經 advise() 呼叫):
  python -c "from augur.advisor.safe_general import general_safe_answerable as f; print(f('有沒有穩賺不賠的股票'))"
  python -c "from augur.advisor.safe_general import general_safe_answerable as f; print(f('台積電2330的EPS是多少'))"

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.safe_general              # 印用途+公開入口（唯讀）
  python -m augur.advisor.safe_general --selftest   # 純紅綠自測（零 IO）
"""
import re

_MAXLEN = 60

# ── A 類 requires-citation 黑名單(命中任一 → 需真實資料、不放行)──
# 股號:四位數;Python \b 對 CJK 失效,改前後不接數字之邊界(「台積電2330的」黏合仍中);年份/金額於 _ticker_hit 排除
_FOURDIGIT = re.compile(r"(?<!\d)(\d{4})(?!\d)")

_A_FINANCIAL = re.compile(
    r"EPS|每股盈餘|營收|營業額|股價|收盤|開盤|成交量|PER|本益比|股價淨值比|PBR|殖利率|"
    r"股利|股息|配息|除權|除息|市值|市佔|ROE|ROA|毛利率?|淨利率?|營益率|成長率|漲幅|跌幅|"
    r"報酬率|周轉率|負債比|EPS|BVPS|自由現金流量")
_A_FINANCIAL_EN = re.compile(
    r"\bEPS\b|\bPER\b|\bPBR\b|\bROE\b|\bROA\b|revenue|earnings|dividend\s*yield|stock\s*price|market\s*cap",
    re.IGNORECASE)

# augur 模型輸出(三敵③最嚴:謊報模型績效)
_A_MODEL = re.compile(
    r"score|分數|\bIC\b|Sharpe|夏普|排名|\brank\b|因子|模型|回測|backtest|勝率|訊號|建議標的|選股結果",
    re.IGNORECASE)

# 出處/歸屬詢問(紅隊 R2 最危險、guard 引文閘只擋引號內逐字、裸出處全漏)
_THINKERS = (r"孔子|孟子|老子|莊子|荀子|韓非子?|墨子|孫子|朱熹|王陽明|司馬遷|曾國藩|"
             r"巴菲特|蒙格|葛拉漢|格雷厄姆|凱因斯|亞當斯密|馬克思|索羅斯|彼得林區|費雪|達里歐")
_CLASSICS = (r"論語|孟子|大學|中庸|道德經|莊子|史記|春秋|周易|易經|孫子兵法|司馬法|"
             r"韓非子|荀子|墨子|詩經|尚書|資治通鑑|國富論")
_A_SOURCE = re.compile(
    r"誰說|誰講|誰寫|哪一?(?:章|篇|卷|節|回|本|書)|出自|出處|典出|原文是|第幾(?:章|條|回|篇)|"
    r"語出|見於|引自|which\s+(?:book|chapter)|who\s+said")
# 引文樣態結構條件:思想家/經典 + 斷言/歸屬語(catch「民無信不立是孔子講的嗎」「這是論語裡的話對吧」)
_A_ATTRIB = re.compile(
    rf"(?:{_THINKERS})[^。\n]{{0,10}}(?:說|講|曰|提出|主張|認為|首創|寫過?|的話|名言|思想)"
    rf"|(?:{_CLASSICS})(?:裡|中|的|說|曰|提|篇|章|一書|這本)"
    rf"|是(?:{_THINKERS}).{{0,4}}(?:說|講|提出|寫)")

# as-of/時效 + 數值化事實(答案隨時點變動、或須查證量)
_A_ASOF = re.compile(
    r"現在|目前|今天|昨天|最新|近期|本季|上季|本月|去年|今年|Q[1-4]|GDP|利率|通膨|通貨膨脹|"
    r"CPI|失業率|匯率|升息|降息|第幾大|哪一年|多少(?:億|元|人|家|%|％|檔|支)")

# ── B 類安全通識白名單 ──
# B1 定義提問線索
_B_DEFINE_CUE = re.compile(
    r"是什麼|什麼是|定義|何謂|怎麼(?:算|計算|運作)|如何計算|運作原理|什麼意思|意思是|解釋|介紹一下")
# B1 封閉通識概念(timeless、非財務比率〔歸 A〕、非可 as-of 化〔歸 A〕;詞表執行層可調,憲章 v1.35.0)
_B_CONCEPTS = (
    "會計", "簿記", "複利", "單利", "分散投資", "資產配置", "多元化", "風險", "資產",
    "負債", "股東權益", "現金流", "財務報表", "損益表", "資產負債表", "現金流量表",
    "供需", "供給", "需求", "機會成本", "沉沒成本", "邊際效益", "規模經濟", "流動性",
    "價值投資", "成長投資", "安全邊際", "護城河", "內在價值", "基本面", "複利效應",
    "資本", "股票", "債券", "基金", "ETF", "指數", "藍籌股", "牛市", "熊市",
    "多頭", "空頭", "泡沫", "景氣循環", "通貨緊縮")
# B2 一般風險原則(不涉具體標的;正解否定式、錯答被 _FUTURE_LEAK 兜底)
_B2_RISK = re.compile(
    r"(?:有沒有|有無|存不存在|是否有|會不會有|哪裡?有).{0,10}"
    r"(?:穩賺不賠|穩賺|穩定獲利|零風險|無風險|保證獲利|包賺|一定賺|必賺|穩健獲利|穩贏)")


def _ticker_hit(q):
    """四位數字是否為股號(排除年份 19xx/20xx+年、金額 xxxx+元/萬/億)。"""
    for m in _FOURDIGIT.finditer(q):
        val = m.group(1)
        after = q[m.end():].lstrip()[:1]
        if val[:2] in ("19", "20") and after == "年":
            continue
        if after in ("元", "萬", "万", "億", "亿", "塊", "块", "圓", "円"):
            continue
        return True
    return False


def _has_a_signal(q):
    """命中任一 A 類需真實資料訊號 → True(不放行)。"""
    return bool(
        _ticker_hit(q)
        or _A_FINANCIAL.search(q) or _A_FINANCIAL_EN.search(q)
        or _A_MODEL.search(q)
        or _A_SOURCE.search(q) or _A_ATTRIB.search(q)
        or _A_ASOF.search(q))


def _has_b_concept(q):
    return any(c in q for c in _B_CONCEPTS)


def general_safe_answerable(query):
    """回 bool:True=可安全交 LLM 通識作答(仍過 guard);False=回固定誠實句。三閘 AND、fail-safe 偏 False。"""
    q = (query or "").strip()
    if not q or len(q) > _MAXLEN:
        return False
    if "《" in q or "》" in q:                       # 結構閘:書名號=引文/出處意圖
        return False
    if _has_a_signal(q):                             # A 閘:需真實資料一律不放行
        return False
    if _B2_RISK.search(q):                           # B2 風險原則
        return True
    if _B_DEFINE_CUE.search(q) and _has_b_concept(q):  # B1 定義題 + 封閉概念
        return True
    return False                                     # 未正面命中 B → fail-safe 保守


def _selftest():
    """純紅綠自測（零 IO）:合成 query→斷言三閘不變式與 fail-safe 偏 False。"""
    f = general_safe_answerable
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # B1 定義題+封閉概念放行
    chk("B1 定義題放行", f("什麼是複利") is True)
    # B2 風險原則放行(否定式常識)
    chk("B2 穩賺不賠放行", f("有沒有穩賺不賠的股票") is True)
    # A 閘:股號+財務數值不放行(三敵①)
    chk("A 股號+財務不放行", f("台積電2330的EPS是多少") is False)
    # A 閘:出處歸屬不放行(紅隊 R2)
    chk("A 出處歸屬不放行", f("民無信不立是孔子講的嗎") is False)
    # A 閘:as-of 時效不放行
    chk("A as-of 時效不放行", f("現在利率是多少") is False)
    # 結構閘:書名號不放行
    chk("書名號不放行", f("論語《學而》怎麼解釋") is False)
    # fail-safe:空字串/超長/未命中 B 一律 False
    chk("空字串 False", f("") is False)
    chk("超長 False", f("複利" * 40) is False)
    chk("未命中 B fail-safe False", f("今天天氣如何") is False)
    # helper 不變式:年份非股號、四位數黏合為股號
    chk("_ticker_hit 排除年份", _ticker_hit("2020年") is False)
    chk("_ticker_hit 命中股號", _ticker_hit("台積電2330") is True)
    chk("_has_b_concept 命中封閉概念", _has_b_concept("解釋複利效應") is True)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.safe_general --selftest;免 DB 免 API)")
