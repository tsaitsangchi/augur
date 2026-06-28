#!/usr/bin/env python
"""augur 全 raw data profiler — 逐表逐欄/逐 type 事實 profile,供「真懂全部定義」之據實基礎(非我以為)。

🎯 這支在做什麼(白話):對全 94 表,自動偵測 long(有 type 欄)vs wide,逐欄/逐 type 算事實 profile:
列數/日期範圍/null率/distinct/值域(min/p50/max)/樣本,並對財報長表偵測**累計(YTD)vs 單季**(同股同年值單調↑=累計)。
join column_catalog 取中文名。輸出供 synthesis 成定義參考 + 回填 catalog dirty_note/type_caveat(現幾乎空)。

唯讀、本地計算、零 Claude usage(#28)。守 #15(據實 profile、非推測)。
用法:PYTHONPATH=src python scripts/profile_raw_data.py [--table X]
"""
import argparse

from augur.core import db

SKIP = {"feature_values", "core_universe", "core_universe_asof", "pipeline_execution_log",
        "data_audit_log", "dataset_catalog", "column_catalog", "field_correlation",
        "field_return_leadlag", "field_lens_map", "raw_data_profile"}


def _cols(cur, t):
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", (t,))
    return cur.fetchall()


def _zh(cur, t):
    cur.execute("SELECT column_name, column_name_zh FROM column_catalog WHERE dataset=%s", (t,))
    return {c: z for c, z in cur.fetchall()}


def _is_cumulative(cur, t):
    """財報長表:取一活躍股,看同年四季 value 是否單調↑(累計 YTD)。回 '累計YTD' / '單季' / '?'。"""
    try:
        cur.execute(f'SELECT date, value FROM "{t}" WHERE type=(SELECT type FROM "{t}" LIMIT 1) '
                    f"AND stock_id='2330' AND date>='2023-01-01' AND date<'2024-01-01' ORDER BY date")
        vals = [float(v) for _, v in cur.fetchall() if v is not None]
        if len(vals) >= 3:
            mono = all(abs(vals[i]) <= abs(vals[i + 1]) + 1e-6 for i in range(len(vals) - 1))
            return "累計YTD" if mono else "單季"
    except Exception:
        pass
    return "?"


def profile_table(cur, t):
    cols = _cols(cur, t)
    colnames = [c for c, _ in cols]
    zh = _zh(cur, t)
    cur.execute(f'SELECT count(*) FROM "{t}"')
    n = cur.fetchone()[0]
    dr = ""
    if "date" in colnames:
        cur.execute(f'SELECT min(date), max(date) FROM "{t}"')
        lo, hi = cur.fetchone()
        dr = f" | 日期 {lo}..{hi}"
    print(f"\n### {t}  ({n:,} 列{dr})")
    if "type" in colnames and "value" in colnames:                     # long-format(財報類)
        cur.execute(f'SELECT type, count(*), min(value), percentile_cont(0.5) within group(order by value), max(value) '
                    f'FROM "{t}" GROUP BY type ORDER BY count(*) DESC')
        rows = cur.fetchall()
        cum = _is_cumulative(cur, t)
        print(f"  [long-format、{len(rows)} 種 type、語意={cum}] 前 12 type(type | n | min/p50/max):")
        for ty, c, mn, md, mx in rows[:12]:
            print(f"    {ty[:42]:42s} {c:>8,} {float(mn):>14.2f}/{float(md):>12.2f}/{float(mx):>14.2f}")
        if len(rows) > 12:
            print(f"    …(共 {len(rows)} type、餘略)")
    else:                                                              # wide-format
        for c, dt in cols:
            if dt in ("numeric", "bigint", "integer", "double precision", "real"):
                cur.execute(f'SELECT count("{c}"), count(*)-count("{c}"), min("{c}"), '
                            f'percentile_cont(0.5) within group(order by "{c}"), max("{c}") FROM "{t}"')
                nn, nulls, mn, md, mx = cur.fetchone()
                z = zh.get(c, "")
                rng = f"{float(mn):.2f}/{float(md):.2f}/{float(mx):.2f}" if mn is not None else "(全空)"
                print(f"    {c[:34]:34s} {z[:14]:14s} null={nulls:>10,} min/p50/max={rng}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="只 profile 單表")
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.table:
                tables = [args.table]
            else:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
                tables = [r[0] for r in cur.fetchall() if r[0] not in SKIP and not r[0].startswith("pg_")]
            print(f"profile {len(tables)} 表")
            for t in tables:
                try:
                    profile_table(cur, t)
                except Exception as e:
                    print(f"\n### {t}  ⚠️ profile 失敗: {e}")


if __name__ == "__main__":
    main()
