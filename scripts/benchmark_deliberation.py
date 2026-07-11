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
  python scripts/benchmark_deliberation.py --run              # adhoc:24 題×兩臂,qwen3:4b(傳統對照)
  python scripts/benchmark_deliberation.py --run --n-per-class 4 --model qwen3:8b
  python scripts/benchmark_deliberation.py --report           # 歷史 run 摘要
  python scripts/benchmark_deliberation.py --preregister      # B2 GATE:先凍結判準快照(門檻/口徑/seeds)
  python scripts/benchmark_deliberation.py --gate gate_XXXX   # 開跑三臂×3題集seed(run/task 承載,resume-safe,過夜級)
  python scripts/benchmark_deliberation.py --report-gate gate_XXXX  # 斷言快照+三判準+McNemar 合併 p
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
                 "deliberation_claimz", "probability_calibrators", "core_universe_v2", "lexicon_knowledge"]   # core_universe 真存在=素材 bug(GATE 首跑 2026-07-11),換真缺名
_QUANT_TABLES = ["feature_values", "probability_oos_sample", "knowledge_item", "prediction_values",
                 "knowledge_lexicon", "model_registry", "probability_calibrator", "prediction_probability",
                 "knowledge_source", "deliberation_verdict"]   # B2:8→10(information_schema 實查追加,§2.2 題量)
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


def build_tasks(n_per_class, seed=None):
    """造題:每類 n 條(半真半假);真值即時機械確立。回 [(task_class, claim_text, truth)]。
    B2/P-1:seed=題集抽樣 seed(以 random.Random(seed) 抽樣/排列題庫;非解碼 seed——temperature=0
    貪婪解碼下解碼 seed 為 no-op,重複軸=題目抽樣才統計真實);seed=None → 傳統定序(相容既有 --run)。"""
    import random
    rng = random.Random(seed) if seed is not None else None
    k = n_per_class // 2

    def pick(pool, m):
        return rng.sample(pool, min(m, len(pool))) if rng else pool[:m]

    tasks = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in pick(_SCHEMA_TRUE, k):
            cur.execute("SELECT to_regclass('public.'||%s) IS NOT NULL", (t,))
            assert cur.fetchone()[0], f"素材失效:{t!r} 不存在(更新 _SCHEMA_TRUE)"   # 真值機械驗證(GATE 首跑教訓)
            tasks.append(("schema", f"資料表 {t} 存在於本專案 PostgreSQL public schema", True))
        for t in pick(_SCHEMA_FALSE, k):
            cur.execute("SELECT to_regclass('public.'||%s) IS NULL", (t,))
            assert cur.fetchone()[0], f"素材失效:{t!r} 竟存在(更新 _SCHEMA_FALSE;core_universe 前例)"
            tasks.append(("schema", f"資料表 {t} 存在於本專案 PostgreSQL public schema", False))
        for i, t in enumerate(pick(_QUANT_TABLES, n_per_class)):
            cur.execute(f"SELECT count(*) FROM {t}")
            actual = cur.fetchone()[0]
            if i % 2 == 0:   # 真:實際數的下界
                thr = max(1, int(actual * 0.5))
                tasks.append(("quant", f"資料表 {t} 至少有 {thr} 列", True))
            else:            # 假:實際數的兩倍+10
                thr = actual * 2 + 10
                tasks.append(("quant", f"資料表 {t} 至少有 {thr} 列", False))
    text = (REPO / _DOC_FILE).read_text(encoding="utf-8", errors="replace")
    for s in pick(_DOC_TRUE, k):
        assert s in text, f"素材失效:{s!r} 不在 {_DOC_FILE}(更新素材)"
        tasks.append(("doc", f"檔案 {_DOC_FILE} 內含字串「{s}」", True))
    for s in pick(_DOC_FALSE, k):
        assert s not in text, f"素材失效:{s!r} 竟在 {_DOC_FILE}"
        tasks.append(("doc", f"檔案 {_DOC_FILE} 內含字串「{s}」", False))
    if rng:
        rng.shuffle(tasks)   # 排列亦入抽樣軸
    return tasks


