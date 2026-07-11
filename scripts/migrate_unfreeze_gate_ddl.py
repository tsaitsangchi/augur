#!/usr/bin/env python
"""解凍 GATE DDL — prediction_unfreeze_gate 建表+挪門柱 trigger(驗證總綱 V2 缺口③)。

🎯 這支在做什麼(白話):FREEZE 解凍(接新資料/live 再驗證)的通過判準**現在凍結**——鏡射 B2
   bench_batch 精神:先凍結後評估、不挪門柱。機械強制三件:①非 draft 後 criteria 不可變;
   ②凍結後簽核欄鎖定;③狀態轉移白名單(堵 frozen→draft 兩步降級);非 draft 不得刪(廢止=superseded
   留痕)。判準值=人拍板(approved_by 留痕,CHECK 強制 frozen 必有簽核)。唯記錄面、不進預測管線。

守 #6(冪等)· #15(挪門柱=RAISE)· #12(DDL 單一住所=本檔)· #10(superseded 鏈=完整審計軌)。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §4.1。

執行指令矩陣:
  python scripts/migrate_unfreeze_gate_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_unfreeze_gate_ddl.py --run     # 冪等建表+trigger
  python scripts/migrate_unfreeze_gate_ddl.py --verify  # 表+trigger 存在斷言(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS prediction_unfreeze_gate (
  gate_id          text PRIMARY KEY,
  purpose          text NOT NULL DEFAULT 'unfreeze'
                     CHECK (purpose IN ('unfreeze','adhoc')),
  criteria         jsonb NOT NULL,
  criteria_sha     text  NOT NULL,
  status           text  NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft','frozen','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  approved_by      text,
  approved_at      timestamptz,
  git_sha          text NOT NULL,
  evaluated_at     timestamptz,
  result_snapshot  jsonb,
  evaluation_ref   text,
  note             text,
  CONSTRAINT chk_ug_frozen_signed CHECK
    (status <> 'frozen' OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)),
  CONSTRAINT chk_ug_eval_signed CHECK
    (status NOT IN ('evaluated_pass','evaluated_fail')
     OR (approved_at IS NOT NULL AND evaluated_at IS NOT NULL))
);

CREATE OR REPLACE FUNCTION unfreeze_gate_no_goalpost() RETURNS trigger AS $$
DECLARE legal boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status <> 'draft' THEN
      RAISE EXCEPTION 'unfreeze gate %: 非 draft 不得刪(留痕;廢止=status superseded)', OLD.gate_id;
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.status <> 'draft'
     AND (NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha
          OR NEW.criteria::text IS DISTINCT FROM OLD.criteria::text) THEN
    RAISE EXCEPTION 'unfreeze gate %: 已凍結,criteria 不得變更(挪門柱);另立新 gate、舊列 superseded', OLD.gate_id;
  END IF;
  IF OLD.status <> 'draft' AND OLD.approved_at IS NOT NULL
     AND (NEW.approved_by IS DISTINCT FROM OLD.approved_by
          OR NEW.approved_at IS DISTINCT FROM OLD.approved_at) THEN
    RAISE EXCEPTION 'unfreeze gate %: 凍結後簽核欄不得改', OLD.gate_id;
  END IF;
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    legal := (OLD.status = 'draft'  AND NEW.status IN ('frozen','superseded'))
          OR (OLD.status = 'frozen' AND NEW.status IN ('evaluated_pass','evaluated_fail','superseded'));
    IF NOT legal THEN
      RAISE EXCEPTION 'unfreeze gate %: 非法狀態轉移 % → %(白名單:draft→frozen|superseded;frozen→evaluated_*|superseded;終態不可回改,複核=另立新 gate)',
        OLD.gate_id, OLD.status, NEW.status;
    END IF;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_unfreeze_no_goalpost ON prediction_unfreeze_gate;
CREATE TRIGGER trg_unfreeze_no_goalpost
  BEFORE UPDATE OR DELETE ON prediction_unfreeze_gate
  FOR EACH ROW EXECUTE FUNCTION unfreeze_gate_no_goalpost();

COMMENT ON TABLE prediction_unfreeze_gate IS
  'FREEZE 解凍 GATE 預註冊(鏡射 deliberation_bench_batch B2):判準先凍結後評估,挪門柱=trigger 狀態白名單拒+CLI exit 1;判準值人拍板(approved_by 留痕);唯記錄面、不進預測管線';
"""


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(DDL)
        conn.commit()
    print("✓ --run 完成(冪等):prediction_unfreeze_gate + trg_unfreeze_no_goalpost 就位")
    return 0


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.prediction_unfreeze_gate') IS NOT NULL")
        t = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='trg_unfreeze_no_goalpost'")
        g = cur.fetchone()[0] > 0
    ok = t and g
    print(f"{'✓' if ok else '✗'} verify:表={t} trigger={g}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.run:
        return run()
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.prediction_unfreeze_gate')")
        if cur.fetchone()[0]:
            cur.execute("SELECT gate_id, status, preregistered_at::date FROM prediction_unfreeze_gate ORDER BY preregistered_at DESC LIMIT 5")
            rows = cur.fetchall()
            print("現況:", rows if rows else "(表在、零列)")
        else:
            print("現況:(表未建,先 --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
