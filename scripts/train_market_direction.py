#!/usr/bin/env python
"""市場方向模型 — 大盤 H 期方向機率之 walk-forward OOS(oracle 主計畫 §2.3/§5.1 MktLogit)。

🎯 這支在做什麼(白話):H 軌的「市場分量」——每交易日一組市場特徵(market_direction_feature,
   #8 逐欄 visible_date)→ L2 邏輯迴歸 → 預測「大盤(TAIEX 報酬指數)未來 H 交易日收正的機率 P_mkt」。
   標籤=1[TAIEX(t+H)/TAIEX(t)−1 > 0](未來報酬,#8 只入訓不入特徵)。折口徑唯一=walkforward.splits
   +calendar 保證下界 embargo(=H+特徵滯後,§5.2 零雙軌)。逐折 fit(impute+scale+logit 都只吃 train)、
   predict test → market_direction_probability(P_mkt per panel×horizon)。這是 DirStack 的市場分量輸入,
   本身不出 UI、不進 GATE(GATE 判的是合成後的個股絕對方向)。多 seed:Logit 無隨機性 → seed 記 0(#11)。

守 #8(特徵 visible_date<=panel;標籤=未來、只入訓)· #12(折口徑複用 walkforward)· #9/#10(git_sha 溯源)
   · #28(本機 sklearn CPU、零 API)· #29a/d。前置=build_market_direction_features.py --run(全期特徵)。
   SSOT=reports/augur_oracle_upgrade_master_plan_20260711.md §2.3/§5.1。

執行指令矩陣:
  python scripts/train_market_direction.py                          # 無參數:現況(唯讀:特徵/標籤/已產機率覆蓋)
  python scripts/train_market_direction.py --run                    # 全 horizon(20/40/82/120)walk-forward OOS
  python scripts/train_market_direction.py --run --horizons 20 120  # 指定 horizon
  python scripts/train_market_direction.py --run --min-train 24     # 最小訓練折(預設 24 panel)
"""
import argparse
import hashlib
import subprocess
import sys
import warnings
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np
from augur.core import db
from augur.evaluation import label as _label
from augur.evaluation import walkforward

warnings.filterwarnings("ignore")   # sklearn 早期折全 NaN 欄跳過/penalty 棄用皆非致命(逐折獨立 fit)

H_HORIZONS = (20, 40, 82, 120)
MODEL_ID = "MktLogit"


def _ensure_model(cur, feats, git7):
    """model_registry FK 前置:上登記 MktLogit 家族列(walk-forward 逐折 refit、無單一 artifact;
    horizon=0=多 horizon 標記,真 horizon 住 market_direction_probability.horizon)。冪等。"""
    fh = hashlib.sha256(",".join(sorted(feats)).encode()).hexdigest()[:16]
    cur.execute("INSERT INTO model_registry (model_id, family, horizon, train_span, asof_snapshot, "
                "feats_hash, seed, artifact_path, git_sha) VALUES (%s,%s,0,%s,%s,%s,0,%s,%s) "
                "ON CONFLICT (model_id) DO NOTHING",
                (MODEL_ID, "MktLogit", "[2008-12-31,2026-05-31]", "2026-05-31", fh,
                 "walk_forward_refit_per_fold(無單一 artifact)", git7))


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _load_features(cur):
    """market_direction_feature → (panel_dates 排序, feats 排序, X 矩陣 float[n_panel×n_feat] 含 NaN)。
    #8:每 (panel,feature) 取 visible_date<=panel 之最新值(builder 已逐欄 lag,此處防禦式再濾)。"""
    cur.execute("SELECT DISTINCT feature FROM market_direction_feature ORDER BY feature")
    feats = [r[0] for r in cur.fetchall()]
    if not feats:
        return [], [], np.empty((0, 0))
    cur.execute("SELECT DISTINCT panel_date FROM market_direction_feature ORDER BY panel_date")
    panels = [r[0] for r in cur.fetchall()]
    fidx = {f: j for j, f in enumerate(feats)}
    X = np.full((len(panels), len(feats)), np.nan)
    pidx = {p: i for i, p in enumerate(panels)}
    cur.execute("SELECT panel_date, feature, value FROM market_direction_feature "
                "WHERE visible_date <= panel_date")
    for p, f, v in cur.fetchall():
        if p in pidx and v is not None:
            X[pidx[p], fidx[f]] = float(v)
    return panels, feats, X


