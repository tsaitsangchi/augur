#!/usr/bin/env python
"""組合層前瞻風險模擬 — 候選組合之 MaxDD 分布與歷史情境重放(模擬非預測;A 軌縮版 2026-07-25 hugo 拍板)。
🎯 這支在做什麼(白話):對單一部署 cell(預設 RankRidge_H60,33 檔等權**候選組合**——in_portfolio=候選、
   非部署事實)把成分股聚合成**一條投組日報酬序列**(固定權重;共同覆蓋日交集、缺值日剔除揭露、零補值 #1),
   然後:(a) 複用 simulate_mc_paths 既有 bootstrap 引擎模 n_paths 條 h 日路徑 → 終值/MaxDD 分布 +
   P(MaxDD<risk_policy 閾值)——**參考用**;(b) 2008/2020/2022 歷史片段確定性重放——**主結論**(能引入
   756td 窗外的尾部;bootstrap 產不出窗內不存在的事件=窗偏差,summary 硬綁揭露)。
   四鎖繼承 simulate_mc_paths:①模擬非預測 disclaimer 硬綁 ②只存 summary ③不入 chat payload ④憲章
   「路徑類需求唯以模擬情境滿足」(v1.46.0 第三部 validate);風控閾值單向唯讀(不回寫 risk_policy、不觸發降倉)。
守 #1(零補值)· #8(僅 ≤as-of;as-of 機械綁權重 panel_date)· #3/#12(複用引擎與 mc_simulation_run 表、零新表)·
   #15(裸投組無 overlay=保守口徑、窗偏差、存活者偏誤全硬綁揭露)· #28 · #29a/d。
執行指令矩陣:
  python scripts/simulate_portfolio_risk.py                       # 無參數:現況(唯讀:已存 PORT_ run)
  python scripts/simulate_portfolio_risk.py --run                 # RankRidge_H60 全套:bootstrap(h=60)+三 episode
  python scripts/simulate_portfolio_risk.py --run --episode 2008  # 只跑指定情境重放
  python scripts/simulate_portfolio_risk.py --run --cell RankRidge_H120 --n-paths 10000 --seed 42
  python scripts/simulate_portfolio_risk.py --compare --cell RankRidge_H60 # 四法對照表(唯讀帳本、零重算)
  python scripts/simulate_portfolio_risk.py --run --analog all    # M1 跨市場類比六窗(analog 硬標示)
  python scripts/simulate_portfolio_risk.py --run --analog us2008 # 單窗(校準錨:對照台股 2008)
  python scripts/simulate_portfolio_risk.py --selftest            # 零 DB 純紅綠(聚合數學/MaxDD 一致/揭露欄鎖)
註:bootstrap 族=四法(iid/block/stationary/garch_fhs;後二為 2026-07-26 方法擴充對照組——拆固定塊長/
   波動齊性假設;仍同窗重抽、episode 主結論地位不變)。garch_fhs 依賴 arch 套件、缺席 graceful SKIP。
"""
import argparse
import hashlib
import json
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.core import db
from augur.evaluation.portfolio import drawdown_series
from augur.execution.risk_control import load_policies
from simulate_mc_paths import BLOCK_LEN, PCTS, _garch_fhs_paths, _git7, _simulate, _stationary_paths

ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36

BOOT_METHODS = ("iid_bootstrap", "block_bootstrap", "stationary_bootstrap", "garch_fhs")

MIN_COMMON_TD = 252            # 共同覆蓋誠實下限(不足=fail-closed 拒跑、不硬出數字)
WINDOW_TD = 756
EPISODES = {"2008": ("2008-09-01", "2009-03-31"), "2020": ("2020-01-15", "2020-04-30"),
            "2022": ("2022-01-01", "2022-12-31"),
            # 五窗擴充(2026-07-27 預註冊凍結;SSOT=reports/augur_risk_sim_expansion_plan_20260727.md;
            # 不得因結果回改窗——要改=新名另註冊。覆蓋不足(<MIN_EPISODE_W_COVER)=誠實拒跑屬合法結果)
            "1997": ("1997-08-01", "1999-02-28"),   # 亞洲金融風暴+本土型金融風暴全段
            "2000": ("2000-02-01", "2001-09-30"),   # dot-com 崩跌全段含 911 谷底
            "2011": ("2011-02-01", "2011-12-31"),   # 歐債危機年
            "2015": ("2015-04-01", "2015-09-30"),   # A 股連動+8/24 全球閃崩
            "2018": ("2018-10-01", "2019-01-31")}   # 貿易戰急跌段
MIN_EPISODE_W_COVER = 0.70     # 情境重放權重覆蓋誠實下限
DISCLAIMER = ("組合層模擬情境(模擬非預測):候選組合歷史報酬之重抽/重放統計,非模型預測、非熔斷預告;"
              "固定權重無風控 overlay=裸投組保守口徑;與方向軸機率/risk_control 實際觸發判定分欄、永不混排。")


def _load_cell_portfolio(cur, cell):
    cur.execute("""SELECT panel_date, stock_id, weight FROM prediction_values
        WHERE model_id LIKE %s AND in_portfolio
          AND panel_date=(SELECT max(panel_date) FROM prediction_values)
        ORDER BY stock_id""", (cell + "%",))
    rows = cur.fetchall()
    if not rows:
        raise RuntimeError(f"cell {cell} 無候選組合列(prediction_values in_portfolio)")
    panel = rows[0][0]
    members = [(sid, float(w)) for _, sid, w in rows]
    wsum = sum(w for _, w in members)
    assert abs(wsum - 1.0) < 1e-6, f"權重和 {wsum} ≠ 1(cell 圈選錯誤?)"
    return panel, members


