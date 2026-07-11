#!/usr/bin/env python
"""D 軌日頻方向模型 — 個股未來 k 交易日方向機率之年塊 walk-forward OOS(oracle 主計畫 §3.4/§3.5;v2 revival plan §3.2)。

🎯 這支在做什麼(白話):D 軌預測「個股未來 k 交易日收正的機率」。特徵=daily_direction_feature_values;
   標籤=1[close(t+k)/close(t)−1>0](未來報酬,#8 只入訓)。折=**年塊 walk-forward+真 purge**(train 樣本日
   ≤ test 年首交易日前推 k+1 td——標籤完全實現於 test 年前,#8;v1 零 purge 缺陷已修)。
   兩模式:
   - **--run(v1 口徑)**:DailyLogit+DailyGBDT champion(OOS hit 擇勝;歷史口徑保留、DELETE 已 scope 至
     model_id——v1 審計列不可毀,revival plan §3.1)。
   - **--run-v2(revival §3.2)**:族=DailyGBDT_cal;**purged isotonic 校準層**(train 內切 fit-set/校準尾段、
     間留 k+1 td 內層 embargo;GBDT 只 fit 於 fit-set;isotonic fit 於尾段之 out-of-sample 預測;凍結複合
     模型套 test——憲章硬綁② purged 校準器);**per-seed 落列**(#11 逐 seed 統計);無 champion 選擇
     (受判 family 由 gate criteria 預先鎖定,winner's curse 廢止)。

守 #8(特徵 lag 0、標籤未來只入訓、真 purge)· #11(per-seed 落列)· #12(model_registry)· #28(本地 sklearn)· #29a/d。
   前置=build_daily_direction_features.py + gate approved(先凍後跑)。SSOT=revival plan §3.2/§5。

執行指令矩陣:
  python scripts/train_daily_direction.py                        # 無參數:現況(唯讀)
  python scripts/train_daily_direction.py --run                  # v1 口徑(champion;歷史保留)
  python scripts/train_daily_direction.py --run-v2               # v2:DailyGBDT_cal(k=5、3 seeds、purged isotonic)
  python scripts/train_daily_direction.py --run-v2 --ks 5 --seeds 3
"""
import argparse
import bisect
import hashlib
import subprocess
import sys
import warnings
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from augur.core import db

warnings.filterwarnings("ignore")
K_SET = (1, 5)
FREEZE = "2026-05-31"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _ensure_model(cur, model_id, family, feats, git7, artifact_note):
    fh = hashlib.sha256(",".join(sorted(feats)).encode()).hexdigest()[:16]
    cur.execute("INSERT INTO model_registry (model_id, family, horizon, train_span, asof_snapshot, "
                "feats_hash, seed, artifact_path, git_sha) VALUES (%s,%s,0,%s,%s,%s,0,%s,%s) "
                "ON CONFLICT (model_id) DO NOTHING",
                (model_id, family, "[2015-01-01,2026-05-31]", FREEZE, fh, artifact_note, git7))


def _load_features(cur):
    cur.execute("SELECT panel_date, target_id, feature, value FROM daily_direction_feature_values")
    df = pd.DataFrame(cur.fetchall(), columns=["date", "stock", "feature", "value"])
    if df.empty:
        return None, None
    wide = df.pivot_table(index=["date", "stock"], columns="feature", values="value").reset_index()
    feats = [c for c in wide.columns if c not in ("date", "stock")]
    return wide, feats


def _labels(cur, stocks, k):
    """close(t+k)/close(t)−1>0 之方向標籤,逐股 groupby shift(交易日序)。回 {(date,stock): y}。"""
    cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
        WHERE stock_id = ANY(%s) AND date >= '2014-06-01' AND date <= %s ORDER BY stock_id, date""",
        (list(stocks), FREEZE))
    px = pd.DataFrame(cur.fetchall(), columns=["stock", "date", "close"])
    px["close"] = px["close"].astype(float)
    px = px.sort_values(["stock", "date"])
    px["fwd"] = px.groupby("stock")["close"].shift(-k) / px["close"] - 1
    px = px[px["fwd"].notna()]
    return {(r.date, r.stock): (1 if r.fwd > 0 else 0) for r in px.itertuples(index=False)}


def _market_cal(cur):
    cur.execute("SELECT date FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' ORDER BY date")
    return [r[0] for r in cur.fetchall()]


def _purge_cutoff(cal, ty, k):
    """真 purge:train 樣本日上限 = test 年首交易日前推 k+1 個交易日(標籤窗完全實現於 test 年前,#8)。"""
    first = next((d for d in cal if d.year == ty), None)
    if first is None:
        return None
    i = bisect.bisect_left(cal, first)
    return cal[max(i - k - 1, 0)]


def _cal_back(cal, d, n):
    """交易日曆上 ≤d 之最近日再往回 n 個交易日。"""
    i = bisect.bisect_right(cal, d) - 1
    return cal[max(i - n, 0)]


def _fit_logit(Xtr, ytr, Xte):
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if len(set(ytr)) < 2:
        return np.full(len(Xte), float(np.mean(ytr)))
    p = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1000))
    p.fit(Xtr, ytr)
    return p.predict_proba(Xte)[:, 1]


