#!/usr/bin/env python
"""S3-BETA-beta2 — 單一交互候選 pb_pctile_x_dvlog 材料化＋IC（禁重跑舊四名 verify）。

🎯 z(pb_self_pctile_252d)×z(dollar_volume_log_20d) 寫入 feature_candidate_values；
   印 pan-hist／as-of 單因子 IC＋HAC-t。過 HAC(|t|≥2) 才建議另跑 verify_candidate_promotion。
守 FZ/GATE-keep · skip-sync · no-SIM-apply · #8 · #11 · #15。

執行指令矩陣:
  python scripts/run_s3_beta2_interaction.py              # 印矩陣
  python scripts/run_s3_beta2_interaction.py --run        # 只算 β2＋IC（H20,H60）
  python scripts/run_s3_beta2_interaction.py --run --since 2014-01-01 --h 20,60
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.audit import feature_candidate as cand
from augur.audit import feature_diagnostics as fd
from augur.core import db


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default="2014-01-01")
    ap.add_argument("--h", default="20,60")
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    hs = [int(x) for x in args.h.split(",")]
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date",
                (args.since,),
            )
            panels = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
            core = [r[0] for r in cur.fetchall()]
        print(f"β2 materialize only={cand.BETA2_INTERACT} | {len(panels)} panel × {len(core)} core")
        n = cand.compute_candidates(conn, panels, core, only=[cand.BETA2_INTERACT])
        print(f"  寫入/更新 {n:,} 值")
        with db.transaction(conn) as cur:
            cur.execute(
                f"SELECT count(*), min(panel_date), max(panel_date) FROM {cand.FEATURE_TABLE} "
                "WHERE feature=%s",
                (cand.BETA2_INTERACT,),
            )
            cnt, mn, mx = cur.fetchone()
        print(f"  表內 {cand.BETA2_INTERACT}: n={cnt} {mn}..{mx}")

        print(f"\n══ pan-hist 單因子 rank IC（鏡①⑤）══")
        print(f"{'feature':26s}" + "".join(f"  H={h}: IC/iid-t/HAC-t/勝率/n" for h in hs))
        for f in (cand.BETA2_INTERACT, "pb_self_pctile_252d"):
            line = f"{f:26s}"
            for h in hs:
                s = fd.single_factor_ic(conn, panels, h, core, [f], asof=False).get(f, {})
                ic = s.get("mean_ic")
                if ic is None:
                    line += "   n/a                  "
                else:
                    line += (f"  {ic:+.4f}/{s.get('effective_t', float('nan')):>5.2f}/"
                             f"{s.get('effective_t_hac', float('nan')):>5.2f}/"
                             f"{s.get('hit_rate', float('nan')):.2f}/{s.get('n_panels', 0):>2d}")
            print(line)

        print(f"\n══ as-of 單因子 rank IC（提拔預篩）══")
        print(f"{'feature':26s}" + "".join(f"  H={h}: IC/iid-t/HAC-t/勝率/n" for h in hs))
        for f in (cand.BETA2_INTERACT, "pb_self_pctile_252d"):
            line = f"{f:26s}"
            for h in hs:
                s = fd.single_factor_ic(conn, panels, h, core, [f], asof=True).get(f, {})
                ic = s.get("mean_ic")
                if ic is None:
                    line += "   n/a                  "
                else:
                    line += (f"  {ic:+.4f}/{s.get('effective_t', float('nan')):>5.2f}/"
                             f"{s.get('effective_t_hac', float('nan')):>5.2f}/"
                             f"{s.get('hit_rate', float('nan')):.2f}/{s.get('n_panels', 0):>2d}")
            print(line)

        # 預凍判讀：as-of H60 HAC |t|≥2 才「IC 有證據」→ 可另跑 #11
        s60 = fd.single_factor_ic(conn, panels, 60, core, [cand.BETA2_INTERACT], asof=True).get(
            cand.BETA2_INTERACT, {}
        )
        hac = s60.get("effective_t_hac")
        ok_ic = hac is not None and abs(float(hac)) >= 2.0
        print(
            f"\n預篩: as-of H60 HAC-t={hac} → "
            + ("✓ |t|≥2——可另跑 verify_candidate_promotion --features "
               f"{cand.BETA2_INTERACT} --h 60 --seeds 3 --keep"
               if ok_ic
               else "✗ 未過 HAC——停、不自動 #11、不 promote")
        )
        return 0 if ok_ic else 2


if __name__ == "__main__":
    sys.exit(main())
