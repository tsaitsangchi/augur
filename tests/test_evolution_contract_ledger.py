"""Phase 5 契約落地之回歸鎖 — 三軸帳本由**同一常數清單**生成,且 live DB 與該清單一致。

為何要兩層(code 層 + live DB 層):`LEDGER_COMMON` 只是 repo 裡的字串,DDL 生成得再對,
**部署過的資料庫可能沒跟上**(2026-07-14 已犯:chk 存在於 live 卻無對應 migration;
教訓＝驗 DB 層宣稱要查 live DB,不能只 grep repo)。故第二層直接對 information_schema 查。

無 DB 時 live 層 skip(非 fail)——CI 無庫仍能跑 code 層。
"""
import pytest

from augur.audit import evolution_ledger_ddl as L

AXES = ("raw", "tw", "lai")
COMMON_COLS = [c for c, _ in L.LEDGER_COMMON]


def _live_cur():
    """回 (cm, cur);連不上回 (None, None)。

    以**真的連連看**判定有無 live DB,不以環境變數名猜(連線參數住 augur.core.config,
    不必然來自 PGDATABASE/PGHOST——用變數名當旗標會讓 live 層在有庫時仍靜默 skip)。

    ⚠ 必須**持有 context manager 物件**再 __enter__:`db.connect().__enter__()` 之 CM 無人引用,
    隨即被 GC → 其 finally 關掉連線 → 下一句就 InterfaceError(2026-07-27 實撞)。
    這正是 `augur.core.heavy_slot` 開頭警告的同一個陷阱,只是這裡是靜默 skip 而非靜默放鎖。
    """
    try:
        from augur.core import db
        cm = db.connect()
        conn = cm.__enter__()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        return cm, cur
    except Exception:  # noqa: BLE001
        return None, None


_CM, _CUR = _live_cur()
needs_db = pytest.mark.skipif(_CUR is None, reason="DB 不可連;live 層 skip")


def test_common_columns_are_single_source():
    """三軸 DDL 之共用欄一律出自 LEDGER_COMMON——任一軸自行加減即紅。"""
    for axis in AXES:
        ddl = L.ledger_ddl(axis)
        for col, spec in L.LEDGER_COMMON:
            assert f"{col} {spec}" in ddl, f"{axis} 軸缺共用欄定義:{col}"


def test_axis_tables_are_distinct():
    """三軸各自成表(I1:判準本體不共用;合併成一表即型別錯誤)。"""
    tables = [L.AXES[a]["table"] for a in AXES]
    assert len(set(tables)) == 3, f"三軸表名應相異:{tables}"


def test_uid_check_shared_but_axis_pinned():
    """uid 格式共用一式,但各軸另以 axis CHECK 釘死自己那個字母(跨軸寫錯表即擋)。"""
    uid_spec = dict(L.LEDGER_COMMON)["iteration_uid"]
    assert "(tw|lai|raw)-[0-9]{8}-r[0-9]{2}" in uid_spec
    for axis in AXES:
        assert f"axis = '{axis}'" in L.ledger_ddl(axis) or f"axis='{axis}'" in L.ledger_ddl(axis), \
            f"{axis} 軸未釘死 axis CHECK"


def test_cross_notify_default_is_inert():
    """佈告欄預設空(I7 零效力):預設值不得是會讓 driver 分支的內容。"""
    spec = dict(L.LEDGER_COMMON)["cross_notify_json"]
    assert "DEFAULT '[]'::jsonb" in spec


@needs_db
def test_live_tables_match_constant_list():
    """**live DB** 三軸帳本實有全部共用欄——repo 對了但庫沒跟上也要紅。"""
    cur = _CUR
    for axis in AXES:
        table = L.AXES[axis]["table"]
        cur.execute("""SELECT column_name FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s""", (table,))
        live = {r[0] for r in cur.fetchall()}
        assert live, f"live DB 無表 {table}"
        missing = [c for c in COMMON_COLS if c not in live]
        assert not missing, f"{table} live 缺共用欄:{missing}"


@needs_db
def test_live_all_tables_exist():
    """ALL_TABLES 每張都真的在 live DB(清單列了卻沒建=宣稱與事實不符)。"""
    cur, missing = _CUR, []
    for t in L.ALL_TABLES:
        cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
        if cur.fetchone()[0] is None:
            missing.append(t)
    assert not missing, f"ALL_TABLES 列了但 live DB 沒有:{missing}"


def test_c7_contract_kinds_and_blacklist():
    """C7 契約:三型齊、黑名單非空、且 claim 上限存在(無上限=可灌爆 brief)。"""
    from augur.audit.evolution_contract import BLACKLIST, MAX_CLAIMS, SCHEMAS
    assert set(SCHEMAS) == {"brief/1", "hint/1", "xnotify/1"}, "契約鍵帶版號(換版=新鍵,不就地改語意)"
    assert len(BLACKLIST) >= 6, "黑名單詞不得被悄悄縮減"
    assert MAX_CLAIMS > 0


def test_c7_rejects_numeric_arrays():
    """brief 不得夾帶數列(那是把面板偷渡給 advisor 的路;I5 語料不互灌)。"""
    from augur.audit.evolution_contract import validate
    bad = {"kind": "brief", "version": 1, "generated_at": "2026-07-27T00:00:00",
           "claims": [{"claim_level": "ledger_fact", "text": "x", "ref": "t:1",
                       "series": [0.1, 0.2, 0.3]}]}
    assert validate(bad, "brief"), "夾帶數列之 brief 應被拒"
