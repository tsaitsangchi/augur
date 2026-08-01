#!/usr/bin/env python3
"""🎯 sim 軸機械閘補強 DDL——專章判準三 CHECK＋arms_covered 欄＋kill_switch scope 加 sim（H2 件三）。

守原則 #6（--apply 才動 DB；DROP IF EXISTS＋ADD＝冪等可重跑）、#15（CHECK 落 DB 層＝紅燈會亮；
selftest 以壞變體驗紅）、#29a/d、#30（lock_timeout 5s 絕不排隊；dump 期間禁跑）。

內容（SSOT＝reports/w2_20260801/H2_sim_first_method.md §3.3；Steward 裁決「照案＋丙甲」）：
  (1) chk_sce_llm_is_synthetic：llm_local 候選必攜 is_synthetic（專章 §2.3 機械化）
  (2) chk_seil_gain_basis_on_terminal：終態輪必聲明 gain_basis（專章 §3.6 NULL 缺口）
  (3) arms_covered 欄＋chk_sev_five_arm_floor：promoted 判決須涵蓋五臂（專章 §3.4）
  (4) chk_kill_switch_scope 值域加 'sim'（live 親驗：現 CHECK 封閉四值，單靠 INSERT 必被擋）
  DML：sim 煞車列 INSERT（NOT EXISTS 冪等；丙甲＝set_by 記腳本名之誠實 provenance，非人簽）。

**排窗紀律**：本支屬波3統一 DDL 窗（3c，與 D4/B4/E2 同窗）——備妥不跑；dump 期間禁 DDL（#30）。
**同批 code diff（apply 時同一變更集落地，本支不改碼）**：
  src/augur/philosophy/evolution.py:242  KILL_SCOPES = ("tw","lai","raw","global","sim")
  scripts/set_evolution_kill_switch.py:52  selftest 封閉集斷言同步五值（改斷言先跑＝驗紅，改 :242 後轉綠）
**誠實記載**：sim scope 列落地後初期零消費者（run_sim_evolution_iteration.py W5 才接線）——
  不得宣稱「sim 軸已受煞車保護」；此列＝作用點預置。

執行指令矩陣
------------
    python scripts/migrate_sim_constraints_ddl.py            # 無參數=--check（唯讀）
    python scripts/migrate_sim_constraints_ddl.py --check    # 唯讀：四閘/欄/煞車列/code 同步狀態
    python scripts/migrate_sim_constraints_ddl.py --apply    # 落地 DDL＋DML（冪等；3c 統一窗、dump 期間禁跑）
    python scripts/migrate_sim_constraints_ddl.py --selftest # 紅綠自測（免 DB；含壞 DDL/壞 DML 驗紅）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

DDL = """
SET lock_timeout = '5s';

-- (1) 專章 §2.3 機械化：llm_local 候選必攜 synthetic 標記（八表 0 列，驗證零成本）
ALTER TABLE sim_evolution_candidate DROP CONSTRAINT IF EXISTS chk_sce_llm_is_synthetic;
ALTER TABLE sim_evolution_candidate
  ADD CONSTRAINT chk_sce_llm_is_synthetic
  CHECK (origin <> 'llm_local' OR is_synthetic);

-- (2) 專章 §3.6 NULL 缺口封閉：終態輪必須聲明目標函數基礎
ALTER TABLE sim_evolution_iteration_ledger DROP CONSTRAINT IF EXISTS chk_seil_gain_basis_on_terminal;
ALTER TABLE sim_evolution_iteration_ledger
  ADD CONSTRAINT chk_seil_gain_basis_on_terminal
  CHECK (status NOT IN ('succeeded','failed') OR gain_basis IS NOT NULL);

-- (3) 專章 §3.4 五臂完備性：promoted 之判決須涵蓋五臂（robot 為加嚴第六臂、不強制）
ALTER TABLE sim_evolution_verdict ADD COLUMN IF NOT EXISTS arms_covered text[];
ALTER TABLE sim_evolution_verdict DROP CONSTRAINT IF EXISTS chk_sev_five_arm_floor;
ALTER TABLE sim_evolution_verdict
  ADD CONSTRAINT chk_sev_five_arm_floor
  CHECK (verdict <> 'promoted' OR
         arms_covered @> ARRAY['live','ceiling','floor','shuffled','mismatched']::text[]);

