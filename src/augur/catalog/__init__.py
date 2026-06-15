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
from augur.core import db, generic_schema, schema
from augur.ingestion import finmind, sync


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
            "fetch_mode", "data_id_source", "n_dimension_ids", "earliest_date", "frequency",
            "n_stocks", "n_dates", "anti_leakage_note", "source_provenance", "notes")
_COL_COLS = ("dataset", "column_name", "ordinal", "column_name_zh", "zh_source",
             "inferred_type", "size", "is_pk", "anti_leakage_flag")


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
                    tuple(c.get(k) for k in _COL_COLS))


# ── 探測填表（orchestration + 逐 dataset 探測）──
def build(conn, datasets=None, progress=None):
    """探測 FinMind+FRED 全 dataset → 填 2 表。datasets=None 則全 `sync.daily_datasets()` + FRED。
    ⚠️ 放量 #17（probe 經 finmind 三層限速）；須授權後跑。"""
    with db.transaction(conn) as cur:
        bootstrap_catalog_tables(cur)
    targets = datasets or (list(sync.daily_datasets()) + ["fred_series"])
    done = 0
    for ds in targets:
        meta, cols = probe_dataset(conn, ds, progress=progress)
        meta["fetch_mode"], est = optimal_mode(meta)
        with db.transaction(conn) as cur:
            _upsert_dataset(cur, meta)
            _upsert_columns(cur, ds, cols)
        done += 1
        if progress:
            progress(f"[{done}/{len(targets)}] {ds}: {meta['fetch_mode']}(~{est} calls) · "
                     f"{len(cols)} 欄 · 最早 {meta.get('earliest_date')}")
    return {"datasets": done}


def probe_dataset(conn, ds, *, progress=None):
    """探測單一 dataset → (meta:dict, cols:list[dict])。

    meta：source/category/tier/endpoint/excluded/excluded_reason/data_id_source/n_dimension_ids/
          earliest_date/frequency/n_stocks/n_dates/anti_leakage_note/source_provenance/notes。
    cols：每欄 {column_name, ordinal, column_name_zh, zh_source, inferred_type, size, is_pk, anti_leakage_flag}。

    步驟（實作見段 2）：
      1) 欄+型別：已落地表讀 DB schema 真值；否則最小單位 probe `/data` 1 列 → `generic_schema.infer_schema`。
      2) 中文：`/translation`（FM 官方 dict）對得上→FM；否則金融用語；落地補欄→derived。
      3) 最早日：已落地 DB `MIN(date)`；否則 wide-probe `min(date)`。
      4) mode 原料：n_stocks=DB distinct stock_id 或 roster；n_dates=DB distinct date 或頻率估。
      5) data_id 來源：`/datalist`（總經/契約）→roster→doc（#18 階層）；n_dimension_ids。
      6) tier/排除：`/user_info` + `ingest.OUT_OF_UNIT` + intraday(#4)。
    """
    raise NotImplementedError("probe_dataset 實作見段 2（待用戶過目段 1 結構後續寫）")
