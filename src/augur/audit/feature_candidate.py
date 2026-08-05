"""augur 特徵候選計算 + 五鏡驗證底料 — 把相關性分析浮現之候選做成 as-of 安全特徵、供橫斷面 IC 驗。

🎯 這支在做什麼（白話）：依方法論母原則③（目標相對→特徵必相對化）把兩個潛力發現做成**正式特徵候選**,
寫進候選 staging 表 feature_candidate_values（核心股 × panel、as-of 安全),供 `feature_diagnostics` 五鏡橫斷面 rank IC 驗證:

1. PBR-value 強化（raw pb_ratio 之三層相對化,審查 G12/G13）：
   - `pb_xsec_rank`：同日橫斷面 percentile rank（0-1、低=便宜）
   - `pb_industry_demean`：pb − 產業內中位（TaiwanStockInfo.industry_category、同 panel）
   - `pb_self_pctile_252d`：當前 PBR 在自身 252 交易日歷史之百分位（0-1）
2. govbank×inst 背離交互（相關分析 govbank_net~inst_net −0.48）：
   - `inst_govbank_divergence`：橫斷面 z(institutional_net_buy_ratio_20d) − z(gov_bank_net_buy_60d)
3. β2 交互（S3-BETA-beta2，2026-08-05）：
   - `pb_pctile_x_dvlog`：同 panel 橫斷面 z(`pb_self_pctile_252d`) × z(`dollar_volume_log_20d`)
     （流動性控制；cutoff-free；母原則③相對化後再交互）

anti-leakage（#8）：全候選只用 panel t（含）以前之值——橫斷面 rank/z/demean 為同 panel 內運算、自身百分位
為 ≤t 歷史窗;無未來。source-pure（#1）：算不出（無 raw / 窗不足 / 同 panel 無變異）→ 缺列、不補。
**實驗性**：候選寫獨立 staging 表、不寫 feature_values（audit 邊界:生產表由 feature 層獨佔寫入;
staging 機制性隔離 core_gate/canonical_features 完整度 gate,非僅紀律);通過五鏡才提拔進 features/ 生產。

守 #1 · #8 · #9（rank/z/demean/percentile 皆 cutoff-free、無硬編閾值）· 母原則③相對化 · #12（驗證用 evaluation SSOT helper）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.audit.feature_candidate              # 印用途+公開入口（唯讀）
  python -m augur.audit.feature_candidate --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from augur.core import db

PROD_TABLE = "feature_values"                 # 唯讀來源（生產特徵;audit 層不寫,憲章 audit 邊界）
FEATURE_TABLE = "feature_candidate_values"    # 候選 staging（audit 自建;verify_* 家族以 fc.FEATURE_TABLE 為候選寫入口）
CANDIDATES = (
    "pb_xsec_rank",
    "pb_industry_demean",
    "pb_self_pctile_252d",
    "inst_govbank_divergence",
    "pb_pctile_x_dvlog",  # β2：pctile × 流動性 log-dollar-volume
)
BETA2_INTERACT = "pb_pctile_x_dvlog"


def ensure_candidate_table(conn):
    """建候選 staging 表（schema 同構 feature_values;audit 自建分析表、不碰生產表）。冪等。"""
    with db.transaction(conn) as cur:
        cur.execute(f"CREATE TABLE IF NOT EXISTS {FEATURE_TABLE} ("
                    "panel_date date NOT NULL, stock_id varchar(255) NOT NULL, "
                    "feature varchar(255) NOT NULL, value numeric(20,6) NOT NULL, "
                    "PRIMARY KEY (panel_date, stock_id, feature))")


def _panel_feature(cur, panel_date, feature, stocks):
    """某 panel 某特徵之 {stock_id: value}（限 stocks;讀生產表）。"""
    cur.execute(f"SELECT stock_id, value FROM {PROD_TABLE} WHERE panel_date=%s AND feature=%s AND stock_id = ANY(%s)",
                (panel_date, feature, list(stocks)))
    return {str(r[0]): float(r[1]) for r in cur.fetchall()}


def _industry_map(cur, stocks):
    cur.execute("SELECT stock_id, industry_category FROM \"TaiwanStockInfo\" WHERE stock_id = ANY(%s)", (list(stocks),))
    return {str(r[0]): r[1] for r in cur.fetchall()}


def _zscore(d):
    """{id:val} → 橫斷面 z（母體 std；單元素/零變異 → 空 dict）。"""
    if len(d) < 3:
        return {}
    v = np.array(list(d.values()), float)
    sd = v.std()
    if not np.isfinite(sd) or sd == 0:
        return {}
    m = v.mean()
    return {k: float((x - m) / sd) for k, x in d.items()}


def _interact_z(a, b):
    """同鍵集合上 z(a)×z(b)；任一侧 z 空 → 空 dict（#35 純函式）。"""
    za, zb = _zscore(a), _zscore(b)
    return {k: float(za[k] * zb[k]) for k in set(za) & set(zb)}


