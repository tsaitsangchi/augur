#!/usr/bin/env python
"""本地模型行為評測之兩張表 — 凍結題庫 + 評測帳本(S0 修尺,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):舊評測器已實證失效(常數字串 0.654 > 現役 pack 0.492;事實敏感度 0%;
   評的是被截斷的思考鏈;「固定集」隨語料成長而漂移)。修法之地基＝把題庫**實體化凍結進 DB**
   (不再每次現算 md5 序、不再會漂),並把每次評測連同 set_id/eval_code_hash 寫進**帳本**——
   跨版本比較前先比 hash,不同即拒絕比較(fail-loud),杜絕「跨三把尺宣稱單調上升」。
   兩表皆掛誠實閘(DELETE/TRUNCATE 拒;UPDATE 須通行證),鏡射 migrate_honesty_guards_ddl.py。
守 #1(不補假分)· #9/#10(可溯源)· #12(改 writer 非手補)· #15(壞尺=假兆)· P4.E3(只失效不刪)· #29a/d。
執行指令矩陣:
  python scripts/migrate_local_model_eval_ddl.py            # 無參數:現況(唯讀:兩表存在?列數?閘?)
  python scripts/migrate_local_model_eval_ddl.py --apply    # 執行遷移(冪等)
  python scripts/migrate_local_model_eval_ddl.py --dry-run  # 只印 SQL、不動 DB
  python scripts/migrate_local_model_eval_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

GUC = "augur.honesty_write"
LAYERS = ("L1_RETRIEVED", "L2_NO_RETRIEVAL", "L3_ABSENT", "L4_AMBIG")
# v2 格名(EVALSET-V2-go,hugo 2026-07-28;對照孿生五格)——CHECK 放寬為 v1∪v2:
# v1 舊列仍合法(P4.E3 留檔不失效),v2 新格可入。SSOT=augur_evalset_v2_rebuild_plan_20260728.md §七。
CELLS_V2 = ("B1_FAITHFUL", "B2_NO_RETRIEVAL", "B3_AMBIGUITY", "C1_ZH_EXISTENCE", "C2P_ZH_PAIR")
TABLES = ("local_model_eval_item", "local_model_eval_run")

WIDEN_LAYER_CHECK = f"""
ALTER TABLE local_model_eval_item DROP CONSTRAINT IF EXISTS local_model_eval_item_layer_check;
ALTER TABLE local_model_eval_item ADD CONSTRAINT local_model_eval_item_layer_check
  CHECK (layer = ANY (ARRAY[{", ".join(f"'{x}'" for x in LAYERS + CELLS_V2)}]));