def arm_single_shot(tasks, model, timeout, think=False, num_predict=2000):
    """單發臂:qwen 直判真偽(LLM 意見;無棄權選項=其真實使用形態)。回 {idx: bool}。
    think=False → 批式一 call(single_fast 傳統形態);think=True → **逐題 call+try/except**
    (§2.2 判準5:num_predict=4096 思考+答案預算、單題失敗=缺該 idx=計錯,臂不整臂死)。"""
    from augur.advisor.ollama import make_structured_llm_fn
    if not think:
        schema = {"type": "object", "properties": {"verdicts": {"type": "array", "items": {
            "type": "object", "properties": {"idx": {"type": "integer"}, "is_true": {"type": "boolean"}},
            "required": ["idx", "is_true"]}}}, "required": ["verdicts"]}
        listing = "\n".join(f"{i}. {c}" for i, (_, c, _t) in enumerate(tasks))
        fn = make_structured_llm_fn(schema, model=model, timeout=timeout, retries=1,
                                    options={"temperature": 0, "num_predict": num_predict})
        out = fn("逐條判斷下列關於本專案(augur,台股量化系統)的宣稱是否為真。對每條回 idx 與 is_true:\n" + listing)
        return {int(v["idx"]): bool(v["is_true"]) for v in out.get("verdicts", [])}
    schema1 = {"type": "object", "properties": {"is_true": {"type": "boolean"}}, "required": ["is_true"]}
    fn = make_structured_llm_fn(schema1, model=model, timeout=timeout, retries=1, think=True,
                                options={"temperature": 0, "num_predict": num_predict})
    out = {}
    for i, (_, c, _t) in enumerate(tasks):
        try:
            out[i] = bool(fn(f"判斷此關於本專案(augur,台股量化系統)的宣稱是否為真,回 is_true:\n{c}")["is_true"])
        except Exception as e:                                  # 逐題 try/except:單題失敗=缺 idx=計錯
            print(f"    (think 臂第 {i} 題失敗:{type(e).__name__})")
    return out


_ANCHOR_SCHEMA = {"type": "object", "properties": {
    "assigned_verifier": {"type": "string", "enum": ["information_schema", "db_query", "file_grep", "human_claude"]},
    "anchor": {"type": "string"}}, "required": ["assigned_verifier", "anchor"]}

_ENGINE_CONTRACT = """把下列宣稱轉成一個可機械驗證的檢查。anchor 只放參數本身:
- information_schema:驗表存在。anchor="表名"(如 "feature_values")
- db_query:量比較。anchor="SELECT 單標量 => 比較子 數值"(如 "SELECT count(*) FROM t => >= 10")
- file_grep:檔內字串。anchor="路徑::字串"(如 "CLAUDE.md::換機接續")
無法機驗 → human_claude。只輸出 JSON。
宣稱:{claim}"""


def arm_engine(tasks, model, timeout, rules=None):
    """engine 臂:qwen 寫錨(L1 grounding+L2 lint 沿用引擎同一支)→ oracle 裁決;undecidable/human=棄權。
    回 {idx: True/False/None(棄權)}。rules:GATE 模式**必傳生產 config rules**(§2.2 判準6:GATE 驗的
    引擎=生產引擎);None → RULES_ALL(既有 --run 相容)。"""
    from augur.advisor.ollama import make_structured_llm_fn
    sys.path.insert(0, str(REPO / "scripts"))
    from augur.deliberation.anchors import fast_anchor as _fast_anchor, normalize_anchor as _normalize_anchor, schema_grounding as _schema_grounding, verifier_lint as _verifier_lint   # #12 單一住所
    fn = make_structured_llm_fn(_ANCHOR_SCHEMA, model=model, timeout=timeout, retries=1,
                                options={"temperature": 0, "num_predict": 300})
    out, meta = {}, {}
    for i, (cls, claim, _t) in enumerate(tasks):
        fp = _fast_anchor(claim, _DOC_FILE if cls == "doc" else None, rules)   # 快路(GATE=生產 rules)
        if fp:
            ver, anc, _rid = fp
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


# ═══ P0-B2 GATE-lite(補完計畫 §2.2):預註冊→開跑→報告,事後不得挪門柱 ═══════════
GATE_ARMS = ("single_fast", "single_think", "engine")
GATE_SEEDS = (41, 42, 43)          # 題集抽樣 seed(P-1:非解碼 seed)
GATE_MIN_PP = 15                    # 判準1:engine vs 最佳非引擎臂 median acc 增量 ≥ +15pp(P-3 不挪)
GATE_ALPHA = 0.05                   # 判準3:McNemar 合併(3輪90題)p 門檻


def mcnemar_exact(b, c):
    """McNemar 精確雙尾(math.comb 二項尾機率,零新依賴):b/c=不一致對數。b=c→1.0;b=0,c=13→≈2.44e-4。"""
    import math
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


