#!/usr/bin/env python
"""🎯 資料新鮮度哨兵——catalog 驅動，逐 dataset 問「這張表還在更新嗎」，日更表停更即紅。

起因（優化計畫書 20260803 第 14 步 M-G9）：82 張具 `date` 欄之 vendor 表**零 per-dataset
新鮮度哨兵**。`TaiwanStockTotalReturnIndex` 自 2026-07-09 起停更，下游三處（H 軌
`h_fires` 之當月日期集合、market 型模型之 TAIEX 序列末點、`market_direction_feature`
panel）跟著靜默失效 —— 全程沒有任何機制會亮燈，直到人親手去查 `max(date)` 才發現。

**設計約束（非可選）**：不得以裸 `max(date)` 全掃。本庫索引幾乎都是 `(stock_id, date)`
形狀，date 非前導欄 ⇒ 裸 max 得掃完整棵索引：實測 `TaiwanStockPriceAdj` 單表 20.27s、
全量逾 120s 被 timeout。本支改走 `augur.audit.freshness` 之四條路徑（堆尾預探 ＋
date-leading／skip-scan／plain-max），全量目標 < 60s，超時即紅（`--budget-sec`）。

**判準住 library、不住本檔**（#12）：紅／黃／綠三態、節奏推定、交易日換算全在
`augur.audit.freshness`（純函式、`--selftest` 可個別驗證）；本檔只做 DB IO、列印、
與 `validation_evidence` 之冪等 upsert。

**堆尾預探為何只准判綠**：`ctid >= '(blocks-N,0)'` 讀到的是真實存在之列，故
「堆尾已達期望日 ⇒ 全表必達」成立（可判綠）；反向不成立（堆尾舊不代表全表舊，
upsert 型表尤然）⇒ 未達標一律落到精確路徑重問，絕不據堆尾判紅。

守 #15（紅燈要會亮：本支之通過條件即「今日 live 必須有紅」，全綠視為未通過）·
#9／#10（每個日期出自真 query，可 trace 回本檔所印之 SQL 模式）· #28（純本地、零 API、
零 usage）· #29(a)(b)(d)（個別可執行／來源住 DB／指令矩陣＋實測）· #35（自測餵真輸出）。

執行指令矩陣
------------
    python scripts/check_dataset_freshness.py                       # 無參數＝--check（唯讀；有 red → exit 1）
    python scripts/check_dataset_freshness.py --check               # 全量掃描＋逐表判定
    python scripts/check_dataset_freshness.py --check --json        # 機器可讀（供 cron／稽核）
    python scripts/check_dataset_freshness.py --check --only TaiwanStockTotalReturnIndex
    python scripts/check_dataset_freshness.py --check --max-lag 5   # 放寬容忍（交易日）
    python scripts/check_dataset_freshness.py --check --strict      # amber 亦計入 exit 1
    python scripts/check_dataset_freshness.py --check --simulate TaiwanStockTotalReturnIndex=2026-07-31
                                                                    # 鑑別力雙向驗證：假游標不碰資料
    python scripts/check_dataset_freshness.py --register-evidence   # 冪等 upsert 一列 validation_evidence（DML）
    python scripts/check_dataset_freshness.py --selftest            # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime
from typing import Optional

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from psycopg2 import sql

from augur.audit import freshness
from augur.audit.freshness import DatasetFreshness

CALENDAR_TABLE = "TaiwanStockTradingDate"   # 交易日曆（1999-01-05～2026-12-31、6,937 列）
DATE_COL = "date"
EVIDENCE_ID = "E10_dataset_freshness"
EVIDENCE_CMD = "python scripts/check_dataset_freshness.py --check"
DEFAULT_BUDGET_SEC = 60.0

# catalog 驅動之受檢集合：**登錄於 catalog、表實存、且有 date 欄**者（#29b：清單住 DB，
# 不寫死於本檔；新增 dataset ＝ catalog 多一列即自動納入，零改碼）。
SCOPE_SQL = """
SELECT dc.dataset, dc.frequency, dc.attestation_mode, COALESCE(dc.finalize_lag_days, 1)
FROM dataset_catalog dc
WHERE to_regclass(quote_ident(dc.dataset)) IS NOT NULL
  AND EXISTS (SELECT 1 FROM information_schema.columns c
              WHERE c.table_schema = 'public' AND c.table_name = dc.dataset
                AND c.column_name = %s)
