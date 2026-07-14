"""L5 角色層「誠實博學的我」— 檢索編排 + 三級誠實分級器(v3.0 W8;拍板3 落地)。

🎯 這支在做什麼(白話):對話回答前的**誠實分級**——主檢索(retrieve_all,CLEAN 述詞把關)之外,
   對「庫存但歸屬未驗」之隔離館藏(review_flag=true 有全文作品,被主檢索排除)做**旁查**,決定三級誠實:
   - (iii) 主檢索有真兆 → 正常作答(交 advise+guard;本層不作答、不第二閘)
   - (ii) 主檢索空、但 query 提到隔離館藏某作品 → 第二固定句「知識庫存有此著作但歸屬未驗證,不予引用」
   - (i) 主檢索空、隔離館藏也無 → 第一固定句「知識庫中無此內容」
   分級器=機械(title-mention 確定性比對),閉集僅此二句(憲章 v1.25.0);**不繞 advise/guard 單閘**——
   本層只在「檢索空」時挑閉集句,有真兆時一律走既有 advise 路。
守 #1/#15(誠實閉集、逐字真兆)· 憲章 v1.25.0(三級誠實固定句閉集=判準,分級器住此)· #12(不自建第二閘)。

執行指令矩陣(本檔=library;對話經 serve_advisor_openai 殼):
  python -c "from augur.advisor.answer import honesty_level; print(honesty_level('談談司馬法', []))"

自測(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.advisor.answer              # 印用途+公開入口(唯讀)
  python -m augur.advisor.answer --selftest   # 純紅綠自測(零 IO)
"""
from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE, UNVERIFIED_ATTRIBUTION_RESPONSE
from augur.core import db


def unverified_attribution_lookup(query, limit=3):
    """隔離館藏旁查(拍板3 level-ii):review_flag=true 有全文之作品,其 title/title_zh 是否被 query 提及。
    這些作品被主檢索 CLEAN 述詞(review_flag=false)排除=未驗歸屬;旁查命中=庫存但不予引用(第二固定句),
    非庫中確無。回命中之 title 清單(≤limit);query 空或無命中→[]。title-mention=確定性低誤判信號。"""
    q = (query or "").strip()
    if len(q) < 2:
        return []
    with db.connect() as conn, db.transaction(conn) as cur:
        # title(或 title_zh)為 query 之子字串=user 提到該作品名(如「談談司馬法」→司馬法)
        cur.execute(
            "SELECT DISTINCT w.title FROM philosophy_work w "
            "JOIN philosophy_work_text t ON t.work_id=w.work_id "
            "WHERE w.review_flag IS TRUE AND length(coalesce(w.title,''))>=2 "
            "AND (position(lower(w.title) IN lower(%s))>0 "
            "     OR (w.title_zh IS NOT NULL AND length(w.title_zh)>=2 AND position(w.title_zh IN %s)>0)) "
            "LIMIT %s", (q, q, limit))
        return [r[0] for r in cur.fetchall()]


def honesty_level(query, citations, sidecar_fn=unverified_attribution_lookup):
    """三級誠實分級(拍板3;citations=主檢索 retrieve_all 結果)。
    回 (level, fixed_response|None):
      level 3 → (3, None):有真兆 → 交既有 advise+guard 正常作答(本層不介入)
      level 2 → (2, UNVERIFIED_ATTRIBUTION_RESPONSE):檢索空但隔離館藏命中(庫存未驗)
      level 1 → (1, NO_KNOWLEDGE_RESPONSE):檢索空且隔離館藏無(庫中確無)。
    sidecar_fn 可注入(測試);閉集僅此二句(憲章 v1.25.0,不得執行層自擴)。"""
    if citations:
        return 3, None
    hits = sidecar_fn(query)
    if hits:
        return 2, UNVERIFIED_ATTRIBUTION_RESPONSE
    return 1, NO_KNOWLEDGE_RESPONSE


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # 分級器純函式紅綠(注入 stub sidecar_fn=零 IO,不觸 db)
    lv3 = honesty_level("談談司馬法", ["真兆citation"], sidecar_fn=lambda q: ["不該被叫到"])
    chk("有真兆→level 3+None(不介入)", lv3 == (3, None))
    lv2 = honesty_level("談談司馬法", [], sidecar_fn=lambda q: ["司馬法"])
    chk("空檢索+隔離命中→level 2+未驗句", lv2 == (2, UNVERIFIED_ATTRIBUTION_RESPONSE))
    lv1 = honesty_level("不存在的東西", [], sidecar_fn=lambda q: [])
    chk("空檢索+隔離無→level 1+庫中無句", lv1 == (1, NO_KNOWLEDGE_RESPONSE))
    # 閉集不變式:兩固定句非空且相異(憲章 v1.25.0 閉集僅此二句)
    chk("閉集二句非空且相異",
        bool(NO_KNOWLEDGE_RESPONSE) and bool(UNVERIFIED_ATTRIBUTION_RESPONSE)
        and NO_KNOWLEDGE_RESPONSE != UNVERIFIED_ATTRIBUTION_RESPONSE)
    # IO-bound 入口結構斷言(不呼叫,僅確認公開名存在)
    chk("旁查入口存在", callable(unverified_attribution_lookup))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.answer --selftest;免 DB 免 API)")
