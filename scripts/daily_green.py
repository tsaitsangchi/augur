#!/usr/bin/env python
"""常綠驗證入口 — 煙測+顧問回歸+Qdrant 影子(+選配基準)每日機械綠檢(e2e 主計畫 P7)。

🎯 這支在做什麼(白話):把「系統還暢通嗎」變成一條每日命令——依序跑
   ① verify_knowledge_e2e_smoke --run(v1.40.0 暢通不變式)② verify_advisor_regression --run --no-llm
   ③ verify_qdrant_shadow --run(cutover 後持續守門)④(--with-benchmark)deliberation 基準快檢。
   任一 FAIL=exit≠0+紅字;結果各自落庫(shadow_eval/benchmark)。**FREEZE 安全**:全程零外部 API、
   零市場資料;與 daily_maintenance(市場同步,FREEZE 下休眠)嚴格分離。

守 #28(全本地零 token)· v1.38.0 FREEZE(不觸市場)· v1.40.0(煙測=暢通判定)· #29a。

執行指令矩陣:
  python scripts/daily_green.py                    # 三驗證器依序(預設)
  python scripts/daily_green.py --with-benchmark   # 加基準快檢(4b,每類 2 題)
  python scripts/daily_green.py --skip shadow      # 跳過某驗證器(qdrant 維護時)
  # systemd:systemctl --user enable --now augur-green.timer(每日 07:30)
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

STEPS = [
    ("smoke", ["scripts/verify_knowledge_e2e_smoke.py", "--run"]),
    ("regression", ["scripts/verify_advisor_regression.py", "--run", "--no-llm"]),
    ("shadow", ["scripts/verify_qdrant_shadow.py", "--run"]),
    ("delib-watch", ["scripts/resolve_escalation.py", "--watch"]),   # D3/D5:殭屍 session+人裁積壓(warn-only)
]


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--with-benchmark", dest="bench", action="store_true")
    ap.add_argument("--skip", nargs="*", default=[], choices=[s[0] for s in STEPS])
    args = ap.parse_args()
    steps = [(n, c) for n, c in STEPS if n not in args.skip]
    if args.bench:
        steps.append(("benchmark", ["scripts/benchmark_deliberation.py", "--run",
                                    "--n-per-class", "2", "--model", "qwen3:4b"]))
    fails = []
    t0 = time.time()
    for name, cmd in steps:
        ts = time.time()
        r = subprocess.run([PY, str(REPO / cmd[0]), *cmd[1:]], capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{'✓' if ok else '✗'} {name:<11} exit={r.returncode}({time.time()-ts:.0f}s)")
        if not ok:
            fails.append(name)
            print("   " + (r.stdout + r.stderr).strip().splitlines()[-1][:110])
    print(f"═> {'全綠' if not fails else 'FAIL:' + ','.join(fails)}({(time.time()-t0)/60:.1f} 分)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
