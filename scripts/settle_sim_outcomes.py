#!/usr/bin/env python
"""sim 軸結算 writer — SIM-CAL-R1 之 live run 實現值結算,寫 sim_realized_outcome(W5-2;計畫 §4.5)。

🎯 這支在做什麼(白話):對 sim_run_link 中 gate='SIM-CAL-R1' 且尚無 sim_realized_outcome 列之 run,
   照 settle_arena_labels 已驗證藍本判 label:用 TaiwanStockPriceAdj **已實現** TAIEX 交易日曆數出
   「asof 後第 21 個交易日」=label 日(未來日曆不可知,未實現=跳過待下輪 #8)。分支:label 日有成交
   ⇒ settle_mode='normal';label 日無成交且市場日曆已過 label+7 日 ⇒ 'last_trade' 用最後成交價;
   最後成交距 label >30 日 ⇒ 'unsettleable'(realized 欄 NULL,DB CHECK 兜底);PriceAdj factor 於
   [asof,label] 窗不連續(拼接簽名:唯 f<1 段回落;減資 f0≥1 豁免)⇒ 'unsettleable'(factor_event,
   毒值不入證據、計入 n_excluded)。realized_logret=ln(close_label/close_asof);asof 收盤與 run
   summary.last_close 同源自檢(差>捨入即印警告)。寫入=insert-only 一次寫死(表無 UPDATE 閘,自律
   不 UPDATE;逐列先斷言 label>asof,chk_sro_forward 兜底)。煞車:kill switch scope∈{sim,global}
   halt 即拒跑。遲產 run(created_at≥label;S-3 catch-up)不擋結算、印明揭露供 W3 detail。

守 #6(冪等:只挑未結列) · #8(label=已實現才結) · #9/#10(實現值全出自 PriceAdj 可溯) ·
   #15(分支與 factor 簽名=機械檢核非自律) · #28(本地零 usage) · #29a/d。
   藍本=scripts/settle_arena_labels.py(WAIT_DAYS/UNSETTLE_GAP_DAYS/FACTOR_TOL 同源 import,單一住所)。

執行指令矩陣:
  python scripts/settle_sim_outcomes.py                # 無參數:現況(唯讀:未結/已結/settle_mode 分佈)
  python scripts/settle_sim_outcomes.py --dry-run      # 分類診斷唯讀(label 判定+factor 檢核+分佈;零寫入)
  python scripts/settle_sim_outcomes.py --apply        # 冪等結算所有 label 已實現之 run(insert-only 一次寫死)
  python scripts/settle_sim_outcomes.py --selftest     # 零 DB:日曆計格/四分支/logret/前向斷言/factor 簽名/煞車紅測
"""
import argparse
import math
import os
import subprocess
import sys
from bisect import bisect_right
from datetime import timedelta
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.catalog import world_concept
from settle_arena_labels import (FACTOR_TOL, TAIPEI, UNSETTLE_GAP_DAYS, WAIT_DAYS,
                                 _at, _last_le, _prices)

GATE_ID = "SIM-CAL-R1"
LOOKBACK_DAYS = 40      # 價格抓取下緣緩衝(涵蓋 asof 前最後成交與 30 日 gap 判定;同藍本)
CLOSE_TOL = 0.011       # summary.last_close 存 2 位小數 ⇒ 捨入上界 0.005+浮點餘裕;超過=印警告
ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _label_on(cal, asof, h):
    """已實現日曆上「asof 後第 h 個交易日」;未實現回 None(同藍本 bisect 口徑,不猜未來 #8)。"""
    li = bisect_right(cal, asof) + h - 1
    return cal[li] if 0 <= li < len(cal) else None


def _assert_forward(asof, label):
    """真未來斷言:label 必嚴格晚於 asof(chk_sro_forward 之程式端先鋒;違者 fail-loud 不寫)。"""
    if label is None or label <= asof:
        raise ValueError(f"label {label} 未嚴格晚於 asof {asof}")


