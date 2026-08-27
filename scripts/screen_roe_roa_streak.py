#!/usr/bin/env python3
"""台股 ROE／ROA 連續六年嚴格遞增篩選 — 公開資訊觀測站年報財務分析（零 FinMind／FRED）。

🎯 這支在做什麼（白話）：從 MOPS「財務分析資料查詢彙總表」t51sb02 抓上市＋上櫃
   各年「資產報酬率(%)」「權益報酬率(%)」，篩出
   2020<2021<2022<2023<2024<2025 同時成立於 ROE 與 ROA 的股票，
   依 2025 年 ROE 由高到低列出代號、名稱、六年 ROE／ROA，並寫 CSV／Markdown／HTML／PDF。

守 #1（來源＝MOPS 申報值，缺列即排除）· #9／#10（數字可追溯）· #15（不補 placeholder）·
#24 精神（對公開站溫和間隔，不狂打）。本支不連 DB、不打 FinMind／FRED。

執行指令矩陣：
  python3 scripts/screen_roe_roa_streak.py                 # 印用途＋矩陣（不打網）
  python3 scripts/screen_roe_roa_streak.py --selftest      # 純函式＋HTML fixture 紅綠自測（零 IO）
  python3 scripts/screen_roe_roa_streak.py --run           # 抓 MOPS、篩選、寫 reports/ 與 PDF
  python3 scripts/screen_roe_roa_streak.py --run --out-dir reports
  python3 scripts/screen_roe_roa_streak.py --from-csv reports/augur_tw_roe_roa_streak_20260827.csv
  python3 scripts/screen_roe_roa_streak.py --pdf-from reports/augur_tw_roe_roa_streak_20260827.html
"""
from __future__ import annotations

import argparse
import csv
import http.cookiejar
import json
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

import _bootstrap  # noqa: F401

YEARS = (2020, 2021, 2022, 2023, 2024, 2025)
MARKETS = (("sii", "上市"), ("otc", "上櫃"))
MOPS_FORM = "https://mopsov.twse.com.tw/mops/web/t51sb02"
MOPS_AJAX = "https://mopsov.twse.com.tw/mops/web/ajax_t51sb02"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TZ8 = timezone(timedelta(hours=8))
MISSING_TOKENS = {"", "--", "-", "—", "NA", "N/A", "n/a", "不適用", "無"}


class _TableParser(HTMLParser):
    """只抽 HTML table 列；不依賴 bs4／pandas。"""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", "", "".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if self._row:
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def parse_ratio(raw: str | None) -> float | None:
    """把 MOPS 儲存格轉成百分比數字；缺值／非數字 → None（#1 不補）。"""
    if raw is None:
        return None
    s = str(raw).strip().replace(",", "").replace("%", "").replace("\u3000", "")
    s = s.replace("△", "").replace("▲", "")
    if s in MISSING_TOKENS:
        return None
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def strictly_increasing(xs: list[float]) -> bool:
    """嚴格遞增（相鄰必須 <，相等不算）。"""
    if len(xs) < 2:
        return False
    return all(a < b for a, b in zip(xs, xs[1:]))


def meets_roe_roa_streak(roe: list[float], roa: list[float]) -> bool:
    """六年 ROE 與六年 ROA 皆嚴格遞增才過關。"""
    return (
        len(roe) == len(roa) == len(YEARS)
        and strictly_increasing(roe)
        and strictly_increasing(roa)
    )


def _metric_header_row(table: list[list[str]]) -> list[str] | None:
    for row in table[:4]:
        joined = "".join(row)
        if "資產報酬率" in joined and "權益報酬率" in joined:
            return row
    return None


def _roa_roe_offsets(metric_header: list[str]) -> tuple[int, int]:
    roa_i = roe_i = None
    for i, h in enumerate(metric_header):
        if "資產報酬率" in h:
            roa_i = i
        elif "權益報酬率" in h:
            roe_i = i
    if roa_i is None or roe_i is None:
        raise ValueError(f"表頭找不到 ROA／ROE：{metric_header}")
    return roa_i, roe_i


@dataclass
class YearRow:
    stock_id: str
    name: str
    market: str
    roa: float
    roe: float


