#!/usr/bin/env python
"""Roadmap R7 產品閘哨兵 — G-P1–G-P10 結構／禁語／引用機械驗（R7 S1）。

🎯 這支在做什麼(白話):把 R7 計畫 §4.1 產品閘 G-P1–G-P10 釘成可對指定計畫 path
   重複跑的機械檢查——章節存在性、四判準區塊、PME-AUTO-B 引用或豁免、禁語抽樣
  （可答完備／確立級可交易／解凍暗示／一律人准上線）。欠項列清單，不靜默 PASS。
   **不做**語義「計畫夠好」之 LLM 核准（屬 U7／人裁）；**不做**產品業務實作／S2 掛接。
守 #15(裁決出檔案／regex 非我以為)· #20(plan-first)· #29(個別可執行＋矩陣)· R7 §4.1／§5 S1。

執行指令矩陣:
  python scripts/verify_roadmap_r7_gate.py                         # 印矩陣＋跑 --check-framework
  python scripts/verify_roadmap_r7_gate.py --check-framework       # S1 框架：哨兵／模板／§4.1／PME-AUTO-B
  python scripts/verify_roadmap_r7_gate.py --inventory             # S0：§4.2 產品 path 存在性
  python scripts/verify_roadmap_r7_gate.py --check --plan PATH     # 對指定計畫驗 G-P1–G-P10
  python scripts/verify_roadmap_r7_gate.py --check --plan PATH --json
  python scripts/verify_roadmap_r7_gate.py --selftest              # 純紅綠自測(免 DB 免 API)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
R7_PLAN = REPO / "reports" / "augur_roadmap_r7_plan_20260724.md"
CHECKLIST_TEMPLATE = REPO / "audits" / "ROADMAP-R7-PRODUCT-GATE-CHECKLIST-TEMPLATE.md"
ROADMAP = REPO / "reports" / "augur_constitution_to_implementation_roadmap_20260724.md"

# §4.2 活躍產品索引（與 R7 計畫對齊；改計畫表須同步此清單）
PRODUCT_INDEX: list[tuple[str, str]] = [
    ("P-ADV", "reports/augur_omniscient_advisor_plan_20260709.md"),
    ("P-SH", "reports/augur_prediction_short_horizon_model_plan_20260709.md"),
    ("P-OMNI", "reports/augur_omniscient_e2e_master_plan_20260710.md"),
    ("P-ALP", "reports/taiwan_alpha_improvement_plan_20260717.md"),
    ("P-PME", "reports/augur_philosophy_market_evolution_loop_plan_20260724.md"),
    ("P-PDF", "reports/knowledge_pdf_extraction_plan_20260712.md"),
    ("P-SOP", "reports/augur_prediction_sop_master_20260706.md"),
    ("P-ARENA", "reports/augur_direction_live_arena_plan_20260711.md"),
]

GATE_IDS = [f"G-P{i}" for i in range(1, 11)]

# 禁語：肯定性宣稱（排除禁令／風險／攻擊敘述）
_FORBIDDEN = [
    (
        "claim_answerable",
        re.compile(r"可答完備"),
        re.compile(
            r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
            r"未宣稱|不宣稱|不無.{0,16}宣稱|對外無|零出現|無「|"
            r"evaluated_pass|門柱|驗收|\bA9\b|G-P9|宣稱鎖)"
        ),
    ),
    (
        "claim_tradable",
        re.compile(r"確立級.{0,8}可交易|可交易.{0,8}確立級|確立級可交易"),
        re.compile(
            r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
            r"未宣稱|不宣稱|不無.{0,16}宣稱|對外無|零出現|無「|"
            r"evaluated_pass|門柱|驗收|\bA9\b|G-P9|宣稱鎖)"
        ),
    ),
    (
        "unfreeze_hint",
        re.compile(r"(已解凍\s*(FinMind|FRED|API)|解凍\s*(FinMind|FRED|API)\s*(完成|生效)|操作凍結\s*解除)"),
        re.compile(r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|FZ-keep|不解凍|維持凍結)"),
    ),
    (
        "human_gate_hard",
        re.compile(r"一律人准(特徵)?上線"),
        re.compile(
            r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
            r"不寫死|不\s*寫死|寫死|豁免|衝突|標記|不做|硬非目標|非目標|"
            r"否決|不採|對照|引用|對齊|G-P6)"
        ),
    ),
    # U7 F-U7-5：幽靈完備宣稱（結構綠≠PRODSET／Dividend 完備）
    (
        "claim_prodset",
        re.compile(r"生產特徵集已登錄"),
        re.compile(
            r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
            r"未|無|仍缺|partial|幽靈|未做|未真|≠可交易|philosophy\s*域|"
            r"G-PME-PRODSET|宣稱鎖|驗收)"
        ),
    ),
    (
        "claim_dividend_complete",
        re.compile(r"(Dividend\s*(特徵)?完備|股息.{0,8}完備)"),
        re.compile(
            r"(禁|不得|≠|非|不是|勿|仍禁|攻擊|FAIL|停手|禁止|緩解|風險|焦點|"
            r"未|無|仍缺|partial|PAUSED|G-DIV|凍結|宣稱鎖|驗收)"
        ),
    ),
]

_I_MARK = re.compile(r"\[I\]")
_SCHEMA = re.compile(
    r"(Table\s+schema|\(a\)\s*Table\s+schema|表\s*schema|table\s+schema|"
    r"##\s*\d+\.\s*\(a\)|##\s*.*schema)",
    re.I,
)
_PYTHON = re.compile(
    r"(\(b\)\s*Python|Python\s*程式規畫|程式規畫|##\s*\d+\.\s*\(b\)|"
    r"python\s*程式)",
    re.I,
)
_FOUR = re.compile(
    r"(執行前\s*四判準|四判準|①\s*完整|完整\s*[／/]\s*內部一致|"
    r"與現況.{0,6}一致.{0,12}可實作|G-P4)",
    re.I,
)
_NONGOAL = re.compile(r"(非目標|硬邊界|明確不做|硬非目標|不做清單)", re.I)
_PME_B = re.compile(r"PME-AUTO-B")
_EXEMPT = re.compile(r"(豁免|不適用).{0,24}(Steward|steward)|Steward.{0,24}(豁免|不適用)")
_ULTRA = re.compile(r"(ultracode|ULTRACODE|deliberate\.py|U\d\b|對抗)", re.I)
_MAJOR = re.compile(r"(Steward|major).{0,40}(治權|判準|人裁)|(假關|10-14|G-KDO)", re.I)
_CLAIM_LOCK = re.compile(
    r"(不宣稱|禁).{0,12}(確立級|可交易|可答完備)|(確立級|可交易|可答完備).{0,12}(禁|不宣稱)",
    re.I,
)
_BOUNDARY = re.compile(r"(R5|R6).{0,40}(PME|凍結|FinMind)|與\s*R5.*R6|邊界表", re.I)


def _row(aid: str, status: str, detail: str) -> dict:
    return {"id": aid, "status": status, "detail": detail}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _forbidden_hits(text: str) -> list[str]:
    hits: list[str] = []
    for name, pat, neg in _FORBIDDEN:
        for i, line in enumerate(text.splitlines(), 1):
            if pat.search(line) and not neg.search(line):
                hits.append(f"{name}@{i}:{line.strip()[:80]}")
    return hits


def check_plan(plan_path: Path) -> list[dict]:
    """對單一計畫 markdown 跑 G-P1–G-P10；欠項→FAIL，不靜默 PASS。"""
    rows: list[dict] = []
    if not plan_path.is_file():
        for gid in GATE_IDS:
            rows.append(_row(gid, "FAIL", f"plan missing: {plan_path}"))
        return rows

    text = _read(plan_path)
    try:
        rel = str(plan_path.resolve().relative_to(REPO))
    except ValueError:
        rel = str(plan_path)

    # G-P1
    ok_i = bool(_I_MARK.search(text[:4000]))
    rows.append(_row("G-P1", "PASS" if ok_i else "FAIL",
                     f"{rel} [I]={'yes' if ok_i else 'MISSING'}"))

    # G-P2
    ok_s = bool(_SCHEMA.search(text))
    rows.append(_row("G-P2", "PASS" if ok_s else "FAIL",
                     "schema 節存在" if ok_s else "欠：(a) table schema 節"))

    # G-P3
    ok_p = bool(_PYTHON.search(text))
    rows.append(_row("G-P3", "PASS" if ok_p else "FAIL",
                     "python 規畫節存在" if ok_p else "欠：(b) python 規畫節"))

    # G-P4
    ok_f = bool(_FOUR.search(text))
    rows.append(_row("G-P4", "PASS" if ok_f else "FAIL",
                     "四判準區塊可指" if ok_f else "欠：執行前四判準書面區塊"))

    # G-P5
    ok_n = bool(_NONGOAL.search(text))
    rows.append(_row("G-P5", "PASS" if ok_n else "FAIL",
                     "非目標／硬邊界節存在" if ok_n else "欠：非目標／硬邊界專節"))

    # G-P6
    has_b = bool(_PME_B.search(text))
    has_ex = bool(_EXEMPT.search(text))
    hard_hits = [
        h for h in _forbidden_hits(text) if h.startswith("human_gate_hard@")
    ]
    if hard_hits and not has_ex:
        rows.append(_row("G-P6", "FAIL", f"寫死一律人准上線且無豁免: {hard_hits[:2]}"))
    elif has_b or has_ex:
        rows.append(_row("G-P6", "PASS",
                         "PME-AUTO-B 引用" if has_b else "Steward 豁免欄可指"))
    else:
        rows.append(_row("G-P6", "FAIL", "欠：PME-AUTO-B 引用或 Steward 豁免"))

    # G-P7
    ok_u = bool(_ULTRA.search(text))
    rows.append(_row("G-P7", "PASS" if ok_u else "FAIL",
                     "ultracode／審議插入點可指" if ok_u else "欠：階段 ultracode／審議計畫"))

    # G-P8
    ok_m = bool(_MAJOR.search(text))
    rows.append(_row("G-P8", "PASS" if ok_m else "FAIL",
                     "major→Steward／禁假關可指" if ok_m else "欠：major／假關路徑明示"))

    # G-P9（含 U7：PRODSET／Dividend 完備幽靈詞）
    claim_hits = [
        h for h in _forbidden_hits(text)
        if h.startswith((
            "claim_answerable@",
            "claim_tradable@",
            "claim_prodset@",
            "claim_dividend_complete@",
        ))
    ]
    lock = bool(_CLAIM_LOCK.search(text))
    if claim_hits:
        rows.append(_row("G-P9", "FAIL", f"肯定禁語宣稱: {claim_hits[:3]}"))
    elif lock:
        rows.append(_row("G-P9", "PASS", "宣稱鎖存在且無肯定禁語"))
    else:
        rows.append(_row("G-P9", "FAIL", "欠：確立級／可答完備宣稱鎖明示"))

    # G-P10
    ok_b = bool(_BOUNDARY.search(text))
    unf = [h for h in _forbidden_hits(text) if h.startswith("unfreeze_hint@")]
    if unf:
        rows.append(_row("G-P10", "FAIL", f"解凍暗示: {unf[:2]}"))
    elif ok_b:
        rows.append(_row("G-P10", "PASS", "R5／R6／PME／凍結邊界可指"))
    else:
        rows.append(_row("G-P10", "FAIL", "欠：與 R5／R6／PME／凍結邊界表（或引用）"))

    return rows


def check_framework() -> list[dict]:
    """S1 框架驗收（A6 核心＋索引／政策引用）。"""
    rows: list[dict] = []
    script = Path(__file__).resolve()
    doc = __doc__ or ""
    rows.append(_row(
        "F1",
        "PASS" if "執行指令矩陣" in doc else "FAIL",
        "哨兵含執行指令矩陣" if "執行指令矩陣" in doc else "欠矩陣",
    ))
    rows.append(_row(
        "F2",
        "PASS" if CHECKLIST_TEMPLATE.is_file() else "FAIL",
        f"模板 {CHECKLIST_TEMPLATE.relative_to(REPO)}"
        if CHECKLIST_TEMPLATE.is_file()
        else f"欠模板 {CHECKLIST_TEMPLATE}",
    ))
    plan_ok = R7_PLAN.is_file()
    text = _read(R7_PLAN) if plan_ok else ""
    has_gates = all(f"**G-P{i}**" in text or f"G-P{i}" in text for i in range(1, 11))
    rows.append(_row(
        "F3",
        "PASS" if plan_ok and has_gates else "FAIL",
        "R7 計畫 §4.1 G-P1–G-P10 可指" if plan_ok and has_gates else "欠閘條 SSOT",
    ))
    has_b = bool(_PME_B.search(text)) if text else False
    hard = [h for h in _forbidden_hits(text) if h.startswith("human_gate_hard@")] if text else []
    rows.append(_row(
        "F4",
        "PASS" if has_b and not hard else "FAIL",
        "引用 PME-AUTO-B 且無寫死人准"
        if has_b and not hard
        else f"PME-AUTO-B={has_b} hard={hard[:2]}",
    ))
    # 產品索引至少列齊 PRODUCT_INDEX 代號
    missing_codes = [c for c, _ in PRODUCT_INDEX if c not in text] if text else [c for c, _ in PRODUCT_INDEX]
    rows.append(_row(
        "F5",
        "PASS" if not missing_codes else "FAIL",
        "§4.2 產品索引代號齊" if not missing_codes else f"欠代號 {missing_codes}",
    ))
    road_ok = ROADMAP.is_file() and "R7" in _read(ROADMAP)
    rows.append(_row(
        "F6",
        "PASS" if road_ok else "FAIL",
        "路線圖含 R7 節" if road_ok else "欠路線圖 R7",
    ))
    rows.append(_row("F7", "PASS", f"script={script.relative_to(REPO)}"))
    return rows


def inventory() -> list[dict]:
    rows: list[dict] = []
    for code, rel in PRODUCT_INDEX:
        p = REPO / rel
        rows.append(_row(
            code,
            "PASS" if p.is_file() else "FAIL",
            rel if p.is_file() else f"MISSING {rel}",
        ))
    return rows


def _print_rows(rows: list[dict], title: str) -> int:
    print(title)
    n_fail = 0
    deficits: list[str] = []
    for r in rows:
        st = r["status"]
        mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "·", "WARN": "!"}.get(st, "?")
        print(f"  {mark} {r['id']:8} {st:5}  {r['detail']}")
        if st == "FAIL":
            n_fail += 1
            deficits.append(f"{r['id']}: {r['detail']}")
    if deficits:
        print("欠項清單:")
        for d in deficits:
            print(f"  - {d}")
    print(f"結果: {'PASS' if n_fail == 0 else 'FAIL'} (fail={n_fail})")
    return 0 if n_fail == 0 else 1


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("矩陣字串在 docstring", "執行指令矩陣" in (__doc__ or ""))
    chk("GATE_IDS=10", len(GATE_IDS) == 10)
    chk("PRODUCT_INDEX≥8", len(PRODUCT_INDEX) >= 8)

    # 禁語：肯定命中、禁令不誤抓
    claim = "本產品已達可答完備狀態"
    chk("可答完備肯定可抓", bool(_FORBIDDEN[0][1].search(claim) and not _FORBIDDEN[0][2].search(claim)))
    ban = "禁可答完備宣稱（除非授權）"
    chk("可答完備禁令不誤抓", not (bool(_FORBIDDEN[0][1].search(ban)) and not _FORBIDDEN[0][2].search(ban)))

    hard = "特徵上線一律人准上線"
    chk("一律人准可抓", bool(_FORBIDDEN[3][1].search(hard) and not _FORBIDDEN[3][2].search(hard)))
    soft = "不寫死一律人准特徵上線"
    chk("不寫死人准不誤抓", not (bool(_FORBIDDEN[3][1].search(soft)) and not _FORBIDDEN[3][2].search(soft)))
    conflict = "| **寫死「一律人准特徵上線」** | 與 PME-AUTO-B 衝突 |"
    chk("衝突表列不誤抓", not (bool(_FORBIDDEN[3][1].search(conflict)) and not _FORBIDDEN[3][2].search(conflict)))

    # U7 幽靈詞：肯定可抓、禁令／≠可交易不誤抓
    by_name = {t[0]: t for t in _FORBIDDEN}
    prod_affirm = "本產品生產特徵集已登錄，可上線"
    prod_ban = "禁宣稱生產特徵集已登錄＝可交易（G-PME-PRODSET）"
    div_affirm = "本產品 Dividend 特徵完備可上線"
    div_ban = "Dividend 特徵未完備（G-DIV-1 partial／PAUSED）"
    chk(
        "PRODSET 肯定可抓",
        bool(by_name["claim_prodset"][1].search(prod_affirm)
             and not by_name["claim_prodset"][2].search(prod_affirm)),
    )
    chk(
        "PRODSET 禁令不誤抓",
        not (bool(by_name["claim_prodset"][1].search(prod_ban)
                  and not by_name["claim_prodset"][2].search(prod_ban))),
    )
    chk(
        "Dividend 完備肯定可抓",
        bool(by_name["claim_dividend_complete"][1].search(div_affirm)
             and not by_name["claim_dividend_complete"][2].search(div_affirm)),
    )
    chk(
        "Dividend 未完備不誤抓",
        not (bool(by_name["claim_dividend_complete"][1].search(div_ban)
                  and not by_name["claim_dividend_complete"][2].search(div_ban))),
    )

    # 迷你計畫 fixture
    good = """# Demo [I]
