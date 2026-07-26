"""🎯 三 ledger 同構之機械斷言(V2 Phase 5 驗收:「三張 CREATE TABLE 由同一常數清單生成」)。
C2 裁決的核心=同構是契約不是巧合;本測試把它固化為回歸鎖——任何人改單一軸的骨架欄位即紅。
執行:pytest tests/test_evolution_ledger_ddl.py -q
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from augur.audit.evolution_ledger_ddl import AXES, LEDGER_COMMON, full_ddl, ledger_ddl  # noqa: E402


def test_three_ledgers_generated_from_same_constant():
    """三表逐字含共同骨架每一欄(同一清單生成=同構的機械定義)。"""
    for axis in ("raw", "tw", "lai"):
        ddl = ledger_ddl(axis)
        for col, decl in LEDGER_COMMON:
            assert f"{col} {decl}" in ddl, f"{axis} 缺共同欄 {col}"


def test_axis_specific_columns_do_not_leak_across():
    """專屬欄不跨軸洩漏(raw 的 tier 不出現在 tw/lai,反之亦然)。"""
    for axis, spec in AXES.items():
        others = [a for a in AXES if a != axis]
        for col, _ in spec["extra"]:
            for o in others:
                if col not in [c for c, _ in AXES[o]["extra"]]:
                    assert not re.search(rf"^\s+{col}\s", ledger_ddl(o), re.M), \
                        f"{axis} 專屬欄 {col} 洩漏進 {o}"


def test_gain_basis_checks_differ_per_axis():
    """I1:判準本體不共用——gain_basis CHECK 三軸互異。"""
    assert len({AXES[a]["gain_basis_check"] for a in AXES}) == 3


def test_full_ddl_contains_all_nine_tables():
    blob = "\n".join(full_ddl())
    for t in ("raw_evolution_iteration_ledger", "evolution_iteration_ledger", "local_ai_iteration_ledger",
              "evolution_hypothesis_hint", "evolution_evidence_run", "raw_table_coverage_snapshot",
              "evolution_deferred_work", "local_model_eval_set_check", "evolution_prereg_gate"):
        assert f"CREATE TABLE IF NOT EXISTS {t}" in blob
