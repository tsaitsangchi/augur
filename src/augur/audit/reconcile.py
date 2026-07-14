"""augur 對帳稽核 — DB↔API byte-level attestation（#7：證明 DB 無幻像）。

🎯 這支在做什麼（白話）：
把 DB 既有資料逐列拉出、重抓 API 真值、逐欄 byte 比對，分四類——
- **matched**：DB 與 API 同鍵、值逐欄相等。
- **value_mismatch**：同鍵但值不同（DB≠API）。
- **missing_in_db**：API 有、DB 無（覆蓋缺口；重跑 sync 即補）。
- **extra_in_db**：DB 有、API 無（**幻像/PK 碰撞紅旗**；須查根因）。

attestation 通過 = **value_mismatch=0 ∧ extra_in_db=0**（API 即權威 #2，定案資料應與之逐 byte 相等）。

入口：
- `reconcile_by_date(conn, table)`：逐交易日對帳（價量/法人等 by-date dataset）；回 `per_date` 定位差異日。
- `reconcile_market(conn, table)`：單批對帳（roster / 市場別 dataset，API 一次抓）。
- `reconcile_fred(conn, series)`：逐 series 對帳 `fred_series`（DB vs FRED API）。
- `verdict(*results)`：彙整多表 → 通過與否。
- `heal_by_date(conn, table)`：偵測→重跑 sync 補齊（一鍵）；對 fixable 日期跑 `sync_by_date`，再驗。

職責複用：schema/PK 查 DB（不另立白名單 #2）、finmind/fred 抓 API。**對帳函式唯讀**；唯 `heal_by_date`
為「偵測 + 重跑 sync」orchestrator——**寫入仍走 `sync_by_date` 的 upsert 路徑（非 hand-patch，守 #1/#6）**。
比對正規化對齊 `generic_schema`（null/placeholder→None、數字 float 比到 6 位）避免型別假性 mismatch。

守 #7（DB↔API 對帳）· #2（schema/真值以 API 為準）· #1（無幻像之可驗證鐵證）· #15（差異留存供 audit）。
"""
from __future__ import annotations

from augur.core import db, generic_schema, schema
from augur.ingestion import finmind, fred, sync
from augur.ingestion.ingest import FRED_TABLE, _aggregate_daily, aggregate_method

_NULL = {"", "none", "null", "nan", "nat"}
_EXAMPLES_CAP = 10
COVERAGE_SAMPLE = 5            # coverage 對帳抽樣日曆日數(新聞流逐日)
COVERAGE_MISS_TOL = 0.2       # coverage:DB 漏抓占 API 容忍比(新聞去重/時序差、非逐條 byte)


def _norm(v):
    """比對正規化：null/placeholder→None；bool→小寫字串；可轉數字→round(float,6)；其餘→str.strip()。"""
    if v is None:
        return None
    if isinstance(v, bool):                 # bool 須在 float 前判（float(True)=1.0 把布林誤轉數值 →
        return str(v).lower()               # DB varchar 'true' vs API bool True 之 PK key 永不匹配 → 100% false EX≡MIS，Dealer is_after_hour 實證 2026-06-24）
    if isinstance(v, str):
        s = v.strip()
        if s.lower() in _NULL:
            return None
        if len(s) > 1 and s[0] == "0" and s.isdigit():   # 前導零識別碼（ETF '0050'、'009802'）→ 保留 str、不轉 float
            return s                                       # （否則 float('009802')=9802.0 與 '9802' 碰撞 → 假 VM/EX/MIS，DayTrading 實證 2026-06-24）
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return str(v).strip()


def _key(row, pk):
    # 用 _norm（與值比對一致）：數值 PK 欄 DB(NUMERIC Decimal) 與 API(raw str) 正規化為同值，
    # 否則寬 PK（含數值欄）之 DB/API key 永遠對不上 → 100% false EX/MIS（2026-06-11 GovBank 實證）。
    return tuple(_norm(row.get(c)) for c in pk)


