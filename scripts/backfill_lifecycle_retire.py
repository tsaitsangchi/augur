#!/usr/bin/env python
"""下市 retire 事件 backfill — TaiwanStockDelisting → identity_lifecycle_event(Phase 2(d);裁③ retire 先行)。

🎯 這支在做什麼(白話):把來源下市紀錄表 TaiwanStockDelisting(date/stock_id/stock_name)逐筆結清為
   lifecycle **retire 事件**(RULING-2026-015 裁③:生產順序=型別載體→retire 先行→存量鑄造→屬性同步)——
   retire 屬 lifecycle.EVIDENCE_REQUIRED 九型別,evidence_ref=下市來源列(表名+鍵+名,#10 可溯源)。

   **關鍵語義(下市碼尚未鑄造=「預鑄 retired 身份」路徑)**:retire 先行時 registry 可能空——
   · 碼查無任何 alias → **先 mint 一枚 augur_id(evidence=下市紀錄列、alias=adopted:T.1 判準
     RULING-2026-014 已採認)再掛 retire 事件**。效果:後續存量鑄造遇同碼今日名冊列時,
     detect_code_reuse 紅旗成立 → 走 ID.43 provisional 分裂、不縫合(此即裁③要的效果)。
   · 碼已繫既有身(如沙盒 3,149 adopted 殘留=鑄造先行之錯序、或未來重跑)→ **不把 retire 掛上既有身**
     (既有身 evidence=今日名冊,指涉現存個體;掛上=強縫歷史)——改鑄 **provisional 分身**攜下市
     evidence 掛 retire(ID.43 存續邊界截斷精神;之後同碼 resolve 回既有活身=provisional_resolved+紅旗)。
   · 同枚下市列已有完全同 evidence 之 retire 事件 → already(冪等:重跑零新增)。
   **名實不符誠實計數**:下市名 ≠ 今日名冊 max(date) 名集 → 人裁佇列(表列印+可選 CSV),不強縫。

   **單實例防護(裁①)**:--apply 全程單一交易,首語句 pg_try_advisory_xact_lock(hashtext(LOCK_KEY))
   ——未取得=另一實例執行中,誠實中止零寫入;交易結束自動釋放。逐碼再取 resolve.acquire_code_lock
   (與 resolve_or_mint 同鍵派生 #12)互斥並行攝取。僅 SELECT/INSERT(augur_app 憲章表 ACL 型下可跑)。

   **--rehearse-clean(乾淨順序重演;沙盒驗證策略)**:沙盒殘留使真 code_system 無法重演「retire 先行」
   之生產順序——本模式以 rehearsal 專用 code_system 命名空間(候選解析鍵=code_system+code,與殘留隔離)
   於**單一交易內**先跑 retire backfill、再跑全名冊鑄造,實測生產順序之效果數(342 retire/3,149 minted
   含 235 provisional 預期),**結束一律 ROLLBACK 零殘留**。單線程回滾演練無並發可護且數千 advisory 鍵
   近 shared lock table 上限 → code_lock=False(誠實揭露,見 resolve.resolve_or_mint docstring)。

守 裁①(單實例+advisory lock)· 裁③(retire 先行)· ID.40(retire evidence 硬義務)· ID.43(不縫合)·
   #6(冪等)· #9/#10(數量實跑·evidence 可溯源)· #29(a 個別可執行/d 指令矩陣)· #3(不動 ingest.py)。

執行指令矩陣:
  python scripts/backfill_lifecycle_retire.py                    # graceful:印指令矩陣(零副作用)
  python scripts/backfill_lifecycle_retire.py --check            # 唯讀:預覽各路徑計數+名實不符佇列、不寫入
  python scripts/backfill_lifecycle_retire.py --apply            # 實跑(單一交易+單實例 advisory lock)
  python scripts/backfill_lifecycle_retire.py --apply --mismatch-csv reports/x.csv   # 佇列另存 CSV
  python scripts/backfill_lifecycle_retire.py --rehearse-clean   # 乾淨順序重演(rehearsal 命名空間;一律回滾)
  python scripts/backfill_lifecycle_retire.py --selftest         # 紅綠鎖(判準/SQL 不變式;免 DB 免 API)

⚠ 生產 apply 屬 P5 一次拍板事項(RULING-2026-015 主文 4);本腳本沙盒(DB_NAME=augur_sandbox)演練先行。
"""
from __future__ import annotations

