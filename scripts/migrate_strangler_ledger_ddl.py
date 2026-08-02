#!/usr/bin/env python3
"""🎯 建 vendor 直綁絞殺帳本表——每個被改線的檔，雙讀比對結果留一條不可覆寫的帳。

WM.36 合規弧 M3 地基（計畫 §4 表③「絞殺帳本」照案；設計 SSOT＝
reports/wm3536_vendor_registry_plan_20260802.md §4／§5 表列 4）。消費端＝scripts/compare_shadow_binding.py。
守原則 #6（--apply 才動 DB；冪等可重跑；--apply 歸主 session 窗、須 hugo 明示）、#15（diff≠0 記紅列、
不覆寫——紅燈必須留得住）、#12（guard 函式復用 migrate_honesty_guards_ddl 單一住所，不自造第二實作）、
#29a/d、#35（壞變體驗紅）。

## 為什麼另立一支（不併入 migrate_world_concept_registry_ddl.py）

1. **條文地位不同**：①② 二表承 WM.36 登錄義務（條文），③ 帳本為 **[I] 落地憑證、非條文義務**
   （計畫 §4 原文）——混在同一支會讓「哪幾張表是條文要的」不可辨。
2. **不改寫已生效之回歸鎖（#35 向前生效之界線）**：M1 那支之 `ddl_invariants` 已凍住
   「恰二表／恰四 trigger／恰二處 provenance NOT NULL」等計數；加第三張表必須改寫那些斷言，
   而「任何觸碰即落入改寫」＝要對一支**已 --apply 生效**的腳本重跑全部驗紅。分家＝零改寫風險。
3. **施作時序不同**：①② 已 live（2026-08-02 M1），③ 尚未執行——分家使 `--check` 誠實反映
   「這張還沒建」，不被已建的二表掩蓋。

## ⚠ 待確認事項（本支未執行，主 session／Steward 過目時裁）

**guard trigger 是否上**：計畫 §4 原文「不新增 honesty trigger 於本批」，但 G0 格 3 裁示
「照案（二表七欄溯源＋**trigger 同 honesty 家族**）」——其文義及於 ①②，**③ 未經明示**。
本支**預設上 trigger**（理由：③ 是帳本，紅列若可被裸手 UPDATE／DELETE 抹掉，整條絞殺鏈的
「紅燈會亮」保證即失效；與既有兩帳本表上閘之先例同型）。不同意者以 `--no-guard` 生成無 trigger 版本
（DDL 印出可過目）。**本支不代決、不代簽**。

執行指令矩陣
------------
    python3 scripts/migrate_strangler_ledger_ddl.py             # 無參數＝印矩陣＋--check（唯讀，DB 不可達則 graceful）
    python3 scripts/migrate_strangler_ledger_ddl.py --check     # 唯讀：表在否／trigger 數／列況
    python3 scripts/migrate_strangler_ledger_ddl.py --print-ddl # 唯讀：印將執行之 DDL 全文（過目用，零連線）
    python3 scripts/migrate_strangler_ledger_ddl.py --apply     # 建表（冪等；須 hugo #6 明示；dump 期間禁跑 #30）
    python3 scripts/migrate_strangler_ledger_ddl.py --apply --no-guard   # 同上但不掛 honesty trigger
    python3 scripts/migrate_strangler_ledger_ddl.py --selftest  # 紅綠自測（免 DB 免 API；壞變體驗紅 #35）
"""

from __future__ import annotations

import argparse
import re
import sys

import _bootstrap  # noqa: F401

TABLE = "vendor_binding_strangler_ledger"

# ── 表本體：計畫 §4 表③ 逐字照案（僅加冪等外衣 IF NOT EXISTS＋#30 lock_timeout）──
DDL_TABLE = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS vendor_binding_strangler_ledger (
    file_path      text NOT NULL,
    batch          text NOT NULL,
    occurrences    int  NOT NULL,
    shadow_diff_rows bigint,
    verdict        text NOT NULL CHECK (verdict IN ('green','red','pending')),
    evidence_ref   text,
    verified_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (file_path, verified_at)
);

COMMENT ON TABLE vendor_binding_strangler_ledger IS
  'WM.36 絞殺帳本(計畫 §4 表③;非條文義務、為落地憑證):一檔一次雙讀影子比對一列——green=diff 0 才准切,red=熔斷回退,pending=比對未達成(含新舊 SQL 全等之無鑑別力情形,誠實不記綠);append-only:同檔重驗=新列(PK 含 verified_at),舊列不覆寫';
