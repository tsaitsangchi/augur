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

import concurrent.futures as cf
from datetime import date, timedelta

import psycopg2

from augur.core import db, schema
from augur.ingestion import finmind, fred, ingest

ROSTER_TABLE = "TaiwanStockInfo"
FULL_START = "1990-01-01"   # **僅 FinMind** backward-search / 寬窗探測之 outer-bound（早於任何 FinMind 資料、API 只回實際範圍→等同全史,#18 最早日由 API 決定）。
                            # 非 per-stock fetch 起點（用 _data_era_start 取 API 元年）、非 FRED 起點（FRED 有 pre-1990 → start=None 全史,見 sync_fred）
PER_STOCK_WORKERS = 32       # 逐股抓並發數（fetch 並發、DB 寫序列；start rate 仍受 _pace 約束在 ~1/s 安全值）
                            # 實證 2026-06-11:3/4 並發皆 0 ban、throughput ~1/s（pace-bound）;4 在 API 中速(3-8s)時較 3 有 headroom;現 32（#27 試錯逼近更高並發、start rate 仍 _pace-bound）
                            # 安全來源:thread-safe _pace 預約時槽 → start rate ≤1/s（與單流同,IP 對外速率不變,#17/#24）


def seed_roster(conn):
    """PHASE 2：落地 TaiwanStockInfo（全市場名冊）→ 回 distinct stock_id list。"""
    ingest.ingest_finmind(conn, ROSTER_TABLE)
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT DISTINCT stock_id FROM "{ROSTER_TABLE}" '
                    f'WHERE stock_id IS NOT NULL ORDER BY stock_id')
        return [r[0] for r in cur.fetchall()]


def daily_datasets():
    """PHASE 4 列舉：FinMind 全 dataset 去掉 intraday（#4）+ OUT_OF_UNIT（分點/權證 資料量物理排除 #3/#4）+ BACKFILL_DEFERRED（鉅額可抓但 scope 待決）→ 日頻清單（#3 動態、無 hardcoded）。"""
    return [d for d in finmind.list_datasets()
            if not ingest.is_intraday(d) and d not in ingest.BACKFILL_DEFERRED and d not in ingest.OUT_OF_UNIT]


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


def _date_has_time(conn, dataset, start, end):
    """dataset 之 date 是否含時間（datetime '..:..' → 24/7 事件型如 News，by-date 不跳週末；純 date
    交易型 → 跳週末省 request）。先看 DB 既有樣本；首次無表則自 start 探首個有資料日。
    守 #18：週末取捨依資料事實、不假設——News 週末有新聞，跳週末會漏 → 違資料來源一致性。"""
    with db.transaction(conn) as cur:
        if "date" in schema.get_dataset_columns(cur, dataset):
            cur.execute(f'SELECT date FROM "{dataset}" WHERE date IS NOT NULL LIMIT 1')
            row = cur.fetchone()
            if row and row[0]:
                return ":" in str(row[0])
    probe = date.fromisoformat(start[:10])
    last = date.fromisoformat((end or date.today().isoformat())[:10])
    for _ in range(8):                                    # 自 start 探最多 8 日找首個有資料日 sample
        if probe > last:
            break
        try:
            rows = finmind.fetch(dataset, start_date=probe.isoformat(), end_date=probe.isoformat())
            if rows and rows[0].get("date") is not None:
                return ":" in str(rows[0]["date"])
        except finmind.FinMindError:
            pass
        probe += timedelta(days=1)
    return False


def _bydate_data_start(dataset, full_start, *, end=None):
    """API-driven 起點探測（#18 不空抓）：自 end 往回逐年探（每年取樣 6 個分散日避假日、不探未來日）找最早
    有資料年，再**年內逐月精確到第一個有資料月**（回月初）→ by-date 空跑從「full_start 起 30 年」縮到「該月初幾日」。
    全程無資料 → 回 end（等同不抓，由呼叫端判 not-by-date-capable）。"""
    end_s = end or date.today().isoformat()
    end_y, start_y = int(end_s[:4]), int(full_start[:4])
    earliest = None
    for y in range(end_y, start_y - 1, -1):                    # 自近往遠
        found = False
        for md in ("-11-15", "-08-15", "-05-15", "-02-15", "-12-15", "-06-15"):
            day = f"{y}{md}"
            if day > end_s:                                   # 不探未來日
                continue
            try:
                if finmind.fetch(dataset, start_date=day, end_date=day):
                    found = True
                    break
            except finmind.FinMindError:
                pass
        if found:
            earliest = y
        elif earliest is not None:                            # 已有資料年、再往回一年無資料 → 抵起點邊界 → 停
            break
    if not earliest:
        return end_s
    # 年內精確化（#18 消除年初空跑）：earliest 只定到「年」、年初無資料月仍逐日空跑（如 GovBank 元年 2021
    # 但年中才有資料）→ 年內逐月探（每月 2 取樣日）第一個有資料月、回該月初，空跑從「年初」縮到「月初」。
    for m in range(1, 13):
        for dd in ("-10", "-20"):
            day = f"{earliest}-{m:02d}{dd}"
            if day > end_s:
                return f"{earliest}-{m:02d}-01"
            try:
                if finmind.fetch(dataset, start_date=day, end_date=day):
                    return f"{earliest}-{m:02d}-01"
            except finmind.FinMindError:
                pass
    return f"{earliest}-01-01"


