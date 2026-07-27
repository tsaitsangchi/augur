#!/usr/bin/env python
"""TWEVO 迭代 driver — I0→I9 一輪閉環,編排既有 script(subprocess),逐步落帳 evolution_iteration_ledger。

🎯 這支在做什麼(白話):TWEVO=三軸自進化的「台股預測」軸。一輪的意思是:從假說 map 出發,建候選特徵值→
   走漏斗→跑 local-gates 八閘→看有沒有「雙綠」→(閘全綠且人閘允許才)APPLY 進 prodset→重訓→arena 對局→
   回饋成下一輪的 map 清單→算這輪比上輪有沒有變好、要不要停損。本 driver **不自己算閘**,只按步圖呼叫
   既有 script 並把每步的 rc/起訖/產物寫進 steps_json(驗收 A3);判準住 `augur.philosophy.iteration`。

三條與「跑得動」同等重要的紀律:
  ① **重活經 heavy_slot 單槽鎖**(I1/I2/I3/I6/I7):本機 Ollama/PG/CPU 各一份,兩支重活同時跑=結果不可比;
     搶不到鎖**不 silent skip**,寫 evolution_deferred_work 並以 rc=75 退出(積壓可見)。
  ② **I5 APPLY 需明示**:預設 `apply_allowed=false`。`--allow-apply` 走 V2-AUTOADVANCE R2 之四道機械篩
     (雙綠∧kill clear、FAIL_SIGN 篩過、對照臂偽陽率閘、單輪上限 1 特徵),並在帳上留 gate_ref;
     **人閘碼 `TWEVO-APPLY-go` 由 hugo 親跑**時走 `--allow-apply --gate-ref TWEVO-APPLY-go`。driver 不代簽。
  ③ **不可比誠實回 incomparable**:閘口徑換過(GATE-raise)或無前輪 → gain=NULL、`gain_basis='incomparable'`,
     且**不計入停損**——不可比≠沒進步(2026-07-26 量尺失效之同型防線)。

守 #15(半途失敗 fail-closed 不前進;不可比不冒充無增益)· #6(APPLY 須明示)· #26(執行層自主、人閘停手)
   · #12(判準單一住所=philosophy.iteration)· #28(全本地零 Claude token)· #29a/d。
SSOT=v2 總控 §3.5 I1–I8／TWEVO 計畫 §4 步圖。

執行指令矩陣:
  python scripts/run_evolution_iteration.py                      # 無參數:現況(唯讀:近輪/未竟步/停損計數)
  python scripts/run_evolution_iteration.py --open               # 只開輪(寫 planned→running 一列)
  python scripts/run_evolution_iteration.py --run --dry-run      # 全輪乾跑(印各步將執行之指令,零寫入)
  python scripts/run_evolution_iteration.py --run                # 全輪(I5 不 APPLY;apply_allowed=false)
  python scripts/run_evolution_iteration.py --run --allow-apply --gate-ref V2-AUTOADVANCE
  python scripts/run_evolution_iteration.py --step I3            # 只跑一步(續跑半途中斷之輪)
  python scripts/run_evolution_iteration.py --close              # 只結輪(算 gain/停損並寫終態)
  python scripts/run_evolution_iteration.py --close --partial    # 未跑完仍結輪→halted(不計增益)
  python scripts/run_evolution_iteration.py --selftest           # 零 DB 純紅綠(步圖/零代簽/鎖斷言)
"""
import argparse
import datetime as dt
import json
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.core.heavy_slot import HeavySlot, SlotLost
from augur.philosophy import iteration as it

TRIGGER_CODE = "TWEVO-S2-go"        # 開輪碼(拍板碼非人名);APPLY 之人閘碼另計=TWEVO-APPLY-go
AUTO_GATE_REF = "V2-AUTOADVANCE"    # R2 閘內自動 APPLY 之依據碼(留痕給 R6 週掃視)
RC_SLOT_BUSY = 75                   # 搶不到 heavy slot 之退出碼(非失敗、屬積壓)
PY = sys.executable

