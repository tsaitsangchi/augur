#!/usr/bin/env python
"""augur schema 中文註解 — 把 table/column 中文名寫進 PostgreSQL COMMENT(冪等、可重跑)。

這支在做什麼(白話):掃 DB 既有表,逐表把中文名寫進 COMMENT——表/欄中文取自 DB catalog SSOT
(dataset_catalog.table_name_zh + column_catalog.column_name_zh/zh_source);catalog 未收錄之
augur infra 表(稽核/管線日誌)用 in-file augur 釋義。來源標記寫在 table comment,
column comment 保持乾淨中文。無中文來源的表/欄不瞎補——表跳過、欄列警告(#15 誠實)。

為什麼不用 /translation API:實證 2026-06-12——它只支援 12 dataset,且翻的是 row-value 科目
(type 值→「應付帳款」),非欄位名;欄名中文權威=官方文檔對照(已逐欄收錄進 column_catalog)。

守 #2(只加 metadata、不動 API 原樣名稱)· #15(來源分層標記+缺則警告)· #12(DB catalog 為表/欄中文單一引用源)。
執行指令矩陣:python scripts/annotate_schema_comments.py
"""
from psycopg2 import sql

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# infra 表中文 seed(#29b 整改 2026-07-13):本 dict 僅為 bootstrap 種子——每次執行先冪等 upsert 進
# dataset_catalog/column_catalog(excluded=true,source='infra' 防誤入 sync 選表路徑;build 實證不清手植列),
# 之後統一從 catalog 讀(單一 DB 路徑);新增 infra 表中文=直接 INSERT catalog、零改碼。
OWN_TABLE_ZH = {
    "data_audit_log": "資料稽核留痕(DB↔API 對帳 #7)",
    "pipeline_execution_log": "管線執行日誌",
}
OWN_COL_ZH = {
    "data_audit_log": {
        "id": "流水號", "dataset": "資料集", "data_id": "資料維度代碼(股票/序列等)",
        "action": "動作(寫入/對帳等)", "rows": "列數", "logged_at": "記錄時間", "detail": "細節",
    },
    "pipeline_execution_log": {
        "id": "流水號", "task": "任務", "target": "目標(資料集/表)", "status": "狀態",
        "rows": "列數", "started_at": "開始時間", "ended_at": "結束時間", "detail": "細節",
    },
}


def load_catalog(cur):
    """DB catalog → ({table: (表中文, 類別)}, {table: {col: (欄中文, zh_source)}});表/欄中文之單一引用源(#12)。"""
    cur.execute("SELECT dataset, table_name_zh, category FROM dataset_catalog")
    tables = {ds: (zh, cat) for ds, zh, cat in cur.fetchall()}
    cur.execute("SELECT dataset, column_name, column_name_zh, zh_source FROM column_catalog")
    cols = {}
    for ds, col, zh, src in cur.fetchall():
        if zh:
            cols.setdefault(ds, {})[col] = (zh, src or "")
    return tables, cols


def seed_infra_catalog(cur):
    """infra 表中文 seed → catalog 冪等 upsert(#29b:SSOT=DB、dict=種子)。excluded=true 防入 sync 選表。"""
    for t, zh in OWN_TABLE_ZH.items():
        cur.execute(
            "INSERT INTO dataset_catalog (dataset, table_name_zh, source, category, excluded, excluded_reason) "
            "VALUES (%s,%s,'infra','infra',true,'augur infra 表(非 API dataset;僅中文註記 seed,#29b)') "
            "ON CONFLICT (dataset) DO UPDATE SET table_name_zh=EXCLUDED.table_name_zh", (t, zh))
        cur.execute("DELETE FROM column_catalog WHERE dataset=%s", (t,))   # column_catalog 無唯一鍵→依 build 同慣例 DELETE+INSERT(#6 冪等)
        for i, (c, czh) in enumerate(OWN_COL_ZH.get(t, {}).items(), 1):
            cur.execute(
                "INSERT INTO column_catalog (dataset, column_name, ordinal, column_name_zh, zh_source) "
                "VALUES (%s,%s,%s,%s,'augur釋義')", (t, c, i, czh))


def main():
    done_t = done_c = 0
    warn, skipped = [], []
    with db.connect() as conn, db.transaction(conn) as cur:
        seed_infra_catalog(cur)                     # dict=seed → catalog;之後統一讀 catalog(單一 DB 路徑)
        cat_tables, cat_cols = load_catalog(cur)
        print(f"catalog:DB dataset_catalog/column_catalog({len(cat_tables)} datasets;infra seed 已 upsert)")
        cur.execute("SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            if t in cat_tables:
                tzh, tcat = cat_tables[t]
                zh_map = {c: z for c, (z, _) in cat_cols.get(t, {}).items()}
                srcs = "/".join(sorted({s for _, s in cat_cols.get(t, {}).values() if s}))
                tcomment = (f"{tzh}(表名中文:dataset_catalog)|" if tzh else "") + \
                           (f"類別:{tcat}|" if tcat else "") + \
                           f"欄中文來源:column_catalog(zh_source:{srcs or '未標'})"
            else:
                skipped.append(t)                # catalog 未收錄且非 augur infra 表:無來源不瞎補(#15)
                continue
            cur.execute("SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position", (t,))
            cols = [r[0] for r in cur.fetchall()]
            cur.execute(sql.SQL("COMMENT ON TABLE {} IS {}").format(sql.Identifier(t), sql.Literal(tcomment)))
            done_t += 1
            for c in cols:
                zh = zh_map.get(c)
                if not zh:
                    warn.append(f"{t}.{c}")      # 無來源不瞎補(#15)
                    continue
                cur.execute(sql.SQL("COMMENT ON COLUMN {}.{} IS {}").format(
                    sql.Identifier(t), sql.Identifier(c), sql.Literal(zh)))
                done_c += 1
    print(f"完成:{done_t} 表 comment、{done_c} 欄 comment")
    if skipped:
        print(f"跳過 {len(skipped)} 表(catalog 未收錄、無中文來源不瞎補):{skipped}")
    if warn:
        print(f"⚠️ 無中文來源、未註解 {len(warn)} 欄(不瞎補):{warn}")


if __name__ == "__main__":
    main()
