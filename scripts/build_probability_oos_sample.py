#!/usr/bin/env python
"""機率校準 OOS 對樣本 emit — walk-forward 逐折 refit 同族 Ridge、落 probability_oos_sample(e2e 主計畫 P2/§6.2)。

🎯 這支在做什麼(白話):對每個 horizon,用 revalidate **同一套** walk-forward 折(#12 零雙軌:
   `walkforward.splits`+`baseline._asof_stocks/_panel_matrix`+`label` SSOT,折內 StandardScaler+Ridge(α=1.0)
   同族 refit),把每折 OOS 的(股, 分數, 橫斷面分位, 已實現 forward return, 同儕中位數, 相對標籤, exit_date)
   逐列落 `probability_oos_sample`——這是 P6 機率校準器唯一合法的 fit 對樣本(D3 落表;#10 可溯源)。
   **exit_date=標籤窗完全實現日(t+1 進場後第 h 交易日)**=purge 校準之機械斷言依據(#8:
   校準器僅得 fit 於 exit_date<fit_asof 之折)。分位方向契約:1=最強、與標籤同向(憲章 v1.40.0)。
   fwd_ret/peer_median 皆 FREEZE 內已實現、非未來(#8)。

守 #8(exit_date/embargo 折)· #10(全欄溯源)· #12(折/label/宇宙全複用 revalidate 同一 SSOT helper)·
   #15(算不出之折/股缺列不補)· CLAUDE #29a。SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §1.3/§5.2/§6.2。

執行指令矩陣:
  python scripts/build_probability_oos_sample.py                        # 無參數:各 horizon 折覆蓋矩陣(唯讀)
  python scripts/build_probability_oos_sample.py --run --horizon 60     # 單 horizon(冪等 per-fold DELETE+INSERT)
  python scripts/build_probability_oos_sample.py --run --all            # 封閉集 {5,20,40,60,90,120,240}
  python scripts/build_probability_oos_sample.py --run --horizon 60 --limit-folds 2   # 最小驗證(#25)
  python scripts/build_probability_oos_sample.py --run --horizon 60 --model-family RankXGB  # 另族(Phase 1 條件觸發)
  python scripts/build_probability_oos_sample.py --run --horizon 60 --asof 2026-05-31  # 快照錨(預設同左;滾動須 Steward 明示)
  python scripts/build_probability_oos_sample.py --verify               # purge 斷言:exit_date 全非 NULL 且=panel_date+h td

紀律(P6 選項 D 精神,2026-08-05):本管線預設視為歷史快照錨產物;無 --limit-folds 之全量 --run
  建議僅在 Steward 明示 as-of／範圍時執行。選項 C=--asof 可參數化,預設仍釘 DEFAULT_AS_OF,滾動≠自動。
"""
import argparse
import statistics
import subprocess
import sys
from datetime import date

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

from augur.core import db
from augur.core.closed_horizons import H_TRACK
from augur.evaluation import baseline, walkforward
from augur.evaluation import label as label_mod
from augur.models import ranker

HORIZONS = H_TRACK      # 作業封閉集；H90 取代 H82（2026-08-14）
DEFAULT_AS_OF = "2026-05-31"          # 預設快照錨(P6 選項 C:可 --asof 覆寫;滾動須另句授權,非改此常數即自動滾)
AS_OF = DEFAULT_AS_OF                 # 相容別名(狀態列／舊呼叫);runtime 以 CLI --asof 為準
MODEL_FAMILY = "RankRidge"            # 逐折 refit 同族(A-36 同族近似聲明之 family 錨);--model-family 可選其他 Wave-A 族
                                       # (S4-DIRFAMILY-GENERALIZE Phase 0,2026-08-04:泛化非新增族,見該計畫)


def _git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, cwd=_bootstrap.__file__.rsplit("/", 2)[0]
                              ).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _asof_panels(conn, as_of=DEFAULT_AS_OF):
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date <= %s ORDER BY 1", (as_of,))
        return [r[0] for r in cur.fetchall()]


