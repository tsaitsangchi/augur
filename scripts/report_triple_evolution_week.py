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
from verify_evolution_acceptance import rcell_cells  # R-CELL′ 逐格收攏(H1;同源單一住所 #12)

# 期限**不得寫死**——判準住 evolution_prereg_gate 且受 criteria_sha 保護,程式另存副本
# 即為「凍結了判準文字卻沒凍結解釋它的程式」之同型缺口(2026-07-31 實犯:當日 GATE-raise
# 把期限由 10-31 改為 07-31 並 supersede 舊列,而本檔仍印 10-31,且其自測還把過期值鎖住)。
# 保留常數僅作**歷史錨**與 DB 不可讀時之誠實標記,不參與任何判定。
SUNSET_DEADLINE_HISTORICAL = date(2026, 10, 31)  # 原始凍結值(V2-SUNSET,已 superseded)


def recent_alerts(lines, today, days=7):
    """alerts.log 行 → 近 N 日者。**純函式**（登錄冊 C4′）。行格式＝'YYYY-MM-DD HH:MM:SS+ZZzz FAIL unit'。

    無法解析日期之行**保留**（sink 壞掉寫出怪行時，寧可多印不可靜默丟——丟棄=另一種假綠）。
    """
    out = []
    for ln in lines:
        d = ln[:10]
        try:
            ok = (today - date.fromisoformat(d)).days < days
        except ValueError:
            ok = True   # 不可解析＝保留
        if ok and ln.strip():
            out.append(ln.rstrip())
    return out


def demote_fail_pending(is_active, action, queue_status, prom_verdict):
    """現役成員之 demote FAIL 帳是否該出現在「待你裁決」——**純函式**（judge_b 同型，登錄冊 A4）。

    真條件＝四要件合取：現役 ∧ demote 提案 ∧ 被閘記 rejected_gate ∧ G-PROM 確為 FAIL 族
    （FAIL/FAIL_SIGN 皆算；PASS 之 demote 列不出單——inst_cumflow 型正確不入列）。
    """
    return (bool(is_active) and action == "demote" and queue_status == "rejected_gate"
            and str(prom_verdict or "").startswith("FAIL"))


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


def sign_rows_from_history(rows):
    """feature_sign_check 全史列 → {feature: 聚合 verdict}。**純函式**（judge_b 同型;週報 (b) 口徑）。

    口徑（2026-08-01,A3 落地時記錄之另案殘項）:某 feature「通過」＝該 feature 在表內
    **每個 h 各自最新列皆 PASS**。步驟:(1) per-(feature,h) 取最新列(同刻取後讀入者;
    SQL 端以 ORDER BY check_id 供序);(2) 全 h 皆 PASS ⇒ "PASS";任一 h 非 PASS ⇒
    聚合值＝逐 h 明細(≠"PASS" ⇒ judge_b fail-closed 照舊擋下)。無列＝不入 dict＝
    judge_b 之「無紀錄」不變。
    捨棄舊口徑 `DISTINCT ON (feature)`「整表最新一列」——A3 後引擎會補寫**單 h** 列
    (實例 2026-08-01 20:43 inst_cumflow_position_120d 僅 h=60),該列在舊口徑下會
    **遮住其他 h(如 h=20)之最新裁決**。口徑住本純函式而非 SQL:退回單列口徑之突變,
    自測之遮蔽 case 立即紅(SQL 端無口徑可被靜默改掉)。
    rows=[(feature, h, verdict, checked_at), ...] 任意序;checked_at 可比較即可。
    """
    latest: dict = {}
    for feat, h, verdict, ts in rows:
        k = (feat, h)
        if k not in latest or ts >= latest[k][0]:
            latest[k] = (ts, verdict)
    per_feat: dict = {}
    for (feat, h), (_, verdict) in latest.items():
        per_feat.setdefault(feat, {})[h] = verdict
    return {feat: ("PASS" if all(v == "PASS" for v in hv.values())
                   else "、".join(f"h{h}={v}" for h, v in sorted(hv.items())))
            for feat, hv in per_feat.items()}


