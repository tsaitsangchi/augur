"""augur 核心股選拔 — 純完整度 gate（核心 ＝ 全部 source-pure 完整股，無評分、無排名）。

這支在做什麼（白話）：核心股 ＝ 在**所有指定面板**都備齊「**全部 canonical 特徵**」的股、
且屬於**核心股候選空間**（真台股個股、非 ETF、非 roster 污染）。
**只看完整度，不評分、不排名、無上限**（#10 質>量：核心可以少、不以數量為目標）。任一面板任一特徵
缺值（缺列）即排除——pan-historical 完整度關。

兩道完整度關（隱含）+ 一道候選空間關：
- 候選空間（PHASE 6 前置定義）：真股票代碼（stock_id 數字開頭）∧ 非 ETF（industry_category 非 ETF 類）。
  - 排 ETF：被動指數追蹤（持有他股之組合）非個股預測對象、模型對 ETF 之相對強弱排序無實質意義。
  - 排污染：TaiwanStockInfo.stock_id 欄混入產業分類名（'Automobile' / 'Tourism'）+ 指數代號（'TAIEX' / 'TPEx'）
    等非股票項（roster 污染、實證 2026-06-24 PHASE 8 後處理發現 31 個污染項通過 gate）→ 結構性排除。
- raw-complete：無 raw → 算不出特徵 → 該股根本不在 feature_values → 自然排除。
- feature-complete：在所有 panel 都有全部 canonical 特徵之股才入核心。

canonical 特徵集**由資料判定**（取面板內最大特徵集，反硬編 §0.0-I 精神）——不寫死特徵數。

邊界：不算特徵、不訓練、**不評分排名**（無 CoreScore / 無 top-N 上限）；selection 唯一判準＝資料完整
（source-pure）+ 結構候選空間（真台股個股）。自建 core_universe 表（自建 DDL，CREATE IF NOT EXISTS）。

守 #1（只收 source-pure 完整股）· #10（質>量，可少、不評分不排名）· #5（型別）。
"""
from __future__ import annotations

from psycopg2.extras import execute_values

from augur.core import db
from augur.features.panel import FEATURE_TABLE

CORE_TABLE = "core_universe"
DDL = f"""
CREATE TABLE IF NOT EXISTS {CORE_TABLE} (
    stock_id     VARCHAR(255) PRIMARY KEY,
    panels       INTEGER NOT NULL,
    features     INTEGER NOT NULL,
    committed_at TIMESTAMP NOT NULL DEFAULT now()
)"""

# as-of 快照表（point-in-time 核心）:每個 as_of_date 一份「截至當日完整度核心」名單（#8 消 survivorship）
ASOF_TABLE = "core_universe_asof"
DDL_ASOF = f"""
CREATE TABLE IF NOT EXISTS {ASOF_TABLE} (
    as_of_date   DATE NOT NULL,
    stock_id     VARCHAR(255) NOT NULL,
    panels       INTEGER NOT NULL,
    features     INTEGER NOT NULL,
    committed_at TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (as_of_date, stock_id)
)"""

# build 參數出處表（provenance）—— 每次 build 寫一列,使「這批核心股用什麼參數產生」可考、可精確重現
# （解 2026-06-29 痛點:dump 成品之 core_universe 參數不可考。append 歷史、最新列＝當前快照之參數）
META_TABLE = "core_universe_build_meta"
DDL_META = f"""
CREATE TABLE IF NOT EXISTS {META_TABLE} (
    build_id            SERIAL PRIMARY KEY,
    committed_at        TIMESTAMP NOT NULL DEFAULT now(),
    scope               VARCHAR(16) NOT NULL,        -- 'pan_hist' | 'asof'
    panel_start         DATE NOT NULL,
    panel_end           DATE NOT NULL,
    panel_count         INTEGER NOT NULL,
    liquidity_pct       DOUBLE PRECISION,            -- 流動性下界百分位（NULL=不過濾）
    liquidity_threshold DOUBLE PRECISION,            -- 算出之 dollar_volume_log_20d 閾值（asof=最新 panel）
    conditional         TEXT,                         -- conditional 設定序列化（如 monthly_revenue_yoy=金融保險業|金控業）
    feat_count          INTEGER NOT NULL,
    feat_list           TEXT NOT NULL,               -- universal 特徵清單（逗號;使「用哪些 feat」可考）
    core_count          INTEGER NOT NULL             -- 產出核心股數（asof=最新 panel）
)"""

# 候選空間定義（PHASE 6 前置;結構性排除、非完整度判定）—— 非 ETF、真台股個股代碼
# ETF industry_category 全集（TaiwanStockInfo 實證 2026-06-24:'ETF' 261+'上櫃指數股票型基金(ETF)' 125+'上櫃ETF' 119=505 檔）
ETF_INDUSTRY = ("ETF", "上櫃指數股票型基金(ETF)", "上櫃ETF")
# 真股票代碼 SQL predicate:數字開頭（純數字 1101 / ETF 風格 00631L / 特別股 01005T / 含字母 2882B 皆通過；
# roster 污染如 'Automobile' / 'TAIEX' / 'Tourism' 純字母開頭排除）
_REAL_STOCK_PREDICATE = "stock_id ~ '^[0-9]'"


