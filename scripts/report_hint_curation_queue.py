#!/usr/bin/env python
"""hint→map 策展佇列橋 — approved hint 印成 ready-to-fill 策展段(燃料線的人簽節點,唯讀)。

🎯 這支在做什麼(白話):RAWEVO hint 經 H3 approve 後,**不能**自動進 principle_factor_map——
   map 的 direction/principle_id 皆 NOT NULL 是憲政設計(每列=繫於原理的**有向**假說;I0 明文
   「人+文獻、禁 AI 入庫」)。方向與原理歸屬=假說著作權=人。本支把 approved 且尚未入 map 的
   hint 整理成**策展段草稿**(provenance 數字帶好、原理/文獻/方向留白),供人填完後入
   `curate_pme_map_expand.py` 之 SEED(入 git=人簽軌)→ --apply 入 map。
   燃料線全貌:H3 approve(人)→ **本佇列 curate(人+文獻)** → map → 候選 builder(逐欄 as-of
   防漏設計,另篇)→ I1 有料。approve 只是第一節點,不是終點——誠實說清楚。
守 #1(禁 AI 生成假說入庫;本支零寫入)· #9/#10(provenance 全出自 hint 落帳)· #15 · #29a/d。
SSOT=v2 §5.1 I0/RAWEVO 計畫 H3;map 憲政=PME MAP §3。

執行指令矩陣:
  python scripts/report_hint_curation_queue.py            # 無參數:佇列現況(唯讀)
  python scripts/report_hint_curation_queue.py --stanzas  # 印全部 ready-to-fill 策展段
  python scripts/report_hint_curation_queue.py --selftest # 零 DB 紅綠
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

STANZA = '''# ── 策展段草稿(hint {hint_id};人填三處【】後入 curate_pme_map_expand.py SEED) ──
{{
    "name": "【學派 name,如 microstructure】",
    "sources": [{{"citation": "【真實可核文獻;禁 ai_generated】", "source_type": "paper"}}],
    "principles": [{{
        "statement": "【原理陳述(人撰)】",
        "hypothesis": "{feature}:【何以此交互預期有向?】",
        "factors": [{{"feature": "{feature}", "direction": 【+1 或 -1(文獻預期 IC 方向)】}}],
        # hint 溯源(機械帶好,直接保留):
        "hint_id": "{hint_id}", "provenance": {prov}
    }}]
}}'''


def queue(cur):
    """回 approved 且 feature 尚未入 map 之 hint 列。"""
    cur.execute("""
      SELECT h.hint_id, h.suggested_map->>'feature_hint', h.provenance, h.decided_by,
             h.decided_at::date
      FROM evolution_hypothesis_hint h
      WHERE h.decision='approved'
        AND NOT EXISTS (SELECT 1 FROM principle_factor_map m
                        WHERE m.hint_id = h.hint_id
                           OR m.feature = h.suggested_map->>'feature_hint')
      ORDER BY h.decided_at""")
    return cur.fetchall()


def show(stanzas):
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = queue(cur)
        cur.execute("SELECT count(*) FROM evolution_hypothesis_hint WHERE decision='pending'")
        n_pend = cur.fetchone()[0]
        cur.execute("""SELECT count(*) FROM evolution_hypothesis_hint h
            JOIN principle_factor_map m ON m.hint_id = h.hint_id""")
        n_done = cur.fetchone()[0]
    print(f"── hint 燃料線現況:pending {n_pend} → approved 待策展 {len(rows)} → 已入 map {n_done} ──")
    if not rows:
        print("  (無 approved 待策展;H3 批覆入口=admin /digest 頁)")
        return 0
    for hid, feat, prov, by, at in rows:
        print(f"  {hid}  {feat}  (approved by {by} @{at})")
        if stanzas:
            print(STANZA.format(hint_id=hid, feature=feat,
                                prov=json.dumps(prov or {}, ensure_ascii=False)))
    if not stanzas:
        print("  → 印策展段:--stanzas;填完三處【】入 curate_pme_map_expand.py SEED 後 --apply")
    print("  ⚠ 方向/原理=假說著作權(人+文獻,I0);候選值 builder 另篇(逐欄 as-of 防漏設計)")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    s = STANZA.format(hint_id="raw-h-x", feature="a_x_b_level", prov='{"n_obs": 300}')
    chk("策展段帶 hint 溯源(hint_id+provenance 機械帶好)", "raw-h-x" in s and '"n_obs": 300' in s)
    chk("三處人填留白(學派/文獻/方向)", s.count("【") >= 4)
    chk("方向留白且明示 ±1 語意(文獻預期 IC 方向)", "+1 或 -1" in s)
    chk("禁 ai_generated 提醒在段內", "ai_generated" in s)
    import inspect
    body = inspect.getsource(sys.modules[__name__]).split("def _selftest")[0]
    chk("零寫入(唯讀橋;無 INSERT/UPDATE)",
        "INSERT INTO" not in body and "UPDATE " not in body)
    chk("佇列排除已入 map 者(hint_id 或同名 feature)", "m.hint_id = h.hint_id" in body
        and "m.feature = h.suggested_map->>'feature_hint'" in body)
    chk("燃料線全貌誠實印出(approve≠終點)", "approve 只是第一節點" in body)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="hint→map 策展佇列橋(唯讀;人簽節點)")
    ap.add_argument("--stanzas", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.stanzas:
        return show(True)
    print(__doc__)
    return show(False)


if __name__ == "__main__":
    sys.exit(main())
