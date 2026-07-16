#!/usr/bin/env python
"""模型分數復現驗證 — 凍結 artifact 重打分決定性至 5 位小數(arena 前置 G2;計畫 §6.5 校正版)。

🎯 這支在做什麼(白話):990ddea 判準「4 模型分數復現至 5 位小數」之機械化——載入 4 支凍結 artifact
   (model_ids **讀自 990ddea 凍結原文 scope.model_ids**=ce62866 家族、零 hardcode #12),對全部
   ≤FREEZE(2026-05-31) feature panel 重打分(同 predict 管線:baseline._asof_stocks+_panel_matrix
   +artifact.feats 凍結欄序),score round 至 5 位 → 逐 (model,panel) hash 凍 baseline(表
   score_repro_baseline,本檔 DDL 單一住所)。之後任何時點 --verify 重載重打分,**hash 變=artifact
   被改/環境漂移(sklearn 數值變)/管線不決定性 → FAIL**。
   校正(2026-07-16 實證):probability_oos_sample.score=walk-forward 逐折現場 refit 之產物,**非**
   此 4 artifact 輸出——OOS 分數不是本工具的比對對象(比了=假 mismatch);本工具鎖的是 artifact 決定性。
   零 API、純本地(#28)。

守 #15(hash=機械證據)· #12(model_ids/panel 集皆讀 DB 凍結原文,不複製常數)· #8(凍結段)· #29a/d。
   SSOT=reports/arena_g1g5_admission_gate_plan_20260716.md §6.5。

執行指令矩陣:
  python scripts/verify_score_repro.py             # 無參數:現況(唯讀)
  python scripts/verify_score_repro.py --init      # 冪等建 score_repro_baseline 表
  python scripts/verify_score_repro.py --freeze    # 4 artifact × ≤FREEZE panel 重打分凍 baseline(~數分)
  python scripts/verify_score_repro.py --verify    # 重載重打分 hash 比對(0 mismatch=exit 0)
  python scripts/verify_score_repro.py --selftest  # 純函式紅綠(零 DB 零 API)
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

SOURCE_GATE = "unfreeze_06dcb178267d"   # model_ids/FREEZE SSOT=其凍結 criteria(trigger 鎖)
DECIMALS = 5                            # 990ddea g2_repro.score_repro_decimals

DDL = """
CREATE TABLE IF NOT EXISTS score_repro_baseline (
  model_id    text NOT NULL,
  panel_date  date NOT NULL,
  row_count   bigint NOT NULL,
  score_hash  text NOT NULL,
  decimals    int  NOT NULL,
  frozen_at   timestamptz NOT NULL DEFAULT now(),
  git_sha     text,
  PRIMARY KEY (model_id, panel_date)
);
COMMENT ON TABLE score_repro_baseline IS
  'G2 score 復現鎖:凍結 artifact 對 ≤FREEZE panel 重打分 round5 之 hash;verify hash 變=artifact 被改/環境漂移 FAIL';
