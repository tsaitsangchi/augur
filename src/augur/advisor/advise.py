"""P5 顧問組裝 — 檢索 + 唯讀 payload → prompt → LLM → 生成後防幻覺閘。

🎯 唯一動筆處。數字通道(唯讀轉述 payload)⊕ 引文通道(逐字檢索)→ 組 prompt → llm_fn → guard。
   llm_fn 為抽象界面(可接 Claude API 或本地 LLM 或 mock),advisor 本身不綁特定 LLM。
守 憲章 v1.17.0(顧問對預測/哲學表皆唯讀、零寫回)· #1/#8/#15(經 guard 落地)。
"""
from augur.advisor.prompt import build_prompt
from augur.advisor.guard import guard


def advise(query, payload, llm_fn, k=6, retrieve_fn=None):
    """顧問一次問答。

    query:     用戶問題
    payload:   PredictionPayload(唯讀真實預測)
    llm_fn:    prompt(str) -> response(str) 的抽象 LLM 呼叫(可接 Claude API / 本地 / mock)
    k:         檢索引文數
    回:{response, guard, citations, prompt}
    """
    from augur.philosophy.retrieval import retrieve
    citations = (retrieve_fn or retrieve)(query, k=k)
    prompt = build_prompt(query, payload, citations)
    response = llm_fn(prompt)
    verdict = guard(response, payload, citations)
    return {"response": response, "guard": verdict, "citations": citations, "prompt": prompt}
