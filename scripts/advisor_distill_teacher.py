#!/usr/bin/env python
"""S4 Claude teacher gold 生成【骨架 — 預設不放量;耗 Claude usage、須人拍板(#28/DP1)】。

🎯 這支在做什麼(白話):對每筆已建 context(真實檢索 + expected label),交 **Claude teacher**
   生**行為正確的 gold 白話答**寫回 advisor_distill_context.target_response——
     · 情境 2/3(out-of-corpus / impossible)→ 誠實 decline/hedge 示範(不套三姿態、不引經據典);
     · 情境 1(in-corpus)→ 忠實推理 + [N] 引用(數字只轉 payload、事實 ⊂ context)。
   Claude **只教 behavior、不供事實**(界線-B):gold 內任何事實斷言後續 S5 硬驗 ⊂ context、不過即丟。

   **⚠ 本檔為骨架、預設不放量**:S4 = 耗 Claude usage(#28、DP1 人拍板)。--run 需 --confirm 且
   偵測到 teacher 憑證/機制才執行;否則印「teacher 機制未定/未授權」並 exit,不自行燒 usage。
   teacher 呼叫機制(build_teacher_messages 已備好 messages)可接:(A) Anthropic API(需 ANTHROPIC_API_KEY,
   .env 現無)、(B) workflow 內 Claude agents、(C) 手動貼 Claude UI 回填——由用戶拍板後接線 _call_teacher。
   **冪等 + 游標**:只處理 target_response IS NULL 者;限額錯誤即停可續(#24/#28)。
守 #1(Claude 只教行為、事實由 S5 驗 ⊂ context)· #28(usage-aware、預設不放量、限額即停)·
   #6(冪等游標 resume)· 憲章 v1.34.0(Claude-as-teacher 自問自答,作用域執行層)· CLAUDE #29。
   計畫 SSOT=reports/augur_advisor_selfqa_training_plan_20260706.md §S4 · DP1 · §⑦。

執行指令矩陣:
  python scripts/advisor_distill_teacher.py                       # 無參數=印矩陣 + 現況 + teacher 機制偵測(安全)
  python scripts/advisor_distill_teacher.py --preview 3           # 唯讀:印 3 題 teacher prompt(不呼叫、供人審)
  python scripts/advisor_distill_teacher.py --run --confirm       # 放量生 gold(耗 usage;須 teacher 機制已接線)
"""
import argparse
import json
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db

_TEACHER_SYSTEM = """你是 augur advisor 的行為示範老師(teacher)。你只示範「該怎麼誠實地回答」,不供事實。
鐵律:
1. 若 expected=DECLINE(語料庫無此專題,如太陽能製程/半導體/生醫術語):誠實說明 augur 語料庫無此主題,
   可給一句標註「以下為通用常識、非出自 augur 語料」的簡短說明,但**不套三姿態、不引經據典、不編造細節數字**。
2. 若 expected=REFUSE(未來預測/保證語/即時個股數據/離題創作):婉拒,說明 augur 不做未來預測、不提供即時報價、
   只解讀已算好的真實預測與哲學素養。
3. 若 expected=ANSWER(in-corpus 哲學/投資概念,有相關 context):據下方逐字 context 忠實推理,
   引用時標 [N];**任何事實/數字/古典出處必須來自 context,不得外插你自己的知識**。
回答繁體中文、簡潔。"""


def build_teacher_messages(query, expected, context):
    """組 teacher 呼叫用 messages(system + user 含真實 context)。純組裝、不呼叫任何 API。"""
    cites = context.get("citations", [])
    ctx_lines = [f"[{i+1}] {c.get('work_title') or c.get('item_title','')}: {c.get('text','')}"
                 for i, c in enumerate(cites)] or ["(檢索無結果——若 expected=ANSWER 但無 context,仍須誠實 decline)"]
    user = (f"expected 行為 = {expected}\n問題:{query}\n\n可用真兆 context(逐字檢索;事實只能來自這裡):\n"
            + "\n".join(ctx_lines))
    return [{"role": "system", "content": _TEACHER_SYSTEM},
            {"role": "user", "content": user}]


def detect_teacher_mechanism():
    """偵測可用 teacher 機制(誠實回報,不自行決定放量)。回 (available, note)。"""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True, "偵測到 ANTHROPIC_API_KEY → 可接 (A) Anthropic API(須人拍板放量、#28)"
    return False, ("未偵測到 ANTHROPIC_API_KEY(.env 現無)。teacher 機制待用戶拍板:"
                   "(A) 設 ANTHROPIC_API_KEY 走 API / (B) workflow 內 Claude agents / (C) 手動貼 Claude UI 回填。")


def _call_teacher(messages):
    """實際呼叫 Claude teacher——**待用戶拍板機制後接線**(A/B/C)。骨架階段 raise。"""
    raise NotImplementedError(
        "teacher 呼叫機制未接線。build_teacher_messages 已備好 messages;"
        "用戶拍板 A(API)/B(workflow)/C(手動)後於此接線,再 --run --confirm。")


def preview(cur, n):
    cur.execute(
        "SELECT q.question, q.expected, c.context FROM advisor_distill_context c "
        "JOIN advisor_distill_question q USING(question_id) "
        "WHERE c.target_response IS NULL ORDER BY c.context_id LIMIT %s", (n,))
    rows = cur.fetchall()
    if not rows:
        print("  無 pending gold(全部已生 or 尚無 context)。")
        return
    for query, expected, context in rows:
        msgs = build_teacher_messages(query, expected, context)
        print("=" * 72)
        print(f"[expected={expected}] {query}")
        print("--- teacher user message ---")
        print(msgs[1]["content"][:600])


def run(conn, confirm):
    available, note = detect_teacher_mechanism()
    if not confirm:
        sys.exit("✗ --run 為放量(耗 usage、DP1),須 --confirm。")
    if not available:
        sys.exit(f"✗ teacher 機制未就緒、不放量:{note}")
    with db.transaction(conn) as cur:
        cur.execute("SELECT c.context_id, q.question, q.expected, c.context "
                    "FROM advisor_distill_context c JOIN advisor_distill_question q USING(question_id) "
                    "WHERE c.target_response IS NULL ORDER BY c.context_id")
        pending = cur.fetchall()
    model = os.environ.get("DISTILL_TEACHER_MODEL", "claude-opus-4-8")
    done = 0
    for cid, query, expected, context in pending:
        messages = build_teacher_messages(query, expected, context)
        gold = _call_teacher(messages)                        # 限額錯誤即停可續(#28);骨架階段 raise
        with db.transaction(conn) as cur:
            cur.execute("UPDATE advisor_distill_context SET target_response=%s, teacher_model=%s, "
                        "teacher_at=now() WHERE context_id=%s", (gold, model, cid))
        done += 1
    print(f"  生成 {done} gold(model={model})。下一步 S5 硬校驗。")


def stats(cur):
    cur.execute("SELECT count(*) FILTER (WHERE target_response IS NULL), count(*) FROM advisor_distill_context")
    pending, total = cur.fetchone()
    print(f"── S4 現況 ── context {total}、待生 gold {pending}、已生 {total-pending}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    args, _ = ap.parse_known_args()

    with db.connect() as conn:
        if args.run:
            run(conn, args.confirm)
            return
        with db.transaction(conn) as cur:
            if args.preview:
                preview(cur, args.preview)
                return
            print(__doc__.split("執行指令矩陣:")[1])
            stats(cur)
        available, note = detect_teacher_mechanism()
        print(f"\n── teacher 機制偵測 ── available={available}\n  {note}")


if __name__ == "__main__":
    main()
