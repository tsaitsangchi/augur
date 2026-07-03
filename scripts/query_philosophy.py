#!/usr/bin/env python
"""P3 互動檢索驗證 — 查詢 → 逐字可溯源哲學引用。

🎯 驗證 L2 檢索層:給查詢 → 回 top-k 逐字段落 + 溯源 + verbatim 逐字回查標記(原文子字串比對)。
守 #1(逐字可溯源)· #28(本地)· #18。
執行指令矩陣:python scripts/query_philosophy.py <查詢字串>
"""
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.philosophy.retrieval import retrieve, verify_verbatim


def main():
    query = " ".join(sys.argv[1:]) or "the wise investor and margin of safety"
    print(f"查詢: {query!r}\n" + "=" * 70)
    for c in retrieve(query, k=5):
        v = "✓逐字" if verify_verbatim(c) else "✗改寫"
        print(f"[{c.score:.3f}] 《{c.work_title}》/ {c.thinker} — {c.chapter}  [{v}]")
        print(f"  {c.text.strip()[:180]}")
        print(f"  ↳ {c.source_url}\n")


if __name__ == "__main__":
    main()
