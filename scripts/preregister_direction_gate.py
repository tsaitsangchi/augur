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
  python scripts/preregister_direction_gate.py --preregister-v2   # v2 四門(K=4;estimand/α/窗/fail_path 凍結)
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


V2_GATES = ("dgate_D_5_v2", "dgate_H_40_v2", "dgate_H_20_v2", "dgate_H_82_v2")


def _criteria_v2(key, ece):
    """v2 四門判準(revival plan §0.4/§3.7):estimand 機械欄+α 分級+家族句+fail_path(no-v3)+provenance
    全入 criteria 隨 sha 凍結——evaluate 依此取樣與判定,零事後自由度。"""
    c = {
        "version": "v2",
        "gate_rules": {
            "i_hitrate": ("hit-rate 顯著優於同窗『全局多數類固定方向』基線 max(p_bar,1-p_bar)(同窗實算;"
                          "禁逐 panel 實現值〔千里眼〕基線——v1 H 軌程序教訓);顯著性=逐 panel (hit−naive) "
                          "序列 HAC Eff-t 單尾 p<alpha(禁 iid;lag 見 hac_min_lag)"),
            "ii_brier": "OOS Brier < 基線 p_bar*(1-p_bar)(同窗實算)",
            "iii_calibration": {"ece_ceiling": ece, "ece_source": "judgestop_threshold.calib_late_ece_ceiling(DB 讀值)",
                                "quantile_monotone": "p_up 十分位 vs 實現上漲頻率單調(Spearman>0)"},
        },
        "base_rate_rule": "多數類基線與 p_bar 一律同窗實算入 result_snapshot,不預先編數",
        "scoring": "horizon 級聚合;禁單股準確率;abstain 無(方向機率必出);FREEZE 內=歷史 walk-forward OOS 非 live",
        "econ_axis": "經濟終關(cost 0.00585 同口徑)=獨立標示軸不在 GATE 內;展示分級閉集依憲章 v1.42.0",
        "fail_path": ("任一關不過=evaluated_fail 判死留檔、永不出 UI;"
                      "v2 家族全 fail=方向軸凍結至 FREEZE 解凍+新資料累積,期間不得另立同假說新 gate(不開 v3)"),
        "family_disclosure": ("v2 家族 K=4(D_5_v2/H_40_v2/H_20_v2/H_82_v2)一次揭露、封閉(執行中不得追加);"
                              "完整測試序列=v1 六門+v2 四門=同一凍結資料共 10 門,結案報告一律 10 門全列;"
                              "家族 Bonferroni 參考 α=0.0125=參考非裁決、不得據以變更展示分級"),
        "provenance": ("假說選自 v1 判死解剖(同一凍結資料、證據相依非獨立、名義 p 帶選擇偏誤);"
                       "D5 hit p=0.038 為 v1 best-of-2 champion 選擇後之名義值未校正——"
                       "v2 新可證偽內容=D5 Brier 翻正/H 軌新特徵與月頻增量"),
    }
    if key == "D5":
        c.update({
            "k_td": 5, "alpha": 0.05, "hac_min_lag": 6,
            "estimand": {"table": "daily_direction_oos_sample", "hcol": "k_td", "model_id": "DailyGBDT_cal",
                         "seed_aggregation": "mean", "panel_window": None},
            "calibrator": "purged isotonic:fit-set/校準尾段內層 embargo k+1 td;GBDT 只 fit 於 fit-set、"
                          "isotonic fit 於尾段 out-of-sample 預測(憲章硬綁②);isotonic 可移動 p=0.5 交叉點"
                          "——v1 hit 過關不自動保留",
            "expected": "全家族最高過門機率;econ 預期 dead(來回 0.585% vs k=5 損益兩平≈66.5% 命中)",
        })
    else:
        h = {"H40": 40, "H20": 20, "H82": 82}[key]
        c.update({
            "horizon_td": h,
            "alpha": 0.05 if key == "H40" else 0.01,
            "hac_min_lag": {"H20": 2, "H40": 3, "H82": 5}[key],   # ≥ceil(h/21)+1(月頻重疊窗覆蓋)
            "estimand": {"table": "direction_oos_sample", "hcol": "horizon", "model_id": "DirStackM",
                         "seed_aggregation": "seed0",
                         "panel_window": ["2021-04-01", "2025-12-31"]},   # 方案 A:季頻 rank 時代(親核點)
            "market_component": "MktLogit_v2(criteria 預先鎖定;MktGBDT 僅陪跑列報、不入裁決)",
            "combo_layer": "top3/top5 隨本門(direction_combo_oos_sample 列報、n 明標、不得單獨解鎖)",
            "expected": {"H40": "低中(v1 修正基線 p≈0.105 起點+新特徵/月頻增量)",
                         "H20": "低(v1 修正基線 p≈0.44 起點)",
                         "H82": "低(v1 三關全敗;120 日曆天主錨)"}[key],
        })
        if key in ("H20", "H82"):
            c["review_tier_cap"] = ("次門 provisional(α=0.01 綁定):即便三關全過,唯『觀察名單』"
                                    "(review_observation_only)、不得完整展示;確證唯解凍後新資料 confirmatory gate")
    return c


