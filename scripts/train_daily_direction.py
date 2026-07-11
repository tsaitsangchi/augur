#!/usr/bin/env python
"""D 軌日頻方向模型 — 個股未來 k 交易日方向機率之年塊 walk-forward OOS(oracle 主計畫 §3.4/§3.5)。

🎯 這支在做什麼(白話):D 軌預測「個股未來 k 交易日收正的機率」(k∈{1,5})。特徵=daily_direction_feature_
   values(§3.3);標籤=1[close(t+k)/close(t)−1>0](未來報酬,#8 只入訓)。折=**年塊 walk-forward**(§3.5:
   test 以「年」為塊≈11 折、expanding train、embargo=k td 隔開 train 尾與 test 首,#8 保證)。族:DailyLogit
   (基線,seed 0)+ DailyGBDT(HistGradientBoosting 挑戰者,多 seed≥3)。**champion**(OOS pooled hit 高者)之
   逐股逐日 p_up/y_up 寫 daily_direction_oos_sample(餵 evaluate_direction_gate 判 dgate_D_1/D_5)。
   誠實預期:1-5 日方向最噪、預註冊即標 expected dead;此支給 gate 公平一測,結果照實。

守 #8(特徵 lag 0、標籤未來只入訓、embargo 隔折)· #11(GBDT 多 seed)· #12(model_registry 落帳)· #28(本地 sklearn)· #29a/d。
   前置=build_daily_direction_features.py --run + gate dgate_D_* approved。SSOT=oracle 主計畫 §3.4/§3.5。

執行指令矩陣:
  python scripts/train_daily_direction.py                        # 無參數:現況(唯讀)
  python scripts/train_daily_direction.py --run                  # k∈{1,5} 年塊 walk-forward → OOS
  python scripts/train_daily_direction.py --run --ks 1           # 指定 k
  python scripts/train_daily_direction.py --run --seeds 3        # GBDT seed 數(預設 3)
"""
import argparse
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


def _ensure_model(cur, model_id, family, feats, git7):
    fh = hashlib.sha256(",".join(sorted(feats)).encode()).hexdigest()[:16]
    cur.execute("INSERT INTO model_registry (model_id, family, horizon, train_span, asof_snapshot, "
                "feats_hash, seed, artifact_path, git_sha) VALUES (%s,%s,0,%s,%s,%s,0,%s,%s) "
                "ON CONFLICT (model_id) DO NOTHING",
                (model_id, family, "[2015-01-01,2026-05-31]", FREEZE, fh, "walk_forward_refit_per_fold", git7))


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


def _fit_gbdt(Xtr, ytr, Xte, seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    if len(set(ytr)) < 2:
        return np.full(len(Xte), float(np.mean(ytr)))
    clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05,
                                         early_stopping=True, random_state=seed)
    clf.fit(Xtr, ytr)
    return clf.predict_proba(Xte)[:, 1]


def _year_blocks(dates, k):
    """年塊 walk-forward:test=每年、train=該年首日前(扣 embargo=k td)之全部。回 [(train_mask_fn, test_year)]。"""
    years = sorted({d.year for d in dates})
    return [y for y in years if y > years[0]]     # 首年純訓、不當 test


def run(ks, seeds):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        wide, feats = _load_features(cur)
        if wide is None:
            print("✗ 無 daily_direction_feature_values(先跑 build_daily_direction_features.py --run)"); return 1
        stocks = wide["stock"].unique().tolist()
        print(f"D 軌特徵:{len(wide)} 列 × {len(feats)} feat / {wide['date'].nunique()} 交易日 / {len(stocks)} 檔")
        _ensure_model(cur, "DailyLogit", "DailyLogit", feats, git7)
        _ensure_model(cur, "DailyGBDT", "DailyGBDT", feats, git7)
        conn.commit()
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
                preds = {}                      # (date,stock) -> mean p_up over seeds
                n_seeds = 1 if fitter == "logit" else seeds
                for fid, ty in enumerate(test_years):
                    emb_cut = pd.Timestamp(year=ty, month=1, day=1).date()
                    tr = has & (years < ty) & (dates < np.datetime64(emb_cut))
                    te = has & (years == ty)
                    if tr.sum() < 500 or te.sum() == 0:
                        continue
                    acc = np.zeros(te.sum())
                    for sd in range(n_seeds):
                        if fitter == "logit":
                            acc += _fit_logit(X_all[tr], y_all[tr], X_all[te])
                        else:
                            acc += _fit_gbdt(X_all[tr], y_all[tr], X_all[te], sd)
                    p_up = acc / n_seeds
                    for i, gi in enumerate(np.where(te)[0]):
                        preds[(wide["date"].iloc[gi], wide["stock"].iloc[gi], fid)] = p_up[i]
                hit = np.mean([(p > 0.5) == (lab[(d, s)] > 0.5) for (d, s, _), p in preds.items()]) if preds else 0
                print(f"  k={k} {model_id}: OOS {len(preds)} 列 pooled_hit={hit:.4f}")
                if champ is None or hit > champ[1]:
                    champ = (model_id, hit, preds)

            model_id, _, preds = champ
            from psycopg2.extras import execute_values
            cur.execute("DELETE FROM daily_direction_oos_sample WHERE k_td=%s", (k,))
            execute_values(cur, "INSERT INTO daily_direction_oos_sample "
                "(model_id, target_id, panel_date, k_td, p_up, y_up, fold_id, seed) VALUES %s",
                [(model_id, s, d, k, float(p), lab[(d, s)], fid, 0) for (d, s, fid), p in preds.items()],
                page_size=10000)
            conn.commit()
            print(f"  k={k} champion={model_id} 寫 daily_direction_oos_sample {len(preds)} 列")
    print("✓ D 軌訓練完成(下一棒:evaluate_direction_gate.py --evaluate dgate_D_1/D_5)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*),count(DISTINCT panel_date) FROM daily_direction_feature_values")
        f = cur.fetchone()
        cur.execute("SELECT k_td, count(*), count(DISTINCT model_id) FROM daily_direction_oos_sample GROUP BY k_td ORDER BY k_td")
        oos = cur.fetchall()
    print(f"特徵:{f[0]} 列 / {f[1]} 交易日;OOS:{oos or '(無)'}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--ks", nargs="*", type=int, default=list(K_SET))
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    if args.run:
        return run(args.ks, args.seeds)
    return status()


if __name__ == "__main__":
    sys.exit(main())
