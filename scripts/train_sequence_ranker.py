#!/usr/bin/env python
"""序列 DL 排序模型評測 CLI — SeqLSTM walk-forward OOS 對照冠軍(S4-Wave-C Phase 0，評測用、不寫庫)。

🎯 這支在做什麼(白話):S4-Wave-C 首個真 adapter 之評測編排——把既有序列窗張量(`features.sequence`)
   接上新模型(`models.sequence_ranker.SeqLSTM`)，走與 RankRidge/RankGBDT/ENS_ridge_gbdt **同一份**
   H60 非重疊 panel 集(#12，同 panel hash 可比)的 purged walk-forward 折(`walkforward.splits`)，
   對每折逐 as-of 疊訓練張量→fit SeqLSTM→predict test 折→**複用共用選股函式**
   (`portfolio.build_long_portfolio`)建投組→算單折報酬，彙總同 `run_backtest` 形狀之指標。
   **效能命門**:每股歷史面板(`build_stock_panel`)只抓一次、快取於記憶體，之後任意多個 as-of／折
   皆為零 DB 之純張量 reshape(`stack_windows`)——見計畫書
   `reports/augur_s4_wave_c_lstm_adapter_plan_20260804.md` §3.1。
   `--smoke`:只跑訓練樣本最多之最後一折、單一 seed，量實測耗時，供 Phase 0a 可行性判斷
   (CPU-only、本機無 GPU)——**不**代表完整 OOS 分數，僅耗時煙測。

守 #8(train 統計/折切分不看未來)· #12(折/選股/指標複用既有函式，非另造)· #15(seed 可重現)·
   #28(本地零 usage)· FZ/GATE-keep(本檔全程唯讀，零寫庫、零 registry)。
   ≠可交易/確立級；零 FinMind/FRED。

執行指令矩陣:
  python scripts/train_sequence_ranker.py                                # 無參數=印本矩陣+操作值(不執行)
  python scripts/train_sequence_ranker.py --smoke                       # Phase 0a:最後一折、單一 seed、耗時煙測
  python scripts/train_sequence_ranker.py --smoke --seed 1               # 指定 seed 之煙測
  python scripts/train_sequence_ranker.py --run --seeds 1,2,42           # Phase 0b:全量折×3 seed 評測(建議 Phase 0a 過門後才跑,CPU 可能耗時)
  python scripts/train_sequence_ranker.py --run --horizon 60 --window 60 --nan-threshold 0.3
"""
import argparse
import sys
import time

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
import numpy as np

from augur.core import db
from augur.evaluation import baseline, label as label_mod, portfolio, walkforward
from augur.features.sequence import stack_windows
from augur.models.sequence_patchtst import SeqPatchTSTSmall
from augur.models.sequence_ranker import SeqLSTM
from augur.models.sequence_transformer import SeqTransformerSmall

COST_TW = 0.00585
FAMILIES = {
    "SeqLSTM": SeqLSTM,
    "SeqTransformerSmall": SeqTransformerSmall,
    "SeqPatchTSTSmall": SeqPatchTSTSmall,
}


def _make_model(family, seed):
    cls = FAMILIES[family]
    # 0b 預設＝0a 薄殼；CPU-only 友善
    return cls(seed=seed)


def _nonoverlap(panels, h):
    """貪婪挑非重疊再平衡 panel(與 run_economic_eval.py 同口徑，#12——同 SINCE/UNTIL/h 產出同 panel hash)。"""
    need = h * 1.45 * 0.9
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def _h_panels(conn, since, until, h):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s AND panel_date<=%s "
            "ORDER BY panel_date", (since, until))
        panels = [r[0] for r in cur.fetchall()]
    return _nonoverlap(panels, h) if panels else []


def _stock_universe(conn, asof_dates):
    """歷史 as-of 宇宙聯集(複用 baseline._asof_stocks，#12；跨日期聯集供一次性面板快取涵蓋所需股票)。"""
    uni = set()
    for d in asof_dates:
        uni |= set(baseline._asof_stocks(conn, d))
    return sorted(uni)


def _fetch_panels(conn, stock_ids):
    """一次性抓每股日頻面板(#12 複用 field_correlation.build_stock_panel)。回 (dict, 耗時秒)。"""
    from augur.audit.field_correlation import build_stock_panel
    t0 = time.time()
    panels = {sid: build_stock_panel(conn, sid) for sid in stock_ids}
    return panels, time.time() - t0


