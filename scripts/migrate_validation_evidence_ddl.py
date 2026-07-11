#!/usr/bin/env python
"""驗證證據帳本 DDL — validation_evidence 建表+種子(驗證總綱 V0;缺口①機械層)。

🎯 這支在做什麼(白話):把「憑什麼相信預測鏈每一環」從散落的報告/commit 變成**可機械重驗的帳本**——
   每列=一條策展斷言+重驗方式(sql 自動/script_exit 白名單/manual 人審)。green=斷言此刻對 DB 為真
   (非方法論背書);**已知債(E5 survivorship/gm 斷點/macro 潛伏)以 red/amber 誠實入帳、無處可藏**。
   種子=總綱 §1.1 E1-E10 矩陣之一次性 bootstrap(#29b:此後 SSOT=DB,增列=INSERT 零改碼);
   解凍 GATE(V2)之 --strict 前置消費此表。

守 #29b(策展斷言住 DB)· #10(source_ref 溯源)· #15(紅列誠實)· #6(冪等)· #29a。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §1/§3.1。

執行指令矩陣:
  python scripts/migrate_validation_evidence_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_validation_evidence_ddl.py --run     # 冪等建表+種子(ON CONFLICT DO NOTHING)
  python scripts/migrate_validation_evidence_ddl.py --verify  # 驗收:10 chain_link 各≥1、總數≥18(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS validation_evidence (
  evidence_id      text PRIMARY KEY,
  chain_link       text NOT NULL CHECK (chain_link IN
                     ('raw','feature','promotion','gate','train','oos',
                      'calibration','probability','economic','harness')),
  claim            text NOT NULL,
  check_type       text NOT NULL DEFAULT 'sql'
                     CHECK (check_type IN ('sql','script_exit','manual')),
  check_sql        text,
  check_cmd        text,
  source_ref       text NOT NULL,
  status           text NOT NULL DEFAULT 'unverified'
                     CHECK (status IN ('green','amber','red','unverified')),
  status_note      text,
  last_verified_at timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT chk_ve_sql_presence CHECK (check_type <> 'sql' OR check_sql IS NOT NULL),
  CONSTRAINT chk_ve_cmd_presence CHECK (check_type <> 'script_exit' OR check_cmd IS NOT NULL)
);
COMMENT ON TABLE validation_evidence IS
  '驗證證據帳本(缺口①機械層):策展斷言+重驗方式;green=斷言此刻對 DB 為真,非方法論背書;已知債紅列誠實入帳;解凍 GATE 之 --strict 前置消費此表';
"""

