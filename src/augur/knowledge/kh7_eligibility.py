"""KH7 對抗可答性機械裁決 — KH7-S1 最小 slice。

🎯 這支在做什麼(白話):吃單探針 `summarize_probe_result` 形狀（gap／merged／
   multi_source／spurious），依閉集規則裁 eligibility_pass／fail／needs_human_review。
   **不是**答案 SSOT、**不**自動 approve／activate、**禁**依 domain 寫死專題應答。
守 #15(缺料誠實)· #18(領域名詞)· NHC-keep· HUMAN-APPROVE-keep· FZ-keep。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.knowledge.kh7_eligibility
  python -m augur.knowledge.kh7_eligibility --selftest
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

STATUSES = (
    "unchecked",
    "eligibility_pass",
    "eligibility_fail",
    "contradiction_found",  # S1 不實作矛盾模板；僅閉集預留
    "needs_human_review",
)


def _as_list(flags: Any) -> list[str]:
    if flags is None:
        return []
    if isinstance(flags, list):
        return [str(x) for x in flags]
    if isinstance(flags, str):
        try:
            parsed = json.loads(flags)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except json.JSONDecodeError:
            pass
        return [flags] if flags else []
    return []


def _axis_counts(summary: Mapping[str, Any]) -> dict[str, int]:
    raw = summary.get("axis_hit_counts")
    if isinstance(raw, dict):
        return {str(k): int(v or 0) for k, v in raw.items()}
    # ledger hit_counts 形狀
    hc = summary.get("hit_counts")
    if isinstance(hc, str):
        try:
            hc = json.loads(hc)
        except json.JSONDecodeError:
            hc = {}
    if isinstance(hc, dict):
        axis = hc.get("axis") or {}
        if isinstance(axis, dict):
            return {str(k): int(v or 0) for k, v in axis.items()}
    return {}


def _merged_hits(summary: Mapping[str, Any]) -> int:
    if "merged_hits" in summary:
        return int(summary.get("merged_hits") or 0)
    hc = summary.get("hit_counts")
    if isinstance(hc, str):
        try:
            hc = json.loads(hc)
        except json.JSONDecodeError:
            hc = {}
    if isinstance(hc, dict) and "merged" in hc:
        return int(hc.get("merged") or 0)
    return 0


def _multi_source(summary: Mapping[str, Any]) -> int:
    if "multi_source_hits" in summary:
        return int(summary.get("multi_source_hits") or 0)
    hc = summary.get("hit_counts")
    if isinstance(hc, str):
        try:
            hc = json.loads(hc)
        except json.JSONDecodeError:
            hc = {}
    if isinstance(hc, dict) and "multi_source" in hc:
        return int(hc.get("multi_source") or 0)
    return 0


def _axis_labels(summary: Mapping[str, Any]) -> list[str]:
    """從 axes[].label 或 axis 查詢字串抽出軸標籤。"""
    labels: list[str] = []
    axes = summary.get("axes")
    if isinstance(axes, str):
        try:
            axes = json.loads(axes)
        except json.JSONDecodeError:
            axes = []
    if isinstance(axes, list):
        for a in axes:
            if isinstance(a, dict):
                lab = str(a.get("label") or "").strip()
                if lab:
                    labels.append(lab)
    if labels:
        return labels
    for q in summary.get("queries") or []:
        if not isinstance(q, dict):
            continue
        if str(q.get("qkey") or "").startswith("axis:"):
            lab = str(q.get("query") or "").strip()
            if lab:
                labels.append(lab)
    return labels


def _hit_text_blob(summary: Mapping[str, Any]) -> str:
    tops = summary.get("top_hits")
    if isinstance(tops, str):
        try:
            tops = json.loads(tops)
        except json.JSONDecodeError:
            tops = []
    parts: list[str] = []
    for h in tops or []:
        if not isinstance(h, dict):
            continue
        parts.append(str(h.get("title") or ""))
        parts.append(str(h.get("snippet") or ""))
    return "\n".join(parts)


def detect_ungrounded(summary: Mapping[str, Any]) -> bool:
    """軸 label 皆未出現於任一 top-hit title／snippet → True（確定性字串包含）。

    無 label 可校 → False；merged=0 交由 no_corpus 規則，此處 False。
    """
    if _merged_hits(summary) <= 0:
        return False
    labels = _axis_labels(summary)
    if not labels:
        return False
    blob = _hit_text_blob(summary).lower()
    if not blob.strip():
        # 有 merged 卻無 top 摘要可校 → 視為未落地
        return True
    return all(lab.lower() not in blob for lab in labels)


def decide_eligibility(summary: Mapping[str, Any]) -> dict:
    """單探針機械裁決。回 {status, reasons, evidence}；不寫 DB。

    規則（計畫 §3.1，順序優先；2026-07-29 加 ungrounded）:
      0. 軸 label 皆未落地 top-hit（ungrounded）→ eligibility_fail
      1. no_corpus 或 merged_hits<=0 → eligibility_fail
      2. 任一 no_axis:* → eligibility_fail
      3. spurious_risk=high 或 ungrounded∈gap → eligibility_fail
      4. single_axis_only → needs_human_review
      5. covered>=2 ∧ multi_source>=1 ∧ spurious=low ∧ 無 ungrounded → eligibility_pass
      6. 其餘 → needs_human_review
    """
    gap = list(_as_list(summary.get("gap_flags")))
    merged = _merged_hits(summary)
    multi = _multi_source(summary)
    axis = _axis_counts(summary)
    covered = sum(1 for n in axis.values() if n > 0)
    spurious = str(summary.get("spurious_risk") or "n/a")
    probe_id = str(summary.get("probe_id") or "")
    ungrounded = (
        "ungrounded_hits" in gap
        or bool(summary.get("ungrounded_hits"))
        or detect_ungrounded(summary)
    )
    if ungrounded and "ungrounded_hits" not in gap:
        gap = gap + ["ungrounded_hits"]

    evidence = {
        "probe_id": probe_id,
        "merged_hits": merged,
        "multi_source_hits": multi,
        "axis_hit_counts": axis,
        "covered": covered,
        "gap_flags": gap,
        "spurious_risk": spurious,
        "ungrounded_hits": ungrounded,
        "axis_labels": _axis_labels(summary),
    }
    reasons: list[str] = []

    if ungrounded:
        reasons.append("ungrounded_axis_labels")
        return {
            "status": "eligibility_fail",
            "reasons": reasons,
            "evidence": evidence,
        }

    if "no_corpus" in gap or merged <= 0:
        reasons.append("no_corpus_or_empty_merged")
        return {
            "status": "eligibility_fail",
            "reasons": reasons,
            "evidence": evidence,
        }

    no_axis = [f for f in gap if f.startswith("no_axis:")]
    if no_axis:
        reasons.append("missing_axis:" + ",".join(no_axis))
        return {
            "status": "eligibility_fail",
            "reasons": reasons,
            "evidence": evidence,
        }

    if spurious == "high":
        reasons.append("spurious_risk_high")
        return {
            "status": "eligibility_fail",
            "reasons": reasons,
            "evidence": evidence,
        }

    if "single_axis_only" in gap:
        reasons.append("single_axis_only")
        return {
            "status": "needs_human_review",
            "reasons": reasons,
            "evidence": evidence,
        }

    if covered >= 2 and multi >= 1 and spurious == "low" and not ungrounded:
        reasons.append("multi_axis_multi_source_low_spurious")
        return {
            "status": "eligibility_pass",
            "reasons": reasons,
            "evidence": evidence,
        }

    reasons.append("grey_zone")
    return {
        "status": "needs_human_review",
        "reasons": reasons,
        "evidence": evidence,
    }


def batch_decide(summaries: Sequence[Mapping[str, Any]]) -> list[dict]:
    """批次裁決；每筆附 probe_id 於頂層便於帳本。"""
    out: list[dict] = []
    for s in summaries:
        d = decide_eligibility(s)
        d["probe_id"] = str(s.get("probe_id") or d["evidence"].get("probe_id") or "")
        out.append(d)
    return out


def _selftest() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    fail_empty = decide_eligibility({
        "probe_id": "t0",
        "merged_hits": 0,
        "multi_source_hits": 0,
        "axis_hit_counts": {"a": 0, "b": 0},
        "gap_flags": ["no_corpus", "no_axis:a", "no_axis:b"],
        "spurious_risk": "n/a",
    })
    check("空語料→fail", fail_empty["status"] == "eligibility_fail")

    fail_axis = decide_eligibility({
        "probe_id": "t1",
        "merged_hits": 3,
        "multi_source_hits": 0,
        "axis_hit_counts": {"a": 3, "b": 0},
        "gap_flags": ["no_axis:b"],
        "spurious_risk": "medium",
    })
    check("缺軸→fail", fail_axis["status"] == "eligibility_fail")

    fail_spur = decide_eligibility({
        "probe_id": "t2",
        "merged_hits": 5,
        "multi_source_hits": 0,
        "axis_hit_counts": {"a": 5, "b": 0},
        "gap_flags": [],
        "spurious_risk": "high",
    })
    check("高假相關→fail", fail_spur["status"] == "eligibility_fail")

    review_single = decide_eligibility({
        "probe_id": "t3",
        "merged_hits": 2,
        "multi_source_hits": 0,
        "axis_hit_counts": {"a": 2, "b": 0},
        "gap_flags": ["single_axis_only"],
        "spurious_risk": "medium",
    })
    check("單軸→human", review_single["status"] == "needs_human_review")

    passed = decide_eligibility({
        "probe_id": "t4",
        "merged_hits": 4,
        "multi_source_hits": 2,
        "axis_hit_counts": {"a": 2, "b": 2},
        "gap_flags": [],
        "spurious_risk": "low",
    })
    check("多軸多源低假→pass", passed["status"] == "eligibility_pass")

    fail_ungrounded = decide_eligibility({
        "probe_id": "KNI-EVAL-EMPTY-CORPUS",
        "merged_hits": 16,
        "multi_source_hits": 2,
        "axis_hit_counts": {"a": 6, "b": 6},
        "axes": [
            {"role": "a", "label": "ZZZZ-NONEXISTENT-AXIS-ALPHA-KNI-EVAL"},
            {"role": "b", "label": "ZZZZ-NONEXISTENT-AXIS-BETA-KNI-EVAL"},
        ],
        "top_hits": [
            {"title": "Augustine Donatist", "snippet": "philosophy neighbor"},
            {"title": "Origen writings", "snippet": "patristic"},
        ],
        "gap_flags": [],
        "spurious_risk": "low",
    })
    check("ungrounded 字串校驗→fail（即使 multi+low）",
          fail_ungrounded["status"] == "eligibility_fail"
          and "ungrounded_axis_labels" in fail_ungrounded["reasons"])
    check("detect_ungrounded 真", detect_ungrounded({
        "merged_hits": 2,
        "axes": [{"label": "NO-SUCH-LABEL-XYZ"}],
        "top_hits": [{"title": "hello", "snippet": "world"}],
    }))
    check("detect 有落地字→False", not detect_ungrounded({
        "merged_hits": 2,
        "axes": [{"label": "第一性原理"}],
        "top_hits": [{"title": "談第一性原理", "snippet": "x"}],
    }))

    grey = decide_eligibility({
        "probe_id": "t5",
        "merged_hits": 3,
        "multi_source_hits": 0,
        "axis_hit_counts": {"a": 1, "b": 1},
        "gap_flags": [],
        "spurious_risk": "medium",
    })
    check("灰區→human", grey["status"] == "needs_human_review")

    batch = batch_decide([
        {"probe_id": "a", "merged_hits": 0, "gap_flags": ["no_corpus"],
         "axis_hit_counts": {}, "multi_source_hits": 0, "spurious_risk": "n/a"},
        {"probe_id": "b", "merged_hits": 4, "multi_source_hits": 2,
         "axis_hit_counts": {"x": 2, "y": 2}, "gap_flags": [], "spurious_risk": "low"},
    ])
    check("batch 長度", len(batch) == 2)
    check("batch probe_id", batch[0]["probe_id"] == "a" and batch[1]["probe_id"] == "b")

    # 禁專題答案樹／approve：以 AST 掃呼叫，不誤傷 docstring 禁令字樣
    import ast
    from pathlib import Path

    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                calls.append(fn.attr)
    # 函式體不得出現答案樹 dict 賦值（docstring 禁令字樣除外——只掃 Call）
    check("無 approve/activate/transition 呼叫",
          "approve" not in calls and "activate" not in calls and "transition" not in calls)
    check("decide_eligibility 為純函式出口",
          "decide_eligibility" in src and "batch_decide" in src)
    check("閉集含 contradiction_found 預留", "contradiction_found" in STATUSES)

    print("kh7_eligibility 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or "--selftest" in args or "-h" in args or "--help" in args:
        if "--selftest" in args:
            return _selftest()
        print(__doc__)
        if "-h" in args or "--help" in args:
            return 0
        return _selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
