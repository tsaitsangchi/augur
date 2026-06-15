"""augur 元資料登錄 catalog（dataset_catalog / column_catalog）— 橫切層。

🎯 這支在做什麼（白話）：對每個 FinMind/FRED dataset 做 API 探測，取得「怎麼抓」的元資料
（欄/型別/中文/最優抓取模式/data_id 來源/最早日期/排除/n_stocks/n_dates…），落地為 2 張 DB
登錄表，作後續所有 API 抓取的**單一驅動依據**（取代邊探邊抓）。表＝SSOT、`datasets_zh.md` 可由表生成。

公開 API：`bootstrap_catalog_tables`（建空表）· `build`（探測填表，放量）· `optimal_mode`（動態最優模式）。
存取：`from augur import catalog; catalog.build(conn)` / `catalog.optimal_mode(meta)`。

守原則 #18（依 API 探測、持久化、非白名單）· #2/#3（API 權威/通用）· #5（型別）· #6（upsert 冪等）·
#15（每欄標 provenance + last_verified；型別/中文＝augur 推導非 FinMind 權威，明標）· #16（clean-room）·
#17（probe 經 finmind 三層限速）。

⚠️ build()/refresh() 會打 API 探測（放量 #17）→ 須用戶授權後跑；bootstrap_catalog_tables（建空表）無害。
用法：PYTHONPATH=src python scripts/build_catalog.py        （建表 + 全探測填表）
"""
from datetime import date, timedelta

from augur.core import db, generic_schema, schema
from augur.ingestion import finmind, ingest, sync

# ── curated 報告知識 seed（provenance=doc；**非 fetch 白名單**，是特殊抓法/edge-case 註解，可刷新）──
# 對映 reports/augur_datasource_finmind_fred_20260615（A2/A3/A5/A8/A9）+ finmind-fetch-methods 記憶。
QUOTA_EXPIRY = "2026-06-24"           # FinMind sponsor token 到期；sponsor-only 抓法到期後抓不到（趕到期前）
_DEDICATED_URL = {                    # 分點/券商聚合走專屬 URL（非 /data），報告 A2——「難抓」之正確 endpoint
    "TaiwanStockTradingDailyReport": "/taiwan_stock_trading_daily_report",
    "TaiwanStockTradingDailyReportSecIdAgg": "/taiwan_stock_trading_daily_report_secid_agg",
}
_SPONSOR_ONLY = frozenset({           # 6/24 到期後抓不到，報告 A3/A5
    "TaiwanStockTradingDailyReport", "TaiwanStockTradingDailyReportSecIdAgg",
    "TaiwanStockWarrantTradingDailyReport", "TaiwanStockGovernmentBankBuySell",
    "TaiwanStockBlockTrade", "TaiwanStockLoanCollateralBalance",
})
_SINGLE_DAY = frozenset({"TaiwanStockNews"})   # size-too-large→end_date 須 none 逐日（非 intraday 者），報告 A9
_DIRTY_VALUE_NOTES = {                # 欄級已知髒值（建表前即知該存字串、防型別爆炸重演），報告 A8
    ("TaiwanFuturesDaily", "contract_date"): "契約月/價差碼 200710 或 200710/200711 → 字串非數字",
    ("TaiwanOptionDaily", "contract_date"): "週選契約碼 201211W4 → 字串",
    ("TaiwanFuturesFinalSettlementPrice", "contract_month"): "週合約碼 202101W1 → 字串",
    ("TaiwanStockSecuritiesLending", "return_date"): "sentinel -1（無/未定）→ 字串非數字",
    ("TaiwanStockConvertibleBondDailyOverview", "date"): "非法日 1911-00-00 → 字串",
    ("USStockPrice", "stock_id"): "彙總髒行 stock_id=null → 整批改 by-dim-id 逐 ticker",
}


