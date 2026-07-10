#!/usr/bin/env python
"""審議→蒸餾橋接 — (發現,裁決,證據)三元組映射為 advisor_distill QA 題(引擎計畫 §8.5/需求(e))。

🎯 這支在做什麼(白話):把審議引擎「oracle 裁決過」的宣稱轉成蒸餾題庫——每條 confirmed/refuted
   claim(必有 is_deterministic verdict)→ 一題「此宣稱是否成立?」QA(expected=ANSWER、
   situation_label=1〔可答:有機械證據〕、topic_source='deliberation'、topic_ref=claim_id 溯源)。
   下游走既有蒸餾管線(S2 build_context→S3 teacher→S4 validate),本橋零重造。
   **界線(引擎計畫界線-A)**:蒸餾產物零回流預測管線(distill 表已自 augur_predict REVOKE,既有閘);
   escalated/undecidable/pending 不入題(無機械真值=不可教)。

守 #12(下游全複用既有 S2-S4)· #15(只橋 oracle 裁決過者)· #29a。冪等:question UNIQUE ON CONFLICT skip。

執行指令矩陣:
  python scripts/bridge_deliberation_distill.py            # 無參數:可橋接現況(唯讀)
  python scripts/bridge_deliberation_distill.py --run      # 橋接全部已裁決 claims(冪等)
  python scripts/bridge_deliberation_distill.py --run --limit 20 --batch-tag delib_v1
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

Q_TMPL = "以下關於 augur 系統現況的宣稱是否成立?請依知識庫證據回答:「{claim}」"


def eligible(cur, limit=None):
    cur.execute(f"""
        SELECT c.claim_id, c.claim_text, c.status, c.category,
               (SELECT v.evidence FROM deliberation_verdict v
                WHERE v.claim_id=c.claim_id AND v.is_deterministic ORDER BY v.ran_at DESC LIMIT 1)
        FROM deliberation_claim c
        WHERE c.status IN ('confirmed','refuted')
          AND EXISTS (SELECT 1 FROM deliberation_verdict v
                      WHERE v.claim_id=c.claim_id AND v.is_deterministic)
        ORDER BY c.claim_id {f'LIMIT {int(limit)}' if limit else ''}""")
    return cur.fetchall()


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--batch-tag", dest="tag", default="delib_bridge_v1")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        rows = eligible(cur, args.limit)
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            print(f"可橋接(confirmed/refuted+確定性 verdict):{len(rows)} 條")
            cur.execute("SELECT count(*) FROM advisor_distill_question WHERE topic_source='deliberation'")
            print(f"已橋接:{cur.fetchone()[0]} 題")
            return 0
        n_new = 0
        for cid, claim, status, category, _ev in rows:
            cur.execute("""
                INSERT INTO advisor_distill_question
                  (question, situation_label, expected, domain, topic_source, topic_ref, batch_tag)
                VALUES (%s, 1, 'ANSWER', %s, 'deliberation', %s, %s)
                ON CONFLICT (question) DO NOTHING""",
                (Q_TMPL.format(claim=claim[:400]), category, f"claim_id={cid};oracle={status}", args.tag))
            n_new += cur.rowcount
        conn.commit()
        print(f"✓ 橋接 {n_new} 新題(來源 {len(rows)} 條裁決;冪等 skip {len(rows)-n_new});"
              f"下游=advisor_distill_build_context → teacher → validate(既有 S2-S4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
