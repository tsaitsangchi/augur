"""augur 隔離稽核 — 素養層絕不進預測管線之可執行架構不變式(audit 領域元件、#8 命門)。

🎯 這支在做什麼(白話):把治權鐵則「廣博哲學/多域知識素養層零量化價值、不進預測管線」
   (憲章 philosophy 邊界 v1.17.0/v1.19.0)從口號變成**可自動檢測的架構不變式**,並升為
   正式 audit 模組(SSOT,取代散落 test 的 ad-hoc 檢查、閉誠實債 c「隔離 AST 稽核未建」):
   - **(a) import 稽核**:預測管線 7 package(features/models/universe/evaluation/ingestion/
     audit/catalog)AST-walk 任一 import `augur.philosophy` / `augur.advisor` / `augur.knowledge`
     = 違規(素養/顧問層只能單向依賴預測輸出、反向零依賴)。
   - **(b) 字面旁路稽核**:預測管線 + `augur.core` 禁**字串拼 SQL** 觸及 RBAC 授權表/resolver
     與 chat 對話表/API;預測管線 + core + 素養層寫入者(knowledge/philosophy)禁觸及蒸餾
     staging 表 `advisor_distill_*`(界線-A:蒸餾產物零回流真兆庫;import 稽核看不到 raw SQL)。
     純預測消費者另禁產物表 `prediction_values`/`prediction_probability` 字面(G-PV-1 PV-α)。
   - **(c) 對位稽核**:resolver 必住 `augur.knowledge`、chat_history 必住 `augur.advisor`
     (FORBIDDEN 前綴、預測管線零 import),絕不誤置 `augur.core`(否則 pipeline 經 core 可達)。

乾淨 API:`check_isolation() -> list[str]`(回違規清單、空=通過);`if __name__=='__main__'`
   印結果 + exit(1 若違規)。`tests/test_philosophy_isolation.py` import 本模組為 SSOT(#12 不重複)。

守 #1(零幻像)· #8(anti-leakage、素養→預測旁路是命門)· #12(隔離邏輯唯一住此、test 引用不重寫)·
   #18(命名慣例:audit 領域元件、`import_isolation`=做什麼一看即知)· 憲章 philosophy 邊界(v1.17.0/v1.19.0)。

執行指令矩陣:
  python -m augur.audit.import_isolation      # 稽核全庫隔離不變式(0 違規→exit 0、有違規→列印+exit 1)
  python src/augur/audit/import_isolation.py  # 同上(個別可執行、#29;需先 pip install -e . 或 PYTHONPATH=src)
"""
from __future__ import annotations

import ast
import pathlib

# 預測管線模組(raw→feature→universe→model→validate + 橫切 audit/catalog);不含 core(共用)、philosophy(被隔離者)
PIPELINE = ("features", "models", "universe", "evaluation", "ingestion", "audit", "catalog")
# 素養/顧問/知識層:預測管線絕不 import(FORBIDDEN 前綴、單向依賴)
# augur.evolution(V2 Phase 2.1/I3,2026-07-26):LAIEVO 之家——預測管線 import 之=行為評測層滲入預測,同禁
FORBIDDEN = ("augur.philosophy", "augur.advisor", "augur.knowledge", "augur.evolution")
# RBAC 授權表/resolver:禁被預測管線【或 augur.core】以 import 或字串拼 SQL 觸及(知識→預測旁路面)
RBAC_LITERALS = ("app_user", "user_group", "group_domain_grant", "allowed_domains", "resolve_allowed_domains")
# chat 對話原文表/API:禁字面被預測管線/core 觸及(對話原文禁進預測管線/當特徵;import 稽核看不到 raw SQL)
CHAT_LITERALS = ("chat_session", "chat_message", "chat_history", "append_message", "load_messages")
# 蒸餾(自問自答訓練)staging 表:Claude 生的 Q&A/gold 是訓練行為樣本、**非真兆**(界線-A);
# 禁被預測管線【或 augur.core / 素養層 knowledge/philosophy writer】字面觸及——絕不成 citation、
# 不入 knowledge_*/feature_values、不進預測 7 package(計畫 §③界線-A)。
DISTILL_LITERALS = ("advisor_distill_question", "advisor_distill_context", "advisor_distill_")
# 審議引擎(本地 ultracode)工作帳:qwen 提的 claim/裁決是**審議行為樣本、非真兆**(界線-A 同構);
# 禁被預測管線/core/素養層寫入者字面觸及——絕不成 citation、不入 knowledge_*/feature_values、不進預測 7 package。
DELIB_LITERALS = ("deliberation_session", "deliberation_claim", "deliberation_verdict",
                  "deliberation_escalation", "deliberation_benchmark", "deliberation_lens", "deliberation_")
