"""knowledge/vectorindex Milvus Lite adapter 煙測(單檔嵌入式、不依賴 PG/不打 API)。

🎯 五方法介面對真 Milvus Lite 檔的機械保證:建 collection/upsert 冪等/search 只回
   (pg_pk, distance)/delete 傳播/stats pk 枚舉自驗/filter 封閉集 fail loud/異維拒用/
   重開檔可續查(可拋棄索引=檔案層真持久)。
守 #15(真跑非 mock)· 紅線③(search 永不回內容)· e2e 計畫 §3-S6/§6(SOP-B)。
"""
import random

import pytest

# Milvus 為退役後端(2026-07-14 Qdrant serving 已上為生產 serving 索引);pymilvus 為 optional dep,
# 未裝時整檔 skip 非 fail(測試衛生#15;Qdrant 介面由 verify_qdrant_shadow 0.972+向量等值直測驗證)。
pytest.importorskip("pymilvus", reason="Milvus 退役後端;pymilvus 未裝→跳過其嵌入式介面煙測(Qdrant 另驗)")

from augur.knowledge.vectorindex import CollectionSpec, MilvusLiteIndex  # noqa: E402

DIM = 8


def _rows(n, seed=7):
    rnd = random.Random(seed)
    return [{"pg_pk": i + 1, "vector": [rnd.random() for _ in range(DIM)],
             "domain": "chemistry" if i % 2 else "", "entity_type": "paper" if i % 2 else "",
             "taxonomy_id": i % 3, "language": "en" if i % 2 else "zh"} for i in range(n)]


@pytest.fixture
def idx(tmp_path):
    ix = MilvusLiteIndex(tmp_path / "t.db")
    ix.ensure_collection(CollectionSpec(name="t_col", dim=DIM))
    yield ix
    ix.close()


def test_upsert_search_stats_delete(idx):
    rows = _rows(10)
    assert idx.upsert(rows) == 10
    st = idx.stats(include_pks=True)
    assert st["exists"] and st["row_count"] == 10 and st["pg_pks"] == {r["pg_pk"] for r in rows}
    hits = idx.search(rows[3]["vector"], k=3)
    assert len(hits) == 3 and hits[0][0] == rows[3]["pg_pk"]           # 自身=最近鄰
    assert all(isinstance(p, int) and isinstance(d, float) for p, d in hits)  # 只回 (pk, distance)
    en = idx.search(rows[3]["vector"], k=10, filters={"language": "en"})
    assert en and all(p % 2 == 0 for p, _ in en)                        # en 列=偶 pk(建構規則)
    assert idx.stats(filters={"language": "en"})["row_count"] == 5
    idx.delete([1, 3])
    assert idx.stats()["row_count"] == 8
    idx.upsert([rows[5]])                                               # 同 pk 重 upsert=冪等
    assert idx.stats()["row_count"] == 8


def test_filter_closed_set_fail_loud(idx):
    idx.upsert(_rows(3))
    with pytest.raises(ValueError):
        idx.search([0.0] * DIM, k=1, filters={"sentence": "x"})         # 欄不在封閉集
    with pytest.raises(ValueError):
        idx.search([0.0] * DIM, k=1, filters={"domain": 'a" or 1==1'})  # 禁引號(不注入)
    with pytest.raises(ValueError):
        idx.upsert([{"pg_pk": 99, "vector": [0.0] * DIM}])              # 缺 payload 欄


def test_dim_mismatch_and_unbound(tmp_path):
    p = tmp_path / "d.db"
    ix = MilvusLiteIndex(p)
    with pytest.raises(RuntimeError):
        ix.stats()                                                      # 未 ensure 先用=fail loud
    ix.ensure_collection(CollectionSpec(name="d_col", dim=DIM))
    ix.upsert(_rows(2))
    with pytest.raises(ValueError):
        ix.ensure_collection(CollectionSpec(name="d_col", dim=16))      # 異維=新表世代,拒覆用
    ix.close()


def test_reopen_persistence(tmp_path):
    p = tmp_path / "r.db"
    rows = _rows(5)
    with MilvusLiteIndex(p) as ix:
        ix.ensure_collection(CollectionSpec(name="r_col", dim=DIM))
        ix.upsert(rows)
    with MilvusLiteIndex(p) as ix2:                                     # 重開檔=真持久
        ix2.ensure_collection(CollectionSpec(name="r_col", dim=DIM))
        assert ix2.stats()["row_count"] == 5
        assert ix2.search(rows[0]["vector"], k=1)[0][0] == rows[0]["pg_pk"]
