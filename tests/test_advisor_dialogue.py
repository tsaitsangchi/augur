"""對話族(N5/N6/N8/M2)純函數回歸測試 — 不打 Ollama、不連 DB(verify 以 monkeypatch 替身)。

🎯 (1) N5 strip_think:<think> 段機械剝除(閉合全刪/未閉合 fail-closed 截斷);
   (2) N6 KnowledgePayload+guard_knowledge(P8 已拍板 2026-07-04,已接線 advise;接線級測在
       test_advisor_guard.py):雙源白名單/已驗引文段豁免②③/無 picks 逆向閘 no-op——正反例全覆蓋;
   (3) M2 advise 注入 retrieve_fn 一律後驗 verify_verbatim(注入不繞過);
   (4) N8 oai_compat:guard fail=固定誠實句閉集、guard verdict 機械尾註、偽 SSE 收於 [DONE]。
守 #1/#8/#15(閘為機械保證非自律)· 計畫 §3-S7/§9(R0 誠實雙向之單元級)。
"""
from dataclasses import dataclass

from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE, guard_knowledge
from augur.advisor.ollama import strip_think
from augur.advisor.payload import KnowledgePayload, example_payload
from augur.advisor import oai_compat


@dataclass
class _Cite:  # guard/prompt 僅用欄位之最小替身(duck typing,免 DB)
    text: str
    work_title: str = "《測試文獻》"
    thinker: str = "測試作者"
    chapter: str = "ch1"
    source_url: str = "http://example.org"


_KQUOTE = "the molar mass of the compound was measured as 114.32 g/mol under standard pressure"
_KCITES = [_Cite(text=f"In the original paper, {_KQUOTE}, which the authors replicated twice.")]
_KPAYLOAD = KnowledgePayload(as_of="2026-07-04", domain="chemistry", sql_numbers=frozenset({3160.0}))


# ── N5 strip_think(P8 閘鏈一環) ──
def test_strip_think_removes_closed_block():
    assert strip_think("<think>內心推理…</think>正式回答。") == "正式回答。"

def test_strip_think_removes_multiple_blocks():
    assert strip_think("<think>a</think>回答一。<think>b</think>回答二。") == "回答一。回答二。"

def test_strip_think_unclosed_truncates_fail_closed():
    assert strip_think("回答前段。<think>被截斷的思考…") == "回答前段。"

def test_strip_think_plain_text_untouched():
    assert strip_think("  純回答,無思考段。 ") == "純回答,無思考段。"


# ── N6 KnowledgePayload ──
def test_knowledge_payload_numbers_from_sql_set_only():
    p = KnowledgePayload(as_of="2026-07-04", domain="chemistry", sql_numbers=frozenset({119, 3160.0}))
    assert p.numbers() == {119.0, 3160.0}
    assert p.picks == ()

def test_knowledge_payload_frozen():
    import dataclasses
    try:
        object.__getattribute__(_KPAYLOAD, "domain")
        _KPAYLOAD.__class__(as_of="x", domain="y")  # 可建
        frozen_ok = False
        try:
            _KPAYLOAD.domain = "z"  # type: ignore[misc]
        except dataclasses.FrozenInstanceError:
            frozen_ok = True
        assert frozen_ok
    except Exception as e:  # pragma: no cover
        raise AssertionError(f"frozen 檢查失敗: {e}")


# ── N6 guard_knowledge(P8 已拍板)──
def test_gk_verified_quote_number_exempt():
    # 引文段(已過①)內數字 114.32 豁免②(文獻原文非系統宣稱)
    v = guard_knowledge(f"文獻記載「{_KQUOTE}」,此為原文轉述。", _KPAYLOAD, _KCITES)
    assert v["pass"], v["issues"]

def test_gk_number_outside_quote_blocked():
    v = guard_knowledge("由此可知分子量約為 114.32。", _KPAYLOAD, _KCITES)
    assert not v["pass"]
    assert any("雙源白名單" in i for i in v["issues"])

def test_gk_sql_numbers_second_source_allows():
    v = guard_knowledge("staging 計數為 3160.00 列。", _KPAYLOAD, _KCITES, sql_numbers=(3160.0,))
    assert v["pass"], v["issues"]

def test_gk_unverified_quote_still_blocked_and_not_exempt():
    v = guard_knowledge("文獻說「this compound weighs exactly 999.99 g/mol total」。", _KPAYLOAD, _KCITES)
    assert not v["pass"]
    assert any("引文" in i for i in v["issues"])
    assert any("999.99" in i for i in v["issues"])  # 未過① → 不豁免②

