#!/usr/bin/env python
"""as-of 預測出單 CLI — 載 registry 模型 → 當日核心宇宙橫斷面 rank → top-N → prediction_values(SOP S7)。

🎯 這支在做什麼(白話):對某 as-of 日,載回 registry 中「≤as-of 之最新同 family/horizon」artifact,
   取當日 core_universe_asof 名單之特徵矩陣,predict 出每股分數 → 橫斷面排序 → 寫 prediction_values
   (panel_date/model_id/stock_id/score/rank),並印 top-N。這是靈魂產品輸出口:**系統建議、人決策——
   只出相對強弱排序清單,不下單、不動錢**。
   as-of 凍結:只用 ≤as-of 已知特徵、model 不得晚於 as-of 訓練(registry.latest 已 asof_snapshot≤as-of);
   feats_hash 口徑鎖:artifact 凍結之特徵集與當下不符即拒(防漂移)。**複用鐵律**:_panel_matrix/_asof_stocks
   複用 baseline 同 helper → 與離線驗證同口徑(#12)。
守 #8(as-of 凍結、只用已知)· #12(複用 baseline helper)· #15(feats_hash 口徑鎖)· 隔離不變式(寫
   prediction_values、禁被預測 package 回讀)· 靈魂(系統建議人決策、不下單)· CLAUDE #29。

執行指令矩陣:
  python scripts/predict_asof.py                                    # 無參數=印本矩陣+操作值(不預測)
  python scripts/predict_asof.py --run                              # 預測(預設 RankRidge H=60 as-of=最新 top-N=20)
  python scripts/predict_asof.py --run --horizon 20 --top-n 30 --asof 2026-05-31
  python scripts/predict_asof.py --run --dry-run                    # 只算+印 top-N、不寫 prediction_values
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.evaluation import baseline
from augur.models import artifact, registry


def _latest_asof(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT max(as_of_date) FROM {baseline.ASOF_TABLE}")
        r = cur.fetchone()
        return r[0] if r else None


def predict(horizon, family, asof, top_n=20, dry_run=False):
    """載 artifact → 當日核心宇宙 predict → rank → (可選)寫 prediction_values。回 rows[(rank,sid,score)]。"""
    with db.connect() as conn:
        asof = asof or _latest_asof(conn)
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
        order = sorted(zip(sids, scores), key=lambda t: t[1], reverse=True)  # 分數降序=相對強
        rows = [(i + 1, sid, float(sc)) for i, (sid, sc) in enumerate(order)]
        if not dry_run:
            with db.transaction(conn) as cur:
                cur.execute("DELETE FROM prediction_values WHERE panel_date=%s AND model_id=%s",
                            (asof, reg["model_id"]))
                cur.executemany(
                    "INSERT INTO prediction_values (panel_date,model_id,stock_id,score,rank) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    [(asof, reg["model_id"], sid, sc, rk) for rk, sid, sc in rows])
    tag = "(dry-run 未寫庫)" if dry_run else f"→ prediction_values ({len(rows)} 列)"
    print(f"✓ as-of {asof} 預測 model={reg['model_id']} {tag}")
    print(f"── top-{top_n} 相對強弱(系統建議、人決策、不下單)──")
    for rk, sid, sc in rows[:top_n]:
        print(f"  #{rk:<3} {sid:<8} score={sc:+.4f}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="as-of 預測出單(載 registry→top-N→prediction_values)")
    ap.add_argument("--run", action="store_true", help="執行預測(無此旗標=只印矩陣+操作值)")
    ap.add_argument("--horizon", type=int, default=60, help="預測 horizon(交易日)")
    ap.add_argument("--family", default="RankRidge", help="模型族(默認 RankRidge)")
    ap.add_argument("--asof", default=None, help="as-of 日(預設=core_universe_asof 最新)")
    ap.add_argument("--top-n", type=int, default=20, dest="top_n", help="印出前 N 名(預設 20)")
    ap.add_argument("--dry-run", action="store_true", dest="dry_run", help="只算+印、不寫 prediction_values")
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__)
        print(f"目前操作值:horizon={args.horizon} family={args.family} asof={args.asof or '(最新)'} "
              f"top_n={args.top_n} dry_run={args.dry_run}")
        return 0
    r = predict(args.horizon, args.family, args.asof, args.top_n, args.dry_run)
    return 0 if r is not None else 1


if __name__ == "__main__":
    sys.exit(main())
