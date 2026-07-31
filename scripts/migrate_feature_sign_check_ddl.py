#!/usr/bin/env python3
"""🎯 符號一致性檢查之落帳表——把「通過了嗎」從 markdown 搬進機器查得到的地方。

守原則 #9（可溯源：判定須有 (a)(b)(c) 來源）、#12（帳本為唯一權威）、#15（無證據≠通過）。

起因（2026-07-31 實證）：SUNSET (b) 逐字要求「每一新成員**通過符號一致性檢查**」，
而該尺 `scripts/verify_sign_consistency.py`（07-28 建）**存在但未接線**：
  · `GATE_IDS` 七閘無 `G-SIGN`；`promotion_queue` 中 `gate_json ? 'G-SIGN'` 命中 **0** 列；
  · **全庫無任何 sign 結果表**——唯一「通過」紀錄寫在 `audits/PRODSET-LENDING-PROMOTION-20260729.md`；
  · `inst_cumflow_position_120d`（07-24 進 prodset，早於該尺存在）**零符號證據**。
⇒ 「新成員是否通過符號檢查」無法機械查證。Steward 2026-07-31 裁「**要回頭補**」
（射程 all_active：所有現役成員皆須有紀錄，不因進場早於該尺而豁免）。

**本表只存機器算得之證據**，無人簽欄——不觸「不代打人簽」。verdict 三值皆為
`judge_sign` 之機械輸出；`UNJUDGEABLE`（無方向或方向衝突）**不等於 PASS**（fail-closed）。

**鎖安全**：`CREATE TABLE` 建新表只取系統目錄之 RowExclusiveLock，**不碰任何既有使用者表**，
故與進行中之長交易（如 TWEVO I3 持 `feature_values`／`evolution_iteration_ledger` 之
AccessShare）無衝突。惟仍以 `lock_timeout` 保底：搶不到即放棄，不排隊——
排隊中之 AccessExclusive 會堵住其後一切查詢，那才是 #30 鎖風暴之成因。

執行指令矩陣
------------
    python3 scripts/migrate_feature_sign_check_ddl.py            # 無參數＝--check（唯讀）
    python3 scripts/migrate_feature_sign_check_ddl.py --check    # 唯讀：表在否＋現有列數＋現役覆蓋
    python3 scripts/migrate_feature_sign_check_ddl.py --apply    # 建表（冪等；帶 lock_timeout）
    python3 scripts/migrate_feature_sign_check_ddl.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

TABLE = "feature_sign_check"
LOCK_TIMEOUT = "3s"

DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
  check_id         BIGSERIAL PRIMARY KEY,
  feature          TEXT NOT NULL,
  h                INTEGER NOT NULL,
  direction        SMALLINT,
  direction_source TEXT NOT NULL,
  point_ic         DOUBLE PRECISION,
  boot_ics         JSONB,
  n_panels         INTEGER,
  panels_first     DATE,
  panels_last      DATE,
  verdict          TEXT NOT NULL CHECK (verdict IN ('PASS','FAIL','UNJUDGEABLE')),
  code_sha         VARCHAR(64),
  checked_at       TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

IDX = f"CREATE INDEX IF NOT EXISTS ix_fsc_feature ON {TABLE}(feature, checked_at DESC)"

COMMENTS = [
    f"COMMENT ON TABLE {TABLE} IS "
    "'符號一致性檢查(SIGN-B)之落帳;判準住 verify_sign_consistency.judge_sign。"
    "本表只存機器算得之證據、無人簽欄。查無列＝未通過(fail-closed),不得讀為通過'",
    f"COMMENT ON COLUMN {TABLE}.verdict IS "
    "'PASS|FAIL|UNJUDGEABLE;UNJUDGEABLE(無方向/方向衝突)**不等於 PASS**'",
    f"COMMENT ON COLUMN {TABLE}.direction_source IS "
    "'方向之出處:factor_direction_ruling 優先於 principle_factor_map'",
]


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{TABLE}",))
        has = cur.fetchone()[0]
        print(f"  表 {TABLE}：{'在' if has else '**不在**（須 --apply）'}")
        if has:
            cur.execute(f"SELECT count(*) FROM {TABLE}")
            print(f"  現有列數：{cur.fetchone()[0]}")
        cur.execute("SELECT feature FROM evolution_production_feature_set "
                    "WHERE set_status='active' ORDER BY feature")
        active = [r[0] for r in cur.fetchall()]
        print(f"  現役成員（射程 all_active，Steward 2026-07-31 裁）：{active or '（無）'}")
        if has and active:
            cur.execute(f"""SELECT DISTINCT ON (feature) feature, verdict, checked_at
                             FROM {TABLE} WHERE feature = ANY(%s)
                            ORDER BY feature, checked_at DESC""", (active,))
            got = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        else:
            got = {}
        for f in active:
            v = got.get(f)
            print(f"    {f}：{v[0] + ' @' + str(v[1])[:19] if v else '**無紀錄 ⇒ 未通過(fail-closed)**'}")
    return 0


def _apply(conn) -> int:
    with conn.cursor() as cur:
        # 搶不到鎖即放棄、不排隊（排隊中之 AccessExclusive 會堵住後續一切查詢＝#30 鎖風暴）。
        cur.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")
        cur.execute(DDL)
        cur.execute(IDX)
        for c in COMMENTS:
            cur.execute(c)
    conn.commit()
    print(f"✓ {TABLE} 就位（冪等；lock_timeout={LOCK_TIMEOUT}）")
    print("  下一步：verify_sign_consistency.py 需加 --record 才會寫入本表（另案）。")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("DDL 冪等（IF NOT EXISTS）", "IF NOT EXISTS" in DDL and "IF NOT EXISTS" in IDX)
    chk("verdict 有 CHECK 約束（三值以外寫不進來）",
        "CHECK (verdict IN ('PASS','FAIL','UNJUDGEABLE'))" in DDL)
    chk("UNJUDGEABLE 為合法值但非 PASS（fail-closed 之載體）",
        "UNJUDGEABLE" in DDL and "'UNJUDGEABLE'" in DDL)
    chk("無人簽欄（不觸『不代打人簽』）",
        not any(k in DDL for k in ("approved_by", "signed_by", "promoted_by", "decided_by")))
    body = open(__file__, encoding="utf-8").read()
    chk("apply 前設 lock_timeout（搶不到即放棄、不排隊＝#30 鎖風暴之防）",
        "lock_timeout" in body.split("def _apply")[1].split("def _selftest")[0])
    chk("有 feature+時間索引（取最新一筆之查詢會用到）", "ix_fsc_feature" in IDX and "checked_at DESC" in IDX)
    chk("留有 provenance 欄（direction_source／code_sha／n_panels）",
        all(c in DDL for c in ("direction_source", "code_sha", "n_panels")))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=f"{TABLE} 落帳表（符號一致性檢查之機器可查證據）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())
