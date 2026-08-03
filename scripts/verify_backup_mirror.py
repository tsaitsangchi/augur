#!/usr/bin/env python
"""🎯 備份鏡像哨兵——量「鏡像現在還在、而且真的還原得回來」，不是量 `cp` 當下的離開碼。

起因（優化計畫書第 18 步 M-O2，2026-08-03）：`scripts/backup_database.sh` 之鏡像步驟為
`mkdir -p && cp -r … && echo "✓ 鏡像完成"`——綠燈量的是 cp 的 rc。實測同日：`~/logs/backup.log`
之 08-01 那輪逐字寫「✓ 鏡像完成」，而 `/mnt/c/database` 為 `total 0`（空）。本地 dump 有走
`pg_restore -l` 驗 toc（印「11G / 2696 物件 / 352s」），**鏡像那一份完全沒驗**。

本支量的四件事（缺一即紅；「cp 曾經成功」不在其中）：
  1. 鏡像目錄裡真有 `augur_YYYYMMDD_weekly_Fd` 組——空目錄＝紅，不是「無事發生」
  2. 該組可被 `pg_restore -l` 解析、物件數 ≥ 100（不可解析＝只是一堆位元組）
  3. `*.dat.gz` 檔數 == TOC 之 TABLE DATA 項數——drvfs 半途中斷之 cp 於此翻紅
  4. 與本地同名組逐項比對（物件數／資料檔數／總位元組）——任一不一致即紅
  再加新鮮度：最新「可還原」鏡像之年齡 ≤ 8 日（週六週備份 + 1 日寬限）。

**閾值刻意不開 env 旋鈕**：異裝置選型（M-O2 之 Steward 部分）未決前，本紅燈就是該待裁事項的
可見載體——不得以放寬閾值、加豁免或改判來消燈（計畫書第 18 步驗收④逐字）。
**射程誠實**：`pg_restore -l` 只讀 toc.dat；本支以「資料檔數 == TOC 資料項數 + 總位元組相符」
補強完整性，但**不宣稱**已證明可還原成一個可查詢的庫——那唯有真跑 `pg_restore` 到臨時庫才算，
成本 11G/數十分鐘，不在本支射程（列為殘餘，見計畫書 §4 異裝置條）。

守 #15（紅燈要會亮、假綠不留）· #9／#10（數字出自 `pg_restore` 與檔案系統，非估算）·
#28（純本地、零 usage、零外部 API）· #29a/d · #35（自測餵真輸出、紅綠雙向、下游絆線）。

執行指令矩陣
------------
    python scripts/verify_backup_mirror.py                      # 無參數＝--check（唯讀；紅則 exit 1）
    python scripts/verify_backup_mirror.py --check              # 唯讀哨兵：逐組驗證＋新鮮度判定
    python scripts/verify_backup_mirror.py --check --json       # 機器可讀（供 cron／稽核）
    python scripts/verify_backup_mirror.py --check --record     # 同上＋附一列備份帳本（JSONL append）
    python scripts/verify_backup_mirror.py --register-evidence  # 冪等 upsert 一列 validation_evidence（DML）
    python scripts/verify_backup_mirror.py --selftest           # 紅綠自測（免 DB 免 API；餵真 toc 輸出）
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import _bootstrap  # noqa: F401

DUMP_DIR = Path(os.environ.get("AUGUR_DUMP_DIR", str(Path.home() / "db_dumps")))
MIRROR_DIR = Path(os.environ.get("AUGUR_DUMP_MIRROR", "/mnt/c/database"))
LEDGER_NAME = "backup_ledger.jsonl"   # 帳本住 dump 目錄旁、不住 DB:DB 死了帳本要還在(循環依賴)

MAX_AGE_DAYS = 8      # 週六週備份 + 1 日寬限;**無 env 旋鈕**——見檔頭「不得加豁免」
MIN_OBJECTS = 100     # 與 backup_database.sh [2/4] 同一閾值
SET_RE = re.compile(r"^augur_(\d{8})_weekly_Fd$")

EVIDENCE_ID = "E10_backup_mirror_fresh"
EVIDENCE_CMD = "venv/bin/python scripts/verify_backup_mirror.py --check"


# ── 純函式（自測以真實 pg_restore -l 輸出餵之） ──────────────────────────────

def parse_set_date(name: str) -> Optional[date]:
    """備份組目錄名 → 該組之資料日期;非本支產物口徑回 None(無法判齡)。"""
    m = SET_RE.match(name)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def count_toc_objects(toc_text: str) -> int:
    """`pg_restore -l` 輸出 → 物件列數。尺與 backup_database.sh 之 `grep -vc '^;'` 相同。"""
    return sum(1 for ln in toc_text.splitlines() if ln and not ln.startswith(";"))


def count_toc_data_entries(toc_text: str) -> int:
    """TOC 中「有資料檔」之項數——directory format 每項對應一個 <oid>.dat[.gz]。"""
    return sum(1 for ln in toc_text.splitlines() if " TABLE DATA " in ln)


def toc_has_blobs(toc_text: str) -> bool:
    """large object 存在時檔數不變式另有形狀 ⇒ 該項檢查退場並誠實標示,不假裝適用。"""
    return any(" BLOBS " in ln for ln in toc_text.splitlines())


@dataclasses.dataclass
class SetFacts:
    """一組備份（本地或鏡像）之據實測得事實;problems 非空即「不可還原」。"""
    name: str
    where: str
    objects: Optional[int] = None
    data_entries: Optional[int] = None
    data_files: Optional[int] = None
    total_bytes: Optional[int] = None
    age_days: Optional[int] = None
    blobs: bool = False
    problems: list = dataclasses.field(default_factory=list)

    @property
    def restorable(self) -> bool:
        return not self.problems


def completeness_problems(objects, data_files, data_entries, blobs):
    """純判定：一組備份之 toc/檔案事實 → 問題清單（空＝完整）。inspect_set 走這條、自測亦驗這條。"""
    out = []
    if objects is not None and objects < MIN_OBJECTS:
        out.append(f"物件數異常（{objects} < {MIN_OBJECTS}）")
    if blobs:
        out.append("含 BLOBS 項——資料檔數不變式不適用，須人工複核（本支不假裝覆蓋）")
    elif data_files != data_entries:
        out.append(f"資料檔缺漏（*.dat[.gz] {data_files} 個 vs TOC 資料項 {data_entries} 個）")
    return out


def verdict(mirrors, max_age_days: int = MAX_AGE_DAYS):
    """純判定：鏡像事實表 → ('green'|'red', 說明行)。空清單＝紅（異地層為零）。"""
    if not mirrors:
        return "red", ["鏡像目錄無任何備份組（augur_YYYYMMDD_weekly_Fd）——異地備份層為零"]
    fresh = [m for m in mirrors
             if m.restorable and m.age_days is not None and m.age_days <= max_age_days]
    if fresh:
        best = min(fresh, key=lambda m: m.age_days)
        return "green", [f"最新可還原鏡像 {best.name}：{best.age_days} 日齡 ≤ {max_age_days} 日"
                         f"（物件 {best.objects}／資料檔 {best.data_files}）"]
    lines = [f"無任何「可還原且 ≤ {max_age_days} 日」之鏡像備份組："]
    for m in mirrors:
        why = "；".join(m.problems) if m.problems else f"年齡 {m.age_days} 日 > {max_age_days} 日"
        lines.append(f"  {m.name}：{why}")
    return "red", lines


def rc_of(status: str) -> int:
    """判定 → 離開碼。`--check` 走這條;自測亦驗這條（斷言與 rc 之間不留縫）。"""
    return 0 if status == "green" else 1


def compare_pair(mirror: SetFacts, local: Optional[SetFacts]) -> None:
    """鏡像 ↔ 本地同名組逐項比對，不一致寫回 mirror.problems（就地）。"""
    if local is None or not local.restorable:
        return
    for label, a, b in (("物件數", mirror.objects, local.objects),
                        ("資料檔數", mirror.data_files, local.data_files),
                        ("總位元組", mirror.total_bytes, local.total_bytes)):
        if a is not None and b is not None and a != b:
            mirror.problems.append(f"{label}與本地不一致（鏡像 {a} vs 本地 {b}）")


# ── IO ────────────────────────────────────────────────────────────────────────

def list_sets(root: Path):
    if not root.is_dir():
        return []
    return sorted((p for p in root.iterdir() if p.is_dir() and p.name.startswith("augur_")),
                  key=lambda p: p.name)


def read_toc(path: Path):
    """跑 `pg_restore -l`（唯讀、只讀 toc.dat）→ (stdout, 錯誤說明)。"""
    try:
        r = subprocess.run(["pg_restore", "-l", str(path)],
                           capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return None, "找不到 pg_restore（PostgreSQL client 未安裝）"
    except subprocess.TimeoutExpired:
        return None, "pg_restore -l 逾時（>300s）"
    if r.returncode != 0:
        return None, f"pg_restore -l 不可解析（rc={r.returncode}：{r.stderr.strip()[:100]}）"
    return r.stdout, None


def inspect_set(path: Path, today: date, where: str) -> SetFacts:
    f = SetFacts(name=path.name, where=where)
    d = parse_set_date(path.name)
    if d is None:
        f.problems.append("名稱不合本支產物口徑（augur_YYYYMMDD_weekly_Fd）——無法判齡")
    else:
        f.age_days = (today - d).days
    try:
        entries = list(path.iterdir())
    except OSError as e:
        f.problems.append(f"目錄不可讀（{type(e).__name__}）")
        return f
    f.total_bytes = sum(p.stat().st_size for p in entries if p.is_file())
    f.data_files = sum(1 for p in entries if p.name.endswith((".dat", ".dat.gz"))
                       and p.name != "toc.dat")
    if not (path / "toc.dat").is_file():
        f.problems.append("缺 toc.dat")
        return f
    toc, err = read_toc(path)
    if toc is None:
        f.problems.append(err)
        return f
    f.objects = count_toc_objects(toc)
    f.data_entries = count_toc_data_entries(toc)
    f.blobs = toc_has_blobs(toc)
    f.problems.extend(completeness_problems(f.objects, f.data_files, f.data_entries, f.blobs))
    return f


def collect(today: Optional[date] = None):
    """→ (本地事實表, 鏡像事實表)。唯讀:只跑 pg_restore -l 與 stat。"""
    today = today or date.today()
    locals_ = [inspect_set(p, today, "local") for p in list_sets(DUMP_DIR)]
    by_name = {f.name: f for f in locals_}
    mirrors = []
    for p in list_sets(MIRROR_DIR):
        f = inspect_set(p, today, "mirror")
        compare_pair(f, by_name.get(f.name))
        mirrors.append(f)
    return locals_, mirrors


def ledger_path() -> Path:
    return DUMP_DIR / LEDGER_NAME


def append_ledger(status: str, reasons, locals_, mirrors) -> Path:
    """一列備份帳本（JSONL append-only）。**不住 DB**——DB 沒了帳本得還在。"""
    row = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "verdict": status,
        "reasons": reasons,
        "max_age_days": MAX_AGE_DAYS,
        "local_dir": str(DUMP_DIR),
        "mirror_dir": str(MIRROR_DIR),
        "local": [dataclasses.asdict(f) for f in locals_],
        "mirror": [dataclasses.asdict(f) for f in mirrors],
    }
    p = ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return p


# ── 模式 ──────────────────────────────────────────────────────────────────────

def check(as_json: bool = False, record: bool = False) -> int:
    locals_, mirrors = collect()
    status, reasons = verdict(mirrors)
    if as_json:
        print(json.dumps({"verdict": status, "reasons": reasons,
                          "local": [dataclasses.asdict(f) for f in locals_],
                          "mirror": [dataclasses.asdict(f) for f in mirrors]},
                         ensure_ascii=False, indent=2))
    else:
        print(f"── 備份鏡像哨兵（本地 {DUMP_DIR}／鏡像 {MIRROR_DIR}） ──")
        for f in locals_:
            print(f"  本地 {f.name}：{'可還原' if f.restorable else '✗ ' + '；'.join(f.problems)}"
                  + (f"（物件 {f.objects}／資料檔 {f.data_files}／{f.total_bytes} B）"
                     if f.restorable else ""))
        if not mirrors:
            print(f"  鏡像：(無)  ← {MIRROR_DIR} 內無 augur_* 備份組")
        for f in mirrors:
            print(f"  鏡像 {f.name}：{'可還原' if f.restorable else '✗ ' + '；'.join(f.problems)}"
                  + (f"（物件 {f.objects}／資料檔 {f.data_files}／{f.total_bytes} B）"
                     if f.restorable else ""))
        icon = "✓" if status == "green" else "✗"
        for ln in reasons:
            print(f"  {ln}")
        print(f"{icon} 鏡像新鮮度判定：{status}")
        if status == "red":
            print("  ⚠ 此紅燈為 M-O2「異裝置選型」待裁事項之可見載體——修法是把異地備份做出來，"
                  "不是放寬閾值或加豁免。")
    if record:
        print(f"  帳本已附一列 → {append_ledger(status, reasons, locals_, mirrors)}")
    return rc_of(status)


def register_evidence() -> int:
    """冪等 upsert 一列 validation_evidence（DML;不建表、不改 schema）。"""
    from augur.core import db

    locals_, mirrors = collect()
    status, reasons = verdict(mirrors)
    note = "；".join(reasons)[:900]
    claim = (f"最新可還原鏡像備份年齡 ≤ {MAX_AGE_DAYS} 日"
             "（pg_restore -l 可解析＋資料檔數=TOC 資料項＋與本地物件數/位元組一致）")
    status_note = ("M-O2：異裝置選型（Steward 部分）未決前，本列不得改判或加豁免——"
                   "它是該待裁事項之可見載體（優化計畫書 20260803 第 18 步 驗收④）。")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO validation_evidence "
            "(evidence_id, chain_link, claim, check_type, check_cmd, source_ref, "
            " status, status_note, machine_note, last_verified_at) "
            "VALUES (%s,'harness',%s,'script_exit',%s,%s,%s,%s,%s,now()) "
            "ON CONFLICT (evidence_id) DO UPDATE SET "
            "  claim=EXCLUDED.claim, check_cmd=EXCLUDED.check_cmd, "
            "  source_ref=EXCLUDED.source_ref, status=EXCLUDED.status, "
            "  machine_note=EXCLUDED.machine_note, last_verified_at=now()",
            (EVIDENCE_ID, claim, EVIDENCE_CMD,
             "reports/augur_optimization_master_plan_20260803.md 第 18 步（M-O2）"
             "；scripts/backup_database.sh",
             status, status_note, note))
        conn.commit()
        cur.execute("SELECT status, machine_note, last_verified_at FROM validation_evidence "
                    "WHERE evidence_id=%s", (EVIDENCE_ID,))
        row = cur.fetchone()
    print(f"✓ validation_evidence upsert：{EVIDENCE_ID} → {row[0]}")
    print(f"  machine_note：{row[1]}")
    print(f"  last_verified_at：{row[2]}")
    print("  （status_note 僅於首次 INSERT 寫入;重跑不覆寫——人裁欄不受機器每跑抹除）")
    return rc_of(row[0])


# ── 自測（#35：純函式餵真輸入、紅綠雙向、下游絆線；免 DB 免 API） ─────────────

# 取自 `pg_restore -l ~/db_dumps/augur_20260801_weekly_Fd` 之真實輸出（前 22 行原樣）。
_REAL_TOC = """;
; Archive created at 2026-08-01 13:18:31 CST
;     dbname: augur
;     TOC Entries: 2700
;     Compression: gzip
;     Dump Version: 1.16-0
;     Format: DIRECTORY
;     Integer: 4 bytes
;     Offset: 8 bytes
;     Dumped from database version: 17.10 (Ubuntu 17.10-1.pgdg24.04+1)
;     Dumped by pg_dump version: 17.10 (Ubuntu 17.10-1.pgdg24.04+1)
;
;
; Selected TOC Entries:
;
14; 2615 2200 SCHEMA - public augur
7470; 0 0 COMMENT - SCHEMA public augur
2; 3079 1178662 EXTENSION - vector
7471; 0 0 COMMENT - EXTENSION vector
1461; 1247 1178991 TYPE public src_kind augur
2382; 1247 1178998 TYPE public unit_state augur
808; 1255 1264809 FUNCTION public admit_state_guard() augur
"""
_REAL_TOC_DATA = """7444; 0 1264814 TABLE DATA public admission_assist_run augur
7128; 0 1179396 TABLE DATA public advisor_distill_context augur
"""


def _mk(name, age, ok=True, objects=2696, files=322):
    f = SetFacts(name=name, where="mirror", objects=objects, data_entries=files,
                 data_files=files, total_bytes=11007676021, age_days=age)
    if not ok:
        f.problems.append("缺 toc.dat")
    return f


def selftest() -> int:
    ok = 0

    def chk(label, cond):
        nonlocal ok
        print(f"  {'✓' if cond else '✗'} {label}")
        if not cond:
            ok = 1

    # 1) 物件數之尺：真實輸出前 22 行有 7 個非註解列（`grep -vc '^;'` 同值）
    chk("真 toc 前 22 行 → 物件 7", count_toc_objects(_REAL_TOC) == 7)
    chk("純註解文字 → 物件 0（紅向）", count_toc_objects("; only comments\n;\n") == 0)
    # 2) 資料項之尺
    chk("真 TABLE DATA 兩列 → 資料項 2",
        count_toc_data_entries(_REAL_TOC + _REAL_TOC_DATA) == 2)
    chk("無 TABLE DATA → 資料項 0（紅向）", count_toc_data_entries(_REAL_TOC) == 0)
    chk("本庫 toc 無 BLOBS", toc_has_blobs(_REAL_TOC + _REAL_TOC_DATA) is False)
    # 3) 判齡
    chk("真產物名 → 2026-08-01", parse_set_date("augur_20260801_weekly_Fd") == date(2026, 8, 1))
    chk("非本支口徑名 → None（紅向）", parse_set_date("augur_20260731_postmerge_Fd") is None)
    # 3b) 完整性不變式（數字取自本機真 dump：2696 物件／322 資料檔）
    chk("真值 2696/322/322 → 無問題", completeness_problems(2696, 322, 322, False) == [])
    chk("少一個資料檔（321 vs 322）→ 有問題（半途中斷之 cp）",
        len(completeness_problems(2696, 321, 322, False)) == 1)
    chk("物件數低於地板 → 有問題", len(completeness_problems(3, 322, 322, False)) == 1)
    chk("含 BLOBS → 不假裝覆蓋（判有問題而非放行）",
        len(completeness_problems(2696, 322, 322, True)) == 1)
    # 3c) 鏡像 ↔ 本地逐項比對（就地寫回 problems）
    m, lo = _mk("augur_20260801_weekly_Fd", 2), _mk("augur_20260801_weekly_Fd", 2)
    m.total_bytes = lo.total_bytes - 603
    compare_pair(m, lo)
    chk("鏡像位元組短少 → 比對判紅", not m.restorable)
    m2, lo2 = _mk("augur_20260801_weekly_Fd", 2), _mk("augur_20260801_weekly_Fd", 2)
    compare_pair(m2, lo2)
    chk("鏡像與本地全等 → 比對放行（綠向）", m2.restorable)
    # 4) verdict 四情境（含今日 live 之形狀：鏡像空）
    chk("鏡像空 → red", verdict([])[0] == "red")
    chk("新鮮可還原 → green", verdict([_mk("augur_20260801_weekly_Fd", 2)])[0] == "green")
    chk("可還原但 9 日齡 → red", verdict([_mk("augur_20260725_weekly_Fd", 9)])[0] == "red")
    chk("新鮮但缺 toc → red", verdict([_mk("augur_20260801_weekly_Fd", 2, ok=False)])[0] == "red")
    chk("一綠一舊 → green（取最新可還原者）",
        verdict([_mk("augur_20260725_weekly_Fd", 9), _mk("augur_20260801_weekly_Fd", 2)])[0]
        == "green")
    # 5) 下游絆線：判定 → 離開碼之對映即 --check 所用者
    chk("rc 綁定：red→1", rc_of(verdict([])[0]) == 1)
    chk("rc 綁定：green→0", rc_of(verdict([_mk("augur_20260801_weekly_Fd", 2)])[0]) == 0)
    # 6) 真 IO 路徑：合成壞鏡像組必被判不可還原且不 crash
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "augur_20260803_weekly_Fd"
        bad.mkdir()
        (bad / "toc.dat").write_bytes(b"not a real toc")
        (bad / "7444.dat.gz").write_bytes(b"x")
        f = inspect_set(bad, date(2026, 8, 3), "mirror")
        chk("壞 toc 之合成組 → 不可還原（真跑 pg_restore -l）", not f.restorable)
        chk("壞組年齡仍判得出（0 日）", f.age_days == 0)
        empty = Path(td) / "empty_mirror"
        empty.mkdir()
        chk("空鏡像目錄 → 無備份組", list_sets(empty) == [])
    # 7) 真上游輸出（本機有 dump 才跑;無則誠實 SKIP，不假綠）
    real = sorted(p for p in list_sets(DUMP_DIR) if SET_RE.match(p.name))
    if real:
        f = inspect_set(real[-1], date.today(), "local")
        chk(f"本機真 dump {f.name} → 可還原", f.restorable)
    else:
        print(f"  — SKIP 本機真 dump 檢查（{DUMP_DIR} 無 augur_*_weekly_Fd）")
    print("自測：" + ("全通過 ✓" if ok == 0 else "有失敗 ✗"))
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--register-evidence", dest="reg", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.reg:
        return register_evidence()
    if not args.check:
        print(__doc__.split("執行指令矩陣")[1].split("------------")[1])
    return check(as_json=args.json, record=args.record)


if __name__ == "__main__":
    sys.exit(main())
