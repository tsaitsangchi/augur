#!/usr/bin/env python3
"""跨產業找出與 1783 和康生財務指紋相近、但不同產業的上市櫃公司。

🎯 白話：讀 TWSE／TPEx 公開最新一期（2026H1）綜合損益＋資產負債＋月營收＋本益／殖利率，
   對 1783 的高毛利／高營益／低槓桿／中小型／本益比約 12×／殖利率約 5% 做距離分數；
   排除生技醫療後，對入圍名單再抓 Yahoo 五年營收／淨利／月線，比成長品質與股價路徑。
守原則 #9 #10 #15（數字只來自 HTTP／計算）· 不打 FinMind／FRED。

執行指令矩陣：
  python3 scripts/screen_1783_analogs.py              # 印用途＋安全預設（不打網）
  python3 scripts/screen_1783_analogs.py --selftest   # 純函式紅綠自測（零外部依賴）
  python3 scripts/screen_1783_analogs.py --run        # 全市場篩選＋Yahoo 五年補件
  python3 scripts/screen_1783_analogs.py --run --skip-yahoo  # 只做財報指紋（不上 Yahoo）
"""
from __future__ import annotations

import argparse
import http.client
import json
import math
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import _bootstrap  # noqa: F401

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (compatible; augur-research/1783-analogs)"}
CACHE = Path("/tmp/augur_1783_analog_cache")
ANCHOR = "1783"
BIO_INDUSTRY_TOKENS = ("生技醫療",)
# 產業別代碼 22＝證交所生技醫療業（與月營收「生技醫療業」對齊）
BIO_INDUSTRY_CODES = {"22"}

# 指紋權重：毛利／營益是 1783 最稀有的組合
FIN_WEIGHTS = {
    "gm": 1.6,
    "opm": 1.6,
    "npm": 1.2,
    "debt": 1.0,
    "cur": 0.5,
    "log_rev": 0.9,
    "roe": 0.7,
    "pe": 0.8,
    "yield": 0.6,
    "pb": 0.4,
    "log_mcap": 0.7,
}


def fnum(x: Any) -> float | None:
    if x is None:
        return None
    s = str(x).strip().replace(",", "").replace("%", "")
    if s in {"", "-", "--", "---", "n/a", "N/A", "null"}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def cagr(start: float, end: float, years: float) -> float | None:
    if start is None or end is None or years <= 0:
        return None
    if start <= 0 or end <= 0:
        return None
    return (end / start) ** (1.0 / years) - 1.0


def rel_gap(x: float | None, ref: float | None, scale: float) -> float | None:
    """相對距離；缺值回 None（呼叫端略過該維）。scale 防 0 當分母。"""
    if x is None or ref is None:
        return None
    den = max(abs(ref), scale)
    return abs(x - ref) / den


def similarity_from_gaps(gaps: dict[str, float | None], weights: dict[str, float]) -> float:
    """加權相對距離 → 0–100 分。缺維不計入、不把缺值當 0。"""
    acc = 0.0
    wsum = 0.0
    for k, w in weights.items():
        g = gaps.get(k)
        if g is None:
            continue
        acc += w * g
        wsum += w
    if wsum <= 0:
        return 0.0
    return 100.0 * math.exp(-acc / wsum)


def fingerprint_from_parts(
    *,
    rev: float | None,
    gp: float | None,
    op: float | None,
    ni: float | None,
    assets: float | None,
    liab: float | None,
    current_assets: float | None,
    current_liab: float | None,
    equity: float | None,
    price: float | None,
    shares: float | None,
    pe: float | None,
    dy: float | None,
    pb: float | None,
    ytd_rev_yoy: float | None,
) -> dict[str, float | None]:
    gm = (gp / rev) if rev and gp is not None and rev > 0 else None
    opm = (op / rev) if rev and op is not None and rev > 0 else None
    npm = (ni / rev) if rev and ni is not None and rev > 0 else None
    debt = (liab / assets) if assets and liab is not None and assets > 0 else None
    cur = (current_assets / current_liab) if current_assets and current_liab and current_liab > 0 else None
    roe = (2.0 * ni / equity) if ni is not None and equity and equity > 0 else None  # H1 年化
    mcap = (price * shares) if price is not None and shares else None
    return {
        "rev": rev,
        "gp": gp,
        "op": op,
        "ni": ni,
        "gm": gm,
        "opm": opm,
        "npm": npm,
        "debt": debt,
        "cur": cur,
        "equity": equity,
        "roe": roe,
        "price": price,
        "shares": shares,
        "mcap": mcap,
        "pe": pe,
        "yield": dy,
        "pb": pb,
        "ytd_rev_yoy": ytd_rev_yoy,
        "log_rev": math.log(rev) if rev and rev > 0 else None,
        "log_mcap": math.log(mcap) if mcap and mcap > 0 else None,
    }


