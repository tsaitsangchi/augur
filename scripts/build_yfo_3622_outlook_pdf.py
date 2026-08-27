#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 3622 洋華近五年財務與未來五年前景／全球競爭力 PDF。

執行指令矩陣
  python3 scripts/build_yfo_3622_outlook_pdf.py
  python3 scripts/build_yfo_3622_outlook_pdf.py --selftest
守原則 #9 #10 #16
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from datetime import date
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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports"
PDF_NAME = "augur_3622_yfo_5y_finance_outlook_20260827.pdf"
HTML_NAME = "augur_3622_yfo_download.html"
MD_NAME = "augur_3622_yfo_5y_finance_outlook_20260827.md"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

NAVY = colors.HexColor("#0B1F3A")
NAVY2 = colors.HexColor("#16324F")
GOLD = colors.HexColor("#C4A35A")
TEAL = colors.HexColor("#1F6F6A")
CREAM = colors.HexColor("#F6F1E7")
PALE = colors.HexColor("#EEF3F7")
RED = colors.HexColor("#8B3A3A")
MUTED = colors.HexColor("#5A6570")
WHITE = colors.white

# 單位：新台幣百萬元（除 EPS／股利／比率外）。來源見報告附錄。
YEARS = [2021, 2022, 2023, 2024, 2025]
REV = [1449.3, 1545.6, 1639.0, 1577.3, 1725.6]
GP = [281.6, 408.2, 598.2, 723.8, 766.1]
OI = [54.1, 200.6, 356.5, 469.3, 483.4]
PRETAX = [264.5, 449.9, 584.6, 807.5, 1038.3]
NI_CO = [296.5, 433.9, 609.6, 769.9, 970.0]
NI_P = [279.4, 416.1, 567.5, 720.4, 921.6]
EPS = [1.85, 2.75, 3.75, 4.76, 6.09]
DPS = [1.20, 1.50, 2.00, 3.00, 3.20]
ASSETS = [6060.6, 6281.9, 7410.1, 8010.4, 8744.7]
EQUITY = [5283.5, 5652.7, 6637.5, 7251.0, 7878.1]
LIAB = [777.1, 629.2, 772.6, 759.4, 866.6]
OCF = [59.3, 444.4, 360.5, 637.9, 312.6]
ICF = [-45.0, 23.1, -106.5, -71.5, 35.2]
FCF_FIN = [-65.5, -345.1, -263.9, -328.8, -524.8]
BVPS = [34.56, 36.95, 43.31, 47.36, 51.53]
GM = [19.4, 26.4, 36.5, 45.9, 44.4]
OM = [3.7, 13.0, 21.7, 29.8, 28.0]
NM = [19.3, 26.9, 34.6, 45.7, 53.4]
ROE = [5.6, 7.6, 9.2, 10.4, 12.2]
LIAB_R = [12.8, 10.0, 10.4, 9.5, 9.9]


def _font():
    if "CJK" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CJK", FONT_PATH, subfontIndex=0))
    try:
        font_manager.fontManager.addfont(FONT_PATH)
    except Exception:
        pass
    fp = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [fp.get_name(), "WenQuanYi Micro Hei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return fp


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="CoverKicker", fontName="CJK", fontSize=10, textColor=GOLD, alignment=TA_CENTER, letterSpacing=1.2, spaceAfter=8))
    ss.add(ParagraphStyle(name="CoverTitle", fontName="CJK", fontSize=26, leading=34, textColor=WHITE, alignment=TA_CENTER, spaceAfter=10))
    ss.add(ParagraphStyle(name="CoverSub", fontName="CJK", fontSize=12, leading=18, textColor=CREAM, alignment=TA_CENTER, spaceAfter=6))
    ss.add(ParagraphStyle(name="H1", fontName="CJK", fontSize=16, leading=22, textColor=NAVY, spaceBefore=14, spaceAfter=8))
    ss.add(ParagraphStyle(name="H2", fontName="CJK", fontSize=13, leading=18, textColor=NAVY2, spaceBefore=10, spaceAfter=6))
    ss.add(ParagraphStyle(name="H3", fontName="CJK", fontSize=11.5, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=4))
    ss.add(ParagraphStyle(name="Body", fontName="CJK", fontSize=9.5, leading=15, textColor=NAVY, alignment=TA_JUSTIFY, spaceAfter=6))
    ss.add(ParagraphStyle(name="BulletBody", fontName="CJK", fontSize=9.5, leading=14.5, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2))
    ss.add(ParagraphStyle(name="Caption", fontName="CJK", fontSize=8, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=10))
    ss.add(ParagraphStyle(name="Foot", fontName="CJK", fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="Callout", fontName="CJK", fontSize=10, leading=15, textColor=NAVY, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="Cell", fontName="CJK", fontSize=8, leading=11, textColor=NAVY, alignment=TA_CENTER))
    ss.add(ParagraphStyle(name="CellL", fontName="CJK", fontSize=8, leading=11, textColor=NAVY, alignment=TA_LEFT))
    ss.add(ParagraphStyle(name="Disclaimer", fontName="CJK", fontSize=8, leading=12, textColor=RED, alignment=TA_JUSTIFY, spaceAfter=8))
    ss.add(ParagraphStyle(name="Source", fontName="CJK", fontSize=8, leading=12, textColor=MUTED, alignment=TA_LEFT, spaceAfter=3))
    ss.add(ParagraphStyle(name="TOC", fontName="CJK", fontSize=11, leading=18, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2))
    return ss


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 12 * mm, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 12.8 * mm, w, 0.8 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("CJK", 8)
    canvas.drawString(16 * mm, h - 8 * mm, "3622 洋華光電｜近五年財務分析與未來五年前景／全球競爭力")
    canvas.drawRightString(w - 16 * mm, h - 8 * mm, "2026-08-27")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 10 * mm, w, 0.6 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("CJK", 7.5)
    canvas.drawString(16 * mm, 4.2 * mm, "公開資料整理｜非投資建議｜self-reported")
    canvas.drawRightString(w - 16 * mm, 4.2 * mm, f"{doc.page}")
    canvas.restoreState()