def bootstrap(cur):
    """建 core_universe + build_meta 表（自建 DDL，冪等）。"""
    cur.execute(DDL)
    cur.execute(DDL_META)


def _conditional_str(conditional):
    """conditional dict 序列化為可考字串（如 monthly_revenue_yoy=金融保險業|金控業;None→None）。"""
    if not conditional:
        return None
    return ";".join(f"{k}={'|'.join(v)}" for k, v in conditional.items())


def _write_build_meta(cur, scope, pds, feats, liquidity_pct, liquidity_threshold, conditional, core_count):
    """寫 build 出處列（參數可考、可精確重現;append 歷史、最新列＝當前快照）。"""
    cur.execute(DDL_META)
    cur.execute(
        f"INSERT INTO {META_TABLE} (scope, panel_start, panel_end, panel_count, "
        f"liquidity_pct, liquidity_threshold, conditional, feat_count, feat_list, core_count) "
        f"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (scope, min(pds), max(pds), len(pds), liquidity_pct, liquidity_threshold,
         _conditional_str(conditional), len(feats), ",".join(feats), core_count))


def canonical_features(cur, panel_dates):
    """canonical 特徵集 = 面板內出現過之全部 distinct 特徵（由資料判定，反硬編）。"""
    cur.execute(f"SELECT DISTINCT feature FROM {FEATURE_TABLE} WHERE panel_date = ANY(%s)", (list(panel_dates),))
    return sorted(r[0] for r in cur.fetchall())


def _select_core(cur, panel_dates, feats, *, liquidity_pct=None, conditional=None):
    """完整度 + 候選空間 gate 純查詢 → (core stock_ids, extra)。供 build_universe / build_universe_asof 共用。

    候選空間（真台股個股 ∧ 非 ETF）∩ universal 全齊 ∩ conditional(豁免產業免/其他齊) ∩ 流動性(可選)。
    liquidity 以這批 panel 之 latest（max）為基準算分位（as-of 時即 t 當時流動性、point-in-time）。
    """
    panel_dates = list(panel_dates)
    cond = conditional or {}
    universal = [f for f in feats if f not in cond]   # 所有股必齊（conditional 特徵移出 universal、改條件式要求）
    # required = 實際可用 (panel, universal 特徵) 組合數（market-wide ≥1 股）——某特徵在某 panel 全市場 0 覆蓋
    # （如 gov_bank 早於源表 2021-07、缺列）不計入 required，避免「結構性不存在」誤殺核心或靜默 0-core
    # （審查 G9/R6：逐 panel 可用性，非 union 假設每 panel 皆有該特徵；HAVING count=available 仍要求股備齊所有「可用」格）。
    cur.execute(
        f"SELECT count(*) FROM (SELECT DISTINCT panel_date, feature FROM {FEATURE_TABLE} "
        f"WHERE panel_date = ANY(%s) AND feature = ANY(%s)) t", (panel_dates, universal))
    required = cur.fetchone()[0]
    extra = {"available_combos": required,
             "absent_combos": len(panel_dates) * len(universal) - required}   # #15 揭露結構性缺格、不靜默

    # E:流動性 gate(動態相對分位數、可選)——latest panel 之 dollar_volume_log_20d P(liquidity_pct) 為下界
    liq_filter, liq_params = "", []
    if liquidity_pct is not None:
        latest = max(panel_dates)
        cur.execute(
            "SELECT percentile_cont(%s) WITHIN GROUP (ORDER BY value) FROM feature_values "
            "WHERE panel_date=%s AND feature='dollar_volume_log_20d'",
            (liquidity_pct / 100.0, latest))
        thr = cur.fetchone()[0]
        extra["liquidity_threshold"] = float(thr) if thr is not None else None
        extra["liquidity_pct"] = liquidity_pct
        if thr is not None:
            liq_filter = (
                "AND EXISTS (SELECT 1 FROM feature_values lq "
                "WHERE lq.stock_id=fv.stock_id AND lq.panel_date=%s "
                "AND lq.feature='dollar_volume_log_20d' AND lq.value >= %s) ")
            liq_params = [latest, thr]

    # conditional gate:每個 conditional 特徵 → 屬豁免產業 OR 該特徵全 panel 齊（HAVING 後接、per-stock 子查詢）
    cond_filter, cond_params = "", []
    for feat, exempt in cond.items():
        cond_filter += (
            " AND (EXISTS (SELECT 1 FROM \"TaiwanStockInfo\" ci "
            "WHERE ci.stock_id=fv.stock_id AND ci.industry_category IN %s) "
            "OR (SELECT count(*) FROM feature_values cf WHERE cf.stock_id=fv.stock_id "
            "AND cf.panel_date=ANY(%s) AND cf.feature=%s)=%s) ")
        cond_params += [tuple(exempt), panel_dates, feat, len(panel_dates)]

    # 完整度 gate + 候選空間過濾:真股票代碼 ∧ 非 ETF ∧ 流動性 ∧ universal 全齊 ∧ conditional(豁免/齊)
    cur.execute(
        f"SELECT stock_id FROM {FEATURE_TABLE} fv "
        f"WHERE panel_date = ANY(%s) AND feature = ANY(%s) "
        f"  AND {_REAL_STOCK_PREDICATE} "                                       # 真股票代碼(排污染:產業名/指數名)
        f"  AND NOT EXISTS ("                                                   # 排 ETF
        f"    SELECT 1 FROM \"TaiwanStockInfo\" si "
        f"    WHERE si.stock_id = fv.stock_id AND si.industry_category IN %s) "
        f"  {liq_filter}"                                                       # E:流動性 gate(可選)
        f"GROUP BY stock_id HAVING count(*) = %s {cond_filter} ORDER BY stock_id",
        (panel_dates, universal, ETF_INDUSTRY, *liq_params, required, *cond_params))
    return [r[0] for r in cur.fetchall()], extra


