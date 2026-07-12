#!/usr/bin/env python
"""擂台候選註冊 — 凍結協定執行(arena plan §2.2;insert-only、provenance 必填)。

🎯 這支在做什麼(白話):把參賽者的身分證凍進 direction_arena_candidate——spec(配方/轉換口徑/
   conversion_selection_log/refit 政策/provenance)+code_sha(git HEAD)+weights_hash(權重檔 sha256;
   滾動 refit 類=null)。市場隊 spec 必填 repo/revision/license(白名單)+offline_only:true。
   凍後不可改(trigger);換版=新 model_key 新列且歷代全計 K。

守 #15(凍結協定機械化)· #10(provenance)· #29a/d。SSOT=arena plan §2.2。

執行指令矩陣:
  python scripts/register_arena_candidate.py                                # 無參數:參賽者清單(唯讀)
  python scripts/register_arena_candidate.py --register-defaults           # 註冊 §2.1 枚舉表全體(冪等)
  python scripts/register_arena_candidate.py --retire <key> --note "..."   # 退役留痕(status 轉移)
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

LICENSE_WHITELIST = ("apache-2.0", "mit")


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


DEFAULTS = [
    # (model_key, team, track, gate_eligible, spec)
    ("own_daily_rolling", "own", "D", True, {
        "recipe": "價量4特徵+HistGBDT(3-seed)+isotonic(train尾段);滾動 refit=每出手日以可見史重訓",
        "refit_policy": "per-round;train_data_max_date 逐列留痕",
        "conversion": "分類器直出機率", "horizons": [5]}),
    ("own_v2_frozen", "own", "D", False, {
        "recipe": "v2 DailyGBDT_cal 凍結配方(同 spec 假說已兩敗)",
        "note": "對照列不立門不佔 K(arena plan §2.1)", "horizons": [5]}),
    ("majority", "baseline", "D", False, {"rule": "全局多數類", "horizons": [5]}),
    ("momentum_20", "baseline", "D", False, {"rule": "20d 動量條件頻率(慣例值凍結)", "horizons": [5]}),
    ("mc_bootstrap", "baseline", "D", False, {"rule": "52w block bootstrap 正終值比例(seed 42)", "horizons": [5]}),
    ("chronos_bolt_small", "market", "D", True, {
        "provenance": {"repo": "amazon/chronos-bolt-small", "revision": "main", "license": "apache-2.0"},
        "offline_only": True,
        "conversion": "終點分位曲線過現價位置之線性插值(P=1-F(現價))",
        "conversion_selection_log": "唯一嘗試之口徑、零調參;無凍結資料表現參與選擇", "horizons": [5]}),
    ("timesfm_25_200m", "market", "D", True, {
        "provenance": {"repo": "google/timesfm-2.5-200m-pytorch", "revision": "main", "license": "apache-2.0"},
        "offline_only": True,
        "conversion": "同 chronos(分位頭終點分位插值)",
        "conversion_selection_log": "唯一嘗試之口徑、零調參;無凍結資料表現參與選擇", "horizons": [5]}),
    ("own_stack_rolling", "own", "H", True, {
        "recipe": "DirStackM 配方(月頻 stack)+MktLogit_v2 分量;滾動 refit",
        "refit_policy": "per-month;train_data_max_date 留痕",
        "conversion": "logit 直出機率", "horizons": [20, 40, 82]}),
    ("own_threelens_interact", "own", "H", True, {
        "recipe": "44 特徵(35 三鏡頭直餵+9 先驗交互對)月頻;HistGBM(max_iter=200,depth=3,lr=0.05)"
                  "×3-seed(7/42/2026)平均+isotonic(訓練尾 20% 面板);市場 context 不用(delta=特徵寬度)",
        "interact_pairs_ssot": "scripts/build_threelens_monthly.py INTERACT_PAIRS(T0 拍板凍結 2026-07-12;9 對)",
        "feature_source": "direction_threelens_feature_monthly(builder=feature_values 同 generator 零口徑漂移)",
        "refit_policy": "per-month rolling;train=標籤結算<as-of 全歷史",
        "conversion": "isotonic 校準機率直出",
        "engineering_smoke": "2026-07-12 一次跑零迭代(非 gate 宣稱);A3 家族先凍後跑",
        "horizons": [20, 40, 82]}),
]


def _validate(team, spec):
    if team == "market":
        pv = spec.get("provenance") or {}
        assert pv.get("repo") and pv.get("revision"), "市場隊 provenance repo/revision 必填"
        assert (pv.get("license") or "").lower() in LICENSE_WHITELIST, f"license 須在白名單 {LICENSE_WHITELIST}"
        assert spec.get("offline_only") is True, "市場隊 offline_only:true 必填(predict 零網路,硬約束)"
        assert spec.get("conversion_selection_log"), "conversion_selection_log 必填(轉換口徑選擇紀錄)"


def register_defaults():
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        n = 0
        for key, team, track, elig, spec in DEFAULTS:
            _validate(team, spec)
            cur.execute("""INSERT INTO direction_arena_candidate
                (model_key, team, track, gate_eligible, spec, code_sha, weights_hash, registry_model_id)
                VALUES (%s,%s,%s,%s,%s,%s,NULL,%s) ON CONFLICT (model_key) DO NOTHING""",
                (key, team, track, elig, json.dumps(spec, ensure_ascii=False), git7,
                 "DailyGBDT_cal" if key == "own_v2_frozen" else None))
            n += cur.rowcount
        conn.commit()
    print(f"✓ 註冊 {n} 新列(冪等;已存在者不動——凍結協定)")
    print("  立門候選(佔 K)=own_daily_rolling、chronos_bolt_small、timesfm_25_200m(D×5)"
          "+own_stack_rolling(H×20/40/82)→ K 草案=6 門")
    return 0


def retire(key, note):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE direction_arena_candidate SET status='retired', retire_note=%s WHERE model_key=%s "
                    "AND status<>'retired' RETURNING model_key", (note or "unspecified", key))
        if not cur.fetchone():
            sys.exit(f"✗ {key} 不存在或已退役")
        conn.commit()
    print(f"✓ {key} 退役留痕(其 ledger 仍入 gate 家族——arena plan §2.2)")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--register-defaults", action="store_true", dest="reg")
    ap.add_argument("--retire")
    ap.add_argument("--note")
    args = ap.parse_args()
    if args.reg:
        return register_defaults()
    if args.retire:
        return retire(args.retire, args.note)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.direction_arena_candidate')")
        if not cur.fetchone()[0]:
            print("(表未建;先 migrate_direction_arena_ddl.py --run)"); return 0
        cur.execute("SELECT model_key, team, track, gate_eligible, status FROM direction_arena_candidate ORDER BY team, model_key")
        for r in cur.fetchall():
            print(f"  {r[0]:<20} {r[1]:<9} {r[2]} 立門={r[3]} {r[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
