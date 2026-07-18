#!/usr/bin/env python
"""存量鑄造 backfill — 現有名冊實體一次性 mint 入 entity_registry(Phase 2(b);ID.11 義務結清·存量側)。

🎯 這支在做什麼(白話):把系統**已在消費**的三份名冊實體,經 `resolve_or_mint` 單一入口補鑄永久 augur_id——
   · Security:TaiwanStockInfo 之真股票代碼(stock_id 數字開頭;含 ETF/特別股,皆有價證券個體);
   · Index:TaiwanStockInfo 之指數列(stock_id 非數字開頭 ∧ industry_category ∈ Index/大盤——來源自標,
     含 TAIEX/TPEx 大盤與各產業類指數;此即 core_gate 所稱 roster「污染」項之真身,於此正名為 Index 個體);
   · FredSeries:fred_series 觀測表之 distinct series_id。
   **冪等**(已繫 alias 者解析回同枚、零重鑄→重跑 minted=0)、**分批**(每批一交易 commit,resume-safe #6)、
   mint evidence=名冊來源列引用(#10 可溯源)。紅旗(detect_code_reuse)依 ID.43 鑄 provisional 不縫合並計數。
   僅 SELECT/INSERT(append-only ACL 型下可跑);數量以名冊實跑為準、不轉抄任何預設值(#9)。

守 ID.11(存量結清)· ID.43(紅旗 provisional)· #6(冪等分批)· #9/#10(數量實跑·evidence 可溯源)·
   #29(a 個別可執行/b 名冊住 DB/d 指令矩陣)· #3(不動 ingest.py;增量接線屬 Phase 2 後段另呈)。

執行指令矩陣:
  python scripts/backfill_entity_registry.py                 # graceful:印指令矩陣(零副作用)
  python scripts/backfill_entity_registry.py --check         # 唯讀:名冊數量+已繫/未繫存量、不寫入
  python scripts/backfill_entity_registry.py --apply         # 實跑鑄造(分批 commit;預設每批 500)
  python scripts/backfill_entity_registry.py --apply --batch-size 200
  python scripts/backfill_entity_registry.py --selftest      # 紅綠鎖(名冊定義/evidence 格式;免 DB 免 API)

⚠ 生產 apply 屬 P5 拍板事項;本腳本沙盒(DB_NAME=augur_sandbox)演練先行。
"""
from __future__ import annotations

import argparse
import sys
import time

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

# `from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest 零依賴可個別跑(#29)。

# 名冊定義(SQL 一律唯讀;值謂詞為來源自標語彙:industry_category='Index'/'大盤' 係 FinMind 對指數列之標記,
# '^[0-9]' 同 core_gate._REAL_STOCK_PREDICATE 之真股票代碼判準)
ROSTERS = [
    # (label, entity_type, code_system_attr, sql)
    ("Security", "Security", "CODE_SYSTEM_FINMIND_STOCK", """
        SELECT stock_id,
               'TaiwanStockInfo|stock_id=' || stock_id || '|date=' || COALESCE(max(date)::text, '') AS evidence_ref,
               max(date) AS valid_from
        FROM "TaiwanStockInfo" WHERE stock_id ~ '^[0-9]'
        GROUP BY stock_id ORDER BY stock_id"""),
    ("Index", "Index", "CODE_SYSTEM_FINMIND_STOCK", """
        SELECT stock_id,
               'TaiwanStockInfo|stock_id=' || stock_id
                 || '|industry_category=' || string_agg(DISTINCT industry_category, '|' ORDER BY industry_category)
                 AS evidence_ref,
               max(date) AS valid_from
        FROM "TaiwanStockInfo"
        WHERE stock_id !~ '^[0-9]' AND industry_category IN ('Index', '大盤')
        GROUP BY stock_id ORDER BY stock_id"""),
    ("FredSeries", "FredSeries", "CODE_SYSTEM_FRED_SERIES", """
        SELECT series_id,
               'fred_series|series_id=' || series_id
                 || '|obs=' || min(date)::text || '..' || max(date)::text AS evidence_ref,
               NULL::date AS valid_from
        FROM fred_series GROUP BY series_id ORDER BY series_id"""),
]

ACTOR = "scripts/backfill_entity_registry"

# 名冊分割前瞻縫隙之殘差計數(minors 批 RULING-2026-015):非數字碼 ∧ 非 Index/大盤 → 不落
# Security/Index 任一名冊之列;現況 0,>0 時=來源新增未涵蓋類目,誠實計數供人檢視、不靜默漏鑄。
RESIDUAL_SQL = """
    SELECT count(DISTINCT stock_id) FROM "TaiwanStockInfo"
    WHERE stock_id !~ '^[0-9]'
      AND (industry_category IS NULL OR industry_category NOT IN ('Index', '大盤'))"""


def read_roster(cur, sql):
    """名冊實讀 → [(external_code, evidence_ref, valid_from), …](唯讀;數量以此為準 #9)。"""
    cur.execute(sql)
    return cur.fetchall()


def mint_batch(cur, entries, entity_type, code_system, actor=ACTOR):
    """一批名冊列經 resolve_or_mint;回計數 dict(冪等:已繫者 resolved、零重鑄)。"""
    from augur.identity import resolve
    counts = {"minted": 0, "resolved": 0, "provisional_minted": 0,
              "provisional_resolved": 0, "ambiguous": 0, "red_flag": 0}
    for external_code, evidence_ref, valid_from in entries:
        r = resolve.resolve_or_mint(cur, code_system, external_code, entity_type,
                                    evidence_ref, actor, valid_from=valid_from)
        counts[r["action"]] += 1
        if r["red_flag"]:
            counts["red_flag"] += 1
    return counts