"""


def _git7():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parent.parent)).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _score_hash(pairs, decimals=DECIMALS):
    """[(stock_id, raw_score)…] → 排序後 'sid|round5' 行流 sha256。純函式(selftest 可測)。"""
    h = hashlib.sha256()
    for sid, sc in sorted(pairs, key=lambda p: str(p[0])):
        h.update(f"{sid}|{round(float(sc), decimals)}\n".encode())
    return h.hexdigest()


def _spec(cur):
    """自 990ddea 凍結原文讀 model_ids+FREEZE(零 hardcode;trigger 鎖=讀現值即原文)。"""
    cur.execute("SELECT criteria->'scope' FROM prediction_unfreeze_gate WHERE gate_id=%s", (SOURCE_GATE,))
    row = cur.fetchone()
    if not row:
        sys.exit(f"✗ 來源 gate {SOURCE_GATE} 不存在(model_ids SSOT 斷)")
    scope = row[0]
    return scope["model_ids"], scope["freeze_asof"]


def _rescore_all(conn):
    """4 artifact × ≤FREEZE panel 重打分 → yield (model_id, panel_date, n, hash)。同 predict 管線。"""
    from augur.evaluation import baseline
    from augur.models import artifact as artifact_mod
    with db.transaction(conn) as cur:
        model_ids, freeze = _spec(cur)
        cur.execute("SELECT model_id, artifact_path FROM model_registry WHERE model_id = ANY(%s)", (model_ids,))
        paths = dict(cur.fetchall())
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date <= %s ORDER BY 1", (freeze,))
        panels = [r[0] for r in cur.fetchall()]
    missing = [m for m in model_ids if not paths.get(m) or not Path(paths[m]).exists()]
    if missing:
        sys.exit(f"✗ artifact 檔缺:{missing}")
    for mid in sorted(model_ids):
        art = artifact_mod.load(paths[mid])
        est, feats = art["estimator"], art["feats"]
        for pd_ in panels:
            sids = baseline._asof_stocks(conn, pd_)
            sids, X = baseline._panel_matrix(conn, pd_, sids, feats)
            if len(sids) == 0:
                continue
            scores = est.predict(X)
            yield mid, pd_, len(sids), _score_hash(zip(sids, scores))
        print(f"  {mid}:{len(panels)} panel 打分完", flush=True)


def init():
    with db.connect() as conn:
        conn.cursor().execute(DDL)
        conn.commit()
    print("✓ --init 完成(冪等):score_repro_baseline 就位")
    return 0


def freeze():
    git = _git7()
    n = 0
    with db.connect() as conn:
        cur = conn.cursor()
        for mid, pd_, rc, hsh in _rescore_all(conn):
            cur.execute("INSERT INTO score_repro_baseline (model_id,panel_date,row_count,score_hash,decimals,git_sha) "
                        "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (model_id,panel_date) DO NOTHING",
                        (mid, pd_, rc, hsh, DECIMALS, git))
            n += cur.rowcount
        conn.commit()
    print(f"✓ freeze:新凍 {n} (model,panel) baseline(既有跳過;重凍=先人工 DELETE 留痕)")
    return 0


def verify():
    mism, seen = [], set()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT model_id, panel_date, row_count, score_hash FROM score_repro_baseline")
            base = {(r[0], r[1]): (r[2], r[3]) for r in cur.fetchall()}
        if not base:
            print("✗ verify:無 baseline(先 --freeze)")
            return 1
        for mid, pd_, rc, hsh in _rescore_all(conn):
            k = (mid, pd_)
            seen.add(k)
            if k in base and (rc, hsh) != base[k]:
                mism.append(k)
    missing = sorted(set(base) - seen)
    ok = not mism and not missing
    print(f"{'✓ PASS(4 artifact 重打分 100% 復現至 5 位)' if ok else '✗ FAIL'} "
          f"verify:baseline {len(base)}、比對 {len(seen & set(base))}")
    if mism:
        print(f"  ✗ score hash 不符 {len(mism)}(artifact 被改/環境漂移!):{[(m, str(p)) for m, p in mism[:6]]}")
    if missing:
        print(f"  ✗ baseline 組合重打不出 {len(missing)}:{[(m, str(p)) for m, p in missing[:6]]}")
    return 0 if ok else 1


def _selftest():
    """純函式紅綠(零 DB 零 API #29a)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    p = [("A", 1.234567891), ("B", -0.5)]
    chk("_score_hash 決定性", _score_hash(p) == _score_hash(list(p)))
    chk("_score_hash 順序無關", _score_hash(p) == _score_hash(p[::-1]))
    chk("_score_hash round5 等價(第6位差被吸收)", _score_hash(p) == _score_hash([("A", 1.2345689), ("B", -0.5)]))
    chk("_score_hash 第5位差→hash 變", _score_hash(p) != _score_hash([("A", 1.23458), ("B", -0.5)]))
    chk("_score_hash 增股→hash 變", _score_hash(p) != _score_hash(p + [("C", 0.0)]))
    chk("DDL 冪等+PK", "CREATE TABLE IF NOT EXISTS" in DDL and "PRIMARY KEY" in DDL)
    chk("DECIMALS=5(990ddea 判準)", DECIMALS == 5)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.init:
        return init()
    if args.freeze:
        return freeze()
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.score_repro_baseline')")
        if cur.fetchone()[0]:
            cur.execute("SELECT model_id, count(*), max(frozen_at)::date FROM score_repro_baseline GROUP BY model_id")
            rows = cur.fetchall()
            print("現況:", rows if rows else "(表在、零 baseline;先 --freeze)")
        else:
            print("現況:(表未建,先 --init)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