def _member_closes(cur, sids, since, until):
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    cur.execute(f"""SELECT stock_id, date, close FROM {adj_sql}
        WHERE stock_id = ANY(%s) AND date BETWEEN %s AND %s AND close > 0
        ORDER BY date""", (list(sids), since, until))
    by_stock = {}
    for sid, d, c in cur.fetchall():
        by_stock.setdefault(sid, {})[d] = float(c)
    return by_stock


def _portfolio_returns(members, by_stock, dates_all):
    """共同覆蓋日交集 → 固定權重投組簡單報酬序列。回 (rets, common_dates, dropped_n)。零補值(#1)。"""
    sids = [s for s, _ in members]
    common = [d for d in dates_all if all(d in by_stock.get(s, {}) for s in sids)]
    dropped = len(dates_all) - len(common)
    if len(common) < 2:
        return np.array([]), common, dropped
    rets = []
    for prev, cur_d in zip(common, common[1:]):
        r = sum(w * (by_stock[s][cur_d] / by_stock[s][prev] - 1.0) for s, w in members)
        rets.append(r)
    return np.array(rets), common, dropped


def _maxdd_per_path(paths):
    """paths=累積簡單報酬[n,h] → 各路徑 MaxDD(負值)。與 drawdown_series 同義之向量化版(selftest 鎖一致)。"""
    wealth = 1.0 + paths
    runmax = np.maximum.accumulate(wealth, axis=1)
    return (wealth / runmax - 1.0).min(axis=1)


def _bootstrap_summary(logr, h, n_paths, method, seed, policies, window_maxdd, meta):
    rng = np.random.default_rng(seed)
    fit_diag = None
    if method == "stationary_bootstrap":             # 方法擴充 2026-07-26:對照組(拆固定塊長假設)
        paths = _stationary_paths(logr, h, n_paths, BLOCK_LEN, rng)
    elif method == "garch_fhs":                      # 對照組(拆波動齊性假設);缺 arch → None=SKIP
        try:
            paths, fit_diag = _garch_fhs_paths(logr, h, n_paths, rng)
        except ImportError:
            return None
    else:
        paths = _simulate(logr, h, n_paths, method, BLOCK_LEN, rng)
    term, mdd = paths[:, -1], _maxdd_per_path(paths)
    dd_gate = policies.get("dd_circuit", {})
    thr = dd_gate.get("threshold")
    summ = {
        "disclaimer": DISCLAIMER, "kind": "bootstrap_reference", **meta,
        "terminal": {f"ret_p{p}": round(float(np.percentile(term, p)), 5) for p in PCTS},
        "maxdd": {f"p{p}": round(float(np.percentile(mdd, p)), 5) for p in PCTS},
        "p_maxdd_lt_policy": (None if thr is None else round(float((mdd < thr).mean()), 4)),
        "policy_threshold": thr,
        "p_maxdd_lt_info": {f"{t:+.0%}": round(float((mdd < t).mean()), 4) for t in (-0.10, -0.15)},
        "window_actual_maxdd": round(window_maxdd, 5),
        "note_policy": "P(MaxDD<閾)=歷史重抽之模擬統計,非模型預測、非熔斷預告;閾值唯讀自 risk_policy、"
                       "模擬結果不回寫不觸發;-10%/-15% 檔位=資訊性分位、非既有閾值",
        "note_window_bias": "重抽窗內無某級事件→該檔位機率≈0 係窗的性質、非安全證據;窗內實際最深回檔="
                            f"{window_maxdd:+.1%}(錨);主結論請看 episode_replay 列",
    }
    if fit_diag:
        summ["fit_diag"] = fit_diag                  # garch_fhs 擬合品質入帳可稽(方法擴充計畫 §二)
    return summ


def _episode_summary(members, by_stock, dates_all, name, policies, meta):
    sids = [s for s, _ in members]
    covered = [(s, w) for s, w in members if any(d in by_stock.get(s, {}) for d in dates_all)]
    w_cover = sum(w for _, w in covered)
    if w_cover < MIN_EPISODE_W_COVER:
        return {"disclaimer": DISCLAIMER, "kind": "episode_refused", **meta,
                "episode": name, "weight_coverage": round(w_cover, 4),
                "note": f"權重覆蓋 {w_cover:.0%} < {MIN_EPISODE_W_COVER:.0%} 誠實下限→拒答(不硬出數字,#15)"}
    renorm = [(s, w / w_cover) for s, w in covered]
    rets, common, dropped = _portfolio_returns(renorm, by_stock, dates_all)
    if len(rets) < 20:
        return {"disclaimer": DISCLAIMER, "kind": "episode_refused", **meta, "episode": name,
                "note": f"共同覆蓋僅 {len(rets)} td→拒答"}
    cum = float(np.prod(1.0 + rets) - 1.0)
    mdd = float(drawdown_series(list(rets))[1].min())
    return {
        "disclaimer": DISCLAIMER, "kind": "episode_replay", **meta,
        "episode": name, "span": [str(common[0]), str(common[-1])], "n_td": len(rets),
        "cum_return": round(cum, 5), "maxdd": round(mdd, 5),
        "weight_coverage": round(w_cover, 4), "n_members_covered": len(covered),
        "dropped_dates": dropped,
        "note_single_scenario": "歷史情境重放=單一確定性路徑,非機率、非分布、非預測;與 bootstrap 分布分欄永不混排",
        "note_survivor": "本重放含存活者偏誤:成分=今日候選組合(活到今天的股)、非當年可選集,結果偏樂觀",
        "note_renorm": f"未覆蓋成分已剔除、權重再正規化(={len(covered)}/{len(members)} 檔之縮水投組,明標非原組合)",
    }


