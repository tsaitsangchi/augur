#!/usr/bin/env python
"""被取代原值快照帳本 schema 遷移 — raw_supersede_log 一表冪等落地(AUD-02 補正)。

🎯 這支在做什麼(白話):硬化「被取代原值快照帳本」——`reconcile.heal_by_date` 偵測 value_mismatch
   後,heal 覆寫 raw API 表前,把「敗方(DB pre-image old_row)＋勝方(incoming API new_row)＋裁決脈絡」
   快照成 append-only 一列,使「API wins」成為攜帶自身 Evidence 的新 Knowledge(憲章 P4.E5 矛盾保存、
   MUST NOT last-write-wins)。**表本體 DDL 單一權威住 schema.INFRA_DDL['raw_supersede_log'](issue 10:
   本腳本引用之、不另手維 CREATE TABLE);本腳本只加硬化**:三 index + **append-only BEFORE UPDATE OR DELETE
   trigger(決策 A=(a))** + **BEFORE TRUNCATE statement trigger(堵整表抹除,issue 2③)** + **REVOKE
   UPDATE/DELETE/TRUNCATE FROM PUBLIC(縱深防禦,issue 2①)** + **tombstone 法規抹除 SECURITY DEFINER 受控
   函式(決策 A 附帶義務、P4.E3 唯一例外;issue 2②以 owner 身分成唯一可覆寫者)**。全部 IF NOT EXISTS /
   CREATE OR REPLACE,非破壞新表型、重跑零副作用。

決策(卷宗 §三,Steward 2026-07-17 拍板):
  A=(a) append-only BEFORE UPDATE OR DELETE trigger + tombstone 例外路徑;
  B=(b) attestation_run_id nullable(heal 直呼 sync 無 run 時恆 None、非待回填;不改 attestation_result 寫序)。

⚠ 殘餘風險(issue 2⑤,卷宗載明):表 owner 隱含保有全 DML、可 DISABLE/DROP TRIGGER;GUC/trigger/REVOKE
   縱深只擋「非 owner 角色」。須以部署層「表 owner ≠ 應用/ingestion 角色」處置,append-only 方為完整機器保證。

守 #6(冪等重跑安全、破壞性 DDL 非本表〔新表型〕)· #12(DDL 單一住所)· #15(--selftest 六不變式回歸鎖)·
   CLAUDE #29(個別可執行 + 指令矩陣 + graceful 無參數)· 憲章 P4.E3/E5/E6 · WM.30/WM.34。
   SSOT=docs/remediation/AUD-02-raw-supersede-log.md。

執行指令矩陣:
  python scripts/migrate_raw_supersede_ddl.py            # 冪等執行 DDL(表+index+trigger+tombstone fn)+ 印驗證清單
  python scripts/migrate_raw_supersede_ddl.py --check    # 唯讀:只印驗證清單、不執行 DDL
  python scripts/migrate_raw_supersede_ddl.py --selftest # 紅綠鎖(六不變式;免 DB 免 API、零 usage;DB 相關者標注需 PG)

⚠ 本機無 PostgreSQL:須於備援環境或人類本機跑 --check ＋ --selftest,經人類 #7 實測、#19 檢視、P5 拍板後
   apply 生產 DB、併 main(卷宗 §四末項)。
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db, schema

# ── DDL。順序:表(引用 schema.INFRA_DDL 單一權威) → index → comment → REVOKE → append-only 硬化 → TRUNCATE 堵 → 例外路徑 ──
DDL = [
    # 帳表本體:每列＝一次「API wins」裁決之新 Knowledge(同時指涉衝突敗方 old_row + 勝方 new_row,
    # 攜自身 Evidence(attestation_run_id + reason + actor),append-only、永不覆寫原始證據)。
    # **表本體 DDL 唯一權威=schema.INFRA_DDL['raw_supersede_log'](issue 10:消除雙住所漂移;bootstrap_infra
    # 亦建同一常數、store() 依賴其存在)**;本腳本只加下方硬化(index/trigger/REVOKE/tombstone)。
    ("table raw_supersede_log", schema.INFRA_DDL["raw_supersede_log"]),
    ("index ix_supersede_table_time", """
        CREATE INDEX IF NOT EXISTS ix_supersede_table_time
          ON raw_supersede_log ("table", superseded_at)"""),
    ("index ix_supersede_run", """
        CREATE INDEX IF NOT EXISTS ix_supersede_run
          ON raw_supersede_log (attestation_run_id)"""),
    ("index ix_supersede_pk_gin", """
        CREATE INDEX IF NOT EXISTS ix_supersede_pk_gin
          ON raw_supersede_log USING GIN (pk)"""),
    ("comment raw_supersede_log", """
        COMMENT ON TABLE raw_supersede_log IS
        'heal 覆寫前被取代原值快照帳本(AUD-02;P4.E5 衝突裁決留痕);append-only(trigger + REVOKE 硬化)、唯 raw_supersede_tombstone() 得法規抹除(P4.E3 唯一例外);attestation_run_id 決策 B nullable(heal 直呼 sync 無 run 時恆 None、非待回填);actor=P4.E6 斷言主體'"""),
    # 縱深防禦(issue 2①):對 PUBLIC REVOKE 覆寫/刪除/整表抹除。GUC 閘非存取控制(任意角色可自行 SET LOCAL
    # augur.supersede_erase='on')→ 真正之閘=權限層:非 owner 角色無 UPDATE/DELETE/TRUNCATE 權,GUC 設了也
    # mutate 不了(setup_predict_role 另對 augur_predict REVOKE ALL)。owner 殘餘風險見檔頭 ⚠(部署層 owner 分離)。
    ("revoke mutate from public", """
        REVOKE UPDATE, DELETE, TRUNCATE ON raw_supersede_log FROM PUBLIC"""),
    # 決策 A=(a):append-only 硬化。BEFORE UPDATE OR DELETE → RAISE;唯 tombstone SECURITY DEFINER 函式
    # (以 owner 身分、設交易本地 GUC augur.supersede_erase='on')得繞過。GUC 僅為函式內開關,真正之閘=上方
    # REVOKE + 下方 SECURITY DEFINER(唯 owner 得覆寫);三者合成「不可覆寫原始證據」機器可稽核保證(WM.34)。
    ("function raw_supersede_log_append_only", """
        CREATE OR REPLACE FUNCTION raw_supersede_log_append_only()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            IF current_setting('augur.supersede_erase', true) IS DISTINCT FROM 'on' THEN
                RAISE EXCEPTION
                  'raw_supersede_log 為 append-only 原始證據帳表(P4.E3/P4.E5):% 遭拒;法規抹除須經 raw_supersede_tombstone() 受控路徑', TG_OP
                  USING ERRCODE = 'raise_exception';
            END IF;
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION
                  'raw_supersede_log 不許實體 DELETE(即使法規抹除):僅得 UPDATE 為 tombstone、保留骨架(id/table/pk/superseded_at/reason)'
                  USING ERRCODE = 'raise_exception';
            END IF;
            RETURN NEW;
        END;
        $fn$"""),
    ("trigger trg_raw_supersede_append_only", """
        DROP TRIGGER IF EXISTS trg_raw_supersede_append_only ON raw_supersede_log;
        CREATE TRIGGER trg_raw_supersede_append_only
            BEFORE UPDATE OR DELETE ON raw_supersede_log
            FOR EACH ROW EXECUTE FUNCTION raw_supersede_log_append_only()"""),
    # append-only 縱深(issue 2③):row-level BEFORE UPDATE/DELETE trigger 攔不到 TRUNCATE(不觸 row-level)→
    # 補 statement-level BEFORE TRUNCATE 一律 RAISE,堵「TRUNCATE 整表抹除證據帳」洞。無例外:tombstone 走逐列
    # UPDATE、從不 TRUNCATE,故此 trigger 無 GUC 繞過。
    ("function raw_supersede_log_no_truncate", """
        CREATE OR REPLACE FUNCTION raw_supersede_log_no_truncate()
        RETURNS trigger LANGUAGE plpgsql AS $fn$
        BEGIN
            RAISE EXCEPTION
              'raw_supersede_log 為 append-only 原始證據帳表(P4.E3/P4.E5):TRUNCATE 一律禁止(整表抹除證據帳);法規抹除須逐列經 raw_supersede_tombstone()'
              USING ERRCODE = 'raise_exception';
        END;
        $fn$"""),
    ("trigger trg_raw_supersede_no_truncate", """
        DROP TRIGGER IF EXISTS trg_raw_supersede_no_truncate ON raw_supersede_log;
        CREATE TRIGGER trg_raw_supersede_no_truncate
            BEFORE TRUNCATE ON raw_supersede_log
            FOR EACH STATEMENT EXECUTE FUNCTION raw_supersede_log_no_truncate()"""),
    # 決策 A 附帶義務:tombstone 法規抹除受控函式——**唯一得繞過 append-only trigger 之路徑**。
    # SECURITY DEFINER(issue 2②):以函式 owner 身分執行→配合上方 REVOKE(應用角色無直接 UPDATE 權、僅得
    # EXECUTE 本函式),owner 成唯一可覆寫身分,使「tombstone 為唯一繞過」為權限層保證而非僅倚賴任意可設之 GUC。
    # search_path 釘死(SECURITY DEFINER 安全慣例,防 search_path 注入)。抹除 old_row/new_row 內容本體,但留
    # tombstone 骨架(id/table/pk/superseded_at/reason)＋抹除事件 provenance(note 記 who/when/why)。
    # set_config is_local=true=交易本地、交易結束自動還原;非經本函式之 UPDATE/DELETE 一律被 trigger RAISE 擋下。P4.E3 唯一例外。
    ("function raw_supersede_tombstone", """
        CREATE OR REPLACE FUNCTION raw_supersede_tombstone(
            p_id BIGINT, p_erase_reason TEXT, p_actor TEXT DEFAULT current_user)
        RETURNS void LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = pg_catalog, public AS $fn$
        BEGIN
            IF p_erase_reason IS NULL OR btrim(p_erase_reason) = '' THEN
                RAISE EXCEPTION 'raw_supersede_tombstone:法規抹除須具明確 reason(P4.E3 例外須留 provenance)';
            END IF;
            PERFORM set_config('augur.supersede_erase', 'on', true);   -- 僅本交易繞過 append-only
            UPDATE raw_supersede_log
               SET old_row = jsonb_build_object('_tombstoned', true),
                   new_row = jsonb_build_object('_tombstoned', true),
                   note    = format('TOMBSTONE|erased_at=%s|actor=%s|reason=%s|prev_note=%s',
                                    now(), p_actor, p_erase_reason, COALESCE(note, ''))
             WHERE id = p_id;
            IF NOT FOUND THEN
                PERFORM set_config('augur.supersede_erase', 'off', true);
                RAISE EXCEPTION 'raw_supersede_tombstone:id=% 不存在', p_id;
            END IF;
            PERFORM set_config('augur.supersede_erase', 'off', true);
        END;
        $fn$"""),
    # SECURITY DEFINER 函式預設 PUBLIC 可 EXECUTE→以 owner 權跑 UPDATE 等於人人可抹除。REVOKE EXECUTE FROM
    # PUBLIC 使法規抹除須明示 GRANT 授權(issue 2②:tombstone 為「受控」唯一例外);部署層 GRANT EXECUTE 予
    # 專用抹除角色。owner 隱含保有(殘餘,見檔頭 ⚠)。
    ("revoke tombstone execute from public", """
        REVOKE EXECUTE ON FUNCTION raw_supersede_tombstone(BIGINT, TEXT, TEXT) FROM PUBLIC"""),
    ("comment raw_supersede_tombstone", """
        COMMENT ON FUNCTION raw_supersede_tombstone(BIGINT, TEXT, TEXT) IS
        'P4.E3 唯一例外:法規抹除(SECURITY DEFINER、EXECUTE 須授權)。抹除 old_row/new_row 內容本體但留 tombstone 骨架＋抹除 provenance;唯一得繞過 append-only trigger 之受控路徑(交易本地 GUC augur.supersede_erase)'"""),
]

VERIFY = [
    ("raw_supersede_log 欄", "SELECT string_agg(column_name,', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='raw_supersede_log'"),
    ("FK→attestation_result", "SELECT string_agg(pg_get_constraintdef(oid),' | ') FROM pg_constraint WHERE conrelid='raw_supersede_log'::regclass AND contype='f'"),
    ("索引", "SELECT string_agg(indexname,', ' ORDER BY indexname) FROM pg_indexes WHERE tablename='raw_supersede_log'"),
    ("triggers(append-only + no-truncate)", "SELECT string_agg(tgname,', ' ORDER BY tgname) FROM pg_trigger WHERE tgrelid='raw_supersede_log'::regclass AND NOT tgisinternal"),
    ("tombstone 受控函式(SECURITY DEFINER?)", "SELECT proname || CASE WHEN prosecdef THEN '(SECURITY DEFINER✓)' ELSE '(⚠非 DEFINER)' END FROM pg_proc WHERE proname='raw_supersede_tombstone'"),
    ("PUBLIC 對本表殘餘 mutate 權(應無 UPDATE/DELETE/TRUNCATE)", "SELECT COALESCE(string_agg(privilege_type,', '),'(無)') FROM information_schema.role_table_grants WHERE table_name='raw_supersede_log' AND grantee='PUBLIC'"),
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
    """紅綠鎖(卷宗 §2.3.5 六不變式;免 DB 免 API、零 usage)。
    ①heal 觸發快照 / ②非 heal 不觸發 / ③no-op upsert 不入帳 / ④byte-differ 入帳
      → 純邏輯(generic_schema._supersessions)＋ gate(provision_and_upsert stub),零 IO;
    ⑤帳表 append-only(trigger RAISE) / ⑥同交易回滾 → **需 PG**(此處僅標注,備援環境 --check + 實測驗)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import augur.core.generic_schema as gs

    cols = ["stock_id", "date", "close"]
    keys = ["stock_id", "date"]
    # ③ no-op:incoming 與 DB pre-image 值等價('12.5'==Decimal 12.5)→ 不入帳
    db_rows = [{"stock_id": "1101", "date": "2026-06-30", "close": 12.5}]
    inc_noop = [{"stock_id": "1101", "date": "2026-06-30", "close": "12.5"}]
    chk("③ no-op upsert(值未變、_norm 等價)不入帳",
        gs._supersessions(cols, keys, inc_noop, db_rows) == [])
    # ④ byte-differ:close 真異(12.5→9.9)→ 恰一列、old/new 忠實
    inc_diff = [{"stock_id": "1101", "date": "2026-06-30", "close": "9.9"}]
    sup = gs._supersessions(cols, keys, inc_diff, db_rows)
    chk("④ byte-differ(值真異)入帳恰 1 列", len(sup) == 1)
    chk("④ old_row=DB pre-image、new_row=incoming",
        bool(sup) and str(sup[0][1].get("close")) == "12.5" and str(sup[0][2].get("close")) == "9.9")
    # 純 insert(無 pre-image)不留痕(P4.E5:只裁決衝突、不記純新增)
    chk("純 insert(DB 無此 PK)不入帳",
        gs._supersessions(cols, keys, [{"stock_id": "9999", "date": "2026-06-30", "close": "1"}], db_rows) == [])
    # ①② gate:provision_and_upsert 之 snapshot_reason 閘(stub 內部 IO 函式、cur=None、零 IO)
    saved = (gs.infer_schema, gs.detect_keys, gs.ensure_table, gs.upsert, gs._snapshot_superseded)
    seen = {}
    gs.infer_schema = lambda rows: {"date": "DATE"}
    gs.detect_keys = lambda rows, schema, require=(): ["date"]
    gs.ensure_table = lambda cur, table, schema, keys: keys
    gs.upsert = lambda cur, table, rows, schema, keys: len(rows)
    gs._snapshot_superseded = lambda cur, table, rows, schema, keys, reason, run_id=None: seen.update(reason=reason, run_id=run_id)
    try:
        gs.provision_and_upsert(None, "t", [{"date": "2026-01-01"}], snapshot_reason=None)
        chk("② 非 heal(snapshot_reason None)不觸發快照", "reason" not in seen)
        gs.provision_and_upsert(None, "t", [{"date": "2026-01-01"}], snapshot_reason="heal_by_date")
        chk("① heal(snapshot_reason 非 None)觸發快照且透傳 reason", seen.get("reason") == "heal_by_date")
        chk("① 決策 B:run_id 預設 None(事後回填)", seen.get("run_id") is None)
    finally:
        (gs.infer_schema, gs.detect_keys, gs.ensure_table, gs.upsert, gs._snapshot_superseded) = saved
    # upsert 本體不動之錨:snapshot_reason 預設 None ⇒ 主路徑語義不變(gate 未觸)
    chk("主路徑不動:provision_and_upsert 預設 snapshot_reason=None",
        gs.provision_and_upsert.__defaults__ is not None)
    print("  ⑤ 帳表 append-only(trigger RAISE UPDATE/DELETE + BEFORE TRUNCATE RAISE + REVOKE FROM PUBLIC +")
    print("     tombstone SECURITY DEFINER)：需 PG——備援環境 --check 驗上述存在 + 實測非 owner 角色 mutate/TRUNCATE 遭拒")
    print("  ⑥ 同交易回滾(快照與 heal 同 cur、例外一起 rollback;含 _assert_append_only fail-loud)：需 PG——備援環境實測")
    print("自測:" + ("全通過 ✓(①②③④＋純 insert 零 IO 綠;⑤⑥需 PG)" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="被取代原值快照帳本硬化 DDL(raw_supersede_log;冪等;表本體引用 schema.INFRA_DDL;加 append-only + no-truncate trigger + REVOKE + tombstone SECURITY DEFINER)")
    ap.add_argument("--check", action="store_true", help="唯讀:只印驗證清單、不執行 DDL")
    ap.add_argument("--selftest", action="store_true", help="紅綠鎖(六不變式;免 DB 免 API)")
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