# ── 兩張登錄表 DDL（計算型內部表 → 自建 explicit DDL，憲章第五部③）──
def bootstrap_catalog_tables(cur):
    """建 dataset_catalog（表級）+ column_catalog（欄級）；CREATE IF NOT EXISTS（#6 冪等）。"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dataset_catalog (
            dataset            VARCHAR(255) PRIMARY KEY,
            source             VARCHAR(16),          -- finmind / fred
            category           VARCHAR(32),
            tier               VARCHAR(16),          -- F / F(id) / B / S
            endpoint           VARCHAR(64),          -- /data / dedicated / /series/observations
            excluded           BOOLEAN DEFAULT FALSE,
            excluded_reason    VARCHAR(255),
            fetch_mode         VARCHAR(32),          -- 派生:per-stock/by-date/by-dim-id/market/single-day（見 optimal_mode）
            data_id_source     VARCHAR(32),          -- datalist / roster / none / doc
            n_dimension_ids    INTEGER,              -- by-dim-id 之維度 id 數（總經/契約）
            earliest_date      DATE,
            frequency          VARCHAR(16),          -- daily / quarterly / monthly / event / snapshot / single-series / single-day
            n_stocks           INTEGER,              -- per-stock universe（原料）
            n_dates            INTEGER,              -- by-date 期數（原料）
            anti_leakage_note  TEXT,
            source_provenance  VARCHAR(32),          -- DB / probe / doc
            notes              TEXT,
            data_id_required   BOOLEAN,              -- 〔擴〕free 是否需逐股/維度 id
            single_day_only    BOOLEAN,              -- 〔擴〕size-too-large→end_date 須 none 逐日（News 等）
            reconcile_scope    VARCHAR(32),          -- 〔擴〕roster-scoped/by-date/by-dim-id/full-history（防假 MIS/假 PASS）
            dedicated_url      VARCHAR(128),         -- 〔擴〕分點/券商聚合專屬 URL（非 /data）
            quota_expiry       DATE,                 -- 〔擴〕sponsor-only 到期日（2026-06-24 前須抓）
            last_verified      TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS column_catalog (
            dataset            VARCHAR(255),
            column_name        VARCHAR(255),
            ordinal            INTEGER,
            column_name_zh     VARCHAR(255),
            zh_source          VARCHAR(16),          -- FM / finance / derived
            inferred_type      VARCHAR(32),          -- DATE / NUMERIC / VARCHAR / TEXT
            size               VARCHAR(32),
            is_pk              BOOLEAN DEFAULT FALSE,
            anti_leakage_flag  BOOLEAN DEFAULT FALSE,
            dirty_value_note   TEXT,                 -- 〔擴〕已知髒值樣態（建表前知該存字串、防型別爆炸）
            type_caveat        TEXT,                 -- 〔擴〕型別降級註記（date→VARCHAR 等）
            last_verified      TIMESTAMP,
            PRIMARY KEY (dataset, column_name)
        )
    """)


# ── 動態最優模式（存原料、即時重算；不凍結會變的 n_dates，設計 §3.3）──
def optimal_mode(c):
    """依 catalog 原料算「最少呼叫」之抓取模式 + 預估呼叫數 → (mode, est_calls)。"""
    if c.get("excluded"):
        return ("excluded", 0)
    freq = c.get("frequency")
    if freq in ("snapshot", "single-series"):          # 單一序列 / 名冊快照：一次寬查
        return ("market", 1)
    if c.get("data_id_source") == "datalist":          # 總經 / 契約：逐維度 id 各一次全史
        return ("by-dim-id", c.get("n_dimension_ids") or 1)
    if freq == "single-day":                           # News / tick：逐日
        return ("single-day", c.get("n_dates") or 0)
    cands = []
    if c.get("n_stocks"):
        cands.append(("per-stock", c["n_stocks"]))     # 逐股各一次全史
    if c.get("n_dates"):
        cands.append(("by-date", c["n_dates"]))        # 逐日各一次全市場
    return min(cands, key=lambda x: x[1]) if cands else ("market", 1)


# ── 冪等寫入（#6；last_verified 用 SQL now() 免 Python 時鐘）──
_DS_COLS = ("dataset", "source", "category", "tier", "endpoint", "excluded", "excluded_reason",
            "fetch_mode", "data_id_source", "data_id_required", "n_dimension_ids", "earliest_date",
            "frequency", "single_day_only", "reconcile_scope", "dedicated_url", "quota_expiry",
            "n_stocks", "n_dates", "anti_leakage_note", "source_provenance", "notes")
_COL_COLS = ("dataset", "column_name", "ordinal", "column_name_zh", "zh_source",
             "inferred_type", "size", "is_pk", "anti_leakage_flag", "dirty_value_note", "type_caveat")


def _upsert_dataset(cur, m):
    ph = ", ".join(["%s"] * len(_DS_COLS) + ["now()"])
    upd = ", ".join(f"{c}=EXCLUDED.{c}" for c in list(_DS_COLS)[1:] + ["last_verified"])
    cur.execute(f'INSERT INTO dataset_catalog ({", ".join(_DS_COLS)}, last_verified) VALUES ({ph}) '
                f'ON CONFLICT (dataset) DO UPDATE SET {upd}',
                tuple(m.get(c) for c in _DS_COLS))


