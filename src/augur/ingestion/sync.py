"""augur 全市場 sync engine — 名冊 + 動態列舉 + 全史 sync + 斷點續傳（憲章 PHASE 2-4）。

這支在做什麼（白話）：
- **PHASE 2 名冊**（`seed_roster`）：落地 `TaiwanStockInfo`（全市場名冊）→ 回全部 stock_id。
- **PHASE 4 動態列舉**（`daily_datasets`）：`finmind.list_datasets()` 拿 FinMind 全 dataset，**去掉
  intraday**（#4）→ 日頻清單；**無 hardcoded 表清單**（#3）。
- **逐 dataset sync**（`sync_finmind_dataset`）：先試「市場別」（不帶 data_id）；若 FinMind 說需要
  data_id → 自動切「逐股」模式（用 roster 跑）。**adaptive**，不靠 hardcoded 分類。
- **斷點續傳**（`_max_date` + #6）：**逐股** dataset 每股看 DB 既有 `max(date)`，只從那天起續抓；
  無表→全史。重跑安全（generic 是 `ON CONFLICT` 冪等）。
- **全市場增量**（`sync_by_date`）：不帶 data_id 逐「交易日」抓整個市場（一筆 = 一天全市場 ~4 萬檔），
  DB resume 從既有 `max(date)` 起。**每日維護 request 從 3100（逐股）→ 範圍內交易日數（個位數）**。
  適用「不帶 data_id 即回整日全市場」之 dataset；需 data_id 者回 `not-by-date-capable`。
- `sync_fred`：對給定 FRED series 清單做同樣 resume sync（落 `fred_series`）。
- `sync_all`：PHASE 2→4 一條龍（可傳 roster/dataset 子集做小範圍測試）。

職責複用：抓在 finmind/fred、建表/upsert 在 generic_schema、守門+稽核在 ingest——本檔只「排程 +
動態列舉 + adaptive 模式 + 斷點續傳」，不重複那些（#12）。

⚠️ 真正全市場全史跑屬 long-running（§一.12 每 5 分鐘回報 + §二.6 SHMM/caffeinate），由呼叫端在
授權下執行；本模組提供引擎與小範圍可測性。

守 #3（動態列舉、無 hardcoded 清單）· #4（intraday 不收）· #6（冪等 + DB-driven 斷點續傳）· #1/#2（忠實落地）。
"""
from __future__ import annotations

from datetime import date, timedelta

from augur.core import db, schema
from augur.ingestion import finmind, fred, ingest

ROSTER_TABLE = "TaiwanStockInfo"
FULL_START = "1990-01-01"   # 早於 FinMind 任何資料 → 等同全史


def seed_roster(conn):
    """PHASE 2：落地 TaiwanStockInfo（全市場名冊）→ 回 distinct stock_id list。"""
    ingest.ingest_finmind(conn, ROSTER_TABLE)
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT DISTINCT stock_id FROM "{ROSTER_TABLE}" '
                    f'WHERE stock_id IS NOT NULL ORDER BY stock_id')
        return [r[0] for r in cur.fetchall()]


def daily_datasets():
    """PHASE 4 列舉：FinMind 全 dataset 去掉 intraday（#4）+ 範圍外（#3 OUT_OF_UNIT）→ 日頻清單（#3 動態、無 hardcoded）。"""
    return [d for d in finmind.list_datasets()
            if not ingest.is_intraday(d) and d not in ingest.OUT_OF_UNIT]


def _max_date(conn, table, id_col=None, id_val=None):
    """該表（可選某 id）DB 既有 max(date)（str）；無表/無 date 欄/無資料 → None（→ 全史）。"""
    with db.transaction(conn) as cur:
        if "date" not in schema.get_dataset_columns(cur, table):
            return None
        if id_col and id_val is not None:
            cur.execute(f'SELECT max(date) FROM "{table}" WHERE "{id_col}"=%s', (id_val,))
        else:
            cur.execute(f'SELECT max(date) FROM "{table}"')
        row = cur.fetchone()
    return str(row[0]) if row and row[0] else None


