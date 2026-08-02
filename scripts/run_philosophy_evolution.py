#!/usr/bin/env python
"""哲學↔市場進化編排 — PME S2：寫 evolution_run＋閘證據＋promotion_queue（零市場 API）。

🎯 這支在做什麼（白話）：一鍵建立可重現 run 帳本、覆蓋快照、逐 map 組 gate_json，並寫入
   晉升佇列。`--skeleton`：G-PROM／G-ECON 誠實 SKIP（≠ PASS）。`--local-gates`：對 mapped
   特徵用本地 DB `feature_values`／panel 重算 G-PROM 三關＋G-ECON #14，裁決 PASS／FAIL／SKIP
   （缺資料誠實 SKIP／FAIL，禁止為跑閘 sync／FinMind／FRED）。閘全綠才可能 pending_auto→S3 APPLY。

守 #1 #14 #15 #29；計畫 §4 S2／§4.1；PME-AUTO-B＋FZ-keep；PME-E123。

執行指令矩陣:
  python scripts/run_philosophy_evolution.py                 # 印用途（安全預設）
  python scripts/run_philosophy_evolution.py --skeleton      # S2 骨架：SKIP 重閘
  python scripts/run_philosophy_evolution.py --skeleton --with-local-evidence
  python scripts/run_philosophy_evolution.py --local-gates   # 本地重算 G-PROM／G-ECON（零 API）
  python scripts/run_philosophy_evolution.py --local-gates --dry-run
  python scripts/run_philosophy_evolution.py --local-gates --skip-multi-seed  # 三關(c) SKIP（勿假 PASS）
  python scripts/run_philosophy_evolution.py --control-arms  # M-1 對照臂:置換+錯配 null→evidence_run(V2-CTRL)
  python scripts/run_philosophy_evolution.py --control-arms --draws 20 --arm-seed 7  # 小樣本煙測
  python scripts/run_philosophy_evolution.py --selftest      # 免 DB
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    DEFAULT_GATE_CONFIG,
    KILL_CLEAR,
    KILL_HALT,
    SIGN_BOOT_SEEDS,
    SIGN_MIN_SERIES,
    SIGN_SEED0,
    attest_complete,
    build_gate_json,
    classify_coverage,
    decide_queue_status,
    effective_kill_state,
    evaluate_g_econ_from_evidence,
    evaluate_g_prom_from_evidence,
    evaluate_g_sign_from_evidence,
    map_action_from_evidence,
    normalize_kill_state,
    scan_noexec_text,
)


def _vss():
    """同目錄 script 互 import（先例＝run_meta_replay.py:96-98）；G-SIGN 方向正典與落帳複用 #12。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import verify_sign_consistency as vss
    return vss


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # ── B1 寫者自收尾（登錄冊 2026-08-01；行為驗證零 DB）──
    _st, _note = _abort_status(RuntimeError("boom"))
    chk("B1:_abort_status 餵真例外→failed+aborted note",
        _st == "failed" and _note.startswith("aborted: RuntimeError: boom"))
    chk("B1:note 截 200 字（超長例外不炸帳本欄）",
        len(_abort_status(RuntimeError("x" * 999))[1]) == 200)
    import signal as _sig
    _fired = {}
    try:
        _sigterm_to_exit(_sig.SIGTERM, None)
    except SystemExit as e:
        _fired["rc"] = e.code
    chk("B1:SIGTERM→SystemExit(143)（finally 得以跑）", _fired.get("rc") == 128 + _sig.SIGTERM)

    class _RecCur:
        def __init__(self):
            self.sql, self.params, self.rowcount = [], [], 1   # rowcount：誠實訊息讀它

        def execute(self, q, p=None):
            self.sql.append(q); self.params.append(p)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _RecConn:
        def __init__(self):
            self.cur, self.committed = _RecCur(), False

        def cursor(self):
            return self.cur

        def commit(self):
            self.committed = True

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    _rec = _RecConn()
    from augur.core import db as _dbmod    # patch 模組屬性（_abort_close 延遲 import 取同一模組物件）
    _orig_connect = _dbmod.connect
    _dbmod.connect = lambda: _rec
    try:
        _abort_close(77, RuntimeError("killed"))
    finally:
        _dbmod.connect = _orig_connect
    chk("B1:_abort_close 真送 UPDATE 且帶 status='running' 謂詞（不碰非殭屍列）",
        _rec.committed and any("AND status='running'" in q for q in _rec.cur.sql))
    chk("B1:run_id 以參數傳入（非字串拼接）",
        any(p and 77 in p for p in _rec.cur.params))

    # ── I5B-甲 世代 supersede(裁決 I5B-照建議;行為驗證零 DB;recording double 同 B1 先例)──
    _q = _RecConn()
    _q.cur.rowcount = 3
    _n_sup = _supersede_stale_pending(_q.cur, 22, "debt_ratio")
    _qsql = " ".join(_q.cur.sql)
    chk("I5B:回傳 rowcount 誠實計數(非常數)", _n_sup == 3)
    chk("I5B:最窄謂詞三件齊(pending_auto ∧ 同 feature ∧ run_id<本 run)——拔任一即紅",
        "queue_status='pending_auto'" in _qsql and "feature=%s" in _qsql
        and "run_id < %s" in _qsql)
    chk("I5B:標 superseded 終態且帶誠實閘 GUC 通行證(同交易)",
        "SET queue_status='superseded'" in _qsql
        and "SET LOCAL augur.honesty_write" in _qsql)
    chk("I5B:decided_by 自陳機器世代(非人簽)+參數化傳值",
        any(p and "superseded_by_run_22" in p and "debt_ratio" in p and 22 in p
            for p in _q.cur.params))

    text = Path(__file__).read_text(encoding="utf-8")
    chk("script G-NOEXEC clean", scan_noexec_text(text) == [])
    g = build_gate_json(
        g_iso={"verdict": "PASS"},
        g_map={"verdict": "PASS"},
        g_prom={"verdict": "SKIP", "reason": "skeleton"},
        g_econ={"verdict": "SKIP", "reason": "FZ-keep"},
        g_attest={"verdict": "PASS"},
        g_kill={"verdict": "PASS"},
        g_noexec={"verdict": "PASS"},
        g_sign={"verdict": "SKIP", "reason": "skeleton"},
    )
    chk("skeleton → rejected_gate", decide_queue_status(g, KILL_CLEAR) == "rejected_gate")
    prom = evaluate_g_prom_from_evidence(
        {"n_panels": 12, "mean_ic": 0.04, "hac_t": 2.1, "seed_deltas": [0.01, 0.01, 0.02]}
    )
    econ = evaluate_g_econ_from_evidence(
        {"port_sharpe": 1.0, "bench_sharpe": 0.8, "max_dd": -0.15, "n_periods": 8}
    )
    g2 = build_gate_json(
        g_iso={"verdict": "PASS"},
        g_map={"verdict": "PASS"},
        g_prom=prom,
        g_econ=econ,
        g_attest={"verdict": "PASS"},
        g_kill={"verdict": "PASS"},
        g_noexec={"verdict": "PASS"},
        g_sign={"verdict": "PASS"},
    )
    chk("local green → pending_auto", decide_queue_status(g2, KILL_CLEAR) == "pending_auto")
    # —— M-1 符號一致性(2026-07-27 拍板;實測值錨=volume_gini_60d 病灶形態) ——
    sign = evaluate_g_prom_from_evidence(
        {"n_panels": 32, "mean_ic": -0.0539, "hac_t": -3.966,
         "seed_deltas": [0.01, 0.01, 0.02], "expected_direction": 1}
    )
    chk("顯著反向 → FAIL_SIGN(非 SKIP、非 PASS)", sign["verdict"] == "FAIL_SIGN")
    chk("FAIL_SIGN 記 expected/observed(gate_json 驗收)",
        sign.get("expected_direction") == 1 and sign.get("observed_sign") == -1
        and sign.get("sign_significant") is True)
    g3 = build_gate_json(
        g_iso={"verdict": "PASS"}, g_map={"verdict": "PASS"}, g_prom=sign, g_econ=econ,
        g_attest={"verdict": "PASS"}, g_kill={"verdict": "PASS"}, g_noexec={"verdict": "PASS"},
        g_sign={"verdict": "PASS"},   # 驗 FAIL_SIGN 通道不被 G-SIGN 干擾
    )
    chk("FAIL_SIGN → rejected_gate(不入 pending_auto)",
        decide_queue_status(g3, KILL_CLEAR) == "rejected_gate")
    chk("樣本不足時不裁 FAIL_SIGN(insufficient 優先,3 panels 非證據)",
        evaluate_g_prom_from_evidence(
            {"n_panels": 3, "mean_ic": -0.9, "hac_t": -5.0, "seed_deltas": None,
             "expected_direction": 1})["verdict"] != "FAIL_SIGN")
    chk("正向不受影響(既有 PASS 路徑不變)",
        evaluate_g_prom_from_evidence(
            {"n_panels": 12, "mean_ic": 0.04, "hac_t": 2.1,
             "seed_deltas": [0.01, 0.01, 0.02], "expected_direction": 1})["verdict"] == "PASS")
    # —— M-1 對照臂純函式(_draw_abs_hac;免 DB 合成資料) ——
    import numpy as _np
    _r = _np.random.default_rng(7)
    strong = []
    for _i in range(30):  # 30 panel、preds==labels 完美訊號
        vals = {f"s{j}": float(_r.normal()) for j in range(40)}
        strong.append((vals, dict(vals)))
    live_t = _draw_abs_hac(strong, "shuffled", _np.random.default_rng(1))
    chk("置換臂:完美訊號被打亂後 |hac_t| 仍可算(null 有值)", live_t is not None)
    d1 = _draw_abs_hac(strong, "mismatched", _np.random.default_rng(3))
    d2 = _draw_abs_hac(strong, "mismatched", _np.random.default_rng(3))
    chk("決定性:同 seed 同 |hac_t|(common/pool 排序後才餵 rng)", d1 == d2)
    chk("panel<10 → None(不足額不出數)", _draw_abs_hac(strong[:5], "shuffled", _np.random.default_rng(1)) is None)
    chk("未知臂 fail-loud", (lambda: [_draw_abs_hac(strong, "lve", _np.random.default_rng(1))]
        ).__class__ is not None and _raises_ctrl(lambda: _draw_abs_hac(strong, "lve", _np.random.default_rng(1))))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _raises_ctrl(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def _code_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:64]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _env_halt() -> bool:
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == KILL_HALT


