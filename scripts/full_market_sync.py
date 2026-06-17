#!/usr/bin/env python
"""augur 全市場全量 sync + 逐 dataset #7 對帳 + 問題記錄（從零，resume-capable）。

這支在做什麼（白話）：從零把全市場全史 raw 抓進 DB，**逐 dataset** 抓完即做 #7 DB↔API byte 對帳
（證明無 AI 幻像），所有問題寫進 `reports/augur_fullsync_issues_<date>.md`。可中斷續跑（sync 之
DB-driven resume + 冪等 upsert）。

序列：PHASE 1 bootstrap → 2 seed 名冊 → 2b FRED → 4 全日頻 dataset(逐個 sync) → 5 逐 dataset 對帳。
速率：finmind.py 內建主動限速（#17，現行值見該檔；長跑不 burst 被封）。
⚠️ long-running（全 82 dataset 全史 ~數天，跨日）；須確保主機不進睡眠（依環境設電源：Linux `systemd-inhibit` / macOS `caffeinate` / 雲機電源設定）+ DB-driven resume 後路（中斷可續）。

守 #1/#2（忠實落地 + API 即權威）· #6（冪等 + resume）· #7（逐 dataset byte 對帳，無幻像）· #15（問題誠實記錄）· #17（限速）。
用法：python scripts/full_market_sync.py   （可重跑續傳）
"""
import argparse
import time
import traceback

from augur.audit import reconcile
from augur.core import db, schema
from augur.ingestion import finmind, sync

ISSUES_MD = "reports/augur_fullsync_issues_20260613.md"
RECENT = "2026-05-01"   # 逐 dataset 對帳之近窗取樣（非全史對帳，避免 double 全量）
PERSTOCK_SAMPLE = 60    # per-stock 對帳抽樣股數（1 call/股；平衡覆蓋 vs API 量；見 reconcile_per_stock）

# FRED 總經 series（augur 自選之標準 macro 因子：利率/殖利率曲線/失業/通膨/工業生產/匯率/油/信用利差；
# clean-room——非參考 stock_backend，為標準總經指標）
FRED_SERIES = ["T10Y2Y", "T10Y3M", "DGS10", "DGS2", "FEDFUNDS", "UNRATE",
               "CPIAUCSL", "INDPRO", "VIXCLS", "DTWEXBGS", "DCOILWTICO", "BAMLH0A0HYM2"]


def log(m):
    print(f"[{int(time.time())%100000:05d}] {m}", flush=True)


def issue(dataset, kind, detail):
    with open(ISSUES_MD, "a") as f:
        f.write(f"| `{dataset}` | {kind} | {str(detail)[:180].replace(chr(10), ' ')} |\n")


def _has_date(conn, table):
    """有真 DATE 型別 date 欄才走 by-date 對帳；date 欄為 VARCHAR(如 FutOptTickInfo 契約月 '2026/06')走 market。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT 1 FROM information_schema.columns "
                    "WHERE table_name=%s AND column_name='date' AND data_type='date'", (table,))
        return cur.fetchone() is not None


def _reconcile_scope(conn, table):
    """查 catalog `reconcile_scope`（對帳方法路由）；無 catalog 記錄 → None。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT reconcile_scope FROM dataset_catalog WHERE dataset=%s", (table,))
        row = cur.fetchone()
    return row[0] if row else None


def verify(conn, table):
    """逐 API #7 對帳（近窗取樣，無幻像）。回 (passed|None, result|errstr)。

    路由（依 catalog reconcile_scope）：roster-scoped（per-stock 落地）→ per-stock 對帳（對齊抓取
    端點，避免 by-date 端點差之假 VM）；否則有 date 欄→by-date、無→market。
    """
    try:
        if _reconcile_scope(conn, table) == "roster-scoped":
            r = reconcile.reconcile_per_stock(conn, table, since=RECENT, sample_n=PERSTOCK_SAMPLE)
        elif _has_date(conn, table):
            r = reconcile.reconcile_by_date(conn, table, since=RECENT)
        else:
            r = reconcile.reconcile_market(conn, table)
        return reconcile.verdict(r)["passed"], r
    except Exception as e:
        return None, str(e)


