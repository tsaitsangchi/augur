#!/usr/bin/env python3
"""🎯 建 headline 宣稱帳 `alpha_headline_anchor`——治權簽核錨終於有機器可查的家。

守原則 #6（--apply 才動 DB；冪等可重跑）、#10（每列 source_ref 可溯源）、#12（honesty guard
函式復用 migrate_honesty_guards_ddl 之單一住所，不自造第二實作）、#15（claimed_at 不可考=NULL
不補造時戳；簽核值與本機機算帳分 claim_kind、不混桶）、#29a/d。

起因（登錄冊 E2，2026-08-01）：headline 治權認定 1.1321（hugo 簽）與本機快照 1.1302 皆無
DB 帳——trial_ledger 停在 07-13（1.1972 舊世代）、revalidation_baseline 凍在 07-09；
「確立級數字」與帳本分家。本表＝append-only 宣稱帳（修訂=新列+supersedes_id，永不覆寫）；
「登錄時刻 recorded_at」與「宣稱所指時點 claim_asof」與「原始宣稱行為 claimed_at」三時點分立。
**本支不做 INSERT**——簽錨列唯 hugo TTY 親跑（never-type-human-signature；範本在 E2 呈案 §3.4）。

執行指令矩陣
------------
    python3 scripts/migrate_alpha_headline_anchor_ddl.py            # 無參數=--check（唯讀）
    python3 scripts/migrate_alpha_headline_anchor_ddl.py --check    # 唯讀:表/兩 trigger/列分佈
    python3 scripts/migrate_alpha_headline_anchor_ddl.py --apply    # 建表+掛 guard（冪等;3c DDL 窗、dump 期間禁跑 #30）
    python3 scripts/migrate_alpha_headline_anchor_ddl.py --selftest # 紅綠自測（免 DB;含壞 DDL 驗紅）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

DDL = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS alpha_headline_anchor (
  anchor_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  anchor_label  text        NOT NULL,
  claim_kind    text        NOT NULL CHECK (claim_kind IN
                  ('governance_signed','local_snapshot','historical_reference')),
  metric_name   text        NOT NULL DEFAULT 'net_sharpe',
  metric_value  double precision NOT NULL,
  recipe        text        NOT NULL,
  scale_note    text        NOT NULL,
  n_basis       text        NOT NULL,
  claim_asof    date        NOT NULL,
  claimed_at    timestamptz,
  recorded_at   timestamptz NOT NULL DEFAULT now(),
  source_ref    text        NOT NULL,
  signed_by     text,
  machine       text,
  supersedes_id bigint REFERENCES alpha_headline_anchor(anchor_id),
  note          text,
  CONSTRAINT chk_aha_signed CHECK (claim_kind <> 'governance_signed' OR signed_by IS NOT NULL)
);

DROP TRIGGER IF EXISTS trg_alpha_headline_anchor_honesty_row ON alpha_headline_anchor;
CREATE TRIGGER trg_alpha_headline_anchor_honesty_row
  BEFORE UPDATE OR DELETE ON alpha_headline_anchor
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_alpha_headline_anchor_honesty_trunc ON alpha_headline_anchor;
CREATE TRIGGER trg_alpha_headline_anchor_honesty_trunc
  BEFORE TRUNCATE ON alpha_headline_anchor
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

COMMENT ON TABLE alpha_headline_anchor IS
  'headline 宣稱帳(append-only 家譜;登錄冊 E2 2026-08-01):治權簽核錨與本機快照分 claim_kind 落帳;claim_asof(宣稱所指)/claimed_at(原始宣稱,不可考=NULL 不補造)/recorded_at(登錄)三時點分立;修訂=新列+supersedes_id,不覆寫;governance_signed 列唯 hugo TTY 親簽';
"""


