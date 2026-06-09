"""augur 全市場 sync engine — 名冊 + 動態列舉 + 全史 sync + 斷點續傳（憲章 PHASE 2-4）。

這支在做什麼（白話）：
- **PHASE 2 名冊**（`seed_roster`）：落地 `TaiwanStockInfo`（全市場名冊）→ 回全部 stock_id。
- **PHASE 4 動態列舉**（`daily_datasets`）：`finmind.list_datasets()` 拿 FinMind 全 dataset，**去掉
  intraday**（#4）→ 日頻清單；**無 hardcoded 表清單**（#3）。
- **逐 dataset sync**（`sync_finmind_dataset`）：先試「市場別」（不帶 data_id）；若 FinMind 說需要
  data_id → 自動切「逐股」模式（用 roster 跑）。**adaptive**，不靠 hardcoded 分類。
- **斷點續傳**（`_max_date` + #6）：**逐股** dataset 每股看 DB 既有 `max(date)`，只從那天起續抓；
  無表→全史。重跑安全（generic 是 `ON CONFLICT` 冪等）。⚠️ **market dataset 目前每次重抓全史**
  （分類探測須用寬窗才可靠）；market 增量 resume + 超大 market 表分日期段抓 = 待 production 優化。
- `sync_fred`：對給定 FRED series 清單做同樣 resume sync（落 `fred_series`）。
- `sync_all`：PHASE 2→4 一條龍（可傳 roster/dataset 子集做小範圍測試）。

職責複用：抓在 finmind/fred、建表/upsert 在 generic_schema、守門+稽核在 ingest——本檔只「排程 +
動態列舉 + adaptive 模式 + 斷點續傳」，不重複那些（#12）。

⚠️ 真正全市場全史跑屬 long-running（§一.12 每 5 分鐘回報 + §二.6 SHMM/caffeinate），由呼叫端在
授權下執行；本模組提供引擎與小範圍可測性。

守 #3（動態列舉、無 hardcoded 清單）· #4（intraday 不收）· #6（冪等 + DB-driven 斷點續傳）· #1/#2（忠實落地）。
"""
from __future__ import annotations

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
    """PHASE 4 列舉：FinMind 全 dataset 去掉 intraday（#4）→ 日頻清單（#3 動態、無 hardcoded）。"""
    return [d for d in finmind.list_datasets() if not ingest.is_intraday(d)]


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
    total = stocks = 0
    for i, sid in enumerate(roster, 1):
        start = _max_date(conn, dataset, "stock_id", sid) or full_start
        try:
            res = ingest.ingest_finmind(conn, dataset, data_id=sid, start_date=start)
        except finmind.FinMindError:
            continue   # 該股無此資料 → 跳過（不中斷全批）
        total += res["rows"]
        stocks += 1 if res["rows"] else 0
        if progress and i % 200 == 0:
            progress(f"  {dataset}: {i}/{len(roster)} 股、累計 {total} 列")
    return {"dataset": dataset, "mode": "per-stock", "rows": total, "stocks_with_data": stocks}


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
