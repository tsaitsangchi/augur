#!/usr/bin/env python
"""歷史 as-of 既有族 V0／V1 驗証 — 共用當時 feature_values；不寫庫、不 promote、不開 NF。

🎯 這支在做什麼（白話）：對 D≤價頂，盤點截面 8 族 × H_TRACK 有無登錄（V0），
   若該窗標籤已實現（panel 之後 ≥H+1 個交易日）才 dry-run predict＋Spearman rank IC（V1）。
   默認 latest≤D 可能是同日 stamp（不是 OOS）。--oos 才用 latest < D。
   單 panel IC ≠確立、≠報酬％、≠可換冠。VECM／TCN／NB／RL／0812 NF 不在這裡開訓。

執行指令矩陣:
  python scripts/verify_asof_families.py --scan
  python scripts/verify_asof_families.py --date 2026-07-31
  python scripts/verify_asof_families.py --date 2026-08-07 --ic --oos
  python scripts/verify_asof_families.py --walk --oos
  python scripts/verify_asof_families.py --walk --oos --horizon 10 --limit 4
  python scripts/verify_asof_families.py --date 2026-08-18          # 價頂 V0（無已實現窗則略過 --ic）
  python scripts/check_asof_ready.py --fake-b3-date                # 該日 → rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import predict_asof
from augur.core import asof_ready, db
from augur.evaluation import label as label_mod
from augur.evaluation import metrics as ic_mod
from augur.models import registry


def _scores_from_rows(rows) -> dict:
    return {str(sid): float(sc) for _rk, sid, sc, _inp, _w in rows}


def _top_spread(scores: dict, rets: dict, top_frac: float = 0.1):
    """top-frac score 的已實現 log 報酬均 − 其餘均。單 panel；≠#14。"""
    common = [s for s in scores if s in rets]
    if len(common) < 10:
        return None
    common.sort(key=lambda s: scores[s], reverse=True)
    k = max(1, int(round(len(common) * top_frac)))
    top = common[:k]
    rest = common[k:]
    if not rest:
        return None
    mu_t = sum(rets[s] for s in top) / len(top)
    mu_r = sum(rets[s] for s in rest) / len(rest)
    return mu_t - mu_r


def inventory(cur, d: str) -> dict:
    snap = asof_ready.snapshot(cur, d)
    cells = asof_ready.family_cells(cur, d)
    other = asof_ready.other_lane_registry(cur)
    return {"snap": snap, "cells": cells, "other": other}


def run_ic(asof, horizons, families, *, oos: bool = False) -> list[dict]:
    """已實現窗：quiet dry-run predict → rank IC。零寫庫。"""
    out = []
    pick = registry.latest_before if oos else registry.latest
    for h in horizons:
        for fam in families:
            rec = {
                "family": fam,
                "horizon": int(h),
                "asof": str(asof),
                "oos": bool(oos),
            }
            reg = pick(fam, h, asof)
            if reg is None:
                rec.update(
                    status="no_model",
                    ic=None,
                    n=0,
                    model_id=None,
                    stamp="unknown",
                    model_asof=None,
                )
                out.append(rec)
                print(f"  {fam:<10} H{h:<3} no_model  (oos={oos})")
                continue
            rec["model_id"] = reg["model_id"]
            rec["model_asof"] = reg.get("asof_snapshot")
            rec["stamp"] = asof_ready.stamp_kind(rec["model_asof"], asof)
            rows = predict_asof.predict(
                h, fam, asof, top_n=0, dry_run=True, quiet=True,
                strict_before=oos,
            )
            if not rows:
                rec.update(status="predict_fail", ic=None, n=0)
                out.append(rec)
                continue
            scores = _scores_from_rows(rows)
            with db.connect() as conn:
                rets = label_mod.forward_returns(
                    conn, asof_ready.as_date(asof), list(scores), h,
                )
            labs = label_mod.cross_sectional_rank(rets)
            ic = ic_mod.rank_ic(scores, labs)
            spread = _top_spread(scores, rets)
            rec.update(
                status="ok",
                ic=None if ic is None else round(float(ic), 4),
                n=len([s for s in scores if s in labs]),
                spread=None if spread is None else round(float(spread), 4),
            )
            if rec["stamp"] == "same_day":
                rec["flag"] = "same_day"
            elif rec.get("ic") in (1.0, -1.0):
                rec["flag"] = "degenerate_ic"
            out.append(rec)
            print(
                f"  {fam:<10} H{h:<3} ic={rec['ic']!s:<8} n={rec['n']:<4} "
                f"stamp={rec['stamp']:<9} spread={rec['spread']!s:<8} {rec['model_id']}"
            )
            if rec.get("flag") == "same_day":
                print("    ⚠ 同日 stamp：不是 OOS；不採為勝（加 --oos）")
            elif rec.get("flag") == "degenerate_ic":
                print("    ⚠ 完美相關：不採為勝；須下一 panel 對照（#15）")
    return out


