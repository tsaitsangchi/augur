#!/usr/bin/env python
"""擂台對局 — 逐候選出方向機率落 ledger(arena plan §2.3;A0=合成冒煙、A2 後=live cron 入口)。

🎯 這支在做什麼(白話):兩模式——
   **--smoke-synthetic(A0;FREEZE 內唯一合法模式)**:合成隨機漫步序列(SYNTH_*)餵每個 adapter,
   驗介面/shape/OOM;**不碰任何真實價格、不落任何 DB 列、不輸出任何真實股票之 p_up**(grep 驗收)。
   **--run(A2 後)**:讀 live 價格→各 active 候選出手→寫 direction_arena_prediction(反回填 trigger
   守真未來)。**前置機械閘:arena direction_gate 列存在且 status=approved(先凍後跑),否則拒跑**
   ——FREEZE 解凍前此模式必拒。

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
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM direction_gate WHERE gate_id LIKE 'dgate_arena%%' AND status='approved'")
        if not cur.fetchone()[0]:
            print("✗ live 對局拒跑:arena direction_gate 未預註冊+核准(先凍後跑,arena plan §1 門二)。\n"
                  "  前置鏈:A-2 解凍修憲 → unfreeze GATE evaluate pass → A2 預註冊 arena gate(hugo TTY)。")
            return 1
    print("(gate 已核——live 對局路徑於 A2 實作完成後啟用)")
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
