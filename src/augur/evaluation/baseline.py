"""augur M-1 基準階梯 — B0 隨機 / B1 動能 / B2 Ridge / M1 GBDT 之 purged walk-forward rank IC。

🎯 這支在做什麼（白話）：F3 model 的第一個可驗證 MVP——對核心股、用 feature_values 的特徵預測 H 日
橫斷面相對強弱（label 層造），跑「基準階梯」逐階比較，每階都過 purged walk-forward（#8）、報 rank IC：
- **B0 隨機**：零假設地板（隨機排序、IC≈0）——任何模型贏不了它即無意義。
- **B1 動能**：單因子（momentum_20d），最廉價可行解。
- **B2 Ridge**：線性可達上限。
- **M1 GBDT**（LightGBM）：主軸，非線性交互——不贏 B2 即「非線性無增量」（誠實記錄 #15）。

evaluation **自包含雙軌**（憲章第三部、#12）：本層自己 train→predict、**不讀 model 層 artifacts**（防汙染）；
label/walkforward/metrics 全 import SSOT helper（跨模型可比）。stochastic（#15）：GBDT 多 seed 取統計——
MVP 先單 seed、M-2 再 ≥3 seed（本檔 `seeds` 參數預留）。

守 #8（label 層 t+1 + walkforward purge）· #12（SSOT helper）· #14（排序 IC、非 AUC）· #15（基準階梯逐階誠實、raw IC 雙口徑待 M-2）。
"""
from __future__ import annotations

import numpy as np

from augur.core import db
from augur.evaluation import cross_section
from augur.evaluation import label as label_mod
from augur.evaluation import metrics, walkforward

FEATURE_TABLE = "feature_values"
ASOF_TABLE = "core_universe_asof"
CANDIDATE_TABLE = "feature_candidate_values"   # audit 層候選 staging（憲章 audit 邊界:生產表 feature 層獨佔寫）——存在才併讀


def canonical_features(conn, panel_dates):
    """模型特徵集 = 在**每個 panel 都出現**之特徵（交集）——某特徵僅部分 panel 覆蓋（如 gov_bank 早於源表
    2021-07、早期 panel 缺列）則排除,確保跨 panel 特徵維度一致、不因部分缺格使整 panel 落空（審查 G9 評估層對偶；
    由資料判定、反硬編）。"""
    pds = list(panel_dates)
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT feature FROM {FEATURE_TABLE} WHERE panel_date = ANY(%s) "
                    f"GROUP BY feature HAVING count(DISTINCT panel_date) = %s", (pds, len(pds)))
        return sorted(r[0] for r in cur.fetchall())


def _panel_matrix(conn, panel_date, stocks, feats):
    """組 panel 之特徵矩陣 → (stock_ids[k], X[k×f])。只收「全 feats 齊」之股（core 股應全齊）。"""
    fset = set(stocks)
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT stock_id, feature, value FROM {FEATURE_TABLE} WHERE panel_date=%s AND feature = ANY(%s)",
                    (panel_date, feats))
        rows = cur.fetchall()
        cur.execute("SELECT to_regclass(%s) IS NOT NULL", (CANDIDATE_TABLE,))
        if cur.fetchone()[0]:   # 候選 staging 併讀（僅補 feats 內明點名之候選;canonical_features 不看此表 → core 不受污染）
            cur.execute(f"SELECT stock_id, feature, value FROM {CANDIDATE_TABLE} WHERE panel_date=%s AND feature = ANY(%s)",
                        (panel_date, feats))
            rows += cur.fetchall()
    by_stock = {}
    for sid, f, v in rows:
        sid = str(sid)
        if sid in fset:
            by_stock.setdefault(sid, {})[f] = float(v)
    sids, X = [], []
    for sid, fv in by_stock.items():
        if len(fv) == len(feats):                       # 全 feats 齊（缺任一不入；core 股應齊）
            sids.append(sid)
            X.append([fv[f] for f in feats])
    return sids, np.array(X, dtype=float) if X else np.empty((0, len(feats)))


def _asof_stocks(conn, panel_date):
    """讀該 as_of_date 之 point-in-time 核心名單（core_universe_asof、#8 消 survivorship）。"""
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT stock_id FROM {ASOF_TABLE} WHERE as_of_date=%s", (panel_date,))
        return [r[0] for r in cur.fetchall()]


