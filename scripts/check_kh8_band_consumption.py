#!/usr/bin/env python3
"""🎯 KH8 band 消費側探針——直讀基表 `confidence_band` 路徑數＋honest view 落地（M-G14）。

守原則 #15（有直讀假訊號路徑就要紅）· #28（本地 grep＋唯讀 SQL）· #29a/d · #35。

驗收（master 第 23 步）：今日 live **直讀路徑數 > 0 即紅**（全綠＝未通過）。
honest view 另由 `migrate_kh8_honest_view_ddl.py` 建；本支不改消費者（遷移屬後續）。

執行指令矩陣
------------
    python3 scripts/check_kh8_band_consumption.py            # 無參數＝--check
    python3 scripts/check_kh8_band_consumption.py --check    # grep 直讀＋view 現況；路徑>0 → rc=1
    python3 scripts/check_kh8_band_consumption.py --json
    python3 scripts/check_kh8_band_consumption.py --selftest
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
VIEW = "knowhow_evidence_weight_honest"
# 直讀＝指向基表且取 confidence_band（排除 evidence.py 寫入軸、本二支探針／DDL、測試字樣）
SKIP_PATH_PARTS = (
    "/knowledge/evidence.py",
    "/check_kh8_band_consumption.py",
    "/migrate_kh8_honest_view_ddl.py",
    "/migrate_kh8_kh9_min_ddl.py",
)
BAND_LINE = re.compile(r"confidence_band")
BASE_TABLE = re.compile(r"knowhow_evidence_weight(?!_honest)")


def is_direct_read_hit(path: str, line: str) -> bool:
    """純函式：此行是否為『基表＋confidence_band』消費向嫌疑。"""
    if any(p in path.replace("\\", "/") for p in SKIP_PATH_PARTS):
        return False
    if "confidence_band_usable" in line or "confidence_band_raw" in line:
        return False
    if "_honest" in line and "confidence_band" in line:
        return False
    return bool(BAND_LINE.search(line)) and (
        bool(BASE_TABLE.search(line))
        or "confidence_band" in line  # JOIN 分多行：同檔另有基表命中才計——見 scan
    )


def classify_file_hits(path: str, lines: list[str]) -> list[tuple[int, str]]:
    """一檔多行：檔內同時見基表名與 confidence_band 之 band 行＝直讀嫌疑。純函式。"""
    joined = "\n".join(lines)
    if not BASE_TABLE.search(joined):
        return []
    if any(p in path.replace("\\", "/") for p in SKIP_PATH_PARTS):
        return []
    out = []
    for i, ln in enumerate(lines, 1):
        if BAND_LINE.search(ln) and "confidence_band_usable" not in ln \
                and "confidence_band_raw" not in ln:
            out.append((i, ln.strip()[:160]))
    return out


def scan_repo(root: Path) -> list[dict]:
    hits = []
    for p in sorted(root.rglob("*.py")):
        rel = str(p.relative_to(root))
        if any(x in rel for x in ("venv/", ".git/", "__pycache__/", "site-packages/")):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, snip in classify_file_hits(rel, text.splitlines()):
            hits.append({"path": rel, "line": lineno, "snip": snip})
    return hits


def _check(*, as_json=False) -> int:
    hits = scan_repo(REPO)
    view_ok = False
    usable_n = None
    pop_ok = None
    try:
        from augur.core import db
        with db.connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (f"public.{VIEW}",))
            view_ok = bool(cur.fetchone()[0])
            if view_ok:
                cur.execute(
                    f"SELECT bool_or(population_ok), "
                    f"count(*) FILTER (WHERE confidence_band_usable IS NOT NULL) "
                    f"FROM {VIEW}"
                )
                pop_ok, usable_n = cur.fetchone()
    except Exception as exc:
        err = str(exc)
    else:
        err = None

    snap = {
        "direct_read_n": len(hits),
        "direct_reads": hits[:30],
        "view_exists": view_ok,
        "population_ok": pop_ok,
        "usable_nonnull_n": usable_n,
        "error": err,
    }
    # 驗收：直讀 >0 必紅；view 缺亦紅
    rc = 1 if (len(hits) > 0 or not view_ok) else 0
    snap["rc"] = rc
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
        return rc

    print("── KH8 band 消費側探針（M-G14）──")
    print(f"  直讀嫌疑路徑：{len(hits)}（>0 即紅＝今日通過條件）")
    for h in hits[:12]:
        print(f"    {h['path']}:{h['line']}: {h['snip']}")
    if len(hits) > 12:
        print(f"    …另 {len(hits) - 12} 處")
    print(f"  honest view `{VIEW}`：{'在' if view_ok else '**不在**'}"
          + (f"；population_ok={pop_ok}；usable≠NULL 列={usable_n}" if view_ok else ""))
    if err:
        print(f"  DB：{err}")
    if rc:
        print("  → **紅** rc=1：尚有基表直讀 或 view 未建——"
              "修法＝改讀 confidence_band_usable／經 discrimination gate，不是放寬探針")
    else:
        print("  → 綠：零直讀且 view 在——⚠ 若母體仍無鑑別力卻綠＝先懷疑掃描漏檔")
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    fake = [
        'SELECT confidence_band FROM knowhow_evidence_weight',
        'x = weight["confidence_band"]',
    ]
    hits = classify_file_hits("scripts/reevaluate_kh_depths.py", fake)
    chk("真形：基表+band → 命中", len(hits) >= 1)
    chk("跳過 evidence.py",
        classify_file_hits("src/augur/knowledge/evidence.py", fake) == [])
    chk("honest usable 行不算直讀",
        classify_file_hits("scripts/x.py",
                           ["SELECT confidence_band_usable FROM knowhow_evidence_weight_honest"])
        == [])
    chk("無基表之純字樣不計",
        classify_file_hits("scripts/x.py", ['band = "confidence_band"']) == [])
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M-G14 KH8 band 消費探針")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check(as_json=a.json)


if __name__ == "__main__":
    sys.exit(main())
