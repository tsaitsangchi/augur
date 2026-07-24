#!/usr/bin/env python
"""Roadmap R6 S1＋S2 統一哨兵 — 終態宣稱鎖＋本地暢通／隔離機械驗(R6-E12)。

🎯 這支在做什麼(白話):把 R6 計畫 §7 驗收 A1–A8／A10 釘成可個別跑的機械哨兵——
   (S1) G-FT-1 CHECK、fulltext_status 終態帳、終態詞彙禁半套宣稱、AST／predict role 隔離、
        advisor 預設非 predict、本機 LLM 焊點;(S2) 可選串 verify_knowledge_e2e_smoke --run。
   **不含** A9／U6(另授權)、**不含** HAR-ext／FinMind／FRED。宣稱詞彙見 TERMINAL_VOCAB。
守 #15(裁決出 DB／pytest／AST 非我以為)· #1(隔離)· #29(個別可執行＋矩陣)· R6 計畫 §4 S1–S2。

執行指令矩陣:
  python scripts/verify_roadmap_r6_s12.py              # 印矩陣＋跑 --check(A1–A5,A7,A8,A10;不含 A6 煙測)
  python scripts/verify_roadmap_r6_s12.py --check      # 同上唯讀哨兵(零外部 knowledge 放量)
  python scripts/verify_roadmap_r6_s12.py --with-smoke # --check 後再跑 e2e 煙測(A6;本機 sentinel)
  python scripts/verify_roadmap_r6_s12.py --json       # 機器可讀(exit 0=近程 A* 綠;A9 永不由此綠)
  python scripts/verify_roadmap_r6_s12.py --selftest   # 純紅綠自測(免 DB 免 API)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

# S1 終態詞彙鎖(供 U6 攻擊;與計畫 §4 對齊——改此須同步計畫/閉合 audit,[I] 不改 [N])
TERMINAL_VOCAB = {
    "harvest_complete": (
        "達該 item license 允許之最終可檢索態:"
        "有全文→sentences→(scope 啟用則)embed;"
        "或無授權全文→metadata＋knowledge_fulltext_status 終態列"
    ),
    "answerable": "advisor 檢索路徑能對該內容產出 guard 通過之引用(或誠實固定句);owned_local 僅本機",
    "blocked": "license／OA／resolver 阻擋已落帳於 knowledge_fulltext_status(≠漏做、≠未嘗試)",
    "forbidden": "僅 title／staging pending／metadata 有列 稱 harvest 完成或可答;外部雲端 LLM",
}

# A3:肯定性半套宣稱——「僅 metadata＝完成／可答」(排除禁令／風險名／攻擊焦點)
# 風險表列「| metadata 當可答 | …緩解…」不是宣稱,不計入。
_A3_PAT = re.compile(
    r"(僅\s*metadata.{0,24}(完成|可答)|"
    r"metadata[\s\-]*only.{0,24}(complete|answerable|完成|可答)|"
    r"止於\s*metadata.{0,12}(完成|可答|harvest)|"
    r"metadata\s*[＝=]\s*(harvest\s*)?完成|"
    r"metadata\s*[＝=]\s*可答|"
    r"metadata\s*當\s*(答案|可答).{0,8}(完成|宣稱|即))",
    re.I,
)
_A3_NEG = re.compile(
    r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
    r"半套|不得只抓|不得謊稱|非止於|≠可答|誠實|"
    r"零「|抽樣無|無半套|哨兵掃)"  # 閉合／審計敘述「點名禁句≠自稱完成」
)
_A3_SCOPE = [
    REPO / "HANDOFF.md",
    REPO / "reports" / "augur_constitution_to_implementation_roadmap_20260724.md",
    REPO / "reports" / "augur_roadmap_r6_plan_20260724.md",
    REPO / "reports" / "augur_roadmap_r3_gap_ledger_20260724.md",
]


def _row(aid: str, status: str, detail: str) -> dict:
    return {"id": aid, "status": status, "detail": detail}


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("TERMINAL_VOCAB 四鍵", set(TERMINAL_VOCAB) >= {"harvest_complete", "answerable", "blocked", "forbidden"})
    chk("禁半套句在 forbidden", "metadata" in TERMINAL_VOCAB["forbidden"])
    # A3:風險名不命中;肯定半套命中
    risk = "| metadata 當可答 | A3＋U6＋fulltext_status | 完成句無終態證據 |"
    chk("A3 風險列不誤抓", not bool(_A3_PAT.search(risk)))
    claim = "本輪 harvest 完成＝僅 metadata 即可答"
    chk("A3 肯定半套可抓", bool(_A3_PAT.search(claim) and not _A3_NEG.search(claim)))
    audit = "哨兵掃 Gap：零「僅 metadata＝完成／可答」肯定宣稱"
    chk("A3 審計點名禁句不誤抓",
        not (_A3_PAT.search(audit) and not _A3_NEG.search(audit)))
    chk("矩陣字串在 docstring", "執行指令矩陣" in (__doc__ or ""))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _a1(cur) -> dict:
    cur.execute(
        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid='knowledge_item_text'::regclass AND contype='c' "
        "AND (conname=%s OR pg_get_constraintdef(oid) LIKE %s)",
        ("chk_itext_owned_local_private", "%owned_local%"),
    )
    rows = cur.fetchall()
    hit = any(
        r[0] == "chk_itext_owned_local_private" and "local_private" in (r[1] or "")
        for r in rows
    )
    return _row("A1", "PASS" if hit else "FAIL",
                f"chk_itext_owned_local_private={'yes' if hit else 'no'} n={len(rows)}")


def _a2(cur) -> dict:
    cur.execute("SELECT to_regclass('knowledge_fulltext_status') IS NOT NULL")
    exists = bool(cur.fetchone()[0])
    cur.execute(
        "SELECT count(*) FROM pg_constraint "
        "WHERE conrelid='knowledge_fulltext_status'::regclass AND contype='c' "
        "AND pg_get_constraintdef(oid) LIKE %s",
        ("%status%",),
    )
    n_chk = cur.fetchone()[0] if exists else 0
    ok = exists and n_chk >= 1
    return _row("A2", "PASS" if ok else "FAIL",
                f"table={exists} status_check_n={n_chk}")


def _a3() -> dict:
    bad = []
    for p in _A3_SCOPE:
        if not p.is_file():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not _A3_PAT.search(line):
                continue
            if _A3_NEG.search(line):
                continue
            bad.append(f"{p.relative_to(REPO)}:{i}")
    # audits 近期 R6 閉合／計畫檔抽樣
    for p in sorted((REPO / "audits").glob("ROADMAP-R6*.md")):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if _A3_PAT.search(line) and not _A3_NEG.search(line):
                bad.append(f"{p.relative_to(REPO)}:{i}")
    return _row("A3", "PASS" if not bad else "FAIL",
                "零半套完成宣稱" if not bad else f"hits={bad[:8]}")


def _a4() -> dict:
    r = subprocess.run(
        [PY, "-m", "pytest", "tests/test_philosophy_isolation.py", "-q", "--tb=line"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    out = (r.stdout + r.stderr)[-400:]
    ok = r.returncode == 0 and "passed" in out
    return _row("A4", "PASS" if ok else "FAIL", out.replace("\n", " ")[-200:])


def _a5(cur) -> dict:
    from augur.core import config
    app_u = config.DB_PARAMS.get("user")
    pred_u = config.DB_PARAMS_PREDICT.get("user")
    role_ok = app_u != "augur_predict" and pred_u == "augur_predict"
    cur.execute("SELECT current_user")
    sess = cur.fetchone()[0]
    sess_ok = sess != "augur_predict"
    # predict 對素養 SELECT＝false(抽樣)
    denied = 0
    checked = 0
    for t in ("knowledge_item", "philosophy_work", "knowledge_sentence"):
        cur.execute("SELECT to_regclass(%s)", (t,))
        if cur.fetchone()[0] is None:
            continue
        cur.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", ("augur_predict", f'"{t}"'))
        got = cur.fetchone()[0]
        checked += 1
        if got is False:
            denied += 1
    priv_ok = checked >= 2 and denied == checked
    ok = role_ok and sess_ok and priv_ok
    return _row(
        "A5", "PASS" if ok else "FAIL",
        f"app_ne_predict={role_ok} sess_ne_predict={sess_ok} "
        f"predict_denied={denied}/{checked}",
    )


def _a7() -> dict:
    from augur.advisor import ollama
    src = (REPO / "scripts" / "serve_advisor_openai.py").read_text(encoding="utf-8")
    wire_ok = "ollama" in src and "openai.OpenAI" not in src and "Anthropic" not in src
    reject_ok = False
    try:
        ollama._assert_local_host("https://api.openai.com/v1")
    except RuntimeError:
        reject_ok = True
    st = subprocess.run(
        [PY, "-m", "augur.advisor.ollama", "--selftest"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    ok = wire_ok and reject_ok and st.returncode == 0
    return _row("A7", "PASS" if ok else "FAIL",
                f"wire_local={wire_ok} reject_public={reject_ok} ollama_selftest={st.returncode==0}")


def _a8() -> dict:
    r = subprocess.run(
        ["bash", "-lc", "pgrep -af 'sync_finmind|ingestion.finmind|fred_series' 2>/dev/null | grep -v grep || true"],
        capture_output=True, text=True,
    )
    lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    # 本哨兵自身可能出現在 pgrep——過濾
    lines = [ln for ln in lines if "verify_roadmap_r6_s12" not in ln]
    ok = len(lines) == 0
    return _row("A8", "PASS" if ok else "FAIL",
                "無 FinMind／FRED 放量進程" if ok else f"procs={lines[:3]}")


def _a10() -> dict:
    ledger = (REPO / "reports" / "augur_roadmap_r3_gap_ledger_20260724.md").read_text(encoding="utf-8")
    line = next((ln for ln in ledger.splitlines() if ln.startswith("| G-KDO-1")), "")
    ok = "calendar" in line.lower() or "DEFER" in line
    # 維持 none 列不得被偷改成「R6 已關」之類——只確認仍為 calendar
    g_iso = next((ln for ln in ledger.splitlines() if ln.startswith("| G-ISO-1")), "")
    g_ft = next((ln for ln in ledger.splitlines() if ln.startswith("| G-FT-1")), "")
    maintain = "**none**" in g_iso and "**none**" in g_ft
    return _row("A10", "PASS" if ok and maintain else "FAIL",
                f"G-KDO-1_calendar={ok} G-ISO-1/G-FT-1_none={maintain}")


def _a6_smoke() -> dict:
    r = subprocess.run(
        [PY, "-u", str(REPO / "scripts" / "verify_knowledge_e2e_smoke.py"), "--run", "--json"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    blob = (r.stdout or "") + (r.stderr or "")
    parsed = None
    for line in reversed(blob.splitlines()):
        line = line.strip()
        if line.startswith("{") and '"pass"' in line:
            try:
                parsed = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if parsed is not None:
        ok = bool(parsed.get("pass")) and r.returncode == 0
        failed = [c.get("check") for c in (parsed.get("checks") or []) if not c.get("ok")]
        detail = "e2e pass" if ok else f"failed={failed[:4]} rc={r.returncode}"
    else:
        ok = r.returncode == 0 and "PASS(暢通)" in blob
        detail = blob.replace("\n", " ")[-240:] if not ok else "e2e pass(no json)"
    return _row("A6", "PASS" if ok else "FAIL", detail)

def run_check(*, with_smoke: bool) -> list[dict]:
    from augur.core import db

    rows: list[dict] = []
    with db.connect() as conn:
        with conn.cursor() as cur:
            rows.append(_a1(cur))
            rows.append(_a2(cur))
            rows.append(_a5(cur))
    rows.append(_a3())
    rows.append(_a4())
    rows.append(_a7())
    rows.append(_a8())
    rows.append(_a10())
    # A9 永不由此腳本 PASS——明示 SKIP
    rows.append(_row("A9", "SKIP", "U6 另授權;本哨兵不自動開 U6／不稱可答完備"))
    if with_smoke:
        rows.append(_a6_smoke())
    else:
        rows.append(_row("A6", "SKIP", "未傳 --with-smoke;請另跑或加旗標"))
    # 穩定排序
    order = {f"A{i}": i for i in range(1, 11)}
    rows.sort(key=lambda r: order.get(r["id"], 99))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--with-smoke", action="store_true")
    ap.add_argument("--json", dest="as_json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    args, _ = ap.parse_known_args(argv)

    if args.selftest:
        return _selftest()
    if args.help:
        print((__doc__ or "").strip())
        return 0

    # 無參數／--check／--json／--with-smoke：印詞彙＋跑哨兵(安全預設=不放量;煙測另旗)
    if not args.as_json:
        matrix = (__doc__ or "").split("執行指令矩陣:", 1)
        if len(matrix) > 1:
            print("執行指令矩陣:" + matrix[1].split("守 #", 1)[0].rstrip())
        print("TERMINAL_VOCAB:")
        for k, v in TERMINAL_VOCAB.items():
            print(f"  {k}: {v}")

    rows = run_check(with_smoke=args.with_smoke)
    hard = [r for r in rows if r["status"] == "FAIL"]
    # 近程哨兵綠＝A1–A5,A7,A8,A10 PASS;A6 僅 --with-smoke 計入;A9 永 SKIP
    required = {"A1", "A2", "A3", "A4", "A5", "A7", "A8", "A10"}
    if args.with_smoke:
        required.add("A6")
    req_rows = [r for r in rows if r["id"] in required]
    ok = all(r["status"] == "PASS" for r in req_rows) and not hard

    if args.as_json:
        print(json.dumps({"pass": ok, "vocab": TERMINAL_VOCAB, "checks": rows}, ensure_ascii=False))
    else:
        for r in rows:
            icon = {"PASS": "✓", "FAIL": "✗", "SKIP": "○"}.get(r["status"], "?")
            print(f"  {icon} {r['id']} {r['status']}: {r['detail']}")
        print(f"═> {'PASS(R6-E12 哨兵)' if ok else 'FAIL'}  required={sorted(required)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