def _market_label(cur, panels, h):
    """TAIEX 報酬指數 → 每 panel 之 H 交易日前瞻報酬 fwd_ret 與方向 y∈{0,1}。回 {panel: (y, fwd_ret)}。
    以全交易日曆定位 t+H(label.full_calendar);t+H 越界(未來未知,如 as-of 尾端)→ 該 panel 無標籤(略)。"""
    cur.execute("SELECT date, price FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' ORDER BY date")
    rows = cur.fetchall()
    px = {d: float(p) for d, p in rows}
    cal = [d for d, _ in rows]                       # TAIEX 自身交易日曆(=市場曆)
    cidx = {d: i for i, d in enumerate(cal)}
    out = {}
    for p in panels:
        i = cidx.get(p)
        if i is None or i + h >= len(cal):
            continue
        p0, p1 = px[cal[i]], px[cal[i + h]]
        if p0 and p0 > 0:
            r = p1 / p0 - 1.0
            out[p] = (1 if r > 0 else 0, r)
    return out


def _fit_predict(Xtr, ytr, Xte):
    """impute(median)+standardize+L2 logit,全參數只 fit 於 train(#8 零洩漏)。回 test 之 p_up。"""
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if len(set(ytr)) < 2:                            # train 單一類 → 退回基率常數預測
        return np.full(len(Xte), float(np.mean(ytr)))
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                         LogisticRegression(penalty="l2", C=1.0, max_iter=1000))
    pipe.fit(Xtr, ytr)
    return pipe.predict_proba(Xte)[:, 1]


def run(horizons, min_train):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        panels, feats, X = _load_features(cur)
        if len(panels) < min_train + 5:
            print(f"✗ 特徵面板僅 {len(panels)}(< min_train {min_train}+5);先跑 build_market_direction_features.py --run")
            return 1
        print(f"市場特徵:{len(panels)} panel × {len(feats)} feat({panels[0]}~{panels[-1]})")
        _ensure_model(cur, feats, git7); conn.commit()
        cal = _label.full_calendar(conn)
        for h in horizons:
            lab = _market_label(cur, panels, h)
            keep = [i for i, p in enumerate(panels) if p in lab]     # 只留有標籤 panel
            pk = [panels[i] for i in keep]
            Xk = X[keep]
            yk = np.array([lab[p][0] for p in pk])
            folds = walkforward.splits(pk, h, calendar=cal, min_train=min_train)
            pos = {p: i for i, p in enumerate(pk)}
            wrote = 0
            for fold in folds:
                tr = [pos[p] for p in fold["train"]]
                ti = pos[fold["test"]]                    # test=單一 panel(walkforward.splits)
                if not tr:
                    continue
                pr = float(_fit_predict(Xk[tr], yk[tr], Xk[[ti]])[0])
                cur.execute(
                    "INSERT INTO market_direction_probability "
                    "(panel_date, model_id, horizon, p_mkt_up, calibrator_id, git_sha) "
                    "VALUES (%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (panel_date, model_id, horizon) DO UPDATE SET "
                    "p_mkt_up=EXCLUDED.p_mkt_up, git_sha=EXCLUDED.git_sha, created_at=now()",
                    (fold["test"], MODEL_ID, h, pr, "raw_logit", git7))
                wrote += 1
            conn.commit()
            base = float(np.mean(yk)) if len(yk) else float("nan")
            print(f"  H{h:<3} folds={len(folds)} 寫 P_mkt {wrote} 列 | 大盤上漲基率 p̄={base:.3f} n_label={len(yk)}")
    print("✓ 市場分量完成(市場分量不出 UI/不進 GATE;供 DirStack 合成)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT panel_date) FROM market_direction_feature")
        nf, npf = cur.fetchone()
        cur.execute("SELECT horizon, count(*) FROM market_direction_probability GROUP BY horizon ORDER BY horizon")
        prob = cur.fetchall()
    print(f"市場特徵:{nf} 列 / {npf} panel")
    print(f"已產 P_mkt:{prob or '(無)'}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--horizons", nargs="*", type=int, default=list(H_HORIZONS))
    ap.add_argument("--min-train", dest="min_train", type=int, default=24)
    args = ap.parse_args()
    if args.run:
        return run(args.horizons, args.min_train)
    return status()


if __name__ == "__main__":
    sys.exit(main())
