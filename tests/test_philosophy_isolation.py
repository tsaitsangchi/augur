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
# RBAC 隔離擴充〔v1.28.0,計畫 §6.4/C8〕:授權表/resolver 禁被預測管線【或 augur.core】以 import 或【字串拼 SQL】觸及
RBAC_LITERALS = ("app_user", "user_group", "group_domain_grant", "allowed_domains", "resolve_allowed_domains")
SCAN_STR = PIPELINE + ("core",)   # grep-lint 面:預測管線 + core 皆禁字面引用 RBAC(擋不 import 但字串旁路)
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


def _rbac_string_refs():
    out = []
    for pkg in SCAN_STR:
        d = _ROOT / pkg
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            txt = py.read_text(encoding="utf-8")
            for lit in RBAC_LITERALS:
                if lit in txt:
                    out.append(f"{py.relative_to(_ROOT.parent.parent)} → RBAC 字面 '{lit}'")
    return out


def test_pipeline_and_core_have_no_rbac_string_reference():
    """預測管線 + augur.core 禁以字串拼 SQL 觸及授權表/resolver(擋不 import 但字串旁路;計畫 C8/§6.4-2)。"""
    v = _rbac_string_refs()
    assert not v, "預測管線/core 違反 RBAC 隔離(字面引用授權表/resolver＝知識→預測旁路面):\n" + "\n".join(v)


def test_rbac_resolver_lives_in_knowledge_not_core():
    """RBAC resolver 必住 augur.knowledge(FORBIDDEN 前綴)、絕不在 augur.core(否則 pipeline 經 core 可達＝破 #1;計畫 C8/§6.4-1)。"""
    access = _ROOT / "knowledge" / "access.py"
    assert access.exists(), "resolver 應住 src/augur/knowledge/access.py(FORBIDDEN 前綴、預測管線零 import)"
    assert ("augur." + access.parent.name) in FORBIDDEN
    core = _ROOT / "core"
    if core.exists():
        for py in core.rglob("*.py"):
            assert "resolve_allowed_domains" not in py.read_text(encoding="utf-8"), \
                f"resolver 誤置 augur.core({py.name})＝開知識→預測旁路、破 #1 命門"


if __name__ == "__main__":
    v = _violations() + _rbac_string_refs()
    if v:
        print("❌ 違反隔離不變式:\n" + "\n".join(v))
        raise SystemExit(1)
    print(f"✓ 隔離不變式通過:{' / '.join(PIPELINE)} 零 import 素養層 + 預測/core 零 RBAC 字面 + resolver 住 knowledge")
