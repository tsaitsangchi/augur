"""Know-how 交互探針展開／多軸查詢／RRF 合併 — KH5／KH6 最小 slice。

🎯 這支在做什麼(白話):讀 `knowhow_interaction_probe` 列的 template／axes／params，
   展開成多軸查詢＋交互全句，以 reciprocal rank fusion（RRF）合併多路命中，
   產出缺口旗標／假相關風險摘要。本層是探針方法論，**不是**答案 SSOT、
   **不**改 answer gate、**不**自動灌 PME／approve／activate。
守 #1(命中須可溯源)· #15(缺料誠實 gap)· #18(領域名詞)· NHC-keep(禁專題答案樹)· FZ-keep。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.knowledge.interaction_probe
  python -m augur.knowledge.interaction_probe --selftest
"""
from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence

_SLOT_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")
_LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
_LABEL_SEP_RE = re.compile(r"[·／/｜|\s]+")
RRF_K = 60
# exact 命中額外加權（≈再投一票於 rank≈1），避免 RRF 被哲學近鄰淹沒字面命中
RRF_EXACT_BONUS = 1.0 / (RRF_K + 1)


def expand_prompt(template: str, params: Mapping[str, Any] | None) -> str:
    """把 `{{slot}}` 用 template_params 實例化；缺槽保留原字面（誠實可見）。"""
    params = params or {}

    def _repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in params:
            return m.group(0)
        return str(params[key])

    return _SLOT_RE.sub(_repl, template or "")


def normalize_axes(axes: Any, *, knowhow_axis: str = "", raw_axis: str = "") -> list[dict]:
    """axes JSONB／字串／空 → 有序 [{role,label}]；空則退回二元投影欄。"""
    raw = axes
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = []
    out: list[dict] = []
    if isinstance(raw, list):
        for i, a in enumerate(raw):
            if isinstance(a, dict):
                label = str(a.get("label") or "").strip()
                role = str(a.get("role") or f"axis{i}").strip() or f"axis{i}"
                if label:
                    out.append({"role": role, "label": label})
            elif isinstance(a, str) and a.strip():
                out.append({"role": f"axis{i}", "label": a.strip()})
    if out:
        return out
    fallback = []
    if (knowhow_axis or "").strip():
        fallback.append({"role": "knowhow", "label": knowhow_axis.strip()})
    if (raw_axis or "").strip():
        fallback.append({"role": "raw", "label": raw_axis.strip()})
    return fallback


def build_queries(
    *,
    expanded_prompt: str,
    axes: Sequence[Mapping[str, Any]],
    template_params: Mapping[str, Any] | None = None,
) -> list[dict]:
    """多軸擴軸＋交互全句查詢清單（通用；零領域 hardcode）。

    回 [{"qkey","role","query"}, ...]：
      - 每軸一查（label；若 params 有同 role 值則優先）
      - 一條 interaction＝expanded_prompt
    """
    params = dict(template_params or {})
    queries: list[dict] = []
    seen: set[str] = set()
    for i, axis in enumerate(axes):
        role = str(axis.get("role") or f"axis{i}")
        label = str(axis.get("label") or "").strip()
        q = str(params.get(role) or label).strip()
        if not q or q in seen:
            continue
        seen.add(q)
        queries.append({"qkey": f"axis:{role}", "role": role, "query": q})
    full = (expanded_prompt or "").strip()
    if full and full not in seen:
        queries.append({"qkey": "interaction", "role": "interaction", "query": full})
    return queries


def rrf_merge(
    ranked_lists: Mapping[str, Sequence[Any]],
    *,
    k: int = RRF_K,
    id_fn=None,
) -> list[dict]:
    """Reciprocal Rank Fusion：多查詢排名合併。

    ranked_lists: qkey → 有序列（命中物件）
    id_fn: 物件 → 穩定 id；預設用物件本身（可 hash）或 str(obj)
    回 [{id, score, sources, item}, ...] 依 score 降序。
    """
    if id_fn is None:
        def id_fn(obj):  # noqa: E306 — 內嵌預設
            if hasattr(obj, "sent_id"):
                return ("item", getattr(obj, "sent_id"))
            if hasattr(obj, "chunk_id"):
                return ("work", getattr(obj, "chunk_id"))
            return ("obj", str(obj))

    scores: dict[Any, float] = {}
    sources: dict[Any, set[str]] = {}
    items: dict[Any, Any] = {}
    for qkey, ranked in ranked_lists.items():
        for rank, obj in enumerate(ranked, start=1):
            oid = id_fn(obj)
            scores[oid] = scores.get(oid, 0.0) + 1.0 / (k + rank)
            if getattr(obj, "via", None) == "exact":
                scores[oid] += RRF_EXACT_BONUS
            sources.setdefault(oid, set()).add(qkey)
            items[oid] = obj
    merged = [
        {
            "id": oid,
            "score": scores[oid],
            "sources": sorted(sources[oid]),
            "item": items[oid],
        }
        for oid in scores
    ]
    merged.sort(key=lambda r: (-r["score"], str(r["id"])))
    return merged


