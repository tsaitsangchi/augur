#!/usr/bin/env python3
"""🎯 axis registry——「演化軸」由兩處寫死 CHECK 收斂為一張表，兩表改 FK（專章【待裁③】乙案）。

守 #29(b)（決定行為的資料住 DB、不寫死——軸是策展的、會增減、非邏輯）、#15、#6。

起因（2026-07-31，Steward 選定 ③＝乙）：同一個「軸」概念在兩張表有**兩套不同值域**、
皆寫死於 CHECK——
  `evolution_prereg_gate_axis_check`        ＝ ('tw','lai','raw','program')
  `evolution_hypothesis_hint_from_axis_check`＝ ('tw','lai','raw')   ← 連 'program' 都沒有
新增軸（如 'sim'）須改兩處 code；且已經漂移一次。乙案＝建 `evolution_axis` registry、
兩處 CHECK 改 FK：**新增軸＝INSERT 一列、零改碼**，且兩表值域自此不可能再漂移。

**本支只做結構收斂，不做語意擴張**：
  - 種子＝現有兩 CHECK 之**聯集** {tw, lai, raw, program}；**不含 'sim'**——
    'sim' 之登錄繫於專章 enact（普遍晉升路徑之人類授權門），不得由遷移夾帶。
  - ⚠ **誠實揭露之語意副作用**：統一後 `from_axis='program'` 成為合法
    （原 hint 表 CHECK 不含之）。此為「消除漂移」之必然結果，非本支目的；
    已於 --check 印出、並記於本 docstring 供 Steward 位階認定時併酌。
  - registry 掛 DELETE/TRUNCATE 拒絕（軸之退場＝政策變更，須走治權、不得靜默刪列）；
    FK 本身亦使被引用之軸無法被刪。

**apply 前置**：Steward 之位階認定（patch 或重大判準修正）作成後方得 --apply
（GOVERNANCE-ANNEX v1.1 第 2 條第 3 款；認定屬 Steward 保留）。

執行指令矩陣
------------
    python3 scripts/migrate_evolution_axis_registry_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_evolution_axis_registry_ddl.py --check    # 唯讀：現況＋資料相容性＋將變更
    python3 scripts/migrate_evolution_axis_registry_ddl.py --apply    # 實作（冪等；須 Steward 位階認定後）
    python3 scripts/migrate_evolution_axis_registry_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

# 種子＝現有兩 CHECK 之聯集；描述為既有事實之簡述，非新判準
SEED_AXES = (
    ("tw", "台股演化軸（TWEVO 迭代；第一登錄域之足跡）"),
    ("lai", "本地 AI 能力軸（LAIEVO 評測臂／量尺）"),
    ("raw", "raw data 假說軸（RAWEVO 掃描）"),
    ("program", "迭代程序自身軸（程序重演／meta 門）"),
    # ('sim', ...) 不在此——繫於模擬方法專章 enact，登錄＝INSERT 一列（屆時亦零改碼）
)

DDL_TABLE = """
CREATE TABLE IF NOT EXISTS evolution_axis (
    axis          text PRIMARY KEY,
    description   text NOT NULL,
    registered_at timestamptz NOT NULL DEFAULT now(),
    note          text
);
CREATE OR REPLACE FUNCTION evolution_axis_no_delete() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'evolution_axis 為軸 registry：DELETE/TRUNCATE 一律拒絕（軸之退場＝政策變更，須走治權留痕）';
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_evo_axis_no_delete ON evolution_axis;
CREATE TRIGGER trg_evo_axis_no_delete
    BEFORE DELETE ON evolution_axis
    FOR EACH ROW EXECUTE FUNCTION evolution_axis_no_delete();
DROP TRIGGER IF EXISTS trg_evo_axis_no_truncate ON evolution_axis;
CREATE TRIGGER trg_evo_axis_no_truncate
    BEFORE TRUNCATE ON evolution_axis
    FOR EACH STATEMENT EXECUTE FUNCTION evolution_axis_no_delete();
