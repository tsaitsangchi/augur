#!/usr/bin/env python
"""arena 前置 admission GATE 裁判 — G1+G2 機械評估、原子單筆 verdict(計畫 §6.3;核心裁判)。

🎯 這支在做什麼(白話):對已凍結之 arena_admission_gate 跑 G1(資料地基,PIN 框架)+G2(anti-leakage
   迴歸)機械檢查,**原子 AND 收斂單筆** evaluated_pass|evaluated_fail(+result_snapshot 逐關證據;
   無 per-component 覆寫=不 cherry-pick)。守門鏈(可跑性,敗=exit 1 **不動 gate**):status=frozen →
   criteria_sha 覆算 → 繼承 sha 斷言(990ddea 等值) → 守門5 先凍後跑(approved_at < live 工件最早
   created_at;現 0 列=vacuous 過)。實質敗(G1/G2 紅)→寫 evaluated_fail=**終態**(trigger 鎖;複核=
   另立新 gate)。**--check=唯讀預演**(全檢查、印、不寫)——凍結後先 --check 再 --evaluate,不白燒。
   未落地依賴(score repro 工具/U5 queue)一律 **fail-closed 誠實紅**列 blocker(#8 不裝綠)。

守 #15(機械證據/fail-closed)· #12(檢查全引 criteria/呼既有工具,不複製常數)· #8(誠實紅)· #29a/d。
   SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md §6.3/§9。

執行指令矩陣:
  python scripts/evaluate_arena_admission.py                       # 無參數:矩陣+gate 清單(唯讀)
  python scripts/evaluate_arena_admission.py --check arena_adm_XXX # 唯讀預演(跑全檢查、不寫 status)
  python scripts/evaluate_arena_admission.py --evaluate arena_adm_XXX  # 正式:守門+檢查+原子單筆寫(終態!)
  python scripts/evaluate_arena_admission.py --selftest            # 判定邏輯純函式紅綠(零 DB 零 API)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

SCRIPTS = Path(__file__).resolve().parent
SOURCE_GATE = "unfreeze_06dcb178267d"


def _sha16(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()[:16]


# ── 守門鏈(可跑性;敗=不動 gate) ──────────────────────────────────────────────
def _guards(cur, gate_id):
    cur.execute("SELECT status, criteria, criteria_sha, approved_at FROM arena_admission_gate WHERE gate_id=%s",
                (gate_id,))
    row = cur.fetchone()
    if not row:
        return None, [f"✗ gate {gate_id} 不存在"]
    st, crit, sha, aa = row
    msgs = []
    if st != "frozen":
        msgs.append(f"✗ 守門1:status={st}≠frozen(draft 先 --freeze;終態不得再評)")
    if _sha16(crit) != sha:
        msgs.append("✗ 守門2:criteria_sha 覆算不符(挪門柱)")
    cur.execute("SELECT criteria FROM prediction_unfreeze_gate WHERE gate_id=%s", (SOURCE_GATE,))
    srow = cur.fetchone()
    if not srow:
        msgs.append(f"✗ 守門3:繼承來源 {SOURCE_GATE} 不存在")
    else:
        inh = crit.get("inherited", {})
        keys = ("g1_data", "g2_repro")
        if _sha16({k: inh.get(k) for k in keys}) != _sha16({k: srow[0].get(k) for k in keys}):
            msgs.append("✗ 守門3:繼承子塊 ≠ 990ddea 凍結原文(挪門柱)")
    cur.execute("SELECT min(created_at) FROM direction_arena_prediction")
    first_live = cur.fetchone()[0]
    if first_live is not None and aa is not None and aa >= first_live:
        msgs.append(f"✗ 守門5:approved_at {aa} ≥ 首筆 live 工件 {first_live}(先凍後跑時序破)")
    return (st, crit, first_live), msgs


# ── G1:資料地基(PIN 框架) ───────────────────────────────────────────────────
def _check_g1(conn, crit):
    snap, ok = {}, True
    pin = crit.get("g1_pin", {})
    snap["asof"] = pin.get("asof")
    snap["seg_le_0531"] = "governance_satisfied(凍結期快照認證;CLAUDE 資料期限條)"
    seg = pin.get("segments", {}).get("2026-06-01~2026-06-30", {})
    vm = seg.get("verification_mode", {})
    if isinstance(vm, dict) and vm.get("pending_decision"):
        ok = False
        snap["seg_jun"] = "✗ blocker:06 月段驗證方式未拍板(criteria pending_decision;fail-closed)"
    else:
        # 凍結時已具體化:vm={"mode":X,"evidence":{"driver_like":...,"audit_since":"2026-06-01"}}
        ev = (vm or {}).get("evidence", {}) if isinstance(vm, dict) else {}
        with db.transaction(conn) as cur:
            # run_at::date 須別名:cast 輸出欄名仍=run_at,會遮蔽 ORDER BY 使排序退化成按「日」
            # (同日兩列未定序→抓到舊 FAIL 列;2026-07-16 實證)
            cur.execute("SELECT passed, missing_in_db, exempt_n, sampled_n, coverage_gap_n, incomplete_n, "
                        "run_at::date AS run_date, driver FROM attestation_result "
                        "WHERE driver LIKE %s AND audit_since=%s ORDER BY run_at DESC LIMIT 1",
                        (ev.get("driver_like", "%"), ev.get("audit_since", "2026-06-01")))
            r = cur.fetchone()
        if not r:
            ok = False
            snap["seg_jun"] = f"✗ 無符合之 attestation_result(driver~{ev.get('driver_like')} since={ev.get('audit_since')})"
        else:
            p, mis, ex_n, samp_n, gap_n, inc_n, rd, drv = r
            ok = ok and bool(p)
            snap["seg_jun"] = {"passed": bool(p), "driver": drv, "run_date": str(rd),
                               "missing_in_db": int(mis or 0), "exempt_n": ex_n, "sampled_n": samp_n,
                               "coverage_gap_n": gap_n, "incomplete_n": inc_n,
                               "mis_note": "D-4:MIS 揭露非斷言 0;界定=豁免/端點/合法無資料"}
    with db.transaction(conn) as cur:   # evidence_ledger_gate(繼承 990ddea):validation_evidence 紅列=0
        cur.execute("SELECT count(*) FILTER (WHERE status='red'), count(*) FROM validation_evidence")
        red, tot = cur.fetchone()
    snap["evidence_ledger"] = {"red": red, "total": tot}
    if red:
        ok = False
        snap["evidence_ledger"]["note"] = "✗ 紅列在帳(須人裁除名或修復留痕)"
    snap["asof_charter"] = "governance_satisfied(07-12 解凍入憲 commit 7d337ec ≤ gate approved_at)"
    return ok, snap


# ── G2:anti-leakage 迴歸 ────────────────────────────────────────────────────
def _hash_verify(axis):
    """呼元件3 CLI(#29a 個別可執行之複用);rc=0=PASS。"""
    r = subprocess.run([sys.executable, str(SCRIPTS / "freeze_feature_panel_hash.py"),
                        "--verify", "--axis", axis], capture_output=True, text=True, cwd=str(SCRIPTS.parent))
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["(無輸出)"])[-1][:120]


