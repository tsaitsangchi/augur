#!/usr/bin/env python
"""arena 前置 admission GATE DDL — arena_admission_gate 建表+挪門柱 trigger(arena 前置 G1-G5 計畫 §5.1/§6.1)。

🎯 這支在做什麼(白話):arena 開賽前置(G1 資料對帳+G2 anti-leakage 迴歸)之通過判準物件——鏡射
   prediction_unfreeze_gate(已退史料)之挪門柱紀律,但帶 **axis 消歧**(shared_foundation/direction/
   relative_strength、D-2 軸別落地)+**supersedes_gate_id** retry 鏈(D-3/G5)。機械強制:①非 draft 後
   criteria 不可變;②凍結後簽核欄鎖定;③狀態轉移白名單(draft→frozen|superseded;frozen→evaluated_*
   |superseded;終態不可回改);非 draft 不得刪(廢止=superseded 留痕)。判準值人拍板(approved_by 留痕)。
   唯記錄面、不進預測管線。

守 #6(冪等)· #15(挪門柱=RAISE)· #12(DDL 單一住所=本檔;trigger 邏輯鏡射 trg_unfreeze_no_goalpost)
   · #10(superseded+supersedes_gate_id=完整審計軌)。SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md §5.1/§6.1。

執行指令矩陣:
  python scripts/migrate_arena_admission_gate_ddl.py            # 無參數:現況(唯讀)
  python scripts/migrate_arena_admission_gate_ddl.py --run      # 冪等建表+trigger+自參照 FK
  python scripts/migrate_arena_admission_gate_ddl.py --verify   # 表+trigger+axis/supersedes 欄存在斷言(exit 0/1)
  python scripts/migrate_arena_admission_gate_ddl.py --selftest # 挪門柱 trigger 紅綠(adhoc 假列、測畢 superseded 留痕)
"""
import argparse
import json
import sys
import uuid

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS arena_admission_gate (
  gate_id            text PRIMARY KEY,
  axis               text NOT NULL
                       CHECK (axis IN ('shared_foundation','direction','relative_strength')),
  purpose            text,
  criteria           jsonb NOT NULL,
  criteria_sha       text  NOT NULL,
  status             text  NOT NULL DEFAULT 'draft'
                       CHECK (status IN ('draft','frozen','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at   timestamptz NOT NULL DEFAULT now(),
  approved_by        text,
  approved_at        timestamptz,
  git_sha            text,
  evaluated_at       timestamptz,
  result_snapshot    jsonb,
  evaluation_ref     text,
  supersedes_gate_id text REFERENCES arena_admission_gate(gate_id),
  note               text,
  CONSTRAINT chk_aag_frozen_signed CHECK
    (status <> 'frozen' OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)),
  CONSTRAINT chk_aag_evaluated_stamped CHECK
    (status NOT IN ('evaluated_pass','evaluated_fail')
     OR (approved_at IS NOT NULL AND evaluated_at IS NOT NULL))
);

CREATE OR REPLACE FUNCTION arena_admission_no_goalpost() RETURNS trigger AS $$
DECLARE legal boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status <> 'draft' THEN
      RAISE EXCEPTION 'arena admission gate %: 非 draft 不得刪(留痕;廢止=status superseded)', OLD.gate_id;
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.status <> 'draft'
     AND (NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha
          OR NEW.criteria::text IS DISTINCT FROM OLD.criteria::text) THEN
    RAISE EXCEPTION 'arena admission gate %: 已凍結,criteria 不得變更(挪門柱);另立新 gate、舊列 superseded', OLD.gate_id;
  END IF;
  IF OLD.status <> 'draft' AND OLD.approved_at IS NOT NULL
     AND (NEW.approved_by IS DISTINCT FROM OLD.approved_by
          OR NEW.approved_at IS DISTINCT FROM OLD.approved_at) THEN
    RAISE EXCEPTION 'arena admission gate %: 凍結後簽核欄不得改', OLD.gate_id;
  END IF;
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    legal := (OLD.status = 'draft'  AND NEW.status IN ('frozen','superseded'))
          OR (OLD.status = 'frozen' AND NEW.status IN ('evaluated_pass','evaluated_fail','superseded'));
    IF NOT legal THEN
      RAISE EXCEPTION 'arena admission gate %: 非法狀態轉移 % → %(白名單:draft→frozen|superseded;frozen→evaluated_*|superseded;終態不可回改,複核=另立新 gate)',
        OLD.gate_id, OLD.status, NEW.status;
    END IF;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_arena_admission_no_goalpost ON arena_admission_gate;
CREATE TRIGGER trg_arena_admission_no_goalpost
  BEFORE UPDATE OR DELETE ON arena_admission_gate
  FOR EACH ROW EXECUTE FUNCTION arena_admission_no_goalpost();

COMMENT ON TABLE arena_admission_gate IS
  'arena 開賽前置 admission GATE(G1 對帳+G2 anti-leakage;鏡射 unfreeze gate 挪門柱紀律):axis 消歧軸別(D-2)、supersedes_gate_id retry 鏈(D-3);挪門柱=trigger 白名單拒+CLI exit 1;判準值人拍板;唯記錄面、不進預測管線';
"""


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(DDL)
        conn.commit()
    print("✓ --run 完成(冪等):arena_admission_gate + trg_arena_admission_no_goalpost + supersedes 自參照 FK 就位")
    return 0


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.arena_admission_gate') IS NOT NULL")
        t = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='trg_arena_admission_no_goalpost'")
        g = cur.fetchone()[0] > 0
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_name='arena_admission_gate' "
                    "AND column_name IN ('axis','supersedes_gate_id')")
        cols = cur.fetchone()[0] == 2
    ok = bool(t and g and cols)
    print(f"{'✓' if ok else '✗'} verify:表={t} trigger={g} axis+supersedes 欄={cols}")
    return 0 if ok else 1


def selftest():
    """挪門柱 trigger 紅綠(adhoc 假列,測畢 superseded 留痕;#15 回歸鎖)。"""
    fails = 0
    with db.connect() as conn:
        cur = conn.cursor()
        gid = f"arena_selftest_{uuid.uuid4().hex[:8]}"
        cur.execute("INSERT INTO arena_admission_gate (gate_id,axis,purpose,criteria,criteria_sha,git_sha) "
                    "VALUES (%s,'shared_foundation','adhoc',%s,%s,'selftest')",
                    (gid, json.dumps({"t": 1}), "selftest"))
        conn.commit()
        # (1) draft→evaluated_pass 非法(白名單:draft 僅可→frozen/superseded)
        try:
            cur.execute("UPDATE arena_admission_gate SET status='evaluated_pass' WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest1:draft→evaluated_pass 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest1:draft→evaluated_pass 被拒")
        # (2) 凍結後改 criteria 非法(挪門柱)
        cur.execute("UPDATE arena_admission_gate SET status='frozen', approved_by='selftest', approved_at=now() "
                    "WHERE gate_id=%s", (gid,))
        conn.commit()
        try:
            cur.execute("UPDATE arena_admission_gate SET criteria=%s WHERE gate_id=%s", (json.dumps({"t": 2}), gid))
            conn.commit(); print("✗ selftest2:凍後改 criteria 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest2:凍後改 criteria 被拒(挪門柱)")
        # (3) frozen→draft 兩步降級非法
        try:
            cur.execute("UPDATE arena_admission_gate SET status='draft' WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest3:frozen→draft 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest3:frozen→draft 降級被拒")
        # (4) 非 draft 不得刪(留痕)
        try:
            cur.execute("DELETE FROM arena_admission_gate WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest4:frozen 列被刪"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest4:非 draft 不得刪")
        # cleanup:frozen→superseded 合法(廢止留痕)
        cur.execute("UPDATE arena_admission_gate SET status='superseded' WHERE gate_id=%s", (gid,))
        conn.commit()
        print(f"(selftest 假列 {gid} 已 superseded 留痕)")
    print(f"═> selftest {'全過 ✓' if fails == 0 else f'{fails} 敗 ✗'}")
    return 0 if fails == 0 else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.run:
        return run()
    if args.verify:
        return verify()
    if args.selftest:
        return selftest()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.arena_admission_gate')")
        if cur.fetchone()[0]:
            cur.execute("SELECT gate_id, axis, status, approved_by FROM arena_admission_gate "
                        "ORDER BY preregistered_at DESC LIMIT 5")
            rows = cur.fetchall()
            print("現況:", rows if rows else "(表在、零列)")
        else:
            print("現況:(表未建,先 --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
