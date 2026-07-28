#!/usr/bin/env python
"""建匯入檔案合格檢驗 S1 DDL — knowledge_import_job / knowledge_import_qualification。

🎯 這支在做什麼(白話):為本機檔案匯入補上 S1 最小帳本——job 級 `knowledge_import_job` 與檔案級
   `knowledge_import_qualification`，另建 verdict/reason code 字典表作 DB SSOT。此表只記錄 preflight 與
   入庫真相，**不**做 approve/activate、**不**改既有 license gate、**不**碰市場 API。
守 #6(冪等 DDL)· #29a/d(指令矩陣)· FZ-keep(零 FinMind/FRED)。

執行指令矩陣:
  python scripts/migrate_import_qualification_ddl.py
  python scripts/migrate_import_qualification_ddl.py --dry-run
  python scripts/migrate_import_qualification_ddl.py --apply
  python scripts/migrate_import_qualification_ddl.py --check
  python scripts/migrate_import_qualification_ddl.py --selftest
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from augur.knowledge import import_qualification as iq

DDL = f"""
CREATE TABLE IF NOT EXISTS knowledge_import_verdict_dict (
    verdict        text PRIMARY KEY,
    label_zh       text NOT NULL,
    is_terminal    boolean NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS knowledge_import_reason_code_dict (
    reason_code    text PRIMARY KEY,
    verdict        text NOT NULL REFERENCES knowledge_import_verdict_dict(verdict),
    label_zh       text NOT NULL,
    is_preflight   boolean NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS knowledge_import_job (
    job_id             bigserial PRIMARY KEY,
    channel            text NOT NULL CHECK (channel IN ('local_files')),
    source_key         varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
    root_path          text NOT NULL,
    declared_license   text NOT NULL,
    access_scope       varchar(16) NOT NULL,
    domain             varchar(64) NOT NULL,
    owner_user_id      bigint REFERENCES app_user(user_id),
    is_dry_run         boolean NOT NULL DEFAULT false,
    status             text NOT NULL CHECK (status IN ('running','completed','failed')),
    total_files        integer NOT NULL DEFAULT 0,
    scanned_files      integer NOT NULL DEFAULT 0,
    ok_files           integer NOT NULL DEFAULT 0,
    dup_files          integer NOT NULL DEFAULT 0,
    short_files        integer NOT NULL DEFAULT 0,
    skip_files         integer NOT NULL DEFAULT 0,
    fail_files         integer NOT NULL DEFAULT 0,
    summary            jsonb NOT NULL DEFAULT '{{}}'::jsonb,
    started_at         timestamptz NOT NULL DEFAULT now(),
    finished_at        timestamptz
);

CREATE TABLE IF NOT EXISTS knowledge_import_qualification (
    qualification_id   bigserial PRIMARY KEY,
    job_id             bigint NOT NULL REFERENCES knowledge_import_job(job_id) ON DELETE CASCADE,
    abs_path           text NOT NULL,
    rel_path           text NOT NULL,
    size_bytes         bigint,
    verdict            text NOT NULL REFERENCES knowledge_import_verdict_dict(verdict),
    reason_code        text NOT NULL REFERENCES knowledge_import_reason_code_dict(reason_code),
    preflight          jsonb NOT NULL DEFAULT '{{}}'::jsonb,
    ingest_status      text,
    item_id            integer REFERENCES knowledge_item(item_id),
    segment_rows       integer NOT NULL DEFAULT 0,
    error_text         text,
    preflight_at       timestamptz,
    ingested_at        timestamptz,
    created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kiq_job
  ON knowledge_import_qualification (job_id, qualification_id);
CREATE INDEX IF NOT EXISTS idx_kiq_reason
  ON knowledge_import_qualification (reason_code, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_kij_started
  ON knowledge_import_job (started_at DESC);

INSERT INTO knowledge_import_verdict_dict (verdict, label_zh, is_terminal) VALUES
  ('{iq.VERDICT_PENDING}', '待判定', false),
  ('{iq.VERDICT_PASS}',    '通過',   true),
  ('{iq.VERDICT_REJECT}',  '不合格', true),
  ('{iq.VERDICT_ERROR}',   '錯誤',   true)
ON CONFLICT (verdict) DO NOTHING;

INSERT INTO knowledge_import_reason_code_dict (reason_code, verdict, label_zh, is_preflight) VALUES
  ('{iq.REASON_QUEUED}',            '{iq.VERDICT_PENDING}', '已排入檢驗', true),
  ('{iq.REASON_PREFLIGHT_OK}',      '{iq.VERDICT_PASS}',    'preflight 通過', true),
  ('{iq.REASON_TOO_SHORT}',         '{iq.VERDICT_REJECT}',  '文字過短', true),
  ('skip_oversize',                 '{iq.VERDICT_REJECT}',  '超過單檔大小上限', true),
  ('skip_symlink',                  '{iq.VERDICT_REJECT}',  '符號連結已略過', true),
  ('skip_empty',                    '{iq.VERDICT_REJECT}',  '空檔', true),
  ('skip_decode_error',             '{iq.VERDICT_REJECT}',  '文字解碼失敗', true),
  ('skip_parse_error',              '{iq.VERDICT_REJECT}',  '解析失敗或檔案損壞', true),
  ('skip_encrypted',                '{iq.VERDICT_REJECT}',  '加密檔需先解密', true),
  ('skip_unknown_ext',              '{iq.VERDICT_REJECT}',  '未支援副檔名', true),
  ('skip_no_text',                  '{iq.VERDICT_REJECT}',  '無可抽文字', true),
  ('skip_missing_ocr',              '{iq.VERDICT_REJECT}',  '缺 OCR 引擎', true),
  ('skip_missing_parser',           '{iq.VERDICT_REJECT}',  '缺解析器或轉檔器', true),
  ('{iq.REASON_SKIP_OTHER}',        '{iq.VERDICT_REJECT}',  '其他略過原因', true),
  ('{iq.REASON_DUPLICATE_CONTENT}', '{iq.VERDICT_PASS}',    '內容重複，沿用既有 item', false),
  ('{iq.REASON_WRITE_OK}',          '{iq.VERDICT_PASS}',    '已寫入知識層', false),
  ('{iq.REASON_INGEST_ERROR}',      '{iq.VERDICT_ERROR}',   '入庫錯誤', false)
ON CONFLICT (reason_code) DO NOTHING;
"""


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建兩主表", "knowledge_import_job" in DDL and "knowledge_import_qualification" in DDL)
    chk("DDL 建字典表", "knowledge_import_verdict_dict" in DDL and "knowledge_import_reason_code_dict" in DDL)
    chk("channel 僅 local_files", "channel IN ('local_files')" in DDL)
    chk("queued/pass/reject/error 種子齊", all(v in DDL for v in ("queued", "pass", "reject", "error")))
    chk("approve/activate 未入 DDL", "approve" not in DDL and "activate" not in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    need = {
        "knowledge_import_job",
        "knowledge_import_qualification",
        "knowledge_import_verdict_dict",
        "knowledge_import_reason_code_dict",
    }
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            """
            SELECT table_name
              FROM information_schema.tables
             WHERE table_schema='public'
               AND table_name LIKE 'knowledge_import_%'
            """
        )
        got = {r[0] for r in cur.fetchall()}
        print(f"tables={sorted(got)}")
        missing = need - got
        if missing:
            print(f"✗ 缺表 {sorted(missing)}")
            return 1
        cur.execute("SELECT count(*) FROM knowledge_import_verdict_dict")
        n_verdict = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM knowledge_import_reason_code_dict")
        n_reason = cur.fetchone()[0]
        print(f"verdict_dict={n_verdict} reason_dict={n_reason}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S1 匯入檔案合格檢驗 DDL")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check_live()

    from augur.core import db

    apply = bool(args.apply) and not args.dry_run
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.knowledge_import_job')")
        job_exists = bool(cur.fetchone()[0])
        cur.execute("SELECT to_regclass('public.knowledge_import_qualification')")
        qual_exists = bool(cur.fetchone()[0])
        print("IMPORT-QUAL-GATE S1 DDL 現況:")
        print(f"  knowledge_import_job: {'已在' if job_exists else '待建'}")
        print(f"  knowledge_import_qualification: {'已在' if qual_exists else '待建'}")
    if not apply:
        print("\n(唯讀 dry-run；--apply 才套用。此 DDL 只建帳本，不動 approve/activate。)")
        return 0

    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(DDL)
    print("  ✓ S1 DDL 冪等完成")
    return check_live()


if __name__ == "__main__":
    sys.exit(main())
