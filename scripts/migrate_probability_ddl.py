#!/usr/bin/env python
"""相對機率層 schema 遷移 — probability_oos_sample / probability_calibrator / prediction_probability 三表冪等落地(e2e 主計畫 P1)。

🎯 這支在做什麼(白話):建立「橫斷面相對機率」層的三張承載表——
   ① `probability_oos_sample`:walk-forward OOS 折的(分位,已實現相對標籤)對樣本,**exit_date 併落**
      =purge 校準之機械斷言依據(D3 拍板「落表」;#10 可溯源);
   ② `probability_calibrator`:校準器 provenance(方法/參數/Brier/ECE/可靠度分箱/同族聲明)——
      機率數字可 trace 回哪個校準器(憲章 v1.40.0「相對機率誠實判準」);
   ③ `prediction_probability`:P(勝過同儕中位數|as-of,H) 之 DB 承載,econ_verdict 判死標籤與機率
      同列硬綁(D2)、calibrator_id FK 溯源。**唯一合法口徑=橫斷面相對機率,禁絕對漲跌機率**。
   隔離:僅 advisor 唯讀;PIPELINE 7 pkg 零回讀、augur_predict role 不授 SELECT(A-28 預測輸出不自迴圈)。

守 #6(冪等)· #8(exit_date=purge 斷言依據)· #10(全欄可溯源)· #12(DDL 單一住所)· 憲章 v1.40.0 相對機率誠實判準 ·
   CLAUDE #29a。SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §5.2-5.4/§6.1。

執行指令矩陣:
  python scripts/migrate_probability_ddl.py            # 無參數:印本矩陣+三表現況(唯讀)
  python scripts/migrate_probability_ddl.py --run      # 冪等建三表
  python scripts/migrate_probability_ddl.py --verify   # 斷言三表+CHECK/FK 就位(exit 0/1)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

TABLES = ("probability_oos_sample", "probability_calibrator", "prediction_probability")

DDL = [
    ("table probability_oos_sample", """
        CREATE TABLE IF NOT EXISTS probability_oos_sample (
          horizon           int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),
          panel_date        date NOT NULL,
          model_family      text NOT NULL,
          stock_id          text NOT NULL,
          score             double precision NOT NULL,
          rank_pctile       double precision NOT NULL CHECK (rank_pctile BETWEEN 0 AND 1),
          fwd_ret           double precision NOT NULL,
          peer_median_ret   double precision NOT NULL,
          label_beat_median boolean NOT NULL,
          exit_date         date NOT NULL,
          git_sha           text NOT NULL,
          created_at        timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (horizon, panel_date, model_family, stock_id)
        )"""),
    ("index ix_prob_oos_h_exit", """
        CREATE INDEX IF NOT EXISTS ix_prob_oos_h_exit ON probability_oos_sample (horizon, exit_date)"""),
    ("comment probability_oos_sample", """
        COMMENT ON TABLE probability_oos_sample IS
        'walk-forward OOS 折之機率校準對樣本(D3 落表);rank_pctile 方向契約 1=最強與標籤同向;exit_date=標籤窗完全實現日=purge 機械斷言依據;fwd_ret/peer_median_ret 皆 FREEZE 內已實現(#8);82=D1(a) 條件觸發保留'"""),
    ("table probability_calibrator", """
        CREATE TABLE IF NOT EXISTS probability_calibrator (
          calibrator_id    text PRIMARY KEY,
          horizon          int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),
          method           text NOT NULL CHECK (method IN ('platt','isotonic')),
          fit_asof         date NOT NULL,
          n_fit_samples    int  NOT NULL,
          n_fit_folds      int  NOT NULL,
          purge_verified   boolean NOT NULL,
          params           jsonb NOT NULL,
          brier            double precision,
          brier_baseline   double precision,
          ece              double precision,
          reliability_bins jsonb,
          family_note      text NOT NULL,
          git_sha          text NOT NULL,
          created_at       timestamptz NOT NULL DEFAULT now()
        )"""),
    ("comment probability_calibrator", """
        COMMENT ON TABLE probability_calibrator IS
        '機率校準器 provenance(憲章 v1.40.0 相對機率誠實判準);purge_verified=機械斷言全 fit 樣本 exit_date<fit_asof;params 可重現(#15);family_note=同族近似聲明固定用語(A-36);brier_baseline=base-rate 常數對照、禁 iid 顯著性宣稱'"""),
    ("table prediction_probability", """
        CREATE TABLE IF NOT EXISTS prediction_probability (
          panel_date    date NOT NULL,
          model_id      text NOT NULL REFERENCES model_registry(model_id),
          stock_id      text NOT NULL,
          horizon       int  NOT NULL CHECK (horizon IN (20,40,60,82,120)),
          rank_pctile   double precision NOT NULL CHECK (rank_pctile BETWEEN 0 AND 1),
          p_beat_median double precision NOT NULL CHECK (p_beat_median > 0 AND p_beat_median < 1),
          calibrator_id text NOT NULL REFERENCES probability_calibrator(calibrator_id),
          econ_verdict  text NOT NULL CHECK (econ_verdict IN ('dead','thin_unestablished','established')),
          calendar_days int  NOT NULL,
          created_at    timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (panel_date, model_id, stock_id)
        )"""),
    ("index ix_pred_prob_panel_h", """
        CREATE INDEX IF NOT EXISTS ix_pred_prob_panel_h ON prediction_probability (panel_date, horizon)"""),
    ("comment prediction_probability", """
        COMMENT ON TABLE prediction_probability IS
        'P(勝過同儕中位數|as-of,H)——唯一合法口徑=橫斷面相對機率、禁絕對漲跌機率(憲章 v1.40.0);econ_verdict 與機率同列硬綁不可分離(D2);calendar_days=日曆日近似呈現偏差之推導 SSOT(A-27);僅 advisor 唯讀、PIPELINE 零回讀、augur_predict 不授 SELECT(A-28)'"""),
]


def _existing(cur):
    cur.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name = ANY(%s)", (list(TABLES),))
    return {r[0] for r in cur.fetchall()}


def status():
    with db.connect() as conn:
        cur = conn.cursor()
        have = _existing(cur)
        for t in TABLES:
            mark = "✓" if t in have else "✗ 未建"
            n = "-"
            if t in have:
                cur.execute(f"SELECT count(*) FROM {t}")
                n = cur.fetchone()[0]
            print(f"  {mark} {t}(rows={n})")
        return have


def run():
    with db.connect() as conn:
        cur = conn.cursor()
        for name, sql in DDL:
            cur.execute(sql)
            print(f"  ✓ {name}")
        conn.commit()
    print("✓ --run 完成(冪等)")


def verify() -> int:
    ok = True
    with db.connect() as conn:
        cur = conn.cursor()
        have = _existing(cur)
        for t in TABLES:
            if t not in have:
                print(f"✗ 缺表 {t}"); ok = False
        # CHECK/FK 斷言(constraint 存在性)
        cur.execute("""
            SELECT conrelid::regclass::text, contype, count(*)
            FROM pg_constraint
            WHERE conrelid::regclass::text = ANY(%s)
            GROUP BY 1,2 ORDER BY 1,2""", (list(TABLES),))
        cons = {(r[0], r[1]): r[2] for r in cur.fetchall()}
        expect = [  # (表, 約束型別, 最少數):c=CHECK p=PK f=FK
            ("probability_oos_sample", "c", 2), ("probability_oos_sample", "p", 1),
            ("probability_calibrator", "c", 2), ("probability_calibrator", "p", 1),
            ("prediction_probability", "c", 4), ("prediction_probability", "p", 1),
            ("prediction_probability", "f", 2),
        ]
        for t, ctype, n_min in expect:
            got = cons.get((t, ctype), 0)
            if got < n_min:
                print(f"✗ {t} 約束 {ctype} 數 {got} < {n_min}"); ok = False
        # A-28 隔離斷言:augur_predict 對三表無任何權限
        cur.execute("""
            SELECT table_name, count(*) FROM information_schema.table_privileges
            WHERE grantee='augur_predict' AND table_name = ANY(%s) GROUP BY 1""", (list(TABLES),))
        for t, n in cur.fetchall():
            print(f"✗ A-28 違反:augur_predict 對 {t} 有 {n} 項權限(應零)"); ok = False
    print("✓ --verify 全綠" if ok else "✗ --verify 失敗")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.run:
        run(); return 0
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    print("三表現況(唯讀):")
    status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
