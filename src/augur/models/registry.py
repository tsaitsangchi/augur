"""模型登錄 — model_registry 表 CRUD(#15 可重現 + resume 帳本;SOP §3)。

🎯 這支在做什麼(白話):每 fit 好一個模型,把身分證(family/horizon/train_span/as-of/feats_hash/
   seed/metrics/artifact_path/git_sha)寫進 model_registry;predict 時查「≤as-of 之最新同 family/
   horizon artifact」載回。resume:已訓折/模型可查、重跑冪等 upsert(#6)。
守 #15(git_sha/feats_hash 凍結可重現)· #6(resume 冪等)· 隔離不變式(非預測輸入表)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.models.registry              # 印用途+公開入口（唯讀）
  python -m augur.models.registry --selftest   # 純紅綠自測（零 IO）
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


def _selftest():
    """自測（零 DB/零 API：全公開函式皆 DB/subprocess，僅 import-smoke + 結構斷言，不呼任何函式 #3）。"""
    import inspect                              # 延遲 import（純標準庫、零 IO #3）
    import augur.models.registry as m          # import-smoke:模組可載入
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("公開入口皆存在(register/latest/exists/git_sha)",
        all(hasattr(m, n) for n in ("register", "latest", "exists", "git_sha")))
    chk("公開入口皆 callable",
        all(callable(getattr(m, n)) for n in ("register", "latest", "exists", "git_sha")))
    # register 簽名鎖:身分證欄位齊全(#15 可重現鍵不得漏)
    rp = list(inspect.signature(m.register).parameters)
    chk("register 簽名含 feats_hash/seed/asof_snapshot/git-sha 鍵",
        all(p in rp for p in ("family", "horizon", "train_span", "asof_snapshot",
                              "feats_hash", "seed", "metrics", "artifact_path")))
    chk("latest 簽名=(family,horizon,asof_snapshot)",
        list(inspect.signature(m.latest).parameters) == ["family", "horizon", "asof_snapshot"])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.registry --selftest;免 DB 免 API)")
