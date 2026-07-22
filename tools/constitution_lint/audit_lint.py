"""audit_lint — 管「code 合憲」（骨架）：對既有/新 code 查憲章 ENFORCE 之機器可稽核不變式。

依 `AUGUR-MC v1.3 §8.3`（ENFORCE 核心不變式須可機器稽核）＋總綱 §5.4：
- 引用鏈**雙合法終點**：`K→Evidence→Observation` **∪** 明示宣告之假設（P4.E6，攜顯式標記＋P4.E4/E7 Confidence 上限）；
- Action→Identity 六元組（P5.E1）；Knowledge 五元組（P4.E1）；Confidence 存在性（P4.E1/E8）。
- 以 **AUD-01/03/10/11** 為 failing check 種子（須能重現審計 critical/major 之對應項）。

⚠ 骨架（skeleton）：本檔為**規則框架 + 可示範種子規則**。規則以輕量文本/DDL 掃描重現已知審計發現；
   完整規則集與語義嚴格度隨 **L3（Identity）/L4（Confidence）充任**收緊（版本化 linter，總綱 §5.4）。
   **治權自動化止於判定與阻擋**——本工具只報 finding、決不改 code（P5.W2）。

政策（總綱 §5.4）：`--policy greenfield`＝新 code 於 merge 當下必綠（finding 即 error）；
   `--policy legacy`（預設）＝既有系統以補正期追蹤（finding 為 warning，附 AUD 對應）。
"""
from __future__ import annotations

import pathlib
import re

from .model import LintResult, Severity

_CONFIDENCE_RE = re.compile(r"\bconfidence\b", re.I)
_KNOWLEDGE_5TUPLE = ["source", "timestamp|_at\\b|logged_at|created_at", "identity|_id\\b|stock_id",
                     "evidence|attestation|provenance", "confidence"]
_ACTION_LOG_HINT = re.compile(r"(pipeline_execution_log|data_audit_log|automation_action|action_log)", re.I)
_ACTOR_COLS = re.compile(r"\b(actor|actor_identity|authorization|authorization_ref)\b", re.I)
_VENDOR_BIND = re.compile(r'FROM\s+"Taiwan\w+"', re.I)


def _read_files(root: pathlib.Path, suffixes):
    for p in root.rglob("*"):
        if p.suffix in suffixes and ".git" not in p.parts:
            try:
                yield p, p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue


def _sev(policy):
    return Severity.ERROR if policy == "greenfield" else Severity.WARNING


# ── 種子規則（每條重現一項已知審計發現）──────────────────────
def rule_confidence_absent(res, root, policy):
    """AUD-03（critical）：全系統無 Confidence 概念（P4.E1 五元組缺第五元、P4.E8 無傳播）。"""
    hits = 0
    for _p, txt in _read_files(root, {".py", ".sql"}):
        if _CONFIDENCE_RE.search(txt):
            hits += 1
    if hits == 0:
        res.add("AUD-03", _sev(policy), "全掃描範圍零 `confidence` 命中——Knowledge 五元組缺第五元、"
                "無單一形式化語義（P4.E1 不可豁免核心／P4.E8）", "AUGUR-MC v1.3 §P4.E1/§P4.E8")
    else:
        res.add("AUD-03", Severity.INFO, f"`confidence` 命中 {hits} 檔（存在性初步滿足；語義統一性待 L4 充任後強檢）",
                "AUGUR-MC v1.3 §P4.E8")


def _table_body(txt, open_paren_idx):
    """以括號深度計數取 CREATE TABLE 完整表身（MUST-FIX C：勿用 `\\((.*?)\\)`——欄型別括號 VARCHAR(64)/NUMERIC(10,2) 會誤截）。"""
    depth = 0
    for j in range(open_paren_idx, len(txt)):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                return txt[open_paren_idx + 1:j]
    return txt[open_paren_idx + 1:]   # 括號未閉（畸形 DDL）：回至文末，不炸


def rule_action_identity(res, root, policy):
    """AUD-10/11（major）：自動行動留痕表缺 Actor Identity / Authorization 欄（P5.E1 六元組、F6）。"""
    for p, txt in _read_files(root, {".py", ".sql"}):
        for m in re.finditer(r'CREATE TABLE[^(]*?(pipeline_execution_log|data_audit_log)[^(]*?\(', txt, re.I):
            body = _table_body(txt, m.end() - 1)
            if not _ACTOR_COLS.search(body):
                res.add("AUD-10", _sev(policy),
                        f"行動留痕表 `{m.group(1)}` 無 actor/authorization 欄——Action 之 Identity 歸因不可機器稽核（P5.E1、F6）",
                        "AUGUR-MC v1.3 §P5.E1/§8.3", location=str(p.relative_to(root)))


def rule_data_first_binding(res, root, policy):
    """AUD-01（critical）：消費模組 SQL 直綁 vendor 表名（F1 Data First 之 code 面徵兆）。"""
    files = set()
    for p, txt in _read_files(root, {".py"}):
        if _VENDOR_BIND.search(txt) and "core" not in p.parts[-2:] and "ingestion" not in str(p):
            files.add(str(p.relative_to(root)))
    if files:
        res.add("AUD-01", _sev(policy),
                f"{len(files)} 個消費模組 SQL 直綁 vendor 表名（FROM \"Taiwan…\"）——World Model 層缺位、"
                f"資料來源結構即系統結構（F1）。樣本：{sorted(files)[:5]}", "AUGUR-MC v1.3 §F1/§P1.E1")


# 規則登記表（骨架種子；後續階段擴充並隨 L3/L4 收緊）
_RULES = [
    ("AUD-03", rule_confidence_absent),
    ("AUD-10/11", rule_action_identity),
    ("AUD-01", rule_data_first_binding),
]

# 尚未實作之規則（登記為 stub，明示骨架邊界，不靜默遺漏）
_STUB_RULES = [
    ("AUD-04/05/06", "Identity registry / lifecycle / 跨來源解析（P3）——待 L3 Identity 充任後實作"),
    ("AUD-02/08/09", "只失效不刪除 / 雙時間 / supersede（P4.E2/E3/E5）——部分已補正；linter 化待 L4"),
    ("K→E→Observation", "引用鏈雙合法終點完整性靜態稽核（P4.E6）——需 L4 Confidence 語義就緒"),
]


def lint_code(code_root: str, policy: str = "legacy") -> LintResult:
    """對 code 目錄跑 audit_lint 骨架。policy: 'legacy'（warning）| 'greenfield'（error）。"""
    root = pathlib.Path(code_root)
    res = LintResult(target=f"{code_root} [audit_lint/{policy}]")
    if not root.is_dir():
        res.add("IO", Severity.ERROR, f"code 路徑不存在或非目錄：{code_root}")
        return res
    for _rid, fn in _RULES:
        fn(res, root, policy)
    for rid, desc in _STUB_RULES:
        res.add(rid, Severity.INFO, f"[骨架未實作] {desc}", "總綱 §5.4")
    return res
