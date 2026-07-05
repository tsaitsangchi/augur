"""RBAC 強制越權迴歸測試(P3,計畫 §7 T1-T18 可單元化子集)— 預設 deny、fail-closed 驗收。

涵蓋:T1(無群組→空集)· T2(super 不濾 domain 仍過 CLEAN)· T3(works 側非 super deny)·
     T12(resolver 不存在/None→fail-closed)· T13(非授權邊界域對非 super deny 之 SQL 形)。
整合型(T6-T10 IDOR/header/session)走 live smoke,非本檔。
守 #5(fail-closed 授權)· 憲章 v1.28.0(RBAC 準則 ii/iii)。
"""
from augur.knowledge import access, corpus
from augur.philosophy import retrieval


# ── clean_item_sql fail-closed 邏輯(純單元、無 DB、無模型)──
def test_clean_item_sql_nonsuper_empty_domains_denies():
    """T1/T13:非 super 且無授權域(None 或空集)→ 'AND false'(預設 deny、非「不濾」)。"""
    frag, params = corpus.clean_item_sql("i", "x", is_super=False, allowed_domains=None)
    assert "AND false" in frag and params == []
    frag2, _ = corpus.clean_item_sql("i", "x", is_super=False, allowed_domains=frozenset())
    assert "AND false" in frag2


def test_clean_item_sql_nonsuper_with_domains_parametrized():
    """非 super 有授權域 → domain = ANY(%s)、**參數化**(開放值不內插、無注入面)。"""
    frag, params = corpus.clean_item_sql("i", "x", is_super=False, allowed_domains={"rd_mgmt"})
    assert "i.domain = ANY(%s::text[])" in frag
    assert params == [["rd_mgmt"]]
    assert "AND false" not in frag


def test_clean_item_sql_super_no_domain_clause():
    """T2:super → 不濾 domain,但仍過 license/entity_type CLEAN。"""
    frag, params = corpus.clean_item_sql("i", "x", is_super=True)
    assert "domain = ANY" not in frag and "AND false" not in frag
    assert "license IN" in frag and "entity_type IN" in frag and params == []


def test_clean_item_sql_returns_tuple_not_str():
    """契約:回 (fragment, params) 二元組(呼叫端 frag,fp = ...);防退回純字串致位置參數地雷。"""
    r = corpus.clean_item_sql("i", "x", is_super=True)
    assert isinstance(r, tuple) and len(r) == 2 and isinstance(r[0], str) and isinstance(r[1], list)


# ── clean_item_sql local_private 擁有者收窄(RBAC 群組建置,§4.5;anti-leakage 命門)──
def test_clean_item_sql_local_private_owner_scoping():
    """local_private＝擁有者收窄(非 domain):非 super+owner→owner_user_id=%s 參數化、**不 domain 收窄**;
    非 super+owner 缺→AND false(deny);super→見全部私有(不加收窄)。跨使用者 fail-closed(#5)。"""
    frag, params = corpus.clean_item_sql("i", "x", access_scope="local_private",
                                         is_super=False, owner_user_id=7)
    assert "x.owner_user_id = %s" in frag and params == [7]
    assert "domain = ANY" not in frag                       # 私有=個人文件、不 domain 收窄
    frag2, p2 = corpus.clean_item_sql("i", "x", access_scope="local_private",
                                      is_super=False, owner_user_id=None)
    assert "AND false" in frag2 and p2 == []                # 無身分 → deny(不外洩)
    frag3, _ = corpus.clean_item_sql("i", "x", access_scope="local_private", is_super=True)
    assert "AND false" not in frag3 and "owner_user_id" not in frag3   # super 見全部私有
    assert "access_scope = 'local_private'" in frag3


# ── resolver fail-closed(DB,但不存在/None 恆 deny、無 DB 狀態假設)──
def test_resolver_failclosed_unknown_and_none():
    """T12:user 不存在/None → (False, ∅)——絕不當 super、絕不吐全庫。"""
    assert access.resolve_allowed_domains(None) == (False, frozenset())
    assert access.resolve_allowed_domains(10**9) == (False, frozenset())


# ── retrieve(works 側):A/B 裁決＝B(憲章 v1.29.0)——公版素養對【登入者】公開、未登入 deny ──
def test_works_side_public_authenticated_deny_unauth():
    """T3(v1.29.0):works=哲學/文學公版素養對所有登入者公開;**未登入(scope=None)→ deny**(fail-closed、
    早於 DB/模型)。已登入→works 公開(非 domain 收窄)之整合驗證見 retrieve_all 非 super→回 Citation(works)。"""
    assert retrieval.retrieve("安全邊際", k=4, scope=None) == []   # 未登入 → deny(不載模型、快)
