#!/usr/bin/env python3
"""🎯 建度量登錄表 `measure_registry`——「引用一個數字，就得同時說出它是用哪把尺量的」。

設計 SSOT＝reports/augur_optimization_master_plan_20260803.md（M-N2；§1 第 9 步「同批建基線」、
第 20 步「七組一名多義正名」、附(a) 表 schema 第三列）。**本支只建表、不塞資料**——七組口徑之
登錄走 `scripts/register_measure.py`（第 20 步），`authoritative` 標定屬 Steward。

## 為什麼要這張表（r4 §3.4／§7.4-1）

同一個名字底下並存多把尺，是本專案「權威數字在寫下當天就開始腐爛」的機制性成因：
`public 表數`＝334（`relkind='r'`）或 335（`pg_tables` 含分區父表）；`script 支數`＝327
（`ls scripts/*.py`）或 470（`check_cmd_matrix` 射程）；`sent_no_emb` 有四把尺。手抄任一個數字
而不附尺，讀者無從判斷它是過期、是別把尺、還是真的錯——**三種病症在文件上長得一模一樣**。
本表把「尺」升為第一級實體：`(measure_key, ruler_key)` 為主鍵，每列自帶 `definition`（這把尺量
的到底是什麼）與 `repro_cmd`（怎麼重跑出來）⇒ 數字改由程式導出，文件只引 `measure_key`。

## 兩條機械線（本支唯一之實質主張）

1. **`repro_cmd`／`definition` 非空**（NOT NULL ＋ 去空白後長度 > 0）：登錄一把不能重跑的尺，
   等於把手抄搬進 DB 換個地方腐爛。空字串能滿足 NOT NULL，故必須另加長度 CHECK。
2. **每個 `measure_key` 至多一把 authoritative**：以 partial unique index 機械保證。

**誠實射程（#15，不得被讀成「恰 1 已機械保證」）**：計畫驗收句為「每個 `measure_key` 之
`count(*) FILTER (WHERE authoritative)` **恰為 1**」。partial unique index 只擋得住 **> 1**；
**＝0**（某個 measure_key 一把 authoritative 都沒標）在 DDL 層無法以非延遲約束表達，
現由 `--check` 逐列報「no_authoritative」承接，屬**報而不擋**。不要把本表當成「恰 1 已上閘」。

## `authoritative_by`：對計畫欄位表之**加嚴**擴充（本支唯一偏離，明列於此）

計畫附(a) 之欄位表為 `measure_key`／`ruler_key`／`definition`／`repro_cmd`／`authoritative`／
`registered_at`，未含簽署欄。但同計畫第 20 步之「誰」欄逐字寫 `authoritative` 標定屬 **hugo**——
若無簽署欄，AI 自行標的 authoritative 與 Steward 標的在 DB 裡**長得一模一樣**，
「不代打人簽」在此表就沒有任何機械載體。故加 `authoritative_by text` ＋
CHECK「authoritative 為真則簽署人非空」：標權威**必須具名**。
CHECK 擋不住冒名（誰都能填 'hugo'）——這點不假裝解決，見下方殘項。

**誠實殘項（#15）**：
(a) 冒名不可擋——`authoritative_by='hugo'` 由誰打進去，DB 分不出來。本表把「無記名標權威」
    變成不可能，但「代打人簽」仍只由紀律承接（記憶檔 never-type-human-signature）。
(b) 本表**無 honesty trigger**：裸手 `UPDATE measure_registry SET authoritative=...` 可默改口徑
    且不留痕。是否掛閘＝計畫第 21 步、繫於 M-P11 裁決（Steward），本支刻意不預判、不自行上閘。

守原則 #6（--apply 才動 DB、冪等可重跑、--apply 歸主 session 窗須 hugo 明示）、#12（不自造 guard
函式第二住所）、#15（射程誠實、報而不擋者明說）、#29a/d、#30（lock_timeout 不排隊）、#35（驗紅）。

執行指令矩陣
------------
    python3 scripts/migrate_measure_registry_ddl.py              # 無參數＝印矩陣＋--check（唯讀；DB 不可達則 graceful）
    python3 scripts/migrate_measure_registry_ddl.py --check      # 唯讀：表在否／索引／每 measure_key 之 authoritative 計數
    python3 scripts/migrate_measure_registry_ddl.py --print-ddl  # 唯讀：印將執行之 DDL 全文（過目用，零連線）
    python3 scripts/migrate_measure_registry_ddl.py --apply      # 建表＋索引（冪等；須 hugo #6 明示；dump 期間禁跑 #30）；完成後自動接 --verify-red
    python3 scripts/migrate_measure_registry_ddl.py --verify-red # 建表後實證約束真的會拒（全程 ROLLBACK、零殘留）
    python3 scripts/migrate_measure_registry_ddl.py --selftest   # 紅綠自測（免 DB 免 API；壞變體驗紅 #35）

⚠ `--verify-red` 自身尚未被執行過（表未建、無從跑）——**它的首次執行即是它自己的驗紅**。
   若表名／欄名寫錯，其綠對照臂會失敗；設計上不存在「紅臂全綠」之假綠路徑（見 probe_spec_defects）。
"""

