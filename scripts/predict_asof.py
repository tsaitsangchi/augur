#!/usr/bin/env python
"""as-of 預測出單 CLI — 載 registry 模型 → 當日核心宇宙橫斷面 rank → top-decile long 投組 → prediction_values(SOP S7)。

🎯 這支在做什麼(白話):對某 as-of 日,載回 registry 中「≤as-of 之最新同 family/horizon」artifact,
   取當日 core_universe_asof 名單之特徵矩陣,predict 出每股分數 → 橫斷面排序 →**用共用投組 fn 建 top-decile
   long 投組**(portfolio.build_long_portfolio,#12 命門:與 run_backtest 同一支選股邏輯、零雙軌漂移)→
   寫 prediction_values(panel_date/model_id/stock_id/score/rank/in_portfolio/weight),並印投組。這是靈魂
   產品輸出口:**系統建議、人決策——只出相對強弱排序 + long 部位建議,不下單、不動錢**。
   as-of 凍結:只用 ≤as-of 已知特徵、model 不得晚於 as-of 訓練(registry.latest 已 asof_snapshot≤as-of);
   feats_hash 口徑鎖:artifact 凍結之特徵集與當下不符即拒(防漂移)。**複用鐵律**:_panel_matrix/_asof_stocks
   複用 baseline 同 helper、投組建構複用 portfolio.build_long_portfolio → 與離線回測同口徑(#12)。
守 #8(as-of 凍結、只用已知)· #12(複用 baseline helper + 共用投組 fn)· #15(feats_hash 口徑鎖)· 隔離不變式(寫
   prediction_values、禁被預測 package 回讀)· 靈魂(系統建議人決策、不下單)· CLAUDE #29。

執行指令矩陣:
  python scripts/predict_asof.py                                    # 無參數=印本矩陣+操作值(不預測)
  python scripts/predict_asof.py --run                              # 預測(預設 RankRidge H=60 top10% equal LO as-of=最新)
  python scripts/predict_asof.py --run --horizon 120 --asof 2026-05-31  # STAGE D 首選(Ridge H120 LO top10%)
  python scripts/predict_asof.py --run --top-frac 0.1 --weight equal   # long 投組分位/加權(預設 top10% 等權)
  python scripts/predict_asof.py --run --weight pred --risk-control    # pred 加權 + 收尾風控 overlay(單標的 cap/DD/換手)
  python scripts/predict_asof.py --run --dry-run                    # 只算+印、不寫 prediction_values
  python scripts/predict_asof.py --run --horizon 40 --asof 2026-05-31 --candidate   # D4 候選語意單 horizon 重跑
  python scripts/predict_asof.py --candidate --rewrite-all --asof 2026-05-31        # D4 四 horizon 既有列冪等重寫
"""
import argparse
import datetime as _dt
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation import baseline, label as label_mod, portfolio
from augur.execution import risk_control
from augur.models import artifact, registry

COST_TW = 0.00585   # 台股來回成本(換手扣、同 portfolio 回測口徑 #12)


def _as_date(v):
    """CLI 傳入 as-of 為字串 → date 物件(baseline helper 之 = ANY(date[]) 需型別一致,防 date=text)。"""
    return _dt.date.fromisoformat(v) if isinstance(v, str) else v


def _latest_asof(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT max(as_of_date) FROM {baseline.ASOF_TABLE}")
        r = cur.fetchone()
        return r[0] if r else None


def _deployed_dd_returns(conn, model_id, asof, h):
    """已部署投組之**實現**淨報酬序列(供 DD 熔斷算當前回檔;#8 命門:只用 forward 窗已關閉、報酬全實現之過去 panel)。

    對每個 < asof 之過去 prediction_values panel P:**唯 P 之後第 h 個交易日 ≤ asof(forward 窗已關閉)才納入**
    (窗未關閉=報酬未實現=未來,一律跳過,#8 零 look-ahead);取該 panel in_portfolio 股+權重,以 label.forward_returns
    (已實現價、#12 複用)算加權 simple 報酬 gross,扣換手成本(vs 上期成分)得淨,依 panel 升序串成序列。
    回 [net_ret,...];不足(現況 1 期/窗未關)→ [](DD 熔斷 dormant、誠實不假裝有歷史 #15)。
    """
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM prediction_values "
                    "WHERE model_id=%s AND panel_date<%s ORDER BY panel_date", (model_id, asof))
        panels = [r[0] for r in cur.fetchall()]
    rets, prev_ids = [], None
    for p in panels:
        future = [d for d in cal if d > p]
        # exit = 進場後第 h 個交易日 = future[h](_entry_exit 口徑);exit ≤ asof 才算窗已關閉、報酬全實現(#8)
        if len(future) < h + 1 or future[h] > asof:          # forward 窗未關閉 → 報酬未實現、跳過(#8 零 look-ahead)
            continue
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id, weight FROM prediction_values "
                        "WHERE model_id=%s AND panel_date=%s AND in_portfolio ORDER BY rank", (model_id, p))
            port = cur.fetchall()
        if not port:
            continue
        sids = [s for s, _ in port]
        w = {s: float(wt) for s, wt in port}
        fwd = label_mod.forward_returns(conn, p, sids, h, calendar=cal)   # 已實現 log 報酬
        common = [s for s in sids if s in fwd]
        if not common:
            continue
        gross = float(sum(w[s] * float(np.expm1(fwd[s])) for s in common))
        turn = portfolio._turnover(sids, prev_ids)
        rets.append(gross - turn * COST_TW)                  # 淨(扣換手、同回測口徑)
        prev_ids = sids
    return rets


