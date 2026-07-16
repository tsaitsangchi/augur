#!/usr/bin/env python
"""arena 前置 admission GATE 預註冊 CLI — 組判準/凍結/查核(arena 前置 G1-G5 計畫 §6.2)。

🎯 這支在做什麼(白話):把「方向 arena 開賽前置(G1 資料+G2 anti-leakage)怎樣才算過」組成判準快照
   → draft 入 arena_admission_gate → **人拍板 --freeze 才生效**(approved_by 留痕,AI 不代拍)。
   繼承紀律:G1/G2 子判準**逐鍵複製**自已退史料之 unfreeze gate 990ddea 凍結原文(該列 criteria
   有 trigger 鎖=讀現值即凍結原文),freeze/check 時 **sha 等值斷言**——機械證明「機制置換未挪門柱」。
   G1 依 G1-PIN(hugo 2026-07-16):as-of 釘 2026-06-30、不滾動追;06 月段驗證方式誠實標待拍板。

守 #15(挪門柱=sha 斷言 exit 1)· #12(判準值引用不複製常數;繼承=複製+sha 錨屬例外、為斷言而複製)
   · #10(supersedes 雙向鏈留痕)· #29a/d。SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md。

執行指令矩陣:
  python scripts/preregister_arena_admission_gate.py                 # 無參數:印矩陣+gate 清單(唯讀)
  python scripts/preregister_arena_admission_gate.py --preregister   # 組草案(繼承 990ddea)→draft
  python scripts/preregister_arena_admission_gate.py --freeze arena_adm_XXXX --approved-by hugo  # 人拍板凍結
  python scripts/preregister_arena_admission_gate.py --check arena_adm_XXXX   # 覆算 sha+繼承斷言+trigger
  python scripts/preregister_arena_admission_gate.py --backfill-supersedes arena_adm_XXXX  # 990ddea 後繼回填
  python scripts/preregister_arena_admission_gate.py --selftest      # 繼承 sha 斷言純函式紅綠(零 DB)
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

SOURCE_GATE = "unfreeze_06dcb178267d"     # 已退史料之 unfreeze gate(criteria trigger 鎖=凍結原文)
SOURCE_SHA = "990ddea219ad24e0"           # 其 criteria_sha(全塊);繼承子塊另算子 sha
PIN_ASOF = "2026-06-30"                   # G1-PIN(hugo 2026-07-16):arena 資料地基固定 as-of
INHERIT_KEYS = ("g1_data", "g2_repro")    # 逐鍵複製之子判準塊


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _sha16(obj):
    """與 preregister_unfreeze_gate._criteria_sha 同口徑(sha256/sort_keys/16hex)——跨 gate 可比。"""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()[:16]


def _inherited_block(source_criteria):
    """自 990ddea 凍結原文逐鍵複製 G1/G2 子塊+子塊 sha 錨。純函式(selftest 可測)。"""
    sub = {k: source_criteria[k] for k in INHERIT_KEYS}
    return {**sub, "source_gate": SOURCE_GATE, "source_criteria_sha": SOURCE_SHA,
            "anchor_sha": _sha16(sub)}


def _verify_inheritance(criteria, source_criteria):
    """雙斷言:①新 gate inherited 子塊 sha==anchor(內部一致);②==990ddea 對應子塊現值 sha(繼承等值)。
    回 (ok, 覆算sha, anchor, 來源sha)。純函式(selftest 可測)。"""
    inh = criteria.get("inherited", {})
    sub = {k: inh.get(k) for k in INHERIT_KEYS}
    re_sha = _sha16(sub)
    src_sha = _sha16({k: source_criteria[k] for k in INHERIT_KEYS})
    return (re_sha == inh.get("anchor_sha") == src_sha), re_sha, inh.get("anchor_sha"), src_sha


def _build_criteria(cur):
    """組 arena 前置(shared_foundation 軸)判準:繼承塊+G1-PIN+G2 機制+G5 治理;決策引計畫書決策紀錄。"""
    cur.execute("SELECT criteria, criteria_sha, status FROM prediction_unfreeze_gate WHERE gate_id=%s",
                (SOURCE_GATE,))
    row = cur.fetchone()
    if not row:
        sys.exit(f"✗ 來源 gate {SOURCE_GATE} 不存在(繼承鏈斷)")
    src, src_sha, src_status = row
    if src_sha != SOURCE_SHA:
        sys.exit(f"✗ 來源 criteria_sha {src_sha} ≠ 預期 {SOURCE_SHA}(來源被改?trigger 應擋、須人查)")
    return {
        "axis": "shared_foundation",
        "scope_note": "方向 arena 開賽硬前置=G1+G2(D-2 Reading A:確立升格走方向軸門二 evaluate_direction_gate、"
                      "≥60 clusters;相對強度 G3/G4 歸相對強度部署、不 gate 方向 arena);開賽即 review_observation_only tier",
        "inherited": _inherited_block(src),
        "g1_pin": {
            "asof": PIN_ASOF,
            "no_rolling": True,
            "rationale": "hugo 2026-07-16:『資料就定在 2026-06-30、不要再去追資料完整』——live byte 對帳=移動標靶,"
                         "滾動綠明天即過期;固定 as-of=固定標靶可永久綠,且與 feature_values 凍結後 panel(06-30)對齊",
            "segments": {
                "<=2026-05-31": "凍結期快照認證(既有、定案不變;CLAUDE 資料期限條)",
                "2026-06-01~2026-06-30": {"required": "一次對帳到綠→凍 G1 參照,之後不滾動追",
                                          "verification_mode": {
                                              "mode": "sampled_disclosed",
                                              "decided_by": "hugo 2026-07-16(聊天拍板:「06 月段用抽樣」)",
                                              "evidence": {"driver_like": "daily_maintenance%",
                                                           "audit_since": "2026-06-01"},
                                              "disclosure": "roster 表抽 40 股/表(sampled_n 揭露)+by-date 全量+heal;"
                                                            "固定窗跑一次永久有效、非滾動追"}},
            },
            "mis_disclosure": "D-4:result_snapshot 明列真實 MIS 及性質(非抽樣吸收),驗收 SQL 註明界定",
        },
        "g2": {
            "feature_panel_hash": {"baseline_table": "feature_panel_hash_baseline",
                                   "normalization": "D-6:復用 reconcile._norm 口徑+定點舍入+確定性排序"
                                                    "(panel_date,id,feature)+NULL sentinel;normalization_ref 版本化",
                                   "frozen_as_of": PIN_ASOF, "pass_rule": "全 panel value_hash+row_count==baseline,0 mismatch"},
            "direction_leakage": {"decision": "D-1 補做", "table": "daily_direction_feature_values",
                                  "first_step": "查 build_daily_direction_features.py as-of 紀律;有 lookahead=真 bug 須修",
                                  "pass_rule": "方向軸 hash baseline 就位且驗證 0 mismatch"},
            "score_repro_decimals": 5,
            "restatement": "U5:diff 報告人裁(review),非自動 fail/pass;restatement_review_queue 無 pending 或已簽核",
        },
        "g5": {"atomic": "G1∧G2 AND 收斂單筆 evaluated_pass/fail,無 per-component 覆寫",
               "retry": "fail 後另立新 gate,supersedes_gate_id 鏈留痕",
               "relaxation": "D-11:白名單枚舉放鬆方向(floor↓/ceiling↑/count↓/alpha↑)+未列鍵 fail-closed 要求簽核"},
        "enforcement": {"chokepoints": ["run_arena_daily_pipeline._gate_approved", "run_arena_round.live_round"],
                        "rule": "arena_admission_gate evaluated_pass(axis=shared_foundation) AND 既有 dgate_arena% approved"},
        "decision_record": "reports/arena_g1g5_admission_gate_plan_20260716.md 決策紀錄(D-1~D-6,D-11+G1-PIN)",
    }


def preregister(note, supersedes=None):
    with db.connect() as conn:
        cur = conn.cursor()
        crit = _build_criteria(cur)
        gid = f"arena_adm_{uuid.uuid4().hex[:12]}"
        cur.execute("INSERT INTO arena_admission_gate (gate_id, axis, purpose, criteria, criteria_sha, git_sha, "
                    "supersedes_gate_id, note) VALUES (%s,%s,'arena_open_precondition',%s,%s,%s,%s,%s)",
                    (gid, crit["axis"], json.dumps(crit, ensure_ascii=False), _sha16(crit), _git7(),
                     supersedes, note))
        if supersedes:      # 舊 draft 廢止留痕(draft→superseded 合法;非 draft 由 trigger 白名單裁)
            cur.execute("UPDATE arena_admission_gate SET status='superseded' WHERE gate_id=%s AND status='draft'",
                        (supersedes,))
        conn.commit()
    print(f"✓ 預註冊 draft gate={gid}(sha={_sha16(crit)};繼承 {SOURCE_GATE}/{SOURCE_SHA}"
          + (f";supersedes {supersedes}" if supersedes else "") + ")")
    print(f"  凍結指令:python scripts/preregister_arena_admission_gate.py --freeze {gid} --approved-by <你的名字>")
    return 0


def freeze(gate_id, approved_by):
    if not approved_by:
        sys.exit("✗ --freeze 需 --approved-by(判準值=決策層,人拍板留痕;AI 不代拍)")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, criteria FROM arena_admission_gate WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            sys.exit(f"✗ gate {gate_id} 不存在")
        if row[0] != "draft":
            sys.exit(f"✗ status={row[0]}≠draft 不得凍結")
        cur.execute("SELECT criteria FROM prediction_unfreeze_gate WHERE gate_id=%s", (SOURCE_GATE,))
        src = cur.fetchone()[0]
        ok, re_sha, anchor, src_sha = _verify_inheritance(row[1], src)
        if not ok:
            sys.exit(f"✗ 繼承斷言敗(挪門柱?):覆算 {re_sha} anchor {anchor} 來源 {src_sha}——不得凍結")
        cur.execute("UPDATE arena_admission_gate SET status='frozen', approved_by=%s, approved_at=now() "
                    "WHERE gate_id=%s", (approved_by, gate_id))
        conn.commit()
    print(f"✓ gate {gate_id} 已凍結(approved_by={approved_by};繼承斷言過)——criteria 不可變(trigger 強制)")
    return 0


def check(gate_id):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT criteria, criteria_sha, status, approved_by, approved_at FROM arena_admission_gate "
                    "WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ gate {gate_id} 不存在"); return 1
        crit, sha, st, ab, aa = row
        resha = _sha16(crit)
        cur.execute("SELECT criteria FROM prediction_unfreeze_gate WHERE gate_id=%s", (SOURCE_GATE,))
        src = cur.fetchone()[0]
        inh_ok, re_sha, anchor, src_sha = _verify_inheritance(crit, src)
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='trg_arena_admission_no_goalpost'")
        trg = cur.fetchone()[0] > 0
        ok = (resha == sha) and inh_ok and trg
        print(f"gate {gate_id}: status={st} approved_by={ab}@{aa}")
        print(f"  sha 覆算 {resha} == 存列 {sha}: {'✓' if resha == sha else '✗ 挪門柱!'}")
        print(f"  繼承斷言(覆算==anchor==990ddea 現值): {'✓' if inh_ok else f'✗({re_sha}/{anchor}/{src_sha})'}")
        print(f"  trigger 存在: {'✓' if trg else '✗'}")
        print(f"  g1_pin asof={crit['g1_pin']['asof']} 06月段驗證={crit['g1_pin']['segments']['2026-06-01~2026-06-30']['verification_mode']}")
    return 0 if ok else 1


def backfill_supersedes(gate_id):
    """990ddea 後繼回填(雙向鏈):前驅已在新 gate criteria.inherited;後繼記舊列 evaluation_ref
    (evaluation_ref 不在 trigger 鎖鍵、可補;status 不動=史料不擾)。"""
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM arena_admission_gate WHERE gate_id=%s", (gate_id,))
        if not cur.fetchone():
            sys.exit(f"✗ 新 gate {gate_id} 不存在,不得回填")
        ref = f"superseded_by: arena_admission_gate/{gate_id}"
        cur.execute("UPDATE prediction_unfreeze_gate SET evaluation_ref=%s WHERE gate_id=%s", (ref, SOURCE_GATE))
        conn.commit()
    print(f"✓ {SOURCE_GATE}.evaluation_ref ← {ref}(雙向鏈完成;status/criteria 未動)")
    return 0


def _selftest():
    """繼承 sha 斷言純函式紅綠(零 DB/零 API #29a)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    src = {"g1_data": {"reconcile": "x"}, "g2_repro": {"hash": "y"}, "other": 1}
    inh = _inherited_block(src)
    chk("_inherited_block 只複製 INHERIT_KEYS", set(INHERIT_KEYS) < set(inh) and "other" not in inh)
    chk("_inherited_block 帶 anchor/source", inh["anchor_sha"] == _sha16({k: src[k] for k in INHERIT_KEYS})
        and inh["source_gate"] == SOURCE_GATE)
    crit = {"inherited": inh}
    okv, r, a, s = _verify_inheritance(crit, src)
    chk("繼承等值→斷言過", okv and r == a == s)
    tam = {"inherited": {**inh, "g1_data": {"reconcile": "TAMPERED"}}}
    chk("改繼承子塊→斷言敗(挪門柱偵測)", _verify_inheritance(tam, src)[0] is False)
    src2 = {**src, "g1_data": {"reconcile": "DRIFTED"}}
    chk("來源漂移→斷言敗", _verify_inheritance(crit, src2)[0] is False)
    chk("_sha16 決定性+16hex", _sha16({"a": 1}) == _sha16({"a": 1}) and len(_sha16({})) == 16)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--preregister", action="store_true")
    ap.add_argument("--note")
    ap.add_argument("--supersedes", metavar="OLD_GATE_ID")
    ap.add_argument("--freeze", metavar="GATE_ID")
    ap.add_argument("--approved-by", dest="ab")
    ap.add_argument("--check", metavar="GATE_ID")
    ap.add_argument("--backfill-supersedes", dest="bfs", metavar="GATE_ID")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.preregister:
        return preregister(args.note, supersedes=args.supersedes)
    if args.freeze:
        return freeze(args.freeze, args.ab)
    if args.check:
        return check(args.check)
    if args.bfs:
        return backfill_supersedes(args.bfs)
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
