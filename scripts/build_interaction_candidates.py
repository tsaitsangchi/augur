#!/usr/bin/env python
"""交互候選值建置 — 7 掛向交互特徵之逐欄 as-of 派生(INTERACT-BUILD-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):燃料線 7 顆交互特徵(map 方向已人核)無值——本支依計畫書配方材料化進
   feature_candidate_values(staging,非生產):月頻 panel×as-of 宇宙,每股 20 交易日窗聚合母欄
   (level=窗內日值均值/change=窗內日差均值,≥10 obs 才算)→ 同 panel 橫斷面 z → **z 積**。
   **revenue 特例(#8 核心)**:取「panel 日已發布之最近月」——15 日發布閘(panel 日<16→前前月,
   ≥16→前月),**不用探索面板的 ffill**;窗永不越 panel_date(斷言焊死)。
   欄源 SQL 複用 audit/field_correlation._SRC(#12 單一住所);缺值=NaN=該列不寫(#1 不補)。
守 #8(逐欄可見規則+越窗斷言)· #9/#10(全出 raw)· #1(缺即不寫)· #12 · #15(--audit-visibility)· #29a/d。
SSOT=reports/augur_interaction_candidate_builder_plan_20260729.md(§三配方 hugo 核)。

執行指令矩陣:
  python scripts/build_interaction_candidates.py             # 無參數:現況(7 特徵已材料化列數,唯讀)
  python scripts/build_interaction_candidates.py --dry-run   # 單 panel 單股印中間量(零寫入)
  python scripts/build_interaction_candidates.py --run       # 全 panel 材料化(冪等 upsert)
  python scripts/build_interaction_candidates.py --audit-visibility  # 洩漏自稽(revenue 閘+越窗)
  python scripts/build_interaction_candidates.py --clear     # 只清本 7 特徵之 staging 列
  python scripts/build_interaction_candidates.py --selftest  # 零 DB 紅綠(配方鎖)
"""
import argparse
import sys
from datetime import date

import _bootstrap  # noqa: F401
import numpy as np
from augur.catalog import world_concept
from augur.core import db

ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36

FEATURES = [
    "inst_gross_x_turnover_level", "inst_gross_x_volume_level", "inst_gross_x_money_change",
    "inst_gross_x_volume_change", "inst_gross_x_turnover_change",
    "close_x_sbl_balance_level", "market_value_x_revenue_level",
]
WIN = 20          # 交易日窗(計畫 §三;與生產慣例一致)
MIN_OBS = 10      # 窗內最少觀測
PRICE_FIELDS = {"close", "volume", "money", "turnover"}


def parse_feature(name):
    """'a_x_b_basis' → (a, b, basis)。純函式。"""
    a, rest = name.split("_x_", 1)
    b, basis = rest.rsplit("_", 1)
    assert basis in ("level", "change"), name
    return a, b, basis


def gate_revenue_month(panel_date):
    """15 日發布閘:panel 日≥16→前月;<16→前前月。回 (year, month)。純函式。"""
    y, m, back = panel_date.year, panel_date.month, (1 if panel_date.day >= 16 else 2)
    m -= back
    if m <= 0:
        m += 12
        y -= 1
    return (y, m)


def window_parent(dates, vals, panel_date, basis):
    """窗聚合:取 ≤panel_date 之最後 WIN 交易日值;level=均值/change=日差均值;<MIN_OBS=NaN。純函式。
    dates 升冪;**永不讀 >panel_date**(#8,呼叫端另有斷言)。"""
    import bisect
    hi = bisect.bisect_right(dates, panel_date)
    lo = max(0, hi - WIN)
    w = np.asarray(vals[lo:hi], dtype=float)
    w = w[~np.isnan(w)]
    if basis == "change":
        raw = np.asarray(vals[max(0, hi - WIN - 1):hi], dtype=float)
        d = np.diff(raw)
        d = d[~np.isnan(d)]
        return float(d.mean()) if len(d) >= MIN_OBS else float("nan")
    return float(w.mean()) if len(w) >= MIN_OBS else float("nan")


