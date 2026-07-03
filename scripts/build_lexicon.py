#!/usr/bin/env python
"""辭書層 builder — 六源公版辭書/註疏全文(philosophy_work_text)→ knowledge_lexicon(L3 定義層,計畫 T2)。

🎯 這支在做什麼(白話):把已入庫的公版辭書/註疏**逐字全文**,用確定性規則 parser
   (`augur.knowledge.lexicon_parsers`,零 ML 零 AI 生成)切成詞條,寫入 `knowledge_lexicon`:
   term=textnorm 正規化形(與 concordance 可 JOIN)、term_display=原貌、定義逐字、locator 可回原書。
   六源:說文解字/康熙字典/Webster 1913/Roget 1911/王弼注/十三經注疏。
   前置=該辭書 work 全文已入庫;缺全文時**印落地指引**(既有 fetch 工具鏈;英文源以 gutendex
   一次 search call 實測 ebook id,#25 不寫死記憶值)。解析失敗計數誠實印出(寧缺)。
守 #1(逐字自公版來源、禁 AI 生成定義)· #6(ON CONFLICT DO NOTHING 冪等重跑)·
   #15(解析/寫入計數實證、樣本印出供逐字對回原文)· #25(僅指引路徑一次 search 探測)· CLAUDE #29。

執行指令矩陣:
  python scripts/build_lexicon.py                                   # 無參數:列六源+各源全文/lexicon 現況統計
  python scripts/build_lexicon.py --source shuowen                  # 說文解字 → knowledge_lexicon
  python scripts/build_lexicon.py --source webster1913 --limit 50   # 只入前 50 條(#25 微測)
  python scripts/build_lexicon.py --source wangbi --dry-run         # 只解析印統計樣本、不寫 DB
  # --source 六選一:shuowen | kangxi | webster1913 | roget1911 | wangbi | shisanjing
"""
import json
import urllib.parse
import urllib.request
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import lexicon_parsers

UA = {"User-Agent": "augur-knowledge/1.0 (research; contact via repo)"}

# 六源定義:patterns=philosophy_work 標題對映(title/title_zh ILIKE)、mode=解析粒度
#   per_segment=逐 work_text 段解析、locator 前綴該段 chapter(維基文庫每段=一卷/一篇)
#   whole=全 work 串接後解析(Gutenberg 依 8000 字硬切段,詞條會跨段界)
SOURCES = {
    "shuowen": dict(
        label="說文解字(許慎,公版字書)", language="zh", mode="per_segment",
        parser="parse_shuowen", patterns=["%說文解字%", "%shuowen%"],
        fetch_hint=("維基文庫(zh.wikisource.org/wiki/說文解字)——用既有工具鏈:\n"
                    "     ① 建 thinker(許慎)+work(說文解字)(acquire→promote 或手動 INSERT)\n"
                    "     ② 仿 scripts/fetch_chinese_classics.py(MediaWiki API 子頁全文)抓入 work_text")),
    "kangxi": dict(
        label="康熙字典(公版字書)", language="zh", mode="per_segment",
        parser="parse_kangxi", patterns=["%康熙字典%", "%kangxi%"],
        fetch_hint=("維基文庫(zh.wikisource.org/wiki/康熙字典)——同說文路徑;\n"
                    "     ⚠ 計畫 T2:維基文庫康熙完整性須執行時實測(部分部首頁可能缺)")),
    "webster1913": dict(
        label="Webster's Unabridged Dictionary 1913(公版英文辭典)", language="en", mode="whole",
        parser="parse_webster1913", patterns=["%webster%dictionary%", "%webster%unabridged%"],
        gutendex_search="Webster Unabridged Dictionary"),
    "roget1911": dict(
        label="Roget's Thesaurus 1911(公版英文類語辭典)", language="en", mode="whole",
        parser="parse_roget1911", patterns=["%roget%thesaurus%", "%thesaurus%roget%"],
        gutendex_search="Roget Thesaurus"),
    "wangbi": dict(
        label="老子道德真經注(王弼,公版註疏)", language="zh", mode="per_segment",
        parser="parse_wangbi", patterns=["%王弼%", "%道德真經注%", "%道德真經註%", "%老子道德經注%"],
        fetch_hint=("維基文庫(zh.wikisource.org/wiki/道德真經註 或 老子道德經注)——同說文路徑;\n"
                    "     thinker=王弼(226-249)")),
    "shisanjing": dict(
        label="十三經注疏(公版註疏,13 部)", language="zh", mode="per_segment",
        parser="parse_shisanjing",
        patterns=["%十三經注疏%", "%注疏%", "%註疏%", "%周易正義%", "%尚書正義%",
                  "%毛詩正義%", "%禮記正義%", "%春秋左傳正義%"],
        fetch_hint=("維基文庫(如 zh.wikisource.org/wiki/論語注疏、周易正義…逐部)——同說文路徑;\n"
                    "     13 部各自為一 work(論語注疏/孝經注疏/爾雅注疏/孟子注疏/周禮注疏/儀禮注疏…)")),
}


