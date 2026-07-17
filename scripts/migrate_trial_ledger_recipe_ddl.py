#!/usr/bin/env python
"""trial_ledger recipe 遷移 — 建構/標籤配方鍵入帳(alpha 計畫 Phase 1-1;拍板點 2 hugo 2026-07-18)。

🎯 這支在做什麼(白話):trial_ledger 的 UNIQUE 鍵原無欄可表達「建構/標籤變體」(P1 buffer/P4 vol-target/
   M2 標籤等)→同號配方不同建構會撞鍵或漏記=**N 靜默低估**(審查 A-M1/B-B1)。遷移=加 `recipe` 欄
   (DEFAULT 'plain'=現行無 overlay 建構;既有 32 列自動回填)+UNIQUE 擴含 recipe。
   消費端(deflate_headline_verdict/revalidate)N 口徑=**數列**(per-row net_sharpe)——recipe 新列天然
   入計、查詢零改動(#12 實查 :84-86/:297);selftest 斷言兩端一致。詞彙表 SSOT=改善計畫 §4.3(b)。

守 #6(冪等)· #12(N 口徑單一語意)· #30(DDL 避開 dump/長查詢;ACCESS EXCLUSIVE 鎖)· #29a/d。
   SSOT=reports/taiwan_alpha_improvement_plan_20260717.md 附錄 A.2。

執行指令矩陣:
  python scripts/migrate_trial_ledger_recipe_ddl.py            # 無參數:現況(唯讀)
  python scripts/migrate_trial_ledger_recipe_ddl.py --run      # 冪等遷移(加欄+回填+UNIQUE 擴)
  python scripts/migrate_trial_ledger_recipe_ddl.py --verify   # 結構斷言(exit 0/1)
  python scripts/migrate_trial_ledger_recipe_ddl.py --selftest # 消費端口徑一致純斷言(零寫入)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

UQ_COLS = ["model", "horizon", "top_frac", "weight", "feats_hash", "cost", "sample_since", "recipe"]


def _has_recipe(cur):
    cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name='trial_ledger' AND column_name='recipe'")
    return bool(cur.fetchone())


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        if _has_recipe(cur):
            print("✓ recipe 欄已存在(冪等跳過)")
            return verify()
        cur.execute("ALTER TABLE trial_ledger ADD COLUMN recipe text NOT NULL DEFAULT 'plain'")
        cur.execute("COMMENT ON COLUMN trial_ledger.recipe IS "
                    "'建構/標籤配方鍵(詞彙表=alpha 改善計畫 §4.3(b) 凍結;plain=無 overlay 現行建構;新詞=新預註冊)'")
        cur.execute("ALTER TABLE trial_ledger DROP CONSTRAINT trial_ledger_uq")
        cur.execute(f"ALTER TABLE trial_ledger ADD CONSTRAINT trial_ledger_uq UNIQUE ({', '.join(UQ_COLS)})")
        conn.commit()
    print("✓ --run 完成:recipe 欄(DEFAULT 'plain' 回填既有列)+UNIQUE 擴 8 欄")
    return verify()


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        has = _has_recipe(cur)
        cur.execute("""SELECT array_agg(a.attname ORDER BY x.ord) FROM pg_constraint c
                       JOIN LATERAL unnest(c.conkey) WITH ORDINALITY x(attnum, ord) ON true
                       JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=x.attnum
                       WHERE c.conname='trial_ledger_uq'""")
        uq = list(cur.fetchone()[0] or [])
        tot = plain = 0
        if has:
            cur.execute("SELECT count(*), count(*) FILTER (WHERE recipe='plain') FROM trial_ledger")
            tot, plain = cur.fetchone()
    ok = has and uq == UQ_COLS
    print(f"{'✓' if ok else '✗'} verify:recipe 欄={has} UNIQUE={uq}")
    print(f"  列回填:{tot} 列中 {plain} 列 recipe='plain'")
    return 0 if ok else 1


def _selftest():
    """消費端 N 口徑一致斷言(零寫入):deflate/revalidate 之 N=數列(非七欄 DISTINCT)→recipe 新列天然入計。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import re
    dh = open("scripts/deflate_headline_verdict.py").read()
    rv = open("scripts/revalidate.py").read()
    chk("deflate 消費端=per-row 取 metric_value(數列口徑)",
        bool(re.search(r"SELECT horizon, metric_value FROM trial_ledger", dh)))
    chk("deflate 無七欄 DISTINCT 組合計數(recipe 列天然入計)",
        "DISTINCT (model" not in dh and "DISTINCT(model" not in dh)
    chk("revalidate 消費端=per-row 取 metric_value", bool(re.search(r"metric_value FROM trial_ledger", rv)))
    chk("UQ_COLS 尾=recipe(擴充鍵)", UQ_COLS[-1] == "recipe" and len(UQ_COLS) == 8)
    bf = open("scripts/migrate_trial_ledger_ddl.py").read()
    chk("BACKFILL 寫入端 ON CONFLICT=8 欄含 recipe(2026-07-17 漏網實證:selftest 原只鎖讀取端)",
        "sample_since, recipe)" in bf)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.run:
        return run()
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        has = _has_recipe(cur)
        cur.execute("SELECT count(*) FROM trial_ledger")
        print(f"現況:recipe 欄={'已存在' if has else '未遷移'}、trial_ledger {cur.fetchone()[0]} 列")
    return 0


if __name__ == "__main__":
    sys.exit(main())