"""

# ── guard trigger（預設上；--no-guard 可去。函式本體＝migrate_honesty_guards_ddl.py 單一住所）──
DDL_GUARD = """
DROP TRIGGER IF EXISTS trg_vendor_binding_strangler_ledger_honesty_row ON vendor_binding_strangler_ledger;
CREATE TRIGGER trg_vendor_binding_strangler_ledger_honesty_row
  BEFORE UPDATE OR DELETE ON vendor_binding_strangler_ledger
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_vendor_binding_strangler_ledger_honesty_trunc ON vendor_binding_strangler_ledger;
CREATE TRIGGER trg_vendor_binding_strangler_ledger_honesty_trunc
  BEFORE TRUNCATE ON vendor_binding_strangler_ledger
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
"""


def build_ddl(with_guard: bool = True) -> str:
    """→ 將執行之 DDL 全文（純函式）。with_guard=False ⇒ 只建表、不掛 trigger。"""
    return DDL_TABLE + (DDL_GUARD if with_guard else "")


def ddl_invariants(ddl: str, with_guard: bool = True) -> list:
    """回傳被違反之不變式名清單（空＝全守）。純函式；selftest 以本尊驗綠、壞變體驗紅。

    #35 型 3 註記（同 M1／E2 先例）：DDL 字串即被逐字執行之行為載體，對載體驗形＝對行為驗形；
    惟**沙盒實跑仍是更強證據**——本批鐵律零 DDL 執行，故此項列殘餘（--apply 前於沙盒庫實跑）。
    """
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    if ddl.count(f"CREATE TABLE IF NOT EXISTS {TABLE}") != 1:
        bad.append("table_idempotent")
    for col in ("file_path", "batch", "occurrences", "shadow_diff_rows",
                "verdict", "evidence_ref", "verified_at"):
        if col not in ddl:
            bad.append(f"col_{col}")
    if "IN ('green','red','pending')" not in ddl:
        bad.append("verdict_closed_set")
    if not re.search(r"PRIMARY KEY \(file_path, verified_at\)", ddl):
        bad.append("append_only_pk")          # 同檔重驗＝新列;舊列（含紅列）不被覆寫
    # NULL＝比對未達成,與 0（真無差異）不得混為一談 ⇒ 宣告須恰為 nullable（NOT NULL/DEFAULT 皆違）
    if not re.search(r"shadow_diff_rows\s+bigint\s*,", ddl):
        bad.append("diff_rows_nullable")
    if "verdict        text NOT NULL" not in ddl:
        bad.append("verdict_not_null")
    if "UPDATE" in ddl.replace("BEFORE UPDATE OR DELETE", "") or "DELETE FROM" in ddl:
        bad.append("no_mutation_in_ddl")
    if "INSERT INTO" in ddl:
        bad.append("no_insert_in_ddl")
    if "CREATE OR REPLACE FUNCTION" in ddl or "CREATE FUNCTION" in ddl:
        bad.append("guard_fn_not_self_made")  # #12：函式住 migrate_honesty_guards_ddl.py
    n_guard = ddl.count("honesty_ledger_guard()")
    if with_guard and (n_guard != 2 or ddl.count("DROP TRIGGER IF EXISTS") != 2):
        bad.append("two_guard_triggers")
    if not with_guard and n_guard != 0:
        bad.append("no_guard_variant_leaks_trigger")
    return bad


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        if not cur.fetchone()[0]:
            print(f"  · table {TABLE} 不在（未 --apply）——compare_shadow_binding.py --apply 會 fail-closed 拒寫")
            return 0
        print(f"  ✓ table {TABLE} 在")
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid = %s::regclass AND NOT tgisinternal",
                    (TABLE,))
        n = cur.fetchone()[0]
        print(f"  {'✓' if n == 2 else '·'} honesty guard trigger {n}/2"
              f"{'（--no-guard 版本即 0/2）' if n == 0 else ''}")
        cur.execute(f"SELECT verdict, count(*) FROM {TABLE} GROUP BY 1 ORDER BY 1")
        rows = cur.fetchall()
        print("  帳本列：" + ("（空——尚無檔改線）" if not rows
                             else "; ".join(f"{k} {c}" for k, c in rows)))
    return 0


def _apply(conn, with_guard: bool) -> int:
    from augur.core import db
    if with_guard:
        with db.transaction(conn) as cur:
            cur.execute("SELECT count(*) FROM pg_proc WHERE proname='honesty_ledger_guard'")
            if cur.fetchone()[0] == 0:
                print("✗ honesty_ledger_guard 函式不存在——先跑 migrate_honesty_guards_ddl.py --apply"
                      "（#12 不自造第二住所），或以 --no-guard 建無閘版")
                return 1
    with db.transaction(conn) as cur:
        cur.execute(build_ddl(with_guard))
    print(f"✓ DDL 冪等完成（{TABLE}{'＋二 trigger' if with_guard else '，無 guard'}）")
    return _check(conn)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    ddl = build_ddl(True)
    chk("本尊 DDL（含 guard）全不變式守住（綠）", ddl_invariants(ddl) == [])
    chk("--no-guard 變體：不變式守住且不夾帶 trigger（綠）",
        ddl_invariants(build_ddl(False), with_guard=False) == []
        and "honesty_ledger_guard" not in build_ddl(False))
    chk("build_ddl 為純函式：with_guard 真假生不同 DDL、表本體相同",
        build_ddl(True) != build_ddl(False) and build_ddl(False) in build_ddl(True))
    # ── 壞變體驗紅（在檔常駐版；scratch 突變另證，見 commit/report）──
    chk("驗紅：拿掉 verdict 閉集 → verdict_closed_set 報違",
        "verdict_closed_set" in ddl_invariants(ddl.replace("IN ('green','red','pending')", "")))
    chk("驗紅：PK 改成只有 file_path → append_only_pk 報違（同檔重驗會覆寫舊紅列）",
        "append_only_pk" in ddl_invariants(
            ddl.replace("PRIMARY KEY (file_path, verified_at)", "PRIMARY KEY (file_path)")))
    chk("驗紅：shadow_diff_rows 改 NOT NULL DEFAULT 0 → 報違（比對未達成會冒充『零差異』）",
        "diff_rows_nullable" in ddl_invariants(
            ddl.replace("shadow_diff_rows bigint", "shadow_diff_rows bigint NOT NULL DEFAULT 0")))
    chk("驗紅：verdict 可為 NULL → 報違（判定不得留空冒充未定）",
        "verdict_not_null" in ddl_invariants(
            ddl.replace("verdict        text NOT NULL", "verdict        text        ")))
    chk("驗紅：少一支 trigger → two_guard_triggers 報違",
        "two_guard_triggers" in ddl_invariants(ddl.replace(
            "DROP TRIGGER IF EXISTS trg_vendor_binding_strangler_ledger_honesty_trunc "
            "ON vendor_binding_strangler_ledger;", "", 1)))
    chk("驗紅：DDL 自造 guard 函式 → 報違（#12 單一住所）",
        "guard_fn_not_self_made" in ddl_invariants(
            ddl + "\nCREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$ $$;"))
    chk("驗紅：DDL 夾帶 INSERT → 報違（DDL 與寫入分離）",
        "no_insert_in_ddl" in ddl_invariants(ddl + "\nINSERT INTO vendor_binding_strangler_ledger VALUES (1);"))
    chk("驗紅：DDL 夾帶 DELETE FROM → 報違（帳本不得於遷移中被清）",
        "no_mutation_in_ddl" in ddl_invariants(ddl + "\nDELETE FROM vendor_binding_strangler_ledger;"))
    chk("驗紅：拿掉 lock_timeout → 報違（#30 dump 期間鎖風暴）",
        "lock_timeout" in ddl_invariants(ddl.replace("SET lock_timeout = '5s';", "")))
    chk("驗紅：少一欄（evidence_ref）→ col_evidence_ref 報違",
        "col_evidence_ref" in ddl_invariants(ddl.replace("evidence_ref   text,", "")))
    chk("驗紅：--no-guard 變體卻夾帶 trigger → 報違（旗標與產物須一致）",
        "no_guard_variant_leaks_trigger" in ddl_invariants(build_ddl(True), with_guard=False))
    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="vendor 直綁絞殺帳本表 DDL（計畫 §4 表③；--apply 須 hugo 明示）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print-ddl", dest="print_ddl", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-guard", dest="no_guard", action="store_true",
                    help="不掛 honesty trigger（見標頭待確認事項）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.print_ddl:
        print(build_ddl(not a.no_guard))
        return 0
    no_args = not (a.check or a.apply)
    if no_args:
        print(__doc__.split("執行指令矩陣")[-1].split("------------\n")[-1])
    from augur.core import db
    if no_args:
        try:
            with db.connect() as conn:
                return _check(conn)
        except Exception as e:  # noqa: BLE001 — 無參數須 graceful 不裸 traceback（#29a）
            print(f"（--check 需 DB；現不可達：{e}；--selftest／--print-ddl 免 DB 可跑）")
            return 0
    with db.connect() as conn:
        if a.apply:
            return _apply(conn, not a.no_guard)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
