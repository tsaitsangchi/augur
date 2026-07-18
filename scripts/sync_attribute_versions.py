#!/usr/bin/env python
"""屬性版本同步 — TaiwanStockInfo 快照差異偵測 → entity_attribute_version SCD-2 append(Phase 2(c);AUD-07)。

🎯 這支在做什麼(白話):把名冊之時變屬性(industry_category/stock_name/type)對每檔已鑄 augur_id 之
   **最新已存版本**做差異偵測——值異(或首見)→ `attribute_version.put_version` **append 新版本**(SCD-2、
   禁原地覆蓋;append-only ACL 型下純 INSERT 可跑),值同→零寫入(冪等:重跑 appended=0)。
   名冊現值口徑:每檔取 **max(date) 當日之列集**(FinMind 逐列 date=更新日;多列屬性以 sorted DISTINCT '|'
   聚合,如 2330 產業='半導體業|電子工業'——不擅裁單值、聚合口徑本身可回放);valid_from=該 max(date)。
   使 core_gate 產業判定日後可改讀 as-of(attribute_version.get_asof;消費切換屬 Phase 2 後段/Phase 6,
   本腳本只結清「屬性繫結存在」義務 ID.60)。範圍=Security 名冊(數字碼;指數列無時變屬性且 date=NULL,不納)。

守 ID.60(as-of 繫結)· AUD-07(產業判定 as-of 解之資料側)· #6(冪等)· #10(evidence=名冊來源列)·
   #29(a 個別可執行/d 指令矩陣)· #3(不動 core_gate 消費端)。

執行指令矩陣:
  python scripts/sync_attribute_versions.py                 # graceful:印指令矩陣(零副作用)
  python scripts/sync_attribute_versions.py --check         # 唯讀:差異統計(將 append 幾筆)、不寫入
  python scripts/sync_attribute_versions.py --apply         # 實跑差異 append(單一交易)
  python scripts/sync_attribute_versions.py --selftest      # 紅綠鎖(聚合/差異純邏輯;免 DB 免 API)

⚠ 生產 apply 屬 P5 拍板事項;沙盒(DB_NAME=augur_sandbox)演練先行。日常節拍併入 daily_maintenance 屬後段接線。
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date as _date

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

# `from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest 零依賴可個別跑(#29)。

ATTRS = ("industry_category", "stock_name", "type")
ACTOR = "scripts/sync_attribute_versions"

# 名冊現值:每檔 max(date) 當日列集之屬性聚合(sorted DISTINCT '|';IS NOT DISTINCT FROM 容 NULL date 邊角)
ROSTER_SQL = """
    WITH latest AS (
        SELECT stock_id, max(date) AS d FROM "TaiwanStockInfo"
        WHERE stock_id ~ '^[0-9]' GROUP BY stock_id)
    SELECT t.stock_id, l.d,
           string_agg(DISTINCT t.industry_category, '|' ORDER BY t.industry_category),
           string_agg(DISTINCT t.stock_name,        '|' ORDER BY t.stock_name),
           string_agg(DISTINCT t.type,              '|' ORDER BY t.type)
    FROM "TaiwanStockInfo" t
    JOIN latest l ON t.stock_id = l.stock_id AND t.date IS NOT DISTINCT FROM l.d
    GROUP BY t.stock_id, l.d ORDER BY t.stock_id