import argparse
import csv
import sys
import time

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

# `from augur.core import db`(→psycopg2)延遲至 main() 內;identity 模組為純 Python、selftest 可 import。

ACTOR = "scripts/backfill_lifecycle_retire"
LOCK_KEY = "augur:phase2:retire_backfill"          # 單實例 advisory lock 鍵(hashtext)
ENTITY_TYPE = "Security"                            # 下市紀錄皆數字碼(T.1 判準域;實讀親證)
REHEARSAL_PREFIX = "rehearsal:"                     # 乾淨順序重演之 code_system 前綴(與殘留隔離)

# 下市名冊實讀(唯讀;evidence=來源列引用:表名+鍵(stock_id,date)+名,#10 可溯源、亦為冪等鍵)
DELISTING_SQL = """
    SELECT stock_id, stock_name, date,
           'TaiwanStockDelisting|stock_id=' || stock_id || '|date=' || date::text
             || '|name=' || COALESCE(stock_name, '') AS evidence_ref
    FROM "TaiwanStockDelisting" ORDER BY stock_id, date"""

# 名實不符人裁佇列(唯讀):下市名 ≠ 今日名冊 max(date) 當日名集之任一名 → 誠實列出、不強縫
MISMATCH_SQL = """
    WITH latest AS (
        SELECT stock_id, max(date) AS d FROM "TaiwanStockInfo" GROUP BY stock_id),
    roster_names AS (
        SELECT i.stock_id, string_agg(DISTINCT i.stock_name, '|' ORDER BY i.stock_name) AS names
        FROM "TaiwanStockInfo" i
        JOIN latest l ON i.stock_id = l.stock_id AND i.date IS NOT DISTINCT FROM l.d
        GROUP BY i.stock_id)
    SELECT d.stock_id, d.date, d.stock_name, r.names
    FROM "TaiwanStockDelisting" d JOIN roster_names r ON r.stock_id = d.stock_id
    WHERE NOT EXISTS (
        SELECT 1 FROM "TaiwanStockInfo" i
        JOIN latest l2 ON i.stock_id = l2.stock_id AND i.date IS NOT DISTINCT FROM l2.d
        WHERE i.stock_id = d.stock_id AND i.stock_name IS NOT DISTINCT FROM d.stock_name)
    ORDER BY d.stock_id"""


def retire_action(candidate_ids, evidence_matched_ids):
    """純判準:碼之 alias 候選 augur_id 序列 + 已具本下市列 evidence 之 retire 事件者 → (action, augur_id|None)。

    action ∈ {'already','mint_retire','provisional_retire'}:
      already            — 本下市列已結清(同 evidence 之 retire 事件在案)=冪等重跑零新增。
      mint_retire        — 碼查無任何 alias(retire 先行、registry 空):預鑄 retired 身份
                           (mint+adopted alias+retire 事件;T.1 判準已採認 RULING-2026-014)。
      provisional_retire — 碼已繫既有身(殘留/錯序/重用):不掛 retire 上既有身(強縫歷史)、
                           改鑄 provisional 分身攜下市 evidence 掛 retire(ID.43 不縫合)。
    """
    distinct = list(dict.fromkeys(candidate_ids))
    matched = [a for a in distinct if a in frozenset(evidence_matched_ids)]
    if matched:
        return ("already", matched[0])
    if not distinct:
        return ("mint_retire", None)
    return ("provisional_retire", None)


