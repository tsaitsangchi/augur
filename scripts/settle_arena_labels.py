#!/usr/bin/env python
"""擂台結算 — 以已實現交易日動態判定 label 日,冪等結算 direction_arena_prediction(arena plan §2.3/§5)。

🎯 這支在做什麼(白話):讀 ledger 未結算列,用 TaiwanStockPriceAdj **已實現**交易日曆(TAIEX 錨)數出
   「pred_date 後第 horizon_td 個交易日」=實際 label 日(未來日曆不可知、label_due_est 僅排程提示;F3)。
   realized_ret=close(label)/close(pred)−1、y_up=(ret>0)。停牌分支:label 日無成交且市場日曆已過
   label+7 日→settle_mode='last_trade' 用最後成交價;最後成交距 label 超 30 日→'unsettleable' 不填
   y_up 只標記(標的消失的誠實,防 live 倖存者偏差)。寫入前兩道 fail-closed 閘:
   ①逐列斷言 created_at(台北日)<label 日(真未來完整性;違者整批禁結算 exit 1);
   ②PriceAdj factor(adj close/raw close)於本批 [pred,label] 窗**單調性檢核**——拼接損傷(F2 實錘
   15 檔)factor 會回落;不過即 exit 1 禁結算、整批零寫入(處置=修 writer+重抓 #12,非 hand-patch)。
   冪等:只挑 settled_at IS NULL;DDL trigger③ 機械保證結算欄唯 NULL→值一次。

守 #6(冪等可重跑)· #8(label=已實現才結、不猜未來日曆)· #12(損傷不 hand-patch)· #15(factor 機械
   檢核非自律)· #28(本地零 usage)· #29a/d。SSOT=reports/augur_direction_live_arena_plan_20260711.md §2.3/§5。

執行指令矩陣:
  python scripts/settle_arena_labels.py                # 無參數:現況(唯讀:未結算/已結算分佈)
  python scripts/settle_arena_labels.py --run          # 冪等結算(兩閘不過=exit 1 零寫入)
  python scripts/settle_arena_labels.py --check-factor # 只跑 factor 單調性檢核(唯讀診斷,零寫入)
"""
import argparse
import sys
from bisect import bisect_left, bisect_right
from datetime import timedelta
from zoneinfo import ZoneInfo

import _bootstrap  # noqa: F401
from augur.core import db

TAIPEI = ZoneInfo("Asia/Taipei")
WAIT_DAYS = 7            # 停牌觀察窗:市場日曆過 label+7 日仍無成交才進停牌分支(防資料延遲誤判)
UNSETTLE_GAP_DAYS = 30   # 最後成交距 label 超 30 日=unsettleable(不填 y_up 只標記)
FACTOR_TOL = 0.005       # factor 相對回落容忍:2 位小數捨入雜訊上界;拼接損傷典型 >1%
LOOKBACK_DAYS = 40       # 價格抓取下緣緩衝(涵蓋 pred 前最後成交與 30 日 gap 判定)


def _prices(cur, table, targets, lo, hi):
    """{stock_id: (dates 升冪, closes)};close>0 濾停牌哨兵。table 僅來自本檔常數(非外部輸入)。"""
    cur.execute(f'SELECT stock_id, date, close::float8 FROM "{table}" WHERE stock_id = ANY(%s) '
                "AND date BETWEEN %s AND %s AND close > 0 ORDER BY stock_id, date", (targets, lo, hi))
    out = {}
    for sid, d, c in cur.fetchall():
        out.setdefault(sid, ([], []))
        out[sid][0].append(d)
        out[sid][1].append(c)
    return out


def _last_le(series, d):
    """series 中 ≤ d 之最後一筆 (date, close);無則 (None, None)。"""
    i = bisect_right(series[0], d) - 1
    return (series[0][i], series[1][i]) if i >= 0 else (None, None)


def _at(series, d):
    """series 中恰於 d 之 close;無則 None。"""
    j = bisect_left(series[0], d)
    return series[1][j] if j < len(series[0]) and series[0][j] == d else None


def _classify(cur):
    """未結算列→逐列判定:回 (plans, pending 統計, 完整性違規, factor 檢核窗, 未結算總數)。
    plan=(model_key, target_id, pred_date, horizon_td, settle_mode, realized_ret|None)。"""
    cur.execute("SELECT model_key, target_id, pred_date, horizon_td, created_at "
                "FROM direction_arena_prediction WHERE settled_at IS NULL")
    rows = cur.fetchall()
    if not rows:
        return [], {}, [], {}, 0

    lo = min(r[2] for r in rows) - timedelta(days=LOOKBACK_DAYS)
    cur.execute('SELECT date FROM "TaiwanStockPriceAdj" WHERE stock_id=%s AND date >= %s ORDER BY date',
                ("TAIEX", lo))
    cal = [r[0] for r in cur.fetchall()]
    market_max = cal[-1] if cal else None

    realized, pending, violations = [], {}, []
    for mk, tid, pred, h, created in rows:
        li = bisect_right(cal, pred) + h - 1
        if not cal or li >= len(cal):
            pending["label 未實現(交易日未數滿)"] = pending.get("label 未實現(交易日未數滿)", 0) + 1
            continue
        label = cal[li]
        if created.astimezone(TAIPEI).date() >= label:   # 真未來完整性:出手須早於標籤實現首日
            violations.append((mk, tid, pred, h, created, label))
            continue
        realized.append((mk, tid, pred, h, label))
    if violations or not realized:
        return [], pending, violations, {}, len(rows)

    targets = sorted({r[1] for r in realized})
    hi = max(r[4] for r in realized)
    adj = _prices(cur, "TaiwanStockPriceAdj", targets, lo, hi)

    plans, windows = [], {}
    for mk, tid, pred, h, label in realized:
        ser = adj.get(tid, ([], []))
        _, pred_close = _last_le(ser, pred)
        label_close = _at(ser, label)
        if label_close is not None and pred_close is not None:
            plans.append((mk, tid, pred, h, "normal", label_close / pred_close - 1))
        elif market_max < label + timedelta(days=WAIT_DAYS):
            pending["停牌觀察中(label+7 日未過)"] = pending.get("停牌觀察中(label+7 日未過)", 0) + 1
            continue
        else:
            last_d, last_c = _last_le(ser, label)
            if (label_close is None and pred_close is not None and last_d is not None
                    and (label - last_d).days <= UNSETTLE_GAP_DAYS):
                plans.append((mk, tid, pred, h, "last_trade", last_c / pred_close - 1))
            else:
                plans.append((mk, tid, pred, h, "unsettleable", None))
        if plans and plans[-1][4] != "unsettleable" and plans[-1][:4] == (mk, tid, pred, h):
            w = windows.get(tid)
            windows[tid] = (min(w[0], pred), max(w[1], label)) if w else (pred, label)
    return plans, pending, [], windows, len(rows)


