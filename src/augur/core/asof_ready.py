"""as-of 就緒閘 — 歷史 D 能否收特徵／訓練／出單（anti fake-B3）。

🎯 這支在做什麼（白話）：判斷某個交易日 D 是「庫內當時世界夠不夠」：
  PriceAdj(TAIEX)≥D 且 feature_values 有 D → ready（可訓可出單）；
  有價無特徵 → need_collect（可 build_feature_panel，不是假今天）；
  價 < D → fake_b3（禁止把模型登記成還沒發生的 asof）。
  方向臂訓練鎖＝pick_lock／resolve_lock（未指定 → 價頂＝可更新最新日；≠ COMPLETENESS_ASOF）。
  截面族共用同一張 panel。零 live API。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.core.asof_ready
  python -m augur.core.asof_ready --selftest
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Optional

from augur.core.closed_horizons import H_TRACK

STATUS_READY = "ready"
STATUS_NEED_COLLECT = "need_collect"
STATUS_FAKE_B3 = "fake_b3"
STATUS_NO_PRICE = "no_price"

A_FAMILIES = (
    "RankRidge",
    "RankGBDT",
    "RankXGB",
    "RankCat",
    "RankRF",
    "RankKNN",
    "RankMLP",
    "RankSVM",
)

# 方向臂（⊥ 邊界 A；RETRAIN-ALL 包）。數 model_id，不是 family。
DAILY_IDS = ("DailyLogit", "DailyGBDT", "DailyGBDT_cal")
MKT_IDS = ("MktLogit", "MktLogit_v2")
STACK_IDS = ("DirStackM",)
NEED_A_CELLS = len(A_FAMILIES) * len(H_TRACK)
NEED_DAILY = len(DAILY_IDS)
NEED_MKT = len(MKT_IDS)
NEED_STACK = len(STACK_IDS)

RC_READY = 0
RC_NEED_COLLECT = 2
RC_FAKE_B3 = 3
RC_NO_PRICE = 4

# 完整性定案錨（憲章歷史判準）。方向臂訓練鎖 ≠ 此常數，見 pick_lock／resolve_lock。
COMPLETENESS_ASOF = date(2026, 5, 31)

_STATUS_RC = {
    STATUS_READY: RC_READY,
    STATUS_NEED_COLLECT: RC_NEED_COLLECT,
    STATUS_FAKE_B3: RC_FAKE_B3,
    STATUS_NO_PRICE: RC_NO_PRICE,
}


def as_date(v: Any) -> Optional[date]:
    """CLI／DB 值 → date；空 → None。純函式。"""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()[:10]
    if not s:
        return None
    return date.fromisoformat(s)


def classify_asof(d: Any, price_max: Any, fv_rows: int) -> str:
    """純函式：D × 價頂 × 該日特徵列數 → 狀態字。"""
    dd = as_date(d)
    pm = as_date(price_max)
    n = int(fv_rows or 0)
    if dd is None:
        return STATUS_NO_PRICE
    if pm is None:
        return STATUS_NO_PRICE
    if dd > pm:
        return STATUS_FAKE_B3
    if n <= 0:
        return STATUS_NEED_COLLECT
    return STATUS_READY


def rc_of(status: str) -> int:
    return _STATUS_RC.get(status, 1)


def pack_is_complete(
    *,
    a_cells: int,
    daily: int,
    mkt: int,
    stack: int,
    asof: Any,
    price_max: Any,
) -> bool:
    """截面 8×8 已齊才算包；方向臂只在 D＝價頂列入（單一 model_id，歷史 D 不得要求）。"""
    if int(a_cells or 0) < NEED_A_CELLS:
        return False
    dd, pm = as_date(asof), as_date(price_max)
    if dd is None or pm is None or dd != pm:
        return True
    return (
        int(daily or 0) >= NEED_DAILY
        and int(mkt or 0) >= NEED_MKT
        and int(stack or 0) >= NEED_STACK
    )


def snapshot(cur, d: Any) -> dict:
    """唯讀 DB：D 的價／特徵／核心／邊界 A＋方向臂 registry。cur 須已開。"""
    dd = as_date(d)
    if dd is None:
        raise ValueError("as-of 日空")
    price_max = taiex_price_max(cur)
    cur.execute(
        "SELECT count(distinct feature), count(*) FROM feature_values WHERE panel_date=%s",
        (dd,),
    )
    nfeat, nrows = cur.fetchone()
    cur.execute(
        "SELECT 1 FROM core_universe_asof WHERE as_of_date=%s LIMIT 1",
        (dd,),
    )
    has_core = bool(cur.fetchone())
    iso = dd.isoformat()
    cur.execute(
        """
        SELECT count(*) FROM model_registry
        WHERE asof_snapshot::text = %s
          AND family = ANY(%s)
        """,
        (iso, list(A_FAMILIES)),
    )
    registry_a = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT count(DISTINCT family || ':' || horizon::text)
          FROM model_registry
         WHERE family = ANY(%s)
           AND horizon = ANY(%s)
           AND asof_snapshot::text = %s
        """,
        (list(A_FAMILIES), list(H_TRACK), iso),
    )
    registry_a_cells = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(DAILY_IDS), iso),
    )
    registry_daily = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(MKT_IDS), iso),
    )
    registry_mkt = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(STACK_IDS), iso),
    )
    registry_stack = int(cur.fetchone()[0] or 0)
    cur.execute("SELECT max(panel_date) FROM feature_values")
    fv_max = cur.fetchone()[0]
    st = classify_asof(dd, price_max, int(nrows or 0))
    price_max_s = None if price_max is None else str(price_max)[:10]
    at_tip = price_max_s == iso
    pack_complete = pack_is_complete(
        a_cells=registry_a_cells,
        daily=registry_daily,
        mkt=registry_mkt,
        stack=registry_stack,
        asof=dd,
        price_max=price_max,
    )
    return {
        "asof": iso,
        "status": st,
        "rc": rc_of(st),
        "price_max": price_max_s,
        "fv_max": None if fv_max is None else str(fv_max)[:10],
        "fv_nfeat": int(nfeat or 0),
        "fv_nrows": int(nrows or 0),
        "has_core": has_core,
        "registry_a": registry_a,
        "registry_a_cells": registry_a_cells,
        "registry_daily": registry_daily,
        "registry_mkt": registry_mkt,
        "registry_stack": registry_stack,
        "need_a_cells": NEED_A_CELLS,
        "at_tip": at_tip,
        "pack_complete": pack_complete,
    }


