"""augur 哲學↔市場進化狀態機 — PME 閉環純函式（閘評估／kill-switch／覆蓋分類）。

🎯 這支在做什麼（白話）：把「假說→市場重驗→有界自動晉升」的機械閘與緊急停做成
   可回歸的 library（零 IO `--selftest`）。不進預測 runtime；不生成原則；不含下單。
   編排腳本（coverage／run／apply／kill-switch）呼叫本模組；G-PROM／G-ECON 證據由
   呼叫端餵入——凍結期間可誠實 SKIP（≠ PASS），禁 FinMind／FRED。

守 #1 #14 #15 #18；計畫 SSOT＝reports/augur_philosophy_market_evolution_loop_plan_20260724.md。

執行指令矩陣（本檔=library #18；免 DB 免 API）:
  python -m augur.philosophy.evolution              # 印用途+公開入口（唯讀）
  python -m augur.philosophy.evolution --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from typing import Any, Mapping

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
DEFAULT_GATE_CONFIG: dict[str, Any] = {
    "policy": "PME-AUTO-B",
    "kill_required": True,
    "fz_keep": True,
    "gates": {
        "G-PROM": {"require_hac_t": True, "min_seeds": 3},
        "G-ECON": {"require_sharpe_vs_benchmark": True},
    },
    "soul_wording_pending": True,  # [I] 靈魂措辭另案；不擅改 [N]
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
        switch_id       SMALLINT PRIMARY KEY DEFAULT 1 CHECK (switch_id = 1),
        state           VARCHAR(16) NOT NULL DEFAULT 'clear',
        set_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        set_by          VARCHAR(128) NOT NULL,
        reason          TEXT,
        CHECK (state IN ('clear','halt'))
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


def status_after_apply(action: str, before: str | None) -> str:
    """philosophy_principle.status 轉移（B 引擎寫入）。"""
    if action == "promote":
        return "validated"
    if action == "demote":
        return "rejected"
    if action == "freeze":
        return "untested" if not before else before
    return before or "untested"


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("GATE_IDS 七閘", len(GATE_IDS) == 7)
    chk("DDL 五表", len(EVOLUTION_DDL) == 5 and all("CREATE TABLE" in d for d in EVOLUTION_DDL))
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
    chk("map_action freeze blocked", map_action_from_evidence(coverage_class="blocked_div", g_prom_pass=True, g_econ_pass=True) == "freeze")
    chk("DEFAULT_GATE_CONFIG fz_keep", DEFAULT_GATE_CONFIG.get("fz_keep") is True)
    chk("soul wording pending flag", DEFAULT_GATE_CONFIG.get("soul_wording_pending") is True)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("公開入口: classify_coverage / build_gate_json / all_gates_green / may_apply /")
    print("          decide_queue_status / normalize_kill_state / scan_noexec_text / attest_complete")
    print("(自測: python -m augur.philosophy.evolution --selftest；免 DB 免 API)")