def _factor_check(cur, windows):
    """本批 [pred,label] 窗 adj/raw factor 單調性(時間升冪不得回落>TOL;拼接損傷=回落)。回違規列。"""
    if not windows:
        return [], 0
    targets = sorted(windows)
    lo, hi = min(w[0] for w in windows.values()), max(w[1] for w in windows.values())
    adj = _prices(cur, "TaiwanStockPriceAdj", targets, lo, hi)
    raw = _prices(cur, "TaiwanStockPrice", targets, lo, hi)
    viol, n_checked = [], 0
    for tid, (wlo, whi) in windows.items():
        a, r = adj.get(tid), raw.get(tid)
        if not a or not r:
            continue   # raw 缺=無從對照(資料缺口非損傷證據;誠實跳過並計數於摘要)
        rmap = dict(zip(r[0], r[1]))
        seq = [(d, c / rmap[d]) for d, c in zip(a[0], a[1]) if wlo <= d <= whi and d in rmap]
        if len(seq) >= 2:
            n_checked += 1
        for (d0, f0), (d1, f1) in zip(seq, seq[1:]):
            if f1 < f0 * (1 - FACTOR_TOL):
                viol.append((tid, d0, f0, d1, f1))
    return viol, n_checked


def settle(write):
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            plans, pending, violations, windows, n_unsettled = _classify(cur)
            factor_viol, n_checked = _factor_check(cur, windows)
        if n_unsettled == 0:
            print("無未結算列(冪等:無事可做)")
            return 0
        if violations:
            print(f"✗ 完整性斷言不過:{len(violations)} 列 created_at(台北日)≥label 日→整批禁結算(exit 1)")
            for mk, tid, pred, h, created, label in violations[:20]:
                print(f"  {mk} {tid} pred={pred} h={h} created={created} label={label}")
            return 1
        print(f"未結算 {n_unsettled} 列|可結算 {len(plans)}|pending {sum(pending.values())} "
              f"{dict(pending) if pending else ''}")
        print(f"factor 單調性檢核:{n_checked} 檔窗對照,違規 {len(factor_viol)}")
        if factor_viol:
            for tid, d0, f0, d1, f1 in factor_viol[:20]:
                print(f"  ✗ {tid} {d0}→{d1} factor {f0:.6f}→{f1:.6f}(回落>{FACTOR_TOL:.1%})")
            print("✗ factor 檢核不過→禁結算、整批零寫入(exit 1;處置=修 writer+重抓 #12,不 hand-patch)")
            return 1
        modes = {m: sum(1 for p in plans if p[4] == m) for m in ("normal", "last_trade", "unsettleable")}
        if not write:
            print(f"(唯讀診斷,未寫入)分佈:{modes}")
            return 0
        with db.transaction(conn) as cur:
            for mk, tid, pred, h, mode, ret in plans:
                y = None if ret is None else (1 if ret > 0 else 0)
                cur.execute("UPDATE direction_arena_prediction SET y_up=%s, realized_ret=%s, settle_mode=%s, "
                            "settled_at=now() WHERE model_key=%s AND target_id=%s AND pred_date=%s "
                            "AND horizon_td=%s AND settled_at IS NULL", (y, ret, mode, mk, tid, pred, h))
        print(f"✓ 結算完成:{modes}(trigger③ 保證唯 NULL→值一次;重跑冪等)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_prediction')")
        if not cur.fetchone()[0]:
            print("(表未建;先 migrate_direction_arena_ddl.py --run)")
        else:
            cur.execute("SELECT count(*), count(settled_at), "
                        "count(*) FILTER (WHERE settle_mode='normal'), "
                        "count(*) FILTER (WHERE settle_mode='last_trade'), "
                        "count(*) FILTER (WHERE settle_mode='unsettleable') FROM direction_arena_prediction")
            n, s, nm, lt, un = cur.fetchone()
            print(f"ledger {n} 列|已結算 {s}(normal {nm}/last_trade {lt}/unsettleable {un})|未結算 {n - s}")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


def main():
    ap = argparse.ArgumentParser(description="擂台結算:已實現交易日動態判 label+停牌分支+factor 檢核(fail-closed)")
    ap.add_argument("--run", action="store_true", help="冪等結算(寫 ledger 結算欄)")
    ap.add_argument("--check-factor", action="store_true", dest="factor", help="只跑 factor 檢核(唯讀)")
    args = ap.parse_args()
    if args.run or args.factor:
        return settle(write=args.run)
    return status()


if __name__ == "__main__":
    sys.exit(main())