def _find_works(cur, cfg):
    """依標題 pattern 找已有全文之 work(排除 review_flag 待稽核者,對齊計畫 T-1)。"""
    conds = " OR ".join(["w.title ILIKE %s OR w.title_zh ILIKE %s"] * len(cfg["patterns"]))
    params = [p for pat in cfg["patterns"] for p in (pat, pat)]
    cur.execute(
        f"""SELECT w.work_id, COALESCE(w.title_zh, w.title) AS name
            FROM philosophy_work w
            WHERE ({conds}) AND COALESCE(w.review_flag, false) = false
              AND EXISTS (SELECT 1 FROM philosophy_work_text t WHERE t.work_id = w.work_id)
            ORDER BY w.work_id""", params)
    return cur.fetchall()


def _lexicon_exists(cur):
    cur.execute("SELECT to_regclass('knowledge_lexicon')")
    return cur.fetchone()[0] is not None


def _gutendex_probe(search):
    """gutendex 一次 search call 實測 ebook id(#25:僅缺全文指引時呼叫、不寫死記憶值)。"""
    url = "https://gutendex.com/books?search=" + urllib.parse.quote(search)
    try:
        d = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30).read().decode())
        return [(b["id"], b["title"], "; ".join(a["name"] for a in b.get("authors", [])),
                 b.get("copyright")) for b in d.get("results", [])[:3]], url
    except Exception as e:                                   # 網路失敗:誠實印 URL 供手動查
        return e, url


def _print_fetch_guidance(skey, cfg):
    print(f"⚠ 前置未滿足:{cfg['label']} 尚無全文入庫(philosophy_work + work_text)。落地指引:")
    if "gutendex_search" in cfg:
        hits, url = _gutendex_probe(cfg["gutendex_search"])
        if isinstance(hits, Exception):
            print(f"  ① gutendex 探測失敗({hits});手動查:{url}")
        elif not hits:
            print(f"  ① gutendex 實測 0 命中;換關鍵詞手動查:{url}")
        else:
            print("  ① gutendex 實測 ebook id(一次 search call,#25):")
            for gid, title, authors, copyrighted in hits:
                print(f"       id={gid:<6} {title[:60]}({authors})copyright={copyrighted}")
        print("  ② 建 work:python scripts/acquire_knowledge.py --source gutendex_search "
              f"--query \"{cfg['gutendex_search']}\"")
        print("       → python scripts/promote_knowledge.py --entity-type work")
        print("  ③ 抓全文:confirmed.json=[{\"work_id\":W,\"language\":\"en\","
              "\"actual_txt_url\":\"https://www.gutenberg.org/ebooks/<id>.txt.utf-8\"}]")
        print("       → python scripts/fetch_confirmed_fulltext.py confirmed.json")
    else:
        print("  " + cfg["fetch_hint"])
    print(f"  完成後重跑:python scripts/build_lexicon.py --source {skey}")


def _parse_work(cur, work_id, cfg):
    """讀一部 work 全文→parser;回 (rows, failed)。rows=(term_display, definition, locator, lex_type)。"""
    parser = getattr(lexicon_parsers, cfg["parser"])
    cur.execute("SELECT chapter, content FROM philosophy_work_text "
                "WHERE work_id=%s ORDER BY seq NULLS LAST, text_id", (work_id,))
    segs = cur.fetchall()
    if cfg["mode"] == "whole":
        entries, failed = parser("\n".join(c for _, c in segs))
        return list(entries), failed
    rows, failed = [], 0
    for chapter, content in segs:        # 維基文庫段=卷/篇:chapter 前綴 locator(可回原書)
        entries, f = parser(content)
        failed += f
        for e in entries:
            loc = "·".join(x for x in (chapter, e.locator) if x) or None
            rows.append(lexicon_parsers.LexEntry(e.term_display, e.definition, loc, e.lex_type))
    return rows, failed


