#!/usr/bin/env python3
"""Generate HIM (8446) 5-year financial & outlook PDF.

Numbers are sourced from public filings / aggregators listed in the report.
This is not investment advice.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
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

ROOT = Path(__file__).resolve().parent
CHART_DIR = ROOT / "charts"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

NAVY = colors.HexColor("#1B2A4A")
GOLD = colors.HexColor("#C4A35A")
CREAM = colors.HexColor("#F7F4EE")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#5A5A5A")
GREEN = colors.HexColor("#2E7D4F")
RED = colors.HexColor("#B23A3A")
LINE = colors.HexColor("#D9D2C5")
ROW_ALT = colors.HexColor("#F3EFE6")

YEARS = ["2021", "2022", "2023", "2024", "2025"]
# 合併損益：季報加總，與公司 2023–2025 年報核對一致；單位百萬新台幣
REV = [836.57, 897.37, 1198.53, 1375.49, 1084.71]
GP = [656.85, 639.29, 727.71, 861.89, 726.51]
OI = [384.14, 418.09, 466.69, 593.04, 456.48]
PBT = [413.43, 376.03, 524.55, 747.20, 673.17]
NI = [347.32, 314.26, 435.60, 605.43, 545.18]
EPS = [6.56, 5.94, 8.23, 11.44, 10.30]
GM = [r / v * 100 for r, v in zip(GP, REV)]
OM = [r / v * 100 for r, v in zip(OI, REV)]
NM = [r / v * 100 for r, v in zip(NI, REV)]

ASSETS = [3213, 3126, 3245, 2898, 2917]
EQUITY = [1570, 1649, 1820, 2109, 2231]
DEBT = [1139, 926, 710, 160, 116]
CASH_STI = [1187, 1298, 1686, 1389, 1470]
NET_CASH = [48, 372, 976, 1229, 1354]
BVPS = [29.69, 31.16, 34.40, 39.86, 42.18]

OCF = [356.04, 554.04, 618.35, 561.74, 456.71]
FCF = [355.58, 550.80, 616.71, 558.78, 455.16]
DIV_PAID = [185.20, 238.12, 264.57, 317.49, 423.32]
DIV_PER_SHARE_PAID = [3.5, 4.5, 5.0, 6.0, 8.0]  # 該年現金流出＝前一年度盈餘配發

SHARES = 52.9144  # 百萬股；股本 529.144 百萬
PRICE = 85.20  # 2026-08-27 收盤
TTM_NI = 415.42
TTM_REV = 1182.0
TTM_OI = 476.88


def _setup_fonts() -> None:
    pdfmetrics.registerFont(TTFont("CN", FONT_PATH, subfontIndex=0))
    try:
        font_manager.fontManager.addfont(FONT_PATH)
    except Exception:
        pass
    name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = name
    plt.rcParams["font.sans-serif"] = [name, "WenQuanYi Micro Hei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="CoverKicker", fontName="CN", fontSize=10, textColor=GOLD, alignment=TA_CENTER, tracking=1.2))
    ss.add(ParagraphStyle(name="CoverTitle", fontName="CN", fontSize=22, leading=30, textColor=colors.white, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle(name="CoverSub", fontName="CN", fontSize=12, leading=18, textColor=colors.HexColor("#E8E0D0"), alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="H1", fontName="CN", fontSize=14, leading=20, textColor=NAVY, spaceBefore=10, spaceAfter=6))
    ss.add(ParagraphStyle(name="H2", fontName="CN", fontSize=12, leading=17, textColor=colors.HexColor("#3D4F73"), spaceBefore=8, spaceAfter=4))
    ss.add(ParagraphStyle(name="Body", fontName="CN", fontSize=9.2, leading=14.2, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6))
    ss.add(ParagraphStyle(name="BulletBody", fontName="CN", fontSize=9.2, leading=13.8, textColor=INK, leftIndent=2))
    ss.add(ParagraphStyle(name="Caption", fontName="CN", fontSize=8, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8))
    ss.add(ParagraphStyle(name="Footer", fontName="CN", fontSize=7.5, textColor=MUTED))
    ss.add(ParagraphStyle(name="Small", fontName="CN", fontSize=8, leading=11.5, textColor=MUTED, alignment=TA_JUSTIFY))
    ss.add(ParagraphStyle(name="Callout", fontName="CN", fontSize=9.5, leading=14.5, textColor=NAVY, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="Th", fontName="CN", fontSize=7.8, leading=11, textColor=colors.white, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="Td", fontName="CN", fontSize=7.8, leading=11, textColor=INK, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="TdL", fontName="CN", fontSize=7.8, leading=11, textColor=INK, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="Disclaimer", fontName="CN", fontSize=8, leading=12, textColor=MUTED, alignment=TA_JUSTIFY))
    return ss


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 14.8 * mm, w, 1.2 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("CN", 8)
        canvas.drawString(16 * mm, h - 9.2 * mm, "華研國際音樂（8446）｜近五年財務分析與未來五年前景")
        canvas.drawRightString(w - 16 * mm, h - 9.2 * mm, "2026-08-27")
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(MUTED)
        canvas.setFont("CN", 7.5)
        canvas.drawString(16 * mm, 5 * mm, "公開資訊彙編｜非投資建議｜self-reported 前景段落")
        canvas.drawRightString(w - 16 * mm, 5 * mm, f"{doc.page}")
    canvas.restoreState()


def _cover_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 28 * mm, w, 8 * mm, fill=1, stroke=0)
    canvas.rect(0, 22 * mm, w, 3 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("CN", 10)
    canvas.drawCentredString(w / 2, h - 24 * mm, "EQUITY RESEARCH  ·  CULTURAL & CREATIVE")
    canvas.setFont("CN", 13)
    canvas.drawCentredString(w / 2, h * 0.62 + 46, "華研國際音樂股份有限公司")
    canvas.setFont("CN", 22)
    canvas.drawCentredString(w / 2, h * 0.62 + 14, "近五年財務分析")
    canvas.drawCentredString(w / 2, h * 0.62 - 16, "與未來五年前景／全球競爭力")
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.6)
    canvas.line(w * 0.28, h * 0.62 - 30, w * 0.72, h * 0.62 - 30)
    canvas.setFillColor(colors.HexColor("#E8E0D0"))
    canvas.setFont("CN", 11)
    canvas.drawCentredString(w / 2, h * 0.62 - 52, "櫃買代號 8446　｜　HIM International Music")
    canvas.setFont("CN", 9)
    canvas.drawCentredString(w / 2, h * 0.38, "報告日：2026 年 8 月 27 日")
    canvas.drawCentredString(w / 2, h * 0.38 - 16, "股價錨點：85.20 元（2026-08-27 收盤）")
    canvas.drawCentredString(w / 2, h * 0.38 - 32, "財報覆蓋：2021 全年～2025 全年，並含 2026 上半年")
    canvas.setFillColor(GOLD)
    canvas.setFont("CN", 8.5)
    canvas.drawCentredString(w / 2, 32 * mm, "本報告僅供研究參考，不構成買賣建議")
    canvas.restoreState()


def _p(ss, text, style="Body"):
    return Paragraph(text, ss[style])


def _kpi_table(ss):
    mkt = PRICE * SHARES
    ttm_eps = TTM_NI / SHARES
    pe = PRICE / ttm_eps
    pb = PRICE / 38.03
    dy = 8.0 / PRICE * 100
    data = [
        [Paragraph(x, ss["Th"]) for x in ["市值", "TTM 本益比", "股價淨值比", "現金殖利率", "2025 EPS", "淨現金／股"]],
        [
            Paragraph(f"{mkt/100:.1f} 億", ss["Td"]),
            Paragraph(f"{pe:.1f}×", ss["Td"]),
            Paragraph(f"{pb:.2f}×", ss["Td"]),
            Paragraph(f"{dy:.1f}%", ss["Td"]),
            Paragraph("10.30 元", ss["Td"]),
            Paragraph(f"{NET_CASH[-1]/SHARES:.1f} 元", ss["Td"]),
        ],
    ]
    t = Table(data, colWidths=[28 * mm] * 6)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BACKGROUND", (0, 1), (-1, 1), CREAM),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.4, GOLD),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
            ]
        )
    )
    return t


def _grid(ss, headers, rows, col_widths=None):
    head = [Paragraph(h, ss["Th"]) for h in headers]
    body = []
    for row in rows:
        cells = []
        for i, c in enumerate(row):
            st = ss["TdL"] if i == 0 else ss["Td"]
            cells.append(Paragraph(str(c), st))
        body.append(cells)
    t = Table([head] + body, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LINE),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]
    for i in range(1, len(body) + 1):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        else:
            cmds.append(("BACKGROUND", (0, i), (-1, i), colors.white))
    t.setStyle(TableStyle(cmds))
    return t


def _save_charts() -> dict[str, Path]:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    fig_w, fig_h = 9.2, 3.6

    fig, ax1 = plt.subplots(figsize=(fig_w, fig_h), dpi=140)
    x = list(range(len(YEARS)))
    b1 = ax1.bar([i - 0.18 for i in x], REV, width=0.36, color="#1B2A4A", label="營收")
    b2 = ax1.bar([i + 0.18 for i in x], NI, width=0.36, color="#C4A35A", label="稅後淨利")
    ax1.set_xticks(x, YEARS)
    ax1.set_ylabel("百萬新台幣")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(frameon=False, loc="upper left")
    ax1.set_title("合併營收與稅後淨利（2021–2025）", loc="left", fontsize=11, color="#1B2A4A")
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 18, f"{h:.0f}", ha="center", va="bottom", fontsize=7, color="#333")
    fig.tight_layout()
    paths["rev"] = CHART_DIR / "rev_ni.png"
    fig.savefig(paths["rev"], bbox_inches="tight", facecolor="white")
    plt.close()

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=140)
    ax.plot(YEARS, GM, marker="o", color="#1B2A4A", label="毛利率")
    ax.plot(YEARS, OM, marker="s", color="#C4A35A", label="營業利益率")
    ax.plot(YEARS, NM, marker="^", color="#2E7D4F", label="淨利率")
    ax.set_ylabel("%")
    ax.set_ylim(20, 90)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("獲利率走勢：授權年份 vs 演唱會年份", loc="left", fontsize=11, color="#1B2A4A")
    fig.tight_layout()
    paths["margin"] = CHART_DIR / "margins.png"
    fig.savefig(paths["margin"], bbox_inches="tight", facecolor="white")
    plt.close()

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=140)
    ax.plot(YEARS, CASH_STI, marker="o", color="#1B2A4A", label="現金＋短投")
    ax.plot(YEARS, DEBT, marker="s", color="#B23A3A", label="有息負債")
    ax.plot(YEARS, NET_CASH, marker="^", color="#2E7D4F", label="淨現金")
    ax.plot(YEARS, EQUITY, marker="d", color="#C4A35A", label="股東權益")
    ax.set_ylabel("百萬新台幣")
    ax.legend(frameon=False, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("資產負債：去槓桿與淨現金累積", loc="left", fontsize=11, color="#1B2A4A")
    fig.tight_layout()
    paths["bs"] = CHART_DIR / "balance.png"
    fig.savefig(paths["bs"], bbox_inches="tight", facecolor="white")
    plt.close()

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=140)
    ax.bar([i - 0.2 for i in x], OCF, width=0.4, color="#1B2A4A", label="營業現金流")
    ax.bar([i + 0.2 for i in x], DIV_PAID, width=0.4, color="#C4A35A", label="現金股利")
    ax.set_xticks(x, YEARS)
    ax.set_ylabel("百萬新台幣")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("營業現金流 vs 現金股利（高配息仍被本業現金覆蓋）", loc="left", fontsize=11, color="#1B2A4A")
    fig.tight_layout()
    paths["cf"] = CHART_DIR / "cashflow.png"
    fig.savefig(paths["cf"], bbox_inches="tight", facecolor="white")
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(fig_w, 3.8), dpi=140)
    mix24 = [2, 48, 50]
    mix25 = [0.6, 58.3, 41.1]
    colors_pie = ["#8A8478", "#C4A35A", "#1B2A4A"]
    labels = ["實體產品", "授權", "演藝經紀"]
    axes[0].pie(mix24, labels=labels, colors=colors_pie, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
    axes[0].set_title("2024 營收結構", fontsize=10, color="#1B2A4A")
    axes[1].pie(mix25, labels=labels, colors=colors_pie, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
    axes[1].set_title("2025 營收結構", fontsize=10, color="#1B2A4A")
    fig.tight_layout()
    paths["mix"] = CHART_DIR / "mix.png"
    fig.savefig(paths["mix"], bbox_inches="tight", facecolor="white")
    plt.close()

    fig, ax = plt.subplots(figsize=(fig_w, 3.8), dpi=140)
    names = ["華研 2025", "JYP 2025", "HYBE 2025"]
    # 約當億美元：華研 ~0.034、JYP ~0.58、HYBE 1.86（匯率示意，僅比量級）
    vals = [0.034, 0.58, 1.86]
    ax.barh(names, vals, color=["#C4A35A", "#5A6F93", "#1B2A4A"])
    ax.set_xlabel("約當年營收（十億美元，量級比較）")
    ax.set_title("全球娛樂公司量級：華研是精品曲庫，不是平台型巨頭", loc="left", fontsize=11, color="#1B2A4A")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, v in enumerate(vals):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    paths["scale"] = CHART_DIR / "scale.png"
    fig.savefig(paths["scale"], bbox_inches="tight", facecolor="white")
    plt.close()
    return paths


def _img(path: Path, width=175 * mm):
    return Image(str(path), width=width, height=width * 0.40)


def _callout(ss, text):
    inner = Paragraph(text, ss["Callout"])
    t = Table([[inner]], colWidths=[178 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.8, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def build_story(ss, charts: dict[str, Path]):
    story = []
    story.append(PageBreak())

    story.append(_p(ss, "一、執行摘要", "H1"))
    story.append(
        _callout(
            ss,
            "一句定錨：華研是「高毛利華語曲庫＋頭部藝人巡演」的現金機器，不是全球造星平台。"
            "近五年獲利在疫情低點後走高，2024 EPS 11.44 元見高、2025 因巡演空窗回落至 10.30 元仍屬歷史次高；"
            "2026 上半年本業已回升，下半年約 20 場巡演與預收款跳升是可見的領先指標。",
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(_kpi_table(ss))
    story.append(_p(ss, "圖表與比率以 2026-08-27 收盤價 85.20 元、流通 5,291.44 萬股計算。TTM＝截至 2026/6/30。", "Caption"))

    story.append(
        _p(
            ss,
            "近五年（2021–2025）合併營收自 8.37 億升至 2024 高峰 13.75 億、2025 因演唱會準備週期回落到 10.85 億（-21.1%）。"
            "同一期間稅後淨利自 3.47 億升至 2024 的 6.05 億、2025 仍有 5.45 億；淨利率 2025 反而升到約 50%，"
            "因為授權占比回升、且處分網易雲音樂（Cloud Village）持股貢獻業外。本業營業利益 2025 為 4.56 億、營益率 42%，"
            "仍遠高於一般傳產與多數娛樂同業。資產負債表同步去槓桿：有息負債由 2021 年底 11.4 億降至 2025 年底 1.2 億，"
            "淨現金 13.5 億、約每股 25.5 元。現金股利由 3.5 元一路加到 8 元（2025、2026 連續兩年），殖利率以現價計約 9.4%。",
        )
    )
    story.append(
        _p(
            ss,
            "未來五年（2026–2030）的產業底盤偏多：IFPI《Global Music Report 2026》顯示 2025 年全球錄音產業收入 317 億美元、連十一年成長，"
            "串流佔 69.6%；中國躍居全球第四大市場、年增 20.1%。華研 2024 外銷已佔 82%，曲庫變現高度綁大中華數位平台與華語巡演圈。"
            "全球競爭力上，它在華語「經典曲庫授權」有真實護城河（S.H.E、林宥嘉、動力火車、F.I.R. 等錄音與詞曲資產仍在公司），"
            "但對 HYBE／JYP 這類全球粉絲平台＋多團巡演機器，量級差兩個數量級，英語市場與超級粉絲生態幾乎空白。"
            "合理基準（self-reported、非目標價）：巡演大年營收落在 12–16 億、EPS 8–12 元；空窗年靠授權守住高個位數 EPS 與高配息。"
            "要升級成成長股，必須證明第二代藝人能獨立撐起票房，而不是只靠兩組頭部巡演的週期。",
        )
    )

    story.append(_p(ss, "二、公司與商業模式", "H1"))
    story.append(
        _p(
            ss,
            "華研國際音樂成立於 1999 年，2013 年 12 月櫃買掛牌，是台灣少數以流行音樂為本業的上櫃公司。"
            "主業三塊：① 錄音著作與詞曲之數位／影視／KTV／公播授權；② 藝人演藝經紀與世界巡迴演唱會；③ 實體專輯、周邊（佔比已極低）。"
            "公開資料稱曲庫約 2,000–2,400 首錄音著作、約 1,600–1,700 首詞曲、數百部視聽著作；旗下約 40 位藝人。"
            "現役票房支柱為動力火車、林宥嘉，另有郁可唯、F.I.R.、周蕙、閻奕格、曾沛慈、李友廷及女團 babyMINT 等。"
            "S.H.E 經紀約於 2018 年不續，但歌曲所屬權仍在華研——這是後來「曲庫授權現金流」敘事的起點。",
        )
    )
    story.append(
        _p(
            ss,
            "經濟本質：一首已完成的歌曲是沉沒成本，之後在 Spotify／QQ 音樂／網易雲／YouTube／短影音／廣告／影視的每一次播放都是高增量毛利。"
            "演唱會則相反——場租、製作、差旅、分潤，毛利率明顯較低，但能一次認列大額營收、並回頭拉抬曲庫與商演。"
            "因此財報呈現「授權年：營收較小、毛利率極高；巡演年：營收放大、毛利率被稀釋、絕對利潤未必差」。"
            "2024 營收結構約為授權 48%、演藝經紀 50%、實體 2%；2025 巡演空窗後授權回升至 58.3%、演藝 41.1%、實體 0.6%。"
            "2024 銷售地區：內銷 18%、外銷 82%，中國數位授權與海外巡演是規模所在，也是地緣與平台議價的集中風險。",
        )
    )

    story.append(_p(ss, "三、近五年損益分析", "H1"))
    story.append(_img(charts["rev"]))
    story.append(_p(ss, "資料：合併綜合損益季報加總；2023–2025 與公司年報核對一致。單位：百萬新台幣。", "Caption"))

    yoy = ["—"] + [f"{(REV[i]/REV[i-1]-1)*100:+.1f}%" for i in range(1, 5)]
    story.append(
        _grid(
            ss,
            ["科目", "2021", "2022", "2023", "2024", "2025"],
            [
                ["營業收入（百萬）", f"{REV[0]:.0f}", f"{REV[1]:.0f}", f"{REV[2]:.0f}", f"{REV[3]:.0f}", f"{REV[4]:.0f}"],
                ["營收年增", *yoy],
                ["營業毛利", f"{GP[0]:.0f}", f"{GP[1]:.0f}", f"{GP[2]:.0f}", f"{GP[3]:.0f}", f"{GP[4]:.0f}"],
                ["毛利率", f"{GM[0]:.1f}%", f"{GM[1]:.1f}%", f"{GM[2]:.1f}%", f"{GM[3]:.1f}%", f"{GM[4]:.1f}%"],
                ["營業利益", f"{OI[0]:.0f}", f"{OI[1]:.0f}", f"{OI[2]:.0f}", f"{OI[3]:.0f}", f"{OI[4]:.0f}"],
                ["營業利益率", f"{OM[0]:.1f}%", f"{OM[1]:.1f}%", f"{OM[2]:.1f}%", f"{OM[3]:.1f}%", f"{OM[4]:.1f}%"],
                ["稅前淨利", f"{PBT[0]:.0f}", f"{PBT[1]:.0f}", f"{PBT[2]:.0f}", f"{PBT[3]:.0f}", f"{PBT[4]:.0f}"],
                ["稅後淨利", f"{NI[0]:.0f}", f"{NI[1]:.0f}", f"{NI[2]:.0f}", f"{NI[3]:.0f}", f"{NI[4]:.0f}"],
                ["淨利率", f"{NM[0]:.1f}%", f"{NM[1]:.1f}%", f"{NM[2]:.1f}%", f"{NM[3]:.1f}%", f"{NM[4]:.1f}%"],
                ["EPS（元）", f"{EPS[0]:.2f}", f"{EPS[1]:.2f}", f"{EPS[2]:.2f}", f"{EPS[3]:.2f}", f"{EPS[4]:.2f}"],
            ],
            col_widths=[38 * mm] + [28 * mm] * 5,
        )
    )
    story.append(_p(ss, "表 1　合併損益五年摘要。淨利採歸屬母公司／與 EPS 對應之年報口徑。", "Caption"))

    story.append(_p(ss, "3.1 營收：疫情谷底 → 巡演高峰 → 準備年回檔", "H2"))
    story.append(
        _p(
            ss,
            "2020–2021 現場演出停擺，月營收年減約三成（2021 全年 8.37 億、較 2020 的約 11.65 億 -28%）。"
            "2022 微升 7.3% 到 8.97 億，解封剛開始。2023 年增 33.6% 到 12.0 億、2024 再增 14.8% 到 13.75 億，"
            "對應林宥嘉《idol》、動力火車《都是因為愛》等大型巡演放量。"
            "2025 公司自述：林宥嘉巡演 2024 年底收官、動力火車 2025 年 10 月落幕，該年處於「正常準備週期、場次較少」，"
            "營收 10.85 億、-21.1%。這是商業模式的季節，不是授權崩盤：授權絕對額 2025 仍有 6.32 億，高於許多年份的全部營收。",
        )
    )
    story.append(_img(charts["margin"]))
    story.append(_p(ss, "授權年份毛利率可到 70–80%；巡演年份掉到約 60%。營業利益率五年都在 39–46%，結構極強。", "Caption"))

    story.append(_p(ss, "3.2 獲利率：組合變化大於成本失控", "H2"))
    story.append(
        _p(
            ss,
            "毛利率 2021 約 78.5%（幾乎是純授權），2023–2024 因演藝占比拉高降至 61–63%，2025 授權回升、毛利率回到 67%。"
            "營業利益率五年落在 39–46%，費用並未隨營收等比爆炸——推銷／管理／音樂製作（帳上研發）相對穩定。"
            "2024 營業利益 5.93 億為五年高峰；2025 本業 4.56 億，年減 23%，幅度與營收接近。"
            "但 2025 稅後只年減 10%，因為業外淨利由 2024 的 1.54 億升至 2.17 億，其中處分及評價 Cloud Village 利益 1.20 億。"
            "這筆業外 2026 年已沒有：公司明說持股於 2025 上半年處分完畢。讀 2026 年獲利必須把「本業」和「業外一次性」拆開。"
            "實證：2026 上半年營業利益 2.43 億、優於 2025 同期 2.22 億；稅後 2.04 億卻低於去年同期 3.34 億——差距幾乎全是少了金融資產利益。",
        )
    )

    story.append(_p(ss, "3.3 2026 年迄今：本業回升，預收款是領先指標", "H2"))
    story.append(
        _grid(
            ss,
            ["期間", "營收", "毛利率", "營業利益", "稅後（母公司）", "EPS"],
            [
                ["2026Q1", "2.18 億", "72.6%", "0.97 億", "0.94 億", "1.78"],
                ["2026Q2", "3.99 億", "53.7%", "1.46 億", "1.10 億", "2.07"],
                ["2026H1", "6.17 億", "60.4%", "2.43 億", "2.04 億", "3.85"],
                ["2025H1（對照）", "5.20 億", "68.3%", "2.22 億", "3.34 億", "6.31"],
            ],
            col_widths=[32 * mm] + [29.2 * mm] * 5,
        )
    )
    story.append(_p(ss, "表 2　2026 上半年 vs 2025 上半年。Q2 毛利率下降反映動力火車小巨蛋等現場成本入帳。", "Caption"))
    story.append(
        _p(
            ss,
            "公司指出：2026 上半年 5 場、下半年預計約 20 場，包括動力火車《一路向前》（台北小巨蛋三場秒殺）與林宥嘉《超級管家》世界巡迴（6 月廣州起跑）。"
            "資產負債表上「預收／合約負債」由 2025 年底 1.69 億跳到 2026/6/30 的 4.08 億——這是已售票、尚未認列的演唱會收入，"
            "對下半年營收是可核對的領先指標，不是口頭展望。H1 月營收累計年增約 18.6%。",
        )
    )

    story.append(PageBreak())
    story.append(_p(ss, "四、資產負債、現金流與股利", "H1"))
    story.append(_img(charts["bs"]))
    story.append(_p(ss, "有息負債五年砍掉九成；淨現金從幾乎為零變成每股超過 25 元。", "Caption"))

    cr = [1811 / 1459, 1717 / 1322, 1775 / 1283, 1452 / 648, 1548 / 587]
    de = [1139 / 1571, 926 / 1649, 710 / 1820, 160 / 2109, 116 / 2231]
    roe = [NI[i] / EQUITY[i] * 100 for i in range(5)]
    roa = [NI[i] / ASSETS[i] * 100 for i in range(5)]
    story.append(
        _grid(
            ss,
            ["科目", "2021", "2022", "2023", "2024", "2025"],
            [
                ["資產總額", "3,213", "3,126", "3,245", "2,898", "2,917"],
                ["股東權益", "1,570", "1,649", "1,820", "2,109", "2,231"],
                ["有息負債", "1,139", "926", "710", "160", "116"],
                ["現金＋短投", "1,187", "1,298", "1,686", "1,389", "1,470"],
                ["淨現金", "48", "372", "976", "1,229", "1,354"],
                ["每股淨值（元）", "29.69", "31.16", "34.40", "39.86", "42.18"],
                ["流動比", f"{cr[0]:.2f}", f"{cr[1]:.2f}", f"{cr[2]:.2f}", f"{cr[3]:.2f}", f"{cr[4]:.2f}"],
                ["負債／權益", f"{de[0]:.0%}", f"{de[1]:.0%}", f"{de[2]:.0%}", f"{de[3]:.0%}", f"{de[4]:.0%}"],
                ["ROE（期末）", f"{roe[0]:.1f}%", f"{roe[1]:.1f}%", f"{roe[2]:.1f}%", f"{roe[3]:.1f}%", f"{roe[4]:.1f}%"],
                ["ROA（期末）", f"{roa[0]:.1f}%", f"{roa[1]:.1f}%", f"{roa[2]:.1f}%", f"{roa[3]:.1f}%", f"{roa[4]:.1f}%"],
            ],
            col_widths=[38 * mm] + [28 * mm] * 5,
        )
    )
    story.append(_p(ss, "表 3　資產負債與報酬率。單位除比率、每股外為百萬新台幣。ROE 用期末權益（未平均）以便五年連續比較。", "Caption"))
    story.append(
        _p(
            ss,
            "財務政策清楚：用營業現金流還短債、發股利。2021 仍有短債 9.4 億；2024 單年償還短債 5.5 億，負債比從 73% 壓到 8% 以下。"
            "2024–2025 資產總額下降，主因還債與金融資產處分，不是營運萎縮造成的資不抵債。"
            "長期資產約 11.5 億「其他長期資產」主要是投資性不動產（租金進業外），提供穩定但非核心的利息／租金底倉。"
            "無形資產（曲庫相關攤銷資產）2025 年底約 0.62 億——帳面遠遠低於曲庫經濟價值，這是音樂公司普遍的會計落差，"
            "分析時應看授權現金流，而不是把無形資產當成曲庫市值。",
        )
    )

    story.append(_img(charts["cf"]))
    fcf_m = [FCF[i] / REV[i] * 100 for i in range(5)]
    payout_next = ["68.6%", "84.2%", "72.9%", "69.9%", "77.7%"]  # 當年EPS對次年已宣布／已付現金股利
    story.append(
        _grid(
            ss,
            ["科目", "2021", "2022", "2023", "2024", "2025"],
            [
                ["營業現金流", "356", "554", "618", "562", "457"],
                ["自由現金流", "356", "551", "617", "559", "455"],
                ["FCF 利潤率", f"{fcf_m[0]:.0f}%", f"{fcf_m[1]:.0f}%", f"{fcf_m[2]:.0f}%", f"{fcf_m[3]:.0f}%", f"{fcf_m[4]:.0f}%"],
                ["該年現金股利", "185", "238", "265", "317", "423"],
                ["每股現金（該年付出）", "3.5", "4.5", "5.0", "6.0", "8.0"],
                ["該年盈餘現金配發率", payout_next[0], payout_next[1], payout_next[2], payout_next[3], payout_next[4]],
            ],
            col_widths=[42 * mm] + [27.2 * mm] * 5,
        )
    )
    story.append(
        _p(
            ss,
            "表 4　現金流與股利。配發率定義為「次年付出之現金股利 ÷ 當年 EPS」。2026 年 5 月已再配 8 元（對 2025 EPS 10.30）。"
            "五年 FCF 年年覆蓋股利；資本支出極低（每年數百萬到兩、三千萬），音樂製作多走費用化，這是輕資產高配息能成立的原因。",
            "Caption",
        )
    )
    story.append(
        _p(
            ss,
            "評價位置（描述、非建議）：現價 85.2 元、TTM EPS 約 7.85 元 → 本益比約 10.8 倍；對 2025 全年 EPS 10.30 則約 8.3 倍。"
            "P/B 約 2.0–2.2（視用年底或除息後淨值）。現金殖利率約 9.4%。"
            "TTM 營業利益 4.77 億、企業價值（市值 45.1 億－淨現金 13.5 億）約 31.6 億 → EV/EBIT 約 6.6 倍。"
            "市場付的是「高殖利率的曲庫現金流」，沒有付「全球偶像工業」的成長溢價。股價從歷史高點回落後，走勢落後於 2023–2024 盈餘復甦——"
            "這可以解釋為巡演週期折現、中國曝險折價，或市場不願把業外利益資本化。",
        )
    )

    story.append(_p(ss, "五、營運結構與質化觀察", "H1"))
    story.append(_img(charts["mix"]))
    story.append(_p(ss, "2024 為雙引擎；2025 授權重新過半。實體產品已可忽略。", "Caption"))
    story.append(
        _p(
            ss,
            "授權：數位串流、影視同步、廣告、KTV、公播。這是護城河與估值底。中國付費串流仍在升級（超會、SVIP），IFPI 指中國 2025 年增 20.1%、成為全球第四大錄音市場。"
            "華研作為華語經典供給方，對平台有內容籌碼，但單一市場／少數平台的議價仍可能壓授權費率。"
            "演藝：毛利率較低（現場成本、海外分潤），波動大，卻是品牌與新歌的放大器。2026 巡演檔期密集，是本業恢復的主引擎。"
            "新人與詞曲：公司 2026 擴大第 20 屆全球網路詞曲創作大賽（百萬預付簽約金、創作營），並推出「音樂產房」計畫。"
            "這是正確的長期投資，但財報上還看不到足以替代頭部兩組的第二曲線——這是五年前景的最大未知數。",
        )
    )

    story.append(PageBreak())
    story.append(_p(ss, "六、產業未來五年：全球錄音、華語與現場", "H1"))
    story.append(_p(ss, "6.1 全球錄音產業（已實現數字）", "H2"))
    story.append(
        _p(
            ss,
            "IFPI Global Music Report 2026：2025 年全球錄音收入 317 億美元，年增 6.4%，連續第 11 年成長，並首度越過 300 億。"
            "串流收入突破 220 億、佔 69.6%；其中付費訂閱年增 8.8%、佔總收入 52.4%，付費帳戶 8.37 億。"
            "亞洲年增 10.9%；日本回升 8.9%；中國年增 20.1%，超越德國成為全球第四大市場。"
            "實體年增 8.0%（黑膠 +13.7%），下載繼續萎縮。威脅面：串流造假、生成式 AI 內容、成熟市場（北美）增速放緩。"
            "對華研的含義：它所賣的「正版華語錄音授權」正處於全球與中國都還在擴的池子裡，不是夕陽實體唱片。",
        )
    )
    story.append(_p(ss, "6.2 現場演出與華語流行", "H2"))
    story.append(
        _p(
            ss,
            "疫後全球現場娛樂的特徵是：頭部場館／巡演需求極強、中腰部分化。K-pop 把巡演做成可出口的工業（HYBE 2025 演唱會收入 7,639 億韓元、約 5.4 億美元，年增 69%；全年營收 2.65 兆韓元、約 18.6 億美元）。"
            "華語市場的現場則高度集中在華語圈場館與音樂節，票房可以很好（小巨蛋秒殺是真實需求），但較難複製成歐美體育場巡演網。"
            "中國營業性演出票房在政策與消費意願允許時能高速成長，也隨時受審批、場館供給、總量調控影響。"
            "台灣作為內容原產地：創作密度高、金曲獎與華語經典仍有文化權重，但內需人口不足以養活全球級偶像工業；出口幾乎等於大中華＋新馬。"
            "未來五年華語流行的結構機會：短影音發現 → 串流變現 → 現場收割的閉環仍在；風險是年輕聽眾時長被 K-pop、短影音 BGM、AI 翻唱切走。",
        )
    )
    story.append(_p(ss, "6.3 科技變數：短影音、超粉、AI", "H2"))
    story.append(
        _p(
            ss,
            "短影音（抖音／TikTok／Reels）已是新歌與舊曲第二生命的主戰場，同步授權與廣告分潤會繼續成長，但也讓「爆款」更短命。"
            "超粉經濟（會員、周邊、專屬內容）是 HYBE Weverse、JYP 與 Live Nation 聯盟在做的事；華研尚未顯示對等的自有粉絲平台。"
            "生成式 AI：對「新發行」可能帶來廉價供給與串流污染；對「有情緒記憶的經典曲庫」傷害較慢，因為廣告主、影視、KTV 與現場仍要可識別的人聲與作品。"
            "IFPI 已把串流詐欺列為產業議題。權利人若能證明真實人氣，平台分潤談判才站得住。"
            "五年視窗內，華研較可能的科技紅利是：用 AI 降翻唱／多語宣傳成本、加速詞曲篩選；較不可能的是靠虛擬偶像一夜變成全球公司。",
        )
    )

    story.append(_p(ss, "七、全球競爭力評估", "H1"))
    story.append(_img(charts["scale"]))
    story.append(_p(ss, "營收量級為示意換算，只用來標尺度，不當作精確匯率評價。", "Caption"))
    story.append(
        _grid(
            ss,
            ["構面", "華研位置", "對照", "五年含義"],
            [
                ["曲庫深度（華語）", "強", "S.H.E／林宥嘉／動力火車／F.I.R. 等可授權資產", "授權底倉可續"],
                ["造星工業", "中偏弱", "無 HYBE 式多團流水線；詞曲大賽是正確但不夠", "第二曲線未證成"],
                ["現場出口", "區域強、全球弱", "華語巡演圈 vs BTS 82 場全球網", "大年看華語場館供給"],
                ["平台／超粉", "弱", "無自有全球粉籍與電商中台", "變現仍靠第三方"],
                ["財務質量", "極強", "淨現金、FCF、高 ROE、低 capex", "能熬過空窗年"],
                ["地理多元化", "弱", "2024 外銷 82%，中國權重高", "平台與政策單一風險"],
                ["語系／文化圈", "華語精品", "K-pop、拉丁、非洲是全球增量主戰場", "難吃到英語主流"],
            ],
            col_widths=[32 * mm, 28 * mm, 58 * mm, 52 * mm],
        )
    )
    story.append(_p(ss, "表 5　競爭力計分卡（質化、self-reported）。", "Caption"))
    story.append(
        _p(
            ss,
            "同業地圖：台灣側是相信音樂（五月天）、杰威爾（周杰倫）、滾石、福茂、種子與三大國際公司在台子公司——"
            "多數未上市，華研的「可投資標的稀缺」本身是溢價來源之一。"
            "中國側對手是平台（騰訊音樂、網易雲）而非唱片公司：華研是供給方，平台是通路與議價對手。"
            "韓國側 HYBE／JYP／SM 是另一個運動：把藝人當全球 IP、把巡演當主業、把粉籍當基礎設施。"
            "華研若用他們的營收成長率當 KPI，一定輸；若用「每單位資本創造的自由現金流與配息」當 KPI，華研其實很強。"
            "全球競爭力結論：在華語錄音權利這層，華研是有座位的供應商；在全球娛樂工業這層，它是利基玩家。"
            "未來五年要「提高全球競爭力」，現實路徑不是打進 Billboard 主流，而是（1）守住並重訂中國／華語串流費率、"
            "（2）把巡演做成可預測的雙年週期、（3）讓 1–2 組 25 歲世代藝人產生可輸出的現場需求、"
            "（4）增加東南亞華語與日韓翻唱／同步的授權表面積。",
        )
    )

    story.append(_p(ss, "八、2026–2030 情景（self-reported，非財測）", "H1"))
    story.append(
        _p(
            ss,
            "公司未出具公開財務預測。以下三情景是依歷史週期、2026 已見巡演與預收款、以及產業量級做的研究假設，"
            "用來框「什麼叫超預期／低於預期」，不是目標價或保證。",
        )
    )
    story.append(
        _grid(
            ss,
            ["情景", "關鍵假設", "營收帶（億）", "EPS 帶（元）", "辨認訊號"],
            [
                [
                    "基準",
                    "每 2 年一輪頭部巡演；授權隨中國串流中速成長；無新的一代頭牌",
                    "11–15",
                    "8–12",
                    "預收款隨巡演年在 3–5 億間擺動；授權年增高個位數",
                ],
                [
                    "樂觀",
                    "兩組以上可同時巡演；中國費率或範圍上修；1 組新人形成票房",
                    "15–20 高峰年",
                    "12–15",
                    "授權絕對額穩定＞7 億；新人單年演藝貢獻可見",
                ],
                [
                    "保守",
                    "中國授權壓力、頭牌老化、無新人接棒；現場審批干擾",
                    "9–12",
                    "6–9",
                    "授權連續衰退；預收款不再回升；配息被迫下修",
                ],
            ],
            col_widths=[22 * mm, 48 * mm, 28 * mm, 28 * mm, 52 * mm],
        )
    )
    story.append(_p(ss, "表 6　五年情景箱。數字為研究區間，不是公司指引。", "Caption"))
    story.append(
        _p(
            ss,
            "2026 年本身較接近「基準偏樂觀的巡演年」：H1 本業已年增、H2 場次指引約 20 場、預收款 4.08 億。"
            "若下半年執行順利，全年營收有機會重新靠近 2023–2024 的 12–14 億帶，EPS 則因少了 2025 業外，"
            "未必再見到 11 元——這是健康的（本業質量上升、一次性下降）。"
            "2027–2028 若重複 2025 那種準備年，營收回落不應自動解讀為衰退故事，要看授權絕對額是否守住。"
            "2030 年的分水嶺：曲庫是否仍被年輕聽眾與短影音使用，以及公司是否還能賣出「下一張小巨蛋」。",
        )
    )

    story.append(_p(ss, "九、風險", "H1"))
    bullets = [
        "藝人集中：動力火車與林宥嘉同時失速或不再巡演，演藝營收會立刻回到 2025 型空窗，且更難靠業外補。",
        "中國平台與政策：外銷 82% 背後是大中華授權與巡演。費率重談、內容審批、場館總量或外匯，都會直接打到現金流。",
        "把業外當本業：2025 淨利率 50% 含金融資產利益，2026 起不應再當常態。",
        "曲庫老化：經典歌有長尾，但短影音世代若不持續注入新作，授權成長會趨近市場費率而非量的擴張。",
        "AI 與串流詐欺：污染推薦池、稀釋每曲單價；權利人舉證成本上升。",
        "高配息的機會成本：配發率約 70–85%，戰術上很股東友好，戰略上若要買粉籍平台、海外場館權益或大型經紀，現金緩衝比看起來薄。",
        "治理與關鍵人：文創公司對製作、經紀關係與授權合約的關鍵人依賴高，這在財報附註裡不會完全顯現。",
        "流動性：日成交張數偏低，價格對消息與除息的敏感度高於大型權值股。",
    ]
    for b in bullets:
        story.append(Paragraph(f"• {b}", ss["BulletBody"]))
        story.append(Spacer(1, 1.2 * mm))

    story.append(_p(ss, "十、結論", "H1"))
    story.append(
        _callout(
            ss,
            "華研近五年證明了三件事：曲庫能在沒有現場時養活高 EPS；現場回來時營收可以一年加三成；"
            "管理層選擇把超額現金還債再配息，而不是盲目做大。"
            "未來五年產業風向（全球串流、中國市場升級、現場超粉）對「權利人」有利，對「沒有全球粉絲基礎設施的華語廠牌」只是中性偏多。"
            "它最可能繼續當一家高殖利率、高 ROE、營收會隨巡演心跳的精品音樂公司。"
            "全球競爭力的誠實位置：華語曲庫第一梯隊供應商，不是 HYBE 的台灣版。"
            "若五年後要改寫這句話，證據必須是：授權絕對額創新高、且頭部巡演不再只有兩組名字。",
        )
    )

    story.append(_p(ss, "附錄 A｜資料來源與方法", "H1"))
    story.append(
        _p(
            ss,
            "本報告所有歷史財務數字來自已公開來源的交叉核對，未呼叫 FinMind／FRED 即時 API，亦未使用未公開內線。"
            "損益 2023–2025 與華研年報／營業報告書核對（2024 營收 1,375,487 千元、2025 營收 1,084,714 千元、EPS 11.44／10.30）。"
            "2021–2022 及各季數列取公開季報彙整（HiStock 損益表／利潤比率、ifa.ai、stockanalysis.com）。"
            "資產負債與現金流取 stockanalysis 彙編之合併年報數列（單位百萬，四捨五入）。"
            "股利取財報狗／現金流量表交叉（2021–2026 現金股利 3.5／4.5／5.0／6.0／8.0／8.0 元）。"
            "產業：IFPI Global Music Report 2026；HYBE／JYP 2025 年報與法說；MoneyDJ 公司條目（2024 產品與地區占比）。"
            "股價為 2026-08-27 收盤 85.20 元。前景與競爭力評級為撰寫者 self-reported 分析，不是公司指引，也不是投資建議。",
            "Disclaimer",
        )
    )
    story.append(_p(ss, "附錄 B｜2026 年作品與巡演（公司已公開）", "H2"))
    story.append(
        _p(
            ss,
            "動力火車《一路向前》世界巡迴（台北小巨蛋 5/15–17 售罄）；林宥嘉《超級管家》世界巡迴（2026/6/27 廣州起）。"
            "新作含動力火車〈I Need You〉、曾沛慈〈孤單心事〉（音樂產房計畫）、鄭馥儀校園三部曲、babyMINT〈WIL：D〉、"
            "郁可唯電影宣傳曲〈一覺醒來〉、李友廷影集片尾曲〈未完成的歌〉。第 20 屆全球網路詞曲創作大賽擴大舉辦。",
            "Disclaimer",
        )
    )
    return story


def main() -> int:
    _setup_fonts()
    charts = _save_charts()
    ss = _styles()
    out_pdf = ROOT / "華研8446_近五年財務與未來五年前景_20260827.pdf"
    # also ASCII copy for tooling
    out_ascii = ROOT / "HIM_8446_5y_finance_outlook_20260827.pdf"

    def first_page(c, d):
        _cover_page(c, d)

    def later(c, d):
        _header_footer(c, d)

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=16 * mm,
        title="華研國際音樂（8446）近五年財務分析與未來五年前景",
        author="Research compilation 2026-08-27",
        subject="HIM 8446 financial analysis",
    )
    story = build_story(ss, charts)
    doc.build(story, onFirstPage=first_page, onLaterPages=later)

    # duplicate ascii-named file
    out_ascii.write_bytes(out_pdf.read_bytes())
    print(f"PDF_PAGES_WRITTEN {out_pdf}")
    print(f"PDF_ASCII {out_ascii}")
    print(f"SIZE {out_pdf.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