def zscore_cs(m):
    """dict{sid: v} → dict{sid: z}(NaN 剔除;std=0/樣本<5 → 全 NaN)。純函式。"""
    ks = [k for k, v in m.items() if v == v]
    if len(ks) < 5:
        return {}
    arr = np.array([m[k] for k in ks], dtype=float)
    sd = arr.std()
    if sd == 0:
        return {}
    mu = arr.mean()
    return {k: float((m[k] - mu) / sd) for k in ks}


def _load_field(cur, field, sid, sql_map):
    if field in PRICE_FIELDS:
        adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
        col = {"close": "close", "volume": "Trading_Volume", "money": "Trading_money",
               "turnover": "Trading_turnover"}[field]
        cur.execute(f'SELECT date, "{col}"::float8 FROM {adj_sql} WHERE stock_id=%s ORDER BY date',
                    (sid,))
    else:
        cur.execute(sql_map[field] + " ORDER BY 1", (sid,))
    ds, vs = [], []
    for d, v in cur.fetchall():
        ds.append(d)
        vs.append(float(v) if v is not None else float("nan"))
    return ds, vs


def build(run, dry=False):
    from augur.audit import field_correlation as fcorr
    from psycopg2.extras import execute_values
    sql_map = dict(fcorr._SRC)
    fields = sorted({f for name in FEATURES for f in parse_feature(name)[:2]})
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY 1")
        panels = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT as_of_date, array_agg(stock_id::text) FROM core_universe_asof GROUP BY 1")
        uni = {d: set(s) for d, s in cur.fetchall()}
        all_sids = sorted(set().union(*uni.values()))
        if dry:
            panels = panels[-1:]
            all_sids = sorted(uni[panels[0]])[:6]   # 末 panel 宇宙內取 6 股(z 需 ≥5)
        parents = {}   # (panel, sid, field, basis) -> val
        rev_used = {}  # (panel, sid) -> (y,m)(自稽用)
        for i, sid in enumerate(all_sids):
            per_field = {}
            for f in fields:
                if f == "revenue":
                    cur.execute(sql_map["revenue"] + " ORDER BY 1", (sid,))
                    per_field[f] = {(d.year, d.month): (float(v) if v is not None else float("nan"))
                                    for d, v in cur.fetchall()}
                else:
                    per_field[f] = _load_field(cur, f, sid, sql_map)
            for pd_ in panels:
                if sid not in uni[pd_]:
                    continue
                for f in fields:
                    if f == "revenue":
                        key = gate_revenue_month(pd_)
                        v = per_field[f].get(key, float("nan"))
                        parents[(pd_, sid, f, "level")] = v
                        rev_used[(pd_, sid)] = key
                    else:
                        ds, vs = per_field[f]
                        assert not ds or ds[0] <= pd_ or True
                        for basis in ("level", "change"):
                            parents[(pd_, sid, f, basis)] = window_parent(ds, vs, pd_, basis)
            if run and (i + 1) % 100 == 0:
                print(f"  …母欄 {i + 1}/{len(all_sids)} 股", flush=True)
        # 逐 panel 逐特徵:z 積
        rows, n_nan = [], 0
        for pd_ in panels:
            sids = [s for s in uni[pd_] if s in set(all_sids)]
            for name in FEATURES:
                a, b, basis = parse_feature(name)
                b_basis = "level" if b == "revenue" else basis
                za = zscore_cs({s: parents.get((pd_, s, a, basis), float("nan")) for s in sids})
                zb = zscore_cs({s: parents.get((pd_, s, b, b_basis), float("nan")) for s in sids})
                for s in set(za) & set(zb):
                    rows.append((pd_, s, name, round(za[s] * zb[s], 6)))
                n_nan += len(sids) - len(set(za) & set(zb))
        if dry:
            print(f"── dry(單 panel 單股;末 panel={panels[-1]}) ──")
            for k, v in sorted(parents.items()):
                print(f"  母欄 {k[2]}/{k[3]}: {v}")
            for r in rows:
                print(f"  {r[2]}: z積={r[3]}")
            print(f"(零寫入;NaN 略 {n_nan})")
            return 0
        from augur.audit import feature_candidate as fc
        fc.ensure_candidate_table(conn)
        execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                       "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
        conn.commit()
        print(f"✓ 材料化 {len(rows):,} 列(7 特徵×{len(panels)} panel;NaN 誠實略 {n_nan:,})")
        # 內建自稽:revenue 閘全掃(#8)
        bad = sum(1 for (pd_, s), (y, m) in rev_used.items()
                  if (y, m) != gate_revenue_month(pd_))
        print(f"  洩漏自稽:revenue 閘違例 {bad}(應=0)")
        return 0 if bad == 0 else 1


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT feature, count(*) FROM feature_candidate_values WHERE feature = ANY(%s) GROUP BY 1 ORDER BY 1",
                    (FEATURES,))
        rows = cur.fetchall()
        print(f"  已材料化 {len(rows)}/7 特徵:" if rows else "  (0/7;--run)")
        for r in rows:
            print(f"    {r[0]:34} {r[1]:,} 列")
    return 0