def parse_t51sb02_html(html: str, market: str) -> list[YearRow]:
    """從 t51sb02 HTML 抽出（代號, 名稱, ROA, ROE）。"""
    p = _TableParser()
    p.feed(html)
    if not p.tables:
        return []
    table = max(p.tables, key=lambda t: len(t) * max((len(r) for r in t), default=0))
    metric_header = _metric_header_row(table)
    if metric_header is None:
        return []
    roa_off, roe_off = _roa_roe_offsets(metric_header)
    out: list[YearRow] = []
    for row in table:
        if len(row) < 4:
            continue
        sid = row[0]
        if not re.fullmatch(r"[0-9]{4}[0-9A-Za-z]?", sid):
            continue
        metrics = row[2:]
        if roa_off >= len(metrics) or roe_off >= len(metrics):
            continue
        roa = parse_ratio(metrics[roa_off])
        roe = parse_ratio(metrics[roe_off])
        if roa is None or roe is None:
            continue
        name = row[1].replace("\u3000", "").strip()
        out.append(YearRow(sid, name, market, roa, roe))
    return out


class MopsClient:
    def __init__(self, pause_s: float = 1.2):
        self.pause_s = pause_s
        self._ctx = ssl.create_default_context()
        jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar),
            urllib.request.HTTPSHandler(context=self._ctx),
        )
        self._warmed = False

    def _headers(self, *, ajax: bool = False) -> dict[str, str]:
        h = {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        }
        if ajax:
            h["Content-Type"] = "application/x-www-form-urlencoded"
            h["Origin"] = "https://mopsov.twse.com.tw"
            h["Referer"] = MOPS_FORM
        return h

    def _warm(self) -> None:
        if self._warmed:
            return
        req = urllib.request.Request(MOPS_FORM, headers=self._headers())
        with self._opener.open(req, timeout=45) as r:
            r.read()
        self._warmed = True
        time.sleep(min(self.pause_s, 0.8))

    def fetch_year(self, ad_year: int, typek: str) -> str:
        self._warm()
        roc = ad_year - 1911
        body = urlencode(
            {
                "encodeURIComponent": "1",
                "run": "Y",
                "step": "1",
                "TYPEK": typek,
                "year": str(roc),
                "firstin": "1",
                "off": "1",
                "ifrs": "Y",
            }
        ).encode()
        req = urllib.request.Request(
            MOPS_AJAX, data=body, headers=self._headers(ajax=True), method="POST"
        )
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                with self._opener.open(req, timeout=60) as r:
                    raw = r.read()
                time.sleep(self.pause_s)
                return raw.decode("utf-8", errors="replace")
            except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
                last_err = e
                time.sleep(2.0 * (attempt + 1))
        raise RuntimeError(f"MOPS 抓取失敗 year={ad_year} TYPEK={typek}: {last_err}")


@dataclass
class Screened:
    stock_id: str
    name: str
    market: str
    roe: dict[int, float]
    roa: dict[int, float]


@dataclass
class ScreenResult:
    rows: list[Screened]
    n_year_market: dict[tuple[int, str], int] = field(default_factory=dict)
    n_complete_both: int = 0
    n_roe_only: int = 0
    n_roa_only: int = 0
    fetched_at: str = ""
    source: str = MOPS_FORM


def screen_panel(
    panel: dict[str, dict[int, YearRow]],
) -> tuple[list[Screened], int, int, int]:
    """panel[sid][year] = YearRow → 過關列＋完整樣本／單邊遞增計數。"""
    complete = roe_only = roa_only = 0
    hits: list[Screened] = []
    for sid, by_year in panel.items():
        if any(y not in by_year for y in YEARS):
            continue
        roe = [by_year[y].roe for y in YEARS]
        roa = [by_year[y].roa for y in YEARS]
        complete += 1
        roe_ok = strictly_increasing(roe)
        roa_ok = strictly_increasing(roa)
        if roe_ok and not roa_ok:
            roe_only += 1
        if roa_ok and not roe_ok:
            roa_only += 1
        if roe_ok and roa_ok:
            latest = by_year[YEARS[-1]]
            hits.append(
                Screened(
                    stock_id=sid,
                    name=latest.name,
                    market=latest.market,
                    roe={y: by_year[y].roe for y in YEARS},
                    roa={y: by_year[y].roa for y in YEARS},
                )
            )
    hits.sort(key=lambda r: (-r.roe[YEARS[-1]], r.stock_id))
    return hits, complete, roe_only, roa_only


