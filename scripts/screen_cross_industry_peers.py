#!/usr/bin/env python3
"""跨產業財務指紋對照 — 以錨股五年損益／體質／價量路徑，在上市櫃中找不同產業、路徑相近的個股。

🎯 這支在做什麼（白話）：從公開資訊觀測站（MOPS／mopsov）抓上市＋上櫃年報綜合損益與
最新資產負債，配證交所／櫃買收盤與本益／淨值比，以及 Yahoo 還原價路徑，對錨股
（預設 4166 友霖）做可重跑的相似度排序。不打 FinMind／FRED。不是進出場建議。

守原則精華 #1 #9 #15（數字只出自本次 HTTP／解析輸出）；#28 本地計算。

執行指令矩陣：
  python scripts/screen_cross_industry_peers.py --selftest
  python scripts/screen_cross_industry_peers.py --anchor 4166
  python scripts/screen_cross_industry_peers.py --anchor 4166 --top 12 --out reports/tmp_4166_peers.json
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import math
import ssl
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

import _bootstrap  # noqa: F401

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()
CACHE = Path("/tmp/augur_peer_screen")
BIOTECH = {"生技醫療業", "生技醫療", "22"}
MOPS_INCOME = "https://mopsov.twse.com.tw/mops/web/ajax_t163sb04"
# 綜合損益表數字單位＝千元（MOPS t163sb04／t187ap06 慣例；4166 113 年 1,222,816＝12.23 億可對上）


class Tables(HTMLParser):
    """極簡 HTML table 擷取（MOPS ajax 頁）。"""

    def __init__(self):
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._t: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._in_td = True

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_td:
            self._row.append("".join(self._cell).strip())
            self._in_td = False
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self._t.append(self._row)
            self._row = None
        elif tag == "table" and self._t is not None:
            self.tables.append(self._t)
            self._t = None

    def handle_data(self, data):
        if self._in_td:
            self._cell.append(data)


def _http(url: str, data: dict | None = None, retries: int = 4) -> bytes:
    body = urlencode(data).encode() if data else None
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Referer"] = "https://mopsov.twse.com.tw/mops/web/t163sb04"
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET/POST fail {url}: {last}")


def _cached(name: str, fetcher) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if p.exists() and p.stat().st_size > 200:
        return p.read_bytes()
    raw = fetcher()
    p.write_bytes(raw)
    return raw


def _num(x) -> float | None:
    if x is None:
        return None
    s = str(x).strip().replace(",", "").replace(" ", "")
    if s in {"", "--", "-", "NA", "n/a", "null"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_income_html(html: str) -> dict[str, dict]:
    """回 {stock_id: {rev, gp, op, ni, eps}}；只吃有「營業收入」欄的一般業表。"""
    p = Tables()
    p.feed(html)
    out: dict[str, dict] = {}
    for t in p.tables:
        if not t or "營業收入" not in t[0]:
            continue
        header = t[0]
        idx = {h: i for i, h in enumerate(header)}

        def col(*names):
            for n in names:
                if n in idx:
                    return idx[n]
            return None

        i_id = col("公司代號")
        i_rev = col("營業收入")
        i_gp = col("營業毛利（毛損）淨額", "營業毛利（毛損）")
        i_op = col("營業利益（損失）", "營業利益")
        i_ni = col("淨利（淨損）歸屬於母公司業主", "本期淨利（淨損）")
        i_eps = col("基本每股盈餘（元）")
        if i_id is None or i_rev is None:
            continue
        for row in t[1:]:
            if i_id >= len(row):
                continue
            sid = row[i_id].strip()
            if not sid.isdigit():
                continue
            out[sid] = {
                "rev": _num(row[i_rev]) if i_rev < len(row) else None,
                "gp": _num(row[i_gp]) if i_gp is not None and i_gp < len(row) else None,
                "op": _num(row[i_op]) if i_op is not None and i_op < len(row) else None,
                "ni": _num(row[i_ni]) if i_ni is not None and i_ni < len(row) else None,
                "eps": _num(row[i_eps]) if i_eps is not None and i_eps < len(row) else None,
            }
    return out


def fetch_annual_income(year_roc: int, typek: str) -> dict[str, dict]:
    key = f"inc_{typek}_{year_roc}.html"
    raw = _cached(
        key,
        lambda: _http(
            MOPS_INCOME,
            {
                "encodeURIComponent": "1",
                "step": "1",
                "firstin": "1",
                "off": "1",
                "TYPEK": typek,
                "isnew": "false",
                "year": str(year_roc),
                "season": "04",
            },
        ),
    )
    time.sleep(0.4)
    return parse_income_html(raw.decode("utf-8", "replace"))


def _csv_url(url: str, name: str) -> list[dict]:
    raw = _cached(name, lambda: _http(url)).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))


def load_company_map() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for mkt, url, listed_key in [
        ("twse", "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv", "上市日期"),
        ("tpex", "https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv", "上櫃日期"),
    ]:
        for r in _csv_url(url, f"co_{mkt}.csv"):
            sid = r.get("公司代號", "").strip()
            if not sid:
                continue
            shares = _num(r.get("已發行普通股數或TDR原股發行股數"))
            cap = _num(r.get("實收資本額"))
            out[sid] = {
                "name": r.get("公司簡稱") or r.get("公司名稱"),
                "industry_code": str(r.get("產業別", "")).strip(),
                "listed": (r.get(listed_key) or "").strip(),
                "shares": shares,
                "capital": cap,
                "mkt": mkt,
            }
    for mkt, url in [
        ("twse", "https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv"),
        ("tpex", "https://mopsfin.twse.com.tw/opendata/t187ap05_O.csv"),
    ]:
        for r in _csv_url(url, f"rev_{mkt}.csv"):
            sid = r.get("公司代號", "").strip()
            if sid in out:
                out[sid]["industry"] = r.get("產業別", "")
                out[sid]["mrev"] = _num(r.get("營業收入-當月營收"))
                out[sid]["mrev_yoy"] = _num(r.get("營業收入-去年同月增減(%)"))
                out[sid]["ytd"] = _num(r.get("累計營業收入-當月累計營收"))
                out[sid]["ytd_yoy"] = _num(r.get("累計營業收入-前期比較增減(%)"))
    return out


def load_latest_bs() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for mkt, url in [
        ("twse", "https://mopsfin.twse.com.tw/opendata/t187ap07_L_ci.csv"),
        ("tpex", "https://mopsfin.twse.com.tw/opendata/t187ap07_O_ci.csv"),
    ]:
        for r in _csv_url(url, f"bs_{mkt}.csv"):
            sid = r.get("公司代號", "").strip()
            ta, tl = _num(r.get("資產總計")), _num(r.get("負債總計"))
            ca, cl = _num(r.get("流動資產")), _num(r.get("流動負債"))
            eq = _num(r.get("權益總計"))
            bps = _num(r.get("每股參考淨值"))
            out[sid] = {
                "ta": ta,
                "tl": tl,
                "ca": ca,
                "cl": cl,
                "eq": eq,
                "bps": bps,
                "debt_ratio": (tl / ta) if ta and tl is not None and ta else None,
                "current_ratio": (ca / cl) if ca and cl else None,
            }
    return out


def load_latest_income_h1() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for mkt, url in [
        ("twse", "https://mopsfin.twse.com.tw/opendata/t187ap06_L_ci.csv"),
        ("tpex", "https://mopsfin.twse.com.tw/opendata/t187ap06_O_ci.csv"),
    ]:
        for r in _csv_url(url, f"h1_{mkt}.csv"):
            sid = r.get("公司代號", "").strip()
            rev, gp, op, ni = (
                _num(r.get("營業收入")),
                _num(r.get("營業毛利（毛損）")),
                _num(r.get("營業利益（損失）")),
                _num(r.get("本期淨利（淨損）")),
            )
            out[sid] = {
                "rev": rev,
                "gp": gp,
                "op": op,
                "ni": ni,
                "eps": _num(r.get("基本每股盈餘（元）")),
                "gm": (gp / rev) if rev and gp is not None and rev else None,
                "opm": (op / rev) if rev and op is not None and rev else None,
                "npm": (ni / rev) if rev and ni is not None and rev else None,
            }
    return out


def load_prices() -> dict[str, dict]:
    out: dict[str, dict] = {}
    raw = _cached(
        "twse_day.csv",
        lambda: _http("https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=csv"),
    )
    text = raw.decode("utf-8-sig", "replace")
    # 檔頭可能有日期列
    lines = [ln for ln in text.splitlines() if ln.count(",") >= 6]
    rdr = csv.reader(io.StringIO("\n".join(lines)))
    rows = list(rdr)
    if rows:
        header = [h.strip().strip('"') for h in rows[0]]
        for row in rows[1:]:
            if len(row) < 8:
                continue
            rec = {header[i]: row[i].strip().strip('"') for i in range(min(len(header), len(row)))}
            sid = rec.get("證券代號") or rec.get("代號") or row[0].strip().strip('"')
            px = _num(rec.get("收盤價") or (row[8] if len(row) > 8 else None))
            vol = _num(rec.get("成交股數") or row[2] if len(row) > 2 else None)
            if sid and px:
                out[sid] = {"close": px, "volume": vol, "src": "twse"}
    # 櫃買
    js = json.loads(
        _cached(
            "tpex_day.json",
            lambda: _http(
                "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/"
                "stk_quote_result.php?l=zh-tw&o=json"
            ),
        )
    )
    tables = js.get("tables") or []
    data = tables[0].get("data") if tables else []
    fields = tables[0].get("fields") if tables else []
    for row in data or []:
        rec = {fields[i]: row[i] for i in range(min(len(fields), len(row)))} if fields else {}
        sid = str(rec.get("證券代號") or rec.get("代號") or (row[0] if row else "")).strip()
        px = _num(rec.get("收盤") or rec.get("收盤價") or (row[2] if len(row) > 2 else None))
        vol = _num(rec.get("成交股數") or rec.get("成交量") or (row[7] if len(row) > 7 else None))
        if sid and px:
            out[sid] = {"close": px, "volume": vol, "src": "tpex"}
    return out


def load_pe_pb() -> dict[str, dict]:
    out: dict[str, dict] = {}
    js = json.loads(
        _cached(
            "twse_pe.json",
            lambda: _http(
                "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?response=json&date=20260826"
            ),
        )
    )
    fields, data = js.get("fields") or [], js.get("data") or []
    for row in data:
        rec = {fields[i]: row[i] for i in range(min(len(fields), len(row)))}
        sid = str(rec.get("證券代號", "")).strip()
        if sid:
            out[sid] = {"pe": _num(rec.get("本益比")), "pb": _num(rec.get("股價淨值比")),
                        "yield": _num(rec.get("殖利率(%)"))}
    js = json.loads(
        _cached(
            "tpex_pe.json",
            lambda: _http(
                "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/"
                "pera_result.php?l=zh-tw&o=json"
            ),
        )
    )
    tables = js.get("tables") or []
    data = tables[0].get("data") if tables else js.get("aaData") or []
    fields = tables[0].get("fields") if tables else []
    for row in data or []:
        rec = {fields[i]: row[i] for i in range(min(len(fields), len(row)))} if fields else {}
        sid = str(rec.get("股票代號") or rec.get("證券代號") or (row[0] if row else "")).strip()
        if not sid:
            continue
        pe = _num(rec.get("本益比") or (row[2] if len(row) > 2 else None))
        pb = _num(rec.get("每股淨值") and None)
        # 櫃買欄位常見：代號、名稱、本益比、每股股利、殖利率、股價淨值比
        if fields:
            for k, v in rec.items():
                if "本益" in k:
                    pe = _num(v)
                if "淨值比" in k:
                    pb = _num(v)
        else:
            pe = _num(row[2]) if len(row) > 2 else pe
            pb = _num(row[5]) if len(row) > 5 else pb
        out[sid] = {"pe": pe, "pb": pb}
    return out


def yahoo_chart(symbol: str, listed: str | None = None) -> dict | None:
    """近一年日線；若上櫃日在窗內，只計掛牌後（避開興櫃高點污染 52w）。"""
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range=1y&interval=1d&events=div%7Csplit"
    )
    key = f"chart1y_{symbol.replace('.', '_')}.json"
    try:
        raw = _cached(key, lambda: _http(url))
        time.sleep(0.15)
        d = json.loads(raw)
        res = (d.get("chart") or {}).get("result") or []
        if not res:
            return None
        r0 = res[0]
        meta = r0.get("meta") or {}
        ts = r0.get("timestamp") or []
        closes = ((r0.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
        pairs = [(t, c) for t, c in zip(ts, closes) if c is not None]
        if not pairs:
            return None
        listed_ts = None
        if listed and len(str(listed)) == 8 and str(listed).isdigit():
            d0 = datetime.datetime.strptime(str(listed), "%Y%m%d").replace(
                tzinfo=datetime.timezone(datetime.timedelta(hours=8))
            )
            listed_ts = int(d0.timestamp())
            post = [(t, c) for t, c in pairs if t >= listed_ts]
            if len(post) >= 20:
                pairs = post
        return {
            "last": pairs[-1][1],
            "first": pairs[0][1],
            "high": max(c for _, c in pairs),
            "low": min(c for _, c in pairs),
            "n": len(pairs),
            "ret_1y": pairs[-1][1] / pairs[0][1] - 1 if pairs[0][1] else None,
            "from_high": pairs[-1][1] / max(c for _, c in pairs) - 1,
            "from_low": pairs[-1][1] / min(c for _, c in pairs) - 1,
            "currency": meta.get("currency"),
            "listed_clipped": bool(listed_ts and pairs[0][0] >= listed_ts - 86400),
        }
    except Exception:
        return None


def _ratio(a, b):
    if a is None or not b:
        return None
    return a / b


def _cagr(start, end, years):
    if not start or start <= 0 or not end or end <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def _yoy(cur, prev):
    if cur is None or not prev:
        return None
    return cur / prev - 1


def build_panel(years: dict[int, dict[str, dict]], cos: dict, bs: dict, h1: dict,
                px: dict, pepb: dict) -> dict[str, dict]:
    sids = set()
    for ymap in years.values():
        sids |= set(ymap)
    panel = {}
    for sid in sids:
        co = cos.get(sid) or {}
        y = {yy: (years[yy].get(sid) or {}) for yy in sorted(years)}
        rev = {yy: y[yy].get("rev") for yy in y}
        gm = {yy: _ratio(y[yy].get("gp"), y[yy].get("rev")) for yy in y}
        opm = {yy: _ratio(y[yy].get("op"), y[yy].get("rev")) for yy in y}
        npm = {yy: _ratio(y[yy].get("ni"), y[yy].get("rev")) for yy in y}
        r21, r22, r23, r24, r25 = [rev.get(k) for k in (2021, 2022, 2023, 2024, 2025)]
        first_profit = None
        for yy in (2021, 2022, 2023, 2024, 2025):
            ni = y[yy].get("ni")
            if ni is not None and ni > 0 and first_profit is None:
                first_profit = yy
        b = bs.get(sid) or {}
        price = (px.get(sid) or {}).get("close")
        shares = co.get("shares")
        mktcap = (price * shares) if price and shares else None  # 元
        rec = {
            "sid": sid,
            "name": co.get("name"),
            "industry": co.get("industry") or co.get("industry_code"),
            "mkt": co.get("mkt"),
            "listed": co.get("listed"),
            "rev": rev,
            "gm": gm,
            "opm": opm,
            "npm": npm,
            "eps": {yy: y[yy].get("eps") for yy in y},
            "ni": {yy: y[yy].get("ni") for yy in y},
            "cagr_21_25": _cagr(r21, r25, 4),
            "yoy23": _yoy(r23, r22),
            "yoy24": _yoy(r24, r23),
            "yoy25": _yoy(r25, r24),
            "gm_delta": (gm.get(2025) - gm.get(2021)) if gm.get(2025) is not None and gm.get(2021) is not None else None,
            "opm_delta": (opm.get(2025) - opm.get(2021)) if opm.get(2025) is not None and opm.get(2021) is not None else None,
            "first_profit": first_profit,
            "loss_then_profit": bool(
                (y[2021].get("ni") is not None and y[2021].get("ni") < 0)
                or (y[2022].get("ni") is not None and y[2022].get("ni") < 0)
            ) and bool(y[2025].get("ni") is not None and y[2025].get("ni") > 0),
            "debt_ratio": b.get("debt_ratio"),
            "current_ratio": b.get("current_ratio"),
            "bps": b.get("bps"),
            "h1": h1.get(sid) or {},
            "close": price,
            "volume": (px.get(sid) or {}).get("volume"),
            "mktcap": mktcap,
            "pe": (pepb.get(sid) or {}).get("pe"),
            "pb": (pepb.get(sid) or {}).get("pb"),
            "ytd_yoy": co.get("ytd_yoy"),
        }
        if rec["pb"] is None and price and b.get("bps"):
            rec["pb"] = price / b["bps"]
        panel[sid] = rec
    return panel


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _gauss(x, target, scale) -> float:
    if x is None or target is None or not scale:
        return 0.0
    return math.exp(-((x - target) ** 2) / (2 * scale * scale))


def financial_score(row: dict, anc: dict) -> tuple[float, dict]:
    """路徑分數 0–100。缺件不給滿分、不捏造。"""
    parts = {}
    # 規模：2025 營收（千元）對錨
    parts["scale"] = _gauss(
        math.log((row["rev"].get(2025) or 0) or 1e-9),
        math.log((anc["rev"].get(2025) or 0) or 1e-9),
        0.85,
    )
    parts["cagr"] = _gauss(row.get("cagr_21_25"), anc.get("cagr_21_25"), 0.12)
    # 減速：23 高 → 24 中 → 25 低雙位數
    decel = 0.0
    if row.get("yoy23") and row.get("yoy24") is not None and row.get("yoy25") is not None:
        if row["yoy23"] > row["yoy24"] > 0 and row["yoy25"] < row["yoy24"]:
            decel += 0.55
        decel += 0.45 * _gauss(row["yoy25"], anc.get("yoy25"), 0.12)
    parts["decel"] = _clip01(decel)
    parts["gm_now"] = _gauss(row["gm"].get(2025), anc["gm"].get(2025), 0.10)
    parts["gm_jump"] = _gauss(row.get("gm_delta"), anc.get("gm_delta"), 0.10)
    parts["opm_now"] = _gauss(row["opm"].get(2025), anc["opm"].get(2025), 0.08)
    parts["opm_jump"] = _gauss(row.get("opm_delta"), anc.get("opm_delta"), 0.15)
    # 轉盈窗
    fp, afp = row.get("first_profit"), anc.get("first_profit")
    parts["inflect"] = 1.0 if row.get("loss_then_profit") and fp in {2022, 2023, 2024} else (
        0.55 if fp and afp and abs(fp - afp) <= 1 else 0.15 if (row["ni"].get(2025) or 0) > 0 else 0.0
    )
    parts["lev"] = _gauss(row.get("debt_ratio"), anc.get("debt_ratio"), 0.12)
    parts["liq"] = _gauss(
        math.log((row.get("current_ratio") or 0) + 1e-6),
        math.log((anc.get("current_ratio") or 0) + 1e-6),
        0.7,
    )
    w = {
        "scale": 0.08, "cagr": 0.14, "decel": 0.14, "gm_now": 0.09, "gm_jump": 0.14,
        "opm_now": 0.09, "opm_jump": 0.10, "inflect": 0.14, "lev": 0.05, "liq": 0.03,
    }
    s = 100.0 * sum(w[k] * parts.get(k, 0.0) for k in w)
    return s, parts


def price_score(chart: dict | None, anc_chart: dict | None, row: dict, anc: dict) -> tuple[float, dict]:
    parts = {}
    if not chart or not anc_chart:
        return 0.0, {"missing": 1.0}
    parts["from_high"] = _gauss(chart.get("from_high"), anc_chart.get("from_high"), 0.12)
    parts["ret"] = _gauss(chart.get("ret_1y"), anc_chart.get("ret_1y"), 0.22)
    # 評價
    parts["pb"] = _gauss(row.get("pb"), anc.get("pb"), 0.8)
    pe_a, pe_b = row.get("pe"), anc.get("pe")
    if pe_a and pe_a > 0 and pe_b and pe_b > 0:
        parts["pe"] = _gauss(math.log(pe_a), math.log(pe_b), 0.45)
    else:
        parts["pe"] = 0.25
    # 市值
    if row.get("mktcap") and anc.get("mktcap"):
        parts["mcap"] = _gauss(math.log(row["mktcap"]), math.log(anc["mktcap"]), 0.9)
    else:
        parts["mcap"] = 0.3
    w = {"from_high": 0.28, "ret": 0.22, "pb": 0.18, "pe": 0.16, "mcap": 0.16}
    s = 100.0 * sum(w[k] * parts.get(k, 0.0) for k in w)
    return s, parts


def passes_hard_filter(row: dict, anc: dict) -> tuple[bool, str]:
    ind = (row.get("industry") or "")
    if ind in BIOTECH or "生技" in ind or "醫療" in ind:
        return False, "same_or_bio_industry"
    r25 = row["rev"].get(2025)
    a25 = anc["rev"].get(2025)
    if not r25 or r25 <= 0 or not a25:
        return False, "no_2025_rev"
    # 規模帶：錨的 0.35x–3.5x（友霖 14 億 → 約 5–49 億）
    if r25 < 0.35 * a25 or r25 > 3.5 * a25:
        return False, "scale"
    if (row["ni"].get(2025) or -1) <= 0:
        return False, "not_profitable_2025"
    gm = row["gm"].get(2025)
    if gm is None or gm < 0.38:
        return False, "gm_lt_38"
    cagr = row.get("cagr_21_25")
    if cagr is None or cagr < 0.10:
        return False, "cagr_lt_10"
    dr = row.get("debt_ratio")
    if dr is not None and dr > 0.42:
        return False, "high_debt"
    if row.get("mktcap") and anc.get("mktcap"):
        if row["mktcap"] > 5.0 * anc["mktcap"] or row["mktcap"] < 0.18 * anc["mktcap"]:
            return False, "mktcap"
    y23, y24, y25 = row.get("yoy23"), row.get("yoy24"), row.get("yoy25")
    if y25 is not None and y25 < -0.25:
        return False, "rev_collapse"
    path_hits = 0
    if row.get("loss_then_profit") or (row.get("first_profit") in {2022, 2023, 2024}):
        path_hits += 1
    if (row.get("gm_delta") or 0) >= 0.08:
        path_hits += 1
    if (row.get("opm_delta") or 0) >= 0.10:
        path_hits += 1
    if y23 and y24 is not None and y25 is not None and y23 > 0.35 and y24 < y23 and 0.05 <= y25 <= 0.35:
        path_hits += 1
    snapshot_like = (
        (gm or 0) >= 0.48
        and 0.10 <= (cagr or 0) <= 0.50
        and y25 is not None and 0.05 <= y25 <= 0.30
    )
    if path_hits < 1 and not snapshot_like:
        return False, "no_path"
    row["_path_hits"] = path_hits
    row["_snapshot_like"] = bool(snapshot_like)
    return True, "ok"


def yahoo_symbol(sid: str, mkt: str | None) -> str:
    if mkt == "twse":
        return f"{sid}.TW"
    return f"{sid}.TWO"


def run_screen(anchor: str, top_n: int) -> dict:
    roc_years = {2021: 110, 2022: 111, 2023: 112, 2024: 113, 2025: 114}
    years: dict[int, dict[str, dict]] = {y: {} for y in roc_years}
    print("fetch annual income 2021-2025 sii+otc …", flush=True)
    for y, roc in roc_years.items():
        merged: dict[str, dict] = {}
        for typek in ("sii", "otc"):
            got = fetch_annual_income(roc, typek)
            merged.update(got)
            print(f"  {y} {typek} n={len(got)}", flush=True)
        years[y] = merged
        if anchor not in merged:
            print(f"  WARN {anchor} missing in {y}", flush=True)
    print("fetch company / BS / H1 / prices / PE …", flush=True)
    cos, bs, h1, px, pepb = (
        load_company_map(), load_latest_bs(), load_latest_income_h1(),
        load_prices(), load_pe_pb(),
    )
    panel = build_panel(years, cos, bs, h1, px, pepb)
    if anchor not in panel:
        raise SystemExit(f"anchor {anchor} not in panel")
    anc = panel[anchor]
    print(
        f"anchor {anchor} {anc.get('name')} ind={anc.get('industry')} "
        f"rev25={anc['rev'].get(2025)} cagr={anc.get('cagr_21_25')} "
        f"gm25={anc['gm'].get(2025)} opm25={anc['opm'].get(2025)} "
        f"debt={anc.get('debt_ratio')} close={anc.get('close')} "
        f"mktcap={anc.get('mktcap')} pe={anc.get('pe')} pb={anc.get('pb')}",
        flush=True,
    )
    cands = []
    reasons: dict[str, int] = {}
    for sid, row in panel.items():
        if sid == anchor:
            continue
        ok, why = passes_hard_filter(row, anc)
        reasons[why] = reasons.get(why, 0) + 1
        if not ok:
            continue
        fs, fp = financial_score(row, anc)
        cands.append((fs, sid, fp))
    cands.sort(reverse=True)
    print("hard-filter reasons", reasons, "pass", len(cands), flush=True)
    # 價量：財務前 40 名拉 Yahoo 2y
    take = cands[: max(top_n * 4, 40)]
    print(f"yahoo charts for top {len(take)} + anchor …", flush=True)
    anc_sym = yahoo_symbol(anchor, anc.get("mkt"))
    anc_chart = yahoo_chart(anc_sym, anc.get("listed"))
    ranked = []
    for fs, sid, fp in take:
        row = panel[sid]
        ch = yahoo_chart(yahoo_symbol(sid, row.get("mkt")), row.get("listed"))
        ps, pp = price_score(ch, anc_chart, row, anc)
        combo = 0.70 * fs + 0.30 * ps
        ranked.append(
            {
                "sid": sid,
                "name": row.get("name"),
                "industry": row.get("industry"),
                "mkt": row.get("mkt"),
                "listed": row.get("listed"),
                "fin_score": round(fs, 2),
                "px_score": round(ps, 2),
                "combo": round(combo, 2),
                "fin_parts": {k: round(v, 3) for k, v in fp.items()},
                "px_parts": {k: round(v, 3) for k, v in pp.items()},
                "rev_yi": {str(y): (None if row["rev"].get(y) is None else round(row["rev"][y] / 1e5, 3))
                           for y in (2021, 2022, 2023, 2024, 2025)},
                "yoy": {k: (None if row.get(k) is None else round(row[k], 4))
                        for k in ("cagr_21_25", "yoy23", "yoy24", "yoy25")},
                "gm": {str(y): (None if row["gm"].get(y) is None else round(row["gm"][y], 4))
                       for y in (2021, 2025)},
                "gm_delta": None if row.get("gm_delta") is None else round(row["gm_delta"], 4),
                "opm": {str(y): (None if row["opm"].get(y) is None else round(row["opm"][y], 4))
                        for y in (2021, 2025)},
                "npm_2025": None if row["npm"].get(2025) is None else round(row["npm"][2025], 4),
                "ni_yi": {str(y): (None if row["ni"].get(y) is None else round(row["ni"][y] / 1e5, 3))
                          for y in (2021, 2022, 2023, 2024, 2025)},
                "first_profit": row.get("first_profit"),
                "loss_then_profit": row.get("loss_then_profit"),
                "debt_ratio": None if row.get("debt_ratio") is None else round(row["debt_ratio"], 4),
                "current_ratio": None if row.get("current_ratio") is None else round(row["current_ratio"], 3),
                "close": row.get("close"),
                "mktcap_yi": None if row.get("mktcap") is None else round(row["mktcap"] / 1e8, 2),
                "pe": row.get("pe"),
                "pb": None if row.get("pb") is None else round(row["pb"], 3),
                "ytd_yoy": row.get("ytd_yoy"),
                "path_hits": row.get("_path_hits"),
                "snapshot_like": row.get("_snapshot_like"),
                "h1_gm": (row.get("h1") or {}).get("gm"),
                "h1_opm": (row.get("h1") or {}).get("opm"),
                "chart": None if not ch else {
                    "last": ch["last"], "high": ch["high"], "low": ch["low"],
                    "from_high": round(ch["from_high"], 4),
                    "from_low": round(ch["from_low"], 4),
                    "ret_1y": None if ch.get("ret_1y") is None else round(ch["ret_1y"], 4),
                    "listed_clipped": ch.get("listed_clipped"),
                    "n": ch["n"],
                },
            }
        )
    ranked.sort(key=lambda r: -r["combo"])
    anc_out = {
        "sid": anchor,
        "name": anc.get("name"),
        "industry": anc.get("industry"),
        "listed": anc.get("listed"),
        "rev_yi": {str(y): (None if anc["rev"].get(y) is None else round(anc["rev"][y] / 1e5, 3))
                   for y in (2021, 2022, 2023, 2024, 2025)},
        "yoy": {k: (None if anc.get(k) is None else round(anc[k], 4))
                for k in ("cagr_21_25", "yoy23", "yoy24", "yoy25")},
        "gm": {str(y): (None if anc["gm"].get(y) is None else round(anc["gm"][y], 4))
               for y in (2021, 2025)},
        "gm_delta": None if anc.get("gm_delta") is None else round(anc["gm_delta"], 4),
        "opm": {str(y): (None if anc["opm"].get(y) is None else round(anc["opm"][y], 4))
                for y in (2021, 2025)},
        "npm_2025": None if anc["npm"].get(2025) is None else round(anc["npm"][2025], 4),
        "ni_yi": {str(y): (None if anc["ni"].get(y) is None else round(anc["ni"][y] / 1e5, 3))
                  for y in (2021, 2022, 2023, 2024, 2025)},
        "first_profit": anc.get("first_profit"),
        "debt_ratio": None if anc.get("debt_ratio") is None else round(anc["debt_ratio"], 4),
        "current_ratio": None if anc.get("current_ratio") is None else round(anc["current_ratio"], 3),
        "close": anc.get("close"),
        "mktcap_yi": None if anc.get("mktcap") is None else round(anc["mktcap"] / 1e8, 2),
        "pe": anc.get("pe"),
        "pb": None if anc.get("pb") is None else round(anc["pb"], 3),
        "ytd_yoy": anc.get("ytd_yoy"),
        "chart": None if not anc_chart else {
            "last": anc_chart["last"], "high": anc_chart["high"], "low": anc_chart["low"],
            "from_high": round(anc_chart["from_high"], 4),
            "from_low": round(anc_chart["from_low"], 4),
            "ret_1y": None if anc_chart.get("ret_1y") is None else round(anc_chart["ret_1y"], 4),
            "listed_clipped": anc_chart.get("listed_clipped"),
            "n": anc_chart["n"],
        },
    }
    return {
        "asof": "2026-08-27",
        "source": "MOPS t163sb04 年報／t187ap06-07 2026Q2／TWSE+TPEx 收盤與本益比／Yahoo chart 1y（上櫃後裁切）",
        "anchor": anc_out,
        "filter_reasons": reasons,
        "n_pass_financial": len(cands),
        "ranked": ranked[:top_n],
        "ranked_all_head": ranked[:40],
    }


def _selftest() -> int:
    html = """
    <table><tr><td>公司代號</td><td>公司名稱</td><td>營業收入</td><td>營業毛利（毛損）淨額</td>
    <td>營業利益（損失）</td><td>淨利（淨損）歸屬於母公司業主</td><td>基本每股盈餘（元）</td></tr>
    <tr><td>4166</td><td>友霖</td><td>1,400,000</td><td>790,000</td><td>260,000</td><td>208,000</td><td>0.90</td></tr>
    </table>
    """
    got = parse_income_html(html)
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("parse 4166 rev", got.get("4166", {}).get("rev") == 1400000)
    chk("parse gm pieces", got["4166"]["gp"] == 790000)
    anc = {
        "rev": {2021: 463000, 2025: 1400000},
        "gm": {2021: 0.307, 2025: 0.564},
        "opm": {2021: -0.289, 2025: 0.186},
        "ni": {2021: -103000, 2025: 208000},
        "cagr_21_25": 0.319,
        "yoy23": 0.738, "yoy24": 0.374, "yoy25": 0.145,
        "gm_delta": 0.257, "opm_delta": 0.475, "first_profit": 2023,
        "loss_then_profit": True, "debt_ratio": 0.118, "current_ratio": 7.39,
        "industry": "電機機械", "mktcap": 6e9, "pe": 25, "pb": 2.26,
        "npm": {2025: 0.149},
    }
    twin = {
        "rev": {2021: 500000, 2022: 560000, 2023: 950000, 2024: 1280000, 2025: 1480000},
        "gm": {2021: 0.31, 2025: 0.55}, "opm": {2021: -0.20, 2025: 0.17},
        "ni": {2021: -80000, 2022: -20000, 2023: 30000, 2024: 110000, 2025: 200000},
        "npm": {2025: 0.135},
        "cagr_21_25": _cagr(500000, 1480000, 4),
        "yoy23": 0.70, "yoy24": 0.35, "yoy25": 0.16,
        "gm_delta": 0.24, "opm_delta": 0.37, "first_profit": 2023,
        "loss_then_profit": True, "debt_ratio": 0.15, "current_ratio": 5.0,
        "industry": "電機機械", "mktcap": 7e9, "pe": 22, "pb": 2.1,
    }
    far = {
        "rev": {2021: 50000000, 2025: 52000000},
        "gm": {2021: 0.08, 2025: 0.09}, "opm": {2021: 0.03, 2025: 0.04},
        "ni": {2021: 1000000, 2025: 1100000}, "npm": {2025: 0.02},
        "cagr_21_25": 0.01, "yoy23": 0.02, "yoy24": 0.01, "yoy25": 0.0,
        "gm_delta": 0.01, "opm_delta": 0.01, "first_profit": 2010,
        "loss_then_profit": False, "debt_ratio": 0.55, "current_ratio": 1.1,
        "industry": "水泥工業", "mktcap": 2e11, "pe": 8, "pb": 0.8,
    }
    s1, _ = financial_score(twin, anc)
    s2, _ = financial_score(far, anc)
    chk("twin scores higher than far", s1 > s2 + 20)
    ok_t, _ = passes_hard_filter(twin, anc)
    ok_f, why = passes_hard_filter(far, anc)
    chk("twin passes", ok_t)
    chk("far rejected", (not ok_f) and why in {
        "scale", "gm_lt_38", "cagr_lt_10", "high_debt", "no_path", "mktcap", "rev_collapse"
    })
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--anchor", default="4166")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(_selftest())
    result = run_screen(args.anchor, args.top)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("wrote", args.out, file=sys.stderr)


if __name__ == "__main__":
    main()
