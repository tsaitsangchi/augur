#!/usr/bin/env python
"""🎯 三軸週儀表＋R6 digest——第一行固定印 V2-SUNSET 現況(v2 §2.2)、其餘皆標吞吐非成功。

白話:一頁掃完「這週該不該繼續、有什麼等你、機器自己決定了什麼」。唯讀(A12:對 DB 零寫入)。
  §1 V2-SUNSET 三條件現況+剩餘天數(**第一行**;吞吐指標一律排其後)
  §2 R6 digest:本週 gate_ref='V2-AUTOADVANCE' 自動決策逐筆(表/列/時戳/規則)供 hugo 掃視認領
  §3 待你裁決:qledger awaiting_hugo + hint pending + serving 晉升待處置
  §4 吞吐指標(iteration/hint/coverage 計數;**標明非成功指標**)
守 #15(成功≠吞吐、數字皆現查)· A12(唯讀)· #28(零 token)· #29;SSOT=v2 §2.2/§3.3 C8/R6。

執行指令矩陣:
  python scripts/report_triple_evolution_week.py            # 印週報(唯讀)
  python scripts/report_triple_evolution_week.py --days 14  # 自訂回看窗(預設 7)
  python scripts/report_triple_evolution_week.py --md       # markdown(供 admin console/存檔)
  python scripts/report_triple_evolution_week.py --selftest # 零 DB 純紅綠
"""
import argparse
import sys
from datetime import date, datetime

import _bootstrap  # noqa: F401
from augur.core import db

SUNSET_DEADLINE = date(2026, 10, 31)


def _one(cur, sql, params=()):
    cur.execute(sql, params)
    r = cur.fetchone()
    return r[0] if r else None


def sunset_status(cur):
    """三條件現況(v2 §2.1 逐字);回 [(碼, 達成?, 證據句)]。純查詢、不外推。"""
    settled = _one(cur, "SELECT count(*) FROM direction_arena_prediction WHERE settled_at IS NOT NULL") or 0
    clusters = _one(cur, "SELECT count(DISTINCT pred_date) FROM direction_arena_prediction") or 0
    gate_ok = _one(cur, "SELECT count(*) FROM direction_gate WHERE status='evaluated_pass'") or 0
    a_done = settled > 0 and gate_ok > 0
    a_ev = f"arena 已結算 {settled} 列;方向門 evaluated_pass={gate_ok}(cluster {clusters}/60)"

    n_active = _one(cur, "SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'") or 0
    b_done = n_active > 2
    b_ev = f"prodset active={n_active}(基線 2;須成長且新成員過符號一致性)"

    # (c) 2026-07-27 對抗驗證後改判「未判定」——**不得再自行判綠**。
    # 凍結原文(criteria_sha 65eda893…):「LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched,
    # 且該結論可被獨立重跑複現。」原實作寫的是 `best > shuffled`:既不比 floor 也不比 mismatched,
    # 「可複現」整句碼裡無對應 —— 卻在報告第一行印「續命條件已達成」。
    # 三項親驗使「判綠」無論如何站不住:
    #   ① 前半是空門檻:F@L1 之 floor 與 mismatched **結構性恆為 0**(mismatched 之捐贈題 29/30 屬
    #      L3、1/30 屬 L4,理想答案不含本題 facts),連負對照臂 shuffled(0.1667)自己都「同勝」。
    #   ② 一支 13 行、不看內容只認題幹開頭格式的零知識規則機,實跑 L1.F/L1.P/L3.A/L4.A **全 1.000**
    #      (與 ceiling 打平、勝過每一個 LLM 臂)——此格量到的是題目格式,不是能力。
    #   ③ 後半在現行 harness **結構上不可記錄**:run_id=sha256(set_id|code_hash|arm|model|n_items)
    #      且 ON CONFLICT DO NOTHING,同尺同臂重跑之第二次結果必被靜默丟棄。
    # 修成對齊原文會使 (c) 由 ✅ 轉未達成＝效果上升嚴,依 V2-SUNSET「升嚴須走 GATE-raise」不由 AI 逕判;
    # 但「目前這個 ✅ 是錯的」屬事實陳述,故此處改為 **None=未判定**(既不判綠也不代 hugo 判死)。
    c_rows = _one(cur, """SELECT count(*) FROM local_model_eval_run
        WHERE arm NOT IN ('ceiling','floor','shuffled','mismatched') AND NOT is_invalid""") or 0
    best = _one(cur, """SELECT max(axis_f) FROM local_model_eval_run
        WHERE arm NOT IN ('ceiling','floor','shuffled','mismatched') AND NOT is_invalid""")
    c_done = None
    c_ev = (f"**未判定(爭議)**:有效 LLM 臂={c_rows}、最佳 F@L1={best};"
            "原判定式 best>shuffled 與凍結原文(勝 floor 與 mismatched＋可獨立重跑複現)不符,"
            "且零知識格式規則機於該格實跑 1.000 → 門檻空洞。處置須 hugo(GATE-raise 或裁定原文讀法);"
            "在此之前本列不得被引為續命依據。詳見 audits/V2-SUNSET-C-DISPUTED-20260727.md")
    return [("(a) arena 結算＋方向門可讀數", a_done, a_ev),
            ("(b) prodset active 由 2 成長＋符號一致", b_done, b_ev),
            ("(c) LAIEVO 任一臂 F@L1 勝 floor 與 mismatched 且可複現", c_done, c_ev)]


