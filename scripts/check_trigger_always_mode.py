#!/usr/bin/env python3
"""🎯 Trigger ALWAYS 模式探針——全庫非內部 trigger 之 `tgenabled='A'` 支數（M-G16）。

守原則 #15（origin-mode 可被一句 GUC 靜音卻仍自稱硬閘＝假強度）· #9 · #28 · #29a/d · #35。

起因（優化計畫書第 23 步／r4 G8·D6）：live 非內部 trigger **116** 支全為 origin（`tgenabled='O'`）、
ALWAYS（`'A'`）**0**。`SET session_replication_role='replica'` 可全靜音且事後無痕。
升嚴為 ALWAYS＝Steward 裁決（M-P／§4；本支不改 trigger）。

探針門檻（master 原文）：ALWAYS 支數 **≥1 才綠**；現況 0 ⇒ **必紅**。

執行指令矩陣
------------
    python3 scripts/check_trigger_always_mode.py              # 無參數＝--check
    python3 scripts/check_trigger_always_mode.py --check      # ALWAYS≥1→0；否則 rc=1
    python3 scripts/check_trigger_always_mode.py --check --json
    python3 scripts/check_trigger_always_mode.py --check --min-always 1
    python3 scripts/check_trigger_always_mode.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

DEFAULT_MIN_ALWAYS = 1
# pg_trigger.tgenabled：O=origin／A=always／R=replica／D=disabled
TG_ALWAYS = "A"
TG_ORIGIN = "O"


def always_rc(*, n_always: int, min_always: int = DEFAULT_MIN_ALWAYS) -> int:
    """ALWAYS 支數 ≥ 門檻 → 0；否則 1。純函式。"""
    return 0 if int(n_always) >= int(min_always) else 1


def _scan(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT tgenabled, count(*)::int FROM pg_trigger "
            "WHERE NOT tgisinternal GROUP BY 1 ORDER BY 1"
        )
        by_mode = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute(
            "SELECT count(*)::int FROM pg_trigger WHERE NOT tgisinternal"
        )
        n_all = cur.fetchone()[0]
    return {
        "n_noninternal": n_all,
        "by_tgenabled": by_mode,
        "n_always": int(by_mode.get(TG_ALWAYS, 0)),
        "n_origin": int(by_mode.get(TG_ORIGIN, 0)),
    }


def _hardgate_docs_without_caveat(root) -> list[str]:
    """文件層附帶（M-G16 另）：寫『硬閘』卻未提 origin/replica/ALWAYS 之 hits（報而不單獨定 rc）。"""
    import re
    from pathlib import Path
    root = Path(root)
    hits = []
    pat = re.compile(r"硬閘")
    cave = re.compile(r"origin|ALWAYS|session_replication_role|replica", re.I)
    for p in list(root.glob("docs/**/*.md")) + list(root.glob("src/**/*.py")) \
            + list(root.glob("scripts/**/*.py")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if not pat.search(text):
            continue
        for i, ln in enumerate(text.splitlines(), 1):
            if pat.search(ln) and not cave.search(ln):
                # 前後 1 行也無 caveat 才算
                ctx = "\n".join(text.splitlines()[max(0, i - 2):i + 1])
                if not cave.search(ctx):
                    hits.append(f"{p.relative_to(root)}:{i}")
    return hits


def _check(*, as_json=False, min_always=DEFAULT_MIN_ALWAYS) -> int:
    from augur.core import db
    from pathlib import Path

    with db.connect() as conn:
        snap = _scan(conn)
    rc = always_rc(n_always=snap["n_always"], min_always=min_always)
    docs = _hardgate_docs_without_caveat(Path(__file__).resolve().parents[1])
    snap["min_always"] = min_always
    snap["hardgate_docs_without_caveat_n"] = len(docs)
    snap["hardgate_docs_sample"] = docs[:15]
    snap["rc"] = rc
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
        return rc

    print(f"── Trigger ALWAYS 模式探針（M-G16；門檻 ≥{min_always}）──")
    print(f"  非內部 trigger：{snap['n_noninternal']}"
          f"；tgenabled 分布：{snap['by_tgenabled']}")
    print(f"  ALWAYS('A')：{snap['n_always']}／origin('O')：{snap['n_origin']}")
    print(f"  『硬閘』字樣缺 origin/ALWAYS/replica 限定：{len(docs)} 處（報而不單獨定 rc）")
    for h in docs[:8]:
        print(f"    {h}")
    if rc:
        print("  → **紅** rc=1：ALWAYS=0（或不足）——一句 "
              "`SET session_replication_role='replica'` 可靜音全庫 origin trigger、無痕。"
              "升嚴 ENABLE ALWAYS＝Steward 另裁；本支不改 trigger。")
    else:
        print(f"  → 綠 rc=0：ALWAYS ≥ {min_always}")
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("rc：0 ALWAYS → 紅（live 真形）", always_rc(n_always=0) == 1)
    chk("rc：1 ALWAYS → 綠", always_rc(n_always=1) == 0)
    chk("rc：116 origin 仍與 ALWAYS 無關（門檻只看 A）",
        always_rc(n_always=0, min_always=1) == 1)
    chk("rc：門檻參數化（要 5、只有 3 → 紅）",
        always_rc(n_always=3, min_always=5) == 1)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M-G16 trigger ALWAYS 探針")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-always", type=int, default=DEFAULT_MIN_ALWAYS)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check(as_json=a.json, min_always=a.min_always)


if __name__ == "__main__":
    sys.exit(main())
