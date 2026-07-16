#!/usr/bin/env python
"""擂台對局 — 逐候選出方向機率落 ledger(arena plan §2.3;A0=合成冒煙、A2 後=live cron 入口)。

🎯 這支在做什麼(白話):兩模式——
   **--smoke-synthetic(A0;FREEZE 內唯一合法模式)**:合成隨機漫步序列(SYNTH_*)餵每個 adapter,
   驗介面/shape/OOM;**不碰任何真實價格、不落任何 DB 列、不輸出任何真實股票之 p_up**(grep 驗收)。
   **--run(A2 後)**:讀 live 價格→各 active 候選出手→寫 direction_arena_prediction(反回填 trigger
   守真未來)。**前置雙機械閘(AND;先凍後跑,同 daily_pipeline 縱深防禦)**:閘一=direction_gate
   dgate_arena% approved;閘二=arena_admission_gate shared_foundation evaluated_pass(G1+G2 硬前置,
   G1-G5 計畫 §3.3;fail-closed 表缺=拒)。任一關即拒跑。

守 #8/#15(先凍後跑機械閘)· #25(冒煙=合成最小樣)· #28(本地)· #29a/d。SSOT=arena plan §2.3/§6。

執行指令矩陣:
  python scripts/run_arena_round.py                        # 無參數:候選與 ledger 現況(唯讀)
  python scripts/run_arena_round.py --smoke-synthetic      # A0 合成冒煙(零 DB 寫、零真實資料)
  python scripts/run_arena_round.py --smoke-synthetic --adapters majority momentum_20
  python scripts/run_arena_round.py --run                  # live 對局(A2 後;gate approved 機械閘)
"""
import argparse
import sys
import time

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db


def smoke_synthetic(only):
    """合成隨機漫步 × 全 adapter:驗 shape/範圍/OOM。零 DB、零真實資料、零真實股票代號。"""
    from augur.arena.adapters import REGISTRY
    rng = np.random.default_rng(7)
    series = {}
    for i in range(8):                                     # 8 條合成序列、600 點
        r = rng.normal(0.0003, 0.02, 600)
        series[f"SYNTH_{i}"] = (100 * np.cumprod(1 + r)).tolist()
    keys = only or list(REGISTRY)
    ok = True
    for key in keys:
        t0 = time.time()
        try:
            adapter = REGISTRY[key]()
            out = adapter.predict(series, 5)
            vals = np.array(list(out.values()), float)
            good = (len(out) >= 1 and np.isfinite(vals).all()
                    and (vals >= 0).all() and (vals <= 1).all()
                    and all(k.startswith("SYNTH_") for k in out))
            print(f"  {'✓' if good else '✗'} {key:<20} n={len(out)} p∈[{vals.min():.3f},{vals.max():.3f}] "
                  f"{time.time()-t0:.1f}s")
            ok &= good
        except Exception as e:
            print(f"  ✗ {key:<20} {type(e).__name__}: {str(e)[:90]}(operational 除名事由留痕)")
            ok = False
    print(f"{'✓ 合成冒煙全過(零 DB 寫、零真實 p_up)' if ok else '⚠ 部分 adapter 未過(誠實留痕;不阻其他隊)'}")
    return 0 if ok else 1


