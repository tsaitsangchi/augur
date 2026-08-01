#!/usr/bin/env python3
"""🎯 `knowhow_auto_admit_state` 之誠實閘——降級、刪除、**再晉升**皆須通行證，未曾降級之升級不受阻。

守原則 #15（誠實：狀態不得被靜默改）、#12（帳本為唯一權威）。

起因（2026-07-30 自陳＋核驗共同指出）：該表原**無任何 trigger**，而該日依 Steward 拍板
對其 **145,949 列**執行 `admit_depth 9→7` 之降級——該次 UPDATE 完全沒有機械閘保護，
帳本（`knowhow_depth_reevaluation`）是唯一留痕。深度為顧問引文排序鍵
（`rank_citations_kh_first`），可信度直接影響作答。

**D4 再晉升鎖（2026-08-01 呈案、Steward 裁乙案）**：`upsert_state()` 之 `GREATEST` 單調升
使 07-30 降級可被例行 drain 靜默逆轉（07-31 實證 4 件無通行證爬回 depth 9）。故本閘增：
**曾被重評降級之 item（帳上有 depth_after<depth_before 列），admit_depth 上升＝再晉升，
須 token 通行證且由本閘自動留理由帳**（留痕機械化，不靠寫入者紀律）。

通行證 GUC 對照（皆 `SET LOCAL`＝交易域、commit/rollback 即失效）：
  - `augur.admit_depth_lower = 'on'`：降級通行證（既有）；仍須另留理由帳。
  - `augur.admit_depth_repromote = '<授權參照>'`：再晉升通行證——**非空 token**
    （如 RULING 編號／Steward 拍板紀錄），本閘以之為 run_id 自動 INSERT 理由帳。
  - `augur.change_actor`：操作者名；未設 fallback `current_user`，記入 evidence。

設計不變式（selftest 以壞變體驗紅逐條固化）：未曾降級 item 之升級零阻礙；降級鎖與
DELETE/TRUNCATE 鎖逐字保留；通行證＝非空 token；自動留帳列 depth_after>depth_before
不回饋污染「曾降級」謂詞。

**R1 回收（Steward 已裁；施作序＝先 code 後 DDL 末 R1）**：07-31 四筆再膨脹
（277948–277951）回收至 depth 7；SQL 併於本檔 `R1_RECYCLE_SQL`。
**執行者＝hugo TTY 親跑**（涉治權行為逆轉之回復；不代打人簽）——`--apply-r1` 有
isatty 人閘，非 TTY 一律拒絕。368764／368765 係新准入非再膨脹，不在回收射程。

執行指令矩陣
------------
    python3 scripts/migrate_admit_state_guard_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_admit_state_guard_ddl.py --check    # 唯讀驗證（含函式版本探針）
    python3 scripts/migrate_admit_state_guard_ddl.py --apply    # 掛閘（冪等；3c 統一 DDL 窗）
    python3 scripts/migrate_admit_state_guard_ddl.py --print-r1 # 印 R1 回收 SQL（唯讀）
    python3 scripts/migrate_admit_state_guard_ddl.py --apply-r1 # R1 回收（hugo TTY 親跑；isatty 人閘）
    python3 scripts/migrate_admit_state_guard_ddl.py --selftest # 紅綠自測（免 DB 免 API；壞變體驗紅）

⚠ **apply 時序**：核心 apply＝`CREATE OR REPLACE FUNCTION`（不取表鎖）；trigger 重建段有
   `SET lock_timeout='5s'` 快敗不排隊（#30）。**DDL 前引擎 clamp 須已落地**
   （auto_admit.progressive_item 之 D4 clamp）——否則 advance drain 首批撞閘整批 abort。
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

GUC = "augur.admit_depth_lower"
REPRO_GUC = "augur.admit_depth_repromote"

DDL = """
SET lock_timeout = '5s';

