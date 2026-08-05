#!/usr/bin/env python
"""sim 軸產格 runner — SIM-CAL-R1 格點 live run 產生器(W5-1;計畫 reports/sim_w3w5_implementation_plan_20260802.md §4.2)。

🎯 這支在做什麼(白話):門 SIM-CAL-R1 生效後,在每個「approved 次一交易日起、每 21 個交易日一格」的
   格點 asof,對 52 檔凍結清單跑候選 spec 之 iid_bootstrap 模擬(複用 simulate_mc_paths 引擎函式、
   **不用其 run() 入口**——run_id 需含 spec_sha、單法、要寫 sim_run_link、要讀 kill switch),寫
   mc_simulation_run(summary 追加 terminal_q_grid p1..p99=cov_p80/CRPS/PIT 之物理前提)+
   sim_run_link(candidate_id+gate_ref='SIM-CAL-R1'+arm='live')。asof=資料驅動現查 TAIEX 已實現
   交易日曆,不猜未來。catch-up 冪等:晚跑補產所有已實現缺產格點(iid 對 ≤asof 資料+seed 決定論);
   產出時該格 label 已實現者依 S-3(Steward 圈選「catch-up 註記遲產」)於 summary 註記 late_produced。
   三防衛先驗紅:①kill switch scope∈{sim,global} halt 即拒跑 ②門 sha 兩級覆算不符即拒產
   ③52 檔凍結清單史料限定推導 sha≠pinned 即停。寫入=INSERT ON CONFLICT DO NOTHING(insert-only、
   不走 UPDATE 分支故不需 honesty GUC 通行證;live 證據列一次寫死)。

   **迭代帳本接線(M-T1,2026-08-03)**:`--apply` 於產格前先開 `sim_evolution_iteration_ledger`
   之本輪列(planned)並推進 running,再寫 link——`sim_run_link.iteration_uid` 有 FK 指向該帳本
   (`migrate_sim_ledger_fk_ddl.py`),故**孤兒 uid 由 DB 層排除、非靠自律**;產格中止則結輪 halted
   ＋`gain_basis='incomparable'`(未評估之輪不宣稱增益)。**終態 succeeded/failed 屬 W4 判決端**,
   本支永不寫——產格當下無校準差可比,寫了就是假造增益(專章 §3.6)。帳本 UPDATE 不需 honesty GUC
   (sim 七表現為 delete-only,P2c 緩議;若日後補掛 honesty_ledger_guard 須同步在此加通行證)。

守 #8(僅 ≤asof 歷史;日曆=已實現) · #9/#10(判準 SSOT=門 criteria_text;數字可溯) · #15(防衛先驗紅) ·
   #28(本地零 usage) · #29a/b/d(資料驅動、格點不寫死)。判準 binding=evolution_prereg_gate 之
   SIM-CAL-R1 criteria_text;本支不創設判準、sha 防衛不合即停不放寬。

執行指令矩陣:
  python scripts/run_sim_calibration_cell.py                 # 無參數:現況(唯讀:門態/kill/候選/anchor/格點對帳)
  python scripts/run_sim_calibration_cell.py --dry-run       # 三防衛+全計算唯讀預演(零寫入;印格點×52 對帳)
  python scripts/run_sim_calibration_cell.py --apply         # 冪等補產所有已實現缺產格點(寫 run+link)
  python scripts/run_sim_calibration_cell.py --apply --asof 2026-08-03   # 只產指定格點(非法格點=拒)
  python scripts/run_sim_calibration_cell.py --selftest      # 零 DB:格點數學/run_id/spec/q_grid/三防衛紅測
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date

import _bootstrap  # noqa: F401
import numpy as np
from augur.catalog import world_concept

ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36

GATE_ID = "SIM-CAL-R1"
H_TD = 21                      # 首輪 horizon(門 thresholds.horizon_td=[21];變更=換尺=新 gate_id)
ARM = "live"
FROZEN_ASOF = "2026-05-31"     # 凍結清單之史料限定(R-1:史料受 DELETE 閘保護=推導永穩定)
TARGETS_SHA_PINNED = "649221f491e67048b23ee19f36b85274b588d0896e86447a42203b4125982ce4"
ITER_RE = re.compile(r"^sim-\d{8}-r\d{2}$")
Q_PCTS = tuple(range(1, 100))  # terminal_q_grid p1..p99


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _spec_sha(spec):
    """candidate spec 之 canonical sha(sort_keys+緊湊分隔;與 P0 INSERT 同口徑)。"""
    return _sha(json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _run_identity(gate_id, candidate_id, stock, asof, h, spec_sha):
    """run key 含 spec_sha(§2.1-A):多候選不撞、與史料 key 空間不同不衝突。決定論=冪等。"""
    key = f"simcal|{gate_id}|{candidate_id}|{stock}|{asof}|{h}|{spec_sha}"
    return "mc_" + _sha(key)[:16]


def _gate_guard(row):
    """拒產防衛(criteria_text「評估紀律」延伸到產端):status+兩級 sha 覆算,任一不符 raise。"""
    if row["status"] != "approved":
        raise ValueError(f"門 status={row['status']}≠approved")
    if _sha(row["criteria_text"]) != row["criteria_sha"]:
        raise ValueError("sha256(criteria_text)≠criteria_sha(門文可能被動)")
    m = re.search(r"thresholds_sha=([0-9a-f]{64})", row["criteria_text"])
    if not m:
        raise ValueError("criteria_text 內無 thresholds_sha 錨行")
    if _sha(row["thresholds_text"]) != m.group(1):
        raise ValueError("sha256(thresholds::text)≠criteria_text 末行 thresholds_sha")


def _targets_guard(targets, gate_targets_sha):
    """52 檔凍結清單防衛:排序後 \\n 串接 sha256 必等 pinned 且等門 thresholds.targets_sha。"""
    derived = _sha("\n".join(sorted(targets)))
    if derived != TARGETS_SHA_PINNED:
        raise ValueError(f"凍結清單 sha 漂移:derived={derived[:16]}…≠pinned(n={len(targets)};R-1 halt)")
    if gate_targets_sha != TARGETS_SHA_PINNED:
        raise ValueError("門 thresholds.targets_sha≠pinned(門文與工具鏡射斷裂)")
    return sorted(targets)


def _validate_spec(spec, h_td):
    """registry param_schema 鏡射:required 恰三鍵+additionalProperties:false;h 必等門值。"""
    if set(spec) != {"horizon_td", "n_paths", "seed"}:
        raise ValueError(f"spec 鍵集不符 param_schema(required 三鍵+封閉):{sorted(spec)}")
    if int(spec["horizon_td"]) != h_td:
        raise ValueError(f"spec.horizon_td={spec['horizon_td']}≠門 h={h_td}")
    if int(spec["n_paths"]) <= 0:
        raise ValueError("spec.n_paths 須為正")


def _grid_asofs(cal, anchor, h=H_TD):
    """格點=已實現交易日序列上自 anchor 起每 h 日一格(窗不重疊;唯計已實現=全部可產)。"""
    if anchor not in cal:
        raise ValueError("anchor 不在已實現交易日曆內")
    return cal[cal.index(anchor)::h]


def _label_for(cal, asof, h=H_TD):
    """該格 label 日=asof 後第 h 個已實現交易日;未實現回 None(不猜未來日曆 #8)。"""
    j = cal.index(asof) + h
    return cal[j] if j < len(cal) else None


def _late_note(label):
    """S-3(Steward 圈選「catch-up 註記遲產」):label 已實現後補產之 run 於 summary 誠實註記。"""
    if label is None:
        return None
    return {"post_label_created": True, "label_date": str(label),
            "note": "S-3 catch-up 補產:產出時該格 label 已實現(iid 對 ≤asof 資料+seed 決定論、無洩漏面;W3 detail 揭露)"}


def _q_grid(term):
    """終值報酬 p1..p99(99 分位;仍是摘要不存逐路徑=四鎖②不破)。cov_p80 用 p10/p90、CRPS/PIT 用全格。"""
    return [round(float(v), 6) for v in np.percentile(np.asarray(term, dtype=float), list(Q_PCTS))]


def _halted(states, env_halt=False):
    """煞車:scope∈{sim,global} 任一 halt 或 env 強制 ⇒ True(OR 語意 fail-safe;判準單一住所)。"""
    from augur.philosophy.evolution import effective_kill_state
    return effective_kill_state(states, env_halt=env_halt) == "halt"


def _env_halt():
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt"


# ---------- DB 存取(唯讀載入;寫入唯 produce(apply=True)) ----------

def _load_gate(cur):
    cur.execute("""SELECT status, criteria->>'criteria_text', (criteria->'thresholds')::text,
                          criteria_sha, (approved_at AT TIME ZONE 'Asia/Taipei')::date
                   FROM evolution_prereg_gate WHERE gate_id=%s""", (GATE_ID,))
    r = cur.fetchone()
    if not r:
        return None
    return {"status": r[0], "criteria_text": r[1], "thresholds_text": r[2],
            "criteria_sha": r[3], "approved_date": r[4]}


def _load_candidates(cur):
    cur.execute("""SELECT c.candidate_id, c.method, c.spec, c.spec_sha, c.status, m.status
                   FROM sim_evolution_candidate c
                   JOIN simulation_method_registry m ON m.method=c.method
                   WHERE c.gate_ref=%s ORDER BY c.created_at""", (GATE_ID,))
    return [{"candidate_id": r[0], "method": r[1], "spec": r[2], "spec_sha": r[3],
             "status": r[4], "method_status": r[5]} for r in cur.fetchall()]


def _kill_states(cur):
    cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('sim','global')")
    return [r[0] for r in cur.fetchall()]


def _frozen_targets(cur):
    cur.execute("""SELECT DISTINCT target_id FROM mc_simulation_run
                   WHERE target_id ~ '^[0-9]+$' AND asof_date=%s""", (FROZEN_ASOF,))
    return [r[0] for r in cur.fetchall()]


def _load_calendar(cur, approved_date):
    """anchor=approved 次一(已實現)交易日=回傳序列首元素;空=尚未實現(等 T+1 sync)。"""
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    cur.execute(f"SELECT date FROM {adj_sql} WHERE stock_id=%s AND date > %s ORDER BY date",
                ("TAIEX", approved_date))
    return [r[0] for r in cur.fetchall()]


# ---------- 迭代帳本(sim_evolution_iteration_ledger)狀態接線(M-T1) ----------
# 為何在此:`sim_run_link.iteration_uid` 有 FK 指向本帳本(migrate_sim_ledger_fk_ddl.py)——
# 帳本列不先在,link 物理上寫不進去 ⇒ 孤兒 uid 由 DB 層排除,不靠自律。
# #12:uid 口徑與開/推進/中止之 SQL 單一住所=本檔(migration 端 --open-ledger 亦呼叫此處)。
TRIGGER_CODE = "SIM-CAL-R1-CELL"
ITER_TERMINAL = ("succeeded", "failed", "halted", "stopped_no_gain")
ITER_NOTE = ("產格輪:sim_run_link 之 FK 被指對象;終態(succeeded/failed)屬 W4 判決端,"
             "產格當下無校準差可比、不得宣稱增益")

# 四句 SQL 抽為常量=**被逐字執行之行為載體**(「字串就是 payload」);故 iteration_sql_invariants()
# 對載體驗形＝對行為驗形,且常量與執行體同一住所(改壞 SQL 必同時使不變式紅)。#12/#35。
SQL_OPEN = """INSERT INTO sim_evolution_iteration_ledger
    (iteration_uid, axis, status, trigger_code, gate_ref, apply_allowed, notes)
    VALUES (%s,'sim','planned',%s,%s,false,%s)
    ON CONFLICT (iteration_uid) DO NOTHING"""
SQL_RUNNING = """UPDATE sim_evolution_iteration_ledger SET status='running'
    WHERE iteration_uid=%s AND status='planned'"""
SQL_HALT = """UPDATE sim_evolution_iteration_ledger
    SET status='halted', closed_at=now(), closed_by='run_sim_calibration_cell(執行層)',
        gain=NULL, gain_basis='incomparable', stop_reason=%s
    WHERE iteration_uid=%s AND status NOT IN %s"""
SQL_STEP = """UPDATE sim_evolution_iteration_ledger
    SET steps_json = steps_json || %s::jsonb WHERE iteration_uid=%s"""


def iteration_sql_invariants(sqls):
    """帳本四句 SQL 之不變式檢核。**純函式**——回傳被違反者清單(空=全守)。

    鎖住的行為:①開輪冪等且起於 planned ②推進只吃 planned(不覆寫既有 running/終態)
    ③中止只結未終態列且聲明不可比 ④四句一律帶 iteration_uid 謂詞(不做全表 UPDATE)
    ⑤零 DELETE/TRUNCATE(帳本受 delete-only guard,程式端亦不得試)。
    """
    o, r, h, s = sqls["open"], sqls["running"], sqls["halt"], sqls["step"]
    bad = []
    if "ON CONFLICT (iteration_uid) DO NOTHING" not in o:
        bad.append("open_idempotent")
    if "'planned'" not in o.split("VALUES")[-1]:
        bad.append("open_starts_planned")
    if "status='planned'" not in r.split("WHERE")[-1]:
        bad.append("running_only_from_planned")
    if "status='running'" not in r.split("WHERE")[0]:
        bad.append("running_sets_running")
    if "status NOT IN" not in h.split("WHERE")[-1]:
        bad.append("halt_skips_terminal")
    if "gain_basis='incomparable'" not in h or "status='halted'" not in h:
        bad.append("halt_declares_incomparable")
    for name, sql in sqls.items():
        if "iteration_uid=%s" not in sql and name != "open":
            bad.append(f"{name}_row_scoped")
        for kw in ("DELETE", "TRUNCATE", "DROP"):
            if kw in sql.upper():
                bad.append(f"{name}_destructive")
                break
    if "steps_json ||" not in s:
        bad.append("step_appends_not_replaces")
    return bad


def iteration_uid_for(anchor):
    """anchor(已實現交易日)→ 本輪 uid。**純函式**;形制受 ITER_RE 與帳本 CHECK 雙鎖。"""
    uid = f"sim-{anchor:%Y%m%d}-r01"
    if not ITER_RE.fullmatch(uid):
        raise ValueError(f"iteration_uid 形制不合帳本 CHECK:{uid}")
    return uid


def ensure_iteration_row(cur, uid):
    """開輪(planned;ON CONFLICT DO NOTHING=冪等)。回傳 1=本次新開、0=沿用既有列。"""
    cur.execute(SQL_OPEN, (uid, TRIGGER_CODE, GATE_ID, ITER_NOTE))
    return cur.rowcount


def mark_iteration_running(cur, uid):
    """planned→running(只推進 planned 列;已 running 或終態者不動)。回傳受影響列數。"""
    cur.execute(SQL_RUNNING, (uid,))
    return cur.rowcount


def halt_iteration(cur, uid, reason):
    """產格中止 → 終態 halted ＋ gain_basis='incomparable'。

    為何 halted 而非 failed:中止之輪未經評估,無任何校準差可比;依 tw 端既有先例
    (run_evolution_iteration.close_round:不完整之輪強制 halted＋incomparable)記「不可比」,
    不假造增益宣稱(專章 §3.6)。halted 不受 chk_seil_gain_basis_on_terminal 強制,仍主動聲明。
    """
    cur.execute(SQL_HALT, (reason, uid, ITER_TERMINAL))
    return cur.rowcount


def append_iteration_step(cur, uid, rec):
    """把本次產格實績追加進 steps_json(帳上可溯 #10)。零實績不追加=冪等宣稱維持乾淨。"""
    cur.execute(SQL_STEP, (json.dumps([rec], ensure_ascii=False), uid))
    return cur.rowcount


def _iter_sqls():
    """四句 SQL 之單一取得口徑(執行體與自測共用同一住所)。"""
    return {"open": SQL_OPEN, "running": SQL_RUNNING, "halt": SQL_HALT, "step": SQL_STEP}


def produce(apply, asof_arg):
    from augur.core import db
    from simulate_mc_paths import _hist_logrets, _simulate, _summary, _git7, HIST_WINDOW_TD, BLOCK_LEN
    with db.connect() as conn:
        cur = conn.cursor()
        if _halted(_kill_states(cur), env_halt=_env_halt()):
            print("✗ kill switch halt(scope sim/global 或 env)——拒跑零寫入(exit 1)")
            return 1
        row = _load_gate(cur)
        if row is None:
            print(f"✗ 門 {GATE_ID} 不存在——拒產")
            return 1
        try:
            _gate_guard(row)
            thresholds = json.loads(row["thresholds_text"])
            if H_TD not in thresholds.get("horizon_td", []):
                raise ValueError(f"門 thresholds.horizon_td 不含 {H_TD}")
            targets = _targets_guard(_frozen_targets(cur), thresholds.get("targets_sha", ""))
        except ValueError as e:
            print(f"✗ 防衛不過:{e}——拒產 exit 1 零寫入")
            return 1
        cands = _load_candidates(cur)
        if not cands:
            print("候選 0 列(gate_ref=SIM-CAL-R1):P0/W2 未落地——無事可產(等候選;非錯誤)")
            return 0
        if len(cands) > 1:
            print(f"✗ 候選 {len(cands)} 列>1:R1=單一基線候選(S-1)——停手待裁,不自選")
            return 1
        cand = cands[0]
        try:
            if cand["method_status"] != "registered":
                raise ValueError(f"method={cand['method']} registry status={cand['method_status']}≠registered")
            if _spec_sha(cand["spec"]) != cand["spec_sha"]:
                raise ValueError("spec_sha 覆算不符(候選列完整性)")
            _validate_spec(cand["spec"], H_TD)
        except ValueError as e:
            print(f"✗ 候選防衛不過:{e}——拒產 exit 1")
            return 1
        cal = _load_calendar(cur, row["approved_date"])
        if not cal:
            print(f"anchor 未實現(approved={row['approved_date']} 次一交易日尚未入庫;等 T+1 sync)——無事可產")
            return 0
        anchor = cal[0]
        grid = _grid_asofs(cal, anchor)
        if asof_arg:
            want = date.fromisoformat(asof_arg)
            if want not in grid:
                print(f"✗ --asof {want} 非合法格點(已實現格點={[str(d) for d in grid]})")
                return 1
            todo = [want]
        else:
            todo = grid
        iteration_uid = iteration_uid_for(anchor)
        n_paths, seed = int(cand["spec"]["n_paths"]), int(cand["spec"]["seed"])
        git7 = _git7()
        mode = "APPLY(寫入)" if apply else "DRY-RUN(唯讀預演,零寫入)"
        print(f"═ {GATE_ID} 產格 {mode} ═ anchor={anchor} 格點={len(grid)} 本次={len(todo)} "
              f"候選={cand['candidate_id']} n_paths={n_paths} seed={seed} iter={iteration_uid}")
        if apply:
            # 帳本列先落地並 commit:FK 之被指對象須先在(且中止時仍有列可結 halted)。
            opened = ensure_iteration_row(cur, iteration_uid)
            ran = mark_iteration_running(cur, iteration_uid)
            conn.commit()
            print(f"  帳本 {iteration_uid}:{'新開 planned' if opened else '沿用既有列'}"
                  f"{'→running' if ran else '(狀態不動)'}——sim_run_link.iteration_uid FK 之被指對象")
        else:
            print(f"  [dry] 將確保帳本列 {iteration_uid}(planned→running);本次零寫入")
        tot_new = tot_linked = 0
        try:
            for asof in todo:
                label = _label_for(cal, asof)
                late = _late_note(label)
                ids = {s: _run_identity(GATE_ID, cand["candidate_id"], s, asof, H_TD, cand["spec_sha"])
                       for s in targets}
                all_ids = list(ids.values())
                cur.execute("SELECT run_id FROM mc_simulation_run WHERE run_id=ANY(%s)", (all_ids,))
                have_run = {r[0] for r in cur.fetchall()}
                cur.execute("SELECT run_id FROM sim_run_link WHERE run_id=ANY(%s)", (all_ids,))
                have_link = {r[0] for r in cur.fetchall()}
                n_new = n_skip = n_insuff = n_linked = 0
                for stock in targets:
                    rid = ids[stock]
                    if rid in have_run and rid in have_link:
                        n_skip += 1
                        continue
                    if rid in have_run:                       # run 在、link 缺=補鏈
                        if apply:
                            cur.execute("""INSERT INTO sim_run_link (run_id,candidate_id,gate_id,iteration_uid,arm)
                                           VALUES (%s,%s,%s,%s,%s) ON CONFLICT (run_id) DO NOTHING""",
                                        (rid, cand["candidate_id"], GATE_ID, iteration_uid, ARM))
                        n_linked += 1
                        continue
                    last_close, logr = _hist_logrets(cur, stock, asof, HIST_WINDOW_TD)
                    if logr is None:
                        print(f"  ✗ {stock} ≤{asof} 歷史不足(<60td)——不產(留給 settle 端 n_excluded 口徑)")
                        n_insuff += 1
                        continue
                    rng = np.random.default_rng(seed)
                    paths = _simulate(logr, H_TD, n_paths, "iid_bootstrap", BLOCK_LEN, rng)
                    summ = _summary(last_close, paths, H_TD)
                    summ["terminal_q_grid"] = {"unit": "terminal_simple_return_vs_asof_close",
                                               "p": _q_grid(paths[:, -1])}
                    summ["sim_cal"] = {"gate_id": GATE_ID, "candidate_id": cand["candidate_id"],
                                       "spec_sha": cand["spec_sha"], "iteration_uid": iteration_uid}
                    if late:
                        summ["late_produced"] = late
                    if apply:
                        cur.execute("""INSERT INTO mc_simulation_run
                            (run_id,target_id,asof_date,horizon_td,method,block_len_td,n_paths,seed,
                             summary,is_simulation,git_sha) VALUES (%s,%s,%s,%s,%s,NULL,%s,%s,%s,true,%s)
                            ON CONFLICT (run_id) DO NOTHING""",
                            (rid, stock, asof, H_TD, cand["method"], n_paths, seed,
                             json.dumps(summ, ensure_ascii=False), git7))
                        cur.execute("""INSERT INTO sim_run_link (run_id,candidate_id,gate_id,iteration_uid,arm)
                                       VALUES (%s,%s,%s,%s,%s) ON CONFLICT (run_id) DO NOTHING""",
                                    (rid, cand["candidate_id"], GATE_ID, iteration_uid, ARM))
                    n_new += 1
                if apply:
                    conn.commit()                             # 逐格 commit=resume-safe(#6/#28)
                tot_new += n_new
                tot_linked += n_linked
                tag = " ⚠ 遲產(S-3 已註記 summary.late_produced)" if late else ""
                print(f"  格點 {asof} label={label or '未實現'}:新產 {n_new}/補鏈 {n_linked}/"
                      f"已在跳過 {n_skip}/歷史不足 {n_insuff}(計 {len(targets)} 檔){tag}")
        except Exception as e:                                # 中止即結輪 halted,不留永久 running 假象
            reason = f"產格中止:{type(e).__name__}: {e}"
            if apply:
                conn.rollback()                               # 丟棄本格未 commit 之半套寫入
                halt_iteration(cur, iteration_uid, reason)
                conn.commit()
                print(f"✗ {reason}——已結輪 halted(gain_basis=incomparable);先前已 commit 之格點保留")
            else:
                print(f"✗ {reason}(dry-run:零寫入)")
            return 1
        if apply:
            if tot_new or tot_linked:                         # 零實績不追加=冪等宣稱維持乾淨
                append_iteration_step(cur, iteration_uid, {
                    "step": "produce_cells", "rc": 0, "gate_id": GATE_ID,
                    "candidate_id": cand["candidate_id"], "spec_sha": cand["spec_sha"],
                    "asofs": [str(d) for d in todo], "n_new": tot_new, "n_linked": tot_linked,
                    "n_targets": len(targets), "git_sha": git7})
                conn.commit()
            print(f"✓ 產格完成(insert-only ON CONFLICT DO NOTHING=冪等;重跑零新增即證明);"
                  f"帳本 {iteration_uid} 留 running——終態(succeeded/failed)屬 W4 判決端,不在產格當下宣稱")
        else:
            print("(dry-run:以上為預演對帳,零寫入;--apply 才寫)")
    return 0


def status():
    try:
        from augur.core import db
        with db.connect() as conn, db.transaction(conn) as cur:
            row = _load_gate(cur)
            states = _kill_states(cur)
            cands = _load_candidates(cur)
            if row:
                print(f"門 {GATE_ID}:status={row['status']} approved_date={row['approved_date']}(台北)")
            else:
                print(f"門 {GATE_ID}:不存在")
            print(f"kill(sim/global):{states or '(無列)'} ⇒ {'HALT' if _halted(states, _env_halt()) else 'clear'}")
            print(f"候選(gate_ref={GATE_ID}):{[c['candidate_id'] for c in cands] or 0}")
            if row:
                cal = _load_calendar(cur, row["approved_date"])
                if cal:
                    grid = _grid_asofs(cal, cal[0])
                    print(f"anchor={cal[0]} 已實現格點={[str(d) for d in grid]}(資料最新={cal[-1]})")
                    cur.execute("""SELECT r.asof_date, count(*) FROM sim_run_link l
                                   JOIN mc_simulation_run r ON r.run_id=l.run_id
                                   WHERE l.gate_id=%s GROUP BY 1 ORDER BY 1""", (GATE_ID,))
                    got = dict(cur.fetchall())
                    for g in grid:
                        print(f"  格點 {g}:已產 link {got.get(g, 0)}/52")
                else:
                    print(f"anchor 未實現(approved={row['approved_date']} 次一交易日尚未入庫;等 T+1 sync)")
    except Exception as e:                                # graceful:無 DB 也不裸 traceback(#29a)
        print(f"(現況不可讀:{type(e).__name__}: {e})")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    def raises(fn):
        try:
            fn()
            return False
        except (ValueError, AssertionError):
            return True

    # 真 TAIEX 交易日 fixture(2026-05-25..2026-07-31 實收 48 日;含端午/07-10 休市之真缺口)
    cal = [date.fromisoformat(s) for s in (
        "2026-05-25,2026-05-26,2026-05-27,2026-05-28,2026-05-29,2026-06-01,2026-06-02,2026-06-03,"
        "2026-06-04,2026-06-05,2026-06-08,2026-06-09,2026-06-10,2026-06-11,2026-06-12,2026-06-15,"
        "2026-06-16,2026-06-17,2026-06-18,2026-06-22,2026-06-23,2026-06-24,2026-06-25,2026-06-26,"
        "2026-06-29,2026-06-30,2026-07-01,2026-07-02,2026-07-03,2026-07-06,2026-07-07,2026-07-08,"
        "2026-07-09,2026-07-13,2026-07-14,2026-07-15,2026-07-16,2026-07-17,2026-07-20,2026-07-21,"
        "2026-07-22,2026-07-23,2026-07-24,2026-07-27,2026-07-28,2026-07-29,2026-07-30,2026-07-31").split(",")]
    grid = _grid_asofs(cal, cal[0])
    chk("格點數學:48 日曆自 anchor 起每 21 日=3 格(0/21/42)",
        grid == [cal[0], cal[21], cal[42]] == [date(2026, 5, 25), date(2026, 6, 24), date(2026, 7, 24)])
    chk("格點窗不重疊:相鄰格 index 差=21", cal.index(grid[1]) - cal.index(grid[0]) == 21)
    chk("label:首格 label=第 21 個交易日(2026-06-24)", _label_for(cal, cal[0]) == date(2026, 6, 24))
    chk("label:末格 label 未實現 ⇒ None(不猜未來 #8)", _label_for(cal, cal[42]) is None)
    chk("anchor 不在日曆 ⇒ raise", raises(lambda: _grid_asofs(cal, date(2026, 7, 11))))

    # run 身分:決定論+spec_sha 參與 key(§2.1-A)
    a = _run_identity(GATE_ID, "c1", "2330", "2026-08-03", 21, "aa")
    chk("run_id 決定論(同輸入同 id)", a == _run_identity(GATE_ID, "c1", "2330", "2026-08-03", 21, "aa"))
    chk("run_id 形制 mc_+16hex", a.startswith("mc_") and len(a) == 19)
    chk("spec_sha 變 ⇒ run_id 變(多候選不撞)", a != _run_identity(GATE_ID, "c1", "2330", "2026-08-03", 21, "bb"))
    chk("target 變 ⇒ run_id 變", a != _run_identity(GATE_ID, "c1", "2317", "2026-08-03", 21, "aa"))
    chk("spec_sha canonical:鍵序不影響", _spec_sha({"a": 1, "b": 2}) == _spec_sha({"b": 2, "a": 1}))

    spec = {"horizon_td": 21, "n_paths": 10000, "seed": 42}
    chk("spec 驗證:合法三鍵過", not raises(lambda: _validate_spec(spec, H_TD)))
    chk("spec 驗證:多餘鍵 ⇒ 紅(additionalProperties:false)",
        raises(lambda: _validate_spec({**spec, "tilt": 1}, H_TD)))
    chk("spec 驗證:h≠21 ⇒ 紅", raises(lambda: _validate_spec({**spec, "horizon_td": 42}, H_TD)))

    # q_grid:標準常態 20000 抽 ⇒ 99 格、單調、p50≈0、p10/p90≈∓1.2816(cov_p80 物理前提)
    rng = np.random.default_rng(7)
    term = rng.standard_normal(20000)
    q = _q_grid(term)
    chk("q_grid 恰 99 格且單調不減", len(q) == 99 and all(x <= y for x, y in zip(q, q[1:])))
    chk("q_grid p50≈median(±0.05)", abs(q[49] - float(np.median(term))) < 0.05)
    chk("q_grid p10/p90≈∓1.2816(±0.1)", abs(q[9] + 1.2816) < 0.1 and abs(q[89] - 1.2816) < 0.1)

    # 門防衛:乾淨 fixture 綠、三種竄改各自紅(先驗紅)
    ttext = '{"h": 21}'
    ctext = f"門文…\nthresholds_sha={_sha(ttext)}"
    good = {"status": "approved", "criteria_text": ctext, "thresholds_text": ttext,
            "criteria_sha": _sha(ctext)}
    chk("門防衛:乾淨門過", not raises(lambda: _gate_guard(good)))
    chk("門防衛:criteria_text 被動 ⇒ 紅", raises(lambda: _gate_guard({**good, "criteria_text": ctext + " "})))
    chk("門防衛:thresholds 被動 ⇒ 紅", raises(lambda: _gate_guard({**good, "thresholds_text": '{"h": 20}'})))
    chk("門防衛:status≠approved ⇒ 紅", raises(lambda: _gate_guard({**good, "status": "proposed"})))

    # 凍結清單防衛:口徑=排序+\n 串接(獨立以 hashlib 重算驗口徑);竄改 ⇒ 紅
    import hashlib as _hl
    two = ["2330", "1101"]
    indep = _hl.sha256("1101\n2330".encode()).hexdigest()
    chk("清單口徑:排序+\\n 串接(獨立重算相等)", _sha("\n".join(sorted(two))) == indep)
    chk("清單防衛:sha≠pinned ⇒ 紅(halt 不靜默)", raises(lambda: _targets_guard(two, TARGETS_SHA_PINNED)))

    # 煞車絆線(OR 語意 fail-safe;判準單一住所=augur.philosophy.evolution)
    chk("煞車:任一 scope halt ⇒ 拒跑", _halted(["clear", "halt"]) is True)
    chk("煞車:全 clear ⇒ 放行", _halted(["clear", "clear"]) is False)
    chk("煞車:env AUGUR_EVOLUTION_KILL_SWITCH=halt 可強制", _halted(["clear"], env_halt=True) is True)

    chk("iteration_uid 形制 ^sim-8碼-rNN$", bool(ITER_RE.fullmatch("sim-20260803-r01"))
        and not ITER_RE.fullmatch("sim-2026083-r1"))

    # ── 帳本接線(M-T1):uid 推導＋四句 SQL 之行為不變式(純函式;下游真絆線=DB 之 FK) ──
    chk("uid 推導:anchor→sim-YYYYMMDD-r01(真日期輸入)",
        iteration_uid_for(date(2026, 8, 3)) == "sim-20260803-r01")
    chk("uid 推導:月/日零填補(naive 串接會產生 sim-202615-r01 被 CHECK 拒)",
        iteration_uid_for(date(2026, 1, 5)) == "sim-20260105-r01"
        and bool(ITER_RE.fullmatch(iteration_uid_for(date(2026, 1, 5)))))
    sqls = _iter_sqls()
    chk("本尊四句 SQL 全不變式守住(綠)", iteration_sql_invariants(sqls) == [])
    chk("驗紅:開輪去掉 ON CONFLICT(重跑炸/失冪等)→ open_idempotent 報違",
        "open_idempotent" in iteration_sql_invariants(
            {**sqls, "open": sqls["open"].replace("ON CONFLICT (iteration_uid) DO NOTHING", "")}))
    chk("驗紅:推進去掉 status='planned' 謂詞(會把既有 running/終態覆寫回 running)→ 報違",
        "running_only_from_planned" in iteration_sql_invariants(
            {**sqls, "running": sqls["running"].replace(" AND status='planned'", "")}))
    chk("驗紅:中止去掉 status NOT IN(可覆寫已結之終態列)→ halt_skips_terminal 報違",
        "halt_skips_terminal" in iteration_sql_invariants(
            {**sqls, "halt": sqls["halt"].replace(" AND status NOT IN %s", "")}))
    chk("驗紅:中止改記 gain_basis='calibration_delta'(未評估卻宣稱有校準差)→ 報違",
        "halt_declares_incomparable" in iteration_sql_invariants(
            {**sqls, "halt": sqls["halt"].replace("gain_basis='incomparable'",
                                                  "gain_basis='calibration_delta'")}))
    chk("驗紅:steps_json 由追加改覆寫(抹掉既有步)→ step_appends_not_replaces 報違",
        "step_appends_not_replaces" in iteration_sql_invariants(
            {**sqls, "step": sqls["step"].replace("steps_json || %s::jsonb", "%s::jsonb")}))
    chk("驗紅:任一句夾帶 DELETE(帳本受 delete-only guard)→ destructive 報違",
        "step_destructive" in iteration_sql_invariants(
            {**sqls, "step": sqls["step"] + "; DELETE FROM sim_evolution_iteration_ledger"}))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="SIM-CAL-R1 產格 runner(格點×52 凍結清單;三防衛先驗紅)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="全防衛+全計算唯讀預演(零寫入)")
    g.add_argument("--apply", action="store_true", help="冪等補產(寫 mc_simulation_run+sim_run_link)")
    ap.add_argument("--asof", help="只產指定格點 YYYY-MM-DD(非法格點=拒)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.dry_run or args.apply:
        return produce(apply=args.apply, asof_arg=args.asof)
    return status()


if __name__ == "__main__":
    sys.exit(main())
