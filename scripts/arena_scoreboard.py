#!/usr/bin/env python
"""擂台計分板 — review 級唯讀計分+futility 判停(arena plan §2.4;非裁決、非交易訊號)。

🎯 這支在做什麼(白話):逐候選算 滾動 hit vs 全局多數類基線、Brier、缺席率、unsettleable 率——
   全部 **review 級・觀察中・非裁決・非交易訊號**(輸出必含此固定字串;--check-report=A3 驗收之
   機械斷言)。futility 判停(§2.4 新閉集,取代誤植的 decay 語意):讀 direction_arena_policy 凍結
   閾值(**無列=policy 未凍結、判停停用**,誠實印出、不裁),excess(hit−基線)單邊 95% 信賴上界<0
   →suspected_futility,連續 2 輪→confirmed_stop_entries=**只建議停出新預測**(ledger 留家族、
   不除名——除名=倖存者 K、FWER 失效,審查 S1)。裁決效力=零:gate 判決唯 direction_gate evaluate。

守 #9(數字全出自 DB query)· #15(固定字串機械斷言非自律)· #28(本地零 usage)· #29a/d。
   SSOT=reports/augur_direction_live_arena_plan_20260711.md §2.4。

執行指令矩陣:
  python scripts/arena_scoreboard.py                        # 無參數:計分板(唯讀;含 review 級字串)
  python scripts/arena_scoreboard.py --out report_2026m8.txt  # 計分板寫檔(月報)
  python scripts/arena_scoreboard.py --judge                # futility 判停(policy 未凍結=停用;觸發寫 verdict)
  python scripts/arena_scoreboard.py --check-report report_2026m8.txt  # A3 驗收:斷言含字串集(exit 0/1)
"""
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import _bootstrap  # noqa: F401
from augur.core import db

FIXED = "review 級・觀察中・非裁決・非交易訊號"
TOKENS = ("review 級", "觀察中", "非裁決", "非交易訊號")
ROLL_DATES = 20          # 滾動窗=近 20 個出手日(display only)
POLICY_KEYS = ("futility_min_clusters", "futility_z")   # A2 凍結;缺任一=判停停用
TAIPEI = ZoneInfo("Asia/Taipei")


def _load(cur):
    """候選+ledger 全量(review 級資料量小);表未建回 None。"""
    cur.execute("SELECT to_regclass('public.direction_arena_prediction'), "
                "to_regclass('public.direction_arena_candidate')")
    if not all(cur.fetchone()):
        return None
    cur.execute("SELECT model_key, team, track, status FROM direction_arena_candidate ORDER BY model_key")
    cands = cur.fetchall()
    cur.execute("SELECT model_key, target_id, pred_date, horizon_td, p_up, y_up, settle_mode, settled_at "
                "FROM direction_arena_prediction")
    preds = cur.fetchall()
    return cands, preds


def _majority(preds):
    """全局多數類:distinct (target,pred_date,horizon) 已評分結果之多數(去多模型重複計數)。"""
    seen = {}
    for mk, tid, pd_, h, p, y, sm, sa in preds:
        if y is not None:
            seen[(tid, pd_, h)] = y
    if not seen:
        return None, None
    up = sum(seen.values()) / len(seen)
    return (1 if up >= 0.5 else 0), max(up, 1 - up)


def _per_model(preds, maj):
    """逐候選聚合:hit/滾動 hit/Brier/unsettleable 率/逐出手日 excess clusters。"""
    out = {}
    for mk, tid, pd_, h, p, y, sm, sa in preds:
        m = out.setdefault(mk, {"n": 0, "settled": 0, "unsettleable": 0, "dates": set(),
                                "by_date": {}, "brier": [], "horizons": set()})
        m["n"] += 1
        m["dates"].add(pd_)
        m["horizons"].add(h)
        if sa is not None:
            m["settled"] += 1
        if sm == "unsettleable":
            m["unsettleable"] += 1
        if y is not None:
            hit = 1 if (1 if p > 0.5 else 0) == y else 0
            base = 1 if y == maj else 0
            m["by_date"].setdefault(pd_, []).append((hit, base))
            m["brier"].append((p - y) ** 2)
    return out


def _clusters(m):
    """逐出手日 excess(hit−基線)cluster 序列(升冪)。"""
    return [(d, sum(h for h, b in v) / len(v) - sum(b for h, b in v) / len(v))
            for d, v in sorted(m["by_date"].items())]


def _futility_stats(m, z):
    cl = [e for _, e in _clusters(m)]
    n = len(cl)
    if n < 2:
        return {"n_clusters": n, "mean_excess": cl[0] if cl else None, "upper95": None}
    mean = sum(cl) / n
    sd = math.sqrt(sum((e - mean) ** 2 for e in cl) / (n - 1))
    return {"n_clusters": n, "mean_excess": mean, "upper95": mean + z * sd / math.sqrt(n)}