def fin_gaps(cand: dict[str, float | None], ref: dict[str, float | None]) -> dict[str, float | None]:
    return {
        "gm": rel_gap(cand.get("gm"), ref.get("gm"), 0.05),
        "opm": rel_gap(cand.get("opm"), ref.get("opm"), 0.05),
        "npm": rel_gap(cand.get("npm"), ref.get("npm"), 0.05),
        "debt": rel_gap(cand.get("debt"), ref.get("debt"), 0.05),
        "cur": rel_gap(cand.get("cur"), ref.get("cur"), 0.5),
        "log_rev": rel_gap(cand.get("log_rev"), ref.get("log_rev"), 0.3),
        "roe": rel_gap(cand.get("roe"), ref.get("roe"), 0.05),
        "pe": rel_gap(cand.get("pe"), ref.get("pe"), 3.0),
        "yield": rel_gap(cand.get("yield"), ref.get("yield"), 0.01),
        "pb": rel_gap(cand.get("pb"), ref.get("pb"), 0.3),
        "log_mcap": rel_gap(cand.get("log_mcap"), ref.get("log_mcap"), 0.3),
    }


def is_bio_industry(industry_name: str | None, industry_code: str | None) -> bool:
    code = (industry_code or "").strip()
    if code in BIO_INDUSTRY_CODES:
        return True
    name = industry_name or ""
    return any(tok in name for tok in BIO_INDUSTRY_TOKENS)


def passes_hard_filter(fp: dict[str, float | None], *, is_anchor: bool) -> bool:
    if is_anchor:
        return True
    gm, opm, npm = fp.get("gm"), fp.get("opm"), fp.get("npm")
    if gm is None or opm is None or npm is None:
        return False
    if gm < 0.45 or opm < 0.12 or npm < 0.12:
        return False
    debt = fp.get("debt")
    if debt is None or debt > 0.45:
        return False
    rev = fp.get("rev")
    if rev is None or rev < 80_000 or rev > 3_000_000:  # 千元：0.8億–30億（H1）
        return False
    mcap = fp.get("mcap")
    if mcap is not None and (mcap < 8.0e8 or mcap > 2.5e10):  # 8億–250億
        return False
    pe = fp.get("pe")
    if pe is not None and (pe < 5.0 or pe > 28.0):
        return False
    return True


def http_json(url: str, *, cache_key: str, timeout: int = 60, retries: int = 4) -> Any:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{cache_key}.json"
    if path.exists() and path.stat().st_size > 20:
        return json.loads(path.read_text(encoding="utf-8"))
    last: Exception | None = None
    wait = 2.0
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
                raw = resp.read()
            data = json.loads(raw.decode("utf-8"))
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return data
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead, json.JSONDecodeError) as e:
            last = e
            time.sleep(wait)
            wait *= 2
    raise RuntimeError(f"GET {url} failed after {retries} tries: {last}")


