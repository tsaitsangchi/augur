"""augur 世界概念解析 — 消費端只認「世界概念鍵」，供應商表名字面只活在 DB 資料列。

🎯 這支在做什麼（白話）：
消費模組想讀「台股日 K」時，不再寫死供應商表名，而是問這支「`tw.daily_bar` 的權威表徵在哪？」
本支查 World Concept Registry 二表（`world_concept_registry` 概念主表 → 欄 4 權威表徵指定 →
`world_channel_binding` 通道映射列），回一個 `Binding(表, 欄, 角色)`。
**解析不出來就拋例外、絕不靜默回退成 vendor 字面**——這是本支存在的全部理由：
unmapped／未指定權威表徵之通道，其資料僅具 Observation 地位（WM.35），不得被消費為
Representation 或 Knowledge 之依據；靜默回退＝把不得消費的東西餵進生產鏈，比報錯壞得多。

守原則 #15（fail-closed：不可解析即拋，機制若壞了不得安靜變綠燈）· #9/#10（表徵逐欄出自 DB 列、
可 trace 回 registry binding_id）· #12（vendor 字面單一住所＝`world_channel_binding`，本檔零字面）·
#18（library 白話標頭＋自測 CLI）· #29(b)（映射是資料、住 DB，不寫死 Python dict）· #35（回歸鎖三規則）。

條文錨（specs/WORLD-MODEL-SPECIFICATION.md）
--------------------------------------------
  WM.36:344-358  Registry 為一級結構、登錄七欄；**消費模組對世界事實之引用必須以世界概念為鍵、
                 經 Registry 解析至權威表徵，不得以來源位置字面（表名/欄名/series 識別碼）直接繫結**；
                 自補正期到期日翌日（2026-10-15，RULING-2026-030:81）起無條件適用。
  WM.35:336-340  unmapped＝顯式合法過渡態；unmapped／未登錄通道之資料**僅具 Observation 地位**
                 （得保存、對帳、追溯，不得被消費）→ 本支對此一律拋 `UnmappedConcept`。
  WM.14          權威表徵恰解析至一 → `authoritative_binding_id` NULL 或多重命中皆拒。
  WM.13/WM.25    版本化：現行列＝`superseded_at IS NULL`；已 supersede 之概念／通道不得再被解析。
設計 SSOT＝reports/wm3536_vendor_registry_plan_20260802.md §5 表列 2（G0 2026-08-02 拍板讀法乙）。

公開入口
--------
  resolve(key)         → Binding（權威表徵；不可解析即拋）
  resolve_many(keys)   → {key: Binding}（**任一不可解析即整批拋**，不部分回傳）
  assert_mapped(*keys) → None（消費前置斷言；不可解析即拋）
  resolve_sql(key)     → 引號表名字面，供 f-string 組 SQL（識別碼白名單，不合法即拒）
  concepts_for_table() → 反查某供應商表服務哪些概念（一對多故回 tuple；絞殺工具用）
  load_registry()      → Registry 快照（模組級快取；`clear_cache()` 清）

邊界：**唯讀**——本支不寫 registry、不建表（DDL＝scripts/migrate_world_concept_registry_ddl.py）、
不代填 decided_by（採認＝Steward 附卷裁定，hugo 親簽）。

執行指令矩陣（本檔＝library #18；--selftest 免 DB 免 API 零 usage）
------------
  python -m augur.catalog.world_concept                      # 印用途＋公開入口（唯讀；DB 可達則附現況）
  python -m augur.catalog.world_concept --check              # 逐概念列印可否解析（唯讀；不可解析誠實列 ✗）
  python -m augur.catalog.world_concept --resolve tw.daily_bar   # 解析單鍵（唯讀；失敗印例外訊息、rc=1）
  python -m augur.catalog.world_concept --selftest           # 純紅綠自測（餵真列形 fixture、零 IO）
"""
from __future__ import annotations

import re
from typing import Iterable, Mapping, NamedTuple, Optional, Sequence

CONCEPT_TABLE = "world_concept_registry"
BINDING_TABLE = "world_channel_binding"

CONCEPT_COLS = ("concept_key", "category", "authoritative_binding_id", "superseded_at")
BINDING_COLS = ("binding_id", "concept_key", "source_table", "source_column",
                "channel_role", "mapping_status", "superseded_at")

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class WorldConceptError(Exception):
    """解析失敗之基底——呼叫端 catch 這個即涵蓋全部 fail-closed 情形。"""


