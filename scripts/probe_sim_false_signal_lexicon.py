#!/usr/bin/env python3
"""🎯 FP-A 假兆詞探針——揪 sim 敘事裡的裸「可交易／確立級」宣稱。

白話:把校準綠／判決綠寫成「可交易」或「確立級」＝敘事假兆（P1-3 FP-A）。
  本支只做純函式＋檔面掃描；零 DB、永不 acquire heavy_slot、不 --apply、不碰 evolution。
  否定位白名單＝設計允許之「≠可交易／禁確立級」等前綴（見 NEGATION_PREFIXES）。

守原則 #15 · #28 · #29a/d · #32a · #35（真輸入／先驗紅／禁字面當唯一鎖）。

執行指令矩陣
------------
    python3 scripts/probe_sim_false_signal_lexicon.py              # 無參數＝印矩陣（graceful；rc=0）
    python3 scripts/probe_sim_false_signal_lexicon.py --help
    python3 scripts/probe_sim_false_signal_lexicon.py --selftest   # 零 DB：綠向＋先驗紅；壞偵測器必紅
    python3 scripts/probe_sim_false_signal_lexicon.py --check PATH [PATH ...]
    python3 scripts/probe_sim_false_signal_lexicon.py --text '…'   # 單字串掃描；有裸宣稱 → rc=1
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import _bootstrap  # noqa: F401

PROBE_ID = "FP-A"
CLAIM_TERMS = ("可交易", "確立級")

# 設計允許之否定位：緊貼宣稱詞左側（可夾空白）之否定前綴。
NEGATION_PREFIXES = (
    "≠",
    "禁",
    "非",
    "不是",
    "不得宣稱",
    "不得主張",
    "不得寫成",
    "嚴禁",
    "禁止",
)

# 掃描預設（設計 §4.2）；僅在 --check 且未給 PATH 時啟用。
DEFAULT_GLOBS = (
    "reports/*sim*",
    "reports/*SIM*",
    "audits/OPT-SIM*",
)


@dataclass(frozen=True)
class ClaimHit:
    term: str
    start: int
    end: int
    context: str


def _is_negated(text: str, start: int) -> bool:
    """宣稱詞左側是否緊貼允許之否定位前綴。純函式。"""
    left = text[:start].rstrip()
    # 最長前綴優先，避免「禁」搶「嚴禁」
    for pref in sorted(NEGATION_PREFIXES, key=len, reverse=True):
        if left.endswith(pref):
            return True
    return False


def find_bare_claims(text: str) -> list[ClaimHit]:
    """找出非否定位之裸宣稱詞出現處。純函式——selftest 以真句餵入。"""
    if not text:
        return []
    hits: list[ClaimHit] = []
    for term in CLAIM_TERMS:
        start = 0
        while True:
            i = text.find(term, start)
            if i < 0:
                break
            if not _is_negated(text, i):
                lo = max(0, i - 24)
                hi = min(len(text), i + len(term) + 24)
                ctx = text[lo:hi].replace("\n", " ")
                hits.append(ClaimHit(term=term, start=i, end=i + len(term), context=ctx))
            start = i + len(term)
    return hits


def scan_text(label: str, text: str) -> list[tuple[str, ClaimHit]]:
    """回 [(label, hit), ...]。純函式包裝。"""
    return [(label, h) for h in find_bare_claims(text)]


def scan_paths(paths: list[Path]) -> list[tuple[str, ClaimHit]]:
    """讀檔掃描；缺檔略過並列印警告。非 DB。"""
    out: list[tuple[str, ClaimHit]] = []
    for p in paths:
        if not p.is_file():
            print(f"  ! skip non-file: {p}", file=sys.stderr)
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"  ! skip unreadable {p}: {e}", file=sys.stderr)
            continue
        rel = str(p)
        out.extend(scan_text(rel, text))
    return out


def default_scan_targets(root: Path) -> list[Path]:
    """設計預設 glob → 檔列表（去重、排序）。"""
    found: set[Path] = set()
    for g in DEFAULT_GLOBS:
        found.update(root.glob(g))
    return sorted(p for p in found if p.is_file())


def _print_matrix() -> int:
    doc = __doc__ or ""
    marker = "執行指令矩陣"
    if marker in doc:
        print(doc.split(marker, 1)[1].strip())
    else:
        print(doc)
    print(f"\nprobe_id={PROBE_ID}  terms={list(CLAIM_TERMS)}  (零 DB／禁 acquire)")
    return 0


def _selftest() -> int:
    """零 DB 紅綠自測；含 #35 先驗紅（壞句必揪、壞偵測器不得安靜綠）。"""
    ok = True
    red_evidence: list[str] = []

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # ── 綠向：否定位／潔淨句不得命中 ──
    green_cases = (
        "sim 校準≠可交易≠確立級（TABOO）",
        "本探針禁確立級裸宣稱",
        "嚴禁可交易偷渡入報告",
        "今天天氣晴，無宣稱詞",
        "settle 待結算 0 列，K=0/3",
    )
    for s in green_cases:
        chk(f"綠：無裸宣稱 ← {s[:28]}", find_bare_claims(s) == [])

    # ── 先驗紅證（#35）：設計指定壞句必被揪 ──
    bad = "sim 校準通過故可交易"
    bad_hits = find_bare_claims(bad)
    chk("紅向：壞句「sim 校準通過故可交易」必有 hit", len(bad_hits) >= 1)
    chk("紅向：hit.term 為可交易", bool(bad_hits) and bad_hits[0].term == "可交易")
    red_evidence.append(
        f"fixture={bad!r} → hits={[h.term for h in bad_hits]} @starts={[h.start for h in bad_hits]}"
    )

    bad2 = "本輪已過確立級，可交易進場"
    bad2_hits = find_bare_claims(bad2)
    chk("紅向：同時裸「確立級」＋「可交易」→ ≥2 hits", len(bad2_hits) >= 2)
    red_evidence.append(
        f"fixture={bad2!r} → hits={[h.term for h in bad2_hits]}"
    )

    # ── 驗紅：偵測器被弄壞（恆回 []）→ 同句「必有 hit」條件必須失敗 ──
    def _broken(_text: str) -> list[ClaimHit]:
        return []

    broken_sees = _broken(bad)
    chk(
        "驗紅：壞偵測器對壞句回 [] → 鎖側會紅（證實機制非字面自嗨）",
        len(broken_sees) == 0 and len(bad_hits) >= 1,
    )
    # 下行＝「若我們用壞偵測器當本尊」時綠向斷言會誤綠——用對照臂證明本尊≠壞臂
    chk(
        "驗紅：本尊與壞臂對壞句結果必須不同（防安靜假綠）",
        len(bad_hits) != len(broken_sees),
    )
    red_evidence.append(
        "mutant=_broken→[] vs finder→hits；selftest 要求兩者不等（壞臂不得當綠）"
    )

    # ── 結構：業務段禁 acquire／禁 DB 熱路徑（切掉 selftest 防 #35 型 1）──
    body = Path(__file__).read_text(encoding="utf-8").split("def _selftest")[0]
    chk("不 HeavySlot／不 .acquire(", "HeavySlot" not in body and ".acquire(" not in body)
    chk("不 import augur.core.db／psycopg", "augur.core.db" not in body and "psycopg" not in body)
    chk("PROBE_ID 定錨 FP-A", PROBE_ID == "FP-A")

    print("── 先驗紅證留檔用 ──")
    for line in red_evidence:
        print(f"  · {line}")

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def _check(paths: list[str] | None, text: str | None) -> int:
    findings: list[tuple[str, ClaimHit]] = []
    if text is not None:
        findings.extend(scan_text("<stdin-text>", text))
    if paths:
        findings.extend(scan_paths([Path(p) for p in paths]))
    elif text is None:
        root = Path(__file__).resolve().parents[1]
        targets = default_scan_targets(root)
        print(f"--check default globs → {len(targets)} files")
        findings.extend(scan_paths(targets))

    if not findings:
        print(f"{PROBE_ID}: clean（無裸「可交易／確立級」）")
        return 0

    print(f"{PROBE_ID}: {len(findings)} bare-claim hit(s)")
    for label, h in findings:
        print(f"  {label}:{h.start}  term={h.term}  …{h.context}…")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="FP-A：sim 假兆詞（可交易／確立級）探針",
    )
    ap.add_argument("--selftest", action="store_true", help="零 DB 紅綠自測＋先驗紅")
    ap.add_argument("--check", action="store_true", help="掃描 PATH 或預設 glob")
    ap.add_argument("--text", type=str, default=None, help="掃描單一字串（有 hit → rc=1）")
    ap.add_argument("paths", nargs="*", help="--check 目標檔（可略＝預設 glob）")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()
    if a.check or a.text is not None or a.paths:
        return _check(a.paths or None, a.text)
    return _print_matrix()


if __name__ == "__main__":
    sys.exit(main())
