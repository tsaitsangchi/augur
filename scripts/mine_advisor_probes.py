#!/usr/bin/env python
"""chat 真實問答 → 進化燃料候選礦工(P-B)——唯讀掃 chat_message,候選落 advisor_probe_candidate。

🎯 這支在做什麼(白話):平台的真實使用軌跡就是部署域分布(v2 §0.5:實證教材 87% 是文獻 metadata,
   與真實提問分布脫節)。本支把 chat 分三類收成**候選**(全部 pending、人審才升):
     chat_decline  guard 拒答「知識庫中無此內容」→ 天然 L3/L4 題材(真實地問了、庫真的沒有)
     chat_ambig    回覆含多筆/歧義/請指明 → 消歧義題材
     chat_gold     guard_pass 之實答(非拒答) → gold 候選(答案一併收,provenance=chat)
                   ⚠實查 2026-07-28:chat writer 從不填 guard_pass(85 則全 NULL)→ gold 現實上=0;
                   正解=chat 服務寫 assistant 訊息時落 guard_pass(待辦,不在本支鬆判準)
   **硬界**:①凍結集永不加題——approved_eval 只入未來新 set_id(升級不在本支,人審後另跑)
   ②私有 session 整段跳過(mode 非白名單即跳,fail-closed)③候選內容不出本機不入 git。
守 #1(候選≠題,人審才升)· #8(唯讀掃描)· #15(dedup 防重;計數誠實印)· #26(H 閘=人審)· #29a/d。
SSOT=整合計畫 P-B(reports/augur_advisor_evolution_integration_plan_20260727.md §二)。

執行指令矩陣:
  python scripts/mine_advisor_probes.py            # 無參數:現況(候選分佈,唯讀)
  python scripts/mine_advisor_probes.py --run      # 增量挖掘(冪等;dedup 防重)
  python scripts/mine_advisor_probes.py --run --dry-run   # 只算不寫
  python scripts/mine_advisor_probes.py --selftest # 零 DB 紅綠(分類邏輯)
"""
import argparse
import hashlib
import re
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DECLINE_RE = re.compile(r"知識庫中無此內容|查無|無相關內容")
AMBIG_RE = re.compile(r"多筆|歧義|請指明|哪一(篇|筆|個)")
MODE_ALLOW = ("chat",)          # session mode 白名單;名單外(未知/私有)整段跳過=fail-closed
MIN_Q_LEN = 6                   # 過短問句(如「?」)無題材價值
MIN_GOLD_A_LEN = 40             # gold 候選之最短答長(太短=寒暄,非知識答)


def _dedup(q):
    return hashlib.sha256(re.sub(r"\s+", "", q).lower().encode()).hexdigest()[:16]


def classify(question, answer, guard_pass):
    """回 source_kind|None(None=不收)。優先序:拒答>歧義>gold(嚴格條件)。"""
    if not question or len(question.strip()) < MIN_Q_LEN:
        return None
    a = answer or ""
    if DECLINE_RE.search(a):
        return "chat_decline"
    if AMBIG_RE.search(a):
        return "chat_ambig"
    if guard_pass and len(a) >= MIN_GOLD_A_LEN:
        return "chat_gold"
    return None


def mine(dry):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("""
          SELECT m.session_id, m.message_id, m.content AS answer, m.guard_pass,
                 (SELECT u.content FROM chat_message u
                  WHERE u.session_id=m.session_id AND u.role='user' AND u.message_id < m.message_id
                  ORDER BY u.message_id DESC LIMIT 1) AS question
          FROM chat_message m
          JOIN chat_session s ON s.session_id = m.session_id
          WHERE m.role='assistant' AND s.mode = ANY(%s)
          ORDER BY m.message_id""", (list(MODE_ALLOW),))
        rows = cur.fetchall()
        made, skip_dup, by_kind = 0, 0, {}
        seen = set()      # 批內去重:dry 模式沒有 DB 回看,無此集合會把同題重覆計成新候選(實測 52 vs 9)
        for sid, mid, ans, gp, q in rows:
            kind = classify(q, ans, gp)
            if kind is None:
                continue
            dk = _dedup(q)
            if dk in seen:
                skip_dup += 1
                continue
            cur.execute("SELECT 1 FROM advisor_probe_candidate WHERE dedup_key=%s", (dk,))
            if cur.fetchone():
                skip_dup += 1
                continue
            seen.add(dk)
            by_kind[kind] = by_kind.get(kind, 0) + 1
            made += 1
            if not dry:
                cur.execute("""INSERT INTO advisor_probe_candidate
                    (source_kind, session_id, message_id, question, answer, dedup_key)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (dedup_key) DO NOTHING""",
                    (kind, sid, mid, q, (ans if kind == "chat_gold" else None), dk))
        if not dry:
            conn.commit()
        print(f"掃 assistant 訊息 {len(rows)} 則 → 新候選 {made}({by_kind})、dedup 跳過 {skip_dup}"
              + ("(dry-run:未寫入)" if dry else ""))
        if made and not dry:
            print("→ 人審(H 閘):digest 頁或 SQL 檢視 review_status='pending';"
                  "approved_eval 僅入未來新 set_id(凍結集永不加題)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.advisor_probe_candidate')")
        if cur.fetchone()[0] is None:
            print("  (表未建;先跑 migrate_advisor_probe_ddl.py --apply)")
            return 0
        cur.execute("""SELECT source_kind, review_status, count(*)
            FROM advisor_probe_candidate GROUP BY 1,2 ORDER BY 1,2""")
        rows = cur.fetchall()
        print("  候選分佈:" if rows else "  (0 候選;--run 挖掘)")
        for k, s, n in rows:
            print(f"    {k:14} {s:14} {n}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("拒答→chat_decline", classify("台積電的 PER?", "知識庫中無此內容", False) == "chat_decline")
    chk("歧義→chat_ambig", classify("這篇文獻的作者是誰?", "對應多筆,請指明", True) == "chat_ambig")
    chk("實答→chat_gold(guard_pass+長度)", classify("何謂 as-of?",
        "as-of 口徑指以決策當下可得之資料為準,防止把未來資訊洩漏進特徵;所有 panel 建構一律以此口徑釘住時點。", True) == "chat_gold")
    chk("短答非 gold(寒暄不收)", classify("嗨", "你好!", True) is None)
    chk("guard 未過之實答不收 gold", classify("何謂 as-of?", "a" * 80, False) is None)
    chk("過短問句不收", classify("?", "知識庫中無此內容", False) is None)
    chk("優先序:拒答先於 gold", classify("Q" * 10, "知識庫中無此內容" + "x" * 60, True) == "chat_decline")
    chk("dedup 決定性+空白不敏感", _dedup("a b c") == _dedup("abc"))
    import inspect
    src = inspect.getsource(mine)
    chk("唯讀掃 chat(僅 SELECT chat_*;寫僅入 probe 表)",
        "INSERT INTO advisor_probe_candidate" in src and "UPDATE chat" not in src)
    chk("session mode 白名單 fail-closed(名單外整段跳)", "MODE_ALLOW" in src and MODE_ALLOW == ("chat",))
    chk("gold 才收 answer(拒答/歧義不存回覆)", 'if kind == "chat_gold" else None' in src)
    chk("凍結集永不加題之提醒常駐", "凍結集永不加題" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="chat→進化燃料候選礦工(P-B;唯讀掃描+append-only 候選)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.run:
        return mine(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
