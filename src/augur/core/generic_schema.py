"""augur 通用 auto-schema 引擎 — 看 API 資料長相，自動推導型別、建表、冪等寫入。

這支在做什麼（白話）：
餵一批 API 回來的 dict 列（rows）+ 一個 DB cursor，它就：
1. **看值推型別**（`infer_schema`，#5）：`YYYY-MM-DD` → `DATE`；純數字 → `NUMERIC`（最小 (20,6)，
   超出自動加大）；`stock_id`/券商碼/`year`/`cb_id` 等識別碼 → 強制字串（免被當數字掉前導零）；
   其餘字串 → `VARCHAR(255)`，超過 255 → `TEXT`（無中間寬度）。欄名/欄序照 API（#2）。
2. **偵測主鍵**（`detect_keys`，#6）：從 stock_id/series_id/futures_id/cb_id/date/… 候選欄貪婪挑
   最小唯一組合；挑不出退回全部非空欄（寧可主鍵寬，不掉資料）。
3. **建表/補欄/擴大**（`ensure_table`，#5+#6）：`CREATE TABLE IF NOT EXISTS`（包 SAVEPOINT，多
   worker 併發首建安全）；表已存在 → 沿用 DB 既有主鍵（首建後固定，防小樣本推出更窄鍵覆蓋資料）；
   缺欄補上；既有欄遇更寬值自動 `ALTER COLUMN TYPE` 擴大（VARCHAR→TEXT / 加長 / NUMERIC 加大；
   只擴不縮，防截斷/溢位）。
4. **冪等寫入**（`upsert`，#6）：`ON CONFLICT(主鍵) DO UPDATE`；數字保留 API 原始字串交 PG 精確
   cast（不經 Python float）。

任意 API dataset 都能落地、無白名單（#3）。

邊界：
- **不抓 API**（fetch/throttle/quota/斷點由呼叫端持有）；**不算特徵、不選股**。
- **intraday（tick/分K/5秒）由 ingester 守門排除（#4），不在這層**——本引擎只處理傳進來的列。
- **NULL 忠實落地**：API 給 null/空/'None' → 存 `NULL`（無值，非捏造，不違 #1）；strict source-pure
  之「算不出即缺列、不補 fake/zero」是 **feature 層** 規則（#1 ENFORCE），raw 層忠實反映 API。

守 #5（型別紀律）· #3（純通用 auto-schema）· #2（schema 照 API / 查 DB）· #6（冪等 + 主鍵穩定）· #1（不捏造）。
"""
from __future__ import annotations

import re

# ── 型別規則（#5 型別紀律）────────────────────────────────
VARCHAR_LEN = 255          # 字串下限 VARCHAR(255)；maxlen > 255 → TEXT
NUMERIC_PRECISION = 20     # 數字下限 NUMERIC(20,6)；超出 → 自動擴大
NUMERIC_SCALE = 6

# ── 主鍵候選（#6 主鍵偵測 + augur schema 目錄實見樣態）────
# 順序即偵測優先序：主體識別碼 → 日期 → 維度（逐步構成複合鍵）。
# id 必須排在 date 前：逐 series/逐股樣本之 id 恆定 → 單 id 非唯一 → 續加 date 成 (id, date)；
# 若 date 先行會誤判單 date 主鍵，跨 id 之 ON CONFLICT 將互相覆蓋。
KEY_CANDIDATES = (
    "stock_id", "securities_trader_id", "series_id", "futures_id", "option_id",
    "cb_id", "dealer_code", "currency", "country", "code",
    "date", "Time", "time",
    "year", "ymonth", "yweek",
    "type", "name", "institutional_investors", "contract_type",
    "put_call", "call_put", "trading_session", "transaction_type",
    "HoldingSharesLevel", "industry_category", "origin_name", "item",
)
FORCE_STR = frozenset({"stock_id", "securities_trader_id", "year", "cb_id"})  # 數值樣貌之識別碼/期別
FORCE_DATE = frozenset({"date"})                                             # 純日期欄（#4 日為最小單位）

# 統一 NULL 語意（取樣/主鍵判定/寫入三處共用，否則「判為有值進主鍵但寫入轉 None → NOT NULL 違反」）
_NULL = ("", "none", "null", "nan", "nat")
_NUM_RE = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_null(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip().lower() in _NULL)


