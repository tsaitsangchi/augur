#!/usr/bin/env python3
"""🎯 補跑器——清 `evolution_deferred_work` 積壓：有佐證者記 superseded、無佐證者真補跑。

守原則 #15（積壓不得靜默沉澱；清帳須附機械佐證）、#12（帳本為唯一權威）、#29。

起因（2026-07-31，餓死三日之修）：TWEVO 23:00 搶不到 heavy slot 即 rc=75 落帳走人，
而**全 repo 沒有任何東西會回來清積壓**——`cleared_at` 四筆全 NULL、
`run_evolution_iteration` 於 07-27/28/29 連三日被推遲。fail-fast 沒有錯，
**沒有補跑才是餓死的根因**。本支即那條缺的腿。

**清帳之兩條合法路（缺佐證即不清，不得為了清而清）**：
  (a) **superseded**——該工作已被「積壓時點之後」的成功輪實質涵蓋：
      tw → `evolution_iteration_ledger` 有 `axis='tw' ∧ status='succeeded' ∧
      opened_at ≥ requested_at` 之列（記其 iteration_uid 為佐證）；
      lai → `local_model_eval_run` 有 `created_at ≥ requested_at`（detail 帶 arm 者須同 arm）
      之列（記其 run_id 為佐證）。
  (b) **rerun**——無佐證者，於 heavy slot 空閒時真補跑；**rc=0 才清**，
      rc=75（跑時又被佔）或其他失敗一律留帳、印明。
  **rerun 限新鮮積壓**：無佐證且逾 STALE_HOLD_HOURS(72h)者退 hold 待人裁——
  過期補跑恐非原語境(07-31 實證:66h 舊積壓補跑燒道 13.3h、餓死當夜新輪)。
  **僅 tw/run_evolution_iteration 在 rerun 白名單**：lai 臂之重跑需 set_id／arm 全參數
  且評測身分綁 eval_code_hash，擅自代跑＝造出一個沒人預註冊的實驗，故 lai 只走 (a) 或人工。

**設計取捨**：
  - 本支**不持有** heavy slot——補跑之子行程自己取（同一把鎖，父持子必死鎖）；
    以 `flock /tmp/augur_drain.lock` 防兩個 drain 並行。
  - `cleared_by` 誠實記 `drain:superseded` / `drain:rerun`——**絕不寫人名**（本支是機器）。
  - 佐證寫進該列 `detail`（jsonb merge），列本身不刪不改文（#12）。

執行指令矩陣
------------
    python3 scripts/drain_deferred_work.py                 # 無參數＝--check（唯讀）
    python3 scripts/drain_deferred_work.py --check          # 唯讀：積壓＋slot 現況＋每筆擬處置
    python3 scripts/drain_deferred_work.py --apply          # 實作：superseded 清帳＋白名單補跑
    python3 scripts/drain_deferred_work.py --apply --limit 1        # 一次只處理最舊一筆
    python3 scripts/drain_deferred_work.py --apply --timeout 7200   # 補跑子行程時限（秒，預設 46800）
    python3 scripts/drain_deferred_work.py --selftest       # 紅綠自測（免 DB 免 API）
    # 排程（未掛；由 Steward 決定）：每 30 分 --apply --limit 1，slot 忙時自然空轉
"""

from __future__ import annotations

import argparse
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
DRAIN_LOCK = "/tmp/augur_drain.lock"

# stale-hold 判準（B3 呈案 2026-08-01;值=Steward 輕裁）：無佐證且積壓逾此時齡者不自動補跑。
# 實證：07-31 撿 66h 舊積壓補跑,燒道 13.3h 並餓死當夜 23:00 新輪（twevo.log/#11）。
STALE_HOLD_HOURS = 72.0

# rerun 白名單：(axis, step_key) → 指令。lai 不在此列（見 docstring；擅代跑＝未預註冊實驗）。
RERUN_CMDS = {
    ("tw", "run_evolution_iteration"): [
        str(REPO / "venv/bin/python"), str(REPO / "scripts/run_evolution_iteration.py"),
        "--run", "--slot-wait", "600"],
}


def decide(axis: str, step_key: str, superseded_ref: str | None,
           age_hours: float) -> tuple[str, str]:
    """純函式判準（可自測）：這筆積壓該怎麼處置。

    superseded 佐證存在 → 清帳（附佐證；不受 stale 限制——有證據的清帳永遠誠實）；
    無佐證且積壓逾 STALE_HOLD_HOURS → hold（過期補跑恐非原語境,留帳待人裁）；
    無佐證且在 rerun 白名單 → 補跑；其餘 → hold（**不得為了清而清**）。
    """
    if superseded_ref:
        return "superseded", f"已被積壓時點後之成功輪涵蓋：{superseded_ref}"
    if age_hours > STALE_HOLD_HOURS:
        return "hold", (f"積壓已 {age_hours:.0f}h（>{STALE_HOLD_HOURS:.0f}h stale 判準）"
                        "→ 過期補跑恐非原語境,留帳待人裁,不自動重跑")
    if (axis, step_key) in RERUN_CMDS:
        return "rerun", "無涵蓋佐證 → 補跑（rc=0 才清）"
    return "hold", ("不在 rerun 白名單（lai 臂重跑需全參數＋eval_code_hash 身分，"
                    "擅代跑＝未預註冊實驗）→ 留帳待 (a) 佐證出現或人工處置")