def sync_finmind_dataset(conn, dataset, roster, *, full_start=FULL_START, progress=None):
    """sync 一個 FinMind dataset：市場別探測有資料→市場別；回空/需 data_id→逐股（resume）。回 summary。

    adaptive 判據（實測）：per-stock dataset 不帶 data_id 一律回 0 列、market-wide 則回資料 →
    「市場別探測（不帶 data_id）回空 → 改逐股」最 robust，不靠錯誤訊息。
    """
    if ingest.is_intraday(dataset):
        return {"dataset": dataset, "mode": "skip-intraday", "rows": 0}
    if dataset in ingest.OUT_OF_UNIT:                      # #3 範圍外（sub-stock/非股標的）→ 明文排除
        return {"dataset": dataset, "mode": "excluded-out-of-unit", "rows": 0}
    if progress:
        progress(f"  → {dataset}：分類探測（寬窗 {full_start}-，市場別/逐股判定）…")
    # 1) 分類探測：用 full_start 寬窗（不帶 data_id）。實測 per-stock dataset 唯有寬窗才可靠回空
    #    （窄窗如今日會回「全市場最新」污染判斷）；market dataset 寬窗回全史。有資料 → 市場別。
    try:
        probe = finmind.fetch(dataset, start_date=full_start)
    except finmind.FinMindError as e:
        if "data_id" not in str(e):
            raise   # 真錯誤（非「需要 data_id」）→ 上拋
        probe = []
    if probe:
        res = ingest.store(conn, dataset, probe)   # 寬窗探測即全量，直接存（冪等）
        return {"dataset": dataset, "mode": "market", "rows": res["rows"]}
    # 2) 逐股模式（resume：每股各自從 max(date) 續）
    # canonical-probe（實證 §一.10）：roster 依 stock_id 字串排序，前段多為 ETF/債券/權證（無基本面資料）；
    # 故先用大型股 2330（對所有真 per-stock dataset 皆有資料）判定——回 0/錯 → 此 dataset 非 per-stock
    # （date-based 被誤分類）→ 跳過待正確分類，避免「前段 ETF 全 0」誤殺 BalanceSheet 等真資料 dataset。
    try:
        canon = finmind.fetch(dataset, data_id="2330", start_date=full_start)
    except finmind.FinMindError:
        canon = None
    if not canon:
        # 非 per-stock → fall through 試 by-date（全市場逐交易日、不帶 data_id）。adaptive，不靠 hardcoded 清單。
        # sync_by_date 首筆若需 data_id 會自回 not-by-date-capable（自我守門）→ 此時才真的非 canonical。
        if progress:
            progress(f"  → {dataset}：canonical 2330 回 0/錯 → 改試 by-date（全市場逐交易日）…")
        bd = sync_by_date(conn, dataset, start=(_max_date(conn, dataset) or full_start), progress=progress)
        if bd.get("mode") == "by-date":
            return bd
        return {"dataset": dataset, "mode": "per-stock-non-canonical", "rows": 0, "stocks_with_data": 0}
    if progress:
        progress(f"  → {dataset}：per-stock 模式（canonical 2330 ✓）,逐 {len(roster)} 股（每 50 股回報一次）…")
    total = stocks = 0
    for i, sid in enumerate(roster, 1):
        start = _max_date(conn, dataset, "stock_id", sid) or full_start
        try:
            res = ingest.ingest_finmind(conn, dataset, data_id=sid, start_date=start)
        except finmind.FinMindError:
            continue   # 該股無此資料 → 跳過（不中斷全批）
        total += res["rows"]
        stocks += 1 if res["rows"] else 0
        if progress and i % 50 == 0:
            progress(f"  {dataset}: {i}/{len(roster)} 股、累計 {total} 列")
    return {"dataset": dataset, "mode": "per-stock", "rows": total, "stocks_with_data": stocks}


