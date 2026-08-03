#!/usr/bin/env python3
"""🎯 建 `knowhow_evidence_weight_honest`——KH8 band 消費側誠實 view（M-G14）。

守原則 #12（鑑別力判準與 `evidence.discrimination_verdict`／`MIN_MINORITY_MASS=0.05` 同尺）·
#15（母體無鑑別力時不得把 raw `high` 當可用信號）· #6（`--apply` 才 DDL）· #29a/d · #35。

起因（優化計畫書第 23 步／r4 G11）：寫入閘已接 `discrimination_verdict`（現 live ok=False），
但仍有路徑直讀 `knowhow_evidence_weight.confidence_band`（high ≈146k）當真訊號。
本 view：**不改基表**；另開 `confidence_band_usable`——母體 gate 不過時為 NULL，
raw 仍可見於 `confidence_band_raw`（審計／除錯用不充當證據）。

執行指令矩陣
------------
    python3 scripts/migrate_kh8_honest_view_ddl.py              # 無參數＝--check
    python3 scripts/migrate_kh8_honest_view_ddl.py --check      # 唯讀：view 在否＋抽樣 usable
    python3 scripts/migrate_kh8_honest_view_ddl.py --print-ddl  # 印 DDL（零連線）
    python3 scripts/migrate_kh8_honest_view_ddl.py --apply      # CREATE OR REPLACE VIEW（#6）
    python3 scripts/migrate_kh8_honest_view_ddl.py --selftest   # 免 DB
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

VIEW = "knowhow_evidence_weight_honest"
# 與 src/augur/knowledge/evidence.py MIN_MINORITY_MASS／MIN_DISCRIMINATING_BANDS 鎖同尺
MIN_MINORITY_MASS = 0.05
MIN_DISCRIMINATING_BANDS = 2

DDL = f"""
SET lock_timeout = '5s';

CREATE OR REPLACE VIEW {VIEW} AS
WITH band_counts AS (
  SELECT confidence_band AS b, count(*)::float8 AS c
  FROM knowhow_evidence_weight
  GROUP BY 1
),
band_stats AS (
  SELECT coalesce(sum(c), 0) AS n,
         count(*) FILTER (WHERE c > 0) AS n_bands,
         CASE WHEN coalesce(sum(c), 0) > 0
              THEN 1.0 - max(c) / sum(c) ELSE 0.0 END AS band_mm
  FROM band_counts
),
comp_src AS (
  SELECT components->>'terminal' AS t,
         components->>'embed' AS e,
         components->>'kh4_ok' AS k
  FROM knowhow_evidence_weight
),
comp_stats AS (
  SELECT
    coalesce((SELECT 1.0 - max(c)::float8 / nullif(sum(c), 0)
              FROM (SELECT count(*) c FROM comp_src GROUP BY t) x), 0) AS t_mm,
    coalesce((SELECT 1.0 - max(c)::float8 / nullif(sum(c), 0)
              FROM (SELECT count(*) c FROM comp_src GROUP BY e) y), 0) AS e_mm,
    coalesce((SELECT 1.0 - max(c)::float8 / nullif(sum(c), 0)
              FROM (SELECT count(*) c FROM comp_src GROUP BY k) z), 0) AS k_mm
),
gate AS (
  SELECT bs.n, bs.n_bands, bs.band_mm,
         cs.t_mm, cs.e_mm, cs.k_mm,
         greatest(cs.t_mm, cs.e_mm, cs.k_mm) AS cmax,
         (bs.n > 0
          AND bs.n_bands >= {MIN_DISCRIMINATING_BANDS}
          AND bs.band_mm >= {MIN_MINORITY_MASS}
          AND greatest(cs.t_mm, cs.e_mm, cs.k_mm) >= {MIN_MINORITY_MASS}
         ) AS population_ok
  FROM band_stats bs CROSS JOIN comp_stats cs
)
SELECT
  w.weight_id,
  w.item_id,
  w.run_id,
  w.probe_id,
  w.query_hash,
  w.citation_count,
  w.terminal_score,
  w.contradiction_score,
  w.evidence_score,
  w.confidence_band AS confidence_band_raw,
  CASE WHEN g.population_ok THEN w.confidence_band ELSE NULL END
    AS confidence_band_usable,
  g.population_ok,
  g.n AS population_n,
  round(g.band_mm::numeric, 8) AS population_band_minority_mass,
  round(g.cmax::numeric, 8) AS population_comp_minority_mass_max,
  w.risk_flags,
  w.components,
  w.created_at
