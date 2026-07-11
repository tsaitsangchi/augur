#!/usr/bin/env python
"""解凍 GATE 預註冊 CLI — 判準草案/凍結/查核/評估守門(驗證總綱 V2;§4.4)。

🎯 這支在做什麼(白話):把「FREEZE 解凍怎樣才算過」的五 gate 判準組成快照(DB 現值+U1-U6 建議值)
   → draft 入 prediction_unfreeze_gate → **人拍板 --freeze 才生效**(approved_by 留痕,AI 不代拍)。
   evaluate 守門斷言鏈(任一敗=exit 1):status=frozen → criteria_sha 覆算相符(挪門柱)→ judgestop
   快照=現值(判準分叉)→ new_asof>FREEZE 且 feature_values 實有>FREEZE panel(**FREEZE 生效中
   evaluate 必拒——本計畫內唯一可實測之主路徑,#7 不違 FREEZE**)→ 先凍後跑時序。fail 後再試=
   另立新 gate(舊列 superseded 留痕);放鬆判準須 note 人簽核理由。

守 #15(挪門柱 exit 1)· #12(judgestop/校準/econ 值引用 DB 不複製常數)· #10(superseded 審計軌)· #29a/d。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §4。

執行指令矩陣:
  python scripts/preregister_unfreeze_gate.py                    # 無參數:印矩陣+gate 清單(唯讀)
  python scripts/preregister_unfreeze_gate.py --preregister      # 組草案快照 → draft 列+U 拍板點清單
  python scripts/preregister_unfreeze_gate.py --freeze unfreeze_XXXX --approved-by hugo   # 人拍板凍結
  python scripts/preregister_unfreeze_gate.py --check unfreeze_XXXX     # 印快照+覆算 sha+trigger 斷言
  python scripts/preregister_unfreeze_gate.py --evaluate unfreeze_XXXX --asof 2026-09-30  # FREEZE 內必拒
  python scripts/preregister_unfreeze_gate.py --selftest         # trigger 白名單+守門純函式自測
"""
import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

