#!/usr/bin/env python3
"""產生 2801 彰銀近五年財務／前景 PDF 與下載頁。

🎯 讀報告定稿數字，輸出可下載 PDF＋HTML 落地頁（零外部 API）。
守原則精華 #1 #9 #15；本檔不打 FinMind／FRED。

執行指令矩陣：
  python3 scripts/build_chb2801_report_pdf.py              # 寫 reports/pdf/ 下 PDF＋index.html
  python3 scripts/build_chb2801_report_pdf.py --out DIR    # 指定輸出目錄
  python3 scripts/build_chb2801_report_pdf.py --selftest   # 暫存產出、驗 PDF 標頭／頁數／metadata（零外部）
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "reports" / "pdf"
PDF_NAME = "2801_changhwa_bank_5y_finance_outlook_20260827.pdf"
HTML_NAME = "index.html"
FONT_TTC = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_TTF = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

NAVY = "#1B365D"
GOLD = "#C4A35A"
INK = "#1F1E1D"
MUTED = "#5C584F"
PAPER = "#FBF8F1"
ROW = "#F3EEE3"
LINE = "#D9D1C3"


def _register_font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if os.path.isfile(FONT_TTC):
        pdfmetrics.registerFont(TTFont("CHBSans", FONT_TTC, subfontIndex=0))
        return "CHBSans"
    if os.path.isfile(FONT_TTF):
        pdfmetrics.registerFont(TTFont("CHBSans", FONT_TTF))
        return "CHBSans"
    raise FileNotFoundError("no CJK font")


def _styles(font: str):
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    base = getSampleStyleSheet()
    s = {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName=font, fontSize=11,
            textColor=HexColor(GOLD), alignment=TA_CENTER, tracking=1.2, spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Normal"], fontName=font, fontSize=26,
            textColor=white, alignment=TA_CENTER, leading=36, spaceAfter=10,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontName=font, fontSize=13,
            textColor=HexColor("#E8E0D0"), alignment=TA_CENTER, leading=20, spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Normal"], fontName=font, fontSize=14,
            textColor=HexColor(NAVY), spaceBefore=14, spaceAfter=8, leading=20,
            borderPadding=3,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Normal"], fontName=font, fontSize=12,
            textColor=HexColor(NAVY), spaceBefore=10, spaceAfter=6, leading=16,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName=font, fontSize=9.5,
            textColor=HexColor(INK), leading=16, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName=font, fontSize=9.5,
            textColor=HexColor(INK), leading=16, leftIndent=12, spaceAfter=4,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["Normal"], fontName=font, fontSize=9.5,
            textColor=HexColor(NAVY), leading=15, alignment=TA_LEFT, spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(MUTED), leading=12, spaceAfter=8, spaceBefore=2,
        ),
        "th": ParagraphStyle(
            "th", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=white, leading=11, alignment=TA_CENTER,
        ),
        "td": ParagraphStyle(
            "td", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(INK), leading=11, alignment=TA_CENTER,
        ),
        "td_l": ParagraphStyle(
            "td_l", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(INK), leading=11, alignment=TA_LEFT,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(MUTED), alignment=TA_LEFT,
        ),
        "footer_r": ParagraphStyle(
            "footer_r", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(MUTED), alignment=TA_RIGHT,
        ),
        "disc": ParagraphStyle(
            "disc", parent=base["Normal"], fontName=font, fontSize=8,
            textColor=HexColor(MUTED), leading=12, alignment=TA_JUSTIFY, spaceAfter=4,
        ),
    }
    return s


def _p(text: str, style):
    from reportlab.platypus import Paragraph
    return Paragraph(text.replace("\n", "<br/>"), style)


def _table(headers, rows, styles, col_widths):
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import Table, TableStyle

    head = [_p(h, styles["th"]) for h in headers]
    body = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            st = styles["td_l"] if i == 0 else styles["td"]
            cells.append(_p(str(c), st))
        body.append(cells)
    data = [head] + body
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor(NAVY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, -1), "CHBSans"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.3, HexColor(LINE)),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, HexColor(GOLD)),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), HexColor(ROW)))
        else:
            cmds.append(("BACKGROUND", (0, i), (-1, i), white))
    t.setStyle(TableStyle(cmds))
    return t


def _table_block(headers, rows, styles, col_widths, caption: str):
    from reportlab.platypus import KeepTogether
    return KeepTogether([
        _table(headers, rows, styles, col_widths),
        _p(caption, styles["caption"]),
    ])


def _hr():
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import HRFlowable
    return HRFlowable(width="100%", thickness=0.6, color=HexColor(GOLD), spaceBefore=4, spaceAfter=10)


class _Page:
    def __init__(self, font: str, styles):
        self.font = font
        self.styles = styles

    def __call__(self, canvas, doc):
        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import Paragraph

        canvas.saveState()
        w, h = A4
        if doc.page == 1:
            canvas.restoreState()
            return
        canvas.setFillColor(HexColor(NAVY))
        canvas.rect(0, h - 28, w, 28, fill=1, stroke=0)
        canvas.setFillColor(HexColor(GOLD))
        canvas.rect(0, h - 31, w, 3, fill=1, stroke=0)
        canvas.setFillColor(white)
        canvas.setFont(self.font, 8)
        canvas.drawString(18 * 2.834, h - 20, "2801 彰化銀行｜近五年財務與五年前景／全球競爭力")
        canvas.drawRightString(w - 18 * 2.834, h - 20, "觀點日 2026-08-27  ·  非投資建議")
        canvas.setFillColor(HexColor(PAPER))
        canvas.rect(0, 0, w, 22, fill=1, stroke=0)
        canvas.setFillColor(HexColor(NAVY))
        canvas.rect(0, 22, w, 2, fill=1, stroke=0)
        canvas.setFillColor(HexColor(MUTED))
        canvas.setFont(self.font, 7.5)
        canvas.drawString(18 * 2.834, 8, "[I] self-reported  ·  來源見末頁  ·  未使用 FinMind／FRED API")
        canvas.drawRightString(w - 18 * 2.834, 8, f"{doc.page}")
        canvas.restoreState()


def build_story(styles):
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    story = []
    mm_ = mm

    # —— cover is drawn in onFirstPage; body starts page 2 ——
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    story.append(_p("0. 一句話與聲明", styles["h1"]))
    story.append(_hr())
    story.append(_p(
        "<b>一句</b>：2021–2025 稅後淨利從 88 億走到 178 億、約翻倍；ROE 從 5.2% 升到 8.4%，"
        "仍低於 2025 年國銀平均 10.93%。2026 年前七月已賺 135 億、EPS 1.12 元，海外與財管是主引擎。"
        "它是公股中大型商銀，<b>不是</b>全球系統性銀行。",
        styles["callout"]))
    story.append(_p(
        "本報告為 Augur 領域 [I] 分析、self-reported，<b>不是進出場建議、目標價或可交易訊號</b>。"
        "銀行「營收」在公開彙整＝淨收益（利息淨收益＋利息以外淨收益）。EPS 用公司當年公告基本 EPS；"
        "股票股利會讓次一年度回溯稀釋。本雲端環境無 Augur DB、未打 FinMind／FRED API。",
        styles["disc"]))

    story.append(_p("1. 公司與資料範圍", styles["h1"]))
    story.append(_hr())
    story.append(_p(
        "彰化商業銀行（TWSE 2801）。1905 年於彰化創立，總行臺中，台灣現存最老商業銀行之一；"
        "<b>不是金融控股公司</b>。業務：存款、放款、外匯、信用卡、電子銀行、信託、財富管理、投資。"
        "流通股 11,766,046,253（2026-04-20）。財政部 12.19%、中華郵政 7.50%、國發基金 5.42%。"
        "政府機關持股合計 19.63%，金融機構 22.14%，外資 18.38%。",
        styles["body"]))
    story.append(_p(
        "收盤 2026-08-27：<b>24.70 元</b>（+3.35%）。以除權前股數粗算市值約 2,907 億。"
        "2026-08-05 除權息（現金 0.80＋股票 0.25）。Yahoo 本益比 14.06；2026Q1 每股淨值約 19.21 → "
        "PBR 約 1.29 倍。現金殖利率 0.80／24.70 ≈ 3.2%（股票股利不是現金）。",
        styles["body"]))

    src_rows = [
        ["年報／合併財報", "公司 IR、會計師查核／核閱", "2021–2025；2025Q3；2026Q1–Q2"],
        ["監理", "央行本國銀行營運績效·彰銀列", "2020–2024 年底資本、逾放"],
        ["法說", "2025 全年（2026-03）、2026H1（2026-08-25）", "至 2026 年 7 月自結"],
        ["產業", "惠譽、中華信評、央行／金管會國銀彙總", "2026–2027"],
        ["價／股利", "Yahoo、HiStock、財報狗", "除息 2026-08-05；價 2026-08-27"],
    ]
    story.append(_table_block(["層", "來源", "時點"], src_rows, styles, [32*mm_, 78*mm_, 60*mm_],
                              "表 1　資料範圍。未使用庫內 TaiwanStock* 列（本環境 DB 未掛載）。"))

    story.append(_p("2. 近五年損益：獲利翻倍，結構從投資轉向利差", styles["h1"]))
    story.append(_hr())
    is_rows = [
        ["2021", "286.86", "+5.0%", "101.20", "88.04", "0.84", "5.23%", "0.36%"],
        ["2022", "341.39", "+19.0%", "130.51", "109.71", "1.04", "6.44%", "0.42%"],
        ["2023", "385.70", "+13.0%", "162.37", "129.82", "1.20", "7.27%", "0.46%"],
        ["2024", "418.20", "+8.4%", "183.54", "149.45", "1.33", "7.68%", "0.49%"],
        ["2025", "453.10", "+8.4%", "211.17", "177.75", "1.51", "8.43%", "0.54%"],
        ["2026H1", "—", "—", "—", "113.14", "0.94", "—", "—"],
    ]
    story.append(_table_block(
        ["年", "淨收益", "年增", "稅前", "稅後", "EPS", "ROE", "ROA"],
        is_rows, styles, [18*mm_, 22*mm_, 20*mm_, 22*mm_, 22*mm_, 18*mm_, 20*mm_, 20*mm_],
        "表 2　單位億元／元。淨收益與 Money-link 五年表、HiStock 四季加總一致"
        "（2025 稅後 177.75＝36.24+50.21+49.95+41.35）。ROE／ROA 對 2024 年報與 2025 法說。",
    ))
    for t in [
        "<b>規模</b>：五年稅後 CAGR 約 19%，連續五年創新高。2022 淨收益年增近兩成，其後增速降到高個位數，但稅後仍 15–19%——費用與信用成本沒把利差吃掉。",
        "<b>2025 結構（法說）</b>：利息淨收益 271.06（+18.0%）、手續費 71.87（+4.7%）、投資淨收益 102.66（−12.6%）。利差變強、投資變弱，是比較可重複的組合。財管保險銷售年增近三成，財管手續費 +14%。",
        "<b>利差</b>：2025 NIM 0.92%、存放利差 1.27%（法說雙升）。公股商銀 NIM 長期偏薄，0.92% 仍薄，但方向對。",
        "<b>效率</b>：稅前／淨收益 2021 約 35% → 2025 約 47%。同一套資產，留下來的變多。",
        "<b>與國銀比</b>：2025 全體本國銀行平均 ROE 10.93%、ROA 0.77%（央行）。彰銀 8.43%／0.54% 是自己五年最好、同業中下段。立院預算中心：臺銀、土銀、彰銀這段期間 ROE 都低於同業平均。不要把「創高」讀成「已追上民營金控子行」。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))
    story.append(_p(
        "HiStock 單季淨收益：2026Q2 134.24 億、Q1 124.06 億，已高於 2025 任何一季。上半年不是季節噪音。",
        styles["body"]))

    story.append(_p("3. 2026 年進度：海外＋財管把增速再拉起來", styles["h1"]))
    story.append(_hr())
    story.append(_p("公司 2026-08-25 上半年法說（發言人莊政祺）：", styles["body"]))
    y26 = [
        ["2026Q1", "52.21", "+26.3%", "0.44", "股東會／法說"],
        ["2026H1", "113.14", "+23.9%", "0.94", "法說；HiStock Q1+Q2 相符"],
        ["2026 前七月", "135", "+22.4%", "1.12", "同場法說自結"],
    ]
    story.append(_table_block(["期間", "稅後（億）", "年增", "EPS", "來源"], y26, styles,
                             [32*mm_, 28*mm_, 24*mm_, 22*mm_, 64*mm_],
                             "表 3　2026 進度。"))
    for t in [
        "<b>放款（2026-06-30）</b>：整體營運量 2.1405 兆（+7.17%）。企金平均 1.1168 兆（+7.5%）；大企業 +10.8%、中小企業 +5.3%。台幣約 +5%、外幣約 +21%、海外放款 +26.3% 至 2,155 億。海外：歐美 47.3%（1,019 億）、亞洲不含南京 42.4%（915 億）、南京子行 10.3%（221 億）。授信口頭重點：半導體、AI／HPC、國防與戰略產業。",
        "<b>利差與品質（H1）</b>：存放利差 1.20%→1.30%，NIM 0.95%。逾放 0.15%、覆蓋率超過 900%（2025 年底 0.16%／836.89%）。",
        "<b>手續費（H1）</b>：50.06 億（+35.5%）；財管 39.26 億（+43.4%），佔近八成。高資產團隊累計服務逾 1,500 人；2026-03 開亞資中心高雄專區。顧問約 500 人、年內再加 40 人。",
        "<b>境外獲利</b>：H1 境外＋OBU 稅前（PPOP）35.37 億，佔比 24.2%（2024 約 11%、2025 年 23.9%）。前三大：香港、美國、英國。這是五年最重要的結構變化。",
        "<b>據點</b>：納閩分行暨吉隆坡行銷處 2026-08 揭牌；鳳凰城辦事處金管會已准、待美方；雪梨籌設；多倫多規劃。路徑是跟著台商供應鏈走，不是當地消費金融。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))
    story.append(_p(
        "公司對 2026 全年口頭「審慎樂觀」。3 月法說放款目標 3–5%；H1 已 +7%——不要把 3–5% 當天花板，也不要把 +7% 外推成五年 CAGR。",
        styles["body"]))

    story.append(_p("4. 資產負債、資本、資產品質", styles["h1"]))
    story.append(_hr())
    story.append(_p("4.1 規模", styles["h2"]))
    bs = [
        ["2021-12-31", "2.541 兆", "—", "—", "1,715 億", "個體"],
        ["2022-12-31", "2.670 兆", "1.666 兆", "—", "1,690 億", "個體"],
        ["2023-12-31", "2.901 兆", "1.803 兆", "2.476 兆", "—", "合併"],
        ["2024-12-31", "3.173 兆", "1.968 兆", "2.630 兆", "—", "合併年報"],
        ["2025-09-30", "3.355 兆", "2.014 兆", "2.677 兆", "—", "合併核閱"],
        ["2025-12-31", "3.38 兆", "放款量 +5.11%", "存款 +0.9%；存放比 77.11%", "2,203 億", "法說"],
    ]
    story.append(_table_block(["時點", "總資產", "放款淨額", "存款及匯款", "權益", "口徑"], bs, styles,
                             [28*mm_, 24*mm_, 32*mm_, 42*mm_, 24*mm_, 22*mm_],
                             "表 4　資產負債。2021–2022 為個體、其後合併；銀行母行佔比高，方向仍可比。"))
    story.append(_p(
        "五年資產從約 2.5 兆走到 3.4 兆（年增約 6–9%），穩健膨脹不是暴衝。2025 存款只 +0.9%（台幣 +4%、外幣 −8.2%），"
        "放款快過存款 → 存放比上升、利差較好養，但核心存款蒐集偏慢。2024 年底央行及同業存款從 2023 的 1,132 億跳到 2,343 億，批發資金依賴要盯。"
        "2025 年國銀資產前十：臺銀、中信、合庫、國泰世華、一銀、兆豐、北富銀、玉山、華南、土銀。<b>彰銀不在前十</b>。",
        styles["body"]))

    story.append(_p("4.2 資本（央行年底列）", styles["h2"]))
    cap = [
        ["2021", "14.97%", "12.09%", "10.46%", "6.31%", "13.82"],
        ["2022", "14.30%", "11.43%", "9.71%", "6.26%", "14.79"],
        ["2023", "14.21%", "11.59%", "9.98%", "6.29%", "14.33"],
        ["2024", "14.08%", "11.69%", "10.17%", "6.21%", "14.63"],
    ]
    story.append(_table_block(
        ["年底", "BIS", "T1", "CET1", "槓桿（T1／暴險）", "負債／權益（倍）"],
        cap, styles, [22*mm_, 26*mm_, 26*mm_, 26*mm_, 38*mm_, 34*mm_],
        "表 5　資本適足。夠法定、但沒有愈補愈厚——風險性資產成長略快於資本累積。"
        "2024Q3 法說：Moody’s A2／P-1／穩定（2024-03）、S&amp;P A／A-1／穩定（2023-12）。投資級、與多數公股商銀同帶。",
    ))

    story.append(_p("4.3 資產品質", styles["h2"]))
    npl = [
        ["2020", "0.38%", "335%"],
        ["2021", "0.33%", "387%"],
        ["2022", "0.20%", "638%"],
        ["2023", "0.18%", "693%"],
        ["2024", "0.16%", "797%"],
        ["2025（法說）", "0.16%", "837%"],
        ["2026-06（法說）", "0.15%", ">900%"],
    ]
    story.append(_table_block(
        ["時點", "逾放比", "覆蓋率"], npl, styles, [50*mm_, 50*mm_, 50*mm_],
        "表 6　2020–2024 為央行；2025–2026 為公司法說。多年度連續改善，不是單季化妝。"
        "惠譽對全體國銀：2026–2027 減損放款比可能從 0.7% 升到約 0.8%，主因在海外放款。"
        "彰銀海外放款正在 +26%——品質好與曝險變快是同一件事的兩面。",
    ))

    story.append(_p("5. 股利、評價、股價", styles["h1"]))
    story.append(_hr())
    div = [
        ["2021", "0.50", "0.10", "0.60", "0.84", "~71%"],
        ["2022", "0.55", "0.25", "0.80", "1.04", "~77%"],
        ["2023", "0.55", "0.32", "0.87", "1.20／回溯約 1.16", "~70%"],
        ["2024", "0.50", "0.50", "1.00", "年報 1.33；除權後常見 1.27", "~75–79%"],
        ["2025", "0.80", "0.25", "1.05", "1.51", "~70%"],
    ]
    story.append(_table_block(
        ["盈餘年", "現金", "股票", "合計", "當年 EPS", "配發粗算"],
        div, styles, [22*mm_, 22*mm_, 22*mm_, 22*mm_, 58*mm_, 24*mm_],
        "表 7　所屬年度→次年發放（Yahoo／財報狗）。連續 20 年配息。"
        "2024 年 0.50 股票＝面額 10 元之 5% 無償配股，會把前年 EPS 回溯變薄——1.33 與 1.27 並存不是兩套假帳。",
    ))
    story.append(_p(
        "股價（未還原、僅供位置感）：2021 除息前常見 17–18 元帶；2026-08-27 收 24.70。五年名目漲幅大約四成，加上現金股利總報酬高於股價線。"
        "本益比從長期個位數走入 13–15 倍（Yahoo 同業平均當日 13.39）——市場已把「獲利連創新高」部分付進去。"
        "14 倍不是便宜到可以不看風險，也不是泡沫。",
        styles["body"]))

    story.append(_p("6. 產業未來五年（約 2026–2030）", styles["h1"]))
    story.append(_hr())
    story.append(_p("這節是產業情景，不是彰銀保證會發生的事。", styles["body"]))
    for t in [
        "<b>需求</b>：惠譽 6 月將台灣 2026／2027 GDP 預測上修至 9.4%／4.8%，主引擎半導體／AI 出口與資本支出。中華信評估 2026 國銀放款年增約 8–9%；惠譽約 10%（對 2025 的 6%）。企業放款與海外借款是主軸；不動產放款受選擇性信用管制較悶。彰銀 H1 大企業＋海外的方向與產業風向同向。",
        "<b>利差</b>：美國降息循環仍在，台美利差收斂會打 FX swap（產業敘事有「少兩成」這個量級，不是彰銀自揭）。反向是美元資金成本下降、外幣放款需求上來。2025 國銀投資淨收益已較弱；利息＋手續費才是可延續的柱。中華信評估國銀稅前 ROAA 約 0.8%、第一類資本比近 13%。",
        "<b>競爭</b>：2025 稅前中信 669 億、國泰世華 518、北富銀 426、玉山 386；公股兆豐銀 333、一銀 315。彰銀稅前 211 億，約中信三分之一、玉山一半出頭。台新與新光銀行預計 2027 年初合併；惠譽把台新銀、永豐銀展望調正向。純網銀 2025 仍虧，短期不是獲利威脅，但是支付習慣的長期滲透。公股政策任務會繼續壓 ROE。",
        "<b>品質</b>：國銀 2025 年底逾放約 0.15%，亞太極低檔。惠譽基本情境 2026 減損放款比 0.8%、不利情境仍 &lt;1%。五年主風險不是國內房貸崩，而是海外授信加速 × 地緣（中東、兩岸、關稅）× 半導體資本支出若反轉。",
        "<b>基準（不是預測點）</b>：若 AI 資本支出延續、信用成本維持低檔，國銀獲利有機會在高位再走一段；若 2027 後 GDP 從 9% 掉回 4% 帶、利率中樞下移，淨利成長會從雙位數回到低中個位數。<b>不要用 2021–2025 的 19% CAGR 外推到 2030</b>。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))

    story.append(_p("7. 公司未來五年前景", styles["h1"]))
    story.append(_hr())
    story.append(_p(
        "公司 2026 主軸「展翅高飛、再創新局」：企金／個金雙軌；優結構、擴利差、深協作、穩體質。"
        "股東會另提：深耕客戶、數位／AI、核心存放款、風險、永續。高雄亞灣高資產中心＋生成式 AI 客服／風控是已宣布的執行項。",
        styles["body"]))
    scen = [
        ["基準", "海外放款由雙位數降到高個位數；財管不再每年 +40% 但仍正成長；NIM 守 0.9–1.0%；信用成本仍低",
         "稅後在 2025 的 178 億之上再墊高，增速從 2026 的 20% 帶降到個位數。ROE 挑戰站穩 9%、摸 10%"],
        ["樂觀", "鳳凰城／雪梨／多倫多開業且台商資本支出延續；高資產財管做過損益兩平；NIM 再升一檔",
         "境外佔比守住 25% 以上；EPS 有機會站上 2 元帶（須在股票股利稀釋後仍做得到）"],
        ["保守", "海外信用成本上升、NIM 被降息壓回、財管保險佣金反轉",
         "獲利停在 2025–2026 高位附近；現金股利難再從 0.80 往上跳；股價回歸息收"],
    ]
    story.append(_table_block(["情景", "假設", "2026–2030 意涵"], scen, styles, [22*mm_, 78*mm_, 70*mm_],
                             "表 8　self-reported 情景，非保證。"))
    story.append(_p("結構性約束（五年內很難消失）：", styles["body"]))
    for t in [
        "<b>不是金控</b>：保險、證券、投信交叉銷售比中信／國泰／富邦薄。財管是銀行保代＋信託，天花板低於金控。",
        "<b>公股治理與繳庫</b>：財政部仍是最大股東。穩健、資產品質、政策配合大於極大化 ROE。",
        "<b>數位與品牌</b>：中部／傳統商銀客群強；台北與年輕客的支付／數位帳戶對玉山、中信、國泰仍落後。AI 團隊是起跑，不是已完成的護城河。",
        "<b>資本</b>：CET1 約 10% 屬中等。放款若持續快於內生資本，要不增資、要降風險權重、要更倚股票股利——後者稀釋 EPS。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))
    story.append(_p(
        "<b>基準句</b>：未來五年比較像「把 2021–2025 這段修復再延長、並把海外與財管做成第二曲線」，"
        "不像「長成台灣的 DBS」。可驗證的領先指標：境外獲利佔比是否守住 20% 以上、NIM 是否掉回 0.8% 以下、"
        "逾放是否因海外離開 0.2% 以下、現金股利是否能留在 0.8 元附近而不是再掉回 0.5。",
        styles["callout"]))

    story.append(_p("8. 全球競爭力", styles["h1"]))
    story.append(_hr())
    story.append(_p(
        "先定尺：它<b>不是</b> G-SIB，不是亞洲區域全能銀行。總資產約 3.4 兆台幣（約 1,000 億美元量級），"
        "對上摩根大通、工銀、匯豐差一至兩個數量級；對上星展、華僑、瑞穗、國民銀行也明顯較小。"
        "國際評等 A／A2 是「台灣大型商銀投資級」，不是全球頂尖信用。",
        styles["body"]))
    for t in [
        "<b>台商跨境金融（正在加分的場）</b>：供應鏈重組把台廠資金需求帶到美國、東南亞、歐洲。海外放款歐美近半、亞洲（不含南京）四成。南京子行是少數公股先行登陸據點，兩岸政策是開關。鳳凰城（半導體走廊）、雪梨、多倫多、納閩＝地圖對準台商。這條路跟兆豐（外匯／聯貸）、一銀（海外台商）、中信（網絡更密）重疊——彰銀是追趕者，2024–2026 佔比跳升表示追趕有效，尚未證明已超車。",
        "<b>台灣中大型企金與中小企業</b>：中小企業 H1 仍 +5%，大企業更快。百年分行網的本業。全球競爭力弱，本土關係型放款仍在。",
        "<b>財富管理</b>：低基數高成長。全球私人銀行不在同一場；本土場上輸金控的產品架，但公股客群的信託／保險／傳承需求是真的。高雄亞灣地理對（南台灣高資產、半導體供應鏈），客群 1,500 人仍小。",
        "<b>數位與支付</b>：全球競爭力弱。台灣支付已被金控 App、純網銀、電商生態占領。五年翻盤機率低，目標是避免流失。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))
    story.append(_p(
        "<b>綜合評（self-reported）</b>：在「全球銀行業」分數低；在「服務全球台商的台灣公股商銀」分數中上、且 2024 起明顯改善。"
        "五年競爭力能否再升一格，取決於海外據點是否從「放款量」變成「當地可續的負債與中間業務」，以及信用成本會不會在放量後補一刀。",
        styles["callout"]))

    story.append(_p("9. 風險（已看到的）", styles["h1"]))
    story.append(_hr())
    for t in [
        "海外放款增速大於國內：惠譽點名的減損來源正好是這條。3 月法說稱中東新承作暫停，不代表歐美／亞洲沒有產業循環風險。",
        "NIM 仍薄（0.9x%），對降息與資金成本敏感。投資收益 2025 已年減 12.5%，不能再當穩定柱。",
        "非金控：手續費若保險佣金反轉，H1 財管 +43% 沒有集團其他引擎可補。",
        "股票股利持續稀釋 EPS 與每股指標。",
        "同業存款／批發資金 2024 明顯增加，核心存款成長偏慢。",
        "評價已反映復甦：本益比不再是極端的公股折價。",
        "公股人事、政策貸、兩岸據點都可能在選舉或兩岸情勢下變成約束。",
        "把單季高增速當五年 CAGR；把模型分數或均線當下單依據。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))

    story.append(_p("10. 來源", styles["h1"]))
    story.append(_hr())
    for t in [
        "彰銀 IR：2024 英文年報；2021–2024 與 2025Q3 財務報告 PDF；主要股東 2026-04-20；2024Q3 法說評等頁。",
        "2025 全年法說：工商時報 2026-03-18（淨收益 453.1、稅後 177.74、EPS 1.51、NIM 0.92%、NPL 0.16%、資產 3.38 兆、淨值 2,203 億）。",
        "2026 股東會：工商時報 2026-06-18（現金 0.80＋股票 0.25；Q1 稅後 52.21、EPS 0.44）。",
        "2026H1 法說：工商時報／自由／TVBS／鉅亨 2026-08-25（H1 113.14、前七月 135、EPS 1.12、放款 2.1405 兆、海外 +26.3%、NIM 0.95%、NPL 0.15%）。",
        "五年損益：Money-link；四季：HiStock（加總與年報一致）。股利：Yahoo 2801.TW、財報狗、HiStock。",
        "資本／逾放 2021–2024：央行本國銀行營運績效（彰化商業銀行列）。",
        "國銀 2025：央行稅前 5,819 億、ROE 10.93%、ROA 0.77%、逾放 0.15%；金管會個別行稅前排名。",
        "產業：惠譽 2026-07-21；中華信評放款 8–9%、ROAA 0.8%（工商時報 2026-07-11）。資產排名：央行 2025 年報新聞轉述。股價：Yahoo／HiStock 2026-08-27 收 24.70。",
    ]:
        story.append(_p("• " + t, styles["bullet"]))
    story.append(_p(
        "本環境 Augur PostgreSQL 未掛載，故未引用 TaiwanStockFinancialStatements 庫內列。"
        "若之後庫可用，應用金融業 type 碼（NetInterestIncome／ServiceFeeRevenueCommissionNet／EPS）重跑對帳，不以本檔回寫 raw。",
        styles["disc"]))
    return story


def _cover_page(canvas, doc, font: str):
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import A4

    w, h = A4
    canvas.saveState()
    canvas.setFillColor(HexColor(NAVY))
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(HexColor(GOLD))
    canvas.rect(0, h - 18, w, 18, fill=1, stroke=0)
    canvas.rect(0, 0, w, 18, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont(font, 9)
    canvas.drawCentredString(w / 2, h - 12, "AUGUR  [I]  ANALYSIS  ·  NOT INVESTMENT ADVICE")
    canvas.setFont(font, 11)
    canvas.setFillColor(HexColor(GOLD))
    canvas.drawCentredString(w / 2, h * 0.72, "TWSE 2801")
    canvas.setFillColor(white)
    canvas.setFont(font, 28)
    canvas.drawCentredString(w / 2, h * 0.64, "彰化銀行")
    canvas.setFont(font, 16)
    canvas.drawCentredString(w / 2, h * 0.58, "近五年財務分析")
    canvas.drawCentredString(w / 2, h * 0.54, "公司與產業未來五年前景")
    canvas.drawCentredString(w / 2, h * 0.50, "全球競爭力報告")
    canvas.setStrokeColor(HexColor(GOLD))
    canvas.setLineWidth(1.2)
    canvas.line(w * 0.28, h * 0.46, w * 0.72, h * 0.46)
    canvas.setFont(font, 11)
    canvas.setFillColor(HexColor("#E8E0D0"))
    canvas.drawCentredString(w / 2, h * 0.40, "觀點日　2026-08-27　收盤 24.70 元")
    canvas.drawCentredString(w / 2, h * 0.36, "財報至 2025 全年　進度至 2026 年 7 月自結")
    canvas.setFont(font, 9)
    canvas.drawCentredString(w / 2, h * 0.22,
                             "數字出自公司年報／法說、央行監理表、公開報價；分析層為 self-reported。")
    canvas.drawCentredString(w / 2, h * 0.19,
                             "本文件不構成買賣建議。未使用 FinMind／FRED API。")
    canvas.setFillColor(HexColor(NAVY))
    canvas.setFont(font, 8)
    canvas.drawCentredString(w / 2, 7, "Chang Hwa Commercial Bank  ·  five-year finance & outlook")
    canvas.restoreState()


def write_pdf(path: Path) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

    font = _register_font()
    styles = _styles(font)
    path.parent.mkdir(parents=True, exist_ok=True)
    page = _Page(font, styles)

    def first(c, d):
        _cover_page(c, d, font)

    def later(c, d):
        page(c, d)

    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="2801 Chang Hwa Bank 5-year finance and outlook",
        author="Augur [I] analysis (self-reported)",
        subject="TWSE 2801 financial analysis 2021-2025 and 5-year outlook",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=frame, onPage=first),
        PageTemplate(id="body", frames=frame, onPage=later),
    ])
    # first flowable is spacer+pagebreak so page 1 is cover only
    story = build_story(styles)
    # force body template after cover
    from reportlab.platypus.doctemplate import NextPageTemplate
    story.insert(0, NextPageTemplate("body"))
    doc.build(story)
    return path


def write_html(path: Path, pdf_href: str) -> Path:
    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>下載｜2801 彰銀近五年財務與前景報告</title>
<style>
:root {{ --navy:#1B365D; --gold:#C4A35A; --paper:#FBF8F1; --ink:#1F1E1D; --muted:#5C584F; }}
* {{ box-sizing:border-box }}
body {{ margin:0; font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;
  background:var(--paper); color:var(--ink); }}
.hero {{ background:var(--navy); color:#fff; padding:48px 24px 40px; text-align:center; }}
.hero small {{ color:var(--gold); letter-spacing:.12em; }}
.hero h1 {{ font-weight:600; font-size:28px; margin:12px 0 8px; }}
.hero p {{ color:#E8E0D0; margin:0 auto; max-width:640px; line-height:1.6; }}
.wrap {{ max-width:720px; margin:0 auto; padding:28px 20px 64px; }}
.card {{ background:#fff; border:1px solid #E5DCCB; border-radius:14px; padding:22px 22px 18px;
  box-shadow:0 8px 28px rgba(27,54,93,.06); }}
.btn {{ display:inline-block; background:var(--gold); color:var(--navy); font-weight:700;
  text-decoration:none; padding:14px 22px; border-radius:10px; margin:8px 8px 0 0; }}
.btn.alt {{ background:var(--navy); color:#fff; }}
.btn:hover {{ filter:brightness(1.05) }}
.meta {{ color:var(--muted); font-size:13px; line-height:1.55; margin-top:14px; }}
ul {{ line-height:1.7; padding-left:1.2em; }}
.disc {{ font-size:12px; color:var(--muted); margin-top:22px; line-height:1.55; }}
</style>
</head>
<body>
<header class="hero">
  <small>TWSE 2801　AUGUR [I]</small>
  <h1>彰化銀行｜近五年財務與五年前景</h1>
  <p>全球競爭力報告　·　PDF 可直接下載　·　觀點日 2026-08-27　·　不是投資建議</p>
</header>
<main class="wrap">
  <div class="card">
    <p>2021–2025 稅後淨利 88→178 億、約翻倍；ROE 5.2%→8.4%，仍低於國銀平均 10.93%。2026 年前七月 135 億、EPS 1.12。公股中大型商銀，不是全球系統性銀行。</p>
    <p>
      <a class="btn" href="{pdf_href}" download="{PDF_NAME}">下載 PDF 報告</a>
      <a class="btn alt" href="{pdf_href}" target="_blank" rel="noopener">在瀏覽器開啟 PDF</a>
    </p>
    <p class="meta">檔名：{PDF_NAME}<br>
    對應 markdown：<code>reports/augur_2801_chb_5y_finance_outlook_20260827.md</code></p>
  </div>
  <h2>報告內容</h2>
  <ul>
    <li>近五年損益、利差結構、與國銀平均比較</li>
    <li>2026 上半年／前七月：海外放款、財管、NIM、逾放</li>
    <li>資產負債、央行資本適足與資產品質</li>
    <li>股利與評價位置</li>
    <li>產業 2026–2030 與公司三情景</li>
    <li>全球競爭力定尺（台商跨境 vs 全球銀行）</li>
  </ul>
  <p class="disc">數字出自公司年報／法說、央行監理表與公開報價；分析層為 self-reported。
  本頁與 PDF 皆不構成買賣建議。未使用 FinMind／FRED API。</p>
</main>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def _page_count(data: bytes) -> int:
    import re
    return len(re.findall(rb"/Type\s*/Page(?![sA-Za-z])", data))


def selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        pdf = write_pdf(out / PDF_NAME)
        html = write_html(out / HTML_NAME, PDF_NAME)
        raw = pdf.read_bytes()
        assert raw.startswith(b"%PDF-"), f"not a PDF: {raw[:16]!r}"
        assert pdf.stat().st_size > 40_000, pdf.stat().st_size
        pages = _page_count(raw)
        assert pages >= 5, f"too few pages: {pages}"
        # metadata written by reportlab
        assert b"2801 Chang Hwa Bank" in raw, "missing document title metadata"
        assert html.is_file() and "下載 PDF" in html.read_text(encoding="utf-8")
        # red-path: empty file is not accepted as this builder's output
        bogus = out / "bogus.pdf"
        bogus.write_bytes(b"not-a-pdf")
        assert not bogus.read_bytes().startswith(b"%PDF-")
    print("selftest PASS  pages>=5  size>40k  title metadata present")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="2801 彰銀五年財務報告 PDF")
    p.add_argument("--out", default=str(DEFAULT_OUT), help="輸出目錄")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    out = Path(args.out)
    pdf = write_pdf(out / PDF_NAME)
    html = write_html(out / HTML_NAME, PDF_NAME)
    art = Path("/opt/cursor/artifacts")
    if art.is_dir():
        import shutil
        shutil.copy2(pdf, art / PDF_NAME)
        shutil.copy2(html, art / HTML_NAME)
    print(f"PDF  {pdf}  ({pdf.stat().st_size} bytes)")
    print(f"HTML {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