def compare(db_rows, api_rows, pk, valcols):
    """純比對 db_rows/api_rows(list[dict]) → 四類計數 + 範例（無 I/O）。"""
    dbk = {_key(r, pk): r for r in db_rows}
    apk = {_key(r, pk): r for r in api_rows}
    matched = mismatch = missing = 0
    examples = []
    for k, a in apk.items():
        d = dbk.get(k)
        if d is None:
            missing += 1
            continue
        diff = [c for c in valcols if _norm(d.get(c)) != _norm(a.get(c))]
        if diff:
            mismatch += 1
            if len(examples) < _EXAMPLES_CAP:
                c = diff[0]
                examples.append({"key": k, "col": c, "db": str(d.get(c)), "api": str(a.get(c))})
        else:
            matched += 1
    extra = sum(1 for k in dbk if k not in apk)
    return {"matched": matched, "value_mismatch": mismatch,
            "missing_in_db": missing, "extra_in_db": extra, "examples": examples}


def _meta(cur, table):
    cols = list(schema.get_dataset_columns(cur, table))
    pk = generic_schema.db_primary_key(cur, table)
    return cols, pk, [c for c in cols if c not in pk]


def _db_dicts(cur, table, cols, where="", params=()):
    sql = f'SELECT {", ".join(chr(34) + c + chr(34) for c in cols)} FROM "{table}"'
    if where:
        sql += f" WHERE {where}"
    cur.execute(sql, params)
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def _blank(table):
    return {"table": table, "matched": 0, "value_mismatch": 0,
            "missing_in_db": 0, "extra_in_db": 0, "examples": [], "errors": []}


def _merge(agg, r):
    for k in ("matched", "value_mismatch", "missing_in_db", "extra_in_db"):
        agg[k] += r[k]
    agg["examples"] = (agg["examples"] + r["examples"])[:_EXAMPLES_CAP]


def _is_per_stock(cols):
    """DB 表含 stock_id 欄 = per-stock 落地;by-date 抓全市場(含名冊外雜項)對帳會假 MIS → 須 roster 過濾。"""
    return "stock_id" in cols


def _roster_union(cur, table):
    """對帳個股範圍 = 真名冊(sync.ROSTER_TABLE、與寫入端同 roster)∪ 表內既有股。
    真名冊:roster 股整股缺漏(該表 0 列)之 API 列不再被濾掉 → missing_in_db 可見(修偵測盲點);
    表內既有股:已下市/名冊外但 DB 有史之股仍保留比對、不產假 EX。"""
    cur.execute(f'SELECT DISTINCT stock_id FROM "{table}"')
    ids = {str(r[0]) for r in cur.fetchall()}
    cur.execute(f'SELECT DISTINCT stock_id FROM "{sync.ROSTER_TABLE}" WHERE stock_id IS NOT NULL')
    return ids | {str(r[0]) for r in cur.fetchall()}


def reconcile_by_date(conn, table, dataset=None, *, since=None, progress=None):
    """逐交易日對帳：DB 各日 vs API by-date 重抓（不帶 data_id）。since 限近期日加速。

    回傳除彙總計數外，含 `per_date`：{日期: {value_mismatch, missing_in_db, extra_in_db}}（**只列有差異
    的日子**）→ 供 `fixable_dates`（VM/MIS，可重跑 sync 補）/ `flagged_dates`（EX 紅旗，不自動碰）取用。
    """
    dataset = dataset or table
    agg = _blank(table)
    agg["per_date"] = {}
    agg_m = aggregate_method(dataset, conn)   # DB-first(#29b);迴圈外查一次
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        if since is None:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date')
        else:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" WHERE date >= %s ORDER BY date', (since,))
        dates = [r[0] for r in cur.fetchall()]
    per_stock = _is_per_stock(cols)   # per-stock 表比對真名冊∪表內既有股,排除名冊外雜項(_roster_union)
    roster_ids = None
    if per_stock:
        with db.transaction(conn) as cur:
            roster_ids = _roster_union(cur, table)
    for i, dt in enumerate(dates, 1):
        d = dt if isinstance(dt, str) else dt.isoformat()   # date 欄為 VARCHAR(如契約月 '2026/06')時 dt 是 str、無 isoformat
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, table, cols, "date = %s", (dt,))
        try:
            api = finmind.fetch(dataset, start_date=d, end_date=d)
        except finmind.FinMindError as e:
            agg["errors"].append({"date": d, "error": str(e)})   # 該日抓取失敗 → 記錄跳過,不中斷已對帳的日(#7 韌性)
            continue
        if agg_m:   # intraday-source（GoldPrice 5分鐘）→ 套 ingest 同聚合對齊 DB 日級落地（#4）;否則 raw intraday vs 日級聚合 → 假 MIS
            api = _aggregate_daily(api, agg_m)
        if per_stock:
            api = [row for row in api if str(row.get("stock_id")) in roster_ids]   # 只留真名冊∪表內既有股(排除名冊外雜項;roster 股整股缺漏入 MIS)
        r = compare(dbr, api, pk, val)
        _merge(agg, r)
        if r["value_mismatch"] or r["missing_in_db"] or r["extra_in_db"]:
            agg["per_date"][d] = {k: r[k] for k in ("value_mismatch", "missing_in_db", "extra_in_db")}
        if progress and (i % 3 == 0 or i == len(dates)):   # 每 3 日印(舊 15 日對 sustained 慢 API 之單 dataset 仍靜默>45min 觸看門狗誤殺,2026-07-14 修)
            progress(f"  {table} {i}/{len(dates)} 日 | M{agg['matched']:,} "
                     f"VM{agg['value_mismatch']} MIS{agg['missing_in_db']:,} EX{agg['extra_in_db']}")
    agg["days"] = len(dates)
    agg["incomplete"] = bool(agg["errors"])   # 有任何日抓取失敗 = 未完整對帳 → verdict 不給 pass
    return agg


