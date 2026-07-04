"""W8 三級誠實分級器測試(拍板3/憲章 v1.25.0)— mock 旁查、零 DB 依賴。"""
from augur.advisor.answer import honesty_level
from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE, UNVERIFIED_ATTRIBUTION_RESPONSE, HONESTY_CLOSED_SET


def test_level3_has_citations():
    # 有真兆 citations → level 3、交既有 advise 作答(本層不介入、回 None)
    lvl, resp = honesty_level("任意問題", ["citation"])
    assert lvl == 3 and resp is None


def test_level1_empty_and_no_isolation_hit():
    # 檢索空 + 隔離館藏無命中 → level 1「知識庫中無此內容」
    lvl, resp = honesty_level("庫中確無之題", [], sidecar_fn=lambda q: [])
    assert lvl == 1 and resp == NO_KNOWLEDGE_RESPONSE


def test_level2_empty_but_isolation_hit():
    # 檢索空 + 隔離館藏命中(庫存但歸屬未驗)→ level 2 第二固定句
    lvl, resp = honesty_level("談談某未驗作品", [], sidecar_fn=lambda q: ["某未驗作品"])
    assert lvl == 2 and resp == UNVERIFIED_ATTRIBUTION_RESPONSE


def test_closed_set_only_two():
    # 閉集僅二句(憲章 v1.25.0;分級器不得產閉集外之句)
    assert HONESTY_CLOSED_SET == (NO_KNOWLEDGE_RESPONSE, UNVERIFIED_ATTRIBUTION_RESPONSE)
    for sidecar in (lambda q: [], lambda q: ["x"]):
        _lvl, resp = honesty_level("q", [], sidecar_fn=sidecar)
        assert resp in HONESTY_CLOSED_SET
