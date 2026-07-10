#!/usr/bin/env python
"""相對機率校準器 — probability_oos_sample → Platt(purge)→ probability_calibrator + prediction_probability(e2e P6/§6.3)。

🎯 這支在做什麼(白話):把「橫斷面分位」校準成「P(勝過同儕中位數|as-of,H)」——**唯一合法機率口徑**
   (憲章 v1.40.0 相對機率誠實判準;禁絕對漲跌機率)。
   --fit:對每 horizon 以 **expanding purge** 評估品質(評估折 i 之校準僅 fit 於「標籤窗已完全實現於
   折 i as-of 之前」之樣本,即 exit_date < panel_date(i)——非裸前折 #8),逐折 Brier 對 base-rate
   基線/ECE 10-bin/可靠度分箱(逐折口徑、禁 iid 顯著性宣稱);serve 校準器 fit 於全部 FREEZE 內樣本,
   params/品質/同族聲明(A-36)落 probability_calibrator(provenance 可溯源)。方法=Platt(2 參數
   logistic;折 n 小 isotonic 過擬合 A-8)。
   --emit:套 serve 校準器於 prediction_values 之 as-of 分位(1=最強,方向契約)→ prediction_probability,
   econ_verdict 判死標籤同列硬綁(D2)、calendar_days=日曆日近似(A-27)。
   **誠實預期(#15):校準後機率集中 0.5 附近窄帶(薄 edge)=誠實輸出、非失敗。**

守 #8(purge 機械斷言)· #10(全參可溯源可重現)· #12(對樣本=§6.2 唯一來源;不重算折)· 憲章 v1.40.0 · CLAUDE #29a。
   SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §1.3/§5.3-5.4/§6.3。

執行指令矩陣:
  python scripts/calibrate_relative_probability.py                       # 無參數:各 horizon 校準現況矩陣(唯讀)
  python scripts/calibrate_relative_probability.py --fit --horizon 60    # purge fit → probability_calibrator
  python scripts/calibrate_relative_probability.py --fit --all           # {20,40,60,120} 全 fit
  python scripts/calibrate_relative_probability.py --emit --horizon 60 --asof 2026-05-31  # → prediction_probability
  python scripts/calibrate_relative_probability.py --emit --all --asof 2026-05-31
  python scripts/calibrate_relative_probability.py --report              # 可靠度報告(逐折 Brier/ECE/分箱)
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

from augur.core import db

HORIZONS = (20, 40, 60, 120)
FREEZE = "2026-05-31"
MODEL_FAMILY = "RankRidge"
CAL_DAYS = {20: 29, 40: 58, 60: 87, 82: 119, 120: 174}   # 日曆日近似(§1.2;A-27 呈現偏差推導 SSOT)
# D2/§1.2 經濟裁決標籤(來源:short_horizon/tier3/H120 裁決報告;與機率同列硬綁不可分離)
ECON = {20: "dead", 40: "thin_unestablished", 60: "thin_unestablished",
        82: "thin_unestablished", 120: "thin_unestablished"}
FAMILY_NOTE = ("校準器 fit 於 walk-forward 逐折 refit 之同族(RankRidge)模型,serve 套於 train_ranker "
               "全樣本 artifact 之分位——同 family、非同一模型,機率為同族近似值")  # §1.1 標記④固定用語
MIN_FIT = 200   # 折品質評估之最小可 fit 樣本數(不足=該折跳過、誠實少一折)


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _platt_fit(x, y):
    """Platt:單特徵 logistic(sklearn lbfgs);回 (a,b) 使 p=sigmoid(a*x+b)。"""
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(C=1e6, solver="lbfgs")
    lr.fit(np.asarray(x).reshape(-1, 1), np.asarray(y, dtype=int))
    return float(lr.coef_[0][0]), float(lr.intercept_[0])


def _sigmoid(a, b, x):
    return 1.0 / (1.0 + math.exp(-(a * x + b)))


def _load(cur, h):
    cur.execute("SELECT panel_date, rank_pctile, label_beat_median, exit_date "
                "FROM probability_oos_sample WHERE horizon=%s AND model_family=%s "
                "ORDER BY panel_date, stock_id", (h, MODEL_FAMILY))
    return cur.fetchall()


def fit_horizon(cur, h, git7):
    rows = _load(cur, h)
    if not rows:
        print(f"  ✗ H{h}: 對樣本空(先跑 build_probability_oos_sample --run)"); return None
    panels = sorted({r[0] for r in rows})
    # expanding purge 逐折品質
    fold_brier, fold_base, preds = [], [], []   # preds=(p,label) pooled(供 ECE/分箱;逐折口徑產生)
    folds_used = 0
    for pd_i in panels:
        train = [(x, y) for p, x, y, ex in rows if ex < pd_i]
        test = [(x, y) for p, x, y, ex in rows if p == pd_i]
        if len(train) < MIN_FIT or len({y for _, y in train}) < 2:
            continue
        a, b = _platt_fit([x for x, _ in train], [y for _, y in train])
        ps = [(_sigmoid(a, b, x), y) for x, y in test]
        base = sum(y for _, y in train) / len(train)          # base-rate 常數基線
        fold_brier.append(sum((p - y) ** 2 for p, y in ps) / len(ps))
        fold_base.append(sum((base - y) ** 2 for _, y in ps) / len(ps))
        preds.extend(ps)
        folds_used += 1
    # ECE 10-bin + 可靠度分箱(pooled、逐折產生)
    bins = [{"lo": i / 10, "hi": (i + 1) / 10, "n": 0, "p_mean": 0.0, "y_rate": 0.0} for i in range(10)]
    for p, y in preds:
        i = min(int(p * 10), 9)
        b_ = bins[i]
        b_["n"] += 1
        b_["p_mean"] += p
        b_["y_rate"] += y
    ece = 0.0
    for b_ in bins:
        if b_["n"]:
            b_["p_mean"] /= b_["n"]
            b_["y_rate"] /= b_["n"]
            ece += (b_["n"] / len(preds)) * abs(b_["p_mean"] - b_["y_rate"])
        b_["p_mean"], b_["y_rate"] = round(b_["p_mean"], 4), round(b_["y_rate"], 4)
    # serve 校準器:全樣本 fit(全部 exit_date ≤ FREEZE=建構保證;機械斷言)
    cur.execute("SELECT count(*) FROM probability_oos_sample WHERE horizon=%s AND exit_date > %s", (h, FREEZE))
    purge_ok = cur.fetchone()[0] == 0
    a, b = _platt_fit([r[1] for r in rows], [r[2] for r in rows])
    cid = f"platt_h{h}_asof{FREEZE}_g{git7}"
    cur.execute("""
        INSERT INTO probability_calibrator (calibrator_id, horizon, method, fit_asof, n_fit_samples,
          n_fit_folds, purge_verified, params, brier, brier_baseline, ece, reliability_bins, family_note, git_sha)
        VALUES (%s,%s,'platt',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (calibrator_id) DO UPDATE SET params=EXCLUDED.params, brier=EXCLUDED.brier,
          brier_baseline=EXCLUDED.brier_baseline, ece=EXCLUDED.ece, reliability_bins=EXCLUDED.reliability_bins,
          n_fit_samples=EXCLUDED.n_fit_samples, n_fit_folds=EXCLUDED.n_fit_folds, purge_verified=EXCLUDED.purge_verified""",
        (cid, h, FREEZE, len(rows), folds_used, purge_ok, json.dumps({"a": a, "b": b}),
         round(float(np.mean(fold_brier)), 6) if fold_brier else None,
         round(float(np.mean(fold_base)), 6) if fold_base else None,
         round(ece, 6) if preds else None, json.dumps(bins), FAMILY_NOTE, git7))
    print(f"  ✓ H{h}: {cid} | 折 {folds_used}/{len(panels)} | Brier {np.mean(fold_brier):.4f} "
          f"vs 基線 {np.mean(fold_base):.4f} | ECE {ece:.4f} | purge_verified={purge_ok} | a={a:.3f} b={b:.3f}")
    return cid


def emit_horizon(cur, h, asof, git7):
    cur.execute("SELECT calibrator_id, params FROM probability_calibrator WHERE horizon=%s "
                "ORDER BY created_at DESC LIMIT 1", (h,))
    row = cur.fetchone()
    if not row:
        print(f"  ✗ H{h}: 無校準器(先 --fit)"); return 0
    cid, params = row[0], row[1]
    a, b = params["a"], params["b"]
    cur.execute("SELECT pv.model_id, pv.stock_id, pv.rank FROM prediction_values pv "
                "JOIN model_registry mr USING (model_id) "
                "WHERE pv.panel_date=%s AND mr.family=%s AND mr.horizon=%s ORDER BY pv.rank",
                (asof, MODEL_FAMILY, h))
    rows = cur.fetchall()
    if not rows:
        print(f"  ✗ H{h}: prediction_values 無 {asof} 列"); return 0
    n = len(rows)
    model_id = rows[0][0]
    out = []
    for _, sid, rk in rows:
        pctl = 1.0 - (rk - 1) / (n - 1) if n > 1 else 1.0     # 方向契約:rank1=最強→pctile=1
        p = min(max(_sigmoid(a, b, pctl), 1e-6), 1 - 1e-6)     # CHECK (0,1) 開區間保證
        out.append((asof, model_id, sid, h, round(pctl, 6), round(p, 6), cid, ECON[h], CAL_DAYS[h]))
    cur.execute("DELETE FROM prediction_probability WHERE panel_date=%s AND model_id=%s", (asof, model_id))
    cur.executemany("INSERT INTO prediction_probability (panel_date,model_id,stock_id,horizon,rank_pctile,"
                    "p_beat_median,calibrator_id,econ_verdict,calendar_days) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", out)
    ps = [o[5] for o in out]
    print(f"  ✓ H{h}: emit {n} 檔 | p∈[{min(ps):.3f},{max(ps):.3f}] | econ={ECON[h]} | ≈{CAL_DAYS[h]} 日曆日 | {cid}")
    return n


def status(cur):
    for h in HORIZONS:
        cur.execute("SELECT count(*) FROM probability_oos_sample WHERE horizon=%s", (h,))
        n_s = cur.fetchone()[0]
        cur.execute("SELECT calibrator_id, brier, brier_baseline, ece, n_fit_folds, purge_verified "
                    "FROM probability_calibrator WHERE horizon=%s ORDER BY created_at DESC LIMIT 1", (h,))
        c = cur.fetchone()
        cur.execute("SELECT count(*) FROM prediction_probability WHERE horizon=%s", (h,))
        n_p = cur.fetchone()[0]
        tag = (f"calibrator={c[0]}(Brier {c[1]} vs 基線 {c[2]}, ECE {c[3]}, 折 {c[4]}, purge={c[5]})"
               if c else "無校準器")
        print(f"  H{h}: 樣本 {n_s:,} | {tag} | emit {n_p} 列")


def report(cur):
    print("═══ 可靠度報告(逐折口徑;機率集中 0.5 窄帶=薄 edge 誠實輸出)═══")
    for h in HORIZONS:
        cur.execute("SELECT calibrator_id, brier, brier_baseline, ece, reliability_bins, n_fit_folds "
                    "FROM probability_calibrator WHERE horizon=%s ORDER BY created_at DESC LIMIT 1", (h,))
        c = cur.fetchone()
        if not c:
            print(f"H{h}: 無校準器"); continue
        gain = (c[2] - c[1]) if (c[1] is not None and c[2] is not None) else None
        print(f"\nH{h} {c[0]}(折 {c[5]}):Brier {c[1]} vs 基線 {c[2]}"
              f"(增益 {gain:+.4f} {'✓ 優於基線' if gain and gain > 0 else '⚠ 未優於基線=exploratory'})| ECE {c[3]}")
        for b_ in (c[4] or []):
            if b_["n"]:
                print(f"    bin[{b_['lo']:.1f},{b_['hi']:.1f}) n={b_['n']:<6} 預測均值 {b_['p_mean']:.3f} 實現率 {b_['y_rate']:.3f}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--horizon", type=int, choices=HORIZONS)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--asof", default=FREEZE)
    args = ap.parse_args()
    hs = list(HORIZONS) if args.all else ([args.horizon] if args.horizon else None)
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.fit:
            if not hs:
                sys.exit("--fit 需 --horizon 或 --all")
            for h in hs:
                fit_horizon(cur, h, git7)
            conn.commit()
            return 0
        if args.emit:
            if not hs:
                sys.exit("--emit 需 --horizon 或 --all")
            for h in hs:
                emit_horizon(cur, h, args.asof, git7)
            conn.commit()
            return 0
        if args.report:
            report(cur); return 0
        print(__doc__.split("執行指令矩陣:")[1])
        print("校準現況矩陣(唯讀):")
        status(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