def _print_inventory(inv) -> int:
    snap = inv["snap"]
    st = snap["status"]
    print(
        f"V0 snapshot@{snap['asof']} status={st} price_max={snap['price_max']} "
        f"A格={snap['registry_a_cells']}/{snap['need_a_cells']} pack={snap['pack_complete']}"
    )
    if st == asof_ready.STATUS_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of")
        return asof_ready.RC_FAKE_B3
    if st == asof_ready.STATUS_NO_PRICE:
        return asof_ready.RC_NO_PRICE
    print(asof_ready.format_family_matrix(inv["cells"]))
    print("其他車道（n=0＝預期；禁當可重掃／禁 --apply）")
    print(asof_ready.format_other_lane_registry(inv["other"]))
    return int(snap["rc"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="歷史 as-of 截面族 V0／V1（唯讀）")
    ap.add_argument("--date", dest="asof", default=None, help="as-of 日 YYYY-MM-DD（不是字母 D）")
    ap.add_argument("--ic", action="store_true", help="對已實現窗算 rank IC（dry-run predict，不寫庫）")
    ap.add_argument(
        "--oos",
        action="store_true",
        help="只用 asof_snapshot < panel 的模型（排除同日 stamp）",
    )
    ap.add_argument(
        "--walk",
        action="store_true",
        help="對最近已實現該窗的多個 panel 跑 OOS IC（隱含 --oos --ic）",
    )
    ap.add_argument(
        "--horizon",
        type=int,
        default=5,
        help="--walk 用哪個 H（須在 H_TRACK；預設 5）",
    )
    ap.add_argument("--limit", type=int, default=5, help="--walk 最多幾個 panel（新→舊）")
    ap.add_argument("--scan", action="store_true", help="未齊 8×8 歷史日＋已實現窗（唯讀）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return asof_ready._selftest()
    if args.scan:
        with db.connect() as conn, conn.cursor() as cur:
            rows = asof_ready.scan_incomplete_asof(cur, limit=40)
            complete = asof_ready.scan_complete_asof(cur, limit=8)
            tip = asof_ready.taiex_price_max(cur)
            cal = label_mod.full_calendar(conn)
        print("price_max=%s" % (None if tip is None else tip.isoformat()))
        print("截面已齊: " + ", ".join(r["asof"] for r in complete))
        for r in rows:
            r["realized_h"] = asof_ready.realized_horizons(
                asof_ready.n_trading_days_after(cal, r["asof"], tip)
            )
        print(asof_ready.format_incomplete_scan(rows))
        print("補齊未齊 D：另 HIST-ASOF-apply | track=all（不覆寫方向臂）")
        print("OOS IC：python scripts/verify_asof_families.py --date 2026-08-07 --ic --oos")
        print("walk：python scripts/verify_asof_families.py --walk --oos")
        return 0
    if args.walk:
        args.oos = True
        args.ic = True
        need_h = int(args.horizon)
        if need_h not in asof_ready.H_TRACK:
            print(
                f"✗ --horizon 須為 H_TRACK={list(asof_ready.H_TRACK)}（收到 {need_h}）",
                file=sys.stderr,
            )
            return 2
        with db.connect() as conn, conn.cursor() as cur:
            tip = asof_ready.taiex_price_max(cur)
            cal = label_mod.full_calendar(conn)
            panels = asof_ready.scan_realized_panels(
                cur, cal, need_h=need_h, limit=max(1, int(args.limit)),
            )
        print(
            "V1 OOS walk H%d（stamp < panel；dry-run 未寫庫；IC≠確立≠報酬％） "
            "price_max=%s n=%d"
            % (need_h, None if tip is None else tip.isoformat(), len(panels))
        )
        if not panels:
            print("→ 無已實現 H%d panel（不是假綠）" % need_h)
            return 0
        all_rows = []
        for p in panels:
            print(f"── panel {p['asof']}  n_after={p['n_after']}  realized={list(p['realized_h'])}")
            chunk = run_ic(p["asof"], (need_h,), asof_ready.A_FAMILIES, oos=True)
            all_rows.extend(chunk)
        hint = asof_ready.walk_no_model_hint(need_h, all_rows)
        if hint:
            print("→ " + hint)
        payload = {
            "mode": "walk_oos_h%d" % need_h,
            "horizon": need_h,
            "price_max": None if tip is None else tip.isoformat(),
            "panels": [p["asof"] for p in panels],
            "rows": all_rows,
            "blocker": hint,
            "note": "OOS=stamp<panel；單 panel≠確立；dry-run 未寫庫",
        }
        path = "/tmp/v1-oos-walk-h%d.json" % need_h
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"JSON {path}")
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(args.asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    with db.connect() as conn, conn.cursor() as cur:
        inv = inventory(cur, args.asof)
        cal = label_mod.full_calendar(conn)
    snap = inv["snap"]
    rc = _print_inventory(inv)
    if rc in (asof_ready.RC_FAKE_B3, asof_ready.RC_NO_PRICE):
        return rc
    n_after = asof_ready.n_trading_days_after(cal, snap["asof"], snap["price_max"])
    ready_h = asof_ready.realized_horizons(n_after)
    print(f"panel 之後交易日={n_after}  已實現窗={list(ready_h) or '（無；IC 須等價蓋過 exit）'}")
    print("護欄: score／IC ≠ 報酬％；單 panel ≠確立；同日 stamp ≠ OOS；no-promote；不開 NF")
    if not args.ic:
        print(
            "下一槍 IC：python scripts/verify_asof_families.py --date %s --ic --oos"
            % snap["asof"]
        )
        return int(snap["rc"])
    if not ready_h:
        print("→ --ic 略過：此 D 尚無已實現窗（不是假綠）")
        return int(snap["rc"])
    mode = "OOS（stamp < panel）" if args.oos else "latest≤D（可能同日 stamp）"
    print(f"V1 rank IC {mode}；spread＝top10% 已實現 log 報酬−其餘")
    rows = run_ic(snap["asof"], ready_h, asof_ready.A_FAMILIES, oos=args.oos)
    payload = {
        "asof": snap["asof"],
        "price_max": snap["price_max"],
        "n_after": n_after,
        "realized_h": list(ready_h),
        "oos": bool(args.oos),
        "rows": rows,
        "note": "單 panel；IC≠確立；dry-run 未寫庫；same_day≠OOS",
    }
    tag = "oos" if args.oos else "latest"
    path = f"/tmp/v1-asof-{snap['asof']}-{tag}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"JSON {path}")
    return int(snap["rc"])


if __name__ == "__main__":
    sys.exit(main())