def live_round():
    """live 對局(A2 後):as-of=最新已落地交易日;D 軌每日、H 軌每月首個交易日出手;
    寫 ledger(反回填/不可篡改 trigger 機械守護;ON CONFLICT DO NOTHING=同日重跑冪等)。"""
    import datetime
    import subprocess
    from pathlib import Path
    from augur.arena.adapters import REGISTRY
    git7 = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                          cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM direction_gate WHERE gate_id LIKE 'dgate_arena%%' AND status='approved'")
        if not cur.fetchone()[0]:
            print("✗ live 對局拒跑:arena direction_gate 未預註冊+核准(先凍後跑,arena plan §1 門二)。\n"
                  "  前置鏈:arena_admission_gate G1-G2 evaluated_pass → dgate_arena hugo TTY approve。")
            return 1
        cur.execute("SELECT to_regclass('public.arena_admission_gate')")   # 閘二(縱深防禦,同 daily_pipeline;fail-closed 表缺=拒)
        adm_n = 0
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM arena_admission_gate "
                        "WHERE axis='shared_foundation' AND status='evaluated_pass'")
            adm_n = cur.fetchone()[0]
        if not adm_n:
            print("✗ live 對局拒跑:arena_admission_gate G1-G2 硬前置未 evaluated_pass(G1-G5 計畫 §3.3;"
                  "fail-closed——preregister → hugo --freeze → evaluate;unfreeze GATE 已退史料)。")
            return 1
        cur.execute('SELECT max(date) FROM "TaiwanStockPriceAdj"')
        as_of = cur.fetchone()[0]
        if (datetime.date.today() - as_of).days > 7:
            print(f"✗ 資料過舊(最新 {as_of});先跑每日管線 sync"); return 1
        cur.execute("SELECT date FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' "
                    "AND date >= %s AND date <= %s ORDER BY date",
                    (as_of.replace(day=1), as_of))
        month_days = [r[0] for r in cur.fetchall()]
        h_fires = month_days and month_days[0] == as_of      # H 軌=每月首個交易日出手(月頻 cadence)
        cur.execute("SELECT as_of_date FROM core_universe_asof WHERE as_of_date <= %s "
                    "ORDER BY as_of_date DESC LIMIT 1", (as_of,))
        snap = cur.fetchone()[0]
        cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date = %s", (snap,))
        uni = [r[0] for r in cur.fetchall()]
        cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
            WHERE stock_id = ANY(%s) AND date <= %s AND date >= %s ORDER BY stock_id, date""",
            (uni, as_of, str(as_of - datetime.timedelta(days=900))))
        series = {}
        for sid, d_, c_ in cur.fetchall():
            series.setdefault(sid, []).append(float(c_))
        cur.execute("SELECT price FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' "
                    "AND date <= %s AND date >= %s ORDER BY date",
                    (as_of, str(as_of - datetime.timedelta(days=900))))
        series["TAIEX"] = [float(r[0]) for r in cur.fetchall()]
        series = {k: v for k, v in series.items() if len(v) >= 120}
        print(f"as-of={as_of} 宇宙 {len(series)-1} 檔(+TAIEX);H 軌出手={h_fires}")

        cur.execute("SELECT model_key, track, spec FROM direction_arena_candidate WHERE status='active'")
        total = 0
        for mk, track, spec in cur.fetchall():
            if track == "H" and not h_fires:
                continue
            if mk not in REGISTRY:
                print(f"  ⤳ {mk}: 無 adapter(對照列/未接線)—誠實缺席"); continue
            horizons = (spec or {}).get("horizons", [5])
            try:
                adapter = REGISTRY[mk]()
                for h in horizons:
                    out = adapter.predict(series, h)
                    rows = [(mk, t, as_of, h, float(p), as_of,
                             as_of + datetime.timedelta(days=int(h * 1.6) + 3), git7)
                            for t, p in out.items() if t != "TAIEX" or track == "H"]
                    from psycopg2.extras import execute_values
                    execute_values(cur, """INSERT INTO direction_arena_prediction
                        (model_key, target_id, pred_date, horizon_td, p_up, train_data_max_date, label_due_est, git_sha)
                        VALUES %s ON CONFLICT (model_key, target_id, pred_date, horizon_td) DO NOTHING""", rows)
                    conn.commit()
                    total += len(rows)
                    print(f"  ✓ {mk} h={h}: {len(rows)} 筆出手", flush=True)
            except Exception as e:
                conn.rollback()
                print(f"  ✗ {mk}: {type(e).__name__}: {str(e)[:80]}—誠實缺席(operational 留痕)")
        print(f"✓ 對局落 ledger {total} 列(產出僅入帳本、不進 UI;gate 前零展示)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_candidate')")
        if not cur.fetchone()[0]:
            print("(表未建;先 migrate_direction_arena_ddl.py --run)")
        else:
            cur.execute("SELECT count(*), count(*) FILTER (WHERE status='active') FROM direction_arena_candidate")
            c, a = cur.fetchone()
            cur.execute("SELECT count(*), count(settled_at) FROM direction_arena_prediction")
            p, s = cur.fetchone()
            print(f"候選 {c}(active {a});ledger {p} 列(已結算 {s})")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--smoke-synthetic", action="store_true", dest="smoke")
    ap.add_argument("--adapters", nargs="*")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        return smoke_synthetic(args.adapters)
    if args.run:
        return live_round()
    return status()


if __name__ == "__main__":
    sys.exit(main())
