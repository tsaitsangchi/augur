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
  python scripts/deliberate.py --iterate --topic "..."                # 模式9:DRAFT→ATTACK→REFINE→VERIFY 自我迭代
  python scripts/deliberate.py --judge 12 13 14 --lenses skeptic complete   # 模式4:判官團評分 proposal(soft 排序)
  python scripts/deliberate.py --run-plan plan.json                   # 模式10:批次計畫經 run/task 帳本(resume-safe)
  python scripts/deliberate.py --resume dlrun_XXXX                    # 斷點續跑(done 跳過/failed<3 重試)
  python scripts/deliberate.py --list-runs                            # 近期 run 清單(唯讀)
"""
import argparse
import json
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


def _llm_fn(model, timeout):
    """注入式 llm_fn(prompt, schema)->dict(iterate/panel_judge 用;測試可換假 LLM)。"""
    from augur.advisor.ollama import make_structured_llm_fn

    def fn(prompt, schema):
        return make_structured_llm_fn(schema, model=model, timeout=timeout, retries=1,
                                      options={"temperature": 0, "num_predict": 1600})(prompt)
    return fn


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--panel", action="store_true")
    ap.add_argument("--iterate", action="store_true")
    ap.add_argument("--judge", nargs="*", type=int)
    ap.add_argument("--run-plan", dest="run_plan")
    ap.add_argument("--resume", dest="resume_id")
    ap.add_argument("--list-runs", dest="list_runs", action="store_true")
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
    if args.list_runs:
        from augur.core import db as _db
        with _db.connect() as conn, _db.transaction(conn) as cur:
            cur.execute("SELECT run_id, status, jsonb_array_length(plan), created_at::timestamp(0) "
                        "FROM deliberation_run ORDER BY created_at DESC LIMIT 8")
            for r in cur.fetchall():
                print(f"  {r[0]} | {r[1]:<10} | {r[2]} task | {r[3]}")
        return 0
    if args.iterate:
        if not args.topic:
            sys.exit("--iterate 需 --topic")
        from augur.core import db as _db
        from augur.deliberation import iterate
        with _db.connect() as conn:
            cur = conn.cursor()
            fid = iterate.run_iteration(cur, _llm_fn(args.model, args.timeout), args.topic,
                                        args.target, args.max_rounds, args.model)
            conn.commit()
        print(f"✓ 自我迭代完成 final proposal_id={fid}(鏈可溯:deliberation_proposal.parent_id)")
        return 0
    if args.judge is not None:
        if not args.judge:
            sys.exit("--judge 需 proposal id(s)")
        from augur.core import db as _db
        from augur.deliberation import panel_judge
        lenses = args.lenses or lens_keys()
        with _db.connect() as conn:
            cur = conn.cursor()
            sids = panel_judge.synthesize_panel(cur, _llm_fn(args.model, args.timeout),
                                                args.judge, lenses, args.model)
            conn.commit()
            print(f"✓ 判官團 {len(sids)} 分落庫;排序(soft、零裁決效力):")
            for pid, avg, n in panel_judge.ranking(cur, args.judge):
                print(f"   proposal {pid}: mean={avg:.2f}(n={n})")
        return 0
    if args.run_plan or args.resume_id:
        from augur.core import db as _db
        from augur.deliberation import ledger as lg
        with _db.connect() as conn:
            cur = conn.cursor()
            if args.run_plan:
                plan = json.loads(Path(args.run_plan).read_text(encoding="utf-8"))
                rid = lg.create_run(cur, f"plan:{Path(args.run_plan).name}", plan)
            else:
                rid = args.resume_id
            lg.resume_reset(cur, rid)
            conn.commit()
            print(f"run {rid} 開跑(resume-safe)")
            while True:
                t = lg.next_task(cur, rid)
                conn.commit()
                if not t:
                    break
                tid, seq, p = t
                try:
                    sid, _ = engine.deliberate(p["topic"], _target_block(p.get("target")), p.get("lens", "skeptic"),
                                               p.get("model", args.model), p.get("n", args.n), args.timeout)
                    lg.mark_task(cur, tid, "done" if sid else "failed", sid)
                except Exception as e:
                    print(f"  ✗ task {seq} 失敗:{type(e).__name__}")
                    lg.mark_task(cur, tid, "failed")
                conn.commit()
            st = lg.finish_run(cur, rid)
            conn.commit()
        print(f"run {rid} → {st}")
        return 0 if st == "completed" else 1
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
