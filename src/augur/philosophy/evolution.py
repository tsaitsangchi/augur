"""augur 哲學↔市場進化狀態機 — PME 閉環純函式（閘評估／kill-switch／覆蓋分類）。

🎯 這支在做什麼（白話）：把「假說→市場重驗→有界自動晉升」的機械閘與緊急停做成
   可回歸的 library（零 IO `--selftest`）。不進預測 runtime；不生成原則；不含下單。
   編排腳本（coverage／run／apply／kill-switch／A7 status sync）呼叫本模組；G-PROM／G-ECON
   證據由呼叫端餵入——skeleton 可誠實 SKIP；`--local-gates` 餵本地重算後裁決 PASS／FAIL／SKIP
   （SKIP ≠ PASS）。A7：status=validated 僅認 promote APPLY；map validated_*≠假綠授權。

守 #1 #14 #15 #18；計畫 SSOT＝reports/augur_philosophy_market_evolution_loop_plan_20260724.md。

執行指令矩陣（本檔=library #18；免 DB 免 API）:
  python -m augur.philosophy.evolution              # 印用途+公開入口（唯讀）
  python -m augur.philosophy.evolution --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from typing import Any, Mapping

from augur.core.prodset_contract import (
    PRODSET_ACTIVE,
    PRODSET_REMOVED,
    PRODSET_TABLE,
)

# §4.1 機械閘（全綠才可自動 APPLY；SKIP ≠ PASS）
GATE_IDS = (
    "G-ISO",
    "G-MAP",
    "G-PROM",
    "G-ECON",
    "G-ATTEST",
    "G-KILL",
    "G-NOEXEC",
)

KILL_CLEAR = "clear"
KILL_HALT = "halt"
KILL_STATES = (KILL_CLEAR, KILL_HALT)

COVERAGE_CLASSES = ("mapped", "missing", "retired", "blocked_div")

# A7：philosophy_principle.status ↔ 晉升實證（抽樣／分類規則釘死）
# 不變式：map.validated_* 存在 ≠ 得翻 status=validated（須雙閘 APPLY；禁假綠）
STATUS_ALIGNMENT_CLASSES = (
    "aligned_validated",            # status=validated ∧ promote applied
    "aligned_untested_clean",       # untested ∧ 無 map validated_*
    "map_evidence_gate_rejected",   # untested ∧ 有 validated_* ∧ rejected_gate（誠實殘留）
    "map_evidence_pending_auto",    # untested ∧ pending_auto（待 APPLY）
    "map_evidence_no_queue",        # untested ∧ 有 validated_* ∧ 尚無 queue
    "apply_lag",                    # 已 promote applied 但 status≠validated（可機械收斂）
    "fake_validated",               # status=validated 卻無 promote apply（A7 違規）
    "coverage_blocked_or_missing",  # 僅 blocked_div／missing／retired；禁冒充已對齊 validated
)

# 僅此二類＝A7 違規；raw untested∩validated_* 在 gate_rejected 下≠違規
A7_VIOLATION_CLASSES = frozenset({"fake_validated", "apply_lag"})

# G-DIV-1 PAUSED：股息族覆蓋／重驗／上線不得標完備（計畫 §3.1）
BLOCKED_DIV_FEATURES = frozenset({
    "dividend_yield",
    "dividend_cash",
    "dividend_stock",
    "TaiwanStockDividend",
})

# G-NOEXEC：APPLY 路徑禁券商／下單字面（靜態掃描用；片段拼接避免本檔自誤報）
NOEXEC_FORBIDDEN_LITERALS = tuple(
    "".join(parts)
    for parts in (
        ("place", "_order"),
        ("submit", "_order"),
        ("broker", "_api"),
        ("shio", "aji"),
        ("fugle", "_order"),
        ("auto", "_trade"),
        ("券商", "下單"),
    )
)

# 預設閘閾值（釘入 evolution_run.config_json；同 run 禁事後改寫）
# G-PROM 三關＝方法論 §四：(a) as-of IC (b) |HAC-t|≥2 (c) ≥3 seed 多因子增量 Δ>0
# G-ECON＝#14：淨 Sharpe 優於基準 ∧ MaxDD ≥ floor（floor 為負值下界）
DEFAULT_GATE_CONFIG: dict[str, Any] = {
    "policy": "PME-AUTO-B",
    "kill_required": True,
    "fz_keep": True,
    "gates": {
        "G-PROM": {
            "require_hac_t": True,
            "min_abs_hac_t": 2.0,
            "min_seeds": 3,
            "min_panels": 10,
            "min_delta_ic": 0.0,  # 多 seed 平均 Δ IC 須 > 此值（穩定正增量）
        },
        "G-ECON": {
            "require_sharpe_vs_benchmark": True,
            "cost": 0.00585,
            "top_frac": 0.1,
            "max_dd_floor": -0.60,  # portfolio_net MaxDD 不得劣於此（更負＝FAIL）
        },
    },
    "soul_wording_pending": False,  # [I] G-PME-SOUL closed 2026-07-24；靈魂／#20／A.53 已寫入
}

EVOLUTION_DDL = [
    """CREATE TABLE IF NOT EXISTS evolution_run (
        run_id          BIGSERIAL PRIMARY KEY,
        started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        finished_at     TIMESTAMPTZ,
        since_date      DATE NOT NULL,
        horizon_h       INTEGER NOT NULL,
        code_sha        VARCHAR(64),
        config_json     JSONB NOT NULL,
        status          VARCHAR(32) NOT NULL,
        kill_switch_at_start VARCHAR(16) NOT NULL,
        notes           TEXT,
        CHECK (status IN ('running','succeeded','failed','halted')),
        CHECK (kill_switch_at_start IN ('clear','halt'))
    )""",
    """CREATE TABLE IF NOT EXISTS evolution_coverage_snapshot (
        snapshot_id     BIGSERIAL PRIMARY KEY,
        run_id          BIGINT REFERENCES evolution_run(run_id) ON DELETE CASCADE,
        as_of           TIMESTAMPTZ NOT NULL DEFAULT now(),
        feature         VARCHAR(255) NOT NULL,
        map_count       INTEGER NOT NULL,
        in_feature_values BOOLEAN NOT NULL,
        coverage_class  VARCHAR(32) NOT NULL,
        detail          JSONB,
        CHECK (coverage_class IN ('mapped','missing','retired','blocked_div'))
    )""",
    """CREATE TABLE IF NOT EXISTS promotion_queue (
        queue_id        BIGSERIAL PRIMARY KEY,
        run_id          BIGINT NOT NULL REFERENCES evolution_run(run_id) ON DELETE CASCADE,
        principle_id    INTEGER REFERENCES philosophy_principle(principle_id),
        feature         VARCHAR(255) NOT NULL,
        action          VARCHAR(16) NOT NULL,
        gate_json       JSONB NOT NULL,
        queue_status    VARCHAR(32) NOT NULL,
        decided_at      TIMESTAMPTZ,
        decided_by      VARCHAR(64) NOT NULL DEFAULT 'evolution_engine',
        apply_log_id    BIGINT,
        CHECK (action IN ('promote','demote','freeze')),
        CHECK (queue_status IN ('pending_auto','applied','rejected_gate','halted'))
    )""",
    """CREATE TABLE IF NOT EXISTS evolution_apply_log (
        apply_log_id    BIGSERIAL PRIMARY KEY,
        queue_id        BIGINT NOT NULL REFERENCES promotion_queue(queue_id),
        applied_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        before_status   VARCHAR(16),
        after_status    VARCHAR(16),
        production_set_delta JSONB,
        evidence_json   JSONB NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS evolution_kill_switch (
        switch_id       SMALLINT PRIMARY KEY,
        scope           VARCHAR(8) NOT NULL DEFAULT 'global' UNIQUE,
        state           VARCHAR(16) NOT NULL DEFAULT 'clear',
        set_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        set_by          VARCHAR(128) NOT NULL,
        reason          TEXT,
        CHECK (state IN ('clear','halt')),
        CHECK (scope IN ('tw','lai','raw','global'))
    )""",
    # PME 生產特徵登錄（philosophy 域 allowlist）。≠可交易／確立級；≠predict 熱路徑自動納入。
    """CREATE TABLE IF NOT EXISTS evolution_production_feature_set (
        feature           VARCHAR(255) PRIMARY KEY,
        set_status        VARCHAR(16) NOT NULL DEFAULT 'active',
        registered_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
        source_run_id     BIGINT NOT NULL REFERENCES evolution_run(run_id),
        source_queue_id   BIGINT NOT NULL REFERENCES promotion_queue(queue_id),
        apply_log_id      BIGINT NOT NULL REFERENCES evolution_apply_log(apply_log_id),
        principle_id      INTEGER REFERENCES philosophy_principle(principle_id),
        last_action       VARCHAR(16) NOT NULL,
        CHECK (set_status IN ('active','removed')),
        CHECK (last_action IN ('promote','demote','freeze'))
    )""",
]

# ALTER 補 FK（promotion_queue.apply_log_id → evolution_apply_log；建表後冪等）
EVOLUTION_DDL_POST = [
    """DO $$ BEGIN
        ALTER TABLE promotion_queue
          ADD CONSTRAINT promotion_queue_apply_log_fk
          FOREIGN KEY (apply_log_id) REFERENCES evolution_apply_log(apply_log_id);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$""",
    """COMMENT ON TABLE evolution_production_feature_set IS
        'PME 生產特徵登錄（philosophy 域）；≠可交易/確立級；≠predict 熱路徑自動納入；SSOT=APPLY promote/demote'""",
    # V2 Phase 2.4(C6):kill-switch 由單列升為逐 scope 一列(tw/lai/raw/global);TRI-HALT=global halt。
    # 既有 DB 冪等升級:去 switch_id=1 CHECK → 加 scope 欄 → 補 UNIQUE/CHECK → 種 4 列。
    """DO $$ BEGIN
        ALTER TABLE evolution_kill_switch DROP CONSTRAINT IF EXISTS evolution_kill_switch_switch_id_check;
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name='evolution_kill_switch' AND column_name='scope') THEN
            ALTER TABLE evolution_kill_switch ADD COLUMN scope VARCHAR(8) NOT NULL DEFAULT 'global';
        END IF;
        BEGIN
            ALTER TABLE evolution_kill_switch ADD CONSTRAINT evolution_kill_switch_scope_uq UNIQUE (scope);
        EXCEPTION WHEN duplicate_object OR duplicate_table THEN NULL;
        END;
        BEGIN
            ALTER TABLE evolution_kill_switch ADD CONSTRAINT evolution_kill_switch_scope_check
                CHECK (scope IN ('tw','lai','raw','global'));
        EXCEPTION WHEN duplicate_object THEN NULL;
        END;
    END $$""",
    """INSERT INTO evolution_kill_switch (switch_id, scope, state, set_by, reason)
        VALUES (2,'tw','clear','migrate_philosophy_evolution_ddl','V2 Phase 2.4 scope seed'),
               (3,'lai','clear','migrate_philosophy_evolution_ddl','V2 Phase 2.4 scope seed'),
               (4,'raw','clear','migrate_philosophy_evolution_ddl','V2 Phase 2.4 scope seed')
        ON CONFLICT (scope) DO NOTHING""",
]


def classify_coverage(
    feature: str,
    *,
    in_feature_values: bool,
    retired: bool = False,
) -> str:
    """假說特徵 → coverage_class（互斥）。dividend 族一律 blocked_div（G-DIV-1）。"""
    if feature in BLOCKED_DIV_FEATURES or feature.startswith("dividend_"):
        return "blocked_div"
    if retired:
        return "retired"
    if in_feature_values:
        return "mapped"
    return "missing"


def normalize_kill_state(state: str | None, *, env_halt: bool = False) -> str:
    """DB／呼叫端狀態；環境變數 AUGUR_EVOLUTION_KILL_SWITCH=halt 可強制 halt（OR）。"""
    s = (state or KILL_CLEAR).strip().lower()
    if env_halt or s == KILL_HALT:
        return KILL_HALT
    if s == KILL_CLEAR:
        return KILL_CLEAR
    raise ValueError(f"illegal kill-switch state: {state!r}")


KILL_SCOPES = ("tw", "lai", "raw", "global")


def effective_kill_state(states, *, env_halt: bool = False) -> str:
    """逐 scope 多列口徑(V2 Phase 2.4/C6):任一相干 scope 為 halt ⇒ halt(OR 語意;fail-safe)。
    呼叫端以 `WHERE scope IN (<自軸>,'global')` 取列後把 state 序列餵入;空序列=表無列=clear(建表前相容)。"""
    eff = KILL_CLEAR
    for s in states:
        if normalize_kill_state(s) == KILL_HALT:
            eff = KILL_HALT
    return normalize_kill_state(eff, env_halt=env_halt)


def gate_verdict(result: Mapping[str, Any]) -> str:
    """單一閘結果 → PASS|FAIL|SKIP（大小寫不敏感；缺省 FAIL）。"""
    v = str(result.get("verdict", "FAIL")).upper()
    if v in ("PASS", "FAIL", "SKIP"):
        return v
    return "FAIL"


def all_gates_green(gate_json: Mapping[str, Any]) -> bool:
    """AUTO-B：七閘皆 PASS 才可 APPLY；任一 FAIL／SKIP／缺閘 → False。"""
    for gid in GATE_IDS:
        if gid not in gate_json:
            return False
        if gate_verdict(gate_json[gid]) != "PASS":
            return False
    return True


def build_gate_json(
    *,
    g_iso: Mapping[str, Any],
    g_map: Mapping[str, Any],
    g_prom: Mapping[str, Any],
    g_econ: Mapping[str, Any],
    g_attest: Mapping[str, Any],
    g_kill: Mapping[str, Any],
    g_noexec: Mapping[str, Any],
) -> dict[str, Any]:
    """組裝 gate_json（鍵＝GATE_IDS）。"""
    out = {
        "G-ISO": dict(g_iso),
        "G-MAP": dict(g_map),
        "G-PROM": dict(g_prom),
        "G-ECON": dict(g_econ),
        "G-ATTEST": dict(g_attest),
        "G-KILL": dict(g_kill),
        "G-NOEXEC": dict(g_noexec),
    }
    for gid in GATE_IDS:
        out[gid].setdefault("verdict", "FAIL")
    return out


def decide_queue_status(
    gate_json: Mapping[str, Any],
    kill_state: str,
) -> str:
    """寫入 promotion_queue.queue_status 前決策。"""
    if normalize_kill_state(kill_state) == KILL_HALT:
        return "halted"
    if all_gates_green(gate_json):
        return "pending_auto"
    return "rejected_gate"


def may_apply(
    *,
    kill_state: str,
    gate_json: Mapping[str, Any],
    queue_status: str,
) -> tuple[bool, str]:
    """APPLY 前最終裁決；(ok, reason)。halt → 拒絕；閘未綠 → 拒絕。"""
    if normalize_kill_state(kill_state) == KILL_HALT:
        return False, "G-KILL halt: refuse APPLY"
    if queue_status != "pending_auto":
        return False, f"queue_status={queue_status} (not pending_auto)"
    if not all_gates_green(gate_json):
        return False, "gates not all PASS"
    return True, "ok"


def scan_noexec_text(text: str) -> list[str]:
    """G-NOEXEC：掃描源碼字面；回違規清單（空＝PASS）。"""
    hits = []
    for lit in NOEXEC_FORBIDDEN_LITERALS:
        if lit in text:
            hits.append(lit)
    return hits


def attest_complete(
    *,
    code_sha: str | None,
    since_date: str | None,
    horizon_h: int | None,
    config_json: Mapping[str, Any] | None,
) -> bool:
    """G-ATTEST：run 可重現欄位齊備。"""
    if not code_sha or not str(code_sha).strip():
        return False
    if not since_date:
        return False
    if horizon_h is None or int(horizon_h) <= 0:
        return False
    if not config_json:
        return False
    return True


def map_action_from_evidence(
    *,
    coverage_class: str,
    g_prom_pass: bool,
    g_econ_pass: bool,
) -> str:
    """建議 action：blocked／缺特徵 → freeze；兩閘 PASS → promote；否則 demote。"""
    if coverage_class in ("blocked_div", "missing", "retired"):
        return "freeze"
    if g_prom_pass and g_econ_pass:
        return "promote"
    return "demote"


def evaluate_g_prom_from_evidence(
    evidence: Mapping[str, Any],
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """由本地重算證據裁決 G-PROM（純函式；IO 在呼叫端）。

    evidence 鍵（缺則該關 SKIP／FAIL）：
      n_panels, mean_ic, hac_t, seed_deltas (list[float]|None),
      skipped_reason (str|None) — 整閘無法算時誠實 SKIP
    """
    gcfg = dict((cfg or DEFAULT_GATE_CONFIG).get("gates", {}).get("G-PROM", {}))
    min_abs = float(gcfg.get("min_abs_hac_t", 2.0))
    min_panels = int(gcfg.get("min_panels", 10))
    min_seeds = int(gcfg.get("min_seeds", 3))
    min_delta = float(gcfg.get("min_delta_ic", 0.0))

    skip = evidence.get("skipped_reason")
    if skip:
        return {
            "verdict": "SKIP",
            "reason": str(skip),
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }

    n_panels = evidence.get("n_panels")
    mean_ic = evidence.get("mean_ic")
    hac_t = evidence.get("hac_t")
    seed_deltas = evidence.get("seed_deltas")

    # —— M-1 符號一致性(V2-CTRL/GATE-raise 拍板 2026-07-27;audits/V2-PHASE4-RUBRIC-H2) ——
    # mean_ic 為「已乘 direction」口徑(caller :242) → mean_ic<0 ⟺ 實測符號與假說方向相反。
    # FAIL_SIGN 非 SKIP(終態負判、禁 I8 回填 validated);樣本須先足額(n_panels≥min)才裁——
    # 病灶實證:volume_gini_60d dir=+1 而 mean_ic=-0.0539/hac_t=-3.966(顯著反向)仍過閘,
    # 因舊碼只判 |hac_t| 取絕對值、mean_ic 只驗存在。
    expected_dir = evidence.get("expected_direction")
    if (n_panels is not None and int(n_panels) >= min_panels
            and mean_ic is not None and float(mean_ic) < 0):
        sig = (hac_t is not None and abs(float(hac_t)) >= min_abs)
        return {
            "verdict": "FAIL_SIGN",
            "reason": (f"sign mismatch: direction-adjusted mean_ic={float(mean_ic):+.4f} < 0"
                       + (f"; significant |hac_t|={abs(float(hac_t)):.3f}≥{min_abs}(在假說方向上穩定答錯)"
                          if sig else "")),
            "expected_direction": int(expected_dir) if expected_dir is not None else None,
            "observed_sign": (-int(expected_dir)) if expected_dir else None,
            "sign_significant": sig,
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }

    checks: dict[str, Any] = {
        "asof_ic": False,
        "hac_t": False,
        "multi_seed_delta": False,
    }
    notes: list[str] = []

    if n_panels is None or int(n_panels) < min_panels or mean_ic is None:
        notes.append(f"asof_ic insufficient (n_panels={n_panels}, mean_ic={mean_ic})")
    else:
        checks["asof_ic"] = True

    if hac_t is None:
        notes.append("hac_t missing")
    elif abs(float(hac_t)) < min_abs:
        notes.append(f"|hac_t|={abs(float(hac_t)):.3f} < {min_abs}")
    else:
        checks["hac_t"] = True

    if seed_deltas is None:
        notes.append("multi_seed_delta not computed")
        return {
            "verdict": "SKIP",
            "reason": "G-PROM triad partial: multi-seed not run/unavailable",
            "checks": checks,
            "notes": notes,
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }
    deltas = [float(x) for x in seed_deltas if x is not None]
    if len(deltas) < min_seeds:
        notes.append(f"seed_deltas n={len(deltas)} < min_seeds={min_seeds}")
        return {
            "verdict": "SKIP",
            "reason": "G-PROM triad partial: insufficient seeds",
            "checks": checks,
            "notes": notes,
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }
    mean_delta = sum(deltas) / len(deltas)
    if mean_delta > min_delta and all(d > min_delta for d in deltas):
        checks["multi_seed_delta"] = True
    else:
        notes.append(f"seed Δ mean={mean_delta:+.4f} not stable > {min_delta}")

    all_ok = all(checks.values())
    return {
        "verdict": "PASS" if all_ok else "FAIL",
        "reason": "triad ok" if all_ok else "; ".join(notes) or "triad fail",
        "checks": checks,
        "notes": notes,
        "mean_delta_ic": mean_delta,
        "evidence": dict(evidence),
        "thresholds": gcfg,
    }


def evaluate_g_econ_from_evidence(
    evidence: Mapping[str, Any],
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """由本地 #14 回測證據裁決 G-ECON（純函式）。

    evidence 鍵：port_sharpe, bench_sharpe, max_dd, n_periods, skipped_reason
    """
    gcfg = dict((cfg or DEFAULT_GATE_CONFIG).get("gates", {}).get("G-ECON", {}))
    dd_floor = float(gcfg.get("max_dd_floor", -0.60))

    skip = evidence.get("skipped_reason")
    if skip:
        return {
            "verdict": "SKIP",
            "reason": str(skip),
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }

    port_s = evidence.get("port_sharpe")
    bench_s = evidence.get("bench_sharpe")
    max_dd = evidence.get("max_dd")
    n_periods = evidence.get("n_periods")

    if port_s is None or bench_s is None or n_periods is None or int(n_periods) < 3:
        return {
            "verdict": "SKIP",
            "reason": "econ backtest insufficient (need sharpes + n_periods≥3)",
            "evidence": dict(evidence),
            "thresholds": gcfg,
        }

    beat = float(port_s) > float(bench_s)
    dd_ok = max_dd is not None and float(max_dd) >= dd_floor
    ok = beat and dd_ok
    reason_parts = []
    if not beat:
        reason_parts.append(f"port_sharpe={float(port_s):+.3f} ≤ bench={float(bench_s):+.3f}")
    if not dd_ok:
        reason_parts.append(f"max_dd={max_dd} < floor={dd_floor}")
    return {
        "verdict": "PASS" if ok else "FAIL",
        "reason": "econ ok" if ok else "; ".join(reason_parts),
        "beat_benchmark": beat,
        "dd_ok": dd_ok,
        "evidence": dict(evidence),
        "thresholds": gcfg,
    }


def status_after_apply(action: str, before: str | None) -> str:
    """philosophy_principle.status 轉移（B 引擎寫入）。"""
    if action == "promote":
        return "validated"
    if action == "demote":
        return "rejected"
    if action == "freeze":
        return "untested" if not before else before
    return before or "untested"


def prodset_status_for_action(action: str) -> str | None:
    """APPLY 對生產登錄表之落點：promote→active；demote→removed；freeze→不寫（None）。"""
    a = (action or "").strip().lower()
    if a == "promote":
        return PRODSET_ACTIVE
    if a == "demote":
        return PRODSET_REMOVED
    return None


def production_set_delta(
    feature: str,
    action: str,
    *,
    set_status: str | None = None,
) -> dict[str, Any]:
    """evolution_apply_log.production_set_delta 可溯源 payload（含表名；非僅 feature/action）。"""
    st = set_status if set_status is not None else prodset_status_for_action(action)
    out: dict[str, Any] = {
        "feature": feature,
        "action": action,
        "table": PRODSET_TABLE,
    }
    if st is not None:
        out["set_status"] = st
    else:
        out["set_status"] = None
        out["note"] = "freeze_no_prodset_write"
    return out


def classify_status_alignment(
    *,
    status: str,
    has_map_validated: bool,
    has_promote_applied: bool,
    has_pending_auto: bool = False,
    has_rejected_gate: bool = False,
    coverage_classes: frozenset[str] | set[str] | tuple[str, ...] | None = None,
) -> str:
    """A7 對齊分類（純函式）。

    抽樣規則：
      1) status=validated 僅當存在 promote APPLY 證據 → aligned_validated；否則 fake_validated
      2) promote applied 但 status 未翻 → apply_lag（可 sync；非假綠來源）
      3) untested ∧ map validated_* ∧ rejected_gate → map_evidence_gate_rejected（誠實；禁翻 validated）
      4) untested ∧ pending_auto → map_evidence_pending_auto（等 APPLY，禁預先翻）
      5) untested ∧ 無 validated_* → aligned_untested_clean
      6) 僅 blocked_div／missing／retired → coverage_blocked_or_missing（禁冒充已對齊）
    """
    st = (status or "untested").strip().lower()
    cov = frozenset(coverage_classes or ())
    only_non_mapped = bool(cov) and cov <= frozenset({"blocked_div", "missing", "retired"})

    if has_promote_applied:
        if st == "validated":
            return "aligned_validated"
        return "apply_lag"

    if st == "validated":
        return "fake_validated"

    if only_non_mapped and not has_map_validated:
        return "coverage_blocked_or_missing"

    if not has_map_validated:
        return "aligned_untested_clean"

    # 以下：untested（或非 validated）且有 map validated_*，無 promote apply
    if has_pending_auto:
        return "map_evidence_pending_auto"
    if has_rejected_gate:
        return "map_evidence_gate_rejected"
    return "map_evidence_no_queue"


def sync_action_for_alignment(alignment: str) -> str | None:
    """機械收斂動作；禁對 gate_rejected／pending／no_queue／blocked 翻 validated。"""
    if alignment == "apply_lag":
        return "set_validated"
    if alignment == "fake_validated":
        return "rollback_untested"
    return None


def is_a7_violation(alignment: str) -> bool:
    """A7 違規＝假綠或 APPLY 後 status 未收斂；≠ raw untested∩validated_*。"""
    return alignment in A7_VIOLATION_CLASSES


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("GATE_IDS 七閘", len(GATE_IDS) == 7)
    chk("DDL 六表", len(EVOLUTION_DDL) == 6 and all("CREATE TABLE" in d for d in EVOLUTION_DDL))
    chk("DDL 含 prodset", any(PRODSET_TABLE in d for d in EVOLUTION_DDL))
    chk("prodset promote→active", prodset_status_for_action("promote") == PRODSET_ACTIVE)
    chk("prodset demote→removed", prodset_status_for_action("demote") == PRODSET_REMOVED)
    chk("prodset freeze→None", prodset_status_for_action("freeze") is None)
    delta = production_set_delta("f1", "promote")
    chk("delta has table+active", delta.get("table") == PRODSET_TABLE and delta.get("set_status") == PRODSET_ACTIVE)
    chk("classify dividend → blocked_div", classify_coverage("dividend_yield", in_feature_values=True) == "blocked_div")
    chk("classify mapped", classify_coverage("pe_ratio", in_feature_values=True) == "mapped")
    chk("classify missing", classify_coverage("roe", in_feature_values=False) == "missing")
    chk("classify retired", classify_coverage("x", in_feature_values=False, retired=True) == "retired")
    chk("kill normalize halt", normalize_kill_state("halt") == KILL_HALT)
    chk("kill env forces halt", normalize_kill_state("clear", env_halt=True) == KILL_HALT)

    green = build_gate_json(
        g_iso={"verdict": "PASS"},
        g_map={"verdict": "PASS"},
        g_prom={"verdict": "PASS"},
        g_econ={"verdict": "PASS"},
        g_attest={"verdict": "PASS"},
        g_kill={"verdict": "PASS", "state": "clear"},
        g_noexec={"verdict": "PASS"},
    )
    chk("all_gates_green", all_gates_green(green))
    chk("decide pending_auto", decide_queue_status(green, KILL_CLEAR) == "pending_auto")
    chk("decide halted on kill", decide_queue_status(green, KILL_HALT) == "halted")

    skip_econ = dict(green)
    skip_econ["G-ECON"] = {"verdict": "SKIP", "reason": "FZ-keep"}
    chk("SKIP ≠ PASS", not all_gates_green(skip_econ))
    chk("decide rejected on SKIP", decide_queue_status(skip_econ, KILL_CLEAR) == "rejected_gate")

    ok_apply, reason = may_apply(kill_state=KILL_HALT, gate_json=green, queue_status="pending_auto")
    chk("A5 halt refuses APPLY", (not ok_apply) and "halt" in reason.lower())
    ok_apply2, _ = may_apply(kill_state=KILL_CLEAR, gate_json=green, queue_status="pending_auto")
    chk("clear+green may APPLY", ok_apply2)

    chk("noexec clean", scan_noexec_text("update philosophy_principle set status") == [])
    hit_tok = "".join(("place", "_order"))
    chk("noexec hit", hit_tok in scan_noexec_text(f"call {hit_tok}()"))
    chk("attest complete", attest_complete(code_sha="abc", since_date="2021-01-01", horizon_h=60, config_json=DEFAULT_GATE_CONFIG))
    chk("attest incomplete", not attest_complete(code_sha="", since_date="2021-01-01", horizon_h=60, config_json={}))
    chk("status promote→validated", status_after_apply("promote", "untested") == "validated")
    # A7 分類規則（禁假綠）
    chk(
        "A7 aligned_validated",
        classify_status_alignment(
            status="validated", has_map_validated=True, has_promote_applied=True
        )
        == "aligned_validated",
    )
    chk(
        "A7 fake_validated",
        classify_status_alignment(
            status="validated", has_map_validated=True, has_promote_applied=False
        )
        == "fake_validated",
    )
    chk(
        "A7 gate_rejected ≠ flip",
        classify_status_alignment(
            status="untested",
            has_map_validated=True,
            has_promote_applied=False,
            has_rejected_gate=True,
        )
        == "map_evidence_gate_rejected",
    )
    chk(
        "A7 sync rejects gate_rejected",
        sync_action_for_alignment("map_evidence_gate_rejected") is None,
    )
    chk(
        "A7 sync apply_lag→set_validated",
        sync_action_for_alignment("apply_lag") == "set_validated",
    )
    chk(
        "A7 sync fake→rollback",
        sync_action_for_alignment("fake_validated") == "rollback_untested",
    )
    chk(
        "A7 pending ≠ violation sync",
        sync_action_for_alignment("map_evidence_pending_auto") is None
        and not is_a7_violation("map_evidence_pending_auto"),
    )
    chk("A7 violation fake", is_a7_violation("fake_validated"))
    chk("A7 gate_rejected not violation", not is_a7_violation("map_evidence_gate_rejected"))
    chk(
        "A7 blocked_or_missing",
        classify_status_alignment(
            status="untested",
            has_map_validated=False,
            has_promote_applied=False,
            coverage_classes={"blocked_div", "missing"},
        )
        == "coverage_blocked_or_missing",
    )
    chk("map_action freeze blocked", map_action_from_evidence(coverage_class="blocked_div", g_prom_pass=True, g_econ_pass=True) == "freeze")
    chk("DEFAULT_GATE_CONFIG fz_keep", DEFAULT_GATE_CONFIG.get("fz_keep") is True)
    chk("soul wording pending flag", DEFAULT_GATE_CONFIG.get("soul_wording_pending") is False)
    chk("G-PROM thresholds pinned", DEFAULT_GATE_CONFIG["gates"]["G-PROM"]["min_abs_hac_t"] == 2.0)

    prom_pass = evaluate_g_prom_from_evidence(
        {"n_panels": 20, "mean_ic": 0.05, "hac_t": 2.5, "seed_deltas": [0.01, 0.02, 0.015]}
    )
    chk("G-PROM PASS triad", prom_pass["verdict"] == "PASS")
    prom_fail = evaluate_g_prom_from_evidence(
        {"n_panels": 20, "mean_ic": 0.05, "hac_t": 1.2, "seed_deltas": [0.01, 0.02, 0.015]}
    )
    chk("G-PROM FAIL low hac", prom_fail["verdict"] == "FAIL")
    prom_skip = evaluate_g_prom_from_evidence(
        {"n_panels": 20, "mean_ic": 0.05, "hac_t": 2.5, "seed_deltas": None}
    )
    chk("G-PROM SKIP no seeds", prom_skip["verdict"] == "SKIP")
    econ_pass = evaluate_g_econ_from_evidence(
        {"port_sharpe": 1.2, "bench_sharpe": 0.9, "max_dd": -0.2, "n_periods": 10}
    )
    chk("G-ECON PASS", econ_pass["verdict"] == "PASS")
    econ_fail = evaluate_g_econ_from_evidence(
        {"port_sharpe": 0.5, "bench_sharpe": 0.9, "max_dd": -0.2, "n_periods": 10}
    )
    chk("G-ECON FAIL vs bench", econ_fail["verdict"] == "FAIL")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("公開入口: classify_coverage / build_gate_json / all_gates_green / may_apply /")
    print("          decide_queue_status / normalize_kill_state / scan_noexec_text / attest_complete /")
    print("          evaluate_g_prom_from_evidence / evaluate_g_econ_from_evidence /")
    print("          classify_status_alignment / sync_action_for_alignment / is_a7_violation /")
    print("          prodset_status_for_action / production_set_delta")
    print("(自測: python -m augur.philosophy.evolution --selftest；免 DB 免 API)")
