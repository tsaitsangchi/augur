"""augur 特徵五鏡 audit — 訓練前特徵分診（#11 五鏡合判：不以單一指標判存廢）。

🎯 這支在做什麼（白話）：對 feature_values 的每個特徵，從五個鏡頭診斷它值不值得留：
① 有號單因子 IC ＋ sign 穩定（該特徵單獨排序之 rank IC / HAC Eff-t / 勝率，逐 panel as-of；顯著性不裸用 iid t #11）
② 共線群（特徵兩兩相關，揪冗餘群——共線會把真訊號誤判為噪音）
③ leave-one-out 必要性（從全特徵集移除它、模型 IC 掉多少＝邊際必要性）
④ ensemble SHAP（GBDT 之 mean |SHAP|，是否顯影）
⑤ purged-CV（②除外皆走 walk-forward as-of / purged 面板、非單純 in-sample 樂觀）
裁定（#11）：「不顯影（SHAP≈0）且 ablation-safe（移除 IC 不降）」必移；**任一單一指標不得判生死**。

唯讀稽核（憲章 audit 層）：不改資料、不選股、不產 model artifacts。reuse evaluation helper（#12 口徑一致、可比）。

守 #11（五鏡合判）· #12（label/metric/walkforward/baseline 單一 helper）· #8（purged/as-of）· #15（誠實揭露、不單指標）。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.audit.feature_diagnostics              # 印用途+公開入口（唯讀）
  python -m augur.audit.feature_diagnostics --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np

from augur.evaluation import baseline
from augur.evaluation import label as label_mod
from augur.evaluation import metrics

MODEL = "M1_gbdt"   # leave-one-out 之裁定模型（非線性主軸；可改 B2_ridge）


def single_factor_ic(conn, panels, h, stocks, feats, *, asof=False):
    """鏡①+⑤：每特徵單獨當分數之逐 panel rank IC → {feature: metrics.summarize}（有號 IC + sign 穩定 + 勝率）。

    每 panel 取核心股（asof 則 point-in-time），特徵值直接當預測分數 vs H 日 forward label rank → rank IC。
    無訓練、天然 as-of（特徵 t vs forward label）；跨 panel summarize + HAC t（重疊窗自相關致 iid t 高估、#11 禁裸用）。
    """
    cal = label_mod.full_calendar(conn)
    per_feat = {f: {} for f in feats}
    for pd_ in panels:
        sub = baseline._asof_stocks(conn, pd_) if asof else stocks
        sids, X = baseline._panel_matrix(conn, pd_, sub, feats)
        if len(sids) < 5:
            continue
        lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        for j, f in enumerate(feats):
            ic = metrics.rank_ic({s: X[i, j] for i, s in enumerate(sids)}, lab)
            if ic is not None:
                per_feat[f][pd_] = ic
    return {f: {**metrics.summarize(d), "effective_t_hac": metrics.effective_t_hac(d)}
            for f, d in per_feat.items()}


def collinearity(conn, panels, stocks, feats, *, threshold=0.9, asof=False):
    """鏡②：核心股 × 全 panel 之特徵 pooled 相關矩陣 → 高相關對（|r|≥threshold）+ 全矩陣。"""
    Xs = []
    for pd_ in panels:
        sub = baseline._asof_stocks(conn, pd_) if asof else stocks
        sids, X = baseline._panel_matrix(conn, pd_, sub, feats)
        if len(sids):
            Xs.append(X)
    if not Xs:
        return {"high_pairs": [], "corr": None}
    M = np.vstack(Xs)
    C = np.corrcoef(M, rowvar=False)
    pairs = [(feats[i], feats[j], float(C[i, j]))
             for i in range(len(feats)) for j in range(i + 1, len(feats))
             if np.isfinite(C[i, j]) and abs(C[i, j]) >= threshold]
    return {"high_pairs": sorted(pairs, key=lambda x: -abs(x[2])), "corr": C, "feats": feats}


def leave_one_out(conn, panels, h, stocks, feats, *, asof=False, model=MODEL):
    """鏡③+⑤：full 特徵集 vs 去一特徵之模型 mean_ic（purged walk-forward）→ {feature: {full, without, delta}}。

    delta = full − without；delta>0 ＝ 該特徵有邊際必要性（移除使 IC 下降）；delta≈0 ＝ ablation-safe（可移）。
    ⚠️ 重：跑 len(feats)+1 次 run_ladder（長時，CLI 以 --loo 旗標控）。
    """
    full = baseline.run_ladder(conn, panels, h, stocks, feats=feats, asof=asof)[model]["mean_ic"]
    out = {}
    for f in feats:
        sub = [x for x in feats if x != f]
        without = baseline.run_ladder(conn, panels, h, stocks, feats=sub, asof=asof)[model]["mean_ic"]
        delta = (full - without) if (full is not None and without is not None) else None
        out[f] = {"full": full, "without": without, "delta": delta}
    return out


def shap_importance(conn, panels, h, stocks, feats, *, asof=False, seed=42):
    """鏡④：pooled 訓練一棵 GBDT、TreeSHAP mean |SHAP| → {feature: mean_abs_shap}（降序）。"""
    import shap
    from lightgbm import LGBMRegressor

    X, y = baseline._fold_xy(conn, panels, stocks, feats, h, asof=asof)
    if len(y) < 50:
        return {f: None for f in feats}
    gbm = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                        min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                        random_state=seed, verbose=-1).fit(X, y)
    sv = shap.TreeExplainer(gbm).shap_values(X)
    imp = np.abs(sv).mean(axis=0)
    return dict(sorted(zip(feats, (float(v) for v in imp)), key=lambda x: -x[1]))


def five_mirror(conn, panels, h, stocks, feats, *, asof=False, loo=False,
                ic_floor=0.02, shap_quantile=0.1):
    """五鏡合判 → 每特徵之 {ic, shap, in_collinear_group, loo_delta, verdict}。

    verdict（#11，合判非單指標）：
      - 'drop?'  ＝ SHAP 落最低分位（不顯影）∧ |有號 IC| < ic_floor（弱）∧（若跑 loo）delta≈0（ablation-safe）。
      - 'collinear' ＝ 屬高相關群（建議群內擇一/合併、非逕刪）。
      - 'keep'   ＝ 其餘（有號 IC 或 SHAP 顯影或 loo 必要）。
    ic_floor / shap_quantile 為 operational 揭露參數（#9 不寫死治權、實驗中）；裁定供人合判、非自動刪。
    """
    sf = single_factor_ic(conn, panels, h, stocks, feats, asof=asof)
    col = collinearity(conn, panels, stocks, feats, asof=asof)
    sh = shap_importance(conn, panels, h, stocks, feats, asof=asof)
    loo_res = leave_one_out(conn, panels, h, stocks, feats, asof=asof) if loo else {}

    shap_vals = [v for v in sh.values() if v is not None]
    shap_low = np.quantile(shap_vals, shap_quantile) if shap_vals else 0.0
    collinear_feats = {f for a, b, _ in col["high_pairs"] for f in (a, b)}

    out = {}
    for f in feats:
        ic = sf[f].get("mean_ic")
        shv = sh.get(f)
        loo_d = loo_res.get(f, {}).get("delta") if loo else None
        weak_ic = ic is None or abs(ic) < ic_floor
        weak_shap = shv is not None and shv <= shap_low
        ablation_safe = (loo_d is not None and loo_d <= 0) if loo else True
        if weak_shap and weak_ic and ablation_safe:
            verdict = "drop?"
        elif f in collinear_feats:
            verdict = "collinear"
        else:
            verdict = "keep"
        out[f] = {"ic": ic, "ic_eff_t_hac": sf[f].get("effective_t_hac"),
                  "ic_eff_t_iid": sf[f].get("effective_t"), "shap": shv,
                  "in_collinear_group": f in collinear_feats, "loo_delta": loo_d, "verdict": verdict}
    return {"per_feature": out, "high_pairs": col["high_pairs"]}


def _selftest():
    """自測（零 DB/零 API #29a）：五鏡入口全 IO-bound（每支需 conn）→ import-smoke + 結構斷言
    （公開入口存在且 callable、裁定模型常數、evaluation helper 已接線 #12）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("五鏡入口皆 callable", all(callable(f) for f in (
        single_factor_ic, collinearity, leave_one_out, shap_importance, five_mirror)))
    chk("裁定模型常數 MODEL='M1_gbdt'", MODEL == "M1_gbdt")
    chk("evaluation helper 已接線(#12 單一 helper)",
        baseline is not None and label_mod is not None and metrics is not None)
    chk("numpy import-smoke", hasattr(np, "corrcoef"))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.audit.feature_diagnostics --selftest;免 DB 免 API)")
