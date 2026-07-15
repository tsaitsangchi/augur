#!/usr/bin/env python
"""🎯 dataset_catalog 加 attestation_mode + finalize_lag_days 欄＋seed——#7 對帳分類感知(hugo 2026-07-14 拍板 (a)+(b)):

(a) 滾動安全邊緣:對帳窗上限=today−finalize_lag_days(未定稿邊緣日排除;外盤/夜盤/T+1 發布類 lag=2)。
(b) 分類感知 attestation_mode:'byte'(預設,byte-equal)/'snapshot'(名錄快照型:API 僅返現況宇宙、
    DB 為 as-of 保存=反倖存者偏差之德,byte-equal 結構性不適用→豁免並誠實列印)/'restating'
    (重述型:PriceAdj 除權息季全序列重算,凍結比對天生誤報→豁免註記)/'coverage'(新聞流:
    逐條 byte 不適用,走 reconcile_coverage 量級對帳)。
根因實證(2026-07-14 audit FAIL 鑑識):EX 84,996 之 94%=roster-scoped 名錄被 by-date 端點對帳(端點錯配
假 EX)+快照語意;VM 3,760 主力=外盤時差半成品(UK 3,451);詳 HANDOFF §4.2。分類=策展資料住 DB(#29b)。

守 #29b(分類住 DB 非寫死)· #12(單一 SSOT)· #6(冪等 ADD COLUMN IF NOT EXISTS)· #7(對帳判準,hugo 拍板)。

執行指令矩陣:
  python scripts/migrate_attestation_catalog_ddl.py            # 印現況(欄存在否/現值),不動 DB
  python scripts/migrate_attestation_catalog_ddl.py --migrate  # 冪等建欄+seed
  python scripts/migrate_attestation_catalog_ddl.py --check    # 同無參數(唯讀)
⚠ DDL 於 audit/長跑對帳進行中勿跑(#30 鎖風暴);現 audit 已終態停跑、可執行。
"""
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# seed=證據+性質為據(2026-07-14 對帳 FAIL 鑑識;未列者維持預設 byte/lag=1、觀察續跑再定):
SNAPSHOT = ("TaiwanStockInfoWithWarrant", "TaiwanStockInfoWithWarrantSummary",
            "TaiwanStockIndustryChain", "USStockInfo", "UKStockInfo", "JapanStockInfo",
            "EuropeStockInfo", "IndiaStockInfo")          # 名錄快照型(API 現況宇宙)
RESTATING = ("TaiwanStockPriceAdj",                        # 除權息季全序列重算(機制確定)
             "TaiwanStockDividend")                        # 股利公告會被 TWSE 修訂(金額/除息日;date=未來除息日)——2026-07-14 attest VM=1 實證,hugo 拍板 restating
COVERAGE = ("TaiwanStockNews",)                            # 新聞流(增刪/去重,逐條 byte 不適用)
CADENCE = ("TaiwanBusinessIndicator",                      # 月頻(每月1日);滾動14日窗常空非死→#29 假綠 blocker 之低頻誠實豁免
           "TaiwanStockParValueChange",                    # 事件稀疏(面額變更、月-年間隔);hugo 2026-07-14 拍板 cadence 豁免
           "TaiwanSecuritiesTraderInfo",                   # 不規則(~雙週)券商資訊;hugo 2026-07-14 一併 cadence
           "TaiwanStockDelisting")                         # 事件(下市、週-月間隔);hugo 2026-07-14 一併 cadence
DIM_ONLY = ("USStockPrice",)                               # 維度端點專屬:by-date 回 PK-null 髒列不可 sync、零預測用途→豁免 byte attest(#31;hugo 2026-07-14 (b) exempt、不 per-ticker 放量)
LAG2 = ("TaiwanFuturesSpreadTick",                         # 期貨夜盤跨日
        "TaiwanFuturesDealerTradingVolumeDaily")           # T+1 發布
LAG3 = ("UKStockPrice", "EuropeStockPrice", "JapanStockPrice", "USStockPrice",
        "IndiaStockPrice")                                 # 外盤:時差+全球化/天災延遲發布餘裕(hugo 2026-07-14 拍板 2→3)


def status(cur):
    cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_name='dataset_catalog' "
                "AND column_name IN ('attestation_mode','finalize_lag_days')")
    has = cur.fetchone()[0] == 2
    vals = []
    if has:
        cur.execute("SELECT dataset, attestation_mode, finalize_lag_days FROM dataset_catalog "
                    "WHERE attestation_mode <> 'byte' OR finalize_lag_days <> 1 ORDER BY dataset")
        vals = cur.fetchall()
    return has, vals


def main():
    migrate = "--migrate" in sys.argv or "--run" in sys.argv
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            has, vals = status(cur)
            print(f"attestation 欄: {'存在' if has else '未建'}; 非預設列: "
                  + ("; ".join(f"{d}={m}/lag{g}" for d, m, g in vals) if vals else "(無)"))
            if not migrate:
                print("(唯讀;--migrate 才建欄+seed)")
                return 0
            cur.execute("ALTER TABLE dataset_catalog ADD COLUMN IF NOT EXISTS attestation_mode "
                        "varchar(12) NOT NULL DEFAULT 'byte' "
                        "CHECK (attestation_mode IN ('byte','snapshot','restating','coverage','cadence','dim_only'))")
            # 冪等更新 CHECK 值域:現機欄已存→ADD COLUMN IF NOT EXISTS 不改既有 CHECK,明確 drop+add 補 'cadence'
            # (2026-07-14 cadence 豁免入 catalog;R1 教訓:live 值域須由 repo migration 重現、非手動 ALTER)
            cur.execute("ALTER TABLE dataset_catalog DROP CONSTRAINT IF EXISTS dataset_catalog_attestation_mode_check")
            cur.execute("ALTER TABLE dataset_catalog ADD CONSTRAINT dataset_catalog_attestation_mode_check "
                        "CHECK (attestation_mode IN ('byte','snapshot','restating','coverage','cadence','dim_only'))")
            cur.execute("ALTER TABLE dataset_catalog ADD COLUMN IF NOT EXISTS finalize_lag_days "
                        "smallint NOT NULL DEFAULT 1 CHECK (finalize_lag_days BETWEEN 0 AND 7)")
            for mode, datasets in (("snapshot", SNAPSHOT), ("restating", RESTATING),
                                   ("coverage", COVERAGE), ("cadence", CADENCE), ("dim_only", DIM_ONLY)):
                cur.execute("UPDATE dataset_catalog SET attestation_mode=%s WHERE dataset = ANY(%s)",
                            (mode, list(datasets)))
                print(f"  seed {mode}: {cur.rowcount} 列")
            cur.execute("UPDATE dataset_catalog SET finalize_lag_days=2 WHERE dataset = ANY(%s)", (list(LAG2),))
            print(f"  seed lag=2: {cur.rowcount} 列")
            cur.execute("UPDATE dataset_catalog SET finalize_lag_days=3 WHERE dataset = ANY(%s)", (list(LAG3),))
            print(f"  seed lag=3: {cur.rowcount} 列")
        with db.transaction(conn) as cur:
            has, vals = status(cur)
            print("完成; 非預設列: " + "; ".join(f"{d}={m}/lag{g}" for d, m, g in vals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
