"""系統 identifier 鑄造與解析 — 世界個體之 augur_id(ID.11-14)。

🎯 這支在做什麼(白話):每一世界個體(某檔股票、某指數、某 FRED 序列)於升級為 Knowledge 前,由系統
   鑄造**恰一枚永久 augur_id**(如 `augur:security/…`、`augur:index/…`、`augur:fred_series/…`),
   繫結恰一 `entity_type` 之個體命名空間(型別化命名空間隔離)。identifier 本身即具 Identity 地位之一級
   物件;**永不刪除**(下市/去識別化以 lifecycle 事件 + status=tombstoned 標記,非 DELETE,見 lifecycle.py)。
   型別值域住 DB(`entity_type_catalog`,#29b 非寫死 CHECK):鑄造前經 catalog 校驗,
   **拒絕把分類節點(binding_kind_default='type',如 T.24 Automobile)當個體 instance 鑄造**、
   **拒絕跨 Type 混用命名空間**(augur_id 前綴須與該型別之 namespace_key 一致)。

DDL 單一權威=scripts/migrate_identity_ddl.py;種子=scripts/seed_entity_type_catalog.py。
守 ID.11(系統鑄造義務)· ID.12(型別化命名空間繫結/隔離)· ID.13(永久性)· ID.14(identifier Identity 地位)·
   #29b(型別值域住 DB)· #18(library 可個別 --selftest)。

⚠ **ID.11 義務結案狀態(誠實揭露 #8):機制就位、義務未結**——本模組提供 mint/resolve,但攝取路徑
   (ingestion/ingest.py、sync.py)現仍以外部碼(stock_id/series_id)直充身份、mint 尚無任一呼叫端。
   ID.11「升級 Knowledge 前必須鑄造系統 identifier」之 runtime 義務**未接線**,不得計為 ID.11 已落實。
   follow-up Phase 5:於攝取准入點強制 resolve-or-mint(外部碼→entity_alias→augur_id)+ 稽核閘偵測
   「未繫 augur_id 之 Knowledge 升級」;接線前於合規聲明揭露本狀態(承接 §緊張關係揭露)。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.identity.identifier              # 印用途+公開入口(唯讀)
  python -m augur.identity.identifier --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations

import uuid


def namespace_ok(augur_id, namespace_key) -> bool:
    """型別化命名空間隔離之純判準(ID.12):augur_id 須為 'augur:{namespace_key}/…' 形。"""
    return isinstance(augur_id, str) and augur_id.startswith(f"augur:{namespace_key}/")


def _catalog(cur, entity_type):
    """讀 entity_type_catalog 一列;未登錄回 None(#29b 型別值域住 DB)。"""
    cur.execute(
        "SELECT entity_type, ont_type_ref, top_category, namespace_key, binding_kind_default "
        "FROM entity_type_catalog WHERE entity_type=%s", (entity_type,))
    r = cur.fetchone()
    if r is None:
        return None
    return {"entity_type": r[0], "ont_type_ref": r[1], "top_category": r[2],
            "namespace_key": r[3], "binding_kind_default": r[4]}


def mint(cur, entity_type, evidence_ref, actor, augur_id=None) -> str:
    """鑄造一枚系統 augur_id 並登錄 entity_registry(ID.11);回 augur_id。

    entity_type 須已登錄於 entity_type_catalog(#29b);binding_kind_default 須為 'instance'
    (分類節點=type 不得鑄造為個體,ID.12/ID.53);augur_id 未給則以 namespace_key 生成、
    給定者須通過命名空間隔離校驗。actor=P4.E6 斷言主體(產生此鑄造之 agent/code 身分)。
    """
    row = _catalog(cur, entity_type)
    if row is None:
        raise ValueError(
            f"未登錄之 entity_type={entity_type!r};先 seed_entity_type_catalog / INSERT 一列"
            "(#29b 型別值域住 DB、非寫死 CHECK)")
    if row["binding_kind_default"] != "instance":
        raise ValueError(
            f"entity_type={entity_type!r} binding_kind_default={row['binding_kind_default']!r}:"
            "分類節點(type)不得鑄造為個體 instance(ID.12/ID.53;如 T.24 Automobile 為 type、"
            "不得列為 Security instance)")
    if not actor:
        raise ValueError("mint 須具 actor(P4.E6 斷言主體)")
    ns = row["namespace_key"]
    aid = augur_id or f"augur:{ns}/{uuid.uuid4().hex}"
    if not namespace_ok(aid, ns):
        raise ValueError(
            f"augur_id={aid!r} 與 entity_type={entity_type!r} 之命名空間 'augur:{ns}/' 不符"
            "(禁跨 Type 混用命名空間;ID.12)")
    cur.execute(
        "INSERT INTO entity_registry (augur_id, entity_type, minted_by, evidence_ref, status) "
        "VALUES (%s, %s, %s, %s, 'active')",
        (aid, entity_type, actor, evidence_ref))
    return aid


def resolve(cur, augur_id):
    """解析 augur_id → entity_registry 一列(dict);不存在回 None。"""
    cur.execute(
        "SELECT augur_id, entity_type, minted_at, minted_by, evidence_ref, status "
        "FROM entity_registry WHERE augur_id=%s", (augur_id,))
    r = cur.fetchone()
    if r is None:
        return None
    return {"augur_id": r[0], "entity_type": r[1], "minted_at": r[2],
            "minted_by": r[3], "evidence_ref": r[4], "status": r[5]}


def _selftest():
    """自測(零 DB/零 API;IO-bound 之 mint/resolve 退為 import-smoke,命名空間隔離純判準紅綠)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("namespace_ok 合命名空間→True", namespace_ok("augur:security/abc", "security"))
    chk("namespace_ok 跨 Type 混用→False", not namespace_ok("augur:index/abc", "security"))
    chk("namespace_ok 裸外部碼(非 augur:)→False", not namespace_ok("2330", "security"))
    chk("namespace_ok 非字串→False", not namespace_ok(None, "security"))
    chk("公開入口皆存在", all(callable(f) for f in (mint, resolve, namespace_ok, _catalog)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.identity.identifier --selftest;免 DB 免 API)")
