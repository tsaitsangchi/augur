#!/usr/bin/env python
"""PriceAdj 基準修復 — 受損股完整史重抓至單一現行基準(E1 修復鏈;arena review F2)。

🎯 這支在做什麼(白話):回溯調整序列(TaiwanStockPriceAdj)每逢除息全史重算——增量 append 會把
   「舊基準史+新基準增量」拼接成損傷序列(factor=adj/raw 在除息點回落)。本工具:①factor 單調性
   全表掃描找受損股;②對受損股**整檔重抓**(單一現行基準、per-stock 一 request)、同交易 DELETE+INSERT;
   ③重掃驗證歸零。resume-safe(逐股冪等);#24 三層防護內建於 finmind.fetch。
   **結構性註記**:live 維運下每逢除息此問題必復發——長期正解=庫內以 raw+除權息事件自建調整序列
   (arena plan §5 已規畫用於結算標籤);本工具為過渡期修復器。

守 #12(重抓 writer 非 hand-patch)· #24/#25(步調/最小單位)· #6(逐股交易冪等)· #29a/d。

執行指令矩陣:
  python scripts/repair_priceadj_basis.py                  # 無參數:factor 掃描報告(唯讀)
  python scripts/repair_priceadj_basis.py --repair          # 掃描→受損股整檔重抓→重掃驗證
  python scripts/repair_priceadj_basis.py --repair --limit 5   # 小樣測試(#25)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.ingestion import finmind

FACTOR_TOL = 0.995   # factor 回落 >0.5% = 拼接違規(捨入雜訊上界之外)

SCAN_SQL = """
WITH f AS (
  SELECT a.stock_id, a.date, a.close/NULLIF(r.close,0) AS factor
  FROM "TaiwanStockPriceAdj" a JOIN "TaiwanStockPrice" r USING (stock_id, date)
  WHERE a.stock_id IN (SELECT DISTINCT stock_id FROM core_universe_asof) AND r.close > 0
), v AS (
  SELECT stock_id, factor, lag(factor) OVER (PARTITION BY stock_id ORDER BY date) AS prev
  FROM f
)
SELECT stock_id, count(*) FROM v WHERE factor < prev * %s GROUP BY stock_id ORDER BY stock_id"""


def scan(cur):
    cur.execute(SCAN_SQL, (FACTOR_TOL,))
    return cur.fetchall()


def repair(limit):
    with db.connect() as conn:
        cur = conn.cursor()
        damaged = scan(cur)
        print(f"factor 掃描:{len(damaged)} 檔受損")
        if limit:
            damaged = damaged[:limit]
        n_ok, n_fail = 0, 0
        for i, (sid, nviol) in enumerate(damaged):
            try:
                rows = finmind.fetch("TaiwanStockPriceAdj", data_id=sid,
                                     start_date="1990-01-01", end_date="2099-12-31")
                if not rows:
                    print(f"  ✗ {sid}: API 回 0 列—跳過(留損傷、不誤刪)")
                    n_fail += 1
                    continue
                cols = list(rows[0].keys())
                collist = ", ".join(f'"{c}"' for c in cols)
                ph = ", ".join(["%s"] * len(cols))
                cur.execute('DELETE FROM "TaiwanStockPriceAdj" WHERE stock_id=%s', (sid,))
                cur.executemany(f'INSERT INTO "TaiwanStockPriceAdj" ({collist}) VALUES ({ph})',
                                [tuple(r[c] for c in cols) for r in rows])
                conn.commit()                          # 逐股交易=resume-safe
                n_ok += 1
                if (i + 1) % 20 == 0:
                    print(f"  … {i+1}/{len(damaged)}(最新 {sid}:{len(rows)} 列)", flush=True)
            except Exception as e:
                conn.rollback()
                print(f"  ✗ {sid}: {type(e).__name__}: {str(e)[:80]}—rollback 跳過")
                n_fail += 1
        remain = scan(cur)
        print(f"✓ 修復 {n_ok} 檔(失敗 {n_fail});重掃殘留受損:{len(remain)} 檔"
              + ("" if not remain else f" → {[r[0] for r in remain[:10]]}"))
        return 0 if not remain or limit else 1
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--repair", action="store_true")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    if args.repair:
        return repair(args.limit)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        d = scan(cur)
        print(f"factor 掃描(唯讀):{len(d)} 檔受損" + (f",前 10:{[x[0] for x in d[:10]]}" if d else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