"""

SQL = f"""
CREATE TABLE IF NOT EXISTS local_model_eval_item (
    item_id          bigserial PRIMARY KEY,
    set_id           text NOT NULL,
    layer            text NOT NULL CHECK (layer = ANY (ARRAY[{", ".join(f"'{x}'" for x in LAYERS)}])),
    prompt           text NOT NULL,
    expect           jsonb NOT NULL,
    source_sample_id bigint,
    source_key       jsonb NOT NULL,
    gen_code_hash    text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS local_model_eval_item_uq
    ON local_model_eval_item (set_id, layer, md5(prompt));

CREATE TABLE IF NOT EXISTS local_model_eval_run (
    run_id         text PRIMARY KEY,
    set_id         text NOT NULL,
    eval_code_hash text NOT NULL,
    arm            text NOT NULL,
    model          text NOT NULL,
    n_items        int NOT NULL,
    n_valid        int NOT NULL,
    axis_f         numeric,
    axis_p         numeric,
    axis_a         numeric,
    is_invalid     boolean NOT NULL DEFAULT false,
    detail         jsonb NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS local_model_eval_run_set_idx ON local_model_eval_run (set_id, arm);

CREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION '% on % 遭誠實帳本閘拒絕:無合法路徑(N/凍結錨不可默改,#15)', TG_OP, TG_TABLE_NAME;
    END IF;
    IF TG_OP = 'UPDATE' AND coalesce(current_setting('{GUC}', true), '') <> 'on' THEN
        RAISE EXCEPTION 'UPDATE on % 遭拒:須經工具鏈(SET LOCAL {GUC}=''on'');裸手改寫=默改(#15)', TG_TABLE_NAME;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
"""

TRIG = """
DROP TRIGGER IF EXISTS {t}_honesty_row ON {t};
CREATE TRIGGER {t}_honesty_row BEFORE UPDATE OR DELETE ON {t}
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS {t}_honesty_stmt ON {t};
CREATE TRIGGER {t}_honesty_stmt BEFORE TRUNCATE ON {t}
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
"""


def _full_sql():
    return SQL + "".join(TRIG.format(t=t) for t in TABLES)


def apply(dry):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename = ANY(%s)",
                    (list(TABLES),))
        have = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'local_model_eval%_honesty%'")
        trigs = cur.fetchone()[0]
        cur.execute("""SELECT pg_get_constraintdef(oid) FROM pg_constraint
            WHERE conname='local_model_eval_item_layer_check'""")
        r = cur.fetchone()
        check_ok = bool(r) and all(f"'{c}'" in r[0] for c in CELLS_V2)
        if have == len(TABLES) and trigs >= 2 * len(TABLES) and check_ok:
            print(f"✓ 兩表、{trigs} 個誠實閘、v2 格 CHECK 皆在——冪等跳過"); return 0
        if dry:
            if have < len(TABLES):
                print(_full_sql())
            if not check_ok:
                print(WIDEN_LAYER_CHECK)
            print("(--dry-run:未執行)"); return 0
        if have < len(TABLES):
            cur.execute(_full_sql())
            print(f"✓ 遷移完成:{', '.join(TABLES)} + 誠實閘(DELETE/TRUNCATE 拒、UPDATE 須 {GUC})")
        if not check_ok:
            cur.execute(WIDEN_LAYER_CHECK)
            print(f"✓ layer CHECK 放寬為 v1∪v2({len(LAYERS)}+{len(CELLS_V2)} 格;舊列仍合法)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in TABLES:
            cur.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename=%s", (t,))
            if not cur.fetchone()[0]:
                print(f"  {t}: (未建)"); continue
            cur.execute(f"SELECT count(*) FROM {t}")  # noqa: S608  表名來自本檔常數
            cur.execute(f"SELECT count(*) FROM {t}")  # noqa: S608
            n = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass AND tgname LIKE %s",
                        (t, f"{t}_honesty%"))
            print(f"  {t}: {n} 列、誠實閘 {cur.fetchone()[0]} 個")
        cur.execute("SELECT set_id, count(*), min(layer)||'..'||max(layer) FROM local_model_eval_item "
                    "GROUP BY set_id ORDER BY 1")
        for sid, n, lay in cur.fetchall():
            print(f"    凍結集 {sid}: {n} 題({lay})")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    s = _full_sql()
    import re
    chk("凍結題庫表(set_id/layer/expect/gen_code_hash 齊)",
        "local_model_eval_item" in s and bool(re.search(r"expect\s+jsonb\s+NOT NULL", s))
        and all(k in s for k in ("set_id", "layer", "gen_code_hash")))
    chk("四層 CHECK 白名單", all(f"'{x}'" in s for x in LAYERS))
    chk("v2 五格入 CHECK 放寬式(v1∪v2;舊列仍合法)",
        all(f"'{x}'" in WIDEN_LAYER_CHECK for x in LAYERS + CELLS_V2))
    chk("放寬走 DROP+ADD 同名約束(冪等、單一住所)",
        "DROP CONSTRAINT IF EXISTS" in WIDEN_LAYER_CHECK and "ADD CONSTRAINT" in WIDEN_LAYER_CHECK)
    chk("同集同層同題 UNIQUE(冪等、防重複題)", "local_model_eval_item_uq" in s and "md5(prompt)" in s)
    chk("帳本記三軸+set_id+eval_code_hash(跨尺可辨)",
        all(k in s for k in ("axis_f", "axis_p", "axis_a", "eval_code_hash", "is_invalid")))
    chk("三軸各自成欄(結構上不可能被平均掉)", s.count("axis_") >= 3 and "axis_mean" not in s)
    chk("誠實閘:DELETE/TRUNCATE 拒", "TG_OP IN ('DELETE', 'TRUNCATE')" in s and "RAISE EXCEPTION" in s)
    chk("誠實閘:UPDATE 須通行證", GUC in s and "current_setting" in s)
    chk("兩表皆掛 row+statement 雙 trigger",
        all(f"{t}_honesty_row" in s and f"{t}_honesty_stmt" in s for t in TABLES))
    chk("CREATE IF NOT EXISTS(可重入)", s.count("CREATE TABLE IF NOT EXISTS") == len(TABLES))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="本地模型行為評測兩表遷移(凍結題庫+評測帳本)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
