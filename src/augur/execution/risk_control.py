"""部署前風控 overlay — 套在 predict_asof top-decile long 投組上的決策輔助風控(部署計劃 D3)。

🎯 這支在做什麼(白話):把已建好的 long 投組(portfolio.build_long_portfolio 出的 [(sid,weight,rank)])
   加一層**風控 overlay**,三件事(閾值全讀 DB `risk_policy`、不 hardcode #29b)——
     1. **DD 熔斷**:給投組權益回檔序列(simple 報酬),若當前/最深回檔觸 horizon 閾值(STAGE D 修正:
        H60 −20%/H120 −25%,近期深值非全期溫和)→ 建議降倉(reduce_half 減半 / clear 清倉);
     2. **單標的部位上限**:單股權重超 cap(如 0.10)→ 削頂 + 餘量按比例重分配、和維持為 1;
     3. **換手預算**:本期換手率(vs 上期成分)超預算(如 0.75)→ 告警(高換手侵蝕淨值)。
   **DD 回檔算法複用 portfolio.drawdown_series(#12 不重造)**;閾值 load_policies() 讀 risk_policy 表。
   **風控是決策輔助、系統建議人決策——只出降倉建議 + 告警旗標 + cap 後權重,不自動下單、不動錢**(靈魂)。

守 #8(不觸 as-of/未來)· #9/#15(閾值 trace 回 risk_policy.source_ref=STAGE D 修正值、誠實近期深)·
   #12(DD 算法複用 drawdown_series、選股複用 build_long_portfolio、不另造)· #27(閾值操作值住 DB 可調)·
   #29(閾值資料驅動住 DB)· 隔離不變式(唯讀 risk_policy、不進預測管線)· 靈魂(建議非自動駕駛)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.execution.risk_control              # 印用途+公開入口（唯讀）
  python -m augur.execution.risk_control --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from augur.core import db
from augur.evaluation import portfolio

# 換手率複用 portfolio 之單一住所實作(#12,勿另造)
_turnover = portfolio._turnover


def load_policies(conn, horizon):
    """讀 risk_policy 表某 horizon 之三類閾值(#29b 資料驅動、不 hardcode)。

    回 {policy_key: {'threshold': float, 'action': str, 'source_ref': str, 'note': str}}。
    缺某 policy_key → 該鍵不在 dict(呼叫端須 graceful:無政策=不套該風控、印告警,#15 不假裝有)。
    """
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT policy_key, threshold, action, source_ref, note "
            "FROM risk_policy WHERE horizon=%s", (horizon,))
        return {k: {"threshold": float(t), "action": a, "source_ref": sr, "note": nt}
                for k, t, a, sr, nt in cur.fetchall()}


def dd_circuit(dd_returns, policy):
    """DD 熔斷:回檔序列 → 是否觸發降倉 + 建議。

    dd_returns=投組**歷史 simple 報酬序列**(每期一值,最新在末);policy=load_policies()['dd_circuit']。
    當前回檔=drawdown_series(dd_returns)[-1](權益 vs 歷來高點,≤0)、最深回檔=該序列 min。
    觸發條件:**當前回檔 ≤ 閾值**(如當前 −22% ≤ −20% → 觸)。回 dict:
      {triggered, current_dd, max_dd, threshold, action, source_ref, message}。
    policy 為 None(無此政策)→ triggered=False + 誠實 message「無 dd_circuit 政策」(#15 不假裝)。
    """
    if policy is None:
        return {"triggered": False, "current_dd": None, "max_dd": None, "threshold": None,
                "action": None, "source_ref": None, "message": "無 dd_circuit 政策(risk_policy 未 seed 該 horizon)"}
    _, dd = portfolio.drawdown_series(dd_returns)
    if len(dd) == 0:
        return {"triggered": False, "current_dd": None, "max_dd": None,
                "threshold": policy["threshold"], "action": policy["action"],
                "source_ref": policy["source_ref"], "message": "無有效報酬序列、無法評估回檔"}
    cur_dd = float(dd[-1])
    max_dd = float(dd.min())
    thr = policy["threshold"]
    triggered = cur_dd <= thr
    act = policy["action"] if triggered else "hold"
    msg = (f"⚠ DD 熔斷觸發:當前回檔 {cur_dd:+.1%} ≤ 閾值 {thr:+.1%} → 建議 {act}(系統建議、人決策)"
           if triggered else
           f"✓ 回檔 {cur_dd:+.1%} 未觸閾值 {thr:+.1%};維持部位")
    return {"triggered": triggered, "current_dd": cur_dd, "max_dd": max_dd,
            "threshold": thr, "action": act, "source_ref": policy["source_ref"], "message": msg}


def apply_position_cap(port, policy):
    """單標的部位上限:超 cap 之權重削頂,削掉的總量按未達 cap 者比例重分配,和維持為 1。

    port=[(sid, weight, rank), ...](build_long_portfolio 出);policy=load_policies()['max_position']。
    迭代收斂:每輪把 >cap 者夾到 cap、把溢出量分給仍 <cap 者(依其權重比例),直到無人超 cap 或無處可分。
    回 (new_port, capped_sids):new_port 同結構、權重已受控;capped_sids=被夾頂之股列表。
    policy 為 None → 原封不動回、capped=[](#15 不假裝套了 cap)。
    等權投組(每股 1/N ≤ cap)本就不觸、原樣回(#25 實測情境)。
    **可行性**:cap 只在 N×cap≥1 時能維持權重和為 1;若 N×cap<1(檔數過少、cap 太緊,如 5 檔×0.10=0.5)
    則全夾頂後和 = N×cap < 1——**誠實不硬塞回 1**(硬塞回 1 = 反把權重推回集中、違 cap 本意 #15)。
    生產 top-decile(≥10 檔)cap 0.10 恒可行;此邊界僅退化小投組會遇。
    """
    if policy is None or not port:
        return list(port), []
    cap = policy["threshold"]
    sids = [s for s, _, _ in port]
    ranks = {s: r for s, _, r in port}
    w = {s: float(wt) for s, wt, _ in port}
    capped = set()
    for _ in range(len(sids) + 1):                       # 保證收斂(每輪至少夾一人或停)
        over = {s: w[s] for s in sids if w[s] > cap + 1e-12}
        if not over:
            break
        excess = sum(w[s] - cap for s in over)
        for s in over:
            w[s] = cap
            capped.add(s)
        free = [s for s in sids if s not in capped]      # 仍可承接溢出(未夾頂)者
        base = sum(w[s] for s in free)
        if not free or base <= 0:                        # 無處可分(全被夾)→ 溢出留著、和 <1,誠實不硬塞
            break
        for s in free:
            w[s] += excess * (w[s] / base)
    new_port = sorted(((s, w[s], ranks[s]) for s in sids), key=lambda t: t[2])
    return new_port, sorted(capped, key=lambda s: ranks[s])


def turnover_check(cur_ids, prev_ids, policy):
    """換手預算:本期換手率(vs 上期成分)超預算 → 告警。

    cur_ids/prev_ids=本期/上期投組股 id 列表;policy=load_policies()['turnover_budget']。
    換手率複用 portfolio._turnover(#12);prev_ids=None(初次建倉)→ turnover=1、不當超預算告警。
    回 {turnover, budget, over_budget, action, source_ref, message}。policy None → over_budget=False + 誠實 message。
    """
    if policy is None:
        return {"turnover": None, "budget": None, "over_budget": False, "action": None,
                "source_ref": None, "message": "無 turnover_budget 政策(risk_policy 未 seed 該 horizon)"}
    turn = _turnover(cur_ids, prev_ids)
    budget = policy["threshold"]
    first = prev_ids is None
    over = (not first) and turn > budget
    if first:
        msg = f"初次建倉(換手 {turn:.0%} 不計入預算)"
    elif over:
        msg = f"⚠ 換手 {turn:.0%} > 預算 {budget:.0%} → {policy['action']}(高換手侵蝕淨值、建議限制換股數)"
    else:
        msg = f"✓ 換手 {turn:.0%} ≤ 預算 {budget:.0%}"
    return {"turnover": turn, "budget": budget, "over_budget": over,
            "action": policy["action"], "source_ref": policy["source_ref"], "message": msg}


def apply_overlay(conn, horizon, port, *, dd_returns=None, prev_ids=None):
    """三項風控一次套上投組 → 建議報告 + 受控權重(predict_asof 收尾呼叫此支)。

    conn=DB 連線;horizon=模型 horizon(決定讀哪組閾值);port=build_long_portfolio 出之投組。
    dd_returns=投組歷史 simple 報酬序列(None=無歷史、DD 熔斷不評估);prev_ids=上期投組股(None=初次建倉)。
    回 dict:{horizon, policies_loaded, dd_circuit, position_cap:{new_port,capped}, turnover, controlled_port}。
    controlled_port=套 cap 後之最終權重投組(DD 降倉為**建議旗標**、不自動改權重——人決策)。
    **不自動下單**:DD 熔斷/換手僅出旗標與建議,唯 position_cap 為機械可逆之權重正規化(防單股集中)。
    """
    pol = load_policies(conn, horizon)
    dd = dd_circuit(dd_returns, pol.get("dd_circuit")) if dd_returns is not None else \
        {"triggered": False, "current_dd": None, "max_dd": None, "threshold": None,
         "action": None, "source_ref": None, "message": "未提供報酬序列、DD 熔斷未評估"}
    new_port, capped = apply_position_cap(port, pol.get("max_position"))
    turn = turnover_check([s for s, _, _ in new_port], prev_ids, pol.get("turnover_budget"))
    return {"horizon": horizon, "policies_loaded": sorted(pol.keys()),
            "dd_circuit": dd, "position_cap": {"new_port": new_port, "capped": capped},
            "turnover": turn, "controlled_port": new_port}


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成投組紅綠測三項純風控——
    apply_position_cap 削頂+和守恆、dd_circuit 熔斷觸發判準、turnover_check 換手預算。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # apply_position_cap:純 dict 數學(#12 削頂+溢出重分配)
    port = [("A", 0.7, 1), ("B", 0.1, 2), ("C", 0.1, 3), ("D", 0.1, 4)]
    cp = {"threshold": 0.4, "action": "cap", "source_ref": "t", "note": ""}
    nport, capped = apply_position_cap(port, cp)
    wmap = {s: w for s, w, _ in nport}
    chk("cap 削頂 A→0.4 且入 capped", abs(wmap["A"] - 0.4) < 1e-9 and capped == ["A"])
    chk("cap 後權重和守恆=1", abs(sum(w for _, w, _ in nport) - 1.0) < 1e-9)
    eqp = [("A", 0.25, 1), ("B", 0.25, 2), ("C", 0.25, 3), ("D", 0.25, 4)]
    n2, c2 = apply_position_cap(eqp, cp)
    chk("等權未觸 cap→原樣、capped 空", n2 == eqp and c2 == [])
    chk("policy=None→原樣不套 cap", apply_position_cap(port, None) == (port, []))

    # dd_circuit:當前回檔 ≤ 閾值→觸發(drawdown_series #12 複用)
    dp = {"threshold": -0.20, "action": "reduce_half", "source_ref": "t", "note": ""}
    trig = dd_circuit([0.1, 0.1, -0.3], dp)      # 末期權益 −30% 回檔 ≤ −20%
    chk("dd 當前回檔 ≤ 閾值→觸發+建議降倉", trig["triggered"] and trig["action"] == "reduce_half")
    calm = dd_circuit([0.1, 0.1, 0.1], dp)       # 單調上升、無回檔
    chk("dd 無回檔→不觸發、action=hold", (not calm["triggered"]) and calm["action"] == "hold")
    chk("dd policy=None→不觸發(誠實無政策)", dd_circuit([0.1], None)["triggered"] is False)

    # turnover_check:換手率 vs 預算(_turnover #12 複用)
    tp = {"threshold": 0.75, "action": "limit", "source_ref": "t", "note": ""}
    chk("換手初次建倉→不計超預算",
        turnover_check(["A", "B"], None, tp)["over_budget"] is False)
    chk("換手 100% > 預算 75%→超",
        turnover_check(["A", "B", "C", "D"], ["E", "F", "G", "H"], tp)["over_budget"] is True)
    chk("換手 25% ≤ 預算→不超",
        turnover_check(["A", "B", "C", "D"], ["A", "B", "C", "X"], tp)["over_budget"] is False)
    chk("換手 policy=None→不超(誠實無政策)",
        turnover_check(["A"], ["B"], None)["over_budget"] is False)

    # 結構斷言:IO-bound 入口存在(load_policies/apply_overlay 需 conn,此處僅驗可呼叫名)
    chk("IO 入口 load_policies/apply_overlay 具在",
        callable(load_policies) and callable(apply_overlay))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.execution.risk_control --selftest;免 DB 免 API)")