def _classify_one(dates, closes, asof, label, market_max,
                  wait_days=WAIT_DAYS, gap_days=UNSETTLE_GAP_DAYS):
    """單 run 分支判定(純函式;鏡射藍本):回 (mode, asof_close, realized_close, realized_logret)。
    mode∈{normal,last_trade,unsettleable,pending};realized_logret=ln(close_label/close_asof)。"""
    ser = (dates, closes)
    _, asof_close = _last_le(ser, asof)
    label_close = _at(ser, label)
    if label_close is not None and asof_close:
        return ("normal", asof_close, label_close, math.log(label_close / asof_close))
    if market_max < label + timedelta(days=wait_days):
        return ("pending", asof_close, None, None)
    last_d, last_c = _last_le(ser, label)
    if asof_close and last_d is not None and (label - last_d).days <= gap_days:
        return ("last_trade", asof_close, last_c, math.log(last_c / asof_close))
    return ("unsettleable", asof_close, None, None)


def _splice_violations(seq, tol=FACTOR_TOL):
    """factor 拼接簽名(純函式;口徑鏡射藍本 _factor_check 2026-07-12 鑑識):唯 f<1 段回落=拼接;
    減資/公司行動(f0≥1 回落)豁免。seq=[(date,factor)…] 升冪;回違規配對列。"""
    out = []
    for (d0, f0), (d1, f1) in zip(seq, seq[1:]):
        if f1 < f0 * (1 - tol) and f0 < 1.0:
            out.append((d0, f0, d1, f1))
    return out


def _factor_check(cur, windows):
    """[asof,label] 窗 adj/raw factor 連續性(DB 薄殼包 _splice_violations)。回 (違規 tid 集, 檢核數)。"""
    if not windows:
        return set(), 0
    targets = sorted(windows)
    lo = min(w[0] for w in windows.values())
    hi = max(w[1] for w in windows.values())
    adj = _prices(cur, "TaiwanStockPriceAdj", targets, lo, hi)
    raw = _prices(cur, "TaiwanStockPrice", targets, lo, hi)
    bad, n_checked = set(), 0
    for tid, (wlo, whi) in windows.items():
        a, r = adj.get(tid), raw.get(tid)
        if not a or not r:
            continue        # raw 缺=無從對照(資料缺口非損傷證據;誠實跳過)
        rmap = dict(zip(r[0], r[1]))
        seq = [(d, c / rmap[d]) for d, c in zip(a[0], a[1]) if wlo <= d <= whi and d in rmap]
        if len(seq) >= 2:
            n_checked += 1
        if _splice_violations(seq):
            bad.add(tid)
    return bad, n_checked


def _halted(states, env_halt=False):
    """煞車:scope∈{sim,global} 任一 halt 或 env 強制 ⇒ True(OR fail-safe;判準單一住所)。"""
    from augur.philosophy.evolution import effective_kill_state
    return effective_kill_state(states, env_halt=env_halt) == "halt"


