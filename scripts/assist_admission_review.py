#!/usr/bin/env python
"""ADM-AI-ASSIST 預審 — L2 本地 AI 建議（score＋reason＋audit）；approve／activate 永不由此執行。

🎯 這支在做什麼(白話):讀 proposed 來源／pending staging → L1 機械快篩旗標 → 本地
   Ollama(qwen3:4b) 產 recommend_score∈[0,1]＋reason＋flags → 寫入
   knowledge_admission_assist（actor=local_ai_v1）。**預設零寫（dry-run）**；
   --apply 才落帳本。本支永不 import／呼叫 curation.transition 升級；永不
   UPDATE approval_status。SRC-AUTO L-A／L-V 諮詢層合併本 writer（單一建議軌）。
守 #1/#15（分數非閘通過條件）· 憲章 v1.48.0（一律准入；本檔仍只寫 assist 建議、不代升格）· #28（本地零 Claude）·
   #29（矩陣）· FZ-keep（零市場 API）· ADM-AI-ASSIST 計畫 §2／§5 S1。

**2026-07-30 Steward 兩項拍板**：
  ① **逾時 90 → 9000 秒**（`LLM_TIMEOUT_SEC`）——原 90s 於本機（CPU-only）實測必逾時
     （`_ask_ollama` 90.3s TimeoutError），連鎖成「啟發式 fallback → 無法判斷 →
     hold_for_human → **待人裁**」。故「待人裁」原是**逾時產物、非治權結果**。
  ② **dry-run 亦留「執行事實」**（`admission_assist_run`，run 級非審批級）——
     今日 05:00 timer 跑 58 分鐘、exit 0 卻零留痕，致無法分辨
     「沒東西可審」與「根本沒跑」。**「零寫」指零寫審批，非零留執行痕跡。**

執行指令矩陣:
  python scripts/assist_admission_review.py                      # 無參數:印矩陣＋池量（唯讀）
  python scripts/assist_admission_review.py --dry-run --limit 3   # 產分數樣本，零寫
  python scripts/assist_admission_review.py --dry-run --limit 3 --no-llm  # 啟發式樣本（Ollama 離線）
  python scripts/assist_admission_review.py --apply --limit 5    # 有界寫 assist＋source audit（禁升級）
  python scripts/assist_admission_review.py --dry-run --limit 1 --llm-timeout 60  # 當次覆寫逾時
  python scripts/assist_admission_review.py --dry-run --limit 3 --no-run-ledger    # 除錯：不留執行事實
  python scripts/assist_admission_review.py --dry-run --limit 20 --max-wall-sec 3600  # 有界：總時限 1 小時
  python scripts/assist_admission_review.py --selftest            # 純紅綠：本檔不寫 upgrade
  # 看執行事實（run 級帳本；dry-run 亦留痕）:
  #   psql -d augur -c "SELECT run_id,mode,outcome,examined,llm_ok,llm_fallback,
  #     round(elapsed_sec) el,latency_median_sec FROM admission_assist_run
  #     ORDER BY started_at DESC LIMIT 10"
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
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import _bootstrap  # noqa: F401

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b"
ACTOR = "local_ai_v1"
REASON_MAX = 400
PROMPT_VERSION = "adm_assist_v1"

# 本地 LLM 逾時（秒）。**Steward 拍板 2026-07-30：90 → 9000**。
# 起因（實證，非推測）：`_ask_ollama` 在本機（CPU-only i5-10500、無獨顯）實測
# **90.3s TimeoutError**；且 `think` 早已為 False、`num_predict=220`，故非 thinking 拖累，
# 是 CPU 推論本身就慢。原 90s 之連鎖後果＝逾時→啟發式 fallback→無法判斷→
# `hold_for_human=True` ⇒ 印出「待人裁」。**故「待人裁」原為逾時產物、非治權結果**，
# 本地 AI 從未答成過一次。放寬後方能讓「本地 AI 對原文語意之基本理解」真正產生。
# 承 #27：此為 operational 值、得逐級逼近；真實延遲由 `admission_assist_run` 帳本量出，
# 不憑估算寫死判準。可以 `--llm-timeout` 當次覆寫。
LLM_TIMEOUT_SEC = 9000

# ── 執行事實帳本（Steward 拍板 2026-07-30「讓 dry-run 也留一筆執行事實」）──
# 起因：`augur-admission-assist.timer` 今日 05:00 觸發、跑 **58 分鐘**、exit 0/SUCCESS，
# 卻因單元為 `--dry-run` 而**零留痕** ⇒ 問「今天為什麼沒有審批稽核軌跡」時，
# **無法分辨「沒東西可審」與「根本沒跑」**——過程黑箱，違 #21「不靜默」。
# 本帳本為 **run 級（非審批級）**：記跑了幾筆、耗時、延遲分佈、分數分佈、
# LLM 成功/fallback 計數、池量快照。**不含任何放行語意**，故 dry-run 寫它
# 不違「預設零寫（dry-run）」之本意——零寫指**零寫審批**，非零留執行痕跡。
RUN_LEDGER = "admission_assist_run"
RUN_LEDGER_DDL = f"""
CREATE TABLE IF NOT EXISTS {RUN_LEDGER} (
    run_id           TEXT PRIMARY KEY,
    mode             TEXT NOT NULL CHECK (mode IN ('dry-run','apply')),
    actor            TEXT NOT NULL,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at      TIMESTAMPTZ,
    elapsed_sec      NUMERIC(12,3),
    outcome          TEXT NOT NULL DEFAULT 'running'
                     CHECK (outcome IN ('running','completed','failed')),
    kind             TEXT NOT NULL,
    limit_n          INTEGER NOT NULL,
    use_llm          BOOLEAN NOT NULL,
    model            TEXT NOT NULL,
    prompt_version   TEXT NOT NULL,
    llm_timeout_sec  INTEGER NOT NULL,
    examined         INTEGER NOT NULL DEFAULT 0,
    llm_ok           INTEGER NOT NULL DEFAULT 0,
    llm_fallback     INTEGER NOT NULL DEFAULT 0,
    heuristic_only   INTEGER NOT NULL DEFAULT 0,
    score_min        NUMERIC(6,4),
    score_median     NUMERIC(6,4),
    score_max        NUMERIC(6,4),
    latency_median_sec NUMERIC(12,3),
    latency_max_sec  NUMERIC(12,3),
    pool_proposed    INTEGER,
    pool_pending_staging INTEGER,
    assist_written   INTEGER NOT NULL DEFAULT 0,
    audit_written    INTEGER NOT NULL DEFAULT 0,
    error            TEXT,
    detail           JSONB NOT NULL DEFAULT '{{}}'::jsonb
);
CREATE INDEX IF NOT EXISTS adm_assist_run_started_idx ON {RUN_LEDGER} (started_at DESC);
CREATE INDEX IF NOT EXISTS adm_assist_run_outcome_idx ON {RUN_LEDGER} (outcome);
"""


def _run_stats(samples: list[dict]) -> dict:
    """由逐筆結果算 run 級統計（純函式、可自測；空集回 None 不回 0）。

    #15：空集之統計為 **None（無可算）**，不得以 0 充數——0 會被誤讀為「全員零分」。
    """
    import statistics

    scores = [float(x["score"]) for x in samples if x.get("score") is not None]
    lats = [float(x["elapsed_sec"]) for x in samples if x.get("elapsed_sec") is not None]
    models = [str(x.get("model") or "") for x in samples]
    errs: dict[str, int] = {}
    for x in samples:
        e = (x.get("flags") or {}).get("llm_error")
        if e:
            errs[str(e)] = errs.get(str(e), 0) + 1
    return {
        "examined": len(samples),
        "llm_ok": sum(1 for m in models if m == MODEL),
        "llm_fallback": sum(1 for m in models if m.startswith("heuristic_fallback:")),
        "heuristic_only": sum(1 for m in models if m == "heuristic"),
        "score_min": min(scores) if scores else None,
        "score_median": statistics.median(scores) if scores else None,
        "score_max": max(scores) if scores else None,
        "latency_median_sec": statistics.median(lats) if lats else None,
        "latency_max_sec": max(lats) if lats else None,
        "llm_errors": errs,
    }


def _run_open(mode: str, *, kind: str, limit_n: int, use_llm: bool,
              timeout: int, pools: dict) -> tuple[Any, str] | tuple[None, str]:
    """以**獨立連線**開一筆執行事實並立即 commit——即使本 run 之後崩潰/被殺，痕跡已在。

    獨立連線之理由：`--apply` 之主交易若失敗，同連線寫帳本會被一起 rollback ⇒
    「失敗」這個最該留痕的事實反而不留痕。

    ⚠ `db.connect()` 是 **@contextmanager generator**、非連線物件——直接 `.cursor()`
    會得 `AttributeError: '_GeneratorContextManager' object has no attribute 'cursor'`
    （2026-07-30 實跑抓到；自測無 DB 故未攔到）。故以 `ExitStack` 持有，
    沿用專案 `db.connect()` 之 params，不另接 psycopg2。回傳之 handle 即該 stack。
    """
    try:
        import contextlib

        from augur.core import db

        stack = contextlib.ExitStack()
        conn = stack.enter_context(db.connect())
        cur = conn.cursor()
        cur.execute(RUN_LEDGER_DDL)
        cur.execute("SELECT 'adm-assist-' || to_char(now(),'YYYYMMDDHH24MISS') || '-' "
                    "|| substr(md5(random()::text),1,6)")
        run_id = cur.fetchone()[0]
        cur.execute(
            f"""INSERT INTO {RUN_LEDGER}
                  (run_id, mode, actor, kind, limit_n, use_llm, model, prompt_version,
                   llm_timeout_sec, pool_proposed, pool_pending_staging)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (run_id, mode, ACTOR, kind, limit_n, use_llm, MODEL, PROMPT_VERSION,
             timeout, pools.get("proposed"), pools.get("pending_staging")))
        conn.commit()
        return (stack, conn), run_id
    except Exception as e:  # noqa: BLE001 — 帳本不可用不得阻斷主作業（誠實印出）
        print(f"⚠ 執行事實帳本開帳失敗（主作業繼續）: {type(e).__name__}: {e}")
        return None, ""