def read_delisting(cur):
    """下市名冊實讀 → [(stock_id, stock_name, date, evidence_ref), …](唯讀;數量以此為準 #9)。"""
    cur.execute(DELISTING_SQL)
    return cur.fetchall()


def _evidence_matched(cur, augur_ids, evidence_ref):
    """候選中已具「本下市列 evidence 之 retire 事件」者(冪等鍵=evidence_ref 全等)。"""
    if not augur_ids:
        return frozenset()
    cur.execute(
        "SELECT DISTINCT augur_id FROM identity_lifecycle_event "
        "WHERE augur_id = ANY(%s) AND event_type='retire' AND evidence_ref=%s",
        (list(augur_ids), evidence_ref))
    return frozenset(r[0] for r in cur.fetchall())


def process_delisting(cur, rows, code_system, actor=ACTOR, dry_run=False, code_lock=True):
    """下市列逐筆結清 retire 事件;回計數 dict(冪等:重跑 already、零新增)。dry_run=僅判路徑不寫。

    重用既有機制:claim.resolve_alias(候選)/identifier.mint(鑄)/resolve._register_alias(繫 alias)/
    lifecycle.record_event(retire 屬 EVIDENCE_REQUIRED,evidence 硬義務由該機制與 DB CHECK 雙鎖)。
    code_lock:逐碼 advisory xact lock(裁①,與 resolve_or_mint 同鍵互斥);dry_run/單線程回滾演練不取。
    """
    from augur.identity import claim, identifier, lifecycle, resolve
    counts = {"delisting": 0, "retire_minted": 0, "retire_provisional": 0, "already": 0}
    for stock_id, _stock_name, delist_date, evidence_ref in rows:
        counts["delisting"] += 1
        if code_lock and not dry_run:
            resolve.acquire_code_lock(cur, code_system, stock_id)
        cands = [c["augur_id"] for c in claim.resolve_alias(cur, code_system, stock_id)]
        action, _aid = retire_action(cands, _evidence_matched(cur, cands, evidence_ref))
        if action == "already":
            counts["already"] += 1
            continue
        key = "retire_minted" if action == "mint_retire" else "retire_provisional"
        counts[key] += 1
        if dry_run:
            continue
        status = "adopted" if action == "mint_retire" else "provisional"
        aid = identifier.mint(cur, ENTITY_TYPE, evidence_ref, actor)
        resolve._register_alias(cur, aid, code_system, stock_id, status, evidence_ref)
        lifecycle.record_event(
            cur, aid, "retire", actor, evidence_ref=evidence_ref, valid_time=delist_date,
            note=("下市 backfill(裁③ retire 先行;預鑄 retired 身份)" if action == "mint_retire"
                  else "下市 backfill:碼已繫既有身→provisional 分身、不縫合(ID.43)"))
    return counts


def name_mismatch_rows(cur):
    """名實不符人裁佇列實讀 → [(stock_id, 下市日, 下市名, 今日名冊名集), …](唯讀、誠實計數)。"""
    cur.execute(MISMATCH_SQL)
    return cur.fetchall()


def _print_mismatch(rows, csv_path=None):
    print(f"── 名實不符人裁佇列(下市名≠今日名冊名;{len(rows)} 例、誠實計數不強縫)──")
    for sid, d, dname, rnames in rows:
        print(f"  {sid:<8} 下市 {d} {dname or '(無名)':<12} | 今日名冊 {rnames}")
    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["stock_id", "delist_date", "delist_name", "roster_names_at_max_date"])
            w.writerows(rows)
        print(f"  → 佇列 CSV 已寫 {csv_path}")


def acquire_single_instance(cur):
    """單實例防護(裁①):pg_try_advisory_xact_lock(hashtext(LOCK_KEY));False=另一實例執行中。"""
    cur.execute("SELECT pg_try_advisory_xact_lock(hashtext(%s)::bigint)", (LOCK_KEY,))
    return bool(cur.fetchone()[0])


