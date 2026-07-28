#!/usr/bin/env python
"""source_license_whitelist 表遷移 — SRC-AUTO P1 謂詞之資料側(license 判定=人 seed 帶 citation)。

🎯 這支在做什麼(白話):SRC-AUTO 機械謂詞 P1「license ∈ {public_domain, cc_whitelist}」的依據表。
   license 判定是法務性判斷=**人**——本表每列由 hugo 核(provider pattern + 該 regime 之可核出處),
   AI 只讀不寫值。誠實閘:DELETE/TRUNCATE 拒、UPDATE 須 GUC(白名單被默改=大門默開)。
守 #29b(資料驅動:新 provider=INSERT 非改碼)· #15(誠實閘)· #5(不入密)· #29a/d。
SSOT=reports/augur_source_auto_review_plan_20260728.md §三(SRC-AUTO-go,hugo 2026-07-28)。

執行指令矩陣:
  python scripts/migrate_source_whitelist_ddl.py            # 無參數:現況(表在?列數?)
  python scripts/migrate_source_whitelist_ddl.py --apply    # 遷移(冪等)
  python scripts/migrate_source_whitelist_ddl.py --dry-run  # 只印 SQL
  python scripts/migrate_source_whitelist_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

GUC = "augur.honesty_write"

SQL = f"""
CREATE TABLE IF NOT EXISTS source_license_whitelist (
    provider_pattern TEXT PRIMARY KEY,          -- SQL LIKE pattern 對 source_key(如 'arxiv%')
    license_regime   TEXT NOT NULL CHECK (license_regime IN
                     ('public_domain','cc_whitelist','owned_local','metadata_only')),
    citation         TEXT NOT NULL,             -- 可核出處(該 provider license 之依據;禁空)
    decided_by       TEXT NOT NULL,             -- 人(hugo);AI 不代填
    decided_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (btrim(citation) <> ''), CHECK (btrim(decided_by) <> '')
);

CREATE OR REPLACE FUNCTION src_whitelist_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION '% on source_license_whitelist 遭誠實閘拒絕(退場走新列覆蓋語意,不刪史)', TG_OP;
    END IF;
    IF TG_OP = 'UPDATE' AND coalesce(current_setting('{GUC}', true), '') <> 'on' THEN
        RAISE EXCEPTION 'UPDATE 遭拒:白名單被默改=審批大門默開;須經工具鏈(SET LOCAL {GUC}=on)';
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS src_wl_row ON source_license_whitelist;
CREATE TRIGGER src_wl_row BEFORE UPDATE OR DELETE ON source_license_whitelist
    FOR EACH ROW EXECUTE FUNCTION src_whitelist_guard();
DROP TRIGGER IF EXISTS src_wl_stmt ON source_license_whitelist;
CREATE TRIGGER src_wl_stmt BEFORE TRUNCATE ON source_license_whitelist
    FOR EACH STATEMENT EXECUTE FUNCTION src_whitelist_guard();

-- REGIME-MAP-v1(hugo 2026-07-28 核可):dataLicense 名/URL pattern → regime。
-- 只收無歧義映射(public_domain/cc_whitelist);NC/ND 否決與「未映射=人閘」為 code 側邏輯(fail-closed)。
CREATE TABLE IF NOT EXISTS license_regime_map (
    map_id     SERIAL PRIMARY KEY,
    kind       TEXT NOT NULL CHECK (kind IN ('name','url')),
    pattern    TEXT NOT NULL,
    regime     TEXT NOT NULL CHECK (regime IN ('public_domain','cc_whitelist')),
    rule       TEXT NOT NULL,               -- R1..R4(簽核件條號)
    citation   TEXT NOT NULL CHECK (btrim(citation) <> ''),
    decided_by TEXT NOT NULL CHECK (btrim(decided_by) <> ''),
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (kind, pattern)
);
DROP TRIGGER IF EXISTS lic_map_row ON license_regime_map;
CREATE TRIGGER lic_map_row BEFORE UPDATE OR DELETE ON license_regime_map
    FOR EACH ROW EXECUTE FUNCTION src_whitelist_guard();
DROP TRIGGER IF EXISTS lic_map_stmt ON license_regime_map;
CREATE TRIGGER lic_map_stmt BEFORE TRUNCATE ON license_regime_map
    FOR EACH STATEMENT EXECUTE FUNCTION src_whitelist_guard();

