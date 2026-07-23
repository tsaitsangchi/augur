"""向量 serving 索引 — pgvector(SSOT)之可拋棄外部索引唯一抽象+Milvus Lite / Qdrant adapter。

🎯 這支在做什麼(白話):S6 serving 索引的五方法封閉介面(計畫 §3-S6:ensure_collection/
   upsert/delete/search/stats),search 只回 (pg_pk, distance)、內容永遠回 PG JOIN 取
   ——嵌入=索引非內容(紅線③),Milvus 隨時可 DROP 從 PG 全量重建(SOP-B);
   換 Standalone/他牌=另寫 adapter 換裝,pgvector 及以上零改動。payload=pg_pk+窄 scalar
   (domain/entity_type/taxonomy_id/language),partition key=language;缺值哨兵=''/0(誠實標注非猜值)。
守 #12(單一抽象住所)· #15(pk 枚舉自驗 len==row_count,Lite query_iterator 重複回列實證棄用
   2026-07-04)· #18(領域名詞)· 紅線③ · e2e 計畫 §3-S6/§6(SOP-B 可拋棄性)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.vectorindex              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.vectorindex --selftest   # 純紅綠自測（零 IO）
"""
from dataclasses import dataclass

# payload scalar 封閉集(計畫 §3-S6;統計表任何欄不餵向量、不進 payload)
PAYLOAD_FIELDS = ("domain", "entity_type", "taxonomy_id", "language")
ROW_FIELDS = ("pg_pk", "vector") + PAYLOAD_FIELDS
_ENUM_FILTER = "pg_pk >= 0"     # PG serial pk 恆正,此述詞=全枚舉


@dataclass(frozen=True)
class CollectionSpec:
    """一個 collection 的世代規格;name 一律出自 embedspec.collection_name(禁手寫)。"""
    name: str
    dim: int
    metric: str = "COSINE"


class VectorIndex:
    """五方法封閉介面(計畫 §3-S6);rebuild 摺疊於 ensure_collection、不另開方法。"""

    def ensure_collection(self, spec, rebuild=False):
        """建立(或沿用)collection;rebuild=True 先 DROP(破壞性,呼叫端須明示)。"""
        raise NotImplementedError

    def upsert(self, rows):
        """rows=[{pg_pk, vector, domain, entity_type, taxonomy_id, language}];by pg_pk 冪等。回筆數。"""
        raise NotImplementedError

    def delete(self, pg_pks):
        """按 pg_pk 刪除(orphan 刪除傳播用)。回請求筆數。"""
        raise NotImplementedError

    def search(self, vec, k, filters=None):
        """ANN 檢索;只回 [(pg_pk, distance)]——不回內容(紅線③);distance 只作排序用
        (語意隨 metric/adapter,呼叫端不得對絕對值賦義)。filters={payload欄:值} 等值封閉集。"""
        raise NotImplementedError

    def stats(self, include_pks=False, filters=None):
        """回 {'collection','exists','row_count'[,'pg_pks']};include_pks=True 供 S6 雙向 anti-join 對帳。"""
        raise NotImplementedError