def run_screen(client: MopsClient) -> ScreenResult:
    panel: dict[str, dict[int, YearRow]] = {}
    n_year_market: dict[tuple[int, str], int] = {}
    for ad_year in YEARS:
        for typek, market in MARKETS:
            html = client.fetch_year(ad_year, typek)
            rows = parse_t51sb02_html(html, market)
            n_year_market[(ad_year, market)] = len(rows)
            print(f"  {ad_year} {market}: {len(rows)} 列", flush=True)
            if not rows:
                raise RuntimeError(f"MOPS {ad_year} {market} 解析為空——停止以免假空表")
            for row in rows:
                panel.setdefault(row.stock_id, {})[ad_year] = row
    hits, complete, roe_only, roa_only = screen_panel(panel)
    now = datetime.now(TZ8).strftime("%Y-%m-%d %H:%M %z")
    return ScreenResult(
        rows=hits,
        n_year_market=n_year_market,
        n_complete_both=complete,
        n_roe_only=roe_only,
        n_roa_only=roa_only,
        fetched_at=now,
    )


def _fmt(v: float) -> str:
    return f"{v:.2f}"


def result_from_csv(path: Path, *, fetched_at: str = "", n_complete_both: int = 0,
                    n_roe_only: int = 0, n_roa_only: int = 0) -> ScreenResult:
    rows: list[Screened] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for rec in csv.DictReader(f):
            rows.append(
                Screened(
                    stock_id=rec["stock_id"],
                    name=rec["name"],
                    market=rec["market"],
                    roe={y: float(rec[f"ROE_{y}"]) for y in YEARS},
                    roa={y: float(rec[f"ROA_{y}"]) for y in YEARS},
                )
            )
    return ScreenResult(
        rows=rows,
        n_complete_both=n_complete_both,
        n_roe_only=n_roe_only,
        n_roa_only=n_roa_only,
        fetched_at=fetched_at,
    )
    fields = (
        ["rank", "stock_id", "name", "market"]
        + [f"ROE_{y}" for y in YEARS]
        + [f"ROA_{y}" for y in YEARS]
    )
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(result.rows, 1):
            row = {
                "rank": i,
                "stock_id": r.stock_id,
                "name": r.name,
                "market": r.market,
            }
            for y in YEARS:
                row[f"ROE_{y}"] = _fmt(r.roe[y])
                row[f"ROA_{y}"] = _fmt(r.roa[y])
            w.writerow(row)


def _stats_block(result: ScreenResult) -> str:
    lines = [
        f"- 抓取時點（UTC+8）：{result.fetched_at}",
        f"- 來源：公開資訊觀測站「財務分析資料查詢彙總表」`t51sb02`（{MOPS_FORM}）",
        "- 市場：上市（sii）＋上櫃（otc）；興櫃未納（年報財務分析覆蓋不完整）",
        "- 口徑：各公司申報之**年度**資產報酬率(%)、權益報酬率(%)（E 點通：年報引用申報財務分析；"
        "ROA＝稅後純益／平均資產總額；ROE＝稅後純益／平均權益總額）",
        "- 篩選：ROE 與 ROA 皆須 **2020<2021<2022<2023<2024<2025**（嚴格小於；相等淘汰）",
        "- 排序：2025 年 ROE 由高到低",
        f"- 六年 ROE＋ROA 皆有值之股票數：{result.n_complete_both}",
        f"- 僅 ROE 六年遞增：{result.n_roe_only}；僅 ROA 六年遞增：{result.n_roa_only}",
        f"- **雙條件皆過：{len(result.rows)}**",
    ]
    for (y, mkt), n in sorted(result.n_year_market.items()):
        lines.append(f"- {y} {mkt} 解析列數：{n}")
    return "\n".join(lines)


