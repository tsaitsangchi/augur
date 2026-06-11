"""reconcile.py 純函數回歸測試（不打 API、不依賴 DB；clean-room）。

覆蓋 #7 對帳核心 + 2026-06-11 三修：
- _key/_norm 寬 PK 數值欄配對（GovBank false-negative 修正）
- _is_per_stock（Institutional roster-scoped 判定）
- verdict incomplete（502 容錯：沒比到 ≠ 乾淨）
guard(問題1)/roster 過濾(問題3) 為 reconcile_by_date inline、需 DB mock → 整合測試待補。
"""
from augur.audit import reconcile


# ── _norm 正規化 ──
def test_norm_null_variants_to_none():
    for v in (None, "", "  ", "none", "NULL", "nan", "NaT"):
        assert reconcile._norm(v) is None

def test_norm_numeric_decimal_vs_raw_equal():
    # DB NUMERIC 字串 vs API raw 字串 → 正規化後相等（GovBank 寬 PK 修正核心）
    assert reconcile._norm("1234.000000") == reconcile._norm("1234.0") == 1234.0
    assert reconcile._norm(1234) == 1234.0

def test_norm_string_strip():
    # 非數字字串 → strip（純數字字串會轉 float，故用中文/底線字串測）
    assert reconcile._norm("  定價 ") == "定價"
    assert reconcile._norm(" Foreign_Investor ") == "Foreign_Investor"


# ── _key 用 _norm（寬 PK 含數值欄）──
def test_key_numeric_pk_matches_decimal_vs_raw():
    pk = ["date", "stock_id", "buy_amount"]
    db = {"date": "2026-06-10", "stock_id": "2330", "buy_amount": "1000.000000"}
    api = {"date": "2026-06-10", "stock_id": "2330", "buy_amount": "1000.0"}
    assert reconcile._key(db, pk) == reconcile._key(api, pk)


# ── compare 四類計數 ──
def test_compare_matched_numeric_normalized():
    r = reconcile.compare([{"id": "1", "v": "10.0"}], [{"id": "1", "v": "10.000000"}], ["id"], ["v"])
    assert (r["matched"], r["value_mismatch"], r["missing_in_db"], r["extra_in_db"]) == (1, 0, 0, 0)

def test_compare_value_mismatch_records_example():
    r = reconcile.compare([{"id": "1", "v": "10"}], [{"id": "1", "v": "11"}], ["id"], ["v"])
    assert r["value_mismatch"] == 1 and r["matched"] == 0
    assert r["examples"][0]["col"] == "v"

def test_compare_missing_and_extra():
    # API 有 id=2 DB 無 → missing；DB 有 id=1 API 無 → extra
    r = reconcile.compare([{"id": "1", "v": "x"}], [{"id": "2", "v": "y"}], ["id"], ["v"])
    assert r["missing_in_db"] == 1 and r["extra_in_db"] == 1


# ── _is_per_stock（問題 3 判定）──
def test_is_per_stock_three_cases():
    assert reconcile._is_per_stock(["date", "stock_id", "name"]) is True   # Institutional
    assert reconcile._is_per_stock(["date", "name"]) is False              # TotalInstitutional
    assert reconcile._is_per_stock(["code", "date"]) is False              # FutOptTickInfo


# ── _blank 含 errors 欄（問題 2）──
def test_blank_has_errors_field():
    assert reconcile._blank("T")["errors"] == []


# ── verdict（問題 2：incomplete / errors → 不 pass）──
def _clean():
    return {"matched": 1, "value_mismatch": 0, "extra_in_db": 0, "missing_in_db": 0}

def test_verdict_clean_passes():
    assert reconcile.verdict(_clean())["passed"] is True

def test_verdict_mismatch_fails():
    assert reconcile.verdict({**_clean(), "value_mismatch": 1})["passed"] is False

def test_verdict_extra_fails():
    assert reconcile.verdict({**_clean(), "extra_in_db": 1})["passed"] is False

def test_verdict_incomplete_fails():
    assert reconcile.verdict({**_clean(), "incomplete": True})["passed"] is False

def test_verdict_errors_fails():
    assert reconcile.verdict({**_clean(), "errors": [{"error": "502"}]})["passed"] is False
