#!/usr/bin/env python
"""augur 投資哲學框架 build — 建 6 表 + 落地首批策展（真實權威文獻）。

🎯 把投資學派（價值/品質/成長/動能/週期…、出自真實文獻）結構化為因子假說 + 文獻來源,落地 DB。
組合根:接 philosophy.framework，邏輯在 src、入口不放邏輯（#18）。

守 #1（真實文獻禁 AI 生成入庫）· #14/#15（direction 為假說、validated_ic 須實證回填）· #18。
執行指令矩陣:python scripts/build_philosophy_framework.py
"""
import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.philosophy import framework


def main():
    with db.connect() as conn:
        res = framework.build(conn)
        print(f"投資哲學框架落地:{res['schools']} 學派 / {res['principles']} 原則 / "
              f"{res['factor_map']} 因子映射 / {res['sources']} 文獻來源（首批真實策展）")
        print(f"思想家傳記:{res['thinkers']} 大師 / {res['works']} 著作 / {res['links']} school↔thinker 關聯")


if __name__ == "__main__":
    main()
