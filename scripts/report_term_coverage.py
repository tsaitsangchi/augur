#!/usr/bin/env python
"""知識層三層可解率報告(v3.0 W6)— 每個字的「定義/出現處/思想」可解程度量化。

🎯 這支在做什麼(白話):把用戶「逐字逐句了解每個字」之目標,變成**可量測的 coverage**(命門2:
   不宣稱全知、只報漸近覆蓋率)。以 concordance distinct term(語料實際出現之字)為分母,逐層算可解率:
   - **定義層**:該 term 有 knowledge_lexicon 定義(公版辭書/註疏)之比率
   - **出現處層**:該 term 有 concordance 出現處之比率(=分母本身,恆 100%;另報高頻 term 占比)
   - **思想層**:該 term 進 knowledge_edge 圖譜(term↔work/thinker/school)之比率
   純計數、零 LLM。**append-only 落 knowledge_coverage_metric**(存在則入帳、不重寫歷史),供時序追蹤。
守 #15(誠實 coverage 非全知宣稱)· #1(純計數真兆)· #29。

執行指令矩陣:
  python scripts/report_term_coverage.py            # 印三層可解率(唯讀)
  python scripts/report_term_coverage.py --record   # 另 append 入 knowledge_coverage_metric(若表存在)
"""
import argparse

import _bootstrap  # noqa: F401
from augur.core import db


def _pct(cur, sql, params=()):
    cur.execute(sql, params)
    n, d = cur.fetchone()
    return int(n), int(d), (100.0 * n / d if d else 0.0)


def coverage(cur):
    """回 [(metric_key, numerator, denominator, pct, note)]。分母=concordance distinct term(語料出現字)。"""
    rows = []
    for lang in ("zh", "en"):
        # 定義層:出現之 term 有 lexicon 定義之比
        n, d, p = _pct(cur,
            "SELECT count(DISTINCT c.term), (SELECT count(DISTINCT term) FROM knowledge_concordance WHERE language=%s) "
            "FROM knowledge_concordance c WHERE c.language=%s "
            "AND EXISTS (SELECT 1 FROM knowledge_lexicon l WHERE l.language=c.language AND l.term=c.term)",
            (lang, lang))
        rows.append((f"term_defined_rate_{lang}", n, d, p, "出現字有公版定義之比(定義層可解率)"))
        # 思想層:出現之 term 進 edge 圖譜(term_in_work/term_defined_by)之比
        n2, d2, p2 = _pct(cur,
            "SELECT count(DISTINCT c.term), (SELECT count(DISTINCT term) FROM knowledge_concordance WHERE language=%s) "
            "FROM knowledge_concordance c WHERE c.language=%s "
            "AND EXISTS (SELECT 1 FROM knowledge_edge e WHERE e.predicate IN ('term_in_work','term_defined_by') "
            "  AND e.src_id::text = c.term)",   # edge src 為 term 字面(若 term 圖譜已建)
            (lang, lang))
        rows.append((f"term_ingraph_rate_{lang}", n2, d2, p2, "出現字進思想圖譜之比(思想層可解率;edge 未建則 0)"))
    return rows


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--record", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            rows = coverage(cur)
        print("── 知識層三層可解率(命門2:漸近 coverage、非全知宣稱)──")
        print("  分母=concordance distinct term(語料實際出現之字);出現處層=分母本身恆 100%")
        for key, n, d, p, note in rows:
            print(f"  {key:24} {n:>8,}/{d:>8,} = {p:5.2f}%   — {note}")
        if args.record:
            with db.transaction(conn) as cur:
                cur.execute("SELECT to_regclass('knowledge_coverage_metric')")
                if cur.fetchone()[0] is None:
                    print("  (knowledge_coverage_metric 未建、跳過 --record;text 計畫 W8 建表後可入帳)")
                else:
                    for key, n, d, p, note in rows:
                        cur.execute(
                            "INSERT INTO knowledge_coverage_metric (metric_date, metric_key, numerator, denominator, note) "
                            "VALUES (current_date, %s, %s, %s, %s) ON CONFLICT (metric_date, metric_key) DO NOTHING",
                            (key, n, d, note))
                    print(f"  → append {len(rows)} 指標入 knowledge_coverage_metric(current_date、不重寫歷史)")


if __name__ == "__main__":
    main()