def _check_g2(conn, crit):
    snap, ok = {}, True
    for axis in ("relative_strength", "direction"):
        a_ok, line = _hash_verify(axis)
        snap[f"panel_hash_{axis}"] = ("✓ " if a_ok else "✗ ") + line
        ok = ok and a_ok
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.score_repro_baseline')")
        if cur.fetchone()[0] is None:
            ok = False
            snap["score_repro"] = "✗ blocker:score_repro_baseline 未落地(verify_score_repro.py 未建;fail-closed)"
        else:
            r = subprocess.run([sys.executable, str(SCRIPTS / "verify_score_repro.py"), "--verify"],
                               capture_output=True, text=True, cwd=str(SCRIPTS.parent))
            s_ok = r.returncode == 0
            ok = ok and s_ok
            snap["score_repro"] = ("✓ " if s_ok else "✗ ") + (r.stdout.strip().splitlines() or ["(無輸出)"])[-1][:120]
        cur.execute("SELECT to_regclass('public.restatement_review_queue')")
        if cur.fetchone()[0] is None:
            ok = False
            snap["restatement_u5"] = "✗ blocker:restatement_review_queue 未落地(report_restatement_diff.py 未建;fail-closed)"
        else:
            cur.execute("SELECT count(*) FROM restatement_review_queue WHERE status='pending'")
            pend = cur.fetchone()[0]
            snap["restatement_u5"] = f"pending={pend}" + ("(✗ 未簽核)" if pend else "(✓ 無待裁)")
            ok = ok and pend == 0
    return ok, snap