def preregister_v2():
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT threshold FROM judgestop_threshold WHERE policy_key='calib_late_ece_ceiling' AND frozen")
        row = cur.fetchone()
        if not row:
            sys.exit("✗ judgestop calib_late_ece_ceiling frozen 列缺")
        ece = float(row[0])
        n = 0
        for gid, key, track, h in (("dgate_D_5_v2", "D5", "D", 5), ("dgate_H_40_v2", "H40", "H", 40),
                                   ("dgate_H_20_v2", "H20", "H", 20), ("dgate_H_82_v2", "H82", "H", 82)):
            c = _criteria_v2(key, ece)
            cur.execute("""INSERT INTO direction_gate (gate_id, track, horizon, purpose, criteria, criteria_sha, git_sha, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (gate_id) DO NOTHING""",
                (gid, track, h, f"v2 復活賭注 {key}(revival plan §0.4;先凍後跑)",
                 json.dumps(c, ensure_ascii=False), _sha(c), git7,
                 "v2 家族 K=4;approve=hugo TTY 親核點(含方案 A 窗)"))
            n += cur.rowcount
        conn.commit()
    print(f"✓ v2 預註冊 {n} 列(K=4 家族封閉;estimand/α/窗/fail_path 已凍)")
    print("  親核指令(於你的終端逐門執行):")
    for gid in V2_GATES:
        print(f"    python scripts/preregister_direction_gate.py --approve {gid} --approved-by hugo")
    return 0


ARENA_GATES = [   # (gate_id, model_key, track, horizon_td);K=6 家族封閉(arena plan §2.1 枚舉)
    ("dgate_arena_own_daily_5", "own_daily_rolling", "D", 5),
    ("dgate_arena_chronos_5", "chronos_bolt_small", "D", 5),
    ("dgate_arena_timesfm_5", "timesfm_25_200m", "D", 5),
    ("dgate_arena_own_stack_20", "own_stack_rolling", "H", 20),
    ("dgate_arena_own_stack_40", "own_stack_rolling", "H", 40),
    ("dgate_arena_own_stack_82", "own_stack_rolling", "H", 82),
]
ARENA_MIN_CLUSTERS = {"D": 250, "H": 36}
A3_GATES = [  # A3 獨立新家族(三鏡頭候選計畫 T4;K=3 封閉;跨家族多重性依憲章 v1.45.0 全序列揭露)
    # _r2:原三列 criteria_sha 為手刻配方 bug(12碼/無 separators),舊配方重算證明內容未變;
    # 原列 approved→superseded 留檔(trigger 白名單),同判準以 _r2 重註冊(2026-07-12)
    ("dgate_a3_threelens_20_r2", "own_threelens_interact", "H", 20),
    ("dgate_a3_threelens_40_r2", "own_threelens_interact", "H", 40),
    ("dgate_a3_threelens_82_r2", "own_threelens_interact", "H", 82),
]


