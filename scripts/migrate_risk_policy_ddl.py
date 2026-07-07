#!/usr/bin/env python
"""部署前風控政策 schema 遷移 — risk_policy 一表冪等落地 + STAGE D 修正閾值 seed(部署計劃階段 D3)。

🎯 這支在做什麼(白話):建立「風控政策表」——把 DD 熔斷 / 單標的部位上限 / 換手預算三類閾值,
   以 (horizon, policy_key) 為主鍵住進 DB,**風控模組讀 DB、不 hardcode Python**(#29b:別名/config
   住 DB 精神)。seed 值用 STAGE D **對抗驗證修正後**之近期深回檔——非全期溫和值:
     - DD 熔斷:H60 −20% / H120 −25%(近期 2021 起 regime DD 更深 H60 −19.4%/H120 −24.1%,
       用全期溫和值 H60 −13.9%/H120 −8.7% 會被觸破,#15 誠實=近期深值有據);
     - 單標的部位上限:0.10(top-decile 等權自然 ~2.94%,pred 加權設 cap 防集中);
     - 換手預算:0.75(STAGE D 實測 avg_turnover ~0.65-0.71/期,稍外緣防正常波動誤觸)。
   全部 IF NOT EXISTS + seed ON CONFLICT DO NOTHING(既有值不覆蓋、重跑零副作用、冪等);
   seed 值屬**操作值**(#27 n 小 8-25、方向性),持續再驗證(D5)校準後 UPDATE、不寫死判準。

守 #6(冪等重跑安全)· #12(DDL 單一住所)· #15(閾值 trace 回 STAGE D 報告 §三修正值、誠實近期深值)·
   #27(操作值不入判準、config 可調)· #29(個別可執行 + 指令矩陣、閾值資料驅動住 DB)·
   SSOT=reports/augur_prediction_stageD_robustness_verdict_20260707.md §三 + deployment_plan §8 階段 D3。

執行指令矩陣:
  python scripts/migrate_risk_policy_ddl.py           # 冪等執行 DDL + seed + 印驗證清單(安全預設)
  python scripts/migrate_risk_policy_ddl.py --check   # 唯讀:只印驗證清單 + 現有政策、不執行 DDL/seed
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DDL = [
    ("table risk_policy", """
        CREATE TABLE IF NOT EXISTS risk_policy (
          horizon      int  NOT NULL,
          policy_key   text NOT NULL,
          threshold    double precision NOT NULL,
          action       text NOT NULL,
          source_ref   text NOT NULL,
          note         text,
          updated_at   timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (horizon, policy_key),
          CONSTRAINT risk_policy_key_chk
            CHECK (policy_key IN ('dd_circuit','max_position','turnover_budget'))
        )"""),
    ("comment risk_policy", """
        COMMENT ON TABLE risk_policy IS
        '部署前風控政策(D3);(horizon,policy_key)→閾值+動作,風控模組讀此不 hardcode(#29b);seed=STAGE D 修正近期深值、操作值可 UPDATE(#27)、不進預測管線(隔離不變式外、唯決策輔助)'"""),
    ("comment col threshold", """
        COMMENT ON COLUMN risk_policy.threshold IS
        'dd_circuit=回檔觸發降倉之負門檻(如 -0.20);max_position=單標的權重上限(如 0.10);turnover_budget=每期換手上限(如 0.75)'"""),
    ("comment col source_ref", """
        COMMENT ON COLUMN risk_policy.source_ref IS
        '閾值來源(#15 可溯源):STAGE D 報告 §三修正值/實測 avg_turnover;非記憶推估'"""),
]

# STAGE D 修正閾值 seed(#15:每列 source_ref trace 回 STAGE D 報告;近期深回檔非全期溫和值)
_STAGE_D = "reports/augur_prediction_stageD_robustness_verdict_20260707.md §三(對抗驗證修正)"
SEED = [
    # (horizon, policy_key, threshold, action, source_ref, note)
    (60, "dd_circuit", -0.20, "reduce_half",
     _STAGE_D, "近期 2021 起 H60 LO MaxDD −19.4%(全期 −13.9% 會被觸破);觸 −20% 建議減半降倉"),
    (120, "dd_circuit", -0.25, "reduce_half",
     _STAGE_D, "近期 2021 起 H120 LO MaxDD −24.1%(全期 −8.7% 太樂觀);觸 −25% 建議減半降倉"),
    (60, "max_position", 0.10, "cap",
     _STAGE_D, "單標的權重上限;top-decile 等權自然 ~1/34≈0.029,pred 加權須 cap 防集中"),
    (120, "max_position", 0.10, "cap",
     _STAGE_D, "單標的權重上限;top-decile 等權自然 ~1/34≈0.029,pred 加權須 cap 防集中"),
    (60, "turnover_budget", 0.75, "warn",
     _STAGE_D, "每期換手上限;STAGE D 實測 avg_turnover ~0.65-0.71,超 0.75 告警(高換手侵蝕淨值)"),
    (120, "turnover_budget", 0.75, "warn",
     _STAGE_D, "每期換手上限;STAGE D 實測 avg_turnover ~0.65-0.71,超 0.75 告警(高換手侵蝕淨值)"),
]

VERIFY = [
    ("risk_policy 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='risk_policy'"),
    ("policy_key CHECK", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='risk_policy_key_chk'"),
    ("表 COMMENT", "SELECT obj_description('risk_policy'::regclass)"),
    ("現有政策數", "SELECT count(*) FROM risk_policy"),
]


def _seed(cur):
    for row in SEED:
        cur.execute(
            """INSERT INTO risk_policy (horizon,policy_key,threshold,action,source_ref,note)
               VALUES (%s,%s,%s,%s,%s,%s)
               ON CONFLICT (horizon,policy_key) DO NOTHING""", row)
    print(f"✓ seed {len(SEED)} 列(ON CONFLICT DO NOTHING、既有不覆蓋)")


def _show_policies(cur):
    try:
        cur.execute("SELECT horizon,policy_key,threshold,action,note FROM risk_policy ORDER BY horizon,policy_key")
        rows = cur.fetchall()
        if not rows:
            print("  現有政策: (無)")
            return
        print("── 現有風控政策 ──")
        for h, k, t, a, note in rows:
            print(f"  H{h:<4} {k:<16} threshold={t:+.4g}  action={a:<12} {note or ''}")
    except Exception as e:  # noqa: BLE001  表未建時誠實印、不中斷
        print(f"  現有政策: (查詢失敗:{e})")


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
    ap = argparse.ArgumentParser(description="風控政策 DDL 遷移 + STAGE D 修正閾值 seed(risk_policy;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單 + 現有政策、不執行 DDL/seed")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
            _seed(cur)
        _verify(cur)
        _show_policies(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
