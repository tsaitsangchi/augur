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


def _render_picks_table(payload, top=15):
    """確定性 picks 表(#1:picks=payload ground truth、不經弱 LLM 幻覺)。
    弱本機模型(qwen3:8b)實證會幻覺『選哪些股』+股名+迴圈重複(4 輪 prompt 迭代皆漂移=能力天花板)
    → picks 改由 payload 直接排版注入、LLM 僅負責它可靠的 caveat 敘述(v1.37.0 本機模型約束內、非換外部)。
    score 4dp=對齊 guard 白名單口徑;注入表為 ground truth、免 guard(數字皆出 payload)。"""
    picks = list(payload.picks)[:top]
    if not picks:
        return ""
    # P6 相對機率附欄(payload.probs 唯讀;p 2dp 渲染=4dp 白名單之顯示形;判死 horizon 帶標籤硬綁 D2)
    pmap = {}
    for sym, h, pv, ev, cd in getattr(payload, "probs", ()):
        pmap.setdefault(sym, {})[h] = (pv, ev)
    def _prow(p):
        m = pmap.get(p.symbol, {})
        if not m:
            return ""
        seg = []
        for h, tag in ((20, "P30"), (40, "P60"), (120, "P120")):
            if h in m:
                pv, ev = m[h]
                seg.append(f"{tag} {pv:.2f}" + ("(dead)" if ev == "dead" else ""))
        return(" | " + " ".join(seg)) if seg else ""
    lines = [f"{p.rank}. {p.symbol} {p.name}(score {p.score:.4f}){_prow(p)}" for p in picks]
    more = f"(共 {len(payload.picks)} 檔、列前 {len(picks)})" if len(payload.picks) > len(picks) else ""
    out = (f"根據模型 as-of {payload.as_of}({payload.model} H{payload.horizon})之相對強弱排序,"
           f"看好 top {len(picks)}{more}:\n" + "\n".join(lines))
    note = getattr(payload, "prob_note", "")
    if pmap and note:      # §1.1 四誠實標記與機率同段硬綁、不可分離(v1.40.0;缺一=回歸 FAIL)
        out += "\n── 相對機率附欄說明(與上列數字不可分離)──\n" + note
    return out


def _concept_links(lex_terms, language="zh", scope=None):
    """W2 接線(e2e 計畫 P3;G6 收窄後):lex_terms 兩兩查 term_affinity 真統計 + 共現逐字證據**數**。
    回 [{a,b,npmi,basis_n,n_evidence}](零 AI 生成:npmi/basis_n=S7 封閉式統計;證據句本身不進 prompt、
    僅計數——逐字句呈現屬 W7 後續);scope=(is_super, allowed, user_id) 或 None(fail-closed 只計公版側)。"""
    from augur.knowledge.concept_graph import related_terms, cooccurrence_evidence
    is_super, allowed, uid = (scope if scope else (False, None, None))
    out = []
    terms = [t for t in lex_terms if t][:4]                  # 上限防組合爆炸
    for i, a in enumerate(terms):
        rel = {b: (v, n) for b, v, n in related_terms(a, language=language)}
        for b in terms[i + 1:]:
            if b in rel:
                ev = cooccurrence_evidence(a, b, language=language, limit=3,
                                           is_super=is_super, allowed_domains=allowed, owner_user_id=uid)
                out.append({"a": a, "b": b, "npmi": rel[b][0], "basis_n": rel[b][1], "n_evidence": len(ev)})
    return out


