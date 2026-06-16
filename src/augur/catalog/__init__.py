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

from augur.core import config, db, generic_schema, schema
from augur.ingestion import finmind, ingest, sync

# ── 官方 FinMind dataset 參考（docs/finmind-references/datasets.md；入憲、抓法元資料權威源）──
# tier / intraday / sponsor 從官方解析驅動,取代硬編白名單(守 #3/#18);官方原檔可刷新(curl 覆蓋),
# 官方未列或解析失敗 → 退回硬編/probe 備援(不脆)。section 級 tier:Real-Time→Sponsor、Convertible Bond→Backer。
_OFFICIAL_REF = config.PROJECT_ROOT / "docs" / "finmind-references" / "datasets.md"
_SUBDAY_KW = ("tick", "kbar", "minute", "5second", "每5秒", "分k", "分鐘")   # sub-day 特徵詞(非硬編表名);「逐筆」太寬(BlockTrade 日級)不用


def _parse_official_datasets(path=_OFFICIAL_REF):
    """解析官方 datasets.md(markdown 表格)→ {dataset: {section, tier, params, desc, is_realtime}}。
    各 section 表頭欄不一 → 依表頭動態對映;section 級 tier 宣告(Real-Time 全 Sponsor、Convertible Bond
    全 Backer)在行無 Tier 欄時套用。解析失敗回 {}(呼叫端退回硬編/probe 備援、不脆)。"""
    out, section, headers = {}, None, None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            section, headers = s[3:].strip(), None
        elif s.startswith("|") and "Dataset" in s:
            headers = [h.strip() for h in s.strip("|").split("|")]
        elif s.startswith("|") and headers and "---" not in s:
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            row = dict(zip(headers, cells))
            ds = row.get("Dataset", "").strip()
            if not ds or ds == "Dataset":
                continue
            rt = bool(section and "Real-Time" in section)
            sec_tier = "Sponsor" if rt else ("Backer" if section and "Convertible Bond" in section else None)
            out[ds] = {"section": section, "tier": row.get("Tier") or sec_tier,
                       "params": row.get("Params", ""), "desc": row.get("Description", ""), "is_realtime": rt,
                       "columns": [c.strip() for c in (row.get("Key Columns") or "").split(",") if c.strip()]}
    return out


_OFFICIAL = _parse_official_datasets()
_OFFICIAL_LOWER = {k.lower(): v for k, v in _OFFICIAL.items()}   # 大小寫不敏感索引(容官方文檔 typo)


def _off(ds):
    """取官方記錄(大小寫不敏感、容官方 typo 如 TaiwanOptionTIck);無 → {}。"""
    return _OFFICIAL.get(ds) or _OFFICIAL_LOWER.get(ds.lower(), {})


def _official_tier(ds):
    """官方 tier 文字 → catalog 碼(F/F(id)/B/S);無記錄 → None(呼叫端備援)。"""
    t = (_off(ds).get("tier") or "").lower()
    if "sponsor" in t:
        return "S"
    if "backer" in t:
        return "B"
    if "data_id" in t:
        return "F(id)"
    if "free" in t:
        return "F"
    return None


def _official_is_intraday(ds):
    """官方判 intraday(單位小於日、不抓):sub-day 歷史(tick/分K/每5秒/分鐘),排除 Real-Time snapshot(可抓)。
    依官方 section/desc/名稱關鍵詞、非硬編表名(#18)。無官方記錄 → False(呼叫端退回硬編 INTRADAY 備援)。"""
    m = _off(ds)
    if not m or m.get("is_realtime"):
        return False
    blob = (ds + " " + m["desc"] + " " + m["params"]).lower()
    return any(k in blob for k in _SUBDAY_KW)


def _official_single_day(ds):
    """官方 params 標 'single day' → True(逐日 end_date none 型)。"""
    return "single day" in (_off(ds).get("params") or "").lower()


def _official_columns(ds):
    """官方 datasets.md 'Key Columns' → 欄名 list(大小寫容錯)；無 → []。excluded 表據此記欄位(免 fetch)。"""
    return _off(ds).get("columns") or []


def _category(ds):
    """category＝官方 datasets.md section（功能分類:Technical/Chip/Fundamental/Derivative/International…）；
    'Taiwan Market - X'→'TW-X' 縮短入 VARCHAR(32)；無 section → None（呼叫端對 FRED 給 'Macro'）。"""
    sec = (_off(ds).get("section") or "").replace("Taiwan Market - ", "TW-")
    return sec[:32] or None


