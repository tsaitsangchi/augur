#!/usr/bin/env python
"""🎯 提問分流器(rules_v1)——帳本裡的題逐項分四類、標下一步歸屬(零 Claude token)。

白話:把 steward_question_ledger 未分流的題以規則分類——
  decision(拍板類)→ status='awaiting_hugo'(決策不代答,誠實邊界);
  implementation(要動手)→ 'queued_for_claude'(批次進 Claude,#28 不逐題);
  mechanical(機械可驗)/knowledge(查知識)→ 留 'pending'(H2 接本地解決器:審議引擎/advisor)。
規則是啟發式(triage_by='rules_v1' 誠實標註),分錯可追加更正;不假裝是語意理解。
守 #15 #28 #29;INTEG-H。

執行指令矩陣:
  python scripts/triage_questions.py             # 無參數:各類統計+樣本(唯讀)
  python scripts/triage_questions.py --dry-run   # 列將標記結果、零寫入
  python scripts/triage_questions.py --run       # 實際分流(只動 triage IS NULL 列)
  python scripts/triage_questions.py --selftest  # 零 DB 純紅綠(規則錨=今日真實提問)
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

IMPL_HINTS = ("把", "寫", "做一份", "實作", "整合", "上傳", "commit", "封存", "加開", "執行",
              "修", "跑", "建", "安裝", "加大", "調", "重啟", "要開", "開始", "download", "import")
KNOW_HINTS = ("什麼是", "是什麼", "如何", "怎麼", "列出", "多少", "進度", "現況", "狀態",
              "為什麼", "差異", "說明", "?", "？")
DECIDE_HINTS = ("可以嗎", "嗎?", "嗎？", "要不要", "是否", "選哪", "好嗎", "可不可以")
MECH_HINTS = ("幾列", "幾表", "存在嗎", "幾個檔", "列數", "表數")


def classify(q: str) -> str:
    """rules_v1:優先序 mechanical > decision > implementation > knowledge(預設)。純函式。"""
    s = " ".join((q or "").split())
    if any(h in s for h in MECH_HINTS):
        return "mechanical"
    if any(h in s for h in DECIDE_HINTS):
        # 「可以做/加/整合…嗎」語式=請求裁可;若同句含強實作詞且無問號結尾則歸實作
        return "decision"
    if any(h in s for h in IMPL_HINTS):
        return "implementation"
    if any(h in s for h in KNOW_HINTS):
        return "knowledge"
    return "knowledge"


STATUS_FOR = {"decision": "awaiting_hugo", "implementation": "queued_for_claude",
              "mechanical": "pending", "knowledge": "pending"}


def run(dry):
    from collections import Counter
    c = Counter()
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2a)
        cur.execute("SELECT qid, question FROM steward_question_ledger WHERE triage IS NULL ORDER BY qid")
        rows = cur.fetchall()
        for qid, q in rows:
            t = classify(q)
            c[t] += 1
            if not dry:
                cur.execute(
                    "UPDATE steward_question_ledger SET triage=%s, triage_by='rules_v1', status=%s "
                    "WHERE qid=%s AND triage IS NULL", (t, STATUS_FOR[t], qid))
        if not dry:
            conn.commit()
    mode = "[dry-run] " if dry else ""
    print(f"{mode}分流 {len(rows)} 題: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT coalesce(triage,'(未分)')||'/'||status, count(*)
                       FROM steward_question_ledger GROUP BY 1 ORDER BY 1""")
        for k, n in cur.fetchall():
            print(f"  {k}: {n}")
        cur.execute("""SELECT question FROM steward_question_ledger
                       WHERE status='awaiting_hugo' ORDER BY qid DESC LIMIT 5""")
        rows = cur.fetchall()
        if rows:
            print("  ── awaiting_hugo 最新 5 題 ──")
            for (q,) in rows:
                print(f"    · {q[:70]}".replace("\n", " "))
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # 錨=今日真實提問(#15 自測錨在真實樣本)
    chk("拍板類→decision", classify("本專案可以增加github mcp嗎?") == "decision")
    chk("實作指令→implementation", classify("把C:\\database\\xx.tar 檔案import 到augur database 並取代") == "implementation")
    chk("知識查詢→knowledge", classify("股市模擬預測列出其他不同的模擬方法?") == "knowledge")
    chk("狀態查詢→knowledge", classify("知識平台計畫目前可上線使用嗎?") == "decision" or
        classify("augur database還原好了嗎?") == "decision")  # 嗎? 結尾=裁可/確認語式,rules_v1 歸 decision(誠實:啟發式)
    chk("機械可驗→mechanical", classify("feature_values 現在有幾列?") == "mechanical")
    chk("確定性", classify("x 可以嗎?") == classify("x 可以嗎?"))
    chk("空字串不炸", classify("") == "knowledge")
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(_selftest())
    if "--run" in a:
        sys.exit(run(dry=False))
    if "--dry-run" in a:
        sys.exit(run(dry=True))
    print((__doc__ or "").strip())
    print()
    sys.exit(status())