def _power_ref(cur, track, h):
    """MDE/檢定力機械計算(arena plan §4;審查 S2 的核心要求)——以歷史 OOS 為參考先驗:
    per-cluster excess-hit sd + lag-1 自相關 → LRV 膨脹 → 門檻 n 之有效 n → 各檢定力可偵測邊際。
    全機械、預註冊時算一次凍入 criteria(#9 可溯源)。"""
    import numpy as np
    if track == "D":
        cur.execute("""SELECT panel_date, avg((CASE WHEN (p_up>0.5)=(y_up=1) THEN 1 ELSE 0 END)::float)
            FROM daily_direction_oos_sample WHERE model_id='DailyGBDT_cal' GROUP BY 1 ORDER BY 1""")
    else:
        cur.execute("""SELECT panel_date, avg((CASE WHEN (p_up>0.5)=(y_up=1) THEN 1 ELSE 0 END)::float)
            FROM direction_oos_sample WHERE model_id='DirStackM' AND horizon=%s GROUP BY 1 ORDER BY 1""", (h,))
    xs = np.array([float(r[1]) for r in cur.fetchall()])
    if len(xs) < 30:
        return {"note": "歷史參考樣本不足,MDE 以保守常數", "sd": 0.26, "rho1": 0.7, "inflation": 3.4}
    e = xs - xs.mean()
    sd = float(xs.std())
    rho = float((e[1:] @ e[:-1]) / (e @ e)) if float(e @ e) > 0 else 0.0
    infl = max(1.0, (1 + rho) / (1 - rho)) if rho < 1 else 3.4     # AR(1) LRV 膨脹近似
    n_thr = ARENA_MIN_CLUSTERS[track]
    eff_n = n_thr / infl
    alpha = 0.05 / len(ARENA_GATES)
    from math import sqrt
    z = {"a": 2.394 if alpha < 0.01 else 1.645, "p80": 0.842, "p50": 0.0}   # z_{1-α} 近似(α=.00833→2.394)
    se = sd / sqrt(eff_n)
    return {"sd": round(sd, 4), "rho1": round(rho, 4), "inflation": round(infl, 2),
            "threshold_clusters": n_thr, "effective_n": round(eff_n, 1), "alpha_bonferroni": round(alpha, 5),
            "mde_power80_pp": round((z["a"] + z["p80"]) * se * 100, 2),
            "mde_power50_pp": round(z["a"] * se * 100, 2),
            "honest_note": "gate 誠實定位=偵測可交易級邊際;對 +1-2pp 級微小邊際檢定力≈0(fail 為設計預期)"}


