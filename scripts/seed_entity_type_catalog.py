#!/usr/bin/env python
"""entity_type_catalog 種子 — 由 ONT Annex T 登錄型別值域(#29b 型別值域住 DB;冪等 upsert)。

🎯 這支在做什麼(白話):把 ONT Annex T(T.1-T.61)之 Type 落為 entity_type_catalog 之值域列——每型別登錄
   ont_type_ref、頂層範疇(Entity/Event/State/Relation/Quantity)、個體命名空間 key、預設 binding(instance/
   type),落實型別化命名空間隔離。**型別值域住 DB(#29b,非寫死 CHECK):新增型別=INSERT/upsert 一列、零改碼**。

⚠ **誠實邊界(#9 零幻像)**:ONT Annex T(T.1-T.61)全文之 SSOT 在**外部 augur-constitution repo、不在本 code
   repo**;本腳本不臆造未經核對之 61 型別對照。SEED 僅登錄「本 code repo 可實證接地」之列:
     · 三個 Phase 1 實際領域(Security/Index/FredSeries),對映本系統 finmind 證券、指數、FRED 序列;
       ont_type_ref 於未經 ONT 核對前留 NULL(欄位 nullable、待 ONT sync 補),不臆造 T.n 編號。
     · 一列分類節點守衛(Automobile,ont_type_ref='T.24'——此對照由結構補正設計卷宗明列、可接地),
       binding_kind_default='type',鎖住「分類節點不得鑄造為個體 instance」禁止型態(identifier.mint 校驗)。
   **完整 T.1-T.61 值域**由人類對照 ONT Annex T 後**逐列 append/upsert 落地**(#29b:INSERT 一列、零改碼),
   或以資料驅動來源(knowledge_source 式)引入;本腳本之 SEED 表即該落地之單一入口與冪等 upsert 引擎。

守 #6(冪等 upsert)· #9(不臆造未核對之型別對照)· #12· #29(個別可執行 + 指令矩陣 + graceful)· #29b(值域住 DB)·
   ID.12(型別化命名空間隔離)· ID.53(instance/type 標記)。

執行指令矩陣:
  python scripts/seed_entity_type_catalog.py            # 冪等 upsert SEED + 印現況
  python scripts/seed_entity_type_catalog.py --check    # 唯讀:只印目前 catalog 現況、不寫入
  python scripts/seed_entity_type_catalog.py --selftest  # 紅綠鎖(SEED 結構不變式;免 DB 免 API)

⚠ 須先跑 migrate_identity_ddl.py 建 entity_type_catalog;未 apply 生產 DB 前僅 --check/--selftest。
"""
import argparse
import sys

import _bootstrap  # noqa: F401

# `from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest 零依賴可個別跑(#29)。

# (entity_type, ont_type_ref, top_category, namespace_key, binding_kind_default, note)
# 僅接地列(見檔頭誠實邊界);完整 T.1-T.61 由人對照 ONT Annex T 後逐列 append。
SEED = [
    ("Security", None, "Entity", "security", "instance",
     "台股個股/有價證券(finmind stock_id 繫此;ont_type_ref 待 ONT Annex T sync 補)"),
    ("Index", None, "Entity", "index", "instance",
     "指數(加權/產業指數等;ont_type_ref 待 ONT sync 補)"),
    ("FredSeries", None, "Entity", "fred_series", "instance",
     "FRED 總經序列(fred series_id 繫此;ont_type_ref 待 ONT sync 補)"),
    ("Automobile", "T.24", "Entity", "automobile", "type",
     "分類節點(禁止型態守衛):type 不得鑄造為個體 instance、不得列為 Security instance(ID.12/ID.53)"),
]

# DO UPDATE 僅補 ont_type_ref/note——**不回溯改寫 namespace_key/binding_kind_default/top_category**
# (issue ID.12:原地改寫使既有 augur_id 之 namespace_ok 失效、或改標已鑄 instance 之型別;DB 端 trg_type_catalog_immutable
#  於有 registry 參照時亦硬擋)。新命名空間/binding 語義須 append 新 entity_type 列(#29b:INSERT 一列、零改碼)。
UPSERT = """
    INSERT INTO entity_type_catalog
        (entity_type, ont_type_ref, top_category, namespace_key, binding_kind_default, note)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (entity_type) DO UPDATE SET
        ont_type_ref = EXCLUDED.ont_type_ref,
        note = EXCLUDED.note
"""


def _show(cur):
    print("── entity_type_catalog 現況 ──")
    try:
        cur.execute(
            "SELECT entity_type, COALESCE(ont_type_ref,'(待 ONT)'), top_category, "
            "namespace_key, binding_kind_default FROM entity_type_catalog ORDER BY entity_type")
        rows = cur.fetchall()
        if not rows:
            print("  (空)")
        for et, ont, cat, ns, bind in rows:
            print(f"  {et:<12} ont={ont:<8} {cat:<8} ns=augur:{ns}/  binding={bind}")
        print(f"  共 {len(rows)} 列")
    except Exception as e:  # noqa: BLE001  表未建
        print(f"  (查詢失敗:{e};先跑 migrate_identity_ddl.py 建表)")


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    cats = {"Entity", "Event", "State", "Relation", "Quantity"}
    binds = {"instance", "type"}
    chk("SEED 每列六元組", all(len(r) == 6 for r in SEED))
    chk("SEED top_category 皆合法", all(r[2] in cats for r in SEED))
    chk("SEED binding 皆合法", all(r[4] in binds for r in SEED))
    chk("SEED entity_type 唯一", len({r[0] for r in SEED}) == len(SEED))
    chk("Automobile 為分類節點(type,禁止型態守衛)",
        any(r[0] == "Automobile" and r[4] == "type" for r in SEED))
    chk("三實際領域為 instance(security/index/fred_series)",
        {r[3] for r in SEED if r[4] == "instance"} == {"security", "index", "fred_series"})
    chk("未臆造 ont_type_ref:instance 列於 ONT 未核對前留 None(#9)",
        all(r[1] is None for r in SEED if r[4] == "instance"))
    chk("UPSERT 為冪等(ON CONFLICT DO UPDATE)", "ON CONFLICT (entity_type) DO UPDATE" in UPSERT)
    chk("UPSERT 不回溯改寫 namespace_key/binding/top_category(ID.12 不變式;僅補 ont_type_ref/note)",
        "namespace_key = EXCLUDED" not in UPSERT
        and "binding_kind_default = EXCLUDED" not in UPSERT
        and "top_category = EXCLUDED" not in UPSERT)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="entity_type_catalog 種子(由 ONT Annex T 登錄型別值域;冪等 upsert;#29b 值域住 DB)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印目前 catalog 現況、不寫入")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(SEED 結構不變式;免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    from augur.core import db  # 延遲載入(psycopg2 僅 upsert 執行/--check 需要)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for row in SEED:
                cur.execute(UPSERT, row)
                print(f"✓ upsert {row[0]}")
        _show(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
