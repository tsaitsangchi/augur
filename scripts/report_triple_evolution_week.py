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

# 期限**不得寫死**——判準住 evolution_prereg_gate 且受 criteria_sha 保護,程式另存副本
# 即為「凍結了判準文字卻沒凍結解釋它的程式」之同型缺口(2026-07-31 實犯:當日 GATE-raise
# 把期限由 10-31 改為 07-31 並 supersede 舊列,而本檔仍印 10-31,且其自測還把過期值鎖住)。
# 保留常數僅作**歷史錨**與 DB 不可讀時之誠實標記,不參與任何判定。
SUNSET_DEADLINE_HISTORICAL = date(2026, 10, 31)  # 原始凍結值(V2-SUNSET,已 superseded)


def judge_b(n_active, newcomers, sign_rows, has_tbl, baseline_ts="?"):
    """(b) 之兩要件合取 → (達成?, 說明)。**純函式**——自測餵真輸入驗真行為。

    刻意抽成純函式而非留在 build() 內：字面斷言（`"xxx" in src`）驗不到這種邏輯，
    且會掃到自己那份字串副本而恆綠（2026-07-31 一日內實犯三次之型態）。

    要件一：active 由 2 成長。要件二：**每一新成員**通過符號一致性檢查。
    fail-closed：查無紀錄＝未通過（不是通過）；落帳表未建亦然——「沒證據」≠「有通過」。
    """
    unchecked = [f for f in newcomers if sign_rows.get(f) != "PASS"]
    # has_tbl 必須進**判定**而非只進訊息:表不存在＝證據載體不存在,任何 PASS 都無所附麗。
    # （2026-07-31:本行原只寫 `bool(newcomers) and not unchecked`，自測 fail-closed
    #   那條隨即抓到——has_tbl=False 時仍可能回 True。斷言抓到作者的 bug，這才是它的用處。）
    b_sign_ok = bool(has_tbl) and bool(newcomers) and not unchecked
    done = (n_active > 2) and b_sign_ok
    if not has_tbl:
        note = "符號落帳表 feature_sign_check **未建**⇒無新成員可被證明通過(fail-closed)"
    elif not newcomers:
        note = f"無新成員(基線 {baseline_ts} 之後 registered 者為 0)"
    else:
        det = "、".join(f"{f}={sign_rows.get(f, '無紀錄')}" for f in newcomers)
        note = "新成員符號檢查:" + det + (
            "" if not unchecked else f"；**未通過/未檢:{'、'.join(unchecked)}**")
    return done, note


