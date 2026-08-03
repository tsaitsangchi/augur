#!/usr/bin/env python3
"""🎯 並行容量哨兵——現查 nproc／loadavg／available／llama RSS／heavy_slot（M-O9）。

白話:排班／開並行線前印**當下**容量；容量隨 Ollama 駐留擺盪，**不得引用舊報告數字**。
  輸出對齊週日 09:00 三軸週儀表一行格式。唯讀；**永不 acquire heavy_slot**。

門檻（master §0.3 對映；`--check` 紅燈＝硬阻塞）：
  · available < 1024 MB → 紅（連輕量都危險）
  · loadavg[0] > nproc × 2.0 → 紅（病理過載）
  · 其餘印建議並行上限（重活／中量／輕量），不因此紅。

守原則 #15（數字出 /proc／ps／holder_status）· #28（零 API）· #29a/d · #35。

執行指令矩陣
------------
    python3 scripts/check_parallel_capacity.py              # 無參數＝--check（唯讀）
    python3 scripts/check_parallel_capacity.py --check      # 印容量＋建議；紅則 rc=1
    python3 scripts/check_parallel_capacity.py --check --json
    python3 scripts/check_parallel_capacity.py --week-line  # 只印週報一行
    python3 scripts/check_parallel_capacity.py --selftest   # 零外依：純函式紅綠
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

# 紅燈硬門檻（其餘為建議、不改 rc）
RED_AVAILABLE_MB = 1024
RED_LOAD_OVER_NPROC = 2.0

# §0.3 建議表之可用記憶體切點（MB；advisory only）
HEAVY_LO = 2000   # available < 此 ⇒ 重活上限 1
HEAVY_HI = 6000   # available ≥ 此 ⇒ 重活上限 2
MED_MIN = 1500


def advise_lanes(*, available_mb: int, nproc: int, llama_rss_mb: int) -> dict:
    """依 available 建議三層並行上限。純函式（§0.3 對映）。"""
    if available_mb < HEAVY_LO:
        heavy = 1 if available_mb >= 800 else 0
    elif available_mb >= HEAVY_HI:
        heavy = 2
    else:
        heavy = 1
    if available_mb < MED_MIN:
        medium = 1 if available_mb >= 500 else 0
    elif available_mb < HEAVY_HI:
        medium = 2
    else:
        medium = min(4, max(2, nproc // 3))
    light = min(8, max(2, nproc - 2)) if available_mb >= 200 else 0
    return {
        "heavy": heavy,
        "medium": medium,
        "light": light,
        "note": (
            f"advisory only; llama_rss={llama_rss_mb}MB 擺盪中——"
            "排班前現查，勿引用報告舊數"
        ),
    }


def capacity_rc(*, available_mb: int, load1: float, nproc: int,
                red_available=RED_AVAILABLE_MB,
                red_load_over=RED_LOAD_OVER_NPROC) -> int:
    """硬紅：available 過低或 load1 病理過載。純函式。"""
    if available_mb < red_available:
        return 1
    if nproc > 0 and load1 > nproc * red_load_over:
        return 1
    return 0


def format_week_line(*, nproc, loadavg, available_mb, llama_rss_mb, holders) -> str:
    """週報一行（master §7.3）。純函式。"""
    if isinstance(loadavg, (list, tuple)):
        la = " ".join(f"{float(x):.2f}" for x in loadavg[:3])
    else:
        la = str(loadavg)
    if not holders:
        hs = "無"
    else:
        parts = []
        for h in holders:
            if isinstance(h, dict):
                parts.append(f"{h.get('owner','?')}@{h.get('pid','?')}")
            else:
                parts.append(str(h))
        hs = ",".join(parts)
    return (
        f"容量：nproc={nproc} / loadavg={la} / available={available_mb} MB / "
        f"llama RSS={llama_rss_mb} MB / heavy_slot 持有者={hs}"
    )


def _read_nproc() -> int:
    try:
        return os.cpu_count() or int(Path("/proc/cpuinfo").read_text().count("processor"))
    except Exception:
        return 0


def _read_loadavg() -> tuple[float, float, float]:
    try:
        a, b, c, *_ = Path("/proc/loadavg").read_text().split()
        return float(a), float(b), float(c)
    except Exception:
        return (0.0, 0.0, 0.0)


def _read_available_mb() -> int:
    """優先 MemAvailable（= free -m available）。"""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                kb = int(line.split()[1])
                return kb // 1024
    except Exception:
        pass
    return 0


def _llama_rss_mb() -> int:
    """加總名含 llama-server／ollama runner 之 RSS（KB→MB）。無則 0。"""
    total_kb = 0
    proc = Path("/proc")
    try:
        for p in proc.iterdir():
            if not p.name.isdigit():
                continue
            try:
                cmd = (p / "comm").read_text().strip()
                cmdline = (p / "cmdline").read_text(errors="ignore")
            except Exception:
                continue
            hit = (
                "llama-server" in cmd
                or "llama-server" in cmdline
                or (cmd == "ollama" and "runner" in cmdline)
            )
            if not hit:
                continue
            try:
                for line in (p / "status").read_text().splitlines():
                    if line.startswith("VmRSS:"):
                        total_kb += int(line.split()[1])
                        break
            except Exception:
                continue
    except Exception:
        return 0
    return total_kb // 1024


def _heavy_holders() -> list:
    """唯讀 holder_status；永不 acquire。DB 不可用 → []＋呼叫端註記。"""
    try:
        from augur.core.heavy_slot import holder_status
        st = holder_status()
        return list(st.get("holders") or [])
    except Exception as e:
        return [{"owner": f"(DB不可讀:{type(e).__name__})", "pid": "-", "since": "-"}]


def snapshot() -> dict:
    nproc = _read_nproc()
    loadavg = _read_loadavg()
    available = _read_available_mb()
    llama = _llama_rss_mb()
    holders = _heavy_holders()
    advice = advise_lanes(available_mb=available, nproc=nproc, llama_rss_mb=llama)
    rc = capacity_rc(available_mb=available, load1=loadavg[0], nproc=nproc)
    week = format_week_line(
        nproc=nproc, loadavg=loadavg, available_mb=available,
        llama_rss_mb=llama, holders=holders,
    )
    return {
        "nproc": nproc,
        "loadavg": list(loadavg),
        "available_mb": available,
        "llama_rss_mb": llama,
        "heavy_slot_holders": holders,
        "advice": advice,
        "rc": rc,
        "week_line": week,
        "red_thresholds": {
            "available_mb_lt": RED_AVAILABLE_MB,
            "load1_gt_nproc_x": RED_LOAD_OVER_NPROC,
        },
    }


def _check(*, as_json: bool, week_line_only: bool) -> int:
    snap = snapshot()
    if week_line_only:
        print(snap["week_line"])
        return snap["rc"]
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2, default=str))
        return snap["rc"]
    print(snap["week_line"])
    adv = snap["advice"]
    print(
        f"  建議並行上限（advisory）: 重活={adv['heavy']}／中量={adv['medium']}／"
        f"輕量={adv['light']} —— {adv['note']}"
    )
    print(
        f"  紅燈門檻: available<{RED_AVAILABLE_MB} MB 或 "
        f"load1>nproc×{RED_LOAD_OVER_NPROC} → rc=1；本趟 rc={snap['rc']}"
    )
    print("  紀律: 本支唯讀、不取 heavy_slot、零 FinMind／FRED")
    return snap["rc"]


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # 先驗紅：available 過低必紅
    chk("先驗紅：available=500 → rc=1",
        capacity_rc(available_mb=500, load1=1.0, nproc=12) == 1)
    chk("邊：available=1024 不紅（僅 <）",
        capacity_rc(available_mb=1024, load1=1.0, nproc=12) == 0)
    chk("綠：available=6960 load 正常",
        capacity_rc(available_mb=6960, load1=7.55, nproc=12) == 0)

    # load 病理紅
    chk("先驗紅：load1=25 > 12×2 → rc=1",
        capacity_rc(available_mb=8000, load1=25.0, nproc=12) == 1)
    chk("load1=24 邊上不紅",
        capacity_rc(available_mb=8000, load1=24.0, nproc=12) == 0)

    # 建議表
    a_low = advise_lanes(available_mb=1509, nproc=12, llama_rss_mb=5507)
    chk("低 available ⇒ 重活≤1", a_low["heavy"] <= 1)
    a_hi = advise_lanes(available_mb=6960, nproc=12, llama_rss_mb=647)
    chk("高 available ⇒ 重活=2", a_hi["heavy"] == 2)
    chk("輕量建議 ∈[2,8]", 2 <= a_hi["light"] <= 8)

    line = format_week_line(
        nproc=12, loadavg=(7.55, 7.47, 7.56), available_mb=6960,
        llama_rss_mb=647, holders=[],
    )
    chk("週報行含五欄關鍵字",
        all(k in line for k in ("nproc=", "loadavg=", "available=", "llama RSS=", "heavy_slot")))
    chk("無持有者印「無」", "持有者=無" in line)
    line2 = format_week_line(
        nproc=12, loadavg=(1, 1, 1), available_mb=1000, llama_rss_mb=0,
        holders=[{"owner": "tw_evo", "pid": 1}],
    )
    chk("有持有者印 owner", "tw_evo@1" in line2)

    # 原始碼不 acquire（#35：切掉自測段；並驗 _heavy_holders 真用 holder_status）
    body = Path(__file__).read_text(encoding="utf-8").split("def _selftest")[0]
    chk("不呼叫 HeavySlot.acquire／.acquire(",
        "HeavySlot(" not in body and ".acquire(" not in body)
    chk("_heavy_holders 接 holder_status",
        "holder_status" in body.split("def _heavy_holders")[1].split("def snapshot")[0])

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="並行容量哨兵（M-O9）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--week-line", action="store_true", help="只印週報一行")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    # 無參數＝--check（graceful）
    return _check(as_json=a.json, week_line_only=a.week_line)


if __name__ == "__main__":
    sys.exit(main())