def build_source(cur, skey, cfg, limit=None, dry=False):
    works = _find_works(cur, cfg)
    if not works:
        _print_fetch_guidance(skey, cfg)
        return
    if not dry:
        try:                             # textnorm=並行分派之 SSOT(計畫 §二6);未落地則誠實停
            from augur.knowledge import textnorm
        except ImportError:
            print("⚠ augur.knowledge.textnorm 未落地(計畫 §二6 term 正規化 SSOT,另一分派)。")
            print("  可先 --dry-run 驗 parser;textnorm 落地後重跑本指令。")
            return

        def norm(term_display):
            return textnorm.norm_headword(term_display, cfg["language"])

    from psycopg2.extras import execute_values
    print(f"── {skey}{cfg['label']}):對映 work {len(works)} 部 ──")
    total = dict(parsed=0, failed=0, norm_skip=0, inserted=0)
    for work_id, name in works:
        rows, failed = _parse_work(cur, work_id, cfg)
        if limit is not None:
            rows = rows[: max(0, limit - total["parsed"])]
        total["parsed"] += len(rows)
        total["failed"] += failed
        for e in rows[:3]:               # 抽樣印出供人工逐字對回原文(#15;計畫 T2 驗證)
            print(f"   例|{e.term_display}|[{e.locator}] {e.definition[:60]}")
        if dry:
            print(f"   {name}(work {work_id}):解析 {len(rows)} 條、失敗 {failed}(dry-run 未寫)")
            continue
        values, seen = [], {}
        for e in rows:
            term = norm(e.term_display)
            if not term:
                total["norm_skip"] += 1
                continue
            n = seen[(term, e.locator)] = seen.get((term, e.locator), 0) + 1
            # 同 (term, locator) 重複=跨段 idx 重置之真條目(非同列):確定性序號消歧,不丟資料
            loc = e.locator if n == 1 else f"{e.locator or ''}〔{n}〕"
            values.append((term, e.term_display, cfg["language"], e.definition,
                           work_id, loc, e.lex_type))
        inserted = execute_values(
            cur,
            "INSERT INTO knowledge_lexicon "
            "(term, term_display, language, definition, source_work_id, source_locator, lex_type) "
            "VALUES %s ON CONFLICT DO NOTHING RETURNING lex_id",
            values, fetch=True, page_size=500)
        total["inserted"] += len(inserted)
        print(f"   {name}(work {work_id}):解析 {len(rows)} 條、失敗 {failed}、"
              f"入庫 +{len(inserted)}(重複跳過 {len(values) - len(inserted)})")
    print(f"合計:解析 {total['parsed']} 條、解析失敗 {total['failed']}(寧缺誠實)、"
          f"正規化空跳過 {total['norm_skip']}、入庫 +{total['inserted']}"
          + ("(dry-run 未寫)" if dry else ""))


def show_status(cur):
    print(__doc__.split("執行指令矩陣:")[1])
    lex_ok = _lexicon_exists(cur)
    print("六源現況(前置=該辭書 work 全文已入庫):")
    for skey, cfg in SOURCES.items():
        works = _find_works(cur, cfg)
        if works and lex_ok:
            cur.execute("SELECT count(*) FROM knowledge_lexicon WHERE source_work_id = ANY(%s)",
                        ([w for w, _ in works],))
            lex = f"lexicon {cur.fetchone()[0]} 條"
        else:
            lex = "lexicon 0 條" if lex_ok else "lexicon(表未建)"
        print(f"  {skey:12} {cfg['label']:38} 全文 work {len(works)} 部|{lex}")
    if not lex_ok:
        print("⚠ knowledge_lexicon 未建 — 先跑 python scripts/migrate_text_understanding_ddl.py(T0)")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--source")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.source:
            show_status(cur)
            return
        if args.source not in SOURCES:
            raise SystemExit(f"未知 --source: {args.source}(六選一:{'|'.join(SOURCES)})")
        if not args.dry and not _lexicon_exists(cur):
            raise SystemExit("knowledge_lexicon 未建 — 先跑 python scripts/migrate_text_understanding_ddl.py(T0)")
        build_source(cur, args.source, SOURCES[args.source], limit=args.limit, dry=args.dry)


if __name__ == "__main__":
    main()
