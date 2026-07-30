#!/usr/bin/env python3
"""🎯 KH10 准入 gate 表之機械閘——三治權欄之變更須通行證，且 DELETE/TRUNCATE 一律拒。

守原則 #15（誠實：帳不可被靜默改）、#20（決策層人拍板）。

起因（2026-07-30 獨立核驗 F-bypass-3）：`knowhow_auto_admit_gate` **無任何 trigger**、
`augur` 角色具 UPDATE 權，故 `require_kh8`／`require_kh9`／`max_auto_depth` 三欄
可被**一句 UPDATE 廢止**——而該三欄正是 KH8／KH9 證據要件之開關。核驗實跑：
`UPDATE ... SET require_kh8=false, max_auto_depth=10` → rowcount=1 無阻擋，
隨即使 depth-9 item 在 **KH8 全程未評**（prior_depth）之下升至 depth 10。

處置（同 honesty guard 之既成形式）：
  - DELETE／TRUNCATE：一律 RAISE（gate 為治權組態，不得刪）
  - UPDATE 三治權欄（require_kh8／require_kh9／max_auto_depth）：須 GUC 通行證
    `SET LOCAL augur.kh_gate_change = 'on'`；其餘欄（enabled／channels 等）不受限
  - 任何三欄之變更均寫入 `knowhow_auto_admit_gate_change`（append-only 異動帳）

**通行證非豁免**：三欄之變更依 `AUGUR-MC v1.6 §P5.W5`／大憲章 v1.51.0 通則二 (a)
屬**放寬類**（減少證據要件）者，須走 `governance_proposal` 人簽；本閘僅使其
「不可無痕」，不代替人簽。

執行指令矩陣
------------
    python3 scripts/migrate_kh_gate_guard_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_kh_gate_guard_ddl.py --check    # 唯讀驗證（trigger/表是否就位）
    python3 scripts/migrate_kh_gate_guard_ddl.py --apply    # 建異動帳表＋掛三 trigger（冪等）
    python3 scripts/migrate_kh_gate_guard_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401  # 個別可執行（CLAUDE #29a）

GUARD_COLS = ("require_kh8", "require_kh9", "max_auto_depth")

DDL_CHANGELOG = """
CREATE TABLE IF NOT EXISTS knowhow_auto_admit_gate_change (
    change_id     BIGSERIAL PRIMARY KEY,
    changed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by    TEXT NOT NULL,
    col           TEXT NOT NULL,
    old_value     TEXT,
    new_value     TEXT,
    proposal_ref  TEXT,
    CONSTRAINT kh_gate_change_col_ck CHECK (col IN ('require_kh8','require_kh9','max_auto_depth'))
);
"""

DDL_FUNC = """
CREATE OR REPLACE FUNCTION kh_gate_guard() RETURNS trigger AS $$
DECLARE
    _pass text := current_setting('augur.kh_gate_change', true);
    _who  text := coalesce(current_setting('augur.change_actor', true), current_user);
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'knowhow_auto_admit_gate 為治權組態：DELETE 一律拒絕';
    END IF;
    IF TG_OP = 'UPDATE' THEN
        IF (NEW.require_kh8 IS DISTINCT FROM OLD.require_kh8)
           OR (NEW.require_kh9 IS DISTINCT FROM OLD.require_kh9)
           OR (NEW.max_auto_depth IS DISTINCT FROM OLD.max_auto_depth) THEN
            IF _pass IS DISTINCT FROM 'on' THEN
                RAISE EXCEPTION
                  'require_kh8/require_kh9/max_auto_depth 為證據要件開關：變更須通行證 '
                  '(SET LOCAL augur.kh_gate_change = ''on'')，且放寬類須走 governance_proposal 人簽';
            END IF;
            IF NEW.require_kh8 IS DISTINCT FROM OLD.require_kh8 THEN
                INSERT INTO knowhow_auto_admit_gate_change (changed_by, col, old_value, new_value)
                VALUES (_who, 'require_kh8', OLD.require_kh8::text, NEW.require_kh8::text);
            END IF;
            IF NEW.require_kh9 IS DISTINCT FROM OLD.require_kh9 THEN
                INSERT INTO knowhow_auto_admit_gate_change (changed_by, col, old_value, new_value)
                VALUES (_who, 'require_kh9', OLD.require_kh9::text, NEW.require_kh9::text);
            END IF;
            IF NEW.max_auto_depth IS DISTINCT FROM OLD.max_auto_depth THEN
                INSERT INTO knowhow_auto_admit_gate_change (changed_by, col, old_value, new_value)
                VALUES (_who, 'max_auto_depth', OLD.max_auto_depth::text, NEW.max_auto_depth::text);
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION kh_gate_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'knowhow_auto_admit_gate 為治權組態：TRUNCATE 一律拒絕';
END $$ LANGUAGE plpgsql;
"""

DDL_TRIGGERS = """
DROP TRIGGER IF EXISTS trg_kh_gate_guard ON knowhow_auto_admit_gate;
CREATE TRIGGER trg_kh_gate_guard
    BEFORE UPDATE OR DELETE ON knowhow_auto_admit_gate
    FOR EACH ROW EXECUTE FUNCTION kh_gate_guard();

