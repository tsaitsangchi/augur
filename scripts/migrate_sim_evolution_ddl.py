#!/usr/bin/env python3
"""🎯 sim 軸八表落地（P2）——專章 v1.0 之載體；含 M2/M3 既有表補強；M1 已廢（registry 取代）。

守 #6（--apply 明示）· #15（append-only guard 全掛）· #12（DDL 單一住所＝本檔）。

法源：《模擬方法與自進化元件專章 v1.0》（gp_86c8063fc688 enacted 2026-07-31，hugo TTY 親簽）。
DDL 全文源自實作計畫書 §三(a)（reports/augur_local_ai_market_sim_evolution_plan_20260731.md），
本檔為其**可執行 SSOT**；抽入時注入 trigger 冪等前綴（原文裸 CREATE TRIGGER 重跑會炸）。

**專章判準之 DB 級落地（違反者寫不進去，非靠自律）**：
  §3.6 gain_basis CHECK 僅 ('calibration_delta','none','incomparable')——無方向/報酬 basis 可寫
  §3.7 tilt_free CHECK (tilt_free)——以模型預測 tilt 抽樣之方法註冊不進來
  §2.3 is_synthetic CHECK (is_synthetic)＋trust_rank CHECK (='TR-C')——LLM 產物永久標記+天花板
  §4.1 chk_sev_promote_signed——promoted 必帶人簽三件（偵測級，甲′明文承認非預防）
  §5.1/5.2 verdict append-only＋UPDATE 綁 honesty_ledger_guard；candidate forward-only
  H-1 全部新表**無逐路徑/價格欄**（永久除外項）

**甲′補強第 2 項（本檔自測鎖）**：本檔不設任何人名旗標、不 INSERT 任何人簽欄——
selftest 以行為驗證鎖住（建 parser 斷言無該類旗標；掃 apply SQL 斷言零人簽寫入）。

**M1 已廢（誠實記明）**：計畫原 M1＝把 axis CHECK 改寫死清單加 'sim'；已被 ③乙
（axis registry FK，migrate_evolution_axis_registry_ddl.py 2026-07-31 施作）取代，
**本檔不得重跑 M1**——重跑會把 FK 退回寫死清單。
M2 之 axis 部分亦順 ③乙 改為 FK（非再寫死一份）。

執行指令矩陣
------------
    python3 scripts/migrate_sim_evolution_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_sim_evolution_ddl.py --check    # 唯讀：八表/約束/guard 現況
    python3 scripts/migrate_sim_evolution_ddl.py --apply    # 建八表＋M2/M3（冪等）
    python3 scripts/migrate_sim_evolution_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

DDL_TABLES = [
    ("simulation_method_registry", """
CREATE TABLE IF NOT EXISTS simulation_method_registry (
    method        text PRIMARY KEY,
    family        text NOT NULL CHECK (family IN
                  ('bootstrap','parametric','episode_replay','episode_analog','copula','evt')),
    purpose       text NOT NULL,
    param_schema  jsonb NOT NULL DEFAULT '{}'::jsonb,
    tilt_free     boolean NOT NULL DEFAULT true CHECK (tilt_free),
    status        text NOT NULL DEFAULT 'registered'
                  CHECK (status IN ('registered','retired')),
    gate_ref      text REFERENCES governance_proposal(proposal_id),
    approved_by   text,
    approved_at   timestamptz,
    registered_at timestamptz NOT NULL DEFAULT now(),
    git_sha       text NOT NULL,
    note          text,
    CONSTRAINT chk_smr_registered_signed CHECK (
        status <> 'registered'
        OR (approved_by IS NOT NULL AND approved_at IS NOT NULL AND gate_ref IS NOT NULL))
);
DROP TRIGGER IF EXISTS smr_no_delete ON simulation_method_registry;
CREATE TRIGGER smr_no_delete   BEFORE DELETE   ON simulation_method_registry
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS smr_no_truncate ON simulation_method_registry;
CREATE TRIGGER smr_no_truncate BEFORE TRUNCATE ON simulation_method_registry
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
COMMENT ON COLUMN simulation_method_registry.tilt_free IS
    'H-2 硬綁:CHECK(tilt_free) 使「以模型預測 tilt 抽樣」之方法在 DB 層永遠註冊不進來';