def find_superseded_ref(cur, axis: str, requested_at, detail: dict) -> str | None:
    """查「積壓時點之後」是否已有成功輪（機械佐證；查無回 None、不推測）。"""
    if axis == "tw":
        cur.execute(
            """SELECT iteration_uid FROM evolution_iteration_ledger
                WHERE axis='tw' AND status='succeeded' AND opened_at >= %s
                ORDER BY opened_at LIMIT 1""", (requested_at,))
        r = cur.fetchone()
        return f"evolution_iteration_ledger.iteration_uid={r[0]}" if r else None
    if axis == "lai":
        arm = (detail or {}).get("arm")
        q = "SELECT run_id FROM local_model_eval_run WHERE created_at >= %s"
        p: list = [requested_at]
        if arm:
            q += " AND arm = %s"
            p.append(arm)
        cur.execute(q + " ORDER BY created_at LIMIT 1", p)
        r = cur.fetchone()
        return (f"local_model_eval_run.run_id={r[0]}"
                + (f"(同 arm={arm})" if arm else "")) if r else None
    return None


def _rows(cur):
    cur.execute("""SELECT defer_id, axis, step_key, requested_at, reason, detail
                     FROM evolution_deferred_work
                    WHERE cleared_at IS NULL ORDER BY defer_id""")
    return cur.fetchall()


def check(cur) -> int:
    from augur.core.heavy_slot import holder_status

    st = holder_status()
    print(f"heavy slot 現況：持有中={st['holders'] or '(空閒)'}"
          + (f"｜死亡未釋放殘帳 {len(st['orphans'])} 筆" if st.get("orphans") else ""))
    rows = _rows(cur)
    print(f"未清積壓：{len(rows)} 筆")
    now = datetime.now(timezone.utc)
    for did, ax, sk, at, reason, detail in rows:
        ref = find_superseded_ref(cur, ax, at, detail or {})
        action, why = decide(ax, sk, ref, (now - at).total_seconds() / 3600.0)
        print(f"  #{did} {ax}/{sk} @{at:%m-%d %H:%M} → **{action}**｜{why}")
    print("（唯讀；跑 --apply 實作）")
    return 0


