"""Phase 2 retire backfill 回歸測試 — 冪等/重用碼分裂端到端/名實不符計數/advisory lock 並發防護。

🎯 這支在做什麼(白話):以 pytest 鎖住 RULING-2026-015 補件分支的行為不變式,分三層:
   (A) 純函數層(零 DB):retire_action 三動作判準(already/mint_retire/provisional_retire)+
       sync 之 null_date 誠實跳過純路徑。
   (B) DB 行為層(需 PostgreSQL 沙盒;DB 不可用→skip、=生產庫 augur→skip):
       裁③ 乾淨順序端到端(下市→retire 預鑄→今日名冊 mint→provisional 分裂不縫合)、retire backfill
       冪等(重跑零新增)、殘留錯序下之 provisional 分身(不掛 retire 上既有身)、名實不符佇列自洽、
       resolve_alias 之 alias_id tie-break 確定性。fixture 同 test_phase2_identity:單一交易+teardown
       ROLLBACK(零殘留)。
   (C) 並發層(需沙盒;另開真雙連線):裁① advisory lock 實測——
       (C1) 同碼雙連線:後到者於先到者交易存續期間被鎖阻(lock_timeout 逾時證阻塞=序列化),全程回滾零殘留;
       (C2) 同碼雙連線自然完序:A mint+commit、B 並發解析→兩端同一 augur_id、恆恰一身(雙鑄防護端到端)。
       ⚠ C2 須真 commit 方能跨連線可見:採固定探針碼 test:p2retire/_p2r_lockprobe,首跑後沙盒永久留
       **恰一枚**探針身份(有界、冪等、誠實揭露);之後每跑皆 resolved、零新增。

守 CLAUDE #7(須實測)· #15(DB 不可用 skip 非假 pass)· 裁①/裁③(RULING-2026-015)· ID.40/ID.43。
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import threading
import time
from datetime import date

import pytest

from augur.identity.resolve import resolution_action

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))       # scripts 以 `import _bootstrap` 自插 src/ 路徑


def _load_script(name):
    spec = importlib.util.spec_from_file_location(f"_p2r_{name}", _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


br = _load_script("backfill_lifecycle_retire")

# ════════════════════════════════════════════════════════════════════
# (A) 純函數層 — 零 DB
# ════════════════════════════════════════════════════════════════════


def test_retire_action_already_idempotent():
    """同 evidence 之 retire 事件在案→already(冪等鍵=evidence 全等;重跑零新增)。"""
    assert br.retire_action(["a"], {"a"}) == ("already", "a")
    assert br.retire_action(["a", "b"], {"b"}) == ("already", "b")


def test_retire_action_fresh_mint_retire():
    """碼查無 alias(retire 先行、registry 空)→mint_retire:預鑄 retired 身份。"""
    assert br.retire_action([], set()) == ("mint_retire", None)


def test_retire_action_bound_code_provisional():
    """碼已繫既有身(殘留/錯序/重用)→provisional_retire:分身不縫合(ID.43),不掛 retire 上既有身。"""
    assert br.retire_action(["a"], set()) == ("provisional_retire", None)
    assert br.retire_action(["a", "b"], set()) == ("provisional_retire", None)


def test_sync_null_date_skip_pure():
    """minors:valid_from=None 於任何 DB 存取前計 null_date 跳過(cur=None 可跑即證)、不 today() 兜底。"""
    sync = _load_script("sync_attribute_versions")
    row = {"stock_id": "9999", "valid_from": None,
           "industry_category": "x", "stock_name": "y", "type": "z"}
    c = sync.sync_versions(None, [row], "test:cs")
    assert (c["null_date"], c["appended"], c["entities"], c["unresolved"]) == (1, 0, 0, 0)


# ════════════════════════════════════════════════════════════════════
# (B) DB 行為層 — 需 PostgreSQL 沙盒;單一交易、teardown ROLLBACK 零殘留
# ════════════════════════════════════════════════════════════════════
_CS = "test:p2retire"                 # 測試專用 code_system,與名冊/rehearsal code_system 皆隔離
_EVID = "test|p2retire|fixture"


def _skip_unless_sandbox():
    try:
        import psycopg2  # noqa: F401
        from augur.core import config
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 依賴不可用:{e}")
    if config.DB_PARAMS["dbname"] == "augur":
        pytest.skip("現 DB=augur 生產庫:行為測試僅沙盒跑(DB_NAME=augur_sandbox;DB 紀律)")
    return config


@pytest.fixture()
def cur():
    """單一交易 cursor;teardown ROLLBACK。identity 六表未在場→skip(先跑 migrate_identity_ddl.py)。"""
    config = _skip_unless_sandbox()
    import psycopg2
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用:{e}")
        return
    conn.autocommit = False
    c = conn.cursor()
    c.execute("SELECT count(*) FROM information_schema.tables WHERE table_name IN "
              "('entity_type_catalog','entity_registry','entity_alias',"
              "'identity_lifecycle_event','entity_attribute_version')")
    if c.fetchone()[0] < 5:
        conn.close()
        pytest.skip("identity 表未在場(先跑 migrate_identity_ddl.py)")
        return
    c.execute("SELECT 1 FROM entity_type_catalog WHERE entity_type='Security'")
    if c.fetchone() is None:
        conn.close()
        pytest.skip("entity_type_catalog 未 seed(先跑 seed_entity_type_catalog.py)")
        return
    try:
        yield c
    finally:
        conn.rollback()
        conn.close()


def _delist_row(code, name="舊名股", d=date(2010, 1, 4)):
    ev = f"TaiwanStockDelisting|stock_id={code}|date={d}|name={name}"
    return (code, name, d, ev)


def test_db_clean_order_end_to_end_split(cur):
    """裁③ 端到端(乾淨順序):下市→retire 預鑄(adopted+retire 事件)→今日名冊 mint→provisional 分裂
    不縫合→重跑雙側皆冪等。"""
    import uuid
    from augur.identity import resolve
    code = f"_p2r_{uuid.uuid4().hex[:10]}"
    row = _delist_row(code)
    # (1) retire 先行:預鑄 retired 身份
    c1 = br.process_delisting(cur, [row], _CS, code_lock=False)
    assert (c1["retire_minted"], c1["retire_provisional"], c1["already"]) == (1, 0, 0)
    cur.execute("SELECT augur_id, alias_status FROM entity_alias WHERE code_system=%s "
                "AND external_code=%s", (_CS, code))
    rows = cur.fetchall()
    assert len(rows) == 1 and rows[0][1] == "adopted"
    old_id = rows[0][0]
    assert old_id.startswith("augur:security/")
    cur.execute("SELECT event_type, evidence_ref, valid_time::date FROM identity_lifecycle_event "
                "WHERE augur_id=%s", (old_id,))
    ev = cur.fetchall()
    assert ev == [("retire", row[3], date(2010, 1, 4))]      # evidence=下市來源列、valid_time=下市日
    # (2) 存量鑄造遇同碼今日名冊列 → ID.43 紅旗 provisional 分裂、不縫合
    r = resolve.resolve_or_mint(cur, _CS, code, "Security", "test|roster|today", "pytest/p2retire")
    assert r["action"] == "provisional_minted" and r["red_flag"] is True
    assert r["augur_id"] != old_id                            # 分裂:新身 ≠ 已 retire 舊身
    cur.execute("SELECT alias_status FROM entity_alias WHERE code_system=%s AND external_code=%s "
                "AND augur_id=%s", (_CS, code, r["augur_id"]))
    assert cur.fetchone()[0] == "provisional"
    # (3) 雙側重跑皆冪等:retire→already;resolve→provisional_resolved 回新身
    c2 = br.process_delisting(cur, [row], _CS, code_lock=False)
    assert (c2["already"], c2["retire_minted"], c2["retire_provisional"]) == (1, 0, 0)
    r2 = resolve.resolve_or_mint(cur, _CS, code, "Security", "test|roster|today", "pytest/p2retire")
    assert r2["action"] == "provisional_resolved" and r2["augur_id"] == r["augur_id"]
    cur.execute("SELECT count(DISTINCT augur_id) FROM entity_alias WHERE code_system=%s "
                "AND external_code=%s", (_CS, code))
    assert cur.fetchone()[0] == 2                             # 恰二身:retired 舊+provisional 新,無第三枚


def test_db_retire_backfill_idempotent_rerun(cur):
    """retire backfill 冪等:同批重跑第二輪全 already、registry/lifecycle 計數不變(零新增)。"""
    import uuid
    rows = [_delist_row(f"_p2r_{uuid.uuid4().hex[:10]}") for _ in range(3)]
    c1 = br.process_delisting(cur, rows, _CS, code_lock=False)
    assert c1["retire_minted"] == 3
    cur.execute("SELECT count(*) FROM entity_registry")
    n1 = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE event_type='retire'")
    e1 = cur.fetchone()[0]
    c2 = br.process_delisting(cur, rows, _CS, code_lock=False)
    assert (c2["already"], c2["retire_minted"], c2["retire_provisional"]) == (3, 0, 0)
    cur.execute("SELECT count(*) FROM entity_registry")
    assert cur.fetchone()[0] == n1
    cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE event_type='retire'")
    assert cur.fetchone()[0] == e1


def test_db_residue_order_provisional_no_stitch(cur):
    """殘留錯序(名冊鑄造先行):retire backfill 不把 retire 掛上既有活身(強縫歷史)——鑄 provisional
    分身攜下市 evidence;之後同碼 resolve 回既有活身(provisional_resolved+紅旗)。"""
    import uuid
    from augur.identity import resolve
    code = f"_p2r_{uuid.uuid4().hex[:10]}"
    live = resolve.resolve_or_mint(cur, _CS, code, "Security", "test|roster|today",
                                   "pytest/p2retire")["augur_id"]     # 殘留:名冊身先在
    c1 = br.process_delisting(cur, [_delist_row(code)], _CS, code_lock=False)
    assert (c1["retire_provisional"], c1["retire_minted"]) == (1, 0)
    cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE augur_id=%s", (live,))
    assert cur.fetchone()[0] == 0                             # 既有活身零 retire 事件(未被強縫)
    cur.execute("SELECT augur_id FROM entity_alias WHERE code_system=%s AND external_code=%s "
                "AND alias_status='provisional'", (_CS, code))
    ghost = cur.fetchone()[0]
    assert ghost != live
    cur.execute("SELECT count(*) FROM identity_lifecycle_event WHERE augur_id=%s "
                "AND event_type='retire'", (ghost,))
    assert cur.fetchone()[0] == 1                             # retire 掛在分身上
    r = resolve.resolve_or_mint(cur, _CS, code, "Security", "test|roster|today", "pytest/p2retire")
    assert r["action"] == "provisional_resolved" and r["augur_id"] == live and r["red_flag"] is True


def test_db_real_delisting_read_shape(cur):
    """下市名冊實讀(沙盒真表):列數>0、evidence 皆為來源列引用形、date 無 NULL(retire valid_time 有據)。"""
    rows = br.read_delisting(cur)
    assert len(rows) > 0
    assert all(ev.startswith(f"TaiwanStockDelisting|stock_id={sid}|date=")
               for sid, _n, _d, ev in rows)
    assert all(d is not None for _s, _n, d, _e in rows)


def test_db_name_mismatch_queue_self_consistent(cur):
    """名實不符佇列自洽:每列下市名確不在該碼今日名冊 max(date) 名集中(誠實計數、不強縫)。"""
    rows = br.name_mismatch_rows(cur)
    for sid, _d, dname, rnames in rows:
        assert dname not in (rnames or "").split("|")
    # 佇列碼皆在今日名冊(由 join 構造保證)——抽驗首列
    if rows:
        cur.execute('SELECT count(*) FROM "TaiwanStockInfo" WHERE stock_id=%s', (rows[0][0],))
        assert cur.fetchone()[0] > 0


def test_db_resolve_alias_tiebreak_deterministic(cur):
    """minors:同交易雙 alias(transaction_time 恆等)→resolve_alias 以 alias_id 破 tie、
    resolution_action ambiguous 回傳確定(=後登錄者)。"""
    import uuid
    from augur.identity import claim, identifier, resolve
    code = f"_p2r_{uuid.uuid4().hex[:10]}"
    a1 = identifier.mint(cur, "Security", _EVID, "pytest/p2retire")
    a2 = identifier.mint(cur, "Security", _EVID, "pytest/p2retire")
    resolve._register_alias(cur, a1, _CS, code, "adopted", _EVID)
    resolve._register_alias(cur, a2, _CS, code, "provisional", _EVID)
    cands = claim.resolve_alias(cur, _CS, code)
    assert [c["augur_id"] for c in cands] == [a1, a2]         # alias_id 單調=登錄序
    assert cands[0]["alias_id"] < cands[1]["alias_id"]
    action, aid = resolution_action([c["augur_id"] for c in cands], set())
    assert (action, aid) == ("ambiguous", a2)                 # 最新者=後登錄、不漂移


# ════════════════════════════════════════════════════════════════════
# (C) 並發層 — 裁① advisory lock 實測(另開真雙連線、同碼)
# ════════════════════════════════════════════════════════════════════


def _connect():
    import psycopg2
    from augur.core import config
    conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    conn.autocommit = False
    return conn


def test_db_advisory_lock_blocks_second_conn(cur):
    """(C1) 雙連線同碼:A 持鎖(交易中)時 B 之 resolve_or_mint 被阻(lock_timeout 逾時=序列化證成),
    全程回滾零殘留——無鎖時此情境即審查親測之雙鑄。"""
    import uuid
    import psycopg2.errors
    from augur.identity import resolve
    code = f"_p2r_{uuid.uuid4().hex[:10]}"
    ca, cb = _connect(), _connect()
    try:
        a = ca.cursor()
        ra = resolve.resolve_or_mint(a, _CS, code, "Security", _EVID, "pytest/lockA")
        assert ra["action"] == "minted"                       # A 交易中:持 per-code 鎖、未 commit
        b = cb.cursor()
        b.execute("SET lock_timeout = '800ms'")
        with pytest.raises(psycopg2.errors.LockNotAvailable):
            resolve.resolve_or_mint(b, _CS, code, "Security", _EVID, "pytest/lockB")
    finally:
        ca.rollback(); ca.close()
        cb.rollback(); cb.close()
    cur.execute("SELECT count(*) FROM entity_alias WHERE code_system=%s AND external_code=%s",
                (_CS, code))
    assert cur.fetchone()[0] == 0                             # 雙側回滾:零殘留


def test_db_advisory_lock_concurrent_single_mint(cur):
    """(C2) 雙連線同碼自然完序:A mint→(B 已在鎖上等)→A commit→B 解析回同枚——恆恰一身(雙鑄防護端到端)。

    ⚠ 須真 commit 方跨連線可見:固定探針碼 _p2r_lockprobe,首跑後沙盒留恰一枚探針身份(有界、冪等、
    誠實揭露);之後每跑 A/B 皆 resolved、零新增。"""
    from augur.identity import resolve
    code = "_p2r_lockprobe"
    results = {}
    a_holding = threading.Event()
    ca, cb = _connect(), _connect()
    try:
        def side_a():
            a = ca.cursor()
            results["a"] = resolve.resolve_or_mint(a, _CS, code, "Security", _EVID, "pytest/lockA")
            a_holding.set()                                   # 已持鎖(交易中、未 commit)
            time.sleep(0.6)                                   # 讓 B 到鎖上等
            ca.commit()

        def side_b():
            a_holding.wait(timeout=10)
            b = cb.cursor()                                   # 阻塞於 per-code 鎖,至 A commit 才續行
            results["b"] = resolve.resolve_or_mint(b, _CS, code, "Security", _EVID, "pytest/lockB")
            cb.commit()

        ta, tb = threading.Thread(target=side_a), threading.Thread(target=side_b)
        ta.start(); tb.start()
        ta.join(timeout=15); tb.join(timeout=15)
        assert not ta.is_alive() and not tb.is_alive()
    finally:
        for c in (ca, cb):
            try:
                c.rollback(); c.close()
            except Exception:  # noqa: BLE001
                pass
    assert results["a"]["augur_id"] == results["b"]["augur_id"]   # 同一枚:B 解析回 A 所鑄/所解
    assert results["b"]["action"] in ("resolved", "provisional_resolved")
    cur.execute("SELECT count(DISTINCT augur_id) FROM entity_alias WHERE code_system=%s "
                "AND external_code=%s", (_CS, code))
    assert cur.fetchone()[0] == 1                             # 恆恰一身(無鎖時=2 之雙鑄已根治)
