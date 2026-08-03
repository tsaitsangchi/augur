"""🎯 資料新鮮度判準——「這張表還在更新嗎」的純函式核心（M-G9）。

白話：catalog 97 列（表實存 86、其中具 `date` 欄 82）沒有任何 per-dataset 新鮮度哨兵，所以
`TaiwanStockTotalReturnIndex` 從 2026-07-09 起停更 16 個交易日、下游三處靜默失效，
沒有任何機制會亮紅燈。本模組把「怎麼便宜地問到最新日期」與「落後多久才算紅」
兩件事寫成**可個別驗證的純函式**；DB／IO 一律留在 `scripts/check_dataset_freshness.py`。

## 為什麼不能裸 `max(date)`（設計約束、非可選）

本庫 82 張具 `date` 欄之 vendor 表，其索引幾乎都是 `(stock_id, date)` 這種
**date 非前導欄**的形狀 ⇒ `max(date)` 得掃完整棵索引。實測 `TaiwanStockPriceAdj`
單表 **20.27s**、全量 82 表逾 **120s 被 timeout 中斷**（優化計畫書 20260803 第 14 步）。
本模組給三條索引友善路徑（`probe_plan` 決定）＋一條堆尾預探（CLI 之 `tail_dates`）：

    date-leading  date 為某索引之前導欄 → `ORDER BY date DESC LIMIT 1`，O(log n)
    skip-scan     date 位於索引第 2 欄  → 對前導欄跑 loose index scan（遞迴 CTE），
                  且**達標即早停**（runmax ≥ 期望日就不必再走完 55,674 個 stock_id）
    plain-max     其餘（date 不在任何索引／位於第 3 欄以後）→ 裸 max；本庫此類皆 ≤ 48 萬列

    tail-probe    先讀堆尾 N 個 block 的 `max(date)`——**單向有效**：讀到的日期是
                  真實存在之列，故「堆尾已達期望日」⇒ 全表必達 ⇒ 可判綠（此為下界、
                  非全表 max，故 `observed_is_floor=True` 誠實標記）；堆尾**未**達標
                  則**不得**據以判紅，必須落到上面三條精確路徑。實測 0.03–0.2s／表。

## 紅／黃／綠三態（為什麼不是二態）

停更 16 個交易日的 TRI 與「本來就一季才一列」的 `TaiwanStockBalanceSheet`，
用同一把「落後 N 日即紅」的尺會把後者一起判紅 ⇒ 哨兵三天內就被當狼來了。
故本模組**從資料自身推節奏**（`median_gap_trading_days`，取堆尾最近 12 個相異日期之
間距中位數），只有「本來每個交易日都更新、現在不更了」才判 **red**；
週期／事件型（間距 > 2 交易日）與 snapshot 型落 **amber**（誠實揭露、不假綠、也不假紅）。

守 #15（紅燈要會亮、假綠不留：堆尾預探只准判綠不准判紅，即此原則之機械化）·
#9／#10（每個日期出自真 query，非估算）· #29(b)（節奏自資料推得、不寫死每張表的預期頻率）·
#12（判準單一住所：CLI 只做 IO 與列印，不重寫任何一條判準）。

執行指令矩陣（本檔＝library #18；免 DB 免 API 可個別驗證）：
  python -m augur.audit.freshness              # 印用途＋公開入口（唯讀）
  python -m augur.audit.freshness --selftest   # 純紅綠自測（零 IO；fixture 取自 live 真輸出）
"""
from __future__ import annotations

import bisect
import statistics
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Sequence

# 堆尾預探讀幾個 block（8KB/block）：2000 block ＝ 16MB，實測 0.03–0.2s／表。
TAIL_BLOCKS = 2000
# 堆尾取幾個相異日期用來推節奏：12 個 → 11 段間距，足以分辨日更／週更／月更／季更。
TAIL_DATE_SAMPLE = 12
# 容忍落後幾個交易日才判非綠（期望日已扣掉 catalog 之 finalize_lag_days，此為額外緩衝）。
DEFAULT_MAX_LAG_TDAYS = 2
# 間距中位數 ≤ 此值才算「日更表」——只有日更表停更才判 red。
DAILY_CADENCE_MAX_TDAYS = 2
# attestation_mode 屬「名錄快照型」者不以日更判紅（catalog 已載明其非增量語意）。
NON_DAILY_ATTESTATION_MODES = ("snapshot",)

