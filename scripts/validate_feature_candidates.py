#!/usr/bin/env python
"""augur 特徵候選五鏡驗證 — 算候選 → 橫斷面 rank IC（五鏡①⑤）+ 共線（②）→ 判 raw vs 相對化是否強化。

🎯 這支在做什麼（白話）：把相關分析浮現之兩潛力做成正式候選（audit.feature_candidate）寫進候選 staging 表
feature_candidate_values（audit 邊界:不寫生產表 feature_values）,
對 374 核心跑**橫斷面 rank IC**（evaluation SSOT helper、as-of/purged 口徑、#12）比較:
- raw `pb_ratio`（基準）vs 三層相對化 `pb_xsec_rank` / `pb_industry_demean` / `pb_self_pctile_252d`
  → 答「相對化是否強化」（母原則③ / 審查 G12-G13 消融）
- `inst_govbank_divergence`（govbank×inst 背離）→ 是否有橫斷面預測力
並算候選間 + vs 現有估值特徵之共線（鏡②）。純本地、零 Claude usage（#28）。

組合根:接 audit.feature_candidate（算）+ feature_diagnostics（五鏡 helper）;候選為實驗、未過五鏡不入生產。

守 #1/#8/#9 · #11（五鏡橫斷面 IC、不單指標）· #12（label/metric SSOT）· #15（誠實、n 揭露）。

執行指令矩陣:python scripts/validate_feature_candidates.py --since 2014-01-01 --h 20,60
      python scripts/validate_feature_candidates.py --clear   （驗後清候選、不留 staging）
"""
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as cand
from augur.audit import feature_diagnostics as fd
from augur.core import db


def _panels(cur, since):
    cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (since,))
    return [r[0] for r in cur.fetchall()]


def _core(cur):
    cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
    return [r[0] for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(description="特徵候選五鏡橫斷面 IC 驗證")
    ap.add_argument("--since", default="2014-01-01")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--clear", action="store_true", help="只清候選列、不驗")
    args = ap.parse_args()

    with db.connect() as conn:
        if args.clear:
            print(f"清候選列:{cand.clear_candidates(conn)} 列刪")
            return
        with db.transaction(conn) as cur:
            panels = _panels(cur, args.since)
            core = _core(cur)
        hs = [int(x) for x in args.h.split(",")]
        print(f"算候選:{len(panels)} panel × {len(core)} 核心…")
        n = cand.compute_candidates(conn, panels, core)
        print(f"  候選寫入 {n:,} 值")

        feats = ["pb_ratio", *cand.CANDIDATES]   # raw 基準 + 候選
        print(f"\n══ 橫斷面 rank IC（pan-hist、純單因子、五鏡①⑤）══")
        print(f"{'feature':26s}" + "".join(f"  H={h}: IC/Eff-t/勝率/n" for h in hs))
        for f in feats:
            line = f"{f:26s}"
            for h in hs:
                s = fd.single_factor_ic(conn, panels, h, core, [f], asof=False).get(f, {})
                ic, t, hr, nn = s.get("mean_ic"), s.get("effective_t"), s.get("hit_rate"), s.get("n_panels")
                line += f"  {ic:+.4f}/{t:>5.2f}/{hr:.2f}/{nn:>2d}" if ic is not None else "   n/a            "
            print(line)

        print(f"\n══ 共線（鏡②、|r|≥0.5、候選 vs 估值）══")
        col = fd.collinearity(conn, panels, core, feats, threshold=0.5, asof=False)
        for a, b, r in col["high_pairs"][:12]:
            print(f"  {a} ~ {b}: {r:+.3f}")
        if not col["high_pairs"]:
            print("  （無 |r|≥0.5 對）")

        print("\n判讀:相對化版 |IC|/Eff-t 高於 raw pb_ratio = 強化成立(母原則③);"
              "背離 IC 顯著且與估值低共線 = 新增量。未過 → --clear 清除。")


if __name__ == "__main__":
    main()