def _run_close(handle, run_id: str, *, outcome: str, samples: list[dict],
               assist_written: int = 0, audit_written: int = 0, error: str | None = None) -> None:
    """收帳（含失敗路徑）；帳本不可用時只印警告、不阻斷。`handle`＝`_run_open` 之 (stack, conn)。"""
    if handle is None or not run_id:
        return
    stack, conn = handle
    try:
        st = _run_stats(samples)
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE {RUN_LEDGER} SET
                  finished_at=now(),
                  elapsed_sec=EXTRACT(EPOCH FROM (now()-started_at)),
                  outcome=%s, examined=%s, llm_ok=%s, llm_fallback=%s, heuristic_only=%s,
                  score_min=%s, score_median=%s, score_max=%s,
                  latency_median_sec=%s, latency_max_sec=%s,
                  assist_written=%s, audit_written=%s, error=%s, detail=%s::jsonb
                WHERE run_id=%s""",
            (outcome, st["examined"], st["llm_ok"], st["llm_fallback"], st["heuristic_only"],
             st["score_min"], st["score_median"], st["score_max"],
             st["latency_median_sec"], st["latency_max_sec"],
             assist_written, audit_written, error,
             json.dumps({"llm_errors": st["llm_errors"]}, ensure_ascii=False), run_id))
        conn.commit()
    except Exception as e:  # noqa: BLE001
        print(f"⚠ 執行事實帳本收帳失敗: {type(e).__name__}: {e}")
    finally:
        stack.close()  # 由 db.connect() 之 contextmanager 負責關連線

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
    # 措辭校正（Steward 2026-07-30 指出「不應再出現待人裁」）：
    # 來源放行**有兩條路**——實查 `knowledge_source_review_log`：
    # 機器批 `auto_rules_v1` **48 列** vs `admin` **3 列**，**機器批才是主路徑**。
    # 故原「待人裁」暗示唯一出口是人＝與事實不符。
    # 惟來源層人簽要件（DB CHECK `chk_ks_active_needs_approval`）**仍在、非過時條款**：
    # 憲章 v1.48.0 之「一律准入」只解除 **item 層**，且 **P8「甲成立」正繫於此來源層
    # 代償介入點**——故不得逕行移除，只校正措辭。
    reason = ("啟發式預審：L1=" + ("ok" if l1.get("l1_ok") else "弱")
              + ("；license 風險" if flags["license_risk"] else "")
              + "；待放行（機器批 SRC-AUTO 七謂詞／或人簽）；本預審無放行權")
    return {"score": score, "reason": reason[:REASON_MAX], "flags": flags}


def _ask_ollama(prompt: str, timeout: int = LLM_TIMEOUT_SEC) -> str:
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


def _score_one(cand: dict, *, use_llm: bool, timeout: int = LLM_TIMEOUT_SEC) -> dict:
    l1 = _l1_flags(cand["meta"], cand["target_kind"])
    prompt = f"候選:\n{cand['summary']}\nL1={json.dumps(l1, ensure_ascii=False)}"
    ph = hashlib.sha256((PROMPT_VERSION + prompt).encode()).hexdigest()[:16]
    if use_llm:
        try:
            raw = _ask_ollama(prompt, timeout=timeout)
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

    from augur.knowledge.curation import HUMAN_ONLY

    chk("v1.48 HUMAN_ONLY 空（升級非唯人）", HUMAN_ONLY == set())

    try:
        _assert_no_upgrade_in_source()
        chk("本檔執行路徑無 transition／approval_status 寫入", True)
    except AssertionError as e:
        chk(f"本檔執行路徑無 upgrade ({e})", False)

    h = _heuristic_score("source=demo domain=philosophy license_regime=cc-by",
                         {"l1_ok": True, "l1_notes": []})
    chk("啟發式 score∈[0,1]", 0.0 <= h["score"] <= 1.0)
    chk("啟發式 hold_for_human", h["flags"].get("hold_for_human") is True)
    chk("理由不再稱「待人裁」（機器批 48 列 vs 人簽 3 列，機器批才是主路徑）",
        "待人裁" not in h["reason"] and "待放行" in h["reason"])
    chk("理由仍明示本預審無放行權（AI 不得放行之界線不因措辭改動而鬆）",
        "無放行權" in h["reason"])
    chk("ACTOR=local_ai_v1", ACTOR == "local_ai_v1")
    chk("MODEL=qwen3:4b", MODEL == "qwen3:4b")

    parsed = _parse_llm_json('雜訊 {"score":0.7,"reason":"可審","flags":{"hold_for_human":true}} 尾')
    chk("LLM JSON 解析", parsed is not None and abs(parsed["score"] - 0.7) < 1e-6)

    # ── 逾時（Steward 2026-07-30 拍板 90→9000）：驗**實際送進 urlopen 的值**，非讀常數
    import urllib.request as _u
    seen: dict = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"response": '{"score":0.5,"reason":"x","flags":{}}'}).encode()

    _orig = _u.urlopen
    _u.urlopen = lambda req, timeout=None: (seen.update(timeout=timeout), _Resp())[1]
    try:
        _ask_ollama("p")
        chk(f"_ask_ollama 預設實傳 timeout={LLM_TIMEOUT_SEC}", seen.get("timeout") == LLM_TIMEOUT_SEC)
        _ask_ollama("p", timeout=42)
        chk("timeout 可覆寫（實傳 42）", seen.get("timeout") == 42)
        seen.clear()
        _score_one({"summary": "s", "meta": {}, "target_kind": "source"},
                   use_llm=True, timeout=1234)
        chk("_score_one 之 timeout 確實透傳至 urlopen", seen.get("timeout") == 1234)
    finally:
        _u.urlopen = _orig
    chk("逾時已由 90 放寬（Steward 拍板值）", LLM_TIMEOUT_SEC == 9000)

    # ── 執行事實統計：#15 空集回 None 不回 0（0 會被誤讀為「全員零分」）
    e = _run_stats([])
    chk("空集：examined=0 且統計為 None（非 0）",
        e["examined"] == 0 and e["score_median"] is None and e["latency_median_sec"] is None)
    smp = [
        {"score": 0.9, "elapsed_sec": 1.0, "model": MODEL, "flags": {}},
        {"score": 0.1, "elapsed_sec": 5.0, "model": f"heuristic_fallback:{MODEL}",
         "flags": {"llm_error": "TimeoutError"}},
        {"score": 0.5, "elapsed_sec": 3.0, "model": "heuristic", "flags": {}},
    ]
    st2 = _run_stats(smp)
    chk("三型模型分類正確（llm_ok/fallback/heuristic 各 1）",
        (st2["llm_ok"], st2["llm_fallback"], st2["heuristic_only"]) == (1, 1, 1))
    chk("分數 min/median/max 正確",
        (st2["score_min"], st2["score_median"], st2["score_max"]) == (0.1, 0.5, 0.9))
    chk("延遲 median/max 正確", (st2["latency_median_sec"], st2["latency_max_sec"]) == (3.0, 5.0))
    chk("LLM 錯誤型別有聚合", st2["llm_errors"] == {"TimeoutError": 1})
    chk("帳本 DDL 為冪等且不含 DELETE",
        "IF NOT EXISTS" in RUN_LEDGER_DDL and "DELETE" not in RUN_LEDGER_DDL.upper())
    chk("帳本 mode 受 CHECK 約束為 dry-run/apply 二值",
        "mode IN ('dry-run','apply')" in RUN_LEDGER_DDL)

    # ── 連線契約之行為驗證：`db.connect()` 是 contextmanager 而非連線物件。
    # 前版直接 `db.connect().cursor()` ⇒ 實跑 AttributeError（自測無 DB 故未攔到）。
    # 本測以 fake contextmanager 取代之，若 _run_open 誤把 CM 當連線用即 RED。
    import contextlib as _c

    from augur.core import db as _db

    class _FakeConn:
        def __init__(self):
            self.committed = 0

        def cursor(self):
            outer = self

            class _C:
                def execute(self, sql, args=()):
                    self._sql = sql

                def fetchone(self):
                    return ("run-fake-1",)
            return _C()

        def commit(self):
            self.committed += 1

    fc = _FakeConn()
    _orig_connect = _db.connect
    _db.connect = lambda *a, **k: _c.nullcontext(fc)
    try:
        handle, rid = _run_open("dry-run", kind="source", limit_n=1, use_llm=False,
                                timeout=LLM_TIMEOUT_SEC, pools={"proposed": 1, "pending_staging": 2})
        chk("_run_open 正確使用 contextmanager（非把 CM 當連線）", handle is not None and rid)
        chk("_run_open 開帳即 commit（崩潰前已留痕）", fc.committed >= 1)
        _run_close(handle, rid, outcome="completed", samples=[])
        chk("_run_close 收帳亦 commit", fc.committed >= 2)
    finally:
        _db.connect = _orig_connect

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ADM-AI-ASSIST L2 預審（禁 approve/activate）")
    ap.add_argument("--dry-run", action="store_true", help="產分數樣本，零寫（預設安全）")
    ap.add_argument("--apply", action="store_true", help="寫入 knowledge_admission_assist（有界）")
    ap.add_argument("--limit", type=int, default=5, help="每池上限（預設 5）")
    ap.add_argument("--kind", choices=("source", "staging", "both"), default="both")
    ap.add_argument("--no-llm", action="store_true", help="跳過 Ollama，只用啟發式")
    ap.add_argument("--llm-timeout", type=int, default=LLM_TIMEOUT_SEC,
                    help=f"本地 LLM 逾時秒數（預設 {LLM_TIMEOUT_SEC}；Steward 2026-07-30 由 90 放寬）")
    ap.add_argument("--max-wall-sec", type=int, default=None,
                    help="整個 run 之總時限（秒）；達限即停並收帳（**預設 None＝不設限**，"
                         "照 Steward 之 9000s 逾時原意）。算術風險：timer 為 "
                         "--limit 20 --kind both ＝最多 40 候選，每個吃滿 9000s "
                         "⇒ 最壞 100 小時佔用 LLM 車道")
    ap.add_argument("--no-run-ledger", action="store_true",
                    help="不寫執行事實帳本（僅供除錯；預設一律留痕，含 dry-run）")
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

    mode = "apply" if args.apply else "dry-run"
    with db.connect() as conn:
        cur = conn.cursor()
        pools = _pool_counts(cur)
        print(f"池量: proposed={pools['proposed']} pending_staging={pools['pending_staging']} "
              f"assist_table={'yes' if pools['assist_table'] else 'no'}")
        if args.apply and not pools["assist_table"]:
            print("✗ 缺表：先 python scripts/migrate_admission_assist_ddl.py --apply", file=sys.stderr)
            return 1

        # 執行事實：**開帳即 commit**（獨立連線），故即使後續崩潰/被殺亦已留痕
        lconn, run_id = (None, "") if args.no_run_ledger else _run_open(
            mode, kind=args.kind, limit_n=args.limit, use_llm=use_llm,
            timeout=args.llm_timeout, pools=pools)
        if run_id:
            print(f"執行事實 run_id={run_id}（mode={mode}；逾時={args.llm_timeout}s）")

        results: list[tuple[dict, dict]] = []
        samples: list[dict] = []
        audit_rows = 0
        wall_t0 = time.monotonic()
        wall_stopped = False
        try:
            for kind in kinds:
                cands = _load_candidates(cur, kind=kind, limit=args.limit)
                for cand in cands:
                    # `is not None`（非 truthy）：0 須解為「立刻停」而非「未設限」
                    if (args.max_wall_sec is not None
                            and (time.monotonic() - wall_t0) >= args.max_wall_sec):
                        wall_stopped = True
                        print(f"⏱ 達總時限 {args.max_wall_sec}s，停止取件"
                              f"（已處理 {len(samples)} 筆；本支冪等、重跑即續）")
                        break
                    t0 = time.monotonic()
                    scored = _score_one(cand, use_llm=use_llm, timeout=args.llm_timeout)
                    scored["elapsed_sec"] = round(time.monotonic() - t0, 3)
                    results.append((cand, scored))
                    samples.append(scored)
                    print(f"[{cand['target_kind']}] {cand['target_id']} "
                          f"score={scored['score']:.3f} model={scored.get('model')} "
                          f"{scored['elapsed_sec']}s reason={scored['reason'][:80]}")
                    if args.apply:
                        _write_assist(cur, cand, scored)
                        if _write_source_audit(cur, cand, scored):
                            audit_rows += 1
                if wall_stopped:
                    break
        except BaseException as exc:  # 含 KeyboardInterrupt／SystemExit：失敗亦須留痕
            _run_close(lconn, run_id, outcome="failed", samples=samples,
                       assist_written=0, audit_written=0,
                       error=f"{type(exc).__name__}: {exc}"[:2000])
            raise

        if args.apply:
            conn.commit()
            print(f"✓ 已寫 assist={len(results)} 列、source_audit={audit_rows} 列"
                  f"（actor={ACTOR}；未觸升級）")
        else:
            print(f"dry-run 樣本 {len(results)} 筆（零寫審批）；人裁仍走 "
                  "review_knowledge_source.py --approve/--activate（TTY）")

        st = _run_stats(samples)
        print(f"執行事實：examined={st['examined']} llm_ok={st['llm_ok']} "
              f"fallback={st['llm_fallback']} heuristic={st['heuristic_only']}"
              + (f" 分數 min/median/max={st['score_min']:.3f}/{st['score_median']:.3f}"
                 f"/{st['score_max']:.3f}" if st["score_median"] is not None else " 分數=無可算（空集）")
              + (f" 延遲 median/max={st['latency_median_sec']:.1f}s/{st['latency_max_sec']:.1f}s"
                 if st["latency_median_sec"] is not None else ""))
        if st["llm_errors"]:
            print(f"  LLM 錯誤分佈：{st['llm_errors']}")
        _run_close(lconn, run_id, outcome="completed", samples=samples,
                   assist_written=len(results) if args.apply else 0,
                   audit_written=audit_rows,
                   error=(f"wall_limit_reached:{args.max_wall_sec}s" if wall_stopped else None))
        if wall_stopped:
            print(f"（本 run 因總時限收尾；帳本 error 欄記 wall_limit_reached）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