def _data_era_start(dataset, full_start, *, canon=None):
    """per-stock fetch 起點 floor 由 **API 探得之資料元年** 決定（#18：起點由 API 探測、不寫死）。
    無資料股若以寫死 full_start（如 1990）對 API 寬窗空掃 → 極慢（實證:1990-2026 空掃 ~18s／檔;
    自資料元年起空掃僅 ~0.2s）。canon（2330 全史,主路徑已抓）有資料 → 取 min(date);
    否則探幾檔大型老股取最早有資料日;全空（罕見 sparse dataset）→ full_start。"""
    rows = list(canon) if canon else None
    if not rows:
        for sid in ("2317", "2454", "1101", "2002"):      # 大型老股(2330=canon、空才到此 → 不重探)
            try:
                rows = finmind.fetch(dataset, data_id=sid, start_date=full_start)
            except finmind.FinMindError:
                rows = None
            if rows:
                break
    dates = [r["date"] for r in (rows or []) if r.get("date")]
    return min(dates) if dates else full_start


# 無 /datalist 之少數維度 id（官方文檔 + live-probe 證實全集，#18；非臆測白名單）
_DOC_SEED_IDS = {
    "TaiwanStockTotalReturnIndex": ["TAIEX", "TPEx"],   # 報酬指數:加權/櫃買(文檔+probe 證實僅此 2 個)
}


def _fetch_for_store(dataset, sid, start, *, dedicated=None, end=None):
    """並發 fetch 一 id（**僅 API、不碰 conn/DB → thread-safe**）。回 (sid, rows|None)。
    `dedicated`=special endpoint path → 走 fetch_dedicated；否則普通 /data fetch。
    `end`=範圍上界（鉅額分點等 /data `start_date`-only 會 timeout 者須 `end_date` 限窗、probe 實證 2026-06-23）。
    錯誤（該 id 無此資料等）→ rows=None（跳過,不中斷全批）。"""
    ep = {"end_date": end} if end else {}
    try:
        if dedicated:
            return sid, finmind.fetch_dedicated(dedicated, data_id=sid, start_date=start, **ep)
        return sid, finmind.fetch(dataset, data_id=sid, start_date=start, **ep)
    except finmind.FinMindError:
        return sid, None