-- SRC-QUALIFY(P4P5-go,hugo 2026-07-28):pacing 政策值=人簽資料側(#29b);步②落值唯讀此表。
CREATE TABLE IF NOT EXISTS source_pacing_policy (
    protocol     TEXT PRIMARY KEY,
    pace_seconds NUMERIC NOT NULL CHECK (pace_seconds >= 1.0),
    quota_limit  INTEGER NOT NULL CHECK (quota_limit > 0),
    citation     TEXT NOT NULL CHECK (btrim(citation) <> ''),
    decided_by   TEXT NOT NULL CHECK (btrim(decided_by) <> ''),
    decided_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS pace_pol_row ON source_pacing_policy;
CREATE TRIGGER pace_pol_row BEFORE UPDATE OR DELETE ON source_pacing_policy
    FOR EACH ROW EXECUTE FUNCTION src_whitelist_guard();
DROP TRIGGER IF EXISTS pace_pol_stmt ON source_pacing_policy;
CREATE TRIGGER pace_pol_stmt BEFORE TRUNCATE ON source_pacing_policy
    FOR EACH STATEMENT EXECUTE FUNCTION src_whitelist_guard();
"""


def apply(dry):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.source_license_whitelist')")
        have = cur.fetchone()[0] is not None
        cur.execute("SELECT to_regclass('public.license_regime_map')")
        have2 = cur.fetchone()[0] is not None
        cur.execute("SELECT to_regclass('public.source_pacing_policy')")
        have3 = cur.fetchone()[0] is not None
        cur.execute("SELECT count(*) FROM pg_trigger WHERE (tgname LIKE 'src_wl%' OR tgname LIKE 'lic_map%' OR tgname LIKE 'pace_pol%') AND NOT tgisinternal")
        trigs = cur.fetchone()[0]
        if have and have2 and have3 and trigs >= 6:
            print("✓ 表與誠實閘皆在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            print("(--dry-run:未執行)")
            return 0
        cur.execute(SQL)
        print("✓ source_license_whitelist + 誠實閘 落地(列由 hugo 核入;AI 不代填)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.source_license_whitelist')")
        if cur.fetchone()[0] is None:
            print("  (表未建;--apply)")
            return 0
        cur.execute("SELECT provider_pattern, license_regime, decided_by FROM source_license_whitelist ORDER BY 1")
        rows = cur.fetchall()
        print(f"  白名單 {len(rows)} 列:" if rows else "  (0 列——P1 謂詞在白名單空時全數不過=fail-closed)")
        for r in rows:
            print(f"    {r[0]:24} {r[1]:14} by {r[2]}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("regime 四值 CHECK", all(k in SQL for k in ("public_domain", "cc_whitelist", "owned_local", "metadata_only")))
    chk("citation 禁空(license 判定須可核)", "btrim(citation) <> ''" in SQL)
    chk("decided_by 禁空(人核;AI 不代填)", "btrim(decided_by) <> ''" in SQL)
    chk("誠實閘:DELETE/TRUNCATE 拒+UPDATE 須 GUC", "遭誠實閘拒絕" in SQL and GUC in SQL)
    chk("三表各 row+stmt 雙 trigger(共 6)", SQL.count("CREATE TRIGGER") == 6)
    chk("冪等", "IF NOT EXISTS" in SQL and "DROP TRIGGER IF EXISTS" in SQL)
    chk("REGIME-MAP 表:regime 僅二值(無歧義映射;metadata_only/owned_local 不在此表)",
        "regime IN ('public_domain','cc_whitelist')" in SQL)
    chk("REGIME-MAP 表:kind ∈ name|url+UNIQUE(kind,pattern)",
        "kind IN ('name','url')" in SQL and "UNIQUE (kind, pattern)" in SQL)
    chk("REGIME-MAP 同閘(UPDATE 須 GUC/DELETE 拒)", "lic_map_row" in SQL and "lic_map_stmt" in SQL)
    chk("PACING 表:pace ≥1.0 底線+quota >0(§七 O1 CHECK)",
        "pace_seconds >= 1.0" in SQL and "quota_limit > 0" in SQL)
    chk("PACING 表同閘+人簽欄禁空", "pace_pol_row" in SQL and "pace_pol_stmt" in SQL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="source_license_whitelist 遷移(SRC-AUTO P1)")
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