def _concept_block(links):
    """概念關聯之 prompt 參考塊(確定性、真統計;明示 LLM 不得複述數值→guard 數字白名單不受擾)。"""
    if not links:
        return ""
    lines = [f"- 「{l['a']}」×「{l['b']}」:共現統計關聯(npmi {l['npmi']:.2f}、支持句 {l['basis_n']}、可溯源共現例 {l['n_evidence']})"
             for l in links]
    return ("\n\n[思想關聯參考(語料共現真統計,零 AI 生成;僅供理解脈絡——回答中不得複述本段數值)]\n"
            + "\n".join(lines))


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
    from augur.advisor.relevance import relevant_citations
    from augur.advisor.prompt import _asks_direction_or_path, build_direction_refusal
    # lock②/閘⑥:方向/逐日價格/目標價/準確率排名題 → 短路弱 LLM,直回固定誠實句(gate 狀態 SSOT=
    #   direction_gate 表、逐日價格永久除外)。**不論 picking_intent 是否誤建 picks 皆短路**:此類問句
    #   (每日/準確率/漲跌/未來N天)本就該誠實 decline;純相對問(如「報酬最高前N」不含這些詞)不觸
    #   _DIR_PAT、照走選股主路徑。Mode B(附檔)不套。
    #   此處無 cur(advise() 不持 DB 連線)→ build_direction_refusal 自連唯讀查 direction_gate;
    #   DB 例外退回 hardcode 常數(fail-closed,句不消失)。
    if prompt_fn is None and _asks_direction_or_path(query):
        return {"response": build_direction_refusal(), "guard": {"pass": True, "issues": []},
                "citations": [], "lex_entries": [], "prompt": None}
    src_fn = retrieve if retrieve_fn is None else retrieve_fn
    lex_fn = lexicon_fn or lexicon_lookup
    lex_entries = [e for t in lex_terms for e in lex_fn(t)]
    def _clean(cits):                                    # 機械攔 stale/非逐字(#1,M2)+ 濾 junk 低內容 chunk(B-1)
        return [c for c in cits if verify_verbatim(c) and not is_low_content(c.text)]
    # RBAC scope 一路傳達(P3,§4.4)。
    # T1-a 檢索相關度閘 + translate-for-RETRIEVAL(N9,2026-07-07,誠實優先、只更嚴):
    #   e5-small 對 out-of-corpus(MBB/太陽能/半導體…)硬回離題高分 chunk → 誤當有料令 LLM confabulate。
    #   relevant_citations 以零 usage 內容詞重疊逐條判「命中且相關」——**只留與 query 共享夠強辨識性專詞
    #   (perovskite/solar/孔子/知行合一…)者**,泛用字(system/energy/research/what)與單 CJK 字(能/太/心)
    #   之巧合共現不算(擋前版「系統分析/能源效率/MBB」死因)。全數不相關 → 視同空檢索、走誠實 decline。
    # translate-for-RETRIEVAL(**fallback**):augur 技術/財經文獻多為英文,e5-small 對 CJK 問句跨語 kNN 常把
    #   英文正解沉在哲學/ERP 雜訊裡撈不上來。故 CJK 查詢**先以原文檢索+過濾**;哲學題此時已命中即止(不引英文
    #   噪);**僅當**過濾後無相關引文,**才**譯英文、以英文 query 檢索+過濾(技術跨語題如 solar 靠此撈回)。
    #   譯文**只決定用哪個 query 檢索**——不入 citation/答案/guard(命門);譯失敗(None:OOM/逾時/無 CJK)→
    #   只有原查詢結果(誠實基線,多半 decline)、絕不 raise。Mode B 附加檔(prompt_fn)不套本閘/不翻譯。
    raw = _clean(src_fn(query, k=k, scope=scope))
    if prompt_fn is not None:
        citations = raw                                  # Mode B:附檔由用戶負責相關性,不過濾、不翻譯
    else:
        citations = relevant_citations(query, raw)
        if not citations:                                # 原文檢索無相關 → 英文 fallback(技術跨語題)
            from augur.advisor.query_translation import translate_for_retrieval
            en_query = translate_for_retrieval(query)    # 無 CJK / OOM / 逾時 → None(fail-closed,不 raise)
            if en_query:
                # min_terms=2:誤譯之 en_query 靠單一泛詞巧撞離題引文→過閘→LLM 瞎掰(實證 多主柵→multi-master
                # bus 撞「advantage」一詞令 qwen3 瞎掰光通信);要求 ≥2 辨識詞共享,誤譯 fallback 收斂為誠實 decline。
                citations = relevant_citations(en_query, _clean(src_fn(en_query, k=k, scope=scope)), min_terms=2)
    # 誠實保守白名單通識路(v1.35.0 + B-1 收尾):通識/B2 題(general_safe_answerable)即使檢索到
    # (量測證實多為不相關之非-junk)citations,亦走乾淨通識路——忽略雜訊、避免不相關 citation 令 LLM
    # 非決定性答壞(實證:「有沒有穩賺不賠的股票」撈到王充/韓非子/沉香 → 主路徑時好時壞)。
    whitelist_route = (not lex_entries and prompt_fn is None and general_safe_answerable(query))
    # D4(計畫 §5.2):PredictionPayload 帶真實 picks 時,picks 本身即 context——不得落空檢索誠實-decline
    # 路(否則選股題永遠回「知識庫中無此內容」、picks 永不呈現)。picks 走主路徑 → build_prompt 渲染
    # picks 區塊 + guard() 機械強制數字 ∈ payload.numbers()(捏造數字被擋);此判斷不鬆動 guard、
    # 不繞過任何閘,只是讓「有真兆 payload」不被當成「無 context」。has_picks 對 KnowledgePayload/empty 恆 False。
    has_picks = bool(getattr(payload, "picks", ()))
    if not has_picks and (whitelist_route or (not citations and not lex_entries)):
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
    concept_links = []
    if prompt_fn is None and lex_entries:                    # W2:主路徑+有定義詞才接(Mode B 不套,同其餘閘)
        concept_links = _concept_links(lex_terms, scope=scope)
        prompt += _concept_block(concept_links)
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
    if has_picks:      # D4b 確定性 picks 注入:picks 由 payload ground truth 排版(不經弱 LLM 幻覺)+ LLM caveat 敘述
        response = _render_picks_table(payload) + "\n\n---\n" + response
    return {"response": response, "guard": verdict,
            "citations": citations, "lex_entries": lex_entries, "prompt": prompt,
            "concept_links": concept_links}
