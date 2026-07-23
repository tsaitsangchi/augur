"""augur 特徵候選計算 + 五鏡驗證底料 — 把相關性分析浮現之候選做成 as-of 安全特徵、供橫斷面 IC 驗。

🎯 這支在做什麼（白話）：依方法論母原則③（目標相對→特徵必相對化）把兩個潛力發現做成**正式特徵候選**,
寫進候選 staging 表 feature_candidate_values（核心股 × panel、as-of 安全),供 `feature_diagnostics` 五鏡橫斷面 rank IC 驗證:

1. PBR-value 強化（raw pb_ratio 之三層相對化,審查 G12/G13）：
   - `pb_xsec_rank`：同日橫斷面 percentile rank（0-1、低=便宜）
   - `pb_industry_demean`：pb − 產業內中位（TaiwanStockInfo.industry_category、同 panel）
   - `pb_self_pctile_252d`：當前 PBR 在自身 252 交易日歷史之百分位（0-1）
2. govbank×inst 背離交互（相關分析 govbank_net~inst_net −0.48）：
   - `inst_govbank_divergence`：橫斷面 z(institutional_net_buy_ratio_20d) − z(gov_bank_net_buy_60d)

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
CANDIDATES = ("pb_xsec_rank", "pb_industry_demean", "pb_self_pctile_252d", "inst_govbank_divergence")


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


def compute_candidates(conn, panel_dates, stocks, *, progress=None):
    """對 panel_dates × stocks 算 4 候選 → 寫候選 staging 表（ON CONFLICT 冪等）。回寫入列數。"""
    stocks = [str(s) for s in stocks]
    written = 0
    ensure_candidate_table(conn)
    # pb_self_pctile_252d 需自身 PBR 日序：一次抓全 stocks 全史,記憶體算（避免逐 panel N² 查）
    with db.transaction(conn) as cur:
        cur.execute('SELECT stock_id, date, "PBR"::float8 FROM "TaiwanStockPER" WHERE stock_id = ANY(%s) AND "PBR" IS NOT NULL ORDER BY stock_id, date',
                    (stocks,))
        per_rows = cur.fetchall()
        industry = _industry_map(cur, stocks)
    pbr_by_stock = {}
    for sid, d, v in per_rows:
        pbr_by_stock.setdefault(str(sid), []).append((d, float(v)))

    for pd_ in panel_dates:
        rows = []
        with db.transaction(conn) as cur:
            pb = _panel_feature(cur, pd_, "pb_ratio", stocks)                  # 橫斷面 PBR
            inst = _panel_feature(cur, pd_, "institutional_net_buy_ratio_20d", stocks)
            gov = _panel_feature(cur, pd_, "gov_bank_net_buy_60d", stocks)
        # 1) pb_xsec_rank（同日橫斷面 percentile）
        if len(pb) >= 3:
            s = pd.Series(pb).rank(pct=True)
            rows += [(pd_, k, "pb_xsec_rank", round(float(v), 6)) for k, v in s.items()]
            # 2) pb_industry_demean（產業內中位扣除）
            df = pd.DataFrame({"pb": pb}).assign(ind=lambda d: d.index.map(industry))
            med = df.groupby("ind")["pb"].transform("median")
            dem = (df["pb"] - med).dropna()
            rows += [(pd_, k, "pb_industry_demean", round(float(v), 6)) for k, v in dem.items()]
        # 3) pb_self_pctile_252d（自身 252 交易日歷史百分位、≤panel）
        pdate = pd_ if hasattr(pd_, "year") else None
        for sid in pb:                                                          # 只對有當期 PBR 之股
            hist = [v for (d, v) in pbr_by_stock.get(sid, []) if (d <= pd_ if pdate is None else d <= pdate)]
            if len(hist) >= 60:
                win = hist[-252:]
                cur_v = win[-1]
                pct = float(np.mean([1.0 if x <= cur_v else 0.0 for x in win]))
                rows.append((pd_, sid, "pb_self_pctile_252d", round(pct, 6)))
        # 4) inst_govbank_divergence（橫斷面 z 差）——需兩者皆有（govbank 2021-07+）
        zi, zg = _zscore(inst), _zscore(gov)
        for sid in set(zi) & set(zg):
            rows.append((pd_, sid, "inst_govbank_divergence", round(zi[sid] - zg[sid], 6)))
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


def clear_candidates(conn):
    """移除候選列（五鏡未過 → 不留 staging；不入生產之清理）。回刪除列數。"""
    ensure_candidate_table(conn)
    with db.transaction(conn) as cur:
        cur.execute(f"DELETE FROM {FEATURE_TABLE} WHERE feature = ANY(%s)", (list(CANDIDATES),))
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
    # 結構斷言（常數 + 公開入口）
    chk("CANDIDATES=4 皆 str", len(CANDIDATES) == 4 and all(isinstance(c, str) for c in CANDIDATES))
    chk("生產表唯讀口徑", PROD_TABLE == "feature_values" and FEATURE_TABLE == "feature_candidate_values")
    chk("公開入口存在", all(callable(globals().get(n)) for n in
                       ("compute_candidates", "ensure_candidate_table", "clear_candidates")))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.audit.feature_candidate --selftest;免 DB 免 API)")
