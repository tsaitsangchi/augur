#!/usr/bin/env python3
"""🎯 停損閘 consequence 之機械載體——「三軸整體停止＋帳本封存＋不得換碼重開」終於有槍可扣。

守原則 #12（停止複用 `set_evolution_kill_switch` 既有路徑，不重造）、#15（各成分之
「有沒有」誠實印出，不假裝）、#6（--apply 為重動作：TTY 親簽＋首次啟用=Steward）。

起因（登錄冊 F3，2026-08-01）：V2-SUNSET 凍結條文之 consequence
「三軸整體停止、帳本封存、不得換 trigger_code 重開」**無機械載體**——07-31 結算時
`settle_sunset_gate.py` 誠實自陳不執行；封存腳本不存在。本支＝該載體。

**現行處置（呈案單 F3-apply 建議）**：SUNSET 已 pass、無現行停止需求 ⇒ 通常**不** `--apply`。
M-G12（2026-08-03／r4 G10）：`--check` 之綠＝`pg_trigger` 上 `trg_sunset_seal_%` **掛齊四表**
（SQL 計數＋rc），**不再**以「本行印得出來＝未鏽」自證。現況 0 支 seal ⇒ `--check` 必紅——
這不是腳本鏽了，是載體「未啟用」的誠實態；週報哨會照印紅（不吞）。

三成分設計：
  〔停止〕四 scope 全設 halt——複用 `set_evolution_kill_switch.set_state`；
    誠實印**讀者覆蓋**：tw/raw driver 已接線（07-31）、PME 原生、lai **零 runner 讀**（halt 防未來）。
  〔封存〕三本 iteration ledger＋evolution_run 掛 `sunset_seal_guard` trigger **拒 INSERT/UPDATE**
    ——引擎層拒絕，非狀態欄簿記（應用層自律不滿足封存語意）。DROP TRIGGER 可逆。
  〔重開〕封存 trigger 之例外訊息明載：重開唯 Steward 以**新 trigger_code** 之新裁決
    ＋--unseal——「不得換 trigger_code 重開」之禁令對象是**舊碼複活**，新裁決不受限。

執行指令矩陣
------------
    python3 scripts/execute_sunset_consequence.py            # 無參數＝--check（唯讀；seal 未齊→rc≠0）
    python3 scripts/execute_sunset_consequence.py --check    # SQL 查 seal＋印三成分；掛齊才 rc=0
    python3 scripts/execute_sunset_consequence.py --apply    # 執行停止＋封存（**TTY 親簽；首次=Steward**）
    python3 scripts/execute_sunset_consequence.py --unseal   # 卸封存 trigger（重開程序之機械步；TTY 親簽）
    python3 scripts/execute_sunset_consequence.py --selftest # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import _bootstrap  # noqa: F401

LEDGERS = ("evolution_iteration_ledger", "raw_evolution_iteration_ledger",
           "local_ai_iteration_ledger", "evolution_run")
TRG_PREFIX = "trg_sunset_seal_"
LOCK_TIMEOUT = "5s"

SEAL_FN = """
CREATE OR REPLACE FUNCTION sunset_seal_guard() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION USING MESSAGE =
      '停損封存生效:三軸帳本拒絕 ' || TG_OP || '(表 ' || TG_TABLE_NAME || ')。'
      '重開唯 Steward 新裁決(新 trigger_code)+親跑 execute_sunset_consequence.py --unseal;'
      '「不得換 trigger_code 重開」禁的是舊碼複活,非新裁決。';
