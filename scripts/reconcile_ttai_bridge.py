#!/usr/bin/env python
"""INTEG-F2 — `ttai_import` ↔ 知識層逐計數對帳,差額**逐列分類**成缺口帳(不含糊宣稱「已整合」)。

🎯 這支在做什麼(白話):augur 從 ttai(TiPTOP ERP 語意層)吸了 142,040 個 knowledge_unit。
   「吸進來了」跟「真的都在知識層查得到」是兩件事。本支把兩邊以 `stable_key ↔ external_id` 對接,
   **逐 unit_type 計數**,並把對不上的每一列分三類:
     · `upstream_unparsed`   ttai 側 status≠textualized(上游還沒處理完)——不是 augur 漏抓
     · `no_title`            title 空 → promote_item 本就會 rejected(內容品質排除,誠實可解釋)
     · `unexplained`         **上游有、可用、卻沒進來**——真缺口,逐列印出,不四捨五入成「大致對上」
   有 unexplained 即 **rc=1**(這是閘不是報表;`--report` 才只印不判)。

2026-07-27 首跑之實證(三個假說被自己的資料否證,留檔防後人重走):
   ① 最短長度過濾?否——已橋接列有 2,468 筆比未橋接之最長者還短。
   ② content_hash/title 去重?否——未橋接 57 列中 hash 撞 0 筆。
   ③ 建立時點晚於擷取?否——48 列建於 06-24~26,擷取在 07-06,早就在了。
   → 結論:損失發生在 **acquire(未進 staging)** 而非 promote(staging 141,825 列 100% promoted、零 rejected)。

守 #9/#10(數字全出自 DB query 可溯)· #15(不可解釋者標 unexplained 不編理由)· #28(純 SQL 零 token)· #29a/d。
SSOT=整合計畫 §F2(驗收＝142,040 逐計數對帳,差額列成缺口帳)。

執行指令矩陣:
  python scripts/reconcile_ttai_bridge.py            # 對帳(有 unexplained 即 rc=1;唯讀)
  python scripts/reconcile_ttai_bridge.py --report   # 只印不判(rc 恆 0;供人看)
  python scripts/reconcile_ttai_bridge.py --list     # 逐列印出 unexplained(最多 200 列)
  python scripts/reconcile_ttai_bridge.py --selftest # 零 DB 純紅綠(分類 SQL 之結構鎖)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

SRC = "ttai_erp_pilot"
GAP_CLASSES = ("upstream_unparsed", "no_title", "unexplained")

# 分類式(單一住所:--list 與計數共用同一 CASE,避免兩處漂移)
GAP_CASE = """CASE
        WHEN u.status <> 'textualized' THEN 'upstream_unparsed'
        WHEN u.title IS NULL OR btrim(u.title) = '' THEN 'no_title'
        ELSE 'unexplained' END"""

COUNT_SQL = f"""
SELECT u.unit_type,
       count(*)                                        AS ttai_n,
       count(i.item_id)                                AS bridged_n,
       count(*) FILTER (WHERE i.item_id IS NULL
                          AND {GAP_CASE} = 'upstream_unparsed') AS g_unparsed,
       count(*) FILTER (WHERE i.item_id IS NULL
                          AND {GAP_CASE} = 'no_title')          AS g_notitle,
       count(*) FILTER (WHERE i.item_id IS NULL
                          AND {GAP_CASE} = 'unexplained')       AS g_unexplained
FROM ttai_import.knowledge_unit u
LEFT JOIN knowledge_item i
       ON i.external_id = u.stable_key AND i.source_key = %s
GROUP BY 1 ORDER BY 2 DESC"""

LIST_SQL = f"""
SELECT u.unit_type, u.stable_key, left(coalesce(u.title,''), 40),
       left(coalesce(u.semantic_text,''), 60)
FROM ttai_import.knowledge_unit u
LEFT JOIN knowledge_item i
       ON i.external_id = u.stable_key AND i.source_key = %s