# 步→指令(argv 不含 python;None=driver 內建邏輯步,不外呼)
STEP_CMD = {
    "I0": ["scripts/report_pme_gate_diagnosis.py"],
    "I1": None,                     # 候選建值:首輪無新候選即 no-op(誠實記 skipped_no_candidate)
    "I2": None,                     # 漏斗:無候選則不跑(有候選時走 verify_candidate_promotion.py)
    "I3": ["scripts/run_philosophy_evolution.py", "--local-gates"],
    "I4": None,                     # 雙綠判讀:driver 讀 promotion_queue
    "I5": ["scripts/apply_evolution_promotions.py"],
    "I6": ["scripts/verify_prodset_hotpath.py", "--check"],
    "I7": ["scripts/arena_scoreboard.py"],
    "I8": ["scripts/export_evolution_advisor_brief.py"],
    "I9": None,                     # 停損判準:driver 內建(philosophy.iteration)
}

# **射程聲明**:本 driver 實接之指令窄於 TWEVO 計畫 §5.1 規格者,逐步逐字記明,並寫進 steps_json。
# 理由(#15):十步全 rc=0 會被讀成「一輪完整 TWEVO 跑過了」,若其中數步其實只是唯讀替身而帳上不說,
# 就是用綠燈掩蓋沒做的事——與今日抓到的 A4 橡皮圖章、SUNSET(c) 假綠同型。
# 要補齊者屬「改變自動輪對生產之作用」(train_ranker 寫 model_registry、arena 重跑會與既有排程重複出單),
# 須明示授權後再接,不由 driver 逕自擴權。
STEP_SCOPE = {
    "I0": "計畫 §5.1 另列 curate_pme_map_expand.py(map 擴充);本步僅跑唯讀診斷,未擴 map",
    "I6": "計畫 §5.1 另列 train_ranker.py --run 與 predict_asof.py --run;本步僅 hotpath --check(唯讀),未重訓未預測",
    "I7": "計畫 §5.1 I7a/I7b/I7c 為 arena 出單+結算+revalidation;本步僅讀計分板——"
          "arena 已由 cron 20:00 出單／21:30 結算,driver 再跑會重複出單,故此處**刻意只讀**",
    "I8": "唯讀預覽,未加 --write;brief 落檔另由 export_evolution_advisor_brief.py --write 產出",
}


def _now():
    return dt.datetime.now().isoformat(timespec="seconds")


def _uid(cur):
    today = dt.date.today().strftime("%Y%m%d")
    cur.execute("SELECT count(*) FROM evolution_iteration_ledger WHERE iteration_uid LIKE %s",
                (f"tw-{today}-%",))
    return f"tw-{today}-r{cur.fetchone()[0] + 1:02d}"


def _open_row(cur):
    """回進行中之輪 (uid, steps_json);無則 None。"""
    cur.execute("""SELECT iteration_uid, steps_json FROM evolution_iteration_ledger
        WHERE axis='tw' AND status='running' ORDER BY iteration_id DESC LIMIT 1""")
    r = cur.fetchone()
    return (r[0], r[1] or []) if r else None


def _gate_scale(cur):
    """本輪閘口徑指紋——換尺即不可比之依據(GATE-raise 後 min_abs_hac_t 由 2.0 升 2.643)。

    住 `gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t'`(evolution.py DEFAULT_GATE_CONFIG 之落帳)。
    """
    cur.execute("""SELECT gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t'
        FROM promotion_queue WHERE gate_json ? 'G-PROM'
        ORDER BY queue_id DESC LIMIT 1""")
    r = cur.fetchone()
    return f"min_abs_hac_t={r[0]}" if r and r[0] else "unset"