def _decide(g1_ok, g2_ok):
    """原子 AND(純函式;無 per-component 覆寫)。"""
    return bool(g1_ok and g2_ok)


def _run_checks(conn, crit):
    g1_ok, g1 = _check_g1(conn, crit)
    g2_ok, g2 = _check_g2(conn, crit)
    return _decide(g1_ok, g2_ok), {"g1": {"ok": g1_ok, **g1}, "g2": {"ok": g2_ok, **g2}}


def check(gate_id):
    """唯讀預演:守門+全檢查、印結果、不寫 status(凍結後先跑此、確定再 --evaluate)。"""
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            g, msgs = _guards(cur, gate_id)
        for m in msgs:
            print(m)
        if g is None:
            return 1
        st, crit, _ = g
        if st != "frozen":
            print(f"(status={st};--check 續跑檢查供預覽,--evaluate 會被守門擋)")
        passed, snap = _run_checks(conn, crit)
        print(f"\n══ 預演結果(未寫 gate):{'✅ 會 PASS' if passed and not msgs else '❌ 會 FAIL'} ══")
        print(json.dumps(snap, ensure_ascii=False, indent=1, default=str))
        if msgs:
            print("(守門未過——--evaluate 將 exit 1 不動 gate)")
    return 0 if passed and not msgs else 1


def evaluate(gate_id):
    """正式評估:守門敗=exit 1 不動 gate;守門過→G1∧G2→**原子單筆終態**(trigger 鎖、複核=新 gate)。"""
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            g, msgs = _guards(cur, gate_id)
        for m in msgs:
            print(m)
        if g is None or msgs:
            print("守門未全過:evaluate 不可跑(gate 未動)")
            return 1
        _, crit, _ = g
        passed, snap = _run_checks(conn, crit)
        new_st = "evaluated_pass" if passed else "evaluated_fail"
        with db.transaction(conn) as cur:
            cur.execute("UPDATE arena_admission_gate SET status=%s, evaluated_at=now(), result_snapshot=%s, "
                        "evaluation_ref='evaluate_arena_admission.py' WHERE gate_id=%s",
                        (new_st, json.dumps(snap, ensure_ascii=False, default=str), gate_id))
        print(f"\n══ 正式判決:{'✅ evaluated_pass' if passed else '❌ evaluated_fail'}(終態、原子單筆;複核=另立新 gate)══")
        print(json.dumps(snap, ensure_ascii=False, indent=1, default=str))
    return 0 if passed else 1


def _selftest():
    """判定邏輯純函式紅綠(零 DB 零 API #29a)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("_decide 原子 AND:全綠=pass", _decide(True, True) is True)
    chk("_decide G1 紅→fail", _decide(False, True) is False)
    chk("_decide G2 紅→fail", _decide(True, False) is False)
    chk("_decide 雙紅→fail", _decide(False, False) is False)
    chk("_sha16 決定性(守門2/3 錨)", _sha16({"a": [1, 2]}) == _sha16({"a": [1, 2]}) and len(_sha16({})) == 16)
    # 守門/檢查函式存在且簽名可呼(結構鎖;IO-bound 不實跑)
    chk("公開入口齊", all(callable(f) for f in (_guards, _check_g1, _check_g2, check, evaluate)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", metavar="GATE_ID")
    ap.add_argument("--evaluate", metavar="GATE_ID")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.check:
        return check(args.check)
    if args.evaluate:
        return evaluate(args.evaluate)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.arena_admission_gate')")
        if cur.fetchone()[0]:
            cur.execute("SELECT gate_id, axis, status, approved_by FROM arena_admission_gate "
                        "ORDER BY preregistered_at DESC LIMIT 6")
            for r in cur.fetchall():
                print(f"  {r[0]} [{r[1]}] {r[2]} approved_by={r[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
