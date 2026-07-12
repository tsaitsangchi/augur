#!/usr/bin/env python
"""R6:財經 CJK 檢索品質量測(K 計畫拍板點 R6 之證據;e5-small 命中率/分數帶重疊)。

🎯 這支在做什麼(白話):12 題財經金題+4 題離題負控,各走 retrieve_items 同一檢索路徑,量:
   ①域精度(top-k 命中落在投資三域的比例)②分數帶(財經題 vs 離題題的 cosine 分佈重疊——
   codebase 已實證 e5-small 0.80-0.88 窄帶與相關性幾乎無關,本支把它量成數字);
   結論=R6 裁決證據(合格→投資語料放量照走;不合格→評估換嵌入模型,embedspec 世代機制已備)。

守 #9/#10(全數字出自程式輸出)· #15(量測非宣稱)· #28(本地零 usage)。

執行指令矩陣:
  python scripts/measure_finance_retrieval.py           # 全量量測(唯讀,分鐘級)
  python scripts/measure_finance_retrieval.py --k 8     # 換 top-k
"""
import argparse
import statistics
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.philosophy.retrieval import retrieve_items

FIN_DOMAINS = {"economics_econometrics_and_finance", "business_management_and_accounting", "decision_sciences"}

GOLDEN = [
    "通貨膨脹對股票市場的影響", "殖利率曲線倒掛代表什麼", "動量因子在股票報酬的作用",
    "市盈率估值方法的限制", "停損紀律與風險管理", "分散投資如何降低風險",
    "複利對長期投資的效果", "景氣循環與類股輪動", "成交量與市場流動性的關係",
    "融資融券的風險", "股利再投資策略", "指數化被動投資的優點",
]
OFFTOPIC = ["量子重力與弦論的矛盾", "法式料理醬汁的做法", "巴洛克音樂的對位法", "深海熱泉生態系"]


def probe(queries, k):
    rows = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for q in queries:
            hits = retrieve_items(q, k=k, is_super=True)
            doms = []
            for h in hits:
                cur.execute("SELECT i.domain FROM knowledge_sentence s "
                            "JOIN knowledge_item_text it ON s.itext_id=it.itext_id "
                            "JOIN knowledge_item i ON i.item_id=it.item_id WHERE s.sent_id=%s",
                            (getattr(h, "chunk_id", None) or getattr(h, "sent_id", -1),))
                r = cur.fetchone()
                doms.append(r[0] if r else "?")
            scores = [float(getattr(h, "score", 0.0) or 0.0) for h in hits]
            rows.append({"q": q, "n": len(hits), "domains": doms, "scores": scores})
    return rows


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    fin = probe(GOLDEN, args.k)
    neg = probe(OFFTOPIC, args.k)

    prec = []
    for r in fin:
        if r["n"]:
            prec.append(sum(d in FIN_DOMAINS for d in r["domains"]) / r["n"])
        print(f"  [金題] {r['q'][:18]:20} hits={r['n']} 域精度={prec[-1] if r['n'] else '-':.2f} "
              f"top1={r['scores'][0]:.3f}" if r["n"] else f"  [金題] {r['q'][:18]:20} hits=0")
    fin_top1 = [r["scores"][0] for r in fin if r["scores"]]
    neg_top1 = [r["scores"][0] for r in neg if r["scores"]]
    for r in neg:
        print(f"  [離題] {r['q'][:18]:20} hits={r['n']} top1={r['scores'][0]:.3f}" if r["n"]
              else f"  [離題] {r['q'][:18]:20} hits=0")

    print("\n== R6 量測結論(程式輸出,#9)==")
    dp = statistics.mean(prec) if prec else 0.0
    print(f"域精度(金題 top-{args.k} 落投資三域比例)mean={dp:.2f}(題數 {len(prec)}/{len(GOLDEN)} 有命中)")
    if fin_top1 and neg_top1 and max(fin_top1 + neg_top1) > 0:
        f_lo, n_hi = min(fin_top1), max(neg_top1)
        print(f"分數帶:金題 top1 範圍 [{min(fin_top1):.3f},{max(fin_top1):.3f}] mean={statistics.mean(fin_top1):.3f}")
        print(f"       離題 top1 範圍 [{min(neg_top1):.3f},{max(neg_top1):.3f}] mean={statistics.mean(neg_top1):.3f}")
        overlap = n_hi >= f_lo
        print(f"帶重疊:{'有(離題最高 ≥ 金題最低=分數無法當相關性閘,佐證 relevance.py 窄帶警示)' if overlap else '無(可設分數閘)'}")
    if not (fin_top1 and max(fin_top1) > 0):
        print("(ItemCitation 無 score 欄→分數帶不可量;域精度為本量測唯一有效軸——誠實留痕 #15)")
    print(f"離題負控:{sum(1 for r in neg if r['n'])}/{len(OFFTOPIC)} 題仍回非空 hits=「非空但離題」失敗態實證(advisor relevance 閘為對策)")
    verdict = "合格(域精度 ≥0.6 且金題全有命中)" if dp >= 0.6 and len(prec) == len(GOLDEN) else \
        "不合格→R6 裁決:投資語料放量前建議 rerank/域過濾強制,或評估換嵌入模型(embedspec SOP-A)"
    print(f"R6 verdict:{verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