def assert_not_fake_b3(price_max: Any, asof: Any) -> Optional[str]:
    """價 < asof → 錯誤字；否則 None。純函式。"""
    st = classify_asof(asof, price_max, 1)
    if st == STATUS_FAKE_B3:
        return (
            f"假 B3：PriceAdj TAIEX max({as_date(price_max)}) < asof({as_date(asof)})"
        )
    if st == STATUS_NO_PRICE:
        return "假 B3：TaiwanStockPriceAdj 無 TAIEX 價"
    return None


ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36；不直綁還原價表字面


def taiex_price_max(cur) -> Optional[date]:
    """DB：TAIEX 還原價頂（經 tw.daily_bar_adjusted）。"""
    from augur.catalog import world_concept
    adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    cur.execute(f"SELECT max(date) FROM {adj} WHERE stock_id=%s", ("TAIEX",))
    return as_date(cur.fetchone()[0])


def refuse_if_fake_b3(cur, asof: Any) -> Optional[str]:
    """讀價頂後走 assert_not_fake_b3。訓練／特徵 until 共用。"""
    return assert_not_fake_b3(taiex_price_max(cur), asof)


def pick_lock(asof: Any, price_max: Any) -> tuple[Optional[date], Optional[str]]:
    """方向臂訓練鎖（純函式）：未指定 → 價頂（可更新最新日）；指定則不得超過價頂。"""
    pm = as_date(price_max)
    if pm is None:
        return None, "假 B3：TaiwanStockPriceAdj 無 TAIEX 價"
    if asof is None or asof == "":
        return pm, None
    err = assert_not_fake_b3(pm, asof)
    if err:
        return None, err
    return as_date(asof), None


