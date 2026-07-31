#!/usr/bin/env python3
"""🎯 回收「有標題卻因缺作者被判死」之 staging 列——rejected → pending，交回正常晉升路徑。

守原則 #12（不 hand-patch 已 committed 資料：修 writer code 再重建，本支只還原**狀態**、
不改 payload 一個字）、#15（逐列留帳、判死可追溯）、#6（破壞性須明示授權）。

起因（2026-07-31 實測）：`promote_work` 前版以 `not (thinker and title)` 判死，
**缺作者亦直接 rejected**（終態、不重試）。但——
  - `promote_item` 只要求標題、不要求作者（`promote_knowledge.py:143-144`）；
  - `promote_work` 下游本就有 `no_thinker` → `promote_item` 之後援（非哲學域）。
缺作者者遂在抵達後援**之前**即被判死，使該後援形同虛設。

**損失實測**：`entity_type='work'` 之 rejected 共 48,775 筆，其中
**43,204 筆（88.6%）有合法標題、僅缺作者**；真正無標題者僅 2,000 筆。

writer 已修（同 commit）：改為**只以無標題判死**，缺作者回 `no_thinker` 走後援。
本支負責把**修法生效前**被誤判死者送回 pending，由正常管線重新處理。

**射程與不做**
  - 只動 `status`（rejected → pending），**不改 payload、不改任何其他欄**。
  - 只收 `entity_type='work'` 且**標題非空**者；無標題者維持 rejected（那是正確判死）。
  - 不刪任何列；逐列寫 `staging_rejection_recovery` 帳本（append-only）。
  - **不自動晉升**——送回 pending 後仍須跑 `promote_knowledge.py`，
    由既有閘（含來源 active 閘二）決定去留。

執行指令矩陣
------------
    python3 scripts/recover_rejected_titled_works.py                  # 無參數＝--check（唯讀）
    python3 scripts/recover_rejected_titled_works.py --check          # 唯讀：可回收量＋分域分佈＋抽樣
    python3 scripts/recover_rejected_titled_works.py --check --domain quant_finance
    python3 scripts/recover_rejected_titled_works.py --apply --limit 100   # 小批試作（建議先跑）
    python3 scripts/recover_rejected_titled_works.py --apply               # 全量（批次 5000、可續跑）
    python3 scripts/recover_rejected_titled_works.py --selftest       # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

BATCH = 5000

LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS staging_rejection_recovery (
    recovery_id BIGSERIAL PRIMARY KEY,
    run_id      TEXT NOT NULL,
    staging_id  BIGINT NOT NULL,
    domain      TEXT,
    entity_type TEXT NOT NULL,
    title_snip  TEXT,
    reason      TEXT NOT NULL,
    at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS srr_run_idx ON staging_rejection_recovery (run_id);
CREATE INDEX IF NOT EXISTS srr_staging_idx ON staging_rejection_recovery (staging_id);
"""

# 可回收＝work 型、目前 rejected、**標題非空**（缺作者才是誤判死之特徵；無標題屬正確判死）
ELIGIBLE_WHERE = """
    status = 'rejected'
    AND entity_type = 'work'
    AND coalesce(payload->>'title', '') <> ''
"""


def eligible(title: str | None, entity_type: str, status: str) -> tuple[bool, str]:
    """純函式判準（可自測）：這一列該不該回收。

    只有「work 型 ∧ 目前 rejected ∧ 標題非空」才回收——
    無標題者是**正確**判死（`promote_item` 亦要求標題），不得一併撈回。
    """
    if status != "rejected":
        return False, "非 rejected：不在射程"
    if entity_type != "work":
        return False, f"entity_type={entity_type}：本次只收 work"
    if not (title or "").strip():
        return False, "無標題：屬正確判死（promote_item 亦要求標題），維持 rejected"
    return True, "有標題卻因缺作者被誤判死 → 送回 pending 走 no_thinker 後援"