CREATE OR REPLACE FUNCTION admit_state_guard() RETURNS trigger AS $$
DECLARE
    _lower_pass text := current_setting('augur.admit_depth_lower', true);
    _repro_pass text := current_setting('augur.admit_depth_repromote', true);
    _actor      text := coalesce(current_setting('augur.change_actor', true), current_user);
    _was_demoted boolean := false;
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：DELETE 一律拒絕（只得改深度並留帳）';
    END IF;
    IF TG_OP = 'UPDATE'
       AND NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL
       AND NEW.admit_depth < OLD.admit_depth THEN
        IF _lower_pass IS DISTINCT FROM 'on' THEN
            RAISE EXCEPTION
              'admit_depth 下降（% → %）＝撤銷既有准入宣稱：須通行證 '
              '(SET LOCAL augur.admit_depth_lower = ''on'') 且須留理由帳',
              OLD.admit_depth, NEW.admit_depth;
        END IF;
    END IF;
    -- ── D4 再晉升鎖（2026-08-01 呈案）：曾被重評降級之 item，升 depth 須通行證＋理由帳。
    --    起因＝GREATEST 熱路徑使 07-30 降級 145,949 件可被例行 drain 靜默逆轉（07-31 已實證 4 筆）。
    IF TG_OP = 'UPDATE'
       AND NEW.target_kind = 'item'
       AND NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL
       AND NEW.admit_depth > OLD.admit_depth
       AND NEW.target_id ~ '^[0-9]+$' THEN
        SELECT EXISTS (
            SELECT 1
              FROM knowhow_depth_reevaluation r
             WHERE r.item_id = NEW.target_id::bigint
               AND r.depth_after < r.depth_before
        ) INTO _was_demoted;
        IF _was_demoted THEN
            IF _repro_pass IS NULL OR btrim(_repro_pass) = '' THEN
                RAISE EXCEPTION
                  'item % 曾經重評降級（帳＝knowhow_depth_reevaluation）：admit_depth 上升（% → %）＝再晉升，'
                  '須通行證 SET LOCAL augur.admit_depth_repromote = ''<授權參照>''（如 RULING 編號／Steward 拍板紀錄）；'
                  '本閘將以該參照自動留理由帳',
                  NEW.target_id, OLD.admit_depth, NEW.admit_depth;
            END IF;
            INSERT INTO knowhow_depth_reevaluation
                   (run_id, item_id, depth_before, depth_after, reason, evidence)
            VALUES (_repro_pass, NEW.target_id::bigint, OLD.admit_depth, NEW.admit_depth,
                    '再晉升：曾降級 item 經通行證授權升深（admit_state_guard 自動留帳）',
                    jsonb_build_object(
                        'guard',          'admit_state_guard.repromote',
                        'actor',          _actor,
                        'authorized_via', _repro_pass,
                        'last_run_id',    NEW.last_run_id));
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION admit_state_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：TRUNCATE 一律拒絕';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_admit_state_guard ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_guard
    BEFORE UPDATE OR DELETE ON knowhow_auto_admit_state
    FOR EACH ROW EXECUTE FUNCTION admit_state_guard();

DROP TRIGGER IF EXISTS trg_admit_state_no_truncate ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_no_truncate
    BEFORE TRUNCATE ON knowhow_auto_admit_state
    FOR EACH STATEMENT EXECUTE FUNCTION admit_state_no_truncate();
"""

# R1（Steward 裁「回收」）：07-31 四筆 GREATEST 再膨脹回收至 7；呈案 §3.4 原文。
# 執行者＝hugo（change_actor 如實；AI 不代跑——apply_r1 有 isatty 人閘）。
R1_RECYCLE_SQL = """
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL augur.admit_depth_lower = 'on';      -- 降級通行證（既有閘）
SET LOCAL augur.change_actor = 'hugo';         -- Steward 親跑；AI 不代打
UPDATE knowhow_auto_admit_state
   SET admit_depth = 7, updated_at = now()
 WHERE target_kind='item'
   AND target_id IN ('277948','277949','277950','277951')
   AND admit_depth = 9;                        -- 冪等前提：仍為 9 才動
INSERT INTO knowhow_depth_reevaluation (run_id, item_id, depth_before, depth_after, reason, evidence)
SELECT 'kh-redemote-D4-20260801', v.i, 9, 7,
       '回收 07-31 GREATEST 再膨脹（無通行證之再晉升；KH8 殘餘二：band=high 非 per-item 強證據）',
       jsonb_build_object('via','D4_repromotion_lock 呈案 §3.4',
                          'reinflated_at','2026-07-31 08:57:37+08',
                          'run_ids', jsonb_build_array(521810,521811,521812,521813))
  FROM (VALUES (277948),(277949),(277950),(277951)) v(i);
