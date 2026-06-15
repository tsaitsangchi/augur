"""augur 核心股選拔 — 純完整度 gate（核心 ＝ 全部 source-pure 完整股，無評分、無排名）。

這支在做什麼（白話）：核心股 ＝ 在**所有指定面板**都備齊「**全部 canonical 特徵**」的股。
**只看完整度，不評分、不排名、無上限**（#10 質>量：核心可以少、不以數量為目標）。任一面板任一特徵
缺值（缺列）即排除——pan-historical 完整度關。

兩道完整度關（隱含）：
- raw-complete：無 raw → 算不出特徵 → 該股根本不在 feature_values → 自然排除。
- feature-complete：在所有 panel 都有全部 canonical 特徵之股才入核心。

canonical 特徵集**由資料判定**（取面板內最大特徵集，反硬編 §0.0-I 精神）——不寫死特徵數。

邊界：不算特徵、不訓練、**不評分排名**（無 CoreScore / 無 top-N 上限）；selection 唯一判準＝資料完整
（source-pure）。自建 core_universe 表（自建 DDL，CREATE IF NOT EXISTS）。

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


def bootstrap(cur):
    """建 core_universe 表（自建 DDL，冪等）。"""
    cur.execute(DDL)


def canonical_features(cur, panel_dates):
    """canonical 特徵集 = 面板內出現過之全部 distinct 特徵（由資料判定，反硬編）。"""
    cur.execute(f"SELECT DISTINCT feature FROM {FEATURE_TABLE} WHERE panel_date = ANY(%s)", (list(panel_dates),))
    return sorted(r[0] for r in cur.fetchall())


def build_universe(conn, panel_dates, *, features=None):
    """純完整度 gate：在**所有** panel 都備齊**全部** canonical 特徵之股 → 核心（無評分排名）。commit 新快照。

    回 {core(數量), panels, canonical_features, stock_ids}。
    """
    panel_dates = list(panel_dates)
    with db.transaction(conn) as cur:
        bootstrap(cur)
        feats = sorted(features) if features else canonical_features(cur, panel_dates)
        required = len(panel_dates) * len(feats)
        # 完整度 gate：每股在 (panel × feature) 之 present 數 == required → 全 panel 全特徵齊（無缺列）
        cur.execute(
            f"SELECT stock_id FROM {FEATURE_TABLE} "
            f"WHERE panel_date = ANY(%s) AND feature = ANY(%s) "
            f"GROUP BY stock_id HAVING count(*) = %s ORDER BY stock_id",
            (panel_dates, feats, required))
        core = [r[0] for r in cur.fetchall()]
        cur.execute(f"DELETE FROM {CORE_TABLE}")          # commit 新快照（取代舊核心名單）
        if core:
            execute_values(
                cur,
                f"INSERT INTO {CORE_TABLE} (stock_id, panels, features) VALUES %s",
                [(s, len(panel_dates), len(feats)) for s in core])
    return {"core": len(core), "panels": len(panel_dates),
            "canonical_features": len(feats), "stock_ids": core}
