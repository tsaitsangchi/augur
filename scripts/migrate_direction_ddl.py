#!/usr/bin/env python
"""預言機軸 schema — H/D 兩軌 9 表冪等落地(oracle 主計畫 §7.1;direction_gate 住 migrate_direction_gate_ddl.py)。

🎯 這支在做什麼(白話):建預言機軸(憲章 v1.42.0)的承載表——
   H 軌:market_direction_feature(市場特徵,#8 visible_date 逐欄)/market_direction_probability(大盤方向機率)/
   direction_probability(個股+top3/5 絕對方向機率,gate_id 硬綁+base_rate 硬綁)/direction_oos_sample(審計);
   D 軌:daily_direction_feature_values(日頻面板,晚生特徵誠實 NULL)/daily_direction_probability/
   daily_direction_oos_sample;另 mc_simulation_run(is_simulation DB 級硬綁「模擬非預測」)+
   freeze_manifest(快照版本化,P4-1 觸發前空表)。全部唯 GATE 過後才進 UI(展示分級閉集)。

守 #6(冪等)· #8(visible_date)· #10(git_sha/溯源)· #12(DDL 單一住所)· 憲章 v1.42.0 預言機誠實判準。

執行指令矩陣:
  python scripts/migrate_direction_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_direction_ddl.py --run     # 冪等建 9 表
  python scripts/migrate_direction_ddl.py --verify  # 斷言 9 表+關鍵 CHECK(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLES = ("market_direction_feature", "market_direction_probability", "direction_probability",
          "direction_oos_sample", "daily_direction_feature_values", "daily_direction_probability",
          "daily_direction_oos_sample", "mc_simulation_run", "freeze_manifest")

DDL = [
    ("H① market_direction_feature", """
        CREATE TABLE IF NOT EXISTS market_direction_feature (
          panel_date date NOT NULL, feature text NOT NULL,
          value double precision NOT NULL,
          source_table text NOT NULL,
          visible_date date NOT NULL,
          git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (panel_date, feature))"""),
    ("H② market_direction_probability", """
        CREATE TABLE IF NOT EXISTS market_direction_probability (
          panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
          horizon integer NOT NULL, p_mkt_up double precision NOT NULL CHECK (p_mkt_up BETWEEN 0 AND 1),
          calibrator_id text, git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (panel_date, model_id, horizon))"""),
    ("H③ direction_probability", """
        CREATE TABLE IF NOT EXISTS direction_probability (
          panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
          target_id text NOT NULL,
          horizon integer NOT NULL, p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
          base_rate double precision NOT NULL,
          calendar_days integer NOT NULL,
          calibrator_id text, econ_verdict text NOT NULL,
          gate_id text NOT NULL REFERENCES direction_gate(gate_id),
          created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (panel_date, model_id, target_id, horizon))"""),
    ("H④ direction_oos_sample", """
        CREATE TABLE IF NOT EXISTS direction_oos_sample (
          model_id text NOT NULL, target_id text NOT NULL, panel_date date NOT NULL,
          horizon integer NOT NULL, p_up double precision NOT NULL,
          y_up smallint NOT NULL CHECK (y_up IN (0,1)), fwd_abs_ret double precision,
          fold_id integer NOT NULL, seed integer NOT NULL,
          git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (model_id, target_id, panel_date, horizon, seed))"""),
    ("D① daily_direction_feature_values", """
        CREATE TABLE IF NOT EXISTS daily_direction_feature_values (
          panel_date date NOT NULL, target_id text NOT NULL, feature text NOT NULL,
          value double precision, PRIMARY KEY (panel_date, target_id, feature))"""),
    ("D② daily_direction_probability", """
        CREATE TABLE IF NOT EXISTS daily_direction_probability (
          panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
          target_id text NOT NULL, k_td integer NOT NULL CHECK (k_td IN (1,5)),
          p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
          base_rate double precision NOT NULL, calibrator_id text,
          econ_verdict text NOT NULL,
          gate_id text NOT NULL REFERENCES direction_gate(gate_id),
          created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (panel_date, model_id, target_id, k_td))"""),
    ("D③ daily_direction_oos_sample", """
        CREATE TABLE IF NOT EXISTS daily_direction_oos_sample (
          model_id text NOT NULL, target_id text NOT NULL, panel_date date NOT NULL,
          k_td integer NOT NULL, p_up double precision NOT NULL,
          y_up smallint NOT NULL CHECK (y_up IN (0,1)),
          fold_id integer NOT NULL, seed integer NOT NULL,
          created_at timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (model_id, target_id, panel_date, k_td, seed))"""),
    ("mc_simulation_run(模擬非預測 DB 級硬綁)", """
        CREATE TABLE IF NOT EXISTS mc_simulation_run (
          run_id text PRIMARY KEY, target_id text NOT NULL, asof_date date NOT NULL,
          horizon_td integer NOT NULL,
          method text NOT NULL CHECK (method IN ('iid_bootstrap','block_bootstrap')),
          block_len_td integer, n_paths integer NOT NULL, seed integer NOT NULL,
          summary jsonb NOT NULL,
          is_simulation boolean NOT NULL DEFAULT true CHECK (is_simulation),
          git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now())"""),
    ("freeze_manifest(P4-1 觸發前空表)", """
        CREATE TABLE IF NOT EXISTS freeze_manifest (
          snapshot_version integer PRIMARY KEY,
          asof_freeze date NOT NULL DEFAULT '2026-05-31',
          change_desc text NOT NULL, approved_by text NOT NULL,
          row_delta bigint, dump_ref text, created_at timestamptz NOT NULL DEFAULT now())"""),
    ("comment direction_probability", """
        COMMENT ON TABLE direction_probability IS
        '預言機軸 H 軌(憲章 v1.42.0):P(絕對報酬>0|as-of,H);gate_id 硬綁=唯 direction_gate 過 GATE 者可服務(展示分級閉集);base_rate=同窗多數類基線硬綁;禁單股準確率;FREEZE 內=歷史 OOS 非 live'"""),
    ("comment daily_direction_probability", """
        COMMENT ON TABLE daily_direction_probability IS
        '預言機軸 D 軌(憲章 v1.42.0):次日/k 日方向機率(k∈{1,5} 封閉);econ_verdict 預期 dead 硬綁呈現;逐日價格點位/路徑永久除外(無 GATE 可解)'"""),
]


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        for name, sql in DDL:
            cur.execute(sql)
            print(f"  ✓ {name}")
        conn.commit()
    print("✓ --run 完成(冪等)")
    return 0


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                    "AND table_name = ANY(%s)", (list(TABLES),))
        have = {r[0] for r in cur.fetchall()}
        missing = [t for t in TABLES if t not in have]
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname LIKE '%is_simulation%' OR "
                    "conrelid='mc_simulation_run'::regclass AND contype='c'")
        ok = not missing
        print(f"{'✓' if ok else '✗'} verify:9 表 {len(have)}/9" + (f";缺 {missing}" if missing else ""))
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
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                    "AND table_name = ANY(%s) ORDER BY 1", (list(TABLES),))
        for r in cur.fetchall():
            cur.execute(f'SELECT count(*) FROM "{r[0]}"')
            print(f"  ✓ {r[0]}({cur.fetchone()[0]} 列)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
