#!/usr/bin/env python
"""本地審議引擎 CLI — 薄殼:解析參數 → engine.deliberate → 印報告(P3 模組化後,邏輯全在 src/augur/deliberation/)。

🎯 這支在做什麼(白話):給題目(+可選目標檔+lens),本地 qwen 提「可機械驗證的宣稱」→ 4 真 oracle 裁決
   → 誠實報告。**LLM 意見零證據力,工具輸出才是證據**(#15)——把 Claude ultracode 的「對抗驗證」搬到
   本地:弱模型只需會「提出可驗證的問題」,判對判錯交給誠實工具。全程本地零 Claude token;帳落 deliberation_*。
   邏輯住 src/augur/deliberation/(anchors L1-L5 / lens〔DB〕/ ledger 帳本 / engine 狀態機 / verifiers 4 oracle);
   本檔僅 CLI 串接(#18 CLI=動作動詞、薄殼)。

守 #15(裁決全出 oracle)· #28(唯本機 qwen)· #29a。前置=migrate_deliberation_ddl.py --run。
   SSOT=reports/augur_local_ultracode_engine_plan_20260710.md。

執行指令矩陣:
  python scripts/deliberate.py                                        # 無參數:印矩陣+近期 session(唯讀)
  python scripts/deliberate.py --run --topic "驗證機率層三表就位"        # 題目式(qwen 自析可驗宣稱)
  python scripts/deliberate.py --run --topic "..." --target reports/x.md --lens skeptic   # 附目標檔+視角
  python scripts/deliberate.py --run --topic "..." --model qwen3:8b --max-claims 8        # 換模/量
  python scripts/deliberate.py --panel --topic "..."                  # 多視角 panel+loop-until-dry(全 lens×多輪、三級殺權聚合)
  python scripts/deliberate.py --panel --topic "..." --lenses skeptic complete --max-rounds 3 --dry-k 2
  python scripts/deliberate.py --report <session_id>                  # 重印某 session 裁決報告(唯讀)
"""
import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.deliberation import engine, ledger
from augur.deliberation.lens import lens_keys

REPO = Path(__file__).resolve().parent.parent


def _target_block(target):
    if not target:
        return ""
    p = (REPO / target).resolve()
    if not str(p).startswith(str(REPO)) or not p.is_file():
        sys.exit(f"✗ --target 須為 repo 內檔案:{target}")
    return f"目標檔案 {target}(前 6000 字):\n---\n{p.read_text(encoding='utf-8', errors='replace')[:6000]}\n---"


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--panel", action="store_true")
    ap.add_argument("--topic")
    ap.add_argument("--target")
    ap.add_argument("--lens", default="skeptic")
    ap.add_argument("--lenses", nargs="*")             # panel:多視角(預設全部 enabled)
    ap.add_argument("--model", default="qwen3:4b")     # 結構化步預設 4b(快檔;format 約束壓思考洩漏)
    ap.add_argument("--max-claims", dest="n", type=int, default=6)
    ap.add_argument("--max-rounds", dest="max_rounds", type=int, default=3)
    ap.add_argument("--dry-k", dest="dry_k", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--report")
    args = ap.parse_args()
    if args.report:
        ledger.report(args.report); return 0
    keys = lens_keys()
    if args.panel:
        if not args.topic:
            sys.exit("--panel 需 --topic")
        lenses = args.lenses or keys
        bad = [l for l in lenses if l not in keys]
        if bad:
            sys.exit(f"✗ --lenses 含未知視角 {bad}(deliberation_lens 表;∈ {keys})")
        r = engine.deliberate_panel(args.topic, _target_block(args.target), lenses, args.model,
                                    args.n, args.timeout, max_rounds=args.max_rounds, dry_k=args.dry_k)
        return 0
    if args.run:
        if not args.topic:
            sys.exit("--run 需 --topic")
        if args.lens not in keys:
            sys.exit(f"✗ --lens 須 ∈ {keys}(deliberation_lens 表;新增=INSERT 一列 #29b)")
        sid, _ = engine.deliberate(args.topic, _target_block(args.target), args.lens,
                                   args.model, args.n, args.timeout)
        return 0 if sid else 1
    print(__doc__.split("執行指令矩陣:")[1])
    rows = ledger.recent()
    print("近期 session:" if rows else "近期 session:(無)")
    for r in rows:
        print(f"  {r[0]} | {r[1][:40]} | {r[2]} | {r[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
