#!/usr/bin/env python3
"""🎯 sim 迭代帳本開列＋FK——把 `sim_run_link.iteration_uid` 焊到帳本上（M-T1）。

這支在做什麼（白話）：`run_sim_calibration_cell.py --apply` 首格會一次寫 52 列 `sim_run_link`，
每列帶一個 `iteration_uid`；但該欄**原本沒有 FK**，而 `sim_run_link` 掛了 `simlink_no_delete`
（BEFORE DELETE 恆拒）⇒ **一落地就再也刪不掉**。若那個 uid 在
`sim_evolution_iteration_ledger` 沒有對應列，孤兒 uid 就**永久**留著，事後只剩兩條路：
回填一列去遷就已寫死的 uid（＝追溯粉飾），或永遠加不上這條 FK。
故本支在首格 `--apply` **之前**把 FK 焊上：帳本列不先在，link 物理上就寫不進去。

守 #6（`--apply` 才動 DB；DROP IF EXISTS＋ADD＝冪等可重跑）· #12（uid 推導與開輪 SQL 之單一住所
＝`run_sim_calibration_cell.py`，本支只呼叫不複製）· #15（機械閘落 DB 層，紅燈由 FK 自己亮；
selftest 以壞變體驗紅）· #29a/b/d（anchor 資料驅動現查交易日曆，不寫死日期）· #30（`SET lock_timeout`
絕不排隊；`--apply` 前先驗 dump 鎖與未授予鎖，dump 期間拒跑）。

**設計 SSOT**＝`reports/augur_optimization_master_plan_20260803.md` §2 第 2 步（M-T1）。

**射程誠實（不誇稱）**：
  - FK 只擋「link 指向不存在之帳本列」；**不**保證那一列的內容正確、更不保證輪已被評估。
  - 本支**不**寫 `succeeded`/`failed` 終態、**不**寫 `gain`/`gain_basis`——產格當下無校準差可比，
    終態屬 W4 判決端（`decide_sim_verdict.py`，未實作）。
  - 本支**不**填任何人簽欄（帳本無 decided_by/approved_by；`closed_by` 為執行體名，非人名）。
  - anchor 未實現時 `--open-ledger` **拒開列**（不猜未來交易日曆 #8）；此時 FK 仍可先焊，
    因 runner `--apply` 會在寫 link 之前自己開輪（同一住所之 `ensure_iteration_row`）。

執行指令矩陣
------------
    python3 scripts/migrate_sim_ledger_fk_ddl.py               # 無參數＝--check（唯讀）
    python3 scripts/migrate_sim_ledger_fk_ddl.py --check       # 唯讀：FK 現況/兩表列數/孤兒數/anchor
    python3 scripts/migrate_sim_ledger_fk_ddl.py --apply       # 焊 FK（冪等；dump 進行中即拒跑）
    python3 scripts/migrate_sim_ledger_fk_ddl.py --open-ledger # 開本輪帳本列 planned（anchor 已實現才開）
    python3 scripts/migrate_sim_ledger_fk_ddl.py --selftest    # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import fcntl
import sys

import _bootstrap  # noqa: F401

FK_NAME = "sim_run_link_iteration_uid_fkey"
CHILD = "sim_run_link"
PARENT = "sim_evolution_iteration_ledger"
DUMP_LOCK = "/tmp/augur_pgdump.lock"

# DDL 字串即被逐字執行之行為載體（「字串就是 payload」）⇒ 對載體驗形＝對行為驗形；
# selftest 以壞變體驗紅（#35 型3 之疑慮不適用於此情形；同 migrate_sim_constraints_ddl.py）。
DDL = f"""
SET LOCAL lock_timeout = '5s';

-- M-T1：孤兒 iteration_uid 於 DB 層排除（child 0 列時驗證瞬時；DROP+ADD＝冪等重跑）
ALTER TABLE {CHILD} DROP CONSTRAINT IF EXISTS {FK_NAME};
ALTER TABLE {CHILD}
  ADD CONSTRAINT {FK_NAME}
  FOREIGN KEY (iteration_uid) REFERENCES {PARENT}(iteration_uid);
