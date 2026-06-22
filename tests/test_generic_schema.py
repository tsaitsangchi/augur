"""generic_schema.py 純函數回歸測試（auto-schema 引擎核心；不打 API/DB；clean-room）。

覆蓋型別推導(#5)、主鍵偵測(#6 含 by-date require 防塌陷)、NULL 語意。
順帶記錄 stage 2 已知邊界：非「date」名之日期欄型別只看樣本，樣本不含 sentinel「-1」會誤推 DATE。
"""
import re

from augur.core import generic_schema as gs


# ── NULL / 數字 / 日期 判定 ──
def test_is_null():
    for v in (None, "", "  ", "none", "NULL", "NaN", "nat"):
        assert gs._is_null(v) is True
    for v in ("0", "x", "2026-06-10", 0):
        assert gs._is_null(v) is False

def test_is_num():
    for v in (1, 1.5, "1.5", "-1", "1e5", "-3.14"):
        assert gs._is_num(v) is True
    for v in ("abc", "2026-06-10", "2026/06", True, None):
        assert gs._is_num(v) is False   # bool/日期/含斜線 皆非數字

def test_is_date():
    assert gs._is_date("2026-06-10") is True
    for v in ("2026/06", "2026-6-1", "x", "20260610"):
        assert gs._is_date(v) is False
    # 格式合法但值非法(月/日越界)→ False(2026-06-14 修:防 1911-00-00 等格式對值錯者撞 DATE cast 失敗)
    for v in ("1911-00-00", "2026-13-01", "2026-02-30", "0000-00-00"):
        assert gs._is_date(v) is False


# ── infer_schema 型別推導（#5）──
def test_infer_date_force():
    assert gs.infer_schema([{"date": "2026-06-10"}])["date"] == "DATE"

def test_infer_date_dirty_to_string():
    # FORCE_DATE 但非乾淨 YYYY-MM-DD（如契約月 2026/06）→ 不推 DATE（防塌鍵/cast 錯）
    assert gs.infer_schema([{"date": "2026/06"}])["date"] != "DATE"

def test_infer_numeric():
    assert gs.infer_schema([{"v": "1234.5"}])["v"] == f"NUMERIC({gs.NUMERIC_PRECISION},{gs.NUMERIC_SCALE})"

def test_infer_string():
    assert gs.infer_schema([{"name": "定價"}])["name"] == f"VARCHAR({gs.VARCHAR_LEN})"

def test_infer_force_str_keeps_id_string():
    # stock_id 等識別碼強制字串（免轉數字丟前導零）
    assert gs.infer_schema([{"stock_id": "0050"}])["stock_id"].startswith("VARCHAR")

def test_infer_text_over_255():
    assert gs.infer_schema([{"note": "x" * 300}])["note"] == "TEXT"

def test_infer_date_sentinel_boundary():
    # stage 2 已知邊界：original_return_date 樣本全日期 → 推 DATE…
    assert gs.infer_schema([{"original_return_date": "2026-06-10"}])["original_return_date"] == "DATE"
    # …但樣本含 sentinel「-1」→ 不 all is_date → 退回字串（全量含 -1 時的正解；當前 bug 是樣本未含時誤推 DATE）
    mixed = [{"original_return_date": "2026-06-10"}, {"original_return_date": "-1"}]
    assert gs.infer_schema(mixed)["original_return_date"] != "DATE"


# ── detect_keys 主鍵偵測（#6）──
def test_detect_keys_stock_date():
    rows = [{"stock_id": "2330", "date": "2026-06-09", "v": "1"},
            {"stock_id": "2330", "date": "2026-06-10", "v": "2"},
            {"stock_id": "2317", "date": "2026-06-10", "v": "3"}]
    keys = gs.detect_keys(rows, gs.infer_schema(rows))
    assert "stock_id" in keys and "date" in keys

def test_detect_keys_require_date_bydate_single_day():
    # by-date 單日：stock_id 已唯一 → 原本漏 date；require=('date',) 強制補回防多日 upsert 塌陷
    rows = [{"stock_id": "2330", "date": "2026-06-10", "v": "1"},
            {"stock_id": "2317", "date": "2026-06-10", "v": "2"}]
    keys = gs.detect_keys(rows, gs.infer_schema(rows), require=("date",))
    assert "date" in keys

def test_detect_keys_id_before_date():
    rows = [{"stock_id": "2330", "date": "2026-06-09"},
            {"stock_id": "2330", "date": "2026-06-10"}]
    keys = gs.detect_keys(rows, gs.infer_schema(rows))
    assert keys.index("stock_id") < keys.index("date")

def test_detect_keys_dealer_after_hour_not_volume():
    # Dealer 表:同 (date,dealer_code,futures_id) 有日盤+夜盤 2 筆 → is_after_hour 須入 PK；
    # 否則加完仍不唯一 → 退回全欄 fallback 把 volume 測量值塞進 PK（值一改即對帳 EX≡MIS，2026-06-22 實證）
    rows = [{"date": "2021-04-01", "dealer_code": "F002000", "dealer_name": "元大",
             "futures_id": "TX", "volume": "100", "is_after_hour": "false"},
            {"date": "2021-04-01", "dealer_code": "F002000", "dealer_name": "元大",
             "futures_id": "TX", "volume": "50", "is_after_hour": "true"}]
    keys = gs.detect_keys(rows, gs.infer_schema(rows), require=("date",))
    assert "is_after_hour" in keys
    assert "volume" not in keys and "dealer_name" not in keys


# ── numeric auto-widen（#5 只擴不縮）──
def test_numeric_type_default():
    assert gs._numeric_type(["1.5", "100"]) == f"NUMERIC({gs.NUMERIC_PRECISION},{gs.NUMERIC_SCALE})"

def test_numeric_type_widen_big_int():
    t = gs._numeric_type(["1" * 25])   # 25 位整數，超 precision 20
    p = int(re.search(r"NUMERIC\((\d+),", t).group(1))
    assert p > gs.NUMERIC_PRECISION
