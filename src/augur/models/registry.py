"""模型登錄 — model_registry 表 CRUD(#15 可重現 + resume 帳本;SOP §3)。

🎯 這支在做什麼(白話):每 fit 好一個模型,把身分證(family/horizon/train_span/as-of/feats_hash/
   seed/metrics/artifact_path/git_sha)寫進 model_registry;predict 時查「≤as-of 之最新同 family/
   horizon artifact」載回。resume:已訓折/模型可查、重跑冪等 upsert(#6)。
守 #15(git_sha/feats_hash 凍結可重現)· #6(resume 冪等)· 隔離不變式(非預測輸入表)。
"""
from __future__ import annotations

import json
import subprocess

from augur.core import db


def git_sha():
    """當前 git HEAD sha(半年重跑一致鍵);非 git 環境回 'nogit'。"""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "nogit"
    except Exception:
        return "nogit"


def register(model_id, family, horizon, train_span, asof_snapshot, feats_hash, seed,
             metrics, artifact_path, sha=None):
    """冪等 upsert 一列(ON CONFLICT model_id DO UPDATE)。train_span=(lo_date, hi_date)。"""
    lo, hi = train_span
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            """INSERT INTO model_registry
               (model_id,family,horizon,train_span,asof_snapshot,feats_hash,seed,metrics,artifact_path,git_sha)
               VALUES (%s,%s,%s,daterange(%s,%s,'[]'),%s,%s,%s,%s::jsonb,%s,%s)
               ON CONFLICT (model_id) DO UPDATE SET
                 metrics=EXCLUDED.metrics, artifact_path=EXCLUDED.artifact_path,
                 git_sha=EXCLUDED.git_sha, created_at=now()""",
            (model_id, family, horizon, lo, hi, asof_snapshot, feats_hash, seed,
             json.dumps(metrics or {}), artifact_path, sha or git_sha()))


def latest(family, horizon, asof_snapshot):
    """查 ≤as_of 之最新同 family/horizon 模型(predict/resume 載入);無則 None。回 dict。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            """SELECT model_id, artifact_path, feats_hash, metrics::text, git_sha
               FROM model_registry
               WHERE family=%s AND horizon=%s AND asof_snapshot<=%s
               ORDER BY asof_snapshot DESC, created_at DESC LIMIT 1""",
            (family, horizon, asof_snapshot))
        r = cur.fetchone()
        return None if not r else {"model_id": r[0], "artifact_path": r[1],
                                   "feats_hash": r[2], "metrics": r[3], "git_sha": r[4]}


def exists(model_id):
    """model_id 是否已登錄(resume 跳過已訓)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT 1 FROM model_registry WHERE model_id=%s", (model_id,))
        return cur.fetchone() is not None