"""),
    ("sim_evolution_candidate", """
CREATE TABLE IF NOT EXISTS sim_evolution_candidate (
    candidate_id  text PRIMARY KEY,                       -- 'simc_'||left(sha256(canonical_spec),12)
    method        text NOT NULL REFERENCES simulation_method_registry(method),
    spec          jsonb NOT NULL,
    spec_sha      text NOT NULL UNIQUE,
    origin        text NOT NULL CHECK (origin IN ('llm_local','grid','human','carryover')),
    origin_ref    text,
    is_synthetic  boolean NOT NULL DEFAULT true,
    trust_rank    text NOT NULL DEFAULT 'TR-C' CHECK (trust_rank = 'TR-C'),
    status        text NOT NULL DEFAULT 'candidate'
                  CHECK (status IN ('candidate','evaluating','evaluated','promoted','killed','superseded')),
    iteration_uid text,
    gate_ref      text REFERENCES evolution_prereg_gate(gate_id),
    created_at    timestamptz NOT NULL DEFAULT now(),
    git_sha       text NOT NULL,
    note          text
);
CREATE INDEX IF NOT EXISTS idx_simc_status  ON sim_evolution_candidate (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_simc_method  ON sim_evolution_candidate (method);

CREATE OR REPLACE FUNCTION sim_candidate_forward_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.status IN ('promoted','killed','superseded')
       AND NEW.status IS DISTINCT FROM OLD.status THEN
        RAISE EXCEPTION 'candidate % 已終態(%)不可回改——單向前進(P4.E3);翻案走新列+新證據',
            OLD.candidate_id, OLD.status;
    END IF;
    IF NEW.spec_sha IS DISTINCT FROM OLD.spec_sha OR NEW.method IS DISTINCT FROM OLD.method THEN
        RAISE EXCEPTION 'candidate % 身分欄不可改(T.28 同一 iff);換 spec=新列', OLD.candidate_id;
    END IF;
    RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS simc_forward_only ON sim_evolution_candidate;
CREATE TRIGGER simc_forward_only BEFORE UPDATE   ON sim_evolution_candidate
    FOR EACH ROW       EXECUTE FUNCTION sim_candidate_forward_only();
DROP TRIGGER IF EXISTS simc_no_delete ON sim_evolution_candidate;
CREATE TRIGGER simc_no_delete    BEFORE DELETE   ON sim_evolution_candidate
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS simc_no_truncate ON sim_evolution_candidate;
CREATE TRIGGER simc_no_truncate  BEFORE TRUNCATE ON sim_evolution_candidate
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""),
    ("sim_run_link", """
CREATE TABLE IF NOT EXISTS sim_run_link (
    run_id        text PRIMARY KEY REFERENCES mc_simulation_run(run_id),
    candidate_id  text NOT NULL REFERENCES sim_evolution_candidate(candidate_id),
    gate_id       text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    iteration_uid text NOT NULL,
    arm           text NOT NULL CHECK (arm IN ('live','ceiling','floor','shuffled','mismatched','robot')),
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_simlink_cand ON sim_run_link (candidate_id, arm);
DROP TRIGGER IF EXISTS simlink_no_delete ON sim_run_link;
CREATE TRIGGER simlink_no_delete   BEFORE DELETE   ON sim_run_link
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS simlink_no_truncate ON sim_run_link;
CREATE TRIGGER simlink_no_truncate BEFORE TRUNCATE ON sim_run_link
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""),
    ("sim_realized_outcome", """
CREATE TABLE IF NOT EXISTS sim_realized_outcome (
    run_id         text PRIMARY KEY REFERENCES mc_simulation_run(run_id),
    target_id      text NOT NULL,
    asof_date      date NOT NULL,
    horizon_td     integer NOT NULL,
    label_date     date NOT NULL,
    realized_close double precision,
    realized_logret double precision,
    settle_mode    text NOT NULL CHECK (settle_mode IN ('normal','last_trade','unsettleable')),
    settled_at     timestamptz NOT NULL DEFAULT now(),
    git_sha        text NOT NULL,
    CONSTRAINT chk_sro_forward CHECK (label_date > asof_date),
    CONSTRAINT chk_sro_unsettleable_null CHECK (
        settle_mode <> 'unsettleable' OR realized_logret IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_sro_asof ON sim_realized_outcome (asof_date, horizon_td);
DROP TRIGGER IF EXISTS sro_no_delete ON sim_realized_outcome;
CREATE TRIGGER sro_no_delete   BEFORE DELETE   ON sim_realized_outcome
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS sro_no_truncate ON sim_realized_outcome;
CREATE TRIGGER sro_no_truncate BEFORE TRUNCATE ON sim_realized_outcome
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""),
    ("sim_calibration_eval", """
CREATE TABLE IF NOT EXISTS sim_calibration_eval (
    eval_id        bigserial PRIMARY KEY,
    gate_id        text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    candidate_id   text REFERENCES sim_evolution_candidate(candidate_id),
    arm            text NOT NULL CHECK (arm IN ('live','ceiling','floor','shuffled','mismatched','robot')),
    eval_set_id    text NOT NULL,
    eval_code_hash text NOT NULL,
    n_runs         integer NOT NULL,
    n_valid        integer NOT NULL,
    n_excluded     integer NOT NULL DEFAULT 0,
    is_invalid     boolean NOT NULL DEFAULT false,
    cov_p50        double precision,
    cov_p80        double precision,
    cov_p90        double precision,
    pinball_mean   double precision,
    crps_mean      double precision,
    pit_ks_stat    double precision,
    pit_ks_p       double precision,
    detail         jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at     timestamptz NOT NULL DEFAULT now(),
    git_sha        text NOT NULL,
    CONSTRAINT chk_sce_valid_le_runs CHECK (n_valid <= n_runs)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_sce_cell ON sim_calibration_eval
    (gate_id, coalesce(candidate_id,'-'), arm, eval_set_id, eval_code_hash);
DROP TRIGGER IF EXISTS sce_no_delete ON sim_calibration_eval;
CREATE TRIGGER sce_no_delete   BEFORE DELETE   ON sim_calibration_eval
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS sce_no_truncate ON sim_calibration_eval;
CREATE TRIGGER sce_no_truncate BEFORE TRUNCATE ON sim_calibration_eval
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""),
    ("sim_evolution_verdict", """
CREATE TABLE IF NOT EXISTS sim_evolution_verdict (
    verdict_id        bigserial PRIMARY KEY,
    candidate_id      text NOT NULL REFERENCES sim_evolution_candidate(candidate_id),
    gate_id           text NOT NULL REFERENCES evolution_prereg_gate(gate_id),
    verdict           text NOT NULL CHECK (verdict IN ('promoted','killed','undecidable')),
    basis             jsonb NOT NULL,
    evidence_eval_ids bigint[] NOT NULL,
    decided_by        text,
    decided_at        timestamptz,
    gate_proposal_ref text REFERENCES governance_proposal(proposal_id),
    reopen_of         bigint REFERENCES sim_evolution_verdict(verdict_id),
    created_at        timestamptz NOT NULL DEFAULT now(),
    git_sha           text NOT NULL,
    CONSTRAINT chk_sev_promote_signed CHECK (
        verdict <> 'promoted'
        OR (decided_by IS NOT NULL AND decided_at IS NOT NULL AND gate_proposal_ref IS NOT NULL)),
    CONSTRAINT chk_sev_evidence_nonempty CHECK (array_length(evidence_eval_ids,1) >= 1)
);
CREATE INDEX IF NOT EXISTS idx_sev_cand ON sim_evolution_verdict (candidate_id, created_at DESC);
DROP TRIGGER IF EXISTS sev_no_delete ON sim_evolution_verdict;
CREATE TRIGGER sev_no_delete   BEFORE DELETE   ON sim_evolution_verdict
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS sev_no_truncate ON sim_evolution_verdict;
CREATE TRIGGER sev_no_truncate BEFORE TRUNCATE ON sim_evolution_verdict
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS sev_no_update ON sim_evolution_verdict;
CREATE TRIGGER sev_no_update   BEFORE UPDATE   ON sim_evolution_verdict
    FOR EACH ROW       EXECUTE FUNCTION honesty_ledger_guard();
"""),
    ("sim_llm_proposal", """
CREATE TABLE IF NOT EXISTS sim_llm_proposal (
    proposal_id   bigserial PRIMARY KEY,
    iteration_uid text NOT NULL,
    model         text NOT NULL,
    prompt_sha    text NOT NULL,
    raw_output    text NOT NULL,
    parsed_ok     boolean NOT NULL,
    reject_reason text,
    candidate_id  text REFERENCES sim_evolution_candidate(candidate_id),
    is_synthetic  boolean NOT NULL DEFAULT true CHECK (is_synthetic),
    trust_rank    text NOT NULL DEFAULT 'TR-C' CHECK (trust_rank = 'TR-C'),
    latency_ms    integer,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_simllm_iter ON sim_llm_proposal (iteration_uid, created_at);
DROP TRIGGER IF EXISTS simllm_no_delete ON sim_llm_proposal;
CREATE TRIGGER simllm_no_delete   BEFORE DELETE   ON sim_llm_proposal
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS simllm_no_truncate ON sim_llm_proposal;
CREATE TRIGGER simllm_no_truncate BEFORE TRUNCATE ON sim_llm_proposal
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""),
    ("sim_evolution_iteration_ledger", """
CREATE TABLE IF NOT EXISTS sim_evolution_iteration_ledger (
    iteration_id        bigserial PRIMARY KEY,
    iteration_uid       text NOT NULL UNIQUE
                        CHECK (iteration_uid ~ '^sim-[0-9]{8}-r[0-9]{2}$'),
    axis                text NOT NULL DEFAULT 'sim' CHECK (axis = 'sim'),
    opened_at           timestamptz NOT NULL DEFAULT now(),
    closed_at           timestamptz,
    status              text NOT NULL DEFAULT 'planned'
                        CHECK (status IN ('planned','running','succeeded','failed','halted','stopped_no_gain')),
    trigger_code        varchar(64) NOT NULL,
    steps_json          jsonb NOT NULL DEFAULT '[]'::jsonb,
    gain                boolean,
    gain_basis          varchar(32)
                        CHECK (gain_basis IS NULL OR gain_basis IN
                              ('calibration_delta','none','incomparable')),
    gain_evidence       jsonb NOT NULL DEFAULT '{}'::jsonb,
    consecutive_no_gain integer NOT NULL DEFAULT 0,
    stop_reason         text,
    hints_in            jsonb NOT NULL DEFAULT '[]'::jsonb,
    hints_out           jsonb NOT NULL DEFAULT '[]'::jsonb,
    gate_ref            text REFERENCES evolution_prereg_gate(gate_id),
    eval_set_id         text,
    eval_code_hash      text,
    n_trials            integer,
    selection_scope     text,
    apply_allowed       boolean NOT NULL DEFAULT false,
    closed_by           text,
    superseded_by       text,
    evidence_hash       text,
    notes               text
);
DROP TRIGGER IF EXISTS sim_iter_no_delete ON sim_evolution_iteration_ledger;
CREATE TRIGGER sim_iter_no_delete   BEFORE DELETE   ON sim_evolution_iteration_ledger
    FOR EACH ROW       EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS sim_iter_no_truncate ON sim_evolution_iteration_ledger;
CREATE TRIGGER sim_iter_no_truncate BEFORE TRUNCATE ON sim_evolution_iteration_ledger
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
""")
]

# M2:統一證據帳容納 sim 軸（axis→FK 順 ③乙）與 robot 臂
M2_SQL = """
ALTER TABLE evolution_evidence_run DROP CONSTRAINT IF EXISTS evolution_evidence_run_axis_check;
ALTER TABLE evolution_evidence_run DROP CONSTRAINT IF EXISTS evolution_evidence_run_axis_fkey;
ALTER TABLE evolution_evidence_run ADD CONSTRAINT evolution_evidence_run_axis_fkey
    FOREIGN KEY (axis) REFERENCES evolution_axis(axis);
ALTER TABLE evolution_evidence_run DROP CONSTRAINT IF EXISTS evolution_evidence_run_arm_check;
ALTER TABLE evolution_evidence_run ADD CONSTRAINT evolution_evidence_run_arm_check
    CHECK (arm IN ('ceiling','floor','shuffled','mismatched','robot','live'));
"""

# M3:生產模擬表誠實閘——B4-P2b(RULING-2026-043 併案 2026-08-02)升 UPDATE-GUC honesty_ledger_guard
# (原 delete-only 之 mcsim_no_* legacy 名先卸不掛回;upsert 衝突分支寫入者已帶通行證;#12/#19 住所同步,
# 本檔冪等重跑不得把 delonly 掛回)。sim 專章七表維持 delete-only 不變(P2c 緩議)。
M3_SQL = """
DROP TRIGGER IF EXISTS mcsim_no_delete ON mc_simulation_run;
DROP TRIGGER IF EXISTS mcsim_no_truncate ON mc_simulation_run;
DROP TRIGGER IF EXISTS trg_mc_simulation_run_honesty_row ON mc_simulation_run;
CREATE TRIGGER trg_mc_simulation_run_honesty_row BEFORE UPDATE OR DELETE ON mc_simulation_run
    FOR EACH ROW       EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_mc_simulation_run_honesty_trunc ON mc_simulation_run;
CREATE TRIGGER trg_mc_simulation_run_honesty_trunc BEFORE TRUNCATE ON mc_simulation_run
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
"""

EXPECT_TABLES = [name for name, _ in DDL_TABLES]


def check(cur) -> int:
    ok = True
    for name in EXPECT_TABLES:
        cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
        has = cur.fetchone()[0] is not None
        ntrg = 0
        if has:
            cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass "
                        "AND NOT tgisinternal", (name,))
            ntrg = cur.fetchone()[0]
        print(f"  {name:34} {'✓在' if has else '✗無'}｜trigger {ntrg}")
        ok = ok and has and ntrg >= 2
    cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid='mc_simulation_run'::regclass "
                "AND NOT tgisinternal")
    n = cur.fetchone()[0]
    print(f"  {'mc_simulation_run(M3)':34} guard trigger {n}（≥2 才 PASS）")
    ok = ok and n >= 2
    cur.execute("SELECT conname FROM pg_constraint WHERE conrelid='evolution_evidence_run'::regclass "
                "AND conname='evolution_evidence_run_axis_fkey'")
    m2 = cur.fetchone() is not None
    print(f"  {'evidence_run.axis→FK(M2)':34} {'✓' if m2 else '✗'}")
    ok = ok and m2
    print("PASS 八表＋M2/M3 就位" if ok else "未就位（跑 --apply）")
    return 0 if ok else 1


