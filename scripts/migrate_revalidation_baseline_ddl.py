#!/usr/bin/env python
"""再驗證 baseline 錨 schema 遷移 — revalidation_baseline 一表冪等落地(harness P0 兩宇宙定錨)。

🎯 這支在做什麼(白話):凍結「edge 建置時之 deflated 地板」作為軌B 衰減判停之比較基準——
   逐 (cell, universe) 記 net_sharpe / bench / 超額 / HAC-t / DSR / deflated 有效 Sharpe。
   **兩宇宙並存(用戶拍板)**:universe='asof_incumbent'(全史齊、predict_asof 實際部署交易口徑=操作 baseline)
   + universe='pit_broad'(廣宇宙、incumbency 修正後之誠實地板錨)。軌B 以部署宇宙 baseline 比較衰減、
   廣宇宙錨供揭露(incumbency −16.5% 不惡化)。

   **唯記錄面 + 凍結語義**:baseline 一旦定錨即為軌B 之固定參照(edge 是否從此惡化);非每輪覆寫(#15:
   要偵測「相對建置基線衰減」須有固定錨、非浮動)。重新定錨=明示 re-freeze(換部署模型/宇宙判準時)。
   不進預測管線(隔離不變式外)。

守 #6(冪等)· #12(DDL 單一住所)· #14(經濟價值)· #15(凍結錨=衰減偵測前提、兩宇宙誠實)· #29a ·
   SSOT=reports/augur_prediction_revalidation_harness_plan_20260708.md P0/§3.5。

執行指令矩陣:
  python scripts/migrate_revalidation_baseline_ddl.py          # 冪等執行 DDL + 印驗證清單
  python scripts/migrate_revalidation_baseline_ddl.py --check  # 唯讀:只印驗證清單
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = [
    ("table revalidation_baseline", """
        CREATE TABLE IF NOT EXISTS revalidation_baseline (
          cell          text NOT NULL,                -- 部署 cell 識別(如 'ridge_H60_LO')
          universe      text NOT NULL,                -- 'asof_incumbent'(全史齊部署)| 'pit_broad'(廣宇宙誠實錨)
          frozen_at     timestamptz NOT NULL DEFAULT now(),
          as_of_date    date NOT NULL,                -- 定錨時之 as-of 上界
          net_sharpe    double precision,             -- 年化淨 Sharpe
          bench_sharpe  double precision,
          net_excess    double precision,             -- net − bench(超額 = 軌B 衰減主指標)
          hac_t         double precision,             -- STAGE B as-of IC HAC-t(可 NULL)
          dsr           double precision,             -- deflated Sharpe ratio(per-period、保守 N;軌A 標註用)
          deflated_ann  double precision,             -- deflated 年化有效 Sharpe(haircut×√ppy)
          n_periods     int,
          source_ref    text NOT NULL,                -- 出處(deflation/survivorship verdict 報告)
          note          text,
          PRIMARY KEY (cell, universe),
          CONSTRAINT chk_baseline_universe CHECK (universe IN ('asof_incumbent','pit_broad'))
        )"""),
    ("comment revalidation_baseline", """
        COMMENT ON TABLE revalidation_baseline IS
        '再驗證軌B 之凍結基線錨(harness P0);逐 (cell,universe) 凍結建置時 deflated 地板;兩宇宙並存(asof_incumbent 部署/pit_broad 誠實);軌B 以此固定錨偵測相對衰減;唯記錄面、不進預測管線'"""),
    ("comment col net_excess", """
        COMMENT ON COLUMN revalidation_baseline.net_excess IS
        'net−bench 超額 alpha=軌B 衰減主指標(從曾正轉負=經濟價值消失=判停);DSR 屬軌A 標註不入判停(現況<95%是薄edge常態)'"""),
]

VERIFY = [
    ("revalidation_baseline 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='revalidation_baseline'"),
    ("主鍵", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='revalidation_baseline_pkey'"),
    ("universe CHECK", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='chk_baseline_universe'"),
    ("現有列數", "SELECT count(*) FROM revalidation_baseline"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001
            print(f"  {label}: (查詢失敗:{e})")


def main(argv=None):
    ap = argparse.ArgumentParser(description="再驗證 baseline 錨 DDL(revalidation_baseline;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