FROM knowhow_evidence_weight w
CROSS JOIN gate g;

COMMENT ON VIEW {VIEW} IS
  'M-G14 KH8 消費側誠實面：confidence_band_usable 僅在母體 discrimination_verdict 同尺通過時暴露；'
  '否則 NULL（raw 見 confidence_band_raw）。不改基表；直讀基表 band＝假訊號風險（見 check_kh8_band_consumption）。';
"""


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("view 名固定", VIEW == "knowhow_evidence_weight_honest")
    chk("DDL 含 confidence_band_usable", "confidence_band_usable" in DDL)
    chk("DDL 含 confidence_band_raw", "confidence_band_raw" in DDL)
    chk("DDL 鎖同尺 minority 0.05", "0.05" in DDL)
    chk("DDL 鎖同尺 bands≥2", f">= {MIN_DISCRIMINATING_BANDS}" in DDL
        or f">= {MIN_DISCRIMINATING_BANDS}" in DDL.replace(" ", ""))
    chk("DDL 不 DROP 基表", "DROP TABLE" not in DDL.upper())
    chk("library MIN_MINORITY_MASS 對齊", True)
    try:
        from augur.knowledge.evidence import MIN_MINORITY_MASS as lib_mm
        from augur.knowledge.evidence import MIN_DISCRIMINATING_BANDS as lib_nb
        chk(f"evidence.MIN_MINORITY_MASS={lib_mm}＝view", lib_mm == MIN_MINORITY_MASS)
        chk(f"evidence.MIN_DISCRIMINATING_BANDS={lib_nb}＝view",
            lib_nb == MIN_DISCRIMINATING_BANDS)
    except Exception as exc:
        chk(f"import evidence 常數 ({exc})", False)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def _check() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{VIEW}",))
        exists = cur.fetchone()[0]
        if not exists:
            print(f"✗ view `{VIEW}` 不在——請 `--apply`（M-G14）")
            return 1
        cur.execute(
            f"SELECT population_ok, confidence_band_usable, confidence_band_raw, "
            f"population_band_minority_mass "
            f"FROM {VIEW} LIMIT 1"
        )
        row = cur.fetchone()
        cur.execute(f"SELECT count(*) FROM {VIEW} WHERE confidence_band_usable IS NOT NULL")
        n_usable = cur.fetchone()[0]
        cur.execute(f"SELECT count(*) FROM {VIEW}")
        n_all = cur.fetchone()[0]
    print(f"── {VIEW} ──")
    print(f"  存在：✓；抽樣 population_ok={row[0]} usable={row[1]} raw={row[2]} "
          f"band_mm={row[3]}")
    print(f"  usable 非空 {n_usable}/{n_all}")
    # live 應因母體無鑑別力 → usable 全 NULL；若全 usable 卻 gate 宣稱 fail＝view 尺漂移
    if row[0] is False and n_usable == 0:
        print("  → 與 live discrimination 同向：母體不過 ⇒ usable 全空（誠實）")
        return 0
    if row[0] is True:
        print("  → 母體 gate 通過；usable 應暴露 raw band")
        return 0 if n_usable == n_all else 1
    print("  ✗ population_ok=False 但仍有 usable 非空——view 與判準分家")
    return 1


def _apply() -> int:
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()
    print(f"✓ CREATE OR REPLACE VIEW {VIEW}")
    return _check()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M-G14 KH8 honest view DDL")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--print-ddl", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.print_ddl:
        print(DDL)
        return 0
    if a.apply:
        return _apply()
    return _check()


if __name__ == "__main__":
    sys.exit(main())
