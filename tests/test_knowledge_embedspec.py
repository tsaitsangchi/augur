"""knowledge/embedspec 純函數回歸測試(不打 API、不依賴 DB)。

🎯 嵌入世代 SSOT 的機械保證:slug 確定性(同輸入必同輸出)、collection/同步鍵命名釘死
   (現行世代值 pin 為字面常數——SSOT 一改,測試逼人有意識同步)、封閉集/長度預算 fail loud。
守 #15(確定性)· #12(單一住所:命名只出自 embedspec)· e2e 計畫 §3-S6(禁手寫縮寫)。
"""
import re

import pytest

from augur.knowledge import embedspec


def test_slug_deterministic_and_pinned():
    a = embedspec.model_slug("intfloat/multilingual-e5-small")
    b = embedspec.model_slug("intfloat/multilingual-e5-small")
    assert a == b == "ime5s30b1cd"          # pin 現行世代;換模=有意識更新
    assert embedspec.model_slug() == a       # 預設=MODEL_TAG


def test_slug_format_and_distinct():
    for tag in ("intfloat/multilingual-e5-small", "BAAI/bge-m3", "openai/text-embedding-3-small"):
        s = embedspec.model_slug(tag)
        assert re.fullmatch(r"[a-z0-9]+", s) and len(s) <= 11
    assert embedspec.model_slug("BAAI/bge-m3") != embedspec.model_slug("intfloat/multilingual-e5-small")
    with pytest.raises(ValueError):
        embedspec.model_slug("///")


def test_collection_name_pinned_and_budget():
    assert embedspec.collection_name("sentence", "items") == "kn_sent_it_ime5s30b1cd_tn1"
    assert embedspec.collection_name("sentence", "works") == "kn_sent_wk_ime5s30b1cd_tn1"
    assert embedspec.collection_name("lexicon", "works") == "kn_lex_wk_ime5s30b1cd_tn1"
    for name in (embedspec.collection_name(la, si) for la in ("sentence", "lexicon")
                 for si in ("works", "items")):
        assert re.fullmatch(r"[a-z][a-z0-9_]*", name) and len(name) <= 26


def test_collection_name_closed_sets():
    with pytest.raises(ValueError):
        embedspec.collection_name("chunk", "items")
    with pytest.raises(ValueError):
        embedspec.collection_name("sentence", "corpus")


def test_dim_for_fail_closed():
    assert embedspec.dim_for() == 384
    assert embedspec.dim_for("intfloat/multilingual-e5-small") == 384
    with pytest.raises(KeyError):
        embedspec.dim_for("unregistered/model")


def test_sync_scope_budget():
    key = embedspec.sync_scope(embedspec.collection_name("sentence", "items"), "en")
    assert key == "mv_kn_sent_it_ime5s30b1cd_tn1_en" and len(key) <= 32
    with pytest.raises(ValueError):
        embedspec.sync_scope(embedspec.collection_name("sentence", "items"), "zh-hant")
