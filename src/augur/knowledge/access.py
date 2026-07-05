"""RBAC 授權解析(resolver)— resolve_allowed_domains(user_id) → (is_super, allowed)。

🎯 這支在做什麼(白話):從 DB 群組授權解析某使用者可讀哪些知識 domain。**嚴格三態、型別分離、fail-closed**:
   superuser → (True, ∅);非 super 有 grant → (False, 群組 grant 聯集);其餘一切(user 不存在/inactive/
   無 grant/DB 拋錯)→ (False, ∅)——**空集＝deny、非不濾;絕不當 super、絕不 raise 到吐全庫**。
   禁「None＝ALL」隱式哨兵(is_super 與 allowed 各自獨立)。只讀 app_user/user_group/group_domain_grant
   三表、**零觸預測表、零觸 philosophy_work**。
   **住 augur.knowledge(隔離 FORBIDDEN 前綴)、禁置 augur.core**——否則預測管線經 core 可達 resolver＝
   開知識→預測旁路、破 #1 命門(test_philosophy_isolation 正向 assert 釘死)。
守 #5(fail-closed 授權)· #1(隔離、resolver 不成知識→預測旁路)· 憲章 v1.28.0(RBAC 準則 iii resolver 語意)。
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
