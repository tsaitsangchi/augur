"""augur 單來源落地 orchestrator — 把 FinMind / FRED 抓回的列，落地成 DB 表。

這支在做什麼（白話）：
- 統籌「抓 → 守門 → 寫」一條龍：呼叫 finmind/fred client 取列，過 #4 intraday 守門，
  再用 generic_schema 自動建表 + 冪等寫入（包在一段交易裡），回報 (列數 / schema / 主鍵)。
- **#4 intraday 守門**：`INTRADAY` 列出 8 個 sub-daily dataset（5秒/tick/分K/分鐘）；本系統以日為
  最小單位 → 這些 dataset **一律拒絕落地**（`ingest_finmind` 撞到就拋 `IntradayRejected`）。
- **可選稽核**（預設開）：在同一段交易裡寫一列 `data_audit_log`（哪個 dataset/股、寫了幾列）——
  與資料同進退（atomic），供無幻像對帳留痕；需 infra log 表已 bootstrap（憲章 PHASE 1）。

職責分工：抓資料在 finmind/fred（不在這）；型別/建表/upsert 在 generic_schema（不在這）；
連線/交易在 db（不在這）；本檔只「串起來 + 守 intraday 門 + 留稽核」。

守 #4（intraday 守門拒絕入庫）· #3/#1（忠實落地任意**日頻** API 表，不挑不補）· #6（交易冪等，逐 dataset 各自 commit/rollback）。
"""
from __future__ import annotations

from augur.core import db, generic_schema
from augur.ingestion import finmind, fred

# #4 日為最小單位：以下 sub-daily dataset 一律不落地（已 live 確認皆含秒級/分級時間欄）。
INTRADAY = frozenset({
    "TaiwanStockPriceTick", "TaiwanStockKBar", "TaiwanFuturesTick", "TaiwanOptionTick",
    "TaiwanStockStatisticsOfOrderBookAndTrade", "TaiwanVariousIndicators5Seconds",
    "USStockPriceMinute", "TaiwanStockEvery5SecondsIndex",
})

# `OUT_OF_UNIT`：資料量規模物理界限**排除**（doctrine 原則精華 #3/#4 · 憲章 #18、probe 實證 2026-06-23/24）——日級合格（#4）但全市場全史資料量物理裝不下/抓不完（非實作懶、非抓法不會）。
# 3 表 endpoint 行為一致（per-(股,日) 逐日結構）+ schema PK bug 風險（單列 sample 觸發 detect_keys 提早 return），全市場全史資料量物理不可行：
# - 分點 TradingDailyReport：dedicated by-broker `securities_trader_id`+`date`、per-(券商,股,日) 數十億列 TB 級。
# - 權證 WarrantTradingDailyReport：dedicated by-broker、~數千萬列 + ~178萬 calls。
# - 鉅額分點 BlockTradingDailyReport：/data data_id=股+date（end_date 不吃、per-(股,日) 逐日）、單 call 同股同日 17+ 列券商×trade_type、現 schema PK=stock_id 單欄致 16+→1 覆蓋（probe 實證 2026-06-24）。
# 排除（非暫緩）；data_id 來源備存（券商 TaiwanSecuritiesTraderInfo / 權證代號 TaiwanStockInfo）供未來擴儲+schema PK 修後重議。
OUT_OF_UNIT = frozenset({
    "TaiwanStockTradingDailyReport",
    "TaiwanStockWarrantTradingDailyReport",
    "TaiwanStockBlockTradingDailyReport",
})

# `BACKFILL_DEFERRED`：dedicated/special endpoint、**可抓**、走 dedicated 專抓；excluded＝不進 daily_datasets 自動 by-date bulk（規模、非缺資料）。
# 〔目前空集合（鉅額分點 2026-06-24 移入 OUT_OF_UNIT）；框架保留供未來其他 dedicated dataset 規劃落地時納入〕
BACKFILL_DEFERRED = frozenset()

FRED_TABLE = "fred_series"


class IntradayRejected(RuntimeError):
    """嘗試落地 intraday dataset → 依 #4 拒絕。"""


def is_intraday(dataset) -> bool:
    """該 dataset 是否為 sub-daily（#4 不收）。呼叫端可據此預先過濾。"""
    return dataset in INTRADAY


