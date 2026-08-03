#!/usr/bin/env python3
"""🎯 建「條文 ↔ live 探針」綁定表——治權檔裡的每個權威數字，都得指到一條會自己重跑的量測。

設計 SSOT＝reports/augur_optimization_master_plan_20260803.md（M-N1；§1 第 9 步「同批建基線」、
第 19 步「過期族一次收斂」、第 33 步「10-14 全 13 項機械覆蓋」、附(a) 表 schema 前二列；M-W1 併入）。
**本支只建表、不塞資料**——綁定與量測走 `scripts/sync_treaty_probes.py`／`read_treaty_probes.py`。

## 為什麼要這兩張表（r4 §7.4-2／§6.4）

計畫逐字：手抄數字「在寫下當天就開始腐爛」，且**已實測到同一日內就腐爛**——`2026-10-14` 在治權檔
的命中數當日由 74 處漂到 88 處；vendor 直綁基線由 128/170 漂到 130/172。因此 17 則過期數字的
「個別修正」若不接探針，只是把一個手抄值換成另一個手抄值。本表把關係倒過來：
文件寫的是 `probe_id`，值由 `check_cmd` 當場導出，`--check` 拿導出值對 `expect_expr` 做 diff。

* `treaty_probe_binding`＝一條條文（`clause_ref`＝file:line）綁一把已登錄的尺（複合 FK 指向
  `measure_registry(measure_key, ruler_key)`）＋重跑指令＋期望式＋（可空的）`deadline`。
* `treaty_probe_reading`＝每次量測一列（append）；AI 只登錄**量到的值**。

## 三條機械線（本支之實質主張）

1. **只綁值不綁尺者建不起來**（計畫第 20 步驗收②逐字：「插入無 ruler 之探針列須被 FK 拒」）：
   `(measure_key, ruler_key)` 複合 FK ⇒ 尺沒登錄進 `measure_registry` 就插不進來。
   **故本支之 --apply 須排在 migrate_measure_registry_ddl.py --apply 之後**（無標的則建表即失敗）。
2. **人裁類框，AI 寫不進「已達成」**（計畫附(a) 逐字：「凡涉是否已達成／續延者一律 undecidable，
   AI 只登錄量測值」；第 33 步驗收③）：`treaty_probe_reading.probe_owner` 以**複合 FK**
   `(probe_id, probe_owner)` → `treaty_probe_binding(probe_id, owner)` 綁死（欄位無法謊報 owner），
   再加 CHECK「probe_owner 為 Steward ⇒ verdict 必為 undecidable」。
   ⇒ 對人裁框寫 `meets`／`not_meets` 在 DB 層**不可能**，不必靠稽核查詢事後抓。
   附帶效果（設計如此、非缺陷）：`binding.owner` 由 Steward 改 AI 時，若已有 readings 會被 FK 擋，
   **不能事後把人裁框改判成機器框來解鎖 meets**；真要改判須先處置既有 readings，留痕。
3. **verdict 預設 undecidable**：漏填不會落到 NULL 或 meets，落在最保守值。

**誠實射程（#15，三處不得誇稱）**：
(a) 上述第 2 條擋的是「**寫進去的東西**」，不是「誰寫的」——`owner='AI'` 的機器框裡若填了錯的
    `meets`，DB 照收；那由 `expect_expr` 對照與人審承接，不由本表承接。
(b) 本表**無 honesty trigger**：readings 可被裸手 UPDATE／DELETE 抹掉。掛閘與否＝計畫第 21 步、
    繫於 M-P11 裁決（Steward），本支刻意不預判、不自行上閘；`reading_id` 為 identity ＋ 寫入端
    只 INSERT，是慣例不是機械閘。
(c) `deadline` 可空——多數文件數字探針無期限；「≥13 項綁 2026-10-14」是**資料面**驗收
    （計畫第 33 步驗收①），DDL 不強制、也不該強制。

守原則 #6（--apply 才動 DB、冪等可重跑、--apply 歸主 session 窗須 hugo 明示）、#12（不自造 guard
函式第二住所）、#15（射程誠實）、#29a/d、#30（lock_timeout 不排隊）、#35（驗紅）。

執行指令矩陣
------------
    python3 scripts/migrate_treaty_probe_ddl.py              # 無參數＝印矩陣＋--check（唯讀；DB 不可達則 graceful）
    python3 scripts/migrate_treaty_probe_ddl.py --check      # 唯讀：二表在否／FK 與 CHECK 到位否／綁定與量測列況
    python3 scripts/migrate_treaty_probe_ddl.py --print-ddl  # 唯讀：印將執行之 DDL 全文（過目用，零連線）
    python3 scripts/migrate_treaty_probe_ddl.py --apply      # 建二表（冪等；**須先跑 migrate_measure_registry_ddl.py --apply**；須 hugo #6 明示）；完成後自動接 --verify-red
    python3 scripts/migrate_treaty_probe_ddl.py --verify-red # 建表後實證兩條機械線真的會拒（全程 ROLLBACK、零殘留）
    python3 scripts/migrate_treaty_probe_ddl.py --selftest   # 紅綠自測（免 DB 免 API；壞變體驗紅 #35）

⚠ `--verify-red` 自身尚未被執行過（表未建、無從跑）——**它的首次執行即是它自己的驗紅**。
   若表名／欄名寫錯，其兩條綠對照臂會失敗；設計上不存在「紅臂全綠」之假綠路徑（見 probe_spec_defects）。
"""