# ── M2 EVT(POT-GPD 尾部;參數凍結於進階三法計畫 20260727) ──
EVT_U_Q = 0.05          # 門檻=經驗 5% 分位(凍結)
EVT_MIN_TAIL = 20       # 尾部樣本下限,不足即拒答(#15)
EVT_REFIT = 200         # ξ 之 95% CI 之 refit bootstrap 次數(凍結)


def _evt_summary(logr, h, n_paths, seed, policies, window_maxdd, meta):
    """混合重抽:主體經驗分布 + 左尾 GPD(scipy genpareto MLE);回 summary 或 None(拒答)。

    why 混合而非全 GPD:GPD 只描述超過門檻之尾部,主體照用經驗分布才不失真;
    結構假設仍同 iid(僅尾部校正)——時序相依請看 block/stationary 與 episode(揭露硬綁)。
    """
    from scipy import stats
    r = np.asarray(logr, dtype=float)
    u = float(np.quantile(r, EVT_U_Q))                 # 左尾門檻(對數報酬)
    exc = u - r[r < u]                                 # 超額(正值)
    if exc.size < EVT_MIN_TAIL:
        return {"kind": "evt_refused", "disclaimer": DISCLAIMER, **meta,
                "note": f"尾部樣本 n_tail={exc.size} < {EVT_MIN_TAIL}→拒答(不硬出數字,#15)",
                "threshold_u": round(u, 6), "n_tail": int(exc.size)}
    xi, loc, beta = stats.genpareto.fit(exc, floc=0.0)
    rng = np.random.default_rng(seed)
    body = r[r >= u]
    p_tail = float(exc.size) / float(r.size)
    # ξ 之 95% CI(refit bootstrap;#15 估計不確定性一併揭露)
    xis = []
    for _ in range(EVT_REFIT):
        s = rng.choice(exc, size=exc.size, replace=True)
        try:
            xis.append(float(stats.genpareto.fit(s, floc=0.0)[0]))
        except Exception:  # noqa: BLE001
            continue
    ci = [round(float(np.percentile(xis, 2.5)), 4), round(float(np.percentile(xis, 97.5)), 4)] if xis else None
    # 路徑:每步以 p_tail 機率抽尾(u - GPD 超額)、否則抽主體
    is_tail = rng.random((n_paths, h)) < p_tail
    draws = np.where(
        is_tail,
        u - stats.genpareto.rvs(xi, loc=0.0, scale=beta, size=(n_paths, h), random_state=rng),
        rng.choice(body, size=(n_paths, h), replace=True))
    # 與 _simulate 同一約定:**累積簡單報酬**(exp(cum_log)-1),非淨值。
    # 2026-07-27 實撞:少減 1 使整條路徑平移 +1、MaxDD 被系統性低估(EVT 反比 iid 溫和之假象)。
    paths = np.exp(np.cumsum(draws, axis=1)) - 1.0
    mdd = _maxdd_per_path(paths)
    thr = float(policies.get("maxdd_threshold", -0.2)) if isinstance(policies, dict) else -0.2
    return {"kind": "evt_pot_hybrid", "disclaimer": DISCLAIMER, **meta,
            "maxdd": {q: round(float(np.percentile(mdd, p)), 5)
                      for q, p in (("p5", 5), ("p25", 25), ("p50", 50), ("p95", 95))},
            "p_maxdd_lt_policy": round(float((mdd < thr).mean()), 4), "policy_threshold": thr,
            "threshold_u": round(u, 6), "n_tail": int(exc.size), "p_tail": round(p_tail, 4),
            "gpd_xi": round(float(xi), 4), "gpd_xi_ci95": ci, "gpd_beta": round(float(beta), 6),
            "window_maxdd": round(window_maxdd, 5), "n_paths": n_paths, "horizon_td": h, "seed": seed,
            "note_structure": "結構假設同 iid(僅尾部經 GPD 校正);時序相依看 block/stationary,窗外事件看 episode",
            "note_uncertainty": "尾部樣本少⇒ξ 估計不確定性大,95% CI 已附;點估計不可單獨引用"}


# ── M3 Copula-t + GARCH 邊際(進階三法計畫 20260727 凍結;補「相關性趨一」之洞) ──
COP_DOF_GRID = tuple(range(3, 31))   # t-copula 自由度格點(凍結)
COP_MIN_SURVIVE = 25                 # 邊際收斂存活下限(<25/33 整法拒答)


def _fit_marginals(rets_by_stock, sids):
    """逐股 GARCH(1,1)-t 邊際;回 (存活 sid, 標準化殘差矩陣[T,k], 參數表, 未收斂清單)。"""
    from arch.univariate import ConstantMean, GARCH, StudentsT
    keep, resid, params, failed = [], [], {}, []
    for s in sids:
        r = np.asarray(rets_by_stock[s], dtype=float) * 100.0   # arch 建議 % 尺度(數值穩定)
        try:
            am = ConstantMean(r); am.volatility = GARCH(1, 1); am.distribution = StudentsT()
            res = am.fit(disp="off", show_warning=False)
            z = np.asarray(res.std_resid, dtype=float)
            if not np.all(np.isfinite(z)):
                raise ValueError("non-finite std_resid")
            keep.append(s); resid.append(z)
            params[s] = {"nu": round(float(res.params.get("nu", np.nan)), 3),
                         "omega": float(res.params.get("omega", np.nan)),
                         "alpha": float(res.params.get("alpha[1]", np.nan)),
                         "beta": float(res.params.get("beta[1]", np.nan)),
                         "sigma_last": float(res.conditional_volatility[-1])}
        except Exception as e:  # noqa: BLE001
            failed.append({"stock": s, "reason": type(e).__name__})
    return keep, (np.column_stack(resid) if resid else np.empty((0, 0))), params, failed


