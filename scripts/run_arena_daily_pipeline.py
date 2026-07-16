#!/usr/bin/env python
"""擂台每日管線 — sync→IV→特徵→資料落地檢查→對局 的編排骨架(arena plan §5;A2 後 cron 入口)。

🎯 這支在做什麼(白話):每日收盤後依序 subprocess 呼叫既有 script——
   ①sync_all_by_date(載具=daily_maintenance.py,FinMind 全市場日頻增量)→②sync_fred(載具=
   sync_macro.py)→③derive_market_iv --until→④build_market_direction_features --until→
   ⑤build_daily_direction_features --until→(檢查當日 daily_direction_feature_values 落地,
   **無新列=誠實缺席 exit 0 留 log**——休市/資料未更新即斷檔=無列,反回填 trigger 保證不補跑)
   →⑥run_arena_round --run。**頂部雙機械閘(AND;先凍後跑)**:閘一=direction_gate 有 approved 之
   dgate_arena% 列(§1 門二);閘二=arena_admission_gate 有 evaluated_pass 之 shared_foundation 列
   (G1 資料地基 PIN 06-30+G2 anti-leakage 硬前置;G1-G5 計畫 §3.3)。任一關即拒跑;任一步非零即中止(不半套)。
   結算(settle_arena_labels.py)為獨立冪等步、不在本鏈(對局與結算解耦,另掛)。

守 #8/#15(先凍後跑機械閘)· #24(sync 走既有限速引擎,本檔不另抓 API)· #28(本地編排零 usage)
   · #29a/d。SSOT=reports/augur_direction_live_arena_plan_20260711.md §5。

執行指令矩陣:
  python scripts/run_arena_daily_pipeline.py                    # 無參數:gate/資料現況+步驟(唯讀)
  python scripts/run_arena_daily_pipeline.py --dry-run          # 印步驟不執行
  python scripts/run_arena_daily_pipeline.py --run              # 實跑(gate 機械閘;FREEZE 現況必拒)
  python scripts/run_arena_daily_pipeline.py --run --date 2026-08-03   # 指定 as-of 日(預設台北今日)
"""
import argparse
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import _bootstrap  # noqa: F401
from augur.core import db

TAIPEI = ZoneInfo("Asia/Taipei")
CATCHUP_DAYS = 14   # builders 增量窗下緣(冪等 DELETE+INSERT;涵蓋前幾日管線失敗之補齊)
FEATURE_TABLE = "daily_direction_feature_values"


def _gate_approved():
    """機械閘一:approved 之 dgate_arena% 列數(表未建=0=拒跑)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_gate')")
        if not cur.fetchone()[0]:
            return 0
        cur.execute("SELECT count(*) FROM direction_gate WHERE gate_id LIKE 'dgate_arena%' AND status='approved'")
        return cur.fetchone()[0]


def _admission_pass():
    """機械閘二(G1-G5 計畫 §3.3;AND 前置):arena_admission_gate 有 evaluated_pass 之 shared_foundation
    列=G1(資料地基 PIN 06-30)+G2(anti-leakage 迴歸)硬前置全綠。fail-closed:表缺/列缺=拒跑。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.arena_admission_gate')")
        if not cur.fetchone()[0]:
            return False
        cur.execute("SELECT count(*) FROM arena_admission_gate "
                    "WHERE axis='shared_foundation' AND status='evaluated_pass'")
        return cur.fetchone()[0] > 0


def _steps(d):
    py, s = sys.executable, Path(__file__).resolve().parent
    since = (date.fromisoformat(d) - timedelta(days=CATCHUP_DAYS)).isoformat()
    pre = [
        ("sync_all_by_date(FinMind 全市場日頻增量)", [py, str(s / "daily_maintenance.py"), "--end", d]),
        ("sync_fred(FRED 總經)", [py, str(s / "sync_macro.py"), "--no-catalog"]),
        ("derive_market_iv", [py, str(s / "derive_market_iv.py"), "--run", "--since", since, "--until", d]),
        ("build_market_direction_features",
         [py, str(s / "build_market_direction_features.py"), "--run", "--since", since, "--until", d]),
        ("build_daily_direction_features",
         [py, str(s / "build_daily_direction_features.py"), "--run", "--since", since, "--until", d]),
    ]
    post = [("run_arena_round(對局)", [py, str(s / "run_arena_round.py"), "--run"])]
    return pre, post


