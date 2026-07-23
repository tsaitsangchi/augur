"""annex_d_range_lint — Annex D 範圍型目標列 × 各層 FM/TR 對表（DFR-4）。

依 `AUGUR-WM v1.0` Annex D D0（RULING-2026-030 §二／§五(g)）：目標 Layer 為範圍者，
範圍內每一 Layer 之規格必須於 front-matter `defers-in` 含 `WM.D{n}`，或於 Annex TR
對該列明記承接／不觸及＋理由。

執行指令矩陣：
  python -m tools.constitution_lint.annex_d_range_lint              # 印用途（唯讀）
  python -m tools.constitution_lint.annex_d_range_lint --selftest    # 對真實 corpus 紅綠自測
"""
from __future__ import annotations

import pathlib
import re

from . import compliance_lint
from .model import Finding, Severity

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WM_SPEC = _REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md"
_BASIS = "AUGUR-WM v1.0 Annex D D0（RULING-2026-030 §二／§五(g)）"

_D_TABLE_ROW = re.compile(r"^\|\s*D(\d+)\s*\|[^|]*\|\s*([^|]+?)\s*\|")
_WM_D_FM = re.compile(r"(?:WM\.)?D(\d+)")
_D_TR_HIT = re.compile(
    r"(?:WM\.D(\d+)|\*\*D(\d+)\*\*|^\|\s*(?:`[^`]+`\s+)?(?:\*\*)?D(\d+)(?:\*\*)?[（(])",
    re.M,
)
_LAYER_NUM = re.compile(r"L(\d+)")


def _expand_target_layers(target: str) -> list[int] | None:
    """解析 Annex D「目標 Layer」欄；≥2 個 distinct layer 才為範圍型。"""
    t = target.strip()
    nums = [int(m.group(1)) for m in _LAYER_NUM.finditer(t)]
    if len(nums) < 2:
        return None
    if "/" in t or "／" in t:
        return sorted(set(nums))
    if re.search(r"L\d+\s*[–—-]\s*L\d+", t):
        lo, hi = min(nums), max(nums)
        return list(range(lo, hi + 1))
    return sorted(set(nums))


def parse_annex_d_ranges(wm_path=_WM_SPEC) -> list[dict]:
    """自 WM Annex D 表解析範圍型列 → [{dn, layers, target_raw}, …]。"""
    text = pathlib.Path(wm_path).read_text(encoding="utf-8")
    start = text.find("# Annex D")
    if start < 0:
        return []
    section = text[start:]
    out = []
    for ln in section.splitlines():
        m = _D_TABLE_ROW.match(ln)
        if not m:
            continue
        dn = int(m.group(1))
        target = m.group(2)
        layers = _expand_target_layers(target)
        if layers:
            out.append({"dn": dn, "layers": layers, "target_raw": target.strip()})
    return out


def _layer_spec_map(spec_paths) -> dict[int, pathlib.Path]:
    from . import report as report_mod

    m = {}
    for p in spec_paths:
        layer = report_mod.spec_layer(p)
        if layer.startswith("L") and layer[1:].isdigit():
            m[int(layer[1:])] = p
    return m


def _parse_front_matter(text: str) -> str:
    fields, _ = compliance_lint._parse_front_matter(text)
    return (fields or {}).get("defers-in", "")


def _annex_tr_region(text: str) -> str:
    head = compliance_lint._find_annex_tr_head(text)
    if head is None:
        return ""
    lines = text.splitlines()
    start = text.count("\n", 0, head.start())
    lvl = len(re.match(r"^(#{1,6})\s+", lines[start]).group(1))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+\S", lines[j])
        if m and len(m.group(1)) <= lvl:
            end = j
            break
    return "\n".join(lines[start:end])


def _tr_d_codes(tr_region: str) -> set[int]:
    codes = set()
    for m in _D_TR_HIT.finditer(tr_region):
        for g in m.groups():
            if g:
                codes.add(int(g))
    return codes


def check_corpus(spec_paths=None, wm_path=_WM_SPEC) -> list[Finding]:
    """範圍型 D 列 × 各目標層：FM 或 TR 至少其一可盤點。"""
    if spec_paths is None:
        from . import report as report_mod

        spec_paths = report_mod.corpus_files()
    layer_files = _layer_spec_map(spec_paths)
    ranges = parse_annex_d_ranges(wm_path)
    findings: list[Finding] = []

    for row in ranges:
        dn = row["dn"]
        for layer in row["layers"]:
            spec = layer_files.get(layer)
            if spec is None:
                continue
            try:
                text = spec.read_text(encoding="utf-8")
            except OSError as e:
                findings.append(Finding(
                    "DFR-4", Severity.ERROR,
                    f"D{dn} 目標 L{layer} 無法讀取規格：{e}",
                    _BASIS, str(spec.relative_to(_REPO)), kind="annex_d_range_gap",
                ))
                continue
            fm = _parse_front_matter(text)
            fm_ok = dn in {int(x.group(1)) for x in _WM_D_FM.finditer(fm)}
            tr_ok = dn in _tr_d_codes(_annex_tr_region(text))
            if fm_ok or tr_ok:
                continue
            findings.append(Finding(
                "DFR-4", Severity.ERROR,
                f"Annex D D{dn}（目標 {row['target_raw']}）之 L{layer} slice 未登錄："
                f"front-matter 缺 WM.D{dn} 且 Annex TR 無 D{dn} 承接／不觸及列",
                _BASIS,
                f"{spec.relative_to(_REPO)}（L{layer}）",
                kind="annex_d_range_gap",
            ))
    return findings


def _selftest() -> int:
    if not _WM_SPEC.exists():
        print("annex_d_range_lint selftest: SKIP（非 repo 內執行）")
        return 0
    findings = check_corpus()
    ranges = parse_annex_d_ranges()
    ok = not findings and ranges
    print("annex_d_range_lint selftest:" + (" OK" if ok else " FAIL")
          + f"（範圍型列 {len(ranges)}；gap {len(findings)}）")
    if findings:
        for f in findings[:5]:
            print(f"  {f.format()}")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
