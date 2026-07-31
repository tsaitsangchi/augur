#!/usr/bin/env python3
"""🎯 `promotion_queue` 加寫入時戳——讓「還要多久」從外推變成量測。

守原則 #11（含隨機性之量須取 min/median/max，不是單點）、#15（不以估算充當事實）。

起因（2026-07-31 實犯三次）：I3 之完成時點被我以「總數 ÷ 總時間」外推，先後給出
22:50／00:30／00:07 三個互相矛盾的估計。查明根因後發現**不是算得不準，是沒有東西可算**：

    run 20 共 45 列；decided_at 非空 **0** 列

`promotion_queue` **無任何「本列何時寫入」之欄位**（`decided_at` 是決策時點，pending 者全空）。
逐 feature 之完成時點在 DB 裡不存在 ⇒ 唯一訊號是人手動抽樣之計數 ⇒ 只能外推。
而該量之變異達十倍（run 20 前 5 個約 6.5 分/個，第 6 個逾 17 分）⇒ 單點外推必錯。

加了本欄之後：

    SELECT feature, created_at FROM promotion_queue WHERE run_id=%s ORDER BY created_at

即得**真實成本分布**，可依 #11 報 min/median/max 而非單點，剩餘時間由已完成者之分布推得。

**⚠ 本 DDL 會碰進行中之表**（不同於 `feature_sign_check` 之建新表）：
`ALTER TABLE ... ADD COLUMN` 需 `AccessExclusive`，而 I3 正持續 INSERT 本表。
故 `lock_timeout` **不是保底而是必要條件**——搶不到即放棄，**絕不排隊**：
排隊中之 AccessExclusive 會堵住其後一切查詢，那正是 CLAUDE #30 鎖風暴之成因，
真發生會癱瘓跑了數小時的 I3。搶不到就等它收工再跑，代價只是晚幾小時。

**欄位可為 NULL**：既有列（含 run 20 之 45 列）**不回填**——它們的真實寫入時點已不可考，
灌一個假時戳等於製造看似有據的假資料（#9）。舊列 NULL＝誠實的「查無」。

執行指令矩陣
------------
    python3 scripts/migrate_promotion_queue_timing_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_promotion_queue_timing_ddl.py --check    # 唯讀：欄在否＋覆蓋率＋鎖現況
    python3 scripts/migrate_promotion_queue_timing_ddl.py --apply    # 加欄（冪等；lock_timeout 保護）
    python3 scripts/migrate_promotion_queue_timing_ddl.py --repair   # 修假回填（DROP 後依正確兩句重加）
    python3 scripts/migrate_promotion_queue_timing_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

TABLE = "promotion_queue"
COL = "created_at"
LOCK_TIMEOUT = "3s"

# **兩句，不可合成一句**（2026-07-31 實犯）：
#   `ADD COLUMN x timestamptz DEFAULT now()` 會把 ALTER 當下之時戳**回填給所有既有列**
#   （PG 之 fast-default：now() 為 STABLE、於 ALTER 時求值一次並存為 missing value）
#   ⇒ 486 列全部宣稱寫於同一秒，而它們實際橫跨數日＝**製造看似有據的假資料**（#9）。
#   分成「先無預設加欄（既有列得 NULL）」＋「再設預設（只影響此後之 INSERT）」才正確。
DDL_STEPS = (
    f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {COL} timestamptz",
    f"ALTER TABLE {TABLE} ALTER COLUMN {COL} SET DEFAULT now()",
)
DDL = "; ".join(DDL_STEPS)   # 保留供自測檢視
COMMENT = (
    f"COMMENT ON COLUMN {TABLE}.{COL} IS "
    "'本列寫入時點(2026-07-31 加)。舊列為 NULL＝真實時點不可考、不回填假值。"
    "用途:逐 feature 閘評估成本之真實分布,使進度改以量測而非外推'")


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
        has = cur.fetchone()[0] > 0
        print(f"  {TABLE}.{COL}：{'在' if has else '**不在**（須 --apply）'}")
        if has:
            cur.execute(f"SELECT count(*), count({COL}) FROM {TABLE}")
            n, n_ts = cur.fetchone()
            print(f"  覆蓋：{n_ts}/{n} 列有時戳（舊列 NULL 為預期，不回填）")
        cur.execute("SELECT count(*) FROM pg_stat_activity "
                    "WHERE datname=current_database() AND state='idle in transaction'")
        idle_tx = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pg_locks WHERE NOT granted")
        waiting = cur.fetchone()[0]
        print(f"  鎖現況：idle-in-transaction {idle_tx} 條、等待中之鎖 {waiting} 個")
        if idle_tx:
            print("  ⚠ 有長交易持有本表之 AccessShare 時，ALTER 會搶不到鎖而放棄（那是對的）。")
    return 0


def _apply(conn) -> int:
    with conn.cursor() as cur:
        # **必要條件而非保底**：搶不到即放棄、不排隊（排隊會癱瘓進行中之 I3）。
        cur.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")
        try:
            for _s in DDL_STEPS:
                cur.execute(_s)
            cur.execute(COMMENT)
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            print(f"✗ 搶不到鎖或 DDL 失敗（已放棄、未排隊）：{type(e).__name__}: {e}", file=sys.stderr)
            print("  這是預期行為——待進行中之長交易（如 TWEVO I3）收工後重跑即可。", file=sys.stderr)
            return 3
    conn.commit()
    print(f"✓ {TABLE}.{COL} 就位（冪等；lock_timeout={LOCK_TIMEOUT}）")
    print("  舊列維持 NULL（不回填假時戳）；新列自動帶 now()。")
    return 0


def _repair(conn) -> int:
    """修 2026-07-31 之假回填：既有列被灌上同一秒之時戳。

    偵測條件＝**有 ≥2 列共用同一個 `created_at` 到微秒**（真實寫入不可能如此）。
    處置＝DROP COLUMN 再依正確兩句重加——該欄現有內容**全部為假**，drop 不失去任何真實資訊；
    相對地以 UPDATE 把它們改回 NULL 屬 hand-patch（#12），且無法區分「假回填」與「真的同秒寫入」。
    """
    with conn.cursor() as cur:
        cur.execute(f"SELECT {COL}, count(*) FROM {TABLE} WHERE {COL} IS NOT NULL "
                    f"GROUP BY 1 ORDER BY 2 DESC LIMIT 1")
        r = cur.fetchone()
        if not r or r[1] < 2:
            print("✓ 未偵測到假回填（無 ≥2 列共用同一微秒）——無須修復")
            return 0
        ts, n = r
        cur.execute(f"SELECT count(*) FROM {TABLE}")
        total = cur.fetchone()[0]
        print(f"  偵測到假回填：{n}/{total} 列共用時戳 {ts}")
        print(f"  處置：DROP COLUMN {COL} 後依正確兩句重加（既有列回歸 NULL＝誠實之『查無』）")
        cur.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")
        try:
            cur.execute(f"ALTER TABLE {TABLE} DROP COLUMN {COL}")
            for s in DDL_STEPS:
                cur.execute(s)
            cur.execute(COMMENT)
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            print(f"✗ 搶不到鎖或失敗（已放棄、未排隊）：{type(e).__name__}: {e}", file=sys.stderr)
            return 3
    conn.commit()
    print(f"✓ 已修復；{COL} 現為既有列 NULL、新列自動帶 now()")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    body = open(__file__, encoding="utf-8").read()
    chk("DDL 冪等（IF NOT EXISTS）", "IF NOT EXISTS" in DDL_STEPS[0])
    # 原斷言為 `"NOT NULL" not in DDL`——只驗 DDL 文字、**沒驗真實行為**，
    # 於是放過了「ADD COLUMN ... DEFAULT now() 會回填既有列」這個真正的坑（2026-07-31 實犯：
    # 486 列全被灌上同一秒之假時戳）。改為驗**加欄與設預設必須分兩句**。
    chk("加欄句**不得**帶 DEFAULT（否則回填既有列＝造假資料）",
        "ADD COLUMN" in DDL_STEPS[0] and "DEFAULT" not in DDL_STEPS[0])
    chk("預設另以 SET DEFAULT 設（只影響此後之 INSERT）",
        "SET DEFAULT now()" in DDL_STEPS[1] and "ADD COLUMN" not in DDL_STEPS[1])
    chk("兩句順序正確（先加欄、後設預設）", len(DDL_STEPS) == 2)
    chk("apply 前設 lock_timeout", "lock_timeout" in body.split("def _apply")[1].split("def _selftest")[0])
    chk("搶不到鎖即 rollback 並回非 0（不排隊、不靜默）",
        "conn.rollback()" in body and "return 3" in body)
    chk("失敗訊息明說這是預期行為（不誤導為錯誤）", "這是預期行為" in body)
    # 原斷言禁 "ALTER COLUMN"——但正確的兩句法**必須**用它來 SET DEFAULT，
    # 故該斷言在修好回填坑之後反而變成紅燈（斷言本身寫錯，非 code 錯）。
    # 改為：apply 路徑不得含破壞性動作；DROP 只准出現在明示之 --repair。
    chk("apply 路徑只加欄與設預設（無 DROP／無 SET NOT NULL）",
        not any(k in " ".join(DDL_STEPS) for k in ("DROP", "SET NOT NULL", "USING")))
    chk("DROP 僅存在於明示之 --repair（不會被 --apply 誤觸）",
        "DROP COLUMN" not in body.split("def _apply")[1].split("def _repair")[0])
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=f"{TABLE} 加 {COL}（進度改以量測而非外推）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--repair", action="store_true",
                    help="修 2026-07-31 之假回填（既有列被灌同一秒時戳）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        if a.repair:
            return _repair(conn)
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
