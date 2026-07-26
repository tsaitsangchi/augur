#!/usr/bin/env python
"""三軸演化 v2 全部新表＋ALTER 之冪等落地(V2 Phase 5 V2-LEDGER-go;hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):消費 `augur.audit.evolution_ledger_ddl` 之 DDL 常數(單一住所 #12,本檔零 schema
   文字)——三本同構 ledger、跨軸 hint、證據協定 evidence_run、RAW 覆蓋快照、heavy-slot 積壓、
   題庫漂移落表、預註冊 gate。**前置硬條件已達成**(v2 §6 Phase 5:至少一條跨軸邊有實料——arena 首批
   4,128 列已於 2026-07-26 結算)。落地後把 V2-SUNSET 轉入 evolution_prereg_gate 凍結(--seed-sunset;
   criteria_sha=audits/V2-ADOPTED-SUNSET-20260726.md 之 65eda893…,approved_by 誠實留 NULL=對話拍板非親簽)。
守 #6(DDL 明示)· #12(單一住所)· #30(dump 期禁 DDL——跑前自查 pg_stat_activity)· #29a/d。
執行指令矩陣:
  python scripts/migrate_evolution_v2_ddl.py                # 無參數:現況(唯讀:各表存在?列數?)
  python scripts/migrate_evolution_v2_ddl.py --dry-run      # 印全部 SQL、不動 DB
  python scripts/migrate_evolution_v2_ddl.py --apply        # 執行(冪等;先查無 pg_dump 在跑)
  python scripts/migrate_evolution_v2_ddl.py --seed-sunset  # V2-SUNSET 轉入 prereg gate(冪等)
  python scripts/migrate_evolution_v2_ddl.py --selftest     # 零 DB 紅綠
"""
import argparse
import hashlib
import json
import sys

import _bootstrap  # noqa: F401
from augur.audit.evolution_ledger_ddl import ALL_TABLES, AXES, LEDGER_COMMON, full_ddl
from augur.core import db

SUNSET_CRITERIA = """期限：2026-10-31
(a) arena 至少結算一批且方向門有可讀數；或
(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。"""
SUNSET_SHA = "65eda89328adc75d95e6e03dcf0f31571d5cbb5131efefa45ce9c856d7d8cd01"


def _dump_running(cur):
    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE application_name LIKE 'pg_dump%'")
    return cur.fetchone()[0] > 0


def apply(dry):
    stmts = full_ddl()
    if dry:
        for s in stmts:
            print(s + ";\n")
        print(f"(--dry-run:{len(stmts)} 段未執行)")
        return 0
    with db.connect() as conn, db.transaction(conn) as cur:
        if _dump_running(cur):
            print("✗ pg_dump 進行中——#30 dump 期禁 DDL(鎖風暴);等 dump 完再跑")
            return 1
        for s in stmts:
            cur.execute(s)
    print(f"✓ v2 DDL 落地(冪等):{len(ALL_TABLES)} 表 + ALTER 增補")
    return status()


def seed_sunset():
    """V2-SUNSET → prereg gate(axis='program')。冪等;sha 與 audits 登錄檔逐位一致才寫(#15)。"""
    live_sha = hashlib.sha256(SUNSET_CRITERIA.encode()).hexdigest()
    if live_sha != SUNSET_SHA:
        print(f"✗ criteria 文字與凍結 sha 不符:{live_sha[:12]} vs {SUNSET_SHA[:12]}——不寫(挪門柱嫌疑,先查)")
        return 1
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT status FROM evolution_prereg_gate WHERE gate_id='V2-SUNSET'")
        row = cur.fetchone()
        if row:
            print(f"✓ V2-SUNSET 已在 gate(status={row[0]})——冪等跳過")
            return 0
        cur.execute("""INSERT INTO evolution_prereg_gate
            (gate_id, axis, purpose, criteria, criteria_sha, status, note)
            VALUES ('V2-SUNSET', 'program', %s, %s, %s, 'preregistered', %s)""",
            ("三軸自進化 program-level 落日條款(v2 §2.1;三選一達成續命,全未達成整體停止)",
             json.dumps({"deadline": "2026-10-31", "criteria_text": SUNSET_CRITERIA,
                         "consequence": "三軸整體停止、帳本封存、不得換 trigger_code 重開"},
                        ensure_ascii=False),
             SUNSET_SHA,
             "hugo 對話拍板 2026-07-26;登錄=audits/V2-ADOPTED-SUNSET-20260726.md;"
             "approved_by 誠實留 NULL(對話拍板非親簽,§8.1 榮譽制紀律)——hugo 親跑 UPDATE 填 approved_by 即轉 approved"))
    print(f"✓ V2-SUNSET 已凍結入 evolution_prereg_gate(criteria_sha={SUNSET_SHA[:12]}…,status=preregistered)")
    print("  hugo 親簽指令(可選,轉 approved):")
    print("  UPDATE evolution_prereg_gate SET status='approved', approved_by='hugo', approved_at=now()"
          " WHERE gate_id='V2-SUNSET';")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in ALL_TABLES:
            cur.execute("SELECT to_regclass('public.'||%s)", (t,))
            if cur.fetchone()[0] is None:
                print(f"  {t}: (未建)")
                continue
            cur.execute(f"SELECT count(*) FROM {t}")  # noqa: S608  表名來自本檔常數白名單
            print(f"  {t}: {cur.fetchone()[0]} 列")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("SUNSET criteria sha 逐位符合 audits 凍結值",
        hashlib.sha256(SUNSET_CRITERIA.encode()).hexdigest() == SUNSET_SHA)
    stmts = full_ddl()
    chk("DDL 全冪等(CREATE IF NOT EXISTS/DROP IF EXISTS/ADD IF NOT EXISTS)",
        all(("IF NOT EXISTS" in s) or ("CREATE OR REPLACE" in s) or ("DROP TRIGGER IF EXISTS" in s)
            for s in stmts))
    chk("三 ledger 表名與 §4.2.2 實名一致", {AXES[a]["table"] for a in AXES}
        == {"raw_evolution_iteration_ledger", "evolution_iteration_ledger", "local_ai_iteration_ledger"})
    chk("共同骨架 22 欄(C2 契約)", len(LEDGER_COMMON) == 22)
    import inspect
    chk("apply 先查 pg_dump(#30 鎖風暴)", "_dump_running" in inspect.getsource(apply))
    chk("seed_sunset:sha 不符即拒寫(#15)", "不寫" in inspect.getsource(seed_sunset))
    chk("seed_sunset:approved_by 留 NULL+印 hugo 親簽指令(不代打)",
        "誠實留 NULL" in inspect.getsource(seed_sunset) and "hugo 親簽指令" in inspect.getsource(seed_sunset))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="三軸演化 v2 DDL 落地(消費 evolution_ledger_ddl 常數)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed-sunset", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.seed_sunset:
        return seed_sunset()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
