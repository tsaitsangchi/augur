"""advisor/guard.py 純函數回歸測試(不打 API、不依賴 DB;clean-room)。

🎯 防幻覺機械閘的機械保證:guard 四閘(引文逐字/數字白名單/未來洩漏/逆向翻轉)
   + guard_empty_retrieval(檢索空固定誠實句)+ guard_definition(定義 locator 課責)
   正反例全覆蓋,防 regex/集合比對回歸靜默放行(稽核 執13)。
   數字閘之整數/1 位小數邊界屬 執5 待修判準、此處不鎖定。
   P8 接線級(已拍板 2026-07-04):advise() 對 KnowledgePayload 分派 guard_knowledge
   (雙源=payload.numbers() ∪ 檢索真兆數字集)+殼 mock 端到端(guard_knowledge 單閘級
   正反例在 test_advisor_dialogue.py,此處不重複)。
守 #1(引文/數字不編)· #8(anti-leakage)· #15(誠實率 100% 機制非自律)。
"""
from dataclasses import dataclass

from augur.advisor.guard import (
    NO_KNOWLEDGE_RESPONSE,
    guard,
    guard_definition,
    guard_empty_retrieval,
)
from augur.advisor.payload import KnowledgePayload, example_payload


@dataclass
class _Cite:  # 最小 citation 替身(guard 僅用 .text,duck typing;免 import retrieval 之 DB 依賴)
    text: str


@dataclass
class _Lex:   # 最小 LexEntry 替身(guard 僅用 .term/.definition/.source_locator)
    term: str
    definition: str
    source_locator: str


_QUOTE = "行情總在絕望中誕生,在半信半疑中成長,在憧憬中成熟"
_CITES = [_Cite(text=f"約翰·坦伯頓說過:{_QUOTE},在充滿希望中毀滅。")]
_PAYLOAD = example_payload()


# ── 閘 ①:引文逐字(#1) ──
def test_quote_verbatim_in_citation_passes():
    verdict = guard(f"如引文所言「{_QUOTE}」,當前位階值得留意。", _PAYLOAD, _CITES)
    assert verdict["pass"] and verdict["issues"] == []

def test_quote_fabricated_or_polished_blocked():
    verdict = guard("大師說「市場永遠獎勵最有耐心的那一群人」。", _PAYLOAD, _CITES)
    assert not verdict["pass"]
    assert any("引文" in i for i in verdict["issues"])

def test_quote_shorter_than_8_chars_not_gated():
    # <8 字引號(如強調詞)不課逐字義務
    verdict = guard("所謂「安全邊際」是核心概念。", _PAYLOAD, _CITES)
    assert verdict["pass"]


# ── 閘 ②:數字 ∈ payload 白名單(#1) ──
def test_payload_numbers_pass():
    verdict = guard("#1 2330 score 0.87;驗證 rank_ic 0.1418、Sharpe 1.26。", _PAYLOAD, _CITES)
    assert verdict["pass"] and verdict["issues"] == []

def test_fabricated_decimal_number_blocked():
    verdict = guard("模型給 2330 的 score 高達 0.9999。", _PAYLOAD, _CITES)
    assert not verdict["pass"]
    assert any("數字" in i for i in verdict["issues"])


# ── 閘 ③:未來/保證語(#8) ──
def test_future_leak_blocked():
    for bad in ("這檔保證獲利。", "明天會漲,放心。", "下週必漲。", "TSMC will rise sharply."):
        verdict = guard(bad, _PAYLOAD, _CITES)
        assert not verdict["pass"], bad
        assert any("#8" in i for i in verdict["issues"]), bad

def test_neutral_cycle_language_passes():
    verdict = guard("動能訊號偏強,但週期位階偏高,屬需留意的風險視角。", _PAYLOAD, _CITES)
    assert verdict["pass"]


# ── 閘 ④:逆向翻轉(審查 C-1) ──
def test_reverse_action_blocked():
    for bad in ("群眾過熱,所以應該賣出。", "建議放空這檔。", "Contrarian view: sell instead."):
        verdict = guard(bad, _PAYLOAD, _CITES)
        assert not verdict["pass"], bad
        assert any("逆向" in i for i in verdict["issues"]), bad

def test_contrarian_risk_view_without_reversal_passes():
    verdict = guard("逆向鏡提醒:群眾情緒過熱是風險位階,但這只是視角、不是行動建議。", _PAYLOAD, _CITES)
    assert verdict["pass"]


# ── guard_empty_retrieval:檢索空固定誠實句(#15) ──
def test_empty_retrieval_fixed_honest_response_passes():
    verdict = guard_empty_retrieval(f"  {NO_KNOWLEDGE_RESPONSE}  ", [])
    assert verdict["pass"] and verdict["issues"] == []

def test_empty_retrieval_improvised_answer_blocked():
    verdict = guard_empty_retrieval("我記得葛拉漢大概是這麼說的……", [])
    assert not verdict["pass"]
    assert any(NO_KNOWLEDGE_RESPONSE in i for i in verdict["issues"])

def test_nonempty_retrieval_not_gated():
    verdict = guard_empty_retrieval("任意正常回覆。", _CITES)
    assert verdict["pass"]


# ── guard_definition:定義引用必附 source_locator(#1 可溯源) ──
_DEF = "安全邊際指買入價格顯著低於內在價值之差額保護"

def test_definition_cited_with_locator_passes():
    e = _Lex(term="安全邊際", definition=_DEF, source_locator="《智慧型股票投資人》第20章")
    verdict = guard_definition(f"{_DEF}(見{e.source_locator})。", [e])
    assert verdict["pass"] and verdict["issues"] == []