ORDER BY dc.dataset
"""

# 每張表每個 btree 索引之 key 欄序（只取 indnkeyatts 內之欄——INCLUDE 欄不可用於排序）。
INDEX_SQL = """
SELECT c.relname, array_agg(a.attname ORDER BY k.ord)
FROM pg_index x
JOIN pg_class c ON c.oid = x.indrelid
JOIN pg_class i ON i.oid = x.indexrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN LATERAL unnest(x.indkey) WITH ORDINALITY AS k(attnum, ord)
JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = k.attnum
WHERE n.nspname = 'public' AND x.indisvalid
  AND i.relam = (SELECT oid FROM pg_am WHERE amname = 'btree')
  AND k.ord <= x.indnkeyatts
GROUP BY c.relname, i.relname
"""


# ── 型別轉換 ─────────────────────────────────────────────────────────────────

def as_date(v) -> Optional[date]:
    """把 query 回傳值轉成 `date`；text 欄只接受 ISO 前綴，解不出來一律 None（不猜）。

    本庫兩張表之 `date` 欄為 varchar：`TaiwanStockNews`（'2026-08-01'，可解）與
    `TaiwanFutOptTickInfo`（'2027/06' 契約月份，解不出 ⇒ 誠實 None ⇒ amber）。
    """
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


# ── DB 探測（唯讀） ──────────────────────────────────────────────────────────

def load_calendar(cur) -> list:
    cur.execute(sql.SQL("SELECT {C} FROM {T} WHERE {C} IS NOT NULL ORDER BY {C}")
                .format(C=sql.Identifier(DATE_COL), T=sql.Identifier(CALENDAR_TABLE)))
    return [r[0] for r in cur.fetchall()]


def load_index_columns(cur) -> dict:
    cur.execute(INDEX_SQL)
    out = {}
    for tbl, cols in cur.fetchall():
        out.setdefault(tbl, []).append(list(cols))
    return out


def heap_blocks(cur, table: str) -> int:
    cur.execute("SELECT (pg_relation_size(quote_ident(%s)::regclass) / 8192)::bigint", (table,))
    return int(cur.fetchone()[0] or 0)


def tail_dates(cur, table: str, blocks: int) -> list:
    """堆尾最後 `TAIL_BLOCKS` 個 block 內之最近相異日期（用於推節奏＋判綠下界）。"""
    lo = max(0, blocks - freshness.TAIL_BLOCKS)
    cur.execute(
        sql.SQL("SELECT DISTINCT {C} FROM {T} WHERE ctid >= %s::tid AND {C} IS NOT NULL "
                "ORDER BY {C} DESC LIMIT %s")
        .format(C=sql.Identifier(DATE_COL), T=sql.Identifier(table)),
        (f"({lo},0)", freshness.TAIL_DATE_SAMPLE))
    return [d for d in (as_date(r[0]) for r in cur.fetchall()) if d is not None]


def exact_max(cur, table: str, probe: freshness.Probe, target: Optional[date]) -> Optional[date]:
    """全表精確最新日期，走 `probe` 指定之索引友善路徑。**不得**退化為裸全掃（除 plain-max）。"""
    T, C = sql.Identifier(table), sql.Identifier(DATE_COL)
    if probe.mode == freshness.PROBE_DATE_LEADING:
        cur.execute(sql.SQL("SELECT {C} FROM {T} WHERE {C} IS NOT NULL "
                            "ORDER BY {C} DESC LIMIT 1").format(C=C, T=T))
    elif probe.mode == freshness.PROBE_SKIP_SCAN:
        K = sql.Identifier(probe.key)
        nxt = sql.SQL("(SELECT n.{K} FROM {T} n WHERE n.{K} > w.k ORDER BY n.{K} LIMIT 1)").format(K=K, T=T)
        # 早停條件：running max 已達期望日就不必再走完剩下的維度 id（55,674 個 stock_id 之表
        # 因此由 4.5s 降到 0.06s）。target 為 None（無日曆）時走完整迴圈、不早停。
        stop = (sql.SQL("AND (w.runmax IS NULL OR w.runmax < %s)") if target is not None
                else sql.SQL(""))
        cur.execute(sql.SQL("""
            WITH RECURSIVE w AS (
                SELECT q.k AS k, (SELECT max(x.{C}) FROM {T} x WHERE x.{K} = q.k) AS runmax
                FROM (SELECT s.{K} AS k FROM {T} s ORDER BY s.{K} LIMIT 1) q
              UNION ALL
                SELECT {nxt}, GREATEST(w.runmax, (SELECT max(x.{C}) FROM {T} x WHERE x.{K} = {nxt}))
                FROM w WHERE w.k IS NOT NULL {stop}
            )
            SELECT max(runmax) FROM w
        """).format(C=C, T=T, K=K, nxt=nxt, stop=stop),
            (target.isoformat(),) if target is not None else None)
    else:
        cur.execute(sql.SQL("SELECT max({C}) FROM {T}").format(C=C, T=T))
    return as_date(cur.fetchone()[0])


def scan_one(cur, row, calendar, index_cols, today, max_lag, simulate) -> DatasetFreshness:
    dataset, frequency, mode, lag_days = row
    f = DatasetFreshness(dataset=dataset, frequency=frequency, attestation_mode=mode,
                         finalize_lag_days=lag_days)
    t0 = time.time()
    f.expected = freshness.expected_asof(calendar, today, lag_days)
    probe = freshness.probe_plan(index_cols.get(dataset, []), DATE_COL)

    if dataset in simulate:                       # 假游標：不碰資料、只換 observed（鑑別力驗證）
        f.observed, f.probe_mode = simulate[dataset], "simulated"
        f.notes.append("⚠ observed 為 --simulate 假游標，非 DB 實查")
        tails = tail_dates(cur, dataset, heap_blocks(cur, dataset))
    else:
        tails = tail_dates(cur, dataset, heap_blocks(cur, dataset))
        tail_max = tails[0] if tails else None
        if tail_max is not None and f.expected is not None and tail_max >= f.expected:
            f.observed, f.probe_mode, f.observed_is_floor = tail_max, "tail-probe", True
        else:
            f.observed, f.probe_mode = exact_max(cur, dataset, probe, f.expected), probe.mode

    f.cadence_tdays = freshness.median_gap_trading_days(tails, calendar)
    f.lag_tdays = freshness.trading_day_lag(f.observed, f.expected, calendar)
    f.status, f.reason = freshness.classify(
        observed=f.observed, expected=f.expected, lag_tdays=f.lag_tdays,
        cadence_tdays=f.cadence_tdays, attestation_mode=f.attestation_mode,
        max_lag_tdays=max_lag)
    f.elapsed_sec = round(time.time() - t0, 3)
    return f


def scan(*, only=None, max_lag=freshness.DEFAULT_MAX_LAG_TDAYS, simulate=None, today=None):
    """→ (rows, elapsed_sec)。全程唯讀（僅 SELECT），不寫任何表。"""
    from augur.core import db

    simulate = simulate or {}
    today = today or date.today()
    t0 = time.time()
    with db.connect() as conn:
        cur = conn.cursor()
        calendar = load_calendar(cur)
        index_cols = load_index_columns(cur)
        cur.execute(SCOPE_SQL, (DATE_COL,))
        targets = [r for r in cur.fetchall() if not only or r[0] in only]
        rows = [scan_one(cur, r, calendar, index_cols, today, max_lag, simulate) for r in targets]
    return rows, round(time.time() - t0, 2)


# ── 模式 ─────────────────────────────────────────────────────────────────────

_ICON = {freshness.STATUS_GREEN: "✓", freshness.STATUS_AMBER: "▲", freshness.STATUS_RED: "✗"}


def _row_dict(f: DatasetFreshness) -> dict:
    return {"dataset": f.dataset, "status": f.status, "reason": f.reason,
            "observed": f.observed.isoformat() if f.observed else None,
            "observed_is_floor": f.observed_is_floor,
            "expected": f.expected.isoformat() if f.expected else None,
            "lag_tdays": f.lag_tdays, "cadence_tdays": f.cadence_tdays,
            "probe_mode": f.probe_mode, "frequency": f.frequency,
            "attestation_mode": f.attestation_mode, "elapsed_sec": f.elapsed_sec,
            "notes": f.notes}


def check(*, as_json=False, only=None, max_lag=freshness.DEFAULT_MAX_LAG_TDAYS,
          simulate=None, strict=False, budget=DEFAULT_BUDGET_SEC) -> int:
    rows, elapsed = scan(only=only, max_lag=max_lag, simulate=simulate)
    over_budget = budget > 0 and elapsed > budget
    statuses = [f.status for f in rows] + ([freshness.STATUS_RED] if over_budget else [])
    if as_json:
        print(json.dumps({"elapsed_sec": elapsed, "budget_sec": budget,
                          "over_budget": over_budget, "max_lag_tdays": max_lag,
                          "rows": [_row_dict(f) for f in rows]}, ensure_ascii=False, indent=2))
        return freshness.rc_of(statuses, strict)

    order = {freshness.STATUS_RED: 0, freshness.STATUS_AMBER: 1, freshness.STATUS_GREEN: 2}
    print(f"── 資料新鮮度哨兵（{len(rows)} dataset／容忍 {max_lag} 交易日） ──")
    for f in sorted(rows, key=lambda r: (order[r.status], r.dataset)):
        floor = "≥" if f.observed_is_floor else "="
        print(f"  {_ICON[f.status]} {f.dataset:<48} max{floor}{f.observed or '—'}"
              f"  期望={f.expected or '—'}  {f.reason}")
        for n in f.notes:
            print(f"      {n}")
    n_red = sum(1 for f in rows if f.status == freshness.STATUS_RED)
    n_amber = sum(1 for f in rows if f.status == freshness.STATUS_AMBER)
    print(f"  ── red {n_red}／amber {n_amber}／green {len(rows) - n_red - n_amber}"
          f"；全量 {elapsed}s（預算 {budget}s{'，⚠ 超時' if over_budget else ''}）")
    if n_red == 0 and not simulate:
        print("  ⚠ 全無 red：本哨兵之通過條件是「今日 live 必須抓得出停更表」——"
              "全綠請先懷疑口徑（受檢集合是否為空／期望日是否算錯），不要當作沒事。")
    slow = sorted((f for f in rows), key=lambda r: -r.elapsed_sec)[:3]
    print("  最慢三表：" + "；".join(f"{f.dataset} {f.elapsed_sec}s({f.probe_mode})" for f in slow))
    return freshness.rc_of(statuses, strict)


def register_evidence(*, max_lag=freshness.DEFAULT_MAX_LAG_TDAYS) -> int:
    """冪等 upsert 一列 `validation_evidence`（DML；不建表、不改 schema、不填人簽欄）。"""
    from augur.core import db

    rows, elapsed = scan(max_lag=max_lag)
    reds = [f for f in rows if f.status == freshness.STATUS_RED]
    ambers = [f for f in rows if f.status == freshness.STATUS_AMBER]
    status = freshness.STATUS_RED if reds else (freshness.STATUS_AMBER if ambers
                                                else freshness.STATUS_GREEN)
    note = (f"{len(rows)} dataset／{elapsed}s：red {len(reds)}"
            + (" [" + "、".join(f"{f.dataset}(停更 {f.lag_tdays} 交易日)" for f in reds[:8]) + "]"
               if reds else "")
            + f"；amber {len(ambers)}")[:900]
    claim = (f"catalog 內每張具 date 欄之表，其最新日期落後不超過 {max_lag} 個交易日"
             "（日更表停更即 red；週期／事件／snapshot 型落 amber）")
    status_note = ("M-G9：本列之紅燈載體為『日更表停更』。修法是把該表的抓取鏈接回去"
                   "（如 M-G10 之 _dimension_sync 接線），不是放寬 --max-lag 或加豁免。"
                   "（優化計畫書 20260803 第 14 步 驗收②：全綠即視為未通過。）")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO validation_evidence "
            "(evidence_id, chain_link, claim, check_type, check_cmd, source_ref, "
            " status, status_note, machine_note, last_verified_at) "
            "VALUES (%s,'raw',%s,'script_exit',%s,%s,%s,%s,%s,now()) "
            "ON CONFLICT (evidence_id) DO UPDATE SET "
            "  claim=EXCLUDED.claim, check_cmd=EXCLUDED.check_cmd, "
            "  source_ref=EXCLUDED.source_ref, status=EXCLUDED.status, "
            "  machine_note=EXCLUDED.machine_note, last_verified_at=now()",
            (EVIDENCE_ID, claim, EVIDENCE_CMD,
             "reports/augur_optimization_master_plan_20260803.md 第 14 步（M-G9）"
             "；src/augur/audit/freshness.py",
             status, status_note, note))
        conn.commit()
        cur.execute("SELECT status, machine_note, last_verified_at FROM validation_evidence "
                    "WHERE evidence_id = %s", (EVIDENCE_ID,))
        got = cur.fetchone()
    print(f"✓ validation_evidence upsert：{EVIDENCE_ID} → {got[0]}")
    print(f"  machine_note：{got[1]}")
    print(f"  last_verified_at：{got[2]}")
    print("  （status_note 僅首次 INSERT 寫入;重跑不覆寫——人裁欄不受機器每跑抹除）")
    return freshness.rc_of([got[0]])


# ── 自測（#35：純函式餵真輸入、紅綠雙向；免 DB 免 API） ──────────────────────

def selftest() -> int:
    rc = freshness._selftest()          # 判準本體之紅綠自測（library 側）

    def chk(label, cond):
        nonlocal rc
        print(f"  {'✓' if cond else '✗FAIL'} {label}")
        if not cond:
            rc = 1

    # 型別轉換：兩張 varchar date 欄之真實值（live 抽樣 2026-08-03）
    chk("varchar ISO '2026-08-01'（TaiwanStockNews 真值）→ date", as_date("2026-08-01") == date(2026, 8, 1))
    chk("varchar '2027/06'（TaiwanFutOptTickInfo 真值）→ None（不猜）", as_date("2027/06") is None)
    chk("date 物件原樣通過", as_date(date(2026, 7, 9)) == date(2026, 7, 9))
    chk("timestamp → 取日部分", as_date(datetime(2026, 7, 9, 13, 30)) == date(2026, 7, 9))
    chk("None → None", as_date(None) is None)
    # SQL 組裝：三條路徑各自可組出可解析之字串，且 skip-scan 早停子句在／不在皆成句
    for mode, key in ((freshness.PROBE_DATE_LEADING, None), (freshness.PROBE_SKIP_SCAN, "stock_id"),
                      (freshness.PROBE_PLAIN_MAX, None)):
        p = freshness.Probe(mode, key)
        chk(f"{mode}: probe 物件欄位齊備", p.mode == mode and p.key == key)
    print("哨兵自測：" + ("全通過 ✓" if rc == 0 else "有 FAIL ✗"))
    return rc


def _parse_simulate(items):
    out = {}
    for it in items or []:
        if "=" not in it:
            raise SystemExit(f"--simulate 需 DATASET=YYYY-MM-DD，收到：{it}")
        ds, _, d = it.partition("=")
        out[ds] = date.fromisoformat(d)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="augur 資料新鮮度哨兵（catalog 驅動、索引友善）")
    ap.add_argument("--check", action="store_true", help="全量掃描（預設模式）")
    ap.add_argument("--json", action="store_true", help="機器可讀輸出")
    ap.add_argument("--only", nargs="*", help="只查指定 dataset")
    ap.add_argument("--max-lag", type=int, default=freshness.DEFAULT_MAX_LAG_TDAYS,
                    help=f"容忍落後幾個交易日（預設 {freshness.DEFAULT_MAX_LAG_TDAYS}）")
    ap.add_argument("--strict", action="store_true", help="amber 亦計入 exit 1")
    ap.add_argument("--budget-sec", type=float, default=DEFAULT_BUDGET_SEC,
                    help="全量掃描時間預算（秒;超出即紅。0＝不設限）")
    ap.add_argument("--simulate", nargs="*", metavar="DS=YYYY-MM-DD",
                    help="以假游標覆寫某 dataset 之 observed（鑑別力雙向驗證;不碰資料）")
    ap.add_argument("--register-evidence", dest="reg", action="store_true",
                    help="冪等 upsert 一列 validation_evidence（DML）")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測（免 DB 免 API）")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    sim = _parse_simulate(args.simulate)
    if args.reg:
        if sim:
            print("✗ --register-evidence 不得與 --simulate 併用（假游標不得入證據帳本）")
            return 2
        return register_evidence(max_lag=args.max_lag)
    return check(as_json=args.json, only=args.only, max_lag=args.max_lag,
                 simulate=sim, strict=args.strict, budget=args.budget_sec)


if __name__ == "__main__":
    sys.exit(main())
