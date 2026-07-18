#!/usr/bin/env python
"""prediction serving 版本伴生表 schema 遷移 — prediction_serving_log(AUD-08;KS.41 A1)。

🎯 這支在做什麼(白話):落地 prediction_values 之 **append-only serving 版本伴生表**——每次 predict() 出單
   時,除既有 prediction_values 寫入外,另 append 一列(serving_run_id/created_at/git_sha/superseded_by),
   保存「系統在某時刻實際對人提出過什麼建議」,使**已呈現建議不可被無痕取代、過去認識狀態可 as-of 重建**
   (KS.41 A1 transaction-time append-only)。
   **既有 prediction_values(PK/DELETE+INSERT 主路徑)本輪完全不動**(不破 advisor/風控消費者);
   prediction_values 改為此表之衍生 current 視圖列為 follow-up Phase 4;predict_asof.py 出單同交易 append
   serving_log 亦為 follow-up(本輪僅落地伴生表 + 寫入不由本腳本觸)。
   **append-only 硬化**:BEFORE UPDATE(除 superseded_by 標記外欄位不可變)|DELETE|TRUNCATE RAISE +
   REVOKE FROM PUBLIC + 表級能力 COMMENT 宣告(A1)。全部 IF NOT EXISTS / CREATE OR REPLACE、重跑零副作用。

守 #6(冪等)· #12(DDL 單一住所)· #29· KS.40(雙時間承接)· KS.41(A0 禁止型態→至少 A1 append-only)·
   KS.42(表級能力宣告)· P4.E2。

執行指令矩陣:
  python scripts/migrate_prediction_serving_ddl.py            # 冪等執行 DDL + 印驗證清單
  python scripts/migrate_prediction_serving_ddl.py --check    # 唯讀:只印驗證清單、不執行 DDL
  python scripts/migrate_prediction_serving_ddl.py --selftest  # 紅綠鎖(DDL 結構不變式;免 DB 免 API)

⚠ 未 apply 生產 DB:須經人類 #7 實測、#19 檢視、P5 拍板後 apply、併 main。既有 prediction_values /
   migrate_prediction_ddl.py 完全不動——本表為伴生、風險隔離。owner 殘餘風險同 raw_supersede。
"""
import argparse
import sys

import _bootstrap  # noqa: F401

# `from augur.core import db`(→psycopg2)延遲至 main() 內,使 --selftest 零依賴可個別跑(#29)。