# know-how 語意橋表(K 計畫 R5):「每欄一係數」形狀=最貼近特徵表的旁路面——lexical 詞面共現非資料值相關,
# 禁被預測管線/core 以 raw SQL 字面觸及(SELECT stat_value 當特徵=違共同不變式②;素養層唯讀解讀素材)。
BRIDGE_LITERALS = ("field_term_map", "field_knowhow_lexical_affinity", "knowledge_item_term_stats")
# 被取代原值帳表(AUD-02):old_row(被取代舊值)+superseded_at(事後修正知識)落入預測回讀=WM.35 消費閘破口。
# 純預測消費者 package 禁字面觸及;合法寫入者(core/ingestion/audit——本就 SELECT/INSERT 本表)排除在掃描外。
# ⚠ 2026-07-31 單一角色整併:原與 setup_predict_role 之 DB REVOKE 成「雙閘」,該 role 已退役
#    ⇒ **本 AST/字面閘現為唯一閘**(動態 SQL 旁路不再有 DB 層攔截)。
SUPERSEDE_LITERALS = ("raw_supersede_log",)
# 身份側「事後修正知識」表(步 11 AUD-04/05/07):claim 衝突並存、lifecycle retire/redirect、attribute as-of 修正
# 版本皆屬事後認識,純預測消費者裸讀=洩漏未來修正=WM.35 消費閘破口。
# ⚠ 2026-07-31:原之 DB REVOKE 對偶已隨 augur_predict 退役 ⇒ **本閘為唯一閘**。
IDENTITY_LITERALS = ("identity_claim", "identity_lifecycle_event", "entity_attribute_version")
# 自動行動授權/留痕表(步 11 AUD-10/11):執行層記錄、與預測管線無涉;純預測消費者禁字面觸及(⚠ 2026-07-31 起 DB REVOKE 對偶已退役,本閘為唯一閘)。
ACTION_LITERALS = ("automation_action_log", "authorization_grant")
# 預測產物表(G-PV-1／PV-α)：禁被純消費側回讀當特徵(自迴圈)；合法寫入在 scripts/predict_*、顧問讀在 advisor。
# AST 字面閘對稱 SUPERSEDE；GRANT 層 REVOKE SELECT＝β（本輪未做——predict writer 仍可自讀）。
PRODUCT_LITERALS = ("prediction_values", "prediction_probability")
# LAIEVO/RAWEVO 帳本字面(V2 Phase 2.1/I3):預測管線+core 禁字面觸及 local_model_*/未來三軸 ledger——
# 行為評測樣本/pack 版本是「訓練行為樣本、非真兆」(界線-A 同構)。
# ⚠ 2026-07-31:原之 DB REVOKE 對偶已隨 augur_predict 退役 ⇒ 本閘為唯一閘。
LAIEVO_LITERALS = ("local_model_gold_sample", "local_model_version", "local_model_eval_item",
                   "local_model_eval_run", "local_model_", "local_ai_iteration", "raw_evolution_")
# 反向(I2/I5):augur.evolution 禁 import 預測管線/素養層、禁字面觸及 panel/prodset/預測產物——
# LAI 軸零寫入 feature_values/prodset/promotion_queue 之機械落點(v2 §3.1 正交矩陣)。
# 允許之家依賴=stdlib+augur.core;日後接 augur.deliberation(M-3)須同批來此開洞並附理由,不得默默相依。
EVOLUTION_SRC_FORBIDDEN_IMPORTS = ("augur.features", "augur.models", "augur.universe", "augur.evaluation",
                                   "augur.ingestion", "augur.philosophy", "augur.advisor", "augur.knowledge")
EVOLUTION_PANEL_LITERALS = ("feature_values", "feature_candidate_values", "prediction_values",
                            "promotion_queue", "evolution_production_feature_set", "TaiwanStockPrice")
PREDICT_CONSUMERS = ("features", "models", "universe", "evaluation")   # 純消費側:排除合法寫入者 core/ingestion/audit/catalog