def _report(counts, tag, elapsed=None):
    print(f"── {tag} ──")
    print(f"  下市列 {counts['delisting']} | 預鑄 retired(mint+adopted) {counts['retire_minted']}"
          f" | provisional 分身 {counts['retire_provisional']} | 已結清(冪等) {counts['already']}"
          + (f" | 耗時 {elapsed:.1f}s" if elapsed is not None else ""))


def rehearse_clean(conn):
    """乾淨順序重演(單一交易、一律 ROLLBACK 零殘留):rehearsal 命名空間先 retire 後全名冊鑄造。

    實測裁③ 生產順序效果數(retire 先行→存量鑄造之 provisional 分裂);與沙盒真 code_system 之
    3,149 adopted 殘留隔離(候選解析鍵=code_system+code)。單線程回滾演練 → code_lock=False
    (無並發可護;數千 advisory 鍵近 shared lock table 上限,誠實跳過)。
    """
    import backfill_entity_registry as bf
    from augur.identity import resolve
    cur = conn.cursor()
    try:
        rows = read_delisting(cur)
        r_cs = REHEARSAL_PREFIX + resolve.CODE_SYSTEM_FINMIND_STOCK
        t0 = time.monotonic()
        rc = process_delisting(cur, rows, r_cs, actor=ACTOR + "(rehearse)", code_lock=False)
        _report(rc, f"重演(1) retire 先行 [{r_cs}]", time.monotonic() - t0)
        print("── 重演(2) 全名冊鑄造(retire 之後)──")
        for label, etype, cs_attr, sql in bf.ROSTERS:
            cs = REHEARSAL_PREFIX + getattr(resolve, cs_attr)
            roster = bf.read_roster(cur, sql)
            c = _mint_roster_nolock(cur, bf, roster, etype, cs)
            print(f"  {label:<10} 名冊 {len(roster):>5} | minted {c['minted']:>5}"
                  f" | provisional_minted {c['provisional_minted']:>4} | resolved {c['resolved']}"
                  f" | ambiguous {c['ambiguous']} | 紅旗 {c['red_flag']}")
        # 僅計本重演交易之列(actor=…(rehearse) 只活在本交易、結束即回滾;evidence 前綴分辨 retire 預鑄 vs 名冊鑄)
        cur.execute("SELECT count(*) FROM entity_registry WHERE minted_by = %s "
                    "AND evidence_ref LIKE 'TaiwanStockDelisting|%%'", (ACTOR + "(rehearse)",))
        n_retire = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE event_type='retire' "
                    "AND actor = %s", (ACTOR + "(rehearse)",))
        print(f"  重演交易內:retire backfill 預鑄 {n_retire} 身 | retire 事件 {cur.fetchone()[0]} 枚")
    finally:
        conn.rollback()
        print("── 已 ROLLBACK(rehearsal 零殘留)──")


def _mint_roster_nolock(cur, bf, roster, entity_type, code_system):
    """重演用名冊鑄造:同 bf.mint_batch 計數形,惟 code_lock=False(單線程回滾演練,見 rehearse_clean)。"""
    from augur.identity import resolve
    counts = {"minted": 0, "resolved": 0, "provisional_minted": 0,
              "provisional_resolved": 0, "ambiguous": 0, "red_flag": 0}
    for external_code, evidence_ref, valid_from in roster:
        r = resolve.resolve_or_mint(cur, code_system, external_code, entity_type,
                                    evidence_ref, ACTOR + "(rehearse)", valid_from=valid_from,
                                    code_lock=False)
        counts[r["action"]] += 1
        if r["red_flag"]:
            counts["red_flag"] += 1
    return counts


