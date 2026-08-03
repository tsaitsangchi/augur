#!/usr/bin/env python3
"""🎯 綠燈帳本的兩個機械載體：紅燈時鐘 `red_since` ＋「未驗不得為 green」之 DB 層 CHECK（M-P12）。

守原則 #15（紅燈要會亮、且看得出亮多久）、#9（可溯源：green 必須有被驗過的痕跡）、
#12（不 hand-patch：改 writer + 加約束，不手動 UPDATE 補值）、#6（冪等）。

## 為什麼要這兩樣（2026-08-03 現查）

**(1) `red_since`**：帳本 20 列中 red 5 列，每日 07:10 班次忠實重驗成紅、寫回 DB、**無人處置**。
但「何時開始紅」沒有任何載體 —— `last_verified_at` 記的是「最近一次驗到它是紅的」，用它冒充
紅齡會**系統性低估**（連紅 30 天者看起來像今天才紅）。加一欄 timestamptz，由
`verify_validation_evidence.py` 於轉紅時 `COALESCE(red_since, now())`（連紅不重置）、
轉非紅時清 NULL。

**(2) `chk_ve_green_verified`**：`E3_promotion_funnel`／`E4_gm_promotion_gap` 兩列自種下起
`last_verified_at IS NULL` 卻掛 green，且 `valid_until=2026-10-09`（未來）使效期降轉永不觸發
⇒ **沒有任何機制會碰它們**，卻計入 green 分子。程式層之修補已落地（`demote_never_verified`），
本 CHECK 是它的 DB 層對偶：即便有人直接 `INSERT ... status='green'`，DB 也擋。

## 明確不做：不回填既有紅列之 `red_since`

現有 5 列紅燈之真實起紅時點**無可信來源**——`$HOME/logs/validation_evidence.log` 僅 3 次 run
且無逐行時戳，`last_verified_at` 如上所述會低估。故 `--apply` 後全部為 NULL，由下一次
`--run` 起算；週報一行在此期間誠實印「未起算」而非編一個日期。**寧可說不知道**。

## DDL 窗紀律（CLAUDE #30）

`ALTER TABLE` 取 ACCESS EXCLUSIVE；pg_dump 期間（週六 07:30）持 ACCESS SHARE，被擋住的
EXCLUSIVE 請求會**連鎖擋住後續一切查詢**。`--apply` 前置一律自檢：pg_dump 在跑／有未授予之
鎖等待／有違反 CHECK 之列 ⇒ **拒絕執行**，不硬闖。

執行指令矩陣
------------
    python3 scripts/migrate_validation_evidence_red_since_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_validation_evidence_red_since_ddl.py --check    # 唯讀：欄／約束在否＋違反列＋紅列現況
    python3 scripts/migrate_validation_evidence_red_since_ddl.py --apply    # 加欄＋加 CHECK（冪等；前置自檢不過即拒）
    python3 scripts/migrate_validation_evidence_red_since_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

TABLE = "validation_evidence"
COL = "red_since"
CONS = "chk_ve_green_verified"

# 單一來源：CHECK 與「找出違反者」之查詢皆由這條表述式衍生，兩者不可能漂移。
GREEN_VERIFIED_EXPR = "status <> 'green' OR last_verified_at IS NOT NULL"

COL_DDL = f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {COL} timestamptz"
COL_COMMENT = (
    f"COMMENT ON COLUMN {TABLE}.{COL} IS "
    "'本列最近一次由綠轉紅之時點(連紅不重置、轉非紅清 NULL);紅齡看它、不看 last_verified_at'")
CONS_DDL = f"ALTER TABLE {TABLE} ADD CONSTRAINT {CONS} CHECK ({GREEN_VERIFIED_EXPR})"
VIOLATOR_SQL = f"SELECT evidence_id FROM {TABLE} WHERE NOT ({GREEN_VERIFIED_EXPR}) ORDER BY 1"


def _has_col(cur) -> bool:
    cur.execute("SELECT count(*) FROM information_schema.columns "
                "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
    return cur.fetchone()[0] > 0


def _has_cons(cur) -> bool:
    cur.execute("SELECT count(*) FROM pg_constraint WHERE conname=%s AND conrelid=%s::regclass",
                (CONS, TABLE))
    return cur.fetchone()[0] > 0


def _violators(cur) -> list:
    cur.execute(VIOLATOR_SQL)
    return [r[0] for r in cur.fetchall()]


def ddl_window_blockers(cur) -> list:
    """#30：DDL 窗前置自檢。回傳阻斷原因（空＝可開窗）。"""
    blockers = []
    cur.execute("SELECT count(*) FROM pg_stat_activity "
                "WHERE application_name ILIKE '%pg_dump%' OR query ILIKE 'COPY %TO STDOUT%'")
    if cur.fetchone()[0]:
        blockers.append("pg_dump 疑似在跑（ACCESS SHARE 會與 ALTER 之 ACCESS EXCLUSIVE 互卡）")
    cur.execute("SELECT count(*) FROM pg_locks WHERE NOT granted")
    n_wait = cur.fetchone()[0]
    if n_wait:
        blockers.append(f"pg_locks 有 {n_wait} 個未授予之鎖等待中（已在鎖風暴邊緣，不加碼）")
    cur.execute("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a USING (pid) "
                "WHERE l.relation=%s::regclass AND a.pid <> pg_backend_pid() "
                "AND a.state='idle in transaction'", (TABLE,))
    if cur.fetchone()[0]:
        blockers.append(f"有 idle-in-transaction 之連線持著 {TABLE} 的鎖")
    return blockers


