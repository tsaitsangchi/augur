#!/usr/bin/env python
"""augur 鏡頭軸相關分析 — 以量×形×位三軸結構重檢生產特徵相關矩陣、實證三軸正交性 + 跨鏡結構。

🎯 這支在做什麼(白話):依四鏡頭框架(綜合報告:量=第一性/形=八二/位=康波三正交軸),把 34 生產特徵之
as-of 相關矩陣**按軸分群**,答三問:
1. **三軸真的正交嗎?** cross-axis 中位 |corr| 應 << within-axis(若框架成立)。
2. **冗餘在哪?** within-axis 高相關群(同軸內可去重)。
3. **跨鏡結構在哪?** 最強 cross-axis 對(量×形/量×位/形×位 之交互、特徵前沿)。

口徑 reuse evaluation/audit helper(#12 可比);as-of point-in-time(#8)。純 DB 計算、零 Claude usage(#28)。

守 #8(as-of)· #11(五鏡之共線鏡延伸)· #12(SSOT helper)· #15(誠實揭露 n、係數可溯)。
執行指令矩陣:python scripts/run_lens_correlation.py
"""
from __future__ import annotations

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_diagnostics as fd
from augur.core import db

# 34 特徵 → 三軸(量=第一性資訊內容、形=八二分布集中、位=康波時間相位)
AXIS = {
    # 位(康波相位/位置)
    "cycle_position_252d": "位", "price_to_252d_high": "位", "range_position_120d": "位",
    "days_since_high_252d": "位", "inst_cumflow_position_60d": "位", "inst_cumflow_position_120d": "位",
    # 形(八二集中度)
    "volume_gini_20d": "形", "volume_gini_60d": "形", "volume_max_share_20d": "形", "volume_max_share_60d": "形",
    # 量(第一性:水位/動能/籌碼/估值/規模)— 其餘皆量
}
DEFAULT_AXIS = "量"


def _axis(f):
    return AXIS.get(f, DEFAULT_AXIS)


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", ("2014-01-01",))
            panels = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
            core = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT DISTINCT feature FROM feature_values ORDER BY feature")
            feats = [r[0] for r in cur.fetchall()]
        print(f"鏡頭軸相關:{len(panels)} panel × {len(core)} 核心 × {len(feats)} 特徵(as-of)")
        res = fd.collinearity(conn, panels, core, feats, threshold=0.5, asof=True)
        C, feats = res["corr"], res["feats"]
        n = len(feats)
        axes = [_axis(f) for f in feats]
        cnt = {a: axes.count(a) for a in ("量", "形", "位")}
        print(f"軸分布:量 {cnt['量']} / 形 {cnt['形']} / 位 {cnt['位']}")

        # 1. 三軸正交性:各 axis-pair 之 |corr| 中位/最大(上三角)
        buckets = {}
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if not np.isfinite(C[i, j]):
                    continue
                key = "·".join(sorted([axes[i], axes[j]]))
                buckets.setdefault(key, []).append(abs(C[i, j]))
                pairs.append((abs(C[i, j]), C[i, j], feats[i], feats[j], axes[i], axes[j]))
        print("\n══ 1. 三軸正交性檢驗(|corr| 中位 / 90 分位 / 最大、對數)══")
        print(f"{'軸對':10s} {'中位':>7s} {'p90':>7s} {'最大':>7s} {'對數':>5s}")
        for k in sorted(buckets):
            v = np.array(buckets[k])
            tag = "(within)" if "·" not in k or k.split("·")[0] == k.split("·")[1] else "(cross)"
            print(f"{k:10s} {np.median(v):>7.3f} {np.quantile(v,0.9):>7.3f} {v.max():>7.3f} {len(v):>5d} {tag}")

        # 2. within-axis 冗餘(同軸高相關群)
        print("\n══ 2. 同軸冗餘 top(within-axis |corr|≥0.6)══")
        within = sorted([p for p in pairs if p[4] == p[5] and p[0] >= 0.6], reverse=True)
        for ac, c, a, b, ax, _ in within[:12]:
            print(f"  [{ax}] {a:26s} ~ {b:26s} {c:+.3f}")

        # 3. 跨鏡結構(cross-axis 最強對 = 特徵交互前沿)
        print("\n══ 3. 跨鏡結構 top(cross-axis 最強 |corr|)══")
        cross = sorted([p for p in pairs if p[4] != p[5]], reverse=True)
        for ac, c, a, b, ax1, ax2 in cross[:15]:
            print(f"  [{ax1}×{ax2}] {a:24s} ~ {b:24s} {c:+.3f}")

        print("\n判讀:cross-axis 中位 << within-axis → 三軸正交(框架成立);cross top 對 = 跨鏡交互候選。")


if __name__ == "__main__":
    main()