def fixable_dates(result):
    """從 reconcile_by_date 結果取「可重跑 sync 補齊」的日期（value_mismatch 或 missing_in_db > 0）。

    處置（依 #7）：對這些日期跑 `sync.sync_by_date(start=d, end=d)` 強制重抓、冪等覆蓋——
    correction＝重跑正常 sync，非 hand-patch。
    """
    return sorted(d for d, c in result.get("per_date", {}).items()
                  if c["value_mismatch"] or c["missing_in_db"])


def flagged_dates(result):
    """取 extra_in_db > 0 的日期（DB 有 API 無 = 紅旗）。**不自動補也不自動刪**，須查根因（#7）。"""
    return sorted(d for d, c in result.get("per_date", {}).items() if c["extra_in_db"])


def heal_by_date(conn, table, dataset=None, *, since=None, progress=None):
    """偵測→重跑 sync 補齊（一鍵）：reconcile_by_date 找差異日 → 對 fixable 日期跑 sync_by_date
    （強制重抓、冪等覆蓋；correction＝重跑正常 sync，非 hand-patch，守 #7/#1/#6）→ 再 reconcile 驗證。

    `flagged`（extra_in_db）日期只回報、**不自動碰**（可能合法已下市歷史）。回 {table, fixed, flagged,
    before, after, passed}。
    """
    before = reconcile_by_date(conn, table, dataset, since=since, progress=progress)
    fixable, flagged = fixable_dates(before), flagged_dates(before)
    for d in fixable:
        sync.sync_by_date(conn, dataset or table, start=d, end=d, progress=progress)
    after = reconcile_by_date(conn, table, dataset, since=since, progress=progress) if fixable else before
    keys = ("value_mismatch", "missing_in_db", "extra_in_db")
    return {"table": table, "fixed": fixable, "flagged": flagged,
            "before": {k: before[k] for k in keys}, "after": {k: after[k] for k in keys},
            "passed": after["value_mismatch"] == 0 and after["extra_in_db"] == 0}


