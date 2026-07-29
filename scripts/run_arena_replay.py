#!/usr/bin/env python
"""arena 歷史重演引擎 — 逐日 as-of 出單+即結,寫隔離 replay 帳本(REPLAY-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):對窗內每個 TAIEX 交易日 t:宇宙=最近 ≤t 之 core_universe_asof 快照、
   series=各股 ≤t 收盤(**切片即 as-of,越界斷言焊死**)→ adapter.predict(同 live 機具 #12)→
   立即用已知後續結算(label=TAIEX 日曆 t+h;同 live 三態:normal/last_trade(≤30d)/unsettleable)
   → 寫 direction_arena_replay(live 帳本零觸碰)。逐日 commit+PK 衝突跳過=resume-safe。
   R1 僅乾淨隊(規則式/逐日重訓,零預訓練=全期合法);預訓練外隊須 --allow-pretrained+合法窗
   (R3,發布日親驗後)——fail-closed 預設拒。
守 #8(切片 as-of+雙斷言+DB CHECK)· #9/#10(結算全出已實現價)· #12(複用 adapters)· #15 · #29a/d。
SSOT=reports/augur_arena_replay_plan_20260729.md;效力邊界 §二(live 門不吃 replay)。

執行指令矩陣:
  python scripts/run_arena_replay.py                    # 無參數:現況(各批進度,唯讀)
  python scripts/run_arena_replay.py --probe-one        # #25 單日單隊(majority)先行
  python scripts/run_arena_replay.py --model majority --from 2024-01-01 --to 2026-06-30 --run
  python scripts/run_arena_replay.py --model own_daily_rolling --from 2024-01-01 --to 2026-06-30 --run
  python scripts/run_arena_replay.py --selftest         # 零 DB 紅綠(結算三態/run_id 決定性/洩漏斷言)
"""
import argparse
import bisect
import hashlib
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

CLEAN_TEAMS = ("majority", "momentum_20", "mc_bootstrap", "own_daily_rolling")
H_TD = 5
UNSETTLE_GAP_DAYS = 30   # 同 settle_arena_labels 口徑
MIN_OBS = 120


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def replay_run_id(model, w_from, w_to, code7):
    """決定性批 id(同參同 id=resume 同批)。純函式。"""
    return "rp_" + hashlib.sha256(f"{model}|{w_from}|{w_to}|{code7}".encode()).hexdigest()[:12]


def settle_one(stock_dates, stock_close, pred_date, label_market_date):
    """同 live 三態結算。stock_dates 升冪;回 (settle_mode, label_close|None, label_date|None)。純函式。"""
    i = bisect.bisect_right(stock_dates, label_market_date) - 1
    if i < 0 or stock_dates[i] <= pred_date:
        return ("unsettleable", None, None)
    d = stock_dates[i]
    if d == label_market_date:
        return ("normal", stock_close[d], d)
    if (label_market_date - d).days <= UNSETTLE_GAP_DAYS:
        return ("last_trade", stock_close[d], d)
    return ("unsettleable", None, None)


def asof_slice(dates, closes, t):
    """≤t 切片;斷言不越界(#8)。純函式。"""
    hi = bisect.bisect_right(dates, t)
    out = closes[:hi]
    assert not dates[:hi] or dates[hi - 1] <= t
    return out