def _upsert_columns(cur, dataset, cols):
    cur.execute("DELETE FROM column_catalog WHERE dataset=%s", (dataset,))   # 重探即全換（#6）
    ph = ", ".join(["%s"] * len(_COL_COLS) + ["now()"])
    for c in cols:
        cur.execute(f'INSERT INTO column_catalog ({", ".join(_COL_COLS)}, last_verified) VALUES ({ph})',
                    tuple(dataset if k == "dataset" else c.get(k) for k in _COL_COLS))


# ── 探測填表（orchestration + 逐 dataset 探測）──
def build(conn, datasets=None, progress=None):
    """探測 FinMind+FRED 全 dataset → 填 2 表。datasets=None 則全 `sync.daily_datasets()` + FRED。
    ⚠️ 放量 #17（probe 經 finmind 三層限速）；須授權後跑。"""
    with db.transaction(conn) as cur:
        bootstrap_catalog_tables(cur)
        roster_n = _roster_count(cur)
    targets = datasets or (list(sync.daily_datasets()) + ["fred_series"])
    done = 0
    for ds in targets:
        meta, cols = probe_dataset(conn, ds, progress=progress, roster_n=roster_n)
        meta["fetch_mode"], est = optimal_mode(meta)
        with db.transaction(conn) as cur:
            _upsert_dataset(cur, meta)
            _upsert_columns(cur, ds, cols)
        done += 1
        if progress:
            progress(f"[{done}/{len(targets)}] {ds}: {meta['fetch_mode']}(~{est} calls) · "
                     f"{len(cols)} 欄 · 最早 {meta.get('earliest_date')}")
    return {"datasets": done}


# ── 探測 helper（landed 全讀 DB 真值、un-landed 復用 sync 分類探測；皆復用既有引擎、不重造）──
_ASOF_HINTS = ("announcement", "announce", "create_time", "recentlydeclare", "update_time", "publish")


def _anti_leakage_flag(col):
    """欄名是否為 API 自帶公告/as-of 時點欄（#8 金礦:AnnouncementDate/create_time/RecentlyDeclareDate）。"""
    c = col.lower()
    return any(h in c for h in _ASOF_HINTS)


def _base_type(pg_type):
    """'NUMERIC(20,6)'→'NUMERIC'、'VARCHAR(255)'→'VARCHAR'、'DATE'/'TEXT' 原樣。"""
    return pg_type.split("(")[0].strip().upper()


def _fmt_pg(dtype, clen, prec, scale):
    """information_schema 型別 → 'VARCHAR(255)'/'NUMERIC(20,6)'/'DATE'/'TEXT'（與 #5 寫法一致）。"""
    dtype = dtype.upper()
    if dtype in ("CHARACTER VARYING", "VARCHAR"):
        return f"VARCHAR({clen})" if clen else "VARCHAR"
    if dtype == "NUMERIC":
        return f"NUMERIC({prec},{scale})" if prec is not None else "NUMERIC"
    return dtype


def _is_intraday_data(rows):
    """資料事實判定 intraday（#4 by-fact，補硬編 `ingest.INTRADAY` 之不足）：某單一日曆日內有
    密集 sub-day 時間戳（> 48 個 ＝ sub-30-min 規律取樣）→ intraday（如 GoldPrice 5-min 288/日）；
    區別事件型（News 少量不規律/日 → 非 intraday、仍逐日抓）。heuristic、以單次探測日為據（refresh 可校）。"""
    by_day = {}
    for r in rows[:3000]:
        d = str(r.get("date", "")).replace("T", " ")
        day, _, t = d.partition(" ")
        if ":" in t:
            by_day.setdefault(day, set()).add(t)
    return any(len(times) > 48 for times in by_day.values())


def _roster_count(cur):
    """全市場名冊股數（TaiwanStockInfo distinct stock_id）；無名冊 → None。"""
    if "stock_id" not in generic_schema.db_columns(cur, sync.ROSTER_TABLE):
        return None
    cur.execute(f'SELECT count(DISTINCT stock_id) FROM "{sync.ROSTER_TABLE}"')
    return cur.fetchone()[0]


