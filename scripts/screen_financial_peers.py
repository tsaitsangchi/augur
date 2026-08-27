#!/usr/bin/env python3
"""庫外公開源：以 9930 中聯資源財務輪廓篩選台股電子業近似個股。

🎯 這支在做什麼（白話）：從證交所／櫃買／公開資訊觀測站公開資料抓上市櫃
損益、資產負債、本益／殖利率與年底收盤，用與 9930 相同的財務／成長／評價
向量算距離，列出電子產業近似股。不打 FinMind／FRED。數字只來自 HTTP 回應。

守 #1 #9 #10 #18 #29；API 凍結下走官方公開源。

執行指令矩陣：
  python scripts/screen_financial_peers.py              # 印用途＋公開入口
  python scripts/screen_financial_peers.py --selftest   # 純紅綠自測（零網路）
  python scripts/screen_financial_peers.py --run        # 抓公開源並印排名（需網路）
  python scripts/screen_financial_peers.py --run --json-out reports/data/9930_electronics_peers.json
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import math
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import _bootstrap  # noqa: F401

UA = "Mozilla/5.0 (compatible; augur-research/1.0; +https://github.com/tsaitsangchi/augur)"
CTX = ssl.create_default_context()
CACHE = Path(os.environ.get("AUGUR_PEER_CACHE", "/tmp/9930_peers_cache"))
ELECTRONICS = {
    "半導體業",
    "電腦及週邊設備業",
    "光電業",
    "通信網路業",
    "電子零組件業",
    "電子通路業",
    "資訊服務業",
    "其他電子業",
}
# 9930 錨點（MOPS 年報／證交所；單位：營收千元、EPS 元）— 執行時由資料覆寫
ANCHOR_ID = "9930"


def _sleep():
    time.sleep(0.35)


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def http_post(url: str, data: dict, referer: str, timeout: int = 90) -> bytes:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": referer,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def cached_get(name: str, url: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if p.exists() and p.stat().st_size > 200:
        return p.read_bytes()
    last = None
    for i in range(4):
        try:
            raw = http_get(url)
            p.write_bytes(raw)
            _sleep()
            return raw
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last = e
            time.sleep(2 ** i)
    raise RuntimeError(f"GET failed {url}: {last}")


def cached_post(name: str, url: str, data: dict, referer: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if p.exists() and p.stat().st_size > 200:
        return p.read_bytes()
    last = None
    for i in range(4):
        try:
            raw = http_post(url, data, referer)
            p.write_bytes(raw)
            _sleep()
            return raw
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last = e
            time.sleep(2 ** i)
    raise RuntimeError(f"POST failed {url}: {last}")


def fnum(x) -> float | None:
    if x is None:
        return None
    s = str(x).strip().replace(",", "").replace(" ", "")
    if s in {"", "--", "-", "NA", "n/a", "null", "None"}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if not math.isfinite(v):
        return None
    return v


def cagr(start: float, end: float, years: int) -> float | None:
    if start is None or end is None or years <= 0:
        return None
    if start == 0:
        return None
    if start < 0 or end < 0:
        return None
    return (end / start) ** (1.0 / years) - 1.0


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table = None
        self._row = None
        self._cell = None
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t == "table":
            self._table = []
        elif t == "tr" and self._table is not None:
            self._row = []
        elif t in {"td", "th"} and self._row is not None:
            self._cell = []
            self._in_cell = True

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in {"td", "th"} and self._in_cell:
            txt = htmlmod.unescape("".join(self._cell))
            txt = re.sub(r"\s+", " ", txt).strip()
            self._row.append(txt)
            self._in_cell = False
            self._cell = None
        elif t == "tr" and self._row is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif t == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if self._in_cell:
            self._cell.append(data)


def parse_mops_income(html: str) -> dict[str, dict]:
    """一般業綜合損益：key=stock_id。金額維持 MOPS 千元。"""
    p = _TableParser()
    p.feed(html)
    out: dict[str, dict] = {}
    for tbl in p.tables:
        if len(tbl) < 2:
            continue
        header = tbl[0]
        joined = " ".join(header)
        if "營業收入" not in joined or "營業利益" not in joined:
            continue
        idx = {h: i for i, h in enumerate(header)}

        def col(*names):
            for n in names:
                if n in idx:
                    return idx[n]
            for n in names:
                for h, i in idx.items():
                    if n in h:
                        return i
            return None

        i_id = col("公司代號")
        i_name = col("公司名稱")
        i_rev = col("營業收入")
        i_cogs = col("營業成本")
        i_gp = col("營業毛利（毛損）淨額", "營業毛利（毛損）", "營業毛利")
        i_oi = col("營業利益（損失）", "營業利益")
        i_ni = col("淨利（淨損）歸屬於母公司業主", "淨利（損）歸屬於母公司業主")
        i_eps = col("基本每股盈餘")
        if i_id is None or i_rev is None:
            continue
        for row in tbl[1:]:
            if len(row) <= i_id:
                continue
            sid = row[i_id].strip()
            if not re.fullmatch(r"\d{4}", sid):
                continue

            def g(i):
                return fnum(row[i]) if i is not None and i < len(row) else None

            out[sid] = {
                "stock_id": sid,
                "name": row[i_name].strip() if i_name is not None and i_name < len(row) else "",
                "revenue": g(i_rev),
                "cogs": g(i_cogs),
                "gross_profit": g(i_gp),
                "op_income": g(i_oi),
                "ni_parent": g(i_ni),
                "eps": g(i_eps),
            }
    return out


def parse_mops_balance(html: str) -> dict[str, dict]:
    p = _TableParser()
    p.feed(html)
    out: dict[str, dict] = {}
    for tbl in p.tables:
        if len(tbl) < 2:
            continue
        header = tbl[0]
        joined = " ".join(header)
        if "資產總計" not in joined or "負債總計" not in joined:
            continue
        idx = {h: i for i, h in enumerate(header)}

        def col(*names):
            for n in names:
                if n in idx:
                    return idx[n]
            for n in names:
                for h, i in idx.items():
                    if n in h:
                        return i
            return None

        i_id = col("公司代號")
        i_name = col("公司名稱")
        i_ast = col("資產總計", "資產總額")
        i_lia = col("負債總計", "負債總額")
        i_eq = col("權益總計", "權益總額")
        i_peq = col("歸屬於母公司業主之權益合計", "歸屬於母公司業主之權益")
        i_bv = col("每股參考淨值")
        if i_id is None or i_ast is None:
            continue
        for row in tbl[1:]:
            if len(row) <= i_id:
                continue
            sid = row[i_id].strip()
            if not re.fullmatch(r"\d{4}", sid):
                continue

            def g(i):
                return fnum(row[i]) if i is not None and i < len(row) else None

            out[sid] = {
                "stock_id": sid,
                "name": row[i_name].strip() if i_name is not None and i_name < len(row) else "",
                "assets": g(i_ast),
                "liab": g(i_lia),
                "equity": g(i_eq),
                "parent_eq": g(i_peq),
                "bvps": g(i_bv),
            }
    return out


def mops_payload(year_roc: str, season: str, typek: str) -> dict:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": typek,
        "year": year_roc,
        "season": season,
    }


def fetch_mops_is(year_roc: str, season: str, typek: str) -> dict[str, dict]:
    url = "https://mopsov.twse.com.tw/mops/web/ajax_t163sb04"
    name = f"is_{typek}_{year_roc}_{season}.html"
    raw = cached_post(name, url, mops_payload(year_roc, season, typek), url.replace("ajax_", ""))
    return parse_mops_income(raw.decode("utf-8", "replace"))


def fetch_mops_bs(year_roc: str, season: str, typek: str) -> dict[str, dict]:
    url = "https://mopsov.twse.com.tw/mops/web/ajax_t163sb05"
    name = f"bs_{typek}_{year_roc}_{season}.html"
    raw = cached_post(name, url, mops_payload(year_roc, season, typek), url.replace("ajax_", ""))
    return parse_mops_balance(raw.decode("utf-8", "replace"))


def load_json(url: str, cache_name: str):
    raw = cached_get(cache_name, url)
    return json.loads(raw.decode("utf-8"))


def listed_profiles() -> dict[str, dict]:
    arr = load_json("https://openapi.twse.com.tw/v1/opendata/t187ap03_L", "twse_profile.json")
    out = {}
    for x in arr:
        sid = str(x.get("公司代號", "")).strip()
        out[sid] = {
            "name": x.get("公司簡稱") or x.get("公司名稱"),
            "industry_code": str(x.get("產業別", "")).strip(),
            "market": "TWSE",
            "shares": fnum(x.get("已發行普通股數或TDR原股發行股數")),
            "capital": fnum(x.get("實收資本額")),
        }
    return out


def otc_profiles() -> dict[str, dict]:
    # 櫃買 OpenAPI 公司基本資料
    urls = [
        "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O",
        "https://www.tpex.org.tw/openapi/v1/tpex_listed_company_basic_info",
    ]
    arr = None
    last = None
    for i, url in enumerate(urls):
        try:
            arr = load_json(url, f"tpex_profile_{i}.json")
            if isinstance(arr, list) and arr:
                break
        except Exception as e:
            last = e
            arr = None
    if not arr:
        print(f"WARN OTC profiles unavailable: {last}", file=sys.stderr)
        return {}
    out = {}
    sample_keys = list(arr[0].keys())
    id_key = next((k for k in sample_keys if "代號" in k or k.lower() in {"code", "secid", "securitiescompanycode"}), sample_keys[0])
    name_key = next((k for k in sample_keys if "簡稱" in k or k == "公司名稱"), None)
    ind_key = next((k for k in sample_keys if "產業" in k), None)
    share_key = next((k for k in sample_keys if "發行" in k and "股" in k), None)
    for x in arr:
        sid = str(x.get(id_key, "")).strip()
        if not re.fullmatch(r"\d{4}", sid):
            continue
        out[sid] = {
            "name": x.get(name_key) if name_key else "",
            "industry_code": str(x.get(ind_key, "")).strip() if ind_key else "",
            "industry_name": str(x.get(ind_key, "")).strip() if ind_key else "",
            "market": "TPEx",
            "shares": fnum(x.get(share_key)) if share_key else None,
        }
    return out


def industry_names_listed() -> dict[str, str]:
    arr = load_json("https://openapi.twse.com.tw/v1/opendata/t187ap14_L", "twse_t187ap14.json")
    out = {}
    for x in arr:
        sid = str(x.get("公司代號", "")).strip()
        out[sid] = str(x.get("產業別", "")).strip()
    return out


def industry_names_otc() -> dict[str, str]:
    urls = [
        "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap14_O",
        "https://www.tpex.org.tw/openapi/v1/tpex_listed_company_basic_info",
    ]
    out = {}
    for i, url in enumerate(urls):
        try:
            arr = load_json(url, f"tpex_ind_{i}.json")
        except Exception:
            continue
        if not isinstance(arr, list) or not arr:
            continue
        keys = list(arr[0].keys())
        id_key = next((k for k in keys if "代號" in k or k.lower() in {"code", "secid"}), None)
        ind_key = next((k for k in keys if "產業" in k), None)
        if not id_key:
            continue
        for x in arr:
            sid = str(x.get(id_key, "")).strip()
            if re.fullmatch(r"\d{4}", sid):
                name = str(x.get(ind_key, "")).strip() if ind_key else ""
                if name:
                    out[sid] = name
        if out:
            break
    return out


def twse_bwibbu() -> dict[str, dict]:
    j = load_json(
        "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?response=json",
        "twse_bwibbu.json",
    )
    fields = j.get("fields") or []
    out = {}
    for row in j.get("data") or []:
        rec = dict(zip(fields, row))
        sid = str(rec.get("證券代號", "")).strip()
        out[sid] = {
            "close": fnum(rec.get("收盤價")),
            "yield": fnum(rec.get("殖利率(%)")),
            "pe": fnum(rec.get("本益比")),
            "pb": fnum(rec.get("股價淨值比")),
            "date": j.get("date"),
        }
    return out


def tpex_pe() -> dict[str, dict]:
    urls = [
        "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis",
        "https://www.tpex.org.tw/www/zh-tw/afterTrading/peQryResult?response=json",
    ]
    arr = None
    for i, url in enumerate(urls):
        try:
            raw = cached_get(f"tpex_pe_{i}.json", url)
            arr = json.loads(raw.decode("utf-8"))
            if isinstance(arr, dict):
                arr = arr.get("tables") or arr.get("data") or arr
            if isinstance(arr, list) and arr:
                break
        except Exception:
            arr = None
    if not isinstance(arr, list) or not arr:
        return {}
    # 可能是 list of dict or list of list
    out = {}
    if isinstance(arr[0], dict):
        keys = list(arr[0].keys())
        id_key = next((k for k in keys if "代號" in k or "Code" in k or k == "SecuritiesCompanyCode"), keys[0])
        for x in arr:
            sid = str(x.get(id_key, "")).strip()
            if not re.fullmatch(r"\d{4}", sid):
                continue
            close = fnum(x.get("收盤") or x.get("收盤價") or x.get("Close") or x.get("ClosingPrice"))
            yld = fnum(x.get("殖利率") or x.get("殖利率(%)") or x.get("DividendYield"))
            pe = fnum(x.get("本益比") or x.get("PE") or x.get("PriceEarningRatio"))
            pb = fnum(x.get("股價淨值比") or x.get("PBR") or x.get("PriceBookRatio"))
            out[sid] = {"close": close, "yield": yld, "pe": pe, "pb": pb}
    return out


def twse_day_all(date_yyyymmdd: str) -> dict[str, float]:
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json&date={date_yyyymmdd}"
    j = load_json(url, f"twse_day_{date_yyyymmdd}.json")
    fields = j.get("fields") or []
    out = {}
    if j.get("stat") not in (None, "OK") and not j.get("data"):
        return {}
    for row in j.get("data") or []:
        rec = dict(zip(fields, row))
        sid = str(rec.get("證券代號") or rec.get("代號") or "").strip()
        px = fnum(rec.get("收盤價") or rec.get("收盤"))
        if sid and px is not None:
            out[sid] = px
    return out


def tpex_day(date_slash: str, cache_tag: str) -> dict[str, float]:
    url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes?date={date_slash}&response=json"
    try:
        raw = cached_get(f"tpex_day_{cache_tag}.json", url)
        j = json.loads(raw.decode("utf-8"))
    except Exception:
        return {}
    tables = j.get("tables") if isinstance(j, dict) else None
    rows = None
    fields = None
    if isinstance(tables, list) and tables:
        t0 = tables[0]
        fields = t0.get("fields")
        rows = t0.get("data")
    elif isinstance(j, dict):
        fields = j.get("fields")
        rows = j.get("aaData") or j.get("data")
    out = {}
    if not rows:
        return out
    if fields:
        for row in rows:
            rec = dict(zip(fields, row)) if not isinstance(row, dict) else row
            sid = str(rec.get("證券代號") or rec.get("代號") or "").strip()
            px = fnum(rec.get("收盤") or rec.get("收盤價"))
            if sid and px is not None:
                out[sid] = px
    return out


def merge_maps(*maps: dict) -> dict:
    out = {}
    for m in maps:
        out.update(m)
    return out


def ratio(n, d):
    if n is None or d is None or d == 0:
        return None
    v = n / d
    if not math.isfinite(v):
        return None
    return v


def build_features(sid: str, annual_is: dict, annual_bs: dict, h1_is: dict, h1_prev: dict,
                   quotes: dict, px_old: dict, px_new: dict, profile: dict, industry: str) -> dict | None:
    y21 = annual_is.get("110", {}).get(sid)
    y25 = annual_is.get("114", {}).get(sid)
    if not y21 or not y25:
        return None
    rev21, rev25 = y21.get("revenue"), y25.get("revenue")
    ni21, ni25 = y21.get("ni_parent"), y25.get("ni_parent")
    if not rev21 or not rev25 or rev21 <= 0 or rev25 <= 0:
        return None
    series = {}
    for y in ("110", "111", "112", "113", "114"):
        rec = annual_is.get(y, {}).get(sid)
        if rec:
            series[y] = rec
    # need at least 2021 and 2025
    gm25 = ratio(y25.get("gross_profit"), rev25)
    om25 = ratio(y25.get("op_income"), rev25)
    nm25 = ratio(ni25, rev25)
    gm21 = ratio(y21.get("gross_profit"), y21.get("revenue"))
    om21 = ratio(y21.get("op_income"), y21.get("revenue"))
    bs25 = annual_bs.get("114", {}).get(sid) or {}
    bs21 = annual_bs.get("110", {}).get(sid) or {}
    debt25 = ratio(bs25.get("liab"), bs25.get("assets"))
    debt21 = ratio(bs21.get("liab"), bs21.get("assets"))
    eq = bs25.get("parent_eq") or bs25.get("equity")
    roe25 = ratio(ni25, eq)
    h1 = h1_is.get(sid) or {}
    h1p = h1_prev.get(sid) or {}
    h1_rev_yoy = ratio(h1.get("revenue"), h1p.get("revenue"))
    if h1_rev_yoy is not None:
        h1_rev_yoy -= 1.0
    h1_ni_yoy = None
    if h1.get("ni_parent") is not None and h1p.get("ni_parent") not in (None, 0) and h1p.get("ni_parent") > 0:
        h1_ni_yoy = h1["ni_parent"] / h1p["ni_parent"] - 1.0
    q = quotes.get(sid) or {}
    px0 = px_old.get(sid)
    px1 = px_new.get(sid) or q.get("close")
    px_ret = ratio(px1, px0)
    if px_ret is not None:
        px_ret -= 1.0
    mktcap = None
    sh = profile.get("shares")
    close = q.get("close") or px1
    if sh and close:
        # 已發行股數為股；收盤元 → 市值元
        mktcap = sh * close
    # 毛利率序列是否抬升
    oms = []
    for y in ("110", "111", "112", "113", "114"):
        rec = series.get(y)
        if rec and rec.get("revenue"):
            oms.append(ratio(rec.get("op_income"), rec["revenue"]))
    return {
        "stock_id": sid,
        "name": y25.get("name") or profile.get("name") or "",
        "industry": industry,
        "market": profile.get("market"),
        "rev_2021": rev21,
        "rev_2025": rev25,
        "ni_2021": ni21,
        "ni_2025": ni25,
        "eps_2025": y25.get("eps"),
        "rev_cagr": cagr(rev21, rev25, 4),
        "ni_cagr": cagr(ni21, ni25, 4) if ni21 and ni25 and ni21 > 0 and ni25 > 0 else None,
        "gm_2025": gm25,
        "om_2025": om25,
        "nm_2025": nm25,
        "gm_delta": (gm25 - gm21) if gm25 is not None and gm21 is not None else None,
        "om_delta": (om25 - om21) if om25 is not None and om21 is not None else None,
        "roe_2025": roe25,
        "debt_2025": debt25,
        "debt_delta": (debt25 - debt21) if debt25 is not None and debt21 is not None else None,
        "h1_rev_yoy": h1_rev_yoy,
        "h1_ni_yoy": h1_ni_yoy,
        "h1_om": ratio(h1.get("op_income"), h1.get("revenue")),
        "pe": q.get("pe"),
        "pb": q.get("pb"),
        "yield": q.get("yield"),
        "close": close,
        "px_ret_21_26": px_ret,
        "mktcap": mktcap,
        "assets_2025": bs25.get("assets"),
        "equity_2025": eq,
    }


# 與 9930 對齊的比較軸（權重偏財務體質／成長形態，評價次之）
FEATS = [
    ("rev_cagr", 0.14, 0.04),
    ("ni_cagr", 0.14, 0.06),
    ("om_2025", 0.10, 0.04),
    ("gm_2025", 0.08, 0.05),
    ("om_delta", 0.10, 0.025),
    ("roe_2025", 0.10, 0.05),
    ("debt_2025", 0.08, 0.10),
    ("debt_delta", 0.08, 0.08),
    ("h1_rev_yoy", 0.06, 0.08),
    ("yield", 0.06, 2.0),  # 百分點
    ("pe", 0.04, 6.0),
    ("pb", 0.02, 0.8),
]


def distance(row: dict, anchor: dict) -> float | None:
    acc = 0.0
    wsum = 0.0
    used = 0
    for key, w, scale in FEATS:
        a = anchor.get(key)
        b = row.get(key)
        if a is None or b is None:
            continue
        # yield/pe stored as percent/ratio already
        z = (b - a) / scale
        acc += w * z * z
        wsum += w
        used += 1
    if used < 6 or wsum <= 0:
        return None
    return math.sqrt(acc / wsum)


def hard_filter(row: dict, for_anchor: bool = False) -> bool:
    if for_anchor:
        return True
    if row.get("rev_cagr") is None:
        return False
    # 中速成長、非爆發／非崩塌
    if not (-0.03 <= row["rev_cagr"] <= 0.18):
        return False
    om = row.get("om_2025")
    gm = row.get("gm_2025")
    if om is None or gm is None:
        return False
    if not (0.05 <= om <= 0.22):
        return False
    if not (0.08 <= gm <= 0.38):
        return False
    roe = row.get("roe_2025")
    if roe is None or not (0.08 <= roe <= 0.32):
        return False
    debt = row.get("debt_2025")
    if debt is None or not (0.15 <= debt <= 0.62):
        return False
    ni = row.get("ni_2025")
    if ni is None or ni <= 0:
        return False
    # 獲利增速不低於營收太多（允許略低，但排除獲利衰退）
    if row.get("ni_cagr") is None:
        return False
    if row["ni_cagr"] < 0.02:
        return False
    yld = row.get("yield")
    pe = row.get("pe")
    # 高配息／合理本益：電子成長股常無息，排除
    if yld is None or yld < 3.0:
        return False
    if pe is None or pe <= 0 or pe > 28:
        return False
    return True


def run_screen() -> dict:
    print("fetch profiles / industry / quotes …", flush=True)
    listed = listed_profiles()
    otc = otc_profiles()
    profiles = merge_maps(otc, listed)
    ind_l = industry_names_listed()
    ind_o = industry_names_otc()
    industries = merge_maps(ind_o, ind_l)
    quotes = merge_maps(tpex_pe(), twse_bwibbu())

    print("fetch year-end / latest prices …", flush=True)
    px_2021 = merge_maps(
        twse_day_all("20211230"),
        tpex_day("2021/12/30", "20211230"),
    )
    px_now = merge_maps(
        twse_day_all("20260826"),
        tpex_day("2026/08/26", "20260826"),
    )

    annual_is: dict[str, dict] = {}
    annual_bs: dict[str, dict] = {}
    for y in ("110", "111", "112", "113", "114"):
        print(f"fetch MOPS year {y} …", flush=True)
        is_sii = fetch_mops_is(y, "04", "sii")
        is_otc = fetch_mops_is(y, "04", "otc")
        bs_sii = fetch_mops_bs(y, "04", "sii")
        bs_otc = fetch_mops_bs(y, "04", "otc")
        annual_is[y] = merge_maps(is_otc, is_sii)
        annual_bs[y] = merge_maps(bs_otc, bs_sii)
        print(f"  IS {len(annual_is[y])}  BS {len(annual_bs[y])}", flush=True)

    print("fetch MOPS H1 114/115 …", flush=True)
    h1_prev = merge_maps(fetch_mops_is("114", "02", "otc"), fetch_mops_is("114", "02", "sii"))
    h1_now = merge_maps(fetch_mops_is("115", "02", "otc"), fetch_mops_is("115", "02", "sii"))

    rows = []
    for sid, prof in profiles.items():
        industry = industries.get(sid) or prof.get("industry_name") or ""
        feat = build_features(sid, annual_is, annual_bs, h1_now, h1_prev, quotes, px_2021, px_now, prof, industry)
        if feat:
            rows.append(feat)

    anchor = next((r for r in rows if r["stock_id"] == ANCHOR_ID), None)
    if anchor is None:
        # 9930 可能因產業過濾前就在 rows
        raise SystemExit("anchor 9930 missing from MOPS annual join")

    elec = [r for r in rows if r.get("industry") in ELECTRONICS]
    passed = [r for r in elec if hard_filter(r)]
    ranked = []
    for r in passed:
        d = distance(r, anchor)
        if d is None:
            continue
        r = dict(r)
        r["distance"] = d
        r["profit_faster"] = (r.get("ni_cagr") or 0) - (r.get("rev_cagr") or 0)
        ranked.append(r)
    ranked.sort(key=lambda x: x["distance"])

    src_meta = {
        "mops_is": "https://mopsov.twse.com.tw/mops/web/t163sb04",
        "mops_bs": "https://mopsov.twse.com.tw/mops/web/t163sb05",
        "twse_profile": "https://openapi.twse.com.tw/v1/opendata/t187ap03_L",
        "twse_industry": "https://openapi.twse.com.tw/v1/opendata/t187ap14_L",
        "twse_bwibbu": "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d",
        "twse_day": "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL",
        "quote_date": (quotes.get(ANCHOR_ID) or {}).get("date"),
        "n_feature_rows": len(rows),
        "n_electronics": len(elec),
        "n_passed": len(passed),
        "n_ranked": len(ranked),
    }
    return {"anchor": anchor, "ranked": ranked, "electronics_unfiltered": elec, "meta": src_meta}


def _fmt_pct(x, digits=1):
    if x is None:
        return "—"
    return f"{x*100:.{digits}f}%"


def _fmt_pp(x, digits=1):
    if x is None:
        return "—"
    return f"{x*100:+.{digits}f}pp"


def _fmt_num(x, digits=1):
    if x is None:
        return "—"
    return f"{x:.{digits}f}"


def print_report(payload: dict, topn: int = 15) -> None:
    a = payload["anchor"]
    print("\n=== 錨點 9930 中聯資源（MOPS 年報＋證交所報價）===")
    print(
        f"營收CAGR { _fmt_pct(a['rev_cagr']) }  淨利CAGR { _fmt_pct(a['ni_cagr']) }  "
        f"2025毛利 {_fmt_pct(a['gm_2025'])} 營益 {_fmt_pct(a['om_2025'])} ROE {_fmt_pct(a['roe_2025'])} "
        f"負債比 {_fmt_pct(a['debt_2025'])} 負債變化 {_fmt_pp(a['debt_delta'])}"
    )
    print(
        f"2026H1營收YoY {_fmt_pct(a['h1_rev_yoy'])} 淨利YoY {_fmt_pct(a['h1_ni_yoy'])}  "
        f"本益 {a.get('pe')} 淨值比 {a.get('pb')} 殖利率 {a.get('yield')}%  "
        f"2021-12-30→2026-08-26價 {_fmt_pct(a.get('px_ret_21_26'))}"
    )
    print(f"\n電子業通過硬濾 {payload['meta']['n_passed']}／{payload['meta']['n_electronics']} 家")
    print(f"{'rk':>3} {'代號':<6} {'名稱':<10} {'產業':<12} {'距':>5} {'營收CAGR':>8} {'淨利CAGR':>8} {'營益':>6} {'ROE':>6} {'負債':>6} {'殖利':>5} {'本益':>5} {'H1營收':>7} {'五年價':>7}")
    for i, r in enumerate(payload["ranked"][:topn], 1):
        print(
            f"{i:3d} {r['stock_id']:<6} {r['name'][:10]:<10} {str(r['industry'])[:12]:<12} "
            f"{r['distance']:5.2f} {_fmt_pct(r['rev_cagr']):>8} {_fmt_pct(r['ni_cagr']):>8} "
            f"{_fmt_pct(r['om_2025']):>6} {_fmt_pct(r['roe_2025']):>6} {_fmt_pct(r['debt_2025']):>6} "
            f"{(str(r.get('yield')) if r.get('yield') is not None else '—'):>5} "
            f"{_fmt_num(r.get('pe'), 1):>5} "
            f"{_fmt_pct(r['h1_rev_yoy']):>7} {_fmt_pct(r.get('px_ret_21_26')):>7}"
        )


def json_dump(payload: dict, path: str) -> None:
    slim = {
        "meta": payload["meta"],
        "anchor": payload["anchor"],
        "ranked": payload["ranked"][:40],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {path}")


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    html_is = """
    <table><tr><th>公司代號</th><th>公司名稱</th><th>營業收入</th><th>營業成本</th>
    <th>營業毛利（毛損）淨額</th><th>營業利益（損失）</th>
    <th>淨利（淨損）歸屬於母公司業主</th><th>基本每股盈餘（元）</th></tr>
    <tr><td>1234</td><td>測 dummy</td><td>1000</td><td>800</td><td>200</td><td>100</td><td>80</td><td>1.2</td></tr>
    </table>
    """
    parsed = parse_mops_income(html_is)
    chk("parse revenue", parsed.get("1234", {}).get("revenue") == 1000)
    chk("parse ni", parsed.get("1234", {}).get("ni_parent") == 80)
    html_bs = """
    <table><tr><th>公司代號</th><th>公司名稱</th><th>資產總計</th><th>負債總計</th><th>權益總計</th>
    <th>歸屬於母公司業主之權益合計</th></tr>
    <tr><td>1234</td><td>測</td><td>500</td><td>200</td><td>300</td><td>290</td></tr></table>
    """
    b = parse_mops_balance(html_bs)
    chk("parse assets", b.get("1234", {}).get("assets") == 500)
    chk("cagr 6.8-ish", abs(cagr(10771, 13991, 4) - 0.0676) < 0.001)
    a = {
        "rev_cagr": 0.068, "ni_cagr": 0.148, "om_2025": 0.112, "gm_2025": 0.151,
        "om_delta": 0.029, "roe_2025": 0.186, "debt_2025": 0.406, "debt_delta": -0.138,
        "h1_rev_yoy": -0.066, "yield": 6.2, "pe": 14.4, "pb": 2.6,
    }
    near = dict(a)
    far = dict(a)
    far["rev_cagr"] = 0.40
    far["ni_cagr"] = 0.55
    far["om_2025"] = 0.40
    far["yield"] = 0.5
    far["pe"] = 40
    d0 = distance(near, a)
    d1 = distance(far, a)
    chk("distance self ~0", d0 is not None and d0 < 0.05)
    chk("far > near", d1 is not None and d1 > d0)
    row_ok = dict(a)
    row_ok["ni_2025"] = 100
    chk("hard filter pass clone", hard_filter(row_ok))
    bad = dict(row_ok)
    bad["rev_cagr"] = 0.50
    chk("hard filter reject hypergrowth", not hard_filter(bad))
    # 下游絆線：解析若把千分位當字串未轉 float 必紅
    html_comma = html_is.replace("1000", "13,991,384")
    p2 = parse_mops_income(html_comma)
    chk("comma thousands", p2.get("1234", {}).get("revenue") == 13991384)
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="9930-like electronics peer screen (TWSE/MOPS)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--json-out", default="")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.run:
        payload = run_screen()
        print_report(payload, topn=args.top)
        if args.json_out:
            json_dump(payload, args.json_out)
        return 0
    print(__doc__.split("執行指令矩陣：")[0])
    print("執行指令矩陣：")
    print(__doc__.split("執行指令矩陣：", 1)[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