def _per_stock_sync(conn, dataset, roster, start_floor, progress, *, mode="per-stock", workers=None, dedicated=None, end=None):
    """逐股抓取（roster，每股 resume DB max(date)）→ summary。

    並發（workers>1）：**fetch 並發（僅 API）、DB 寫入仍主執行緒序列**（免 conn race）；start rate 由
    finmind._pace thread-safe 維持 ≥MIN_INTERVAL → IP 對外速率＝單流安全值（#17/#24），只是回應等待重疊。
    """
    workers = workers or PER_STOCK_WORKERS
    # resume 起點:有 DB 列→各自 max(date) 續抓,無→ API 資料元年 floor（#18,非寫死）。
    # 一次 GROUP BY 取全 roster 之 max(date),取代逐股 N+1 查詢（實證:3101 筆 ~250s → 單查 ~秒）。
    db_max = {}
    with db.transaction(conn) as cur:
        if "date" in schema.get_dataset_columns(cur, dataset):
            cur.execute(f'SELECT stock_id, max(date) FROM "{dataset}" GROUP BY stock_id')
            db_max = {str(r[0]): str(r[1]) for r in cur.fetchall() if r[1]}
    starts = {sid: (db_max.get(str(sid)) or start_floor) for sid in roster}
    total = stocks = 0
    failed = []                                   # 抓取失敗(403/cooldown 用盡→rows is None)之 sid=漏抓、供 sync 完精準 heal(#8)

    def _consume(pairs):                          # pairs: iterable of (sid, rows|None)；DB 寫入序列於主執行緒
        nonlocal total, stocks
        for i, (sid, rows) in enumerate(pairs, 1):
            if rows:
                # require_keys=('date',):per-stock 亦強制 date 入 PK(同 by-date 機制)。防首股窄樣本(如某股僅
                # 1 筆股利)→ detect_keys 鎖 PK=stock_id 單欄 → 其餘股多年事件 ON CONFLICT 互蓋塌列(實證
                # 2026-06-28 TaiwanStockDividend:2411 股各僅 1 列、2330 史失)。date 不存則 detect_keys 自略過、無害。
                total += ingest.store(conn, dataset, rows, data_id=sid, require_keys=("date",))["rows"]
                stocks += 1
            elif rows is None:                    # None=抓取失敗(漏抓)→記;[]=真無資料→不記(_fetch_for_store 兩者區分)
                failed.append(sid)
            if progress and i % 50 == 0:
                progress(f"  {dataset}: {i}/{len(roster)} 股、累計 {total} 列（{workers} 並發）")

    if workers > 1:
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            _consume(ex.map(lambda s: _fetch_for_store(dataset, s, starts[s], dedicated=dedicated, end=end), roster))
    else:
        _consume(_fetch_for_store(dataset, s, starts[s], dedicated=dedicated, end=end) for s in roster)
    return {"dataset": dataset, "mode": mode, "rows": total, "stocks_with_data": stocks,
            "failed_ids": failed}


def _info_roster_ids(conn, dataset, progress):
    """#18 階層 (b)：同家族 Info 表作維度 id 權威來源（`XXXPrice`→`XXXInfo`，以 list_datasets 動態驗證
    存在、非臆測白名單；catalog 實證國際股 Price/Info 成對）。Info 表 DB 無則先抓（market 小表）。
    回 stock_id 全集；非 Price 家族 / 無對應 Info → []。"""
    if not dataset.endswith("Price"):
        return []
    info = dataset[:-5] + "Info"
    if info not in finmind.list_datasets():
        return []
    with db.transaction(conn) as cur:
        has_info = "stock_id" in schema.get_dataset_columns(cur, info)
    if not has_info:
        if progress:
            progress(f"  → {dataset}：先抓 {info} 作 id roster…")
        try:
            ingest.ingest_finmind(conn, info)
        except finmind.FinMindError:
            return []
    with db.transaction(conn) as cur:
        if "stock_id" not in schema.get_dataset_columns(cur, info):
            return []
        cur.execute(f'SELECT DISTINCT stock_id FROM "{info}" WHERE stock_id IS NOT NULL ORDER BY stock_id')
        return [r[0] for r in cur.fetchall()]


def _dimension_sync(conn, dataset, full_start, progress):
    """by 維度 id 抓取（#18 階層：FinMind `/datalist` → 文檔種子 → 同家族 Info roster）。
    /datalist／文檔種子（總經小表）：逐 id fetch+store（共用 resume max(date)）。
    Info roster（國際股 Price，數千 ticker）：複用 `_per_stock_sync`（每 id 各自 resume + 並發 + _pace）。
    無任何維度來源 → 回 None（呼叫端改試 per-stock 逐股、不誤跑全 roster）。"""
    dl = finmind.datalist(dataset)
    ids, source = (dl, "/datalist") if dl else (_DOC_SEED_IDS.get(dataset, []), "文檔種子")
    if not ids:
        ids = _info_roster_ids(conn, dataset, progress)
        if ids:
            if progress:
                progress(f"  → {dataset}：by 維度 id（{len(ids)} 個、來源 Info roster）→ 逐 id resume 抓…")
            return _per_stock_sync(conn, dataset, ids, full_start, progress, mode="by-dimension-id")
        return None
    if progress:
        progress(f"  → {dataset}：by 維度 id（{len(ids)} 個、來源 {source}：{ids[:3]}…）")
    start = _max_date(conn, dataset) or full_start
    total = hit = 0
    for did in ids:
        try:
            res = ingest.ingest_finmind(conn, dataset, data_id=did, start_date=start)
        except finmind.FinMindError:
            continue
        total += res["rows"]
        hit += 1 if res["rows"] else 0
    return {"dataset": dataset, "mode": "by-dimension-id", "rows": total, "ids_with_data": hit}