def _fold_xy(conn, panels, stocks, feats, h, calendar=None, asof=False, interactions=None):
    """組多 panel 之 (X, y_rank, panel_index)：y=H 日 forward 橫斷面 rank label。供 train 用。
    asof=True 則每 panel 用該 panel 之 as-of 核心（point-in-time、#8）；False 用固定 stocks。
    interactions（opt-in）：每 panel 在 _panel_matrix 後、vstack 前對該 panel 橫斷面算交互 z 乘積
    （cross_section.augment、綁當下宇宙 #8）；None＝不動既有行為。"""
    Xs, ys = [], []
    for pd_ in panels:
        sub = _asof_stocks(conn, pd_) if asof else stocks
        sids, X = _panel_matrix(conn, pd_, sub, feats)
        if len(sids) == 0:
            continue
        if interactions:
            X, _ = cross_section.augment(X, feats, interactions)          # 逐 panel 橫斷面 z 乘積（vstack 前、當下宇宙）
        lab = label_mod.labels(conn, pd_, sids, h, calendar=calendar)      # {sid: rank}
        keep = [(i, s) for i, s in enumerate(sids) if s in lab]
        if not keep:
            continue
        idx = [i for i, _ in keep]
        Xs.append(X[idx])
        ys.append(np.array([lab[s] for _, s in keep]))
    if not Xs:
        return np.empty((0, len(feats) + len(interactions or []))), np.empty(0)
    return np.vstack(Xs), np.concatenate(ys)


def run_ladder(conn, panel_dates, h, stocks, *, feats=None, seed=42, mom_feature="momentum_20d", asof=False, robust=False, interactions=None):
    """跑基準階梯 B0/B1/B2/M1 之 purged walk-forward → {model: metrics.summarize}。

    每折：train panels 組 (X,y) fit → test panel predict → rank IC（vs test forward label）。
    B0 隨機、B1 動能（test 的 mom_feature 值直接當分數）、B2 Ridge、M1 LGBM。跨折 summarize。
    asof=True 則每 panel 用該 panel 之 as-of 核心（point-in-time、消 survivorship #8）；False 用固定 stocks（pan-historical）。
    """
    from lightgbm import LGBMRegressor
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import RobustScaler, StandardScaler   # robust=True 用 RobustScaler(median/IQR、抗離群、解 pe_ratio 尾 C1)

    feats = feats or canonical_features(conn, panel_dates)
    mom_idx = feats.index(mom_feature) if mom_feature in feats else None
    folds = walkforward.splits(panel_dates, h)
    cal = label_mod.full_calendar(conn)                 # 全日曆一次 query、逐折重用（免 N² 全表掃描）
    rng = np.random.default_rng(seed)
    ic = {m: {} for m in ("B0_random", "B1_momentum", "B2_ridge", "M1_gbdt")}

    for fold in folds:
        test_pd = fold["test"]
        test_stocks = _asof_stocks(conn, test_pd) if asof else stocks
        ts_sids, Xte = _panel_matrix(conn, test_pd, test_stocks, feats)
        if len(ts_sids) < 5:
            continue
        if interactions:
            Xte, _ = cross_section.augment(Xte, feats, interactions)     # test 側逐 panel 橫斷面 z（同 train 口徑、當下宇宙）
        lab = label_mod.labels(conn, test_pd, ts_sids, h, calendar=cal)  # test 真 label
        keep = [i for i, s in enumerate(ts_sids) if s in lab]
        if len(keep) < 5:
            continue
        Xte, ts_sids = Xte[keep], [ts_sids[i] for i in keep]
        ylab = {s: lab[s] for s in ts_sids}

        Xtr, ytr = _fold_xy(conn, fold["train"], stocks, feats, h, calendar=cal, asof=asof, interactions=interactions)
        if len(ytr) < 50:                                              # train 樣本太少 → 跳折
            continue

        # B0 隨機
        ic["B0_random"][test_pd] = metrics.rank_ic(dict(zip(ts_sids, rng.standard_normal(len(ts_sids)))), ylab)
        # B1 動能（test 的 momentum 值直接排序）
        if mom_idx is not None:
            ic["B1_momentum"][test_pd] = metrics.rank_ic(dict(zip(ts_sids, Xte[:, mom_idx])), ylab)
        # B2 Ridge（標準化 + 線性;robust=True 用 RobustScaler 抗離群）
        sc = (RobustScaler() if robust else StandardScaler()).fit(Xtr)
        rdg = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)
        ic["B2_ridge"][test_pd] = metrics.rank_ic(dict(zip(ts_sids, rdg.predict(sc.transform(Xte)))), ylab)
        # M1 GBDT
        gbm = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                            min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                            random_state=seed, verbose=-1).fit(Xtr, ytr)
        ic["M1_gbdt"][test_pd] = metrics.rank_ic(dict(zip(ts_sids, gbm.predict(Xte))), ylab)

    # 顯著性顯示以 HAC t 為準（重疊窗自相關致 iid effective_t 高估、#11 禁裸用）
    return {m: {**metrics.summarize(d), "effective_t_hac": metrics.effective_t_hac(d)}
            for m, d in ic.items()}
