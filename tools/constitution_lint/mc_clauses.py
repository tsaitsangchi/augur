"""從 META-CONSTITUTION.md 枚舉 [N] 條款宇宙（供 WM.44 形式充分性覆蓋檢查）。

依 `AUGUR-MC v1.3 §0.3` 條款編號系統：PA｜P{n}.D / P{n}.W{m} / P{n}.Y / P{n}.E{m}｜EV.1–EV.12｜F1–F6，
另加 §0–§8 之 [N] 章節條款（§x.y 標 [N] 者）。

⚠ 骨架限制：本枚舉以正則抽取「可機器辨識之條款代號」，涵蓋 PA/P#.*/EV.#/F#/§x.y[N]。WM.44 要求之
「全部 [N] 條款」之完全形式枚舉（含正文散落之 MUST/MUST NOT 細目）為 phase-2 強化；故 compliance_lint
之 WM.44 覆蓋檢查以 **warning 級**報告（不誤紅已生效之 AUGUR-WM v1.0），完全強制留待嚴格枚舉就緒。
"""
from __future__ import annotations

import re

_CLAUSE_PATTERNS = [
    (re.compile(r"\bPA\b"), lambda m: "PA"),
    (re.compile(r"\bP([1-5])\.E(\d+)\b"), lambda m: f"P{m.group(1)}.E{m.group(2)}"),
    (re.compile(r"\bP([1-5])\.W(\d+)\b"), lambda m: f"P{m.group(1)}.W{m.group(2)}"),
    (re.compile(r"\bP([1-5])\.D\b"), lambda m: f"P{m.group(1)}.D"),
    (re.compile(r"\bP([1-5])\.Y\b"), lambda m: f"P{m.group(1)}.Y"),
    (re.compile(r"\bEV\.(\d+)\b"), lambda m: f"EV.{m.group(1)}"),
    (re.compile(r"\bF([1-6])\b(?!\.)"), lambda m: f"F{m.group(1)}"),
]

# [N] 章標題：`## §8 … [N]`（章級，粗顆粒）。
_SECTION_CH = re.compile(r"^#{2,4}\s+§\s?(\d+)\b[^\n]*\[N\]", re.M)
# 子條標題：`### 8.3 合規聲明…`／`### 0.6 Hierarchy Rule`（§ 與 [N] 在父章、子標題無之）→ §8.3 等母條款不再隱形（SHOULD #9）。
_SECTION_SUB = re.compile(r"^#{2,4}\s+§?\s?(\d+\.\d+)\b", re.M)


def enumerate_clauses(mc_text: str) -> set:
    """回 MC [N] 條款代號集合（骨架枚舉）：PA/P#.*/EV.#/F#、[N] 章（§n）與子條（§n.m）。"""
    clauses = set()
    for pat, fmt in _CLAUSE_PATTERNS:
        for m in pat.finditer(mc_text):
            clauses.add(fmt(m))
    for m in _SECTION_CH.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    for m in _SECTION_SUB.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    return clauses


def current_mc_version(mc_text: str) -> str:
    """抽取現行憲章版本（§0.1 版本欄）。找不到回空字串。"""
    m = re.search(r"版本[:：]\s*\**v?(\d+\.\d+)", mc_text)
    return f"v{m.group(1)}" if m else ""


def load(mc_path) -> tuple:
    """回 (clauses:set, version:str)。"""
    with open(mc_path, encoding="utf-8") as f:
        text = f.read()
    return enumerate_clauses(text), current_mc_version(text)
