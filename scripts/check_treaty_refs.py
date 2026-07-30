#!/usr/bin/env python3
"""🎯 治權檔交叉引用稽核器——查「指到不存在的治權檔／連到已被取代之版本／現況宣告行落後／SUPERSEDED 指向幽靈版」四類缺陷。

守原則 #10（可溯源：斷掉的引用＝斷掉的溯源鏈）、#12（單一權威家：版本行不得與現存檔案打架）。

起因（2026-07-30）：大憲章 v1.47→v1.48→v1.49 之末段為檔案改名，致 v1.48.0 檔案不存在，
而 README／HANDOFF／v1.47 橫幅／CS-v1.48 共 5 處仍指向它，全靠人眼才發現。本 lint 把該類缺陷機械化。

執行指令矩陣
------------
    python3 scripts/check_treaty_refs.py                # 全掃（唯讀、預設）；有缺陷 exit 1
    python3 scripts/check_treaty_refs.py --json         # 機器可讀（CI／pre-commit）
    python3 scripts/check_treaty_refs.py --selftest     # 紅綠自測（免 DB 免 API 免網路）
    python3 scripts/check_treaty_refs.py --root /path   # 指定 repo 根（預設由本檔位置推得）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

# 掃描範圍：治權入口與領域治權檔（live），不含 reports/（史料引用容許指向舊 repo）
SCAN_GLOBS = (
    "README.md",
    "HANDOFF.md",
    "HANDOFF-governance.md",
    "CLAUDE.md",
    "ARCHITECTURE-OVERVIEW.md",
    "GROUNDING-MAP.md",
    "docs/*.md",
    "docs/compliance/*.md",
    "constitution/GOVERNANCE*.md",
    "specs/*-SPECIFICATION.md",
)
# markdown link 或 backtick 路徑；只收治權三目錄
REF_RE = re.compile(r"(?:\]\(|`)((?:docs|constitution|specs)/[^`)\s]+\.md)(?:\)|`)")
# 散文通配符／史料標記：不算缺陷
GLOB_CHARS = ("*", "{", "<", "?")
LEGACY_MARKERS = ("舊 ", "舊`", "原獨立倉", "史料")
# 現況宣告站點之結構訊號（非策展資料）——只有這些行的版本號被視為「指標」而非史述
STATUS_MARKERS = ("治權已立", "現行版", "判準/憲法")
# 版本化治權檔家族：檔名前綴 → 用於「版本行是否落後」比對
VERSIONED_FAMILIES = ("系統核心思想", "原則精華", "系統架構大憲章")
VER_RE = re.compile(r"^(?P<stem>.+?)_v(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pat>\d+)\.md$")


@dataclass
class Finding:
    kind: str  # dead_ref | link_to_superseded | status_line_stale | dead_superseded
    file: str
    line: int
    detail: str

    def render(self) -> str:
        return f"[{self.kind}] {self.file}:{self.line} — {self.detail}"


def _iter_files(root: Path):
    for pat in SCAN_GLOBS:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                yield p


def _is_ignorable(ref: str, line_text: str) -> bool:
    if any(c in ref for c in GLOB_CHARS):
        return True
    return any(m in line_text for m in LEGACY_MARKERS)


def scan_dead_refs(root: Path) -> list[Finding]:
    """被引用之治權檔路徑不存在（排除散文通配符與明標史料者）。"""
    out: list[Finding] = []
    for path in _iter_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, text in enumerate(lines, 1):
            for ref in REF_RE.findall(text):
                if _is_ignorable(ref, text):
                    continue
                if not (root / ref).exists():
                    out.append(Finding("dead_ref", str(path.relative_to(root)), i, f"引用不存在之治權檔 `{ref}`"))
    return out


def current_versions(root: Path) -> dict[str, tuple[int, int, int]]:
    """各版本化家族於 docs/ 之現存最高版（非 SUPERSEDED 者優先；同版取最高號）。"""
    best: dict[str, tuple[int, int, int]] = {}
    for p in sorted((root / "docs").glob("*.md")):
        m = VER_RE.match(p.name)
        if not m:
            continue
        stem = m.group("stem")
        if stem not in VERSIONED_FAMILIES:
            continue
        head = p.read_text(encoding="utf-8")[:600]
        if "SUPERSEDED" in head:
            continue
        ver = (int(m.group("maj")), int(m.group("min")), int(m.group("pat")))
        if ver > best.get(stem, (-1, -1, -1)):
            best[stem] = ver
    return best


def check_version_lines(root: Path) -> list[Finding]:
    """兩類無歧義之版本缺陷。

    刻意**不**掃散文中的版本提及——「G1-G5 已完成（那次升到 v1.9.1）」「升版落在 commit X」
    是合法史述，非過期指標；行級啟發式無法可靠區分（長行同時含史述與現況），故只查：
      (1) link_to_superseded：入口檔連到檔頭自宣 SUPERSEDED 之治權檔（客觀可判）。
      (2) status_line_stale：帶現況宣告標記（`治權已立`／`現行版`）之行，其版本號低於現行版。
    STATUS_MARKERS 為結構訊號（宣告站點）而非策展資料，故留在 code（同 guard 詞表之裁）。
    """
    cur = current_versions(root)
    out: list[Finding] = []
    entries = [root / "README.md", root / "HANDOFF.md", root / "HANDOFF-governance.md"]
    superseded_files = {
        p.name for p in (root / "docs").glob("*.md") if "SUPERSEDED" in p.read_text(encoding="utf-8")[:600]
    }
    for path in entries:
        if not path.exists():
            continue
        for i, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(m in text for m in LEGACY_MARKERS):
                continue
            for ref in REF_RE.findall(text):
                name = os.path.basename(ref)
                if name in superseded_files and name not in path.name:
                    out.append(
                        Finding("link_to_superseded", str(path.relative_to(root)), i, f"連到已被取代之治權檔 `{ref}`")
                    )
            if not any(m in text for m in STATUS_MARKERS):
                continue
            for stem, (maj, mnr, pat) in cur.items():
                for m in re.finditer(re.escape(stem) + r"[^\n]{0,20}?v(\d+)\.(\d+)\.(\d+)", text):
                    got = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    if got < (maj, mnr, pat):
                        out.append(
                            Finding(
                                "status_line_stale",
                                str(path.relative_to(root)),
                                i,
                                f"現況宣告行之 {stem} 為 v{got[0]}.{got[1]}.{got[2]}，現行為 v{maj}.{mnr}.{pat}",
                            )
                        )
    return out


def check_superseded_banners(root: Path) -> list[Finding]:
    """SUPERSEDED 橫幅所指之後繼檔必須存在（幽靈版偵測）。"""
    out: list[Finding] = []
    for p in sorted((root / "docs").glob("*.md")):
        head = p.read_text(encoding="utf-8")[:1500]
        if "SUPERSEDED" not in head:
            continue
        banner_line = next((i for i, t in enumerate(head.splitlines(), 1) if "SUPERSEDED" in t), 1)
        seg = head[head.index("SUPERSEDED"):][:500]
        for ref in re.findall(r"\]\(([^)\s]+\.md)\)", seg):
            target = (p.parent / ref) if not ref.startswith(("docs/", "constitution/", "specs/")) else (root / ref)
            if not target.exists():
                out.append(
                    Finding("dead_superseded", str(p.relative_to(root)), banner_line, f"SUPERSEDED 指向不存在之後繼檔 `{ref}`")
                )
    return out


def run_all(root: Path) -> list[Finding]:
    return scan_dead_refs(root) + check_version_lines(root) + check_superseded_banners(root)


def _selftest() -> int:
    """四類缺陷各造一例，驗證均被抓到；再驗乾淨樹全綠、史料標記豁免。"""
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs").mkdir()
        (root / "docs" / "原則精華_v1.2.0.md").write_text("# 原則精華 v1.2.0\n本文\n", encoding="utf-8")
        (root / "docs" / "原則精華_v1.1.0.md").write_text(
            "# 原則精華 v1.1.0\n> **SUPERSEDED**：已被 [`原則精華_v9.9.9.md`](原則精華_v9.9.9.md) 取代。\n", encoding="utf-8"
        )
        (root / "README.md").write_text(
            "見 [`docs/不存在的檔.md`](docs/不存在的檔.md)\n"
            "治權已立（原則精華 v1.1.0）\n"
            "表：[`docs/原則精華_v1.1.0.md`](docs/原則精華_v1.1.0.md)\n",
            encoding="utf-8",
        )
        got = {f.kind for f in run_all(root)}
        for kind in ("dead_ref", "status_line_stale", "dead_superseded", "link_to_superseded"):
            if kind not in got:
                fails.append(f"應抓到 {kind} 但未抓到（實得 {sorted(got)}）")
        # 乾淨樹：修好後應全綠
        (root / "docs" / "原則精華_v9.9.9.md").write_text("# 原則精華 v9.9.9\n", encoding="utf-8")
        (root / "docs" / "存在的檔.md").write_text("x\n", encoding="utf-8")
        (root / "README.md").write_text(
            "見 [`docs/存在的檔.md`](docs/存在的檔.md)\n治權已立（原則精華 v9.9.9）\n", encoding="utf-8"
        )
        clean = run_all(root)
        if clean:
            fails.append(f"乾淨樹應 0 缺陷，實得 {[f.render() for f in clean]}")
        # 史料標記豁免
        (root / "README.md").write_text("見 舊 [`docs/已搬走.md`](docs/已搬走.md)\n", encoding="utf-8")
        if scan_dead_refs(root):
            fails.append("史料標記（舊）應豁免，卻被判缺陷")
    for f in fails:
        print(f"FAIL {f}")
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="治權檔交叉引用稽核器（唯讀、零外部依賴）")
    ap.add_argument("--root", default=None, help="repo 根目錄（預設由本檔位置推得）")
    ap.add_argument("--json", action="store_true", help="機器可讀輸出")
    ap.add_argument("--selftest", action="store_true", help="紅綠自測（免 DB 免 API）")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    findings = run_all(root)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        if not findings:
            print(f"治權引用稽核：全綠（root={root}）")
        else:
            print(f"治權引用稽核：{len(findings)} 則缺陷（root={root}）")
            for f in findings:
                print("  " + f.render())
    return 1 if findings else 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip() if "執行指令矩陣" in __doc__ else "")
        print("--- 無參數＝跑全掃（唯讀）---")
    sys.exit(main())
