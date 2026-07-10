#!/usr/bin/env python
"""審議引擎基準測試 — 「引擎 vs 單發 qwen」機械對照,「習得」的可證偽證明(本地審議引擎計畫 §5)。

🎯 這支在做什麼(白話):機械回答「引擎到底比裸問 qwen 好在哪?」——
   造 N 條**半真半假**的宣稱(真值由 DB/檔案**即時機械建構**,零人工標註偏誤;三類:schema 存在/
   quant 量比較/doc 檔內子串),兩臂同題對照:
   · A 臂 single_shot:qwen 直接判每條真偽(**LLM 意見**,structured output)
   · B 臂 engine:qwen 只寫 (verifier,anchor)(含 L1 grounding+L2 lint)→ **oracle 裁決**;
     undecidable/escalate=**棄權**(引擎誠實選項,A 臂沒有)
   判準(#15 可證偽):引擎「習得」⇔ **假確認數 << 單發** 且 裁決準確率 ≥ 單發;證不出=誠實回
   前身計畫「基本不建」結論。結果落 deliberation_benchmark(逐題 detail 可重現 #10)。

守 #15(真值機械建構、結果照實)· #10(逐題落庫)· #28(全本地 qwen 零 Claude)· #29a。
   前置=migrate_deliberation_ddl.py --run。

執行指令矩陣:
  python scripts/benchmark_deliberation.py                    # 無參數:印矩陣+歷史 run 摘要(唯讀)
  python scripts/benchmark_deliberation.py --run              # 預設 24 題(每類 8,半真半假)×兩臂,qwen3:4b
  python scripts/benchmark_deliberation.py --run --n-per-class 4 --model qwen3:8b
  python scripts/benchmark_deliberation.py --report           # 最新對照報告+習得裁決
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.deliberation.verifiers import run_verifier

REPO = Path(__file__).resolve().parent.parent

# 真值建構素材(穩定錨;真值於執行時即時機械確立,非寫死)
_SCHEMA_TRUE = ["feature_values", "model_registry", "prediction_probability", "knowledge_item",
                "deliberation_claim", "probability_calibrator", "core_universe_asof", "knowledge_lexicon"]
_SCHEMA_FALSE = ["feature_valuez", "model_registry_v2", "prediction_probabilities", "knowledge_items",
                 "deliberation_claimz", "probability_calibrators", "core_universe", "lexicon_knowledge"]
_QUANT_TABLES = ["feature_values", "probability_oos_sample", "knowledge_item", "prediction_values",
                 "knowledge_lexicon", "model_registry", "probability_calibrator", "prediction_probability"]
_DOC_FILE = "CLAUDE.md"
_DOC_TRUE = ["換機接續", "最小邊界", "資料真實性", "Clean-Room", "冪等", "FinMind", "本地優先", "碰護欄即停"]
_DOC_FALSE = ["量子占卜協議", "自動下單模組", "保證獲利條款", "無限重試風暴", "跳過驗證直上", "外包雲端LLM",
              "絕對漲跌機率表", "免測試快速通道"]


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, cwd=str(REPO)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def build_tasks(n_per_class):
    """造題:每類 n 條(半真半假交錯);真值即時機械確立。回 [(task_class, claim_text, truth)]。"""
    tasks = []
    k = n_per_class // 2
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in _SCHEMA_TRUE[:k]:
            tasks.append(("schema", f"資料表 {t} 存在於本專案 PostgreSQL public schema", True))
        for t in _SCHEMA_FALSE[:k]:
            tasks.append(("schema", f"資料表 {t} 存在於本專案 PostgreSQL public schema", False))
        for i, t in enumerate(_QUANT_TABLES[:n_per_class]):
            cur.execute(f"SELECT count(*) FROM {t}")
            actual = cur.fetchone()[0]
            if i % 2 == 0:   # 真:實際數的下界
                thr = max(1, int(actual * 0.5))
                tasks.append(("quant", f"資料表 {t} 至少有 {thr} 列", True))
            else:            # 假:實際數的兩倍+10
                thr = actual * 2 + 10
                tasks.append(("quant", f"資料表 {t} 至少有 {thr} 列", False))
    text = (REPO / _DOC_FILE).read_text(encoding="utf-8", errors="replace")
    for s in _DOC_TRUE[:k]:
        assert s in text, f"素材失效:{s!r} 不在 {_DOC_FILE}(更新素材)"
        tasks.append(("doc", f"檔案 {_DOC_FILE} 內含字串「{s}」", True))
    for s in _DOC_FALSE[:k]:
        assert s not in text, f"素材失效:{s!r} 竟在 {_DOC_FILE}"
        tasks.append(("doc", f"檔案 {_DOC_FILE} 內含字串「{s}」", False))
    return tasks


def arm_single_shot(tasks, model, timeout):
    """A 臂:qwen 一批直判真偽(LLM 意見;無棄權選項=其真實使用形態)。回 {idx: bool}。"""
    from augur.advisor.ollama import make_structured_llm_fn
    schema = {"type": "object", "properties": {"verdicts": {"type": "array", "items": {
        "type": "object", "properties": {"idx": {"type": "integer"}, "is_true": {"type": "boolean"}},
        "required": ["idx", "is_true"]}}}, "required": ["verdicts"]}
    listing = "\n".join(f"{i}. {c}" for i, (_, c, _t) in enumerate(tasks))
    fn = make_structured_llm_fn(schema, model=model, timeout=timeout, retries=1,
                                options={"temperature": 0, "num_predict": 2000})
    out = fn("逐條判斷下列關於本專案(augur,台股量化系統)的宣稱是否為真。對每條回 idx 與 is_true:\n" + listing)
    return {int(v["idx"]): bool(v["is_true"]) for v in out.get("verdicts", [])}


_ANCHOR_SCHEMA = {"type": "object", "properties": {
    "assigned_verifier": {"type": "string", "enum": ["information_schema", "db_query", "file_grep", "human_claude"]},
    "anchor": {"type": "string"}}, "required": ["assigned_verifier", "anchor"]}

_ENGINE_CONTRACT = """把下列宣稱轉成一個可機械驗證的檢查。anchor 只放參數本身:
- information_schema:驗表存在。anchor="表名"(如 "feature_values")
- db_query:量比較。anchor="SELECT 單標量 => 比較子 數值"(如 "SELECT count(*) FROM t => >= 10")
- file_grep:檔內字串。anchor="路徑::字串"(如 "CLAUDE.md::換機接續")
無法機驗 → human_claude。只輸出 JSON。
宣稱:{claim}"""


def arm_engine(tasks, model, timeout):
    """B 臂:qwen 寫錨(L1 grounding+L2 lint 沿用引擎同一支)→ oracle 裁決;undecidable/human=棄權。
    回 {idx: True/False/None(棄權)}。"""
    from augur.advisor.ollama import make_structured_llm_fn
    sys.path.insert(0, str(REPO / "scripts"))
    from deliberate import _fast_anchor, _normalize_anchor, _schema_grounding, _verifier_lint   # #12 同一支,零複製
    fn = make_structured_llm_fn(_ANCHOR_SCHEMA, model=model, timeout=timeout, retries=1,
                                options={"temperature": 0, "num_predict": 300})
    out, meta = {}, {}
    for i, (cls, claim, _t) in enumerate(tasks):
        fp = _fast_anchor(claim, _DOC_FILE if cls == "doc" else None)   # L4 快路優先(零 LLM)
        if fp:
            ver, anc = fp
        else:
            try:
                prop = fn(_ENGINE_CONTRACT.format(claim=claim) + _schema_grounding(claim))
            except RuntimeError:
                out[i] = None; meta[i] = ("(LLM 失敗)", "")
                continue
            ver = prop["assigned_verifier"]
            anc = _normalize_anchor(prop["anchor"], ver, _DOC_FILE if cls == "doc" else None)
            ver, anc, _ = _verifier_lint(ver, anc, _DOC_FILE if cls == "doc" else None)
        if ver == "human_claude":
            out[i] = None; meta[i] = (f"{ver}:{anc}", "")
            continue
        verdict, ev = run_verifier(ver, anc)
        out[i] = {"confirmed": True, "refuted": False}.get(verdict)   # undecidable → None 棄權
        meta[i] = (f"{ver}:{anc}"[:90], ev[:90])
    arm_engine.last_meta = meta
    return out


va_marker = object()


def score(tasks, verdicts):
    """逐類計分。回 {task_class: dict(n, correct, false_confirm, abstain, detail)}。"""
    by = {}
    for i, (cls, claim, truth) in enumerate(tasks):
        d = by.setdefault(cls, {"n": 0, "correct": 0, "false_confirm": 0, "abstain": 0, "detail": []})
        v = verdicts.get(i)
        d["n"] += 1
        if v is None:
            d["abstain"] += 1
        else:
            if v == truth:
                d["correct"] += 1
            if v is True and truth is False:
                d["false_confirm"] += 1
        m = getattr(arm_engine, "last_meta", {}).get(i)
        rec = {"claim": claim[:80], "truth": truth, "verdict": v}
        if m and verdicts is not va_marker:
            rec["anchor"], rec["evidence"] = m
        d["detail"].append(rec)
    return by


def run(n_per_class, model, timeout):
    tasks = build_tasks(n_per_class)
    git7 = _git7()
    print(f"造題 {len(tasks)}(每類 {n_per_class},半真半假)| model={model}")
    print("── A 臂 single_shot(裸問 qwen)──")
    va = arm_single_shot(tasks, model, timeout)
    globals()["va_marker"] = va
    sa = score(tasks, va)
    print("── B 臂 engine(qwen 寫錨→oracle 裁決)──")
    vb = arm_engine(tasks, model, timeout)
    sb = score(tasks, vb)
    with db.connect() as conn:
        cur = conn.cursor()
        for arm, s in (("single_shot", sa), ("engine", sb)):
            for cls, d in s.items():
                cur.execute("INSERT INTO deliberation_benchmark (arm, model_tag, task_class, n_tasks, "
                            "n_correct, n_false_confirm, n_abstain, detail, git_sha) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (arm, model, cls, d["n"], d["correct"], d["false_confirm"], d["abstain"],
                             json.dumps(d["detail"], ensure_ascii=False), git7))
        conn.commit()
    _print_verdict(sa, sb, model)
    return 0


def _tot(s, k):
    return sum(d[k] for d in s.values())


def _print_verdict(sa, sb, model):
    print(f"\n═══ 對照結果(model={model})═══")
    print(f"{'':14}{'n':>4}{'判對':>6}{'假確認':>8}{'棄權':>6}")
    for arm, s in (("single_shot", sa), ("engine", sb)):
        for cls, d in sorted(s.items()):
            print(f"{arm:<12}{cls:<6}{d['n']:>3}{d['correct']:>6}{d['false_confirm']:>8}{d['abstain']:>6}")
    na, nb = _tot(sa, "n"), _tot(sb, "n")
    fa, fb = _tot(sa, "false_confirm"), _tot(sb, "false_confirm")
    ca, cb = _tot(sa, "correct"), _tot(sb, "correct")
    ab_b = _tot(sb, "abstain")
    dec_b = nb - ab_b
    acc_a = ca / na if na else 0
    acc_b = cb / dec_b if dec_b else 0
    print(f"\n單發:準確 {ca}/{na}={acc_a:.0%} | 假確認 {fa}")
    print(f"引擎:裁決準確 {cb}/{dec_b}={acc_b:.0%}(棄權 {ab_b})| 假確認 {fb}")
    learned = (fb < fa) and (acc_b >= acc_a)
    print(f"習得裁決:{'✓ 成立(假確認 ' + str(fb) + '<' + str(fa) + ' 且裁決準確率不低於單發)' if learned else '✗ 未成立(誠實回前身「基本不建」檢討)'}")


def report():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT run_at::timestamp(0), arm, model_tag, sum(n_tasks), sum(n_correct), "
                    "sum(n_false_confirm), sum(n_abstain) FROM deliberation_benchmark "
                    "GROUP BY 1,2,3 ORDER BY 1 DESC LIMIT 8")
        for r in cur.fetchall():
            print(f"  {r[0]} {r[1]:<12} {r[2]:<10} n={r[3]} 對={r[4]} 假確認={r[5]} 棄權={r[6]}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--n-per-class", dest="npc", type=int, default=8)
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--timeout", type=float, default=600)
    args = ap.parse_args()
    if args.run:
        return run(args.npc, args.model, args.timeout)
    if args.report:
        report(); return 0
    print(__doc__.split("執行指令矩陣:")[1])
    print("歷史 run(唯讀):")
    report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
