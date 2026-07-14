#!/usr/bin/env python
"""知識庫 admission/隔離健檢 — 日常可跑之 runtime 不變式哨兵(#29 可重用工具)。

🎯 這支在做什麼(白話):唯讀查 DB,機械斷言知識庫 admission 邊界之命門與隔離不變式在
   「schema(約束在位)」與「live 資料」兩層皆成立——
   ① SCHEMA:必要 CHECK 約束存在於 knowledge_item_text(owned_local⇒local_private 命門 /
      擋 ai_generated / access_scope 值域 / license 白名單),偵測換機重建或誤 DROP 使命門牆
      消失之 schema drift(2026-07-14 對抗審查實證:chk_itext_owned_local_private 存在 live DB
      但無 repo migration 重建它——此哨兵即該類 drift 的日常偵測)。
   ② 資料:零 ai_generated(命門 #1)、零 owned_local 非 local_private(隔離)、全文 license 全白名單、
      provenance(source_key/license/source_type)完整度。
   白名單一律引 SSOT(corpus.LICENSE_WHITELIST / admission.SOURCE_TYPE_WHITELIST),不 hardcode(#29b)。
   exit 0=健康;exit 1=FAIL(約束缺失或不變式違反=命門破口,修復優先);--strict 下 exit 2=有 WARN。

守 #1(擋 AI 生成入庫)· #15(裁決全出 DB query 非我以為)· #12(白名單引 SSOT)· #29(個別可執行/graceful/可重用)。

執行指令矩陣:
  python scripts/verify_knowledge_admission_health.py            # 全健檢(唯讀)、印報告 + exit code
  python scripts/verify_knowledge_admission_health.py --json     # 機器可讀(exit 0=綠)
  python scripts/verify_knowledge_admission_health.py --domain finance  # 限某 domain 之資料層檢查
  python scripts/verify_knowledge_admission_health.py --strict   # WARN 亦視為不綠(exit 2)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

OK, WARN, FAIL = "OK", "WARN", "FAIL"

# 必要之 knowledge_item_text CHECK 約束(命門/隔離之 DB 層物理牆);缺一即 schema drift=FAIL。
# def 子字串用於在名稱之外做語義確認(防同名不同義)。
REQUIRED_CHECKS = [
    ("chk_itext_owned_local_private", "owned_local", "owned_local⇒local_private 隔離命門"),
    ("chk_itext_source_type", "ai_generated", "擋 ai_generated 入庫(命門 #1)"),
    ("chk_itext_access_scope", "local_private", "access_scope 值域(public/local_private)"),
]


def _add(results, level, name, detail):
    results.append({"level": level, "check": name, "detail": detail})


def _check_schema(cur, results):
    """① 必要 CHECK 約束在位(抓換機/DROP 導致的命門牆消失)。"""
    from augur.knowledge import corpus
    cur.execute(
        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid='knowledge_item_text'::regclass AND contype='c'"
    )
    live = {n: d for n, d in cur.fetchall()}
    for name, needle, desc in REQUIRED_CHECKS:
        d = live.get(name)
        if d is None:
            _add(results, FAIL, f"schema:{name}", f"缺 CHECK『{desc}』——命門牆不存在(schema drift)")
        elif needle not in d:
            _add(results, FAIL, f"schema:{name}", f"CHECK 存在但語義不符(缺 {needle!r}):{d}")
        else:
            _add(results, OK, f"schema:{name}", desc)
    # license 白名單 CHECK:任一 CHECK def 涵蓋全部 SSOT 白名單值
    lic_ok = any(all(v in d for v in corpus.LICENSE_WHITELIST) for d in live.values())
    _add(results, OK if lic_ok else FAIL, "schema:license_whitelist",
         "license 白名單 CHECK 涵蓋 " + "/".join(corpus.LICENSE_WHITELIST) if lic_ok
         else "無 CHECK 涵蓋完整 license 白名單(SSOT=corpus.LICENSE_WHITELIST)")


def _check_data(cur, results, domain):
    """② live 資料層命門/隔離/provenance 不變式。"""
    from augur.knowledge import corpus
    dom_join = ""
    dom_args = ()
    if domain:
        dom_join = ("JOIN knowledge_item i ON i.item_id=t.item_id AND i.domain=%s")
        dom_args = (domain,)

    def cnt(where, *a):
        cur.execute(f"SELECT count(*) FROM knowledge_item_text t {dom_join} WHERE {where}", dom_args + a)
        return cur.fetchone()[0]

    # 命門 #1:零 ai_generated
    n = cnt("t.source_type='ai_generated'")
    _add(results, OK if n == 0 else FAIL, "data:ai_generated",
         "零 AI 生成入庫" if n == 0 else f"{n} 筆 source_type=ai_generated(命門破口)")
    # 隔離:零 owned_local 非 local_private
    n = cnt("t.license='owned_local' AND t.access_scope IS DISTINCT FROM 'local_private'")
    _add(results, OK if n == 0 else FAIL, "data:owned_local_isolation",
         "owned_local 全 local_private" if n == 0 else f"{n} 筆 owned_local 非 local_private(隔離破口)")
    # 全文 license 白名單(seq>0)
    wl = set(corpus.LICENSE_WHITELIST)
    cur.execute(
        f"SELECT t.license, count(*) FROM knowledge_item_text t {dom_join} "
        f"WHERE t.seq>0 GROUP BY t.license", dom_args)
    bad = {lic: c for lic, c in cur.fetchall() if lic not in wl}
    _add(results, OK if not bad else FAIL, "data:fulltext_license",
         "全文 license 全白名單" if not bad else f"非白名單全文 license:{bad}")
    # provenance 完整度(缺=WARN,可溯源性非洩漏)
    cur.execute(f"SELECT count(*) FROM knowledge_item i WHERE i.source_key IS NULL"
                + (" AND i.domain=%s" if domain else ""), dom_args)
    n = cur.fetchone()[0]
    _add(results, OK if n == 0 else WARN, "prov:item_source_key",
         "item source_key 全回填" if n == 0 else f"{n} 筆 knowledge_item source_key NULL")
    n = cnt("t.license IS NULL")
    _add(results, OK if n == 0 else WARN, "prov:license",
         "item_text license 全有值" if n == 0 else f"{n} 筆 item_text license NULL")
    n = cnt("t.source_type IS NULL")
    _add(results, OK if n == 0 else WARN, "prov:source_type",
         "item_text source_type 全有值" if n == 0 else f"{n} 筆 item_text source_type NULL(可溯源性缺口)")


def run(cur, domain=None):
    results = []
    _check_schema(cur, results)
    _check_data(cur, results, domain)
    return results


def _print_report(results, domain):
    icon = {OK: "✓", WARN: "⚠", FAIL: "✗"}
    print(f"知識庫 admission/隔離健檢" + (f"(domain={domain})" if domain else "(全域)"))
    for r in results:
        print(f"  {icon[r['level']]} {r['check']}: {r['detail']}")
    n_fail = sum(1 for r in results if r["level"] == FAIL)
    n_warn = sum(1 for r in results if r["level"] == WARN)
    verdict = "✗ FAIL(命門/隔離破口或約束缺失)" if n_fail else ("⚠ WARN" if n_warn else "✓ 健康")
    print(f"總判:{verdict} | FAIL {n_fail} / WARN {n_warn} / 共 {len(results)}")
    return n_fail, n_warn


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--domain")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help:
        print(__doc__)
        return 0

    from augur.core import db
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            results = run(cur, args.domain)
    except Exception as e:  # noqa: BLE001  DB 不可用時 graceful(#29a、R5 教訓:不裸 traceback)
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(__doc__.split("執行指令矩陣:")[0].rstrip())
            print(f"\n(DB 不可用,無法健檢:{e})")
        return 3

    n_fail = sum(1 for r in results if r["level"] == FAIL)
    n_warn = sum(1 for r in results if r["level"] == WARN)
    if args.json:
        print(json.dumps({"ok": n_fail == 0, "fail": n_fail, "warn": n_warn, "results": results},
                         ensure_ascii=False))
    else:
        _print_report(results, args.domain)
    if n_fail:
        return 1
    if args.strict and n_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