def test_gk_future_leak_inside_verified_quote_exempt():
    q = "under heating the pressure will rise steadily until equilibrium"
    cites = [_Cite(text=f"As noted, {q}, per the original experiment.")]
    v = guard_knowledge(f"原文:「{q}」。", _KPAYLOAD, cites)
    assert v["pass"], v["issues"]

def test_gk_future_leak_outside_quote_blocked():
    v = guard_knowledge("因此股價 will rise 可期。", _KPAYLOAD, _KCITES)
    assert not v["pass"]
    assert any("#8" in i for i in v["issues"])

def test_gk_reverse_noop_without_picks():
    v = guard_knowledge("所以建議賣出持股。", _KPAYLOAD, _KCITES)  # 知識 payload 無 picks → ④ no-op
    assert not any("逆向" in i for i in v["issues"])

def test_gk_reverse_active_with_picks():
    v = guard_knowledge("所以建議賣出持股。", example_payload(), _KCITES)
    assert any("逆向" in i for i in v["issues"])


# ── M2 advise:注入 retrieve_fn 一律後驗 verify_verbatim ──
def _advise(monkeypatch, verify_result):
    import augur.philosophy.retrieval as retr
    from augur.advisor.advise import advise
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: verify_result)
    # 空檢索誠實分級以替身固定 level-1(免 DB sidecar;本測鎖注入後驗、非測隔離館藏旁查)
    monkeypatch.setattr("augur.advisor.answer.honesty_level", lambda q, c: (1, NO_KNOWLEDGE_RESPONSE))
    calls = {}
    def llm(prompt):
        calls["prompt"] = prompt
        return "(mock)固定回覆。"
    # query 與注入 citation 內容相關(molar mass),使 T1-a relevance gate 判為有料、走主路徑
    # (本測旨在鎖注入後驗 verify_verbatim 分派,非測 relevance;故 query 對齊 citation 主題)
    out = advise("the molar mass of the compound", example_payload(), llm,
                 retrieve_fn=lambda q, k, scope=None: list(_KCITES))
    return out, calls

def test_m2_injected_citations_pass_verify(monkeypatch):
    out, calls = _advise(monkeypatch, verify_result=True)
    assert out["citations"] == list(_KCITES) and "prompt" in calls

def test_m2_injected_citations_failing_verify_dropped_to_honest(monkeypatch):
    out, calls = _advise(monkeypatch, verify_result=False)
    assert out["citations"] == [] and out["response"] == NO_KNOWLEDGE_RESPONSE
    assert "prompt" not in calls  # 全空 → 不經 LLM(機械保證)


# ── N8 oai_compat 純層 ──
def test_models_payload_single_model():
    data = oai_compat.models_payload()["data"]
    assert [m["id"] for m in data] == [oai_compat.MODEL_ID]

def test_last_user_content_str_and_parts():
    msgs = [{"role": "system", "content": "s"},
            {"role": "user", "content": [{"type": "text", "text": "第一段"}, {"type": "text", "text": "第二段"}]}]
    assert oai_compat._last_user_content(msgs) == "第一段\n第二段"
    assert oai_compat._last_user_content([{"role": "user", "content": " hi "}]) == "hi"
    assert oai_compat._last_user_content([]) == ""

def _completion(monkeypatch, llm_text, verify_result=True):
    import augur.philosophy.retrieval as retr
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: verify_result)
    # query 對齊注入 citation 主題(molar mass)使 relevance gate 判有料、走主路徑(本測旨在 guard 分派/尾註)
    body = {"model": "augur-advisor", "messages": [{"role": "user", "content": "the molar mass of the compound"}]}
    return oai_compat.chat_completion(body, llm_fn=lambda p: llm_text,
                                      retrieve_fn=lambda q, k, scope=None: list(_KCITES))

def test_chat_completion_guard_pass_has_verdict_tail(monkeypatch):
    c = _completion(monkeypatch, "(mock)乾淨回覆,零數字零引號。")
    content = c["choices"][0]["message"]["content"]
    assert content.startswith("(mock)乾淨回覆")
    assert "[augur-guard] pass=true" in content
    assert c["augur_guard"]["pass"] is True

