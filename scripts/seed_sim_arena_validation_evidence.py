#!/usr/bin/env python3
"""🎯 把 sim／arena 兩軸接上綠燈帳本（M-P13）——現查這兩軸在 `validation_evidence` 上**零覆蓋**。

守原則 #15（有宣稱就要有會亮的紅燈）、#9／#10（斷言可溯源、可機械重驗）、#29b（策展斷言住 DB，
增列＝INSERT 一列零改碼）、#32(b)（能力宣稱不得單臂高分作數）、#35（先驗紅）。

## 為什麼（2026-08-03 現查，psql）

`SELECT count(*) FROM validation_evidence WHERE evidence_id ILIKE '%sim%' OR claim ILIKE '%sim%'`
＝ **0**；arena 亦同。也就是說：sim 軸與 arena 軸不論壞成什麼樣，帳本上都不會有一盞燈變紅。
而同期 `sim_run_link`／`sim_realized_outcome`／`sim_calibration_eval`／
`sim_evolution_iteration_ledger` 全部 0 列、`direction_gate` 0/29 evaluated_pass、
TRI(TAIEX) 落後 PriceAdj **17 個交易日**——**這些狀況一項都沒有被任何燈號記錄。**

## 鑑別力（本檔之通過條件）

四列中**三列在建列當日即為紅**。這是刻意的：新增的斷言若一建就全綠，只證明它們沒有鑑別力
（優化計畫 20260803 第 17 步 驗收④逐字：「全綠即證明斷言沒有鑑別力，視為未通過」）。
`--verify` 把這件事寫成機械條件——全綠時 exit 1。

四列皆帶**非空守衛**（`count(*)>0` ／ `count(*)=0 OR …`），所以「把來源表清空」不會讓燈變綠。

## 明確不做

- 不代驗：種子 `status='unverified'`、`last_verified_at` 由 `verify_validation_evidence.py`
  真跑後才有值（不手填時戳——那正是 M-P12(a) 修掉的病）。
- 不碰人簽欄：本檔不寫 `approved_by`／`decided_by`／`promoted_by`。
- 不改既有列：`ON CONFLICT DO NOTHING`。

執行指令矩陣
------------
    python3 scripts/seed_sim_arena_validation_evidence.py           # 無參數＝--check（唯讀）
    python3 scripts/seed_sim_arena_validation_evidence.py --check   # 唯讀：逐列在否＋此刻試算會是紅是綠
    python3 scripts/seed_sim_arena_validation_evidence.py --run     # 冪等 INSERT（unverified）＋立刻真重驗
    python3 scripts/seed_sim_arena_validation_evidence.py --verify  # 驗收④⑤：四列在、≥1 紅、lva 全非 NULL
    python3 scripts/seed_sim_arena_validation_evidence.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
import verify_validation_evidence as vve

# evidence_id 之 E<n>_ 前綴與 chain_link 一一對應（沿用既有 20 列之慣例）
PREFIX_LINK = {"E1": "raw", "E2": "feature", "E3": "promotion", "E4": "gate", "E5": "train",
               "E6": "oos", "E7": "calibration", "E8": "probability", "E9": "economic",
               "E10": "harness"}

# (evidence_id, chain_link, claim, check_sql, source_ref, status_note)
ROWS = [
    ("E7_sim_candidate_ledger_linked", "calibration",
     "sim 進化候選皆掛在迭代帳本上（sim_evolution_candidate.iteration_uid 非 NULL 且存在於 "
     "sim_evolution_iteration_ledger）；候選表為空亦不算過",
     "SELECT (SELECT count(*) FROM sim_evolution_candidate)>0 AND COALESCE((SELECT bool_and("
     "c.iteration_uid IS NOT NULL AND EXISTS (SELECT 1 FROM sim_evolution_iteration_ledger g "
     "WHERE g.iteration_uid=c.iteration_uid)) FROM sim_evolution_candidate c), false)",
     "reports/augur_optimization_master_plan_20260803.md 第 17 步(M-P13)／第 12 步(M-T1)；"
     "reports/augur_local_ai_market_sim_evolution_plan_20260731.md §3",
     "M-P13(2026-08-03)新列。現查 candidate 1 列(simc_r1_iid_baseline)、其 iteration_uid 為 NULL、"
     "ledger 0 列 ⇒ **建列當日即紅**。這是 M-T1「開列」之可見載體：候選游離在帳本外時，事後無從"
     "證明它屬哪一輪、gain 由誰記。M-T1 落地後應自然轉綠；若以刪候選或關斷言使其轉綠，即為繞過。"),

    ("E7_sim_evidence_chain_present", "calibration",
     "sim 軸一旦有候選，三張證據表（sim_run_link／sim_realized_outcome／sim_calibration_eval）"
     "不得全空——有能力宣稱而零證據載體即紅",
     "SELECT (SELECT count(*) FROM sim_evolution_candidate)=0 OR ("
     "(SELECT count(*) FROM sim_run_link)>0 AND (SELECT count(*) FROM sim_realized_outcome)>0 "
     "AND (SELECT count(*) FROM sim_calibration_eval)>0)",
     "reports/augur_optimization_master_plan_20260803.md 第 17 步(M-P13)；CLAUDE.md #32(b)",
     "M-P13(2026-08-03)新列。現查 candidate 1 列而三表皆 0 列 ⇒ **紅**。守 #32(b)：能力宣稱須有"
     "預凍對照臂之實測分數；證據表全空時，任何「sim 軸有某能力」之敘述都不得作數。"),

    ("E10_arena_market_series_aligned", "harness",
     "arena 每日管線自身兩件產出不得脫節：市場方向特徵面板末點（步驟④）≥ 對局預測末日（步驟⑥）",
     "SELECT COALESCE((SELECT max(panel_date) FROM market_direction_feature) >= "
     "(SELECT max(pred_date) FROM direction_arena_prediction), false)",
     "scripts/run_arena_daily_pipeline.py:84-90（步驟④→⑥）；scripts/run_arena_round.py:96-100,112-115；"
     "reports/augur_optimization_master_plan_20260803.md 第 14 步(M-G10)／第 17 步(M-P13)",
     "M-P13(2026-08-03)新列。現查 market_direction_feature max(panel_date)=2026-07-09 vs "
     "direction_arena_prediction max(pred_date)=2026-07-31 ⇒ **紅**。這是「步驟④每天都跑、每天都"
     "沒產出新列，而步驟⑥照樣天天出預測」的可見載體——管線 rc 全 0、log 不報錯，靜默脫節。"
     "上游根因＝總報酬指數原始表停在 07-09（落後個股價格表 17 個交易日），"
     "run_arena_round.py:112-115 之 market 序列與 :96-100 之 H 軌出手日集合皆讀它。"
     "**射程**：本列只斷言 arena 自家兩件產出對得上，不斷言上游原始表之新鮮度"
     "（那是 E10_dataset_freshness／M-G9 哨兵之事）；亦不涉供應商表名字面（WM.36 止血閘）。"),

    ("E6_arena_replay_clean_teams", "oos",
     "arena 替身賽 replay 全部出自 CLEAN_TEAMS（arena_replay_run.weights_cutoff_ok 全真且表非空）",
     "SELECT count(*)>0 AND bool_and(weights_cutoff_ok) FROM arena_replay_run",
     "scripts/run_arena_replay.py:107-110；reports/augur_optimization_master_plan_20260803.md 第 17 步",
     "M-P13(2026-08-03)新列。⚠ **射程誠實**：weights_cutoff_ok 由 run_arena_replay.py:109 之 "
     "`model in CLEAN_TEAMS` **靜態判定**，不是實測權重截止日——本列只擋「非 clean 隊之 replay "
     "混入」，**不得被讀為『權重截止已驗證』**。現查 8 列全真 ⇒ 綠；空表退化為紅（count(*)>0 "
     "守衛），不讓「把替身賽清空」變成綠燈。"),
]

INSERT_SQL = (
    "INSERT INTO validation_evidence "
    "(evidence_id, chain_link, claim, check_type, check_sql, source_ref, status, status_note) "
    "VALUES (%s,%s,%s,'sql',%s,%s,'unverified',%s) ON CONFLICT (evidence_id) DO NOTHING")


def _preview(cur, sql):
    """唯讀試算此刻是紅是綠（與 verify 用同一支白名單／同一組約束）。"""
    ok, note = vve._run_sql_check(cur, sql)
    return ("green" if ok else "red") if ok is not None else f"BAD({note})"


def _check(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT evidence_id, status, last_verified_at FROM validation_evidence "
                    "WHERE evidence_id = ANY(%s)", ([r[0] for r in ROWS],))
        live = {e: (s, t) for e, s, t in cur.fetchall()}
        for eid, link, _claim, sql, _ref, _note in ROWS:
            here = live.get(eid)
            state = f"在（{here[0]}）" if here else "**不在**（須 --run）"
            print(f"  {eid:<34} [{link:<11}] {state:<18} 此刻試算＝{_preview(cur, sql)}")
    return 0


def _run(conn) -> int:
    with conn.cursor() as cur:
        n = m = 0
        for eid, link, claim, sql, ref, note in ROWS:
            cur.execute(INSERT_SQL, (eid, link, claim, sql, ref, note))
            n += cur.rowcount
            # 斷言本身改寫時之對齊（沿用 migrate_validation_evidence_ddl.py 對 E1 之作法）：
            # ON CONFLICT DO NOTHING 不會更新既有列 ⇒ 改了 check_sql 卻靜默沿用舊斷言。
            # 對齊一律**退回 unverified**（換了尺就得重量），並印出改了什麼、不靜默。
            cur.execute("UPDATE validation_evidence SET check_sql=%s, claim=%s, source_ref=%s, "
                        "status_note=%s, status='unverified', last_verified_at=NULL "
                        "WHERE evidence_id=%s AND check_sql IS DISTINCT FROM %s "
                        "RETURNING evidence_id", (sql, claim, ref, note, eid, sql))
            if cur.fetchall():
                m += 1
                print(f"  ↻ {eid}：check_sql 與種子不同 → 已對齊、status 退 unverified 待重驗")
    conn.commit()
    print(f"✓ 種子冪等落地：新增 {n}/{len(ROWS)} 列、對齊 {m} 列（status=unverified，尚未驗）")
    print("── 立刻真重驗（last_verified_at 由重驗寫入，不手填時戳）：")
    for eid, *_ in ROWS:
        vve.run(only_id=eid)
    return 0


def _verify(conn) -> int:
    ids = [r[0] for r in ROWS]
    with conn.cursor() as cur:
        cur.execute("SELECT evidence_id, status, last_verified_at FROM validation_evidence "
                    "WHERE evidence_id = ANY(%s) ORDER BY 1", (ids,))
        rows = cur.fetchall()
    ok = True
    missing = sorted(set(ids) - {r[0] for r in rows})
    if missing:
        ok = False
        print(f"  ✗ 缺列：{missing}")
    else:
        print(f"  ✓ 四列皆在（{len(rows)}/{len(ids)}）")
    unverified = [e for e, _s, t in rows if t is None]
    if unverified:
        ok = False
        print(f"  ✗ 驗收⑤ last_verified_at 為 NULL：{unverified}（不得重蹈 M-P12(a) 之未驗列）")
    else:
        print("  ✓ 驗收⑤ 每列 last_verified_at 非 NULL")
    reds = [e for e, s, _t in rows if s == "red"]
    if not reds:
        ok = False
        print("  ✗ 驗收④ 四列全非紅 ⇒ 斷言沒有鑑別力，視為未通過")
    else:
        print(f"  ✓ 驗收④ 今日 live 有 {len(reds)} 列為紅：{reds}")
    for e, s, t in rows:
        print(f"     {e:<34} {s:<11} {t:%Y-%m-%d %H:%M}" if t else f"     {e:<34} {s:<11} -")
    return 0 if ok else 1


class _FakeCur:
    """自測用假 cursor：不連 DB，把最後一次 SELECT 之結果設為固定 boolean。"""

    def __init__(self, value=True):
        self.value = value

    def execute(self, sql, args=None):
        pass

    def fetchone(self):
        return (self.value,)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("至少 3 列（驗收④之下限）", len(ROWS) >= 3)
    chk("evidence_id 不重複", len({r[0] for r in ROWS}) == len(ROWS))
    for eid, link, claim, sql, ref, note in ROWS:
        pre = eid.split("_")[0]
        chk(f"{eid}：前綴 {pre} 與 chain_link 對得上", PREFIX_LINK.get(pre) == link)
        # 白名單以 verify 那支的真判準跑（不在本檔另抄一份規則）。
        # 這裡只證「過得了白名單」；SQL 本身跑不跑得出 boolean，由 --check 對 live 試算。
        got, why = vve._run_sql_check(_FakeCur(True), sql)
        chk(f"{eid}：check_sql 過 verify 白名單（單條 SELECT、無分號）", got is True and why is None)
        chk(f"{eid}：claim 與 status_note 皆非空（紅燈要有可讀的理由）", bool(claim) and bool(note))
        chk(f"{eid}：source_ref 指得出檔或報告", bool(ref) and ("/" in ref or "." in ref))
    chk("種子一律 unverified（不代驗、不手填 last_verified_at）",
        "'unverified'" in INSERT_SQL and "last_verified_at" not in INSERT_SQL)
    chk("不寫任何人簽欄", not any(c in INSERT_SQL for c in ("approved_by", "decided_by", "promoted_by")))
    chk("既有列不被覆寫（ON CONFLICT DO NOTHING）", "ON CONFLICT (evidence_id) DO NOTHING" in INSERT_SQL)
    # 白名單真的會擋（否則上面那排綠燈只是恆真）
    bad, why = vve._run_sql_check(_FakeCur(True), "UPDATE validation_evidence SET status='green'")
    chk("非 SELECT 會被白名單擋（證明上面的綠不是恆真）", bad is None and why is not None)
    bad2, _ = vve._run_sql_check(_FakeCur(True), "SELECT 1; DROP TABLE x")
    chk("多語句會被擋", bad2 is None)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="sim／arena 兩軸之綠燈帳本列（M-P13）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        if a.run:
            return _run(conn)
        if a.verify:
            return _verify(conn)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