def reconcile_per_stock(conn, table, dataset=None, *, since=None, until=None, sample_n=None, progress=None):
    """per-stock 對帳：逐股以 per-stock 端點重抓（data_id=股）、逐股 compare——對齊抓取端點。

    per-stock 抓的表（catalog `reconcile_scope='roster-scoped'`）若改用 by-date 重抓對帳，會因
    FinMind by-date/per-stock 兩端點對同列回值之極小差 → 假 VM（2026-06-17 三大法人 VM=73 實證）。
    改以 per-stock 重抓（同寫入端點）比同源：殘餘 VM 即真差異（近日修訂），交 heal 重抓修、不被掩蓋。

    迭代個股 = `_roster_union`（真名冊 ∪ 表內既有股）：roster 股整股缺漏（該表 0 列）之 API 列入
    missing_in_db 可見（修偵測盲點）；表內已下市股仍保留比對、不產假 EX。
    `until`：對帳窗上限（未定案排除，#7 類別①日頻次日校正/②季頻最新期）——DB 與 API 皆截至 until，
    未定案期差異不入計數（呼叫端計算並誠實知會 #15）；None=DB max(date)。
    `sample_n`：等距抽樣限重抓股數（per-stock 1 call/股，全 roster 太貴）；None=全 roster。
    **取樣＝部分覆蓋（非全股 attest），呼叫端須知會（#7 不靜默縮覆蓋）**。
    回傳含 `per_stock`：{stock_id:{VM,MIS,EX}}（只列有差異股）+ `stocks`（實對股數）、`sampled`（是否抽樣）。
    """
    dataset = dataset or table
    agg = _blank(table)
    agg["per_stock"] = {}
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        stocks = sorted(_roster_union(cur, table))
        cur.execute(f'SELECT max(date) FROM "{table}"')   # 窗上限=DB 最新日：避免同日 API 較新→假 MIS（對齊 by_date DB-date 驅動 / fred 同窗）
        _mx = cur.fetchone()[0]
    dbmax = _mx.isoformat() if _mx is not None and not isinstance(_mx, str) else _mx
    if until is not None:                     # 呼叫端未定案排除:窗上限再收至 until(str 字典序=ISO 日期序)
        u = until if isinstance(until, str) else until.isoformat()
        dbmax = min(dbmax, u) if dbmax else u
    agg["sampled"] = bool(sample_n and len(stocks) > sample_n)
    if agg["sampled"]:
        step = len(stocks) / sample_n          # 等距抽樣（deterministic、可重現，不用 random）
        stocks = [stocks[int(i * step)] for i in range(sample_n)]
    for i, sid in enumerate(stocks, 1):
        where, params = "stock_id = %s", [sid]
        if since:
            where += " AND date >= %s"
            params.append(since)
        if dbmax:
            where += " AND date <= %s"        # DB 側同窗上限(until 未定案排除;until=None 時=表 max、行為不變)
            params.append(dbmax)
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, table, cols, where, tuple(params))
        fp = {"data_id": sid}
        if since:
            fp["start_date"] = since
        if dbmax:
            fp["end_date"] = dbmax
        try:
            api = finmind.fetch(dataset, **fp)                              # 同抓取端點（per-stock）
        except finmind.FinMindError as e:
            agg["errors"].append({"stock_id": sid, "error": str(e)})        # 該股失敗 → 記錄跳過,不中斷（#7 韌性）
            continue
        api = [row for row in api                                           # 對齊 DB 窗 [since, dbmax]（since/dbmax 可能 date/str → 統一 str 字典序比、免型別錯）
               if (not since or str(row.get("date")) >= str(since))
               and (not dbmax or str(row.get("date")) <= str(dbmax))]
        r = compare(dbr, api, pk, val)
        _merge(agg, r)
        if r["value_mismatch"] or r["missing_in_db"] or r["extra_in_db"]:
            agg["per_stock"][sid] = {k: r[k] for k in ("value_mismatch", "missing_in_db", "extra_in_db")}
        if progress and i % 10 == 0:
            progress(f"  {table} {i}/{len(stocks)} 股 | M{agg['matched']:,} "
                     f"VM{agg['value_mismatch']} MIS{agg['missing_in_db']:,} EX{agg['extra_in_db']}")
    agg["stocks"] = len(stocks)
    agg["incomplete"] = bool(agg["errors"])    # 有股抓取失敗 = 未完整對帳 → verdict 不給 pass
    return agg