COMMIT;
"""


def ddl_invariants(ddl: str) -> list[str]:
    """閘 DDL 載體之不變式檢核。**純函式**——回傳被違反者清單（空＝全守）。
    本 DDL 字串即被逐字執行之行為載體，對載體驗形＝對行為驗形（#35 型3 疑慮不適用於
    「字串就是 payload」情形；先例＝migrate_alpha_headline_anchor_ddl）；selftest 以壞變體驗紅。
    行為本身之最終證明＝呈案 §6 窗內負測／正測（BEGIN…ROLLBACK 探針）。"""
    bad: list[str] = []
    body = ddl.split("admit_state_no_truncate")[0]  # guard 函式體（含前置 SET）
    if "TG_OP = 'DELETE'" not in body or "DELETE 一律拒絕" not in body:
        bad.append("delete_locked")
    if "BEFORE TRUNCATE" not in ddl or "TRUNCATE 一律拒絕" not in ddl:
        bad.append("truncate_locked")
    if "NEW.admit_depth < OLD.admit_depth" not in body or GUC not in body:
        bad.append("demote_needs_pass")
    if body.count("NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL") != 2:
        bad.append("null_safe_both_branches")
    # 升方向唯一攔截點＝曾降級者（EXISTS 繫於降級帳）；未曾降級之升級零阻礙
    if (body.count("NEW.admit_depth > OLD.admit_depth") != 1
            or "r.depth_after < r.depth_before" not in body):
        bad.append("repromote_scope_demoted_only")
    if REPRO_GUC not in body:
        bad.append("repromote_guc")
    if "btrim" not in body:
        bad.append("token_nonempty")
    if "INSERT INTO knowhow_depth_reevaluation" not in body:
        bad.append("auto_ledger")
    if "NEW.target_kind = 'item'" not in body or "~ '^[0-9]+$'" not in body:
        bad.append("item_scope_guard")
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    if ddl.count("DROP TRIGGER IF EXISTS") != 2:
        bad.append("idempotent_triggers")
    if body.count("% → %") != 2:
        bad.append("audit_msg_old_new_both_branches")
    if "IS DISTINCT FROM OLD.admit_depth" in ddl:
        bad.append("no_blanket_update_block")
    return bad


def r1_invariants(sql: str) -> list[str]:
    """R1 回收 SQL 之不變式檢核（純函式；射程明界＝僅 4 筆再膨脹）。"""
    bad: list[str] = []
    if "'277948','277949','277950','277951'" not in sql:
        bad.append("scope_four_items")
    if "368764" in sql or "368765" in sql:
        bad.append("scope_creep_new_admissions")  # 新准入二筆不在回收射程（呈案 §3.4 明界）
    if "AND admit_depth = 9" not in sql:
        bad.append("idempotent_only_if_still_9")
    if f"{GUC} = 'on'" not in sql:
        bad.append("demote_pass_present")
    if "INSERT INTO knowhow_depth_reevaluation" not in sql or "kh-redemote-D4-20260801" not in sql:
        bad.append("ledger_insert_with_run_id")
    if " 9, 7," not in sql:
        bad.append("depth_9_to_7")
    if "BEGIN;" not in sql or "COMMIT;" not in sql:
        bad.append("explicit_txn")
    return bad


def check(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.knowhow_auto_admit_state')")
    if not cur.fetchone()[0]:
        print("FAIL knowhow_auto_admit_state 不存在")
        return 1
    cur.execute(
        """SELECT tgname FROM pg_trigger
            WHERE tgrelid='knowhow_auto_admit_state'::regclass AND NOT tgisinternal ORDER BY 1"""
    )
    trg = [r[0] for r in cur.fetchall()]
    print(f"trigger：{trg or '✗ 無（任何人可靜默改准入深度，而深度為引文排序鍵）'}")
    ok = "trg_admit_state_guard" in trg and "trg_admit_state_no_truncate" in trg
    # 函式版本探針（防「trigger 在、函式舊」假綠——trigger 名不隨函式體換版而變）
    cur.execute(
        "SELECT prosrc LIKE '%admit_depth_repromote%' FROM pg_proc WHERE proname='admit_state_guard'"
    )
    row = cur.fetchone()
    repro = bool(row and row[0])
    print(f"再晉升鎖：{'✓ 函式含 repromote 分支' if repro else '✗ 函式為舊版（升方向裸奔）'}")
    ok = ok and repro
    print("PASS 誠實閘就位（降級／刪除／再晉升須通行證）" if ok else "FAIL 未就位（跑 --apply）")
    return 0 if ok else 1


def apply(conn) -> int:
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    print("已掛閘（冪等）；未曾降級之升級不受阻、降級／刪除／再晉升須通行證")
    return check(conn)


def print_r1() -> int:
    print("-- R1 回收 SQL（hugo TTY 親跑；施作序＝DDL 之後）")
    print(R1_RECYCLE_SQL.strip())
    return 0


def apply_r1(conn) -> int:
    if not sys.stdin.isatty():
        print("✗ --apply-r1 須於 TTY 親跑（執行者＝hugo；治權行為逆轉之回復不代打——stdin 非 TTY 拒絕）")
        return 1
    cur = conn.cursor()
    cur.execute(
        "SELECT prosrc LIKE '%admit_depth_repromote%' FROM pg_proc WHERE proname='admit_state_guard'"
    )
    row = cur.fetchone()
    if not (row and row[0]):
        print("✗ 施作序違反：admit_state_guard 尚無 repromote 分支——先 --apply 再 --apply-r1（呈案 §4）")
        return 1
    cur.execute(
        "SELECT count(*) FROM knowhow_depth_reevaluation WHERE run_id='kh-redemote-D4-20260801'"
    )
    if cur.fetchone()[0] > 0:
        print("· R1 已執行過（帳上有 kh-redemote-D4-20260801 列）——不重複記帳，跳過")
        return 0
    ans = input("R1：回收 277948–277951 至 depth 7 並留帳。輸入 R1-GO 確認：").strip()
    if ans != "R1-GO":
        print("未確認，取消")
        return 1
    old_ac = conn.autocommit
    conn.rollback()   # 上方讀查詢已開隱式交易——autocommit 切換須在交易外(psycopg2;2026-08-01 hugo 實跑 ProgrammingError 實證)
    conn.autocommit = True
    try:
        cur.execute(R1_RECYCLE_SQL)
    finally:
        conn.autocommit = old_ac
    cur.execute(
        """SELECT count(*) FROM knowhow_auto_admit_state
            WHERE target_kind='item'
              AND target_id IN ('277948','277949','277950','277951') AND admit_depth=7"""
    )
    n7 = cur.fetchone()[0]
    cur.execute(
        "SELECT count(*) FROM knowhow_depth_reevaluation WHERE run_id='kh-redemote-D4-20260801'"
    )
    nled = cur.fetchone()[0]
    print(f"R1 完成：depth=7 者 {n7}/4；理由帳列 {nled}/4")
    return 0 if (n7 == 4 and nled == 4) else 1


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("本尊 R1 SQL 全不變式守住（綠）", r1_invariants(R1_RECYCLE_SQL) == [])
    chk("驗紅:拔掉升方向分支（退回舊版）→ repromote_scope 報違",
        "repromote_scope_demoted_only" in ddl_invariants(
            DDL.replace("NEW.admit_depth > OLD.admit_depth", "FALSE")))
    chk("驗紅:EXISTS 不繫降級帳（謂詞恆真）→ repromote_scope 報違",
        "repromote_scope_demoted_only" in ddl_invariants(
            DDL.replace("r.depth_after < r.depth_before", "TRUE")))
    chk("驗紅:通行證改可空白 → token_nonempty 報違",
        "token_nonempty" in ddl_invariants(DDL.replace("btrim(_repro_pass) = ''", "FALSE")))
    chk("驗紅:拔掉自動留帳 INSERT → auto_ledger 報違",
        "auto_ledger" in ddl_invariants(
            DDL.replace("INSERT INTO knowhow_depth_reevaluation", "-- gutted")))
    chk("驗紅:拔掉降級鎖 → demote_needs_pass 報違（既有閘逐字保留之鎖）",
        "demote_needs_pass" in ddl_invariants(
            DDL.replace("NEW.admit_depth < OLD.admit_depth", "FALSE")))
    chk("驗紅:升方向改全面攔截 → no_blanket_update_block 報違（未曾降級者不得受阻）",
        "no_blanket_update_block" in ddl_invariants(
            DDL.replace("NEW.admit_depth > OLD.admit_depth",
                        "NEW.admit_depth IS DISTINCT FROM OLD.admit_depth")))
    chk("驗紅:拔掉 item 限定/數字防呆 → item_scope_guard 報違",
        "item_scope_guard" in ddl_invariants(DDL.replace("~ '^[0-9]+$'", "IS NOT NULL")))
    chk("驗紅:R1 拔冪等前提（仍為 9 才動）→ 報違",
        "idempotent_only_if_still_9" in r1_invariants(
            R1_RECYCLE_SQL.replace("AND admit_depth = 9;", ";")))
    chk("驗紅:R1 射程擴至新准入二筆 → scope_creep 報違",
        "scope_creep_new_admissions" in r1_invariants(
            R1_RECYCLE_SQL.replace("'277951'", "'277951','368764'")))
    chk("驗紅:R1 拔降級通行證 → demote_pass_present 報違",
        "demote_pass_present" in r1_invariants(
            R1_RECYCLE_SQL.replace("SET LOCAL augur.admit_depth_lower = 'on';", "")))
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="knowhow_auto_admit_state 誠實閘（DDL；冪等）＋D4 再晉升鎖＋R1 回收")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--print-r1", action="store_true")
    ap.add_argument("--apply-r1", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.print_r1:
        return print_r1()
    from augur.core import db

    with db.connect() as conn:
        if a.apply_r1:
            return apply_r1(conn)
        return apply(conn) if a.apply else check(conn)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
        sys.exit(main(["--check"]))
    sys.exit(main())
