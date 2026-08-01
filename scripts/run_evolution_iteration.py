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
import os
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.core.heavy_slot import HeavySlot, SlotLost
from augur.philosophy import iteration as it

TRIGGER_CODE = "TWEVO-S2-go"        # 開輪碼(拍板碼非人名);APPLY 之人閘碼另計=TWEVO-APPLY-go
AUTO_GATE_REF = "V2-AUTOADVANCE"    # R2 閘內自動 APPLY 之依據碼(留痕給 R6 週掃視)
RC_SLOT_BUSY = 75                   # 搶不到 heavy slot 之退出碼(非失敗、屬積壓)
RC_KILL_HALT = 76                   # kill switch=halt 之退出碼(與 75 分開:停機≠積壓,不該被補跑器撿去重試)
RC_STEP_TIMEOUT = 124               # 外呼步逾時之 rc(沿 GNU timeout 慣例;非 0 故 fail-closed)
PY = sys.executable
# 外呼步逾時上限(秒)。**2026-07-31 晚改 7200→43200**,因原值在數學上保證 I3 永遠跑不完:
# 舊依據(I3 成功兩次=5309s/3626s)取自 07-27 之 36 panels/39 features 時代,已過期;
# 今日實測 run 11 於完整 7200s 只完成 10 個 feature、run 18 於 86 分完成 8 個
# ⇒ **645-720 s/feature**,而 principle_factor_map 現有 37 個在 feature_values 之 feature
# ⇒ 一輪 I3 需 **7-10 小時**(panels 36→66、feature_values 2.51M→8.54M 之後果)。
# 設 43200(12h)=最壞估之 1.2 倍。**不得改以 --skip-multi-seed 或縮 --since 換快**:
# 前者使 G-PROM triad 變 partial SKIP(永遠拿不到雙綠)、後者換 panel 口徑而 _gate_scale
# 只指紋 min_abs_hac_t 看不出來(「宣稱可比但已換尺」之靜默污染)。
STEP_TIMEOUT_SEC = int(os.environ.get("AUGUR_STEP_TIMEOUT_SEC", "43200"))

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


def _should_check_kill(args) -> bool:
    """本次呼叫是否須過 kill 閘。**純函式**——自測餵假 args 驗真行為（免 DB）。

    真會做事的四條路徑（open/close/step/run）皆須檢；`--dry-run` 與無參數狀態顯示不受阻
    （唯讀不算執行）。抽成函式而非留在 main() 內：字面斷言驗不到分支邏輯，
    且 `"xxx" in src` 會掃到斷言自己那份副本而恆綠（2026-07-31 一日內實犯三次）。
    """
    return bool(args.open or args.close or args.step or args.run) and not args.dry_run


def _kill_state() -> str:
    """本軸之有效 kill 狀態（tw ∨ global；OR 語意 fail-safe）。

    判準單一住所＝`augur.philosophy.evolution.effective_kill_state`（#12），不另立口徑。
    自開連線後即關閉——**不佔用長交易**，以免與進行中之輪互相干擾。
    """
    from augur.philosophy.evolution import effective_kill_state
    env_halt = os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt"
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('tw','global')")
        return effective_kill_state([r[0] for r in cur.fetchall()], env_halt=env_halt)


def _open_row(cur):
    """回進行中之輪 (uid, steps_json);無則 None。"""
    cur.execute("""SELECT iteration_uid, steps_json FROM evolution_iteration_ledger
        WHERE axis='tw' AND status='running' ORDER BY iteration_id DESC LIMIT 1""")
    r = cur.fetchone()
    return (r[0], r[1] or []) if r else None


def _gate_scale(cur, run_id=None):
    """本輪閘口徑指紋——換尺即不可比之依據(GATE-raise 後 min_abs_hac_t 由 2.0 升 2.643)。

    住 `gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t'`(evolution.py DEFAULT_GATE_CONFIG 之落帳)。
    **與 dual_green_n 綁同一個 run**:兩者取自不同 run＝拿 A 尺量 B 數,比較失去意義。
    """
    if run_id is None:
        cur.execute("""SELECT gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t'
            FROM promotion_queue WHERE gate_json ? 'G-PROM'
            ORDER BY queue_id DESC LIMIT 1""")
    else:
        cur.execute("""SELECT gate_json->'G-PROM'->'thresholds'->>'min_abs_hac_t'
            FROM promotion_queue WHERE gate_json ? 'G-PROM' AND run_id=%s
            ORDER BY queue_id DESC LIMIT 1""", (run_id,))
    r = cur.fetchone()
    return f"min_abs_hac_t={r[0]}" if r and r[0] else "unset"


