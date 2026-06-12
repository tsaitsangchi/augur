#!/usr/bin/env python
"""augur schema 中文註解 — 把 table/column 中文名寫進 PostgreSQL COMMENT(冪等、可重跑)。

這支在做什麼(白話):掃 DB 既有表,逐表把中文名寫進 COMMENT——欄中文取自 schema catalog
(live API 取樣建檔之 reports/augur_generic_ingester_schema_catalog_*.md,「(文檔)」層)、
表中文與 FRED/infra 欄為 augur 金融釋義(「(augur 釋義)」層)。來源標記寫在 table comment,
column comment 保持乾淨中文。catalog 缺的欄不瞎補、列警告(#15 誠實)。

為什麼不用 /translation API:實證 2026-06-12——它只支援 12 dataset,且翻的是 row-value 科目
(type 值→「應付帳款」),非欄位名;欄名中文權威=官方文檔對照(catalog 已逐欄收錄)。

守 #2(只加 metadata、不動 API 原樣名稱)· #15(來源分層標記+缺則警告)· #12(catalog 為欄中文單一引用源)。
用法:PYTHONPATH=src venv/bin/python scripts/annotate_schema_comments.py
"""
import glob
import re

from psycopg2 import sql

from augur.core import db

# 表中文(augur 金融釋義;catalog 無表層中文 → 由 augur 命名、標記來源)
TABLE_ZH = {
    "TaiwanStockInfo": "台股名冊(上市櫃股票基本資料)",
    "TaiwanStockGovernmentBankBuySell": "官股銀行買賣超日報",
    "TaiwanStockBalanceSheet": "資產負債表",
    "TaiwanDailyShortSaleBalances": "融券與借券賣出日餘額",
    "TaiwanStockFinancialStatements": "綜合損益表",
    "fred_series": "FRED 總經序列觀測值",
    "data_audit_log": "資料稽核留痕(DB↔API 對帳 #7)",
    "pipeline_execution_log": "管線執行日誌",
}

# 非 FinMind 表之欄中文(augur 釋義;FinMind 表欄中文一律取 catalog,不在此維護)
OWN_COL_ZH = {
    "fred_series": {"series_id": "FRED 序列代碼", "date": "觀測日期", "value": "觀測值"},
    "data_audit_log": {
        "id": "流水號", "dataset": "資料集", "data_id": "資料維度代碼(股票/序列等)",
        "action": "動作(寫入/對帳等)", "rows": "列數", "logged_at": "記錄時間", "detail": "細節",
    },
    "pipeline_execution_log": {
        "id": "流水號", "task": "任務", "target": "目標(資料集/表)", "status": "狀態",
        "rows": "列數", "started_at": "開始時間", "ended_at": "結束時間", "detail": "細節",
    },
}

_SEC = re.compile(r"^### `(\w+)`", re.M)
_CAT = re.compile(r"^## ([A-G])\. (.+?)\s*$", re.M)
_ROW = re.compile(r"^\| \d+ \| `([^`]+)` \| [^|]+ \| ([^|]*?) \|", re.M)


def load_catalog():
    """最新 schema catalog → ({table: {col: 中文}}, {table: 類別});欄中文之單一引用源(#12)。"""
    path = sorted(glob.glob("reports/augur_generic_ingester_schema_catalog_*.md"))[-1]
    text = open(path, encoding="utf-8").read()
    col_zh, table_cat = {}, {}
    cats = [(m.start(), f"{m.group(1)}. {m.group(2)}") for m in _CAT.finditer(text)]
    secs = list(_SEC.finditer(text))
    for i, m in enumerate(secs):
        table = m.group(1)
        seg = text[m.end(): secs[i + 1].start() if i + 1 < len(secs) else len(text)]
        col_zh[table] = {c: z.strip() for c, z in _ROW.findall(seg) if z.strip()}
        table_cat[table] = next((c for pos, c in reversed(cats) if pos < m.start()), "")
    return path, col_zh, table_cat


def main():
    cat_path, col_zh, table_cat = load_catalog()
    print(f"catalog:{cat_path}({len(col_zh)} 表)")
    done_t = done_c = 0
    warn = []
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            cur.execute("SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position", (t,))
            cols = [r[0] for r in cur.fetchall()]
            own = OWN_COL_ZH.get(t)
            zh_map = own if own is not None else col_zh.get(t, {})
            src = "augur 釋義" if own is not None else "FinMind 官方文檔對照(catalog)"
            tzh = TABLE_ZH.get(t)
            tcomment = (f"{tzh}(表名中文:augur 釋義)|" if tzh else "") + \
                       (f"類別:{table_cat[t]}|" if table_cat.get(t) else "") + f"欄中文來源:{src}"
            cur.execute(sql.SQL("COMMENT ON TABLE {} IS {}").format(sql.Identifier(t), sql.Literal(tcomment)))
            done_t += 1
            for c in cols:
                zh = zh_map.get(c)
                if not zh:
                    warn.append(f"{t}.{c}")          # 無來源不瞎補(#15)
                    continue
                cur.execute(sql.SQL("COMMENT ON COLUMN {}.{} IS {}").format(
                    sql.Identifier(t), sql.Identifier(c), sql.Literal(zh)))
                done_c += 1
    print(f"完成:{done_t} 表 comment、{done_c} 欄 comment")
    if warn:
        print(f"⚠️ 無中文來源、未註解 {len(warn)} 欄(不瞎補):{warn}")


if __name__ == "__main__":
    main()
