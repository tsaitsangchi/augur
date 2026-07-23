"""路徑治理判準：治理權威語料排除 + 敏感/衍生/二進位 denylist。

本模組為唯讀邏輯（純判斷，無副作用），server 與 index 共用同一判準，
確保「index 不寫入者」與「recall 不回傳者」出自同一定義（避免兩套判準漂移）。

執行指令矩陣：
  python -m tools.project_memory_mcp.govern              # 印用途（唯讀、免外部依賴）
  python -m tools.project_memory_mcp.govern --selftest    # 治理/排除判準紅綠自測（唯讀、免 DB）
"""
from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

# 允許索引之文本副檔名（非清單者一律排除，防二進位/媒體入索引）
_TEXT_EXT = {
    ".md", ".markdown", ".txt", ".rst", ".py", ".json", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".sh", ".sql",
}

# 排除之目錄（衍生物/相依/版控/敏感）。含 venv 各式命名與其 site-packages。
_EXCLUDE_DIRS = {
    ".git", ".project_memory", "logs", "node_modules", "__pycache__",
    ".venv", "venv", ".venv-mcp",
    "site-packages", "dist-packages",
    ".mypy_cache", ".pytest_cache", ".tox", ".eggs",
    ".idea", ".cache", ".claude", "ref_augur",
}

# 排除之檔名（敏感）
_EXCLUDE_NAMES = {".env"}


def is_governance_path(resolved: pathlib.Path) -> bool:
    """治理權威語料判定（路徑前綴）。

    範圍：constitution/ 全域（MC、RULING-*、AMENDMENT-LOG.md、adoption-drafts）；
    specs/ 下之生效規格（檔名含 SPECIFICATION 且不含 -draft）。
    草案（-draft）屬非治理輔助語料，不在此列。與 local_llm_mcp 同一判準。
    """
    try:
        rel = resolved.relative_to(REPO)
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return False
    if parts[0] == "constitution":
        return True
    if parts[0] == "specs":
        name = parts[-1]
        if "SPECIFICATION" in name.upper() and "-draft" not in name.lower():
            return True
    return False


def is_excluded(resolved: pathlib.Path) -> bool:
    """敏感/衍生/二進位排除（與治理排除相互獨立）。"""
    try:
        rel = resolved.relative_to(REPO)
    except ValueError:
        return True  # repo 外一律不索引（路徑封閉）
    if any(part in _EXCLUDE_DIRS for part in rel.parts):
        return True
    if resolved.name in _EXCLUDE_NAMES:
        return True
    if resolved.suffix.lower() not in _TEXT_EXT:
        return True
    return False


def should_index(resolved: pathlib.Path, root: pathlib.Path | None = None) -> bool:
    """是否應納入索引：repo 內、非治理權威、非排除、且為既存檔案。

    root 若給定（如 selftest 之暫存目錄），僅用於相對 denylist 目錄判斷；
    治理判準恆以真實 repo（REPO）為錨（暫存檔本就非治理，回 False 正確）。
    """
    if not resolved.is_file():
        return False
    if is_governance_path(resolved):
        return False
    base = root or REPO
    try:
        rel = resolved.relative_to(base)
    except ValueError:
        return False
    if any(part in _EXCLUDE_DIRS for part in rel.parts):
        return False
    if resolved.name in _EXCLUDE_NAMES:
        return False
    if resolved.suffix.lower() not in _TEXT_EXT:
        return False
    return True


def _selftest() -> int:
    ok = is_governance_path(REPO / "constitution" / "META-CONSTITUTION.md")
    ok = ok and not is_governance_path(REPO / "README.md")
    ok = ok and is_excluded(REPO / ".env")
    ok = ok and is_excluded(REPO / "node_modules" / "x.js")
    ok = ok and not is_excluded(REPO / "README.md")
    ok = ok and should_index(REPO / "README.md")
    ok = ok and not should_index(REPO / "constitution" / "META-CONSTITUTION.md")
    print("govern selftest:" + (" OK" if ok else " FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
