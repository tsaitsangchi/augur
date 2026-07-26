#!/usr/bin/env python
"""三軸計畫文件機械斷言 — 取代人工數字之一致性稽核(V2 Phase 2.6/C8,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):同一條「最機械」的驗收,TRI-v1 原文寫「三處」、兩面獨立審查各數出 6 與 7——
   **手數的驗收條件本身就是假綠來源**。本支把計畫文件的跨檔一致性寫成機械斷言:
   ①五份前身計畫皆有「SSOT=v2」指針行(舊碼/舊契約由指針統一失效,不必逐句獵殺)
   ②`DUAL-IFACE-yes` 於 v2 明列死碼 ③LAIEVO 計畫零裸 `--defer`(須 --defer-heavy)
   ④契約必要欄(C2 硬要求)於 v2 DDL 章全數出現 ⑤三軸名+核心拍板碼於 v2 §12 逐字在冊。
   缺漏 exit≠0(供 CI/pre-commit 掛勾);零 DB 零網路零 usage(#28)。
守 #15(驗收不手數)· #12(斷言單一住所)· #29a/d。
執行指令矩陣:
  python scripts/check_plan_consistency.py            # 全量斷言(rc=0 綠/≠0 列缺漏)
  python scripts/check_plan_consistency.py --selftest # 零檔案紅綠(斷言邏輯)
"""
import pathlib
import sys

import _bootstrap  # noqa: F401

_R = pathlib.Path(__file__).resolve().parents[1] / "reports"
V2 = "augur_self_evolution_master_plan_v2_20260726.md"
PREDECESSORS = (
    "augur_triple_self_evolution_master_plan_20260726.md",
    "augur_dual_self_evolution_interface_20260726.md",
    "augur_raw_data_self_evolution_loop_plan_20260726.md",
    "augur_tw_prediction_self_evolution_loop_plan_20260726.md",
    "augur_local_ai_route_b_no_gpu_plan_20260726.md",
)
CONTRACT_COLS = ("iteration_uid", "briefs_in", "briefs_out", "hints_in", "hints_out",
                 "consecutive_no_gain", "steps_json", "gate_ref", "gain_basis")
VERBATIM_CODES = ("RAWEVO", "TWEVO", "LAIEVO", "FZ-keep", "GATE-keep", "PME-AUTO-B",
                  "V2-SUNSET", "GATE-raise", "TRI-HALT")


def _assertions(read):
    """read(name)->str|None。回缺漏清單(空=全綠)。純函式供 selftest 注入假檔。"""
    out = []
    v2 = read(V2)
    if v2 is None:
        return [f"✗ v2 SSOT 檔不存在:{V2}"]
    for name in PREDECESSORS:
        txt = read(name)
        if txt is None:
            out.append(f"✗ 前身檔缺:{name}")
        elif V2 not in txt:
            out.append(f"✗ {name}:無「SSOT=v2」指針行(舊契約/舊碼未被統一失效)")
    if "DUAL-IFACE-yes" not in v2 or "死碼" not in v2:
        out.append("✗ v2 未把 DUAL-IFACE-yes 明列死碼")
    lai = read(PREDECESSORS[4]) or ""
    for i, line in enumerate(lai.splitlines(), 1):
        if "--defer" in line and "--defer-heavy" not in line:
            out.append(f"✗ LAIEVO 計畫 L{i}:裸 `--defer`(TRI 契約名=--defer-heavy,同名歧異=假綠源)")
    for col in CONTRACT_COLS:
        if col not in v2:
            out.append(f"✗ v2 缺契約必要欄字面:{col}(C2 硬要求)")
    for code in VERBATIM_CODES:
        if code not in v2:
            out.append(f"✗ v2 缺逐字拍板碼/軸名:{code}")
    return out


def run():
    def read(name):
        p = _R / name
        return p.read_text(encoding="utf-8") if p.exists() else None

    miss = _assertions(read)
    if miss:
        print(f"計畫一致性:{len(miss)} 缺漏")
        for m in miss:
            print("  " + m)
        return 1
    print(f"✓ 計畫一致性全綠:{len(PREDECESSORS)} 前身檔皆掛 v2 指針、DUAL-IFACE-yes 死碼在冊、"
          f"零裸 --defer、{len(CONTRACT_COLS)} 契約欄+{len(VERBATIM_CODES)} 拍板碼逐字在冊")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    good = {V2: "DUAL-IFACE-yes 死碼 " + " ".join(CONTRACT_COLS) + " " + " ".join(VERBATIM_CODES)}
    for p in PREDECESSORS:
        good[p] = f"SSOT={V2}"
    chk("全綠案例=零缺漏", _assertions(lambda n: good.get(n)) == [])
    bad = dict(good); bad[PREDECESSORS[0]] = "無指針"
    chk("缺指針被抓", any("指針" in m for m in _assertions(lambda n: bad.get(n))))
    bad2 = dict(good); bad2[PREDECESSORS[4]] = f"SSOT={V2}\n用 --defer 跳過"
    chk("裸 --defer 被抓", any("--defer" in m for m in _assertions(lambda n: bad2.get(n))))
    bad3 = dict(good); bad3[V2] = good[V2].replace("iteration_uid", "")
    chk("缺契約欄被抓", any("iteration_uid" in m for m in _assertions(lambda n: bad3.get(n))))
    chk("v2 缺檔=單一致命缺漏", _assertions(lambda n: None) == [f"✗ v2 SSOT 檔不存在:{V2}"])
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