def ddl_invariants(ddl: str) -> list[str]:
    """DDL 載體之不變式檢核。**純函式**——回傳被違反者清單（空=全守）。
    本表 DDL 字串即被逐字執行之行為載體，故對載體驗形＝對行為驗形（#35 型3 疑慮不適用於
    「字串就是 payload」情形）；selftest 以壞變體驗紅。"""
    bad = []
    if "GENERATED ALWAYS AS IDENTITY PRIMARY KEY" not in ddl:
        bad.append("identity_pk")
    if ddl.count("'governance_signed','local_snapshot','historical_reference'") != 1:
        bad.append("claim_kind_three_values")
    if "chk_aha_signed" not in ddl or "signed_by IS NOT NULL" not in ddl:
        bad.append("signed_check")
    if ddl.count("DROP TRIGGER IF EXISTS") != 2 or ddl.count("honesty_ledger_guard()") != 2:
        bad.append("two_guard_triggers")
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    import re
    m = re.search(r"^\s*claimed_at\s+timestamptz(.*)$", ddl, re.MULTILINE)
    if not m or "NOT NULL" in m.group(1):
        bad.append("claimed_at_nullable")
    if "recorded_at   timestamptz NOT NULL DEFAULT now()" not in ddl:
        bad.append("recorded_at_db_now")
    if "INSERT INTO" in ddl:
        bad.append("no_insert_in_ddl")
    return bad


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.alpha_headline_anchor')")
        exists = bool(cur.fetchone()[0])
        print(f"  {'✓' if exists else '·'} table alpha_headline_anchor {'在' if exists else '不在（未 --apply）'}")
        if not exists:
            return 0
        cur.execute("SELECT count(*) FROM pg_trigger "
                    "WHERE tgrelid='alpha_headline_anchor'::regclass AND NOT tgisinternal")
        ntrg = cur.fetchone()[0]
        print(f"  {'✓' if ntrg == 2 else '✗'} guard trigger {ntrg}/2")
        cur.execute("SELECT claim_kind, count(*) FROM alpha_headline_anchor GROUP BY 1 ORDER BY 1")
        rows = cur.fetchall()
        print("  列分佈:" + ("（空——簽錨待 hugo TTY 親跑）" if not rows
                           else "; ".join(f"{k} {n}" for k, n in rows)))
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_proc WHERE proname='honesty_ledger_guard'")
        if cur.fetchone()[0] == 0:
            print("✗ honesty_ledger_guard 函式不存在——先跑 migrate_honesty_guards_ddl.py（#12 不自造第二住所）")
            return 1
    with db.transaction(conn) as cur:
        cur.execute(DDL)
    print("✓ DDL 冪等完成")
    return _check(conn)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("驗紅:拿掉 CHECK 三值 → claim_kind 不變式報違",
        "claim_kind_three_values" in ddl_invariants(
            DDL.replace("'governance_signed','local_snapshot','historical_reference'", "'x'")))
    chk("驗紅:拿掉簽核 CHECK → signed_check 報違",
        "signed_check" in ddl_invariants(DDL.replace("chk_aha_signed", "chk_gone")))
    chk("驗紅:少一支 trigger → two_guard_triggers 報違",
        "two_guard_triggers" in ddl_invariants(
            DDL.replace("DROP TRIGGER IF EXISTS trg_alpha_headline_anchor_honesty_trunc "
                        "ON alpha_headline_anchor;", "", 1)))
    chk("驗紅:recorded_at 改可指定 → 報違",
        "recorded_at_db_now" in ddl_invariants(
            DDL.replace("recorded_at   timestamptz NOT NULL DEFAULT now()",
                        "recorded_at   timestamptz")))
    chk("驗紅:DDL 夾帶 INSERT → 報違（簽錨非腳本職權）",
        "no_insert_in_ddl" in ddl_invariants(DDL + "\nINSERT INTO alpha_headline_anchor VALUES (1);"))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="alpha_headline_anchor DDL（E2;簽錨=hugo TTY 另跑）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.apply):
        print(__doc__.split("執行指令矩陣")[1].split("-----\n")[-1])
    from augur.core import db
    with db.connect() as conn:
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
