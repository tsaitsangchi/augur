"""AUD-02 raw_supersede_log 補正回歸測試 — heal 覆寫前留痕（`AUGUR-MC v1.3 §P4.E5` 矛盾保存）。

🎯 這支在做什麼(白話):驗證「heal 以 API 現值覆寫 DB 舊值時，覆寫前把被取代舊列快照到
   raw_supersede_log」這條補正的六個不變式。分兩層：
   (A) 純函數層(零 DB、clean-room):`_compute_supersessions` 之判定邏輯——值真異入帳、no-op/純新不入帳、
       _norm 口徑、批內去重。此層在任何環境皆跑。
   (B) DB 行為層(需 PostgreSQL;DB 不可用→skip、非假 pass):gate（非 heal 不留痕）、byte-differ 入帳、
       append-only trigger 擋 UPDATE/DELETE、tombstone 受控例外、同交易回滾。此層須於備援環境/人類本機跑。

守 CLAUDE #7(須實測、紅綠鎖)· #15(誠實:DB 不可用時 skip 非 pass)· #12(SSOT=migrate_raw_supersede_ddl.py)。
   設計卷宗:docs/remediation/AUD-02-raw-supersede-log.md。
"""
from __future__ import annotations

import pytest

from augur.core import generic_schema as gs

# ════════════════════════════════════════════════════════════════════
# (A) 純函數層 — 零 DB，任何環境皆跑（_compute_supersessions 判定核心）
# ════════════════════════════════════════════════════════════════════
KCOLS = ["stock_id", "date"]
SCOLS = ["stock_id", "date", "close"]


def _row(sid, d, close):
    return {"stock_id": sid, "date": d, "close": close}


def test_value_change_logged():
    """值真異＝一筆 supersession，含衝突雙方 old/new＋pk（P4.E5 衝突雙方共存）。"""
    sup = gs._compute_supersessions([_row("2330", "2026-06-30", "605")],
                                    [_row("2330", "2026-06-30", "600")], KCOLS, SCOLS)
    assert len(sup) == 1
    assert sup[0]["old_row"]["close"] == "600"
    assert sup[0]["new_row"]["close"] == "605"
    assert sup[0]["pk"] == {"stock_id": "2330", "date": "2026-06-30"}


def test_noop_upsert_not_logged():
    """byte 同值(no-op upsert)→不入帳（不製造假 supersession）。"""
    same = [_row("2330", "2026-06-30", "605")]
    assert gs._compute_supersessions(same, list(same), KCOLS, SCOLS) == []


def test_pure_insert_not_logged():
    """純新 insert（DB 無此鍵）→不入帳（無被取代舊值）。"""
    assert gs._compute_supersessions([_row("2330", "2026-06-30", "605")],
                                     [_row("1101", "2026-06-30", "1")], KCOLS, SCOLS) == []


def test_norm_numeric_equivalence():
    """_norm 口徑共用:'605'≡'605.0'≡605 視為同值→不入帳（防口徑漂移致假 supersession）。"""
    assert gs._compute_supersessions([_row("2330", "2026-06-30", "605.0")],
                                     [_row("2330", "2026-06-30", "605")], KCOLS, SCOLS) == []


def test_leading_zero_identifier_pairing():
    """前導零識別碼配對:'0050' 不與 50 混（共用 reconcile._norm 之識別碼保護）。"""
    sup = gs._compute_supersessions([_row("0050", "2026-06-30", "9")],
                                    [_row("0050", "2026-06-30", "8")], KCOLS, SCOLS)
    assert len(sup) == 1


def test_batch_dedup_keeps_last():
    """批內同鍵去重＝保留最後一筆（＝upsert 勝方）。"""
    sup = gs._compute_supersessions(
        [_row("2330", "2026-06-30", "601"), _row("2330", "2026-06-30", "605")],
        [_row("2330", "2026-06-30", "600")], KCOLS, SCOLS)
    assert len(sup) == 1 and sup[0]["new_row"]["close"] == "605"


def test_empty_inputs_safe():
    """空輸入/無 keys→空（不炸）。"""
    assert gs._compute_supersessions([], [_row("2330", "2026-06-30", "1")], KCOLS, SCOLS) == []
    assert gs._compute_supersessions([_row("2330", "2026-06-30", "1")], [], KCOLS, SCOLS) == []
    assert gs._compute_supersessions([_row("2330", "2026-06-30", "1")],
                                     [_row("2330", "2026-06-30", "2")], [], SCOLS) == []


# ════════════════════════════════════════════════════════════════════
# (B) DB 行為層 — 需 PostgreSQL；DB 不可用 → skip（誠實、非假 pass）
#     六不變式：gate（非 heal 不留痕）／byte-differ 入帳／no-op 不入帳／
#     append-only trigger 擋 UPDATE+DELETE／tombstone 受控例外／同交易回滾。
#
#     隔離策略：整個 fixture（含 schema 建置與所有寫入）跑在**單一交易**內，teardown 一律 ROLLBACK。
#     PostgreSQL 之 DDL 為交易性 → setup 的建表/trigger/function 與所有 log 列於 rollback 後零殘留，
#     即便對已 apply migration 之正式 DB 亦不污染 raw_supersede_log（append-only 不可 DELETE，故唯有 rollback 能清）。
#     每個子測試以 SAVEPOINT 隔離，令 trigger RAISE 之交易中止不影響後續斷言。
# ════════════════════════════════════════════════════════════════════
_TEST_TABLE = "_aud02_test_raw"


