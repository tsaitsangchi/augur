"""augur 財報基本面特徵 — ROE／負債比（庫內 as-of；零市場 API）。

🎯 這支在做什麼（白話）：給 as-of 面板日 t + stock_id，用已公告財報／資產負債表算：
- `roe`：最近已公告 NetIncome（或 IncomeAfterTaxes）／Equity
- `debt_ratio`：Liabilities／TotalAssets
發布日 gate（#8）→ 算不出缺列（#1）。**不**建 peg／F-Score／macro_regime（另標 deferred／FZ）。

守 #1 #8 #9 #5；MAP-E012 S2；FZ-keep。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.fundamentals              # 印用途＋公開入口
  python -m augur.features.fundamentals --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from datetime import date

from augur.features import release_lag

MAX_STALE_DAYS = 400

_FS_SQL = (
    'SELECT date, type, value::float8 FROM "TaiwanStockFinancialStatements" '
    "WHERE stock_id=%s AND type IN ('NetIncome','IncomeAfterTaxes','IncomeAfterTax') "
    "AND date <= %s AND value IS NOT NULL ORDER BY date"
)
_BS_SQL = (
    'SELECT date, type, value::float8 FROM "TaiwanStockBalanceSheet" '
    "WHERE stock_id=%s AND type IN ('Equity','Liabilities','TotalAssets') "
    "AND date <= %s AND value IS NOT NULL ORDER BY date"
)


def _latest_released(by_date: dict, pdt: date, *types: str):
    """回傳 (季底日, {type: value}) 最近已公告且含所需 type；無則 None。"""
    for d in sorted(by_date, reverse=True):
        dd = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
        if not release_lag.financial_released(dd, pdt):
            continue
        if (pdt - dd).days > MAX_STALE_DAYS:
            continue
        row = by_date[d]
        if all(t in row for t in types):
            return dd, row
    return None


def _pick_income(row: dict) -> float | None:
    for t in ("NetIncome", "IncomeAfterTaxes", "IncomeAfterTax"):
        v = row.get(t)
        if v is not None:
            return float(v)
    return None


def compute_fundamental_features(cur, sid, panel_date) -> dict:
    """→ {roe?, debt_ratio?}；算不出之 key 不出現（#1）。"""
    pdt = panel_date if isinstance(panel_date, date) else date.fromisoformat(str(panel_date)[:10])
    out: dict = {}

    cur.execute(_FS_SQL, (sid, panel_date))
    fs_by: dict = {}
    for d, t, v in cur.fetchall():
        fs_by.setdefault(d, {})[t] = v

    cur.execute(_BS_SQL, (sid, panel_date))
    bs_by: dict = {}
    for d, t, v in cur.fetchall():
        bs_by.setdefault(d, {})[t] = v

    # debt_ratio：同季 Liabilities / TotalAssets
    got = _latest_released(bs_by, pdt, "Liabilities", "TotalAssets")
    if got:
        _, brow = got
        liab, assets = float(brow["Liabilities"]), float(brow["TotalAssets"])
        if assets > 0:
            v = liab / assets
            if v == v and abs(v) != float("inf"):  # finite
                out["debt_ratio"] = float(v)

    # roe：最近已公告收入 / 最近已公告 Equity（可不同表；各自過 gate）
    fs_got = None
    for d in sorted(fs_by, reverse=True):
        dd = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
        if not release_lag.financial_released(dd, pdt):
            continue
        if (pdt - dd).days > MAX_STALE_DAYS:
            continue
        inc = _pick_income(fs_by[d])
        if inc is not None:
            fs_got = (dd, inc)
            break
    eq_got = _latest_released(bs_by, pdt, "Equity")
    if fs_got and eq_got:
        _, income = fs_got
        _, erow = eq_got
        equity = float(erow["Equity"])
        if equity > 0:
            v = income / equity
            if v == v and abs(v) != float("inf"):
                out["roe"] = float(v)

    return out


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    class _Cur:
        def __init__(self, fs, bs):
            self._fs, self._bs = fs, bs
            self._last = None

        def execute(self, sql, params=None):
            self._last = "fs" if "FinancialStatements" in sql else "bs"

        def fetchall(self):
            return self._fs if self._last == "fs" else self._bs

    # Q3 2025 已於 2025-12-31 公告（+45）；Equity/Assets/Liab/NI 齊
    q = date(2025, 9, 30)
    panel = date(2025, 12, 31)
    fs = [(q, "NetIncome", 50.0)]
    bs = [(q, "Equity", 200.0), (q, "Liabilities", 100.0), (q, "TotalAssets", 400.0)]
    feats = compute_fundamental_features(_Cur(fs, bs), "2330", panel)
    chk("roe=0.25", abs(feats.get("roe", -1) - 0.25) < 1e-9)
    chk("debt_ratio=0.25", abs(feats.get("debt_ratio", -1) - 0.25) < 1e-9)

    # 未公告季（panel 太早）→ 缺列
    early = date(2025, 10, 1)  # Q3 +45 = 11/14 尚未到
    empty = compute_fundamental_features(_Cur(fs, bs), "2330", early)
    chk("未公告→缺列", empty == {})

    # assets<=0 → 無 debt_ratio
    bad_bs = [(q, "Equity", 200.0), (q, "Liabilities", 100.0), (q, "TotalAssets", 0.0)]
    no_debt = compute_fundamental_features(_Cur(fs, bad_bs), "2330", panel)
    chk("assets=0 無 debt_ratio", "debt_ratio" not in no_debt)
    chk("仍可有 roe", abs(no_debt.get("roe", -1) - 0.25) < 1e-9)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("公開入口: compute_fundamental_features")
    print("(自測: python -m augur.features.fundamentals --selftest)")
