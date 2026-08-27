#!/usr/bin/env python3
"""產生 6596 寬宏藝術近五年財務與五年前景 PDF。守原則 #9 #10 #15。

執行指令矩陣：
  python3 scripts/build_6596_kham_report.py
  python3 scripts/build_6596_kham_report.py --selftest
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports"
HTML_NAME = "augur_6596_kham_5y_finance_outlook_20260827.html"
PDF_NAME = "augur_6596_kham_5y_finance_outlook_20260827.pdf"
MD_NAME = "augur_6596_kham_5y_finance_outlook_20260827.md"

VIEWPOINT = "2026-08-27"
PRICE_CLOSE = Decimal("96.8")
SHARES_NOW = Decimal("38000000")  # 實收資本 3.80 億


def D(x) -> Decimal:
    return Decimal(str(x))


def rnd(x, n=1) -> float:
    q = D(10) ** -n
    return float(D(x).quantize(q, rounding=ROUND_HALF_UP))


def pct(n, d, nplaces=1) -> float:
    return rnd(D(n) / D(d) * 100, nplaces)


def yi(n) -> str:
    """千元 → 億，保留兩位。"""
    return f"{rnd(D(n) / 100000, 2):.2f}"


def compute() -> dict:
    # 季損益（千元）：營收、毛利、營業利益、稅前、稅後。來源 HiStock；年合計與 MOPS 對過。
    q = {
        "2021Q1": (107113, -8679, -46159, -41289, -33305),
        "2021Q2": (132905, 27401, -3752, -6710, -5122),
        "2021Q3": (4404, 712, -11544, -10236, -7763),
        "2021Q4": (57680, 1310, -47736, -47938, -39476),
        "2022Q1": (410464, 76912, -4304, 14537, 11550),
        "2022Q2": (213392, 22824, -26061, -28692, -22774),
        "2022Q3": (364891, 56794, 5283, 21771, 17778),
        "2022Q4": (294337, 68358, -4506, -5860, -4968),
        "2023Q1": (192162, 47337, 7999, 29164, 27433),
        "2023Q2": (172253, 45356, 2853, 9529, 7051),
        "2023Q3": (568097, 144299, 73372, 81031, 64438),
        "2023Q4": (411604, 155167, 101699, 100860, 80648),
        "2024Q1": (632749, 151033, 88844, 91592, 73263),
        "2024Q2": (342515, 83002, 41284, 34376, 24051),
        "2024Q3": (398709, 130273, 82595, 87222, 71085),
        "2024Q4": (355695, 107969, 66006, 51745, 40130),
        "2025Q1": (463283, 234062, 172499, 181418, 144908),
        "2025Q2": (387898, 153449, 101013, 113474, 91176),
        "2025Q3": (1862624, 655707, 529863, 531989, 425682),
        "2025Q4": (376774, 120364, 73880, 71178, 53761),
        "2026Q1": (604059, 134111, 86859, 98420, 79113),
        "2026Q2": (718359, 309107, 244756, 251057, 200934),
    }

    def ysum(year: int) -> tuple[int, ...]:
        s = [0] * 5
        for i in range(1, 5):
            for j, v in enumerate(q[f"{year}Q{i}"]):
                s[j] += v
        return tuple(s)

    mops_2025 = (3090579, 1163582, 877255, 898059, 715527)
    mops_h1 = (1322418, 443218, 331615, 349477, 280047)
    assert ysum(2025) == mops_2025
    h1 = tuple(a + b for a, b in zip(q["2026Q1"], q["2026Q2"]))
    assert h1 == mops_h1

    eps = {2021: D("-2.86"), 2022: D("0.05"), 2023: D("5.94"), 2024: D("6.27"), 2025: D("18.83")}
    years = {}
    prev_rev = None
    for y in range(2021, 2026):
        rev, gp, op, pbt, ni = ysum(y)
        row = {
            "rev": rev, "gp": gp, "op": op, "pbt": pbt, "ni": ni,
            "gpm": pct(gp, rev), "opm": pct(op, rev), "npm": pct(ni, rev),
            "eps": float(eps[y]),
            "yoy": None if prev_rev is None else pct(rev - prev_rev, prev_rev),
        }
        years[y] = row
        prev_rev = rev

    h1_25 = tuple(a + b for a, b in zip(q["2025Q1"], q["2025Q2"]))
    ocf = {
        2021: sum([-39027, 7117, -57078, -19015]),
        2022: sum([55332, -122804, 60066, -14304]),
        2023: sum([58735, 4145, 124761, 321478]),
        2024: sum([-39109, -66644, 219726, 56582]),
        2025: sum([1007375, 123783, -25159, 278343]),
    }
    assert ocf[2024] == 170555
    assert ocf[2025] == 1384342

    bs = {
        2021: {"a": 934221, "l": 396366, "e": 537855, "ca": 514945, "cl": 356871, "cash": 194054},
        2022: {"a": 819425, "l": 280009, "e": 539416, "ca": 392847, "cl": 256970, "cash": 172751},
        2023: {"a": 1549174, "l": 715759, "e": 833415, "ca": 1147752, "cl": 709872, "cash": 710125},
        2024: {"a": 2007374, "l": 791312, "e": 1216062, "ca": 1567198, "cl": 791220, "cash": 625761},
        2025: {"a": 3039218, "l": 1376559, "e": 1662659, "ca": 2267004, "cl": 1368996, "cash": 180356},
    }
    for y, b in bs.items():
        b["debt"] = pct(b["l"], b["a"])
        b["cur"] = int(round(pct(b["ca"], b["cl"], 0)))

    # 聚財網年報 ROE（平均權益口徑）；2022–2025 可用本表複核
    roe_pub = {2021: -13.18, 2022: 0.29, 2023: 26.16, 2024: 20.35, 2025: 49.71}
    roe_chk = {}
    eq = {2021: 537855, 2022: 539416, 2023: 833415, 2024: 1216062, 2025: 1662659}
    for y in range(2022, 2026):
        avg = (eq[y - 1] + eq[y]) / 2
        roe_chk[y] = pct(years[y]["ni"], avg)
    assert abs(roe_chk[2025] - 49.7) < 0.05

    ttm_eps = rnd(D("11.2") + D("1.42") + D("2.08") + D("5.29"), 2)  # 2025Q3–2026Q2 HiStock
    mkt = rnd(PRICE_CLOSE * SHARES_NOW / D(100000000), 2)
    bps_q2 = rnd(D(1232021) / D(38000), 2)
    pe = rnd(PRICE_CLOSE / D(str(ttm_eps)), 2)
    pbr = rnd(PRICE_CLOSE / D(str(bps_q2)), 2)

    return {
        "q": q,
        "years": years,
        "h1_26": {"rev": h1[0], "gp": h1[1], "op": h1[2], "pbt": h1[3], "ni": h1[4],
                  "gpm": pct(h1[1], h1[0]), "opm": pct(h1[2], h1[0]), "npm": pct(h1[4], h1[0]),
                  "eps": 7.37, "rev_yoy": pct(h1[0] - h1_25[0], h1_25[0]),
                  "ni_yoy": pct(h1[4] - h1_25[4], h1_25[4])},
        "h1_25": {"rev": h1_25[0], "ni": h1_25[4]},
        "q2_26": {"rev": q["2026Q2"][0], "gp": q["2026Q2"][1], "op": q["2026Q2"][2],
                  "ni": q["2026Q2"][4], "eps": 5.29,
                  "gpm": pct(q["2026Q2"][1], q["2026Q2"][0]),
                  "opm": pct(q["2026Q2"][2], q["2026Q2"][0]),
                  "npm": pct(q["2026Q2"][4], q["2026Q2"][0]),
                  "ni_yoy": pct(q["2026Q2"][4] - q["2025Q2"][4], q["2025Q2"][4])},
        "ocf": ocf,
        "bs": bs,
        "roe_pub": roe_pub,
        "bs_q2_26": {"a": 1954550, "l": 722529, "e": 1232021,
                     "debt": pct(722529, 1954550), "bps": bps_q2},
        "bs_q1_26": {"a": 2706562, "l": 1675021, "e": 1031541, "cash": 94031},
        "price": float(PRICE_CLOSE),
        "mkt": mkt,
        "ttm_eps": ttm_eps,
        "pe": pe,
        "pbr": pbr,
        "yield_px": pct(D("18.7"), PRICE_CLOSE),
        "cagr_21_25": rnd(((D(3090579) / D(302102)) ** (D(1) / D(4)) - 1) * 100, 1),
        "cagr_22_25": rnd(((D(3090579) / D(1283084)) ** (D(1) / D(3)) - 1) * 100, 1),
        "liquid_25": 180356 + 1615430,
        "jul26": {"rev": 94502, "yoy": -87.14, "ytd": 1416971, "ytd_yoy": -10.65},
    }


def bar_chart(labels, values, color="#1f4e79", unit="億", width=720, height=220) -> str:
    max_v = max(abs(v) for v in values) or 1
    pad_l, pad_r, pad_t, pad_b = 48, 16, 24, 36
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    n = len(values)
    gap = 18
    bw = (iw - gap * (n - 1)) / n
    zero_y = pad_t + ih * (max_v / (2 * max_v)) if min(values) < 0 else pad_t + ih
    # unipolar
    if min(values) >= 0:
        bars = []
        for i, (lab, v) in enumerate(zip(labels, values)):
            h = 0 if max_v == 0 else ih * (v / max_v)
            x = pad_l + i * (bw + gap)
            y = pad_t + ih - h
            bars.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" fill="{color}"/>'
                f'<text x="{x + bw/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="11" fill="#1a1a1a">{v:.2f}</text>'
                f'<text x="{x + bw/2:.1f}" y="{height - 10}" text-anchor="middle" font-size="12" fill="#333">{lab}</text>'
            )
        return f'<svg viewBox="0 0 {width} {height}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>'
    # bipolar
    span = max_v * 2
    zero_y = pad_t + ih * (max_v / span)
    bars = []
    for i, (lab, v) in enumerate(zip(labels, values)):
        h = ih * (abs(v) / span)
        x = pad_l + i * (bw + gap)
        y = zero_y - h if v >= 0 else zero_y
        c = color if v >= 0 else "#b42318"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" fill="{c}"/>'
            f'<text x="{x + bw/2:.1f}" y="{(y - 6) if v >= 0 else (y + h + 14):.1f}" text-anchor="middle" font-size="11" fill="#1a1a1a">{v:.2f}</text>'
            f'<text x="{x + bw/2:.1f}" y="{height - 10}" text-anchor="middle" font-size="12" fill="#333">{lab}</text>'
        )
    bars.append(f'<line x1="{pad_l}" y1="{zero_y:.1f}" x2="{width-pad_r}" y2="{zero_y:.1f}" stroke="#999" stroke-width="1"/>')
    return f'<svg viewBox="0 0 {width} {height}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>'


def line_chart(labels, series, colors, width=720, height=260) -> str:
    pad_l, pad_r, pad_t, pad_b = 44, 16, 36, 36
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    all_v = [v for s in series for v in s["values"]]
    lo, hi = min(all_v), max(all_v)
    if lo == hi:
        hi = lo + 1
    n = len(labels)
    def xy(i, v):
        x = pad_l + (0 if n == 1 else iw * i / (n - 1))
        y = pad_t + ih * (1 - (v - lo) / (hi - lo))
        return x, y
    parts = []
    lx = pad_l
    for s, col in zip(series, colors):
        parts.append(f'<rect x="{lx}" y="8" width="12" height="12" fill="{col}"/>')
        parts.append(f'<text x="{lx+16}" y="18" font-size="12" fill="#333">{s["name"]}</text>')
        lx += 90
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+ih}" x2="{width-pad_r}" y2="{pad_t+ih}" stroke="#ddd"/>')
    for s, col in zip(series, colors):
        pts = " ".join(f"{xy(i,v)[0]:.1f},{xy(i,v)[1]:.1f}" for i, v in enumerate(s["values"]))
        parts.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.5" points="{pts}"/>')
        for i, v in enumerate(s["values"]):
            x, y = xy(i, v)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>')
            parts.append(f'<text x="{x:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="10" fill="#333">{v:.1f}</text>')
    for i, lab in enumerate(labels):
        x, _ = xy(i, lo)
        parts.append(f'<text x="{x:.1f}" y="{height-10}" text-anchor="middle" font-size="12" fill="#333">{lab}</text>')
    return f'<svg viewBox="0 0 {width} {height}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def html_report(d: dict) -> str:
    y = d["years"]
    labels = ["2021", "2022", "2023", "2024", "2025"]
    rev_e = [rnd(y[int(l)]["rev"] / 100000, 2) for l in labels]
    ni_e = [rnd(y[int(l)]["ni"] / 100000, 2) for l in labels]
    gpm = [y[int(l)]["gpm"] for l in labels]
    opm = [y[int(l)]["opm"] for l in labels]
    npm = [y[int(l)]["npm"] for l in labels]
    chart_rev = bar_chart(labels, rev_e, "#1f4e79")
    chart_ni = bar_chart(labels, ni_e, "#2e7d4f")
    chart_m = line_chart(labels, [
        {"name": "毛利率", "values": gpm},
        {"name": "營益率", "values": opm},
        {"name": "淨利率", "values": npm},
    ], ["#1f4e79", "#c47b17", "#2e7d4f"])

    def yr_row(year):
        r = y[year]
        yoy = "—" if r["yoy"] is None else f"{r['yoy']:+.1f}%"
        return (
            f"<tr><td>{year}</td><td class='n'>{yi(r['rev'])}</td><td class='n'>{yoy}</td>"
            f"<td class='n'>{r['gpm']:.1f}%</td><td class='n'>{r['opm']:.1f}%</td>"
            f"<td class='n'>{yi(r['ni'])}</td><td class='n'>{r['npm']:.1f}%</td>"
            f"<td class='n'>{r['eps']:.2f}</td></tr>"
        )

    bs_rows = []
    for year in range(2021, 2026):
        b = d["bs"][year]
        bs_rows.append(
            f"<tr><td>{year}年底</td><td class='n'>{yi(b['a'])}</td><td class='n'>{yi(b['e'])}</td>"
            f"<td class='n'>{b['debt']:.1f}%</td><td class='n'>{b['cur']}%</td>"
            f"<td class='n'>{yi(b['cash'])}</td></tr>"
        )
    q2 = d["bs_q2_26"]
    bs_rows.append(
        f"<tr><td>2026Q2</td><td class='n'>{yi(q2['a'])}</td><td class='n'>{yi(q2['e'])}</td>"
        f"<td class='n'>{q2['debt']:.1f}%</td><td class='n'>—</td><td class='n'>—</td></tr>"
    )

    ocf_rows = []
    for year in range(2021, 2026):
        ni = y[year]["ni"]
        o = d["ocf"][year]
        ocf_rows.append(
            f"<tr><td>{year}</td><td class='n'>{yi(o)}</td><td class='n'>{yi(ni)}</td>"
            f"<td class='n'>{'是' if o > ni else '否'}</td></tr>"
        )

    h1 = d["h1_26"]
    q2p = d["q2_26"]
    jul = d["jul26"]

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8"/>
<title>6596 寬宏藝術｜近五年財務與未來五年前景</title>
<style>
@page {{ size: A4; margin: 16mm 14mm 18mm 14mm; }}
* {{ box-sizing: border-box; }}
html, body {{
  font-family: "WenQuanYi Micro Hei", "Noto Sans CJK TC", "Noto Sans TC", "Source Han Sans TC", sans-serif;
  color: #1a1a1a; font-size: 11.5pt; line-height: 1.55; margin: 0;
}}
.cover {{
  page-break-after: always; min-height: 240mm; padding: 28mm 8mm 0;
  background: linear-gradient(180deg, #0e2439 0%, #16324d 55%, #1b3d5c 100%);
  color: #f4f1ea;
}}
.cover h1 {{ font-size: 28pt; line-height: 1.25; margin: 0 0 8mm; letter-spacing: 0.04em; }}
.cover .sub {{ font-size: 13pt; opacity: 0.92; margin-bottom: 18mm; }}
.meta {{ font-size: 10.5pt; line-height: 1.7; }}
.badge {{ display: inline-block; border: 1px solid #d4b36a; color: #d4b36a; padding: 2px 10px; border-radius: 99px; font-size: 9.5pt; margin-bottom: 12mm; }}
.warn {{ background: #fff6e8; border-left: 4px solid #c47b17; padding: 8px 12px; margin: 10px 0 16px; font-size: 10.5pt; }}
h2 {{ color: #0e2439; font-size: 16pt; border-bottom: 2px solid #d4b36a; padding-bottom: 4px; margin: 18px 0 10px; page-break-after: avoid; }}
h3 {{ color: #1f4e79; font-size: 12.5pt; margin: 14px 0 6px; page-break-after: avoid; }}
p {{ margin: 0 0 8px; }}
ul {{ margin: 4px 0 10px 18px; padding: 0; }}
li {{ margin-bottom: 4px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin: 8px 0 14px; page-break-inside: avoid; }}
th {{ background: #0e2439; color: #fff; font-weight: 600; padding: 6px 7px; text-align: right; }}
th:first-child {{ text-align: left; }}
td {{ border-bottom: 1px solid #e4e0d8; padding: 5px 7px; }}
td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr:nth-child(even) td {{ background: #f7f5f0; }}
.chart {{ margin: 6px 0 14px; page-break-inside: avoid; }}
.caption {{ font-size: 9.5pt; color: #555; margin: -8px 0 12px; }}
.kpi {{ display: flex; gap: 8px; margin: 8px 0 14px; }}
.kpi div {{ flex: 1; background: #f4f1ea; border-top: 3px solid #d4b36a; padding: 8px 10px; }}
.kpi b {{ display: block; font-size: 14pt; color: #0e2439; }}
.kpi span {{ font-size: 9pt; color: #555; }}
.footer {{ font-size: 9pt; color: #666; margin-top: 18px; }}
.src {{ font-size: 9.5pt; color: #444; }}
.small {{ font-size: 10pt; color: #444; }}
</style>
</head>
<body>

<section class="cover">
  <div class="badge">[I] 研究報告 · self-reported · 非投資建議</div>
  <h1>6596 寬宏藝術<br/>近五年財務分析<br/>與未來五年前景／全球競爭力</h1>
  <div class="sub">上櫃文化創意｜演唱會、音樂劇、展覽主辦＋自有售票＋硬體</div>
  <div class="meta">
    觀點日：{VIEWPOINT}（價：2026-08-27 收盤 96.8 元）<br/>
    財報截至：2026 年第 2 季合併（董事會 2026-08-11）<br/>
    月營收截至：2026 年 7 月<br/>
    發行股數：3,800 萬股　市值約 {d['mkt']:.2f} 億元<br/>
    編製：Augur 雲端研究作業（本環境無生產庫、未打 FinMind／FRED API）
  </div>
</section>

<div class="warn">
  <b>讀法先講清楚。</b>本報告不是進出場建議，也不是目標價。2025 年 EPS 18.83 元是「江蕙＋悲慘世界」級的專案高峰，不是已證明的新常態地板。Rank／均線／本益比都不等於報酬％。分析意見標 self-reported。
</div>

<h2>0. 一句與資料範圍</h2>
<p><b>一句：</b>疫後從虧損走回獲利，2022–2024 營收 12.8→17.3 億、EPS 回到 6 元上下；2025 年跳到營收 30.91 億、稅後 7.16 億、EPS 18.83，配息 18.7 元。2026 上半年仍年增（營收 +55%、獲利 +19%），但 7 月營收年減 87%，顯示這是檔期生意，不是平滑成長股。</p>
<p>寬宏藝術經紀股份有限公司（Kuang Hong Arts Management；TPEx 6596）。2004 年設立、2018-01-04 上櫃，自稱台灣首家進入資本市場的展演主辦商。業務三塊：（1）國內外演唱會／音樂劇／展覽主辦與製作；（2）寬宏售票；（3）硬體與工程（子公司台灣藝人，法說約 10–15% 營收）。法說口徑：演出主辦勞務近九成，且認列 <b>100% 售票收入</b>（非抽佣），營業額因此顯著高於只收佣金的同業——比規模時要先換口徑。</p>
<p class="small">本雲端環境無 Augur PostgreSQL。數字來自公開資訊觀測站重大訊息（年／半年合併）、Yahoo 股市月營收（標精誠／櫃買）、HiStock 季報長表（季加總與 MOPS 2025 全年、2026H1 完全吻合）、聚財網年報比率。未使用 FinMind 即時 API。</p>

<div class="kpi">
  <div><b>30.91 億</b><span>2025 合併營收　年增 78.7%</span></div>
  <div><b>18.83 元</b><span>2025 EPS　配息 18.7 元</span></div>
  <div><b>7.37 元</b><span>2026H1 EPS　獲利年增 18.6%</span></div>
  <div><b>4.8×</b><span>2026-08-27 收盤／近四季 EPS 19.99</span></div>
</div>

<h2>1. 近五年損益</h2>
<p>單位新台幣億元。2021–2024 為 HiStock 四季加總；2025 與 MOPS 董事會公告一致（營收 3,090,579 千元、稅後 715,527 千元）。</p>
<table>
  <thead><tr><th>年</th><th>營收</th><th>年增</th><th>毛利率</th><th>營益率</th><th>稅後淨利</th><th>淨利率</th><th>EPS</th></tr></thead>
  <tbody>
    {yr_row(2021)}
    {yr_row(2022)}
    {yr_row(2023)}
    {yr_row(2024)}
    {yr_row(2025)}
  </tbody>
</table>
<div class="chart">{chart_rev}</div>
<p class="caption">圖 1　合併營收（億元）。2021 是疫情底；2022–2025 複合成長率 34.0%（四年 CAGR 78.8% 被低基期放大，不宜當未來速度）。</p>
<div class="chart">{chart_ni}</div>
<p class="caption">圖 2　稅後淨利（億元）。2021 虧 0.86 億；2022 打平；2023–2024 約 1.8–2.1 億；2025 7.16 億。</p>
<div class="chart">{chart_m}</div>
<p class="caption">圖 3　毛利率／營益率／淨利率（%）。2025 毛利率 37.6%、營益率 28.4%——專案組合極好的一年，不是五年平均。</p>

<h3>怎麼讀這五年</h3>
<ul>
  <li><b>2021</b>：場次幾乎停。營收 3.02 億、毛利率 6.9%、營業損失 1.09 億、EPS −2.86。固定成本（場館保證、人力、租金）壓垮規模。</li>
  <li><b>2022</b>：解封反彈，營收跳到 12.83 億（+325%），仍小虧營業利益；稅後勉強轉正 EPS 0.05。量回來、利潤率還沒回來。</li>
  <li><b>2023–2024</b>：進入「能賺錢的主辦商」。營收 13.44→17.30 億，毛利率 29%／27%，EPS 5.94→6.27。2024 年增近三成，東森／公司稿對應鄭中基、羅志祥、王心凌、大河之舞等檔。</li>
  <li><b>2025</b>：結構性高峰。公司自述主因江蕙演唱會、悲慘世界音樂劇、民歌 50。單季看：Q3 營收 18.63 億、EPS 11.20，幾乎等於 2024 全年營收。Q4 回到 3.77 億——檔期落差非常大。</li>
</ul>
<p>中央社 2025-11-04：江蕙巡演 23 場「場場秒殺」。經濟日報轉述法人估 2025 賺近兩個股本——後來公告就是 18.83 元。把 18.83 當 2026–2030 的 run-rate，是把一次天后復出當成每年都有。</p>

<h2>2. 2026 年迄今：高峰後仍有檔，但基期已高</h2>
<table>
  <thead><tr><th>期間</th><th>營收</th><th>年增</th><th>毛利率</th><th>稅後</th><th>EPS</th><th>來源</th></tr></thead>
  <tbody>
    <tr><td>2026Q1</td><td class="n">6.04</td><td class="n">+30.4%</td><td class="n">22.2%</td><td class="n">0.79</td><td class="n">2.08</td><td>MOPS／季報</td></tr>
    <tr><td>2026Q2</td><td class="n">{yi(q2p['rev'])}</td><td class="n">約 +85%</td><td class="n">{q2p['gpm']:.1f}%</td><td class="n">{yi(q2p['ni'])}</td><td class="n">5.29</td><td>MOPS 2026-08-11</td></tr>
    <tr><td>2026H1</td><td class="n">{yi(h1['rev'])}</td><td class="n">{h1['rev_yoy']:+.1f}%</td><td class="n">{h1['gpm']:.1f}%</td><td class="n">{yi(h1['ni'])}</td><td class="n">7.37</td><td>同上；獲利年增 {h1['ni_yoy']:.1f}%</td></tr>
    <tr><td>2026/07 單月</td><td class="n">{yi(jul['rev'])}</td><td class="n">{jul['yoy']:.2f}%</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td>Yahoo 月營收</td></tr>
    <tr><td>2026/01–07</td><td class="n">{yi(jul['ytd'])}</td><td class="n">{jul['ytd_yoy']:.2f}%</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td>累計年減，基期是 2025 江蕙夏檔</td></tr>
  </tbody>
</table>
<p>Q2 毛利率 43%、單季淨利年增 120%，公司稿主因《歌劇魅影》全省三地＋游鴻明、周蕙、盧廣仲、李翊君。H1 毛利率 33.5%、營益率 25.1%，比 2024 全年好、比 2025 全年差——符合「沒有江蕙級單檔、但仍有音樂劇與中大型演唱會」。</p>
<p>7 月年減 87%（9,450 萬 vs 去年同月 7.35 億）是必須寫進報告的數字：去年夏天是江蕙高雄／台北檔認列。1–7 月累計年減 10.7%，代表 <b>2026 年前七個月還沒追上 2025 的前七個月</b>。下半年要看漢斯季默、彭佳慧、XG、KPOP PRIME 等 8 月檔，以及 2027Q1 已宣布的 BIGBANG 高雄世運 2 場（認列時點在明年）。</p>

<h2>3. 資產負債、現金、週轉</h2>
<p>單位億元。流動比取聚財網年報（與資產表流動資產／流動負債一致）。2025 年底現金只剩 1.80 億，但短期投資 16.15 億——獲利現金大量泊在金融資產，不是「帳上沒錢」。</p>
<table>
  <thead><tr><th>時點</th><th>資產</th><th>權益</th><th>負債比</th><th>流動比</th><th>現金</th></tr></thead>
  <tbody>
    {''.join(bs_rows)}
  </tbody>
</table>
<ul>
  <li>長期借款可忽略（2025 年底僅 756 萬）。負債幾乎全是流動：票款預收、應付製作成本。這是主辦商的正常形狀，不是製造業槓桿。</li>
  <li>權益 2025 年底 16.63 億；2026Q1 掉到 10.32 億，對得上 3 月除息 18.7 元（約 7.11 億現金流出）。Q2 賺回 2.01 億後權益 12.32 億、每股淨值 32.42 元。</li>
  <li>合約負債是這一行的營運資金引擎：富聯網 2025 全年營業現金流 13.84 億，其中合約負債增加 3.36 億。票先收、秀後認——OCF 可以大幅高於淨利。</li>
</ul>
<table>
  <thead><tr><th>年</th><th>營業現金流</th><th>稅後淨利</th><th>OCF&gt;淨利？</th></tr></thead>
  <tbody>
    {''.join(ocf_rows)}
  </tbody>
</table>
<p>2023、2025 現金遠多於盈餘（預收款）。2024 OCF 1.71 億略低於淨利 2.09 億。2021–2022 現金為負，對得上虧損與復甦期營運資金。2025 投資現金流 −15.19 億，主因取得按攤銷後成本衡量金融資產 11.49 億——把票款與獲利停泊，不是蓋廠。</p>
<p>應收週轉天數（聚財）：2021 疫情 39 天 → 2022–2025 約 11–17 天。票務為主的生意本來就該短；不是製造應收帳款故事。</p>
<p>年 ROE（聚財，平均權益）：2021 −13.2%、2022 0.3%、2023 26.2%、2024 20.4%、2025 <b>49.7%</b>。2025 的 50% ROE 來自超高淨利率＋權益還沒被次年巨額配息削薄。2026Q1 配完息後權益下降，同樣獲利水準的 ROE 會看起來更高——那是配息數學，不是本業又強了一截。</p>

<h2>4. 股利、評價、股價</h2>
<table>
  <thead><tr><th>所屬年度</th><th>EPS</th><th>現金股利</th><th>配發率</th><th>除息日</th><th>除息價</th><th>當時殖利率</th></tr></thead>
  <tbody>
    <tr><td>2021</td><td class="n">−2.86</td><td class="n">0</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td class="n">—</td></tr>
    <tr><td>2022</td><td class="n">0.05</td><td class="n">0.50</td><td class="n">（盈餘不足，含公積）</td><td>2023-07-10</td><td class="n">56.7</td><td class="n">0.88%</td></tr>
    <tr><td>2023</td><td class="n">5.94</td><td class="n">5.30</td><td class="n">89.2%</td><td>2024-03-28</td><td class="n">78.7</td><td class="n">6.73%</td></tr>
    <tr><td>2024</td><td class="n">6.27</td><td class="n">7.00</td><td class="n">111.6%（盈餘 5＋公積 2）</td><td>2025-04-01</td><td class="n">95.1</td><td class="n">7.36%</td></tr>
    <tr><td>2025</td><td class="n">18.83</td><td class="n">18.70</td><td class="n">99.3%（盈餘 17.7＋公積 1）</td><td>2026-03-26</td><td class="n">144.0</td><td class="n">12.99%</td></tr>
  </tbody>
</table>
<p>政策很清楚：能配就幾乎全配。這對股東友善，也代表 <b>留存無法支撐「每年再辦一次江蕙級保證金」的資本緩衝</b>。下一檔超大型保證若要自有資金扛，會跟高配息打架。</p>
<p>2026-08-27 收盤 96.8 元，市值 {d['mkt']:.2f} 億。近四季 EPS（2025Q3–2026Q2）= 11.20+1.42+2.08+5.29 = <b>{d['ttm_eps']:.2f} 元</b> → 本益比約 <b>{d['pe']:.2f}×</b>（Yahoo 顯示 4.81×，算法接近）。Q2 每股淨值 32.42 → 淨值比約 <b>{d['pbr']:.2f}×</b>。若改用 2025 單年 EPS 18.83，本益比約 5.1×；若改用 2023–2024 的 6 元 EPS，本益比約 16×。市場現在付的是「高峰剛過、還在出清音樂劇檔期」的價格，不是付 2021 的悲觀、也不是把 18.83 當成永續。</p>
<p>鉅亨 52 週：高 181、低 95.1。除息前 144、現價 96.8，價差大致等於那 18.7 元現金（144−18.7=125.3；之後又從 125 落到 97 附近）。填息沒完成。低流動性（當日約 82 張）會放大波動，不適合成交量故事。</p>

<h2>5. 產業未來五年（台灣 × 亞洲 × 全球）</h2>
<h3>5.1 台灣：場館開了，票房已經不小</h3>
<p>財訊引文化內容策進院／售票平台統計：<b>2024 年</b>流行音樂活動（演唱會、見面會、音樂節）2,128 場、票數 304.58 萬張、銷售金額 <b>90.85 億元</b>，年增 13.7%／20.5%／35.2%。台北市 481 場、逾 238 萬人次；高雄 2025 年大型演唱會逾 109 場、163 萬人次。演唱會觀光產值：台北市逾 84.5 億、高雄 52 億（市政府口徑，含住宿餐飲，不是寬宏營收）。</p>
<p>供給側五年內已發生的事不會倒回去：台北大巨蛋、北流、南流、Zepp 新北、高雄國家體育場當巨蛋替代。中型場（5–1.5 萬）補上，讓「不是天后也能開巡演」變成常態。需求側是疫後實體體驗、K-pop 與華語復出、城市把演唱會當觀光入口。</p>
<p>五年約束也很硬：</p>
<ul>
  <li><b>場館時段是上限。</b>小巨蛋、巨蛋、大巨蛋、世運檔期被體育與政府活動切。台灣 2,300 萬人，GD 台北票房能接近東京，正說明單場滲透已很高，不是還有十倍人口紅利。</li>
  <li><b>藝人費與製作成本上漲。</b>全球巡演東移，保證金競標會更激烈。</li>
  <li><b>2024 的 +35% 票房不能外推五年。</b>那是解封＋新場館＋復出潮的重疊。較合理的產業基準是「高個位數到低雙位數票房成長、場次繼續碎裂化」——除非再出下一個江蕙級國民事件。</li>
</ul>

<h3>5.2 全球現場娛樂</h3>
<p>Mordor Intelligence（第三方估計，非公司數字）：全球 live music 2025 約 <b>511 億美元</b>，2026 約 545 億，2031 約 <b>724 億</b>，2026–2031 CAGR <b>5.8%</b>。亞太是最快區，CAGR 6.3%。Triangle Group 募資稿引亞太現場娛樂 2033 年約 <b>750 億美元</b>。韓國 2025 票房 1.7326 兆韓元（約 12.4 億美元，+18.8%）。印度有組織現場活動估 2027 年超過 2.38 億美元量級（INR 20,000 crore）。</p>
<p>Live Nation 2025（SEC／公司稿，可核）：營收 <b>252 億美元</b>（+9%）、演唱會部門 209 億、觀眾 1.59 億人次、55,000 場。2026 年已售票約 6,700 萬張、年增雙位數。這是全球整合商（主辦＋Ticketmaster＋贊助）的規模。</p>
<p>結構趨勢（未來五年比較可能成立的）：串流無法養活中型藝人 → 現場變成主要現金；歐美成本高把巡演推向亞洲；K-pop／華語／音樂劇 IP 跨市場；主辦商垂直整合票務與旅遊套票。反趨勢：保證金泡沫、黃牛監管、場館不足（韓國就是反例）、單一巨星依賴。</p>

<h2>6. 全球競爭力：寬宏站在哪一層</h2>
<p>先換單位。2025 寬宏營收 30.91 億台幣，約 <b>0.95 億美元</b>（以 32.5 計，僅作數量級）。Live Nation 同年 252 億美元。寬宏不是全球賽道的玩家，是 <b>台灣主辦層的上市公司</b>。競爭力要分三層講，才不會把「台灣第一」誤寫成「亞洲第一」。</p>

<h3>6.1 台灣主辦層——相對強</h3>
<table>
  <thead><tr><th>角色</th><th>代表</th><th>與寬宏的關係</th></tr></thead>
  <tbody>
    <tr><td>主辦</td><td>寬宏、理想國演藝（Live Nation 台灣）、超級圓頂、遠雄創藝</td><td>搶檔期、搶藝人、搶保證金</td></tr>
    <tr><td>製作／工程</td><td>必應創造（6625）、源活、設備商</td><td>寬宏可當客戶也可部分內製（台灣藝人）</td></tr>
    <tr><td>票務</td><td>拓元、寬宏售票、KKTix、ibon、udn</td><td>寬宏有自有系統，但拓元仍是龍頭</td></tr>
    <tr><td>場館</td><td>大巨蛋、小巨蛋、北流／南流、高雄巨蛋／世運、Zepp</td><td>寬宏不擁有巨蛋級場館</td></tr>
  </tbody>
</table>
<p>相對優勢（有公開行為支撐，不是市佔神話）：</p>
<ul>
  <li><b>垂直整合。</b>主辦＋售票＋硬體，法說工程收入 10–15%。失敗檔的虧損可以用票務與租賃部分對沖，但不能消滅主辦風險。</li>
  <li><b>華語國民級與音樂劇。</b>江蕙、民歌 50、《悲慘世界》、《歌劇魅影》65 場——這條產品線 Live Nation 台灣與超級圓頂（偏日韓偶像）不是同一戰場。</li>
  <li><b>全額認列票房。</b>營收表面大，毛利率仍能到 30–40%（好檔）。代表定價與成本控制在高峰年是有效的。</li>
  <li><b>資本市場身份。</b>2018 上櫃，能配息、能增資（2024 籌資現金流為正）。對手許多是未上市。</li>
  <li><b>非北北基。</b>法說強調桃園、新竹、屏東、花蓮。這是把場館供給用滿，不是國際化。</li>
</ul>
<p>相對弱：沒有大巨蛋營運權；票務市佔不是第一；員工與資本規模小，同一季很難並列兩檔「保證金破億」的全球巡演；流動性差，股價不是產業溫度計。</p>

<h3>6.2 亞洲層——有嘗試、尚未構成護城河</h3>
<p>法說：把台灣製作的演唱會以軟體包（藝人、樂師、導演）授權給海外主辦，對方負擔場地與硬體。2025 羅志祥授權澳門，規劃新加坡、馬來西亞、港澳。這是輕資產輸出，適合高配息公司，但授權費不會讓營收再翻一倍。2027Q1 BIGBANG 高雄 2 場是「把亞洲 IP 引進台灣」，方向正確，仍是單檔。</p>
<p>亞洲真正在長的是：韓國場館缺口、泰國／新加坡巡演樞紐、東南亞中產。Triangle（新加坡）募 1,500 萬美元、挖 Live Nation 前亞太總裁，說明區域整合商正在出現。寬宏沒有 18 城網絡，五年內比較可能的位置是 <b>台灣節點＋偶發授權</b>，不是亞洲平台。</p>

<h3>6.3 全球層——規模差兩個數量級</h3>
<p>Live Nation 有場館、票務數據、贊助、全球保證金池。AEG 有場館地產。寬宏沒有這三樣。全球競爭力分數若硬打：產品力（華語／音樂劇策展）中上、營運執行（能辦 23 場江蕙）強、資本與網路弱、國際品牌弱。結論應寫成：<b>在台灣現場娛樂供應鏈裡有定價權的主辦商；在全球現場娛樂產業裡是利基進口商與本國策展商。</b></p>

<h2>7. 公司未來五年：三條路徑（不是預測）</h2>
<p>以下是情境，不是目標價、不是公司指引。公司對 2026 的公開用詞是「營運力求穩定」，並點名大型演唱會與國際音樂劇。</p>
<table>
  <thead><tr><th>情境</th><th>假設</th><th>營收帶（約）</th><th>EPS 帶（約）</th><th>要看到的證據</th></tr></thead>
  <tbody>
    <tr><td>保守</td><td>沒有國民級復出；音樂劇與中型演唱會維持；2025 基期消失</td><td>18–24 億</td><td>6–10</td><td>全年沒有單季營收 &gt;10 億；毛利率回到 25–30%</td></tr>
    <tr><td>基準</td><td>每年 1 檔國際音樂劇或大型巡演＋常態華語蛋；海外授權仍小</td><td>22–28 億</td><td>8–13</td><td>2026 全年接近或略低於 2025；H2 能補 7 月缺口</td></tr>
    <tr><td>樂觀</td><td>再出現江蕙級檔＋音樂劇巡演重疊＋授權放量</td><td>30–40 億</td><td>15–22</td><td>連續兩年單季出現 15 億以上；海外收入有單獨揭露</td></tr>
  </tbody>
</table>
<p>基準情境的意思：<b>把 2023–2024 當地板、2025 當天花板事件</b>，而不是把 2025 當新地板。2026H1 已賺 7.37 元，若 H2 只有普通檔，全年仍可能高於 2024 的 6.27、低於 2025 的 18.83——這叫「高峰回落後的高檔」，不是崩潰。</p>
<p>未來五年產業尾風（場館、亞洲巡演、體驗消費）對寬宏是正的；公司能抓住多少，取決於檔期取得，不是取決於本益比。全球競爭力的升級條件只有幾條可驗證的：海外授權佔營收升到雙位數、取得中型場館營運權、票務會員變成可重複變現的資產、不再把幾乎 100% 盈餘配掉以致無法押下檔保證金。</p>

<h2>8. 風險（已看到的）</h2>
<ol>
  <li><b>檔期集中。</b>2025Q3 一個季度 ≈ 2024 全年營收。2026/07 年減 87% 是同一枚硬幣的背面。</li>
  <li><b>巨星不可複製。</b>江蕙 23 場是十年一遇級事件。沒有第二個二姊時，毛利率與 EPS 會從 38%／18.83 往下走。</li>
  <li><b>幾乎全配。</b>2024–2025 配發率 100% 上下。權益在除息季大幅下降。這不是危機，但是成長選項的機會成本。</li>
  <li><b>保證金與藝人費。</b>全球主辦東移，台灣場次競標更貴。一次失敗檔足以吃掉普通年的獲利。</li>
  <li><b>場館與政策。</b>檔期、實名制、黃牛、噪音、觀光補助都是外部變數。寬宏不擁有巨蛋。</li>
  <li><b>認列口徑。</b>100% 票房入營收，跨公司比規模會高估寬宏、低估抽佣同業。</li>
  <li><b>流動性與評價陷阱。</b>日成交數十到數百張。本益比 5× 用的是含江蕙的 TTM。用中週期 EPS 重算會貴很多。</li>
  <li><b>把下半年已宣布的場次當成已入帳。</b>BIGBANG 在 2027Q1；8 月場次要看實際認列月。</li>
</ol>

<h2>9. 結論</h2>
<p>寬宏是台灣現場娛樂裡少數把「主辦風險」做成公開財報的公司。近五年故事分三段：2021 活不下去、2022–2024 正常賺錢、2025 碰到國民事件而賺了近兩個股本。2026 上半年證明它不是只有江蕙——《歌劇魅影》把毛利率做到 43%——但 7 月數字也證明高峰年的基期會咬人。</p>
<p>未來五年，產業（台灣票房百億、亞洲巡演東移、全球 live music 中個位數成長）對主辦商是順風。寬宏的全球競爭力是「本國策展＋音樂劇進口＋輕資產授權」，不是 Live Nation 的場館／票務帝國。股東能期待的比較像：<b>高波動的高配息文化股</b>，而不是平滑的成長複利機器。</p>
<p>基準看法（self-reported）：2025 的 30.9 億／18.83 元是事件，2023–2024 的 13–17 億／6 元才是比較能討論「沒有天后時公司值多少」的底。現價 96.8 已反映除息與高峰回落；要變成成長敘事，得看到第二檔國民級或海外授權變成穩定科目——目前公開數字還沒證明。</p>

<h2>10. 來源</h2>
<p class="src">
MOPS／MoneyDJ：2025 全年合併（2026-03-09）、2026H1 合併（2026-08-11）<br/>
聯合新聞網 2026-08-11 Q2 營運說明（歌劇魅影、BIGBANG 2027Q1）<br/>
中央社 2025-11-04 前三季與江蕙加場<br/>
東森財經：2024 全年 17.3 億、EPS 6.27、股利 7 元<br/>
HiStock：季損益／資產負債／現金流長表（季加總與 MOPS 年報吻合）<br/>
Yahoo 股市：月營收、股利、2026-08-27 收盤 96.8（精誠／櫃買）<br/>
聚財網：年報比率（毛利率、ROE、流動比）<br/>
CMoney 資產表：現金、短期投資、流動資產<br/>
富聯網：2025 現金流量細項（合約負債、金融資產）<br/>
財訊／104 職場力：2024 台灣流行音樂票房 90.85 億<br/>
Mordor Intelligence：全球 live music 2025–2031<br/>
Live Nation 2025 年報／MBW：營收 252 億美元<br/>
公司 IR：http://khaminc.com.tw/　月營收導向 MOPS<br/>
本輪未打 FinMind／FRED，未讀 Augur 庫內價量（環境無 DB）。
</p>
<p class="footer">層級 [I] · 非 META-CONSTITUTION [N] · 非投資建議 · 數字可回溯至上列公開來源 · 編製日 {VIEWPOINT}</p>
</body>
</html>
"""


