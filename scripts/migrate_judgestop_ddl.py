#!/usr/bin/env python
"""判停器 schema 遷移 — judgestop_threshold + revalidation_verdict 兩表冪等落地 + 閾值 seed(harness P2)。

🎯 這支在做什麼(白話):建兩軌三態判停器所需之兩張表——
   - **judgestop_threshold**(#29b 閾值住 DB、循 knowledge_topic_alias 先例):軌A/軌B 之判準閾值,
     admin 可 INSERT/UPDATE 零改碼;doctrine 硬閾值 frozen=true(調整須人留痕、#15 不調鬆);
     operational 閾值(rel_drop/consecutive_k)校準期 frozen=false、定案後凍結。
   - **revalidation_verdict**(no-AI 機械判詞 + provenance + 隔離):逐輪裁決可稽核可回溯;
     state 三態機械算(閾值比對、非 AI 生成)。

   **判停命門(5 鏡對抗審查釘死)**:**軌A 地板監測=絕對門檻(DSR<95% 等)→ 只標註「未達統計確立」、
   永不判停**(headline 現就<95%=薄 edge 常態,入判停=首輪誤殺);**軌B 衰減告警=相對凍結 baseline
   (revalidation_baseline)顯著劣化(net 從曾勝轉輸/HAC-t 從>2 掉破/deflated 地板轉負)→ 才判停**,
   scoped 部署 cell、同宇宙鎖、連續 k 輪(單點不判)。三態:deploying_unestablished(部署中-未確立、常態)
   / suspected_decay_review(疑似衰減-人審)/ confirmed_decay_stop(確認衰減-停)。

守 #12(DDL 單一住所)· #15(判停≠失敗、DSR 不入判停)· #29b(閾值住 DB、admin 零改碼)· #29a ·
   隔離不變式(verdict 禁 import 素養/advisor、禁回讀 prediction_values)· SSOT=harness plan §0/§3.5/P2。

執行指令矩陣:
  python scripts/migrate_judgestop_ddl.py          # 冪等執行 DDL + seed 閾值 + 印驗證清單
  python scripts/migrate_judgestop_ddl.py --check   # 唯讀:只印驗證清單
  python scripts/migrate_judgestop_ddl.py --no-seed # 只建表、不 seed 閾值
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = [
    ("table judgestop_threshold", """
        CREATE TABLE IF NOT EXISTS judgestop_threshold (
          policy_key  text NOT NULL,          -- dsr_annotate / net_excess_zero / net_excess_rel_drop / hac_t_floor / consecutive_k / deflated_floor_zero
          horizon     int  NOT NULL DEFAULT 0,-- 0=全域;60/120=該 horizon
          track       text NOT NULL,          -- 'A_annotate'(標註、永不判停) | 'B_decay'(衰減判停)
          threshold   double precision NOT NULL,
          frozen      boolean NOT NULL DEFAULT false,   -- 拍板凍結;調整須人留痕(#15 不調鬆)
          source_ref  text NOT NULL,
          note        text,
          PRIMARY KEY (policy_key, horizon),
          CONSTRAINT chk_js_track CHECK (track IN ('A_annotate','B_decay','R_robust'))
        )"""),
    ("migrate chk_js_track +R_robust +created_at (驗證總綱 §3.2)", """
        DO $$ BEGIN
          ALTER TABLE judgestop_threshold DROP CONSTRAINT IF EXISTS chk_js_track;
          ALTER TABLE judgestop_threshold ADD CONSTRAINT chk_js_track
            CHECK (track IN ('A_annotate','B_decay','R_robust'));
          ALTER TABLE judgestop_threshold ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
        END $$"""),
    ("table revalidation_verdict", """
        CREATE TABLE IF NOT EXISTS revalidation_verdict (
          verdict_at        timestamptz NOT NULL DEFAULT now(),
          as_of_date        date NOT NULL,
          cell              text NOT NULL,       -- 部署 cell(如 'ridge_H60_LO')
          universe          text NOT NULL DEFAULT 'asof_incumbent',
          track             text NOT NULL,       -- 'A_annotate' | 'B_decay'
          state             text NOT NULL,       -- 三態
          triggered_cond    text,                -- 軌B 觸發條件(軌A=NULL)
          metric_snapshot   jsonb NOT NULL,      -- {net_sharpe,bench,net_excess,hac_t,dsr,deflated_ann,n} 機械快照
          baseline_ref      text,                -- 軌B 比較之凍結 baseline
          threshold_source  text,                -- judgestop_threshold policy_key
          note              text,
          PRIMARY KEY (as_of_date, cell, track),
          CONSTRAINT chk_rv_track CHECK (track IN ('A_annotate','B_decay')),
          CONSTRAINT chk_rv_state CHECK (state IN ('deploying_unestablished','suspected_decay_review','confirmed_decay_stop'))
        )"""),
    ("comment revalidation_verdict", """
        COMMENT ON TABLE revalidation_verdict IS
        '再驗證兩軌三態判停裁決(harness P2);no-AI:state 由 judgestop_threshold 閾值機械比對算、非 AI 判詞;軌A 絕對門檻只標註永不判停、軌B 相對凍結 baseline 衰減才判停;唯記錄面、不進預測管線、verdict.py 禁 import 素養/advisor'"""),
]

# seed 閾值(bootstrap;SSOT 是 DB 表非 code,種子一次性)。doctrine 硬閾值 frozen=true;operational 校準期 frozen=false。
SEED = [
    # 軌A(絕對門檻、只標註、永不判停)
    ("dsr_annotate", 0, "A_annotate", 0.95, True,
     "deflation_verdict_20260708 §0", "DSR<此=未達統計確立、軌A 標註薄edge常態、永不判停"),
    # 軌B(相對凍結 baseline 衰減、才判停)
    ("net_excess_zero", 0, "B_decay", 0.0, True,
     "harness plan P2", "net−bench≤此=經濟價值消失(從曾勝轉輸)=衰減訊號"),
    ("net_excess_rel_drop", 0, "B_decay", 0.5, False,
     "harness plan P2(校準中)", "超額相對凍結基線下滑>此比例=衰減訊號;operational 待校準凍結"),
    ("hac_t_floor", 0, "B_decay", 2.0, True,
     "harness plan P2/SOP", "IC HAC-t<此(基線曾>2)=顯著性崩=衰減訊號;HAC-t=None(小樣本)不觸發"),
    ("deflated_floor_zero", 0, "B_decay", 0.0, True,
     "harness plan P2", "deflated 年化有效 Sharpe≤此=地板轉負=衰減訊號"),
    ("consecutive_k", 0, "B_decay", 2.0, False,
     "harness plan P2(校準中)", "連續此輪衰減訊號→confirmed_decay_stop、否則 suspected_decay_review;單點不判停"),
]

VERIFY = [
    ("judgestop_threshold 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='judgestop_threshold'"),
    ("revalidation_verdict 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='revalidation_verdict'"),
    ("verdict state CHECK", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='chk_rv_state'"),
    ("seed 閾值(policy/track/threshold/frozen)", "SELECT string_agg(policy_key||'='||threshold||'('||track||(CASE WHEN frozen THEN ',frozen' ELSE '' END)||')', '; ' ORDER BY track,policy_key) FROM judgestop_threshold"),
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
    ap = argparse.ArgumentParser(description="判停器 DDL + 閾值 seed(judgestop_threshold/revalidation_verdict;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單")
    ap.add_argument("--no-seed", action="store_true", help="只建表、不 seed 閾值")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
            if not args.no_seed:
                for pk, h, tr, thr, fz, src, nt in SEED:
                    cur.execute(
                        "INSERT INTO judgestop_threshold (policy_key,horizon,track,threshold,frozen,source_ref,note) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (policy_key,horizon) DO NOTHING",  # 已存在不覆(凍結尊重人留痕)
                        (pk, h, tr, thr, fz, src, nt))
                print(f"✓ seed judgestop_threshold({len(SEED)} 列、ON CONFLICT DO NOTHING 尊重既有)")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