# ── curated 報告知識 seed（provenance=doc；**非 fetch 白名單**，是特殊抓法/edge-case 註解，可刷新）──
# 對映 reports/augur_datasource_finmind_fred_20260615（A2/A3/A5/A8/A9）+ finmind-fetch-methods 記憶。
QUOTA_EXPIRY = "2026-06-24"           # FinMind sponsor token 到期；sponsor-only 抓法到期後抓不到（趕到期前）
_DEDICATED_URL = {                    # 分點/券商聚合走專屬 URL（非 /data），報告 A2——「難抓」之正確 endpoint
    "TaiwanStockTradingDailyReport": "/taiwan_stock_trading_daily_report",
    "TaiwanStockTradingDailyReportSecIdAgg": "/taiwan_stock_trading_daily_report_secid_agg",
    "TaiwanStockWarrantTradingDailyReport": "/taiwan_stock_warrant_trading_daily_report",   # 權證分點（2026-06-16 實證 200-success）
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
    if c.get("source") == "fred":                      # FRED:逐 series_id 各 1 call(走 sync_fred、非 by-date 逐日)
        return ("per-series", c.get("n_dimension_ids") or 0)
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
    targets = datasets or (finmind.list_datasets() + ["fred_series"])   # 全集(含 excluded、亦記其抓法);daily_datasets 會濾掉 intraday/BACKFILL_DEFERRED
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


# _is_intraday_data（單日 sub-day 時間戳 heuristic）已移除：intraday 改由官方 datasets.md 判定
# （_official_is_intraday，#18/#20——憑數據 heuristic 會誤判 News 事件流/snapshot 多合約為 intraday）。


def _roster_count(cur):
    """全市場名冊股數（TaiwanStockInfo distinct stock_id）；無名冊 → None。"""
    if "stock_id" not in generic_schema.db_columns(cur, sync.ROSTER_TABLE):
        return None
    cur.execute(f'SELECT count(DISTINCT stock_id) FROM "{sync.ROSTER_TABLE}"')
    return cur.fetchone()[0]


def _pg_ndistinct(cur, table, col, n_rows):
    """pg_stats 估 distinct 數（instant、避千萬列 count-distinct 慢查；負值=比例×n_rows）；
    無統計（未 ANALYZE）→ 回 None（**絕不做慢 count-distinct**，呼叫端改用 span 估，保 build 快）。
    catalog 本是可刷新估值（#15）；refresh 前可對大表 ANALYZE 提升估準度。"""
    cur.execute("SELECT n_distinct FROM pg_stats WHERE tablename=%s AND attname=%s", (table, col))
    r = cur.fetchone()
    if r and r[0] is not None:
        nd = r[0]
        return int(nd) if nd >= 0 else max(1, int(-nd * (n_rows or 0)))
    return None


def _days_between(earliest, latest):
    """min/max 日之間交易日估（~0.69×日曆日）；供 datetime date（News）或無統計時 n_dates 估。"""
    try:
        return max(1, round((date.fromisoformat(latest) - date.fromisoformat(earliest)).days * 0.69))
    except (ValueError, TypeError):
        return None


def _safe_date(s):
    """正規化 earliest 為合法 YYYY-MM-DD（DATE 欄可存）；月頻 `2026/06`→月初、含時間→取日、非法→None。"""
    if not s:
        return None
    p = str(s)[:10].replace("/", "-").split("-")
    try:
        if len(p) >= 3:
            return date(int(p[0]), int(p[1]), int(p[2])).isoformat()
        if len(p) == 2:
            return date(int(p[0]), int(p[1]), 1).isoformat()
    except (ValueError, TypeError):
        pass
    return None


def _db_metadata(conn, ds):
    """已落地表 metadata 全讀 DB（無 API、用 pg 統計估避千萬列慢查）→
    (col_types, pk_set, earliest, n_stocks, n_dates, has_time, n_rows)。n_dates/n_stocks/n_rows 為估值。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale "
                    "FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", (ds,))
        rows = cur.fetchall()
        pk = set(generic_schema.db_primary_key(cur, ds))
        cset = {r[0] for r in rows}
        cur.execute("SELECT reltuples::bigint FROM pg_class WHERE relname=%s", (ds,))   # n_rows 估(instant)
        rr = cur.fetchone()
        n_rows = rr[0] if rr and rr[0] and rr[0] > 0 else None
        earliest = n_stocks = n_dates = None
        has_time = False
        if "date" in cset:
            cur.execute(f'SELECT min(date), max(date) FROM "{ds}"')                      # fast(min/max)
            r = cur.fetchone()
            earliest = str(r[0])[:10] if r and r[0] else None
            latest = str(r[1])[:10] if r and r[1] else None
            has_time = ":" in str(r[0]) if r and r[0] else False
            n_dates = (_days_between(earliest, latest) if has_time                       # datetime→日跨度估(避數 timestamp)
                       else _pg_ndistinct(cur, ds, "date", n_rows) or _days_between(earliest, latest))
        if "stock_id" in cset:
            n_stocks = _pg_ndistinct(cur, ds, "stock_id", n_rows)
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
    for params in ({"start_date": fs}, {}):                           # 4b 寬窗/無參（月頻 market/名冊 Info special:{}、by-date 單日探不到）→ 1 call market
        if s := _try(**params):
            return s, "single", None, None, _earliest(s)
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


def _recent_day(conn):
    """近期交易日(供 excluded 單日樣本探)：DB TaiwanStockPrice max(date)；無表 → 回退近週工作日。"""
    with db.transaction(conn) as cur:
        if "date" in generic_schema.db_columns(cur, "TaiwanStockPrice"):
            cur.execute('SELECT max(date) FROM "TaiwanStockPrice"')
            r = cur.fetchone()
            if r and r[0]:
                return str(r[0])[:10]
    d = date.today() - timedelta(days=4)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.isoformat()


def _official_earliest(ds):
    """官方 datasets.md 描述若標日期範圍(如 '2005-04-04~now')→ earliest 日；無 → None（免探）。"""
    desc = _off(ds).get("desc", "")
    if "~" in desc:
        head = desc.split("~")[0].strip()[-10:]
        if len(head) == 10 and head[4] == "-" and head[:4].isdigit():
            return head
    return None


def _dedicated_probe_id(conn, ds):
    """dedicated 表 probe 用 data_id：權證→任一權證代號(DB roster)、其餘(分點等)→2330(常存個股、跨史)。"""
    if "warrant" in (_DEDICATED_URL.get(ds) or ""):
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM \"TaiwanStockInfo\" WHERE stock_name LIKE '%購%' OR stock_name LIKE '%售%' LIMIT 1")
            r = cur.fetchone()
            return r[0] if r else None
    return "2330"


def _excluded_sample(conn, ds, roster_n):
    """excluded 表單日樣本探 → (sample, data_id_source, dim_id, n_dimension_ids, n_stocks)；探不到 → 全 None。
    對映診斷實證抓法:dedicated endpoint(分點/權證) → per-stock 2330 → market → /datalist → Info-roster（皆單日避巨量）。
    註:不復用 `_classify_unlanded`（其 canonical start=1990 無 end，對 intraday 單日限定表出錯/回巨量）。"""
    day = _recent_day(conn)

    def _try(**p):
        try:                                                  # timeout 加長:intraday 單日 payload 可達 10-20 萬列
            return finmind.fetch(ds, start_date=day, end_date=day, timeout=180, **p)
        except finmind.FinMindError:
            return None
    durl = _DEDICATED_URL.get(ds)                              # 分點/權證走專屬 endpoint(非 /data)→ 真實 probe(退役「可抓但暫緩」)
    if durl and (did := _dedicated_probe_id(conn, ds)):
        try:
            if s := finmind.fetch_dedicated(durl, data_id=did, date=day, timeout=180):
                return s, "dedicated", did, None, None
        except finmind.FinMindError:
            pass
    s = _try(data_id="2330")                                   # per-stock(tick/kbar) 或 market 忽略 data_id(gold)
    if s and ("stock_id" not in s[0] or any(str(r.get("stock_id")) == "2330" for r in s[:5])):
        has_stk = "stock_id" in s[0]
        return s, ("roster" if has_stk else "none"), None, None, (roster_n if has_stk else None)
    if s := _try():                                            # market(index/orderbook-stat)
        return s, "none", None, None, None
    dl = finmind.datalist(ds)                                  # 維度 id(futures/option tick)
    if dl and (s := _try(data_id=dl[0])):
        return s, "datalist", dl[0], len(dl), None
    base = ds.split("Price")[0] + "Price" if "Price" in ds else ds   # 變體 USStockPriceMinute→USStockPrice → USStockInfo roster
    info = sync._info_roster_ids(conn, base, None)             # Info-roster(國際股 price/minute)
    if info and (s := _try(data_id=info[0])):
        return s, "info-roster", info[0], len(info), len(info)
    return None, None, None, None, None


def _excluded_earliest(conn, ds, src, dim_id):
    """excluded 表 earliest：官方 datasets.md 標的優先（免探）；否則用該表工作抓法**單日回溯探**——
    逐年（3 取樣日避假日）找最早有資料年 → 年內逐月→月初（精確，用戶 directive 2026-06-16：全表完整 metadata）。
    單日 fetch 避巨量寬窗、timeout 180。回 earliest 日字串 或 None。"""
    if off := _official_earliest(ds):
        return off

    def _params(d):
        if src == "roster":
            return {"data_id": "2330", "start_date": d, "end_date": d}
        if src in ("datalist", "info-roster") and dim_id:
            return {"data_id": dim_id, "start_date": d, "end_date": d}
        return {"start_date": d, "end_date": d}

    durl = _DEDICATED_URL.get(ds)
    did = _dedicated_probe_id(conn, ds) if durl else None

    def _has(d):
        if d > date.today().isoformat():
            return False
        try:
            if durl and did:                                  # 分點:2330 跨史→earliest 真;權證:現存代號會到期→可能探不到真起點(資料特性、非暫緩)
                return bool(finmind.fetch_dedicated(durl, data_id=did, date=d, timeout=180))
            return bool(finmind.fetch(ds, timeout=180, **_params(d)))
        except finmind.FinMindError:
            return False
    yr_days = ("02-14", "04-16", "06-13", "08-15", "10-14", "12-16")   # 6 取樣日跨月跨日:避「全週末→假陰性」(實證 2026-06-16:3 日全週末誤判)
    earliest_y = None
    for y in range(date.today().year, 1799, -1):               # 下界 1800＝純 sanity（防無限迴圈、無金融時序早於此）、非「慣例假設」；真起點由邊界邏輯（有資料年後遇無資料年）探得，不設假設停損（窮舉到真的沒資料，2026-06-16 教訓：1990 floor 截斷 GoldPrice）
        if any(_has(f"{y}-{md}") for md in yr_days):
            earliest_y = y
        elif earliest_y is not None:
            break
    if earliest_y is None:
        return None
    for m in range(1, 13):                                      # earliest 年內逐月 → 月初(雙取樣日避假日)
        if any(_has(f"{earliest_y}-{m:02d}-{dd}") for dd in ("13", "21")):
            return f"{earliest_y}-{m:02d}-01"
    return f"{earliest_y}-01-01"


def _official_name_cols(ds):
    """探不到樣本(需未知 id)→ 官方 datasets.md 欄名(型別 NULL、誠實 #15)。"""
    return [{"column_name": n, "ordinal": i, "column_name_zh": None, "zh_source": None,
             "inferred_type": None, "size": None, "is_pk": False,
             "anti_leakage_flag": _anti_leakage_flag(n), "dirty_value_note": None,
             "type_caveat": "官方 datasets.md 欄名（樣本探測未取得、未定型別）"}
            for i, n in enumerate(_official_columns(ds))]


def _excluded_meta(conn, ds, is_finmind, roster_n, frequency):
    """excluded 表(不落地)**完整** metadata(用戶 directive 2026-06-16:不抓也要全欄完整、窮舉非逐點)。
    單日法取 sample+抓法維度+n_stocks → 真型別欄位;下游欄位(n_dates/anti_leakage/data_id_required/
    reconcile_scope)同 fetchable 表推導;earliest 取官方 datasets.md 標的(逐年巨量回溯探另待決)。
    回 (dataset 層 fields:dict, cols:list)。"""
    if not is_finmind:
        return {}, []
    sample, src, dim_id, n_dim, n_stocks = _excluded_sample(conn, ds, roster_n)
    col_types = generic_schema.infer_schema(sample) if sample else {}
    pk = set(generic_schema.detect_keys(sample, col_types)) if sample else set()
    earliest = _safe_date(_excluded_earliest(conn, ds, src, dim_id) if src else _official_earliest(ds))
    asof = [c for c in col_types if _anti_leakage_flag(c)]
    fields = {"data_id_source": src, "n_dimension_ids": n_dim, "n_stocks": n_stocks,
              "earliest_date": earliest,
              "n_dates": _estimate_n_dates(earliest, frequency) if earliest else None,
              "anti_leakage_note": ("as-of 欄: " + ", ".join(asof)) if asof else None,
              "data_id_required": src in ("datalist", "doc", "roster", "info-roster"),
              "reconcile_scope": _reconcile_scope(frequency, src)}
    cols = _build_cols(ds, col_types, pk) if sample else _official_name_cols(ds)
    return fields, cols


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
    # tier / 抓法分類:官方 datasets.md 驅動(權威、取代硬編);官方未列 → 硬編/probe 備援(不脆)
    meta["tier"] = _official_tier(ds) or ("S" if ds in _SPONSOR_ONLY else None)
    meta["category"] = _category(ds) if is_finmind else "Macro"   # 官方 section 功能分類（全表補齊，完整性）
    is_sponsor = meta["tier"] == "S"
    meta["endpoint"] = _endpoint(ds, is_finmind)
    meta["dedicated_url"] = _DEDICATED_URL.get(ds)
    meta["single_day_only"] = _official_single_day(ds) or ds in _SINGLE_DAY
    meta["quota_expiry"] = QUOTA_EXPIRY if is_sponsor else None
    if _official_is_intraday(ds) or ingest.is_intraday(ds):   # 官方 sub-day(主)+ 硬編 INTRADAY(備援);單位小於日不抓(#4)
        meta.update(excluded=True, excluded_reason="單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）",
                    frequency="intraday", source_provenance="official/INTRADAY")   # ≤VARCHAR(32)
        fields, cols = _excluded_meta(conn, ds, is_finmind, roster_n, "intraday")   # 不落地，但全欄 metadata 補齊(窮舉非逐點，用戶 directive)
        meta.update(fields)
        return meta, cols
    if ds in ingest.BACKFILL_DEFERRED:                        # 分點/權證/鉅額:抓法+metadata 真實 probe(退役「可抓但暫緩」placeholder)
        meta.update(excluded=True,                            # excluded＝不進「自動全史 bulk sync」(per-(股,日)規模);catalog metadata 為真實 probe
                    excluded_reason="抓法+欄位/earliest 已實證真實 probe（分點/權證 dedicated endpoint、鉅額 /data）；全史 bulk 落地屬 sync operational（per-(股,日)規模）、非 catalog 缺資料",
                    frequency="daily", source_provenance="dedicated-probe")
        fields, cols = _excluded_meta(conn, ds, is_finmind, roster_n, "daily")   # 真實 probe 全欄 metadata(dedicated-aware)
        meta.update(fields)
        return meta, cols

    with db.transaction(conn) as cur:
        landed = bool(generic_schema.db_columns(cur, ds))

    if landed:
        col_types, pk, earliest, n_stocks, n_dates, has_time, n_rows = _db_metadata(conn, ds)
        meta["source_provenance"] = "DB"
        single_hint = None                                 # landed：由 n_rows≈n_dates 判單一序列（見下）
    elif is_finmind:
        sample, src, n_dim, n_stocks, earliest = _classify_unlanded(conn, ds, roster_n or 0)
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
            if not is_finmind:                          # FRED:n_dimension_ids = DB distinct series_id(供 per-series calls)
                with db.transaction(conn) as cur:
                    cur.execute(f'SELECT count(DISTINCT series_id) FROM "{ds}"')
                    meta["n_dimension_ids"] = cur.fetchone()[0]
        else:
            meta["data_id_source"] = "none"

    earliest = _safe_date(earliest)                        # 正規化(月頻 2026/06→月初、非法→None)再供 frequency/estimate/storage
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
    if ds in ingest._AGGREGATE_DAILY:   # intraday-source→聚合日級(augur-specific;官方標 daily 但 FinMind 回 intraday)
        meta["notes"] = ("intraday-source→聚合日級末筆(%s);官方 daily 但 FinMind 回 intraday、augur 聚合存(#4)"
                         % ingest._AGGREGATE_DAILY[ds])
    if progress:
        progress(f"  probe {ds}: {len(col_types)}欄·{meta['frequency']}·最早{earliest}·{src}")
    return meta, _build_cols(ds, col_types, pk)
