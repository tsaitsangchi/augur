#!/usr/bin/env python3
"""🎯 建 `stock_graph_edge` 表——S3-WAVE-D 組 13（圖邊）之落點，供未來圖模型（GCN/GAT）之股票關係邊。

計畫 SSOT＝`reports/augur_s3_wave_d_sequence_graph_plan_20260804.md` §3.2（table schema 逐欄對照見該檔）。
邊型別閉集：`industry_same`（產業共群，`weight=1.0`）／`return_corr_60d`／`return_corr_120d`（報酬相關性，
`weight`=Pearson 相關係數）。主鍵 `(as_of_date, source_stock_id, target_stock_id, edge_type)`；
`source_stock_id < target_stock_id` 慣例避免無向邊雙存（由寫入端 `build_stock_graph_edges.py` 保證，
非 DB CHECK——CHECK 需字串比較兩欄，會排除合法邊，故留給應用層責任、DDL 僅留 comment 記錄慣例）。

守 #1（`n_obs`／`source_table` 溯源揭露）· #12（DDL 唯一住所，冪等 `IF NOT EXISTS`）· #30（`lock_timeout` 護欄）。

執行指令矩陣:
  python3 scripts/migrate_stock_graph_edge_ddl.py             # 無參數=印矩陣+--check（唯讀,DB 不可達則 graceful）
  python3 scripts/migrate_stock_graph_edge_ddl.py --check     # 唯讀:表是否存在、索引數、現有列數
  python3 scripts/migrate_stock_graph_edge_ddl.py --apply     # 建表（冪等;dump 期間禁跑 #30）
  python3 scripts/migrate_stock_graph_edge_ddl.py --selftest  # 紅綠自測（免 DB 免 API;壞變體驗紅 #35）
"""
from __future__ import annotations

import sys

import _bootstrap  # noqa: F401

TABLE = "stock_graph_edge"

DDL = f"""
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS {TABLE} (
    as_of_date        DATE         NOT NULL,
    source_stock_id   VARCHAR(255) NOT NULL,
    target_stock_id   VARCHAR(255) NOT NULL,
    edge_type         VARCHAR(32)  NOT NULL
        CHECK (edge_type IN ('industry_same', 'return_corr_60d', 'return_corr_120d')),
    weight            NUMERIC(9,6) NOT NULL,
    n_obs             INTEGER,
    source_table      VARCHAR(64)  NOT NULL,
    git_sha           VARCHAR(64),
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (as_of_date, source_stock_id, target_stock_id, edge_type)
);

CREATE INDEX IF NOT EXISTS ix_stock_graph_edge_source
    ON {TABLE} (as_of_date, source_stock_id);
CREATE INDEX IF NOT EXISTS ix_stock_graph_edge_target
    ON {TABLE} (as_of_date, target_stock_id);

COMMENT ON TABLE {TABLE} IS
  'S3-WAVE-D 組 13 圖邊快照（as-of 凍結、可稽核）——產業共群／報酬相關性邊；'
  'source_stock_id<target_stock_id 為寫入端慣例（避免無向邊雙存，非 DB 強制）；'
  '計畫 SSOT=reports/augur_s3_wave_d_sequence_graph_plan_20260804.md。'
  '非生產熱路徑（未接 train_ranker/predict_asof），staging 層比照 market_direction_feature 不掛 honesty guard。';
"""

EDGE_TYPES = ("industry_same", "return_corr_60d", "return_corr_120d")


def ddl_invariants(ddl: str) -> list[str]:
    """回傳被違反之不變式名清單（空=全守）。selftest 以本尊驗綠、壞變體驗紅（#35）。"""
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    if ddl.count(f"CREATE TABLE IF NOT EXISTS {TABLE}") != 1:
        bad.append("table_idempotent")
    if "PRIMARY KEY (as_of_date, source_stock_id, target_stock_id, edge_type)" not in ddl:
        bad.append("composite_pk")
    if not all(f"'{t}'" in ddl for t in EDGE_TYPES):
        bad.append("edge_type_values_present")
    if "CHECK (edge_type IN (" not in ddl:
        bad.append("edge_type_closed_set")
    if ddl.count("CREATE INDEX IF NOT EXISTS") != 2:
        bad.append("two_lookup_indexes")
    if "n_obs" not in ddl or "source_table" not in ddl:
        bad.append("provenance_columns")
    if "INSERT INTO" in ddl or "UPDATE " in ddl or "DELETE " in ddl:
        bad.append("ddl_must_not_write_data")
    return bad


def bootstrap(cur):
    cur.execute(DDL)


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        exists = bool(cur.fetchone()[0])
        print(f"  {'✓' if exists else '·'} table {TABLE} {'在' if exists else '不在（未 --apply）'}")
        if not exists:
            return 0
        cur.execute(
            "SELECT count(*) FROM pg_indexes WHERE tablename=%s AND indexname LIKE 'ix_stock_graph_edge_%%'",
            (TABLE,))
        print(f"  索引數：{cur.fetchone()[0]}/2")
        cur.execute(f"SELECT edge_type, count(*), count(DISTINCT as_of_date) FROM {TABLE} GROUP BY edge_type")
        rows = cur.fetchall()
        if rows:
            for et, n, nd in rows:
                print(f"  {et}: {n} 列（{nd} 個 as_of_date 快照）")
        else:
            print("  現有列數：0（表已建、尚未寫入——符合 Phase 2b 唯讀邊界）")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("驗紅:拿掉 lock_timeout → 報違",
        "lock_timeout" in ddl_invariants(DDL.replace("SET lock_timeout = '5s';\n\n", "")))
    chk("驗紅:拿掉複合主鍵 → composite_pk 報違",
        "composite_pk" in ddl_invariants(
            DDL.replace("PRIMARY KEY (as_of_date, source_stock_id, target_stock_id, edge_type)", "")))
    chk("驗紅:拿掉 edge_type 閉集 CHECK → 報違",
        "edge_type_closed_set" in ddl_invariants(
            DDL.replace("CHECK (edge_type IN ('industry_same', 'return_corr_60d', 'return_corr_120d'))", "")))
    chk("驗紅:少一個索引 → two_lookup_indexes 報違",
        "two_lookup_indexes" in ddl_invariants(
            DDL.replace(f"CREATE INDEX IF NOT EXISTS ix_stock_graph_edge_target\n    ON {TABLE} (as_of_date, target_stock_id);", "")))
    chk("驗紅:DDL 夾帶 INSERT → 報違（DDL 與資料寫入分離，Phase 2b 唯讀邊界）",
        "ddl_must_not_write_data" in ddl_invariants(DDL + f"\nINSERT INTO {TABLE} VALUES (1);"))
    chk("EDGE_TYPES 三型別與 DDL CHECK 一致",
        all(t in DDL for t in EDGE_TYPES) and len(EDGE_TYPES) == 3)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=f"{TABLE} DDL（S3-WAVE-D 組 13；冪等；--apply 建表不寫資料）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    no_args = not (a.check or a.apply)
    if no_args:
        print(__doc__.split("執行指令矩陣")[-1])
    from augur.core import db
    try:
        with db.connect() as conn:
            if a.apply:
                with db.transaction(conn) as cur:
                    bootstrap(cur)
                print("✓ DDL 冪等完成（建表+2 索引，零資料寫入）")
                return _check(conn)
            return _check(conn)
    except Exception as e:  # noqa: BLE001 — 無參數／--check 須 graceful 不裸 traceback（#29a）
        print(f"（需 DB；現不可達:{e};--selftest 免 DB 可跑）")
        return 0


if __name__ == "__main__":
    sys.exit(main())
