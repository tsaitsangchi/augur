"""P5 顧問組裝 — 檢索 + 唯讀 payload → prompt → LLM → 生成後防幻覺閘。

🎯 唯一動筆處。數字通道(唯讀轉述 payload)⊕ 引文通道(逐字檢索)⊕ 定義通道(lexicon)
   → 組 prompt → llm_fn → guard 鏈。機械強制(非 prompt 自律):檢索全空 → 不經 LLM、
   直回固定誠實句;lexicon 定義引用 → guard_definition 課 locator;
   檢索結果(含注入 retrieve_fn)一律後驗 verify_verbatim(M2:注入不繞過 verify);
   payload 型別分派閘(P8 已拍板 2026-07-04):KnowledgePayload → guard_knowledge
   (數字雙源=payload.numbers() ∪ citation_numbers 檢索真兆數字集),其餘 → guard()。
   llm_fn 為抽象界面(可接 Claude API 或本地 LLM 或 mock),advisor 本身不綁特定 LLM。
守 憲章 v1.17.0(顧問對預測/哲學表皆唯讀、零寫回)· #1/#8/#15(經 guard 落地)。
   PME S4：主路徑可附加進化解讀塊（`include_evolution`／`evolution_md`）；Mode B 不套；零回流特徵。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.advise              # 印用途+公開入口（唯讀）
  python -m augur.advisor.advise --selftest   # 純紅綠自測（零 IO）
"""
import re

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
    # 雙窗／漲跌看板：全文已在 validation.board_text（禁再套 LLM 複誦）
    board = (getattr(payload, "validation", None) or {}).get("board_text")
    if isinstance(board, str) and board.strip():
        note = getattr(payload, "prob_note", "") or ""
        out = board.strip()
        if note:
            out += "\n── 相對機率附欄說明(與上列數字不可分離)──\n" + note
        return out
    picks = list(payload.picks)[:top]
    if not picks:
        return ""
    # 去重（同 symbol 只留首次）
    seen, uniq = set(), []
    for p in picks:
        if p.symbol in seen:
            continue
        seen.add(p.symbol)
        uniq.append(p)
    picks = uniq
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
    # model 已含尺標時勿再疊 H{horizon}（對症：相對機率Top10/H60 H60）
    model = getattr(payload, "model", "") or ""
    head_model = model if re.search(r"H\d+|看板", model) else f"{model} H{payload.horizon}"
    out = (f"根據模型 as-of {payload.as_of}({head_model})之相對強弱排序,"
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


def _bridge_links(query, cur, limit=5):
    """K 計畫 K1 接線:問句命中 raw 欄位/特徵名 → 查 field_knowhow_lexical_affinity 之 know-how 詞面關聯。
    唯讀素養層;**lexical=欄位名稱詞×know-how 詞之語料句共現,非該欄資料值與報酬之相關**(免責硬綁於塊首)。"""
    q = (query or "").lower()
    if not q:
        return []
    try:
        if cur is None:
            from augur.core import db as _db
            with _db.connect() as _conn:
                return _bridge_links(query, _conn.cursor(), limit=limit)
        cur.execute(
            "SELECT DISTINCT dataset, column_name FROM field_term_map "
            "WHERE length(column_name) >= 4 AND position(lower(column_name) IN %s) > 0 LIMIT 3", (q,))
        hits = cur.fetchall()
        if not hits:
            return []
        out = []
        for ds, col in hits:
            cur.execute(
                "SELECT knowhow_term, stat_value, cooc_sents, corpus FROM field_knowhow_lexical_affinity "
                "WHERE dataset=%s AND column_name=%s AND stat_key='npmi' "
                "ORDER BY (corpus='items') DESC, stat_value DESC LIMIT %s", (ds, col, limit))
            rows = cur.fetchall()
            if rows:
                out.append({"field": f"{ds}.{col}",
                            "terms": [{"t": r[0], "npmi": float(r[1]), "n": int(r[2]), "corpus": r[3]} for r in rows]})
        return out
    except Exception:
        return []          # fail-closed:橋不可用=沉默略過,不擾主路徑


def _bridge_block(links):
    """橋參考塊(確定性;免責與數值同塊硬綁;LLM 不得複述數值)。"""
    if not links:
        return ""
    lines = []
    for l in links:
        ts = "、".join(f"「{t['t']}」(npmi {t['npmi']:.2f}/共現 {t['n']} 句/{t['corpus']})" for t in l["terms"])
        lines.append(f"- 欄位 {l['field']} ↔ know-how 詞:{ts}")
    return ("\n\n[欄位↔know-how 詞面關聯(lexical:欄位名稱詞與 know-how 詞之語料句共現統計——"
            "**非該欄位資料數值與報酬之相關**;僅供解讀脈絡,回答中不得複述本段數值、不得當交易依據)]\n"
            + "\n".join(lines))


def advise(query, payload, llm_fn, k=6, retrieve_fn=None, lex_terms=(), lexicon_fn=None, prompt_fn=None,
           scope=None, evolution_md=None, include_evolution=True, auto_lift=None, answer_mode=None):
    """顧問一次問答。

    query:      用戶問題
    payload:    PredictionPayload(唯讀真實預測)
    llm_fn:     prompt(str) -> response(str) 的抽象 LLM 呼叫(可接 Claude API / 本地 / mock)
    k:          檢索引文數
    lex_terms:  需查公版定義的詞(lexicon 路徑;定義引用必附 locator)
    retrieve_fn/lexicon_fn: 檢索抽象界面(預設 philosophy.retrieval.retrieve_all＝works∪items、
                不傳策展 domain=；可 mock/注入 Mode B 附加檔檢索)
    prompt_fn:  覆寫 prompt 組裝(Mode B 附加檔用 build_attached_prompt;預設 build_prompt)——
                guard 不變、只換人格框架與檢索語料,誠實三敵防護一致
    evolution_md: PME S4 解讀 markdown（注入則優先；None 且 include_evolution 時 fail-soft 載入）
    include_evolution: 主路徑是否附加 S4 進化解讀（Mode B／prompt_fn 覆寫時一律不附加）
    auto_lift:  KH0-ANSWER-AUTO-LIFT 熱路徑（None＝讀 AUGUR_KH0_ANSWER_AUTO_LIFT；預設關）。
                僅 guard.pass ∧ item 引文 ∧ 非 Mode B ∧ 非 picks；fail-soft 不炸問答。
    answer_mode: None/auto｜compact｜full｜two_phase——知-how／讀出自動緊湊（凍結引文＋短答；
                對症本機 LLM／prompt 體積，非 KH 入庫）。two_phase＝先凍結再短答（同一回合完成）。
    回:{response, guard, citations, lex_entries, prompt, auto_lift?, readout?, compact?}
    """
    from augur.philosophy.retrieval import retrieve_all, lexicon_lookup, verify_verbatim, is_low_content
    from augur.advisor.relevance import (
        relevant_citations, rel_prob_topk_intent, single_ticker_rel_intent,
        rel_prob_board_intent,
    )
    from augur.advisor.prompt import _asks_direction_or_path, build_direction_refusal
    # lock②/閘⑥:方向/逐日價格/目標價題 → 固定誠實句。**例外(PRED-KH)**:若已注入真實
    # PredictionPayload.picks(相對機率 TopK／單股 B2／選股),則不短路——改走真兆主路徑
    # (auto_rel_topn：口語「上漲機率／漲跌幅 TopN」改答相對機率,disclaimer 在 prob_note)。
    # Mode B(附檔)不套。DB 例外時 build_direction_refusal fail-closed。
    # 防衛：呼叫端漏注入時，advise 內仍依意圖補相對 payload，禁止空拒「漲跌幅 topN」。
    has_pred_picks = bool(getattr(payload, "picks", ()))
    # 已注入雙窗看板 → 確定性全文、免 LLM（對症：弱模型複誦重複列／只回單窗）
    board_text = (getattr(payload, "validation", None) or {}).get("board_text")
    if prompt_fn is None and isinstance(board_text, str) and board_text.strip():
        table = _render_picks_table(payload)
        return {
            "response": table,
            "guard": {"pass": True, "issues": []},
            "citations": [], "lex_entries": [], "prompt": None,
            "concept_links": [], "picks_ground_truth": True,
        }
    if prompt_fn is None and not has_pred_picks:
        try:
            board = rel_prob_board_intent(query)
            topk = rel_prob_topk_intent(query)
            sti = single_ticker_rel_intent(query)
            if board is not None:
                from augur.advisor.payload import build_rel_prob_board_payload
                payload = build_rel_prob_board_payload(
                    board["k"], board["horizons"],
                    include_bottom=board["include_bottom"],
                    include_intersect=board["include_intersect"],
                )
                table = _render_picks_table(payload)
                return {
                    "response": table,
                    "guard": {"pass": True, "issues": []},
                    "citations": [], "lex_entries": [], "prompt": None,
                    "concept_links": [], "picks_ground_truth": True,
                }
            if topk is not None:
                from augur.advisor.payload import build_rel_prob_topk_payload
                payload = build_rel_prob_topk_payload(topk[0], topk[1])
                has_pred_picks = bool(getattr(payload, "picks", ()))
            elif sti is not None:
                from augur.advisor.payload import build_single_ticker_rel_payload
                payload = build_single_ticker_rel_payload(sti[0], sti[1])
                has_pred_picks = bool(getattr(payload, "picks", ()))
                # ETF／宇宙外代號:無 picks 時仍給誠實建議包（禁假漲跌％）
                if not has_pred_picks and prompt_fn is None:
                    from augur.advisor.prompt import build_direction_refusal
                    body = build_direction_refusal(query=query)
                    if not _asks_direction_or_path(query):
                        # 純相對問句:不要套「方向判死」開場,只留建議包＋短拒
                        from augur.advisor.prompt import _advice_bundle_for_query, _SIM_HINT
                        body = (
                            f"關於 **{sti[0]}** 的相對強弱:現役相對機率宇宙**沒有此代號**的可引用列 "
                            f"(H{sti[1]})——常見於 ETF／未納入 train 宇宙標的。"
                            "我**不能**捏造該檔「相對％」或「看漲／看跌％」。"
                            + _advice_bundle_for_query(query)
                            + _SIM_HINT
                        )
                    return {"response": body, "guard": {"pass": True, "issues": []},
                            "citations": [], "lex_entries": [], "prompt": None,
                            "picks_ground_truth": False,
                            "rel_miss": {"stock_id": sti[0], "horizon": sti[1]}}
        except Exception:
            has_pred_picks = bool(getattr(payload, "picks", ()))
    if prompt_fn is None and _asks_direction_or_path(query) and not has_pred_picks:
        return {"response": build_direction_refusal(query=query), "guard": {"pass": True, "issues": []},
                "citations": [], "lex_entries": [], "prompt": None, "picks_ground_truth": False}
    # KH-XDOM-S01：預設合併檢索＝retrieve_all（works∪items；不傳策展 domain=）；服器亦可顯式注入同函。
    src_fn = retrieve_all if retrieve_fn is None else retrieve_fn
    lex_fn = lexicon_fn or lexicon_lookup
    lex_entries = [e for t in lex_terms for e in lex_fn(t)]
    def _clean(cits):                                    # 機械攔 stale/非逐字(#1,M2)+ 濾 junk 低內容 chunk(B-1)
        return [c for c in cits if verify_verbatim(c) and not is_low_content(c.text)]
    # picks_skip_A（2026-08-05）:有真兆 picks 且非 Mode B → 跳過向量檢索／譯英
    # （11GB 機上 embed↔8b 互擠實證撞死 llama-server）。lexicon 仍可跑（輕量、非 embed）。
    # Mode B(prompt_fn)不套——附檔檢索由用戶負責。
    has_picks = has_pred_picks
    readout_meta = None
    compact_meta = None
    if has_picks and prompt_fn is None:
        citations = []
    else:
        # RBAC scope 一路傳達(P3,§4.4)。
        # KH-READOUT-RESOLVE：標題／檔名＋讀出意圖 → 有界原文引文，優先於 ANN 雜訊。
        citations = []
        if prompt_fn is None and not has_picks:
            try:
                from augur.knowledge.readout import advise_readout_citations, is_readout_intent
                if is_readout_intent(query):
                    ro = advise_readout_citations(query, scope=scope)
                    # readout 已標題／檔名定位：勿套 ANN junk 的 is_low_content
                    # （PDF TOC／寬空白會被誤判密度不足，如 aap.pdf 應付帳款手冊）
                    keep = [c for c in (ro or []) if verify_verbatim(c)]
                    if keep:
                        citations = keep
                        readout_meta = {
                            "via": "readout",
                            "item_ids": sorted({int(c.item_id) for c in keep if getattr(c, "item_id", None)}),
                        }
            except Exception:
                readout_meta = None
                citations = []
        if prompt_fn is not None:
            raw = _clean(src_fn(query, k=k, scope=scope))
            citations = raw  # Mode B
        elif not citations:
            # T1-a 檢索相關度閘 + translate-for-RETRIEVAL（非 readout 路徑）
            raw = _clean(src_fn(query, k=k, scope=scope))
            citations = relevant_citations(query, raw)
            if not citations:
                from augur.advisor.query_translation import translate_for_retrieval
                en_query = translate_for_retrieval(query)
                if en_query:
                    citations = relevant_citations(
                        en_query, _clean(src_fn(en_query, k=k, scope=scope)), min_terms=2)
            if not citations:
                from augur.advisor.relevance import kh0_floor_citations
                citations = kh0_floor_citations(query, raw)
            from augur.knowledge.auto_admit import rank_citations_kh_first
            citations = rank_citations_kh_first(citations)
    # 誠實保守白名單通識路(v1.35.0 + B-1 收尾):通識/B2 題(general_safe_answerable)即使檢索到
    # (量測證實多為不相關之非-junk)citations,亦走乾淨通識路——忽略雜訊、避免不相關 citation 令 LLM
    # 非決定性答壞(實證:「有沒有穩賺不賠的股票」撈到王充/韓非子/沉香 → 主路徑時好時壞)。
    whitelist_route = (not lex_entries and prompt_fn is None and general_safe_answerable(query))
    # D4(計畫 §5.2):PredictionPayload 帶真實 picks 時,picks 本身即 context——不得落空檢索誠實-decline
    # 路(否則選股題永遠回「知識庫中無此內容」、picks 永不呈現)。picks 走主路徑 → build_prompt 渲染
    # picks 區塊 + guard() 機械強制數字 ∈ payload.numbers()(捏造數字被擋);此判斷不鬆動 guard、
    # 不繞過任何閘,只是讓「有真兆 payload」不被當成「無 context」。has_picks 對 KnowledgePayload/empty 恆 False。
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
                        "citations": [], "lex_entries": [], "prompt": gen_prompt,
                        "picks_ground_truth": False}
            resp = NO_KNOWLEDGE_RESPONSE                 # guard 不過 → fail-closed
            return {"response": resp, "guard": guard_empty_retrieval(resp, []),
                    "citations": [], "lex_entries": [], "prompt": gen_prompt,
                    "picks_ground_truth": False}
        verdict = guard_empty_retrieval(resp, [])
        return {"response": resp, "guard": verdict,
                "citations": [], "lex_entries": [], "prompt": None,
                "picks_ground_truth": False}
    # 緊湊作答（readout／local 知-how 自動）：凍結引文＋短答 prompt＋抛光輸出
    compact_meta = None
    use_compact = False
    if prompt_fn is None and not has_picks:
        from augur.knowledge.compact_answer import freeze_citations, should_compact, wrap_compact_llm
        use_compact = should_compact(
            query, citations, readout_meta=readout_meta, answer_mode=answer_mode,
        )
        if use_compact:
            prefer = (readout_meta or {}).get("item_ids") or []
            ask_terms = []
            try:
                from augur.knowledge.readout import extract_ask_tail, _ask_prefer_terms
                ask_terms = _ask_prefer_terms(extract_ask_tail(query))
            except Exception:
                ask_terms = []
            citations = freeze_citations(
                citations, prefer_item_ids=prefer, prefer_terms=ask_terms or None,
            )
            compact_meta = {
                "mode": (answer_mode or "auto"),
                "n_cites": len(citations),
                "prefer_item_ids": list(prefer),
                "cite_chars": sum(len(getattr(c, "text", "") or "") for c in citations),
            }
            llm_fn = wrap_compact_llm(llm_fn)

    if use_compact and prompt_fn is None:
        from augur.advisor.prompt import build_compact_knowhow_prompt
        prompt = build_compact_knowhow_prompt(query, payload, citations, lex_entries)
        concept_links = []
    else:
        prompt = (prompt_fn or build_prompt)(query, payload, citations, lex_entries)
        concept_links = []
        if prompt_fn is None and lex_entries:                    # W2:主路徑+有定義詞才接(Mode B 不套,同其餘閘)
            concept_links = _concept_links(lex_terms, scope=scope)
            prompt += _concept_block(concept_links)
        # K1 橋：有 picks 時略過（預測通道自足、免再開庫；與 picks_skip_A 同精神）
        if prompt_fn is None and not has_picks:
            prompt += _bridge_block(_bridge_links(query, None))
        # PME S4：進化塊；有 picks 時關閉（Steward picks_skip：再省 IO／檔案讀）
        if prompt_fn is None and include_evolution and not has_picks:
            from augur.philosophy.interpretation import (
                evolution_prompt_block,
                load_interpretation_markdown,
            )
            md = evolution_md if evolution_md is not None else load_interpretation_markdown()
            prompt += evolution_prompt_block(md)
    response = llm_fn(prompt)
    if use_compact:
        from augur.knowledge.compact_answer import (
            ensure_fill_kv_in_response,
            polish_compact_response,
        )
        response = polish_compact_response(response)
        # D-FillAuto：弱模型常只寫「改 wsj02」→ 機器閘從凍引文注入欄位=值
        response = ensure_fill_kv_in_response(response, query, citations)
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
    auto_lift_out = _maybe_wire_auto_lift(
        query=query,
        response=response,
        citations=citations,
        verdict=verdict,
        prompt_fn=prompt_fn,
        has_picks=has_picks,
        auto_lift=auto_lift,
    )
    out = {"response": response, "guard": verdict,
           "citations": citations, "lex_entries": lex_entries, "prompt": prompt,
           "concept_links": concept_links, "picks_ground_truth": bool(has_picks)}
    if auto_lift_out is not None:
        out["auto_lift"] = auto_lift_out
    if readout_meta is not None:
        out["readout"] = readout_meta
    if compact_meta is not None:
        out["compact"] = compact_meta
    return out


