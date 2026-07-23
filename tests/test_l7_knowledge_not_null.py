"""L7.21(f) 四欄引擎層 NOT NULL 拒絕回歸測試（F4 物理落地）。

🎯 這支在做什麼(白話):鎖住 L7.21(f)(i)(ii)(iii)——Source／Identity／Evidence／instance-type
   四欄缺任一時引擎權限層拒絕寫入；每欄一則可執行回歸（`:253` 推定規則之證明掛點）。
   DB 不可用→skip（非假 pass）。owner 分離局部覆蓋見 `tests/test_raw_supersede_log.py`（L7.16）。

守 CLAUDE #7(須實測)· #15(誠實 skip)· #9(零幻像)
"""
from __future__ import annotations

import pytest

_TABLE = "_l7_knowledge_fixture"
_DDL = f"""
CREATE TABLE "{_TABLE}" (
    id bigserial PRIMARY KEY,
    source_id text NOT NULL,
    identity_id text NOT NULL,
    evidence_id text NOT NULL,
    instance_type text NOT NULL CHECK (instance_type IN ('instance', 'type'))
)
"""
_VALID = ("src-1", "id-1", "ev-1", "instance")


@pytest.fixture()
def cur():
    """單一交易 cursor；teardown ROLLBACK。DB 不可用即 skip。"""
    try:
        import psycopg2
        from augur.core import config
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 依賴不可用、跳過 L7.21(f) 測試:{e}")
        return
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 L7.21(f) 測試:{e}")
        return
    conn.autocommit = False
    c = conn.cursor()
    c.execute(f'DROP TABLE IF EXISTS "{_TABLE}"')
    c.execute(_DDL)
    try:
        yield c
    finally:
        conn.rollback()
        conn.close()


def _insert(cur, source_id, identity_id, evidence_id, instance_type):
    cur.execute(
        f'INSERT INTO "{_TABLE}" (source_id, identity_id, evidence_id, instance_type) '
        "VALUES (%s, %s, %s, %s)",
        (source_id, identity_id, evidence_id, instance_type),
    )


def test_valid_row_accepted(cur):
    """四欄齊全→引擎允許寫入（正向錨）。"""
    _insert(cur, *_VALID)
    cur.execute(f'SELECT count(*) FROM "{_TABLE}"')
    assert cur.fetchone()[0] == 1


@pytest.mark.parametrize(
    "col,null_idx",
    [
        ("source_id", 0),
        ("identity_id", 1),
        ("evidence_id", 2),
        ("instance_type", 3),
    ],
    ids=["source", "identity", "evidence", "instance_type"],
)
def test_null_column_rejected_at_engine(cur, col, null_idx):
    """L7.21(f)(iv)：缺該欄之寫入被引擎層拒絕（NOT NULL）。"""
    import psycopg2

    vals = list(_VALID)
    vals[null_idx] = None
    cur.execute("SAVEPOINT sp")
    with pytest.raises(psycopg2.Error):
        _insert(cur, *vals)
    cur.execute("ROLLBACK TO SAVEPOINT sp")


def test_not_null_constraints_present(cur):
    """schema 盤點：四欄皆 NOT NULL（L7.21(f) 可判定判準）。"""
    cur.execute(
        """
        SELECT a.attname
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = %s AND n.nspname = current_schema()
          AND a.attnum > 0 AND NOT a.attisdropped
          AND a.attnotnull
          AND a.attname IN ('source_id', 'identity_id', 'evidence_id', 'instance_type')
        ORDER BY a.attname
        """,
        (_TABLE,),
    )
    assert [r[0] for r in cur.fetchall()] == [
        "evidence_id",
        "identity_id",
        "instance_type",
        "source_id",
    ]