DDL = [
    # append-only serving 版本伴生表(A1);複合 PK 含 serving_run_id(每次出單一版本);superseded_by nullable
    # (指向取代此版本之後續 serving_run_id;標記=UPDATE 唯一許可欄)。無 FK→model_registry(伴生歷史、避免
    # 與主路徑 prediction_values 之 FK 生命週期耦合;model_id 以文字保存)。
    ("table prediction_serving_log", """
        CREATE TABLE IF NOT EXISTS prediction_serving_log (
            serving_run_id text NOT NULL,
            panel_date     date NOT NULL,
            model_id       text NOT NULL,
            stock_id       text NOT NULL,
            score          double precision NOT NULL,
            rank           int NOT NULL,
            in_portfolio   boolean NOT NULL DEFAULT false,
            weight         double precision NOT NULL DEFAULT 0.0,
            created_at     timestamptz NOT NULL DEFAULT now(),
            git_sha        text,
            superseded_by  text,
            PRIMARY KEY (serving_run_id, panel_date, model_id, stock_id)
        )"""),
    ("index ix_serving_panel_model", """
        CREATE INDEX IF NOT EXISTS ix_serving_panel_model
          ON prediction_serving_log (panel_date, model_id)"""),
    ("index ix_serving_run", """
        CREATE INDEX IF NOT EXISTS ix_serving_run
          ON prediction_serving_log (serving_run_id)"""),
    # 表級能力宣告(KS.42):A1=transaction-time append-only。
    ("comment prediction_serving_log", """
        COMMENT ON TABLE prediction_serving_log IS
        'prediction_values append-only serving 版本伴生表(AUD-08;能力=A1 transaction-time append-only,KS.41/KS.42);保存系統某時刻實際對人提出之建議,已呈現建議不可被無痕取代(除 superseded_by 標記外欄位 immutable);prediction_values 主路徑本輪不動、衍生 current 視圖列 follow-up Phase 4'"""),
    ("revoke mutate from public", """
        REVOKE UPDATE, DELETE, TRUNCATE ON prediction_serving_log FROM PUBLIC"""),
    # append-only 硬化(A1):DELETE 一律拒;UPDATE 僅許標記 superseded_by(其餘欄位不可變=已呈現建議 immutable)。
    ("function prediction_serving_log_append_only", """
        CREATE OR REPLACE FUNCTION prediction_serving_log_append_only()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION
                  'prediction_serving_log 為 append-only(KS.41 A1):DELETE 遭拒;過去對人提出之建議不可抹除'
                  USING ERRCODE = 'raise_exception';
            END IF;
            IF ROW(NEW.serving_run_id, NEW.panel_date, NEW.model_id, NEW.stock_id, NEW.score,
                   NEW.rank, NEW.in_portfolio, NEW.weight, NEW.created_at, NEW.git_sha)
               IS DISTINCT FROM
               ROW(OLD.serving_run_id, OLD.panel_date, OLD.model_id, OLD.stock_id, OLD.score,
                   OLD.rank, OLD.in_portfolio, OLD.weight, OLD.created_at, OLD.git_sha) THEN
                RAISE EXCEPTION
                  'prediction_serving_log 為 append-only(KS.41 A1):除 superseded_by 標記外欄位不可變(已呈現建議不可被無痕取代)'
                  USING ERRCODE = 'raise_exception';
            END IF;
            RETURN NEW;
        END;
        $fn$"""),
    ("trigger trg_serving_append_only", """
        DROP TRIGGER IF EXISTS trg_serving_append_only ON prediction_serving_log;
        CREATE TRIGGER trg_serving_append_only
            BEFORE UPDATE OR DELETE ON prediction_serving_log
            FOR EACH ROW EXECUTE FUNCTION prediction_serving_log_append_only()"""),
    ("function prediction_serving_log_no_truncate", """
        CREATE OR REPLACE FUNCTION prediction_serving_log_no_truncate()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              'prediction_serving_log 為 append-only(KS.41 A1):TRUNCATE 一律禁止(整表抹除已呈現建議)'
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("trigger trg_serving_no_truncate", """
        DROP TRIGGER IF EXISTS trg_serving_no_truncate ON prediction_serving_log;
        CREATE TRIGGER trg_serving_no_truncate
            BEFORE TRUNCATE ON prediction_serving_log
            FOR EACH STATEMENT EXECUTE FUNCTION prediction_serving_log_no_truncate()"""),
]

VERIFY = [
    ("prediction_serving_log 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='prediction_serving_log'"),
    ("複合 PK", "SELECT string_agg(a.attname,', ' ORDER BY array_position(i.indkey, a.attnum)) FROM pg_index i JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) WHERE i.indrelid='prediction_serving_log'::regclass AND i.indisprimary"),
    ("append-only + no-truncate triggers", "SELECT string_agg(tgname,', ' ORDER BY tgname) FROM pg_trigger WHERE tgrelid='prediction_serving_log'::regclass AND NOT tgisinternal"),
    ("表級能力 COMMENT(A1)", "SELECT obj_description('prediction_serving_log'::regclass)"),
    ("PUBLIC 殘餘 mutate(應無 UPDATE/DELETE/TRUNCATE)", "SELECT COALESCE(string_agg(privilege_type,', '),'(無)') FROM information_schema.role_table_grants WHERE table_name='prediction_serving_log' AND grantee='PUBLIC'"),
    ("既有 prediction_values 仍在且未被動(不改既有表)", "SELECT to_regclass('prediction_values') IS NOT NULL"),
    ("現有列數", "SELECT count(*) FROM prediction_serving_log"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001
            print(f"  {label}: (查詢失敗:{e})")


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    labels = [lbl for lbl, _ in DDL]
    blob = "\n".join(sql for _, sql in DDL)
    tbl = dict(DDL)["table prediction_serving_log"]
    chk("CREATE TABLE IF NOT EXISTS(冪等新表型)",
        "CREATE TABLE IF NOT EXISTS prediction_serving_log" in tbl)
    chk("複合 PK(serving_run_id, panel_date, model_id, stock_id)",
        "PRIMARY KEY (serving_run_id, panel_date, model_id, stock_id)" in tbl)
    chk("serving 版本欄齊(serving_run_id/created_at/git_sha/superseded_by)",
        all(c in tbl for c in ("serving_run_id", "created_at", "git_sha", "superseded_by")))
    chk("無 FK→model_registry(伴生歷史、避免生命週期耦合)",
        "REFERENCES model_registry" not in blob)
    fn = dict(DDL)["function prediction_serving_log_append_only"]
    chk("append-only:DELETE RAISE", "TG_OP = 'DELETE'" in fn and "DELETE 遭拒" in fn)
    chk("append-only:UPDATE 除 superseded_by 外欄位不可變(ROW IS DISTINCT FROM 比對)",
        "IS DISTINCT FROM" in fn and "superseded_by" not in fn.split("ROW(NEW")[1].split("IS DISTINCT")[0])
    chk("掛 append-only + no-truncate trigger",
        "trigger trg_serving_append_only" in labels and "trigger trg_serving_no_truncate" in labels)
    chk("REVOKE UPDATE/DELETE/TRUNCATE FROM PUBLIC",
        "REVOKE UPDATE, DELETE, TRUNCATE ON prediction_serving_log FROM PUBLIC" in blob)
    chk("表級能力 COMMENT 宣告 A1", "A1 transaction-time append-only" in dict(DDL)["comment prediction_serving_log"])
    print("  DB 語義(DELETE/TRUNCATE RAISE、UPDATE 僅 superseded_by 放行):需 PG——備援環境 --check + 實測")
    print("自測:" + ("全通過 ✓(DDL 結構不變式綠;DB 語義需 PG)" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="prediction serving 伴生表 DDL 遷移(prediction_serving_log;冪等 + A1 append-only 硬化;既有 prediction_values 不動)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(DDL 結構不變式;免 DB 免 API)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    from augur.core import db  # 延遲載入(psycopg2 僅 DDL 執行/--check 需要)
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
