#!/usr/bin/env python
"""符號一致性檢查器 — SUNSET (b)「每一新成員通過符號一致性檢查」之機械尺(SIGN-B-go,hugo 2026-07-28)。

🎯 這支在做什麼(白話):候選特徵入 prodset 前,驗「實現 IC 的符號」與「文獻預期方向
   (principle_factor_map.direction,fuel-line 人簽)」一致——防「數字顯著但方向與原理相反」的
   假訊號入生產。**判式(SIGN-B-go 簽核原文)**:同尺同窗(as-of panel、與提拔漏斗同 h)之
   IC 均值符號 == map.direction,**多 seed 全數同號才過**。
   操作化落註(儀器落地時釘死,#15):rank IC 為確定性統計、無內生 seed——「多 seed」實作為
   **panel 級 block bootstrap**(seed=42+k,k<5,重抽 panel 有放回):點估計與全部 5 個 bootstrap
   均值符號皆 == direction 才 PASS。無 map 方向/多列方向衝突=**UNJUDGEABLE(fail-closed 人閘)**,
   不是 PASS。複用 verify_candidate_promotion 之 as-of panel/IC 機具(#12 不重造)。
守 #8(as-of 同尺)· #9/#10(IC 全出 DB 重算)· #15(不可判誠實)· #12 · #28(本地零 usage)· #29a/d。
判準上位文字=migrate_evolution_v2_ddl.py (b) 條;判式簽核=hugo 2026-07-28「SIGN-B-go(含判式)」。

執行指令矩陣:
  python scripts/verify_sign_consistency.py                  # 無參數:現況(候選×map 方向覆蓋,唯讀)
  python scripts/verify_sign_consistency.py --run            # 全候選判定(--features 可指定;唯讀印報告)
  python scripts/verify_sign_consistency.py --run --features lending_fee_rate_mean_20d
  python scripts/verify_sign_consistency.py --h 20,60        # 同尺同窗之 h(預設 20,60=提拔漏斗口徑)
  python scripts/verify_sign_consistency.py --run --record   # **落帳** feature_sign_check(每 h 一列;append-only)
  python scripts/verify_sign_consistency.py --selftest       # 零 DB 紅綠(判式鎖)

⚠ **--record 前須先建表**:scripts/migrate_feature_sign_check_ddl.py --apply（未建即 rc=2 明說,不靜默）。
⚠ **成本**:每 (feature × h) 需重算一次 as-of IC 序列,會與進行中之 I3／閘評估搶 CPU
   ——放量前先確認 heavy slot 空閒（python -m augur.core.heavy_slot）。
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

N_BOOT_SEEDS = 5
SEED0 = 42


def judge_sign(point_mean, boot_means, direction):
    """判式(SIGN-B-go):sign(點估計)==direction 且全部 bootstrap 均值同號才 PASS。純函式。
    0 均值視為不同號(無方向證據≠方向正確);direction ∈ {+1,-1}。"""
    if direction not in (1, -1):
        return "UNJUDGEABLE"
    vals = [point_mean] + list(boot_means)
    return "PASS" if all(v * direction > 0 for v in vals) else "FAIL"


def map_direction(cur, feature, *, with_source=False):
    """方向來源優先序:①factor_direction_ruling 裁決表(人裁正典,衝突之解)→②map 共識
    (單一方向才用;多列衝突='conflict'、無列=None,皆 fail-closed 人閘)。

    `with_source=True` 回 (direction, source)——供 `feature_sign_check.direction_source` 落帳。
    **刻意做成同一函式之選項而非另寫一支**:優先序若複製兩份會漂（本專案反覆發生之型態）。
    預設回傳型別不變（`run_meta_replay.py:107` 等既有呼叫端不受影響）。
    """
    def _ret(d, src):
        return (d, src) if with_source else d

    cur.execute("SELECT to_regclass('public.factor_direction_ruling')")
    if cur.fetchone()[0] is not None:
        cur.execute("SELECT canonical_direction FROM factor_direction_ruling WHERE feature=%s", (feature,))
        r = cur.fetchone()
        if r:
            return _ret(int(r[0]), "factor_direction_ruling")
    cur.execute("SELECT DISTINCT direction FROM principle_factor_map WHERE feature=%s", (feature,))
    ds = [r[0] for r in cur.fetchall()]
    if not ds:
        return _ret(None, "none")
    return _ret(ds[0] if len(ds) == 1 else "conflict",
                "principle_factor_map" if len(ds) == 1 else "principle_factor_map(conflict)")


def build_sign_rows(feature, direction, source, verdicts, panels, code_sha):
    """把一顆特徵之判定攤成 `feature_sign_check` 之列（每個 h 一列）。**純函式**——自測免 DB。

    `direction` 非 ±1（None／'conflict'）時仍落帳，verdict=UNJUDGEABLE、direction 寫 NULL
    ——**「不可判」必須留痕**，否則查無列與判不出來混為一談（兩者都不是 PASS，但成因不同）。
    """
    import json as _j
    d_db = direction if direction in (1, -1) else None
    pf, pl = (panels[0], panels[-1]) if panels else (None, None)
    return [(feature, h, d_db, source, (None if pt != pt else pt),  # pt!=pt ⇒ NaN
             _j.dumps(bt), n, pf, pl, v, code_sha)
            for h, v, pt, n, bt in verdicts]


def _candidate_features(cur):
    cur.execute("SELECT DISTINCT feature FROM feature_candidate_values ORDER BY 1")
    return [r[0] for r in cur.fetchall()]


def _one(cur, sql, params=()):
    cur.execute(sql, params)
    r = cur.fetchone()
    return r[0] if r else None


def _record_rows(cur, rows):
    """落帳 feature_sign_check（append-only：每次檢查都留一筆，不覆寫歷史）。"""
    cur.executemany(
        "INSERT INTO feature_sign_check (feature,h,direction,direction_source,point_ic,"
        " boot_ics,n_panels,panels_first,panels_last,verdict,code_sha)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)


def run(features, hs, record=False):
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import subprocess
    import verify_candidate_promotion as vcp
    from augur.evaluation import label as label_mod
    print("═══ 符號一致性檢查(SIGN-B;判式=點估計+5 bootstrap 全同號==map.direction)═══")
    if record:
        print("  --record:判定將落帳 feature_sign_check(每個 h 一列)")
    code_sha = None
    if record:
        try:
            code_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                      text=True, timeout=10).stdout.strip()[:40] or None
        except Exception:  # noqa: BLE001  provenance 取不到不該擋住檢查本身
            code_sha = None
    with db.connect() as conn:
        cur = conn.cursor()
        if record and not _one(cur, "SELECT to_regclass('public.feature_sign_check') IS NOT NULL"):
            print("✗ --record 但 feature_sign_check 未建——先跑"
                  " scripts/migrate_feature_sign_check_ddl.py --apply", file=sys.stderr)
            return 2
        feats = features or _candidate_features(cur)
        if not feats:
            print("(無候選)")
            return 0
        panels = vcp._asof_panels(cur)
        cal = label_mod.full_calendar(conn)
        print(f"同尺同窗:as-of panels={len(panels)}({panels[0]}..{panels[-1]});h={hs}")
        n_pass = n_fail = n_unj = 0
        for f in feats:
            d, src = map_direction(cur, f, with_source=True)
            if d is None or d == "conflict":
                n_unj += 1
                why = "map 無方向列(待 fuel-line 策展)" if d is None else "map 多列方向衝突"
                print(f"  ? {f}: UNJUDGEABLE——{why}(fail-closed 人閘)")
                if record:
                    # **不可判也要落帳**:查無列(從未檢)與判不出來(檢了但無方向)是兩件事,
                    # 兩者皆非 PASS,但只有後者能證明「已嘗試」。
                    _record_rows(cur, build_sign_rows(
                        f, d, src, [(h, "UNJUDGEABLE", float("nan"), 0, []) for h in hs],
                        panels, code_sha))
                    conn.commit()
                continue
            verdicts = []
            for h in hs:
                ser = vcp._asof_ic_series(conn, panels, h, f, cal)
                ics = np.array(list(ser.values()), dtype=float)
                if len(ics) < 6:
                    verdicts.append((h, "UNJUDGEABLE", float("nan"), 0, []))
                    continue
                point = float(ics.mean())
                boots = []
                for k in range(N_BOOT_SEEDS):
                    rng = np.random.default_rng(SEED0 + k)
                    boots.append(float(ics[rng.integers(0, len(ics), len(ics))].mean()))
                verdicts.append((h, judge_sign(point, boots, d), point, len(ics), boots))
            if record:
                _record_rows(cur, build_sign_rows(f, d, src, verdicts, panels, code_sha))
                conn.commit()
            overall = ("UNJUDGEABLE" if all(v[1] == "UNJUDGEABLE" for v in verdicts) else
                       "PASS" if all(v[1] == "PASS" for v in verdicts if v[1] != "UNJUDGEABLE") else "FAIL")
            n_pass += overall == "PASS"
            n_fail += overall == "FAIL"
            n_unj += overall == "UNJUDGEABLE"
            det = " ".join(f"h{h}:{v}(IC均值{m:+.4f},n={n})" for h, v, m, n, _b in verdicts)
            icon = {"PASS": "✓", "FAIL": "✗", "UNJUDGEABLE": "?"}[overall]
            print(f"  {icon} {f}: {overall}(map.direction={d:+d}) {det}")
        print(f"\n合計:PASS {n_pass}/FAIL {n_fail}/不可判 {n_unj}"
              f"(不可判=人閘,非通過;全 h 同 PASS 才過=保守,落註)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        feats = _candidate_features(cur)
        print(f"  候選 {len(feats)};map 方向覆蓋:")
        for f in feats:
            d = map_direction(cur, f)
            print(f"    {f:32} → {'無(不可判)' if d is None else d}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("全同號+方向合=PASS", judge_sign(0.02, [0.01, 0.03, 0.02, 0.01, 0.02], 1) == "PASS")
    chk("負向特徵全負+direction=-1=PASS", judge_sign(-0.02, [-0.01, -0.03], -1) == "PASS")
    chk("點估計同向但一 bootstrap 翻號=FAIL(多 seed 全數同號之判式)",
        judge_sign(0.02, [0.01, -0.001, 0.03], 1) == "FAIL")
    chk("方向相反=FAIL", judge_sign(0.02, [0.01, 0.02], -1) == "FAIL")
    chk("零均值=不同號(無證據≠正確)", judge_sign(0.0, [0.01], 1) == "FAIL")
    chk("direction 非 ±1=UNJUDGEABLE", judge_sign(0.02, [0.01], None) == "UNJUDGEABLE")
    import inspect
    src = inspect.getsource(run) + inspect.getsource(map_direction)
    chk("無 map 列/衝突=fail-closed 人閘非 PASS", "UNJUDGEABLE" in src and "conflict" in src)
    chk("裁決表優先於 map 共識(增列式裁決,2026-07-28)", "factor_direction_ruling" in src
        and src.index("factor_direction_ruling") < src.index("principle_factor_map"))
    chk("複用 vcp as-of 機具(#12)", "_asof_ic_series" in src and "_asof_panels" in src)
    chk("bootstrap seed 確定性(42+k)", N_BOOT_SEEDS == 5 and SEED0 == 42)
    # 原斷言為「唯讀:零 UPDATE/INSERT」——加 --record 後**語意上已不成立**（本支會寫）。
    # 改為驗真正該守的：預設唯讀、寫入僅限 feature_sign_check、且永不碰閘／prodset／人簽欄。
    import inspect as _i
    _all = "".join(_i.getsource(f) for f in (run, _record_rows, main))
    chk("預設唯讀（--record 才寫）", "record=False" in _i.getsource(run))
    chk("寫入僅限 feature_sign_check（不碰閘／prodset）",
        "INSERT INTO feature_sign_check" in _i.getsource(_record_rows)
        and not any(t in _all for t in ("promotion_queue", "evolution_production_feature_set",
                                        "evolution_apply_log")))
    chk("無人簽欄（不代打人簽）",
        not any(c in _i.getsource(_record_rows)
                for c in ("approved_by", "promoted_by", "signed_by", "decided_by")))
    # build_sign_rows 為純函式 → 餵真輸入驗真行為（字面斷言會掃到自己那份副本而恆綠）
    _r = build_sign_rows("f1", 1, "principle_factor_map",
                         [(20, "PASS", 0.05, 64, [0.04, 0.06]), (60, "FAIL", -0.01, 64, [-0.02])],
                         ["2020-01-01", "2026-06-30"], "abc123")
    chk("每個 h 各落一列", len(_r) == 2)
    chk("h/verdict/direction 落位正確", _r[0][1] == 20 and _r[0][9] == "PASS" and _r[0][2] == 1)
    chk("panels 起訖隨列落帳（同尺同窗可稽核）", _r[0][7] == "2020-01-01" and _r[0][8] == "2026-06-30")
    _u = build_sign_rows("f2", None, "none", [(20, "UNJUDGEABLE", float("nan"), 0, [])], [], None)
    chk("不可判亦落帳、direction 為 NULL（查無列≠判不出來）",
        len(_u) == 1 and _u[0][2] is None and _u[0][9] == "UNJUDGEABLE")
    chk("NaN 點估計轉 NULL（不寫 NaN 進 DB）", _u[0][4] is None)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="符號一致性檢查(SIGN-B;IC 符號 vs 人簽方向)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--features")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--record", action="store_true",
                    help="把判定落帳 feature_sign_check（每個 h 一列；append-only 不覆寫）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    hs = [int(x) for x in a.h.split(",")]
    if a.run:
        return run(a.features.split(",") if a.features else None, hs, record=a.record)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
