#!/usr/bin/env python3
"""🎯 把 6855 數泓科近五年財務與五年前景分析渲染成可下載 PDF。

守原則精華 #1 #9 #10（數字皆有公開來源；本檔不打 FinMind／FRED）。
本報告為 [I] 研究產出、self-reported，非投資建議。

執行指令矩陣：
  python3 scripts/render_eclatorq_6855_report.py
      # 寫 reports/augur_6855_eclatorq_5y_finance_outlook_20260827.pdf
  python3 scripts/render_eclatorq_6855_report.py --selftest
      # 零外部依賴：註冊字型、渲染 1 頁至暫存檔、斷言檔案非空
"""
from __future__ import annotations

import argparse
import sys
import tempfile
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

REPO = Path(__file__).resolve().parent.parent
OUT_PDF = REPO / "reports" / "augur_6855_eclatorq_5y_finance_outlook_20260827.pdf"
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

NAVY = colors.HexColor("#0B2545")
TEAL = colors.HexColor("#1B6B93")
GOLD = colors.HexColor("#B8860B")
CREAM = colors.HexColor("#F4F1EA")
ROW_ALT = colors.HexColor("#EEF4F8")
GREEN = colors.HexColor("#1F7A4C")
RED = colors.HexColor("#B42318")
GRAY = colors.HexColor("#4A5560")


def find_font() -> str:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    raise FileNotFoundError("找不到中文字型（WenQuanYi / Droid / Noto CJK）")


def register_font() -> str:
    path = find_font()
    pdfmetrics.registerFont(TTFont("Cjk", path, subfontIndex=0))
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Droid Sans Fallback", "Noto Sans CJK TC"]
    plt.rcParams["axes.unicode_minus"] = False
    return path


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName="Cjk", fontSize=11,
            textColor=GOLD, alignment=TA_CENTER, tracking=1.2, spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Cjk", fontSize=26,
            textColor=NAVY, alignment=TA_CENTER, leading=34, spaceAfter=10,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontName="Cjk", fontSize=13,
            textColor=TEAL, alignment=TA_CENTER, leading=20, spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Cjk", fontSize=16,
            textColor=NAVY, spaceBefore=14, spaceAfter=8, leading=22,
            borderPadding=3,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Cjk", fontSize=13,
            textColor=TEAL, spaceBefore=10, spaceAfter=6, leading=18,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Cjk", fontSize=10,
            textColor=NAVY, leading=16, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Cjk", fontSize=10,
            textColor=NAVY, leading=15, leftIndent=12, spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Cjk", fontSize=8.5,
            textColor=GRAY, alignment=TA_CENTER, leading=12, spaceBefore=2, spaceAfter=10,
        ),
        "footnote": ParagraphStyle(
            "footnote", parent=base["Normal"], fontName="Cjk", fontSize=8,
            textColor=GRAY, leading=12, alignment=TA_LEFT, spaceAfter=3,
        ),
        "th": ParagraphStyle(
            "th", parent=base["Normal"], fontName="Cjk", fontSize=8,
            textColor=colors.white, alignment=TA_CENTER, leading=11,
        ),
        "td": ParagraphStyle(
            "td", parent=base["Normal"], fontName="Cjk", fontSize=8,
            textColor=NAVY, alignment=TA_CENTER, leading=11,
        ),
        "td_left": ParagraphStyle(
            "td_left", parent=base["Normal"], fontName="Cjk", fontSize=8,
            textColor=NAVY, alignment=TA_LEFT, leading=11,
        ),
        "quote": ParagraphStyle(
            "quote", parent=base["Normal"], fontName="Cjk", fontSize=10,
            textColor=TEAL, leading=16, leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=8, backColor=CREAM, borderPadding=6,
        ),
        "kpi_v": ParagraphStyle(
            "kpi_v", parent=base["Normal"], fontName="Cjk", fontSize=14,
            textColor=NAVY, alignment=TA_CENTER, leading=18,
        ),
        "kpi_l": ParagraphStyle(
            "kpi_l", parent=base["Normal"], fontName="Cjk", fontSize=8,
            textColor=GRAY, alignment=TA_CENTER, leading=11,
        ),
    }
    return s


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Cjk", 8)
    canvas.drawString(16 * mm, A4[1] - 8 * mm, "6855 數泓科｜近五年財務分析與五年前景／全球競爭力")
    canvas.drawRightString(A4[0] - 16 * mm, A4[1] - 8 * mm, "as-of 2026-08-27  ·  [I] 研究")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Cjk", 8)
    canvas.drawString(16 * mm, 4 * mm, "非投資建議  ·  數字溯源見附錄  ·  self-reported 分析")
    canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1] - 28 * mm, A4[0], 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 38 * mm, A4[0], 3 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Cjk", 10)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 18 * mm, "AUGUR  [I] 個股研究備忘  ·  公開資訊彙整  ·  2026-08-27")
    canvas.setFont("Cjk", 11)
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.62 + 46 * mm, "上櫃  ·  其他電子業  ·  數位手工具")
    canvas.setFont("Cjk", 28)
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.62 + 26 * mm, "數泓科技（6855）")
    canvas.setFont("Cjk", 16)
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.62 + 8 * mm, "近五年財務分析")
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.62 - 8 * mm, "與公司／產業未來五年前景、全球競爭力")
    canvas.setFont("Cjk", 10)
    canvas.drawCentredString(A4[0] / 2, 70 * mm, "Eclatorq Technology Co., Ltd.")
    canvas.drawCentredString(A4[0] / 2, 56 * mm, "資料截止：財務年報至 2025；季報至 2026Q2；月營收至 2026-07")
    canvas.drawCentredString(A4[0] / 2, 44 * mm, "本報告不是進出場建議")
    canvas.restoreState()


def p(text, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


def kpi_table(s):
    cells = [
        [p("118.5 元", s["kpi_v"]), p("27.6 億", s["kpi_v"]), p("15.1× / 12.0×", s["kpi_v"]), p("4.6%", s["kpi_v"])],
        [p("收盤價（2026-08-27 nStock）", s["kpi_l"]),
         p("市值（× 23,249,716 股）", s["kpi_l"]),
         p("本益比：2025 EPS 7.85／TTM 9.90", s["kpi_l"]),
         p("現金殖利率（股利 5.5／除息前 119.5）", s["kpi_l"])],
        [p("49.5%", s["kpi_v"]), p("35.1%", s["kpi_v"]), p("20.5%", s["kpi_v"]), p("96% : 4%", s["kpi_v"])],
        [p("2025 毛利率（年報加總）", s["kpi_l"]),
         p("2025 營業利益率", s["kpi_l"]),
         p("2025 ROE（年報）", s["kpi_l"]),
         p("2025 客戶品牌 : 自有品牌", s["kpi_l"])],
    ]
    t = Table(cells, colWidths=[42 * mm, 42 * mm, 42 * mm, 42 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 0.4, TEAL),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D7DE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("SPAN", (0, 0), (0, 0)),
    ]))
    return t