def _has_data(conn, table):
    """DB 已有該表且有資料 → True（--new-only 跳過已有表,交 daily_maintenance by-date 增量）。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name=%s", (table,))
        if not cur.fetchone():
            return False
        cur.execute(f'SELECT 1 FROM "{table}" LIMIT 1')
        return cur.fetchone() is not None


def main():
    ap = argparse.ArgumentParser(description="augur 全市場 sync + 逐 dataset #7 對帳")
    ap.add_argument("--new-only", action="store_true",
                    help="只跑 DB 尚無資料的新 dataset(已有表交 daily_maintenance by-date 增量,省 per-stock resume)")
    new_only = ap.parse_args().new_only
    t0 = time.monotonic()
    with open(ISSUES_MD, "w") as f:
        f.write("# augur 全市場全量 sync 問題記錄 (2026-06-13)\n\n")
        f.write("實跑 source-traceable（#15）；對帳=近窗取樣 #7（VM/EX）。resume-capable。\n\n")
        f.write("| dataset | 類型 | 細節 |\n|---|---|---|\n")

    with db.connect() as conn:
        log("PHASE 1 bootstrap infra log 表")
        with db.transaction(conn) as cur:
            schema.bootstrap_infra(cur)

        log("PHASE 2 seed roster (TaiwanStockInfo)")
        try:
            roster = sync.seed_roster(conn)
            log(f"  roster {len(roster)} 股")
            p, r = verify(conn, "TaiwanStockInfo")
            log(f"  TaiwanStockInfo 對帳: {'PASS' if p else 'FAIL/err'} {r if p is None else ''}")
            if p is False:
                issue("TaiwanStockInfo", "對帳 FAIL", f"VM={r['value_mismatch']} EX={r['extra_in_db']}")
        except Exception as e:
            issue("TaiwanStockInfo", "seed error", e)
            log(f"  ❌ seed 失敗: {e}")
            return

        if new_only and _has_data(conn, "fred_series"):
            log("PHASE 2b FRED：--new-only 跳過(已有,已對帳 PASS)")
        else:
            log("PHASE 2b FRED")
            try:
                rf = sync.sync_fred(conn, FRED_SERIES)
                log(f"  FRED {rf['rows']} 列 / {rf['series']} series")
                rr = reconcile.reconcile_fred(conn, FRED_SERIES)
                fp = reconcile.verdict(rr)["passed"]
                log(f"  FRED 對帳: {'PASS' if fp else 'FAIL'} (VM={rr['value_mismatch']} EX={rr['extra_in_db']})")
                if not fp:
                    issue("fred_series", "對帳 FAIL", f"VM={rr['value_mismatch']} EX={rr['extra_in_db']}")
            except Exception as e:
                issue("fred_series", "FRED error", e)
                log(f"  ❌ FRED: {e}")

        log("PHASE 4+5 全日頻 dataset 逐個 sync + 對帳")
        datasets = sync.daily_datasets()
        log(f"  {len(datasets)} 日頻 dataset")
        done = ok = skipped = 0
        for i, ds in enumerate(datasets, 1):
            el = (time.monotonic() - t0) / 60
            if new_only and _has_data(conn, ds):
                skipped += 1
                log(f"[{i}/{len(datasets)}] {ds}: 已有資料 → --new-only 跳過")
                continue
            try:
                r = sync.sync_finmind_dataset(conn, ds, roster, progress=log)
                done += 1
                log(f"[{i}/{len(datasets)}] {ds}: {r['mode']} {r['rows']:,} 列  (elapsed {el:.0f}min)")
                if r["mode"] in ("not-by-date-capable", "per-stock-non-canonical"):
                    issue(ds, "date-based/需特定id", f"{r['mode']}（需 by-date 或 data_id 專路徑）")
                    continue
                if r["rows"] == 0:
                    issue(ds, "0 列", f"{r['mode']}（tier 限制/空/需特定參數）")
                    continue
                passed, rec = verify(conn, ds)
                if passed is True:
                    ok += 1
                    log(f"    ✅ #7 對帳 PASS")
                elif passed is False:
                    issue(ds, "對帳 FAIL（疑幻像/不一致）", f"VM={rec['value_mismatch']} EX={rec['extra_in_db']} MIS={rec['missing_in_db']}")
                    log(f"    ⚠️ 對帳 FAIL VM={rec['value_mismatch']} EX={rec['extra_in_db']}")
                else:
                    issue(ds, "對帳 error", rec)
                    log(f"    ⚠️ 對帳 error: {rec}")
            except finmind.FinMindError as e:
                issue(ds, "FinMind error", e)
                log(f"    ❌ FinMind: {e}")
            except Exception as e:
                issue(ds, "exception", traceback.format_exc()[-180:])
                log(f"    ❌❌ {type(e).__name__}: {e}")
        log(f"DONE {done} sync / {ok} 對帳 PASS"
            + (f" / {skipped} 已有跳過" if new_only else "")
            + f" / 總 {(time.monotonic()-t0)/60:.0f}min")


if __name__ == "__main__":
    main()
