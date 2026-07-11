#!/usr/bin/env python
"""蒙地卡羅模擬情境 — 逐日價格路徑之「模擬非預測」分位錐(oracle 主計畫 §3.8;憲章 v1.42.0 §1.2)。

🎯 這支在做什麼(白話):憲法唯一允許回應「未來逐日股價變化」的形式——**不是預測、是模擬**。對 target 的
   as-of(≤FREEZE)歷史日報酬做 **純歷史重抽**(iid bootstrap + block bootstrap〔區塊 21td〕雙法並列),
   模 n_paths=10,000 條 h 交易日路徑 → 逐日分位錐(p5/25/50/75/95)+ 終值分布 + 模擬統計 P(終值>0)。
   **關鍵誠實(§3.8):不以任何模型預測 tilt 抽樣**(純歷史重抽、杜絕「模擬夾帶預測」);中位路徑之走向
   純由該股自身歷史報酬分布決定、非方向模型之判斷(方向模型六門已判死)。seed 顯式入庫可重現。
   **四鎖**:①摘要硬綁 disclaimer「模擬非預測」;②只存 summary 分位錐、**絕不存逐路徑為預測資料**;
   ③模擬數字不入 chat payload(僅 /simulate 頁呈現;此為資料產生器);④憲章 §1.2 明文。is_simulation DB 硬綁 true。

守 §1.2 憲章(逐日價格路徑唯以模擬呈現)· #8(僅用 ≤as-of 歷史)· #9(來源 PriceAdj 可溯)· #15(不夾帶預測)· #28 · #29a/d。
   前置=TaiwanStockPriceAdj。SSOT=oracle 主計畫 §3.8。

執行指令矩陣:
  python scripts/simulate_mc_paths.py                                # 無參數:現況(唯讀:已存 run)
  python scripts/simulate_mc_paths.py --run --stocks 2330            # 2330,預設 horizon{21,42,63,126}雙法
  python scripts/simulate_mc_paths.py --run --stocks 2330 --horizons 30    # 指定 30 交易日
  python scripts/simulate_mc_paths.py --run --stocks 2330 2317 2454 --horizons 30 --n-paths 10000 --seed 42
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

FREEZE = "2026-05-31"
DEFAULT_HORIZONS = (21, 42, 63, 126)
HIST_WINDOW_TD = 756          # 歷史重抽窗:近 3 年(反映當前波動 regime;#8 僅 ≤as-of)
BLOCK_LEN = 21
PCTS = (5, 25, 50, 75, 95)
DISCLAIMER = "蒙地卡羅模擬情境(模擬非預測):歷史日報酬純重抽之情境統計,非模型預測;方向不可預測,中位走向僅反映該股歷史分布。"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _hist_logrets(cur, stock, asof, window):
    """該股 ≤asof 之日對數報酬(近 window td;#8 不看未來)。回 (last_close, np.array logrets)。"""
    cur.execute("""SELECT date, close FROM "TaiwanStockPriceAdj"
        WHERE stock_id=%s AND date <= %s AND close > 0 ORDER BY date DESC LIMIT %s""",
        (stock, asof, window + 1))
    rows = cur.fetchall()[::-1]                       # 升冪
    if len(rows) < 60:
        return None, None
    close = np.array([float(c) for _, c in rows])
    logr = np.diff(np.log(close))
    return float(close[-1]), logr


def _simulate(logr, h, n_paths, method, block_len, rng):
    """回 paths[n_paths, h] 之**累積簡單報酬**(相對 as-of 收盤)。純歷史重抽、零 tilt。"""
    m = len(logr)
    if method == "iid_bootstrap":
        draws = rng.integers(0, m, size=(n_paths, h))
        step = logr[draws]
    else:                                            # block_bootstrap(moving block、保波動叢聚/自相關)
        nb = int(np.ceil(h / block_len))
        starts = rng.integers(0, max(1, m - block_len + 1), size=(n_paths, nb))
        blocks = np.stack([logr[s:s + block_len] for row in starts for s in row])
        step = blocks.reshape(n_paths, nb * block_len)[:, :h]
    cum_log = np.cumsum(step, axis=1)
    return np.exp(cum_log) - 1.0                     # 逐日累積簡單報酬


def _summary(last_close, paths, h):
    """分位錐(逐 td)+ 終值分布 + P(終值>0)。只存摘要、不存逐路徑(鎖②)。"""
    cone = []
    for t in range(h):
        col = paths[:, t]
        cone.append({"td": t + 1,
                     **{f"p{p}": round(float(np.percentile(col, p)), 5) for p in PCTS},
                     **{f"px_p{p}": round(last_close * (1 + float(np.percentile(col, p))), 2) for p in PCTS}})
    term = paths[:, -1]
    return {
        "disclaimer": DISCLAIMER,
        "last_close": round(last_close, 2), "horizon_td": h,
        "cone": cone,
        "terminal": {**{f"ret_p{p}": round(float(np.percentile(term, p)), 5) for p in PCTS},
                     "ret_mean": round(float(term.mean()), 5),
                     "px_p50": round(last_close * (1 + float(np.percentile(term, 50))), 2)},
        "sim_stat_p_terminal_up": round(float((term > 0).mean()), 4),
        "note_p_up": "此 P(終值>0)=歷史重抽之模擬統計,非模型預測、與 D/H 軌 p_up 分欄、永不混排",
    }


def run(stocks, asof, horizons, n_paths, seed, window):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        for stock in stocks:
            last_close, logr = _hist_logrets(cur, stock, asof, window)
            if logr is None:
                print(f"  ✗ {stock} ≤{asof} 歷史不足(<60 td)—略"); continue
            for h in horizons:
                for method in ("iid_bootstrap", "block_bootstrap"):
                    rng = np.random.default_rng(seed)          # seed 顯式、可重現
                    paths = _simulate(logr, h, n_paths, method, BLOCK_LEN, rng)
                    summ = _summary(last_close, paths, h)
                    key = f"mc_{stock}_{asof}_{h}_{method}_{seed}"
                    run_id = "mc_" + hashlib.sha256(key.encode()).hexdigest()[:16]
                    cur.execute("""INSERT INTO mc_simulation_run
                        (run_id, target_id, asof_date, horizon_td, method, block_len_td, n_paths, seed,
                         summary, is_simulation, git_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s)
                        ON CONFLICT (run_id) DO UPDATE SET summary=EXCLUDED.summary, created_at=now()""",
                        (run_id, stock, asof, h, method, BLOCK_LEN if method == "block_bootstrap" else None,
                         n_paths, seed, __import__("json").dumps(summ, ensure_ascii=False), git7))
                    t = summ["terminal"]
                    print(f"  {stock} h={h:<3} {method:<15} | 終值報酬 p5={t['ret_p5']:+.1%} p50={t['ret_p50']:+.1%} "
                          f"p95={t['ret_p95']:+.1%} | 收盤價 p50={t['px_p50']} | 模擬 P(終值>0)={summ['sim_stat_p_terminal_up']}")
            conn.commit()
    print(f"✓ 模擬完成(is_simulation 硬綁 true;只存分位錐摘要、不存逐路徑;seed={seed} 可重現)")
    print(f"  ⚠ {DISCLAIMER}")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT target_id, asof_date, horizon_td, method, n_paths, summary->>'sim_stat_p_terminal_up' "
                    "FROM mc_simulation_run ORDER BY created_at DESC LIMIT 12")
        rows = cur.fetchall()
    print("已存 mc_simulation_run:" if rows else "已存 mc_simulation_run:(無)")
    for r in rows:
        print(f"  {r[0]} asof={r[1]} h={r[2]} {r[3]} n={r[4]} P(終值>0)={r[5]}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--stocks", nargs="*", default=["2330"])
    ap.add_argument("--asof", default=FREEZE)
    ap.add_argument("--horizons", nargs="*", type=int, default=list(DEFAULT_HORIZONS))
    ap.add_argument("--n-paths", dest="n_paths", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--window", type=int, default=HIST_WINDOW_TD)
    args = ap.parse_args()
    if args.run:
        return run(args.stocks, args.asof, args.horizons, args.n_paths, args.seed, args.window)
    return status()


if __name__ == "__main__":
    sys.exit(main())
