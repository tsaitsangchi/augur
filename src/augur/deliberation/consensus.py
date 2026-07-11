"""多視角共識聚合 — 同題 N lens 之 claim 去重+三級殺權(P3 完整版;模式 2/4 judge panel)。

🎯 這支在做什麼(白話):同一題目跑 N 個 lens(各成 session),把它們的 claim **依錨點去重**再聚合裁決——
   一個弱模型單視角會漏、會偏;多視角掃過同一標的,交集才是強訊號。**三級殺權(語意 SSOT)**:
   ① oracle 反證(refuted)=**單票即殺**(工具說假就是假,不投票);
   ② 純意見分歧(全 escalated/undecidable,無 oracle 定論)=需**全票**同向才採、否則保留人裁;
   ③ 多數非全票=**降序**呈現(標記分歧度、不擅自 confirmed)。
   **關鍵:confirmed 仍唯 verifiers.verify_claim 之確定性 verdict 可寫**(consensus 只聚合已裁決結果、
   絕不自行升 confirmed)——多數決不鬆機械鎖(#15;弱模型多數不能造真)。

守 #15(oracle 反證優先於任何多數;consensus 不寫 confirmed)· #12(去重鍵=verifier+anchor)。
"""
from collections import defaultdict


def dedup_key(claim_row):
    """去重鍵=(assigned_verifier, 正規化 anchor)——同一機械檢查不論幾個 lens 提、算一個。"""
    return (claim_row["assigned_verifier"], (claim_row["anchor"] or "").strip().lower())


def aggregate(claim_rows):
    """聚合多 lens 之已裁決 claim(每列須含 verifier/anchor/status/claim_text/lens)。
    回 [{key, claim_text, verifier, anchor, verdict, support, lenses, dissent}] ——
    verdict∈{confirmed,refuted,contested,escalated};三級殺權見模組 docstring。"""
    groups = defaultdict(list)
    for r in claim_rows:
        groups[dedup_key(r)].append(r)
    out = []
    for key, rows in groups.items():
        statuses = [r["status"] for r in rows]
        lenses = sorted({r.get("lens") or r.get("perspective") for r in rows})
        n = len(rows)
        # ① oracle 反證單票即殺(工具說假=假,不投票)
        if any(s == "refuted" for s in statuses):
            verdict = "refuted"
        # confirmed:任一 oracle 確定性 confirmed 即成立(oracle 為真兆源、非多數;#15)
        elif any(s == "confirmed" for s in statuses):
            verdict = "confirmed"
        # ② 全數升級/未定=無 oracle 定論 → escalated(需人裁,不擅自採)
        elif all(s in ("escalated", "undecidable", "pending") for s in statuses):
            verdict = "escalated"
        else:
            verdict = "contested"   # 混合但無 confirmed/refuted → 標分歧
        support = sum(1 for s in statuses if s == verdict)
        out.append({"key": key, "claim_text": rows[0]["claim_text"], "verifier": key[0],
                    "anchor": rows[0]["anchor"], "verdict": verdict, "support": support,
                    "n_lens": n, "lenses": lenses, "dissent": n - support})
    # 降序:confirmed/refuted(有 oracle 定論)在前,分歧度低者在前
    _rank = {"refuted": 0, "confirmed": 0, "contested": 1, "escalated": 2}
    out.sort(key=lambda x: (_rank.get(x["verdict"], 9), x["dissent"], -x["support"]))
    return out


def summarize(agg):
    """一句話統計(供報告尾)。"""
    from collections import Counter
    c = Counter(a["verdict"] for a in agg)
    return f"聚合 {len(agg)} 獨立檢查:confirmed {c['confirmed']} / refuted {c['refuted']} / " \
           f"contested {c['contested']} / escalated {c['escalated']}(oracle 反證單票即殺、多數不造真)"
