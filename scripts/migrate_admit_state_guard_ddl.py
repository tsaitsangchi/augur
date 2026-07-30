#!/usr/bin/env python3
"""🎯 `knowhow_auto_admit_state` 之誠實閘——降級與刪除須通行證，正常升級不受阻。

守原則 #15（誠實：狀態不得被靜默改）、#12（帳本為唯一權威）。

起因（2026-07-30 自陳＋核驗共同指出）：該表**無任何 trigger**，而本日依 Steward 拍板
對其 **145,949 列**執行 `admit_depth 9→7` 之降級——該次 UPDATE **完全沒有機械閘保護**，
帳本（`knowhow_depth_reevaluation`）是唯一留痕。任何人／任何腳本可靜默改任一 item 之
准入深度，而深度現為**顧問引文之排序鍵**（`rank_citations_kh_first`），故其可信度直接
影響作答。

**設計取捨（為何不全表上鎖）**：`upsert_state()` 為層級推進之熱路徑、每 item 每輪皆寫，
且其語義為 `GREATEST(...)` 單調升。全表要通行證會使熱路徑需處處帶 GUC、徒增失敗面。
故本閘**只鎖風險動作**：
  - `DELETE`／`TRUNCATE` → **一律拒絕**（狀態帳不得刪）
  - `UPDATE` 使 `admit_depth` **下降** → 須通行證 `SET LOCAL augur.admit_depth_lower = 'on'`
    （降級＝撤銷既有准入宣稱，屬 `#15` 判死留檔之類型，不得無痕）
  - 其餘 `UPDATE`（升級、時戳、旁欄）→ 不受阻

**通行證非豁免**：降級仍須有可稽核之理由帳（如 `knowhow_depth_reevaluation`）；
本閘僅使其「不可無痕」，不代替留痕義務。

執行指令矩陣
------------
    python3 scripts/migrate_admit_state_guard_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_admit_state_guard_ddl.py --check    # 唯讀驗證
    python3 scripts/migrate_admit_state_guard_ddl.py --apply    # 掛 trigger（冪等）
    python3 scripts/migrate_admit_state_guard_ddl.py --selftest # 紅綠自測（免 DB 免 API）

⚠ **apply 時序**：層級推進（`run_knowhow_auto_admit.py`）進行中亦可 apply——本閘不阻升級路徑。
   惟若同時有降級作業在跑（如 `reevaluate_kh_depths.py`），須待其收槍或確認其已帶通行證。
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

GUC = "augur.admit_depth_lower"

DDL = """
CREATE OR REPLACE FUNCTION admit_state_guard() RETURNS trigger AS $$
DECLARE
    _pass text := current_setting('augur.admit_depth_lower', true);
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：DELETE 一律拒絕（只得改深度並留帳）';
    END IF;
    IF TG_OP = 'UPDATE'
       AND NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL
       AND NEW.admit_depth < OLD.admit_depth THEN
        IF _pass IS DISTINCT FROM 'on' THEN
            RAISE EXCEPTION
              'admit_depth 下降（% → %）＝撤銷既有准入宣稱：須通行證 '
              '(SET LOCAL augur.admit_depth_lower = ''on'') 且須留理由帳',
              OLD.admit_depth, NEW.admit_depth;
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION admit_state_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：TRUNCATE 一律拒絕';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_admit_state_guard ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_guard
    BEFORE UPDATE OR DELETE ON knowhow_auto_admit_state
    FOR EACH ROW EXECUTE FUNCTION admit_state_guard();

DROP TRIGGER IF EXISTS trg_admit_state_no_truncate ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_no_truncate
    BEFORE TRUNCATE ON knowhow_auto_admit_state
    FOR EACH STATEMENT EXECUTE FUNCTION admit_state_no_truncate();
"""


def check(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.knowhow_auto_admit_state')")
    if not cur.fetchone()[0]:
        print("FAIL knowhow_auto_admit_state 不存在")
        return 1
    cur.execute(
        """SELECT tgname FROM pg_trigger
            WHERE tgrelid='knowhow_auto_admit_state'::regclass AND NOT tgisinternal ORDER BY 1"""
    )
    trg = [r[0] for r in cur.fetchall()]
    print(f"trigger：{trg or '✗ 無（任何人可靜默改准入深度，而深度為引文排序鍵）'}")
    ok = "trg_admit_state_guard" in trg and "trg_admit_state_no_truncate" in trg
    print("PASS 誠實閘就位（降級／刪除須通行證）" if ok else "FAIL 未就位（跑 --apply）")
    return 0 if ok else 1


def apply(conn) -> int:
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    print("已掛 trigger（冪等）；升級路徑不受阻、降級與刪除須通行證")
    return check(conn)


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    chk("DELETE 一律拒絕", "DELETE 一律拒絕" in DDL)
    chk("TRUNCATE 一律拒絕", "BEFORE TRUNCATE" in DDL and "TRUNCATE 一律拒絕" in DDL)
    chk("只鎖降級（含 < 比較）", "NEW.admit_depth < OLD.admit_depth" in DDL)
    chk("通行證名一致", GUC in DDL)
    chk("NULL 安全（兩側 IS NOT NULL 前置）",
        "NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL" in DDL)
    chk("升級不受阻（無 > 或 <> 之全面攔截）",
        "NEW.admit_depth > OLD.admit_depth" not in DDL and "IS DISTINCT FROM OLD.admit_depth" not in DDL)
    chk("錯誤訊息含舊值→新值（可稽核）", "% → %" in DDL)
    chk("冪等（DROP TRIGGER IF EXISTS 前置）", DDL.count("DROP TRIGGER IF EXISTS") == 2)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="knowhow_auto_admit_state 誠實閘（DDL；冪等）")
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