def test_reply_text_never_shows_public_citation_block():
    """回歸釘死(憲章 v1.30.0 顧問呈現層):guard-pass + 公版 citations 之回覆【絕不】含公版「引經據典」逐字區塊
    ——只給白話解讀(guard 內部仍以 citations 逐字校驗)。防『改對了但舊服務未重啟/日後靜默回歸』(用戶 2026-07-05
    實測 advisor 舊碼再現引經據典之教訓)。"""
    from augur.philosophy.retrieval import Citation
    cit = [Citation(1, 1, "論語", "孔子", "述而第七", 0, 10, "https://zh.wikisource.org/x", "君子坦蕩蕩", 0.9)]
    t = oai_compat._reply_text({"response": "會計是評估企業價值的工具。",
                                "guard": {"pass": True, "issues": []}, "citations": cit, "lex_entries": []})
    assert "引經據典" not in t and "系統逐字附上" not in t, "公版引經據典區塊外洩(違憲章 v1.30.0 呈現層):\n" + t
    assert "君子坦蕩蕩" not in t          # 逐字原文不外顯
    assert "會計是評估" in t              # 白話解讀保留


def test_reply_text_keeps_mode_b_attached_block():
    """Mode B 附加檔逐字區塊【保留】(用戶自帶文件助讀、非公版引經據典;v1.30.0 明文豁免)。"""
    from augur.philosophy.retrieval import AttachedCitation
    att = [AttachedCitation(text="我的財報摘要", source_text="我的財報摘要全文", work_title="f.txt", source_url="附加文件:f.txt")]
    t = oai_compat._reply_text({"response": "根據你的檔案…", "guard": {"pass": True, "issues": []},
                                "citations": att, "lex_entries": []})
    assert "你附加的文件" in t            # Mode B 區塊保留、不受公版隱藏影響


def test_query_kind_classifies():
    """題型偵測(精準度 §2.1):投資意圖/代號→analysis、純定義→definition、其餘→general(保守不誤殺)。"""
    from augur.advisor.prompt import _query_kind
    assert _query_kind("會計是什麼?") == "definition"
    assert _query_kind("PER 怎麼計算") == "definition"
    assert _query_kind("2330 該不該買?") == "analysis"
    assert _query_kind("台積電值得布局嗎") == "analysis"
    assert _query_kind("今天天氣如何") == "general"


def test_build_prompt_adapts_to_query_kind():
    """定義題 prompt 注入『不套三姿態』hint、分析題注入『投資分析題』hint(治『回答很像』)。"""
    from augur.advisor.prompt import build_prompt
    from augur.advisor.payload import empty_payload
    pdef = build_prompt("會計是什麼?", empty_payload(), [])
    assert "定義/概念題" in pdef and ("不要套三姿態" in pdef or "不要硬套" in pdef)
    pana = build_prompt("2330 該不該買?", empty_payload(), [])
    assert "投資分析題" in pana


def test_system_prompt_has_special_case_handling():
    """特殊題型段(精準度 Iter 4-5，v1.34.0):未來預測/穩賺/離題創作/投資術語 4 類處置須在 SYSTEM_PROMPT，
    且引導模型繞開 guard 觸發詞(明天漲跌/保證)以給有用誠實答——防日後靜默刪除。"""
    from augur.advisor.prompt import SYSTEM_PROMPT
    assert "特殊題型處置" in SYSTEM_PROMPT
    assert "短期" in SYSTEM_PROMPT and "無法可靠預測" in SYSTEM_PROMPT      # 未來預測題
    assert "沒有穩賺不賠" in SYSTEM_PROMPT                                  # 不可能宣稱題
    assert "超出我作為投資顧問的範圍" in SYSTEM_PROMPT                      # 離題創作直接拒
    assert "安全邊際" in SYSTEM_PROMPT                                      # 投資術語投資語境


def test_chat_completion_guard_fail_returns_fixed_honest_closed_set(monkeypatch):
    c = _completion(monkeypatch, "模型 score 高達 0.9999,保證獲利。")   # 編造數字+保證語
    content = c["choices"][0]["message"]["content"]
    body_shown = content.split("[augur-guard]")[0]                     # 答覆本體(機械尾註前)
    # R2 架構(2026-07-04):guard fail 安全不變式=LLM 杜撰內容不進本體(非死比對誠實句字串);
    # 有檢索則揭露系統逐字原文、無檢索回誠實句;尾註可診斷性報被攔值。
    assert "0.9999" not in body_shown and "保證獲利" not in body_shown  # LLM 杜撰不外洩於正文(#1)
    assert NO_KNOWLEDGE_RESPONSE in content or "系統逐字附上" in content # 誠實揭露(withhold 或原文)
    assert "[augur-guard] pass=false" in content
    assert c["augur_guard"]["pass"] is False and c["augur_guard"]["issues"]