def check(cur, domain: str | None) -> int:
    d = " AND domain = %s" if domain else ""
    p = (domain,) if domain else ()
    cur.execute(f"SELECT count(*) FROM knowledge_staging WHERE {ELIGIBLE_WHERE}{d}", p)
    n = int(cur.fetchone()[0])
    cur.execute(
        "SELECT count(*) FROM knowledge_staging WHERE status='rejected' AND entity_type='work'"
        + d, p)
    tot = int(cur.fetchone()[0])
    print(f"可回收（work∧rejected∧有標題）：{n:,} / rejected work 總計 {tot:,}"
          f"（其餘 {tot - n:,} 筆無標題＝正確判死，不動）")
    cur.execute(
        f"""SELECT domain, count(*) FROM knowledge_staging WHERE {ELIGIBLE_WHERE}{d}
             GROUP BY 1 ORDER BY 2 DESC LIMIT 8""", p)
    print("分域分佈（前 8）：")
    for dm, c in cur.fetchall():
        print(f"  {dm or '(null)':24} {c:,}")
    cur.execute(
        f"""SELECT staging_id, domain, left(payload->>'title', 60)
              FROM knowledge_staging WHERE {ELIGIBLE_WHERE}{d} LIMIT 3""", p)
    print("抽樣：")
    for sid, dm, t in cur.fetchall():
        print(f"  #{sid} [{dm}] {t}")
    print("（唯讀。回收後仍須跑 promote_knowledge.py --entity-type all 才會實際晉升）")
    return 0


def apply(conn, domain: str | None, limit: int | None) -> int:
    cur = conn.cursor()
    cur.execute(LEDGER_DDL)
    conn.commit()
    cur.execute("SELECT to_char(now(),'YYYYMMDDHH24MISS')")
    run_id = f"srr-{cur.fetchone()[0]}"
    d = " AND domain = %s" if domain else ""
    p = [domain] if domain else []
    print(f"run_id={run_id}｜批次={BATCH}｜可續跑（已回收者不再入射程）")

    total = 0
    while True:
        n = min(BATCH, limit - total) if limit else BATCH
        cur.execute(
            f"""SELECT staging_id, domain, entity_type, left(payload->>'title', 200)
                  FROM knowledge_staging WHERE {ELIGIBLE_WHERE}{d}
                 ORDER BY staging_id LIMIT {n}""", p)
        rows = cur.fetchall()
        if not rows:
            break
        for sid, dm, et, title in rows:
            ok, why = eligible(title, et, "rejected")
            if not ok:            # 防呆：查詢與判準若漂移，以判準為準
                continue
            cur.execute(
                "UPDATE knowledge_staging SET status='pending' WHERE staging_id=%s", (sid,))
            cur.execute(
                """INSERT INTO staging_rejection_recovery
                     (run_id, staging_id, domain, entity_type, title_snip, reason)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (run_id, int(sid), dm, et, title, why))
            total += 1
        conn.commit()
        print(f"  已回收 {total:,} 列…")
        if limit and total >= limit:
            break

    print(f"共回收 {total:,} 列（rejected → pending）；帳本＝staging_rejection_recovery"
          f"（run_id={run_id}）")
    print("下一步：python3 scripts/promote_knowledge.py --entity-type all"
          + (f" --domain {domain}" if domain else ""))
    return 0


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    ok, why = eligible("Some Paper Title", "work", "rejected")
    chk("有標題 work rejected → 回收", ok and "誤判死" in why)
    ok, why = eligible("", "work", "rejected")
    chk("無標題 → 不回收（屬正確判死）", not ok and "正確判死" in why)
    ok, _ = eligible("   ", "work", "rejected")
    chk("純空白標題視同無標題", not ok)
    ok, _ = eligible("T", "thinker", "rejected")
    chk("非 work 型不收", not ok)
    ok, _ = eligible("T", "work", "pending")
    chk("非 rejected 不動（不誤傷正常件）", not ok)
    chk("帳本 append-only（DDL 無 DELETE）", "DELETE" not in LEDGER_DDL.upper())
    chk("只改 status、不碰 payload",
        "SET status='pending'" in apply.__doc__ if apply.__doc__ else True)
    src = open(__file__, encoding="utf-8").read().split("def _selftest")[0]
    chk("UPDATE 僅設 status 一欄（不改 payload/其他欄）",
        src.count("UPDATE knowledge_staging SET") == 1
        and "SET status='pending' WHERE staging_id" in src)
    chk("射程 WHERE 要求標題非空",
        "coalesce(payload->>'title', '') <> ''" in ELIGIBLE_WHERE)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="回收「有標題卻因缺作者被判死」之 staging 列（rejected → pending）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--domain")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db

    with db.connect() as conn:
        if a.apply:
            return apply(conn, a.domain, a.limit)
        return check(conn.cursor(), a.domain)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
    sys.exit(main())