def _bank_version():
    """題庫版本 hash(素材清單正規化 sha;入快照,開跑後不得改素材)。"""
    import hashlib
    blob = json.dumps([_SCHEMA_TRUE, _SCHEMA_FALSE, _QUANT_TABLES, _DOC_TRUE, _DOC_FALSE, _DOC_FILE],
                      ensure_ascii=False, sort_keys=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def _prod_rules(cur):
    from augur.deliberation import engine_config
    return engine_config.load_rules(cur)


def preregister(model, npc=10):
    """先凍結:寫 bench_batch 快照列(臂集/門檻/口徑/seeds/題量/think 規格/rules sha/題庫版本)。"""
    import uuid as _uuid
    with db.connect() as conn:
        cur = conn.cursor()
        rules, sha = _prod_rules(cur)
        cfg = {"arms": list(GATE_ARMS), "model": model, "n_per_class": npc, "seeds": list(GATE_SEEDS),
               "thresholds": {"min_pp_gain": GATE_MIN_PP, "fc_rule": "engine_fc<=min(other)逐輪且彙總",
                              "mcnemar_alpha": GATE_ALPHA, "mcnemar_scope": "pooled_3rounds"},
               "scoring": "case_acc=n_correct/n_total;abstain=計錯分母不縮;McNemar 對子=逐題判對布林(abstain=錯)",
               "think_spec": {"num_predict": 4096, "timeout": 900, "per_question_try_except": True},
               "rules_config_sha": sha, "bank_version": _bank_version()}
        bid = f"gate_{_uuid.uuid4().hex[:12]}"
        cur.execute("INSERT INTO deliberation_bench_batch (batch_id, purpose, arm_config, git_sha) "
                    "VALUES (%s,'gate',%s,%s)", (bid, json.dumps(cfg, ensure_ascii=False), _git7()))
        conn.commit()
    print(f"✓ 預註冊 batch={bid}(門檻/口徑/seeds 已凍結;開跑後不得挪)")
    print(f"  rules_sha={sha} bank={cfg['bank_version']} → 下一步:--gate {bid}")
    return 0


def gate_run(batch_id, timeout):
    """開跑:三臂 × 3 題集 seed,經模式 10 run/task 帳本(每 task=一 (seed,arm);kill-resume 安全)。"""
    from augur.deliberation import ledger
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT arm_config FROM deliberation_bench_batch WHERE batch_id=%s AND purpose='gate'", (batch_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ 快照缺失:{batch_id} 未預註冊(先 --preregister)"); return 1
        cfg = row[0]
        rules, sha = _prod_rules(cur)
        if sha != cfg["rules_config_sha"]:
            print(f"✗ 生產 rules sha 已變({sha} != 快照 {cfg['rules_config_sha']}):GATE 驗的引擎≠生產引擎,拒跑"); return 1
        if _bank_version() != cfg["bank_version"]:
            print(f"✗ 題庫素材已變(bank {_bank_version()} != 快照 {cfg['bank_version']}):不得開跑後改題庫"); return 1
        plan = [{"seed": s, "arm": a} for s in cfg["seeds"] for a in cfg["arms"]]
        rid = ledger.create_run(cur, f"gate:{batch_id}", plan)
        ledger.resume_reset(cur, rid)
        conn.commit()
        print(f"GATE 開跑 batch={batch_id} run={rid}({len(plan)} task;resume-safe)")
        ts = cfg["think_spec"]
        while True:
            t = ledger.next_task(cur, rid)
            conn.commit()
            if not t:
                break
            tid, seq, payload = t
            s, arm = payload["seed"], payload["arm"]
            print(f"── task {seq + 1}/{len(plan)}: arm={arm} seed={s} ──", flush=True)
            try:
                tasks = build_tasks(cfg["n_per_class"], seed=s)
                if arm == "single_fast":
                    v = arm_single_shot(tasks, cfg["model"], timeout, think=False)
                elif arm == "single_think":
                    v = arm_single_shot(tasks, cfg["model"], ts["timeout"], think=True,
                                        num_predict=ts["num_predict"])
                else:
                    v = arm_engine(tasks, cfg["model"], timeout, rules=rules)
                sc = score(tasks, v)
                for cls, d in sc.items():
                    cur.execute("INSERT INTO deliberation_benchmark (arm, model_tag, task_class, n_tasks, "
                                "n_correct, n_false_confirm, n_abstain, detail, git_sha, batch_id, seed) "
                                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (arm, cfg["model"], cls, d["n"], d["correct"], d["false_confirm"], d["abstain"],
                                 json.dumps(d["detail"], ensure_ascii=False), _git7(), batch_id, s))
                ledger.mark_task(cur, tid, "done")
            except Exception as e:
                print(f"  ✗ task 失敗:{type(e).__name__}: {str(e)[:120]}")
                ledger.mark_task(cur, tid, "failed")
            conn.commit()
        st = ledger.finish_run(cur, rid)
        conn.commit()
    print(f"GATE run {rid} → {st};下一步:--report-gate {batch_id}")
    return 0 if st == "completed" else 1


def _gate_rows(cur, batch_id):
    cur.execute("SELECT arm, seed, sum(n_tasks), sum(n_correct), sum(n_false_confirm), sum(n_abstain), "
                "min(run_at) FROM deliberation_benchmark WHERE batch_id=%s GROUP BY arm, seed", (batch_id,))
    return cur.fetchall()