PROBE_DATE_LEADING = "date-leading"
PROBE_SKIP_SCAN = "skip-scan"
PROBE_PLAIN_MAX = "plain-max"

STATUS_GREEN = "green"
STATUS_AMBER = "amber"
STATUS_RED = "red"


@dataclass
class Probe:
    """一張表要用哪條索引友善路徑問最新日期。`key` 只在 skip-scan 有值（＝前導欄名）。"""

    mode: str
    key: Optional[str] = None


@dataclass
class DatasetFreshness:
    """單一 dataset 之新鮮度事實表（全欄皆有真實來源，無估算欄）。"""

    dataset: str
    observed: Optional[date] = None
    observed_is_floor: bool = False      # True ＝ observed 來自堆尾預探（下界，非全表 max）
    expected: Optional[date] = None
    lag_tdays: Optional[int] = None
    cadence_tdays: Optional[float] = None
    probe_mode: Optional[str] = None
    frequency: Optional[str] = None
    attestation_mode: Optional[str] = None
    finalize_lag_days: Optional[int] = None
    status: str = STATUS_AMBER
    reason: str = ""
    elapsed_sec: float = 0.0
    notes: list = field(default_factory=list)


# ── 探測路徑選擇（純函式；輸入＝pg_index 之真實欄序） ─────────────────────────

def probe_plan(index_key_columns: Sequence[Sequence[str]], date_col: str = "date") -> Probe:
    """依索引欄序挑最便宜的路徑。

    `index_key_columns`：該表每個 btree 索引之 **key 欄名依序**（`indkey` 前 `indnkeyatts` 欄）。
    取 `date_col` 出現位置最前者：位置 0 → date-leading；位置 1 → skip-scan（前導欄即其鍵）；
    位置 ≥2 或不在任何索引 → plain-max（多欄前綴之 row-wise 比較無法走索引——實測
    `TaiwanStockIndustryChain` 之 3 欄前綴遞迴跑 200s 未完，故不納入 skip-scan）。
    """
    best_pos = None
    best_prefix: Sequence[str] = ()
    for cols in index_key_columns:
        if date_col not in cols:
            continue
        pos = list(cols).index(date_col)
        if best_pos is None or pos < best_pos:
            best_pos, best_prefix = pos, list(cols)[:pos]
    if best_pos is None or best_pos >= 2:
        return Probe(PROBE_PLAIN_MAX)
    if best_pos == 0:
        return Probe(PROBE_DATE_LEADING)
    return Probe(PROBE_SKIP_SCAN, best_prefix[0])


# ── 交易日曆換算（純函式；calendar ＝ 已排序之交易日 list） ───────────────────

def expected_asof(calendar: Sequence[date], today: date, finalize_lag_days: int = 1) -> Optional[date]:
    """期望最新日 ＝ 不晚於 `today − finalize_lag_days` 之最後一個交易日（無則 None）。

    扣 `finalize_lag_days` 是 catalog 自己登錄的「未定稿邊緣日」寬限（外盤／T+1 類為 2–3），
    與 `daily_maintenance` 對帳窗上限同一口徑，避免哨兵每天早上都對邊緣日假紅。
    """
    cutoff = date.fromordinal(today.toordinal() - max(0, int(finalize_lag_days or 0)))
    i = bisect.bisect_right(list(calendar), cutoff)
    return calendar[i - 1] if i > 0 else None


def trading_day_lag(observed: Optional[date], expected: Optional[date],
                    calendar: Sequence[date]) -> Optional[int]:
    """落後幾個交易日 ＝ 日曆中落在 (observed, expected] 之交易日數；observed ≥ expected → 0。"""
    if observed is None or expected is None:
        return None
    if observed >= expected:
        return 0
    cal = list(calendar)
    lo = bisect.bisect_right(cal, observed)
    hi = bisect.bisect_right(cal, expected)
    return max(0, hi - lo)


