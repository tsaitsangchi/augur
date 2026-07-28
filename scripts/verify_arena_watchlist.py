#!/usr/bin/env python
"""arena 觀察名單凍結檢定 — W1/W2 日內排列檢定之常設儀器(只驗不改;判準引用預註冊檔)。

🎯 這支在做什麼(白話):audits/ARENA-WATCHLIST-PREREG-20260726.md 凍結了兩筆觀察假設
   (W1 momentum_20 正排序/W2 own_daily_rolling 反排序紅旗)與檢定口徑——本支把該口徑**逐字**落成
   常設程式:同隊同 pred_date 日內將 p_up 於股票間隨機重排(n_perm=4,000、seed=當批結算日 YYYYMMDD、
   統計量=pooled Brier)、Bonferroni m=8、批次=不重疊標籤窗(前一計入批之窗零交易日重疊才另立)。
   **狀態無表、全程重算**(stateless:判準計數由全批重算導出,零新表、確定性可複現)。
   樣本排除 settle_mode='unsettleable';觀察級鐵則不動——本支輸出永遠掛「觀察級」字樣。
守 #15(只驗不改、判準凍結不挪)· #9/#10(統計全出 DB 結算列+排列重算)· #12(排除口徑同 settle)· #29a/d。
判準 SSOT=audits/ARENA-WATCHLIST-PREREG-20260726.md(本支僅執行、不覆述判準全文)。

執行指令矩陣:
  python scripts/verify_arena_watchlist.py             # 無參數:現況(可判批次數/各假設計數,唯讀)
  python scripts/verify_arena_watchlist.py --run       # 全批重算+W1/W2 現況判定(唯讀,印報告)
  python scripts/verify_arena_watchlist.py --selftest  # 零 DB 紅綠(批次切分/排列確定性/計數規則)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np
from augur.core import db

PREREG = "audits/ARENA-WATCHLIST-PREREG-20260726.md"   # 凍結判準檔(輸出必印,名單明文要求)
N_PERM = 4000
ALPHA_BONF = 0.05 / 8      # Bonferroni m=8(凍結)
W1_TEAM, W2_TEAM = "momentum_20", "own_daily_rolling"


def segment_batches(rows):
    """凍結定義:批=不重疊標籤窗——pred_date ≤ 前一計入批窗尾(max label_due)即併入該批,
    嚴格大於才另立新批。rows=[(pred_date, label_due)] 已升冪去重。純函式。"""
    batches = []
    for pd_, due in rows:
        if batches and pd_ <= batches[-1]["end"]:
            batches[-1]["dates"].append(pd_)
            batches[-1]["end"] = max(batches[-1]["end"], due)
        else:
            batches.append({"dates": [pd_], "end": due})
    return batches


def perm_percentile(day_groups, seed):
    """日內排列檢定(凍結口徑):每 pred_date 內重排 p_up、pooled Brier、回觀測值百分位與單尾 p(低端)。
    day_groups=[(p_up array, y array)];確定性=同 seed 同結果。純函式(吃 numpy)。"""
    rng = np.random.default_rng(seed)
    obs = np.concatenate([(p - y) ** 2 for p, y in day_groups]).mean()
    perms = np.empty(N_PERM)
    for i in range(N_PERM):
        tot, n = 0.0, 0
        for p, y in day_groups:
            q = rng.permutation(p)
            tot += ((q - y) ** 2).sum()
            n += len(p)
        perms[i] = tot / n
    p_low = float((perms <= obs).mean())          # W1:排序有正資訊 → 觀測 Brier 落低端
    pct = float((perms < obs).mean() * 100)
    return {"obs_brier": float(obs), "percentile": pct, "p_low": p_low}


def _load(cur):
    cur.execute("""SELECT model_key, pred_date, label_due_est, p_up, y_up
        FROM direction_arena_prediction
        WHERE settled_at IS NOT NULL AND settle_mode <> 'unsettleable'
          AND y_up IS NOT NULL AND model_key IN (%s, %s)
        ORDER BY pred_date""", (W1_TEAM, W2_TEAM))
    return cur.fetchall()


def run():
    print(f"═══ arena 觀察名單凍結檢定(觀察級;判準凍結於 {PREREG},只驗不改)═══")
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = _load(cur)
        cur.execute("""SELECT pred_date, max(settled_at::date) FROM direction_arena_prediction
            WHERE settled_at IS NOT NULL GROUP BY pred_date""")
        settle_day = dict(cur.fetchall())
    if not rows:
        print("(無已結算可判列)")
        return 0
    dates = sorted({(r[1], r[2]) for r in rows})
    batches = segment_batches(dates)
    w1_hits = w1_contra = w2_probe = w2_contra = 0
    for bi, b in enumerate(batches, 1):
        # seed=「當批結算日」;跨日結算時取**首度結算日(min)**——解釋於 2026-07-28 儀器落地時釘死
        # (當下僅首批存在、新批未生=預先落註非挪門柱;首批帳本 settled_at 全=07-27,預註冊例示
        #  seed=20260726 為覆盤當日、與帳本不符,以帳本為準 #15)
        seed = int(min(settle_day[d] for d in b["dates"]).strftime("%Y%m%d"))
        print(f"\n批 {bi}:pred_dates={[str(d) for d in b['dates']]}(窗尾 {b['end']};seed={seed})")
        for team in (W1_TEAM, W2_TEAM):
            groups = []
            for d in b["dates"]:
                sub = [(float(p), int(y)) for mk, pd_, _, p, y in rows if mk == team and pd_ == d]
                if sub:
                    arr = np.array(sub)
                    groups.append((arr[:, 0], arr[:, 1]))
            if not groups:
                print(f"  {team}: 本批無列(跳過)")
                continue
            r = perm_percentile(groups, seed)
            print(f"  {team}: pooled Brier={r['obs_brier']:.4f} 百分位={r['percentile']:.1f} "
                  f"p_low={r['p_low']:.4f}(α_Bonf={ALPHA_BONF:.5f})")
            if team == W1_TEAM:
                w1_hits = w1_hits + 1 if r["p_low"] < ALPHA_BONF else 0   # 「連續」:不中即歸零
                w1_contra += (r["p_low"] > 0.5)
            else:
                w2_probe += (r["percentile"] > 95)
                w2_contra += (r["percentile"] < 80)
    print(f"\n── 現況判定(規則全文見 {PREREG}) ──")
    print(f"  W1:連續達標批 {w1_hits}/3(升「觀察級成立」門檻);反證累計 {w1_contra}/2(撤名單門檻)")
    print(f"  W2:紅旗維持批(>95 百分位)累計 {w2_probe};反證(<80)累計 {w2_contra}/2(撤旗門檻)")
    print(f"  可判批次:{len(batches)}(首批=預註冊已計;新批須新標籤窗結算才出現)")
    print("  ⚠ 觀察級鐵則:一切結果皆觀察級;確立級唯經 direction_gate(≥60 clusters)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = _load(cur)
    dates = sorted({(r[1], r[2]) for r in rows})
    b = segment_batches(dates)
    print(f"  已結算可判 pred_date:{len(dates)};不重疊批次:{len(b)};判準檔:{PREREG}")
    return 0


def _selftest():
    from datetime import date
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    d = date
    # 首批凍結事實:07-15/16 窗重疊 → 併 1 批;窗後新日 → 另立
    b = segment_batches([(d(2026, 7, 15), d(2026, 7, 22)), (d(2026, 7, 16), d(2026, 7, 23)),
                         (d(2026, 7, 25), d(2026, 8, 1))])
    chk("批次切分:重疊窗併批(首批 07-15/16=1 批)", len(b) == 2 and len(b[0]["dates"]) == 2)
    chk("批次切分:窗尾取 max", b[0]["end"] == d(2026, 7, 23))
    chk("批次切分:pred_date>前批窗尾才另立", b[1]["dates"] == [d(2026, 7, 25)])
    p = np.array([0.9, 0.7, 0.5, 0.3, 0.1]); y = np.array([1, 1, 0, 0, 0])
    r1 = perm_percentile([(p, y)], 20260726)
    r2 = perm_percentile([(p, y)], 20260726)
    chk("排列確定性:同 seed 同結果", r1 == r2)
    chk("完美排序落低端百分位", r1["percentile"] < 10)
    r3 = perm_percentile([(p[::-1].copy(), y)], 20260726)
    chk("反向排序落高端百分位(W2 紅旗方向)", r3["percentile"] > 90)
    chk("Bonferroni m=8 凍結", abs(ALPHA_BONF - 0.00625) < 1e-12)
    chk("n_perm=4000 凍結", N_PERM == 4000)
    import inspect
    src = inspect.getsource(run) + inspect.getsource(_load)
    chk("排除 unsettleable(口徑同 settle)", "unsettleable" in src)
    chk("只驗不改:全支零 UPDATE/INSERT", all(k not in src for k in ("UPDATE", "INSERT")))
    chk("輸出引用預註冊檔(名單明文要求)", "PREREG" in inspect.getsource(run) and "WATCHLIST-PREREG" in PREREG)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="arena 觀察名單凍結檢定(只驗不改)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.run:
        return run()
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
