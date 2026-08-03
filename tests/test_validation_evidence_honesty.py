"""🎯 綠燈帳本誠實化之回歸鎖（M-P12(a)(b)）——**「從未被驗過」不得以 green 身分計入**。

守原則 #15（假綠零容忍：分子裡不得有沒被量過的東西）、#9（可溯源：last_verified_at 是
「被碰過」的唯一痕跡）、#35（先驗紅：把守護行為改回壞版本必須讓本檔轉紅）。

背景（2026-08-03 現查）：`E3_promotion_funnel`／`E4_gm_promotion_gap` 兩列 manual green、
`last_verified_at IS NULL`、`valid_until=2026-10-09`（未來）⇒ 效期降轉永遠不觸發、
重驗迴圈對 manual 型 `continue` ⇒ **這兩列自種下起就沒有任何機制會碰它們**，卻一路計入
green 16/20 的分子。本檔鎖的是「降轉真的會發生」與「降轉不代人補簽」。

**射程誠實**：本檔對**真表**跑（同一組 CHECK 約束、同一組 trigger），全程在一段
ROLLBACK 的交易內，不留任何持久寫入。DB 連不上時 skip——故本檔在無 DB 環境為
fail-open；行為層之紅綠唯在有 DB 時成立。純函式層之鎖另在
`python scripts/verify_validation_evidence.py --selftest`。

先驗紅（`test_mutation_no_sweep`）：把 `demote_never_verified` 換成恆空樁（＝M-P12(a)
之前的行為）時，green+NULL 之列**真的**會原封不動留在 green ⇒ 上面那些綠燈是這道降轉
擋下來的，不是資料庫或別處恆真。

執行：pytest tests/test_validation_evidence_honesty.py -v
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import verify_validation_evidence as vve  # noqa: E402

# 形狀逐字取自 live 之 E3_promotion_funnel／E4_gm_promotion_gap（manual／green／lva NULL／
# valid_until 為未來）——不是「我以為的形狀」，是這兩列真正的樣子。
NEVER = "ZZ_TEST_never_verified"
VERIFIED = "ZZ_TEST_already_verified"
_INS = (
    "INSERT INTO validation_evidence (evidence_id, chain_link, claim, check_type, "
    "source_ref, status, last_verified_at, valid_until) "
    "VALUES (%s,'promotion','回歸鎖用合成列（測試交易內、ROLLBACK 不落地）','manual',"
    "'tests/test_validation_evidence_honesty.py',%s,%s, now() + interval '1 year')")


@pytest.fixture
def cur():
    """真表、真約束；整段交易最後一律 ROLLBACK（不留任何持久寫入）。"""
    try:
        from augur.core import db
        cm = db.connect()
        conn = cm.__enter__()
    except Exception as e:                      # noqa: BLE001
        pytest.skip(f"無 DB 連線，行為層鎖跳過：{type(e).__name__}")
    c = conn.cursor()
    try:
        c.execute(_INS, (NEVER, "green", None))
        c.execute(_INS, (VERIFIED, "green", None))
        c.execute("UPDATE validation_evidence SET last_verified_at=now() WHERE evidence_id=%s",
                  (VERIFIED,))
        yield c
    finally:
        conn.rollback()
        cm.__exit__(None, None, None)


def _status(c, eid):
    c.execute("SELECT status, last_verified_at FROM validation_evidence WHERE evidence_id=%s", (eid,))
    return c.fetchone()


def test_never_verified_green_is_demoted(cur):
    """green + last_verified_at IS NULL ⇒ 必須降為 unverified，且被回報出來。"""
    assert _status(cur, NEVER) == ("green", None), "前置：合成列須以 green/NULL 起手"
    demoted = vve.demote_never_verified(cur)
    assert NEVER in demoted
    assert _status(cur, NEVER)[0] == "unverified"


def test_demotion_does_not_forge_verification(cur):
    """降轉**不得**順手補 last_verified_at——那等於程式代替人宣稱「我驗過了」。"""
    vve.demote_never_verified(cur)
    assert _status(cur, NEVER)[1] is None


def test_verified_green_survives(cur):
    """有 last_verified_at 的 green 不受影響（降轉不是無差別掃綠）。"""
    vve.demote_never_verified(cur)
    assert _status(cur, VERIFIED)[0] == "green"


def test_only_id_scopes_the_sweep(cur):
    """--id 時只動那一列。"""
    cur.execute("UPDATE validation_evidence SET status='green', last_verified_at=NULL "
                "WHERE evidence_id=%s", (VERIFIED,))
    demoted = vve.demote_never_verified(cur, only_id=NEVER)
    assert demoted == [NEVER]
    assert _status(cur, VERIFIED)[0] == "green"


def test_mutation_no_sweep(cur, monkeypatch):
    """先驗紅：把降轉換成恆空樁（＝M-P12(a) 之前）⇒ green+NULL 原封不動留在 green。

    這證明上面三個綠燈量的是這道降轉，不是資料庫約束或別處早已把它處理掉。
    """
    monkeypatch.setattr(vve, "demote_never_verified", lambda *a, **k: [])
    assert vve.demote_never_verified(cur) == []
    assert _status(cur, NEVER) == ("green", None)


def test_live_ledger_has_no_never_verified_green():
    """驗收①之常設回歸鎖：live 帳本不得再出現 green + last_verified_at IS NULL。

    （讀已提交狀態，不在測試交易內；改動前此查為 2＝先驗紅之出處。）
    """
    try:
        from augur.core import db
        with db.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT evidence_id FROM validation_evidence "
                      "WHERE status='green' AND last_verified_at IS NULL ORDER BY 1")
            offenders = [r[0] for r in c.fetchall()]
    except Exception as e:                      # noqa: BLE001
        pytest.skip(f"無 DB 連線：{type(e).__name__}")
    assert offenders == [], f"未驗卻計入 green：{offenders}"


def test_red_line_never_fabricates_a_date():
    """red_since 欄未就位時，週報一行不得生出任何日期（寧可說不知道）。"""
    line = vve.format_red_line(4, None, None, has_red_since=False)
    assert "未知" in line
    assert re.search(r"\d{4}-\d{2}-\d{2}", line) is None, line
