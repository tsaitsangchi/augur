#!/usr/bin/env python
"""augur 總經 series sync — 把 features/macro.py 宣告的 FRED 因子落地 fred_series（含 PIT vintage）+ 重探 catalog。

🎯 這支在做什麼（白話）：讀 features/macro.py 的 series 清單與 vintage_map（單一真源），逐檔抓 FRED 全史
落地 fred_series——Tier B（月/季/週、會被回溯修訂）走 ALFRED vintage 存各版真 realtime_start（point-in-time，
#8）、Tier A（每日市場、不修訂）存最新值且 realtime_start＝觀測日；落地後重探 catalog 之 fred_series 元資料，
令 dataset_catalog / column_catalog 對齊新 schema（含 realtime_start 欄）。

組合根：在此把 feature 層決策（macro 清單）接上 ingestion 引擎（sync_fred）——sync 不反相依 feature（#3 層次）。
⚠️ 首次須 fred_series 已是含 realtime_start 主鍵之新 schema；舊表（PK 僅 series_id+date）須先一次性 DROP 重建，
否則既有 PK 被沿用、Tier B 多版會於 ON CONFLICT 互相覆蓋（#6 ensure_table 沿用既有 PK）。重建後本支可冪等重跑。
放量（#17）：每檔 1 call（vintage 全 realtime 一次回），經 fred.py 退避；FRED 限速寬、非 IP 敏感。

守 #8（Tier B vintage＝anti-leakage PIT）· #4（總經日級真兆）· #3（清單在 features/macro、引擎不持）· #6（冪等可重跑）。

用法：PYTHONPATH=src python scripts/sync_macro.py                （全 31 檔 + 重探 catalog）
      PYTHONPATH=src python scripts/sync_macro.py --no-catalog   （只 sync、不重探 catalog）
"""
import argparse

from augur import catalog
from augur.core import db, schema
from augur.features import macro
from augur.ingestion import sync


def main():
    ap = argparse.ArgumentParser(description="sync features/macro.py 宣告之 FRED 總經 series（PIT vintage）")
    ap.add_argument("--no-catalog", action="store_true", help="只 sync fred_series、跳過 catalog 重探")
    args = ap.parse_args()

    series = macro.series_ids()
    vmap = macro.vintage_map()
    n_b = sum(1 for v in vmap.values() if v)
    print(f"FRED 總經 sync：{len(series)} 檔（Tier A {len(series) - n_b} / Tier B vintage {n_b}）")

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            schema.bootstrap_infra(cur)   # data_audit_log 等 infra log 表（sync_fred 經 ingest 寫稽核需之，憲章 PHASE 1）
        res = sync.sync_fred(conn, series, vintage_map=vmap, progress=print)
        print(f"落地完成：{res['rows']:,} 列 / {res['series']} series → {res['table']}")
        if not args.no_catalog:
            print("重探 catalog（fred_series 元資料對齊新 schema）…")
            cres = catalog.build(conn, datasets=["fred_series"], progress=print)
            print(f"catalog 重探完成：{cres}")


if __name__ == "__main__":
    main()
