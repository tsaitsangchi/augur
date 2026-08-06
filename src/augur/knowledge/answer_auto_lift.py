"""KH0 答對 → 自動抬層至 KH1／KH2（R-hybrid／AUTO-LIFT）。

🎯 這支在做什麼(白話):用 R-cite（答中辨識詞 ⊆ 引文）判定答對後，對 item 引文
   跑 progressive_item(up_to=2)。T2：可機械 activate 來源（system actor；每批最多 1 源；
   需 has_text——沿用 maybe_activate_source）。R-human 可覆寫邊界案。
   **不**經 web／對話裸放行。advise 熱路徑須 `AUGUR_KH0_ANSWER_AUTO_LIFT=1`（預設關）。
守 憲章 KH0·v1.48·T2-go·wire-advise-go· FZ-keep· #15。

執行指令矩陣(本檔=library #18):
  python -m augur.knowledge.answer_auto_lift --selftest
  python -m augur.knowledge.answer_auto_lift   # 印用途
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any, Sequence

from augur.advisor import relevance as rel
from augur.knowledge import auto_admit as aa

RULER_HYBRID = "R-hybrid"
ACTOR = "system:kh0_answer_auto_lift"
UP_TO = 2
# T2：AUTO-LIFT 預設機械 activate；每答批次最多 1 個 source_key
ACTIVATE_SOURCE_DEFAULT = True
MAX_SOURCES_PER_LIFT = 1
# advise 熱路徑旗標（預設 off；wire-advise-go）
ENV_FLAG = "AUGUR_KH0_ANSWER_AUTO_LIFT"
# R-cite：至少命中這麼多答側強詞，且命中率 ≥ 此比例（答無強詞→不抬）
_MIN_HIT = 1
_MIN_RATIO = 0.5


def auto_lift_enabled(explicit: bool | None = None) -> bool:
    """wire-advise 旗。explicit 非 None 覆寫；否則讀 ENV（1/true/yes/on）。預設 False。"""
    if explicit is not None:
        return bool(explicit)
    v = (os.environ.get(ENV_FLAG) or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def query_hash(query: str) -> str:
    return hashlib.sha256((query or "").encode("utf-8")).hexdigest()[:32]


def _answer_tokens(answer: str) -> set[str]:
    """答側強辨識詞 ∪ 數字字面（供 R-cite）。"""
    toks = set(rel._strong_distinctive(answer or ""))
    for m in re.findall(r"\d+(?:\.\d+)?", answer or ""):
        toks.add(m)
    return toks


def _cite_blob(citations: Sequence[Any]) -> str:
    parts = []
    for c in citations or []:
        parts.append(rel._cite_text(c))
    return "\n".join(parts)


def r_cite_evaluate(answer: str, citations: Sequence[Any]) -> dict:
    """R-cite：答中強詞／數字須有足夠比例落在引文連合文本。

    回 {pass, hit, total, ratio, note, tokens_hit, tokens_miss}。
    """
    ans_toks = _answer_tokens(answer)
    if not ans_toks:
        return {
            "pass": False,
            "hit": 0,
            "total": 0,
            "ratio": 0.0,
            "note": "answer_no_distinctive_tokens",
            "tokens_hit": [],
            "tokens_miss": [],
        }
    blob = _cite_blob(citations).lower()
    # 數字與 ascii 用 lower blob；CJK 保持原樣掃描
    blob_raw = _cite_blob(citations)
    hit, miss = [], []
    for t in sorted(ans_toks):
        ok = (t.lower() in blob) if t.isascii() or t.replace(".", "").isdigit() else (t in blob_raw)
        (hit if ok else miss).append(t)
    total = len(ans_toks)
    n_hit = len(hit)
    ratio = n_hit / total if total else 0.0
    passed = n_hit >= _MIN_HIT and ratio >= _MIN_RATIO
    return {
        "pass": passed,
        "hit": n_hit,
        "total": total,
        "ratio": ratio,
        "note": "r_cite_pass" if passed else "r_cite_fail",
        "tokens_hit": hit,
        "tokens_miss": miss,
    }


def item_ids_from_citations(citations: Sequence[Any]) -> list[int]:
    ids = []
    seen = set()
    for c in citations or []:
        iid = getattr(c, "item_id", None)
        if iid is None:
            continue
        iid = int(iid)
        if iid in seen:
            continue
        seen.add(iid)
        ids.append(iid)
    return ids


def hybrid_should_lift(*, cite: dict, human_pass: bool = False) -> bool:
    """R-hybrid：R-cite 過 → 抬；否則僅 human_pass 抬。"""
    if cite.get("pass"):
        return True
    return bool(human_pass)


def lift_items(
    cur,
    item_ids: Sequence[int],
    *,
    apply: bool,
    up_to: int = UP_TO,
    activate_source: bool = ACTIVATE_SOURCE_DEFAULT,
    max_sources: int = MAX_SOURCES_PER_LIFT,
) -> list[dict]:
    """對 items 跑 progressive_item；T2 可機械 activate（每批 ≤max_sources 源）。

    activate 條件沿用 auto_admit：須 source_key ∧ has_text（標題件不靠此放行源）。
    """
    out = []
    sources_armed = 0
    armed_keys: set[str] = set()
    for iid in item_ids:
        before = aa.get_admit_depth(cur, "item", str(iid))
        snap = aa._item_snapshot(cur, int(iid))
        allow_act = False
        sk = (snap or {}).get("source_key")
        if (
            activate_source
            and apply
            and snap
            and sk
            and snap.get("has_text")
            and sk not in armed_keys
            and sources_armed < max_sources
        ):
            allow_act = True
            armed_keys.add(str(sk))
            sources_armed += 1
        r = aa.progressive_item(
            cur,
            int(iid),
            up_to=up_to,
            apply=apply,
            activate_source=allow_act,
        )
        after = r.get("admit_depth_after", before) if r.get("ok") else before
        src_actions = [
            a for a in (r.get("actions") or [])
            if isinstance(a, dict) and a.get("action") in ("approve", "activate", "resume", "activate_error")
        ]
        out.append({
            "item_id": int(iid),
            "ok": bool(r.get("ok")),
            "before": before,
            "after": after,
            "error": r.get("error"),
            "seeded": r.get("seeded"),
            "activate_attempted": allow_act,
            "source_key": sk,
            "source_actions": src_actions,
        })
    return out


def log_lift(
    cur,
    *,
    query: str,
    ruler: str,
    cite: dict,
    human_pass: bool,
    lifted: bool,
    item_ids: Sequence[int],
    results: Sequence[dict],
    note: str = "",
) -> int | None:
    """寫 knowhow_answer_lift_log；表缺 → None（呼叫端可先 migrate）。"""
    if not aa._table_exists(cur, "knowhow_answer_lift_log"):
        return None
    before = {str(r["item_id"]): r["before"] for r in results}
    after = {str(r["item_id"]): r["after"] for r in results}
    act_bits = []
    for r in results:
        if r.get("activate_attempted"):
            act_bits.append(f"activate:{r.get('source_key')}:{r.get('source_actions')}")
    note_full = (note or cite.get("note", "")) + (("｜" + ";".join(act_bits)) if act_bits else "")
    cur.execute(
        """
        INSERT INTO knowhow_answer_lift_log
          (query_hash, ruler, cite_pass, human_pass, lifted, item_ids,
           depths_before, depths_after, note, actor)
        VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s)
        RETURNING lift_id
        """,
        (
            query_hash(query),
            ruler,
            bool(cite.get("pass")),
            bool(human_pass),
            bool(lifted),
            list(item_ids),
            json.dumps(before),
            json.dumps(after),
            note_full,
            ACTOR,
        ),
    )
    row = cur.fetchone()
    return int(row[0]) if row else None


def maybe_auto_lift_after_answer(
    cur,
    *,
    query: str,
    answer: str,
    citations: Sequence[Any],
    apply: bool,
    human_pass: bool = False,
    ruler: str = RULER_HYBRID,
    activate_source: bool = ACTIVATE_SOURCE_DEFAULT,
) -> dict:
    """R-hybrid 核可後抬層；T2 可機械 activate（預設 on；可關）。"""
    cite = r_cite_evaluate(answer, citations)
    ids = item_ids_from_citations(citations)
    do_lift = hybrid_should_lift(cite=cite, human_pass=human_pass) and bool(ids)
    results: list[dict] = []
    if do_lift:
        results = lift_items(
            cur, ids, apply=apply, activate_source=activate_source,
        )
    elif ids:
        results = [
            {
                "item_id": i,
                "ok": True,
                "before": aa.get_admit_depth(cur, "item", str(i)),
                "after": aa.get_admit_depth(cur, "item", str(i)),
                "error": None,
                "seeded": False,
                "activate_attempted": False,
                "source_key": None,
                "source_actions": [],
            }
            for i in ids
        ]
    lift_id = None
    if apply:
        lift_id = log_lift(
            cur,
            query=query,
            ruler=ruler,
            cite=cite,
            human_pass=human_pass,
            lifted=do_lift,
            item_ids=ids,
            results=results,
            note=cite.get("note", ""),
        )
    return {
        "ok": True,
        "ruler": ruler,
        "cite": cite,
        "human_pass": human_pass,
        "lifted": do_lift,
        "item_ids": ids,
        "results": results,
        "lift_id": lift_id,
        "apply": apply,
        "activate_source": activate_source,
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    from types import SimpleNamespace as S

    cites = [S(item_id=1, text="ERP 災難還原演練於 14:55 開始，RTO 實際 4.5 小時", item_title="t")]
    # 答對：專詞＋數字都在引文
    good = r_cite_evaluate("ERP 災難還原 RTO 4.5 小時", cites)
    chk("R-cite pass on grounded answer", good["pass"] is True)
    bad = r_cite_evaluate("量子糾纏超光速通信證實", cites)
    chk("R-cite fail on ungrounded", bad["pass"] is False)
    empty = r_cite_evaluate("。。。", cites)
    chk("R-cite fail on empty tokens", empty["pass"] is False)

    chk("hybrid cite→lift", hybrid_should_lift(cite=good) is True)
    chk("hybrid fail no human", hybrid_should_lift(cite=bad, human_pass=False) is False)
    chk("hybrid fail+human", hybrid_should_lift(cite=bad, human_pass=True) is True)

    ids = item_ids_from_citations([S(item_id=7, text="a"), S(item_id=7, text="b"), S(text="works")])
    chk("item ids dedupe skip works", ids == [7])

    chk("query_hash len", len(query_hash("q")) == 32)
    chk("UP_TO=2", UP_TO == 2)
    chk("ACTOR", ACTOR.startswith("system:"))
    chk("T2 activate default on", ACTIVATE_SOURCE_DEFAULT is True)
    chk("T2 max_sources=1", MAX_SOURCES_PER_LIFT == 1)
    chk("flag default off", auto_lift_enabled() is False)
    chk("flag explicit on", auto_lift_enabled(True) is True)
    chk("flag explicit off", auto_lift_enabled(False) is False)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開: r_cite_evaluate / hybrid_should_lift / maybe_auto_lift_after_answer / lift_items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
