#!/usr/bin/env python
"""投資借閱書(在版權、全文法律不可入庫)→ 核心精神軌候選 surfacing(供人撰 philosophy_principle)。

🎯 這支在做什麼(白話):列出「投資/管理類、被 fail-closed 擋為 skip_license 之借閱書」——這些是
   **在版權現代書**(IA 受控數位借閱等),全文法律不可入庫(Hachette v. IA 判 CDL 侵權;憲章全文准入三軌
   +負面清單影子圖書館永不納)。但其**核心精神**得經合法路入庫:**人**(合法讀過該書者)於 philosophy_principle
   撰「可證偽因子假說 + 真實文獻 citation(書名/篇章/頁碼)」→ principle_factor_map → #14 經濟驗證裁決。

   **本工具只 surface 候選之 metadata(書名/作者/來源 id)、零內容**——不讀在版權書、不 AI 摘要生成 principle
   (那才是 #1 假兆 + 侵權;憲章 v1.18.0「嚴禁 AI 整理/摘要版權著作內容入庫」)。principle 撰寫是決策層/人工,
   非本工具產物;本工具＝把借閱書從 skip_license 死路「導向」核心精神軌的入口清單(hugo 2026-07-14 directive)。

守 #1(不讀/不摘要在版權內容、僅 metadata)· 憲章 v1.18.0(核心精神合法載體=因子假說+citation、非摘要)·
   全文准入三軌 + 負面清單· #28(本地零 usage)· #29(a/d 個別可執行+指令矩陣+graceful)。

執行指令矩陣:
  python scripts/report_principle_candidates.py                       # 全投資/管理域借閱書候選(唯讀)
  python scripts/report_principle_candidates.py --domain investment_mgmt finance_mgmt
  python scripts/report_principle_candidates.py --limit 50            # 限筆數
  python scripts/report_principle_candidates.py --csv > cands.csv     # 匯出(書名/作者/id 供撰 principle 引 citation)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

INVEST_DOMAINS = ("investment_mgmt", "finance_mgmt", "accounting_mgmt",
                  "business_mgmt", "mgmt_philosophy")   # 投資/管理智慧域(可 --domain 覆寫)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--domain", nargs="*", default=None, help="限定 domain(預設投資/管理 5 域)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--csv", action="store_true", help="CSV 匯出(domain,title,authors,external_id,url)")
    ap.add_argument("--all", action="store_true",
                    help="不濾雜訊(預設濾 IA 誤標之 podcast/DTIC/OSF 註冊/hash-media,只留真編目書)")
    args, _ = ap.parse_known_args()
    doms = args.domain or list(INVEST_DOMAINS)
    # 雜訊濾網(#15:entity_type='book' 被 IA 汙染——podcast/廣播/技術報告/註冊誤標為 book):
    #   排 osf-註冊、DTIC 技術報告、IA hash-id(28+ 純小寫英數=自動生成之媒體);留 openlibrary /works/ 真編目書+可讀 IA 書名。
    noise = ("" if args.all else
             " AND ki.external_id NOT LIKE 'osf-%%' AND ki.external_id NOT LIKE 'DTIC_%%' "
             " AND ki.external_id !~ '^[a-z0-9]{28,}$' ")   # %% 轉義(psycopg 參數化;LIKE 之 % 須雙寫)
    with db.connect() as conn, db.transaction(conn) as cur:
        # 現況:借閱書已標 skip_license 者(harvest fail-closed 判定)——核心精神軌候選
        cur.execute("""
            SELECT ki.domain, ki.title, COALESCE(ki.authors,''), COALESCE(ki.external_id,''), COALESCE(ki.url,'')
            FROM knowledge_item ki JOIN knowledge_fulltext_status fs ON fs.item_id = ki.item_id
            WHERE ki.entity_type='book' AND fs.status='skip_license' AND ki.domain = ANY(%s)""" + noise + """
            ORDER BY ki.domain, ki.title
            """ + (f" LIMIT {int(args.limit)}" if args.limit else ""), (doms,))
        rows = cur.fetchall()
        # 尚待 harvest 判定者(未試/公版待抓)——清單未完整之誠實揭露(#15)
        cur.execute("""SELECT count(*) FROM knowledge_item ki
                       LEFT JOIN knowledge_fulltext_status fs ON fs.item_id=ki.item_id
                       WHERE ki.entity_type='book' AND ki.domain=ANY(%s) AND fs.item_id IS NULL""", (doms,))
        pending = cur.fetchone()[0]
    if args.csv:
        print("domain,title,authors,external_id,url")
        for d, t, a, e, u in rows:
            print(",".join('"' + str(x).replace('"', "'") + '"' for x in (d, t, a, e, u)))
        return 0
    if not rows and pending == 0:
        print(__doc__.split("執行指令矩陣:")[1])
        print("  (投資/管理域無 skip_license 借閱書;harvest 或未跑或全公版)")
        return 0
    print(f"投資/管理借閱書 → 核心精神軌候選(skip_license、在版權、全文不可入庫;供人撰 principle 引 citation):")
    cur_dom = None
    for d, t, a, e, u in rows:
        if d != cur_dom:
            print(f"\n【{d}】")
            cur_dom = d
        print(f"  · {t[:65]}" + (f"（{a[:30]}）" if a else "") + (f"  [{e}]" if e else ""))
    print(f"\n共 {len(rows)} 本借閱書候選。"
          + (f"⚠ 另 {pending:,} 本尚待 harvest 判定 license(P3 book 跑完再跑本工具得完整清單)。" if pending else ""))
    print("下一步(決策層/人工,AI 不代):合法讀過之書 → build_philosophy_framework.py 撰 philosophy_principle"
          "(school+statement+hypothesis+書名/頁碼 citation)→ principle_factor_map → #14 經濟驗證。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
