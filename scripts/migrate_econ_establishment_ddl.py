#!/usr/bin/env python
"""經濟確立閘 DDL — econ_establishment_gate + econ_eval_run（#14 路徑 E0）。

🎯 這支在做什麼（白話）：給「怎樣才算證明能賺錢」一個可證偽載體——判準先寫死
   （preregistered）→ 人 approve → 跑數字 → evaluate。挪門柱＝trigger 機械拒。
   評估跑次只追加、禁改禁刪。本支只建表＋trigger，**不**插入閘列、不跑經濟、
   不改 econ_verdict_rule、不碰 direction_gate 列。

   對齊 reports/augur_econ_prove_edge_plan_r17_20260817.md §6／§8 E0。
   evaluated_pass ≠ 已改 verdict；AI 禁寫 established。

守 #6（冪等）· #12（DDL 單一住所；horizon CHECK＝closed_horizons.CHECK_ANY）·
   #14（經濟確立記錄面、不進預測管線）· #15（挪門柱 RAISE；敗退留檔）· #26（approve 須簽核）。

執行指令矩陣:
  python scripts/migrate_econ_establishment_ddl.py           # 無參數:現況（唯讀）
  python scripts/migrate_econ_establishment_ddl.py --run     # 冪等建表+trigger
  python scripts/migrate_econ_establishment_ddl.py --verify  # 表+trigger+突變斷言（exit 0/1）
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
import psycopg2
from augur.core import db
from augur.core.closed_horizons import CHECK_ANY

H_ANY = "ARRAY[" + ", ".join(str(h) for h in CHECK_ANY) + "]"

DDL_GATE = f"""
CREATE TABLE IF NOT EXISTS econ_establishment_gate (
  gate_id          text PRIMARY KEY,
  horizon          integer NOT NULL,
  family           text NOT NULL,
  purpose          text NOT NULL,
  criteria         jsonb NOT NULL,
  criteria_sha     text NOT NULL,
  status           text NOT NULL DEFAULT 'preregistered' CHECK (status IN
    ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  approved_by      text, approved_at timestamptz,
  evaluated_at     timestamptz,
  result_snapshot  jsonb,
  evaluation_ref   text,
  git_sha          text NOT NULL,
  note             text,
  CONSTRAINT chk_eg_horizon CHECK (horizon = ANY ({H_ANY})),
  CONSTRAINT chk_eg_approved_signed CHECK
    (status NOT IN ('approved','evaluated_pass','evaluated_fail')
     OR (approved_by IS NOT NULL AND approved_at IS NOT NULL))
);

CREATE OR REPLACE FUNCTION econ_establishment_gate_no_goalpost() RETURNS trigger AS $$
DECLARE legal boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status <> 'preregistered' THEN
      RAISE EXCEPTION 'econ establishment gate %: 非 preregistered 不得刪(敗退留檔;廢止=superseded)', OLD.gate_id;
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.status <> 'preregistered'
     AND (NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha
          OR NEW.criteria::text IS DISTINCT FROM OLD.criteria::text) THEN
    RAISE EXCEPTION 'econ establishment gate %: 已核准,criteria 不得變更(挪門柱);另立新 gate、舊列 superseded', OLD.gate_id;
  END IF;
  IF OLD.status IN ('evaluated_pass','evaluated_fail')
     AND (NEW.result_snapshot::text IS DISTINCT FROM OLD.result_snapshot::text
          OR NEW.evaluated_at IS DISTINCT FROM OLD.evaluated_at
          OR NEW.evaluation_ref IS DISTINCT FROM OLD.evaluation_ref
          OR NEW.git_sha IS DISTINCT FROM OLD.git_sha) THEN
    RAISE EXCEPTION 'econ establishment gate %: 終態列判決快照凍結(result_snapshot/evaluated_at/evaluation_ref/git_sha 不可改寫)', OLD.gate_id;
  END IF;
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    legal := (OLD.status = 'preregistered' AND NEW.status IN ('approved','superseded'))
          OR (OLD.status = 'approved'      AND NEW.status IN ('evaluated_pass','evaluated_fail','superseded'));
    IF NOT legal THEN
      RAISE EXCEPTION 'econ establishment gate %: 非法狀態轉移 % → %(白名單:preregistered→approved|superseded;approved→evaluated_*|superseded;終態不可回改)',
        OLD.gate_id, OLD.status, NEW.status;
    END IF;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_econ_establishment_no_goalpost ON econ_establishment_gate;
CREATE TRIGGER trg_econ_establishment_no_goalpost
  BEFORE UPDATE OR DELETE ON econ_establishment_gate
  FOR EACH ROW EXECUTE FUNCTION econ_establishment_gate_no_goalpost();

COMMENT ON TABLE econ_establishment_gate IS
  '#14 經濟確立賭注載體:判準先凍→人 approve→evaluate;挪門柱=trigger 拒;evaluated_pass ≠ 已改 econ_verdict_rule;AI 禁寫 established;唯記錄面、不進預測管線';
"""

DDL_RUN = """
CREATE TABLE IF NOT EXISTS econ_eval_run (
  run_id           bigserial PRIMARY KEY,
  run_at           timestamptz NOT NULL DEFAULT now(),
  run_kind         text NOT NULL CHECK (run_kind IN ('research','establishment')),
  gate_id          text REFERENCES econ_establishment_gate(gate_id),
  feature_source   text NOT NULL CHECK (feature_source IN ('prodset','canonical')),
  model            text NOT NULL,
  horizon          integer NOT NULL,
  top_frac         double precision NOT NULL,
  weight           text NOT NULL,
  cost             double precision NOT NULL,
  sample_since     date NOT NULL,
  universe         text NOT NULL,
  n_periods        integer,
  periods_per_year double precision,
  net_sharpe       double precision,
  bench_sharpe     double precision,
  net_excess       double precision,
  avg_turnover     double precision,
  dsr              double precision,
  n_trials         integer,
  panel_hash       text,
  paid_n           boolean NOT NULL DEFAULT false,
  git_sha          text,
  note             text,
  CONSTRAINT chk_eer_horizon CHECK (horizon = ANY (""" + H_ANY + """)),
  CONSTRAINT chk_eer_est_gate CHECK (run_kind <> 'establishment' OR gate_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS econ_eval_run_kind_h_src
  ON econ_eval_run (run_kind, horizon, feature_source);

CREATE OR REPLACE FUNCTION econ_eval_run_append_only() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'econ_eval_run: 只追加(禁 UPDATE/DELETE)';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_econ_eval_run_append_only ON econ_eval_run;
CREATE TRIGGER trg_econ_eval_run_append_only
  BEFORE UPDATE OR DELETE ON econ_eval_run
  FOR EACH ROW EXECUTE FUNCTION econ_eval_run_append_only();

COMMENT ON TABLE econ_eval_run IS
  '#14 經濟評估跑次只追加;research 預設不付 N;establishment 必填 gate_id;不回寫預測管線、不改 econ_verdict_rule';
"""


def run() -> int:
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(DDL_GATE)
        cur.execute(DDL_RUN)
        conn.commit()
    print("✓ --run 完成（冪等）:econ_establishment_gate + econ_eval_run + 兩支 trigger")
    return 0


def _exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{name}",))
    return bool(cur.fetchone()[0])


def _trigger_exists(cur, name: str) -> bool:
    cur.execute("SELECT count(*)>0 FROM pg_trigger WHERE tgname=%s AND NOT tgisinternal", (name,))
    return bool(cur.fetchone()[0])


def _status(cur) -> None:
    g = _exists(cur, "econ_establishment_gate")
    r = _exists(cur, "econ_eval_run")
    print(f"econ_establishment_gate: {'在' if g else '未建'}")
    print(f"econ_eval_run: {'在' if r else '未建'}")
    if g:
        cur.execute("SELECT count(*), coalesce(string_agg(gate_id, ',' ORDER BY gate_id), '') FROM econ_establishment_gate")
        n, ids = cur.fetchone()
        print(f"  閘列數={n}" + (f" ids={ids}" if ids else "（空——E1 才預註冊）"))
        cur.execute(
            "SELECT count(*)>0 FROM pg_trigger WHERE tgname='trg_econ_establishment_no_goalpost' AND NOT tgisinternal"
        )
        print(f"  trg_econ_establishment_no_goalpost={bool(cur.fetchone()[0])}")
    if r:
        cur.execute("SELECT count(*) FROM econ_eval_run")
        print(f"  跑次列數={cur.fetchone()[0]}")
        cur.execute(
            "SELECT count(*)>0 FROM pg_trigger WHERE tgname='trg_econ_eval_run_append_only' AND NOT tgisinternal"
        )
        print(f"  trg_econ_eval_run_append_only={bool(cur.fetchone()[0])}")
    cur.execute("SELECT count(*) FROM direction_gate")
    print(f"direction_gate 列數={cur.fetchone()[0]}（E0 不得增刪）")
    cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
    print("econ_verdict_rule:", list(cur.fetchall()))


def _mutation_tests() -> list[str]:
    """未提交交易內探 trigger；結束一律 rollback。失敗理由回傳 list（空＝過）。"""
    fails: list[str] = []
    with db.connect() as conn:
        conn.autocommit = False
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO econ_establishment_gate
                  (gate_id, horizon, family, purpose, criteria, criteria_sha, git_sha, note)
                VALUES
                  ('__e0_mut_probe__', 60, 'RankRidge', 'E0 mutation probe',
                   '{"probe":true}'::jsonb, 'probe_sha_0', 'e0-mut', 'verify-only; rolled back')
                """
            )
            cur.execute(
                """
                UPDATE econ_establishment_gate
                   SET criteria='{"probe":1}'::jsonb, criteria_sha='probe_sha_1'
                 WHERE gate_id='__e0_mut_probe__'
                """
            )
            cur.execute(
                """
                UPDATE econ_establishment_gate
                   SET status='approved', approved_by='mut', approved_at=now()
                 WHERE gate_id='__e0_mut_probe__'
                """
            )
            cur.execute("SAVEPOINT s_criteria")
            try:
                cur.execute(
                    """
                    UPDATE econ_establishment_gate
                       SET criteria='{"probe":2}'::jsonb, criteria_sha='probe_sha_2'
                     WHERE gate_id='__e0_mut_probe__'
                    """
                )
                fails.append("已核准後改 criteria 未被拒")
            except psycopg2.Error as e:
                msg = str(e)
                if "挪門柱" not in msg:
                    fails.append(f"改 criteria 拒了但訊息不含挪門柱: {msg[:160]}")
                cur.execute("ROLLBACK TO SAVEPOINT s_criteria")

            cur.execute("SAVEPOINT s_status")
            try:
                cur.execute(
                    """
                    UPDATE econ_establishment_gate
                       SET status='preregistered'
                     WHERE gate_id='__e0_mut_probe__'
                    """
                )
                fails.append("approved→preregistered 未被拒")
            except psycopg2.Error:
                cur.execute("ROLLBACK TO SAVEPOINT s_status")

            cur.execute("SAVEPOINT s_del")
            try:
                cur.execute("DELETE FROM econ_establishment_gate WHERE gate_id='__e0_mut_probe__'")
                fails.append("刪 approved 閘未被拒")
            except psycopg2.Error:
                cur.execute("ROLLBACK TO SAVEPOINT s_del")

            cur.execute(
                """
                INSERT INTO econ_eval_run
                  (run_kind, feature_source, model, horizon, top_frac, weight, cost,
                   sample_since, universe, note)
                VALUES
                  ('research', 'prodset', 'RankRidge', 60, 0.1, 'LO', 0.00585,
                   '2014-01-01', 'asof_incumbent', 'e0 mut probe')
                """
            )
            cur.execute("SAVEPOINT s_run")
            try:
                cur.execute("UPDATE econ_eval_run SET note='tamper' WHERE note='e0 mut probe'")
                fails.append("econ_eval_run UPDATE 未被拒")
            except psycopg2.Error as e:
                if "只追加" not in str(e):
                    fails.append(f"eval_run UPDATE 拒了但訊息不含只追加: {str(e)[:160]}")
                cur.execute("ROLLBACK TO SAVEPOINT s_run")

            cur.execute("SAVEPOINT s_h82")
            try:
                cur.execute(
                    """
                    INSERT INTO econ_establishment_gate
                      (gate_id, horizon, family, purpose, criteria, criteria_sha, git_sha)
                    VALUES
                      ('__e0_mut_h82__', 82, 'RankRidge', 'must fail', '{}'::jsonb, 'x', 'e0-mut')
                    """
                )
                fails.append("horizon=82 未被 CHECK 拒")
            except psycopg2.Error:
                cur.execute("ROLLBACK TO SAVEPOINT s_h82")
        finally:
            conn.rollback()
    return fails


def verify() -> int:
    with db.connect() as conn, db.transaction(conn) as cur:
        g = _exists(cur, "econ_establishment_gate")
        r = _exists(cur, "econ_eval_run")
        tg = _trigger_exists(cur, "trg_econ_establishment_no_goalpost")
        tr = _trigger_exists(cur, "trg_econ_eval_run_append_only")
        cur.execute("SELECT count(*) FROM econ_establishment_gate")
        n_gate = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM econ_eval_run")
        n_run = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM direction_gate")
        n_dgate = cur.fetchone()[0]
        cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
        verdicts = list(cur.fetchall())
        cur.execute(
            """
            SELECT pg_get_constraintdef(c.oid)
              FROM pg_constraint c
             WHERE c.conrelid='econ_establishment_gate'::regclass
               AND c.conname='chk_eg_horizon'
            """
        )
        hchk = (cur.fetchone() or [""])[0]

    print(f"表 gate={g} run={r} | trigger no_goalpost={tg} append_only={tr}")
    print(f"列數 gate={n_gate} run={n_run} | direction_gate={n_dgate}")
    print(f"econ_verdict_rule={verdicts}")
    print(f"chk_eg_horizon={hchk}")

    ok = g and r and tg and tr
    if not ok:
        print("✗ verify:表或 trigger 缺席")
        return 1
    if "82" in (hchk or ""):
        print("✗ verify:horizon CHECK 含 82")
        return 1
    for h in CHECK_ANY:
        if str(h) not in (hchk or ""):
            print(f"✗ verify:horizon CHECK 缺 {h}")
            return 1

    fails = _mutation_tests()
    if fails:
        print("✗ 突變測試失敗:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("✓ 突變:已核准改 criteria 拒／非法狀態拒／刪 approved 拒／eval_run 只追加／H82 CHECK 拒")

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM econ_establishment_gate")
        n_gate2 = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM econ_eval_run")
        n_run2 = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM direction_gate")
        n_dgate2 = cur.fetchone()[0]
        cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
        verdicts2 = list(cur.fetchall())
    if (n_gate2, n_run2) != (n_gate, n_run):
        print(f"✗ 突變後列數漂移 gate {n_gate}→{n_gate2} run {n_run}→{n_run2}")
        return 1
    if n_dgate2 != n_dgate:
        print(f"✗ direction_gate 列數變了 {n_dgate}→{n_dgate2}")
        return 1
    if verdicts2 != verdicts:
        print("✗ econ_verdict_rule 變了")
        return 1
    print("✓ verify:兩表＋兩 trigger＋突變＋dgate/verdict 未動")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="經濟確立閘 DDL（E0；冪等）")
    ap.add_argument("--run", action="store_true", help="冪等建表+trigger")
    ap.add_argument("--verify", action="store_true", help="表+trigger+突變斷言")
    args = ap.parse_args()
    if args.run:
        return run()
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        _status(cur)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