def _db_metadata(conn, ds):
    """已落地表 metadata 全讀 DB（無 API）→ (col_types, pk_set, earliest, n_stocks, n_dates, has_time)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale "
                    "FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", (ds,))
        rows = cur.fetchall()
        pk = set(generic_schema.db_primary_key(cur, ds))
        cset = {r[0] for r in rows}
        earliest = n_stocks = n_dates = None
        has_time = False
        if "date" in cset:   # n_dates 數 distinct 日（非 timestamp 數——News datetime date 否則爆 155 萬）
            cur.execute(f'SELECT min(date), count(DISTINCT left(date::text, 10)) FROM "{ds}"')
            r = cur.fetchone()
            earliest = str(r[0])[:10] if r and r[0] else None
            n_dates = r[1] if r else None
            cur.execute(f'SELECT date FROM "{ds}" WHERE date IS NOT NULL LIMIT 1')
            d = cur.fetchone()
            has_time = ":" in str(d[0]) if d and d[0] else False
        if "stock_id" in cset:
            cur.execute(f'SELECT count(DISTINCT stock_id) FROM "{ds}"')
            n_stocks = cur.fetchone()[0]
        cur.execute(f'SELECT count(*) FROM "{ds}"')
        n_rows = cur.fetchone()[0]
    return ({r[0]: _fmt_pg(r[1], r[2], r[3], r[4]) for r in rows},
            pk, earliest, n_stocks, n_dates, has_time, n_rows)


def _classify_unlanded(conn, ds, roster_n):
    """未落地 dataset 之 **robust 探測取樣接口**——試各種抓法，前提:抓得到就抓得到（不漏網）。
    → (sample, data_id_source, n_dimension_ids, n_stocks, earliest)；全空＝真無資料或需未知 id。

    cascade 對映 #18 探測階層 + sync adaptive（datasource 報告 A6/A9/A11）、復用 sync 之 #18 階層 helper：
      1 `/datalist` 維度（總經/契約 7 類）→ 2 文檔種子（TotalReturnIndex 等無 datalist）→
      3 canonical 2330（per-stock；驗回的真是 2330 資料、防 market dataset 忽略 data_id 誤判）→
      4 by-date 近日（market/單序列/intraday，單日取樣避全史巨量）→
      5 Info roster（國際股 XXXPrice→XXXInfo）→ 6 大型老股 fallback（稀疏 per-stock 如 CapitalReduction）。
    只取樣不落地（Info roster 步驟會落地小 market Info 表＝探測副作用）。⚠️放量 #17。"""
    fs = sync.FULL_START

    def _try(**p):
        try:
            return finmind.fetch(ds, **p)
        except finmind.FinMindError:
            return None

    def _earliest(rows):
        d = [str(r["date"])[:10] for r in rows if r.get("date")]
        return min(d) if d else None

    dl = finmind.datalist(ds)                                          # 1 /datalist 維度
    if dl and (s := _try(data_id=dl[0], start_date=fs)):
        return s, "datalist", len(dl), len(dl), _earliest(s)
    seed = sync._DOC_SEED_IDS.get(ds)                                  # 2 文檔種子維度
    if seed and (s := _try(data_id=seed[0], start_date=fs)):
        return s, "doc", len(seed), len(seed), _earliest(s)
    s = _try(data_id="2330", start_date=fs)                            # 3 canonical 2330（驗真 per-stock）
    if s and any(str(r.get("stock_id")) == "2330" for r in s[:5]):
        return s, "roster", None, roster_n, sync._data_era_start(ds, fs, canon=s)
    for bk in (1, 2, 3, 7, 14, 30):                                    # 4 by-date 近日（market/單序列/by-date多維/intraday）
        day = (date.today() - timedelta(days=bk)).isoformat()
        if s := _try(start_date=day, end_date=day):
            has_stock = "stock_id" in s[0]
            single = not has_stock and len(s) <= 2                     # 1列/日=單一序列(CnnFearGreed)；多列/日=by-date多維(期貨契約)
            return s, ("single" if single else "none"), None, \
                (1 if single else (roster_n if has_stock else None)), sync._bydate_data_start(ds, fs)
    info = sync._info_roster_ids(conn, ds, None)                       # 5 Info roster（國際股）
    if info and (s := _try(data_id=info[0], start_date=fs)):
        return s, "info-roster", len(info), len(info), _earliest(s)
    for sid in ("2317", "2454", "1101", "2002"):                      # 6 大型老股 fallback（稀疏 per-stock）
        if s := _try(data_id=sid, start_date=fs):
            return s, "roster", None, roster_n, _earliest(s)
    return [], "none", None, None, None


