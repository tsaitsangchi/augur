#!/usr/bin/env python3
"""收集 8936 國統公開財務與價量資料（零 FinMind／FRED）。

守原則 #9 #10 #15：數字只來自 HTTP 回應，原始檔落地備查。

執行指令矩陣：
  python3 scripts/collect_8936_kti_public_data.py
  python3 scripts/collect_8936_kti_public_data.py --selftest
  python3 scripts/collect_8936_kti_public_data.py --out-dir reports/8936_kti_sources
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
TICKER = "8936"
TZ8 = timezone(timedelta(hours=8))


def _save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, (dict, list)):
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        path.write_text(str(obj), encoding="utf-8")


def _get_json(url: str, timeout: int = 60, retries: int = 4):
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


MOPS_HOST = "https://mopsov.twse.com.tw"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(UA)
    s.headers["Referer"] = f"{MOPS_HOST}/mops/web/t163sb04"
    s.get(f"{MOPS_HOST}/mops/web/t163sb04", timeout=30)
    return s


def _post_mops(sess: requests.Session, url: str, year: int, season: str, extra=None) -> str:
    data = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": "otc",
        "year": str(year),
        "season": season,
    }
    if extra:
        data.update(extra)
    r = sess.post(url, data=data, timeout=90)
    r.encoding = "utf-8"
    r.raise_for_status()
    return r.text


def _row_for_ticker(dfs, ticker: str = TICKER) -> dict | None:
    for df in dfs:
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.columns:
            if "公司代號" in col or col in {"公司 代號", "代號"}:
                hit = df[df[col].astype(str).str.strip() == ticker]
                if not hit.empty:
                    rec = hit.iloc[0].to_dict()
                    return {str(k): (None if pd.isna(v) else v) for k, v in rec.items()}
        # header-in-first-row tables
        if df.shape[0] > 1:
            header = [str(x).strip() for x in df.iloc[0].tolist()]
            body = df.iloc[1:].copy()
            body.columns = header
            if "公司代號" in body.columns:
                hit = body[body["公司代號"].astype(str).str.strip() == ticker]
                if not hit.empty:
                    rec = hit.iloc[0].to_dict()
                    return {str(k): (None if pd.isna(v) else v) for k, v in rec.items()}
    return None


def fetch_mops_table(sess: requests.Session, kind: str, roc_year: int, season: str) -> dict:
    urls = {
        "income": f"{MOPS_HOST}/mops/web/ajax_t163sb04",
        "balance": f"{MOPS_HOST}/mops/web/ajax_t163sb05",
        "margin": f"{MOPS_HOST}/mops/web/ajax_t163sb06",
        "cashflow": f"{MOPS_HOST}/mops/web/ajax_t163sb20",
    }
    url = urls[kind]
    html = _post_mops(sess, url, roc_year, season)
    dfs = pd.read_html(StringIO(html))
    row = _row_for_ticker(dfs)
    return {
        "kind": kind,
        "url": url,
        "roc_year": roc_year,
        "season": season,
        "html_bytes": len(html),
        "n_tables": len(dfs),
        "row": row,
    }


def _code_of(row: dict) -> str:
    for k in ("SecuritiesCompanyCode", "CompanyCode", "公司代號"):
        if row.get(k) is not None:
            return str(row.get(k)).strip()
    return ""


def fetch_tpex_quote() -> dict:
    quotes = _get_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes")
    per = _get_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis")
    q = next((x for x in quotes if _code_of(x) == TICKER), None)
    p = next((x for x in per if _code_of(x) == TICKER), None)
    return {"quote": q, "per": p, "quote_n": len(quotes), "per_n": len(per)}


def fetch_tpex_income_snapshot() -> dict | None:
    data = _get_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci")
    return next((x for x in data if _code_of(x) == TICKER), None)


def fetch_tpex_balance_snapshot() -> dict | None:
    data = _get_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap07_O_ci")
    return next((x for x in data if _code_of(x) == TICKER), None)


def fetch_monthly_revenue_latest() -> dict | None:
    data = _get_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O")
    return next((x for x in data if _code_of(x) == TICKER), None)


def fetch_peers(codes: list[str]) -> dict:
    quotes = _get_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes")
    per = _get_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis")
    inc = _get_json("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci")
    want = set(codes)
    return {
        "quotes": [x for x in quotes if _code_of(x) in want],
        "per": [x for x in per if _code_of(x) in want],
        "income": [x for x in inc if _code_of(x) in want],
    }


def _parse_month_row(text: str) -> dict | None:
    m = re.search(
        r"8936\s*國統\s+([0-9,.\-]+)\s+([0-9,.\-]+)\s+([0-9,.\-]+)\s+"
        r"([0-9,.\-]+)\s+([0-9,.\-]+)\s+([0-9,.\-]+)\s+([0-9,.\-]+)\s+([0-9,.\-]+)",
        text,
    )
    if not m:
        return None
    keys = [
        "當月營收",
        "上月營收",
        "去年當月營收",
        "上月比較增減%",
        "去年同月增減%",
        "當月累計營收",
        "去年累計營收",
        "前期比較增減%",
    ]
    return dict(zip(keys, m.groups(), strict=True))


def fetch_monthly_revenue_history(start=(2021, 1), end=None) -> list[dict]:
    """MOPS 上櫃月營收彙總 HTML（千元）。"""
    if end is None:
        now = datetime.now(TZ8)
        end = (now.year, now.month)
    out = []
    y, m = start
    ey, em = end
    while (y, m) <= (ey, em):
        roc = y - 1911
        url = f"{MOPS_HOST}/nas/t21/otc/t21sc03_{roc}_{m}.html"
        try:
            r = requests.get(url, headers=UA, timeout=40)
            text = r.content.decode("cp950", errors="replace")
            row = _parse_month_row(text) if r.status_code == 200 else None
            out.append({"year": y, "month": m, "url": url, "status": r.status_code, "row": row})
        except Exception as e:  # noqa: BLE001 — 單月失敗不中斷整段歷史
            out.append({"year": y, "month": m, "url": url, "row": None, "error": str(e)})
        m += 1
        if m == 13:
            y, m = y + 1, 1
        time.sleep(0.15)
    return out


def fetch_yahoo_monthly() -> dict:
    now = int(datetime.now(tz=timezone.utc).timestamp())
    start = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/8936.TWO"
        f"?period1={start}&period2={now}&interval=1mo&events=div%7Csplit"
    )
    return {"url": url, "payload": _get_json(url)}


def fetch_yahoo_daily_recent() -> dict:
    now = int(datetime.now(tz=timezone.utc).timestamp())
    start = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp())
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/8936.TWO"
        f"?period1={start}&period2={now}&interval=1d"
    )
    return {"url": url, "payload": _get_json(url)}


def fetch_html(url: str) -> dict:
    r = requests.get(url, headers=UA, timeout=40)
    r.encoding = r.apparent_encoding or "utf-8"
    return {"url": url, "status": r.status_code, "text": r.text[:200000], "bytes": len(r.content)}


def collect(out_dir: Path) -> dict:
    fetched_at = datetime.now(TZ8).isoformat()
    manifest = {"ticker": TICKER, "fetched_at": fetched_at, "files": {}}

    def _try(name, fn):
        try:
            val = fn()
            _save(out_dir / f"{name}.json", val)
            manifest["files"][name] = f"{name}.json"
            print(f"OK {name}", flush=True)
            return val
        except Exception as e:  # noqa: BLE001
            _save(out_dir / f"{name}.json", {"error": str(e)})
            print(f"ERR {name} {e}", flush=True)
            return None

    _try("tpex_quote", fetch_tpex_quote)
    _try("tpex_income_snapshot", fetch_tpex_income_snapshot)
    _try("tpex_balance_snapshot", fetch_tpex_balance_snapshot)
    _try("tpex_month_revenue_latest", fetch_monthly_revenue_latest)
    _try("tpex_peers", lambda: fetch_peers(["8936", "8473", "6803", "9950"]))

    sess = _session()
    mops = []
    for roc in range(110, 116):  # 2021–2026
        for season in ("01", "02", "03", "04"):
            if roc == 115 and season not in ("01", "02"):
                continue
            rec = {"roc_year": roc, "season": season}
            for kind in ("income", "balance", "margin", "cashflow"):
                try:
                    rec[kind] = fetch_mops_table(sess, kind, roc, season)
                except Exception as e:  # noqa: BLE001
                    rec[kind] = {"error": str(e)}
                time.sleep(0.25)
            mops.append(rec)
            print(f"MOPS {roc} {season} income_row={bool((rec.get('income') or {}).get('row'))}", flush=True)
    _save(out_dir / "mops_statements.json", mops)
    manifest["files"]["mops_statements"] = "mops_statements.json"

    monthly = fetch_monthly_revenue_history()
    _save(out_dir / "mops_month_revenue.json", monthly)
    manifest["files"]["mops_month_revenue"] = "mops_month_revenue.json"

    try:
        y_m = fetch_yahoo_monthly()
        _save(out_dir / "yahoo_monthly.json", y_m)
        print("OK yahoo_monthly", flush=True)
    except Exception as e:  # noqa: BLE001
        _save(out_dir / "yahoo_monthly.json", {"error": str(e)})
        print("ERR yahoo_monthly", e, flush=True)
    try:
        y_d = fetch_yahoo_daily_recent()
        _save(out_dir / "yahoo_daily.json", y_d)
        print("OK yahoo_daily", flush=True)
    except Exception as e:  # noqa: BLE001
        _save(out_dir / "yahoo_daily.json", {"error": str(e)})
        print("ERR yahoo_daily", e, flush=True)

    pages = {}
    for key, url in {
        "kti_home": "https://www.kti.com.tw/",
        "kti_public": "https://www.kti.com.tw/list/public-information.htm",
        "gvm_5531": "https://www.gvm.com.tw/article/131077",
        "cnyes_hdpe": "https://news.cnyes.com/news/id/6581692",
        "yahoo_hdpe": "https://tw.stock.yahoo.com/news/%E5%9C%8B%E7%B5%B1%E8%BD%89%E6%8A%95%E8%B3%87hdpe%E7%AE%A1%E6%9D%90%E5%BB%A0%E9%A0%90%E8%A8%88%E4%BB%8A%E5%B9%B4%E5%BA%95%E9%87%8F%E7%94%A2-102922727.html",
        "fugle_call": "https://blog.fugle.tw/post/earnings-call-8936-2026-06-16",
        "mordor_hdpe": "https://www.mordorintelligence.com/industry-reports/hdpe-pipes-market",
        "imarc_hdpe": "https://www.imarcgroup.com/hdpe-pipes-market",
        "wearn_fs": "https://stock.wearn.com/financial.asp?kind=8936",
        "histock_is": "https://histock.tw/stock/8936/%E6%90%8D%E7%9B%8A%E8%A1%A8",
        "wra_133": "https://www.wra.gov.tw/News_Content.aspx?n=6430&s=284993&sms=9122",
        "wra_recycle": "https://www.wra.gov.tw/cp.aspx?n=39096",
    }.items():
        try:
            pages[key] = fetch_html(url)
            print(f"HTML {key} {pages[key]['status']} {pages[key]['bytes']}", flush=True)
        except Exception as e:  # noqa: BLE001
            pages[key] = {"url": url, "error": str(e)}
            print(f"HTML {key} ERR {e}", flush=True)
        time.sleep(0.2)
    # 存精簡版（全文太大）；完整 HTML 另存
    slim = {k: {kk: vv for kk, vv in v.items() if kk != "text"} | {"text_head": (v.get("text") or "")[:4000]} for k, v in pages.items()}
    _save(out_dir / "web_pages_meta.json", slim)
    for k, v in pages.items():
        if v.get("text"):
            (out_dir / f"page_{k}.html").write_text(v["text"], encoding="utf-8")

    _save(out_dir / "manifest.json", manifest)
    return manifest


def _selftest() -> int:
    assert TICKER == "8936"
    dummy = pd.DataFrame({"公司代號": ["2330", "8936"], "營業收入": [1, 2]})
    assert _row_for_ticker([dummy])["營業收入"] == 2
    parsed = _parse_month_row("8936國統 505,555 444,799 408,872 13.65 23.64 3,269,131 3,026,436 8.01-")
    assert parsed is not None
    assert parsed["當月營收"] == "505,555"
    print("SELFTEST_OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="收集 8936 國統公開資料")
    p.add_argument("--out-dir", default="reports/8936_kti_sources")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.out_dir:
        # keep argparse happy; used below
        pass
    if args.selftest:
        return _selftest()
    print("collecting into", args.out_dir, flush=True)
    collect(Path(args.out_dir))
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