class MilvusLiteIndex(VectorIndex):
    """Milvus Lite(單檔嵌入式)adapter;pymilvus 3.0 實測行為定錨 2026-07-04:
    partition key 可用、upsert/delete/search 可用、query 不受 16384 上限(枚舉一次取足+計數自驗)。"""

    def __init__(self, db_path):
        from pymilvus import MilvusClient
        self._client = MilvusClient(uri=str(db_path))
        self._spec = None

    # ── 介面五方法 ────────────────────────────────────────────────────
    def ensure_collection(self, spec, rebuild=False):
        from pymilvus import DataType
        c = self._client
        if rebuild and c.has_collection(spec.name):
            c.drop_collection(spec.name)
        if c.has_collection(spec.name):
            self._assert_dim(spec)
            c.load_collection(spec.name)   # 既存 collection 由新 client 開啟=released,須先 load
        else:
            sch = c.create_schema(auto_id=False, enable_dynamic_field=False)
            sch.add_field("pg_pk", DataType.INT64, is_primary=True)
            sch.add_field("vector", DataType.FLOAT_VECTOR, dim=spec.dim)
            sch.add_field("domain", DataType.VARCHAR, max_length=64)
            sch.add_field("entity_type", DataType.VARCHAR, max_length=32)
            sch.add_field("taxonomy_id", DataType.INT64)
            sch.add_field("language", DataType.VARCHAR, max_length=8, is_partition_key=True)
            idx = c.prepare_index_params()
            idx.add_index(field_name="vector", index_type="AUTOINDEX", metric_type=spec.metric)
            c.create_collection(spec.name, schema=sch, index_params=idx)
        self._spec = spec
        return spec.name

    def upsert(self, rows):
        name = self._require_spec().name
        n = 0
        for batch in _chunks(list(rows), 2000):
            for r in batch:
                missing = [f for f in ROW_FIELDS if f not in r]
                if missing:
                    raise ValueError(f"upsert row 缺欄 {missing}(封閉集={ROW_FIELDS})")
            n += self._client.upsert(name, batch)["upsert_count"]
        return n

    def delete(self, pg_pks):
        name = self._require_spec().name
        pks = [int(p) for p in pg_pks]
        for batch in _chunks(pks, 10000):
            self._client.delete(name, ids=batch)
        return len(pks)

    def search(self, vec, k, filters=None):
        name = self._require_spec().name
        res = self._client.search(name, data=[list(map(float, vec))], limit=int(k),
                                  filter=_filter_expr(filters), output_fields=[])
        return [(int(h.id), float(h.distance)) for h in res[0]]

    def stats(self, include_pks=False, filters=None):
        c = self._client
        spec = self._require_spec()
        out = {"collection": spec.name, "exists": c.has_collection(spec.name), "row_count": 0}
        if not out["exists"]:
            return out
        total = int(c.get_collection_stats(spec.name)["row_count"])
        out["row_count"] = total
        if include_pks or filters:
            expr = _filter_expr(filters) or _ENUM_FILTER
            rows = c.query(spec.name, filter=expr, output_fields=["pg_pk"], limit=max(total, 1))
            pks = {int(r["pg_pk"]) for r in rows}
            if not filters and len(pks) != total:
                raise RuntimeError(f"pk 枚舉自驗失敗:枚舉 {len(pks)} != row_count {total}(不得靜默對帳)")
            out["row_count"] = len(pks) if filters else total
            if include_pks:
                out["pg_pks"] = pks
        return out

    # ── plumbing(非介面語意)─────────────────────────────────────────
    def has(self, name):
        """collection 是否已存在(唯讀;供資訊模式免建檔誤創)。"""
        return bool(self._client.has_collection(name))

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def _require_spec(self):
        if self._spec is None:
            raise RuntimeError("先呼叫 ensure_collection(spec) 綁定 collection")
        return self._spec

    def _assert_dim(self, spec):
        desc = self._client.describe_collection(spec.name)
        for f in desc.get("fields", []):
            if f.get("name") == "vector":
                dim = int(f.get("params", {}).get("dim", 0))
                if dim != spec.dim:
                    raise ValueError(f"collection {spec.name} 既存維度 {dim} != spec.dim {spec.dim}"
                                     "(異維模型=新表世代,拍板 P6;不得覆用)")
                return
        raise RuntimeError(f"collection {spec.name} 無 vector 欄(非本抽象所建,拒用)")


