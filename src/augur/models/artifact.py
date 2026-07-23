"""模型 artifact 持久化 — joblib 序列化 fit 好之 estimator + 凍結特徵集 + as-of(SOP §3)。

🎯 這支在做什麼(白話):把 fit 好的模型連同「用了哪些特徵、as-of 哪天、什麼 family/seed」一起
   存成單一 .joblib;predict 時載回 = 離線訓練與上線預測用同一個 artifact(不重算、冪等 resume #6)。
   feats_hash = 特徵集口徑鎖:predict 若當下 canonical 特徵集與 artifact 凍結時不符即拒載(防漂移)。
守 #6(冪等 resume)· #15(feats/as_of 凍結入 artifact、可重現)· 隔離不變式。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.models.artifact              # 印用途+公開入口（唯讀）
  python -m augur.models.artifact --selftest   # 純紅綠自測（零 IO）
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


def _selftest():
    """自測（零 IO）：純測 feats_hash 之口徑鎖不變式——順序無關、feats 變則變、格式穩定。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    h = feats_hash(["b", "a", "c"])
    chk("feats_hash 順序無關(sorted)", h == feats_hash(["c", "b", "a"]))
    chk("feats_hash 集合變則 hash 變(防漂移)", feats_hash(["a", "b"]) != feats_hash(["a", "b", "c"]))
    chk("feats_hash 格式=16 位 hex", len(h) == 16 and all(c in "0123456789abcdef" for c in h))
    chk("feats_hash 確定性(同輸入同值)", feats_hash(["x", "y"]) == feats_hash(["x", "y"]))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.artifact --selftest;免 DB 免 API)")
