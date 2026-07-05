"""augur models — 特徵 → 橫斷面相對強弱 rank 之預測模型層(SOP 計劃 §3)。

🎯 薄封裝生產模型:RankRidge(默認、與 evaluation.baseline B2_ridge 同組態)+ RankGBDT(挑戰者);
   registry(model_registry CRUD)+ artifact(joblib 持久化)。契約極薄=fit/predict/ndarray。
   **隔離不變式**:本 package 零 import knowledge/philosophy/advisor(audit.import_isolation AST 稽核強制)。
守 隔離不變式 · #12(estimator 組態與 baseline 同一份、複用鐵律)· #15(registry 可重現)。
"""
from augur.models.ranker import RankGBDT, RankRidge

__all__ = ["RankRidge", "RankGBDT"]
