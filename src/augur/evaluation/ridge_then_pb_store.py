"""RIDGE-THEN-PB 進場條件帳本 — 條件列＋做多收盤買進／做空收盤賣出。

🎯 這支在做什麼（白話）：探針過齊四閘的多／空標的寫進 `ridge_then_pb_entry`
   （進場＝次一交易日，抱 30 日；未實現不編造）。`ridge_then_pb_long_*`
   記做多 Top10 池＋過齊者於該日還原收盤買進；`ridge_then_pb_short_*`
   記做空 Top10 池＋過齊者於該日還原收盤賣出（條件帳，不是下單、不是可融券）。
   不改 standing、不寫預測分數表。

守 #1 缺即缺 · #6 同 asof 整批覆寫 · 分數≠報酬％ · 條件≠可交易 · 做空≠可空

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.evaluation.ridge_then_pb_store
  python -m augur.evaluation.ridge_then_pb_store --selftest
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any, Iterable, Mapping, Optional

from psycopg2.extras import Json, execute_values

from augur.core import asof_ready, db
from augur.evaluation import label as label_mod
from augur.evaluation import uptrend_pullback as up

TABLE = "ridge_then_pb_entry"
HOLD_TD = 30
COST = 0.00585  # 單邊往返摩擦（與既有路徑 30 日帳同一尺）；做空不加融券費
FAMILY = "RankRidge"

DDL = f"""CREATE TABLE IF NOT EXISTS {TABLE} (
  asof_date date NOT NULL,
  side text NOT NULL,
  stock_id text NOT NULL,
  name text,
  tag text NOT NULL,
  ridge_rank int,
  sort_rank int,
  avg_score double precision,
  dd20_pct double precision,
  bu20_pct double precision,
  gates jsonb,
  window_pass jsonb,
  model_asofs jsonb,
  k int,
  family text NOT NULL DEFAULT '{FAMILY}',
  hold_td int NOT NULL DEFAULT {HOLD_TD},
  entry_date date,
  exit_date date,
  ret_30_log double precision,
  ret_30_pct double precision,
  ret_30_pct_net double precision,
  realized boolean NOT NULL DEFAULT false,
  note text,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (asof_date, side, stock_id)
)"""

TABLE_LONG_ASOF = "ridge_then_pb_long_asof"
TABLE_LONG_ROW = "ridge_then_pb_long_row"
TABLE_LONG_BUY = "ridge_then_pb_long_buy"

DDL_LONG_ASOF = f"""CREATE TABLE IF NOT EXISTS {TABLE_LONG_ASOF} (
  asof_date date PRIMARY KEY,
  n_pool int NOT NULL,
  n_entry int NOT NULL,
  n_wait int NOT NULL,
  k int NOT NULL,
  family text NOT NULL DEFAULT '{FAMILY}',
  model_asofs jsonb,
  note text,
  created_at timestamptz NOT NULL DEFAULT now()
)"""

DDL_LONG_ROW = f"""CREATE TABLE IF NOT EXISTS {TABLE_LONG_ROW} (
  asof_date date NOT NULL,
  sort_rank int NOT NULL,
  stock_id text NOT NULL,
  name text,
  tag text NOT NULL,
  ridge_rank int,
  avg_score double precision,
  dd20_pct double precision,
  window_pass jsonb,
  path_pct jsonb,
  gates jsonb,
  buy_date date,
  buy_price double precision,
  PRIMARY KEY (asof_date, stock_id)
)"""

DDL_LONG_BUY = f"""CREATE TABLE IF NOT EXISTS {TABLE_LONG_BUY} (
  asof_date date NOT NULL,
  stock_id text NOT NULL,
  name text,
  buy_date date NOT NULL,
  buy_price double precision NOT NULL,
  dd20_pct double precision,
  window_pass jsonb,
  path_pct jsonb,
  gates jsonb,
  ridge_rank int,
  sort_rank int,
  avg_score double precision,
  tag text NOT NULL,
  family text NOT NULL DEFAULT '{FAMILY}',
  note text,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (asof_date, stock_id)
)"""

LONG_BUY_NOTE = (
    "做多 Top10 池不剔除；回撤近→遠；過齊才可當進場條件；"
    "買進價＝該交易日還原收盤（不是 t+1）；條件≠可交易；score≠％"
)

TABLE_SHORT_ASOF = "ridge_then_pb_short_asof"
TABLE_SHORT_ROW = "ridge_then_pb_short_row"
TABLE_SHORT_SELL = "ridge_then_pb_short_sell"

DDL_SHORT_ASOF = f"""CREATE TABLE IF NOT EXISTS {TABLE_SHORT_ASOF} (
  asof_date date PRIMARY KEY,
  n_pool int NOT NULL,
  n_entry int NOT NULL,
  n_wait int NOT NULL,
  k int NOT NULL,
  family text NOT NULL DEFAULT '{FAMILY}',
  model_asofs jsonb,
  note text,
  created_at timestamptz NOT NULL DEFAULT now()
)"""

DDL_SHORT_ROW = f"""CREATE TABLE IF NOT EXISTS {TABLE_SHORT_ROW} (
  asof_date date NOT NULL,
  sort_rank int NOT NULL,
  stock_id text NOT NULL,
  name text,
  tag text NOT NULL,
  ridge_rank int,
  avg_score double precision,
  bu20_pct double precision,
  window_pass jsonb,
  path_pct jsonb,
  gates jsonb,
  sell_date date,
  sell_price double precision,
  PRIMARY KEY (asof_date, stock_id)
)"""

DDL_SHORT_SELL = f"""CREATE TABLE IF NOT EXISTS {TABLE_SHORT_SELL} (
  asof_date date NOT NULL,
  stock_id text NOT NULL,
  name text,
  sell_date date NOT NULL,
  sell_price double precision NOT NULL,
  bu20_pct double precision,
  window_pass jsonb,
  path_pct jsonb,
  gates jsonb,
  ridge_rank int,
  sort_rank int,
  avg_score double precision,
  tag text NOT NULL,
  family text NOT NULL DEFAULT '{FAMILY}',
  note text,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (asof_date, stock_id)
)"""

SHORT_SELL_NOTE = (
    "做空 Top10 池不剔除；反彈近→遠；過齊才可當進場條件；"
    "賣出價＝該交易日還原收盤（不是 t+1）；條件≠可交易≠可融券；score≠％"
)


def hold_window(calendar: Iterable, asof, hold: int = HOLD_TD):
    """t+1 進場、再抱 hold 個交易日。日曆不足 → (None, None, False)。"""
    dd = asof_ready.as_date(asof)
    after = [d for d in calendar if d > dd]
    if len(after) < int(hold) + 1:
        entry = after[0] if after else None
        return entry, None, False
    return after[0], after[int(hold)], True


def _simple_pct(log_ret: Optional[float]) -> Optional[float]:
    if log_ret is None:
        return None
    return (math.exp(float(log_ret)) - 1.0) * 100.0


def _net_pct(simple_pct: Optional[float], *, side: str) -> Optional[float]:
    if simple_pct is None:
        return None
    # 做多：毛％ − 摩擦；做空：−毛％ − 摩擦（不加借券，不是可空）
    if str(side) == "short":
        return (-float(simple_pct)) - (COST * 100.0)
    return float(simple_pct) - (COST * 100.0)


def ensure(cur) -> None:
    cur.execute(DDL)


def ensure_long(cur) -> None:
    cur.execute(DDL_LONG_ASOF)
    cur.execute(DDL_LONG_ROW)
    cur.execute(DDL_LONG_BUY)
    cur.execute(
        f"COMMENT ON TABLE {TABLE_LONG_BUY} IS "
        "'做多過齊進場條件之該日還原收盤買進帳；≠下單≠可交易'"
    )
    cur.execute(
        f"COMMENT ON TABLE {TABLE_LONG_ROW} IS "
        "'做多相對強 Top k 池（含等回撤）；回撤近→遠；≠可交易'"
    )


def ensure_short(cur) -> None:
    cur.execute(DDL_SHORT_ASOF)
    cur.execute(DDL_SHORT_ROW)
    cur.execute(DDL_SHORT_SELL)
    cur.execute(
        f"COMMENT ON TABLE {TABLE_SHORT_SELL} IS "
        "'做空過齊進場條件之該日還原收盤賣出帳；≠下單≠可融券≠可交易'"
    )
    cur.execute(
        f"COMMENT ON TABLE {TABLE_SHORT_ROW} IS "
        "'做空相對弱 Top k 池（含等反彈）；反彈近→遠；≠可空'"
    )


def model_asofs(asof) -> dict[str, Optional[str]]:
    from augur.models import registry
    out = {}
    for h in up.H_TRACK:
        row = registry.latest(FAMILY, h, asof)
        if not row:
            out[str(h)] = None
        else:
            snap = row.get("asof_snapshot")
            out[str(h)] = None if snap is None else str(snap)[:10]
    return out


def attach_hold_returns(conn, asof, sids, *, hold: int = HOLD_TD) -> dict[str, dict]:
    """每股 t+1→t+1+hold 的 log 報酬。未實現者不編造。"""
    dd = asof_ready.as_date(asof)
    cal = label_mod.full_calendar(conn)
    entry, exit_, ok = hold_window(cal, dd, hold)
    out = {}
    logs = {}
    if ok and sids:
        logs = label_mod.forward_returns(conn, dd, list(sids), hold, calendar=cal)
    for sid in sids:
        lg = logs.get(sid) if ok else None
        sp = _simple_pct(lg)
        out[sid] = {
            "entry_date": entry,
            "exit_date": exit_,
            "realized": bool(ok and lg is not None),
            "ret_30_log": None if lg is None else float(lg),
            "ret_30_pct": None if sp is None else round(float(sp), 6),
        }
    return out


def persist_entries(conn, payload: Mapping[str, Any], *, hold: int = HOLD_TD) -> dict:
    """覆寫該 asof 的進場條件列；等回撤／等反彈不入帳。"""
    asof = asof_ready.as_date(payload["asof"])
    stamps = payload.get("model_asofs") or model_asofs(asof)
    note = payload.get("note") or ""
    k = int(payload.get("k") or 10)
    rows_spec = []
    for side, pack in (("long", payload.get("long") or {}), ("short", payload.get("short") or {})):
        for r in pack.get("rows") or []:
            if r.get("tag") != up.RIDGE_THEN_PB_ENTRY:
                continue
            rows_spec.append((side, r))
    sids = [r["sid"] for _s, r in rows_spec]
    rets = attach_hold_returns(conn, asof, sids, hold=hold) if sids else {}
    with db.transaction(conn) as cur:
        ensure(cur)
        cur.execute(f"DELETE FROM {TABLE} WHERE asof_date=%s", (asof,))
        tuples = []
        for side, r in rows_spec:
            hr = rets.get(r["sid"]) or {}
            sp = hr.get("ret_30_pct")
            tuples.append((
                asof, side, r["sid"], r.get("name") or "", r["tag"],
                r.get("ridge_rank"), r.get("rank"), r.get("avg_score"),
                r.get("dd20_pct"), r.get("bu20_pct"),
                Json(r.get("gates") or {}),
                Json(r.get("window_pass") or {}),
                Json(stamps),
                k, FAMILY, hold,
                hr.get("entry_date"), hr.get("exit_date"),
                hr.get("ret_30_log"),
                sp,
                _net_pct(sp, side=side),
                bool(hr.get("realized")),
                note,
            ))
        if tuples:
            execute_values(
                cur,
                f"INSERT INTO {TABLE} ("
                "asof_date, side, stock_id, name, tag, ridge_rank, sort_rank, avg_score, "
                "dd20_pct, bu20_pct, gates, window_pass, model_asofs, k, family, hold_td, "
                "entry_date, exit_date, ret_30_log, ret_30_pct, ret_30_pct_net, realized, note"
                ") VALUES %s",
                tuples,
            )
    n_long = sum(1 for s, _ in rows_spec if s == "long")
    n_short = sum(1 for s, _ in rows_spec if s == "short")
    n_real = sum(1 for _s, r in rows_spec if (rets.get(r["sid"]) or {}).get("realized"))
    return {
        "table": TABLE,
        "asof": str(asof),
        "n_long": n_long,
        "n_short": n_short,
        "n_realized_30": n_real,
        "hold_td": hold,
        "cost": COST,
        "returns": {sid: rets[sid] for sid in sids},
    }


def processed_long_asofs(conn) -> set:
    """已跑過做多收盤帳的 asof（含當日 0 檔進場）。"""
    with db.transaction(conn) as cur:
        ensure_long(cur)
        cur.execute(f"SELECT asof_date FROM {TABLE_LONG_ASOF}")
        return {r[0] for r in cur.fetchall()}


def persist_long_close_buys(
    conn,
    payload: Mapping[str, Any],
    closes: Mapping[str, float],
) -> dict:
    """覆寫該 asof 做多 Top k 池；過齊且有當日收盤者寫入買進帳。缺價不編造。"""
    asof = asof_ready.as_date(payload["asof"])
    stamps = payload.get("model_asofs") or model_asofs(asof)
    note = payload.get("note") or LONG_BUY_NOTE
    k = int(payload.get("k") or 10)
    pack = payload.get("long") or {}
    rows = list(pack.get("rows") or [])
    n_entry_tag = sum(1 for r in rows if r.get("tag") == up.RIDGE_THEN_PB_ENTRY)
    n_buy = 0
    n_skip_px = 0
    with db.transaction(conn) as cur:
        ensure_long(cur)
        cur.execute(f"DELETE FROM {TABLE_LONG_BUY} WHERE asof_date=%s", (asof,))
        cur.execute(f"DELETE FROM {TABLE_LONG_ROW} WHERE asof_date=%s", (asof,))
        cur.execute(f"DELETE FROM {TABLE_LONG_ASOF} WHERE asof_date=%s", (asof,))
        row_tuples = []
        buy_tuples = []
        for r in rows:
            sid = str(r["sid"])
            tag = r.get("tag")
            px = closes.get(sid)
            buy_date = asof if (tag == up.RIDGE_THEN_PB_ENTRY and px is not None) else None
            buy_price = None if buy_date is None else float(px)
            if tag == up.RIDGE_THEN_PB_ENTRY and px is None:
                n_skip_px += 1
            row_tuples.append((
                asof, r.get("rank"), sid, r.get("name") or "", tag,
                r.get("ridge_rank"), r.get("avg_score"), r.get("dd20_pct"),
                Json(r.get("window_pass") or {}),
                Json(r.get("path_pct") or {}),
                Json(r.get("gates") or {}),
                buy_date, buy_price,
            ))
            if buy_date is not None:
                n_buy += 1
                buy_tuples.append((
                    asof, sid, r.get("name") or "", buy_date, buy_price,
                    r.get("dd20_pct"),
                    Json(r.get("window_pass") or {}),
                    Json(r.get("path_pct") or {}),
                    Json(r.get("gates") or {}),
                    r.get("ridge_rank"), r.get("rank"), r.get("avg_score"),
                    tag, FAMILY, note,
                ))
        if row_tuples:
            execute_values(
                cur,
                f"INSERT INTO {TABLE_LONG_ROW} ("
                "asof_date, sort_rank, stock_id, name, tag, ridge_rank, avg_score, "
                "dd20_pct, window_pass, path_pct, gates, buy_date, buy_price"
                ") VALUES %s",
                row_tuples,
            )
        if buy_tuples:
            execute_values(
                cur,
                f"INSERT INTO {TABLE_LONG_BUY} ("
                "asof_date, stock_id, name, buy_date, buy_price, dd20_pct, "
                "window_pass, path_pct, gates, ridge_rank, sort_rank, avg_score, "
                "tag, family, note"
                ") VALUES %s",
                buy_tuples,
            )
        cur.execute(
            f"INSERT INTO {TABLE_LONG_ASOF} ("
            "asof_date, n_pool, n_entry, n_wait, k, family, model_asofs, note"
            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                asof, len(rows), n_entry_tag, len(rows) - n_entry_tag, k,
                FAMILY, Json(stamps), note,
            ),
        )
    return {
        "table_buy": TABLE_LONG_BUY,
        "table_row": TABLE_LONG_ROW,
        "table_asof": TABLE_LONG_ASOF,
        "asof": str(asof),
        "n_pool": len(rows),
        "n_entry": n_entry_tag,
        "n_buy": n_buy,
        "n_skip_px": n_skip_px,
        "fill": "asof_close",
    }


def processed_short_asofs(conn) -> set:
    """已跑過做空收盤帳的 asof（含當日 0 檔進場）。"""
    with db.transaction(conn) as cur:
        ensure_short(cur)
        cur.execute(f"SELECT asof_date FROM {TABLE_SHORT_ASOF}")
        return {r[0] for r in cur.fetchall()}


def persist_short_close_sells(
    conn,
    payload: Mapping[str, Any],
    closes: Mapping[str, float],
) -> dict:
    """覆寫該 asof 做空 Top k 池；過齊且有當日收盤者寫入賣出帳。缺價不編造。≠可空。"""
    asof = asof_ready.as_date(payload["asof"])
    stamps = payload.get("model_asofs") or model_asofs(asof)
    note = payload.get("note") or SHORT_SELL_NOTE
    k = int(payload.get("k") or 10)
    pack = payload.get("short") or {}
    rows = list(pack.get("rows") or [])
    n_entry_tag = sum(1 for r in rows if r.get("tag") == up.RIDGE_THEN_PB_ENTRY)
    n_sell = 0
    n_skip_px = 0
    with db.transaction(conn) as cur:
        ensure_short(cur)
        cur.execute(f"DELETE FROM {TABLE_SHORT_SELL} WHERE asof_date=%s", (asof,))
        cur.execute(f"DELETE FROM {TABLE_SHORT_ROW} WHERE asof_date=%s", (asof,))
        cur.execute(f"DELETE FROM {TABLE_SHORT_ASOF} WHERE asof_date=%s", (asof,))
        row_tuples = []
        sell_tuples = []
        for r in rows:
            sid = str(r["sid"])
            tag = r.get("tag")
            px = closes.get(sid)
            sell_date = asof if (tag == up.RIDGE_THEN_PB_ENTRY and px is not None) else None
            sell_price = None if sell_date is None else float(px)
            if tag == up.RIDGE_THEN_PB_ENTRY and px is None:
                n_skip_px += 1
            row_tuples.append((
                asof, r.get("rank"), sid, r.get("name") or "", tag,
                r.get("ridge_rank"), r.get("avg_score"), r.get("bu20_pct"),
                Json(r.get("window_pass") or {}),
                Json(r.get("path_pct") or {}),
                Json(r.get("gates") or {}),
                sell_date, sell_price,
            ))
            if sell_date is not None:
                n_sell += 1
                sell_tuples.append((
                    asof, sid, r.get("name") or "", sell_date, sell_price,
                    r.get("bu20_pct"),
                    Json(r.get("window_pass") or {}),
                    Json(r.get("path_pct") or {}),
                    Json(r.get("gates") or {}),
                    r.get("ridge_rank"), r.get("rank"), r.get("avg_score"),
                    tag, FAMILY, note,
                ))
        if row_tuples:
            execute_values(
                cur,
                f"INSERT INTO {TABLE_SHORT_ROW} ("
                "asof_date, sort_rank, stock_id, name, tag, ridge_rank, avg_score, "
                "bu20_pct, window_pass, path_pct, gates, sell_date, sell_price"
                ") VALUES %s",
                row_tuples,
            )
        if sell_tuples:
            execute_values(
                cur,
                f"INSERT INTO {TABLE_SHORT_SELL} ("
                "asof_date, stock_id, name, sell_date, sell_price, bu20_pct, "
                "window_pass, path_pct, gates, ridge_rank, sort_rank, avg_score, "
                "tag, family, note"
                ") VALUES %s",
                sell_tuples,
            )
        cur.execute(
            f"INSERT INTO {TABLE_SHORT_ASOF} ("
            "asof_date, n_pool, n_entry, n_wait, k, family, model_asofs, note"
            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                asof, len(rows), n_entry_tag, len(rows) - n_entry_tag, k,
                FAMILY, Json(stamps), note,
            ),
        )
    return {
        "table_sell": TABLE_SHORT_SELL,
        "table_row": TABLE_SHORT_ROW,
        "table_asof": TABLE_SHORT_ASOF,
        "asof": str(asof),
        "n_pool": len(rows),
        "n_entry": n_entry_tag,
        "n_sell": n_sell,
        "n_skip_px": n_skip_px,
        "fill": "asof_close",
        "disclaimer": "做空欄是條件排序，不是下單、不是可融券可成交",
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    print("[ridge_then_pb_store selftest]")
    chk("表名", TABLE == "ridge_then_pb_entry")
    chk("DDL", "CREATE TABLE IF NOT EXISTS" in DDL and "PRIMARY KEY" in DDL)
    chk("做多收盤表", TABLE_LONG_BUY == "ridge_then_pb_long_buy")
    chk("做多池表", TABLE_LONG_ROW == "ridge_then_pb_long_row")
    chk("做多日標", TABLE_LONG_ASOF == "ridge_then_pb_long_asof")
    chk("收盤 DDL", "buy_price" in DDL_LONG_BUY and "asof_date" in DDL_LONG_ASOF)
    chk("做空收盤表", TABLE_SHORT_SELL == "ridge_then_pb_short_sell")
    chk("做空池表", TABLE_SHORT_ROW == "ridge_then_pb_short_row")
    chk("做空日標", TABLE_SHORT_ASOF == "ridge_then_pb_short_asof")
    chk("賣出 DDL", "sell_price" in DDL_SHORT_SELL and "asof_date" in DDL_SHORT_ASOF)
    chk("HOLD=30", HOLD_TD == 30)
    e, x, realized = hold_window(
        [date(2026, 6, 1) + timedelta(days=i) for i in range(80)],
        date(2026, 6, 1),
        30,
    )
    chk("窗有進場", e is not None and realized is True and x is not None)
    e2, x2, ok2 = hold_window([date(2026, 8, 18), date(2026, 8, 19)], date(2026, 8, 19), 30)
    chk("價頂不足不編造", ok2 is False and x2 is None)
    chk("做空淨％變號", abs((_net_pct(10.0, side="short") or 0) - (-10.0 - COST * 100)) < 1e-9)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.evaluation.ridge_then_pb_store --selftest)")