def _exit_date(cal, panel_date, h):
    after = [d for d in cal if d > panel_date]
    if len(after) < h + 1:
        return None
    return after[h]


def emit_horizon(conn, h, feats, panels, cal, *, limit_folds=None, git_sha="unknown",
                 model_family=MODEL_FAMILY, as_of=DEFAULT_AS_OF):
    """單 horizon 逐折 emit;折邏輯逐行對齊 revalidate._b_ridge_ic(asof=True)(#12)。回 (folds_emitted, rows)。
    模型 fit 複用 augur.models.ranker(同 portfolio.py 既有 dispatch 模式,#12 零漂移)——
    非重寫超參字面,RankRidge 預設族與原 inline StandardScaler+Ridge(alpha=1.0) 逐行同組態。"""
    est_cls = {c.family: c for c in ranker.ALL_FAMILIES}[model_family]
    as_of_date = date.fromisoformat(as_of)

    folds = walkforward.splits(panels, h, calendar=cal)
    if limit_folds:
        folds = folds[-limit_folds:]   # 取最後 N 折(最早折 train 腿常不足會被誠實跳過,取尾端才有代表性 #25)
    n_folds, n_rows = 0, 0
    for fold in folds:
        test_pd = fold["test"]
        ts_sids, Xte = baseline._panel_matrix(conn, test_pd, baseline._asof_stocks(conn, test_pd), feats)
        if len(ts_sids) < 5:
            continue
        fwd = label_mod.forward_returns(conn, test_pd, ts_sids, h, calendar=cal)
        keep = [i for i, s in enumerate(ts_sids) if s in fwd]
        if len(keep) < 5:
            continue
        Xte, ts_sids = Xte[keep], [ts_sids[i] for i in keep]
        exit_d = _exit_date(cal, test_pd, h)
        if exit_d is None or exit_d > as_of_date:
            # 標籤窗未完全實現,或標籤實現日已外溢快照邊界 → 整折缺列(#8 不外推)。
            # 後者=選項 A 修補(S4-PROB-ASOF-BOUNDARY-FIX-20260804);as_of 由 CLI 傳入(預設 DEFAULT_AS_OF)。
            continue
        # 訓練腿:同 revalidate(as-of 宇宙、rank label)
        Xs, ys = [], []
        for pd_ in fold["train"]:
            sids, X = baseline._panel_matrix(conn, pd_, baseline._asof_stocks(conn, pd_), feats)
            if len(sids) == 0:
                continue
            l2 = label_mod.labels(conn, pd_, sids, h, calendar=cal)
            k2 = [(i, s) for i, s in enumerate(sids) if s in l2]
            if not k2:
                continue
            Xs.append(X[[i for i, _ in k2]])
            ys.append(np.array([l2[s] for _, s in k2]))
        if not Xs:
            continue
        Xtr, ytr = np.vstack(Xs), np.concatenate(ys)
        if len(ytr) < 50:
            continue
        est = est_cls().fit(Xtr, ytr)
        scores = dict(zip(ts_sids, (float(v) for v in est.predict(Xte))))
        pctl = label_mod.cross_sectional_rank(scores)          # 方向契約:1=最強(同 label 排序法,#12)
        med = statistics.median(fwd[s] for s in ts_sids)
        rows = [(h, test_pd, model_family, s, scores[s], pctl[s],
                 fwd[s], med, fwd[s] > med, exit_d, git_sha) for s in ts_sids]
        with db.transaction(conn) as cur:                      # 冪等:per-fold DELETE+INSERT
            cur.execute("DELETE FROM probability_oos_sample WHERE horizon=%s AND panel_date=%s AND model_family=%s",
                        (h, test_pd, model_family))
            cur.executemany(
                "INSERT INTO probability_oos_sample (horizon,panel_date,model_family,stock_id,score,"
                "rank_pctile,fwd_ret,peer_median_ret,label_beat_median,exit_date,git_sha) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
        n_folds += 1
        n_rows += len(rows)
        print(f"  ✓ H{h} fold {test_pd}(n={len(rows)}, exit={exit_d})")
    return n_folds, n_rows


def status(conn, as_of=DEFAULT_AS_OF):
    panels = _asof_panels(conn, as_of)
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        for h in HORIZONS:
            n_splits = len(walkforward.splits(panels, h, calendar=cal))
            cur.execute("SELECT count(DISTINCT panel_date), count(*) FROM probability_oos_sample WHERE horizon=%s", (h,))
            got_f, got_r = cur.fetchone()
            print(f"  H{h}: splits 可產 {n_splits} 折;已 emit {got_f} 折 / {got_r} 列")


def verify(conn) -> int:
    """purge 斷言:exit_date 全非 NULL 且 = panel_date 後第 (1+h)-1 個交易日(t+1 進場後第 h 日)。"""
    ok = True
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM probability_oos_sample WHERE exit_date IS NULL")
        n_null = cur.fetchone()[0]
        if n_null:
            print(f"✗ exit_date NULL {n_null} 列"); ok = False
        cur.execute("SELECT DISTINCT horizon, panel_date, exit_date FROM probability_oos_sample ORDER BY 1,2")
        combos = cur.fetchall()
    if not combos:
        print("✗ 空表(先 --run)"); ok = False
    for h, pd_, exit_got in combos:
        expect = _exit_date(cal, pd_, h)
        if exit_got != expect:
            print(f"✗ H{h} {pd_}: exit_date={exit_got} ≠ 期望 {expect}"); ok = False
    # 方向契約抽驗:每 (h,panel) 內 rank_pctile 最大者之 score 亦為最大
    with db.transaction(conn) as cur:
        cur.execute("""
            SELECT count(*) FROM (
              SELECT horizon, panel_date,
                     (array_agg(stock_id ORDER BY rank_pctile DESC))[1] AS by_pctl,
                     (array_agg(stock_id ORDER BY score       DESC))[1] AS by_score
              FROM probability_oos_sample GROUP BY 1,2) t
            WHERE by_pctl <> by_score""")
        n_bad = cur.fetchone()[0]
        if n_bad:
            print(f"✗ 方向契約破:{n_bad} 折 top-1 分位≠top-1 分數"); ok = False
    print("✓ --verify 全綠(purge 斷言+方向契約)" if ok else "✗ --verify 失敗")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--horizon", type=int, choices=HORIZONS)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit-folds", type=int, default=None)
    ap.add_argument("--model-family", default=MODEL_FAMILY, choices=[c.family for c in ranker.ALL_FAMILIES],
                     help="逐折 refit 之族(預設 RankRidge;Phase 1 條件觸發才用其他 Wave-A 族,見"
                          " augur_s4_dirfamily_generalize_plan_20260804.md)")
    ap.add_argument("--asof", default=DEFAULT_AS_OF,
                     help=f"快照錨(預設 {DEFAULT_AS_OF};P6 選項 C 參數化——滾動到其他日須 Steward 明示,見"
                          " augur_s4_p6_asof_cd_architecture_plan_20260805.md)")
    args = ap.parse_args()
    with db.connect() as conn:
        if args.verify:
            return verify(conn)
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            print(f"折覆蓋矩陣(唯讀;asof={args.asof}):")
            status(conn, args.asof)
            return 0
        hs = list(HORIZONS) if args.all else ([args.horizon] if args.horizon else None)
        if not hs:
            sys.exit("--run 需 --horizon H 或 --all")
        panels = _asof_panels(conn, args.asof)
        feats = baseline.canonical_features(conn, panels)
        cal = label_mod.full_calendar(conn)
        sha = _git_sha()
        print(f"feats={len(feats)} panels={len(panels)} git={sha} family={args.model_family} asof={args.asof}")
        for h in hs:
            nf, nr = emit_horizon(conn, h, feats, panels, cal, limit_folds=args.limit_folds, git_sha=sha,
                                  model_family=args.model_family, as_of=args.asof)
            print(f"H{h}: emit {nf} 折 / {nr} 列")
    return 0


if __name__ == "__main__":
    sys.exit(main())