def _maybe_wire_auto_lift(*, query, response, citations, verdict, prompt_fn, has_picks, auto_lift):
    """wire-advise：旗開＋guard 過＋item 引文 → R-hybrid 抬層。fail-soft。"""
    from augur.knowledge.answer_auto_lift import (
        auto_lift_enabled, item_ids_from_citations, maybe_auto_lift_after_answer,
    )
    if not auto_lift_enabled(auto_lift):
        return None
    if not (verdict or {}).get("pass"):
        return {"ok": True, "skipped": "guard_fail"}
    if prompt_fn is not None or has_picks:
        return {"ok": True, "skipped": "mode_b_or_picks"}
    if not item_ids_from_citations(citations or ()):
        return {"ok": True, "skipped": "no_item_citations"}
    try:
        from augur.core import db as _db
        with _db.connect() as _conn, _conn.cursor() as _cur:
            out = maybe_auto_lift_after_answer(
                _cur,
                query=query or "",
                answer=response or "",
                citations=citations,
                apply=True,
            )
            _conn.commit()
            return out
    except Exception as e:  # noqa: BLE001 — 抬層不得炸主答
        return {"ok": False, "error": str(e), "skipped": "exception"}


def _selftest():
    """自測（零 DB/零 API #29a）：合成資料紅綠測確定性排版函式——picks 表 ground-truth 渲染
    (score 4dp/空 picks 回空)、概念/橋參考塊之免責硬綁與「不得複述數值」註記（回歸鎖:命門免責不可漏）。"""
    from types import SimpleNamespace as NS
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # _render_picks_table：picks=payload ground truth、score 4dp 對齊 guard 白名單口徑
    chk("空 picks→空字串(不落誠實-decline外之雜訊)", _render_picks_table(NS(picks=[])) == "")
    p = NS(rank=1, symbol="2330", name="台積電", score=0.1234)
    tbl = _render_picks_table(NS(picks=[p], probs=(), as_of="2026-05-31", model="F3",
                                 horizon=20, prob_note=""))
    chk("picks 表含 symbol/4dp score/top N", "2330" in tbl and "0.1234" in tbl and "top 1" in tbl)

    # _concept_block / _bridge_block：空→空;非空→免責與「不得複述數值」硬綁(命門)
    chk("_concept_block 空→空", _concept_block([]) == "")
    cb = _concept_block([{"a": "知行合一", "b": "格物", "npmi": 0.42, "basis_n": 7, "n_evidence": 3}])
    chk("概念塊含 npmi 2dp+不得複述數值", "0.42" in cb and "不得複述本段數值" in cb)
    chk("_bridge_block 空→空", _bridge_block([]) == "")
    bb = _bridge_block([{"field": "d.c", "terms": [{"t": "護城河", "npmi": 0.55, "n": 9, "corpus": "items"}]}])
    chk("橋塊含 npmi+非資料值相關免責+不得複述", "0.55" in bb
        and "非該欄位資料數值與報酬之相關" in bb and "不得複述本段數值" in bb)

    # PME S4：evolution 塊純函式語意（零 DB／零 advise 全路徑——全路徑含 _bridge_links 會開庫）
    from augur.philosophy.interpretation import evolution_prompt_block
    eblock = evolution_prompt_block("## PME S4\n> ≠可交易")
    chk("S4 evolution_prompt_block 含禁確立語境", "確立級" in eblock and "≠可交易" in eblock)
    chk("S4 空 md 不注入", evolution_prompt_block("") == "")
    # 模擬 advise 主路徑附加條件（prompt_fn is None ∧ include_evolution）
    def _maybe_append(prompt, *, prompt_fn, include_evolution, evolution_md):
        if prompt_fn is None and include_evolution:
            return prompt + evolution_prompt_block(evolution_md)
        return prompt
    base = "PROMPT"
    chk("S4 條件注入", "PME S4" in _maybe_append(base, prompt_fn=None, include_evolution=True,
                                                  evolution_md="## PME S4\n> ≠可交易"))
    chk("S4 include_evolution=False", "PME S4" not in _maybe_append(
        base, prompt_fn=None, include_evolution=False, evolution_md="## PME S4"))
    chk("S4 Mode B(prompt_fn) 不注入", "PME S4" not in _maybe_append(
        base, prompt_fn=lambda *a: "", include_evolution=True, evolution_md="## PME S4"))

    # picks_skip_A：有 picks → retrieve 絆線不得被呼叫；evolution 不注入（#35 下游絆線）
    from augur.advisor.payload import PredictionPayload, StockPick
    hit = []

    def boom_retrieve(*_a, **_k):
        hit.append(1)
        raise AssertionError("retrieve must not run when picks present")

    pl = PredictionPayload(
        as_of="2026-05-31", horizon=20, model="T",
        picks=(StockPick("2330", 1, 0.5874, "ref", "台積電"),),
        validation={"note": "t"},
        probs=(("2330", 20, 0.5874, "dead", 29),),
        prob_note="相對機率 disclaimer",
    )
    out = advise(
        "2330個股未來30天走勢?", pl,
        llm_fn=lambda _p: "說明:相對機率 0.5874，非可交易確立級。",
        retrieve_fn=boom_retrieve,
        include_evolution=True,
        evolution_md="## PME S4\n> ≠可交易",
    )
    chk("picks→retrieve 零呼叫(絆線)", hit == [])
    chk("picks→citations 空", out["citations"] == [])
    chk("picks→prompt 無 evolution", "PME S4" not in (out.get("prompt") or ""))
    chk("picks→response 含確定性表", "2330" in out["response"] and "0.5874" in out["response"])

    hit2 = []

    def count_retrieve(*_a, **_k):
        hit2.append(1)
        return []

    advise("什麼是知行合一", empty_payload(),
           llm_fn=lambda _p: "x", retrieve_fn=count_retrieve)
    chk("無 picks→仍呼叫 retrieve", len(hit2) >= 1)

    # wire-advise：預設旗關 → 主路徑不附 auto_lift 鍵；explicit False 同；不開庫
    from augur.knowledge.answer_auto_lift import auto_lift_enabled
    chk("AUTO-LIFT 旗預設關", auto_lift_enabled() is False)
    out_off = advise(
        "什麼是知行合一", empty_payload(),
        llm_fn=lambda _p: "知識庫中無可靠原文佐證此題。",
        retrieve_fn=lambda *_a, **_k: [],
        auto_lift=False,
    )
    chk("旗關無 auto_lift 鍵", "auto_lift" not in out_off)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.advise --selftest;免 DB 免 API)")
