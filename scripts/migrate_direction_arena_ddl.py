#!/usr/bin/env python
"""方向 Live 擂台 schema — 4 表+3 防篡改 trigger 冪等落地(arena plan §3;真未來考場之帳本層)。

🎯 這支在做什麼(白話):擂台的承載表——candidate(參賽者凍結協定:spec/code_sha/weights_hash
   insert-only)、prediction(對局帳本:**反回填 trigger** 強制 pred_date 貼緊 created_at=真未來機械保證;
   結算欄唯 NULL→值一次)、policy(futility 判停閾值,住自己表、不動 judgestop_threshold)、verdict
   (futility 三態新閉集 observing/suspected_futility/confirmed_stop_entries)。唯一既有表變更=無。
   對局產出僅落 ledger、不進 payload/UI(gate 前全系統零絕對方向數字,fail-closed)。

守 #6(冪等)· #15(反回填/不可篡改=機械非自律)· #12(DDL 單一住所)· #29a/d。
   SSOT=reports/augur_direction_live_arena_plan_20260711.md §3。

執行指令矩陣:
  python scripts/migrate_direction_arena_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_direction_arena_ddl.py --run     # 冪等建 4 表+3 trigger
  python scripts/migrate_direction_arena_ddl.py --verify  # 表+trigger+負向單測×3(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLES = ("direction_arena_candidate", "direction_arena_prediction",
          "direction_arena_policy", "direction_arena_verdict")

DDL = """
CREATE TABLE IF NOT EXISTS direction_arena_candidate (
  model_key text PRIMARY KEY,
  team text NOT NULL CHECK (team IN ('own','market','baseline')),
  track text NOT NULL CHECK (track IN ('D','H')),
  gate_eligible boolean NOT NULL,
  spec jsonb NOT NULL,
  code_sha text NOT NULL,
  weights_hash text,
  registry_model_id text REFERENCES model_registry(model_id),
  frozen_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','stopped','retired')),
  retire_note text);

CREATE TABLE IF NOT EXISTS direction_arena_prediction (
  model_key text NOT NULL REFERENCES direction_arena_candidate(model_key),
  target_id text NOT NULL,
  pred_date date NOT NULL,
  horizon_td int NOT NULL,
  p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
  train_data_max_date date,
  created_at timestamptz NOT NULL DEFAULT now(),
  label_due_est date,
  y_up smallint CHECK (y_up IN (0,1)),
  realized_ret double precision,
  settle_mode text CHECK (settle_mode IN ('normal','last_trade','unsettleable')),
  settled_at timestamptz,
  git_sha text NOT NULL,
  PRIMARY KEY (model_key, target_id, pred_date, horizon_td));

CREATE TABLE IF NOT EXISTS direction_arena_policy (
  policy_key text PRIMARY KEY,
  threshold double precision NOT NULL,
  frozen boolean NOT NULL DEFAULT true,
  source_ref text NOT NULL);

CREATE TABLE IF NOT EXISTS direction_arena_verdict (
  as_of_date date NOT NULL,
  model_key text NOT NULL REFERENCES direction_arena_candidate(model_key),
  state text NOT NULL CHECK (state IN ('observing','suspected_futility','confirmed_stop_entries')),
  metric_snapshot jsonb NOT NULL,
  threshold_source text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (as_of_date, model_key));

-- trigger①:candidate 凍結協定(insert-only;唯 status 轉移與 retire_note 單次寫)
CREATE OR REPLACE FUNCTION arena_candidate_frozen() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'arena candidate %: 參賽列不得刪(退役=status retired 留檔)', OLD.model_key;
  END IF;
  IF NEW.model_key IS DISTINCT FROM OLD.model_key OR NEW.team IS DISTINCT FROM OLD.team
     OR NEW.track IS DISTINCT FROM OLD.track OR NEW.gate_eligible IS DISTINCT FROM OLD.gate_eligible
     OR NEW.spec::text IS DISTINCT FROM OLD.spec::text OR NEW.code_sha IS DISTINCT FROM OLD.code_sha
     OR NEW.weights_hash IS DISTINCT FROM OLD.weights_hash
     OR NEW.registry_model_id IS DISTINCT FROM OLD.registry_model_id
     OR NEW.frozen_at IS DISTINCT FROM OLD.frozen_at THEN
    RAISE EXCEPTION 'arena candidate %: 凍結協定——spec/身分欄不得變更(換版=新候選新列)', OLD.model_key;
  END IF;
  IF OLD.retire_note IS NOT NULL AND NEW.retire_note IS DISTINCT FROM OLD.retire_note THEN
    RAISE EXCEPTION 'arena candidate %: retire_note 僅得單次寫入', OLD.model_key;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_arena_candidate_frozen ON direction_arena_candidate;
CREATE TRIGGER trg_arena_candidate_frozen
  BEFORE UPDATE OR DELETE ON direction_arena_candidate
  FOR EACH ROW EXECUTE FUNCTION arena_candidate_frozen();