def median_gap_trading_days(dates_desc: Sequence[date],
                            calendar: Sequence[date]) -> Optional[float]:
    """自最近若干相異日期推更新節奏（間距中位數、單位＝交易日）。少於 2 個日期 → None。

    用中位數而非平均：連假、除息停牌等單一長間距不該把日更表誤推成週更表。
    """
    ds = sorted({d for d in dates_desc if d is not None}, reverse=True)
    if len(ds) < 2:
        return None
    gaps = []
    for newer, older in zip(ds, ds[1:]):
        g = trading_day_lag(older, newer, calendar)
        if g is not None and g > 0:
            gaps.append(g)
    return statistics.median(gaps) if gaps else None


# ── 判準（純函式；本模組唯一決定紅綠之處） ───────────────────────────────────

def classify(*, observed: Optional[date], expected: Optional[date], lag_tdays: Optional[int],
             cadence_tdays: Optional[float], attestation_mode: Optional[str] = None,
             max_lag_tdays: int = DEFAULT_MAX_LAG_TDAYS) -> tuple:
    """→ (status, reason)。**red 只給「本來日更、現在停更」**，其餘落後一律 amber。"""
    if observed is None:
        return STATUS_AMBER, "無可判讀之最新日期（表空／date 欄非可解析日期）——不判綠"
    if expected is None or lag_tdays is None:
        return STATUS_AMBER, "無交易日曆可比對，無法判齡"
    if lag_tdays <= max_lag_tdays:
        return STATUS_GREEN, f"落後 {lag_tdays} 個交易日（容忍 {max_lag_tdays}）"
    if (attestation_mode or "") in NON_DAILY_ATTESTATION_MODES:
        return STATUS_AMBER, (f"落後 {lag_tdays} 個交易日，但 attestation_mode="
                              f"{attestation_mode}（名錄快照型，不以日更判紅）")
    if cadence_tdays is None:
        return STATUS_AMBER, f"落後 {lag_tdays} 個交易日，但相異日期不足 2 個、推不出更新節奏"
    if cadence_tdays > DAILY_CADENCE_MAX_TDAYS:
        return STATUS_AMBER, (f"落後 {lag_tdays} 個交易日；本表節奏 ≈ {cadence_tdays:g} 交易日／次"
                              f"（週期／事件型，非日更）")
    return STATUS_RED, (f"停更 {lag_tdays} 個交易日；本表節奏 ≈ {cadence_tdays:g} 交易日／次"
                        f"（日更表停更）")


def rc_of(statuses: Sequence[str], strict: bool = False) -> int:
    """離開碼：有 red → 1；`--strict` 下 amber 亦 1；否則 0。"""
    if STATUS_RED in statuses:
        return 1
    if strict and STATUS_AMBER in statuses:
        return 1
    return 0


# ── 自測（#35：fixture 取自 live 真輸出、紅綠雙向、下游絆線；免 DB 免 API） ──

# 取自 live `pg_index` 之真實欄序（2026-08-03，查詢見本檔 docstring 上游 CLI）：
#   SELECT array_agg(a.attname ORDER BY k.ord) ... WHERE k.ord <= x.indnkeyatts
_REAL_INDEX_COLS = {
    "TaiwanStockTotalReturnIndex": [["stock_id", "date"]],
    "TaiwanOptionDaily": [["date", "option_id", "contract_date", "strike_price", "call_put",
                           "open", "max", "min", "close", "volume", "settlement_price",
                           "open_interest", "trading_session"]],
    "TaiwanStockIndustryChain": [["stock_id", "industry", "sub_industry", "date"]],
    "TaiwanStockMonthRevenue": [["stock_id", "country", "date"]],
    "TaiwanStockInfo": [["stock_id", "type", "industry_category"]],
}

# 取自 live `TaiwanStockTradingDate` 之真實交易日（2026-06-01 ～ 2026-08-10，共 50 日）。
_REAL_CALENDAR = [date.fromisoformat(s) for s in (
    "2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05", "2026-06-08",
    "2026-06-09", "2026-06-10", "2026-06-11", "2026-06-12", "2026-06-15", "2026-06-16",
    "2026-06-17", "2026-06-18", "2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25",
    "2026-06-26", "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03",
    "2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-13",
    "2026-07-14", "2026-07-15", "2026-07-16", "2026-07-17", "2026-07-20", "2026-07-21",
    "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-27", "2026-07-28", "2026-07-29",
    "2026-07-30", "2026-07-31", "2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06",
    "2026-08-07", "2026-08-10")]