def build_universe(conn, panel_dates, *, features=None, liquidity_pct=None, conditional=None):
    """核心 ＝ 候選空間（真台股個股、非 ETF）∩ universal 特徵全齊 ∩ conditional 特徵(豁免產業免/其他齊) ∩ 流動性；commit 新快照。

    `liquidity_pct`(0-100、預設 None=不過濾)：流動性下界（百分位）——以**最近 panel** 之
    `dollar_volume_log_20d` 全市場分布為基準算 percentile_cont 閾值，剔除低於該分位者。**動態相對分位數、不寫死值（#9）**。
    `conditional`: {feature: (exempt_industries,)} — 該特徵對指定產業**豁免完整度要求**（該產業結構性無此特徵、
    不因此誤排除：如月營收對金融保險業——金融業無月營收申報制度、靠財報）；非豁免產業仍須該特徵全 panel 齊。預設 None=全 universal。
    回 {core(數量), panels, canonical_features, stock_ids, liquidity_threshold(若有)}。**pan-historical 單名單**（含 look-ahead，
    嚴格 walk-forward 應改用 build_universe_asof）。
    """
    panel_dates = list(panel_dates)
    with db.transaction(conn) as cur:
        bootstrap(cur)
        feats = sorted(features) if features else canonical_features(cur, panel_dates)
        core, extra = _select_core(cur, panel_dates, feats, liquidity_pct=liquidity_pct, conditional=conditional)
        cur.execute(f"DELETE FROM {CORE_TABLE}")          # commit 新快照（取代舊核心名單）
        if core:
            execute_values(
                cur,
                f"INSERT INTO {CORE_TABLE} (stock_id, panels, features) VALUES %s",
                [(s, len(panel_dates), len(feats)) for s in core])
        _write_build_meta(cur, "pan_hist", panel_dates, feats, liquidity_pct,
                          extra.get("liquidity_threshold"), conditional, len(core))
    return {"core": len(core), "panels": len(panel_dates),
            "canonical_features": len(feats), "stock_ids": core, **extra}


def build_universe_asof(conn, panel_dates, *, features=None, liquidity_pct=None, conditional=None):
    """point-in-time 核心:逐 as-of 面板 t 用 ≤t 的 panels 算完整度核心 → 存 core_universe_asof（#8 消 survivorship）。

    每個 t 的核心 = 「在 [首panel, t] 所有 panel 都齊 canonical 特徵」之候選空間股——**只用 t 當時已知資訊**，
    不以「未來才知道完整」之 pan-historical 名單回填歷史（後者 = look-ahead，IC 會高估）。canonical 特徵集固定取全期
    （feats 跨全 panel_dates，與 M-1 可比），完整度則逐 t 用該 t 之子集判定。liquidity 用各 t 當時分位（point-in-time）。
    回 {as_of_date: core 數量}。
    """
    pds = sorted(panel_dates)
    summary = {}
    with db.transaction(conn) as cur:
        cur.execute(DDL_ASOF)
        feats = sorted(features) if features else canonical_features(cur, pds)
        cur.execute(f"DELETE FROM {ASOF_TABLE}")          # 重建全 as-of 快照
        last_extra = {}
        for i, t in enumerate(pds):
            sub = pds[: i + 1]                            # ≤ t 的 panels（point-in-time、不看未來）
            core, last_extra = _select_core(cur, sub, feats, liquidity_pct=liquidity_pct, conditional=conditional)
            if core:
                execute_values(
                    cur,
                    f"INSERT INTO {ASOF_TABLE} (as_of_date, stock_id, panels, features) VALUES %s",
                    [(t, s, len(sub), len(feats)) for s in core])
            summary[t] = len(core)
        if pds:                                           # 寫 build 出處（asof 用最新 panel 之閾值/核心數）
            _write_build_meta(cur, "asof", pds, feats, liquidity_pct,
                              last_extra.get("liquidity_threshold"), conditional, summary[pds[-1]])
    return summary