-- trigger②:反回填(真未來機械保證——pred_date 貼緊 created_at,堵 horizon 內補插偷看)
CREATE OR REPLACE FUNCTION arena_pred_no_backfill() RETURNS trigger AS $$
BEGIN
  IF NEW.pred_date < ((now() AT TIME ZONE 'Asia/Taipei')::date - 1) THEN
    RAISE EXCEPTION 'arena prediction: 反回填鎖——pred_date % 早於台北今日−1(斷檔=無列、不補跑)', NEW.pred_date;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_arena_pred_no_backfill ON direction_arena_prediction;
CREATE TRIGGER trg_arena_pred_no_backfill
  BEFORE INSERT ON direction_arena_prediction
  FOR EACH ROW EXECUTE FUNCTION arena_pred_no_backfill();

-- trigger③:對局列不可篡改(預測欄禁改;結算欄唯 NULL→值一次)
CREATE OR REPLACE FUNCTION arena_pred_immutable() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'arena prediction: 對局列不得刪(帳本永存)';
  END IF;
  IF NEW.p_up IS DISTINCT FROM OLD.p_up OR NEW.pred_date IS DISTINCT FROM OLD.pred_date
     OR NEW.created_at IS DISTINCT FROM OLD.created_at
     OR NEW.train_data_max_date IS DISTINCT FROM OLD.train_data_max_date
     OR NEW.model_key IS DISTINCT FROM OLD.model_key OR NEW.target_id IS DISTINCT FROM OLD.target_id
     OR NEW.horizon_td IS DISTINCT FROM OLD.horizon_td THEN
    RAISE EXCEPTION 'arena prediction: 預測欄凍結(p_up/pred_date/created_at/... 不可改)';
  END IF;
  IF (OLD.y_up IS NOT NULL AND NEW.y_up IS DISTINCT FROM OLD.y_up)
     OR (OLD.realized_ret IS NOT NULL AND NEW.realized_ret IS DISTINCT FROM OLD.realized_ret)
     OR (OLD.settled_at IS NOT NULL AND NEW.settled_at IS DISTINCT FROM OLD.settled_at) THEN
    RAISE EXCEPTION 'arena prediction: 結算欄唯 NULL→值一次(已結算不得改寫)';
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_arena_pred_immutable ON direction_arena_prediction;
CREATE TRIGGER trg_arena_pred_immutable
  BEFORE UPDATE OR DELETE ON direction_arena_prediction
  FOR EACH ROW EXECUTE FUNCTION arena_pred_immutable();
"""


def run():
    with db.connect() as conn:
        conn.cursor().execute(DDL)
        conn.commit()
    print("✓ --run 完成(冪等):arena 4 表+3 trigger 就位")
    return 0


def verify():
    """表+trigger 存在斷言,加三個負向單測(全在交易內、無條件 ROLLBACK 零落地)。"""
    ok = True
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = ANY(%s)", (list(TABLES),))
        n = cur.fetchone()[0]
        print(f"{'✓' if n == 4 else '✗'} 表 {n}/4")
        ok &= n == 4
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_arena%'")
        t = cur.fetchone()[0]
        print(f"{'✓' if t == 3 else '✗'} trigger {t}/3")
        ok &= t == 3

    def _expect_raise(sql_setup, sql_attack, needle, label):
        with db.connect() as conn:
            cur = conn.cursor()
            hit = False
            try:
                for s in sql_setup:
                    cur.execute(s)
                cur.execute(sql_attack)
            except Exception as e:
                hit = needle in str(e)
                if not hit:
                    print(f"   (非預期錯誤:{str(e)[:80]})")
            finally:
                conn.rollback()
            print(f"{'✓' if hit else '✗'} 負向:{label}")
            return hit

    seed = ["INSERT INTO direction_arena_candidate (model_key, team, track, gate_eligible, spec, code_sha) "
            "VALUES ('__t', 'baseline', 'D', false, '{}', 'x')"]
    ok &= _expect_raise(seed, "UPDATE direction_arena_candidate SET spec='{\"a\":1}' WHERE model_key='__t'",
                        "凍結協定", "candidate spec 不可改")
    ok &= _expect_raise(seed, "INSERT INTO direction_arena_prediction (model_key, target_id, pred_date, "
                        "horizon_td, p_up, git_sha) VALUES ('__t','X','2020-01-01',5,0.5,'x')",
                        "反回填鎖", "prediction 反回填")
    ok &= _expect_raise(seed + ["INSERT INTO direction_arena_prediction (model_key, target_id, pred_date, "
                        "horizon_td, p_up, git_sha) VALUES ('__t','X',(now() AT TIME ZONE 'Asia/Taipei')::date,5,0.5,'x')"],
                        "UPDATE direction_arena_prediction SET p_up=0.9 WHERE model_key='__t'",
                        "預測欄凍結", "prediction p_up 不可改")
    print(f"{'✓ verify 全過' if ok else '✗ verify 未過'}")
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
        for t in TABLES:
            cur.execute("SELECT to_regclass('public.'||%s)", (t,))
            if cur.fetchone()[0]:
                cur.execute(f"SELECT count(*) FROM {t}")
                print(f"  ✓ {t}({cur.fetchone()[0]} 列)")
            else:
                print(f"  ✗ {t}(未建,先 --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
