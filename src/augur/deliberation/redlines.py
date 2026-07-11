"""redline consult — 治權觸線強制升級通道(D6;補完計畫 §4:9 列死設定接電)。

🎯 這支在做什麼(白話):deliberation_redline_trigger(4 antileakage_column + 5 doctrine_file)過去零
   consumer——本模組讓 insert_claim 於**快路之前** consult:claim/anchor 命中觸線(anti-leakage 時點欄
   /治權檔)→ assigned_verifier 強制改 human_claude(+provenance.redline 留痕)→ verify_claim 走
   escalation reason='red_line_category'。**語意**:治權判準/anti-leakage 欄相關宣稱不得由弱模型+oracle
   逕行機裁——決策層人拍板(#19/#26),oracle 證據可附供人參考。redline 命中=快路豁免不了。

守 #19/#26(治權判準人拍板)· #12(consult 單一住所)· #10(命中留痕 kind/pattern)。
"""
_CACHE = None   # process cache;常駐服務重啟即刷新(#7)


def _triggers(cur):
    global _CACHE
    if _CACHE is None:
        cur.execute("SELECT kind, pattern FROM deliberation_redline_trigger")
        _CACHE = cur.fetchall()
    return _CACHE


def consult(cur, claim_text, anchor, verifier):
    """命中觸線 → 回 {kind, pattern};未命中 → None。
    antileakage_column:claim/anchor 含觸線欄名(如 TaiwanStockDividend.AnnouncementDate 之欄部);
    doctrine_file:file_grep 錨路徑含觸線檔。"""
    blob = f"{claim_text}\n{anchor or ''}"
    for kind, pattern in _triggers(cur):
        if kind == "antileakage_column":
            col = pattern.split(".")[-1]                        # 欄部(表.欄 之欄)
            if pattern in blob or col in blob:
                return {"kind": kind, "pattern": pattern}
        elif kind == "doctrine_file":
            if verifier == "file_grep" and pattern in (anchor or ""):
                return {"kind": kind, "pattern": pattern}
            if pattern in blob:
                return {"kind": kind, "pattern": pattern}
    return None