# ── 射程補閘(2026-07-31,r2 §4 B10 收口)───────────────────────────────────────
# 病:PIPELINE 只含 7 package,`arena`/`execution`/`identity`/`deliberation` **從不在任何掃描集合內**。
# r2 實掃確認四者現況對 FORBIDDEN 零 import,但那是「**現況恰好乾淨**」而非「由構造保證」——
# 任何人日後於此四包 import 素養層,不會有任何機械紅燈。
# 急迫性來自單一角色整併(2026-07-31):`#8` 隔離之 DB 層已不存在且原理上無法重建,
# 本 AST 閘成為**唯一**防線 ⇒ 其射程外的每一個 package 都是實質缺口。
OUTER_PKGS = ("arena", "execution", "identity")
# `deliberation`：禁素養層／evolution／**advisor**（LLM 通道改走 `augur.llm`；STRUCT 斷環後不再例外）。
DELIB_FORBIDDEN = ("augur.philosophy", "augur.knowledge", "augur.evolution", "augur.advisor")
# grep-lint 面:預測管線 + core 皆禁字面引用 RBAC/chat(擋不 import 但字串旁路)
SCAN_STR = PIPELINE + ("core",)
# 蒸餾/審議表禁被觸及之範圍=預測管線 + core + 素養層寫入者(產物零回流真兆庫,界線-A)
SCAN_DISTILL = PIPELINE + ("core", "knowledge", "philosophy")

# 本檔:<root>/src/augur/audit/import_isolation.py → parents[1] = <root>/src/augur、parents[3] = <root>
_AUGUR_ROOT = pathlib.Path(__file__).resolve().parents[1]      # <root>/src/augur
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]       # <root>
_SCRIPTS = _REPO_ROOT / "scripts"
# 稽核器自身合法定義 RBAC/chat 字面為**偵測常數**(非 SQL);字面掃描須排除本檔,否則稽核器自我誤報。
_SELF = pathlib.Path(__file__).resolve()
# DDL 常數住所豁免(V2 Phase 5;同 _SELF 之理——schema 定義必然持有表名,非 SQL 存取路徑)。
# **豁免綁純度條件**:該模組一旦 import augur.core.db 或含 connect( 即失純,豁免自動作廢、恢復違規報告
# (_string_ref_violations 內檢);純常數模組拿表名=定義,帶連線的模組拿表名=存取,二者不同罪。
_DDL_HOME = (_AUGUR_ROOT / "audit" / "evolution_ledger_ddl.py").resolve()


def _is_exempt(py: pathlib.Path, txt: str) -> bool:
    p = py.resolve()
    if p == _SELF:
        return True
    if p == _DDL_HOME:
        if "augur.core" in txt or "connect(" in txt:
            return False                             # 失純=豁免作廢,照常報違規
        return True
    return False


def _rel(py: pathlib.Path) -> str:
    """把絕對路徑轉為相對 repo 根的可讀路徑(供違規訊息定位)。"""
    try:
        return str(py.relative_to(_REPO_ROOT))
    except ValueError:
        return str(py)