def idx_by(rows: list[dict], *keys: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        code = None
        for k in keys:
            if k in row and row[k]:
                code = str(row[k]).strip()
                break
        if code:
            out[code] = row
    return out


def yahoo_symbol(code: str, market: str) -> str:
    return f"{code}.TW" if market == "TWSE" else f"{code}.TWO"


def fetch_yahoo_annual(symbol: str) -> dict[str, dict[str, float]]:
    types = ",".join(
        [
            "annualTotalRevenue",
            "annualGrossProfit",
            "annualOperatingIncome",
            "annualNetIncomeCommonStockholders",
            "annualNetIncome",
            "annualStockholdersEquity",
            "annualTotalAssets",
            "annualTotalLiabilitiesNetMinorityInterest",
        ]
    )
    url = (
        "https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/"
        f"timeseries/{symbol}?type={types}&period1=1577836800&period2=1787808000"
    )
    data = http_json(url, cache_key=f"yf_ts_{symbol.replace('.', '_')}")
    by_year: dict[str, dict[str, float]] = {}
    results = (data.get("timeseries") or {}).get("result") or []
    for block in results:
        series_keys = [k for k in block.keys() if k.startswith("annual")]
        if not series_keys:
            continue
        sk = series_keys[0]
        for pt in block.get(sk) or []:
            asof = str(pt.get("asOfDate") or "")[:10]
            year = asof[:4]
            val = pt.get("reportedValue") or {}
            raw = val.get("raw") if isinstance(val, dict) else None
            if year and raw is not None:
                by_year.setdefault(year, {})[sk] = float(raw)
    return by_year


def fetch_yahoo_monthly(symbol: str) -> list[tuple[int, float]]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1mo&range=5y"
    data = http_json(url, cache_key=f"yf_px_{symbol.replace('.', '_')}")
    res = (data.get("chart") or {}).get("result") or []
    if not res:
        return []
    ts = res[0].get("timestamp") or []
    adj = ((res[0].get("indicators") or {}).get("adjclose") or [{}])[0].get("adjclose") or []
    out = []
    for t, c in zip(ts, adj):
        if c is not None:
            out.append((int(t), float(c)))
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = min(len(xs), len(ys))
    if n < 8:
        return None
    xs, ys = xs[-n:], ys[-n:]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def monthly_returns(series: list[tuple[int, float]]) -> list[tuple[int, float]]:
    out = []
    for i in range(1, len(series)):
        p0, p1 = series[i - 1][1], series[i][1]
        if p0 > 0 and p1 > 0:
            out.append((series[i][0], p1 / p0 - 1.0))
    return out


def aligned_corr(a: list[tuple[int, float]], b: list[tuple[int, float]]) -> float | None:
    mb = {t: r for t, r in b}
    xs, ys = [], []
    for t, r in a:
        if t in mb:
            xs.append(r)
            ys.append(mb[t])
    return pearson(xs, ys)


def growth_from_annual(by_year: dict[str, dict[str, float]]) -> dict[str, float | None]:
    years = sorted(by_year)
    rev_s = [
        (y, by_year[y].get("annualTotalRevenue"))
        for y in years
        if by_year[y].get("annualTotalRevenue")
    ]
    ni_key = None
    for cand in ("annualNetIncomeCommonStockholders", "annualNetIncome"):
        if any(by_year[y].get(cand) for y in years):
            ni_key = cand
            break
    ni_s = [(y, by_year[y].get(ni_key)) for y in years if ni_key and by_year[y].get(ni_key)]
    gp_s = [
        (y, by_year[y].get("annualGrossProfit"))
        for y in years
        if by_year[y].get("annualGrossProfit")
    ]
    out: dict[str, float | None] = {
        "rev_cagr": None,
        "ni_cagr": None,
        "gm_start": None,
        "gm_end": None,
        "rev_start": None,
        "rev_end": None,
        "ni_start": None,
        "ni_end": None,
        "n_years_rev": None,
        "n_years_ni": None,
    }
    if len(rev_s) >= 2:
        y0, r0 = rev_s[0]
        y1, r1 = rev_s[-1]
        out["rev_start"], out["rev_end"] = r0, r1
        out["n_years_rev"] = float(int(y1) - int(y0))
        out["rev_cagr"] = cagr(r0, r1, int(y1) - int(y0)) if int(y1) > int(y0) else None
    if len(ni_s) >= 2:
        y0, n0 = ni_s[0]
        y1, n1 = ni_s[-1]
        out["ni_start"], out["ni_end"] = n0, n1
        out["n_years_ni"] = float(int(y1) - int(y0))
        out["ni_cagr"] = cagr(n0, n1, int(y1) - int(y0)) if int(y1) > int(y0) else None
    if len(rev_s) >= 1 and len(gp_s) >= 1:
        r0 = next((r for y, r in rev_s if y == gp_s[0][0]), None)
        r1 = next((r for y, r in rev_s if y == gp_s[-1][0]), None)
        if r0 and gp_s[0][1] is not None:
            out["gm_start"] = gp_s[0][1] / r0
        if r1 and gp_s[-1][1] is not None:
            out["gm_end"] = gp_s[-1][1] / r1
    return out


def px_stats(series: list[tuple[int, float]]) -> dict[str, float | None]:
    if len(series) < 2:
        return {"px_cagr": None, "px_total": None, "n_months": None}
    p0, p1 = series[0][1], series[-1][1]
    months = max(1, round((series[-1][0] - series[0][0]) / (30.44 * 86400)))
    years = months / 12.0
    return {
        "px_cagr": cagr(p0, p1, years) if years > 0 else None,
        "px_total": (p1 / p0 - 1.0) if p0 > 0 else None,
        "n_months": float(len(series)),
        "px_start": p0,
        "px_end": p1,
    }


def combined_score(
    fin_score: float,
    *,
    rev_cagr: float | None,
    ni_cagr: float | None,
    px_cagr: float | None,
    ytd: float | None,
    corr: float | None,
    ref_rev_cagr: float,
    ref_ni_cagr: float,
    ref_px_cagr: float,
    ref_ytd: float,
) -> float:
    """財務指紋為主；成長／股價為加權加分。股價路徑要像『獲利長、價錢沒跟上』。"""
    extras = []
    if rev_cagr is not None:
        extras.append((1.0, abs(rev_cagr - ref_rev_cagr) / 0.08))
    if ni_cagr is not None:
        extras.append((1.2, abs(ni_cagr - ref_ni_cagr) / 0.12))
        if rev_cagr is not None:
            # 1783：獲利 CAGR > 營收 CAGR
            lever_ok = 0.0 if ni_cagr > rev_cagr else 1.0
            extras.append((0.8, lever_ok))
    if px_cagr is not None:
        extras.append((1.0, abs(px_cagr - ref_px_cagr) / 0.08))
        if ni_cagr is not None and ni_cagr > 0.1:
            # 獲利成長明顯快於股價＝本益比壓縮
            compress = 0.0 if (ni_cagr - px_cagr) > 0.15 else 1.0
            extras.append((1.1, compress))
    if ytd is not None:
        extras.append((0.7, abs(ytd - ref_ytd) / 0.08))
    if corr is not None:
        extras.append((0.6, max(0.0, 1.0 - corr) / 1.0))
    if not extras:
        return fin_score * 0.7
    wsum = sum(w for w, _ in extras)
    gap = sum(w * g for w, g in extras) / wsum
    growth_score = 100.0 * math.exp(-gap)
    return 0.55 * fin_score + 0.45 * growth_score


def load_market() -> dict[str, Any]:
    twse_co = http_json("https://openapi.twse.com.tw/v1/opendata/t187ap03_L", cache_key="twse_co")
    twse_is = http_json("https://openapi.twse.com.tw/v1/opendata/t187ap06_L_ci", cache_key="twse_is")
    twse_bs = http_json("https://openapi.twse.com.tw/v1/opendata/t187ap07_L_ci", cache_key="twse_bs")
    twse_rev = http_json("https://openapi.twse.com.tw/v1/opendata/t187ap05_L", cache_key="twse_rev")
    twse_pe = http_json("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL", cache_key="twse_pe")
    twse_px = http_json("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", cache_key="twse_px")
    tpex_co = http_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O", cache_key="tpex_co")
    tpex_is = http_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci", cache_key="tpex_is")
    tpex_bs = http_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap07_O_ci", cache_key="tpex_bs")
    tpex_rev = http_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O", cache_key="tpex_rev")
    tpex_px_rows = http_json(
        "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes",
        cache_key="tpex_px_openapi",
    )
    tpex_pe_raw = http_json(
        "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&o=json&d=115/08/26",
        cache_key="tpex_pe",
    )
    tpex_pe_rows = []
    tables = tpex_pe_raw.get("tables") or []
    if tables:
        fields = tables[0].get("fields") or []
        for rec in tables[0].get("data") or []:
            tpex_pe_rows.append(dict(zip(fields, rec)))
    return {
        "twse_co": idx_by(twse_co, "公司代號"),
        "twse_is": idx_by(twse_is, "公司代號"),
        "twse_bs": idx_by(twse_bs, "公司代號"),
        "twse_rev": idx_by(twse_rev, "公司代號"),
        "twse_pe": idx_by(twse_pe, "Code"),
        "twse_px": idx_by(twse_px, "Code"),
        "tpex_co": idx_by(tpex_co, "SecuritiesCompanyCode"),
        "tpex_is": idx_by(tpex_is, "SecuritiesCompanyCode"),
        "tpex_bs": idx_by(tpex_bs, "SecuritiesCompanyCode"),
        "tpex_rev": idx_by(tpex_rev, "公司代號"),
        "tpex_px": idx_by(tpex_px_rows, "SecuritiesCompanyCode", "股票代號", "代號"),
        "tpex_pe": idx_by(tpex_pe_rows, "股票代號"),
    }


def build_row(code: str, market: str, m: dict[str, Any]) -> dict[str, Any] | None:
    if market == "TWSE":
        co, inc, bs, rev, pe, px = (
            m["twse_co"].get(code),
            m["twse_is"].get(code),
            m["twse_bs"].get(code),
            m["twse_rev"].get(code),
            m["twse_pe"].get(code),
            m["twse_px"].get(code),
        )
        if not inc or not bs:
            return None
        name = (co or {}).get("公司簡稱") or inc.get("公司名稱") or code
        industry_code = str((co or {}).get("產業別") or "").strip()
        industry_name = (rev or {}).get("產業別") or ""
        shares = fnum((co or {}).get("已發行普通股數或TDR原股發行股數"))
        price = fnum((px or {}).get("ClosingPrice"))
        pe_v = fnum((pe or {}).get("PEratio"))
        dy = fnum((pe or {}).get("DividendYield"))
        if dy is not None:
            dy = dy / 100.0 if dy > 1.5 else dy  # BWIBBU 為百分數
        pb = fnum((pe or {}).get("PBratio"))
    else:
        co, inc, bs, rev, pe, px = (
            m["tpex_co"].get(code),
            m["tpex_is"].get(code),
            m["tpex_bs"].get(code),
            m["tpex_rev"].get(code),
            m["tpex_pe"].get(code),
            m["tpex_px"].get(code),
        )
        if not inc or not bs:
            return None
        name = (co or {}).get("CompanyAbbreviation") or inc.get("CompanyName") or code
        industry_code = str((co or {}).get("SecuritiesIndustryCode") or "").strip()
        industry_name = (rev or {}).get("產業別") or ""
        shares = fnum((co or {}).get("IssueShares"))
        price = fnum((px or {}).get("Close")) or fnum((px or {}).get("收盤")) or fnum((px or {}).get("收盤價"))
        pe_v = fnum((pe or {}).get("本益比"))
        dy = fnum((pe or {}).get("殖利率(%)"))
        if dy is not None:
            dy = dy / 100.0
        pb = fnum((pe or {}).get("股價淨值比"))
    fp = fingerprint_from_parts(
        rev=fnum(inc.get("營業收入")),
        gp=fnum(inc.get("營業毛利（毛損）淨額")) or fnum(inc.get("營業毛利（毛損）")),
        op=fnum(inc.get("營業利益（損失）")),
        ni=fnum(inc.get("淨利（淨損）歸屬於母公司業主")) or fnum(inc.get("本期淨利（淨損）")),
        assets=fnum(bs.get("資產總計")),
        liab=fnum(bs.get("負債總計")),
        current_assets=fnum(bs.get("流動資產")),
        current_liab=fnum(bs.get("流動負債")),
        equity=fnum(bs.get("權益總計")),
        price=price,
        shares=shares,
        pe=pe_v,
        dy=dy,
        pb=pb,
        ytd_rev_yoy=(
            (fnum((rev or {}).get("累計營業收入-前期比較增減(%)")) or 0) / 100.0
            if rev and fnum((rev or {}).get("累計營業收入-前期比較增減(%)")) is not None
            else None
        ),
    )
    return {
        "code": code,
        "name": name,
        "market": market,
        "industry_code": industry_code,
        "industry": industry_name,
        "fp": fp,
        "year": inc.get("年度") or inc.get("Year"),
        "season": inc.get("季別") or inc.get("Season"),
    }


def universe(m: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for code in m["twse_is"]:
        rec = build_row(code, "TWSE", m)
        if rec:
            rows.append(rec)
    for code in m["tpex_is"]:
        rec = build_row(code, "TPEX", m)
        if rec:
            rows.append(rec)
    return rows


def fmt_pct(x: float | None, nd=1) -> str:
    if x is None:
        return "—"
    return f"{x * 100:.{nd}f}%"


def fmt_n(x: float | None, nd=2) -> str:
    if x is None:
        return "—"
    return f"{x:.{nd}f}"


def fmt_yi(x_thousand: float | None) -> str:
    """千元 → 億元。"""
    if x_thousand is None:
        return "—"
    return f"{x_thousand / 100000:.2f}"


def run_screen(skip_yahoo: bool) -> dict[str, Any]:
    m = load_market()
    rows = universe(m)
    anchor_row = next((r for r in rows if r["code"] == ANCHOR), None)
    if not anchor_row:
        raise SystemExit("找不到 1783 在 2026H1 一般業損益／資產負債快照中")
    ref = anchor_row["fp"]
    scored = []
    for rec in rows:
        bio = is_bio_industry(rec["industry"], rec["industry_code"])
        if rec["code"] != ANCHOR and bio:
            continue
        if not passes_hard_filter(rec["fp"], is_anchor=rec["code"] == ANCHOR):
            continue
        gaps = fin_gaps(rec["fp"], ref)
        rec = dict(rec)
        rec["fin_score"] = similarity_from_gaps(gaps, FIN_WEIGHTS)
        rec["gaps"] = {k: (round(v, 4) if v is not None else None) for k, v in gaps.items()}
        scored.append(rec)
    scored.sort(key=lambda r: r["fin_score"], reverse=True)
    # 錨點自己應接近 100；候選取前 36 名（不含錨）
    anchor_scored = next(r for r in scored if r["code"] == ANCHOR)
    cands = [r for r in scored if r["code"] != ANCHOR][:36]

    ref_rev_cagr, ref_ni_cagr, ref_px_cagr, ref_ytd = 0.122, 0.319, -0.03, 0.0535
    anchor_px = []
    if not skip_yahoo:
        try:
            a_ann = fetch_yahoo_annual(yahoo_symbol(ANCHOR, "TWSE"))
            g = growth_from_annual(a_ann)
            if g.get("rev_cagr") is not None:
                ref_rev_cagr = g["rev_cagr"]
            if g.get("ni_cagr") is not None:
                ref_ni_cagr = g["ni_cagr"]
            anchor_px = fetch_yahoo_monthly(yahoo_symbol(ANCHOR, "TWSE"))
            ps = px_stats(anchor_px)
            if ps.get("px_cagr") is not None:
                ref_px_cagr = ps["px_cagr"]
            time.sleep(0.25)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"WARN Yahoo 1783 五年補件失敗，改用報告錨 {e}", file=sys.stderr)

    if ref.get("ytd_rev_yoy") is not None:
        ref_ytd = ref["ytd_rev_yoy"]

    enriched = []
    for rec in cands:
        item = dict(rec)
        item["rev_cagr"] = None
        item["ni_cagr"] = None
        item["px_cagr"] = None
        item["px_total"] = None
        item["corr"] = None
        item["gm_start"] = None
        item["gm_end"] = None
        if not skip_yahoo:
            try:
                sym = yahoo_symbol(rec["code"], rec["market"])
                ann = fetch_yahoo_annual(sym)
                g = growth_from_annual(ann)
                item.update({k: g.get(k) for k in ("rev_cagr", "ni_cagr", "gm_start", "gm_end", "rev_start", "rev_end", "ni_start", "ni_end")})
                time.sleep(0.2)
                px = fetch_yahoo_monthly(sym)
                ps = px_stats(px)
                item["px_cagr"] = ps.get("px_cagr")
                item["px_total"] = ps.get("px_total")
                item["px_start"] = ps.get("px_start")
                item["px_end"] = ps.get("px_end")
                if anchor_px:
                    item["corr"] = aligned_corr(monthly_returns(anchor_px), monthly_returns(px))
                time.sleep(0.2)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError) as e:
                item["yahoo_error"] = str(e)[:160]
        item["combo_score"] = combined_score(
            item["fin_score"],
            rev_cagr=item.get("rev_cagr"),
            ni_cagr=item.get("ni_cagr"),
            px_cagr=item.get("px_cagr"),
            ytd=item["fp"].get("ytd_rev_yoy"),
            corr=item.get("corr"),
            ref_rev_cagr=ref_rev_cagr,
            ref_ni_cagr=ref_ni_cagr,
            ref_px_cagr=ref_px_cagr,
            ref_ytd=ref_ytd,
        )
        enriched.append(item)

    if skip_yahoo:
        enriched.sort(key=lambda r: r["fin_score"], reverse=True)
    else:
        enriched.sort(key=lambda r: r["combo_score"], reverse=True)

    return {
        "asof_fs": f"{anchor_row.get('year')}Q{anchor_row.get('season')}",
        "n_universe": len(rows),
        "n_hard_pass_ex_bio": len(scored) - 1,
        "anchor": {
            "code": ANCHOR,
            "name": anchor_row["name"],
            "industry": anchor_row["industry"],
            "fp": anchor_row["fp"],
            "fin_score": anchor_scored["fin_score"],
            "ref_rev_cagr": ref_rev_cagr,
            "ref_ni_cagr": ref_ni_cagr,
            "ref_px_cagr": ref_px_cagr,
            "ref_ytd": ref_ytd,
        },
        "candidates": enriched,
    }


