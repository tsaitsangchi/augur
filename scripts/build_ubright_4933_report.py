#!/usr/bin/env python3
"""友輝光電（4933）近五年財務＋未來五年前景／全球競爭力報告 PDF 產生器。

守原則精華 #1 #9 #10 #15：數字只來自公開財報／交易所／公司揭露，
前瞻段落標示為情境分析（self-reported），不是股價預測或投資建議。

執行指令矩陣
  python3 scripts/build_ubright_4933_report.py
      產生 reports/ubright_4933_financial_outlook_20260827.pdf
  python3 scripts/build_ubright_4933_report.py --out /tmp/4933.pdf
  python3 scripts/build_ubright_4933_report.py --selftest
      零外部依賴：用季報加總核對年報官方數，錯則紅燈。
"""
from __future__ import annotations

import argparse
import sys
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# 公開財報（單位：新台幣仟元，除非另註）。來源見 PDF 附錄。
# 季報損益＝HiStock 轉載之公開財報；2024/2025 年報與公司個體財報核對。
# ---------------------------------------------------------------------------
QUARTERLY_PL = {
    # (rev, gp, oi, pretax, ni)
    (2021, 1): (692_946, 177_167, 88_505, 87_203, 69_281),
    (2021, 2): (745_322, 189_605, 98_221, 90_048, 71_734),
    (2021, 3): (771_573, 190_708, 97_187, 101_799, 81_020),
    (2021, 4): (752_406, 173_017, 79_460, 77_273, 69_664),
    (2022, 1): (692_204, 161_446, 81_732, 110_228, 88_305),
    (2022, 2): (696_842, 201_161, 114_008, 149_717, 118_928),
    (2022, 3): (409_811, 71_845, -4_440, 100_628, 80_175),
    (2022, 4): (493_394, 82_434, 21_098, -25_447, 44),
    (2023, 1): (442_766, 93_843, 7_850, 11_515, 9_169),
    (2023, 2): (658_175, 192_670, 89_236, 158_736, 126_949),
    (2023, 3): (703_698, 187_134, 76_063, 182_049, 145_814),
    (2023, 4): (693_631, 205_015, 120_927, 41_603, 57_612),
    (2024, 1): (611_238, 171_415, 68_917, 198_463, 158_536),
    (2024, 2): (722_796, 232_212, 136_199, 204_550, 162_776),
    (2024, 3): (732_375, 230_125, 119_118, 108_587, 101_885),
    (2024, 4): (870_368, 265_085, 137_276, 185_204, 152_392),
    (2025, 1): (744_941, 267_794, 147_189, 233_852, 186_856),
    (2025, 2): (780_564, 252_624, 161_400, -86_007, -69_793),
    (2025, 3): (772_214, 235_414, 109_180, 244_533, 194_654),
    (2025, 4): (709_777, 203_748, 88_545, 169_521, 161_115),
    (2026, 1): (735_194, 242_081, 134_950, 157_845, 156_431),
    (2026, 2): (681_181, 212_420, 99_532, 113_183, 83_371),
}

# 公司 2025/2024 個體年報（仟元）——用來核對加總與引用官方年報數字
OFFICIAL_ANNUAL = {
    2024: {"rev": 2_936_777, "gp": 909_280, "oi": 464_214, "ni": 575_589, "ocf": 562_594},
    2025: {"rev": 3_007_496, "gp": 969_659, "oi": 509_224, "ni": 472_832, "ocf": 580_990},
}

ANNUAL_EPS = {2021: 3.66, 2022: 3.59, 2023: 4.22, 2024: 7.07, 2025: 5.77}
QUARTERLY_EPS = {
    (2021, 1): 0.87, (2021, 2): 0.90, (2021, 3): 1.01, (2021, 4): 0.88,
    (2022, 1): 1.10, (2022, 2): 1.49, (2022, 3): 1.00, (2022, 4): 0.00,
    (2023, 1): 0.11, (2023, 2): 1.58, (2023, 3): 1.81, (2023, 4): 0.72,
    (2024, 1): 1.95, (2024, 2): 2.00, (2024, 3): 1.25, (2024, 4): 1.87,
    (2025, 1): 2.29, (2025, 2): -0.85, (2025, 3): 2.37, (2025, 4): 1.96,
    (2026, 1): 1.90, (2026, 2): 1.01,
}

# Yahoo 股市轉載合併資產負債（仟元）年底／季底
YE_BS = {
    # assets, liab, equity, ca, cl, cash, st_inv
    2021: (4_319_342, 1_041_555, 3_277_787, 3_245_156, 676_552, 1_895_730, 407_462),
    2022: (4_176_867, 888_953, 3_287_914, 3_248_578, 550_423, 2_088_382, 393_005),
    2023: (4_348_621, 974_448, 3_374_173, 3_464_612, 673_943, 1_932_446, 659_528),
    2024: (4_821_229, 1_104_881, 3_716_348, 3_920_192, 817_357, None, None),
    2025: (4_798_769, 1_092_214, 3_706_555, 3_705_645, 830_452, 1_503_613, 1_147_207),
}
# 2026Q2 最新
BS_2026Q2 = (5_180_512, 1_312_280, 3_868_232, 3_735_925, 1_072_997)
NAV = {2021: 41.00, 2022: 41.01, 2023: 41.66, 2024: 45.40, 2025: 45.03, "2026Q1": 44.00}

# Yahoo 單季營業現金流（仟元）
Q_OCF = {
    (2022, 1): 147_162, (2022, 2): 8_643, (2022, 3): 28_265, (2022, 4): 233_294,
    (2023, 1): 170_391, (2023, 2): 26_805, (2023, 3): 87_466, (2023, 4): 191_001,
    (2024, 1): 60_001, (2024, 2): 191_943, (2024, 3): 70_953, (2024, 4): 240_818,
    (2025, 1): 143_660, (2025, 2): 78_648, (2025, 3): 165_284, (2025, 4): 185_307,
    (2026, 1): 171_800, (2026, 2): 115_052,
}

# 現金股利（所屬盈餘年度）
DPS = {2021: 3.3174, 2022: 2.9112, 2023: 2.977, 2024: 5.9899, 2025: 2.8874}

# 月營收（仟元）——HiStock 轉載公開資訊觀測站
MONTHLY_2025_FY = 3_019_468  # 2025/12 累計
MONTHLY_2024_FY = 2_949_524
H1_2026_REV = 1_416_374
H1_2025_REV = 1_525_504

PRICE_ASOF = 55.10  # 2026-08-27 櫃買收盤
SHARES_2026_M = 82.6  # 股本約 826 百萬 → 82.6 百萬股
PEERS_GM_NOTE = "同業光耀 2025 營收 4.75 億、稅後虧損 2.50 億、EPS -3.45"

FONT_TTF = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
CHART_FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
NAVY = colors.HexColor("#0B2545")
TEAL = colors.HexColor("#0D7377")
GOLD = colors.HexColor("#C9A227")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#F4F7FB")
ROW_ALT = colors.HexColor("#E8EEF5")
RED = colors.HexColor("#B91C1C")
WHITE = colors.white

ASOF = "2026-08-27"
OUT_DEFAULT = Path("reports/ubright_4933_financial_outlook_20260827.pdf")


def quarterly_year_sum(year: int) -> dict[str, float]:
    rows = [QUARTERLY_PL[(year, q)] for q in (1, 2, 3, 4)]
    rev = sum(r[0] for r in rows)
    gp = sum(r[1] for r in rows)
    oi = sum(r[2] for r in rows)
    pretax = sum(r[3] for r in rows)
    ni = sum(r[4] for r in rows)
    return {"rev": rev, "gp": gp, "oi": oi, "pretax": pretax, "ni": ni}


def annual_pl(year: int) -> dict[str, float]:
    """年度損益：2024／2025 優先用個體年報，其餘用四季加總。"""
    if year in OFFICIAL_ANNUAL:
        o = OFFICIAL_ANNUAL[year]
        qsum = quarterly_year_sum(year)
        rev, gp, oi, ni = o["rev"], o["gp"], o["oi"], o["ni"]
        pretax = qsum["pretax"]
    else:
        qsum = quarterly_year_sum(year)
        rev, gp, oi, pretax, ni = qsum["rev"], qsum["gp"], qsum["oi"], qsum["pretax"], qsum["ni"]
    return {
        "rev": rev,
        "gp": gp,
        "oi": oi,
        "pretax": pretax,
        "ni": ni,
        "gm": gp / rev,
        "om": oi / rev,
        "nm": ni / rev,
        "eps": ANNUAL_EPS[year],
    }


