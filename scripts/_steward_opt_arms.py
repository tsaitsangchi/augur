"""🎯 Steward 優化臂位讀取——G13-Q22／G16-ALWAYS 等 [I] 圈選之機械閘（非 [N]）。

守原則 #15（臂未登錄不得 silently 當已授權）· #12（單一住所＝ops JSON）· #28 · #29 · #35。
供 scripts 匯入；`--selftest` 餵真 dict（免 DB 免 API）。

執行指令矩陣
------------
    python3 scripts/_steward_opt_arms.py              # 印用途＋公開入口
    python3 scripts/_steward_opt_arms.py --selftest   # 純函式紅綠自測
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
DEFAULT_ARMS_PATH = _REPO / "ops" / "steward_opt_arms.json"

G13_KEY = "G13-Q22"
G16_KEY = "G16-ALWAYS"
ARM_MACHINE_SUPERSEDE_OK = "machine-supersede-ok"
ARM_ENABLE_PROBE_ONLY = "enable-probe-only"
ARM_ENABLE_ALWAYS_GO = "enable-always-go"


def load_arms(path: Path | None = None) -> dict:
    """讀 ops JSON；缺檔／壞 JSON → {}（fail-closed 呼叫端自判）。純 I/O。"""
    p = path or DEFAULT_ARMS_PATH
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def arm_of(arms: dict, key: str) -> str | None:
    """取某閘之 arm 字串；缺 → None。純函式。"""
    block = arms.get(key) if isinstance(arms, dict) else None
    if not isinstance(block, dict):
        return None
    v = block.get("arm")
    return str(v) if v is not None else None


def machine_supersede_authorized(arms: dict) -> bool:
    """G13-Q22＝machine-supersede-ok 才准機器 awaiting→superseded 寫入。純函式。"""
    return arm_of(arms, G13_KEY) == ARM_MACHINE_SUPERSEDE_OK


def always_enable_authorized(arms: dict) -> bool:
    """G16-ALWAYS＝enable-always-go 才准 ENABLE ALWAYS；probe-only／defer → False。純函式。"""
    return arm_of(arms, G16_KEY) == ARM_ENABLE_ALWAYS_GO


def probe_only_active(arms: dict) -> bool:
    """G16 臂為 enable-probe-only。純函式。"""
    return arm_of(arms, G16_KEY) == ARM_ENABLE_PROBE_ONLY


def _selftest() -> None:
    ok = {
        G13_KEY: {"arm": ARM_MACHINE_SUPERSEDE_OK},
        G16_KEY: {"arm": ARM_ENABLE_PROBE_ONLY},
    }
    bad = {G13_KEY: {"arm": "keep-awaiting"}, G16_KEY: {"arm": ARM_ENABLE_ALWAYS_GO}}
    assert machine_supersede_authorized(ok) is True
    assert machine_supersede_authorized(bad) is False
    assert probe_only_active(ok) is True
    assert always_enable_authorized(ok) is False
    assert always_enable_authorized(bad) is True
    assert arm_of({}, G13_KEY) is None
    print("自測:全通過 ✓")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        raise SystemExit(0)
    print(__doc__)
    print("公開入口: load_arms / arm_of / machine_supersede_authorized / "
          "always_enable_authorized / probe_only_active")
    raise SystemExit(0)
