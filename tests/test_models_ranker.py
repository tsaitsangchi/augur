"""models 層單元回歸 — RankRidge≡baseline B2 組態 + artifact/feats_hash(不連 DB;SOP 階段 A)。"""
import numpy as np
import pytest


def test_rankridge_equals_baseline_b2_config():
    """RankRidge 必與 baseline B2(StandardScaler+Ridge(1.0))逐值等同(複用鐵律 #12、防雙軌漂移)。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from augur.models.ranker import RankRidge
    rng = np.random.default_rng(0)
    Xtr, ytr, Xte = rng.standard_normal((60, 5)), rng.standard_normal(60), rng.standard_normal((15, 5))
    sc = StandardScaler().fit(Xtr)
    ref = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xte))
    got = RankRidge().fit(Xtr, ytr).predict(Xte)
    assert np.allclose(ref, got)


def test_feats_hash_order_invariant():
    from augur.models import artifact
    assert artifact.feats_hash(["a", "b", "c"]) == artifact.feats_hash(["c", "a", "b"])
    assert artifact.feats_hash(["a", "b"]) != artifact.feats_hash(["a", "b", "c"])


def test_ranker_predict_before_fit_raises():
    from augur.models.ranker import RankGBDT, RankRidge
    for cls in (RankRidge, RankGBDT):
        with pytest.raises(RuntimeError):
            cls().predict(np.zeros((3, 4)))


def test_artifact_roundtrip(tmp_path):
    from augur.models import artifact
    from augur.models.ranker import RankRidge
    rng = np.random.default_rng(1)
    X, y, Xte = rng.standard_normal((40, 4)), rng.standard_normal(40), rng.standard_normal((10, 4))
    est = RankRidge().fit(X, y)
    path, fh = artifact.save(est, ["f0", "f1", "f2", "f3"], 60, "2026-05-31", "RankRidge", 0, out_dir=tmp_path)
    d = artifact.load(path)
    assert np.allclose(est.predict(Xte), d["estimator"].predict(Xte))
    assert d["feats_hash"] == fh and d["horizon"] == 60 and d["family"] == "RankRidge"
