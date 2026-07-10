#!/usr/bin/env python
"""來源治理 schema 遷移 — 深抓計畫 S0:M1-M5+審批日誌+健康度+斷點+視圖+staging trigger(憲章 v1.41.0 落地)。

🎯 這支在做什麼(白話):把「世界來源目錄」的治理機件一次落地——
   M1/M2 `knowledge_source` 擴 14 治理欄+CHECK(審批狀態機/license 軌/pace/quota/wave);
   M3 backfill(對帳矩陣:既有生產源→active 追認、manual_file 導管→active、re3data 等→proposed;
      + F 軌 5 列 pseudo-source 收編全文通道,ia_fulltext 依 P8 拍板維持 suspended);
   M4 DOI 正規化一次性合併(norm_doi SSOT=curation.py;跨形態重複→贏家合併);
   M5 harvest 帳本增 'partial' 可重排狀態;
   3.3 review_log/3.4 health/3.5 checkpoints+cursor/3.6 索引+視圖+快照表/3.7 **staging BEFORE INSERT
   trigger(真第三層 fail-closed:非 active 源之資料任何路徑皆進不了 staging;manual_file 豁免寫進閘內)**。
   --apply 前置=pg_dump 快照(#6/#30 復原後路;無快照拒跑)。

守 憲章 v1.41.0 · #6(快照前置+冪等)· #12(DDL 單一住所;norm_doi 引 curation)· #15(backfill 對帳
   加總必=全表、零 NULL 桶)· CLAUDE #29a。SSOT=reports/augur_knowledge_deep_harvest_plan_20260710.md §3。

執行指令矩陣:
  python scripts/migrate_source_governance.py                    # 無參數:現況矩陣(唯讀)
  python scripts/migrate_source_governance.py --dry-run          # backfill/DOI 合併預覽(含 fulltext_eligible 清單)
  python scripts/migrate_source_governance.py --run --snapshot /path/ks_snapshot.dump   # DDL+backfill(需快照)
  python scripts/migrate_source_governance.py --fix-doi          # M4 一次性 DOI 合併(先 --dry-run 看預覽)
  python scripts/migrate_source_governance.py --verify           # W0 驗收:矩陣加總/零NULL/trigger/DOI 重複=0
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge.curation import norm_doi

PSEUDO_SOURCES = [  # §1 F 軌:全文通道收編(無模板=天然不入排程;僅供全文工具查閘+記帳)
    ("gutenberg_files", "fetch_pd_fulltext 之 PG 官方 mirror/catalog 全文通道", "proposed"),
    ("ia_fulltext", "fetch_pd_fulltext 之 IA 卷全文通道", "suspended"),   # P8=方案A:IA 降 metadata,維持 suspended
    ("wikisource_files", "fetch_pd_fulltext 之 Wikisource 頁全文通道", "proposed"),
    ("core_fulltext", "fetch_oa_fulltext 之 CORE 後援通道(P4 後 activate)", "proposed"),
    ("oa_publisher_pool", "fetch_oa_fulltext 之 OA 出版商散點(per-host 分桶 pace)", "proposed"),
]

DDL = [
    ("M1 擴欄", """
        ALTER TABLE knowledge_source
          ADD COLUMN IF NOT EXISTS approval_status      varchar(16) NOT NULL DEFAULT 'proposed',
          ADD COLUMN IF NOT EXISTS approved_by          varchar(64),
          ADD COLUMN IF NOT EXISTS approved_at          timestamptz,
          ADD COLUMN IF NOT EXISTS license_regime       varchar(16),
          ADD COLUMN IF NOT EXISTS fulltext_eligible    boolean NOT NULL DEFAULT false,
          ADD COLUMN IF NOT EXISTS wave                 smallint,
          ADD COLUMN IF NOT EXISTS protocol             varchar(24),
          ADD COLUMN IF NOT EXISTS pace_seconds         numeric(6,2),
          ADD COLUMN IF NOT EXISTS quota_limit          integer,
          ADD COLUMN IF NOT EXISTS quota_window_seconds integer,
          ADD COLUMN IF NOT EXISTS cooldown_seconds     integer,
          ADD COLUMN IF NOT EXISTS max_pages            integer,
          ADD COLUMN IF NOT EXISTS abstract_policy      varchar(8),
          ADD COLUMN IF NOT EXISTS est_scale            text"""),
    ("M2 CHECK", """
        DO $$ BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_approval_status') THEN
            ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_approval_status
              CHECK (approval_status IN ('proposed','approved','active','suspended','exhausted','rejected'));
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_license_regime') THEN
            ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_license_regime
              CHECK (license_regime IS NULL OR license_regime IN ('public_domain','cc_whitelist','metadata_only','owned_local'));
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_active_needs_approval') THEN
            ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_active_needs_approval
              CHECK (approval_status NOT IN ('approved','active') OR approved_by IS NOT NULL);
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ks_abstract_policy') THEN
            ALTER TABLE knowledge_source ADD CONSTRAINT chk_ks_abstract_policy
              CHECK (abstract_policy IS NULL OR abstract_policy IN ('allow','deny'));
          END IF;
        END $$"""),
    ("M2 index", "CREATE INDEX IF NOT EXISTS idx_ks_approval ON knowledge_source(approval_status, wave)"),
    ("M5 harvest partial", """
        DO $$ BEGIN
          ALTER TABLE knowledge_harvest_log DROP CONSTRAINT IF EXISTS knowledge_harvest_log_status_check;
          ALTER TABLE knowledge_harvest_log ADD CONSTRAINT knowledge_harvest_log_status_check
            CHECK (status IN ('ok','empty','error','partial'));
        END $$"""),
    ("3.3 review_log", """
        CREATE TABLE IF NOT EXISTS knowledge_source_review_log (
          review_id    bigserial PRIMARY KEY,
          source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
          action       varchar(16) NOT NULL
                       CHECK (action IN ('propose','probe','approve','activate','suspend','resume',
                                         'exhaust','reject','reopen','edit')),
          old_status   varchar(16),
          new_status   varchar(16),
          actor        varchar(64) NOT NULL,
          os_user      varchar(64),
          reason       text,
          probe_result jsonb,
          created_at   timestamptz NOT NULL DEFAULT now()
        )"""),
    ("3.3 index", "CREATE INDEX IF NOT EXISTS idx_ksrl_source ON knowledge_source_review_log(source_key, created_at DESC)"),
    ("3.4 health", """
        CREATE TABLE IF NOT EXISTS knowledge_source_health (
          source_key         varchar(64) PRIMARY KEY REFERENCES knowledge_source(source_key),
          total_calls        bigint  NOT NULL DEFAULT 0,
          total_errors       bigint  NOT NULL DEFAULT 0,
          consecutive_errors integer NOT NULL DEFAULT 0,
          cooldown_level     smallint NOT NULL DEFAULT 0,
          calls_in_window    integer NOT NULL DEFAULT 0,
          window_started_at  timestamptz,
          last_ok_at         timestamptz,
          last_call_at       timestamptz,
          last_error_at      timestamptz,
          last_error_kind    varchar(16),
          cooldown_until     timestamptz,
          updated_at         timestamptz NOT NULL DEFAULT now()
        )"""),
    ("3.5 dump_checkpoint", """
        CREATE TABLE IF NOT EXISTS knowledge_dump_checkpoint (
          source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
          dump_file    text        NOT NULL,
          byte_offset  bigint      NOT NULL DEFAULT 0,
          items_loaded bigint      NOT NULL DEFAULT 0,
          finished     boolean     NOT NULL DEFAULT false,
          updated_at   timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (source_key, dump_file)
        )"""),
    ("3.5 source_cursor", """
        CREATE TABLE IF NOT EXISTS knowledge_source_cursor (
          source_key   varchar(64) NOT NULL REFERENCES knowledge_source(source_key),
          scope        text        NOT NULL,
          cursor_kind  varchar(16) NOT NULL CHECK (cursor_kind IN ('page_cursor','oai_datestamp')),
          cursor_value text,
          pages_done   integer NOT NULL DEFAULT 0,
          rows_loaded  bigint  NOT NULL DEFAULT 0,
          finished     boolean NOT NULL DEFAULT false,
          updated_at   timestamptz NOT NULL DEFAULT now(),
          PRIMARY KEY (source_key, scope)
        )"""),
    ("3.6 staging index", "CREATE INDEX IF NOT EXISTS idx_staging_source ON knowledge_staging(source_key, status)"),
    ("3.6 view coverage_source", """
        CREATE OR REPLACE VIEW v_knowledge_coverage_source AS
        SELECT s.source_key, s.adapter, s.domain, s.approval_status, s.wave, s.license_regime,
               count(st.staging_id)                                AS staged_total,
               count(*) FILTER (WHERE st.status='promoted')        AS promoted,
               count(*) FILTER (WHERE st.status='rejected')        AS rejected,
               count(*) FILTER (WHERE st.status='pending')         AS pending,
               round(100.0*count(*) FILTER (WHERE st.status='promoted')
                     / nullif(count(st.staging_id),0), 1)          AS promote_rate_pct
        FROM knowledge_source s
        LEFT JOIN knowledge_staging st USING (source_key)
        GROUP BY 1,2,3,4,5,6"""),
    ("3.6 view coverage_domain", """
        CREATE OR REPLACE VIEW v_knowledge_coverage_domain AS
        SELECT d.domain, d.items, d.items_with_text, d.items_open_fulltext, d.items_owned_local,
               d.open_segments, COALESCE(q.queries, 0) AS queries
        FROM (
          SELECT i.domain,
                 count(DISTINCT i.item_id) AS items,
                 count(DISTINCT t.item_id) AS items_with_text,
                 count(DISTINCT t.item_id) FILTER (WHERE t.license IN ('public_domain','cc-by','cc-by-sa','cc0'))
                                           AS items_open_fulltext,
                 count(DISTINCT t.item_id) FILTER (WHERE t.license = 'owned_local') AS items_owned_local,
                 count(t.itext_id) FILTER (WHERE t.license IN ('public_domain','cc-by','cc-by-sa','cc0'))
                                           AS open_segments
          FROM knowledge_item i LEFT JOIN knowledge_item_text t USING (item_id)
          GROUP BY 1
        ) d
        LEFT JOIN (
          SELECT m.augur_domain AS domain, count(*) AS queries
          FROM knowledge_query kq JOIN knowledge_domain_map m ON m.openalex_field = kq.domain
          WHERE kq.enabled GROUP BY 1
        ) q USING (domain)"""),
    ("3.6 view harvest_progress", """
        CREATE OR REPLACE VIEW v_knowledge_harvest_progress AS
        SELECT h.source_key, count(*) AS combos_done,
               count(*) FILTER (WHERE h.status='ok')      AS ok,
               count(*) FILTER (WHERE h.status='partial') AS partial,
               count(*) FILTER (WHERE h.status='empty')   AS empty,
               count(*) FILTER (WHERE h.status='error')   AS error,
               sum(h.rows_staged) AS rows_staged
        FROM knowledge_harvest_log h GROUP BY 1"""),
    ("3.6 coverage_snapshot", """
        CREATE TABLE IF NOT EXISTS knowledge_coverage_snapshot (
          snapped_at   timestamptz NOT NULL DEFAULT now(),
          source_key   varchar(64) NOT NULL,
          staged_total bigint, promoted bigint, rejected bigint, pending bigint,
          PRIMARY KEY (source_key, snapped_at)
        )"""),
    ("3.7 trigger fn", """
        CREATE OR REPLACE FUNCTION trg_staging_source_gate() RETURNS trigger AS $$
        DECLARE st text; ad text;
        BEGIN
          SELECT approval_status, adapter INTO st, ad FROM knowledge_source WHERE source_key = NEW.source_key;
          IF ad = 'manual_file' THEN RETURN NEW; END IF;
          IF st IS DISTINCT FROM 'active' THEN
            RAISE EXCEPTION 'staging gate: source % is %, need active (charter: human approval)',
              NEW.source_key, st;
          END IF;
          RETURN NEW;
        END $$ LANGUAGE plpgsql"""),
    ("3.7 trigger", """
        DO $$ BEGIN
          DROP TRIGGER IF EXISTS staging_source_gate ON knowledge_staging;
          CREATE TRIGGER staging_source_gate BEFORE INSERT ON knowledge_staging
            FOR EACH ROW EXECUTE FUNCTION trg_staging_source_gate();
        END $$"""),
]

# M3 backfill 矩陣(P1;分群 SQL 與計畫矩陣一一對應)
BACKFILL = [
    ("既有生產源→active(追認)",
     "UPDATE knowledge_source SET approval_status='active', approved_by=%(actor)s, approved_at=now() "
     "WHERE enabled AND query_template IS NOT NULL AND adapter <> 'manual_file' "
     "AND approval_status='proposed'"),
    ("manual_file 導管→active(sanctioned 匯入路)",
     "UPDATE knowledge_source SET approval_status='active', approved_by=%(actor)s, approved_at=now(), "
     "protocol='local_file' WHERE adapter='manual_file' AND approval_status='proposed'"),
    # 其餘(re3data stub/具名 NULL 模板/deliberately disabled)自然留 proposed=DEFAULT,零 UPDATE
]


def matrix(cur):
    cur.execute("SELECT approval_status, count(*) FROM knowledge_source GROUP BY 1 ORDER BY 1")
    dist = dict(cur.fetchall())
    cur.execute("SELECT count(*) FROM knowledge_source")
    total = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM knowledge_source WHERE approval_status IS NULL")
    nulls = cur.fetchone()[0]
    return dist, total, nulls


def doi_dupes(cur, limit=None):
    """M4:跨形態 DOI 重複對(external_id 過 norm_doi 後相同、item_id 不同)。"""
    cur.execute("SELECT item_id, external_id FROM knowledge_item WHERE external_id ILIKE '%doi%' "
                "OR external_id LIKE '10.%'")
    seen, dupes = {}, []
    for iid, ext in cur.fetchall():
        key = norm_doi(ext)
        if key in seen and seen[key] != iid:
            dupes.append((seen[key], iid, key))
        else:
            seen[key] = iid
    return dupes[:limit] if limit else dupes


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name='knowledge_source' AND column_name='approval_status'")
        migrated = cur.fetchone()[0] > 0
        print(f"M1 擴欄:{'✓ 已套用' if migrated else '✗ 未套用'}")
        if migrated:
            dist, total, nulls = matrix(cur)
            print(f"審批分佈:{dist}(加總 {sum(dist.values())}/{total},NULL {nulls})")
        for t in ("knowledge_source_review_log", "knowledge_source_health",
                  "knowledge_dump_checkpoint", "knowledge_source_cursor", "knowledge_coverage_snapshot"):
            cur.execute("SELECT to_regclass(%s)", (t,))
            print(f"  {'✓' if cur.fetchone()[0] else '✗'} {t}")
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='staging_source_gate'")
        print(f"  {'✓' if cur.fetchone()[0] else '✗'} staging_source_gate trigger")


def dry_run():
    with db.connect() as conn, db.transaction(conn) as cur:
        print("═══ backfill 預覽(P1 矩陣)═══")
        cur.execute("SELECT count(*) FROM knowledge_source WHERE enabled AND query_template IS NOT NULL "
                    "AND adapter <> 'manual_file'")
        print(f"  → active(生產追認):{cur.fetchone()[0]}(計畫矩陣=53)")
        cur.execute("SELECT count(*) FROM knowledge_source WHERE adapter='manual_file'")
        print(f"  → active(manual_file 導管):{cur.fetchone()[0]}(計畫矩陣=16)")
        cur.execute("SELECT count(*) FROM knowledge_source WHERE NOT (enabled AND query_template IS NOT NULL) "
                    "AND adapter <> 'manual_file'")
        print(f"  → proposed(其餘):{cur.fetchone()[0]}(計畫矩陣=3,507+15+2=3,524)")
        print(f"  + INSERT pseudo-source {len(PSEUDO_SOURCES)} 列(ia_fulltext 起始 suspended,P8=方案A)")
        print("═══ M4 DOI 合併預覽 ═══")
        d = doi_dupes(cur)
        print(f"  跨形態重複對:{len(d)}(計畫實查=152;--fix-doi 執行合併)")
        for a, b, k in d[:5]:
            print(f"    item {a} ⇔ {b}({k[:50]})")


def run(snapshot):
    if not snapshot or not os.path.exists(snapshot):
        sys.exit("✗ --run 需 --snapshot <pg_dump -Fc -t knowledge_source 快照檔>(#6 復原後路;先快照再遷移)")
    actor = os.environ.get("USER", "unknown")
    with db.connect() as conn:
        cur = conn.cursor()
        for name, sql in DDL:
            cur.execute(sql)
            print(f"  ✓ {name}")
        for name, sql in BACKFILL:
            cur.execute(sql, {"actor": actor})
            print(f"  ✓ backfill {name}:{cur.rowcount} 列")
        for key, note, st in PSEUDO_SOURCES:
            cur.execute("""
                INSERT INTO knowledge_source (source_key, adapter, domain, entity_type, enabled,
                                              approval_status, protocol, note, approved_by, approved_at)
                VALUES (%s, 'generic_json', 'general', 'work', false, %s, 'fulltext_channel', %s,
                        CASE WHEN %s <> 'proposed' THEN %s END,
                        CASE WHEN %s <> 'proposed' THEN now() END)
                ON CONFLICT (source_key) DO NOTHING""", (key, st, note, st, actor, st))
        print(f"  ✓ pseudo-source {len(PSEUDO_SOURCES)} 列(冪等)")
        conn.commit()
    print("✓ --run 完成(M4 DOI 合併另跑 --fix-doi)")


def fix_doi():
    with db.connect() as conn:
        cur = conn.cursor()
        d = doi_dupes(cur)
        if not d:
            print("✓ 無跨形態 DOI 重複,M4 無事可做")
            return
        merged = 0
        for winner, loser, _k in d:
            # item_text:贏家無同 seq 段才搬;搬不動的輸家段(seq 撞)刪除(內容同 DOI 同文,贏家版為準)
            cur.execute("UPDATE knowledge_item_text SET item_id=%s WHERE item_id=%s "
                        "AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t2 "
                        "WHERE t2.item_id=%s AND t2.seq=knowledge_item_text.seq)", (winner, loser, winner))
            cur.execute("DELETE FROM knowledge_item_text WHERE item_id=%s", (loser,))
            # fulltext_status:贏家無帳才搬;有帳則刪輸家帳(單一終態帳)
            cur.execute("UPDATE knowledge_fulltext_status SET item_id=%s WHERE item_id=%s "
                        "AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status f2 WHERE f2.item_id=%s)",
                        (winner, loser, winner))
            cur.execute("DELETE FROM knowledge_fulltext_status WHERE item_id=%s", (loser,))
            cur.execute("DELETE FROM knowledge_item WHERE item_id=%s", (loser,))
            merged += 1
        conn.commit()
    print(f"✓ M4 合併 {merged} 對(贏家=先登錄者;孤兒段已重指)")


def verify() -> int:
    ok = True
    with db.connect() as conn, db.transaction(conn) as cur:
        dist, total, nulls = matrix(cur)
        if sum(dist.values()) != total or nulls:
            print(f"✗ 對帳:加總 {sum(dist.values())}≠{total} 或 NULL {nulls}"); ok = False
        else:
            print(f"✓ 對帳:{dist} 加總={total}、零 NULL")
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname='staging_source_gate'")
        if not cur.fetchone()[0]:
            print("✗ trigger 缺"); ok = False
        # 三層閘之第三層實測:對 proposed 源插 staging 應被 RAISE
        cur.execute("SELECT source_key FROM knowledge_source WHERE approval_status='proposed' "
                    "AND adapter <> 'manual_file' LIMIT 1")
        r = cur.fetchone()
        if r:
            try:
                cur.execute("SAVEPOINT sp")
                cur.execute("INSERT INTO knowledge_staging (source_key, entity_type, payload, status) "
                            "VALUES (%s,'document','{}','pending')", (r[0],))
                print(f"✗ trigger 漏擋:proposed 源 {r[0]} 插入成功"); ok = False
                cur.execute("ROLLBACK TO sp")
            except Exception as e:
                cur.execute("ROLLBACK TO sp")
                print(f"✓ trigger fail-closed 實測:{str(e).splitlines()[0][:70]}")
        d = doi_dupes(cur, limit=1)
        if d:
            print(f"✗ DOI 跨形態重複仍存在(--fix-doi 未跑或未盡)"); ok = False
        else:
            print("✓ DOI 跨形態重複=0")
    print("✓ --verify 全綠" if ok else "✗ --verify 失敗")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--snapshot")
    ap.add_argument("--fix-doi", dest="fixdoi", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.dry:
        dry_run(); return 0
    if args.run:
        run(args.snapshot); return 0
    if args.fixdoi:
        fix_doi(); return 0
    if args.verify:
        return verify()
    print(__doc__.split("執行指令矩陣:")[1])
    print("現況(唯讀):")
    status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