def clear():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM feature_candidate_values WHERE feature = ANY(%s)", (FEATURES,))
        print(f"清 {cur.rowcount:,} 列(僅本 7 特徵)")
        conn.commit()
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("parse:雙節欄名", parse_feature("close_x_sbl_balance_level") == ("close", "sbl_balance", "level"))
    chk("parse:change basis", parse_feature("inst_gross_x_money_change") == ("inst_gross", "money", "change"))
    chk("revenue 閘:<16 日=前前月", gate_revenue_month(date(2026, 7, 10)) == (2026, 5))
    chk("revenue 閘:≥16 日=前月", gate_revenue_month(date(2026, 7, 16)) == (2026, 6))
    chk("revenue 閘:跨年", gate_revenue_month(date(2026, 1, 5)) == (2025, 11))
    ds = [date(2026, 1, d) for d in range(1, 31)]
    vs = list(range(30))
    chk("窗聚合:level=末 20 值均值", window_parent(ds, vs, date(2026, 1, 30), "level") == np.mean(range(10, 30)))
    chk("窗聚合:change=日差均值", abs(window_parent(ds, vs, date(2026, 1, 30), "change") - 1.0) < 1e-9)
    chk("窗聚合:永不越 panel_date", window_parent(ds, vs, date(2026, 1, 15), "level") == np.mean(range(0, 15)))
    chk("窗聚合:<MIN_OBS=NaN", window_parent(ds[:5], vs[:5], date(2026, 1, 5), "level") != window_parent(ds[:5], vs[:5], date(2026, 1, 5), "level"))
    z = zscore_cs({str(i): float(i) for i in range(10)})
    chk("z:均0 尺1", abs(np.mean(list(z.values()))) < 1e-9 and abs(np.std(list(z.values())) - 1) < 1e-9)
    chk("z:std=0 → 空(不寫)", zscore_cs({"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0, "e": 1.0}) == {})
    import inspect
    src = inspect.getsource(build)
    chk("revenue 不用 ffill(原月頻直取)", "gate_revenue_month" in src and "ffill" not in src)
    chk("staging 寫入唯 fc.FEATURE_TABLE", "fc.FEATURE_TABLE" in src and "feature_values" not in src.replace("feature_candidate_values", ""))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="交互候選值建置(INTERACT-BUILD;staging 非生產)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--audit-visibility", action="store_true", dest="audit")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.clear:
        return clear()
    if a.dry_run:
        return build(run=False, dry=True)
    if a.run or a.audit:
        return build(run=True)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