def test_definition_cited_locator_missing_from_response_blocked():
    e = _Lex(term="安全邊際", definition=_DEF, source_locator="《智慧型股票投資人》第20章")
    verdict = guard_definition(f"{_DEF}。", [e])
    assert not verdict["pass"]
    assert any("source_locator" in i and "安全邊際" in i for i in verdict["issues"])

def test_definition_cited_entry_without_locator_blocked():
    e = _Lex(term="安全邊際", definition=_DEF, source_locator="")
    verdict = guard_definition(f"{_DEF}。", [e])
    assert not verdict["pass"]
    assert any("無 source_locator" in i for i in verdict["issues"])

def test_definition_not_cited_no_locator_obligation():
    e = _Lex(term="安全邊際", definition=_DEF, source_locator="")
    verdict = guard_definition("這題與該定義無關,只談週期位階。", [e])
    assert verdict["pass"]

def test_definition_frag_under_8_chars_not_gated():
    e = _Lex(term="套利", definition="低買高賣", source_locator="")
    verdict = guard_definition("低買高賣即為套利。", [e])
    assert verdict["pass"]

def test_definition_empty_entries_delegates_to_empty_retrieval():
    assert guard_definition(NO_KNOWLEDGE_RESPONSE, [])["pass"]
    assert not guard_definition("憑印象補一段定義。", [])["pass"]


# ── P8 接線(已拍板 2026-07-04):advise() 對 KnowledgePayload 分派 guard_knowledge ──
@dataclass
class _KCite:  # 知識側 citation 替身(build_prompt 需 work_title/thinker/chapter/source_url)
    text: str
    work_title: str = "《測試文獻》"
    thinker: str = "測試作者"
    chapter: str = "ch1"
    source_url: str = "http://example.org"


_KPAYLOAD = KnowledgePayload(as_of="2026-07-04", domain="chemistry", sql_numbers=frozenset({3160.0}))
_KCITES = [_KCite(text="the molar mass was measured as 114.32 g/mol; staging holds 3160 rows.")]


def _kadvise(monkeypatch, llm_text, cites=None):
    import augur.philosophy.retrieval as retr
    from augur.advisor.advise import advise
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)   # DB 他證另有 M2 測;此處鎖接線分派
    return advise("化學提問", _KPAYLOAD, lambda p: llm_text,
                  retrieve_fn=lambda q, k: list(_KCITES if cites is None else cites))


def test_p8_domain_numbers_dual_source_pass(monkeypatch):
    # 域數字過:3160.00 ∈ payload.numbers()、114.32 ∈ 檢索真兆數字集(雙源、round 口徑一致)
    out = _kadvise(monkeypatch, "staging 共 3160.00 列;文獻量測分子量 114.32 g/mol。")
    assert out["guard"]["pass"], out["guard"]["issues"]


def test_p8_fabricated_number_blocked(monkeypatch):
    # 編造攔:999.99 不在雙源任一側 → 機械攔截(非自律)
    out = _kadvise(monkeypatch, "由此推得分子量為 999.99 g/mol。")
    assert not out["guard"]["pass"]
    assert any("雙源白名單" in i and "999.99" in i for i in out["guard"]["issues"])


def test_p8_honest_closed_set_unchanged(monkeypatch):
    # 閉集不變(P8 拍板明文):固定誠實句字面不變;知識 payload 空檢索仍直回、不經 LLM
    assert NO_KNOWLEDGE_RESPONSE == "知識庫中無此內容"
    out = _kadvise(monkeypatch, "不該被生成的回覆", cites=[])
    assert out["response"] == NO_KNOWLEDGE_RESPONSE and out["prompt"] is None


def test_p8_shell_mock_e2e_knowledge_payload(monkeypatch):
    # 殼 mock 端到端:chat_completion(payload_fn=KnowledgePayload)→advise()→guard_knowledge 同路生效
    import augur.philosophy.retrieval as retr
    from augur.advisor import oai_compat
    monkeypatch.setattr(retr, "verify_verbatim", lambda c: True)
    body = {"model": "augur-advisor", "messages": [{"role": "user", "content": "化學提問"}]}
    ok = oai_compat.chat_completion(body, llm_fn=lambda p: "文獻量測分子量 114.32 g/mol。",
                                    payload_fn=lambda: _KPAYLOAD,
                                    retrieve_fn=lambda q, k: list(_KCITES))
    assert ok["augur_guard"]["pass"] is True
    assert "[augur-guard] pass=true" in ok["choices"][0]["message"]["content"]
    bad = oai_compat.chat_completion(body, llm_fn=lambda p: "由此推得分子量為 999.99 g/mol。",
                                     payload_fn=lambda: _KPAYLOAD,
                                     retrieve_fn=lambda q, k: list(_KCITES))
    assert bad["augur_guard"]["pass"] is False
    # R2 架構(2026-07-04):guard fail 之安全不變式=LLM 杜撰內容不外洩(而非死比對誠實句字串);
    # 有檢索時揭露系統逐字原文供參(_citations_block,真兆非 LLM 產出)。
    content = bad["choices"][0]["message"]["content"]
    body_shown = content.split("[augur-guard]")[0]          # 答覆本體(機械診斷尾註前)
    assert "999.99" not in body_shown and "由此推得" not in body_shown  # 杜撰數字/文字不進本體(#1;尾註可診斷性報被攔值)
    assert NO_KNOWLEDGE_RESPONSE in content or "系統逐字附上" in content  # 誠實揭露(withhold 或原文)
