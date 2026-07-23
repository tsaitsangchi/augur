"""constitution-mcp 之工具實作層（唯讀）。

設計紀律（承接本專案治理教訓，見 reports/MCP-SERVER-OPTIMIZATION-REPORT.md §3.2）：

1. **全部唯讀**——不提供任何寫入／修改工具。修規格為 Steward `§8.5`／`§8.6` 之權，
   不得因本工具而生一條經 MCP 之旁路。
2. **合規檢查永不快取**——`lint_compliance` 每次實跑。本專案已三度實證「陳舊綠燈」
   之害（linter 三輪 error 0 而實質錯誤並存）；於合規判定前置 TTL 快取即自造第四輪。
3. **回傳附出處**——每筆附 `file:line`，俾模型引用時可回溯。
4. **失敗發聲**——解析失敗回明確錯誤，不靜默退回近似答案（承接 B9「靜默降級」教訓）。

執行指令矩陣（本檔為 library，CLI/MCP 消費見 `server.py`；完整回歸鎖見同套件 `selftest.py`）：
  python -m tools.constitution_mcp.tools              # 印用途（唯讀、免外部依賴）
  python -m tools.constitution_mcp.tools --selftest    # 對真實憲章/規格跑 get_clause 等唯讀紅綠自測
"""
from __future__ import annotations

import os
import re

from tools.constitution_lint import compliance_lint, mc_clauses

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MC_PATH = os.path.join(REPO, "constitution", "META-CONSTITUTION.md")
SPECS_DIR = os.path.join(REPO, "specs")
CONST_DIR = os.path.join(REPO, "constitution")


class ToolError(Exception):
    """工具層錯誤——一律發聲，不靜默降級。"""


def _rel(path: str) -> str:
    return os.path.relpath(path, REPO)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise ToolError(f"無法讀取 {_rel(path)}：{e}") from e


# ── 條款查詢 ────────────────────────────────────────────────────────────────

def _mc_labels() -> dict:
    return mc_clauses.load_clause_labels(MC_PATH)


def _spec_files() -> list:
    """生效規格（排除 -draft 歸檔本）。"""
    out = []
    for fn in sorted(os.listdir(SPECS_DIR)):
        if fn.endswith("-SPECIFICATION.md"):
            out.append(os.path.join(SPECS_DIR, fn))
    return out


def _spec_labels() -> dict:
    """全部生效規格之條款標籤，code → 條目（附 spec 檔名）。"""
    merged = {}
    for path in _spec_files():
        text = _read(path)
        fm, _ = compliance_lint._parse_front_matter(text)
        src = f"{fm.get('spec', os.path.basename(path))} {fm.get('spec-version', '')}".strip()
        for code, d in mc_clauses.enumerate_spec_clause_labels(text, src).items():
            d = dict(d)
            d["spec_path"] = _rel(path)
            merged.setdefault(code, d)
    return merged


def get_clause(code: str) -> str:
    """回單一憲章條款之原文、標籤與行號。"""
    code = code.strip()
    labels = _mc_labels()
    d = labels.get(code)
    if d is None:
        near = [c for c in labels if c.lower().startswith(code.lower()[:4])][:8]
        hint = f"\n\n相近代號：{'、'.join(sorted(near))}" if near else ""
        raise ToolError(f"憲章無此條款代號：{code}（母集 {len(labels)} 條）{hint}")
    name = d.get("paren_name") or "（無自有括號名）"
    return (
        f"# {code}（{name}）\n"
        f"出處：constitution/META-CONSTITUTION.md:{d.get('line')}｜來源：{d.get('source')}\n\n"
        f"{d.get('text', '').strip()}"
    )


def get_spec_clause(code: str) -> str:
    """回單一上層規格條款（WM./ONT./ID./KS./L5./L6./L7. 等）之原文。"""
    code = code.strip()
    labels = _spec_labels()
    d = labels.get(code)
    if d is None:
        near = [c for c in labels if c.lower().startswith(code.lower()[:3])][:8]
        hint = f"\n\n相近代號：{'、'.join(sorted(near))}" if near else ""
        raise ToolError(f"生效規格中無此條款代號：{code}（母集 {len(labels)} 條）{hint}")
    name = d.get("paren_name") or "（無自有括號名）"
    return (
        f"# {code}（{name}）\n"
        f"出處：{d.get('spec_path')}:{d.get('line')}｜規格：{d.get('source')}\n\n"
        f"{d.get('text', '').strip()}"
    )