def _fit_gbdt(Xtr, ytr, seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05,
                                         early_stopping=True, random_state=seed)
    clf.fit(Xtr, ytr)
    return clf


def _year_blocks(dates, k):
    """年塊 walk-forward:test=每年、train=真 purge 後之更早樣本(_purge_cutoff)。回 test 年清單(首年純訓)。"""
    years = sorted({d.year for d in dates})
    return [y for y in years if y > years[0]]


def run(ks, seeds):
    """v1 口徑(champion by OOS hit;歷史保留)。DELETE 已 scope 至 (k_td, model_id)——v1 審計列不可毀。"""
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        wide, feats = _load_features(cur)
        if wide is None:
            print("✗ 無 daily_direction_feature_values(先跑 build_daily_direction_features.py --run)"); return 1
        stocks = wide["stock"].unique().tolist()
        print(f"D 軌特徵:{len(wide)} 列 × {len(feats)} feat / {wide['date'].nunique()} 交易日 / {len(stocks)} 檔")
        _ensure_model(cur, "DailyLogit", "DailyLogit", feats, git7, "walk_forward_refit_per_fold")
        _ensure_model(cur, "DailyGBDT", "DailyGBDT", feats, git7, "walk_forward_refit_per_fold")
        conn.commit()
        cal = _market_cal(cur)
        X_all = wide[feats].to_numpy(float)
        dates = wide["date"].to_numpy()
        years = pd.DatetimeIndex(wide["date"]).year.to_numpy()

        for k in ks:
            lab = _labels(cur, stocks, k)
            y_all = np.array([lab.get((d, s), -1) for d, s in zip(wide["date"], wide["stock"])])
            has = y_all >= 0
            test_years = _year_blocks([d for d in wide["date"]], k)
            champ = None
            for model_id, fitter in (("DailyLogit", "logit"), ("DailyGBDT", "gbdt")):
                preds = {}
                n_seeds = 1 if fitter == "logit" else seeds
                for fid, ty in enumerate(test_years):
                    cutoff = _purge_cutoff(cal, ty, k)
                    tr = has & (years < ty) & (dates <= cutoff)
                    te = has & (years == ty)
                    if tr.sum() < 500 or te.sum() == 0:
                        continue
                    acc = np.zeros(te.sum())
                    for sd in range(n_seeds):
                        if fitter == "logit":
                            acc += _fit_logit(X_all[tr], y_all[tr], X_all[te])
                        else:
                            if len(set(y_all[tr])) < 2:
                                acc += np.full(te.sum(), float(np.mean(y_all[tr])))
                            else:
                                acc += _fit_gbdt(X_all[tr], y_all[tr], sd).predict_proba(X_all[te])[:, 1]
                    p_up = acc / n_seeds
                    for i, gi in enumerate(np.where(te)[0]):
                        preds[(wide["date"].iloc[gi], wide["stock"].iloc[gi], fid)] = p_up[i]
                hit = np.mean([(p > 0.5) == (lab[(d, s)] > 0.5) for (d, s, _), p in preds.items()]) if preds else 0
                print(f"  k={k} {model_id}: OOS {len(preds)} 列 pooled_hit={hit:.4f}")
                if champ is None or hit > champ[1]:
                    champ = (model_id, hit, preds)

            model_id, _, preds = champ
            from psycopg2.extras import execute_values
            cur.execute("DELETE FROM daily_direction_oos_sample WHERE k_td=%s AND model_id=%s", (k, model_id))
            execute_values(cur, "INSERT INTO daily_direction_oos_sample "
                "(model_id, target_id, panel_date, k_td, p_up, y_up, fold_id, seed) VALUES %s",
                [(model_id, s, d, k, float(p), lab[(d, s)], fid, 0) for (d, s, fid), p in preds.items()],
                page_size=10000)
            conn.commit()
            print(f"  k={k} champion={model_id} 寫 daily_direction_oos_sample {len(preds)} 列")
    print("✓ D 軌訓練完成(v1 口徑)")
    return 0


