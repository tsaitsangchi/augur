#!/usr/bin/env python
"""模型效能探測 — tok/s / 載入 / VRAM 落帳(D1;補完計畫 §4:效能零落帳之封閉)。

🎯 這支在做什麼(白話):對 {qwen3:4b, qwen3:8b} × 3 類標準題(propose 契約/錨轉換/純結構化 JSON)×
   3 重複(#11)實測 Ollama 終包統計(eval_count/eval_duration/load_duration——過去被丟棄),換算 tok/s
   落 deliberation_model_probe。VRAM 以 nvidia-smi 實測;不可得(WSL2 常見)→ NULL+note **誠實缺測不估算**
   (#9)。model-batched:先 4b 全部、後 8b 全部(載入 ≤2 次);8b 於 4GB VRAM 必 CPU offload、慢=事實照實落。

守 #9(統計實回、NULL 不補值)· #11(3 重複)· #28(全本地零 Claude)· #29a。

執行指令矩陣:
  python scripts/probe_deliberation_models.py               # 無參數:印矩陣+歷史 probe 摘要(唯讀)
  python scripts/probe_deliberation_models.py --run         # 2 模 × 3 類 × 3 重複 = 18 探測(model-batched)
  python scripts/probe_deliberation_models.py --run --models qwen3:4b   # 單模
"""
import argparse
import json
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.advisor.ollama import chat_with_stats

_PROMPTS = {
    "propose": ("就題目「驗證 feature_values 表健康」提出 2 條可機械驗證的宣稱(claims,含 anchor)。",
                {"type": "object", "properties": {"claims": {"type": "array", "items": {"type": "object",
                 "properties": {"claim_text": {"type": "string"}, "anchor": {"type": "string"}},
                 "required": ["claim_text", "anchor"]}}}, "required": ["claims"]}),
    "anchor": ("把宣稱「表 feature_values 至少 100 列」轉成 SELECT 錨,回 anchor 欄位。",
               {"type": "object", "properties": {"anchor": {"type": "string"}}, "required": ["anchor"]}),
    "structured_json": ("回一個 JSON:{\"ok\": true, \"n\": 42}。",
                        {"type": "object", "properties": {"ok": {"type": "boolean"}, "n": {"type": "integer"}},
                         "required": ["ok", "n"]}),
}


def _gpu_mem():
    """nvidia-smi memory.used(MB);不可得 → (None, note)。"""
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return int(r.stdout.strip().splitlines()[0]), None
    except (OSError, subprocess.TimeoutExpired, ValueError):
        pass
    return None, "nvidia-smi unavailable"


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def run(models, reps, timeout):
    git7 = _git7()
    with db.connect() as conn:
        cur = conn.cursor()
        for model in models:                                    # model-batched(載入 ≤ len(models) 次)
            print(f"── {model} ──")
            for kind, (prompt, schema) in _PROMPTS.items():
                for r in range(reps):
                    try:
                        _c, st = chat_with_stats(prompt, model=model, timeout=timeout, schema=schema,
                                                 options={"temperature": 0, "num_predict": 400})
                    except Exception as e:
                        print(f"  ✗ {kind}#{r}: {type(e).__name__}: {str(e)[:80]}")
                        continue
                    ns = 1_000_000
                    ev, evd = st.get("eval_count"), st.get("eval_duration")
                    tps = round(ev / (evd / 1e9), 2) if ev and evd else None
                    mem, note = _gpu_mem()
                    cur.execute(
                        "INSERT INTO deliberation_model_probe (model_tag, task_kind, prompt_chars, "
                        "prompt_eval_count, eval_count, load_ms, prompt_eval_ms, eval_ms, total_ms, "
                        "tok_per_s, gpu_mem_used_mb, note, git_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (model, kind, len(prompt), st.get("prompt_eval_count"), ev,
                         (st.get("load_duration") or 0) // ns or None,
                         (st.get("prompt_eval_duration") or 0) // ns or None,
                         (evd or 0) // ns or None, (st.get("total_duration") or 0) // ns,
                         tps, mem, note, git7))
                    conn.commit()
                    print(f"  ✓ {kind}#{r}: {tps or 'NULL'} tok/s | total {(st.get('total_duration') or 0)//ns} ms"
                          f" | vram {mem or 'NULL'}")
    return 0


def summary():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT model_tag, task_kind, count(*), round(avg(tok_per_s),1), round(min(tok_per_s),1), "
                    "round(max(tok_per_s),1) FROM deliberation_model_probe WHERE tok_per_s IS NOT NULL "
                    "GROUP BY 1,2 ORDER BY 1,2")
        print("歷史 probe(model × kind:n / avg / min / max tok/s):")
        for r in cur.fetchall():
            print(f"  {r[0]:<10} {r[1]:<16} n={r[2]} avg={r[3]} [{r[4]},{r[5]}]")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--models", nargs="*", default=["qwen3:4b", "qwen3:8b"])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=900)
    args = ap.parse_args()
    if args.run:
        return run(args.models, args.reps, args.timeout)
    print(__doc__.split("執行指令矩陣:")[1])
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
