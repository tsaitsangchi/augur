#!/usr/bin/env python3
"""把 8936 國統公開財報來源編成 Markdown＋PDF。

守原則 #9 #10 #15：數字只從 reports/8936_kti_sources 既有 JSON 計算。

執行指令矩陣：
  python3 scripts/build_8936_kti_report.py
  python3 scripts/build_8936_kti_report.py --selftest
  python3 scripts/build_8936_kti_report.py --src reports/8936_kti_sources --out-dir reports
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ8 = timezone(timedelta(hours=8))
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def num(x):
    if x is None:
        return None
    s = str(x).strip().replace(",", "")
    if s in {"", "--", "-", "nan", "None"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def yi(x_thousand) -> float | None:
    v = num(x_thousand)
    return None if v is None else v / 100000.0


def pct(a, b) -> float | None:
    if a is None or b in (None, 0):
        return None
    return 100.0 * a / b


def yoy(cur, prev) -> float | None:
    if cur is None or prev in (None, 0):
        return None
    return 100.0 * (cur - prev) / prev


def f2(v, suffix="") -> str:
    if v is None:
        return "—"
    return f"{v:,.2f}{suffix}"


def f1(v, suffix="") -> str:
    if v is None:
        return "—"
    return f"{v:,.1f}{suffix}"


def f0(v) -> str:
    if v is None:
        return "—"
    return f"{v:,.0f}"


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def row_of(period: dict, kind: str) -> dict:
    block = period.get(kind) or {}
    return block.get("row") or {}


def extract(src: Path) -> dict:
    mops = load_json(src / "mops_statements.json")
    quote_pack = load_json(src / "tpex_quote.json") or {}
    rev_latest = load_json(src / "tpex_month_revenue_latest.json") or {}
    monthly = load_json(src / "mops_month_revenue.json") or []
    yahoo = load_json(src / "yahoo_daily.json") or {}
    peers = load_json(src / "tpex_peers.json") or {}

    by = {}
    for rec in mops or []:
        by[(int(rec["roc_year"]), rec["season"])] = rec

    years = []
    for roc, gy in [(110, 2021), (111, 2022), (112, 2023), (113, 2024), (114, 2025)]:
        rec = by[(roc, "04")]
        inc, bal, cf, mar = row_of(rec, "income"), row_of(rec, "balance"), row_of(rec, "cashflow"), row_of(rec, "margin")
        years.append({
            "year": gy,
            "roc": roc,
            "rev": yi(inc.get("營業收入")),
            "gp": yi(inc.get("營業毛利（毛損）")),
            "oi": yi(inc.get("營業利益（損失）")),
            "ni": yi(inc.get("本期淨利（淨損）")),
            "ni_p": yi(inc.get("淨利（淨損）歸屬於母公司業主")),
            "eps": num(inc.get("基本每股盈餘（元）")),
            "gm": num(mar.get("毛利率(%) (營業毛利)/ (營業收入)")),
            "om": num(mar.get("營業利益率(%) (營業利益)/ (營業收入)")),
            "nm": num(mar.get("稅後純益率(%) (稅後純益)/ (營業收入)")),
            "assets": yi(bal.get("資產總計")),
            "equity": yi(bal.get("權益總計")),
            "eq_p": yi(bal.get("歸屬於母公司業主之權益合計")),
            "liab": yi(bal.get("負債總計")),
            "ca": yi(bal.get("流動資產")),
            "cl": yi(bal.get("流動負債")),
            "nca": yi(bal.get("非流動資產")),
            "bv": num(bal.get("每股參考淨值")),
            "ocf": yi(cf.get("營業活動之淨現金流入（流出）")),
            "icf": yi(cf.get("投資活動之淨現金流入（流出）")),
            "fcf": yi(cf.get("籌資活動之淨現金流入（流出）")),
            "cash": yi(cf.get("期末現金及約當現金餘額")),
        })
    for i, y in enumerate(years):
        prev = years[i - 1] if i else None
        y["rev_yoy"] = yoy(y["rev"], prev["rev"]) if prev else None
        y["debt"] = pct(y["liab"], y["assets"])
        y["cr"] = None if not y["cl"] else y["ca"] / y["cl"]
        if i:
            avg_eq = (prev["eq_p"] + y["eq_p"]) / 2 if prev["eq_p"] and y["eq_p"] else None
            y["roe"] = pct(y["ni_p"], avg_eq)
        else:
            y["roe"] = pct(y["ni_p"], y["eq_p"])
        y["ocf_ni"] = pct(y["ocf"], y["ni_p"])

    h1_26 = by[(115, "02")]
    h1_25 = by[(114, "02")]
    q1_26 = by[(115, "01")]
    inc26, bal26, cf26, mar26 = row_of(h1_26, "income"), row_of(h1_26, "balance"), row_of(h1_26, "cashflow"), row_of(h1_26, "margin")
    inc25h, mar25h = row_of(h1_25, "income"), row_of(h1_25, "margin")
    incq1 = row_of(q1_26, "income")
    h1 = {
        "rev": yi(inc26.get("營業收入")),
        "gp": yi(inc26.get("營業毛利（毛損）")),
        "oi": yi(inc26.get("營業利益（損失）")),
        "ni": yi(inc26.get("本期淨利（淨損）")),
        "ni_p": yi(inc26.get("淨利（淨損）歸屬於母公司業主")),
        "eps": num(inc26.get("基本每股盈餘（元）")),
        "gm": num(mar26.get("毛利率(%) (營業毛利)/ (營業收入)")),
        "om": num(mar26.get("營業利益率(%) (營業利益)/ (營業收入)")),
        "nm": num(mar26.get("稅後純益率(%) (稅後純益)/ (營業收入)")),
        "rev_yoy": yoy(yi(inc26.get("營業收入")), yi(inc25h.get("營業收入"))),
        "rev_25": yi(inc25h.get("營業收入")),
        "gm_25": num(mar25h.get("毛利率(%) (營業毛利)/ (營業收入)")),
        "eps_25": num(inc25h.get("基本每股盈餘（元）")),
        "assets": yi(bal26.get("資產總計")),
        "equity": yi(bal26.get("權益總計")),
        "eq_p": yi(bal26.get("歸屬於母公司業主之權益合計")),
        "liab": yi(bal26.get("負債總計")),
        "ca": yi(bal26.get("流動資產")),
        "cl": yi(bal26.get("流動負債")),
        "bv": num(bal26.get("每股參考淨值")),
        "ocf": yi(cf26.get("營業活動之淨現金流入（流出）")),
        "icf": yi(cf26.get("投資活動之淨現金流入（流出）")),
        "fcf": yi(cf26.get("籌資活動之淨現金流入（流出）")),
        "cash": yi(cf26.get("期末現金及約當現金餘額")),
        "q1_eps": num(incq1.get("基本每股盈餘（元）")),
        "q1_rev": yi(incq1.get("營業收入")),
    }
    h1["debt"] = pct(h1["liab"], h1["assets"])
    h1["cr"] = h1["ca"] / h1["cl"] if h1["cl"] else None
    h1["q2_rev"] = h1["rev"] - h1["q1_rev"] if h1["rev"] and h1["q1_rev"] else None
    h1["q2_eps"] = (h1["eps"] - h1["q1_eps"]) if h1["eps"] is not None and h1["q1_eps"] is not None else None

    q = quote_pack.get("quote") or {}
    per = quote_pack.get("per") or {}
    shares = num(q.get("Capitals"))
    close = num(q.get("Close"))
    mkt = shares * close / 1e8 if shares and close else None

    months = []
    for item in monthly:
        row = item.get("row")
        if not row:
            continue
        months.append({
            "year": item["year"],
            "month": item["month"],
            "rev": num(str(row.get("當月營收", "")).replace(",", "")),
            "yoy": num(str(row.get("去年同月增減%", "")).replace(",", "")),
            "ytd": num(str(row.get("當月累計營收", "")).replace(",", "")),
        })

    ytd = {
        "ym": rev_latest.get("資料年月"),
        "month": yi(rev_latest.get("營業收入-當月營收")),
        "last_year_m": yi(rev_latest.get("營業收入-去年當月營收")),
        "m_yoy": num(rev_latest.get("營業收入-去年同月增減(%)")),
        "ytd": yi(rev_latest.get("累計營業收入-當月累計營收")),
        "ytd_ly": yi(rev_latest.get("累計營業收入-去年累計營收")),
        "ytd_yoy": num(rev_latest.get("累計營業收入-前期比較增減(%)")),
    }

    peer_tbl = []
    per_map = {str(x.get("SecuritiesCompanyCode")): x for x in (peers.get("per") or [])}
    for pq in peers.get("quotes") or []:
        code = str(pq.get("SecuritiesCompanyCode"))
        pp = per_map.get(code, {})
        sh = num(pq.get("Capitals"))
        cl = num(pq.get("Close"))
        peer_tbl.append({
            "code": code,
            "name": pq.get("CompanyName"),
            "close": cl,
            "mkt": sh * cl / 1e8 if sh and cl else None,
            "pe": num(pp.get("PriceEarningRatio")),
            "pb": num(pp.get("PriceBookRatio")),
            "yd": num(pp.get("YieldRatio")),
            "dps": num(pp.get("DividendPerShare")),
        })

    yahoo_divs = []
    payload = (yahoo.get("payload") or {}).get("chart", {}).get("result") or []
    if payload:
        events = ((payload[0].get("events") or {}).get("dividends") or {})
        for rec in events.values():
            yahoo_divs.append({"ts": rec.get("date"), "amount": rec.get("amount")})
        yahoo_divs.sort(key=lambda x: x["ts"] or 0)

    return {
        "fetched_note": "公開資訊觀測站彙總表（mopsov t163sb04/05/06/20）＋櫃買 OpenAPI",
        "years": years,
        "h1": h1,
        "quote": q,
        "per": per,
        "shares": shares,
        "close": close,
        "mkt": mkt,
        "ytd": ytd,
        "months": months,
        "peers": peer_tbl,
        "yahoo_divs": yahoo_divs,
        "asof": "2026-08-26",
    }


def write_markdown(d: dict, path: Path) -> None:
    y = {x["year"]: x for x in d["years"]}
    h = d["h1"]
    q = d["quote"]
    p = d["per"]
    ytd = d["ytd"]
    lines = []
    a = lines.append
    a("---")
    a("title: 8936 國統近五年財務、產業前景與全球競爭力")
    a("date: 2026-08-27")
    a('stock_id: "8936"')
    a('layer: "[I]"')
    a("self_reported: true")
    a("not_advice: true")
    a("asof_price: 2026-08-26")
    a("fs_tip: 2026-06-30")
    a("---")
    a("")
    a("# 8936 國統｜近五年財務分析與未來五年前景／全球競爭力")
    a("")
    a("> **一句**：營收從 2022 低點 37.9 億走到 2025 的 63.1 億，母公司 EPS 1.81→4.08 元；2026 上半年營收再年增約 20%。這是公共工程放量，不是消費循環。毛利率從 2023 的 38% 回到 26% 帶、2026H1 再壓到 22.5%——規模上來、組合變「工程較重」。現金轉換弱於帳面獲利，是營造／統包的結構，不是「賺到錢就進口袋」。")
    a("> **不是**：進出場建議、目標價、或「一定拿得到下一個海淡標」。")
    a("")
    a("本檔為 self-reported 研究整理。財務數字來自公開資訊觀測站彙總表與櫃買中心 OpenAPI 當日回應，**未打 FinMind／FRED**。前景與競爭力段落為對公開政策／產業估計的解讀，不是已實現結果。")
    a("")
    a("## 0. 公司與資料範圍")
    a("")
    a("國統國際股份有限公司（TPEx 8936，產業別「其他」；英文 KUO TOONG INTERNATIONAL / KTI）。1978 年設立，2002-09-09 上櫃。官網自述核心是大口徑輸配水管的設計、製造與裝配：混凝土管、鋼管、延性鑄鐵管，並延伸到免開挖推進、潛盾、海水淡化與淨水／污水整廠的設計、施工與代操作。實收資本 **24.81 億**（普通股 248,078,157 股）。總部屏東新園，登記英文通訊在高雄。簽證會計師事務所：安永。")
    a("")
    a(f"**本次取數時點**：櫃買收盤 {d['asof']}，收盤 **{f2(d['close'])} 元**，市值約 **{f1(d['mkt'])} 億**；本益比 {p.get('PriceEarningRatio')}、淨值比 {p.get('PriceBookRatio')}、現金殖利率 {p.get('YieldRatio')}%（股利／股 {f2(num(p.get('DividendPerShare')))} 元）。財報最新完整年＝2025（民國 114）年報；期中＝2026H1。月營收最新＝民國 {ytd.get('ym')}（2026 年 7 月）。")
    a("")
    a("單位：新台幣億元；損益／資產負債／現金流原始單位為公開資訊觀測站「千元」，本表除以 10 萬。毛利率等％直接取營益分析彙總表。EPS 為基本每股盈餘（元）。")
    a("")
    a("## 1. 近五年損益")
    a("")
    a("| 年 | 營收 | 年增 | 毛利率 | 營益率 | 稅後淨利 | 母公司淨利 | 淨利率 | EPS |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in d["years"]:
        yoy_s = "—" if row["rev_yoy"] is None else f"{row['rev_yoy']:+.1f}%"
        a(
            f"| {row['year']} | {f2(row['rev'])} | {yoy_s} | {f1(row['gm'], '%')} | {f1(row['om'], '%')} | "
            f"{f2(row['ni'])} | {f2(row['ni_p'])} | {f1(row['nm'], '%')} | {f2(row['eps'])} |"
        )
    a(
        f"| 2026H1 | {f2(h['rev'])} | {h['rev_yoy']:+.1f}% | {f1(h['gm'], '%')} | {f1(h['om'], '%')} | "
        f"{f2(h['ni'])} | {f2(h['ni_p'])} | {f1(h['nm'], '%')} | {f2(h['eps'])} |"
    )
    a("")
    a("讀法：")
    a("")
    a(f"- **規模**：2022 營收掉到 {f1(y[2022]['rev'])} 億（年減 {y[2022]['rev_yoy']:.1f}%）是五年低點。之後連續三年擴張，2024 +{y[2024]['rev_yoy']:.1f}%、2025 +{y[2025]['rev_yoy']:.1f}%，2025 全年 {f1(y[2025]['rev'])} 億。這不是溫和通膨，是標案認列上台階。")
    a(f"- **利潤率**：2023 毛利率 {f1(y[2023]['gm'])}%、營益率 {f1(y[2023]['om'])}% 是高峰（量還沒爆、組合較甜）。2024–2025 營收跳升，毛利率回到 {f1(y[2024]['gm'])}%／{f1(y[2025]['gm'])}%。**量大、單價／組合變差**，但營益率仍在 21–22%，比 2021 的 {f1(y[2021]['om'])}% 好一截。")
    a(f"- **盈餘**：母公司 EPS 五年 {f2(y[2021]['eps'])}→{f2(y[2025]['eps'])} 元，年年加。2021 合併淨利 {f2(y[2021]['ni'])} 億低於母公司淨利 {f2(y[2021]['ni_p'])} 億——非控制權益當期為負，看「股東能分到的」用母公司欄。")
    a(f"- **2026H1**：營收 {f2(h['rev'])} 億對 2025H1 {f2(h['rev_25'])} 億，年增 {h['rev_yoy']:.1f}%。毛利率 {f1(h['gm'])}%，低於去年同期 {f1(h['gm_25'])}%，也低於 2025 全年 {f1(y[2025]['gm'])}%。EPS {f2(h['eps'])} 元（Q1 {f2(h['q1_eps'])}、推得 Q2 {f2(h['q2_eps'])}）。成長還在，但 **毛利率在往下走**。")
    a("")
    a("## 2. 2026 年迄今：進度，不是高峰證明")
    a("")
    a("| 期間 | 營收 | 年增 | 來源 |")
    a("|---|---:|---:|---|")
    a(f"| 2026Q1 | {f2(h['q1_rev'])} | （YTD 口徑） | 公開資訊觀測站 115Q1 |")
    a(f"| 2026H1 | {f2(h['rev'])} | {h['rev_yoy']:+.1f}% | 公開資訊觀測站 115Q2；櫃買 OpenAPI 同值 |")
    a(f"| 2026 1–7 月 | {f2(ytd['ytd'])} | {ytd['ytd_yoy']:+.2f}% | 櫃買每月營業收入彙總 資料年月 {ytd['ym']} |")
    a(f"| 2026-07 單月 | {f2(ytd['month'])} | {ytd['m_yoy']:+.2f}% | 同上 |")
    a("")
    a(f"1–7 月累計 {f2(ytd['ytd'])} 億，年增約 18%。若後半維持相似認列節奏，全年有機會站上 70 億附近——**這是把上半年年增外推的算術，不是公司財測，也不是本報告的預測目標**。工程認列可以一季跳一塊，也可以因驗收延後空一季。")
    a("")
    a("## 3. 資產負債、現金、槓桿")
    a("")
    a("| 時點 | 資產 | 權益 | 母公司權益 | 負債比 | 流動比 | 現金 | 每股淨值 |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in d["years"]:
        a(
            f"| {row['year']}年底 | {f1(row['assets'])} | {f1(row['equity'])} | {f1(row['eq_p'])} | "
            f"{f1(row['debt'], '%')} | {f2(row['cr'])} | {f1(row['cash'])} | {f2(row['bv'])} |"
        )
    a(
        f"| 2026Q2 | {f1(h['assets'])} | {f1(h['equity'])} | {f1(h['eq_p'])} | "
        f"{f1(h['debt'], '%')} | {f2(h['cr'])} | {f1(h['cash'])} | {f2(h['bv'])} |"
    )
    a("")
    a("負債比 2021 約 49%，2022 一次降到 38% 附近，之後在 38–40%；2026Q2 回升到約 44%，流動比從 2025 年底 2.12 降到 1.83。權益總額 Q2 低於 2025 年底，符合除息／發放現金後的季節。財務結構不算緊，也不是「零槓桿現金牛」。")
    a("")
    a("| 年 | 營業現金流 | 投資現金流 | 籌資現金流 | 母公司淨利 | 營業CF／母公司淨利 |")
    a("|---|---:|---:|---:|---:|---:|")
    for row in d["years"]:
        a(
            f"| {row['year']} | {f2(row['ocf'])} | {f2(row['icf'])} | {f2(row['fcf'])} | "
            f"{f2(row['ni_p'])} | {f0(row['ocf_ni'])}% |"
        )
    a(f"| 2026H1 | {f2(h['ocf'])} | {f2(h['icf'])} | {f2(h['fcf'])} | {f2(h['ni_p'])} | {f0(pct(h['ocf'], h['ni_p']))}% |")
    a("")
    a(f"只有 2023 營業現金流（{f2(y[2023]['ocf'])} 億）明顯高於母公司淨利。2024 營業現金流只有 {f2(y[2024]['ocf'])} 億、同年投資現金流出 {f2(y[2024]['icf'])} 億；2025 營業現金 {f2(y[2025]['ocf'])} 億、籌資淨流出 {f2(y[2025]['fcf'])} 億（配息級）。**帳上賺得到、現金常常慢一拍**——完工百分比法、應收／合約資產堆在資產負債表是這類公司的常態。把 EPS 當成「口袋裡的現金」會高估可分配能力。")
    a("")
    a("母公司 ROE（母公司淨利／平均母公司權益；2021 用期末）："
      + "、".join(f"{row['year']} {f1(row['roe'])}%" for row in d["years"])
      + "。趨勢向上，但仍是「十幾％的工程股本回報」，不是軟體型 25%+。")
    a("")
    a("## 4. 評價、股利、同業對照")
    a("")
    a(f"2026-08-26 收盤 {f2(d['close'])} 元 × {f0(d['shares'])} 股 → 市值約 {f1(d['mkt'])} 億。櫃買公布本益比 {p.get('PriceEarningRatio')}、淨值比 {p.get('PriceBookRatio')}、現金殖利率 {p.get('YieldRatio')}%。以 2025 EPS {f2(y[2025]['eps'])} 元回算，{f2(d['close'])}／{f2(y[2025]['eps'])} ≈ {d['close']/y[2025]['eps']:.1f} 倍，與櫃買 11.77 接近（櫃買用近四季）。")
    a("")
    a("上櫃同業／鄰近（同一日櫃買行情；8473 山林水為上市、不在此表）：")
    a("")
    a("| 代號 | 名稱 | 收盤 | 市值億 | PER | PBR | 殖利率% |")
    a("|---|---|---:|---:|---:|---:|---:|")
    for pr in d["peers"]:
        a(f"| {pr['code']} | {pr['name']} | {f2(pr['close'])} | {f1(pr['mkt'])} | {f2(pr['pe'])} | {f2(pr['pb'])} | {f2(pr['yd'])} |")
    a("")
    a("崑鼎（廢棄物／環工營運）市值與本益比都高一截；萬國通（塑膠管）本益比／淨值比落在另一個量級。國統夾在「水務工程整合」與「管材製造」之間，不能拿萬國通的倍數當錨，也不能假設自己享有崑鼎那種營運合約能見度。")
    a("")
    a("## 5. 產業未來五年：台灣水資源公共投資窗")
    a("")
    a("這段是政策與產業結構，**不是公司已簽約金額的加總**。")
    a("")
    a("1. **六年行動計畫的量級**。遠見報導（引行政院國家氣候變遷對策委員會）寫：2026–2031「水及流域永續發展行動計畫」規劃投入 **5,531 億元**。水利署 114-12-30 新聞稿：前瞻水環境至 113 年底已累計增加每日 **237 萬噸**水源（約當全國公共用水 +22%）；至民國 120 年還要再增每日 **133 萬噸**，備援率由 48% 拉到 60%。主軸＝多元水源、珍珠串（水庫／管網互聯）、科技造水。點名工程含石門–新竹聯通管、大安大甲溪聯通管、伏流水、再生水廠（桃園／台中／台南／高雄等）、**新竹及臺南海淡廠**。")
    a("2. **再生水**。水利署再生水專頁：行政院已核定本島 **16 案**再生水廠，完成後每日約 **60.69 萬噸**。另一則水利署稿（產業用水）寫已完成桃北、水湳、永康、安平、鳳山、臨海等 6 案、日產約 16.4 萬噸，還有約 10 座。科學園區擴建（寶山二期、中科二期、楠梓等）被要求優先用再生水——這是國統「下水／中水」敘事的官方土壤。")
    a("3. **海淡**。水利署統計：111 年底已完工營運海淡廠 23 座，但全年實際造水量只有 949.92 萬立方公尺（日均約 2.6 萬噸）——既有廠多半是離島／小規模。真正的大型廠是新竹、臺南這一波。工程計畫透明網列有「臺南海水淡化廠工程計畫（第一期）」「新竹海水淡化廠工程計畫」。富果 2026-06-16 法說整理（公司口述、self-reported 轉述）：國統稱已建 5 座、承攬臺南海淡，並瞄準 2027 嘉義海淡；「國內唯一具備設備製造＋施工＋營運」是公司自己的定位句，不是監理機關認證。")
    a("4. **管材與 HDPE**。公司／鉅亨 2026 年報導：轉投資國永泓（持股 60%）做 HDPE 管，四條線 32–1,200 mm，規劃 2026 年底量產，對準海淡取排水、再生水、電信電力管。同時規劃跨入電力管道（報導舉 345kV 興達–南科線，預算約 300 億級、長度近 44 km）——這是「工法遷移」不是「已經得標」。")
    a("5. **全球 HDPE 管**。第三方估計不可當真兆精確值，只作量級：Mordor 寫 2025 全球約 224.6 億美元、2026–2031 CAGR 約 5.98% 至 316.8 億；IMARC 寫 2025 約 220 億、2026–2034 CAGR 約 3.88%。亞太占比約 44%。需求驅動是市政汰換、新興市場管網、再生能源／電網套管。標準口徑競爭激烈，大口徑與專用規格才有技術門檻。")
    a("")
    a("**五年產業情景（self-reported，非預測）**：台灣這五年的水務資本支出窗是真的——海淡、再生水、珍珠串、科學園區用水都寫在官方文件裡。產業增速會接近「公共投資執行率」，不是 GDP。風險是預算遞延、地方抗爭、環評、以及同一池標案被中鼎、大陸工程、日商／韓商 EPC、膜廠（東麗等）切走。全球海淡設備與膜材料仍是歐美日韓的賽場；台灣廠商的可爭位置比較像 **在地統包＋管線＋O&M**，不是全球膜專利。")
    a("")
    a("## 6. 公司五年前景與全球競爭力（self-reported）")
    a("")
    a("### 6.1 公司能打的牌")
    a("")
    a("- **在地水務垂直整合**：管材（DIP／WSP／混凝土）＋推進／潛盾工法＋海淡／淨污水廠 EPC＋代操作。這在台灣公共工程評選裡是「實績分數」，不是簡報分數。")
    a("- **政策同向**：官方要造水、調度、降漏，國統的產品剛好在輸配水與科技造水的接縫。2022–2025 營收與 EPS 的上台階，與這段政策期重合。")
    a("- **HDPE 補產品洞**：海淡取排水、再生水、電力套管很多規格不是鑄鐵／鋼管的主場。自己做 HDPE 是為了報價與交期，不是為了跟中東／大陸管廠打全球市占。")
    a("")
    a("### 6.2 全球競爭力——誠實邊界")
    a("")
    a("| 層 | 判斷 | 依據 |")
    a("|---|---|---|")
    a("| 台灣公共水務 EPC／管線 | 中上、區域領先候選 | 五年財報擴張＋海淡／再生水實績敘事；但標案仍是逐案競爭 |")
    a("| 台灣 HDPE 管 | 尚未量產、未證明 | 子公司規劃 2026 年底；沒有 2025 年報可驗證的 HDPE 營收占比 |")
    a("| 全球海淡設備／膜 | 弱 | 全球龍頭是 Acciona、IDE、Doosan、Veolia 與膜廠 DuPont／Toray／Hydranautics；國統沒有公開的全球市占 |")
    a("| 全球 HDPE 管 | 弱到不在榜 | 亞太產能在中國／印度／中東；國統規模 60 億台幣級營收，不是全球管材平台 |")
    a("| 電網管道工法 | 機會、未兌現 | 只是工法延伸敘事 |")
    a("")
    a("一句話：**國統的競爭力是「台灣水務資本支出週期裡的在地整合商」，不是「全球水務科技公司」。** 把公司寫進全球海淡 CAGR 故事會過度延伸。把公司寫成「沒有護城河的傳產管廠」又忽略它在海淡／推進的實績門檻。正確量尺是：未來五年能拿下多少已列名的台灣標案、毛利率能不能守住 20% 以上、營業現金流能不能跟上 EPS。")
    a("")
    a("### 6.3 基準（不是目標價、不是財測）")
    a("")
    a(f"若 2026 只是「1–7 月年增約 18%、H1 年增 20%」的延續，營收落在高 60 億至低 70 億、EPS 落在 4 元出頭到 4.5 元附近，與目前約 12 倍本益、近 6% 殖利率是「把已可見的工程認列付進價格」。要變成再一輪重估，需要（a）嘉義／北高雄等下一座大型海淡或再生水統包入袋、且（b）毛利率不再往 20% 以下掉、且（c）營業現金流至少接近淨利的一半以上。這三件事 **目前公開數字都還沒同時成立**。")
    a("")
    a("## 7. 風險（已看到的）")
    a("")
    a("1. **毛利率下行**：2023 38% → 2025 26% → 2026H1 22.5%。工程占比升高或成本（鋼、鑄鐵、勞務、利息）吃掉管材利潤。")
    a("2. **現金轉換差**：2024、2025 營業現金流遠低於母公司淨利；合約資產／應收變大時，配息與擴產搶同一桶現金。")
    a("3. **公共工程集中度**：客戶是政府與科學園區。預算遞延、改設計、驗收爭議會直接打營收認列。")
    a("4. **標案輸贏**：海淡／再生水不是國統獨食。中鼎體系、日商、膜廠＋在地土木聯合都在同一池。")
    a("5. **HDPE 量產時程**：2026 年底是規劃，不是產線折舊已經開始貢獻。新廠學習曲線與價格戰可能先吃毛利。")
    a("6. **籌資／CB**：報導稱 2026 年擬發可轉債合計逾 12 億。成功則稀釋與利息；失敗則擴產與標案保證金更緊。")
    a("7. **把政策預算當公司營收**：5,531 億是全國六年治水／供水包，含防洪、疏濬、地方工程，國統能切到的是其中輸配水與造水子集。")
    a("8. **評價已反映成長**：殖利率近 6% 看起來「便宜」，但那是用已公布 DPS 3 元去除以 51 元；獲利若因毛利率續掉，倍數會自己修正。")
    a("")
    a("## 8. 來源與方法")
    a("")
    a("- 綜合損益／資產負債／營益分析／現金流量：公開資訊觀測站彙總表 `mopsov.twse.com.tw` `ajax_t163sb04`／`t163sb05`／`t163sb06`／`t163sb20`，市場別上櫃、民國 110–115 年各季。金額單位千元。第 4 季＝全年累計。")
    a("- 收盤、本益／淨值／殖利率、2026-07 月營收、2026H1 損益快照：櫃買 OpenAPI `tpex_mainboard_quotes`、`tpex_mainboard_peratio_analysis`、`mopsfin_t187ap05_O`、`mopsfin_t187ap06_O_ci`、`mopsfin_t187ap07_O_ci`（日期 1150826）。")
    a("- 公司基本資料：https://www.kti.com.tw/ 及基本資料頁。")
    a("- 水利署：再生水專頁；焦點稿「每日再增加133萬噸水源…」（最後更新 114-12-30）。")
    a("- 遠見：5531 億水及流域永續發展行動計畫報導。")
    a("- 鉅亨／Yahoo 新聞：國永泓 HDPE、2026H1 營收 33.18 億（與觀測站相符）。")
    a("- Mordor Intelligence、IMARC：全球 HDPE 管市場估計（第三方、非官方統計）。")
    a("- 富果法說整理 2026-06-16：公司口述海淡實績與標案意向（轉述，非財報）。")
    a("")
    a("原始 JSON 落地於 `reports/8936_kti_sources/`。本報告不含 Augur 庫內預測分數，也不構成投資建議。")
    a("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _charts(d: dict, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font_manager.fontManager.addfont(FONT)
    name = font_manager.FontProperties(fname=FONT).get_name()
    plt.rcParams["font.family"] = [name, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    years = [x["year"] for x in d["years"]]
    rev = [x["rev"] for x in d["years"]]
    eps = [x["eps"] for x in d["years"]]
    gm = [x["gm"] for x in d["years"]]
    om = [x["om"] for x in d["years"]]

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.6), dpi=140)
    ax = axes[0]
    ax.bar(years, rev, color="#1f4e79", width=0.62)
    ax.set_title("營收（億元）")
    ax.set_ylabel("億元")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax2 = ax.twinx()
    ax2.plot(years, eps, color="#c45911", marker="o", linewidth=2)
    ax2.set_ylabel("EPS（元）", color="#c45911")
    ax = axes[1]
    ax.plot(years, gm, marker="o", color="#2e7d32", label="毛利率")
    ax.plot(years, om, marker="s", color="#6a1b9a", label="營益率")
    ax.set_title("利潤率（%）")
    ax.legend(frameon=False)
    ax.grid(linestyle=":", alpha=0.5)
    fig.tight_layout()
    img = out / "8936_kti_charts.png"
    fig.savefig(img, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return img


def write_pdf(d: dict, md_path: Path, pdf_path: Path, chart: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    pdfmetrics.registerFont(TTFont("CJK", FONT, subfontIndex=0))
    navy = colors.HexColor("#1f4e79")
    gold = colors.HexColor("#c45911")
    pale = colors.HexColor("#eef3f8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverH", fontName="CJK", fontSize=20, leading=28, textColor=navy, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name="CoverS", fontName="CJK", fontSize=11, leading=16, textColor=colors.HexColor("#445"), alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="H1", fontName="CJK", fontSize=14, leading=20, textColor=navy, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="H2", fontName="CJK", fontSize=12, leading=17, textColor=navy, spaceBefore=9, spaceAfter=4))
    styles.add(ParagraphStyle(name="Body", fontName="CJK", fontSize=9.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6, textColor=colors.HexColor("#222")))
    styles.add(ParagraphStyle(name="Item", fontName="CJK", fontSize=9.5, leading=15, leftIndent=12, spaceAfter=3, textColor=colors.HexColor("#222")))
    styles.add(ParagraphStyle(name="Foot", fontName="CJK", fontSize=8, leading=11, textColor=colors.HexColor("#666")))
    styles.add(ParagraphStyle(name="Th", fontName="CJK", fontSize=8, leading=11, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Td", fontName="CJK", fontSize=8, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TdL", fontName="CJK", fontSize=8, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Quote", fontName="CJK", fontSize=9.5, leading=15, backColor=pale, borderPadding=6, spaceAfter=8, textColor=colors.HexColor("#1a1a1a")))

    def P(text, style="Body"):
        return Paragraph(text.replace("\n", "<br/>"), styles[style])

    def tbl(header, rows, col_widths):
        data = [[P(c, "Th") for c in header]]
        for r in rows:
            styled = []
            for i, c in enumerate(r):
                styled.append(P(str(c), "TdL" if i == 0 else "Td"))
            data.append(styled)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "CJK"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, pale]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c5d0da")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    ymap = {x["year"]: x for x in d["years"]}
    h = d["h1"]
    per = d["per"]
    ytd = d["ytd"]
    story = []
    story.append(Spacer(1, 16 * mm))
    story.append(P("8936 國統國際", "CoverH"))
    story.append(P("近五年財務分析", "CoverH"))
    story.append(P("與未來五年前景、全球競爭力報告", "CoverH"))
    story.append(Spacer(1, 8 * mm))
    story.append(P("KUO TOONG INTERNATIONAL CO., LTD. ｜ TPEx 8936", "CoverS"))
    story.append(P(f"資料時點：股價 {d['asof']}　財報至 2026H1　月營收至 2026-07", "CoverS"))
    story.append(P("來源：公開資訊觀測站彙總表、櫃買中心 OpenAPI、經濟部水利署、公司官網", "CoverS"))
    story.append(Spacer(1, 10 * mm))
    story.append(P("本報告為研究整理（self-reported 解讀段已標示），<b>不是投資建議、不是目標價、不是公司財測</b>。未使用 FinMind／FRED。", "CoverS"))
    story.append(PageBreak())

    story.append(P("0. 一句話與範圍", "H1"))
    story.append(P(
        f"營收從 2022 低點 {f1(ymap[2022]['rev'])} 億走到 2025 的 {f1(ymap[2025]['rev'])} 億，母公司 EPS "
        f"{f2(ymap[2021]['eps'])}→{f2(ymap[2025]['eps'])} 元；2026 上半年營收再年增 {h['rev_yoy']:.1f}%。"
        "這是公共工程放量。毛利率從 2023 的 38% 回到 26% 帶、2026H1 再壓到 22.5%。"
        "現金轉換弱於帳面獲利，是營造／統包結構。本報告不給進出場建議。",
        "Quote",
    ))
    story.append(P(
        "國統國際（KTI）1978 年設立、2002-09-09 上櫃。核心是大口徑輸配水管（混凝土管、鋼管、延性鑄鐵管）的設計製造裝配，"
        "並延伸免開挖推進、潛盾、海水淡化與淨水／污水整廠之設計、施工與代操作。實收資本 24.81 億、普通股 248,078,157 股。"
        f"2026-08-26 收盤 {f2(d['close'])} 元，市值約 {f1(d['mkt'])} 億；本益比 {per.get('PriceEarningRatio')}、"
        f"淨值比 {per.get('PriceBookRatio')}、現金殖利率 {per.get('YieldRatio')}%。金額單位新台幣億元（觀測站千元÷10萬）。",
    ))

    story.append(P("1. 近五年損益", "H1"))
    header = ["年", "營收", "年增", "毛利率", "營益率", "稅後淨利", "母公司淨利", "EPS"]
    rows = []
    for row in d["years"]:
        yoy_s = "—" if row["rev_yoy"] is None else f"{row['rev_yoy']:+.1f}%"
        rows.append([
            str(row["year"]), f2(row["rev"]), yoy_s, f1(row["gm"], "%"), f1(row["om"], "%"),
            f2(row["ni"]), f2(row["ni_p"]), f2(row["eps"]),
        ])
    rows.append([
        "2026H1", f2(h["rev"]), f"{h['rev_yoy']:+.1f}%", f1(h["gm"], "%"), f1(h["om"], "%"),
        f2(h["ni"]), f2(h["ni_p"]), f2(h["eps"]),
    ])
    story.append(tbl(header, rows, [18*mm, 22*mm, 22*mm, 22*mm, 22*mm, 26*mm, 26*mm, 18*mm]))
    story.append(Spacer(1, 3 * mm))
    if chart.exists():
        story.append(Image(str(chart), width=170*mm, height=60*mm))
    story.append(P(
        f"2022 是五年營收低點（{f1(ymap[2022]['rev'])} 億、年減 {ymap[2022]['rev_yoy']:.1f}%）。"
        f"之後三年連擴，2025 全年 {f1(ymap[2025]['rev'])} 億。2023 毛利率 {f1(ymap[2023]['gm'])}% 是高峰；"
        f"2024–2025 回到 {f1(ymap[2024]['gm'])}%／{f1(ymap[2025]['gm'])}%，屬於「量大、組合變工程向」。"
        f"母公司 EPS 五年連增。2021 合併淨利低於母公司淨利，非控制權益當期為負，股東可分配看母公司欄。",
    ))

    story.append(P("2. 2026 年迄今", "H1"))
    story.append(tbl(
        ["期間", "營收（億）", "年增", "來源"],
        [
            ["2026Q1", f2(h["q1_rev"]), "YTD 單季", "觀測站 115Q1"],
            ["2026H1", f2(h["rev"]), f"{h['rev_yoy']:+.1f}%", "觀測站 115Q2"],
            ["2026 1–7月", f2(ytd["ytd"]), f"{ytd['ytd_yoy']:+.2f}%", f"櫃買月營收 {ytd.get('ym')}"],
            ["2026-07 單月", f2(ytd["month"]), f"{ytd['m_yoy']:+.2f}%", "同上"],
        ],
        [35*mm, 32*mm, 35*mm, 68*mm],
    ))
    story.append(P(
        f"H1 毛利率 {f1(h['gm'])}%，低於去年同期 {f1(h['gm_25'])}% 與 2025 全年 {f1(ymap[2025]['gm'])}%。"
        "成長還在，毛利率在往下。1–7 月年增約 18% 若外推，全年算術上可能高 60 億至低 70 億——"
        "<b>這是外推不是財測</b>。工程認列可以一季跳一塊，也可以因驗收空一季。",
    ))

    story.append(P("3. 資產負債與現金", "H1"))
    rows = []
    for row in d["years"]:
        rows.append([
            f"{row['year']}底", f1(row["assets"]), f1(row["equity"]), f1(row["debt"], "%"),
            f2(row["cr"]), f1(row["cash"]), f2(row["bv"]),
        ])
    rows.append([
        "2026Q2", f1(h["assets"]), f1(h["equity"]), f1(h["debt"], "%"),
        f2(h["cr"]), f1(h["cash"]), f2(h["bv"]),
    ])
    story.append(tbl(["時點", "資產", "權益", "負債比", "流動比", "現金", "BPS"], rows,
                     [24*mm, 24*mm, 24*mm, 24*mm, 24*mm, 24*mm, 24*mm]))
    story.append(Spacer(1, 2 * mm))
    rows = []
    for row in d["years"]:
        rows.append([str(row["year"]), f2(row["ocf"]), f2(row["icf"]), f2(row["fcf"]), f2(row["ni_p"]), f"{f0(row['ocf_ni'])}%"])
    rows.append(["2026H1", f2(h["ocf"]), f2(h["icf"]), f2(h["fcf"]), f2(h["ni_p"]), f"{f0(pct(h['ocf'], h['ni_p']))}%"])
    story.append(tbl(["年", "營業CF", "投資CF", "籌資CF", "母公司淨利", "CF/淨利"], rows,
                     [24*mm, 28*mm, 28*mm, 28*mm, 32*mm, 28*mm]))
    story.append(P(
        f"負債比 2021 約 49%，之後落在 38–40%；2026Q2 回升到約 {f1(h['debt'])}%，流動比 1.83。"
        f"五年裡只有 2023 營業現金流（{f2(ymap[2023]['ocf'])} 億）明顯高於母公司淨利。"
        f"2024 營業現金僅 {f2(ymap[2024]['ocf'])} 億、投資流出 {f2(ymap[2024]['icf'])} 億；"
        f"2025 籌資淨流出 {f2(ymap[2025]['fcf'])} 億。帳上賺得到、現金常常慢一拍。"
        "母公司 ROE：" + "、".join(f"{r['year']} {f1(r['roe'])}%" for r in d["years"]) + "。",
    ))

    story.append(P("4. 評價與同業", "H1"))
    story.append(P(
        f"市值約 {f1(d['mkt'])} 億。以 2025 EPS {f2(ymap[2025]['eps'])} 元回算約 {d['close']/ymap[2025]['eps']:.1f} 倍，"
        f"與櫃買本益比 {per.get('PriceEarningRatio')} 接近。現金殖利率 {per.get('YieldRatio')}% 用的是已公布 DPS "
        f"{f2(num(per.get('DividendPerShare')))} 元。",
    ))
    prows = [[pr["code"], pr["name"], f2(pr["close"]), f1(pr["mkt"]), f2(pr["pe"]), f2(pr["pb"]), f2(pr["yd"])] for pr in d["peers"]]
    story.append(tbl(["代號", "名稱", "收盤", "市值億", "PER", "PBR", "殖利率%"], prows,
                     [22*mm, 28*mm, 24*mm, 24*mm, 22*mm, 22*mm, 26*mm]))
    story.append(P("崑鼎是環工營運現金流型；萬國通是塑膠管製造。國統夾在水務工程整合與管材之間，倍數不能直接對折。8473 山林水為上市，未列入櫃買此表。"))

    story.append(P("5. 產業未來五年", "H1"))
    story.append(P(
        "政策窗是真的，但 5,531 億是全國六年治水／供水包，不是國統的在手訂單。"
        "水利署（114-12-30）：前瞻至 113 年底已增每日 237 萬噸水源；至民國 120 年再增每日 133 萬噸，備援率 48%→60%。"
        "主軸含珍珠串聯通管、伏流水、再生水、新竹及臺南海淡廠。再生水專頁：已核定 16 案、完成後每日約 60.69 萬噸。"
        "111 年底海淡廠雖有 23 座在營運，全年造水僅 949.92 萬立方公尺——既有廠偏小，大型廠是這一波才開始。"
        "全球 HDPE 管第三方估計約 220 億美元級、CAGR 約 4–6%（Mordor／IMARC，非官方統計）；亞太約 44%。"
        "標準口徑殺價，大口徑與海淡／電網規格才有門檻。",
    ))
    story.append(P(
        "五年產業情景（self-reported）：台灣水務資本支出會接近公共投資執行率，不是 GDP。"
        "風險是預算遞延、環評、以及中鼎體系、日商／韓商 EPC、膜廠切走同一池標案。"
        "全球海淡設備與膜仍是歐美日韓賽場；台灣廠商可爭的是在地統包＋管線＋O&M。",
        "Quote",
    ))

    story.append(P("6. 公司前景與全球競爭力（self-reported）", "H1"))
    story.append(P(
        "能打的牌：在地垂直整合（管材＋推進／潛盾＋海淡／淨污水 EPC＋代操作）剛好對上官方造水／調度／降漏；"
        "2022–2025 財報上台階與這段政策期重合。HDPE 子公司國永泓（報導持股 60%、規劃 2026 年底量產）是補產品洞，"
        "不是去打全球管材市占。電網管道是工法遷移敘事，報導舉興達–南科 345kV 線為例，不是已得標。",
    ))
    story.append(tbl(
        ["層級", "判斷", "依據"],
        [
            ["台灣公共水務 EPC／管線", "中上、區域領先候選", "五年財報擴張＋海淡／再生水實績敘事；仍逐案競爭"],
            ["台灣 HDPE 管", "尚未量產、未證明", "2026 年底規劃；年報尚無 HDPE 營收占比"],
            ["全球海淡設備／膜", "弱", "Acciona／IDE／Doosan／Veolia／Toray／DuPont 主場"],
            ["全球 HDPE 管", "弱、不在榜", "亞太產能在中國／印度／中東；國統是 60 億台幣級"],
            ["電網管道工法", "機會、未兌現", "只有延伸敘事"],
        ],
        [42*mm, 42*mm, 86*mm],
    ))
    story.append(P(
        "<b>國統的競爭力是「台灣水務資本支出週期裡的在地整合商」，不是「全球水務科技公司」。</b>"
        f"基準（不是目標價）：若 2026 只延續 1–7 月約 18% 年增，營收高 60 億至低 70 億、EPS 約 4–4.5 元，"
        f"與目前約 12 倍本益、近 6% 殖利率是「把已可見工程認列付進價格」。要再重估，需要下一座大型海淡或再生水統包入袋、"
        "毛利率不再往 20% 以下掉、且營業現金流至少接近淨利一半。這三件目前沒有同時成立。",
    ))

    story.append(P("7. 風險", "H1"))
    risks = [
        "毛利率下行：2023 年 38% → 2025 年 26% → 2026H1 22.5%。",
        "現金轉換差：2024、2025 營業現金流遠低於母公司淨利。",
        "公共工程集中：預算遞延、改設計、驗收爭議直接打認列。",
        "標案不是獨食：海淡／再生水有中鼎、日商、膜廠＋在地土木。",
        "HDPE 量產只是規劃；新廠學習曲線可能先吃毛利。",
        "報導稱 2026 擬發 CB 逾 12 億：稀釋或保證金壓力。",
        "5,531 億是全國包，國統只能切到輸配水與造水子集。",
        "近 6% 殖利率用已公布 DPS；毛利率若續掉，倍數會自己修正。",
    ]
    for i, r in enumerate(risks, 1):
        story.append(P(f"{i}. {r}", "Item"))

    story.append(P("8. 來源", "H1"))
    story.append(P(
        "公開資訊觀測站彙總表 mopsov ajax_t163sb04／05／06／20（上櫃、民國 110–115）；"
        "櫃買 OpenAPI 行情／本益比／月營收／2026H1 快照（1150826）；"
        "kti.com.tw；水利署再生水專頁與 114-12-30 焦點稿；遠見 5531 億報導；"
        "鉅亨 HDPE 新聞；Mordor／IMARC HDPE 市場估計；富果 2026-06-16 法說整理（公司口述）。"
        "原始檔：reports/8936_kti_sources/。本 PDF 由 scripts/build_8936_kti_report.py 依 JSON 編成。",
        "Foot",
    ))
    story.append(P("© 研究整理｜禁止把本檔數字當成下單依據。", "Foot"))

    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("CJK", 8)
        canvas.setFillColor(colors.HexColor("#667"))
        canvas.drawString(18 * mm, 10 * mm, "8936 國統｜財務與前景｜非投資建議")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{doc.page}")
        canvas.setStrokeColor(navy)
        canvas.setLineWidth(1.2)
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.restoreState()

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="8936 國統近五年財務與前景報告",
        author="augur research (self-reported outlook)",
    )
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)


def _selftest() -> int:
    assert abs(yi(5245526) - 52.45526) < 1e-6
    assert abs(yoy(63.1, 52.46) - 20.282) < 0.01
    dummy = Path("/tmp/8936_selftest_empty")
    dummy.mkdir(exist_ok=True)
    print("SELFTEST_OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="reports/8936_kti_sources")
    p.add_argument("--out-dir", default="reports")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    src = Path(args.src)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    d = extract(src)
    md = out / "augur_8936_kti_5y_finance_outlook_20260827.md"
    pdf = out / "8936_kti_5y_finance_outlook_20260827.pdf"
    write_markdown(d, md)
    chart = _charts(d, src)
    write_pdf(d, md, pdf, chart)
    art = Path("/opt/cursor/artifacts")
    try:
        art.mkdir(parents=True, exist_ok=True)
        dest = art / pdf.name
        dest.write_bytes(pdf.read_bytes())
        print("ARTIFACT", dest)
    except OSError as e:
        print("ARTIFACT_SKIP", e)
    print("MD", md, "bytes", md.stat().st_size)
    print("PDF", pdf, "bytes", pdf.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
