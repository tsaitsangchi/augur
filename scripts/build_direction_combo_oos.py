#!/usr/bin/env python
"""top3/top5 組合層 OOS — 等權組合方向樣本(v2 revival plan §3.5;v1 主計畫 §2.5 原文承襲)。

🎯 這支在做什麼(白話):把 DirStackM 的個股 OOS 疊成「top3/top5 等權組合」樣本——每 (horizon, 月末 panel):
   取該 panel rank_pctile 最高之 3/5 檔(相對軌 as-of picks 口徑),組合標籤 y_up=1[等權實現報酬>0]、
   組合機率 p_up=個股 p_up 等權平均(口徑明標:組合機率=成分均值近似、非獨立模型)。**每 panel 僅 1 組合
   觀測 → n≤panel 數,小樣本明標、單獨列 n;隨個股層 GATE、不得單獨解鎖**。落 direction_combo_oos_sample。

守 #9/#10(全導自 OOS 表+月頻特徵表,git_sha)· #28(本地)· #29a/d。
   前置=train_direction_stack.py --run-v2。SSOT=revival plan §3.5。

執行指令矩陣:
  python scripts/build_direction_combo_oos.py                  # 無參數:現況(唯讀)
  python scripts/build_direction_combo_oos.py --run            # H{20,40,82} × TOP3/TOP5
"""
import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

H_SET = (20, 40, 82)
MODEL_ID = "DirStackM"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def run():
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        for h in H_SET:
            cur.execute("""
                SELECT s.panel_date, s.target_id, s.p_up, s.fwd_abs_ret, f.value AS rank_pctile
                FROM direction_oos_sample s
                JOIN direction_stack_feature_monthly f
                  ON f.panel_date = s.panel_date AND f.target_id = s.target_id AND f.feature = %s
                WHERE s.model_id = %s AND s.horizon = %s AND s.fwd_abs_ret IS NOT NULL""",
                (f"rank_pctile_h{h}", MODEL_ID, h))
            by_panel = {}
            for p, sid, pu, fr, rk in cur.fetchall():
                by_panel.setdefault(p, []).append((sid, float(pu), float(fr), float(rk)))
            wrote = 0
            for p, rows in sorted(by_panel.items()):
                rows.sort(key=lambda r: r[3], reverse=True)      # 相對軌 rank 取 picks(as-of 口徑)
                for combo, k in (("TOP3", 3), ("TOP5", 5)):
                    sel = rows[:k]
                    if len(sel) < k:
                        continue
                    fr = float(np.mean([r[2] for r in sel]))
                    pu = float(np.mean([r[1] for r in sel]))
                    cur.execute(
                        "INSERT INTO direction_combo_oos_sample "
                        "(combo, horizon, panel_date, p_up, y_up, fwd_ret, model_id, seed, git_sha) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,0,%s) "
                        "ON CONFLICT (combo, horizon, panel_date, model_id, seed) DO UPDATE SET "
                        "p_up=EXCLUDED.p_up, y_up=EXCLUDED.y_up, fwd_ret=EXCLUDED.fwd_ret, "
                        "git_sha=EXCLUDED.git_sha, created_at=now()",
                        (combo, h, p, pu, 1 if fr > 0 else 0, fr, MODEL_ID, git7))
                    wrote += 1
            conn.commit()
            print(f"  H{h:<3} 組合樣本 {wrote} 列(n_panel={len(by_panel)};小樣本明標、隨個股門不單獨解鎖)")
    print("✓ 組合層完成")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_combo_oos_sample')")
        if not cur.fetchone()[0]:
            print("(表未建;先 migrate_direction_ddl.py --run)"); return 0
        cur.execute("SELECT combo, horizon, count(*) FROM direction_combo_oos_sample GROUP BY 1,2 ORDER BY 2,1")
        print("combo OOS:", cur.fetchall() or "(無)")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.run:
        return run()
    return status()


if __name__ == "__main__":
    sys.exit(main())