def _fit_t_copula(z):
    """t-copula:Kendall's tau → Pearson R(穩健、避尾部污染)+dof 格點 MLE。回 (R, dof, tail_dep)。"""
    from scipy import special, stats
    k = z.shape[1]
    u = np.clip((np.argsort(np.argsort(z, axis=0), axis=0) + 0.5) / z.shape[0], 1e-6, 1 - 1e-6)
    tau = np.eye(k)
    for i in range(k):
        for j in range(i + 1, k):
            tau[i, j] = tau[j, i] = stats.kendalltau(z[:, i], z[:, j]).statistic or 0.0
    R = np.sin(np.pi * tau / 2.0)                      # tau → Pearson(橢圓族關係式)
    ev = np.linalg.eigvalsh(R)
    if ev.min() < 1e-8:                                # 投影回正定(最近相關矩陣之簡版)
        w, V = np.linalg.eigh(R)
        R = V @ np.diag(np.clip(w, 1e-8, None)) @ V.T
        d = np.sqrt(np.diag(R)); R = R / np.outer(d, d)
    Rinv = np.linalg.inv(R); _, logdet = np.linalg.slogdet(R)
    best = (None, -np.inf)
    for nu in COP_DOF_GRID:                            # profile MLE over dof grid
        t_q = stats.t.ppf(u, nu)
        q = np.einsum("ij,jk,ik->i", t_q, Rinv, t_q)
        ll = float(np.sum(
            special.gammaln((nu + k) / 2) - special.gammaln(nu / 2) - 0.5 * logdet
            - (k - 1) * (special.gammaln((nu + 1) / 2) - special.gammaln(nu / 2))
            - ((nu + k) / 2) * np.log1p(q / nu)
            + ((nu + 1) / 2) * np.sum(np.log1p(t_q ** 2 / nu), axis=1)))
        if ll > best[1]:
            best = (nu, ll)
    dof = best[0]
    rbar = float((R.sum() - k) / (k * (k - 1)))        # 平均非對角相關
    # 尾部相依係數 λ(等相關近似;t-copula 之閉式)
    lam = float(2 * stats.t.cdf(-np.sqrt((dof + 1) * (1 - rbar) / (1 + rbar)), dof + 1))
    return R, dof, {"avg_corr": round(rbar, 4), "tail_dep_lambda": round(lam, 4)}


def _copula_summary(rets_by_stock, weights, h, n_paths, seed, policies, window_maxdd, meta):
    """M3 主流程;回 summary 或拒答 dict。純計算(IO 在呼叫端)。"""
    from scipy import stats
    sids = [s for s, _ in weights]
    keep, z, params, failed = _fit_marginals(rets_by_stock, sids)
    if len(keep) < COP_MIN_SURVIVE:
        return {"kind": "copula_refused", "disclaimer": DISCLAIMER, **meta,
                "note": f"GARCH 邊際存活 {len(keep)}/{len(sids)} < {COP_MIN_SURVIVE}→整法拒答(#15)",
                "failed": failed[:10]}
    R, dof, dep = _fit_t_copula(z)
    w = np.array([wt for s, wt in weights if s in keep], dtype=float)
    w = w / w.sum()
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(R)
    k = len(keep)
    # t-copula 抽樣:多元常態 × sqrt(nu/chi2) → t 邊際分位 → 標準化殘差經驗分位
    g = rng.standard_normal((n_paths * h, k)) @ L.T
    chi = rng.chisquare(dof, size=(n_paths * h, 1))
    t_s = g / np.sqrt(chi / dof)
    u = stats.t.cdf(t_s, dof)
    zsim = np.column_stack([np.quantile(z[:, i], np.clip(u[:, i], 1e-6, 1 - 1e-6)) for i in range(k)])
    sig = np.array([params[s]["sigma_last"] for s in keep])          # 條件波動起點(不外推 GARCH 遞迴=保守)
    step = (zsim * sig) / 100.0                                      # 還原小數尺度
    port = (step @ w).reshape(n_paths, h)
    paths = np.exp(np.cumsum(np.log1p(np.clip(port, -0.99, None)), axis=1)) - 1.0
    mdd = _maxdd_per_path(paths)
    thr = float(policies.get("maxdd_threshold", -0.2)) if isinstance(policies, dict) else -0.2
    return {"kind": "copula_t_garch", "disclaimer": DISCLAIMER, **meta,
            "maxdd": {q: round(float(np.percentile(mdd, p)), 5)
                      for q, p in (("p5", 5), ("p25", 25), ("p50", 50), ("p95", 95))},
            "p_maxdd_lt_policy": round(float((mdd < thr).mean()), 4), "policy_threshold": thr,
            "n_survived": len(keep), "n_members": len(sids), "failed_marginals": failed,
            "copula_dof": dof, **dep, "window_maxdd": round(window_maxdd, 5),
            "n_paths": n_paths, "horizon_td": h, "seed": seed,
            "nu_median": round(float(np.median([params[s]["nu"] for s in keep])), 3),
            "note_structure": "邊際 GARCH(1,1)-t 之條件波動固定於期末值(不遞迴外推=保守);"
                              "相依結構由 t-copula 承載——**本法唯一補的洞=相關性趨一**",
            "note_scope": "未覆蓋成分已剔除並重正規化權重;dof 小=尾部同步更強"}