def gap_flags(*, axis_hit_counts: Mapping[str, int], total_hits: int,
              ungrounded: bool = False) -> list[str]:
    """依各軸／總命中產出缺口旗標（機械、可複現）。"""
    flags: list[str] = []
    if total_hits <= 0:
        flags.append("no_corpus")
    for role, n in axis_hit_counts.items():
        if n <= 0:
            flags.append(f"no_axis:{role}")
    if ungrounded and total_hits > 0:
        flags.append("ungrounded_hits")
    if "no_corpus" not in flags and "ungrounded_hits" not in flags and total_hits > 0:
        # 有命中但僅單軸覆蓋 → 交互橋薄弱
        covered = sum(1 for n in axis_hit_counts.values() if n > 0)
        if covered == 1 and len(axis_hit_counts) >= 2:
            flags.append("single_axis_only")
    return flags


def label_anchor_tokens(label: str) -> list[str]:
    """從軸 label 抽出落地錨點（確定性；非領域 hardcode）。

    含：原字串／去分隔符字串；CJK run 之 3–4 字 n-gram＋整段(≥3)；
    短 CJK run(≤2)整段；拉丁詞 ≥3 字。避免單用「原理」等 2 字泛詞誤綠。
    """
    lab = str(label or "").strip()
    if not lab:
        return []
    anchors: list[str] = [lab]
    cleaned = _LABEL_SEP_RE.sub("", lab)
    if cleaned and cleaned != lab:
        anchors.append(cleaned)
    for run in _CJK_RUN_RE.findall(cleaned or lab):
        if len(run) <= 2:
            anchors.append(run)
            continue
        anchors.append(run)
        for n in (3, 4):
            if len(run) < n:
                continue
            for i in range(0, len(run) - n + 1):
                anchors.append(run[i : i + n])
    for m in _LATIN_WORD_RE.finditer(lab):
        anchors.append(m.group(0))
    out: list[str] = []
    seen: set[str] = set()
    for a in anchors:
        key = a.lower()
        if len(a) < 2 or key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def axis_labels_ungrounded(
    axis_labels: Sequence[str],
    top_hits: Sequence[Mapping[str, Any]],
    *,
    min_label_len: int = 2,
) -> bool:
    """軸 label 錨點是否「全部」未出現於命中 title／snippet／repr（大小寫不敏感）。

    True＝ungrounded（語意 top‑k 假命中常見）。空 label 清單→False。
    校準：複合軸標（如「太陽能…核心」）可用 ≥3 字 CJK 錨點落地，
    不放寬到無錨點的近鄰假綠（ZZZZ-NONEXISTENT 仍 fail）。
    """
    labels = [str(x).strip() for x in (axis_labels or []) if str(x).strip()]
    labels = [x for x in labels if len(x) >= min_label_len]
    if not labels:
        return False
    if not top_hits:
        return True
    anchors: list[str] = []
    for lab in labels:
        anchors.extend(label_anchor_tokens(lab))
    if not anchors:
        return False
    blob_parts: list[str] = []
    for h in top_hits:
        blob_parts.append(str(h.get("title") or ""))
        blob_parts.append(str(h.get("snippet") or ""))
        blob_parts.append(str(h.get("repr") or ""))
    blob = "\n".join(blob_parts).lower()
    return not any(a.lower() in blob for a in anchors)


def spurious_risk(*, axis_hit_counts: Mapping[str, int], multi_source_hits: int, total_hits: int) -> str:
    """粗估假相關風險：字面多、跨軸共現少 → high。"""
    if total_hits <= 0:
        return "n/a"
    covered = sum(1 for n in axis_hit_counts.values() if n > 0)
    if covered >= 2 and multi_source_hits >= 1:
        return "low"
    if covered >= 2:
        return "medium"
    if total_hits >= 3 and covered <= 1:
        return "high"
    return "medium"


def citation_brief(obj: Any, *, text_max: int = 80) -> dict:
    """命中摘要（id＋短 snippet；不灌全文）。"""
    text = (getattr(obj, "text", None) or "")[:text_max]
    if hasattr(obj, "sent_id"):
        return {
            "kind": "item",
            "sent_id": getattr(obj, "sent_id", None),
            "item_id": getattr(obj, "item_id", None),
            "title": getattr(obj, "item_title", None),
            "domain": getattr(obj, "domain", None),
            "via": getattr(obj, "via", None),
            "score": float(getattr(obj, "score", 0.0) or 0.0),
            "snippet": text,
        }
    if hasattr(obj, "chunk_id"):
        return {
            "kind": "work",
            "chunk_id": getattr(obj, "chunk_id", None),
            "work_id": getattr(obj, "work_id", None),
            "title": getattr(obj, "work_title", None),
            "thinker": getattr(obj, "thinker", None),
            "score": float(getattr(obj, "score", 0.0) or 0.0),
            "snippet": text,
        }
    return {"kind": "unknown", "repr": str(obj)[:text_max]}


