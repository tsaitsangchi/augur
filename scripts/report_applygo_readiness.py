#!/usr/bin/env python
"""APPLY-go 決策包 — 逐顆晉升裁決前之唯讀彙整（hugo 人閘 TWEVO-APPLY-go 之呈案工具）。

🎯 這支在做什麼（白話）：run 結輪後 hugo 要逐顆裁「誰可 APPLY 進 prodset」。本工具一鍵把
   三條件現況彙整成決策包印出（**唯讀**、零寫入、零 APPLY、零代簽）：
     ① G-SIGN 已入 GATE_IDS——機械查 `augur.philosophy.evolution` 常數 via import
        （引擎跑動中唯讀 import 安全，不碰引擎檔）
     ② 各候選之 G-SIGN verdict——**雙源**：promotion_queue 該 run 最新世代列之 gate_json
        ＋ feature_sign_check 落帳表最新列；**皆 PASS 才算過**——SKIP／UNJUDGEABLE／查無列
        ＝未通過（fail-closed；落帳表表註明文：查無列不得讀為通過）
     ③ 該候選八閘全 PASS——`all_gates_green`（判準單一住所 #12，不另立口徑）
   每候選一段：八閘逐格／sign 證據（point_ic・boot 同號數・direction）／G-ECON 數字／建議行
   （三條件齊⇒「可裁」；缺⇒列缺什麼）；尾節＝hugo 開閘指令模板（--allow-apply
   --gate-ref TWEVO-APPLY-go）。輸出通篇為 [DRAFT 呈案]——本工具不裁決、不開閘、
   Steward 決定欄留白（#6／#14；決策層人拍板）。

守 #9/#10（每個數字出自 DB query 或常數 import，可溯源）· #15（SKIP≠PASS；查無列＝未通過；
   self-reported 標記 #32(a)）· #18/#29（矩陣＋selftest）· #28（本地零 usage）。

執行指令矩陣:
  python scripts/report_applygo_readiness.py               # 無參數＝安全預設:最新 run 之決策包(唯讀)
  python scripts/report_applygo_readiness.py --run-id 21   # 指定 run
  python scripts/report_applygo_readiness.py --selftest    # 純紅綠自測(免 DB 免 API;fixture=真 gate_json 形)
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from typing import Any, Mapping

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import GATE_IDS, all_gates_green, gate_verdict

HUMAN_GATE_REF = "TWEVO-APPLY-go"


# ──────────────────────────── 純函式（selftest 之標的） ────────────────────────────

def compute_cond1(gate_ids) -> bool:
    """條件①：G-SIGN 在閘集常數內（呼叫端餵 evolution.GATE_IDS；selftest 餵新舊兩代 tuple）。"""
    return "G-SIGN" in tuple(gate_ids)


def gsign_verdicts(
    gate_json: Mapping[str, Any],
    fsc_verdict: str | None,
) -> tuple[str | None, str | None, bool]:
    """條件②素材：(gate_json 裁決, 落帳表裁決, cond2)。

    雙源皆 'PASS' 才 True（fail-closed）：gate_json 無 G-SIGN 鍵（舊七鍵世代）→ None；
    落帳表查無列（fsc_verdict=None）＝未通過；SKIP／UNJUDGEABLE／FAIL 皆非 PASS。
    """
    g = gate_json.get("G-SIGN")
    gv = gate_verdict(g) if isinstance(g, Mapping) else None
    fv = str(fsc_verdict).upper() if fsc_verdict else None
    return gv, fv, (gv == "PASS" and fv == "PASS")


def boot_same_sign(boot_ics, direction) -> tuple[int, int]:
    """sign 證據摘要：bootstrap 均值與 direction 同號之席數／總席數。

    0 均值不計同號（無方向證據≠方向正確，同 judge_sign 口徑）；direction 非 ±1 → 同號數 0。
    """
    boots = [b for b in (boot_ics or []) if b is not None]
    if direction not in (1, -1):
        return 0, len(boots)
    return sum(1 for b in boots if float(b) * direction > 0), len(boots)


def readiness(cond1: bool, cond2: bool, cond3: bool) -> tuple[bool, list[str]]:
    """三條件 → (可裁?, 缺項清單)。任一缺即列名（fail-closed；缺項文字供決策包直接印出）。"""
    missing: list[str] = []
    if not cond1:
        missing.append("①G-SIGN 未入 GATE_IDS")
    if not cond2:
        missing.append("②G-SIGN 非雙源 PASS（gate_json＋feature_sign_check；SKIP/UNJUDGEABLE/查無列≠PASS）")
    if not cond3:
        missing.append("③八閘未全 PASS")
    return (not missing), missing


def recommend_line(ready: bool, missing: list[str], action: str, queue_status: str) -> str:
    """建議行（呈案用語：可裁＝三條件齊，裁決本身仍唯 hugo）。"""
    if ready:
        line = "可裁 —— 三條件齊（裁決＝hugo，工具不代裁）"
        if action != "promote":
            line += f"；⚠ action={action}≠promote，非晉升裁決對象（demote FAIL_SIGN 走 R3 自動通道）"
        if queue_status != "pending_auto":
            line += f"；⚠ queue_status={queue_status}≠pending_auto，I5 不會消費此列"
        return line
    return "缺：" + "；".join(missing)


def gate_cells(gate_json: Mapping[str, Any]) -> list[str]:
    """八閘逐格：依 GATE_IDS 順序；缺鍵（舊世代列）誠實印「無鍵」而非補 FAIL 假數。"""
    cells = []
    for gid in GATE_IDS:
        g = gate_json.get(gid)
        cells.append(f"{gid}={gate_verdict(g) if isinstance(g, Mapping) else '無鍵(舊世代)'}")
    return cells


def sign_evidence(gate_json: Mapping[str, Any], fsc: Mapping[str, Any] | None) -> dict[str, Any]:
    """sign 證據（IC 均值點估計／boot 同號數／direction）：gate_json.G-SIGN.evidence 為主，
    缺者退 feature_sign_check 列；兩邊皆無＝誠實回空（不補值）。"""
    g = gate_json.get("G-SIGN") if isinstance(gate_json.get("G-SIGN"), Mapping) else {}
    ev = g.get("evidence") if isinstance(g.get("evidence"), Mapping) else {}
    f = fsc or {}
    direction = ev.get("direction", g.get("direction", f.get("direction")))
    boots = ev.get("boot_ics", f.get("boot_ics"))
    n_same, n_tot = boot_same_sign(boots, direction)
    return {
        "direction": direction,
        "direction_source": ev.get("direction_source", g.get("direction_source", f.get("direction_source"))),
        "point_ic": ev.get("point_ic", g.get("point_ic", f.get("point_ic"))),
        "n_series": ev.get("n_series", g.get("n_series", f.get("n_panels"))),
        "boot_same": n_same,
        "boot_total": n_tot,
    }


def econ_numbers(gate_json: Mapping[str, Any]) -> dict[str, Any] | None:
    """G-ECON 數字（port/bench sharpe・max_dd・n_periods・span・turnover）；無 evidence＝None（誠實缺料）。"""
    g = gate_json.get("G-ECON")
    if not isinstance(g, Mapping):
        return None
    ev = g.get("evidence")
    if not isinstance(ev, Mapping):
        return None
    return {k: ev.get(k) for k in
            ("port_sharpe", "bench_sharpe", "max_dd", "n_periods", "span", "avg_turnover")}


def _fmt(v, spec) -> str:
    return format(v, spec) if isinstance(v, (int, float)) else "—"


def render_candidate(cand: Mapping[str, Any], cond1: bool, idx: int, total: int) -> list[str]:
    """單一候選之段落（純函式：餵 dict 出 lines；selftest 以 fixture 走同一條路）。"""
    gj = cand["gate_json"]
    fsc = cand.get("fsc")
    gv, fv, cond2 = gsign_verdicts(gj, fsc.get("verdict") if fsc else None)
    cond3 = all_gates_green(gj)
    ready, missing = readiness(cond1, cond2, cond3)
    se = sign_evidence(gj, fsc)
    eco = econ_numbers(gj)
    mark = lambda b: "✓" if b else "✗"  # noqa: E731

    lines = [
        f"── 候選 {idx}/{total}: {cand['feature']}",
        f"   queue_id={cand['queue_id']} · action={cand['action']} · queue_status={cand['queue_status']}"
        + (f" · 該 run 同 feature 列數={cand['n_rows']}(取最新)" if cand.get("n_rows", 1) > 1 else ""),
        "   八閘: " + " · ".join(gate_cells(gj)),
        (f"   sign: direction={se['direction'] if se['direction'] is not None else '—'}"
         f"({se['direction_source'] or '—'}) · point_ic={_fmt(se['point_ic'], '+.5f')}"
         f" · boot 同號 {se['boot_same']}/{se['boot_total']} · n_series={se['n_series'] if se['n_series'] is not None else '—'}"),
    ]
    if fsc:
        agree = "一致" if gv == fv else f"⚠ 與 gate_json 不一致（gate={gv} vs 落帳={fv}）→ 以較嚴者計"
        lines.append(f"   落帳表 feature_sign_check: {fv} @{str(fsc.get('checked_at'))[:19]}"
                     f"（h={fsc.get('h', '—')}, n_panels={fsc.get('n_panels', '—')}）— {agree}")
    else:
        lines.append("   落帳表 feature_sign_check: **查無列 ⇒ 未通過（fail-closed，表註明文）**")
    if eco:
        lines.append(f"   G-ECON: port_sharpe={_fmt(eco['port_sharpe'], '+.3f')}"
                     f" vs bench={_fmt(eco['bench_sharpe'], '+.3f')}"
                     f" · max_dd={_fmt(eco['max_dd'], '+.2%')}"
                     f" · n_periods={eco['n_periods'] if eco['n_periods'] is not None else '—'}"
                     f" · span={eco['span'] or '—'}"
                     f" · turnover={_fmt(eco['avg_turnover'], '.1%')}")
    else:
        gv_econ = gate_verdict(gj["G-ECON"]) if isinstance(gj.get("G-ECON"), Mapping) else "無鍵"
        lines.append(f"   G-ECON: verdict={gv_econ}（無 evidence 數字——誠實缺料，不補值）")
    lines.append(f"   條件: ①{mark(cond1)} ②{mark(cond2)}（gate={gv or '無鍵'}, 落帳={fv or '無列'}） ③{mark(cond3)}")
    lines.append(f"   建議行: {recommend_line(ready, missing, cand['action'], cand['queue_status'])}")
    lines.append("")
    return lines


def render_pack(pack: Mapping[str, Any]) -> list[str]:
    """整包（純函式）。pack 鍵：run_id/run_status/started/finished/kill/fsc_table_exists/candidates。"""
    rid = pack["run_id"]
    cond1 = compute_cond1(GATE_IDS)
    cands = pack["candidates"]
    bar = "=" * 72
    out = [
        bar,
        f"APPLY-go 決策包（run {rid}） — [DRAFT 呈案] 未經拍板不得施作",
        bar,
        f"產生時刻: {dt.datetime.now().isoformat(timespec='seconds')}（本機）· 工具=scripts/report_applygo_readiness.py（唯讀）",
        "self-reported 標記(#32a): 本包為 AI 彙整之呈案；量化數字皆出自 live DB query(#9b)",
        "  與 augur.philosophy.evolution 常數 import(#9a)；本工具不產生任何裁決效力。",
        "L6.18(c) 自我利益揭露: 本包對象＝AI 進化引擎自身之晉升裁決——AI 僅呈案與證據整備，",
        "  不得為核准主體；裁決與開閘唯 hugo 親跑（人閘碼 TWEVO-APPLY-go，工具不代簽）。",
        "證偽條件: 底層事實變動（GATE_IDS 改版／promotion_queue 新列／feature_sign_check 新列／",
        "  run 結輪）即使本包過期——裁前重跑本工具；run 尚在 running 時本包一律僅屬預覽。",
        "",
        "── 現場狀態（現查，非抄）",
        f"   run {rid}: status={pack['run_status']} · started={str(pack['started'])[:19]}"
        f" · finished={str(pack['finished'])[:19] if pack['finished'] else '—'}",
    ]
    if pack["run_status"] == "running":
        out.append("   ⚠ run 尚在 running——候選集與閘值仍會變動；本包僅屬預覽，結輪後重跑再裁。")
    kill = " ".join(f"{s}={st}" for s, st in pack["kill"]) or "（表無列＝clear）"
    out.append(f"   kill-switch: {kill}（任一相干 scope=halt 時 I5 一律拒 APPLY）")
    out.append(f"   條件①: GATE_IDS={len(GATE_IDS)} 閘，{'含' if cond1 else '**不含**'} G-SIGN"
               f" → {'✓' if cond1 else '✗（G-SIGN 未入閘＝全部候選不可裁）'}"
               "（機械查 augur.philosophy.evolution.GATE_IDS via import）")
    if not pack["fsc_table_exists"]:
        out.append("   ⚠ feature_sign_check 表不存在——條件②之落帳源缺席，全部候選 cond2=False（fail-closed）")
    out.append("")
    out.append(f"── 候選逐顆（{len(cands)} 顆；每 feature 取該 run 最新一列）")
    out.append("")

    dispatchable: list[Mapping[str, Any]] = []
    for i, c in enumerate(cands, 1):
        out.extend(render_candidate(c, cond1, i, len(cands)))
        _, _, cond2 = gsign_verdicts(c["gate_json"], c["fsc"].get("verdict") if c.get("fsc") else None)
        ready, _ = readiness(cond1, cond2, all_gates_green(c["gate_json"]))
        if ready and c["action"] == "promote" and c["queue_status"] == "pending_auto":
            dispatchable.append(c)

    out.append("── hugo 開閘指令模板（親跑；工具不代簽）")
    out.append("   可裁清單（action=promote ∧ 三條件齊 ∧ queue_status=pending_auto）:")
    if dispatchable:
        for i, c in enumerate(dispatchable, 1):
            out.append(f"     {i}. {c['feature']}（queue_id={c['queue_id']}）")
    else:
        out.append("     （本 run 目前無可裁之 promote 候選）")
    # 全集＝全部 pending_auto **列**（含被新列蓋過之舊世代列）——I5 逐列消費，漏列即漏裁。
    latest_qid = {c["feature"]: c["queue_id"] for c in cands}
    pending_all = pack.get("pending_rows", [])
    out.append("   該 run pending_auto 全集（I5 一次 APPLY 會消費之全部列，供逐顆核對）:")
    if pending_all:
        for p in pending_all:
            sup = ""
            if latest_qid.get(p["feature"]) != p["queue_id"]:
                sup = (f" ⚠ 非最新世代列（同 feature 最新=queue_id "
                       f"{latest_qid.get(p['feature'])}）——I5 仍會消費，裁前先核此列閘值")
            out.append(f"     - {p['feature']}（queue_id={p['queue_id']}, action={p['action']}）{sup}")
    else:
        out.append("     （無 pending_auto 列——I5 無可消費對象）")
    out.append("   # 先乾跑看單顆裁決（唯讀）:")
    out.append("   venv/bin/python scripts/apply_evolution_promotions.py --dry-run --queue-id <N>")
    out.append("   # 逐顆開閘（hugo 親跑;一次恰一顆=S-i 機械載體,2026-08-02 --queue-id 落地後之正路）:")
    out.append(f"   venv/bin/python scripts/apply_evolution_promotions.py --allow-apply --gate-ref {HUMAN_GATE_REF} --queue-id <N>")
    out.append("   ⚠ 舊整批路（--step I5 --allow-apply）仍在但不建議——一次消費該 run 全部 pending_auto")
    out.append("     （含 demote 自動通道列）；改用上行逐顆路;有不欲 APPLY 之列即停手先問（#6），勿旁路。")
    out.append("")
    out.append("   Steward 決定欄: ______________________________（留白待 hugo；工具不代填）")
    return out


# ──────────────────────────── DB 讀取（唯讀） ────────────────────────────

def fetch_pack(conn, run_id: int | None = None) -> dict[str, Any] | None:
    """唯讀彙整：promotion_queue 最新世代列＋feature_sign_check 最新列＋run／kill 現場。零寫入。"""
    with conn.cursor() as cur:
        if run_id is None:
            cur.execute("SELECT max(run_id) FROM evolution_run")
            row = cur.fetchone()
            run_id = row[0] if row else None
        if run_id is None:
            return None
        cur.execute("SELECT status, started_at, finished_at FROM evolution_run WHERE run_id=%s", (run_id,))
        run_row = cur.fetchone()
        if run_row is None:
            return None
        cur.execute("SELECT scope, state FROM evolution_kill_switch WHERE scope IN ('tw','global') ORDER BY scope")
        kill = cur.fetchall()
        cur.execute("SELECT to_regclass('public.feature_sign_check') IS NOT NULL")
        fsc_exists = bool(cur.fetchone()[0])
        cur.execute(
            """SELECT DISTINCT ON (feature)
                      queue_id, feature, action, queue_status, gate_json,
                      count(*) OVER (PARTITION BY feature) AS n_rows
                 FROM promotion_queue WHERE run_id=%s
                ORDER BY feature, queue_id DESC""",
            (run_id,),
        )
        cands = [
            {"queue_id": r[0], "feature": r[1], "action": r[2], "queue_status": r[3],
             "gate_json": r[4], "n_rows": r[5], "fsc": None}
            for r in cur.fetchall()
        ]
        # pending_auto 全集＝**全部列**（非僅最新世代）——I5 消費的是列不是 feature；
        # 2026-08-01 親驗 run 21 有 6 列「被新列蓋過但仍 pending_auto」，只列最新世代會漏報。
        cur.execute(
            """SELECT queue_id, feature, action FROM promotion_queue
                WHERE run_id=%s AND queue_status='pending_auto' ORDER BY queue_id""",
            (run_id,),
        )
        pending_rows = [{"queue_id": r[0], "feature": r[1], "action": r[2]} for r in cur.fetchall()]
        if fsc_exists and cands:
            cur.execute(
                """SELECT DISTINCT ON (feature)
                          feature, verdict, direction, direction_source, point_ic,
                          boot_ics, n_panels, h, checked_at
                     FROM feature_sign_check WHERE feature = ANY(%s)
                    ORDER BY feature, checked_at DESC""",
                ([c["feature"] for c in cands],),
            )
            by_feat = {r[0]: {"verdict": r[1], "direction": r[2], "direction_source": r[3],
                              "point_ic": r[4], "boot_ics": r[5], "n_panels": r[6],
                              "h": r[7], "checked_at": r[8]} for r in cur.fetchall()}
            for c in cands:
                c["fsc"] = by_feat.get(c["feature"])
    return {"run_id": run_id, "run_status": run_row[0], "started": run_row[1],
            "finished": run_row[2], "kill": kill, "fsc_table_exists": fsc_exists,
            "candidates": cands, "pending_rows": pending_rows}


# ──────────────────────────── selftest（免 DB 免 API） ────────────────────────────

# fixture＝真 gate_json 形：抄自 live DB promotion_queue queue_id=599（run 21，2026-08-01 親查），
# 鍵形與數值皆實物（#9b 溯源）；僅裁自測所需欄。
FIXTURE_GATE_JSON: dict[str, Any] = {
    "G-ISO": {"verdict": "PASS", "n_violations": 0},
    "G-MAP": {"verdict": "PASS", "coverage_class": "mapped", "in_feature_values": True},
    "G-PROM": {"verdict": "PASS", "reason": "triad ok",
               "checks": {"hac_t": True, "asof_ic": True, "multi_seed_delta": True},
               "mean_delta_ic": 0.0025369503426230463},
    "G-ECON": {"verdict": "PASS", "reason": "econ ok", "beat_benchmark": True, "dd_ok": True,
               "evidence": {"span": "2021-08-31..2026-04-30", "max_dd": -0.24613261739947323,
                            "n_periods": 57, "port_sharpe": 2.069297016877409,
                            "avg_turnover": 0.12924665746570033, "bench_sharpe": 1.8667604686326615}},
    "G-ATTEST": {"verdict": "PASS", "since": "2021-01-01", "horizon_h": 60,
                 "code_sha": "4b43ac64241b21457c03324f96144038c8b6dc39"},
    "G-KILL": {"verdict": "PASS", "state": "clear", "db": "clear"},
    "G-NOEXEC": {"verdict": "PASS", "hits": []},
    "G-SIGN": {"verdict": "PASS", "judge": "PASS", "direction": -1,
               "direction_source": "principle_factor_map",
               "point_ic": -0.0534185698809342, "n_series": 64,
               "evidence": {"boot_ics": [-0.044550673515956776, -0.0579572111124239,
                                         -0.0517972596703965, -0.04583380572827088,
                                         -0.051895807658224054],
                            "n_series": 64, "point_ic": -0.0534185698809342,
                            "direction": -1, "direction_source": "principle_factor_map",
                            "engine_direction": -1}},
}

FIXTURE_FSC: dict[str, Any] = {
    "verdict": "PASS", "direction": -1, "direction_source": "principle_factor_map",
    "point_ic": -0.0534185698809342,
    "boot_ics": [-0.044550673515956776, -0.0579572111124239, -0.0517972596703965,
                 -0.04583380572827088, -0.051895807658224054],
    "n_panels": 64, "h": 60, "checked_at": "2026-08-01 21:38:38",
}

OLD_SEVEN_GATE_IDS = ("G-ISO", "G-MAP", "G-PROM", "G-ECON", "G-ATTEST", "G-KILL", "G-NOEXEC")


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # 條件①（下游絆線：G-SIGN 若退出 GATE_IDS，本工具之呈案前提崩壞，紅是誠實結果）
    chk("cond1: 現行 GATE_IDS 含 G-SIGN（八閘世代前提）", compute_cond1(GATE_IDS))
    chk("cond1: 舊七閘 tuple → False（紅路）", not compute_cond1(OLD_SEVEN_GATE_IDS))

    # 條件③（fixture 餵真 gate_json 形；判準借道 all_gates_green，#12 同口徑）
    chk("cond3: fixture 八鍵全 PASS → True", all_gates_green(FIXTURE_GATE_JSON))
    no_sign = {k: v for k, v in FIXTURE_GATE_JSON.items() if k != "G-SIGN"}
    chk("cond3: 去 G-SIGN 鍵（舊世代列）→ False", not all_gates_green(no_sign))
    skipped = dict(FIXTURE_GATE_JSON)
    skipped["G-SIGN"] = {"verdict": "SKIP", "reason": "test"}
    chk("cond3: G-SIGN=SKIP → False（SKIP≠PASS）", not all_gates_green(skipped))

    # 條件②（雙源 fail-closed）
    gv, fv, c2 = gsign_verdicts(FIXTURE_GATE_JSON, "PASS")
    chk("cond2: gate=PASS ∧ 落帳=PASS → True", gv == "PASS" and fv == "PASS" and c2)
    chk("cond2: 落帳查無列 → False（查無列＝未通過）", not gsign_verdicts(FIXTURE_GATE_JSON, None)[2])
    chk("cond2: 落帳=UNJUDGEABLE → False", not gsign_verdicts(FIXTURE_GATE_JSON, "UNJUDGEABLE")[2])
    chk("cond2: gate=SKIP ∧ 落帳=PASS → False", not gsign_verdicts(skipped, "PASS")[2])
    gv7, _, c2_7 = gsign_verdicts(no_sign, "PASS")
    chk("cond2: gate 無 G-SIGN 鍵 → (None, False)", gv7 is None and not c2_7)

    # sign 證據（boot 同號數；0 不計同號＝judge_sign 同口徑）
    boots = FIXTURE_GATE_JSON["G-SIGN"]["evidence"]["boot_ics"]
    chk("boot_same_sign: fixture dir=-1 → 5/5", boot_same_sign(boots, -1) == (5, 5))
    flipped = boots[:1] + [+0.001] + boots[2:]
    chk("boot_same_sign: 一席翻號 → 4/5", boot_same_sign(flipped, -1) == (4, 5))
    chk("boot_same_sign: 0 均值不計同號", boot_same_sign([0.0] + boots[1:], -1) == (4, 5))
    chk("boot_same_sign: direction=None → 0 同號", boot_same_sign(boots, None) == (0, 5))

    # readiness 真值表
    chk("readiness(T,T,T)=可裁、零缺項", readiness(True, True, True) == (True, []))
    r1 = readiness(False, True, True)
    chk("readiness 缺① → 不可裁、缺項=①", not r1[0] and len(r1[1]) == 1 and r1[1][0].startswith("①"))
    r2 = readiness(True, False, True)
    chk("readiness 缺② → 不可裁、缺項=②", not r2[0] and len(r2[1]) == 1 and r2[1][0].startswith("②"))
    r3 = readiness(True, True, False)
    chk("readiness 缺③ → 不可裁、缺項=③", not r3[0] and len(r3[1]) == 1 and r3[1][0].startswith("③"))
    chk("readiness 全缺 → 三缺項", readiness(False, False, False)[1].__len__() == 3)

    # 建議行（行為測：函式輸出，非源碼字面）
    chk("建議行: 三條件齊+promote+pending_auto → 可裁", recommend_line(True, [], "promote", "pending_auto").startswith("可裁"))
    chk("建議行: 可裁但非 pending_auto → 帶 I5 不消費警語",
        "pending_auto" in recommend_line(True, [], "promote", "applied"))
    chk("建議行: 缺項 → 以「缺：」開頭並列名", recommend_line(False, ["③八閘未全 PASS"], "promote", "pending_auto").startswith("缺："))

    # G-ECON 數字
    eco = econ_numbers(FIXTURE_GATE_JSON)
    chk("econ_numbers: fixture 六數齊", eco is not None and all(
        eco[k] is not None for k in ("port_sharpe", "bench_sharpe", "max_dd", "n_periods", "span", "avg_turnover")))
    chk("econ_numbers: 無 evidence → None（誠實缺料）",
        econ_numbers({"G-ECON": {"verdict": "PASS"}}) is None)

    # 端到端 render（fixture 餵真形走整條呈案路；驗語意非字面）
    cand = {"queue_id": 599, "feature": "lending_fee_rate_mean_30d", "action": "promote",
            "queue_status": "pending_auto", "gate_json": FIXTURE_GATE_JSON, "n_rows": 1,
            "fsc": FIXTURE_FSC}
    pack = {"run_id": 21, "run_status": "running", "started": "2026-08-01 18:41:39",
            "finished": None, "kill": [("global", "clear"), ("tw", "clear")],
            "fsc_table_exists": True, "candidates": [cand],
            "pending_rows": [
                # 真形（2026-08-01 親驗 run 21）：同 feature 之舊世代列可仍 pending_auto
                {"queue_id": 555, "feature": "lending_fee_rate_mean_30d", "action": "promote"},
                {"queue_id": 599, "feature": "lending_fee_rate_mean_30d", "action": "promote"},
            ]}
    text = "\n".join(render_pack(pack))
    chk("render: 可裁候選進尾節可裁清單", "1. lending_fee_rate_mean_30d（queue_id=599）" in text)
    chk("render: 開閘模板帶人閘碼", f"--allow-apply --gate-ref {HUMAN_GATE_REF}" in text)
    chk("render: running 之 run 帶預覽警語", "尚在 running" in text)
    chk("render: Steward 決定欄留白", "Steward 決定欄" in text and "留白待 hugo" in text)
    chk("render: 全集含被蓋過之舊世代 pending 列（queue_id=555）並帶消費警語",
        "queue_id=555" in text and "非最新世代列" in text)
    chk("render: 最新世代 pending 列（599）不帶非最新警語",
        any(("queue_id=599, action=promote" in ln and "非最新世代列" not in ln) for ln in text.splitlines()))
    bad_cand = dict(cand, gate_json=skipped, fsc=None)
    bad_text = "\n".join(render_candidate(bad_cand, True, 1, 1))
    chk("render: G-SIGN=SKIP ∧ 落帳無列 → 建議行列缺②③、不出「可裁」",
        "缺：" in bad_text and "②" in bad_text and "③" in bad_text and "可裁" not in bad_text)
    chk("render: 落帳無列印 fail-closed 警語", "查無列 ⇒ 未通過" in bad_text)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


# ──────────────────────────── CLI ────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="APPLY-go 決策包（唯讀呈案；裁決唯 hugo）")
    ap.add_argument("--run-id", type=int, default=None, help="指定 run（預設＝最新 run）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    try:
        with db.connect() as conn:
            pack = fetch_pack(conn, a.run_id)
    except Exception as e:  # graceful（#29a）：無參數安全預設不得裸 traceback
        print(f"✗ DB 唯讀查詢失敗：{type(e).__name__}: {e}")
        print("  （本工具唯讀零寫入；確認 .env 與 PostgreSQL 後重試，或先跑 --selftest）")
        return 1
    if pack is None:
        print("✗ 查無 evolution_run 列（或指定之 run-id 不存在）——無從產包")
        return 1
    print("\n".join(render_pack(pack)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