def annual_ocf(year: int) -> int:
    return sum(Q_OCF[(year, q)] for q in (1, 2, 3, 4))


def cagr(start: float, end: float, years: int) -> float:
    if start <= 0 or end <= 0 or years <= 0:
        return float("nan")
    return (end / start) ** (1 / years) - 1


def avg_equity_roe(year: int) -> float:
    eq_end = YE_BS[year][2]
    eq_beg = YE_BS[year - 1][2] if (year - 1) in YE_BS else eq_end
    return annual_pl(year)["ni"] / ((eq_beg + eq_end) / 2)


def avg_assets_roa(year: int) -> float:
    a_end = YE_BS[year][0]
    a_beg = YE_BS[year - 1][0] if (year - 1) in YE_BS else a_end
    return annual_pl(year)["ni"] / ((a_beg + a_end) / 2)


def ttm_eps() -> float:
    keys = [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]
    return sum(QUARTERLY_EPS[k] for k in keys)


def ttm_ni() -> int:
    keys = [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]
    return sum(QUARTERLY_PL[k][4] for k in keys)


def fmt_yi(n: float) -> str:
    """仟元 → 億（一位小數）。"""
    return f"{n / 100_000:.2f}"


def fmt_pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"


def fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"


# ---------------------------------------------------------------------------
# --selftest：純函式餵真季報，核對官方年報（#35 禁字面斷言）
# ---------------------------------------------------------------------------
def selftest() -> int:
    failures: list[str] = []
    for year, official in OFFICIAL_ANNUAL.items():
        got = quarterly_year_sum(year)
        # 營收／淨利與個體年報必須咬死；毛利／營業利益 HiStock 季報與年報分類有約 1% 差額，不強行相等。
        for key in ("rev", "ni"):
            if got[key] != official[key]:
                failures.append(
                    f"{year} {key}: quarterly_sum={got[key]} official={official[key]}"
                )
        if abs(got["gp"] - official["gp"]) / official["gp"] > 0.02:
            failures.append(
                f"{year} gp drift >2%: quarterly_sum={got['gp']} official={official['gp']}"
            )
    # 毛利率區間：2025 年報 32%
    pl25 = annual_pl(2025)
    if not (0.31 <= pl25["gm"] <= 0.33):
        failures.append(f"2025 GM out of expected band: {pl25['gm']}")
    # TTM EPS 應與 Yahoo 本益比回推接近（55.1 / 7.64 ≈ 7.21）
    te = ttm_eps()
    if not (7.0 <= te <= 7.5):
        failures.append(f"TTM EPS unexpected: {te}")
    # 2025 股利發放率約 50%
    payout = DPS[2025] / ANNUAL_EPS[2025]
    if not (0.48 <= payout <= 0.52):
        failures.append(f"2025 payout {payout}")
    # 2026H1 月營收應等於 Q1+Q2 季報營收（允許月報／季報 1 仟元誤差）
    h1 = QUARTERLY_PL[(2026, 1)][0] + QUARTERLY_PL[(2026, 2)][0]
    if abs(h1 - H1_2026_REV) > 2:
        failures.append(f"H1 2026 rev mismatch {h1} vs {H1_2026_REV}")
    if failures:
        print("SELFTEST FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print("SELFTEST PASS")
    print(f"  2024 rev={annual_pl(2024)['rev']:,} ni={annual_pl(2024)['ni']:,}")
    print(f"  2025 rev={annual_pl(2025)['rev']:,} ni={annual_pl(2025)['ni']:,}")
    print(f"  TTM EPS={ttm_eps():.2f}  PE={PRICE_ASOF / ttm_eps():.2f}")
    return 0


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def _setup_mpl() -> None:
    # 文泉驛同時含中文與 ASCII 數字；Droid Sans Fallback 缺 0-9 會讓圖軸變空白。
    fm.fontManager.addfont(CHART_FONT)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Noto Sans", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def _fig_to_image(fig, width=170 * mm, height=78 * mm) -> Image:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)


def chart_revenue_profit() -> Image:
    years = [2021, 2022, 2023, 2024, 2025]
    revs = [annual_pl(y)["rev"] / 100_000 for y in years]
    nis = [annual_pl(y)["ni"] / 100_000 for y in years]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = np.arange(len(years))
    bars = ax.bar(x, revs, width=0.55, color="#0D7377", label="營收（億元）")
    ax2 = ax.twinx()
    ax2.plot(x, nis, color="#C9A227", marker="o", linewidth=2.4, label="稅後淨利（億元）")
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylabel("營收（億元）")
    ax2.set_ylabel("稅後淨利（億元）")
    ax.set_title("友輝 2021–2025 營收與稅後淨利", loc="left", fontsize=12, color="#0B2545")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    for b, v in zip(bars, revs):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}", ha="center", fontsize=8)
    fig.tight_layout()
    return _fig_to_image(fig)


def chart_margins() -> Image:
    years = [2021, 2022, 2023, 2024, 2025]
    gm = [annual_pl(y)["gm"] * 100 for y in years]
    om = [annual_pl(y)["om"] * 100 for y in years]
    nm = [annual_pl(y)["nm"] * 100 for y in years]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(years, gm, marker="o", color="#0D7377", linewidth=2.2, label="毛利率")
    ax.plot(years, om, marker="s", color="#0B2545", linewidth=2.2, label="營業利益率")
    ax.plot(years, nm, marker="^", color="#C9A227", linewidth=2.2, label="稅後淨利率")
    ax.set_title("獲利率走勢：產品組合優化帶動本業走升", loc="left", fontsize=12, color="#0B2545")
    ax.set_ylabel("%")
    ax.set_xticks(years)
    ax.grid(linestyle=":", alpha=0.5)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    return _fig_to_image(fig)


def chart_quarterly_rev() -> Image:
    keys = sorted(k for k in QUARTERLY_PL if k[0] >= 2021)
    labels = [f"{y}Q{q}" for y, q in keys]
    revs = [QUARTERLY_PL[k][0] / 1000 for k in keys]  # 百萬
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    colors_bar = ["#94a3b8" if y < 2026 else "#0D7377" for y, q in keys]
    ax.bar(range(len(keys)), revs, color=colors_bar, width=0.85)
    ax.set_xticks(range(0, len(keys), 2))
    ax.set_xticklabels([labels[i] for i in range(0, len(keys), 2)], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("營收（百萬元）")
    ax.set_title("單季營收：2022 下半年谷底後回升，2026 上半年年減", loc="left", fontsize=11, color="#0B2545")
    ax.axhline(np.mean(revs), color="#C9A227", linestyle="--", linewidth=1, label="期間平均")
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle=":", alpha=0.45)
    fig.tight_layout()
    return _fig_to_image(fig)


def chart_bs() -> Image:
    years = [2021, 2022, 2023, 2024, 2025]
    cashish = []
    for y in years:
        cash, st = YE_BS[y][5], YE_BS[y][6]
        if cash is None:
            # 2024 現金未完整抓到，用流動資產−粗估營運資金；改用 2024Q4 官方個體現金+FVTPL
            cashish.append((1_769_234 + 969_217) / 100_000)
        else:
            cashish.append((cash + (st or 0)) / 100_000)
    equity = [YE_BS[y][2] / 100_000 for y in years]
    liab = [YE_BS[y][1] / 100_000 for y in years]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = np.arange(len(years))
    ax.bar(x - 0.22, equity, 0.28, label="股東權益", color="#0B2545")
    ax.bar(x, liab, 0.28, label="總負債", color="#94a3b8")
    ax.bar(x + 0.22, cashish, 0.28, label="現金＋短期投資", color="#0D7377")
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylabel("億元")
    ax.set_title("資產負債：低槓桿、現金部位接近總負債的兩倍以上", loc="left", fontsize=11, color="#0B2545")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", linestyle=":", alpha=0.45)
    fig.tight_layout()
    return _fig_to_image(fig)


