#!/usr/bin/env python3
"""🎯 `admission_assist_run`（執行事實帳本）之誠實閘——刪除一律拒絕。

守原則 #15（執行痕跡不得被抹）、#21（不靜默）。

起因（2026-07-30 Steward 拍板「讓 dry-run 也留一筆執行事實」）：
  該帳本存在之唯一目的是讓「跑了但沒東西可審」與「根本沒跑」可被分辨。
  若其列可被刪，該目的即失——刪掉一列就回到黑箱。

**設計取捨**：`UPDATE` **不鎖**——`running → completed/failed` 之狀態轉移是正常路徑
（`_run_close` 要寫 finished_at／統計）。只鎖 `DELETE`／`TRUNCATE`。

⚠ **誠實界線（承第三次獨立核驗 V-5 之教訓，不重蹈過度宣稱）**：
  本閘使刪除**不可無痕**，但**不是不可繞過**——本表 owner 為 `augur`
  ＝所有 script 所用之角色，故 `ALTER TABLE ... DISABLE TRIGGER ALL` 後仍可刪且零留痕。
  真正封閉需**角色分離**（治權表改由非 `augur` 角色持有並 REVOKE），非本閘射程。
  **故本檔不得宣稱「不可篡改」，只宣稱「一般路徑下刪除被拒」。**

執行指令矩陣
------------
    python3 scripts/migrate_assist_run_guard_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_assist_run_guard_ddl.py --check    # 唯讀驗證
    python3 scripts/migrate_assist_run_guard_ddl.py --apply    # 掛 trigger（冪等）
    python3 scripts/migrate_assist_run_guard_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

TABLE = "admission_assist_run"

DDL = f"""
CREATE OR REPLACE FUNCTION assist_run_no_delete() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '{TABLE} 為執行事實帳本：DELETE 一律拒絕（刪一列即回到「分不清沒跑或沒東西可審」之黑箱）';
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION assist_run_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '{TABLE} 為執行事實帳本：TRUNCATE 一律拒絕';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assist_run_no_delete ON {TABLE};
CREATE TRIGGER trg_assist_run_no_delete
    BEFORE DELETE ON {TABLE}
    FOR EACH ROW EXECUTE FUNCTION assist_run_no_delete();

DROP TRIGGER IF EXISTS trg_assist_run_no_truncate ON {TABLE};
CREATE TRIGGER trg_assist_run_no_truncate
    BEFORE TRUNCATE ON {TABLE}
    FOR EACH STATEMENT EXECUTE FUNCTION assist_run_no_truncate();
"""


def check(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
    if not cur.fetchone()[0]:
        print(f"SKIP {TABLE} 不存在（跑一次 assist_admission_review.py --dry-run 即自建）")
        return 0
    cur.execute("""SELECT tgname FROM pg_trigger
                    WHERE tgrelid=%s::regclass AND NOT tgisinternal ORDER BY 1""", (TABLE,))
    trg = [r[0] for r in cur.fetchall()]
    print(f"trigger：{trg or '✗ 無（執行痕跡可被靜默刪除）'}")
    ok = "trg_assist_run_no_delete" in trg and "trg_assist_run_no_truncate" in trg
    if ok:
        # 行為複驗（全程 rollback、不留痕）：**交易內自插一列再刪**並斷言被拒。
        # 不用 `WHERE false`——FOR EACH ROW trigger 於零列匹配時不觸發，那會誤報 FAIL；
        # 也不刪既有列——那會拿真痕跡當試驗品。
        try:
            cur.execute(
                f"""INSERT INTO {TABLE}
                      (run_id, mode, actor, kind, limit_n, use_llm, model,
                       prompt_version, llm_timeout_sec)
                    VALUES ('guard-probe-rollback','dry-run','guard_check','source',
                            0, false, 'n/a', 'n/a', 0)""")
            cur.execute(f"DELETE FROM {TABLE} WHERE run_id='guard-probe-rollback'")
            conn.rollback()
            print("FAIL 閘在 pg_trigger 但 DELETE **未**被拒")
            ok = False
        except Exception as e:  # noqa: BLE001 — 預期被 RAISE 擋
            conn.rollback()
            print(f"行為複驗：DELETE 實測被拒 ✓（{str(e).splitlines()[0][:70]}）")
    print("PASS 誠實閘就位（DELETE／TRUNCATE 被拒；⚠ owner 仍可 DISABLE TRIGGER，見檔頭）"
          if ok else "FAIL 未就位（跑 --apply）")
    return 0 if ok else 1


def apply(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
    if not cur.fetchone()[0]:
        print(f"✗ {TABLE} 不存在：先跑 assist_admission_review.py --dry-run --limit 1（自建表）")
        return 1
    cur.execute(DDL)
    conn.commit()
    print("已掛 trigger（冪等）；UPDATE 不受阻（running→completed 為正常轉移）")
    return check(conn)


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    chk("DELETE 被拒", "BEFORE DELETE" in DDL and "DELETE 一律拒絕" in DDL)
    chk("TRUNCATE 被拒", "BEFORE TRUNCATE" in DDL and "TRUNCATE 一律拒絕" in DDL)
    chk("UPDATE 不鎖（running→completed 須可寫）", "BEFORE UPDATE" not in DDL)
    chk("冪等（兩個 DROP TRIGGER IF EXISTS）", DDL.count("DROP TRIGGER IF EXISTS") == 2)
    chk("檔頭誠實揭露 owner 可 DISABLE TRIGGER（不作過度宣稱）",
        "DISABLE TRIGGER ALL" in __doc__ and "不可篡改" in __doc__)
    chk("check() 含行為複驗（真下 DELETE 斷言被拒，非只讀 pg_trigger）",
        "行為複驗" in open(__file__, encoding="utf-8").read().split("def _selftest")[0])
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="admission_assist_run 誠實閘（DDL；冪等）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db

    with db.connect() as conn:
        return apply(conn) if a.apply else check(conn)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
        sys.exit(main(["--check"]))
    sys.exit(main())