def test_chat_completion_rejects_empty_messages():
    import pytest
    with pytest.raises(ValueError):
        oai_compat.chat_completion({"messages": []}, llm_fn=lambda p: "x")

def test_sse_events_role_first_and_done_last(monkeypatch):
    c = _completion(monkeypatch, "(mock)乾淨回覆。")
    events = [oai_compat.role_event(c["id"], c["created"])] + list(oai_compat.content_events(c, size=8))
    assert '"role": "assistant"' in events[0]
    assert events[-1] == "data: [DONE]\n\n"
    assert any('"finish_reason": "stop"' in e for e in events)
    import json as _json
    deltas = [_json.loads(e[6:]) for e in events[:-1]]                  # 去 "data: " 前綴
    text = "".join(d["choices"][0]["delta"].get("content", "") for d in deltas)
    assert "[augur-guard]" in text                                      # 尾註隨 chunk 完整送出


# ── W2b/Phase2 空檢索誠實保守白名單放行(憲章 v1.35.0)──
def test_general_safe_answerable_golden_set():
    """紅隊 golden-set(對抗審查實測反例):A 類需真實資料一律 False、B 類通識 True、
    fail-safe 偏保守。詞表增刪須過此 gate、false-positive(誤放需 citation 題)零容忍。"""
    from augur.advisor.safe_general import general_safe_answerable as f
    # A 類需真實資料/出處/模型 → 必 False(誤放=踩三敵①)
    for q in ["台積電2330的EPS是多少", "2330 該不該買", "台積電 score 多少", "這個因子 IC 多少",
              "什麼是無風險利率", "本益比怎麼算", "台積電殖利率多少", "現在通膨多少",
              "民無信不立是孔子講的嗎", "知之為知之這是論語裡的話對吧", "誰說過知足常樂",
              "巴菲特說過什麼名言", "論語裡怎麼講誠信", "《論語》在講什麼"]:
        assert f(q) is False, q
    # B 類通識(B1 定義 / B2 風險原則)→ 必 True
    for q in ["有沒有穩賺不賠的股票", "有沒有保證獲利的投資", "存不存在零風險的標的",
              "分散投資是什麼意思", "什麼是複利", "會計是什麼", "護城河是什麼意思"]:
        assert f(q) is True, q
    # 年份/金額不誤判為股號(不因誤報 A 而崩)
    assert f("1929年大蕭條是什麼") in (True, False)      # 不 crash、不因 ticker 誤殺
    assert f("") is False and f("x" * 61) is False       # 空/超長結構閘


def test_guard_attribution_backing_check():
    """出處斷言閘(第五條):空檢索任何出處斷言 fail;非空須被斷言之經典有 citation 佐證,
    否則 fail(R2 錯章捏造);現代歸屬不擋(已接受殘餘);有佐證放行。"""
    from augur.advisor.guard import guard_attribution as g
    lunyu = [_Cite(text="君子務本 本立而道生", work_title="論語")]
    augus = [_Cite(text="奧古斯丁論盲導盲", work_title="懺悔錄")]
    assert g("民無信不立出自論語顏淵篇。", [])["pass"] is False           # 空:裸出處
    assert g("民無信不立確實出自《論語·為政》。", augus)["pass"] is False  # 非空但無佐證=R2
    assert g("正如《論語》所說君子務本。", lunyu)["pass"] is True         # 真引論語→佐證
    assert g("這見於孟子公孫丑篇。", lunyu)["pass"] is False              # 斷言孟子卻只引論語
    assert g("安全邊際源自格雷厄姆的價值投資。", augus)["pass"] is True   # 現代歸屬不擋
    assert g("沒有穩賺不賠的股票,都有風險。", [])["pass"] is True         # 乾淨無斷言