def _last_complete_run(cur):
    """回最新一個**引擎自己跑完**之 run_id;無則 None。兩道過濾缺一不可:

    (1) `status='succeeded'`——不得用 `max(run_id) FROM promotion_queue`,被砍死之半套掃描
        也會留 promotion_queue 列,其 run_id 更大卻只掃到少數 feature。2026-07-31 實測:
        run 12-19 各只掃到 5/1/1/3/12/9/9/7 個 feature(完整 37-39),而 max=19
        ⇒ 以 7 個 feature 之碎片冒充本輪完整證據算增益。
    (2) `config_json ? 'mode'`——`evolution_run` **混住兩類列**:引擎輪帶 `mode`,
        人工紀錄帶 `kind`(如 run 10 = `{"kind":"human_promotion",...}`,hugo 2026-07-29
        親搬 lending_fee_rate_mean_20d)。只濾 succeeded 會取到 run 10,
        **把人在輪外的手動晉升記成自動輪的成果**——本專案最忌之自我欺騙型態(#15)。
    """
    cur.execute("""SELECT max(run_id) FROM evolution_run
        WHERE status='succeeded' AND config_json ? 'mode'""")
    r = cur.fetchone()
    return r[0] if r else None


def _snapshot(cur):
    """本輪數字摘要(compare_gain 之輸入;全出自 DB query,#9/#10)。

    雙綠=**最新一個跑完的 run** 內 G-PROM ∧ G-ECON 皆 PASS 之相異特徵數
    (跨 run 累計會把舊輪算進來;取半套 run 則以碎片冒充完整證據)。
    prodset_active_n(snapshot_ver=2 起,2026-08-01 Steward 裁決)=**同一 run 晉升且仍 active**
    之列數(source_run_id 限縮)——全域計數會把人在輪外的手動晉升(如 run 10 human_promotion)
    記成自動輪的增益;版本鍵使新 scoped cur 對舊全域 prev 直比誠實回 incomparable
    (gate_scale 指紋只抓閘門檻換尺、抓不到摘要本身換口徑)。
    """
    rid = _last_complete_run(cur)
    if rid is None:
        dual_green, active = 0, 0       # 無完整 run=自動輪零產出;不得退回全域計數冒充
    else:
        cur.execute("""SELECT count(DISTINCT feature) FROM promotion_queue
            WHERE run_id = %s
              AND gate_json->'G-PROM'->>'verdict'='PASS'
              AND gate_json->'G-ECON'->>'verdict'='PASS'""", (rid,))
        dual_green = cur.fetchone()[0]
        cur.execute("""SELECT count(*) FROM evolution_production_feature_set
            WHERE set_status='active' AND source_run_id = %s""", (rid,))
        active = cur.fetchone()[0]
    return {"snapshot_ver": it.SNAPSHOT_VER,
            "dual_green_n": dual_green, "prodset_active_n": active,
            "arena_prereg_win": None, "gate_scale": _gate_scale(cur, rid),
            "source_run_id": rid}


def _tail(raw, n):
    """取末 n 行為 **str** list。`TimeoutExpired.stdout` 即使 text=True 仍是 bytes
    (CPython 以 b''.join 建例外、不經 newline translation),直接進 json.dumps 會炸
    TypeError ⇒ 該步仍然落不了帳(2026-07-31 15:21 實犯,見 journald)。"""
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", "replace")
    return (raw or "").strip().splitlines()[-n:]