from __future__ import annotations

import argparse
import re
import sys

import _bootstrap  # noqa: F401

BINDING = "treaty_probe_binding"
READING = "treaty_probe_reading"
PARENT = "measure_registry"          # M-N2；本支之複合 FK 標的（住 migrate_measure_registry_ddl.py）

DDL = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS treaty_probe_binding (
    probe_id     text NOT NULL,
    clause_ref   text NOT NULL,
    deadline     date,
    measure_key  text NOT NULL,
    ruler_key    text NOT NULL,
    check_cmd    text NOT NULL,
    expect_expr  text NOT NULL,
    owner        text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT treaty_probe_binding_pkey PRIMARY KEY (probe_id),
    CONSTRAINT treaty_probe_binding_owner_uk UNIQUE (probe_id, owner),
    CONSTRAINT treaty_probe_binding_owner_closed CHECK (owner IN ('AI','Steward')),
    CONSTRAINT treaty_probe_binding_clause_ref_shape CHECK (clause_ref ~ '^[^:]+:.+$'),
    CONSTRAINT treaty_probe_binding_check_cmd_nonempty CHECK (length(btrim(check_cmd)) > 0),
    CONSTRAINT treaty_probe_binding_expect_expr_nonempty CHECK (length(btrim(expect_expr)) > 0),
    CONSTRAINT treaty_probe_binding_ruler_fk
        FOREIGN KEY (measure_key, ruler_key)
        REFERENCES measure_registry (measure_key, ruler_key)
);

CREATE TABLE IF NOT EXISTS treaty_probe_reading (
    reading_id   bigint GENERATED ALWAYS AS IDENTITY,
    probe_id     text NOT NULL,
    probe_owner  text NOT NULL,
    read_at      timestamptz NOT NULL DEFAULT now(),
    value_text   text NOT NULL,
    verdict      text NOT NULL DEFAULT 'undecidable',
    machine_note text,
    CONSTRAINT treaty_probe_reading_pkey PRIMARY KEY (reading_id),
    CONSTRAINT treaty_probe_reading_verdict_closed
        CHECK (verdict IN ('meets','not_meets','undecidable')),
    CONSTRAINT treaty_probe_reading_steward_undecidable
        CHECK (probe_owner <> 'Steward' OR verdict = 'undecidable'),
    CONSTRAINT treaty_probe_reading_probe_fk
        FOREIGN KEY (probe_id, probe_owner)
        REFERENCES treaty_probe_binding (probe_id, owner)
);

CREATE INDEX IF NOT EXISTS treaty_probe_reading_probe_read_at
    ON treaty_probe_reading (probe_id, read_at DESC);

COMMENT ON TABLE treaty_probe_binding IS
  'M-N1 條文↔live 探針綁定:clause_ref(file:line)綁一把已登錄的尺(複合 FK→measure_registry),值由 check_cmd 當場導出對 expect_expr diff——文件引 probe_id、不手抄數字。owner=AI(機器可判)/Steward(人裁)。無 honesty trigger(掛否繫 M-P11)';