def _g_iso() -> dict:
    from augur.audit.import_isolation import check_isolation

    v = check_isolation()
    return {"verdict": "PASS" if not v else "FAIL", "n_violations": len(v)}


def _g_noexec() -> dict:
    """掃 APPLY／編排入口；evolution.py 為偵測器本體、不掃（對齊 import_isolation 自排除）。"""
    root = Path(__file__).resolve().parents[1]
    targets = [
        root / "scripts" / "apply_evolution_promotions.py",
        root / "scripts" / "run_philosophy_evolution.py",
        root / "scripts" / "set_evolution_kill_switch.py",
    ]
    hits = []
    for p in targets:
        if p.exists():
            hits.extend(scan_noexec_text(p.read_text(encoding="utf-8")))
    return {"verdict": "PASS" if not hits else "FAIL", "hits": hits}


def _load_maps(cur):
    cur.execute(
        """
        SELECT m.map_id, m.principle_id, m.feature, m.direction,
               m.validated_ic, m.validated_econ,
               EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature = m.feature) AS in_fv
        FROM principle_factor_map m
        ORDER BY m.feature, m.principle_id
        """
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _prom_econ_skeleton(row: dict, *, with_local: bool) -> tuple[dict, dict, dict]:
    """G-PROM／G-ECON／G-SIGN：skeleton 預設 SKIP；--with-local-evidence 僅附 validated_* 仍 SKIP。"""
    sign = {"verdict": "SKIP", "reason": "skeleton; sign not evaluated"}
    if not with_local:
        return (
            {"verdict": "SKIP", "reason": "skeleton; use --local-gates for PASS/FAIL"},
            {"verdict": "SKIP", "reason": "skeleton; use --local-gates for PASS/FAIL"},
            sign,
        )
    prom = {
        "verdict": "SKIP",
        "reason": "local validated_ic present but promotion triad not re-run (--local-gates)",
        "validated_ic": row.get("validated_ic"),
    }
    econ = {
        "verdict": "SKIP",
        "reason": "local validated_econ present but #14 not re-eval (--local-gates)",
        "validated_econ": row.get("validated_econ"),
    }
    if row.get("validated_ic") is None:
        prom = {"verdict": "SKIP", "reason": "no validated_ic; blocked or never verified"}
    if row.get("validated_econ") is None:
        econ = {"verdict": "SKIP", "reason": "no validated_econ; never verified"}
    return prom, econ, sign


def _ridge_mean_ic(conn, panels: list, h: int, feats: list[str]) -> float | None:
    """as-of purged walk-forward Ridge mean IC（G-PROM 多 seed 增量專用；零 GBDT）。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    from augur.evaluation import baseline, metrics, walkforward
    from augur.evaluation import label as label_mod

    if not feats or len(panels) < 3:
        return None
    cal = label_mod.full_calendar(conn)
    folds = walkforward.splits(panels, h, calendar=cal)
    ic_by: dict = {}
    for fold in folds:
        test_pd = fold["test"]
        ts_sids, Xte = baseline._panel_matrix(
            conn, test_pd, baseline._asof_stocks(conn, test_pd), feats
        )
        if len(ts_sids) < 5:
            continue
        lab = label_mod.labels(conn, test_pd, ts_sids, h, calendar=cal)
        keep = [i for i, s in enumerate(ts_sids) if s in lab]
        if len(keep) < 5:
            continue
        Xte = Xte[keep]
        ts_sids = [ts_sids[i] for i in keep]
        ylab = {s: lab[s] for s in ts_sids}
        Xtr, ytr = baseline._fold_xy(
            conn, fold["train"], None, feats, h, calendar=cal, asof=True
        )
        if len(ytr) < 50:
            continue
        sc = StandardScaler().fit(Xtr)
        pred = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xte))
        ic = metrics.rank_ic(dict(zip(ts_sids, pred)), ylab)
        if ic is not None:
            ic_by[test_pd] = ic
    return metrics.summarize(ic_by).get("mean_ic")


def _compute_feature_gates(
    conn,
    *,
    feature: str,
    direction: int,
    panels: list,
    h: int,
    cfg: dict,
    skip_multi_seed: bool,
    prod_feats: list[str] | None,
) -> tuple[dict, dict, dict]:
    """本地 DB 重算單一 feature 之 G-PROM／G-ECON／G-SIGN（零外部 API）。"""
    import numpy as np

    from augur.core import db
    from augur.evaluation import baseline, metrics, portfolio
    from augur.evaluation import label as label_mod

    g_prom_cfg = cfg.get("gates", {}).get("G-PROM", {})
    g_econ_cfg = cfg.get("gates", {}).get("G-ECON", {})
    cost = float(g_econ_cfg.get("cost", 0.00585))
    top_frac = float(g_econ_cfg.get("top_frac", 0.1))
    min_seeds = int(g_prom_cfg.get("min_seeds", 3))

    # —— as-of IC + HAC ——
    cal = label_mod.full_calendar(conn)
    ic_by_panel: dict = {}
    for pd_ in panels:
        stk = baseline._asof_stocks(conn, pd_)
        if not stk:
            with db.transaction(conn) as cur:
                cur.execute("SELECT stock_id FROM core_universe")
                stk = [str(r[0]) for r in cur.fetchall()]
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT stock_id, value FROM feature_values "
                "WHERE panel_date=%s AND feature=%s AND stock_id = ANY(%s)",
                (pd_, feature, stk),
            )
            preds = {str(s): float(v) * int(direction) for s, v in cur.fetchall() if v is not None}
        if len(preds) < 5:
            continue
        labs = label_mod.labels(conn, pd_, list(preds), h, calendar=cal)
        ic = metrics.rank_ic(preds, labs)
        if ic is not None:
            ic_by_panel[pd_] = ic

    summ = metrics.summarize(ic_by_panel)
    hac_t = metrics.effective_t_hac(ic_by_panel) if ic_by_panel else None

    # —— G-SIGN 證據（A3；判式=SIGN-B-go）——正典方向另取（裁決表優先、conflict 偵測；
    # 不沿用呼叫端 None→1 硬默認，那會偽造方向）。ic_by_panel 為「已乘 engine 方向」口徑，
    # 落證據前還原 raw（dir∈±1 故乘回即 raw），與 feature_sign_check／verify_sign_consistency 同口徑。
    vss = _vss()
    with db.transaction(conn) as cur:
        d_canon, d_src = vss.map_direction(cur, feature, with_source=True)
    ics = [float(v) for v in ic_by_panel.values()]
    sign_ev: dict = {
        "direction": d_canon,
        "direction_source": d_src,
        "engine_direction": int(direction),   # IC 乘用值；與正典不一致時如實入帳供稽核
        "n_series": len(ics),
        "point_ic": None,
        "boot_ics": None,
    }
    if len(ics) >= SIGN_MIN_SERIES:
        arr = np.array(ics, dtype=float)
        boots_adj = []
        for k in range(SIGN_BOOT_SEEDS):
            rng_s = np.random.default_rng(SIGN_SEED0 + k)
            boots_adj.append(float(arr[rng_s.integers(0, len(arr), len(arr))].mean()))
        sign_ev["point_ic"] = float(arr.mean()) * int(direction)
        sign_ev["boot_ics"] = [b * int(direction) for b in boots_adj]
    g_sign = evaluate_g_sign_from_evidence(sign_ev, cfg)

    prom_ev: dict = {
        "n_panels": summ.get("n_panels", 0),
        "mean_ic": summ.get("mean_ic"),
        "hac_t": hac_t,
        "hit_rate": summ.get("hit_rate"),
        "seed_deltas": None,
        # M-1 符號一致性:判決函式據此裁 FAIL_SIGN 並記 expected/observed(gate_json 驗收 A)
        "expected_direction": int(direction),
    }

    if summ.get("n_panels", 0) == 0:
        prom_ev["skipped_reason"] = "no as-of IC panels (missing FV / labels)"
        g_prom = evaluate_g_prom_from_evidence(prom_ev, cfg)
        g_econ = evaluate_g_econ_from_evidence(
            {"skipped_reason": "skipped: no IC panels → econ not run"}, cfg
        )
        # g_sign 此時 n_series=0 → UNJUDGEABLE⇒FAIL(fail-closed；非 SKIP——儀器有跑、樣本不足非證據)
        return g_prom, g_econ, g_sign

    # —— multi-seed 增量（Ridge-only；方法論 §四 (c)；不跑 GBDT 以免放量過慢）——
    if skip_multi_seed:
        prom_ev["seed_deltas"] = None
        prom_ev["multi_seed_note"] = "caller --skip-multi-seed → triad partial SKIP"
    elif prod_feats is None:
        prom_ev["seed_deltas"] = None
        prom_ev["multi_seed_note"] = "canonical_features unavailable"
    else:
        if feature in prod_feats:
            base_feats = [f for f in prod_feats if f != feature]
            add_feats = list(prod_feats)
        else:
            base_feats = list(prod_feats)
            add_feats = list(prod_feats) + [feature]
        deltas: list[float] = []
        try:
            # Ridge 本身確定性；用 panel bootstrap（80%）當 ≥3 seed 變異來源（等價 JSON 證據）
            rng = np.random.default_rng(42)
            n_take = max(10, int(round(0.8 * len(panels))))
            n_take = min(n_take, len(panels))
            for k in range(min_seeds):
                idx = sorted(rng.choice(len(panels), size=n_take, replace=False).tolist())
                sub = [panels[i] for i in idx]
                b = _ridge_mean_ic(conn, sub, h, base_feats)
                a = _ridge_mean_ic(conn, sub, h, add_feats)
                if b is None or a is None:
                    continue
                deltas.append(float(a) - float(b))
            prom_ev["seed_deltas"] = deltas if deltas else None
            prom_ev["multi_seed_method"] = "ridge_panel_bootstrap_80pct"
            if not deltas:
                prom_ev["multi_seed_note"] = "ridge ladder returned no IC for seeds"
        except Exception as e:  # noqa: BLE001 — 誠實 SKIP，不假 FAIL 噪音
            prom_ev["seed_deltas"] = None
            prom_ev["multi_seed_note"] = f"multi-seed error: {type(e).__name__}: {e}"[:200]

    g_prom = evaluate_g_prom_from_evidence(prom_ev, cfg)

    # —— G-ECON 單因子 #14 ——
    econ_ev: dict = {}
    try:
        bt = portfolio.run_backtest(
            conn,
            panels,
            h,
            feats=[feature],
            top_frac=top_frac,
            cost=cost,
            asof=True,
            model="B2_ridge",
        )
        if not bt:
            econ_ev["skipped_reason"] = "backtest empty (n_periods<3 or matrix gaps)"
        else:
            pn = bt.get("portfolio_net") or {}
            bn = bt.get("benchmark_net") or {}
            econ_ev = {
                "port_sharpe": pn.get("sharpe"),
                "bench_sharpe": bn.get("sharpe"),
                "max_dd": pn.get("max_drawdown"),
                "n_periods": bt.get("n_periods"),
                "span": bt.get("span"),
                "avg_turnover": bt.get("avg_turnover"),
            }
    except Exception as e:  # noqa: BLE001
        econ_ev = {"skipped_reason": f"econ error: {type(e).__name__}: {e}"[:200]}

    g_econ = evaluate_g_econ_from_evidence(econ_ev, cfg)
    return g_prom, g_econ, g_sign


def _draw_abs_hac(panel_data: list, arm: str, rng) -> float | None:
    """單一 draw 之 |hac_t|(純函式;IO 在呼叫端)。panel_data=[(preds{stock:val}, labels{stock:ret}),…]。

    shuffled  =逐 panel 打亂 labels(零訊號 null;floor 語意)——量閘的經驗偽陽率。
    mismatched=固定一個 stock 置換 π 施於全 panels(特徵自相關保留、對到錯的股票)——
               「量級對、類別選錯」null(mismatched 語意;volume_gini_60d 型失效的母體)。
    決定性:common/pool 皆排序後才餵 rng;同 seed 同結果。
    """
    from augur.evaluation import metrics

    perm_map = None
    if arm == "mismatched":
        pool = sorted({s for preds, _ in panel_data for s in preds})
        if len(pool) < 5:
            return None
        shuffled_pool = list(pool)
        rng.shuffle(shuffled_pool)
        perm_map = dict(zip(pool, shuffled_pool))
    ic_by: dict = {}
    for i, (preds, labs) in enumerate(panel_data):
        common = sorted(s for s in preds if s in labs)
        if len(common) < 5:
            continue
        if arm == "shuffled":
            vals = [labs[s] for s in common]
            idx = rng.permutation(len(vals))
            labd = {s: float(vals[int(j)]) for s, j in zip(common, idx)}
            ic = metrics.rank_ic({s: preds[s] for s in common}, labd)
        elif arm == "mismatched":
            pr = {s: preds[perm_map[s]] for s in common if perm_map.get(s) in preds}
            if len(pr) < 5:
                continue
            ic = metrics.rank_ic(pr, {s: labs[s] for s in pr})
        else:
            raise ValueError(f"未知對照臂:{arm}")
        if ic is not None:
            ic_by[i] = ic
    if len(ic_by) < 10:
        return None
    t = metrics.effective_t_hac(ic_by)
    return abs(float(t)) if t is not None else None


def run_control_arms(*, since: str, horizon_h: int, draws: int, seed: int) -> int:
    """M-1 對照臂(V2-CTRL-go 2026-07-27):null 分布走同一 local-gates 統計路徑(rank_ic+HAC)。

    結果寫 evolution_evidence_run(axis='tw', arm∈{shuffled,mismatched},
    metric='hac_t_abs_ge2_rate');detail 含 |hac_t| 分位數(p95=GATE-raise 預註冊規則輸入:
    經驗偽陽率>10% ⇒ min_abs_hac_t 升至經驗 95 分位;升嚴唯一方向)。
    中止條件(計畫 §6 Phase 4):壁鐘>2h → 提前收束、剩餘 draws 誠實記於 detail(統計力降)。
    """
    import hashlib as _hl

    import numpy as np

    from augur.core import db
    from augur.evaluation import label as label_mod

    t0 = time.monotonic()
    gcfg = DEFAULT_GATE_CONFIG.get("gates", {}).get("G-PROM", {})
    min_abs = float(gcfg.get("min_abs_hac_t", 2.0))
    rng = np.random.default_rng(seed)
    code_sha = _code_sha()

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date",
                (since,))
            panels = [r[0] for r in cur.fetchall()]
            cur.execute(
                "SELECT DISTINCT feature FROM feature_values WHERE panel_date>=%s", (since,))
            feats = sorted(r[0] for r in cur.fetchall())
        if len(panels) < 10 or not feats:
            print(f"✗ 素材不足:panels={len(panels)} feats={len(feats)}")
            return 1
        print(f"── control-arms draws={draws}/arm seed={seed} min_abs={min_abs} "
              f"panels={len(panels)} feats={len(feats)} ──", flush=True)
        cal = label_mod.full_calendar(conn)
        labels_by_panel: dict = {}
        for k, pd_ in enumerate(panels):
            with db.transaction(conn) as cur:
                cur.execute("SELECT DISTINCT stock_id FROM feature_values WHERE panel_date=%s", (pd_,))
                stk = [str(r[0]) for r in cur.fetchall()]
            labs = label_mod.labels(conn, pd_, stk, horizon_h, calendar=cal)
            labels_by_panel[pd_] = {s: v for s, v in labs.items() if v is not None}
            if (k + 1) % 25 == 0:
                print(f"  …labels {k+1}/{len(panels)}", flush=True)

        feat_data_cache: dict = {}

        def _panel_data(f: str) -> list:
            if f not in feat_data_cache:
                rows = []
                for pd_ in panels:
                    with db.transaction(conn) as cur:
                        cur.execute(
                            "SELECT stock_id, value FROM feature_values "
                            "WHERE panel_date=%s AND feature=%s", (pd_, f))
                        preds = {str(s): float(v) for s, v in cur.fetchall() if v is not None}
                    rows.append((preds, labels_by_panel[pd_]))
                feat_data_cache[f] = rows
            return feat_data_cache[f]

        # draws 屬組態(n=3 煙測與 n=200 全量是不同尺)→入 suite_id;
        # 撞 UNIQUE(axis,suite,code,arm,metric)實證 2026-07-27:煙測列佔鍵、全量寫入炸
        suite_id = _hl.sha256(json.dumps(
            {"feats": feats, "panels": [str(p) for p in panels], "h": horizon_h,
             "min_abs": min_abs, "draws": draws, "scheme": "control_arms_v1"},
            sort_keys=True).encode()).hexdigest()[:12]

        summary: dict = {}
        pending_rows: list[tuple] = []
        for arm in ("shuffled", "mismatched"):
            ts: list[float] = []
            attempted = 0
            truncated = False
            for d in range(draws):
                if time.monotonic() - t0 > 7200:
                    truncated = True
                    print(f"  ⚠ 壁鐘>2h 中止條件:{arm} 於 draw {d}/{draws} 提前收束(統計力降)", flush=True)
                    break
                attempted += 1
                f = feats[int(rng.integers(len(feats)))]
                t = _draw_abs_hac(_panel_data(f), arm, rng)
                if t is not None:
                    ts.append(t)
                if attempted % 25 == 0:
                    print(f"  …{arm} {attempted}/{draws}", flush=True)
            arr = np.array(ts) if ts else np.array([0.0])
            rate = float((np.array(ts) >= min_abs).mean()) if ts else None
            detail = {
                "seed": seed, "since": since, "h": horizon_h, "threshold": min_abs,
                "draws_requested": draws, "draws_attempted": attempted, "truncated": truncated,
                "abs_hac_p50": float(np.percentile(arr, 50)) if ts else None,
                "abs_hac_p95": float(np.percentile(arr, 95)) if ts else None,
                "abs_hac_p99": float(np.percentile(arr, 99)) if ts else None,
                "abs_hac_max": float(arr.max()) if ts else None,
                "n_features": len(feats), "n_panels": len(panels),
                "gate_raise_rule": "empirical_fp_rate>0.10 => min_abs_hac_t := p95 (預註冊 audits/V2-PHASE4-RUBRIC-H2-APPROVED-20260727)",
            }
            # 先印後寫:寫入失敗不得滅掉算了幾十分鐘的結果(2026-07-27 教訓——200 draws 因
            # UNIQUE 撞鍵在首筆 INSERT 全滅);兩臂算完一次交易落庫
            summary[arm] = {"rate": rate, "p95": detail["abs_hac_p95"], "n_valid": len(ts)}
            print(f"  [{arm:<10}] 偽陽率(|hac_t|≥{min_abs})={rate if rate is not None else 'N/A'} "
                  f" p95={detail['abs_hac_p95']}  n_valid={len(ts)}/{attempted}", flush=True)
            print(f"    detail={json.dumps(detail, ensure_ascii=False)}", flush=True)
            pending_rows.append((suite_id, code_sha, arm, rate, attempted, len(ts),
                                 attempted - len(ts), rate is None, attempted, json.dumps(detail)))
        with db.transaction(conn) as cur:
            for row in pending_rows:
                cur.execute(
                    """INSERT INTO evolution_evidence_run
                       (axis, suite_id, code_hash, arm, metric_name, metric_value,
                        n_items, n_valid, n_excluded, is_invalid, n_trials, selection_scope, detail)
                       VALUES ('tw', %s, %s, %s, 'hac_t_abs_ge2_rate', %s, %s, %s, %s, %s, %s,
                               'control_arms_v1', %s)""", row)

    worst = max((v["rate"] or 0.0) for v in summary.values())
    if worst > 0.10:
        p95s = [v["p95"] for v in summary.values() if v["p95"] is not None]
        print(f"  ⚠ GATE-raise 預註冊規則觸發:經驗偽陽率 {worst:.1%} > 10% ⇒ "
              f"APPLY 篩以經驗 95 分位 {max(p95s):.3f} 取代 min_abs_hac_t={min_abs}(升嚴;R2(c))")
    else:
        print(f"  ✓ 經驗偽陽率 ≤10%(最壞 {worst:.1%}):min_abs_hac_t={min_abs} 維持")
    print(f"  suite_id={suite_id} code={code_sha[:12]} 壁鐘={time.monotonic()-t0:.0f}s "
          f"(evidence_run 已落 2 列)")
    return 0


def _supersede_stale_pending(cur, run_id: int, feature: str) -> int:
    """I5B-甲(裁決 I5B-照建議):開新世代列前,同 feature 舊 run 之 pending_auto 標 superseded。

    最窄謂詞=pending_auto ∧ 同 feature ∧ run_id<本 run——同 run 多 principle 合法列、
    已裁列(applied/rejected_gate/halted)永不觸碰(機器僅關機器 pending,不碰人裁);
    decided_by 自陳世代供逐列稽核(非人簽、不代打)。UPDATE 過誠實帳本閘(B4-P2a)須 GUC
    通行證,與新列 INSERT 同交易=世代交替原子性。前置 DDL:queue_status CHECK 須含 superseded。
    """
    cur.execute("SET LOCAL augur.honesty_write = 'on'")
    cur.execute(
        "UPDATE promotion_queue SET queue_status='superseded', decided_at=now(), "
        "decided_by=%s "
        "WHERE queue_status='pending_auto' AND feature=%s AND run_id < %s",
        (f"superseded_by_run_{run_id}", feature, run_id))
    return cur.rowcount


def run_evolution(
    *,
    since: str,
    horizon_h: int,
    dry_run: bool,
    mode: str,
    with_local: bool,
    skip_multi_seed: bool,
) -> int:
    from augur.core import db
    from augur.evaluation import baseline

    cfg = dict(DEFAULT_GATE_CONFIG)
    cfg["mode"] = mode
    cfg["with_local_evidence"] = with_local
    cfg["skip_multi_seed"] = skip_multi_seed
    cfg["since"] = since
    cfg["horizon_h"] = horizon_h
    sha = _code_sha()
    g_iso = _g_iso()
    g_noexec = _g_noexec()
    attest_ok = attest_complete(
        code_sha=sha, since_date=since, horizon_h=horizon_h, config_json=cfg
    )
    g_attest = {
        "verdict": "PASS" if attest_ok else "FAIL",
        "code_sha": sha,
        "since": since,
        "horizon_h": horizon_h,
    }

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_run')")
        if cur.fetchone()[0] is None:
            print("✗ 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        # V2 Phase 2.4(C6):逐 scope 口徑——本引擎屬 tw 軸;自軸或 global 任一 halt 即停(OR、fail-safe)
        cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('tw','global')")
        kill_states = [r[0] for r in cur.fetchall()]
        kill_db = "halt" if "halt" in kill_states else (kill_states[0] if kill_states else KILL_CLEAR)
        kill_eff = effective_kill_state(kill_states, env_halt=_env_halt())
        g_kill = {
            "verdict": "PASS" if kill_eff == KILL_CLEAR else "FAIL",
            "state": kill_eff,
            "db": kill_db,
        }
        maps = _load_maps(cur)
        cur.execute(
            "SELECT DISTINCT panel_date FROM feature_values "
            "WHERE panel_date>=%s ORDER BY panel_date",
            (since,),
        )
        panels = [r[0] for r in cur.fetchall()]

    feat_class: dict[str, str] = {}
    for m in maps:
        feat_class[m["feature"]] = classify_coverage(
            m["feature"], in_feature_values=bool(m["in_fv"])
        )

    print(f"── PME S2 mode={mode} ──")
    print(f"  maps={len(maps)} panels={len(panels)} kill={kill_eff}")
    print(f"  G-ISO={g_iso['verdict']} G-NOEXEC={g_noexec['verdict']} G-ATTEST={g_attest['verdict']}")
    print(f"  dry_run={dry_run} skip_multi_seed={skip_multi_seed}")

    # per-feature gate cache（同 feature 多 principle 共用）
    gate_cache: dict[str, tuple[dict, dict, dict]] = {}
    prod_feats: list[str] | None = None
    if mode == "local_gates" and panels:
        with db.connect() as conn:
            try:
                prod_feats = baseline.canonical_features(conn, panels)
                print(f"  canonical_features n={len(prod_feats)}")
            except Exception as e:  # noqa: BLE001
                print(f"  ⚠ canonical_features failed: {e} → multi-seed will SKIP")
                prod_feats = None

    # G-SIGN 雙寫 feature_sign_check（僅 live 非 dry-run；A3 §3.4.5）。表未建=大聲警告後略過
    # （不擋輪；訊息每 run stdout 可見、非靜默），gate_json 內之 G-SIGN verdict 不受影響。
    sign_sink = {"checked": False, "ok": False}

    def _sign_record(f: str, gs: dict) -> None:
        vss = _vss()
        if not sign_sink["checked"]:
            sign_sink["checked"] = True
            with db.connect() as c, db.transaction(c) as cur:
                cur.execute("SELECT to_regclass('public.feature_sign_check')")
                sign_sink["ok"] = cur.fetchone()[0] is not None
            if not sign_sink["ok"]:
                print("  ⚠ feature_sign_check 未建——G-SIGN 只落 gate_json、sign 帳本缺頁"
                      "（先跑 scripts/migrate_feature_sign_check_ddl.py --apply）", flush=True)
        if not sign_sink["ok"]:
            return
        ev = gs.get("evidence") or {}
        pt = ev.get("point_ic")
        rows = vss.build_sign_rows(
            f, ev.get("direction"), ev.get("direction_source"),
            [(horizon_h, gs.get("judge", "UNJUDGEABLE"),
              (float(pt) if pt is not None else float("nan")),
              int(ev.get("n_series") or 0), list(ev.get("boot_ics") or []))],
            [str(p) for p in panels], sha)
        with db.connect() as c, db.transaction(c) as cur:
            vss._record_rows(cur, rows)

    def gates_for(m: dict) -> tuple[dict, dict, dict]:
        f = m["feature"]
        cls = feat_class[f]
        if mode != "local_gates":
            return _prom_econ_skeleton(m, with_local=with_local)
        if cls in ("blocked_div", "missing", "retired"):
            reason = f"coverage_class={cls}; G-PROM/G-ECON not evaluated"
            return (
                {"verdict": "SKIP", "reason": reason, "coverage_class": cls},
                {"verdict": "SKIP", "reason": reason, "coverage_class": cls},
                {"verdict": "SKIP", "reason": f"coverage_class={cls}; G-SIGN not evaluated",
                 "coverage_class": cls},
            )
        if f in gate_cache:
            return gate_cache[f]
        t0 = time.monotonic()
        print(f"  … local-gates compute {f} (dir={m['direction']:+d}) …", flush=True)
        with db.connect() as conn:
            gp, ge, gs = _compute_feature_gates(
                conn,
                feature=f,
                direction=int(m["direction"] or 1),
                panels=panels,
                h=horizon_h,
                cfg=cfg,
                skip_multi_seed=skip_multi_seed,
                prod_feats=prod_feats,
            )
        print(
            f"    → G-PROM={gp['verdict']} G-ECON={ge['verdict']} SIGN={gs['verdict']} "
            f"({time.monotonic()-t0:.1f}s)",
            flush=True,
        )
        gate_cache[f] = (gp, ge, gs)
        if not dry_run and gs.get("verdict") != "SKIP":
            _sign_record(f, gs)
        return gp, ge, gs

    if dry_run:
        sample = maps[:5] if mode == "local_gates" else maps[:3]
        for m in sample:
            cls = feat_class[m["feature"]]
            g_map = {
                "verdict": "PASS" if cls == "mapped" else "FAIL",
                "coverage_class": cls,
            }
            g_prom, g_econ, g_sign = gates_for(m)
            gj = build_gate_json(
                g_iso=g_iso,
                g_map=g_map,
                g_prom=g_prom,
                g_econ=g_econ,
                g_attest=g_attest,
                g_kill=g_kill,
                g_noexec=g_noexec,
                g_sign=g_sign,
            )
            dry_action = map_action_from_evidence(
                coverage_class=cls,
                g_prom_pass=g_prom.get("verdict") == "PASS",
                g_econ_pass=g_econ.get("verdict") == "PASS",
            )
            qs = decide_queue_status(gj, kill_eff, action=dry_action)
            print(
                f"  dry {m['feature']}: class={cls} "
                f"PROM={g_prom.get('verdict')} ECON={g_econ.get('verdict')} "
                f"SIGN={g_sign.get('verdict')} "
                f"action={dry_action} →{qs}"
            )
        return 0

    notes = f"S2 {mode}"
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            """
            INSERT INTO evolution_run
              (since_date, horizon_h, code_sha, config_json, status, kill_switch_at_start, notes)
            VALUES (%s, %s, %s, %s::jsonb, 'running', %s, %s)
            RETURNING run_id
            """,
            (date.fromisoformat(since), horizon_h, sha, json.dumps(cfg), kill_eff, notes),
        )
        run_id = cur.fetchone()[0]
        _ACTIVE_RUN["id"], _ACTIVE_RUN["closed"] = run_id, False   # B1 登記（收尾錨）

        seen = set()
        for m in maps:
            f = m["feature"]
            if f in seen:
                continue
            seen.add(f)
            cls = feat_class[f]
            n_maps = sum(1 for x in maps if x["feature"] == f)
            cur.execute(
                """
                INSERT INTO evolution_coverage_snapshot
                  (run_id, feature, map_count, in_feature_values, coverage_class, detail)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    run_id,
                    f,
                    n_maps,
                    bool(m["in_fv"]),
                    cls,
                    json.dumps({"phase": f"S2-{mode}"}),
                ),
            )

    # queue 列：local-gates 計算可能很久 → 逐筆短交易，避免長鎖
    n_pending = n_rej = n_halt = n_superseded = 0
    verdict_tally = {"G-PROM": {}, "G-ECON": {}, "G-SIGN": {}}
    for m in maps:
        cls = feat_class[m["feature"]]
        g_map = {
            "verdict": "PASS" if cls == "mapped" else "FAIL",
            "coverage_class": cls,
            "in_feature_values": bool(m["in_fv"]),
        }
        g_prom, g_econ, g_sign = gates_for(m)
        for gid, gv in (("G-PROM", g_prom), ("G-ECON", g_econ), ("G-SIGN", g_sign)):
            v = str(gv.get("verdict", "FAIL"))
            verdict_tally[gid][v] = verdict_tally[gid].get(v, 0) + 1
        gj = build_gate_json(
            g_iso=g_iso,
            g_map=g_map,
            g_prom=g_prom,
            g_econ=g_econ,
            g_attest=g_attest,
            g_kill=g_kill,
            g_noexec=g_noexec,
            g_sign=g_sign,
        )
        action = map_action_from_evidence(
            coverage_class=cls,
            g_prom_pass=g_prom.get("verdict") == "PASS",
            g_econ_pass=g_econ.get("verdict") == "PASS",
        )
        # action 先算再裁 queue_status:demote+FAIL_SIGN → pending_auto(R3 除役通道)
        qs = decide_queue_status(gj, kill_eff, action=action)
        with db.connect() as conn, db.transaction(conn) as cur:
            # I5B-甲:同交易先關同 feature 舊世代 pending(冪等;該 feature 首列即清空,
            # 後續 0 列)。kill halt 期間不動舊列(halt=照跑但不採用;供下個 clear run 自癒補關,
            # 謂詞 run_id<本 run 天然跨代補抓)。
            if kill_eff == KILL_CLEAR:
                n_superseded += _supersede_stale_pending(cur, run_id, m["feature"])
            cur.execute(
                """
                INSERT INTO promotion_queue
                  (run_id, principle_id, feature, action, gate_json, queue_status, decided_by)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s,'evolution_engine')
                """,
                (run_id, m["principle_id"], m["feature"], action, json.dumps(gj), qs),
            )
        if qs == "pending_auto":
            n_pending += 1
        elif qs == "halted":
            n_halt += 1
        else:
            n_rej += 1

    final = "halted" if kill_eff == KILL_HALT else "succeeded"
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2b)
        cur.execute(
            "UPDATE evolution_run SET finished_at=now(), status=%s WHERE run_id=%s",
            (final, run_id),
        )
    _ACTIVE_RUN["closed"] = True            # B1：正常關帳，abort 收尾不再介入

    print(f"✓ run_id={run_id} status={final} queue pending={n_pending} rejected={n_rej} "
          f"halted={n_halt} superseded_stale={n_superseded}")
    print(f"  G-PROM tally={verdict_tally['G-PROM']} G-ECON tally={verdict_tally['G-ECON']} "
          f"G-SIGN tally={verdict_tally['G-SIGN']}")
    if n_pending:
        print(f"  → S3: python scripts/apply_evolution_promotions.py --run-id {run_id}")
    else:
        print("  → 無 pending_auto（閘未全綠／SKIP／FAIL）— 不假綠 APPLY")
    return 0