-- (4) kill_switch scope 值域加 sim（親驗：現 CHECK 封閉四值＝INSERT 之物理前提；表僅 4 列驗證瞬時）
ALTER TABLE evolution_kill_switch DROP CONSTRAINT IF EXISTS chk_kill_switch_scope;
ALTER TABLE evolution_kill_switch
  ADD CONSTRAINT chk_kill_switch_scope
  CHECK (scope = ANY (ARRAY['tw'::text,'lai'::text,'raw'::text,'global'::text,'sim'::text]));
"""

DML = """
INSERT INTO evolution_kill_switch (switch_id, state, set_by, reason, scope)
SELECT (SELECT max(switch_id) + 1 FROM evolution_kill_switch),
       'clear', 'migrate_sim_constraints_ddl',
       'sim 軸開軸前置：緊急煞車作用點（初期零消費者，W5 driver 接線）', 'sim'
WHERE NOT EXISTS (SELECT 1 FROM evolution_kill_switch WHERE scope = 'sim');
"""

NEW_CONSTRAINTS = ("chk_sce_llm_is_synthetic", "chk_seil_gain_basis_on_terminal",
                   "chk_sev_five_arm_floor")
FIVE_ARMS = "ARRAY['live','ceiling','floor','shuffled','mismatched']::text[]"
FIVE_SCOPES = "ARRAY['tw'::text,'lai'::text,'raw'::text,'global'::text,'sim'::text]"


def ddl_invariants(ddl: str) -> list[str]:
    """DDL 載體不變式檢核。**純函式**——回傳被違反者清單（空=全守）。
    DDL 字串即被逐字執行之行為載體，對載體驗形＝對行為驗形（#35 型3 疑慮不適用於
    「字串就是 payload」情形）；selftest 以壞變體驗紅。"""
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    for name in NEW_CONSTRAINTS:
        if not (ddl.count(f"DROP CONSTRAINT IF EXISTS {name}") == 1
                and ddl.count(f"ADD CONSTRAINT {name}") == 1):
            bad.append(f"{name}_drop_then_add")
    if "CHECK (origin <> 'llm_local' OR is_synthetic)" not in ddl:
        bad.append("llm_synthetic_predicate")
    if "CHECK (status NOT IN ('succeeded','failed') OR gain_basis IS NOT NULL)" not in ddl:
        bad.append("terminal_gain_basis_predicate")
    if ddl.count(FIVE_ARMS) != 1 or "arms_covered @>" not in ddl:
        bad.append("five_arm_floor_predicate")
    if "ADD COLUMN IF NOT EXISTS arms_covered text[]" not in ddl:
        bad.append("arms_covered_column")
    if ddl.count(FIVE_SCOPES) != 1 or ddl.count("DROP CONSTRAINT IF EXISTS chk_kill_switch_scope") != 1:
        bad.append("scope_five_values")
    for kw in ("DROP TABLE", "TRUNCATE", "DELETE FROM"):
        if kw in ddl:
            bad.append("no_destructive")
            break
    if "INSERT INTO" in ddl:
        bad.append("ddl_no_dml")
    return bad


def dml_invariants(dml: str) -> list[str]:
    """DML 載體不變式檢核（純函式；空=全守）。"""
    bad = []
    if dml.count("INSERT INTO evolution_kill_switch") != 1:
        bad.append("single_insert")
    if "WHERE NOT EXISTS" not in dml or "scope = 'sim'" not in dml:
        bad.append("insert_idempotent_guard")
    if "'clear'" not in dml or "'halt'" in dml:
        bad.append("initial_state_clear")
    if "'migrate_sim_constraints_ddl'" not in dml or "'hugo'" in dml:
        bad.append("set_by_script_provenance")  # 丙甲：腳本做的記腳本名；寫人名=代打人簽
    for kw in ("UPDATE", "DELETE", "TRUNCATE", "DROP"):
        if kw in dml:
            bad.append("dml_insert_only")
            break
    return bad


def _code_scopes_have_sim() -> bool:
    from augur.philosophy.evolution import KILL_SCOPES
    return "sim" in KILL_SCOPES


def _check(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        for name in NEW_CONSTRAINTS:
            cur.execute("SELECT count(*) FROM pg_constraint WHERE conname=%s", (name,))
            ok = cur.fetchone()[0] == 1
            print(f"  {'✓' if ok else '·'} {name} {'在位' if ok else '未落地（波3窗）'}")
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name='sim_evolution_verdict' AND column_name='arms_covered'")
        ok = cur.fetchone()[0] == 1
        print(f"  {'✓' if ok else '·'} sim_evolution_verdict.arms_covered {'在' if ok else '未落地（波3窗）'}")
        cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conname='chk_kill_switch_scope'")
        row = cur.fetchone()
        has_sim = bool(row) and "'sim'" in row[0]
        print(f"  {'✓' if has_sim else '·'} chk_kill_switch_scope 含 sim: {has_sim}")
        cur.execute("SELECT state, set_by FROM evolution_kill_switch WHERE scope='sim'")
        row = cur.fetchone()
        print(f"  {'✓' if row else '·'} 煞車列 scope=sim: " +
              (f"state={row[0]} set_by={row[1]}" if row else "無（波3窗 DML）"))
    code_ok = _code_scopes_have_sim()
    print(f"  {'✓' if code_ok else '·'} code KILL_SCOPES 含 sim: {code_ok}"
          + ("" if code_ok else "（同批 code diff 待落——evolution.py:242＋set_evolution_kill_switch.py:52）"))
    if row and not code_ok:
        print("  ⚠ DB 已有 sim 列但 code 未同步——立即補 code diff（同一變更集義務）")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute(DDL)
        cur.execute(DML)
        cur.execute("SELECT count(*) FROM evolution_kill_switch WHERE scope='sim'")
        n = cur.fetchone()[0]
        if n != 1:
            print(f"✗ sim 煞車列數異常={n}（預期 1）——整包回滾")
            raise SystemExit(1)
    print("✓ DDL＋DML 冪等完成")
    print("⚠ 誠實記載：sim scope 初期零消費者（W5 driver 才接線）——不得宣稱「sim 軸已受煞車保護」")
    if not _code_scopes_have_sim():
        print("⚠ 同批 code diff 未落：evolution.py:242 KILL_SCOPES 加 'sim'＋"
              "set_evolution_kill_switch.py:52 斷言同步（先改斷言驗紅、再改 :242 轉綠）")
    return _check(conn)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("本尊 DML 全不變式守住（綠）", dml_invariants(DML) == [])
    chk("驗紅：scope 五值陣列拿掉 'sim' → scope_five_values 報違",
        "scope_five_values" in ddl_invariants(DDL.replace(",'sim'::text", "")))
    chk("驗紅：llm CHECK 條件反轉 → llm_synthetic_predicate 報違",
        "llm_synthetic_predicate" in ddl_invariants(
            DDL.replace("origin <> 'llm_local' OR is_synthetic",
                        "origin <> 'llm_local' OR NOT is_synthetic")))
    chk("驗紅：五臂少一臂 → five_arm_floor_predicate 報違",
        "five_arm_floor_predicate" in ddl_invariants(DDL.replace("'mismatched'", "'x'")))
    chk("驗紅：終態 CHECK 拿掉 → 報違",
        "terminal_gain_basis_predicate" in ddl_invariants(
            DDL.replace("OR gain_basis IS NOT NULL", "")))
    chk("驗紅：少 DROP IF EXISTS（失冪等）→ 報違",
        "chk_sce_llm_is_synthetic_drop_then_add" in ddl_invariants(
            DDL.replace("ALTER TABLE sim_evolution_candidate DROP CONSTRAINT IF EXISTS "
                        "chk_sce_llm_is_synthetic;", "", 1)))
    chk("驗紅：DDL 夾帶 DROP TABLE → no_destructive 報違",
        "no_destructive" in ddl_invariants(DDL + "\nDROP TABLE sim_evolution_candidate;"))
    chk("驗紅：DML set_by 改人名 → set_by_script_provenance 報違（代打人簽）",
        "set_by_script_provenance" in dml_invariants(
            DML.replace("'migrate_sim_constraints_ddl'", "'hugo'")))
    chk("驗紅：DML 拿掉 NOT EXISTS（失冪等）→ 報違",
        "insert_idempotent_guard" in dml_invariants(
            DML.replace("WHERE NOT EXISTS (SELECT 1 FROM evolution_kill_switch WHERE scope = 'sim')",
                        "")))
    chk("驗紅：DML state 改 halt → initial_state_clear 報違",
        "initial_state_clear" in dml_invariants(DML.replace("'clear'", "'halt'")))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="sim 軸機械閘 DDL（H2 件三；波3統一窗 3c 才 --apply）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.apply):
        print(__doc__.split("執行指令矩陣")[1].split("------\n")[-1])
    from augur.core import db
    import psycopg2
    try:  # graceful（#29a）：connect 為 contextmanager，例外在 __enter__ 才炸，故包整個 with
        with db.connect() as conn:
            return _apply(conn) if a.apply else _check(conn)
    except psycopg2.OperationalError as e:
        print(f"✗ DB 連線失敗：{str(e).strip()}（需 .env 環境；set -a && . ./.env && set +a）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
