#!/usr/bin/env python
"""自我求知驅動器 v2 — 從已收文獻標題抽技術片語缺口→生成收割 query(hugo 2026-07-25「需要的知識就去抓」)。
🎯 這支在做什麼(白話):讓收割從固定清單升級為**缺口驅動**。v2 訊號源=**已收文獻標題之反覆技術片語**
   (如 'realized volatility'、'model collapse'),取「在 ≥3 篇標題出現、且尚無同名 query」者→寫回
   knowledge_query(同域、origin='self_seek_v2')→下輪收割自動深掘該主題。冪等 dedup;既核域內、零新域。
   **v1 缺陷與退場(2026-07-25 自揭)**:v1 讀 knowledge_term_stats(Porter **詞幹**表),產出 'europ'
   /'labour'/'honour' 等**詞幹碎片與泛用詞**,當搜尋詞會抓回垃圾並空耗額度(違 #24 精神);且掛
   domain='general'(未註冊)→26 條全為死列。v1 那批已 disable 留痕(P4.E3 只失效不刪)。
守 #29b(query 住 DB)· 憲章 v1.19.0(新域人拍板——v2 只寫既核域,不觸此閘)· #24(不產垃圾查詢)· #28 · #29a/d。
執行指令矩陣:
  python scripts/evolve_self_seek.py                # 無參數:現況(自我求知 query 統計+近期樣本,唯讀)
  python scripts/evolve_self_seek.py --seek         # 掃缺口→寫 query(冪等;預設兩既核域)
  python scripts/evolve_self_seek.py --seek --domain quant_finance --top 15
  python scripts/evolve_self_seek.py --retire-v1    # 將 v1 死列 query 停用留痕(一次性)
  python scripts/evolve_self_seek.py --selftest     # 零 DB 紅綠
"""
import argparse
import re
import sys
from collections import Counter

import _bootstrap  # noqa: F401
from augur.core import db

DOMAINS = ("quant_finance", "software_engineering")
MIN_TITLES = 3        # 片語須在 ≥N 篇標題出現(反覆=真概念、非一次性)
STOP_EN = {
    "the", "and", "for", "with", "from", "that", "this", "using", "based", "via", "into", "over",
    "under", "between", "among", "toward", "towards", "their", "these", "those", "such", "which",
    "when", "where", "what", "how", "why", "new", "novel", "study", "studies", "case", "paper",
    "approach", "approaches", "method", "methods", "model", "models", "analysis", "results",
    "evidence", "effects", "effect", "impact", "role", "use", "used", "can", "does", "are", "was",
    "its", "his", "her", "our", "you", "your", "not", "but", "all", "one", "two", "three", "some",
    "more", "most", "less", "than", "also", "may", "might", "shall", "should", "would", "could",
}


URL_RE = re.compile(
    r"https?://\S+|www\.\S+|\b[\w.-]+\.(?:com|org|net|io|edu|gov|ai|co|dev|me)\b"
    r"|\b10\.\d{4,}/\S+|\bdoi:\S+|\barxiv:\S+|\S+/\S+/\S+", re.I)   # URL/網域/DOI/arXiv id/多段路徑
BAD_TOKENS = {"http", "https", "www", "com", "org", "net", "html", "pdf", "doi", "arxiv", "github", "gitlab"}


def _strip_urls(text):
    """剝除 URL/網域/DOI/路徑(2026-07-26 修:v2 首跑抓到 'github com-public-apis-public-apis' 雜訊)。"""
    return URL_RE.sub(" ", text or "")


def _clean_phrase(ph):
    """片語級守衛:含網路 token、含連字號長串(路徑殘骸)、或全數字者剔除。"""
    toks = ph.split()
    if any(t in BAD_TOKENS for t in toks):
        return False
    if any(t.count("-") >= 2 for t in toks):        # com-public-apis-public-apis 型殘骸
        return False
    return not any(t.isdigit() for t in toks)


OVERLAP_MAX = 0.5     # token Jaccard 門檻(達此即視為同概念不同切窗)


def _too_similar(ph, chosen):
    """重疊切窗去重(2026-07-26 修:v2 產出 'prompt engineering large'/'engineering large language' 等
    同概念片段)。判準:①子串包含 ②token 集被涵蓋 ③Jaccard ≥ OVERLAP_MAX(3-token 滑窗共享 2 token 恰=0.5,故含等號;
    2-token 共享 1 token=0.33 不誤殺)。"""
    a = set(ph.split())
    for o in chosen:
        b = set(o.split())
        if ph == o or ph in o or o in ph:
            return True
        if a <= b or b <= a:
            return True
        if a & b and len(a & b) / len(a | b) >= OVERLAP_MAX:
            return True
    return False


