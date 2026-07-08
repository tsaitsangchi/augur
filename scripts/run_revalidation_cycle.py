#!/usr/bin/env python
"""持續再驗證 cycle 編排(harness P3)— #8 gate → revalidate → verdict → 判停告警落地。

🎯 這支在做什麼(白話):把持續再驗證一輪串起來,並把判停**告警落地**(非背景無人看)——
   1. **#8 gate**:先跑 release-lag anti-leakage 測試(`tests/test_release_lag_antileakage.py`),
      **不過即中止**(fail-closed:洩漏未守住則不出裁決,#8 零容忍)。
   2. **revalidate --run**:重跑 B/C/D + deflation 整合(寫 revalidation_ledger,#12 SSOT)。
   3. **revalidate_verdict**:兩軌三態判停(讀 ledger vs 凍結 baseline、寫 revalidation_verdict)。
   4. **告警落地**:讀本輪 verdict,**非 deploying_unestablished(疑似/確認衰減)即印顯著告警橫幅**
      (一次性、由執行者當下看見,靈魂:判停=建議、人決策;不自動下架)。

   **cadence(#28、不自掛長喚醒鏈)**:panel 資料驅動——最新 panel 已有、且未在 ledger 才跑一輪
   (`--skip-existing`),否則跳過。季頻節奏(H60 ~每季新 panel);**一次性排程 or 用戶手動觸發、
   背景零 usage 本地跑,不輪詢、不掛多次自我喚醒**(等下一季底由用戶/排程 ping,非常駐 daemon)。

守 #8(gate 不過即中止 fail-closed)· #12(編排既有腳本、不重造)· #15(判停告警誠實落地、非無人看)·
   #28(panel 資料驅動、一次性、本地零 usage、不自掛喚醒鏈)· 靈魂(判停=系統建議、人決策)。
   SSOT=harness plan P3。

執行指令矩陣:
  python scripts/run_revalidation_cycle.py                 # 完整一輪(#8 gate→revalidate→verdict→告警)
  python scripts/run_revalidation_cycle.py --skip-8gate    # 略 #8 gate(僅供快測;生產不建議略)
  python scripts/run_revalidation_cycle.py --skip-revalidate  # 略重跑(用現況 ledger 只跑 verdict+告警,快測)
  python scripts/run_revalidation_cycle.py --dry-run       # verdict 不寫、其餘照跑
"""
import argparse
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db

HERE = "scripts"


def _run(cmd, label):
    print(f"\n{'─'*70}\n▶ {label}\n{'─'*70}", flush=True)
    r = subprocess.run([sys.executable] + cmd)
    return r.returncode


def _latest_verdict(as_of=None):
    """讀本輪(或指定 as_of)部署 cell 之兩軌 verdict 狀態(告警落地依此)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        if as_of is None:
            cur.execute("SELECT max(as_of_date) FROM revalidation_verdict")
            as_of = cur.fetchone()[0]
        if as_of is None:
            return None, []
        cur.execute("SELECT track, state, triggered_cond, note FROM revalidation_verdict "
                    "WHERE as_of_date=%s ORDER BY track", (as_of,))
        return as_of, cur.fetchall()


def _alert(as_of, rows):
    """判停告警落地:非 deploying 即印顯著橫幅(一次性、執行者當下看見)。回 True 若有告警。"""
    b = next((r for r in rows if r[0] == "B_decay"), None)
    state = b[1] if b else "unknown"
    if state == "deploying_unestablished":
        print(f"\n✓ 再驗證裁決(as_of {as_of}):deploying_unestablished ——薄 edge 部署中、未達統計確立但"
              f"無衰減訊號;continue 追蹤(#15 判停≠失敗)。")
        return False
    banner = "█" * 70
    label = {"suspected_decay_review": "⚠ 疑似衰減 — 人審",
             "confirmed_decay_stop": "🛑 確認衰減 — 建議停(人決策)"}.get(state, state)
    print(f"\n{banner}\n  判停告警(as_of {as_of}):{label}\n  觸發:{b[2] if b else '?'}\n  訊號:{b[3] if b else '?'}\n"
          f"  → 靈魂:系統建議、人決策——請人審證據(revalidation_verdict/ledger/baseline)後決定退場/重估/擴宇宙。\n{banner}")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="持續再驗證 cycle 編排(P3)")
    ap.add_argument("--skip-8gate", action="store_true", help="略 #8 gate(僅快測、生產不建議)")
    ap.add_argument("--skip-revalidate", action="store_true", help="略 revalidate 重跑(用現況 ledger 只跑 verdict)")
    ap.add_argument("--dry-run", action="store_true", help="verdict 不寫入(其餘照跑)")
    args = ap.parse_args(argv)

    # 1. #8 gate(fail-closed:不過即中止)
    if not args.skip_8gate:
        rc = _run(["-m", "pytest", "tests/test_release_lag_antileakage.py", "-q"], "#8 anti-leakage gate")
        if rc != 0:
            sys.exit("✗ #8 gate 未過(release-lag 洩漏未守住)——中止,不出再驗證裁決(#8 零容忍 fail-closed)。")
        print("✓ #8 gate 過(release-lag build 端守住)。")

    # 2. revalidate --run(deflation 整合)
    if not args.skip_revalidate:
        rc = _run([f"{HERE}/revalidate.py", "--run", "--skip-existing"], "revalidate --run(B/C/D + deflation)")
        if rc != 0:
            sys.exit("✗ revalidate 失敗——中止。")

    # 3. revalidate_verdict(兩軌三態)
    vcmd = [f"{HERE}/revalidate_verdict.py"] + (["--dry-run"] if args.dry_run else [])
    rc = _run(vcmd, "revalidate_verdict(兩軌三態判停)")
    if rc != 0:
        sys.exit("✗ verdict 失敗——中止。")

    # 4. 告警落地
    as_of, rows = _latest_verdict()
    if rows:
        _alert(as_of, rows)
    else:
        print("(無 verdict 列;--dry-run 或首輪未寫)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