"""


def ddl_invariants(ddl: str) -> list[str]:
    """DDL 載體不變式檢核。**純函式**——回傳被違反者清單（空＝全守）。"""
    bad = []
    if "SET LOCAL lock_timeout" not in ddl:
        bad.append("lock_timeout")            # #30：絕不排隊（排隊中的 AccessExclusive 會鎖全表）
        # LOCAL＝只作用於本交易，不污染連線後續（psycopg2 預設 autocommit=False ⇒ 恆在交易內）
    if not (ddl.count(f"DROP CONSTRAINT IF EXISTS {FK_NAME}") == 1
            and ddl.count(f"ADD CONSTRAINT {FK_NAME}") == 1):
        bad.append("fk_drop_then_add")        # 失冪等：重跑即炸
    if f"FOREIGN KEY (iteration_uid) REFERENCES {PARENT}(iteration_uid)" not in ddl:
        bad.append("fk_points_at_ledger")     # 指錯表＝閘等於不存在
    if "ON DELETE CASCADE" in ddl or "ON DELETE SET NULL" in ddl:
        bad.append("no_cascade")              # 帳本受 delete-only guard，link 不得因級聯被抹
    if "NOT VALID" in ddl:
        bad.append("must_validate")           # NOT VALID＝存量不檢＝假綠
    for kw in ("DROP TABLE", "TRUNCATE", "DELETE FROM", "INSERT INTO", "UPDATE "):
        if kw in ddl:
            bad.append("ddl_only_no_dml_no_destructive")
            break
    return bad


def _dump_running() -> bool:
    """dump 進行中？（#30：pg_dump 持 AccessShare，DDL 之 AccessExclusive 會排隊並反向鎖全表）"""
    try:
        fd = open(DUMP_LOCK, "a")
    except OSError:
        return False                          # 鎖檔開不了＝視同無 dump（不因輔助檢查而擋死主流程）
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except OSError:
        return True
    finally:
        fd.close()


def _anchor(cur):
    """現查 anchor（＝門 approved 之次一**已實現**交易日）與本輪 uid；未實現回 (None, None)。

    #12：門載入、日曆載入、uid 推導全部呼叫 run_sim_calibration_cell（產格端同一住所），
    本支不複製任何一份——兩邊若漂移，寫進去的 uid 與開好的列就對不上。
    """
    from run_sim_calibration_cell import _load_gate, _load_calendar, iteration_uid_for
    row = _load_gate(cur)
    if row is None:
        return None, None
    cal = _load_calendar(cur, row["approved_date"])
    if not cal:
        return None, None
    return cal[0], iteration_uid_for(cal[0])


def _counts(cur):
    cur.execute(f"SELECT count(*) FROM {CHILD}")                              # noqa: S608
    n_child = cur.fetchone()[0]
    cur.execute(f"SELECT count(*) FROM {PARENT}")                             # noqa: S608
    n_parent = cur.fetchone()[0]
    cur.execute(f"""SELECT count(*) FROM {CHILD} l
                    LEFT JOIN {PARENT} g USING (iteration_uid)
                    WHERE g.iteration_uid IS NULL""")                         # noqa: S608
    n_orphan = cur.fetchone()[0]
    return n_child, n_parent, n_orphan


def _fk_def(cur):
    cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname=%s "
                "AND conrelid=%s::regclass", (FK_NAME, CHILD))
    row = cur.fetchone()
    return row[0] if row else None


