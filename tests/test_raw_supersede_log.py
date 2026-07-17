"""AUD-02 raw_supersede_log 補正回歸測試 — heal 覆寫前留痕（`AUGUR-MC v1.3 §P4.E5` 矛盾保存）。

🎯 這支在做什麼(白話):以 pytest 鎖住 AUD-02 補正的行為不變式，分兩層：
   (A) 純函數層(零 DB、clean-room):`_supersessions` 判定核心——值真異入帳、no-op/純新不入帳、_norm 口徑、
       前導零反例、批內去重。此層在裝了 psycopg2 的任何環境皆跑（`_supersessions` 共用 reconcile._norm）。
   (B) DB 行為層(需 PostgreSQL;DB 不可用→skip、非假 pass):gate（非 heal 不留痕）、byte-differ 入帳、
       append-only trigger 擋 UPDATE/DELETE/TRUNCATE、tombstone 受控例外、同交易回滾。須於備援環境/人類本機跑。

   本檔補齊 `remediation/impl-2026-07-17` 實作缺少的**可執行 DB 行為回歸**（原僅 generic_schema._selftest
   鎖純邏輯、migrate --selftest 鎖 DDL 結構文字，無 pytest 實跑 trigger/tombstone/回滾）。合併取長：以該
   分支之實作為基底（強項：REVOKE 縱深、SECURITY DEFINER tombstone、actor 欄、INFRA_DDL 單一源），加本測試。

守 CLAUDE #7(須實測、紅綠鎖)· #15(誠實:DB 不可用時 skip 非 pass)· #12(SSOT=migrate_raw_supersede_ddl.py)。
"""
from __future__ import annotations

import pytest

from augur.core import generic_schema as gs

# ════════════════════════════════════════════════════════════════════
# (A) 純函數層 — 零 DB（gs._supersessions(cols, keys, rows, db_rows) → [(pk, old_row, new_row), …]）
# ════════════════════════════════════════════════════════════════════
KCOLS = ["stock_id", "date"]
SCOLS = ["stock_id", "date", "close"]


def _row(sid, d, close):
    return {"stock_id": sid, "date": d, "close": close}


def _sup(incoming, db):
    return gs._supersessions(SCOLS, KCOLS, incoming, db)


def test_value_change_logged():
    """值真異＝一筆 supersession，含衝突雙方 old/new＋pk（P4.E5 衝突雙方共存）。"""
    out = _sup([_row("2330", "2026-06-30", "605")], [_row("2330", "2026-06-30", "600")])
    assert len(out) == 1
    pk, old_row, new_row = out[0]
    assert old_row["close"] == "600" and new_row["close"] == "605"
    assert pk == {"stock_id": "2330", "date": "2026-06-30"}


def test_noop_upsert_not_logged():
    """byte 同值(no-op upsert)→不入帳。"""
    same = [_row("2330", "2026-06-30", "605")]
    assert _sup(same, list(same)) == []


def test_pure_insert_not_logged():
    """純新 insert（DB 無此鍵）→不入帳。"""
    assert _sup([_row("2330", "2026-06-30", "605")], [_row("1101", "2026-06-30", "1")]) == []


def test_norm_numeric_equivalence():
    """_norm 口徑共用:'605'≡'605.0'≡605 視為同值→不入帳（防口徑漂移假 supersession）。"""
    assert _sup([_row("2330", "2026-06-30", "605.0")], [_row("2330", "2026-06-30", "605")]) == []


def test_leading_zero_identifier_pairing():
    """前導零識別碼:'0050'(incoming) 不與 '50'(db) 誤配（反例鎖；退化則碰撞→誤配→轉紅）。"""
    assert _sup([_row("0050", "2026-06-30", "9")], [_row("50", "2026-06-30", "8")]) == []
    assert len(_sup([_row("0050", "2026-06-30", "9")], [_row("0050", "2026-06-30", "8")])) == 1


def test_batch_dedup_keeps_last():
    """批內同鍵去重＝保留最後一筆（＝upsert 勝方）。"""
    out = _sup([_row("2330", "2026-06-30", "601"), _row("2330", "2026-06-30", "605")],
               [_row("2330", "2026-06-30", "600")])
    assert len(out) == 1 and out[0][2]["close"] == "605"


