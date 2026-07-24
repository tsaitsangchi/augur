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
    attest_complete,
    build_gate_json,
    classify_coverage,
    decide_queue_status,
    evaluate_g_econ_from_evidence,
    evaluate_g_prom_from_evidence,
    map_action_from_evidence,
    normalize_kill_state,
    scan_noexec_text,
)


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

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
    )
    chk("local green → pending_auto", decide_queue_status(g2, KILL_CLEAR) == "pending_auto")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


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


def _prom_econ_skeleton(row: dict, *, with_local: bool) -> tuple[dict, dict]:
    """G-PROM／G-ECON：skeleton 預設 SKIP；--with-local-evidence 僅附 validated_* 仍 SKIP。"""
    if not with_local:
        return (
            {"verdict": "SKIP", "reason": "skeleton; use --local-gates for PASS/FAIL"},
            {"verdict": "SKIP", "reason": "skeleton; use --local-gates for PASS/FAIL"},
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
    return prom, econ


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
) -> tuple[dict, dict]:
    """本地 DB 重算單一 feature 之 G-PROM／G-ECON（零外部 API）。"""
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
    prom_ev: dict = {
        "n_panels": summ.get("n_panels", 0),
        "mean_ic": summ.get("mean_ic"),
        "hac_t": hac_t,
        "hit_rate": summ.get("hit_rate"),
        "seed_deltas": None,
    }

    if summ.get("n_panels", 0) == 0:
        prom_ev["skipped_reason"] = "no as-of IC panels (missing FV / labels)"
        g_prom = evaluate_g_prom_from_evidence(prom_ev, cfg)
        g_econ = evaluate_g_econ_from_evidence(
            {"skipped_reason": "skipped: no IC panels → econ not run"}, cfg
        )
        return g_prom, g_econ

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
    return g_prom, g_econ


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
        cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id=1")
        row = cur.fetchone()
        kill_db = row[0] if row else KILL_CLEAR
        kill_eff = normalize_kill_state(kill_db, env_halt=_env_halt())
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
    gate_cache: dict[str, tuple[dict, dict]] = {}
    prod_feats: list[str] | None = None
    if mode == "local_gates" and panels:
        with db.connect() as conn:
            try:
                prod_feats = baseline.canonical_features(conn, panels)
                print(f"  canonical_features n={len(prod_feats)}")
            except Exception as e:  # noqa: BLE001
                print(f"  ⚠ canonical_features failed: {e} → multi-seed will SKIP")
                prod_feats = None

    def gates_for(m: dict) -> tuple[dict, dict]:
        f = m["feature"]
        cls = feat_class[f]
        if mode != "local_gates":
            return _prom_econ_skeleton(m, with_local=with_local)
        if cls in ("blocked_div", "missing", "retired"):
            reason = f"coverage_class={cls}; G-PROM/G-ECON not evaluated"
            return (
                {"verdict": "SKIP", "reason": reason, "coverage_class": cls},
                {"verdict": "SKIP", "reason": reason, "coverage_class": cls},
            )
        if f in gate_cache:
            return gate_cache[f]
        t0 = time.monotonic()
        print(f"  … local-gates compute {f} (dir={m['direction']:+d}) …", flush=True)
        with db.connect() as conn:
            gp, ge = _compute_feature_gates(
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
            f"    → G-PROM={gp['verdict']} G-ECON={ge['verdict']} "
            f"({time.monotonic()-t0:.1f}s)",
            flush=True,
        )
        gate_cache[f] = (gp, ge)
        return gp, ge

    if dry_run:
        sample = maps[:5] if mode == "local_gates" else maps[:3]
        for m in sample:
            cls = feat_class[m["feature"]]
            g_map = {
                "verdict": "PASS" if cls == "mapped" else "FAIL",
                "coverage_class": cls,
            }
            g_prom, g_econ = gates_for(m)
            gj = build_gate_json(
                g_iso=g_iso,
                g_map=g_map,
                g_prom=g_prom,
                g_econ=g_econ,
                g_attest=g_attest,
                g_kill=g_kill,
                g_noexec=g_noexec,
            )
            qs = decide_queue_status(gj, kill_eff)
            print(
                f"  dry {m['feature']}: class={cls} "
                f"PROM={g_prom.get('verdict')} ECON={g_econ.get('verdict')} →{qs}"
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
    n_pending = n_rej = n_halt = 0
    verdict_tally = {"G-PROM": {}, "G-ECON": {}}
    for m in maps:
        cls = feat_class[m["feature"]]
        g_map = {
            "verdict": "PASS" if cls == "mapped" else "FAIL",
            "coverage_class": cls,
            "in_feature_values": bool(m["in_fv"]),
        }
        g_prom, g_econ = gates_for(m)
        for gid, gv in (("G-PROM", g_prom), ("G-ECON", g_econ)):
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
        )
        qs = decide_queue_status(gj, kill_eff)
        action = map_action_from_evidence(
            coverage_class=cls,
            g_prom_pass=g_prom.get("verdict") == "PASS",
            g_econ_pass=g_econ.get("verdict") == "PASS",
        )
        with db.connect() as conn, db.transaction(conn) as cur:
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
        cur.execute(
            "UPDATE evolution_run SET finished_at=now(), status=%s WHERE run_id=%s",
            (final, run_id),
        )

    print(f"✓ run_id={run_id} status={final} queue pending={n_pending} rejected={n_rej} halted={n_halt}")
    print(f"  G-PROM tally={verdict_tally['G-PROM']} G-ECON tally={verdict_tally['G-ECON']}")
    if n_pending:
        print(f"  → S3: python scripts/apply_evolution_promotions.py --run-id {run_id}")
    else:
        print("  → 無 pending_auto（閘未全綠／SKIP／FAIL）— 不假綠 APPLY")
    return 0


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
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.local_gates:
        mode = "local_gates"
    elif args.skeleton or args.dry_run:
        mode = "skeleton"
    else:
        print((__doc__ or "").split("🎯")[0].strip())
        print("安全預設：請顯式 --skeleton / --local-gates / --dry-run（或 --selftest）")
        print("例: python scripts/run_philosophy_evolution.py --local-gates")
        return 0
    return run_evolution(
        since=args.since,
        horizon_h=args.h,
        dry_run=bool(args.dry_run),
        mode=mode,
        with_local=args.with_local_evidence,
        skip_multi_seed=bool(args.skip_multi_seed),
    )


if __name__ == "__main__":
    raise SystemExit(main())
