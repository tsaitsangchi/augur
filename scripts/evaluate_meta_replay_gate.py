#!/usr/bin/env python
"""meta-replay 門機械裁判 — 程序增益三關(META-REPLAY-go §六,判準凍於 dgate_meta_replay_*)。

🎯 這支在做什麼(白話):讀 meta_replay_perf 之 (ic_next − ic_next_static) cutoff 序列(排除首
   cutoff=靜態自身),判三關:(i) HAC 單尾 p<0.05 增益>0 (ii) 程序集絕對水準 ≥ 靜態 90%
   (iii) prodset 逐期 Jaccard 異動率併報(揭露不判)。n<60=**不可判非 fail**;判=終態
   (evaluated_pass/fail 落 direction_gate,不可回改;換程序=新 proc_sha 新家族另評)。
   每次輸出首行印宣稱域章(§二三刀)。
守 #15(不可判誠實/判準 sha 核對)· #9/#10(全出帳本)· #29a/d。
SSOT=reports/augur_meta_replay_plan_20260729.md §六。

執行指令矩陣:
  python scripts/evaluate_meta_replay_gate.py                     # 無參數:可判性(唯讀)
  python scripts/evaluate_meta_replay_gate.py --evaluate dgate_meta_replay_B2_ridge --proc-sha <sha>
  python scripts/evaluate_meta_replay_gate.py --selftest          # 零 DB 紅綠(三關鎖)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

SCOPE_STAMP = ("【宣稱域】固定現行工具箱與判準之程序歷史逐期 OOS 增益(META-REPLAY 計畫 §二);"
               "工具箱含後見之明,禁『當年就會賺』解讀")


def gate_verdict(diffs, ic_proc, ic_static, min_clusters=60, alpha=0.05):
    """三關純函式。回 (verdict, detail)——verdict ∈ pass/fail/undecidable。"""
    from augur.evaluation import metrics
    n = len(diffs)
    if n < min_clusters:
        return ("undecidable", {"n": n, "why": f"n<{min_clusters}=不可判非 fail"})
    ser = {i: float(d) for i, d in enumerate(diffs)}
    t = metrics.effective_t_hac(ser)
    from scipy import stats
    p = float(1 - stats.norm.cdf(t)) if t is not None else None   # 單尾:增益>0
    g1 = p is not None and p < alpha and float(np.mean(diffs)) > 0
    mp, ms = float(np.mean(ic_proc)), float(np.mean(ic_static))
    g2 = mp >= 0.9 * ms if ms > 0 else mp >= ms
    return ("pass" if (g1 and g2) else "fail",
            {"n": n, "mean_diff": round(float(np.mean(diffs)), 5), "hac_t": t,
             "p_one_sided": (round(p, 5) if p is not None else None),
             "mean_ic_proc": round(mp, 5), "mean_ic_static": round(ms, 5),
             "i_gain": g1, "ii_floor": g2})


def jaccard_turnover(prodsets):
    """逐期 Jaccard 異動率(1−J);併報不判。純函式。"""
    out = []
    for a, b in zip(prodsets, prodsets[1:]):
        sa, sb = set(a), set(b)
        u = sa | sb
        out.append(1 - len(sa & sb) / len(u) if u else 0.0)
    return out


def evaluate(gate_id, proc_sha):
    print(SCOPE_STAMP)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT criteria, status FROM direction_gate WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ 門不存在:{gate_id}")
            return 1
        cr, st = row
        if st != "approved":
            print(f"✗ {gate_id} 現態 {st}——唯 approved 可判(終態不可回改)")
            return 1
        m = cr["estimand"]["model_id"]
        cur.execute("""SELECT cutoff_date, ic_next, ic_next_static FROM meta_replay_perf
            WHERE proc_sha=%s AND model=%s AND ic_next IS NOT NULL AND ic_next_static IS NOT NULL
            ORDER BY cutoff_date""", (proc_sha, m))
        rows = cur.fetchall()
        rows = rows[1:]                                   # 排除首 cutoff(靜態=自身,判準明文)
        diffs = [float(a) - float(b) for _, a, b in rows]
        icp = [float(a) for _, a, _ in rows]
        ics = [float(b) for _, _, b in rows]
        verdict, det = gate_verdict(diffs, icp, ics, cr["estimand"]["min_clusters"])
        cur.execute("""SELECT prodset FROM meta_replay_cutoff WHERE proc_sha=%s ORDER BY cutoff_date""",
                    (proc_sha,))
        to = jaccard_turnover([list(r[0]) for r in cur.fetchall()])
        det["iii_turnover_mean"] = round(float(np.mean(to)), 4) if to else None
        det["proc_sha"] = proc_sha
        print(f"{gate_id} @family {proc_sha}: {verdict}")
        print(json.dumps(det, ensure_ascii=False, indent=1))
        if verdict == "undecidable":
            print("(不可判——不落終態;湊滿 cutoff 再評)")
            return 0
        new_status = "evaluated_pass" if verdict == "pass" else "evaluated_fail"
        cur.execute("""UPDATE direction_gate SET status=%s, evaluated_at=now(), result_snapshot=%s
            WHERE gate_id=%s AND status='approved'""",
            (new_status, json.dumps(det, ensure_ascii=False), gate_id))
        conn.commit()
        print(f"→ {new_status}(終態落檔)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT gate_id, status FROM direction_gate WHERE track='M' ORDER BY 1""")
        for g, s in cur.fetchall():
            print(f"  {g:32} {s}")
        cur.execute("""SELECT proc_sha, model, count(*) FROM meta_replay_perf
            GROUP BY 1,2 ORDER BY 1,2""")
        for r in cur.fetchall():
            print(f"  perf: {r[0]} {r[1]} n={r[2]}(門檻 60+首期排除)")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    rng = np.random.default_rng(7)
    good = list(rng.normal(0.02, 0.01, 80))
    v, d = gate_verdict(good, list(rng.normal(0.1, 0.02, 80)), list(rng.normal(0.08, 0.02, 80)))
    chk("強增益 80 期=pass", v == "pass")
    v2, _ = gate_verdict(list(rng.normal(0.0, 0.01, 80)), [0.1] * 80, [0.1] * 80)
    chk("零增益=fail", v2 == "fail")
    v3, d3 = gate_verdict(good[:20], [0.1] * 20, [0.08] * 20)
    chk("n<60=不可判非 fail", v3 == "undecidable" and "不可判" in d3["why"])
    v4, _ = gate_verdict(good, list(rng.normal(0.05, 0.01, 80)), list(rng.normal(0.10, 0.01, 80)))
    chk("增益顯著但絕對水準<90% 靜態=fail(防贏在基準爛)", v4 == "fail")
    chk("Jaccard:全同=0/全換=1", jaccard_turnover([["a"], ["a"]]) == [0.0]
        and jaccard_turnover([["a"], ["b"]]) == [1.0])
    import inspect
    src = inspect.getsource(evaluate)
    chk("排除首 cutoff(靜態=自身)", "rows[1:]" in src)
    chk("undecidable 不落終態", "不落終態" in src)
    chk("宣稱域章首行", "SCOPE_STAMP" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="meta-replay 門裁判(三關;終態)")
    ap.add_argument("--evaluate")
    ap.add_argument("--proc-sha", dest="psha")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.evaluate and a.psha:
        return evaluate(a.evaluate, a.psha)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