def test_empty_inputs_safe():
    """空 incoming／空 db pre-image → 空（不炸）。

    註：空 keys 之守衛在呼叫端 `_snapshot_superseded`（`if not keys or not rows: return 0`），
    非在純函式 `_supersessions`（其在生產路徑恆收非空 keys）——此處只鎖純函式合約。
    """
    assert _sup([], [_row("2330", "2026-06-30", "1")]) == []
    assert _sup([_row("2330", "2026-06-30", "1")], []) == []


def test_gate_calls_snapshot_only_when_reason(monkeypatch):
    """主路徑 gate 零 DB 回歸鎖：provision_and_upsert 僅 snapshot_reason 非 None 時呼叫 _snapshot_superseded。

    鎖住「主路徑一 byte 不變」承諾於 CI（monkeypatch 掉 DB 相依與快照本體，純驗 gate 分流）。
    """
    calls = []
    monkeypatch.setattr(gs, "infer_schema", lambda rows: {"stock_id": "TEXT", "date": "DATE", "close": "NUMERIC(20,6)"})
    monkeypatch.setattr(gs, "detect_keys", lambda rows, schema, require=(): ["stock_id", "date"])
    monkeypatch.setattr(gs, "ensure_table", lambda cur, t, s, k: k)
    monkeypatch.setattr(gs, "upsert", lambda cur, t, rows, s, k: len(rows))
    monkeypatch.setattr(gs, "_snapshot_superseded", lambda cur, t, rows, s, k, reason, run_id=None: calls.append(reason) or 0)
    rows = [{"stock_id": "2330", "date": "2026-06-30", "close": "1"}]
    gs.provision_and_upsert(None, "t", rows, require_keys=("date",))                              # reason=None（主路徑）
    assert calls == []                                                                            # 不快照
    gs.provision_and_upsert(None, "t", rows, require_keys=("date",), snapshot_reason="heal_by_date")
    assert calls == ["heal_by_date"]                                                             # heal→快照，reason 正確透傳


# ════════════════════════════════════════════════════════════════════
# (B) DB 行為層 — 需 PostgreSQL；DB 不可用 → skip。整個 fixture 跑在單一交易、teardown ROLLBACK（零殘留；
#     PG DDL 交易性 → 建表/trigger/log 列於 rollback 後零殘留，對已 apply 之正式 DB 亦不污染）。
# ════════════════════════════════════════════════════════════════════
_TEST_TABLE = "_aud02_test_raw"


@pytest.fixture()
def cur():
    """單一交易 cursor：schema 就緒後 yield；teardown ROLLBACK。DB 不可用即 skip。"""
    try:
        import psycopg2  # noqa: F401
        from augur.core import config, schema
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 依賴不可用、跳過 DB 行為測試:{e}")
        return
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 DB 行為測試:{e}")
        return
    conn.autocommit = False
    import importlib.util
    import pathlib
    import sys
    scripts_dir = pathlib.Path(__file__).resolve().parents[1] / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))     # migration 以 `import _bootstrap`（scripts/ helper）自插 src/ 路徑
    mig_path = scripts_dir / "migrate_raw_supersede_ddl.py"
    spec = importlib.util.spec_from_file_location("_mig_aud02", mig_path)
    mig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mig)
    c = conn.cursor()
    schema.bootstrap_infra(c)                       # 建 infra 表（含 raw_supersede_log；IF NOT EXISTS 冪等）
    c.execute(f'DROP TABLE IF EXISTS "{_TEST_TABLE}"')
    for _label, ddl in mig.DDL:                     # 套 migration 硬化（trigger/tombstone/REVOKE/index；冪等）
        c.execute(ddl)
    try:
        yield c
    finally:
        conn.rollback()                             # 一律回滾：schema 變更與所有 log 列零殘留
        conn.close()


def _seed(cur, close):
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": close}], require_keys=("date",))


def _heal(cur, close):
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": close}],
                            require_keys=("date",), snapshot_reason="heal_by_date")


