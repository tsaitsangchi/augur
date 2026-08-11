#!/usr/bin/env python
"""STRUCT 循環探針 — AST 套件級 import 雙向／三角（零 DB · 零改碼寫庫）。

🎯 把 STRUCT-CYCLE-EXPLORE 一次性盤點收成可重跑 CLI：掃 `src/augur/**/*.py` 的
   `from augur.X...`／`import augur.X`，建套件→套件邊，列雙向對與三角環。
   **唯讀**；不解圈、不 DDL、不 COMMIT。解圈須另 GO。
守 FZ/GATE-keep · zero-code 寫庫 · #15 可重現（同樹同結果）。

執行指令矩陣:
  python scripts/explore_struct_cycles.py                 # 印矩陣
  python scripts/explore_struct_cycles.py --selftest      # 合成圖＋可選實樹煙測（零 DB）
  python scripts/explore_struct_cycles.py --run           # 掃本 repo src/augur 印雙向／三角
  python scripts/explore_struct_cycles.py --run --json    # JSON stdout
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = REPO_ROOT / "src" / "augur"


def _pkg_of(mod: str) -> str | None:
    """augur.foo.bar → foo；非 augur.* → None。"""
    parts = mod.split(".")
    if len(parts) < 2 or parts[0] != "augur":
        return None
    return parts[1]


def collect_augur_imports(py_path: Path) -> set[str]:
    """回此檔依賴的 augur.<pkg>（第一層套件名集合）。"""
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="ignore"), filename=str(py_path))
    except SyntaxError:
        return set()
    deps: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            pkg = _pkg_of(node.module)
            if pkg:
                deps.add(pkg)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                pkg = _pkg_of(alias.name)
                if pkg:
                    deps.add(pkg)
    return deps


def build_package_edges(src_root: Path) -> dict[str, set[str]]:
    """套件→套件邊（不含自環）。"""
    edges: dict[str, set[str]] = collections.defaultdict(set)
    if not src_root.is_dir():
        raise FileNotFoundError(f"src_root 不存在: {src_root}")
    for py in sorted(src_root.rglob("*.py")):
        rel = py.relative_to(src_root)
        # src/augur/foo/bar.py → 定義所在套件 = foo（頂層檔=名 stem 當作 pkg 則略過混亂：用 parent）
        parts = rel.parts
        if parts[0] == "__init__.py" and len(parts) == 1:
            continue
        def_pkg = parts[0] if len(parts) > 1 else py.stem
        if def_pkg.endswith(".py"):
            def_pkg = Path(def_pkg).stem
        for dep in collect_augur_imports(py):
            if dep != def_pkg:
                edges[def_pkg].add(dep)
    return {k: set(v) for k, v in edges.items()}


def bidirectional_pairs(edges: dict[str, set[str]]) -> list[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for a, outs in edges.items():
        for b in outs:
            if a in edges.get(b, ()):
                pairs.add(tuple(sorted((a, b))))
    return sorted(pairs)


def triangles(edges: dict[str, set[str]]) -> list[tuple[str, str, str]]:
    tris: set[tuple[str, str, str]] = set()
    for a, outs in edges.items():
        for b in outs:
            for c in edges.get(b, ()):
                if c != a and a in edges.get(c, ()):
                    tris.add(tuple(sorted((a, b, c))))
    return sorted(tris)


def summarize(edges: dict[str, set[str]]) -> dict:
    bi = bidirectional_pairs(edges)
    tri = triangles(edges)
    return {
        "n_packages": len(set(edges) | {b for s in edges.values() for b in s}),
        "n_edges": sum(len(v) for v in edges.values()),
        "bidirectional": [list(p) for p in bi],
        "n_bidirectional": len(bi),
        "triangles": [list(t) for t in tri],
        "n_triangles": len(tri),
        "edges": {k: sorted(v) for k, v in sorted(edges.items())},
    }


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # 合成圖：A↔B、A→C→B→A 三角
    synth = {
        "a": {"b", "c"},
        "b": {"a", "c"},
        "c": {"a"},
        "d": {"e"},
        "e": set(),
    }
    bi = bidirectional_pairs(synth)
    tri = triangles(synth)
    chk("雙向含 a-b", ("a", "b") in bi)
    chk("雙向含 a-c", ("a", "c") in bi)
    chk("三角含 a-b-c", ("a", "b", "c") in tri)
    chk("d-e 非雙向", ("d", "e") not in bi)
    s = summarize(synth)
    chk("summarize n_bidirectional", s["n_bidirectional"] == 2)
    chk("summarize n_triangles>=1", s["n_triangles"] >= 1)

    # 實樹煙測（可重跑）：至少掃得到 core，且雙向數≥1（歷史錨：audit↔core 等）
    try:
        real = build_package_edges(DEFAULT_SRC)
        chk("實樹有 core 出邊或入邊", "core" in real or any("core" in v for v in real.values()))
        bi_r = bidirectional_pairs(real)
        chk("實樹雙向≥1", len(bi_r) >= 1)
        # 錨：2026-08-07 探索帳曾見 audit↔core
        chk("實樹含 audit↔core（錨）", ("audit", "core") in bi_r)
    except Exception as e:
        chk(f"實樹掃描無例外({type(e).__name__})", False)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--src", default=str(DEFAULT_SRC), help="augur 套件根（預設 src/augur）")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    src = Path(args.src)
    edges = build_package_edges(src)
    summary = summarize(edges)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"src={src} | packages≈{summary['n_packages']} | directed_edges={summary['n_edges']}")
    print("package_edges:")
    for a, outs in summary["edges"].items():
        print(f"  {a} -> {outs}")
    print(f"\nbidirectional_pairs (n={summary['n_bidirectional']}):")
    for a, b in summary["bidirectional"]:
        print(f"  {a} ↔ {b}")
    print(f"\ntriangles (n={summary['n_triangles']}):")
    for t in summary["triangles"]:
        print(f"  {'-'.join(t)}")
    print("\n（唯讀探針；解圈／DDL 須另 GO）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