def _landed(d):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(f"SELECT to_regclass('public.{FEATURE_TABLE}')")
        if not cur.fetchone()[0]:
            return 0
        cur.execute(f"SELECT count(*) FROM {FEATURE_TABLE} WHERE panel_date = %s", (d,))
        return cur.fetchone()[0]


def _print_plan(d):
    pre, post = _steps(d)
    for i, (label, argv) in enumerate(pre, 1):
        print(f"  {i}. {label}\n     $ {' '.join(argv)}")
    print(f"  6. (in-process)檢查 {FEATURE_TABLE} panel_date={d} 落地——無新列=誠實缺席 exit 0 留 log")
    for i, (label, argv) in enumerate(post, 7):
        print(f"  {i}. {label}\n     $ {' '.join(argv)}")


def run(d, dry):
    n_gate = _gate_approved()
    adm = _admission_pass()
    print(f"機械閘一:direction_gate approved dgate_arena% 列={n_gate}{'(開)' if n_gate else '(關)'} | "
          f"機械閘二:arena_admission_gate G1-G2 evaluated_pass={'✓(開)' if adm else '✗(關)'}"
          f"{'' if (n_gate and adm) else ' → 實跑必拒(先凍後跑)'}")
    if dry:
        print(f"--dry-run(as-of {d};只印不執行):")
        _print_plan(d)
        return 0
    if not n_gate or not adm:
        print("✗ 拒跑:雙閘須全開——閘一=direction_gate dgate_arena% approved(hugo TTY 親核);"
              "閘二=arena_admission_gate G1-G2 硬前置 evaluated_pass(preregister_arena_admission_gate"
              " → hugo --freeze → evaluate_arena_admission --evaluate;unfreeze GATE 已退史料 2026-07-16)。")
        return 1
    pre, post = _steps(d)
    for label, argv in pre:
        print(f"▶ {label}")
        rc = subprocess.run(argv).returncode
        if rc != 0:
            print(f"✗ 步驟「{label}」exit={rc} → 中止(斷檔=無列、不補跑;修復後重跑本管線即冪等補齊)")
            return rc
    n = _landed(d)
    if not n:
        print(f"誠實缺席:{d} 於 {FEATURE_TABLE} 無新列(休市/上游無更新)——本輪不出手、"
              "斷檔=無列(反回填 trigger 保證不可事後補插)。exit 0")
        return 0
    print(f"✓ 資料落地:{d} 共 {n} 列特徵")
    for label, argv in post:
        print(f"▶ {label}")
        rc = subprocess.run(argv).returncode
        if rc != 0:
            print(f"✗ 步驟「{label}」exit={rc}")
            return rc
    print("✓ 每日管線完成")
    return 0


def status(d):
    n_gate = _gate_approved()
    print(f"gate 現況:approved dgate_arena% 列={n_gate}{'(閘開)' if n_gate else '(閘關;實跑必拒=正確)'}")
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(f"SELECT to_regclass('public.{FEATURE_TABLE}')")
        if cur.fetchone()[0]:
            cur.execute(f"SELECT max(panel_date) FROM {FEATURE_TABLE}")
            print(f"特徵現況:{FEATURE_TABLE} max(panel_date)={cur.fetchone()[0]}")
        cur.execute("SELECT to_regclass('public.direction_arena_prediction')")
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*), max(pred_date) FROM direction_arena_prediction")
            n, mx = cur.fetchone()
            print(f"ledger 現況:{n} 列(max pred_date={mx})")
    print(f"步驟(as-of {d}):")
    _print_plan(d)
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(description="擂台每日管線編排(gate 機械閘;sync→特徵→誠實缺席檢查→對局)")
    ap.add_argument("--run", action="store_true", help="實跑(gate approved 才放行)")
    ap.add_argument("--dry-run", action="store_true", dest="dry", help="印步驟不執行")
    ap.add_argument("--date", help="as-of 日 YYYY-MM-DD(預設台北今日)")
    args = ap.parse_args()
    try:
        d = args.date or datetime.now(TAIPEI).date().isoformat()
        date.fromisoformat(d)
    except ValueError:
        print(f"✗ --date 非 YYYY-MM-DD:{args.date}")
        return 1
    if args.run or args.dry:
        return run(d, dry=args.dry)
    return status(d)


if __name__ == "__main__":
    sys.exit(main())
