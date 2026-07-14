"""augur 總體經濟因子清單 — 宣告要從 FRED 抓哪些 macro series + 其 point-in-time 抓法。

🎯 這支在做什麼（白話）：
augur 用哪些 FRED 總經數列當情境輸入，是 **feature 設計的決策**（fred.py client 不持清單、由呼叫端決定）。
本檔即那份決策：列出每檔 `series_id` + 它屬哪一層 + 該怎麼抓才不洩漏，當「抓哪些 series」的單一真源。

兩層（依**會不會被回溯修訂**分，決定 anti-leakage 抓法，#8）：
- **Tier A（每日市場數列）**：殖利率 / 利差 / 匯率 / VIX / 信用利差 / 油價 / 指數——**當日觀測值、當天即知、
  事後不修訂**。故抓最新值即可，`realtime_start = 觀測日`（市場收盤值當日可見，**正確、非近似**）。
- **Tier B（月 / 季 / 週經濟數列）**：失業 / CPI / GDP / 工業生產…——**發布落後 + 會被回溯修訂**。直接用最新
  修訂值＝拿「當時還看不到的數字」回測＝假兆（#8）。故走 **ALFRED vintage**（逐 vintage 存真實
  `realtime_start`），feature 層才能取「面板日當下真看得到」那版。

非「白名單臆測」（別於 #3/#18 對 FinMind 結構之禁）：FRED 無「augur 要哪些總經因子」的 /datalist，這本就是
策展決策；清單每檔均經 live FRED API 證實存在（#15），非為省探測硬編。

守 #8（anti-leakage：Tier B vintage 取當下可見版）· #4（總經日級真兆值得抓）· #15（每檔 live 證實）· #1/#2（忠實落地 FRED）。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.macro              # 印用途+公開入口（唯讀）
  python -m augur.features.macro --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from collections import namedtuple

# tier：'A'＝每日市場（不修訂、realtime_start=date）｜'B'＝月/季/週經濟（會修訂、ALFRED vintage）
# vintage：是否走 ALFRED 全 vintage 抓法（＝ tier=='B'）
MacroSeries = namedtuple("MacroSeries", ["series_id", "tier", "vintage", "zh"])


def _a(sid, zh):   # Tier A：每日市場、不 vintage
    return MacroSeries(sid, "A", False, zh)


def _b(sid, zh):   # Tier B：月/季/週經濟、走 vintage
    return MacroSeries(sid, "B", True, zh)


SERIES = (
    # ── Tier A：每日市場數列（不修訂、當日可見；realtime_start=date）──
    _a("DGS10", "美國10年期公債殖利率"),
    _a("DGS2", "美國2年期公債殖利率"),
    _a("DGS3MO", "美國3個月期公債殖利率"),
    _a("DGS30", "美國30年期公債殖利率"),
    _a("T10Y2Y", "10年減2年殖利率利差（曲線斜率）"),
    _a("T10Y3M", "10年減3月殖利率利差（衰退訊號）"),
    _a("DFF", "聯邦資金有效利率"),
    _a("T5YIE", "5年期市場隱含通膨預期"),
    _a("T10YIE", "10年期市場隱含通膨預期"),
    _a("DTWEXBGS", "名目廣義美元指數"),
    _a("DEXTAUS", "新台幣對美元匯率"),
    _a("DEXKOUS", "韓元對美元匯率"),
    _a("DEXCHUS", "人民幣對美元匯率"),
    _a("DEXJPUS", "日圓對美元匯率"),
    _a("VIXCLS", "CBOE VIX 波動率指數"),
    _a("BAMLH0A0HYM2", "ICE BofA 美國高收益債選擇權調整利差"),
    _a("BAMLC0A0CM", "ICE BofA 美國投資級公司債選擇權調整利差"),
    _a("DCOILWTICO", "WTI 原油價格"),
    _a("DCOILBRENTEU", "Brent 原油價格"),
    _a("NASDAQCOM", "那斯達克綜合指數"),
    _a("DPRIME", "銀行基本放款利率"),
    _a("RRPONTSYD", "隔夜逆回購（美元流動性）"),
    # ── Tier B：月/季/週經濟數列（會修訂、發布落後；ALFRED vintage）──
    _b("UNRATE", "美國失業率（月）"),
    _b("CPIAUCSL", "美國CPI消費者物價指數（月）"),
    _b("INDPRO", "美國工業生產指數（月）"),
    _b("PAYEMS", "美國非農就業人數（月）"),
    _b("GDPC1", "美國實質GDP（季）"),
    _b("UMCSENT", "密西根大學消費者信心（月）"),
    _b("M2SL", "美國M2貨幣供給（月）"),
    _b("WALCL", "Fed總資產（週）"),
    _b("WRESBAL", "Fed準備金（週）"),
)


def series_ids():
    """全部 series_id（落地/列舉用）。"""
    return [s.series_id for s in SERIES]


def vintage_map():
    """{series_id: 是否走 ALFRED vintage}（sync 依此套 Tier A/B 抓法）。"""
    return {s.series_id: s.vintage for s in SERIES}


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成/實 SERIES 紅綠測 tier↔vintage 不變式與清單一致性。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("_a→Tier A/不 vintage", _a("X", "x").tier == "A" and _a("X", "x").vintage is False)
    chk("_b→Tier B/vintage", _b("Y", "y").tier == "B" and _b("Y", "y").vintage is True)
    chk("tier↔vintage 不變式(vintage⇔B、tier∈{A,B})",
        all(s.tier in ("A", "B") and s.vintage == (s.tier == "B") for s in SERIES))
    ids = series_ids()
    chk("series_id 無重複(vintage_map 不覆蓋)", len(ids) == len(set(ids)))
    chk("vintage_map 鍵集=series_ids", set(vintage_map()) == set(ids))
    chk("A/B 兩層皆非空", any(s.tier == "A" for s in SERIES) and any(s.tier == "B" for s in SERIES))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.macro --selftest;免 DB 免 API)")
