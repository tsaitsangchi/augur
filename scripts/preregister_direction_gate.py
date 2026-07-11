#!/usr/bin/env python
"""方向 GATE 預註冊 CLI — H/D 兩軌判準先凍後跑(oracle 主計畫 §0.4/§2.6/§6.1;憲章 v1.42.0)。

🎯 這支在做什麼(白話):把「怎樣才算過」在跑任何 OOS 數字**之前**寫死——每 (track,horizon) 一列
   direction_gate:GATE=三關同過((i) hit-rate 顯著優於同窗**多數類基線** max(p̄,1−p̄),HAC/date-cluster
   口徑禁 iid;(ii) Brier < p̄(1−p̄);(iii) ECE ≤ judgestop `calib_late_ece_ceiling`(DB 讀值 #12)+分位桶
   單調)。經濟終關=獨立標示軸不在 GATE 內。H120 非重疊 n=35 → **review 級寫死**(過了最高只得觀察
   名單)。**approve 唯決策層人**(TTY 閘;AI/腳本 fail-closed)。挪門柱=direction_gate trigger 機械拒。

守 #15(先凍後跑;敗退路徑寫死)· #26(approve 唯人)· #12(ECE 門檻 DB 讀值)· #29a。

執行指令矩陣:
  python scripts/preregister_direction_gate.py                    # 無參數:gate 清單(唯讀)
  python scripts/preregister_direction_gate.py --preregister-all  # H{20,40,82,120}+D{1,5} 六列 draft
  python scripts/preregister_direction_gate.py --approve dgate_H_82 --approved-by hugo   # 人親核(TTY)
  python scripts/preregister_direction_gate.py --check dgate_H_82 # sha 覆算+trigger 斷言
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

H_HORIZONS = (20, 40, 82, 120)
D_KS = (1, 5)


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _sha(c):
    return hashlib.sha256(json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()[:16]


def _criteria(track, h, ece_ceiling):
    c = {
        "gate_rules": {
            "i_hitrate": "hit-rate 顯著優於同窗多數類樸素基線 max(p_bar, 1-p_bar);顯著性=date-cluster/HAC Eff-t p<0.05(合併口徑,禁 iid)",
            "ii_brier": "OOS Brier < 基線 p_bar*(1-p_bar)(同窗實算)",
            "iii_calibration": {"ece_ceiling": ece_ceiling, "ece_source": "judgestop_threshold.calib_late_ece_ceiling(DB 讀值)",
                                "quantile_monotone": "p_up 十分位 vs 實現上漲頻率單調(Spearman>0)"},
        },
        "base_rate_rule": "多數類基線與 p_bar 一律同窗實算入 result_snapshot,不預先編數(H82 個股 up-rate=增訓時實算)",
        "scoring": "horizon 級聚合;禁單股準確率;abstain 無(方向機率必出);FREEZE 內=歷史 walk-forward OOS 非 live",
        "econ_axis": "經濟終關(run_economic_eval 同口徑 cost 0.00585)=獨立標示軸,不在 GATE 內;展示分級閉集依憲章 v1.42.0",
        "fail_path": "任一關不過=evaluated_fail 判死留檔、永不出 UI;重試=另立新 gate(舊列 superseded)",
    }
    if track == "H":
        c["horizon_td"] = h
        c["nonoverlap_n"] = {20: 213, 40: 106, 82: 52, 120: 35}[h]
        if h == 120:
            c["review_tier_cap"] = "n=35 review 級寫死:即便三關全過,最高只得「證據不足、觀察名單」,不得完整展示"
        if h == 82:
            c["note"] = "P2-1 A 案主錨(120 日曆天≈H82);個股 base-rate 增訓後實算"
    else:
        c["k_td"] = h
        c["expected_econ"] = "dead(來回 0.585% vs 日中位振幅;k=5 損益兩平≈66.5% 命中——預期內誠實死亡)"
    return c


def preregister_all():
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT threshold FROM judgestop_threshold WHERE policy_key='calib_late_ece_ceiling' AND frozen")
        row = cur.fetchone()
        if not row:
            sys.exit("✗ judgestop calib_late_ece_ceiling frozen 列缺(ECE 門檻 DB 讀值前置)")
        ece = float(row[0])
        n = 0
        for track, hs in (("H", H_HORIZONS), ("D", D_KS)):
            for h in hs:
                gid = f"dgate_{track}_{h}"
                c = _criteria(track, h, ece)
                cur.execute("""INSERT INTO direction_gate (gate_id, track, horizon, purpose, criteria, criteria_sha, git_sha, note)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (gate_id) DO NOTHING""",
                    (gid, track, h, f"{track} 軌 h={h} 可證偽賭注(oracle 主計畫 §0.4)",
                     json.dumps(c, ensure_ascii=False), _sha(c), git7,
                     "判準值=計畫建議;approve=二次親核點(人 TTY)"))
                n += cur.rowcount
        conn.commit()
    print(f"✓ 預註冊 {n} 列 draft(H×4+D×2;判準先凍後跑)")
    print("  親核指令(逐列或全批):python scripts/preregister_direction_gate.py --approve dgate_H_20 --approved-by <你>")
    return 0


def approve(gate_id, by):
    if not sys.stdin.isatty():
        sys.exit("✗ approve 唯決策層人(TTY 閘;AI/腳本 fail-closed 拒——憲章 v1.42.0)")
    if not by:
        sys.exit("✗ 需 --approved-by")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE direction_gate SET status='approved', approved_by=%s, approved_at=now() "
                    "WHERE gate_id=%s AND status='preregistered' RETURNING track, horizon", (by, gate_id))
        row = cur.fetchone()
        if not row:
            sys.exit(f"✗ {gate_id} 不存在或非 preregistered")
        conn.commit()
    print(f"✓ {gate_id}(track={row[0]} h={row[1]})已核准 by {by}——criteria 自此不可變(trigger),可跑 evaluate")
    return 0


def check(gate_id):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT criteria, criteria_sha, status, approved_by FROM direction_gate WHERE gate_id=%s", (gate_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ {gate_id} 不存在"); return 1
        resha = _sha(row[0])
        ok = resha == row[1]
        print(f"{gate_id}: status={row[2]} approved_by={row[3]} sha {'✓一致' if ok else '✗ 挪門柱!'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--preregister-all", action="store_true", dest="pre")
    ap.add_argument("--approve")
    ap.add_argument("--approved-by", dest="by")
    ap.add_argument("--check")
    args = ap.parse_args()
    if args.pre:
        return preregister_all()
    if args.approve:
        return approve(args.approve, args.by)
    if args.check:
        return check(args.check)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT gate_id, track, horizon, status, approved_by FROM direction_gate ORDER BY track, horizon")
        for r in cur.fetchall():
            print(f"  {r[0]:<14} track={r[1]} h={r[2]:<4} {r[3]:<14} by={r[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
