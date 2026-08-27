#!/usr/bin/env python3
"""Render Hanpin (2488) 5-year financial + 5-year outlook PDF (Traditional Chinese)."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
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

FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
pdfmetrics.registerFont(TTFont("WQY", FONT, subfontIndex=0))

NAVY = colors.HexColor("#1B365D")
GOLD = colors.HexColor("#C4A35A")
TEAL = colors.HexColor("#2A6F7F")
INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#5C6B73")
RULE = colors.HexColor("#D6D9DE")
ROW = colors.HexColor("#F4F6F8")
RED = colors.HexColor("#9B2C2C")
GREEN = colors.HexColor("#1F6B4A")
WHITE = colors.white

OUT = Path(__file__).resolve().parent / "hanpin_2488_financial_outlook_20260827.pdf"


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("CoverKicker", fontName="WQY", fontSize=10, textColor=GOLD, alignment=TA_CENTER, tracking=1.2, spaceAfter=6))
    ss.add(ParagraphStyle("CoverTitle", fontName="WQY", fontSize=22, leading=30, textColor=WHITE, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle("CoverSub", fontName="WQY", fontSize=12, leading=18, textColor=colors.HexColor("#E8EEF4"), alignment=TA_CENTER, spaceAfter=4))
    ss.add(ParagraphStyle("CoverMeta", fontName="WQY", fontSize=9, leading=14, textColor=colors.HexColor("#C5D0DB"), alignment=TA_CENTER))
    ss.add(ParagraphStyle("H1", fontName="WQY", fontSize=14, leading=20, textColor=NAVY, spaceBefore=12, spaceAfter=8))
    ss.add(ParagraphStyle("H2", fontName="WQY", fontSize=11.5, leading=16, textColor=TEAL, spaceBefore=9, spaceAfter=5))
    ss.add(ParagraphStyle("H3", fontName="WQY", fontSize=10.5, leading=15, textColor=NAVY, spaceBefore=7, spaceAfter=4))
    ss.add(ParagraphStyle("Body", fontName="WQY", fontSize=9.2, leading=14.5, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6))
    ss.add(ParagraphStyle("Note", fontName="WQY", fontSize=8, leading=12, textColor=MUTED, alignment=TA_JUSTIFY, spaceAfter=6))
    ss.add(ParagraphStyle("BodyBullet", fontName="WQY", fontSize=9.2, leading=14.2, textColor=INK, leftIndent=12, spaceAfter=3))
    ss.add(ParagraphStyle("Caption", fontName="WQY", fontSize=8, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8))
    ss.add(ParagraphStyle("Footer", fontName="WQY", fontSize=7.5, textColor=MUTED))
    ss.add(ParagraphStyle("Th", fontName="WQY", fontSize=8, leading=11, textColor=WHITE, alignment=TA_CENTER))
    ss.add(ParagraphStyle("Td", fontName="WQY", fontSize=8, leading=11, textColor=INK, alignment=TA_CENTER))
    ss.add(ParagraphStyle("TdL", fontName="WQY", fontSize=8, leading=11, textColor=INK, alignment=TA_LEFT))
    ss.add(ParagraphStyle("TdR", fontName="WQY", fontSize=8, leading=11, textColor=INK, alignment=TA_RIGHT))
    ss.add(ParagraphStyle("KPI", fontName="WQY", fontSize=8.2, leading=11.5, textColor=INK, alignment=TA_CENTER))
    ss.add(ParagraphStyle("KPIVal", fontName="WQY", fontSize=11, leading=14, textColor=NAVY, alignment=TA_CENTER))
    ss.add(ParagraphStyle("KPILab", fontName="WQY", fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_CENTER))
    ss.add(ParagraphStyle("Disc", fontName="WQY", fontSize=8, leading=12, textColor=colors.HexColor("#4A3728"), alignment=TA_JUSTIFY))
    return ss


S = styles()


def P(text, style="Body"):
    return Paragraph(text, S[style])


def th(*cells):
    return [P(c, "Th") for c in cells]


def td(*cells, right=False, left=False):
    st = "TdL" if left else ("TdR" if right else "Td")
    return [P(c, st) for c in cells]


def table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "WQY"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("GRID", (0, 0), (-1, -1), 0.3, RULE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), ROW))
    t.setStyle(TableStyle(cmds))
    return t


def kpi_row(items):
    cells = []
    for lab, val, note in items:
        inner = Table(
            [[P(val, "KPIVal")], [P(lab, "KPILab")], [P(note, "KPILab")]],
            colWidths=[36 * mm],
        )
        inner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F8FA")),
                    ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        cells.append(inner)
    outer = Table([cells], colWidths=[38 * mm] * len(items))
    outer.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
    return outer


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 12 * mm, w, 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 12.8 * mm, w, 1.2 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("WQY", 8)
        canvas.drawString(16 * mm, h - 8 * mm, "2488 漢平｜近五年財務分析與未來五年前景／全球競爭力")
        canvas.drawRightString(w - 16 * mm, h - 8 * mm, "公開資訊彙編｜非投資建議")
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, w, 10 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, 10 * mm, w, 0.8 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("WQY", 7.5)
        canvas.drawString(16 * mm, 4.2 * mm, "資料截止：2026-08-27　單位：新台幣仟元（另註除外）")
        canvas.drawRightString(w - 16 * mm, 4.2 * mm, f"第 {doc.page} 頁")
    canvas.restoreState()


def cover_page(canvas, doc):
    # first page uses cover; subsequent use header_footer
    if doc.page == 1:
        canvas.saveState()
        w, h = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, w, h, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 28 * mm, w, 8 * mm, fill=1, stroke=0)
        canvas.rect(0, 22 * mm, w, 3 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("WQY", 9)
        canvas.drawCentredString(w / 2, h - 24 * mm, "AUGUR 公開資訊研究備忘　·　非預測系統輸出　·　非投資建議")
        canvas.setFont("WQY", 11)
        canvas.drawCentredString(w / 2, h - 58 * mm, "台灣上市　其他電子　證券代號 2488")
        canvas.setFont("WQY", 24)
        canvas.drawCentredString(w / 2, h - 78 * mm, "漢平電子工業股份有限公司")
        canvas.setFont("WQY", 16)
        canvas.drawCentredString(w / 2, h - 92 * mm, "近五年財務分析報告")
        canvas.setFont("WQY", 14)
        canvas.drawCentredString(w / 2, h - 108 * mm, "暨公司／產業未來五年前景與全球競爭力")
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.8)
        canvas.line(45 * mm, h - 118 * mm, w - 45 * mm, h - 118 * mm)
        canvas.setFont("WQY", 10)
        canvas.setFillColor(colors.HexColor("#E8EEF4"))
        lines = [
            "分析期間：2021–2025 完整會計年度　＋　2026 年上半年／1–7 月營收",
            "展望期間：2026–2030（產業公開預測＋公司已揭露策略；公司未發布財測）",
            "主要來源：漢平合併財報（PwC 查核）／114 年報致股東報告書／MOPS 月營收轉載／RIAA／產業研調",
            "報告日：2026 年 8 月 27 日",
        ]
        y = h - 138 * mm
        for line in lines:
            canvas.drawCentredString(w / 2, y, line)
            y -= 8 * mm
        canvas.setFillColor(GOLD)
        canvas.setFont("WQY", 9)
        canvas.drawCentredString(w / 2, 36 * mm, "本報告所有量化數字均可回溯至附錄來源；展望段落標為分析意見（self-reported），非權威確認。")
        canvas.restoreState()
    else:
        header_footer(canvas, doc)


def build():
    story = []
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # DISCLAIMER
    story.append(P("0. 使用說明與邊界", "H1"))
    disc = Table(
        [[P(
            "本文件為公開資訊彙編與分析備忘，<b>不是</b>漢平公司發布的財務預測，也<b>不是</b> augur 預測管線／arena 對局之輸出。"
            "漢平 114 年報載明「本公司並未對外公開預測數」。文中 2026–2030 前景為依已揭露策略與產業公開研調所作之情境討論（self-reported），"
            "<b>不得</b>當作股價、獲利或下單依據。本公司未對漢平出具買進／賣出評等。"
            "FinMind／FRED 外部取數通道於本任務未使用；本報告未連本地 PostgreSQL（本雲端環境無 .env／庫）。",
            "Disc",
        )]],
        colWidths=[178 * mm],
    )
    disc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF4E8")),
        ("BOX", (0, 0), (-1, -1), 0.8, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(disc)
    story.append(Spacer(1, 4 * mm))

    story.append(P("1. 執行摘要", "H1"))
    story.append(P(
        "漢平（2488）是台南起家、以中國深圳為主要製造基地的專業音訊 <b>OEM／ODM</b>。"
        "產品線涵蓋 Hi-Fi／DJ 唱盤（直驅與皮帶）、媒體播放器、混音器與 MIDI 控制器。"
        "合併營收幾乎 100% 來自音訊；營建／租賃僅貢獻租金（2025 年 2,671 仟元）。"
        "近五年獲利品質明顯優於營收規模：營收在 24.9–31.8 億元區間震盪，稅後淨利卻從 2021 年約 1.42 億升至 2024 年高峰 4.19 億，2025 年回落至 3.65 億（EPS 4.56 元）。"
        "財務結構極為保守：2025 年底現金及約當現金 11.58 億、流動金融資產另約 10.1 億、短期借款僅 3,000 萬，負債比 26%、權益比 74%。"
        "弱點同樣清楚：前三大客戶佔營收約六成、製造高度集中於深圳、對美營收 2025 年近乎腰斬、毛利率自 2023 年 26.7% 高點回落到 2025 年 22.9% 與 2026H1 的 22.1%。",
        "Body",
    ))
    story.append(kpi_row([
        ("2025 合併營收", "28.82 億", "年減 9.3%"),
        ("2025 稅後淨利", "3.65 億", "EPS 4.56 元"),
        ("2025 毛利率", "22.9%", "營業利益率 11.5%"),
        ("2026H1 EPS", "2.21 元", "營收年增 18.9%"),
        ("2026 年 1–7 月營收", "19.20 億", "累計年增 25.0%"),
    ]))
    story.append(P("圖表數字來源見第 2–4 節與附錄 A。單位新台幣。", "Caption"))

    story.append(P(
        "<b>五年前景一句話（分析意見，非財測）</b>：產業端——專業音訊設備全球市場公開研調約以 2024–2030 CAGR 5.3% 擴張；黑膠在美國 2025 年續創連 19 年成長（RIAA：4,680 萬張、批發收入 10.4 億美元），但已從「爆發復甦」進入「精品收藏化／利基成長」（此為公司 114 年報用語）。"
        "公司端——2026 年截至 7 月營收年增 25%，顯示 2025 年美國客戶去化後有回補；中期競爭力取決於能否把訂單從低價量產轉到高階唱盤與數位／類比整合，並降低中國製造＋美歐關稅與大客戶集中度風險。",
        "Body",
    ))

    story.append(P("2. 公司與產業定位", "H1"))
    story.append(P("2.1 基本資料", "H2"))
    story.append(table(
        [
            th("項目", "內容", "來源"),
            td("公司全名", "漢平電子工業股份有限公司　Hanpin Electron Co., Ltd.", left=True),
            td("上市／資本", "2001/09/17 上市；普通股股本 799,994 仟元（約 8,000 萬股、面額 10 元）", left=True),
            td("成立", "1965 年台南創立（官網）；公司登記 1969/04/01（合併財報附註）", left=True),
            td("負責人", "董事長兼總經理：劉深鏗；簽證會計師：資誠（田中玉、林秀珊）", left=True),
            td("地址／網站", "台南市仁德區中正路三段 256 號　http://www.hanpin.com.tw/", left=True),
            td("員工人數", "官網 About：約 860 人（未標年份；僅能作量級參考）", left=True),
            td("認證", "官網自稱 ISO-9001／ISO-9002", left=True),
        ],
        [32 * mm, 100 * mm, 46 * mm],
    ))
    # fix three-col rows - I used 2-col td. Rebuild properly.
    story.pop()
    story.append(table(
        [
            th("項目", "內容"),
            td("公司全名", "漢平電子工業股份有限公司（Hanpin Electron Co., Ltd.）", left=True),
            td("證券／產業", "2488　上市　其他電子", left=True),
            td("上市／股本", "2001/09/17 上市；普通股股本 799,994 仟元（約 8,000 萬股）", left=True),
            td("成立", "1965 年台南創立（官網）；公司登記 1969/04/01（2025 合併財報附註 1）", left=True),
            td("負責人", "董事長兼總經理劉深鏗；發言人同；會計主管朱文賢", left=True),
            td("簽證", "資誠聯合會計師事務所（2025／2024 無保留意見）", left=True),
            td("製造佈局", "台灣母公司接單／研發；香港報關；深圳兩家子公司製造（漢志電子、漢平電子）", left=True),
            td("產品（官網）", "消費電子：Hi-Fi 唱盤、CD 播放器；Pro-Audio：擴大機、混音器、EQ、PA；DJ：唱盤、播放器、混音器、MIDI", left=True),
            td("員工人數", "官網 Introduction：約 860 人（未標截止日，僅作量級）", left=True),
        ],
        [36 * mm, 142 * mm],
    ))
    story.append(P("表 1　公司基本資料。來源：漢平官網 About／Products；2025 合併財報；114 年報轉載（treelazy）。", "Caption"))

    story.append(P("2.2 集團結構與製造地理", "H2"))
    story.append(P(
        "2025 合併財報附註與附表顯示：母公司對香港漢志電子進貨 2,300,870 仟元（佔母公司進貨 86%），香港再向深圳漢志電子進貨 2,315,628 仟元（佔其進貨 85%）。"
        "這是典型的「台灣接單—香港轉口—深圳製造」三角。"
        "大陸投資：漢平電子（深圳）帳面 250,696 仟元、當期損益 5,147 仟元；漢志電子（深圳）帳面 523,656 仟元、當期損益 34,201 仟元——產能與獲利重心在漢志深圳。"
        "經投資審議委員會核准對陸投資 361,445 仟元。非流動資產地理：台灣 433,050、中國 119,829 仟元（2025）。"
        "營收幾乎全部外銷：台灣＋中國合計僅約 0.8%。",
        "Body",
    ))

    story.append(P("2.3 產品與研發方向（公司已揭露）", "H2"))
    story.append(P(
        "114 年報致股東報告書列出 2025 年研發成果：Hi-Fi 高階唱盤、全自動播放唱盤＋無線傳輸、專業 MIDI 控制器整合多進多出聲卡、專業 DJ 唱盤結合電腦 MIDI、高扭力直驅馬達唱盤、數位黑膠系統音頻介面、高效率交換式電源。"
        "2025 合併研發支出 111,585 仟元，佔營收 4%（2024：121,186 仟元、約 3.8%）。"
        "2026 策略原文關鍵詞：「高階工藝轉型」「智慧化技術整合」「精品收藏化與利基成長」「類比底蘊與數位便利」「北美與歐洲品牌溢價」。",
        "Body",
    ))

    story.append(P("3. 近五年財務分析（2021–2025）", "H1"))
    story.append(P("3.1 合併損益趨勢", "H2"))
    story.append(P(
        "2023–2025 數字直接取自漢平英文版合併財報（與 2026/02/25 法說簡報一致）。"
        "2021–2022 單季損益取自 HiStock 轉載之公開季報；將四季加總後，2023–2025 加總值與官方合併數<b>逐項相符</b>，故 2021–2022 加總可合理視為同一口徑之公開報表重編。",
        "Body",
    ))
    story.append(table(
        [
            th("項目", "2021", "2022", "2023", "2024", "2025"),
            td("營業收入", "2,485,647", "3,085,191", "2,461,954", "3,177,581", "2,882,427"),
            td("營收年增率", "—", "+24.1%", "−20.2%", "+29.1%", "−9.3%"),
            td("營業毛利", "418,408", "635,238", "657,977", "773,744", "660,940"),
            td("毛利率", "16.8%", "20.6%", "26.7%", "24.4%", "22.9%"),
            td("營業利益", "157,620", "312,279", "367,799", "417,238", "330,466"),
            td("營業利益率", "6.3%", "10.1%", "14.9%", "13.1%", "11.5%"),
            td("稅前淨利", "199,009", "418,729", "454,987", "541,441", "432,805"),
            td("本期淨利", "142,031", "307,428", "351,127", "419,069", "364,592"),
            td("純益率", "5.7%", "10.0%", "14.3%", "13.2%", "12.6%"),
            td("基本 EPS（元）", "1.79", "3.86", "4.39", "5.24", "4.56"),
            td("稀釋 EPS（元）", "—", "—", "—", "5.16", "4.49"),
            td("研發費用", "—", "—", "—", "121,186", "111,585"),
        ],
        [32 * mm, 29 * mm, 29 * mm, 29 * mm, 29 * mm, 30 * mm],
    ))
    story.append(P("表 2　合併損益五年。2023–2025：漢平合併綜合損益表。2021–2022：HiStock 季報加總（驗證見上文）。EPS：2023–2025 取財報；2021–2022 取 HiStock／Money-link 與官方一致之年 EPS。", "Caption"))

    story.append(P(
        "<b>解讀。</b>營收是「兩年一循環」而非穩步成長：2022、2024 衝高（30.9／31.8 億），2023、2025 回落（24.6／28.8 億）。"
        "這符合消費／專業音訊 OEM 的訂單年——品牌客戶庫存補貨與去化交替。"
        "獲利卻未跟營收同幅崩：2023 營收年減 20%，淨利仍年增（351 vs 307 百萬），因為毛利率跳升至 26.7%。"
        "2021→2025 營收 CAGR 約 3.8%，淨利 CAGR 約 26.6%——獲利成長主要來自組合／製程／匯兌與業外，而非規模擴張。"
        "2025 年減的主因在美國：對美營收由 1,196,612 降至 610,967 仟元（−48.9%），而荷蘭由 559,808 升至 777,237 仟元（+38.8%），部分抵銷。",
        "Body",
    ))

    story.append(P("3.2 資產負債與財務安全", "H2"))
    story.append(table(
        [
            th("項目", "2023 底", "2024 底", "2025 底"),
            td("現金及約當現金", "（2024 期初 861,419）", "654,346", "1,158,189"),
            td("按攤銷後成本衡量之金融資產—流動", "—", "1,015,659", "893,242"),
            td("透過損益按公允價值—流動", "—", "277,891", "116,746"),
            td("應收帳款淨額", "（2024 期初 291,120）", "495,039", "285,710"),
            td("存貨", "—", "360,129", "395,195"),
            td("流動資產／佔比", "2,644,079／76%", "2,857,276／74%", "2,933,990／77%"),
            td("不動產廠房設備", "353,303", "341,213", "351,535"),
            td("資產總計", "3,456,498", "3,878,330", "3,805,522"),
            td("短期借款", "—", "30,000", "30,000"),
            td("流動負債", "666,634", "821,465", "756,715"),
            td("負債總計／負債比", "985,976／29%", "1,144,915／30%", "997,789／26%"),
            td("權益總計／權益比", "2,470,522／71%", "2,733,415／70%", "2,807,733／74%"),
            td("每股淨值（元，權益÷8,000 萬股）", "30.88", "34.17", "35.10"),
        ],
        [62 * mm, 38 * mm, 38 * mm, 40 * mm],
    ))
    story.append(P("表 3　合併資產負債（官方簡明＋2025 財報）。2023 欄取 2026/02/25 法說簡明合併資產負債表與 2024 財報比較數。", "Caption"))

    story.append(P(
        "流動比 2025＝2,933,990／756,715＝<b>3.88</b> 倍；速動比（扣存貨）＝<b>3.36</b> 倍。"
        "有息負債幾乎只有短期借款 3,000 萬，利息費用 845 仟元，營業利益／利息＝約 <b>391</b> 倍——實質無槓桿。"
        "現金＋流動定存／債券＋FVTPL＝2,168,177 仟元，佔資產 57%；若再加非流動定存／公司債 301,665，金融資產超過 24.7 億。"
        "這是「製造商＋準現金公司」的混合體：本業賺現金，多餘資金放定存、債券與基金（台壽／富邦次順位債各 1 億、受益憑證等）。"
        "HiStock 轉載負債比：2021 年底曾達 48.8%，2022 已降至 29.4%，此後維持 26–30%——去槓桿已完成。",
        "Body",
    ))

    story.append(P("3.3 現金流、股利與資本配置", "H2"))
    story.append(table(
        [
            th("項目", "2024", "2025"),
            td("營業活動現金流入", "489,555", "568,149"),
            td("其中：營運產生（稅前調整後）", "565,163", "661,282"),
            td("購置不動產廠房設備", "(16,401)", "(37,022)"),
            td("投資活動現金流", "(549,458)", "236,804"),
            td("發放現金股利", "(223,998)", "(255,998)"),
            td("融資活動現金流", "(214,654)", "(258,511)"),
            td("期末現金", "654,346", "1,158,189"),
            td("每股現金股利（所屬年度）", "3.20 元（2024 盈餘）", "3.00 元（2025 盈餘，董事會擬議）"),
            td("股利／EPS", "61.1%", "65.8%"),
        ],
        [70 * mm, 54 * mm, 54 * mm],
    ))
    story.append(P("表 4　現金流與股利。來源：2025 合併現金流量表、權益變動表附註 6(15)。2023 盈餘配 2.8 元、2022 盈餘配 2.5 元、2021 盈餘配 1.2 元（HiStock 除權息表；2022–2024 配息金額可與財報現金股利列交叉）。", "Caption"))

    story.append(P(
        "2025 營業現金流 5.68 億＞淨利 3.65 億（OCF／NI＝1.56），主因應收帳款下降 2.09 億（出貨放緩後收回）及 FVTPL 部位減少 1.62 億（此項較接近投資活動，解讀營業現金品質時應打折）。"
        "資本支出極低（PPE 3,702 萬），本業自由現金流充裕，足以覆蓋 2.56 億股利。"
        "配息率連續五年落在約 61–67%（HiStock），符合章程「可分配盈餘至少 10% 作股利、現金股利佔股利 10–100%」且實務上接近高現金配。"
        "2026/02/25 董事會擬配 2025 盈餘每股 3 元（239,998 仟元）。",
        "Body",
    ))

    story.append(P("3.4 獲利能力與週轉", "H2"))
    story.append(table(
        [
            th("比率", "2024", "2025", "算法／來源"),
            td("ROE", "16.11%", "13.16%", left=True),
            td("ROA", "11.44%", "9.51%", left=True),
            td("稅前純益／實收資本", "67.68%", "54.10%", left=True),
            td("存貨週轉（次）", "—", "5.88", left=True),
            td("應收週轉（次）", "—", "7.38", left=True),
            td("應付週轉（次）", "—", "6.36", left=True),
            td("現金轉換週期（日）", "—", "約 54 日", left=True),
        ],
        [48 * mm, 28 * mm, 28 * mm, 74 * mm],
    ))
    story.pop()
    story.append(table(
        [
            th("比率", "2024", "2025", "來源／算法"),
            [
                P("ROE", "TdL"), P("16.11%", "Td"), P("13.16%", "Td"),
                P("114 年報致股東報告書；複核：364,592／平均權益 2,770,574＝13.16%", "TdL"),
            ],
            [
                P("ROA", "TdL"), P("11.44%", "Td"), P("9.51%", "Td"),
                P("同左；複核：364,592／平均資產 3,841,926＝9.49%（四捨五入差）", "TdL"),
            ],
            [
                P("稅前／實收資本", "TdL"), P("67.68%", "Td"), P("54.10%", "Td"),
                P("114 年報致股東報告書", "TdL"),
            ],
            [
                P("存貨週轉", "TdL"), P("—", "Td"), P("5.88 次", "Td"),
                P("銷貨成本 2,221,487／平均存貨 377,662", "TdL"),
            ],
            [
                P("應收週轉", "TdL"), P("—", "Td"), P("7.38 次", "Td"),
                P("營收／平均應收 390,375", "TdL"),
            ],
            [
                P("應付週轉", "TdL"), P("—", "Td"), P("6.36 次", "Td"),
                P("銷貨成本／平均應付 349,327", "TdL"),
            ],
            [
                P("約當現金轉換週期", "TdL"), P("—", "Td"), P("≈54 日", "Td"),
                P("存貨天數 62＋應收 49−應付 57", "TdL"),
            ],
        ],
        [36 * mm, 24 * mm, 26 * mm, 92 * mm],
    ))
    story.append(P("表 5　獲利與週轉。ROE／ROA 以公司年報為準；週轉率為本報告依 2025 財報計算。", "Caption"))

    story.append(P(
        "同業比較（Money-link 轉載、2026Q2 累計）：漢平毛利率 22.11% vs 同業平均 7.24%；營業利益率 11.38% vs 4.32%；純益率 11.44% vs 3.40%；負債比 34.07% vs 60.93%。"
        "「同業」為上市其他電子分類平均，涵蓋異質公司，<b>不能</b>解釋為唱盤 OEM 同業對標，但足以說明漢平在「其他電子」籃子裡屬高毛利、低槓桿的利基製造。"
        "存貨跌價：2025 備抵 13,684（原料為主 12,593），查核關鍵事項即「規格變更導致原料過時」——這是 ODM 結構性風險，不是一次性事件。",
        "Body",
    ))

    story.append(P("3.5 客戶與地區集中度", "H2"))
    story.append(table(
        [
            th("地區營收", "2023", "佔比", "2024", "佔比", "2025", "佔比"),
            td("美國", "786,746", "32.0%", "1,196,612", "37.7%", "610,967", "21.2%"),
            td("荷蘭", "508,346", "20.6%", "559,808", "17.6%", "777,237", "27.0%"),
            td("日本", "304,851", "12.4%", "349,706", "11.0%", "332,256", "11.5%"),
            td("其他（各國&lt;10%）", "836,281", "34.0%", "1,049,253", "33.0%", "1,138,777", "39.5%"),
            td("台灣＋中國", "25,730", "1.0%", "22,202", "0.7%", "23,190", "0.8%"),
            td("合計", "2,461,954", "100%", "3,177,581", "100%", "2,882,427", "100%"),
        ],
        [36 * mm, 24 * mm, 18 * mm, 26 * mm, 18 * mm, 26 * mm, 18 * mm],
    ))
    story.append(P("表 6　地區營收。來源：2024 及 2025 合併財報附註 14(6)。客戶 anonymized。", "Caption"))

    story.append(table(
        [
            th("重大客戶（＞10%）", "2023", "2024", "2025"),
            td("Company D", "535,454", "961,800", "515,660"),
            td("Company C", "408,273", "474,014", "775,646"),
            td("Company F", "370,893", "467,763", "470,689"),
            td("Company A", "339,029", "302,106", "未再列（推定＜10%）"),
            td("上列合計／佔營收", "1,653,649／67.2%", "2,205,683／69.4%", "1,761,995／61.1%"),
        ],
        [44 * mm, 44 * mm, 44 * mm, 46 * mm],
    ))
    story.append(P("表 7　重大客戶。來源：2024 財報附註 14(7)（含 2023 比較）、2025 財報附註 14(7)。2024 之 A 佔比 9.5%，嚴格說低於 10% 門檻但仍被列示。", "Caption"))

    story.append(P(
        "集中度含義：任一國際品牌砍單即可移動全年營收兩個百分點以上。"
        "2024 年 Company D 跳到 9.62 億（推定對應美國高峰），2025 回落到 5.16 億，與對美營收腰斬同方向。"
        "Company C 2025 升至 7.76 億，與荷蘭成為第一大地區同方向——歐洲客戶在 2025 成為穩定錨。"
        "Company F 連續三年約 3.7–4.7 億，是最穩的第三支柱。"
        "財報未揭露品牌名稱，本報告<b>不臆測</b>對應 Audio-Technica／Technics／Pioneer DJ（AlphaTheta）／Numark 等。",
        "Body",
    ))

    story.append(P("3.6 季節性與 2026 年進度", "H2"))
    story.append(P(
        "單季營收長期呈現「Q1 淡、Q3 旺」：2025 為 5.79／7.20／8.50／7.35 億；2024 為 4.27／7.01／9.98／10.52 億（Q4 因美國拉貨而異常強）。"
        "2026H1（董事會 2026/08/03 通過）：營收 1,543,276（+18.9%）、毛利 341,195（毛利率 22.11%）、營業利益 175,634（11.38%）、稅前 221,138、稅後 176,477、EPS 2.21 元。"
        "期末資產 4,212,812、負債 1,435,430、權益 2,777,382——資產較 2025 年底增加，負債比升至約 34%（Money-link 2026Q2 累計 34.07%），符合上半年備料／應收擴張的製造季節性，不宜直接解讀為財務惡化。"
        "月營收（HiStock／PChome 轉載公開資訊觀測站）：2026 年 1–7 月合計 <b>1,920,467</b> 仟元，相對 2025 年同期 1,536,501 年增 <b>25.0%</b>；7 月單月 377,191（+58.2% YoY）。"
        "這是事實進度，不是全年財測。H2 是否延續，取決於美國客戶是否持續回補、以及往年 Q3 旺季能否再現。",
        "Body",
    ))

    story.append(table(
        [
            th("2026 月營收", "金額", "YoY", "累計", "累計 YoY"),
            td("1 月", "229,505", "+31.9%", "229,505", "+31.9%"),
            td("2 月", "161,774", "+0.1%", "391,279", "+16.6%"),
            td("3 月", "208,728", "−14.0%", "600,007", "+3.7%"),
            td("4 月", "303,410", "+29.8%", "903,417", "+11.2%"),
            td("5 月", "283,019", "+26.5%", "1,186,436", "+14.5%"),
            td("6 月", "356,840", "+36.2%", "1,543,276", "+18.9%"),
            td("7 月", "377,191", "+58.2%", "1,920,467", "+25.0%"),
        ],
        [32 * mm, 32 * mm, 28 * mm, 38 * mm, 36 * mm],
    ))
    story.append(P("表 8　2026 年月營收。來源：HiStock／PChome 轉載之上市櫃合併營收（與 6 月底累計 1,543,276 恰等於 H1 財報營收，交叉驗證通過）。", "Caption"))

    story.append(P("3.7 五年財務結論（可證偽）", "H2"))
    for b in [
        "品質：高現金、低負債、高配息、本業持續正營業利益——財務失敗風險極低。",
        "成長：營收不是成長股軌跡，是訂單循環股；獲利五年上台階後在 3.5–4.2 億區間震盪。",
        "結構風險：客戶前三約 60%、產能在深圳、需求在美歐日——地緣與關稅是第一風險，不是利息或流動性。",
        "2025 是「美國去化年」；2026 截至 7 月是「回補年」。能否把回補變成新的營收平台，要看 H2 與大客戶 2027 年規劃，目前沒有公司財測可引用。",
    ]:
        story.append(P("• " + b, "BodyBullet"))

    story.append(P("4. 產業未來五年前景（2026–2030）", "H1"))
    story.append(P(
        "漢平同時站在三條需求曲線上：①全球專業音訊設備；②黑膠／唱盤硬體；③消費性音響與 DJ 文化的數位化周邊（MIDI、音頻介面、無線）。三者增速不同，不能用單一 CAGR 外推公司營收。",
        "Body",
    ))

    story.append(P("4.1 專業音訊設備", "H2"))
    story.append(P(
        "Global Industry Analysts／Research and Markets（2026 年 8 月刊）：全球 Professional Audio Equipment 2024 年估 213 億美元，2030 年 290 億，<b>CAGR 5.3%</b>（2024–2030）。"
        "美國 2024 年約 58 億；中國 2030 年估 59 億（CAGR 8.5%）；日本 CAGR 約 2.5%、德國約 3.4%。"
        "混音器、麥克風子類 CAGR 約 6.6%。驅動因子（該報告摘要）：現場演出與串流內容的音質升級、無線化、工作室／活動製作、汽車與家用娛樂的專業化滲透。"
        "這條曲線對漢平的意義：Pro-Audio／DJ 混音器、控制器、播放器有中個位數的名義增長天花板；要賺到高於 5% 的公司增長，必須靠<b>單價上移或市佔</b>，不能指望產業beta。",
        "Body",
    ))

    story.append(P("4.2 黑膠與唱盤", "H2"))
    story.append(P(
        "RIAA 2025 年終報告（2026/03/16）：美國黑膠批發收入 10.429 億美元（+9.3%），銷量 4,680 萬張（+7.9%），連續第 19 年成長，約佔全球黑膠產值近 50%；實體格式總收入 13.8 億，黑膠遠高於 CD（3.124 億、2,950 萬張、收入 −7.8%）。"
        "須注意：RIAA 自 2025 年起改以批發價值為主，與早年零售估值<b>不可直接接龍</b>。"
        "唱盤硬體研調區間分歧：MarketIntelo 稱 2025 年全球唱盤市場 12 億美元、2034 年 19 億、2026–2034 CAGR 5.8%；WorldMetrics 另一組數字稱 2023 年 12 億、2032 年 23 億、CAGR 9.2%。"
        "<b>兩組不能平均、也不能選高的用</b>——本報告只採「未來五年全球唱盤硬體大概率落在中高個位數 CAGR、且直驅／專業 DJ 子類快於皮帶入門機」這一與多份摘要一致的方向，不採單一點預測為真。",
        "Body",
    ))
    story.append(P(
        "漢平 114 年報自己的產業判斷更保守、也更接近經營現實：2026 年黑膠已進入「精品收藏化」與「利基成長」，並點名成品出口的關稅韌性。"
        "IndexBox 對專業唱盤的質化描述亦同：入門紅利消退後，價值成長將快於量；直驅佔比上升；OEM 白牌在中階將被擠壓。"
        "對漢平：量的紅利（2020–2024 那波「人人買入門唱盤」）正在結束；活路是 Hi-Fi 高階、高扭力直驅、數位黑膠介面——這與公司 2026 研發清單一致。",
        "Body",
    ))

    story.append(P("4.3 數位／類比整合與鄰近市場", "H2"))
    story.append(P(
        "Grand View Research：全球無線麥克風 2025 年 26.1 億美元、2033 年 48.4 億，2026–2033 CAGR 8.1%；DAW 軟體 2025 年 43.9 億、2033 年 88.5 億，CAGR 9.4%。"
        "漢平並非麥克風或 DAW 公司，但 114 年報明確要做：MIDI＋多通道聲卡、唱盤＋電腦／行動裝置／顯示器、無線與 APP、混音器升級為帶 DSP／音頻介面的數位混音器。"
        "鄰近市場較快的 CAGR 提供的是「產品單價與黏著度」的選擇權，不是自動營收。執行風險在韌體／軟體人才與品牌客戶是否願意把這層價值分給 OEM。",
        "Body",
    ))

    story.append(P("4.4 總體與法規環境（公司已引用）", "H2"))
    story.append(P(
        "114 年報引 IMF 2025 年 10 月預測：全球貿易量增速由 2025 年 3.6% 降至 2026 年 2.3%，並點名美國關稅、中國產業調整、AI、地緣與氣候。"
        "「提前備貨效應消退」寫進致股東報告書——這與 2024Q4 對美爆量、2025 年對美腰斬的財報數字互證。"
        "未來五年只要美對中（或對轉口）消費電子關稅不退，深圳製造的漢平就會持續面對：客戶要求移轉產地、FOB 漲價被拒、或品牌把低階單交給東南亞競爭者。",
        "Body",
    ))

    story.append(P("5. 公司未來五年前景（分析情境，非財測）", "H1"))
    story.append(P(
        "公司未公布 2026–2030 營收或 EPS 指引。以下三個情境是本報告的分析架構，用來把已揭露事實排成可檢驗命題，<b>不是</b>預測值。",
        "Body",
    ))

    story.append(P("5.1 基準情境（較可能）", "H2"))
    for b in [
        "營收：在 28–34 億元區間波動，中位緩慢上移。2026 年若 H2 不出現 2024 式透支，全年有機會收復或略過 2024 的 31.8 億；但不能把 1–7 月 +25% 年增直線外推到 36 億以上。",
        "獲利：毛利率穩定在 21–24%（低於 2023 高峰、高於 2021）。EPS 中樞 4–5.5 元，配息 2.8–3.5 元。ROE 落在 12–16%。",
        "產品：高階唱盤與 MIDI／介面佔比緩升，入門皮帶機價格戰，整體量平、值微增。",
        "地理：歐洲（荷蘭）與「其他」分散地區補美國波動；美國不再回到 2024 年 38% 佔比，除非出現新的大客戶導入。",
    ]:
        story.append(P("• " + b, "BodyBullet"))

    story.append(P("5.2 樂觀情境（需同時滿足）", "H2"))
    for b in [
        "品牌客戶把高階直驅／Hi-Fi 專案放量，且漢平拿到數位黑膠／無線模組的 NRE＋量產。",
        "關稅上，客戶接受轉嫁或把「台灣設計＋第三地組裝」方案落地（目前公開資料未證實已有越南／墨西哥產能）。",
        "黑膠量續增而非平台期，專業 DJ 直驅 CAGR 高於整體唱盤（MarketIntelo 摘要稱專業 DJ 應用約 7.1%）。",
        "若以上成立，營收才有機會在五年內站上明顯高於 35 億的新平台；這是選擇權，不是基準。",
    ]:
        story.append(P("• " + b, "BodyBullet"))

    story.append(P("5.3 保守情境", "H2"))
    for b in [
        "美國關稅或品牌「China+1」把中低階訂單移走；前三大任一流失且 12 個月內補不回。",
        "黑膠量見頂、入門機價格戰，毛利率跌破 20%。",
        "結果：營收回到 24–28 億、EPS 3 元上下。財務仍不太可能虧損（現金與低固定成本結構是緩衝），但估值與配息會下修。",
    ]:
        story.append(P("• " + b, "BodyBullet"))

    story.append(P("5.4 2026 年可檢驗里程碑（到 2027 年報即可對照）", "H2"))
    for b in [
        "2026 全年營收是否至少持平或超過 2025 的 28.82 億（YTD 已大幅領先，門檻低；真正的檢驗是否接近／超過 2024 的 31.78 億）。",
        "毛利率是否守住 22%（H1 已是 22.11%，H2 若為衝量可能再壓）。",
        "對美營收佔比是否從 21% 回升、以及 Company D 是否止跌。",
        "年報研發清單是否出現可出貨的高階／無線／數位黑膠 SKU，而不只是「預計開發」。",
        "中國以外製造是否有具體資本支出或投資公告（目前 2025 年 PPE 僅 3.7 億帳面、當年購置 3,702 萬，看不出新基地）。",
    ]:
        story.append(P("• " + b, "BodyBullet"))

    story.append(P("6. 全球競爭力評估", "H1"))
    story.append(P("6.1 漢平在價值鏈的位置", "H2"))
    story.append(P(
        "漢平不是面向消費者的品牌商，而是「全球專業音訊業者的策略伙伴」（114 年報產銷政策原文）：從概念、工業設計、規格、量產、包裝到物流的一條龍 ODM。"
        "官網產品型錄以自有型號（DJ-U1160、BJ-U1000 等）展示直驅／皮帶唱盤能力，實際出貨以客戶品牌為主。"
        "價值鏈上，品牌商（Audio-Technica、Technics／Panasonic、AlphaTheta／Pioneer DJ、inMusic／Numark、Reloop、Pro-Ject、Thorens 等）掌握通路與溢價；"
        "精密唱頭、部分馬達仍高度依賴日歐供應（IndexBox 供應鏈描述）。漢平的可防守資產是：唱盤機構／直驅馬達製程 know-how、DJ 產品認證與多年客戶關係、台南研發＋深圳成本的組合。",
        "Body",
    ))

    story.append(P("6.2 競爭力矩陣（質化，附證據）", "H2"))
    story.append(table(
        [
            th("構面", "評等", "證據"),
            [
                P("財務韌性", "TdL"), P("強", "Td"),
                P("淨現金、負債比 26%、利息保障極高、配息穩定", "TdL"),
            ],
            [
                P("製造成本", "TdL"), P("中偏強", "Td"),
                P("深圳量產＋台灣接單；但關稅正在侵蝕此優勢", "TdL"),
            ],
            [
                P("產品深度", "TdL"), P("中偏強", "Td"),
                P("直驅／皮帶唱盤、MIDI、混音器、播放器齊；高階 Hi-Fi 仍在加碼期", "TdL"),
            ],
            [
                P("技術升級", "TdL"), P("中", "Td"),
                P("研發佔營收 4%；方向對（數位介面／無線），尚未看到軟體平台級護城河", "TdL"),
            ],
            [
                P("客戶結構", "TdL"), P("弱至中", "Td"),
                P("前三約 61%；2024–2025 單一客戶大進大出", "TdL"),
            ],
            [
                P("地理需求", "TdL"), P("中", "Td"),
                P("美歐日主力，已證歐可補美；新興市場未在財報單列", "TdL"),
            ],
            [
                P("產地多元", "TdL"), P("弱", "Td"),
                P("製造利潤在深圳；無公開的中國以外量產基地", "TdL"),
            ],
            [
                P("品牌／定價權", "TdL"), P("弱至中", "Td"),
                P("OEM 本質；年報想「北美歐洲品牌溢價」是意圖而非已實現品牌", "TdL"),
            ],
            [
                P("ESG／治理", "TdL"), P("中", "Td"),
                P("法說含 ESG 頁；董座兼總經理（職能未分離）；配發基層員工酬勞條款已入章", "TdL"),
            ],
        ],
        [32 * mm, 24 * mm, 122 * mm],
    ))
    story.append(P("表 9　全球競爭力質化矩陣。評等為本報告分析意見。", "Caption"))

    story.append(P("6.3 對全球競爭者的相對位置", "H2"))
    story.append(P(
        "品牌層：Technics 在高端直驅的文化符號、Audio-Technica 在入門到中階的零售覆蓋、AlphaTheta 在俱樂部 DJ 生態，都不是漢平要正面取代的對象；漢平的戰場是「這些品牌（及第二層歐洲品牌）要把多少機種交給哪一家亞洲 ODM」。"
        "製造層：中國珠三角仍有大量消費音響白牌與 OEM，價格戰能力不弱於漢平；漢平的差異化必須是良率、認證、DJ 機構精度、以及能做小量高階的彈性——查核報告也承認原料規格變更會造成過時庫存，代表客製化是雙刃。"
        "五年競爭力消長關鍵不在「會不會做唱盤」（這門手藝漢平已做數十年），而在：①高階製程是否被品牌承認；②能否把數位介面做成客戶離不開的模組；③產地選項是否出現。缺一，則全球角色停留在「優質但可替代的亞洲 ODM」。",
        "Body",
    ))

    story.append(P("6.4 關稅與供應鏈：競爭力的最大外生變數", "H2"))
    story.append(P(
        "2025 年對美營收腰斬，是近年最強的壓力測試：公司沒有因此虧損，毛利率只從 24.4% 降到 22.9%，證明固定成本低、能縮。"
        "但也證明需求地理集中時，一年可以少掉 6 億營收。"
        "未來五年若美國維持對中製消費電子的高關稅，漢平的全球競爭力分數會被「產地」一項持續扣分，即使產品工程是加分。"
        "年報已把「關稅韌性」寫成高階黑膠策略的一部分——意思是高單價較能吸收關稅。這在邏輯上成立，但要把公司從 29 億營收做出結構性成長，仍需要客戶在高階機種上的份額，而不只是同機種漲價。",
        "Body",
    ))

    story.append(P("7. 主要風險清單", "H1"))
    story.append(table(
        [
            th("風險", "機制", "已觀察訊號"),
            [
                P("大客戶流失", "TdL"),
                P("前三約 60%；單一客戶年減可達數億", "TdL"),
                P("Company D：9.62→5.16 億（2024→2025）", "TdL"),
            ],
            [
                P("美國關稅／去中", "TdL"),
                P("深圳製造、美國曾為第一大市場", "TdL"),
                P("對美 12.0→6.1 億；年報點名關稅與備貨消退", "TdL"),
            ],
            [
                P("黑膠週期見頂", "TdL"),
                P("唱盤是核心能力所在", "TdL"),
                P("公司自述進入利基成長；研調 CAGR 分歧", "TdL"),
            ],
            [
                P("存貨過時", "TdL"),
                P("ODM 客製原料；查核關鍵事項", "TdL"),
                P("2025 備抵 13,684，原料為主", "TdL"),
            ],
            [
                P("匯兌", "TdL"),
                P("營收外幣、成本人民幣、報表台幣", "TdL"),
                P("2024 兌換利益 50,712 vs 2025 僅 10,935", "TdL"),
            ],
            [
                P("業外與金融資產", "TdL"),
                P("大量定存／債券／基金；利率下行降利息收入", "TdL"),
                P("2025 利息收入 64,358（佔稅前 15%）", "TdL"),
            ],
            [
                P("關鍵人", "TdL"),
                P("董事長兼總經理兼發言人", "TdL"),
                P("治理職能未分離（事實，非違法）", "TdL"),
            ],
            [
                P("出口截止認定", "TdL"),
                P("外銷控制權移轉時點為查核關鍵事項", "TdL"),
                P("PwC 2025 查核強調 cut-off", "TdL"),
            ],
        ],
        [32 * mm, 58 * mm, 88 * mm],
    ))
    story.append(P("表 10　風險。均有財報或年報對應。", "Caption"))

    story.append(P("8. 總結", "H1"))
    story.append(P(
        "漢平近五年交出的是一份「小而美的利基製造商」成績單：營收不大、獲利與現金流很好、股東以現金股利參與、幾乎沒有財務槓桿風險。"
        "它不是高成長電子股，也不是會因為黑膠新聞而線性爆發的故事股。"
        "未來五年，產業給它的 beta 大約是專業音訊 5% 左右、唱盤硬體中高個位數且結構上移；alpha 只能來自高階化與數位整合是否被品牌客戶買單，以及產地風險是否被管理。"
        "2026 年截至 7 月的 +25% 營收是真實的近端證據，顯示 2025 年的美國缺口正在補；但要把這段回補寫成五年新平台，還缺少產地第二引擎與客戶結構下降的證據。"
        "在證據出現前，合理的基本假設是：<b>續當高配息、高現金的週期性 ODM，全球角色穩固但可替代；上行選擇權存在，尚未被財報證實已經行使。</b>",
        "Body",
    ))

    story.append(P("附錄 A　來源與取數邊界", "H1"))
    rows = [
        ("S1", "漢平 2025／2024 合併財報（英文）", "http://www.hanpin.com.tw/Finance/Investors_06_01_114Q4AE.pdf", "損益、資產負債、現金流、地區、客戶、大陸投資、股利"),
        ("S2", "漢平 2024／2023 合併財報（英文）", "http://www.hanpin.com.tw/Finance/Investors_06_01_113Q4AE.pdf", "2023 地區與客戶比較數"),
        ("S3", "2026/02/25 法說簡報（中／英）", "hanpin.com.tw/Finance/ 漢平2026年法說簡報", "2023–2025 簡明損益與資產負債、公司概況"),
        ("S4", "114 年報致股東報告書", "公開資訊觀測站／treelazy 轉載", "ROA／ROE、研發清單、2026 策略、IMF 引述、產銷政策"),
        ("S5", "2026/08/03 董事會 H1 財報公告", "MoneyDJ 轉載 MOPS", "2026H1 營收至 EPS、期末資產負債"),
        ("S6", "月營收", "HiStock／PChome 轉載 MOPS", "2026 年 1–7 月；6 月累計與 H1 財報交叉驗證"),
        ("S7", "季報加總 2021–2022", "HiStock 損益表", "方法：2023–2025 加總＝官方年報，回溯同口徑"),
        ("S8", "股利與每股淨值、負債比", "HiStock；nStock；Money-link", "2021–2025 配息；負債比 2021 高點"),
        ("S9", "公司官網", "hanpin.com.tw About／Products", "產品線、860 人、ISO、據點"),
        ("S10", "RIAA 2025 Year-End", "riaa.com 2026/03/16；Billboard 引述", "美國黑膠 46.8M 張、10.43 億美元"),
        ("S11", "專業音訊市場", "GII／Research and Markets 摘要，2026-08", "213→290 億美元，CAGR 5.3%"),
        ("S12", "唱盤市場研調", "MarketIntelo；WorldMetrics", "僅作區間，不取單一點為真"),
        ("S13", "鄰近市場", "Grand View Research 公開摘要", "無線麥克風、DAW CAGR"),
    ]
    src_data = [th("代號", "文件", "位置", "使用欄位")]
    for a, b, c, d in rows:
        src_data.append([P(a, "Td"), P(b, "TdL"), P(c, "TdL"), P(d, "TdL")])
    story.append(table(src_data, [14 * mm, 48 * mm, 52 * mm, 64 * mm]))
    story.append(P("表 11　來源。本雲端任務未使用 FinMind／FRED API，亦未連 augur PostgreSQL。", "Caption"))

    story.append(P("附錄 B　計算底稿（本報告自行計算者）", "H1"))
    story.append(P(
        "營收 CAGR 2021–2025＝(2,882,427／2,485,647)^(1/4)−1＝3.77%。"
        "淨利 CAGR＝(364,592／142,031)^(1/4)−1＝26.6%。"
        "2025 毛利率＝660,940／2,882,427＝22.93%；營業利益率＝330,466／2,882,427＝11.46%；純益率＝12.65%。"
        "前三大 2025＝(775,646+515,660+470,689)／2,882,427＝61.1%。"
        "對美 2025 年增＝610,967／1,196,612−1＝−48.9%；荷蘭＝777,237／559,808−1＝+38.8%。"
        "2026H1 營收年增＝1,543,276／1,298,039−1＝18.89%（分母為 2025H1 月營收累計，與季報加總 578,502+719,537＝1,298,039 一致）。",
        "Body",
    ))
    story.append(P(
        "報告日 2026-08-27。後續月營收、2026Q3 財報與關稅政策若發布，應覆蓋本備忘之近端敘事；五年結構判斷（ODM、深圳製造、高現金、客戶集中）在公司未宣布產地或客戶結構重大變化前維持。",
        "Note",
    ))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="2488 漢平｜近五年財務分析與未來五年前景／全球競爭力",
        author="Augur public-information research memo",
        subject="Hanpin Electron 2488 financial analysis 2021-2025 and 2026-2030 outlook",
    )
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print("WROTE", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    build()