def reconcile_by_dim_id(conn, table, dataset=None, *, since=None, progress=None):
    """by-dim-id 對帳：逐 datalist 維度 id 重抓（data_id=維度）累積 → 對 DB 全窗 compare（對齊抓取端點）。

    by-dim-id 抓的表（catalog `reconcile_scope='by-dim-id'`，如 CrudeOilPrices Brent/WTI、ExchangeRate 幣別）
    若用 by-date 重抓（不帶 data_id）回空 → 假 MIS（2026-06-18 實證）。改逐維度 id 重抓比同源。
    維度 id 取自 datalist（同 `_dimension_sync` 抓取來源）；datalist 空 → incomplete（不誤判 EX/MIS）。
    """
    dataset = dataset or table
    agg = _blank(table)
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        dbr = _db_dicts(cur, table, cols, "date >= %s" if since else "", (since,) if since else ())
        cur.execute(f'SELECT max(date) FROM "{table}"')
        _mx = cur.fetchone()[0]
    dbmax = _mx.isoformat() if _mx is not None and not isinstance(_mx, str) else _mx
    dim_ids = finmind.datalist(dataset) or []
    agg["dim_ids"] = len(dim_ids)
    if not dim_ids:
        agg["errors"].append({"error": "datalist 無維度 id → 無法逐維度對帳"})
        agg["incomplete"] = True
        return agg
    api = []
    for i, did in enumerate(dim_ids, 1):
        fp = {"data_id": did}
        if since:
            fp["start_date"] = since
        if dbmax:
            fp["end_date"] = dbmax
        try:
            api.extend(finmind.fetch(dataset, **fp))                 # 同抓取端點（逐維度 id）
        except finmind.FinMindError as e:
            agg["errors"].append({"dim_id": did, "error": str(e)})   # 該維度失敗 → 記錄跳過（#7 韌性）
            continue
        if progress and i % 10 == 0:
            progress(f"  {table} {i}/{len(dim_ids)} 維度 | M{agg['matched']:,}")
    api = [row for row in api                                        # 對齊 DB 窗 [since, dbmax]（since/dbmax 可能 date 或 str → 統一 str 字典序比、免型別錯）
           if (not since or str(row.get("date")) >= str(since))
           and (not dbmax or str(row.get("date")) <= str(dbmax))]
    r = compare(dbr, api, pk, val)
    _merge(agg, r)
    agg["incomplete"] = bool(agg["errors"])    # 有維度抓取失敗 = 未完整對帳 → verdict 不給 pass
    return agg


def reconcile_market(conn, table, dataset=None, *, fetch_params=None, progress=None):
    """單批對帳：DB 全表 vs API 一次抓（roster / 市場別 dataset）。"""
    dataset = dataset or table
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        dbr = _db_dicts(cur, table, cols)
    try:
        api = finmind.fetch(dataset, **(fetch_params or {}))
    except finmind.FinMindError as e:
        r = _blank(table)
        r["errors"] = [{"error": str(e)}]
        r["incomplete"] = True   # 抓取失敗 → 整批未對帳,verdict 不給 pass
        return r
    r = compare(dbr, api, pk, val)
    r["table"] = table
    return r


def reconcile_coverage(conn, table, dataset=None, *, since=None, sample_days=COVERAGE_SAMPLE, progress=None):
    """覆蓋率/列數對帳：新聞/文本時序流（date 帶時間戳、無數值 value 欄）逐條 byte 對帳不適用。

    不逐 distinct 時間戳重抓（如 News distinct date 156 萬→API 爆炸＋必然 incomplete）；改按**日曆日**
    （date 前 10 字）聚合，取近 sample_days 個 DB 日曆日各重抓 API by-date，比 DB 該日列數 vs API 列數
    **量級**——新聞會去重/增刪、不逐條 byte 比，但 DB 應覆蓋 API（漏抓占比 ≤ COVERAGE_MISS_TOL）。
    `coverage_ok` = 抽樣日皆抓到（not incomplete）∧ DB 漏抓占 API ≤ 容忍。`since` 保留簽名一致（未用：
    取近 sample_days 日本即近窗）。回傳標準 agg（value_mismatch 恆 0：不比 value）+ coverage_ok + per_day。
    """
    dataset = dataset or table
    agg = _blank(table)
    agg["per_day"] = {}
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT substring(CAST("date" AS TEXT), 1, 10) d, count(*) '
                    f'FROM "{table}" GROUP BY d ORDER BY d DESC LIMIT %s', (sample_days,))
        db_days = cur.fetchall()
    for d, db_n in db_days:
        try:
            api = finmind.fetch(dataset, start_date=d, end_date=d)
        except finmind.FinMindError as e:
            agg["errors"].append({"date": d, "error": str(e)})
            continue
        api_n = len(api)
        agg["matched"] += min(db_n, api_n)
        agg["missing_in_db"] += max(0, api_n - db_n)   # API 多於 DB → DB 該日漏抓（記錄；容忍去重差）
        agg["per_day"][d] = (db_n, api_n)
    total_api = sum(a for _, a in agg["per_day"].values())
    agg["incomplete"] = bool(agg["errors"]) or not db_days
    agg["coverage_ok"] = (not agg["incomplete"]) and (total_api == 0 or agg["missing_in_db"] <= total_api * COVERAGE_MISS_TOL)
    if progress:
        progress(f"  {table} coverage {len(agg['per_day'])}/{sample_days} 日 · 漏 {agg['missing_in_db']}/{total_api} · "
                 f"{'OK' if agg['coverage_ok'] else 'FAIL'}")
    return agg


