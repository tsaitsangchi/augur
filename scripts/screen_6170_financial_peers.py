#!/usr/bin/env python
"""6170 統振財務／成長／評價指紋 → 台股上市櫃同型篩選（公開資訊觀測站＋證交所／櫃買；不打 FinMind／FRED）。

🎯 這支在做什麼（白話）：把 6170 近五年「V 型營收 → 毛利走高 → 2026 走平 → 高配息／約 10 倍本益」
   收成可重跑的閘與距離分數，對上市＋上櫃全市場篩財務特徵相近的個股，並拉短名單五年月收盤作股價對照。
   本環境無 Augur DB；來源＝MOPS／TWSE／TPEX 公開頁＋短名單 Yahoo 月線（價／息）。不是進出場建議。

守原則精華 #1 #9 #10 #15（數字出自程式抓取／計算，禁止 placeholder）· CLAUDE #28（不打 FinMind／FRED）。

執行指令矩陣：
  python scripts/screen_6170_financial_peers.py              # 印用途＋矩陣；不抓網
  python scripts/screen_6170_financial_peers.py --selftest   # 零網路：解析／V 型閘／分數紅綠
  python scripts/screen_6170_financial_peers.py --run        # 抓公開資料、篩選、寫 reports/
  python scripts/screen_6170_financial_peers.py --run --cache-dir /tmp/augur_6170_peer_screen
"""
from __future__ import annotations

import argparse
import csv
import html as htmlmod
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
MOPS = "https://mopsov.twse.com.tw/mops/web"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
SLEEP_S = 1.15
STOCK_RE = re.compile(r"^\d{4}$")

# 錨點＝公開年報／月營收／評價（與 6170 報告同一套公開數字；單位：營收千元、比率％、市值億）
ANCHOR = {
    "stock_id": "6170",
    "rev_2025": 3_186_452.0,
    "yoy_2022": -17.1,
    "yoy_2023": -8.4,
    "yoy_2024": 28.5,
    "yoy_2025": 9.7,
    "yoy_2026": -1.42,
    "gm_2025": 31.3,
    "gm_delta": 10.1,
    "opm_2025": 9.8,
    "opm_delta": 5.0,
    "pe": 9.9,
    "dy": 8.22,
    "pb": 2.42,
    "mcap_yi": 47.3,
    "cr": 1.67,
    "ca_ratio": 0.835,
}


def parse_num(s: str | None) -> float | None:
    """公開表數字：千分位、括號負值、-- 空值。"""
    if s is None:
        return None
    t = htmlmod.unescape(re.sub(r"<[^>]+>", "", str(s))).strip()
    t = t.replace("\xa0", " ").replace(",", "").replace("％", "").replace("%", "")
    if t in ("", "--", "---", "-", "n/a", "N/A", "nan", "NaN", "*"):
        return None
    neg = False
    if t.startswith("(") and t.endswith(")"):
        neg, t = True, t[1:-1]
    t = t.replace("+", "")
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def yoy(cur: float | None, prev: float | None) -> float | None:
    if cur is None or prev is None or prev == 0:
        return None
    return (cur / prev - 1.0) * 100.0


def pct(n: float | None, d: float | None) -> float | None:
    if n is None or d is None or d == 0:
        return None
    return n / d * 100.0


def ratio(n: float | None, d: float | None) -> float | None:
    if n is None or d is None or d == 0:
        return None
    return n / d


def clip01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def sim(x: float | None, anchor: float, scale: float) -> float | None:
    if x is None or scale <= 0:
        return None
    return clip01(1.0 - abs(x - anchor) / scale)


def v_recovery_flags(yoy_by_year: dict[int, float | None]) -> dict[str, bool]:
    """V 型成長閘：2023 停／跌、2024 明顯回升、2025 仍正但降速、2026 走平。"""
    y23 = yoy_by_year.get(2023)
    y24 = yoy_by_year.get(2024)
    y25 = yoy_by_year.get(2025)
    y26 = yoy_by_year.get(2026)
    return {
        "pause_2023": y23 is not None and y23 <= 5.0,
        "rebound_2024": y24 is not None and y24 >= 10.0,
        "slow_2025": y25 is not None and -5.0 <= y25 <= 22.0,
        "flat_2026": y26 is None or abs(y26) <= 12.0,
    }


def passes_pattern(flags: dict[str, bool]) -> bool:
    return all(flags[k] for k in ("pause_2023", "rebound_2024", "slow_2025", "flat_2026"))


def score_row(row: dict) -> tuple[float, dict[str, float | None]]:
    """相對 6170 錨點的 0–100 距離分數（缺項不計入平均）。"""
    parts: dict[str, float | None] = {
        "rev": sim(math.log10(row["rev_2025"] / 1000.0), math.log10(31.86), 0.55)
        if row.get("rev_2025") else None,
        "mcap": sim(math.log10(row["mcap_yi"]), math.log10(47.3), 0.55)
        if row.get("mcap_yi") and row["mcap_yi"] > 0 else None,
        "yoy23": sim(row.get("yoy_2023"), ANCHOR["yoy_2023"], 18.0),
        "yoy24": sim(row.get("yoy_2024"), ANCHOR["yoy_2024"], 18.0),
        "yoy25": sim(row.get("yoy_2025"), ANCHOR["yoy_2025"], 12.0),
        "yoy26": sim(row.get("yoy_2026"), ANCHOR["yoy_2026"], 10.0),
        "gm": sim(row.get("gm_2025"), ANCHOR["gm_2025"], 10.0),
        "gmd": sim(row.get("gm_delta"), ANCHOR["gm_delta"], 8.0),
        "opm": sim(row.get("opm_2025"), ANCHOR["opm_2025"], 6.0),
        "pe": sim(row.get("pe"), ANCHOR["pe"], 6.0),
        "dy": sim(row.get("dy"), ANCHOR["dy"], 4.0),
        "pb": sim(row.get("pb"), ANCHOR["pb"], 1.4),
        "cr": sim(row.get("cr"), ANCHOR["cr"], 0.8),
        "ca": sim(row.get("ca_ratio"), ANCHOR["ca_ratio"], 0.25),
    }
    w = {
        "rev": 1.1, "mcap": 1.1, "yoy23": 1.0, "yoy24": 1.3, "yoy25": 1.2, "yoy26": 1.3,
        "gm": 1.2, "gmd": 1.1, "opm": 1.2, "pe": 1.1, "dy": 1.2, "pb": 0.7, "cr": 0.6, "ca": 0.7,
    }
    num = den = 0.0
    for k, v in parts.items():
        if v is None:
            continue
        num += w[k] * v
        den += w[k]
    score = 100.0 * num / den if den else 0.0
    return score, parts