def _ast_import_scan(dirs, forbidden, tag, why) -> list[str]:
    """通用 AST import 掃描:dirs 下任一 .py import forbidden 前綴 → 違規列(可測性:dirs 可注入)。"""
    out = []
    for d in dirs:
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods = [n.name for n in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods = [node.module]
                else:
                    continue
                for m in mods:
                    if any(m == f or m.startswith(f + ".") for f in forbidden):
                        out.append(f"[{tag}] {_rel(py)}:{node.lineno} → import {m}({why})")
    return out


def _import_violations() -> list[str]:
    """(a) 預測管線任一 package AST import 素養層/evolution(FORBIDDEN)→ 違規列。"""
    return _ast_import_scan([_AUGUR_ROOT / p for p in PIPELINE], FORBIDDEN,
                            "import", "素養層/evolution 禁進預測管線")


def _string_ref_violations(dirs, literals, tag) -> list[str]:
    """字面掃描:dirs 下任一 .py 含 literals 任一字面 → 違規列(擋字串拼 SQL 旁路)。"""
    out = []
    for d in dirs:
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            txt = py.read_text(encoding="utf-8")
            if _is_exempt(py, txt):                      # 稽核器自身/純 DDL 住所(失純即豁免作廢)
                continue
            for lit in literals:
                if lit in txt:
                    out.append(f"[{tag}] {_rel(py)} → 字面 '{lit}'(字串拼 SQL 旁路)")
    return out


def _placement_violations() -> list[str]:
    """(c) 對位:resolver 住 augur.knowledge、chat_history 住 augur.advisor;core 不得含其 API。"""
    out = []
    core = _AUGUR_ROOT / "core"
    # resolver 對位
    access = _AUGUR_ROOT / "knowledge" / "access.py"
    if not access.exists():
        out.append("[placement] src/augur/knowledge/access.py 不存在(resolver 應住 FORBIDDEN 前綴、預測零 import)")
    if core.exists():
        for py in core.rglob("*.py"):
            t = py.read_text(encoding="utf-8")
            if "resolve_allowed_domains" in t:
                out.append(f"[placement] {_rel(py)} → resolver 誤置 augur.core(開知識→預測旁路、破 #1 命門)")
    # chat_history 對位
    ch = _AUGUR_ROOT / "advisor" / "chat_history.py"
    if not ch.exists():
        out.append("[placement] src/augur/advisor/chat_history.py 不存在(chat_history 應住 FORBIDDEN 前綴、預測零 import)")
    if core.exists():
        for py in core.rglob("*.py"):
            t = py.read_text(encoding="utf-8")
            if "append_message" in t or "chat_message" in t:
                out.append(f"[placement] {_rel(py)} → 對話歷史 API/表誤置 augur.core(開對話→預測旁路)")
    return out


def _scripts_predict_leak_violations() -> list[str]:
    """scripts/ 中【import 預測 package 者】禁字面觸及 RBAC/chat 表(擋預測批次腳本 JOIN 授權/對話表洩漏面)。
    (scripts/ 合法 import 素養層之 UI 腳本不受此限,僅 import 預測 package 者受檢。)"""
    predict = tuple("augur." + p for p in PIPELINE)
    out = []
    if not _SCRIPTS.exists():
        return out
    for py in _SCRIPTS.rglob("*.py"):
        txt = py.read_text(encoding="utf-8")
        try:
            tree = ast.parse(txt)
        except SyntaxError:
            continue
        imports_predict = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            else:
                continue
            if any(m == p or m.startswith(p + ".") for m in mods for p in predict):
                imports_predict = True
                break
        if imports_predict:
            for lit in (RBAC_LITERALS + CHAT_LITERALS):
                if lit in txt:
                    out.append(f"[scripts] scripts/{py.relative_to(_SCRIPTS)} → import 預測 package 又字面觸及 '{lit}'(洩漏面)")
    return out


def check_isolation() -> list[str]:
    """完整隔離稽核 → 違規清單(空 list=隔離成立、通過)。涵蓋 (a) import (b) 字面旁路 (c) 對位 (d) scripts 洩漏面。"""
    return (
        _import_violations()
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_STR], RBAC_LITERALS, "rbac")
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_STR], CHAT_LITERALS, "chat")
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_DISTILL], DISTILL_LITERALS, "distill")
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_DISTILL], DELIB_LITERALS, "deliberation")
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_STR], BRIDGE_LITERALS, "bridge")
        + _string_ref_violations([_AUGUR_ROOT / p for p in PREDICT_CONSUMERS], SUPERSEDE_LITERALS, "supersede")
        + _string_ref_violations([_AUGUR_ROOT / p for p in PREDICT_CONSUMERS], IDENTITY_LITERALS, "identity")
        + _string_ref_violations([_AUGUR_ROOT / p for p in PREDICT_CONSUMERS], ACTION_LITERALS, "action")
        + _string_ref_violations([_AUGUR_ROOT / p for p in PREDICT_CONSUMERS], PRODUCT_LITERALS, "product")
        # V2 Phase 2.1(I3):三重盲區補閘——LAIEVO 帳本字面(預測/core 禁觸)+evolution 反向(import+panel 字面)
        + _string_ref_violations([_AUGUR_ROOT / p for p in SCAN_STR], LAIEVO_LITERALS, "laievo")
        + _ast_import_scan([_AUGUR_ROOT / "evolution"], EVOLUTION_SRC_FORBIDDEN_IMPORTS,
                           "evolution-import", "evolution 禁 import 預測管線/素養層(I2 單向)")
        # 射程補閘(2026-07-31):四個此前不受掃之 package
        + _ast_import_scan([_AUGUR_ROOT / p for p in OUTER_PKGS], FORBIDDEN,
                           "outer-import", "arena/execution/identity 禁 import 素養層/evolution")
        + _ast_import_scan([_AUGUR_ROOT / "deliberation"], DELIB_FORBIDDEN,
                           "delib-import", "deliberation 禁 import 素養層/evolution/advisor（LLM＝augur.llm）")
        + _string_ref_violations([_AUGUR_ROOT / "evolution"], EVOLUTION_PANEL_LITERALS, "evolution-panel")
        + _placement_violations()
        + _scripts_predict_leak_violations()
    )


def main() -> int:
    v = check_isolation()
    if v:
        print("❌ 違反隔離不變式(素養層洩漏進預測管線、憲章 philosophy 邊界 v1.17.0/v1.19.0):")
        for line in v:
            print("  " + line)
        return 1
    print(f"✓ 隔離不變式通過:{' / '.join(PIPELINE)} 零 import 素養層 + 預測/core 零 RBAC/chat 字面 + "
          f"預測/core/素養層零 advisor_distill 字面(界線-A)+ 純預測消費者零 raw_supersede_log/identity(claim/"
          f"lifecycle/attribute)/action(automation/authz)/product(prediction_values|probability)字面"
          f"(WM.35＋G-PV-1 PV-α)+ "
          f"resolver/chat_history 住對位 + scripts 預測腳本零洩漏面")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