def run_v2(ks, seeds):
    """v2(revival §3.2):DailyGBDT_cal——purged isotonic 校準層+per-seed 落列;無 champion 選擇。"""
    from sklearn.isotonic import IsotonicRegression
    model_id = "DailyGBDT_cal"
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        wide, feats = _load_features(cur)
        if wide is None:
            print("✗ 無特徵"); return 1
        stocks = wide["stock"].unique().tolist()
        print(f"D 軌 v2 特徵:{len(wide)} 列 × {len(feats)} feat({sorted(feats)})")
        _ensure_model(cur, model_id, "DailyGBDT_cal", feats, git7,
                      "walk_forward_refit_per_fold + purged_isotonic(fit-set/cal-tail 內層 embargo k+1 td)")
        conn.commit()
        cal = _market_cal(cur)
        X_all = wide[feats].to_numpy(float)
        dates = wide["date"].to_numpy()
        years = pd.DatetimeIndex(wide["date"]).year.to_numpy()

        for k in ks:
            lab = _labels(cur, stocks, k)
            y_all = np.array([lab.get((d, s), -1) for d, s in zip(wide["date"], wide["stock"])])
            has = y_all >= 0
            test_years = _year_blocks([d for d in wide["date"]], k)
            rows_out = []
            for fid, ty in enumerate(test_years):
                cutoff = _purge_cutoff(cal, ty, k)
                tr = has & (years < ty) & (dates <= cutoff)
                te = has & (years == ty)
                if tr.sum() < 2000 or te.sum() == 0:
                    continue
                # purged isotonic:train 內切 fit-set / 校準尾段(85% 分位日起)+ 內層 embargo k+1 td
                tr_dates = dates[tr]
                uniq = np.unique(tr_dates)
                tail_start = uniq[int(len(uniq) * 0.85)]
                inner_cut = _cal_back(cal, tail_start, k + 1)
                fit_m = tr & (dates <= inner_cut)
                cal_m = tr & (dates >= tail_start)
                use_iso = fit_m.sum() >= 2000 and cal_m.sum() >= 500 and len(set(y_all[fit_m])) >= 2
                te_idx = np.where(te)[0]
                for sd in range(seeds):
                    if not use_iso:
                        p_te = np.full(len(te_idx), float(np.mean(y_all[tr])))
                    else:
                        clf = _fit_gbdt(X_all[fit_m], y_all[fit_m], sd)
                        p_cal = clf.predict_proba(X_all[cal_m])[:, 1]     # 尾段=校準器之 out-of-sample
                        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(p_cal, y_all[cal_m])
                        p_te = iso.predict(clf.predict_proba(X_all[te])[:, 1])
                    for i, gi in enumerate(te_idx):
                        rows_out.append((model_id, wide["stock"].iloc[gi], wide["date"].iloc[gi], k,
                                         float(np.clip(p_te[i], 0.0, 1.0)), int(y_all[gi]), fid, sd))
                print(f"  k={k} fold ty={ty}: fit={fit_m.sum()} cal={cal_m.sum()} te={te.sum()} iso={use_iso}", flush=True)
            from psycopg2.extras import execute_values
            cur.execute("DELETE FROM daily_direction_oos_sample WHERE k_td=%s AND model_id=%s", (k, model_id))
            execute_values(cur, "INSERT INTO daily_direction_oos_sample "
                "(model_id, target_id, panel_date, k_td, p_up, y_up, fold_id, seed) VALUES %s",
                rows_out, page_size=10000)
            conn.commit()
            n_seed = len({r[7] for r in rows_out})
            print(f"  k={k} {model_id} 寫 {len(rows_out)} 列(per-seed×{n_seed};#11)")
    print("✓ D 軌 v2 訓練完成(裁決=evaluate_direction_gate.py 依 criteria estimand)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*),count(DISTINCT panel_date) FROM daily_direction_feature_values")
        f = cur.fetchone()
        cur.execute("SELECT model_id, k_td, count(*), count(DISTINCT seed) FROM daily_direction_oos_sample "
                    "GROUP BY 1,2 ORDER BY 2,1")
        oos = cur.fetchall()
    print(f"特徵:{f[0]} 列 / {f[1]} 交易日;OOS(model,k,rows,seeds):{oos or '(無)'}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--run-v2", action="store_true", dest="v2")
    ap.add_argument("--ks", nargs="*", type=int)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    if args.v2:
        return run_v2(args.ks or [5], args.seeds)
    if args.run:
        return run(args.ks or list(K_SET), args.seeds)
    return status()


if __name__ == "__main__":
    sys.exit(main())