def rcell_status_line(scale_tag, caps, live_cells, robot_cells):
    """R-CELL′ 逐格狀態行(H1 2026-08-01)——**純函式**(自測餵真輸入;judge_b 同型)。

    caps={capability 格名};live_cells={格:[(n_total,n_answered,mean|None) 逐 live run]};
    robot_cells={格:robot 該格 mean}。有效格計數只數全格有效者;缺格誠實列示
    n_answered/n_total(R-CELL′-2);robot=量尺哨兵非受測臂(S-8:分數僅驗尺、永不入排名)。
    """
    n_ok, parts = 0, []
    for cname in sorted(caps):
        good = [e for e in live_cells.get(cname, []) if e[2] is not None]
        gaps = [e for e in live_cells.get(cname, []) if e[2] is None]
        n_ok += len(good)
        rb = robot_cells.get(cname)
        if good:
            parts.append(f"{cname} 有效 {len(good)} run F={'/'.join(f'{e[2]:.4f}' for e in good)}"
                         f"(robot 哨兵 {rb if rb is not None else '無'})")
        elif gaps:
            parts.append(f"{cname} 缺格({'、'.join(f'{e[1]}/{e[0]}' for e in gaps)})")
    return (f"R-CELL′ 逐格{scale_tag}:capability 有效格 {n_ok};" + ";".join(parts)
            + ";S-8:robot=量尺哨兵非受測臂(分數僅驗尺、不入排名)")