def live_sunset_gate(cur):
    """自 DB 取現行(非 superseded)之 SUNSET 閘 → (deadline, gate_id, status, evaluated_at)。

    無現行閘＝治權狀態異常,**不猜、不回退到常數**:拋例外讓報表大聲失敗,
    而非靜默印一個沒有依據的日期。
    """
    cur.execute("""SELECT gate_id, criteria->>'deadline', status, evaluated_at
                     FROM evolution_prereg_gate
                    WHERE axis='program' AND status <> 'superseded'
                    ORDER BY preregistered_at DESC LIMIT 1""")
    r = cur.fetchone()
    if not r or not r[1]:
        raise SystemExit(
            "✗ evolution_prereg_gate 查無現行(非 superseded)之 program 軸閘,或其 criteria 無 deadline。"
            "\n  本報表拒絕以寫死日期充數——請先確認治權狀態(SELECT gate_id,status,criteria->>'deadline'"
            " FROM evolution_prereg_gate;)。")
    return date.fromisoformat(r[1]), r[0], r[2], r[3]


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
    # 分母一律讀**門內凍結值**、不寫死(2026-07-31 W0-3):原寫死 "/60" 係 2026-07-17 之舊口徑,
    # 而 live 之 arena 門實查 min_clusters=250(own_daily/chronos/timesfm 等)與 36(own_stack 三門),
    # **無任何門為 60** ⇒ 週儀表會逐週印出與判準不符之分母(本檔首跑為 2026-08-02,尚無存量誤印)。
    need = _one(cur, """SELECT min((criteria->>'min_clusters')::int) FROM direction_gate
                        WHERE status='approved' AND criteria ? 'min_clusters'""")
    need_s = str(need) if need is not None else "未定(無 approved 門帶 min_clusters)"
    a_ev = (f"arena 已結算 {settled} 列;方向門 evaluated_pass={gate_ok}"
            f"(cluster {clusters}/{need_s};分母＝現行 approved 門之最低凍結門檻)")

    # (b) 逐字為**兩個要件之合取**:「active 由 2 成長，**且每一新成員通過符號一致性檢查**」。
    # 原碼 `b_done = n_active > 2` **只實作了第一個**,符號要件僅存在於顯示字串 b_ev
    # ⇒ 一旦 active 成長,週報即印「(b) 達成」而符號尺可能一次都沒跑過(2026-07-31 補;
    # 該尺 scripts/verify_sign_consistency.py 存在但未接線:GATE_IDS 無 G-SIGN、
    # promotion_queue 之 G-SIGN 命中 0 列、且無任何落帳表)。
    #
    # **「新成員」之基線定義**（顯式常數,便於 Steward 依 §8.1 改讀法;不藏在邏輯裡）:
    #   取 SUNSET 凍結時點 evolution_prereg_gate.preregistered_at('2026-07-27 15:30:36')。
    #   於此之後 registered 者為「新成員」。改為「所有現役皆須檢」只需把下行改成極早日期。
    B_BASELINE_TS = "2026-07-27 15:30:36+08"
    n_active = _one(cur, "SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'") or 0
    cur.execute("SELECT feature FROM evolution_production_feature_set "
                "WHERE set_status='active' AND registered_at > %s ORDER BY feature", (B_BASELINE_TS,))
    newcomers = [r[0] for r in cur.fetchall()]
    has_tbl = _one(cur, "SELECT to_regclass('public.feature_sign_check') IS NOT NULL")
    sign_rows: dict[str, str] = {}
    if has_tbl and newcomers:
        cur.execute("""SELECT DISTINCT ON (feature) feature, verdict FROM feature_sign_check
                        WHERE feature = ANY(%s) ORDER BY feature, checked_at DESC""", (newcomers,))
        sign_rows = dict(cur.fetchall())
    b_done, sign_note = judge_b(n_active, newcomers, sign_rows, has_tbl, B_BASELINE_TS)
    b_ev = f"prodset active={n_active}(基線 2;須成長 ∧ 新成員過符號一致性)｜{sign_note}"

    # (c) **SUNSET-C-align**(hugo 2026-07-28 拍板;audits/V2-RUBRIC-GO-20260728.md)——
    # 實作逐字對齊凍結原文(criteria_sha 65eda893…):「LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與
    # mismatched,且該結論可被獨立重跑複現。」
    #   · 「任一臂」取**受測臂**(非對照臂;字面連 shuffled 都滿足=荒謬,解釋登錄於 audit)。
    #   · 「同時勝過」=同尺(set_id+eval_code_hash)之 axis_f **嚴格** > floor 與 > mismatched。
    #   · 「可被獨立重跑複現」=同尺同臂 ≥2 個獨立 run **皆**成立(run_id 自 2026-07-28 起帶
    #     attempt 序,重跑可記錄;先前結構上不可能,故此前之「達成」宣稱皆無效)。
    # 歷史:07-27 前的實作寫 best>shuffled(不比 floor/mismatched、無複現對應)且自行印「已達成」,
    # 經對抗驗證停用(V2-SUNSET-C-DISPUTED-20260727.md)。量尺空洞問題(robot 五格 1.000)另屬
    # S-4/S-8 待裁——本判定忠實執行凍結文字,空洞與否之語意權在 hugo,證據句誠實附註。
    CTRL = ('ceiling', 'floor', 'shuffled', 'mismatched', 'robot')
    cur.execute("""SELECT set_id, eval_code_hash FROM local_model_eval_run
        WHERE arm <> ALL(%s) AND NOT is_invalid ORDER BY created_at DESC LIMIT 1""", (list(CTRL),))
    r = cur.fetchone()
    c_done, c_ev = False, "無任何有效受測臂 run(對照臂不算「臂」)"
    if r:
        sid, ch = r
        floor_f = _one(cur, """SELECT axis_f FROM local_model_eval_run WHERE set_id=%s
            AND eval_code_hash=%s AND arm='floor' ORDER BY created_at DESC LIMIT 1""", (sid, ch))
        mism_f = _one(cur, """SELECT axis_f FROM local_model_eval_run WHERE set_id=%s
            AND eval_code_hash=%s AND arm='mismatched' ORDER BY created_at DESC LIMIT 1""", (sid, ch))
        if floor_f is None or mism_f is None:
            c_ev = f"同尺({sid[:8]}/{ch[:8]})缺 floor/mismatched 對照臂=不可判(缺對照非通過)"
        else:
            cur.execute("""SELECT arm, count(*) AS n_runs,
                    count(*) FILTER (WHERE axis_f > %s AND axis_f > %s) AS n_win
                FROM local_model_eval_run WHERE set_id=%s AND eval_code_hash=%s
                  AND arm <> ALL(%s) AND NOT is_invalid GROUP BY arm""",
                (floor_f, mism_f, sid, ch, list(CTRL)))
            arms = cur.fetchall()
            first = [a for a, n, w in arms if w >= 1]
            repro = [a for a, n, w in arms if w >= 2 and w == n]
            c_done = bool(repro)
            robot_f = _one(cur, """SELECT axis_f FROM local_model_eval_run WHERE set_id=%s
                AND eval_code_hash=%s AND arm='robot' ORDER BY created_at DESC LIMIT 1""", (sid, ch))
            c_ev = (f"同尺 {sid[:8]}/{ch[:8]}:floor F={floor_f} mism F={mism_f};"
                    f"首半(嚴格同勝)之臂={first or '無'};複現(≥2 run 皆勝)之臂={repro or '**無**'}"
                    + (f";⚠量尺附註:robot(零知識格式機)同尺 F={robot_f}"
                       "——(c) 凍結文字不含 robot,語意權=S-8 待裁" if robot_f is not None else ""))
    c_done = bool(c_done)
    return [("(a) arena 結算＋方向門可讀數", a_done, a_ev),
            ("(b) prodset active 由 2 成長＋符號一致", b_done, b_ev),
            ("(c) LAIEVO 任一臂 F@L1 勝 floor 與 mismatched 且可複現", c_done, c_ev)]


