"""P5 顧問組裝 — 檢索 + 唯讀 payload → prompt → LLM → 生成後防幻覺閘。

🎯 唯一動筆處。數字通道(唯讀轉述 payload)⊕ 引文通道(逐字檢索)⊕ 定義通道(lexicon)
   → 組 prompt → llm_fn → guard 鏈。機械強制(非 prompt 自律):檢索全空 → 不經 LLM、
   直回固定誠實句;lexicon 定義引用 → guard_definition 課 locator;
   檢索結果(含注入 retrieve_fn)一律後驗 verify_verbatim(M2:注入不繞過 verify);
   payload 型別分派閘(P8 已拍板 2026-07-04):KnowledgePayload → guard_knowledge
   (數字雙源=payload.numbers() ∪ citation_numbers 檢索真兆數字集),其餘 → guard()。
   llm_fn 為抽象界面(可接 Claude API 或本地 LLM 或 mock),advisor 本身不綁特定 LLM。
守 憲章 v1.17.0(顧問對預測/哲學表皆唯讀、零寫回)· #1/#8/#15(經 guard 落地)。
"""
from augur.advisor.prompt import build_prompt
from augur.advisor.guard import (NO_KNOWLEDGE_RESPONSE, citation_numbers, guard,
                                 guard_attribution, guard_definition, guard_empty_retrieval,
                                 guard_knowledge)
from augur.advisor.payload import KnowledgePayload, empty_payload
from augur.advisor.safe_general import general_safe_answerable


def advise(query, payload, llm_fn, k=6, retrieve_fn=None, lex_terms=(), lexicon_fn=None, prompt_fn=None,
           scope=None):
    """顧問一次問答。

    query:      用戶問題
    payload:    PredictionPayload(唯讀真實預測)
    llm_fn:     prompt(str) -> response(str) 的抽象 LLM 呼叫(可接 Claude API / 本地 / mock)
    k:          檢索引文數
    lex_terms:  需查公版定義的詞(lexicon 路徑;定義引用必附 locator)
    retrieve_fn/lexicon_fn: 檢索抽象界面(預設 philosophy.retrieval;可 mock/注入 Mode B 附加檔檢索)
    prompt_fn:  覆寫 prompt 組裝(Mode B 附加檔用 build_attached_prompt;預設 build_prompt)——
                guard 不變、只換人格框架與檢索語料,誠實三敵防護一致
    回:{response, guard, citations, lex_entries, prompt}
    """
    from augur.philosophy.retrieval import retrieve, lexicon_lookup, verify_verbatim
    src_fn = retrieve if retrieve_fn is None else retrieve_fn
    citations = [c for c in src_fn(query, k=k, scope=scope) if verify_verbatim(c)]  # RBAC scope 一路傳達(P3,§4.4);機械攔 stale/非逐字(#1,M2)
    lex_fn = lexicon_fn or lexicon_lookup
    lex_entries = [e for t in lex_terms for e in lex_fn(t)]
    if not citations and not lex_entries:
        # 檢索全空 → 三級誠實分級(憲章 v1.25.0)+ 誠實保守白名單放行(v1.35.0,W2b/Phase2)。
        # 機械分級(answer.honesty_level 旁查 title-mention):level-2(隔離館藏未驗)恆不放行。
        from augur.advisor.answer import honesty_level
        lvl, resp = honesty_level(query, citations)
        # 誠實保守白名單(v1.35.0):僅 level-1(庫中確無)、非 Mode B(prompt_fn 未覆寫)、通識白名單三閘
        # AND 命中 → 交 LLM 通識作答;放行路走 empty_payload(數字/引文白名單=∅)+ guard_knowledge +
        # 出處斷言閘,guard 任一不過即 fail-closed 退回第一固定句(誠實下限=現行、最壞退化不惡化)。
        if lvl == 1 and prompt_fn is None and general_safe_answerable(query):
            ep = empty_payload()
            gen_prompt = build_prompt(query, ep, [], lex_entries)
            gen_resp = llm_fn(gen_prompt)
            vk = guard_knowledge(gen_resp, ep, [], sql_numbers=())
            va = guard_attribution(gen_resp, [])
            verdict = {"pass": vk["pass"] and va["pass"], "issues": vk["issues"] + va["issues"]}
            if verdict["pass"]:
                return {"response": gen_resp, "guard": verdict,
                        "citations": [], "lex_entries": [], "prompt": gen_prompt}
            resp = NO_KNOWLEDGE_RESPONSE                 # guard 不過 → fail-closed
            return {"response": resp, "guard": guard_empty_retrieval(resp, []),
                    "citations": [], "lex_entries": [], "prompt": gen_prompt}
        verdict = guard_empty_retrieval(resp, citations)
        return {"response": resp, "guard": verdict,
                "citations": citations, "lex_entries": lex_entries, "prompt": None}
    prompt = (prompt_fn or build_prompt)(query, payload, citations, lex_entries)
    response = llm_fn(prompt)
    if isinstance(payload, KnowledgePayload):
        # P8 域條款(已拍板 2026-07-04):雙源=payload.numbers() ∪ 本回合檢索真兆數字集
        verdict = guard_knowledge(response, payload, citations,
                                  sql_numbers=citation_numbers(citations))
    else:
        verdict = guard(response, payload, citations)
    av = guard_attribution(response, citations)      # 第五條(v1.35.0):主路徑亦查出處斷言之 citation 佐證
    if not av["pass"]:                               # (R2:撈到不相關 citation 卻捏造古典出處/錯章 → fail-closed)
        verdict["issues"].extend(av["issues"])
        verdict["pass"] = not verdict["issues"]
    if lex_entries:
        dv = guard_definition(response, lex_entries)
        verdict["issues"].extend(dv["issues"])
        verdict["pass"] = not verdict["issues"]
    return {"response": response, "guard": verdict,
            "citations": citations, "lex_entries": lex_entries, "prompt": prompt}
