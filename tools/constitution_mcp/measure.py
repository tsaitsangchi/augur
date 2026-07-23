"""實測 constitution-mcp 之 context 節省（供 reports/MCP-SERVER-OPTIMIZATION-REPORT.md §3.3 回填）。

  執行指令矩陣：
  python3 -m tools.constitution_mcp.measure

**度量單位為字元數（精確）**；token 數為估算，故一律標示區間並註明換算基礎，
不以單一數字冒充實測——本專案已多次因「手數／估算冒充程式輸出」而失準。
"""
from __future__ import annotations

import os

from . import tools

REPO = tools.REPO

# CJK 為主之中文技術文本，粗估 1 token ≈ 1.0–1.4 字元；英數碼段落較稀疏。
# 取區間下上界，避免以單一數字冒充精確值。
TOK_LO, TOK_HI = 1.4, 1.0


def _tok(chars: int) -> str:
    return f"{int(chars / TOK_LO):,}–{int(chars / TOK_HI):,}"


def _filechars(rel: str) -> int:
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return len(f.read())


SCENARIOS = [
    ("核對一條憲章條款原文（如 P4.E1 之括號名與內涵）",
     lambda: tools.get_clause("P4.E1"),
     "constitution/META-CONSTITUTION.md"),
    ("核對一條規格條款（如 WM.44 形式充分性）",
     lambda: tools.get_spec_clause("WM.44"),
     "specs/WORLD-MODEL-SPECIFICATION.md"),
    ("核對 L7 之一條（如 L7.21 Knowledge 物理欄位）",
     lambda: tools.get_spec_clause("L7.21"),
     "specs/INFRASTRUCTURE-SPECIFICATION.md"),
    ("找出「Evidence 不可空」相關條款落點",
     lambda: tools.search_clauses("不可空", 12),
     "specs/INFRASTRUCTURE-SPECIFICATION.md"),
    ("新 session 開場：摸清八層現況",
     lambda: tools.layer_status(),
     "HANDOFF.md"),
    ("查一份裁決之主文",
     lambda: tools.get_ruling("2026-002"),
     "constitution/RULING-2026-002-LAYER1-ADOPTION.md"),
    ("查最近修訂登錄",
     lambda: tools.list_amendments(5),
     "constitution/AMENDMENT-LOG.md"),
    ("跑一份規格之 compliance lint",
     lambda: tools.lint_compliance("specs/AGENT-RUNTIME-SPECIFICATION.md"),
     "specs/AGENT-RUNTIME-SPECIFICATION.md"),
]


def run() -> int:
    print(f"# constitution-mcp context 節省實測\n")
    print(f"換算基礎：1 token ≈ {TOK_HI}–{TOK_LO} 字元（CJK 技術文本）；字元數為精確值，token 為估算區間。\n")
    print("| 場景 | MCP 回傳 | 取代之整檔讀取 | 字元節省 | 估算 token 節省 |")
    print("|---|---|---|---|---|")

    tot_mcp = tot_full = 0
    for desc, fn, replaced in SCENARIOS:
        try:
            out = fn()
        except tools.ToolError as e:
            print(f"| {desc} | **失敗**：{e} | — | — | — |")
            continue
        n, full = len(out), _filechars(replaced)
        tot_mcp += n
        tot_full += full
        pct = (1 - n / full) * 100 if full else 0
        print(f"| {desc} | {n:,} 字元 | `{replaced}` {full:,} 字元 | **{pct:.1f}%** | {_tok(full - n)} |")

    pct = (1 - tot_mcp / tot_full) * 100
    print(f"\n**八場景合計**：MCP {tot_mcp:,} 字元 vs 整檔 {tot_full:,} 字元"
          f"／節省 **{pct:.1f}%**（估 {_tok(tot_full - tot_mcp)} tokens）")
    print("\n※ 本表比較之基準為「該場景下若無工具則須整檔讀入之檔案」。實務上並非每次點查詢"
          "都會整檔讀入（模型可能改用 grep 分段讀取），故本表為**上界**；惟本專案歷史"
          "紀錄顯示整檔讀入為常態，故其量級具代表性。需要逐列重建整張矩陣等全文工作時，"
          "讀全檔仍為正解，MCP 不取代之。")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