def chart_returns() -> Image:
    years = [2022, 2023, 2024, 2025]  # 需前年權益
    roe = [avg_equity_roe(y) * 100 for y in years]
    roa = [avg_assets_roa(y) * 100 for y in years]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(years, roe, marker="o", color="#0D7377", linewidth=2.3, label="ROE（平均權益）")
    ax.plot(years, roa, marker="s", color="#0B2545", linewidth=2.3, label="ROA（平均資產）")
    ax.set_title("股東／資產報酬：2024 高峰、2025 回落但仍優於 2022–23", loc="left", fontsize=11, color="#0B2545")
    ax.set_ylabel("%")
    ax.set_xticks(years)
    ax.grid(linestyle=":", alpha=0.5)
    ax.legend(frameon=False)
    fig.tight_layout()
    return _fig_to_image(fig)


def chart_radar() -> Image:
    """競爭力雷達＝本報告自我評分（self-reported），不是第三方評等。"""
    labels = ["技術深度", "財務彈性", "客戶黏性", "規模／市佔", "產品多元", "成長可證偽"]
    ubright = [7.5, 9.0, 7.0, 3.5, 6.5, 5.0]
    global_majors = [9.0, 8.0, 8.5, 9.0, 8.0, 5.5]  # 3M / LG / DNP 類型
    tw_peers = [6.0, 4.5, 6.0, 3.0, 5.0, 4.0]  # 光耀／迎輝類型
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    def close(v):
        return v + v[:1]

    fig, ax = plt.subplots(figsize=(6.2, 5.2), subplot_kw={"polar": True})
    ax.plot(angles, close(ubright), color="#0D7377", linewidth=2, label="友輝（本報告評分）")
    ax.fill(angles, close(ubright), color="#0D7377", alpha=0.18)
    ax.plot(angles, close(global_majors), color="#64748b", linewidth=1.5, linestyle="--", label="國際大廠（3M／LG／DNP 類型）")
    ax.plot(angles, close(tw_peers), color="#C9A227", linewidth=1.5, label="台灣同業中位")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_title("全球競爭力雷達（self-reported 分析評分，非機構評等）", fontsize=11, color="#0B2545", pad=16)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), frameon=False, fontsize=8)
    fig.tight_layout()
    return _fig_to_image(fig, width=155 * mm, height=105 * mm)


def chart_scenarios() -> Image:
    years = [2025, 2026, 2027, 2028, 2029, 2030]
    base = [30.1, 29.5, 30.5, 31.5, 32.5, 33.5]
    bull = [30.1, 32.0, 35.0, 38.0, 41.0, 45.0]
    bear = [30.1, 27.5, 26.0, 25.0, 24.0, 23.0]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.fill_between(years, bear, bull, color="#0D7377", alpha=0.12, label="情境區間")
    ax.plot(years, base, color="#0B2545", linewidth=2.4, marker="o", label="基準：營收緩步、組合優化")
    ax.plot(years, bull, color="#0D7377", linewidth=1.6, linestyle="--", label="樂觀：車載 QD＋電子紙＋被動放量")
    ax.plot(years, bear, color="#B91C1C", linewidth=1.6, linestyle="--", label="保守：LCD／NB 下滑＋殺價")
    ax.set_ylabel("營收（億元，情境）")
    ax.set_title("未來五年營收情境（非預測；2025 為已實現）", loc="left", fontsize=11, color="#0B2545")
    ax.set_xticks(years)
    ax.legend(frameon=False, fontsize=8)
    ax.grid(linestyle=":", alpha=0.45)
    fig.tight_layout()
    return _fig_to_image(fig)


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def register_font() -> str:
    pdfmetrics.registerFont(TTFont("CN", FONT_TTF))
    return "CN"


def make_styles(font: str) -> dict:
    ss = getSampleStyleSheet()
    styles = {
        "cover_kicker": ParagraphStyle("kicker", fontName=font, fontSize=10, textColor=GOLD, tracking=1.2, alignment=TA_CENTER, spaceAfter=6),
        "cover_title": ParagraphStyle("ct", fontName=font, fontSize=22, leading=30, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "cover_sub": ParagraphStyle("cs", fontName=font, fontSize=12, leading=18, textColor=SLATE, alignment=TA_CENTER, spaceAfter=4),
        "h1": ParagraphStyle("h1", fontName=font, fontSize=14, leading=20, textColor=NAVY, spaceBefore=12, spaceAfter=8, borderPadding=3),
        "h2": ParagraphStyle("h2", fontName=font, fontSize=12, leading=17, textColor=TEAL, spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("body", fontName=font, fontSize=9.5, leading=15, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=6),
        "body_left": ParagraphStyle("bl", fontName=font, fontSize=9.5, leading=15, textColor=SLATE, alignment=TA_LEFT, spaceAfter=6),
        "caption": ParagraphStyle("cap", fontName=font, fontSize=8, leading=11, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER, spaceAfter=10, spaceBefore=2),
        "bullet": ParagraphStyle("bu", fontName=font, fontSize=9.5, leading=14.5, textColor=SLATE, leftIndent=8, spaceAfter=3),
        "th": ParagraphStyle("th", fontName=font, fontSize=8, leading=11, textColor=WHITE, alignment=TA_CENTER),
        "td": ParagraphStyle("td", fontName=font, fontSize=8, leading=11, textColor=SLATE, alignment=TA_CENTER),
        "td_l": ParagraphStyle("tdl", fontName=font, fontSize=8, leading=11, textColor=SLATE, alignment=TA_LEFT),
        "footer": ParagraphStyle("ft", fontName=font, fontSize=7.5, textColor=colors.HexColor("#94a3b8")),
        "callout": ParagraphStyle("co", fontName=font, fontSize=9.5, leading=14.5, textColor=NAVY, alignment=TA_LEFT),
        "small": ParagraphStyle("sm", fontName=font, fontSize=8, leading=12, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=4),
        "toc": ParagraphStyle("toc", fontName=font, fontSize=10.5, leading=18, textColor=SLATE),
    }
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("CN", 8)
    canvas.drawString(16 * mm, A4[1] - 8 * mm, "友輝光電（4933）財務與產業前景報告")
    canvas.drawRightString(A4[0] - 16 * mm, A4[1] - 8 * mm, f"資料截至 {ASOF}")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("CN", 7.5)
    canvas.drawString(16 * mm, 4 * mm, "非投資建議｜數字出自公開財報與交易所｜前瞻＝情境分析")
    canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def p(styles, key, text) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), styles[key])


def simple_table(styles, headers, rows, col_widths):
    head = [Paragraph(h, styles["th"]) for h in headers]
    data = [head]
    for row in rows:
        data.append([Paragraph(str(c), styles["td"] if i else styles["td_l"]) for i, c in enumerate(row)])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "CN"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        else:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style_cmds))
    return t