class QdrantIndex(VectorIndex):
    """Qdrant adapter(embedded path 或 server url;GPU 時代可拋棄外部索引之第二 adapter,SOP-B)。
    介面五方法與 MilvusLiteIndex 同語意:point id=pg_pk、payload=窄 scalar 封閉集、language 等值過濾;
    search 只回 (pg_pk, score)——score 隨 metric、呼叫端不得賦絕對值義(#紅線③、與 Milvus 同契約)。
    pgvector 仍為 SSOT,本索引隨時可 DROP 從 PG 全量重建。"""

    def __init__(self, *, url=None, path=None, api_key=None):
        from qdrant_client import QdrantClient
        if bool(url) == bool(path):
            raise ValueError("QdrantIndex 須且僅須給 url(server)或 path(embedded)之一")
        self._client = QdrantClient(url=url, api_key=api_key) if url else QdrantClient(path=str(path))
        self._spec = None

    # ── 介面五方法 ────────────────────────────────────────────────────
    def ensure_collection(self, spec, rebuild=False):
        from qdrant_client.models import Distance, VectorParams
        c = self._client
        if rebuild and c.collection_exists(spec.name):
            c.delete_collection(spec.name)
        if c.collection_exists(spec.name):
            self._assert_dim(spec)
        else:
            metric = getattr(Distance, spec.metric.upper())   # "COSINE" → Distance.COSINE
            c.create_collection(spec.name, vectors_config=VectorParams(size=spec.dim, distance=metric))
        self._spec = spec
        return spec.name

    def upsert(self, rows):
        from qdrant_client.models import PointStruct
        name = self._require_spec().name
        n = 0
        for batch in _chunks(list(rows), 1000):
            pts = []
            for r in batch:
                missing = [f for f in ROW_FIELDS if f not in r]
                if missing:
                    raise ValueError(f"upsert row 缺欄 {missing}(封閉集={ROW_FIELDS})")
                pts.append(PointStruct(id=int(r["pg_pk"]), vector=list(map(float, r["vector"])),
                                       payload={f: r[f] for f in PAYLOAD_FIELDS}))
            self._client.upsert(name, points=pts, wait=True)
            n += len(pts)
        return n

    def delete(self, pg_pks):
        from qdrant_client.models import PointIdsList
        name = self._require_spec().name
        pks = [int(p) for p in pg_pks]
        for batch in _chunks(pks, 10000):
            self._client.delete(name, points_selector=PointIdsList(points=batch), wait=True)
        return len(pks)

    def search(self, vec, k, filters=None):
        name = self._require_spec().name
        from qdrant_client.models import SearchParams
        # hnsw_ef=操作值(#27;2026-07-10 影子實測:預設 ef 對 pgvector 精確參照 mean 0.858<0.90;
        # runtime 與影子同參=量測即線上行為)
        res = self._client.query_points(name, query=list(map(float, vec)), limit=int(k),
                                        query_filter=_qdrant_filter(filters),
                                        search_params=SearchParams(hnsw_ef=256),
                                        with_payload=False, with_vectors=False)
        return [(int(p.id), float(p.score)) for p in res.points]

    def stats(self, include_pks=False, filters=None):
        c = self._client
        spec = self._require_spec()
        out = {"collection": spec.name, "exists": c.collection_exists(spec.name), "row_count": 0}
        if not out["exists"]:
            return out
        flt = _qdrant_filter(filters)
        total = int(c.count(spec.name, count_filter=flt, exact=True).count)
        out["row_count"] = total
        if include_pks:
            pks, offset = set(), None
            while True:
                pts, offset = c.scroll(spec.name, scroll_filter=flt, limit=10000, offset=offset,
                                       with_payload=False, with_vectors=False)
                pks.update(int(p.id) for p in pts)
                if offset is None:
                    break
            if len(pks) != total:
                raise RuntimeError(f"pk 枚舉自驗失敗:枚舉 {len(pks)} != count {total}(不得靜默對帳)")
            out["pg_pks"] = pks
        return out

    # ── plumbing(非介面語意)─────────────────────────────────────────
    def has(self, name):
        return bool(self._client.collection_exists(name))

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def _require_spec(self):
        if self._spec is None:
            raise RuntimeError("先呼叫 ensure_collection(spec) 綁定 collection")
        return self._spec

    def _assert_dim(self, spec):
        vconf = self._client.get_collection(spec.name).config.params.vectors
        dim = int(getattr(vconf, "size", 0))   # 未命名向量=VectorParams;命名向量(dict)非本抽象所建
        if dim != spec.dim:
            raise ValueError(f"collection {spec.name} 既存維度 {dim} != spec.dim {spec.dim}"
                             "(異維模型=新表世代,拍板 P6;不得覆用)")


def _qdrant_filter(filters):
    """{payload欄:值}→Qdrant Filter(全 must 等值);欄名封閉集、值型別把關(fail loud、不注入)。
    None/空 → None(全枚舉,Qdrant 端=無過濾)。"""
    if not filters:
        return None
    from qdrant_client.models import FieldCondition, Filter, MatchValue
    conds = []
    for field, val in sorted(filters.items()):
        if field not in PAYLOAD_FIELDS:
            raise ValueError(f"filter 欄不在封閉集 {PAYLOAD_FIELDS}: {field!r}")
        if isinstance(val, bool) or not isinstance(val, (int, str)):
            raise ValueError(f"filter 值僅收 int/str: {field}={val!r}")
        conds.append(FieldCondition(key=field, match=MatchValue(value=val)))
    return Filter(must=conds)


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _filter_expr(filters):
    """{payload欄:值}→Milvus 布林式;欄名封閉集、值禁引號/反斜線(fail loud,不注入)。"""
    if not filters:
        return ""
    parts = []
    for field, val in sorted(filters.items()):
        if field not in PAYLOAD_FIELDS:
            raise ValueError(f"filter 欄不在封閉集 {PAYLOAD_FIELDS}: {field!r}")
        if isinstance(val, bool) or not isinstance(val, (int, str)):
            raise ValueError(f"filter 值僅收 int/str: {field}={val!r}")
        if isinstance(val, str):
            if '"' in val or "\\" in val:
                raise ValueError(f"filter 字串值禁引號/反斜線: {val!r}")
            parts.append(f'{field} == "{val}"')
        else:
            parts.append(f"{field} == {val}")
    return " and ".join(parts)


