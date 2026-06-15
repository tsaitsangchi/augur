"""ingest.py 純函數測試 — #4 intraday 守門 + aggregate-daily 聚合(GoldPrice intraday→日級)。不打 API/DB。"""
from augur.ingestion import ingest


def test_is_intraday():
    assert ingest.is_intraday("TaiwanStockKBar") is True       # sub-day、#4 不收
    assert ingest.is_intraday("TaiwanStockPrice") is False


def test_aggregate_daily_close():
    # intraday(每日多筆)→ 每日末筆(date 字串最大=最晚時間);date 規約純日級
    rows = [
        {"date": "2026-06-11 00:00:00", "Price": 4049.59},
        {"date": "2026-06-11 23:05:00", "Price": 4219.54},   # 末筆
        {"date": "2026-06-12 00:00:00", "Price": 4200.00},
        {"date": "2026-06-12 22:05:00", "Price": 4218.68},   # 末筆
        {"date": "1995-06-01", "Price": 383.50},             # 早期已日級(無時間)→ 該筆即末筆
    ]
    out = ingest._aggregate_daily(rows, "close")
    assert {r["date"]: r["Price"] for r in out} == {
        "2026-06-11": 4219.54, "2026-06-12": 4218.68, "1995-06-01": 383.50}
    assert all(len(r["date"]) == 10 for r in out)             # date 純日級(去時間)


def test_aggregate_daily_empty():
    assert ingest._aggregate_daily([], "close") == []


def test_aggregate_daily_in_seed():
    assert "GoldPrice" in ingest._AGGREGATE_DAILY              # GoldPrice 標 aggregate(augur-specific)