"""

# (表, 欄, 舊 CHECK 名, 新 FK 名)
REWIRES = (
    ("evolution_prereg_gate", "axis",
     "evolution_prereg_gate_axis_check", "evolution_prereg_gate_axis_fkey"),
    ("evolution_hypothesis_hint", "from_axis",
     "evolution_hypothesis_hint_from_axis_check", "evolution_hypothesis_hint_from_axis_fkey"),
)


def plan_lines() -> list[str]:
    """純函式（可自測）：本遷移將做的事，逐條可讀。"""
    out = [f"建 evolution_axis（DELETE/TRUNCATE 拒絕）＋種子 {len(SEED_AXES)} 軸"
           f"（{'/'.join(a for a, _ in SEED_AXES)}；**不含 sim**——繫於專章 enact）"]
    for tbl, col, chk, fk in REWIRES:
        out.append(f"{tbl}.{col}：DROP CHECK {chk} → ADD FK {fk} REFERENCES evolution_axis")
    out.append("語意副作用（誠實）：from_axis='program' 由不合法變合法（原 hint CHECK 不含）")
    return out


def check(cur) -> int:
    cur.execute("SELECT to_regclass('public.evolution_axis')")
    has = cur.fetchone()[0] is not None
    print(f"evolution_axis：{'已存在' if has else '未建'}")
    if has:
        cur.execute("SELECT axis FROM evolution_axis ORDER BY 1")
        print(f"  已登錄軸：{[r[0] for r in cur.fetchall()]}")
    for tbl, col, chk, fk in REWIRES:
        cur.execute("SELECT conname, contype FROM pg_constraint WHERE conrelid=%s::regclass "
                    "AND conname IN (%s, %s)", (tbl, chk, fk))
        st = {n: t for n, t in cur.fetchall()}
        cur.execute(f"SELECT {col}, count(*) FROM {tbl} GROUP BY 1 ORDER BY 1")
        vals = cur.fetchall()
        seed = {a for a, _ in SEED_AXES}
        bad = [v for v, _ in vals if v not in seed]
        print(f"{tbl}.{col}：CHECK={'在' if chk in st else '無'}｜FK={'在' if fk in st else '無'}"
              f"｜現有值 {vals}｜FK 相容性：{'✗ 有種子外值 ' + str(bad) if bad else '✓ 全在種子內'}")
    print("── 遷移計畫：")
    for ln in plan_lines():
        print(f"  - {ln}")
    print("（唯讀。--apply 前置＝Steward 位階認定，見 docstring）")
    return 0


def apply(conn) -> int:
    cur = conn.cursor()
    cur.execute(DDL_TABLE)
    for axis, desc in SEED_AXES:
        cur.execute("INSERT INTO evolution_axis (axis, description) VALUES (%s,%s) "
                    "ON CONFLICT (axis) DO NOTHING", (axis, desc))
    for tbl, col, chk, fk in REWIRES:
        cur.execute("SELECT 1 FROM pg_constraint WHERE conrelid=%s::regclass AND conname=%s",
                    (tbl, chk))
        if cur.fetchone():
            cur.execute(f"ALTER TABLE {tbl} DROP CONSTRAINT {chk}")
        cur.execute("SELECT 1 FROM pg_constraint WHERE conrelid=%s::regclass AND conname=%s",
                    (tbl, fk))
        if not cur.fetchone():
            cur.execute(f"ALTER TABLE {tbl} ADD CONSTRAINT {fk} "
                        f"FOREIGN KEY ({col}) REFERENCES evolution_axis(axis)")
    conn.commit()
    print("已收斂：兩表 axis 值域自此同源（registry）；新增軸＝INSERT 一列、零改碼")
    return check(cur)


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    seed = [a for a, _ in SEED_AXES]
    chk("種子＝兩 CHECK 之聯集（tw/lai/raw/program）", seed == ["tw", "lai", "raw", "program"])
    chk("**種子不含 sim**（sim 繫於專章 enact，遷移不得夾帶）", "sim" not in seed)
    lines = "\n".join(plan_lines())
    chk("計畫含兩處 CHECK→FK", lines.count("DROP CHECK") == 2 and lines.count("ADD FK") == 2)
    chk("語意副作用有誠實揭露（program 入 from_axis）", "program" in lines and "誠實" in lines)
    chk("registry 有 DELETE/TRUNCATE 拒絕", "BEFORE DELETE" in DDL_TABLE
        and "BEFORE TRUNCATE" in DDL_TABLE)
    chk("種子冪等（ON CONFLICT DO NOTHING）",
        "ON CONFLICT (axis) DO NOTHING" in __import__("inspect").getsource(apply))
    src_apply = __import__("inspect").getsource(apply)
    chk("constraint 增刪皆條件式（冪等可重跑）",
        src_apply.count("pg_constraint") == 2 and "if cur.fetchone()" in src_apply
        and "if not cur.fetchone()" in src_apply)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="axis registry 遷移（兩處寫死 CHECK → 一表 FK；冪等）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db

    with db.connect() as conn:
        if a.apply:
            return apply(conn)
        return check(conn.cursor())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
        sys.exit(main(["--check"]))
    sys.exit(main())
