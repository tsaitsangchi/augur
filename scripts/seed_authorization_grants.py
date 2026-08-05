#!/usr/bin/env python
"""authorization_grant 種子 — 將既有 Steward GO／拍板碼照錄為機讀授權列(C軌 P1 Phase 0a)。

🎯 這支在做什麼(白話):把已經發生過的授權(TWEVO-APPLY／predict-asof-write／sim 判決寫入)
   寫成 authorization_grant 列,供 action_log.resolve_grant_id 掛 FK——**內容照錄、不代簽新權**。
守 P5.E1 · #10(basis_doc_ref 可溯) · #29a。

執行指令矩陣:
  python scripts/seed_authorization_grants.py              # 無參數:印現況(唯讀)
  python scripts/seed_authorization_grants.py --run         # 冪等種子(同 action_type 已存在則跳過)
  python scripts/seed_authorization_grants.py --selftest    # 結構自測(零 DB)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401

# Steward 已明示之拍板／GO 照錄(非 AI 新授)——對話 2026-08-05 裁示 wire_all_three
SEEDS = (
    {
        "action_type": "evolution_apply",
        "grantor_identity": "steward:hugo",
        "effective_from": "2026-07-31",
        "basis_doc_ref": "TWEVO-APPLY-go / V2-AUTOADVANCE (run_evolution_iteration I5)",
        "note": "C軌P1種子;既有人閘碼照錄",
    },
    {
        "action_type": "predict_values_write",
        "grantor_identity": "steward:hugo",
        "effective_from": "2026-08-04",
        "basis_doc_ref": "audits/PREDICT-ASOF-WRITE-GO-20260804.md",
        "note": "C軌P1種子;predict-asof-write-go 照錄",
    },
    {
        "action_type": "sim_verdict_write",
        "grantor_identity": "steward:hugo",
        "effective_from": "2026-08-04",
        "basis_doc_ref": "SIM-FIRST-CELL / decide_sim_verdict killed|undecidable only",
        "note": "C軌P1種子;拒寫 promoted 不變",
    },
)


def status(cur):
    cur.execute("SELECT authorization_id, scope_params->>'action_type', basis_doc_ref "
                "FROM authorization_grant ORDER BY 1")
    rows = cur.fetchall()
    print(f"authorization_grant 列數={len(rows)}")
    for r in rows:
        print(f"  id={r[0]} action_type={r[1]} basis={r[2]}")


def seed(cur):
    n_new = 0
    for s in SEEDS:
        cur.execute(
            "SELECT 1 FROM authorization_grant WHERE scope_params->>'action_type'=%s LIMIT 1",
            (s["action_type"],))
        if cur.fetchone():
            print(f"  · skip 已存在 {s['action_type']}")
            continue
        cur.execute(
            "INSERT INTO authorization_grant (grantor_identity, scope_params, effective_from, "
            "basis_doc_ref, note) VALUES (%s,%s,%s,%s,%s) RETURNING authorization_id",
            (s["grantor_identity"], json.dumps({"action_type": s["action_type"]}),
             s["effective_from"], s["basis_doc_ref"], s["note"]))
        print(f"  ✓ 新種子 id={cur.fetchone()[0]} {s['action_type']}")
        n_new += 1
    return n_new


def _selftest():
    ok = True
    types = [s["action_type"] for s in SEEDS]
    ok = ok and len(types) == len(set(types)) == 3
    print(f"  {'✓' if ok else '✗'} 三 action_type 互異")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        cur = conn.cursor()
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            status(cur)
            return 0
        n = seed(cur)
        conn.commit()
        print(f"✓ 種子完成 new={n}")
        status(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
