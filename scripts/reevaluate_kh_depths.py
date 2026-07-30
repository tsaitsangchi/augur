#!/usr/bin/env python3
"""🎯 以現行（已修）評估器重評 KH 准入深度——把「以無效證據取得之 depth」降回真實值。

守原則 #15（誠實回報：判死留檔、不靜默）、#1（不以無效證據支撐宣稱）。

起因（2026-07-30，hugo 拍板「重評 145,949 件」）：
  獨立核驗證明 145,949 件之 `admit_depth=9` 係以**零變異之 KH8 橡皮章**取得
  （母體選擇效應致 terminal／embed／kh4_ok 恆 1.0、score 底線 0.72、必落 high band）。
  修正後之 KH8 對**全母體**回 fail（`kh8_non_discriminating`），故該 depth 不成立。

**重評之口徑（誠實界定）**：
  以**現行評估器邏輯**重新裁決每一 item 之 KH8／KH9 verdict——
  鑑別力檢定為**母體級**（全域一致），故逐 item 只需讀其既存 weight 之 band
  即可得新 verdict；**不重算輸入、不寫新 weight 列**（避免以 145,949 列新帳膨脹
  該表，且輸入未變、重算必得同值）。
  `depth 0–7` 之既有判定**不重驗、亦不撤銷**——本次僅收斂 8 以上之無效層級。

**不做**：不刪任何列；不動 `knowhow_evidence_weight`／`knowhow_synthesis_run`
  （其為已發生之評估事實、屬史料）；不改 gate 組態。

執行指令矩陣
------------
    python3 scripts/reevaluate_kh_depths.py                 # 無參數＝--check（唯讀）
    python3 scripts/reevaluate_kh_depths.py --check          # 唯讀：現況分佈＋將變更之筆數
    python3 scripts/reevaluate_kh_depths.py --apply          # 實作（批次 5000、可續跑、逐列留帳）
    python3 scripts/reevaluate_kh_depths.py --apply --limit 100   # 小批試作
    python3 scripts/reevaluate_kh_depths.py --selftest       # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

import _bootstrap  # noqa: F401

BATCH = 5000
LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS knowhow_depth_reevaluation (
    reeval_id   BIGSERIAL PRIMARY KEY,
    run_id      TEXT NOT NULL,
    item_id     BIGINT NOT NULL,
    depth_before SMALLINT NOT NULL,
    depth_after  SMALLINT NOT NULL,
    reason       TEXT NOT NULL,
    evidence     JSONB NOT NULL,
    at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS kh_reeval_run_idx ON knowhow_depth_reevaluation (run_id);
CREATE INDEX IF NOT EXISTS kh_reeval_item_idx ON knowhow_depth_reevaluation (item_id);
"""


def new_depth_for(band: str | None, disc_ok: bool, before: int) -> tuple[int, str]:
    """以現行評估器邏輯裁決新 depth（純函式，可自測）。

    KH8 pass ⇔ band ∈ {high,medium,low} **且** 母體具鑑別力；否則 fail。
    KH8 fail ⇒ 該 item 不得停在 8 以上 ⇒ 收斂至 7（0–7 之既有判定不重驗、不撤銷）。
    """
    if before < 8:
        return before, "before<8：不在本次射程"
    if disc_ok and band in ("high", "medium", "low"):
        return before, "KH8 pass（母體具鑑別力且 band 合格）：depth 保留"
    if not disc_ok:
        return 7, "KH8 fail：母體無鑑別力（kh8_non_discriminating）→ 收斂至 7"
    return 7, f"KH8 fail：band={band} 不合格 → 收斂至 7"