@pytest.fixture()
def cur():
    """單一交易 cursor：schema 就緒後 yield；teardown ROLLBACK（零殘留）。DB 不可用即 skip。"""
    try:
        import psycopg2
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
    mig_path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "migrate_raw_supersede_ddl.py"
    spec = importlib.util.spec_from_file_location("_mig_aud02", mig_path)
    mig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mig)
    c = conn.cursor()
    schema.bootstrap_infra(c)                       # 建 infra 表（含 raw_supersede_log；IF NOT EXISTS 冪等）
    c.execute(f'DROP TABLE IF EXISTS "{_TEST_TABLE}"')
    for _label, ddl in mig.DDL:                     # 套 migration 硬化（trigger/tombstone/index；冪等）
        c.execute(ddl)
    try:
        yield c
    finally:
        conn.rollback()                             # 一律回滾：schema 變更與所有 log 列零殘留
        conn.close()


def _seed(cur, close):
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": close}],
                            require_keys=("date",))


def _log_count(cur):
    cur.execute('SELECT count(*) FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))
    return cur.fetchone()[0]


def _heal(cur, close):
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": close}],
                            require_keys=("date",), snapshot_reason="heal_by_date")


def test_db_gate_non_heal_no_snapshot(cur):
    """gate：snapshot_reason=None（主路徑/daily 增量）覆寫值亦不留痕。"""
    _seed(cur, "600")
    gs.provision_and_upsert(cur, _TEST_TABLE,
                            [{"stock_id": "2330", "date": "2026-06-30", "close": "605"}],
                            require_keys=("date",))   # 無 snapshot_reason
    assert _log_count(cur) == 0


def test_db_heal_byte_differ_logged(cur):
    """heal（snapshot_reason 非 None）覆寫真異值 → 入帳一筆，old/new 正確。"""
    _seed(cur, "600")
    _heal(cur, "605")
    cur.execute('SELECT old_row->>%s, new_row->>%s, reason FROM raw_supersede_log WHERE "table"=%s',
                ("close", "close", _TEST_TABLE))
    assert cur.fetchone() == ("600", "605", "heal_by_date")


def test_db_heal_noop_not_logged(cur):
    """heal 重抓但值與 DB 相同（no-op upsert）→ 不入帳。"""
    _seed(cur, "605")
    _heal(cur, "605")
    assert _log_count(cur) == 0


def test_db_append_only_blocks_update_delete(cur):
    """append-only trigger（決策 A）：對 raw_supersede_log 之 UPDATE 與 DELETE 皆 RAISE。"""
    import psycopg2
    _seed(cur, "600")
    _heal(cur, "605")
    for stmt, params in (('UPDATE raw_supersede_log SET note=%s WHERE "table"=%s', ("x", _TEST_TABLE)),
                         ('DELETE FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))):
        cur.execute("SAVEPOINT sp")
        with pytest.raises(psycopg2.Error):
            cur.execute(stmt, params)
        cur.execute("ROLLBACK TO SAVEPOINT sp")     # 復原被 RAISE 中止之交易態、續驗
    assert _log_count(cur) == 1                      # 兩次違規皆被擋、帳列仍在


def test_db_tombstone_controlled_erasure(cur):
    """tombstone 受控函式（P4.E3 唯一例外）：抹 old/new 內容本體、保留該列＋provenance；須具事由。"""
    import psycopg2
    _seed(cur, "600")
    _heal(cur, "605")
    cur.execute('SELECT id FROM raw_supersede_log WHERE "table"=%s', (_TEST_TABLE,))
    rid = cur.fetchone()[0]
    cur.execute("SAVEPOINT sp")
    with pytest.raises(psycopg2.Error):              # 空事由被拒
        cur.execute("SELECT tombstone_raw_supersede(%s, %s)", (rid, ""))
    cur.execute("ROLLBACK TO SAVEPOINT sp")
    cur.execute("SELECT tombstone_raw_supersede(%s, %s)", (rid, "GDPR erasure req #42"))  # 具事由：抹內容、留列
    cur.execute("SELECT old_row->>'_tombstoned', note FROM raw_supersede_log WHERE id=%s", (rid,))
    tombstoned, note = cur.fetchone()
    assert tombstoned == "true" and "GDPR erasure req #42" in note
    assert _log_count(cur) == 1                       # 列仍在（tombstone 非 DELETE）


def test_db_same_transaction_rollback(cur):
    """同交易原子性：heal 快照後於同交易人為報錯 → 快照與 upsert 一起回滾（P4.E5 交易同一性）。

    以 SAVEPOINT 模擬「heal 段內」之後續失敗：ROLLBACK TO 使該段（快照＋upsert）整段退回。"""
    _seed(cur, "600")
    before = _log_count(cur)
    cur.execute("SAVEPOINT healstep")
    _heal(cur, "605")                                 # 快照 + upsert 覆寫
    assert _log_count(cur) == before + 1              # 段內已見快照
    cur.execute("ROLLBACK TO SAVEPOINT healstep")     # 模擬同交易後續失敗 → 整段退回
    assert _log_count(cur) == before                  # 快照隨之回滾
    cur.execute(f'SELECT close FROM "{_TEST_TABLE}" WHERE stock_id=%s', ("2330",))
    assert str(cur.fetchone()[0]) in ("600", "600.000000")   # DB 值未被覆寫（仍為 600）
