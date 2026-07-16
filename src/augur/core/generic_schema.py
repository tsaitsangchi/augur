"""augur 通用 auto-schema 引擎 — 看 API 資料長相，自動推導型別、建表、冪等寫入。

🎯 這支在做什麼（白話）：
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

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.core.generic_schema              # 印用途+公開入口（唯讀）
  python -m augur.core.generic_schema --selftest   # 純紅綠自測（零 IO；AUD-02 _supersessions 鎖需共用
                                                   #  reconcile._norm，未裝 psycopg2 時誠實 skip、其餘全綠）
"""
from __future__ import annotations

import datetime
import json
import re

# ── 型別規則（#5 型別紀律）────────────────────────────────
VARCHAR_LEN = 255          # 字串下限 VARCHAR(255)；maxlen > 255 → TEXT
NUMERIC_PRECISION = 20     # 數字下限 NUMERIC(20,6)；超出 → 自動擴大
NUMERIC_SCALE = 6

# ── 主鍵候選（#6 主鍵偵測 + augur schema 目錄實見樣態）────
# 順序即偵測優先序：主體識別碼 → 日期 → 維度（逐步構成複合鍵）。
# id 必須排在 date 前：逐 series/逐股樣本之 id 恆定 → 單 id 非唯一 → 續加 date 成 (id, date)；
# 若 date 先行會誤判單 date 主鍵，跨 id 之 ON CONFLICT 將互相覆蓋。
# realtime_start 緊接 date：FRED ALFRED vintage 同 (series_id, date) 有多版 → 需 realtime_start 區辨成
# (series_id, date, realtime_start)（point-in-time 取版，#8）；其餘資料源無此欄、不受影響。
# is_after_hour/trading_session：日盤/夜盤維度——Dealer 表同 (date, dealer_code, futures/option_id) 有日盤+夜盤 2 筆，
# 不納入則加完仍不唯一 → detect_keys 退回全欄 fallback、把 volume 測量值塞進 PK → 對帳 by-date 時值一改即 key 錯位（EX≡MIS）。
KEY_CANDIDATES = (
    "stock_id", "securities_trader_id", "series_id", "futures_id", "option_id",
    "cb_id", "dealer_code", "currency", "country", "code",
    "date", "realtime_start", "Time", "time",
    "year", "ymonth", "yweek",
    "type", "name", "institutional_investors", "contract_type",
    "put_call", "call_put", "trading_session", "is_after_hour", "transaction_type",
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
    if not (isinstance(v, str) and _DATE_RE.match(v.strip())):
        return False
    try:                                       # 格式對仍須驗日期合法性:1911-00-00 / 2026-13-01 等
        datetime.date.fromisoformat(v.strip())  # 格式合法、值非法者 → 非 DATE → 存字串(#1 不丟列、#2 API 原值)
        return True
    except ValueError:
        return False


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


def detect_keys(rows, schema, require=()):
    """貪婪挑能唯一識別 sample 列之最小候選欄組合；退回非空非 TEXT 欄（#6 主鍵穩定）。
    主鍵不可空 → 只用 sample 全非空之欄。

    require：必納入 PK 之欄（即使 sample 不需它即唯一）。用於 by-date 單期 sample——單日 sample 內
    stock_id 已唯一會漏掉 date，require=('date',) 強制補回，防多日 upsert 互相覆蓋塌成每股 1 列。
    """
    cols = list(schema)
    nonnull = [c for c in cols if all(not _is_null(r.get(c)) for r in rows)]
    chosen = []
    for c in (x for x in KEY_CANDIDATES if x in nonnull):
        chosen.append(c)
        if len({tuple(r.get(x) for x in chosen) for r in rows}) == len(rows):
            for rk in require:                       # 強制納入（如 by-date 之 date，sample 單期會漏）
                if rk in nonnull and rk not in chosen:
                    chosen.append(rk)
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
        elif dt in ("NUMERIC", "DATE") and base != dt:
            # 跨型別降級（#5 值域只擴不縮的延伸）：首批樣本全數字/日期 → 推 NUMERIC/DATE，後續批出現
            # 不相容值 → 降級為字串容納 API 全值域（API 即權威 #2；不丟列 #1）。衝突全集＝「批推導 ≠ DB 型別」：
            # 含字串撞數字欄（spread 契約月 '200710/200711'、週選 '201211W4'）與「長得像數字的 sentinel」
            # 撞日期欄（'-1' 會被推成 NUMERIC、非字串 → 不能只比對 VARCHAR/TEXT，2026-06-13 實測）。
            # NUMERIC 用 trim_scale 去尾零（200710.000000→'200710'，與 API 原字串 byte-equal，守 #7）；
            # DATE ::text 即 ISO 原樣。同族 NUMERIC 加寬走上一分支；base==dt 不動。
            target = "TEXT" if base == "TEXT" else f"VARCHAR({VARCHAR_LEN})"
            using = f'trim_scale("{c}")::text' if dt == "NUMERIC" else f'"{c}"::text'
            cur.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{c}" TYPE {target} USING {using}')
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


def _supersessions(cols, keys, rows, db_rows):
    """純邏輯（零 IO、可個別驗證 #29a）：incoming rows × DB 現值 pre-image → 「值真異」之 supersession 三元組。
    共用 `reconcile._norm`（同語意比對，防 Decimal/date/前導零口徑漂移致假/漏 supersession）——**不另實作**。
    純 insert（DB 無此 PK、無 pre-image）與 no-op（值未變）皆不入帳（P4.E5：只裁決衝突、不記純新增/未變）。
    回 [(pk, old_row, new_row), …]：old_row=敗方 DB pre-image、new_row=勝方 incoming（_coerce 對齊寫入口徑）。"""
    from augur.audit.reconcile import _norm   # 延遲 import：避 reconcile→generic_schema 循環
    valcols = [c for c in cols if c not in keys]
    db_by_key = {tuple(_norm(d.get(k)) for k in keys): d for d in db_rows}
    dedup = {}                                # 批內去重：鏡射 upsert 261–263（同鍵保留最後一筆＝API 最新）
    for r in rows:
        dedup[tuple(_norm(r.get(k)) for k in keys)] = r
    out = []
    for nk, r in dedup.items():
        d = db_by_key.get(nk)
        if d is None:                         # 純 insert、無 pre-image → 不留痕
            continue
        if not any(_norm(d.get(c)) != _norm(r.get(c)) for c in valcols):
            continue                          # no-op upsert（值未變）→ 不入帳
        out.append(({k: d.get(k) for k in keys},
                    {c: d.get(c) for c in cols},
                    {c: _coerce(r.get(c)) for c in cols}))
    return out


def _jdump(o):
    """JSONB 序列化函式：非 JSON 原生型別（Decimal/date/None…）以 `str` 忠實表示——Decimal('12.50')→'12.50'
    保留精度尾零、date→ISO、None→null、float 仍為 JSON 數字。經 psycopg2 `Json(…, dumps=_jdump)` 注入
    （**非 `default=`**：psycopg2 `Json.__init__(adapted, dumps=None)` 無 `default` 參數，誤傳即 TypeError）。"""
    return json.dumps(o, default=str)


# P4.E6 斷言主體（issue 3）：記錄「哪個 code 元件斷言此次覆寫」。activity 由 `reason` 承載、活動輸入由
# table+pk+valid_time 承載、上游依賴由 old_row→new_row 承載——使每列自足回答 P4.E6 溯源三問，不倚賴恆 NULL
# 之 run_id。（含 git sha 之細粒度版本、activity_params/source_ref 之更完整 provenance 屬卷宗 §三 另注之
# Layer-4 治權增修、須 P5 拍板，不在本執行層補正範圍——見交付註記。）
_SUPERSEDE_ACTOR = "augur.core.generic_schema:_snapshot_superseded"


def _assert_append_only(cur):
    """fail-loud（issue 8）：把被取代原值落地前，確認 raw_supersede_log 之 append-only trigger 已就位。
    bootstrap_infra 只建裸表；硬化（append-only/truncate trigger + tombstone 受控函式）由
    scripts/migrate_raw_supersede_ddl.py 人工 gate apply。未 apply 前，拒絕把原始證據快照落入「可被 UPDATE/
    DELETE/TRUNCATE 竄改」之帳表（P4.E5/E3）——同交易 raise → heal 一起 rollback，促人先跑 migration 再 heal
    （不靜默覆寫、不靜默落入無保護帳表）。"""
    cur.execute("SELECT to_regclass('raw_supersede_log')")
    if cur.fetchone()[0] is None:
        raise RuntimeError("raw_supersede_log 不存在（bootstrap_infra 未跑）；拒絕快照被取代原值（P4.E5）")
    cur.execute("SELECT 1 FROM pg_trigger WHERE tgrelid='raw_supersede_log'::regclass "
                "AND tgname='trg_raw_supersede_append_only' AND NOT tgisinternal")
    if cur.fetchone() is None:
        raise RuntimeError(
            "raw_supersede_log 缺 append-only trigger（scripts/migrate_raw_supersede_ddl.py 尚未 apply）；"
            "拒絕將被取代原值快照落入可竄改帳表（P4.E5/E3 fail-loud）——先 apply 硬化 DDL 再 heal。")


def _snapshot_superseded(cur, table, rows, schema, keys, reason, run_id=None):
    """heal 覆寫前快照（AUD-02、P4.E5）：取 DB 現值 pre-image、值真異者寫 raw_supersede_log。
    與 upsert 同 `cur`、同交易；快照排在 upsert **之前**先取 pre-image（先取後覆寫，P4.E5 交易同一性、
    任一例外一起 rollback）。

    `reason`＝產生活動（'heal_by_date'/'daily_heal'/'full_universe_heal'；P4.E6 activity）。
    `run_id`＝決策 B：`attestation_run_id` nullable。heal 直呼 sync、本無對帳 run 可帶時恆 None——**非「暫時
    待回填」，而是此路徑結構上無 run 可對**（誠實記；不改 attestation_result 寫序）。P4.E6 溯源三問由每列自身
    承載：斷言主體＝`actor`、產生活動＝`reason`、活動輸入/上游依賴＝`table`+`pk`+`valid_time`+`old_row`→`new_row`。
    JSONB 以 `Json(…, dumps=_jdump)` 序列化（psycopg2 Json 無 `default=` 參數，見 _jdump）。回入帳列數。"""
    from psycopg2.extras import Json, execute_values
    if not keys or not rows:
        return 0
    cols = list(schema)
    dedup = {}                                # 批內去重後之 PK 集（鏡射 upsert 261–263，比照 IN 子句規模）
    for r in rows:
        dedup[tuple(_coerce(r.get(k)) for k in keys)] = r
    items = list(dedup.values())
    # pre-image 抓取以 `_coerce` 建 WHERE-IN 參數（issue 4）——刻意鏡射 upsert(260) 之 ON CONFLICT 命中口徑
    # （找出 upsert「將」覆寫的那些既有列）；_supersessions 內部再以共用 `_norm` join＋比值。字串/日期鍵下
    # _coerce≡_norm（皆 strip、保前導零識別碼）故抓取與比對口徑一致、既有列不會漏抓致靜默滅失；數字鍵之
    # 原值交 PG cast 與 upsert 同命中。混合型別複合鍵之紅綠鎖見 _selftest。
    if len(keys) == 1:                        # 取 DB pre-image：WHERE (pkcols) IN (…)（複合鍵用 tuple IN）
        where = f'"{keys[0]}" IN (' + ", ".join(["%s"] * len(items)) + ")"
        params = [_coerce(r.get(keys[0])) for r in items]
    else:
        tup = "(" + ", ".join(["%s"] * len(keys)) + ")"
        where = "(" + ", ".join(f'"{c}"' for c in keys) + ") IN (" + ", ".join([tup] * len(items)) + ")"
        params = [_coerce(r.get(k)) for r in items for k in keys]
    collist = ", ".join(f'"{c}"' for c in cols)
    cur.execute(f'SELECT {collist} FROM "{table}" WHERE {where}', params)
    db_rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    sup = _supersessions(cols, keys, rows, db_rows)
    if not sup:
        return 0
    _assert_append_only(cur)                  # issue 8：有被取代列要落地前，確認硬化 trigger 就位（否則 fail-loud、同交易 rollback）
    date_is_date = schema.get("date") == "DATE"
    data = []
    for pk, old_row, new_row in sup:
        # valid_time：僅真 DATE 欄填典型 DATE 值；varchar-date dataset（契約月 '2026/06' 等）存 NULL——但該列
        # valid time **未滅失**，仍完整保存於 old_row（含 date 欄）與 pk（date 入鍵時）；typed 欄僅便查用途（issue 6）。
        dv = old_row.get("date")
        vt = dv if (date_is_date and isinstance(dv, datetime.date)) else None
        # 兩側口徑刻意不對稱、各自忠實其來源（卷宗 §2.2；issue 5：明載之取捨非疏漏）：old_row=DB pre-image
        # （原生 Decimal/date 經 _jdump 保精度字串）、new_row=incoming（_coerce 後值）。
        data.append((table, Json(pk, dumps=_jdump), Json(old_row, dumps=_jdump),
                     Json(new_row, dumps=_jdump), vt, reason, run_id, _SUPERSEDE_ACTOR))
    execute_values(
        cur,
        'INSERT INTO raw_supersede_log ("table", pk, old_row, new_row, valid_time, reason, '
        'attestation_run_id, actor) VALUES %s',
        data, page_size=500)
    return len(sup)


def provision_and_upsert(cur, table, rows, require_keys=(), snapshot_reason=None, snapshot_run_id=None):
    """一站式：infer_schema → ensure_table（重用既有 PK）→〔選配快照〕→ upsert。
    require_keys：必納入 PK 之欄（傳給 detect_keys；如 by-date 之 ('date',)）。
    snapshot_reason：**預設 None＝不快照**（upsert 主路徑與 daily 增量 sync 語義一 byte 不變）；僅 heal 呼叫端
      透傳非 None（'heal_by_date'/'daily_heal'）→ ensure_table 後、upsert 前快照被取代原值（AUD-02、P4.E5）。
    snapshot_run_id：決策 B——attestation_run_id nullable（預設 None；heal 直呼 sync 之路徑本無對帳 run 可帶、
      結構上恆 None，非暫時待回填；P4.E6 溯源改由列內 actor/reason/pk 承載，見 _snapshot_superseded）。
    回傳 (寫入列數, schema, effective_keys)；呼叫端負責 commit + audit。"""
    schema = infer_schema(rows)
    keys = detect_keys(rows, schema, require=require_keys)
    eff = ensure_table(cur, table, schema, keys)
    if snapshot_reason is not None:   # gate：heal 前先取 pre-image 快照（同 cur 同交易、早於 byte 覆寫）
        _snapshot_superseded(cur, table, rows, schema, eff, snapshot_reason, snapshot_run_id)
    return upsert(cur, table, rows, schema, eff), schema, eff


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成資料紅綠測型別推導 + 主鍵偵測之核心不變式。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # 值分類（#5 型別紀律地基）
    chk("_is_num/_is_null/_is_date 基本", _is_num("1.5") and _is_null("") and _is_date("2026-06-30"))
    chk("_is_date 拒非法日('2026-13-01')", not _is_date("2026-13-01"))
    chk("_is_num 排除 bool", _is_num(True) is False)
    # FORCE_STR 識別碼不被當數字（防前導零/大整數塌）：'0050' → 字串非 NUMERIC
    s = infer_schema([{"stock_id": "0050", "date": "2026-06-30", "close": "12.5"}])
    chk("FORCE_STR stock_id→字串(非 NUMERIC)", s["stock_id"].startswith("VARCHAR") or s["stock_id"] == "TEXT")
    chk("乾淨日期→DATE", s["date"] == "DATE")
    chk("純數字→NUMERIC 且守下限(20,6)", s["close"] == f"NUMERIC({NUMERIC_PRECISION},{NUMERIC_SCALE})")
    # 混入非數字值 → 降級為字串容納全值域（#1 不丟列、#2 API 權威）
    s2 = infer_schema([{"m": "200710"}, {"m": "200710/200711"}])
    chk("數字欄混字串→退字串", s2["m"].startswith("VARCHAR") or s2["m"] == "TEXT")
    # detect_keys 貪婪最小鍵 + require 強制補欄
    rows = [{"stock_id": "1101", "date": "2026-06-30", "close": "1"},
            {"stock_id": "1102", "date": "2026-06-30", "close": "2"}]
    sch = infer_schema(rows)
    chk("detect_keys 單日 sample stock_id 即唯一", detect_keys(rows, sch) == ["stock_id"])
    chk("detect_keys require 補回 date", detect_keys(rows, sch, require=("date",)) == ["stock_id", "date"])
    # AUD-02 快照純邏輯紅綠鎖（_supersessions 零 IO；byte-differ 入帳、no-op/純 insert 不入帳，P4.E5）。
    # _supersessions 共用 reconcile._norm（硬約束:不另實作）→ 拖入 reconcile→core.db→psycopg2；未裝該相依時
    # 誠實 skip（issue 9:還原「免 DB 免 API」可驗性，不讓 ModuleNotFoundError 崩掉整組自測）。
    try:
        from augur.audit.reconcile import _norm as _probe_norm   # noqa: F401  探共用 _norm 依賴鏈可用性
        _have_norm = True
    except ImportError:
        _have_norm = False
        print("  ⏭ SKIP AUD-02 _supersessions 紅綠鎖（未裝 psycopg2/dotenv；共用 reconcile._norm 依賴鏈不可用）")
    if _have_norm:
        scols, skeys = ["stock_id", "date", "close"], ["stock_id", "date"]
        sdb = [{"stock_id": "1101", "date": "2026-06-30", "close": 12.5}]
        chk("_supersessions no-op（_norm 等價 '12.5'==12.5）不入帳",
            _supersessions(scols, skeys, [{"stock_id": "1101", "date": "2026-06-30", "close": "12.5"}], sdb) == [])
        _sup = _supersessions(scols, skeys, [{"stock_id": "1101", "date": "2026-06-30", "close": "9.9"}], sdb)
        chk("_supersessions byte-differ 入帳恰 1、old=pre-image/new=incoming",
            len(_sup) == 1 and str(_sup[0][1]["close"]) == "12.5" and str(_sup[0][2]["close"]) == "9.9")
        chk("_supersessions 純 insert（DB 無此 PK）不留痕",
            _supersessions(scols, skeys, [{"stock_id": "9999", "date": "2026-06-30", "close": "1"}], sdb) == [])
        # issue 4:混合型別複合鍵（date 為 date 型 vs str、close 為 float vs str）——共用 _norm 對齊 join，
        # 既有列不漏抓致靜默滅失；值真異入帳恰 1（鎖「pre-image 抓取口徑 vs 比對口徑一致」不變式）。
        mdb = [{"stock_id": "1101", "date": datetime.date(2026, 6, 30), "close": 12.5}]
        minc = [{"stock_id": "1101", "date": "2026-06-30", "close": "9.9"}]
        chk("_supersessions 混合型別複合鍵（date/str、float/str）_norm 對齊、值真異入帳恰 1",
            len(_supersessions(scols, skeys, minc, mdb)) == 1)
    # issue 7:JSONB 序列化契約（_jdump）——psycopg2 Json 經 dumps= 注入、非 default=（Json 無 default 參數）。
    # 免 psycopg2 亦可驗序列化本身:Decimal 保精度尾零、date→ISO、None→null、float 仍數字（產出合法 JSON）。
    import decimal
    _back = json.loads(_jdump({"d": decimal.Decimal("12.50"), "dt": datetime.date(2026, 6, 30), "n": None, "f": 12.5}))
    chk("_jdump Decimal 保精度字串 '12.50'（不塌成 12.5）", _back["d"] == "12.50")
    chk("_jdump date→ISO / None→null / float→數字",
        _back["dt"] == "2026-06-30" and _back["n"] is None and _back["f"] == 12.5)
    chk("provision_and_upsert 預設 snapshot_reason=None（主路徑不快照、語義不變）",
        provision_and_upsert.__defaults__ == ((), None, None))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.core.generic_schema --selftest;免 DB 免 API)")