def summarize_probe_result(
    *,
    probe_id: str,
    arity: int,
    interaction_kind: str,
    expanded_prompt: str,
    axes: Sequence[Mapping[str, Any]],
    queries: Sequence[Mapping[str, Any]],
    ranked_lists: Mapping[str, Sequence[Any]],
    merged: Sequence[Mapping[str, Any]],
    top_n: int = 8,
) -> dict:
    """組裝單探針結果 dict（stdout／report／ledger 共用）。"""
    axis_roles = [str(a.get("role") or f"axis{i}") for i, a in enumerate(axes)]
    axis_hit_counts = {
        role: len(ranked_lists.get(f"axis:{role}", []) or [])
        for role in axis_roles
    }
    interaction_hits = len(ranked_lists.get("interaction", []) or [])
    multi = sum(1 for m in merged if len(m.get("sources") or []) >= 2)
    total = len(merged)
    tops = []
    for m in list(merged)[:top_n]:
        brief = citation_brief(m["item"], text_max=160)
        brief["rrf"] = round(float(m["score"]), 6)
        brief["sources"] = list(m.get("sources") or [])
        tops.append(brief)
    # 證據路徑：合併 top ∪ 各軸 ranked 命中（防 RRF 淹沒字面 exact）
    grounding_hits: list[dict] = list(tops)
    seen_g: set[tuple] = set()
    for h in grounding_hits:
        seen_g.add((h.get("kind"), h.get("sent_id") or h.get("chunk_id") or h.get("title")))
    for role in axis_roles:
        for obj in list(ranked_lists.get(f"axis:{role}", []) or [])[:top_n]:
            brief = citation_brief(obj, text_max=160)
            key = (brief.get("kind"), brief.get("sent_id") or brief.get("chunk_id") or brief.get("title"))
            if key in seen_g:
                continue
            seen_g.add(key)
            brief["sources"] = [f"axis:{role}"]
            grounding_hits.append(brief)
    # 軸落地校驗：優先用 axis:* query 字串，否則用 axis label
    axis_labels = [
        str(q.get("query") or "").strip()
        for q in queries
        if str(q.get("qkey") or "").startswith("axis:")
    ]
    if not axis_labels:
        axis_labels = [str(a.get("label") or "").strip() for a in axes]
    ungrounded = axis_labels_ungrounded(axis_labels, grounding_hits)
    flags = gap_flags(
        axis_hit_counts=axis_hit_counts, total_hits=total, ungrounded=ungrounded,
    )
    risk = spurious_risk(
        axis_hit_counts=axis_hit_counts,
        multi_source_hits=multi,
        total_hits=total,
    )
    # 無落地字串卻「低假相關」＝誤導；升為 high（與 KH7 fail 對齊）
    if ungrounded and risk == "low":
        risk = "high"
    return {
        "probe_id": probe_id,
        "arity": arity,
        "interaction_kind": interaction_kind,
        "expanded_prompt": expanded_prompt,
        "axes": [dict(a) for a in axes],
        "queries": [dict(q) for q in queries],
        "axis_hit_counts": axis_hit_counts,
        "interaction_hits": interaction_hits,
        "merged_hits": total,
        "multi_source_hits": multi,
        "gap_flags": flags,
        "spurious_risk": risk,
        "top_hits": tops,
        "grounding_hits": grounding_hits[:32],
        "ungrounded_hits": ungrounded,
        "advise_ok": None,
        "pme_candidate": False,
    }


