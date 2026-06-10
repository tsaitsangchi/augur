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
            "missing_in_db": 0, "extra_in_db": 0, "examples": []}


def _merge(agg, r):
    for k in ("matched", "value_mismatch", "missing_in_db", "extra_in_db"):
        agg[k] += r[k]
    agg["examples"] = (agg["examples"] + r["examples"])[:_EXAMPLES_CAP]


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
    for i, dt in enumerate(dates, 1):
        d = dt.isoformat()
        with db.transaction(conn) as cur:
            dbr = _db_dicts(cur, table, cols, "date = %s", (dt,))
        api = finmind.fetch(dataset, start_date=d, end_date=d)
        r = compare(dbr, api, pk, val)
        _merge(agg, r)
        if r["value_mismatch"] or r["missing_in_db"] or r["extra_in_db"]:
            agg["per_date"][d] = {k: r[k] for k in ("value_mismatch", "missing_in_db", "extra_in_db")}
        if progress and i % 15 == 0:
            progress(f"  {table} {i}/{len(dates)} 日 | M{agg['matched']:,} "
                     f"VM{agg['value_mismatch']} MIS{agg['missing_in_db']:,} EX{agg['extra_in_db']}")
    agg["days"] = len(dates)
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


def reconcile_market(conn, table, dataset=None, *, fetch_params=None, progress=None):
    """單批對帳：DB 全表 vs API 一次抓（roster / 市場別 dataset）。"""
    dataset = dataset or table
    with db.transaction(conn) as cur:
        cols, pk, val = _meta(cur, table)
        dbr = _db_dicts(cur, table, cols)
    api = finmind.fetch(dataset, **(fetch_params or {}))
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
    """彙整多表 → #7 attestation 判定（value_mismatch=0 ∧ extra_in_db=0）。"""
    tvm = sum(r["value_mismatch"] for r in results)
    tex = sum(r["extra_in_db"] for r in results)
    return {"matched": sum(r["matched"] for r in results),
            "value_mismatch": tvm, "extra_in_db": tex,
            "missing_in_db": sum(r["missing_in_db"] for r in results),
            "passed": tvm == 0 and tex == 0}
