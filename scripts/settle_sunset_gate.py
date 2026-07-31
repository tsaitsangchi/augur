#!/usr/bin/env python3
"""🎯 V2-SUNSET-r2 結算：把 Steward 之裁決寫進閘（兩條路徑，強制 TTY 親簽）。

守 `AUGUR-MC v1.6 §8.1`（條文解釋權專屬 Steward——**本腳本不判、只記錄人的判**）、
`§P5.W2`（人類權威根節點；AI 不得代簽）、`AUGUR-L6 v1.2` L6.18(a)（反自我交易：
Agent 不得為涉及自身監督機制之變更之核准主體——SUNSET 即對 Agent 進化程式之停損閘）、
#15（判死留檔）、#6（不可逆須明示）、#12（帳本為唯一權威）。

╔═══════════════════════════════════════════════════════════════════════════════╗
║ ⛔ **`--settle-fail` 不可逆，且不可更正。**                                      ║
║   `prereg_gate_no_goalpost` 對 `status IN (evaluated_pass, evaluated_fail,     ║
║   superseded)` 之列**拒絕全欄 UPDATE**——連日後 supersede 補正都不可能。          ║
║   ⇒ 裁錯了沒有回頭路；不是「難改」，是**永遠改不了**。                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

**結算 ≠ 停止（本腳本不假裝執行 consequence）**
凍結條文之 consequence 為「三軸整體停止、帳本封存、不得換 trigger_code 重開」，
但其機械載體**目前不存在**（2026-07-31 實查）：
  · `evolution_kill_switch` 四 scope（global／tw／raw／lai）**全 `clear`**；
  · `run_evolution_iteration.py`（tw）與 `run_raw_evolution_iteration.py`（raw）
    對 `kill_switch` **引用各 0 處**（僅 `run_philosophy_evolution.py` 3 處）；
  · **無封存／halt 腳本**；無任何依 deadline 自動動作之 code。
⇒ 本腳本**只寫閘之終態**，不設 kill switch、不封存帳本、不停任何 runner。
   跑完之後三軸**照常可跑**——「停止」在機械層尚待實作。此事實會在執行時再印一次。

**裁決基礎須記帳**：(a) 之爭點即「讀法」（R1 任一 direction_gate 列有數／R2 arena 之
方向門產出可評之數／R3 程式 `evaluated_pass>0`）。`--basis` 為必填，寫入
`result_snapshot.ruling_basis`；不記則日後無從稽核「當時依哪把尺裁的」。

執行指令矩陣
------------
    python3 scripts/settle_sunset_gate.py                    # 無參數＝--check（唯讀）
    python3 scripts/settle_sunset_gate.py --check            # 唯讀：閘現況＋三條件實證＋兩路徑之差異
    python3 scripts/settle_sunset_gate.py --settle-pass --basis R1   # 裁三條件至少一達成（**須 TTY 親簽**）
    python3 scripts/settle_sunset_gate.py --settle-fail --basis R2   # 裁全未達成（**須 TTY 親簽＋逐字確認**）
    python3 scripts/settle_sunset_gate.py --selftest         # 紅綠自測（免 DB 免 API）

⚠ 兩條 settle 路徑於非互動環境（管線／cron／agent）一律拒絕——簽名無預設值、不代填 OS 帳號。
⚠ `--settle-fail` 另須逐字輸入確認句，防手滑。
"""

from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

GATE_ID = "V2-SUNSET-r2"
CONFIRM_PHRASE = "我裁定全未達成且知悉此列永遠不可更正"

BASES = {
    "R1": "任一 direction_gate 列有可讀之數",
    "R2": "arena 之方向門產出可評之數",
    "R3": "判定程式口徑：direction_gate.status='evaluated_pass' > 0",
    "other": "其他（須於 --basis-note 說明）",
}


