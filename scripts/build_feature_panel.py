#!/usr/bin/env python
"""augur 特徵面板 build — 呼叫 features.panel.build_panel 把 as-of 面板特徵寫入 feature_values（冪等可重跑）。

🎯 這支在做什麼（白話）：對指定 as-of 面板日（預設＝feature_values 既有全部 panel、即「重建現有面板」），
對全 roster（TaiwanStockInfo）逐股算特徵（價量 + 月營收 + 籌碼 + 估值）寫入 feature_values。新增特徵後重跑本支
即把新特徵補進既有面板（ON CONFLICT DO UPDATE、冪等）；算不出之特徵缺列（#1）。純 DB 計算、不放 API、可逆。

組合根：把 feature 層（panel.build_panel）接上薄 CLI；邏輯在 src、入口不放邏輯（#3 層次、CLAUDE #18）。

守 #1（算不出即缺列）· #6（冪等可重跑）· #8（panel 特徵 as-of ≤t）· #18（命名/標頭慣例）。

用法：PYTHONPATH=src python scripts/build_feature_panel.py                    （重建既有全部面板）
      PYTHONPATH=src python scripts/build_feature_panel.py --since 2014-01-01    （只建 ≥2014 之既有面板）
      PYTHONPATH=src python scripts/build_feature_panel.py --panels 2025-12-31,2025-09-30  （只建指定面板）
"""
import argparse

from augur.core import db
from augur.features import panel


def _panel_dates(cur, since, explicit):
    """面板日清單：--panels 顯式 > --since 過濾既有 > 全部既有（feature_values distinct）。"""
    if explicit:
        return sorted(explicit)
    sql = "SELECT DISTINCT panel_date FROM feature_values"
    params = ()
    if since:
        sql += " WHERE panel_date >= %s"
        params = (since,)
    cur.execute(sql + " ORDER BY panel_date", params)
    return [r[0] for r in cur.fetchall()]


def _roster(cur):
    """全 roster：TaiwanStockInfo 之 distinct stock_id（build_panel 自會跳過無價量列之股）。"""
    cur.execute('SELECT DISTINCT stock_id FROM "TaiwanStockInfo" ORDER BY stock_id')
    return [r[0] for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(description="build feature_values 面板（冪等可重跑）")
    ap.add_argument("--since", help="只建此日(含)以後之既有面板 YYYY-MM-DD")
    ap.add_argument("--panels", help="指定面板日(逗號分隔)，覆寫 --since/既有")
    args = ap.parse_args()
    explicit = [p.strip() for p in args.panels.split(",")] if args.panels else None

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            pds = _panel_dates(cur, args.since, explicit)
            roster = _roster(cur)
        if not pds:
            print("無面板可建（feature_values 空且未指定 --panels）")
            return
        print(f"build feature panel：{len(pds)} 面板 × {len(roster)} roster（{pds[0]}..{pds[-1]}）")
        total_v = total_s = 0
        for pd_ in pds:
            res = panel.build_panel(conn, pd_, roster)
            total_v += res["values"]
            total_s += res["stocks"]
            print(f"  ✓ {pd_}: {res['stocks']} 股、{res['values']} 值")
        print(f"完成：{len(pds)} 面板、累計 {total_s} 股次、{total_v:,} 值")


if __name__ == "__main__":
    main()