def _selftest():
    """紅綠鎖(retire_action 判準/SQL 唯讀不變式/機制重用;免 DB 免 API、零 usage)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("同 evidence 已結清→already(冪等)", retire_action(["a"], {"a"}) == ("already", "a"))
    chk("碼查無 alias→mint_retire(預鑄 retired 身份;retire 先行)",
        retire_action([], set()) == ("mint_retire", None))
    chk("碼已繫既有身(無本列 evidence)→provisional_retire(不縫合 ID.43)",
        retire_action(["a"], set()) == ("provisional_retire", None))
    chk("多候選其一已結清→already(不重複鑄)", retire_action(["a", "b"], {"b"}) == ("already", "b"))
    chk("候選去重保序", retire_action(["a", "a"], set()) == ("provisional_retire", None))
    for label, sql in (("DELISTING_SQL", DELISTING_SQL), ("MISMATCH_SQL", MISMATCH_SQL)):
        chk(f"{label} 唯讀 SELECT(無 INSERT/UPDATE/DELETE/TRUNCATE)",
            not any(w in sql.upper() for w in ("INSERT", "UPDATE", "DELETE", "TRUNCATE")))
    chk("evidence=下市來源列引用(表名+鍵+名;亦為冪等鍵)",
        "'TaiwanStockDelisting|stock_id='" in DELISTING_SQL and "|date=" in DELISTING_SQL)
    from augur.identity import lifecycle, resolve
    chk("retire 屬 lifecycle EVIDENCE_REQUIRED(ID.40 九型別;重用既有機制非自維)",
        lifecycle.evidence_required("retire"))
    chk("per-code lock 單一住所=resolve.acquire_code_lock(裁① 同鍵互斥 #12)",
        callable(getattr(resolve, "acquire_code_lock", None)))
    empty = process_delisting(None, [], "test:cs", dry_run=True)
    chk("空名冊零 DB 可跑且計數鍵完整",
        set(empty) == {"delisting", "retire_minted", "retire_provisional", "already"}
        and all(v == 0 for v in empty.values()))
    chk("actor 具名(P4.E6)且 rehearsal 前綴隔離",
        "backfill_lifecycle_retire" in ACTOR and REHEARSAL_PREFIX.endswith(":"))
    chk("單實例 LOCK_KEY 具名", bool(LOCK_KEY) and "retire_backfill" in LOCK_KEY)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="下市 retire 事件 backfill(TaiwanStockDelisting→lifecycle retire;裁③ retire 先行;"
                    "冪等單一交易+單實例 advisory lock)")
    ap.add_argument("--check", action="store_true", help="唯讀:預覽路徑計數+名實不符佇列、不寫入")
    ap.add_argument("--apply", action="store_true", help="實跑(單一交易;pg_try_advisory_xact_lock 單實例)")
    ap.add_argument("--rehearse-clean", action="store_true",
                    help="乾淨順序重演(rehearsal 命名空間、一律 ROLLBACK 零殘留)")
    ap.add_argument("--mismatch-csv", metavar="PATH", help="名實不符人裁佇列另存 CSV")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.check or args.apply or args.rehearse_clean):
        ap.print_help()  # graceful:無參數零副作用(#29a)
        return 0
    from augur.core import db
    from augur.identity import resolve
    with db.connect() as conn:
        if args.rehearse_clean:
            rehearse_clean(conn)
            return 0
        t0 = time.monotonic()
        with db.transaction(conn) as cur:   # --apply 全程單一交易(342 列小量;原子=零孤兒)
            if args.apply and not acquire_single_instance(cur):
                print("⚠ 另一實例執行中(pg_try_advisory_xact_lock 未取得)——單實例防護(裁①),中止零寫入")
                return 2
            rows = read_delisting(cur)
            counts = process_delisting(cur, rows, resolve.CODE_SYSTEM_FINMIND_STOCK,
                                       dry_run=args.check)
            mism = name_mismatch_rows(cur)
            _report(counts, "預覽(唯讀)" if args.check else "backfill 結果", time.monotonic() - t0)
            _print_mismatch(mism, csv_path=args.mismatch_csv)
            cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE event_type='retire'")
            print(f"  identity_lifecycle_event retire 事件現存 {cur.fetchone()[0]} 枚"
                  + ("(唯讀、未寫入)" if args.check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