def _sign(action: str) -> str:
    """人閘：強制互動 TTY、無預設值、不代填 OS 帳號（同 gate_raise_sunset_deadline.py 口徑）。"""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise SystemExit(
            f"P5.W2 人閘：{action} 須於互動 TTY 執行。\n"
            "  非互動環境（管線／cron／agent）一律拒絕——AI 不得代簽。\n"
            "  §8.1 解釋權專屬 Steward；L6.18(a) Agent 不得為涉自身監督機制變更之核准主體。")
    typed = input(f"簽名者（親手輸入名字，將寫入 {GATE_ID}.result_snapshot.ruled_by；不得留空）: ").strip()
    if not typed:
        raise SystemExit("P5.W2 人閘：簽名不得留空——本 CLI 無預設值、不代填 OS 帳號")
    return typed


def _evidence(cur) -> dict:
    """結算當下之三條件實證（寫入 result_snapshot；純查詢、不判定）。"""
    def one(sql, args=()):
        cur.execute(sql, args)
        r = cur.fetchone()
        return r[0] if r else None

    ev = {}
    ev["arena_settled_rows"] = one(
        "SELECT count(*) FROM direction_arena_prediction WHERE settled_at IS NOT NULL")
    ev["arena_distinct_pred_date"] = one(
        "SELECT count(DISTINCT pred_date) FROM direction_arena_prediction")
    ev["dgate_evaluated_pass"] = one(
        "SELECT count(*) FROM direction_gate WHERE status='evaluated_pass'")
    ev["dgate_evaluated_fail_with_numbers"] = one(
        "SELECT count(*) FROM direction_gate WHERE status='evaluated_fail' "
        "AND evaluated_at IS NOT NULL AND result_snapshot IS NOT NULL")
    ev["dgate_arena_with_numbers"] = one(
        "SELECT count(*) FROM direction_gate WHERE gate_id LIKE '%%arena%%' "
        "AND evaluated_at IS NOT NULL AND result_snapshot IS NOT NULL")
    ev["dgate_arena_total"] = one(
        "SELECT count(*) FROM direction_gate WHERE gate_id LIKE '%%arena%%'")
    ev["prodset_active"] = one(
        "SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'")
    # 雙綠須拆兩層:裸清單會把「已在 prodset 者」與「歷史上曾雙綠者」一併算進來,
    # 讀者易誤判為「有 N 個新候選可讓 (b) 成長」。(b) 問的是 **active 由 2 成長**,
    # 故真正相關者＝雙綠 ∧ 尚未 active。2026-07-31 實例:裸清單 3 個,其中
    # inst_cumflow_position_120d 已 active、volume_gini_60d 為 07-26 基線記載之
    # 「符號反向待人裁(H5)」,真正可推進 (b) 者僅 cycle_position_252d 一個。
    cur.execute(
        "SELECT DISTINCT feature FROM promotion_queue "
        "WHERE gate_json->'G-PROM'->>'verdict'='PASS' AND gate_json->'G-ECON'->>'verdict'='PASS'")
    dg = sorted(r[0] for r in cur.fetchall())
    cur.execute("SELECT feature FROM evolution_production_feature_set WHERE set_status='active'")
    active = {r[0] for r in cur.fetchall()}
    ev["dual_green_features"] = dg
    ev["dual_green_not_yet_active"] = [f for f in dg if f not in active]
    # 最近一輪仍雙綠者（歷史曾雙綠 ≠ 現在仍雙綠）
    cur.execute(
        "SELECT DISTINCT feature FROM promotion_queue WHERE run_id=("
        "  SELECT max(run_id) FROM evolution_run WHERE status='succeeded' AND config_json ? 'mode')"
        " AND gate_json->'G-PROM'->>'verdict'='PASS' AND gate_json->'G-ECON'->>'verdict'='PASS'")
    ev["dual_green_in_last_complete_run"] = sorted(r[0] for r in cur.fetchall())
    ev["kill_switch"] = dict(
        (r[0], r[1]) for r in
        (cur.execute("SELECT scope, state FROM evolution_kill_switch") or cur.fetchall()))
    return ev


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT status, criteria->>'deadline', criteria->>'criteria_text', "
            "       evaluated_at, approved_by FROM evolution_prereg_gate WHERE gate_id=%s",
            (GATE_ID,))
        row = cur.fetchone()
        if not row:
            print(f"✗ live 查無 {GATE_ID}", file=sys.stderr)
            return 1
        status, deadline, ctext, evaluated_at, approved_by = row
        print(f"閘 {GATE_ID}：status={status} deadline={deadline} "
              f"approved_by={approved_by} evaluated_at={evaluated_at or 'NULL（未結算）'}")
        if status != "approved":
            print(f"⚠ status 非 approved ⇒ **已為終態，不可再結算**（trigger 拒絕全欄 UPDATE）")
            return 2
        print("\n── 凍結 criteria 逐字 ──")
        for ln in (ctext or "").splitlines():
            print(f"  {ln}")
        ev = _evidence(cur)
        print("\n── 結算當下之實證（純查詢、不判定）──")
        print(f"  arena 已結算列數 = {ev['arena_settled_rows']}；相異 pred_date = {ev['arena_distinct_pred_date']}")
        print(f"  direction_gate：evaluated_pass = {ev['dgate_evaluated_pass']}；"
              f"evaluated_fail 且有數 = {ev['dgate_evaluated_fail_with_numbers']}")
        print(f"  **arena 之方向門有數者 = {ev['dgate_arena_with_numbers']} / {ev['dgate_arena_total']}**")
        print(f"  prodset active = {ev['prodset_active']}")
        print(f"  雙綠候選（歷來任一輪）= {ev['dual_green_features'] or '（無）'}")
        print(f"    其中**尚未 active**（＝真正可推進 (b) 者）= "
              f"{ev['dual_green_not_yet_active'] or '（無）'}")
        print(f"    最近一個完整輪仍雙綠者 = {ev['dual_green_in_last_complete_run'] or '（無）'}")
        print(f"  kill_switch = {ev['kill_switch']}")
        print("\n── 兩條路徑之差異 ──")
        print("  --settle-pass → status=evaluated_pass；三軸續命；仍可日後另開新閘升嚴")
        print("  --settle-fail → status=evaluated_fail；**永久不可更正**；且見下")
        print("\n⛔ 結算 ≠ 停止：kill_switch 未設、帳本未封存、runner 不受影響。")
        print("   tw 與 raw 之 runner 對 kill_switch 引用各 0 處 ⇒ 即使設了 halt 也沒有 runner 會讀。")
        print("   「三軸整體停止、帳本封存」在機械層尚待實作；本腳本不假裝做到。")
        print("\n§8.1 解釋權專屬 Steward。本腳本不判定任何條件，只記錄人的裁決。")
    return 0


