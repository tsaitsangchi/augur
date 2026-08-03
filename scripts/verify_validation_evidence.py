#!/usr/bin/env python
"""證據帳本重驗 CLI — validation_evidence 逐列重驗+狀態更新(驗證總綱 V0;解凍 GATE 前置)。

🎯 這支在做什麼(白話):讀帳本每列,依 check_type 重驗——sql 型跑唯讀 SELECT(前綴白名單機械擋、
   須回單列單欄 boolean);script_exit 型只在 --with-scripts 才執行(命令白名單=venv/bin/python scripts/
   開頭)採 exit code;manual 型:未過期跳過、過期(valid_until<now())自動轉 unverified 待 hugo 重簽
   (C1 甲案 2026-08-01;green/amber 才降轉、red 不動——紅比未驗誠實;只寫 machine_note,
   status_note/last_verified_at 永不觸碰;valid_until 欄未就位時 graceful 走舊行為+警示,cron 不斷炊)。
   **green=斷言此刻對 DB 為真、非方法論背書**;
   斷言寫壞=標 red+note 不 crash 整批(#15)。--strict:任一非 green → exit 1(daily_green 選配段+
   解凍 GATE V2 之機械前置——已知債紅列須先人裁除名或修復,無處可藏)。

**M-P12(a)(2026-08-03):`last_verified_at IS NULL` 者不得計入 green**——該欄是「這條斷言被實際
   碰過」的唯一痕跡;為 NULL 即**從未被任何檢驗碰過**,其 green 是種子當下寫死的字串而非驗證結果。
   實犯:`E3_promotion_funnel`／`E4_gm_promotion_gap` 兩列 manual green、`valid_until=2026-10-09`
   ⇒ 效期檢查永遠不觸發、`last_verified_at` 永遠 NULL,於是**以 green 身分計入分子且無任何機制
   會讓它變紅**。處置=每次 `--run` 開頭一律把 green/amber 且 lva IS NULL 者降為 `unverified`
   (`demote_never_verified`);sql 型隨後被真重驗而自然復綠(帶真 lva),manual 型停在 unverified
   待 hugo 親簽——**不代簽、不代填 lva**。DB 層對偶鎖=`chk_ve_green_verified`
   (`scripts/migrate_validation_evidence_red_since_ddl.py`,待 DDL 窗)。

**M-P12(b):紅燈時鐘 `red_since`**——紅列「何時開始紅」現無載體,每日 07:10 忠實重驗成紅卻無人
   處置且**無從得知已紅多久**。處置=轉紅時 `red_since=COALESCE(red_since, now())`(不覆寫既有
   起算點)、轉非紅時清 NULL;每次 `--run`／`--list` 尾行印一句紅燈時鐘。**欄未就位時誠實印
   「欄未就位」、不以 `last_verified_at` 冒充**(那是「最近一次驗到它是紅的」,會低估紅齡)。

守 #15(紅列誠實、錯不掩)· #5(SELECT-only/命令白名單)· #6(冪等重跑)· #29a · #35(先驗紅)。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §1.3;
   M-P12=reports/augur_optimization_master_plan_20260803.md 第 17 步。

執行指令矩陣:
  python scripts/verify_validation_evidence.py                 # 無參數:印矩陣+帳本現況(唯讀)
  python scripts/verify_validation_evidence.py --list          # 逐列狀態+紅燈時鐘一行
  python scripts/verify_validation_evidence.py --run           # 重驗全部 sql 型(script 跳過;manual 過期→unverified)
  python scripts/verify_validation_evidence.py --run --id E6_oos_frozen_rowcount
  python scripts/verify_validation_evidence.py --run --with-scripts   # 連 script_exit 型一起(重)
  python scripts/verify_validation_evidence.py --strict        # 任一非 green → exit 1(GATE 前置)
  python scripts/verify_validation_evidence.py --week-line     # M-P12(b) 週報紅燈一行（告知哨）
  python scripts/verify_validation_evidence.py --selftest      # 純函式紅綠自測(免 DB 免 API)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

REPO = Path(__file__).resolve().parent.parent
_CMD_PREFIX = "venv/bin/python scripts/"    # script_exit 白名單前綴(機械擋)
NEVER_VERIFIED_NOTE = (
    "M-P12(a):last_verified_at IS NULL ⇒ 從未被任何檢驗碰過,不得以 green/amber 身分計入;"
    "降 unverified——sql 型待本輪重驗、manual 型待 hugo 親簽(本程式不代簽、不代填 last_verified_at)")


def _run_sql_check(cur, check_sql):
    """唯讀 SELECT、單列單欄 boolean;違約 → (None, 錯誤說明)。"""
    s = (check_sql or "").strip().rstrip(";")
    if not s.lower().startswith("select") or ";" in s:
        return None, "check_sql 不過白名單(僅單條 SELECT)"
    try:
        cur.execute("BEGIN TRANSACTION READ ONLY")
        cur.execute("SET LOCAL statement_timeout='60s'")
        cur.execute(s)
        row = cur.fetchone()
        cur.execute("ROLLBACK")
    except Exception as e:
        try:
            cur.execute("ROLLBACK")
        except Exception:
            pass
        return None, f"查詢失敗:{type(e).__name__}: {str(e)[:120]}"
    if row is None or len(row) != 1 or not isinstance(row[0], bool):
        return None, f"未回單列單欄 boolean:{row!r}"
    return row[0], None


def _run_script_check(check_cmd):
    """白名單命令 exit code;僅 --with-scripts 路徑呼叫。"""
    cmd = (check_cmd or "").strip()
    if not cmd.startswith(_CMD_PREFIX):
        return None, f"命令不過白名單(須以 {_CMD_PREFIX} 開頭)"
    try:
        r = subprocess.run(cmd.split(), cwd=str(REPO), capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None, "script 逾時(>600s)"
    return r.returncode == 0, f"exit={r.returncode}"


def _has_col(cur, col):
    """欄在否——DDL 由 --apply 於 DDL 窗落地,未落地時走 graceful 舊行為、cron 不斷炊。"""
    cur.execute("SELECT count(*) FROM information_schema.columns "
                "WHERE table_name='validation_evidence' AND column_name=%s", (col,))
    return cur.fetchone()[0] > 0


def _has_valid_until(cur):
    """C1 過渡偵測:valid_until 欄在否(DDL-1 由主 session 落地;未落地時走舊行為不炸 cron)。"""
    return _has_col(cur, "valid_until")


def demote_never_verified(cur, only_id=None, has_red_since=False):
    """M-P12(a):green/amber 但 `last_verified_at IS NULL` ⇒ 從未被任何檢驗碰過 ⇒ 降 unverified。

    **不 commit**(交易邊界留給呼叫端,測試得以 ROLLBACK 驗真行為)。回傳被降轉之 evidence_id 列表。
    只寫 status/machine_note(+red_since 清 NULL);**永不觸碰 status_note(人裁原文)與
    last_verified_at(起算基準)**——後者一碰即等於代替人宣稱「我驗過了」。
    """
    sql = ("UPDATE validation_evidence SET status='unverified', machine_note=%s"
           + (", red_since=NULL" if has_red_since else "")
           + " WHERE status IN ('green','amber') AND last_verified_at IS NULL"
           + (" AND evidence_id=%s" if only_id else "")
           + " RETURNING evidence_id")
    cur.execute(sql, (NEVER_VERIFIED_NOTE,) + ((only_id,) if only_id else ()))
    return [r[0] for r in cur.fetchall()]


def format_red_line(n_red, oldest_id, oldest_since, has_red_since):
    """M-P12(b) 週報一行(純函式;無 DB)。**欄未就位／未起算時不編日期**——寧可說不知道。"""
    if n_red == 0:
        return "red 0 條"
    if not has_red_since:
        return (f"red {n_red} 條，最久者 red_since=未知"
                "（red_since 欄未就位；scripts/migrate_validation_evidence_red_since_ddl.py --apply 後起算）")
    if oldest_since is None:
        return (f"red {n_red} 條，最久者 red_since=未起算"
                "（欄剛就位，本輪重驗後才有值）")
    return f"red {n_red} 條，最久者 red_since={oldest_since:%Y-%m-%d}（{oldest_id}）"


def red_report(cur, has_red_since):
    """讀全帳本紅列(不受 --id 過濾影響:週報一行講的是整本帳)→ 交給 format_red_line。"""
    if has_red_since:
        cur.execute("SELECT evidence_id, red_since FROM validation_evidence WHERE status='red' "
                    "ORDER BY red_since NULLS LAST, evidence_id")
    else:
        cur.execute("SELECT evidence_id, NULL::timestamptz FROM validation_evidence "
                    "WHERE status='red' ORDER BY evidence_id")
    rows = cur.fetchall()
    oid, since = rows[0] if rows else (None, None)
    return format_red_line(len(rows), oid, since, has_red_since)


def run(only_id=None, with_scripts=False):
    with db.connect() as conn:
        cur = conn.cursor()
        has_vu = _has_valid_until(cur)
        has_rs = _has_col(cur, "red_since")
        if not has_vu:
            print("  ⚠ valid_until 欄未就位(C1 DDL-1 待 --apply)——manual 有效期檢查暫走舊行為(永不降轉)")
        if not has_rs:
            print("  ⚠ red_since 欄未就位(M-P12b DDL 待 --apply)——紅燈時鐘暫無起算點,尾行誠實印「未知」")
        # M-P12(a):先把「從未被檢驗過卻掛 green/amber」者降轉,再進重驗迴圈——
        # sql 型會在同一輪被真重驗而復綠(帶真 last_verified_at),manual 型停在 unverified 待人簽。
        demoted = demote_never_verified(cur, only_id, has_rs)
        if demoted:
            conn.commit()
            for eid in demoted:
                print(f"  ? {eid}: 從未被檢驗(last_verified_at IS NULL)→ unverified(M-P12a)")
        cur.execute("SELECT evidence_id, check_type, check_sql, check_cmd, status"
                    + (", valid_until" if has_vu else "") + " FROM validation_evidence "
                    + ("WHERE evidence_id=%s " if only_id else "") + "ORDER BY evidence_id",
                    (only_id,) if only_id else ())
        rows = cur.fetchall()
        n_g = n_r = n_skip = n_exp = 0
        for row in rows:
            eid, ctype, csql, ccmd, st = row[:5]
            vu = row[5] if has_vu else None
            if ctype == "manual":
                # C1 甲案:過期(DB 端 now() 判)之 green/amber 降轉 unverified;red 不動。
                # 只寫 status+machine_note——status_note(人裁原文)/last_verified_at(起算基準+重簽稽核痕)不觸碰。
                if vu is not None and st in ("green", "amber"):
                    cur.execute(
                        "UPDATE validation_evidence SET status='unverified', machine_note=%s "
                        "WHERE evidence_id=%s AND check_type='manual' "
                        "AND valid_until < now() AND status IN ('green','amber')",
                        (f"manual 有效期已過(valid_until={vu:%Y-%m-%d});自動轉 unverified,待 hugo 重簽", eid))
                    if cur.rowcount:
                        conn.commit()
                        n_exp += 1
                        print(f"  ✗ {eid}: manual 有效期已過({vu:%Y-%m-%d}) → unverified(待 hugo 重簽)")
                        continue
                n_skip += 1
                print(f"  — {eid}: manual(人審;現況 {st}"
                      + (f";有效至 {vu:%Y-%m-%d}" if vu else ";無有效期") + ")")
                continue
            if ctype == "script_exit" and not with_scripts:
                n_skip += 1
                print(f"  — {eid}: script_exit(--with-scripts 才執行;現況 {st})")
                continue
            ok, note = (_run_sql_check(cur, csql) if ctype == "sql" else _run_script_check(ccmd))
            if ok is None:
                new, nn = "red", note
            else:
                new, nn = ("green", note) if ok else ("red", note or "斷言為假")
            # **本稽核器不得寫 status_note**——該欄記人裁/設計理由(半衰期以年計、寫入者是人),
            # 機器判定一律進 machine_note(每跑覆寫)。原碼 `status_note=COALESCE(%s,status_note)`
            # 之 COALESCE 為死碼(上一行 `or "斷言為假"` 保證 nn 恆非空)⇒ 每跑必覆寫;該表
            # trigger=0、無 pre-image ⇒ 2026-07-31 13:29 一跑即抹掉 E1 之 hugo 拍板逐字理由。
            # M-P12(b):紅燈時鐘——轉紅時 COALESCE 保留既有起算點(連紅不重置、紅齡才算得準),
            # 轉非紅時清 NULL(下次再紅重新起算)。欄未就位則整段不寫,行為與舊版同。
            rs = (", red_since=CASE WHEN %s='red' THEN COALESCE(red_since, now()) END" if has_rs else "")
            cur.execute("UPDATE validation_evidence SET status=%s, machine_note=%s, "
                        "last_verified_at=now()" + rs + " WHERE evidence_id=%s",
                        (new, nn) + ((new,) if has_rs else ()) + (eid,))
            conn.commit()
            n_g += (new == "green"); n_r += (new == "red")
            print(f"  {'✓' if new == 'green' else '✗'} {eid} → {new}" + (f"({nn})" if nn else ""))
        print(f"── 重驗完:green {n_g} / red {n_r} / 過期轉 unverified {n_exp} / 跳過 {n_skip}(manual/script)")
        print(f"── 紅燈時鐘:{red_report(cur, has_rs)}")
    return 0


def _list():
    with db.connect() as conn, db.transaction(conn) as cur:
        has_vu = _has_valid_until(cur)
        cur.execute("SELECT evidence_id, chain_link, check_type, status, "
                    "coalesce(to_char(last_verified_at,'MM-DD HH24:MI'),'-'), "
                    + ("coalesce(to_char(valid_until,'YYYY-MM-DD'),'-')" if has_vu else "'-'")
                    + " FROM validation_evidence ORDER BY chain_link, evidence_id")
        for r in cur.fetchall():
            icon = {"green": "✓", "red": "✗", "amber": "△", "unverified": "?"}[r[3]]
            print(f"  {icon} [{r[1]:<11}] {r[0]:<28} {r[2]:<11} {r[3]:<10} {r[4]}"
                  + (f" 有效至 {r[5]}" if r[5] != "-" else ""))
        print(f"── 紅燈時鐘:{red_report(cur, _has_col(cur, 'red_since'))}")


def strict():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT evidence_id, status FROM validation_evidence WHERE status <> 'green' ORDER BY 1")
        bad = cur.fetchall()
    if bad:
        print(f"✗ --strict:{len(bad)} 列非 green(解凍 GATE 前置不滿足——已知債須人裁除名或修復):")
        for eid, st in bad:
            print(f"   {st:<10} {eid}")
        return 1
    print("✓ --strict:帳本全綠")
    return 0


class _RecordingCursor:
    """只記下被送出的 SQL 與參數(不連 DB)——供自測檢查 demote 產生的 SET/WHERE 形狀。"""

    def __init__(self):
        self.sql = None
        self.args = None

    def execute(self, sql, args=None):
        self.sql, self.args = sql, args

    def fetchall(self):
        return []


def _selftest():
    """純函式紅綠自測(免 DB 免 API)。行為層之真證據在
    `pytest tests/test_validation_evidence_honesty.py`(對真表跑、ROLLBACK)。"""
    import datetime as _dt
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # ── format_red_line 四分支(timestamptz 之真形狀＝datetime.datetime,已對 live 查證) ──
    chk("0 紅不編任何日期", format_red_line(0, None, None, True) == "red 0 條")
    no_col = format_red_line(4, None, None, False)
    chk("欄未就位→說未知、不冒充日期", "未知" in no_col and "2026" not in no_col)
    not_yet = format_red_line(4, "E2_x", None, True)
    chk("欄在但尚未起算→說未起算、不編日期", "未起算" in not_yet and "2026" not in not_yet)
    real = format_red_line(3, "E2_x", _dt.datetime(2026, 7, 29, 7, 10, tzinfo=_dt.timezone.utc), True)
    chk("有起算點→印 YYYY-MM-DD 與該列 id", "2026-07-29" in real and "E2_x" in real)
    chk("條數如實帶出", real.startswith("red 3 條"))

    # ── demote_never_verified 產生之 SQL 形狀(haystack=執行期字串,非本檔原始碼) ──
    c = _RecordingCursor()
    demote_never_verified(c)
    sql = c.sql.lower()
    set_clause = sql.split("where")[0]
    chk("只降轉 green/amber", "status in ('green','amber')" in sql)
    chk("條件鎖在 last_verified_at IS NULL", "last_verified_at is null" in sql)
    chk("SET 段不碰 last_verified_at(不代人宣稱已驗)", "last_verified_at" not in set_clause)
    chk("SET 段不碰 status_note(人裁原文)", "status_note" not in set_clause)
    chk("欄未就位時不寫 red_since", "red_since" not in sql)
    c2 = _RecordingCursor()
    demote_never_verified(c2, has_red_since=True)
    chk("欄就位時清 red_since(unverified 非紅)", "red_since=null" in c2.sql.lower())
    c3 = _RecordingCursor()
    demote_never_verified(c3, only_id="E3_promotion_funnel")
    chk("--id 時加上單列過濾", "evidence_id=%s" in c3.sql and c3.args[-1] == "E3_promotion_funnel")
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def week_line() -> int:
    """M-P12(b)／§7.3：只印「紅燈：…」一行（週報掛載；告知哨 rc=0）。"""
    from augur.core import db
    with db.connect() as conn, conn.cursor() as cur:
        has_rs = _has_col(cur, "red_since")
        body = red_report(cur, has_rs)
    print(f"紅燈：validation_evidence {body}")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--id", dest="only_id")
    ap.add_argument("--with-scripts", dest="ws", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--week-line", action="store_true",
                    help="M-P12(b) 週報一行（紅燈時鐘）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.week_line:
        return week_line()
    if args.run:
        return run(args.only_id, args.ws)
    if args.strict:
        return strict()
    if args.list:
        _list(); return 0
    print(__doc__.split("執行指令矩陣:")[1])
    _list()
    return 0


if __name__ == "__main__":
    sys.exit(main())