def run(model, w_from, w_to, allow_pretrained=False, probe=False):
    from augur.arena.adapters import REGISTRY
    from psycopg2.extras import execute_values
    if model not in CLEAN_TEAMS and not allow_pretrained:
        print(f"⛔ {model} 非乾淨隊(預訓練)——R3 合法窗親驗前 fail-closed 拒跑(--allow-pretrained+計畫 §三)")
        return 75
    if model not in REGISTRY:
        print(f"✗ {model} 無 adapter")
        return 1
    code7 = _git7()
    rid = replay_run_id(model, w_from, w_to, code7)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT date FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX' ORDER BY date")
        cal = [r[0] for r in cur.fetchall()]
        days = [d for d in cal if w_from <= d <= w_to]
        # label 須已實現:去尾 h 日
        days = [d for d in days if cal.index(d) + H_TD < len(cal)] if days else []
        if probe:
            days = days[-1:]
        if not days:
            print("(窗內無可結交易日)")
            return 1
        cur.execute("SELECT as_of_date, array_agg(stock_id::text) FROM core_universe_asof GROUP BY 1 ORDER BY 1")
        snaps = cur.fetchall()
        snap_dates = [s[0] for s in snaps]
        cur.execute("""SELECT stock_id, date, close FROM "TaiwanStockPriceAdj"
            WHERE date >= %s ORDER BY stock_id, date""", (w_from - timedelta(days=900),))
        sd, sc = {}, {}
        for sid, d_, c_ in cur.fetchall():
            sd.setdefault(sid, []).append(d_)
            sc.setdefault(sid, {})[d_] = float(c_)
        cur.execute("""SELECT date, price FROM "TaiwanStockTotalReturnIndex" WHERE stock_id='TAIEX'
            AND date >= %s ORDER BY date""", (w_from - timedelta(days=900),))
        taiex = cur.fetchall()
        cur.execute("""INSERT INTO arena_replay_run
            (replay_run_id, model_key, window_start, window_end, weights_cutoff_ok, code_sha, spec)
            VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (replay_run_id) DO NOTHING""",
            (rid, model, w_from, w_to, model in CLEAN_TEAMS, code7,
             '{"h": %d, "engine": "run_arena_replay v1"}' % H_TD))
        conn.commit()
        # resume:已寫日跳過
        cur.execute("""SELECT DISTINCT pred_date FROM direction_arena_replay
            WHERE replay_run_id=%s AND model_key=%s""", (rid, model))
        done = {r[0] for r in cur.fetchall()}
        todo = [d for d in days if d not in done]
        print(f"批 {rid} {model} {w_from}→{w_to}:{len(days)} 交易日(已 {len(done)}/續 {len(todo)})", flush=True)
        adapter = REGISTRY[model]()
        n = 0
        for k, t in enumerate(todo):
            si = bisect.bisect_right(snap_dates, t) - 1
            if si < 0:
                continue
            uni = set(snaps[si][1])
            series = {}
            for sid in uni:
                ds = sd.get(sid)
                if not ds:
                    continue
                hi = bisect.bisect_right(ds, t)
                if hi >= MIN_OBS and ds[hi - 1] == t:      # 當日有成交才出單(同 live 精神)
                    series[sid] = [sc[sid][d] for d in ds[:hi]]
            series["TAIEX"] = asof_slice([d for d, _ in taiex], [p for _, p in taiex], t)
            if len(series) < 50:
                continue
            label_market = cal[cal.index(t) + H_TD]
            out = adapter.predict(series, H_TD)
            rows = []
            for tgt, p in out.items():
                if tgt == "TAIEX" or tgt not in uni:
                    continue
                mode, lc, _ = settle_one(sd[tgt], sc[tgt], t, label_market)
                base = sc[tgt][t]
                if mode == "unsettleable":
                    rows.append((rid, model, tgt, t, H_TD, float(p), t, None, None, mode))
                else:
                    ret = lc / base - 1
                    rows.append((rid, model, tgt, t, H_TD, float(p), t, int(ret > 0), round(ret, 6), mode))
            if rows:
                execute_values(cur, """INSERT INTO direction_arena_replay
                    (replay_run_id, model_key, target_id, pred_date, horizon_td, p_up,
                     train_data_max_date, y_up, realized_ret, settle_mode)
                    VALUES %s ON CONFLICT DO NOTHING""", rows)
                conn.commit()
                n += len(rows)
            if probe:
                print(f"── #25 單日探測 {t}:{len(rows)} 筆(樣本 {rows[0] if rows else '無'})")
            elif (k + 1) % 20 == 0:
                print(f"  …{k + 1}/{len(todo)} 日({n:,} 列)", flush=True)
        print(f"✓ 批 {rid} 完:{n:,} 列入 replay 帳本(live 零觸碰)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_replay')")
        if cur.fetchone()[0] is None:
            print("  (表未建;migrate_arena_replay_ddl --apply)")
            return 0
        cur.execute("""SELECT model_key, count(DISTINCT pred_date), count(*),
                              count(*) FILTER (WHERE settle_mode='unsettleable')
                       FROM direction_arena_replay GROUP BY 1 ORDER BY 1""")
        for r in cur.fetchall():
            print(f"  {r[0]:20} {r[1]:,} 日 {r[2]:,} 列(unsettleable {r[3]:,})")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    ds = [date(2026, 1, d) for d in (5, 6, 7, 8, 9, 12)]
    cl = {d: 10.0 + i for i, d in enumerate(ds)}
    chk("結算 normal", settle_one(ds, cl, date(2026, 1, 5), date(2026, 1, 9)) == ("normal", 14.0, date(2026, 1, 9)))
    chk("結算 last_trade(停牌回溯 ≤30d)",
        settle_one(ds, cl, date(2026, 1, 5), date(2026, 1, 10))[0] == "last_trade")
    chk("結算 unsettleable(label 前無 >pred 成交)",
        settle_one(ds[:1], cl, date(2026, 1, 5), date(2026, 1, 9))[0] == "unsettleable")
    chk("run_id 決定性", replay_run_id("m", date(2024, 1, 1), date(2026, 6, 30), "abc")
        == replay_run_id("m", date(2024, 1, 1), date(2026, 6, 30), "abc"))
    chk("run_id 隨窗變", replay_run_id("m", date(2024, 1, 1), date(2026, 6, 30), "abc")
        != replay_run_id("m", date(2024, 1, 2), date(2026, 6, 30), "abc"))
    chk("as-of 切片不越界", asof_slice(ds, [cl[d] for d in ds], date(2026, 1, 8)) == [10.0, 11.0, 12.0, 13.0])
    import inspect
    src = inspect.getsource(run)
    chk("預訓練隊 fail-closed(R3 前拒)", "allow_pretrained" in src and "return 75" in src)
    chk("live 帳本零觸碰", "direction_arena_prediction" not in src)
    chk("resume:已寫日跳過+PK 衝突跳過", "DISTINCT pred_date" in src and "ON CONFLICT DO NOTHING" in src)
    chk("當日有成交才出單(同 live)", "ds[hi - 1] == t" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="arena 歷史重演引擎(隔離帳本;R1 乾淨隊)")
    ap.add_argument("--model")
    ap.add_argument("--from", dest="w_from")
    ap.add_argument("--to", dest="w_to")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--probe-one", action="store_true", dest="probe")
    ap.add_argument("--allow-pretrained", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.probe:
        return run("majority", date(2026, 5, 1), date(2026, 6, 30), probe=True)
    if a.run and a.model and a.w_from and a.w_to:
        return run(a.model, date.fromisoformat(a.w_from), date.fromisoformat(a.w_to),
                   allow_pretrained=a.allow_pretrained)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
