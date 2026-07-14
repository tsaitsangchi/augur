"""augur 循環相位特徵 — 康波「時間結構」鏡頭之存活軸(C2 價格相位 + C4 資金流循環)。

🎯 這支在做什麼(白話):康波的本質不是「40-60 年」,而是「現在在自身循環的哪裡」。對每股、as-of 面板日 t,
用**自身歷史極值**(非固定週期)量「相位」:
- `range_position_120d`:還原價在自身 120d 區間之相位(0=谷/1=峰)
- `days_since_high_252d`:距 252d 高點歷時(窗內比例、循環齡)
- `inst_cumflow_position_{60,120}d`:法人累計淨流在自身區間之相位(吸籌 vs 派發)

**提拔複核結論(2026-06-27、過第4道關卡)**:康波六軸中 **C2(價格相位)+ C4(流相位)存活**(as-of HAC-t |2.8-4.4|、
inst_cumflow_position_120d 為全集最強 Eff-t 4.35);**淘汰**:range_position_60d/days_since_low/max_drawdown/
momentum_accel/momentum_resonance/vol_term_structure(單因子 Eff-t<2 或多因子不增量)。淘汰者探索碼見 git 史 +
`reports/augur_kondratiev_cycle_research_20260627.md`。既有 `cycle_position_252d`(panel.py)= C2 252d 相位。

思想可入、數字不回流(#9/#16):禁固定循環長度;相位由資料自身極值定義。anti-leakage(#8):只用 ≤t 後向窗。
source-pure(#1):算不出(窗不足/零區間)→ 缺列。型別 #5。

守 #1 · #8 · #9(data-driven 相位、無固定週期) · #5 · 康波設計六軸之 C2/C4(存活軸)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.phase              # 印用途+公開入口（唯讀）
  python -m augur.features.phase --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np


def _range_position(c, w):
    """x 在 ≤t 之 w 窗自身區間之相位 (c[-1]−min)/(max−min),0=谷 1=峰;窗不足/零區間 → None。"""
    if len(c) < w:
        return None
    seg = c[-w:]
    lo, hi = seg.min(), seg.max()
    return float((seg[-1] - lo) / (hi - lo)) if hi > lo else None


def _price_phase(df):
    """C2:還原價 → 120d 相位 + 距 252d 高點歷時(存活軸)。"""
    out = {}
    c = df["close"].astype(float).to_numpy()
    v = _range_position(c, 120)
    if v is not None:
        out["range_position_120d"] = v
    if len(c) >= 252:                                          # 距 252d 高點歷時(窗內比例 0-1)
        seg = c[-252:]
        out["days_since_high_252d"] = float((len(seg) - 1 - int(np.argmax(seg))) / (len(seg) - 1))
    return {k: float(v) for k, v in out.items() if v is not None and np.isfinite(v)}


# C4 法人累計淨流(≤t 後向 ~252 交易日、逐日淨買 GROUP BY date)
_INST_DAILY_SQL = (
    'SELECT date, (sum(buy)-sum(sell))::float8 FROM "TaiwanStockInstitutionalInvestorsBuySell" '
    'WHERE stock_id=%s AND date <= %s GROUP BY date ORDER BY date DESC LIMIT 252'
)


def _inst_flow_cycle(cur, sid, panel_date):
    """C4:法人累計淨流在自身 rolling 區間之相位(吸籌 vs 派發);60/120d 窗(存活軸)。"""
    out = {}
    cur.execute(_INST_DAILY_SQL, (sid, panel_date))
    rows = cur.fetchall()
    if len(rows) < 60:
        return out
    net = np.array([r[1] for r in rows[::-1]], dtype=float)        # 還原升序
    net = net[np.isfinite(net)]
    cum = np.cumsum(net)
    for w in (60, 120):
        v = _range_position(cum, w)                                # 累計流相位(0=派發底、1=吸籌頂)
        if v is not None:
            out[f"inst_cumflow_position_{w}d"] = v
    return out


def compute_phase_features(cur, sid, panel_date, price_df=None):
    """康波 per-stock 存活相位特徵(C2 + C4)→ {feature: value};算不出之特徵缺列(#1)。"""
    out = {}
    if price_df is not None and len(price_df):
        out.update(_price_phase(price_df))                        # C2
    out.update(_inst_flow_cycle(cur, sid, panel_date))            # C4
    return {k: float(v) for k, v in out.items() if v is not None and np.isfinite(v)}


def _selftest():
    """純紅綠(零 IO):相位不變式——0=谷 1=峰、窗不足/零區間 → None。"""
    import numpy as np
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    chk("升序末=峰 → 相位 1.0", _range_position(np.array([1., 2, 3, 4, 5]), 5) == 1.0)
    chk("降序末=谷 → 相位 0.0", _range_position(np.array([5., 4, 3, 2, 1]), 5) == 0.0)
    chk("中位 → 相位 0.5", _range_position(np.array([0., 10, 5]), 3) == 0.5)
    chk("窗不足 → None", _range_position(np.array([1., 2, 3]), 5) is None)
    chk("零區間(全等) → None", _range_position(np.array([3., 3, 3]), 3) is None)
    chk("公開入口 compute_phase_features 存在", callable(compute_phase_features))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.features.phase --selftest;免 DB 免 API)")
