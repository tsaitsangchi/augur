"""#8 DB 層隔離硬閘機械測試 — augur_predict role 對素養層零存取(GRANT/REVOKE 閘、擋動態 SQL 旁路)。

🎯 這支在做什麼(白話):A' 隔離雙閘之「DB 層硬保證」機械驗證——`augur.audit.import_isolation` 靜態 AST
   擋不到的**動態 SQL 旁路**(執行期組字串撈素養表),由受限 role `augur_predict` 的 GRANT/REVOKE 於 DB 層擋。
   本測試斷言:預測 role 對 philosophy_/knowledge_/chat_/RBAC/蒸餾**一律 SELECT 拒**(素養不進預測管線 DB 層
   硬擋)、對預測管線表 SELECT 准 + 輸出表可寫。**#8 零容忍:任一 forbidden 表 SELECT 准 = 洩漏 = FAIL。**

   role 未建/DB 不可用 → skip(誠實標「DB 閘未 apply」、非假 pass);setup_predict_role.py --apply 建。
守 #8(anti-leakage:素養層 DB 層硬擋、機械驗非約定)· #1(隔離)· #12(role SSOT=setup_predict_role.py)· #25。
"""
from __future__ import annotations

import psycopg2
import pytest

from augur.core import config

PREDICT_ROLE = "augur_predict"
# 素養層(預測 role 一律 SELECT 拒;洩漏=FAIL)——跨前綴取樣
FORBIDDEN = ["philosophy_work", "philosophy_work_text", "knowledge_item", "knowledge_concordance",
             "knowledge_sentence", "chat_message", "chat_session", "app_user", "advisor_distill_context"]
# 預測管線(SELECT 准)
ALLOWED_READ = ["feature_values", "core_universe_asof", "model_registry", "prediction_values",
                "revalidation_ledger", "judgestop_threshold"]
# 輸出/記錄表(可寫)
WRITABLE = ["prediction_values", "model_registry", "revalidation_ledger", "trial_ledger", "revalidation_verdict"]


@pytest.fixture()
def cur():
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 DB 隔離測試:{e}")
    c = conn.cursor()
    c.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (PREDICT_ROLE,))
    if not c.fetchone():
        conn.close()
        pytest.skip(f"role {PREDICT_ROLE} 未建(DB 隔離硬閘未 apply;setup_predict_role.py --apply --confirm)")
    yield c
    conn.close()


def _has(cur, table, priv):
    """has_table_privilege;表名加引號保大小寫;表不存在回 None(新鮮 DB 該表未建 → 跳)。"""
    cur.execute("SELECT to_regclass(%s)", (table,))
    if cur.fetchone()[0] is None:
        return None
    cur.execute("SELECT has_table_privilege(%s, %s, %s)", (PREDICT_ROLE, f'"{table}"', priv))
    return cur.fetchone()[0]


def test_predict_role_denied_on_erudition_layer(cur):
    """#8 命門:預測 role 對素養層(philosophy/knowledge/chat/RBAC/蒸餾)SELECT 一律拒——任一准=洩漏。"""
    checked = 0
    for t in FORBIDDEN:
        got = _has(cur, t, "SELECT")
        if got is None:
            continue
        checked += 1
        assert got is False, f"#8 洩漏!augur_predict 可 SELECT 素養表 {t}(素養層進了預測管線 DB)"
    assert checked >= 3, f"素養表僅驗到 {checked} 張(<3)、覆蓋不足、不足以宣稱隔離守住(#15)"


def test_predict_role_allowed_on_prediction_pipeline(cur):
    """預測 role 對預測管線表 SELECT 准(GRANT 未過度收=不誤殺預測自身存取)。"""
    for t in ALLOWED_READ:
        got = _has(cur, t, "SELECT")
        if got is None:
            continue
        assert got is True, f"augur_predict 讀不到預測表 {t}(grants 缺、預測管線會斷)"


def test_predict_role_can_write_outputs(cur):
    """預測 role 可寫輸出/記錄表(prediction_values/model_registry/harness ledger)。"""
    for t in WRITABLE:
        got = _has(cur, t, "INSERT")
        if got is None:
            continue
        assert got is True, f"augur_predict 不能寫輸出表 {t}(WRITABLE grants 缺)"
