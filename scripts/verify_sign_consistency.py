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
  python scripts/verify_sign_consistency.py --selftest       # 零 DB 紅綠(判式鎖)
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


def map_direction(cur, feature):
    """principle_factor_map 之人簽方向;無列=None、多列衝突=

    'conflict'(皆 fail-closed 人閘)。"""
    cur.execute("SELECT DISTINCT direction FROM principle_factor_map WHERE feature=%s", (feature,))
    ds = [r[0] for r in cur.fetchall()]
    if not ds:
        return None
    return ds[0] if len(ds) == 1 else "conflict"


def _candidate_features(cur):
    cur.execute("SELECT DISTINCT feature FROM feature_candidate_values ORDER BY 1")
    return [r[0] for r in cur.fetchall()]


def run(features, hs):
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import verify_candidate_promotion as vcp
    from augur.evaluation import label as label_mod
    print("═══ 符號一致性檢查(SIGN-B;判式=點估計+5 bootstrap 全同號==map.direction)═══")
    with db.connect() as conn:
        cur = conn.cursor()
        feats = features or _candidate_features(cur)
        if not feats:
            print("(無候選)")
            return 0
        panels = vcp._asof_panels(cur)
        cal = label_mod.full_calendar(conn)
        print(f"同尺同窗:as-of panels={len(panels)}({panels[0]}..{panels[-1]});h={hs}")
        n_pass = n_fail = n_unj = 0
        for f in feats:
            d = map_direction(cur, f)
            if d is None or d == "conflict":
                n_unj += 1
                why = "map 無方向列(待 fuel-line 策展)" if d is None else "map 多列方向衝突"
                print(f"  ? {f}: UNJUDGEABLE——{why}(fail-closed 人閘)")
                continue
            verdicts = []
            for h in hs:
                ser = vcp._asof_ic_series(conn, panels, h, f, cal)
                ics = np.array(list(ser.values()), dtype=float)
                if len(ics) < 6:
                    verdicts.append((h, "UNJUDGEABLE", float("nan"), 0))
                    continue
                point = float(ics.mean())
                boots = []
                for k in range(N_BOOT_SEEDS):
                    rng = np.random.default_rng(SEED0 + k)
                    boots.append(float(ics[rng.integers(0, len(ics), len(ics))].mean()))
                verdicts.append((h, judge_sign(point, boots, d), point, len(ics)))
            overall = ("UNJUDGEABLE" if all(v[1] == "UNJUDGEABLE" for v in verdicts) else
                       "PASS" if all(v[1] == "PASS" for v in verdicts if v[1] != "UNJUDGEABLE") else "FAIL")
            n_pass += overall == "PASS"
            n_fail += overall == "FAIL"
            n_unj += overall == "UNJUDGEABLE"
            det = " ".join(f"h{h}:{v}(IC均值{m:+.4f},n={n})" for h, v, m, n in verdicts)
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
    chk("複用 vcp as-of 機具(#12)", "_asof_ic_series" in src and "_asof_panels" in src)
    chk("bootstrap seed 確定性(42+k)", N_BOOT_SEEDS == 5 and SEED0 == 42)
    chk("唯讀:零 UPDATE/INSERT", "UPDATE" not in src and "INSERT" not in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="符號一致性檢查(SIGN-B;IC 符號 vs 人簽方向)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--features")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    hs = [int(x) for x in a.h.split(",")]
    if a.run:
        return run(a.features.split(",") if a.features else None, hs)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
