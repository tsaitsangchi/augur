#!/usr/bin/env python
"""S3 真兆 context 注入 — 每題實跑 retrieve_all 取**真實** citations + 真實 payload,寫 advisor_distill_context。

🎯 這支在做什麼(白話):對每題(advisor_distill_question 中 context_built=false 者)實跑本地
   philosophy.retrieval.retrieve_all(query, scope),把**真實檢索結果**(含情境2 那種撈到的
   不相關哲學 chunk——這正是要訓模型識別的輸入)+ 真實 example payload,序列化成 context JSONB,
   寫 advisor_distill_context;target_response 欄**留空待 S4**(界線-B:真實檢索 vs teacher 示範分欄)。
   同步記 query_relevant 判定(T1-a 相關度閘)——情境2 題應 relevant=false(撈到的是真不相關 citation)。

   **零 Claude 編造**:context 全為真實 retrieve_all 輸出(可 trace 回 DB chunk_id/sent_id 列),
   payload 為真實 example_payload(as-of 凍結預測);此步不呼叫任何 LLM。
   **冪等 + 游標 resume**(#6):UNIQUE(question_id) + context_built 旗標;中斷可續、重跑不重複。
   **GATE**:context 一律真實檢索、零編造;情境2 題確認 relevant=false(撈到真不相關 citation)。
守 #1(context=真兆檢索、可溯源;非 AI 生)· #6(冪等游標)· #9/#10(citation trace 回 chunk_id/sent_id)·
   #15(GATE 實證情境2 撈到真不相關)· 憲章 v1.17.0(顧問對哲學/預測表唯讀)· CLAUDE #29。
   計畫 SSOT=reports/augur_advisor_selfqa_training_plan_20260706.md §S3 · §③界線-B。

執行指令矩陣:
  python scripts/advisor_distill_build_context.py                # 無參數=印矩陣 + 現況(安全預設)
  python scripts/advisor_distill_build_context.py --run          # 對所有 pending 題實跑檢索、寫 context
  python scripts/advisor_distill_build_context.py --run --limit 20   # 小批(游標 resume 可續)
  python scripts/advisor_distill_build_context.py --stats        # 唯讀:已建 context 數 / relevant 分佈
"""
import argparse
import json
from dataclasses import asdict

import _bootstrap  # noqa: F401
from augur.core import db

# 蒸餾檢索 scope:super(is_super=True,無 domain 收窄)——復現生產失敗路徑(計畫 §S3/§①環1 super 路徑),
# 讓情境2 題也撈到「離題但高分」的假 context,才能訓模型識別。(蒸餾 staging、非對外服務。)
_SCOPE = (True, frozenset(), 1)


def _serialize_citation(c):
    """把 Citation / ItemCitation dataclass 轉可 JSON 之 dict(型別感知,含 __type__ 標記可溯源型別)。
    score 為 float 直存;不含任何 AI 生成——純 DB 檢索列之欄位。"""
    d = asdict(c)
    d["__type__"] = type(c).__name__
    return d


def build_one(query):
    """對單題實跑真實檢索:回 (context_dict, n_citations, relevant)。零 LLM、零編造。"""
    from augur.philosophy.retrieval import retrieve_all, verify_verbatim, is_low_content
    from augur.advisor.relevance import query_relevant, best_overlap
    from augur.advisor.payload import example_payload
    raw = retrieve_all(query, k=6, scope=_SCOPE)
    cites = [c for c in raw if verify_verbatim(c) and not is_low_content(c.text)]  # 同 advise() 前處理
    relevant = query_relevant(query, cites)
    payload = example_payload()
    ctx = {
        "query": query,
        "citations": [_serialize_citation(c) for c in cites],
        "relevance_overlap": round(best_overlap(query, cites), 4),
        "relevant": relevant,
        "payload": {
            "as_of": payload.as_of, "horizon": payload.horizon, "model": payload.model,
            "picks": [asdict(p) for p in payload.picks],
            "validation": payload.validation,
        },
    }
    return ctx, len(cites), relevant


def _pending(conn, limit):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT question_id, question FROM advisor_distill_question "
            "WHERE context_built IS FALSE ORDER BY question_id" + (f" LIMIT {int(limit)}" if limit else ""))
        return cur.fetchall()


def run(conn, limit):
    """對 pending 題(context_built=false)逐題實跑、**逐題 commit**(游標 resume:中斷後已建者不重跑)。回 processed 計數。"""
    pending = _pending(conn, limit)
    if not pending:
        print("  無 pending 題(全部 context 已建)。")
        return 0
    done = 0
    for qid, query in pending:
        ctx, n, relevant = build_one(query)                  # 檢索在 transaction 外(唯讀、慢);寫入才進 transaction
        with db.transaction(conn) as cur:
            cur.execute(
                "INSERT INTO advisor_distill_context "
                "(question_id, context, n_citations, relevant, retrieval_scope) "
                "VALUES (%s,%s,%s,%s,%s) "
                "ON CONFLICT (question_id) DO UPDATE SET "
                "context=EXCLUDED.context, n_citations=EXCLUDED.n_citations, "
                "relevant=EXCLUDED.relevant, retrieval_scope=EXCLUDED.retrieval_scope, built_at=now()",
                (qid, json.dumps(ctx, ensure_ascii=False), n, relevant, str(_SCOPE)))
            cur.execute("UPDATE advisor_distill_question SET context_built=true WHERE question_id=%s", (qid,))
        done += 1
        if done % 10 == 0:
            print(f"  … {done}/{len(pending)} 題 context 已建")
    return done


def stats(cur):
    """已建 context 現況 + 情境×relevant 交叉(GATE 佐證:情境2 應多 relevant=false)。"""
    cur.execute("SELECT count(*) FROM advisor_distill_context")
    total = cur.fetchone()[0]
    cur.execute(
        "SELECT q.situation_label, c.relevant, count(*) "
        "FROM advisor_distill_context c JOIN advisor_distill_question q USING(question_id) "
        "GROUP BY q.situation_label, c.relevant ORDER BY q.situation_label, c.relevant")
    print(f"── context 現況(已建 {total})── (情境 × relevant 交叉)")
    _ln = {1: "in-corpus", 2: "out-of-corpus", 3: "impossible"}
    for label, rel, cnt in cur.fetchall():
        print(f"  情境{label}({_ln.get(label,'?')})  relevant={rel!s:>5}: {cnt}")
    return total


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--stats", action="store_true")
    args, _ = ap.parse_known_args()

    if not (args.run or args.stats):
        print(__doc__.split("執行指令矩陣:")[1])
        with db.connect() as conn, db.transaction(conn) as cur:
            stats(cur)
        return

    with db.connect() as conn:
        if args.stats:
            with db.transaction(conn) as cur:
                stats(cur)
            return
        done = run(conn, args.limit)                          # 逐題 commit、游標 resume(#6)
        with db.transaction(conn) as cur:
            stats(cur)
    print(f"\n✓ S3 完成:本次處理 {done} 題(context 全為真實檢索、零編造;target_response 待 S4)")


if __name__ == "__main__":
    main()