def _select_channels(panels, as_of, window_len, nan_threshold):
    """資料驅動通道篩選(非硬編)：以給定 as_of 算全通道 NaN 率，回 (kept, dropped, nan_rate_dict)。"""
    tensor, ok_ids, excluded, chans = stack_windows(panels, as_of, window_len)
    if tensor.size == 0 or not chans:
        return [], list(chans), {}
    nan_rate = {c: float(np.isnan(tensor[:, :, i]).mean()) for i, c in enumerate(chans)}
    kept = [c for c in chans if nan_rate[c] < nan_threshold]
    dropped = [c for c in chans if nan_rate[c] >= nan_threshold]
    return kept, dropped, nan_rate


def _build_xy(conn, panels, asof_dates, window_len, channels, h, calendar):
    """對多個歷史 as-of 疊訓練樣本(stack_windows 零 DB + label_mod.labels 取 0-1 rank，#12 同 RankRidge 目標)。"""
    Xs, ys = [], []
    for d in asof_dates:
        tensor, ok_ids, excluded, chans = stack_windows(panels, d, window_len, channels)
        if not ok_ids:
            continue
        lab = label_mod.labels(conn, d, ok_ids, h, calendar=calendar)
        keep_idx = [i for i, sid in enumerate(ok_ids) if sid in lab]
        if not keep_idx:
            continue
        Xs.append(tensor[keep_idx])
        ys.append(np.array([lab[ok_ids[i]] for i in keep_idx]))
    if not Xs:
        return np.empty((0, window_len, len(channels or []))), np.empty(0)
    return np.concatenate(Xs, axis=0), np.concatenate(ys)


def _one_fold(conn, panels, fold, window_len, channels, h, calendar, seed,
              prev_w=None, prev_ret=None, family="SeqLSTM"):
    """單折:build train xy→fit family→predict test→共用選股/報酬(#12)。

    `prev_w`/`prev_ret`：上一折投組權重 dict／報酬 dict，給了才算真實漂移換手
    (鏈式,同 `portfolio.run_backtest` 口徑,含 prev_ret 加權漂移);皆 None＝初次建倉(turnover=1.0，
    僅 --smoke 單折煙測使用此路)。回 (gross_ret, turnover, cur_w, ret_by_id, timings dict)
    ——cur_w/ret_by_id 供下一折鏈式傳入。
    """
    t0 = time.time()
    Xtr, ytr = _build_xy(conn, panels, fold["train"], window_len, channels, h, calendar)
    t_build = time.time() - t0
    if len(ytr) < 30:
        return None, None, prev_w, prev_ret, {"build_xy": t_build, "n_train": len(ytr)}

    t0 = time.time()
    model = _make_model(family, seed).fit(Xtr, ytr)
    t_fit = time.time() - t0

    Xte, ok_ids, excluded, _ = stack_windows(panels, fold["test"], window_len, channels)
    if not ok_ids:
        return None, None, prev_w, prev_ret, {"build_xy": t_build, "fit": t_fit, "n_train": len(ytr), "n_test": 0}

    t0 = time.time()
    scores = model.predict(Xte)
    t_pred = time.time() - t0

    fwd = label_mod.forward_returns(conn, fold["test"], ok_ids, h, calendar=calendar)
    common = [s for s in ok_ids if s in fwd]
    if len(common) < 10:
        return None, None, prev_w, prev_ret, {"build_xy": t_build, "fit": t_fit, "predict": t_pred,
                                               "n_train": len(ytr), "n_test": len(common)}
    idx = [ok_ids.index(s) for s in common]
    common_scores = scores[idx]
    ret_by_id = {s: float(np.expm1(fwd[s])) for s in common}
    port = portfolio.build_long_portfolio(common, common_scores, top_frac=0.2, weight="equal")
    gross = float(sum(w * ret_by_id[sid] for sid, w, _ in port))
    cur_w = {sid: w for sid, w, _ in port}
    turn = portfolio._turnover(cur_w, prev_w, prev_ret)   # 鏈式漂移換手;煙測 prev_w=None=初次建倉
    timings = {"build_xy": t_build, "fit": t_fit, "predict": t_pred,
               "n_train": len(ytr), "n_test": len(common), "n_port": len(port)}
    return gross, turn, cur_w, ret_by_id, timings


