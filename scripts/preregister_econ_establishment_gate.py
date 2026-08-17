#!/usr/bin/env python
"""經濟確立閘預註冊 — 把 H60 主格「怎樣才算證明能賺錢」在跑數字前寫死。

🎯 這支在做什麼（白話）：E1 只插入一列
   `egate_H_60_ridge_LO_prodset_r17`（RankRidge × H60 long-only top10% 等權 ×
   現役 prodset × DSR≥0.95 × 雙宇宙 × live OOS K=4）。status＝preregistered。
   **不**順便立 H20／其他窗。approve 唯決策層人（TTY；本支有 --approve 但 E1 不准呼叫）。
   對齊 reports/augur_econ_prove_edge_plan_r17_20260817.md §5。

守 #15（先凍後跑）· #26（approve 唯人）· #12（判準單一住所＝本檔 CRITERIA）· #14（不改 verdict）。

執行指令矩陣:
  python scripts/preregister_econ_establishment_gate.py                 # 無參數:閘清單（唯讀）
  python scripts/preregister_econ_establishment_gate.py --preregister   # 插入 H60 主閘 draft
  python scripts/preregister_econ_establishment_gate.py --check         # 預設主閘 sha 覆算
  python scripts/preregister_econ_establishment_gate.py --check GATE    # 指定閘
  python scripts/preregister_econ_establishment_gate.py --approve GATE --approved-by NAME
      # 人親核（TTY；AI/非 TTY fail-closed）——E1 不准呼叫
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

GATE_ID = "egate_H_60_ridge_LO_prodset_r17"
FAMILY = "RankRidge"
HORIZON = 60
PURPOSE = (
    "#14 經濟確立主格：RankRidge H60 long-only top10% 等權、現役 prodset 必過；"
    "先凍後跑；evaluated_pass ≠ 改 econ_verdict_rule"
)


def _git7() -> str:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parent.parent),
            ).stdout.strip()
            or "unknown"
        )
    except OSError:
        return "unknown"


def _sha(c) -> str:
    return hashlib.sha256(
        json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()[:16]


def criteria() -> dict:
    """§5 凍結細胞＋AND 機械式。改此 dict＝改賭注；已核准後 trigger 拒寫入。"""
    return {
        "version": "econ_establishment_r17",
        "cell": {
            "family": FAMILY,
            "family_aliases": ["RankRidge", "B2_ridge", "ridge"],
            "horizon": HORIZON,
            "side": "long-only",
            "top_frac": 0.1,
            "weight": "equal",
            "ledger_weight": "LO",
            "cost": 0.00585,
            "cost_stress": 0.008775,
            "cost_stress_mult": 1.5,
            "sample_since_primary": "2014-01-01",
            "sample_since_robust": "2021-01-01",
            "universes": ["asof_incumbent", "pit_broad"],
            "feature_source_required": "prodset",
            "feature_source_control": "canonical",
            "seed": 42,
            "nonoverlap": "run_economic_eval._nonoverlap",
            "until_rule": "approve 當日最後已實現 H60 label 之 panel；禁未實現段",
        },
        "dsr": {
            "min": 0.95,
            "unit": "per-period",
            "forbid_annualized_bug": True,
            "n_source": "trial_ledger",
            "n_key": ["model", "horizon", "top_frac", "weight", "feats_hash", "cost"],
            "primary_dsr_cell": "prodset/since2014/asof_incumbent",
            "broad_dsr_disclosure": True,
        },
        "live_oos": {
            "k": 4,
            "origin_rule": "閘 freeze 後的出門 as-of 起算非重疊已實現持有",
            "overlap_forbidden": True,
        },
        "pass_and": [
            "net_sharpe(prodset, since2014, asof_incumbent) > bench_sharpe",
            "net_sharpe(prodset, since2014, pit_broad) > bench_sharpe",
            "net_sharpe(prodset, since2021, asof_incumbent) > bench_sharpe",
            "net_sharpe(prodset, since2021, pit_broad) > bench_sharpe",
            "dsr(per-period, N=ledger, primary_dsr_cell) >= 0.95",
            "1.5x cost 後 incumbent since2014 仍 net>bench",
            "live_oos 非重疊已實現期數 >= 4 且該子集 net>bench",
            "criteria_sha 未變",
        ],
        "fail_path": (
            "任一 AND 不過=evaluated_fail 留檔；econ_verdict_rule 保持 thin_unestablished；"
            "禁刪列；重試=另立新 gate、舊列 superseded；AI 禁 UPDATE established"
        ),
        "out_of_scope": {
            "no_revive_h20": True,
            "no_other_horizons": True,
            "no_direction_gate": True,
            "canonical_not_in_and": True,
            "evaluated_pass_does_not_write_verdict": True,
        },
        "plan_ref": "reports/augur_econ_prove_edge_plan_r17_20260817.md#§5",
    }


def _list(cur) -> None:
    cur.execute(
        "SELECT gate_id, horizon, family, status, criteria_sha, approved_by "
        "FROM econ_establishment_gate ORDER BY horizon, gate_id"
    )
    rows = cur.fetchall()
    if not rows:
        print("現況:econ_establishment_gate 零列（尚未 --preregister）")
        return
    for r in rows:
        print(f"  {r[0]}  h={r[1]}  {r[2]}  {r[3]}  sha={r[4]}  by={r[5]}")


def preregister() -> int:
    c = criteria()
    sha = _sha(c)
    git7 = _git7()
    payload = json.dumps(c, ensure_ascii=False)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT gate_id, status, criteria_sha, horizon FROM econ_establishment_gate"
        )
        existing = list(cur.fetchall())
        others = [r for r in existing if r[0] != GATE_ID]
        if others:
            conn.rollback()
            print("✗ 表內已有非主閘列（E1 只准 H60 一列）:")
            for r in others:
                print(f"    {r[0]} h={r[3]} {r[1]}")
            return 1
        hit = next((r for r in existing if r[0] == GATE_ID), None)
        if hit:
            if hit[1] != "preregistered":
                conn.rollback()
                print(f"✗ {GATE_ID} 已是 {hit[1]}，E1 不得覆寫")
                return 1
            if hit[2] != sha:
                conn.rollback()
                print(
                    f"✗ {GATE_ID} 已在且 sha 不同（DB={hit[2]} code={sha}）。"
                    "改賭注須 Steward 明示；本 GO 不覆寫"
                )
                return 1
            conn.rollback()
            print(f"✓ 已存在且 sha 一致:{GATE_ID} sha={sha}（冪等 no-op）")
            return 0
        cur.execute(
            """
            INSERT INTO econ_establishment_gate
              (gate_id, horizon, family, purpose, criteria, criteria_sha, git_sha, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                GATE_ID,
                HORIZON,
                FAMILY,
                PURPOSE,
                payload,
                sha,
                git7,
                "E1 draft；approve=E2 TTY；禁 H20／他窗；禁改 verdict",
            ),
        )
        conn.commit()
    print(f"✓ 預註冊 {GATE_ID}  status=preregistered  sha={sha}  git={git7}")
    print("  下一槍（另貼，TTY）:")
    print(
        "    python scripts/preregister_econ_establishment_gate.py "
        f"--approve {GATE_ID} --approved-by <名>"
    )
    return 0