def search_clauses(query: str, limit: int = 12, scope: str = "all") -> str:
    """關鍵詞檢索條款；回代號＋標籤＋摘句，不回全文。"""
    query = query.strip()
    if not query:
        raise ToolError("query 不得為空")
    if scope not in ("all", "mc", "specs"):
        raise ToolError(f"scope 須為 all／mc／specs 之一，得 {scope}")

    pool = {}
    if scope in ("all", "mc"):
        for c, d in _mc_labels().items():
            pool[c] = (d, "constitution/META-CONSTITUTION.md", d.get("line"))
    if scope in ("all", "specs"):
        for c, d in _spec_labels().items():
            pool.setdefault(c, (d, d.get("spec_path"), d.get("line")))

    ql = query.lower()
    hits = []
    for code, (d, path, line) in pool.items():
        name = d.get("paren_name") or ""
        text = d.get("text", "")
        score = 0
        if ql in code.lower():
            score += 100
        if ql in name.lower():
            score += 50
        n = text.lower().count(ql)
        score += min(n, 10) * 5
        if score:
            idx = text.lower().find(ql)
            if idx < 0:
                snippet = text[:120].replace("\n", " ")
            else:
                s = max(0, idx - 50)
                snippet = ("…" if s else "") + text[s:idx + 110].replace("\n", " ") + "…"
            hits.append((score, code, name, path, line, snippet))

    if not hits:
        raise ToolError(f"無命中：{query}（檢索範圍 {scope}，母集 {len(pool)} 條）")

    hits.sort(key=lambda h: (-h[0], h[1]))
    lines = [f"檢索「{query}」（範圍 {scope}）：{len(hits)} 命中，列前 {min(limit, len(hits))}\n"]
    for _, code, name, path, line, snippet in hits[:limit]:
        lines.append(f"* **{code}**（{name or '—'}）@ {path}:{line}\n  {snippet}")
    if len(hits) > limit:
        lines.append(f"\n（另有 {len(hits) - limit} 筆未列；以 get_clause／get_spec_clause 取全文）")
    return "\n".join(lines)


# ── 合規檢查（永不快取）────────────────────────────────────────────────────

def lint_compliance(spec_path: str) -> str:
    """對規格檔實跑 §8.3 compliance lint。**每次實跑，不快取。**"""
    path = spec_path if os.path.isabs(spec_path) else os.path.join(REPO, spec_path)
    if not os.path.isfile(path):
        raise ToolError(f"找不到規格檔：{spec_path}")

    res = compliance_lint.lint_spec(path, MC_PATH)
    err, warn = res.errors, res.warnings
    info = [f for f in res.findings if f not in err and f not in warn]

    head = (
        f"# lint_compliance：{_rel(path)}\n"
        f"判定：{'✅ PASS' if res.passed else '❌ FAIL'}"
        f"（error {len(err)} / warning {len(warn)} / info {len(info)}）\n"
        f"※ 本結果為本次實跑所得，未經任何快取。\n"
    )
    if not res.findings:
        return head + "\n無發現。"

    out = [head]
    for label, group in (("ERROR", err), ("WARNING", warn), ("INFO", info)):
        if not group:
            continue
        out.append(f"\n## {label}（{len(group)}）")
        for f in group[:60]:
            loc = f" @ {f.location}" if f.location else ""
            basis = f" [{f.mc_basis}]" if f.mc_basis else ""
            out.append(f"* `{f.rule}`{loc}{basis}\n  {f.message}")
        if len(group) > 60:
            out.append(f"\n（另有 {len(group) - 60} 筆未列——以 CLI 取完整報表："
                       f"`python3 -m tools.constitution_lint compliance {_rel(path)}`）")
    return "\n".join(out)


# ── 治權狀態 ────────────────────────────────────────────────────────────────

