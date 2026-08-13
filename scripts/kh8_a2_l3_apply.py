#!/usr/bin/env python3
"""KH8 A2-L3 — 以 A2-v1 批次 INSERT 新 weight 列（雙明示後才 --apply）。

對齊:
  reports/augur_kh8_a2_land_design_spec_20260808.md §4 L3
  audits/KH8-DISCRIM-A2-L3-GO-20260813.md

回滾:
  DELETE FROM knowhow_evidence_weight WHERE run_id = 'kh8:a2-l3:20260813';

執行指令矩陣:
  python scripts/kh8_a2_l3_apply.py --dry-run
  python scripts/kh8_a2_l3_apply.py --apply
  python scripts/kh8_a2_l3_apply.py --rollback
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import _bootstrap  # noqa: F401

RUN_ID = "kh8:a2-l3:20260813"
OUT = Path("/tmp/kh8-a2-l3")


def _inputs_from_latest_row(cite_n: int, components: dict | None) -> dict:
    """與 L2 投影同軸：由現行列 components 還原 A2 輸入（免每列重掃全文）。"""
    c = components or {}
    terminal = float(c.get("terminal", 1.0 if cite_n > 0 else 0.0))
    embed = float(c.get("embed", 0.0))
    kh4_ok = float(c.get("kh4_ok", 0.0))
    status = c.get("kh4_answer_status")
    if status is None and kh4_ok >= 1.0:
        status = "eligible"
    has_sentence = terminal >= 1.0
    has_text = terminal >= 0.5 or has_sentence
    has_embedding = embed >= 1.0
    return dict(
        citation_count=int(cite_n),
        has_text=bool(has_text),
        has_sentence=bool(has_sentence),
        has_embedding=bool(has_embedding),
        kh4_answer_status=status,
    )


def _load_latest(cur):
    cur.execute(
        """
        SELECT DISTINCT ON (item_id)
               item_id, citation_count, evidence_score, confidence_band, components
          FROM knowhow_evidence_weight
         ORDER BY item_id, weight_id DESC
        """
    )
    return cur.fetchall()


def cmd_dry_or_apply(*, apply: bool) -> int:
    from augur.core import db
    from augur.knowledge.evidence import (
        FORMULA_A2_V1,
        compute_evidence_weight,
        minority_mass,
        population_discriminates,
        record_weight,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    rollback = OUT / "rollback.sql"
    rollback.write_text(
        f"-- KH8 A2-L3 rollback\n"
        f"DELETE FROM knowhow_evidence_weight WHERE run_id = '{RUN_ID}';\n",
        encoding="utf-8",
    )

    with db.connect() as conn, conn.cursor() as cur:
        rows = _load_latest(cur)
        print(f"n_latest={len(rows)} apply={apply} run_id={RUN_ID}", flush=True)
        live_bands = Counter(r[3] for r in rows)
        live_scores = [float(r[2]) for r in rows]
        live_mm = minority_mass(live_bands.values())

        a2_bands = Counter()
        a2_scores = []
        wrote = 0
        batch = 0
        for item_id, cite_n, _score, _band, components in rows:
            if isinstance(components, str):
                components = json.loads(components)
            inp = _inputs_from_latest_row(int(cite_n or 0), components)
            w = compute_evidence_weight(**inp, formula=FORMULA_A2_V1)
            a2_bands[w["confidence_band"]] += 1
            a2_scores.append(float(w["evidence_score"]))
            if apply:
                record_weight(cur, item_id=int(item_id), weight=w, run_id=RUN_ID)
                wrote += 1
                batch += 1
                if batch >= 1000:
                    conn.commit()
                    print(f"  commit wrote={wrote}", flush=True)
                    batch = 0
        if apply and batch:
            conn.commit()

        a2_mm = minority_mass(a2_bands.values())
        disc_before = None
        if not apply:
            disc_before = population_discriminates(cur)
        disc_after = population_discriminates(cur) if apply else None

    def p50(xs):
        return float(statistics.median(xs)) if xs else None

    summary = {
        "n": len(rows),
        "apply": apply,
        "run_id": RUN_ID,
        "wrote": wrote,
        "live_bands": dict(live_bands),
        "live_minority": live_mm,
        "live_score_p50": p50(live_scores),
        "a2_bands": dict(a2_bands),
        "a2_minority": a2_mm,
        "a2_score_p50": p50(a2_scores),
        "a2_proj_ok_est": a2_mm >= 0.05,
        "disc_before": disc_before,
        "disc_after": disc_after,
        "default_formula_still": "legacy",
        "rollback_sql": str(rollback),
    }
    out_json = OUT / ("apply.json" if apply else "dry-run.json")
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str), flush=True)
    print(f"WROTE {out_json}", flush=True)
    print(f"ROLLBACK {rollback}", flush=True)
    return 0


def cmd_rollback() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM knowhow_evidence_weight WHERE run_id=%s",
            (RUN_ID,),
        )
        n = int(cur.fetchone()[0])
        print(f"rollback candidates run_id={RUN_ID} n={n}", flush=True)
        cur.execute(
            "DELETE FROM knowhow_evidence_weight WHERE run_id=%s",
            (RUN_ID,),
        )
        conn.commit()
        print(f"deleted={cur.rowcount}", flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--rollback", action="store_true")
    args = ap.parse_args(argv)
    if args.rollback:
        return cmd_rollback()
    return cmd_dry_or_apply(apply=bool(args.apply))


if __name__ == "__main__":
    raise SystemExit(main())
