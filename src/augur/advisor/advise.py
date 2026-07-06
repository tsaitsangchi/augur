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
    from augur.philosophy.retrieval import retrieve, lexicon_lookup, verify_verbatim, is_low_content
    from augur.advisor.relevance import query_relevant
    src_fn = retrieve if retrieve_fn is None else retrieve_fn
    # RBAC scope 一路傳達(P3,§4.4);機械攔 stale/非逐字(#1,M2)+ 濾 junk 低內容 chunk(B-1 收尾,量測後定)
    citations = [c for c in src_fn(query, k=k, scope=scope) if verify_verbatim(c) and not is_low_content(c.text)]
    lex_fn = lexicon_fn or lexicon_lookup
    lex_entries = [e for t in lex_terms for e in lex_fn(t)]
    # T1-a 檢索相關度閘(誠實優先、只更嚴):out-of-corpus(MBB/太陽能/半導體…)e5-small 硬回離題高分
    # chunk(cosine 0.80~0.88 窄帶與相關無關)→ 系統誤當有料 → LLM 憑弱知識 confabulate。此閘以零 usage
    # 內容詞重疊判定「命中但不相關」,全數不相關 → 視同實質空檢索、落既有 honesty_level([]) 誠實 decline 路。
    # Mode B 附加檔(prompt_fn 覆寫)不套此閘(附檔是用戶自帶語料、相關性由用戶負責、非 augur 庫外題)。
    relevant = bool(citations) and (prompt_fn is not None or query_relevant(query, citations))
    if not relevant:
        citations = []                                   # 全不相關 → 清空,主路徑不餵 LLM 離題 context
    # 誠實保守白名單通識路(v1.35.0 + B-1 收尾):通識/B2 題(general_safe_answerable)即使檢索到
    # (量測證實多為不相關之非-junk)citations,亦走乾淨通識路——忽略雜訊、避免不相關 citation 令 LLM
    # 非決定性答壞(實證:「有沒有穩賺不賠的股票」撈到王充/韓非子/沉香 → 主路徑時好時壞)。
    whitelist_route = (not lex_entries and prompt_fn is None and general_safe_answerable(query))
    if whitelist_route or (not citations and not lex_entries):
        # 三級誠實分級(憲章 v1.25.0):以空 citations 判分級(sidecar 旁查 title-mention 優先;
        # 白名單一律忽略不相關檢索)——level-2(隔離館藏未驗)恆不放行。
        from augur.advisor.answer import honesty_level
        lvl, resp = honesty_level(query, [])
        # 僅 level-1(庫中確無)、非 Mode B、通識白名單三閘 AND 命中 → 交 LLM 通識作答;放行路走
        # empty_payload(數字/引文白名單=∅)+ guard_knowledge + 出處斷言閘,guard 任一不過即 fail-closed。
        if lvl == 1 and whitelist_route:
            ep = empty_payload()
            gen_prompt = build_prompt(query, ep, [], [])
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
        verdict = guard_empty_retrieval(resp, [])
        return {"response": resp, "guard": verdict,
                "citations": [], "lex_entries": [], "prompt": None}
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