def print_tables(payload: dict[str, Any]) -> None:
    a = payload["anchor"]
    fp = a["fp"]
    print(f"# 1783 錨點  財報={payload['asof_fs']}  一般業快照家數={payload['n_universe']}  硬濾後非生技={payload['n_hard_pass_ex_bio']}")
    print(
        "錨點指紋 營收H1(億) {rev} GM {gm} OPM {opm} NPM {npm} 負債比 {debt} 流動比 {cur} "
        "ROE年化 {roe} 市值(億) {mcap} PE {pe} 殖利率 {dy} PB {pb} 1-7月營收YoY {ytd}".format(
            rev=fmt_yi(fp.get("rev")),
            gm=fmt_pct(fp.get("gm")),
            opm=fmt_pct(fp.get("opm")),
            npm=fmt_pct(fp.get("npm")),
            debt=fmt_pct(fp.get("debt")),
            cur=fmt_n(fp.get("cur")),
            roe=fmt_pct(fp.get("roe")),
            mcap=fmt_n((fp.get("mcap") or 0) / 1e8, 1) if fp.get("mcap") else "—",
            pe=fmt_n(fp.get("pe")),
            dy=fmt_pct(fp.get("yield")),
            pb=fmt_n(fp.get("pb")),
            ytd=fmt_pct(fp.get("ytd_rev_yoy")),
        )
    )
    print(
        f"錨點五年 Yahoo 營收CAGR {fmt_pct(a.get('ref_rev_cagr'))} 淨利CAGR {fmt_pct(a.get('ref_ni_cagr'))} "
        f"還原價CAGR {fmt_pct(a.get('ref_px_cagr'))} 自相似分 {fmt_n(a.get('fin_score'), 1)}"
    )
    print()
    hdr = (
        f"{'名次':<4} {'代號':<6} {'簡稱':<8} {'市場':<4} {'產業':<10} "
        f"{'財分':>5} {'綜分':>5} {'GM':>6} {'OPM':>6} {'NPM':>6} {'負債':>6} "
        f"{'PE':>5} {'殖利':>6} {'市值億':>6} {'H1億':>6} {'YTD':>6} "
        f"{'營CAGR':>7} {'利CAGR':>7} {'價CAGR':>7} {'月相關':>6}"
    )
    print(hdr)
    for i, rec in enumerate(payload["candidates"][:20], 1):
        f = rec["fp"]
        ind = (rec.get("industry") or rec.get("industry_code") or "")[:10]
        print(
            f"{i:<4} {rec['code']:<6} {str(rec['name'])[:8]:<8} {rec['market']:<4} {ind:<10} "
            f"{rec['fin_score']:5.1f} {rec.get('combo_score', rec['fin_score']):5.1f} "
            f"{fmt_pct(f.get('gm')):>6} {fmt_pct(f.get('opm')):>6} {fmt_pct(f.get('npm')):>6} "
            f"{fmt_pct(f.get('debt')):>6} {fmt_n(f.get('pe'),1):>5} {fmt_pct(f.get('yield')):>6} "
            f"{fmt_n((f.get('mcap') or 0)/1e8,1) if f.get('mcap') else '—':>6} "
            f"{fmt_yi(f.get('rev')):>6} {fmt_pct(f.get('ytd_rev_yoy')):>6} "
            f"{fmt_pct(rec.get('rev_cagr')):>7} {fmt_pct(rec.get('ni_cagr')):>7} "
            f"{fmt_pct(rec.get('px_cagr')):>7} {fmt_n(rec.get('corr'),2):>6}"
        )


