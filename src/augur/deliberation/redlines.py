"""redline consult — 治權觸線強制升級通道(D6;補完計畫 §4:9 列死設定接電)。

🎯 這支在做什麼(白話):deliberation_redline_trigger(4 antileakage_column + 5 doctrine_file)過去零
   consumer——本模組讓 insert_claim 於**快路之前** consult:claim/anchor 命中觸線(anti-leakage 時點欄
   /治權檔)→ assigned_verifier 強制改 human_claude(+provenance.redline 留痕)→ verify_claim 走
   escalation reason='red_line_category'。**語意**:治權判準/anti-leakage 欄相關宣稱不得由弱模型+oracle
   逕行機裁——決策層人拍板(#19/#26),oracle 證據可附供人參考。redline 命中=快路豁免不了。

守 #19/#26(治權判準人拍板)· #12(consult 單一住所)· #10(命中留痕 kind/pattern)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.redlines              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.redlines --selftest   # 純紅綠自測（零 IO）
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


def _selftest():
    """自測（零 DB/零 API）：預置 _CACHE 合成觸線 → 紅綠測 consult 命中/未中不變式（cur=None、不觸 cursor）。"""
    global _CACHE
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("公開入口存在", callable(consult) and callable(_triggers))
    saved = _CACHE
    try:
        _CACHE = [("antileakage_column", "TaiwanStockDividend.AnnouncementDate"),
                  ("doctrine_file", "docs/原則精華")]   # 預置→_triggers 回 cache、cur 未用（零 IO）
        # antileakage:全 pattern（表.欄）命中
        h = consult(None, "檢查 TaiwanStockDividend.AnnouncementDate 洩漏", None, "sql")
        chk("antileakage 全欄名命中", h is not None and h["kind"] == "antileakage_column")
        # antileakage:僅欄部（表.欄 之欄）亦命中
        h = consult(None, "AnnouncementDate 當日資料", None, "sql")
        chk("antileakage 欄部命中", h is not None and h["kind"] == "antileakage_column")
        # doctrine_file:file_grep 錨路徑含觸線檔命中
        h = consult(None, "宣稱", "docs/原則精華_v1.9.0.md", "file_grep")
        chk("doctrine file_grep 錨命中", h is not None and h["kind"] == "doctrine_file")
        # doctrine_file:非 file_grep 但 pattern 落 blob 亦命中
        h = consult(None, "引用 docs/原則精華 內容", None, "sql")
        chk("doctrine blob 命中", h is not None and h["kind"] == "doctrine_file")
        # 無觸線 → None（快路豁免不了 只作用於命中）
        chk("未命中回 None", consult(None, "普通宣稱無觸線", "some/other/path", "sql") is None)
    finally:
        _CACHE = saved   # 復原 process cache，不留自測污染
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.deliberation.redlines --selftest;免 DB 免 API)")