def _selftest() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    expanded = expand_prompt(
        "依「{{principle}}」如何使用「{{ai_axis}}」來強化「{{tech_domain}}」？",
        {"principle": "第一性原理", "ai_axis": "AI 模型", "tech_domain": "太陽能材料研發技術核心"},
    )
    check("expand 三槽實例化", "第一性原理" in expanded and "AI 模型" in expanded and "太陽能" in expanded)
    check("expand 缺槽保留", "{{missing}}" in expand_prompt("x{{missing}}y", {}))

    axes = normalize_axes(
        [{"role": "principle", "label": "第一性原理"},
         {"role": "method", "label": "AI 模型"},
         {"role": "domain", "label": "太陽能材料研發技術核心"}],
    )
    check("normalize_axes 長度 3", len(axes) == 3)
    check("normalize 空→二元投影", len(normalize_axes([], knowhow_axis="A", raw_axis="B")) == 2)

    qs = build_queries(expanded_prompt=expanded, axes=axes, template_params={
        "principle": "第一性原理", "ai_axis": "AI 模型", "tech_domain": "太陽能材料研發技術核心",
    })
    check("queries 含 interaction", any(q["qkey"] == "interaction" for q in qs))
    check("queries ≥ arity+1 或去重後≥2", len(qs) >= 2)

    # RRF：兩路同 id 應升權
    class _H:
        def __init__(self, sid):
            self.sent_id = sid
            self.text = f"t{sid}"
            self.score = 0.5

    merged = rrf_merge({
        "axis:a": [_H(1), _H(2)],
        "axis:b": [_H(2), _H(3)],
    })
    check("RRF 共現 id=2 排前", merged[0]["id"] == ("item", 2))
    check("RRF sources 含兩路", set(merged[0]["sources"]) == {"axis:a", "axis:b"})

    flags = gap_flags(axis_hit_counts={"a": 0, "b": 1}, total_hits=1)
    check("gap 含 no_axis:a", "no_axis:a" in flags)
    check("無命中→no_corpus", "no_corpus" in gap_flags(axis_hit_counts={"a": 0}, total_hits=0))
    check("spurious high 單軸多命中",
          spurious_risk(axis_hit_counts={"a": 5, "b": 0}, multi_source_hits=0, total_hits=5) == "high")
    check("spurious low 跨軸共現",
          spurious_risk(axis_hit_counts={"a": 2, "b": 2}, multi_source_hits=1, total_hits=3) == "low")

    summary = summarize_probe_result(
        probe_id="RKI-FP-AI-SOLAR",
        arity=3,
        interaction_kind="kh_x_kh_x_kh",
        expanded_prompt=expanded,
        axes=axes,
        queries=qs,
        ranked_lists={"axis:principle": [_H(1)], "interaction": [_H(1), _H(9)]},
        merged=merged[:3],
    )
    check("summary 有 probe_id", summary["probe_id"] == "RKI-FP-AI-SOLAR")
    check("summary 禁寫死答案樹欄", "answer_tree" not in summary and summary.get("pme_candidate") is False)
    check("citation_brief item", citation_brief(_H(7))["kind"] == "item")

    check(
        "ungrounded：無意義軸+無關命中",
        axis_labels_ungrounded(
            ["ZZZZ-NONEXISTENT-AXIS-ALPHA"],
            [{"title": "論衡", "snippet": "古之傳文"}],
        ) is True,
    )
    check(
        "grounded：label 出現於 title",
        axis_labels_ungrounded(
            ["第一性原理"],
            [{"title": "第一性原理筆記", "snippet": "…"}],
        ) is False,
    )
    check(
        "錨點校準：複合 label 靠 3 字 n-gram",
        axis_labels_ungrounded(
            ["太陽能材料研發技術核心"],
            [{"title": "rdai_全球太陽能資料來源探測報告", "snippet": "polysilicon"}],
        ) is False,
    )
    check(
        "錨點不假綠：僅「原理」不落地第一性原理",
        axis_labels_ungrounded(
            ["第一性原理"],
            [{"title": "取得當月第一天", "snippet": "原理同取得最後一天"}],
        ) is True,
    )
    check("anchor 含 太陽能", "太陽能" in label_anchor_tokens("太陽能材料研發技術核心"))
    empty_axes = [{"role": "a", "label": "ZZZZ-NONEXISTENT-AXIS-ALPHA"},
                  {"role": "b", "label": "ZZZZ-NONEXISTENT-AXIS-BETA"}]
    empty_qs = build_queries(
        expanded_prompt="「ZZZZ-NONEXISTENT-AXIS-ALPHA」與「ZZZZ-NONEXISTENT-AXIS-BETA」",
        axes=empty_axes,
    )

    class _Junk:
        def __init__(self):
            self.sent_id = 99
            self.text = "論衡篇章"
            self.item_title = "論衡"
            self.score = 0.9

    junk_merged = rrf_merge({"axis:a": [_Junk()], "axis:b": [_Junk()]})
    empty_sum = summarize_probe_result(
        probe_id="KNI-EVAL-EMPTY-CORPUS",
        arity=2,
        interaction_kind="kh_x_kh",
        expanded_prompt=empty_qs[-1]["query"] if empty_qs else "",
        axes=empty_axes,
        queries=empty_qs,
        ranked_lists={"axis:a": [_Junk()], "axis:b": [_Junk()]},
        merged=junk_merged,
    )
    check("empty corpus → ungrounded_hits∈gap",
          "ungrounded_hits" in empty_sum["gap_flags"])
    check("empty corpus → spurious 不維持 low", empty_sum["spurious_risk"] != "low")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.interaction_probe --selftest;免 DB 免 API)")