def _catalog_plan(conn, dataset):
    """讀 dataset_catalog 之 (fetch_mode, data_id_source, earliest)——SQL 直讀、**不 import catalog 避循環**
    （catalog 模組 import sync）。無 catalog 表 / 無記錄 / excluded → None（呼叫端 adaptive fallback、不脆）。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('dataset_catalog')")
        if cur.fetchone()[0] is None:                          # 無 catalog 表 → adaptive
            return None
        cur.execute("SELECT fetch_mode, data_id_source, earliest_date::text "
                    "FROM dataset_catalog WHERE dataset=%s AND NOT excluded", (dataset,))
        return cur.fetchone()


def _sync_by_plan(conn, dataset, roster, plan, full_start, progress):
    """catalog 驅動抓取（階段 F）：按 catalog fetch_mode 走正解，**復用** sync_by_date / _dimension_sync /
    _per_stock_sync / market store（不重造）。成功回 summary；失敗 / 未覆蓋 mode → None（呼叫端 adaptive fallback）。
    起點 = DB max(date) resume（#6）或 catalog earliest 或 full_start。"""
    mode, _src, earliest = plan
    start = _max_date(conn, dataset) or earliest or full_start
    try:
        if mode in ("by-date", "single-day"):                  # 逐交易日全市場（single-day 事件型亦逐日）
            r = sync_by_date(conn, dataset, start=start, progress=progress)
            return r if r.get("mode") == "by-date" else None   # not-by-date-capable / pk-null → adaptive
        if mode == "by-dim-id":                                 # 逐維度 id（總經/契約，datalist 驅動）
            return _dimension_sync(conn, dataset, full_start, progress)
        if mode == "per-stock":                                 # 逐股（roster）
            return _per_stock_sync(conn, dataset, roster, earliest or full_start, progress)
        if mode == "market":                                    # 市場單批（snapshot/單序列；GoldPrice 經 ingest 聚合 hook）
            rows = finmind.fetch(dataset, start_date=start)
            res = ingest.store(conn, dataset, rows) if rows else {"rows": 0}
            return {"dataset": dataset, "mode": "catalog-market", "rows": res["rows"]}
    except (finmind.FinMindError, psycopg2.Error) as e:
        if progress:
            progress(f"  → {dataset}：catalog 驅動({mode})失敗 → adaptive fallback：{str(e)[:60]}")
        return None
    return None                                                 # 未覆蓋 mode（per-series 等）→ adaptive