def _check(conn) -> int:
    with conn.cursor() as cur:
        has_c, has_k = _has_col(cur), _has_cons(cur)
        print(f"  {COL} 欄　　：{'在' if has_c else '**不在**（須 --apply）'}")
        print(f"  {CONS} 約束：{'在' if has_k else '**不在**（須 --apply）'}")
        bad = _violators(cur)
        print(f"  違反『green 必須驗過』之列：{len(bad)} {bad if bad else ''}"
              + ("  ← 須先跑 verify_validation_evidence.py --run 清乾淨，否則 --apply 會被 DB 拒"
                 if bad else ""))
        cur.execute("SELECT evidence_id, " + (COL if has_c else "NULL::timestamptz")
                    + f", last_verified_at FROM {TABLE} WHERE status='red' ORDER BY 1")
        rows = cur.fetchall()
        print(f"  紅列 {len(rows)} 條：")
        for eid, rs, lva in rows:
            rs_s = rs.strftime("%Y-%m-%d") if rs else ("未起算" if has_c else "欄未就位")
            lva_s = f"{lva:%Y-%m-%d %H:%M}" if lva else "NULL"
            print(f"    {eid:<30} red_since={rs_s:<12} last_verified_at={lva_s}")
        blockers = ddl_window_blockers(cur)
        print("  DDL 窗前置：" + ("可開窗（無阻斷）" if not blockers else "**不可開窗**"))
        for b in blockers:
            print(f"    ✗ {b}")
    return 0


def _apply(conn) -> int:
    with conn.cursor() as cur:
        bad = _violators(cur)
        if bad:
            print(f"✗ 拒絕 --apply：{len(bad)} 列違反『green 必須驗過』：{bad}", file=sys.stderr)
            print("  先跑 venv/bin/python scripts/verify_validation_evidence.py --run", file=sys.stderr)
            return 1
        blockers = ddl_window_blockers(cur)
        if blockers:
            print("✗ 拒絕 --apply：DDL 窗前置不過（#30 鎖風暴）：", file=sys.stderr)
            for b in blockers:
                print(f"    {b}", file=sys.stderr)
            return 1
        cur.execute("SET LOCAL lock_timeout='5s'")   # 拿不到鎖就放棄,不排隊擋住全庫
        cur.execute(COL_DDL)
        cur.execute(COL_COMMENT)
        if not _has_cons(cur):
            cur.execute(CONS_DDL)
    conn.commit()
    print(f"✓ {TABLE}.{COL} 與 {CONS} 就位（冪等）")
    print(f"  註：既有紅列之 {COL} 一律 NULL——真實起紅時點無可信來源，不回填、不編日期；"
          "下次 --run 起算。")
    return 0