def _cover_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 28 * mm, w, 8 * mm, fill=1, stroke=0)
    canvas.rect(0, 22 * mm, w, 2.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, w, 22 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("CJK", 9)
    canvas.drawCentredString(w / 2, 10 * mm, "資料時點 2026-08-27｜財報至 2026H1／月營收至 2026-07｜價 2026-08-26 收盤 53.10")
    canvas.restoreState()


def _p(text, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


def _table(data, col_widths, header=True):
    sty = [
        ("FONTNAME", (0, 0), (-1, -1), "CJK"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D5DDE5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ]
    if header:
        sty += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("BACKGROUND", (0, 1), (-1, 1), PALE),
        ]
        for i in range(2, len(data)):
            if i % 2 == 0:
                sty.append(("BACKGROUND", (0, i), (-1, i), CREAM))
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(sty))
    return t


def _callout(text, styles, bg=CREAM):
    inner = Paragraph(text, styles["Callout"])
    t = Table([[inner]], colWidths=[170 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 1.2, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def _style_ax(ax, fp):
    ax.title.set_fontproperties(fp)
    ax.xaxis.label.set_fontproperties(fp)
    ax.yaxis.label.set_fontproperties(fp)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fp)
    leg = ax.get_legend()
    if leg is not None:
        for t in leg.get_texts():
            t.set_fontproperties(fp)


def _charts(fp, tmp: Path) -> dict[str, Path]:
    paths = {}
    # 1 revenue / profit
    fig, ax = plt.subplots(figsize=(8.4, 3.6), dpi=140)
    x = list(range(len(YEARS)))
    w = 0.22
    ax.bar([i - 1.5 * w for i in x], REV, width=w, label="營收", color="#16324F")
    ax.bar([i - 0.5 * w for i in x], GP, width=w, label="毛利", color="#1F6F6A")
    ax.bar([i + 0.5 * w for i in x], OI, width=w, label="營業利益", color="#C4A35A")
    ax.bar([i + 1.5 * w for i in x], NI_P, width=w, label="母公司淨利", color="#8B3A3A")
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in YEARS], fontproperties=fp)
    ax.set_ylabel("百萬新台幣", fontproperties=fp)
    ax.legend(prop=fp, frameon=False, ncol=4, loc="upper left")
    ax.set_title("近五年損益規模", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_pnl.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["pnl"] = p

    # 2 margins
    fig, ax = plt.subplots(figsize=(8.4, 3.4), dpi=140)
    ax.plot(YEARS, GM, marker="o", color="#1F6F6A", label="毛利率")
    ax.plot(YEARS, OM, marker="s", color="#C4A35A", label="營業利益率")
    ax.plot(YEARS, NM, marker="D", color="#8B3A3A", label="母公司淨利率")
    ax.set_ylabel("%", fontproperties=fp)
    ax.legend(prop=fp, frameon=False)
    ax.set_title("獲利率走勢：本業改善、淨利率被業外放大", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_mgn.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["mgn"] = p

    # 3 bs
    fig, ax = plt.subplots(figsize=(8.4, 3.4), dpi=140)
    ax.bar(YEARS, EQUITY, label="權益", color="#16324F")
    ax.bar(YEARS, LIAB, bottom=EQUITY, label="負債", color="#C4A35A")
    ax.set_ylabel("百萬新台幣", fontproperties=fp)
    ax.legend(prop=fp, frameon=False)
    ax.set_title("資產結構：權益厚、負債極低", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_bs.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["bs"] = p

    # 4 cash
    fig, ax = plt.subplots(figsize=(8.4, 3.4), dpi=140)
    ax.bar([y - 0.25 for y in YEARS], OCF, width=0.25, label="營業現金", color="#1F6F6A")
    ax.bar(YEARS, ICF, width=0.25, label="投資現金", color="#C4A35A")
    ax.bar([y + 0.25 for y in YEARS], FCF_FIN, width=0.25, label="融資現金", color="#8B3A3A")
    ax.axhline(0, color="#333", linewidth=0.6)
    ax.set_ylabel("百萬新台幣", fontproperties=fp)
    ax.legend(prop=fp, frameon=False, ncol=3)
    ax.set_title("現金流量：本業有現金，融資端高配息流出", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_cf.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["cf"] = p

    # 5 eps dps
    fig, ax = plt.subplots(figsize=(8.4, 3.3), dpi=140)
    ax.bar([y - 0.18 for y in YEARS], EPS, width=0.36, label="EPS", color="#16324F")
    ax.bar([y + 0.18 for y in YEARS], DPS, width=0.36, label="現金股利（所屬年度）", color="#C4A35A")
    ax.set_ylabel("元／股", fontproperties=fp)
    ax.legend(prop=fp, frameon=False)
    ax.set_title("EPS 與現金股利同步墊高，配發率約五至六成", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_div.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["div"] = p

    # 6 competitiveness
    labels = [
        "台 69/161kV 電纜附件",
        "財務槓桿與現金",
        "台電計畫能見度",
        "越南＋1 產地彈性",
        "345kV／國際電網",
        "消費觸控全球",
        "電子紙模組全球",
        "本業規模／成長",
    ]
    scores = [8.5, 9.0, 7.5, 6.5, 3.0, 2.5, 3.5, 4.0]
    fig, ax = plt.subplots(figsize=(8.4, 3.8), dpi=140)
    colors_bar = ["#1F6F6A" if s >= 6 else "#C4A35A" if s >= 4 else "#8B3A3A" for s in scores]
    ax.barh(labels[::-1], scores[::-1], color=colors_bar[::-1])
    ax.set_xlim(0, 10)
    ax.set_xlabel("相對分數 0–10（本研究自評，非市場共識）", fontproperties=fp)
    for lab in ax.get_yticklabels():
        lab.set_fontproperties(fp)
    ax.set_title("全球／區域競爭力自評（越高越有優勢）", fontproperties=fp, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _style_ax(ax, fp)
    fig.tight_layout()
    p = tmp / "c_comp.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["comp"] = p
    return paths


def _img(path: Path, width=170 * mm):
    return Image(str(path), width=width, height=width * 0.42)


def build_story(styles, charts) -> list:
    S = styles
    story = []

    # cover content (drawn on navy by onFirstPage; we still put spacers + white text via colored paragraphs)
    story.append(Spacer(1, 42 * mm))
    story.append(_p("AUGUR 公開資料研究報告　｜　[I] 分析層　｜　self-reported", S["CoverKicker"]))
    story.append(_p("3622 洋華光電", S["CoverTitle"]))
    story.append(_p("近五年財務分析<br/>與公司／產業未來五年前景、全球競爭力", S["CoverTitle"]))
    story.append(Spacer(1, 8 * mm))
    story.append(_p("Young Fast Optoelectronics Co., Ltd.　TWSE: 3622", S["CoverSub"]))
    story.append(_p("機電（高壓電纜附件）× 光電（觸控／電子紙／整機）雙引擎", S["CoverSub"]))
    story.append(Spacer(1, 18 * mm))
    story.append(
        _p(
            "一句定錨：這是一家「台灣電網附件現金牛 ＋ 光電轉型事業 ＋ 厚金融資產／黃金部位」的混合體。"
            "近五年 EPS 從 1.85 升到 6.09，主要不是營收爆發，而是機電高毛利＋業外評價／租金／股利。"
            "未來五年勝負在台電強韌電網拉貨能延到何時，以及光電能否真正損平——不是全球消費電子龍頭賽道。",
            S["CoverSub"],
        )
    )
    story.append(PageBreak())

    # TOC / exec
    story.append(_p("0. 執行摘要", S["H1"]))
    story.append(
        _p(
            "本報告彙整公開資訊觀測站／公司官網月營收、合併財報、2025–2026 法說會、台電電網政策與電子紙／觸控產業第三方規模估計，"
            "對 3622 洋華光電（下稱洋華）做近五年財務剖析，並推估公司與所屬產業 2026–2030 前景與全球競爭位置。"
            "本地 Augur 資料庫本輪未連線；亦未呼叫 FinMind／FRED API。所有量化數字均可回溯至下列公開來源（見第 9 節）。"
            "本文件為研究整理、非投資建議、非目標價。",
            S["Body"],
        )
    )
    story.append(
        _callout(
            "<b>核心判斷（self-reported）</b><br/>"
            "1. <b>財務結構極強</b>：2025 年底負債比 9.9%、流動比逾 10 倍、每股淨值 51.53 元，接近淨現金／淨金融資產公司。<br/>"
            "2. <b>獲利品質必須拆開</b>：2025 營業利益 4.83 億，母公司淨利 9.22 億，約一半來自業外（金融資產／黃金評價、租金、股利、權益法）。"
            "2026Q2 本業仍賺 0.93 億，母公司 EPS 卻僅 0.01 元，顯示業外可正可負。<br/>"
            "3. <b>本業是台灣電網附件的區域冠軍，不是全球觸控冠軍</b>。69kV／161kV 終端匣與接續匣市占約 45%／55%（公司／法說口徑）；"
            "光電已退出消費手機主戰場，改做工控、博弈監視器、中大尺寸電子紙貼合。<br/>"
            "4. <b>未來五年基準情境</b>：機電靠台電 5,645 億強韌電網計畫看到約 2028–2032，在手訂單 30 億、年拉貨約 13 億；"
            "光電求損平與結構轉型。整體營收估落在 16–19 億區間震盪，EPS 高度取決於金融資產評價，不宜把 2025 的 6.09 元當常態本業地板。",
            S,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(_p("目錄", S["H2"]))
    toc = [
        "1. 公司定位與商業模式",
        "2. 近五年損益與獲利品質",
        "3. 資產負債、現金流與股利",
        "4. 2026 年進度（H1＋7 月）",
        "5. 產業未來五年前景",
        "6. 全球競爭力評分與對照",
        "7. 2026–2030 三情境",
        "8. 風險與觀察指標",
        "9. 資料來源與方法限制",
    ]
    for line in toc:
        story.append(_p(line, S["TOC"]))

    # 1
    story.append(_p("1. 公司定位與商業模式", S["H1"]))
    story.append(
        _p(
            "洋華光電股份有限公司，2002 年設立於桃園觀音，2008 年更名、2009 年上市。表面被分在「光電類股」，"
            "實際營收結構已翻轉：<b>2025 年機電約 82%、光電約 18%</b>（工商時報／2026-05-13 法說後報導）。"
            "把洋華當觸控面板成長股，會看錯主引擎。",
            S["Body"],
        )
    )
    story.append(_p("1.1 兩大事業", S["H2"]))
    story.append(
        _table(
            [
                ["構面", "機電事業群", "光電事業群"],
                [
                    Paragraph("產品", S["CellL"]),
                    Paragraph("69kV／161kV 電纜終端匣、接續匣、被覆保護裝置；345kV 精密金屬件代工起步", S["CellL"]),
                    Paragraph("投射式電容／電阻觸控、強化玻璃、EPD／ChLCD 貼合、Monitor／整機組裝", S["CellL"]),
                ],
                [
                    Paragraph("客戶", S["CellL"]),
                    Paragraph("台灣電線電纜廠 → 最終用戶以台電公共工程為主", S["CellL"]),
                    Paragraph("工控、類消費、車載、博弈機、運動器材標案", S["CellL"]),
                ],
                [
                    Paragraph("據點", S["CellL"]),
                    Paragraph("台灣觀音廠；2007 與日本 VISCAS（古河電工體系）合資掌握關鍵料件", S["CellL"]),
                    Paragraph("越南廠為光電生產基地（深耕約 11 年）；中國廠已停產、留售服", S["CellL"]),
                ],
                [
                    Paragraph("2026 公司口徑", S["CellL"]),
                    Paragraph("在手未執行訂單 30 億、年拉貨約 13 億、未來兩年產能近滿載；全年持平或微降", S["CellL"]),
                    Paragraph("博弈機監視器＋大尺寸運動器材帶動；目標損益兩平；電子紙量增但規模仍小", S["CellL"]),
                ],
                [
                    Paragraph("競爭本質", S["CellL"]),
                    Paragraph("台電合格名錄＋國產化門檻的區域寡占", S["CellL"]),
                    Paragraph("消費觸控已敗給 in-cell；改打利基組裝與貼合", S["CellL"]),
                ],
            ],
            [28 * mm, 71 * mm, 71 * mm],
        )
    )
    story.append(_p("表 1　雙事業定位（公司官網產品線＋2025-11／2026-05 法說整理）", S["Caption"]))

    story.append(_p("1.2 第三塊：資產配置公司的性格", S["H2"]))
    story.append(
        _p(
            "2026Q1 法說揭露：現金及定存 6.54 億、金融資產及權益法投資 50.59 億、黃金（FVTPL）8.86 億。"
            "對照當時市值約 80 億，金融資產＋黃金已接近市值七成。歷史上越南閒置廠出租、持有兆豐金／合庫金／第一金／台企銀等金融股股息，"
            "加上轉投資昀光（車用背光模組）權益法利益，使「本業 EPS」與「帳上 EPS」長期分叉。"
            "2025Q3 單季黃金評價利益約 1.32 億（法說），就是這種分叉的具體例子。",
            S["Body"],
        )
    )
    story.append(_p("1.3 沿革：為什麼看起來像光電股", S["H2"]))
    story.append(
        _p(
            "2007 年電阻／電容觸控放量，公司曾自稱全球最大觸控供應商，並與原機電主體合併，留下「光電」之名與上市分類。"
            "其後消費觸控被 on-cell／in-cell 與陸廠成本結構取代；越南廠原為跟隨三星布局，進展不如預期，多餘廠房改出租。"
            "機電反而是 2002 年就與古河電工技術合作、2005 年取得台電 69／161kV 合格資格的老本行。"
            "2022 年起電子紙全貼合、2024 年蓋板玻璃往上游整合、並投資陳虹光電合作監視器／整機，屬光電求生而非重返消費電子巔峰。",
            S["Body"],
        )
    )

    # 2
    story.append(_p("2. 近五年損益與獲利品質", S["H1"]))
    story.append(
        _p(
            "以下年度損益以公開季報加總交叉核對公司官網全年營收。單位新台幣百萬元。母公司淨利與 EPS 對齊 MoneyLink／stockanalysis 之歸屬母公司數。",
            S["Body"],
        )
    )
    story.append(
        _table(
            [
                ["年度", "2021", "2022", "2023", "2024", "2025", "五年CAGR"],
                ["營業收入", "1,449", "1,546", "1,639", "1,577", "1,726", "4.5%"],
                ["年增率", "56.4%*", "6.7%", "6.0%", "−3.8%", "9.4%", "—"],
                ["營業毛利", "282", "408", "598", "724", "766", "28.4%"],
                ["毛利率", "19.4%", "26.4%", "36.5%", "45.9%", "44.4%", "—"],
                ["營業利益", "54", "201", "356", "469", "483", "73%"],
                ["營業利益率", "3.7%", "13.0%", "21.7%", "29.8%", "28.0%", "—"],
                ["稅前淨利", "265", "450", "585", "807", "1,038", "40.7%"],
                ["母公司淨利", "279", "416", "568", "720", "922", "34.8%"],
                ["母公司淨利率", "19.3%", "26.9%", "34.6%", "45.7%", "53.4%", "—"],
                ["EPS（元）", "1.85", "2.75", "3.75", "4.76", "6.09", "34.7%"],
                ["業外佔稅前（估）", "80%", "55%", "39%", "42%", "53%", "—"],
            ],
            [36 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 24 * mm],
        )
    )
    story.append(_p("表 2　近五年合併損益。*2021 營收年增含低基期。業外佔稅前＝1−營業利益／稅前淨利（近似）。", S["Caption"]))
    story.append(_img(charts["pnl"]))
    story.append(_p("圖 1　營收幾乎走平，毛利／營業利益／淨利卻連續墊高。", S["Caption"]))
    story.append(_img(charts["mgn"]))
    story.append(_p("圖 2　毛利率 2021→2024 從 19% 跳到 46%，反映產品組合轉向高毛利機電。", S["Caption"]))

    story.append(_p("2.1 營收：規模沒有爆發", S["H2"]))
    story.append(
        _p(
            "五年營收在 14.5–17.3 億之間。2024 年減 3.8%，2025 年增 9.4% 回到 17.26 億（公司官網全年累計 1,725,633 千元）。"
            "這不是高成長故事。真正變的是<b>組合</b>：機電占比升到八成、毛利率翻倍以上。"
            "2024 年報自述：合併營收 1,577,292 千元、年減 3.76%；歸屬母公司淨利 720,443 千元、年增 26.94%；"
            "毛利與營業利益年增 21% 與 31.7%，主因高毛利機電與成本精簡。",
            S["Body"],
        )
    )
    story.append(_p("2.2 本業確實變好，但 2025 已接近平台", S["H2"]))
    story.append(
        _p(
            "營業利益 2021 年僅 0.54 億，2024 已 4.69 億，2025 再增至 4.83 億（＋3%），增速明顯放緩。"
            "毛利率 2025 年 44.4%、略低於 2024 的 45.9%。"
            "讀法：機電滿載後，增量來自產品組合與加班，公司自己說法說「一年約 2,500 項、加班能加的量有限」。"
            "本業獲利的下一個台階，取決於 345kV 國產化或光電損平，而不是再把 69／161kV 市占從 50% 再翻一倍——台灣市場就這麼大。",
            S["Body"],
        )
    )
    story.append(_p("2.3 獲利品質：淨利 ≠ 本業現金牛的全部", S["H2"]))
    story.append(
        _p(
            "2025 稅前 10.38 億、營業利益 4.83 億，業外約 5.55 億。淨利率 53% 在製造業極異常，必須當成「本業＋投資組合」的加總。"
            "2026Q2 提供反向證據：單季營收 4.22 億、營業利益 0.93 億仍正，稅前只剩 0.41 億，歸屬母公司淨利 116 萬、EPS 0.01 元。"
            "同季其他綜合損益 6.07 億（累計 4.16 億），顯示部分金融資產走 FVOCI、黃金等走 FVTPL，損益表與權益波動可以不同步。"
            "<b>分析 EPS 時至少拆三層：營業利益、FVTPL 評價、FVOCI／匯率 OCI。</b>可配息的是已實現＋依法可分配的保留盈餘，不是單季評價高峰。",
            S["Body"],
        )
    )
    story.append(
        _table(
            [
                ["季", "營收", "毛利率", "營業利益", "稅前", "稅後", "母公司EPS"],
                ["2025Q1", "374", "46.1%", "101", "220", "214", "1.34"],
                ["2025Q2", "436", "46.4%", "150", "155", "125", "0.75"],
                ["2025Q3", "484", "45.7%", "159", "446", "439", "2.80"],
                ["2025Q4", "431", "39.5%", "74", "217", "192", "1.20"],
                ["2026Q1", "363", "38.4%", "77", "174", "170", "1.09"],
                ["2026Q2", "422", "36.9%", "93", "41", "7", "0.01"],
            ],
            [28 * mm, 24 * mm, 24 * mm, 28 * mm, 22 * mm, 22 * mm, 22 * mm],
        )
    )
    story.append(_p("表 3　近六季：2025Q3 稅前被業外放大；2026Q2 業外反向把 EPS 打穿。單位百萬元。", S["Caption"]))

    # 3
    story.append(_p("3. 資產負債、現金流與股利", S["H1"]))
    story.append(_p("3.1 資產負債：幾乎無槓桿的資產管理體", S["H2"]))
    story.append(
        _table(
            [
                ["年底", "總資產", "總負債", "權益", "負債比", "流動比", "每股淨值"],
                ["2021", "6,061", "777", "5,283", "12.8%", "約8×*", "34.56"],
                ["2022", "6,282", "629", "5,653", "10.0%", "—", "36.95"],
                ["2023", "7,410", "773", "6,637", "10.4%", "1,077%", "43.31"],
                ["2024", "8,010", "759", "7,251", "9.5%", "1,245%", "47.36"],
                ["2025", "8,745", "867", "7,878", "9.9%", "1,067%", "51.53"],
                ["2026Q2", "9,317", "1,330", "7,987†", "14.3%", "650%", "52.17"],
            ],
            [26 * mm, 24 * mm, 24 * mm, 24 * mm, 22 * mm, 26 * mm, 24 * mm],
        )
    )
    story.append(
        _p(
            "表 4　單位百萬元。2026Q2 負債上升主因應付股利認列（季節性，H1 常見）。†權益＝資產−負債；歸屬母公司權益 7,895 百萬。"
            "*2021 流動比為資產／流動負債約略。2023–2025 流動比取年報／財務比率揭露。",
            S["Caption"],
        )
    )
    story.append(_img(charts["bs"]))
    story.append(_p("圖 3　五年資產＋2,684 百萬（＋44%），幾乎全來自權益累積與金融資產增值，而非舉債擴張。", S["Caption"]))
    story.append(
        _p(
            "2024 年報：長期資金占固定資產 862%、負債比 9.48%，流動／速動比 1,245%／1,171%。"
            "固定資產 2025 年底 7.77 億，低於流動資產 64.4 億——工廠不是資產主體，<b>流動資產與長期投資才是</b>。"
            "ROE 2023–2025 約 9.2%→10.4%→12.2%（母公司淨利／平均權益）。數字不差，但有一部分是金融資產市價幫忙把分子做大；"
            "分母（權益）同時被 OCI 推高，所以 ROE 沒有看起來那麼「經營超額」。",
            S["Body"],
        )
    )

    story.append(_p("3.2 現金流量：本業能吐現金，2025 營業現金掉一截", S["H2"]))
    story.append(
        _table(
            [
                ["年度", "營業現金", "投資現金", "融資現金", "母公司淨利", "營業現金／淨利"],
                ["2021", "59", "−45", "−66", "279", "0.21"],
                ["2022", "444", "23", "−345", "416", "1.07"],
                ["2023", "360", "−106", "−264", "568", "0.64"],
                ["2024", "638", "−72", "−329", "720", "0.89"],
                ["2025", "313", "35", "−525", "922", "0.34"],
            ],
            [28 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm, 30 * mm],
        )
    )
    story.append(
        _p(
            "表 5　現金流為 HiStock 單季加總（百萬元）。2025 營業現金 3.13 億遠低於淨利 9.22 億，符合大量未實現評價利益的圖像。"
            "融資現金持續大幅流出，對齊高現金股利。HiStock 的「自由現金流」把整筆投資現金流扣掉，含金融資產買賣，不宜當教科書 FCF。",
            S["Caption"],
        )
    )
    story.append(_img(charts["cf"]))
    story.append(_p("圖 4　2022–2024 營業現金強；2025 淨利創新高但營業現金回落——這是品質警訊，不是成長加速。", S["Caption"]))

    story.append(_p("3.3 股利與評價", S["H2"]))
    story.append(_img(charts["div"]))
    story.append(_p("圖 5　所屬年度現金股利 1.2→3.2 元；2025 配發率 3.2／6.09＝52.5%。", S["Caption"]))
    story.append(
        _table(
            [
                ["所屬年", "EPS", "現金股利", "配發率", "除息年", "除息前價", "當時現金殖利率"],
                ["2021", "1.85", "1.20", "64.9%", "2022", "29.60", "4.05%"],
                ["2022", "2.75", "1.50", "54.5%", "2023", "45.05", "3.33%"],
                ["2023", "3.75", "2.00", "53.3%", "2024", "60.70", "3.29%"],
                ["2024", "4.76", "3.00", "63.0%", "2025", "58.60", "5.12%"],
                ["2025", "6.09", "3.20", "52.5%", "2026/09/08", "49.80*", "6.43%*"],
            ],
            [24 * mm, 22 * mm, 24 * mm, 24 * mm, 28 * mm, 24 * mm, 24 * mm],
        )
    )
    story.append(_p("表 6　股利取 HiStock 除權息表。*2025 年度股利除息前價／殖利率為該表列示，除息日 2026-09-08。", S["Caption"]))
    story.append(
        _p(
            "股本約 15.13 億（1.513 億股）。2026-08-26 收盤 53.10、市值約 80.4 億（stockanalysis）；"
            "2026-08-27 HiStock 盤後 53.3。以 TTM EPS 5.10 計本益比約 10.4 倍；以 2025 EPS 6.09 計約 8.7 倍；"
            "股價淨值比約 53.1／52.17≈1.02 倍。2026 年 1–8 月本益比帶約 9–11 倍，低於 2021 的 20 倍以上（當時 EPS 基期低）。"
            "市場給的是「高資產、高股息、低成長」的控股／公用事業式倍數，不是成長股倍數。",
            S["Body"],
        )
    )

    # 4
    story.append(_p("4. 2026 年進度（截至 7 月）", S["H1"]))
    story.append(
        _table(
            [
                ["期間", "營收", "年增", "毛利率", "營益率", "母公司淨利", "EPS"],
                ["2025H1", "810", "+0.1%†", "46.2%", "30.9%", "316", "2.09"],
                ["2026H1", "785", "−3.1%", "37.6%", "21.6%", "166", "1.10"],
                ["2026Q1", "363", "−2.8%", "38.4%", "21.1%", "160*", "1.09"],
                ["2026Q2", "422", "−3.3%", "36.9%", "22.2%", "1.2", "0.01"],
                ["2026 1–7 月", "929", "−3.6%", "—", "—", "—", "—"],
            ],
            [32 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 26 * mm, 22 * mm],
        )
    )
    story.append(
        _p(
            "表 7　單位百萬元。月營收取公司官網；H1 財報取 2026-08-13 董事會通過之合併財報（營業收入 785,134 千元，EPS 1.10）。"
            "*Q1 母公司淨利取法說約 1.60 億。†2025H1 對 2024H1。",
            S["Caption"],
        )
    )
    story.append(
        _p(
            "公司 2026-05-12 法說：機電因台電上半年拉貨延遲，全年持平或微降，下半年補回；光電受博弈機監視器與大尺寸運動器材帶動、目標損平。"
            "法人整理（工商時報）：今年營收估小幅衰退，EPS 仍盼「半個股本以上」（≥5 元）——前提是業外不要像 Q2 那樣整季轉負。"
            "1–7 月營收年減 3.6%，與「小幅衰退」方向一致。毛利率從 46% 掉到 38%，是 2026 比 2025 更需要盯的本業變化"
            "（原物料、機電組合、光電出貨占比）。",
            S["Body"],
        )
    )

    # 5
    story.append(_p("5. 產業未來五年前景（2026–2030）", S["H1"]))
    story.append(_p("5.1 台灣輸配電與電纜附件：洋華真正的主場", S["H2"]))
    story.append(
        _p(
            "台電 2022-09 公布「強化電網韌性建設計畫」十年投入 <b>5,645 億元</b>：分散工程 4,379 億、強固 1,250 億、防衛 16.9 億；"
            "規劃新設 28 座變電所、24 座屋內化。政策起因是 2022-03-03 全台大停電。後續政治要求關鍵區域提前至約 2028 完成，"
            "161kV 交連 PE 電纜及附屬器材曾出現約 193 億的史上最大電纜標，由合機、宏泰、大山、華電、大亞、華新、華榮等線纜廠分食。"
            "洋華不直接賣電纜，而是賣線纜廠與工程端必須配套的<b>終端匣／接續匣／保護裝置</b>——電纜標越大，附件需求越穩。",
            S["Body"],
        )
    )
    story.append(
        _p(
            "法說補充：分散工程預算中約 40% 以上落在 2026–2032；至 2032 仍有變電所新建。公司在手 30 億訂單、年消化約 13 億，"
            "能見度大約兩年，不是十年鎖定。五年前景因此分成兩段：<b>2026–2028 執行加速段</b>（滿載、加班、毛利高但量難再翻倍）；"
            "<b>2029–2032 計畫尾聲段</b>（若無下一個國產化品項或外銷，機電營收有平台或緩降風險）。"
            "345kV 目前台灣幾乎全進口，洋華已替日本原廠代工精密金屬件（法說過往一年約 0.5 億），這是唯一對內的「升級敘事」，"
            "但要變成數億級營收仍須技術移轉與台電合格時程，不能當成已到手。",
            S["Body"],
        )
    )
    story.append(_p("5.2 觸控面板：結構性衰退的舊戰場", S["H2"]))
    story.append(
        _p(
            "外掛式（GG／GFF／OGS）觸控在手機、筆電已被 in-cell／on-cell 吃掉。全球平板觸控仍由 TPK、GIS、Nissha 等掌握六成以上，"
            "中國產能佔比過半、台灣約兩成（第三方市場報告口徑，僅作產業地圖、非洋華市占）。"
            "洋華已離開這個賽道的主戰場，轉工控／醫療／博弈／車載利基。利基市場穩、長尾、價格壓力較消費電子小，"
            "但總量不足以撐起一家曾以觸控成名的上市公司。未來五年觸控對洋華是<b>現金流維生＋組裝垂直整合的零件</b>，不是成長引擎。",
            S["Body"],
        )
    )
    story.append(_p("5.3 電子紙與中大尺寸模組：高成長賽道、洋華在組裝層", S["H2"]))
    story.append(
        _p(
            "電子紙第三方估計分歧大，必須並列、不得單取樂觀數：Mordor Intelligence 估 2025 年市場 29.9 億美元、2030 年 58.9 億、CAGR 14.5%；"
            "The Business Research Company 估 2025 年 57.2 億美元、2030 年 224.4 億、CAGR 31.3%。兩者差一個數量級，"
            "說明這個賽道的「全球規模」本身還不穩定，只能當方向不能當模型輸入。"
            "結構事實較清楚：<b>E Ink（8069）掌握薄膜與專利護城河</b>；2025-04 元太與友達子公司 AUO Display Plus 擬合資在龍科建大尺寸 EPD 模組線、"
            "資本額 3.9 億、友達系 51%／元太 49%、目標 2025Q4 量產。這直接打在「中大尺寸電子紙模組」這一層——也就是洋華正在轉型的那一層。",
            S["Body"],
        )
    )
    story.append(
        _p(
            "洋華的位置是貼合／前導光／中大尺寸模組與廣告／公車站牌／導覽看板，不是薄膜。法說：出貨量增、規模經濟仍需時間；"
            "Monitor＋電子紙合計希望佔光電部門 20% 以上。這是合理的利基策略，但面對元太＋友達的大尺寸合資，"
            "洋華全球競爭力是「可參與的二線組裝／利基客戶」，不是標準制定者。五年內若終端看板與零售電子紙放量，洋華可以吃到溢出訂單；"
            "若品牌商綁定元太—友達產能，溢出有限。",
            S["Body"],
        )
    )
    story.append(_p("5.4 博弈機監視器、運動器材標案、車用", S["H2"]))
    story.append(
        _p(
            "2026Q1 光電成長主因博弈機監視器穩定出貨與大尺寸運動器材標案。標案波動大，公司已提示延續性取決於客戶是否再得標。"
            "車用走 IATF16949，轉投資昀光做車用背光，屬權益法貢獻而非合併營收主體。這些線可以讓光電「少虧、接近損平」，"
            "五年內要成為十億級新引擎，證據不足。",
            S["Body"],
        )
    )
    story.append(_p("5.5 地緣：越南是光電的保單，不是機電的新大陸", S["H2"]))
    story.append(
        _p(
            "關稅與中國＋1 讓客戶詢問越南產能。洋華越南廠已在、可出租可自用，這是真實選擇權。但機電合格與台電體系綁在台灣，"
            "短期無法把 69／161kV 附件變成出口爆發。全球競爭力加分在「光電交貨地彈性」，不加分在「成為東南亞電網冠軍」。",
            S["Body"],
        )
    )

    # 6
    story.append(_p("6. 全球競爭力評分與對照", S["H1"]))
    story.append(_img(charts["comp"]))
    story.append(_p("圖 6　自評分數：強在台灣電網附件與資產負債，弱在全球顯示與超高壓。", S["Caption"]))
    story.append(
        _p(
            "全球競爭力不能用「光電類股」四個字概括。下面用產品層拆開。分數為本研究自評（0–10），不是第三方評等。",
            S["Body"],
        )
    )
    story.append(
        _table(
            [
                ["層級", "對手／標竿", "洋華位置", "五年走向"],
                [
                    Paragraph("69／161kV 附件（台灣）", S["CellL"]),
                    Paragraph("台電合格名錄內少數國產廠；日系原廠（古河／VISCAS、住友等）在超高壓與進口件", S["CellL"]),
                    Paragraph("69kV 市占約 45%、161kV 約 55%；國產化第一家雙電壓合格（公司沿革 2005）", S["CellL"]),
                    Paragraph("維持寡占、量受台電預算節奏限制；難再大幅擴市占", S["CellL"]),
                ],
                [
                    Paragraph("345kV／HVDC 附件（全球）", S["CellL"]),
                    Paragraph("Prysmian、Nexans、古河、住友、NKT、3M 等", S["CellL"]),
                    Paragraph("台灣幾乎無自製；洋華做日系精密金屬件代工，年約數千萬至低億", S["CellL"]),
                    Paragraph("若技術移轉＋合格，是唯一上一個電壓等級的門票；未合格前全球競爭力弱", S["CellL"]),
                ],
                [
                    Paragraph("消費觸控", S["CellL"]),
                    Paragraph("TPK、GIS、歐菲光、Nissha、京東方體系內製", S["CellL"]),
                    Paragraph("已退出手機主戰場，剩餘工控／利基外掛式", S["CellL"]),
                    Paragraph("全球份額可忽略；不再是競爭維度", S["CellL"]),
                ],
                [
                    Paragraph("電子紙模組", S["CellL"]),
                    Paragraph("E Ink 薄膜壟斷；友達—元太大尺寸合資；OED、漢王、各模組廠", S["CellL"]),
                    Paragraph("中大尺寸貼合／前導光，客戶利基", S["CellL"]),
                    Paragraph("賽道成長、洋華吃組裝層溢出；標準與材料不在手上", S["CellL"]),
                ],
                [
                    Paragraph("整機／博弈／工控顯示", S["CellL"]),
                    Paragraph("台灣中小型組裝與陸廠", S["CellL"]),
                    Paragraph("與陳虹合作、觀音產能、垂直整合蓋板到整機", S["CellL"]),
                    Paragraph("可改善光電損平；全球品牌力弱、看個別客戶", S["CellL"]),
                ],
            ],
            [32 * mm, 46 * mm, 46 * mm, 46 * mm],
        )
    )
    story.append(_p("表 8　分層競爭地圖。市占數字為公司／法說／媒體引述之台灣市場口徑，非全球。", S["Caption"]))

    story.append(_p("6.1 SWOT（五年視線）", S["H2"]))
    story.append(
        _table(
            [
                ["優勢 S", "劣勢 W"],
                [
                    Paragraph("台電雙電壓合格＋與古河體系合資；台灣 69／161kV 附件領先；負債極低、流動性極高；高現金股利文化；越南產地選擇權；機電 ISO14001／45001、光電 IATF16949", S["CellL"]),
                    Paragraph("合併營收只有十餘億，固定成本與上市殼相對重；光電長期虧損或僅求損平；本業產能滿載後增量有限；獲利被金融資產綁住，EPS 波動像投資公司；研發／品牌在全球顯示鏈弱", S["CellL"]),
                ],
                ["機會 O", "威脅 T"],
                [
                    Paragraph("強韌電網執行加速至 2028；345kV 國產化；中大尺寸彩色電子紙（Spectra 6 等）看板需求；關稅驅動非中國組裝；昀光車用背光若持續成長", S["CellL"]),
                    Paragraph("台電預算政治化或工程延宕（2026H1 已發生拉貨延遲）；計畫 2030 前後週期尾聲；金價／金融股反轉（2026Q2 已示範）；元太—友達大尺寸模組擠壓；原物料與膠體成本；光電客戶標案斷檔", S["CellL"]),
                ],
            ],
            [85 * mm, 85 * mm],
        )
    )
    story.append(_p("表 9　SWOT。機會項都還不是財報主體；威脅項有些已在 2026 上半年出現。", S["Caption"]))

    story.append(_p("6.2 一句全球定位", S["H2"]))
    story.append(
        _callout(
            "洋華不是全球觸控或電子紙的冠軍選手，而是<b>台灣輸配電關鍵附件的在地冠軍</b>，外掛一個正在縮減虧損的利基光電組裝廠，"
            "再外掛一個規模接近市值的金融資產／黃金組合。以全球競爭力語言：在 69／161kV 冷縮附件這個窄門裡，它有區域定價權；"
            "一出這個窄門（消費顯示、超高壓系統、海外電網總包），它是追隨者。五年策略若走「守住窄門、試探 345kV、光電損平、資產穩配息」，"
            "與它的能力稟賦一致。若敘事改寫成「全球電子紙成長股」，證據不足。",
            S,
        )
    )

    # 7
    story.append(_p("7. 2026–2030 三情境（不是目標價）", S["H1"]))
    story.append(
        _p(
            "以下為情境框架，用來組織已看見的驅動因子，<b>不是預測、不是目標價、不是進出場建議</b>。"
            "營收以合併營業收入計；EPS 含業外，故給區間而非點值。",
            S["Body"],
        )
    )
    story.append(
        _table(
            [
                ["", "保守", "基準", "樂觀"],
                [
                    Paragraph("機電", S["CellL"]),
                    Paragraph("台電拉貨持續延、2028 後計畫空窗；年營收落到低於 12 億", S["CellL"]),
                    Paragraph("在手 30 億消化完後仍有接續標；年拉貨 12–14 億維持至約 2029", S["CellL"]),
                    Paragraph("加速完工＋345kV 合格貢獻放量；機電站穩 15 億以上", S["CellL"]),
                ],
                [
                    Paragraph("光電", S["CellL"]),
                    Paragraph("標案斷、電子紙放量失敗，部門續虧、拖累毛利率", S["CellL"]),
                    Paragraph("2026–27 接近損平；Monitor＋電子紙佔光電 ≥20%", S["CellL"]),
                    Paragraph("損平後轉正，光電佔合併營收回升到 25–30%", S["CellL"]),
                ],
                [
                    Paragraph("業外", S["CellL"]),
                    Paragraph("金價／金融股回檔，評價利益轉損失（Q2 型）", S["CellL"]),
                    Paragraph("租金＋股利穩定，評價有正有負、多年互抵", S["CellL"]),
                    Paragraph("金融資產續漲，淨利再與本業脫鉤創新高", S["CellL"]),
                ],
                [
                    Paragraph("合併營收（約）", S["CellL"]),
                    Paragraph("14–16 億", S["CellL"]),
                    Paragraph("16–19 億", S["CellL"]),
                    Paragraph("20–24 億", S["CellL"]),
                ],
                [
                    Paragraph("本業營業利益", S["CellL"]),
                    Paragraph("2.5–3.5 億", S["CellL"]),
                    Paragraph("4–5.5 億", S["CellL"]),
                    Paragraph("6 億以上", S["CellL"]),
                ],
                [
                    Paragraph("EPS 區間", S["CellL"]),
                    Paragraph("1.5–3.5 元（評價虧損年）", S["CellL"]),
                    Paragraph("4–6 元", S["CellL"]),
                    Paragraph("＞6 元（需業外幫忙）", S["CellL"]),
                ],
                [
                    Paragraph("配息", S["CellL"]),
                    Paragraph("仍配、但可能降到 2 元以下", S["CellL"]),
                    Paragraph("維持約五至六成、2.5–3.5 元", S["CellL"]),
                    Paragraph("3.5 元以上", S["CellL"]),
                ],
            ],
            [28 * mm, 47 * mm, 47 * mm, 48 * mm],
        )
    )
    story.append(_p("表 10　五年情境。基準機率最高，因為在手訂單與台電計畫是已揭露事實；樂觀需要 345kV 或光電轉正兩件新事實。", S["Caption"]))
    story.append(
        _p(
            "對照 2026 已發生：H1 營收年減 3%、毛利率下滑、Q2 EPS 0.01，落點暫時偏基準偏下、靠近保守的「業外負向」子集。"
            "下半年台電是否補貨，是 2026 全年能否留在基準的關鍵開關。",
            S["Body"],
        )
    )

    # 8
    story.append(_p("8. 風險與觀察指標", S["H1"]))
    bullets = [
        "單季 EPS 與 OCI 大幅背離：評價科目主導時，不要用年化 EPS 推估值。",
        "機電在手訂單與年拉貨：30 億／13 億是 2026-05 法說數字，需看後續法說有無下滑。",
        "毛利率能否守住 38% 以上：2026H1 已從 46% 掉到 38%，若落到 30% 以下，本業故事要重寫。",
        "光電能否在 2026–2027 損平：公司自己設的目標；連續虧損則垂直整合只是費用。",
        "345kV 合格與出貨金額：從「代工 0.5 億」變成「自有合格產品」才算升級。",
        "黃金與金融資產占比：FVTPL 8.86 億（2026Q1）在金價波動時足以打穿單季本業。",
        "台電預算與工程進度的政治風險：電價補貼與電網計畫被混著砍的敘事，公司認為計畫本身不受影響，仍需追蹤決標。",
        "元太—友達大尺寸 EPD 合資量產進度：直接競爭光電新業務。",
        "越南廠客戶從詢問到量產的轉換率：詢問≠營收。",
        "配發率與營業現金流比：2025 營業現金／淨利僅 0.34，若連續兩年，高配息要吃存量現金或賣金融資產。",
    ]
    items = [ListItem(Paragraph(b, S["BulletBody"]), leftIndent=8, bulletColor=GOLD) for b in bullets]
    story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=12, bulletFontName="CJK"))

    # 9
    story.append(_p("9. 資料來源、方法與限制", S["H1"]))
    story.append(
        _p(
            "本報告為 self-reported 研究整理（工具層規則：AI 產出不得當作世界已證實的權威）。"
            "本地 PostgreSQL 本輪無連線，故不引用 Augur 庫內列；亦未呼叫 FinMind／FRED。"
            "數字只來自下列公開通道。跨來源衝突時，優先公司官網月營收與董事會／股東會通過之合併財報，其次法說逐字，再次媒體整理。",
            S["Body"],
        )
    )
    story.append(_p("主要來源", S["H2"]))
    srcs = [
        "公司官網月營收 https://www.yfo.com.tw/revenue_tw.php（2022-01 至 2026-07 全年／累計）。",
        "公司沿革／產品線 https://www.yfo.com.tw/（2002 古河合作、2005 台電合格、2007 合併與 VISCAS 合資、2009 上市、2022 電子紙、2024 蓋板玻璃）。",
        "2026-08-13 董事會通過 2026H1 合併財報（MoneyDJ 轉公開資訊觀測站：營收 785,134 千元、EPS 1.10、資產 9,317,460 千元）。",
        "MoneyLink 近五年營收／稅前／稅後／EPS；2026Q2 同業比較毛利率。",
        "HiStock 損益表、資產表、負債權益、現金流量、EPS、每股淨值、除權息、本益比。",
        "stockanalysis.com TPE:3622 損益／市值／TTM（2026-08-26 收盤 53.10、市值 81.0 億、TTM 營收 17.01 億、TTM EPS 5.10）。",
        "2024 年報財務分析摘要（treelazy 轉載：負債比 9.48%、流動比 1,244.89%、ROE 10.37%、純益率 48.81%）。",
        "法說：2025-11-18（富果整理）、2026-05-12（BigGo／工商時報／Yahoo 股市）。",
        "中央社 2020-08-28 越南廠架構；2022-09-15 台電 5,645 億電網計畫。",
        "電子紙：Mordor Intelligence；The Business Research Company／Research and Markets；友達 2025-04-02 合資公告。",
        "觸控產業集中度：第三方平板觸控市場概述（TPK／GIS／Nissha）。",
    ]
    items = [ListItem(Paragraph(b, S["Source"]), leftIndent=6, bulletColor=MUTED) for b in srcs]
    story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=10, bulletFontName="CJK"))

    story.append(_p("已知衝突與處理", S["H2"]))
    story.append(
        _p(
            "部分二手法說摘要把 2025 全年營收寫成 7.26 億，與公司官網 17.26 億、MoneyLink 1,726 百萬衝突。"
            "本報告判定 7.26 億為 1,726 百萬之誤讀（漏掉「十」），以官網 1,725,633 千元為準。"
            "2025 前三季「營收 12.95 億」與官網 1–9 月 12.95 億相符，不能拿去推翻全年 17.26 億。",
            S["Body"],
        )
    )
    story.append(_p("限制", S["H2"]))
    story.append(
        _p(
            "無逐線分割的正式部門別財報（機電／光電營業利益未全面公開）；業外細項（黃金 vs 股利 vs 租金 vs 權益法）僅有法說片段；"
            "全球電子紙規模估計分歧；台灣附件市占為公司口徑、無獨立稽核市調；"
            "現金流量採季報加總，與會計師簽證年報可能有重分類差異。"
            "未做現場訪廠、未訪談供應鏈、未取得未公開內部預測。",
            S["Body"],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        _p(
            "免責：本文件僅供研究與討論，不構成證券買賣、信託或任何投資建議。過去獲利、股利與市占不保證未來。",
            S["Disclaimer"],
        )
    )
    story.append(
        _p(
            f"編製：Augur 研究整理　｜　日期：{date.today().isoformat()}　｜　檔名：{PDF_NAME}",
            S["Source"],
        )
    )
    return story


def write_html(pdf_name: str, path: Path) -> None:
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>下載｜3622 洋華近五年財務與前景報告</title>
  <style>
    body {{ font-family: "Noto Sans CJK TC", "Microsoft JhengHei", sans-serif; background:#0B1F3A; color:#F6F1E7; margin:0; }}
    main {{ max-width: 720px; margin: 12vh auto; padding: 32px; background:#16324F; border-top: 6px solid #C4A35A; }}
    h1 {{ margin-top:0; font-size: 1.6rem; }}
    a.btn {{ display:inline-block; margin-top:18px; padding:12px 22px; background:#C4A35A; color:#0B1F3A;
             text-decoration:none; font-weight:700; }}
    a.btn:hover {{ background:#e0c07a; }}
    p {{ line-height:1.6; color:#d9e2ea; }}
    .note {{ font-size: .85rem; color:#9aa8b5; }}
  </style>
</head>
<body>
  <main>
    <p class="note">AUGUR 公開資料研究　｜　self-reported　｜　非投資建議</p>
    <h1>3622 洋華光電<br/>近五年財務分析與未來五年前景／全球競爭力</h1>
    <p>PDF 已產生。點下方按鈕即可下載（約數百 KB）。</p>
    <a class="btn" href="{pdf_name}" download="{pdf_name}">下載 PDF 報告</a>
    <p class="note" style="margin-top:24px">若瀏覽器未觸發下載，請對連結按右鍵「另存連結」。資料時點 2026-08-27。</p>
  </main>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def write_markdown(path: Path) -> None:
    path.write_text(
        f"""---
title: 3622 洋華近五年財務與產業前景／全球競爭力
date: 2026-08-27
stock_id: "3622"
layer: "[I]"
self_reported: true
price_tip: 2026-08-26
fs_tip: 2026-06-30
not_advice: true
pdf: {PDF_NAME}
---

# 3622 洋華光電｜近五年財務分析與未來五年前景、全球競爭力

> **一句**：這是「台灣電網附件現金牛 ＋ 光電轉型 ＋ 厚金融資產／黃金」的混合體。五年 EPS 1.85→6.09，主因機電高毛利與業外，不是營收爆發。  
> **PDF**：[`{PDF_NAME}`]({PDF_NAME})　下載頁：[`{HTML_NAME}`]({HTML_NAME})  
> **不是**：進出場建議或目標價。

完整圖表、三情境與競爭力評分見 PDF。本 md 只留可追溯的數字骨架。

## 近五年損益（百萬新台幣）

| 年 | 營收 | 毛利率 | 營益率 | 母公司淨利 | 淨利率 | EPS | 現金股利 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 1,449 | 19.4% | 3.7% | 279 | 19.3% | 1.85 | 1.20 |
| 2022 | 1,546 | 26.4% | 13.0% | 416 | 26.9% | 2.75 | 1.50 |
| 2023 | 1,639 | 36.5% | 21.7% | 568 | 34.6% | 3.75 | 2.00 |
| 2024 | 1,577 | 45.9% | 29.8% | 720 | 45.7% | 4.76 | 3.00 |
| 2025 | 1,726 | 44.4% | 28.0% | 922 | 53.4% | 6.09 | 3.20 |

2025 全年營收以公司官網 1,725,633 千元為準（否決二手法說誤植的 7.26 億）。

## 2026 進度

- H1 營收 785,134 千元（−3.1%）、毛利率 37.61%、EPS 1.10。Q2 母公司 EPS 0.01。
- 1–7 月營收 929,046 千元（−3.56%）。
- 2026-08-26 收盤 53.10；TTM EPS 約 5.10；P/B 約 1.02；2025 股利 3.2 元。

## 前景一句

基準：機電吃台電 5,645 億強韌電網看到約 2028–2032，在手 30 億／年拉約 13 億；光電求損平。全球競爭力強在台灣 69／161kV 附件寡占，弱在消費觸控與電子紙材料層。

來源與限制見 PDF 第 9 節。
""",
        encoding="utf-8",
    )


def selftest() -> int:
    assert abs(sum(REV) / 5 - 1587.36) < 1
    assert PDF_NAME.endswith(".pdf")
    assert Path(FONT_PATH).is_file()
    print("selftest ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fp = _font()
    styles = _styles()
    with tempfile.TemporaryDirectory() as td:
        charts = _charts(fp, Path(td))
        pdf_path = OUT_DIR / PDF_NAME
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=16 * mm,
            title="3622 洋華光電｜近五年財務分析與未來五年前景／全球競爭力",
            author="Augur research (self-reported)",
        )
        story = build_story(styles, charts)
        doc.build(story, onFirstPage=_cover_page, onLaterPages=_header_footer)

    write_html(PDF_NAME, OUT_DIR / HTML_NAME)
    write_markdown(OUT_DIR / MD_NAME)
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size} bytes)")
    print(f"wrote {OUT_DIR / HTML_NAME}")
    print(f"wrote {OUT_DIR / MD_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