def sync_finmind_dataset(conn, dataset, roster, *, full_start=FULL_START, progress=None):
    """sync 一個 FinMind dataset：市場別探測有資料→市場別；回空/需 data_id→逐股（resume）。回 summary。

    adaptive 判據（實測）：per-stock dataset 不帶 data_id 一律回 0 列、market-wide 則回資料 →
    「市場別探測（不帶 data_id）回空 → 改逐股」最 robust，不靠錯誤訊息。
    """
    if ingest.is_intraday(dataset):
        return {"dataset": dataset, "mode": "skip-intraday", "rows": 0}
    if dataset in ingest.OUT_OF_UNIT:                     # 分點/權證:資料量物理排除（#3/#4、TB/數千萬列）→ 不抓
        return {"dataset": dataset, "mode": "out-of-unit-excluded", "rows": 0}
    if dataset in ingest.BACKFILL_DEFERRED:               # 鉅額:可抓但暫緩自動 backfill（scope 待決）→ 自動路徑跳過、走 dedicated 專抓
        return {"dataset": dataset, "mode": "deferred-backfill", "rows": 0}
    # catalog 驅動（階段 F）：讀 catalog fetch_mode 走正解、取代 adaptive 探測（省探測 overhead + 用正解抓法，
    # 如 4 截斷表 by-date/by-dim-id）；catalog 無/異常/未覆蓋 mode → 回落下方 adaptive（守 #18 fallback、不脆）。
    cat = _catalog_plan(conn, dataset)
    if cat and cat[0]:
        planned = _sync_by_plan(conn, dataset, roster, cat, full_start, progress)
        if planned is not None:
            if progress:
                progress(f"  → {dataset}：catalog 驅動 {cat[0]} → {planned.get('rows', 0)} 列")
            return planned
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
        try:
            res = ingest.store(conn, dataset, probe)   # 寬窗探測即全量，直接存（冪等）
            return {"dataset": dataset, "mode": "market", "rows": res["rows"]}
        except psycopg2.IntegrityError as e:
            # market 寬窗批含 PK-null 髒列（實證 2026-06-13：USStockPrice 1997-09-30 stock_id=null，
            # 無法歸屬標的）→ 整批棄用、改走維度 id 路徑（#18 (b) Info roster；逐 id 抓乾淨且各自 resume，
            # 用戶決策：不丟列硬塞、整表換抓法）。無維度來源才上拋原錯。
            if progress:
                progress(f"  → {dataset}：market 批 PK-null 髒列（{type(e).__name__}）→ 改 by 維度 id")
            dim = _dimension_sync(conn, dataset, full_start, progress)
            if dim is not None:
                return dim
            raise
    # 2) 逐股模式（resume：每股各自從 max(date) 續）
    # canonical-probe（實證 §一.10）：roster 依 stock_id 字串排序，前段多為 ETF/債券/權證（無基本面資料）；
    # 故先用大型股 2330（對所有真 per-stock dataset 皆有資料）判定——回 0/錯 → 此 dataset 非 per-stock
    # （date-based 被誤分類）→ 跳過待正確分類，避免「前段 ETF 全 0」誤殺 BalanceSheet 等真資料 dataset。
    try:
        canon = finmind.fetch(dataset, data_id="2330", start_date=full_start)
    except finmind.FinMindError:
        canon = None
    if not canon:
        # canonical 空 → 近期多日試（不帶 data_id）判 by-date 可行性：回資料=可 by-date；全空/需 data_id
        # = 該走 by 維度 id 或 per-stock（避免對「不帶 data_id 回 0/需 data_id」dataset 誤跑 by-date + backward-probe 空掃）
        by_date_ok = False
        for _bk in (0, 1, 2, 3, 7):
            _d = (date.today() - timedelta(days=_bk)).isoformat()
            try:
                if finmind.fetch(dataset, start_date=_d, end_date=_d):
                    by_date_ok = True
                    break
            except finmind.FinMindError as e:
                if "data_id" in str(e):
                    break   # 「data_id can't be none」→ 需 data_id、不可 by-date
        if by_date_ok:
            if progress:
                progress(f"  → {dataset}：canonical 空、by-date 可行 → by-date（探起始年免空抓）…")
            bd_start = _max_date(conn, dataset) or _bydate_data_start(dataset, full_start)
            bd = sync_by_date(conn, dataset, start=bd_start, progress=progress)
            if bd.get("mode") == "by-date":
                return bd
        # by-date 不行（首筆需 data_id）→ by 維度 id（#18 階層：/datalist → 文檔種子）
        dim = _dimension_sync(conn, dataset, full_start, progress)
        if dim is not None:   # 有維度來源（即使 rows=0 標 by-dimension-id；不誤跑全 roster）
            return dim
        # 無維度來源 → per-stock 逐股 fallback（per-stock 但 canonical 2330 誤判者，如 CapitalReduction 減資股稀疏）
        era = _data_era_start(dataset, full_start)   # canon 空 → helper 探大型股取元年（#18 不寫死起點）
        ps = _per_stock_sync(conn, dataset, roster, era, progress, mode="per-stock-fallback")
        if ps["stocks_with_data"]:
            return ps
        return {"dataset": dataset, "mode": "absent", "rows": 0}   # 已試 market/canonical/by-date/維度id/逐股
    # canonical 2330 ✓ → per-stock；起點 floor = API 探得之資料元年（canon min(date)），不寫死 full_start（#18）
    era = _data_era_start(dataset, full_start, canon=canon)
    if progress:
        progress(f"  → {dataset}：per-stock 模式（canonical 2330 ✓、資料元年 {era}）,逐 {len(roster)} 股（每 50 股回報一次）…")
    return _per_stock_sync(conn, dataset, roster, era, progress)