def reconcile_fred(conn, series_ids, *, vintage_map=None, progress=None):
    """逐 series 對帳 fred_series：DB vs FRED API。PK＝(series_id, date, realtime_start)。

    vintage_map：`{series_id: vintage}`——決定抓法與容忍策略（由呼叫端／features.macro 傳入）：
    - **Tier B（vintage=True）**：以 `fetch(vintage=True)` 抓全 vintage，按 (series_id, date, realtime_start)
      **逐版精確對帳**（每一 ALFRED vintage 就該逐一對上、值相符）→ **不套日期位移容忍**（多版非位移）。
      ALFRED vintage 為 append-only，DB 應為 API 之子集；EX>0 即真異常、不容忍。
    - **Tier A（vintage=False，預設）**：抓最新值（realtime_start＝觀測日）。**FRED restatement 容忍**
      （2026-06-17 實證 `BAMLH0A0HYM2` 06-16→06-19、同值 4.15、Juneteenth 重對齊）→ DB 有 API 無之筆,
      若其 value 在 API 同 series 有同值（值還在、僅日期移）→ 合法 restatement、**不計 EX**（#7「以 API
      當前值為準、容忍合法 restatement」;**不刪 DB 真值**守 #12/#15）。回傳含 `fred_vintage`（Tier A 容忍筆數）。
    """
    vmap = vintage_map or {}
    agg = _blank(FRED_TABLE)
    agg["fred_vintage"] = 0
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, FRED_TABLE)
    for sid in series_ids:
        is_vintage = vmap.get(sid, False)
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, FRED_TABLE, cols, "series_id = %s", (sid,))
            cur.execute(f'SELECT min(date) FROM "{FRED_TABLE}" WHERE series_id = %s', (sid,))
            start = cur.fetchone()[0]
        api = fred.fetch(sid, start_date=start.isoformat() if start else None, vintage=is_vintage)   # 同 DB 窗 + 同 tier 抓法，避免假 missing/EX
        r = compare(dbr, api, pk, val)
        if r["extra_in_db"] and not is_vintage:   # 僅 Tier A 套 restatement 容忍:DB 有 API 無、value 在 API 同值(僅日期移)→ 不計 EX
            apk = {_key(a, pk) for a in api}
            api_vals = {_norm(a.get("value")) for a in api}
            vintage = sum(1 for d in dbr if _key(d, pk) not in apk and _norm(d.get("value")) in api_vals)
            r["extra_in_db"] -= vintage
            agg["fred_vintage"] += vintage
        _merge(agg, r)
        if progress:
            progress(f"  FRED {sid}: M{agg['matched']:,} VM{agg['value_mismatch']} EX{agg['extra_in_db']}")
    return agg


def verdict(*results):
    """彙整多表 → #7 attestation 判定（value_mismatch=0 ∧ extra_in_db=0 ∧ 無未完整對帳）。"""
    tvm = sum(r["value_mismatch"] for r in results)
    tex = sum(r["extra_in_db"] for r in results)
    incomplete = any(r.get("incomplete") or r.get("errors") for r in results)   # 有抓取失敗未比對 → 無法 attest（#15:沒比到 ≠ 比過且乾淨）
    return {"matched": sum(r["matched"] for r in results),
            "value_mismatch": tvm, "extra_in_db": tex,
            "missing_in_db": sum(r["missing_in_db"] for r in results),
            "incomplete": incomplete,
            "passed": tvm == 0 and tex == 0 and not incomplete}