def _log_count(cur):
    cur.execute('SELECT count(*) FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))
    return cur.fetchone()[0]


def test_db_gate_non_heal_no_snapshot(cur):
    """gate：snapshot_reason=None（主路徑/daily 增量）覆寫值亦不留痕。"""
    _seed(cur, "600")
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": "605"}], require_keys=("date",))
    assert _log_count(cur) == 0


def test_db_heal_byte_differ_logged(cur):
    """heal 覆寫真異值 → 入帳一筆，old/new 正確（old_row NUMERIC(20,6) → '600.000000'，故數值比對）。"""
    _seed(cur, "600")
    _heal(cur, "605")
    cur.execute('SELECT old_row->>%s, new_row->>%s, reason FROM raw_supersede_log WHERE "table"=%s',
                ("close", "close", _TEST_TABLE))
    old_c, new_c, reason = cur.fetchone()
    assert (float(old_c), float(new_c), reason) == (600.0, 605.0, "heal_by_date")


def test_db_heal_noop_not_logged(cur):
    """heal 重抓但值與 DB 相同（no-op upsert）→ 不入帳。"""
    _seed(cur, "605")
    _heal(cur, "605")
    assert _log_count(cur) == 0


def test_db_append_only_blocks_update_delete(cur):
    """append-only trigger：對 raw_supersede_log 之 UPDATE 與 DELETE 皆 RAISE。"""
    import psycopg2
    _seed(cur, "600")
    _heal(cur, "605")
    for stmt, params in (('UPDATE raw_supersede_log SET note=%s WHERE "table"=%s', ("x", _TEST_TABLE)),
                         ('DELETE FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))):
        cur.execute("SAVEPOINT sp")
        with pytest.raises(psycopg2.Error):
            cur.execute(stmt, params)
        cur.execute("ROLLBACK TO SAVEPOINT sp")
    assert _log_count(cur) == 1


def test_db_truncate_blocked(cur):
    """TRUNCATE 亦被 statement-level BEFORE TRUNCATE trigger 擋（row-level 擋不住 TRUNCATE）。"""
    import psycopg2
    _seed(cur, "600")
    _heal(cur, "605")
    cur.execute("SAVEPOINT sp")
    with pytest.raises(psycopg2.Error):
        cur.execute("TRUNCATE raw_supersede_log")
    cur.execute("ROLLBACK TO SAVEPOINT sp")
    assert _log_count(cur) == 1


def test_db_tombstone_controlled_erasure(cur):
    """tombstone 受控函式（P4.E3 唯一例外）：抹 old/new 內容本體、保留該列＋provenance；須具事由。"""
    import psycopg2
    _seed(cur, "600")
    _heal(cur, "605")
    cur.execute('SELECT id FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))
    rid = cur.fetchone()[0]
    cur.execute("SAVEPOINT sp")
    with pytest.raises(psycopg2.Error):              # 空事由被拒
        cur.execute("SELECT raw_supersede_tombstone(%s, %s)", (rid, ""))
    cur.execute("ROLLBACK TO SAVEPOINT sp")
    cur.execute("SELECT raw_supersede_tombstone(%s, %s)", (rid, "GDPR erasure req #42"))  # 具事由：抹內容、留列
    cur.execute("SELECT old_row->>'_tombstoned', note FROM raw_supersede_log WHERE id=%s", (rid,))
    tombstoned, note = cur.fetchone()
    assert tombstoned == "true" and "GDPR erasure req #42" in note
    assert _log_count(cur) == 1                       # 列仍在（tombstone 非 DELETE）


def test_db_same_transaction_rollback(cur):
    """同交易原子性：heal 快照後於同交易失敗 → 快照與 upsert 一起回滾（P4.E5 交易同一性；SAVEPOINT 模擬）。"""
    _seed(cur, "600")
    before = _log_count(cur)
    cur.execute("SAVEPOINT healstep")
    _heal(cur, "605")
    assert _log_count(cur) == before + 1              # 段內已見快照
    cur.execute("ROLLBACK TO SAVEPOINT healstep")     # 模擬同交易後續失敗 → 整段退回
    assert _log_count(cur) == before                  # 快照隨之回滾
    cur.execute(f'SELECT close FROM "{_TEST_TABLE}" WHERE stock_id=%s', ("2330",))
    assert str(cur.fetchone()[0]) in ("600", "600.000000")   # DB 值未被覆寫