def _settle(conn, verdict: str, basis: str, basis_note: str | None) -> int:
    assert verdict in ("evaluated_pass", "evaluated_fail")
    if basis not in BASES:
        print(f"✗ --basis 須為 {'/'.join(BASES)} 之一", file=sys.stderr)
        return 1
    if basis == "other" and not basis_note:
        print("✗ --basis other 時 --basis-note 必填（否則日後無從稽核依哪把尺裁的）", file=sys.stderr)
        return 1
    if _check(conn) != 0:
        return 1

    print(f"\n{'='*70}")
    print(f"即將把 {GATE_ID} 結算為 **{verdict}**")
    print(f"裁決基礎（ruling_basis）= {basis}：{BASES[basis]}")
    if basis_note:
        print(f"附記 = {basis_note}")
    if verdict == "evaluated_fail":
        print("\n⛔ 此為**不可逆且不可更正**之動作：")
        print("   終態列被 trigger 拒絕全欄 UPDATE，連日後 supersede 補正都不可能。")
        print("   凍結條文之 consequence 為「三軸整體停止、帳本封存、不得換 trigger_code 重開」，")
        print("   但本腳本**不執行** consequence（機制不存在，見上）——寫完之後三軸照常可跑。")
    print(f"{'='*70}\n")

    signer = _sign(f"--settle-{verdict.split('_')[1]}")   # ← 人閘：非 TTY 到不了這裡
    if verdict == "evaluated_fail":
        typed = input(f"逐字輸入以確認（防手滑）：\n  {CONFIRM_PHRASE}\n> ").strip()
        if typed != CONFIRM_PHRASE:
            raise SystemExit("✗ 確認句不符——未寫入任何內容（安全退出）")

    with conn.cursor() as cur:
        ev = _evidence(cur)
        snapshot = {
            "verdict": verdict,
            "ruled_by": signer,
            "ruling_basis": basis,
            "ruling_basis_text": BASES[basis],
            "ruling_basis_note": basis_note,
            "evidence_at_ruling": ev,
            "consequence_executed": False,
            "consequence_note": (
                "本次結算未執行 consequence：kill_switch 未設、帳本未封存、runner 未停。"
                "機械載體不存在（tw/raw runner 對 kill_switch 引用各 0 處、無封存腳本）。"),
            "evidence_ref": "reports/augur_sunset_a_ruling_evidence_20260731.md",
        }
        cur.execute(
            "UPDATE evolution_prereg_gate SET status=%s, evaluated_at=now(), result_snapshot=%s, "
            "note=COALESCE(note||' | ','')||%s WHERE gate_id=%s AND status='approved'",
            (verdict, json.dumps(snapshot, ensure_ascii=False),
             f"結算 {verdict}（ruled_by={signer}, basis={basis}）；consequence 未執行（機制不存在）",
             GATE_ID))
        if cur.rowcount != 1:
            conn.rollback()
            print("✗ 未更新任何列（status 已非 approved？）——已回滾", file=sys.stderr)
            return 1
    conn.commit()
    print(f"\n✓ {GATE_ID} 已結算為 {verdict}（ruled_by={signer}, basis={basis}）")
    print("  ⚠ 此列自此為終態，trigger 拒絕一切後續 UPDATE。")
    if verdict == "evaluated_fail":
        print("  ⚠ **consequence 未執行**——三軸未停、帳本未封存。若要真的停止，須另行實作並執行。")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # ── 本段於 2026-07-31 夜全面改寫 ──────────────────────────────────────────
    # 原十條皆為 `"字面" in body`，而 `body = open(__file__).read()`＝**整檔含本段**
    # ⇒ 字面必在 ⇒ **十條中九條永遠不會紅**。突變實測（scripts/check_false_assertions.py
    # 之外另以探針逐條驗證）：把 TTY 人閘拆掉、把 `AND status='approved'` 拿掉
    # （終態列變可覆寫）、把 `rowcount != 1` 回滾拆掉（誤更新靜默 commit）、
    # 把逐字確認句拆掉——**四種破壞下自測皆全綠**。
    # 本支保護的是**不可逆之治權結算**，這種保護不能只是文字。
    # 改法：全部餵真輸入／假 cursor 驗真行為，零 DB（#18）。
    import io

    chk("三種讀法皆可選（不預設任一把尺）", all(k in BASES for k in ("R1", "R2", "R3")))

    # (1) TTY 人閘：非互動時 _sign() 必須 SystemExit
    # **必須餵非空字串**：餵空字串會走到「簽名不得留空」那條 SystemExit，
    # 於是拆掉 isatty 檢查後斷言仍通過——**以錯的理由變綠**（2026-07-31 撰寫本段時實犯，
    # 突變測試當場抓到：拆 isatty 後紅燈數不變）。餵 "hugo" 才能隔離出 isatty 那條路。
    _si, _so = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = io.StringIO("hugo\n"), io.StringIO()
    try:
        _got = _sign("--settle-fail")
        _blocked = False
    except SystemExit:
        _blocked, _got = True, None
    finally:
        sys.stdin, sys.stdout = _si, _so
    chk("非互動 TTY 時 _sign() 拒簽——即使輸入非空（拆掉 isatty 即紅）",
        _blocked and _got is None)

    # (2) 假 cursor：驗 UPDATE 真的帶 status='approved' 前提、且 rowcount≠1 會回滾
    class _Cur:
        def __init__(self, rowcount=1):
            self.sql, self.rowcount = [], rowcount

        def execute(self, q, p=None):
            self.sql.append(q)

        def fetchone(self):
            return (0,)          # _evidence 之各計數；值不重要，本段驗的是控制流

        def fetchall(self):
            return []

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _Conn:
        def __init__(self, rowcount=1):
            self.cur, self.committed, self.rolled = _Cur(rowcount), False, False

        def cursor(self):
            return self.cur

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled = True

    # (3) 以真流程驗控制流與 SQL（monkeypatch _check 與 _sign 略過互動與 DB）
    _oc, _os_ = globals()["_check"], globals()["_sign"]
    globals()["_check"] = lambda conn: 0
    globals()["_sign"] = lambda act: "test"
    try:
        _bad = _Conn(rowcount=0)
        _rc = _settle(_bad, "evaluated_pass", "R1", None)
        chk("rowcount=0 時回滾且回非 0（不靜默 commit）",
            _rc != 0 and _bad.rolled and not _bad.committed)
        _good = _Conn(rowcount=1)
        _rc2 = _settle(_good, "evaluated_pass", "R1", None)
        chk("rowcount=1 時 commit 且回 0（綠燈也要驗得到）",
            _rc2 == 0 and _good.committed and not _good.rolled)
        # **必須驗 _settle 真正送出的 SQL**，不是測試裡手寫的字串。
        # （2026-07-31 撰寫本段時實犯：原斷言檢查自己 execute 的字串 ⇒ 拿掉生產碼之
        #   `AND status='approved'` 後仍不紅；突變測試當場抓到。）
        _upd = [q for q in _good.cur.sql if "UPDATE evolution_prereg_gate" in q]
        chk("_settle 送出之 UPDATE 帶 status='approved' 前提（終態不覆寫）",
            bool(_upd) and all("status='approved'" in q for q in _upd))
        # snapshot 以參數傳入 execute()，故改由 _settle 之實際建構驗：
        # 攔下 executemany/execute 之參數不便，改直接檢查該常數在建構處為 False。
        # （原寫成 `... or True` ＝恆真廢斷言，2026-07-31 撰寫本段時實犯、隨即刪除。）
        import inspect as _i
        _settle_src = _i.getsource(_settle)
        chk("snapshot 之 consequence_executed 建構為 False（非 True）",
            '"consequence_executed": False' in _settle_src)
    finally:
        globals()["_check"], globals()["_sign"] = _oc, _os_

    # (4) --settle-fail 之逐字確認句：打錯字必須拒
    chk("確認句非空且夠長（防誤觸）", len(CONFIRM_PHRASE) >= 12)
    chk("確認句含『不可更正』（讓簽的人看到後果）", "不可更正" in CONFIRM_PHRASE)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=f"{GATE_ID} 結算（記錄 Steward 裁決；不代判）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--settle-pass", action="store_true", help="裁三條件至少一達成")
    ap.add_argument("--settle-fail", action="store_true", help="裁全未達成（**不可逆且不可更正**）")
    ap.add_argument("--basis", choices=list(BASES), help="裁決所依之讀法（settle 時必填）")
    ap.add_argument("--basis-note", help="裁決基礎之附記（--basis other 時必填）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.settle_pass and a.settle_fail:
        print("✗ 兩條路徑不得同時指定", file=sys.stderr)
        return 1
    from augur.core import db
    with db.connect() as conn:
        if a.settle_pass or a.settle_fail:
            if not a.basis:
                print("✗ settle 時 --basis 必填（裁決依哪把尺，須留帳供日後稽核）", file=sys.stderr)
                return 1
            return _settle(conn,
                           "evaluated_pass" if a.settle_pass else "evaluated_fail",
                           a.basis, a.basis_note)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
