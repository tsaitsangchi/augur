"""augur 估值特徵 — PER/PBR/殖利率/市值（F2c、第一性軸④ 價格-價值缺口）。

🎯 這支在做什麼（白話）：給 as-of 面板日 t + 一個 stock_id，query 估值表算 5 個估值面特徵：
本益比、淨值比、殖利率、市值規模、（可選）價格相對 10 年線位置。as-of ≤t 最近一筆。

對應 F2 roadmap F2c 期、第一性計畫軸④（估值水位）：
- f1 pe_ratio：本益比 PER（估值水位、raw 值；樹自學分界、不硬編「便宜」閾值 #9）
- f2 pb_ratio：淨值比 PBR
- f3 dividend_yield：殖利率（%）
- f4 market_cap_log：log(市值)（size 規模因子；log 壓縮量綱）
- f5 price_to_10yr：原始收盤 / 10 年線 − 1（超長期均值回歸位置；需 TaiwanStockPrice + 10Year，缺則略；
  #8：用原始收盤而非前向還原 PriceAdj，避免未來股利/分割因子回溯注入歷史價之偷看）

**無 P-lag 風險**（別於財報三表 #8）：PER/PBR/殖利率/市值皆交易所**每日公布**（基於最近財報 EPS + 當日價）→
date ≤ panel_date 即 as-of 安全。**#9**：估值 raw 值入 feature（不設「PER<15 便宜」硬閾值，相對化交給樹/橫斷面）。
**#1**：算不出（無資料 / PER≤0 虧損 / 市值≤0）→ 不含該 key（缺列、不存 fake）。

守 #1（算不出即缺列）· #8（as-of ≤t、無 P-lag）· #9（估值不硬編閾值）· #5（numeric）· F2 roadmap F2c。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.valuation              # 印用途+公開入口（唯讀）
  python -m augur.features.valuation --selftest   # 純紅綠自測（零 IO：假 cursor 驗缺列/formula）
"""
from __future__ import annotations

import numpy as np

from augur.catalog.world_concept import quote_ident, resolve

MARKET_CAP_CONCEPT = "tw.market_capitalization.stock"
_MV_PREFERRED_COL = "market_value"