def _title_phrase_gaps(cur, domain, top):
    """文獻標題 → 反覆技術片語(2-3 詞)缺口。回 [(phrase, n_titles)]。"""
    cur.execute("""SELECT title FROM knowledge_item
        WHERE domain=%s AND title IS NOT NULL AND length(title) > 20 LIMIT 3000""", (domain,))
    cnt = Counter()
    for (title,) in cur.fetchall():
        title = _strip_urls(title)
        words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]{2,}", title)]
        words = [w for w in words if w not in STOP_EN and len(w) >= 3]
        for n in (2, 3):
            for i in range(len(words) - n + 1):
                cnt[" ".join(words[i:i + n])] += 1
    cur.execute("SELECT lower(query) FROM knowledge_query")
    seen = {r[0] for r in cur.fetchall()}
    cands = [(ph, c) for ph, c in cnt.most_common(top * 40)
             if c >= MIN_TITLES and ph not in seen and _clean_phrase(ph)]
    cands.sort(key=lambda x: (-x[1], -len(x[0].split())))     # 頻次優先、同頻取較長(資訊量高)
    out = []
    for ph, c in cands:
        if not _too_similar(ph, [o for o, _ in out]):
            out.append((ph, c))
        if len(out) >= top:
            break
    return out


def seek(domains, top):
    total = 0
    with db.connect() as conn:
        cur = conn.cursor()
        for dom in domains:
            gaps = _title_phrase_gaps(cur, dom, top)
            if not gaps:
                print(f"  {dom}: 無新缺口(語料不足或已全數成 query)")
                continue
            for ph, c in gaps:
                cur.execute("""INSERT INTO knowledge_query (query_id, domain, query, enabled, note, origin)
                    SELECT (SELECT max(query_id) FROM knowledge_query) + 1, %s, %s, true, %s, 'self_seek_v2'
                    WHERE NOT EXISTS (SELECT 1 FROM knowledge_query k WHERE lower(k.query)=lower(%s))""",
                    (dom, ph, f"自我求知 v2:標題片語缺口(見於 {c} 篇 {dom} 文獻)", ph))
                total += cur.rowcount
            print(f"  {dom}: 缺口 {len(gaps)} → 新 query {total};樣本: " + ", ".join(p for p, _ in gaps[:5]))
        conn.commit()
    print(f"✓ 共新增 {total} 條(既核域內、下輪收割自動深掘;晉升類決策不涉)")
    return 0


def retire_v1():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""UPDATE knowledge_query SET enabled=false,
            note = coalesce(note,'') || ' | v1 退場 2026-07-25:詞幹碎片非真缺口、domain=general 未註冊致死列(留痕不刪)'
            WHERE origin='self_seek' AND enabled""")
        print(f"✓ v1 死列已停用留痕:{cur.rowcount} 條")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT origin, count(*), count(*) FILTER (WHERE enabled)
            FROM knowledge_query WHERE origin LIKE 'self_seek%' GROUP BY origin ORDER BY origin""")
        rows = cur.fetchall()
        if not rows:
            print("  (尚無自我求知 query)")
        for o, n, en in rows:
            print(f"  {o}: {n} 條(enabled {en})")
        cur.execute("""SELECT domain, query FROM knowledge_query WHERE origin='self_seek_v2'
            ORDER BY query_id DESC LIMIT 6""")
        for d, q in cur.fetchall():
            print(f"    · [{d}] {q}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import inspect
    src = inspect.getsource(_title_phrase_gaps)
    chk("訊號源改文獻標題(非 Porter 詞幹表)", "knowledge_item" in src and "term_stats" not in src)
    chk("反覆門檻(≥3 篇=真概念)", MIN_TITLES >= 3 and "c >= MIN_TITLES" in src)
    chk("多詞片語(2-3 詞、非單字碎片)", "for n in (2, 3)" in src)
    chk("停用詞濾(the/using/based/model…)", {"the", "using", "based", "model"} <= STOP_EN)
    chk("v1 碎片詞若入停用詞或非片語即不再產出", all(len(w) >= 3 for w in STOP_EN))
    s2 = inspect.getsource(seek)
    chk("寫入既核域、不觸新域閘", "DOMAINS" in globals() and "'general'" not in s2)
    chk("query 冪等 dedup(lower 比對)", "lower(k.query)=lower(%s)" in s2)
    chk("v1 退場=停用留痕非刪除(P4.E3)", "enabled=false" in inspect.getsource(retire_v1))
    chk("URL/DOI/路徑剝除", _strip_urls(
        "see https://github.com/x/y and 10.1234/abc plus doi:10.1/z").split() == ["see", "and", "plus"])
    chk("片語守衛擋實測雜訊 github com-public-apis-public-apis", not _clean_phrase("github com-public-apis-public-apis"))
    chk("片語守衛擋網域/數字 token", not _clean_phrase("www example") and not _clean_phrase("volatility 2008"))
    chk("正常技術片語照過", _clean_phrase("reinforcement learning") and _clean_phrase("retrieval-augmented generation"))
    chk("重疊切窗去重:實測雜訊組互斥", _too_similar("engineering large language", ["prompt engineering large"]))
    chk("重疊去重:token 集涵蓋亦擋", _too_similar("augmented generation", ["retrieval augmented generation"]))
    chk("不同概念不誤殺", not _too_similar("market liquidity", ["transaction cost", "deep learning"]))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="自我求知驅動器 v2(標題片語缺口→收割 query)")
    ap.add_argument("--seek", action="store_true")
    ap.add_argument("--domain", choices=DOMAINS)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--retire-v1", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.retire_v1:
        return retire_v1()
    if a.seek:
        return seek([a.domain] if a.domain else list(DOMAINS), a.top)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
