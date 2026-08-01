#!/usr/bin/env python3
"""🎯 把「還沒試抓全文」從隱性缺列升為顯性列——121,389 件未嘗試終於可數、可分桶、可收斂。

守原則 #15(「未嘗試」與「license 阻擋」是兩回事,不得混桶;誠實非終態旗標)· #6(冪等
ON CONFLICT DO NOTHING、絕不覆寫既有終態;分批 commit 可續)· #12(status 封閉集 SSOT=
migrate_fulltext_status_ddl.py,本支只消費)· #28(全程本地 DB,零外部 API)。

起因(登錄冊 D1,2026-08-01):knowledge_item 121,389 件無全文亦無 fulltext_status 列——
「未嘗試」以**缺列**表達=不可數、不可查、與「表不存在」同形;KH4 亦無從區分
「還沒試」與「試過被擋」。本支回填 status='unattempted'(非終態,任何真實嘗試以
ON CONFLICT 覆寫),9 處消費端已改以 status<>'unattempted' 判終態(行為保存)。

reason 格式=「<bucket>：<人可讀說明>」——前綴機器可解析,分四桶:
  pending_oa_queue     DOI 形→fetch_oa_fulltext 佇列    pending_entity_queue  entity 型→fetch_entity_fulltext
  local_no_text        本機/SFTP 通道(件A隔離不外送)     no_resolver           現行工具鏈無法嘗試(誠實)

執行指令矩陣
------------
    python3 scripts/backfill_fulltext_unattempted.py                  # 無參數=--check(唯讀分桶)
    python3 scripts/backfill_fulltext_unattempted.py --check          # 唯讀:待回填分桶統計
    python3 scripts/backfill_fulltext_unattempted.py --apply          # 分批 20,000 回填至 0(冪等可續)
    python3 scripts/backfill_fulltext_unattempted.py --apply --limit 100   # 首輪最小(#25)
    python3 scripts/backfill_fulltext_unattempted.py --sweep-stale    # 刪已有全文之殘留 unattempted 列
    python3 scripts/backfill_fulltext_unattempted.py --verify [--expect-oa N]  # V1-V4 驗收(V3 交易內試 kh4 後回滾)
    python3 scripts/backfill_fulltext_unattempted.py --selftest       # 紅綠自測(免 DB 免 API)
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

BATCH = 20_000
ENTITY_QUEUE = ("book", "report", "compound", "material")   # =fetch_entity_fulltext.ENTITIES(#19 跨檔一致)
LOCAL_PROTOCOLS = ("local_file", "sftp")                    # =fetch_oa PENDING_WHERE 排除清單(件A隔離)

# 四桶 reason(SSOT——Python classify 與 SQL CASE 同源自此 dict,不可能漂移);不含單引號(SQL 內嵌)
REASONS = {
    "local_no_text":        "local_no_text：本機/SFTP 通道無全文檔——件A隔離、不外送 OA resolver",
    "pending_oa_queue":     "pending_oa_queue：DOI 形、屬 fetch_oa_fulltext 佇列——尚未嘗試",
    "pending_entity_queue": "pending_entity_queue：entity 型、屬 fetch_entity_fulltext 佇列——尚未嘗試",
    "no_resolver":          "no_resolver：無對應 resolver——現行工具鏈無法嘗試(誠實,非漏做)",
}

# DOI 形判式=fetch_oa_fulltext.PENDING_WHERE 同族(#19);SQL 與 Python 各表述一次、selftest 對測
_DOI_SQL = ("(i.external_id LIKE '10.%' OR i.external_id ILIKE 'https://doi.org/10.%'"
            " OR i.external_id ILIKE 'http://doi.org/10.%'"
            " OR i.external_id ILIKE 'https://dx.doi.org/10.%'"
            " OR i.external_id ILIKE 'http://dx.doi.org/10.%'"
            " OR i.external_id ILIKE 'doi:10.%')")
_DOI_PREFIXES = ("10.", "doi:10.", "https://doi.org/10.", "http://doi.org/10.",
                 "https://dx.doi.org/10.", "http://dx.doi.org/10.")


def is_doi_form(external_id):
    """external_id 是否 DOI 形(與 _DOI_SQL 同義;ILIKE→lower)。純函式。"""
    v = (external_id or "").strip().lower()
    return v.startswith(_DOI_PREFIXES)


def classify_unattempted(external_id, entity_type, protocol):
    """未嘗試件分桶。**純函式**——優先序:通道隔離>DOI>entity>無 resolver(與 _case_sql 同序)。"""
    if protocol in LOCAL_PROTOCOLS:
        return "local_no_text"
    if is_doi_form(external_id):
        return "pending_oa_queue"
    if entity_type in ENTITY_QUEUE:
        return "pending_entity_queue"
    return "no_resolver"


def _case_sql():
    """分桶之 SQL CASE——與 classify_unattempted 同源(REASONS/清單)同序。純函式。"""
    protos = ", ".join(f"'{p}'" for p in LOCAL_PROTOCOLS)
    ents = ", ".join(f"'{e}'" for e in ENTITY_QUEUE)
    return (f"CASE WHEN ks.protocol IN ({protos}) THEN '{REASONS['local_no_text']}' "
            f"WHEN {_DOI_SQL} THEN '{REASONS['pending_oa_queue']}' "
            f"WHEN i.entity_type IN ({ents}) THEN '{REASONS['pending_entity_queue']}' "
            f"ELSE '{REASONS['no_resolver']}' END")


_POOL_WHERE = """
    NOT EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id = i.item_id)
    AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status f WHERE f.item_id = i.item_id)
