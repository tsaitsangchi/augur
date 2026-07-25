#!/usr/bin/env python
"""自我求知驅動器 — 偵測知識缺口→自動生成收割 query(hugo 2026-07-25「需要的知識就去抓」)。
🎯 這支在做什麼(白話):讓收割從「固定清單」升級為「缺口驅動」——掃 knowledge_term_stats 找
   「語料高頻出現、但 lexicon 無定義」的術語(=系統天天讀到卻不懂的詞),濾停用詞與泛用頻帶後,
   把真缺口寫成 knowledge_query(origin='self_seek'、既核域內、INSERT 零改碼 #29b)——下一輪收割
   自動去抓。**域邊界=人閘**:缺口若指向未核域,不擅開、印清單待 hugo 拍板(能抓≠該抓)。冪等 dedup。
   迭代誠實註記:v1 缺口訊號=詞頻帶+停用詞濾(粗);後續可上 distinctiveness/弱答題訊號。
守 #29b(query=資料住 DB)· 憲章 v1.19.0(新域人拍板)· #28(全本地)· #29a/d。
執行指令矩陣:
  python scripts/evolve_self_seek.py                # 無參數:現況(self_seek query 統計+缺口預覽,唯讀)
  python scripts/evolve_self_seek.py --seek         # 跑一輪缺口掃描→寫 query(冪等)
  python scripts/evolve_self_seek.py --seek --top 30
  python scripts/evolve_self_seek.py --selftest     # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

# Porter 詞幹後的常見英文停用詞幹(v1 粗濾;缺口=知識詞非功能詞)
STOP = {"place", "which", "these", "reason", "present", "those", "under", "purpos", "about",
        "there", "their", "would", "could", "should", "other", "after", "befor", "where",
        "becaus", "through", "between", "against", "during", "without", "within", "while",
        "shall", "might", "every", "since", "still", "again", "howev", "therefor", "thereof",
        "herein", "hereof", "first", "second", "third", "gener", "differ", "includ", "follow",
        "provid", "requir", "consid", "possibl", "certain", "particular", "respect", "accord"}
DF_CEIL_RATIO = 0.5   # df 超過語料最大 df 之 50%=泛用詞頻帶、非知識缺口


def _gaps(cur, top, language):
    cur.execute("SELECT max(w) FROM (SELECT sum(df_works) w FROM knowledge_term_stats WHERE language=%s GROUP BY term) x",
                (language,))
    ceil = (cur.fetchone()[0] or 0) * DF_CEIL_RATIO
    cur.execute("""SELECT t.term, sum(t.df_works) AS w FROM knowledge_term_stats t
        WHERE t.language=%s AND length(t.term) >= 5
          AND NOT EXISTS (SELECT 1 FROM knowledge_lexicon l WHERE l.term = t.term)
        GROUP BY t.term HAVING sum(t.df_works) <= %s
        ORDER BY sum(t.df_works) DESC LIMIT %s""", (language, ceil, top * 3))
    return [(t, int(w)) for t, w in cur.fetchall() if t not in STOP][:top]


def seek(top):
    with db.connect() as conn:
        cur = conn.cursor()
        gaps = _gaps(cur, top, "en") + _gaps(cur, max(5, top // 3), "zh")
        if not gaps:
            print("缺口掃描:無(高頻未解術語為空)"); return 0
        new = 0
        for term, w in gaps:
            cur.execute("""INSERT INTO knowledge_query (query_id, domain, query, enabled, note, origin)
                SELECT (SELECT max(query_id) FROM knowledge_query) + 1, 'general', %s, true,
                       %s, 'self_seek'
                WHERE NOT EXISTS (SELECT 1 FROM knowledge_query k WHERE k.query=%s)""",
                (term, f"自我求知缺口:語料 df={w}、lexicon 無定義(v1 詞頻帶訊號)", term))
            new += cur.rowcount
        conn.commit()
        print(f"缺口 {len(gaps)} 個 → 新 query {new} 條(origin=self_seek、既核 general 域;下輪收割自動抓)")
        print("  樣本:", ", ".join(t for t, _ in gaps[:8]))
        print("  域邊界誠實註記:v1 全數入 general 域(arxiv/crossref/core adapter);專域歸類與未核域人閘=v2")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(*) FILTER (WHERE enabled) FROM knowledge_query WHERE origin='self_seek'")
        n, en = cur.fetchone()
        print(f"  self_seek query: {n} 條(enabled {en})")
        cur.execute("SELECT query FROM knowledge_query WHERE origin='self_seek' ORDER BY query_id DESC LIMIT 5")
        for (q,) in cur.fetchall():
            print(f"    · {q}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("停用詞濾網涵蓋實測雜訊(place/which/these/purpos)", all(w in STOP for w in ("place", "which", "these", "purpos")))
    chk("df 泛用頻帶天花板存在(0<ratio<1)", 0 < DF_CEIL_RATIO < 1)
    import inspect
    s = inspect.getsource(seek)
    chk("query 寫入冪等(NOT EXISTS dedup)", "NOT EXISTS" in s)
    chk("origin 標記 self_seek(provenance)", "'self_seek'" in s)
    chk("v1 只入既核 general 域(未核域不擅開)", "'general'" in s and "人閘" in s)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="自我求知驅動器(缺口→收割 query)")
    ap.add_argument("--seek", action="store_true")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.seek:
        return seek(a.top)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
