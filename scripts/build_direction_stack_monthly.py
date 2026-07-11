#!/usr/bin/env python
"""月頻 stack 特徵 — DirStackM 之月末 as-of 特徵面板(v2 revival plan §3.4;不污染 feature_values canonical 網格)。

🎯 這支在做什麼(白話):H 軌 v2 的個股月頻特徵層——每「月末交易日」×「最近相對 panel 之宇宙股」一組:
   m_vol_60(60td 日報酬 std)、m_mom_60(60td 報酬)、m_beta_252(對 TAIEX 252td beta,rolling 動差公式)
   ——皆由日價(TaiwanStockPriceAdj/TRI)月末直算(#8 t 收盤 lag0);m_inst_net_z(法人 20 日淨買 252d z,
   lag-1 值位移);rank_pctile_h{20,40,82}(probability_oos_sample 最近 as-of panel 之相對強弱,**如實陳舊**:
   2021+ 季頻 stale≤3 月、2016-2020 年頻 stale≤12 月——判門窗由 gate criteria 凍結,此表只如實落值)。
   落 direction_stack_feature_monthly(scoped DELETE 冪等)。

守 #8(月末 as-of、lag 口徑逐特徵)· #9/#10(git_sha;全在庫)· #28(本地 pandas)· #29a/d。
   前置=probability_oos_sample(相對軌)。SSOT=revival plan §3.4/§5。

執行指令矩陣:
  python scripts/build_direction_stack_monthly.py                    # 無參數:現況(唯讀)
  python scripts/build_direction_stack_monthly.py --run              # 全期(2017-01~FREEZE 月末)
  python scripts/build_direction_stack_monthly.py --run --since 2021-01-01
  python scripts/build_direction_stack_monthly.py --run --months 3   # 小樣測試(最早 3 個月末,#25)
"""
import argparse
import bisect
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from augur.core import db

START, FREEZE = "2017-01-01", "2026-05-31"
H_RANKS = (20, 40, 82)
FEATS = ["m_vol_60", "m_mom_60", "m_beta_252", "m_inst_net_z"] + [f"rank_pctile_h{h}" for h in H_RANKS]


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _month_ends(cal, since):
    """TAIEX 交易日曆 → 每月最後交易日(since~FREEZE)。"""
    out, cur_m = [], None
    for d in cal:
        if cur_m is not None and (d.year, d.month) != cur_m:
            out.append(prev)
        cur_m, prev = (d.year, d.month), d
    out.append(prev)
    return [d for d in out if str(d) >= since]


