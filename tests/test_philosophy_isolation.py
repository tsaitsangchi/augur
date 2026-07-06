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
import pathlib

# SSOT(#12):隔離不變式邏輯住 audit 模組、本 test 只引用(不重寫);常數與掃描全自 audit 取。
from augur.audit import import_isolation as iso

# 為向後相容保留本 test 之常數別名(其他 test/工具若引用不破);權威定義在 iso.*
PIPELINE = iso.PIPELINE
FORBIDDEN = iso.FORBIDDEN
RBAC_LITERALS = iso.RBAC_LITERALS
SCAN_STR = iso.SCAN_STR
_ROOT = pathlib.Path(__file__).resolve().parent.parent / "src" / "augur"


def _violations():
    """import 稽核(SSOT＝audit 模組);回違規列。"""
    return iso._import_violations()


def test_pipeline_does_not_import_philosophy_advisor_or_knowledge():
    v = _violations()
    assert not v, "預測管線違反素養層隔離(哲學/知識不進預測管線、憲章 v1.17.0/v1.19.0):\n" + "\n".join(v)


def _rbac_string_refs():
    """RBAC 字面旁路稽核(SSOT＝audit 模組);回違規列。"""
    return iso._string_ref_violations([iso._AUGUR_ROOT / p for p in SCAN_STR], RBAC_LITERALS, "rbac")


def test_pipeline_and_core_have_no_rbac_string_reference():
    """預測管線 + augur.core 禁以字串拼 SQL 觸及授權表/resolver(擋不 import 但字串旁路;計畫 C8/§6.4-2)。"""
    v = _rbac_string_refs()
    assert not v, "預測管線/core 違反 RBAC 隔離(字面引用授權表/resolver＝知識→預測旁路面):\n" + "\n".join(v)


def test_audit_module_check_isolation_passes():
    """audit 模組總入口 check_isolation() 於現行 code 零違規(閉誠實債 c:隔離 AST 稽核已建為正式 audit 模組)。"""
    v = iso.check_isolation()
    assert not v, "augur.audit.import_isolation.check_isolation() 回違規:\n" + "\n".join(v)


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
CHAT_LITERALS = iso.CHAT_LITERALS   # SSOT＝audit 模組
_SCRIPTS = _ROOT.parent.parent / "scripts"


def _string_refs(dirs, literals):
    """字面旁路稽核(SSOT＝audit 模組;tag 隨 literals 判 chat/rbac)。"""
    tag = "chat" if literals is CHAT_LITERALS else "rbac"
    return iso._string_ref_violations(dirs, literals, tag)


def test_pipeline_and_core_have_no_chat_table_reference():
    """預測管線 + core 禁字面引用 chat 表/API(對話原文禁進預測管線/當特徵;三鏡 critical、字串旁路)。"""
    v = _string_refs([iso._AUGUR_ROOT / p for p in SCAN_STR], CHAT_LITERALS)
    assert not v, "預測管線/core 違反對話歷史隔離(字面引用 chat 表/API＝對話→預測旁路):\n" + "\n".join(v)


def test_scripts_importing_prediction_do_not_touch_chat_or_rbac():
    """scripts/ 之【匯入預測 package 者】禁字面觸及 chat/RBAC 表——擋『預測批次腳本 JOIN chat_message/授權表』
    之洩漏面(scripts/ 合法 import 素養層之 UI 腳本不受此限,僅 import 預測 package 者受檢);三鏡 critical。SSOT＝audit 模組。"""
    bad = iso._scripts_predict_leak_violations()
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
    # SSOT:直接跑 audit 模組總入口(涵蓋 import/字面/對位/scripts 全稽核)。
    raise SystemExit(iso.main())
