#!/usr/bin/env python
"""建／擴 knowhow_auto_admit_* — KH10-AUTO-ADMIT S0＋S0.1。

🎯 這支在做什麼(白話):漸進入庫帳本 DDL——run（含 admit_depth）／state 水印／gate
   （enabled 入憲後可 true；raw_floor／progressive 開；max_auto_depth 精準上限）。
   零市場 API；不灌 PME。
守 #6(冪等)· #29a/d· 憲章 v1.48.0 一律准入· FZ-keep· PME-GATE-keep· NHC-keep。

執行指令矩陣:
  python scripts/migrate_knowhow_auto_admit_ddl.py              # 安全預設:印矩陣+--check
  python scripts/migrate_knowhow_auto_admit_ddl.py --check      # 唯讀現況
  python scripts/migrate_knowhow_auto_admit_ddl.py --apply      # 冪等建表+S0.1 增量+gate
  python scripts/migrate_knowhow_auto_admit_ddl.py --show       # 列 gate／state 摘要
  python scripts/migrate_knowhow_auto_admit_ddl.py --selftest   # 零 DB 紅綠
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

GATE_ID = "auto_admit_v1"

DDL_RUN = """
CREATE TABLE IF NOT EXISTS knowhow_auto_admit_run (
  run_id           BIGSERIAL PRIMARY KEY,
  channel          TEXT NOT NULL
                   CHECK (channel IN ('local_files','sftp','topic_harvest')),
  target_kind      TEXT NOT NULL CHECK (target_kind IN ('source','item','batch')),
  target_id        TEXT NOT NULL,
  admit_depth_before INT NOT NULL DEFAULT 0
                   CHECK (admit_depth_before BETWEEN 0 AND 10),
  admit_depth_after  INT NOT NULL DEFAULT 0
                   CHECK (admit_depth_after BETWEEN 0 AND 10),
  raw_verdict      TEXT NOT NULL DEFAULT 'pending'
                   CHECK (raw_verdict IN ('pending','pass','fail','escalate')),
  full_verdict     TEXT NOT NULL DEFAULT 'pending'
                   CHECK (full_verdict IN ('pending','pass','fail','escalate')),
  verdict          TEXT NOT NULL DEFAULT 'pending'
                   CHECK (verdict IN ('pending','pass','fail','escalate')),
  layer_scores     JSONB NOT NULL DEFAULT '{}'::jsonb,
  actions          JSONB NOT NULL DEFAULT '[]'::jsonb,
  actor            TEXT NOT NULL DEFAULT 'system:kh10_auto_admit',
  note             TEXT,
  started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at      TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_auto_admit_target
  ON knowhow_auto_admit_run (channel, target_kind, target_id, started_at DESC);
COMMENT ON TABLE knowhow_auto_admit_run IS
  'KH10-AUTO-ADMIT: 漸進裁決帳（admit_depth 0=原文…10=滿層）；非答案 SSOT';
"""

DDL_STATE = """
CREATE TABLE IF NOT EXISTS knowhow_auto_admit_state (
  target_kind      TEXT NOT NULL CHECK (target_kind IN ('source','item')),
  target_id        TEXT NOT NULL,
  channel          TEXT NOT NULL
                   CHECK (channel IN ('local_files','sftp','topic_harvest')),
  admit_depth      INT NOT NULL DEFAULT 0 CHECK (admit_depth BETWEEN 0 AND 10),
  layer_scores     JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_run_id      BIGINT,
  PRIMARY KEY (target_kind, target_id)
);
CREATE INDEX IF NOT EXISTS idx_auto_admit_state_depth
  ON knowhow_auto_admit_state (admit_depth, channel);
COMMENT ON TABLE knowhow_auto_admit_state IS
  'KH10-AUTO-ADMIT: 漸進水印 admit_depth；非答案 SSOT';
"""

DDL_GATE = """
CREATE TABLE IF NOT EXISTS knowhow_auto_admit_gate (
  gate_id            TEXT PRIMARY KEY DEFAULT 'auto_admit_v1',
  enabled            BOOLEAN NOT NULL DEFAULT true,
  raw_floor_enabled  BOOLEAN NOT NULL DEFAULT true,
  progressive_enabled BOOLEAN NOT NULL DEFAULT true,
  max_auto_depth     INT NOT NULL DEFAULT 7
                     CHECK (max_auto_depth BETWEEN 0 AND 10),
  require_kh8        BOOLEAN NOT NULL DEFAULT true,
  require_kh9        BOOLEAN NOT NULL DEFAULT true,
  channels           TEXT[] NOT NULL DEFAULT ARRAY['local_files','sftp','topic_harvest'],
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         TEXT
);
COMMENT ON TABLE knowhow_auto_admit_gate IS
  'KH10-AUTO-ADMIT v1.48: enabled 預設 true（機械可升級）；progressive／raw_floor 開';
"""

ALTER_RUN = """
ALTER TABLE knowhow_auto_admit_run
  ADD COLUMN IF NOT EXISTS raw_verdict TEXT NOT NULL DEFAULT 'pending';
ALTER TABLE knowhow_auto_admit_run
  ADD COLUMN IF NOT EXISTS full_verdict TEXT NOT NULL DEFAULT 'pending';
ALTER TABLE knowhow_auto_admit_run
  ADD COLUMN IF NOT EXISTS admit_depth_before INT NOT NULL DEFAULT 0;
ALTER TABLE knowhow_auto_admit_run
  ADD COLUMN IF NOT EXISTS admit_depth_after INT NOT NULL DEFAULT 0;
"""

ALTER_GATE = """
ALTER TABLE knowhow_auto_admit_gate
  ADD COLUMN IF NOT EXISTS raw_floor_enabled BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE knowhow_auto_admit_gate
  ADD COLUMN IF NOT EXISTS progressive_enabled BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE knowhow_auto_admit_gate
  ADD COLUMN IF NOT EXISTS max_auto_depth INT NOT NULL DEFAULT 7;
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建 run", "knowhow_auto_admit_run" in DDL_RUN)
    chk("DDL 建 state", "knowhow_auto_admit_state" in DDL_STATE)
    chk("DDL 建 gate", "knowhow_auto_admit_gate" in DDL_GATE)
    chk("admit_depth 欄", "admit_depth_before" in DDL_RUN and "admit_depth" in DDL_STATE)
    chk("progressive 欄", "progressive_enabled" in DDL_GATE)
    chk("max_auto_depth", "max_auto_depth" in DDL_GATE)
    chk("v1.48 enabled 預設 true", "DEFAULT true" in DDL_GATE.split("enabled")[1][:80])
    chk("三通道閉集", "local_files" in DDL_RUN and "topic_harvest" in DDL_RUN)
    chk("指令矩陣", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        for t in (
            "knowhow_auto_admit_run",
            "knowhow_auto_admit_gate",
            "knowhow_auto_admit_state",
        ):
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            print(f"{t}={'已在' if cur.fetchone()[0] else '缺'}")
        cur.execute(
            """
            SELECT gate_id, enabled, raw_floor_enabled,
                   COALESCE(progressive_enabled, true),
                   COALESCE(max_auto_depth, 7),
                   require_kh8, require_kh9
            FROM knowhow_auto_admit_gate WHERE gate_id=%s
            """,
            (GATE_ID,),
        )
        row = cur.fetchone()
        if not row:
            print("gate 種子缺")
            return 1
        gid, en, raw, prog, mx, r8, r9 = row
        print(
            f"gate={gid} enabled={en} raw_floor={raw} progressive={prog} "
            f"max_auto_depth={mx} require_kh8={r8} require_kh9={r9}"
        )
        cur.execute("SELECT count(*), coalesce(max(admit_depth),0) FROM knowhow_auto_admit_state")
        n, mxd = cur.fetchone()
        print(f"state rows={n} max_depth={mxd}")
        if raw is not True:
            print("✗FAIL: raw_floor_enabled 應 true")
            return 1
        if prog is not True:
            print("✗FAIL: progressive_enabled 應 true")
            return 1
        print("S0.1 閘驗收 ✓")
    return 0


def show() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowhow_auto_admit_gate')")
        if not cur.fetchone()[0]:
            print("gate 未建")
            return 1
        cur.execute(
            "SELECT gate_id, enabled, raw_floor_enabled, progressive_enabled, "
            "max_auto_depth, updated_by FROM knowhow_auto_admit_gate"
        )
        for r in cur.fetchall():
            print(f"  gate: {r}")
        cur.execute("SELECT to_regclass('public.knowhow_auto_admit_state')")
        if cur.fetchone()[0]:
            cur.execute(
                "SELECT admit_depth, count(*) FROM knowhow_auto_admit_state "
                "GROUP BY 1 ORDER BY 1"
            )
            print("  state depth buckets:")
            for d, c in cur.fetchall():
                print(f"    depth={d}: {c}")
    return 0


def apply() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL_RUN)
        cur.execute(ALTER_RUN)
        cur.execute(DDL_STATE)
        cur.execute(DDL_GATE)
        cur.execute(ALTER_GATE)
        cur.execute("SELECT 1 FROM knowhow_auto_admit_gate WHERE gate_id=%s", (GATE_ID,))
        if cur.fetchone():
            cur.execute(
                """
                UPDATE knowhow_auto_admit_gate SET
                  raw_floor_enabled = true,
                  progressive_enabled = true,
                  max_auto_depth = COALESCE(max_auto_depth, 7),
                  enabled = true,
                  updated_by = 'migrate_knowhow_auto_admit_ddl.py:S0.1',
                  updated_at = now()
                WHERE gate_id=%s
                """,
                (GATE_ID,),
            )
            print(f"  gate 更新: enabled=true progressive=true max_auto_depth≤7")
        else:
            cur.execute(
                """
                INSERT INTO knowhow_auto_admit_gate (
                  gate_id, enabled, raw_floor_enabled, progressive_enabled,
                  max_auto_depth, require_kh8, require_kh9, channels, updated_by
                ) VALUES (
                  %s, true, true, true, 7, true, true,
                  ARRAY['local_files','sftp','topic_harvest'],
                  'migrate_knowhow_auto_admit_ddl.py:S0.1'
                )
                """,
                (GATE_ID,),
            )
            print(f"  gate 種子: {GATE_ID} enabled=true")
        # FK soft：last_run_id 不強制 REFERENCES（避免循環建表序）
        conn.commit()
    print("  ✓ KH10-AUTO-ADMIT S0.1 DDL 冪等完成")
    return check_live()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="KH10-AUTO-ADMIT DDL S0/S0.1")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.show:
        return show()
    if args.check:
        return check_live()
    if not args.apply:
        print(__doc__)
        print("(唯讀；--apply 才套用)")
        return check_live()
    return apply()


if __name__ == "__main__":
    sys.exit(main())
