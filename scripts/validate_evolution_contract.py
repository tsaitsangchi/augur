#!/usr/bin/env python
"""🎯 跨軸交換物驗證 CLI(C7)——brief/hint/xnotify 檔案過契約才准流通(產生端消費端同一把尺)。

白話:任何 brief/hint/xnotify JSON 檔在被 advisor/三軸 driver 消費前,先過本 CLI(rc=0 才算
合格交付物);判準本體住 `augur.audit.evolution_contract`(#12 單一住所,本檔只做 IO 與回報)。
守 #15 #8 #10 #29;SSOT=v2 總控 §3.3 C7;INTEG-C(整合計畫 P-C)。

執行指令矩陣:
  python scripts/validate_evolution_contract.py                          # 無參數:印矩陣+契約摘要(安全預設)
  python scripts/validate_evolution_contract.py --file b.json --kind brief   # 驗單檔(rc=0 合格/1 不合格)
  python scripts/validate_evolution_contract.py --file h.json --kind hint
  python scripts/validate_evolution_contract.py --scan                   # 掃 var/ 全部交付物(任一不合即 rc=1)
  python scripts/validate_evolution_contract.py --scan --dir var/briefs
  python scripts/validate_evolution_contract.py --selftest               # 免 DB 免 API(委派模組自測)
"""
import argparse
import json
import pathlib
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


ROOT = pathlib.Path(__file__).resolve().parents[1]
# 交付物住所 → 型別(#12:掃描範圍是資料而非猜測;新增出口目錄來此補一列)
SCAN_DIRS = {"var/briefs": "brief", "var/hints": "hint", "var/xnotify": "xnotify"}


def scan(root_dir=None) -> int:
    """掃全部交付物目錄;**一個都沒有也算 rc=0**,但明說「零檔」——不讓空目錄看起來像全過。"""
    targets = ({root_dir: _kind_of(root_dir)} if root_dir else SCAN_DIRS)
    n_ok = n_bad = 0
    for rel, kind in targets.items():
        d = ROOT / rel
        if not d.is_dir():
            print(f"  {rel:16} (目錄不存在,略過)")
            continue
        files = sorted(d.glob("*.json"))
        print(f"  {rel:16} kind={kind} 檔數={len(files)}")
        for p in files:
            try:
                errs = validate(json.loads(p.read_text(encoding="utf-8")), kind)
            except (OSError, json.JSONDecodeError) as e:
                errs = [f"讀檔/解析失敗:{e}"]
            if errs:
                n_bad += 1
                print(f"    ✗ {p.name}({len(errs)} 項):" + "; ".join(str(e) for e in errs[:3]))
            else:
                n_ok += 1
    print(f"\n掃描結果:合格 {n_ok}、不合格 {n_bad}"
          + ("(零檔=尚無交付物,非「全過」)" if n_ok + n_bad == 0 else ""))
    return 1 if n_bad else 0


def _kind_of(rel: str) -> str:
    for k, v in SCAN_DIRS.items():
        if rel.rstrip("/").endswith(k.split("/")[-1]):
            return v
    return "brief"


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--file", help="待驗 JSON 檔路徑")
    ap.add_argument("--kind", choices=[s.split("/")[0] for s in SCHEMAS])
    ap.add_argument("--scan", action="store_true", help="掃交付物目錄全量(任一不合即 rc=1)")
    ap.add_argument("--dir", help="--scan 指定單一目錄")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _module_selftest()
    if a.scan or a.dir:
        print("── C7 交付物掃描 ──")
        return scan(a.dir)
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
