#!/usr/bin/env python
"""augur 對帳總驗 driver — 全 API 表 #7 byte-level attestation,依 catalog reconcile_scope 路由。

🎯 白話:把 DB 既有 API 資料表逐表對 FinMind/FRED 真值比對,**依 catalog `reconcile_scope` 走對的對帳法**——
- by-date(逐交易日全市場):價量/法人/期權 → reconcile_by_date(近 recent_days 定案日;GoldPrice 等聚合表自動對齊日級)。
- roster-scoped(per-stock 端點):籌碼等逐股抓 → reconcile_per_stock(抽樣 ROSTER_SAMPLE 股、部分覆蓋知會 #7;
  近 UNSETTLED_BUFFER 日未定案排除,同 by-date)。
- full-history(季/月頻 per-stock):財報等 → reconcile_per_stock 全史,排除最新一期(發布/重編中未定案 #7 類別②)。
- market(snapshot/單一序列):date-insensitive 表 → reconcile_market 單批寬查(逐日對帳=每史日拿現值 → 假 EX/MIS)。
- by-dim-id(逐維度碼):總經/匯率/利率 → reconcile_by_dim_id(datalist 驅動)。
- coverage(事件流):News 同日多則文本 → reconcile_coverage(列數量級、非逐 byte)。
- fred_series:逐 series 全史 → reconcile_fred(走 FRED 額度、不佔 FinMind)。
全表清單 = catalog excluded=f(動態、非硬編 #18);infra log 表跳過。逐表即時印,末了彙總 #7 verdict。對帳唯讀、冪等、中斷重跑無害。
**逐表 PASS/FAIL 判定不自算、一律交 `reconcile.verdict()`**(#12 單一住所;含 coverage_gap 空視窗擋綠之假綠 blocker);
本 driver 只負責窗策略(未定案日不計)與誠實標註。

守 #7(DB↔API 對帳)· #12(判定住 library、driver 不複製判式)· #15(未定案/抽樣/coverage 誠實標註)·
   #24/#25(走 finmind 內建限速)· #16/#17(clean-room)。
執行指令矩陣:PYTHONPATH=src caffeinate -dimsu venv/bin/python scripts/reconcile_audit.py
      [--only by-date|roster-scoped|full-history|market|by-dim-id|coverage|fred] [--tables A,B] [--recent-days 30]
  venv/bin/python scripts/reconcile_audit.py --selftest   # 判定接線紅綠自測(免 DB 免 API、零 FinMind 呼叫)
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import reconcile
from augur.core import db
from augur.features import macro
from augur.ingestion.ingest import FRED_TABLE, aggregate_method

SKIP = {"data_audit_log", "pipeline_execution_log"}   # infra log,非 API 資料 → 不對帳
RECENT_DAYS = 30
UNSETTLED_BUFFER = 2     # 日頻:最近 N 個交易日視為未定案(當日盤後仍在校正,對帳天然差異)→ 不計 verdict
ROSTER_SAMPLE = 50       # roster-scoped per-stock 對帳抽樣股數(全 roster×31 表太貴;部分覆蓋、報告標註 #7/#15)


def _p(msg):
    print(msg, flush=True)


def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def _catalog_tables(conn):
    """從 catalog 讀全 excluded=f 表 + reconcile_scope + attestation_mode(動態、非硬編 #18)。回 [(dataset, scope, mode)];
    無 reconcile_scope → 預設 by-date;infra log 表略過。catalog 未建 → 空(呼叫端報錯)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('dataset_catalog')")
        if cur.fetchone()[0] is None:
            return []
        cur.execute("SELECT dataset, COALESCE(reconcile_scope,'by-date'), COALESCE(attestation_mode,'byte') "
                    "FROM dataset_catalog WHERE NOT excluded ORDER BY dataset")
        return [(ds, scope, mode) for ds, scope, mode in cur.fetchall() if ds not in SKIP]


def _recent_since(conn, table, recent_days):
    """近 recent_days(+緩衝)個 distinct date 下限,限對帳近窗加速;表無 date/無資料 → None(全史)。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC LIMIT %s',
                        (recent_days + UNSETTLED_BUFFER,))
            dates = [r[0] for r in cur.fetchall()]
        return _iso(dates[-1]) if dates else None   # 回 str(isoformat)：reconcile 各函數 since 比較/SQL/fetch 一律期望 str，免 str>=date 型別錯
    except Exception:
        return None


def _unsettled(conn, table, n=UNSETTLED_BUFFER):
    """最近 n 個 distinct date(未定案、不計 verdict);表無 date → 空。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC LIMIT %s', (n,))
            return {_iso(r[0]) for r in cur.fetchall()}
    except Exception:
        return set()


def _settled_max(conn, table, skip):
    """定案窗上限=排除最新 skip 個 distinct date(未定案)後之最新日;不足 skip+1 個日 → None(不設上限)。"""
    try:
        with db.transaction(conn) as cur:
            cur.execute(f'SELECT DISTINCT date FROM "{table}" ORDER BY date DESC OFFSET %s LIMIT 1', (skip,))
            row = cur.fetchone()
        return _iso(row[0]) if row else None
    except Exception:
        return None


def _audit(conn, dataset, scope, mode, recent_days):
    """依 catalog attestation_mode 豁免(SSOT reconcile.EXEMPT_*)+ reconcile_scope 路由 → 統一 summary。
    attestation_mode 豁免與 daily_maintenance 共用同一政策(#12,(B) 2026-07-14)——根治「reconcile_audit 不認
    attestation_mode → tick/dim_only 假 EX 分歧」;窗策略(unsettled 緩衝)為本 driver 特有、保留。"""
    if mode in reconcile.EXEMPT_MODES:                        # 豁免非靜默(誠實 #15;與 daily_maintenance 同 SSOT)
        _p(f"[{dataset}] 豁免({mode}——{reconcile.EXEMPT_REASON[mode]};catalog #7(b))")
        return _summary(dataset, "exempt",
                        {"table": dataset, "matched": 0, "value_mismatch": 0, "missing_in_db": 0,
                         "extra_in_db": 0, "errors": []})
    if dataset == FRED_TABLE:                                  # fred_series:走 FRED API、全 series 全史
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT series_id FROM fred_series ORDER BY series_id")
            sids = [r[0] for r in cur.fetchall()]
        _p(f"[{dataset}] fred:{len(sids)} series 全史")
        return _summary(dataset, "fred",
                        reconcile.reconcile_fred(conn, sids, vintage_map=macro.vintage_map(), progress=_p))

    if scope == "market":                                      # snapshot/單一序列(date-insensitive):單批寬查,逐日對帳=每史日拿現值 → 假 EX/MIS
        _p(f"[{dataset}] market:單批寬查對帳")
        return _summary(dataset, "market", reconcile.reconcile_market(conn, dataset, progress=_p))
    if scope == "full-history":                                # 季/月頻 per-stock 全史;最新一期發布/重編中未定案(#7 類別②)→ 排除
        until = _settled_max(conn, dataset, skip=1)
        unsettled = _unsettled(conn, dataset, n=1) if until else set()
        _p(f"[{dataset}] full-history:per-stock 全史抽樣 {ROSTER_SAMPLE} 股;未定案最新期 {sorted(unsettled)}")
        agg = reconcile.reconcile_per_stock(conn, dataset, until=until, sample_n=ROSTER_SAMPLE, progress=_p)
        return _summary(dataset, "full-history", agg, unsettled=unsettled)
    since = _recent_since(conn, dataset, recent_days)
    sincestr = _iso(since) if since else "全史"
    if scope == "by-dim-id":
        _p(f"[{dataset}] by-dim-id:逐維度 id 重抓 since {sincestr}")
        return _summary(dataset, "by-dim-id", reconcile.reconcile_by_dim_id(conn, dataset, since=since, progress=_p))
    if scope == "roster-scoped":                               # 日頻籌碼同有次日校正曝險(#7 類別①)→ 同 by-date 排除未定案
        until = _settled_max(conn, dataset, skip=UNSETTLED_BUFFER)
        unsettled = _unsettled(conn, dataset) if until else set()
        _p(f"[{dataset}] roster-scoped:per-stock 抽樣 {ROSTER_SAMPLE} 股 since {sincestr};未定案緩衝 {sorted(unsettled)}")
        agg = reconcile.reconcile_per_stock(conn, dataset, since=since, until=until,
                                            sample_n=ROSTER_SAMPLE, progress=_p)
        return _summary(dataset, "roster-scoped", agg, unsettled=unsettled)
    if scope == "coverage" or aggregate_method(dataset, conn) == "all":   # 事件流 → coverage(依 catalog scope 路由;aggregate_method DB-first、seed dict 為備援 #29b)
        _p(f"[{dataset}] coverage:事件流列數量級對帳")
        return _summary(dataset, "coverage", reconcile.reconcile_coverage(conn, dataset, progress=_p))
    # by-date(含 GoldPrice 聚合,reconcile_by_date 內已對齊日級):排除未定案日 from verdict
    unsettled = _unsettled(conn, dataset)
    _p(f"[{dataset}] by-date:近窗 since {sincestr};未定案緩衝 {sorted(unsettled)}")
    agg = reconcile.reconcile_by_date(conn, dataset, since=since, progress=_p)
    return _summary(dataset, "by-date", agg, unsettled=unsettled)


def _summary(dataset, kind, agg, *, unsettled=None):
    """統一抽出 vm/ex/mis + verdict + 誠實標註(未定案排除 / 抽樣部分覆蓋 / coverage / vintage)。

    **判定交 `reconcile.verdict()`**(#12):本 driver 只算「未定案窗過濾後」之計數再餵進去。
    自算判式(舊碼 `vm==0 and ex==0 and not inc`)漏 `coverage_gap` → 空視窗死 feed 可被認證 PASS(#15 假綠)。"""
    note = ""
    if kind == "by-date" and unsettled:                        # 排除未定案日(當日盤後校正,非真差異)
        per = agg.get("per_date", {})
        sett = {d: c for d, c in per.items() if d not in unsettled}
        vm = sum(c["value_mismatch"] for c in sett.values())
        ex = sum(c["extra_in_db"] for c in sett.values())
        mis = sum(c["missing_in_db"] for c in sett.values())
        if any(d in unsettled for d in per):
            note = f"未定案 {sorted(unsettled)} 不計 verdict"
    else:
        vm, ex, mis = agg.get("value_mismatch", 0), agg.get("extra_in_db", 0), agg.get("missing_in_db", 0)
        if unsettled:                                          # roster-scoped/full-history:窗上限已排除未定案期(#7)
            note = f"未定案 {sorted(unsettled)} 不計 verdict(對帳窗已排除)"
    if vm and "PriceAdj" in dataset:                           # 還原價隨未來除權息回溯重算(#7 類別③,以抓取時點 API 現值為準)
        note = (note + " ｜ " if note else "") + "PriceAdj VM 疑似除權息回溯重算 → 走 heal 重抓對齊現值、非幻像紅旗"
    inc = bool(agg.get("incomplete") or agg.get("errors"))
    vres = {**agg, "table": dataset, "matched": agg.get("matched", 0),        # 其餘旗標(coverage_gap/sampled)原封帶過
            "value_mismatch": vm, "extra_in_db": ex, "missing_in_db": mis, "incomplete": inc}
    passed = reconcile.verdict(vres)["passed"]         # 判定住 library #12:vm/ex/incomplete/coverage_gap 一律由 verdict 判
    if kind == "coverage":
        cov_ok = bool(agg.get("coverage_ok"))          # 量級覆蓋另有判準(漏抓占比容忍)→ 與 verdict 取交集,只會更嚴
        passed = passed and cov_ok
        note = f"coverage {'OK' if cov_ok else 'FAIL'}(漏 {mis}、列數量級非逐 byte)"
    if agg.get("coverage_gap"):                        # 空視窗=從未比對 → 誠實揭露,不靜默(舊判式漏此即假綠)
        note = (note + " ｜ " if note else "") + "空視窗未對帳(coverage_gap:死 feed/窗內無資料)→ 不計綠 #15"
    if agg.get("sampled"):
        note = (note + " ｜ " if note else "") + f"抽樣 {agg.get('stocks', '?')} 股(部分覆蓋 #7)"
    if agg.get("fred_vintage"):
        note = (note + " ｜ " if note else "") + f"Tier A restatement 容忍 {agg['fred_vintage']}"
    # by-date examples 混未定案日差異(無 date 無法乾淨過濾)→ 不放,定案日真差異另查
    examples = [] if kind == "by-date" else agg.get("examples", [])[:3]
    return {"table": dataset, "kind": kind, "matched": agg.get("matched", 0),
            "vm": vm, "ex": ex, "mis": mis, "incomplete": inc, "note": note,
            "examples": examples, "errors": agg.get("errors", [])[:3], "passed": passed}


def _print_row(r):
    """逐表即時印一行(長跑進度監看 #21)+ 標註/差異/錯誤附註。"""
    _p(f"{r['table']:46s} {r['kind']:14s} {r['matched']:>9,} VM{r['vm']:<4} EX{r['ex']:<4} MIS{r['mis']:<7,} "
       f"{'PASS ✅' if r['passed'] else 'FAIL ❌'}")
    if r["note"]:
        _p(f"    └ {r['note']}")
    if r["examples"]:
        _p(f"    └ 差異範例:{r['examples']}")
    if r["errors"]:
        _p(f"    └ ⚠️ 抓取錯誤:{r['errors']}")


def _parse(argv):
    only, tables, recent = None, None, RECENT_DAYS
    i = 0
    while i < len(argv):
        if argv[i] == "--only":
            only = argv[i + 1]; i += 2
        elif argv[i] == "--tables":
            tables = set(argv[i + 1].split(",")); i += 2
        elif argv[i] == "--recent-days":
            recent = int(argv[i + 1]); i += 2
        else:
            i += 1
    return only, tables, recent


class _EmptyCur:
    """自測用零 DB stub cursor:任何查詢皆回空集。餵給 `reconcile_by_date` 即走「空視窗」真路徑
    (dates=[] ⇒ 逐日迴圈零圈 ⇒ **零 finmind.fetch**),取回產生器之真輸出當 fixture。"""

    def execute(self, *a, **k):
        return None

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def close(self):
        return None


class _EmptyConn:
    def cursor(self):
        return _EmptyCur()

    def commit(self):
        return None

    def rollback(self):
        return None


def _selftest():
    """自測(免 DB 免 API):判定接線回歸鎖——fixture 取自 `reconcile` 之**真輸出**(reconcile_by_date
    空視窗 agg / compare 真差異計數),非手寫 dict;直接餵 `_summary` 之真判定路徑,不驗字面。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    gap = reconcile.reconcile_by_date(_EmptyConn(), "SELFTEST_EMPTY")     # 真產生器輸出(零 API)
    base = {**gap, "coverage_gap": False}                                 # 對照臂:僅此一欄之差
    chk("fixture=產生器真輸出:空視窗即標 coverage_gap(產生器鍵名/語意漂移即紅)",
        gap.get("coverage_gap") is True and gap.get("incomplete") is False)
    r_gap, r_ok = _summary("SELFTEST_EMPTY", "by-date", gap), _summary("SELFTEST_EMPTY", "by-date", base)
    chk("空視窗表擋綠(自算判式回 True=假綠;接 verdict 才紅)", r_gap["passed"] is False)
    chk("對照臂:僅去 coverage_gap 即回綠(紅不是別的原因造成)", r_ok["passed"] is True)
    chk("空視窗誠實標註、對照臂無標註(不靜默)", bool(r_gap["note"]) and not r_ok["note"])
    chk("豁免表不因接 verdict 誤紅", _summary("X", "exempt", base)["passed"] is True)
    chk("抓取失敗(errors)仍擋綠", _summary("X", "by-date", {**base, "errors": [{"e": 1}]})["passed"] is False)

    cmp_bad = reconcile.compare([{"id": 1, "v": "10"}], [{"id": 1, "v": 11}], ["id"], ["v"])   # 真 VM 計數
    per = {k: cmp_bad[k] for k in ("value_mismatch", "missing_in_db", "extra_in_db")}
    r_uns = _summary("T", "by-date", {**base, "per_date": {"2026-08-03": per}}, unsettled={"2026-08-03"})
    r_set = _summary("T", "by-date", {**base, "per_date": {"2026-08-01": per}}, unsettled={"2026-08-03"})
    chk("窗策略保留:未定案日之差異不計 verdict", r_uns["passed"] is True and r_uns["vm"] == 0)
    chk("窗策略保留:定案日之真 VM 擋綠且計數同 compare 真輸出",
        r_set["passed"] is False and r_set["vm"] == cmp_bad["value_mismatch"] > 0)

    cov = {**base, "coverage_ok": True}
    chk("coverage:量級判準 FAIL 擋綠", _summary("N", "coverage", {**cov, "coverage_ok": False})["passed"] is False)
    chk("coverage:量級 OK 且無 gap → 綠", _summary("N", "coverage", cov)["passed"] is True)
    chk("coverage:空視窗仍擋綠(與 verdict 取交集只會更嚴)",
        _summary("N", "coverage", {**gap, "coverage_ok": True})["passed"] is False)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:                 # 免 DB 免 API,須先於 db.connect
        return _selftest()
    only, tables, recent = _parse(argv)
    results = []
    with db.connect() as conn:
        plan = _catalog_tables(conn)
        if not plan:
            _p("⚠️ catalog 無 excluded=f 表(catalog 未建?)→ 無表可對帳")
            return 1
        for dataset, scope, mode in plan:
            if tables and dataset not in tables:
                continue
            if only and scope != only and not (only == "fred" and dataset == FRED_TABLE):
                continue
            r = _audit(conn, dataset, scope, mode, recent)
            results.append(r)
            _print_row(r)
    if not results:
        _p("(無符合條件之表)")
        return 0
    all_pass = all(r["passed"] for r in results)
    _p("=" * 78)
    _p(f"#7 對帳總驗 {len(results)} 表 verdict:"
       f"{'全表 PASS ✅(value_mismatch=0 ∧ extra_in_db=0 ∧ 無未完整 ∧ 無空視窗,無幻像)' if all_pass else '有表 FAIL ❌ — 見上逐表'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
