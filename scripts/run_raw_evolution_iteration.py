#!/usr/bin/env python
"""RAWEVO 迭代 driver — R0 開輪→R1 覆蓋快照→R2 缺口四分類→R3 交互假說候選→結輪(全程庫內唯讀)。
🎯 這支在做什麼(白話):RAWEVO=三軸自進化的資料地基層(v2 §3;RAWEVO 計畫 §4)。每輪讓「我們對 raw 的
   理解」變好一格:對 dataset_catalog 全表拍**覆蓋快照**(est_rows/日期範圍/新鮮度/對帳基線態)、
   把缺口機械分**四類**(true_gap 真缺/freeze_gap 凍結致缺/schema_gap/semantic_ok 語意上非缺)、
   從 field_correlation 提**交互假說候選**(pending hint,人閘 H3 分流——approve 唯 hugo)。
   **鐵律**:全程唯讀 raw(零 FinMind/FRED,FZ-keep)、不補洞、不 APPLY、零寫 feature_values/prodset/
   promotion_queue(I2;selftest 結構斷言);hint 之 direction **留白**=誠實(符號由 TWEVO 閘驗,
   volume_gini_60d 符號盲教訓——RAW 不預設方向)。差分=hint 層級(provenance 快照 corr/n_obs,邊1 處置)。
守 #8(唯讀不看未來)· #9/#10(快照全出自 DB query 可溯)· #15(分類=機械近似,語意細分留人閘,不冒充定論)
   · #26(執行層自主;人閘=H3)· #29a/d。SSOT=v2 §3.2 邊1/邊2、RAWEVO 計畫 §4。
執行指令矩陣:
  python scripts/run_raw_evolution_iteration.py                 # 無參數:現況(唯讀:近輪/快照/hint 統計)
  python scripts/run_raw_evolution_iteration.py --run           # 完整一輪:open→R1→R2→R3→close
  python scripts/run_raw_evolution_iteration.py --run --dry-run # 只算不寫(印將產出之摘要)
  python scripts/run_raw_evolution_iteration.py --run --top-hints 15
  python scripts/run_raw_evolution_iteration.py --selftest      # 零 DB 紅綠(分類邏輯/零寫入斷言)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TRIGGER_CODE = "RAWEVO-S1-go"     # hugo 2026-07-26「排行程一直往下做」概括授權(登錄=audits/V2-ADOPTED-SUNSET);開輪碼非人名
FREEZE_LONG_STALE = dt.date(2026, 6, 1)   # max_date 早於此=長期停更(真缺候選);晚於此=凍結窗可解釋
FREQ_TOL_DAYS = {"daily": 7, "weekly": 14, "monthly": 45, "quarterly": 130, "yearly": 400}
MIN_HINT_NOBS = 300               # hint 候選之最低樣本股數(反覆=真結構,承 #15)
# R3 v2(2026-07-26 首批自首後修):|corr| 降冪撈出的是**定義恆等式**(margin_usage 由 balance 算出、
# market_value=close×股數、money=volume×價、foreign_room=上限-holding、price_to_10yr 分子即 close)
# ——套套邏輯永遠贏過真結構。改:①中頻帶(真假說住這裡)②同字首家族排除③已知衍生鏈排除(邏輯非策展資料,住 code 合憲)。
HINT_ABS_BAND = (0.25, 0.85)      # 恆等式>0.9、雜訊<0.25;真交互結構多住中頻帶
DERIVED_FAMILIES = (              # 同鏈=定義相依,相關無假說價值;新增衍生鏈時來此補
    # r03 擴充(第二批自檢):per/pbr/dividend_yield 皆為價格比值(分子或分母=價),與價/市值共動是機械的
    {"close", "market_value", "price_to_10yr", "money", "open", "high", "low", "spread",
     "per", "pbr", "dividend_yield"},
    {"volume", "money", "turnover"},
    {"margin_balance", "margin_usage", "margin_limit"},
    {"foreign_holding", "foreign_room", "foreign_limit"},
)


def _same_family(fa, fb):
    """定義相依判定:同衍生鏈、或同字首 token(margin_/foreign_ 型)。"""
    if any(fa in fam and fb in fam for fam in DERIVED_FAMILIES):
        return True
    return fa.split("_")[0] == fb.split("_")[0]
STMT_TIMEOUT_MS = 30000           # 逐表 min/max(date) 逾時上限(誠實記 NULL 不硬等)


def classify_gap(freq, has_table, has_date, staleness, max_date):
    """缺口四分類(機械近似第一版;語意細分留 R4 人閘,#15 不冒充定論)。"""
    if not has_table:
        return "schema_gap"
    if freq in FREQ_TOL_DAYS:
        if not has_date:
            return "schema_gap"
        if staleness is None:
            return "schema_gap"
        if staleness <= FREQ_TOL_DAYS[freq]:
            return "ok"
        if max_date is not None and max_date < FREEZE_LONG_STALE:
            return "true_gap"          # 凍結(07-24 起)之前早已停更=真缺/來源停供候選
        return "freeze_gap"            # 凍結窗可解釋之陳舊(白名單日更外之表)
    return "semantic_ok"               # snapshot/single-series 等:陳舊判準不適用


def _uid(cur):
    today = dt.date.today().strftime("%Y%m%d")
    cur.execute("SELECT count(*) FROM raw_evolution_iteration_ledger WHERE iteration_uid LIKE %s",
                (f"raw-{today}-%",))
    return f"raw-{today}-r{cur.fetchone()[0] + 1:02d}"


def r1_coverage(cur, uid, write):
    """R1:逐 dataset_catalog 列拍覆蓋快照。回 (n_rows, gap_counter)。"""
    cur.execute("SELECT id, passed FROM attestation_result ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    attest_ref, attest_passed = (row if row else (None, None))
    cur.execute("SELECT dataset, frequency, excluded, coalesce(excluded_reason,'') FROM dataset_catalog ORDER BY dataset")
    cats = cur.fetchall()
    today = dt.date.today()
    n, gaps = 0, {}
    for ds, freq, excluded, exc_reason in cats:
        cur.execute("SELECT to_regclass('public.'||quote_ident(%s))", (ds,))
        has_table = cur.fetchone()[0] is not None
        est = mn = mx = staleness = None
        has_date = False
        if has_table:
            cur.execute("SELECT reltuples::bigint FROM pg_class WHERE relname=%s", (ds,))
            r = cur.fetchone()
            est = r[0] if r else None
            cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name='date'", (ds,))
            has_date = cur.fetchone() is not None
            if has_date:
                cur.execute("SAVEPOINT tbl_probe")       # 單表失敗不廢全交易(逾時/型別非 date)
                try:
                    cur.execute(f"SET LOCAL statement_timeout = {STMT_TIMEOUT_MS}")
                    cur.execute(f'SELECT min(date), max(date) FROM "{ds}"')  # noqa: S608 表名出自 catalog
                    mn, mx = cur.fetchone()
                    if mx and isinstance(mx, dt.date):
                        staleness = (today - mx).days
                    else:
                        mn = mx = None                   # date 欄非日期型(如 TEXT):誠實記 NULL
                    cur.execute("RELEASE SAVEPOINT tbl_probe")
                except Exception:  # noqa: BLE001  逾時/型別:誠實記 NULL、交易回捲到 savepoint
                    cur.execute("ROLLBACK TO SAVEPOINT tbl_probe")
                    mn = mx = staleness = None
                cur.execute(f"SET LOCAL statement_timeout = 0")  # noqa: F541
        gc = classify_gap(freq, has_table, has_date, staleness, mx)
        gaps[gc] = gaps.get(gc, 0) + 1
        if write:
            cur.execute("""INSERT INTO raw_table_coverage_snapshot
                (iteration_uid, dataset, est_rows, min_date, max_date, date_semantics, staleness_days,
                 freq_class, catalog_registered, last_attest_ref, last_attest_passed, gap_class, detail)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,true,%s,%s,%s,%s)
                ON CONFLICT (iteration_uid, dataset) DO NOTHING""",
                (uid, ds, est, mn, mx,
                 "observation" if has_date else ("no_date" if has_table else None),
                 staleness, freq, attest_ref, attest_passed, gc,
                 json.dumps({"excluded": bool(excluded), "excluded_reason": exc_reason[:120],
                             "note": "est_rows=pg_class.reltuples(估計);attest=全域 run 級(非逐表)"},
                            ensure_ascii=False)))
        n += 1
    return n, gaps


def r3_hints(cur, uid, top, write):
    """R3:field_correlation 強結構對 → pending hint(direction 留白;dedup_key 防重;差分=provenance 快照)。"""
    lo, hi = HINT_ABS_BAND
    cur.execute("""SELECT field_a, field_b, basis, count(*) AS n_stock,
                round(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)::numeric, 3) AS med
        FROM field_correlation WHERE corr IS NOT NULL AND field_a < field_b
        GROUP BY field_a, field_b, basis HAVING count(*) >= %s
           AND abs(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)) BETWEEN %s AND %s
        ORDER BY abs(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)) DESC LIMIT %s""",
        (MIN_HINT_NOBS, lo, hi, top * 6))
    made, ids = 0, []
    for fa, fb, basis, nst, med in cur.fetchall():
        if made >= top:
            break
        if _same_family(fa, fb):
            continue                                   # 定義相依=零假說價值,靜默跳過(計數見 detail)
        dedup = f"raw:fieldcorr:{fa}x{fb}:{basis}"
        cur.execute("SELECT 1 FROM evolution_hypothesis_hint WHERE dedup_key=%s", (dedup,))
        if cur.fetchone():
            continue
        hid = "raw-h-" + hashlib.sha256(dedup.encode()).hexdigest()[:8]
        if write:
            cur.execute("""INSERT INTO evolution_hypothesis_hint
                (hint_id, from_axis, from_iteration_uid, hint_text, suggested_map, provenance, dedup_key)
                VALUES (%s,'raw',%s,%s,%s,%s,%s) ON CONFLICT (dedup_key) DO NOTHING""",
                (hid, uid,
                 f"raw 欄位 {fa}×{fb} 之 {basis} 相關跨股中位 {med}(n={nst})——候選交互結構,"
                 f"是否入 map 由人閘分流(H3);direction 留白=RAW 不預設方向(符號由 TWEVO 閘驗)",
                 json.dumps({"principle_hint": None, "feature_hint": f"{fa}_x_{fb}_{basis}",
                             "direction": None}, ensure_ascii=False),
                 json.dumps({"kind": "field_correlation", "refs": [f"field_correlation:{fa}|{fb}|{basis}"],
                             "n_obs": int(nst), "median_corr": float(med),
                             "snapshot_at": dt.date.today().isoformat()}, ensure_ascii=False),
                 dedup))
        made += 1
        ids.append(hid)
    return made, ids


def _kill_state(cur) -> str:
    """本軸之有效 kill 狀態（raw ∨ global；OR 語意 fail-safe）。

    口徑與判準單一住所＝`augur.philosophy.evolution.effective_kill_state`（#12）。
    2026-07-31 補：本 driver 原**對 kill_switch 零引用**——按下停機鈕後 raw 仍會開輪、
    仍寫帳本，即「停機」實為「照跑」。tw driver 同缺（另案，須待其收工後補）。
    """
    from augur.philosophy.evolution import effective_kill_state
    cur.execute("SELECT state FROM evolution_kill_switch WHERE scope IN ('raw','global')")
    return effective_kill_state([r[0] for r in cur.fetchall()],
                                env_halt=os.environ.get(
                                    "AUGUR_EVOLUTION_KILL_SWITCH", "").strip().lower() == "halt")


def run(top_hints, dry):
    with db.connect() as conn:
        cur = conn.cursor()
        if _kill_state(cur) == "halt":
            # fail-closed：不開輪、不寫帳本、非 0 退出（供 cron log 與 OnFailure 可見）。
            print("⛔ RAWEVO kill switch=halt(scope raw 或 global)——不開輪。"
                  "解除：UPDATE evolution_kill_switch SET state='clear' WHERE scope IN ('raw','global');")
            return 75
        uid = _uid(cur)
        print(f"── RAWEVO 開輪 {uid}(trigger={TRIGGER_CODE};dry={dry}) ──")
        if not dry:
            cur.execute("""INSERT INTO raw_evolution_iteration_ledger
                (iteration_uid, axis, status, trigger_code, tier, steps_json)
                VALUES (%s,'raw','running',%s,'P1','[]'::jsonb)""", (uid, TRIGGER_CODE))
            conn.commit()
        n, gaps = r1_coverage(cur, uid, write=not dry)
        print(f"  R1 覆蓋快照:{n} 表|分類 {gaps}")
        made, ids = r3_hints(cur, uid, top_hints, write=not dry)
        print(f"  R3 假說候選:新 hint {made} 則(pending;人閘 H3 分流,approve 唯 hugo)")
        if dry:
            print("(dry-run:未寫入)"); return 0
        steps = [{"step": "R1_coverage", "rc": 0, "n_rows": n, "gap_counter": gaps},
                 {"step": "R3_hints", "rc": 0, "n_new_hints": made, "hint_ids": ids}]
        gain = bool(made or gaps.get("true_gap") or gaps.get("freeze_gap"))
        cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2b)
        cur.execute("""UPDATE raw_evolution_iteration_ledger
            SET status='succeeded', closed_at=now(), closed_by='run_raw_evolution_iteration(執行層)',
                steps_json=%s, gain=%s, gain_basis=%s,
                gain_evidence=%s, gap_summary_json=%s, hints_out=%s
            WHERE iteration_uid=%s""",
            (json.dumps(steps, ensure_ascii=False), gain, "new_gap" if gain else "none",
             json.dumps({"suite_id": "rawevo_r1r3_v1", "n_snapshot": n, "n_hints": made},
                        ensure_ascii=False),
             json.dumps(gaps, ensure_ascii=False), json.dumps(ids, ensure_ascii=False), uid))
        conn.commit()
        print(f"✓ 結輪 {uid}:gain={gain}(basis={'new_gap' if gain else 'none'})")
        if made:
            print("  人閘 H3——hugo 檢視後親跑(逐 id 或整批;B4-P2a 後 UPDATE 須帶誠實閘通行證):")
            print("    SELECT hint_id, hint_text FROM evolution_hypothesis_hint WHERE decision='pending';")
            print("    BEGIN; SET LOCAL augur.honesty_write='on';  -- B4-P2a 通行證(裸 UPDATE 遭閘拒)")
            print("    UPDATE evolution_hypothesis_hint SET decision='approved', decided_by='hugo',"
                  " decided_at=now(), decision_code='RAWEVO-HINT-approve <ids>' WHERE hint_id IN ('…'); COMMIT;")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT iteration_uid, status, gain, gain_basis, opened_at::date
            FROM raw_evolution_iteration_ledger ORDER BY iteration_id DESC LIMIT 5""")
        rows = cur.fetchall()
        print("近輪:" if rows else "近輪:(無;--run 開首輪)")
        for r in rows:
            print(f"  {r[0]} {r[1]} gain={r[2]}({r[3]}) @{r[4]}")
        cur.execute("SELECT count(*), count(DISTINCT iteration_uid) FROM raw_table_coverage_snapshot")
        n, it = cur.fetchone()
        print(f"覆蓋快照:{n} 列/{it} 輪")
        cur.execute("SELECT decision, count(*) FROM evolution_hypothesis_hint WHERE from_axis='raw' GROUP BY 1")
        for d, c in cur.fetchall():
            print(f"hint[{d}]: {c}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # kill switch（2026-07-31 補；本 driver 原對其零引用＝「停機」實為「照跑」）。
    # 判準本體在 augur.philosophy.evolution（單一住所 #12），此處驗真行為＋接線。
    from augur.philosophy.evolution import effective_kill_state as _eks
    chk("kill:任一 scope halt ⇒ halt(OR 語意 fail-safe)", _eks(["clear", "halt"]) == "halt")
    chk("kill:全 clear ⇒ clear", _eks(["clear", "clear"]) == "clear")
    chk("kill:env AUGUR_EVOLUTION_KILL_SWITCH=halt 可強制", _eks(["clear"], env_halt=True) == "halt")
    _src = open(__file__, encoding="utf-8").read()
    chk("run() 開輪前檢 kill(接線存在,非只有函式)",
        "if _kill_state(cur) == \"halt\"" in _src)
    chk("halt 時 fail-closed:不開輪、不寫帳本、rc≠0", "return 75" in _src)
    chk("kill 查詢含 global scope(不只自軸)", "scope IN ('raw','global')" in _src)

    chk("分類:新鮮 daily=ok", classify_gap("daily", True, True, 3, dt.date(2026, 7, 24)) == "ok")
    chk("分類:長期停更=true_gap(ExchangeRate 型)",
        classify_gap("daily", True, True, 2081, dt.date(2020, 11, 13)) == "true_gap")
    chk("分類:凍結窗內陳舊=freeze_gap(不誣賴來源)",
        classify_gap("daily", True, True, 20, dt.date(2026, 7, 6)) == "freeze_gap")
    chk("分類:無實表=schema_gap", classify_gap("daily", False, False, None, None) == "schema_gap")
    chk("分類:daily 卻無 date 欄=schema_gap", classify_gap("daily", True, False, None, None) == "schema_gap")
    chk("分類:snapshot/single-series=semantic_ok(陳舊判準不適用)",
        classify_gap("single-series", True, True, 999, dt.date(2020, 1, 1)) == "semantic_ok")
    # R3 v2:恆等式排除(首批 10 則自首教訓)
    chk("家族排除:margin_balance×margin_usage(定義相依)", _same_family("margin_balance", "margin_usage"))
    chk("家族排除:close×market_value(市值=價×股數)", _same_family("close", "market_value"))
    chk("家族排除:money×volume(金額=量×價)", _same_family("money", "volume"))
    chk("家族排除:foreign_holding×foreign_room(room=限-持)", _same_family("foreign_holding", "foreign_room"))
    chk("跨家族不誤殺:margin_balance×inst_net", not _same_family("margin_balance", "inst_net"))
    chk("頻帶排除恆等式:band 上限<0.9", HINT_ABS_BAND[1] < 0.9)
    src = open(__file__, encoding="utf-8").read()
    # 斷言只掃「程式體」:去模組 docstring 與 selftest 段——斷言字串/說明文自含目標字面=自匹配假紅
    # (2026-07-26 當日第五次同型教訓:pgrep×3、eval compare、本處)
    body = src.split("def _selftest")[0].split('"""', 2)[-1]
    chk("**零寫入 panel(I2 結構斷言)**:程式體無 INSERT/UPDATE 至 feature_values/prodset/promotion_queue",
        not any(f"INTO {t}" in body or f"UPDATE {t}" in body
                for t in ("feature_values", "evolution_production_feature_set", "promotion_queue")))
    chk("零 FinMind/FRED(FZ-keep)", "finmind" not in body.lower() and "fred_api" not in body.lower())
    chk("hint direction 留白(符號盲教訓)", '"direction": None' in body)
    chk("hint 帶 n_obs+快照 provenance(邊1 差分)", '"n_obs"' in body and '"snapshot_at"' in body)
    chk("人閘指令印出而非代打(H3)", "decided_by='hugo'" in body and "hugo 檢視後親跑" in body)
    chk("trigger_code=拍板碼非人名", "RAWEVO-S1-go" in TRIGGER_CODE)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="RAWEVO 迭代 driver(R0-R3;全程庫內唯讀)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--top-hints", type=int, default=10)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.run:
        return run(a.top_hints, a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
