#!/usr/bin/env python
"""arena replay 帳本遷移 — 歷史重演軌之隔離表(REPLAY-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):replay 證據軌的兩張表——arena_replay_run(一批=一模型一窗,含權重合法窗判)
   ＋direction_arena_replay(重演出單+即結)。**隔離不變式**:live 表(direction_arena_prediction)
   零觸碰;--check=交叉污染稽核(live 開賽日前 live 表必無列=兩軌天然不相交,若未來重疊即報)。
守 #8(train_data_max_date 斷言欄)· #15(--check 稽核)· #29a/d。
SSOT=reports/augur_arena_replay_plan_20260729.md §四。

執行指令矩陣:
  python scripts/migrate_arena_replay_ddl.py            # 無參數:現況(表在?各窗列數?,唯讀)
  python scripts/migrate_arena_replay_ddl.py --apply    # 遷移(冪等)
  python scripts/migrate_arena_replay_ddl.py --check    # 隔離稽核(唯讀)
  python scripts/migrate_arena_replay_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

SQL = """
CREATE TABLE IF NOT EXISTS arena_replay_run (
    replay_run_id     TEXT PRIMARY KEY,
    model_key         TEXT NOT NULL,
    window_start      DATE NOT NULL,
    window_end        DATE NOT NULL,
    weights_cutoff_ok BOOLEAN NOT NULL,
    code_sha          TEXT NOT NULL,
    spec              JSONB NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (window_start <= window_end)
);
CREATE TABLE IF NOT EXISTS direction_arena_replay (
    replay_run_id       TEXT NOT NULL REFERENCES arena_replay_run(replay_run_id),
    model_key           TEXT NOT NULL,
    target_id           TEXT NOT NULL,
    pred_date           DATE NOT NULL,
    horizon_td          INT  NOT NULL,
    p_up                NUMERIC NOT NULL CHECK (p_up >= 0 AND p_up <= 1),
    train_data_max_date DATE NOT NULL,
    y_up                INT CHECK (y_up IN (0, 1)),
    realized_ret        NUMERIC,
    settle_mode         TEXT NOT NULL CHECK (settle_mode IN ('normal', 'last_trade', 'unsettleable')),
    settled_at          TIMESTAMPTZ,        -- estimand settled_only 慣例(unsettleable=NULL)
    CHECK (train_data_max_date <= pred_date),           -- #8 洩漏硬 CHECK
    PRIMARY KEY (replay_run_id, model_key, target_id, pred_date, horizon_td)
);
CREATE INDEX IF NOT EXISTS idx_dar_model_pred ON direction_arena_replay (model_key, pred_date);
"""


def apply(dry=False):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_replay')")
        if cur.fetchone()[0] is not None:
            print("✓ 表皆在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            return 0
        cur.execute(SQL)
        print("✓ replay 兩表落地(live 表零觸碰)")
    return 0


def check():
    """隔離稽核:①replay 表對 live 表零外鍵/零寫依賴(結構性)②同 (model,pred_date,horizon) 兩軌重疊列印報(資訊,
    重疊本身合法——同模型可同日既 live 又 replay,但供人眼確認無誤植)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT count(*) FROM direction_arena_replay r
            JOIN direction_arena_prediction l USING (model_key, target_id, pred_date, horizon_td)""")
        overlap = cur.fetchone()[0]
        print(f"  兩軌同鍵重疊列:{overlap}(資訊性;live 帳本零寫入為結構保證)")
        cur.execute("""SELECT count(*) FROM direction_arena_replay
            WHERE train_data_max_date > pred_date""")
        print(f"  #8 違例(train>pred):{cur.fetchone()[0]}(應=0,另有 CHECK 雙保險)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_replay')")
        if cur.fetchone()[0] is None:
            print("  (表未建;--apply)")
            return 0
        cur.execute("""SELECT r.replay_run_id, r.model_key, r.window_start, r.window_end,
                              count(p.*) FROM arena_replay_run r
                       LEFT JOIN direction_arena_replay p USING (replay_run_id)
                       GROUP BY 1,2,3,4 ORDER BY 1""")
        rows = cur.fetchall()
        print(f"  replay 批:{len(rows)}")
        for r in rows:
            print(f"    {r[0]} {r[1]} {r[2]}→{r[3]} {r[4]:,} 列")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("#8 硬 CHECK(train≤pred)", "train_data_max_date <= pred_date" in SQL)
    chk("權重合法窗欄(weights_cutoff_ok)", "weights_cutoff_ok BOOLEAN NOT NULL" in SQL)
    chk("settle 三態 CHECK", "'unsettleable'" in SQL and "'last_trade'" in SQL)
    chk("p_up 值域 CHECK", "p_up >= 0 AND p_up <= 1" in SQL)
    chk("隔離:SQL 不觸 live 表", "direction_arena_prediction" not in SQL)
    chk("冪等", "IF NOT EXISTS" in SQL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="arena replay 帳本遷移(隔離軌)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.check:
        return check()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