def test_advise_empty_retrieval_whitelist_routing(monkeypatch):
    """空檢索路由(v1.35.0):B 放行→呼叫 LLM 回通識;A 回退→不呼叫 LLM 回固定句;
    放行但 LLM 捏造出處→出處閘 fail-closed 退固定句(誠實下限=現行)。honesty_level 以替身免 DB。"""
    from augur.advisor.advise import advise
    from augur.advisor.payload import empty_payload
    monkeypatch.setattr("augur.advisor.answer.honesty_level",
                        lambda q, c: (1, NO_KNOWLEDGE_RESPONSE))         # 強制 level-1、免 DB sidecar
    empty_ret = lambda q, k=6, scope=None: []
    calls = []
    def llm(p): calls.append(p); return "沒有穩賺不賠的股票,任何投資都有風險。"
    r = advise("有沒有穩賺不賠的股票", empty_payload(), llm, retrieve_fn=empty_ret, scope=None)
    assert calls and r["response"].startswith("沒有穩賺不賠") and r["guard"]["pass"]   # B2 放行
    calls.clear()
    r2 = advise("台積電2330的EPS是多少", empty_payload(), llm, retrieve_fn=empty_ret, scope=None)
    assert not calls and r2["response"] == NO_KNOWLEDGE_RESPONSE                        # A 回退、零 LLM
    r3 = advise("有沒有穩賺不賠的股票", empty_payload(),
                lambda p: "沒有穩賺不賠,正如《論語》所說。", retrieve_fn=empty_ret, scope=None)
    assert r3["response"] == NO_KNOWLEDGE_RESPONSE                                      # 放行但捏造出處→fail-closed


def test_is_low_content_junk_filter():
    """B-1 junk 濾(檢索相關度收尾):符號/空白 junk chunk 判 low_content、真引文不誤殺
    (量測結論:cosine 門檻不可行故不設分數閘,唯 junk 為門檻外安全確定子集)。"""
    from augur.philosophy.retrieval import is_low_content
    for junk in ["--", "’”", "6\n\n", "   ", "···", "。。。"]:
        assert is_low_content(junk) is True, junk
    for real in ["君子敬而無失，與人恭而有禮；四海之內，皆兄弟也。",
                 "And he was right. I sometimes think that speculation must be",
                 "沒有穩賺不賠的股票,任何投資都有風險。"]:
        assert is_low_content(real) is False, real


def test_advise_whitelist_ignores_irrelevant_citations(monkeypatch):
    """B-1 收尾:通識/B2 題即使檢索到(量測證實多不相關之非-junk)citations,仍走乾淨通識路、
    忽略之(citations=[])——避免不相關 citation 令 LLM 非決定性答壞(穩賺不賠撈到王充/韓非子之實證)。"""
    from augur.advisor.advise import advise
    from augur.advisor.payload import empty_payload
    monkeypatch.setattr("augur.advisor.answer.honesty_level", lambda q, c: (1, NO_KNOWLEDGE_RESPONSE))
    import augur.philosophy.retrieval as retr
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)
    irrelevant = [_Cite(text="王充論衡:世俗見人節行高則曰賢哲如此何不貴見人謀慮深", work_title="論衡")]
    calls = []
    def llm(p): calls.append(p); return "沒有穩賺不賠的股票,任何投資都有風險。"
    r = advise("有沒有穩賺不賠的股票", empty_payload(), llm,
               retrieve_fn=lambda q, k=6, scope=None: list(irrelevant), scope=(True, frozenset(), None))
    assert calls and r["response"].startswith("沒有穩賺不賠")   # 走通識路(非主路徑)
    assert r["citations"] == []                                  # 不相關 citation 被忽略、不進答案


# ── T1-a 檢索相關度閘(out-of-corpus 誠實 decline;MBB 失敗根因修)──
def test_relevance_signal_separates_off_topic_from_classical():
    """relevance 內容詞重疊信號:離題(MBB/太陽能/半導體)遠低於閾值、經典真題遠高於閾值。
    純機械零 usage;本機語料實測校準值見 relevance.RELEVANCE_FLOOR。"""
    from augur.advisor.relevance import best_overlap, query_relevant, RELEVANCE_FLOOR
    from dataclasses import dataclass
    @dataclass
    class C:
        text: str; work_title: str = ""; thinker: str = ""
    # 離題:query 內容詞與王陽明原文幾無重疊(虛字已剔)→ 低於地板 → 不相關
    mbb_cites = [C(text="無善無惡心之體 有善有惡意之動 知善知惡是良知", work_title="王陽明全集", thinker="王陽明")]
    assert best_overlap("多主柵MBB的核心技術優勢是什麼", mbb_cites) < RELEVANCE_FLOOR
    assert query_relevant("多主柵MBB的核心技術優勢是什麼", mbb_cites) is False
    # 經典真題:query「知行合一」與王陽明原文高度重疊 → 高於地板 → 相關
    zx_cites = [C(text="知是行之始 行是知之成 知行合一 聖學只一個功夫", work_title="王陽明全集", thinker="王陽明")]
    assert best_overlap("王陽明的知行合一是什麼", zx_cites) >= RELEVANCE_FLOOR
    assert query_relevant("王陽明的知行合一是什麼", zx_cites) is True
    # 空 citations → 不相關(交既有空檢索路)
    assert query_relevant("任何問題", []) is False