FREEZE = "2026-05-31"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _criteria_sha(criteria):
    return hashlib.sha256(json.dumps(criteria, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()[:16]


def _criteria_draft(cur):
    """組草案:DB 現值快照(零 hardcode 已在 DB 之值)+U1-U6 建議值(標 proposal:true)。"""
    cur.execute("SELECT policy_key, threshold FROM judgestop_threshold WHERE frozen AND track IN ('A_annotate','B_decay')")
    js = {k: float(v) for k, v in cur.fetchall()}
    cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY horizon")
    econ = {str(h): v for h, v in cur.fetchall()}
    cur.execute("SELECT count(*) FROM revalidation_baseline")
    n_base = cur.fetchone()[0]
    cur.execute("SELECT DISTINCT ON (horizon) horizon, round(brier::numeric,4), round(ece::numeric,4) "
                "FROM probability_calibrator ORDER BY horizon, created_at DESC")
    cals = {f"H{h}": {"brier": float(b), "ece": float(e)} for h, b, e in cur.fetchall()}
    cur.execute("SELECT model_id FROM model_registry WHERE model_id LIKE 'RankRidge_H%%_2026-05-31_seed42_%%' ORDER BY model_id")
    models = [r[0] for r in cur.fetchall()]
    return {
        "scope": {"freeze_asof": FREEZE, "horizons": [20, 40, 60, 120],
                  "h82_excluded": "econ_verdict_rule 有 82 列但 HORIZONS 封閉集無 82,GATE 誠實不含",
                  "cells": ["ridge_H60_LO", "ridge_H120_LO"],
                  "universes": ["asof_incumbent", "pit_broad"], "model_ids": models},
        "baseline_refs": {"revalidation_baseline_rows": n_base, "calibrators": cals,
                          "econ_verdict_rule": econ},
        "judgestop_snapshot": js,
        "evidence_ledger_gate": "verify_validation_evidence.py --strict 全綠(已知債列須人裁除名或修復留痕)",
        "g1_data": {"reconcile": "in-scope 表 byte-level 對帳全綠至 as-of'(PHASE5 既有工具)",
                    "asof_charter": "as-of' 更新已入憲(commit 時間>approved_at)"},
        "g2_repro": {"feature_hash_stable": "panel<=FREEZE 之 feature_values 逐 panel hash 不變",
                     "score_repro_decimals": 5,
                     "U5_restatement": {"proposal": True, "rule": "源 restatement→diff 報告人裁(review),非自動 fail/pass"}},
        "g3_calibration": {"U1_window_periods": {"proposal": True, "value": 6,
                                                 "note": "≥6 非重疊期才可下確立級;4-5 期僅 review 中期讀數;H60 6 期≈1.4 年、H120≈2.9 年,不因等不及降門檻"},
                           "U2_brier_rule": {"proposal": True,
                                             "value": "live Brier-0.25:<=0 pass;(0,+0.005] review;>+0.005 fail"},
                           "U3_ece_ceiling": {"proposal": True, "value": 0.05}},
        "g4_econ_upgrade": {"rule": "thin→established 需同時 net_excess>0 且 HAC-t>=hac_t_floor 且 DSR>=dsr_annotate",
                            "U4_consecutive_rounds": {"proposal": True, "value": 2},
                            "U4b_add_deflated": {"proposal": True, "value": True,
                                                 "note": "加 deflated_ann>0 第四條件(同 frozen 列 deflated_floor_zero)"},
                            "h20_dead_no_shortcut": "H20 復活須重走 B 提拔三審,GATE 不提供捷徑"},
        "g5_rollback": {"atomic": "任一 gate fail→evaluated_fail,不部分採納;judgestop 軌B 照常",
                        "retry": "fail 後再試=另立新 gate(舊列 superseded 留痕)",
                        "U6_relax_policy": {"proposal": True,
                                            "value": "放鬆須 note 人簽核理由(留痕);替代=一律禁止(更嚴)"}},
    }


def preregister(note):
    with db.connect() as conn:
        cur = conn.cursor()
        crit = _criteria_draft(cur)
        gid = f"unfreeze_{uuid.uuid4().hex[:12]}"
        cur.execute("INSERT INTO prediction_unfreeze_gate (gate_id, criteria, criteria_sha, git_sha, note) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (gid, json.dumps(crit, ensure_ascii=False), _criteria_sha(crit), _git7(), note))
        conn.commit()
    print(f"✓ 預註冊 draft gate={gid}(sha={_criteria_sha(crit)})")
    print("── U 系列拍板點(人凍結才生效;--freeze 前可另立新 draft 改值)──")
    print("  U1 live 視窗=6 期(替代 4/8) | U2 Brier 分級 pass/review/fail(+0.005 線) | U3 ECE=0.05(替代 0.03)")
    print("  U4 連續 2 輪(替代 3)+U4b 加 deflated>0 第四條件 | U5 restatement=人裁 review | U6 放鬆須簽核留痕(替代一律禁)")
    print(f"  凍結指令:python scripts/preregister_unfreeze_gate.py --freeze {gid} --approved-by <你的名字>")
    return 0


def freeze(gate_id, approved_by):
    if not approved_by:
        sys.exit("✗ --freeze 需 --approved-by(判準值=決策層,人拍板留痕;AI 不代拍)")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, criteria FROM prediction_unfreeze_gate WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            sys.exit(f"✗ gate {gate_id} 不存在")
        if row[0] != "draft":
            sys.exit(f"✗ status={row[0]}≠draft 不得凍結")
        cur.execute("SELECT policy_key, threshold FROM judgestop_threshold WHERE frozen AND track IN ('A_annotate','B_decay')")
        live = {k: float(v) for k, v in cur.fetchall()}
        if row[1].get("judgestop_snapshot") != live:
            sys.exit(f"✗ judgestop 快照與現值不等(分叉):快照 {row[1].get('judgestop_snapshot')} vs 現值 {live}")
        cur.execute("UPDATE prediction_unfreeze_gate SET status='frozen', approved_by=%s, approved_at=now() "
                    "WHERE gate_id=%s", (approved_by, gate_id))
        conn.commit()
    print(f"✓ gate {gate_id} 已凍結(approved_by={approved_by})——此後 criteria 不可變(trigger 強制)")
    return 0


def check(gate_id):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT criteria, criteria_sha, status, approved_by, approved_at FROM prediction_unfreeze_gate "
                    "WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ gate {gate_id} 不存在"); return 1
        crit, sha, st, ab, aa = row
        resha = _criteria_sha(crit)
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='trg_unfreeze_no_goalpost'")
        trg = cur.fetchone()[0] > 0
        ok = (resha == sha) and trg
        print(f"gate {gate_id}: status={st} approved_by={ab}@{aa}")
        print(f"  sha 覆算 {resha} == 存列 {sha}: {'✓' if resha == sha else '✗ 挪門柱!'}")
        print(f"  trigger 存在: {'✓' if trg else '✗'}")
        print(f"  快照摘要: horizons={crit['scope']['horizons']} judgestop={crit['judgestop_snapshot']}")
    return 0 if ok else 1


def evaluate(gate_id, new_asof):
    """守門斷言鏈(§4.4;任一敗=exit 1)。FREEZE 生效中=主路徑必拒(本計畫內可實測)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT status, criteria, criteria_sha, approved_at FROM prediction_unfreeze_gate WHERE gate_id=%s",
                    (gate_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ gate {gate_id} 不存在"); return 1
        st, crit, sha, aa = row
        if st != "frozen":
            print(f"✗ 守門1:status={st}≠frozen(draft/superseded 不得評)"); return 1
        if _criteria_sha(crit) != sha:
            print("✗ 守門2:criteria_sha 覆算不符(挪門柱)"); return 1
        cur.execute("SELECT policy_key, threshold FROM judgestop_threshold WHERE frozen AND track IN ('A_annotate','B_decay')")
        if crit["judgestop_snapshot"] != {k: float(v) for k, v in cur.fetchall()}:
            print("✗ 守門3:judgestop 現值≠快照(判準分叉)"); return 1
        cur.execute("SELECT count(*) FROM feature_values WHERE panel_date > %s", (FREEZE,))
        if not (new_asof > FREEZE and cur.fetchone()[0] > 0):
            print(f"✗ 守門4:FREEZE 生效中(as-of {FREEZE} 凍結、無 >FREEZE panel)——evaluate 不可跑;"
                  "解凍=人決策入憲後接新資料才有此路"); return 1
        print("守門 1-4 過;守門5(先凍後跑時序)與 G1-G5 逐項機械評估=解凍後路徑(本計畫內不可達)")
    return 0


def selftest():
    """trigger 白名單+sha 覆算自測(adhoc draft 假列,FREEZE 內可跑、測畢即刪 draft 列合法)。"""
    fails = 0
    with db.connect() as conn:
        cur = conn.cursor()
        gid = f"unfreeze_selftest_{uuid.uuid4().hex[:8]}"
        crit = {"t": 1}
        cur.execute("INSERT INTO prediction_unfreeze_gate (gate_id, purpose, criteria, criteria_sha, git_sha) "
                    "VALUES (%s,'adhoc',%s,%s,'selftest')", (gid, json.dumps(crit), _criteria_sha(crit)))
        conn.commit()
        # (1) draft→evaluated_pass 非法(白名單)
        try:
            cur.execute("UPDATE prediction_unfreeze_gate SET status='evaluated_pass' WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest1:draft→evaluated_pass 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest1:draft→evaluated_pass 被 trigger 拒")
        # (2) 凍結(簽核)→改 criteria 非法
        cur.execute("UPDATE prediction_unfreeze_gate SET status='frozen', approved_by='selftest', approved_at=now() "
                    "WHERE gate_id=%s", (gid,))
        conn.commit()
        try:
            cur.execute("UPDATE prediction_unfreeze_gate SET criteria=%s WHERE gate_id=%s",
                        (json.dumps({"t": 2}), gid))
            conn.commit(); print("✗ selftest2:凍後改 criteria 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest2:凍後改 criteria 被 trigger 拒(挪門柱)")
        # (3) frozen→draft 兩步降級非法
        try:
            cur.execute("UPDATE prediction_unfreeze_gate SET status='draft' WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest3:frozen→draft 未被擋"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest3:frozen→draft 降級被 trigger 拒(F10)")
        # (4) 非 draft 不得刪 → superseded 廢止合法
        try:
            cur.execute("DELETE FROM prediction_unfreeze_gate WHERE gate_id=%s", (gid,))
            conn.commit(); print("✗ selftest4:frozen 列被刪"); fails += 1
        except Exception:
            conn.rollback(); print("✓ selftest4:非 draft 不得刪(留痕)")
        cur.execute("UPDATE prediction_unfreeze_gate SET status='superseded' WHERE gate_id=%s", (gid,))
        conn.commit()
        print(f"(selftest 假列 {gid} 已 superseded 留痕;adhoc 不礙正式 gate)")
    print(f"═> selftest {'全過 ✓' if fails == 0 else f'{fails} 敗 ✗'}")
    return 0 if fails == 0 else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--preregister", action="store_true")
    ap.add_argument("--note")
    ap.add_argument("--freeze", metavar="GATE_ID")
    ap.add_argument("--approved-by", dest="ab")
    ap.add_argument("--check", metavar="GATE_ID")
    ap.add_argument("--evaluate", metavar="GATE_ID")
    ap.add_argument("--asof")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.preregister:
        return preregister(args.note)
    if args.freeze:
        return freeze(args.freeze, args.ab)
    if args.check:
        return check(args.check)
    if args.evaluate:
        if not args.asof:
            sys.exit("--evaluate 需 --asof")
        return evaluate(args.evaluate, args.asof)
    if args.selftest:
        return selftest()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.prediction_unfreeze_gate')")
        if cur.fetchone()[0]:
            cur.execute("SELECT gate_id, purpose, status, approved_by FROM prediction_unfreeze_gate ORDER BY preregistered_at DESC LIMIT 6")
            for r in cur.fetchall():
                print(f"  {r[0]} [{r[1]}] {r[2]} approved_by={r[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
