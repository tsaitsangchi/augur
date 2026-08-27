#!/usr/bin/env python3
"""產生 3596 智易近五年財務＋未來五年前景 PDF。

資料僅來自公開財報／年報／重大訊息與公開產業研究，零 FinMind／FRED API。
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
OUT_DIR = ROOT.parent
PDF_NAME = "arcadyan_3596_5yr_financial_outlook_20260827.pdf"
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
NAVY = colors.HexColor("#0F2C4C")
TEAL = colors.HexColor("#1A6B7A")
GOLD = colors.HexColor("#C4A35A")
LIGHT = colors.HexColor("#F4F1EA")
ROW_ALT = colors.HexColor("#EEF3F6")
RED = colors.HexColor("#8B2E2E")
GREEN = colors.HexColor("#1F6B4A")

# 單位：新台幣百萬元（由千元／四捨五入至百萬）；比率為 %
# 來源見報告末「資料來源與方法」
YEARS = ["2021", "2022", "2023", "2024", "2025"]
REV = [38240, 47168, 51158, 48967, 52976]
GP = [5310, 6586, 7385, 7416, 8086]
OP = [2199, 2200, 3164, 3038, 3500]
PARENT_NI = [1788, 2013, 2421, 2486, 2777]
CONSOL_NI = [1702, 1915, 2390, 2480, 2774]
EPS = [8.60, 9.20, 10.98, 11.28, 12.60]
GPM = [13.9, 14.0, 14.4, 15.1, 15.3]
OPM = [5.8, 4.7, 6.2, 6.2, 6.6]
NPM = [4.5, 4.1, 4.7, 5.1, 5.2]
ASSETS = [33901, 40021, 38549, 39307, 44811]
LIAB = [20978, 26081, 23649, 23280, 27778]
EQUITY = [12923, 13939, 14900, 16027, 17033]
DEBT_RATIO = [61.9, 65.2, 61.3, 59.2, 62.0]
ROE = [13.8, 14.4, 16.4, 16.0, 16.4]
ROA = [5.0, 4.8, 6.2, 6.5, 6.2]
RD = [1939, None, 2887, 2742, 3013]
OCF = [None, None, 5590, 8769, 3735]
CAPEX = [None, None, 1240, 993, 716]

# 文泉驛含 CJK 與 ASCII；Droid Fallback 缺數字／英文字形。
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "DejaVu Sans", "Droid Sans Fallback"]
plt.rcParams["axes.unicode_minus"] = False
from matplotlib import font_manager as _fm

_fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
_WQY = _fm.FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
plt.rcParams["font.sans-serif"] = [_WQY.get_name(), "DejaVu Sans"]


def _chart(path: Path, fig) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_charts(tmp: Path) -> dict[str, Path]:
    tmp.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = range(len(YEARS))
    w = 0.35
    b1 = ax.bar([i - w / 2 for i in x], [v / 1000 for v in REV], w, color="#1A6B7A", label="營收（十億）")
    b2 = ax.bar([i + w / 2 for i in x], [v / 1000 for v in PARENT_NI], w, color="#C4A35A", label="母公司淨利（十億）")
    ax.set_xticks(list(x), YEARS)
    ax.set_ylabel("新台幣十億元")
    ax.set_title("智易 3596｜合併營收與歸屬母公司淨利（2021–2025）")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for b, v in zip(b1, REV):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.4, f"{v/1000:.1f}", ha="center", fontsize=8)
    out["rev"] = _chart(tmp / "rev.png", fig)

    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    ax.plot(YEARS, GPM, "o-", color="#1A6B7A", lw=2.2, label="毛利率")
    ax.plot(YEARS, OPM, "s-", color="#0F2C4C", lw=2.2, label="營業利益率")
    ax.plot(YEARS, NPM, "^-", color="#C4A35A", lw=2.2, label="合併淨利率")
    ax.set_ylabel("%")
    ax.set_title("獲利率走勢（2021–2025）")
    ax.legend(frameon=False, ncol=3)
    ax.set_ylim(0, 18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    out["margin"] = _chart(tmp / "margin.png", fig)

    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    ax.plot(YEARS, ROE, "o-", color="#1A6B7A", lw=2.2, label="ROE（期末權益）")
    ax.plot(YEARS, ROA, "s-", color="#8B2E2E", lw=2.2, label="ROA（合併淨利／期末資產）")
    ax.plot(YEARS, DEBT_RATIO, "^--", color="#888888", lw=1.6, label="負債比率")
    ax.set_ylabel("%")
    ax.set_title("報酬與槓桿（2021–2025）")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    out["roe"] = _chart(tmp / "roe.png", fig)

    # product mix 2023-2025
    labels = ["智慧家庭", "行動通訊", "寬頻固網", "其他"]
    mix = {
        "2023": [17578, 16967, 15157, 1455],
        "2024": [22499, 16128, 8919, 1422],
        "2025": [19745, 16374, 15241, 1616],
    }
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    import numpy as np

    xx = np.arange(3)
    w = 0.2
    cols = ["#0F2C4C", "#1A6B7A", "#C4A35A", "#A3B4C2"]
    for i, lab in enumerate(labels):
        vals = [mix[y][i] / 1000 for y in ["2023", "2024", "2025"]]
        ax.bar(xx + (i - 1.5) * w, vals, w, label=lab, color=cols[i])
    ax.set_xticks(xx, ["2023", "2024", "2025"])
    ax.set_ylabel("新台幣十億元")
    ax.set_title("產品組合（合併營收細分）")
    ax.legend(frameon=False, ncol=4, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    out["product"] = _chart(tmp / "product.png", fig)

    geo_labels = ["美洲", "歐洲", "亞洲及其他"]
    geo = {
        "2023": [22331, 17432, 11395],
        "2024": [21067, 13155, 14746],
        "2025": [25308, 17750, 9918],
    }
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    bottom = np.zeros(3)
    gcols = ["#1A6B7A", "#0F2C4C", "#C4A35A"]
    for i, lab in enumerate(geo_labels):
        vals = np.array([geo[y][i] / 1000 for y in ["2023", "2024", "2025"]])
        ax.bar(["2023", "2024", "2025"], vals, bottom=bottom, label=lab, color=gcols[i])
        bottom += vals
    ax.set_ylabel("新台幣十億元")
    ax.set_title("地區別營收（依客戶所在地）")
    ax.legend(frameon=False, ncol=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    out["geo"] = _chart(tmp / "geo.png", fig)

    # 5-year scenario (illustrative, not a price target)
    fig, ax = plt.subplots(figsize=(8.2, 3.5))
    yrs = [2025, 2026, 2027, 2028, 2029, 2030]
    base = [53.0, 54.5, 56.5, 59.0, 61.5, 64.0]
    bull = [53.0, 57.0, 62.0, 68.0, 74.0, 80.0]
    bear = [53.0, 51.0, 50.0, 51.5, 53.0, 54.5]
    ax.fill_between(yrs, bear, bull, color="#1A6B7A", alpha=0.12)
    ax.plot(yrs, base, "o-", color="#1A6B7A", lw=2.2, label="基準（約 CAGR 4%）")
    ax.plot(yrs, bull, "s--", color="#1F6B4A", lw=1.8, label="樂觀（約 CAGR 8.5%）")
    ax.plot(yrs, bear, "^--", color="#8B2E2E", lw=1.8, label="保守（約 CAGR 0.5%）")
    ax.set_ylabel("合併營收（十億元）")
    ax.set_title("2026–2030 營收情境帶（示意，非公司財測）")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    out["scenario"] = _chart(tmp / "scenario.png", fig)
    return out


def register_font() -> str:
    # TTC：0＝比例、1＝等寬；兩者皆含 ASCII＋CJK
    pdfmetrics.registerFont(TTFont("CJK", FONT, subfontIndex=0))
    return "CJK"


def styles(font: str) -> dict:
    ss = getSampleStyleSheet()
    s = {}
    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker", fontName=font, fontSize=11, textColor=GOLD, alignment=TA_LEFT, spaceAfter=6, tracking=1
    )
    s["cover_title"] = ParagraphStyle(
        "cover_title", fontName=font, fontSize=26, leading=34, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub", fontName=font, fontSize=13, leading=20, textColor=TEAL, alignment=TA_LEFT, spaceAfter=4
    )
    s["h1"] = ParagraphStyle(
        "h1", fontName=font, fontSize=16, leading=22, textColor=NAVY, spaceBefore=14, spaceAfter=8, borderPadding=3
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName=font, fontSize=12.5, leading=18, textColor=TEAL, spaceBefore=10, spaceAfter=6
    )
    s["body"] = ParagraphStyle(
        "body", fontName=font, fontSize=9.5, leading=15.5, textColor=colors.HexColor("#1C2430"), alignment=TA_JUSTIFY, spaceAfter=7
    )
    s["small"] = ParagraphStyle(
        "small", fontName=font, fontSize=8, leading=12, textColor=colors.HexColor("#4A5560"), alignment=TA_LEFT, spaceAfter=4
    )
    s["caption"] = ParagraphStyle(
        "caption", fontName=font, fontSize=8, leading=11, textColor=colors.HexColor("#5A6570"), alignment=TA_CENTER, spaceBefore=2, spaceAfter=10
    )
    s["th"] = ParagraphStyle("th", fontName=font, fontSize=7.5, leading=10.5, textColor=colors.white, alignment=TA_CENTER)
    s["td"] = ParagraphStyle("td", fontName=font, fontSize=7.8, leading=11, textColor=NAVY, alignment=TA_CENTER)
    s["tdl"] = ParagraphStyle("tdl", fontName=font, fontSize=7.8, leading=11, textColor=NAVY, alignment=TA_LEFT)
    s["quote"] = ParagraphStyle(
        "quote", fontName=font, fontSize=9.5, leading=15, textColor=NAVY, leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=8, backColor=LIGHT
    )
    s["footer"] = ParagraphStyle("footer", fontName=font, fontSize=7.5, textColor=colors.HexColor("#6A7380"), alignment=TA_CENTER)
    return s


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, A4[1] - 12.8 * mm, A4[0], 1.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("CJK", 8)
    canvas.drawString(16 * mm, A4[1] - 8 * mm, "智易科技（3596.TW）｜近五年財務分析與未來五年前景／全球競爭力")
    canvas.drawRightString(A4[0] - 16 * mm, A4[1] - 8 * mm, "公開資訊彙編｜2026-08-27")
    canvas.setFillColor(LIGHT)
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#6A7380"))
    canvas.setFont("CJK", 7.5)
    canvas.drawString(16 * mm, 4 * mm, "非投資建議。數字可溯至公司合併財務報告／年報／重大訊息。")
    canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def p(text: str, st) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), st)


def table(headers, rows, col_w, st, header_color=NAVY):
    data = [[Paragraph(str(h), st["th"]) for h in headers]]
    for r in rows:
        line = []
        for i, c in enumerate(r):
            sty = st["tdl"] if i == 0 else st["td"]
            line.append(Paragraph(str(c), sty))
        data.append(line)
    t = Table(data, colWidths=col_w, repeatRows=1)
    cmd = [
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "CJK"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D7DE")),
        ("BACKGROUND", (0, 1), (-1, 1), ROW_ALT),
    ]
    for i in range(2, len(data)):
        if i % 2 == 1:
            cmd.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        else:
            cmd.append(("BACKGROUND", (0, i), (-1, i), colors.white))
    t.setStyle(TableStyle(cmd))
    return t


def img(path: Path, width=178 * mm):
    from PIL import Image as PILImage

    with PILImage.open(path) as im:
        w, h = im.size
    height = width * h / w
    return Image(str(path), width=width, height=height)


def build(pdf_path: Path) -> Path:
    font = register_font()
    st = styles(font)
    charts = make_charts(ROOT / "_charts")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=14 * mm,
        title="智易科技（3596）近五年財務分析與未來五年前景、全球競爭力報告",
        author="公開資訊彙編（非投資建議）",
        subject="Arcadyan 3596 five-year financial and outlook report",
    )
    story = []

    # COVER
    story.append(Spacer(1, 18 * mm))
    story.append(p("ARCADYAN TECHNOLOGY　股票代號 3596.TW", st["cover_kicker"]))
    story.append(p("智易科技股份有限公司<br/>近五年財務分析報告", st["cover_title"]))
    story.append(p("暨公司／產業未來五年前景與全球競爭力評估", st["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    meta = Table(
        [
            [p("報告日", st["small"]), p("2026 年 8 月 27 日", st["body"])],
            [p("分析期間", st["small"]), p("財務：2021–2025 全年；近況補 2026 上半年與 1–7 月營收", st["body"])],
            [p("展望期間", st["small"]), p("2026–2030（情境分析，非公司正式財測）", st["body"])],
            [p("主資料", st["small"]), p("公司合併財務報告、113 年年報、2026/8/5 重大訊息、公開產業研究", st["body"])],
            [p("性質", st["small"]), p("公開資訊彙編與結構解讀。非投資建議、非目標價、非下單訊號。", st["body"])],
        ],
        colWidths=[28 * mm, 150 * mm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BOX", (0, 0), (-1, -1), 0.4, GOLD),
            ]
        )
    )
    story.append(meta)
    story.append(Spacer(1, 8 * mm))
    story.append(
        p(
            "一句話：智易是仁寶集團網通 ODM／JDM，核心在電信與有線電視業者的 CPE（閘道器、FWA、PON、Cable Modem、Wi-Fi）。"
            "近五年營收自約 382 億走到 530 億，EPS 自 8.60 元走到 12.60 元；毛利率由約 14% 緩升至 15% 以上。"
            "未來五年產業主軸是 Wi-Fi 7 滲透、5G FWA、光纖／DOCSIS 4.0 升級與電信軟體平台客製，而非消費零售品牌戰。"
            "全球競爭力來自電信認證門檻、晶片 Early Access、越南製造與產品／地區分散；主要風險是客戶集中、Smart Home 下滑、關稅與地緣、以及 ODM 價格戰。",
            st["body"],
        )
    )
    story.append(PageBreak())

    # 1 摘要
    story.append(p("一、執行摘要", st["h1"]))
    story.append(
        p(
            "本報告只使用已公開、可回溯的來源：智易官網投資人專區之合併財務報告與年報、公開資訊觀測站重大訊息、"
            "以及 Counterpoint、Dell’Oro（經 RCR Wireless 轉述）、NETGEAR 10-K 等同業／產業公開文件。"
            "本環境未連上 augur 本地資料庫，亦未呼叫 FinMind／FRED。所有金額除另註外為合併報表、新台幣。",
            st["body"],
        )
    )
    story.append(p("1.1 近五年財務結論", st["h2"]))
    bullets = [
        "規模：合併營收 2021 年 382.40 億 → 2025 年 529.76 億，四年 CAGR 約 8.5%。中間 2024 年因庫存與客戶需求年減 4.3%，2025 年以寬頻固網回升年增 8.2% 再創新高。",
        "獲利：歸屬母公司淨利 17.88 億 → 27.77 億；基本 EPS 8.60 → 12.60 元。毛利率 13.9% → 15.3%，顯示產品組合與成本控管優於單純「做大營收」。",
        "現金與槓桿：幾乎無長期借款（2025 年底長期借款為 0）。2024 年營業現金流 87.7 億特別強；2025 年因應收與存貨上升，OCF 降至 37.3 億，但仍覆蓋資本支出與股利。",
        "股東回饋：113 年度現金（盈餘 6.5 元＋資本公積 1.0 元）合計約 16.53 億；114 年度董事會擬配發每股現金股利 8.0 元（約 17.63 億）。公司章程現金股利不低於總股利 10%，盈餘分派不低於稅後淨利 30%。",
        "2026 上半年：合併營收 266.66 億、毛利 40.45 億（15.17%）、營業利益 17.51 億、稅後 14.32 億、EPS 6.50 元，上半年 EPS 為公司歷史新高。7 月營收 48.47 億，1–7 月 315.13 億、年增 2.8%。",
    ]
    for b in bullets:
        story.append(p("• " + b, st["body"]))

    story.append(p("1.2 前景與競爭力結論（2026–2030）", st["h2"]))
    bullets = [
        "產業：寬頻 CPE 進入「換機週期重疊」——Wi-Fi 7 在電信通道的滲透、5G FWA 續增、北美 Cable DOCSIS 4.0／DAA、光纖 XGS-PON。Dell’Oro 對整體寬頻設備 2025–2030 的量成長並不激進（轉述約 0.3% CAGR），成長來自單價與規格升級，而非出貨暴衝。",
        "公司結構優勢：產品（智慧家庭／行動通訊／寬頻固網）與地區（美／歐／亞）同時分散，單一 Cable 或單一洲的週期較不易把整家公司打穿——這也是 2025 年智易穩、中磊弱、2026 上半年走勢又對調的原因。",
        "真正的五年題：不是「網通會不會成長」，而是 Smart Home 何時止跌、Wi-Fi 7／FWA／PON 能否把 ASP 與毛利再往上、越南產能與關稅配置能否守住北美電信訂單。",
        "全球位置：電信 ODM 第一線（NETGEAR 10-K 將 Arcadyan 列為服務供應商市場競爭者；公開測速資料曾指智易為 Verizon 主要供應、美國路由器市占前列）。對手是中磊、啟碁、Sagemcom、Vantiva、Sercomm、Hitron、華為／中興（受限制市場）與品牌端 NETGEAR／TP-Link／eero。智易的護城河是認證＋軟體客製＋JDM，不是消費品牌。",
        "基準情境：2026–2030 營收低至中個位數年增、毛利率守在 15% 附近、EPS 隨配息與股本穩定緩步向上。樂觀要看 Smart Home 回升＋北美／歐洲電信大升級疊加；悲觀是電信 capex 再遞延、關稅侵蝕、或前兩大客戶同時掉單。",
    ]
    for b in bullets:
        story.append(p("• " + b, st["body"]))

    # 2 公司
    story.append(p("二、公司定位與商業模式", st["h1"]))
    story.append(
        p(
            "智易科技（Arcadyan Technology Corporation）2003 年設立，總部位於新竹，股票代號 3596。"
            "最終母公司為仁寶電腦，集團持股約 33%。合併主業為寬頻接取、無線區域網路、數位家庭多媒體、行動寬頻與無線影音產品之研發、產製與銷售。"
            "客戶以全球電信營運商、MSO（有線電視多系統營運商）與網通品牌為主，採 ODM／JDM：從規格、軟體平台到製造一條龍，強調客製化而非純代工組裝。",
            st["body"],
        )
    )
    story.append(
        p(
            "產品地圖（113 年年報）：5G FWA CPE、Wi-Fi Mesh／Wi-Fi 7 閘道與企業 AP、VDSL／G.fast、GPON／XGS-PON／NG-PON2、DOCSIS 3.1／4.0 Cable Modem、Android TV OTT／IP STB、Edge AI Box、LTE／小基站、車用 76–80GHz BSD 雷達與整合天線防盜器。"
            "軟體側參與 RDK、EasyMesh、開放軟體平台，這是電信標案裡「進得去、待得住」的條件。",
            st["body"],
        )
    )
    story.append(
        p(
            "製造：越南為主要非流動資產所在地（2025 年底越南非流動資產 31.16 億、台灣 28.27 億）。年報載明擴大越南智動化／關燈工廠、RBA VAP 白金級，並與各地代工夥伴組成多地製造，回應美中關稅與供應鏈重組。研發人員約 780 人量級，研發費用率約 5.6–5.7%。",
            st["body"],
        )
    )

    # 3 財務
    story.append(p("三、近五年財務績效（2021–2025）", st["h1"]))
    story.append(p("3.1 規模與獲利總表", st["h2"]))
    story.append(
        p(
            "下表以合併財務報告為準。營收、毛利、營業利益、淨利單位為新台幣百萬元（由千元四捨五入）。"
            "2022 年營業利益採四季已公告合併綜合損益表加總（全年報表該列於 PDF 文字抽取未完整取得，故加註）。"
            "淨利率以合併本期淨利／營收；ROE 以歸屬母公司淨利／期末權益總額（含非控制權益之權益總額，2024、2025 與公司年報揭露之 16.0% 接近）。",
            st["small"],
        )
    )
    headers = ["項目", "2021", "2022", "2023", "2024", "2025"]
    rows = [
        ["合併營收", "38,240", "47,168", "51,158", "48,967", "52,976"],
        ["年增率", "—", "+23.3%", "+8.5%", "−4.3%", "+8.2%"],
        ["營業毛利", "5,310", "6,586", "7,385", "7,416", "8,086"],
        ["毛利率", "13.9%", "14.0%", "14.4%", "15.1%", "15.3%"],
        ["營業利益", "2,199", "2,200*", "3,164", "3,038", "3,500"],
        ["營業利益率", "5.8%", "4.7%*", "6.2%", "6.2%", "6.6%"],
        ["合併本期淨利", "1,702", "1,915†", "2,390", "2,480", "2,774"],
        ["歸屬母公司淨利", "1,788", "2,013", "2,421", "2,486", "2,777"],
        ["基本 EPS（元）", "8.60", "9.20", "10.98", "11.28", "12.60"],
        ["研發費用", "1,939", "—", "2,887", "2,742", "3,013"],
        ["研發／營收", "5.1%", "—", "5.6%", "5.6%", "5.7%"],
    ]
    story.append(table(headers, rows, [32 * mm] + [29 * mm] * 5, st))
    story.append(p("*2022 營業利益：四季合併綜合損益表加總。†2022 合併淨利：四季加總；歸屬母公司淨利 2,013 百萬為全年報表附註。單位：新台幣百萬元。", st["caption"]))
    story.append(img(charts["rev"]))
    story.append(p("圖 1　合併營收與歸屬母公司淨利", st["caption"]))
    story.append(img(charts["margin"]))
    story.append(p("圖 2　毛利率／營業利益率／淨利率", st["caption"]))

    story.append(p("3.2 怎麼讀這五年", st["h2"]))
    story.append(
        p(
            "2021–2022 是疫情後寬頻與 5G FWA 放量。營收從 382 億跳到 472 億（+23%），但營業利益幾乎持平、利益率被稀釋到約 4.7%——"
            "典型「出貨很好、組合與費用還沒跟上」的一年。行動通訊產品從 2021 年 19.1 億暴增到 2022 年 159.5 億，是結構轉變的主軸；智慧家庭則從 227 億降到 166 億。",
            st["body"],
        )
    )
    story.append(
        p(
            "2023 是高峰年：營收 511.6 億、營業利益 31.6 億、EPS 10.98 元。美洲 223.3 億成為最大區域。公司開始把毛利率從 14% 往上推。",
            st["body"],
        )
    )
    story.append(
        p(
            "2024 是庫存年：營收年減 4.3% 至 489.7 億，但毛利率升至 15.1%、EPS 仍升至 11.28 元，營業現金流 87.7 億為五年最強。"
            "年報自述：台灣通訊產值 113 年預估年減 2.4%，公司出貨約當台灣網通市場 4%。產品上，智慧家庭升至 225.0 億，寬頻固網掉到 89.2 億——Cable／固網客戶調整庫存的痕跡很清楚。"
            "前十大客戶結構劇烈切換：甲客戶從 2023 年 5.9% 升至 2024 年 15.8%（77.4 億），丙客戶從 17.3% 掉到 4.2%。這解釋了為什麼電信 ODM 的「大客戶輪動」可以在營收持平下仍改善毛利。",
            st["body"],
        )
    )
    story.append(
        p(
            "2025 是寬頻回來的一年：營收 529.8 億（+8.2%）創新高，毛利 80.9 億、營業利益 35.0 億、EPS 12.60 元。寬頻固網自 89.2 億回升到 152.4 億（+71%），智慧家庭回落到 197.5 億。"
            "地區上美洲 253.1 億（47.8%）、歐洲 177.5 億（33.5%）、亞洲及其他 99.2 億（18.7%）——亞洲明顯收縮、歐美上升。"
            "客戶：丑客戶 70.4 億、乙客戶 69.4 億（皆逾 10%），甲客戶從 77.4 億掉到 9.2 億。集中度仍高，但「誰是第一大」一年可以換人。",
            st["body"],
        )
    )

    story.append(p("3.3 資產負債與現金流", st["h2"]))
    story.append(img(charts["roe"]))
    story.append(p("圖 3　ROE／ROA／負債比率", st["caption"]))
    rows = [
        ["資產總計", "33,901", "40,021", "38,549", "39,307", "44,811"],
        ["負債總計", "20,978", "26,081", "23,649", "23,280", "27,778"],
        ["權益總計", "12,923", "13,939", "14,900", "16,027", "17,033"],
        ["負債比率", "61.9%", "65.2%", "61.3%", "59.2%", "62.0%"],
        ["流動比（若揭露）", "—", "—", "134%", "137%", "136%"],
        ["ROE", "13.8%", "14.4%", "16.4%", "16.0%", "16.4%"],
        ["ROA", "5.0%", "4.8%", "6.2%", "6.5%", "6.2%"],
        ["營業現金流", "—", "—", "5,590", "8,769", "3,735"],
        ["購置不動產廠房設備", "—", "—", "1,240", "993", "716"],
        ["現金股利（含資本公積分派）", "—", "—", "—", "1,653", "1,763（擬）"],
    ]
    story.append(table(headers, rows, [42 * mm] + [27 * mm] * 5, st))
    story.append(p("單位：新台幣百萬元。2024 流動比、ROA、ROE 取自 113 年年報董事會報告（137%、6.5%、16.0%）。2025 流動比＝流動資產／流動負債。", st["caption"]))
    story.append(
        p(
            "財務結構可稱穩健：2025 年底短期借款僅 1.85 億（2024 年底 11.8 億），長期借款為 0。"
            "現金及約當現金從 81.6 億降到 46.9 億，但「按攤銷後成本衡量之金融資產－流動」（定期存款性質）從 51.0 億升到 89.2 億，兩者合計約 136 億，與前一年約 133 億相當——是分類移動，不是現金蒸發。"
            "真正要盯的是營運資金：存貨 111.4 → 145.2 億、應收 52.5 → 81.7 億，這把 2025 年 OCF 從 87.7 億壓到 37.3 億。"
            "同時合約負債 20.7 → 31.8 億，代表客戶預付款增加，不全是壞的「壓貨」。2026 年中資產進一步擴到 542.1 億、負債 376.7 億，屬旺季備料與應收膨脹，須看下半年能否轉成現金。",
            st["body"],
        )
    )

    story.append(p("3.4 產品與地區結構", st["h2"]))
    story.append(img(charts["product"]))
    story.append(p("圖 4　產品組合（智慧家庭／行動通訊／寬頻固網）", st["caption"]))
    story.append(img(charts["geo"]))
    story.append(p("圖 5　地區別營收", st["caption"]))
    rows = [
        ["智慧家庭", "226.9", "166.3", "175.8", "225.0", "197.5"],
        ["行動通訊（含 FWA 等）", "19.1", "159.5", "169.7", "161.3", "163.7"],
        ["寬頻固網", "126.6", "132.3", "151.6", "89.2", "152.4"],
        ["其他", "9.8", "13.6", "14.6", "14.2", "16.2"],
        ["美洲", "98.95", "185.3", "223.3", "210.7", "253.1"],
        ["歐洲", "202.7", "181.5", "174.3", "131.6", "177.5"],
        ["亞洲及其他", "80.8", "104.8", "113.9", "147.5", "99.2"],
    ]
    story.append(table(["（十億元）"] + YEARS, rows, [38 * mm] + [28 * mm] * 5, st))
    story.append(p("2021–2022 取自 2022 年合併財報附註「客戶合約之收入」；2023–2025 取自 2024、2025 年合併財報同附註。", st["caption"]))
    story.append(
        p(
            "結構解讀：智易不是「單一產品押注」。2022 年靠行動通訊（FWA 爆發）補智慧家庭下滑；2024 年靠智慧家庭補寬頻固網庫存；2025 年靠寬頻固網補智慧家庭。"
            "2026 上半年公開產業追蹤指出：美洲年增約 27%、行動通訊約 +28%、寬頻約 +16%，但智慧家庭約 −27%、亞洲約 −46%，互相抵銷後整體只剩低個位數成長。"
            "因此未來五年若只看「FWA 很好」會誤判；總成長的鑰匙在智慧家庭是否止跌。",
            st["body"],
        )
    )

    story.append(p("3.5 2026 年截至最新公告", st["h2"]))
    rows = [
        ["合併營收", "26,666", "26,165", "+1.9%"],
        ["營業毛利", "4,045", "3,980", "+1.6%"],
        ["毛利率", "15.17%", "15.21%", "約持平"],
        ["營業利益", "1,751", "—", "—"],
        ["稅前淨利", "1,883", "1,780", "+5.8%"],
        ["本期淨利", "1,432", "1,339", "+6.9%"],
        ["基本 EPS（元）", "6.50", "6.10", "+0.40 元"],
        ["期末資產", "54,211", "—", "—"],
        ["期末負債", "37,667", "—", "—"],
        ["母公司業主權益", "16,456", "—", "—"],
    ]
    story.append(
        table(
            ["2026 H1（百萬）", "本期", "去年同期", "變化"],
            rows,
            [42 * mm, 38 * mm, 38 * mm, 50 * mm],
            st,
        )
    )
    story.append(p("來源：公開資訊觀測站 2026/8/5「115 年第二季合併財務報告」重大訊息；損益同比取自同日綜合損益表新聞稿。", st["caption"]))
    story.append(
        p(
            "單季：Q2 營收 138.82 億、毛利率 15.18%、稅後 7.43 億、EPS 3.38 元（歷年同期新高、歷史次高）。"
            "公司自評「產品組合優化及成本控管」，對全年審慎樂觀，並稱將加大研發。"
            "7 月營收 48.47 億（歷史次高，月增 2.3%、年增 7.7%），1–7 月 315.13 億、年增 2.8%。"
            "若單純把上半年年化，全年營收約在 530–550 億區間，接近 2025 年水準再微增——與「低個位數成長」敘事一致，尚未看到加速年。",
            st["body"],
        )
    )

    # 4 產業
    story.append(p("四、產業未來五年前景（2026–2030）", st["h1"]))
    story.append(p("4.1 產業地圖", st["h2"]))
    story.append(
        p(
            "智易所在的是「服務供應商通道的寬頻 CPE／閘道器」：電信與有線電視把盒子放到用戶家裡，賺的是標案、認證、軟體客製與多年換機，不是屈臣氏貨架上的消費路由器。"
            "上游是 Qualcomm、Broadcom、MediaTek 等晶片；中游是智易、中磊、啟碁、Sagemcom、Vantiva、Hitron 等 ODM／OEM；下游是 Verizon、Comcast、Charter、歐亞電信與品牌商。"
            "年報把產業驅動寫成五條：5G／6G、邊緣與雲、AI 維運、資安、綠色通訊。對智易現金流真正有感的，是其中會變成「家裡那一台盒子要換」的部分。",
            st["body"],
        )
    )
    story.append(p("4.2 四條換機曲線", st["h2"]))
    story.append(
        p(
            "（1）Wi-Fi 7：Counterpoint（2025 研究）預估，到 2030 年電信通道全球寬頻 CPE 出貨將有 54% 支援 Wi-Fi 7。"
            "2025 年終端（手機／筆電／平板）已開始帶 Wi-Fi 7，電信端會落後 1–3 年才大規模換閘道——這正是 2026–2029 的主航道。"
            "Dell’Oro 轉述：2025 年消費 Wi-Fi 7 路由器出貨年增 211%（亞洲低價機帶量），但電信商策略分歧：有的兩盒（獨立 Modem＋Wi-Fi 7 路由器），有的一盒整合；部分業者甚至故意等 Wi-Fi 8 而不把 Wi-Fi 7 一次換滿。"
            "對智易：Wi-Fi 7 IAD、EasyMesh R5、RDK-based Wi-Fi 7、企業 AP 已在 113 年年報列為開發完成項目，屬於「規格已備妥、看電信時程」的狀態。",
            st["body"],
        )
    )
    story.append(
        p(
            "（2）5G FWA：固定無線接取是 2022 年智易行動通訊營收暴增的原因，北美 T-Mobile／Verizon 類業者用 5G 替代最後一哩光纖。"
            "公開市場研究常見「2030 年 FWA CPE 產值約 70 億美元、CAGR 雙位數」的區間（各機構數字不同，此處只作數量級，不作精確預估）。"
            "Dell’Oro：2025 年 5G FWA CPE 出貨年增 11%，成長還在、斜率已不如爆發年。"
            "智易已做出 5G／Wi-Fi 7 portable FWA 與帶 AI 運算的 FWA。未來五年 FWA 是「續航」不是「從 0 到 1」。",
            st["body"],
        )
    )
    story.append(
        p(
            "（3）光纖 PON 與銅線退場：GPON → XGS-PON／NG-PON2、G.fast hybrid。年報與 2025 財報都顯示寬頻固網在 2025 年大幅回升，與電信加速光纖到府、銅線退役一致。"
            "Dell’Oro：2025 年 PON ONT 全球出貨 1.58 億台。中國 FTTR（光纖到房）走低價雙頻 Wi-Fi 7 ONT，台灣 ODM 較難在純價格帶贏；歐美 XGS-PON 閘道才是智易的場。",
            st["body"],
        )
    )
    story.append(
        p(
            "（4）北美 Cable／DOCSIS 4.0：這是中磊比智易更敏感的週期。Charter Network Evolution 時程已從 2025 延到 2027；2025 年 CPE 空窗、2026 年 DAA／基礎設施支出回升（Dell’Oro：2026Q1 Cable DAA 支出年增 40%）。"
            "智易有 DOCSIS 3.1／4.0 產品，但 Cable 不是唯一引擎，所以 2025 年比中磊抗跌、2026 年彈升也沒中磊那麼陡。未來五年若 DOCSIS 4.0 閘道在 2027 前後放量，智易會吃到一塊，但不是全部故事。",
            st["body"],
        )
    )
    story.append(p("4.3 產業成長的誠實上限", st["h2"]))
    story.append(
        p(
            "寬頻用戶數全球仍增，但已開發市場接近飽和。Dell’Oro 對整體寬頻設備 2025–2030 的量成長轉述約 0.3% 年均——"
            "意思是：這不是「AI 伺服器式」的爆發產業，而是規格升級（Wi-Fi 6→7、DOCSIS 3.1→4.0、GPON→XGS-PON）帶動 ASP 與產品組合的產業。"
            "誰能把電信客製軟體、認證與交期做成轉換成本，誰就能在量不爆炸時仍擴利潤。"
            "IEK（年報引用）：113 年台灣通訊產值年減 2.4%，114 年需求回到正常。這與智易 2024 年減、2025–2026 低個位數回升的財報完全同向。",
            st["body"],
        )
    )

    # 5 競爭力
    story.append(p("五、全球競爭力", st["h1"]))
    story.append(p("5.1 競爭場與對手", st["h2"]))
    story.append(
        p(
            "NETGEAR 2024 年 10-K 在服務供應商市場點名的競爭者包括：Actiontec、Airties、Arcadyan、ARRIS、ASUS、AVM、Compal Broadband、D-Link、eero、Hitron、Huawei、Inseego、Nokia、Plume、Sagem、Sercomm、Technicolor／Vantiva、TP-Link、Ubee、ZTE、Zyxel 等。"
            "這張名單說明兩件事：第一，智易已被全球品牌商視為同一級對手；第二，戰場極碎，沒有人能「贏下全球 CPE」。",
            st["body"],
        )
    )
    rows = [
        ["智易 3596", "電信／MSO 閘道、FWA、PON、Cable、STB", "美歐亞分散；越南製造；仁寶 33%", "認證＋軟體客製＋JDM"],
        ["中磊 5388", "偏美洲 Cable／寬頻終端、商用網通", "美洲權重大", "直供電信；Cable 週期彈性高、波動也高"],
        ["啟碁 6285", "車用／衛星／網通模組，產品更廣", "和碩體系", "車用與衛星分散網通週期"],
        ["Sagemcom／Vantiva", "歐美電信閘道傳統強者", "歐洲品牌／營運商關係深", "在地認證與營運商 lock-in"],
        ["華為／中興", "全產品線、價格與垂直整合", "受歐美安全限制", "在受限市場讓出份額給台廠／歐廠"],
        ["NETGEAR／TP-Link／eero", "消費與部分電信", "品牌與通路", "零售價戰；電信標案不是主場"],
    ]
    story.append(
        table(
            ["對手", "產品重心", "結構特徵", "對智易的意義"],
            rows,
            [32 * mm, 48 * mm, 42 * mm, 48 * mm],
            st,
        )
    )
    story.append(p("5.2 智易的五項相對優勢", st["h2"]))
    adv = [
        "電信門檻：標案週期長、認證與軟體客製重，新進者不易用低價砸開。年報自己把這寫成「市場開發時間較長，進入障礙也較高」。",
        "晶片 Early Access：國際晶片廠指定為 Early Access Partner，Wi-Fi 7／5G 新矽能較早設計導入。這是時間優勢，不是永久護城河。",
        "產品與地區分散：相對中磊更不容易被單一 Cable 空窗打穿。2025 年就是實證。",
        "越南＋多地製造：非中國產能符合北美電信與潛在關稅；RBA 白金級對歐美 ESG 稽核是門票。",
        "集團與現金：仁寶體系、低有息負債、百億級存款，撐得住電信專案的週轉與股利。",
    ]
    for i, a in enumerate(adv, 1):
        story.append(p(f"{i}. {a}", st["body"]))
    story.append(p("5.3 相對弱勢與未解題", st["h2"]))
    weak = [
        "沒有消費品牌溢價，毛利率 15% 量級是優質 ODM，不是品牌 30%+。價格戰一起來，15% 會被咬。",
        "客戶 anonymized 但逾 10% 的客戶經常有兩家，單一電信商掉單會在一年內改寫營收結構（2024↔2025 的甲客戶即是）。",
        "亞洲及其他 2025 年與 2026 上半年明顯失速，分散結構的另一面是「永遠有一條腿在掉」。",
        "車用雷達、Edge AI Box、小基站仍屬培育，年報列為方向，尚未在產品細分裡獨立成能改變總營收斜率的引擎。",
        "公開測速市占（例如美國路由器 Speedtest 份額）衡量的是裝機存量，不是利潤；且高度綁定特定電信商的盒子，電信商一換標就可能掉。",
    ]
    for i, a in enumerate(weak, 1):
        story.append(p(f"{i}. {a}", st["body"]))

    # 6 五年展望
    story.append(p("六、公司未來五年前景（2026–2030）", st["h1"]))
    story.append(
        p(
            "以下為情境分析，不是公司財測，也不是股價目標。錨定點是：2025 年營收 530 億、毛利率 15.3%、EPS 12.60；2026 上半年已走完約一半、年增低個位數。",
            st["body"],
        )
    )
    story.append(img(charts["scenario"]))
    story.append(p("圖 6　營收情境帶（示意）", st["caption"]))
    rows = [
        [
            "保守",
            "Smart Home 續跌、電信 capex 再延、關稅侵蝕",
            "2026–2030 營收 510–545 億震盪",
            "毛利 14–15%；EPS 高個位數至 12 元附近",
        ],
        [
            "基準",
            "FWA／PON／Wi-Fi 7 補上 Smart Home；電信換機正常",
            "CAGR 約 3–5%，2030 年約 620–660 億",
            "毛利 15–16%；EPS 隨獲利緩升、配息維持",
        ],
        [
            "樂觀",
            "Smart Home 止跌回升＋北美 DOCSIS 4.0 與歐美 Wi-Fi 7 疊加",
            "CAGR 約 7–9%，2030 年約 750–820 億",
            "毛利挑戰 16%+；EPS 挑戰年增雙位數",
        ],
    ]
    story.append(
        table(
            ["情境", "前提", "營收路徑", "獲利含義"],
            rows,
            [22 * mm, 52 * mm, 52 * mm, 44 * mm],
            st,
        )
    )
    story.append(
        p(
            "為何基準不是爆發：產業量成長平坦、公司自己 2026 年至今只交出低個位數營收年增、智慧家庭仍在掉。"
            "為何不是衰退：電信換機有規格剛性（Wi-Fi 7、XGS-PON、DOCSIS 4.0），越南產能與認證讓智易仍在短名單上，現金與零長期借款提供緩衝。"
            "113 年年報對 114 年出貨量原估 +5% 至 +10%；實際 2025 營收 +8.2%，落在區間內。這種「公司指引偏保守、實際貼著區間走」的模式，比激進財測更接近電信 ODM 的節奏。",
            st["body"],
        )
    )
    story.append(p("6.1 未來五年經營槓桿（公司已揭示的動作）", st["h2"]))
    levers = [
        "產品：提高高單價／高毛利比重；Wi-Fi 7、FWA+AI、XGS-PON hybrid、DOCSIS 4.0、Edge AI Box、車用雷達。",
        "客戶：既有電信擴大品類（銅線→光纖→行動）、開發新興市場電信、MSO 滲透。",
        "製造：越南智動化、多地代工、關稅情境下的產地彈性。",
        "軟體：單一軟體平台、RDK／EasyMesh／開源電信堆疊，縮短客製週期。",
        "資本：穩定現金股利（近年 6.5–8.0 元量級）＋低槓桿，用獲利而非擴張負債成長。",
    ]
    for a in levers:
        story.append(p("• " + a, st["body"]))

    # 7 風險
    story.append(p("七、風險、觀察指標與方法限度", st["h1"]))
    story.append(p("7.1 主要風險", st["h2"]))
    risks = [
        "客戶集中與標案輪動：單一逾 10% 客戶的進出可在一年改寫營收與毛利。",
        "Smart Home 持續失血：這是 2026 年總成長封頂的主因；若跌勢不收斂，樂觀情境不成立。",
        "關稅與產地：北美電信訂單對「中國製造」敏感；越南不是萬能，產能、人力與物流都有上限。",
        "匯率：營收以美元／歐元為主、報表為新台幣；財報有遠期外匯與避險，但無法消掉所有損益波動。",
        "記憶體與零組件：網通 BOM 含 DRAM／Flash／PMIC，缺料或漲價會直接打毛利（ODM 轉嫁有時滯）。",
        "資安與地緣：電信設備受政府資安審查；台海與出口管制是尾部風險。",
        "技術代差：若電信商跳過 Wi-Fi 7 等 Wi-Fi 8，已備料的 7 世代閘道可能變成庫存。",
        "本報告不含股價、本益比或技術分析；不推論「該買該賣」。",
    ]
    for a in risks:
        story.append(p("• " + a, st["body"]))
    story.append(p("7.2 建議追蹤的公開指標（無需預測）", st["h2"]))
    kpis = [
        "月營收年增是否從 2026 年 1–7 月的 +2.8% 走出低個位數。",
        "每季產品細分：智慧家庭是否止跌、寬頻固網與行動通訊是否續增。",
        "毛利率是否守住 15%；掉到 14% 以下代表價格戰或組合惡化。",
        "存貨與應收週轉、合約負債：OCF 能否從 2025 年的「備料年」回到 2024 年的「收現年」。",
        "前兩大客戶占比與名稱輪動（年報隱碼，但金額公開）。",
        "北美 Cable DAA／DOCSIS 4.0 與歐美電信 Wi-Fi 7 標案新聞（產業領先指標）。",
    ]
    for a in kpis:
        story.append(p("• " + a, st["body"]))

    story.append(p("7.3 資料來源與方法（可稽核）", st["h2"]))
    story.append(
        p(
            "財務主表：智易 2021 年英文合併財報；2022、2024、2025 年中文合併財報（安侯建業查核，董事會通過日 2025 年報為 2026/2/25）。"
            "2023 年比較數字取自 2024 年合併財報。"
            "2022 年部分損益列（營業利益、合併淨利）以四季已公告合併綜合損益表加總，並在表下註記。"
            "年報敘事與地區占比、研發、股利、員工、IEK 引用：智易 113 年度中文年報。"
            "2026 H1：公開資訊觀測站 2026/8/5 重大訊息及同日綜合損益表。"
            "7 月營收：公司 2026/8 營收新聞。"
            "產業：Counterpoint Research〈54% of Broadband CPE Shipments in 2030 will be Wi-Fi 7-based〉；RCR Wireless 轉述 Dell’Oro（2026/3/18）；NETGEAR Form 10-K 2024；優分析 2026/8/12 對中磊／智易結構比較（僅用其引述之公開產業事實與公司已公告細分，不用其投資結論）。",
            st["body"],
        )
    )
    story.append(
        p(
            "未使用：FinMind API、FRED API、內部未公開資料庫、分析師目標價、股價與技術指標。"
            "本環境無 augur PostgreSQL 可查，故未引用庫內特徵或預測分數。"
            "前瞻段落為情境，不是精準財測；產業第三方的 2030 年市占／產值數字各機構不同，本文只採已公開、可點名來源，並避免把單一家顧問公司的點估計寫成「世界如此」。",
            st["body"],
        )
    )
    story.append(
        p(
            "免責：本文件為公開資訊之結構整理與情境討論，供研究參考。不構成證券投資、法律或稅務建議。任何人依本文件作成之決定，應自行承擔結果。",
            st["small"],
        )
    )
    story.append(Spacer(1, 6 * mm))
    end = Table(
        [
            [
                p(
                    "<b>報告產出</b><br/>檔名：arcadyan_3596_5yr_financial_outlook_20260827.pdf<br/>日期：2026-08-27<br/>主體：智易科技 Arcadyan（3596.TW）",
                    st["small"],
                )
            ]
        ],
        colWidths=[178 * mm],
    )
    end.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(end)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return pdf_path


if __name__ == "__main__":
    target = OUT_DIR / PDF_NAME
    path = build(target)
    print(f"WROTE {path} bytes={path.stat().st_size}")
