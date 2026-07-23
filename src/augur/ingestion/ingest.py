"""augur 單來源落地 orchestrator — 把 FinMind / FRED 抓回的列，落地成 DB 表。

🎯 這支在做什麼（白話）：
- 統籌「抓 → 守門 → 寫」一條龍：呼叫 finmind/fred client 取列，過 #4 intraday 守門，
  再用 generic_schema 自動建表 + 冪等寫入（包在一段交易裡），回報 (列數 / schema / 主鍵)。
- **#4 intraday 守門**：`INTRADAY` 列出 8 個 sub-daily dataset（5秒/tick/分K/分鐘）；本系統以日為
  最小單位 → 這些 dataset **一律拒絕落地**（`ingest_finmind` 撞到就拋 `IntradayRejected`）。
- **可選稽核**（預設開）：在同一段交易裡寫一列 `data_audit_log`（哪個 dataset/股、寫了幾列）——
  與資料同進退（atomic），供無幻像對帳留痕；需 infra log 表已 bootstrap（憲章 PHASE 1）。

職責分工：抓資料在 finmind/fred（不在這）；型別/建表/upsert 在 generic_schema（不在這）；
連線/交易在 db（不在這）；本檔只「串起來 + 守 intraday 門 + 留稽核」。

守 #4（intraday 守門拒絕入庫）· #3/#1（忠實落地任意**日頻** API 表，不挑不補）· #6（交易冪等，逐 dataset 各自 commit/rollback）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.ingestion.ingest              # 印用途+公開入口（唯讀）
  python -m augur.ingestion.ingest --selftest   # 純紅綠自測（零 IO）
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
# ↑ 2026-07-13 #29b 整改:三個 frozenset/dict 降級為「catalog-build seed + DB 不可用時 fail-safe 後備」
#   (sanctioned seed 模式);runtime 選表/聚合一律 DB-first(catalog_exclusions/aggregate_method),
#   catalog build 仍讀本檔集合寫 DB(code→DB 種子方向,不循環)。


def catalog_exclusions(cur):
    """dataset_catalog 排除集(excluded=true)——runtime 選表之單一 DB 路徑(#29b)。
    catalog 缺表/空/查詢失敗 → None(呼叫端退 code-set 後備;bootstrap PHASE<2 亦安全)。"""
    try:
        cur.execute("SELECT dataset FROM dataset_catalog WHERE excluded")
        rows = {r[0] for r in cur.fetchall()}
        return rows or None
    except Exception:
        return None


def aggregate_method(dataset, conn=None):
    """該 dataset 之日級聚合法('close'/'all')或 None。DB-first(#29b):
    dataset_catalog.aggregate_daily_method 欄存在 → DB 為 SSOT(欄有值用之、無值=非聚合表);
    欄未建(migrate_catalog_aggregate_ddl 未跑)或無 conn/查詢失敗 → 退 code seed dict(過渡零風險)。"""
    if conn is not None:
        try:
            with db.transaction(conn) as cur:
                cur.execute("SELECT 1 FROM information_schema.columns "
                            "WHERE table_name='dataset_catalog' AND column_name='aggregate_daily_method'")
                if cur.fetchone():
                    cur.execute("SELECT aggregate_daily_method FROM dataset_catalog WHERE dataset=%s", (dataset,))
                    row = cur.fetchone()
                    return row[0] if row and row[0] else None
        except Exception:
            pass
    return _AGGREGATE_DAILY.get(dataset)


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


def _fred_pk_ok(conn):
    """fred_series 既有 PK 是否含 realtime_start（#8 PIT 前提）。表不存在→True（首建即用正確 PK）。
    require_keys 因『PK 首建固定』對既有舊表永不生效（稽核 2026-07-04 決1）→ 此為程式守門。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('fred_series')")
        if cur.fetchone()[0] is None:
            return True
        cur.execute("SELECT a.attname FROM pg_index i JOIN pg_attribute a "
                    "ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) "
                    "WHERE i.indrelid='fred_series'::regclass AND i.indisprimary")
        return "realtime_start" in {r[0] for r in cur.fetchall()}


def ingest_fred(conn, series_id, *, audit=True, **params):
    """抓並落地一個 FRED series（落地表 = fred_series）。回 result dict。
    vintage 旗標經 **params 透傳 fred.fetch；**無論 tier** 強制 (series_id, date, realtime_start)
    複合鍵（Tier A 之 realtime_start＝觀測日），令兩 tier 共表 PK 一致——否則 Tier A 先落地（PK 只到
    date）會使 Tier B vintage 多版於 ON CONFLICT 互相覆蓋＝資料流失（#8）。
    **落地前守門（稽核 2026-07-04 決1）**：既有 fred_series PK 不含 realtime_start 即拒落地——
    把『vintage 靜默塌版』變成程式強制錯誤（require_keys 對舊表無效之根治=DROP 重建）。"""
    if not _fred_pk_ok(conn):
        raise finmind.FinMindError(
            "fred_series 既有 PK 不含 realtime_start（#8 PIT 前提未成立）；Tier B vintage 多版會於 "
            "ON CONFLICT 靜默塌版=資料流失。→ 決策層授權後 DROP fred_series 再跑 scripts/sync_macro.py "
            "重建（PK 首建固定之唯一根治，稽核決1）。")
    rows = fred.fetch(series_id, **params)
    return store(conn, FRED_TABLE, rows, data_id=series_id, audit=audit,
                 require_keys=("date", "realtime_start"))


def store(conn, table, rows, *, data_id=None, audit=True, require_keys=(),
          snapshot_reason=None, snapshot_run_id=None):
    """落地已抓好的列（呼叫端已 fetch；如 sync 的市場別探測列，免重抓）。空列 → 回 0。
    require_keys：必納入 PK 之欄（透傳 provision_and_upsert；如 by-date 之 ('date',)）。
    snapshot_reason：**預設 None＝主路徑不快照、語義不變**；僅 heal 呼叫端透傳非 None（'heal_by_date'/
      'daily_heal'）→ heal 覆寫前把被取代原值快照至 raw_supersede_log（AUD-02、P4.E5，與寫入同交易）。
    snapshot_run_id：決策 B——attestation_run_id nullable（預設 None；heal 直呼 sync 之路徑本無對帳 run 可帶、
      結構上恆 None，非待回填；不改 attestation_result 寫序）。

    一段交易內 provision_and_upsert（+ 可選稽核），原子提交（#6）。"""
    if not rows:
        return {"table": table, "rows": 0, "schema": {}, "keys": []}
    agg = aggregate_method(table, conn)   # DB-first(#29b);intraday-source（如 GoldPrice 5-min）→ 聚合日級衍生（#4）、不存 intraday 原始
    if agg:
        rows = _aggregate_daily(rows, agg)
    rk = require_keys
    if data_id is not None:   # by data_id 落地:該 data_id 對應之維度欄(值=data_id 者,如 GovBonds 之 name/匯率之 currency)強制入 PK,防不同 id 同 date 互相覆蓋塌列
        rk = tuple(set(require_keys) | {k for k in rows[0] if str(rows[0].get(k)) == str(data_id)})
    with db.transaction(conn) as cur:
        n, schema, keys = generic_schema.provision_and_upsert(
            cur, table, rows, require_keys=rk,
            snapshot_reason=snapshot_reason, snapshot_run_id=snapshot_run_id)
        if audit:
            cur.execute(
                "INSERT INTO data_audit_log (dataset, data_id, action, rows) VALUES (%s, %s, %s, %s)",
                (table, data_id, "upsert", n))
    return {"table": table, "rows": n, "schema": schema, "keys": keys}


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成資料紅綠測 is_intraday/_aggregate_daily 之
    #4 核心不變式（intraday 守門、close 取每日末筆、all 保留同日多列、date 規約純日級）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("is_intraday intraday→True", is_intraday("TaiwanStockPriceTick") is True)
    chk("is_intraday 日級→False", is_intraday("TaiwanStockPrice") is False)
    rows = [{"date": "2020-01-01 09:00", "close": 1}, {"date": "2020-01-01 13:00", "close": 2},
            {"date": "2020-01-02 10:00", "close": 3}]
    c = _aggregate_daily(rows, "close")
    chk("close 每日 1 列（3 列→2 日）", len(c) == 2)
    chk("close 取每日末筆（01-01→close=2）",
        next(r for r in c if r["date"] == "2020-01-01")["close"] == 2)
    chk("close date 規約純日級（去時間）", all(len(str(r["date"])) == 10 for r in c))
    a = _aggregate_daily(rows, "all")
    chk("all 保留同日多列（3 列→3 列）", len(a) == 3)
    chk("all date 規約純日級（去時間）", all(len(str(r["date"])) == 10 for r in a))
    chk("無 date 之列丟棄", _aggregate_daily([{"close": 9}], "all") == [])
    chk("FRED_TABLE 常數", FRED_TABLE == "fred_series")
    chk("IntradayRejected 為 RuntimeError 子類", issubclass(IntradayRejected, RuntimeError))
    for nm in ("ingest_finmind", "ingest_fred", "store", "catalog_exclusions", "aggregate_method"):
        chk(f"公開入口 {nm} 存在", callable(globals().get(nm)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.ingestion.ingest --selftest;免 DB 免 API)")