def sync_by_date(conn, dataset, *, start=None, end=None, progress=None):
    """全市場增量 by-date sync：不帶 data_id 逐交易日抓整個市場（一筆=一天全市場）+ DB resume。

    適用「不帶 data_id 即回整日全市場」之日頻 dataset（價量/法人/融資券…）；需 data_id 之 dataset
    回 mode='not-by-date-capable'。每日維護 request 從 3100（逐股）→ 範圍內交易日數（通常個位數）。
    start 預設 = DB 既有 max(date)（resume，重抓該日補結算）；DB 空且未給 start → 拒絕（首次全史請
    用 sync_finmind_dataset 逐股）。end 預設 = 今日。
    """
    if ingest.is_intraday(dataset):
        return {"dataset": dataset, "mode": "skip-intraday", "rows": 0}
    if dataset in ingest.OUT_OF_UNIT:                      # #3 範圍外 → 明文排除（與 sync_finmind_dataset 一致，增量路徑亦守）
        return {"dataset": dataset, "mode": "excluded-out-of-unit", "rows": 0}
    if start is None:
        start = _max_date(conn, dataset)
        if start is None:
            raise ValueError(f"{dataset}：DB 無既有資料且未指定 start；by-date 為增量用途，"
                             f"首次全史請用 sync_finmind_dataset（逐股）或明確給 start")
    end = end or date.today().isoformat()
    cur, last = date.fromisoformat(start[:10]), date.fromisoformat(end[:10])
    total = tdays = reqs = 0
    while cur <= last:
        if cur.weekday() >= 5:                    # 週末無交易 → 不發請求（#17 省 request）
            cur += timedelta(days=1)
            continue
        day = cur.isoformat()
        try:
            rows = finmind.fetch(dataset, start_date=day, end_date=day)   # by-date：不帶 data_id = 整日全市場
        except finmind.FinMindError as e:
            if reqs == 0 and "data_id" in str(e):                         # 首筆即需 data_id → 不支援 by-date
                return {"dataset": dataset, "mode": "not-by-date-capable", "rows": 0}
            reqs += 1
            cur += timedelta(days=1)
            continue                                                      # 某日錯 → 跳過該日，不中斷
        reqs += 1
        if rows:
            # require_keys=('date',)：by-date 單日 sample 內 stock_id 已唯一會漏掉 date，強制 date 入 PK
            # 防多日 upsert 互相覆蓋塌成每股 1 列（pilot 實證 bug）
            total += ingest.store(conn, dataset, rows, require_keys=("date",))["rows"]
            tdays += 1
        cur += timedelta(days=1)
        if progress and reqs % 20 == 0:
            progress(f"  {dataset} by-date {day}: {tdays} 交易日 / {total} 列 / {reqs} 筆")
    return {"dataset": dataset, "mode": "by-date", "rows": total, "trading_days": tdays, "requests": reqs}


def sync_fred(conn, series_ids, *, full_start=FULL_START, progress=None):
    """sync 給定 FRED series 清單（落 fred_series，每 series resume）。回 summary。"""
    total = 0
    for sid in series_ids:
        start = _max_date(conn, ingest.FRED_TABLE, "series_id", sid) or full_start
        try:
            res = ingest.ingest_fred(conn, sid, start_date=start)
        except fred.FredError:
            continue
        total += res["rows"]
        if progress:
            progress(f"  FRED {sid}: +{res['rows']} 列")
    return {"table": ingest.FRED_TABLE, "series": len(series_ids), "rows": total}


def sync_all(conn, *, roster=None, datasets=None, fred_series=None, full_start=FULL_START, progress=print):
    """PHASE 2→4 一條龍。roster/datasets/fred_series 可傳子集做小範圍；None → 全量（long-running）。"""
    if roster is None:
        if progress:
            progress("PHASE 2：seed roster…")
        roster = seed_roster(conn)
    if datasets is None:
        datasets = daily_datasets()
    if progress:
        progress(f"PHASE 4：{len(datasets)} 日頻 dataset × {len(roster)} 股")
    results = []
    for i, ds in enumerate(datasets, 1):
        r = sync_finmind_dataset(conn, ds, roster, full_start=full_start, progress=progress)
        results.append(r)
        if progress:
            progress(f"[{i}/{len(datasets)}] {ds}: {r['mode']} {r['rows']} 列")
    if fred_series:
        results.append(sync_fred(conn, fred_series, full_start=full_start, progress=progress))
    return results


def sync_all_by_date(conn, *, datasets=None, end=None, progress=print):
    """每日維護入口：對所有（或給定）日頻 dataset 跑 by-date 全市場增量（resume）。

    每 dataset 的 mode：`by-date`（成功增量）/ `no-baseline`（DB 無基線，需先 sync_finmind_dataset
    逐股初載）/ `not-by-date-capable`（需 data_id，須走逐股或逐 id 路徑）/ `skip-intraday`。
    """
    if datasets is None:
        datasets = daily_datasets()
    if progress:
        progress(f"每日維護 by-date：{len(datasets)} 日頻 dataset")
    results = []
    for i, ds in enumerate(datasets, 1):
        try:
            r = sync_by_date(conn, ds, end=end, progress=progress)
        except ValueError:
            r = {"dataset": ds, "mode": "no-baseline", "rows": 0}   # DB 無既有資料 → 需先逐股初載
        results.append(r)
        if progress:
            progress(f"[{i}/{len(datasets)}] {ds}: {r['mode']} {r.get('rows', 0)} 列 / {r.get('requests', '-')} 筆")
    return results