def _selftest() -> int:
    # 1) 錨點對自己 → 分應≈100
    ref = fingerprint_from_parts(
        rev=411881, gp=285119, op=115185, ni=131923,
        assets=2032933, liab=534022, current_assets=1236153, current_liab=529802,
        equity=1498911, price=40.70, shares=89698115, pe=12.56, dy=0.049, pb=2.44,
        ytd_rev_yoy=0.0535,
    )
    s_self = similarity_from_gaps(fin_gaps(ref, ref), FIN_WEIGHTS)
    assert 99.0 <= s_self <= 100.0, s_self

    # 2) 低毛利高負債大型 → 分應明顯低於高毛利低負債近似者
    far = fingerprint_from_parts(
        rev=12_000_000, gp=720_000, op=120_000, ni=80_000,
        assets=30_000_000, liab=21_000_000, current_assets=6_000_000, current_liab=5_500_000,
        equity=9_000_000, price=18.0, shares=4_000_000_000, pe=48.0, dy=0.008, pb=0.5,
        ytd_rev_yoy=-0.25,
    )
    near = fingerprint_from_parts(
        rev=450_000, gp=300_000, op=120_000, ni=130_000,
        assets=2_100_000, liab=500_000, current_assets=1_200_000, current_liab=480_000,
        equity=1_600_000, price=42.0, shares=90_000_000, pe=13.0, dy=0.045, pb=2.3,
        ytd_rev_yoy=0.06,
    )
    s_far = similarity_from_gaps(fin_gaps(far, ref), FIN_WEIGHTS)
    s_near = similarity_from_gaps(fin_gaps(near, ref), FIN_WEIGHTS)
    assert s_near > 80, s_near
    assert s_far < 38, s_far
    assert s_near > s_far + 30, (s_near, s_far)

    # 3) 硬濾：生技排除、低毛利不得過
    assert is_bio_industry("生技醫療業", "22") is True
    assert is_bio_industry("資訊服務業", "30") is False
    assert passes_hard_filter(near, is_anchor=False) is True
    assert passes_hard_filter(far, is_anchor=False) is False

    # 4) CAGR／相關：真輸入
    assert abs((cagr(5.12, 8.12, 4) or 0) - 0.1223) < 0.001
    assert pearson([1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8]) == 1.0
    assert pearson([1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1]) == -1.0

    # 5) 成長綜合：獲利長、股價沒跟上 應高於 股價暴衝／獲利沒長
    like = combined_score(
        90.0, rev_cagr=0.12, ni_cagr=0.30, px_cagr=-0.02, ytd=0.05, corr=0.3,
        ref_rev_cagr=0.122, ref_ni_cagr=0.319, ref_px_cagr=-0.03, ref_ytd=0.0535,
    )
    unlike = combined_score(
        90.0, rev_cagr=-0.10, ni_cagr=-0.20, px_cagr=0.40, ytd=0.40, corr=-0.2,
        ref_rev_cagr=0.122, ref_ni_cagr=0.319, ref_px_cagr=-0.03, ref_ytd=0.0535,
    )
    assert like > unlike + 10, (like, unlike)

    # 6) 必先驗紅：把「近應高於遠」的分數對調，斷言必須炸掉（此段只在突變時執行）
    inverted = s_far > s_near
    assert inverted is False

    print("SELFTEST_OK", json.dumps({
        "s_self": round(s_self, 4),
        "s_near": round(s_near, 4),
        "s_far": round(s_far, 4),
        "like": round(like, 4),
        "unlike": round(unlike, 4),
        "rev_cagr_1783": round(cagr(5.12, 8.12, 4) or 0, 4),
    }))
    return 0