def _prev_portfolio(conn, model_id, asof):
    """上一期(< asof 之最近 panel)同 model 之投組成分股(in_portfolio),供風控換手檢查。
    無前期(初次建倉)→ None(turnover_check 視為初次、不當超預算告警,#15)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT max(panel_date) FROM prediction_values WHERE model_id=%s AND panel_date<%s",
                    (model_id, asof))
        prev = cur.fetchone()[0]
        if prev is None:
            return None
        cur.execute("SELECT stock_id FROM prediction_values "
                    "WHERE model_id=%s AND panel_date=%s AND in_portfolio ORDER BY rank", (model_id, prev))
        return [r[0] for r in cur.fetchall()]


def predict(horizon, family, asof, top_n=20, top_frac=0.1, weight="equal", dry_run=False,
            risk=False):
    """載 artifact → 當日核心宇宙 predict → rank → 共用 fn 建 top-decile long 投組 → (可選)寫 prediction_values。

    回 rows[(rank,sid,score,in_portfolio,weight)]。投組建構複用 portfolio.build_long_portfolio(#12 命門:
    與 run_backtest 同一支選股邏輯、live≡回測零漂移)。risk=True 時收尾套 execution.risk_control overlay
    (單標的 cap 生效於落庫權重;DD 熔斷/換手為建議旗標、不自動下單),閾值讀 risk_policy(#29b)。
    """
    with db.connect() as conn:
        asof = _as_date(asof) or _latest_asof(conn)
        if asof is None:
            print("✗ core_universe_asof 無資料;中止。"); return None
        reg = registry.latest(family, horizon, asof)
        if reg is None:
            print(f"✗ registry 無 ≤{asof} 之 {family} H={horizon} 模型;先跑 train_ranker.py。"); return None
        art = artifact.load(reg["artifact_path"])
        feats = art["feats"]
        # feats_hash 口徑鎖:當下 canonical 特徵集須與 artifact 凍結時一致
        cur_feats = baseline.canonical_features(conn, [asof]) or feats
        if artifact.feats_hash(feats) != reg["feats_hash"]:
            print(f"✗ artifact feats_hash 與 registry 不符(artifact 損壞?);中止。"); return None
        stocks = baseline._asof_stocks(conn, asof)
        if not stocks:
            print(f"✗ {asof} 無 core_universe_asof 名單;中止。"); return None
        sids, X = baseline._panel_matrix(conn, asof, stocks, feats)
        if len(sids) < 5:
            print(f"✗ {asof} 全 feats 齊之股僅 {len(sids)}<5(特徵覆蓋不足);中止。"); return None
        scores = art["estimator"].predict(X)
        order = sorted(zip(sids, [float(s) for s in scores]), key=lambda t: t[1], reverse=True)  # 分數降序=相對強
        # 共用投組 fn:top-frac long 選取 + 權重(#12,與 run_backtest 位元一致)
        port = portfolio.build_long_portfolio(sids, scores, top_frac=top_frac, weight=weight)
        overlay = None
        if risk:                                                         # 收尾風控 overlay(D3):cap 生效於權重、DD/換手出旗標
            prev_ids = _prev_portfolio(conn, reg["model_id"], asof)      # 上期投組 → 換手 live(#12,無前期=初次建倉)
            dd_rets = _deployed_dd_returns(conn, reg["model_id"], asof, horizon)  # 已實現部署報酬序列 → DD熔斷 live(#8 只用已關閉窗)
            overlay = risk_control.apply_overlay(conn, horizon, port,
                                                 dd_returns=(dd_rets or None), prev_ids=prev_ids)
            port = overlay["controlled_port"]                            # 受控權重(單標的 cap)落庫
        pw = {sid: w for sid, w, _ in port}                              # {入選股: 權重}
        rows = [(i + 1, sid, sc, sid in pw, pw.get(sid, 0.0)) for i, (sid, sc) in enumerate(order)]
        if not dry_run:
            with db.transaction(conn) as cur:
                cur.execute("DELETE FROM prediction_values WHERE panel_date=%s AND model_id=%s",
                            (asof, reg["model_id"]))
                cur.executemany(
                    "INSERT INTO prediction_values (panel_date,model_id,stock_id,score,rank,in_portfolio,weight) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [(asof, reg["model_id"], sid, sc, rk, inp, w) for rk, sid, sc, inp, w in rows])
    tag = "(dry-run 未寫庫)" if dry_run else f"→ prediction_values ({len(rows)} 列)"
    n_port = len(port)
    print(f"✓ as-of {asof} 預測 model={reg['model_id']} {tag}")
    print(f"── long 投組建議 top{top_frac:.0%}/{weight}({n_port} 檔;系統建議、人決策、不下單)──")
    for rk, sid, sc, inp, w in rows:
        if inp:
            print(f"  #{rk:<3} {sid:<8} score={sc:+.4f} w={w:.4f}")
    print(f"── 排序 top-{top_n}(★=入投組)──")
    for rk, sid, sc, inp, w in rows[:top_n]:
        print(f"  {'★' if inp else ' '} #{rk:<3} {sid:<8} score={sc:+.4f}")
    if overlay is not None:
        _print_risk(overlay)
    return rows


def _print_risk(overlay):
    """印風控 overlay 報告(D3:DD 熔斷/單標的 cap/換手;閾值 trace risk_policy.source_ref)。"""
    print(f"── 風控 overlay(H{overlay['horizon']}、政策讀 risk_policy;系統建議、人決策、不下單)──")
    if not overlay["policies_loaded"]:
        print("  ⚠ risk_policy 無此 horizon 政策 → 先跑 migrate_risk_policy_ddl.py seed(#15 未套風控)")
        return
    print(f"  已載政策: {', '.join(overlay['policies_loaded'])}")
    print(f"  DD 熔斷 : {overlay['dd_circuit']['message']}")
    cap = overlay["position_cap"]
    if cap["capped"]:
        print(f"  部位上限: 削頂 {len(cap['capped'])} 檔 {cap['capped']}(權重已受控、和維持 1)")
    else:
        print(f"  部位上限: 無單股超上限(等權自然分散、未觸 cap)")
    print(f"  換手預算: {overlay['turnover']['message']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="as-of 預測出單(載 registry→top-N→prediction_values)")
    ap.add_argument("--run", action="store_true", help="執行預測(無此旗標=只印矩陣+操作值)")
    ap.add_argument("--horizon", type=int, default=60, help="預測 horizon(交易日)")
    ap.add_argument("--family", default="RankRidge", help="模型族(默認 RankRidge)")
    ap.add_argument("--asof", default=None, help="as-of 日(預設=core_universe_asof 最新)")
    ap.add_argument("--top-n", type=int, default=20, dest="top_n", help="排序印出前 N 名(預設 20)")
    ap.add_argument("--top-frac", type=float, default=0.1, dest="top_frac", help="long 投組分位(預設 STAGE D top10%%)")
    ap.add_argument("--weight", default="equal", choices=["equal", "pred"], help="投組加權(equal=STAGE D LO/pred=rank 加權)")
    ap.add_argument("--dry-run", action="store_true", dest="dry_run", help="只算+印、不寫 prediction_values")
    ap.add_argument("--risk-control", action="store_true", dest="risk",
                    help="收尾套 execution.risk_control overlay(單標的 cap 生效於落庫權重、DD/換手出旗標;閾值讀 risk_policy #29b)")
    ap.add_argument("--candidate", action="store_true",
                    help="D4 候選語意明示:in_portfolio=該 horizon top-frac 候選組合成員(非「已部署」;部署事實由 payload 讀 registry 獨立承載)")
    ap.add_argument("--rewrite-all", action="store_true", dest="rewrite_all",
                    help="D4 全量重寫:四 horizon {20,40,60,120} 既有列 per (panel_date,model_id) DELETE+INSERT 冪等重寫(需 --candidate 與 --asof)")
    args = ap.parse_args(argv)
    if args.rewrite_all:
        if not (args.candidate and args.asof):
            print("✗ --rewrite-all 需 --candidate(語意明示)與 --asof(明確時點,不默認最新)"); return 1
        ok = True
        for h in (20, 40, 60, 120):    # 封閉集(82=D1(a) 條件觸發後加入)
            print(f"── D4 重寫 H{h} ──")
            try:
                r = predict(h, args.family, args.asof, args.top_n, args.top_frac, args.weight, False, False)
            except Exception as e:     # 單 horizon 失敗(如 artifact 缺檔)不得炸全場;錯得大聲、續跑其餘(#15)
                print(f"✗ H{h} 失敗:{e}")
                r = None
            ok = ok and (r is not None)
        return 0 if ok else 1
    if not args.run:
        print(__doc__)
        print(f"目前操作值:horizon={args.horizon} family={args.family} asof={args.asof or '(最新)'} "
              f"top_n={args.top_n} top_frac={args.top_frac} weight={args.weight} dry_run={args.dry_run} "
              f"risk={args.risk}")
        return 0
    r = predict(args.horizon, args.family, args.asof, args.top_n, args.top_frac, args.weight,
                args.dry_run, args.risk)
    return 0 if r is not None else 1


if __name__ == "__main__":
    sys.exit(main())
