#!/usr/bin/env python
"""augur 元資料 catalog 建置 — 探測 FinMind+FRED 全 dataset 填 dataset_catalog / column_catalog。

🎯 這支在做什麼（白話）：跑 `catalog.build()`，探測全 83 dataset + FRED 的「怎麼抓」元資料
（endpoint / 抓取模式 / data_id 來源 / 最早日 / 欄型別 / 排除 / reconcile_scope / 髒值…）落地 2
登錄表，成為後續所有 API 抓取的**權威依據**（更正確 / 更快 / 更省 token）。datasets_zh.md 可由表生成。
並順手 bootstrap 抓取要寫的 infra log 表（pipeline_execution_log / data_audit_log，憲章 PHASE 1）→ 換機一指令備齊全 infra。

⚠️ 放量（#17）：un-landed dataset 需 API 探測（含 earliest backward-probe）；landed 多為 DB 讀 + 少量
API；excluded（intraday / OUT_OF_UNIT）無探測。全程經 finmind 三層防護（_pace → _quota_gate → 403 冷卻）。
守 #18（探測持久化、非白名單）· #17（限速）· #15（provenance + last_verified）· #6（upsert 冪等、可重跑）。

用法：PYTHONPATH=src python scripts/build_catalog.py            （全 83 + FRED）
      PYTHONPATH=src python scripts/build_catalog.py --datasets TaiwanStockPrice,GoldPrice   （子集）
"""
import argparse

from augur.core import db, schema
from augur import catalog


def main():
    ap = argparse.ArgumentParser(description="探測 FinMind+FRED 填 metadata catalog（放量 #17）")
    ap.add_argument("--datasets", help="逗號分隔子集；省略＝全 sync.daily_datasets() + FRED")
    args = ap.parse_args()
    targets = args.datasets.split(",") if args.datasets else None
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            schema.bootstrap_infra(cur)   # 順手建抓取要寫的 infra log 表（憲章 PHASE 1）→ 換機一指令備齊全 infra
        result = catalog.build(conn, datasets=targets, progress=print)
    print(f"完成: {result}")


if __name__ == "__main__":
    main()
