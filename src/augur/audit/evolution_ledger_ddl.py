#!/usr/bin/env python
"""三軸演化帳本 DDL 常數 — 單一住所(V2 §4.2;Phase 5 V2-LEDGER-go,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):三本 iteration ledger(raw/tw/lai)**逐字同構**——共同骨架由同一常數清單生成、
   各軸只加專屬欄(C2 裁決:不合表,合表會把專屬欄退化成無 CHECK 的 JSONB、且一條 CHECK 壞三軸)。
   另含跨軸 hint 表(UNIQUE dedup_key+decision 單向前進)、證據協定落點 evidence_run、RAW 覆蓋快照、
   heavy-slot 積壓表、題庫漂移落表、預註冊 gate(V2-SUNSET 落點)。**pytest 斷言三表同一清單生成**
   (tests/test_evolution_ledger_ddl.py)——這是「同構」由文字變機械的落點。
   誠實閘:三本 ledger＋hint/evidence 五表已全升 UPDATE-GUC honesty_ledger_guard
   (hint/evidence=**B4-P2a 2026-08-01**;三 ledger=**B4-P2b 2026-08-02**,RULING-2026-043 併案
   ——UPDATE 須帶 SET LOCAL augur.honesty_write='on' 通行證,裸手默改被拒;legacy 名
   hint_no_*/evidence_no_*/tw_iter_no_*/raw_iter_no_*/lai_iter_no_* 先卸不掛回;
   hint_decision_forward_only 獨立 domain 閘保留)。兩 guard 函式皆住 migrate_honesty_guards_ddl(#12)。
守 #12(單一住所)· #29b(schema 由本檔常數生成、migrate 只消費)· P4.E3(append-only)。
執行指令矩陣:
  python -m augur.audit.evolution_ledger_ddl            # 無參數:印用途+表清單(唯讀)
  python -m augur.audit.evolution_ledger_ddl --selftest # 零 DB 紅綠(同構/CHECK/命名不變式)
"""
from __future__ import annotations

import sys

