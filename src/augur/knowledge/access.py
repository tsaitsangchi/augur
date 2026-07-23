"""RBAC 授權解析(resolver)— resolve_allowed_domains(user_id) → (is_super, allowed)。

🎯 這支在做什麼(白話):從 DB 群組授權解析某使用者可讀哪些知識 domain。**嚴格三態、型別分離、fail-closed**:
   superuser → (True, ∅);非 super 有 grant → (False, 群組 grant 聯集);其餘一切(user 不存在/inactive/
   無 grant/DB 拋錯)→ (False, ∅)——**空集＝deny、非不濾;絕不當 super、絕不 raise 到吐全庫**。
   禁「None＝ALL」隱式哨兵(is_super 與 allowed 各自獨立)。只讀 app_user/user_group/group_domain_grant
   三表、**零觸預測表、零觸 philosophy_work**。
   **住 augur.knowledge(隔離 FORBIDDEN 前綴)、禁置 augur.core**——否則預測管線經 core 可達 resolver＝
   開知識→預測旁路、破 #1 命門(test_philosophy_isolation 正向 assert 釘死)。
守 #5(fail-closed 授權)· #1(隔離、resolver 不成知識→預測旁路)· 憲章 v1.28.0(RBAC 準則 iii resolver 語意)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.access              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.access --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from augur.core import db


def resolve_allowed_domains(user_id):
    """回 (is_super: bool, allowed: frozenset[str])。任何異常/查無/inactive/無 grant → (False, frozenset())。"""
    if user_id is None:
        return (False, frozenset())
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            # is_super:單列、無 JOIN、無聚合;查無/inactive → 視為 (False, ∅)
            cur.execute("SELECT is_superuser FROM app_user WHERE user_id = %s AND is_active", (user_id,))
            row = cur.fetchone()
            if row is None:
                return (False, frozenset())
            if row[0]:
                return (True, frozenset())          # superuser:allowed 由 enforcement 忽略
            # 非 super:群組 grant 聯集;FILTER(WHERE ... IS NOT NULL)+COALESCE('{}') 杜絕 {NULL} 誤判
            cur.execute(
                "SELECT COALESCE(array_agg(DISTINCT g.domain) FILTER (WHERE g.domain IS NOT NULL), '{}') "
                "FROM user_group ug JOIN group_domain_grant g USING (group_id) WHERE ug.user_id = %s",
                (user_id,))
            return (False, frozenset(cur.fetchone()[0] or []))
    except Exception:
        return (False, frozenset())                 # fail-closed:DB 錯絕不吐全庫


def _selftest():
    """純紅綠自測(零 IO):驗 user_id=None 之 pure fail-closed 路徑(未觸 DB)+ 隔離/結構不變式。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # None → (False, ∅):此路徑於 db.connect() 前 return,零觸 DB(#5 fail-closed 且純)
    res = resolve_allowed_domains(None)
    chk("None→tuple 二元", isinstance(res, tuple) and len(res) == 2)
    chk("None→is_super=False(絕不當 super)", res[0] is False)
    chk("None→allowed=frozenset()(空集＝deny、非不濾)", res[1] == frozenset() and isinstance(res[1], frozenset))
    # 隔離不變式:resolver 須住 augur.knowledge、禁 augur.core(否則預測經 core 可達＝旁路 #1)
    _mod = __spec__.name if __spec__ else __name__   # -m 執行下 __name__=="__main__",真模組名取 __spec__.name
    chk("模組住 augur.knowledge(隔離前綴)", _mod.startswith("augur.knowledge"))
    chk("非住 augur.core(禁旁路)", not _mod.startswith("augur.core"))
    chk("公開入口 resolve_allowed_domains 存在且可呼", callable(globals().get("resolve_allowed_domains")))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.access --selftest;免 DB 免 API)")