class UnknownConcept(WorldConceptError):
    """概念鍵不在 Registry（或其現行列已被 supersede）。"""


class UnmappedConcept(WorldConceptError):
    """概念在、但無可消費之權威表徵（未指定／通道 unmapped／通道已 supersede）＝WM.35 僅 Observation 地位。"""


class RegistryIntegrityError(WorldConceptError):
    """Registry 自身不一致（權威指定落空／現行列非恰一／表名不合法）——寧可拒也不猜。"""


class Binding(NamedTuple):
    """權威表徵（WM.36 欄 3＋欄 4 之解析結果）。`column` 為 None＝表級暫登（plan §9 Q5）。"""
    concept_key: str
    binding_id: int
    table: str
    column: Optional[str]
    role: str


class Registry(NamedTuple):
    """二表快照（唯讀）——解析全程只讀這個，故所有解析邏輯皆為純函式可餵 fixture。"""
    concepts: tuple
    bindings: tuple


# ── 純函式核心（#35(1) 餵真列形 fixture 即可紅綠雙向；無任何 vendor 字面、無任何回退預設）──
def current(rows: Iterable[Mapping]) -> list:
    """濾出現行列（WM.13/WM.25：`superseded_at IS NULL`）。已 supersede 之列不得參與解析。"""
    return [r for r in rows if r.get("superseded_at") is None]


def resolve_rows(concept_key: str, concept_rows: Sequence[Mapping],
                 binding_rows: Sequence[Mapping]) -> Binding:
    """由二表列解析權威表徵。純函式；六種不可消費情形一律拋，**無回退分支**。

    拒絕清單（逐條對應條文）：
      · 無現行概念列          → UnknownConcept（鍵不存在或已 supersede）
      · 現行概念列非恰一      → RegistryIntegrityError（append-only 修訂列並存時之保護，WM.14 恰一）
      · authoritative 為 NULL → UnmappedConcept（WM.14 欄 4 未指定＝WM.35 僅 Observation 地位）
      · 權威指定落空/多命中   → RegistryIntegrityError
      · 權威通道已 supersede  → UnmappedConcept
      · 通道 mapping_status≠mapped 或掛在別的概念 → UnmappedConcept / RegistryIntegrityError
    """
    hits = [r for r in current(concept_rows) if r.get("concept_key") == concept_key]
    if not hits:
        raise UnknownConcept(
            f"世界概念 {concept_key!r} 無現行登錄列——未登錄或已 supersede；"
            f"不得以供應商表名字面代替（WM.36:356）。先登錄 {CONCEPT_TABLE}。")
    if len(hits) > 1:
        raise RegistryIntegrityError(
            f"世界概念 {concept_key!r} 現行列 {len(hits)} 筆（應恰一，WM.14）——"
            "修訂列並存時須以 superseded_at 標舊列；解析拒絕在多重現行列上猜。")
    concept = hits[0]
    bid = concept.get("authoritative_binding_id")
    if bid is None:
        raise UnmappedConcept(
            f"世界概念 {concept_key!r} 未指定權威表徵（{CONCEPT_TABLE}.authoritative_binding_id IS NULL）"
            "——其通道資料僅具 Observation 地位，得保存/對帳/追溯，**不得被消費為 Representation 或 "
            "Knowledge 之依據**（WM.35:338）。採認＝Steward 附卷裁定，非本支可代決。")
    matched = [b for b in binding_rows if b.get("binding_id") == bid]
    if len(matched) != 1:
        raise RegistryIntegrityError(
            f"世界概念 {concept_key!r} 之權威指定 binding_id={bid} 命中 {len(matched)} 列（應恰一）——"
            f"{BINDING_TABLE} 資料不一致，拒絕解析。")
    b = matched[0]
    if b.get("superseded_at") is not None:
        raise UnmappedConcept(
            f"世界概念 {concept_key!r} 之權威通道 binding_id={bid} 已 supersede——"
            "權威指定須改指現行通道列後才可消費（WM.25）。")
    if b.get("mapping_status") != "mapped":
        raise UnmappedConcept(
            f"世界概念 {concept_key!r} 之權威通道 binding_id={bid} 為 "
            f"{b.get('mapping_status')!r}——unmapped 通道僅具 Observation 地位（WM.35:338）。")
    if b.get("concept_key") != concept_key:
        raise RegistryIntegrityError(
            f"權威通道 binding_id={bid} 掛在概念 {b.get('concept_key')!r}，"
            f"與被解析之 {concept_key!r} 不符——拒絕跨概念解析。")
    table = b.get("source_table")
    if not table:
        raise RegistryIntegrityError(f"權威通道 binding_id={bid} 之 source_table 為空——拒絕組 SQL。")
    return Binding(concept_key, bid, table, b.get("source_column"), b.get("channel_role"))


