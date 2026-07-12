#!/usr/bin/env python
"""方向產物表 fail-closed 機械閘 + 輸出契約補欄(憲章 v1.45.0 輸出契約條之 DB 落地)。

🎯 這支在做什麼(白話):direction_probability / daily_direction_probability 兩張產物表掛
   BEFORE INSERT/UPDATE trigger——對應 direction_gate 非 evaluated_pass 一律拒寫(fail-closed
   下沉為 DB 不變式,不靠腳本自律);並補 expected_ret / hit_rate 兩欄(三產物閉集承載)。

守 #6(冪等)· #12(DDL 單一住所)· 憲章 v1.45.0(輸出契約:fail-closed 須為 trigger 級機械閘)。

執行指令矩陣:
  python scripts/migrate_direction_product_gate_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_direction_product_gate_ddl.py --run     # 冪等落 DDL+trigger
  python scripts/migrate_direction_product_gate_ddl.py --verify  # 交易內負向測試(必 ROLLBACK)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
ALTER TABLE direction_probability       ADD COLUMN IF NOT EXISTS expected_ret double precision;
ALTER TABLE direction_probability       ADD COLUMN IF NOT EXISTS hit_rate     double precision;
ALTER TABLE daily_direction_probability ADD COLUMN IF NOT EXISTS expected_ret double precision;
ALTER TABLE daily_direction_probability ADD COLUMN IF NOT EXISTS hit_rate     double precision;

CREATE OR REPLACE FUNCTION direction_product_gate_guard() RETURNS trigger AS $$
DECLARE st text;
BEGIN
  SELECT status INTO st FROM direction_gate WHERE gate_id = NEW.gate_id;
  IF st IS DISTINCT FROM 'evaluated_pass' THEN
    RAISE EXCEPTION 'fail-closed(憲章 v1.45.0 輸出契約):gate % 狀態 %(須 evaluated_pass)不得寫產物表',
      NEW.gate_id, COALESCE(st, '不存在');
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_dirprob_gate_guard ON direction_probability;
CREATE TRIGGER trg_dirprob_gate_guard BEFORE INSERT OR UPDATE ON direction_probability
  FOR EACH ROW EXECUTE FUNCTION direction_product_gate_guard();
DROP TRIGGER IF EXISTS trg_ddirprob_gate_guard ON daily_direction_probability;
CREATE TRIGGER trg_ddirprob_gate_guard BEFORE INSERT OR UPDATE ON daily_direction_probability
  FOR EACH ROW EXECUTE FUNCTION direction_product_gate_guard();
"""


def status(cur):
    cur.execute("SELECT tgname FROM pg_trigger WHERE tgname LIKE '%gate_guard%' AND NOT tgisinternal")
    trigs = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_name IN "
                "('direction_probability','daily_direction_probability') AND column_name IN ('expected_ret','hit_rate')")
    cols = cur.fetchone()[0]
    print(f"trigger:{trigs or '未掛'};契約欄:{cols}/4")


def verify(cur):
    """交易內負向測試:引 evaluated_fail 門與不存在門各插一列,兩者皆須被 trigger 拒——無條件 ROLLBACK。"""
    cur.execute("SELECT gate_id FROM direction_gate WHERE status='evaluated_fail' LIMIT 1")
    row = cur.fetchone()
    fail_gate = row[0] if row else "gate_not_exist"
    ok = 0
    for gid, label in [(fail_gate, "evaluated_fail 門"), ("no_such_gate_xyz", "不存在門")]:
        cur.execute("SAVEPOINT sp")
        try:
            cur.execute(
                "INSERT INTO direction_probability (panel_date, model_id, target_id, horizon, p_up, "
                "base_rate, calendar_days, calibrator_id, econ_verdict, gate_id) "
                "SELECT '2026-06-30', model_id, 'TEST', 40, 0.5, 0.5, 60, 'test_cal', 'dead', %s "
                "FROM model_registry LIMIT 1", (gid,))
            print(f"✗ {label}:未被攔(fail-closed 破)")
        except Exception:
            ok += 1
            print(f"✓ {label}:trigger 拒寫")
        cur.execute("ROLLBACK TO SAVEPOINT sp")
    print("(正向路徑無 evaluated_pass 門可測——誠實留待首個 pass 門)" )
    return ok == 2


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.run:
            cur.execute(DDL)
            conn.commit()
            print("✓ 契約欄+gate guard trigger 就位(冪等)")
            status(cur)
            return 0
        if args.verify:
            passed = verify(cur)
            conn.rollback()
            return 0 if passed else 1
        status(cur)
        print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