# ── B1 寫者自收尾（登錄冊 2026-08-01）────────────────────────────────────────
# 病：引擎半途被殺（driver 逾時 kill／2h 快車道砍）時 evolution_run 之 'running' 列
# 無人收尾——殭屍累積 run 11-19 共 9 列，未來每次被殺再產一列。
# 解：SIGTERM→SystemExit（讓 finally/except 有機會跑；SIGKILL 攔不到＝回填器的事）；
# 開輪後登記 run_id，未正常關帳而退出時以**新短連線**補記 failed+aborted note
# （主連線可能正處 aborted transaction，不可複用）。
_ACTIVE_RUN: dict = {"id": None, "closed": False}


def _sigterm_to_exit(signum, frame):  # noqa: ARG001
    raise SystemExit(128 + signum)


def _abort_status(exc) -> tuple[str, str]:
    """例外 → (status, note)。**純函式**——自測餵真例外驗。"""
    return "failed", f"aborted: {type(exc).__name__}: {exc}"[:200]


def _abort_close(run_id, exc) -> None:
    st, note = _abort_status(exc)
    try:
        from augur.core import db          # 本檔慣例＝函式內延遲 import（模組層無 db 名）
        with db.connect() as c2, c2.cursor() as cu:
            cu.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2b)
            cu.execute(
                "UPDATE evolution_run SET finished_at=now(), status=%s, "
                "notes=COALESCE(notes||' | ','')||%s "
                "WHERE run_id=%s AND status='running'", (st, note, run_id))
            n = cu.rowcount
            c2.commit()
        # rowcount 誠實：0 列（已被他人關帳/列不存在）不得印「已補記」——那是另一種假綠
        print(f"⚠ run {run_id} " + (f"已補記 {st}（{note}）——不留殭屍 running" if n
                                     else "無 running 列可補（已關帳或不存在）——無動作"))
    except Exception as e2:  # noqa: BLE001
        # 收尾失敗不得吞掉原始例外；印明留給回填器（防呆機制自己不得靜默失效）
        print(f"⚠ abort-close 亦失敗（{type(e2).__name__}）——留給回填器", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--skeleton", action="store_true")
    ap.add_argument("--local-gates", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--with-local-evidence", action="store_true")
    ap.add_argument(
        "--skip-multi-seed",
        action="store_true",
        help="local-gates 時略過 G-PROM (c)；結果必非假 PASS（triad partial SKIP）",
    )
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--control-arms", action="store_true",
                    help="M-1 對照臂:置換+錯配 null 走同一統計路徑→evolution_evidence_run(V2-CTRL-go)")
    ap.add_argument("--draws", type=int, default=200, help="每臂 draw 數(預設 200;煙測可降)")
    ap.add_argument("--arm-seed", type=int, default=42)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.control_arms:
        return run_control_arms(since=args.since, horizon_h=args.h,
                                draws=args.draws, seed=args.arm_seed)
    if args.local_gates:
        mode = "local_gates"
    elif args.skeleton or args.dry_run:
        mode = "skeleton"
    else:
        print((__doc__ or "").split("🎯")[0].strip())
        print("安全預設：請顯式 --skeleton / --local-gates / --dry-run（或 --selftest）")
        print("例: python scripts/run_philosophy_evolution.py --local-gates")
        return 0
    import signal
    signal.signal(signal.SIGTERM, _sigterm_to_exit)
    try:
        return run_evolution(
            since=args.since,
            horizon_h=args.h,
            dry_run=bool(args.dry_run),
            mode=mode,
            with_local=args.with_local_evidence,
            skip_multi_seed=bool(args.skip_multi_seed),
        )
    except BaseException as e:              # noqa: BLE001  SystemExit/KeyboardInterrupt 皆須收尾
        if _ACTIVE_RUN["id"] is not None and not _ACTIVE_RUN["closed"]:
            _abort_close(_ACTIVE_RUN["id"], e)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
