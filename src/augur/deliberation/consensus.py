"""多視角共識聚合 — 同題 N lens 之 claim 去重+三級殺權(P3 完整版;模式 2/4 judge panel)。

🎯 這支在做什麼(白話):同一題目跑 N 個 lens(各成 session),把它們的 claim **依錨點去重**再聚合裁決——
   一個弱模型單視角會漏、會偏;多視角掃過同一標的,交集才是強訊號。**三級殺權(語意 SSOT)**:
   ① oracle 反證(refuted)=**單票即殺**(工具說假就是假,不投票);
   ② 純意見分歧(全 escalated/undecidable,無 oracle 定論)=需**全票**同向才採、否則保留人裁;
   ③ 多數非全票=**降序**呈現(標記分歧度、不擅自 confirmed)。
   **關鍵:confirmed 仍唯 verifiers.verify_claim 之確定性 verdict 可寫**(consensus 只聚合已裁決結果、
   絕不自行升 confirmed)——多數決不鬆機械鎖(#15;弱模型多數不能造真)。

守 #15(oracle 反證優先於任何多數;consensus 不寫 confirmed)· #12(去重鍵=verifier+anchor)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.consensus              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.consensus --selftest   # 純紅綠自測（零 IO）
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


def _selftest():
    """自測（零 DB/零 API #29a）：合成 claim 紅綠測三級殺權——固化「refuted 單票即殺 >
    confirmed > 全升級 escalated > 混合 contested」與去重鍵正規化為回歸鎖(#15/#12)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    def row(status, anchor="a", verifier="v", lens="L"):
        return {"assigned_verifier": verifier, "anchor": anchor,
                "status": status, "claim_text": "c", "lens": lens}

    # 去重鍵:anchor strip+lower、綁 verifier(#12)
    chk("dedup_key 正規化(strip/lower)",
        dedup_key({"assigned_verifier": "s", "anchor": "  Foo  "}) == ("s", "foo"))
    # ① refuted 單票即殺——同組即使有 confirmed 仍判 refuted(oracle 反證 > 多數 #15)
    r = aggregate([row("refuted", lens="L1"), row("confirmed", lens="L2")])
    chk("refuted 單票即殺 > confirmed", len(r) == 1 and r[0]["verdict"] == "refuted")
    # confirmed:任一 oracle confirmed 即成立(無 refuted 時)
    chk("任一 confirmed → confirmed",
        aggregate([row("confirmed"), row("escalated")])[0]["verdict"] == "confirmed")
    # ② 全升級/未定 → escalated(需人裁)
    chk("全 escalated/undecidable → escalated",
        aggregate([row("escalated"), row("undecidable")])[0]["verdict"] == "escalated")
    # ③ 混合(無 confirmed/refuted、非全升級)→ contested
    chk("混合非全升級 → contested",
        aggregate([row("supported"), row("escalated")])[0]["verdict"] == "contested")
    # 同 verifier+anchor 跨 lens 去重成一組;不同 anchor 不併
    chk("同鍵跨 lens 併一組",
        len(aggregate([row("escalated", lens="L1"), row("escalated", lens="L2")])) == 1)
    chk("不同 anchor 不併",
        len(aggregate([row("escalated", anchor="a"), row("escalated", anchor="b")])) == 2)
    # 降序:有 oracle 定論(refuted/confirmed rank 0)排在分歧(escalated rank 2)之前
    ordered = aggregate([row("escalated", anchor="z"), row("confirmed", anchor="a")])
    chk("降序:oracle 定論在分歧前", ordered[0]["verdict"] == "confirmed")
    # summarize:純字串統計、含計數
    s = summarize([{"verdict": "confirmed"}, {"verdict": "refuted"}])
    chk("summarize 回字串含計數", isinstance(s, str) and "confirmed 1" in s and "refuted 1" in s)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.deliberation.consensus --selftest;免 DB 免 API)")