def _snapshot(cur):
    """本輪數字摘要(compare_gain 之輸入;全出自 DB query,#9/#10)。

    雙綠=**最新一 run** 內 G-PROM ∧ G-ECON 皆 PASS 之相異特徵數(跨 run 累計會把舊輪算進來)。
    """
    cur.execute("""SELECT count(DISTINCT feature) FROM promotion_queue
        WHERE run_id = (SELECT max(run_id) FROM promotion_queue)
          AND gate_json->'G-PROM'->>'verdict'='PASS'
          AND gate_json->'G-ECON'->>'verdict'='PASS'""")
    dual_green = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'")
    active = cur.fetchone()[0]
    return {"dual_green_n": dual_green, "prodset_active_n": active,
            "arena_prereg_win": None, "gate_scale": _gate_scale(cur)}


def _run_cmd(step, argv, dry):
    started = _now()
    if dry:
        print(f"    [dry] {PY} {' '.join(argv)}")
        return it.step_record(step, argv[0], argv[1:], 0, started, _now(), dry_run=True)
    p = subprocess.run([PY] + argv, cwd=str(_bootstrap.ROOT) if hasattr(_bootstrap, "ROOT") else None,
                       capture_output=True, text=True, timeout=7200)
    tail = (p.stdout or "").strip().splitlines()[-3:]
    return it.step_record(step, argv[0], argv[1:], p.returncode, started, _now(),
                          stdout_tail=tail, stderr_tail=(p.stderr or "").strip().splitlines()[-2:])


def _do_step(cur, uid, step, dry, allow_apply, gate_ref):
    """跑一步,回 step_record。內建邏輯步(I1/I2/I4/I9)不外呼。"""
    started = _now()
    if step == "I4":
        snap = _snapshot(cur)
        return it.step_record(step, "(driver)", [], 0, started, _now(),
                              dual_green_n=snap["dual_green_n"], gate_scale=snap["gate_scale"])
    if step in ("I1", "I2"):
        cur.execute("SELECT count(DISTINCT feature) FROM feature_candidate_values")
        n = cur.fetchone()[0]
        return it.step_record(step, "(driver)", [], 0, started, _now(),
                              n_candidate_features=n,
                              note="無新候選=no-op(首輪預期;有候選時走 builder/漏斗)" if not n else "沿用既有候選")
    if step == "I9":
        return it.step_record(step, "(driver)", [], 0, started, _now(), note="停損判準於 --close 計算")
    if step == "I5" and not allow_apply:
        return it.step_record(step, "(driver)", [], 0, started, _now(), applied=False,
                              note="apply_allowed=false → 不 APPLY(需 --allow-apply;人閘 TWEVO-APPLY-go)")
    argv = list(STEP_CMD[step])
    if step == "I5":
        argv.append("--dry-run") if dry else None
    rec = _run_cmd(step, argv, dry)
    if step == "I5" and not dry and rec["rc"] == 0:
        rec["gate_ref"] = gate_ref
    if step in STEP_SCOPE:
        rec["scope_note"] = STEP_SCOPE[step]      # 射程窄於計畫者,帳上逐字說明(不以 rc=0 掩蓋)
    return rec


def _append_step(cur, uid, rec):
    cur.execute("""UPDATE evolution_iteration_ledger
        SET steps_json = steps_json || %s::jsonb WHERE iteration_uid=%s""",
        (json.dumps([rec], ensure_ascii=False), uid))


def open_round(dry):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM evolution_iteration_ledger WHERE axis='tw' AND status='running'")
        if cur.fetchone()[0]:
            got = _open_row(cur)
            print(f"已有進行中之輪 {got[0]}({len(got[1])} 步已跑);續跑用 --step 或 --run")
            return 0
        uid = _uid(cur)
        if dry:
            print(f"[dry] 將開輪 {uid}(trigger={TRIGGER_CODE})")
            return 0
        cur.execute("""INSERT INTO evolution_iteration_ledger
            (iteration_uid, axis, status, trigger_code, apply_allowed) VALUES (%s,'tw','running',%s,false)""",
            (uid, TRIGGER_CODE))
        conn.commit()
        print(f"✓ 開輪 {uid}(trigger={TRIGGER_CODE};apply_allowed=false)")
    return 0