# 三本 ledger 共同骨架(逐字同構;C2 契約必要欄=V2-P-yes 硬要求、非建議)
LEDGER_COMMON = (
    ("iteration_id", "BIGSERIAL PRIMARY KEY"),
    ("iteration_uid", "TEXT NOT NULL UNIQUE CHECK (iteration_uid ~ '^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$')"),
    ("axis", "TEXT NOT NULL CHECK (axis IN ('tw','lai','raw'))"),
    ("opened_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("closed_at", "TIMESTAMPTZ"),
    ("status", "TEXT NOT NULL DEFAULT 'planned' CHECK (status IN "
               "('planned','running','succeeded','failed','halted','stopped_no_gain'))"),
    ("trigger_code", "VARCHAR(64) NOT NULL"),
    ("steps_json", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
    ("gain", "BOOLEAN"),
    ("gain_basis", "VARCHAR(32)"),          # 各軸 CHECK 於專屬段補(I1:判準本體不共用)
    ("gain_evidence", "JSONB NOT NULL DEFAULT '{}'::jsonb"),
    ("consecutive_no_gain", "INTEGER NOT NULL DEFAULT 0"),
    ("stop_reason", "TEXT"),
    ("briefs_in", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
    ("briefs_out", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
    ("hints_in", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
    ("hints_out", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
    ("cross_notify_json", "JSONB NOT NULL DEFAULT '[]'::jsonb"),   # 佈告零效力(I7)
    ("gate_ref", "TEXT"),
    ("closed_by", "TEXT"),
    ("notes", "TEXT"),
    ("superseded_by", "TEXT"),
)

# 各軸實名+專屬欄+gain_basis CHECK(§4.2.2)
AXES = {
    "raw": {
        "table": "raw_evolution_iteration_ledger",
        "extra": (
            ("tier", "TEXT CHECK (tier IN ('P1','P2','P3'))"),
            ("gap_summary_json", "JSONB NOT NULL DEFAULT '{}'::jsonb"),
            ("coverage_snapshot_ref", "BIGINT"),
        ),
        "gain_basis_check": "('new_gap','hint_approved','none','incomparable')",
    },
    "tw": {
        "table": "evolution_iteration_ledger",
        "extra": (
            ("apply_allowed", "BOOLEAN NOT NULL DEFAULT false"),
            ("dual_green_names", "TEXT[]"),
            ("near_miss_json", "JSONB"),
            ("source_run_id", "BIGINT"),
            ("evidence_hash", "TEXT"),      # 內容定址(整數 serial 跨機不可攜之結構修正)
        ),
        "gain_basis_check": "('dual_green_delta','prodset_delta','arena_prereg','none','incomparable')",
    },
    "lai": {
        "table": "local_ai_iteration_ledger",
        "extra": (
            ("eval_set_id", "TEXT"),
            ("eval_code_hash", "TEXT"),
            ("n_trials", "INTEGER"),
            ("selection_scope", "TEXT"),
        ),
        "gain_basis_check": "('eval_delta','none','incomparable')",
    },
}

GUARD_FN = "honesty_delete_only_guard"      # 既有函式(migrate_honesty_guards_ddl;#12 不重造)
GUC_GUARD_FN = "honesty_ledger_guard"       # UPDATE-GUC 版(B4-P2a;同住 migrate_honesty_guards_ddl)


def ledger_ddl(axis: str) -> str:
    """單軸 ledger 完整 DDL(表+gain_basis CHECK+索引+UPDATE-GUC honesty 雙 trigger;
    B4-P2b:legacy delete-only 名先卸不掛回——本檔冪等重跑不得把 delonly 掛回,#12/#19)。"""
    spec = AXES[axis]
    t = spec["table"]
    cols = ",\n    ".join(f"{c} {d}" for c, d in LEDGER_COMMON + spec["extra"])
    return f"""CREATE TABLE IF NOT EXISTS {t} (
    {cols},
    CHECK (gain_basis IS NULL OR gain_basis IN {spec['gain_basis_check']}),
    CHECK (axis = '{axis}')
);
CREATE INDEX IF NOT EXISTS ix_{axis}_iter_status ON {t} (status, opened_at DESC);
DROP TRIGGER IF EXISTS {axis}_iter_no_delete_row ON {t};
DROP TRIGGER IF EXISTS {axis}_iter_no_truncate ON {t};
DROP TRIGGER IF EXISTS trg_{t}_honesty_row ON {t};
CREATE TRIGGER trg_{t}_honesty_row BEFORE UPDATE OR DELETE ON {t}
    FOR EACH ROW EXECUTE FUNCTION {GUC_GUARD_FN}();
DROP TRIGGER IF EXISTS trg_{t}_honesty_trunc ON {t};
CREATE TRIGGER trg_{t}_honesty_trunc BEFORE TRUNCATE ON {t}
    FOR EACH STATEMENT EXECUTE FUNCTION {GUC_GUARD_FN}();"""


HINT_FORWARD_FN = """CREATE OR REPLACE FUNCTION hint_decision_forward_only() RETURNS trigger AS $$
BEGIN
    IF OLD.decision <> 'pending' AND NEW.decision IS DISTINCT FROM OLD.decision THEN
        RAISE EXCEPTION 'hint % decision 已定(%)不可回改——單向前進(P4.E3);要翻案走新 hint 列+duplicate_of',
            OLD.hint_id, OLD.decision;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;"""

HINT_DDL = f"""CREATE TABLE IF NOT EXISTS evolution_hypothesis_hint (
    hint_id             TEXT PRIMARY KEY,
    from_axis           TEXT NOT NULL CHECK (from_axis IN ('tw','lai','raw')),
    from_iteration_uid  TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    hint_text           TEXT NOT NULL,
    suggested_map       JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    provenance          JSONB NOT NULL,
    dedup_key           TEXT NOT NULL UNIQUE,
    duplicate_of        TEXT,
    decision            TEXT NOT NULL DEFAULT 'pending'
                        CHECK (decision IN ('pending','approved','data_debt_only','rejected')),
    decided_by          TEXT,
    decided_at          TIMESTAMPTZ,
    decision_code       TEXT,
    gate_ref            TEXT,
    CHECK (decision = 'pending'
           OR (decided_by IS NOT NULL AND decided_at IS NOT NULL AND decision_code IS NOT NULL))
);
DROP TRIGGER IF EXISTS hint_decision_forward_only ON evolution_hypothesis_hint;
CREATE TRIGGER hint_decision_forward_only BEFORE UPDATE ON evolution_hypothesis_hint
    FOR EACH ROW EXECUTE FUNCTION hint_decision_forward_only();
DROP TRIGGER IF EXISTS hint_no_delete ON evolution_hypothesis_hint;
DROP TRIGGER IF EXISTS hint_no_truncate ON evolution_hypothesis_hint;
DROP TRIGGER IF EXISTS trg_evolution_hypothesis_hint_honesty_row ON evolution_hypothesis_hint;
CREATE TRIGGER trg_evolution_hypothesis_hint_honesty_row BEFORE UPDATE OR DELETE ON evolution_hypothesis_hint
    FOR EACH ROW EXECUTE FUNCTION {GUC_GUARD_FN}();
DROP TRIGGER IF EXISTS trg_evolution_hypothesis_hint_honesty_trunc ON evolution_hypothesis_hint;
CREATE TRIGGER trg_evolution_hypothesis_hint_honesty_trunc BEFORE TRUNCATE ON evolution_hypothesis_hint
    FOR EACH STATEMENT EXECUTE FUNCTION {GUC_GUARD_FN}();"""

EVIDENCE_DDL = f"""CREATE TABLE IF NOT EXISTS evolution_evidence_run (
    evidence_id     BIGSERIAL PRIMARY KEY,
    axis            TEXT NOT NULL CHECK (axis IN ('tw','raw')),
    suite_id        TEXT NOT NULL,
    code_hash       TEXT NOT NULL,
    arm             TEXT NOT NULL CHECK (arm IN ('ceiling','floor','shuffled','mismatched','live')),
    metric_name     TEXT NOT NULL,
    metric_value    DOUBLE PRECISION,
    n_items         INTEGER NOT NULL,
    n_valid         INTEGER NOT NULL,
    n_excluded      INTEGER NOT NULL DEFAULT 0,
    is_invalid      BOOLEAN NOT NULL DEFAULT false,
    n_trials        INTEGER,
    selection_scope TEXT,
    detail          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (axis, suite_id, code_hash, arm, metric_name)
);
DROP TRIGGER IF EXISTS evidence_no_delete ON evolution_evidence_run;
DROP TRIGGER IF EXISTS evidence_no_truncate ON evolution_evidence_run;
DROP TRIGGER IF EXISTS trg_evolution_evidence_run_honesty_row ON evolution_evidence_run;
CREATE TRIGGER trg_evolution_evidence_run_honesty_row BEFORE UPDATE OR DELETE ON evolution_evidence_run
    FOR EACH ROW EXECUTE FUNCTION {GUC_GUARD_FN}();
DROP TRIGGER IF EXISTS trg_evolution_evidence_run_honesty_trunc ON evolution_evidence_run;
CREATE TRIGGER trg_evolution_evidence_run_honesty_trunc BEFORE TRUNCATE ON evolution_evidence_run
    FOR EACH STATEMENT EXECUTE FUNCTION {GUC_GUARD_FN}();"""

COVERAGE_DDL = """CREATE TABLE IF NOT EXISTS raw_table_coverage_snapshot (
    snapshot_id       BIGSERIAL PRIMARY KEY,
    iteration_uid     TEXT NOT NULL,
    dataset           TEXT NOT NULL,
    est_rows          BIGINT,
    exact_rows        BIGINT,
    min_date          DATE, max_date DATE,
    date_semantics    TEXT CHECK (date_semantics IN
                        ('observation','event_future_ok','calendar','snapshot','no_date')),
    staleness_days    INTEGER,
    freq_class        TEXT,
    gap_years_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
    catalog_registered BOOLEAN NOT NULL,
    last_attest_ref   BIGINT,
    last_attest_passed BOOLEAN,
    gap_class         TEXT,
    detail            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (iteration_uid, dataset)
);"""

DEFERRED_DDL = """CREATE TABLE IF NOT EXISTS evolution_deferred_work (
    defer_id      BIGSERIAL PRIMARY KEY,
    axis          TEXT NOT NULL,
    step_key      TEXT NOT NULL,
    requested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason        TEXT NOT NULL,
    cleared_at    TIMESTAMPTZ,
    cleared_by    TEXT,
    detail        JSONB NOT NULL DEFAULT '{}'::jsonb
);"""

EVAL_SET_CHECK_DDL = """CREATE TABLE IF NOT EXISTS local_model_eval_set_check (
    check_id    BIGSERIAL PRIMARY KEY,
    set_id      TEXT NOT NULL,
    checked_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    n_items     INTEGER NOT NULL,
    n_drifted   INTEGER NOT NULL,
    detail      JSONB NOT NULL DEFAULT '{}'::jsonb
);"""

PREREG_NO_GOALPOST_FN = """CREATE OR REPLACE FUNCTION prereg_gate_no_goalpost() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'DELETE on evolution_prereg_gate 遭拒:預註冊閘不可刪(挪門柱;P4.E3)';
    END IF;
    IF OLD.status IN ('evaluated_pass','evaluated_fail','superseded') THEN
        RAISE EXCEPTION 'gate % 已終態(%)不可改——挪門柱禁止;要改開新 gate 列並 supersede',
            OLD.gate_id, OLD.status;
    END IF;
    IF NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha THEN
        RAISE EXCEPTION 'gate % criteria_sha 不可改(判準凍結;升嚴走 GATE-raise 開新列)', OLD.gate_id;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;"""

PREREG_DDL = """CREATE TABLE IF NOT EXISTS evolution_prereg_gate (
    gate_id         TEXT PRIMARY KEY,
    axis            TEXT NOT NULL CHECK (axis IN ('tw','lai','raw','program')),
    purpose         TEXT NOT NULL,
    criteria        JSONB NOT NULL,
    criteria_sha    TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN
                      ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')),
    preregistered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_by     TEXT, approved_at TIMESTAMPTZ,
    git_sha         TEXT,
    evaluated_at    TIMESTAMPTZ, result_snapshot JSONB, evaluation_ref TEXT,
    note            TEXT
);
DROP TRIGGER IF EXISTS prereg_gate_no_goalpost ON evolution_prereg_gate;
CREATE TRIGGER prereg_gate_no_goalpost BEFORE UPDATE OR DELETE ON evolution_prereg_gate
    FOR EACH ROW EXECUTE FUNCTION prereg_gate_no_goalpost();"""

# ALTER 增補(§4.3;kill_switch scope 已由 migrate_philosophy_evolution_ddl 承載,不重複)
ALTERS = (
    "ALTER TABLE local_model_eval_run ADD COLUMN IF NOT EXISTS n_trials INTEGER",
    "ALTER TABLE local_model_eval_run ADD COLUMN IF NOT EXISTS selection_scope TEXT",
    "ALTER TABLE local_model_eval_run ADD COLUMN IF NOT EXISTS n_excluded INTEGER DEFAULT 0",
    "ALTER TABLE principle_factor_map ADD COLUMN IF NOT EXISTS hint_id TEXT",
    "ALTER TABLE principle_factor_map ADD COLUMN IF NOT EXISTS provenance JSONB",
    "ALTER TABLE principle_factor_map ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
)

# C6(v2 §3.3):kill switch 由單列升「逐 scope 一列」(tw/lai/raw/global)。
# why 住這裡:set_evolution_kill_switch.py 讀寫皆假設 scope 欄+四種子列已在;此升級曾無 migration
# 承載(2026-07-27 PC002 換機還原實證:UndefinedColumn、G-KILL 讀取路徑 fail-closed 阻塞)——#12 補正。
KILL_SCOPE_STMTS = (
    "ALTER TABLE evolution_kill_switch ADD COLUMN IF NOT EXISTS scope TEXT",
    "UPDATE evolution_kill_switch SET scope='global' WHERE scope IS NULL",
    # 拆舊單列設計之 CHECK(switch_id=1);DROP IF EXISTS=冪等
    "ALTER TABLE evolution_kill_switch DROP CONSTRAINT IF EXISTS evolution_kill_switch_switch_id_check",
    """DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_kill_switch_scope') THEN
            ALTER TABLE evolution_kill_switch
                ADD CONSTRAINT chk_kill_switch_scope CHECK (scope IN ('tw','lai','raw','global'));
        END IF;
    END $$""",
    # UNIQUE(scope)=set_state「UPDATE ... WHERE scope=」正確性前提
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_kill_switch_scope ON evolution_kill_switch (scope)",
    # 種子四 scope 全列(set_state 為 UPDATE-only、無列即拒;既有列保留其 state=halt 語意不動)
    """INSERT INTO evolution_kill_switch (switch_id, scope, state, set_by, reason)
       SELECT (SELECT coalesce(max(switch_id), 0) FROM evolution_kill_switch) + row_number() OVER (),
              s, 'clear', 'migrate_evolution_v2_ddl', 'C6 scope 種子'
       FROM unnest(ARRAY['global','tw','lai','raw']) AS s
       WHERE NOT EXISTS (SELECT 1 FROM evolution_kill_switch k WHERE k.scope = s)""",
    "ALTER TABLE evolution_kill_switch ALTER COLUMN scope SET NOT NULL",
)

ALL_TABLES = tuple(AXES[a]["table"] for a in ("raw", "tw", "lai")) + (
    "evolution_hypothesis_hint", "evolution_evidence_run", "raw_table_coverage_snapshot",
    "evolution_deferred_work", "local_model_eval_set_check", "evolution_prereg_gate")


def full_ddl() -> list[str]:
    """全部 DDL 語句(依相依序;函式先於 trigger)。"""
    return ([HINT_FORWARD_FN, PREREG_NO_GOALPOST_FN]
            + [ledger_ddl(a) for a in ("raw", "tw", "lai")]
            + [HINT_DDL, EVIDENCE_DDL, COVERAGE_DDL, DEFERRED_DDL, EVAL_SET_CHECK_DDL, PREREG_DDL]
            + list(ALTERS) + list(KILL_SCOPE_STMTS))


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    common_cols = [c for c, _ in LEDGER_COMMON]
    for want in ("iteration_uid", "briefs_in", "briefs_out", "hints_in", "hints_out",
                 "consecutive_no_gain", "steps_json", "gate_ref", "gain", "gain_basis",
                 "opened_at", "closed_at"):
        chk(f"契約必要欄在共同骨架:{want}", want in common_cols)
    ddls = {a: ledger_ddl(a) for a in AXES}
    chk("三表由同一常數清單生成(逐字同構)", all(
        all(f"{c} {d}" in ddls[a] for c, d in LEDGER_COMMON) for a in AXES))
    chk("gain_basis CHECK 各軸不同(I1 判準本體不共用)",
        len({AXES[a]["gain_basis_check"] for a in AXES}) == 3)
    chk("axis 自鎖 CHECK(raw 表只能 axis='raw')", all(f"CHECK (axis = '{a}')" in ddls[a] for a in AXES))
    chk("uid regex 三軸共用", all("^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$" in ddls[a] for a in AXES))
    chk("三 ledger 已升 UPDATE-GUC(B4-P2b RULING-2026-043):honesty_ledger_guard 雙 trigger"
        "+卸 legacy 名不掛回",
        all(GUC_GUARD_FN in ddls[a] and GUARD_FN not in ddls[a]
            and f"BEFORE UPDATE OR DELETE ON {AXES[a]['table']}" in ddls[a]
            and f"DROP TRIGGER IF EXISTS {a}_iter_no_delete_row ON" in ddls[a]
            and f"CREATE TRIGGER {a}_iter_no_delete_row" not in ddls[a]
            and f"DROP TRIGGER IF EXISTS {a}_iter_no_truncate ON" in ddls[a]
            and f"CREATE TRIGGER {a}_iter_no_truncate" not in ddls[a]
            for a in AXES))
    chk("hint/evidence 已升 UPDATE-GUC(B4-P2a RULING-2026-043):honesty_ledger_guard 雙 trigger"
        "+卸 legacy 名不掛回",
        GUC_GUARD_FN in HINT_DDL and GUC_GUARD_FN in EVIDENCE_DDL
        and GUARD_FN not in HINT_DDL and GUARD_FN not in EVIDENCE_DDL
        and "BEFORE UPDATE OR DELETE ON evolution_hypothesis_hint" in HINT_DDL
        and "BEFORE UPDATE OR DELETE ON evolution_evidence_run" in EVIDENCE_DDL
        and "DROP TRIGGER IF EXISTS hint_no_delete ON" in HINT_DDL
        and "CREATE TRIGGER hint_no_delete" not in HINT_DDL
        and "DROP TRIGGER IF EXISTS evidence_no_delete ON" in EVIDENCE_DDL
        and "CREATE TRIGGER evidence_no_delete" not in EVIDENCE_DDL)
    chk("hint:dedup_key UNIQUE+decision 單向前進 trigger",
        "dedup_key           TEXT NOT NULL UNIQUE" in HINT_DDL and "hint_decision_forward_only" in HINT_DDL)
    chk("hint:非 pending 須三欄齊(decided_by/at/code)", "decision = 'pending'" in HINT_DDL)
    chk("evidence:五臂封閉集+UNIQUE 防重", "'ceiling','floor','shuffled','mismatched','live'" in EVIDENCE_DDL
        and "UNIQUE (axis, suite_id, code_hash, arm, metric_name)" in EVIDENCE_DDL)
    chk("coverage:last_attest_passed 欄在(基線可能是失敗態,須誠實記)", "last_attest_passed" in COVERAGE_DDL)
    chk("prereg:no_goalpost(終態不可改+criteria_sha 凍結)", "criteria_sha 不可改" in PREREG_NO_GOALPOST_FN)
    chk("ALTER 全冪等(IF NOT EXISTS)", all("IF NOT EXISTS" in a for a in ALTERS))
    # 2026-07-27 補正:原斷言稱 scope 住 migrate_philosophy_evolution_ddl——實查該檔零 scope(虛指),
    # 換機還原即斷(PC002 實證 UndefinedColumn)。C6 升級自此住本檔 KILL_SCOPE_STMTS(#12 唯一住所)。
    chk("C6 kill_switch scope 升級住本檔(四 scope 種子+UNIQUE+CHECK)",
        any("ADD COLUMN IF NOT EXISTS scope" in s for s in KILL_SCOPE_STMTS)
        and any("ux_kill_switch_scope" in s for s in KILL_SCOPE_STMTS)
        and all(x in " ".join(KILL_SCOPE_STMTS) for x in ("'global'", "'tw'", "'lai'", "'raw'")))
    chk("ALTERS 與 KILL_SCOPE 分治(kill_switch 不混入一般 ALTER)",
        not any("kill_switch" in a for a in ALTERS))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print(f"表清單({len(ALL_TABLES)}):")
    for t in ALL_TABLES:
        print(f"  {t}")
    print(f"ALTER 增補:{len(ALTERS)} 條;落地=scripts/migrate_evolution_v2_ddl.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