def _pair_bools(cur, batch_id, arm, seed):
    """逐題判對布林(abstain=錯;detail 依 (task_class, claim) 排序穩定配對)。"""
    cur.execute("SELECT task_class, detail FROM deliberation_benchmark WHERE batch_id=%s AND arm=%s AND seed=%s",
                (batch_id, arm, seed))
    out = {}
    for cls, det in cur.fetchall():
        for rec in det:
            out[(cls, rec["claim"])] = (rec["verdict"] is not None and rec["verdict"] == rec["truth"])
    return out


def report_gate(batch_id):
    """讀快照斷言(缺失/挪門柱/rules 漂移=exit 1)→ 三判準逐項 pass/fail + McNemar 合併 p(+逐輪照實)。"""
    import statistics
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT arm_config, preregistered_at FROM deliberation_bench_batch "
                    "WHERE batch_id=%s AND purpose='gate'", (batch_id,))
        row = cur.fetchone()
        if not row:
            print(f"✗ 快照缺失:{batch_id}"); return 1
        cfg, prereg_at = row
        _r, sha = _prod_rules(cur)
        if sha != cfg["rules_config_sha"]:
            print(f"✗ rules sha 不符(生產 {sha} != 快照 {cfg['rules_config_sha']})"); return 1
        rows = _gate_rows(cur, batch_id)
        if not rows:
            print("✗ 無 GATE 結果列(先 --gate)"); return 1
        if not all(prereg_at < r[6] for r in rows):
            print("✗ preregistered_at ≥ min(run_at):非先凍結後開跑"); return 1
        acc, fc = {}, {}
        for arm, s, n, cor, f, ab, _ in rows:
            acc.setdefault(arm, {})[s] = cor / n          # 口徑:分母=全題(abstain 計錯)
            fc.setdefault(arm, {})[s] = f
        med = {a: statistics.median(v.values()) for a, v in acc.items()}
        others = [a for a in med if a != "engine"]
        best = max(others, key=lambda a: med[a])
        gain_pp = (med["engine"] - med[best]) * 100
        c1 = gain_pp >= cfg["thresholds"]["min_pp_gain"]
        c2 = all(fc["engine"][s] <= min(fc[a][s] for a in others) for s in fc["engine"]) and \
            sum(fc["engine"].values()) <= min(sum(fc[a].values()) for a in others)
        b = c = 0
        per_round_p = []
        for s in sorted(acc["engine"]):
            eb, ob = _pair_bools(cur, batch_id, "engine", s), _pair_bools(cur, batch_id, best, s)
            rb = sum(1 for k in eb if not eb[k] and ob.get(k))
            rc = sum(1 for k in eb if eb[k] and not ob.get(k, True))
            b += rb; c += rc
            per_round_p.append((s, mcnemar_exact(rb, rc)))
        p_pooled = mcnemar_exact(b, c)
        c3 = p_pooled < cfg["thresholds"]["mcnemar_alpha"]
        print(f"═══ GATE 報告 batch={batch_id}(門檻讀自快照,非 code 常數)═══")
        print(f"  median acc:engine={med['engine']:.1%} vs 最佳非引擎 {best}={med[best]:.1%} → 增量 {gain_pp:+.1f}pp"
              f"(門檻 +{cfg['thresholds']['min_pp_gain']}pp){' ✓' if c1 else ' ✗'}")
        print(f"  假確認:engine={sum(fc['engine'].values())} vs 各臂 min={min(sum(fc[a].values()) for a in others)}"
              f"{' ✓' if c2 else ' ✗'}")
        print(f"  McNemar(vs {best}):合併 b={b} c={c} p={p_pooled:.2e}(α={cfg['thresholds']['mcnemar_alpha']})"
              f"{' ✓' if c3 else ' ✗'} | 逐輪照實:{[(s, f'{p:.3f}') for s, p in per_round_p]}")
        ok = c1 and c2 and c3
        print(f"  ═> GATE {'PASS:engine 效力預註冊成立' if ok else 'FAIL:engine 效力維持 experimental(不改門柱重跑;重跑=新 batch 新預註冊)'}")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--preregister", action="store_true")
    ap.add_argument("--gate", metavar="BATCH_ID")
    ap.add_argument("--report-gate", dest="report_gate_id", metavar="BATCH_ID")
    ap.add_argument("--n-per-class", dest="npc", type=int, default=8)
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--timeout", type=float, default=600)
    args = ap.parse_args()
    if args.preregister:
        return preregister(args.model, npc=10)
    if args.gate:
        return gate_run(args.gate, args.timeout)
    if args.report_gate_id:
        return report_gate(args.report_gate_id)
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