def quote_ident(name) -> str:
    """識別碼白名單＋加引號（純函式）。不合白名單即拒——registry 資料列亦不得成為注入面。"""
    if not isinstance(name, str) or not _IDENT.match(name):
        raise RegistryIntegrityError(f"識別碼不合法，拒絕組 SQL：{name!r}")
    return '"' + name + '"'


def concepts_for_table_rows(source_table: str, binding_rows: Sequence[Mapping]) -> tuple:
    """反查：某供應商表之現行通道列服務哪些世界概念（純函式）。

    一對多（WM.36 欄 3 明文）故回 tuple——例：同一下市通道同時服務成員資格與下市兩概念。
    回空 tuple＝該表未登錄或全為 unmapped ⇒ 其資料僅具 Observation 地位。
    """
    return tuple(sorted({b["concept_key"] for b in current(binding_rows)
                         if b.get("source_table") == source_table and b.get("concept_key")}))


def unresolved(concept_rows: Sequence[Mapping], binding_rows: Sequence[Mapping]) -> list:
    """→ [(concept_key, 例外訊息)]，逐概念試解析（純函式）。供 --check 誠實列紅、絞殺前置盤點。"""
    out = []
    for r in sorted(current(concept_rows), key=lambda x: x.get("concept_key") or ""):
        key = r.get("concept_key")
        try:
            resolve_rows(key, concept_rows, binding_rows)
        except WorldConceptError as e:
            out.append((key, str(e)))
    return out


# ── DB 面（唯讀；快取一份快照，解析全走純函式）──
_CACHE: Optional[Registry] = None


def _fetch(conn) -> Registry:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {', '.join(CONCEPT_COLS)} FROM {CONCEPT_TABLE}")
        concepts = tuple(dict(zip(CONCEPT_COLS, row)) for row in cur.fetchall())
        cur.execute(f"SELECT {', '.join(BINDING_COLS)} FROM {BINDING_TABLE}")
        bindings = tuple(dict(zip(BINDING_COLS, row)) for row in cur.fetchall())
    return Registry(concepts, bindings)


def load_registry(conn=None, refresh: bool = False) -> Registry:
    """讀二表快照（模組級快取）。表不存在／連不上一律轉 `RegistryIntegrityError`（不回空快照假裝有）。"""
    global _CACHE
    if _CACHE is not None and not refresh:
        return _CACHE
    from augur.core import db
    try:
        if conn is not None:
            snap = _fetch(conn)
        else:
            with db.connect() as own:
                snap = _fetch(own)
    except WorldConceptError:
        raise
    except Exception as e:  # noqa: BLE001 — 讀不到 registry 一律 fail-closed，不得退成空快照
        raise RegistryIntegrityError(
            f"讀取 World Concept Registry 失敗（{type(e).__name__}: {e}）——"
            "二表是否已 migrate？先跑 scripts/migrate_world_concept_registry_ddl.py --check") from e
    _CACHE = snap
    return snap


def clear_cache() -> None:
    """清模組級快照快取（registry 改動後、或長跑程序需重讀時呼叫）。"""
    global _CACHE
    _CACHE = None


def _snap(conn, snapshot: Optional[Registry]) -> Registry:
    return snapshot if snapshot is not None else load_registry(conn)


def resolve(concept_key: str, conn=None, snapshot: Optional[Registry] = None) -> Binding:
    """世界概念鍵 → 權威表徵。不可解析即拋 `WorldConceptError`（**永不回退 vendor 字面**）。"""
    s = _snap(conn, snapshot)
    return resolve_rows(concept_key, s.concepts, s.bindings)