def _report(cur) -> int:
    fk = _fk_def(cur)
    n_child, n_parent, n_orphan = _counts(cur)
    print(f"  {'✓' if fk else '·'} FK {FK_NAME}: {fk or '未落地'}")
    print(f"  · 列數 {CHILD}={n_child}／{PARENT}={n_parent}")
    print(f"  {'✓' if n_orphan == 0 else '✗'} 孤兒 uid（link 無對應帳本列）={n_orphan}"
          + ("（⚠ 兩表 0 列＝trivially 0，首格落地後重跑才有鑑別力）" if n_child == 0 else ""))
    anchor, uid = _anchor(cur)
    if anchor is None:
        print("  · anchor 未實現（門 approved 次一交易日尚未入庫）⇒ 本輪 uid 尚不可推導；"
              "帳本列由 runner --apply 當下自開（不猜未來日曆 #8）")
    else:
        cur.execute(f"SELECT status, opened_at::date FROM {PARENT} "                # noqa: S608
                    "WHERE iteration_uid=%s", (uid,))
        row = cur.fetchone()
        print(f"  {'✓' if row else '·'} anchor={anchor} 本輪 uid={uid}："
              + (f"帳本列在（status={row[0]} opened={row[1]}）" if row else "帳本列未開"))
    return 0


