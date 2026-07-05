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
    calls = {}
    def llm(prompt):
        calls["prompt"] = prompt
        return "(mock)固定回覆。"
    out = advise("test query", example_payload(), llm,
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
    body = {"model": "augur-advisor", "messages": [{"role": "user", "content": "問題"}]}
    return oai_compat.chat_completion(body, llm_fn=lambda p: llm_text,
                                      retrieve_fn=lambda q, k, scope=None: list(_KCITES))

def test_chat_completion_guard_pass_has_verdict_tail(monkeypatch):
    c = _completion(monkeypatch, "(mock)乾淨回覆,零數字零引號。")
    content = c["choices"][0]["message"]["content"]
    assert content.startswith("(mock)乾淨回覆")
    assert "[augur-guard] pass=true" in content
    assert c["augur_guard"]["pass"] is True

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
