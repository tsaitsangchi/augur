#!/usr/bin/env python
"""跨模一致率 — 4b vs 8b 同題 session 級對齊(D7;補完計畫 §4:從未同題對比之封閉)。

🎯 這支在做什麼(白話):同 topic+lens 各以兩模跑一 session,以 consensus.dedup_key(verifier+正規化
   anchor)對齊,落三個誠實指標:(i) 檢查集合 Jaccard(兩模「想驗什麼」像不像);(ii) 交集 key 之 status
   一致率(**同錨同 oracle 恆同=偏高屬預期,照實報不當成績**);(iii) escalate 率差(弱模湊不出合約錨
   的頻率差)。model-batched:先跑完全部 topic 之 A 模、再一次載 B 模(載入 ≤2 次/run);全批排 P3 過夜。

守 #9/#10(逐 key 對照 detail 落帳可重現)· #11(多 topic)· #28(全本地)· #29a。

執行指令矩陣:
  python scripts/compare_deliberation_models.py                    # 無參數:印矩陣+歷史摘要(唯讀)
  python scripts/compare_deliberation_models.py --run              # 預設 5 題 × (4b,8b)(model-batched;過夜級)
  python scripts/compare_deliberation_models.py --run --topics-file f.json --model-a qwen3:4b --model-b qwen3:8b
"""
import argparse
import json
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.deliberation import consensus, engine

_DEFAULT_TOPICS = [
    "驗證機率層三表(probability_oos_sample/probability_calibrator/prediction_probability)存在且非空",
    "驗證審議帳本核心表(deliberation_claim/deliberation_verdict/deliberation_session)存在",
    "驗證 feature_values 表至少 200 萬列且 model_registry 非空",
    "驗證知識層 knowledge_item 表存在且 knowledge_source 表至少 3000 列",
    "驗證 core_universe_asof 表存在且至少 10000 列",
]


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _session_keys(cur, sid):
    cur.execute("SELECT claim_text, assigned_verifier, anchor, status FROM deliberation_claim "
                "WHERE session_id=%s", (sid,))
    rows = [{"claim_text": t, "assigned_verifier": v, "anchor": a, "status": s}
            for t, v, a, s in cur.fetchall()]
    keys = {consensus.dedup_key(r): r["status"] for r in rows}
    esc = sum(1 for r in rows if r["status"] == "escalated") / len(rows) if rows else None
    return keys, esc


def run(topics, model_a, model_b, timeout):
    git7 = _git7()
    sess = {}                                                  # (model, i) → session_id;model-batched
    for model in (model_a, model_b):
        print(f"── {model}(model-batched)──")
        for i, topic in enumerate(topics):
            sid, _ = engine.deliberate(topic, "", "skeptic", model, 6, timeout)
            sess[(model, i)] = sid
    with db.connect() as conn:
        cur = conn.cursor()
        for i, topic in enumerate(topics):
            sa, sb = sess.get((model_a, i)), sess.get((model_b, i))
            if not sa or not sb:
                print(f"  ⚠ topic {i} 缺 session(a={sa},b={sb}),跳"); continue
            ka, ea = _session_keys(cur, sa)
            kb, eb = _session_keys(cur, sb)
            common = set(ka) & set(kb)
            union = set(ka) | set(kb)
            jac = len(common) / len(union) if union else 0.0
            agree = sum(1 for k in common if ka[k] == kb[k])
            detail = [{"key": list(k), "a": ka.get(k), "b": kb.get(k)} for k in sorted(union)]
            cur.execute(
                "INSERT INTO deliberation_model_agreement (topic, model_a, model_b, session_a, session_b, "
                "n_a, n_b, n_common, jaccard, n_agree, escalate_rate_a, escalate_rate_b, detail, git_sha) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (topic, model_a, model_b, sa, sb, len(ka), len(kb), len(common), round(jac, 4),
                 agree, ea, eb, json.dumps(detail, ensure_ascii=False), git7))
            conn.commit()
            print(f"  topic{i}: Jaccard={jac:.2f} 交集 {len(common)}(一致 {agree}) esc a={ea} b={eb}")
    return 0


def summary():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(DISTINCT topic), round(avg(jaccard),3), sum(n_agree), sum(n_common) "
                    "FROM deliberation_model_agreement")
        r = cur.fetchone()
        print(f"歷史:topics={r[0]} avg Jaccard={r[1]} 交集一致 {r[2]}/{r[3]}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--topics-file", dest="tf")
    ap.add_argument("--model-a", default="qwen3:4b")
    ap.add_argument("--model-b", default="qwen3:8b")
    ap.add_argument("--timeout", type=float, default=900)
    args = ap.parse_args()
    if args.run:
        topics = json.loads(open(args.tf).read()) if args.tf else _DEFAULT_TOPICS
        return run(topics, args.model_a, args.model_b, args.timeout)
    print(__doc__.split("執行指令矩陣:")[1])
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