from __future__ import annotations

import argparse
import re
import sys

import _bootstrap  # noqa: F401

TABLE = "measure_registry"

DDL = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS measure_registry (
    measure_key      text NOT NULL,
    ruler_key        text NOT NULL,
    definition       text NOT NULL,
    repro_cmd        text NOT NULL,
    authoritative    boolean NOT NULL DEFAULT false,
    authoritative_by text,
    registered_at    timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT measure_registry_pkey PRIMARY KEY (measure_key, ruler_key),
    CONSTRAINT measure_registry_definition_nonempty CHECK (length(btrim(definition)) > 0),
    CONSTRAINT measure_registry_repro_cmd_nonempty  CHECK (length(btrim(repro_cmd)) > 0),
    CONSTRAINT measure_registry_authoritative_signed
        CHECK (authoritative IS FALSE OR authoritative_by IS NOT NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS measure_registry_one_authoritative
    ON measure_registry (measure_key) WHERE authoritative;

COMMENT ON TABLE measure_registry IS
  'M-N2 度量登錄:一名多義之解藥——(measure_key, ruler_key) 為主鍵,每把尺自帶 definition 與 repro_cmd;文件引 measure_key、數字由 repro_cmd 導出,不手抄。authoritative 每 key 至多 1(partial unique index);=0 由 register_measure --check 報而不擋。無 honesty trigger(掛否繫 M-P11 裁決)';
COMMENT ON COLUMN measure_registry.repro_cmd IS
  '可重跑出本尺之值的指令全文;登錄不可重跑之尺=把手抄搬進 DB,故 NOT NULL 且去空白後須非空';
COMMENT ON COLUMN measure_registry.authoritative_by IS
  '標定 authoritative 之人(Steward);CHECK 使「標權威必具名」,但擋不住冒名——代打人簽仍只由紀律承接';
"""


def build_ddl() -> str:
    """→ 將執行之 DDL 全文（純函式，零副作用；`--apply` 逐字執行本字串）。"""
    return DDL


# 每列 = (不變式名, 必須出現於 DDL 之字面/正則, 是否為正則)
def ddl_invariants(ddl: str) -> list:
    """回傳被違反之不變式名清單（空＝全守）。純函式；selftest 以本尊驗綠、壞變體驗紅。

    #35 型 3 註記（沿 migrate_strangler_ledger_ddl.py 先例）：DDL 字串即 `--apply` 逐字執行之
    行為載體，對載體驗形＝對行為驗形；惟**沙盒實跑仍是更強證據**——本批鐵律「DDL 只備不跑」，
    故列為殘項（--apply 前於交易內建表→試插違規列→ROLLBACK，實證 CHECK/索引真會拒）。
    """
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    if ddl.count(f"CREATE TABLE IF NOT EXISTS {TABLE}") != 1:
        bad.append("table_idempotent")
    for col in ("measure_key", "ruler_key", "definition", "repro_cmd",
                "authoritative", "authoritative_by", "registered_at"):
        if not re.search(rf"^\s+{col}\s+\S", ddl, re.M):
            bad.append(f"col_{col}")
    if not re.search(r"PRIMARY KEY \(measure_key, ruler_key\)", ddl):
        bad.append("composite_pk")          # treaty_probe_binding 之複合 FK 指標的,少一半即無法綁尺
    if not re.search(r"CREATE UNIQUE INDEX IF NOT EXISTS \S+\s*\n?\s*ON measure_registry \(measure_key\) WHERE authoritative",
                     ddl):
        bad.append("one_authoritative_index")
    if "length(btrim(definition)) > 0" not in ddl:
        bad.append("definition_nonempty")   # 空字串滿足 NOT NULL ⇒ 必須另有長度 CHECK
    if "length(btrim(repro_cmd)) > 0" not in ddl:
        bad.append("repro_cmd_nonempty")
    if not re.search(r"authoritative IS FALSE OR authoritative_by IS NOT NULL", ddl):
        bad.append("authoritative_signed")  # 標權威必具名（人簽欄之機械載體）
    if not re.search(r"definition\s+text NOT NULL", ddl) or not re.search(r"repro_cmd\s+text NOT NULL", ddl):
        bad.append("口徑欄_not_null")
    if not re.search(r"authoritative\s+boolean NOT NULL DEFAULT false", ddl):
        bad.append("authoritative_default_false")   # 預設不是權威;要當權威得明著標並具名
    if "INSERT INTO" in ddl:
        bad.append("no_seed_in_ddl")        # 登錄走 register_measure.py,不由遷移偷塞
    if re.search(r"\bUPDATE\b", ddl) or "DELETE FROM" in ddl or "TRUNCATE" in ddl:
        bad.append("no_mutation_in_ddl")
    if "CREATE OR REPLACE FUNCTION" in ddl or "CREATE FUNCTION" in ddl:
        bad.append("guard_fn_not_self_made")        # #12：guard 函式住 migrate_honesty_guards_ddl.py
    return bad


def authoritative_verdicts(rows) -> list:
    """rows=[(measure_key, n_rulers, n_auth)] → [(measure_key, 判定)]；判定∈ok/no_authoritative/多重。

    純函式（無 DB）。「恰 1」之 **=0 那半邊**由本函式承接——DDL 之 partial unique index 只擋 >1。
    """
    out = []
    for key, n_rulers, n_auth in rows:
        if n_auth == 1:
            verdict = "ok"
        elif n_auth == 0:
            verdict = "no_authoritative"
        else:
            verdict = f"multi_authoritative({n_auth})"
        out.append((key, verdict, n_rulers))
    return out


# ── --verify-red：建表後實證「約束真的會拒」；全程在一個必定 ROLLBACK 的交易內 ──
# 每列＝(名稱, SQL, 期望 SQLSTATE 或 None＝綠對照臂須成功)。
# 綠對照臂不可省（評測樣板地板之教訓）：若表名寫錯／欄名寫錯,**每一條紅臂都會因 42P01/42703 而
# 「被拒」** ⇒ 全紅通過＝假綠。綠臂一失敗即揭穿。
_SEED = ("INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd,"
         " authoritative, authoritative_by)"
         " VALUES ('mr_selfverify','r_a','d','c', true, 'VERIFY-ROLLBACK')")
RED_PROBES = (
    ("綠對照：合法列可插入（表/欄名寫錯的話這裡就會炸，紅臂全綠即假綠）",
     "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd)"
     " VALUES ('mr_selfverify','r_b','d2','c2')", None),
    ("紅：同 measure_key 標第二把 authoritative → partial unique index 拒",
     "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd,"
     " authoritative, authoritative_by)"
     " VALUES ('mr_selfverify','r_c','d','c', true, 'VERIFY-ROLLBACK')", "23505"),
    ("紅：標 authoritative 卻不具名 → authoritative_signed CHECK 拒（人簽欄之機械載體）",
     "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd, authoritative)"
     " VALUES ('mr_selfverify','r_d','d','c', true)", "23514"),
    ("紅：repro_cmd 給空白字串 → repro_cmd_nonempty CHECK 拒（NOT NULL 擋不住空字串）",
     "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd)"
     " VALUES ('mr_selfverify','r_e','d','   ')", "23514"),
    ("紅：definition 給空字串 → definition_nonempty CHECK 拒",
     "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd)"
     " VALUES ('mr_selfverify','r_f','','c')", "23514"),
    ("紅：同 (measure_key, ruler_key) 重覆 → 複合 PK 拒",
     _SEED, "23505"),
)


def probe_spec_defects(probes) -> list:
    """回傳探針規格本身的缺陷（空＝規格健全）。純函式；防「紅臂全綠＝假綠」與「期望碼過寬」。"""
    bad = []
    if not any(exp is None for _, _, exp in probes):
        bad.append("no_green_arm")            # 沒有綠對照臂 ⇒ 表名打錯時全紅通過
    if not any(exp is not None for _, _, exp in probes):
        bad.append("no_red_arm")
    for name, sql, exp in probes:
        if exp is not None and (not isinstance(exp, str) or len(exp) != 5 or not exp.isdigit()):
            bad.append(f"loose_sqlstate:{name}")   # 只斷言「有丟例外」會把 42P01 當成閘生效
        if not sql.strip().upper().startswith("INSERT"):
            bad.append(f"not_insert:{name}")
    return bad


def _verify_red(conn) -> int:
    """建表後實證：綠臂真能寫、紅臂真被對的 SQLSTATE 拒。**全程 ROLLBACK，不留任何列。**"""
    import psycopg2
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        if not cur.fetchone()[0]:
            print(f"  · table {TABLE} 不在——先 --apply 再跑 --verify-red")
            return 1
    ok = True
    try:
        with conn.cursor() as cur:
            cur.execute(_SEED)
            for name, sql, expect in RED_PROBES:
                cur.execute("SAVEPOINT p")
                try:
                    cur.execute(sql)
                    got = None
                except psycopg2.Error as e:
                    got = e.pgcode
                cur.execute("ROLLBACK TO SAVEPOINT p")
                good = (got == expect)
                ok &= good
                print(f"  {'✓' if good else '✗'} {name}｜期望 {expect or '成功'}／實得 {got or '成功'}")
    finally:
        conn.rollback()
    print("--verify-red：" + ("全通過 ✓（已 ROLLBACK，零殘留）" if ok else "有失敗 ✗（約束未如設計生效）"))
    return 0 if ok else 1


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        if not cur.fetchone()[0]:
            print(f"  · table {TABLE} 不在（未 --apply）——treaty_probe_binding 之複合 FK 無標的，"
                  f"M-N1 建表會失敗；本支須先於 migrate_treaty_probe_ddl.py")
            return 0
        print(f"  ✓ table {TABLE} 在")
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename=%s ORDER BY 1", (TABLE,))
        idx = [r[0] for r in cur.fetchall()]
        has_partial = "measure_registry_one_authoritative" in idx
        print(f"  {'✓' if has_partial else '✗'} partial unique index one_authoritative"
              f"{'' if has_partial else '（缺——每 key 可標多把權威）'}；索引：{', '.join(idx) or '（無）'}")
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass AND NOT tgisinternal", (TABLE,))
        print(f"  · honesty trigger {cur.fetchone()[0]} 支（現行設計＝不掛；掛否繫 M-P11 裁決／計畫第 21 步）")
        cur.execute("""SELECT measure_key, count(*), count(*) FILTER (WHERE authoritative)
                       FROM measure_registry GROUP BY 1 ORDER BY 1""")
        rows = cur.fetchall()
        if not rows:
            print("  登錄列：（空——七組口徑尚未登錄；走 scripts/register_measure.py，計畫第 20 步）")
            return 0
        bad = [(k, v, n) for k, v, n in authoritative_verdicts(rows) if v != "ok"]
        print(f"  登錄：{len(rows)} 個 measure_key／{sum(r[1] for r in rows)} 把尺；"
              f"authoritative 判定不為 ok 者 {len(bad)} 個")
        for k, v, n in bad:
            print(f"    · {k}：{v}（共 {n} 把尺）")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute(build_ddl())
    print(f"✓ DDL 冪等完成（{TABLE}＋partial unique index，無 trigger）")
    rc = _check(conn)
    print("── 建表後即刻驗紅（#35：閘裝上就當場證明它會拒，不留給日後）")
    return _verify_red(conn) or rc


def _fake_conn(silent_constraints=()):
    """腳本化的假連線：讓 `_verify_red` 的流程可在**零 DB** 下被實跑驗證。

    `silent_constraints`＝一組「本該拒、卻默默放行」的紅臂名關鍵字——用來模擬「約束被卸掉／
    寫錯而靜默失效」，`--verify-red` 對這種情況**必須變紅**。這是對驗證器自身的回歸鎖：
    只證明它在好情況下印綠是不夠的（那種綠可能恆綠）。
    """
    import psycopg2

    class Err(psycopg2.Error):
        def __init__(self, code):
            self._c = code

        @property
        def pgcode(self):
            return self._c

    expect_by_sql = {sql: exp for _, sql, exp in RED_PROBES}
    silenced = {sql for name, sql, exp in RED_PROBES
                if exp is not None and any(k in name for k in silent_constraints)}

    state = {"seeded": False}

    class Cur:
        def execute(self, sql, params=None):
            if sql.startswith("SELECT to_regclass"):
                self._row = ("exists",)
                return
            if sql == _SEED and not state["seeded"]:
                state["seeded"] = True   # 種子列首次寫入成功;同一句再來才是 PK 撞擊（與真 DB 同）
                return
            exp = expect_by_sql.get(sql)
            if exp is not None and sql not in silenced:
                raise Err(exp)          # 約束正常生效＝依設計拒絕

        def fetchone(self):
            return self._row

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class Conn:
        def __init__(self):
            self.rolled_back = 0

        def cursor(self):
            return Cur()

        def rollback(self):
            self.rolled_back += 1

    return Conn()


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    ddl = build_ddl()
    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(ddl) == [])
    chk("build_ddl 為純函式：兩次呼叫全等且不含資料列", build_ddl() == build_ddl() and "INSERT" not in build_ddl())
    chk("本尊不夾帶 trigger（掛閘繫 M-P11，本支不預判）", "CREATE TRIGGER" not in ddl)
    # ── 壞變體驗紅（打靶點＝DDL 行為碼本身，非 docstring）──
    chk("驗紅：拿掉複合 PK 之後半 → composite_pk 報違（M-N1 之綁尺 FK 會失去標的）",
        "composite_pk" in ddl_invariants(
            ddl.replace("PRIMARY KEY (measure_key, ruler_key)", "PRIMARY KEY (measure_key)")))
    chk("驗紅：partial unique index 去掉 WHERE authoritative → one_authoritative_index 報違（變成全表唯一、擋錯東西）",
        "one_authoritative_index" in ddl_invariants(
            ddl.replace("ON measure_registry (measure_key) WHERE authoritative",
                        "ON measure_registry (measure_key)")))
    chk("驗紅：刪掉 partial unique index 整段 → one_authoritative_index 報違（多把權威可並存）",
        "one_authoritative_index" in ddl_invariants(
            re.sub(r"CREATE UNIQUE INDEX.*?;\n", "", ddl, flags=re.S)))
    chk("驗紅：repro_cmd 只留 NOT NULL、拿掉長度 CHECK → repro_cmd_nonempty 報違（空字串可過 NOT NULL）",
        "repro_cmd_nonempty" in ddl_invariants(
            ddl.replace("CHECK (length(btrim(repro_cmd)) > 0)", "CHECK (repro_cmd IS NOT NULL)")))
    chk("驗紅：definition 同型放寬 → definition_nonempty 報違",
        "definition_nonempty" in ddl_invariants(
            ddl.replace("CHECK (length(btrim(definition)) > 0)", "CHECK (true)")))
    chk("驗紅：拿掉「標權威必具名」CHECK → authoritative_signed 報違（AI 標的與人標的變成無從分辨）",
        "authoritative_signed" in ddl_invariants(
            ddl.replace("authoritative IS FALSE OR authoritative_by IS NOT NULL", "true")))
    chk("驗紅：authoritative 預設改 true → authoritative_default_false 報違（登錄即權威＝一名多義沒解掉）",
        "authoritative_default_false" in ddl_invariants(
            ddl.replace("authoritative    boolean NOT NULL DEFAULT false",
                        "authoritative    boolean NOT NULL DEFAULT true")))
    chk("驗紅：少一欄（authoritative_by）→ col_authoritative_by 報違",
        "col_authoritative_by" in ddl_invariants(ddl.replace("    authoritative_by text,\n", "")))
    chk("驗紅：repro_cmd 改為可空 → 口徑欄_not_null 報違",
        "口徑欄_not_null" in ddl_invariants(ddl.replace("repro_cmd        text NOT NULL",
                                                        "repro_cmd        text         ")))
    chk("驗紅：拿掉 lock_timeout → 報違（#30 dump 期間鎖風暴）",
        "lock_timeout" in ddl_invariants(ddl.replace("SET lock_timeout = '5s';", "")))
    chk("驗紅：DDL 偷塞種子列 → no_seed_in_ddl 報違（登錄須走 register_measure.py 之可審路徑）",
        "no_seed_in_ddl" in ddl_invariants(ddl + "\nINSERT INTO measure_registry VALUES ('x','y','d','c');"))
    chk("驗紅：DDL 夾帶 UPDATE → no_mutation_in_ddl 報違（遷移不得默改既有口徑）",
        "no_mutation_in_ddl" in ddl_invariants(ddl + "\nUPDATE measure_registry SET authoritative=true;"))
    chk("驗紅：DDL 自造 guard 函式 → guard_fn_not_self_made 報違（#12 單一住所）",
        "guard_fn_not_self_made" in ddl_invariants(
            ddl + "\nCREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$ $$;"))
    chk("驗紅：表名改掉 → table_idempotent 報違（改名等於建了另一張表、舊表還在）",
        "table_idempotent" in ddl_invariants(
            ddl.replace(f"CREATE TABLE IF NOT EXISTS {TABLE}", "CREATE TABLE IF NOT EXISTS measure_reg")))
    # ── authoritative_verdicts：「恰 1」之兩邊（DDL 只擋 >1，=0 由此承接）──
    chk("恰1判定：1 把權威 → ok", authoritative_verdicts([("k", 3, 1)]) == [("k", "ok", 3)])
    chk("恰1判定：0 把權威 → no_authoritative（此半邊 DDL 擋不到、報而不擋）",
        authoritative_verdicts([("k", 4, 0)])[0][1] == "no_authoritative")
    chk("恰1判定：2 把權威 → multi_authoritative（DB 有索引時不該發生;索引若被 DROP 仍報得出來）",
        authoritative_verdicts([("k", 4, 2)])[0][1].startswith("multi_authoritative"))
    chk("恰1判定：多組各自判、不互相污染",
        [v for _, v, _ in authoritative_verdicts([("a", 2, 1), ("b", 2, 0)])] == ["ok", "no_authoritative"])
    # ── --verify-red 之探針規格（防「紅臂全綠＝假綠」）──
    chk("探針規格健全：有綠對照臂、有紅臂、期望碼皆為 5 碼 SQLSTATE", probe_spec_defects(RED_PROBES) == [])
    chk("驗紅：拿掉綠對照臂 → no_green_arm 報違（表名打錯時紅臂會全數『被拒』而假綠）",
        "no_green_arm" in probe_spec_defects([p for p in RED_PROBES if p[2] is not None]))
    chk("驗紅：期望碼放寬成「有丟例外就算」→ loose_sqlstate 報違（42P01 會被當成閘生效）",
        any(d.startswith("loose_sqlstate") for d in probe_spec_defects(
            [(n, s, (True if e else e)) for n, s, e in RED_PROBES])))
    chk("紅臂覆蓋四條機械線（唯一索引／具名／非空／複合 PK）",
        {p[2] for p in RED_PROBES if p[2]} == {"23505", "23514"} and len(RED_PROBES) >= 5)
    # ── 對 --verify-red 本身實跑（假連線、零 DB）：好情況印綠，且**約束靜默失效時必須變紅** ──
    def run_vr(conn):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):     # 內層逐條輸出不灌進自測畫面
            return _verify_red(conn)

    fc = _fake_conn()
    chk("verify-red 實跑：約束全數如設計生效 → rc=0，且結束時已 rollback（零殘留）",
        run_vr(fc) == 0 and fc.rolled_back >= 1)
    chk("verify-red 驗紅：partial unique index 被卸掉（第二把 authoritative 靜默寫入）→ rc≠0",
        run_vr(_fake_conn(silent_constraints=("標第二把 authoritative",))) != 0)
    chk("verify-red 驗紅：「標權威必具名」CHECK 被卸掉 → rc≠0",
        run_vr(_fake_conn(silent_constraints=("不具名",))) != 0)
    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="度量登錄表 measure_registry DDL（M-N2；--apply 須 hugo 明示）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print-ddl", dest="print_ddl", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verify-red", dest="verify_red", action="store_true",
                    help="建表後實證約束真的會拒（全程 ROLLBACK、零殘留）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.print_ddl:
        print(build_ddl())
        return 0
    no_args = not (a.check or a.apply or a.verify_red)
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
            return _apply(conn)
        return _verify_red(conn) if a.verify_red else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
