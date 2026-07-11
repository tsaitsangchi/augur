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
  python scripts/train_market_direction.py --run-v2                 # v2:MktLogit_v2(as-of join 修復+新特徵;v1 列不覆寫)
  python scripts/train_market_direction.py --run-v2 --with-gbdt     # +MktGBDT 陪跑(step-refit 21;不入裁決鏈)
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


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _load_features(cur):
    """market_direction_feature → (panel_dates 排序, feats 排序, X 矩陣 float[n_panel×n_feat] 含 NaN)。
    #8 **as-of join(v2 修復,revival plan §3.1)**:每 (panel,feature) 取「visible_date≤panel 之最新可見值」
    ——v1 按 panel_date 對位使 lag-1 特徵(visible=次日)0 列進模;as-of 取值後籌碼/情緒族首次可被消費。
    per-feature 消費計數落 stdout(P1 驗收據此,非查表)。"""
    cur.execute("SELECT DISTINCT feature FROM market_direction_feature ORDER BY feature")
    feats = [r[0] for r in cur.fetchall()]
    if not feats:
        return [], [], np.empty((0, 0))
    cur.execute("SELECT DISTINCT panel_date FROM market_direction_feature ORDER BY panel_date")
    panels = [r[0] for r in cur.fetchall()]
    X = np.full((len(panels), len(feats)), np.nan)
    pdates = np.array(panels)
    consumed = {}
    for j, f in enumerate(feats):
        cur.execute("SELECT visible_date, value FROM market_direction_feature "
                    "WHERE feature=%s AND value IS NOT NULL ORDER BY visible_date, panel_date", (f,))
        rows = cur.fetchall()
        if not rows:
            consumed[f] = 0
            continue
        vis = np.array([r[0] for r in rows])
        val = np.array([float(r[1]) for r in rows])
        idx = np.searchsorted(vis, pdates, side="right") - 1   # 每 panel:最新 visible≤panel 之列
        ok = idx >= 0
        X[ok, j] = val[idx[ok]]
        consumed[f] = int(ok.sum())
    print("  per-feature 消費(as-of join;P1 驗收):" +
          ", ".join(f"{f}={consumed[f]}" for f in feats))
    zero = [f for f in feats if consumed[f] == 0]
    if zero:
        print(f"  ⚠ 零消費特徵:{zero}")
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


def _fit_predict_gbdt(Xtr, ytr, seeds):
    """MktGBDT 挑戰者(陪跑、不入裁決鏈):HistGB 多 seed 平均。回 fitted models(供 step-refit 重用)。"""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline
    if len(set(ytr)) < 2:
        return None
    models = []
    for sd in range(seeds):
        p = make_pipeline(SimpleImputer(strategy="median"),
                          HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05,
                                                         early_stopping=True, random_state=sd))
        p.fit(Xtr, ytr)
        models.append(p)
    return models


def run(horizons, min_train, model_id=MODEL_ID, family="logit", seeds=3, refit_step=1):
    """family='logit'(逐折 refit)|'gbdt'(step-refit 每 refit_step 折重訓一次,MktGBDT 陪跑)。
    v2 一律新 model_id(MktLogit_v2/MktGBDT)——v1 MktLogit 列不覆寫(revival plan §3.1 證據保全)。"""
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        panels, feats, X = _load_features(cur)
        if len(panels) < min_train + 5:
            print(f"✗ 特徵面板僅 {len(panels)}(< min_train {min_train}+5);先跑 build_market_direction_features.py --run")
            return 1
        print(f"市場特徵:{len(panels)} panel × {len(feats)} feat({panels[0]}~{panels[-1]});model_id={model_id}")
        fam = {"logit": "MktLogit", "gbdt": "MktGBDT"}[family]
        _ensure_model_id(cur, model_id, fam, feats, git7); conn.commit()
        cal = _label.full_calendar(conn)
        for h in horizons:
            lab = _market_label(cur, panels, h)
            keep = [i for i, p in enumerate(panels) if p in lab]     # 只留有標籤 panel
            pk = [panels[i] for i in keep]
            Xk = X[keep]
            yk = np.array([lab[p][0] for p in pk])
            folds = walkforward.splits(pk, h, calendar=cal, min_train=min_train)
            pos = {p: i for i, p in enumerate(pk)}
            wrote, gb_models, gb_at = 0, None, -10**9
            for fi, fold in enumerate(folds):
                tr = [pos[p] for p in fold["train"]]
                ti = pos[fold["test"]]                    # test=單一 panel(walkforward.splits)
                if not tr:
                    continue
                if family == "logit":
                    pr = float(_fit_predict(Xk[tr], yk[tr], Xk[[ti]])[0])
                else:                                     # gbdt:step-refit(train 只會更舊=embargo 更保守)
                    if gb_models is None or fi - gb_at >= refit_step:
                        gb_models = _fit_predict_gbdt(Xk[tr], yk[tr], seeds)
                        gb_at = fi
                    if gb_models is None:
                        pr = float(np.mean(yk[tr]))
                    else:
                        pr = float(np.mean([m.predict_proba(Xk[[ti]])[0, 1] for m in gb_models]))
                cur.execute(
                    "INSERT INTO market_direction_probability "
                    "(panel_date, model_id, horizon, p_mkt_up, calibrator_id, git_sha) "
                    "VALUES (%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (panel_date, model_id, horizon) DO UPDATE SET "
                    "p_mkt_up=EXCLUDED.p_mkt_up, git_sha=EXCLUDED.git_sha, created_at=now()",
                    (fold["test"], model_id, h, pr, "raw_" + family, git7))
                wrote += 1
            conn.commit()
            base = float(np.mean(yk)) if len(yk) else float("nan")
            print(f"  H{h:<3} folds={len(folds)} 寫 P_mkt {wrote} 列 | 大盤上漲基率 p̄={base:.3f} n_label={len(yk)}")
    print("✓ 市場分量完成(市場分量不出 UI/不進 GATE;供 DirStack 合成)")
    return 0


def _ensure_model_id(cur, model_id, family, feats, git7):
    fh = hashlib.sha256(",".join(sorted(feats)).encode()).hexdigest()[:16]
    cur.execute("INSERT INTO model_registry (model_id, family, horizon, train_span, asof_snapshot, "
                "feats_hash, seed, artifact_path, git_sha) VALUES (%s,%s,0,%s,%s,%s,0,%s,%s) "
                "ON CONFLICT (model_id) DO NOTHING",
                (model_id, family, "[2008-12-31,2026-05-31]", "2026-05-31", fh,
                 "walk_forward_refit_per_fold(無單一 artifact)", git7))


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
    ap.add_argument("--run-v2", action="store_true", dest="v2")       # MktLogit_v2(as-of join+新特徵)
    ap.add_argument("--with-gbdt", action="store_true", dest="gbdt")  # MktGBDT 陪跑(step-refit 21)
    ap.add_argument("--horizons", nargs="*", type=int, default=list(H_HORIZONS))
    ap.add_argument("--min-train", dest="min_train", type=int, default=24)
    args = ap.parse_args()
    if args.v2:
        rc = run(args.horizons, args.min_train, model_id="MktLogit_v2", family="logit")
        if rc == 0 and args.gbdt:
            rc = run(args.horizons, args.min_train, model_id="MktGBDT", family="gbdt", refit_step=21)
        return rc
    if args.run:
        return run(args.horizons, args.min_train)
    return status()


if __name__ == "__main__":
    sys.exit(main())