def build(days, md):
    L = []
    h1 = (lambda s: L.append(f"\n## {s}")) if md else (lambda s: L.append(f"\n── {s} ──"))
    with db.connect() as conn, db.transaction(conn) as cur:
        gate = live_sunset_gate(cur)
        deadline, gate_id, g_status, g_evaluated = gate
        left = (deadline - date.today()).days
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
        if g_status in ("evaluated_pass", "evaluated_fail"):
            # 已結算 ⇒ 不再倒數;印終局裁決,並保留三條件現況供掃視(結算後條件仍會變動)。
            L.append(f"# {gate_id}:**已結算 {g_status}**(evaluated_at={g_evaluated});"
                     f"期限 {deadline};現況確定達成 {n_ok}/3、未判定 {n_und}"
                     f"（現況僅供掃視,裁決以 result_snapshot 為準）")
        else:
            L.append(f"# {gate_id}:剩 {left} 天(至 {deadline});"
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

        h1(f"本週自動審批(SRC-AUTO;近 {days} 日;P5.W5 掃視認領)")
        cur.execute("""SELECT created_at, source_key, reason FROM knowledge_source_review_log
                       WHERE actor='auto_rules_v1' AND action='approve'
                         AND created_at > now() - make_interval(days => %s)
                       ORDER BY review_id DESC""", (days,))
        arows = cur.fetchall()
        L.append(f"  自動批 {len(arows)} 源" + ("" if arows else "(無)"))
        for ts, k, _ in arows[:20]:
            L.append(f"  · {ts:%m-%d %H:%M} {k}(留痕=逐謂詞 JSON,查 review_log)")
        if len(arows) > 20:
            L.append(f"  …另 {len(arows)-20} 筆")
        n_susp = _one(cur, """SELECT count(*) FROM knowledge_source s
            WHERE s.approval_status='suspended' AND EXISTS (
              SELECT 1 FROM knowledge_source_review_log l
              WHERE l.source_key=s.source_key AND l.actor='auto_rules_v1'
                AND l.action='approve')""") or 0
        if n_susp:
            L.append(f"  ⛔ 熔斷中:{n_susp} 個自動批源被 suspend——自動批全域暫停待人查(SRC-AUTO §二)")

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
    # 舊斷言為 `SUNSET_DEADLINE == date(2026,10,31)`——把**程式自己存的副本**鎖住,
    # 於是 07-31 GATE-raise 之後它仍是綠的、而報表印過期日期。
    # **不用字面斷言**:`"xxx" in src` 會掃到斷言自己那份字串副本而恆綠
    # （2026-07-31 一日內實犯三次;install_cron.sh 用字元類切開,此處改驗真行為）。
    chk("期限取自 DB 之現行閘(函式存在且可呼叫,非寫死常數)",
        callable(globals().get("live_sunset_gate")))
    # (b) 之判定改為純函式 judge_b,以下餵真輸入驗真行為——退回舊邏輯即會紅。
    chk("(b) 未成長(active=2)⇒未達成", judge_b(2, [], {}, True)[0] is False)
    chk("(b) 已成長但新成員無符號紀錄⇒**未達成**(fail-closed)",
        judge_b(3, ["f_new"], {}, True)[0] is False)
    chk("(b) 已成長但符號 FAIL⇒未達成",
        judge_b(3, ["f_new"], {"f_new": "FAIL"}, True)[0] is False)
    chk("(b) 已成長且新成員全 PASS⇒達成(綠燈也要驗得到)",
        judge_b(3, ["f_new"], {"f_new": "PASS"}, True)[0] is True)
    chk("(b) 落帳表未建⇒未達成且說明理由",
        judge_b(3, ["f_new"], {"f_new": "PASS"}, False)[0] is False
        and "未建" in judge_b(3, ["f_new"], {}, False)[1])
    chk("(b) 多個新成員只要一個未過即整體未達成",
        judge_b(4, ["a", "b"], {"a": "PASS"}, True)[0] is False)
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