# ── M1 跨市場類比(進階三法計畫 20260727 凍結窗;analog=非台股歷史、等權市場路徑、β=1 承受) ──
ANALOG_EPISODES = {
    "us1929": ("USStockPrice", "1929-09-01", "1932-07-31"),
    "us1973": ("USStockPrice", "1973-01-01", "1974-12-31"),
    "us1987": ("USStockPrice", "1987-08-01", "1987-12-31"),
    "us2000": ("USStockPrice", "2000-03-01", "2002-10-31"),
    "us2008": ("USStockPrice", "2008-09-01", "2009-03-31"),   # 校準錨:對照台股 2008 重放
    "uk1973": ("UKStockPrice", "1973-01-01", "1975-01-31"),
}
MIN_ANALOG_STOCKS = 100      # 日覆蓋誠實下限(計畫凍結;1929 年代可能觸發=合法拒答)
ANALOG_NOTES = ("analog:非台股歷史——類比市場之等權分散組合實際路徑",
                "組合視同 β=1 承受該市場路徑;不做個股映射(映射任意性=自我欺騙)",
                "來源是否含已下市股未證實:倖存者偏誤方向未知,數字僅類比參考")


def _analog_market_path(cur, table, start, end):
    """類比市場等權日報酬(單一 SQL 窗函數;逐日橫斷面 winsorize 1%/99%;RAM 零壓)。
    回 (dates, rets, n_min, n_med);首日因無前收自然剔除。"""
    # 海外表收盤欄=大寫 "Close"(FinMind 慣例,與台股表小寫 close 不同;2026-07-27 實撞)
    cur.execute(f"""
        WITH px AS (SELECT stock_id, date, "Close" AS close,
                lag("Close") OVER (PARTITION BY stock_id ORDER BY date) AS prev
            FROM "{table}" WHERE date BETWEEN %s AND %s AND "Close" > 0),
        r AS (SELECT date, close/prev - 1 AS ret FROM px WHERE prev > 0),
        q AS (SELECT date, percentile_cont(0.01) WITHIN GROUP (ORDER BY ret) AS lo,
                     percentile_cont(0.99) WITHIN GROUP (ORDER BY ret) AS hi,
                     count(*) AS n FROM r GROUP BY date)
        SELECT r.date, avg(GREATEST(q.lo, LEAST(q.hi, r.ret))), max(q.n)
        FROM r JOIN q USING (date) GROUP BY r.date ORDER BY r.date""", (start, end))
    rows = cur.fetchall()
    if not rows:
        return [], np.array([]), 0, 0
    dates = [r[0] for r in rows]
    rets = np.array([float(r[1]) for r in rows])
    ns = sorted(int(r[2]) for r in rows)
    return dates, rets, ns[0], ns[len(ns) // 2]


def _analog_summary(name, dates, rets, n_min, n_med, meta, tw2008_maxdd=None):
    """類比情境 summary(純函式;#15 拒答邏輯與揭露硬綁)。"""
    base = {"disclaimer": DISCLAIMER, "analog_notes": list(ANALOG_NOTES), **meta,
            "analog": name, "market_table": ANALOG_EPISODES[name][0]}
    if len(rets) < 20 or n_min < MIN_ANALOG_STOCKS:
        return {**base, "kind": "analog_refused",
                "note": f"日覆蓋 min={n_min} < {MIN_ANALOG_STOCKS} 或天數不足({len(rets)} td)→拒答(不硬出數字,#15)",
                "n_td": len(rets), "n_stocks_min": n_min}
    cum = float(np.prod(1.0 + rets) - 1.0)
    mdd = float(drawdown_series(list(rets))[1].min())
    out = {**base, "kind": "episode_analog", "span": [str(dates[0]), str(dates[-1])],
           "n_td": len(rets), "cum_return": round(cum, 5), "maxdd": round(mdd, 5),
           "n_stocks_min": n_min, "n_stocks_med": n_med, "winsorize": "cross-section 1%/99%"}
    if name == "us2008" and tw2008_maxdd is not None:
        out["calib_anchor"] = {"tw2008_replay_maxdd": tw2008_maxdd,
                               "delta": round(mdd - tw2008_maxdd, 5),
                               "note": "校準錨:同窗台股重放 vs 美股類比之差=類比法失真度量尺"}
    return out


def run_analogs(cell, names, seed):
    """M1 主流程:逐窗算類比路徑→summary→落 mc_simulation_run(method=episode_analog_*)。"""
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        panel, members = _load_cell_portfolio(cur, cell)
        target = f"PORT_{cell}_{panel}"
        meta = {"cell": cell, "panel_date": str(panel), "n_members": len(members)}
        tw2008 = None
        cur.execute("""SELECT (summary->>'maxdd')::float8 FROM mc_simulation_run
            WHERE target_id=%s AND method='episode_replay_2008' LIMIT 1""", (target,))
        r = cur.fetchone()
        tw2008 = float(r[0]) if r and r[0] is not None else None
        for name in names:
            table, s, e = ANALOG_EPISODES[name]
            dates, rets, n_min, n_med = _analog_market_path(cur, table, s, e)
            summ = _analog_summary(name, dates, rets, n_min, n_med, meta, tw2008)
            method = f"episode_analog_{name}"
            key = f"mc_{target}_{panel}_{summ.get('n_td', 0) or 1}_{method}_{seed}"
            run_id = "mc_" + hashlib.sha256(key.encode()).hexdigest()[:16]
            cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2b:upsert 衝突分支)
            cur.execute("""INSERT INTO mc_simulation_run
                (run_id, target_id, asof_date, horizon_td, method, block_len_td, n_paths, seed,
                 summary, is_simulation, git_sha) VALUES (%s,%s,%s,%s,%s,NULL,1,%s,%s,true,%s)
                ON CONFLICT (run_id) DO UPDATE SET summary=EXCLUDED.summary, created_at=now()""",
                (run_id, target, panel, summ.get("n_td", 0) or 1, method, seed,
                 json.dumps(summ, ensure_ascii=False, default=str), git7))
            if summ["kind"] == "episode_analog":
                extra = ""
                if "calib_anchor" in summ:
                    extra = f" | 校準錨Δ={summ['calib_anchor']['delta']:+.3f}(vs 台股2008)"
                print(f"  [類比層] {name}: cum={summ['cum_return']:+.1%} MaxDD={summ['maxdd']:+.1%} "
                      f"(日覆蓋 min={n_min}/med={n_med}){extra}")
            else:
                print(f"  [類比層] {name}: {summ['note']}")
        conn.commit()
    print(f"✓ 類比完成(analog 硬標示;is_simulation=true;台股 episode 主結論地位不動)")
    return 0