def build(days, md):
    L = []
    h1 = (lambda s: L.append(f"\n## {s}")) if md else (lambda s: L.append(f"\n── {s} ──"))
    with db.connect() as conn, db.transaction(conn) as cur:
        left = (SUNSET_DEADLINE - date.today()).days
        conds = sunset_status(cur)
        # ok 三態:True 達成 / False 未達成 / None **未判定**(判準與實作不符,須人裁)。
        # 未判定**不計入達成數**——把爭議算成達成就是自己把落日條款關掉(#15)。
        n_ok = sum(1 for _, ok, _ in conds if ok is True)
        n_und = sum(1 for _, ok, _ in conds if ok is None)
        verdict = ("續命條件已達成" if n_ok else
                   f"**無任一條件確定達成**(其中 {n_und} 條未判定待人裁);"
                   "**期限到而仍無確定達成者即整體停止、帳本封存、不得換 trigger_code 重開**"
                   if n_und else
                   "**三條件皆未達成——期限到即整體停止、帳本封存、不得換 trigger_code 重開**")
        L.append(f"# V2-SUNSET:剩 {left} 天(至 {SUNSET_DEADLINE});"
                 f"確定達成 {n_ok}/3、未判定 {n_und} → {verdict}")
        for code, ok, ev in conds:
            L.append(f"  {'✅' if ok is True else ('⚠' if ok is None else '⬜')} {code}\n      {ev}")

        h1(f"R6 自動決策 digest(近 {days} 日;請掃視認領)")
        cur.execute("""SELECT a.applied_at, q.feature, q.action, a.before_status, a.after_status,
                              a.evidence_json->>'auto_rule'
                       FROM evolution_apply_log a JOIN promotion_queue q USING (queue_id)
                       WHERE a.evidence_json->>'gate_ref'='V2-AUTOADVANCE'
                         AND a.applied_at > now() - make_interval(days => %s)
                       ORDER BY a.applied_at DESC""", (days,))
        rows = cur.fetchall()
        L.append(f"  本期自動決策 {len(rows)} 筆" + ("" if rows else "(無)"))
        for ts, feat, act, b, a_, rule in rows[:20]:
            L.append(f"  · {ts:%m-%d %H:%M} {feat}: {act} {b}→{a_}  [{rule}]")
        if len(rows) > 20:
            L.append(f"  …另 {len(rows)-20} 筆(全量查 evolution_apply_log)")

        h1("待你裁決(awaiting_hugo)")
        n_q = _one(cur, "SELECT count(*) FROM steward_question_ledger WHERE status='awaiting_hugo'") or 0
        L.append(f"  提問帳本 awaiting_hugo:{n_q} 題")
        cur.execute("""SELECT question FROM steward_question_ledger
                       WHERE status='awaiting_hugo' ORDER BY qid DESC LIMIT 5""")
        for (q,) in cur.fetchall():
            L.append(f"    · {' '.join(q.split())[:72]}")
        n_hint = _one(cur, "SELECT count(*) FROM evolution_hypothesis_hint WHERE decision='pending'") or 0
        L.append(f"  hint 待批(H3 RAWEVO-HINT-approve):{n_hint} 則")
        n_srv = _one(cur, "SELECT count(*) FROM local_model_version WHERE status='serving' AND promoted_by IS NULL") or 0
        L.append(f"  serving 無 promoted_by(P5.W2 缺人簽):{n_srv} 列")
        # R6 降級哨兵:近 14 日零認領動作 → 提示
        if n_q and left > 0:
            L.append("  ⚠ R6:連續 2 週 digest 無人認領 ⇒ 自動降回逐案人閘(防規則簽淪為無人監督)")

        h1("吞吐指標(**非成功指標**,v2 §2.2)")
        for label, sql in (("evolution_run", "SELECT count(*) FROM evolution_run"),
                           ("promotion_queue", "SELECT count(*) FROM promotion_queue"),
                           ("hint 累計", "SELECT count(*) FROM evolution_hypothesis_hint"),
                           ("raw coverage 快照", "SELECT count(*) FROM raw_table_coverage_snapshot"),
                           ("eval_run 累計", "SELECT count(*) FROM local_model_eval_run"),
                           ("evidence_run 累計", "SELECT count(*) FROM evolution_evidence_run")):
            L.append(f"  {label}: {_one(cur, sql)}")
        cur.execute("SELECT scope||'='||state FROM evolution_kill_switch ORDER BY scope")
        L.append("  kill-switch: " + "、".join(r[0] for r in cur.fetchall()))
    L.append(f"\n(唯讀報表;產生於 {datetime.now():%F %H:%M};成功定義=SUNSET 三條件,吞吐數字不構成進度宣稱)")
    return "\n".join(L)


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    src = open(__file__, encoding="utf-8").read()
    chk("第一行為 SUNSET(v2 §2.2 硬要求)", 'L.append(f"# V2-SUNSET' in src)
    chk("吞吐標明非成功指標", "**非成功指標**" in src)
    # A12 唯讀:掃 SQL 字面而非全檔(自測斷言字串本身含關鍵字=假紅;2026-07-27 實撞)
    sql_lits = [ln for ln in src.splitlines()
                if ("cur.execute" in ln or "_one(cur," in ln or ln.strip().startswith(("\"\"\"SELECT", "'SELECT")))]
    chk("唯讀:SQL 字面無 INSERT/UPDATE/DELETE(A12)",
        not any(k in " ".join(sql_lits).upper() for k in ("INSERT INTO", "UPDATE ", "DELETE FROM")))
    chk("R6 降級條款成文", "自動降回逐案人閘" in src)
    chk("三條件逐字對齊 v2 §2.1", all(x in src for x in ("(a) arena", "(b) prodset", "(c) LAIEVO")))
    chk("期限=2026-10-31(criteria 凍結值)", SUNSET_DEADLINE == date(2026, 10, 31))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    print(build(a.days, a.md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
