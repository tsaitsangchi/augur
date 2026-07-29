#!/usr/bin/env python
"""建 knowhow_evidence_weight + knowhow_synthesis_run — KH8/KH9 min-LAND。

🎯 這支在做什麼(白話):證據權重／合成回放兩張帳本 DDL（冪等）；可選抬
   knowhow_auto_admit_gate.max_auto_depth→9。零市場 API；不灌 PME。
守 #6(冪等)· #29a/d· FZ-keep· PME-GATE-keep· HUMAN-APPROVE-keep。

執行指令矩陣:
  python scripts/migrate_kh8_kh9_min_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_kh8_kh9_min_ddl.py --check      # 唯讀現況
  python scripts/migrate_kh8_kh9_min_ddl.py --apply      # 冪等建表+抬 max_auto_depth=9
  python scripts/migrate_kh8_kh9_min_ddl.py --show       # 列 row 摘要
  python scripts/migrate_kh8_kh9_min_ddl.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

DDL_EVIDENCE = """
CREATE TABLE IF NOT EXISTS knowhow_evidence_weight (
  weight_id            BIGSERIAL PRIMARY KEY,
  item_id              BIGINT,
  run_id               TEXT NOT NULL,
  probe_id             TEXT,
  query_hash           TEXT NOT NULL,
  citation_count       INT NOT NULL DEFAULT 0,
  terminal_score       REAL NOT NULL DEFAULT 0,
  contradiction_score  REAL NOT NULL DEFAULT 0,
  evidence_score       REAL NOT NULL DEFAULT 0,
  confidence_band      TEXT NOT NULL
                       CHECK (confidence_band IN ('high','medium','low','absent')),
  risk_flags           JSONB NOT NULL DEFAULT '[]'::jsonb,
  components           JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kh8_weight_item
  ON knowhow_evidence_weight (item_id, weight_id DESC);
CREATE INDEX IF NOT EXISTS idx_kh8_weight_run
  ON knowhow_evidence_weight (run_id, created_at DESC);
COMMENT ON TABLE knowhow_evidence_weight IS
  'KH8 min-LAND: 證據權重帳本（非 approve／非可交易；非答案 SSOT）';
"""

DDL_SYNTHESIS = """
CREATE TABLE IF NOT EXISTS knowhow_synthesis_run (
  synthesis_id         BIGSERIAL PRIMARY KEY,
  item_id              BIGINT,
  run_id               TEXT NOT NULL UNIQUE,
  query_text           TEXT NOT NULL,
  answer_state         TEXT NOT NULL
                       CHECK (answer_state IN (
                         'drafted','synthesized','replay_logged','postmortem_needed')),
  evidence_score       REAL,
  weight_id            BIGINT REFERENCES knowhow_evidence_weight(weight_id)
                       ON DELETE SET NULL,
  replay_json          JSONB NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kh9_synth_item
  ON knowhow_synthesis_run (item_id, synthesis_id DESC);
COMMENT ON TABLE knowhow_synthesis_run IS
  'KH9 min-LAND: 合成／回放帳本（≠approve／≠PME APPLY）';
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 含 evidence", "knowhow_evidence_weight" in DDL_EVIDENCE)
    chk("DDL 含 synthesis", "knowhow_synthesis_run" in DDL_SYNTHESIS)
    for b in ("high", "medium", "low", "absent"):
        chk(f"band {b}", f"'{b}'" in DDL_EVIDENCE)
    for s in ("drafted", "synthesized", "replay_logged", "postmortem_needed"):
        chk(f"state {s}", f"'{s}'" in DDL_SYNTHESIS)
    chk("禁 approve 欄", "approval_status" not in DDL_EVIDENCE + DDL_SYNTHESIS)
    chk(
        "禁 activate 欄／動作",
        "activate" not in DDL_EVIDENCE.lower()
        and "activate" not in DDL_SYNTHESIS.lower(),
    )
    # 欄位定義段（COMMENT 前）不得出現 tradable 欄名
    ev_cols = DDL_EVIDENCE.split("COMMENT", 1)[0].lower()
    syn_cols = DDL_SYNTHESIS.split("COMMENT", 1)[0].lower()
    chk("無 tradable 欄名", "tradable" not in ev_cols and "tradable" not in syn_cols)
    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        for t in ("knowhow_evidence_weight", "knowhow_synthesis_run"):
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            exists = bool(cur.fetchone()[0])
            print(f"{t}={'已在' if exists else '缺'}", end="")
            if exists:
                cur.execute(f"SELECT count(*) FROM {t}")
                print(f" rows={cur.fetchone()[0]}")
            else:
                print()
        cur.execute("SELECT to_regclass(%s)", ("public.knowhow_auto_admit_gate",))
        if cur.fetchone()[0]:
            cur.execute(
                "SELECT max_auto_depth, require_kh8, require_kh9 "
                "FROM knowhow_auto_admit_gate WHERE gate_id='auto_admit_v1'"
            )
            row = cur.fetchone()
            if row:
                print(
                    f"gate max_auto_depth={row[0]} "
                    f"require_kh8={row[1]} require_kh9={row[2]}"
                )
    return 0


def show() -> int:
    return check_live()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH8/KH9 min-LAND DDL")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check or args.show:
        return check_live() if args.check or args.show else 0

    from augur.core import db

    if not args.apply:
        print(__doc__)
        print("(唯讀；--apply 才套用)")
        return check_live()

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL_EVIDENCE)
        cur.execute(DDL_SYNTHESIS)
        # 抬 gate：KH8/9 可評估後允許 progressive 達 9（≠可交易）
        cur.execute("SELECT to_regclass(%s)", ("public.knowhow_auto_admit_gate",))
        if cur.fetchone()[0]:
            cur.execute(
                """
                UPDATE knowhow_auto_admit_gate
                   SET max_auto_depth = GREATEST(COALESCE(max_auto_depth, 0), 9),
                       updated_at = now(),
                       updated_by = 'migrate_kh8_kh9_min_ddl.py:KH8-KH9-min-LAND'
                 WHERE gate_id = 'auto_admit_v1'
                """
            )
            print("  ✓ gate max_auto_depth ≥ 9")
        conn.commit()
    print("  ✓ KH8/KH9 min DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
