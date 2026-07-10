#!/usr/bin/env python3
"""🎯 本地接續狀態閱讀器 — 一次讀出 HANDOFF.md + Claude memory 全部內文,零 Claude usage。

給「人」或「本地 AI(qwen3:8b)」在不開 Claude session 的情況下,取得完整專案接續狀態
(跨機交接指南 + 所有長期記憶)。守原則 #28(本地優先)、#8(誠實:memory 機器本地、不隨 git,
找不到就明說不佯裝)。

⚠ 前提誠實:此程式「不會」減少 Claude 自己讀 memory 的量——Claude 每個 session 由 harness
自動注入 MEMORY.md 索引。它省的是「人/本地 AI 不必開 Claude 就能讀到全狀態」那條路徑的 token。

memory 目錄「機器本地、不隨 git」:預設從 cwd 推導 ~/.claude/projects/<mangled>/memory/,
找不到(如剛換機、尚未產生 memory)不報錯、只印 HANDOFF + 提示。

執行指令矩陣:
    python read_handoff.py                    # 完整 digest(HANDOFF + memory 索引 + 全 memory 內文)→ stdout
    python read_handoff.py --list             # 只列 memory 標題/索引(快速一覽)
    python read_handoff.py --handoff-only      # 只印 HANDOFF.md
    python read_handoff.py --memory-only       # 只印 memory(索引 + 全內文)
    python read_handoff.py --out state.md      # 寫入檔案(供本地 AI 讀取/備份)
    python read_handoff.py --memory-dir DIR     # 手動指定 memory 目錄(跨機/非標準路徑)
    python read_handoff.py | ollama run qwen3:8b "根據以下專案狀態回答我的問題: ..."  # 餵本地 AI
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def default_memory_dir() -> Path:
    """從真實 cwd 推導 Claude Code 的 per-project memory 目錄(路徑 mangling: '/' → '-')。"""
    mangled = str(REPO_ROOT).replace("/", "-")
    return Path.home() / ".claude" / "projects" / mangled / "memory"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """輕量 frontmatter 解析(不引 yaml):回 (欄位 dict, 內文)。非 frontmatter 檔回 ({}, 全文)。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
    return meta, parts[2].lstrip("\n")


def read_handoff() -> str:
    p = REPO_ROOT / "HANDOFF.md"
    if not p.exists():
        return "(此 repo 無 HANDOFF.md)"
    return p.read_text(encoding="utf-8")


def read_memory_index(memdir: Path) -> str:
    idx = memdir / "MEMORY.md"
    if not idx.exists():
        return "(memory 目錄無 MEMORY.md 索引)"
    return idx.read_text(encoding="utf-8")


def read_memory_bodies(memdir: Path) -> list[tuple[str, str, str]]:
    """回 [(name, description, body), ...],依檔名排序,排除索引本身。"""
    out = []
    for f in sorted(memdir.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        out.append((meta.get("name", f.stem), meta.get("description", ""), body.strip()))
    return out


def build_digest(memdir: Path, mode: str) -> str:
    lines: list[str] = []
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Augur 專案接續狀態 digest — {stamp}(本地產生,零 Claude usage)")
    lines.append("")

    mem_exists = memdir.is_dir()
    if not mem_exists and mode != "handoff":
        lines.append(f"> ⚠ 找不到 memory 目錄 `{memdir}` — 可能是剛換機、尚未產生本地 memory。")
        lines.append("> memory 機器本地、不隨 git;此為預期狀況,非錯誤。以下僅含 HANDOFF。")
        lines.append("")

    if mode in ("full", "handoff"):
        lines.append("=" * 60)
        lines.append("## 一、HANDOFF.md(跨機接續指南)")
        lines.append("=" * 60)
        lines.append("")
        lines.append(read_handoff())
        lines.append("")

    if mode in ("full", "memory") and mem_exists:
        lines.append("=" * 60)
        lines.append("## 二、Claude memory 索引(MEMORY.md)")
        lines.append("=" * 60)
        lines.append("")
        lines.append(read_memory_index(memdir))
        lines.append("")
        lines.append("=" * 60)
        lines.append("## 三、Claude memory 全內文")
        lines.append("=" * 60)
        for name, desc, body in read_memory_bodies(memdir):
            lines.append("")
            lines.append(f"### ▸ {name}")
            if desc:
                lines.append(f"_{desc}_")
            lines.append("")
            lines.append(body)
            lines.append("")

    return "\n".join(lines)


def build_list(memdir: Path) -> str:
    lines = ["# memory 一覽", ""]
    if not memdir.is_dir():
        return f"(找不到 memory 目錄 {memdir} — 機器本地、可能尚未產生)"
    lines.append("## 索引(MEMORY.md)")
    lines.append(read_memory_index(memdir))
    lines.append("")
    lines.append("## 檔案清單")
    for name, desc, _ in read_memory_bodies(memdir):
        lines.append(f"- **{name}** — {desc}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="本地 HANDOFF + Claude memory 閱讀器(零 Claude usage)")
    ap.add_argument("--memory-dir", type=Path, default=None, help="手動指定 memory 目錄(預設從 cwd 推導)")
    ap.add_argument("--out", type=Path, default=None, help="寫入檔案(預設印到 stdout)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--list", action="store_true", help="只列 memory 標題/索引")
    g.add_argument("--handoff-only", action="store_true", help="只印 HANDOFF.md")
    g.add_argument("--memory-only", action="store_true", help="只印 memory")
    args = ap.parse_args()

    memdir = args.memory_dir or default_memory_dir()

    if args.list:
        text = build_list(memdir)
    elif args.handoff_only:
        text = build_digest(memdir, "handoff")
    elif args.memory_only:
        text = build_digest(memdir, "memory")
    else:
        text = build_digest(memdir, "full")

    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"✓ 已寫入 {args.out}({len(text)} 字元)", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