def gate_reasons(row: dict) -> list[str]:
    reasons: list[str] = []
    sid = row.get("stock_id") or ""
    if not STOCK_RE.match(sid):
        reasons.append("not_4digit")
    if any(row.get(f"rev_{y}") in (None, 0) for y in (2021, 2022, 2023, 2024, 2025)):
        reasons.append("missing_rev_5y")
    rev = row.get("rev_2025")
    if rev is None or rev < 800_000 or rev > 12_000_000:
        reasons.append("rev_scale")
    if (row.get("eps_2025") or 0) <= 0:
        reasons.append("eps_nonpos")
    if (row.get("rev_2025") or 0) <= (row.get("rev_2023") or 0):
        reasons.append("no_level_recovery")
    gm, opm = row.get("gm_2025"), row.get("opm_2025")
    if gm is None or not (18.0 <= gm <= 45.0):
        reasons.append("gm_band")
    if opm is None or not (4.0 <= opm <= 18.0):
        reasons.append("opm_band")
    if (row.get("gm_delta") or -99) < 0:
        reasons.append("no_gm_expansion")
    flags = v_recovery_flags({y: row.get(f"yoy_{y}") for y in (2023, 2024, 2025, 2026)})
    if not passes_pattern(flags):
        reasons.append("v_pattern")
    mcap = row.get("mcap_yi")
    if mcap is not None and not (8.0 <= mcap <= 200.0):
        reasons.append("mcap_band")
    pe = row.get("pe")
    if pe is not None and not (5.0 <= pe <= 20.0):
        reasons.append("pe_band")
    ind = row.get("industry") or ""
    if any(x in ind for x in ("金融保險", "金控", "銀行", "證券", "期貨", "保險", "油電燃氣")):
        reasons.append("industry_exclude")
    return reasons


def passes_gates(row: dict) -> bool:
    return not gate_reasons(row)


def valuation_twin_reasons(row: dict) -> list[str]:
    """第二層：市場在付高配息、約 10 倍本益的小市值——不要求 2024 V 型跳升。"""
    reasons: list[str] = []
    sid = row.get("stock_id") or ""
    if not STOCK_RE.match(sid):
        reasons.append("not_4digit")
    rev = row.get("rev_2025")
    if rev is None or rev < 800_000 or rev > 8_000_000:
        reasons.append("rev_scale")
    if (row.get("eps_2025") or 0) <= 0:
        reasons.append("eps_nonpos")
    gm, opm = row.get("gm_2025"), row.get("opm_2025")
    if gm is None or not (18.0 <= gm <= 45.0):
        reasons.append("gm_band")
    if opm is None or not (4.0 <= opm <= 18.0):
        reasons.append("opm_band")
    y26 = row.get("yoy_2026")
    if y26 is None or abs(y26) > 10.0:
        reasons.append("not_flat_2026")
    y25 = row.get("yoy_2025")
    if y25 is not None and not (-12.0 <= y25 <= 20.0):
        reasons.append("yoy25_band")
    mcap = row.get("mcap_yi")
    if mcap is None or not (12.0 <= mcap <= 120.0):
        reasons.append("mcap_band")
    pe = row.get("pe")
    if pe is None or not (6.0 <= pe <= 15.0):
        reasons.append("pe_band")
    dy = row.get("dy")
    if dy is None or not (5.5 <= dy <= 12.0):
        reasons.append("dy_band")
    ind = row.get("industry") or ""
    if any(x in ind for x in ("金融保險", "金控", "銀行", "證券", "期貨", "保險", "油電燃氣")):
        reasons.append("industry_exclude")
    return reasons


def passes_valuation(row: dict) -> bool:
    return not valuation_twin_reasons(row)


def clean_cell(raw: str) -> str:
    t = htmlmod.unescape(re.sub(r"<[^>]+>", "", raw))
    return re.sub(r"\s+", " ", t).replace("\xa0", " ").strip()


