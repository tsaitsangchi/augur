#!/usr/bin/env python
"""DirStack 合成層 — 個股絕對方向機率 = 市場分量 × 相對分量(oracle 主計畫 §2.3/§5.1)。

🎯 這支在做什麼(白話):把兩個「都已 walk-forward OOS」的分量疊成「個股未來 H 交易日絕對收正的機率」——
   相對分量=probability_oos_sample 的 rank_pctile(個股相對同儕強弱,已 OOS);市場分量=market_direction_
   probability 的 P_mkt(大盤方向,已 OOS)。合成器=L2 邏輯迴歸,特徵 [logit(P_mkt), rank_pctile,
   交互項],標籤 y_up=1[fwd_ret>0](個股絕對報酬方向,現成於 probability_oos_sample.fwd_ret)。
   **合成器本身再 walk-forward**(早 panel 訓、晚 panel 測、embargo 保證下界)→ direction_oos_sample
   (誠實 OOS p_up/y_up,餵 evaluate_direction_gate 判 GATE)。零新資料:absolute 標籤全導自現成 fwd_ret。
   多 seed:Logit 無隨機性 → seed 記 0(#11)。個股準確率禁單看(#憲章)——GATE 只判 horizon 級聚合。

守 #8(輸入分量皆已 OOS;合成器 embargo 折)· #12(折口徑複用 walkforward)· #9(標籤導自現成 fwd_ret 可溯)
   · #28(本機 sklearn)· #29a/d。前置=train_market_direction.py --run(P_mkt)+probability_oos_sample(相對)。
   SSOT=reports/augur_oracle_upgrade_master_plan_20260711.md §2.3。

執行指令矩陣:
  python scripts/train_direction_stack.py                       # 無參數:現況(唯讀:可合成 horizon×覆蓋)
  python scripts/train_direction_stack.py --run                 # 全可合成 horizon → direction_oos_sample
  python scripts/train_direction_stack.py --run --horizons 20   # 指定 horizon
  python scripts/train_direction_stack.py --run-v2              # v2:DirStackM 月頻(H20/40/82;revival §3.4)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db
from augur.evaluation import label as _label
from augur.evaluation import walkforward

H_HORIZONS = (20, 40, 82, 120)
MODEL_ID = "DirStack"
MKT_MODEL = "MktLogit"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _load_joined(cur, h):
    """join probability_oos_sample(相對,季度再平衡 panel)× market_direction_probability(市場,每日)。
    相對 panel 常落日曆期末(可能非交易日)→ 市場分量取「最近交易日 ≤ 相對 panel 之 P_mkt」(as-of 對齊,
    #8 安全:panel_date≤s.panel_date 於 s.panel_date 當下可見、且該 P_mkt 本身已 walk-forward OOS)。
    回 list[(panel_date, stock_id, rank_pctile, fwd_ret, p_mkt)]。"""
    cur.execute("""
        SELECT s.panel_date, s.stock_id, s.rank_pctile, s.fwd_ret, m.p_mkt_up
        FROM probability_oos_sample s
        JOIN LATERAL (
            SELECT p_mkt_up FROM market_direction_probability
            WHERE horizon = s.horizon AND model_id = %s AND panel_date <= s.panel_date
            ORDER BY panel_date DESC LIMIT 1
        ) m ON true
        WHERE s.horizon = %s AND s.rank_pctile IS NOT NULL AND s.fwd_ret IS NOT NULL
        ORDER BY s.panel_date, s.stock_id""", (MKT_MODEL, h))
    return cur.fetchall()


def _features(rank_pctile, p_mkt):
    """[logit(P_mkt), rank_pctile(中心化), 交互項]。P_mkt clip 防 logit 爆。"""
    pm = np.clip(np.asarray(p_mkt, float), 1e-4, 1 - 1e-4)
    lg = np.log(pm / (1 - pm))
    rk = np.asarray(rank_pctile, float) - 0.5
    return np.column_stack([lg, rk, lg * rk])


def _fit_predict(Xtr, ytr, Xte):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    if len(set(ytr)) < 2:
        return np.full(len(Xte), float(np.mean(ytr)))
    sc = StandardScaler().fit(Xtr)
    clf = LogisticRegression(penalty="l2", C=1.0, max_iter=1000).fit(sc.transform(Xtr), ytr)
    return clf.predict_proba(sc.transform(Xte))[:, 1]


def run(horizons, min_train):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cal = _label.full_calendar(conn)
        done = []
        for h in horizons:
            rows = _load_joined(cur, h)
            if not rows:
                print(f"  H{h:<3} 無可合成列(需 probability_oos_sample h={h} + P_mkt 皆就位)—略")
                continue
            panels = sorted({r[0] for r in rows})
            by_panel = {}
            for pd_, sid, rk, fr, pm in rows:
                by_panel.setdefault(pd_, []).append((sid, float(rk), float(fr), float(pm)))
            folds = walkforward.splits(panels, h, calendar=cal, min_train=min_train)
            wrote = 0
            for fid, fold in enumerate(folds):
                tr_rows = [x for p in fold["train"] for x in by_panel.get(p, [])]
                te = by_panel.get(fold["test"], [])       # test=單一 panel(walkforward.splits)
                if not tr_rows or not te:
                    continue
                Xtr = _features([r[1] for r in tr_rows], [r[3] for r in tr_rows])
                ytr = np.array([1 if r[2] > 0 else 0 for r in tr_rows])
                Xte = _features([r[1] for r in te], [r[3] for r in te])
                pred = _fit_predict(Xtr, ytr, Xte)
                for (sid, rk, fr, pm), pr in zip(te, pred):
                    cur.execute(
                        "INSERT INTO direction_oos_sample "
                        "(model_id, target_id, panel_date, horizon, p_up, y_up, fwd_abs_ret, fold_id, seed, git_sha) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,%s) "
                        "ON CONFLICT (model_id, target_id, panel_date, horizon, seed) DO UPDATE SET "
                        "p_up=EXCLUDED.p_up, y_up=EXCLUDED.y_up, fwd_abs_ret=EXCLUDED.fwd_abs_ret, "
                        "fold_id=EXCLUDED.fold_id, git_sha=EXCLUDED.git_sha, created_at=now()",
                        (MODEL_ID, sid, fold["test"], h, float(pr), 1 if fr > 0 else 0, fr, fid, git7))
                    wrote += 1
            conn.commit()
            ally = [1 if x[2] > 0 else 0 for r in by_panel.values() for x in r]
            base = float(np.mean(ally)) if ally else float("nan")
            print(f"  H{h:<3} folds={len(folds)} 寫 OOS {wrote} 列 | 個股絕對上漲基率 p̄={base:.3f} "
                  f"多數類基線 max(p̄,1−p̄)={max(base,1-base):.3f} n={len(ally)}")
            done.append(h)
    print(f"✓ DirStack 合成完成 horizon={done}(下一棒:evaluate_direction_gate.py --evaluate 判 GATE)")
    return 0


def run_v2(horizons, min_train):
    """v2(revival plan §3.4):DirStackM——月頻 panel(檢定力誠實 ×1.5~2)+豐富特徵直餵
    [logit(P_mkt_v2), rank−0.5, 交互, vol60, mom60, beta252, inst_z];標籤=PriceAdj 月末 h td 前瞻方向
    (自算,不再抄 probability_oos_sample.fwd_ret);市場分量=MktLogit_v2(criteria 預先鎖定、無 challenger
    選擇)。判門窗由 gate criteria 凍結(方案 A=2021-04+),此處全窗訓練、estimand 過濾住 evaluate。"""
    import hashlib
    model_id, mkt_model = "DirStackM", "MktLogit_v2"
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cal = _label.full_calendar(conn)
        # 月頻特徵 → wide
        cur.execute("SELECT panel_date, target_id, feature, value FROM direction_stack_feature_monthly")
        df_rows = cur.fetchall()
        if not df_rows:
            print("✗ 無 direction_stack_feature_monthly(先跑 build_direction_stack_monthly.py --run)"); return 1
        import pandas as pd
        df = pd.DataFrame(df_rows, columns=["panel", "stock", "feature", "value"])
        wide = df.pivot_table(index=["panel", "stock"], columns="feature", values="value").reset_index()
        panels = sorted(wide["panel"].unique())
        stocks = sorted(wide["stock"].unique())
        print(f"DirStackM:月頻 {len(panels)} panel × {len(stocks)} 檔")
        base_feats = ["m_vol_60", "m_mom_60", "m_beta_252", "m_inst_net_z"]
        fh_src = base_feats + ["logit_pmkt", "rank", "interaction"]
        fh = hashlib.sha256(",".join(sorted(fh_src)).encode()).hexdigest()[:16]
        cur.execute("INSERT INTO model_registry (model_id, family, horizon, train_span, asof_snapshot, "
                    "feats_hash, seed, artifact_path, git_sha) VALUES (%s,'DirStackM',0,%s,%s,%s,0,%s,%s) "
                    "ON CONFLICT (model_id) DO NOTHING",
                    (model_id, "[2017-01-01,2026-05-31]", "2026-05-31", fh,
                     "walk_forward_refit_per_fold(monthly stack)", git7))
        conn.commit()
        # 日價 → 每股 date→close 序(標籤自算)
        cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
            WHERE stock_id = ANY(%s) AND date >= '2016-06-01' AND date <= '2026-05-31'
            ORDER BY stock_id, date""", (stocks,))
        px = {}
        for sid, d_, c_ in cur.fetchall():
            px.setdefault(sid, ([], []))
            px[sid][0].append(d_); px[sid][1].append(float(c_))
        pxi = {sid: ({d: i for i, d in enumerate(ds)}, cs) for sid, (ds, cs) in px.items()}

        for h in horizons:
            rank_col = f"rank_pctile_h{h}"
            if rank_col not in wide.columns:
                print(f"  H{h:<3} 無 {rank_col}—略"); continue
            # P_mkt as-of per panel
            pmk = {}
            for p in panels:
                cur.execute("SELECT p_mkt_up FROM market_direction_probability "
                            "WHERE horizon=%s AND model_id=%s AND panel_date<=%s "
                            "ORDER BY panel_date DESC LIMIT 1", (h, mkt_model, p))
                r = cur.fetchone()
                if r:
                    pmk[p] = float(r[0])
            by_panel = {}
            for _, r in wide.iterrows():
                p, sid = r["panel"], r["stock"]
                if p not in pmk or not np.isfinite(r.get(rank_col, np.nan)):
                    continue
                idx, cs = pxi.get(sid, ({}, []))
                i = idx.get(p)
                if i is None or i + h >= len(cs) or cs[i] <= 0:
                    continue
                fr = cs[i + h] / cs[i] - 1.0
                by_panel.setdefault(p, []).append(
                    (sid, float(r[rank_col]), fr, pmk[p],
                     [r.get(c, np.nan) for c in base_feats]))
            pks = sorted(by_panel)
            if len(pks) < min_train + 3:
                print(f"  H{h:<3} 可用 panel 僅 {len(pks)}—略"); continue
            folds = walkforward.splits(pks, h, calendar=cal, min_train=min_train)
            wrote = 0
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler

            def _X(rows_):
                pm = np.clip(np.array([x[3] for x in rows_], float), 1e-4, 1 - 1e-4)
                lg = np.log(pm / (1 - pm))
                rk = np.array([x[1] for x in rows_], float) - 0.5
                ex = np.array([x[4] for x in rows_], float)
                return np.column_stack([lg, rk, lg * rk, ex])

            for fid, fold in enumerate(folds):
                tr_rows = [x for p in fold["train"] for x in by_panel.get(p, [])]
                te = by_panel.get(fold["test"], [])
                if len(tr_rows) < 200 or not te:
                    continue
                ytr = np.array([1 if x[2] > 0 else 0 for x in tr_rows])
                if len(set(ytr)) < 2:
                    pred = np.full(len(te), float(np.mean(ytr)))
                else:
                    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                         LogisticRegression(penalty="l2", C=1.0, max_iter=1000))
                    pipe.fit(_X(tr_rows), ytr)
                    pred = pipe.predict_proba(_X(te))[:, 1]
                for (sid, rk_, fr, pm_, _ex), pr in zip(te, pred):
                    cur.execute(
                        "INSERT INTO direction_oos_sample "
                        "(model_id, target_id, panel_date, horizon, p_up, y_up, fwd_abs_ret, fold_id, seed, git_sha) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,%s) "
                        "ON CONFLICT (model_id, target_id, panel_date, horizon, seed) DO UPDATE SET "
                        "p_up=EXCLUDED.p_up, y_up=EXCLUDED.y_up, fwd_abs_ret=EXCLUDED.fwd_abs_ret, "
                        "fold_id=EXCLUDED.fold_id, git_sha=EXCLUDED.git_sha, created_at=now()",
                        (model_id, sid, fold["test"], h, float(pr), 1 if fr > 0 else 0, fr, fid, git7))
                    wrote += 1
            conn.commit()
            ally = [1 if x[2] > 0 else 0 for rs in by_panel.values() for x in rs]
            base = float(np.mean(ally)) if ally else float("nan")
            print(f"  H{h:<3} 月頻 folds={len(folds)} 寫 OOS {wrote} 列 | p̄={base:.3f} n={len(ally)} "
                  f"panels={len(pks)}({pks[0]}~{pks[-1]})")
    print("✓ DirStackM 完成(判門=evaluate 依 criteria estimand:model_id+窗過濾)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT horizon, count(*) FROM probability_oos_sample GROUP BY horizon ORDER BY horizon")
        rel = dict(cur.fetchall())
        cur.execute("SELECT horizon, count(*) FROM market_direction_probability WHERE model_id=%s GROUP BY horizon", (MKT_MODEL,))
        mkt = dict(cur.fetchall())
        cur.execute("SELECT horizon, count(*) FROM direction_oos_sample GROUP BY horizon ORDER BY horizon")
        oos = dict(cur.fetchall())
    print("可合成性(需相對 & 市場分量皆 >0):")
    for h in H_HORIZONS:
        r, m = rel.get(h, 0), mkt.get(h, 0)
        print(f"  H{h:<3} 相對={r} 市場={m} → {'✓可合成' if r and m else '✗缺分量'} | 已產 OOS={oos.get(h,0)}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--run-v2", action="store_true", dest="v2")   # DirStackM 月頻(revival §3.4)
    ap.add_argument("--horizons", nargs="*", type=int)
    ap.add_argument("--min-train", dest="min_train", type=int)
    args = ap.parse_args()
    if args.v2:
        return run_v2(args.horizons or [20, 40, 82], args.min_train or 24)
    if args.run:
        return run(args.horizons or list(H_HORIZONS), args.min_train or 8)
    return status()


if __name__ == "__main__":
    sys.exit(main())