def resolve_many(concept_keys: Iterable[str], conn=None,
                 snapshot: Optional[Registry] = None) -> dict:
    """批量解析。**任一不可解析即整批拋**——部分回傳會誘使呼叫端對缺項回退字面。"""
    s = _snap(conn, snapshot)
    return {k: resolve_rows(k, s.concepts, s.bindings) for k in concept_keys}


def assert_mapped(*concept_keys: str, conn=None, snapshot: Optional[Registry] = None) -> None:
    """消費前置斷言：全部可解析則靜默返回，否則拋（訊息含首個不可解析之原因）。"""
    resolve_many(concept_keys, conn=conn, snapshot=snapshot)


def resolve_sql(concept_key: str, conn=None, snapshot: Optional[Registry] = None) -> str:
    """→ 引號表名字面，供 f-string 組 SQL：`f'SELECT ... FROM {resolve_sql("tw.daily_bar")}'`。"""
    return quote_ident(resolve(concept_key, conn=conn, snapshot=snapshot).table)


def concepts_for_table(source_table: str, conn=None,
                       snapshot: Optional[Registry] = None) -> tuple:
    """反查某供應商表服務之世界概念（一對多回 tuple；絞殺工具據此把舊直綁對應到概念鍵）。"""
    return concepts_for_table_rows(source_table, _snap(conn, snapshot).bindings)


# ── 紅綠自測（#35：純函式餵真列形 fixture／輸入側突變驗紅／零字面斷言；免 DB 免 API）──
def _fixture() -> Registry:
    """真列形 fixture——欄名與型別取自 live 二表（2026-08-02 唯讀親驗之列形，值為真值）。

    live 現況：六概念 authoritative_binding_id 全 NULL、通道 98 列（mapped 10/unmapped 88）。
    """
    concepts = (
        {"concept_key": "tw.daily_bar", "category": "event",
         "authoritative_binding_id": None, "superseded_at": None},
        {"concept_key": "tw.delisting", "category": "event",
         "authoritative_binding_id": 3, "superseded_at": None},
        {"concept_key": "tw.roster_membership", "category": "state",
         "authoritative_binding_id": None, "superseded_at": None},
    )
    bindings = (
        {"binding_id": 75, "concept_key": "tw.daily_bar", "source_table": "TaiwanStockPrice",
         "source_column": None, "channel_role": "observation",
         "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 81, "concept_key": "tw.daily_bar", "source_table": "TaiwanStockPriceAdj",
         "source_column": None, "channel_role": "derived",
         "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 2, "concept_key": "tw.roster_membership",
         "source_table": "TaiwanStockDelisting", "source_column": None,
         "channel_role": "observation", "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 3, "concept_key": "tw.delisting", "source_table": "TaiwanStockDelisting",
         "source_column": None, "channel_role": "observation",
         "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 90, "concept_key": None, "source_table": "TaiwanStockNews",
         "source_column": None, "channel_role": "observation",
         "mapping_status": "unmapped", "superseded_at": None},
    )
    return Registry(concepts, bindings)


def _with_concept(snap: Registry, key: str, **patch) -> Registry:
    """回一份把某概念列逐欄覆寫過的新快照（輸入側突變之工具；不改原 fixture）。"""
    out = tuple({**c, **patch} if c["concept_key"] == key else c for c in snap.concepts)
    return Registry(out, snap.bindings)


def _with_binding(snap: Registry, bid: int, **patch) -> Registry:
    out = tuple({**b, **patch} if b["binding_id"] == bid else b for b in snap.bindings)
    return Registry(snap.concepts, out)


