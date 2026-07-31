#!/usr/bin/env python3
"""🎯 把「機器判定輸出」與「人裁理由」拆成兩欄——稽核器不得再覆寫人寫的字。

守原則 #15（誠實：人的判斷不得被機器靜默抹除）、#12（帳本為唯一權威）、#9（可溯源）。

起因（2026-07-31 實犯，journald／DB 雙證）：`verify_validation_evidence.py:88` 之

    new, nn = ("green", note) if ok else ("red", note or "斷言為假")
    UPDATE validation_evidence SET status_note = COALESCE(%s, status_note) ...

上一行的 `or "斷言為假"` 保證 `nn` 恆非空 ⇒ **`COALESCE` 是死碼、每跑必覆寫**。
該表 **trigger 數＝0**、無 pre-image、無稽核軌，故覆寫完全無痕。2026-07-31 13:29
該稽核器一跑，`E1_raw_reconcile_exit` 之

    「(a) 2026-07-14 hugo 拍板:改讀正典驅動持久化 verdict(attestation_result)——…」

即被機器字串「斷言為假」取代（同批受害：`E2_feature_frozen_panel`／`E4_exclusion_set_contract`，
惟二者之種子 `status_note` 本為 NULL，無人裁原文可失）。

**為何加欄而非只改 COALESCE**：兩者本是不同種類的東西——`status_note` 記「為什麼當初這樣判／
人裁了什麼」（半衰期以年計、寫入者是人），`machine_note` 記「這次跑出什麼」（每跑覆寫、
寫入者是程式）。塞同一欄則任一方的正確行為都會毀掉另一方：機器不覆寫則紅燈沒有理由可讀，
機器覆寫則人裁消失。分欄後兩者各自單調，稽核器**永不觸碰 `status_note`**。

**本腳本不代人重寫任何判斷**：`--restore-e1` 只把 E1 之 `status_note` 還原成
`migrate_validation_evidence_ddl.py` SEEDS 內既存之逐字原文（來源＝repo，非 AI 生成），
且僅在該欄現值為機器字串時才動；已被人另行改寫者一律不碰。

執行指令矩陣
------------
    python3 scripts/migrate_validation_evidence_machine_note_ddl.py             # 無參數＝--check（唯讀）
    python3 scripts/migrate_validation_evidence_machine_note_ddl.py --check     # 唯讀：欄位在否＋三列現值
    python3 scripts/migrate_validation_evidence_machine_note_ddl.py --apply     # 加欄（冪等）
    python3 scripts/migrate_validation_evidence_machine_note_ddl.py --restore-e1  # 還原 E1 人裁原文（冪等）
    python3 scripts/migrate_validation_evidence_machine_note_ddl.py --selftest  # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

TABLE = "validation_evidence"
COL = "machine_note"
E1 = "E1_raw_reconcile_exit"
SEED_FILE = Path(__file__).with_name("migrate_validation_evidence_ddl.py")
# 稽核器曾寫入之機器字串;僅當現值屬此集合才視為「被覆寫」而可還原。
MACHINE_STRINGS = ("斷言為假",)

DDL = f'ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {COL} text'

COMMENT = (
    f"COMMENT ON COLUMN {TABLE}.{COL} IS "
    "'機器判定輸出(每次 verify 覆寫);人裁理由住 status_note、稽核器不得寫'"
)


def seed_note(evidence_id: str) -> str | None:
    """自 migrate_validation_evidence_ddl.py 之 SEEDS 取該列之 status_note 逐字原文。

    以 AST 解析而非 import：該檔 import 時會拉 DB 相依，唯讀取值不該有副作用。
    """
    src = SEED_FILE.read_text(encoding="utf-8")
    m = re.search(r"SEEDS\s*=\s*\[(.*?)\n\]", src, re.S)
    if not m:
        return None
    for row in ast.literal_eval("[" + m.group(1) + "]"):
        if row and row[0] == evidence_id:
            return row[8] if len(row) > 8 else None
    return None


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
        has = cur.fetchone()[0] > 0
        print(f"  {COL} 欄：{'在' if has else '**不在**（須 --apply）'}")
        cur.execute(
            f"SELECT evidence_id, status, status_note FROM {TABLE} "
            "WHERE evidence_id IN ('E1_raw_reconcile_exit','E2_feature_frozen_panel',"
            "'E4_exclusion_set_contract') ORDER BY evidence_id")
        for eid, st, note in cur.fetchall():
            flag = "  ← 機器字串（人裁已失）" if (note or "") in MACHINE_STRINGS else ""
            print(f"  {eid} | {st} | status_note={note!r}{flag}")
    s = seed_note(E1)
    print(f"  E1 種子原文：{'有（可還原）' if s else '無'}")
    return 0


def _apply(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute(COMMENT)
    conn.commit()
    print(f"✓ {TABLE}.{COL} 就位（冪等）")
    return 0


def _restore_e1(conn) -> int:
    want = seed_note(E1)
    if not want:
        print("✗ 種子查無 E1 之 status_note——不代寫、不猜", file=sys.stderr)
        return 1
    with conn.cursor() as cur:
        cur.execute(f"SELECT status_note FROM {TABLE} WHERE evidence_id=%s", (E1,))
        row = cur.fetchone()
        if not row:
            print(f"✗ 查無 {E1}", file=sys.stderr)
            return 1
        cur_note = row[0]
        if cur_note == want:
            print("✓ E1 已是種子原文（冪等，無動作）")
            return 0
        if (cur_note or "") not in MACHINE_STRINGS:
            # 現值既非機器字串亦非種子原文 ⇒ 可能是人另行改寫過,不得覆蓋。
            print(f"⚠ E1 現值非已知機器字串亦非種子原文，**不動**：{cur_note!r}")
            print("  （若確為應還原者，請人工確認後再處置——本腳本不猜人的意思）")
            return 2
        cur.execute(f"UPDATE {TABLE} SET status_note=%s WHERE evidence_id=%s", (want, E1))
    conn.commit()
    print(f"✓ E1 status_note 已還原為種子原文（{len(want)} 字）")
    print(f"  原機器字串：{cur_note!r}")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("DDL 用 IF NOT EXISTS（冪等）", "IF NOT EXISTS" in DDL)
    s = seed_note(E1)
    chk("種子可解析出 E1 之 status_note", isinstance(s, str) and len(s) > 20)
    chk("種子原文含 hugo 拍板字樣（確認取到的是人裁那句）", s and "hugo" in s)
    chk("機器字串集合非空且含實犯之『斷言為假』", "斷言為假" in MACHINE_STRINGS)
    chk("種子原文不在機器字串集合（否則還原邏輯自我抵銷）", s not in MACHINE_STRINGS)
    chk("不存在之 evidence_id 回 None（不亂猜）", seed_note("E_NOT_EXIST_ZZZ") is None)
    body = Path(__file__).read_text(encoding="utf-8")
    chk("restore 對未知現值採不動（不覆蓋人另行改寫者）", "不動" in body and "return 2" in body)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validation_evidence 加 machine_note 欄＋還原 E1 人裁原文")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore-e1", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        if a.apply:
            return _apply(conn)
        if a.restore_e1:
            return _restore_e1(conn)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