def close_round(dry, partial=False):
    """結輪:算 gain(對前一已結輪)、遞推停損計數、寫終態。

    **完整性先於一切**:仍有步未跑完 → 預設**拒絕結輪**(半套結成 succeeded＝把沒做的事記成做了)。
    `--partial` 才可結,且此時強制 `halted` ＋ gain 記 `incomparable`——不完整之輪**無資格宣稱增益**。
    """
    with db.connect() as conn:
        cur = conn.cursor()
        got = _open_row(cur)
        if not got and dry:
            got = ("(dry:未開輪)", [])          # 乾跑仍算給人看(gain/停損之算式驗得到)
        if not got:
            print("無進行中之輪(先 --open)")
            return 1
        uid, steps = got
        done_ok = {s["step"] for s in steps if s.get("rc") == 0}
        missing = [k for k in it.STEP_KEYS if k not in done_ok]
        failed = [s["step"] for s in steps if s.get("rc") not in (0, None)]
        if missing and not partial and not dry:
            print(f"✗ 拒絕結輪 {uid}:尚有 {len(missing)} 步未成功({','.join(missing)})")
            print("  半套結成 succeeded＝把沒做的事記成做了。續跑 --step,或明示 --partial 結成 halted。")
            return 1

        cur.execute("""SELECT gain_evidence, consecutive_no_gain FROM evolution_iteration_ledger
            WHERE axis='tw' AND closed_at IS NOT NULL ORDER BY iteration_id DESC LIMIT 1""")
        r = cur.fetchone()
        prev_snap = (r[0] or {}).get("snapshot") if r else None
        prev_cnt = r[1] if r else 0
        cur_snap = _snapshot(cur)
        if missing:
            gain, basis = None, "incomparable"     # 不完整之輪無資格宣稱增益
        else:
            gain, basis = it.compare_gain(prev_snap, cur_snap)
        cnt = it.next_no_gain_count(prev_cnt or 0, gain, basis)
        status = ("failed" if failed else
                  "halted" if missing else
                  "stopped_no_gain" if it.should_stop(cnt) else "succeeded")
        reason = (f"步驟失敗:{','.join(failed)}(fail-closed,不前進)" if failed else
                  f"未跑完即結輪(--partial):缺 {','.join(missing)};不完整之輪不計增益、不計停損" if missing else
                  it.stop_reason_text(cnt) if status == "stopped_no_gain" else None)
        if dry:
            print(f"[dry] {uid} → {status} gain={gain}({basis}) 連續無增益={cnt}"
                  + (f" 缺步 {','.join(missing)}" if missing else ""))
            return 0
        cur.execute("""UPDATE evolution_iteration_ledger
            SET status=%s, closed_at=now(), closed_by='run_evolution_iteration(執行層)',
                gain=%s, gain_basis=%s, gain_evidence=%s, consecutive_no_gain=%s, stop_reason=%s
            WHERE iteration_uid=%s""",
            (status, gain, basis,
             json.dumps({"suite_id": "twevo_i0i9_v1", "snapshot": cur_snap,
                         "prev_snapshot": prev_snap, "missing_steps": missing}, ensure_ascii=False),
             cnt, reason, uid))
        conn.commit()
        print(f"✓ 結輪 {uid}:{status} gain={gain}(basis={basis}) 連續無增益={cnt}")
        if basis == "incomparable":
            print("  (不可比:無前輪/閘口徑換過/輪不完整——**不計停損**,誠實非「沒進步」)")
        if status == "stopped_no_gain":
            print(f"  ⚠ 停損:{reason}")
            print("  重啟須人裁(R5):hugo 檢視後以新 trigger_code 開輪")
    return 0