def check(gate_id: str) -> int:
    code_sha = _sha(criteria())
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            "SELECT criteria, criteria_sha, status, approved_by, horizon, family "
            "FROM econ_establishment_gate WHERE gate_id=%s",
            (gate_id,),
        )
        row = cur.fetchone()
        cur.execute("SELECT count(*), count(*) FILTER (WHERE horizon<>60) FROM econ_establishment_gate")
        n_all, n_other = cur.fetchone()
        cur.execute("SELECT count(*) FROM direction_gate")
        n_dgate = cur.fetchone()[0]
        cur.execute("SELECT horizon, verdict FROM econ_verdict_rule WHERE horizon IN (20,60) ORDER BY 1")
        verdicts = list(cur.fetchall())
    if not row:
        print(f"✗ {gate_id} 不存在")
        return 1
    db_crit, db_sha, status, by, h, fam = row
    db_resha = _sha(db_crit)
    ok = db_resha == db_sha == code_sha
    print(
        f"{gate_id}: h={h} family={fam} status={status} by={by} "
        f"sha DB={db_sha} re={db_resha} code={code_sha} "
        f"{'✓一致' if ok else '✗ 不一致'}"
    )
    print(f"閘列數={n_all} 非H60={n_other}  direction_gate={n_dgate}")
    print(f"econ_verdict 20/60={verdicts}")
    if n_other:
        print("✗ 出現非 H60 閘列")
        return 1
    if h != 60 or fam != FAMILY:
        print("✗ 主閘 horizon/family 不對")
        return 1
    if status != "preregistered" and gate_id == GATE_ID:
        # --check 在 E2 之後仍可用；E1 驗收要求 preregistered
        pass
    if not ok:
        return 1
    print("✓ --check 通過")
    return 0


def approve(gate_id: str, by: str | None) -> int:
    if not sys.stdin.isatty():
        sys.exit("✗ approve 唯決策層人（TTY 閘；AI/腳本 fail-closed）")
    if not by:
        sys.exit("✗ 需 --approved-by")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE econ_establishment_gate SET status='approved', approved_by=%s, approved_at=now() "
            "WHERE gate_id=%s AND status='preregistered' RETURNING horizon",
            (by, gate_id),
        )
        row = cur.fetchone()
        if not row:
            conn.rollback()
            sys.exit(f"✗ {gate_id} 不存在或非 preregistered")
        conn.commit()
    print(f"✓ {gate_id} h={row[0]} 已核准 by {by}——criteria 自此不可變，可跑 establishment eval")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="經濟確立閘預註冊（E1；H60 主格）")
    ap.add_argument("--preregister", action="store_true")
    ap.add_argument("--check", nargs="?", const=GATE_ID, metavar="GATE")
    ap.add_argument("--approve", metavar="GATE")
    ap.add_argument("--approved-by", dest="by")
    args = ap.parse_args()
    if args.preregister:
        rc = preregister()
        if rc != 0:
            return rc
        return check(GATE_ID)
    if args.approve:
        return approve(args.approve, args.by)
    if args.check:
        return check(args.check)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        _list(cur)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
