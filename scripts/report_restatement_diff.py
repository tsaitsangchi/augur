#!/usr/bin/env python
"""源 restatement 人裁佇列 — U5「diff 報告人裁、非自動 fail/pass」機械化(arena 前置 G2;計畫 §5.4/§6.6)。

🎯 這支在做什麼(白話):990ddea U5 判準=「源 restatement→diff 報告人裁(review),非自動 fail/pass」。
   本工具=其落地佇列:凍結段(≤PIN as-of)資料被上游改寫時(由 panel-hash verify mismatch/對帳 VM/
   人工發現),**登記一筆 diff 摘要進 restatement_review_queue(pending)**→人裁簽核(benign=良性修訂
   /action=需處置)。gate 裁判(evaluate_arena_admission)查「無 pending」——**pending 在帳=G2 不綠**
   (人裁完才放行,非自動判)。本工具零 API(#28):diff 來源=既有驗證工具之發現,非主動重抓。

守 #10(diff_summary 可溯源)· #15(人裁留痕 signed_by/at)· #12(DDL 單一住所=本檔)· #29a/d。
   SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md §5.4/§6.6。

執行指令矩陣:
  python scripts/report_restatement_diff.py                     # 無參數:佇列現況(唯讀)
  python scripts/report_restatement_diff.py --init              # 冪等建 restatement_review_queue
  python scripts/report_restatement_diff.py --add --table feature_values --summary '{"panel":"2026-03-31","note":"hash mismatch"}'
  python scripts/report_restatement_diff.py --signoff 3 --by hugo --verdict benign --note "FRED 合法修訂"
  python scripts/report_restatement_diff.py --selftest          # 純函式紅綠(零 DB 零 API)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS restatement_review_queue (
  id            bigserial PRIMARY KEY,
  source_table  text NOT NULL,
  vintage_from  date,
  vintage_to    date,
  diff_summary  jsonb NOT NULL,
  status        text NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','signed_off_benign','signed_off_action')),
  signed_by     text,
  signed_at     timestamptz,
  note          text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT chk_rrq_signed CHECK
    (status = 'pending' OR (signed_by IS NOT NULL AND signed_at IS NOT NULL))
);
COMMENT ON TABLE restatement_review_queue IS
  'U5 restatement 人裁佇列:凍結段被上游改寫之 diff 登記(pending)→人裁簽核(benign/action);gate 查無 pending 才放行——人裁非自動判';
"""

_VERDICT = {"benign": "signed_off_benign", "action": "signed_off_action"}


def _parse_summary(raw):
    """--add 之 diff_summary 驗 JSON(必 dict;可溯源 #10)。純函式(selftest 可測)。"""
    obj = json.loads(raw)
    if not isinstance(obj, dict) or not obj:
        raise ValueError("diff_summary 須為非空 JSON object")
    return obj


def init():
    with db.connect() as conn:
        conn.cursor().execute(DDL)
        conn.commit()
    print("✓ --init 完成(冪等):restatement_review_queue 就位")
    return 0


def add(table, summary_raw, vfrom, vto):
    summary = _parse_summary(summary_raw)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO restatement_review_queue (source_table,vintage_from,vintage_to,diff_summary) "
                    "VALUES (%s,%s,%s,%s) RETURNING id",
                    (table, vfrom, vto, json.dumps(summary, ensure_ascii=False)))
        rid = cur.fetchone()[0]
        conn.commit()
    print(f"✓ 登記 diff #{rid}(pending;{table})——人裁:--signoff {rid} --by <人> --verdict benign|action")
    return 0


def signoff(rid, by, verdict, note):
    if not by:
        sys.exit("✗ --signoff 需 --by(人裁留痕;AI 不代簽)")
    if verdict not in _VERDICT:
        sys.exit(f"✗ --verdict 須 benign|action(得 {verdict})")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE restatement_review_queue SET status=%s, signed_by=%s, signed_at=now(), note=%s "
                    "WHERE id=%s AND status='pending' RETURNING id",
                    (_VERDICT[verdict], by, note, rid))
        row = cur.fetchone()
        conn.commit()
    if not row:
        print(f"✗ #{rid} 不存在或非 pending(已簽核不得改判——重議=另 add 新列留痕)")
        return 1
    print(f"✓ #{rid} 簽核 {verdict}(by={by})")
    return 0


def _selftest():
    """純函式紅綠(零 DB 零 API #29a)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("_parse_summary 合法 JSON object", _parse_summary('{"a":1}') == {"a": 1})
    for bad in ('[]', '"str"', '{}', 'notjson'):
        try:
            _parse_summary(bad)
            chk(f"_parse_summary 拒 {bad!r}", False)
        except (ValueError, json.JSONDecodeError):
            chk(f"_parse_summary 拒 {bad!r}", True)
    chk("DDL 冪等+PK+CHECK 簽核", "CREATE TABLE IF NOT EXISTS" in DDL and "chk_rrq_signed" in DDL)
    chk("verdict 白名單=benign/action", set(_VERDICT) == {"benign", "action"})
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--table")
    ap.add_argument("--summary")
    ap.add_argument("--vintage-from", dest="vfrom")
    ap.add_argument("--vintage-to", dest="vto")
    ap.add_argument("--signoff", type=int, metavar="ID")
    ap.add_argument("--by")
    ap.add_argument("--verdict")
    ap.add_argument("--note")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.init:
        return init()
    if args.add:
        if not (args.table and args.summary):
            sys.exit("--add 需 --table 與 --summary '<json>'")
        return add(args.table, args.summary, args.vfrom, args.vto)
    if args.signoff:
        return signoff(args.signoff, args.by, args.verdict, args.note)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.restatement_review_queue')")
        if cur.fetchone()[0]:
            cur.execute("SELECT status, count(*) FROM restatement_review_queue GROUP BY status")
            rows = cur.fetchall()
            print("佇列現況:", rows if rows else "(表在、零列=無已知 restatement)")
        else:
            print("佇列現況:(表未建,先 --init)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