def _env_halt():
    return os.environ.get("AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt"


def settle(apply):
    from augur.core import db
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('sim','global')")
        if _halted([r[0] for r in cur.fetchall()], env_halt=_env_halt()):
            print("✗ kill switch halt(scope sim/global 或 env)——拒跑零寫入(exit 1)")
            return 1
        cur.execute("""SELECT l.run_id, r.target_id, r.asof_date, r.horizon_td,
                              (r.summary->>'last_close')::float8, r.created_at
                       FROM sim_run_link l
                       JOIN mc_simulation_run r ON r.run_id=l.run_id
                       LEFT JOIN sim_realized_outcome o ON o.run_id=l.run_id
                       WHERE l.gate_id=%s AND o.run_id IS NULL
                       ORDER BY r.asof_date, r.target_id""", (GATE_ID,))
        rows = cur.fetchall()
        if not rows:
            print("無未結算列(冪等:無事可做)")
            return 0
        lo = min(r[2] for r in rows) - timedelta(days=LOOKBACK_DAYS)
        adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
        cur.execute(f"SELECT date FROM {adj_sql} WHERE stock_id=%s AND date >= %s ORDER BY date",
                    ("TAIEX", lo))
        cal = [r[0] for r in cur.fetchall()]
        market_max = cal[-1] if cal else None
        realized, n_pending = [], 0
        for rid, tid, asof, h, sum_close, created in rows:
            label = _label_on(cal, asof, h)
            if label is None:
                n_pending += 1
                continue
            realized.append((rid, tid, asof, h, label, sum_close, created))
        print(f"未結算 {len(rows)} 列|label 已實現 {len(realized)}|label 未實現(待下輪) {n_pending}")
        if not realized:
            return 0
        targets = sorted({r[1] for r in realized})
        hi = max(r[4] for r in realized)
        adj = _prices(cur, "TaiwanStockPriceAdj", targets, lo, hi)
        plans, windows, n_late = [], {}, 0
        for rid, tid, asof, h, label_, sum_close, created in realized:
            ser = adj.get(tid, ([], []))
            mode, asof_close, rclose, rlogret = _classify_one(ser[0], ser[1], asof, label_, market_max)
            if mode == "pending":
                n_pending += 1
                continue
            if (sum_close is not None and asof_close
                    and abs(asof_close - sum_close) > CLOSE_TOL):
                print(f"  ⚠ {tid} asof={asof} 收盤自檢:PriceAdj={asof_close} vs summary.last_close={sum_close}"
                      f"(差>捨入;誠實揭露,仍以 PriceAdj 為準結算)")
            if created.astimezone(TAIPEI).date() >= label_:
                n_late += 1     # S-3 遲產揭露(catch-up 補產合法;不擋結算,W3 detail 揭露)
            plans.append((rid, tid, asof, h, label_, mode, rclose, rlogret))
            if mode != "unsettleable":
                w = windows.get(tid)
                windows[tid] = (min(w[0], asof), max(w[1], label_)) if w else (asof, label_)
        bad_tids, n_checked = _factor_check(cur, windows)
        if bad_tids:
            for tid in sorted(bad_tids):
                print(f"  ⚠ {tid} factor 不連續([asof,label] 窗)→ 本輪 unsettleable(factor_event,不入證據)")
        plans = [(rid, tid, asof, h, label,
                  ("unsettleable" if tid in bad_tids else mode),
                  (None if tid in bad_tids else rclose),
                  (None if tid in bad_tids else rlogret))
                 for rid, tid, asof, h, label, mode, rclose, rlogret in plans]
        dist = {m: sum(1 for p in plans if p[5] == m) for m in ("normal", "last_trade", "unsettleable")}
        print(f"factor 檢核:{n_checked} 檔窗對照,違規 {len(bad_tids)}|分佈:{dist}|遲產(S-3)揭露:{n_late} 列")
        if not apply:
            print("(dry-run:唯讀診斷,零寫入;--apply 才寫)")
            return 0
        git7 = _git7()
        with db.transaction(conn) as wcur:
            for rid, tid, asof, h, label, mode, rclose, rlogret in plans:
                _assert_forward(asof, label)
                wcur.execute("""INSERT INTO sim_realized_outcome
                    (run_id,target_id,asof_date,horizon_td,label_date,realized_close,realized_logret,
                     settle_mode,git_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (run_id) DO NOTHING""",
                    (rid, tid, asof, h, label, rclose, rlogret, mode, git7))
        print(f"✓ 結算完成:{dist}(insert-only 一次寫死;重跑冪等=只挑未結列)")
    return 0


def status():
    try:
        from augur.core import db
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("""SELECT count(*), count(o.run_id),
                                  count(*) FILTER (WHERE o.settle_mode='normal'),
                                  count(*) FILTER (WHERE o.settle_mode='last_trade'),
                                  count(*) FILTER (WHERE o.settle_mode='unsettleable')
                           FROM sim_run_link l
                           LEFT JOIN sim_realized_outcome o ON o.run_id=l.run_id
                           WHERE l.gate_id=%s""", (GATE_ID,))
            n, s, nm, lt, un = cur.fetchone()
            print(f"link({GATE_ID}) {n} 列|已結 {s}(normal {nm}/last_trade {lt}/unsettleable {un})|未結 {n - s}")
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
        except ValueError:
            return True

    from datetime import date
    # 真 TAIEX 交易日 fixture(2026-05-25..2026-07-31 實收 48 日;含端午/07-10 休市之真缺口)
    cal = [date.fromisoformat(s) for s in (
        "2026-05-25,2026-05-26,2026-05-27,2026-05-28,2026-05-29,2026-06-01,2026-06-02,2026-06-03,"
        "2026-06-04,2026-06-05,2026-06-08,2026-06-09,2026-06-10,2026-06-11,2026-06-12,2026-06-15,"
        "2026-06-16,2026-06-17,2026-06-18,2026-06-22,2026-06-23,2026-06-24,2026-06-25,2026-06-26,"
        "2026-06-29,2026-06-30,2026-07-01,2026-07-02,2026-07-03,2026-07-06,2026-07-07,2026-07-08,"
        "2026-07-09,2026-07-13,2026-07-14,2026-07-15,2026-07-16,2026-07-17,2026-07-20,2026-07-21,"
        "2026-07-22,2026-07-23,2026-07-24,2026-07-27,2026-07-28,2026-07-29,2026-07-30,2026-07-31").split(",")]
    chk("label 計格:asof=2026-05-25 後第 21 個交易日=2026-06-24(跨端午休市)",
        _label_on(cal, date(2026, 5, 25), 21) == date(2026, 6, 24))
    chk("label 計格:日曆不足 ⇒ None(待下輪,不猜未來)", _label_on(cal, date(2026, 7, 24), 21) is None)
    chk("label 計格:asof 為非交易日亦以次序數(bisect 口徑同藍本)",
        _label_on(cal, date(2026, 5, 24), 21) == date(2026, 6, 23))

    asof, label = date(2026, 5, 25), date(2026, 6, 24)
    mm = cal[-1]
    # normal:asof 與 label 皆有成交
    m, ac, rc, lr = _classify_one([asof, label], [100.0, 110.0], asof, label, mm)
    chk("分支 normal+logret=ln(110/100)", m == "normal" and ac == 100.0 and rc == 110.0
        and abs(lr - math.log(1.10)) < 1e-12)
    # pending:label 無成交且市場未過 label+7 日
    m, _, _, _ = _classify_one([asof], [100.0], asof, label, label + timedelta(days=3))
    chk("分支 pending:label 無成交且未過 +7 日觀察窗", m == "pending")
    # last_trade:label 無成交、已過 +7 日、最後成交距 label 10 日
    last_d = label - timedelta(days=10)
    m, _, rc, lr = _classify_one([asof, last_d], [100.0, 95.0], asof, label, mm)
    chk("分支 last_trade:用最後成交價+logret=ln(95/100)", m == "last_trade" and rc == 95.0
        and abs(lr - math.log(0.95)) < 1e-12)
    # unsettleable:最後成交距 label 35 日(>30)⇒ realized 欄 NULL
    m, _, rc, lr = _classify_one([asof - timedelta(days=10)], [100.0], asof, label, mm)
    chk("分支 unsettleable:gap>30 日 ⇒ realized NULL(chk_sro_unsettleable_null 同義)",
        m == "unsettleable" and rc is None and lr is None)

    chk("前向斷言:label>asof 過", not raises(lambda: _assert_forward(asof, label)))
    chk("前向斷言:label<=asof ⇒ 紅(chk_sro_forward 先鋒)", raises(lambda: _assert_forward(label, asof)))
    chk("前向斷言:label=None ⇒ 紅", raises(lambda: _assert_forward(asof, None)))

    # factor 拼接簽名(藍本 2026-07-12 鑑識口徑;FACTOR_TOL 同源 import)
    d = [date(2026, 6, i) for i in (1, 2, 3)]
    chk("factor:f<1 段回落=拼接簽名 ⇒ 抓到",
        len(_splice_violations([(d[0], 0.98), (d[1], 0.90), (d[2], 0.90)])) == 1)
    chk("factor:減資型(f0≥1 回落至 ~1)豁免不攔",
        _splice_violations([(d[0], 1.30), (d[1], 1.00), (d[2], 1.00)]) == [])
    chk("factor:捨入雜訊(容忍內)不誣賴",
        _splice_violations([(d[0], 0.980), (d[1], 0.979), (d[2], 0.979)]) == [])

    # 煞車絆線(OR 語意 fail-safe;判準單一住所=augur.philosophy.evolution)
    chk("煞車:任一 scope halt ⇒ 拒跑", _halted(["clear", "halt"]) is True)
    chk("煞車:全 clear ⇒ 放行", _halted(["clear", "clear"]) is False)
    chk("煞車:env 強制 halt", _halted(["clear"], env_halt=True) is True)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="SIM-CAL-R1 結算 writer(已實現日曆判 label;insert-only 一次寫死)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="分類診斷唯讀(零寫入)")
    g.add_argument("--apply", action="store_true", help="冪等結算(寫 sim_realized_outcome)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.dry_run or args.apply:
        return settle(apply=args.apply)
    return status()


if __name__ == "__main__":
    sys.exit(main())