def apply(conn, limit: int | None, timeout: int) -> int:
    from augur.core.heavy_slot import holder_status

    cur = conn.cursor()
    done = 0
    for did, ax, sk, at, reason, detail in _rows(cur):
        if limit and done >= limit:
            break
        ref = find_superseded_ref(cur, ax, at, detail or {})
        age_h = (datetime.now(timezone.utc) - at).total_seconds() / 3600.0
        action, why = decide(ax, sk, ref, age_h)
        if action == "hold":
            print(f"  #{did} {ax}/{sk} → hold｜{why}")
            continue
        if action == "superseded":
            cur.execute(
                """UPDATE evolution_deferred_work
                      SET cleared_at=now(), cleared_by='drain:superseded',
                          detail = coalesce(detail,'{}'::jsonb) || %s::jsonb
                    WHERE defer_id=%s AND cleared_at IS NULL""",
                (json.dumps({"drain_evidence": ref}, ensure_ascii=False), did))
            conn.commit()
            done += 1
            print(f"  #{did} {ax}/{sk} → ✓ superseded｜{ref}")
            continue
        # rerun：slot 忙即誠實空轉（下次再來），不硬擠
        if holder_status()["holders"]:
            print(f"  #{did} {ax}/{sk} → slot 被佔（{holder_status()['holders']}），本輪不補跑")
            break
        cmd = RERUN_CMDS[(ax, sk)]
        print(f"  #{did} {ax}/{sk} → 補跑：{' '.join(cmd)}（timeout={timeout}s）", flush=True)
        try:
            rc = subprocess.call(cmd, cwd=str(REPO), timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"  #{did} → ✗ 補跑逾時（{timeout}s）；留帳、不清", flush=True)
            break
        if rc == 0:
            cur.execute(
                """UPDATE evolution_deferred_work
                      SET cleared_at=now(), cleared_by='drain:rerun',
                          detail = coalesce(detail,'{}'::jsonb) || %s::jsonb
                    WHERE defer_id=%s AND cleared_at IS NULL""",
                (json.dumps({"drain_rerun_rc": 0}, ensure_ascii=False), did))
            conn.commit()
            done += 1
            print(f"  #{did} → ✓ 補跑成功、已清")
        else:
            print(f"  #{did} → ✗ 補跑 rc={rc}（75=又被佔）；留帳、不清", flush=True)
            break
    print(f"本輪處置 {done} 筆；餘 {len(_rows(cur))} 筆未清")
    return 0


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    a, w = decide("tw", "run_evolution_iteration", "ledger.uid=X", 1.0)
    chk("有佐證 → superseded（不重跑）", a == "superseded" and "X" in w)
    a, _ = decide("tw", "run_evolution_iteration", None, 1.0)
    chk("tw 無佐證 → rerun（白名單內）", a == "rerun")
    a, w = decide("lai", "eval_local_model", None, 1.0)
    chk("lai 無佐證 → hold（不擅代跑未預註冊實驗）", a == "hold" and "eval_code_hash" in w)
    a, _ = decide("lai", "eval_local_model", "run_id=Y", 1.0)
    chk("lai 有佐證 → superseded", a == "superseded")
    a, _ = decide("raw", "unknown_step", None, 1.0)
    chk("未知軸/步 → hold（不亂跑）", a == "hold")
    a, w = decide("tw", "run_evolution_iteration", None, 100.0)
    chk("stale(>72h) 無佐證 → hold 不補跑（舊邏輯回 rerun;本 case 在舊碼必紅）",
        a == "hold" and "stale" in w)
    a, _ = decide("tw", "run_evolution_iteration", "ledger.uid=X", 100.0)
    chk("stale 但有佐證 → 仍 superseded（證據清帳不受 stale 限制）", a == "superseded")
    a, _ = decide("tw", "run_evolution_iteration", None, STALE_HOLD_HOURS)
    chk("恰等於門檻 → 仍 rerun（嚴格大於才 stale,邊界不誤殺）", a == "rerun")

    class _FakeCur:
        def __init__(self, ret):
            self.ret = ret
            self.sqls: list = []

        def execute(self, sql, args=()):
            self.sqls.append((" ".join(sql.split()), tuple(args)))

        def fetchone(self):
            return self.ret

    fc = _FakeCur(("uid_123",))
    ref = find_superseded_ref(fc, "tw", "2026-07-28", {})
    chk("tw 佐證查詢綁 status='succeeded' 且時點下界正確",
        "status='succeeded'" in fc.sqls[0][0] and "opened_at >= %s" in fc.sqls[0][0]
        and fc.sqls[0][1] == ("2026-07-28",) and ref and "uid_123" in ref)
    fc2 = _FakeCur(("run9",))
    ref2 = find_superseded_ref(fc2, "lai", "2026-07-27", {"arm": "behavior"})
    chk("lai 帶 arm 時查詢綁同 arm", "arm = %s" in fc2.sqls[0][0]
        and fc2.sqls[0][1] == ("2026-07-27", "behavior") and "run9" in (ref2 or ""))
    fc3 = _FakeCur(None)
    chk("查無佐證回 None（不推測）", find_superseded_ref(fc3, "tw", "2026-07-30", {}) is None)
    chk("rerun 白名單僅 tw 一項（lai 不得入）",
        list(RERUN_CMDS) == [("tw", "run_evolution_iteration")])
    chk("補跑指令帶 --slot-wait（子行程自己等鎖、父不持鎖）",
        "--slot-wait" in RERUN_CMDS[("tw", "run_evolution_iteration")])
    src = open(__file__, encoding="utf-8").read().split("def _selftest")[0]
    chk("清帳絕不寫人名（cleared_by 僅 drain:*）",
        "drain:superseded" in src and "drain:rerun" in src
        and "cleared_by='hugo'" not in src)
    chk("清帳條件含 cleared_at IS NULL（冪等、不覆蓋既清）",
        src.count("AND cleared_at IS NULL") >= 2)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="evolution_deferred_work 補跑器（superseded/rerun/hold）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    # 須 ≥ run_evolution_iteration.STEP_TIMEOUT_SEC(43200)否則本層先砍、內層逾時永遠不觸發,
    # 步紀錄一樣落不了帳(2026-07-31:內層 7200 內層先砍,故未暴露;調高內層後本層即成新上限)。
    ap.add_argument("--timeout", type=int, default=46800)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db

    if a.apply:
        lockf = open(DRAIN_LOCK, "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("另一個 drain 正在跑（/tmp/augur_drain.lock 被持有）——本次退出，非錯誤")
            return 0
    with db.connect() as conn:
        if a.apply:
            return apply(conn, a.limit, a.timeout)
        return check(conn.cursor())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
        sys.exit(main(["--check"]))
    sys.exit(main())