def _run_cmd(step, argv, dry):
    started = _now()
    if dry:
        print(f"    [dry] {PY} {' '.join(argv)}")
        return it.step_record(step, argv[0], argv[1:], 0, started, _now(), dry_run=True)
    try:
        p = subprocess.run([PY] + argv, cwd=str(_bootstrap.ROOT) if hasattr(_bootstrap, "ROOT") else None,
                           capture_output=True, text=True, timeout=STEP_TIMEOUT_SEC)
    except subprocess.TimeoutExpired as e:
        # 逾時**不得讓例外上拋**:上拋會在 _append_step 之前炸掉整支 driver ⇒ 該步完全不落帳
        # (steps_json 查無此步)、輪永遠停在 running。2026-07-30 23:00 實犯,連四晚無產出。
        # 改為記成一般失敗步 → 走既有 fail-closed 路徑(不前進、可 --step 續跑)。
        return it.step_record(step, argv[0], argv[1:], RC_STEP_TIMEOUT, started, _now(),
                              stdout_tail=_tail(e.stdout, 3),
                              stderr_tail=[f"TimeoutExpired after {STEP_TIMEOUT_SEC}s"]
                                          + _tail(e.stderr, 2),
                              note=f"逾時 {STEP_TIMEOUT_SEC}s(可調 AUGUR_STEP_TIMEOUT_SEC);"
                                   "子行程已開之 evolution_run 列可能殘留 running,見行程計畫 W1-7")
    return it.step_record(step, argv[0], argv[1:], p.returncode, started, _now(),
                          stdout_tail=_tail(p.stdout, 3), stderr_tail=_tail(p.stderr, 2))


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
        # A5（登錄冊 2026-08-01）：一步之成敗以**末次嘗試**為準（判準住 iteration.py #12）。
        # 舊邏輯「任一步曾敗即敗」使 r01（I3 −15,−15,0 重試成功、十步末次全綠）被標
        # failed 且與 gain=true 自相矛盾；曾敗之誠實由 steps_json 全史＋retried_steps 留痕。
        fa = it.final_attempts(steps)
        done_ok = {k for k, r in fa.items() if r.get("rc") == 0}
        missing = [k for k in it.STEP_KEYS if k not in done_ok]
        failed = [k for k in it.STEP_KEYS
                  if k in fa and fa[k].get("rc") not in (0, None)]
        retried = it.retried_ok_steps(steps)
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
        # 版本鍵不符=不比、印明(判準住 iteration.incomparable_reason #12,此處只印不重算):
        # 舊全域 prev 對新 scoped cur 直比=拿舊尺量新數,gate_scale 指紋抓不到此換尺。
        ver_note = None
        if it.incomparable_reason(prev_snap, cur_snap) == "snapshot_ver":
            ver_note = (f"  (版本鍵不符:prev snapshot_ver={(prev_snap or {}).get('snapshot_ver')}"
                        f" ≠ cur={cur_snap.get('snapshot_ver')}——prodset_active_n 已由全域改"
                        " run-scoped,跨版直比會把口徑差冒充增益,故不比;下一輪起同版可比)")
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
            if ver_note:
                print(ver_note)
            return 0
        cur.execute("""UPDATE evolution_iteration_ledger
            SET status=%s, closed_at=now(), closed_by='run_evolution_iteration(執行層)',
                gain=%s, gain_basis=%s, gain_evidence=%s, consecutive_no_gain=%s, stop_reason=%s
            WHERE iteration_uid=%s""",
            (status, gain, basis,
             json.dumps({"suite_id": "twevo_i0i9_v1", "snapshot": cur_snap,
                         "prev_snapshot": prev_snap, "missing_steps": missing,
                         "retried_steps": retried}, ensure_ascii=False),
             cnt, reason, uid))
        conn.commit()
        print(f"✓ 結輪 {uid}:{status} gain={gain}(basis={basis}) 連續無增益={cnt}")
        if basis == "incomparable":
            print("  (不可比:無前輪/摘要版本換過/閘口徑換過/輪不完整——**不計停損**,誠實非「沒進步」)")
            if ver_note:
                print(ver_note)
        if status == "stopped_no_gain":
            print(f"  ⚠ 停損:{reason}")
            print("  重啟須人裁(R5):hugo 檢視後以新 trigger_code 開輪")
    return 0