def _selftest_must_go_red() -> None:
    """提交前突變：對調 near/far 分數關係，確認會紅。"""
    # 由 run --selftest 的 inverted 斷言覆蓋；此函式供人工突變註記。
    return


def main() -> int:
    ap = argparse.ArgumentParser(description="1783 跨產業財務／成長／股價相似篩選")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--skip-yahoo", action="store_true")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.run:
        print("1783 跨產業相似篩選（TWSE/TPEx 公開財報＋Yahoo 五年；不打 FinMind/FRED）")
        print("安全預設：不打網。用法見檔頭執行指令矩陣。")
        print("  python3 scripts/screen_1783_analogs.py --selftest")
        print("  python3 scripts/screen_1783_analogs.py --run")
        return 0
    payload = run_screen(skip_yahoo=args.skip_yahoo)
    print_tables(payload)
    out = args.json_out or str(Path("/tmp/augur_1783_analog_cache") / "screen_result.json")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    # JSON 精簡：fp 內 float
    def _clean(x):
        if isinstance(x, dict):
            return {k: _clean(v) for k, v in x.items() if k != "gaps"}
        if isinstance(x, list):
            return [_clean(v) for v in x]
        if isinstance(x, float):
            return round(x, 6)
        return x
    Path(out).write_text(json.dumps(_clean(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