"""


def roster_rows(cur):
    """名冊現值實讀 → [{stock_id, valid_from, 各屬性}](唯讀)。"""
    cur.execute(ROSTER_SQL)
    return [{"stock_id": sid, "valid_from": d or _date.today(),
             "industry_category": ind, "stock_name": name, "type": typ}
            for sid, d, ind, name, typ in cur.fetchall()]


def latest_versions(cur, augur_id):
    """該 augur_id 每屬性之最新已存版本值(依 transaction_time;無版本之屬性缺鍵)。"""
    cur.execute(
        "SELECT DISTINCT ON (attribute_name) attribute_name, attribute_value "
        "FROM entity_attribute_version WHERE augur_id=%s "
        "ORDER BY attribute_name, transaction_time DESC, valid_from DESC", (augur_id,))
    return dict(cur.fetchall())


def diff_attrs(current, row):
    """純差異判準:最新已存版本 dict vs 名冊列 → 須 append 之 [(attr, new_value), …](值同→空)。"""
    return [(a, row[a]) for a in ATTRS if row.get(a) is not None and current.get(a) != row[a]]


def sync_versions(cur, rows, code_system, actor=ACTOR, dry_run=False):
    """差異偵測→SCD-2 append;回計數 dict。已鑄 alias 唯一未退役者才同步(未繫/歧義誠實計數、不強縫)。"""
    from augur.identity import attribute_version, claim, resolve
    from augur.identity.resolve import resolution_action
    counts = {"entities": 0, "appended": 0, "unchanged": 0, "unresolved": 0, "ambiguous": 0}
    for row in rows:
        cands = claim.resolve_alias(cur, code_system, row["stock_id"])
        cand_ids = [c["augur_id"] for c in cands]
        action, aid = resolution_action(cand_ids, resolve._retired_subset(cur, cand_ids))
        if action in ("mint", "provisional_mint"):
            counts["unresolved"] += 1        # 未鑄(先跑 backfill_entity_registry)
            continue
        if action == "ambiguous":
            counts["ambiguous"] += 1         # 待人解析、不強縫(ID.43)
            continue
        counts["entities"] += 1
        pend = diff_attrs(latest_versions(cur, aid), row)
        if not pend:
            counts["unchanged"] += 1
            continue
        evidence = f"TaiwanStockInfo|stock_id={row['stock_id']}|date={row['valid_from']}"
        for attr, value in pend:
            counts["appended"] += 1
            if not dry_run:
                attribute_version.put_version(
                    cur, aid, attr, value, row["valid_from"],
                    source_ref="TaiwanStockInfo", evidence_ref=evidence)
    return counts


def _report(counts, elapsed=None, dry=False):
    tag = "差異統計(唯讀)" if dry else "同步結果"
    print(f"── {tag} ──")
    print(f"  已繫實體 {counts['entities']} | append {counts['appended']} | 無變 {counts['unchanged']}"
          f" | 未鑄 {counts['unresolved']} | 歧義 {counts['ambiguous']}"
          + (f" | 耗時 {elapsed:.1f}s" if elapsed is not None else ""))


def _selftest():
    """紅綠鎖(diff_attrs 純邏輯 + 名冊 SQL 不變式;免 DB 免 API、零 usage)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    row = {"stock_id": "2330", "valid_from": _date(2026, 7, 16),
           "industry_category": "半導體業|電子工業", "stock_name": "台積電", "type": "twse"}
    chk("首見(無既存版本)→三屬性全 append",
        diff_attrs({}, row) == [("industry_category", "半導體業|電子工業"),
                                ("stock_name", "台積電"), ("type", "twse")])
    same = {"industry_category": "半導體業|電子工業", "stock_name": "台積電", "type": "twse"}
    chk("值同→零 append(冪等)", diff_attrs(same, row) == [])
    chk("單屬性異→僅該屬性 append",
        diff_attrs({**same, "type": "emerging"}, row) == [("type", "twse")])
    chk("名冊值 None 之屬性不 append(不以缺值覆蓋)",
        diff_attrs(same, {**row, "stock_name": None}) == [])
    chk("ATTRS 恰為名冊三時變屬性", ATTRS == ("industry_category", "stock_name", "type"))
    chk("名冊 SQL 唯讀且以 max(date) 列集聚合(sorted DISTINCT)",
        ROSTER_SQL.strip().upper().startswith("WITH")
        and "max(date)" in ROSTER_SQL and "string_agg(DISTINCT" in ROSTER_SQL
        and not any(w in ROSTER_SQL.upper() for w in ("INSERT", "UPDATE", "DELETE", "TRUNCATE")))
    chk("公開入口皆存在", all(callable(f) for f in (roster_rows, latest_versions, diff_attrs, sync_versions)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="TaiwanStockInfo 屬性差異偵測→entity_attribute_version SCD-2 append(冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:差異統計、不寫入")
    ap.add_argument("--apply", action="store_true", help="實跑差異 append(單一交易)")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.check or args.apply):
        ap.print_help()  # graceful:無參數零副作用(#29a)
        return 0
    from augur.core import db
    from augur.identity.resolve import CODE_SYSTEM_FINMIND_STOCK
    t0 = time.monotonic()
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = roster_rows(cur)
        counts = sync_versions(cur, rows, CODE_SYSTEM_FINMIND_STOCK, dry_run=args.check)
    _report(counts, time.monotonic() - t0, dry=args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
