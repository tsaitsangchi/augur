#!/usr/bin/env python
"""方向 GATE 機械裁判 — 讀 direction_oos_sample 對已核准 gate 判三關(oracle 主計畫 §2.6;憲章 v1.42.0)。

🎯 這支在做什麼(白話):把「approve 時凍死的判準」用 OOS 真數字機械覆算,判 pass/fail——**無人為裁量、
   無挪門柱**(criteria 由 trigger 鎖死;此支只讀不改 criteria)。三關(全出 OOS,禁編數):
   (i) hit-rate 顯著優於「同窗多數類樸素基線 max(p̄,1−p̄)」:逐 panel 算 (hit−base) 序列 → HAC 去相關
       Eff-t(禁裸 iid,重疊窗高估)→ 單尾 p<0.05;
   (ii) OOS Brier < 基線 p̄(1−p̄)(常數基率預測之 Brier);
   (iii) 校準:ECE ≤ judgestop 凍結上限(criteria 內 DB 讀值)且 p_up 十分位 vs 實現上漲頻率單調(Spearman>0)。
   三關全過=evaluated_pass;任一不過=evaluated_fail(判死留檔、永不出 UI)。H120 即便過,review_tier_cap
   限「觀察名單」(結果快照標記,展示端據以降級)。裁決全落 result_snapshot(可溯,#10)。**這是機械層、非
   人閘**:AI/腳本可跑(如 verify_claim);approve 才唯人。終態不可回改(trigger);重判=另立新 gate。

守 #15(裁決全出 OOS、禁編數)· #8(直接吃已 OOS 之 direction_oos_sample)· #12(ECE 上限 DB 讀值、口徑複用)
   · #10(result_snapshot 可溯)· #29a/d。前置=train_direction_stack.py --run + gate status=approved。
   SSOT=reports/augur_oracle_upgrade_master_plan_20260711.md §2.6。

執行指令矩陣:
  python scripts/evaluate_direction_gate.py                       # 無參數:gate 現況+可判性(唯讀)
  python scripts/evaluate_direction_gate.py --evaluate dgate_H_20 # 判單一 gate
  python scripts/evaluate_direction_gate.py --evaluate-all        # 判所有 approved gate(有 OOS 資料者)
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db
from augur.evaluation.metrics import effective_t_hac


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _ece(p, y, bins=10):
    """expected calibration error:等寬十分位,Σ (n_b/N)·|conf_b − acc_b|。"""
    p, y = np.asarray(p, float), np.asarray(y, float)
    edges = np.linspace(0, 1, bins + 1)
    n, e = len(p), 0.0
    for b in range(bins):
        lo, hi = edges[b], edges[b + 1]
        m = (p >= lo) & (p < hi if b < bins - 1 else p <= hi)
        if m.sum():
            e += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return float(e)


def _spearman_monotone(p, y, bins=10):
    """p_up 十分位桶之(平均 p, 實現上漲頻率)Spearman;桶不足 3 → None。回 rho。"""
    p, y = np.asarray(p, float), np.asarray(y, float)
    order = np.argsort(p)
    p, y = p[order], y[order]
    qs = np.array_split(np.arange(len(p)), bins)
    xs, ys = [], []
    for q in qs:
        if len(q):
            xs.append(p[q].mean()); ys.append(y[q].mean())
    if len(xs) < 3:
        return None
    rx = np.argsort(np.argsort(xs)); ry = np.argsort(np.argsort(ys))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    denom = math.sqrt(float(rx @ rx) * float(ry @ ry))
    return float(rx @ ry / denom) if denom > 0 else None


def _assert_clean_tree():
    """判前斷言(revival plan §3.1):工作樹 clean+evaluation_ref=實際 HEAD——腳本內容可被 git 釘死。
    v1 程序教訓:判決時 evaluate 腳本未入 git,evaluation_ref 釘不住內容。"""
    root = str(Path(__file__).resolve().parent.parent)
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=root).stdout.strip()
    if dirty:
        sys.exit(f"✗ 判前斷言失敗:工作樹不乾淨(先 commit 再判;evaluation_ref 須真能釘住腳本內容)\n{dirty[:400]}")


def _fetch_samples(cur, gate_id, track, h, criteria):
    """estimand 引擎(revival plan §3.1):criteria 內機械樣本定義(model_id/窗/seed 聚合)→ 參數化取樣;
    無 estimand 之 gate(v1 遺產)→ 斷言範圍內單一 model_id,多 family 未指名=拒判(挪門柱後門封死)。
    回 list[(panel_date, p_up, y_up)](seed 已聚合)。"""
    est = criteria.get("estimand")
    tbl, hcol = ("direction_oos_sample", "horizon") if track == "H" else ("daily_direction_oos_sample", "k_td")
    if est:
        tbl, hcol = est["table"], est["hcol"]
        q = f"SELECT panel_date, target_id, p_up, y_up, seed FROM {tbl} WHERE {hcol}=%s AND model_id=%s"
        params = [h, est["model_id"]]
        win = est.get("panel_window")
        if win:
            q += " AND panel_date >= %s AND panel_date <= %s"
            params += [win[0], win[1]]
        cur.execute(q + " ORDER BY panel_date", params)
        raw = cur.fetchall()
        if not raw:
            return None
        agg = est.get("seed_aggregation", "seed0")
        if agg == "seed0":
            return [(p, float(pu), int(y)) for p, t, pu, y, sd in raw if sd == 0]
        grp = {}
        for p, t, pu, y, sd in raw:                       # mean:同 (panel,target) 對 seeds 取均值成一列
            grp.setdefault((p, t), []).append((float(pu), int(y)))
        return [(p, float(np.mean([x[0] for x in v])), v[0][1]) for (p, t), v in sorted(grp.items())]
    cur.execute(f"SELECT count(DISTINCT model_id) FROM {tbl} WHERE {hcol}=%s", (h,))
    if cur.fetchone()[0] > 1:
        print(f"  ✗ {gate_id}:{tbl} h={h} 含多個 model_id 而 criteria 無 estimand 指名——拒判(revival §3.1)")
        return "REFUSE"
    cur.execute(f"SELECT panel_date, p_up, y_up FROM {tbl} WHERE {hcol}=%s ORDER BY panel_date", (h,))
    return [(p, float(pu), int(y)) for p, pu, y in cur.fetchall()]


def _evaluate_one(cur, gate_id):
    cur.execute("SELECT track, horizon, criteria, status FROM direction_gate WHERE gate_id=%s", (gate_id,))
    row = cur.fetchone()
    if not row:
        print(f"  ✗ {gate_id} 不存在"); return None
    track, h, criteria, status = row
    if status != "approved":
        print(f"  ⤳ {gate_id} status={status}≠approved(終態不可回改;重判=另立新 gate)—略"); return None
    data = _fetch_samples(cur, gate_id, track, h, criteria)
    if data == "REFUSE":
        return None
    if not data:
        print(f"  ⤳ {gate_id} 無 OOS 資料(先跑訓練器)—略"); return None

    by_panel = {}
    for pd_, p_up, y_up in data:
        by_panel.setdefault(pd_, []).append((float(p_up), int(y_up)))
    P = np.array([d[1] for d in data], float)
    Y = np.array([d[2] for d in data], float)
    pbar = float(Y.mean())
    base_major = max(pbar, 1 - pbar)

    # (i) 逐 panel (model_hit − naive_hit) 序列 → HAC Eff-t → 單尾 p。
    #     naive=全局多數類「固定方向」(非逐 panel 偷看實現值挑贏面之千里眼基線):
    #     全局 p̄≥0.5 → 一律預測 up,naive 逐 panel hit = p̄_panel;否則一律 down,hit = 1−p̄_panel。
    majority_up = pbar >= 0.5
    diff_by_panel = {}
    for pd_, rs in by_panel.items():
        yy = np.array([r[1] for r in rs], float)
        hit = float(np.mean([(pp > 0.5) == (yy_i > 0.5) for pp, yy_i in rs]))
        pj = float(yy.mean())
        naive = pj if majority_up else (1 - pj)
        diff_by_panel[pd_] = hit - naive
    alpha = float(criteria.get("alpha", 0.05))
    n_pan = len(diff_by_panel)
    lag = max(1, int(np.floor(4 * (n_pan / 100) ** (2 / 9))))
    min_lag = criteria.get("hac_min_lag")
    if min_lag:
        lag = max(lag, int(min_lag))                      # 月頻重疊窗覆蓋(criteria 凍結;revival §3.1)
    t = effective_t_hac(diff_by_panel, lag=lag)
    p_one = (1 - _phi(t)) if t is not None else None
    overall_hit = float(np.mean([(P > 0.5) == (Y > 0.5)]))
    c1 = t is not None and p_one is not None and p_one < alpha

    # (ii) Brier
    brier = float(np.mean((P - Y) ** 2))
    brier_base = pbar * (1 - pbar)
    c2 = brier < brier_base

    # (iii) ECE + 單調
    ece = _ece(P, Y)
    ece_ceiling = float(criteria["gate_rules"]["iii_calibration"]["ece_ceiling"])
    rho = _spearman_monotone(P, Y)
    c3 = ece <= ece_ceiling and rho is not None and rho > 0

    passed = bool(c1 and c2 and c3)
    review_cap = "review_tier_cap" in criteria
    snapshot = {
        "n_samples": len(data), "n_panels": len(by_panel),
        "base_rate_pbar": round(pbar, 4), "majority_base": round(base_major, 4),
        "alpha": alpha, "hac_lag": lag,
        "estimand_echo": criteria.get("estimand"),
        "i_hitrate": {"overall_hit": round(overall_hit, 4), "hac_eff_t": round(t, 3) if t else None,
                      "p_one_sided": round(p_one, 5) if p_one is not None else None, "pass": c1},
        "ii_brier": {"model": round(brier, 5), "base": round(brier_base, 5), "pass": c2},
        "iii_calibration": {"ece": round(ece, 4), "ece_ceiling": ece_ceiling,
                            "spearman_monotone": round(rho, 3) if rho is not None else None, "pass": c3},
        "verdict": "pass" if passed else "fail",
        "display_tier": ("review_observation_only" if (passed and review_cap)
                         else "full" if passed else "never_shown"),
    }
    new_status = "evaluated_pass" if passed else "evaluated_fail"
    cur.execute("UPDATE direction_gate SET status=%s, evaluated_at=now(), result_snapshot=%s, "
                "evaluation_ref=%s, git_sha=%s WHERE gate_id=%s",
                (new_status, json.dumps(snapshot, ensure_ascii=False),
                 f"evaluate_direction_gate.py@{_git7()}", _git7(), gate_id))
    mark = "✅PASS" if passed else "❌FAIL"
    tier = snapshot["display_tier"]
    print(f"  {mark} {gate_id}(h={h}) hit={overall_hit:.3f} vs base={base_major:.3f} "
          f"Efft={t if t is None else round(t,2)} p={p_one if p_one is None else round(p_one,4)} | "
          f"Brier {brier:.4f}<{brier_base:.4f}={c2} | ECE {ece:.3f}≤{ece_ceiling}&mono={rho if rho is None else round(rho,2)}={c3} → 展示層={tier}")
    return new_status


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT gate_id, track, horizon, status FROM direction_gate ORDER BY track, horizon")
        gates = cur.fetchall()
        cur.execute("SELECT horizon, count(*) FROM direction_oos_sample GROUP BY horizon")
        hoos = dict(cur.fetchall())
    print("GATE 現況與可判性:")
    for gid, tr, h, st in gates:
        avail = hoos.get(h, 0) if tr == "H" else 0
        judgeable = "✓可判" if st == "approved" and avail else ("已判" if st.startswith("evaluated") else "✗待訓練/核准")
        print(f"  {gid:<14} {tr} h={h:<4} {st:<16} OOS={avail:<6} {judgeable}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--evaluate")
    ap.add_argument("--evaluate-all", action="store_true", dest="all")
    args = ap.parse_args()
    if args.evaluate or args.all:
        _assert_clean_tree()                              # 判前斷言(revival §3.1)
        with db.connect() as conn:
            cur = conn.cursor()
            if args.all:
                cur.execute("SELECT gate_id FROM direction_gate WHERE status='approved' ORDER BY track, horizon")
                gids = [r[0] for r in cur.fetchall()]
            else:
                gids = [args.evaluate]
            for gid in gids:
                _evaluate_one(cur, gid)
                conn.commit()
            # 家族總表(機械輸出;criteria family_disclosure 句不可消失——revival §3.7)
            cur.execute("SELECT gate_id, status, coalesce(result_snapshot->>'verdict','—'), "
                        "coalesce(result_snapshot->>'display_tier','—') FROM direction_gate ORDER BY preregistered_at, gate_id")
            rows = cur.fetchall()
            print(f"\n═══ 家族總表(全 {len(rows)} 門一律全列;v1+v2 同一凍結資料)═══")
            for gid, st, vd, tier in rows:
                print(f"  {gid:<16} {st:<16} verdict={vd:<5} tier={tier}")
            cur.execute("SELECT criteria->>'family_disclosure' FROM direction_gate WHERE gate_id LIKE '%\\_v2' "
                        "AND criteria ? 'family_disclosure' LIMIT 1")
            fd = cur.fetchone()
            if fd and fd[0]:
                print(f"  [家族句] {fd[0]}")
        return 0
    return status()


if __name__ == "__main__":
    sys.exit(main())