def _is_num(v) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    return isinstance(v, str) and _NUM_RE.match(v.strip()) is not None


def _is_date(v) -> bool:
    return isinstance(v, str) and _DATE_RE.match(v.strip()) is not None


def _digits(v):
    """(整數位數, 小數位數)，供 NUMERIC 精度推導。"""
    s = v.strip() if isinstance(v, str) else repr(float(v))
    if "e" in s.lower():
        s = format(float(s), "f")
    intp, _, dec = s.lstrip("-").partition(".")
    return len(intp.lstrip("0") or "0"), len(dec.rstrip("0"))


def _string_type(maxlen) -> str:
    return "TEXT" if maxlen > VARCHAR_LEN else f"VARCHAR({VARCHAR_LEN})"


def _numeric_type(vals) -> str:
    max_int = max_dec = 0
    for v in vals:
        i, d = _digits(v)
        max_int, max_dec = max(max_int, i), max(max_dec, d)
    scale = max(NUMERIC_SCALE, min(max_dec, 12))
    precision = max(NUMERIC_PRECISION, max_int + scale + 4)
    return f"NUMERIC({precision},{scale})"


def infer_schema(rows):
    """rows(list[dict]) → {col: pg_type}；型別由觀測值推導（#5），欄名/欄序照 API（#2）。"""
    cols = list(dict.fromkeys(c for r in rows for c in r))   # 保留 API 欄序、去重
    schema = {}
    for c in cols:
        vals = [r[c] for r in rows if c in r and not _is_null(r[c])]
        if c in FORCE_DATE and (not vals or all(_is_date(v) for v in vals)):
            schema[c] = "DATE"   # 乾淨 YYYY-MM-DD 或空樣本才 DATE；timestamp / 月頻 '2026/06' 照值推成字串（防塌鍵 / cast 錯）
        elif c in FORCE_STR or c in ("Time", "time"):
            schema[c] = _string_type(max((len(str(v)) for v in vals), default=0))
        elif vals and all(_is_date(v) for v in vals):
            schema[c] = "DATE"
        elif vals and all(_is_num(v) for v in vals):
            schema[c] = _numeric_type(vals)
        else:
            schema[c] = _string_type(max((len(str(v)) for v in vals), default=0))
    return schema


def detect_keys(rows, schema):
    """貪婪挑能唯一識別 sample 列之最小候選欄組合；退回非空非 TEXT 欄（#6 主鍵穩定）。
    主鍵不可空 → 只用 sample 全非空之欄。"""
    cols = list(schema)
    nonnull = [c for c in cols if all(not _is_null(r.get(c)) for r in rows)]
    chosen = []
    for c in (x for x in KEY_CANDIDATES if x in nonnull):
        chosen.append(c)
        if len({tuple(r.get(x) for x in chosen) for r in rows}) == len(rows):
            return chosen
    return [c for c in nonnull if schema[c] != "TEXT"] or nonnull or cols


# ── DB introspection（#2：schema 以 DB 為準）──────────────
def db_columns(cur, table):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s", (table,))
    return {r[0] for r in cur.fetchall()}


def db_primary_key(cur, table):
    """既有表之 PRIMARY KEY 欄（依 key 順序）；無表/無 PK → []。"""
    cur.execute(
        """
        SELECT a.attname FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = to_regclass(%s) AND i.indisprimary
        ORDER BY array_position(i.indkey, a.attnum)
        """,
        (f'"{table}"',),
    )
    return [r[0] for r in cur.fetchall()]


def _db_types(cur, table):
    cur.execute(
        "SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale "
        "FROM information_schema.columns WHERE table_name=%s",
        (table,),
    )
    return {r[0]: (r[1].upper(), r[2], r[3], r[4]) for r in cur.fetchall()}


_TYPE_RE = re.compile(r"^([A-Z ]+?)(?:\((\d+)(?:,(\d+))?\))?$")


def _parse_type(t):
    m = _TYPE_RE.match(t.strip().upper())
    if not m:
        return (t.strip().upper(), None, None)
    return (m.group(1).strip(),
            int(m.group(2)) if m.group(2) else None,
            int(m.group(3)) if m.group(3) else None)