def run(conn, *, apply: bool, limit: int | None) -> int:
    from augur.knowledge import evidence as kh8

    cur = conn.cursor()
    cur.execute(
        """SELECT coalesce(admit_depth,0) d, count(*) FROM knowhow_auto_admit_state
            WHERE target_kind='item' GROUP BY 1 ORDER BY 1"""
    )
    before_dist = cur.fetchall()
    print(f"重評前 admit_depth 分佈：{before_dist}")

    disc = kh8.population_discriminates(cur)
    print(f"KH8 母體鑑別力：ok={disc['ok']}｜{disc['note'][:120]}")

    cur.execute(
        """SELECT count(*) FROM knowhow_auto_admit_state
            WHERE target_kind='item' AND coalesce(admit_depth,0) >= 8"""
    )
    n_target = int(cur.fetchone()[0])
    print(f"射程（depth≥8）：{n_target:,} 件")

    if not apply:
        cur.execute(
            """SELECT s.target_id, s.admit_depth, w.confidence_band
                 FROM knowhow_auto_admit_state s
                 LEFT JOIN LATERAL (SELECT confidence_band FROM knowhow_evidence_weight
                                     WHERE item_id = s.target_id::bigint
                                     ORDER BY weight_id DESC LIMIT 1) w ON true
                WHERE s.target_kind='item' AND coalesce(s.admit_depth,0) >= 8 LIMIT 5"""
        )
        print("抽樣裁決（前 5）：")
        for tid, d, band in cur.fetchall():
            nd, why = new_depth_for(band, disc["ok"], int(d))
            print(f"  item={tid} {d}→{nd}｜band={band}｜{why}")
        would = 0 if disc["ok"] else n_target
        print(f"預計變更：{would:,} 件（{'無變更：母體具鑑別力' if disc['ok'] else 'depth 9/8 → 7'}）")
        print("（唯讀；跑 --apply 實作）")
        return 0

    cur.execute(LEDGER_DDL)
    conn.commit()
    cur.execute("SELECT to_char(now(),'YYYYMMDDHH24MISS')")
    run_id = f"kh-reeval-{cur.fetchone()[0]}"
    print(f"run_id={run_id}｜批次={BATCH}｜可續跑（已處理者不再入射程）")

    total = 0
    while True:
        cur.execute(
            f"""SELECT s.target_id, s.admit_depth, w.confidence_band
                  FROM knowhow_auto_admit_state s
                  LEFT JOIN LATERAL (SELECT confidence_band FROM knowhow_evidence_weight
                                      WHERE item_id = s.target_id::bigint
                                      ORDER BY weight_id DESC LIMIT 1) w ON true
                 WHERE s.target_kind='item' AND coalesce(s.admit_depth,0) >= 8
                 ORDER BY s.target_id::bigint
                 LIMIT {min(BATCH, limit - total) if limit else BATCH}"""
        )
        rows = cur.fetchall()
        if not rows:
            break
        changed = 0
        for tid, d, band in rows:
            nd, why = new_depth_for(band, disc["ok"], int(d))
            if nd == int(d):
                continue
            cur.execute(
                "UPDATE knowhow_auto_admit_state SET admit_depth=%s, updated_at=now() "
                "WHERE target_kind='item' AND target_id=%s",
                (nd, str(tid)),
            )
            cur.execute(
                """INSERT INTO knowhow_depth_reevaluation
                     (run_id, item_id, depth_before, depth_after, reason, evidence)
                   VALUES (%s,%s,%s,%s,%s,%s::jsonb)""",
                (run_id, int(tid), int(d), nd, why,
                 '{"band": %s, "disc_ok": %s, "gate": "kh8_non_discriminating"}'
                 % (f'"{band}"' if band else "null", str(disc["ok"]).lower())),
            )
            changed += 1
        conn.commit()
        total += changed
        print(f"  已重評 {total:,} 件…")
        if changed == 0 or (limit and total >= limit):
            break

    cur.execute(
        """SELECT coalesce(admit_depth,0) d, count(*) FROM knowhow_auto_admit_state
            WHERE target_kind='item' GROUP BY 1 ORDER BY 1"""
    )
    print(f"重評後 admit_depth 分佈：{cur.fetchall()}")
    print(f"共重評 {total:,} 件；帳本＝knowhow_depth_reevaluation（run_id={run_id}）")
    return 0


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    d, why = new_depth_for("high", False, 9)
    chk("無鑑別力 + depth9 → 7", d == 7 and "kh8_non_discriminating" in why)
    d, _ = new_depth_for("high", True, 9)
    chk("有鑑別力 + band high + depth9 → 保留 9", d == 9)
    d, _ = new_depth_for("absent", True, 9)
    chk("有鑑別力 + band absent → 7", d == 7)
    d, why = new_depth_for(None, False, 3)
    chk("depth3 不在射程（不動）", d == 3 and "不在本次射程" in why)
    d, _ = new_depth_for(None, False, 8)
    chk("depth8 亦收斂至 7", d == 7)
    chk("LEDGER 為 append-only（無 DELETE 語句）", "DELETE" not in LEDGER_DDL)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="以現行評估器重評 KH 准入深度（可續跑、逐列留帳）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db

    with db.connect() as conn:
        return run(conn, apply=a.apply, limit=a.limit)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("--- 無參數＝--check（唯讀）---")
    sys.exit(main())