def _criteria_arena(model_key, track, h, ece, power):
    return {
        "version": "arena", "alpha": 0.05 / len(ARENA_GATES),
        "gate_rules": {
            "i_hitrate": ("hit-rate 顯著優於同窗全局多數類固定方向基線 max(p_bar,1-p_bar);"
                          "逐 cluster (hit−naive) 序列 HAC Eff-t 單尾 p<alpha(禁 iid)"),
            "ii_brier": "OOS Brier < p_bar*(1-p_bar)(同窗實算)",
            "iii_calibration": {"ece_ceiling": ece, "ece_source": "judgestop_threshold.calib_late_ece_ceiling(DB 讀值)",
                                "quantile_monotone": "十分位 Spearman>0"},
        },
        "estimand": {"table": "direction_arena_prediction", "hcol": "horizon_td", "key_col": "model_key",
                     "model_id": model_key, "seed_aggregation": "seed0", "panel_window": None,
                     "settled_only": True},
        "min_clusters": ARENA_MIN_CLUSTERS[track],
        "auto_trigger": ("第一個滿足『已結算 cluster ≥min_clusters』之月末自動觸發 evaluate;"
                         "結算窗=開賽日至觸發日全部已結算列、無裁剪(零人為裁量,審查 S4)"),
        "hac_min_lag": 6 if track == "D" else max(2, h // 21 + 1),
        "power_disclosure": power,
        "family_disclosure": (f"arena 家族 K={len(ARENA_GATES)}(枚舉凍結、中途加入者入下輪新家族);"
                              "完整測試序列=v1 六門+v2 四門+arena 六門=16 門一律全列"),
        "fail_path": ("任一關不過=evaluated_fail 判死留檔;全家族 fail=結案句限定「在檢定力 X% 下未偵測到 "
                      "≥MDE 邊際」(禁『證偽所有邊際』措辭);同 spec 假說終局、換版=新候選新家族"),
        "provenance": ("prereg-now-evaluate-later:預註冊於首輪對局前(先凍後跑,滿足憲章 v1.42);"
                       "hugo approve 時併簽『係真未來新實驗、不構成對凍結資料重試、不違 no-v3 本旨』"),
        "scoring": "horizon 級聚合;禁單股準確率;live 結算列(normal/last_trade)為判據、unsettleable 除外且揭露",
        "econ_axis": "經濟終關=獨立標示軸不在 GATE 內;過門後另判",
    }


def preregister_a3():
    """A3 家族預註冊(先凍後跑;α=0.05/3;跨家族全序列揭露=v1 六門+v2 四門+A2 六門+A3 三門=19 門)。"""
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT threshold FROM judgestop_threshold WHERE policy_key='calib_late_ece_ceiling' AND frozen")
        row = cur.fetchone()
        if not row:
            sys.exit("✗ judgestop ECE 門檻缺")
        ece = float(row[0])
        cur.execute("SELECT 1 FROM direction_arena_candidate WHERE model_key='own_threelens_interact'")
        if not cur.fetchone():
            sys.exit("✗ 候選未凍結註冊(先 register_arena_candidate.py --register-defaults)")
        n = 0
        for gid, mk, track, h in A3_GATES:
            c = _criteria_arena(mk, track, h, ece, _power_ref(cur, track, h))
            c["version"] = "arena_a3"
            c["alpha"] = 0.05 / len(A3_GATES)
            c["family_disclosure"] = (f"A3 家族 K={len(A3_GATES)}(獨立於 A2 六門家族;Bonferroni 僅控本家族內);"
                                      "完整測試序列=v1 六門+v2 四門+A2 六門+A3 三門=19 門一律全列(憲章 v1.45.0 跨家族揭露)")
            c["power_disclosure"]["alpha_bonferroni"] = round(0.05 / len(A3_GATES), 5)
            cur.execute("""INSERT INTO direction_gate (gate_id, track, horizon, purpose, criteria, criteria_sha, git_sha, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (gate_id) DO NOTHING""",
                (gid, track, h, f"A3 真未來賭注 {mk} {track}×{h}(三鏡頭候選計畫;prereg-now-evaluate-later)",
                 json.dumps(c, ensure_ascii=False), _sha(c), git7,
                 "approve 併簽:係真未來新實驗、不構成對凍結資料重試、不違 no-v3 本旨"))
            n += cur.rowcount
        conn.commit()
        print(f"✓ A3 家族預註冊 {n} 門(K={len(A3_GATES)}, α={0.05/len(A3_GATES):.4f};TTY approve 三行見下)")
        for gid, *_ in A3_GATES:
            print(f"  python scripts/preregister_direction_gate.py --approve {gid} --approved-by hugo")


def preregister_arena():
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT threshold FROM judgestop_threshold WHERE policy_key='calib_late_ece_ceiling' AND frozen")
        row = cur.fetchone()
        if not row:
            sys.exit("✗ judgestop ECE 門檻缺")
        ece = float(row[0])
        cur.execute("SELECT count(*) FROM direction_arena_candidate WHERE gate_eligible")
        if cur.fetchone()[0] < len(ARENA_GATES) - 2:
            sys.exit("✗ 立門候選未註冊齊(先 register_arena_candidate.py --register-defaults)")
        n = 0
        for gid, mk, track, h in ARENA_GATES:
            c = _criteria_arena(mk, track, h, ece, _power_ref(cur, track, h))
            cur.execute("""INSERT INTO direction_gate (gate_id, track, horizon, purpose, criteria, criteria_sha, git_sha, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (gate_id) DO NOTHING""",
                (gid, track, h, f"arena 真未來賭注 {mk} {track}×{h}(arena plan §4;prereg-now-evaluate-later)",
                 json.dumps(c, ensure_ascii=False), _sha(c), git7,
                 "approve=hugo TTY(併簽 no-v3 相容句);evaluate=樣本門檻自動觸發"))
            n += cur.rowcount
        conn.commit()
    print(f"✓ arena 預註冊 {n} 列(K={len(ARENA_GATES)};MDE/檢定力已機械凍入 criteria)")
    for gid, *_ in ARENA_GATES:
        print(f"    python scripts/preregister_direction_gate.py --approve {gid} --approved-by hugo")
    return 0


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
    ap.add_argument("--preregister-v2", action="store_true", dest="pre_v2")
    ap.add_argument("--preregister-arena", action="store_true", dest="pre_arena")
    ap.add_argument("--preregister-a3", action="store_true", dest="pre_a3")
    ap.add_argument("--approve")
    ap.add_argument("--approved-by", dest="by")
    ap.add_argument("--check")
    args = ap.parse_args()
    if args.pre_arena:
        return preregister_arena()
    if args.pre_a3:
        return preregister_a3()
    if args.pre_v2:
        return preregister_v2()
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
