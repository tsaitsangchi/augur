"""augur 對帳稽核 — DB↔API byte-level attestation（#7：證明 DB 無幻像）。

這支在做什麼（白話）：
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
from augur.ingestion.ingest import FRED_TABLE

_NULL = {"", "none", "null", "nan", "nat"}
_EXAMPLES_CAP = 10


def _norm(v):
    """比對正規化：null/placeholder→None；可轉數字→round(float,6)；其餘→str.strip()。"""
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower() in _NULL:
        return None
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
    """DB 表含 stock_id 欄 = per-stock 落地(DB 僅 roster 上市股);by-date 抓全市場(含權證)對帳會假 MIS → 須 roster-scoped。"""
    return "stock_id" in cols


def reconcile_by_date(conn, table, dataset=None, *, since=None, progress=None):
    """逐交易日對帳：DB 各日 vs API by-date 重抓（不帶 data_id）。since 限近期日加速。

    回傳除彙總計數外，含 `per_date`：{日期: {value_mismatch, missing_in_db, extra_in_db}}（**只列有差異
    的日子**）→ 供 `fixable_dates`（VM/MIS，可重跑 sync 補）/ `flagged_dates`（EX 紅旗，不自動碰）取用。
    """
    dataset = dataset or table
    agg = _blank(table)
    agg["per_date"] = {}
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        if since is None:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date')
        else:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" WHERE date >= %s ORDER BY date', (since,))
        dates = [r[0] for r in cur.fetchall()]
    per_stock = _is_per_stock(cols)   # per-stock 表只比對 DB roster 內個股,排除 API 全市場權證(scope 對齊)
    roster_ids = None
    if per_stock:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT stock_id FROM "{table}"')
            roster_ids = {str(r[0]) for r in cur.fetchall()}
    for i, dt in enumerate(dates, 1):
        d = dt if isinstance(dt, str) else dt.isoformat()   # date 欄為 VARCHAR(如契約月 '2026/06')時 dt 是 str、無 isoformat
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, table, cols, "date = %s", (dt,))
        try:
            api = finmind.fetch(dataset, start_date=d, end_date=d)
        except finmind.FinMindError as e:
            agg["errors"].append({"date": d, "error": str(e)})   # 該日抓取失敗 → 記錄跳過,不中斷已對帳的日(#7 韌性)
            continue
        if per_stock:
            api = [row for row in api if str(row.get("stock_id")) in roster_ids]   # 只留 DB roster 內個股(排除全市場權證)
        r = compare(dbr, api, pk, val)
        _merge(agg, r)
        if r["value_mismatch"] or r["missing_in_db"] or r["extra_in_db"]:
            agg["per_date"][d] = {k: r[k] for k in ("value_mismatch", "missing_in_db", "extra_in_db")}
        if progress and i % 15 == 0:
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


def reconcile_per_stock(conn, table, dataset=None, *, since=None, sample_n=None, progress=None):
    """per-stock 對帳：逐股以 per-stock 端點重抓（data_id=股）、逐股 compare——對齊抓取端點。

    per-stock 抓的表（catalog `reconcile_scope='roster-scoped'`）若改用 by-date 重抓對帳，會因
    FinMind by-date/per-stock 兩端點對同列回值之極小差 → 假 VM（2026-06-17 三大法人 VM=73 實證）。
    改以 per-stock 重抓（同寫入端點）比同源：殘餘 VM 即真差異（近日修訂），交 heal 重抓修、不被掩蓋。

    `sample_n`：等距抽樣限重抓股數（per-stock 1 call/股，全 roster 太貴）；None=全 roster。
    **取樣＝部分覆蓋（非全股 attest），呼叫端須知會（#7 不靜默縮覆蓋）**。
    回傳含 `per_stock`：{stock_id:{VM,MIS,EX}}（只列有差異股）+ `stocks`（實對股數）、`sampled`（是否抽樣）。
    """
    dataset = dataset or table
    agg = _blank(table)
    agg["per_stock"] = {}
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        cur.execute(f'SELECT DISTINCT stock_id FROM "{table}" ORDER BY stock_id')
        stocks = [str(r[0]) for r in cur.fetchall()]
        cur.execute(f'SELECT max(date) FROM "{table}"')   # 窗上限=DB 最新日：避免同日 API 較新→假 MIS（對齊 by_date DB-date 驅動 / fred 同窗）
        _mx = cur.fetchone()[0]
    dbmax = _mx.isoformat() if _mx is not None and not isinstance(_mx, str) else _mx
    agg["sampled"] = bool(sample_n and len(stocks) > sample_n)
    if agg["sampled"]:
        step = len(stocks) / sample_n          # 等距抽樣（deterministic、可重現，不用 random）
        stocks = [stocks[int(i * step)] for i in range(sample_n)]
    for i, sid in enumerate(stocks, 1):
        where, params = "stock_id = %s", [sid]
        if since:
            where += " AND date >= %s"
            params.append(since)
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
        api = [row for row in api                                           # 對齊 DB 窗 [since, dbmax]（per-stock 抓回全史/含當日較新）
               if (not since or str(row.get("date")) >= since)
               and (not dbmax or str(row.get("date")) <= dbmax)]
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


def reconcile_fred(conn, series_ids, *, progress=None):
    """逐 series 對帳 fred_series：DB vs FRED API。"""
    agg = _blank(FRED_TABLE)
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, FRED_TABLE)
    for sid in series_ids:
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, FRED_TABLE, cols, "series_id = %s", (sid,))
            cur.execute(f'SELECT min(date) FROM "{FRED_TABLE}" WHERE series_id = %s', (sid,))
            start = cur.fetchone()[0]
        api = fred.fetch(sid, start_date=start.isoformat() if start else None)   # 同 DB 窗，避免 pre-sync 史誤判 missing
        _merge(agg, compare(dbr, api, pk, val))
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