def _report(cands, preds):
    maj, base = _majority(preds)
    lines = [f"擂台計分板|定位:{FIXED}",
             f"(裁決效力=零;gate 判決唯 direction_gate evaluate。全局多數類基線 hit="
             f"{'—' if base is None else f'{base:.3f}(多數類={maj})'})"]
    if not cands:
        lines.append("(擂台尚未開賽:candidate 0 列)")
    models = _per_model(preds, maj)
    all_dates_by_h = {}
    for mk, tid, pd_, h, *_ in preds:
        all_dates_by_h.setdefault(h, set()).add(pd_)
    for mk, team, track, st in cands:
        m = models.get(mk)
        if not m:
            lines.append(f"  {mk:<22} {team:<8} {track} [{st}] 出手 0(尚無對局列)")
            continue
        hits = [h for v in m["by_date"].values() for h, b in v]
        hit = sum(hits) / len(hits) if hits else None
        roll_dates = sorted(m["by_date"])[-ROLL_DATES:]
        rhits = [h for d in roll_dates for h, b in m["by_date"][d]]
        rhit = sum(rhits) / len(rhits) if rhits else None
        brier = sum(m["brier"]) / len(m["brier"]) if m["brier"] else None
        expect = sum(len(all_dates_by_h.get(h, set())) for h in m["horizons"])
        own = sum(len(all_dates_by_h.get(h, set()) & m["dates"]) for h in m["horizons"])
        absent = 1 - own / expect if expect else None
        uns = m["unsettleable"] / m["settled"] if m["settled"] else None
        fmt = lambda v, p="{:.3f}": "—" if v is None else p.format(v)
        lines.append(f"  {mk:<22} {team:<8} {track} [{st}] 出手 {m['n']}(已結算 {m['settled']})|"
                     f"hit 全期 {fmt(hit)}/近{ROLL_DATES}日 {fmt(rhit)} vs 基線 {fmt(base)}|"
                     f"Brier {fmt(brier, '{:.4f}')}|缺席率 {fmt(absent, '{:.1%}')}|"
                     f"unsettleable {fmt(uns, '{:.1%}')}")
    lines.append(f"—— 本表 {FIXED};數字全出自 direction_arena_prediction 實查(#9)。")
    return "\n".join(lines)


def judge():
    """futility 判停:policy 未凍結=停用;觸發=寫 direction_arena_verdict(冪等,同日重跑不覆寫)。"""
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            data = _load(cur)
            if data is None:
                print("(表未建;先 migrate_direction_arena_ddl.py --run)")
                return 0
            cands, preds = data
            cur.execute("SELECT to_regclass('public.direction_arena_policy')")
            policy = {}
            if cur.fetchone()[0]:
                cur.execute("SELECT policy_key, threshold FROM direction_arena_policy")
                policy = dict(cur.fetchall())
        print(f"futility 判停|定位:{FIXED}")
        missing = [k for k in POLICY_KEYS if k not in policy]
        if not policy or missing:
            print(f"policy 未凍結、判停停用(direction_arena_policy 無列或缺 {missing or POLICY_KEYS};A2 凍結後啟用)")
            return 0
        min_cl, z = int(policy["futility_min_clusters"]), float(policy["futility_z"])
        maj, _ = _majority(preds)
        models = _per_model(preds, maj)
        today = datetime.now(TAIPEI).date()
        with db.transaction(conn) as cur:
            for mk in sorted(models):
                st = _futility_stats(models[mk], z)
                triggered = (st["n_clusters"] >= min_cl and st["upper95"] is not None and st["upper95"] < 0)
                cur.execute("SELECT state FROM direction_arena_verdict WHERE model_key=%s AND as_of_date<%s "
                            "ORDER BY as_of_date DESC LIMIT 1", (mk, today))
                prev = (cur.fetchone() or [None])[0]
                state = ("confirmed_stop_entries" if triggered and prev in
                         ("suspected_futility", "confirmed_stop_entries")
                         else "suspected_futility" if triggered else "observing")
                snap = dict(st, majority_class=maj, futility_min_clusters=min_cl, futility_z=z, prev_state=prev)
                cur.execute("INSERT INTO direction_arena_verdict (as_of_date, model_key, state, metric_snapshot, "
                            "threshold_source) VALUES (%s,%s,%s,%s,'direction_arena_policy') "
                            "ON CONFLICT (as_of_date, model_key) DO NOTHING",
                            (today, mk, state, json.dumps(snap, default=str)))
                up = "—" if st["upper95"] is None else f"{st['upper95']:+.4f}"
                print(f"  {mk:<22} clusters={st['n_clusters']} excess 上界95={up} → {state}")
        print("(confirmed_stop_entries=僅建議停出新預測;既有 ledger 全數留家族入 gate,不除名。)")
    return 0


def check_report(path):
    p = Path(path)
    if not p.exists():
        print(f"✗ 檔不存在:{path}")
        return 1
    text = p.read_text(encoding="utf-8", errors="replace")
    missing = [s for s in (FIXED,) + TOKENS if s not in text]
    for s in missing:
        print(f"✗ 缺字串:「{s}」")
    print("✓ check-report 過:review 級字串集齊備" if not missing else f"✗ check-report 不過({len(missing)} 缺)")
    return 0 if not missing else 1


def main():
    ap = argparse.ArgumentParser(description="擂台計分板(review 級、非裁決)+futility 判停")
    ap.add_argument("--out", help="計分板寫檔(月報)")
    ap.add_argument("--judge", action="store_true", help="futility 判停(觸發寫 verdict)")
    ap.add_argument("--check-report", dest="check", help="斷言檔含 review 級字串集(A3 驗收)")
    args = ap.parse_args()
    if args.check:
        return check_report(args.check)
    if args.judge:
        return judge()
    with db.connect() as conn, db.transaction(conn) as cur:
        data = _load(cur)
    if data is None:
        print(f"(表未建;先 migrate_direction_arena_ddl.py --run)|定位:{FIXED}")
        return 0
    text = _report(*data)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"→ 已寫 {args.out}")
    else:
        print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
