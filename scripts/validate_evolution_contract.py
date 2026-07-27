#!/usr/bin/env python
"""🎯 跨軸交換物驗證 CLI(C7)——brief/hint/xnotify 檔案過契約才准流通(產生端消費端同一把尺)。

白話:任何 brief/hint/xnotify JSON 檔在被 advisor/三軸 driver 消費前,先過本 CLI(rc=0 才算
合格交付物);判準本體住 `augur.audit.evolution_contract`(#12 單一住所,本檔只做 IO 與回報)。
守 #15 #8 #10 #29;SSOT=v2 總控 §3.3 C7;INTEG-C(整合計畫 P-C)。

執行指令矩陣:
  python scripts/validate_evolution_contract.py                          # 無參數:印矩陣+契約摘要(安全預設)
  python scripts/validate_evolution_contract.py --file b.json --kind brief   # 驗單檔(rc=0 合格/1 不合格)
  python scripts/validate_evolution_contract.py --file h.json --kind hint
  python scripts/validate_evolution_contract.py --selftest               # 免 DB 免 API(委派模組自測)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401

from augur.audit.evolution_contract import (
    BLACKLIST,
    CLAIM_LEVELS,
    MAX_CLAIMS,
    SCHEMAS,
    validate,
)
from augur.audit.evolution_contract import _selftest as _module_selftest


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--file", help="待驗 JSON 檔路徑")
    ap.add_argument("--kind", choices=[s.split("/")[0] for s in SCHEMAS])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _module_selftest()
    if not a.file or not a.kind:
        print((__doc__ or "").strip())
        print(f"\n契約摘要: SCHEMAS={SCHEMAS} CLAIM_LEVELS={CLAIM_LEVELS} "
              f"claims≤{MAX_CLAIMS} 黑名單={BLACKLIST}")
        return 0
    try:
        with open(a.file, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"✗ 讀檔/解析失敗: {e}")
        return 1
    errs = validate(obj, a.kind)
    if errs:
        print(f"✗ {a.file} 不合 {a.kind}/1 契約({len(errs)} 項):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"✓ {a.file} 合格({a.kind}/1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
