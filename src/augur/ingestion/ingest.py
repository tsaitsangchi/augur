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

# `OUT_OF_UNIT`（v1.4.0 #3 重定義）：非「資料維度排除」，而是「規模物理不可行之 operational 暫緩」。
# 資料維度上合格（日級，符合 #4 唯一資料本質排除準則）；僅因 FinMind 限「單 id × 單日」查（無範圍查、
# 無 metadata 取範圍）致全市場抓取規模物理不可行 → 暫緩、待有能力補通用多維度抓取(#18)再抓，非治權排除。
# 實證 2026-06-10 規模：
# - TaiwanStockTradingDailyReport：券商分點進出明細（券商 × 股 × 日，sub-stock；單股×單日 only × 3100 股 = 數十億列）。
# - TaiwanStockWarrantTradingDailyReport：權證日成交（權證宇宙 126,368 檔）。
# - TaiwanStockBlockTradingDailyReport：鉅額交易（稀疏 → backward-probe 取樣多落空、難可靠定起點）。
OUT_OF_UNIT = frozenset({
    "TaiwanStockTradingDailyReport",
    "TaiwanStockWarrantTradingDailyReport",
    "TaiwanStockBlockTradingDailyReport",
})

FRED_TABLE = "fred_series"


class IntradayRejected(RuntimeError):
    """嘗試落地 intraday dataset → 依 #4 拒絕。"""


def is_intraday(dataset) -> bool:
    """該 dataset 是否為 sub-daily（#4 不收）。呼叫端可據此預先過濾。"""
    return dataset in INTRADAY


def ingest_finmind(conn, dataset, *, audit=True, **params):
    """抓並落地一個 FinMind dataset（表名 = dataset）。intraday → 拒絕。回 result dict。"""
    if dataset in INTRADAY:
        raise IntradayRejected(f"{dataset}：intraday（#4 日為最小單位）→ 不落地")
    rows = finmind.fetch(dataset, **params)
    return store(conn, dataset, rows, data_id=params.get("data_id"), audit=audit)


def ingest_fred(conn, series_id, *, audit=True, **params):
    """抓並落地一個 FRED series（落地表 = fred_series）。回 result dict。"""
    rows = fred.fetch(series_id, **params)
    return store(conn, FRED_TABLE, rows, data_id=series_id, audit=audit)


def store(conn, table, rows, *, data_id=None, audit=True, require_keys=()):
    """落地已抓好的列（呼叫端已 fetch；如 sync 的市場別探測列，免重抓）。空列 → 回 0。
    require_keys：必納入 PK 之欄（透傳 provision_and_upsert；如 by-date 之 ('date',)）。

    一段交易內 provision_and_upsert（+ 可選稽核），原子提交（#6）。"""
    if not rows:
        return {"table": table, "rows": 0, "schema": {}, "keys": []}
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
