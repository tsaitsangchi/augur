"""生產特徵集讀契約 — PME prodset → 預測熱路徑允許清單（唯讀、禁 philosophy import）。

🎯 這支在做什麼（白話）：從 `evolution_production_feature_set` 讀 `set_status=active`
   特徵名，再與 `feature_values` 跨 panel 覆蓋取交集，供 train／predict 當允許清單。
   住 `augur.core` 讓 PIPELINE／scripts 可 import，**不**經 `augur.philosophy`（AST 閘）。
   空 active → 呼叫端 fail-closed（FC-empty）；**不**回退全量 canonical。
   ≠可交易／確立級；零 FinMind／FRED。

守 #1(真讀 DB)· #8(anti-leakage：素養不進管線 import)· #12(讀側 SSOT)· #15(n_feats 誠實)· #18。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.core.prodset_contract              # 印用途+公開入口（唯讀）
  python -m augur.core.prodset_contract --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from augur.core import db

PRODSET_TABLE = "evolution_production_feature_set"
PRODSET_ACTIVE = "active"
PRODSET_REMOVED = "removed"
FEATURE_TABLE = "feature_values"
# 覆蓋起點＝evaluation.baseline.CANONICAL_START 同值（core 不反向 import evaluation）
CANONICAL_START = "2008-12-31"

FEATURE_SOURCE_PRODSET = "prodset"
FEATURE_SOURCE_CANONICAL = "canonical"
FEATURE_SOURCES = (FEATURE_SOURCE_PRODSET, FEATURE_SOURCE_CANONICAL)


class ProdsetEmptyError(RuntimeError):
    """prodset active 為空（FC-empty）；禁 fallback canonical。"""


def load_active_features(conn) -> list[str]:
    """SELECT feature WHERE set_status=active → 排序 list（可空）。"""
    with db.transaction(conn) as cur:
        cur.execute(
            f"SELECT feature FROM {PRODSET_TABLE} WHERE set_status=%s ORDER BY feature",
            (PRODSET_ACTIVE,),
        )
        return [r[0] for r in cur.fetchall()]


def covered_features(conn, panel_dates) -> list[str]:
    """在 CANONICAL_START 起每個 panel 皆出現於 feature_values 之特徵（嚴格交集；canonical 同構）。"""
    pds = [p for p in panel_dates if str(p) >= CANONICAL_START]
    if not pds:
        return []
    with db.transaction(conn) as cur:
        cur.execute(
            f"SELECT feature FROM {FEATURE_TABLE} WHERE panel_date = ANY(%s) "
            f"GROUP BY feature HAVING count(DISTINCT panel_date) = %s",
            (pds, len(pds)),
        )
        return sorted(r[0] for r in cur.fetchall())


def resolve_prodset_feats(conn, panel_dates, *, require_nonempty: bool = False) -> list[str]:
    """feats = sorted(active ∩ 於 panel 窗至少出現一次)。

    不用「全 panel 嚴格交集」當 prodset 預設——晉升特徵常短於 CANONICAL_START 全史，
    嚴格交集會把合法 active 誤殺成空集再誘使假寬 fallback。缺列 panel 由 _fold_xy／_panel_matrix
    自然跳過。require_nonempty 且空 active → ProdsetEmptyError。
    """
    active = load_active_features(conn)
    if require_nonempty and not active:
        raise ProdsetEmptyError("prodset empty: no active features in evolution_production_feature_set")
    if not active:
        return []
    pds = [p for p in panel_dates if str(p) >= CANONICAL_START]
    if not pds:
        return []
    with db.transaction(conn) as cur:
        cur.execute(
            f"SELECT DISTINCT feature FROM {FEATURE_TABLE} "
            f"WHERE panel_date = ANY(%s) AND feature = ANY(%s)",
            (pds, list(active)),
        )
        covered = {r[0] for r in cur.fetchall()}
    return sorted(f for f in active if f in covered)


def _selftest() -> int:
    """零 DB／零 API：常數＋公開契約回歸鎖。"""
    import inspect
    import pathlib

    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("表名常數=evolution_production_feature_set", PRODSET_TABLE == "evolution_production_feature_set")
    chk("status 常數 active/removed", PRODSET_ACTIVE == "active" and PRODSET_REMOVED == "removed")
    chk("CANONICAL_START=2008-12-31", CANONICAL_START == "2008-12-31")
    chk("FEATURE_SOURCES 含 prodset/canonical",
        FEATURE_SOURCE_PRODSET in FEATURE_SOURCES and FEATURE_SOURCE_CANONICAL in FEATURE_SOURCES)
    chk("公開入口 callable",
        all(callable(f) for f in (load_active_features, covered_features, resolve_prodset_feats)))
    sig = inspect.signature(resolve_prodset_feats)
    chk("resolve_prodset_feats 含 require_nonempty", "require_nonempty" in sig.parameters)
    chk("ProdsetEmptyError 為 RuntimeError 子類", issubclass(ProdsetEmptyError, RuntimeError))
    import ast
    import pathlib
    text = pathlib.Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(text)
    bad_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name == "augur.philosophy" or n.name.startswith("augur.philosophy."):
                    bad_imports.append(n.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "augur.philosophy" or node.module.startswith("augur.philosophy."):
                bad_imports.append(node.module)
    chk("本檔 AST 零 import augur.philosophy", bad_imports == [])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("公開入口: load_active_features / covered_features / resolve_prodset_feats")
    print("(自測: python -m augur.core.prodset_contract --selftest; 免 DB 免 API)")
