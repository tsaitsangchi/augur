#!/usr/bin/env python3
"""🎯 TWEVO run 22 觀察帳——I5B 首次生效點之前置快照＋隔晨四／五項機械驗收（M-T6）。

守原則 #15（觀察數字皆真 query）· #28（零 API／不取 heavy_slot）· #29a/d ·
M-T5（本支唯讀；永不 `--allow-apply`、永不手動搶 slot）。

SSOT：`ops/RUNBOOK-20260803-night.md` T-22:5x／隔晨；
`reports/augur_optimization_master_plan_20260803.md` 第 8 步。

  〔前置〕`--prerun`：把 `pending_auto` 全集 export 到 CSV，並印基線計數。
  〔隔晨〕`--morning`：五項機械檢查 → rc=0 全過／rc=1 有紅；可 `--write-audit`。

執行指令矩陣
------------
    python3 scripts/observe_twevo_run22.py                 # 無參數＝印用途＋基線現況（唯讀）
    python3 scripts/observe_twevo_run22.py --prerun        # 22:5x：寫 CSV 快照＋印基線
    python3 scripts/observe_twevo_run22.py --morning       # 結輪後／隔晨：五項驗收
    python3 scripts/observe_twevo_run22.py --morning --json
    python3 scripts/observe_twevo_run22.py --morning --write-audit
    python3 scripts/observe_twevo_run22.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO / "audits" / "prerun22_pending_snapshot_20260803.csv"
DEFAULT_AUDIT = REPO / "audits" / "OPT-W0-RUN22-20260803.md"
EXPECTED_NEXT_RUN = 22


def morning_verdict(snap: dict) -> dict:
    """五項驗收純函式（master 第 8 步）。回傳 checks＋ok。"""
    status = snap.get("latest_run_status")
    latest_id = snap.get("latest_run_id")
    n_sup = int(snap.get("n_superseded") or 0)
    pending = snap.get("pending_by_run") or {}
    if pending:
        pending_ok = set(int(k) for k in pending) == {EXPECTED_NEXT_RUN}
    else:
        pending_ok = True
    basis = snap.get("gain_basis")
    gain_ok = basis is not None and str(basis) != "incomparable"
    n_apply = int(snap.get("apply_log_new_since_prerun") or 0)
    apply_ok = n_apply == 0

    checks = [
        ("① latest evolution_run status=succeeded 且 run_id=22",
         status == "succeeded" and latest_id == EXPECTED_NEXT_RUN),
        ("② superseded 列 > 0（I5B 首次）", n_sup > 0),
        ("③ pending_auto 全屬 run 22（或 0 列）", pending_ok),
        ("④ 最新 ledger gain basis ≠ incomparable", gain_ok),
        ("⑤ evolution_apply_log 無偷跑新增（相對窗）", apply_ok),
    ]
    return {"checks": checks, "ok": all(c[1] for c in checks)}


def _baseline(cur) -> dict:
    cur.execute(
        "SELECT count(*), coalesce(min(run_id),0), coalesce(max(run_id),0) "
        "FROM promotion_queue WHERE queue_status='pending_auto'"
    )
    n, mn, mx = cur.fetchone()
    cur.execute(
        "SELECT run_id, count(*) FROM promotion_queue "
        "WHERE queue_status='pending_auto' GROUP BY 1 ORDER BY 1"
    )
    by_run = {int(r[0]): int(r[1]) for r in cur.fetchall()}
    cur.execute(
        "SELECT count(*) FROM promotion_queue WHERE queue_status='superseded'"
    )
    n_sup = cur.fetchone()[0]
    cur.execute(
        "SELECT run_id, status FROM evolution_run ORDER BY run_id DESC LIMIT 1"
    )
    row = cur.fetchone()
    return {
        "n_pending_auto": int(n),
        "pending_run_min": int(mn),
        "pending_run_max": int(mx),
        "pending_by_run": by_run,
        "n_superseded": int(n_sup),
        "latest_run_id": int(row[0]) if row else None,
        "latest_run_status": row[1] if row else None,
    }


def _prerun(path: Path) -> int:
    from augur.core import db

    path.parent.mkdir(parents=True, exist_ok=True)
    with db.connect() as conn, conn.cursor() as cur:
        base = _baseline(cur)
        cur.execute(
            "SELECT queue_id, run_id, feature, action, queue_status "
            "FROM promotion_queue WHERE queue_status='pending_auto' "
            "ORDER BY queue_id"
        )
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print("── M-T6 prerun 快照（I5B 基線）──")
    print(f"  寫入：{path}（{len(rows)} 列）")
    print(f"  pending_auto={base['n_pending_auto']} by_run={base['pending_by_run']}")
    print(f"  superseded={base['n_superseded']}；最新 evolution_run="
          f"{base['latest_run_id']}/{base['latest_run_status']}")
    if base["n_pending_auto"] and set(base["pending_by_run"]) != {21}:
        print("  ⚠ 預期 run 21 全集；現況 by_run 異形——照存，隔晨對照以本檔為準")
    print("  紀律：23:00 後勿改 evolution driver、勿 --allow-apply、勿搶 heavy_slot")
    return 0


def _morning_scan(conn, *, apply_since: datetime | None) -> dict:
    with conn.cursor() as cur:
        snap = _baseline(cur)
        cur.execute(
            "SELECT gain_evidence->>'basis' FROM evolution_iteration_ledger "
            "ORDER BY opened_at DESC NULLS LAST LIMIT 1"
        )
        r = cur.fetchone()
        snap["gain_basis"] = r[0] if r else None
        if apply_since is not None:
            cur.execute(
                "SELECT count(*) FROM evolution_apply_log WHERE applied_at >= %s",
                (apply_since,),
            )
        else:
            cur.execute(
                "SELECT count(*) FROM evolution_apply_log "
                "WHERE applied_at::date = CURRENT_DATE"
            )
        snap["apply_log_new_since_prerun"] = int(cur.fetchone()[0])
        # 別名：today 窗
        snap["apply_log_today_n"] = snap["apply_log_new_since_prerun"]
    return snap


def _write_audit(path: Path, snap: dict, verdict: dict, prerun_csv: Path) -> None:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    lines = [
        "# OPT-W0-RUN22 觀察帳（2026-08-03）",
        "",
        "> 位階：[I] · M-T6／runbook T-22:5x＋隔晨 · **零人工搶 slot、零 --allow-apply**",
        f"> 寫入：{now}",
        "",
        "## 前置快照",
        "",
        f"- CSV：`{prerun_csv.relative_to(REPO) if prerun_csv.exists() else prerun_csv}`",
        "",
        "## 隔晨機械五項",
        "",
        "| # | 條件 | 結果 |",
        "|---|---|---|",
    ]
    for name, ok in verdict["checks"]:
        lines.append(f"| {name} | {'✓' if ok else '✗'} |")
    lines += [
        "",
        "## 現查數字",
        "",
        "```json",
        json.dumps(snap, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
        f"**總評**：{'全綠' if verdict['ok'] else '有紅——對照 runbook「不對就停」'}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  寫入 audit：{path}")


def _morning(*, as_json=False, write_audit=False, apply_since=None) -> int:
    from augur.core import db

    since = None
    if apply_since:
        since = datetime.fromisoformat(apply_since)
    with db.connect() as conn:
        snap = _morning_scan(conn, apply_since=since)
    # pending_by_run keys for pure fn
    snap_for_v = dict(snap)
    verdict = morning_verdict(snap_for_v)
    out = {"snap": snap, "verdict": verdict}
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    else:
        print("── M-T6 morning 驗收（run 22／I5B）──")
        print(f"  latest_run={snap['latest_run_id']}/{snap['latest_run_status']}")
        print(f"  superseded={snap['n_superseded']}；pending={snap['pending_by_run']}")
        print(f"  gain_basis={snap['gain_basis']!r}；apply_log_窗內新增="
              f"{snap['apply_log_new_since_prerun']}")
        for name, ok in verdict["checks"]:
            print(f"  {'✓' if ok else '✗'} {name}")
        print("  → " + ("全綠 rc=0" if verdict["ok"] else "**有紅** rc=1——停手回報，勿繞閘"))
    if write_audit:
        _write_audit(DEFAULT_AUDIT, snap, verdict, DEFAULT_CSV)
    return 0 if verdict["ok"] else 1


def _status() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        base = _baseline(cur)
    print("── M-T6 現況（唯讀；未寫檔）──")
    print(f"  pending_auto={base['n_pending_auto']} by_run={base['pending_by_run']}")
    print(f"  superseded={base['n_superseded']}；最新 run="
          f"{base['latest_run_id']}/{base['latest_run_status']}")
    print(f"  prerun CSV 目標：{DEFAULT_CSV}")
    print("  下一步：22:5x → --prerun；結輪後 → --morning [--write-audit]")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    good = morning_verdict({
        "latest_run_status": "succeeded",
        "latest_run_id": 22,
        "n_superseded": 5,
        "n_pending_auto": 3,
        "pending_by_run": {22: 3},
        "gain_basis": "delta_ic",
        "apply_log_new_since_prerun": 0,
    })
    chk("理想隔晨 → ok", good["ok"] is True)
    bad_i5b = morning_verdict({
        "latest_run_status": "succeeded",
        "latest_run_id": 22,
        "n_superseded": 0,
        "n_pending_auto": 0,
        "pending_by_run": {},
        "gain_basis": "delta_ic",
        "apply_log_new_since_prerun": 0,
    })
    chk("superseded=0 → 紅（I5B 未生效）", bad_i5b["ok"] is False)
    bad_gain = morning_verdict({
        "latest_run_status": "succeeded",
        "latest_run_id": 22,
        "n_superseded": 1,
        "n_pending_auto": 0,
        "pending_by_run": {},
        "gain_basis": "incomparable",
        "apply_log_new_since_prerun": 0,
    })
    chk("gain incomparable → 紅", bad_gain["ok"] is False)
    bad_pending = morning_verdict({
        "latest_run_status": "succeeded",
        "latest_run_id": 22,
        "n_superseded": 1,
        "n_pending_auto": 17,
        "pending_by_run": {21: 17},
        "gain_basis": "delta_ic",
        "apply_log_new_since_prerun": 0,
    })
    chk("pending 仍全 run 21 → 紅", bad_pending["ok"] is False)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M-T6 TWEVO run22 觀察帳（唯讀）")
    ap.add_argument("--prerun", action="store_true", help="22:5x 寫 pending_auto CSV")
    ap.add_argument("--morning", action="store_true", help="結輪／隔晨五項驗收")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-audit", action="store_true")
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--apply-since", help="apply_log 計數下界 ISO（預設＝今日）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.prerun:
        return _prerun(a.csv)
    if a.morning:
        return _morning(as_json=a.json, write_audit=a.write_audit,
                        apply_since=a.apply_since)
    return _status()


if __name__ == "__main__":
    sys.exit(main())
