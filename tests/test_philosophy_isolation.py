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


# 對話歷史隔離〔chat-history DB,2026-07-05 三鏡對抗審查:isolation 鏡 critical〕:
# chat 表/API 是對話原文,禁被預測管線【或 core】以【字串拼 SQL】觸及(import 稽核看不到 raw SQL)。
CHAT_LITERALS = ("chat_session", "chat_message", "chat_history", "append_message", "load_messages")
_SCRIPTS = _ROOT.parent.parent / "scripts"


def _string_refs(dirs, literals):
    out = []
    for d in dirs:
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            txt = py.read_text(encoding="utf-8")
            for lit in literals:
                if lit in txt:
                    out.append(f"{py.relative_to(_ROOT.parent.parent)} → 字面 '{lit}'")
    return out


def test_pipeline_and_core_have_no_chat_table_reference():
    """預測管線 + core 禁字面引用 chat 表/API(對話原文禁進預測管線/當特徵;三鏡 critical、字串旁路)。"""
    v = _string_refs([_ROOT / p for p in SCAN_STR], CHAT_LITERALS)
    assert not v, "預測管線/core 違反對話歷史隔離(字面引用 chat 表/API＝對話→預測旁路):\n" + "\n".join(v)


def test_scripts_importing_prediction_do_not_touch_chat_or_rbac():
    """scripts/ 之【匯入預測 package 者】禁字面觸及 chat/RBAC 表——擋『預測批次腳本 JOIN chat_message/授權表』
    之洩漏面(scripts/ 合法 import 素養層之 UI 腳本不受此限,僅 import 預測 package 者受檢);三鏡 critical。"""
    predict = tuple("augur." + p for p in PIPELINE)
    bad = []
    for py in (_SCRIPTS.rglob("*.py") if _SCRIPTS.exists() else []):
        txt = py.read_text(encoding="utf-8")
        try:
            tree = ast.parse(txt)
        except SyntaxError:
            continue
        imports_predict = False
        for node in ast.walk(tree):
            mods = ([n.name for n in node.names] if isinstance(node, ast.Import)
                    else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            if any(m == p or m.startswith(p + ".") for m in mods for p in predict):
                imports_predict = True
                break
        if imports_predict:
            for lit in (RBAC_LITERALS + CHAT_LITERALS):
                if lit in txt:
                    bad.append(f"scripts/{py.name} → import 預測 package 又字面觸及 '{lit}'")
    assert not bad, "scripts/ 預測批次腳本觸及 chat/RBAC 表(洩漏面):\n" + "\n".join(bad)


def test_chat_history_lives_in_advisor_not_core():
    """對話歷史模組必住 augur.advisor(FORBIDDEN 前綴、預測零 import),絕不在 augur.core(對照 resolver 釘法;三鏡 high)。"""
    ch = _ROOT / "advisor" / "chat_history.py"
    assert ch.exists(), "chat_history 應住 src/augur/advisor/chat_history.py(FORBIDDEN 前綴、預測管線零 import)"
    assert ("augur." + ch.parent.name) in FORBIDDEN
    core = _ROOT / "core"
    if core.exists():
        for py in core.rglob("*.py"):
            t = py.read_text(encoding="utf-8")
            assert "append_message" not in t and "chat_message" not in t, \
                f"對話歷史 API/表誤置 augur.core({py.name})＝開對話→預測旁路"


if __name__ == "__main__":
    v = _violations() + _rbac_string_refs() + _string_refs([_ROOT / p for p in SCAN_STR], CHAT_LITERALS)
    if v:
        print("❌ 違反隔離不變式:\n" + "\n".join(v))
        raise SystemExit(1)
    print(f"✓ 隔離不變式通過:{' / '.join(PIPELINE)} 零 import 素養層 + 預測/core 零 RBAC/chat 字面 + resolver/chat_history 住對位")
