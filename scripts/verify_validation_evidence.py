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

守 #15(紅列誠實、錯不掩)· #5(SELECT-only/命令白名單)· #6(冪等重跑)· #29a。
   SSOT=reports/augur_prediction_validation_master_plan_20260711.md §1.3。

執行指令矩陣:
  python scripts/verify_validation_evidence.py                 # 無參數:印矩陣+帳本現況(唯讀)
  python scripts/verify_validation_evidence.py --list          # 逐列狀態
  python scripts/verify_validation_evidence.py --run           # 重驗全部 sql 型(script 跳過;manual 過期→unverified)
  python scripts/verify_validation_evidence.py --run --id E6_oos_frozen_rowcount
  python scripts/verify_validation_evidence.py --run --with-scripts   # 連 script_exit 型一起(重)
  python scripts/verify_validation_evidence.py --strict        # 任一非 green → exit 1(GATE 前置)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

REPO = Path(__file__).resolve().parent.parent
_CMD_PREFIX = "venv/bin/python scripts/"    # script_exit 白名單前綴(機械擋)


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


def _has_valid_until(cur):
    """C1 過渡偵測:valid_until 欄在否(DDL-1 由主 session 落地;未落地時走舊行為不炸 cron)。"""
    cur.execute("SELECT count(*) FROM information_schema.columns "
                "WHERE table_name='validation_evidence' AND column_name='valid_until'")
    return cur.fetchone()[0] > 0


def run(only_id=None, with_scripts=False):
    with db.connect() as conn:
        cur = conn.cursor()
        has_vu = _has_valid_until(cur)
        if not has_vu:
            print("  ⚠ valid_until 欄未就位(C1 DDL-1 待 --apply)——manual 有效期檢查暫走舊行為(永不降轉)")
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
            cur.execute("UPDATE validation_evidence SET status=%s, machine_note=%s, "
                        "last_verified_at=now() WHERE evidence_id=%s", (new, nn, eid))
            conn.commit()
            n_g += (new == "green"); n_r += (new == "red")
            print(f"  {'✓' if new == 'green' else '✗'} {eid} → {new}" + (f"({nn})" if nn else ""))
        print(f"── 重驗完:green {n_g} / red {n_r} / 過期轉 unverified {n_exp} / 跳過 {n_skip}(manual/script)")
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


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--id", dest="only_id")
    ap.add_argument("--with-scripts", dest="ws", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
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
