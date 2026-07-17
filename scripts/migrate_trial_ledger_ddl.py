#!/usr/bin/env python
"""試驗帳本 schema 遷移 + 回填 — trial_ledger 一表冪等落地(deflation 閘、SOP 債 d)。

🎯 這支在做什麼(白話):建立「試驗帳本」——把 augur 跑過的**每一個 backtest 試驗**(model×horizon×
   權重口徑×特徵集×成本×樣本期)逐列記錄下來,供 DSR/deflated Sharpe **機械計數試驗數 N**——
   `N = count DISTINCT (model, top_frac, weight, feats_hash, cost, horizon)`(SOP-strict 鍵),
   另備 `sample_since` 欄使「含樣本期變化的完整試驗數」亦可查。
   **N 一律由此表 query 得出、禁人手填報**(sop_master §6 decision-G7:手報 N 系統性低估真試驗數 →
   deflation 少扣血 = 敵③自欺向量、blocker 級);12 僅為 headline 選型下界,真 N 隨 ladder/多 seed/backtest 增長。

   **回填**:從 `revalidation_ledger` 之 net_sharpe 列機械抽取真實試驗(#15 N/SR 全 trace、不編),
   非新跑 backtest(純本地、零 API、不放量)。冪等:同 (model,horizon,weight,feats_hash,cost,sample_since)
   之回填以 ON CONFLICT 更新最新 net_sharpe,重跑零副作用。**唯記錄面**:不進預測管線(隔離不變式外)。

守 #6(冪等重跑安全)· #12(DDL 單一住所、SR 由既有 revalidation_ledger 抽、不重造)· #14(經濟價值口徑)·
   #15(N/SR 全 trace 真實試驗、不編不估;手報 N 屬未驗證)· CLAUDE #29a(個別可執行 + 指令矩陣 + 冪等 + bootstrap)·
   SSOT=reports/augur_prediction_sop_master_20260706.md §6 decision-G7 · reports/augur_prediction_model_improvement_plan_20260707.md 階段 0-A。

執行指令矩陣:
  python scripts/migrate_trial_ledger_ddl.py             # 冪等執行 DDL + 回填 + 印驗證清單(安全預設)
  python scripts/migrate_trial_ledger_ddl.py --check     # 唯讀:只印驗證清單與現況 N、不執行 DDL/回填
  python scripts/migrate_trial_ledger_ddl.py --no-backfill # 只建表、不回填(空表)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# 34-feat canonical set 之穩定識別(STAGE B 交集特徵集;非逐特徵 hash,以口徑標籤釘)——
# 同一特徵集之所有 backtest 共用,使 SOP DISTINCT 鍵之 feats_hash 維度可計數。
CANONICAL_FEATS_HASH = "canonical34_stageB_20260706"

DDL = [
    ("table trial_ledger", """
        CREATE TABLE IF NOT EXISTS trial_ledger (
          trial_id      bigserial PRIMARY KEY,
          run_at        timestamptz NOT NULL DEFAULT now(),
          model         text NOT NULL,                    -- ridge / gbdt / ...
          horizon       int  NOT NULL,                    -- 60 / 120 / ...
          top_frac      double precision NOT NULL,        -- 0.1 = top10%
          weight        text NOT NULL,                    -- LO / LS / LS+borrow2%
          feats_hash    text NOT NULL,                    -- 特徵集口徑識別(canonical34_...)
          cost          double precision NOT NULL,        -- 來回成本(0.00585 = 0.585%)
          sample_since  text NOT NULL,                    -- 樣本期起點(since2014 / since2021)
          metric_name   text NOT NULL DEFAULT 'net_sharpe',
          metric_value  double precision,                 -- 該試驗之 headline 指標(net_sharpe)
          n_periods     int,                              -- 該試驗有效期數(T,DSR 需)
          seed          int,                              -- single-seed 揭露(NULL=確定性/多seed中位)
          source        text NOT NULL DEFAULT 'revalidation_ledger',  -- 回填來源(#15 trace)
          note          text,
          CONSTRAINT trial_ledger_uq UNIQUE (model, horizon, top_frac, weight, feats_hash, cost, sample_since)
        )"""),
    ("index ix_trial_sopkey", """
        CREATE INDEX IF NOT EXISTS ix_trial_sopkey
          ON trial_ledger (model, top_frac, weight, feats_hash, cost, horizon)"""),
    ("comment trial_ledger", """
        COMMENT ON TABLE trial_ledger IS
        'deflation 試驗帳本(SOP 債 d/§6 G7);每 backtest 試驗逐列;DSR 之試驗數 N = count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon) 一律由此表 query 機械得出、禁人手填;唯記錄面、不進預測管線'"""),
    ("comment col sample_since", """
        COMMENT ON COLUMN trial_ledger.sample_since IS
        '樣本期起點;SOP-strict N 鍵不含此欄(12 選型下界口徑),但含此欄之完整試驗數為誠實上界(每樣本期=獨立 backtest、獨立多重比較曝險);deflation 一律取較保守(較大)N'"""),
    ("comment col metric_value", """
        COMMENT ON COLUMN trial_ledger.metric_value IS
        '該試驗 headline 指標(預設 net_sharpe);Var(SR_trials) 由本欄跨全部試驗 cell 算,供 DSR 之 SR_0 期望最大 Sharpe(#15 SR 分布 trace 真實試驗)'"""),
]

# 回填:從 revalidation_ledger 之 net_sharpe 列抽真實試驗(config='<weight>|<since>')。
BACKFILL = f"""
    INSERT INTO trial_ledger
      (model, horizon, top_frac, weight, feats_hash, cost, sample_since,
       metric_name, metric_value, n_periods, source, note)
    SELECT
      model,
      horizon,
      0.1                          AS top_frac,
      split_part(config, '|', 1)   AS weight,
      '{CANONICAL_FEATS_HASH}'     AS feats_hash,
      0.00585                      AS cost,
      split_part(config, '|', 2)   AS sample_since,
      'net_sharpe'                 AS metric_name,
      metric_value,
      n_periods,
      'revalidation_ledger'        AS source,
      'backfill from revalidation_ledger stage=' || stage AS note
    FROM revalidation_ledger
    WHERE metric_name = 'net_sharpe'
    ON CONFLICT (model, horizon, top_frac, weight, feats_hash, cost, sample_since, recipe)
    DO UPDATE SET metric_value = EXCLUDED.metric_value,
                  n_periods    = EXCLUDED.n_periods,
                  run_at       = now(),
                  note         = EXCLUDED.note
"""

VERIFY = [
    ("trial_ledger 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='trial_ledger'"),
    ("UNIQUE 約束", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='trial_ledger_uq'"),
    ("索引", "SELECT string_agg(indexname,', ' ORDER BY indexname) FROM pg_indexes WHERE tablename='trial_ledger'"),
    ("表 COMMENT", "SELECT obj_description('trial_ledger'::regclass)"),
    ("現有列數", "SELECT count(*) FROM trial_ledger"),
    ("N (SOP-strict 鍵: model,top_frac,weight,feats_hash,cost,horizon)",
     "SELECT count(*) FROM (SELECT DISTINCT model, top_frac, weight, feats_hash, cost, horizon FROM trial_ledger) t"),
    ("N (含 sample_since 之完整試驗數 = 誠實上界)",
     "SELECT count(*) FROM (SELECT DISTINCT model, top_frac, weight, feats_hash, cost, horizon, sample_since FROM trial_ledger) t"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001  表未建時 count/comment 會失敗 → 誠實印,不中斷
            print(f"  {label}: (查詢失敗:{e})")


def main(argv=None):
    ap = argparse.ArgumentParser(description="試驗帳本 DDL 遷移 + 回填(trial_ledger;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL/回填")
    ap.add_argument("--no-backfill", action="store_true", help="只建表、不回填")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
            if not args.no_backfill:
                cur.execute(BACKFILL)
                print(f"✓ backfill from revalidation_ledger (rowcount={cur.rowcount})")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