def write_markdown(path: Path, result: ScreenResult) -> None:
    lines = [
        "# 台股 ROE／ROA 連續六年嚴格遞增名單（2020–2025）",
        "",
        "> **不是**進出場建議。本表只篩公開年報財務分析數字的單調性，不評估本業品質、不宣稱可交易。",
        "",
        "## 資料與口徑",
        "",
        _stats_block(result),
        "",
        "## 名單（依 2025 年 ROE 排序）",
        "",
        "| 序 | 代號 | 名稱 | 市場 | "
        + " | ".join(f"ROE {y}" for y in YEARS)
        + " | "
        + " | ".join(f"ROA {y}" for y in YEARS)
        + " |",
        "|" + "|".join(["---"] * 4) + "|" + "|".join(["---:"] * (len(YEARS) * 2)) + "|",
    ]
    for i, r in enumerate(result.rows, 1):
        cells = [str(i), r.stock_id, r.name, r.market]
        cells += [_fmt(r.roe[y]) for y in YEARS]
        cells += [_fmt(r.roa[y]) for y in YEARS]
        lines.append("| " + " | ".join(cells) + " |")
    if not result.rows:
        lines.append("| （無） | — | — | — |" + " | ".join(["—"] * (len(YEARS) * 2)) + " |")
    lines += [
        "",
        "## 誠實邊界",
        "",
        "- 本環境無 Augur PostgreSQL，故**未**用庫內 `TaiwanStockFinancialStatements` 重算；"
        "數字直接取 MOPS 申報財務分析（與 E 點通年報口徑相同）。",
        "- 未打 FinMind／FRED。",
        "- 缺任一年 ROE 或 ROA（`--`／未申報）即不進名單，不補值。",
        "- 金融業／KY／異會計年度公司只要該年有申報值即納入比較，未另設產業門。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html(path: Path, pdf_name: str, result: ScreenResult) -> None:
    rows_html = []
    for i, r in enumerate(result.rows, 1):
        tds = [
            f"<td class='c'>{i}</td>",
            f"<td class='c'>{r.stock_id}</td>",
            f"<td>{r.name}</td>",
            f"<td class='c'>{r.market}</td>",
        ]
        for y in YEARS:
            cls = "num hi" if y == YEARS[-1] else "num"
            tds.append(f"<td class='{cls}'>{_fmt(r.roe[y])}</td>")
        for y in YEARS:
            tds.append(f"<td class='num'>{_fmt(r.roa[y])}</td>")
        rows_html.append("<tr>" + "".join(tds) + "</tr>")
    if not rows_html:
        rows_html.append(
            f"<tr><td colspan='{4 + 2 * len(YEARS)}' class='c'>無符合條件之股票</td></tr>"
        )
    roe_ths = "".join(f"<th>ROE {y}</th>" for y in YEARS)
    roa_ths = "".join(f"<th>ROA {y}</th>" for y in YEARS)
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8"/>
<title>台股 ROE／ROA 連續六年嚴格遞增（2020–2025）</title>
<style>
  @page {{ size: A3 landscape; margin: 10mm; }}
  body {{ font-family: "WenQuanYi Micro Hei", "Noto Sans CJK TC", sans-serif;
         color:#1a1a1a; font-size:12px; }}
  h1 {{ font-size:22px; margin:0 0 6px; }}
  .sub {{ color:#444; margin:0 0 12px; }}
  .meta {{ background:#f4f6f8; padding:10px 14px; border-radius:6px; margin-bottom:14px; }}
  .meta ul {{ margin:6px 0 0; padding-left:1.2em; }}
  .dl {{ margin:0 0 12px; }}
  .dl a {{ display:inline-block; background:#0b5cab; color:#fff; text-decoration:none;
           padding:8px 14px; border-radius:4px; font-size:14px; }}
  @media print {{ .dl {{ display:none; }} }}
  table {{ border-collapse:collapse; width:100%; }}
  th, td {{ border:1px solid #cfd6dd; padding:4px 6px; }}
  th {{ background:#0b5cab; color:#fff; font-weight:600; }}
  tr:nth-child(even) td {{ background:#f7fafc; }}
  .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .c {{ text-align:center; }}
  .hi {{ font-weight:700; background:#e8f1fb !important; }}
  .note {{ margin-top:12px; color:#444; font-size:11px; }}
</style>
</head>
<body>
  <h1>台股 ROE／ROA 連續六年嚴格遞增名單</h1>
  <p class="sub">條件：2020&lt;2021&lt;2022&lt;2023&lt;2024&lt;2025 同時成立於 ROE 與 ROA　·　依 2025 年 ROE 排序　·　單位：%</p>
  <p class="dl"><a href="{pdf_name}" download>下載 PDF</a>
     <a href="{pdf_name.replace('.pdf','.csv')}" download style="background:#2c7a4b;margin-left:8px;">下載 CSV</a></p>
  <div class="meta">
    <strong>資料與口徑</strong>
    <ul>
      <li>抓取時點（UTC+8）：{result.fetched_at}</li>
      <li>來源：公開資訊觀測站財務分析資料查詢彙總表 t51sb02</li>
      <li>市場：上市＋上櫃；六年 ROE＋ROA 皆有值 {result.n_complete_both} 檔；雙條件皆過 <strong>{len(result.rows)}</strong> 檔</li>
      <li>僅 ROE 遞增 {result.n_roe_only}；僅 ROA 遞增 {result.n_roa_only}</li>
      <li>嚴格小於（相等淘汰）；缺年不補值。本表非投資建議。</li>
    </ul>
  </div>
  <table>
    <thead>
      <tr>
        <th>序</th><th>代號</th><th>名稱</th><th>市場</th>
        {roe_ths}{roa_ths}
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
  <p class="note">未使用 FinMind／FRED；本環境無 Augur DB，數字直接取 MOPS 申報年報財務分析。</p>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _cjk_font() -> Path:
    """文泉驛 TTC 含中英數字；抽出 TTF 給 fpdf2 嵌字。"""
    ttc = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
    ttf = Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
    if ttc.is_file():
        from fontTools.ttLib import TTCollection

        tmp = Path(tempfile.gettempdir()) / "augur-wqy-microhei.ttf"
        if not tmp.is_file() or tmp.stat().st_size < 100_000:
            TTCollection(str(ttc)).fonts[0].save(str(tmp))
        return tmp
    if ttf.is_file():
        return ttf
    raise FileNotFoundError("找不到中文字型（文泉驛微米黑 / Droid Sans Fallback）")


def write_pdf_fpdf(path: Path, result: ScreenResult) -> None:
    """用系統 CJK 字型嵌字產生 PDF（可抽字、不依賴 Chrome）。"""
    from fpdf import FPDF

    font = _cjk_font()
    pdf = FPDF(orientation="L", unit="mm", format="A3")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.add_font("cjk", fname=str(font))
    pdf.set_font("cjk", size=16)
    pdf.cell(0, 9, "台股 ROE／ROA 連續六年嚴格遞增名單（2020–2025）", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("cjk", size=10)
    pdf.multi_cell(
        0,
        5,
        "條件：ROE 與 ROA 皆 2020<2021<2022<2023<2024<2025（嚴格小於）　·　"
        f"依 2025 年 ROE 排序　·　單位 %　·　過關 {len(result.rows)} 檔／"
        f"六年皆有值 {result.n_complete_both} 檔　·　抓取 {result.fetched_at}　·　"
        "來源：公開資訊觀測站 t51sb02　·　本表非投資建議",
    )
    pdf.ln(2)
    headers = (
        ["序", "代號", "名稱", "市場"]
        + [f"ROE{y}" for y in YEARS]
        + [f"ROA{y}" for y in YEARS]
    )
    widths = [10, 16, 22, 14] + [22] * 12
    pdf.set_font("cjk", size=8)
    pdf.set_fill_color(11, 92, 171)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    if not result.rows:
        pdf.cell(sum(widths), 7, "無符合條件之股票", border=1, align="C")
        pdf.ln()
    for i, r in enumerate(result.rows, 1):
        if i % 2 == 0:
            pdf.set_fill_color(247, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        vals = (
            [str(i), r.stock_id, r.name, r.market]
            + [_fmt(r.roe[y]) for y in YEARS]
            + [_fmt(r.roa[y]) for y in YEARS]
        )
        aligns = ["C", "C", "L", "C"] + ["R"] * 12
        for v, w, a in zip(vals, widths, aligns):
            pdf.cell(w, 7, v, border=1, fill=True, align=a)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("cjk", size=8)
    pdf.multi_cell(
        0,
        4.5,
        "口徑：年度資產報酬率＝稅後純益／平均資產總額；權益報酬率＝稅後純益／平均權益總額"
        "（MOPS 年報財務分析申報值）。缺年不補值。未打 FinMind／FRED；本環境無 Augur DB。",
    )
    pdf.output(str(path))


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    """Chrome headless 轉 PDF。寫完檔後 Chrome 可能不退出，故設 timeout＋驗檔。"""
    udd = tempfile.mkdtemp(prefix="chrome-pdf-")
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={udd}",
        "--no-pdf-header-footer",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={pdf_path.resolve()}",
        f"file://{html_path.resolve()}",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=35)
    except subprocess.TimeoutExpired:
        if not (pdf_path.is_file() and pdf_path.stat().st_size > 1000):
            raise
    finally:
        shutil.rmtree(udd, ignore_errors=True)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise RuntimeError(f"PDF 未產出或過小: {pdf_path}")


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("parse 30.29", parse_ratio("30.29") == 30.29)
    chk("parse 缺值 --", parse_ratio("--") is None)
    chk("parse 括號負數", parse_ratio("(1.25)") == -1.25)
    chk("遞增真", strictly_increasing([1, 2, 3, 4, 5, 6]))
    # 紅鎖：若誤用 <=，相等會被當成過關
    chk("相等必須紅", not strictly_increasing([1, 2, 2, 3, 4, 5]))
    chk("回降必須紅", not strictly_increasing([1, 2, 3, 4, 5, 4]))
    roe_ok = [1, 2, 3, 4, 5, 6]
    roa_ok = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    chk("雙遞增過關", meets_roe_roa_streak(roe_ok, roa_ok))
    chk("ROE 平盤不過", not meets_roe_roa_streak([1, 2, 2, 4, 5, 6], roa_ok))
    chk("ROA 回降不過", not meets_roe_roa_streak(roe_ok, [0.1, 0.2, 0.4, 0.3, 0.5, 0.6]))

    fixture = """
    <table class="hasBorder">
      <tr><th>公司代號</th><th>公司簡稱</th><th>財務結構</th><th>償債能力</th>
          <th>經營能力</th><th>獲利能力</th><th>現金流量</th></tr>
      <tr>
        <td>負債佔資產比率(%)</td><td>長期資金佔不動產、廠房及設備比率(%)</td>
        <td>流動比率(%)</td><td>速動比率(%)</td><td>利息保障倍數(%)</td>
        <td>應收款項週轉率(次)</td><td>平均收現日數</td><td>存貨週轉率(次)</td>
        <td>平均銷貨日數</td><td>不動產、廠房及設備週轉率(次)</td>
        <td>總資產週轉率(次)</td><td>資產報酬率(%)</td><td>權益報酬率(%)</td>
        <td>稅前純益佔實收資本比率(%)</td><td>純益率(%)</td><td>每股盈餘(元)</td>
        <td>現金流量比率(%)</td><td>現金流量允當比率(%)</td><td>現金再投資比率(%)</td>
      </tr>
      <tr>
        <td>2330</td><td>台積電</td><td>35.39</td><td>167.77</td><td>244.23</td>
        <td>220.95</td><td>71.51</td><td>12.19</td><td>29.94</td><td>4.71</td>
        <td>77.49</td><td>0.92</td><td>0.47</td><td>19.32</td><td>30.29</td>
        <td>542.11</td><td>40.51</td><td>45.25</td><td>144.42</td><td>110.14</td>
        <td>14.35</td>
      </tr>
      <tr>
        <td>9999</td><td>缺值 Dummy</td><td>1</td><td>1</td><td>1</td><td>1</td>
        <td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td>
        <td>--</td><td>--</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td>
      </tr>
    </table>
    """
    parsed = parse_t51sb02_html(fixture, "上市")
    chk("fixture 只收有值列", len(parsed) == 1)
    chk("fixture 2330 ROA", parsed and abs(parsed[0].roa - 19.32) < 1e-9)
    chk("fixture 2330 ROE", parsed and abs(parsed[0].roe - 30.29) < 1e-9)

    # 面板：一檔過關、一檔 ROE 平、一檔缺年
    def yr(sid, name, seq_roe, seq_roa):
        return {
            y: YearRow(sid, name, "上市", seq_roa[i], seq_roe[i])
            for i, y in enumerate(YEARS)
        }

    panel = {
        "1111": yr("1111", "過關", [1, 2, 3, 4, 5, 6], [0.5, 1, 1.5, 2, 2.5, 3]),
        "2222": yr("2222", "ROE平ROA升", [1, 2, 2, 4, 5, 6], [0.5, 1, 1.5, 2, 2.5, 3]),
        "3333": {2020: YearRow("3333", "缺年", "上市", 1, 1)},
    }
    hits, complete, roe_only, roa_only = screen_panel(panel)
    chk("面板完整樣本=2", complete == 2)
    chk("過關 1 檔", len(hits) == 1 and hits[0].stock_id == "1111")
    chk("ROA 單邊 1（ROE 平盤）", roa_only == 1 and roe_only == 0)
    chk("依 2025 ROE 排序鍵存在", hits[0].roe[2025] == 6)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _print_matrix() -> int:
    doc = (__doc__ or "").strip()
    print(doc.split("執行指令矩陣")[0].strip())
    print("\n執行指令矩陣：")
    print("  python3 scripts/screen_roe_roa_streak.py                 # 本說明（不打網）")
    print("  python3 scripts/screen_roe_roa_streak.py --selftest      # 零 IO 自測")
    print("  python3 scripts/screen_roe_roa_streak.py --run           # 抓 MOPS 寫報告＋PDF")
    print("  python3 scripts/screen_roe_roa_streak.py --from-csv reports/augur_tw_roe_roa_streak_20260827.csv")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="台股 ROE／ROA 六年嚴格遞增篩選（MOPS）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true", help="抓 MOPS 並寫出報告")
    ap.add_argument("--pdf-from", help="既有 HTML 轉 PDF（Chrome；不再抓網）")
    ap.add_argument("--from-csv", help="既有 CSV 用 CJK 字型重出 PDF（不再抓網）")
    ap.add_argument("--out-dir", default="reports")
    ap.add_argument("--pause", type=float, default=1.2, help="兩次 MOPS 請求間隔秒")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.pdf_from:
        html_path = Path(args.pdf_from)
        pdf_path = html_path.with_suffix(".pdf")
        html_to_pdf(html_path, pdf_path)
        print(f"PDF {pdf_path} ({pdf_path.stat().st_size} bytes)", flush=True)
        return 0
    if args.from_csv:
        csv_path = Path(args.from_csv)
        md_path = csv_path.with_suffix(".md")
        meta = {"fetched_at": datetime.now(TZ8).strftime("%Y-%m-%d %H:%M %z")}
        if md_path.is_file():
            md = md_path.read_text(encoding="utf-8")
            def _grab(label: str) -> str | None:
                m = re.search(rf"{re.escape(label)}：([^\n]+)", md)
                return m.group(1).strip() if m else None
            fa = _grab("抓取時點（UTC+8）")
            if fa:
                meta["fetched_at"] = fa
            for key, label in (
                ("n_complete_both", "六年 ROE＋ROA 皆有值之股票數"),
                ("n_roe_only", "僅 ROE 六年遞增"),
                ("n_roa_only", "僅 ROA 六年遞增"),
            ):
                raw = _grab(label)
                if raw and re.match(r"\d+", raw):
                    meta[key] = int(re.match(r"\d+", raw).group(0))
        result = result_from_csv(csv_path, **meta)
        pdf_path = csv_path.with_suffix(".pdf")
        write_pdf_fpdf(pdf_path, result)
        print(f"PDF {pdf_path} ({pdf_path.stat().st_size} bytes)", flush=True)
        return 0
    if not args.run:
        return _print_matrix()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = "20260827"
    stem = f"augur_tw_roe_roa_streak_{stamp}"
    print("抓取 MOPS t51sb02（上市＋上櫃 × 2020–2025）…", flush=True)
    result = run_screen(MopsClient(pause_s=args.pause))
    csv_path = out_dir / f"{stem}.csv"
    md_path = out_dir / f"{stem}.md"
    html_path = out_dir / f"{stem}.html"
    pdf_path = out_dir / f"{stem}.pdf"
    write_csv(csv_path, result)
    write_markdown(md_path, result)
    write_html(html_path, pdf_path.name, result)
    print(f"過關 {len(result.rows)} 檔；寫 {csv_path.name} / {md_path.name} / {html_path.name}", flush=True)
    try:
        write_pdf_fpdf(pdf_path, result)
    except ImportError:
        print("fpdf2 未裝，改走 Chrome headless", flush=True)
        html_to_pdf(html_path, pdf_path)
    print(f"PDF {pdf_path} ({pdf_path.stat().st_size} bytes)", flush=True)
    # 機器可重跑摘要（reports/*.json 被 gitignore；stdout 為 #9 來源）
    summary = {
        "n_pass": len(result.rows),
        "n_complete_both": result.n_complete_both,
        "n_roe_only": result.n_roe_only,
        "n_roa_only": result.n_roa_only,
        "fetched_at": result.fetched_at,
        "ids": [r.stock_id for r in result.rows],
    }
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