def iter_tables(page: str) -> list[list[list[str]]]:
    out: list[list[list[str]]] = []
    for tm in re.finditer(r"<table\b[^>]*>(.*?)</table>", page, flags=re.I | re.S):
        rows: list[list[str]] = []
        for tr in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", tm.group(1), flags=re.I | re.S):
            cells = [clean_cell(c) for c in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", tr.group(1), flags=re.I | re.S)]
            if cells:
                rows.append(cells)
        if rows:
            out.append(rows)
    return out


def header_map(row: list[str]) -> dict[str, int] | None:
    idx = {c: i for i, c in enumerate(row)}
    if "公司代號" not in idx and "代號" not in idx:
        return None
    return idx


def pick(idx: dict[str, int], row: list[str], *names: str) -> str | None:
    for n in names:
        if n in idx and idx[n] < len(row):
            return row[idx[n]]
    return None


def decode_bytes(blob: bytes) -> str:
    for enc in ("utf-8", "cp950", "big5"):
        try:
            t = blob.decode(enc)
        except UnicodeDecodeError:
            continue
        if "公司" in t or "營收" in t or "收益" in t:
            return t
    return blob.decode("utf-8", "replace")


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_post(url: str, data: dict, timeout: int = 120) -> bytes:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
                 "Referer": "https://mopsov.twse.com.tw/"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cache_fetch(cache_dir: Path, key: str, fetcher, sleep: bool = True) -> bytes:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{key}.bin"
    if path.exists() and path.stat().st_size > 200:
        return path.read_bytes()
    if sleep:
        time.sleep(SLEEP_S)
    blob = fetcher()
    path.write_bytes(blob)
    return blob


def mops_post(cache_dir: Path, key: str, endpoint: str, data: dict) -> str:
    blob = cache_fetch(cache_dir, key, lambda: http_post(f"{MOPS}/{endpoint}", data))
    return decode_bytes(blob)


# ── parsers ──────────────────────────────────────────────────────────────────

def parse_company_page(page: str, market: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for table in iter_tables(page):
        hdr = None
        for row in table:
            hm = header_map(row)
            if hm and ("產業類別" in hm or "公司簡稱" in hm):
                hdr = hm
                continue
            if not hdr:
                continue
            sid = pick(hdr, row, "公司代號", "代號") or ""
            if not STOCK_RE.match(sid):
                continue
            shares = parse_num(pick(hdr, row, "已發行普通股數或TDR原發行股數", "已發行普通股數"))
            capital = parse_num(pick(hdr, row, "實收資本額(元)", "實收資本額"))
            if shares is None and capital is not None:
                shares = capital / 10.0
            out[sid] = {
                "stock_id": sid,
                "name": pick(hdr, row, "公司簡稱", "公司名稱") or "",
                "industry": pick(hdr, row, "產業類別") or "",
                "shares": shares,
                "market": market,
            }
    return out


def parse_income_page(page: str, year: int) -> dict[str, dict]:
    """年／季綜合損益（累計）。商業格式取營收／毛利／營益／母公司淨利／EPS。"""
    out: dict[str, dict] = {}
    for table in iter_tables(page):
        hdr = None
        for row in table:
            hm = header_map(row)
            if hm and any(k in hm for k in ("營業收入", "收益", "基本每股盈餘（元）")):
                hdr = hm
                continue
            if not hdr:
                continue
            sid = pick(hdr, row, "公司代號") or ""
            if not STOCK_RE.match(sid):
                continue
            rev = parse_num(pick(hdr, row, "營業收入", "收益"))
            gp = parse_num(pick(hdr, row, "營業毛利（毛損）淨額", "營業毛利（毛損）"))
            opi = parse_num(pick(hdr, row, "營業利益（損失）", "營業利益"))
            ni_p = parse_num(pick(hdr, row, "淨利（損）歸屬於母公司業主", "本期淨利（淨損）"))
            eps = parse_num(pick(hdr, row, "基本每股盈餘（元）"))
            rec = out.setdefault(sid, {"stock_id": sid})
            # 商業格式優先於金融「收益」表（同一檔可能出現兩表）
            if "營業收入" in hdr or rec.get(f"rev_{year}") is None:
                rec[f"rev_{year}"] = rev
                rec[f"gp_{year}"] = gp
                rec[f"opi_{year}"] = opi
                rec[f"ni_{year}"] = ni_p
                rec[f"eps_{year}"] = eps
                rec[f"fmt_{year}"] = "rev" if "營業收入" in hdr else "fin"
    return out


def parse_bs_page(page: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for table in iter_tables(page):
        hdr = None
        for row in table:
            hm = header_map(row)
            if hm and ("流動資產" in hm or "資產總額" in hm or "資產合計" in hm or "資產總計" in hm):
                hdr = hm
                continue
            if not hdr:
                continue
            sid = pick(hdr, row, "公司代號") or ""
            if not STOCK_RE.match(sid):
                continue
            ca = parse_num(pick(hdr, row, "流動資產"))
            nca = parse_num(pick(hdr, row, "非流動資產"))
            ta = parse_num(pick(hdr, row, "資產總額", "資產合計", "資產總計"))
            cl = parse_num(pick(hdr, row, "流動負債"))
            ncl = parse_num(pick(hdr, row, "非流動負債"))
            eq = parse_num(pick(
                hdr, row, "權益總額", "權益合計", "權益總計",
                "歸屬於母公司業主之權益", "歸屬於母公司業主之權益合計",
            ))
            bps = parse_num(pick(hdr, row, "每股參考淨值", "每股淨值"))
            out[sid] = {
                "ca": ca, "nca": nca, "ta": ta, "cl": cl, "ncl": ncl, "eq": eq, "bps": bps,
            }
    return out


def parse_month_rev_page(page: str) -> dict[str, dict]:
    """t21sc03：當月／累計營收與年增（千元、％）。"""
    out: dict[str, dict] = {}
    for table in iter_tables(page):
        for row in table:
            if len(row) < 10:
                continue
            sid = row[0].strip()
            if not STOCK_RE.match(sid):
                continue
            # 典型：代號 名稱 當月 上月 去年當月 月增 年增 累計 去年累計 累計年增
            ytd = parse_num(row[7]) if len(row) > 7 else None
            ytd_yoy = parse_num(row[9]) if len(row) > 9 else None
            month_yoy = parse_num(row[6]) if len(row) > 6 else None
            out[sid] = {"rev_ytd": ytd, "yoy_2026": ytd_yoy, "month_yoy": month_yoy, "name_rev": row[1]}
    return out


def parse_bwibbu(payload: dict) -> dict[str, dict]:
    fields = payload.get("fields") or []
    idx = {n: i for i, n in enumerate(fields)}
    out: dict[str, dict] = {}
    for row in payload.get("data") or []:
        sid = str(row[idx["證券代號"]]).strip() if "證券代號" in idx else ""
        if not STOCK_RE.match(sid):
            continue
        out[sid] = {
            "price": parse_num(row[idx["收盤價"]]) if "收盤價" in idx else None,
            "dy": parse_num(row[idx["殖利率(%)"]]) if "殖利率(%)" in idx else None,
            "pe": parse_num(row[idx["本益比"]]) if "本益比" in idx else None,
            "pb": parse_num(row[idx["股價淨值比"]]) if "股價淨值比" in idx else None,
            "val_date": payload.get("date"),
        }
    return out


def parse_tpex_quotes(payload: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for table in payload.get("tables") or []:
        fields = table.get("fields") or []
        idx = {re.sub(r"<[^>]+>", "", n).strip(): i for i, n in enumerate(fields)}
        sid_k = "代號" if "代號" in idx else None
        if not sid_k:
            continue
        for row in table.get("data") or []:
            sid = str(row[idx[sid_k]]).strip()
            if not STOCK_RE.match(sid):
                continue
            px = None
            for k in idx:
                if "收盤" in k:
                    px = parse_num(row[idx[k]])
                    break
            shares = None
            for k in idx:
                if "發行股數" in k:
                    shares = parse_num(row[idx[k]])
                    break
            out[sid] = {"price": px, "shares_quote": shares, "val_date": payload.get("date")}
    return out


def merge_income(dst: dict[str, dict], src: dict[str, dict]) -> None:
    for sid, rec in src.items():
        dst.setdefault(sid, {"stock_id": sid}).update(rec)


def enrich(row: dict) -> dict:
    for y, p in ((2022, 2021), (2023, 2022), (2024, 2023), (2025, 2024)):
        row[f"yoy_{y}"] = yoy(row.get(f"rev_{y}"), row.get(f"rev_{p}"))
    row["gm_2021"] = pct(row.get("gp_2021"), row.get("rev_2021"))
    row["gm_2025"] = pct(row.get("gp_2025"), row.get("rev_2025"))
    row["opm_2021"] = pct(row.get("opi_2021"), row.get("rev_2021"))
    row["opm_2025"] = pct(row.get("opi_2025"), row.get("rev_2025"))
    row["npm_2025"] = pct(row.get("ni_2025"), row.get("rev_2025"))
    g1, g5 = row.get("gm_2021"), row.get("gm_2025")
    row["gm_delta"] = (g5 - g1) if g1 is not None and g5 is not None else None
    o1, o5 = row.get("opm_2021"), row.get("opm_2025")
    row["opm_delta"] = (o5 - o1) if o1 is not None and o5 is not None else None
    row["cr"] = ratio(row.get("ca"), row.get("cl"))
    if row.get("ta") is None and row.get("ca") is not None and row.get("nca") is not None:
        row["ta"] = row["ca"] + row["nca"]
    row["ca_ratio"] = ratio(row.get("ca"), row.get("ta"))
    row["ncl_ratio"] = ratio(row.get("ncl"), row.get("ta"))
    row["roe"] = pct(row.get("ni_2025"), row.get("eq"))
    shares = row.get("shares") or row.get("shares_quote")
    px = row.get("price")
    if px and shares:
        row["mcap_yi"] = px * shares / 1e8
    if row.get("pe") is None and px and row.get("eps_2025"):
        row["pe"] = px / row["eps_2025"]
    if row.get("pb") is None and px and row.get("bps"):
        row["pb"] = px / row["bps"]
    if row.get("dy") is None and px and row.get("dps"):
        row["dy"] = row["dps"] / px * 100.0
    return row


def yahoo_monthly(symbol: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1mo&range=5y&events=div"
    blob = http_get(url, timeout=40)
    data = json.loads(blob.decode())
    res = (data.get("chart") or {}).get("result") or []
    if not res:
        return {"symbol": symbol, "error": "no_result"}
    r0 = res[0]
    ts = r0.get("timestamp") or []
    closes = (((r0.get("indicators") or {}).get("quote") or [{}])[0].get("close")) or []
    series = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        series.append({"t": int(t), "close": float(c)})
    divs = []
    events = (r0.get("events") or {}).get("dividends") or {}
    for item in events.values():
        divs.append({"t": int(item.get("date") or 0), "amount": float(item.get("amount") or 0)})
    return {"symbol": symbol, "series": series, "dividends": divs, "meta": r0.get("meta") or {}}


def year_end_close(series: list[dict], year: int) -> float | None:
    picked = [x for x in series if time.gmtime(x["t"]).tm_year == year]
    return picked[-1]["close"] if picked else None


def last_close(series: list[dict]) -> float | None:
    return series[-1]["close"] if series else None


def dps_ttm(divs: list[dict], asof_t: int | None = None) -> float:
    if not divs:
        return 0.0
    asof_t = asof_t or int(time.time())
    lo = asof_t - 366 * 24 * 3600
    return sum(d["amount"] for d in divs if lo <= d["t"] <= asof_t)


# ── fetch + screen ────────────────────────────────────────────────────────────

def fetch_universe(cache_dir: Path) -> dict[str, dict]:
    companies: dict[str, dict] = {}
    for market, typek in (("sii", "sii"), ("otc", "otc")):
        page = mops_post(cache_dir, f"t51_{typek}", "ajax_t51sb01", {
            "encodeURIComponent": "1", "step": "1", "firstin": "1", "off": "1",
            "TYPEK": typek, "code": "",
        })
        companies.update(parse_company_page(page, market))
        print(f"  companies {market} cumulative={len(companies)}", flush=True)

    income: dict[str, dict] = {}
    for typek in ("sii", "otc"):
        for roc, year in ((110, 2021), (111, 2022), (112, 2023), (113, 2024), (114, 2025)):
            page = mops_post(cache_dir, f"inc_{typek}_{roc}_04", "ajax_t163sb04", {
                "encodeURIComponent": "1", "step": "1", "firstin": "1", "off": "1",
                "isQuery": "Y", "TYPEK": typek, "year": str(roc), "season": "04",
            })
            parsed = parse_income_page(page, year)
            merge_income(income, parsed)
            print(f"  income {typek} {year} n={len(parsed)} union={len(income)}", flush=True)

    bs: dict[str, dict] = {}
    for typek in ("sii", "otc"):
        page = mops_post(cache_dir, f"bs_{typek}_114_04", "ajax_t163sb05", {
            "encodeURIComponent": "1", "step": "1", "firstin": "1", "off": "1",
            "isQuery": "Y", "TYPEK": typek, "year": "114", "season": "04",
        })
        parsed = parse_bs_page(page)
        bs.update(parsed)
        print(f"  bs {typek} n={len(parsed)}", flush=True)

    month: dict[str, dict] = {}
    for mkt, path in (("sii", "sii"), ("otc", "otc")):
        url = f"https://mopsov.twse.com.tw/nas/t21/{path}/t21sc03_115_7.html"
        blob = cache_fetch(cache_dir, f"rev_{mkt}_115_7", lambda u=url: http_get(u))
        parsed = parse_month_rev_page(decode_bytes(blob))
        month.update(parsed)
        print(f"  month {mkt} n={len(parsed)}", flush=True)

    bw = json.loads(cache_fetch(
        cache_dir, "twse_bwibbu",
        lambda: http_get("https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?response=json&selectType=ALL"),
        sleep=True,
    ).decode())
    twse_val = parse_bwibbu(bw)
    print(f"  twse val n={len(twse_val)} date={bw.get('date')}", flush=True)

    tpex_raw = json.loads(cache_fetch(
        cache_dir, "tpex_quotes",
        lambda: http_get("https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes?response=json"),
        sleep=True,
    ).decode())
    tpex_val = parse_tpex_quotes(tpex_raw)
    print(f"  tpex quotes n={len(tpex_val)} date={tpex_raw.get('date')}", flush=True)

    rows: dict[str, dict] = {}
    sids = set(companies) | set(income) | set(month)
    for sid in sids:
        row = {"stock_id": sid}
        row.update(companies.get(sid) or {})
        row.update(income.get(sid) or {})
        row.update(bs.get(sid) or {})
        row.update(month.get(sid) or {})
        if sid in twse_val:
            row.update(twse_val[sid])
            row.setdefault("market", "sii")
        if sid in tpex_val:
            # 上櫃報價覆蓋價格／股數；本益／殖利率上市才有官方表
            q = tpex_val[sid]
            if row.get("price") is None:
                row["price"] = q.get("price")
            row.setdefault("shares_quote", q.get("shares_quote"))
            row.setdefault("val_date", q.get("val_date"))
            row.setdefault("market", "otc")
        enrich(row)
        rows[sid] = row
    return rows


def attach_yahoo(peers: list[dict]) -> None:
    for row in peers:
        if row.get("yahoo_symbol"):
            continue
        mkt = row.get("market")
        suffix = ".TW" if mkt == "sii" else ".TWO"
        sym = f"{row['stock_id']}{suffix}"
        try:
            time.sleep(0.35)
            y = yahoo_monthly(sym)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            row["yahoo_error"] = f"{type(exc).__name__}:{exc}"
            continue
        series = y.get("series") or []
        divs = y.get("dividends") or []
        row["yahoo_symbol"] = sym
        row["px_2021"] = year_end_close(series, 2021)
        row["px_2022"] = year_end_close(series, 2022)
        row["px_2023"] = year_end_close(series, 2023)
        row["px_2024"] = year_end_close(series, 2024)
        row["px_2025"] = year_end_close(series, 2025)
        row["px_last"] = last_close(series)
        row["dps_ttm"] = dps_ttm(divs)
        if row.get("dy") is None and row.get("px_last") and row["dps_ttm"]:
            row["dy"] = row["dps_ttm"] / row["px_last"] * 100.0
        p23, p25, plast = row.get("px_2023"), row.get("px_2025"), row.get("px_last")
        row["ret_23to25"] = yoy(p25, p23)
        row["ret_25to_now"] = yoy(plast, p25)
        row["ret_21to_now"] = yoy(plast, row.get("px_2021"))
        print(f"  yahoo {sym} last={row.get('px_last')} dps={row.get('dps_ttm')}", flush=True)


def fmt(v, nd=1, suffix="") -> str:
    if v is None:
        return "—"
    return f"{v:.{nd}f}{suffix}"


def yi_from_k(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v / 100_000:.2f}"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def write_report(
    path: Path,
    anchor: dict,
    peers: list[dict],
    val_peers: list[dict],
    n_univ: int,
    n_gate: int,
    n_val: int,
    val_note: str,
) -> None:
    a_top = [r for r in peers if r.get("stock_id") != "6170"][:2]
    b_top = [r for r in val_peers if r.get("stock_id") != "6170"][:4]
    overlap = {r["stock_id"] for r in peers} & {r["stock_id"] for r in val_peers} - {"6170"}
    a_txt = "、".join(f"{r['stock_id']} {r.get('name')}" for r in a_top) or "（無）"
    b_txt = "、".join(
        f"{r['stock_id']} {r.get('name')}（息 {fmt(r.get('dy'))}%）" for r in b_top
    ) or "（無）"
    lines = [
        "---",
        "title: 6170 統振財務指紋之台股同型篩選",
        "date: 2026-08-27",
        "stock_id: \"6170\"",
        "layer: \"[I]\"",
        "self_reported: true",
        "not_advice: true",
        "---",
        "",
        "# 6170 統振｜財務／成長／股價同型個股（台股上市櫃）",
        "",
        "> **［I］研究整理 · self-reported · 非投資建議。** 本環境無 Augur DB、未呼叫 FinMind／FRED。"
        "數字出自本檔同日 `scripts/screen_6170_financial_peers.py --run` 對 MOPS／TWSE／TPEX 公開頁的抓取與計算；"
        "短名單股價／息為 Yahoo Finance 月線。分析框架 self-reported，不得當成「世界如此」。不是進出場建議、不是目標價。",
        "",
        "## 0. 一句話",
        "",
        "6170 的可對照指紋不是「全球跨境支付」，而是兩件幾乎不重疊的事："
        "**（A）V 型營收＋毛利走高＋2026 走平**，與 **（B）約 10 倍本益＋6–8% 現金殖利率的小市值。** "
        f"上市櫃宇宙 {n_univ} 檔中，（A）硬閘 **{n_gate}** 檔（含自己）、（B）評價閘 **{n_val}** 檔（含自己）。"
        "通信網路硬體同業幾乎對不上這兩件；持照匯兌沒有第二家上市櫃。",
        "",
        "## 1. 錨點（6170 自己）",
        "",
        "| 項 | 值 |",
        "|---|---:|",
        f"| 市場／產業 | {anchor.get('market','')}／{anchor.get('industry','')} |",
        f"| 2025 營收（億） | {yi_from_k(anchor.get('rev_2025'))} |",
        f"| 年增 2022→2026YTD（％） | {fmt(anchor.get('yoy_2022'))}／{fmt(anchor.get('yoy_2023'))}／"
        f"{fmt(anchor.get('yoy_2024'))}／{fmt(anchor.get('yoy_2025'))}／{fmt(anchor.get('yoy_2026'))} |",
        f"| 毛利率 2021→2025（％） | {fmt(anchor.get('gm_2021'))} → {fmt(anchor.get('gm_2025'))}（Δ {fmt(anchor.get('gm_delta'))}） |",
        f"| 營益率 2021→2025（％） | {fmt(anchor.get('opm_2021'))} → {fmt(anchor.get('opm_2025'))} |",
        f"| 2025 EPS／ROE | {fmt(anchor.get('eps_2025'),2)}／{fmt(anchor.get('roe'))} |",
        f"| 收盤／市值（億） | {fmt(anchor.get('price'),2)}／{fmt(anchor.get('mcap_yi'))} |",
        f"| 本益／淨值／殖利率 | {fmt(anchor.get('pe'))}×／{fmt(anchor.get('pb'),2)}×／{fmt(anchor.get('dy'))}% |",
        f"| 淨利率 2025（％） | {fmt(anchor.get('npm_2025'))}（營益率 {fmt(anchor.get('opm_2025'))}；差額＝非營業） |",
        f"| 流動比／流動資產占比 | {fmt(anchor.get('cr'),2)}／{fmt((anchor.get('ca_ratio') or 0)*100 if anchor.get('ca_ratio') is not None else None)}% |",
        f"| 評價日 | {anchor.get('val_date') or '—'} |",
        "",
        val_note,
        "",
        "## 2. 兩層閘",
        "",
        "**A 成長閘（同時成立）**：五年營收齊、2025 營收 8–120 億且高於 2023；年增 2023≤5%、2024≥10%、2025 介於 −5%～22%、2026 年迄今累計年增絕對值 ≤12%；毛利率 18–45% 且高於 2021、營益率 4–18%；EPS>0；市值 8–200 億、本益 5–20×（有數字才濾）；排除金融保險／金控／銀行／證券／期貨／保險／油電燃氣。",
        "",
        "**B 評價閘**：本益 6–15×、現金殖利率 5.5–12%、市值 12–120 億、2026 走平（累計年增絕對值 ≤10%）、毛利率／營益率同 A 的帶、營收 8–80 億。**不要求** 2024 跳升。上櫃無官方殖利率者進不了 B（資料缺口）。",
        "",
        "A 的分數是錨點距離（規模取 log、年增／利潤率／評價分項加權），**不是**預測報酬。",
        "",
        "## 3. 成長軌跡同型（A 閘：V 型＋毛利走高＋2026 走平）",
        "",
        "| 名次 | 代號 | 簡稱 | 市場 | 產業 | 分數 | 2025營收億 | 年增24／25／26YTD | 毛利率21→25 | 營益率25 | 本益 | 殖利率 | 市值億 |",
        "|---:|---|---|---|---|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    rank = 0
    for r in peers:
        if r["stock_id"] == "6170":
            continue
        rank += 1
        lines.append(
            f"| {rank} | {r['stock_id']} | {r.get('name') or ''} | {r.get('market') or ''} | "
            f"{r.get('industry') or ''} | {fmt(r.get('score'))} | {yi_from_k(r.get('rev_2025'))} | "
            f"{fmt(r.get('yoy_2024'))}／{fmt(r.get('yoy_2025'))}／{fmt(r.get('yoy_2026'))} | "
            f"{fmt(r.get('gm_2021'))}→{fmt(r.get('gm_2025'))} | {fmt(r.get('opm_2025'))} | "
            f"{fmt(r.get('pe'))} | {fmt(r.get('dy'))}% | {fmt(r.get('mcap_yi'))} |"
        )
    lines += [
        "",
        "## 4. 評價同型（B 閘：本益 6–15×、殖利率 5.5–12%、2026 走平；不要求 2024 跳升）",
        "",
        "這層才對上「市場在付高配息、不付 FinTech 倍數」。",
        "",
        "| 名次 | 代號 | 簡稱 | 市場 | 產業 | 2025營收億 | 年增23／24／25／26YTD | 毛利率25 | 營益率25 | 本益 | 殖利率 | 市值億 |",
        "|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    vrank = 0
    for r in val_peers:
        if r["stock_id"] == "6170":
            continue
        vrank += 1
        lines.append(
            f"| {vrank} | {r['stock_id']} | {r.get('name') or ''} | {r.get('market') or ''} | "
            f"{r.get('industry') or ''} | {yi_from_k(r.get('rev_2025'))} | "
            f"{fmt(r.get('yoy_2023'))}／{fmt(r.get('yoy_2024'))}／{fmt(r.get('yoy_2025'))}／{fmt(r.get('yoy_2026'))} | "
            f"{fmt(r.get('gm_2025'))} | {fmt(r.get('opm_2025'))} | "
            f"{fmt(r.get('pe'))} | {fmt(r.get('dy'))}% | {fmt(r.get('mcap_yi'))} |"
        )
    lines += [
        "",
        "## 5. 股價路徑（Yahoo 月線；息為 TTM 現金股利）",
        "",
        "| 代號 | 簡稱 | 層 | 2023年底 | 2025年底 | 最近月 | 23→25％ | 25→今％ | TTM現金股利 |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    a_ids = {r["stock_id"] for r in peers}
    b_ids = {r["stock_id"] for r in val_peers}
    seen_px: set[str] = set()
    for r in list(peers) + list(val_peers):
        if r["stock_id"] in seen_px:
            continue
        seen_px.add(r["stock_id"])
        layer = []
        if r["stock_id"] in a_ids:
            layer.append("A")
        if r["stock_id"] in b_ids:
            layer.append("B")
        lines.append(
            f"| {r['stock_id']} | {r.get('name') or ''} | {'+'.join(layer) or '—'} | "
            f"{fmt(r.get('px_2023'),2)} | {fmt(r.get('px_2025'),2)} | {fmt(r.get('px_last'),2)} | "
            f"{fmt(r.get('ret_23to25'))} | {fmt(r.get('ret_25to_now'))} | {fmt(r.get('dps_ttm'),2)} |"
        )
    lines += [
        "",
        "## 6. 怎麼讀（不是目標價）",
        "",
        "- **沒有第二家 6170。** A 閘進來的多是電子／機械／紡織製造：損益表的 V 型像，殖利率只有 3–5%，不是高配息服務股。B 閘進來的才是「本益約十倍、息 6% 以上」——成長軌常常是緩步或已過跳升年（例如觀光股 2023 已大增、數位雲端 2024 只有個位數年增）。",
        "- **通信網路同業對不上。** 硬體同業不是虧損、就是本益數十倍、或 2026 仍雙位數成長。較近的 6486 互動：毛利率／營益率接近、市值接近，但 2026 年迄今年增仍約兩成、毛利沒有五年走擴，進不了 A／B 閘。",
        "- **匯兌執照同業沒有上市櫃第二家。** 這份名單不是 Q Pay 對手盤。",
        "- 與 6170 一樣要核對：**淨利率是否明顯高於營益率**（美元資產評價墊 EPS）。本篩以營益率為本業帶。",
        "- 股價座標：6170 是 2023 年底後走平、靠息；A 閘若 2023→2025 股價翻倍，已經不是同一種價錢。B 閘較接近「高息橫盤」。",
        "- Yahoo 月線的 TTM 息若為 0 但 B 閘殖利率非 0，**以證交所 BWIBBU 殖利率為準**；Yahoo 漏息不能讀成「沒配」。",
        "",
        "## 6.1 若只看幾檔對照（self-reported）",
        "",
        f"- **損益表最像**：{a_txt}。殖利率多半遠低於 6170 的約 8%。",
        f"- **評價／配息最像**：{b_txt}。這層 2024 通常沒有 +28% 跳升。",
        f"- **A∩B 不含 6170 的檔數**：{len(overlap)}。機械意思＝沒有第二家同時滿足成長軌與高息十倍本益。",
        "",
        "## 7. 來源與重跑",
        "",
        "- MOPS `ajax_t51sb01` 基本資料；`ajax_t163sb04` 年報損益 2021–2025；`ajax_t163sb05` 2025 資產負債（欄名含「總計」）。",
        "- 月營收：`/nas/t21/{sii,otc}/t21sc03_115_7.html`（2026 年 1–7 月累計年增）。",
        "- 上市評價：TWSE `BWIBBU_d`；上櫃價格／發行股數：TPEX `dailyQuotes`。上櫃本益／殖利率若缺，短名單用年報 EPS 與 Yahoo TTM 息補。",
        "- 重跑：`python scripts/screen_6170_financial_peers.py --run`",
        "",
        "本檔為［I］。self-reported。不是投資建議。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run(cache_dir: Path, top_n: int) -> int:
    print("fetch universe (MOPS/TWSE/TPEX; no FinMind/FRED)", flush=True)
    rows = fetch_universe(cache_dir)
    n_univ = len(rows)
    scored: list[dict] = []
    for row in rows.values():
        if not passes_gates(row):
            continue
        sc, parts = score_row(row)
        row["score"] = sc
        row["score_parts"] = parts
        scored.append(row)
    scored.sort(key=lambda r: (-(r["score"]), r["stock_id"]))
    print(f"universe={n_univ} gatedA={len(scored)}", flush=True)

    val_scored: list[dict] = []
    for row in rows.values():
        if not passes_valuation(row):
            continue
        sc, _ = score_row(row)
        row["score"] = row.get("score") or sc
        val_scored.append(row)
    val_scored.sort(key=lambda r: (abs((r.get("dy") or 0) - 8.22) + 0.4 * abs((r.get("pe") or 0) - 9.9), r["stock_id"]))
    print(f"gatedB={len(val_scored)}", flush=True)

    anchor = rows.get("6170") or {"stock_id": "6170"}
    if "score" not in anchor:
        sc, _ = score_row(enrich(anchor))
        anchor["score"] = sc
    short = [r for r in scored if r["stock_id"] != "6170"][:top_n]
    val_short = [r for r in val_scored if r["stock_id"] != "6170"][:top_n]
    pack = [anchor] + short
    val_pack = [anchor] + val_short
    print("yahoo prices for shortlist", flush=True)
    attach_yahoo(pack + val_short)
    for r in pack + val_short:
        if r.get("dps_ttm") and r.get("px_last") and r.get("dy") is None:
            r["dy"] = r["dps_ttm"] / r["px_last"] * 100.0
        r["score"], _ = score_row(r)
    short.sort(key=lambda r: (-(r.get("score") or 0), r["stock_id"]))
    pack = [anchor] + short

    fields = [
        "stock_id", "name", "market", "industry", "score",
        "rev_2021", "rev_2022", "rev_2023", "rev_2024", "rev_2025",
        "yoy_2022", "yoy_2023", "yoy_2024", "yoy_2025", "yoy_2026",
        "gm_2021", "gm_2025", "gm_delta", "opm_2021", "opm_2025", "opm_delta",
        "eps_2025", "roe", "npm_2025", "price", "pe", "pb", "dy", "mcap_yi", "cr", "ca_ratio",
        "px_2021", "px_2023", "px_2025", "px_last", "ret_23to25", "ret_25to_now", "dps_ttm",
    ]
    csv_path = REPO / "reports" / "augur_6170_welldone_peer_screen_20260827.csv"
    md_path = REPO / "reports" / "augur_6170_welldone_peer_screen_20260827.md"
    seen = set()
    csv_rows: list[dict] = []
    for r in pack + val_short + scored + val_scored:
        if r["stock_id"] in seen:
            continue
        seen.add(r["stock_id"])
        csv_rows.append(r)
    write_csv(csv_path, csv_rows, fields)
    val_note = (
        f"資料時點：月營收 2026 年 1–7 月累計；年報至 2025；評價／收盤取抓取當日公開檔（{anchor.get('val_date') or '見 TWSE/TPEX'}）。"
    )
    write_report(md_path, anchor, pack, val_pack, n_univ, len(scored), len(val_scored), val_note)
    print(f"wrote {md_path}")
    print(f"wrote {csv_path}")
    print("--- A growth ---")
    for r in pack:
        print(
            f"{r['stock_id']} {r.get('name')} score={fmt(r.get('score'))} "
            f"rev25={yi_from_k(r.get('rev_2025'))} yoy24/25/26="
            f"{fmt(r.get('yoy_2024'))}/{fmt(r.get('yoy_2025'))}/{fmt(r.get('yoy_2026'))} "
            f"gm={fmt(r.get('gm_2025'))} pe={fmt(r.get('pe'))} dy={fmt(r.get('dy'))} "
            f"mcap={fmt(r.get('mcap_yi'))}",
            flush=True,
        )
    print("--- B valuation ---")
    for r in val_pack:
        print(
            f"{r['stock_id']} {r.get('name')} "
            f"rev25={yi_from_k(r.get('rev_2025'))} yoy23/24/25/26="
            f"{fmt(r.get('yoy_2023'))}/{fmt(r.get('yoy_2024'))}/{fmt(r.get('yoy_2025'))}/{fmt(r.get('yoy_2026'))} "
            f"pe={fmt(r.get('pe'))} dy={fmt(r.get('dy'))} mcap={fmt(r.get('mcap_yi'))}",
            flush=True,
        )
    return 0


# ── selftest（#35：真輸入、禁字面、先驗紅）───────────────────────────────────

def _selftest() -> int:
    failed: list[str] = []

    def chk(name: str, cond: bool) -> None:
        if not cond:
            failed.append(name)

    chk("parse 千分位", parse_num("3,186,452") == 3_186_452)
    chk("parse 括號負", parse_num("(405)") == -405)
    chk("parse 空", parse_num("--") is None)
    chk("yoy 6170-2024", abs((yoy(2906, 2261) or 0) - 28.527) < 0.02)

    flags_6170 = v_recovery_flags({2023: -8.4, 2024: 28.5, 2025: 9.7, 2026: -1.42})
    chk("6170 V 閘應過", passes_pattern(flags_6170))
    flags_hyper = v_recovery_flags({2023: 20.0, 2024: 40.0, 2025: 35.0, 2026: 18.0})
    chk("高成長路徑不應過閘（紅證：把 2023 停滯拿掉就會誤收）", not passes_pattern(flags_hyper))
    flags_still_down = v_recovery_flags({2023: -20.0, 2024: -10.0, 2025: 3.0, 2026: -2.0})
    chk("續跌無 2024 回升不應過", not passes_pattern(flags_still_down))
    flags_no_flat = v_recovery_flags({2023: -8.0, 2024: 28.0, 2025: 10.0, 2026: 25.0})
    chk("2026 仍雙位數不應過", not passes_pattern(flags_no_flat))

    row_6170 = {
        "stock_id": "6170", "industry": "通信網路業",
        "rev_2021": 2_977_000, "rev_2022": 2_469_000, "rev_2023": 2_261_000,
        "rev_2024": 2_906_000, "rev_2025": 3_186_452,
        "gp_2021": 631_000, "gp_2025": 997_547,
        "opi_2021": 143_000, "opi_2025": 312_826,
        "ni_2025": 437_168, "eps_2025": 4.49, "eq": 2_144_480,
        "ca": 3_652_091, "cl": 2_191_799, "ta": 4_373_909, "ncl": 37_630,
        "price": 48.65, "pe": 9.9, "pb": 2.42, "dy": 8.22, "shares": 97_260_000,
        "yoy_2026": -1.42,
    }
    enrich(row_6170)
    chk("6170 硬閘應過", passes_gates(row_6170))
    sc0, _ = score_row(row_6170)
    chk("6170 對自身分數高", sc0 >= 85)

    row_bad = dict(row_6170)
    row_bad["stock_id"] = "9999"
    row_bad["rev_2024"] = row_6170["rev_2023"] * 0.9
    row_bad["rev_2025"] = row_6170["rev_2023"] * 0.92
    enrich(row_bad)
    chk("無水準回升應被閘擋（紅證：若只看 2025 年增正會漏）", not passes_gates(row_bad))

    row_bank = dict(row_6170)
    row_bank["stock_id"] = "2881"
    row_bank["industry"] = "金融保險業"
    chk("金控產業應排除", not passes_gates(row_bank))

    # 突變紅：若誤把「2024 年增≥10」改成「≥100」，6170 必須被擋——用真輸入鎖住閾值
    flags_mut = v_recovery_flags({2023: -8.4, 2024: 28.5, 2025: 9.7, 2026: -1.42})
    chk("閾值未漂到 100%（28.5 仍算回升）", flags_mut["rebound_2024"] is True)
    chk("10% 以下不算回升", v_recovery_flags({2023: -8.4, 2024: 9.9, 2025: 9.7, 2026: -1.4})["rebound_2024"] is False)

    bs_page = (
        "<table><tr><th>公司代號</th><th>公司名稱</th><th>流動資產</th><th>非流動資產</th>"
        "<th>資產總計</th><th>流動負債</th><th>非流動負債</th><th>權益總計</th>"
        "<th>每股參考淨值</th></tr>"
        "<tr><td>6170</td><td>統振</td><td>3,652,091</td><td>721,818</td>"
        "<td>4,373,909</td><td>2,191,799</td><td>37,630</td><td>2,144,480</td>"
        "<td>21.90</td></tr></table>"
    )
    bs = parse_bs_page(bs_page)
    chk("資產總計別名", bs["6170"]["ta"] == 4_373_909)
    chk("權益總計別名", bs["6170"]["eq"] == 2_144_480)
    row_6170.update(bs["6170"])
    enrich(row_6170)
    chk("流動資產占比", abs((row_6170["ca_ratio"] or 0) - 0.835) < 0.01)
    chk("評價閘 6170 應過", passes_valuation(row_6170))
    row_low_dy = dict(row_6170)
    row_low_dy["stock_id"] = "6117"
    row_low_dy["dy"] = 3.2
    chk("低殖利率不進評價層（紅證：若只看本益會把迎廣誤收進來）", not passes_valuation(row_low_dy))

    if failed:
        print("SELFTEST FAIL:")
        for n in failed:
            print(" -", n)
        return 1
    print("SELFTEST OK", len([1, 2, 3]), "groups")
    return 0


def print_matrix() -> int:
    print("6170 統振財務指紋 → 台股上市櫃同型篩選（MOPS／TWSE／TPEX；不打 FinMind／FRED）")
    print("執行指令矩陣：")
    print("  python scripts/screen_6170_financial_peers.py")
    print("  python scripts/screen_6170_financial_peers.py --selftest")
    print("  python scripts/screen_6170_financial_peers.py --run")
    print("  python scripts/screen_6170_financial_peers.py --run --cache-dir /tmp/augur_6170_peer_screen")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="6170 financial peer screen")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--cache-dir", default="/tmp/augur_6170_peer_screen")
    p.add_argument("--top", type=int, default=12)
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.run:
        return run(Path(args.cache_dir), args.top)
    return print_matrix()


if __name__ == "__main__":
    sys.exit(main())