def callout_box(styles, text: str):
    inner = Paragraph(text, styles["callout"])
    t = Table([[inner]], colWidths=[178 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E6F4F4")),
                ("BOX", (0, 0), (-1, -1), 1.2, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def bullets(styles, items: list[str]):
    return [Paragraph(f"• {it}", styles["bullet"]) for it in items]


def build_story(styles) -> list:
    s = styles
    years = [2021, 2022, 2023, 2024, 2025]
    pls = {y: annual_pl(y) for y in years}
    rev_cagr = cagr(pls[2021]["rev"], pls[2025]["rev"], 4)
    ni_cagr = cagr(pls[2021]["ni"], pls[2025]["ni"], 4)
    ttm_e = ttm_eps()
    pe = PRICE_ASOF / ttm_e
    mktcap = PRICE_ASOF * SHARES_2026_M / 10  # 億：55.1 * 82.6e6 / 1e8
    pb_q1 = PRICE_ASOF / NAV["2026Q1"]
    dy = DPS[2025] / PRICE_ASOF
    story: list = []

    # Cover
    story.append(Spacer(1, 28 * mm))
    story.append(p(s, "cover_kicker", "UBright Optronics　上櫃光電　新纖集團"))
    story.append(p(s, "cover_title", "友輝光電股份有限公司（4933）<br/>近五年財務分析<br/>與未來五年前景、全球競爭力報告"))
    story.append(Spacer(1, 6 * mm))
    story.append(p(s, "cover_sub", f"資料截止：{ASOF}（櫃買收盤 {PRICE_ASOF:.2f} 元）"))
    story.append(p(s, "cover_sub", "最新財報：2026 年第 2 季　｜　年報核對：2024、2025 個體財報（勤業眾信）"))
    story.append(Spacer(1, 10 * mm))
    cover_kpi = simple_table(
        s,
        ["指標", "數值", "口徑"],
        [
            ["近四季 EPS（TTM）", f"{ttm_e:.2f} 元", "2025Q3–2026Q2 季 EPS 加總"],
            ["本益比", f"{pe:.1f} 倍", f"收盤 {PRICE_ASOF:.2f} ÷ TTM EPS"],
            ["股價淨值比", f"{pb_q1:.2f} 倍", f"以 2026Q1 每股淨值 {NAV['2026Q1']:.2f} 元"],
            ["現金殖利率", f"{dy*100:.1f}%", "2025 盈餘配息 2.8874 元／收盤價"],
            ["2025 營收／淨利", f"{fmt_yi(pls[2025]['rev'])} 億／{fmt_yi(pls[2025]['ni'])} 億", "季報加總＝個體年報"],
            ["2025 毛利率／營益率", f"{fmt_pct(pls[2025]['gm'])}／{fmt_pct(pls[2025]['om'])}", "本業獲利創近五年高"],
            ["負債比（2025 年底）", "22.8%", "無銀行長短期借款"],
            ["2026 上半年營收年增", "-7.2%", "月營收累計 14.16 億 vs 去年 15.26 億"],
        ],
        [48 * mm, 52 * mm, 78 * mm],
    )
    story.append(cover_kpi)
    story.append(Spacer(1, 8 * mm))
    story.append(
        callout_box(
            s,
            "本報告不是買賣建議，也不是目標價。歷史數字皆可回溯至公開財報或交易所揭露；"
            "未來五年為情境分析（self-reported），前提改變則結論改變。友輝為利基光學膜廠，"
            "不是面板龍頭，解讀時勿把產業成長直接當成公司成長。",
        )
    )
    story.append(PageBreak())

    # TOC
    story.append(p(s, "h1", "目錄"))
    toc = [
        "一、執行摘要",
        "二、公司與產品定位",
        "三、近五年財務分析（2021–2025，並含 2026 上半年）",
        "　　3.1 損益與成長　3.2 獲利率　3.3 資產負債與現金　3.4 現金流與股利　3.5 報酬率",
        "四、產業結構與未來五年前景",
        "五、全球競爭力評估",
        "六、未來五年三情境（基準／樂觀／保守）",
        "七、主要風險與觀察清單",
        "附錄：資料表、方法與來源",
    ]
    for line in toc:
        story.append(p(s, "toc", line))
    story.append(Spacer(1, 6 * mm))
    story.append(p(s, "h2", "讀本報告前先記住的三件事"))
    story.extend(
        bullets(
            s,
            [
                "營收五年幾乎持平（CAGR 約 {:.1f}%），但稅後淨利 CAGR 約 {:.1f}%——故事在「組合與毛利」，不在「衝量」。".format(
                    rev_cagr * 100, ni_cagr * 100
                ),
                "財務結構極穩：現金與約當＋金融資產遠高於有息負債（實際銀行借款為 0），股利政策長期偏高，但 2025 配息率降至約 50%，與擴產／新事業留存一致。",
                "本業（LCD 增亮膜）所在的純 BEF 市場全球僅數億美元量級、成長個位數；真正的變量是車載顯示、量子點膜、電子紙、被動元件與半導體塗布——後者多數仍在驗證或放量初期。",
            ],
        )
    )
    story.append(PageBreak())

    # Ch1
    story.append(p(s, "h1", "一、執行摘要"))
    story.append(
        p(
            s,
            "body",
            "友輝光電（上櫃 4933，英文 UBright Optronics）成立於 2003 年，總部桃園大溪，"
            "為新光合成纖維（1409）轉投資、持股約 49% 的子公司。核心能力是精密微結構複製、"
            "UV 膠配方與光學設計，傳統產品是 TFT-LCD 背光模組用聚光片／增亮膜（BEF）。"
            "近年官網與法說已把產品面擴到複合膜、量子點膜、偏光片保護膜、電子紙塗布、"
            "車載高輝度膜，以及精密陶瓷被動元件。2025 年前三季產品組合（公司於法說揭露）："
            "筆電約 52%、車載約 15%、電子紙約 12%、保護膜約 11%，其餘為平板／電視等。",
        )
    )
    story.append(
        p(
            s,
            "body",
            f"以 {ASOF} 收盤 {PRICE_ASOF:.2f} 元、流通約 {SHARES_2026_M:.1f} 百萬股估算，"
            f"市值約 {mktcap:.0f} 億元。近四季 EPS {ttm_e:.2f} 元，本益比約 {pe:.1f} 倍"
            f"（Yahoo 同日揭示 7.64 倍、同業平均約 40 倍，同業平均被虧損股拉高，不宜直接當估值錨）。"
            f"2026Q1 每股淨值 44.00 元，P/B 約 {pb_q1:.2f} 倍。2025 盈餘配息 2.8874 元，"
            f"現金殖利率約 {dy*100:.1f}%。成交量長期偏薄（當日約百張等級），流動性折價存在。",
        )
    )
    story.append(p(s, "h2", "財務結論（已實現，可核對）"))
    story.extend(
        bullets(
            s,
            [
                f"2021→2025 營收 {fmt_yi(pls[2021]['rev'])} 億 → {fmt_yi(pls[2025]['rev'])} 億（四年 CAGR {fmt_pct(rev_cagr)}）；2022 為循環谷底 {fmt_yi(pls[2022]['rev'])} 億。",
                f"同期稅後淨利 {fmt_yi(pls[2021]['ni'])} 億 → {fmt_yi(pls[2025]['ni'])} 億（CAGR {fmt_pct(ni_cagr)}）；2024 為高峰 {fmt_yi(pls[2024]['ni'])} 億、EPS 7.07 元。",
                f"毛利率 2021 年 {fmt_pct(pls[2021]['gm'])} → 2025 年 {fmt_pct(pls[2025]['gm'])}；營業利益率 {fmt_pct(pls[2021]['om'])} → {fmt_pct(pls[2025]['om'])}。本業品質明顯改善。",
                "2025 年第 2 季本業仍賺（營業利益 1.61 億），但業外大虧使單季稅後 -0.70 億、EPS -0.85 元；隨後三季業外回正。品質分析必須把「本業」與「匯兌／金融資產評價」切開。",
                f"2026 上半年合併營收 14.16 億、年減 7.2%；毛利率仍有 32.1%，本業沒有崩。獲利 2.40 億、EPS 2.91 元，低於 2025 上半年（2025H1 含 Q2 業外大虧，基期扭曲）。",
            ],
        )
    )
    story.append(p(s, "h2", "前景與競爭力結論（情境，非點預測）"))
    story.extend(
        bullets(
            s,
            [
                "產業：全球顯示器光學膜（含偏光片等大宗）機構預估 2024–2030 CAGR 約 6.8%；但友輝真正所在的純增亮膜（BEF）市場規模遠小、CAGR 約 1–3%。成長不在「LCD 面積」，而在車載高亮度、Mini-LED 均光、少層高規膜、以及非 LCD。",
                "公司：管理層 2025–2026 法說主軸是「產品組合優化＋非 LCD」。無鎘車載量子點膜（公司自稱全球首家量產）、電子紙、被動元件、與美系材料商合作的半導體精密塗布，是未來五年的選擇權；後兩項尚未形成可驗證的年度營收支柱。",
                "全球位置：在台灣光學膜同業中，友輝近五年獲利與資產負債明顯優於光耀（3666，2025 虧損）與迎輝（規模更小）。對上 3M、LG、DNP、三星 Cheil，友輝是利基追隨者而非規則制定者。全球競爭力＝「利基高毛利供應商」，不是「全球龍頭」。",
            ],
        )
    )
    story.append(PageBreak())

    # Ch2
    story.append(p(s, "h1", "二、公司與產品定位"))
    story.append(p(s, "h2", "2.1 沿革與據點"))
    story.append(
        p(
            s,
            "body",
            "大溪廠為傳統光學膜／Lens 膜片主力（公司稱約佔營收七成，稼動約七至八成），"
            "產品偏筆電與車載客製；竹南廠（2020 年設立）做精密塗布與奈米級光學膜"
            "（約三成營收，稼動八至九成）。2026 年資本支出公司估約 2 億餘元，用於新事業擴線，"
            "暫無大規模擴廠。董事長吳昕杰、總經理辛隆賓。會計師：勤業眾信。",
        )
    )
    story.append(p(s, "h2", "2.2 產品與技術"))
    story.append(
        p(
            s,
            "body",
            "增亮膜把背光散射光集中到正面，一片 LCD 通常要 1–2 張稜鏡片，佔背光材料成本不低。"
            "複合膜把擴散功能做進增亮膜，減少膜層。量子點膜提升色域，車載中控要高亮度與高飽和。"
            "公司另做保護膜、抗眩、電子紙手感塗布、OCA，以及壓敏／熱敏電阻、安規電容等精密陶瓷。"
            "上游 PET 膜與新纖集團有垂直關係（MoneyDJ 記載 PET 供應商含新科）。"
            "終端／間接客戶歷年揭露含友達、群創、彩晶、三星、LGD、京東方、海信、TCL、Sony 等；"
            "銷售早期有相當比例經裁切運籌（華宏）。",
        )
    )
    mix = simple_table(
        s,
        ["應用（2025 前三季，法說）", "營收比重", "意涵"],
        [
            ["筆記型電腦光學膜", "約 52%", "仍是基本盤；2026 管理層因記憶體缺料轉保守"],
            ["車載顯示光學膜／QD", "約 15%", "單車螢幕變大、要抗陽光高亮度；毛利較佳"],
            ["電子紙相關", "約 12%", "高毛利客戶；公司預期 2026 仍可雙位數成長"],
            ["保護膜", "約 11%", "偏光片製程／出貨用高潔淨 PET"],
            ["平板、電視、其他", "約 10%", "消費性 LCD，價格壓力大"],
            ["非 LCD 合計（電子紙＋被動等）", "約 30%", "2026 規劃再小幅提升"],
        ],
        [52 * mm, 38 * mm, 88 * mm],
    )
    story.append(mix)
    story.append(p(s, "caption", "資料：2025 年 11 月／2026 年法說相關報導轉述公司揭露。比重為約數，加總可能因四捨五入不為 100%。"))
    story.append(p(s, "h2", "2.3 商業模式一句話"))
    story.append(
        p(
            s,
            "body",
            "友輝不是「面板景氣的槓桿股」。它是把光學微結構與塗布 know-how 賣給顯示器供應鏈的材料廠。"
            "量的上限被 LCD 出貨與均單價綁住；質的上限取決於能否把車載、電子紙、被動元件、半導體塗布"
            "做成第二條獲利曲線。過去四年已經證明「減量也能加利」；未來五年要證明「新曲線能補 LCD 的洞」。",
        )
    )
    story.append(PageBreak())

    # Ch3
    story.append(p(s, "h1", "三、近五年財務分析"))
    story.append(p(s, "h2", "3.1 損益與成長"))
    story.append(chart_revenue_profit())
    story.append(p(s, "caption", "圖 1　營收與稅後淨利。營收單位與淨利皆為億元。數字＝四季公開財報加總。"))

    pl_rows = []
    for y in years:
        d = pls[y]
        yoy_r = "" if y == 2021 else f"{(d['rev']/pls[y-1]['rev']-1)*100:+.1f}%"
        yoy_n = "" if y == 2021 else f"{(d['ni']/pls[y-1]['ni']-1)*100:+.1f}%"
        pl_rows.append(
            [
                str(y),
                fmt_yi(d["rev"]),
                yoy_r or "—",
                fmt_yi(d["gp"]),
                fmt_yi(d["oi"]),
                fmt_yi(d["ni"]),
                yoy_n or "—",
                f"{d['eps']:.2f}",
            ]
        )
    story.append(
        simple_table(
            s,
            ["年度", "營收(億)", "營收YoY", "毛利(億)", "營業利益(億)", "稅後淨利(億)", "淨利YoY", "EPS(元)"],
            pl_rows,
            [18 * mm, 22 * mm, 22 * mm, 22 * mm, 26 * mm, 26 * mm, 22 * mm, 20 * mm],
        )
    )
    story.append(p(s, "caption", "表 1　年度損益。2024／2025 採個體年報（營收、淨利與四季加總一致）；2021–2023 為四季公開財報加總。"))
    story.append(
        p(
            s,
            "body",
            "五年走勢可分成三段。"
            "（1）2021：面板循環高檔，營收近 30 億，但毛利率只有約 25%，是「有量、利不頂尖」。"
            "（2）2022–2023Q1：全球 IT 與電視去庫存，2022Q3 營收掉到 4.10 億、當季營業利益轉負；"
            "2022Q4 稅後幾乎打平。這是壓力測試——公司沒有靠槓桿硬撐，負債比反而降到約 21%。"
            "（3）2023Q2 起復甦，2024 營收回到 29.4 億且 EPS 創 7.07 元新高；2025 營收再微增至 30.1 億，"
            "但淨利回落，主因 Q2 業外而非本業失速。",
        )
    )
    story.append(chart_quarterly_rev())
    story.append(p(s, "caption", "圖 2　單季營收（百萬元）。青色為 2026 年。"))
    story.append(
        p(
            s,
            "body",
            f"2026 年上半年月營收累計 {H1_2026_REV/1000:,.1f} 百萬、年減 7.2%。"
            "Q1 營收 7.35 億、Q2 6.81 億。管理層對筆電因 DRAM 缺料轉保守，車載則「全球車市量不增、"
            "單車顯示面積增」。本業營益率 Q1 18.4%、Q2 14.6%，仍明顯高於 2021–22 年中樞。"
            "重點：2026 目前是「溫和降量、毛利仍守住」，不是 2022 那種循環崩潰。",
        )
    )

    story.append(p(s, "h2", "3.2 獲利率：真正的五年主線"))
    story.append(chart_margins())
    story.append(p(s, "caption", "圖 3　年度毛利率、營業利益率、稅後淨利率。"))
    m_rows = []
    for y in years:
        d = pls[y]
        m_rows.append([str(y), fmt_pct(d["gm"]), fmt_pct(d["om"]), fmt_pct(d["nm"])])
    story.append(simple_table(s, ["年度", "毛利率", "營業利益率", "稅後淨利率"], m_rows, [30 * mm, 48 * mm, 50 * mm, 50 * mm]))
    story.append(
        p(
            s,
            "body",
            "毛利率從 2021 年 24.7%、2022 年 22.6%（谷底），拉到 2024 年 30.6%、2025 年 32.2%。"
            "這不是景氣送分：2022 量縮時毛利更差，之後量回來且產品組合往車載、高輝度、電子紙移動，"
            "才出現「量未必更大、每單位更賺錢」。營業利益率同步從 12.3% 升到 16.9%。"
            "研發費用 2025 年 2.71 億、佔營收 9%，對製造公司偏高，這是毛利能守住的成本。"
            "稅後淨利率波動大於本業，因為利息收入（帳上大量現金與金融資產）與兌換／FVTPL 評價很大："
            "2024 業外淨額 +2.33 億，2025 僅 +0.53 億；2025Q2 單季業外約 -2.47 億，直接把全年淨利率從本業軌道拉歪。",
        )
    )
    story.append(
        callout_box(
            s,
            "品質判讀：看友輝，優先看毛利率與營業利益，其次才看 EPS。"
            "2024 EPS 7.07 含豐厚業外；2025 EPS 5.77 被 Q2 業外懲罰；2026H1 EPS 2.91 的本業含金量，"
            "要對照營益率 16.6%（累計）而不是對照淨利率。",
        )
    )

    story.append(p(s, "h2", "3.3 資產負債：防禦性極強"))
    story.append(chart_bs())
    story.append(p(s, "caption", "圖 4　權益、負債、現金＋短期投資（2024 現金採個體年報現金 17.69 億＋FVTPL 9.69 億）。"))
    bs_rows = []
    for y in years:
        a, l, e, ca, cl, cash, st = YE_BS[y]
        cr = ca / cl
        dr = l / a
        bs_rows.append(
            [
                str(y),
                fmt_yi(a),
                fmt_yi(l),
                fmt_yi(e),
                f"{dr*100:.1f}%",
                f"{cr*100:.0f}%",
                f"{NAV[y]:.2f}",
            ]
        )
    story.append(
        simple_table(
            s,
            ["年底", "總資產(億)", "總負債(億)", "權益(億)", "負債比", "流動比", "每股淨值"],
            bs_rows,
            [20 * mm, 26 * mm, 26 * mm, 26 * mm, 24 * mm, 24 * mm, 32 * mm],
        )
    )
    story.append(
        p(
            s,
            "body",
            "2025 年底合併總資產 48.0 億、權益 37.1 億、負債 10.9 億、負債比 22.8%。"
            "財報狗揭露短期借款與長期借款皆為 0；負債主要是應付帳款、租賃負債、退款負債與稅負。"
            "2025 年底現金 15.0 億＋短期投資 11.5 億＝26.5 億，約當每股 32 元現金及金融資產，"
            "相對收盤 55 元，資產很「重現金」。2026Q2 總資產 51.8 億、權益 38.7 億、流動比 348%。"
            "固定資產僅約 4.3 億（2025 年底），這是輕資產塗布廠，不是資本密集面板廠。"
            "退款負債（個體 2025 年底 2.66 億）反映光學膜常見的售後折讓／品質準備，分析時不要把流動負債全當成即將抽銀根的銀行債。",
        )
    )

    story.append(PageBreak())
    story.append(p(s, "h2", "3.4 現金流與股利"))
    ocf_rows = []
    for y in (2022, 2023, 2024, 2025):
        ocf = annual_ocf(y)
        ni = pls[y]["ni"]
        dps = DPS[y]
        payout = dps / ANNUAL_EPS[y]
        ocf_rows.append(
            [
                str(y),
                fmt_yi(ocf),
                fmt_yi(ni),
                f"{ocf/ni:.2f}",
                f"{dps:.4f}",
                f"{payout*100:.0f}%",
            ]
        )
    story.append(
        simple_table(
            s,
            ["年度", "營業現金流(億)", "稅後淨利(億)", "OCF／淨利", "現金 DPS(元)", "發放率"],
            ocf_rows,
            [22 * mm, 32 * mm, 32 * mm, 28 * mm, 32 * mm, 32 * mm],
        )
    )
    story.append(p(s, "caption", "表 2　現金流與股利。OCF 為 Yahoo 單季加總；2024／2025 與個體年報 5.63／5.81 億接近（合併與個體差額很小）。"))
    story.append(
        p(
            s,
            "body",
            "營業現金流連續四年覆蓋淨利（比值 0.9–1.4），獲利不是紙上富貴。"
            "2024 配 5.99 元、發放率約 85%，對應該年超額獲利（含業外）一次吐回；"
            "2025 配 2.89 元、發放率約 50%，較前四年 70–90% 下降，時點上對得上公司把 2025–2026 資本支出"
            "從約 1 億級拉到 2–2.5 億、為新產線留存。五年平均現金股利約 3.6 元。"
            "融資現金流每年中段出現約 2.4–5.0 億流出，對應除息，不是償債危機。",
        )
    )

    story.append(p(s, "h2", "3.5 報酬率與杜邦"))
    story.append(chart_returns())
    story.append(p(s, "caption", "圖 5　ROE／ROA 採「稅後淨利 ÷ 當年與前年平均權益（資產）」。2024 ROE 約 16.2% 與公開彙整一致。"))
    dupont_rows = []
    for y in (2022, 2023, 2024, 2025):
        d = pls[y]
        at = d["rev"] / ((YE_BS[y][0] + YE_BS[y - 1][0]) / 2)
        lev = ((YE_BS[y][0] + YE_BS[y - 1][0]) / 2) / ((YE_BS[y][2] + YE_BS[y - 1][2]) / 2)
        roe = d["nm"] * at * lev
        dupont_rows.append(
            [
                str(y),
                fmt_pct(d["nm"]),
                f"{at:.2f}x",
                f"{lev:.2f}x",
                fmt_pct(roe),
                fmt_pct(avg_assets_roa(y)),
            ]
        )
    story.append(
        simple_table(
            s,
            ["年度", "淨利率", "資產週轉", "權益乘數", "ROE（杜邦）", "ROA"],
            dupont_rows,
            [22 * mm, 28 * mm, 28 * mm, 28 * mm, 36 * mm, 36 * mm],
        )
    )
    story.append(
        p(
            s,
            "body",
            "杜邦拆解很清楚：友輝不是靠槓桿堆 ROE（權益乘數僅 1.27–1.32），也不是靠衝週轉"
            "（資產週轉約 0.53–0.64，現金太多會拖週轉）。ROE 升降幾乎全來自淨利率。"
            "這有兩面：正面是財務紀律，不靠借款放大；負面是帳上 20 億級現金與金融資產若只能賺存款／票息，"
            "會壓低 ROE 上限。2024 的 16% ROE 部分來自業外；要複製，必須本業毛利維持或把多餘現金變成高 ROIC 的新事業。"
            "2025 平均權益 ROE 約 12.7%，仍高於 2022–23 的 8–10%。",
        )
    )

    story.append(p(s, "h2", "3.6 同業對照（台灣光學膜）"))
    story.append(
        p(
            s,
            "body",
            "可公開對照的台灣同業：光耀（3666，稜鏡片／增亮膜，年報列友輝為競爭同業）、"
            "迎輝（3523，光學膜＋ITO，規模小）、華宏（8240，光學膜裁切運籌，淨值更大但商業模式偏運籌）。"
            f"{PEERS_GM_NOTE}。"
            "迎輝淨值約 3.7 億（2026Q2 同業排行），不到友輝的十分之一。"
            "結論：在「台灣上市櫃、做增亮膜」這個小圈子，友輝是財務與獲利的第一梯隊；"
            "這不等於全球第一梯隊。",
        )
    )
    story.append(PageBreak())

    # Ch4 industry
    story.append(p(s, "h1", "四、產業結構與未來五年前景"))
    story.append(p(s, "h2", "4.1 產業地圖：別把「光學膜」四個字當成同一個市場"))
    story.append(
        p(
            s,
            "body",
            "顯示器光學膜至少要拆三層。"
            "第一層是偏光片及其 TAC／PET 保護膜，全球百億美元量級，玩家是日東電工、住友化學、LG 化學、杉金、明基材料等——"
            "友輝官網有偏光片保護膜，但這不是它的歷史基本盤。"
            "第二層是背光堆疊：增亮膜、擴散膜、反射膜。Strategic Market Research 將整體 display optical film"
            "估為 2024 年 285 億美元、2030 年 427 億美元、CAGR 6.8%——此口徑含偏光片，會嚴重高估 BEF 的成長。"
            "第三層才是友輝核心的純 BEF：Research and Markets（2026–2031）把核心 BEF 放在 2026 年約 1–3 億美元、"
            "至 2031 CAGR 僅 1.2–2.2%；IndexBox 對 2026–2035 的基準情境約 3.2% CAGR。"
            "換句話說：未來五年這個產業「不會爆發」，會緩慢挪移。",
        )
    )
    story.append(p(s, "h2", "4.2 需求端：誰還需要增亮膜？"))
    story.extend(
        bullets(
            s,
            [
                "筆電／監視器：仍是 LCD 為主，是友輝今日基本盤。2026 變數是 DRAM 缺料壓抑筆電備貨，公司已公開轉保守。中期 Windows 換機與 AI PC 可能帶來週期性補庫，但不是結構性爆發。",
                "電視：大尺寸化對膜面積有利，但中國廠殺價、且高端往 Mini-LED／OLED 走。友輝電視比重已降到「其他」。",
                "車載：最強結構趨勢。電動車與智慧座艙讓單車螢幕從 5–7 吋變成 10–15 吋、多螢幕；白天可讀性要求數千 nits，光學效率直接關係熱與耗電。Mini-LED 車載出貨 2024 約 450 萬片、2025 估 675 萬片（UBI Research）；OLED 車載也在長，2030 年約 1,300 萬片量級。友輝已進高階車系高輝度膜，並推無鎘車載 QD 膜。",
                "電子紙：閱讀器與電子貨架標籤；公司 2025 前三季已佔 12%，並說 2026 看雙位數成長。這是非 LCD 裡目前唯一已放量的獲利來源。",
                "OLED／Micro-LED：自發光，理論上不需要 BEF。這是本業的天花板。車載 OLED 滲透提高，會吃掉一部分「高階車載 LCD＋BEF」的蛋糕，同時也可能打開 OLED 保護膜／光學膠的新需求——友輝官網已列 OLED 曲面保護膜，但貢獻未單獨揭露。",
            ],
        )
    )
    story.append(p(s, "h2", "4.3 供給端：專利過後的紅海與利基"))
    story.append(
        p(
            s,
            "body",
            "3M 曾以 BEF／DBEF 專利定義這個產業。專利到期後，韓系（LG、Shinwha、Cheil）、"
            "日系（DNP、Kuraray）、台系（友輝、光耀、迎輝）與中國大陸（激智、康得新、寧波樂凱、維奇、光志、聚飛）"
            "切入。大宗稜鏡片變成價格戰；活路在微結構客製、多層貼合（雙貼／三貼）、車規認證（IATF 16949）、"
            "高輝度抗熱、無鎘 QD、以及把擴散＋增亮做成一張膜。中國同業擴產使標準品年降價數個百分點，"
            "這是友輝必須持續「減標準品、加利基品」的原因——過去四年毛利率走勢顯示這條路目前走得通。",
        )
    )
    story.append(p(s, "h2", "4.4 未來五年產業前景（2026–2030）"))
    story.append(
        p(
            s,
            "body",
            "基準判斷（self-reported）：純 BEF 全球量緩步、價有壓力；價值成長集中在車載高亮度、Mini-LED 均光、"
            "少層高規與整合膜。LCD 不會突然消失——IT 與車載 LCD 仍會在 2030 年佔大宗——但「每台裝置的膜張數」"
            "可能因整合膜下降，單價則因規格上升。偏光片產業本身也在中國化。對台灣利基廠，未來五年是"
            "「存量市場裡搶高毛利位子」，不是「增量市場躺著長」。"
            "相鄰的被動元件與半導體先進封裝塗布，屬於另一個產業邏輯（驗證長、一旦進去黏性高），"
            "不能用顯示器 CAGR 去外推。",
        )
    )
    story.append(PageBreak())

    # Ch5 competitiveness
    story.append(p(s, "h1", "五、全球競爭力評估"))
    story.append(
        p(
            s,
            "small",
            "以下雷達圖與分數為本報告分析評分（self-reported），用來把「質性判斷」攤開給讀者挑戰，"
            "不是標普、不是市調機構、也不是內部評等。分數 0–10。",
        )
    )
    story.append(chart_radar())
    story.append(p(s, "caption", "圖 6　友輝 vs 國際大廠類型 vs 台灣同業中位。規模／市佔是友輝最大的結構弱項。"))

    story.append(p(s, "h2", "5.1 相對國際大廠"))
    story.append(
        p(
            s,
            "body",
            "3M 的多層反射偏光增亮（DBEF）與品牌規格影響力，友輝做不到同等級的系統定義權。"
            "LG、三星 Cheil 有垂直面板集團當內需；DNP／Kuraray 有材料科學縱深。"
            "友輝的打法是：不在全球標準品上拼產能，而在筆電／車載客製稜鏡、複合膜、無鎘車載 QD 上當「指定第二或利基第一」。"
            "這在全球價值鏈裡是「可被替代的高品質供應商」，黏性來自認證週期與光學設計協同，不是來自標準。"
            "車規認證與高階車系導入是真實護城河，但護城河寬度取決於客戶是否雙源、以及中國車載供應鏈是否用本土膜廠替代。",
        )
    )
    story.append(p(s, "h2", "5.2 相對中國大陸同業"))
    story.append(
        p(
            s,
            "body",
            "大陸廠商在標準稜鏡片的成本與內需面板（京東方、華星、惠科）鏈上更有優勢，價格是他們的武器。"
            "友輝 2022 年銷售區域曾揭內銷 57%、外銷 43%，客戶含陸系品牌，因此不是「只做台灣」。"
            "競爭點在：客製光學、車規、無鎘 QD、電子紙塗布良率。若未來五年只守標準 NB 膜，中國同業會把毛利率打回 20% 出頭；"
            "若利基產品佔比續升，友輝可以繼續用 30% 毛利與大陸標準品錯位。2026 法說提到中國車載「價格競爭激烈、毛利率偏低」，"
            "顯示這條戰線已經發生。",
        )
    )
    story.append(p(s, "h2", "5.3 相對台灣同業"))
    story.append(
        p(
            s,
            "body",
            "光耀同樣做稜鏡片、同樣轉車載／高階筆電，但 2025 營收掉到 4.75 億且虧損，說明「轉利基」不是自動成功。"
            "友輝能把毛利率做到 32%、且帳上淨現金，代表客戶結構、良率或產品世代領先同業一截。"
            "華宏偏裁切運籌，與友輝是上下游合作多於全面重疊。迎輝多元化到 ITO 與儲能，光學膜已非全部。"
            "台灣圈內，友輝目前是「財務最健康、本業毛利最高」的增亮膜廠之一——這是區域競爭力，不是全球霸權。",
        )
    )
    story.append(p(s, "h2", "5.4 競爭力資產與缺口"))
    gap = simple_table(
        s,
        ["構面", "現況（已實現）", "缺口／不確定"],
        [
            ["技術", "微結構、UV 膠、複合膜、無鎘車載 QD（公司自稱首家量產）", "DBEF 等級多層光學、Micro-LED 均光是否跟得上"],
            ["認證", "車規、高階車系高輝度膜、電子紙客戶黏性", "半導體先進封裝塗布「要 2–3 年」才可能量產"],
            ["成本", "新纖體系 PET、台灣兩廠、客製化寧可減量", "標準品拼不過中國；客製化產能彈性有限"],
            ["財務", "零銀行借款、OCF 穩、可自我出資新事業", "多餘現金 ROIC 偏低；金融資產評價干擾 EPS"],
            ["規模", "年營收約 30 億、市值約 45 億", "無法定義全球規格；大客戶議價力不對稱"],
            ["產品組合", "NB 降至約五成，非 LCD 約三成", "被動元件尚未貢獻年度營收；半導體更早"],
        ],
        [28 * mm, 78 * mm, 72 * mm],
    )
    story.append(gap)
    story.append(PageBreak())

    # Ch6 scenarios
    story.append(p(s, "h1", "六、未來五年三情境（2026–2030）"))
    story.append(
        p(
            s,
            "body",
            "以下不是目標價，也不是「會漲會跌」。是把產業與公司已揭露的路徑，收成三組可證偽的營運軌道。"
            "2025 營收 30.1 億為已實現錨點。數字為約略量級，用來討論方向而非精確預算。",
        )
    )
    story.append(chart_scenarios())
    story.append(p(s, "caption", "圖 7　營收情境（億元）。灰色區間＝樂觀與保守包絡。"))

    story.append(p(s, "h2", "6.1 基準情境（主觀權重最高）"))
    story.extend(
        bullets(
            s,
            [
                "假設：NB 溫和衰退或持平；車載面積成長抵銷車市量平；電子紙續長但產業總量不大；被動元件 2026–27 開始貢獻但不到營收 10%；半導體塗布 2028 前無意義貢獻。",
                "營收：2026 年約 28–31 億（H1 已年減 7%，全年可能小負或持平），之後每年低中個位數，2030 約 32–35 億。",
                "毛利率：28–33% 區間震盪，取決於利基品能否補上標準品價格跌。營業利益率中樞 14–18%。",
                "盈餘：本業 EPS 中樞約 4–6 元，業外讓年度落在 3–7 元。股利維持「有賺就配」、發放率 50–80%。",
                "全球位子：繼續當台灣／亞洲利基供應商，不進入全球前三大 BEF 廠討論名單。",
            ],
        )
    )
    story.append(p(s, "h2", "6.2 樂觀情境"))
    story.extend(
        bullets(
            s,
            [
                "假設：無鎘車載 QD 成為中控面板材料選項之一並放量；電子紙高階應用超預期；被動元件通過歐／中／台客戶認證並在 2027 後形成年 數億營收；半導體塗布在 2028–30 開始認列。",
                "營收：2030 挑戰 40–45 億。毛利率因組合再優化站穩 33% 以上。ROE 回到 15% 以上且比較不靠業外。",
                "這情境的證偽條件：連續兩個年度非 LCD 比重不再提升、或車載毛利被中國殺價打回 NB 水準。",
            ],
        )
    )
    story.append(p(s, "h2", "6.3 保守情境"))
    story.extend(
        bullets(
            s,
            [
                "假設：OLED 車載加速、NB 長周期下滑、中國標準品價格戰打進利基規格、新事業驗證失敗或嚴重延後。",
                "營收：逐步回到 23–26 億。毛利率下滑至 22–26%（接近 2021–22）。EPS 掉到 2–3 元，配息跟著降。帳上現金仍在，破產風險極低，但會變成「高現金、低成長的類定存股」。",
                "即使走保守，負債結構使財務危機機率仍然低——這是友輝與高槓桿光電股的根本差別。",
            ],
        )
    )
    story.append(
        callout_box(
            s,
            "五年後怎麼驗收（建議觀察清單，而非預測）："
            "（1）非 LCD 營收比重是否從約 30% 再往上；"
            "（2）毛利率能否在營收持平甚至下降時仍 ≥28%；"
            "（3）被動元件是否出現連續四季可辨識的營收；"
            "（4）車載（含 QD）比重是否站穩並高於 15%；"
            "（5）本業營業利益的波動是否小於 EPS 波動（代表業外不再主導敘事）。",
        )
    )
    story.append(PageBreak())

    # Ch7 risks
    story.append(p(s, "h1", "七、主要風險與觀察清單"))
    risk = simple_table(
        s,
        ["風險", "機制", "已出現的證據", "嚴重度"],
        [
            ["LCD／OLED 替代", "自發光減少 BEF 張數", "車載 OLED 出貨預估 2030 年約 1,300 萬片", "高（結構）"],
            ["中國殺價", "標準與車載低階膜 ASP 下滑", "公司親口：中國車載毛利偏低", "高"],
            ["客戶／應用集中", "NB 仍約一半營收", "2026 因 DRAM 對 NB 轉保守", "中高"],
            ["業外干擾", "現金與 FVTPL、美金資產評價", "2025Q2 本業賺、稅後虧", "中（擾動 EPS）"],
            ["新事業執行", "被動元件／半導體驗證長", "半導體「要 2–3 年」；被動仍在送樣", "中"],
            ["關鍵原料", "PET、UV 膠、QD 材料", "PET 與集團相關，集中度需持續揭露", "中"],
            ["流動性折價", "日成交常僅數十至數百張", f"{ASOF} 成交約百張", "中（估值）"],
            ["匯率", "外銷與美元資產", "2025 其他利益損失、Q2 業外大波動", "中"],
            ["關鍵人員／集團", "新纖持股約 49%，策略受母公司影響", "長期存在", "低–中"],
        ],
        [32 * mm, 48 * mm, 62 * mm, 36 * mm],
    )
    story.append(risk)
    story.append(Spacer(1, 4 * mm))
    story.append(
        p(
            s,
            "body",
            "反過來，友輝的「下跌緩衝」也很具體：零銀行借款、每股約 32 元現金及金融資產、"
            "本業仍有 30% 毛利、股利政策讓股東在等待新事業時有現金回報。"
            "這組合比較像「高品質的成熟利基製造商＋若干未定價選擇權」，"
            "不像「高成長科技故事股」。用成長股的本益比去期待它，會失望；"
            "用「本業賺錢、資產不爆」的製造股框架，五年財務歷史是對得上的。",
        )
    )

    story.append(p(s, "h1", "結語"))
    story.append(
        p(
            s,
            "body",
            "近五年，友輝做成了一件在台灣光電業並不常見的事：營收幾乎不成長，卻把毛利率從約 25% 拉到 32%，"
            "把負債比壓在 23% 上下，並維持高配息。這證明管理層的「組合優化」不是口號。"
            "未來五年，產業不會再給一次 2020–21 那種 LCD 面積紅利；全球純 BEF 是成熟市場。"
            "公司要把同樣的能力複製到車載 QD、電子紙、被動元件與半導體塗布。"
            "複製成功，它會從「高毛利的增亮膜廠」變成「精密塗布平台」——全球競爭力上一個台階，但仍是利基。"
            "複製失敗，它大概率仍是一家不容易倒、殖利率還在、成長停滯的現金牛。"
            "兩種結局的財務下限都不差；真正的分歧是五年後毛利率與非 LCD 比重，而不是明年單季 EPS。",
        )
    )
    story.append(PageBreak())

    # Appendix
    story.append(p(s, "h1", "附錄 A　單季損益明細（仟元）"))
    q_rows = []
    for k in sorted(QUARTERLY_PL):
        y, q = k
        rev, gp, oi, pretax, ni = QUARTERLY_PL[k]
        q_rows.append(
            [
                f"{y}Q{q}",
                fmt_int(rev),
                fmt_int(gp),
                f"{gp/rev*100:.1f}%",
                fmt_int(oi),
                fmt_int(ni),
                f"{QUARTERLY_EPS[k]:.2f}",
            ]
        )
    story.append(
        simple_table(
            s,
            ["季", "營收", "毛利", "毛利率", "營業利益", "稅後淨利", "EPS"],
            q_rows,
            [22 * mm, 28 * mm, 28 * mm, 22 * mm, 28 * mm, 28 * mm, 22 * mm],
        )
    )
    story.append(p(s, "caption", "附錄 A 資料：HiStock 轉載公開財報；加總 2024／2025 與公司年報一致。"))

    story.append(p(s, "h1", "附錄 B　方法、範圍與來源"))
    story.extend(
        bullets(
            s,
            [
                f"截止日：{ASOF}。股價為櫃買當日收盤 55.10 元（Yahoo／HiStock 同日）。",
                "損益：季報加總。2024、2025 已與友輝官網公布之個體財務報告（勤業眾信，報告日 2026-03-13）核對一致。",
                "資產負債：Yahoo 股市轉載之合併報表；2025 年底權益 37.07 億與個體年報權益一致。",
                "現金流：Yahoo 單季營業現金流加總；2024／2025 與個體年報 5.63／5.81 億接近。",
                "股利：PChome 股市除權息表（盈餘年度 2021–2025）。",
                "月營收：HiStock 轉載公開資訊觀測站；2026/1–6 累計 1,416,374 仟元、年減 7.2%。",
                "產品組合與新事業：經濟日報、MoneyDJ、Yahoo 新聞對 2025-11 與 2026 法說的轉述；非財報科目，約數。",
                "產業規模：Strategic Market Research（整體光學膜）；Research and Markets、IndexBox（BEF）；UBI Research（車載 Mini-LED／OLED）。不同機構口徑不同，只作量級。",
                "未使用 FinMind／FRED API。本環境無 augur 生產資料庫，故未引用庫內 panel。",
                "前瞻段落為情境分析（self-reported），不是財務預測書、不是評等、不是投資建議。",
            ],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p(s, "h2", "主要公開來源 URL"))
    urls = [
        "公司官網 https://www.ubright.com.tw/",
        "2025 個體年報 PDF https://www.ubright.com.tw/wp-content/uploads/2025/11/2025-Q4-個體-中文.pdf",
        "HiStock 損益／EPS／毛利率 https://histock.tw/stock/4933/",
        "Yahoo 資產負債／現金流 https://tw.stock.yahoo.com/quote/4933.TWO",
        "PChome 股利 https://pchome.megatime.com.tw/stock/sto3/ock1/sid4933.html",
        "財報狗資產／負債 https://statementdog.com/analysis/4933/",
    ]
    for u in urls:
        story.append(p(s, "small", u))
    story.append(Spacer(1, 6 * mm))
    story.append(
        p(
            s,
            "small",
            "編製：依公開資訊整理之分析報告。任何錯誤以發行人向公開資訊觀測站申報之財報為準。"
            "轉載或投資決策請自行承擔風險。",
        )
    )
    return story


def build_pdf(out: Path) -> Path:
    _setup_mpl()
    font = register_font()
    styles = make_styles(font)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="友輝光電（4933）近五年財務分析與未來五年前景、全球競爭力報告",
        author="公開資訊整理",
        subject=f"4933 UBright financial and industry outlook as of {ASOF}",
    )
    doc.build(build_story(styles), onFirstPage=header_footer, onLaterPages=header_footer)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="產生 4933 友輝財務與前景 PDF")
    parser.add_argument("--out", type=Path, default=OUT_DEFAULT, help="輸出 PDF 路徑")
    parser.add_argument("--selftest", action="store_true", help="零外部依賴核對年報加總")
    parser.add_argument("--also", type=Path, nargs="*", default=[], help="額外複製一份到這些路徑")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    rc = selftest()
    if rc != 0:
        return rc
    path = build_pdf(args.out)
    print(f"WROTE {path} ({path.stat().st_size} bytes)")
    for extra in args.also:
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_bytes(path.read_bytes())
        print(f"COPIED {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
