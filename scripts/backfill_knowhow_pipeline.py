#!/usr/bin/env python
"""十領域 know-how 全鏈背景補齊 — registry→acquire→staging→promote→公版全文 work_text(本地零 LLM)。

🎯 這支在做什麼(白話):串既有引擎跑完整知識管線——
   A) DBpedia 九域驗證查詢 acquire thinker → B) OpenAlex/Crossref/arXiv/OSTI 十域論文 metadata
   → C) promote(冪等去重、lineage)→ D) fetch_all_thinker_works 遍歷全 thinker 抓 Gutenberg
   公版著作全文直入 work_text(copyright=false 程式判定、逐字無摘要)。
守 #1(全真實 API、公版判定=Gutenberg collection 事實)· #17/#25(sleep 限速)· #6 冪等可續 ·
   #28(本地零 usage)· CLAUDE #29。版權著作自然停在書目/metadata(合法終點)。

執行指令矩陣:
  python scripts/backfill_knowhow_pipeline.py            # 全鏈(背景建議:nohup 或 harness 背景)
  python scripts/backfill_knowhow_pipeline.py --skip-fulltext   # 只跑 A-C(不掃 Gutenberg)
"""
import sys
import time
import subprocess

import _bootstrap  # noqa: F401
from augur.core import db

PY = sys.executable


def load_registry():
    """域/查詢詞/DBpedia 來源一律讀 DB(knowledge_query + knowledge_source),零 hardcode(#29b)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT source_key FROM knowledge_source "
                    "WHERE adapter='dbpedia_sparql' AND source_key LIKE 'dbpedia_%%' "
                    "AND source_key <> 'dbpedia_philosophers' AND enabled ORDER BY 1")
        dbp = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT domain, query FROM knowledge_query WHERE enabled ORDER BY domain, query_id")
        queries = {}
        for dom, q in cur.fetchall():
            queries.setdefault(dom, []).append(q)
    return dbp, queries


def run(*a):
    print('▶', ' '.join(a), flush=True)
    subprocess.run([PY, 'scripts/' + a[0], *a[1:]], check=False)


def main():
    t0 = time.time()
    dbp_sources, queries = load_registry()
    print(f'registry 載入:DBpedia 域來源 {len(dbp_sources)}、查詢詞 {sum(len(v) for v in queries.values())} 個 / {len(queries)} 域', flush=True)
    # A) DBpedia 域 thinker(來源=registry、零 hardcode)
    for src_key in dbp_sources:
        run('acquire_knowledge.py', '--source', src_key, '--limit', '200')
        time.sleep(3)
    run('promote_knowledge.py', '--entity-type', 'thinker')
    print(f'--- A) DBpedia thinker 完成 {time.time()-t0:.0f}s ---', flush=True)

    # B) 各域論文 metadata(查詢詞=knowledge_query 表、零 hardcode)
    for dom, qs in queries.items():
        for q in qs:
            for src in ('openalex_works', 'crossref_works'):
                run('acquire_knowledge.py', '--source', src, '--query', q, '--limit', '25', '--domain', dom)
                time.sleep(2)
    for dom in ('energy_materials', 'solar_materials'):        # 材料域補 arXiv+OSTI(前 2 詞)
        for q in queries.get(dom, [])[:2]:
            for src in ('arxiv_search', 'osti_energy'):
                run('acquire_knowledge.py', '--source', src, '--query', q, '--limit', '25', '--domain', dom)
                time.sleep(2)
    run('promote_knowledge.py', '--entity-type', 'work')   # match 到 thinker 者入 work,其餘留審
    print(f'--- B) 論文 metadata 完成 {time.time()-t0:.0f}s ---', flush=True)

    # D) 公版全文:遍歷全 thinker 之 Gutenberg 著作(冪等 seen-skip、copyright=false 才收)
    if '--skip-fulltext' not in sys.argv:
        run('fetch_all_thinker_works.py')
    # 終態統計
    with db.connect() as conn, db.transaction(conn) as cur:
        for label, q in [('thinker', 'SELECT count(*) FROM philosophy_thinker'),
                         ('work', 'SELECT count(*) FROM philosophy_work'),
                         ('work_text 段', 'SELECT count(*) FROM philosophy_work_text'),
                         ('有全文 work', "SELECT count(DISTINCT work_id) FROM philosophy_work_text"),
                         ('staging promoted', "SELECT count(*) FROM knowledge_staging WHERE status='promoted'"),
                         ('staging pending', "SELECT count(*) FROM knowledge_staging WHERE status='pending'")]:
            cur.execute(q)
            print(f'  {label}: {cur.fetchone()[0]:,}', flush=True)
    print(f'=== 全鏈完成 {(time.time()-t0)/60:.1f} 分 ===', flush=True)


if __name__ == '__main__':
    main()
