"""macro_vintage PIT 讀取器回歸 — 證 #8 vintage 濾版/T−1 保守/fail-loud(2026-07-11 審計 latent 債之門)。

🎯 這支在測什麼(白話):用真 fred_series vintage 資料證——(1)Tier B 拿「panel 當下現行版」、
   拿不到未來修訂(GDPC1 2020Q1 於 2020-05 只見 advance 初值、於 2024 見後修版且兩值不同);
   (2)發布滯後被尊重(panel 早於首發 → None);(3)Tier A 消費上界=panel−1;(4)未知 series fail-loud。
"""
import pytest

from augur.core import db
from augur.features import macro_vintage


@pytest.fixture(scope="module")
def cur():
    with db.connect() as conn:
        yield conn.cursor()


def test_tier_b_pit_no_future_revision(cur):
    """GDPC1 觀測 2020-01-01:早 panel 見初值、晚 panel 見修訂版,且不同(=濾版真的把版本鎖在當下)。"""
    early = macro_vintage.value_asof(cur, "GDPC1", "2020-01-01", "2020-05-31")
    late = macro_vintage.value_asof(cur, "GDPC1", "2020-01-01", "2025-05-31")
    assert early is not None and late is not None
    assert early != late                        # 修訂存在且被 PIT 區分(audit 實證:多 vintage)
    # early 必等於「首發後最早可見版」之獨立 SQL(自洽性)
    cur.execute("SELECT value::float8 FROM fred_series WHERE series_id='GDPC1' AND date='2020-01-01' "
                "AND realtime_start <= '2020-05-31' ORDER BY realtime_start DESC LIMIT 1")
    assert early == cur.fetchone()[0]


def test_tier_b_release_lag_respected(cur):
    """GDPC1 2020Q1(obs 2020-01-01)首發 2020-04-29 → panel 2020-03-31 應 None(尚未公布、不可見)。"""
    assert macro_vintage.value_asof(cur, "GDPC1", "2020-01-01", "2020-03-31") is None


def test_as_of_invariants(cur):
    """as_of 回列不變式:obs_date ≤ cutoff 且 vintage ≤ cutoff(對 Tier B 抽 UNRATE)。"""
    r = macro_vintage.as_of(cur, "UNRATE", "2020-06-30")
    assert r is not None
    v, d, rs = r
    assert d <= macro_vintage.visible_cutoff("UNRATE", "2020-06-30")
    assert rs <= macro_vintage.visible_cutoff("UNRATE", "2020-06-30")


def test_tier_a_t_minus_1(cur):
    """Tier A(DGS10 每日):cutoff=panel−1(美時區/T+1 保守),as_of 之 obs date 不得=panel 當日。"""
    from datetime import date
    cutoff = macro_vintage.visible_cutoff("DGS10", "2026-05-29")
    assert cutoff == date(2026, 5, 28)
    r = macro_vintage.as_of(cur, "DGS10", "2026-05-29")
    assert r is not None and r[1] <= cutoff


def test_unknown_series_fail_loud():
    with pytest.raises(ValueError):
        macro_vintage.visible_cutoff("NOT_A_SERIES", "2026-05-31")
