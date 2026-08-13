"""KH ingest-driven 觸發（階 C）— 依庫內訊號 S0–S9 建議／有界補救。

🎯 這支在做什麼(白話):量測庫內 S0–S9 訊號、建議有界補救；hook 預設只 check，
   `--apply`／ENV 才一槍執行（S0 drain 或 S3 concordance）。不默開 AUTO-LIFT／timer。

對齊: reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md
護欄: 無日曆假進化；APPLY 選開；FZ/GATE-keep（知識）。

ENV:
  AUGUR_KH_INGEST_TRIGGER=0     關閉 hook／CLI 預設量測（預設開）
  AUGUR_KH_INGEST_TRIGGER_APPLY=1  允許有界 apply（預設關）

執行指令矩陣(本檔=library #18):
  python -m augur.knowledge.ingest_triggers --selftest
  python scripts/kh_ingest_trigger.py --check
  python scripts/kh_ingest_trigger.py --dry-run
  python scripts/kh_ingest_trigger.py --apply
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PLAN_REF = "reports/augur_kh_ingest_driven_trigger_plan_b_20260812.md"
ENV_ENABLE = "AUGUR_KH_INGEST_TRIGGER"
ENV_APPLY = "AUGUR_KH_INGEST_TRIGGER_APPLY"
STATE_PATH = Path.home() / ".augur" / "kh_ingest_trigger_state.json"
REPO = Path(__file__).resolve().parents[3]  # .../augur/src/augur/knowledge → repo root
PY = str(REPO / "venv" / "bin" / "python3")
APPLY_ADVANCE_CAP = 500
APPLY_CONC_LIMIT = 5000  # S3 有界補建；Steward 2026-08-12 由 200 調高

# 優先：S0→S5→S3→S2→S1→S7→S4→S6→S8（對齊 B §2）
_PRIORITY = ("S0", "S5", "S3", "S2", "S1", "S7", "S4", "S6", "S8")


def enabled() -> bool:
    return os.environ.get(ENV_ENABLE, "1").strip() not in ("0", "false", "False", "no")


def apply_enabled() -> bool:
    return os.environ.get(ENV_APPLY, "").strip() in ("1", "true", "True", "yes")


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(st: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def measure_signals(cur, *, skips: dict | None = None) -> dict:
    """唯讀量測；S5／S6／S7／S8／S9 多為人工／運維訊號（本函式標 not_auto）。"""
    out: dict = {"plan": PLAN_REF}

    cur.execute(
        """SELECT count(*) FROM knowledge_item i
             LEFT JOIN knowhow_auto_admit_state st
               ON st.target_kind='item' AND st.target_id=i.item_id::text
            WHERE st.target_id IS NULL"""
    )
    breach = int(cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM knowledge_item")
    items_total = int(cur.fetchone()[0])
    out["S0"] = {"fired": breach > 0, "kh0_breach": breach, "items_total": items_total}

    st = _load_state()
    prev_items = int(st.get("items_total") or 0)
    delta_items = max(0, items_total - prev_items) if prev_items else 0
    out["S1"] = {
        "fired": delta_items >= 1,
        "items_total": items_total,
        "delta_since_last": delta_items,
        "note": "first_seen_baseline" if not prev_items else "",
    }

    cur.execute(
        """SELECT count(*) FROM knowledge_kh4_state WHERE answer_status='eligible'"""
    )
    eligible = int(cur.fetchone()[0])
    prev_el = int(st.get("eligible_total") or 0)
    delta_el = max(0, eligible - prev_el) if prev_el else 0
    out["S2"] = {
        "fired": delta_el >= 1,
        "eligible_total": eligible,
        "delta_since_last": delta_el,
        "note": "first_seen_baseline" if not prev_el else "",
    }

    # S3：items 主游標落後（廉价：max(sent_id) vs cursor；非精確待補句數）
    s3 = {"fired": False, "langs": {}}
    for lang in ("zh", "en"):
        scope = f"concordance_items_{lang}"
        cur.execute(
            "SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope=%s",
            (scope,),
        )
        row = cur.fetchone()
        cursor = int(row[0]) if row and row[0] is not None else 0
        cur.execute(
            """SELECT coalesce(max(sent_id),0) FROM knowledge_sentence
                WHERE text_id IS NULL AND language=%s""",
            (lang,),
        )
        mx = int(cur.fetchone()[0])
        lag = max(0, mx - cursor)
        s3["langs"][lang] = {"cursor": cursor, "max_sent_id": mx, "lag_est": lag}
        if lag > 0:
            s3["fired"] = True
    out["S3"] = s3

    skip_n = 0
    if skips:
        skip_n = sum(int(v) for v in skips.values())
    out["S4"] = {
        "fired": skip_n >= 3,
        "skip_total": skip_n,
        "skips": dict(skips or {}),
        "note": "from_ingress_batch" if skips is not None else "not_in_batch",
    }

    for sid, note in (
        ("S5", "false_decline_manual_or_smoke"),
        ("S6", "lift_log_ops_flag"),
        ("S7", "private_asr_smoke"),
        ("S8", "domain_ft_steward_go"),
        ("S9", "kh8_never_auto"),
    ):
        out[sid] = {"fired": False, "auto": False, "note": note}

    return out


def fired_in_priority(signals: dict) -> list[str]:
    hit = []
    for sid in _PRIORITY:
        cell = signals.get(sid) or {}
        if cell.get("fired"):
            hit.append(sid)
    return hit


def recommend(signals: dict) -> list[dict]:
    """回傳建議動作（字串／argv）；不含副作用。"""
    acts: list[dict] = []
    for sid in fired_in_priority(signals):
        if sid == "S0":
            n = min(int(signals["S0"]["kh0_breach"]), APPLY_ADVANCE_CAP)
            acts.append({
                "signal": "S0",
                "wave": "K-Data",
                "apply_ok": True,
                "argv": [PY, "scripts/run_kh_chain.py", "--run", "--phase", "advance",
                         "--up-to", "0", "--limit", str(n)],
                "summary": f"KH0 breach drain up_to=0 limit={n}",
            })
        elif sid == "S3":
            # 先 zh；en 若也 lag 下一輪再補
            lang = "zh" if (signals["S3"]["langs"].get("zh") or {}).get("lag_est", 0) else "en"
            acts.append({
                "signal": "S3",
                "wave": "K-Hit",
                "apply_ok": True,
                "argv": [PY, "scripts/build_concordance.py", "--scope", "items",
                         "--language", lang, "--limit", str(APPLY_CONC_LIMIT)],
                "summary": f"concordance items×{lang} limit={APPLY_CONC_LIMIT}",
            })
        elif sid == "S1":
            acts.append({
                "signal": "S1",
                "wave": "K-Data",
                "apply_ok": False,
                "summary": "new items — rely on ingress KIP; re-check S0 after",
            })
        elif sid == "S2":
            acts.append({
                "signal": "S2",
                "wave": "K-Hit",
                "apply_ok": False,
                "summary": "new eligible — optional readout sample / conc backfill (manual)",
            })
        elif sid == "S4":
            acts.append({
                "signal": "S4",
                "wave": "K-Parse",
                "apply_ok": False,
                "summary": "parser skips≥3 — Steward reingest / tool fix",
            })
        else:
            acts.append({
                "signal": sid,
                "wave": "ops",
                "apply_ok": False,
                "summary": (signals.get(sid) or {}).get("note") or "manual",
            })
    return acts


def persist_baseline(signals: dict) -> None:
    st = _load_state()
    st["items_total"] = int((signals.get("S1") or signals.get("S0") or {}).get("items_total")
                            or signals.get("S0", {}).get("items_total") or 0)
    if "S0" in signals:
        st["items_total"] = int(signals["S0"]["items_total"])
    if "S2" in signals:
        st["eligible_total"] = int(signals["S2"]["eligible_total"])
    st["kh0_breach"] = int(signals.get("S0", {}).get("kh0_breach") or 0)
    _save_state(st)


def format_report(signals: dict, acts: list[dict]) -> str:
    lines = [
        "══ KH ingest-trigger（階 C · 訊號）══",
        f"  plan: {PLAN_REF}",
        f"  enable={enabled()} apply_env={apply_enabled()}",
    ]
    for sid in ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"):
        cell = signals.get(sid) or {}
        flag = "FIRE" if cell.get("fired") else "ok"
        extra = {k: v for k, v in cell.items() if k not in ("fired",)}
        lines.append(f"  {sid} [{flag}] {extra}")
    fired = fired_in_priority(signals)
    lines.append(f"  priority_hit: {fired or '∅ → no-op'}")
    if acts:
        lines.append("  recommend:")
        for a in acts:
            lines.append(f"    - {a['signal']}/{a['wave']}: {a['summary']}"
                         + (" [apply_ok]" if a.get("apply_ok") else " [advise_only]"))
    else:
        lines.append("  recommend: (none)")
    return "\n".join(lines)


def apply_light(acts: list[dict], *, dry_run: bool = False) -> list[dict]:
    """只執行 apply_ok 且排序最前的一槍（有界）；禁全鏈深層。"""
    results = []
    chosen = next((a for a in acts if a.get("apply_ok") and a.get("argv")), None)
    if not chosen:
        return [{"status": "no-op", "reason": "no_apply_ok_action"}]
    argv = chosen["argv"]
    results.append({"status": "dry-run" if dry_run else "run", "argv": argv,
                    "signal": chosen["signal"]})
    if dry_run:
        return results
    # 與重 LLM 讓位：若 lock 被佔且本動作非必須，仍允許 advance（無 LLM）
    r = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True, timeout=3600)
    results[-1]["rc"] = r.returncode
    results[-1]["stdout_tail"] = (r.stdout or "")[-2000:]
    results[-1]["stderr_tail"] = (r.stderr or "")[-1000:]
    return results


def hook_after_ingress(
    *,
    channel: str,
    job_id: int | str | None = None,
    skips: dict | None = None,
    stats: dict | None = None,
) -> dict:
    """入庫成功後呼叫：預設只量測＋印；APPLY=1 才有界補救。"""
    if not enabled():
        return {"skipped": True, "reason": "AUGUR_KH_INGEST_TRIGGER=0"}
    from augur.core import db

    with db.connect() as conn:
        cur = conn.cursor()
        sig = measure_signals(cur, skips=skips)
    # 本批有入庫成功 → 強制視 S1 有擴張訊號（即使 baseline 同輪）
    if stats and int(stats.get("ok") or 0) > 0:
        sig["S1"]["fired"] = True
        sig["S1"]["batch_ok"] = int(stats["ok"])
    acts = recommend(sig)
    report = format_report(sig, acts)
    print(f"[kh_ingest_trigger] channel={channel} job={job_id}\n{report}", flush=True)
    out: dict = {"signals": sig, "actions": acts, "report": report}
    if apply_enabled():
        out["apply"] = apply_light(acts, dry_run=False)
        print(f"[kh_ingest_trigger] apply={out['apply']}", flush=True)
    else:
        out["apply"] = [{"status": "skipped", "reason": f"set {ENV_APPLY}=1 to apply"}]
    persist_baseline(sig)
    return out


def selftest() -> int:
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)
            print(f"  ✗ {name}")
        else:
            print(f"  ✓ {name}")

    sig = {
        "S0": {"fired": False},
        "S1": {"fired": True},
        "S2": {"fired": True},
        "S3": {"fired": True, "langs": {"zh": {"lag_est": 10}}},
        "S4": {"fired": False},
        "S5": {"fired": True},
        "S6": {"fired": False},
        "S7": {"fired": False},
        "S8": {"fired": False},
    }
    order = fired_in_priority(sig)
    chk("priority S5 before S3", order[:2] == ["S5", "S3"])
    acts = recommend({
        "S0": {"fired": True, "kh0_breach": 12, "items_total": 100},
        "S1": {"fired": False},
        "S2": {"fired": False},
        "S3": {"fired": False, "langs": {}},
        "S4": {"fired": False},
        "S5": {"fired": False},
        "S6": {"fired": False},
        "S7": {"fired": False},
        "S8": {"fired": False},
        "S9": {"fired": False},
    })
    chk("S0 recommend apply_ok", acts and acts[0].get("apply_ok") is True)
    chk("--up-to 0 in argv", acts and "--up-to" in acts[0]["argv"] and "0" in acts[0]["argv"])
    dry = apply_light([], dry_run=True)
    chk("empty acts no-op", dry and dry[0].get("status") == "no-op")
    chk("enabled default true", enabled() is True)
    print("公開: measure_signals / recommend / hook_after_ingress / selftest")
    if fails:
        print(f"SELFTEST FAIL: {fails}")
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    # library self-entry
    sys.exit(selftest())