def _check(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        rc = _report(cur)
    print(f"  · dump 鎖 {DUMP_LOCK}：{'⚠ 進行中（DDL 須等）' if _dump_running() else '空閒（可下 DDL）'}")
    return rc


def _apply(conn) -> int:
    from augur.core import db
    if _dump_running():
        print(f"✗ dump 進行中（{DUMP_LOCK} 被持有）——依 #30 拒下 DDL，零寫入。dump 完再跑。")
        return 1
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_locks WHERE NOT granted")
        waiting = cur.fetchone()[0]
        if waiting:
            print(f"✗ 現有 {waiting} 個未授予鎖在排隊——DDL 會加劇鎖風暴（#30），拒跑零寫入。")
            return 1
        before = _counts(cur)
        print(f"  DDL 前對帳：{CHILD}={before[0]} {PARENT}={before[1]} 孤兒={before[2]}")
        if before[2]:
            print(f"✗ 已有 {before[2]} 列孤兒 uid——FK 加不上（且 link 受 no_delete 恆拒不可清）。"
                  "須先由 Steward 裁定回填或另立補救，本支拒動，零寫入。")
            return 1
        cur.execute(DDL)
        after = _counts(cur)
        fk = _fk_def(cur)
        if not fk:
            print("✗ DDL 後 pg_constraint 查無 FK——整包回滾")
            raise SystemExit(1)
        if after != before:
            print(f"✗ DDL 前後列數不一致 {before} → {after}（DDL 不得動資料）——整包回滾")
            raise SystemExit(1)
        print(f"  DDL 後對帳：{CHILD}={after[0]} {PARENT}={after[1]} 孤兒={after[2]}（與前相同）")
    print(f"✓ FK 焊上：{fk}")
    print("⚠ 誠實記載：FK 只擋「指向不存在之帳本列」；不保證該列內容正確、不代表輪已評估。")
    return _check(conn)


def _open_ledger(conn) -> int:
    """開本輪帳本列（planned）。anchor 未實現即拒開——不猜未來交易日曆（#8）。"""
    from augur.core import db
    from run_sim_calibration_cell import ensure_iteration_row
    with db.transaction(conn) as cur:
        anchor, uid = _anchor(cur)
        if anchor is None:
            print("· anchor 未實現（門 approved 次一交易日尚未入庫）——**不開列**："
                  "開了就是猜未來交易日曆（#8）。等收盤 sync 後重跑，"
                  "或直接由 runner --apply 於產格前自開（同一住所）。")
            return 0
        n = ensure_iteration_row(cur, uid)
        cur.execute(f"SELECT status, trigger_code, gate_ref FROM {PARENT} "      # noqa: S608
                    "WHERE iteration_uid=%s", (uid,))
        row = cur.fetchone()
    print(f"✓ 帳本列 {uid}：{'本次新開' if n else '既有列沿用（冪等）'}"
          f" status={row[0]} trigger={row[1]} gate_ref={row[2]}")
    print("⚠ 本支只開 planned；running 由 runner 產格當下推進，終態屬 W4 判決端（本支永不寫）。")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("驗紅：拿掉 lock_timeout（DDL 會排隊並反向鎖全表 #30）→ 報違",
        "lock_timeout" in ddl_invariants(DDL.replace("SET LOCAL lock_timeout = '5s';", "")))
    chk("驗紅：少 DROP IF EXISTS（重跑即炸、失冪等）→ 報違",
        "fk_drop_then_add" in ddl_invariants(
            DDL.replace(f"ALTER TABLE {CHILD} DROP CONSTRAINT IF EXISTS {FK_NAME};", "", 1)))
    chk("驗紅：FK 改指別表（閘等於不存在）→ fk_points_at_ledger 報違",
        "fk_points_at_ledger" in ddl_invariants(
            DDL.replace(f"REFERENCES {PARENT}(iteration_uid)",
                        "REFERENCES sim_evolution_candidate(candidate_id)")))
    chk("驗紅：加 ON DELETE CASCADE（帳本一動就抹 link 證據）→ no_cascade 報違",
        "no_cascade" in ddl_invariants(
            DDL.replace("(iteration_uid);", "(iteration_uid) ON DELETE CASCADE;")))
    chk("驗紅：改 NOT VALID（存量不檢＝假綠）→ must_validate 報違",
        "must_validate" in ddl_invariants(
            DDL.replace("(iteration_uid);", "(iteration_uid) NOT VALID;")))
    chk("驗紅：DDL 夾帶 DELETE FROM → ddl_only_no_dml_no_destructive 報違",
        "ddl_only_no_dml_no_destructive" in ddl_invariants(
            DDL + f"\nDELETE FROM {CHILD};"))
    chk("驗紅：DDL 夾帶 INSERT INTO（本支不得寫資料，開列走 --open-ledger 之同一住所）→ 報違",
        "ddl_only_no_dml_no_destructive" in ddl_invariants(
            DDL + f"\nINSERT INTO {PARENT}(iteration_uid) VALUES ('sim-20260803-r01');"))

    # 人簽紀律（甲′行為鎖）：本支不得設任何人名旗標、不得寫人簽欄
    opts = {o for a in _parser()._actions for o in a.option_strings}
    chk("無人名旗標（--approved-by/--decided-by/--promoted-by/--signed-by 不存在）",
        not opts & {"--approved-by", "--decided-by", "--promoted-by", "--signed-by"})
    import inspect
    bodies = inspect.getsource(_apply) + inspect.getsource(_open_ledger)
    chk("apply/open 本體零人名字面（不代打人簽）",
        "'hugo'" not in bodies and '"hugo"' not in bodies)
    chk("開列走同一住所（呼叫 run_sim_calibration_cell.ensure_iteration_row，不自寫 INSERT）",
        "ensure_iteration_row" in inspect.getsource(_open_ledger)
        and "INSERT" not in inspect.getsource(_open_ledger).upper())
    chk("終態不由本支寫（succeeded/failed/gain_basis 不出現於 apply/open 本體）",
        not any(w in bodies for w in ("succeeded", "failed", "gain_basis")))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="sim 迭代帳本開列＋FK（M-T1；冪等）")
    ap.add_argument("--check", action="store_true", help="唯讀：FK/列數/孤兒/anchor 現況")
    ap.add_argument("--apply", action="store_true", help="焊 FK（冪等；dump 進行中即拒）")
    ap.add_argument("--open-ledger", action="store_true",
                    help="開本輪帳本列 planned（anchor 已實現才開）")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main(argv=None) -> int:
    a = _parser().parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.apply or a.open_ledger):
        print(__doc__.split("執行指令矩陣")[1].split("------\n")[-1])
        print("--- 無參數＝--check（唯讀）---")
    from augur.core import db
    import psycopg2
    try:                       # graceful（#29a）：connect 為 contextmanager，例外在 __enter__ 才炸
        with db.connect() as conn:
            if a.apply:
                return _apply(conn)
            if a.open_ledger:
                return _open_ledger(conn)
            return _check(conn)
    except psycopg2.OperationalError as e:
        print(f"✗ DB 連線失敗：{str(e).strip()}（需 .env 環境；set -a && . ./.env && set +a）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