def compute_candidates(conn, panel_dates, stocks, *, progress=None, only=None):
    """對 panel_dates × stocks 算候選 → 寫候選 staging 表（ON CONFLICT 冪等）。回寫入列數。

    only: 可選 iterable，只算所列名（β2 窄跑用）；預設全 CANDIDATES。
    """
    stocks = [str(s) for s in stocks]
    want = set(only) if only is not None else set(CANDIDATES)
    written = 0
    ensure_candidate_table(conn)
    # pb_self_pctile_252d 需自身 PBR 日序：一次抓全 stocks 全史,記憶體算（避免逐 panel N² 查）
    need_pbr = bool(want & {"pb_xsec_rank", "pb_industry_demean", "pb_self_pctile_252d", BETA2_INTERACT})
    with db.transaction(conn) as cur:
        per_rows = []
        if need_pbr:
            cur.execute(
                'SELECT stock_id, date, "PBR"::float8 FROM "TaiwanStockPER" '
                "WHERE stock_id = ANY(%s) AND \"PBR\" IS NOT NULL ORDER BY stock_id, date",
                (stocks,),
            )
            per_rows = cur.fetchall()
        industry = _industry_map(cur, stocks) if want & {"pb_industry_demean"} else {}
    pbr_by_stock = {}
    for sid, d, v in per_rows:
        pbr_by_stock.setdefault(str(sid), []).append((d, float(v)))

    for pd_ in panel_dates:
        rows = []
        with db.transaction(conn) as cur:
            pb = _panel_feature(cur, pd_, "pb_ratio", stocks) if need_pbr else {}
            inst = (
                _panel_feature(cur, pd_, "institutional_net_buy_ratio_20d", stocks)
                if "inst_govbank_divergence" in want else {}
            )
            gov = (
                _panel_feature(cur, pd_, "gov_bank_net_buy_60d", stocks)
                if "inst_govbank_divergence" in want else {}
            )
            dv = (
                _panel_feature(cur, pd_, "dollar_volume_log_20d", stocks)
                if BETA2_INTERACT in want else {}
            )
        pctile = {}
        if want & {"pb_xsec_rank", "pb_industry_demean"} and len(pb) >= 3:
            if "pb_xsec_rank" in want:
                s = pd.Series(pb).rank(pct=True)
                rows += [(pd_, k, "pb_xsec_rank", round(float(v), 6)) for k, v in s.items()]
            if "pb_industry_demean" in want:
                df = pd.DataFrame({"pb": pb}).assign(ind=lambda d: d.index.map(industry))
                med = df.groupby("ind")["pb"].transform("median")
                dem = (df["pb"] - med).dropna()
                rows += [(pd_, k, "pb_industry_demean", round(float(v), 6)) for k, v in dem.items()]
        # pb_self_pctile_252d（自身 252 交易日歷史百分位、≤panel）——β2 亦需此中間量
        if want & {"pb_self_pctile_252d", BETA2_INTERACT}:
            pdate = pd_ if hasattr(pd_, "year") else None
            for sid in pb:
                hist = [v for (d, v) in pbr_by_stock.get(sid, []) if (d <= pd_ if pdate is None else d <= pdate)]
                if len(hist) >= 60:
                    win = hist[-252:]
                    cur_v = win[-1]
                    pct = float(np.mean([1.0 if x <= cur_v else 0.0 for x in win]))
                    pctile[sid] = pct
                    if "pb_self_pctile_252d" in want:
                        rows.append((pd_, sid, "pb_self_pctile_252d", round(pct, 6)))
        if "inst_govbank_divergence" in want:
            zi, zg = _zscore(inst), _zscore(gov)
            for sid in set(zi) & set(zg):
                rows.append((pd_, sid, "inst_govbank_divergence", round(zi[sid] - zg[sid], 6)))
        if BETA2_INTERACT in want and pctile and dv:
            for sid, val in _interact_z(pctile, dv).items():
                rows.append((pd_, sid, BETA2_INTERACT, round(val, 6)))
        if rows:
            with db.transaction(conn) as cur:
                execute_values(
                    cur,
                    f"INSERT INTO {FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                    f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value",
                    rows)
            written += len(rows)
        if progress:
            progress(f"  候選 {pd_}: +{len(rows)} 值（累計 {written}）")
    return written


def clear_candidates(conn, features=None):
    """移除候選列（五鏡未過 → 不留 staging；不入生產之清理）。回刪除列數。

    features: 可選只清所列名；預設清全部 CANDIDATES。
    """
    ensure_candidate_table(conn)
    feats = list(features) if features is not None else list(CANDIDATES)
    with db.transaction(conn) as cur:
        cur.execute(f"DELETE FROM {FEATURE_TABLE} WHERE feature = ANY(%s)", (feats,))
        return cur.rowcount


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # _zscore 純函式紅綠（cutoff-free、母體 std）
    chk("z: <3 元素→空", _zscore({"a": 1.0, "b": 2.0}) == {})            # 樣本不足
    chk("z: 零變異→空", _zscore({"a": 5.0, "b": 5.0, "c": 5.0}) == {})   # sd=0
    z = _zscore({"a": 1.0, "b": 2.0, "c": 3.0})                          # mean=2, popstd=√(2/3)
    chk("z: 中位→0", abs(z["b"]) < 1e-9)
    chk("z: 端值對稱", abs(z["a"] + z["c"]) < 1e-9)
    chk("z: 端值量值", abs(z["c"] - 1.2247448713915890) < 1e-6)
    # β2 交互純函式
    inter = _interact_z({"a": 1.0, "b": 2.0, "c": 3.0}, {"a": 3.0, "b": 2.0, "c": 1.0})
    chk("interact: 兩側皆有鍵", set(inter) == {"a", "b", "c"})
    chk("interact: 中位×中位→0", abs(inter["b"]) < 1e-9)
    chk("interact: 端值異號積為負", inter["a"] < 0 and inter["c"] < 0)
    # 結構斷言（常數 + 公開入口）
    chk("CANDIDATES 含 β2 名", BETA2_INTERACT in CANDIDATES and len(CANDIDATES) == 5)
    chk("生產表唯讀口徑", PROD_TABLE == "feature_values" and FEATURE_TABLE == "feature_candidate_values")
    chk("公開入口存在", all(callable(globals().get(n)) for n in
                       ("compute_candidates", "ensure_candidate_table", "clear_candidates", "_interact_z")))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.audit.feature_candidate --selftest;免 DB 免 API)")
