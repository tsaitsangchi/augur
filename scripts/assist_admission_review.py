#!/usr/bin/env python
"""ADM-AI-ASSIST 預審 — L2 本地 AI 建議（score＋reason＋audit）；approve／activate 永不由此執行。

🎯 這支在做什麼(白話):讀 proposed 來源／pending staging → L1 機械快篩旗標 → 本地
   Ollama(qwen3:4b) 產 recommend_score∈[0,1]＋reason＋flags → 寫入
   knowledge_admission_assist（actor=local_ai_v1）。**預設零寫（dry-run）**；
   --apply 才落帳本。本支永不 import／呼叫 curation.transition 升級；永不
   UPDATE approval_status。SRC-AUTO L-A／L-V 諮詢層合併本 writer（單一建議軌）。
守 #1/#15（分數非閘通過條件）· 憲章 v1.41.0（升級唯人）· #28（本地零 Claude）·
   #29（矩陣）· FZ-keep（零市場 API）· ADM-AI-ASSIST 計畫 §2／§5 S1。

執行指令矩陣:
  python scripts/assist_admission_review.py                      # 無參數:印矩陣＋池量（唯讀）
  python scripts/assist_admission_review.py --dry-run --limit 3   # 產分數樣本，零寫
  python scripts/assist_admission_review.py --dry-run --limit 3 --no-llm  # 啟發式樣本（Ollama 離線）
  python scripts/assist_admission_review.py --apply --limit 5    # 有界寫 assist＋source audit（禁升級）
  python scripts/assist_admission_review.py --selftest            # 純紅綠：禁 HUMAN_ONLY／禁 upgrade
  # S3 timer（systemd user；預設 dry-run；apply 須 install_services.sh --with-assist-apply）:
  #   systemctl --user start augur-admission-assist.service
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import _bootstrap  # noqa: F401

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b"
ACTOR = "local_ai_v1"
REASON_MAX = 400
PROMPT_VERSION = "adm_assist_v1"

SYSTEM = (
    "你是入庫預審助理。只輸出一行 JSON："
    '{"score":0.0到1.0,"reason":"≤80字中文","flags":{"hold_for_human":bool,'
    '"license_risk":bool,"dup_suspect":bool,"suggested_domain":""}}。'
    "score 高=較值得人優先審；你沒有放行權；有疑慮就 hold_for_human=true。"
)


def _pool_counts(cur):
    cur.execute("SELECT count(*) FROM knowledge_source WHERE approval_status='proposed'")
    n_src = int(cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM knowledge_staging WHERE status='pending'")
    n_stg = int(cur.fetchone()[0])
    cur.execute("SELECT to_regclass('public.knowledge_admission_assist')")
    has = cur.fetchone()[0] is not None
    n_assist = 0
    if has:
        cur.execute("SELECT count(*) FROM knowledge_admission_assist")
        n_assist = int(cur.fetchone()[0])
    return {"proposed": n_src, "pending_staging": n_stg, "assist_rows": n_assist, "assist_table": has}


def _load_candidates(cur, *, kind: str, limit: int):
    if kind == "source":
        cur.execute("""
            SELECT source_key, domain, adapter, protocol,
                   coalesce(license_regime,''), coalesce(est_scale::text,''),
                   left(coalesce(adapter_config::text,''), 240)
            FROM knowledge_source
            WHERE approval_status='proposed'
            ORDER BY source_key
            LIMIT %s""", (limit,))
        rows = []
        for k, dom, ada, proto, lic, est, cfg in cur.fetchall():
            rows.append({
                "target_kind": "source",
                "target_id": k,
                "summary": (f"source={k} domain={dom} adapter={ada} protocol={proto} "
                            f"license_regime={lic} est_scale={est} cfg={cfg}"),
                "meta": {"domain": dom, "adapter": ada, "protocol": proto, "license_regime": lic},
            })
        return rows
    cur.execute("""
        SELECT staging_id::text, coalesce(source_key,''), coalesce(status,''),
               coalesce(domain,''), coalesce(entity_type,''),
               left(coalesce(payload::text,''), 280),
               left(coalesce(source_url,''), 120)
        FROM knowledge_staging
        WHERE status='pending'
        ORDER BY staging_id
        LIMIT %s""", (limit,))
    rows = []
    for sid, sk, st, dom, et, payload, url in cur.fetchall():
        rows.append({
            "target_kind": "staging",
            "target_id": sid,
            "summary": (f"staging_id={sid} source_key={sk} status={st} domain={dom} "
                        f"entity_type={et} url={url} payload={payload}"),
            "meta": {"source_key": sk, "status": st, "domain": dom},
        })
    return rows


def _l1_flags(meta: dict, kind: str) -> dict:
    """L1 機械快篩旗標（零 LLM）；不過關只標旗，不冒充通過。"""
    flags = {"l1_ok": True, "l1_notes": []}
    if kind == "source":
        if not meta.get("domain"):
            flags["l1_ok"] = False
            flags["l1_notes"].append("missing_domain")
        if not meta.get("adapter"):
            flags["l1_ok"] = False
            flags["l1_notes"].append("missing_adapter")
        if (meta.get("license_regime") or "") in ("", "unknown", "null"):
            flags["l1_notes"].append("license_regime_empty")
    else:
        if not meta.get("source_key"):
            flags["l1_ok"] = False
            flags["l1_notes"].append("staging_no_source_key")
    return flags


def _heuristic_score(summary: str, l1: dict) -> dict:
    """Ollama 離線／--no-llm：決定性啟發式（非裁決；僅排隊輔助）。"""
    s = summary.lower()
    score = 0.45
    flags = {
        "hold_for_human": True,
        "license_risk": "nc" in s or "nd" in s or "all rights" in s,
        "dup_suspect": False,
        "suggested_domain": "",
        "mode": "heuristic",
    }
    if "public" in s or "cc-by" in s or "cc0" in s:
        score += 0.2
        flags["license_risk"] = False
    if "ai_generated" in s or "chatgpt" in s:
        score -= 0.3
        flags["hold_for_human"] = True
        flags["license_risk"] = True
    if not l1.get("l1_ok"):
        score -= 0.15
        flags["hold_for_human"] = True
    score = max(0.0, min(1.0, round(score, 3)))
    reason = ("啟發式預審：L1=" + ("ok" if l1.get("l1_ok") else "弱")
              + ("；license 風險" if flags["license_risk"] else "")
              + "；待人裁（AI 無放行權）")
    return {"score": score, "reason": reason[:REASON_MAX], "flags": flags}


def _ask_ollama(prompt: str, timeout: int = 90) -> str:
    body = {
        "model": MODEL,
        "prompt": prompt,
        "system": SYSTEM,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 220},
    }
    req = urllib.request.Request(
        OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"]


def _parse_llm_json(text: str) -> dict | None:
    # 取最外層 JSON 物件（允許 flags 巢狀）
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        obj = json.loads(text[start: end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or "score" not in obj:
        return None
    try:
        score = float(obj["score"])
    except (TypeError, ValueError):
        return None
    score = max(0.0, min(1.0, score))
    reason = str(obj.get("reason") or "")[:REASON_MAX]
    flags = obj.get("flags") if isinstance(obj.get("flags"), dict) else {}
    flags.setdefault("hold_for_human", True)
    flags["mode"] = "ollama"
    return {"score": score, "reason": reason or "（無理由）", "flags": flags}


def _score_one(cand: dict, *, use_llm: bool) -> dict:
    l1 = _l1_flags(cand["meta"], cand["target_kind"])
    prompt = f"候選:\n{cand['summary']}\nL1={json.dumps(l1, ensure_ascii=False)}"
    ph = hashlib.sha256((PROMPT_VERSION + prompt).encode()).hexdigest()[:16]
    if use_llm:
        try:
            raw = _ask_ollama(prompt)
            parsed = _parse_llm_json(raw)
            if parsed:
                parsed["flags"] = {**l1, **parsed["flags"]}
                parsed["model"] = MODEL
                parsed["prompt_hash"] = ph
                return parsed
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            h = _heuristic_score(cand["summary"], l1)
            h["flags"]["llm_error"] = type(e).__name__
            h["flags"] = {**l1, **h["flags"]}
            h["model"] = f"heuristic_fallback:{MODEL}"
            h["prompt_hash"] = ph
            return h
    h = _heuristic_score(cand["summary"], l1)
    h["flags"] = {**l1, **h["flags"]}
    h["model"] = "heuristic"
    h["prompt_hash"] = ph
    return h


def _write_assist(cur, cand: dict, scored: dict) -> None:
    cur.execute("""
        INSERT INTO knowledge_admission_assist
          (target_kind, target_id, score, reason, flags, actor, model, prompt_hash)
        VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s)""",
                (cand["target_kind"], cand["target_id"], scored["score"], scored["reason"],
                 json.dumps(scored["flags"], ensure_ascii=False), ACTOR,
                 scored.get("model"), scored.get("prompt_hash")))


def _write_source_audit(cur, cand: dict, scored: dict) -> bool:
    """S2: assist 建議另留 source review_log，方便 /gov 唯讀掃視；永不改狀態。"""
    source_key = cand["target_id"] if cand["target_kind"] == "source" else cand["meta"].get("source_key")
    if not source_key:
        return False
    cur.execute("SELECT approval_status FROM knowledge_source WHERE source_key=%s", (source_key,))
    row = cur.fetchone()
    if not row:
        return False
    old = new = row[0]
    reason = json.dumps({
        "target_kind": cand["target_kind"],
        "target_id": cand["target_id"],
        "recommend_score": scored["score"],
        "reason": scored["reason"],
        "flags": scored["flags"],
        "model": scored.get("model"),
        "prompt_hash": scored.get("prompt_hash"),
    }, ensure_ascii=False)
    cur.execute("""
        INSERT INTO knowledge_source_review_log
          (source_key, action, old_status, new_status, actor, os_user, reason, probe_result)
        VALUES (%s,'assist',%s,%s,%s,%s,%s,NULL)""",
                (source_key, old, new, ACTOR, ACTOR, reason))
    return True


def _assert_no_upgrade_in_source():
    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    skip = {"selftest", "_assert_no_upgrade_in_source"}

    class V(ast.NodeVisitor):
        def __init__(self):
            self.bad = []
            self._skip = 0

        def visit_FunctionDef(self, node):
            if node.name in skip:
                self._skip += 1
                self.generic_visit(node)
                self._skip -= 1
                return
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            if self._skip == 0:
                name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if name == "transition":
                    self.bad.append(("transition", node.lineno))
            self.generic_visit(node)

    v = V()
    v.visit(tree)
    if v.bad:
        raise AssertionError(f"禁 upgrade 呼叫: {v.bad}")
    # 只掃字串常數中的 SQL（避開本函式／selftest 說明文字誤傷）
    sqlish = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            sqlish.append(node.value)
        elif isinstance(node, ast.JoinedStr):
            for vpart in node.values:
                if isinstance(vpart, ast.Constant) and isinstance(vpart.value, str):
                    sqlish.append(vpart.value)
    blob = "\n".join(sqlish)
    if re.search(r"UPDATE\s+knowledge_source", blob, re.I):
        raise AssertionError("禁對 knowledge_source 做 UPDATE")
    if re.search(r"SET\s+approval_status\s*=", blob, re.I):
        raise AssertionError("禁 SET 審批態")
    return True


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    from augur.knowledge.curation import HUMAN_ONLY, transition

    chk("HUMAN_ONLY 含 approve/activate", {"approve", "activate"} <= HUMAN_ONLY)
    raised = False
    try:
        transition("nonexistent_source_adm_assist_probe", "approve", "adm_assist", system=True)
    except PermissionError:
        raised = True
    except Exception:
        raised = False
    chk("system+approve → PermissionError", raised)

    try:
        _assert_no_upgrade_in_source()
        chk("本檔執行路徑無 transition／approval_status 寫入", True)
    except AssertionError as e:
        chk(f"本檔執行路徑無 upgrade ({e})", False)

    h = _heuristic_score("source=demo domain=philosophy license_regime=cc-by",
                         {"l1_ok": True, "l1_notes": []})
    chk("啟發式 score∈[0,1]", 0.0 <= h["score"] <= 1.0)
    chk("啟發式 hold_for_human", h["flags"].get("hold_for_human") is True)
    chk("ACTOR=local_ai_v1", ACTOR == "local_ai_v1")
    chk("MODEL=qwen3:4b", MODEL == "qwen3:4b")

    parsed = _parse_llm_json('雜訊 {"score":0.7,"reason":"可審","flags":{"hold_for_human":true}} 尾')
    chk("LLM JSON 解析", parsed is not None and abs(parsed["score"] - 0.7) < 1e-6)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ADM-AI-ASSIST L2 預審（禁 approve/activate）")
    ap.add_argument("--dry-run", action="store_true", help="產分數樣本，零寫（預設安全）")
    ap.add_argument("--apply", action="store_true", help="寫入 knowledge_admission_assist（有界）")
    ap.add_argument("--limit", type=int, default=5, help="每池上限（預設 5）")
    ap.add_argument("--kind", choices=("source", "staging", "both"), default="both")
    ap.add_argument("--no-llm", action="store_true", help="跳過 Ollama，只用啟發式")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not (args.dry_run or args.apply):
        print(__doc__)
        print("預設安全：無 --dry-run／--apply 只印矩陣；approve／activate 永不由此支執行。")
        try:
            from augur.core import db
            with db.connect() as conn:
                pools = _pool_counts(conn.cursor())
            print(f"池量（唯讀）: proposed={pools['proposed']} pending_staging={pools['pending_staging']} "
                  f"assist_rows={pools['assist_rows']} table={'yes' if pools['assist_table'] else 'no'}")
        except Exception as e:
            print(f"(池量暫不可讀: {type(e).__name__}: {e})")
        return 0

    if args.apply and args.dry_run:
        print("✗ --apply 與 --dry-run 互斥", file=sys.stderr)
        return 2

    from augur.core import db

    use_llm = not args.no_llm
    kinds = ["source", "staging"] if args.kind == "both" else [args.kind]

    with db.connect() as conn:
        cur = conn.cursor()
        pools = _pool_counts(cur)
        print(f"池量: proposed={pools['proposed']} pending_staging={pools['pending_staging']} "
              f"assist_table={'yes' if pools['assist_table'] else 'no'}")
        if args.apply and not pools["assist_table"]:
            print("✗ 缺表：先 python scripts/migrate_admission_assist_ddl.py --apply", file=sys.stderr)
            return 1

        results = []
        audit_rows = 0
        for kind in kinds:
            cands = _load_candidates(cur, kind=kind, limit=args.limit)
            for cand in cands:
                scored = _score_one(cand, use_llm=use_llm)
                results.append((cand, scored))
                print(f"[{cand['target_kind']}] {cand['target_id']} "
                      f"score={scored['score']:.3f} model={scored.get('model')} "
                      f"reason={scored['reason'][:80]}")
                if args.apply:
                    _write_assist(cur, cand, scored)
                    if _write_source_audit(cur, cand, scored):
                        audit_rows += 1
        if args.apply:
            conn.commit()
            print(f"✓ 已寫 assist={len(results)} 列、source_audit={audit_rows} 列"
                  f"（actor={ACTOR}；未觸升級）")
        else:
            print(f"dry-run 樣本 {len(results)} 筆（零寫）；人裁仍走 "
                  "review_knowledge_source.py --approve/--activate（TTY）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