class _FakeCur:
    """自測用假 cursor：記下送出的 SQL，依查詢內容回固定計數（零 DB）。"""

    def __init__(self, violators=(), dump=0, waits=0, idle=0, has_cons=0):
        self.executed = []
        self._v, self._dump, self._waits, self._idle, self._cons = \
            list(violators), dump, waits, idle, has_cons
        self._last = ""

    def execute(self, sql, args=None):
        self.executed.append(sql)
        self._last = sql

    def fetchall(self):
        return [(v,) for v in self._v]

    def fetchone(self):
        s = self._last
        for needle, val in (("pg_dump", self._dump), ("NOT granted", self._waits),
                            ("idle in transaction", self._idle), ("pg_constraint", self._cons)):
            if needle in s:
                return (val,)
        return (0,)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _FakeConn:
    def __init__(self, cur):
        self._cur, self.commits = cur, 0

    def cursor(self):
        return self._cur

    def commit(self):
        self.commits += 1


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("加欄冪等（IF NOT EXISTS）", "IF NOT EXISTS" in COL_DDL)
    chk("CHECK 與違反者查詢同源（各恰含該表述式一次，不可能漂移）",
        CONS_DDL.count(GREEN_VERIFIED_EXPR) == 1 and VIOLATOR_SQL.count(GREEN_VERIFIED_EXPR) == 1)
    chk("違反者查詢為 NOT(表述式)（找的是被 CHECK 擋下的那一群）",
        VIOLATOR_SQL.count(f"NOT ({GREEN_VERIFIED_EXPR})") == 1)
    # 表述式之語意紅綠：以 psycopg2 對 timestamptz 之真形狀（datetime／None）逐格驗
    import datetime as _dt
    now = _dt.datetime(2026, 8, 3, 12, 0, tzinfo=_dt.timezone.utc)

    def passes(status, lva):
        return status != "green" or lva is not None

    chk("green + 已驗 → 過", passes("green", now))
    chk("green + 未驗 → 擋（E3／E4_gm 之形狀）", not passes("green", None))
    chk("red + 未驗 → 過（紅列不因未驗而被擋）", passes("red", None))
    chk("unverified + 未驗 → 過", passes("unverified", None))

    # ── --apply 之前置行為（假 conn／假 cursor，零 DB）：不過就不得送出任何 ALTER ──
    def run_apply(**kw):
        cur = _FakeCur(**kw)
        conn = _FakeConn(cur)
        rc = _apply(conn)
        return rc, " ".join(cur.executed), conn.commits

    rc, sql, commits = run_apply(violators=["E3_promotion_funnel"])
    chk("有違反列 → rc=1 且一條 ALTER 都沒送出", rc == 1 and "ALTER TABLE" not in sql and commits == 0)
    rc, sql, commits = run_apply(waits=3)
    chk("有未授予鎖等待 → rc=1 且不送 ALTER（#30 不加碼）",
        rc == 1 and "ALTER TABLE" not in sql and commits == 0)
    rc, sql, commits = run_apply(dump=1)
    chk("pg_dump 在跑 → rc=1 且不送 ALTER", rc == 1 and "ALTER TABLE" not in sql and commits == 0)
    rc, sql, commits = run_apply()
    chk("前置全過 → rc=0、送出加欄＋加約束、commit 一次",
        rc == 0 and COL_DDL in sql and CONS_DDL in sql and commits == 1)
    chk("前置全過時先設 lock_timeout（拿不到鎖就放棄，不排隊擋全庫）", "lock_timeout" in sql)
    rc, sql, _ = run_apply(has_cons=1)
    chk("約束已在 → 不重複 ADD CONSTRAINT（冪等）", rc == 0 and CONS_DDL not in sql)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validation_evidence 加 red_since 欄＋green 必須驗過之 CHECK")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