def smoke(since, until, h, window_len, seed, nan_threshold, family="SeqLSTM"):
    """Phase 0a:只跑訓練樣本最多之最後一折、單一 seed，量實測耗時（可行性判斷，非完整 OOS）。"""
    with db.connect() as conn:
        cal = label_mod.full_calendar(conn)
        panel_dates = _h_panels(conn, since, until, h)
        if len(panel_dates) < 3:
            print(f"✗ {since}~{until} h={h} 非重疊 panel 僅 {len(panel_dates)}<3;中止。"); return 1
        folds = walkforward.splits(panel_dates, h, calendar=cal)
        if not folds:
            print("✗ 無可用折(min_train 未達);中止。"); return 1
        fold = folds[-1]   # 最後一折=train 樣本最多、CPU 耗時最壞情境(#15 保守估計方向)
        print(f"Phase 0a 煙測 | family={family} | 全量折數={len(folds)}(僅跑最後一折) | "
              f"fold train={len(fold['train'])} panels "
              f"test={fold['test']} | h={h} window={window_len} seed={seed}")

        all_dates = fold["train"] + [fold["test"]]
        t0 = time.time()
        uni = _stock_universe(conn, all_dates)
        t_uni = time.time() - t0
        print(f"  歷史 as-of 宇宙聯集：{len(uni)} 支股票（{t_uni:.1f}s）")

        panels, t_fetch = _fetch_panels(conn, uni)
        print(f"  一次性面板抓取（{len(uni)} 股 × ~31 SQL/股）：{t_fetch:.1f}s"
              "（此為一次性成本，之後任意折/seed 皆免重抓）")

        kept, dropped, nan_rate = _select_channels(panels, fold["test"], window_len, nan_threshold)
        print(f"  通道篩選（NaN 率 < {nan_threshold:.0%}）：保留 {len(kept)}／排除 {len(dropped)}")
        if dropped:
            print(f"    排除：{dropped}")
        if len(kept) < 3:
            print(f"✗ 保留通道數 {len(kept)}<3（過稀，不硬湊）；中止，誠實回報。"); return 1

        gross, turn, _cur_w, _prev_ret, timings = _one_fold(
            conn, panels, fold, window_len, kept, h, cal, seed, family=family)
        t_total = t_uni + t_fetch + timings.get("build_xy", 0) + timings.get("fit", 0) + timings.get("predict", 0)
        print(f"\n  n_train={timings.get('n_train', 0)} n_test={timings.get('n_test', 0)} "
              f"n_port={timings.get('n_port', 0)}")
        print(f"  耗時分解：宇宙聯集={t_uni:.1f}s 面板抓取={t_fetch:.1f}s "
              f"建訓練張量={timings.get('build_xy', 0):.1f}s fit={timings.get('fit', 0):.1f}s "
              f"predict={timings.get('predict', 0):.1f}s")
        print(f"  單折總耗時（含一次性面板抓取）={t_total:.1f}s")
        if gross is not None:
            print(f"  單折 gross return（未扣成本，僅 1 期、非 Sharpe——煙測不代表完整 OOS）={gross:+.4f}")

        # 可行性外推(#15,非保證、僅開發近似):一次性面板抓取不重複;全量估計=面板抓取(略大於本次,因需
        # 涵蓋全部折數之歷史宇宙聯集,非本折 2 個 as-of 之聯集)+folds×3 seed×(build_xy+fit+predict)
        per_fold_compute = timings.get("build_xy", 0) + timings.get("fit", 0) + timings.get("predict", 0)
        est_full = t_fetch * 1.3 + len(folds) * 3 * per_fold_compute   # 面板抓取估上調 30%(全量宇宙略大)
        print(f"\n  單折重覆成本(build_xy+fit+predict,不含一次性面板抓取,此值×folds×seed 才是全量主體)"
              f"={per_fold_compute:.1f}s")
        print(f"  可行性外推（非保證,僅開發近似）：全量 {len(folds)} 折×3 seed ≈ {est_full:.0f}s "
              f"（≈{est_full/60:.1f} 分鐘）")
        gate_a = per_fold_compute < 300      # 單折重覆成本<5分鐘(排除一次性面板抓取,因該項全量只付一次)
        gate_b = est_full < 7200             # 全量外推<2小時
        verdict = "可行" if (gate_a and gate_b) else "不可行(CPU 算力不足以支撐全量 walk-forward)"
        print(f"  Phase 0a 判定：{verdict}（門檻：單折重覆成本<5分鐘［{'過' if gate_a else '不過'}］"
              f"且全量外推<2小時［{'過' if gate_b else '不過'}］）")
    return 0


