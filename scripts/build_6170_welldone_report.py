#!/usr/bin/env python3
"""6170 統振近五年財務＋五年前景＋全球競爭力報告產生器。

🎯 這支在做什麼（白話）：把已溯源的公開財報／監理／產業數字編成繁中 Markdown 與 PDF。
本環境無 Augur DB，不打 FinMind／FRED。輸出不是進出場建議。

守原則精華 #1 #9 #10 #15；CLAUDE #16。

執行指令矩陣：
  python3 scripts/build_6170_welldone_report.py              # 寫 reports/ 的 md＋pdf
  python3 scripts/build_6170_welldone_report.py --pdf-only   # 只寫 pdf
  python3 scripts/build_6170_welldone_report.py --md-only    # 只寫 md
  python3 scripts/build_6170_welldone_report.py --selftest   # 純函式餵真輸入（零 IO）
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
OUT_STEM = "augur_6170_welldone_5y_finance_outlook_20260827"
REPORT_DATE = "2026-08-27"
VIEWPOINT = "2026-08-27T13:35+08:00"
PRICE = 48.65
PRICE_SRC = "HiStock 2026-08-27 收盤"
SHARES = 97_260_038
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

# 單位：新台幣千元。季損益＝HiStock 單季；2024／2025 全年損益＝114 年報致股東報告。
# 2026H1＝MOPS 2026-08-07 董事會公告（歸屬母公司淨利／EPS 用公告數）。
Q_IS = {
    "2021Q1": {"rev": 719522, "gp": 165068, "oi": 47383, "pbt": 49459, "ni": 44653, "eps": 0.44},
    "2021Q2": {"rev": 738741, "gp": 143039, "oi": 32278, "pbt": 22774, "ni": 20943, "eps": 0.20},
    "2021Q3": {"rev": 759407, "gp": 158338, "oi": 37174, "pbt": 44270, "ni": 44991, "eps": 0.40},
    "2021Q4": {"rev": 759314, "gp": 165168, "oi": 26752, "pbt": 86215, "ni": 94583, "eps": 0.82},
    "2022Q1": {"rev": 768566, "gp": 154319, "oi": 37979, "pbt": 56638, "ni": 57753, "eps": 0.54},
    "2022Q2": {"rev": 754146, "gp": 172966, "oi": 42457, "pbt": 101638, "ni": 102677, "eps": 1.17},
    "2022Q3": {"rev": 457641, "gp": 138076, "oi": 33647, "pbt": 65387, "ni": 57047, "eps": 0.65},
    "2022Q4": {"rev": 488441, "gp": 143209, "oi": 39238, "pbt": 38134, "ni": 32277, "eps": 0.37},
    "2023Q1": {"rev": 543444, "gp": 147572, "oi": 46771, "pbt": 59728, "ni": 50016, "eps": 0.57},
    "2023Q2": {"rev": 510476, "gp": 155064, "oi": 48040, "pbt": 79287, "ni": 64140, "eps": 0.73},
    "2023Q3": {"rev": 590034, "gp": 194389, "oi": 59325, "pbt": 144163, "ni": 127600, "eps": 1.35},
    "2023Q4": {"rev": 617433, "gp": 203264, "oi": 69227, "pbt": 45089, "ni": 12897, "eps": 0.09},
    "2024Q1": {"rev": 700357, "gp": 212837, "oi": 50602, "pbt": 106593, "ni": 81282, "eps": 0.94},
    "2024Q2": {"rev": 693850, "gp": 207138, "oi": -4050, "pbt": 34709, "ni": 10972, "eps": 0.49},
    "2024Q3": {"rev": 736872, "gp": 214967, "oi": 68339, "pbt": 62695, "ni": 49182, "eps": 0.51},
    "2024Q4": {"rev": 774858, "gp": 230450, "oi": 152149, "pbt": 211468, "ni": 188235, "eps": 1.45},
    "2025Q1": {"rev": 817850, "gp": 257538, "oi": 92680, "pbt": 119520, "ni": 96730, "eps": 0.99},
    "2025Q2": {"rev": 785480, "gp": 240783, "oi": 79963, "pbt": 98071, "ni": 77366, "eps": 0.80},
    "2025Q3": {"rev": 813488, "gp": 261759, "oi": 78350, "pbt": 193255, "ni": 155161, "eps": 1.60},
    "2025Q4": {"rev": 769634, "gp": 237467, "oi": 61833, "pbt": 135373, "ni": 108503, "eps": 1.10},
    "2026Q1": {"rev": 823238, "gp": 256194, "oi": 76202, "pbt": 131761, "ni": 106264, "eps": 1.09},
    "2026Q2": {"rev": 765382, "gp": 258349, "oi": 79273, "pbt": 133686, "ni": 107349, "eps": 1.10},
}

# 年報／MOPS 覆蓋全年或半年（優先於季加總）。NI＝本期淨利；parent＝歸屬母公司。
ANNUAL_OVERRIDE = {
    2024: {"rev": 2905937, "gp": 865392, "ni": 330117, "eps": 3.39, "roe_ar": 0.17, "src": "114年報致股東報告"},
    2025: {"rev": 3186452, "gp": 997547, "ni": 437168, "eps": 4.49, "roe_ar": 0.21, "src": "114年報致股東報告"},
}
H1_2026 = {
    "rev": 1588620, "gp": 514543, "oi": 155524, "pbt": 265447,
    "ni": 213613, "parent": 212478, "eps": 2.18,
    "assets": 5316318, "liab": 3345744, "equity_parent": 1955685,
    "src": "MOPS 2026-08-07 第2季財務報告提報董事會",
}

# 資產負債：HiStock 季底千元。
BS = {
    "2021Q4": {"ca": 2373095, "ppe": 480447, "assets": 3201366, "cl": 1613861, "lt": 42526, "liab": 1656387, "eq": 1544979},
    "2022Q4": {"ca": 2304386, "ppe": 412935, "assets": 3166054, "cl": 1718444, "lt": 39456, "liab": 1757900, "eq": 1408154},
    "2023Q4": {"ca": 3431321, "ppe": 402916, "assets": 4119371, "cl": 2131381, "lt": 36510, "liab": 2167891, "eq": 1951480},
    "2024Q4": {"ca": 3793759, "ppe": 394624, "assets": 4471551, "cl": 2473872, "lt": 37040, "liab": 2510912, "eq": 1960639},
    "2025Q4": {"ca": 3652091, "ppe": 389492, "assets": 4373909, "cl": 2191799, "lt": 37630, "liab": 2229429, "eq": 2144480},
    "2026Q1": {"ca": 4383559, "ppe": 387732, "assets": 5096925, "cl": 3204414, "lt": 37623, "liab": 3242037, "eq": 1854888},
}

# HiStock 現金流：由季與季不單調累加，判為單季非 YTD。單位千元。
CFQ = {
    "2021": {"ocf": [276481, 48148, -202069, -109057], "icf": [-147804, -343263, 88005, -104309], "fcf_fin": [216050, -88068, 19635, 63200]},
    "2022": {"ocf": [34454, -118324, 549699, -273905], "icf": [-90043, -58814, -234574, 88353], "fcf_fin": [67071, 34941, -181237, 363600]},
    "2023": {"ocf": [135621, -678131, -75719, -71842], "icf": [-229328, 236635, 250219, -24077], "fcf_fin": [-165440, 392051, -130427, 75511]},
    "2024": {"ocf": [-281241, 388422, 487677, -189396], "icf": [-12613, -4629, -1791, 53758], "fcf_fin": [367430, -368329, -333562, 152296]},
    "2025": {"ocf": [-399980, 302463, 208371, 168095], "icf": [-2594, -77, -930, -9297], "fcf_fin": [167730, -318869, -58913, -128607]},
}

# 現金股利＝發放年度（對前一會計年度盈餘）。nStock／鉅亨。
DIVIDEND_PAID = {
    2022: 1.60, 2023: 2.10, 2024: 2.73, 2025: 3.11, 2026: 4.00,
}
EPS_FOR_PAYOUT = {2022: 1.86, 2023: 2.73, 2024: 2.74, 2025: 3.39, 2026: 4.49}

MONTHLY_2026 = {
    1: 278.59, 2: 262.28, 3: 282.39, 4: 257.21, 5: 250.88, 6: 257.31, 7: 270.41,
}
YTD_JUL_2026 = 1859.05  # 百萬
YTD_JUL_2025 = 1885.90
JUL_2026 = 270.405  # 公告千元→百萬 270.405
JUL_2025 = 281.857

MIX_2025 = {"通訊服務": (2611974, 81.97), "IC及其他通路": (574478, 18.03)}


def _sum_qs(year: int, key: str) -> int:
    return sum(Q_IS[f"{year}Q{q}"][key] for q in (1, 2, 3, 4))


def year_is(year: int) -> dict:
    """回傳該年損益（千元）與年報覆蓋標記。"""
    rev = _sum_qs(year, "rev")
    gp = _sum_qs(year, "gp")
    oi = _sum_qs(year, "oi")
    pbt = _sum_qs(year, "pbt")
    ni = _sum_qs(year, "ni")
    eps = round(sum(Q_IS[f"{year}Q{q}"]["eps"] for q in (1, 2, 3, 4)), 2)
    src = "HiStock 單季加總"
    ov = ANNUAL_OVERRIDE.get(year)
    if ov:
        rev, gp, ni, eps = ov["rev"], ov["gp"], ov["ni"], ov["eps"]
        src = ov["src"]
    return {
        "rev": rev, "gp": gp, "oi": oi, "pbt": pbt, "ni": ni, "eps": eps, "src": src,
        "gm": gp / rev, "om": oi / rev, "nm": ni / rev,
    }


def yoy(cur: float, prev: float) -> float | None:
    if prev == 0:
        return None
    return cur / prev - 1.0


def yi(v: float) -> str:
    """千元 → 億，兩位小數。"""
    return f"{v / 100000:.2f}"


def pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    return f"{x * 100:.{digits}f}%"


def signed_pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x * 100:.{digits}f}%"


def avg_equity_roe(year: int, ni: int) -> float:
    cur = BS[f"{year}Q4"]["eq"]
    prev_key = f"{year - 1}Q4"
    if prev_key not in BS:
        return ni / cur
    return ni / ((BS[prev_key]["eq"] + cur) / 2)


def derived() -> dict:
    years = [2021, 2022, 2023, 2024, 2025]
    rows = {y: year_is(y) for y in years}
    for y in years[1:]:
        rows[y]["rev_yoy"] = yoy(rows[y]["rev"], rows[y - 1]["rev"])
        rows[y]["ni_yoy"] = yoy(rows[y]["ni"], rows[y - 1]["ni"])
    rows[2021]["rev_yoy"] = None
    rows[2021]["ni_yoy"] = None
    for y in years:
        rows[y]["roe"] = avg_equity_roe(y, rows[y]["ni"])
        b = BS[f"{y}Q4"]
        rows[y]["debt"] = b["liab"] / b["assets"]
        rows[y]["cr"] = b["ca"] / b["cl"]
        rows[y]["ocf"] = sum(CFQ[str(y)]["ocf"])
        rows[y]["icf"] = sum(CFQ[str(y)]["icf"])
        rows[y]["fin"] = sum(CFQ[str(y)]["fcf_fin"])
    h1_25_rev = Q_IS["2025Q1"]["rev"] + Q_IS["2025Q2"]["rev"]
    h1_25_gp = Q_IS["2025Q1"]["gp"] + Q_IS["2025Q2"]["gp"]
    h1_25_oi = Q_IS["2025Q1"]["oi"] + Q_IS["2025Q2"]["oi"]
    h1_25_ni = Q_IS["2025Q1"]["ni"] + Q_IS["2025Q2"]["ni"]
    ttm_eps = (
        Q_IS["2025Q3"]["eps"] + Q_IS["2025Q4"]["eps"]
        + Q_IS["2026Q1"]["eps"] + Q_IS["2026Q2"]["eps"]
    )
    mkt = PRICE * SHARES
    bvps = H1_2026["equity_parent"] / SHARES * 1000  # 千元權益／股數 → 元
    pe = PRICE / ttm_eps
    pb = PRICE / bvps
    dy = DIVIDEND_PAID[2026] / PRICE
    payout = {y: DIVIDEND_PAID[y] / EPS_FOR_PAYOUT[y] for y in DIVIDEND_PAID}
    # 500 億÷1,291.1136 億；金額單位彼此約分，與千元／億無關。
    qpay_share = 500.0 / 1291.1136
    return {
        "rows": rows,
        "h1_25": {"rev": h1_25_rev, "gp": h1_25_gp, "oi": h1_25_oi, "ni": h1_25_ni},
        "h1_26_rev_yoy": yoy(H1_2026["rev"], h1_25_rev),
        "h1_26_oi_yoy": yoy(H1_2026["oi"], h1_25_oi),
        "h1_26_ni_yoy": yoy(H1_2026["parent"], h1_25_ni),
        "ttm_eps": ttm_eps,
        "mkt": mkt,
        "bvps": bvps,
        "pe": pe,
        "pb": pb,
        "dy": dy,
        "payout": payout,
        "qpay_share": qpay_share,
        "jul_yoy": JUL_2026 / JUL_2025 - 1,
        "ytd_jul_yoy": YTD_JUL_2026 / YTD_JUL_2025 - 1,
        "nonop_2025": rows[2025]["pbt"] - rows[2025]["oi"],
        "nonop_h1": H1_2026["pbt"] - H1_2026["oi"],
        "debt_h1": H1_2026["liab"] / H1_2026["assets"],
    }


def _selftest() -> int:
    """純函式餵真輸入：年加總、年報覆蓋、ROE、市值、配發率。禁字面 haystack。"""
    ok = True

    def chk(name: str, cond: bool, detail: str = ""):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}{('  ' + detail) if detail else ''}")

    r21 = year_is(2021)
    chk("2021 營收＝四季加總", r21["rev"] == 2976984, str(r21["rev"]))
    chk("2021 毛利＝四季加總", r21["gp"] == 631613)
    chk("2021 稅後＝四季加總", r21["ni"] == 205170)
    chk("2021 EPS 季加總 1.86", abs(r21["eps"] - 1.86) < 1e-9)
    r25 = year_is(2025)
    chk("2025 營收用年報 3186452 非整季加總", r25["rev"] == 3186452)
    chk("2025 稅後用年報 437168", r25["ni"] == 437168)
    qsum_ni = _sum_qs(2025, "ni")
    chk("年報淨利與季加總差距 < 100 萬", abs(qsum_ni - 437168) < 1000, f"季加總={qsum_ni}")
    roe25 = avg_equity_roe(2025, 437168)
    chk("2025 ROE（平均權益）約 21.3%", 0.210 < roe25 < 0.216, f"{roe25:.4f}")
    d = derived()
    chk("TTM EPS＝4.89", abs(d["ttm_eps"] - 4.89) < 1e-9, str(d["ttm_eps"]))
    chk("2026 配發率＝4/4.49", abs(d["payout"][2026] - 4.00 / 4.49) < 1e-12)
    chk("市值＝價×股數", abs(d["mkt"] - PRICE * SHARES) < 1e-6)
    chk("H1 毛利率＝GP/Rev", abs(H1_2026["gp"] / H1_2026["rev"] - 514543 / 1588620) < 1e-15)
    # 下游絆線：把 2021Q1 營收抽走應讓年加總不再等於 2976984
    saved = Q_IS["2021Q1"]["rev"]
    Q_IS["2021Q1"]["rev"] = 0
    broken = year_is(2021)["rev"]
    Q_IS["2021Q1"]["rev"] = saved
    chk("絆線：抽走 2021Q1 營收則年加總必變", broken != 2976984, str(broken))
    chk("絆線復原後加總回來", year_is(2021)["rev"] == 2976984)
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _charts(d: dict, tmpdir: Path) -> dict[str, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font_manager.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
    plt.rcParams["axes.unicode_minus"] = False
    years = [2021, 2022, 2023, 2024, 2025]
    rows = d["rows"]
    paths = {}

    fig, ax = plt.subplots(figsize=(8.2, 3.6), dpi=140)
    x = list(range(len(years)))
    w = 0.36
    rev = [rows[y]["rev"] / 100000 for y in years]
    ni = [rows[y]["ni"] / 100000 for y in years]
    ax.bar([i - w / 2 for i in x], rev, w, color="#1f4e79", label="營收（億）")
    ax.bar([i + w / 2 for i in x], ni, w, color="#c45911", label="稅後淨利（億）")
    ax.set_xticks(x, [str(y) for y in years])
    ax.set_ylabel("新台幣億元")
    ax.set_title("統振 6170｜近五年營收與稅後淨利")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p1 = tmpdir / "rev_ni.png"
    fig.savefig(p1)
    plt.close()
    paths["rev_ni"] = p1

    fig, ax = plt.subplots(figsize=(8.2, 3.6), dpi=140)
    ax.plot(years, [rows[y]["gm"] * 100 for y in years], "o-", color="#2e7d32", label="毛利率")
    ax.plot(years, [rows[y]["om"] * 100 for y in years], "s-", color="#1565c0", label="營益率")
    ax.plot(years, [rows[y]["nm"] * 100 for y in years], "^-", color="#c62828", label="淨利率")
    ax.set_ylabel("%")
    ax.set_title("統振 6170｜近五年利潤率")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p2 = tmpdir / "margins.png"
    fig.savefig(p2)
    plt.close()
    paths["margins"] = p2

    fig, ax = plt.subplots(figsize=(8.2, 3.6), dpi=140)
    eps = [rows[y]["eps"] for y in years]
    div = [DIVIDEND_PAID[y + 1] for y in years]  # 次年發放
    ax.plot(years, eps, "o-", color="#1f4e79", label="EPS（該年）")
    ax.plot(years, div, "s--", color="#c45911", label="次年現金股利")
    ax.set_ylabel("元／股")
    ax.set_title("統振 6170｜EPS 與次年現金股利")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p3 = tmpdir / "eps_div.png"
    fig.savefig(p3)
    plt.close()
    paths["eps_div"] = p3
    return paths


def build_markdown(d: dict) -> str:
    rows = d["rows"]
    h1 = H1_2026
    lines = []
    a = lines.append
    a("---")
    a("title: 6170 統振近五年財務、五年前景與全球競爭力")
    a(f"date: {REPORT_DATE}")
    a(f"viewpoint: {VIEWPOINT}")
    a('stock_id: "6170"')
    a('layer: "[I]"')
    a("self_reported: true")
    a(f"price_tip: {REPORT_DATE}")
    a("fs_tip: 2026-06-30")
    a("not_advice: true")
    a("---")
    a("")
    a("# 6170 統振｜近五年財務分析、產業五年前景與全球競爭力")
    a("")
    a(f"> **一句**：營收從 2023 低點 22.61 億回到 2025 的 **31.86 億**（五年新高），EPS 從 1.86 走到 **4.49**，配息同步到 **4.00 元**。成長主軸是移工小額匯兌（Q Pay），不是電信預付卡。2026 年前七月營收年減 1.42%，本業營益率大致持平，淨利仍被美元資產評價等非營業項放大——把 EPS 當「匯款爆發」會高估本業速度。")
    a("> **不是**：進出場建議、目標價、可交易訊號。本報告 self-reported；數字皆有出處。")
    a("")
    a("## 0. 公司、資料範圍、這次為什麼沒有庫內列")
    a("")
    a("統振股份有限公司（TPEX 6170，ISIN TW0006170004，英文 WELLDONE）。1977-08-19 設立，2002-04-16 上櫃，櫃買分類「通信網路業」。實收資本 9.73 億、發行 **97,260,038** 股、面額 10 元。董事長陳威宇、總經理／發言人何明哲。簽證勤業眾信。最大法人股東宏碁（2353）持股約 **12.81%**（鉅亨 2026-03-13）。")
    a("")
    a("本業已從電池／電信通路轉成「外籍人士生活服務」：")
    a("")
    a("1. **金融科技／Q Pay（QuickPay）**：台灣第一家取得金管會外籍移工國外小額匯兌執照（2019 沙盒、2021 許可、2024-10 續照）。114 年報：有效會員逾 40 萬、全年處理匯款金額突破 **500 億元**。")
    a("2. **電信預付卡**：台灣大哥大外勞預付卡銷售；機場（桃園、小港）入境電信櫃台。年報寫：打詐管制＋費率下滑，此塊當穩定現金流、不再當成長引擎。")
    a("3. **國際人力／移工仲介**與 **快速購旅行社（Q Go）**：票務與返鄉，生態圈延伸。")
    a("4. **通路（子公司東旺利，持股 92.26%）**：電信器材、食品化妝品、金頂電池等代理。114 年報部門：通訊服務 **81.97%**、IC 及其他通路 **18.03%**。")
    a("")
    a(f"**本輪資料邊界（誠實）**：Cloud Agent 環境無 Augur PostgreSQL、無 `.env`，故 **沒有** `TaiwanStockFinancialStatements` 庫內列。本報告不開 FinMind／FRED。數字改走公開通道：公司年報／IR、MOPS 公告、金管會銀行局、勞動部／內政部轉述、World Bank、Wise FY25 RNS、Western Union 2024 Form 10-K、HiStock 季報彙整、PChome 月營收。HiStock 為加總／展示層，**全年 2024–2025 以年報為準**，季報用來看路徑與 2021–2023。")
    a("")
    a(f"流通股 {SHARES:,}。收盤 **{PRICE:.2f}**（{PRICE_SRC}）→ 市值約 **{d['mkt']/1e8:.1f} 億**。近四季 EPS {d['ttm_eps']:.2f} → 本益比 **{d['pe']:.1f}×**；2026Q2 歸屬母公司權益每股淨值 **{d['bvps']:.2f}** → 淨值比 **{d['pb']:.2f}×**；現金股利 4.00／收盤 → 殖利率 **{pct(d['dy'], 2)}**。")
    a("")
    a("## 1. 近五年損益")
    a("")
    a("單位新台幣億元。2021–2023＝HiStock 單季加總；2024–2025 營收／毛利／淨利／EPS＝114 年報。營益率用季營業利益加總／營收（年報未單列營益，故標「季加總」）。")
    a("")
    a("| 年 | 營收 | 年增 | 毛利率 | 營益率 | 稅後淨利 | 淨利率 | EPS | ROE |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for y in (2021, 2022, 2023, 2024, 2025):
        r = rows[y]
        a(
            f"| {y} | {yi(r['rev'])} | {signed_pct(r['rev_yoy'])} | {pct(r['gm'])} | {pct(r['om'])} | {yi(r['ni'])} | {pct(r['nm'])} | {r['eps']:.2f} | {pct(r['roe'])} |"
        )
    a("")
    a("讀法：")
    a("")
    a("- **規模路徑是 V 型，不是直線**：2021 營收 29.77 億 → 2022 −17.1% → 2023 再 −8.4% 落到 22.61 億（疫情後移工回流空窗＋預付卡／通路調整）。2024 +28.5% 回到 29.06 億，2025 再 +9.65% 到 **31.86 億**，五年新高。")
    a("- **利潤率上台階**：毛利率 2021 的 21.2% 走到 2023 以後約 30–31%。營益率從 4.8% 升到約 9–10%。這與匯款（金流服務、高毛利）占比上升、預付卡量縮一致。")
    a(f"- **淨利率跑得比營益率快**：2025 淨利率 13.7%、營益率 9.8%。年報明文：除匯款成長外，**持有美元資產因美元升值產生評價利益**也挹注淨利。2025 稅前淨利（季加總）{yi(rows[2025]['pbt'])} 億、營業利益 {yi(rows[2025]['oi'])} 億，差額約 **{yi(d['nonop_2025'])} 億**——不是小數。2026 上半年同樣：稅前 {yi(h1['pbt'])} 億、營業利益 {yi(h1['oi'])} 億。**EPS 成長有一塊不是本業。**")
    a("- **單季雜訊**：2024Q2 營業利益 −405 萬（唯一虧損季），同季稅後仍正；2023Q4 稅後只剩 0.13 億、EPS 0.09，營業利益卻有 0.69 億——非營業／稅務把單季打歪，看年或看營業利益。")
    a("- **ROE**：2021 約 13.3%（缺 2020 年底權益，用期末）→ 2025 **21.3%**（平均權益；與年報自陳 21%、Goodinfo 21.3% 同口徑）。高 ROE 搭配高配發，權益累積不快。")
    a("")
    a("114 年部門（年報產品組合，千元）：通訊服務 2,611,974（81.97%）、IC 及其他通路 574,478（18.03%）。通訊服務＝預付卡＋匯款等「對移工的服務收入」，不是設備製造。")
    a("")
    a("## 2. 2026 年迄今：營收走平、獲利仍增")
    a("")
    a("| 期間 | 營收 | 年增 | 毛利率 | 營業利益 | 稅後（母公司） | EPS | 來源 |")
    a("|---|---:|---:|---:|---:|---:|---:|---|")
    a(f"| 2026Q1 | {yi(Q_IS['2026Q1']['rev'])} | {signed_pct(yoy(Q_IS['2026Q1']['rev'], Q_IS['2025Q1']['rev']))} | {pct(Q_IS['2026Q1']['gp']/Q_IS['2026Q1']['rev'])} | {yi(Q_IS['2026Q1']['oi'])} | {yi(Q_IS['2026Q1']['ni'])} | 1.09 | HiStock 單季 |")
    a(f"| 2026Q2 | {yi(Q_IS['2026Q2']['rev'])} | {signed_pct(yoy(Q_IS['2026Q2']['rev'], Q_IS['2025Q2']['rev']))} | {pct(Q_IS['2026Q2']['gp']/Q_IS['2026Q2']['rev'])} | {yi(Q_IS['2026Q2']['oi'])} | {yi(Q_IS['2026Q2']['ni'])} | 1.10 | HiStock 單季 |")
    a(f"| 2026H1 | {yi(h1['rev'])} | {signed_pct(d['h1_26_rev_yoy'])} | {pct(h1['gp']/h1['rev'])} | {yi(h1['oi'])} | {yi(h1['parent'])} | {h1['eps']:.2f} | MOPS 公告 |")
    a(f"| 2026 1–7 月 | {YTD_JUL_2026/100:.2f} | {signed_pct(d['ytd_jul_yoy'])} | — | — | — | — | 鉅亨／PChome 月營收 |")
    a("")
    a(f"7 月單月 2.70 億，年增 {signed_pct(d['jul_yoy'], 2)}。H1 營收年增 {signed_pct(d['h1_26_rev_yoy'])}，營業利益年增 {signed_pct(d['h1_26_oi_yoy'])}，歸屬母公司淨利相對 2025H1 季加總仍年增約 {pct(d['h1_26_ni_yoy'])}（2025H1 季加總稅後 1.74 億，口徑為綜合損益稅後、與歸屬母公司略有差異）。")
    a("")
    a("讀法：2026 不是 2024 那種「營收跳 28%」的年份。量走平、組合與非營業項撐 EPS。若要把 2025 的 32% 淨利成長外推五年，2026 前七個月**還沒提供證據**。")
    a("")
    a("## 3. 資產負債、現金、匯兌浮額")
    a("")
    a("匯兌業者資產負債表會隨客戶款進出大幅擺動，負債比高不一定是「借太多去擴產」。")
    a("")
    a("| 時點 | 資產 | 權益 | 負債比 | 流動比 | 流動資產 | 流動負債 |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    for key, lab in [("2021Q4", "2021年底"), ("2022Q4", "2022年底"), ("2023Q4", "2023年底"), ("2024Q4", "2024年底"), ("2025Q4", "2025年底"), ("2026Q1", "2026Q1")]:
        b = BS[key]
        a(f"| {lab} | {yi(b['assets'])} | {yi(b['eq'])} | {pct(b['liab']/b['assets'])} | {b['ca']/b['cl']:.2f} | {yi(b['ca'])} | {yi(b['cl'])} |")
    a(f"| 2026Q2 | {yi(h1['assets'])} | {yi(h1['equity_parent'])}（母公司） | {pct(d['debt_h1'])} | — | — | — |")
    a("")
    a("長期借款極低（約 0.37–0.43 億），槓桿幾乎全是流動負債——符合代收代付／匯款清算。2026Q2 資產 53.16 億、負債 33.46 億，比 2025 年底資產 43.74 億明顯膨脹，是浮額不是突然變重資產公司。PPE 五年緩降（4.80→3.89 億），這家不是製造廠。")
    a("")
    a("2023Q2→Q3 淨值從 14.05 億跳到 19.37 億，遠大於當季盈餘；同期長期投資下降、投資現金流為正。本資料集**不能**把該跳升拆成「現增／評價／處分利益」各多少——只記錄有這一跳。")
    a("")
    a("年度營業現金流（HiStock 單季加總，億）：")
    a("")
    a("| 年 | 營業 CF | 投資 CF | 融資 CF | 稅後淨利 |")
    a("|---|---:|---:|---:|---:|")
    for y in (2021, 2022, 2023, 2024, 2025):
        r = rows[y]
        a(f"| {y} | {yi(r['ocf'])} | {yi(r['icf'])} | {yi(r['fin'])} | {yi(r['ni'])} |")
    a("")
    a("2023 營業 CF −6.90 億 vs 淨利 +2.55 億——清算／營運資金可以把會計盈餘和現金拉開一整年。2024 營業 CF 4.05 億高於淨利；2025 2.79 億低於淨利 4.37 億。**不能用「年年營業 CF＞淨利」形容這家。** 2026Q1 營業 CF −1.18 億。高配息在融資項（2025 融資 CF 四季合計約 −3.39 億）。")
    a("")
    a("## 4. 股利、評價、籌碼位置")
    a("")
    a("| 發放年 | 現金股利 | 對應 EPS（前年） | 粗配發率 | 除息日 |")
    a("|---|---:|---:|---:|---|")
    a("| 2022 | 1.60 | 1.86 | 86.0% | 2022-07-14 |")
    a("| 2023 | 2.10 | 2.73 | 76.9% | 2023-07-18 |")
    a("| 2024 | 2.73 | 2.74 | 99.6% | 2024-07-15 |")
    a("| 2025 | 3.11 | 3.39 | 91.7% | 2025-07-10 |")
    a("| 2026 | **4.00** | 4.49 | **89.1%** | 2026-07-08 |")
    a("")
    a("2026-07-08 除息 4 元，除息前收盤 52.30、參考價 48.3（鉅亨）。之後收盤回到約 48.7 附近——以 08-27 的 48.65 看，息值尚未用股價漲幅補回。配發率接近九成：股東拿到現金，公司留下的成長資本薄。這與「要建移工生態圈、升級 Q Pay 核心系統」（年報新管理層承諾）並存——擴張若要加速，不是靠留存盈餘就是靠負債／現增，目前長期債幾乎沒有。")
    a("")
    a(f"評價（{REPORT_DATE}）：本益 {d['pe']:.1f}×、淨值 {d['pb']:.2f}×、現金殖利率 {pct(d['dy'], 2)}。近四季 EPS 已把 2025Q3 的 1.60（含較高非營業）算進去；若非營業項明年縮小，這個本益比的分母會下降。**殖利率高＝市場在付「配得多」，不是付「全球匯款龍頭倍數」。**")
    a("")
    a("## 5. 產業五年前景（2026–2030）")
    a("")
    a("### 5.1 需求：台灣缺工是慢變數，不是循環")
    a("")
    a("勞動部／內政部轉述：2025 年底在台移工約 **85.9–86.6 萬**（年報 85.9 萬；知新聞引內政部 86.6 萬）。公司官網引國發會：至 **2030 年前再引進約 40 萬**外籍人力；總經理公開談話估 **2028 前後破百萬**。驅動是少子化、老化、產業與長照缺工（80 歲以上免巴氏量表申請家庭看護等政策放寬）。短中期人數往上的方向，公開人口統計與政策方向一致；**速度**仍取決許可數、來源國供給、薪資與地緣。")
    a("")
    a("這不是全球電子製造那種「明年倍增或腰斬」的賽道，是勞動力結構推著走的服務 TAM。人數 CAGR 個位數到低雙位數（公司／報導曾述近年約 7%）比「爆發成長」更像底稿。")
    a("")
    a("### 5.2 匯款池：合法管道在吃地下匯兌")
    a("")
    a("金管會銀行局（外籍移工國外小額匯兌）：")
    a("")
    a("- 2024：約 **842 億**、894 萬筆（年增金額 33.7%、筆數 46.9%）")
    a("- 2025H1：約 **603 億**")
    a("- 2025 全年：**1,291.1136 億**、1,235.9 萬筆（金額年增 53.36%、筆數年增 38.18%）；申報用戶未歸戶合計約 99.8 萬戶（可重複，故高於移工人數）")
    a("- 平均每筆 2025 約 1.04 萬（2024 約 0.94 萬）")
    a("")
    a("法規上限：每筆等值 3 萬、每月 5 萬、每年 50 萬；只准單向匯出。地下匯兌仍在。公司與媒體估「合法＋代結匯＋地下」可到約 **2,000 億**——此數是推估，不是金管會表。年報把地下匯兌寫成「尚待轉化的機會」，前提是打詐與電支條例把流量趕到持照業者。")
    a("")
    a("五年底稿（**不是預測，是機制**）：(a) 移工人數↑；(b) 合法滲透率↑；(c) 件均隨薪資微升。三者可以同向，使持照市場五年內再長一截；**不保證統振市占不變**。2025 的 53% 金額年增含低基期與滲透，不能當 2026–2030 的常態 CAGR。")
    a("")
    a("### 5.3 預付卡：成熟、受管制")
    a("")
    a("打詐造成申請收緊、費率下滑。年報把它降級為現金牛。五年前景＝守市占、不是敘事核心。機場櫃台吃入境旅客，與觀光／航班連動，不是移工結構那條慢坡。")
    a("")
    a("### 5.4 生態圈（票務、仲介、錢包）")
    a("")
    a("快速購旅行社 2024-08 設立（持股 67%），年報稱票務穩健、要與 Q Pay 協同。這塊 2025 還沒大到改寫部門占比（通路仍 18%）。五年要「匯款×通訊×旅運×消費」變成第二成長曲線，目前公開數字只證明**方向**，未證明**規模**。")
    a("")
    a("## 6. 全球競爭力")
    a("")
    a("### 6.1 先定座標：統振是台灣走廊專家，不是全球匯款網路")
    a("")
    a("| 層級 | 規模（已溯源） | 統振位置 |")
    a("|---|---|---|")
    a("| 全球對低收入／中等收入國匯款 | World Bank：2023 年約 **6,560 億美元**；預估 2024 +2.3%、2025 +2.8% 至約 **6,900 億美元** | 台灣持照移工匯出 2025 年 1,291 億台幣 ≈ **40 億美元**量級（以 32 元兌 1 美元粗換），約全球 LMIC 匯款的 **0.6%** |")
    a("| 全球多走廊 FinTech | Wise FY2025（至 2025-03-31）：跨境量 **1,452 億英鎊**、活躍客戶 1,560 萬 | Q Pay 2025 處理量 >500 億台幣 ≈ **16 億美元**；會員 40 萬。量差兩個數量級以上 |")
    a("| 全球品牌＋代理點 | Western Union 2024：合併營收 **42.097 億美元**；Consumer Money Transfer **37.980 億美元**（約 90%）；交易筆數年增 4%；代理點約 38 萬、200+ 國家 | 統振 2025 合併營收 31.86 億台幣 ≈ **1.0 億美元**；走廊＝台灣→越／印／菲／泰 |")
    a("| 台灣持照移工小額匯兌 | 2025 年 1,291 億；6 家持照（歐付寶 2026 核准、預計 Q4 推出） | 年報量 500 億／金管會市場 1,291 億 ≈ **38.7%**（下限，因「突破 500 億」可能更高）。業界估前两大合計約 6–7 成；CTWANT 曾寫 QuickPay 市占約 52%（口徑可能不同，並列不合併） |")
    a("")
    a("**全球競爭力一句**：在「台灣移工→東南亞四國」這條受監理的利基走廊，統振是先行者、前段班；在全球跨境支付產業裡，它不是 Wise／WU 的同場對手，也還不是可輸出的區域平台。年報「商業模式輸出、跨國經營」是願景，公開財報沒有海外營收占比可證。")
    a("")
    a("### 6.2 本地護城河（已看到的）")
    a("")
    a("1. **牌照時點**：第一張移工小額匯兌執照，七年會員與合規流程。")
    a("2. **預付卡通路**：移工來台就要通訊，這是匯款 App 的實體獲客口。電支業者嘆獲客成本可逾萬元、生態難抄（知新聞）。")
    a("3. **四語客服＋超商＋海外資金池**：公司稱 30 分鐘到帳。這是營運能力，不是不可複製，但是新進者的時間稅。")
    a("4. **網路效應雛形**：40 萬會員在約 86 萬移工裡不是飽和，但口碑在社群裡是真的進入障礙。")
    a("")
    a("### 6.3 本地與全球的競爭壓力")
    a("")
    a("| 對手類型 | 代表 | 對統振的含義 |")
    a("|---|---|---|")
    a("| 同業持照 | 東聯互動（活躍用戶 2026-03 底報 20 萬）、數位至匯、美家人力、融創 | 前两大仍約 6–7 成，但家數已到 6；價格／到帳／場景會被比 |")
    a("| 電支入場 | 歐付寶（6878），金管會核准兼營，預計 2026Q4 推 O`PAY | 第一次有「支付生態」而不是「匯款 App」來搶同一群人 |")
    a("| 銀行／傳統匯款 | 銀行電匯、西聯在台據點 | 費率與體驗通常較差，但是合規存量 |")
    a("| 地下匯兌 | 未持照掮客 | 仍是最大「市占」來源之一；打詐對持照業者偏多，但不會一夜消失 |")
    a("| 全球 App | Wise、Remitly、GCash 等 | 移工走廊有語言、現金提領、雇主／仲介場景；全球 App 未在公開資料顯示已拿走台灣持照市場。五年風險是**監理互認或大平台進來**，不是今天已被取代 |")
    a("")
    a("人力仲介出身的對手在「移工落地第一天」接觸；統振的第一天接觸是預付卡。兩種獲客口不同，五年會不會被仲介＋匯款一條龍吃掉，要看仲介牌照業者的產品，不是看全球品牌廣告。")
    a("")
    a("### 6.4 五年競爭力判斷（self-reported）")
    a("")
    a("- **守得住的**：台灣持照移工匯兌前段班，生態圈（卡＋匯＋票）比純匯款 App 完整。")
    a("- **還沒證明的**：商業模式輸出、對 Wise 級單位經濟的費率透明度、非移工跨境、雙向匯款（法規不准）。")
    a("- **會被打的點**：歐付寶與後續電支、東聯互動的社群滲透、預付卡獲客口若被打詐政策繼續縮。")
    a("- **全球分數**：利基領先、全球弱。把 6170 寫進「全球金融科技競爭力」而不加「台灣移工走廊」限定，是錯座標。")
    a("")
    a("## 7. 2026–2030 情境（基準，不是目標價）")
    a("")
    a("假設只討論公司基本面路徑，不推股價。")
    a("")
    a("| 情境 | 機制 | 營收看法 | EPS 看法 |")
    a("|---|---|---|---|")
    a("| **基準** | 移工緩增、合法滲透續升但速度低於 2025；預付卡持平或緩降；匯款市占被新進者削一點；美元評價不再年年同幅正貢獻 | 營收低至中個位數年增，落在 32–38 億帶 | 本業 EPS 未必跟 2025 的 4.49 直線外推；非營業項回歸後，更接近「營益率 9–10% 的服務公司」 |")
    a("| **偏多** | 地下匯兌加速合法化、件均與頻率升、Q Go／錢包提高 ARPU、市占守在四成上下 | 重新出現雙位數營收年增 | 配息可維持高，但配發率需略降才養得起系統升級 |")
    a("| **偏空** | 電支／銀行搶價、預付卡量再縮、匯率反向打美元資產、打詐誤傷通路 | 營收跌回 28 億附近或更低 | 高配發下現金與評價一起緊 |")
    a("")
    a("2026 年前七個月比較靠近**基準偏平**，不是偏多。年報 115 年方針是「以 Q Pay 為核心」——方向清楚，未給可核對的會員／量公開指引（公司無財務預測）。")
    a("")
    a("## 8. 風險（已在數字裡看到的）")
    a("")
    a("1. **盈餘品質**：淨利含美元資產評價。2025、2026H1 稅前都明顯高於營業利益。")
    a("2. **營收 2026 走平**：1–7 月年減 1.42%，與 2024–2025 的恢復段不同。")
    a("3. **配發率 ~89%**：留存薄；系統升級與生態圈擴張的資金不在帳上現金牛敘事裡自動出現。")
    a("4. **競爭家數 5→6、電支出場**：市占是存量優勢，不是法令鎖定的獨占。")
    a("5. **預付卡監理**：打詐收緊＝獲客口變窄。")
    a("6. **現金流與浮額**：單季營業 CF 可大幅為負；負債比隨清算跳。這是商業模式，也是流動性管理點。")
    a("7. **走廊集中**：法規單向、四國、台灣雇主市場。來源國政策、薪資、遣返、地緣都會打同一條 TAM。")
    a("8. **把本益比 10×、殖利率 8% 讀成「全球 FinTech 低估」**：評價付的是高配息台股服務股，不是跨境支付平台倍數。")
    a("")
    a("## 9. 來源")
    a("")
    a("- 公司：https://www.welldone.com.tw/ ｜關於我們｜114 年報致股東報告（樹懶生活轉載年報文本）｜114Q1 合併財報 PDF")
    a("- MOPS／鉅亨／MoneyDJ：2026-08-07 第 2 季財務報告提報董事會；2026-07 營收公告；2026-03-13 全年獲利與配息 4 元")
    a("- HiStock：損益表、EPS、資產表、負債與權益、現金流量表（2026-08-27 擷取）")
    a("- PChome 股市：月營收 2021–2026")
    a("- nStock／鉅亨除息：現金股利與除息日")
    a("- 金管會銀行局：外籍移工國外小額匯兌統計（2025-08-21 稿；2025 全年數字見知新聞引金管會）")
    a("- 勞動部／內政部移工人數：年報與知新聞轉述")
    a("- World Bank Migration and Development Brief，2024-06-26")
    a("- Wise plc FY25 RNS：跨境量 £145.2bn、客戶 15.6m")
    a("- Western Union Form 10-K year ended 2024-12-31：營收 $4,209.7m；CMT $3,798.0m；交易筆數 +4%；~380,000 agent locations")
    a("- MoneyDJ《移工匯兌市場添新戰友》；知新聞歐付寶入場；CTWANT 市占／2000 億推估（後者標推估）")
    a("")
    a("本報告 [I] 研究整理、self-reported 分析框架。**不是**投資建議。")
    a("")
    return "\n".join(lines) + "\n"


def _pdf_styles():
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont("WD", FONT_PATH, subfontIndex=0))
    ss = getSampleStyleSheet()
    styles = {
        "cover_kicker": ParagraphStyle("cover_kicker", fontName="WD", fontSize=10, textColor="#c45911", alignment=TA_CENTER, spaceAfter=8),
        "cover": ParagraphStyle("cover", fontName="WD", fontSize=20, leading=28, alignment=TA_CENTER, textColor="#1f4e79", spaceAfter=10),
        "cover_sub": ParagraphStyle("cover_sub", fontName="WD", fontSize=11, leading=16, alignment=TA_CENTER, textColor="#444444", spaceAfter=6),
        "h1": ParagraphStyle("h1", fontName="WD", fontSize=14, leading=20, textColor="#1f4e79", spaceBefore=12, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName="WD", fontSize=12, leading=17, textColor="#2e5a88", spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("body", fontName="WD", fontSize=9.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6, textColor="#222222"),
        "bullet": ParagraphStyle("bullet", fontName="WD", fontSize=9.5, leading=15, leftIndent=14, spaceAfter=3, textColor="#222222"),
        "cell": ParagraphStyle("cell", fontName="WD", fontSize=7.5, leading=10, alignment=TA_CENTER),
        "cell_l": ParagraphStyle("cell_l", fontName="WD", fontSize=7.5, leading=10, alignment=TA_LEFT),
        "foot": ParagraphStyle("foot", fontName="WD", fontSize=7.5, leading=10, textColor="#666666", alignment=TA_LEFT),
        "caption": ParagraphStyle("caption", fontName="WD", fontSize=8, leading=11, textColor="#555555", alignment=TA_CENTER, spaceAfter=10),
        "disc": ParagraphStyle("disc", fontName="WD", fontSize=8.5, leading=13, alignment=TA_JUSTIFY, textColor="#333333", spaceAfter=6),
    }
    return styles


def _tbl(data, col_w, styles):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    wrapped = []
    for i, row in enumerate(data):
        wr = []
        for j, cell in enumerate(row):
            st = styles["cell"] if j > 0 or i == 0 else styles["cell_l"]
            if i == 0:
                st = styles["cell"]
            wr.append(__import__("reportlab.platypus", fromlist=["Paragraph"]).Paragraph(str(cell), st))
        wrapped.append(wr)
    t = Table(wrapped, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "WD"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f4ef")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7f4ef"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c5c0b5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def build_pdf(d: dict, pdf_path: Path, charts: dict[str, Path]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

    styles = _pdf_styles()
    story = []
    P = lambda t, k="body": Paragraph(t, styles[k])

    story.append(Spacer(1, 14 * mm))
    story.append(P("AUGUR［I］研究整理　·　self-reported　·　非投資建議", "cover_kicker"))
    story.append(P("6170 統振 WELLDONE", "cover"))
    story.append(P("近五年財務分析、產業五年前景<br/>與全球競爭力報告", "cover"))
    story.append(Spacer(1, 5 * mm))
    story.append(P(f"觀點時點　{VIEWPOINT}", "cover_sub"))
    story.append(P(f"收盤價　{PRICE:.2f} 元（{PRICE_SRC}）　·　TPEX 通信網路　·　發行 {SHARES/1e4:.2f} 萬股", "cover_sub"))
    story.append(P(f"市值約 {d['mkt']/1e8:.1f} 億　·　本益 {d['pe']:.1f}×　·　淨值比 {d['pb']:.2f}×　·　現金殖利率 {pct(d['dy'], 2)}", "cover_sub"))
    story.append(Spacer(1, 8 * mm))
    story.append(P(
        f"營收從 2023 低點 22.61 億回到 2025 的 <b>31.86 億</b>（五年新高），EPS 從 1.86 走到 <b>4.49</b>，配息到 <b>4.00 元</b>。"
        "成長主軸是移工小額匯兌 Q Pay，不是電信預付卡。"
        f"2026 年前七月營收年減 {pct(d['ytd_jul_yoy'], 2)}；淨利含美元資產評價，不能把 EPS 全算本業。"
        "在台灣持照移工匯兌走廊屬前段班；全球跨境支付產業裡不是 Wise／WU 同場對手。",
        "body",
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(P(
        "本環境無 Augur 資料庫，未呼叫 FinMind／FRED。數字來自公司年報、MOPS 公告、金管會、World Bank、Wise FY25、Western Union 10-K、HiStock／PChome 公開彙整。分析框架為 self-reported，不得當成「世界如此」的權威確認。不是進出場建議、不是目標價。",
        "disc",
    ))
    story.append(PageBreak())

    story.append(P("0. 一句話與公司定位", "h1"))
    story.append(P(
        f"營收從 2023 低點 22.61 億回到 2025 的 <b>31.86 億</b>（五年新高），EPS 從 1.86 走到 <b>4.49</b>，配息到 <b>4.00 元</b>。"
        f"成長主軸是移工小額匯兌 Q Pay，不是電信預付卡。2026 年前七月營收年減 {pct(d['ytd_jul_yoy'], 2)}，"
        "本業營益率大致持平，淨利仍被美元資產評價等非營業項放大。把 EPS 當「匯款爆發」會高估本業速度。"
        "本報告不是進出場建議、不是目標價。",
    ))
    story.append(P(
        "統振股份有限公司（TPEX 6170，ISIN TW0006170004，WELLDONE）1977-08-19 設立、2002-04-16 上櫃。"
        "董事長陳威宇、總經理何明哲。最大法人股東宏碁持股約 12.81%（鉅亨 2026-03-13）。"
        "本業：① Q Pay 移工小額匯兌（台灣首張執照；年報：會員逾 40 萬、2025 處理匯款突破 500 億）；"
        "② 台灣大哥大外勞預付卡與桃園／小港機場電信櫃台；③ 仲介與快速購旅行社 Q Go；"
        "④ 子公司東旺利通路（持股 92.26%）。114 年部門：通訊服務 81.97%、IC 及其他通路 18.03%。",
    ))

    story.append(P("1. 近五年損益", "h1"))
    story.append(P("單位新台幣億元。2021–2023＝HiStock 單季加總；2024–2025 營收／毛利／淨利／EPS＝114 年報。營益率＝季營業利益加總／營收。"))
    rows = d["rows"]
    head = ["年", "營收", "年增", "毛利率", "營益率", "稅後", "淨利率", "EPS", "ROE"]
    data = [head]
    for y in (2021, 2022, 2023, 2024, 2025):
        r = rows[y]
        data.append([
            str(y), yi(r["rev"]), signed_pct(r["rev_yoy"]), pct(r["gm"]), pct(r["om"]),
            yi(r["ni"]), pct(r["nm"]), f"{r['eps']:.2f}", pct(r["roe"]),
        ])
    usable = 174 * mm
    story.append(_tbl(data, [usable * x for x in (0.09, 0.11, 0.11, 0.11, 0.11, 0.11, 0.12, 0.12, 0.12)], styles))
    story.append(Spacer(1, 3 * mm))
    story.append(Image(str(charts["rev_ni"]), width=170 * mm, height=75 * mm))
    story.append(P("圖 1　營收與稅後淨利（2024–2025 淨利／營收採年報）", "caption"))
    story.append(Image(str(charts["margins"]), width=170 * mm, height=75 * mm))
    story.append(P("圖 2　毛利率／營益率／淨利率。淨利率快於營益率＝非營業項（含美元評價）在墊 EPS。", "caption"))

    story.append(P("讀法", "h2"))
    story.append(P("規模是 V 型：2021 的 29.77 億跌到 2023 的 22.61 億（−17.1% 再 −8.4%），2024 +28.5%、2025 +9.65% 創五年新高。毛利率從 21% 走到 30–31%，營益率從 4.8% 走到約 9–10%，與匯款（高毛利金流服務）占比上升一致。"))
    story.append(P(
        f"淨利率跑贏營益率是關鍵品質問題。2025 稅前（季加總）{yi(rows[2025]['pbt'])} 億、營業利益 {yi(rows[2025]['oi'])} 億，差額約 {yi(d['nonop_2025'])} 億。"
        f"2026H1 稅前 {yi(H1_2026['pbt'])} 億、營業利益 {yi(H1_2026['oi'])} 億，差額 {yi(d['nonop_h1'])} 億。"
        "年報明文美元資產評價利益挹注淨利。EPS 從 3.39 到 4.49 不能全算本業。",
    ))
    story.append(P("雜訊：2024Q2 營業利益 −405 萬仍稅後為正；2023Q4 EPS 僅 0.09 但營業利益 0.69 億。看年、看營業利益，不看單季淨利說故事。"))

    story.append(P("2. 2026 年迄今", "h1"))
    h1 = H1_2026
    data = [
        ["期間", "營收", "年增", "毛利率", "營益", "母公司稅後／稅後", "EPS"],
        ["2026Q1", yi(Q_IS["2026Q1"]["rev"]), signed_pct(yoy(Q_IS["2026Q1"]["rev"], Q_IS["2025Q1"]["rev"])),
         pct(Q_IS["2026Q1"]["gp"] / Q_IS["2026Q1"]["rev"]), yi(Q_IS["2026Q1"]["oi"]), yi(Q_IS["2026Q1"]["ni"]), "1.09"],
        ["2026Q2", yi(Q_IS["2026Q2"]["rev"]), signed_pct(yoy(Q_IS["2026Q2"]["rev"], Q_IS["2025Q2"]["rev"])),
         pct(Q_IS["2026Q2"]["gp"] / Q_IS["2026Q2"]["rev"]), yi(Q_IS["2026Q2"]["oi"]), yi(Q_IS["2026Q2"]["ni"]), "1.10"],
        ["2026H1 公告", yi(h1["rev"]), signed_pct(d["h1_26_rev_yoy"]), pct(h1["gp"] / h1["rev"]),
         yi(h1["oi"]), yi(h1["parent"]), f"{h1['eps']:.2f}"],
        ["2026 1–7 月", f"{YTD_JUL_2026/100:.2f}", signed_pct(d["ytd_jul_yoy"]), "—", "—", "—", "—"],
    ]
    story.append(_tbl(data, [usable * x for x in (0.16, 0.14, 0.14, 0.14, 0.14, 0.16, 0.12)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P(
        f"7 月單月 2.70 億、年減 {pct(d['jul_yoy'], 2)}。H1 營收年減約 0.9%，營業利益年減約 {pct(d['h1_26_oi_yoy'])}，"
        "歸屬母公司淨利仍高於 2025H1 季加總稅後（口徑略異）。2026 不是 2024 那種營收跳 28% 的年份；量走平、非營業項撐 EPS。"
        "要把 2025 淨利 +32% 外推五年，前七個月沒有提供證據。",
    ))

    story.append(P("3. 資產負債與現金", "h1"))
    data = [["時點", "資產", "權益", "負債比", "流動比", "流動資產", "流動負債"]]
    for key, lab in [("2021Q4", "2021底"), ("2022Q4", "2022底"), ("2023Q4", "2023底"),
                     ("2024Q4", "2024底"), ("2025Q4", "2025底"), ("2026Q1", "2026Q1")]:
        b = BS[key]
        data.append([lab, yi(b["assets"]), yi(b["eq"]), pct(b["liab"] / b["assets"]),
                     f"{b['ca']/b['cl']:.2f}", yi(b["ca"]), yi(b["cl"])])
    data.append(["2026Q2", yi(h1["assets"]), yi(h1["equity_parent"]) + "母", pct(d["debt_h1"]), "—", "—", "—"])
    story.append(_tbl(data, [usable * x for x in (0.13, 0.14, 0.16, 0.13, 0.12, 0.16, 0.16)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P(
        "長期借款僅約 0.4 億，負債幾乎全是流動項——代收代付／匯款清算浮額，不是擴產槓桿。"
        "2026Q2 資產 53.16 億相對 2025 底 43.74 億的膨脹，是浮額。PPE 五年緩降，這家不是製造廠。"
        "2023Q2→Q3 淨值 14.05→19.37 億，大於當季盈餘；本資料集不能拆成現增／評價／處分各多少。",
    ))
    data = [["年", "營業CF", "投資CF", "融資CF", "稅後淨利"]]
    for y in (2021, 2022, 2023, 2024, 2025):
        r = rows[y]
        data.append([str(y), yi(r["ocf"]), yi(r["icf"]), yi(r["fin"]), yi(r["ni"])])
    story.append(_tbl(data, [usable * x for x in (0.16, 0.21, 0.21, 0.21, 0.21)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P(
        "HiStock 現金流判為單季（不單調累加）後再加總。2023 營業 CF −6.90 億 vs 淨利 +2.55 億；"
        "2025 營業 CF 2.79 億低於淨利 4.37 億。不能用「年年營業 CF＞淨利」形容匯兌業。"
        "2026Q1 營業 CF −1.18 億。高配息走融資項。",
    ))

    story.append(P("4. 股利與評價", "h1"))
    story.append(Image(str(charts["eps_div"]), width=170 * mm, height=75 * mm))
    story.append(P("圖 3　EPS 與「次年」現金股利（2025 盈餘→2026 配 4.00 元）", "caption"))
    data = [
        ["發放年", "現金股利", "對應 EPS", "粗配發率", "除息日"],
        ["2022", "1.60", "1.86", "86.0%", "2022-07-14"],
        ["2023", "2.10", "2.73", "76.9%", "2023-07-18"],
        ["2024", "2.73", "2.74", "99.6%", "2024-07-15"],
        ["2025", "3.11", "3.39", "91.7%", "2025-07-10"],
        ["2026", "4.00", "4.49", "89.1%", "2026-07-08"],
    ]
    story.append(_tbl(data, [usable * x for x in (0.18, 0.2, 0.2, 0.2, 0.22)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P(
        f"除息前收盤 52.30、參考價 48.3。{REPORT_DATE} 收盤 {PRICE:.2f}，息值尚未用漲幅補回。"
        f"本益 {d['pe']:.1f}×（TTM EPS {d['ttm_eps']:.2f}，含 2025Q3 的高非營業季）、"
        f"淨值比 {d['pb']:.2f}×（母公司 BPS {d['bvps']:.2f}）、現金殖利率 {pct(d['dy'], 2)}。"
        "市場在付高配息服務股，不是付全球跨境支付平台倍數。配發近九成與「要升級 Q Pay 核心系統」並存：留存薄。",
    ))

    story.append(P("5. 產業五年前景（2026–2030）", "h1"))
    story.append(P("需求", "h2"))
    story.append(P(
        "在台移工 2025 年底約 85.9–86.6 萬（年報／內政部轉述）。公司引國發會：2030 年前再引進約 40 萬；"
        "總經理談話估 2028 前後破百萬。驅動是少子化、老化、產業與長照缺工。這是勞動力結構的慢變數，"
        "不是電子製造那種明年倍增或腰斬的賽道。人數往上的方向與政策一致；速度仍取決許可、來源國與薪資。",
    ))
    story.append(P("合法匯款池", "h2"))
    story.append(P(
        "金管會外籍移工國外小額匯兌：2024 約 842 億／894 萬筆；2025H1 約 603 億；"
        "2025 全年 1,291.1136 億、1,235.9 萬筆（金額年增 53.36%）。平均每筆約 1.04 萬。"
        "上限每筆 3 萬、每月 5 萬、每年 50 萬、只准單向匯出。地下匯兌仍在；媒體／公司推估合計可到約 2,000 億——該數是推估。"
        "五年機制：(a) 人數↑ (b) 合法滲透↑ (c) 件均微升。2025 的 53% 含低基期，不能當 2026–2030 常態 CAGR。"
        "預付卡受打詐與費率下滑，年報降為現金牛。Q Go 票務是生態圈方向，2025 還沒改寫 18% 通路占比。",
    ))

    story.append(P("6. 全球競爭力", "h1"))
    data = [
        ["層級", "已溯源規模", "統振位置"],
        ["全球 LMIC 匯款", "World Bank 2023 約 6,560 億美元；2025 估約 6,900 億",
         "台灣持照移工匯出 2025 年 1,291 億台幣≈40 億美元，約全球 0.6%"],
        ["全球多走廊 FinTech", "Wise FY25 跨境量 1,452 億英鎊、客戶 1,560 萬",
         "Q Pay 2025＞500 億台幣≈16 億美元、會員 40 萬；量差兩個數量級"],
        ["全球品牌代理網路", "WU 2024 營收 42.10 億美元；CMT 37.98 億；據點約 38 萬、200+ 國",
         "統振 2025 營收 31.86 億台幣≈1.0 億美元；走廊＝台灣→越印菲泰"],
        ["台灣持照小額匯兌", "2025 年 1,291 億；持照 6 家（歐付寶 2026 核准）",
         "500／1,291≈38.7%（年報「突破 500 億」為下限）；業界前两大約 6–7 成"],
    ]
    story.append(_tbl(data, [usable * x for x in (0.22, 0.40, 0.38)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P(
        "<b>座標</b>：統振是「台灣移工→東南亞四國」受監理利基的先行者與前段班；"
        "不是 Wise／Western Union 的同場對手。年報「商業模式輸出、跨國經營」是願景，財報沒有海外營收占比可證。"
        "護城河：首張執照、預付卡獲客口、四語＋超商＋資金池（公司稱 30 分鐘到帳）、40 萬會員口碑。"
        "壓力：東聯互動等同業、歐付寶 2026Q4 電支生態入場、銀行與地下匯兌、打詐縮預付卡口。"
        "全球 App 尚未在公開資料顯示拿走台灣持照市場；五年風險是監理互認或大平台進來，不是今天已被取代。"
        "全球競爭力分數：利基領先、全球弱。不加「台灣移工走廊」限定就把 6170 寫進全球金融科技競爭力，是錯座標。",
    ))

    story.append(P("7. 2026–2030 情境（不是目標價）", "h1"))
    data = [
        ["情境", "機制", "營收看法", "EPS 看法"],
        ["基準", "移工緩增、滲透續升但慢於 2025；預付卡平或降；市占被削一點；匯率評價不再年年同幅正貢獻",
         "低至中個位數年增，約 32–38 億帶", "本業不必外推 4.49；非營業回歸後更像營益率 9–10% 的服務公司"],
        ["偏多", "地下匯兌加速合法化、ARPU 升、市占守約四成", "再出現雙位數年增", "高配息可維持，但配發率需略降才養系統"],
        ["偏空", "電支／銀行搶價、預付卡再縮、匯率反向、打詐誤傷", "跌回 28 億附近或更低", "高配發下現金與評價一起緊"],
    ]
    story.append(_tbl(data, [usable * x for x in (0.12, 0.38, 0.25, 0.25)], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(P("2026 年前七個月比較靠近基準偏平，不是偏多。公司無公開財務預測。"))

    story.append(P("8. 風險", "h1"))
    risks = [
        "盈餘品質：淨利含美元資產評價；2025 與 2026H1 稅前都明顯高於營業利益。",
        "營收 2026 走平：1–7 月年減 1.42%。",
        "配發率約 89%，留存薄，與系統升級承諾並存。",
        "持照家數 5→6，電支歐付寶入場，市占不是法令獨占。",
        "預付卡打詐收緊＝獲客口變窄。",
        "單季營業 CF 可大幅為負；負債比隨清算跳。",
        "走廊集中：單向、四國、台灣雇主市場。",
        "本益比約 10×、殖利率約 8% 不是「全球 FinTech 低估」。",
    ]
    for i, t in enumerate(risks, 1):
        story.append(P(f"{i}. {t}", "bullet"))

    story.append(P("9. 來源", "h1"))
    story.append(P(
        "公司 IR welldone.com.tw、114 年報致股東報告、MOPS 2026-08-07 第 2 季財報公告、"
        "鉅亨 2026-03-13／2026-07 月營收、HiStock 五大報表（2026-08-27）、PChome 月營收、"
        "nStock 股利、金管會銀行局移工小額匯兌統計、World Bank Migration and Development Brief 2024-06-26、"
        "Wise plc FY25 RNS（£145.2bn）、Western Union Form 10-K 2024（營收 $4,209.7m；CMT $3,798.0m）、"
        "MoneyDJ／知新聞／CTWANT（CTWANT 之 52% 市占與 2,000 億合計池標為報導／推估，不與金管會表合併）。",
        "disc",
    ))
    story.append(P("本檔為［I］研究整理。分析框架 self-reported。不是投資建議、不是目標價、不是可交易訊號。", "disc"))

    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("WD", 7.5)
        canvas.setFillColor("#666666")
        canvas.drawString(18 * mm, 10 * mm, "6170 統振｜［I］非投資建議｜self-reported")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{REPORT_DATE}  ·  {doc.page}")
        canvas.setStrokeColor("#1f4e79")
        canvas.setLineWidth(0.6)
        canvas.line(18 * mm, A4[1] - 12 * mm, A4[0] - 18 * mm, A4[1] - 12 * mm)
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.restoreState()

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title="6170 統振近五年財務、五年前景與全球競爭力",
        author="Augur [I] research",
    )
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="6170 統振財務前景報告產生器")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--pdf-only", action="store_true")
    p.add_argument("--md-only", action="store_true")
    p.add_argument("--out-dir", default=str(REPO / "reports"))
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not Path(FONT_PATH).is_file():
        print(f"缺少中文字型：{FONT_PATH}", file=sys.stderr)
        return 2
    d = derived()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{OUT_STEM}.md"
    pdf_path = out_dir / f"{OUT_STEM}.pdf"
    if not args.pdf_only:
        md_path.write_text(build_markdown(d), encoding="utf-8")
        print(f"wrote {md_path}")
    if not args.md_only:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            charts = _charts(d, Path(td))
            build_pdf(d, pdf_path, charts)
        print(f"wrote {pdf_path} size={pdf_path.stat().st_size}")
        artifacts = Path("/opt/cursor/artifacts")
        if artifacts.is_dir() or artifacts.is_symlink():
            artifacts.mkdir(parents=True, exist_ok=True)
            dest = artifacts / "6170_welldone_5y_finance_outlook_20260827.pdf"
            dest.write_bytes(pdf_path.read_bytes())
            print(f"copied {dest}")
            html = artifacts / "6170_welldone_report_download.html"
            html.write_text(
                """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8"/>
  <title>下載｜6170 統振財務前景報告 PDF</title>
  <style>
    body { font-family: "Noto Sans TC", "PingFang TC", sans-serif; max-width: 42rem; margin: 12vh auto; padding: 0 1.5rem; color: #222; }
    a.btn { display: inline-block; background: #1f4e79; color: #fff; padding: .75rem 1.25rem; border-radius: 6px; text-decoration: none; }
    .meta { color: #555; font-size: .9rem; }
  </style>
</head>
<body>
  <p class="meta">AUGUR［I］研究整理 · 非投資建議</p>
  <h1>6170 統振｜近五年財務、五年前景與全球競爭力</h1>
  <p>觀點時點 2026-08-27。請下載 PDF 閱讀全文、圖表與來源。</p>
  <p><a class="btn" href="6170_welldone_5y_finance_outlook_20260827.pdf" download>下載 PDF</a></p>
</body>
</html>
""",
                encoding="utf-8",
            )
            print(f"copied {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