def layer_status() -> str:
    """回八層現況：規格版本、mc-version、生效／草案、對應歸檔。"""
    mc_text = _read(MC_PATH)
    mc_ver = mc_clauses.current_mc_version(mc_text)
    rows = []
    for path in _spec_files():
        text = _read(path)
        fm, _ = compliance_lint._parse_front_matter(text)
        rows.append({
            "layer": fm.get("layer", "?"),
            "spec": fm.get("spec", os.path.basename(path)),
            "ver": fm.get("spec-version", "?"),
            "mc": fm.get("mc-version", "?"),
            "path": _rel(path),
            "waivers": fm.get("waivers", "[]"),
            "tensions": fm.get("open-tensions", "[]"),
        })
    rows.sort(key=lambda r: str(r["layer"]))

    out = [
        "# 八層治權現況",
        f"Layer 0 元憲章：constitution/META-CONSTITUTION.md｜**{mc_ver}**",
        f"（本表由各規格 front-matter 實地解析，非硬編碼；母集 {len(mc_clauses.enumerate_clauses(mc_text))} 條 [N] 條款）\n",
        "| Layer | 規格 | 版本 | 依據 MC | 檔案 |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        out.append(f"| {r['layer']} | {r['spec']} | **{r['ver']}** | {r['mc']} | `{r['path']}` |")

    drift = [r for r in rows if r["mc"] and mc_ver not in str(r["mc"])]
    if drift:
        out.append("\n⚠️ **mc-version 落差**（規格所依 MC 版本與現行不符）：")
        for r in drift:
            out.append(f"* Layer {r['layer']} {r['spec']}：依 {r['mc']}，現行 {mc_ver}")
    return "\n".join(out)


_RULING_RE = re.compile(r"(?:INTERPRETATION-)?RULING-(\d{4}-\d{3})")


def _ruling_index() -> dict:
    idx = {}
    for fn in sorted(os.listdir(CONST_DIR)):
        m = _RULING_RE.match(fn)
        if m and fn.endswith(".md"):
            idx[m.group(1)] = os.path.join(CONST_DIR, fn)
    return idx


def get_ruling(number: str) -> str:
    """回裁決之主文與依據（截斷長文；全文以 Read 取）。"""
    num = number.strip()
    m = re.search(r"(\d{4}-\d{3})", num)
    if m:
        num = m.group(1)
    elif num.isdigit():
        num = f"2026-{int(num):03d}"
    idx = _ruling_index()
    path = idx.get(num)
    if path is None:
        raise ToolError(f"無裁決 {num}。現存：{'、'.join(sorted(idx)) or '（無）'}")

    text = _read(path)
    limit = 4000
    body = text if len(text) <= limit else text[:limit] + \
        f"\n\n…（全文 {len(text)} 字元，此處截前 {limit}；以 Read 取 `{_rel(path)}` 讀全文）"
    return f"出處：{_rel(path)}\n\n{body}"


def list_amendments(limit: int = 10) -> str:
    """回修訂登錄簿（AMENDMENT-LOG）最近 N 筆之摘要。"""
    path = os.path.join(CONST_DIR, "AMENDMENT-LOG.md")
    text = _read(path)
    blocks = re.split(r"^## (AL-\d{4}-\d{3})\s*$", text, flags=re.M)
    entries = []
    for i in range(1, len(blocks) - 1, 2):
        entries.append((blocks[i], blocks[i + 1].strip()))
    if not entries:
        raise ToolError(f"無法自 {_rel(path)} 解析 AL 條目（格式可能已變更）——本結果不具權威，請檢查解析錨點")

    out = [f"# 修訂登錄簿：共 {len(entries)} 筆，列最近 {min(limit, len(entries))}\n出處：{_rel(path)}\n"]
    for code, body in entries[-limit:][::-1]:
        lines = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("*")]
        out.append(f"## {code}\n" + "\n".join(lines[:5]))
    return "\n\n".join(out)


def _selftest() -> int:
    if not os.path.isfile(MC_PATH):
        print("constitution_mcp.tools selftest: SKIP（非 repo 內執行，找不到 META-CONSTITUTION.md）")
        return 0
    ok = True
    try:
        ok = ok and "PA" in get_clause("PA")
        ok = ok and "檢索" in search_clauses("Confidence")
        ok = ok and "八層治權現況" in layer_status()
    except ToolError as exc:
        ok = False
        print(f"  ✗ ToolError：{exc}")
    try:
        get_clause("__no_such_code__")
        ok = False  # 應丟 ToolError，不丟即為缺陷
    except ToolError:
        pass
    print("constitution_mcp.tools selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
