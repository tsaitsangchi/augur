#!/usr/bin/env python
"""排序模型訓練 CLI — as-of purged 生產模型 fit → artifact + model_registry(SOP 階段 A/S6)。

🎯 這支在做什麼(白話):對 ≤as-of 之所有已實現 label 的核心 panel,用 canonical 特徵集 fit 一個生產
   RankRidge(或挑戰者 RankGBDT),存成 artifact + 登錄 registry,供 predict_asof 載回出單。
   **複用鐵律**:特徵矩陣/label/as-of 名單全複用 evaluation.baseline 之同一 helper(canonical_features
   /_fold_xy/_asof_stocks)→ 離線驗證(baseline.run_ladder B2)與上線預測同組態、零雙軌漂移(#12);
   RankRidge estimator 與 baseline B2_ridge 逐值等同(已冒煙驗證)。
   as-of 凍結:panels 一律 ≤as_of;label 未實現之近 panel 由 label 自然回空、_fold_xy 跳過(#8)。
   (階段 A 骨幹:先端到端跑通;embargo 保證下界/提拔 HAC gate/經濟終關 = 階段 A'/B/C 續接。)
守 #8(as-of 凍結、label 層 t+1)· #12(複用 baseline helper、estimator 同組態)· #15(registry git_sha/
   feats_hash 凍結可重現)· #6(冪等:同 model_id 已登錄可 --resume 跳過)· CLAUDE #29 · 隔離不變式。

執行指令矩陣:
  python scripts/train_ranker.py                                   # 無參數=印本矩陣+操作值(安全預設、不訓練)
  python scripts/train_ranker.py --run                             # 訓練(預設 RankRidge H=60 seed=42 as-of=最新)
  python scripts/train_ranker.py --run --horizon 20 --family RankRidge --asof 2026-05-31
  python scripts/train_ranker.py --run --family RankGBDT --seed 1  # 挑戰者
  python scripts/train_ranker.py --run --resume                    # 同 model_id 已登錄則跳過(冪等)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.evaluation import baseline, label as label_mod
from augur.models import artifact, registry
from augur.models.ranker import RankGBDT, RankRidge

FAMILIES = {"RankRidge": RankRidge, "RankGBDT": RankGBDT}


def _train_note(horizon):
    """model_registry.metrics.note = 誠實使用 caveat(trace 回 STAGE D SSOT、非估算數字)。"""
    base = ("long-only 生產模型;經濟成功度量=淨 Sharpe/Calmar 非 IC(#14);"
            "survivorship 債 b 未閉環(core_universe_asof 實為當前存活名單)→ as-of IC 帶樂觀偏誤,呈現須明標。")
    if horizon >= 120:
        base += (" ⚠ H120 近期(2021+)非重疊經濟回測 n≈8 小樣本(STAGE D)——"
                 "抽樣誤差大、排名方向性非精確保證;定論待持續再驗證資料累積(#15)。")
    return base


def _panels_upto(conn, asof):
    """≤as_of 之所有特徵 panel_date(升序)。"""
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT DISTINCT panel_date FROM {baseline.FEATURE_TABLE} "
                    f"WHERE panel_date<=%s ORDER BY panel_date", (asof,))
        return [r[0] for r in cur.fetchall()]


def _latest_asof(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"SELECT max(as_of_date) FROM {baseline.ASOF_TABLE}")
        r = cur.fetchone()
        return r[0] if r else None


def train(horizon, family, seed, asof, resume=False):
    """fit 生產模型 → 存 artifact + 登錄 registry。回 (model_id, path, metrics_stub)。"""
    est_cls = FAMILIES[family]
    with db.connect() as conn:
        asof = asof or _latest_asof(conn)
        if asof is None:
            print("✗ core_universe_asof 無資料(先建 universe);中止。"); return None
        panels = _panels_upto(conn, asof)
        if len(panels) < 3:
            print(f"✗ ≤{asof} 之 panel 僅 {len(panels)} 個,不足訓練;中止。"); return None
        feats = baseline.canonical_features(conn, panels)
        fh = artifact.feats_hash(feats)
        model_id = f"{family}_H{horizon}_{asof}_seed{seed}_{fh}"
        if resume and registry.exists(model_id):
            print(f"↩ {model_id} 已登錄,--resume 跳過。"); return (model_id, None, None)
        cal = label_mod.full_calendar(conn)
        # as-of 生產模型:train 於所有 ≤as_of panel(label 未實現者 _fold_xy 自然跳過);asof=True 逐 panel 用 point-in-time 核心
        X, y = baseline._fold_xy(conn, panels, None, feats, horizon, calendar=cal, asof=True)
        if len(y) < 50:
            print(f"✗ 可用訓練樣本 {len(y)}<50(label 未實現/覆蓋不足);中止。"); return None
        est = est_cls(seed=seed) if family == "RankGBDT" else est_cls()
        est.fit(X, y)
        path, fh2 = artifact.save(est, feats, horizon, asof, family, seed)
        metrics = {"n_train_rows": int(len(y)), "n_feats": len(feats), "n_panels": len(panels),
                   "note": _train_note(horizon)}   # 誠實 caveat(#15;non-fabricated、trace 回 STAGE D SSOT)
        registry.register(model_id, family, horizon, (panels[0], asof), asof, fh2, seed, metrics, path)
    print(f"✓ 訓練完成 model_id={model_id}")
    print(f"  train_rows={len(y)} feats={len(feats)} panels={len(panels)}([{panels[0]}..{asof}])")
    print(f"  artifact={path}")
    return (model_id, path, metrics)


def main(argv=None):
    ap = argparse.ArgumentParser(description="排序模型訓練(as-of 生產模型→artifact+registry;複用鐵律)")
    ap.add_argument("--run", action="store_true", help="執行訓練(無此旗標=只印矩陣+操作值)")
    ap.add_argument("--horizon", type=int, default=60, help="預測 horizon(交易日;主戰場 20/60,H=252 禁入)")
    ap.add_argument("--family", default="RankRidge", choices=list(FAMILIES), help="模型族(默認 RankRidge)")
    ap.add_argument("--seed", type=int, default=42, help="random seed")
    ap.add_argument("--asof", default=None, help="as-of 凍結日(預設=core_universe_asof 最新)")
    ap.add_argument("--resume", action="store_true", help="同 model_id 已登錄則跳過(冪等)")
    args = ap.parse_args(argv)
    if args.horizon == 252:
        print("✗ H=252 禁入提拔/經濟主表(embargo=4 結構洩漏,SOP 拍板2);中止。"); return 1
    if not args.run:
        print(__doc__)
        print(f"目前操作值:horizon={args.horizon} family={args.family} seed={args.seed} "
              f"asof={args.asof or '(最新)'} resume={args.resume}")
        return 0
    r = train(args.horizon, args.family, args.seed, args.asof, args.resume)
    return 0 if r else 1


if __name__ == "__main__":
    sys.exit(main())