# `_AGGREGATE_DAILY`（augur-specific、官方 datasets.md 無此概念）：FinMind 回 intraday 但「無日級替代表」者，
# 抓後聚合日級衍生存（#4「只存日級衍生」、不存 intraday 原始）。值＝聚合法。實證：GoldPrice 5-min（~288 筆/日，
# 2018-）、官方標 macro daily 但實際回 intraday → 聚合每日末筆 close；早期（1990-2016）已日級（1 筆/日）亦正確。
# TaiwanStockNews（秒級時間戳新聞流、漏網 intraday）→ method='all'：date 去時間、保留同日多則（同日同 PK 交 upsert 去重）。
# 別於 INTRADAY（純 sub-day、有日級替代如 TaiwanStockPrice → 完全不收）。
_AGGREGATE_DAILY = {"GoldPrice": "close", "TaiwanStockNews": "all"}


def _aggregate_daily(rows, method="close"):
    """intraday-source rows → 日級衍生（#4「只存日級衍生」）。date 一律規約純日級（去時間）→ generic_schema
    推 DATE 不降級回 varchar。
    method='close'：每日末筆（date 字串最大者）→ 1 筆/日（價格類，如 GoldPrice 5-min;早期已日級該筆即末筆）。
    method='all'：保留同日所有列、僅 date 去時間 → 多筆/日（事件流，如 News 同日多則;同日同 PK 交 upsert 去重）。"""
    if method == "all":
        out = []
        for r in rows:
            d = str(r.get("date", ""))[:10]
            if not d:
                continue
            nr = dict(r)
            nr["date"] = d                                      # date 規約純日級（去時間）、保留同日所有列
            out.append(nr)
        return out
    by_day = {}
    for r in rows:
        d = str(r.get("date", ""))[:10]
        if not d:
            continue
        cur = by_day.get(d)
        if cur is None or str(r["date"]) > str(cur["date"]):   # 取每日末筆（date 字串最大＝最晚時間）
            by_day[d] = r
    out = []
    for d in sorted(by_day):
        nr = dict(by_day[d])
        nr["date"] = d                                          # date 規約純日級（去時間）
        out.append(nr)
    return out


def ingest_finmind(conn, dataset, *, audit=True, **params):
    """抓並落地一個 FinMind dataset（表名 = dataset）。intraday → 拒絕。回 result dict。"""
    if dataset in INTRADAY:
        raise IntradayRejected(f"{dataset}：intraday（#4 日為最小單位）→ 不落地")
    rows = finmind.fetch(dataset, **params)
    return store(conn, dataset, rows, data_id=params.get("data_id"), audit=audit)


def ingest_fred(conn, series_id, *, audit=True, **params):
    """抓並落地一個 FRED series（落地表 = fred_series）。回 result dict。
    vintage 旗標經 **params 透傳 fred.fetch；**無論 tier** 強制 (series_id, date, realtime_start)
    複合鍵（Tier A 之 realtime_start＝觀測日），令兩 tier 共表 PK 一致——否則 Tier A 先落地（PK 只到
    date）會使 Tier B vintage 多版於 ON CONFLICT 互相覆蓋＝資料流失（#8）。"""
    rows = fred.fetch(series_id, **params)
    return store(conn, FRED_TABLE, rows, data_id=series_id, audit=audit,
                 require_keys=("date", "realtime_start"))


def store(conn, table, rows, *, data_id=None, audit=True, require_keys=()):
    """落地已抓好的列（呼叫端已 fetch；如 sync 的市場別探測列，免重抓）。空列 → 回 0。
    require_keys：必納入 PK 之欄（透傳 provision_and_upsert；如 by-date 之 ('date',)）。

    一段交易內 provision_and_upsert（+ 可選稽核），原子提交（#6）。"""
    if not rows:
        return {"table": table, "rows": 0, "schema": {}, "keys": []}
    if table in _AGGREGATE_DAILY:   # intraday-source（如 GoldPrice 5-min）→ 聚合日級衍生（#4）、不存 intraday 原始
        rows = _aggregate_daily(rows, _AGGREGATE_DAILY[table])
    rk = require_keys
    if data_id is not None:   # by data_id 落地:該 data_id 對應之維度欄(值=data_id 者,如 GovBonds 之 name/匯率之 currency)強制入 PK,防不同 id 同 date 互相覆蓋塌列
        rk = tuple(set(require_keys) | {k for k in rows[0] if str(rows[0].get(k)) == str(data_id)})
    with db.transaction(conn) as cur:
        n, schema, keys = generic_schema.provision_and_upsert(cur, table, rows, require_keys=rk)
        if audit:
            cur.execute(
                "INSERT INTO data_audit_log (dataset, data_id, action, rows) VALUES (%s, %s, %s, %s)",
                (table, data_id, "upsert", n))
    return {"table": table, "rows": n, "schema": schema, "keys": keys}
