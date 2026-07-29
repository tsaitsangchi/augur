#!/usr/bin/env python
"""authority_tier 欄遷移＋71 源 backfill — TIER-全表-核可(hugo 2026-07-29)之落地。

🎯 這支在做什麼(白話):rdai 憲章 §3.3 權威層級移植——`knowledge_source.authority_tier` 一欄
   (CHECK 七值、可 NULL=未評)＋把 hugo 核可之 71 列從**提案表報告原文解析 backfill**
   (git 內報告=簽核 SSOT;解析列數≠71 即 fail-closed 拒跑,防轉抄誤差)。
   落地即活化 SRC-AUTO P6 謂詞(tier ∉ {T3,T4} 才可自動批;auto_review tier_wired 偵測既有)。
   誠實註記:未評(NULL)源依 P6 簽核原文**放行**(僅 T3/T4 必人);要收緊 NULL 亦必人=另簽。
守 #9/#10(值全出簽核報告可溯)· #15(列數不符 fail-closed)· #29a/d · #30(ALTER 前查長交易)。
簽核 SSOT=reports/augur_authority_tier_proposal_20260728.md(hugo「TIER-全表-核可」2026-07-29)。

執行指令矩陣:
  python scripts/migrate_authority_tier_ddl.py            # 無參數:現況(欄在?分佈?,唯讀)
  python scripts/migrate_authority_tier_ddl.py --apply    # 遷移+backfill(冪等)
  python scripts/migrate_authority_tier_ddl.py --dry-run  # 只印解析結果與 SQL
  python scripts/migrate_authority_tier_ddl.py --selftest # 零 DB 紅綠(解析器 fixture)
"""
import argparse
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

PROPOSAL = Path(__file__).resolve().parent.parent / "reports" / "augur_authority_tier_proposal_20260728.md"
TIERS = ("T0", "T1", "T2", "T3", "T4", "internal", "NA_philosophy")
EXPECT_N = 71

DDL = """
ALTER TABLE knowledge_source ADD COLUMN IF NOT EXISTS authority_tier TEXT
    CHECK (authority_tier IN ('T0','T1','T2','T3','T4','internal','NA_philosophy'));
COMMENT ON COLUMN knowledge_source.authority_tier IS
    'rdai §3.3 權威層級(TIER-全表-核可 2026-07-29;NULL=未評;SRC-AUTO P6 讀此欄)';
"""

_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*([A-Za-z0-9_]+)\*\*\s*\|")


def parse_proposal(text):
    """提案表 md → [(source_key, tier)];tier 非法值即丟(fail-closed 由呼叫端計數)。純函式。"""
    out = []
    for ln in text.splitlines():
        m = _ROW.match(ln)
        if m and m.group(2) in TIERS:
            out.append((m.group(1), m.group(2)))
    return out


def apply(dry):
    rows = parse_proposal(PROPOSAL.read_text(encoding="utf-8"))
    if len(rows) != EXPECT_N:
        print(f"⛔ 解析 {len(rows)} 列 ≠ 簽核 {EXPECT_N} 列——fail-closed 拒跑(#15,防轉抄/表改動)")
        return 75
    if dry:
        print(DDL)
        for k, t in rows[:8]:
            print(f"  {k:32} → {t}")
        print(f"  …共 {len(rows)} 列(--dry-run 未執行)")
        return 0
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()
            AND state <> 'idle' AND pid <> pg_backend_pid()
            AND now() - xact_start > interval '5 minutes'""")
        if cur.fetchone()[0]:
            print("⛔ 有 >5 分鐘長交易在跑——ALTER 會排鎖風暴(#30),稍後再跑")
            return 75
        cur.execute(DDL)
        n = 0
        for k, t in rows:
            cur.execute("""UPDATE knowledge_source SET authority_tier=%s
                WHERE source_key=%s AND (authority_tier IS DISTINCT FROM %s)""", (t, k, t))
            n += cur.rowcount
        print(f"✓ 欄落地+backfill 寫入 {n} 列(冪等;簽核值全出提案表)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT 1 FROM information_schema.columns
            WHERE table_name='knowledge_source' AND column_name='authority_tier'""")
        if not cur.fetchone():
            print("  (欄未建;--apply)")
            return 0
        cur.execute("""SELECT coalesce(authority_tier,'(未評)'), count(*) FROM knowledge_source
            WHERE approval_status='active' GROUP BY 1 ORDER BY 2 DESC""")
        for r in cur.fetchall():
            print(f"  {r[0]:16} {r[1]}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    FIX = """| source_key | a | d | l | **建議 tier** | 理由 |
| `arxiv_search` | arxiv | general | cc | **T1** | 預印本 |
| `x_bad` | g | g | g | **T9** | 非法值 |
| `ctext_books` | g | philosophy | pd | **NA_philosophy** | 原典 |
文字行不匹配
| `curation_biology` | manual_file | biology | owned | **internal** | 內部 |"""
    rows = parse_proposal(FIX)
    chk("解析:合法列全收", ("arxiv_search", "T1") in rows and ("ctext_books", "NA_philosophy") in rows
        and ("curation_biology", "internal") in rows)
    chk("解析:非法 tier 丟棄(fail-closed 計數會抓)", all(k != "x_bad" for k, _ in rows))
    chk("解析:表頭/雜行不誤收", len(rows) == 3)
    chk("七值 CHECK 與解析白名單同源", all(t in DDL for t in TIERS))
    import inspect
    src = inspect.getsource(apply)
    chk("列數≠71=拒跑", "EXPECT_N" in src and "return 75" in src)
    chk("ALTER 前查長交易(#30)", "xact_start" in src)
    chk("backfill 冪等(IS DISTINCT FROM)", "IS DISTINCT FROM" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="authority_tier 遷移+backfill(TIER-全表-核可)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
