"""#8 anti-leakage 機械測試 — 證明「決策日 T 不用 release>T 之資料」(三敵②偷看未來之機械守門)。

🎯 這支在做什麼(白話):release-lag gate 建於 feature build 時(panel.py / margin_cycle.py),用
`release_lag.financial_released` / `revenue_released` 剔掉「公告日 > panel_date」的財報/月營收。本測試對
**真實 production build 路徑**注入 synthetic 資料點(公告日 > T),斷言它**不出現**在 T 的特徵——若出現＝洩漏。

三型(部署計畫 D1、§3.3):
- **注入型**(T-1):造 release∈(T1,T2] 之新財報/新月營收 → 斷言 T1 不反映、T2 反映(build 端逐 date gate)。
- **邊界型**(T-2):release 恰在 T vs T±1 → 斷言 `financial_released`/`revenue_released` ±1 日布林正確。
- **整合型**(T-3):對某 panel T 端到端 build_panel → 斷言貢獻該 panel feature 的月營收 release≤T(依型別)。

命門鐵律——**負向自證**:每個「不洩漏」斷言都配一個 `leak_mode` 版本——把 gate 換成永遠放行的假 gate
(＝模擬「未來資料被無條件使用」之洩漏),斷言此時測試會抓到未來值出現(gate 版 PASS、leak 版 FAIL)。
沒有負向自證的守門測試＝假守門(隨便 pass 比沒有更危險)。故洩漏路徑真被本測試涵蓋、非空轉。

隔離/可逆(#25):所有 DB 寫入用 synthetic stock_id(`ZZTEST_*`、實查不與任何真實 stock_id 碰撞);
**每測試結尾硬 DELETE 清除** synthetic 列(build_panel 內部 db.transaction 會 commit 子交易 → 純 rollback
不足以保證回收,故用「注入前 clean + 測試後 DELETE」雙保險)。不放量 API、不動任何真實 stock_id 之資料。

守 #8(零容忍 anti-leakage 機械化)· #12(復用 release_lag / panel / margin_cycle production 路徑、不重造)·
   #15(抓到洩漏就報、不掩蓋)· #25(synthetic 小樣本、不放量)。
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import psycopg2
import pytest

from augur.core import config
from augur.features import margin_cycle, panel, release_lag

# synthetic 隔離前綴(實查零碰撞真實 stock_id;測試後硬清除)
SID_PREFIX = "ZZTEST_LEAK"

# 被 synthetic 注入的所有源表(清理與碰撞檢查對象)
_SYNTH_TABLES = (
    "TaiwanStockFinancialStatements",
    "TaiwanStockMonthRevenue",
    "TaiwanStockPriceAdj",
    "feature_values",
)


# ══════════════════════════════════════════════════════════════════════════
#  純單元:release_lag 布林 gate(不碰 DB;邊界型 T-2 之地基)
# ══════════════════════════════════════════════════════════════════════════

def test_revenue_release_date_maps_to_15th_of_announce_month():
    # 月營收 date=公告月(資料月+1);release=該公告月 15 日。5 月營收 date=6/1 → release=6/15。
    assert release_lag.revenue_release_date(dt.date(2026, 6, 1)) == dt.date(2026, 6, 15)


def test_financial_release_date_quarter_vs_annual_lag():
    # Q1/Q2/Q3 季底 +45;年報(Q4、12/31)+90(次年 3/31 前後)。
    assert release_lag.financial_release_date(dt.date(2026, 3, 31)) == dt.date(2026, 3, 31) + dt.timedelta(days=45)
    assert release_lag.financial_release_date(dt.date(2026, 12, 31)) == dt.date(2026, 12, 31) + dt.timedelta(days=90)


# ── 邊界型 T-2:release 恰在 T vs T-1 vs T+1 → 布林 ±1 日正確 ──
def test_financial_released_boundary_pm1_day():
    q = dt.date(2026, 3, 31)
    rel = release_lag.financial_release_date(q)               # = 2026-05-15
    assert release_lag.financial_released(q, rel) is True      # 公告當日 = 可用(release ≤ T)
    assert release_lag.financial_released(q, rel - dt.timedelta(days=1)) is False   # 前一日 = 未公告
    assert release_lag.financial_released(q, rel + dt.timedelta(days=1)) is True     # 後一日 = 已公告


def test_revenue_released_boundary_pm1_day():
    d = dt.date(2026, 6, 1)                                    # 5 月營收
    rel = release_lag.revenue_release_date(d)                  # = 2026-06-15
    assert release_lag.revenue_released(d, rel) is True
    assert release_lag.revenue_released(d, rel - dt.timedelta(days=1)) is False
    assert release_lag.revenue_released(d, rel + dt.timedelta(days=1)) is True


# ══════════════════════════════════════════════════════════════════════════
#  DB 注入基礎設施(synthetic-only、測試後硬清除)
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def synth_conn():
    """給一個 DB 連線與 synthetic stock_id;注入前確認 synthetic 乾淨、測試後硬 DELETE 所有 synthetic 列。

    為何不靠純 rollback:panel.build_panel 內部用 db.transaction(conn) 會 commit 子交易(價量/特徵各自落地),
    純 rollback 無法回收已 commit 之 synthetic 列 → 改以「前 clean + 後 DELETE」機械保證隔離(#25)。
    """
    try:
        conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"DB 不可用、跳過 DB 注入測試:{e}")

    def _clean(c):
        for t in _SYNTH_TABLES:
            c.execute(f'DELETE FROM "{t}" WHERE stock_id LIKE %s', (SID_PREFIX + "%",))
        c.connection.commit()

    cur = conn.cursor()
    # 防禦:注入前確認 synthetic 前綴確實不與任何真實資料碰撞(理應 0 列)。
    for t in _SYNTH_TABLES:
        cur.execute(f'SELECT count(*) FROM "{t}" WHERE stock_id LIKE %s', (SID_PREFIX + "%",))
        n = cur.fetchone()[0]
        assert n == 0, f"{t} 已有 {n} 列 synthetic 前綴列、拒絕注入(隔離 #25)"
    try:
        yield conn, SID_PREFIX
    finally:
        try:
            _clean(conn.cursor())     # 硬清除:無論子交易是否 commit、synthetic 列一律回收
        finally:
            conn.close()


def _inject_financials(cur, sid, quarters):
    """注入 (quarter_end_date, revenue, gross_profit) 到 TaiwanStockFinancialStatements(synthetic)。"""
    for qend, rev, gp in quarters:
        cur.execute('INSERT INTO "TaiwanStockFinancialStatements"(date,stock_id,type,value) VALUES (%s,%s,%s,%s)',
                    (qend, sid, "Revenue", rev))
        cur.execute('INSERT INTO "TaiwanStockFinancialStatements"(date,stock_id,type,value) VALUES (%s,%s,%s,%s)',
                    (qend, sid, "GrossProfit", gp))
    cur.connection.commit()


def _inject_revenue(cur, sid, months):
    """注入 (announce_month_date, revenue) 到 TaiwanStockMonthRevenue(synthetic)。"""
    for adate, rev in months:
        cur.execute('INSERT INTO "TaiwanStockMonthRevenue"(date,stock_id,country,revenue,revenue_month,revenue_year,create_time) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (adate, sid, "Taiwan", rev, float(adate.month), float(adate.year), str(adate)))
    cur.connection.commit()


# ══════════════════════════════════════════════════════════════════════════
#  注入型 T-1:財報 — 新財報 release∈(T1,T2] 不得反映於 T1
# ══════════════════════════════════════════════════════════════════════════
#
# 構造:8 季**已公告且毛利率互異**歷史(margins 見下,2024Q4=0.30 於自身分位=0.625) + 第 9 季(當季)
# 極端高毛利率(0.90)。當季 date=q_new(2025-03-31)、release=q_new+45=2025-05-15。取 T1=release-1、T2=release。
#   - T1(當季未公告):released 僅 8 季、last=2024Q4 → pctile(0.30)=0.625(當季 0.90 不計入)。
#   - T2(當季已公告):released 9 季、last=當季 0.90(史上最高)→ pctile=1.0。
# 若 T1 已 =1.0 ⇒ 用了 release>T1 的未來財報 ⇒ 洩漏。歷史刻意互異,使 pctile 有鑑別力(非全 tie=1.0)。

def _margin_quarters():
    """8 季互異毛利率(2024Q4=0.30、自身分位 0.625)+ 當季 2025Q1 極端高(0.90)。回 (quarters, q_new)。"""
    hist_ends = [dt.date(y, m, d) for y in (2023, 2024) for (m, d) in ((3, 31), (6, 30), (9, 30), (12, 31))]
    hist_margins = [0.10, 0.15, 0.20, 0.25, 0.35, 0.40, 0.45, 0.30]   # 2024Q4(末筆)=0.30 → 分位 0.625
    quarters = [(qe, 100.0, m * 100.0) for qe, m in zip(hist_ends, hist_margins)]   # gp = margin*rev
    q_new = dt.date(2025, 3, 31)                                        # 當季:release=2025-05-15
    quarters.append((q_new, 100.0, 90.0))                              # margin=0.90=史上唯一極端高
    return quarters, q_new


_T1_PCTILE = 0.625     # T1(當季未公告)之期望分位:2024Q4 margin 0.30 在 8 季互異歷史中
_T2_PCTILE = 1.0       # T2(當季已公告)之期望分位:當季 0.90 = 史上最高


def _margin_pctile(cur, sid, panel_date, *, leak_mode=False):
    """跑 production margin_cycle 於 (sid, panel_date),回 gross_margin_pctile(缺→None)。
    leak_mode=True:把 financial_released 換成永遠 True(＝模擬洩漏:無條件用未來財報)。"""
    if leak_mode:
        orig = release_lag.financial_released
        release_lag.financial_released = lambda d, p: True
        try:
            feats = margin_cycle.compute_margin_cycle_features(cur, sid, panel_date)
        finally:
            release_lag.financial_released = orig
    else:
        feats = margin_cycle.compute_margin_cycle_features(cur, sid, panel_date)
    return feats.get("gross_margin_pctile")


def test_T1_financial_new_report_not_reflected_before_release(synth_conn):
    """注入型:release∈(T1,T2] 之新極端財報,T1 不反映(=0.625,舊分布)、T2 反映(=1.0)。gate 版正確。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    quarters, q_new = _margin_quarters()
    _inject_financials(cur, sid, quarters)
    rel = release_lag.financial_release_date(q_new)          # 2025-05-15
    t1 = rel - dt.timedelta(days=1)                          # 當季未公告
    t2 = rel                                                 # 當季已公告

    p1 = _margin_pctile(cur, sid, t1)
    p2 = _margin_pctile(cur, sid, t2)

    assert p2 == pytest.approx(_T2_PCTILE), f"T2(release≤T2)應含新財報、pctile=1.0,得 {p2}"
    assert p1 == pytest.approx(_T1_PCTILE), (
        f"洩漏或分位錯!T1={t1} < release={rel} 之 pctile 應=0.625(舊分布、當季未計入),得 {p1}"
        "——若=1.0 表示 build 用了 release>T 的未來財報")
    assert p1 != p2, "T1 與 T2 應不同(新財報跨 release 邊界改變 pctile);相同=gate 未生效"


def test_T1_financial_NEGATIVE_leak_mode_FAILS(synth_conn):
    """負向自證(命門):把 gate 換成永遠放行 → T1 也用未來財報 → pctile 由 0.625 變 1.0。
    斷言「leak_mode 下 T1 確實反映未來財報(=1.0)」——證明測試路徑真能被洩漏影響(非空轉)。
    gate 版與 leak 版相異 = 上一測試之 T1 斷言在真洩漏下必 FAIL(守門有鑑別力)。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    quarters, q_new = _margin_quarters()
    _inject_financials(cur, sid, quarters)
    rel = release_lag.financial_release_date(q_new)
    t1 = rel - dt.timedelta(days=1)

    p1_gate = _margin_pctile(cur, sid, t1, leak_mode=False)   # gate:當季不入 → 0.625
    p1_leak = _margin_pctile(cur, sid, t1, leak_mode=True)    # leak:當季無條件入 → 1.0

    assert p1_gate == pytest.approx(_T1_PCTILE), f"gate 版應剔未公告當季(=0.625),得 {p1_gate}"
    assert p1_leak == pytest.approx(_T2_PCTILE), (
        f"負向自證失敗:無條件放行未來財報後 T1 仍未反映(得 {p1_leak}≠1.0)——測試路徑對洩漏不敏感(假測試)")
    assert p1_gate != p1_leak, "gate 版與 leak 版必須相異,否則守門測試無鑑別力(假守門)"


# ══════════════════════════════════════════════════════════════════════════
#  注入型 T-1:月營收 — 未公告月營收不得入 YoY(走 panel production gate 邏輯)
# ══════════════════════════════════════════════════════════════════════════
#
# 走 production _REVENUE_SQL + release_lag.revenue_released + _compute_revenue_yoy(panel.build_panel:133-151 之
# 過濾與演算法,零重造)。造 13 個月營收,最近月 announce 之 release∈(T1,T2]。
#   - T1:最近月被剔 → 僅 12 筆 <13 → YoY 算不出(None)。
#   - T2:最近月納入 → YoY=log(500/100)=log(5)。

def _revenue_months_13():
    """13 個月營收(announce_date=每月 1 號、逐月遞增),最近月 revenue 為極端值放大差異。回 (months, last)。"""
    base = [dt.date(2024 + (1 + i) // 12, (1 + i) % 12 + 1, 1) for i in range(13)]   # 2024-02-01 .. 2025-02-01
    months = [(adate, 100.0) for adate in base[:-1]]
    last = base[-1]
    months.append((last, 500.0))     # 最近月極端高
    return months, last


def _revenue_yoy(cur, sid, panel_date, *, leak_mode=False):
    """複製 panel.build_panel 月營收 gate+YoY(panel.py:133-151)於單股,回 monthly_revenue_yoy(缺→None)。
    走真實 _REVENUE_SQL + release_lag.revenue_released + _compute_revenue_yoy(production 函式)。
    leak_mode=True:gate 換永遠 True(模擬洩漏)。"""
    cur.execute(panel._REVENUE_SQL, (sid, panel_date))
    rev_rows = cur.fetchall()
    pdt = panel_date if isinstance(panel_date, dt.date) else dt.date.fromisoformat(str(panel_date)[:10])
    gate = (lambda d, p: True) if leak_mode else release_lag.revenue_released
    rev_rel = [(d, r) for d, r in rev_rows
               if gate(d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10]), pdt)]
    return panel._compute_revenue_yoy(rev_rel)


def test_T1_revenue_unreleased_month_not_in_yoy(synth_conn):
    """注入型:最近月營收 release∈(T1,T2],T1 之 YoY 不得用最近月(None)、T2 才用(log5)。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    months, last = _revenue_months_13()
    _inject_revenue(cur, sid, months)
    rel = release_lag.revenue_release_date(last)
    t1 = rel - dt.timedelta(days=1)
    t2 = rel

    y1 = _revenue_yoy(cur, sid, t1)
    y2 = _revenue_yoy(cur, sid, t2)

    assert y2 == pytest.approx(np.log(5.0), rel=1e-6), f"T2 應含最近月、YoY≈log(5),得 {y2}"
    assert y1 != y2, f"洩漏!T1={t1} < release={rel} 卻用了最近月營收(y1={y1}==y2)"
    assert y1 is None, f"T1 剔最近月後僅 12 筆(<13)、YoY 應算不出(None),得 {y1}——若非 None 疑洩漏"


def test_T1_revenue_NEGATIVE_leak_mode_FAILS(synth_conn):
    """負向自證:gate 換永遠放行 → T1 也用最近月 → y1=log(5)=y2 → 上一測試 T1 斷言在真洩漏下必 FAIL。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    months, last = _revenue_months_13()
    _inject_revenue(cur, sid, months)
    rel = release_lag.revenue_release_date(last)
    t1 = rel - dt.timedelta(days=1)

    y1_gate = _revenue_yoy(cur, sid, t1, leak_mode=False)
    y1_leak = _revenue_yoy(cur, sid, t1, leak_mode=True)

    assert y1_gate is None, f"gate 版:未公告最近月被剔、僅 12 筆算不出(None),得 {y1_gate}"
    assert y1_leak == pytest.approx(np.log(5.0), rel=1e-6), (
        f"負向自證失敗:無條件放行未來月營收後 T1 仍未用最近月(得 {y1_leak})——測試路徑對洩漏不敏感(假測試)")
    assert y1_gate != y1_leak, "gate 版與 leak 版必須相異(守門有鑑別力)"


# ══════════════════════════════════════════════════════════════════════════
#  整合型 T-3:端到端 build_panel — 未公告月營收不得落地 feature_values
# ══════════════════════════════════════════════════════════════════════════

_PRICE_TABLE = "TaiwanStockPriceAdj"


def _inject_prices(cur, sid, panel_date, n=300):
    """注入 n 個交易日合成還原價(供 build_panel 價量特徵不因缺價而整股 drop)。單調小漲、避免 0。"""
    rows, price = [], 100.0
    for i in range(n):
        day = panel_date - dt.timedelta(days=i)
        p = price * (1 + 0.0005 * (n - i))
        rows.append((day, sid, p, 1000.0 + i, p * (1000.0 + i), 0.01, p * 1.01, p * 0.99))
    cols = 'date,stock_id,close,"Trading_Volume","Trading_money","Trading_turnover","max","min"'
    args = ",".join(cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", r).decode() for r in rows)
    cur.execute(f'INSERT INTO "{_PRICE_TABLE}"({cols}) VALUES {args}')
    cur.connection.commit()


def _panel_yoy_value(cur, panel_date, sid):
    cur.execute("SELECT value FROM feature_values WHERE panel_date=%s AND stock_id=%s AND feature='monthly_revenue_yoy'",
                (panel_date, sid))
    r = cur.fetchone()
    return None if r is None else float(r[0])


def test_T3_integration_build_panel_excludes_unreleased_revenue(synth_conn):
    """整合型(端到端 build_panel):panel T=release-1,注入之未公告最近月營收不得使 monthly_revenue_yoy 落地。
    另逐 date 斷言:凡 release>T 之月營收皆判未公告(provenance:貢獻該 panel 之月營收 release≤T)。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    months, last = _revenue_months_13()
    rel = release_lag.revenue_release_date(last)
    t1 = rel - dt.timedelta(days=1)          # panel T:最近月尚未公告
    _inject_revenue(cur, sid, months)
    _inject_prices(cur, sid, t1, n=300)

    panel.build_panel(conn, t1, [sid])       # production 端到端

    val = _panel_yoy_value(cur, t1, sid)
    assert val is None, (
        f"洩漏!panel T={t1} < release={rel},build_panel 卻落地 monthly_revenue_yoy={val}"
        "——最近月未公告卻進了特徵")

    # provenance 斷言:凡 release>T 之月營收其 gate 必判未公告(未貢獻)。
    cur.execute(panel._REVENUE_SQL, (sid, t1))
    for d, _r in cur.fetchall():
        dd = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10])
        if release_lag.revenue_release_date(dd) > t1:
            assert release_lag.revenue_released(dd, t1) is False, (
                f"月營收 {dd}(release>T={t1})gate 卻放行(洩漏)")


def test_T3_integration_build_panel_includes_released_revenue(synth_conn):
    """整合型對照(邊界另一側):panel 推到 release 當日 T2=rel → 最近月已公告 → monthly_revenue_yoy 落地。
    證明 build_panel 非「總是不落地」(否則 T3 之 None 斷言空過);gate 於邊界正確含 release≤T 者。"""
    conn, sid = synth_conn
    cur = conn.cursor()
    months, last = _revenue_months_13()
    rel = release_lag.revenue_release_date(last)
    t2 = rel                                 # 最近月已公告
    _inject_revenue(cur, sid, months)
    _inject_prices(cur, sid, t2, n=300)

    panel.build_panel(conn, t2, [sid])

    val = _panel_yoy_value(cur, t2, sid)
    assert val is not None, "T2=release 當日最近月已公告、monthly_revenue_yoy 應落地(gate 不得過度保守剔真值)"
    assert val == pytest.approx(np.log(5.0), rel=1e-6), f"T2 之 YoY 應含最近月(≈log5),得 {val}"