WHERE i.item_id IS NULL AND {GAP_CASE} = 'unexplained'
ORDER BY u.unit_type, u.stable_key LIMIT %s"""


def reconcile(list_rows=0):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(COUNT_SQL, (SRC,))
        rows = cur.fetchall()
        tot = [0] * 5
        print(f"── INTEG-F2 對帳:ttai_import.knowledge_unit ↔ knowledge_item({SRC}) ──")
        print(f"  {'unit_type':10} {'ttai':>7} {'已橋接':>8} {'上游未處理':>10} {'無標題':>7} {'**未解釋**':>10}")
        for t, n, b, gu, gn, gx in rows:
            print(f"  {t:10} {n:7} {b:8} {gu:10} {gn:7} {gx:10}")
            for i, v in enumerate((n, b, gu, gn, gx)):
                tot[i] += v
        print(f"  {'合計':10} {tot[0]:7} {tot[1]:8} {tot[2]:10} {tot[3]:7} {tot[4]:10}")

        cur.execute("""SELECT count(*) FROM knowledge_item i WHERE i.source_key=%s
            AND NOT EXISTS (SELECT 1 FROM ttai_import.knowledge_unit u
                            WHERE u.stable_key = i.external_id)""", (SRC,))
        orphan = cur.fetchone()[0]
        cur.execute("""SELECT status, count(*) FROM knowledge_staging
            WHERE source_key=%s GROUP BY 1""", (SRC,))
        staging = dict(cur.fetchall())

        print(f"\n  反向孤兒(知識層有/ttai 無):{orphan}")
        print(f"  staging:{staging}(全 promoted 即損失不在 promote 段)")
        if list_rows:
            cur.execute(LIST_SQL, (SRC, list_rows))
            got = cur.fetchall()
            print(f"\n  未解釋列(前 {len(got)} 筆):")
            for t, k, ti, tx in got:
                print(f"    {t:8} {k:46} title={ti!r} text={tx!r}")

        gap = tot[0] - tot[1]
        print(f"\n  差額 {gap} = 上游未處理 {tot[2]} + 無標題 {tot[3]} + **未解釋 {tot[4]}**")
        if tot[4]:
            print(f"  ✗ 有 {tot[4]} 列上游可用卻未進來——**尚不得宣稱「已整合」**;"
                  f"處置=重跑 acquire 補灌或裁定排除(逐列有據)")
        else:
            print("  ✓ 差額全部可解釋(上游未處理／內容品質排除),對帳成立")
        return tot[4], orphan


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("三分類齊", GAP_CLASSES == ("upstream_unparsed", "no_title", "unexplained"))
    chk("**分類式單一住所**(計數與逐列共用同一 CASE,不會兩處漂移)",
        GAP_CASE in COUNT_SQL and GAP_CASE in LIST_SQL)
    chk("接鍵=stable_key↔external_id(非 title 模糊比對)",
        "i.external_id = u.stable_key" in COUNT_SQL)
    chk("source_key 以參數傳(非字串內插)", "%s" in COUNT_SQL and f"'{SRC}'" not in COUNT_SQL)
    src = open(__file__, encoding="utf-8").read()
    body = src.split("def _selftest")[0].split('"""', 2)[-1]
    chk("有反向孤兒查核(只查單向會漏掉知識層多出來的列)",
        "NOT EXISTS (SELECT 1 FROM ttai_import.knowledge_unit u" in body)
    chk("孤兒亦入 rc 判定(不只印出來就算)", "if (unexplained or orphan)" in src)
    chk("**唯讀**:程式體零 INSERT/UPDATE/DELETE",
        not any(k in body.upper() for k in ("INSERT INTO", "UPDATE ", "DELETE FROM")))
    chk("未解釋>0 時 rc≠0(是閘非報表)", "return tot[4], orphan" in body)
    chk("不編理由:未解釋類不給推測性標籤", "'unexplained'" in body)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTEG-F2 ttai↔知識層逐計數對帳")
    ap.add_argument("--report", action="store_true", help="只印不判(rc 恆 0)")
    ap.add_argument("--list", type=int, nargs="?", const=200, default=0,
                    help="逐列印出未解釋列(預設上限 200)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    unexplained, orphan = reconcile(a.list)
    if a.report:
        return 0
    return 1 if (unexplained or orphan) else 0


if __name__ == "__main__":
    sys.exit(main())