def run_full(since, until, h, window_len, seeds, nan_threshold, family="SeqLSTM"):
    """Phase 0b:全量折×seed walk-forward 評測(唯讀、不寫庫;面板僅全域抓取一次,折鏈同 run_backtest 換手口徑)。"""
    with db.connect() as conn:
        cal = label_mod.full_calendar(conn)
        panel_dates = _h_panels(conn, since, until, h)
        if len(panel_dates) < 3:
            print(f"✗ {since}~{until} h={h} 非重疊 panel 僅 {len(panel_dates)}<3;中止。"); return 1
        folds = walkforward.splits(panel_dates, h, calendar=cal)
        if not folds:
            print("✗ 無可用折(min_train 未達);中止。"); return 1
        seed_list = [int(s) for s in str(seeds).split(",") if s.strip()]
        print(f"Phase 0b 全量評測 | family={family} | 折數={len(folds)} | seeds={seed_list} | "
              f"h={h} window={window_len}")
        print("  預凍門：3-seed min net Sharpe > RankRidge_H60 1.3016 → else STOP promote")

        all_dates = sorted(set(d for f in folds for d in (f["train"] + [f["test"]])))
        t0 = time.time()
        uni = _stock_universe(conn, all_dates)
        t_uni = time.time() - t0
        panels, t_fetch = _fetch_panels(conn, uni)
        print(f"  一次性面板抓取（{len(uni)} 股）：宇宙聯集 {t_uni:.1f}s + 抓取 {t_fetch:.1f}s"
              f"（全程僅一次,供全部 {len(folds)} 折×{len(seed_list)} seed 共用）")

        kept, dropped, _ = _select_channels(panels, folds[-1]["test"], window_len, nan_threshold)
        print(f"  通道篩選：保留 {len(kept)}／排除 {len(dropped)}")
        if len(kept) < 3:
            print(f"✗ 保留通道數 {len(kept)}<3（過稀）；中止。"); return 1

        t_run0 = time.time()
        seed_net = []
        for seed in seed_list:
            gross_list, net_list, used_dates = [], [], []
            prev_w, prev_ret = None, None
            for fold in folds:
                gross, turn, prev_w, prev_ret, _t = _one_fold(
                    conn, panels, fold, window_len, kept, h, cal, seed, prev_w, prev_ret,
                    family=family)
                if gross is None:
                    continue
                gross_list.append(gross)
                net_list.append(gross - turn * COST_TW)
                used_dates.append(fold["test"])
            if len(gross_list) < 3:
                print(f"  seed={seed}: 可用折數 {len(gross_list)}<3,略過"); continue
            ppy = len(gross_list) / max((used_dates[-1] - used_dates[0]).days / 365.0, 1e-9)
            mg = portfolio._metrics(gross_list, ppy)
            mn = portfolio._metrics(net_list, ppy)
            print(f"  seed={seed} n_folds={len(gross_list)}｜gross_sharpe={mg.get('sharpe')}"
                  f" gross_hit={mg.get('hit_rate')}｜net_sharpe={mn.get('sharpe')} net_hit={mn.get('hit_rate')}"
                  f" net_cagr={mn.get('cagr')}")
            seed_net.append(float(mn.get("sharpe") or float("nan")))
        print(f"\n  全量評測總耗時={time.time() - t_run0:.1f}s（不含前置面板抓取）")
        valid = [x for x in seed_net if np.isfinite(x)]
        if len(valid) >= 3:
            mn_sh = min(valid)
            champ = 1.3016
            verdict = "PASS promote-gate" if mn_sh > champ else "STOP promote"
            print(f"  閘：min net Sharpe={mn_sh:.4f} vs RankRidge_H60 {champ} → {verdict}")
        else:
            print("  閘：可用 seed<3 → STOP promote（不足樣本）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="序列 DL walk-forward 評測(Phase 0;唯讀、不寫庫)")
    ap.add_argument("--run", action="store_true", help="Phase 0b:執行全量折×seed 評測(建議先--smoke過門)")
    ap.add_argument("--smoke", action="store_true", help="Phase 0a:僅跑最後一折、單一 seed,量耗時判可行性")
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--until", default="2026-06-30")
    ap.add_argument("--horizon", type=int, default=60, dest="h")
    ap.add_argument("--window", type=int, default=60, dest="window_len")
    ap.add_argument("--seed", type=int, default=42, help="--smoke 用單一 seed")
    ap.add_argument("--seeds", default="1,2,42", help="--run 用逗號分隔多 seed(#11)")
    ap.add_argument("--family", default="SeqLSTM", choices=sorted(FAMILIES.keys()),
                    help="模型族：SeqLSTM／SeqTransformerSmall（NF-C-TFM）／SeqPatchTSTSmall（NF-D-PATCH）")
    ap.add_argument("--nan-threshold", type=float, default=0.3, dest="nan_threshold",
                    help="通道篩選:NaN 率≥此值即排除(預設 0.3)")
    args = ap.parse_args(argv)

    if not args.smoke and not args.run:
        print(__doc__)
        print(f"目前操作值:since={args.since} until={args.until} horizon={args.h} window={args.window_len} "
              f"family={args.family} nan_threshold={args.nan_threshold} "
              f"smoke_seed={args.seed} run_seeds={args.seeds}")
        return 0
    if args.smoke:
        return smoke(args.since, args.until, args.h, args.window_len, args.seed,
                     args.nan_threshold, family=args.family)
    return run_full(args.since, args.until, args.h, args.window_len, args.seeds,
                    args.nan_threshold, family=args.family)


if __name__ == "__main__":
    sys.exit(main())