def test_advise_off_topic_citations_route_to_honest_decline(monkeypatch):
    """T1-a 核心(MBB 修):非白名單題檢索到高分但**不相關**的 citations(e5-small 硬回離題經典)→
    relevance gate 判實質空 → 走 honesty_level([]) 誠實 decline、**不餵 LLM**(快、不需 qwen3 生成)。
    這是 MBB「自信講錯」的根因修:離題 context 不再偽裝成有料。"""
    from augur.advisor.advise import advise
    from augur.advisor.payload import empty_payload
    monkeypatch.setattr("augur.advisor.answer.honesty_level", lambda q, c: (1, NO_KNOWLEDGE_RESPONSE))
    import augur.philosophy.retrieval as retr
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)
    # MBB 撈到離題王陽明(實測 cosine ~0.84 但內容詞不相關);query 非 B 概念白名單
    off_topic = [_Cite(text="無善無惡心之體 有善有惡意之動 知善知惡是良知 為善去惡是格物", work_title="王陽明全集")]
    calls = []
    def llm(p): calls.append(p); return "MBB 是通信領域的多主控單元協調技術……"   # 若被呼叫即 confabulate
    r = advise("多主柵MBB/SMBB的核心技術優勢是什麼", empty_payload(), llm,
               retrieve_fn=lambda q, k=6, scope=None: list(off_topic), scope=(True, frozenset(), None))
    assert not calls                                   # 誠實 decline 在 LLM 前觸發、零 qwen3(快)
    assert r["response"] == NO_KNOWLEDGE_RESPONSE       # 回固定誠實句(非 confabulate)
    assert r["citations"] == []                         # 離題 citation 不進答案


def test_advise_relevant_citations_reach_main_path(monkeypatch):
    """T1-a 不誤傷 in-corpus:非白名單題檢索到**相關** citations(內容詞重疊 ≥ 地板)→ 照舊走主路徑餵 LLM。
    防「什麼都 decline 的假誠實」(計畫雙向誠實約束:in-corpus 真題敢據真兆答)。"""
    from augur.advisor.advise import advise
    from augur.advisor.payload import empty_payload
    import augur.philosophy.retrieval as retr
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)
    relevant = [_Cite(text="知是行之始 行是知之成 知行合一 聖學只一個功夫 更無二", work_title="王陽明全集")]
    calls = []
    def llm(p): calls.append(p); return "知行合一講的是認知與實踐本為一體。"
    r = advise("王陽明的知行合一是什麼", empty_payload(), llm,
               retrieve_fn=lambda q, k=6, scope=None: list(relevant), scope=(True, frozenset(), None))
    assert calls                                        # 相關 → 走主路徑、餵 LLM
    assert r["citations"] == relevant                   # 相關 citation 保留


def test_advise_mode_b_attached_bypasses_relevance_gate(monkeypatch):
    """Mode B 附加檔(prompt_fn 覆寫)不套 relevance gate:附檔是用戶自帶語料、相關性由用戶負責、非 augur
    庫外題;gate 只治 augur 語料檢索之離題偽 context。"""
    from augur.advisor.advise import advise
    from augur.advisor.payload import KnowledgePayload
    from augur.advisor.prompt import build_attached_prompt
    import augur.philosophy.retrieval as retr
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)
    # 附檔 citation 與 query 內容詞可低重疊,但 Mode B 不套 gate → 仍走主路徑
    att = [_Cite(text="the molar mass was measured as 114.32 g/mol", work_title="附檔")]
    calls = []
    def llm(p): calls.append(p); return "根據你的檔案第 1 段……"
    r = advise("這份文件講什麼", KnowledgePayload(as_of="attached", domain="attached"), llm,
               retrieve_fn=lambda q, k=6, scope=None: list(att),
               prompt_fn=build_attached_prompt, scope=(True, frozenset(), None))
    assert calls and r["citations"] == att              # Mode B 繞過 gate、citation 保留