def ensure_table(cur, table, schema, keys):
    """建表（不存在）或補欄 + auto-widen（已存在）；回傳 effective keys。
    表已存在且有 PK → 沿用既有 PK（#6 主鍵穩定）。"""
    cols = db_columns(cur, table)
    if not cols:
        import psycopg2
        body = ", ".join(f'"{c}" {t}' for c, t in schema.items())
        pk = ", ".join(f'"{c}"' for c in keys)
        # CREATE TABLE 對 pg_type catalog 非併發安全：多 worker 同時首建撞 Duplicate/UniqueViolation。
        # SAVEPOINT 隔離 → 輸家回滾本次 CREATE、改走補欄路徑，不丟該批資料（#6 重跑/併發安全）。
        cur.execute("SAVEPOINT _ct")
        try:
            cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({body}, '
                        f'CONSTRAINT "{table}_pk" PRIMARY KEY ({pk}))')
            cur.execute("RELEASE SAVEPOINT _ct")
            return list(keys)
        except (psycopg2.errors.DuplicateTable,
                psycopg2.errors.DuplicateObject,
                psycopg2.errors.UniqueViolation):
            cur.execute("ROLLBACK TO SAVEPOINT _ct")
            cols = db_columns(cur, table)
            if not cols:
                raise
    # 已存在（或競態 fall-through）：補缺欄 + auto-widen 既有欄（只擴不縮，#5；防早期窄樣本致截斷/溢位）
    have = _db_types(cur, table)
    for c, t in schema.items():
        if c not in cols:
            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN "{c}" {t}')
            continue
        base, p1, s1 = _parse_type(t)
        ex = have.get(c)
        if not ex:
            continue
        dt, clen, ep, es = ex
        is_char = dt in ("CHARACTER VARYING", "VARCHAR")
        if is_char and base == "TEXT":
            cur.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{c}" TYPE TEXT')
        elif is_char and base == "VARCHAR" and p1 and clen and p1 > clen:
            cur.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{c}" TYPE VARCHAR({p1})')
        elif dt == "NUMERIC" and base == "NUMERIC" and p1 and s1 is not None and ep:
            scale = max(s1, es or 0)
            precision = max(p1 - s1, (ep or 0) - (es or 0)) + scale
            if precision > ep or scale > (es or 0):
                cur.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{c}" TYPE NUMERIC({precision},{scale})')
    return db_primary_key(cur, table) or list(keys)


def _coerce(v):
    """null/placeholder → NULL（#1：無值即 NULL，不捏造）；字串原樣交 PG cast；數字原樣。"""
    if _is_null(v):
        return None
    return v.strip() if isinstance(v, str) else v


def upsert(cur, table, rows, schema, keys):
    """ON CONFLICT(keys) DO UPDATE 冪等寫入（#6）；回傳列數。"""
    from psycopg2.extras import execute_values
    cols = list(schema)
    data = [tuple(_coerce(r.get(c)) for c in cols) for r in rows]
    if keys:   # 批次內同主鍵去重（保留最後一筆＝API 最新）：防同批多列撞同鍵之 ON CONFLICT CardinalityViolation
        kidx = [cols.index(k) for k in keys]
        data = list({tuple(t[i] for i in kidx): t for t in data}.values())
    collist = ", ".join(f'"{c}"' for c in cols)
    conflict = ", ".join(f'"{c}"' for c in keys)
    sets = ", ".join(f'"{c}"=EXCLUDED."{c}"' for c in cols if c not in keys)
    action = f"DO UPDATE SET {sets}" if sets else "DO NOTHING"
    execute_values(
        cur,
        f'INSERT INTO "{table}" ({collist}) VALUES %s ON CONFLICT ({conflict}) {action}',
        data, page_size=1000)
    return len(data)


def provision_and_upsert(cur, table, rows):
    """一站式：infer_schema → ensure_table（重用既有 PK）→ upsert。
    回傳 (寫入列數, schema, effective_keys)；呼叫端負責 commit + audit。"""
    schema = infer_schema(rows)
    keys = detect_keys(rows, schema)
    eff = ensure_table(cur, table, schema, keys)
    return upsert(cur, table, rows, schema, eff), schema, eff