def _raised(fn, exc=WorldConceptError):
    """跑 fn：拋 exc → True；正常返回 → False（**回退字面之實作會在此變 False ⇒ 紅**）。"""
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    fx = _fixture()

    # (1) 綠：權威指定齊備 → 逐欄等於 fixture 之權威列（非「有回傳就算過」）
    b = resolve("tw.delisting", snapshot=fx)
    chk("mapped＋權威指定 → 解析成功且逐欄等於該 binding 列",
        b == Binding("tw.delisting", 3, "TaiwanStockDelisting", None, "observation"))

    # (2) 資料驅動之鎖：同一鍵改指另一通道，解析結果必須跟著變
    #     （若實作內建 concept→表 對照表或回退字面，這條回舊值 ⇒ 紅）
    fx_adj = _with_concept(fx, "tw.daily_bar", authoritative_binding_id=81)
    fx_raw = _with_concept(fx, "tw.daily_bar", authoritative_binding_id=75)
    chk("權威指定改指衍生通道 → 表/角色隨資料變（證明真讀列、非內建對照）",
        resolve("tw.daily_bar", snapshot=fx_adj) ==
        Binding("tw.daily_bar", 81, "TaiwanStockPriceAdj", None, "derived")
        and resolve("tw.daily_bar", snapshot=fx_raw).table == "TaiwanStockPrice")

    # (3)–(9) 紅：七種不可消費情形一律拋，且**無任何回傳值**
    chk("authoritative NULL → 拋 UnmappedConcept（WM.35 僅 Observation 地位；live 現況即此）",
        _raised(lambda: resolve("tw.daily_bar", snapshot=fx), UnmappedConcept))
    chk("未知鍵 → 拋 UnknownConcept（不得回退 vendor 字面）",
        _raised(lambda: resolve("tw.not_registered", snapshot=fx), UnknownConcept))
    chk("概念列已 supersede（無現行列）→ 拋 UnknownConcept",
        _raised(lambda: resolve("tw.delisting", snapshot=_with_concept(
            fx, "tw.delisting", superseded_at="2026-08-02")), UnknownConcept))
    chk("權威通道已 supersede → 拋 UnmappedConcept",
        _raised(lambda: resolve("tw.delisting", snapshot=_with_binding(
            fx, 3, superseded_at="2026-08-02")), UnmappedConcept))
    chk("權威指定落空（指向不存在之 binding_id）→ 拋 RegistryIntegrityError",
        _raised(lambda: resolve("tw.delisting", snapshot=_with_concept(
            fx, "tw.delisting", authoritative_binding_id=99999)), RegistryIntegrityError))
    chk("權威通道掛在別的概念 → 拋 RegistryIntegrityError（拒跨概念解析）",
        _raised(lambda: resolve("tw.delisting", snapshot=_with_concept(
            fx, "tw.delisting", authoritative_binding_id=2)), RegistryIntegrityError))
    chk("權威通道為 unmapped → 拋 UnmappedConcept",
        _raised(lambda: resolve("tw.delisting", snapshot=_with_binding(
            fx, 3, mapping_status="unmapped", concept_key=None)), UnmappedConcept))

    # (10) append-only 修訂列並存（PK 呈案甲案之前瞻鎖）：現行列非恰一 → 拒絕在多重現行列上猜
    dup = Registry(fx.concepts + ({"concept_key": "tw.delisting", "category": "event",
                                   "authoritative_binding_id": 2, "superseded_at": None},),
                   fx.bindings)
    chk("同鍵兩筆現行列 → 拋 RegistryIntegrityError（WM.14 恰一；append-only 修訂之保護）",
        _raised(lambda: resolve("tw.delisting", snapshot=dup), RegistryIntegrityError))

    # (11) 批量／斷言：任一失敗即整批拋，不部分回傳
    chk("resolve_many 全可解析 → 逐鍵等於單筆解析",
        resolve_many(["tw.delisting"], snapshot=fx) == {"tw.delisting": b})
    chk("resolve_many 含不可解析鍵 → 整批拋（不部分回傳、不誘發回退）",
        _raised(lambda: resolve_many(["tw.delisting", "tw.daily_bar"], snapshot=fx)))
    chk("assert_mapped 可解析 → 靜默返回 None",
        assert_mapped("tw.delisting", snapshot=fx) is None)
    chk("assert_mapped 不可解析 → 拋",
        _raised(lambda: assert_mapped("tw.daily_bar", snapshot=fx)))

    # (12) 組 SQL 面：識別碼白名單＋解析失敗不得產出任何字面
    chk("resolve_sql → 引號表名（＝quote_ident(權威表)）",
        resolve_sql("tw.delisting", snapshot=fx) == quote_ident("TaiwanStockDelisting"))
    chk("resolve_sql 對不可解析鍵 → 拋（**不得回傳任何表名字面**）",
        _raised(lambda: resolve_sql("tw.daily_bar", snapshot=fx)))
    chk("quote_ident 拒注入形（引號/分號/空白/空字串/非字串）",
        all(_raised(lambda v=v: quote_ident(v), RegistryIntegrityError)
            for v in ('x"; DROP TABLE y --', "a b", "", None, 1, "1abc")))
    chk("quote_ident 收合法識別碼（大小寫皆可）",
        quote_ident("fred_series") == '"fred_series"' and len(quote_ident("A")) == 3)

    # (13) 反查（絞殺工具之入口）：一對多、unmapped 不算
    chk("concepts_for_table：一表服務兩概念 → 兩鍵（WM.36 欄 3 一對多）",
        concepts_for_table("TaiwanStockDelisting", snapshot=fx) ==
        ("tw.delisting", "tw.roster_membership"))
    chk("concepts_for_table：unmapped 表 → 空（僅 Observation 地位，不可作解析入口）",
        concepts_for_table("TaiwanStockNews", snapshot=fx) == ()
        and concepts_for_table("NotInRegistry", snapshot=fx) == ())
    chk("concepts_for_table：已 supersede 之通道列不列入",
        concepts_for_table("TaiwanStockDelisting",
                           snapshot=_with_binding(fx, 2, superseded_at="2026-08-02")) ==
        ("tw.delisting",))

    # (14) --check 之資料面：live 現況（authoritative 全 NULL）必須誠實列為不可解析
    unres = dict(unresolved(fx.concepts, fx.bindings))
    chk("unresolved：權威未指定之概念被列出、已指定者不列（--check 誠實紅之依據）",
        set(unres) == {"tw.daily_bar", "tw.roster_membership"})

    # (15) 快取語意：clear_cache 後不得殘留舊快照（長跑程序讀到過期 registry ＝ 默改風險）
    global _CACHE
    _CACHE = fx
    clear_cache()
    chk("clear_cache 後快取為空（不殘留過期 registry）", _CACHE is None)

    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def _print_entries() -> None:
    print(__doc__.split("公開入口")[0].strip())
    print("\n公開入口：resolve / resolve_many / assert_mapped / resolve_sql / "
          "concepts_for_table / load_registry / clear_cache（全唯讀）")
    print("例外：WorldConceptError ← UnknownConcept / UnmappedConcept / RegistryIntegrityError")
    print(__doc__.split("執行指令矩陣")[-1].split("------------\n")[-1])


