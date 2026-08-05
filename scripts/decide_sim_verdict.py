#!/usr/bin/env python3
"""🎯 W4 判決工具——把 sim_calibration_eval 五臂素材收攏成 sim_evolution_verdict（M-M5／P1-11）。

白話:讀同 cell 之 5 列 eval＋門 thresholds，依 SIM-CAL-R1 判式寫 **killed** 或 **undecidable**。
  **promoted 路徑一律不寫**（專章 §4.2／§4.4——`decided_by` 須 hugo 親跑；本工具不設人名旗標）。
  證據鏈終點懸空之缺口＝本支；evaluator（W3）只產素材，判定屬本支（W4）。

守原則 #12（判式素材單一住所＝`evaluate_sim_calibration` 之 k1/k2/k3／undecidable）·
  #15（先驗紅）· #28（零 API）· #29a/d · #35（純函式餵真輸入）。

執行指令矩陣
------------
    python3 scripts/decide_sim_verdict.py                      # 無參數＝現況（唯讀：eval／verdict 水位）
    python3 scripts/decide_sim_verdict.py --check              # 唯讀預演判決（不寫表）
    python3 scripts/decide_sim_verdict.py --check --candidate ID --gate SIM-CAL-R1
    python3 scripts/decide_sim_verdict.py --apply              # 寫 killed／undecidable（拒寫 promoted）
    python3 scripts/decide_sim_verdict.py --selftest           # 零 DB：純函式紅綠＋先驗紅
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from evaluate_sim_calibration import (  # 判式單一住所 #12
    REQUIRED_ARMS,
    GATE_ID as DEFAULT_GATE,
    k1_breach,
    k2_live_beats_arm,
    k3_breach,
    undecidable_reasons,
)

REQUIRED_FIVE = REQUIRED_ARMS  # live/ceiling/floor/shuffled/mismatched
PROMOTED_BLOCK = (
    "🔴 殘項：promoted 路徑需人簽（decided_by／decided_at／gate_proposal_ref）；"
    "本工具不寫 promoted、不設人名旗標"
)


def decide_from_bundle(
    *,
    n_valid: int,
    n_valid_min: int,
    k_clusters: int,
    date_clusters_min: int,
    arms_present: list | tuple,
    k1: bool,
    k2: bool,
    k3: bool,
    evidence_eval_ids: list | tuple,
    thresholds_snapshot: dict | None = None,
    k_detail: dict | None = None,
) -> dict:
    """純函式：素材 → {verdict, basis, evidence_eval_ids, write_allowed}。

    優先序：undecidable（樣本／簇／缺臂）→ killed（k1∨k2∨k3）→ promoted_eligible（拒寫）。
    write_allowed＝僅 killed／undecidable。
    """
    ids = [int(x) for x in evidence_eval_ids]
    und = undecidable_reasons(
        n_valid, n_valid_min, k_clusters, date_clusters_min, arms_present, required=REQUIRED_FIVE
    )
    basis = {
        "thresholds": thresholds_snapshot or {
            "n_valid_min": n_valid_min,
            "date_clusters_min": date_clusters_min,
        },
        "undecidable_reasons": und,
        "k1_breach": bool(k1),
        "k2_breach": bool(k2),
        "k3_breach": bool(k3),
        "arms_present": list(arms_present),
        "n_valid": n_valid,
        "k_clusters": k_clusters,
        "self_reported": "W4 decide=self-reported; promoted 須三鎖人簽",
    }
    if k_detail:
        basis["k_detail"] = k_detail

    if und:
        return {
            "verdict": "undecidable",
            "basis": basis,
            "evidence_eval_ids": ids,
            "write_allowed": True,
            "arms_covered": list(arms_present),
            "note": "§5.4 誠實無能為合法產出",
        }
    if k1 or k2 or k3:
        return {
            "verdict": "killed",
            "basis": basis,
            "evidence_eval_ids": ids,
            "write_allowed": True,
            "arms_covered": list(arms_present),
            "note": "k1/k2/k3 任一 breach＝判死留檔",
        }
    return {
        "verdict": "promoted_eligible",
        "basis": basis,
        "evidence_eval_ids": ids,
        "write_allowed": False,
        "arms_covered": list(arms_present),
        "note": PROMOTED_BLOCK,
    }


def decide_from_eval_rows(rows: list, thresholds: dict) -> dict:
    """由 sim_calibration_eval 列＋thresholds 推 bundle 再判決。純函式（列形狀固定）。

    `rows`＝list of dict: eval_id, arm, n_valid, detail(dict|str), cov_p80, cov_p90, pit_ks_p
    同一 cell 之五臂列；detail 優先吃 evaluator 已寫之 k1/k2_breach/k3／undecidable_reasons。
    """
    if not rows:
        out = decide_from_bundle(
            n_valid=0, n_valid_min=int(thresholds["n_valid_min"]),
            k_clusters=0, date_clusters_min=int(thresholds["date_clusters_min"]),
            arms_present=[], k1=False, k2=False, k3=False,
            evidence_eval_ids=[], thresholds_snapshot=thresholds,
        )
        out["write_allowed"] = False
        out["note"] = "無 eval 列可作證據——拒寫"
        return out

    arms = []
    ids = []
    live = None
    detail0 = {}
    for r in rows:
        arm = r["arm"]
        arms.append(arm)
        ids.append(int(r["eval_id"]))
        d = r.get("detail") or {}
        if isinstance(d, str):
            d = json.loads(d)
        if arm == "live":
            live = r
            detail0 = d

    n_valid = int(detail0.get("n_reconcile", {}).get("n_valid")
                  or (live or rows[0]).get("n_valid") or 0)
    k_clusters = 0
    k2d = detail0.get("k2") or {}
    for arm_d in k2d.values():
        if isinstance(arm_d, dict) and arm_d.get("delta_per_cluster"):
            k_clusters = max(k_clusters, len(arm_d["delta_per_cluster"]))

    if "k1" in detail0 and "k2_breach" in detail0 and "k3" in detail0:
        k1 = bool(detail0["k1"].get("breach"))
        k2 = bool(detail0["k2_breach"])
        k3 = bool(detail0["k3"].get("breach"))
        k_detail = {"k1": detail0.get("k1"), "k2": detail0.get("k2"), "k3": detail0.get("k3")}
    else:
        cov80 = float((live or {}).get("cov_p80") or 0.0)
        cov90 = float((live or {}).get("cov_p90") or 0.0)
        tol = thresholds.get("cov_tol") or {"p80": 0.05, "p90": 0.05}
        k1 = k1_breach(cov80, cov90, float(tol["p80"]), float(tol["p90"]))
        pit_p = (live or {}).get("pit_ks_p")
        p_min = float((thresholds.get("pit") or {}).get("p_min") or 0.05)
        k3 = k3_breach(float(pit_p), p_min) if pit_p is not None else True
        k2 = True  # 缺 LCB＝不得宣稱勝過地板臂（fail-closed）
        k_detail = {"recomputed": True, "k2_fail_closed": "缺 detail.k2 LCB"}

    out = decide_from_bundle(
        n_valid=n_valid,
        n_valid_min=int(thresholds["n_valid_min"]),
        k_clusters=k_clusters,
        date_clusters_min=int(thresholds["date_clusters_min"]),
        arms_present=arms,
        k1=k1, k2=k2, k3=k3,
        evidence_eval_ids=ids,
        thresholds_snapshot=thresholds,
        k_detail=k_detail,
    )
    if not ids or any(i <= 0 for i in ids):
        out["write_allowed"] = False
        out["note"] = ((out.get("note") or "") + "；evidence_eval_ids 非法").lstrip("；")
    return out


def _git7() -> str:
    try:
        from simulate_mc_paths import _git7 as g
        return g()
    except Exception:
        return "unknown"


def _load_thresholds(cur, gate_id: str) -> dict:
    cur.execute(
        "SELECT criteria->'thresholds' FROM evolution_prereg_gate WHERE gate_id=%s",
        (gate_id,),
    )
    row = cur.fetchone()
    if not row or row[0] is None:
        raise RuntimeError(f"gate {gate_id} 無 thresholds")
    th = row[0]
    return th if isinstance(th, dict) else json.loads(th)


def _load_eval_rows(cur, gate_id: str, candidate_id: str | None, eval_set_id: str | None):
    sql = """
        SELECT eval_id, arm, n_valid, detail, cov_p80, cov_p90, pit_ks_p,
               eval_set_id, eval_code_hash, candidate_id
          FROM sim_calibration_eval
         WHERE gate_id=%s
    """
    args: list = [gate_id]
    if candidate_id:
        sql += " AND candidate_id=%s"
        args.append(candidate_id)
    if eval_set_id:
        sql += " AND eval_set_id=%s"
        args.append(eval_set_id)
    sql += " ORDER BY created_at DESC, eval_id DESC"
    cur.execute(sql, args)
    cols = ("eval_id", "arm", "n_valid", "detail", "cov_p80", "cov_p90", "pit_ks_p",
            "eval_set_id", "eval_code_hash", "candidate_id")
    all_rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    if not all_rows:
        return [], None, None
    # 取最新同 cell（eval_set_id + eval_code_hash + candidate）
    key = (all_rows[0]["eval_set_id"], all_rows[0]["eval_code_hash"], all_rows[0]["candidate_id"])
    cell = [r for r in all_rows
            if (r["eval_set_id"], r["eval_code_hash"], r["candidate_id"]) == key]
    return cell, key[0], cell[0]["candidate_id"]


def _insert_verdict(cur, *, candidate_id, gate_id, decision, git_sha):
    if decision["verdict"] not in ("killed", "undecidable"):
        raise RuntimeError(PROMOTED_BLOCK)
    if not decision.get("write_allowed"):
        raise RuntimeError("write_allowed=False——拒寫")
    ids = decision["evidence_eval_ids"]
    if not ids or any(i <= 0 for i in ids):
        raise RuntimeError("evidence_eval_ids 必須為真實 eval_id 且非空")
    # 禁寫人簽欄——故意不帶 decided_by／decided_at／gate_proposal_ref
    cur.execute(
        """
        INSERT INTO sim_evolution_verdict
          (candidate_id, gate_id, verdict, basis, evidence_eval_ids,
           arms_covered, git_sha)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING verdict_id
        """,
        (
            candidate_id,
            gate_id,
            decision["verdict"],
            json.dumps(decision["basis"], ensure_ascii=False, default=str),
            ids,
            decision.get("arms_covered") or [],
            git_sha,
        ),
    )
    return cur.fetchone()[0]


def status_or_check(*, apply: bool, check: bool, gate_id: str,
                    candidate_id: str | None, eval_set_id: str | None) -> int:
    try:
        from augur.core import db
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM sim_calibration_eval WHERE gate_id=%s", (gate_id,))
            n_eval = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM sim_evolution_verdict WHERE gate_id=%s", (gate_id,))
            n_ver = cur.fetchone()[0]
            print(f"水位: gate={gate_id} eval={n_eval} verdict={n_ver}")
            if not check and not apply:
                print(__doc__.split("執行指令矩陣")[1])
                print(f"  {PROMOTED_BLOCK}")
                return 0

            th = _load_thresholds(cur, gate_id)
            rows, set_id, cand = _load_eval_rows(cur, gate_id, candidate_id, eval_set_id)
            cand = candidate_id or cand
            print(f"  cell: candidate={cand or '?'} eval_set_id={set_id or '∅'} n_rows={len(rows)}")
            if not rows:
                print("  ✗ 無 eval 列——無法判決（W3 尚未寫入；K=3 齊後才有）")
                return 1
            decision = decide_from_eval_rows(rows, th)
            print(f"  判決={decision['verdict']} write_allowed={decision['write_allowed']}")
            print(f"  note={decision.get('note')}")
            print(f"  basis.undecidable={decision['basis'].get('undecidable_reasons')}")
            print(f"  k1/k2/k3 breach="
                  f"{decision['basis']['k1_breach']}/"
                  f"{decision['basis']['k2_breach']}/"
                  f"{decision['basis']['k3_breach']}")
            if decision["verdict"] == "promoted_eligible":
                print(f"  {PROMOTED_BLOCK}")
                return 0 if check else 1
            if check:
                print("  --check 完（零寫入）")
                return 0
            if apply:
                if not cand:
                    print("✗ --apply 缺 candidate_id")
                    return 1
                from augur.execution import action_log
                vid = _insert_verdict(
                    cur, candidate_id=cand, gate_id=gate_id,
                    decision=decision, git_sha=_git7(),
                )
                # P5.E1 六元組(C軌P1,2026-08-05):僅 killed／undecidable 真寫才留痕;promoted 本就不寫
                auth_ref = action_log.resolve_grant_id(cur, "sim_verdict_write")
                aid = action_log.log_action(
                    cur,
                    actor_identity="decide_sim_verdict",
                    authorization_ref=auth_ref,
                    knowledge_basis={"gate_id": gate_id, "candidate_id": cand,
                                    "verdict": decision["verdict"], "verdict_id": vid},
                    action_type="sim_verdict_write",
                    target=f"{gate_id}:{cand}",
                    expected_effect={"table": "sim_evolution_verdict", "verdict": decision["verdict"]},
                )
                action_log.link_observed_effect(cur, aid, None, status="completed")
                conn.commit()
                print(f"✓ 寫入 verdict_id={vid} verdict={decision['verdict']} action_id={aid}")
                return 0
            return 0
    except Exception as e:
        print(f"(DB／執行異常: {type(e).__name__}: {e})")
        if not check and not apply:
            print(__doc__.split("執行指令矩陣")[1])
            return 0
        return 1


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    th = {
        "n_valid_min": 100,
        "date_clusters_min": 3,
        "cov_tol": {"p80": 0.05, "p90": 0.05},
        "pit": {"p_min": 0.05},
        "skill_arms": ["floor", "shuffled", "mismatched"],
    }

    # —— 先驗紅：undecidable（樣本不足）必須紅路徑（寫成 undecidable，非 promoted）
    und = decide_from_bundle(
        n_valid=50, n_valid_min=100, k_clusters=3, date_clusters_min=3,
        arms_present=list(REQUIRED_FIVE), k1=False, k2=False, k3=False,
        evidence_eval_ids=[11, 12, 13, 14, 15], thresholds_snapshot=th,
    )
    chk("先驗紅→綠：n_valid<min ⇒ undecidable", und["verdict"] == "undecidable")
    chk("undecidable 可寫", und["write_allowed"] is True)

    # —— 缺臂 undecidable
    miss = decide_from_bundle(
        n_valid=150, n_valid_min=100, k_clusters=3, date_clusters_min=3,
        arms_present=["live", "ceiling"], k1=False, k2=False, k3=False,
        evidence_eval_ids=[1], thresholds_snapshot=th,
    )
    chk("缺臂 ⇒ undecidable", miss["verdict"] == "undecidable"
        and any("缺臂" in r for r in miss["basis"]["undecidable_reasons"]))

    # —— killed：k1 breach
    killed = decide_from_bundle(
        n_valid=150, n_valid_min=100, k_clusters=3, date_clusters_min=3,
        arms_present=list(REQUIRED_FIVE), k1=True, k2=False, k3=False,
        evidence_eval_ids=[21, 22, 23, 24, 25], thresholds_snapshot=th,
    )
    chk("k1 breach ⇒ killed", killed["verdict"] == "killed" and killed["write_allowed"])

    # —— killed：k2／k3
    chk("k2 breach ⇒ killed",
        decide_from_bundle(
            n_valid=150, n_valid_min=100, k_clusters=3, date_clusters_min=3,
            arms_present=list(REQUIRED_FIVE), k1=False, k2=True, k3=False,
            evidence_eval_ids=[1], thresholds_snapshot=th,
        )["verdict"] == "killed")
    chk("k3 breach ⇒ killed",
        decide_from_bundle(
            n_valid=150, n_valid_min=100, k_clusters=3, date_clusters_min=3,
            arms_present=list(REQUIRED_FIVE), k1=False, k2=False, k3=True,
            evidence_eval_ids=[1], thresholds_snapshot=th,
        )["verdict"] == "killed")

    # —— 全過 ⇒ promoted_eligible 且拒寫（不代打）
    prom = decide_from_bundle(
        n_valid=150, n_valid_min=100, k_clusters=3, date_clusters_min=3,
        arms_present=list(REQUIRED_FIVE), k1=False, k2=False, k3=False,
        evidence_eval_ids=[31, 32, 33, 34, 35], thresholds_snapshot=th,
    )
    chk("全清 ⇒ promoted_eligible 拒寫",
        prom["verdict"] == "promoted_eligible" and prom["write_allowed"] is False)
    chk("promoted note 標 🔴 殘項", "🔴" in (prom.get("note") or ""))

    # —— undecidable 優先於 killed（樣本不足即使 k1 breach 也先 undecidable）
    pri = decide_from_bundle(
        n_valid=10, n_valid_min=100, k_clusters=1, date_clusters_min=3,
        arms_present=list(REQUIRED_FIVE), k1=True, k2=True, k3=True,
        evidence_eval_ids=[1], thresholds_snapshot=th,
    )
    chk("undecidable 優先於 killed", pri["verdict"] == "undecidable")

    # —— 從 eval 列：detail 含 k1 breach
    rows_killed = [
        {
            "eval_id": 100 + i, "arm": arm, "n_valid": 150,
            "cov_p80": 0.90, "cov_p90": 0.90, "pit_ks_p": 0.5,
            "detail": {
                "n_reconcile": {"n_valid": 150},
                "k1": {"breach": True, "cov_p80": 0.90, "cov_p90": 0.90},
                "k2": {a: {"lcb": 0.1, "live_beats": True,
                           "delta_per_cluster": {"c0": 0.1, "c1": 0.1, "c2": 0.1}}
                       for a in ("floor", "shuffled", "mismatched")},
                "k2_breach": False,
                "k3": {"breach": False, "pit_ks_p": 0.5},
            } if arm == "live" else {},
        }
        for i, arm in enumerate(REQUIRED_FIVE)
    ]
    d_k = decide_from_eval_rows(rows_killed, th)
    chk("eval 列 detail → killed", d_k["verdict"] == "killed" and len(d_k["evidence_eval_ids"]) == 5)

    # —— k1_breach／k2／k3 與上游一致（絆線：弄壞則紅）
    chk("上游 k1 綠仍綠", not k1_breach(0.83, 0.87, 0.05, 0.05))
    chk("上游 k1 紅仍紅（先驗紅保留）", k1_breach(0.90, 0.90, 0.05, 0.05))
    chk("上游 k2 LCB>0 勝", k2_live_beats_arm(1e-6))
    chk("上游 k3 p<p_min 紅", k3_breach(0.04, 0.05))

    # —— 程式體不設人名旗標（#35：切掉自測段再查 haystack）
    body = Path(__file__).read_text(encoding="utf-8").split("def _selftest")[0]
    chk("無 --decided-by 旗標", "--decided-by" not in body)
    parts = body.split("INSERT INTO sim_evolution_verdict")
    chk("有 INSERT sim_evolution_verdict", len(parts) > 1)
    cols = parts[1].split("RETURNING")[0]
    chk("INSERT 欄位清單不帶 decided_by", "decided_by" not in cols)

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="W4 sim 判決（killed／undecidable；M-M5）")
    ap.add_argument("--check", action="store_true", help="唯讀預演")
    ap.add_argument("--apply", action="store_true", help="寫 killed／undecidable")
    ap.add_argument("--gate", default=DEFAULT_GATE)
    ap.add_argument("--candidate", default=None)
    ap.add_argument("--eval-set-id", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply and a.check:
        print("✗ --apply 與 --check 互斥")
        return 2
    return status_or_check(
        apply=a.apply, check=a.check, gate_id=a.gate,
        candidate_id=a.candidate, eval_set_id=a.eval_set_id,
    )


if __name__ == "__main__":
    sys.exit(main())
