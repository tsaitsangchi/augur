#!/usr/bin/env python3
"""🎯 evolution_run 殭屍回填——把「行程早死、列仍 running」之死列補記 failed。

守原則 #12（不 hand-patch：以 writer 型腳本帶理由帳批次回填，謂詞冪等）、
#15（帳本不得表達不存在的「正在跑」）、#6（--apply 動帳本＝Steward 拍板後執行）。

起因（登錄冊 B1，2026-08-01）：引擎半途被殺時無人收尾——殭屍累積 9 列
（run 11-19，07-30~07-31 drain-timer 時代之 SIGKILL 產物）。寫者自收尾已於同日
補上（`run_philosophy_evolution.py` SIGTERM handler＋abort-close），**攔得住
SIGTERM 攔不住 SIGKILL**——SIGKILL 之殘留即本支之責。

**活引擎雙閘**（絕不誤殺正在跑的輪）：
  (1) `pgrep -f run_philosophy_evolution` 有任何行程 ⇒ 跳過**全部**（不猜哪列是它的）；
  (2) `started_at` 距今 < 1 小時者一律不動（開輪極早期 pgrep 競態之緩衝）。

執行指令矩陣
------------
    python3 scripts/backfill_evolution_run_zombies.py            # 無參數＝--check（唯讀）
    python3 scripts/backfill_evolution_run_zombies.py --check    # 唯讀：逐列列殭屍與擬處置
    python3 scripts/backfill_evolution_run_zombies.py --apply    # 回填（**Steward 拍板後**；謂詞冪等）
    python3 scripts/backfill_evolution_run_zombies.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import subprocess
import sys

import _bootstrap  # noqa: F401

ENGINE_PATTERN = "run_philosophy_evolution"
MIN_AGE_HOURS = 1
NOTE = ("zombie backfill 2026-08-01: driver timeout/SIGKILL(07-31 修復前之歷史殭屍);"
        "依登錄冊 B1、Steward 拍板後批次回填")


def is_safe_to_backfill(engine_alive, age_hours, status):
    """單列可否回填。**純函式**——紅綠雙向自測。

    engine_alive ⇒ 全部不動（不猜哪列屬於活引擎）；未滿 MIN_AGE_HOURS 不動（競態緩衝）；
    僅 status='running' 可回填（終態列不碰）。
    """
    return (not engine_alive) and status == "running" and age_hours >= MIN_AGE_HOURS


def _engine_alive() -> bool:
    """真引擎（python 行程）存活否。

    pgrep -f 對**整條 cmdline** 匹配 ⇒ 會誤中含該字樣之 shell 包裝（實犯 2026-08-01：
    本工具經 bash -c eval 呼叫時,包裝行程 cmdline 內含 pattern 而被當成活引擎）。
    故以 /proc/<pid>/comm 過濾:只有 comm 為 python* 者才算引擎。
    """
    r = subprocess.run(["pgrep", "-f", ENGINE_PATTERN], capture_output=True, text=True)
    for pid in r.stdout.split():
        try:
            comm = open(f"/proc/{pid}/comm", encoding="utf-8").read().strip()
        except OSError:
            continue                        # 行程已亡＝非活引擎
        if comm.startswith("python"):
            return True
    return False


def _rows(cur):
    cur.execute(
        "SELECT run_id, started_at, status, "
        "extract(epoch from (now()-started_at))/3600.0 AS age_h, "
        "coalesce(left(notes,60),'') FROM evolution_run "
        "WHERE status='running' ORDER BY run_id")
    return cur.fetchall()


def _check(conn) -> int:
    alive = _engine_alive()
    with conn.cursor() as cur:
        rows = _rows(cur)
    print(f"引擎行程存活：{'是（全部不動）' if alive else '否'}；running 列 {len(rows)} 筆")
    for rid, st, status, age, note in rows:
        act = "回填 failed" if is_safe_to_backfill(alive, age, status) else "不動"
        print(f"  run {rid}｜{st}｜{age:.1f}h｜{note}｜擬處置={act}")
    if not rows:
        print("  （無殭屍）")
    return 0


def _apply(conn) -> int:
    alive = _engine_alive()
    if alive:
        print("⛔ 引擎行程存活——全部不動（不猜哪列是它的）。收工後再跑。", file=sys.stderr)
        return 3
    with conn.cursor() as cur:
        rows = _rows(cur)
        todo = [r for r in rows if is_safe_to_backfill(alive, r[3], r[2])]
        if not todo:
            print("✓ 無可回填列（冪等）")
            return 0
        for rid, st, _status, age, _n in todo:
            cur.execute(
                "UPDATE evolution_run SET finished_at=now(), status='failed', "
                "notes=COALESCE(notes||' | ','')||%s WHERE run_id=%s AND status='running'",
                (NOTE, rid))
            print(f"  ✓ run {rid}（{st}，{age:.1f}h）→ failed（rowcount={cur.rowcount}）")
    conn.commit()
    print(f"✓ 回填 {len(todo)} 列；steps 全史未動（#12：只補終態不改歷史）")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("死列+夠老 ⇒ 回填", is_safe_to_backfill(False, 5.0, "running") is True)
    chk("引擎存活 ⇒ 全不動（雙閘一）", is_safe_to_backfill(True, 99.0, "running") is False)
    chk("未滿 1h ⇒ 不動（競態緩衝，雙閘二）", is_safe_to_backfill(False, 0.5, "running") is False)
    chk("終態列 ⇒ 不碰（謂詞冪等之根）", is_safe_to_backfill(False, 99.0, "succeeded") is False)
    chk("恰 1h 含界可回填", is_safe_to_backfill(False, 1.0, "running") is True)
    body = open(__file__, encoding="utf-8").read()
    chk("UPDATE 帶 status='running' 謂詞（apply 冪等可重跑）",
        "AND status='running'" in body.split("def _apply")[1].split("def _selftest")[0])
    chk("note 為機器碼非人名（不代打人簽）",
        "hugo" not in NOTE and "backfill" in NOTE)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="evolution_run 殭屍回填（B1；--apply 須 Steward）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