def run_round(steps_to_run, dry, allow_apply, gate_ref, slot_wait: float = 0):
    """跑一輪(或指定單步)。重活前取 heavy slot;搶不到即積壓落帳並 rc=75。

    `slot_wait`(2026-07-31,餓死三日之修):>0 時**有界等待**該秒數(每 15s 重試)——
    23:00 之本支與時長不可預測之 lai 評測臂共用單槽,原「秒退」使 07-27/28/29 連三日
    rc=75 且無補跑 ⇒ 錯過一秒＝損失一天。等待上限由呼叫端(cron)明示,預設 0 不變。
    """
    slot = HeavySlot("tw_iteration")
    heavy_needed = any(it.step_meta(s)["heavy"] for s in steps_to_run)
    if heavy_needed and not dry:
        if slot_wait > 0:
            print(f"heavy slot 有界等待中(上限 {slot_wait:.0f}s;佔用者見 "
                  f"python -m augur.core.heavy_slot)…", flush=True)
        if not slot.acquire(wait_seconds=slot_wait):
            slot.defer("run_evolution_iteration", "heavy slot busy",
                       {"steps": steps_to_run, "at": _now(),
                        "waited_seconds": slot_wait})
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

    # ── kill switch（2026-07-31 補）──
    # **不用字面斷言**（`"xxx" in src` 會掃到斷言自己那份字串副本而恆綠；同日實犯三次）。
    # 以 monkeypatch 直接驗 main() 之真行為：halt 時應立刻返回、不碰 DB、不取 heavy slot。
    from augur.philosophy.evolution import effective_kill_state as _eks
    chk("kill:任一 scope halt ⇒ halt(OR 語意 fail-safe)", _eks(["clear", "halt"]) == "halt")
    chk("kill:全 clear ⇒ clear", _eks(["clear", "clear"]) == "clear")
    chk("kill:env AUGUR_EVOLUTION_KILL_SWITCH=halt 可強制", _eks(["clear"], env_halt=True) == "halt")
    chk("_kill_state 存在且可呼叫", callable(globals().get("_kill_state")))
    # 閘之射程：四條動作路徑皆檢（停機時不該佔住單槽鎖讓別的軸也動不了）；
    # dry-run 與狀態顯示不受阻。以假 args 驗——**不得呼叫 main(["--run","--dry-run"])**，
    # 那會走進 open_round() 之 db.connect() 而違反 #18「自測免 DB」（2026-07-31 實犯，
    # 以 DB_PORT=59999 複驗確認會 rc=1 崩掉）。
    class _A:
        def __init__(self, **kw):
            self.open = self.close = self.run = self.dry_run = False
            self.step = None
            self.__dict__.update(kw)
    for _f in ("open", "close", "run"):
        chk(f"閘涵蓋 --{_f}", _should_check_kill(_A(**{_f: True})) is True)
    chk("閘涵蓋 --step", _should_check_kill(_A(step="I3")) is True)
    chk("--dry-run 不受閘阻(唯讀不算執行)", _should_check_kill(_A(run=True, dry_run=True)) is False)
    chk("無參數狀態顯示不受閘阻", _should_check_kill(_A()) is False)

    # **守衛下游注入故障**，而非拆掉守衛。
    # 拆守衛之測法（本日 21:01 實犯）會讓無守衛之路徑**真的執行**——當時 main(["--run"])
    # 一路跑到 open_round → 搶不到 slot → 寫 deferred，污染帳本 4 筆。
    # 改法：把守衛**下游**的 open_round/run_round/close_round 換成「一被呼叫就爆」。
    # 守衛有效 ⇒ 下游永不被呼叫 ⇒ 綠；守衛失效 ⇒ 立刻大聲失敗且**零 DB 寫入**。
    _orig_ks = globals()["_kill_state"]
    _downstream = {n: globals()[n] for n in ("open_round", "run_round", "close_round")}

    def _tripwire(*_a, **_k):
        raise AssertionError("守衛未擋住——不該走到這裡（若非測試中，帳本已被污染）")

    globals()["_kill_state"] = lambda: "halt"
    for _n in _downstream:
        globals()[_n] = _tripwire
    try:
        for _act in ("--run", "--open", "--close"):
            chk(f"halt 時 {_act} 擋在下游之前(絆線未被觸發＝零 DB 寫入)",
                main([_act]) == RC_KILL_HALT)
        chk("halt 時 --step I3 亦擋", main(["--step", "I3"]) == RC_KILL_HALT)
        # 反向驗：絆線本身確實會爆（否則上面四條可能是「下游根本沒被換掉」而假綠）
        _fired = False
        try:
            _tripwire()
        except AssertionError:
            _fired = True
        chk("絆線本身會爆(否則上四條為假綠)", _fired)
    finally:
        globals()["_kill_state"] = _orig_ks
        globals().update(_downstream)
    chk("RC_KILL_HALT 與 RC_SLOT_BUSY 分開(停機≠積壓,不該被補跑器撿去重試)",
        RC_KILL_HALT != RC_SLOT_BUSY)

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
    # --slot-wait 透傳之行為驗證(2026-07-31):以 fake acquire 攔實收值,非 grep 字面
    from augur.core import heavy_slot as _hs
    seen = {}
    _orig_acq = _hs.HeavySlot.acquire
    _orig_defer = _hs.HeavySlot.defer
    _hs.HeavySlot.acquire = lambda self, wait_seconds=0, poll_seconds=15: (
        seen.__setitem__("wait", wait_seconds), False)[1]
    _hs.HeavySlot.defer = lambda self, *a, **k: None
    try:
        rc = run_round(["I1"], False, False, AUTO_GATE_REF, slot_wait=123)
        chk("--slot-wait 實透傳至 acquire(實收 wait_seconds=123)", seen.get("wait") == 123)
        chk("等滿仍失敗 → rc=75 積壓語義不變", rc == RC_SLOT_BUSY)
    finally:
        _hs.HeavySlot.acquire = _orig_acq
        _hs.HeavySlot.defer = _orig_defer
    # 逾時之行為驗證(2026-07-31 W0-0):以 fake subprocess.run 拋 TimeoutExpired,驗**回一筆步紀錄**
    # 而非上拋。字面斷言在此無效——正是「例外有沒有被接住」這件事字面驗不到(債 #14 同型)。
    _orig_run = subprocess.run
    # payload **必須是 bytes**:真實 TimeoutExpired 之 stdout/stderr 即使 text=True 亦為 bytes。
    # 舊版假例外未帶 output/stderr(⇒None,走 str 分支),於是這組斷言對真正的洞免疫——
    # 2026-07-31 15:21 線上 rc=124 印出後即 TypeError,而自測全綠(假綠第六犯)。
    subprocess.run = lambda *a, **k: (_ for _ in ()).throw(
        subprocess.TimeoutExpired(cmd="fake", timeout=1, output=b"a\nb\nc\n", stderr=b"e\n"))
    try:
        _rec = _run_cmd("I3", ["scripts/nonexistent_for_selftest.py"], False)
        chk("逾時被接住:回步紀錄不上拋(否則該步永不落帳)", isinstance(_rec, dict))
        chk(f"逾時 rc={RC_STEP_TIMEOUT} 非 0(走 fail-closed 不前進)", _rec.get("rc") == RC_STEP_TIMEOUT)
        # 真正要驗的不是「例外被接住」而是「這筆紀錄落得了帳」——落帳即 _append_step 之 json.dumps。
        _ser = None
        try:
            json.dumps([_rec], ensure_ascii=False)
            _ser = True
        except TypeError:
            _ser = False
        chk("逾時紀錄可序列化(json.dumps 不拋;否則接住了也仍落不了帳)", _ser)
        chk("逾時 tail 已解碼為 str(非 bytes)",
            all(isinstance(x, str) for x in _rec.get("stdout_tail") or []))
    except subprocess.TimeoutExpired:
        chk("逾時被接住:回步紀錄不上拋(否則該步永不落帳)", False)
    finally:
        subprocess.run = _orig_run
    chk("逾時上限可組態(不寫死;實測 I3 需 60-88 分)", STEP_TIMEOUT_SEC > 0
        and "AUGUR_STEP_TIMEOUT_SEC" in body)
    chk("掉鎖 fail-loud(接 SlotLost 後停手)", "except SlotLost" in body and "停手不續跑" in body)
    chk("搶不到鎖有 defer 落帳(不 silent skip)", "slot.defer(" in body)
    chk("失敗步 fail-closed 不前進", "fail-closed 停止本輪" in body)
    chk("gain 判準外包 philosophy.iteration(單一住所)",
        "it.compare_gain(" in body and "def compare_gain" not in body)
    # prodset_delta 基準(2026-08-01 Steward 裁決)——行為式驗 _snapshot 之 run-scoped 計數,零 DB。
    # fixture 模擬「run 20 自動晉升 1 顆 active＋run 10 人工晉升 1 顆 active」:scoped 查詢
    # (參數帶本輪 run_id)回 1、全域查詢回 2——突變體拿掉 source_run_id 過濾即必紅,非字面斷言。
    class _SnapCur:
        def __init__(self, rid=20):
            self._rid, self._next = rid, None

        def execute(self, sql, params=None):
            p = params or ()
            if "evolution_run" in sql:
                self._next = (self._rid,)
            elif "evolution_production_feature_set" in sql:
                self._next = (1,) if (self._rid is not None and self._rid in p) else (2,)
            elif "count(DISTINCT feature)" in sql:
                self._next = (1,)
            else:
                self._next = ("2.643",)

        def fetchone(self):
            return self._next
    _snap = _snapshot(_SnapCur())
    chk("snapshot 帶版本鍵(單一住所=iteration.SNAPSHOT_VER)",
        _snap.get("snapshot_ver") == it.SNAPSHOT_VER)
    chk("prodset_active_n 已 run-scoped(fixture:scoped=1/全域=2;退回全域計數必紅)",
        _snap.get("prodset_active_n") == 1)
    chk("scoped 計數與 dual_green 綁同一 run(source_run_id 同源)",
        _snap.get("source_run_id") == 20)
    chk("無完整 run ⇒ prodset_active_n=0(不退回全域計數冒充)",
        _snapshot(_SnapCur(rid=None)).get("prodset_active_n") == 0)
    _prev_global = {k: v for k, v in _snap.items() if k != "snapshot_ver"}
    chk("跨版直比誠實回 incomparable(舊全域 prev 無版本鍵=不比;gate_scale 指紋抓不到此換尺)",
        it.compare_gain(_prev_global, _snap) == (None, "incomparable"))
    chk("同版仍可比(版本鍵不擋正常增益判讀)",
        it.compare_gain(_snap, {**_snap, "prodset_active_n": 2}) == (True, "prodset_delta"))
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
    ap.add_argument("--slot-wait", type=float, default=0, metavar="SEC",
                    help="搶不到 heavy slot 時之有界等待秒數(預設 0=秒退;"
                         "cron 23:00 建議 10800=等到最晚 02:00)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    # ── kill switch（2026-07-31 補）────────────────────────────────────────────
    # 本 driver 原**對 kill_switch 零引用**（raw driver 同缺、已於同日修）：按下停機鈕後
    # tw 仍會開輪、仍取 heavy slot、仍跑滿 I0–I9（I3 現需 7–12h LLM），只有 I3 之子行程
    # 與 I5 會把結果標成 halted／拒絕晉升 ⇒ 「停機」實為「照跑但不採用」。
    # 檢查點刻意放在**取 heavy slot 之前**、且涵蓋 open/close/step/run 全部動作路徑：
    # 停機時不該佔住單槽鎖讓別的軸也動不了。狀態顯示（無參數）不受阻——唯讀不算執行。
    if _should_check_kill(a):
        ks = _kill_state()
        if ks == "halt":
            print("⛔ TWEVO kill switch=halt(scope tw 或 global)——不開輪、不取 heavy slot。"
                  "\n   解除：UPDATE evolution_kill_switch SET state='clear' WHERE scope IN ('tw','global');")
            return RC_KILL_HALT
    if a.open:
        return open_round(a.dry_run)
    if a.close:
        return close_round(a.dry_run, a.partial)
    if a.step:
        if a.step not in it.STEP_KEYS:
            print(f"未知步驟 {a.step}(合法:{','.join(it.STEP_KEYS)})")
            return 2
        return run_round([a.step], a.dry_run, a.allow_apply, a.gate_ref, slot_wait=a.slot_wait)
    if a.run:
        rc = open_round(a.dry_run)
        if rc:
            return rc
        rc = run_round(list(it.STEP_KEYS), a.dry_run, a.allow_apply, a.gate_ref, slot_wait=a.slot_wait)
        if rc:
            return rc
        return close_round(a.dry_run, a.partial)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