DROP TRIGGER IF EXISTS trg_kh_gate_no_truncate ON knowhow_auto_admit_gate;
CREATE TRIGGER trg_kh_gate_no_truncate
    BEFORE TRUNCATE ON knowhow_auto_admit_gate
    FOR EACH STATEMENT EXECUTE FUNCTION kh_gate_no_truncate();
"""


def check(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.knowhow_auto_admit_gate')")
    if not cur.fetchone()[0]:
        print("FAIL knowhow_auto_admit_gate 不存在")
        return 1
    cur.execute("SELECT to_regclass('public.knowhow_auto_admit_gate_change')")
    has_log = cur.fetchone()[0] is not None
    cur.execute(
        """SELECT tgname FROM pg_trigger
            WHERE tgrelid='knowhow_auto_admit_gate'::regclass AND NOT tgisinternal
            ORDER BY 1"""
    )
    trg = [r[0] for r in cur.fetchall()]
    print(f"異動帳表：{'✓' if has_log else '✗ 未建'}")
    print(f"trigger：{trg or '✗ 無（一句 UPDATE 即可廢止證據要件）'}")
    ok = has_log and "trg_kh_gate_guard" in trg and "trg_kh_gate_no_truncate" in trg
    print("PASS 機械閘就位" if ok else "FAIL 機械閘未就位（跑 --apply）")
    return 0 if ok else 1


def apply(conn) -> int:
    cur = conn.cursor()
    cur.execute(DDL_CHANGELOG)
    cur.execute(DDL_FUNC)
    cur.execute(DDL_TRIGGERS)
    conn.commit()
    print("已建異動帳表＋掛三 trigger（冪等）")
    return check(conn)


def _selftest() -> int:
    fails = []
    if set(GUARD_COLS) != {"require_kh8", "require_kh9", "max_auto_depth"}:
        fails.append("GUARD_COLS 不符三治權欄")
    for frag in ("DELETE 一律拒絕", "augur.kh_gate_change", "governance_proposal"):
        if frag not in DDL_FUNC:
            fails.append(f"DDL 缺關鍵語義：{frag}")
    for col in GUARD_COLS:
        if col not in DDL_FUNC:
            fails.append(f"DDL 未涵蓋欄 {col}")
    if "BEFORE TRUNCATE" not in DDL_TRIGGERS:
        fails.append("缺 TRUNCATE trigger")
    if "IS DISTINCT FROM" not in DDL_FUNC:
        fails.append("未用 IS DISTINCT FROM（NULL 比較會漏判）")
    for f in fails:
        print(f"FAIL {f}")
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KH10 gate 表機械閘（DDL；冪等）")
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
        print("--- 無參數＝--check（唯讀）---")
    sys.exit(main())