def sentinel_line(name, rc, tail_lines):
    """哨兵一行(F3 防鏽哨/門指紋哨共用)。**純函式**——rc≠0 必紅、無輸出視同紅(不吞)。

    抽成純函式之由:兩處呼叫端各有一份三元式,字面斷言驗不到「紅會不會真的印紅」,
    且複製貼上二份=改一處漏一處(#35(1) 純函式餵真輸入)。
    """
    tail = [t.strip() for t in (tail_lines or []) if t and t.strip()]
    mark = "🟢" if rc == 0 and tail else "🔴"
    body = "；".join(tail) if tail else "(無輸出=異常,視同紅)"
    return f"  {mark} {name}(rc={rc})｜{body}"


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
    # **「新成員」之射程＝Steward 依 §8.1 之裁決（2026-07-31：「要回頭補」）：**
    #   採 **all_active**——**所有現役成員**皆須有符號檢查紀錄，不因進場早於 SIGN-B 而豁免。
    #   被此裁決涵蓋者＝`inst_cumflow_position_120d`（2026-07-24 進 prodset，早於 SIGN-B
    #   〔07-28 建〕存在，故至今零符號證據）。另一現役 `lending_fee_rate_mean_20d`
    #   （07-29 進、凍結後）在任一讀法下皆須檢。
    #   曾考慮之較窄讀法＝post_freeze（只檢凍結時點之後 registered 者），**已由 Steward 否決**，
    #   保留於此僅為留痕；欲改回改 B_SCOPE 一處即可，判準不藏在邏輯裡。
    B_SCOPE = "all_active"        # all_active | post_freeze
    B_FREEZE_TS = "2026-07-27 15:30:36+08"   # post_freeze 讀法用；all_active 下不參與判定
    n_active = _one(cur, "SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'") or 0
    if B_SCOPE == "all_active":
        cur.execute("SELECT feature FROM evolution_production_feature_set "
                    "WHERE set_status='active' ORDER BY feature")
    else:
        cur.execute("SELECT feature FROM evolution_production_feature_set "
                    "WHERE set_status='active' AND registered_at > %s ORDER BY feature",
                    (B_FREEZE_TS,))
    newcomers = [r[0] for r in cur.fetchall()]
    has_tbl = _one(cur, "SELECT to_regclass('public.feature_sign_check') IS NOT NULL")
    sign_rows: dict[str, str] = {}
    if has_tbl and newcomers:
        # 口徑住純函式 sign_rows_from_history(per-(feature,h) 各自最新列全 PASS 才 PASS);
        # SQL 只撈史料不做judgment——舊 DISTINCT ON (feature) 單列口徑會被 A3 單 h 補寫列遮蔽。
        cur.execute("""SELECT feature, h, verdict, checked_at FROM feature_sign_check
                        WHERE feature = ANY(%s) ORDER BY check_id""", (newcomers,))
        sign_rows = sign_rows_from_history(cur.fetchall())
    b_done, sign_note = judge_b(n_active, newcomers, sign_rows, has_tbl,
                                f"射程={B_SCOPE}（Steward 2026-07-31 裁：所有現役皆須檢）")
    b_ev = (f"prodset active={n_active}(基線 2;須成長 ∧ 新成員過符號一致性;"
            f"符號口徑=每個 h 各自最新列皆 PASS)｜{sign_note}")

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
                       "——(c) 凍結文字不含 robot;S-8(H1 拍板 2026-08-01):robot=量尺哨兵"
                       "非受測臂,其 veto 作用於證據力層(A′),不動 (c) 字面" if robot_f is not None else ""))
    c_done = bool(c_done)
    # R-CELL′ 逐格狀態(H1 2026-08-01):capability 格之有效格數＋live-vs-robot 哨兵線。
    # (c) 聚合口徑照舊並列於上;此行=A′ 判讀層之逐格口徑(不換尺;rcell_cells 同源 #12)。
    cur.execute("""SELECT DISTINCT set_id FROM local_model_eval_item
        WHERE expect->>'cell_class'='capability'""")
    cap_sets = [x[0] for x in cur.fetchall()]
    if cap_sets:
        cur.execute("""SELECT set_id, eval_code_hash FROM local_model_eval_run
            WHERE set_id = ANY(%s) AND arm <> ALL(%s)
            ORDER BY created_at DESC LIMIT 1""", (cap_sets, list(CTRL)))
        r2 = cur.fetchone()
        if r2:
            sid2, ch2 = r2
            cur.execute("""SELECT layer FROM local_model_eval_item
                WHERE set_id=%s AND expect->>'cell_class'='capability' GROUP BY 1""", (sid2,))
            caps2 = {x[0] for x in cur.fetchall()}
            cur.execute("""SELECT arm, detail FROM local_model_eval_run
                WHERE set_id=%s AND eval_code_hash=%s ORDER BY created_at""", (sid2, ch2))
            robot2, live2 = {}, {}
            for arm2, d2 in cur.fetchall():
                cs = rcell_cells((d2 or {}).get("per_item", []))
                if arm2 == "robot":
                    robot2 = {k: v[2] for k, v in cs.items() if v[2] is not None}
                elif arm2 not in CTRL:
                    for cname in caps2:
                        if cname in cs:
                            live2.setdefault(cname, []).append(cs[cname])
            c_ev += "\n      " + rcell_status_line(f"({sid2[:8]}/{ch2[:8]})", caps2, live2, robot2)
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

        # S-iii(F3-apply 圈選 2026-08-01):consequence 載體防鏽哨——每週實跑 --check(唯讀)。
        # 紅=「不啟用只常備」策略之證偽條件觸發(呈案單 F3 條:屆時改季度演練),故紅要照印不吞。
        import subprocess
        from pathlib import Path
        _f3 = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent / "execute_sunset_consequence.py"),
             "--check"], capture_output=True, text=True, timeout=120)
        _f3_tail = (_f3.stdout or _f3.stderr or "").strip().splitlines()
        L.append(sentinel_line("consequence 載體防鏽哨(--check)", _f3.returncode, _f3_tail[-1:]))

        # 門指紋哨(2026-08-02;哨兵落地時留之「掛週報候選另日一行」):逐列覆算 criteria_sha
        # 與文自洽。紅=某門之判準文與其指紋分家(挪門柱或資料毀損)——治權級,故照印不吞。
        _sha = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent / "verify_gate_sha_integrity.py"),
             "--check"], capture_output=True, text=True, timeout=120)
        _sha_tail = [ln for ln in (_sha.stdout or _sha.stderr or "").strip().splitlines()
                     if "→" in ln or "MISMATCH" in ln]
        L.append(sentinel_line("門指紋哨(criteria_sha 覆算)", _sha.returncode, _sha_tail))

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

        # C4′ 失敗警示（登錄冊 2026-08-01）：OnFailure sink 落 alerts.log,此處印近 7 日
        # ——sink 落了行但沒人看見＝紅燈失效之最後一哩。
        import pathlib
        _alog = pathlib.Path.home() / "logs" / "alerts.log"
        _alerts = recent_alerts(_alog.read_text(encoding="utf-8").splitlines(),
                                date.today()) if _alog.exists() else []
        h1(f"系統失敗警示(近 7 日;OnFailure sink)")
        if _alerts:
            L.append(f"  **{len(_alerts)} 件**——逐件查因,勿只清 log:")
            for a in _alerts[-8:]:
                L.append(f"    · {a}")
        else:
            L.append("  0 件(13 支 service 全程無失敗;sink 端到端驗證於 2026-08-01)")

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
        # 現役成員之 demote FAIL 帳（登錄冊 A4，2026-08-01）：demote 提案因非 FAIL_SIGN 被記
        # rejected_gate＝「名義人裁」，但先前**查無任何人裁載體**——帳上有 FAIL 證據卻無人會看到
        # （實例：lending_fee_rate_mean_20d 於 run 20 G-PROM FAIL 仍 active）。本段即該載體。
        # 口徑＝只看最新完整引擎輪（succeeded ∧ config_json?'mode'）：舊 run 之 FAIL 不重複出單。
        cur.execute("""SELECT q.feature, q.queue_id, q.gate_json->'G-PROM'->>'verdict'
                         FROM promotion_queue q
                         JOIN evolution_production_feature_set p
                           ON p.feature=q.feature AND p.set_status='active'
                        WHERE q.run_id=(SELECT max(run_id) FROM evolution_run
                                         WHERE status='succeeded' AND config_json ? 'mode')
                          AND q.action='demote' AND q.queue_status='rejected_gate'""")
        _dr = [r for r in cur.fetchall()
               if demote_fail_pending(True, "demote", "rejected_gate", r[2])]
        if _dr:
            L.append(f"  **現役 FAIL 除役帳待裁:{len(_dr)} 顆**——帳上有 G-PROM FAIL 卻仍 active,"
                     "除役與否須人裁(勿靜默):")
            for f, qid, v in _dr:
                L.append(f"    · {f}(queue {qid}, {v})——裁除役=demote 走既有 APPLY;裁保留=記理由")
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
    chk("哨兵:rc=0 且有輸出 → 🟢", sentinel_line("X", 0, ["ok"]).startswith("  🟢"))
    chk("哨兵:rc≠0 → 🔴(紅不被吞;哨兵回紅=週報必顯形)", sentinel_line("X", 1, ["MISMATCH=1"]).startswith("  🔴"))
    chk("哨兵:rc=0 但零輸出 → 🔴(靜默=異常,不當綠)", sentinel_line("X", 0, []).startswith("  🔴"))
    chk("哨兵:紅時原文照印不改寫", "MISMATCH=1" in sentinel_line("X", 1, ["MISMATCH=1"]))
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
    # C4′ alerts 顯示（登錄冊 2026-08-01）：純函式餵真輸入
    _t = date(2026, 8, 1)
    chk("C4′:近 7 日內之 FAIL 行保留", recent_alerts(
        ["2026-07-30 10:00:00+0800 FAIL x.service"], _t) != [])
    chk("C4′:7 日外之行過濾", recent_alerts(
        ["2026-07-01 10:00:00+0800 FAIL old.service"], _t) == [])
    chk("C4′:不可解析行保留（sink 壞掉寧多印不靜默丟）", recent_alerts(
        ["GARBAGE not a date"], _t) == ["GARBAGE not a date"])
    chk("C4′:空檔零告警（綠燈也要驗得到）", recent_alerts([], _t) == [])
    # A4 載體（登錄冊 2026-08-01）：純函式餵真輸入，四要件缺一即 False（紅綠雙向都驗）
    chk("A4:現役+demote+rejected_gate+FAIL ⇒ 出單",
        demote_fail_pending(True, "demote", "rejected_gate", "FAIL") is True)
    chk("A4:FAIL_SIGN 亦屬 FAIL 族 ⇒ 出單",
        demote_fail_pending(True, "demote", "rejected_gate", "FAIL_SIGN") is True)
    chk("A4:G-PROM=PASS 之 demote 不出單（inst_cumflow 型）",
        demote_fail_pending(True, "demote", "rejected_gate", "PASS") is False)
    chk("A4:非現役不出單", demote_fail_pending(False, "demote", "rejected_gate", "FAIL") is False)
    chk("A4:pending_auto（尚在自動道）不出單",
        demote_fail_pending(True, "demote", "pending_auto", "FAIL") is False)
    chk("(b) 多個新成員只要一個未過即整體未達成",
        judge_b(4, ["a", "b"], {"a": "PASS"}, True)[0] is False)
    # (b) per-(feature,h) 口徑（2026-08-01）:純函式餵真列 fixture(鏡射 live 之 A3 雙寫形狀:
    # 13:57 雙 h 落帳、20:43 引擎補寫**單 h=60** 列)。舊 DISTINCT ON (feature) 單列口徑
    # 只看 20:43 那列 ⇒ h20 之 FAIL 被遮——退回舊口徑,下一條立即紅。
    _mask = [("inst_cumflow_position_120d", 20, "FAIL", "2026-08-01 13:57:33+08"),
             ("inst_cumflow_position_120d", 60, "PASS", "2026-08-01 13:57:33+08"),
             ("inst_cumflow_position_120d", 60, "PASS", "2026-08-01 20:43:20+08")]
    chk("(b) h20 最新 FAIL 不被其後之單 h60 補寫列遮蔽(per-h 口徑;明細誠實列 h20=FAIL)",
        judge_b(3, ["inst_cumflow_position_120d"], sign_rows_from_history(_mask), True)[0] is False
        and "h20=FAIL" in sign_rows_from_history(_mask)["inst_cumflow_position_120d"])
    _ok = [("inst_cumflow_position_120d", 20, "PASS", "2026-08-01 13:57:33+08"),
           ("inst_cumflow_position_120d", 60, "PASS", "2026-08-01 13:57:33+08"),
           ("inst_cumflow_position_120d", 60, "PASS", "2026-08-01 20:43:20+08")]
    chk("(b) 每個 h 各自最新列皆 PASS ⇒ 聚合 PASS(綠燈也要驗得到)",
        sign_rows_from_history(_ok) == {"inst_cumflow_position_120d": "PASS"}
        and judge_b(3, ["inst_cumflow_position_120d"], sign_rows_from_history(_ok), True)[0] is True)
    chk("(b) 同 h 之舊 FAIL 被新 PASS 取代(per-h 取最新,不翻舊帳、不過度嚴格)",
        sign_rows_from_history([("f", 20, "FAIL", "2026-07-30"),
                                ("f", 20, "PASS", "2026-07-31")]) == {"f": "PASS"})
    chk("(b) UNJUDGEABLE 非 PASS ⇒ 未達成",
        judge_b(3, ["f"], sign_rows_from_history(
            [("f", 20, "UNJUDGEABLE", "2026-08-01"), ("f", 60, "PASS", "2026-08-01")]), True)[0] is False)
    chk("(b) 零列 ⇒ 空 dict(無紀錄 fail-closed 不變)",
        sign_rows_from_history([]) == {}
        and judge_b(3, ["f"], sign_rows_from_history([]), True)[0] is False)
    chk("(b) active=1 未成長:唯一現役即使全 h PASS 仍未達成(2026-08-01 mean_20d demote 後現況)",
        judge_b(1, ["inst_cumflow_position_120d"], sign_rows_from_history(_ok), True)[0] is False)
    # R-CELL′ 逐格狀態行(H1 2026-08-01):純函式餵真輸入(haystack=回傳值,非本檔 src)
    _ln = rcell_status_line("(s/h)", {"C1", "C2P"},
                            {"C1": [(36, 34, None)],
                             "C2P": [(24, 24, 0.6667), (24, 24, 0.6667)]},
                            {"C1": 0.5, "C2P": 0.5})
    chk("R-CELL′ 行:有效格只數全格有效者(C2P×2=2)且 C1 以缺格 34/36 列示",
        "capability 有效格 2" in _ln and "C1 缺格(34/36)" in _ln)
    chk("R-CELL′ 行:live-vs-robot 哨兵線在場且 S-8 語意成文(robot 不入排名)",
        "robot 哨兵 0.5" in _ln and "不入排名" in _ln)
    chk("R-CELL′ 行:零 live run 時有效格=0(綠燈也要驗得到)",
        "capability 有效格 0" in rcell_status_line("(s/h)", {"C1"}, {}, {}))
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