COMMENT ON TABLE treaty_probe_reading IS
  'M-N1 探針量測(append,一次一列):AI 只登錄量到的值。probe_owner 以複合 FK 綁死 binding.owner 無法謊報;人裁框(Steward)之 verdict 經 CHECK 鎖為 undecidable ⇒ AI 在 DB 層寫不進「已達成/續延」。無 honesty trigger(掛否繫 M-P11)';
COMMENT ON COLUMN treaty_probe_reading.probe_owner IS
  '非冗餘欄:與 probe_id 合成 FK 指向 binding(probe_id, owner),使「人裁框不得寫 meets」成為單表 CHECK 可表達之不變式(免跨表 trigger)';
COMMENT ON COLUMN treaty_probe_binding.deadline IS
  '可空;有期限者(如 2026-10-14 日曆項)才填。「≥13 項綁 10-14」屬資料面驗收,DDL 不強制';
"""


def build_ddl() -> str:
    """→ 將執行之 DDL 全文（純函式，零副作用；`--apply` 逐字執行本字串）。"""
    return DDL


def ddl_invariants(ddl: str) -> list:
    """回傳被違反之不變式名清單（空＝全守）。純函式；selftest 以本尊驗綠、壞變體驗紅。

    #35 型 3 註記（沿 migrate_strangler_ledger_ddl.py 先例）：DDL 字串即 `--apply` 逐字執行之
    行為載體，對載體驗形＝對行為驗形；惟**沙盒實跑仍是更強證據**——本批鐵律「DDL 只備不跑」，
    故列為殘項（--apply 前於交易內建表→試插「無 ruler 之綁定」與「Steward 框之 meets」→ROLLBACK，
    實證兩條機械線真會拒，即計畫第 20 步驗收②與第 33 步驗收③之直接證據）。
    """
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    for t in (BINDING, READING):
        if ddl.count(f"CREATE TABLE IF NOT EXISTS {t}") != 1:
            bad.append(f"table_idempotent_{t}")
    for col in ("probe_id", "clause_ref", "deadline", "measure_key", "ruler_key",
                "check_cmd", "expect_expr", "owner", "created_at"):
        if not re.search(rf"^\s+{col}\s+\S", ddl, re.M):
            bad.append(f"binding_col_{col}")
    for col in ("reading_id", "probe_owner", "read_at", "value_text", "verdict", "machine_note"):
        if not re.search(rf"^\s+{col}\s+\S", ddl, re.M):
            bad.append(f"reading_col_{col}")
    # ── 機械線 1：只綁值不綁尺者插不進來（計畫第 20 步驗收②）──
    if not re.search(r"FOREIGN KEY \(measure_key, ruler_key\)\s*\n?\s*REFERENCES measure_registry \(measure_key, ruler_key\)",
                     ddl):
        bad.append("ruler_composite_fk")
    if not re.search(r"measure_key\s+text NOT NULL", ddl) or not re.search(r"ruler_key\s+text NOT NULL", ddl):
        bad.append("ruler_cols_not_null")     # 可空則 FK 對 NULL 放行 ⇒ 無尺之探針又活了
    # ── 機械線 2：人裁框 AI 寫不進「已達成」（計畫附(a)／第 33 步驗收③）──
    if not re.search(r"FOREIGN KEY \(probe_id, probe_owner\)\s*\n?\s*REFERENCES treaty_probe_binding \(probe_id, owner\)",
                     ddl):
        bad.append("owner_mirror_fk")         # 少了它,probe_owner 可謊報成 'AI' 繞過下面那條 CHECK
    if "UNIQUE (probe_id, owner)" not in ddl:
        bad.append("binding_owner_uk")        # 複合 FK 之標的鍵;缺之則上面那條 FK 建不起來
    if not re.search(r"probe_owner <> 'Steward' OR verdict = 'undecidable'", ddl):
        bad.append("steward_undecidable")
    if not re.search(r"probe_owner\s+text NOT NULL", ddl):
        bad.append("probe_owner_not_null")    # 可空則 CHECK 為 NULL⇒不拒,人裁框可寫 meets
    if "owner IN ('AI','Steward')" not in ddl:
        bad.append("owner_closed_set")        # 開放集則 owner='ai' 之類拼法可繞過 Steward 判定
    # ── 機械線 3：verdict 保守預設＋閉集 ──
    if "verdict IN ('meets','not_meets','undecidable')" not in ddl:
        bad.append("verdict_closed_set")
    if not re.search(r"verdict\s+text NOT NULL DEFAULT 'undecidable'", ddl):
        bad.append("verdict_default_undecidable")
    # ── 其餘欄位不變式 ──
    if "length(btrim(check_cmd)) > 0" not in ddl:
        bad.append("check_cmd_nonempty")      # 不能重跑的探針＝手抄換個地方
    if "length(btrim(expect_expr)) > 0" not in ddl:
        bad.append("expect_expr_nonempty")    # 沒有期望式就沒有 diff,--check 恆綠
    if "clause_ref ~ '^[^:]+:.+$'" not in ddl:
        bad.append("clause_ref_shape")        # file:line;指不回原文的綁定無法被人複驗
    if not re.search(r"deadline\s+date,", ddl):
        bad.append("deadline_nullable")       # 多數文件數字探針無期限;NOT NULL 會逼人填假期限
    if not re.search(r"value_text\s+text NOT NULL", ddl):
        bad.append("value_text_not_null")     # 量測列的存在理由就是那個值
    if "GENERATED ALWAYS AS IDENTITY" not in ddl:
        bad.append("reading_identity_pk")
    # ── 遷移純度 ──
    if "INSERT INTO" in ddl:
        bad.append("no_seed_in_ddl")          # 綁定走 sync_treaty_probes.py,不由遷移偷塞
    if re.search(r"\bUPDATE\b", ddl) or "DELETE FROM" in ddl or "TRUNCATE" in ddl:
        bad.append("no_mutation_in_ddl")
    if "ON DELETE CASCADE" in ddl or "ON UPDATE CASCADE" in ddl:
        bad.append("no_cascade")              # readings 是證據:不隨綁定變動被連坐刪改
    if "CREATE OR REPLACE FUNCTION" in ddl or "CREATE FUNCTION" in ddl:
        bad.append("guard_fn_not_self_made")  # #12：guard 函式住 migrate_honesty_guards_ddl.py
    return bad


def apply_order_blocker(parent_exists: bool) -> str | None:
    """→ 阻擋原因（None＝可 --apply）。純函式：標的表不在時，複合 FK 會使建表失敗 ⇒ 先擋、給修法。"""
    if parent_exists:
        return None
    return (f"{PARENT} 不在——本支之複合 FK 無標的，--apply 會失敗。"
            f"先跑：python3 scripts/migrate_measure_registry_ddl.py --apply")


# ── --verify-red：建表後實證「兩條機械線真的會拒」；全程在一個必定 ROLLBACK 的交易內 ──
# 這正是計畫第 20 步驗收②（無 ruler 之探針須被 FK 拒）與第 33 步驗收③（AI 不得對人裁框寫 meets）
# 之直接證據——把兩句驗收從備忘錄變成一條可重跑指令。
# 綠對照臂不可省（評測樣板地板之教訓）：表名／欄名若寫錯,**每一條紅臂都會因 42P01/42703 而被拒**
# ⇒ 全紅通過＝假綠。綠臂一失敗即揭穿。
_SEED = (
    "INSERT INTO measure_registry (measure_key, ruler_key, definition, repro_cmd)"
    " VALUES ('tp_selfverify','r_a','d','c')",
    "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
    " check_cmd, expect_expr, owner)"
    " VALUES ('tp_ai','X.md:1','tp_selfverify','r_a','cmd','470','AI')",
    "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
    " check_cmd, expect_expr, owner)"
    " VALUES ('tp_steward','Y.md:2','tp_selfverify','r_a','cmd','n/a','Steward')",
)
RED_PROBES = (
    ("綠對照：機器框寫 meets 可成功（表/欄名寫錯的話這裡就會炸，紅臂全綠即假綠）",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_ai','AI','470','meets')", None),
    ("綠對照：人裁框寫 undecidable 可成功（AI 只登錄量測值這條路必須是通的）",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_steward','Steward','88 處/32 檔','undecidable')", None),
    ("紅：綁定指向未登錄之尺 → ruler 複合 FK 拒（計畫第 20 步驗收②：只綁值不綁尺者插不進來）",
     "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
     " check_cmd, expect_expr, owner)"
     " VALUES ('tp_noruler','Z.md:3','tp_selfverify','r_NOT_REGISTERED','cmd','1','AI')", "23503"),
    ("紅：人裁框寫 meets → steward_undecidable CHECK 拒（計畫第 33 步驗收③）",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_steward','Steward','x','meets')", "23514"),
    ("紅：人裁框寫 not_meets → 同一條 CHECK 拒（「未達成」同屬人裁,AI 不得代判）",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_steward','Steward','x','not_meets')", "23514"),
    ("紅：把 probe_owner 謊報成 AI 以繞過上條 → owner 鏡射 FK 拒（欄位無法自稱另一種 owner）",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_steward','AI','x','meets')", "23503"),
    ("紅：verdict 給閉集外之值 → verdict_closed_set CHECK 拒",
     "INSERT INTO treaty_probe_reading (probe_id, probe_owner, value_text, verdict)"
     " VALUES ('tp_ai','AI','x','probably')", "23514"),
    ("紅：clause_ref 不含 file:line → clause_ref_shape CHECK 拒（指不回原文＝人無法複驗）",
     "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
     " check_cmd, expect_expr, owner)"
     " VALUES ('tp_badref','沒有行號','tp_selfverify','r_a','cmd','1','AI')", "23514"),
    ("紅：owner 給閉集外之值（小寫 steward）→ owner_closed_set CHECK 拒",
     "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
     " check_cmd, expect_expr, owner)"
     " VALUES ('tp_badowner','W.md:4','tp_selfverify','r_a','cmd','1','steward')", "23514"),
    ("紅：check_cmd 給空白字串 → check_cmd_nonempty CHECK 拒（不能重跑的探針＝手抄換個地方）",
     "INSERT INTO treaty_probe_binding (probe_id, clause_ref, measure_key, ruler_key,"
     " check_cmd, expect_expr, owner)"
     " VALUES ('tp_nocmd','V.md:5','tp_selfverify','r_a','   ','1','AI')", "23514"),
)


def probe_spec_defects(probes) -> list:
    """回傳探針規格本身的缺陷（空＝規格健全）。純函式；防「紅臂全綠＝假綠」與「期望碼過寬」。"""
    bad = []
    if not any(exp is None for _, _, exp in probes):
        bad.append("no_green_arm")            # 沒有綠對照臂 ⇒ 表名打錯時紅臂會全數「被拒」而假綠
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
        for t in (PARENT, BINDING, READING):
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            if not cur.fetchone()[0]:
                print(f"  · table {t} 不在——先 --apply 再跑 --verify-red")
                return 1
    ok = True
    try:
        with conn.cursor() as cur:
            for s in _SEED:
                cur.execute(s)
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
    print("--verify-red：" + ("全通過 ✓（已 ROLLBACK，零殘留）" if ok else "有失敗 ✗（機械線未如設計生效）"))
    return 0 if ok else 1


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{PARENT}",))
        parent_exists = bool(cur.fetchone()[0])
        blocker = apply_order_blocker(parent_exists)
        print(f"  {'✓' if parent_exists else '✗'} 前置 {PARENT}：{'在' if parent_exists else blocker}")
        for t in (BINDING, READING):
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            if not cur.fetchone()[0]:
                print(f"  · table {t} 不在（未 --apply）")
                continue
            cur.execute("""SELECT conname FROM pg_constraint
                           WHERE conrelid=%s::regclass ORDER BY 1""", (t,))
            cons = [r[0] for r in cur.fetchall()]
            print(f"  ✓ table {t} 在；約束 {len(cons)}：{', '.join(cons)}")
            cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass AND NOT tgisinternal", (t,))
            print(f"    · honesty trigger {cur.fetchone()[0]} 支（現行設計＝不掛；繫 M-P11／計畫第 21 步）")
        cur.execute("SELECT to_regclass(%s)", (f"public.{BINDING}",))
        if not cur.fetchone()[0]:
            return 0
        cur.execute(f"""SELECT count(*), count(*) FILTER (WHERE deadline = DATE '2026-10-14'),
                               count(*) FILTER (WHERE owner='Steward')
                        FROM {BINDING}""")
        n, n_1014, n_steward = cur.fetchone()
        print(f"  綁定：{n} 條（其中 deadline=2026-10-14 {n_1014} 條／目標 ≥13；人裁框 {n_steward} 條）")
        cur.execute(f"""SELECT count(*) FROM {BINDING} b
                        WHERE NOT EXISTS (SELECT 1 FROM {READING} r WHERE r.probe_id=b.probe_id)""")
        print(f"  未量測之綁定：{cur.fetchone()[0]} 條（>0 ⇒ read_treaty_probes.py 尚未跑完）")
        cur.execute(f"""SELECT count(*) FROM {READING}
                        WHERE probe_owner='Steward' AND verdict <> 'undecidable'""")
        n_bad = cur.fetchone()[0]
        print(f"  {'✓' if n_bad == 0 else '✗'} 人裁框之非 undecidable 量測：{n_bad} 列"
              f"（CHECK 在時結構上必為 0；非 0 ⇒ 約束被卸過，查 pg_constraint）")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{PARENT}",))
        blocker = apply_order_blocker(bool(cur.fetchone()[0]))
    if blocker:
        print(f"✗ {blocker}")
        return 1
    with db.transaction(conn) as cur:
        cur.execute(build_ddl())
    print(f"✓ DDL 冪等完成（{BINDING}＋{READING}＋索引，無 trigger）")
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

    class Cur:
        def execute(self, sql, params=None):
            self.last = sql
            if sql.startswith("SELECT to_regclass"):
                self._row = ("exists",)
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
    # ── 機械線 1：綁值必綁尺（計畫第 20 步驗收②）──
    chk("驗紅：複合 FK 退成單欄 measure_key → ruler_composite_fk 報違（尺沒綁上＝只綁值）",
        "ruler_composite_fk" in ddl_invariants(
            ddl.replace("FOREIGN KEY (measure_key, ruler_key)\n        REFERENCES measure_registry (measure_key, ruler_key)",
                        "FOREIGN KEY (measure_key)\n        REFERENCES measure_registry (measure_key)")))
    chk("驗紅：整條 ruler FK 拿掉 → ruler_composite_fk 報違",
        "ruler_composite_fk" in ddl_invariants(ddl.replace("REFERENCES measure_registry (measure_key, ruler_key)", "")))
    chk("驗紅：ruler_key 改可空 → ruler_cols_not_null 報違（FK 遇 NULL 放行,無尺探針復活）",
        "ruler_cols_not_null" in ddl_invariants(
            ddl.replace("ruler_key    text NOT NULL", "ruler_key    text         ")))
    # ── 機械線 2：人裁框 AI 寫不進「已達成」（計畫第 33 步驗收③）──
    chk("驗紅：拿掉 owner 鏡射 FK → owner_mirror_fk 報違（probe_owner 可謊報成 AI 繞過 CHECK）",
        "owner_mirror_fk" in ddl_invariants(
            ddl.replace("REFERENCES treaty_probe_binding (probe_id, owner)", "")))
    chk("驗紅：拿掉 binding 之 UNIQUE(probe_id, owner) → binding_owner_uk 報違（鏡射 FK 沒有標的鍵）",
        "binding_owner_uk" in ddl_invariants(ddl.replace("UNIQUE (probe_id, owner)", "UNIQUE (probe_id)")))
    chk("驗紅：拿掉 Steward⇒undecidable 之 CHECK → steward_undecidable 報違（AI 可對人裁框寫 meets）",
        "steward_undecidable" in ddl_invariants(
            ddl.replace("probe_owner <> 'Steward' OR verdict = 'undecidable'", "true")))
    chk("驗紅：CHECK 方向寫反（改成 AI 框才須 undecidable）→ steward_undecidable 報違",
        "steward_undecidable" in ddl_invariants(
            ddl.replace("probe_owner <> 'Steward' OR verdict = 'undecidable'",
                        "probe_owner <> 'AI' OR verdict = 'undecidable'")))
    chk("驗紅：probe_owner 改可空 → probe_owner_not_null 報違（CHECK 遇 NULL 不拒）",
        "probe_owner_not_null" in ddl_invariants(
            ddl.replace("probe_owner  text NOT NULL", "probe_owner  text         ")))
    chk("驗紅：owner 開放集 → owner_closed_set 報違（'steward' 小寫即繞過人裁判定）",
        "owner_closed_set" in ddl_invariants(ddl.replace("owner IN ('AI','Steward')", "owner IS NOT NULL")))
    # ── 機械線 3：verdict 保守預設＋閉集 ──
    chk("驗紅：verdict 預設改 meets → verdict_default_undecidable 報違（漏填即宣稱已達成）",
        "verdict_default_undecidable" in ddl_invariants(
            ddl.replace("verdict      text NOT NULL DEFAULT 'undecidable'",
                        "verdict      text NOT NULL DEFAULT 'meets'")))
    chk("驗紅：verdict 閉集放寬 → verdict_closed_set 報違",
        "verdict_closed_set" in ddl_invariants(
            ddl.replace("verdict IN ('meets','not_meets','undecidable')", "verdict IS NOT NULL")))
    # ── 其餘欄位不變式 ──
    chk("驗紅：check_cmd 只留 NOT NULL、拿掉長度 CHECK → check_cmd_nonempty 報違（空字串可過 NOT NULL）",
        "check_cmd_nonempty" in ddl_invariants(
            ddl.replace("CHECK (length(btrim(check_cmd)) > 0)", "CHECK (check_cmd IS NOT NULL)")))
    chk("驗紅：expect_expr 同型放寬 → expect_expr_nonempty 報違（無期望式則 diff 恆綠）",
        "expect_expr_nonempty" in ddl_invariants(
            ddl.replace("CHECK (length(btrim(expect_expr)) > 0)", "CHECK (true)")))
    chk("驗紅：clause_ref 不再要求 file:line → clause_ref_shape 報違（指不回原文＝人無法複驗）",
        "clause_ref_shape" in ddl_invariants(ddl.replace("clause_ref ~ '^[^:]+:.+$'", "clause_ref IS NOT NULL")))
    chk("驗紅：deadline 改 NOT NULL → deadline_nullable 報違（無期限探針被逼填假期限）",
        "deadline_nullable" in ddl_invariants(ddl.replace("deadline     date,", "deadline     date NOT NULL,")))
    chk("驗紅：value_text 改可空 → value_text_not_null 報違（量測列可不帶量到的值）",
        "value_text_not_null" in ddl_invariants(
            ddl.replace("value_text   text NOT NULL", "value_text   text         ")))
    chk("驗紅：少一欄（machine_note）→ reading_col_machine_note 報違",
        "reading_col_machine_note" in ddl_invariants(ddl.replace("    machine_note text,\n", "")))
    chk("驗紅：少一欄（expect_expr）→ binding_col_expect_expr 報違",
        "binding_col_expect_expr" in ddl_invariants(ddl.replace("    expect_expr  text NOT NULL,\n", "")))
    # ── 遷移純度 ──
    chk("驗紅：加 ON DELETE CASCADE → no_cascade 報違（刪綁定就連坐抹掉量測證據）",
        "no_cascade" in ddl_invariants(
            ddl.replace("REFERENCES treaty_probe_binding (probe_id, owner)",
                        "REFERENCES treaty_probe_binding (probe_id, owner) ON DELETE CASCADE")))
    chk("驗紅：DDL 偷塞綁定列 → no_seed_in_ddl 報違（綁定須走 sync_treaty_probes.py 之可審路徑）",
        "no_seed_in_ddl" in ddl_invariants(ddl + "\nINSERT INTO treaty_probe_binding VALUES ('p');"))
    chk("驗紅：DDL 夾帶 UPDATE → no_mutation_in_ddl 報違",
        "no_mutation_in_ddl" in ddl_invariants(ddl + "\nUPDATE treaty_probe_reading SET verdict='meets';"))
    chk("驗紅：DDL 自造 guard 函式 → guard_fn_not_self_made 報違（#12 單一住所）",
        "guard_fn_not_self_made" in ddl_invariants(
            ddl + "\nCREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$ $$;"))
    chk("驗紅：reading 表名改掉 → table_idempotent_treaty_probe_reading 報違",
        "table_idempotent_treaty_probe_reading" in ddl_invariants(
            ddl.replace(f"CREATE TABLE IF NOT EXISTS {READING}", "CREATE TABLE IF NOT EXISTS tpr")))
    chk("驗紅：拿掉 lock_timeout → 報違（#30 dump 期間鎖風暴）",
        "lock_timeout" in ddl_invariants(ddl.replace("SET lock_timeout = '5s';", "")))
    # ── --apply 次序閘（純函式）──
    chk("次序閘：measure_registry 不在 → 擋下並給修法（不讓 --apply 撞 FK 才失敗）",
        (apply_order_blocker(False) or "").startswith(PARENT))
    chk("次序閘：measure_registry 在 → 放行（None）", apply_order_blocker(True) is None)
    # ── --verify-red 之探針規格（防「紅臂全綠＝假綠」）──
    chk("探針規格健全：有綠對照臂、有紅臂、期望碼皆為 5 碼 SQLSTATE", probe_spec_defects(RED_PROBES) == [])
    chk("驗紅：拿掉綠對照臂 → no_green_arm 報違（表名打錯時紅臂會全數『被拒』而假綠）",
        "no_green_arm" in probe_spec_defects([p for p in RED_PROBES if p[2] is not None]))
    chk("驗紅：期望碼放寬成「有丟例外就算」→ loose_sqlstate 報違（42P01 會被當成閘生效）",
        any(d.startswith("loose_sqlstate") for d in probe_spec_defects(
            [(n, s, (True if e else e)) for n, s, e in RED_PROBES])))
    chk("紅臂兩型俱在：FK 拒(23503) 與 CHECK 拒(23514) 各至少一條",
        {p[2] for p in RED_PROBES if p[2]} >= {"23503", "23514"})
    chk("計畫兩句驗收各有專屬紅臂：無 ruler 之綁定(第20步②)＋人裁框寫 meets(第33步③)",
        any(p[2] == "23503" and "r_NOT_REGISTERED" in p[1] for p in RED_PROBES)
        and any(p[2] == "23514" and "'Steward','x','meets'" in p[1] for p in RED_PROBES))
    chk("謊報 owner 之繞道有紅臂（否則第33步③只擋老實人）",
        any(p[2] == "23503" and "'tp_steward','AI'" in p[1] for p in RED_PROBES))
    chk("綠對照臂涵蓋兩種 owner（只驗一種會漏掉 CHECK 把人裁框整個鎖死之誤植）",
        {"'tp_ai','AI'" in p[1] for p in RED_PROBES if p[2] is None} == {True, False} or
        (any("'tp_ai','AI'" in p[1] for p in RED_PROBES if p[2] is None)
         and any("'tp_steward','Steward'" in p[1] for p in RED_PROBES if p[2] is None)))
    # ── 對 --verify-red 本身實跑（假連線、零 DB）：好情況印綠，且**約束靜默失效時必須變紅** ──
    def run_vr(conn):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):     # 內層逐條輸出不灌進自測畫面
            return _verify_red(conn)

    fc = _fake_conn()
    chk("verify-red 實跑：約束全數如設計生效 → rc=0，且結束時已 rollback（零殘留）",
        run_vr(fc) == 0 and fc.rolled_back >= 1)
    chk("verify-red 驗紅：人裁框那條 CHECK 被卸掉（靜默放行 meets）→ rc≠0",
        run_vr(_fake_conn(silent_constraints=("人裁框寫 meets",))) != 0)
    chk("verify-red 驗紅：ruler 複合 FK 被卸掉（無尺之綁定靜默寫入）→ rc≠0",
        run_vr(_fake_conn(silent_constraints=("綁定指向未登錄之尺",))) != 0)
    chk("verify-red 驗紅：謊報 owner 之鏡射 FK 被卸掉 → rc≠0",
        run_vr(_fake_conn(silent_constraints=("謊報成 AI",))) != 0)
    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="條文↔live 探針綁定表 DDL（M-N1；--apply 須 hugo 明示、且須先建 measure_registry）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print-ddl", dest="print_ddl", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verify-red", dest="verify_red", action="store_true",
                    help="建表後實證兩條機械線真的會拒（全程 ROLLBACK、零殘留）")
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
