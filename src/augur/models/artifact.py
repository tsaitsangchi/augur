"""模型 artifact 持久化 — joblib 序列化 fit 好之 estimator + 凍結特徵集 + as-of(SOP §3)。

🎯 這支在做什麼(白話):把 fit 好的模型連同「用了哪些特徵、as-of 哪天、什麼 family/seed」一起
   存成單一 .joblib;predict 時載回 = 離線訓練與上線預測用同一個 artifact(不重算、冪等 resume #6)。
   feats_hash = 特徵集口徑鎖:predict 若當下 canonical 特徵集與 artifact 凍結時不符即拒載(防漂移)。
守 #6(冪等 resume)· #15(feats/as_of 凍結入 artifact、可重現)· 隔離不變式。
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from augur.core import config

MODELS_DIR = config.PROJECT_ROOT / "models_artifacts"


def feats_hash(feats):
    """canonical 特徵集之口徑鎖 hash(順序無關;feats 變則 hash 變 → predict 拒載口徑不符 artifact)。"""
    return hashlib.sha256("\n".join(sorted(feats)).encode()).hexdigest()[:16]


def save(estimator, feats, horizon, asof_snapshot, family, seed, out_dir=None):
    """存 artifact,回 (path:str, feats_hash:str)。"""
    import joblib
    out_dir = Path(out_dir) if out_dir else MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    fh = feats_hash(feats)
    path = out_dir / f"{family}_H{horizon}_{asof_snapshot}_seed{seed}_{fh}.joblib"
    joblib.dump({"estimator": estimator, "feats": list(feats), "horizon": horizon,
                 "asof_snapshot": str(asof_snapshot), "family": family, "seed": seed,
                 "feats_hash": fh}, path)
    return str(path), fh


def load(path):
    """載 artifact dict(estimator/feats/horizon/asof_snapshot/family/seed/feats_hash)。"""
    import joblib
    return joblib.load(path)