# ── config-driven factory(e2e 計畫 P4;憲章 v1.40.0 接縫 DB 化)──

def make_index(scope):
    """讀 knowledge_vectorstore_config 選 serving 後端(切換/退回=UPDATE 一列,#29b):
    backend='pgvector' → None(現行 SQL 內建 ANN 路=SSOT 直查);
    'qdrant_server'   → QdrantIndex(url=endpoint);'qdrant_embedded' → QdrantIndex(path=endpoint)。
    **世代機械斷言(v1.40.0)**:config.embed_model/dims 必須==embedspec 現行世代,不一致 raise
    (fail-loud 拒服務,防混世代索引靜默污染檢索)。config 缺列→None(=pgvector,保守)。"""
    from augur.core import db as _db
    from augur.knowledge import embedspec as _es
    with _db.connect() as conn, _db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowledge_vectorstore_config')")
        if not cur.fetchone()[0]:
            return None
        cur.execute("SELECT backend, endpoint, embed_model, dims, fallback "
                    "FROM knowledge_vectorstore_config WHERE scope=%s", (scope,))
        row = cur.fetchone()
    if not row:
        return None
    backend, endpoint, model, dims, _fb = row
    if backend == "pgvector":
        return None
    if model != _es.MODEL_TAG or int(dims) != _es.dim_for():
        raise RuntimeError(f"vectorstore config 世代不一致(scope={scope}):config=({model},{dims}) "
                           f"≠ embedspec=({_es.MODEL_TAG},{_es.dim_for()})——fail-loud 拒服務(v1.40.0)")
    if backend == "qdrant_server":
        return QdrantIndex(url=endpoint or "http://127.0.0.1:6333")
    if backend == "qdrant_embedded":
        return QdrantIndex(path=endpoint)
    raise RuntimeError(f"未知 backend {backend!r}")


def _selftest():
    """純紅綠自測(零 IO):純 helper 字串建構/切片 + 封閉集不變式 + 介面結構斷言;
    不觸 adapter client 建構(那才會連 Milvus/Qdrant),故無 network/DB。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    def raises(fn):
        try:
            fn(); return False
        except Exception:                                   # 純呼叫、任何拒絕即預期(零 IO)
            return True
    # _filter_expr 純字串建構(無 import、無 IO)——注入防護是最該守的性質
    chk("空 filter→空串", _filter_expr(None) == "" and _filter_expr({}) == "")
    chk("str 值加引號", _filter_expr({"language": "en"}) == 'language == "en"')
    chk("int 值不加引號", _filter_expr({"taxonomy_id": 5}) == "taxonomy_id == 5")
    chk("多欄 sorted+and",
        _filter_expr({"language": "en", "domain": "phil"}) == 'domain == "phil" and language == "en"')
    chk("欄不在封閉集→raise", raises(lambda: _filter_expr({"evil": "x"})))
    chk("bool 值→raise", raises(lambda: _filter_expr({"taxonomy_id": True})))
    chk("引號注入→raise", raises(lambda: _filter_expr({"language": 'a"b'})))
    chk("反斜線注入→raise", raises(lambda: _filter_expr({"language": "a\\b"})))
    # _qdrant_filter None→None(不觸 qdrant_client import)
    chk("_qdrant_filter None→None", _qdrant_filter(None) is None and _qdrant_filter({}) is None)
    # _chunks 純切片
    chk("_chunks 均分+尾批", list(_chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]])
    chk("_chunks 空→無批", list(_chunks([], 3)) == [])
    # 封閉集不變式(payload/row 契約)
    chk("ROW=pk+vec+payload", ROW_FIELDS == ("pg_pk", "vector") + PAYLOAD_FIELDS)
    chk("_ENUM_FILTER 全枚舉述詞", _ENUM_FILTER == "pg_pk >= 0")
    # CollectionSpec 預設 metric + frozen
    chk("CollectionSpec 預設 COSINE", CollectionSpec("c", 384).metric == "COSINE")
    chk("CollectionSpec frozen", raises(lambda: setattr(CollectionSpec("c", 384), "dim", 1)))
    # 介面五方法齊備 + adapter 繼承(結構斷言、零 IO)
    for m in ("ensure_collection", "upsert", "delete", "search", "stats"):
        chk(f"VectorIndex.{m} 存在", hasattr(VectorIndex, m))
    chk("adapter 皆繼承介面",
        issubclass(MilvusLiteIndex, VectorIndex) and issubclass(QdrantIndex, VectorIndex))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.vectorindex --selftest;免 DB 免 API)")
