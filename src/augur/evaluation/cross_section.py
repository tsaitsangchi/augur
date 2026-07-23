"""augur 橫斷面交互變換 — eval 層動態算「橫斷面 z 標準化後因子交乘」之衍生特徵。

🎯 這支在做什麼（白話）：交互特徵（如 inter_fh_x_p10yr＝外資持股 × 10 年線位置）是**橫斷面量**——
其值依「當前評估宇宙」整池組成而變（z 用當前 panel 橫斷面 mean/std）、非單股 as-of raw。
故不入 feature_values（per-stock、宇宙無關），由 eval 層在組好 panel 矩陣後動態 append、綁當前宇宙——
與 label（同屬宇宙相依量、亦 eval 層動態）同層；換宇宙（374→461→1117）時自動依新宇宙重歸一、不凍結舊值。
口徑＝橫斷面簡單 z 乘積（與提拔驗證 `verify_interaction_promotion.py` 同源、ΔIC 可重現）。

守 #8（橫斷面 z 只用該 panel 當下宇宙、不跨日、不洩漏未來）· #11/#14（過四道漏斗+提拔關卡+經濟價值）·
   #12（口徑與 verify 同源）· #18（領域名詞、eval 層派生變換）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.evaluation.cross_section              # 印用途+公開入口（唯讀）
  python -m augur.evaluation.cross_section --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np

# 交互註冊表：name → (成分 a, 成分 b)；兩成分須為生產 feat（canonical），交互＝橫斷面 z(a)×z(b)。
# inter_fh_x_p10yr（外資持股 × 10年線位置）：過四道漏斗 + 經濟價值 #14（2026-06-29）。
# ⚠️ **局部效應、非 robust alpha**：僅 374 核心宇宙 + 生產特徵集有適度增量（H60 ΔIC+0.0034/Sharpe 1.21→1.25、
#    H120 Sharpe 1.53→1.61）；**換寬宇宙（1245 股含中小型）ΔIC 轉負（−0.0005）、經濟價值不再提升**
#    → **opt-in 限 374 核心宇宙、不設生產預設、不外推至擴展宇宙**（2026-06-29 換宇宙重測實證、#15「驗證活下來
#    才算數」；經濟直覺：外資持股 × 10年線交互或僅大型權值股有意義、中小型股無此效應）。
INTERACTIONS = {
    "inter_fh_x_p10yr": ("foreign_holding_pct", "price_to_10yr"),
}


def _z(v):
    """橫斷面簡單 z（與提拔驗證口徑同源：(v-mean)/std）。"""
    return (v - v.mean()) / (v.std() + 1e-9)


def augment(X, feats, want):
    """對已組好之 panel 矩陣 X（k 股 × f 特徵、feats 為欄名序）append 請求之交互欄（橫斷面 z 乘積）。

    z 用當前 X 之橫斷面（＝當前評估宇宙、point-in-time #8）；兩成分須在 feats 內（canonical 含）。
    回 (X', feats')——股（列）不變、只在尾端加交互欄（不動既有欄序，B1 mom_idx 等仍有效）。
    want 中成分不在 feats 之交互略過（理論上 prod 含兩成分）。
    """
    if not want or len(X) == 0:
        return X, list(feats)
    fidx = {f: i for i, f in enumerate(feats)}
    add_cols, add_names = [], []
    for name in want:
        a, b = INTERACTIONS[name]
        if a not in fidx or b not in fidx:
            continue
        add_cols.append(_z(X[:, fidx[a]]) * _z(X[:, fidx[b]]))
        add_names.append(name)
    if not add_cols:
        return X, list(feats)
    return np.column_stack([X, *add_cols]), list(feats) + add_names


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # 註冊表結構：交互＝兩成分 tuple
    chk("INTERACTIONS 含 inter_fh_x_p10yr", "inter_fh_x_p10yr" in INTERACTIONS)
    chk("成分為 (foreign_holding_pct, price_to_10yr)",
        INTERACTIONS["inter_fh_x_p10yr"] == ("foreign_holding_pct", "price_to_10yr"))
    # _z：橫斷面 z 均值≈0（#8 口徑）
    z = _z(np.array([1., 2., 3.]))
    chk("_z 均值≈0", abs(z.mean()) < 1e-6)
    # _z：常數輸入不炸（除零護欄 +1e-9）→ 全 0
    chk("_z 常數輸入→全0", np.allclose(_z(np.array([5., 5., 5.])), 0.0))
    # augment：尾端 append 交互欄、股(列)不變、既有欄序不動
    X = np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]])
    feats = ["foreign_holding_pct", "price_to_10yr", "other"]
    X2, f2 = augment(X, feats, ["inter_fh_x_p10yr"])
    chk("augment 列數不變、加一欄", X2.shape == (3, 4))
    chk("augment 欄名尾端加交互", f2 == feats + ["inter_fh_x_p10yr"])
    chk("augment 既有欄序不動", np.array_equal(X2[:, :3], X))
    chk("augment 交互值=z(a)×z(b)",
        np.allclose(X2[:, 3], _z(X[:, 0]) * _z(X[:, 1])))
    # augment：空 want / 空 X → 原樣回、feats 為 list 副本
    chk("augment 空 want 原樣回", augment(X, feats, [])[1] == feats)
    # augment：成分不在 feats 之交互略過
    X3, f3 = augment(X[:, :1], ["foreign_holding_pct"], ["inter_fh_x_p10yr"])
    chk("augment 缺成分則略過", f3 == ["foreign_holding_pct"] and X3.shape == (3, 1))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.evaluation.cross_section --selftest;免 DB 免 API)")