def run(since, n_months):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT date FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' "
                    "AND date <= %s ORDER BY date", (FREEZE,))
        cal = [r[0] for r in cur.fetchall()]
        mes = _month_ends(cal, since)
        if n_months:
            mes = mes[:n_months]
        # 相對軌 rank as-of 源(2016-12-31 起年頻→2021+ 季頻;如實陳舊)
        cur.execute("SELECT panel_date, horizon, stock_id, rank_pctile FROM probability_oos_sample "
                    "WHERE horizon = ANY(%s) AND rank_pctile IS NOT NULL", (list(H_RANKS),))
        rk = pd.DataFrame(cur.fetchall(), columns=["panel", "h", "stock", "rank"])
        rk_panels = sorted(rk["panel"].unique())
        print(f"月末 panel:{len(mes)}({mes[0]}~{mes[-1]});rank 源 panel:{len(rk_panels)}")
        # 宇宙=各月末最近 rank panel(h=20)之股票集聯集
        stocks = sorted(rk["stock"].unique())
        # 日價(含 400 天緩衝供 252td 窗)
        buf = str(pd.Timestamp(mes[0]) - pd.Timedelta(days=550)).split()[0]
        cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
            WHERE stock_id = ANY(%s) AND date >= %s AND date <= %s ORDER BY stock_id, date""",
            (stocks, buf, FREEZE))
        px = pd.DataFrame(cur.fetchall(), columns=["stock", "date", "close"])
        px["close"] = px["close"].astype(float)
        cur.execute("SELECT date, price FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' "
                    "AND date >= %s AND date <= %s ORDER BY date", (buf, FREEZE))
        mk = pd.DataFrame(cur.fetchall(), columns=["date", "mpx"])
        mk["mpx"] = mk["mpx"].astype(float)
        mk["mret"] = mk["mpx"].pct_change()
        px = px.merge(mk[["date", "mret"]], on="date", how="left").sort_values(["stock", "date"])
        g = px.groupby("stock", group_keys=False)
        px["ret"] = g["close"].pct_change()
        px["m_vol_60"] = g["ret"].transform(lambda s: s.rolling(60, min_periods=40).std())
        px["m_mom_60"] = g["close"].pct_change(60)
        # beta_252:rolling 動差公式(cov/var,全 transform 向量化)
        for col, expr in (("_rs_rm", px["ret"] * px["mret"]), ("_rs", px["ret"]),
                          ("_rm", px["mret"]), ("_rm2", px["mret"] ** 2)):
            px[col] = expr
        for col in ("_rs_rm", "_rs", "_rm", "_rm2"):
            px[col + "_m"] = px.groupby("stock", group_keys=False)[col].transform(
                lambda s: s.rolling(252, min_periods=150).mean())
        var_m = px["_rm2_m"] - px["_rm_m"] ** 2
        px["m_beta_252"] = np.where(var_m > 1e-10, (px["_rs_rm_m"] - px["_rs_m"] * px["_rm_m"]) / var_m, np.nan)
        # 法人 z(20d 淨買和之 252d z;lag-1 值位移)
        cur.execute("""SELECT stock_id, date, sum(buy::float8 - sell::float8)
            FROM "TaiwanStockInstitutionalInvestorsBuySell"
            WHERE stock_id = ANY(%s) AND date >= %s AND date <= %s GROUP BY stock_id, date""",
            (stocks, buf, FREEZE))
        ins = pd.DataFrame(cur.fetchall(), columns=["stock", "date", "net"]).sort_values(["stock", "date"])
        ins["net"] = ins["net"].astype(float)
        gi = ins.groupby("stock", group_keys=False)
        s20 = gi["net"].transform(lambda s: s.rolling(20, min_periods=10).sum())
        mu = s20.groupby(ins["stock"]).transform(lambda s: s.rolling(252, min_periods=60).mean())
        sd = s20.groupby(ins["stock"]).transform(lambda s: s.rolling(252, min_periods=60).std())
        ins["m_inst_net_z"] = ((s20 - mu) / sd).groupby(ins["stock"]).shift(1)
        px = px.merge(ins[["stock", "date", "m_inst_net_z"]], on=["stock", "date"], how="left")

        rows = []
        for me in mes:
            ri = bisect.bisect_right(rk_panels, me) - 1          # 最近 rank panel ≤ 月末(as-of)
            if ri < 0:
                continue
            rp = rk_panels[ri]
            rk_me = rk[rk["panel"] == rp]
            uni = set(rk_me[rk_me["h"] == 20]["stock"])
            snap = px[(px["date"] == me) & px["stock"].isin(uni)]
            for _, r in snap.iterrows():
                for fn in ("m_vol_60", "m_mom_60", "m_beta_252", "m_inst_net_z"):
                    v = r[fn]
                    if v is not None and np.isfinite(v):
                        rows.append((me, r["stock"], fn, float(v), git7))
            for h in H_RANKS:
                sub = rk_me[rk_me["h"] == h]
                for st, rv in zip(sub["stock"], sub["rank"]):
                    if st in uni:
                        rows.append((me, st, f"rank_pctile_h{h}", float(rv), git7))
        cur.execute("DELETE FROM direction_stack_feature_monthly WHERE panel_date >= %s AND feature = ANY(%s)",
                    (mes[0], FEATS))
        from psycopg2.extras import execute_values
        execute_values(cur, "INSERT INTO direction_stack_feature_monthly "
                            "(panel_date, target_id, feature, value, git_sha) VALUES %s", rows, page_size=10000)
        conn.commit()
        print(f"✓ 月頻 stack 特徵 {len(rows)} 列({len(mes)} 月末;FREEZE 截尾斷言=max panel {max(m for m in mes)})")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_stack_feature_monthly')")
        if not cur.fetchone()[0]:
            print("(表未建;先 migrate_direction_ddl.py --run)"); return 0
        cur.execute("SELECT count(*), count(DISTINCT panel_date), count(DISTINCT target_id), "
                    "min(panel_date), max(panel_date) FROM direction_stack_feature_monthly")
        print("direction_stack_feature_monthly:", cur.fetchone())
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default=START)
    ap.add_argument("--months", type=int)
    args = ap.parse_args()
    if args.run:
        return run(args.since, args.months)
    return status()


if __name__ == "__main__":
    sys.exit(main())
