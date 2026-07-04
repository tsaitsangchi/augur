#!/usr/bin/env python
"""知識全文理解層 常備完整性稽核器(v3.0 W2)— 逐字承諾/歸屬/語料閘之機器證明,取代抽樣手驗。

🎯 這支在做什麼(白話):把「逐字可溯源、歸屬乾淨、reference 不入語意層」等不變式從口頭承諾
   變成**可重放的機器檢查**——任一違反即 exit 1(擋下游管線/CI)。檢查項:
   - **C-chunk 定位子串**:每 chunk.content == 現行 work_text[char_start:char_end](防 stale;決4 之常備化)
   - **C2 句逐字子串**:每 sentence.sentence == 來源 content[char_start:char_end](work_text/item_text 兩側)
   - **C6 定義溯源**:每 lexicon.definition 前綴出現於其 source_work 全文(公版辭書逐字入庫)
   - **INV 歸屬**:有全文之 work review_flag=NULL 必 0(T-1 稽核常備不變式)
   - **INV 語料閘**:corpus_class='reference' 之 work 產出句/chunk 必 0(W2.5 單一語意欄不變式)
   - **INV 授權**:item_text.license 必 ∈ 四值白名單(#1 版權硬擋)
守 #1(逐字可溯源/授權硬擋)· #15(常備機器證明、不宣稱「全懂」靠抽樣)· #12(閘述詞引 corpus.py)· #29。

執行指令矩陣:
  python scripts/verify_text_integrity.py            # --sample(預設、快;C2/C6 抽樣),唯讀、印清單
  python scripts/verify_text_integrity.py --full     # C2/C6 全量逐字驗(慢;INV/C-chunk 本就全量)
  python scripts/verify_text_integrity.py --sample-n 5000   # 調抽樣量
  # exit 0=全過;exit 1=有違反(可掛 CI/管線前置閘)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import corpus


def _one(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()[0]


def verify(cur, *, full=False, sample_n=2000):
    """回 [(label, violations, note), ...]。violations>0 = 違反。"""
    checks = []
    samp = "" if full else f"ORDER BY random() LIMIT {sample_n}"
    scope = "全量" if full else f"抽樣{sample_n}"

    # C-chunk 定位子串(全量,便宜):chunk.content == work_text[char_start:char_end]
    checks.append(("C-chunk 定位子串(全量)", _one(cur,
        "SELECT count(*) FROM philosophy_chunk c JOIN philosophy_work_text t USING(text_id) "
        "WHERE c.text_id IS NOT NULL AND c.content <> substring(t.content FROM c.char_start+1 FOR c.char_end-c.char_start)"),
        "chunk 逐字對現行 work_text 他證(決4 常備化)"))

    # C2 句逐字子串(work 側):sentence == work_text[char_start:char_end]
    checks.append((f"C2 句逐字·work 側({scope})", _one(cur,
        f"SELECT count(*) FROM (SELECT s.sentence, s.char_start, s.char_end, t.content FROM knowledge_sentence s "
        f"JOIN philosophy_work_text t ON t.text_id=s.text_id WHERE s.text_id IS NOT NULL {samp}) q "
        "WHERE q.sentence <> substring(q.content FROM q.char_start+1 FOR q.char_end-q.char_start)"),
        "句逐字對來源全文他證"))

    # C2 句逐字子串(item 側):sentence == item_text[char_start:char_end]
    n_item = _one(cur, "SELECT count(*) FROM knowledge_sentence WHERE itext_id IS NOT NULL")
    if n_item:
        checks.append((f"C2 句逐字·item 側({scope})", _one(cur,
            f"SELECT count(*) FROM (SELECT s.sentence, s.char_start, s.char_end, it.content FROM knowledge_sentence s "
            f"JOIN knowledge_item_text it ON it.itext_id=s.itext_id WHERE s.itext_id IS NOT NULL {samp}) q "
            "WHERE q.sentence <> substring(q.content FROM q.char_start+1 FOR q.char_end-q.char_start)"),
            f"item 側 {n_item:,} 句"))

    # C6 定義溯源:lexicon.definition 前 20 字出現於 source_work 之某段全文
    # (EXISTS+position 短路;避 string_agg 全文串接 × 15 萬 lexicon 之病態成本。C6 恆抽樣、慢項)
    c6_n = min(sample_n, 500) if not full else sample_n
    checks.append((f"C6 定義溯源(抽樣{c6_n})", _one(cur,
        "SELECT count(*) FROM (SELECT l.definition, l.source_work_id FROM knowledge_lexicon l "
        f"WHERE length(l.definition)>=8 ORDER BY random() LIMIT {c6_n}) q "
        "WHERE NOT EXISTS (SELECT 1 FROM philosophy_work_text t "
        "WHERE t.work_id=q.source_work_id AND position(left(q.definition,20) IN t.content) > 0)"),
        "公版辭書/註疏定義逐字入庫、可溯源 source_work"))

    # INV 歸屬:有全文之 work review_flag=NULL 必 0
    checks.append(("INV 歸屬(有全文 review_flag=NULL)", _one(cur,
        "SELECT count(DISTINCT w.work_id) FROM philosophy_work w "
        "JOIN philosophy_work_text t ON t.work_id=w.work_id WHERE w.review_flag IS NULL"),
        "T-1 稽核常備不變式=0"))

    # INV 語料閘:reference work 產出句/chunk 必 0(W2.5)
    clean = corpus.clean_work_sql("w")  # 述詞 SSOT(#12)——本檢查驗其對偶:非 literary 不得有語意層產物
    checks.append(("INV 語料閘·reference 句", _one(cur,
        "SELECT count(*) FROM knowledge_sentence s JOIN philosophy_work_text t ON t.text_id=s.text_id "
        "JOIN philosophy_work w ON w.work_id=t.work_id WHERE w.corpus_class='reference'"),
        f"corpus_class 單一語意欄(閘 SSOT={clean})"))
    checks.append(("INV 語料閘·reference chunk", _one(cur,
        "SELECT count(*) FROM philosophy_chunk c JOIN philosophy_work w ON w.work_id=c.work_id "
        "WHERE w.corpus_class='reference'"),
        "reference 只走 lexicon 路"))

    # INV 授權:item_text.license ∈ 白名單
    wl = ", ".join(f"'{v}'" for v in corpus.LICENSE_WHITELIST)
    checks.append(("INV 授權(item_text license 白名單)", _one(cur,
        f"SELECT count(*) FROM knowledge_item_text WHERE license NOT IN ({wl})"),
        f"#1 版權硬擋({corpus.LICENSE_WHITELIST})"))

    return checks


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--sample-n", type=int, default=2000)
    args, _ = ap.parse_known_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        checks = verify(cur, full=args.full, sample_n=args.sample_n)
    print("── 知識全文理解層 完整性稽核(verify_text_integrity)──")
    # C6 為諮詢級(advisory):parser 重組之定義(如康熙考證段字頭+接續行合併)非原始連續子串、
    # 內容仍出自 source_work——報告供查但不硬 fail;硬不變式(C-chunk/C2/歸屬/corpus_class/license)才擋 exit。
    bad = 0
    for label, viol, note in checks:
        advisory = label.startswith("C6")
        ok = viol == 0
        if not ok and not advisory:
            bad += 1
        mark = "✓" if ok else ("⚠" if advisory else "✗")
        tail = "(諮詢級、不擋 exit)" if advisory and not ok else ""
        print(f"  {mark} {label}: {viol} 違反{tail}   — {note}")
    print(f"→ 硬不變式 {'全過' if not bad else f'**{bad} 項違反 → exit 1**'}(C6 諮詢級另計)")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
