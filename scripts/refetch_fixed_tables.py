#!/usr/bin/env python
"""augur A② 修 schema 邊界後重抓截斷表 + 逐表 #7 對帳(resume-capable)。

🎯 這支在做什麼(白話):A① 修好 `generic_schema` 型別邊界(非法日期/契約月/週合約/sentinel 降級)
+ `sync` PK-null fallback(by-date 優先、撞 null 才逐 ticker by-dim-id)後,重抓 sync 期間撞 exception
而截斷的表:
- **resume 續抓後段**(前段完整):FuturesDaily(2007-)、OptionDaily(2012-)、USStockPrice(1997-,
  adaptive by-date 優先)、ConvertibleBondDailyOverview(2010-)。各表從 DB max(date) 續(#6)。
- **DROP 全史重抓**(僅 1 列、resume 會漏 before):FuturesFinalSettlementPrice。
逐表抓完做 #7 近窗對帳(byte-equal API、無幻像)。

⚠️ long-running 放量(~2 萬+ call、會週期觸額度閘暫停、跨日);須 caffeinate + 主機不睡 + resume 後路。
守 #1/#2(忠實落地)· #6(冪等+resume)· #7(對帳)· #17(限速)· #19(修 code 後重抓補完整性)。
用法:PYTHONPATH=src caffeinate -dimsu nohup venv/bin/python scripts/refetch_fixed_tables.py > /tmp/augur_refetch.log 2>&1 &
"""
import time

from augur.audit import reconcile
from augur.core import db, schema
from augur.ingestion import sync

RESUME = ["TaiwanFuturesDaily", "TaiwanOptionDaily", "USStockPrice",
          "TaiwanStockConvertibleBondDailyOverview"]
DROP_FIRST = ["TaiwanFuturesFinalSettlementPrice"]   # 僅 1 列、幾乎全空 → DROP 全史重抓(resume 漏 before)
RECENT = "2026-05-01"   # 逐表對帳近窗(避免 double 全量)


def log(m):
    print(f"[{int(time.time()) % 100000:05d}] {m}", flush=True)


def verify(conn, table):
    """逐表 #7 對帳:有真 DATE 欄走 by-date 近窗、否則 market 單批。回 (passed|None, result|err)。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute("SELECT 1 FROM information_schema.columns "
                        "WHERE table_name=%s AND column_name='date' AND data_type='date'", (table,))
            has_date = cur.fetchone() is not None
        r = reconcile.reconcile_by_date(conn, table, since=RECENT) if has_date \
            else reconcile.reconcile_market(conn, table)
        return reconcile.verdict(r)["passed"], r
    except Exception as e:
        return None, str(e)


def main():
    t0 = time.monotonic()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            schema.bootstrap_infra(cur)
        log("seed roster(per-stock fallback 用)…")
        roster = sync.seed_roster(conn)
        for t in DROP_FIRST:
            with db.transaction(conn) as cur:
                cur.execute(f'DROP TABLE IF EXISTS "{t}"')
            log(f"DROP {t}(全史重抓)")
        for i, t in enumerate(RESUME + DROP_FIRST, 1):
            el = (time.monotonic() - t0) / 60
            log(f"[{i}/{len(RESUME) + len(DROP_FIRST)}] 重抓 {t}(elapsed {el:.0f}min)…")
            try:
                r = sync.sync_finmind_dataset(conn, t, roster, progress=log)
                log(f"  {t}: {r['mode']} {r.get('rows', 0):,} 列")
                if r.get("rows"):
                    p, rec = verify(conn, t)
                    if p is True:
                        log("  ✅ #7 對帳 PASS")
                    elif p is False:
                        log(f"  ⚠️ 對帳 FAIL VM={rec['value_mismatch']} EX={rec['extra_in_db']} MIS={rec['missing_in_db']}")
                    else:
                        log(f"  對帳 err: {rec}")
            except Exception as e:
                log(f"  ❌ {type(e).__name__}: {str(e)[:120]}")
        log(f"DONE 重抓 {len(RESUME) + len(DROP_FIRST)} 表 / 總 {(time.monotonic() - t0) / 60:.0f}min")


if __name__ == "__main__":
    main()