def sync_by_date(conn, dataset, *, start=None, end=None, progress=None):
    """全市場增量 by-date sync：不帶 data_id 逐交易日抓整個市場（一筆=一天全市場）+ DB resume。

    適用「不帶 data_id 即回整日全市場」之日頻 dataset（價量/法人/融資券…）；需 data_id 之 dataset
    回 mode='not-by-date-capable'。每日維護 request 從 3100（逐股）→ 範圍內交易日數（通常個位數）。
    start 預設 = DB 既有 max(date)（resume，重抓該日補結算）；DB 空且未給 start → 拒絕（首次全史請
    用 sync_finmind_dataset 逐股）。end 預設 = 今日。
    """
    if ingest.is_intraday(dataset):
        return {"dataset": dataset, "mode": "skip-intraday", "rows": 0}
    if dataset in ingest.OUT_OF_UNIT:                     # 分點/權證:資料量物理排除（#3/#4）→ 不抓（增量路徑亦守）
        return {"dataset": dataset, "mode": "out-of-unit-excluded", "rows": 0}
    if dataset in ingest.BACKFILL_DEFERRED:               # 鉅額:可抓但暫緩自動 backfill（與 sync_finmind_dataset 一致）
        return {"dataset": dataset, "mode": "deferred-backfill", "rows": 0}
    if start is None:
        start = _max_date(conn, dataset)
        if start is None:
            raise ValueError(f"{dataset}：DB 無既有資料且未指定 start；by-date 為增量用途，"
                             f"首次全史請用 sync_finmind_dataset（逐股）或明確給 start")
    end = end or date.today().isoformat()
    skip_weekend = not _date_has_time(conn, dataset, start, end)   # 事件型(datetime)週末有資料→不跳；交易型→跳
    cur, last = date.fromisoformat(start[:10]), date.fromisoformat(end[:10])
    total = tdays = reqs = 0
    while cur <= last:
        if skip_weekend and cur.weekday() >= 5:   # 交易型週末無交易→省 request(#17)；事件型(News)不跳→不漏週末
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
            try:
                total += ingest.store(conn, dataset, rows, require_keys=("date",))["rows"]
                tdays += 1
            except psycopg2.IntegrityError:
                # by-date 批含 PK-null 髒列（國際股如 USStockPrice 之彙總/髒行 stock_id=null 撞 NOT NULL PK）→
                # by-date 不適合此 dataset：回非 by-date mode，sync_finmind_dataset fall through 至 _dimension_sync
                # 走 by-dim-id（Info roster 逐 ticker、每行必有 id，根除 null PK；整表換抓法、不丟列硬塞，#3 adaptive）
                return {"dataset": dataset, "mode": "pk-null-needs-dim", "rows": total}
        cur += timedelta(days=1)
        if progress and reqs % 20 == 0:
            progress(f"  {dataset} by-date {day}: {tdays} 交易日 / {total} 列 / {reqs} 筆")
    return {"dataset": dataset, "mode": "by-date", "rows": total, "trading_days": tdays, "requests": reqs}


def sync_fred(conn, series_ids, *, vintage_map=None, progress=None):
    """sync 給定 FRED series 清單（落 fred_series，每 series 全抓）。回 summary。

    vintage_map：`{series_id: 是否走 ALFRED vintage}`——Tier B=True 取全 vintage（保留各版真
    realtime_start，供 point-in-time）、Tier A=False 取最新值（realtime_start=觀測日）；未列入者預設
    False。由呼叫端（features/macro）決定，本引擎不持清單（#3 / 層次：ingestion 不反相依 feature）。"""
    vmap = vintage_map or {}
    total = 0
    for sid in series_ids:
        # FRED 一律抓全史（每 series 單一 call、資料小、idempotent ON CONFLICT）:確保完整含 pre-1990 + 取最新修訂;
        # 不 resume——_max_date 起點會永久漏掉首抓被 1990 截掉的史 → 須每次全抓回填;#18 最早日由 API 決定(start=None)
        # vintage=True 者連全 vintage 一併抓（realtime 全範圍），同屬「全史回填」語意。
        try:
            res = ingest.ingest_fred(conn, sid, start_date=None, vintage=vmap.get(sid, False))
        except fred.FredError:
            continue
        total += res["rows"]
        if progress:
            progress(f"  FRED {sid}: +{res['rows']} 列{'（vintage）' if vmap.get(sid) else ''}")
    return {"table": ingest.FRED_TABLE, "series": len(series_ids), "rows": total}


def sync_all(conn, *, roster=None, datasets=None, fred_series=None, fred_vintage=None,
             full_start=FULL_START, progress=print):
    """PHASE 2→4 一條龍。roster/datasets/fred_series 可傳子集做小範圍；None → 全量（long-running）。
    fred_vintage：`{series_id: vintage}` 透傳 sync_fred（Tier B 須帶，否則 Tier B 會被當非 vintage 落地＝洩漏）。"""
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
        results.append(sync_fred(conn, fred_series, vintage_map=fred_vintage, progress=progress))
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
