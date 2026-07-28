#!/usr/bin/env python
"""SRC-QUALIFY 步② — pacing 政策落值(零網路、純 DB;P4P5-go,hugo 2026-07-28 親核政策值)。

🎯 這支在做什麼(白話):步①證據波後,凡「P1 路乙判入 ∩ 近 30 日 2xx OAI-PMH probe ∩ 倉自報
   completeListSize 在證據裡」的 re3data 倉,把 P5 三欄一次落齊——pace_seconds/quota_limit 取
   `source_pacing_policy`(人簽表)、est_scale 取 probe 證據之倉自報數(**不編數 #9**;無自報=跳過
   =誠實留人工桶)。provenance 記 adapter_config->'pacing'(含 probe_review_id 可回鏈)。
   不變式:「已落值 ⇒ P5 三欄齊」全有或全無;不碰 approval_status/enabled(審批唯 SRC-AUTO --run)。
守 #9/#10(est 唯倉自報、可回鏈)· #15(無自報誠實跳過)· #29a/b/d · #26(規則內自動)。
SSOT=reports/augur_src_p4p5_qualification_plan_20260728.md §三/§五。

執行指令矩陣:
  python scripts/set_source_pacing.py             # 無參數:現況(可落值/已落值/誠實缺數,唯讀)
  python scripts/set_source_pacing.py --dry-run   # 列將落值倉+值來源(零寫入)
  python scripts/set_source_pacing.py --run       # 落值(冪等;有 pacing provenance 者跳過)
  python scripts/set_source_pacing.py --selftest  # 零 DB 紅綠(純邏輯/不變式鎖)
"""
import argparse
import json
import sys
import time

import _bootstrap  # noqa: F401
from augur.core import db

PROBE_FRESH_DAYS = 30
POLICY_VERSION = "v1"


def eligible_rows(cur):
    """P1 判入 ∩ 新鮮 2xx OAI-PMH probe ∩ 未落值 → [(key, review_id, size)]。size=None 者由呼叫端誠實跳過。"""
    from auto_review_sources import classify_licenses
    cur.execute("SELECT kind, pattern, regime FROM license_regime_map")
    rm = cur.fetchall()
    cur.execute("""SELECT DISTINCT ON (s.source_key) s.source_key,
                          s.adapter_config->'re3data'->'licenses',
                          l.review_id, (l.probe_result->>'complete_list_size')
                   FROM knowledge_source s
                   JOIN knowledge_source_review_log l ON l.source_key = s.source_key
                   WHERE s.approval_status='proposed'
                     AND NOT (coalesce(s.adapter_config,'{}'::jsonb) ? 'pacing')
                     AND l.action='probe' AND l.probe_result->>'protocol'='OAI-PMH'
                     AND (l.probe_result->>'http_status')::int BETWEEN 200 AND 299
                     AND l.created_at > now() - make_interval(days => %s)
                   ORDER BY s.source_key, l.review_id DESC""", (PROBE_FRESH_DAYS,))
    out = []
    for k, lic, rid, size in cur.fetchall():
        if classify_licenses(lic or [], rm):
            out.append((k, rid, int(size) if size and size.isdigit() else None))
    return out


def apply_pacing(dry):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT protocol, pace_seconds, quota_limit FROM source_pacing_policy WHERE protocol='OAI-PMH'")
        pol = cur.fetchone()
        if not pol:
            print("⛔ source_pacing_policy 無 OAI-PMH 政策列(人簽前置未到)——不動")
            return 75
        _, pace, quota = pol
        rows = eligible_rows(cur)
        todo = [(k, rid, sz) for k, rid, sz in rows if sz is not None]
        skipped = len(rows) - len(todo)
        print(f"合格 {len(rows)} 倉:可落值 {len(todo)}｜無倉自報數誠實跳過 {skipped}(留人工桶,#9 不編)")
        for k, rid, sz in todo:
            if dry:
                print(f"  · {k}: pace={pace} quota={quota} est_scale='{sz}'(probe#{rid} 倉自報)")
                continue
            prov = json.dumps({"pacing": {"policy": POLICY_VERSION, "protocol": "OAI-PMH",
                                          "probe_review_id": rid,
                                          "at": time.strftime("%Y-%m-%dT%H:%M:%S")}})
            cur.execute("""UPDATE knowledge_source
                SET pace_seconds=%s, quota_limit=%s, est_scale=%s,
                    adapter_config = coalesce(adapter_config,'{}'::jsonb) || %s::jsonb
                WHERE source_key=%s AND approval_status='proposed'
                  AND NOT (coalesce(adapter_config,'{}'::jsonb) ? 'pacing')""",
                (pace, quota, str(sz), prov, k))
            if cur.rowcount:
                print(f"  ✓ {k}: pace={pace} quota={quota} est_scale='{sz}'(probe#{rid})")
        if not dry:
            conn.commit()
            print("→ 下一步:auto_review_sources.py --dry-run 重分桶(可自動桶應首次非空)→ P2 抽核 20")
        else:
            print("(--dry-run:未寫入)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT count(*) FILTER (WHERE adapter_config ? 'pacing') FROM knowledge_source
                       WHERE source_key LIKE 're3data_r3d%'""")
        print(f"  已落值:{cur.fetchone()[0]}")
        rows = eligible_rows(cur)
        n_sz = sum(1 for _, _, sz in rows if sz is not None)
        print(f"  待落值合格倉:{len(rows)}(有倉自報數 {n_sz}/誠實缺 {len(rows) - n_sz})")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import inspect
    src_el = inspect.getsource(eligible_rows)
    src_ap = inspect.getsource(apply_pacing)
    chk("政策值唯讀人簽表(無 hardcode 2.0/500)",
        "source_pacing_policy" in src_ap and "2.0" not in src_ap and "500" not in src_ap)
    chk("無政策列=rc 75 不動(fail-closed)", "return 75" in src_ap)
    chk("est 唯倉自報(probe 證據 complete_list_size)", "complete_list_size" in src_el)
    chk("無自報數=誠實跳過非補 0", "sz is not None" in src_ap and "誠實跳過" in src_ap)
    chk("冪等:pacing provenance 雙查(選取+UPDATE WHERE)",
        src_el.count("? 'pacing'") == 1 and src_ap.count("? 'pacing'") == 1)
    chk("probe 須 2xx+新鮮+OAI-PMH 協定", "BETWEEN 200 AND 299" in src_el
        and "make_interval" in src_el and "'OAI-PMH'" in src_el)
    chk("provenance 可回鏈(probe_review_id)", "probe_review_id" in src_ap)
    chk("不變式:不碰 approval_status/enabled",
        "SET approval_status" not in src_ap and "enabled" not in src_ap)
    chk("P1 判入複用 classify_licenses(單一住所)", "classify_licenses" in src_el)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="SRC-QUALIFY 步②:pacing 政策落值(零網路)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.dry_run or a.run:
        return apply_pacing(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