def _check(conn=None) -> int:
    snap = load_registry(conn, refresh=True)
    n_map = sum(1 for b in current(snap.bindings) if b.get("mapping_status") == "mapped")
    print(f"── Registry 現況：概念 {len(current(snap.concepts))} 現行列／"
          f"通道 {len(current(snap.bindings))} 現行列（mapped {n_map}）──")
    bad = dict(unresolved(snap.concepts, snap.bindings))
    for r in sorted(current(snap.concepts), key=lambda x: x["concept_key"]):
        key = r["concept_key"]
        if key in bad:
            print(f"  ✗ {key}：{bad[key].split('——')[0]}")
        else:
            b = resolve_rows(key, snap.concepts, snap.bindings)
            print(f"  ✓ {key} → {b.table}"
                  f"{'.' + b.column if b.column else ''}（{b.role}, binding_id={b.binding_id}）")
    if bad:
        print(f"  ⚠ {len(bad)}/{len(current(snap.concepts))} 概念尚不可消費——"
              "消費端呼叫 resolve() 會 fail-closed 拋例外（這是正確行為，非 bug）。")
    return 0


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="世界概念解析 API（WM.35/36；唯讀）")
    ap.add_argument("--check", action="store_true", help="逐概念列印可否解析（唯讀）")
    ap.add_argument("--resolve", metavar="CONCEPT_KEY", help="解析單一世界概念鍵（唯讀）")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測（免 DB 免 API）")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.resolve:
        try:
            print(resolve(a.resolve))
        except WorldConceptError as e:
            print(f"✗ {type(e).__name__}: {e}")
            return 1
        return 0
    if a.check:
        return _check()
    _print_entries()
    try:
        return _check()
    except WorldConceptError as e:  # 無參數須 graceful（#29a 同精神）
        print(f"（現況需 DB；現不可達：{e}）\n（--selftest 免 DB 可跑）")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