# (evidence_id, chain_link, claim, check_type, check_sql, check_cmd, source_ref, status, status_note)
SEEDS = [
    ("E1_raw_reconcile_exit", "raw", "raw 對帳工具(byte 對帳+敵①attestation)exit 0", "script_exit", None,
     "venv/bin/python scripts/reconcile_audit.py",
     "augur_prediction_sop_master_20260706.md §PHASE5", "unverified",
     "stdout+exit-code 工具、無落帳表(誠實標示);--with-scripts 才執行"),
    ("E2_feature_frozen_panel", "feature", "feature_values FREEZE 面板=2,418,655 列/35 特徵/35 panel(兩輪 #8 審計修復後)", "sql",
     "SELECT count(*)=2418655 AND count(DISTINCT feature)=35 AND count(DISTINCT panel_date)=35 FROM feature_values",
     None, "augur_antileakage_audit_20260711.md;commit cd8b35e/abf5da8", "unverified", None),
    ("E2_macro_latent_debt", "feature", "macro 潛伏債:Tier A realtime_start 為碼構造非實測(重 sync 屬解凍後);消費端由 macro_vintage.py 介面強制濾版", "manual",
     None, None, "augur_antileakage_audit_20260711.md §4;src/augur/features/macro_vintage.py", "amber",
     "reader 已封門(零現行消費者);Tier A 重 sync=解凍後動作——债未清、僅緩解"),
    ("E3_promotion_funnel", "promotion", "特徵提拔走四道漏斗+HAC Eff-t+經濟終關(IC 顯著性禁裸 iid)", "manual",
     None, None, "augur_feature_discovery_methodology_20260626.md §四;augur_prediction_stageB_promotion_verdict_20260706.md",
     "green", "人審 2026-07-11:依既有方法論 SSOT+B 提拔裁決報告"),
    ("E4_canonical_intersection_28", "gate", "canonical 特徵=全 panel 交集 gate 之 28 特徵", "sql",
     "SELECT count(*)=28 FROM (SELECT feature FROM feature_values GROUP BY feature "
     "HAVING count(DISTINCT panel_date)=(SELECT count(DISTINCT panel_date) FROM feature_values)) t",
     None, "src/augur/evaluation/baseline.py:30 canonical_features", "unverified", None),
    ("E4_gm_promotion_gap", "gate", "gross_margin_pctile 提拔過四道漏斗卻被交集 gate 靜默排除——提拔↔canonical 銜接無契約", "manual",
     None, None, "augur_prediction_validation_master_plan_20260711.md §2.3(V1 斷點調查)", "red",
     "已知債:V1 調查產裁決建議(a)/(b)/(c) 供人拍板;紅列直到裁決"),
    ("E5_models_frozen_four", "train", "4 生產模型 RankRidge H20/40/60/120(as-of 2026-05-31,seed42)在 registry", "sql",
     "SELECT count(*)=4 FROM model_registry WHERE model_id LIKE 'RankRidge_H%_2026-05-31_seed42_%'",
     None, "model_registry;2026-07-11 乾淨重訓同值實證", "unverified", None),
    ("E5_survivorship_debt", "train", "core_universe_asof 實為當前存活名單→as-of IC 帶樂觀偏誤(survivorship 債 b)", "manual",
     None, None, "augur_prediction_survivorship_economic_verdict_20260708.md;train_ranker._train_note", "red",
     "已知債:量級已估、經濟裁決含此 caveat;解凍後以真 PIT 名單重估"),
    ("E6_oos_frozen_rowcount", "oos", "OOS 樣本 FREEZE 快照恰 42,456 列且 exit_date 零 NULL", "sql",
     "SELECT count(*)=42456 AND bool_and(exit_date IS NOT NULL) FROM probability_oos_sample",
     None, "augur_omniscient_e2e_master_plan_20260710.md §6.2", "unverified",
     "凍結計數型:解凍重建時隨 GATE 流程更新、非假警報"),
    ("E6_purge_assertion", "oos", "OOS purge 機械斷言(exit_date=panel+h 交易日、embargo 下界)全綠", "script_exit", None,
     "venv/bin/python scripts/build_probability_oos_sample.py --verify",
     "scripts/build_probability_oos_sample.py", "unverified", None),
    ("E7_calibrator_purge_brier", "calibration", "每 horizon 最新校準器 purge_verified 且 Brier<基線(語意型,合法再 fit 不翻紅)", "sql",
     "SELECT bool_and(purge_verified AND brier < brier_baseline) FROM ("
     "SELECT DISTINCT ON (horizon) purge_verified, brier, brier_baseline "
     "FROM probability_calibrator ORDER BY horizon, created_at DESC) t",
     None, "probability_calibrator;e2e §6.3", "unverified", None),
    ("E7_h60_ece_outlier", "calibration", "H60 ECE 0.0157 為四 horizon 最高(其餘 ~0.008)——待 V1 子期間分解判讀", "manual",
     None, None, "augur_prediction_validation_master_plan_20260711.md §2.1", "amber",
     "非紅(仍過 Brier 基線);V1 判讀前不背書"),
    ("E8_probability_frozen", "probability", "prediction_probability FREEZE 快照 1,376 列/4 horizon、p∈(0,1)", "sql",
     "SELECT count(*)=1376 AND count(DISTINCT horizon)=4 AND bool_and(p_beat_median>0 AND p_beat_median<1) "
     "FROM prediction_probability", None, "commit 7fd3426(誠實 UI);憲章 v1.40.0 口徑", "unverified", None),
    ("E8_econ_verdict_bound", "probability", "機率列 econ_verdict 與 econ_verdict_rule 逐 horizon 一致(判死標籤硬綁不漂)", "sql",
     "SELECT bool_and(p.econ_verdict=r.verdict) FROM prediction_probability p JOIN econ_verdict_rule r USING(horizon)",
     None, "econ_verdict_rule(3遷 #29b);commit abf5da8", "unverified", None),
    ("E9_econ_rule_sourced", "economic", "econ_verdict_rule 5 列全帶 source_report 溯源(dead/thin 誠實判死)", "sql",
     "SELECT count(*)=5 AND bool_and(source_report IS NOT NULL) FROM econ_verdict_rule",
     None, "short_horizon/tier3/H120 裁決報告(20260706-09)", "unverified", None),
    ("E9_judgestop_frozen", "economic", "判停閾 6 列且凍結列 ≥4(凍結尊重人留痕、種子不覆寫)", "sql",
     "SELECT count(*)=6 AND count(*) FILTER (WHERE frozen) >= 4 FROM judgestop_threshold",
     None, "scripts/migrate_judgestop_ddl.py;trial_ledger 32 列", "unverified", None),
    ("E10_revalidation_harness", "harness", "再驗證 harness 帳本就位(ledger≥204/baseline≥4;可增長語意型)", "sql",
     "SELECT (SELECT count(*) FROM revalidation_ledger)>=204 AND (SELECT count(*) FROM revalidation_baseline)>=4",
     None, "augur_prediction_revalidation_harness_plan_20260708.md", "unverified", None),
    ("E10_daily_green", "harness", "daily_green 四段(smoke/regression/shadow/delib-watch)exit 0", "script_exit", None,
     "venv/bin/python scripts/daily_green.py", "scripts/daily_green.py", "unverified",
     "重段(~90s);--with-scripts 才執行"),
]


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(DDL)
        n = 0
        for row in SEEDS:
            cur.execute(
                "INSERT INTO validation_evidence (evidence_id, chain_link, claim, check_type, check_sql, "
                "check_cmd, source_ref, status, status_note) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (evidence_id) DO NOTHING", row)
            n += cur.rowcount
        conn.commit()
    print(f"✓ --run 完成(冪等):表就位、種子新增 {n}/{len(SEEDS)}")
    return 0


def verify():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT chain_link) FROM validation_evidence")
        n, links = cur.fetchone()
        ok = n >= 18 and links == 10
        print(f"{'✓' if ok else '✗'} 驗收:總數 {n}(≥18)、chain_link {links}/10")
        cur.execute("SELECT chain_link, count(*) FROM validation_evidence GROUP BY 1 ORDER BY 1")
        for r in cur.fetchall():
            print(f"   {r[0]:<12} {r[1]}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.run:
        return run()
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.validation_evidence')")
        if cur.fetchone()[0]:
            cur.execute("SELECT status, count(*) FROM validation_evidence GROUP BY 1")
            print("現況:", dict(cur.fetchall()))
        else:
            print("現況:(表未建,先 --run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