def apply(conn) -> int:
    cur = conn.cursor()
    # lock_timeout（2026-07-31 實證教訓 #30）：對熱表下 DDL 時，排隊中的 ACCESS EXCLUSIVE
    # 會反向擋住該表一切查詢。5s 拿不到即放棄整批 rollback（冪等、改天重跑），不排隊。
    cur.execute("SET lock_timeout = '5s'")
    for name, sql in DDL_TABLES:
        cur.execute(sql)
        print(f"  ✓ {name}")
    cur.execute(M2_SQL)
    print("  ✓ M2 evidence_run（axis→FK、arm 加 robot）")
    cur.execute(M3_SQL)
    print("  ✓ M3 mc_simulation_run UPDATE-GUC honesty(B4-P2b;DELETE/TRUNCATE 恆拒)")
    conn.commit()
    return check(cur)


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    all_sql = "\n".join(sql for _, sql in DDL_TABLES)
    chk("八表齊備", len(DDL_TABLES) == 8)
    chk("§3.6 gain_basis 閉集（無方向/報酬 basis）",
        "'calibration_delta','none','incomparable'" in all_sql.replace("\n", "")
        or "('calibration_delta','none','incomparable')" in " ".join(all_sql.split()))
    chk("§3.7 tilt_free 硬綁", "CHECK (tilt_free)" in all_sql)
    chk("§2.3 synthetic 永久標記＋TR-C 天花板",
        "CHECK (is_synthetic)" in all_sql and "CHECK (trust_rank = 'TR-C')" in all_sql)
    chk("§4.1 promoted 必帶人簽三件", "chk_sev_promote_signed" in all_sql)
    chk("每張表皆有 no_delete＋no_truncate",
        all(("no_delete" in sql and "no_truncate" in sql) for _, sql in DDL_TABLES))
    chk("trigger 冪等（每 CREATE TRIGGER 前有 DROP IF EXISTS）",
        all_sql.count("CREATE TRIGGER") == all_sql.count("DROP TRIGGER IF EXISTS"))
    chk("H-1 無逐路徑/價格點位欄",
        not __import__("re").search(r"\b(price_path|daily_price|target_price|path_json)\b", all_sql))
    chk("verdict UPDATE 綁 honesty_ledger_guard", "honesty_ledger_guard" in dict(DDL_TABLES)["sim_evolution_verdict"])
    chk("M3 已升 UPDATE-GUC（B4-P2b）:honesty_ledger_guard 雙 trigger+卸 mcsim_no_* 不掛回",
        "honesty_ledger_guard" in M3_SQL and "honesty_delete_only_guard" not in M3_SQL
        and "BEFORE UPDATE OR DELETE ON mc_simulation_run" in M3_SQL
        and "DROP TRIGGER IF EXISTS mcsim_no_delete ON" in M3_SQL
        and "CREATE TRIGGER mcsim_no_delete" not in M3_SQL
        and "DROP TRIGGER IF EXISTS mcsim_no_truncate ON" in M3_SQL
        and "CREATE TRIGGER mcsim_no_truncate" not in M3_SQL)
    chk("sim 七表維持 delete-only 不變（P2c 緩議:住所歸 sim 專章、不由 honesty 機制代升）",
        all("honesty_delete_only_guard" in sql for name, sql in DDL_TABLES
            if name != "sim_evolution_verdict"))
    chk("M1 未收錄（registry FK 不得被退回寫死清單）",
        "evolution_prereg_gate_axis_check" not in all_sql + M2_SQL + M3_SQL)

    # 甲′補強第 2 項:行為鎖
    ap = _parser()
    opts = {o for a in ap._actions for o in a.option_strings}
    chk("無人名旗標（--approved-by/--decided-by/--promoted-by 不存在）",
        not opts & {"--approved-by", "--decided-by", "--promoted-by", "--signed-by"})
    import inspect
    apply_src = inspect.getsource(apply)
    chk("apply 本體零 INSERT（只跑 DDL 常量，無任何資料寫入）",
        "INSERT" not in apply_src.upper())
    chk("DDL 常量無 INSERT INTO（本檔只建載體、不填內容——方法註冊須人簽另走）",
        "INSERT INTO" not in (all_sql + M2_SQL + M3_SQL).upper())
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="sim 軸八表落地（P2；冪等）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = _parser().parse_args(argv)
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