def md_report(d: dict) -> str:
    y = d["years"]
    h1 = d["h1_26"]
    lines = [
        "---",
        "title: 6596 寬宏藝術近五年財務與未來五年前景",
        f"date: {VIEWPOINT}",
        f"viewpoint: {VIEWPOINT}T16:00+08:00",
        'stock_id: "6596"',
        'layer: "[I]"',
        "self_reported: true",
        "price_tip: 2026-08-27",
        "fs_tip: 2026-06-30",
        "not_advice: true",
        "---",
        "",
        "# 6596 寬宏藝術｜近五年財務與未來五年前景／全球競爭力",
        "",
        f"> **一句**：2025 營收 30.91 億、EPS 18.83、配息 18.7 是江蕙級高峰；2026H1 仍年增但 7 月年減 87%。現價 96.8、市值約 {d['mkt']:.2f} 億、近四季本益比約 {d['pe']:.1f}×。  ",
        "> **不是**：進出場建議。高峰 EPS ≠ 新地板。",
        "",
        "完整排版與圖表見同目錄 PDF／HTML。本環境無 Augur DB、未打 FinMind API。",
        "",
        "## 近五年損益（億元）",
        "",
        "| 年 | 營收 | 年增 | 毛利率 | 營益率 | 稅後 | 淨利率 | EPS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for year in range(2021, 2026):
        r = y[year]
        yoy = "—" if r["yoy"] is None else f"{r['yoy']:+.1f}%"
        lines.append(
            f"| {year} | {yi(r['rev'])} | {yoy} | {r['gpm']:.1f}% | {r['opm']:.1f}% | {yi(r['ni'])} | {r['npm']:.1f}% | {r['eps']:.2f} |"
        )
    lines += [
        "",
        f"2026H1 營收 {yi(h1['rev'])} 億（{h1['rev_yoy']:+.1f}%）、稅後 {yi(h1['ni'])} 億（{h1['ni_yoy']:+.1f}%）、EPS 7.37。",
        f"2026-07 單月 {yi(d['jul26']['rev'])} 億、年減 87.14%；1–7 月累計年減 10.65%。",
        "",
        "## 下載",
        "",
        f"- PDF：`reports/{PDF_NAME}`",
        f"- HTML：`reports/{HTML_NAME}`",
        "",
    ]
    return "\n".join(lines) + "\n"


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = "/usr/local/bin/google-chrome"
    udd = Path("/tmp/chrome-6596-pdf")
    udd.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--no-sandbox", "--disable-dev-shm-usage",
        f"--user-data-dir={udd}",
        "--virtual-time-budget=8000",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    try:
        subprocess.run(cmd, check=True, timeout=45)
    except subprocess.TimeoutExpired:
        if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
            raise
    if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF"):
        raise RuntimeError("PDF 未產出")


def selftest() -> int:
    d = compute()
    assert d["years"][2025]["rev"] == 3090579
    assert d["h1_26"]["eps"] == 7.37
    assert d["ocf"][2025] == 1384342
    print("selftest ok", {"rev2025": d["years"][2025]["rev"], "pe": d["pe"]})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    d = compute()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUT_DIR / HTML_NAME
    pdf_path = OUT_DIR / PDF_NAME
    md_path = OUT_DIR / MD_NAME
    html_path.write_text(html_report(d), encoding="utf-8")
    md_path.write_text(md_report(d), encoding="utf-8")
    print_pdf(html_path, pdf_path)
    print(json.dumps({
        "html": str(html_path),
        "pdf": str(pdf_path),
        "md": str(md_path),
        "pdf_bytes": pdf_path.stat().st_size,
        "mkt": d["mkt"],
        "pe": d["pe"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
