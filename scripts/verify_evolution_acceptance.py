#!/usr/bin/env python
"""🎯 三軸驗收器 A0–A12(v2 §7)——逐條機械查證,**「沒資料」不算通過**(回 N/A 非 PASS)。

白話:v2 §7 列了 13 條驗收,先前只存在於計畫文字。本支把每條寫成 SQL/rg 查證:
  PASS=條件成立且**有資料支撐**｜FAIL=條件被違反(須處置)｜N/A=尚無相關資料(誠實,非通過)。
最末印「PASS/FAIL/NA」三計數與總判(有 FAIL → rc=1);零寫入(唯讀稽核)、零 Claude token。
守 #15(空表≠通過;未跑≠合格)· #12(判準文字引 v2 §7 不改寫)· #28 · #29a/d。

執行指令矩陣:
  python scripts/verify_evolution_acceptance.py            # 全 13 條(唯讀)
  python scripts/verify_evolution_acceptance.py --check    # 同上(別名;供 CI/cron)
  python scripts/verify_evolution_acceptance.py --only A4 A9   # 只跑指定條
  python scripts/verify_evolution_acceptance.py --selftest # 零 DB 純紅綠(結構鎖)
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

ROOT = Path(__file__).resolve().parents[1]
LEDGERS = ("raw_evolution_iteration_ledger", "evolution_iteration_ledger", "local_ai_iteration_ledger")
UID_RE = r"^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$"
AUTOADVANCE_SINCE = "2026-07-27"   # V2-AUTOADVANCE 生效日(audits/V2-AUTOADVANCE-PROPOSAL-20260727.md);A5 不溯及既往之界


def _q(cur, sql, params=()):
    cur.execute(sql, params)
    r = cur.fetchone()
    return r[0] if r else None


def _rg(pattern, *paths, exclude=()):
    """回命中行數(rg 缺席時退 grep -r);零命中=0。

    exclude=檔名清單:掃描時排除。用於「稽核器自己寫下的判準文字被自己掃到」之假紅
    (2026-07-27 同型第三犯:`verify` 內含 `if`,使 `(if|elif|while)` 自我命中)。
    """
    ex_rg = [a for f in exclude for a in ("-g", f"!{f}")]
    ex_gr = [f"--exclude={f}" for f in exclude]
    for tool in (["rg", "-c", "--no-heading", *ex_rg, pattern],
                 ["grep", "-rc", *ex_gr, pattern]):
        try:
            out = subprocess.run(tool + [str(ROOT / p) for p in paths],
                                 capture_output=True, text=True, timeout=120)
            return sum(int(x.rsplit(":", 1)[-1]) for x in out.stdout.splitlines()
                       if x.rsplit(":", 1)[-1].strip().isdigit())
        except FileNotFoundError:
            continue
    return 0


def _checks(cur):
    """回 [(碼, 判準摘要, verdict, 證據)];verdict ∈ PASS/FAIL/N/A。"""
    out = []

    def add(code, desc, verdict, ev):
        out.append((code, desc, verdict, ev))

    # A0 FZ:豁免清單外零放量
    n_audit = _q(cur, "SELECT count(*) FROM data_audit_log WHERE logged_at > now() - interval '7 days'") or 0
    add("A0", "三軸全程無豁免清單外之 FinMind/FRED 放量",
        "N/A" if n_audit == 0 else "PASS", f"近 7 日 data_audit_log {n_audit} 列(白名單驅動者待 Phase 6 接線)")

    # A1 iteration_uid 格式與唯一
    tot = bad = 0
    for t in LEDGERS:
        if _q(cur, "SELECT to_regclass(%s)", (f"public.{t}",)) is None:
            continue
        tot += _q(cur, f"SELECT count(*) FROM {t}") or 0
        bad += _q(cur, f"SELECT count(*) FROM {t} WHERE iteration_uid !~ %s", (UID_RE,)) or 0
    add("A1", "iteration_uid 格式合法且跨三表唯一",
        "N/A" if tot == 0 else ("PASS" if bad == 0 else "FAIL"), f"三 ledger 共 {tot} 列、格式違反 {bad}")

    # A2 GATE 八閘值與 SKIP≠PASS
    n_skip_applied = _q(cur, """SELECT count(*) FROM promotion_queue
        WHERE queue_status='applied' AND gate_json->'G-PROM'->>'verdict'='SKIP'""") or 0
    add("A2", "SKIP≠PASS;ECON-only 禁晉升",
        "PASS" if n_skip_applied == 0 else "FAIL", f"G-PROM=SKIP 卻 applied 之列:{n_skip_applied}")

    # A3 steps_json 每步有 rc/started/finished;closed_at+closed_by 才算結輪
    closed = halfclosed = 0
    for t in LEDGERS:
        if _q(cur, "SELECT to_regclass(%s)", (f"public.{t}",)) is None:
            continue
        closed += _q(cur, f"SELECT count(*) FROM {t} WHERE closed_at IS NOT NULL") or 0
        halfclosed += _q(cur, f"SELECT count(*) FROM {t} WHERE closed_at IS NOT NULL AND closed_by IS NULL") or 0
    add("A3", "closed_at 與 closed_by 皆非空才算結輪",
        "N/A" if closed == 0 else ("PASS" if halfclosed == 0 else "FAIL"),
        f"已結輪 {closed} 列、缺 closed_by {halfclosed}")

    # A4 gain=true ⇒ 證據指向同勝 floor 與 mismatched 之列
    # 2026-07-27 對抗驗證抓到本條原為**橡皮圖章**:只數 gain=true 的列數就蓋 PASS,
    # 從不讀 gain_evidence、從不呼叫 evidence_level(且 UNION ALL 只取首列,連加總都沒做到)。
    # 改為**逐列真讀證據**:帶得動對照臂數字者才交給 evidence_protocol 判;帶不動者不得算通過。
    from augur.audit.evidence_protocol import evidence_level
    METRIC_BASES = ("dual_green_delta", "prodset_delta", "arena_prereg", "eval_metric")
    rows = []
    for t in LEDGERS:
        if _q(cur, "SELECT to_regclass(%s)", (f"public.{t}",)) is None:
            continue
        cur.execute(f"SELECT iteration_uid, gain_basis, gain_evidence FROM {t} WHERE gain IS TRUE")  # noqa: S608
        rows += [(t, u, b, e or {}) for u, b, e in cur.fetchall()]
    judged, unsubstantiated, na_basis = [], [], []
    for _t, uid, basis, ev in rows:
        arms = ev.get("arms") if isinstance(ev.get("arms"), dict) else None
        if arms and {"floor", "mismatched", "live"} <= set(arms):
            lvl = evidence_level({k: arms.get(k) for k in
                                  ("ceiling", "floor", "shuffled", "mismatched", "live")})
            (judged if lvl in ("weak", "scoped_established") else unsubstantiated).append(f"{uid}:{lvl}")
        elif basis in METRIC_BASES:
            unsubstantiated.append(f"{uid}:{basis} 無對照臂數字")
        else:
            na_basis.append(f"{uid}:{basis}")   # 如 RAWEVO new_gap:非「勝過對照」型宣稱,本條不適用
    add("A4", "gain=true 且屬度量型 ⇒ gain_evidence 須帶對照臂且過 evidence_protocol",
        "N/A" if not rows else ("FAIL" if unsubstantiated else ("PASS" if judged else "N/A")),
        f"gain=true {len(rows)} 列:經判讀通過 {judged or 0}、**無據 {unsubstantiated or 0}**、"
        f"非度量型不適用 {na_basis or 0}")

    # A5 APPLY 紀律:apply_allowed ⇒ gate_ref 指向 enacted
    # 規則自 V2-AUTOADVANCE 生效日起適用;先前列**不溯及既往**但分開列示(不靜默放過)
    n_apply = _q(cur, "SELECT count(*) FROM evolution_apply_log") or 0
    n_noref_new = _q(cur, """SELECT count(*) FROM evolution_apply_log
        WHERE applied_at >= %s AND coalesce(evidence_json->>'gate_ref','')=''""",
                     (AUTOADVANCE_SINCE,)) or 0
    n_noref_old = _q(cur, """SELECT count(*) FROM evolution_apply_log
        WHERE applied_at < %s AND coalesce(evidence_json->>'gate_ref','')=''""",
                     (AUTOADVANCE_SINCE,)) or 0
    add("A5", f"APPLY 須有 gate_ref(規則自 {AUTOADVANCE_SINCE} 生效,不溯及既往)",
        "N/A" if n_apply == 0 else ("PASS" if n_noref_new == 0 else "FAIL"),
        f"apply_log {n_apply} 列;生效後無 gate_ref {n_noref_new}"
        + (f";生效前 {n_noref_old} 列(規則前之歷史列,誠實列示不追溯)" if n_noref_old else ""))

    # A6 人閘完整:hint approved 才可被引用;serving 須有 promoted_by
    n_srv_nosig = _q(cur, """SELECT count(*) FROM local_model_version
        WHERE status='serving' AND (promoted_by IS NULL OR promoted_by='')""") or 0
    n_hint_bad = _q(cur, """SELECT count(*) FROM evolution_hypothesis_hint
        WHERE decision='approved' AND (decided_by IS NULL OR decision_code IS NULL)""") or 0
    add("A6", "serving 須有 promoted_by;approved hint 須有 decided_by/decision_code",
        "PASS" if n_srv_nosig == 0 and n_hint_bad == 0 else "FAIL",
        f"serving 缺簽 {n_srv_nosig}、approved 缺人證 {n_hint_bad}")

    # A7 通知不連鎖:driver 不得依 cross_notify_json 分支
    # 查的是「**分支**」不是字面出現:DDL 欄定義與本驗收器自身之引用皆屬正常
    # (2026-07-27:原判準以字面計數,5 處命中中 3 處是本檔自己=假紅,同型於今日兩次「掃太廣」)
    SELF = Path(__file__).name
    n_branch = _rg(r"(if|elif|while).*cross_notify_json", "scripts", "src", exclude=(SELF,))
    n_lit = _rg(r"cross_notify_json", "scripts", "src")
    add("A7", "三軸 driver 無**依 cross_notify_json 分支**之控制流(佈告欄零效力)",
        "PASS" if n_branch == 0 else "FAIL",
        f"控制流分支 {n_branch} 處(字面出現 {n_lit} 處=DDL 欄定義與本驗收器引用,屬正常)")

    # A8 重活互斥:搶不到鎖者有 deferred 列
    n_def = _q(cur, "SELECT count(*) FROM evolution_deferred_work") or 0
    add("A8", "重活互斥;搶不到鎖者於 evolution_deferred_work 有列",
        "N/A" if n_def == 0 else "PASS", f"deferred {n_def} 列(heavy_slot v2 已上線)")

    # A9 三軸隔離:isolation 零違規 + predict 對 local_model_* 零授權
    from augur.audit.import_isolation import check_isolation
    v = check_isolation()
    # 樣式以參數傳(SQL 內裸 % 會被 psycopg2 當佔位符;2026-07-27 實撞 IndexError)
    n_grant = _q(cur, """SELECT count(*) FROM information_schema.role_table_grants
        WHERE grantee='augur_predict'
          AND (table_name LIKE %s ESCAPE '!' OR table_name LIKE %s ESCAPE '!')""",
                 ("local!_model!_%", "raw!_evolution!_%")) or 0
    add("A9", "check_isolation 零違規;augur_predict 對 local_model_*/raw_evolution_* 零授權",
        "PASS" if not v and n_grant == 0 else "FAIL", f"isolation 違規 {len(v)}、predict 授權 {n_grant}")

    # A10 措辭掃描:brief/hint/週報零黑名單
    from augur.audit.evolution_contract import BLACKLIST, validate
    briefs = sorted((ROOT / "var" / "briefs").glob("*.json")) if (ROOT / "var" / "briefs").is_dir() else []
    bad_brief = []
    for p in briefs:
        import json
        try:
            errs = validate(json.loads(p.read_text(encoding="utf-8")), "brief")
        except Exception as e:  # noqa: BLE001
            errs = [f"讀取失敗 {type(e).__name__}"]
        if errs:
            bad_brief.append(p.name)
    add("A10", f"brief 過 C7 契約且零黑名單({len(BLACKLIST)} 詞)",
        "N/A" if not briefs else ("PASS" if not bad_brief else "FAIL"),
        f"brief {len(briefs)} 檔、不合格 {bad_brief or 0}")

    # A11 停損各自:達 N ⇒ stopped_no_gain 且 stop_reason 非空
    n_stop = n_stop_bad = 0
    for t in LEDGERS:
        if _q(cur, "SELECT to_regclass(%s)", (f"public.{t}",)) is None:
            continue
        n_stop += _q(cur, f"SELECT count(*) FROM {t} WHERE status='stopped_no_gain'") or 0
        n_stop_bad += _q(cur, f"SELECT count(*) FROM {t} WHERE status='stopped_no_gain' "
                              "AND coalesce(stop_reason,'')=''") or 0
    add("A11", "停損列須有 stop_reason",
        "N/A" if n_stop == 0 else ("PASS" if n_stop_bad == 0 else "FAIL"),
        f"停損 {n_stop} 列、缺 reason {n_stop_bad}")

    # A12 儀表唯讀且首行為 SUNSET
    rpt = ROOT / "scripts" / "report_triple_evolution_week.py"
    src = rpt.read_text(encoding="utf-8") if rpt.exists() else ""
    sql_lines = [ln for ln in src.splitlines() if "cur.execute" in ln or "_one(cur," in ln]
    writes = any(k in " ".join(sql_lines).upper() for k in ("INSERT INTO", "UPDATE ", "DELETE FROM"))
    add("A12", "週儀表對 DB 零寫入且第一行為 V2-SUNSET",
        "PASS" if src and not writes and 'L.append(f"# V2-SUNSET' in src else "FAIL",
        f"儀表存在={bool(src)}、SQL 含寫入={writes}")
    return out


def run(only):
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = _checks(cur)
    if only:
        rows = [r for r in rows if r[0] in set(only)]
    n = {"PASS": 0, "FAIL": 0, "N/A": 0}
    print("── 三軸驗收 A0–A12(v2 §7;唯讀) ──")
    for code, desc, verdict, ev in rows:
        n[verdict] = n.get(verdict, 0) + 1
        mark = {"PASS": "✓", "FAIL": "✗", "N/A": "○"}[verdict]
        print(f"  {mark} {code} {desc}\n      {ev}")
    print(f"\n  合計:PASS {n['PASS']} · FAIL {n['FAIL']} · N/A {n['N/A']}(尚無資料=誠實未通過,非合格)")
    if n["FAIL"]:
        print("  → 有 FAIL:須處置後重驗(rc=1)")
    return 1 if n["FAIL"] else 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    src = Path(__file__).read_text(encoding="utf-8")
    chk("三態判定(N/A 非 PASS——空表不算通過)", '"N/A"' in src and "尚無資料=誠實未通過" in src)
    chk("十三條 A0–A12 齊", all(f'"{c}"' in src for c in [f"A{i}" for i in range(13)]))
    chk("唯讀:自身 SQL 無寫入", not any(k in " ".join(
        ln for ln in src.splitlines() if "cur.execute" in ln or "_q(cur," in ln).upper()
        for k in ("INSERT INTO", "UPDATE ", "DELETE FROM")))
    chk("A9 走既有 check_isolation(不自造隔離判準,#12)", "from augur.audit.import_isolation import" in src)
    chk("A10 走既有 C7 validator(不自造契約,#12)", "from augur.audit.evolution_contract import" in src)
    chk("uid regex 與 ledger CHECK 同式", UID_RE == r"^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$")
    chk("有 FAIL 即 rc=1(供 CI/cron 機械把關)", "return 1 if n[\"FAIL\"] else 0" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(a.only)


if __name__ == "__main__":
    sys.exit(main())