"""

_OA_PENDING = """
    SELECT count(*) FROM knowledge_item i
    WHERE (i.external_id LIKE '10.%' OR i.external_id ILIKE 'https://doi.org/10.%'
       OR i.external_id ILIKE 'http://doi.org/10.%' OR i.external_id ILIKE 'https://dx.doi.org/10.%'
       OR i.external_id ILIKE 'http://dx.doi.org/10.%' OR i.external_id ILIKE 'doi:10.%')
      AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
      AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status b
                      WHERE b.item_id = i.item_id AND b.status <> 'unattempted')
      AND NOT EXISTS (SELECT 1 FROM knowledge_source ks WHERE ks.source_key = i.source_key
                      AND ks.protocol IN ('local_file','sftp'))
"""


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {_case_sql()} AS bucket, count(*) FROM knowledge_item i "
                    f"LEFT JOIN knowledge_source ks ON ks.source_key = i.source_key "
                    f"WHERE {_POOL_WHERE} GROUP BY 1 ORDER BY 2 DESC")
        rows = cur.fetchall()
        cur.execute("SELECT count(*) FROM knowledge_fulltext_status WHERE status='unattempted'")
        done = cur.fetchone()[0]
    total = sum(n for _, n in rows)
    print(f"── 待回填分桶(唯讀)── 池={total:,} | 已回填 unattempted={done:,}")
    for reason, n in rows:
        print(f"  {n:>9,}  {reason.split('：')[0]}")
    return 0


def _apply(conn, limit) -> int:
    total = 0
    from augur.core import db
    while True:
        batch = BATCH if limit is None else max(0, min(BATCH, limit - total))
        if batch == 0:
            break
        with db.transaction(conn) as cur:
            cur.execute(f"""
                INSERT INTO knowledge_fulltext_status (item_id, status, reason)
                SELECT i.item_id, 'unattempted', {_case_sql()}
                FROM knowledge_item i
                LEFT JOIN knowledge_source ks ON ks.source_key = i.source_key
                WHERE {_POOL_WHERE}
                ORDER BY i.item_id
                LIMIT {int(batch)}
                ON CONFLICT (item_id) DO NOTHING
            """)
            n = cur.rowcount
        total += n
        print(f"  批 +{n:,}(累計 {total:,})", flush=True)
        if n < batch:
            break
    print(f"✓ 回填完成:{total:,} 列(冪等,重跑=0)")
    return 0


def _sweep(conn) -> int:
    """已有全文者之殘留 unattempted 列=過期旗標,刪之(本表零 trigger,親驗 2026-08-01)。"""
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("""DELETE FROM knowledge_fulltext_status f
                       WHERE f.status = 'unattempted'
                         AND EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id = f.item_id)""")
        n = cur.rowcount
    print(f"✓ sweep:刪過期 unattempted {n:,} 列(已有全文者)")
    return 0


def _verify(conn, expect_oa) -> int:
    ok = True
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) FROM knowledge_item i WHERE {_POOL_WHERE}")
    v1 = cur.fetchone()[0]
    ok &= v1 == 0
    print(f"  {'✓' if v1 == 0 else '✗'} V1 無列缺口歸零(no_text_no_flag={v1:,})")
    cur.execute("SELECT count(*) FROM knowledge_fulltext_status WHERE status='unattempted'")
    v2 = cur.fetchone()[0]
    ok &= v2 > 0
    print(f"  {'✓' if v2 > 0 else '✗'} V2 unattempted 列已落({v2:,})")
    # V3 絆線:抽 5 件 unattempted 走真 kh4 派生,不得判 terminal_blocked(交易內、ROLLBACK 不留痕)
    cur.execute("SELECT item_id FROM knowledge_fulltext_status WHERE status='unattempted' "
                "ORDER BY item_id LIMIT 5")
    ids = [r[0] for r in cur.fetchall()]
    if ids:
        from augur.knowledge import kh4
        wrote = kh4.refresh_items(cur, item_ids=ids)
        if wrote:
            cur.execute("SELECT count(*) FROM knowledge_kh4_state WHERE item_id = ANY(%s) "
                        "AND status_reason = 'terminal_blocked'", (ids,))
            bad = cur.fetchone()[0]
            ok &= bad == 0
            print(f"  {'✓' if bad == 0 else '✗'} V3 kh4 絆線:{len(ids)} 件 unattempted 判 terminal_blocked={bad}(須 0)")
        else:
            print("  ~ V3 SKIP:knowledge_kh4_state 未建,kh4 絆線無從驗(誠實跳過非通過)")
    else:
        ok = False
        print("  ✗ V3 無 unattempted 樣本可驗(先 --apply)")
    cur.execute(_OA_PENDING)
    v4 = cur.fetchone()[0]
    if expect_oa is None:
        print(f"  ~ V4 fetch_oa pending={v4:,}(未給 --expect-oa,僅印不判)")
    else:
        ok &= v4 == expect_oa
        print(f"  {'✓' if v4 == expect_oa else '✗'} V4 fetch_oa pending 不因回填而變({v4:,} vs 基準 {expect_oa:,})")
    conn.rollback()   # V3 之 kh4_state 寫入不落地
    print("驗收:全通過 ✓" if ok else "驗收:有失敗 ✗")
    return 0 if ok else 1


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # ① classify 純函式餵真輸入(佇列樣本取自 live externals 之形)
    chk("DOI 裸形→oa 佇列", classify_unattempted("10.1257/aer.20230011", "article", None) == "pending_oa_queue")
    chk("DOI url 形(大小寫不敏)→oa 佇列",
        classify_unattempted("HTTPS://DOI.ORG/10.1000/x", "article", None) == "pending_oa_queue")
    chk("entity book 非 DOI→entity 佇列",
        classify_unattempted("ia-book-123", "book", None) == "pending_entity_queue")
    chk("無 resolver 誠實桶", classify_unattempted("osf-abc", "article", None) == "no_resolver")
    chk("local_file 通道優先於一切(件A隔離)",
        classify_unattempted("10.5/x", "book", "local_file") == "local_no_text")
    chk("sftp 同隔離", classify_unattempted(None, "book", "sftp") == "local_no_text")
    # ② DOI 判式負樣本(與 _DOI_SQL 同義之邊界)
    chk("localfile:sha1 非 DOI", not is_doi_form("localfile:3f2a"))
    chk("210.x 非 DOI(前綴非 10.)", not is_doi_form("210.5/x"))
    chk("doi:10. 前綴是 DOI", is_doi_form("doi:10.5/x"))
    # ③ SQL CASE 與 classify 同源同序(驗生成物之行為序,非驗檔案文字)
    case = _case_sql()
    chk("CASE 四桶 reason 各恰一次", all(case.count(r) == 1 for r in REASONS.values()))
    chk("CASE 優先序=通道>DOI>entity>else",
        case.index(REASONS["local_no_text"]) < case.index(REASONS["pending_oa_queue"])
        < case.index(REASONS["pending_entity_queue"]) < case.index(REASONS["no_resolver"]))
    # ④ reason 前綴機器可解析(「<bucket>：…」)
    chk("reason 前綴=桶名+全形冒號", all(v.startswith(k + "：") for k, v in REASONS.items()))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="回填 fulltext 'unattempted' 旗標(D1;冪等分批)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="--apply 上限(首輪最小 #25)")
    ap.add_argument("--sweep-stale", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--expect-oa", type=int, default=None, help="--verify V4 之回填前基準值")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.apply or a.sweep_stale or a.verify):
        print(__doc__.split("執行指令矩陣")[1].split("-----\n")[-1])
        a.check = True   # 安全預設=唯讀分桶(#29a)
    from augur.core import db
    with db.connect() as conn:
        if a.apply:
            return _apply(conn, a.limit)
        if a.sweep_stale:
            return _sweep(conn)
        if a.verify:
            return _verify(conn, a.expect_oa)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
