"""Phase 2 Identity 接縫回歸測試 — resolve_or_mint/backfill 冪等/code-reuse 紅旗/屬性版本 append。

🎯 這支在做什麼(白話):以 pytest 鎖住 Phase 2 沙盒演練包的行為不變式,分兩層:
   (A) 純函數層(零 DB、clean-room):resolution_action 五動作判準(mint/resolved/provisional_mint/
       provisional_resolved/ambiguous)+ sync 之 diff_attrs 差異純邏輯。
   (B) DB 行為層(需 PostgreSQL;DB 不可用→skip、非假 pass;**現 database=augur 生產庫→skip,沙盒紀律**):
       resolve_or_mint 鑄→再解析同枚(冪等)、code-reuse 紅旗案例(retire 後同碼再現→provisional 新身不縫合、
       重跑不重複鑄)、backfill 全名冊重跑計數不變(minted=0)、屬性版本 append(SCD-2 不覆蓋+get_asof 讀最新+
       重跑零 append)。fixture 比照 tests/test_raw_supersede_log.py 雙角色模式:單一交易+teardown ROLLBACK
       (沙盒零殘留);六表/守衛 trigger 未在場時以 DB_SUPERUSER 套 migration(migration 屬 owner 側、行為屬應用側)。

守 CLAUDE #7(須實測、紅綠鎖)· #15(誠實:DB 不可用時 skip 非 pass)· ID.11/ID.43/ID.60。
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
from datetime import date

import pytest

from augur.identity.resolve import resolution_action

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))       # scripts 以 `import _bootstrap` 自插 src/ 路徑


def _load_script(name):
    spec = importlib.util.spec_from_file_location(f"_p2_{name}", _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ════════════════════════════════════════════════════════════════════
# (A) 純函數層 — 零 DB
# ════════════════════════════════════════════════════════════════════

def test_resolution_action_fresh_mint():
    """查無候選→mint(adopted 路徑)。"""
    assert resolution_action([], set()) == ("mint", None)


def test_resolution_action_single_live_resolved():
    """恰一候選且無 retire 史→直接解析(增量主路徑)。"""
    assert resolution_action(["a"], set()) == ("resolved", "a")


def test_resolution_action_code_reuse_provisional_mint():
    """紅旗:唯一候選已 retire(碼再現)→provisional_mint、不縫合舊身(ID.43)。"""
    assert resolution_action(["a"], {"a"}) == ("provisional_mint", None)


def test_resolution_action_provisional_rerun_idempotent():
    """紅旗重跑:retire 舊身+前次已鑄之未退役新身→解析回新身、不重複鑄造。"""
    assert resolution_action(["a", "b"], {"a"}) == ("provisional_resolved", "b")


def test_resolution_action_ambiguous_no_mint():
    """>1 未退役候選→ambiguous 回最新、呼叫端零寫入(待人解析,DEFER L4/5)。"""
    assert resolution_action(["a", "b"], set()) == ("ambiguous", "b")
    assert resolution_action(["a", "b", "c"], {"a"}) == ("ambiguous", "c")


def test_resolution_action_dedup_preserves_order():
    """候選去重保序(同 augur_id 多列 alias 不誤判 ambiguous)。"""
    assert resolution_action(["a", "a", "a"], set()) == ("resolved", "a")


def test_diff_attrs_pure_logic():
    """sync 差異純邏輯:首見全 append、值同零 append(冪等)、單屬性異僅該屬性、None 不覆蓋。"""
    sync = _load_script("sync_attribute_versions")
    row = {"stock_id": "2330", "valid_from": date(2026, 7, 16),
           "industry_category": "半導體業|電子工業", "stock_name": "台積電", "type": "twse"}
    assert [a for a, _ in sync.diff_attrs({}, row)] == list(sync.ATTRS)
    same = {k: row[k] for k in sync.ATTRS}
    assert sync.diff_attrs(same, row) == []
    assert sync.diff_attrs({**same, "type": "emerging"}, row) == [("type", "twse")]
    assert sync.diff_attrs(same, {**row, "stock_name": None}) == []


# ════════════════════════════════════════════════════════════════════
# (B) DB 行為層 — 需 PostgreSQL(沙盒);單一交易、teardown ROLLBACK 零殘留
# ════════════════════════════════════════════════════════════════════
_CS_TEST = "test:phase2"          # 測試專用 code_system,與名冊 code_system 隔離
_EVID = "test|phase2|fixture"


@pytest.fixture()
def cur():
    """單一交易 cursor:六表/守衛就緒後 yield;teardown ROLLBACK。DB 不可用或=生產庫 augur 即 skip。"""
    try:
        import psycopg2  # noqa: F401
        from augur.core import config
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 依賴不可用、跳過 DB 行為測試:{e}")
        return
    if config.DB_PARAMS["dbname"] == "augur":
        pytest.skip("現 DB=augur 生產庫:行為測試僅沙盒跑(DB_NAME=augur_sandbox;DB 紀律)")
        return
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 DB 行為測試:{e}")
        return
    conn.autocommit = False
    c = conn.cursor()
    c.execute("SELECT count(*) FROM information_schema.tables WHERE table_name IN "
              "('entity_type_catalog','entity_registry','entity_alias','identity_claim',"
              "'identity_lifecycle_event','entity_attribute_version')")
    if c.fetchone()[0] < 6:
        # 雙角色模式(比照 test_raw_supersede_log):migration 屬 owner 側,以 DB_SUPERUSER 套用;無憑證→skip
        import os
        su_pw = os.getenv("DB_SUPERUSER_PASSWORD")
        if not su_pw:
            conn.close()
            pytest.skip("identity 六表未在場且無 DB_SUPERUSER_PASSWORD、跳過(先跑 migrate_identity_ddl.py)")
            return
        from augur.core import config as _cfg
        mig = _load_script("migrate_identity_ddl")
        aconn = psycopg2.connect(connect_timeout=10, **{**_cfg.DB_PARAMS,
                                 "user": os.getenv("DB_SUPERUSER", "postgres"), "password": su_pw})
        aconn.autocommit = True
        try:
            ac = aconn.cursor()
            for _label, ddl in mig.DDL:
                ac.execute(ddl)
        finally:
            aconn.close()
    # 型別 catalog 就緒(Security instance);未 seed 之庫於本交易內補(teardown 回滾、零殘留)
    c.execute("SELECT 1 FROM entity_type_catalog WHERE entity_type='Security'")
    if c.fetchone() is None:
        seed = _load_script("seed_entity_type_catalog")
        for row in seed.SEED:
            c.execute(seed.UPSERT, row)
    try:
        yield c
    finally:
        conn.rollback()                     # 一律回滾:測試鑄造/事件/版本零殘留
        conn.close()


def _mint_code(cur, code, evidence=_EVID):
    from augur.identity import resolve
    return resolve.resolve_or_mint(cur, _CS_TEST, code, "Security", evidence, "pytest/phase2")


def test_db_resolve_or_mint_fresh_then_idempotent(cur):
    """首見→minted+adopted alias;再呼叫→resolved 同枚(冪等、不重複鑄);registry 恰一列。"""
    import uuid
    code = f"_p2_{uuid.uuid4().hex[:10]}"
    r1 = _mint_code(cur, code)
    assert r1["action"] == "minted" and not r1["red_flag"]
    assert r1["augur_id"].startswith("augur:security/")
    cur.execute("SELECT alias_status FROM entity_alias WHERE code_system=%s AND external_code=%s",
                (_CS_TEST, code))
    assert [s for (s,) in cur.fetchall()] == ["adopted"]
    r2 = _mint_code(cur, code)
    assert r2["action"] == "resolved" and r2["augur_id"] == r1["augur_id"]
    cur.execute("SELECT count(*) FROM entity_registry WHERE augur_id=%s", (r1["augur_id"],))
    assert cur.fetchone()[0] == 1


def test_db_code_reuse_red_flag_provisional_no_stitch(cur):
    """紅旗案例(ID.43):retire 後同碼再現→provisional 新身、不縫合舊身;重跑解析回新身不再鑄。"""
    import uuid
    from augur.identity import lifecycle
    code = f"_p2_{uuid.uuid4().hex[:10]}"
    old = _mint_code(cur, code)["augur_id"]
    lifecycle.record_event(cur, old, "retire", "pytest/phase2",
                           evidence_ref="test|TaiwanStockDelisting|模擬下市")
    r3 = _mint_code(cur, code)
    assert r3["red_flag"] is True
    assert r3["action"] == "provisional_minted" and r3["augur_id"] != old
    cur.execute("SELECT alias_status FROM entity_alias WHERE code_system=%s AND external_code=%s "
                "AND augur_id=%s", (_CS_TEST, code, r3["augur_id"]))
    assert cur.fetchone()[0] == "provisional"
    r4 = _mint_code(cur, code)                      # 重跑冪等:解析回 provisional 新身
    assert r4["action"] == "provisional_resolved" and r4["augur_id"] == r3["augur_id"]
    cur.execute("SELECT count(DISTINCT augur_id) FROM entity_alias WHERE code_system=%s "
                "AND external_code=%s", (_CS_TEST, code))
    assert cur.fetchone()[0] == 2                   # 恰二身:舊(retired)+新(provisional),無第三枚


def test_db_backfill_idempotent_rerun(cur):
    """backfill 全名冊重跑:第二輪 minted=0 且 entity_registry 計數不變(冪等)。"""
    bf = _load_script("backfill_entity_registry")
    from augur.identity import resolve

    def run_once():
        out = {}
        for label, etype, cs_attr, sql in bf.ROSTERS:
            roster = bf.read_roster(cur, sql)
            out[label] = bf.mint_batch(cur, roster, etype, getattr(resolve, cs_attr))
        return out

    run_once()
    cur.execute("SELECT count(*) FROM entity_registry")
    n1 = cur.fetchone()[0]
    second = run_once()
    cur.execute("SELECT count(*) FROM entity_registry")
    n2 = cur.fetchone()[0]
    assert n2 == n1                                  # 重跑計數不變
    assert all(c["minted"] == 0 and c["provisional_minted"] == 0 for c in second.values())
    assert sum(c["resolved"] for c in second.values()) > 0


def test_db_attribute_version_append_scd2(cur):
    """屬性版本:首同步全 append→重跑零 append(冪等)→值變 append 新版本(不覆蓋)、get_asof 讀到最新。"""
    import uuid
    from augur.identity import attribute_version
    sync = _load_script("sync_attribute_versions")
    code = f"_p2_{uuid.uuid4().hex[:10]}"
    aid = _mint_code(cur, code)["augur_id"]
    row_v1 = {"stock_id": code, "valid_from": date(2026, 7, 1),
              "industry_category": "半導體業", "stock_name": "測試股", "type": "emerging"}
    c1 = sync.sync_versions(cur, [row_v1], _CS_TEST)
    assert (c1["entities"], c1["appended"]) == (1, 3)
    c2 = sync.sync_versions(cur, [row_v1], _CS_TEST)
    assert (c2["appended"], c2["unchanged"]) == (0, 1)          # 冪等:重跑零 append
    row_v2 = {**row_v1, "valid_from": date(2026, 7, 16), "type": "twse"}
    c3 = sync.sync_versions(cur, [row_v2], _CS_TEST)
    assert c3["appended"] == 1                                   # 僅異動屬性 append
    cur.execute("SELECT count(*) FROM entity_attribute_version WHERE augur_id=%s "
                "AND attribute_name='type'", (aid,))
    assert cur.fetchone()[0] == 2                                # SCD-2:兩版本並存、未覆蓋
    latest = attribute_version.get_asof(cur, aid, "type", "2027-01-01")
    assert latest["attribute_value"] == "twse"
    cur.execute("SELECT count(*) FROM entity_attribute_version WHERE augur_id=%s", (aid,))
    assert cur.fetchone()[0] == 4                                # 3 首版 + 1 異動版


def test_db_sync_skips_unresolved_and_ambiguous(cur):
    """sync 對未鑄碼誠實計 unresolved(不強縫);歧義(>1 未退役身)計 ambiguous 零寫入。"""
    import uuid
    sync = _load_script("sync_attribute_versions")
    ghost = {"stock_id": f"_p2_{uuid.uuid4().hex[:10]}", "valid_from": date(2026, 7, 16),
             "industry_category": "x", "stock_name": "y", "type": "z"}
    c = sync.sync_versions(cur, [ghost], _CS_TEST)
    assert (c["unresolved"], c["appended"]) == (1, 0)
    code = f"_p2_{uuid.uuid4().hex[:10]}"
    a1 = _mint_code(cur, code)["augur_id"]                       # 同碼二未退役身=歧義(手工構造)
    from augur.identity import identifier, resolve as rz
    a2 = identifier.mint(cur, "Security", _EVID, "pytest/phase2")
    rz._register_alias(cur, a2, _CS_TEST, code, "provisional", _EVID)
    assert a1 != a2
    amb = sync.sync_versions(cur, [{**ghost, "stock_id": code}], _CS_TEST)
    assert (amb["ambiguous"], amb["appended"]) == (1, 0)