## 1. 非目標
硬邊界：不解凍。
## 5. (a) Table schema
無新表。
## 6. (b) Python 程式規畫
scripts/foo.py
執行前四判準：①完整 ②內部一致 ③與現況一致 ④可實作
上線政策引用 PME-AUTO-B。
ultracode U7；major→Steward；禁假關 10-14／G-KDO。
不宣稱確立級可交易；不宣稱可答完備。
與 R5／R6／PME／凍結邊界表見引用。
"""
    bad = """# Demo no mark
只有口頭計畫，無 schema。
一律人准特徵上線。
本輪可答完備。
"""
    ghost = """# Demo [I]
## 1. 非目標
硬邊界。
## 5. (a) Table schema
有表。
## 6. (b) Python 程式規畫
scripts/foo.py
執行前四判準：①完整 ②內部一致 ③與現況一致 ④可實作
上線政策引用 PME-AUTO-B。
ultracode U7；major→Steward；禁假關。
不宣稱確立級可交易；不宣稱可答完備。
與 R5／R6／PME／凍結邊界表見引用。
本產品生產特徵集已登錄。
本產品 Dividend 特徵完備可上線。
"""
    gr = {r["id"]: r["status"] for r in check_plan(_write_tmp(good))}
    br = {r["id"]: r["status"] for r in check_plan(_write_tmp(bad))}
    gh = {r["id"]: r["status"] for r in check_plan(_write_tmp(ghost))}
    chk("good 全 PASS", all(v == "PASS" for v in gr.values()))
    chk("bad G-P1 FAIL", br.get("G-P1") == "FAIL")
    chk("bad G-P2 FAIL", br.get("G-P2") == "FAIL")
    chk("bad G-P6 FAIL", br.get("G-P6") == "FAIL")
    chk("bad G-P9 FAIL", br.get("G-P9") == "FAIL")
    chk("ghost PRODSET/Dividend → G-P9 FAIL", gh.get("G-P9") == "FAIL")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _write_tmp(content: str) -> Path:
    import tempfile

    td = Path(tempfile.mkdtemp(prefix="r7gate_"))
    p = td / "plan.md"
    p.write_text(content, encoding="utf-8")
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="R7 產品閘 G-P1–G-P10 哨兵")
    ap.add_argument("--check", action="store_true", help="對 --plan 跑 G-P*")
    ap.add_argument("--plan", type=Path, help="計畫 markdown 路徑（相對 repo 或絕對）")
    ap.add_argument("--check-framework", action="store_true", help="S1 框架驗收")
    ap.add_argument("--inventory", action="store_true", help="S0 產品 path 盤點")
    ap.add_argument("--json", action="store_true", help="機器可讀 JSON")
    ap.add_argument("--selftest", action="store_true", help="零 DB 自測")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    # 無參：印矩陣＋框架檢查
    if not any([args.check, args.check_framework, args.inventory]):
        print((__doc__ or "").split("執行指令矩陣:")[0].strip())
        print()
        print("執行指令矩陣:")
        for ln in (__doc__ or "").splitlines():
            if ln.strip().startswith("python scripts/verify_roadmap_r7_gate"):
                print(ln)
        print()
        args.check_framework = True

    all_rows: list[dict] = []
    rc = 0

    if args.inventory:
        rows = inventory()
        all_rows.extend(rows)
        if args.json:
            pass
        else:
            rc |= _print_rows(rows, "S0 產品索引盤點:")

    if args.check_framework:
        rows = check_framework()
        all_rows.extend(rows)
        if not args.json:
            rc |= _print_rows(rows, "S1 框架驗收:")

    if args.check:
        if not args.plan:
            print("✗ --check 須搭配 --plan PATH", file=sys.stderr)
            return 2
        plan = args.plan if args.plan.is_absolute() else (REPO / args.plan)
        rows = check_plan(plan)
        all_rows.extend(rows)
        if not args.json:
            rc |= _print_rows(rows, f"G-P* 檢查 ({plan}):")

    if args.json:
        fails = sum(1 for r in all_rows if r["status"] == "FAIL")
        print(json.dumps({"rows": all_rows, "fail": fails, "ok": fails == 0},
                         ensure_ascii=False, indent=2))
        return 0 if fails == 0 else 1

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