END $$ LANGUAGE plpgsql;
"""


def seal_ddl(table):
    """單表封存 DDL。**純函式**——自測驗其形。拒 INSERT/UPDATE；DELETE 已有 honesty guard 管。"""
    return (f"CREATE TRIGGER {TRG_PREFIX}{table} BEFORE INSERT OR UPDATE ON {table} "
            f"FOR EACH ROW EXECUTE FUNCTION sunset_seal_guard()")


def reader_coverage_note(tw_refs, raw_refs, lai_refs):
    """kill switch 讀者覆蓋之誠實句。純函式。"""
    lai = "lai **零 runner 讀（halt 僅防未來）**" if lai_refs == 0 else f"lai {lai_refs} 處"
    return f"讀者覆蓋:tw {tw_refs} 處/raw {raw_refs} 處/{lai}"


def seal_check_rc(n_sealed, n_expected=None):
    """封存燈之 exit code（純函式；M-G12）。掛齊四表→0；少一支→1。量的是 seal，不是本腳本存在。"""
    if n_expected is None:
        n_expected = len(LEDGERS)
    return 0 if n_sealed >= n_expected else 1


def _sign(action):
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise SystemExit(f"P5.W2 人閘:{action} 須互動 TTY——AI 不得代簽;首次啟用=Steward")
    typed = input("簽名者（親手輸入名字;不得留空）: ").strip()
    if not typed:
        raise SystemExit("P5.W2 人閘:簽名不得留空——無預設值、不代填 OS 帳號")
    return typed


def _seal_state(cur):
    cur.execute("SELECT c.relname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid "
                "WHERE t.tgname LIKE %s", (TRG_PREFIX + "%",))
    return {r[0] for r in cur.fetchall()}


def _check(conn) -> int:
    """M-G12：綠＝`trg_sunset_seal_%` 覆蓋 LEDGERS 四表（SQL）；0 支即紅——不再自證「印得出來」。"""
    import subprocess
    with conn.cursor() as cur:
        cur.execute("SELECT scope||'='||state FROM evolution_kill_switch ORDER BY scope")
        ks = [r[0] for r in cur.fetchall()]
        sealed = _seal_state(cur)
        # 與 master 驗收同形：`tgname LIKE 'trg_sunset_seal_%'`（含非 LEDGERS 孤兒亦計入普查）
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE %s AND NOT tgisinternal",
                    (TRG_PREFIX + "%",))
        n_seal_pg = cur.fetchone()[0]
    root = pathlib.Path(__file__).resolve().parents[1]
    refs = {}
    for tag, f in (("tw", "scripts/run_evolution_iteration.py"),
                   ("raw", "scripts/run_raw_evolution_iteration.py"),
                   ("lai", "scripts/eval_local_model.py")):
        r = subprocess.run(["grep", "-c", "kill_switch", f], capture_output=True,
                           text=True, cwd=str(root))
        refs[tag] = int((r.stdout or "0").strip() or 0)
    missing = [t for t in LEDGERS if t not in sealed]
    rc = seal_check_rc(len(sealed))
    print("── consequence 載體健檢（M-G12：seal SQL＋rc；誠實含缺口）──")
    print(f"  〔停止〕kill_switch: {', '.join(ks) if ks else '（無列）'}")
    print(f"          {reader_coverage_note(refs['tw'], refs['raw'], refs['lai'])}")
    print(f"  〔封存〕seal trigger: LEDGERS {len(sealed)}/{len(LEDGERS)}"
          f"；pg_trigger LIKE '{TRG_PREFIX}%' = {n_seal_pg}"
          + (f"（已掛：{', '.join(sorted(sealed))}）" if sealed else "")
          + (f"；缺：{', '.join(missing)}" if missing else ""))
    if missing:
        print("          → **紅**：封存未齊（策略可暫不 --apply，但 --check 不得假綠）")
    print("  〔重開〕綁定於 seal 例外訊息（新裁決＋--unseal；舊碼複活被禁）")
    print(f"  → rc={rc}（0＝四表封存齊；≠0＝量到缺 seal，不是『本腳本印得出來』）")
    return rc


def _apply(conn) -> int:
    signer = _sign("--apply（停止＋封存）")
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import set_evolution_kill_switch as ks
    for scope in ("tw", "lai", "raw", "global"):
        ks.set_state("halt", scope=scope, by=signer,
                     reason="SUNSET consequence: 三軸整體停止(execute_sunset_consequence)")
    with conn.cursor() as cur:
        cur.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")
        cur.execute(SEAL_FN)
        sealed = _seal_state(cur)
        for t in LEDGERS:
            if t in sealed:
                print(f"  = {t} 已封（冪等跳過）")
                continue
            cur.execute(seal_ddl(t))
            print(f"  ✓ {t} 封存 trigger 掛上")
    conn.commit()
    print(f"✓ consequence 已執行（by={signer}）:四 scope halt＋{len(LEDGERS)} 表拒寫")
    return 0


def _unseal(conn) -> int:
    signer = _sign("--unseal（重開之機械步）")
    with conn.cursor() as cur:
        cur.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")
        for t in LEDGERS:
            cur.execute(f"DROP TRIGGER IF EXISTS {TRG_PREFIX}{t} ON {t}")
    conn.commit()
    print(f"✓ 封存已卸（by={signer}）。kill_switch 之 clear 另跑 set_evolution_kill_switch --clear。")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    d = seal_ddl("evolution_run")
    chk("seal DDL 拒 INSERT 與 UPDATE（封存=引擎層拒寫）",
        "BEFORE INSERT OR UPDATE" in d and "sunset_seal_guard" in d)
    chk("seal DDL 不含 DELETE（既有 honesty guard 之責,不重疊）", "DELETE" not in d)
    chk("四載體表全列（三本 ledger＋evolution_run）", len(LEDGERS) == 4
        and all("ledger" in t or t == "evolution_run" for t in LEDGERS))
    chk("重開訊息載明新裁決路徑（非死鎖）", "unseal" in SEAL_FN and "新 trigger_code" in SEAL_FN)
    chk("lai 零讀者之誠實句（不假裝覆蓋）",
        "零 runner 讀" in reader_coverage_note(3, 3, 0))
    chk("lai 有讀者時不誣賴", "零" not in reader_coverage_note(3, 3, 2))
    chk("M-G12 seal_check_rc：0 支 → rc=1（先驗紅）", seal_check_rc(0) == 1)
    chk("M-G12 seal_check_rc：齊 4 → rc=0", seal_check_rc(4) == 0)
    chk("M-G12 seal_check_rc：缺 1 → rc=1", seal_check_rc(3) == 1)
    # 射程=getsource(_apply)（不含本段）——初版用整檔 body 被第四閘（假斷言閘）當場擋下：
    # 恆真三條，正是該閘要抓的病。閘上線第二次 commit 即抓到作者自己＝閘是真的。
    import inspect as _i
    _apply_src = _i.getsource(_apply)
    _check_src = _i.getsource(_check)
    chk("apply 前設 lock_timeout（絕不排隊=#30）", "lock_timeout" in _apply_src)
    chk("停止複用既有 set_state（#12 不重造）",
        "import set_evolution_kill_switch" in _apply_src and "ks.set_state" in _apply_src)
    chk("M-G12 --check 不再自證『印得出來＝未鏽』", "印得出來＝未鏽" not in _check_src)
    chk("M-G12 --check 以 seal_check_rc 決定 rc",
        "return rc" in _check_src and "rc = seal_check_rc" in _check_src)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="停損 consequence 載體（--check＝seal SQL 燈；未齊即紅）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--unseal", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        if a.apply:
            return _apply(conn)
        if a.unseal:
            return _unseal(conn)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
