"""🎯 L7.16 衝突登錄之條件式紅燈：live 仍為單一角色 ⇒ RULING-2026-042 與 AL-2026-046 必須在。

守原則 #15（機制壞了不得安靜變綠燈）、#9（憲法層宣稱可溯源）。
恢復 2026-07-31 刪除 test_db_tombstone_controlled_erasure 後「superuser 零自動紅燈」之缺口：
非斷言角色分離（前提已消滅），而是斷言「既成事實必須保持已登錄」。
若日後恢復角色分離（出現獨立 app 角色），條件不成立、本鎖自然靜默——屬設計而非假綠。
先驗紅：RULING 檔不在 working tree 時本檔必 FAIL（施作留痕 audits/L716-RULING-042-REDRUN-*.md）。
"""
from pathlib import Path

import psycopg2
import pytest

REPO = Path(__file__).resolve().parent.parent
RULING = REPO / "constitution" / "RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md"
AMENDMENT_LOG = REPO / "constitution" / "AMENDMENT-LOG.md"


def is_single_role_state(role_names: set[str]) -> bool:
    """純函式：非系統角色扣除 postgres 後只剩 augur ⇒ 單一角色狀態（L7.16 前提消滅）。"""
    app_like = {r for r in role_names if r != "postgres"}
    return app_like == {"augur"}


def _live_roles() -> set[str]:
    from augur.core.config import DB_PARAMS  # noqa: PLC0415

    with psycopg2.connect(**DB_PARAMS) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT rolname FROM pg_roles WHERE rolname NOT LIKE 'pg\\_%'")
        return {r[0] for r in cur.fetchall()}


def test_single_role_predicate_red_green():
    """純函式餵已知輸入：整併後真形（紅綠雙向）。"""
    assert is_single_role_state({"augur", "postgres"})
    assert not is_single_role_state({"augur", "augur_predict", "postgres"})
    assert not is_single_role_state({"augur", "augur_owner", "postgres"})


def test_l716_conflict_must_stay_registered():
    """live 單一角色 ⇒ 042 裁決檔與 AL-2026-046 皆必須在（缺任一即紅）。"""
    try:
        roles = _live_roles()
    except Exception as exc:  # DB 不可達＝誠實 skip，非假 pass
        pytest.skip(f"DB unreachable: {exc}")
    if not is_single_role_state(roles):
        pytest.skip(f"role separation restored ({sorted(roles)}); L7.16 premise back, lock dormant")
    assert RULING.exists(), (
        "live 為單一角色但 RULING-2026-042 不在——治權登錄被移除或尚未落地，"
        "衝突回到零登錄狀態（r3 §七）")
    text = RULING.read_text(encoding="utf-8")
    assert "L7.16" in text and "AL-2026-046" in text
    assert "## AL-2026-046" in AMENDMENT_LOG.read_text(encoding="utf-8")
