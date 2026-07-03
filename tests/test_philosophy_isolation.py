#!/usr/bin/env python
"""P0 治權隔離不變式 — 預測管線絕不 import philosophy/advisor/knowledge(素養層絕不進預測管線)。

🎯 把憲章「廣博哲學全文量化零價值、不進預測管線」(v1.17.0)與「多域知識素養層零量化價值、
   不進預測管線」(v1.19.0)從口號變成**可自動檢測的架構不變式**:
   features/models/universe/evaluation/ingestion/audit/catalog 任一模組 import
   `augur.philosophy` / `augur.advisor` / `augur.knowledge` = 違規 fail。
   素養/顧問層只能單向依賴預測輸出、反向零依賴。
守原則 #1(零幻像)· #8(anti-leakage)· 憲章 philosophy 邊界(v1.17.0/v1.19.0)· 學習計畫 P0(d) 隔離骨架。

用法:PYTHONPATH=src python tests/test_philosophy_isolation.py  或  pytest tests/test_philosophy_isolation.py
"""
import ast
import pathlib

# 預測管線模組(raw→feature→universe→model→validate + 橫切 audit/catalog);不含 core(共用)、philosophy(被隔離者)
PIPELINE = ("features", "models", "universe", "evaluation", "ingestion", "audit", "catalog")
FORBIDDEN = ("augur.philosophy", "augur.advisor", "augur.knowledge")
_ROOT = pathlib.Path(__file__).resolve().parent.parent / "src" / "augur"


def _violations():
    out = []
    for pkg in PIPELINE:
        d = _ROOT / pkg
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [n.name for n in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods = [node.module]
                for m in mods:
                    if any(m == f or m.startswith(f + ".") for f in FORBIDDEN):
                        out.append(f"{py.relative_to(_ROOT.parent.parent)}:{node.lineno} → import {m}")
    return out


def test_pipeline_does_not_import_philosophy_advisor_or_knowledge():
    v = _violations()
    assert not v, "預測管線違反素養層隔離(哲學/知識不進預測管線、憲章 v1.17.0/v1.19.0):\n" + "\n".join(v)


if __name__ == "__main__":
    v = _violations()
    if v:
        print("❌ 違反素養層隔離:\n" + "\n".join(v))
        raise SystemExit(1)
    print(f"✓ 隔離不變式通過:{' / '.join(PIPELINE)} 皆未 import philosophy/advisor/knowledge")
