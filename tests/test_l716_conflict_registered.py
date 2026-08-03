"""🎯 L7.16 衝突登錄之條件式紅燈：live 仍為單一角色 ⇒ RULING-2026-042 與 AL-2026-046 必須在且已簽。

守原則 #15（機制壞了不得安靜變綠燈）、#9（憲法層宣稱可溯源）。
恢復 2026-07-31 刪除 test_db_tombstone_controlled_erasure 後「superuser 零自動紅燈」之缺口：
非斷言角色分離（前提已消滅），而是斷言「既成事實必須保持已登錄＋已簽核」。
若日後恢復角色分離（出現獨立 app 角色），條件不成立、本鎖自然靜默——屬設計而非假綠。
先驗紅：RULING 檔不在 working tree 時本檔必 FAIL（施作留痕 audits/L716-RULING-042-REDRUN-*.md）。
M-G11（2026-08-03）：舊鎖只驗「檔在＋字樣」——簽核欄 `[x]`→`[ ]` 仍綠；本檔加 `steward_approval_checked`。
"""
import re
from pathlib import Path

import psycopg2
import pytest

REPO = Path(__file__).resolve().parent.parent
RULING = REPO / "constitution" / "RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md"
AMENDMENT_LOG = REPO / "constitution" / "AMENDMENT-LOG.md"

# 簽核欄區塊內「准：」勾選列（blockquote bullet）。[x]=已簽；[ ]=未生效（r4 G6／M-G11）。
_STEWARD_APPROVAL = re.compile(
    r"簽核欄（Steward）[\s\S]*?-\s*\[([ xX])\]\s*\*\*准",
    re.MULTILINE,
)


def is_single_role_state(role_names: set[str]) -> bool:
    """純函式：非系統角色扣除 postgres 後只剩 augur ⇒ 單一角色狀態（L7.16 前提消滅）。"""
    app_like = {r for r in role_names if r != "postgres"}
    return app_like == {"augur"}


def steward_approval_checked(text: str) -> bool:
    """純函式：裁決正文之 Steward 簽核欄「准：」列是否為 `[x]`（已生效）。"""
    m = _STEWARD_APPROVAL.search(text)
    return bool(m) and m.group(1).lower() == "x"


def _uncheck_steward_approval(text: str) -> str:
    """把真產生器正文之簽核勾選改回空白（先驗紅原料；不動磁碟）。"""
    out, n = re.subn(
        r"(簽核欄（Steward）[\s\S]*?-\s*)\[([xX])\](\s*\*\*准)",
        r"\1[ ]\3",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n != 1:
        raise AssertionError(f"無法在記憶體複本把簽核欄 [x]→[ ]（命中 {n}）")
    return out


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


def test_steward_approval_checked_red_green():
    """M-G11 先驗紅：真檔正文已簽＝綠；同文把 [x] 改 [ ] 必須變紅（禁字面假 fixture）。"""
    live = RULING.read_text(encoding="utf-8")
    assert steward_approval_checked(live), "live RULING-2026-042 簽核欄應為已勾選"
    unsigned = _uncheck_steward_approval(live)
    assert not steward_approval_checked(unsigned), (
        "簽核欄改回 [ ] 後 steward_approval_checked 仍綠＝鎖失效（r4 G6）")
    assert "L7.16" in unsigned and "AL-2026-046" in unsigned  # 舊四條字樣仍在＝隔離「只鎖檔在」假綠


def test_l716_conflict_must_stay_registered():
    """live 單一角色 ⇒ 042 裁決檔與 AL-2026-046 皆必須在且簽核欄已勾（缺任一即紅）。"""
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
    assert steward_approval_checked(text), (
        "RULING-2026-042 簽核欄未勾選——裁決未生效卻登錄存在＝假綠（M-G11／r4 G6）")