def _merge(total, part):
    for k, v in part.items():
        total[k] = total.get(k, 0) + v
    return total


def run_backfill(conn, batch_size=500, actor=ACTOR):
    """全名冊分批鑄造(每批一交易 commit;resume-safe);回 {label: counts}。"""
    from augur.core import db
    from augur.identity import resolve
    out = {}
    for label, entity_type, cs_attr, sql in ROSTERS:
        code_system = getattr(resolve, cs_attr)
        with db.transaction(conn) as cur:
            roster = read_roster(cur, sql)
        totals = {}
        for i in range(0, len(roster), batch_size):
            with db.transaction(conn) as cur:
                _merge(totals, mint_batch(cur, roster[i:i + batch_size],
                                          entity_type, code_system, actor))
        totals["roster"] = len(roster)
        out[label] = totals
    return out


def _check(cur):
    """唯讀現況:名冊數 vs 已繫 alias 存量(不寫入)。"""
    from augur.identity import resolve
    print("── backfill 現況(唯讀) ──")
    for label, _etype, cs_attr, sql in ROSTERS:
        code_system = getattr(resolve, cs_attr)
        roster = read_roster(cur, sql)
        cur.execute(
            "SELECT count(DISTINCT external_code) FROM entity_alias "
            "WHERE code_system=%s AND external_code = ANY(%s)",
            (code_system, [r[0] for r in roster] or ["_"]))
        bound = cur.fetchone()[0]
        print(f"  {label:<10} 名冊 {len(roster):>5} | 已繫 alias {bound:>5} | 未繫 {len(roster) - bound:>5}")
    cur.execute(RESIDUAL_SQL)
    residual = cur.fetchone()[0]
    print(f"  名冊殘差列(非數字∧非 Index/大盤,不落任一名冊){residual:>5}"
          + (" ⚠ >0:來源新增未涵蓋類目、須人檢視" if residual else ""))
    cur.execute("SELECT count(*) FROM entity_registry")
    print(f"  entity_registry 現有 {cur.fetchone()[0]} 列")


def _selftest():
    """紅綠鎖(名冊定義/evidence 不變式;免 DB 免 API、零 usage)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    labels = [r[0] for r in ROSTERS]
    chk("三份名冊(Security/Index/FredSeries)", labels == ["Security", "Index", "FredSeries"])
    chk("名冊 SQL 皆唯讀 SELECT(無 INSERT/UPDATE/DELETE)",
        all(sql.strip().upper().startswith("SELECT")
            and not any(w in sql.upper() for w in ("INSERT", "UPDATE", "DELETE", "TRUNCATE"))
            for _, _, _, sql in ROSTERS))
    chk("Security 用真股票代碼判準 ^[0-9](同 core_gate)",
        "~ '^[0-9]'" in dict((r[0], r[3]) for r in ROSTERS)["Security"])
    chk("Index 以來源自標 industry_category(Index/大盤)判別、非硬編碼名單",
        "industry_category IN ('Index', '大盤')" in dict((r[0], r[3]) for r in ROSTERS)["Index"])
    chk("名冊殘差計數 SQL 唯讀且=兩名冊謂詞之補集(非數字∧非 Index/大盤)",
        RESIDUAL_SQL.strip().upper().startswith("SELECT")
        and "!~ '^[0-9]'" in RESIDUAL_SQL
        and "NOT IN ('Index', '大盤')" in RESIDUAL_SQL
        and not any(w in RESIDUAL_SQL.upper() for w in ("INSERT", "UPDATE", "DELETE", "TRUNCATE")))
    chk("每份名冊 evidence 皆引名冊來源列(表名+鍵)",
        all(src in sql for (_, _, _, sql), src in
            zip(ROSTERS, ("TaiwanStockInfo|stock_id=", "TaiwanStockInfo|stock_id=", "fred_series|series_id="))))
    empty = mint_batch(None, [], "Security", "finmind:stock_id")
    chk("空批零 DB 可跑且計數鍵完整",
        set(empty) == {"minted", "resolved", "provisional_minted",
                       "provisional_resolved", "ambiguous", "red_flag"}
        and all(v == 0 for v in empty.values()))
    chk("actor 具名(P4.E6 斷言主體)", bool(ACTOR) and "backfill_entity_registry" in ACTOR)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="存量鑄造 backfill(三名冊→entity_registry;冪等分批;evidence=名冊來源列)")
    ap.add_argument("--check", action="store_true", help="唯讀:名冊數+已繫存量、不寫入")
    ap.add_argument("--apply", action="store_true", help="實跑鑄造(分批 commit)")
    ap.add_argument("--batch-size", type=int, default=500, help="每批列數(每批一交易;預設 500)")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.check or args.apply):
        ap.print_help()  # graceful:無參數零副作用(#29a)
        return 0
    from augur.core import db
    with db.connect() as conn:
        if args.check:
            with db.transaction(conn) as cur:
                _check(cur)
            return 0
        t0 = time.monotonic()
        out = run_backfill(conn, batch_size=args.batch_size)
        elapsed = time.monotonic() - t0
        print("── backfill 結果 ──")
        for label, c in out.items():
            print(f"  {label:<10} 名冊 {c['roster']:>5} | minted {c['minted']:>5} | resolved {c['resolved']:>5}"
                  f" | provisional(mint/res) {c['provisional_minted']}/{c['provisional_resolved']}"
                  f" | ambiguous {c['ambiguous']} | 紅旗 {c['red_flag']}")
        with db.transaction(conn) as cur:
            cur.execute("SELECT count(*) FROM entity_registry")
            print(f"  entity_registry 總列數 {cur.fetchone()[0]} | 耗時 {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