def run_round(steps_to_run, dry, allow_apply, gate_ref):
    """跑一輪(或指定單步)。重活前取 heavy slot;搶不到即積壓落帳並 rc=75。"""
    slot = HeavySlot("tw_iteration")
    heavy_needed = any(it.step_meta(s)["heavy"] for s in steps_to_run)
    if heavy_needed and not dry:
        if not slot.acquire():
            slot.defer("run_evolution_iteration", "heavy slot busy",
                       {"steps": steps_to_run, "at": _now()})
            print(f"⚠ 重活單槽被佔用 → 已寫 evolution_deferred_work(積壓可見);rc={RC_SLOT_BUSY}")
            return RC_SLOT_BUSY
    try:
        with db.connect() as conn:
            cur = conn.cursor()
            got = _open_row(cur)
            if not got and dry:
                got = ("(dry:未開輪)", [])      # 乾跑不需真列,但仍走完整步圖(否則 dry 驗不到後面的步)
            if not got:
                print("無進行中之輪(先 --open,或用 --run 自動開輪)")
                return 1
            uid, steps = got
            for step in steps_to_run:
                if heavy_needed and not dry:
                    slot.verify()               # 每個 heavy step 邊界重驗(掉鎖 fail-loud)
                print(f"  → {step} {it.step_meta(step)['name']}")
                rec = _do_step(cur, uid, step, dry, allow_apply, gate_ref)
                print(f"    rc={rec['rc']}" + (f" {rec.get('note','')}" if rec.get("note") else ""))
                if not dry:
                    _append_step(cur, uid, rec)
                    conn.commit()
                if rec["rc"] not in (0, None):
                    print(f"  ✗ {step} rc={rec['rc']} → fail-closed 停止本輪(不前進;修正後 --step {step} 重試)")
                    return rec["rc"]
    except SlotLost as e:
        print(f"✗ 重活鎖掉了:{e} → 停手不續跑(#15 fail-loud)")
        return 1
    finally:
        slot.release()
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT iteration_uid, status, gain, gain_basis, consecutive_no_gain,
                jsonb_array_length(steps_json), opened_at::date
            FROM evolution_iteration_ledger WHERE axis='tw' ORDER BY iteration_id DESC LIMIT 5""")
        rows = cur.fetchall()
        print("近輪:" if rows else "近輪:(無;--open 或 --run 開首輪)")
        for r in rows:
            print(f"  {r[0]} {r[1]} gain={r[2]}({r[3]}) 無增益={r[4]} 步數={r[5]} @{r[6]}")
        got = _open_row(cur)
        if got:
            nxt = it.next_step(got[1])
            print(f"進行中:{got[0]} → 下一步 {nxt or '(已跑完,可 --close)'}")
        print(f"停損門檻:TWEVO-N={it.STOP_N}(incomparable 不計)")
        cur.execute("SELECT count(*) FROM evolution_deferred_work")
        print(f"積壓(搶不到重活鎖):{cur.fetchone()[0]} 列")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("步圖十步齊(I0..I9 皆有 STEP_CMD 條目)", set(STEP_CMD) == set(it.STEP_KEYS))
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    missing = [c[0] for c in STEP_CMD.values() if c and not (root / c[0]).is_file()]
    # 被改名/刪掉的 script 會讓該步靜默走成 rc≠0 而非「這步沒接線」——鎖成紅
    chk(f"**每步所指 script 皆在**(改名即紅,不靜默):缺 {missing or 0}", not missing)
    chk("重活步經鎖:I1/I2/I3/I6/I7 標 heavy",
        all(it.step_meta(s)["heavy"] for s in ("I1", "I2", "I3", "I6", "I7")))
    chk("I5 標 writes(APPLY 會寫生產表)", it.step_meta("I5")["writes"])
    chk("搶不到鎖之退出碼非 0(積壓可見非靜默)", RC_SLOT_BUSY != 0)
    chk("開輪碼=拍板碼非人名", TRIGGER_CODE == "TWEVO-S2-go")

    src = open(__file__, encoding="utf-8").read()
    # 只掃程式體:模組 docstring 與本自測段自含目標字面=自匹配假紅(2026-07-26/27 同型教訓已五犯)
    body = src.split("def _selftest")[0].split('"""', 2)[-1]
    chk("**零代簽人閘**:程式體不寫 promoted_by/decided_by/approved_by",
        not any(k in body for k in ("promoted_by", "decided_by", "approved_by")))
    chk("**APPLY 預設關**:INSERT 開輪時 apply_allowed=false", "apply_allowed) VALUES (%s,'tw','running',%s,false)" in body)
    chk("APPLY 走 --allow-apply 明示旗標", "allow_apply" in body and "if step == \"I5\" and not allow_apply" in body)
    chk("自動 APPLY 留痕 gate_ref(R6 週掃視)", 'rec["gate_ref"] = gate_ref' in body)
    chk("重活鎖用 heavy_slot 非 flock(C3 第二版)", "HeavySlot(" in body and "flock" not in body)
    chk("掉鎖 fail-loud(接 SlotLost 後停手)", "except SlotLost" in body and "停手不續跑" in body)
    chk("搶不到鎖有 defer 落帳(不 silent skip)", "slot.defer(" in body)
    chk("失敗步 fail-closed 不前進", "fail-closed 停止本輪" in body)
    chk("gain 判準外包 philosophy.iteration(單一住所)",
        "it.compare_gain(" in body and "def compare_gain" not in body)
    chk("incomparable 不計停損之訊息有印", "不計停損" in body)
    chk("每步落帳含 rc/started/finished(A3;經 step_record)", "it.step_record(" in body)
    # 射程聲明:窄於計畫 §5.1 之步驟必須逐字說明,否則十步全綠會被讀成「完整一輪跑過了」
    chk("**射程窄於計畫者有 scope_note**(I0/I6/I7/I8)",
        set(STEP_SCOPE) == {"I0", "I6", "I7", "I8"})
    chk("scope_note 真的寫進 steps_json(不只是常數擺著)",
        'rec["scope_note"] = STEP_SCOPE[step]' in body)
    chk("I7 刻意只讀之理由記明(避免與 cron 重複出單)", "重複出單" in STEP_SCOPE["I7"])
    chk("I6 未重訓未預測記明(train_ranker/predict_asof 未接)",
        "train_ranker" in STEP_SCOPE["I6"] and "predict_asof" in STEP_SCOPE["I6"])
    chk("重啟須人裁(R5)訊息在", "重啟須人裁" in body)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="TWEVO 迭代 driver(I0–I9;重活經 heavy slot)")
    ap.add_argument("--open", action="store_true", help="只開輪")
    ap.add_argument("--run", action="store_true", help="跑整輪(未開則自動開輪)")
    ap.add_argument("--step", metavar="I3", help="只跑一步(續跑半途中斷之輪)")
    ap.add_argument("--close", action="store_true", help="只結輪(算 gain/停損)")
    ap.add_argument("--partial", action="store_true",
                    help="允許未跑完即結輪(結成 halted;不計增益不計停損)")
    ap.add_argument("--allow-apply", action="store_true",
                    help="允許 I5 APPLY(預設關;人閘碼請配 --gate-ref TWEVO-APPLY-go)")
    ap.add_argument("--gate-ref", default=AUTO_GATE_REF, help=f"APPLY 之依據碼(預設 {AUTO_GATE_REF})")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.open:
        return open_round(a.dry_run)
    if a.close:
        return close_round(a.dry_run, a.partial)
    if a.step:
        if a.step not in it.STEP_KEYS:
            print(f"未知步驟 {a.step}(合法:{','.join(it.STEP_KEYS)})")
            return 2
        return run_round([a.step], a.dry_run, a.allow_apply, a.gate_ref)
    if a.run:
        rc = open_round(a.dry_run)
        if rc:
            return rc
        rc = run_round(list(it.STEP_KEYS), a.dry_run, a.allow_apply, a.gate_ref)
        if rc:
            return rc
        return close_round(a.dry_run, a.partial)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
