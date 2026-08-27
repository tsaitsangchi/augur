#!/usr/bin/env python3
"""產生 6690 安碁資訊近五年財務與產業前景 PDF。

🎯 這支在做什麼（白話）：把已交叉核對的公開財報／產業數字編成 A4 繁中 PDF
   （含圖表），寫入 reports/，並複製一份到 downloads/ 供下載。不打 FinMind／FRED。
守原則精華 #1 #9 #10 #15。

執行指令矩陣：
  python3 scripts/build_6690_acsi_report_pdf.py
      # 產出 reports/augur_6690_acsi_5y_finance_outlook_20260827.pdf
  python3 scripts/build_6690_acsi_report_pdf.py --out /tmp/acsi.pdf
  python3 scripts/build_6690_acsi_report_pdf.py --selftest
      # 零外部依賴：CAGR 純函式真輸入＋產出 PDF 魔術碼／頁數
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
FONT_PATH = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
DEFAULT_OUT = REPO / "reports" / "augur_6690_acsi_5y_finance_outlook_20260827.pdf"
DOWNLOAD_COPY = REPO / "reports" / "downloads" / "6690_安碁資訊_近五年財務與前景報告.pdf"

# 單位：新台幣百萬元（另標者除外）。來源見報告末頁。
YEARS = [2021, 2022, 2023, 2024, 2025]
REV = [1447, 1603, 1845, 2146, 2432]
GP = [542.21, 642.49, 733.33, 890.33, 1032.23]
OI = [132.23, 185.45, 233.00, 293.49, 363.81]
NI = [86.85, 155.37, 190.59, 225.76, 306.69]  # 歸屬母公司
EPS = [6.68, 7.92, 8.66, 10.13, 10.22]  # 台股慣用季加總／公司公告
GM = [37.46, 40.08, 39.76, 41.48, 42.44]
OM = [9.14, 11.57, 12.63, 13.67, 14.96]
NM = [6.00, 9.69, 10.33, 10.52, 12.61]
ROE = [13.16, 13.38, 15.23, 10.49, 9.97]
ROA = [5.46, 5.47, 6.26, 5.10, 4.79]
ASSETS = [2105, 2135, 2520, 4681, 4820]
EQUITY = [1113, 1209, 1294, 3012, 3138]
CASH = [419.86, 568.39, 453.15, 1520, 894.21]
AR = [505.39, 485.34, 604.76, 712.94, 838.55]
DEBT = [309.23, 283.18, 245.03, 477.76, 436.02]
OCF = [624.97, 862.34, 859.38, 1487, 1277]
FCF = [318.93, 818.53, 700.20, 491.65, 1207]
DIV = [3.7, 4.5, 5.2, 6.0, 9.0]  # 盈餘所屬年度對應次年發放


def cagr(start: float, end: float, periods: int) -> float:
    """年複合成長率。periods＝間隔年數。"""
    if start <= 0 or periods <= 0:
        raise ValueError("cagr 需要正起始值與正年數")
    return (end / start) ** (1.0 / periods) - 1.0


def pct(n: float, digits: int = 1) -> str:
    return f"{n * 100:.{digits}f}%"


def _register_font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"缺少中文字型：{FONT_PATH}")
    pdfmetrics.registerFont(TTFont("WQY", str(FONT_PATH), subfontIndex=0))
    return "WQY"


def _charts_dir(tmpdir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Droid Sans Fallback"]
    plt.rcParams["axes.unicode_minus"] = False
    navy = "#0F3A5F"
    teal = "#1A7A7A"
    rust = "#C45C26"
    paths: dict[str, Path] = {}

    def save(name: str) -> Path:
        p = tmpdir / f"{name}.png"
        plt.tight_layout()
        plt.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close()
        return p

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = range(len(YEARS))
    w = 0.38
    ax.bar([i - w / 2 for i in x], [v / 100 for v in REV], w, color=navy, label="營收（億）")
    ax.bar([i + w / 2 for i in x], [v / 100 for v in NI], w, color=teal, label="稅後淨利（億）")
    ax.set_xticks(list(x), [str(y) for y in YEARS])
    ax.set_ylabel("新台幣億元")
    ax.set_title("營收與稅後淨利（歸屬母公司）")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    paths["rev_ni"] = save("rev_ni")

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(YEARS, GM, marker="o", color=navy, label="毛利率")
    ax.plot(YEARS, OM, marker="s", color=teal, label="營益率")
    ax.plot(YEARS, NM, marker="^", color=rust, label="淨利率")
    ax.set_ylabel("%")
    ax.set_title("獲利率走勢")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, 50)
    paths["margins"] = save("margins")

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(YEARS, ROE, marker="o", color=navy, label="ROE")
    ax.plot(YEARS, ROA, marker="s", color=teal, label="ROA")
    ax.set_ylabel("%")
    ax.set_title("股東權益／資產報酬率")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    paths["returns"] = save("returns")

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(YEARS, [v / 100 for v in OCF], marker="o", color=navy, label="營業現金流（億）")
    ax.plot(YEARS, [v / 100 for v in FCF], marker="s", color=teal, label="自由現金流（OCF−資本支出，億）")
    ax.set_title("現金創造（注意：合約履約無形資產支出未從 FCF 扣）")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    paths["cash"] = save("cash")

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.bar(YEARS, DIV, color=teal)
    for y, d in zip(YEARS, DIV):
        ax.text(y, d + 0.15, f"{d:.1f}", ha="center", fontsize=9)
    ax.set_ylabel("元／股")
    ax.set_title("現金股利（依盈餘所屬年度；2025 盈餘於 2026-06-25 除息 9 元）")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    paths["div"] = save("div")

    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    labels = [
        "台灣資安\nMordor 2026–31",
        "全球資安\nGartner 2025–30",
        "安碁營收\n2021–25",
        "管理服務\n台灣 至 2031",
        "雲端部署\n台灣 至 2031",
    ]
    vals = [11.21, 10.7, cagr(REV[0], REV[-1], 4) * 100, 14.23, 16.34]
    colors = [teal, navy, rust, "#5B8C5A", "#6B5B95"]
    ax.barh(labels, vals, color=colors)
    ax.set_xlabel("CAGR %")
    ax.set_title("成長率對照（產業為第三方預測；公司為已實現）")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    paths["cagr"] = save("cagr")

    return paths


def build_pdf(out: Path) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    font = _register_font()
    out.parent.mkdir(parents=True, exist_ok=True)
    navy = colors.HexColor("#0F3A5F")
    teal = colors.HexColor("#1A7A7A")
    pale = colors.HexColor("#F4F7FA")
    line = colors.HexColor("#D0D7DE")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverKicker", fontName=font, fontSize=11, textColor=teal, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name="CoverTitle", fontName=font, fontSize=22, textColor=navy, alignment=TA_CENTER, leading=30, spaceAfter=10))
    styles.add(ParagraphStyle(name="CoverSub", fontName=font, fontSize=12, textColor=colors.HexColor("#334155"), alignment=TA_CENTER, leading=18, spaceAfter=6))
    styles.add(ParagraphStyle(name="H1", fontName=font, fontSize=14, textColor=navy, spaceBefore=12, spaceAfter=8, leading=20))
    styles.add(ParagraphStyle(name="H2", fontName=font, fontSize=12, textColor=teal, spaceBefore=10, spaceAfter=6, leading=16))
    styles.add(ParagraphStyle(name="Body", fontName=font, fontSize=9.5, leading=15, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1E293B"), spaceAfter=6))
    styles.add(ParagraphStyle(name="Note", fontName=font, fontSize=8, leading=12, textColor=colors.HexColor("#64748B"), spaceAfter=6))
    styles.add(ParagraphStyle(name="Item", fontName=font, fontSize=9.5, leading=14.5, leftIndent=12, textColor=colors.HexColor("#1E293B"), spaceAfter=3))
    styles.add(ParagraphStyle(name="Footer", fontName=font, fontSize=7.5, textColor=colors.HexColor("#64748B"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Cell", fontName=font, fontSize=8, leading=11, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="CellL", fontName=font, fontSize=8, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Warn", fontName=font, fontSize=8.5, leading=13, textColor=colors.HexColor("#9A3412"), backColor=colors.HexColor("#FFF7ED"), borderPadding=6, spaceAfter=8))

    def P(text: str, style: str = "Body") -> Paragraph:
        return Paragraph(text, styles[style])

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(navy)
        canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(font, 8)
        canvas.drawString(16 * mm, A4[1] - 8 * mm, "6690 安碁資訊｜近五年財務分析與五年前景／全球競爭力")
        canvas.drawRightString(A4[0] - 16 * mm, A4[1] - 8 * mm, "觀測日 2026-08-27")
        canvas.setFillColor(line)
        canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.setFont(font, 7.5)
        canvas.drawString(16 * mm, 4 * mm, "非投資建議 · 分析屬 self-reported · 數字均有出處")
        canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"{doc.page}")
        canvas.restoreState()

    story = []
    tmpdir = Path(tempfile.mkdtemp(prefix="acsi6690_"))
    try:
        charts = _charts_dir(tmpdir)

        story += [
            Spacer(1, 38 * mm),
            P("AUGUR 研究備忘｜[I] 工具層分析｜非治權文書", "CoverKicker"),
            P("6690 安碁資訊<br/>近五年財務分析<br/>與未來五年前景、全球競爭力", "CoverTitle"),
            P("Acer Cyber Security Inc.（TPEX 6690）", "CoverSub"),
            P("觀測時點：2026-08-27　｜　財報尖：2026 年上半年　｜　月營收尖：2026-07", "CoverSub"),
            Spacer(1, 8 * mm),
            P(
                "一句：安碁是台灣純度最高的上市櫃資安服務股。2021–2025 營收年複合成長約 13.9%，"
                "毛利率跨過 40%、營益率從 9% 走到近 15%，2025 稅後淨利首破 3 億、EPS 10.22 元。"
                "它在政府 SOC 與金融 SOC 有本地領先地位，但全球營收規模約 7,600 萬美元，"
                "不是 Palo Alto／CrowdStrike 那一級的產品平台商。未來五年的題目是："
                "台灣法規與人才缺口能不能繼續把 MSSP 訂單灌進來，以及東南亞能不能從「有辦公室」變成「有營收」。",
                "Body",
            ),
            Spacer(1, 6 * mm),
            P(
                "本報告不是進出場建議、不是目標價、不是財測保證。情境數字是把已實現成長率對上產業第三方預測後的推估區間，"
                "不是公司公告的 2026–2030 指引。",
                "Warn",
            ),
            PageBreak(),
        ]

        story += [
            P("0. 資料範圍、方法與免責", "H1"),
            P(
                "本輪<strong>未</strong>查詢 Augur 本地 PostgreSQL（本環境無可用 DB 連線），也<strong>未</strong>呼叫 FinMind／FRED。"
                "財務數列以公開合併財報二次轉載為主（S&amp;P Global via stockanalysis、HiStock 季報、聯合新聞網轉述公司 2025 年報數字），"
                "並與公司 2026-03-23 法說會轉述、114 年致股東報告交叉。產業規模取 Gartner 2Q26 預測與 Mordor Intelligence 台灣資安報告（2026 年版）。",
                "Body",
            ),
            P(
                "單位除另標外為新台幣。損益「稅後淨利」採<strong>歸屬母公司</strong>。"
                "2021 年仍有少數股權（約 2,675 萬），繼續營業部門淨利 1.136 億、歸屬母公司 8,685 萬；2022 年起已無少數股權。"
                "EPS 採台灣投資人慣用的年度加總／公司公告（2025 官方 10.22 元）。"
                "S&amp;P 口徑 2021 基本 EPS 5.11 元，差異來自加權流通股與少數股權，本文不以該年 5.11 當成長起點。",
                "Body",
            ),
            P("1. 公司是什麼", "H1"),
            P(
                "安碁資訊股份有限公司（Acer Cyber Security，上櫃 6690，數位雲端／軟體與資訊服務）。"
                "2000-05-29 設立，2019-10-30 上櫃。董事長施宣輝、總經理吳乙南、財務長／發言人譚百良。"
                "實收資本 3.00 億、流通普通股約 2,999.97 萬股、簽證會計師安侯建業。"
                "宏碁集團持股歷史上約六成，品牌與雲端子公司（宏碁雲架構 Acer eDC，2022 年併入）是結構性資源，不是「獨立新創」。",
                "Body",
            ),
            P("商業模式（MSSP，不是硬體代理）", "H2"),
            P("• 資訊安全委外監控（SOC 7×24）：月費制、高續約，毛利率約四成。政府 SOC 市占公司自述逾 60%，金融約 50%。", "Item"),
            P("• 營運不中斷：資料中心／算力中心、異地備援（2022 年因備援需求把相關能力併回）。", "Item"),
            P("• 資安檢測與顧問：弱點掃描、滲透測試、ISO 27001、零信任規劃；專案認列，季波動較大。", "Item"),
            P("• 雲地聯防 Cloud SOC：與 Azure／AWS／Google Cloud 整合，公司自述為「唯一具備雲地整合的台灣 MSSP」。", "Item"),
            P("• OT／關鍵基礎設施：台電智慧電網 IDS 擴大案（約 7,000 萬級）、IEC 62443。", "Item"),
            P("• 安碁學苑：2025 累計培訓逾 1 萬人次；勞動部許可，對準台灣資安人才缺口。", "Item"),
            P(
                "114 年營收結構：資訊安全服務 21.45 億（88.22%）、資訊部門營運委外 2.86 億（11.78%）。"
                "政府與金融仍是基本盤；製造業與中小企業 2025 客戶數 +17.6%、營收 +23.4%，是增量最快的一群。"
                "銷售地區長期約 99.7% 台灣——這是本地護城河，也是全球競爭力的天花板。",
                "Body",
            ),
            P("2. 近五年損益：量利齊升，不是一次行情", "H1"),
            P(
                f"2021→2025 營收 14.47→24.32 億，年複合成長 <strong>{pct(cagr(REV[0], REV[-1], 4))}</strong>。"
                f"營業利益 1.32→3.64 億，CAGR <strong>{pct(cagr(OI[0], OI[-1], 4))}</strong>。"
                f"歸屬母公司淨利 0.87→3.07 億，CAGR <strong>{pct(cagr(NI[0], NI[-1], 4))}</strong> "
                f"（若改以 2022 為起點，三年 CAGR {pct(cagr(NI[1], NI[-1], 3))}，較不受 2021 少數股權扭曲）。"
                "2025 營收年增 13.3%，優於資策會 MIC 對台灣資安 2025 產值 +12.3% 的預測；淨利年增 36%，因為毛利率與營益率同時走高，再加上現金增資後的絕對獲利把股數稀釋吃掉。",
                "Body",
            ),
        ]

        def money_table() -> Table:
            head = ["科目", "2021", "2022", "2023", "2024", "2025"]
            rows = [
                ["營收", "14.47 億", "16.03 億", "18.45 億", "21.46 億", "24.32 億"],
                ["營收年增", "—", "+10.8%", "+15.1%", "+16.4%", "+13.3%"],
                ["毛利", "5.42 億", "6.42 億", "7.33 億", "8.90 億", "10.32 億"],
                ["毛利率", "37.5%", "40.1%", "39.8%", "41.5%", "42.4%"],
                ["營業利益", "1.32 億", "1.85 億", "2.33 億", "2.93 億", "3.64 億"],
                ["營益率", "9.1%", "11.6%", "12.6%", "13.7%", "15.0%"],
                ["稅後淨利*", "0.87 億", "1.55 億", "1.91 億", "2.26 億", "3.07 億"],
                ["淨利率", "6.0%", "9.7%", "10.3%", "10.5%", "12.6%"],
                ["EPS（元）", "6.68", "7.92", "8.66", "10.13", "10.22"],
                ["ROE", "13.2%", "13.4%", "15.2%", "10.5%", "10.0%"],
                ["ROA", "5.5%", "5.5%", "6.3%", "5.1%", "4.8%"],
            ]
            data = [[Paragraph(c, styles["Cell"]) for c in head]]
            data += [[Paragraph(c, styles["Cell"]) for c in r] for r in rows]
            t = Table(data, colWidths=[28 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), navy),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BACKGROUND", (0, 1), (-1, -1), pale),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pale, colors.white]),
                        ("GRID", (0, 0), (-1, -1), 0.3, line),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E8EEF4")),
                    ]
                )
            )
            return t

        story += [
            money_table(),
            P("*稅後淨利＝歸屬母公司。2021 繼續營業部門淨利 1.14 億（含少數股權）。EPS 為公司／台股慣用口徑。", "Note"),
            Image(str(charts["rev_ni"]), width=170 * mm, height=74 * mm),
            Image(str(charts["margins"]), width=170 * mm, height=74 * mm),
            P("讀法", "H2"),
            P("• 成長是「連續雙位數營收」而不是單年爆發。2023–2025 三年營收年增 15.1%／16.4%／13.3%，基期變大後速度略降、絕對增量仍在加。", "Item"),
            P("• 利潤率是這檔股票的核心故事：營益率五年 +5.8 個百分點。服務比重高、SOC 月費、規模攤提研發，這條路走得通。", "Item"),
            P("• EPS 2024→2025 只從 10.13 到 10.22（+0.9%），因為 2024 現金增資把股本擴大約 36%。淨利 +36% 剛好把稀釋吃完——EPS 沒爆發，不代表獲利沒爆發。", "Item"),
            P("• ROE 從 2023 的 15.2% 掉到 2025 的 10.0%，主因權益因增資從 13 億跳到 31 億，不是獲利崩潰。看 ROIC（2025 約 12.6%）比看被稀釋的 ROE 更接近本業。", "Item"),
            P("• 研發費用 2025 約 3.65 億、佔營收 15%，高於多數台灣 SI。這是服務產品化（ATHENA 情資、安答 Agentic AI）的成本，也是毛利率能守住 40% 的條件。", "Item"),
            PageBreak(),
            P("3. 資產負債、現金與「看起來超高」的自由現金流", "H1"),
        ]

        bs_head = ["時點", "資產", "權益", "負債比*", "現金", "應收", "有息負債", "流動比"]
        bs_rows = [
            ["2021 年底", "21.1 億", "11.1 億", "47%", "4.2 億", "5.1 億", "3.1 億", "1.42"],
            ["2022 年底", "21.4 億", "12.1 億", "43%", "5.7 億", "4.9 億", "2.8 億", "1.67"],
            ["2023 年底", "25.2 億", "12.9 億", "49%", "4.5 億", "6.0 億", "2.5 億", "1.12"],
            ["2024 年底", "46.8 億", "30.1 億", "36%", "15.2 億", "7.1 億", "4.8 億", "2.54"],
            ["2025 年底", "48.2 億", "31.4 億", "35%", "8.9 億", "8.4 億", "4.4 億", "2.47"],
            ["2026/6/30", "48.1 億", "30.2 億", "37%", "13.5 億", "8.1 億", "4.2 億", "2.14"],
        ]
        bs_data = [[Paragraph(c, styles["Cell"]) for c in bs_head]]
        bs_data += [[Paragraph(c, styles["Cell"]) for c in r] for r in bs_rows]
        bs = Table(bs_data, colWidths=[24 * mm] + [22 * mm] * 7)
        bs.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pale, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.3, line),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story += [
            bs,
            P("*負債比＝總負債／總資產。2024 權益跳升主因現金增資約 16.0 億（普通股發行）。2024 不動產（土地 5.03 億＋建物 3.52 億）入帳，PPE 從 6.8 億升到 15.6 億。", "Note"),
            Image(str(charts["returns"]), width=170 * mm, height=74 * mm),
            Image(str(charts["cash"]), width=170 * mm, height=74 * mm),
            P(
                "營業現金流年年高於淨利：2025 OCF 12.77 億 vs 淨利 3.07 億。這在 SOC／專案公司很常見——"
                "合約負債（預收）與攤銷、折舊會把現金前移。2025 合約負債仍有 1.54 億流動＋2.08 億長期。",
                "Body",
            ),
            P(
                "必須拆開的一項：S&amp;P「自由現金流」2025 為 12.07 億（OCF−不動產廠房設備資本支出 0.69 億），"
                "但投資現金流同年 −16.81 億，其中「購買無形資產」8.42 億、證券投資 7.66 億。"
                "無形資產在安碁的帳上，很大一塊是履約用軟硬體（法說：投資現金流出主要是履行合約的軟硬體採購）。"
                "若把無形資產採購一併扣掉，調整後 FCF ≈ 12.77 − 0.69 − 8.42 ＝ <strong>3.66 億</strong>，仍高於淨利，但不是帳面 12 億那種「印鈔」。"
                "2024 因購置不動產，PPE 資本支出 9.95 億，調整後更緊。",
                "Body",
            ),
            P(
                "財務槓桿低：2025 年底有息負債 4.36 億、淨現金約 4.58 億（現金 8.94−負債 4.36）；"
                "2026/6/30 淨現金回升到約 12.8 億（現金及約當 13.5＋短投後更高）。"
                "配 9 元（總額約 2.70 億）之後現金仍厚。這家公司目前不是「靠舉債衝營收」。",
                "Body",
            ),
            P("4. 股利、股本與評價位置", "H1"),
            Image(str(charts["div"]), width=170 * mm, height=74 * mm),
            P(
                "現金股利（盈餘年度→次年發放）：3.7→4.5→5.2→6.0→9.0 元。"
                "2025 盈餘配發率約 88%（9.00／10.22），公司於 2026-03-23 法說說從歷史約 60% 拉到近 90%，理由是保留盈餘夠、對現金流有信心。"
                "2026-06-25 除息、7-23 發放。以 2026-08-27 收盤 165 元計，殖利率約 5.5%；本益比約 15×（165／近四季 EPS 10.95），股價淨值比約 1.64×（淨值約 100.8 元）。"
                "流通股約 3,000 萬、市值約 49.5 億。",
                "Body",
            ),
            P(
                "股本事件：2022、2024 兩次現金增資（2024 發行普通股現金流入約 16.0 億，股數約 22.2→30.1 百萬）。"
                "2025 年底普通股 3.00 億（面額 10 元）。增資讓每股盈餘「看起來平」、讓 ROE 下降、讓帳上現金與土地一次到位——"
                "評價時不要用 2023 的 15% ROE 當永續，也不要用「EPS 沒成長」否定淨利成長。",
                "Body",
            ),
            P("5. 2026 年迄今：成長還在，毛利率在讓", "H1"),
        ]

        ytd_head = ["期間", "營收", "年增", "毛利率", "營益率", "稅後", "EPS"]
        ytd_rows = [
            ["2025H1", "11.14 億", "—", "42.2%", "14.1%", "1.31 億", "4.37"],
            ["2026Q1", "6.25 億", "+21.0%*", "37.5%", "13.1%", "0.68 億", "2.27"],
            ["2026Q2", "6.59 億", "+10.3%", "40.4%", "15.2%", "0.85 億", "2.83"],
            ["2026H1", "12.84 億", "+15.3%", "39.0%", "14.2%", "1.53 億", "5.10"],
            ["2026-01–07 營收", "14.95 億", "+14.3%", "—", "—", "—", "—"],
        ]
        ytd_data = [[Paragraph(c, styles["Cell"]) for c in ytd_head]]
        ytd_data += [[Paragraph(c, styles["Cell"]) for c in r] for r in ytd_rows]
        ytd = Table(ytd_data, colWidths=[32 * mm, 24 * mm, 22 * mm, 22 * mm, 22 * mm, 24 * mm, 22 * mm])
        ytd.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), teal),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pale, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.3, line),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story += [
            ytd,
            P("*Q1 營收年增以 2026Q1 6.25 億 vs 2025Q1 5.16 億計算。7 月單月營收 2.11 億、月減 11.9%、年增 8.9%——單月波動大，CFO 要求看季。", "Note"),
            P(
                "上半年營收、淨利、EPS 都創同期新高，年增約 15–17%。管理層維持 2026 營收雙位數成長的口頭展望。"
                "要盯的是毛利率：H1 38.96%，年減 3.21 個百分點。可能原因包括 SI／專案組合、履約成本、人力。"
                "營益率仍守住 14%——費用控制把毛利讓出的部分補回來了。若毛利率繼續往 36% 以下走，15% 營益率故事會裂。",
                "Body",
            ),
            P(
                "券商模型（CMoney 轉述，2026-08 時點，<strong>非本報告預測</strong>）：2026 EPS 約 11.36、2027 約 13.22。"
                "群益 TRADING BUY 等評等屬券商意見。H1 已賺 5.10，若下半年只重複 2025 下半年的 5.85，全年也會靠近 11 元——這是算術，不是保證。",
                "Body",
            ),
            PageBreak(),
            P("6. 產業未來五年：全球與台灣", "H1"),
            P("6.1 全球資安支出", "H2"),
            P(
                "Gartner（2025-07-29）：2024 年全球資安終端支出 1,934 億美元 → 2025 年 2,130 億（+10.1%）→ 2026 年 2,398 億（+12.5%）。"
                "服務 838／928 億、軟體 1,059／1,212 億（2025／2026），軟體是最快的一塊。"
                "Gartner 2Q26 更新（2026-06-25）：2026 年全球資訊安全 2,489 億美元（固定匯率 +12.7%），2030 年 3,726 億，2025–2030 CAGR <strong>10.7%</strong>，期間新增年支出 1,544 億美元。",
                "Body",
            ),
            P("成長最快的細項（Gartner 2Q26，2025→2030 CAGR）不是防火牆，而是雲與 AI：", "Body"),
            P("• 雲端安全態勢管理 CSPM 27.6%（47→161 億美元）", "Item"),
            P("• 雲端存取安全仲介 CASB 24.3%", "Item"),
            P("• 雲端工作負載防護 CWPP 21.0%", "Item"),
            P("• 零信任網路存取 ZTNA 20.9%（NAC 同期在萎縮——預算在搬家，不是資安變小）", "Item"),
            P("• 「保護 AI」首次被單列，並塞進 Other Security Software；該段 2025 156 億→2030 376 億（CAGR 18.5%），新增美元比任何單一細項都多（+219 億）。Gartner 預期 2029 年這塊會超過終端防護，成為最大單項。", "Item"),
            P(
                "對安碁的意義：全球增量在雲安全、零信任、保護 AI、託管服務。安碁的產品不是 CSPM 套裝軟體，它賣的是「有人 7×24 看、能過台灣法規、能接混合雲」的服務。"
                "全球 CAGR 10.7% 是天花板參考，不是安碁的自動成長率。",
                "Body",
            ),
            P("6.2 台灣資安市場", "H2"),
            P(
                "Mordor Intelligence（2026 年版，研究期 2020–2031）：台灣資安市場 2025 年 <strong>11.7 億美元</strong> → 2026 年 13.0 億 → 2031 年 22.2 億，"
                "2026–2031 CAGR <strong>11.21%</strong>。結構：解決方案 2025 占 63.2%，但管理服務 CAGR 14.23%（安碁所在賽道快於整體）；"
                "地端仍占 56.2%，雲端部署 CAGR 16.34%；大型企業占 71.6%，中小企業 CAGR 12.26%；BFSI 占 23.0%，醫療 CAGR 最快 15.02%。",
                "Body",
            ),
            P("驅動（Mordor 量化衝擊為方向值，不是可加總的精確分解）：", "Body"),
            P("• 資通安全法 2.0：納管從 4 類擴到 6 類關鍵基礎設施，未通報最高罰 1,000 萬；數發部要求年度第三方稽核 → 立刻變成 SOC／事件應變／弱點掃描訂單。", "Item"),
            P("• 日均約 240 萬次攻擊、地緣與半導體供應鏈（美歐客戶要安全證明）→ 政府與製造的剛性預算。", "Item"),
            P("• 人才缺口：Mordor 寫約 8 萬人；安碁法說用「逾 2 萬」——口徑不同，方向相同：請不起人就外包 MSSP，這是安碁的基本需求函數。", "Item"),
            P("• 工廠 OT／IT 收斂（TXOne 調查：94% 台灣工廠有源自 IT 的 OT 事件）、科學園區私有 5G、金融零信任沙盒。", "Item"),
            P("抑制：中小企業資安預算低、政府仍偏愛設備採購（拖慢純 SaaS）、跨境資料限制（這反而擋外國 MSSP、利於在地業者）、雙語人才貴。", "Body"),
            P(
                "資策會 MIC（公司致股東報告引用）：台灣資安產值 2025 +12.3%、2026 +10.8%。"
                "安碁 2025 營收 +13.3%，略快於 MIC。工研院 IEK 較早的「2026 年產值千億台幣、雙位數」與 Mordor 的美元口徑不是同一套帳，不能直接除匯率對倒。",
                "Body",
            ),
            Image(str(charts["cagr"]), width=170 * mm, height=78 * mm),
            P("7. 全球競爭力：本地冠軍，全球小廠", "H1"),
            P("7.1 先把量級講清楚", "H2"),
            P(
                "2025 年安碁營收 24.32 億新台幣，約 7,600 萬美元（法說換算）。"
                "同期間全球資安支出已超過 2,000 億美元。安碁占全球不到 0.04%。"
                "CrowdStrike、Palo Alto Networks、Fortinet、Microsoft 安全雲、趨勢科技的年營收是十億至百億美元級。"
                "用「全球資安成長 11%」外推安碁股價，是把 TAM 誤認成 SAM。",
                "Body",
            ),
            P("7.2 它實際在跟誰搶", "H2"),
            P("台灣 MSSP／SOC／檢測：中華資安、數聯資安、精誠（6214）、關貿網路、部分電信與大型 SI（零壹 3029、邁達特 6112 更多是產品通路，安碁是它們的下游服務商）。", "Item"),
            P("全球平台：客戶端點／雲端會同時買 CrowdStrike、Microsoft Defender、Palo Alto、Azure Security——安碁是「把這些日誌接到 SOC 代操」的一層，互補多於取代。", "Item"),
            P("新進 AI 資安：CyCraft 等在紅隊／AI 防禦有能見度。安碁的「安答」是維運代理人，不是同一條產品線。", "Item"),
            P("7.3 相對優勢（已看到證據的）", "H2"),
            P("• 政府與金融 SOC 市占：16 個政府機關、8 家關鍵基礎設施（含經濟部所屬國營）、金融約五成。這是牌照、資歷、場地與信任堆出來的，不是廣告。", "Item"),
            P("• 法規在地性：資安法 2.0、金管會資安 2.0、年度第三方稽核、政府偏好地端／主權雲。Mordor 把「外國 MSSP 跨境資料限制」列為市場抑制項——對安碁是保護。", "Item"),
            P("• 雲地一條龍：2022 併宏碁雲架構後有 Azure CSP／MSP 資格，Cloud SOC 加地端 SIEM。純產品商沒有 7×24 中文維運；純 SI 沒有這麼深的 SOC。", "Item"),
            P("• OT 已接到電：台電約 7,000 萬級變電設施擴充，不是簡報上的「即將布局」。製造業 2025 營收 +23.4% 對得上。", "Item"),
            P("• 宏碁品牌與集團雲、學苑補人才。台灣資安評比相對東協的論述，是總經理在法說用來解釋「為什麼從泰國切」的理由，尚待營收驗證。", "Item"),
            P("7.4 相對弱勢（同樣是證據）", "H2"),
            P("• 地域集中：約 99.7% 台灣。泰國辦公室兩年後仍在「轉型成終端與遠端服務」、評估其他市場——這不是已經全球化。", "Item"),
            P("• 產品平台薄弱：沒有可出口的大型安全軟體訂閱。海外要複製的是人、流程、在地合規，單位經濟差、複製慢。", "Item"),
            P("• 規模：市值約 50 億新台幣，接得下台電與政府大案，接不下跨國十年平台標。", "Item"),
            P("• 人才與薪資通膨：服務業成長最終碰到人。安答號稱弱掃人力 −30%、目標自動化 50%——這是緩解，不是消除。", "Item"),
            P("• 毛利率 2026H1 已下滑 3.2 個百分點。若未來為了搶製造／中小企／東南亞而提高 SI 硬體組合，40% 毛利會往 SI 的 20–30% 靠。", "Item"),
            PageBreak(),
            P("8. 公司未來五年前景（2026–2030）", "H1"),
            P(
                "公司沒有公布 2026–2030 逐年財測。以下三個情境是把（a）已實現 2021–2025 營收 CAGR 13.9%、"
                "（b）MIC／Mordor／Gartner 約 11% 產業增速、（c）2026 迄今 +14% 營收、（d）管理層「2026 雙位數」口頭展望"
                "放在一起的算術區間。<strong>不是承諾、不是目標價輸入、不是 Augur 模型輸出。</strong>",
                "Body",
            ),
        ]

        sc_head = ["情境", "假設", "2026 營收", "2030 營收", "五年 CAGR", "對獲利的含義"]
        sc_rows = [
            [
                "保守",
                "台灣政府／金融預算平、東南亞沒打開、毛利率因組合下滑守在 37–39%",
                "約 26.5–27 億（+9–11%）",
                "約 36–38 億",
                "約 8–9%",
                "EPS 緩步，配息仍可但 88% 配發率會往回修",
            ],
            [
                "基準",
                "持續略快於產業：政府 SOC 續約＋製造／中小企＋Cloud SOC，東南亞仍小",
                "約 27.5–28 億（+13–15%）",
                "約 42–45 億",
                "約 11–13%",
                "淨利率 12% 附近，2030 淨利約 5–5.5 億量級",
            ],
            [
                "樂觀",
                "AI SOC 產能真的放出來、OT／零信任大單連續、泰國模式複製到馬／印",
                "約 28.5 億以上",
                "約 50 億以上",
                "約 15%+",
                "營益率站穩 16%+；這需要海外營收明顯離開 0.3%",
            ],
        ]
        sc_data = [[Paragraph(c, styles["Cell"]) for c in sc_head]]
        for r in sc_rows:
            sc_data.append([Paragraph(c, styles["CellL"]) for c in r])
        sc = Table(sc_data, colWidths=[18 * mm, 42 * mm, 32 * mm, 28 * mm, 22 * mm, 36 * mm])
        sc.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pale, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.3, line),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story += [
            sc,
            P(
                "基準情境的錨：2026 年前七月累計已 +14.3%，要掉到個位數全年成長，下半年必須明顯失速。"
                "2030 年 42–45 億營收意味著安碁仍是「台灣龍頭 MSSP」，不是區域產品巨頭。"
                "即使樂觀到 50 億，以匯率 32 計也才約 1.6 億美元——全球競爭力仍是利基，不是平台。",
                "Body",
            ),
            P("成長雙箭頭（公司 115 年致股東報告原文方向）", "H2"),
            P("1. AI 對應方案：SOC 監測（帳號／通訊異常）、檢測自動化（弱掃人力已降約 50%、網頁弱掃與滲測約 30%）、ISMS 顧問 LLM 助手、Cloud SOC 安答代理人、AI 治理（PMO：治理／架構／應用）。", "Item"),
            P("2. 雲端服務：One Team 與 eDC、地端日誌上雲、混合雲。Gartner 雲安全細項 20%+ CAGR 是這條的外部風。", "Item"),
            P("三大營收支柱：SI 放大規模 × SOC × 營運不中斷。SI 做大有助營收、可能壓毛利——這是基準與保守情境的分歧點。", "Item"),
            P(
                "東南亞：2018 進泰國、2023 設辦公室，主推 EDR／MDR、一次性檢測、SOC 加值，再看馬來西亞與印尼的台商製造聚落。"
                "五年內若海外仍 <5% 營收，全球競爭力評分不應上修。若突破 10%，才談「區域化」。目前證據停在「有據點、有論述」。",
                "Body",
            ),
            P("9. 風險（已發生或結構上必然）", "H1"),
            P("1. 台灣 TAM 有限。Mordor 2031 年整個台灣資安才 22 億美元；安碁再怎麼搶市占，也會碰到政府標案週期與預算天花板。", "Item"),
            P("2. 客戶集中於政府／金融。選舉、預算、資安法執行力一鬆，SOC 續約與新案會一起慢。", "Item"),
            P("3. 毛利率下行已在 2026H1 出現。SI 組合、人力、專案成本是三條可能的裂縫。", "Item"),
            P("4. 88% 配發率。成長若要砸錢建海外 SOC 或買公司，不是沒現金，是股東已習慣高配息。", "Item"),
            P("5. 現金增資稀釋剛發生過。再融資不是不可能，EPS 會再被打斷。", "Item"),
            P("6. 攻擊面與交付風險。SOC 業者自己被攻、或重大客戶出事，是聲譽尾部風險。", "Item"),
            P("7. 全球平台商下探服務層（Microsoft／Google 綁 MSP）。安碁現在是夥伴，夥伴條款可以改。", "Item"),
            P("8. 東南亞在地化、執照、語言、付款習慣。失敗模式是「開了辦公室、營收仍是台灣」。", "Item"),
            P("9. 把券商 EPS、產業 CAGR、或本益比河流圖藍色區間當成「會漲」——那是評價描述，不是報酬。", "Item"),
            P("10. 結論", "H1"),
            P(
                "近五年財務：這是一張乾淨的複合成長表。營收、毛利率、營益率、淨利同向變好；現金流能撐近九成配息；"
                "資產負債在增資後變厚、槓桿低。瑕疵是股本膨脹讓 EPS／ROE 看起來平、以及 2026 上半年毛利率回吐。",
                "Body",
            ),
            P(
                "未來五年產業：全球與台灣資安都還在 10–12% 的中高速軌道，而且管理服務、雲、零信任、保護 AI、OT 比平均更快。"
                "法規與人才缺口對 MSSP 是順風。這不是週期股的「補庫存」，比較像合規預算。",
                "Body",
            ),
            P(
                "全球競爭力：安碁是台灣資安服務的第一梯隊，不是全球資安的第一梯隊。"
                "競爭力建立在中文、法規、政府信任、雲地維運，而不是可規模化的軟體毛利。"
                "五年後更可能的成功樣子，是「台灣仍主導、製造／OT／中小企比重升高、東南亞開始看得到營收、AI 讓每人產值上升」；"
                "比較不像的樣子，是「成為亞洲 CrowdStrike」。用對標尺，這五年的財務紀錄是撐得住「略快於產業」的基準情境的；"
                "用錯標尺，會把 50 億市值的公司拿去跟千億美元賽道比，然後失望。",
                "Body",
            ),
            P("11. 來源（可回溯）", "H1"),
            P("• 公司：acercsi.com；114 年致股東報告／年報（樹懶生活轉載產品組合與全文）；2026-03-23 法說會（BigGo 英文整理）。", "Item"),
            P("• 財報數字：stockanalysis.com（S&amp;P Global）損益／資產負債／現金流量／比率；HiStock 季損益與 EPS、除權息；PChome 股市 2026Q2 比較損益；聯合新聞網 2025 年報通過稿（營收 2,431,957 千元、營業淨利 363,814 千、稅後 306,685 千、EPS 10.22、擬配 9.0 元）。", "Item"),
            P("• 市況：Win 投資／PChome 2026-07 月營收、2026-08-27 股價 165 元。", "Item"),
            P("• 產業：Gartner 新聞稿 2025-07-29；Gartner Forecast: Information Security, Worldwide, 2024–2030, 2Q26（G00855892，轉述自 Software Strategies Blog 2026-07-06）；Mordor Intelligence Taiwan Cybersecurity 2026–2031；MIC 2023–2027 產值（公司年報引用）。", "Item"),
            P("• 競爭與商業模式背景：優分析、Vocus 2023–2024 產業整理（僅作結構描述，財務以年報為準）。", "Item"),
            Spacer(1, 4 * mm),
            P(
                "編製：Augur 研究備忘 2026-08-27。層級 [I]。分析文字為模型 self-reported，不得當成「世界如此」的權威確認。"
                "本文件不構成投資、法律或會計建議。",
                "Note",
            ),
        ]

        def first_page(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(navy)
            canvas.rect(0, A4[1] - 28 * mm, A4[0], 28 * mm, fill=1, stroke=0)
            canvas.setFillColor(teal)
            canvas.rect(0, 0, A4[0], 8 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont(font, 9)
            canvas.drawString(16 * mm, A4[1] - 12 * mm, "AUGUR  ·  TPEX 6690")
            canvas.drawRightString(A4[0] - 16 * mm, A4[1] - 12 * mm, "Confidentiality: public sources only")
            canvas.setFont(font, 8)
            canvas.drawString(16 * mm, 3 * mm, "非投資建議")
            canvas.restoreState()

        doc = SimpleDocTemplate(
            str(out),
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=18 * mm,
            bottomMargin=14 * mm,
            title="6690 安碁資訊｜近五年財務分析與五年前景、全球競爭力",
            author="Augur research memo (self-reported)",
        )
        doc.build(story, onFirstPage=first_page, onLaterPages=header_footer)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return out


def _selftest() -> int:
    # 純函式真輸入：已知 100→146.41 四年 CAGR＝10%
    got = cagr(100.0, 146.41, 4)
    if abs(got - 0.10) > 1e-3:
        print(f"SELFTEST FAIL cagr {got}", file=sys.stderr)
        return 1
    # 下游：真的產出 PDF，用檔頭與頁數驗，不用原始碼字面
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.pdf"
        build_pdf(p)
        raw = p.read_bytes()[:8]
        if raw[:4] != b"%PDF":
            print(f"SELFTEST FAIL magic {raw!r}", file=sys.stderr)
            return 1
        from pypdf import PdfReader

        n = len(PdfReader(str(p)).pages)
        if n < 8:
            print(f"SELFTEST FAIL pages {n}", file=sys.stderr)
            return 1
        print(f"selftest ok cagr={got:.4f} pages={n} bytes={p.stat().st_size}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="6690 安碁資訊財務前景 PDF")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    path = build_pdf(args.out)
    DOWNLOAD_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, DOWNLOAD_COPY)
    html = DOWNLOAD_COPY.parent / "index.html"
    html.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>下載｜6690 安碁資訊財務與前景報告</title>
  <style>
    body {{ font-family: "Noto Sans CJK TC", "WenQuanYi Micro Hei", sans-serif; margin: 0; background: #0F3A5F; color: #fff; }}
    main {{ max-width: 640px; margin: 12vh auto; padding: 32px; background: #102a43; border-radius: 12px; }}
    a.btn {{ display: inline-block; margin-top: 20px; padding: 12px 22px; background: #1A7A7A; color: #fff; text-decoration: none; border-radius: 8px; }}
    p {{ line-height: 1.6; color: #dbeafe; }}
  </style>
</head>
<body>
  <main>
    <h1>6690 安碁資訊</h1>
    <p>近五年財務分析與未來五年前景、全球競爭力報告（PDF）。觀測日 2026-08-27。非投資建議。</p>
    <a class="btn" href="{DOWNLOAD_COPY.name}" download>下載 PDF</a>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"wrote {path} ({path.stat().st_size} bytes)")
    print(f"download copy {DOWNLOAD_COPY}")
    print(f"download page {html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
