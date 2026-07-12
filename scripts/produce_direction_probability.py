#!/usr/bin/env python
"""方向三產物生產器(憲章 v1.45.0 輸出契約之 O1;fail-closed:無 evaluated_pass 門=零列)。

🎯 這支在做什麼(白話):對每個 `evaluated_pass` 的擂台方向門,呈現「**gate 所驗證的 artifact 本身**」
   ——該凍結候選在 direction_arena_prediction 的最新 live 預測(F1 修正:不重訓、不換模型)——寫入
   direction_probability(H 軌)/daily_direction_probability(D 軌),附三產物:p_up、hit_rate(=gate
   result 之 horizon 級命中率,非單股)、expected_ret(E[r]ᵢ=(2·hit−1)×該股已實現波幅−成本;波幅估計量
   =近 250 交易日 |H-td 前瞻報酬| 中位數;成本=direction_product_config.cost_roundtrip,#29b 住 DB)。
   econ_verdict 唯讀自 direction_econ_verdict(無列=fail-closed 拒產,H3 修正);market 候選(無
   registry model_id)不寫本表、唯以擂台 ledger 原样呈現(F2 路由,呈現層另接)。
   DB trigger(migrate_direction_product_gate_ddl)機械擋非 pass 門——本支之 fail-closed 是第二層。

守 #6(冪等)· #9(hit/vol/cost 全可溯源)· 憲章輸出契約(閉式假設揭露硬綁由呈現層帶)。

執行指令矩陣:
  python scripts/produce_direction_probability.py            # 現況:pass 門數/產物列數(唯讀)
  python scripts/produce_direction_probability.py --run      # 生產(無 pass 門=誠實 0 列)
  python scripts/produce_direction_probability.py --check    # 機械斷言:無 pass 門時產物表必為 0 列
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

CONFIG_DDL = """
CREATE TABLE IF NOT EXISTS direction_product_config (
  key text PRIMARY KEY, value double precision NOT NULL, note text);
INSERT INTO direction_product_config VALUES
  ('cost_roundtrip', 0.00585, '台股來回成本(手續費×2×0.6折+證交稅;源=run_direction_econ_eval COST_TW,#29b 落 DB)')
ON CONFLICT (key) DO NOTHING;
CREATE TABLE IF NOT EXISTS direction_econ_verdict (
  gate_id text PRIMARY KEY REFERENCES direction_gate(gate_id),
  verdict text NOT NULL CHECK (verdict IN ('alive','thin_unestablished','dead')),
  decided_at timestamptz NOT NULL DEFAULT now(),
  source text NOT NULL);
"""

VOL_SQL = """
WITH r AS (
  SELECT stock_id, abs(close / NULLIF(lag(close, %s) OVER (PARTITION BY stock_id ORDER BY date), 0) - 1) AS aret
  FROM "TaiwanStockPriceAdj" WHERE stock_id = ANY(%s) AND date >= (SELECT max(date) - 400 FROM "TaiwanStockPriceAdj")
)
SELECT stock_id, percentile_cont(0.5) WITHIN GROUP (ORDER BY aret) FROM r WHERE aret IS NOT NULL GROUP BY stock_id
"""


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(CONFIG_DDL)
        cur.execute("SELECT gate_id FROM direction_gate WHERE status='evaluated_pass'")
        passes = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT count(*) FROM direction_probability")
        n_h = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM daily_direction_probability")
        n_d = cur.fetchone()[0]
        print(f"evaluated_pass 門:{len(passes)} | 產物列:H={n_h} D={n_d}")
        if args.check:
            ok = passes or (n_h == 0 and n_d == 0)
            print("✓ fail-closed 成立:無 pass 門、產物表零列" if ok and not passes else
                  ("✓ 有 pass 門(產物依門)" if ok else "✗ 違憲:無 pass 門卻有產物列"))
            return 0 if ok else 1
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        if not passes:
            print("誠實拒產:無任何 evaluated_pass 門 → 0 列(憲章輸出契約 fail-closed;非錯誤)")
            return 0
        cur.execute("SELECT value FROM direction_product_config WHERE key='cost_roundtrip'")
        cost = float(cur.fetchone()[0])
        produced = 0
        for gid in passes:
            # gate→候選(dgate_arena_<model_key>_<h>)→凍結候選之 live ledger(gate 驗證的 artifact 本身)
            cur.execute("SELECT criteria->>'model_key', criteria->>'key_col', result->>'hit_rate' "
                        "FROM direction_gate WHERE gate_id=%s", (gid,))
            mk, key_col, hit_s = cur.fetchone()
            if not mk or hit_s is None:
                print(f"  {gid}: criteria 缺 model_key/result 缺 hit_rate → 拒產(fail-closed)")
                continue
            cur.execute("SELECT verdict FROM direction_econ_verdict WHERE gate_id=%s", (gid,))
            ev = cur.fetchone()
            if not ev:
                print(f"  {gid}: 無 econ_verdict 列 → 拒產(H3 fail-closed:經濟裁決先落 direction_econ_verdict)")
                continue
            cur.execute("SELECT registry_model_id FROM direction_arena_candidate WHERE model_key=%s", (mk,))
            r = cur.fetchone()
            if not r or not r[0]:
                print(f"  {gid}: market 候選(無 registry model_id)→ 不入產物表、唯擂台 ledger 呈現(F2 路由)")
                continue
            model_id, hit = r[0], float(hit_s)
            cur.execute("SELECT DISTINCT ON (target_id) target_id, pred_date, p_up, horizon_td "
                        "FROM direction_arena_prediction WHERE model_key=%s ORDER BY target_id, pred_date DESC", (mk,))
            preds = cur.fetchall()
            ids = [p[0] for p in preds]
            h_td = preds[0][3] if preds else 20
            cur.execute(VOL_SQL, (h_td, ids))
            vol = dict(cur.fetchall())
            for tid, pdate, p_up, htd in preds:
                v = vol.get(tid)
                er = (2 * hit - 1) * float(v) - cost if v is not None else None
                cur.execute(
                    "INSERT INTO direction_probability (panel_date, model_id, target_id, horizon, p_up, base_rate, "
                    "calendar_days, calibrator_id, econ_verdict, gate_id, expected_ret, hit_rate) "
                    "VALUES (%s,%s,%s,%s,%s,0.5,%s,'arena_live',%s,%s,%s,%s) "
                    "ON CONFLICT DO NOTHING",
                    (pdate, model_id, tid, htd, p_up, htd, ev[0], gid, er, hit))
                produced += cur.rowcount
        print(f"✓ 產 {produced} 列(gate 驗證之 artifact 原樣;E[r] 閉式假設揭露由呈現層硬綁)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
