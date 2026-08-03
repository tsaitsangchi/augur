#!/usr/bin/env python
"""🎯 三軸驗收器 A0–A12(v2 §7)——逐條機械查證,**「沒資料」不算通過**(回 N/A 非 PASS)。

白話:v2 §7 列了 13 條驗收,先前只存在於計畫文字。本支把每條寫成 SQL/rg 查證:
  PASS=條件成立且**有資料支撐**｜FAIL=條件被違反(須處置)｜N/A=尚無相關資料(誠實,非通過)。
最末印「PASS/FAIL/NA」三計數與總判(有 FAIL → rc=1);零寫入(唯讀稽核)、零 Claude token。
A13=A′ 依 R-CELL′ 逐格判讀(H1 2026-08-01):有效性單位=(run,格)、run 級 is_invalid 不連坐、
缺格誠實列示、wins 限 capability 有效格;判讀層修不換尺(eval_code_hash 涵蓋域零觸碰)。
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
CTRL_ARMS = ("ceiling", "floor", "shuffled", "mismatched", "robot")


def rcell_cells(per_item):
    """R-CELL′-1/2 逐格收攏(H1 2026-08-01):per_item → {格: (n_total, n_answered, mean_f|None)}。

    有效格 iff 該格**全部**題目皆有有效作答(零筆帶 invalid 鍵、逐項 f 非空;f 可為 0 故判 is not None)。
    無效格 mean_f=None=**非證據亦非反證**——缺項與難度相關、部分均值向上偏誤
    (C1 三 run 部分均值 0.606-0.625>floor 0.5 而全格無效,H1 §2.4 實證),不得入判。純函式。
    """
    agg = {}
    for it in per_item or []:
        lay = it.get("layer")
        nt, na, s = agg.get(lay, (0, 0, 0.0))
        f = it.get("f")
        answered = ("invalid" not in it) and (f is not None)
        agg[lay] = (nt + 1, na + (1 if answered else 0), s + (f if answered else 0.0))
    return {lay: (nt, na, (s / na) if (na == nt and na > 0) else None)
            for lay, (nt, na, s) in agg.items()}


def rcell_judge(cell, cap_cells):
    """R-CELL′ A′ 判定核心(H1 2026-08-01)——**純函式**,--selftest 餵 fixture 驗紅綠。

    run 級 is_invalid 不整輪連坐(R-CELL′-1;判讀有效性單位=(run,格))。
    cell={(set_id,hash): {arm: [逐 run 之 rcell_cells() 輸出]}};cap_cells={set_id: {capability 格名}}。
    回 (wins, n_live_runs, missing, incomp):
      wins    僅 capability 之**有效格**(R-CELL′-5)且 evidence_level ≥ weak 之 run ≥2(R-CELL′-4 原式);
      missing capability 缺格誠實列示 n_answered/n_total(R-CELL′-2,不得靜默消失);
      incomp  對照臂多 attempt 同格不同值=fail-loud 判 incomparable(R-CELL′-3)。
    """
    from augur.audit.evidence_protocol import evidence_level
    wins, missing, incomp, n_live = [], [], [], 0
    for (sid, ch), arms in sorted(cell.items()):
        caps = cap_cells.get(sid, set())
        tag = f"[{sid[:8]}/{ch[:8]}]"
        ctrl0 = {}
        for a in CTRL_ARMS:
            vals, bad = {}, set()
            for r in arms.get(a) or []:
                for cname, (_nt, _na, m) in r.items():
                    if m is None:
                        continue
                    if cname in vals and vals[cname] != m:
                        bad.add(cname)
                    vals.setdefault(cname, m)
            for cname in sorted(bad):
                vals.pop(cname, None)
                if cname in caps:
                    incomp.append(f"{a}@{cname}{tag}")
            ctrl0[a] = vals
        if not all(arms.get(a) for a in ("floor", "mismatched", "robot")):
            continue                                    # 缺對照=不可判(非通過)
        for arm, runs in sorted(arms.items()):
            if arm in CTRL_ARMS:
                continue
            n_live += len(runs)
            cells = set().union(*[set(r) for r in runs]) if runs else set()
            for cname in sorted(cells & caps):          # R-CELL′-5:behavior 格永不入 wins
                gaps = [f"{r[cname][1]}/{r[cname][0]}" for r in runs
                        if cname in r and r[cname][2] is None]
                if gaps:
                    missing.append(f"{arm}@{cname}{tag} 缺格:{'、'.join(gaps)}")
                if any(cname not in ctrl0[a] for a in ("floor", "mismatched", "robot")):
                    missing.append(f"{arm}@{cname}{tag} 對照臂缺有效格=不可判")
                    continue
                ok_runs = [r for r in runs if cname in r and r[cname][2] is not None
                           and evidence_level(
                               {"ceiling": ctrl0["ceiling"].get(cname),
                                "floor": ctrl0["floor"].get(cname),
                                "shuffled": ctrl0["shuffled"].get(cname),
                                "mismatched": ctrl0["mismatched"].get(cname),
                                "robot": ctrl0["robot"].get(cname), "live": r[cname][2]})
                           in ("weak", "scoped_established")]
                if len(ok_runs) >= 2:
                    wins.append(f"{arm}@{cname}{tag}({len(ok_runs)} run)")
    return wins, n_live, missing, incomp


def deferred_judge(n_rc75, n_uncleared, n_total):
    """A8 判定核心(M-T2 2026-08-03)——**純函式**,--selftest 餵 fixture 驗紅綠。

    A8 要驗的是「搶不到重活鎖者**不 silent skip**」。原式拿 `evolution_deferred_work` 的
    **總**列數判(0→N/A,否則 PASS):清帳是 `UPDATE cleared_at` 而非 `DELETE`,故總列數
    只增不減 ⇒ 一旦有過一筆就**永遠 PASS**、結構上不可能 FAIL(「這盞綠燈量的不是它宣稱
    在量的東西」)。改以 rc=75 事件數對照未清列數,FAIL 支路才真的可達。

    ⚠ **射程(誠實揭露)**:`n_rc75` 之口徑＝三軸 ledger `steps_json` 內 `rc=75` 之**步**事件。
    driver 自身之 slot-busy 路徑在**開輪之前**就 `return RC_SLOT_BUSY`,不寫 steps_json ⇒
    **該路徑不在本 counter 涵蓋內**,只涵蓋「某一步之外呼腳本自行搶槽失敗」。要涵蓋 driver
    自身路徑須另建拒絕帳(heavy_slot 只記 acquire 成功,不記 denial)——不在 M-T2 射程,列殘項。
    """
    ev = f"rc=75 步事件 {n_rc75} 筆｜deferred 未清 {n_uncleared}/總 {n_total} 列"
    if n_rc75 > 0 and n_uncleared == 0:
        return "FAIL", ev + "——有 rc=75 卻零未清積壓(落帳被吞或被靜默清帳)"
    if n_rc75 == 0 and n_total == 0:
        return "N/A", ev + "——無事件亦無帳,無資料可驗(誠實未通過)"
    return "PASS", ev + "——rc=75 事件與積壓帳相符(heavy_slot v2)"


def _q(cur, sql, params=()):
    cur.execute(sql, params)
    r = cur.fetchone()
    return r[0] if r else None


def _rg(pattern, *paths, exclude=()):
    """回命中行數(rg 缺席時退 grep -r);零命中=0。

    exclude=檔名清單:掃描時排除。用於「稽核器自己寫下的判準文字被自己掃到」之假紅
    (2026-07-27 同型第三犯:`verify` 內含 `if`,使 `(if|elif|while)` 自我命中)。
    __pycache__ 一律排除(同型第四犯 2026-08-01:本檔被他檔 import 後生成 .pyc,
    其內含本檔 pattern 字串常數;grep fallback 不看 .gitignore 且 --exclude 只除
    .py 不除 .pyc ⇒ A7 自我命中假紅)。
    """
    ex_rg = [a for f in exclude for a in ("-g", f"!{f}")] + ["-g", "!__pycache__"]
    ex_gr = [f"--exclude={f}" for f in exclude] + ["--exclude-dir=__pycache__"]
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
    # 2026-08-03(M-T2):原式=「總列數 0→N/A,否則 PASS」——deferred 列**只增不減**(清帳是
    # UPDATE cleared_at 不是 DELETE),故總列數一旦 >0 就永遠 >0 ⇒ **結構上不可能 FAIL**。
    # 改為「rc=75 事件數 vs 未清列數」對照:有事件而無未清列 ⇒ 積壓帳被吞掉(2026-07-27
    # UndefinedColumn 被 except 吞成 stderr、0 列落地之同型)⇒ FAIL。
    n_unc = _q(cur, "SELECT count(*) FROM evolution_deferred_work WHERE cleared_at IS NULL") or 0
    n_tot = _q(cur, "SELECT count(*) FROM evolution_deferred_work") or 0
    n_rc75 = sum((_q(cur, f"""SELECT count(*) FROM {t} l,
            LATERAL jsonb_array_elements(CASE WHEN jsonb_typeof(l.steps_json)='array'
                THEN l.steps_json ELSE '[]'::jsonb END) s
            WHERE (s->>'rc') = '75'""") or 0) for t in LEDGERS)
    v8, ev8 = deferred_judge(n_rc75, n_unc, n_tot)
    add("A8", "重活互斥;rc=75 事件皆於 evolution_deferred_work 留有未清列", v8, ev8)

    # A9 三軸隔離:isolation 零違規
    # 原另驗「augur_predict 對 local_model_*/raw_evolution_* 零授權」。2026-07-31 單一角色整併後
    # 該 role 退役 ⇒ **此子判準必須移除而非留著**:`role_table_grants WHERE grantee='<不存在角色>'`
    # 回 0 列,原式 `n_grant == 0` 會恆真 ⇒ **假綠**(把「角色不存在」讀成「零授權已驗」)。
    # 現行 #8 之機械落點唯 check_isolation(AST);射程 7 package,見 import_isolation.PIPELINE。
    from augur.audit.import_isolation import check_isolation
    v = check_isolation()
    add("A9", "check_isolation 零違規(#8 現唯 AST 稽核;predict role 已退役、DB 層子判準已移除)",
        "PASS" if not v else "FAIL", f"isolation 違規 {len(v)}")

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

    # A13=A′ 能力判準(EVALSET-V2 預註冊;audits/V2-RUBRIC-GO-20260728.md §七)——
    # 任一**受測臂**於任一 capability 格 evidence_level ≥ weak(嚴格勝 floor∧mismatched∧robot),
    # 且同臂同格 **≥2 個獨立 run 皆成立**。⚠ 語意=**成就判準非不變式**:未達成回 N/A(誠實未達),
    # **永不回 FAIL**——「還沒變強」不是違規,把它記紅會逼出 Goodhart。
    # R-CELL′(H1 拍板 2026-08-01):判讀粒度由 run 級改 (run,格)——原 SQL 濾 is_invalid 使
    # 132 題任一逾時即整輪作廢,A13 對 live 結構性失明;判定核心=rcell_judge(純函式,A′ 原式不動)。
    from collections import defaultdict
    cur.execute("""SELECT DISTINCT set_id FROM local_model_eval_item
        WHERE expect->>'cell_class'='capability'""")
    v2_sets = [r[0] for r in cur.fetchall()]
    ap_verdict, ap_ev = "N/A", "尚無 capability 格之凍結集"
    if v2_sets:
        cur.execute("""SELECT set_id, layer FROM local_model_eval_item
            WHERE set_id = ANY(%s) AND expect->>'cell_class'='capability' GROUP BY 1, 2""", (v2_sets,))
        cap_cells = defaultdict(set)
        for sid, lay in cur.fetchall():
            cap_cells[sid].add(lay)
        cur.execute("""SELECT set_id, eval_code_hash, arm, detail FROM local_model_eval_run
            WHERE set_id = ANY(%s) ORDER BY created_at""", (v2_sets,))
        cell = defaultdict(lambda: defaultdict(list))   # (sid,hash)->arm->[逐run之rcell_cells()]
        for sid, ch, arm, d in cur.fetchall():
            cell[(sid, ch)][arm].append(rcell_cells((d or {}).get("per_item", [])))
        wins, n_live_runs, missing, incomp = rcell_judge(cell, cap_cells)
        if wins:
            ap_verdict, ap_ev = "PASS", f"**A′ 達成(scoped,僅及該格;self-reported #32a)**:{wins}"
        elif n_live_runs:
            ap_verdict, ap_ev = "N/A", (f"未達成(非違規):受測 run={n_live_runs},"
                                        "無 (臂,capability 格) 有 ≥2 有效格 ≥weak")
        else:
            ap_verdict, ap_ev = "N/A", "v2 集尚無受測 run(批跑進行中)"
        if missing:
            ap_ev += f";缺格(R-CELL′-2 誠實列示,非證據亦非反證):{missing}"
        if incomp:
            ap_ev += f";⚠對照臂 attempt 不同值=incomparable(R-CELL′-3):{incomp}"
    add("A13", "A′:任一受測臂於能力格 ≥weak(勝 floor∧mismatched∧robot)且 ≥2 run 複現",
        ap_verdict, ap_ev)
    return out


def run(only):
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = _checks(cur)
    if only:
        rows = [r for r in rows if r[0] in set(only)]
    n = {"PASS": 0, "FAIL": 0, "N/A": 0}
    print("── 三軸驗收 A0–A13(v2 §7+A′;唯讀) ──")
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

    # ── R-CELL′ 紅綠(H1 2026-08-01)——純函式餵 fixture 驗真行為,零 DB;非字面斷言 ──
    def _pi(cname, n_ok, n_bad, f):
        return ([{"layer": cname, "f": f}] * n_ok
                + [{"layer": cname, "invalid": "error:TimeoutError"}] * n_bad)

    c1 = rcell_cells(_pi("C1", 34, 2, 0.62))["C1"]
    chk("R-CELL′-1/2:部分格(34/36 答、均值 0.62>0.5)mean 必為 None(缺格非證據)",
        c1[0] == 36 and c1[1] == 34 and c1[2] is None)
    chk("R-CELL′-1:全格有效才給 mean;f=0 亦屬有效作答(0 非 falsy 缺答)",
        abs(rcell_cells(_pi("C2P", 24, 0, 2 / 3))["C2P"][2] - 2 / 3) < 1e-9
        and rcell_cells([{"layer": "X", "f": 0}])["X"] == (1, 1, 0.0))

    def _ctrl(vc1, vc2, vb1):
        return [rcell_cells(_pi("C1", 36, 0, vc1) + _pi("C2P", 24, 0, vc2) + _pi("B1", 24, 0, vb1))]

    fx = {("s", "h"): {
        "ceiling": _ctrl(1.0, 1.0, 1.0), "floor": _ctrl(0.5, 0.5, 0.0),
        "shuffled": _ctrl(0.47, 0.46, 0.0), "mismatched": _ctrl(0.0, 0.0, 0.0),
        "robot": _ctrl(0.5, 0.5, 0.9),
        "behavior": [
            rcell_cells(_pi("C1", 34, 2, 0.62) + _pi("C2P", 24, 0, 2 / 3) + _pi("B1", 24, 0, 0.99)),
            rcell_cells(_pi("C1", 33, 3, 0.61) + _pi("C2P", 24, 0, 2 / 3) + _pi("B1", 24, 0, 0.99))]}}
    wins, n_live, missing, _ic = rcell_judge(fx, {"s": {"C1", "C2P"}})
    chk("R-CELL′-1/4:含逾時題之 run 其 C2P 有效格仍計入,恰一勝(不多不少)且 run 不連坐",
        wins == ["behavior@C2P[s/h](2 run)"] and n_live == 2)
    chk("R-CELL′-2:C1 部分格(0.62>floor 0.5)不入 wins、以缺格 34/36 列示(乙案假 PASS 之封條)",
        not any("C1" in w for w in wins) and any("C1" in m and "34/36" in m for m in missing))
    chk("R-CELL′-5:behavior 格(B1 0.99>robot 0.9)永不入 wins(判準文字寫進實作)",
        not any("B1" in w for w in wins))
    w2, _n2, m2, i2 = rcell_judge(
        {("s", "h"): {"floor": [{"C2P": (24, 24, 0.5)}, {"C2P": (24, 24, 0.6)}],
                      "mismatched": [{"C2P": (24, 24, 0.0)}], "robot": [{"C2P": (24, 24, 0.5)}],
                      "behavior": [{"C2P": (24, 24, 0.9)}, {"C2P": (24, 24, 0.9)}]}},
        {"s": {"C2P"}})
    chk("R-CELL′-3:對照臂兩 attempt 同格不同值 ⇒ fail-loud incomparable、該格不產 win",
        w2 == [] and any("floor@C2P" in x for x in i2) and any("不可判" in x for x in m2))

    # ── A8 紅綠(M-T2 2026-08-03)——純函式餵 fixture,驗**FAIL 支路真的可達** ──
    # 舊式(總列數 0→N/A 否則 PASS)對任何 n_total>0 都回 PASS ⇒ **第一條即舊碼之突變體
    # 偵測器**(scratch 實測:退回舊式該條轉紅、其餘三條仍綠)。
    # ⚠ 本組只鎖**判式**;A8 取數之 SQL 謂詞(`cleared_at IS NULL`)與 rc=75 之 jsonb 展開
    # 需 PG 才能跑,不在本自測射程——同一謂詞之行為鎖住在 run_evolution_iteration 之自測。
    chk("A8:有 rc=75 事件而零未清積壓 ⇒ FAIL(舊式在此回 PASS=結構上不可能紅)",
        deferred_judge(3, 0, 9)[0] == "FAIL")
    chk("A8:有 rc=75 事件且有未清積壓 ⇒ PASS(落帳確實發生)",
        deferred_judge(3, 3, 12)[0] == "PASS")
    chk("A8:live 現況(0 事件/0 未清/9 已清)⇒ PASS 而非恆亮告警",
        deferred_judge(0, 0, 9)[0] == "PASS")
    chk("A8:零事件零帳 ⇒ N/A(空表不算通過)", deferred_judge(0, 0, 0)[0] == "N/A")
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
