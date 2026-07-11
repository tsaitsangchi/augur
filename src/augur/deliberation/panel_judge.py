"""judge panel — 判官(lens×model)對 proposal 評分/排序(模式 4;補完計畫 §3.3)。

🎯 這支在做什麼(白話):多判官(每 lens 一視角)對提案打分+說理,產「送 VERIFY 優先序/多提案擇優」的
   **soft 排序權**——**panel 分數絕不產生 confirmed**(#15:多數與人意見皆不造真;hard 裁決唯 oracle
   verify_claim)。rubric(評分規準)預註冊入每列(快照,事後可稽)。8b 判官=選配(4GB VRAM 約束,預設 4b);
   model-batched:同 run 同模全跑完再換模(載入 ≤2 次)。llm_fn 注入式(測試可假 LLM 零 GPU)。

守 #15(零 confirmed 權)· #10(rubric 快照入列、rationale 留痕)· #12(lens 住 DB 重用)。
"""
import json

RUBRIC = {   # 預註冊評分規準(v1;改規準=新版本入列,舊列快照不變)
    "version": "rubric_v1",
    "axes": {"verifiability": "宣稱可機械驗證的比例與品質(權重 0.4)",
             "soundness": "論述與證據的一致性、無明顯漏洞(權重 0.4)",
             "completeness": "題目範圍覆蓋度(權重 0.2)"},
    "scale": "0-10(整數或 .5)",
}

SCORE_SCHEMA = {"type": "object", "properties": {
    "score": {"type": "number"}, "rationale": {"type": "string"}},
    "required": ["score", "rationale"]}


def synthesize_panel(cur, llm_fn, proposal_ids, lenses, model):
    """判官團:每 proposal × 每 lens 打分落 deliberation_panel_score。回 [score_id]。
    **零 claim 寫入**(#15 驗收③:panel 路徑不碰 deliberation_claim)。"""
    out = []
    for pid in proposal_ids:                       # model-batched:單模呼叫者自行分批傳入
        cur.execute("SELECT content FROM deliberation_proposal WHERE proposal_id=%s", (pid,))
        row = cur.fetchone()
        if not row:
            continue
        content = row[0]
        for lens in lenses:
            cur.execute("SELECT prompt FROM deliberation_lens WHERE lens_key=%s AND enabled", (lens,))
            lp = cur.fetchone()
            persona = lp[0] if lp else ""
            r = llm_fn(f"{persona}\n依規準評分此提案(0-10)並說理:\n規準:{json.dumps(RUBRIC['axes'], ensure_ascii=False)}"
                       f"\n提案:{json.dumps(content, ensure_ascii=False)[:3500]}", SCORE_SCHEMA)
            score = max(0.0, min(10.0, float(r.get("score", 0))))
            cur.execute("INSERT INTO deliberation_panel_score (proposal_id, judge_model, judge_lens, rubric, "
                        "score, rationale) VALUES (%s,%s,%s,%s,%s,%s) RETURNING score_id",
                        (pid, model, lens, json.dumps(RUBRIC, ensure_ascii=False), score,
                         (r.get("rationale") or "")[:800]))
            out.append(cur.fetchone()[0])
    return out


def ranking(cur, proposal_ids):
    """panel 排序(mean score 降序;soft 權——僅供選送 VERIFY 優先序,零裁決效力)。"""
    cur.execute("SELECT proposal_id, avg(score)::float8, count(*) FROM deliberation_panel_score "
                "WHERE proposal_id = ANY(%s) GROUP BY 1 ORDER BY 2 DESC", (list(proposal_ids),))
    return cur.fetchall()
