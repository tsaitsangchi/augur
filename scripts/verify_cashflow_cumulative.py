#!/usr/bin/env python
"""augur 現金流逐 type 累計乾淨驗 — 改用 |Q4|/|Q1| 比值法(抗變號,取代有缺陷的 |value|-單調)。

🎯 這支在做什麼(白話):上次 |value|-單調測對「會變號的現金流」不準。改用穩健法:累計 YTD 之 Q4(全年)
量級應遠大於 Q1(一季)→ 跨股 median(|Q4|/|Q1|) ≥ ~2 = 累計;≈1 = 單季。逐 34 type 乾淨定論。
用 2021(現金流四季全)。守 #15(換穩健法、逐 type 驗)。本地零 usage(#28)。
用法:PYTHONPATH=src python scripts/verify_cashflow_cumulative.py
"""
import numpy as np
from augur.core import db

T = "TaiwanStockCashFlowsStatement"
YR = 2021


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT type FROM "{T}" ORDER BY type')
            types = [r[0] for r in cur.fetchall()]
            print(f"現金流 {len(types)} type 累計驗(|Q4|/|Q1| 中位、{YR})\n")
            agg = {}
            for ty in types:
                cur.execute(f'SELECT stock_id, substr(date::text,6,5) q, value FROM "{T}" '
                            f"WHERE type=%s AND date>='{YR}-01-01' AND date<'{YR+1}-01-01' AND value IS NOT NULL", (ty,))
                bys = {}
                for sid, q, v in cur.fetchall():
                    bys.setdefault(sid, {})[q] = float(v)
                ratios = []
                for sid, qd in bys.items():
                    q1, q4 = qd.get("03-31"), qd.get("12-31")
                    if q1 and q4 and abs(q1) > 1:
                        ratios.append(abs(q4) / abs(q1))
                if len(ratios) >= 10:
                    med = float(np.median(ratios))
                    sem = "累計YTD" if med >= 2.0 else ("單季" if med <= 1.5 else "混合?")
                    agg[sem] = agg.get(sem, 0) + 1
                    print(f"  {ty[:50]:50s} med|Q4|/|Q1|={med:>5.1f} → {sem}  ({len(ratios)}股)")
                else:
                    agg["?不足"] = agg.get("?不足", 0) + 1
                    print(f"  {ty[:50]:50s} 樣本不足({len(ratios)}股)")
            print(f"\n→ 彙總: {agg}")


if __name__ == "__main__":
    main()
