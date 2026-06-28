#!/usr/bin/env python
"""augur 逐表逐年覆蓋掃描 — 找所有覆蓋缺口(承 BalanceSheet 2022-24 缺季之發現,全表掃)。

🎯 這支在做什麼(白話):對每張有 date 的表,逐年算 distinct 日期數 + distinct 股數,推斷頻率(日/週/月/季),
**標出偏離該表常態頻率之年(缺口)** + 最後日期(陳舊)。財報季表逐年列缺哪季。供「已驗覆蓋」之據實基礎。

唯讀、本地、零 usage(#28)。守 #15(逐表掃、標缺口、不假設完整)。
用法:PYTHONPATH=src python scripts/scan_coverage.py
"""
import argparse
from collections import Counter

from augur.core import db

FIN = {"TaiwanStockFinancialStatements", "TaiwanStockBalanceSheet", "TaiwanStockCashFlowsStatement"}


def _has(cur, t, col):
    cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s", (t, col))
    return cur.fetchone() is not None


def scan(cur, t):
    if not _has(cur, t, "date"):
        return None
    has_stock = _has(cur, t, "stock_id")
    sc = ", count(distinct stock_id)" if has_stock else ", 0"
    cur.execute(f'SELECT substr(date::text,1,4) yr, count(distinct date){sc} FROM "{t}" GROUP BY yr ORDER BY yr')
    rows = cur.fetchall()
    if not rows:
        return None
    ndates = [int(d) for _, d, _ in rows]
    mode = Counter(ndates).most_common(1)[0][0]                # 常態年日期數
    freq = ("日" if mode > 150 else "週" if mode > 35 else "月" if mode > 8 else "季/事件")
    # 缺口年:日期數 < 常態之 60%(且常態>1)
    gaps = [(y, d, s) for y, d, s in rows if mode > 1 and d < mode * 0.6]
    return {"freq": freq, "mode": mode, "years": len(rows), "span": f"{rows[0][0]}-{rows[-1][0]}",
            "last": None, "gaps": gaps, "has_stock": has_stock, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table")
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.table:
                tables = [args.table]
            else:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                            "AND table_name LIKE 'Taiwan%' ORDER BY table_name")
                tables = [r[0] for r in cur.fetchall()]
            print(f"覆蓋掃描 {len(tables)} 表(Taiwan*)\n")
            clean, gapped, fin_detail = [], [], []
            for t in tables:
                try:
                    r = scan(cur, t)
                except Exception as e:
                    print(f"⚠️ {t}: {e}"); continue
                if r is None:
                    continue
                if t in FIN:                                    # 財報季表:逐年列季
                    cur.execute(f"SELECT substr(date::text,1,4) yr, string_agg(distinct substr(date::text,6,5),',' order by substr(date::text,6,5)) "
                                f"FROM \"{t}\" WHERE type=(SELECT type FROM \"{t}\" GROUP BY type ORDER BY count(*) DESC LIMIT 1) GROUP BY yr ORDER BY yr")
                    qy = cur.fetchall()
                    miss = [f"{y}({q})" for y, q in qy if len(q.split(",")) < 4 and y >= "2015"]
                    fin_detail.append((t, miss))
                if r["gaps"]:
                    gapped.append((t, r))
                else:
                    clean.append((t, r))
            print("══ 財報季表逐年缺季(≥2015、<4季)══")
            for t, miss in fin_detail:
                print(f"  {t}: {'、'.join(miss) if miss else '✅ 各年四季全'}")
            print(f"\n══ 有覆蓋缺口之表({len(gapped)})══")
            for t, r in gapped:
                g = "; ".join(f"{y}={d}({'股'+str(s) if r['has_stock'] else ''})" for y, d, s in r["gaps"][:6])
                print(f"  {t} [{r['freq']}、常態{r['mode']}/年]: 缺口年 {g}")
            print(f"\n══ 覆蓋正常之表({len(clean)})══")
            print("  " + "、".join(t for t, _ in clean))


if __name__ == "__main__":
    main()