_PER_SQL = (
    'SELECT "PER"::float8, "PBR"::float8, dividend_yield::float8 '
    'FROM "TaiwanStockPER" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)
_TENYR_SQL = (
    'SELECT close::float8 FROM "TaiwanStock10Year" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)
_RAW_CLOSE_SQL = (   # #8 修正(2026-07-10 審計):原讀 TaiwanStockPriceAdj——前向還原把「未來」股利/分割因子
    # 回溯注入歷史價(adj/raw 比值隨錨點日漂移)=偷看未來;改讀原始 TaiwanStockPrice,與 raw-basis 之
    # TaiwanStock10Year 同 point-in-time 口徑(消除 restatement 洩漏並修正混口徑)。
    'SELECT close::float8 FROM "TaiwanStockPrice" WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1'
)


def market_value_asof_sql_from_table(source_table: str, fact_col: str = _MV_PREFERRED_COL) -> str:
    """純函式：表＋欄 → 市值 as-of 單列 SQL（#35；禁 vendor 字面散落於生產常數）。"""
    return (
        f"SELECT {quote_ident(fact_col)}::float8 FROM {quote_ident(source_table)} "
        f"WHERE stock_id=%s AND date <= %s ORDER BY date DESC LIMIT 1"
    )


def market_value_asof_sql(conn=None) -> str:
    """經 Registry resolve 組市值 as-of SQL（UNBIND-70；禁回退 vendor 字面）。"""
    b = resolve(MARKET_CAP_CONCEPT, conn=conn)
    cols = [c.strip() for c in (b.column or "").split(",") if c.strip()]
    if not cols:
        fact = _MV_PREFERRED_COL
    elif _MV_PREFERRED_COL in cols:
        fact = _MV_PREFERRED_COL
    elif len(cols) == 1:
        fact = cols[0]
    else:
        raise RuntimeError(
            f"UNBIND-70: {MARKET_CAP_CONCEPT} multi-column unexpected for market_value "
            f"scalar: column={b.column!r} table={b.table!r} binding_id={b.binding_id}"
        )
    return market_value_asof_sql_from_table(b.table, fact)


def compute_valuation_features(cur, sid, panel_date, *, market_value_sql=None):
    """對 sid + panel_date 算估值 features → {feature: value}；算不出 → 不含該 key（缺列、#1）。

    market_value_sql：可選覆蓋（自測餵 from_table）；預設 resolve tw.market_capitalization.stock。
    """
    out = {}

    # f1-f3 PER/PBR/殖利率（同一表最近一筆）
    cur.execute(_PER_SQL, (sid, panel_date))
    row = cur.fetchone()
    if row:
        per, pbr, dy = row
        if per is not None and per > 0 and np.isfinite(per):          # 本益比>0（虧損股 PER 負/無意義→缺）
            out["pe_ratio"] = float(per)
        if pbr is not None and pbr > 0 and np.isfinite(pbr):
            out["pb_ratio"] = float(pbr)
        if dy is not None and dy >= 0 and np.isfinite(dy):            # 殖利率≥0（0=不配息、真值）
            out["dividend_yield"] = float(dy)

    # f4 市值 log（size 因子）— resolve tw.market_capitalization.stock（UNBIND-70）
    mv_sql = market_value_sql if market_value_sql is not None else market_value_asof_sql(
        getattr(cur, "connection", None))
    cur.execute(mv_sql, (sid, panel_date))
    row = cur.fetchone()
    if row and row[0] is not None and row[0] > 0:
        v = float(np.log(row[0]))
        if np.isfinite(v):
            out["market_cap_log"] = v

    # f5 還原收盤 / 10 年線 − 1（超長期均值回歸位置；10Year 2011 起、缺則略）
    cur.execute(_TENYR_SQL, (sid, panel_date))
    tr = cur.fetchone()
    if tr and tr[0] is not None and tr[0] > 0:
        cur.execute(_RAW_CLOSE_SQL, (sid, panel_date))
        cr = cur.fetchone()
        if cr and cr[0] is not None and cr[0] > 0:
            v = float(cr[0] / tr[0] - 1.0)
            if np.isfinite(v):
                out["price_to_10yr"] = v

    return out


class _FakeCur:
    """自測用純記憶 cursor（零 IO）：依 SQL 命中之表／欄回合成列，模擬 execute→fetchone 序。"""
    def __init__(self, rows):
        self._rows = rows          # {'per','mv','tenyr','close': tuple|None}
        self._last = None
        self.connection = None     # 自測不走 resolve；須餵 market_value_sql=
    def execute(self, sql, params=None):
        if "TaiwanStockPER" in sql:
            self._last = "per"
        elif "market_value" in sql and "LIMIT 1" in sql:
            self._last = "mv"
        elif "TaiwanStock10Year" in sql:
            self._last = "tenyr"
        elif "TaiwanStockPrice" in sql:
            self._last = "close"
    def fetchone(self):
        return self._rows.get(self._last)


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：假 cursor 合成列紅綠測估值不變式——
    虧損股缺列（#1/#9）· log/ratio formula · 殖利率 0 為真值 · 無資料全缺列（#1）；
    UNBIND-70 helper 換表／換欄會紅（#35）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    mv_sql_ok = market_value_asof_sql_from_table("TaiwanStockMarketValue", "market_value")
    chk("mv helper uses quoted table + market_value",
        '"TaiwanStockMarketValue"' in mv_sql_ok and '"market_value"' in mv_sql_ok
        and "ORDER BY date DESC LIMIT 1" in mv_sql_ok)
    mv_sql_bad = market_value_asof_sql_from_table("OtherCap", "market_value")
    chk("mv helper table swap changes SQL (#35 會紅)",
        mv_sql_bad != mv_sql_ok and '"OtherCap"' in mv_sql_bad)
    mv_sql_col = market_value_asof_sql_from_table("TaiwanStockMarketValue", "XCap")
    chk("mv helper column swap changes SQL (#35 會紅)",
        mv_sql_col != mv_sql_ok and '"XCap"' in mv_sql_col)

    mv = float(np.exp(20.0))
    normal = compute_valuation_features(
        _FakeCur({"per": (15.0, 2.0, 3.0), "mv": (mv,), "tenyr": (100.0,), "close": (120.0,)}),
        "2330", "2026-05-31", market_value_sql=mv_sql_ok)
    chk("正常三值齊全(PER/PBR/殖利率)",
        normal["pe_ratio"] == 15.0 and normal["pb_ratio"] == 2.0 and normal["dividend_yield"] == 3.0)
    chk("market_cap_log=log(mv)", abs(normal["market_cap_log"] - 20.0) < 1e-9)
    chk("price_to_10yr=close/10yr-1", abs(normal["price_to_10yr"] - 0.2) < 1e-9)

    loss = compute_valuation_features(
        _FakeCur({"per": (-1.0, 2.0, 3.0)}), "9999", "2026-05-31",
        market_value_sql=mv_sql_ok)
    chk("虧損股 PER≤0 缺列(#1/#9)", "pe_ratio" not in loss and loss["pb_ratio"] == 2.0)

    edge = compute_valuation_features(
        _FakeCur({"per": (15.0, 2.0, 0.0), "mv": (0.0,)}), "1111", "2026-05-31",
        market_value_sql=mv_sql_ok)
    chk("殖利率=0 保留(真值非缺)", edge["dividend_yield"] == 0.0)
    chk("市值≤0 缺 market_cap_log(#1)", "market_cap_log" not in edge)

    empty = compute_valuation_features(
        _FakeCur({}), "0000", "2026-05-31", market_value_sql=mv_sql_ok)
    chk("無資料→全缺列(#1)", empty == {})

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:compute_valuation_features(cur, sid, panel_date) → {feature: value}（算不出即缺列 #1）")
    print("     market_value → resolve('tw.market_capitalization.stock')（UNBIND-70）")
    print("(自測:python -m augur.features.valuation --selftest;免 DB 免 API)")