def _infer_frequency(has_date, has_time, has_stock, data_id_source, n_dates, earliest, is_single_series=False):
    """頻率推定（供 optimal_mode 之 snapshot/single-series/single-day 分支；其餘 cadence 估標籤）。
    is_single_series＝1 列/日之單一連續序列（CnnFearGreed）→ market 1 call；別於 by-date 多維（期貨多契約/日）。"""
    if not has_date:
        return "snapshot"
    if has_time:
        return "single-day"
    if is_single_series:
        return "single-series"
    if earliest and n_dates:
        try:
            cad = (date.today() - date.fromisoformat(earliest[:10])).days / max(n_dates, 1)
            if cad > 250:
                return "yearly"
            if cad > 45:
                return "quarterly"
            if cad > 20:
                return "monthly"
        except ValueError:
            pass
    return "daily"


def _estimate_n_dates(earliest, freq):
    """未落地 dataset 之 n_dates 估（earliest+頻率；供 optimal_mode 選 per-stock vs by-date）。"""
    try:
        yrs = (date.today() - date.fromisoformat(earliest[:10])).days / 365.25
    except (ValueError, TypeError):
        return None
    return max(1, round(yrs * {"daily": 245, "monthly": 12, "quarterly": 4, "yearly": 1}.get(freq, 245)))


def _endpoint(ds, is_finmind):
    """API endpoint（記「怎麼抓」）：FRED observations / 分點專屬 URL / 預設 /data。"""
    if not is_finmind:
        return "/series/observations"
    return _DEDICATED_URL.get(ds, "/data")


def _reconcile_scope(frequency, data_id_source):
    """對帳範圍（防假 MIS / 假 PASS，報告實戰 §1.H/I/J）：低頻全史、per-stock roster-scoped、維度 by-dim-id。"""
    if frequency in ("quarterly", "monthly", "yearly"):
        return "full-history"          # 低頻近窗空 → 須全史對帳（排未定案最新季）
    if data_id_source == "roster":
        return "roster-scoped"         # per-stock 落地 → 只比 roster 股（排權證、防假 MIS）
    if data_id_source in ("datalist", "doc", "info-roster", "series"):
        return "by-dim-id"
    return "by-date"


def _build_cols(dataset, col_types, pk):
    """欄級 catalog：型別（DB/probe 推得）+ PK + anti-leakage 旗標 + 髒值/型別降級註記（防型別爆炸重演）。
    column_name_zh 留 NULL——**FinMind 不提供欄名中文**（/translation 翻科目值非欄名、且多回空）；
    中文由 curated `datasets_zh.md`（augur 金融用語策展）另行 seed（zh_source=金融），非 API-derivable（誠實 #15）。"""
    cols = []
    for i, (c, t) in enumerate(col_types.items()):
        base = _base_type(t)
        caveat = ("date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日）"
                  if "date" in c.lower() and base == "VARCHAR" else None)
        cols.append({
            "column_name": c, "ordinal": i,
            "column_name_zh": None, "zh_source": None,
            "inferred_type": base, "size": t,
            "is_pk": c in pk, "anti_leakage_flag": _anti_leakage_flag(c),
            "dirty_value_note": _DIRTY_VALUE_NOTES.get((dataset, c)),
            "type_caveat": caveat,
        })
    return cols