def latest_legal(cur) -> Optional[date]:
    """可更新最新日＝TAIEX PriceAdj 價頂。不是日曆今天。"""
    return taiex_price_max(cur)


def resolve_lock(cur, asof: Any = None) -> tuple[Optional[date], Optional[str]]:
    """DB：方向臂 as-of／until。未指定 → 價頂。"""
    return pick_lock(asof, taiex_price_max(cur))


def bind_iso(cur, asof: Any = None) -> tuple[Optional[str], Optional[str]]:
    """resolve_lock → (ISO 日, None) 或 (None, 錯字)。"""
    d, err = resolve_lock(cur, asof)
    if err:
        return None, err
    return d.isoformat(), None


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    d = date(2026, 8, 7)
    chk("as_date ISO", as_date("2026-08-07") == d)
    chk("as_date date", as_date(d) == d)
    chk("ready", classify_asof(d, date(2026, 8, 12), 10) == STATUS_READY)
    chk(
        "need_collect",
        classify_asof(d, date(2026, 8, 12), 0) == STATUS_NEED_COLLECT,
    )
    chk(
        "fake_b3 今天無價",
        classify_asof(date(2026, 8, 13), date(2026, 8, 12), 99) == STATUS_FAKE_B3,
    )
    chk("no_price", classify_asof(d, None, 10) == STATUS_NO_PRICE)
    chk("rc fake=3", rc_of(STATUS_FAKE_B3) == 3)
    chk("rc collect=2", rc_of(STATUS_NEED_COLLECT) == 2)
    chk(
        "assert fake 有字",
        assert_not_fake_b3("2026-08-12", "2026-08-13") is not None,
    )
    chk(
        "assert 歷史 D 過",
        assert_not_fake_b3("2026-08-12", "2026-08-07") is None,
    )
    chk("A 包 8 族", len(A_FAMILIES) == 8)
    chk("H_TRACK 8 窗", len(H_TRACK) == 8 and NEED_A_CELLS == 64)
    chk("方向臂 id 數", NEED_DAILY == 3 and NEED_MKT == 2 and NEED_STACK == 1)
    chk(
        "hist D 不要求方向臂",
        pack_is_complete(
            a_cells=64, daily=0, mkt=0, stack=0,
            asof="2026-07-31", price_max="2026-08-14",
        ),
    )
    chk(
        "hist D 截面未齊",
        not pack_is_complete(
            a_cells=4, daily=3, mkt=2, stack=1,
            asof="2026-07-31", price_max="2026-08-14",
        ),
    )
    chk(
        "價頂缺方向臂未齊",
        not pack_is_complete(
            a_cells=64, daily=0, mkt=0, stack=0,
            asof="2026-08-14", price_max="2026-08-14",
        ),
    )
    chk(
        "價頂全包",
        pack_is_complete(
            a_cells=64, daily=3, mkt=2, stack=1,
            asof="2026-08-14", price_max="2026-08-14",
        ),
    )
    d, e = pick_lock(None, date(2026, 8, 12))
    chk("未指定鎖價頂", d == date(2026, 8, 12) and e is None)
    d, e = pick_lock("2026-08-07", "2026-08-12")
    chk("指定歷史 D", d == date(2026, 8, 7) and e is None)
    d, e = pick_lock("2026-08-13", "2026-08-12")
    chk("指定假 B3", d is None and e is not None)
    d, e = pick_lock(None, None)
    chk("無價拒鎖", d is None and e is not None)
    chk("完整性錨≠訓練鎖", COMPLETENESS_ASOF == date(2026, 5, 31))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.core.asof_ready --selftest；免 DB 免 API)")
