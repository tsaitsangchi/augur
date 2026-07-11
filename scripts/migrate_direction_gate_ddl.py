#!/usr/bin/env python
"""方向 GATE DDL — direction_gate 建表+挪門柱 trigger(預言機主計畫 §2.6/§7.1;H/D 兩軌預註冊)。

🎯 這支在做什麼(白話):H 軌(絕對走向機率)與 D 軌(逐日方向機率)的可證偽賭注載體——判準先寫死
   (preregistered)→ 決策層人 approve → 跑數字 → evaluate;**挪門柱=trigger 機械拒**(非 preregistered
   後 criteria 不可變/狀態白名單/approve 須簽核/唯 preregistered 可刪)。兩軌 gate 獨立(track CHECK);
   ECE 門檻等引 judgestop DB 值(#12 不寫死)。鏡射 prediction_unfreeze_gate 前例。

守 #6(冪等)· #15(挪門柱 RAISE;敗退路徑=evaluated_fail 留檔永不出 UI)· #12(DDL 單一住所)· #26(approve 唯人)。
   SSOT=reports/augur_oracle_upgrade_master_plan_20260711.md §0.4/§2.6。

執行指令矩陣:
  python scripts/migrate_direction_gate_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_direction_gate_ddl.py --run     # 冪等建表+trigger
  python scripts/migrate_direction_gate_ddl.py --verify  # 表+trigger 斷言(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS direction_gate (
  gate_id          text PRIMARY KEY,
  track            text NOT NULL CHECK (track IN ('H','D')),
  horizon          integer NOT NULL,
  purpose          text NOT NULL,
  criteria         jsonb NOT NULL,
  criteria_sha     text NOT NULL,
  status           text NOT NULL DEFAULT 'preregistered' CHECK (status IN
    ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  approved_by      text, approved_at timestamptz,
  evaluated_at     timestamptz, result_snapshot jsonb, evaluation_ref text,
  git_sha          text NOT NULL, note text,
  CONSTRAINT chk_dg_approved_signed CHECK
    (status NOT IN ('approved','evaluated_pass','evaluated_fail')
     OR (approved_by IS NOT NULL AND approved_at IS NOT NULL))
);

CREATE OR REPLACE FUNCTION direction_gate_no_goalpost() RETURNS trigger AS $$
DECLARE legal boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status <> 'preregistered' THEN
      RAISE EXCEPTION 'direction gate %: 非 preregistered 不得刪(敗退留檔;廢止=superseded)', OLD.gate_id;
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.status <> 'preregistered'
     AND (NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha
          OR NEW.criteria::text IS DISTINCT FROM OLD.criteria::text) THEN
    RAISE EXCEPTION 'direction gate %: 已核准,criteria 不得變更(挪門柱);另立新 gate、舊列 superseded', OLD.gate_id;
  END IF;
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    legal := (OLD.status = 'preregistered' AND NEW.status IN ('approved','superseded'))
          OR (OLD.status = 'approved'      AND NEW.status IN ('evaluated_pass','evaluated_fail','superseded'));
    IF NOT legal THEN
      RAISE EXCEPTION 'direction gate %: 非法狀態轉移 % → %(白名單:preregistered→approved|superseded;approved→evaluated_*|superseded;終態不可回改)',
        OLD.gate_id, OLD.status, NEW.status;
    END IF;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_direction_no_goalpost ON direction_gate;
CREATE TRIGGER trg_direction_no_goalpost
  BEFORE UPDATE OR DELETE ON direction_gate
  FOR EACH ROW EXECUTE FUNCTION direction_gate_no_goalpost();

COMMENT ON TABLE direction_gate IS
  '預言機方向可證偽賭注載體(H/D 兩軌獨立;主計畫 §0.4):判準先寫死→人 approve→evaluate;挪門柱=trigger 拒;fail=判死留檔永不出 UI(展示分級閉集 §1.2);唯記錄面、不進預測管線';
"""


def run():
    with db.connect() as conn:
        conn.cursor().execute(DDL)
        conn.commit()
    print("✓ --run 完成(冪等):direction_gate + trg_direction_no_goalpost 就位")
    return 0


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_gate') IS NOT NULL")
        t = cur.fetchone()[0]
        cur.execute("SELECT count(*)>0 FROM pg_trigger WHERE tgname='trg_direction_no_goalpost'")
        g = cur.fetchone()[0]
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
        cur.execute("SELECT to_regclass('public.direction_gate')")
        if cur.fetchone()[0]:
            cur.execute("SELECT gate_id, track, horizon, status FROM direction_gate ORDER BY preregistered_at DESC LIMIT 8")
            rows = cur.fetchall()
            print("現況:", rows if rows else "(表在、零列——判準預註冊於 O1 數字前)")
        else:
            print("現況:(表未建,先 --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