def probe_dataset(conn, ds, *, progress=None, roster_n=None):
    """探測單一 dataset → (meta:dict, cols:list[dict])。

    已落地表：欄/型別/最早日/n_stocks/n_dates 全讀 DB 真值（source_provenance=DB、無 API except translation/datalist）；
    未落地：finmind 分類探測（datalist→canonical 2330→by-date）取樣 → infer_schema（provenance=probe）。
    中文＝/translation 官方（無則留白、不捏造金融用語，#15）；anti_leakage_flag 由公告時點欄名偵測（#8）。
    fetch_mode 不在此定（由 `optimal_mode` 動態算）；frequency/n_stocks/n_dates 為其原料。
    ⚠️ 對未落地 dataset 及 translation/datalist 會打 API（放量 #17）；皆經 finmind 三層防護。
    """
    is_finmind = ds != "fred_series"
    meta = {"dataset": ds, "source": "finmind" if is_finmind else "fred", "excluded": False}
    # 靜態 fetch recipe（curated 報告知識；含 excluded 者亦記、保留「怎麼抓」的正解，如分點 dedicated URL）
    meta["endpoint"] = _endpoint(ds, is_finmind)
    meta["dedicated_url"] = _DEDICATED_URL.get(ds)
    meta["single_day_only"] = ds in _SINGLE_DAY
    meta["quota_expiry"] = QUOTA_EXPIRY if ds in _SPONSOR_ONLY else None
    if ds in _SPONSOR_ONLY:
        meta["tier"] = "S"
    if ingest.is_intraday(ds):
        meta.update(excluded=True, excluded_reason="intraday（#4 日為最小單位 gate）",
                    frequency="intraday", source_provenance="ingest.INTRADAY")
        return meta, []
    if ds in ingest.OUT_OF_UNIT:
        meta.update(excluded=True, excluded_reason="規模物理不可行 operational 暫緩（#3）",
                    source_provenance="ingest.OUT_OF_UNIT")
        return meta, []

    with db.transaction(conn) as cur:
        landed = bool(generic_schema.db_columns(cur, ds))

    if landed:
        col_types, pk, earliest, n_stocks, n_dates, has_time, n_rows = _db_metadata(conn, ds)
        meta["source_provenance"] = "DB"
        single_hint = None                                 # landed：由 n_rows≈n_dates 判單一序列（見下）
    elif is_finmind:
        sample, src, n_dim, n_stocks, earliest = _classify_unlanded(conn, ds, roster_n or 0)
        if sample and _is_intraday_data(sample):           # #4 by-fact：補硬編 INTRADAY 之漏（如 GoldPrice 5-min）
            meta.update(excluded=True, excluded_reason="intraday by-data（單日密集 sub-day 時間戳 >48，#4）",
                        frequency="intraday", source_provenance="probe(intraday-by-data)")
            return meta, []
        col_types = generic_schema.infer_schema(sample) if sample else {}
        pk = set(generic_schema.detect_keys(sample, col_types)) if sample else set()
        has_time = bool(sample) and ":" in str(sample[0].get("date", ""))
        n_dates = n_rows = None
        single_hint = (src == "single")                    # _classify by-date 已判（1 列/日=單序列）
        meta["source_provenance"] = "probe" if sample else "probe(empty)"
        meta["data_id_source"] = "none" if src == "single" else src
        if n_dim is not None:
            meta["n_dimension_ids"] = n_dim
    else:                                                  # fred_series 未落地（罕見：FRED 未跑）
        col_types, pk, earliest, n_stocks, n_dates, has_time, n_rows = {}, set(), None, None, None, False, None
        single_hint = False
        meta["source_provenance"] = "probe(empty)"

    if "data_id_source" not in meta:                       # landed / FRED：補 data_id 來源維度
        dl = finmind.datalist(ds) if is_finmind else []
        if dl:
            meta["data_id_source"], meta["n_dimension_ids"] = "datalist", len(dl)
        elif "stock_id" in col_types:
            meta["data_id_source"] = "roster"
        elif "series_id" in col_types:
            meta["data_id_source"] = "series"
        else:
            meta["data_id_source"] = "none"

    has_stock = "stock_id" in col_types
    if single_hint is None:                                # landed 單序列判：無 stock、非維度、~1 列/日
        single_hint = (not has_stock and meta["data_id_source"] not in ("datalist", "doc")
                       and bool(n_dates) and bool(n_rows) and n_rows <= n_dates * 2)
    meta["frequency"] = _infer_frequency("date" in col_types, has_time, has_stock,
                                         meta.get("data_id_source"), n_dates, earliest, bool(single_hint))
    if n_dates is None and earliest:
        n_dates = _estimate_n_dates(earliest, meta["frequency"])
    asof = [c for c in col_types if _anti_leakage_flag(c)]
    src = meta.get("data_id_source")
    meta.update(earliest_date=earliest, n_stocks=n_stocks, n_dates=n_dates,
                anti_leakage_note=("as-of 欄: " + ", ".join(asof)) if asof else None,
                data_id_required=src in ("datalist", "doc", "roster", "info-roster", "series"),
                reconcile_scope=_reconcile_scope(meta["frequency"], src),
                single_day_only=meta["single_day_only"] or meta["frequency"] == "single-day")
    if progress:
        progress(f"  probe {ds}: {len(col_types)}欄·{meta['frequency']}·最早{earliest}·{src}")
    return meta, _build_cols(ds, col_types, pk)