def run(cell, episodes, n_paths, seed, h):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        panel, members = _load_cell_portfolio(cur, cell)
        horizon = int(cell.rsplit("_H", 1)[-1]) if "_H" in cell else h
        policies = load_policies(conn, horizon)
        target = f"PORT_{cell}_{panel}"
        meta = {"cell": cell, "panel_date": str(panel), "n_members": len(members),
                "note_candidate": "in_portfolio=候選組合成員(非部署事實;predict_asof D4 語意)"}
        # 聚合(≤panel、共同覆蓋、零補值)
        adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
        cur.execute(f"""SELECT DISTINCT date FROM {adj_sql}
            WHERE stock_id=%s AND date<=%s AND close>0 ORDER BY date DESC LIMIT %s""",
            (members[0][0], panel, WINDOW_TD + 1))
        dates_win = [r[0] for r in cur.fetchall()][::-1]
        by_stock = _member_closes(cur, [s for s, _ in members], dates_win[0], panel)
        rets, common, dropped = _portfolio_returns(members, by_stock, dates_win)
        if len(rets) < MIN_COMMON_TD:
            print(f"✗ 共同覆蓋 {len(rets)} td < {MIN_COMMON_TD} 誠實下限→拒跑(fail-closed)"); return 1
        logr = np.log1p(rets)
        window_maxdd = float(drawdown_series(list(rets))[1].min())
        print(f"候選組合 {cell}@{panel}:{len(members)} 檔|共同覆蓋 {len(rets)} td(剔除 {dropped} 日)|"
              f"窗內實際 MaxDD={window_maxdd:+.1%}")
        rows = []
        for method in BOOT_METHODS:
            summ = _bootstrap_summary(logr, horizon, n_paths, method, seed, policies, window_maxdd,
                                      {**meta, "effective_window_td": len(rets), "dropped_dates": dropped})
            if summ is None:
                print(f"  [參考] {method:<19} SKIP(arch 未安裝——graceful、非失敗)"); continue
            rows.append((method, BLOCK_LEN if method in ("block_bootstrap", "stationary_bootstrap") else None,
                         horizon, summ))
            fd = summ.get("fit_diag")
            print(f"  [參考] {method:<19} h={horizon} | MaxDD p50={summ['maxdd']['p50']:+.1%} "
                  f"p95={summ['maxdd']['p95']:+.1%} | P(MaxDD<{summ['policy_threshold']})={summ['p_maxdd_lt_policy']}"
                  + (f" | persistence={fd['persistence']}" if fd else ""))
        # M2 EVT(參考層;凍結參數 u=5%/refit=200)
        evt = _evt_summary(logr, horizon, n_paths, seed, policies, window_maxdd,
                           {**meta, "effective_window_td": len(rets)})
        rows.append(("evt_pot_hybrid", None, horizon, evt))
        # M3 copula-t + GARCH 邊際(參考層;逐股日報酬序列)
        # 逐股序列須**等長對齊**才能疊成殘差矩陣:取共同覆蓋日交集(零補值 #1;
        # 真實成因=上市晚/停牌,2026-07-27 實撞 756 vs 749)。
        cop_dates = [d for d in dates_win if all(d in by_stock.get(s, {}) for s, _ in members)]
        rets_by_stock = {}
        if len(cop_dates) > 60:
            for s, _w in members:
                cl = by_stock[s]
                a = np.asarray([cl[d] for d in cop_dates], dtype=float)
                rets_by_stock[s] = a[1:] / a[:-1] - 1.0
        cop = _copula_summary(rets_by_stock, [(s, w) for s, w in members if s in rets_by_stock],
                              horizon, n_paths, seed, policies, window_maxdd,
                              {**meta, "effective_window_td": len(rets)})
        rows.append(("copula_t_garch", None, horizon, cop))
        if cop["kind"] == "copula_t_garch":
            print(f"  [參考] {'copula_t_garch':<19} h={horizon} | MaxDD p50={cop['maxdd']['p50']:+.1%} "
                  f"p95={cop['maxdd']['p95']:+.1%} | P(MaxDD<{cop['policy_threshold']})={cop['p_maxdd_lt_policy']}"
                  f" | dof={cop['copula_dof']} 平均相關={cop['avg_corr']} 尾部相依λ={cop['tail_dep_lambda']}"
                  f" 存活={cop['n_survived']}/{cop['n_members']}")
        else:
            print(f"  [參考] copula_t_garch     {cop['note']}")
        if evt["kind"] == "evt_pot_hybrid":
            print(f"  [參考] {'evt_pot_hybrid':<19} h={horizon} | MaxDD p50={evt['maxdd']['p50']:+.1%} "
                  f"p95={evt['maxdd']['p95']:+.1%} | P(MaxDD<{evt['policy_threshold']})={evt['p_maxdd_lt_policy']}"
                  f" | ξ={evt['gpd_xi']} CI95={evt['gpd_xi_ci95']} n_tail={evt['n_tail']}")
        else:
            print(f"  [參考] evt_pot_hybrid     {evt['note']}")
        for ep in episodes:
            s, e = EPISODES[ep]
            cur.execute(f"""SELECT DISTINCT date FROM {adj_sql}
                WHERE date BETWEEN %s AND %s ORDER BY date""", (s, e))
            ep_dates = [r[0] for r in cur.fetchall()]
            ep_closes = _member_closes(cur, [x for x, _ in members], s, e)
            summ = _episode_summary(members, ep_closes, ep_dates, ep, policies, meta)
            rows.append((f"episode_replay_{ep}", None, summ.get("n_td", 0) or 1, summ))
            tag = (f"cum={summ['cum_return']:+.1%} MaxDD={summ['maxdd']:+.1%} 權重覆蓋={summ['weight_coverage']:.0%}"
                   if summ["kind"] == "episode_replay" else summ["note"])
            print(f"  [主結論] episode {ep}: {tag}")
        for method, blk, hh, summ in rows:
            key = f"mc_{target}_{panel}_{hh}_{method}_{seed}"
            run_id = "mc_" + hashlib.sha256(key.encode()).hexdigest()[:16]
            cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2b:upsert 衝突分支)
            cur.execute("""INSERT INTO mc_simulation_run
                (run_id, target_id, asof_date, horizon_td, method, block_len_td, n_paths, seed,
                 summary, is_simulation, git_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s)
                ON CONFLICT (run_id) DO UPDATE SET summary=EXCLUDED.summary, created_at=now()""",
                (run_id, target, panel, hh, method, blk,
                 n_paths if method.endswith("bootstrap") else 1, seed,
                 json.dumps(summ, ensure_ascii=False, default=str), git7))
        conn.commit()
    print(f"✓ 完成(is_simulation=true;只存摘要;seed={seed} 可重現)\n  ⚠ {DISCLAIMER}")
    return 0


