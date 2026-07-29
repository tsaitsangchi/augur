"""KH9 合成與回放 — 最小可評估片（min-LAND）。

🎯 這支在做什麼(白話):吃 KH8 權重列，寫入 knowhow_synthesis_run（structured
   synthesis + replay_json），讓系統可回看「為何這次判定」。
   **不**越權升格 approve／activate／PME apply；≠可交易。
守 #15(缺料誠實)· #18(領域名詞)· NHC-keep· FZ-keep· PME-GATE-keep· HUMAN-APPROVE-keep。

執行指令矩陣(本檔=library #18；免 DB 可個別驗證):
  python -m augur.knowledge.synthesis
  python -m augur.knowledge.synthesis --selftest
"""
from __future__ import annotations

import json
from typing import Any, Mapping

ANSWER_STATES = (
    "drafted",
    "synthesized",
    "replay_logged",
    "postmortem_needed",
)
PASS_STATES = frozenset({"synthesized", "replay_logged"})


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def build_synthesis(
    *,
    item_id: int,
    weight: Mapping[str, Any],
    snap: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """純函式：由權重＋可選 snap 產出合成／回放工件。"""
    band = str(weight.get("confidence_band") or "absent")
    score = float(weight.get("evidence_score") or 0.0)
    snap = snap or {}
    if band == "absent":
        state = "postmortem_needed"
    elif band in ("high", "medium"):
        state = "replay_logged"
    else:
        state = "synthesized"

    domain = snap.get("domain") or ""
    source_key = snap.get("source_key") or ""
    query_text = (
        f"KH9 replay item_id={int(item_id)} domain={domain} source={source_key}"
    )
    replay = {
        "kind": "kh9_min_replay",
        "item_id": int(item_id),
        "weight_id": weight.get("weight_id"),
        "confidence_band": band,
        "evidence_score": score,
        "risk_flags": weight.get("risk_flags") or [],
        "components": weight.get("components") or {},
        "boundaries": {
            "eligibility_pass_ne_approve": True,
            "approve_ne_tradable": True,
            "no_pme_solar_gates": True,
            "fz_keep": True,
        },
        "snap": {
            "has_text": bool(snap.get("has_text")),
            "has_sentence": bool(snap.get("has_sentence")),
            "has_embedding": bool(snap.get("has_embedding")),
            "domain": domain,
            "source_key": source_key,
        },
    }
    return {
        "query_text": query_text,
        "answer_state": state,
        "evidence_score": score,
        "replay_json": replay,
        "run_id": f"kh9:item:{int(item_id)}:w{weight.get('weight_id') or 0}",
    }


def record_synthesis(
    cur,
    *,
    item_id: int,
    synth: Mapping[str, Any],
    weight_id: int | None,
) -> int:
    cur.execute(
        """
        INSERT INTO knowhow_synthesis_run
          (item_id, run_id, query_text, answer_state, evidence_score,
           weight_id, replay_json)
        VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
        ON CONFLICT (run_id) DO UPDATE SET
          query_text=EXCLUDED.query_text,
          answer_state=EXCLUDED.answer_state,
          evidence_score=EXCLUDED.evidence_score,
          weight_id=EXCLUDED.weight_id,
          replay_json=EXCLUDED.replay_json,
          created_at=now()
        RETURNING synthesis_id
        """,
        (
            int(item_id),
            str(synth["run_id"]),
            str(synth["query_text"]),
            str(synth["answer_state"]),
            float(synth["evidence_score"]) if synth.get("evidence_score") is not None else None,
            int(weight_id) if weight_id is not None else None,
            _json(synth["replay_json"]),
        ),
    )
    return int(cur.fetchone()[0])


def evaluate_item_synthesis(cur, snap: Mapping[str, Any]) -> dict[str, Any]:
    """auto_admit evaluate_layer(9) 入口：需 KH8 權重列→寫 replay 帳。"""
    cur.execute("SELECT to_regclass(%s)", ("public.knowhow_synthesis_run",))
    if not cur.fetchone()[0]:
        return {"verdict": "skipped", "note": "KH9 表未建"}

    cur.execute("SELECT to_regclass(%s)", ("public.knowhow_evidence_weight",))
    if not cur.fetchone()[0]:
        return {"verdict": "fail", "note": "KH8 表缺→無法合成"}

    from augur.knowledge import evidence as ev

    item_id = int(snap["item_id"])
    weight = ev.latest_weight_for_item(cur, item_id)
    if not weight:
        return {
            "verdict": "fail",
            "note": "尚無 KH8 權重列（須先 evaluate_layer 8）",
            "action": "kh9_no_weight",
        }

    synth = build_synthesis(item_id=item_id, weight=weight, snap=dict(snap))
    sid = record_synthesis(
        cur, item_id=item_id, synth=synth, weight_id=weight.get("weight_id")
    )
    state = synth["answer_state"]
    note = (
        f"synthesis_id={sid} state={state} weight_id={weight.get('weight_id')} "
        f"score={synth['evidence_score']}（≠approve／≠PME）"
    )
    if state in PASS_STATES:
        return {
            "verdict": "pass",
            "note": note,
            "action": "kh9_replay_logged",
            "synthesis_id": sid,
            "synthesis": synth,
        }
    return {
        "verdict": "fail",
        "note": note + "；postmortem_needed→fail",
        "action": "kh9_postmortem",
        "synthesis_id": sid,
        "synthesis": synth,
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    rich = {
        "weight_id": 42,
        "confidence_band": "high",
        "evidence_score": 0.85,
        "risk_flags": [],
        "components": {"formula": "test"},
    }
    s = build_synthesis(item_id=1, weight=rich, snap={"domain": "d", "has_text": True})
    chk("rich→replay_logged", s["answer_state"] == "replay_logged")
    chk("rich pass-state", s["answer_state"] in PASS_STATES)
    chk("run_id has weight", "w42" in s["run_id"])
    chk("replay has boundaries", s["replay_json"]["boundaries"]["fz_keep"] is True)

    thin = {
        "weight_id": 7,
        "confidence_band": "absent",
        "evidence_score": 0.05,
        "risk_flags": ["insufficient_evidence"],
        "components": {},
    }
    s2 = build_synthesis(item_id=2, weight=thin)
    chk("absent→postmortem", s2["answer_state"] == "postmortem_needed")
    chk("absent not pass", s2["answer_state"] not in PASS_STATES)

    low = {
        "weight_id": 3,
        "confidence_band": "low",
        "evidence_score": 0.2,
        "risk_flags": [],
        "components": {},
    }
    s3 = build_synthesis(item_id=3, weight=low)
    chk("low→synthesized", s3["answer_state"] == "synthesized")
    chk("states closed", set(ANSWER_STATES) == set(PASS_STATES) | {"drafted", "postmortem_needed"})
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or "").split("🎯")[0].strip())
    print("公開: build_synthesis / evaluate_item_synthesis / record_synthesis")
    print("(自測: python -m augur.knowledge.synthesis --selftest)")
