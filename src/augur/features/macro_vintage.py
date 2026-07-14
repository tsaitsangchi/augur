"""augur 總經 PIT 讀取器 — fred_series 之唯一合法消費門(#8 vintage 濾版於介面上機械強制)。

🎯 這支在做什麼(白話):fred_series 存了各 vintage(realtime_start=該版可見起日),但「消費端須濾
   realtime_start ≤ panel 取當下可見版」過去只是註解、無強制——任何人照 date≤panel 慣例寫 SQL 就會
   拿到未來修訂值(revision 洩漏 #8;2026-07-11 審計 latent 債)。本模組把濾版做進**唯一 API**:
   - Tier B(vintage 序列,如 GDPC1/UNRATE):`date ≤ panel AND realtime_start ≤ panel`,同 date 取
     realtime_start 最大之「panel 當下現行版」——拿得到當時的初值/當時已出的修訂、拿不到未來版。
   - Tier A(每日市場序列):落地時 realtime_start 被觀測日覆寫(fred.py 決策、非 FRED 實測),且美時區
     date=T 於台股 T 日收盤尚不可見(DFF/RRPONTSYD 更為 T+1 發布)→ 一律 **T−1 保守消費**(TIER_A_LAG_DAYS)。
   未知 series_id 一律 fail-loud(#15,防繞過本門直寫 SQL 的假替代)。回列皆帶防衛斷言 realtime_start≤有效 cutoff。

守 #8(vintage 濾版/T−1 保守)· #15(fail-loud、防衛斷言)· #12(fred_series 消費謂詞單一住所=本檔)。
   現況誠實:尚無任何生產特徵消費總經(feature_values 零 macro 特徵)——本模組是「接線前先建好門」,
   非既有洩漏之修補;未來 macro 特徵一律經此門、不得對 fred_series 寫 raw SQL。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.macro_vintage              # 印用途+公開入口（唯讀）
  python -m augur.features.macro_vintage --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from datetime import date, timedelta

from augur.features import macro

TIER_A_LAG_DAYS = 1   # 美時區日數列保守滯後:date=T 於台股 T 日不可見(時區+T+1 發布)→ 消費上界=panel−1


def _coerce(d):
    return d if isinstance(d, date) else date.fromisoformat(str(d)[:10])


def visible_cutoff(series_id, panel_date):
    """該序列於 panel_date 之「可見資料日上界」:Tier B=panel 本身(靠 vintage 濾版)、Tier A=panel−1(保守)。
    未知 series_id → ValueError(fail-loud #15)。"""
    vm = macro.vintage_map()
    if series_id not in vm:
        raise ValueError(f"未知 FRED series {series_id!r}(不在 macro.SERIES;#15 fail-loud、不猜 Tier)")
    p = _coerce(panel_date)
    return p if vm[series_id] else p - timedelta(days=TIER_A_LAG_DAYS)


def as_of(cur, series_id, panel_date):
    """panel_date 當下可見之最新觀測(PIT):回 (value: float, obs_date, vintage_realtime_start) 或 None。
    Tier B 取「最新可見觀測之 panel 當下現行版」;Tier A 以 T−1 上界。"""
    cutoff = visible_cutoff(series_id, panel_date)
    cur.execute(
        'SELECT value::float8, date, realtime_start FROM fred_series '
        "WHERE series_id=%s AND date <= %s AND realtime_start <= %s AND value IS NOT NULL "  # 缺值非觀測(FRED '.'→NULL)
        "ORDER BY date DESC, realtime_start DESC LIMIT 1",
        (series_id, cutoff, cutoff))
    row = cur.fetchone()
    if not row:
        return None
    v, d, rs = row
    assert rs <= cutoff, f"PIT 防衛斷言失敗:{series_id} realtime_start={rs} > cutoff={cutoff}"   # 不可能;護欄
    return float(v), d, rs


def value_asof(cur, series_id, obs_date, panel_date):
    """指定觀測日 obs_date 於 panel_date 當下可見之「現行版」值(PIT 修訂語意):回 float 或 None
    (None=該觀測於 panel 當下尚未首發、或無此觀測)。"""
    cutoff = visible_cutoff(series_id, panel_date)
    cur.execute(
        'SELECT value::float8, realtime_start FROM fred_series '
        "WHERE series_id=%s AND date=%s AND realtime_start <= %s "
        "ORDER BY realtime_start DESC LIMIT 1",
        (series_id, _coerce(obs_date), cutoff))
    row = cur.fetchone()
    if not row:
        return None
    assert row[1] <= cutoff
    return float(row[0])


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    p = date(2026, 7, 14)
    # _coerce:date 直通、字串取前 10 碼
    chk("_coerce date 直通", _coerce(p) == p)
    chk("_coerce ISO 字串截前10碼", _coerce("2026-07-14T09:30:00") == p)
    # visible_cutoff:Tier B(vintage)=panel 本身;Tier A(每日)=panel−1(保守 T−1)
    chk("Tier B 上界=panel", visible_cutoff("UNRATE", p) == p)
    chk("Tier A 上界=panel−1", visible_cutoff("DGS10", p) == p - timedelta(days=1))
    # 未知 series → fail-loud(#15)
    try:
        visible_cutoff("NOPE_XYZ", p); raised = False
    except ValueError:
        raised = True
    chk("未知 series fail-loud", raised)
    # 常數與 IO-bound 公開入口存在(結構斷言)
    chk("TIER_A_LAG_DAYS==1", TIER_A_LAG_DAYS == 1)
    chk("as_of/value_asof 可呼叫", callable(as_of) and callable(value_asof))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.macro_vintage --selftest;免 DB 免 API)")