def compare(cell):
    """四法對照(唯讀帳本、零重算;方法擴充計畫 P3):MaxDD 分位並排+P(MaxDD<閾)。判讀按計畫 §一預註冊規則。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT method, summary FROM mc_simulation_run
            WHERE target_id LIKE %s AND method = ANY(%s) ORDER BY array_position(%s::text[], method)""",
            (f"PORT_{cell}_%", list(BOOT_METHODS), list(BOOT_METHODS)))
        rows = cur.fetchall()
    if not rows:
        print(f"(cell {cell} 無 bootstrap 族 run;先 --run)"); return 1
    print(f"{cell} 四法對照(參考層;主結論=episode_replay、不在此表):")
    print(f"  {'method':<20}{'MaxDD p5':>10}{'p25':>8}{'p50':>8}{'p95':>8}{'P(<閾)':>9}")
    for m, s in rows:
        md, p = s["maxdd"], s.get("p_maxdd_lt_policy")
        print(f"  {m:<20}{md['p5']:>10.1%}{md['p25']:>8.1%}{md['p50']:>8.1%}{md['p95']:>8.1%}"
              f"{('n/a' if p is None else format(p, '.4f')):>9}")
        fd = s.get("fit_diag")
        if fd:
            print(f"      fit: ω={fd['omega']} α={fd['alpha']} β={fd['beta']} "
                  f"persistence={fd['persistence']} converged={fd['converged']}")
    print("  ⚠ 窗偏差不變:四法皆重抽同一窗、變不出窗外事件;episode 重放主結論地位不變")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT target_id, method, horizon_td,
                       coalesce(summary->'maxdd'->>'p95', summary->>'maxdd') AS mdd
                       FROM mc_simulation_run WHERE target_id LIKE 'PORT_%' ORDER BY created_at DESC LIMIT 12""")
        rows = cur.fetchall()
    if not rows:
        print("(尚無 PORT_ 組合層模擬 run;--run 產生)")
    for t, m, h, mdd in rows:
        print(f"  {t} {m:<22} h={h:<4} maxdd(p95或情境)={mdd}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import datetime as dt
    d = [dt.date(2026, 1, i) for i in range(1, 6)]
    by = {"A": {d[0]: 100, d[1]: 110, d[2]: 99, d[3]: 99, d[4]: 120},
          "B": {d[0]: 50, d[1]: 55, d[2]: 45, d[4]: 60}}          # B 缺 d[3]
    rets, common, dropped = _portfolio_returns([("A", .5), ("B", .5)], by, d)
    chk("共同覆蓋剔缺值日(#1 零補值)", dropped == 1 and len(common) == 4)
    chk("聚合數學:等權兩股首日報酬=(10%+10%)/2", abs(rets[0] - 0.10) < 1e-12)
    paths = np.array([[0.10, -0.10, 0.20]])
    chk("MaxDD 向量化=drawdown_series 同義",
        abs(_maxdd_per_path(paths)[0] - drawdown_series([0.10, (0.9 / 1.1) - 1, (1.2 / 0.9) - 1])[1].min()) < 1e-12)
    ep = _episode_summary([("A", .5), ("B", .5)], {"A": by["A"]}, d, "2008", {}, {})
    chk("episode 權重覆蓋<70%→誠實拒答", ep["kind"] == "episode_refused")
    bs = _bootstrap_summary(np.log1p(np.array([0.01, -0.02] * 130)), 5, 50, "iid_bootstrap", 42,
                            {"dd_circuit": {"threshold": -0.2}}, -0.05, {})
    for note in ("note_policy", "note_window_bias", "disclaimer"):
        chk(f"揭露欄硬綁:{note}", note in bs and bool(bs[note]))
    d30 = [dt.date(2026, 2, 1) + dt.timedelta(days=i) for i in range(30)]
    by30 = {"A": {dd: 100 + i for i, dd in enumerate(d30)}}
    ep_ok = _episode_summary([("A", 1.0)], by30, d30, "x", {}, {})
    chk("情境揭露欄硬綁三件", ep_ok["kind"] == "episode_replay" and all(
        k in ep_ok for k in ("note_single_scenario", "note_survivor", "note_renorm")))
    # 方法擴充增項(2026-07-26 計畫 P1)
    lr = np.tile(np.array([0.01, -0.02, 0.005, 0.003]), 75)
    p_a = _stationary_paths(lr, 8, 5, BLOCK_LEN, np.random.default_rng(7))
    chk("stationary:同 seed 逐位重現", np.array_equal(
        p_a, _stationary_paths(lr, 8, 5, BLOCK_LEN, np.random.default_rng(7))))
    chk("stationary:形狀/有限", p_a.shape == (5, 8) and np.isfinite(p_a).all())
    big = _stationary_paths(lr, 6, 3, 10 ** 9, np.random.default_rng(3))
    stp = np.diff(np.concatenate([np.zeros((3, 1)), np.log1p(big)], axis=1), axis=1)
    m = len(lr)
    chk("stationary:mean_block→∞ 退化為環繞連續片段", all(
        any(np.allclose(stp[i], np.take(lr, (np.arange(6) + st) % m)) for st in range(m)) for i in range(3)))
    try:
        import arch  # noqa: F401
        rng = np.random.default_rng(11)
        syn = np.concatenate([rng.normal(0, .005, 200), rng.normal(0, .03, 100), rng.normal(0, .005, 200)])
        gp, fd = _garch_fhs_paths(syn, 10, 50, np.random.default_rng(5))
        chk("garch_fhs:persistence∈(0,1) 且收斂", 0 < fd["persistence"] < 1 and fd["converged"])
        chk("garch_fhs:形狀/有限/fit_diag 齊", gp.shape == (50, 10) and np.isfinite(gp).all()
            and all(k in fd for k in ("omega", "alpha", "beta", "n_obs", "note_fit")))
    except ImportError:
        print("  ⊘ garch_fhs 兩項 SKIP(arch 未安裝——graceful 非 FAIL)")
    # ── M2 EVT(2026-07-27;判準=CI 覆蓋而非點估誤差) ──
    from scipy import stats as _st
    _TRUE_XI = 0.25
    _r = -_st.genpareto.rvs(_TRUE_XI, loc=0, scale=0.01, size=30000,
                            random_state=np.random.default_rng(7))
    _s = _evt_summary(_r, 20, 300, 42, {}, -0.2, {"cell": "T"})
    chk("EVT:GPD 門檻穩定性——ξ 之 95% CI 覆蓋真值(統計正確判準;點估誤差隨 n 變、非判準)",
        _s["kind"] == "evt_pot_hybrid" and _s["gpd_xi_ci95"][0] < _TRUE_XI < _s["gpd_xi_ci95"][1])
    chk("EVT:ξ 點估收斂(n_tail=1500 時誤差 <20%;實證 24.8%→11.6%→6.8% @300/1500/6000)",
        abs(_s["gpd_xi"] - _TRUE_XI) / _TRUE_XI < 0.20)
    chk("EVT:尾部樣本不足→拒答(不硬出數字)",
        _evt_summary(np.random.default_rng(1).normal(0, 0.01, 50), 20, 100, 42, {}, -0.1,
                     {"cell": "T"})["kind"] == "evt_refused")
    chk("EVT:路徑口徑=累積簡單報酬(與 _simulate 同約定;少減 1 會系統性低估 MaxDD)",
        "np.exp(np.cumsum(draws, axis=1)) - 1.0" in open(__file__, encoding="utf-8").read())
    chk("EVT:不確定性揭露欄齊(ξ CI/n_tail/結構假設)",
        all(k in _s for k in ("gpd_xi_ci95", "n_tail", "note_structure", "note_uncertainty")))
    # ── M3 copula(2026-07-27;合成資料還原已知相關) ──
    _k, _T, _TRUE = 6, 3000, 0.4
    _R = np.full((_k, _k), _TRUE); np.fill_diagonal(_R, 1.0)
    _z = np.random.default_rng(11).multivariate_normal(np.zeros(_k), _R, size=_T)
    _Rh, _dof, _dep = _fit_t_copula(_z)
    _off = (_Rh.sum() - _k) / (_k * (_k - 1))
    chk(f"copula:相關還原誤差<0.05(真值 {_TRUE} → {_off:.4f})", abs(_off - _TRUE) < 0.05)
    chk("copula:R 正定(必要條件;非正定即 Cholesky 失敗)", bool(np.all(np.linalg.eigvalsh(_Rh) > 0)))
    chk("copula:dof 落格點內", _dof in COP_DOF_GRID)
    chk("copula:尾部相依 λ∈[0,1]", 0.0 <= _dep["tail_dep_lambda"] <= 1.0)
    chk("copula:存活不足→整法拒答(不硬出數字)",
        _copula_summary({f"s{i}": np.random.default_rng(i).normal(0, .01, 400) for i in range(3)},
                        [(f"s{i}", 1/3) for i in range(3)], 20, 50, 42, {}, -0.1,
                        {"cell": "T"})["kind"] == "copula_refused")
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="組合層前瞻風險模擬(模擬非預測)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cell", default="RankRidge_H60")
    ap.add_argument("--episode", choices=[*EPISODES, "all"], default="all")
    ap.add_argument("--analog", choices=[*ANALOG_EPISODES, "all"],
                    help="M1 跨市場類比(六窗凍結;analog 硬標示、β=1 市場路徑)")
    ap.add_argument("--n-paths", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.compare:
        return compare(a.cell)
    if not a.run:
        print(__doc__)
        return status()
    if a.analog:
        names = list(ANALOG_EPISODES) if a.analog == "all" else [a.analog]
        return run_analogs(a.cell, names, a.seed)
    eps = list(EPISODES) if a.episode == "all" else [a.episode]
    return run(a.cell, eps, a.n_paths, a.seed, 60)


if __name__ == "__main__":
    sys.exit(main())