# 取自 live 堆尾預探之真實相異日期序列（2026-08-03；`ctid >= '(blocks-2000,0)'::tid`）。
_REAL_TAIL_DATES = {
    "TaiwanStockTotalReturnIndex": ["2026-07-09", "2026-07-08", "2026-07-07", "2026-07-06",
                                    "2026-07-03", "2026-07-02", "2026-07-01", "2026-06-30",
                                    "2026-06-29", "2026-06-26", "2026-06-25", "2026-06-24"],
    "TaiwanStockBalanceSheet": ["2026-06-30", "2026-03-31"],
    "TaiwanStockWeekPrice": ["2026-07-27", "2026-07-20"],
    "TaiwanStockPriceAdj": ["2026-07-31", "2026-07-30", "2026-07-29", "2026-07-28",
                            "2026-07-27", "2026-07-24", "2026-07-23", "2026-07-22",
                            "2026-07-21", "2026-07-20", "2026-07-17", "2026-07-16"],
    "JapanStockInfo": ["2019-01-14"],
}


def _tail(name):
    return [date.fromisoformat(s) for s in _REAL_TAIL_DATES[name]]


def _selftest() -> int:
    rc = 0

    def chk(label, cond):
        nonlocal rc
        print(f"  {'✓' if cond else '✗FAIL'} {label}")
        if not cond:
            rc = 1

    cal = _REAL_CALENDAR
    # 1) 路徑選擇——設計約束之機械載體：`(stock_id, date)` 一律不得掉回裸 max
    chk("TRI 之 (stock_id,date) → skip-scan，鍵＝stock_id",
        probe_plan(_REAL_INDEX_COLS["TaiwanStockTotalReturnIndex"])
        == Probe(PROBE_SKIP_SCAN, "stock_id"))
    chk("TaiwanOptionDaily 之 date 前導 → date-leading",
        probe_plan(_REAL_INDEX_COLS["TaiwanOptionDaily"]).mode == PROBE_DATE_LEADING)
    chk("3 欄前綴（IndustryChain）→ plain-max（row-wise 比較走不了索引）",
        probe_plan(_REAL_INDEX_COLS["TaiwanStockIndustryChain"]).mode == PROBE_PLAIN_MAX)
    chk("2 欄前綴（MonthRevenue）→ plain-max",
        probe_plan(_REAL_INDEX_COLS["TaiwanStockMonthRevenue"]).mode == PROBE_PLAIN_MAX)
    chk("索引不含 date（TaiwanStockInfo）→ plain-max",
        probe_plan(_REAL_INDEX_COLS["TaiwanStockInfo"]).mode == PROBE_PLAIN_MAX)
    chk("無任何索引 → plain-max（不 crash）", probe_plan([]).mode == PROBE_PLAIN_MAX)
    chk("多索引取 date 位置最前者（(stock_id,date) + (date)）→ date-leading",
        probe_plan([["stock_id", "date"], ["date"]]).mode == PROBE_DATE_LEADING)

    # 2) 期望日：today=2026-08-03(一)、lag=1 → 08-02(日) 非交易日 → 退回 07-31(五)
    chk("finalize_lag=1 之期望日 ＝ 2026-07-31",
        expected_asof(cal, date(2026, 8, 3), 1) == date(2026, 7, 31))
    chk("finalize_lag=0 之期望日 ＝ 2026-08-03（當日即交易日）",
        expected_asof(cal, date(2026, 8, 3), 0) == date(2026, 8, 3))
    chk("日曆全在未來 → None（不假裝有期望日）",
        expected_asof(cal, date(2026, 1, 1), 1) is None)

    # 3) 落後日數：TRI 07-09 → 07-31 之間確為 16 個交易日（逐日可數，見 _REAL_CALENDAR）
    chk("TRI 07-09→07-31 ＝ 16 個交易日",
        trading_day_lag(date(2026, 7, 9), date(2026, 7, 31), cal) == 16)
    chk("已追平 → 0", trading_day_lag(date(2026, 7, 31), date(2026, 7, 31), cal) == 0)
    chk("超前（未來日）→ 0", trading_day_lag(date(2026, 12, 1), date(2026, 7, 31), cal) == 0)
    chk("observed 缺 → None（不當 0）", trading_day_lag(None, date(2026, 7, 31), cal) is None)

    # 4) 節奏：真堆尾序列 → 日更／週更／季更三分
    chk("TRI 堆尾 12 日 → 節奏 1 交易日（日更）",
        median_gap_trading_days(_tail("TaiwanStockTotalReturnIndex"), cal) == 1)
    chk("PriceAdj 堆尾 12 日 → 節奏 1 交易日（日更）",
        median_gap_trading_days(_tail("TaiwanStockPriceAdj"), cal) == 1)
    chk("WeekPrice 堆尾（07-27／07-20）→ 節奏 5 交易日（週更）",
        median_gap_trading_days(_tail("TaiwanStockWeekPrice"), cal) == 5)
    chk("BalanceSheet 堆尾（06-30／03-31）→ 節奏 > 2 交易日（季更）",
        (median_gap_trading_days(_tail("TaiwanStockBalanceSheet"), cal) or 0)
        > DAILY_CADENCE_MAX_TDAYS)
    chk("單一日期（JapanStockInfo）→ None（推不出節奏、不猜）",
        median_gap_trading_days(_tail("JapanStockInfo"), cal) is None)

    # 5) 判準紅綠雙向——同一組 TRI 事實，只換 observed 就必須翻面
    tri_cadence = median_gap_trading_days(_tail("TaiwanStockTotalReturnIndex"), cal)
    exp = expected_asof(cal, date(2026, 8, 3), 1)
    red = classify(observed=date(2026, 7, 9), expected=exp,
                   lag_tdays=trading_day_lag(date(2026, 7, 9), exp, cal),
                   cadence_tdays=tri_cadence, attestation_mode="byte")
    green = classify(observed=exp, expected=exp,
                     lag_tdays=trading_day_lag(exp, exp, cal),
                     cadence_tdays=tri_cadence, attestation_mode="byte")
    chk("TRI 停在 07-09 → red", red[0] == STATUS_RED)
    chk("TRI 追平 07-31 → green（同一把尺、雙向鑑別）", green[0] == STATUS_GREEN)
    chk("落後但季更（BalanceSheet 節奏）→ amber 而非 red",
        classify(observed=date(2026, 6, 30), expected=exp, lag_tdays=22,
                 cadence_tdays=median_gap_trading_days(_tail("TaiwanStockBalanceSheet"), cal),
                 attestation_mode="byte")[0] == STATUS_AMBER)
    chk("落後且 snapshot 型 → amber（catalog 已載明非增量）",
        classify(observed=date(2019, 1, 14), expected=exp, lag_tdays=1800,
                 cadence_tdays=1.0, attestation_mode="snapshot")[0] == STATUS_AMBER)
    chk("無 observed → amber（不判綠）",
        classify(observed=None, expected=exp, lag_tdays=None,
                 cadence_tdays=None)[0] == STATUS_AMBER)
    chk("容忍值放寬到 20 → TRI 轉綠（門檻參數化之證明）",
        classify(observed=date(2026, 7, 9), expected=exp, lag_tdays=16,
                 cadence_tdays=tri_cadence, attestation_mode="byte",
                 max_lag_tdays=20)[0] == STATUS_GREEN)

    # 6) 下游絆線：判定 → 離開碼之對映即 CLI 所用者
    chk("rc：有 red → 1", rc_of([STATUS_GREEN, STATUS_AMBER, STATUS_RED]) == 1)
    chk("rc：全綠含 amber → 0", rc_of([STATUS_GREEN, STATUS_AMBER]) == 0)
    chk("rc：--strict 下 amber → 1", rc_of([STATUS_GREEN, STATUS_AMBER], strict=True) == 1)

    print("自測：" + ("全通過 ✓" if rc == 0 else "有 FAIL ✗"))
    return rc


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("## ")[0].strip())
    print("公開入口：probe_plan / expected_asof / trading_day_lag / "
          "median_gap_trading_days / classify / rc_of")
    print("(自測：python -m augur.audit.freshness --selftest;免 DB 免 API)")
