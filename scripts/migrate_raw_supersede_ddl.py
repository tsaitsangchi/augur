#!/usr/bin/env python
"""raw_supersede_log schema 遷移 — AUD-02 補正：heal 覆寫前「被取代原值」快照帳本（冪等）。

🎯 這支在做什麼(白話):建立「被取代原值」append-only 帳本。現行 heal（reconcile.heal_by_date /
   daily_maintenance --heal）偵測到 value_mismatch（DB≠API，兩個不同時點 Observation 衝突）後，
   以同一 upsert 路徑把 DB 舊值原地覆寫為 API 現值——舊值一經 heal 即不可復原＝last-write-wins。
   本表在覆寫**前**把敗方(old_row) DB 現值＋勝方(new_row) incoming API 列＋裁決 provenance 快照留存，
   使「API wins」成為攜自身 Evidence 之新 Knowledge、衝突雙方共存、永不覆寫原始證據。

憲章依據:`AUGUR-MC v1.3 §P4.E5`(矛盾保存,MUST NOT last-write-wins,§8.4 不可豁免)、
   `§P4.E3`(只失效不刪除)、`§P4.E6`(provenance);`AUGUR-WM v1.0 §WM.16/§WM.30/§WM.34`。
   設計卷宗:docs/remediation/AUD-02-raw-supersede-log.md(決策 A=(a) 硬 trigger＋tombstone 例外)。

守 #6(冪等重跑安全)· #12(DDL 單一住所)· #15(每列 trace 回 attestation_run_id/reason)· CLAUDE #29。
   **本表為原始證據帳本**:append-only 由 DB trigger 硬性保證(決策 A);唯一得繞過之路徑為
   `tombstone_raw_supersede(id, reason)` 受控函式(P4.E3 法規強制抹除唯一例外:抹內容本體、留 tombstone＋provenance)。
   **被預測回讀隔離**:old_row（被取代舊值）落預測回讀屬 WM.35 消費閘破口→建表後須跑
   `setup_predict_role --apply`（本表已列入 FORBIDDEN，REVOKE from augur_predict）。

執行指令矩陣:
  python scripts/migrate_raw_supersede_ddl.py           # 冪等執行 DDL + 印驗證清單(安全預設)
  python scripts/migrate_raw_supersede_ddl.py --check   # 唯讀:只印驗證清單、不執行 DDL
  python scripts/migrate_raw_supersede_ddl.py --selftest # DDL 純文字結構自測(零 DB)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DDL = [
    ("table raw_supersede_log", """
        CREATE TABLE IF NOT EXISTS raw_supersede_log (
            id                 BIGSERIAL   PRIMARY KEY,
            "table"            TEXT        NOT NULL,
            pk                 JSONB       NOT NULL,
            old_row            JSONB       NOT NULL,
            new_row            JSONB       NOT NULL,
            superseded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            valid_time         DATE,
            reason             TEXT        NOT NULL,
            attestation_run_id BIGINT      REFERENCES attestation_result(id),
            note               TEXT
        )"""),
    ("index ix_supersede_table_time", """
        CREATE INDEX IF NOT EXISTS ix_supersede_table_time
          ON raw_supersede_log ("table", superseded_at)"""),
    ("index ix_supersede_run", """
        CREATE INDEX IF NOT EXISTS ix_supersede_run
          ON raw_supersede_log (attestation_run_id)"""),
    ("index ix_supersede_pk_gin", """
        CREATE INDEX IF NOT EXISTS ix_supersede_pk_gin
          ON raw_supersede_log USING GIN (pk)"""),
    # ── 決策 A=(a):append-only 硬 trigger（BEFORE UPDATE OR DELETE RAISE），使不可覆寫成機器可稽核保證（WM.34）。
    #    唯一例外:tombstone_raw_supersede() 於同交易 SET LOCAL augur.supersede_tombstone='on' 後之 UPDATE（抹內容、留 tombstone）。
    #    DELETE 一律禁止（即使法規抹除亦保留 tombstone 列）。custom GUC 以 current_setting(...,true) missing_ok 讀取。
    ("function raw_supersede_log_append_only", """
        CREATE OR REPLACE FUNCTION raw_supersede_log_append_only() RETURNS trigger AS $fn$
        BEGIN
          IF TG_OP = 'UPDATE'
             AND current_setting('augur.supersede_tombstone', true) = 'on' THEN
            RETURN NEW;   -- 受控 tombstone 路徑(P4.E3 法規抹除唯一例外;僅 row-level UPDATE)
          END IF;
          -- UPDATE/DELETE/TRUNCATE 一律擋（TRUNCATE 亦落此路徑；tombstone 例外不及於 DELETE/TRUNCATE）
          RAISE EXCEPTION 'raw_supersede_log append-only (AUD-02/AUGUR-MC P4.E5,§8.4 不可豁免);'
            ' UPDATE/DELETE/TRUNCATE 一律禁止;抹除僅得經 tombstone_raw_supersede(id,reason) 法規受控路徑';
        END;
        $fn$ LANGUAGE plpgsql"""),
    ("trigger raw_supersede_log_no_mutate", """
        DO $mig$ BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='raw_supersede_log_no_mutate'
                           AND tgrelid='raw_supersede_log'::regclass) THEN
            CREATE TRIGGER raw_supersede_log_no_mutate
              BEFORE UPDATE OR DELETE ON raw_supersede_log
              FOR EACH ROW EXECUTE FUNCTION raw_supersede_log_append_only();
          END IF;
        END $mig$"""),
    # M3（對抗審查）：row-level trigger 擋不住 TRUNCATE（PG TRUNCATE 不觸發 FOR EACH ROW）→ 整本證據帳可被一語句清空。
    # 補 statement-level BEFORE TRUNCATE trigger（共用同函式，TG_OP='TRUNCATE' 落 RAISE 分支），使決策 A 之 WM.34 硬保證真閉合。
    ("trigger raw_supersede_log_no_truncate", """
        DO $mig$ BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='raw_supersede_log_no_truncate'
                           AND tgrelid='raw_supersede_log'::regclass) THEN
            CREATE TRIGGER raw_supersede_log_no_truncate
              BEFORE TRUNCATE ON raw_supersede_log
              FOR EACH STATEMENT EXECUTE FUNCTION raw_supersede_log_append_only();
          END IF;
        END $mig$"""),
    # ── 決策 A 附帶義務:tombstone 法規抹除受控函式（P4.E3 唯一例外）。抹除 old_row/new_row 內容本體，
    #    但保留該列（tombstone）＋完整 provenance（原 reason/superseded_at/attestation_run_id 不動、note 追記抹除事由）。
    #    SET LOCAL 交易域內生效並於交易結束自動失效;抹後即刻改回 'off' 收緊，避免同交易後續 UPDATE 誤放行。
    ("function tombstone_raw_supersede", """
        CREATE OR REPLACE FUNCTION tombstone_raw_supersede(p_id BIGINT, p_reason TEXT)
        RETURNS void AS $fn$
        BEGIN
          IF p_reason IS NULL OR btrim(p_reason) = '' THEN
            RAISE EXCEPTION 'tombstone_raw_supersede: 法規抹除須具事由 p_reason（provenance 不得空）';
          END IF;
          SET LOCAL augur.supersede_tombstone = 'on';
          UPDATE raw_supersede_log
             SET old_row = jsonb_build_object('_tombstoned', true),
                 new_row = jsonb_build_object('_tombstoned', true),
                 note    = concat_ws(' | ', note,
                             'TOMBSTONE(法規強制抹除 P4.E3): ' || p_reason || ' @ ' || now()::text)
           WHERE id = p_id;
          SET LOCAL augur.supersede_tombstone = 'off';
        END;
        $fn$ LANGUAGE plpgsql"""),
    ("comment raw_supersede_log", """
        COMMENT ON TABLE raw_supersede_log IS
        'heal 覆寫前「被取代原值」快照帳本(AUD-02;P4.E5 衝突裁決留痕);每列＝一次 API-wins 裁決之新 Knowledge,同時指涉衝突敗方(old_row)＋勝方(new_row),攜自身 Evidence(attestation_run_id+reason);append-only(trigger 硬保證),永不覆寫原始證據;唯一抹除路徑 tombstone_raw_supersede()(P4.E3 法規例外);隔離不變式:REVOKE from augur_predict'"""),
    ("comment col old_row", """
        COMMENT ON COLUMN raw_supersede_log.old_row IS
        '敗方:upsert 前 DB 現值 pre-image(被取代之原始 Observation);與 new_row 同交易快照、口徑一致以利衝突重建'"""),
    ("comment col attestation_run_id", """
        COMMENT ON COLUMN raw_supersede_log.attestation_run_id IS
        '裁決 provenance(P4.E6);決策 B=(b) nullable＋事後回填:heal_by_date 直呼 sync 無對帳 run 時恆 NULL,溯源鏈由 reason＋old_row/new_row 承載、不因無 run_id 而斷'"""),
]

VERIFY = [
    ("raw_supersede_log 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='raw_supersede_log'"),
    ("FK → attestation_result", "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='raw_supersede_log'::regclass AND contype='f'"),
    ("索引", "SELECT string_agg(indexname,', ' ORDER BY indexname) FROM pg_indexes WHERE tablename='raw_supersede_log'"),
    ("append-only triggers（no_mutate+no_truncate）", "SELECT string_agg(tgname,', ' ORDER BY tgname) FROM pg_trigger WHERE tgrelid='raw_supersede_log'::regclass AND NOT tgisinternal"),
    ("tombstone 受控函式", "SELECT proname FROM pg_proc WHERE proname='tombstone_raw_supersede'"),
    ("表 COMMENT", "SELECT obj_description('raw_supersede_log'::regclass)"),
    ("現有列數", "SELECT count(*) FROM raw_supersede_log"),
]


def _verify(cur):
    print("── 驗證清單 ──")
    for label, sql in VERIFY:
        try:
            cur.execute(sql)
            row = cur.fetchone()
            print(f"  {label}: {(row[0] if row and row[0] is not None else '(無)')}")
        except Exception as e:  # noqa: BLE001  表未建時 count/comment 會失敗 → 誠實印,不中斷
            print(f"  {label}: (查詢失敗:{e})")


def _selftest():
    """DDL 純文字結構自測(零 DB):固化本 migration 之核心不變式，換機/重構時紅綠可查。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    labels = [lbl for lbl, _ in DDL]
    blob = "\n".join(sql for _, sql in DDL)
    chk("表 DDL 為 CREATE TABLE IF NOT EXISTS(冪等)",
        any("CREATE TABLE IF NOT EXISTS raw_supersede_log" in s for _, s in DDL))
    chk("五元組+衝突雙方欄齊全(pk/old_row/new_row/superseded_at/valid_time/reason/attestation_run_id)",
        all(c in blob for c in ("pk", "old_row", "new_row", "superseded_at", "valid_time", "reason", "attestation_run_id")))
    chk("FK 指向 attestation_result(P4.E6 provenance)", "REFERENCES attestation_result(id)" in blob)
    chk("append-only trigger:BEFORE UPDATE OR DELETE + RAISE(決策 A=(a))",
        "BEFORE UPDATE OR DELETE ON raw_supersede_log" in blob and "RAISE EXCEPTION" in blob)
    chk("TRUNCATE 守衛:BEFORE TRUNCATE FOR EACH STATEMENT(M3；row-level 擋不住 TRUNCATE)",
        "BEFORE TRUNCATE ON raw_supersede_log" in blob and "FOR EACH STATEMENT" in blob)
    chk("trigger 冪等(pg_trigger 存在性守衛;含 no_truncate)",
        "tgname='raw_supersede_log_no_mutate'" in blob and "tgname='raw_supersede_log_no_truncate'" in blob)
    chk("tombstone 受控函式存在(P4.E3 唯一例外)+ 須具事由",
        "FUNCTION tombstone_raw_supersede" in blob and "provenance 不得空" in blob)
    chk("tombstone 僅 UPDATE 放行、DELETE 恆禁(保留 tombstone 列)",
        "TG_OP = 'UPDATE'" in blob and "current_setting('augur.supersede_tombstone', true) = 'on'" in blob)
    chk("三索引(table_time/run/pk_gin)",
        all(x in blob for x in ("ix_supersede_table_time", "ix_supersede_run", "ix_supersede_pk_gin")))
    chk("GIN 索引於 pk(JSONB 可查)", "USING GIN (pk)" in blob)
    chk("表與關鍵欄有 COMMENT(可追溯)",
        any("COMMENT ON TABLE raw_supersede_log" in s for _, s in DDL))
    chk("DDL label 唯一", len(labels) == len(set(labels)))
    print("  —— 通過（DDL 結構自測；DB 行為六不變式須於備援環境跑 test_raw_supersede_log.py）"
          if ok else "  —— 有 FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="raw_supersede_log DDL 遷移(AUD-02;append-only＋tombstone;冪等)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    ap.add_argument("--selftest", action="store_true", help="DDL 純文字結構自測(零 DB)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.check:
            for label, ddl in DDL:
                cur.execute(ddl)
                print(f"✓ {label}")
        _verify(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
