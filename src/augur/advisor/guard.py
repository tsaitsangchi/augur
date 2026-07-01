"""P6 生成後防幻覺閘 — 把三敵防護從 prompt 自律變成機械 gate。

🎯 顧問輸出送出前的最後守門:數字 ∈ payload、引號 ⊂ 檢索原文、無未來洩漏語、逆向不翻轉。
   任一不過 → 標記(供攔截/重生成)。這是 #1/#8/#15 在對話層的唯一可靠落地(無「哲學專屬豁免」)。
守 #1(數字/引文不編)· #8(anti-leakage)· #15(誠實)· 憲章 v1.17.0(哲學不凌駕數據、審查 C-1)。
"""
import re

_FUTURE_LEAK = re.compile(
    r"will (rise|fall|surge|crash|soar|plunge)|保證|必(漲|跌|賺)|下週.{0,6}(漲|跌)|明(日|天).{0,6}(漲|跌)|未來.{0,4}(會漲|會跌|必)")
_REVERSE = re.compile(
    r"所以.{0,8}(該|應|建議).{0,4}(賣|放空|反著|做空)|建議.{0,4}(賣出|放空|做空)|reverse the (call|model|score)|sell instead")


def guard(response, payload, citations):
    """回 {'pass': bool, 'issues': [str]}。issues 非空 = 應攔截/重生成。"""
    issues = []
    cite_texts = [c.text for c in citations]

    # ① 引文校驗:引號內容(≥8 字)須逐字存在於某 citation(防編造/潤飾引文)
    for quote in re.findall(r'[「『"]([^」』"]{8,})[」』"]', response):
        if not any(quote in t for t in cite_texts):
            issues.append(f"引文非逐字或非庫內(#1):{quote[:40]!r}")

    # ② 數字校驗:顯著小數(score/IC/Sharpe 類)須 ∈ payload(防編造預測數字)
    allowed = payload.numbers()
    for m in re.findall(r"\d+\.\d{2,}", response):
        if round(float(m), 4) not in allowed:
            issues.append(f"數字非 payload、疑編造(#1):{m}")

    # ③ 未來/保證語(#8 anti-leakage)
    if _FUTURE_LEAK.search(response):
        issues.append("含未來預測/保證語(#8)")

    # ④ 逆向翻轉(審查 C-1):逆向不得輸出與模型分數相反的行動含義
    if _REVERSE.search(response):
        issues.append("逆向鏡翻轉模型結論、輸出相反行動(禁、審查 C-1)")

    return {"pass": not issues, "issues": issues}