def make_table(headers, rows, s, col_widths=None):
    head = [p(h, s["th"]) for h in headers]
    data = [head]
    for r in rows:
        data.append([p(str(c), s["td_left"] if i == 0 else s["td"]) for i, c in enumerate(r)])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Cjk"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D7DE")),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(cmds))
    return t


def save_charts(tmpdir: Path) -> dict[str, Path]:
    years = ["2021", "2022", "2023", "2024", "2025"]
    rev = [4.443, 4.488, 4.801, 6.219, 6.262]  # 億
    ni = [0.963, 1.273, 1.330, 2.139, 1.825]
    gm = [46.38, 46.49, 47.72, 49.35, 49.51]
    om = [30.25, 27.29, 30.68, 31.75, 35.13]
    nm = [21.67, 28.36, 27.71, 34.39, 29.15]
    paths = {}

    fig, ax1 = plt.subplots(figsize=(7.2, 3.2), dpi=140)
    ax1.bar(years, rev, color="#1B6B93", width=0.55, label="營收")
    ax1.set_ylabel("營收（億元）", color="#1B6B93")
    ax1.tick_params(axis="y", labelcolor="#1B6B93")
    ax2 = ax1.twinx()
    ax2.plot(years, ni, color="#B8860B", marker="o", linewidth=2.2, label="稅後淨利")
    ax2.set_ylabel("稅後淨利（億元）", color="#B8860B")
    ax2.tick_params(axis="y", labelcolor="#B8860B")
    ax1.set_title("近五年營收與稅後淨利")
    fig.tight_layout()
    p1 = tmpdir / "rev_ni.png"
    fig.savefig(p1, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["rev_ni"] = p1

    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=140)
    ax.plot(years, gm, marker="o", color="#0B2545", label="毛利率")
    ax.plot(years, om, marker="s", color="#1B6B93", label="營業利益率")
    ax.plot(years, nm, marker="^", color="#B8860B", label="淨利率")
    ax.set_ylim(15, 55)
    ax.set_ylabel("%")
    ax.set_title("近五年三率")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    p2 = tmpdir / "margins.png"
    fig.savefig(p2, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["margins"] = p2

    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    m2024 = [55617, 53738, 43808, 47406, 63062, 44930, 47873, 51542, 47510, 50100, 69891, 46429]
    m2025 = [69177, 51255, 48925, 44411, 80039, 57256, 45849, 38032, 41518, 44097, 49496, 56179]
    m2026 = [39127, 47421, 46956, 51071, 62767, 64273, 73290, None, None, None, None, None]
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=140)
    ax.plot(months, [x / 1000 for x in m2024], color="#9AA5B1", marker=".", label="2024")
    ax.plot(months, [x / 1000 for x in m2025], color="#1B6B93", marker="o", label="2025")
    ax.plot(months[:7], [x / 1000 for x in m2026[:7]], color="#B8860B", marker="s", label="2026")
    ax.set_ylabel("月營收（百萬元）")
    ax.set_title("月營收：2024–2026（至 7 月）")
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    p3 = tmpdir / "monthly.png"
    fig.savefig(p3, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["monthly"] = p3

    labels = ["北美", "台灣", "亞洲", "歐洲", "其他"]
    v2022 = [51.75, 27.28, 11.47, 7.98, 1.52]
    v2024 = [60.33, 21.20, 8.54, 8.03, 1.90]
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=140)
    ax.bar([i - 0.18 for i in x], v2022, width=0.36, color="#9AA5B1", label="2022")
    ax.bar([i + 0.18 for i in x], v2024, width=0.36, color="#1B6B93", label="2024")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("%")
    ax.set_title("銷售地區占比（年報）")
    ax.legend(frameon=False)
    fig.tight_layout()
    p4 = tmpdir / "region.png"
    fig.savefig(p4, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["region"] = p4

    return paths


def build_story(s, charts: dict[str, Path]):
    story = []
    story.append(Spacer(1, 100 * mm))
    story.append(PageBreak())

    story.append(p("0. 讀法、範圍與資料誠實", s["h1"]))
    story.append(p(
        "本檔為 Augur 倉內 <b>[I] 研究備忘</b>，不是憲章、不是進出場單。分析意見標 <b>self-reported</b>："
        "不得當成「世界如此」或「能力如此」的權威確認。本環境無本機 PostgreSQL／.env，"
        "<b>未使用 FinMind／FRED API</b>（取數凍結仍有效）；財務數字取自公司年報、永續報告書、"
        "公開資訊觀測站轉載之彙整站（HiStock 季報／月營收）與 2026 年 8 月新聞稿，並以年報勾稽。",
        s["body"],
    ))
    story.append(p(
        "<b>一句定錨</b>：數泓科是台灣第一家以「傳統手工具聚落＋工研院機電整合」做成的數位扭力工具廠。"
        "近五年營收從 4.44 億走到 6.26 億，毛利率穩在 46–50%；2025 稅後衰退來自匯兌，不是本業垮掉。"
        "未來五年勝負在三件事：專業級占比能否續升、歐洲與半導體訂單能否變成經常性營收、"
        "以及北美 DIY／匯率／關稅這三個外部變數。",
        s["quote"],
    ))
    story.append(kpi_table(s))
    story.append(Spacer(1, 4 * mm))
    story.append(p(
        "流通股 23,249,716（實收資本 232,497 仟元）。2026Q1 每股淨值 35.79 元（權益 832,101 仟元），"
        "股價淨值比約 3.3×。TTM EPS＝2025Q3–Q4（2.72＋3.03）＋2026H1（4.15）＝9.90 元。",
        s["body"],
    ))

    story.append(p("1. 公司是什麼", s["h1"]))
    story.append(p(
        "數泓科技股份有限公司（Eclatorq）2006-06-26 由工研院機械所技術團隊與 11 家中部手工具業者合資成立，"
        "2022-10-06 上櫃。總部台中潭子北環路 15-1 號。董事長游祥鎮（銳泰精密），總經理／發言人李明華。"
        "簽證會計師：安永聯合（黃宇廷、羅文振）。2024 年底員工 106 人；研發 11 人（碩士以上約 27%）。",
        s["body"],
    ))
    story.append(p(
        "產品幾乎全是數位手工具及零組件（2025 年 99.71%）：數位扭力扳手、迷你扳手、無線扳手、"
        "數位螺絲起子、扭力／角度接桿、角度規。應用以汽車維修與航太為主，並向半導體精密鎖固、"
        "植牙醫療工具與 AR／視覺鎖固系統延伸。商業模式是<b>專業代工為主、自有品牌為輔</b>："
        "2024 客戶品牌:自有＝97:3，出貨 233,657 PCS；2025 為 96:4，專業:DIY＝52:48。"
        "北美車庫論壇指出 Stanley Black &amp; Decker 旗下 Mac／Proto／Facom／USAG 的數位扭力扳手"
        "多數由其代工——這解釋了「品牌不出名、毛利卻接近五成」的結構。",
        s["body"],
    ))
    story.append(p(
        "11 家黑手股東本身就是台灣手工具隱形冠軍（套筒銳泰、活動扳手伯鑫、鋸子久允、起子義成、"
        "至光、英發、特典、崑印、向得行、東立、防震力）。這不是一般電子代工的「找低成本供應鏈」，"
        "而是把既有金屬成形聚落的鍛造／熱處理／品管，接上感測、韌體、無線與遠端校準。"
        "公司年報自稱遠端網路校準為「全世界首創」——此為公司自陳，本報告不當成獨立驗證的技術事實。",
        s["body"],
    ))

    story.append(p("2. 近五年損益：規模跳一階，本業比稅後穩", s["h1"]))
    story.append(p(
        "單位新台幣仟元。2021 年 HiStock 未單列 Q1，Q2 欄位與 Q3＋Q4 加總恰等於年報全年營收 444,335，"
        "本表按「H1＋Q3＋Q4」加總，並用 112 年報「110 年純益率 21.67%」勾稽稅後。2022–2024 與永續報告書／年報一致。",
        s["footnote"],
    ))
    story.append(make_table(
        ["年度", "營收", "年增", "毛利", "毛利率", "營業利益", "營益率", "稅後", "淨利率", "EPS"],
        [
            ["2021", "444,335", "—", "206,082", "46.4%", "134,400", "30.3%", "96,278", "21.7%", "5.34"],
            ["2022", "448,763", "+1.0%", "208,649", "46.5%", "122,476", "27.3%", "127,252", "28.4%", "6.47"],
            ["2023", "480,057", "+7.0%", "229,123", "47.7%", "147,260", "30.7%", "133,036", "27.7%", "5.72"],
            ["2024", "621,907", "+29.6%", "306,890", "49.4%", "197,449", "31.8%", "213,861", "34.4%", "9.20"],
            ["2025", "626,234", "+0.7%", "310,043", "49.5%", "220,009", "35.1%", "182,541", "29.2%", "7.85"],
        ],
        s,
        col_widths=[16*mm, 20*mm, 16*mm, 20*mm, 16*mm, 22*mm, 16*mm, 20*mm, 16*mm, 14*mm],
    ))
    story.append(p("表 1　近五年綜合損益（仟元）。來源：113／114 年報、2024 永續報告書、HiStock 季報加總。", s["caption"]))
    story.append(Image(str(charts["rev_ni"]), width=168 * mm, height=74 * mm))
    story.append(p("圖 1　營收在 2024 跳一階；2025 營收持平、稅後回落。", s["caption"]))
    story.append(Image(str(charts["margins"]), width=168 * mm, height=74 * mm))
    story.append(p("圖 2　毛利率五年緩升；2025 營益率創新高，淨利率被匯兌拉下來。", s["caption"]))

    story.append(p("怎麼讀這五年", s["h2"]))
    story.append(p(
        "• <b>2021</b>：疫後訂單爆發年。營收 4.44 億（年報；對 2020 的 3.26 億大幅跳升），本業已經是三成營益率的公司。<br/>"
        "• <b>2022</b>：上櫃年。營收幾乎持平（+1.0%），營業利益反而掉，但稅後因營業外（含匯兌）拉到淨利率 28.4%。"
        "IPO 現金進帳，年底資產從 5.83 億跳到 9.85 億。<br/>"
        "• <b>2023</b>：客戶庫存調整。營收 +7.0% 到 4.80 億，EPS 因股本膨脹（加權股數到 23,250 仟股）降到 5.72。"
        "專業:DIY 與北美占比開始上升。<br/>"
        "• <b>2024</b>：結構年。營收 +29.6% 到 6.22 億，稅後 +60.8% 到 2.14 億，EPS 9.20 歷史高。"
        "年報歸因客戶需求增加；外部整理指疫情暫停的品牌共同開發在 2024 放量。出貨 23.4 萬支，DIY 略多於專業（51:49）。"
        "營業外淨利益 73,979 仟元（含匯兌）是稅後「看起來特別好」的原因之一。<br/>"
        "• <b>2025</b>：本業更好、帳面更差。營收 6.26 億僅 +0.7% 仍創新高；<b>營業利益 2.20 億、營益率 35.1%，五年最高</b>；"
        "稅後 1.83 億、年減 14.7%，EPS 7.85。總經理李明華（2026-03 新聞）：獲利衰退主因新台幣升值匯兌損失，"
        "美國對等關稅影響相對輕微。Q2 單季稅後 −19,293 仟元、EPS −0.83，是匯兌不是毛利崩——"
        "同季毛利率 50.16%、營益率 41.88%。全年毛利率 49.51% 再創新高。",
        s["body"],
    ))

    story.append(p("3. 2026 上半年：營收還沒回來，獲利基期很低所以年增很大", s["h1"]))
    story.append(make_table(
        ["期間", "營收", "年增", "毛利率", "營益率", "稅後", "EPS", "來源"],
        [
            ["2026Q1", "133,109", "−21.4%", "48.8%", "29.5%", "47,167", "2.03", "HiStock 季報"],
            ["2026Q2", "178,111", "−2.0%", "48.8%", "35.3%", "49,357", "2.12", "HiStock 季報"],
            ["2026H1", "311,220", "−11.3%", "48.8%", "32.8%", "96,524", "4.15", "公司／工商時報 2026-08-11"],
            ["2026 1–7 月", "384,510", "−3.1%", "—", "—", "—", "—", "HiStock 月營收"],
        ],
        s,
        col_widths=[24*mm, 22*mm, 18*mm, 18*mm, 18*mm, 20*mm, 16*mm, 36*mm],
    ))
    story.append(p("表 2　2026 進度。H1 稅後年增 +97.8% 是因為 2025H1 含 Q2 匯兌大虧，不是本業翻倍。", s["caption"]))
    story.append(Image(str(charts["monthly"]), width=168 * mm, height=76 * mm))
    story.append(p("圖 3　2026 年 1 月深谷（年減 43%），7 月 7,329 萬創單月新高、年增 59.9%。", s["caption"]))
    story.append(p(
        "公司（2026-08-11 經濟日報／工商時報）說：國際情勢緩和、美元走穩，手工具客戶回補庫存，"
        "專業級新品挹注；前七月專業級出貨數量占比由 2025 約 52% 升到 57%。毛利率被新品帶動、抵銷原物料與薪資。"
        "7 月之後累計營收缺口已收到 −3.1%。若 8–12 月能接近 2024 下半年節奏（當時 7–12 月約 3.13 億），"
        "全年有機會接近或超過 2025；這是情境，不是公司財測——公司未公開財務預測。",
        s["body"],
    ))
    story.append(p(
        "半導體：公司稱高精密數位工具與量測系統已取得半導體大廠認可，<b>預期 2026 年底前有機會試單出貨</b>。"
        "同時開發 AR＋視覺辨識的 AI 製造／監控系統。這兩項在財報裡都還不是已認列的經常性營收，"
        "只能當選擇權，不能當 2026 年的基數。",
        s["body"],
    ))

    story.append(p("4. 資產負債：輕資產、現金停在「按攤銷後成本衡量之金融資產」", s["h1"]))
    story.append(make_table(
        ["時點", "資產", "負債", "權益", "負債比", "流動比", "每股淨值"],
        [
            ["2021Q4", "582,575", "100,255", "482,320", "17.2%", "4.91", "—"],
            ["2022Q4", "985,073", "292,958", "692,115", "29.7%", "3.06", "—"],
            ["2023Q4", "1,050,762", "320,724", "730,038", "30.5%", "3.01", "—"],
            ["2024Q4", "1,208,927", "339,004", "869,923", "28.0%", "3.36", "37.4"],
            ["2025Q4", "1,388,351", "475,373", "912,978", "34.2%", "2.77", "39.3"],
            ["2026Q2", "1,473,180", "589,920", "883,260", "40.0%", "2.37", "38.0"],
        ],
        s,
        col_widths=[22*mm, 26*mm, 24*mm, 24*mm, 20*mm, 20*mm, 20*mm],
    ))
    story.append(p("表 3　資產負債（仟元）。2026Q2 取 PChome 股市；其餘 HiStock／年報。每股淨值＝權益／23,249,716。", s["caption"]))
    story.append(p(
        "結構特徵：流動資產長期佔總資產 90% 以上（2026Q2 94.3%）。固定資產只有約 7 千萬——組裝＋委外金屬件，不是重資本工廠。"
        "2026Q2「其他應收款」667.6 百萬、佔總資產 45%。看起來刺眼，但 113 年報現金流量說明寫得很清楚："
        "投資活動現金流出主因是<b>按攤銷後成本衡量之金融資產增加</b>（三個月以上定存／債券型金融資產），"
        "不是客戶欠款爆掉。應收帳款淨額僅 1.14 億（7.8%），與營收規模匹配。",
        s["body"],
    ))
    story.append(p(
        "負債比從上櫃前 17% 升到 2026Q2 的 40%，主因短期借款（2026Q2 3.24 億，佔資產 22%）加上股利。"
        "流動比從 2024 的 3.36 降到 2.37，仍在安全區，但方向是「把閒置資金與短貸一起做財務操作」，"
        "不是經營惡化。利息保障在年報歷史裡長期很高（110 年甚至無息）；要盯的是短貸滾續與定存對利率的敏感，不是償債危機。",
        s["body"],
    ))
    story.append(p(
        "年報財務比率補充（112 年報五年分析，會計師簽證）：存貨週轉天數 2021 年 145 天 → 2022 年 239 天 → 2023 年 266 天，"
        "反映少量多樣、備料拉長。這是此商業模式的代價：週轉慢、毛利高。總資產週轉 2022 年因 IPO 現金墊高分母掉到 0.57，"
        "之後維持 0.5 附近——賺的是利潤率，不是周轉速度。",
        s["body"],
    ))

    story.append(p("5. 現金流、股利、獲利品質", s["h1"]))
    story.append(p(
        "113 年報揭露 2023／2024 現金流（仟元）：營業 183,191 → 215,076；投資 −262,922 → −210,898；"
        "籌資 −86,921 → −94,845。營業現金流兩年都覆蓋稅後（2023 稅後 1.33 億、2024 2.14 億；"
        "2024 OCF 2.15 億約等於稅後，品質正常，沒有「獲利全是應收」）。投資端持續把現金換成按攤銷後成本金融資產；"
        "籌資端是還短貸＋發股利。",
        s["body"],
    ))
    story.append(make_table(
        ["所屬年度", "EPS", "現金股利", "股票股利", "配息率", "除息日", "除息前價", "現金殖利率"],
        [
            ["2021", "5.34", "4.0", "0", "74.9%", "2022-06-07", "—", "—"],
            ["2022", "6.47", "4.5", "0", "69.6%", "2023-06-06", "88.5", "5.08%"],
            ["2023", "5.72", "3.5", "1.0", "現金 61.2%", "2024-08-01", "132.5", "2.64%"],
            ["2024", "9.20", "6.0", "0", "65.2%", "2025-08-07", "140.0", "4.29%"],
            ["2025", "7.85", "5.5*", "0", "70.1%", "2026-08-06", "119.5", "4.60%"],
        ],
        s,
        col_widths=[20*mm, 16*mm, 20*mm, 20*mm, 24*mm, 24*mm, 22*mm, 22*mm],
    ))
    story.append(p("表 4　股利。*2025 為盈餘 5.0＋資本公積 0.5。來源：HiStock 除權息、聯合新聞網 2026-03。", s["caption"]))
    story.append(p(
        "配息率鎖在 65–75% 現金（2023 另配 1 元股票）。這是「高ROE、輕資本、多餘現金回股東」的公司，"
        "不是靠留存擴大產能的成長股。五年現金股利合計 23.5 元（不含 2023 股票）。"
        "代價是成長若要靠併購或自建重資產，現有政策幫不上忙——而公司目前也不走那條路。",
        s["body"],
    ))

    story.append(p("6. 杜邦與同業：利潤率是護城河，周轉與規模不是", s["h1"]))
    story.append(make_table(
        ["年度", "ROE", "ROA", "淨利率", "資產週轉", "權益乘數"],
        [
            ["2021（年報）", "23.3%", "18.6%", "21.7%", "0.86", "1.21"],
            ["2022（年報）", "21.7%", "16.3%", "28.4%", "0.57", "1.42"],
            ["2023（年報）", "18.7%", "13.4%", "27.7%", "0.46", "1.44"],
            ["2024（年報）", "26.7%", "19.2%", "34.4%", "0.55*", "1.39"],
            ["2025（年報）", "20.5%", "14.3%", "29.2%", "0.48*", "1.52"],
        ],
        s,
        col_widths=[32*mm, 28*mm, 28*mm, 28*mm, 28*mm, 28*mm],
    ))
    story.append(p("表 5　杜邦。標 * 的資產週轉＝營收／當年底資產，與年報「平均資產」口徑可能差一截，僅供對方向。", s["caption"]))
    story.append(p(
        "ROE 的引擎是淨利率，不是周轉、也不是槓桿。2024 淨利率被匯兌推到 34%，ROE 26.7%；"
        "2025 本業營益率更高，但淨利率回 29%，ROE 回 20.5%。看本業用營業利益／權益："
        "2025 營業利益 2.20 億／平均權益約 8.91 億 ≈ 24.7%，比稅後 ROE 更穩。",
        s["body"],
    ))
    story.append(p(
        "可公開比較的台灣同業不是「其他電子」，而是手工具股東伯鑫（6904，活動扳手）。"
        "伯鑫 2025 營收約 8.65 億、大於數泓；2024 各季毛利率約 34–36%、營益率約 22–25%；"
        "2025–2026Q1 毛利率掉到 28–35%。數泓毛利率長期高出約 15 個百分點。"
        "這不是管理魔術，是產品：數位扭力＝金屬件＋感測＋軟體＋校準服務，機械扳手做不到這個定價。"
        "國內年報也寫：數位手工具「於國內市場並無上市、上櫃之同業」。真正的對手在歐美日品牌端。",
        s["body"],
    ))
    story.append(p(
        "相對台灣手工具全體：年報用經濟部「扳手及其他手工具內外銷」當分母，"
        "2022–2024 市占約 0.69%／0.56%／0.69%（2024 分母 896.8 億）。"
        "這衡量的是「在整個手工具大海裡的水滴」，不是數位扭力這個小池塘的市占。"
        "公司與今周刊／經理人報導的自我定位是台灣數位手工具龍頭、全球前段代工廠之一；"
        "獨立第三方市占數字本輪找不到可與年報勾稽的來源，故不編造。",
        s["body"],
    ))

    story.append(p("7. 產業：傳統手工具升級帶，不是電子週期股", s["h1"]))
    story.append(p(
        "手工具分工業組裝、專業維修、家庭 DIY。扭力工具的本質是：螺絲有扭力規格，超過就斷、不足就鬆。"
        "數位化把老師傅手感變成可紀錄、可上傳、可追溯的牛頓・米。需求驅動是汽車（含 EV 電池／底盤）、"
        "航太、能源、工業 4.0 鎖付追溯、以及 DIY 大賣場把「電子扭力扳手」做成貨架標配。",
        s["body"],
    ))
    story.append(p(
        "台灣位置：中彰投有全球少見的完整手工具聚落（逾 2,000 家、以中小企業為主）。"
        "經濟部 2012 年把數位手工具列為亮點傳統產業。美國是台灣手工具第一大出口市場。"
        "中國低價機械扳手是紅海；數位中高階仍受美中關稅與品質認證保護，台灣代工有結構性縫隙。"
        "這條縫不是永遠的：一旦中國廠通過同等校準與無線協定，價差會被壓縮。",
        s["body"],
    ))
    story.append(p(
        "全球市場規模各顧問數字差一個數量級，不能當單一事實引用。本輪查到的公開區間：<br/>"
        "• Strategic Market Research：數位扭力扳手 2024 年 6.20 億美元，2030 年 9.20 億，CAGR 6.8%。<br/>"
        "• Grand Research Store：2025 年 2.70 億美元，2034 年 3.55 億，CAGR 4.1%。<br/>"
        "• Reanin：2025 年 19.0 億美元，2032 年 25.8 億，CAGR 4.5%（口徑顯然更寬）。<br/>"
        "• Grand View Research（電動扭力工具，含 nutrunner 等）：2024 年 6.40 億美元，2033 年 10.1 億，CAGR 5.2%。<br/>"
        "能用的共同結論只有一句：<b>這是數億至十數億美元的利基市場，未來五年複合成長大概中個位數到高個位數，不是半導體式的翻倍賽道</b>。"
        "數泓 2025 營收約 1,900 萬美元量級，在「數位扭力扳手」窄口徑裡不是可以忽略的小廠，"
        "在「全球工具集團」口徑裡則是 Snap-on／SBD／Hilti 的供應商而非對等競爭者。",
        s["body"],
    ))
    story.append(Image(str(charts["region"]), width=168 * mm, height=74 * mm))
    story.append(p("圖 4　北美從 2022 年 51.8% 升到 2024 年 60.3%；台灣占比下降。歐洲仍不到一成——這是公司自己要補的洞。", s["caption"]))

    story.append(p("年報寫的下游品牌地圖", s["h2"]))
    story.append(p(
        "美國銷售端：Stanley Black &amp; Decker、Bostitch、Ritchie、Mac Tools、Lowe's、Snap-on。"
        "歐洲：Stahlwille、BeA、Prebena、Omer、Hazet。國外主要競爭對手（品牌＋製造）："
        "美國 Snap-on、日本東日 Tohnichi、歐洲 Stahlwille。這些公司賣的是品牌、服務車、校正實驗室與規格話語權；"
        "數泓賣的是被包在別人品牌裡的機電模組。客戶 &gt;700 家、單一客戶不至於致命，但<b>通路品牌集中在北美專業／DIY 連鎖</b>，"
        "總體仍是「美國景氣＋美元」β。",
        s["body"],
    ))

    story.append(p("8. 公司未來五年前景（self-reported 情境，不是財測）", s["h1"]))
    story.append(p(
        "公司未公開 2026–2030 財務預測。114 年報致股東報告書與 2026 年 8 月法說型新聞構成「官方敘事」："
        "專業產品拉歐洲市占、DIY 在北美擴張並進歐洲／亞洲；智慧鎖固（AR／AI／5G／即時錄影）、"
        "電動數位工具、植牙醫療工具；尋求與競爭對手合作「建立依賴性」。2024 年報曾寫 2025 出貨目標 290,400 PCS"
        "（實際 2025 營收幾乎持平，PCS 未在本輪找到全年實績）。以下三情境是分析者對公開資訊的推演，標 self-reported。",
        s["body"],
    ))
    story.append(make_table(
        ["情境", "假設", "2026–2030 營收方向", "毛利率", "結果樣貌"],
        [
            ["基準", "專業級維持 ≥55%；歐洲緩升；半導體僅試單；匯率不再單邊大升",
             "年複合成長約中高個位數（接近產業 4–8%＋些許市占）",
             "47–50%",
             "2030 營收約 8–10 億；EPS 波動主要來自匯兌，本業 ROE 仍 18–24%"],
            ["樂觀", "半導體／智慧鎖固 2027 起貢獻可辨識營收；歐洲專業突破 15%+",
             "低雙位數 CAGR",
             "50%+",
             "從「高毛利代工」走到「製程資料／系統」；估值邏輯會變，不只是配息股"],
            ["保守", "北美 DIY 長疲；關稅加碼；新台幣再升；半導體試單沒轉量",
             "營收停在 6–7 億",
             "42–46%",
             "仍能配息，但 2024 那種跳躍不再現；短貸＋定存的財務槓桿變得更顯眼"],
        ],
        s,
        col_widths=[18*mm, 42*mm, 38*mm, 20*mm, 54*mm],
    ))
    story.append(p("表 6　五年情境。不是目標價、不是建議。任何路徑都可能被單一客戶或匯率打亂。", s["caption"]))

    story.append(p("支撐基準／樂觀的公開證據", s["h2"]))
    story.append(p(
        "1. <b>產品組合已在轉</b>：專業級出貨占比 2024 年 49% → 2025 年 52% → 2026 前七月 57%。"
        "專業級較不易被大賣場促銷價打死，這是毛利率能守住 48% 以上的直接原因。<br/>"
        "2. <b>2026 年中已見到訂單回補</b>：7 月營收歷史新高。這只能證明補庫存發生了，不能證明新循環的斜率。<br/>"
        "3. <b>半導體與系統是真實在研發的產品線</b>，不是空口：年報列智慧鎖固、電動工具、醫療工具為正式 R&amp;D 方向；"
        "今周刊 2024 年已報導高單價扳手進入半導體龍頭。轉成營收的時點仍是「預期年底試單」。<br/>"
        "4. <b>本業現金會生現金</b>：OCF≈稅後、配息 65–75%，五年內不必為了維持股利去傷害資產負債——除非短貸利率急升。",
        s["body"],
    ))
    story.append(p("壓著樂觀的結構限制", s["h2"]))
    story.append(p(
        "1. <b>自有品牌只有 4%</b>。成長天花板在客戶要貨多少，不在 Eclatorq 品牌廣告。年報目標把自有品牌拉到 6% 仍是配角。<br/>"
        "2. <b>研發 11 人、研發費 2025 年 2,541 萬（營收 4.06%）</b>，低於 2024 的 3,067 萬。"
        "要同時做 AR 視覺鎖固、電動工具、植牙、半導體級精度，人力很緊。這是「利基冠軍」常見的瓶頸。<br/>"
        "3. <b>北美 60%</b>。歐洲 2024 年只有 8%。公司自己把「三年內歐美中 DIY 擴張」寫進計畫；目前數字還沒跟上敘事。<br/>"
        "4. <b>匯兌是盈餘的第二事業部</b>。2024 營業外＋7,398 萬、2025 Q2 單季轉虧，振幅大於本業季度波動。"
        "沒有避險政策的公開細節在本輪被獨立驗證。<br/>"
        "5. <b>市場本身只有中個位數成長</b>。要五年翻倍，必須吃市占或做出系統／半導體新曲線，不能靠產業β。",
        s["body"],
    ))

    story.append(p("9. 全球競爭力：在價值鏈的哪一層", s["h1"]))
    story.append(p(
        "若把數位扭力產業拆成四層——(A) 規格與品牌（Snap-on、SBD、Stahlwille、Tohnichi、Gedore、Norbar、Hilti）；"
        "(B) 精密扭力製造與校準實驗室；(C) 感測／無線／軟體模組；(D) 金屬成形與表面處理——"
        "數泓的家在 <b>B＋C，外包 D 給中部股東與供應鏈，幾乎不擁有 A</b>。"
        "Garage Journal 用戶要買 Eclatorq 3/4\" 扳手，得到的建議是「去買 Mac／Proto／Facom」。"
        "這句話同時是護城河（已經嵌進全球品牌 SKU）與天花板（終端忠誠度不在自己身上）。",
        s["body"],
    ))
    story.append(make_table(
        ["構面", "相對位置", "證據", "五年內會怎麼變"],
        [
            ["技術", "利基領先（台灣）／全球跟跑（對 Tohnichi／Stahlwille 實驗室）",
             "工研院出身、遠端校準自陳、專利 PatSnap 列 55 件",
             "若 AR／AI 鎖固做成，可從工具跳到製程資料；做不成則停在電子扳手"],
            ["製造", "強：少量多樣、聚落一站購足",
             "中彰投 11 家股東、年報強調彈性生產",
             "關稅若逼出海外產能，輕資產優勢會被測試"],
            ["品牌", "弱：4% 自有（Eclatorq／WIZTANK／e-Dynamic）",
             "2025 年報 96:4",
             "官方要拉到 6%，改變不了代工本質"],
            ["客戶", "廣（700+）但區域集中",
             "北美 60%、年報列 SBD／Mac／Lowe's 等",
             "歐洲與半導體是唯一能改地圖的兩個向量"],
            ["成本／關稅", "中：台灣中高階受惠美中關稅，自身也曝美銷",
             "2025 公司稱關稅影響輕；2026 H1 營收仍 −11%",
             "對等關稅若升級，ODM 報價權在品牌客戶"],
            ["規模", "小",
             "營收 ~6 億、員工 106、研發 11",
             "併購或被品牌深化綁定，比自己長成集團更可能"],
            ["財務", "強",
             "毛利 ~50%、配息、OCF 覆蓋",
             "可當「活得久」的本錢，買不到市占"],
        ],
        s,
        col_widths=[22*mm, 42*mm, 48*mm, 60*mm],
    ))
    story.append(p("表 7　全球競爭力評分卡（質化、self-reported）。", s["caption"]))

    story.append(p("對主要對手怎麼打", s["h2"]))
    story.append(p(
        "• <b>Snap-on</b>：賣服務車與技師終身關係，數位扳手只是目錄一頁。數泓不正面打，而是當可能的 OEM／或被排除在外的局外人。"
        "年報把它同時列在「美國市場品牌」與「國外主要競爭對手」——關係是競合。<br/>"
        "• <b>Stanley Black &amp; Decker（Mac／Proto／Facom／USAG）</b>：這是數泓最深的通道。優點是放量與認證一次做完；"
        "風險是 SBD 自己有 CDI Torque，隨時可雙源或內製。<br/>"
        "• <b>Tohnichi（東日）</b>：扭力計與工業鎖付的日本規格權威，實驗室與 ISO 話語權強，尤其半導體／日系車廠。"
        "數泓要進半導體，比的是精度、可追溯與日系供應商資格，不是 DIY 貨架。<br/>"
        "• <b>Stahlwille／Gedore／Hazet／Norbar</b>：歐洲專業工場。公司把「專業產品強化歐洲」當 2026 方針，"
        "代表這塊現在不是強項（2024 歐洲營收只有 5.0 千萬、8%）。<br/>"
        "• <b>中國電子扭力／低價 Amazon 品牌</b>：打 DIY 低價段。數泓用專業級占比提升來躲開，不是去拼 29.99 美元貨架。",
        s["body"],
    ))

    story.append(p("台灣聚落當全球競爭力來源", s["h2"]))
    story.append(p(
        "這是數泓最不像電子代工的一點。11 家股東把「網內互打」變成共同持股的數位化平台，"
        "讓一套電子模組可以接到活動扳手、套筒、起子、鋸子周邊的既有出口通道。"
        "經理人／今周刊把這稱為「11 家黑手打群架」。全球對手裡，很少有同等密度的金屬加工聚落可以在 50 公里內完成"
        "鍛造、熱處理、加工、電子組裝、校正、包裝。這是地理＋股權的雙重綁定，複製成本高。"
        "反面：決策是聯盟政治，擴產與降價未必像單一家族工廠那樣快。",
        s["body"],
    ))

    story.append(p("10. 風險清單（按對五年結果的殺傷力）", s["h1"]))
    story.append(p(
        "1. <b>客戶／品牌雙源</b>。ODM 96%。SBD 或 Lowe's 抽單或要求年降，營收與毛利同一季受傷。<br/>"
        "2. <b>美元與新台幣</b>。已在 2024／2025  empirically 驗證：本業可以創新高，稅後仍可以少 15% 或單季虧損。<br/>"
        "3. <b>美國關稅與貿易政策</b>。公司說 2025 影響輕；這句話的有效期是政策不變。手工具是傳統關稅標的。<br/>"
        "4. <b>北美 DIY 庫存週期</b>。2026 年 1 月營收年減 43% 是這個風險的實例。專業級占比上升是對沖，不是免疫。<br/>"
        "5. <b>技術規格被品牌內製或被中國追上</b>。無線協定、App、校準雲端都可被規格化採購。<br/>"
        "6. <b>半導體／醫療敘事落空</b>。試單延後是常態；若 2027 仍無經常性營收，樂觀情境關閉，估值回到「高殖利率代工」。<br/>"
        "7. <b>關鍵人與研發深度</b>。106 人、研發 11 人。總經理是工研院出身的技術靈魂；此規模沒有雙執行長備援的公開揭露。<br/>"
        "8. <b>流動性</b>。日成交常只有數張到數十張。再好的基本面，進出成本是另一件事——本報告不討論交易。",
        s["body"],
    ))

    story.append(p("11. 結論", s["h1"]))
    story.append(p(
        "數泓科近五年交出的成績單是：<b>一家不大、很會賺錢、現金會回來、成長靠一两次產品週期跳躍而不是平滑 CAGR 的利基製造商</b>。"
        "2021–2025 營收年複合成長約 9%；毛利率從 46% 走到 50%；本業營業利益 2025 年其實是新高。"
        "市場給的 12–15 倍本益比、4.6% 現金殖利率，反映的是「配息＋利基」而不是「半導體故事已經兌現」。",
        s["body"],
    ))
    story.append(p(
        "未來五年，產業本身大概只給中個位數的風。公司能不能明顯跑贏，取決於專業級與歐洲是否把北美 DIY 的 β 降下來，"
        "以及半導體／智慧鎖固能不能從新聞變成營收附註裡的產品別。全球競爭力的誠實位置："
        "<b>在品牌客戶的供應鏈裡是重要模組商，在終端技師的腦子裡幾乎不存在</b>。"
        "這個位置可以很舒服地再活五年（財務允許），但不會自動變成 Snap-on。"
        "把代工做成「客戶離不開的校準與資料層」是年報自己寫的戰略；目前唯一可驗證的進度是專業級出貨占比上升，其餘仍是計畫。",
        s["body"],
    ))
    story.append(p(
        "本報告不排序、不給目標價、不暗示買賣。若只留三個後續觀察點：① 每月營收是否能把 2026 累計年增轉正；"
        "② 專業級占比與歐洲營收比重；③ 2026 年底半導體試單是否在之後兩季變成可重複出貨。",
        s["quote"],
    ))

    story.append(p("附錄 A　月營收明細（仟元，HiStock）", s["h1"]))
    story.append(make_table(
        ["月", "2024", "YoY", "2025", "YoY", "2026", "YoY"],
        [
            ["1", "55,617", "+44.5%", "69,177", "+24.4%", "39,127", "−43.4%"],
            ["2", "53,738", "+44.9%", "51,255", "−4.6%", "47,421", "−7.5%"],
            ["3", "43,808", "+17.2%", "48,925", "+11.7%", "46,956", "−4.0%"],
            ["4", "47,406", "+38.9%", "44,411", "−6.3%", "51,071", "+15.0%"],
            ["5", "63,062", "+44.3%", "80,039", "+26.9%", "62,767", "−21.6%"],
            ["6", "44,930", "+25.3%", "57,256", "+27.4%", "64,273", "+12.3%"],
            ["7", "47,873", "+33.7%", "45,849", "−4.2%", "73,290", "+59.8%"],
            ["8", "51,542", "+10.2%", "38,032", "−26.2%", "—", "—"],
            ["9", "47,510", "−1.9%", "41,518", "−12.6%", "—", "—"],
            ["10", "50,100", "+39.6%", "44,097", "−12.0%", "—", "—"],
            ["11", "69,891", "+27.1%", "49,496", "−29.2%", "—", "—"],
            ["12", "46,429", "+47.0%", "56,179", "+21.0%", "—", "—"],
            ["全年/累計", "621,906", "+29.5%", "626,234", "+0.7%", "384,510*", "−3.1%"],
        ],
        s,
        col_widths=[18*mm, 24*mm, 22*mm, 24*mm, 22*mm, 24*mm, 22*mm],
    ))
    story.append(p("表 8　*2026 為 1–7 月累計。全年 2024／2025 與年報 621,907／626,234 差 1 仟元，屬進位。", s["caption"]))

    story.append(p("附錄 B　地區營收（年報，仟元）", s["h1"]))
    story.append(make_table(
        ["地區", "2021", "佔比", "2022", "佔比", "2023", "佔比", "2024", "佔比"],
        [
            ["北美", "206,309", "46.4%", "232,246", "51.8%", "285,362", "59.4%", "375,219", "60.3%"],
            ["台灣", "135,228", "30.4%", "122,430", "27.3%", "93,387", "19.5%", "131,812", "21.2%"],
            ["亞洲", "53,508", "12.0%", "51,476", "11.5%", "56,530", "11.8%", "53,094", "8.5%"],
            ["歐洲", "43,894", "9.9%", "35,795", "8.0%", "37,010", "7.7%", "49,955", "8.0%"],
            ["其他", "5,396", "1.2%", "6,816", "1.5%", "7,768", "1.6%", "11,827", "1.9%"],
            ["合計", "444,335", "100%", "448,763", "100%", "480,057", "100%", "621,907", "100%"],
        ],
        s,
        col_widths=[18*mm, 22*mm, 16*mm, 22*mm, 16*mm, 22*mm, 16*mm, 22*mm, 16*mm],
    ))
    story.append(p("表 9　2021 地區取上櫃前業績發表會（2022-09-13）與年報加總勾稽；2022–2024 取 112／113 年報。2025 地區別本輪未在已抓到的 114 致股東報告中完整列表。", s["caption"]))

    story.append(p("附錄 C　來源（每一類數字對得回哪裡）", s["h1"]))
    story.append(p(
        "• 公司年報 112／113 年度（eclatorq.com 股東會資訊；MOPS 同步）：損益、資產、地區、研發、市占分母、競爭對手名單、財務比率。<br/>"
        "• 114 年度致股東報告書（treelazy／年報轉載）：2025 營收 626,234、稅後 182,541、EPS 7.85、負債比 34.24%、流動比 277%、"
        "ROA 14.32%、ROE 20.48%、純益率 29.15%、研發 25,412、品牌 96:4、專業:DIY 52:48。<br/>"
        "• 2024 永續報告書：2022–2024 完整損益、員工 106、資本額、業務描述。<br/>"
        "• HiStock 季報／月營收／EPS／資產負債／現金流／除權息：時間序列；已用年報合計數勾稽。<br/>"
        "• 經濟日報／工商時報／聯合新聞網 2026-03、2026-08-11：H1 與 7 月營收、專業級 57%、半導體試單、匯兌說明。<br/>"
        "• nStock 公司小百科 2026-08-27：收盤 118.5、市值、7 月營收。<br/>"
        "• 經理人、今周刊、CENS、vocus 產業訪談：11 家股東故事、代工關係；不當成財務數字來源。<br/>"
        "• Strategic Market Research、Grand Research Store、Reanin、Grand View Research：僅用以顯示市場規模估計分歧。<br/>"
        "• PatSnap 公司頁：專利約 55 件（第三方爬梳，非專利局一次證明）。<br/>"
        "• 伯鑫 6904：HiStock 利潤比率、Win 投資／PChome 營收規模，作為傳統手工具對照，不是合併報表。",
        s["footnote"],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(p(
        "限制：本環境無 Augur 資料庫，2026Q2 資產負債取彙整站而非 XBRL 原檔；"
        "2021 年 HiStock 缺獨立 Q1，採 H1 解讀；前瞻段落為情境不是預測；"
        "商業顧問的全球市占表（例如把 Snap-on 數位扭力營收寫成數千萬美元）內部不一致，故不引用其排名百分比。",
        s["footnote"],
    ))
    story.append(p(
        "© 本 PDF 為 Augur 專案 [I] 研究產出，層級低於憲章與原則精華。禁止把本檔數字寫進任何 [N] 治理文書。",
        s["footnote"],
    ))
    return story


def render_pdf(path: Path) -> Path:
    register_font()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        charts = save_charts(Path(td))
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=14 * mm,
            rightMargin=14 * mm,
            topMargin=18 * mm,
            bottomMargin=14 * mm,
            title="6855 數泓科近五年財務分析與五年前景、全球競爭力",
            author="Augur [I] research (self-reported)",
        )
        s = styles()
        story = build_story(s, charts)
        def first_page(canvas, doc_):
            cover_page(canvas, doc_)
        def later(canvas, doc_):
            header_footer(canvas, doc_)
        doc.build(story, onFirstPage=first_page, onLaterPages=later)
    return path


def selftest() -> int:
    register_font()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        out = Path(f.name)
    try:
        register_font()
        doc = SimpleDocTemplate(str(out), pagesize=A4)
        s = styles()
        doc.build([p("selftest 數泓科 6855", s["body"])])
        size = out.stat().st_size
        if size < 1000:
            print(f"FAIL size={size}")
            return 1
        print(f"PASS font+pdf size={size}")
        return 0
    finally:
        out.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="渲染 6855 數泓科財務前景 PDF")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    out = render_pdf(OUT_PDF)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
