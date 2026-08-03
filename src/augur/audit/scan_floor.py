"""🎯 掃描器「對象數地板」——「一個對象都沒掃到」不得與「掃過都沒問題」同判綠燈。

白話:靜態掃描器普遍寫成「發現違規→rc=1;否則 rc=0」。於是**掃描範圍整個消失**時
(worktree 內缺目錄／ROOT 推導錯／目錄改名／glob 口徑打錯／`--path` 指到不存在的檔)
掃描器印「0 檔、0 問題」並回 rc=0 ⇒ **事故愈嚴重愈綠**。本模組把「至少要掃到 N 個對象」
寫成可餵真輸入之純函式,供各閘在**真實掃描結果之下游**判紅(#35(2) 絆線位置在下游)。

地板 ≠ 品質:過地板只證明掃描器**有在掃**,不證明結果正確;未過地板則該次掃描之綠燈
一律無效(視同未執行)。三種宣告可疊用——
  數量地板 `FloorCheck`  總對象數 < N 即紅(抓「範圍整個消失」)
  分組地板 `group_checks` 每個掃描根各自 ≥1(抓「總數還夠、但某個根目錄整個不見」)
  錨　　檢 `anchor_checks` 指名檔案必須在實掃集內(不隨 repo 成長腐化,抓「換了一批對象」)

守原則 #15(紅燈必須會亮)· #35(回歸鎖三規則:純函式餵真輸入／下游絆線／禁字面斷言)·
#9/#10(數字出自實掃、可重跑溯源)· #28(零 DB 零 API 零 usage)。
地板常數住各消費端(安全繫於機械閘之工程門檻屬邏輯側,#29(b) 同 vendor 基線 caliber 之豁免款)。
消費者:`scripts/check_cmd_matrix.py`·`scripts/check_false_assertions.py`·`scripts/check_vendor_binding.py`
SSOT=`reports/augur_optimization_master_plan_20260803.md` M-G2(源:r4 §7.4-3「空集合＝綠燈」家族根因)

執行指令矩陣:
  python -m augur.audit.scan_floor             # 印用途+公開入口(唯讀)
  python -m augur.audit.scan_floor --selftest  # 純紅綠自測(免 DB 免 API、零 usage)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class FloorCheck:
    """一項地板宣告:某對象集實掃到 `observed` 個,低於 `floor` 即紅。"""

    label: str
    observed: int
    floor: int

    @property
    def ok(self) -> bool:
        return self.observed >= self.floor


def shortfalls(checks):
    """→ 未達地板者(純函式)。"""
    return [c for c in checks if not c.ok]


def anchor_checks(seen, anchors):
    """錨檢:每個 anchor 必須出現在實掃對象集 `seen` 內(observed 0/1、floor 1)。純函式。

    數量地板抓不到「換了一批對象但總數仍夠」(如 ROOT 指到另一棵樹);錨檢抓得到。
    """
    seen = set(seen)
    return [FloorCheck(f"錨:{a}", int(a in seen), 1) for a in anchors]


def group_checks(observed, floor=1, prefix="分組"):
    """每組(如各掃描根目錄)各自的地板。`observed`={組名: 實掃數}。純函式。"""
    return [FloorCheck(f"{prefix}:{k}", int(n), floor) for k, n in sorted(dict(observed).items())]


def verdict(scanner, checks):
    """(掃描器名, FloorCheck 列) → (rc, 訊息列)。純函式——呼叫端負責列印。

    **空宣告即紅**:`checks` 為空代表這支閘沒有宣告任何地板,那正是本模組要消滅的形狀
    (無對象可比 ⇒ 恆綠),故不當作「全部通過」。
    """
    if not checks:
        return 1, [f"✗ {scanner} 未宣告任何對象數地板——無地板之綠燈不成立(空宣告即紅)。"]
    bad = shortfalls(checks)
    if not bad:
        detail = "; ".join(f"{c.label}={c.observed}≥{c.floor}" for c in checks)
        return 0, [f"✓ {scanner} 對象數地板:{detail}"]
    msgs = [f"✗ {scanner} **實掃對象數低於地板**——本次掃描之綠燈無效(視同未執行):"]
    msgs += [f"  ↓ {c.label}:實掃 {c.observed} < 地板 {c.floor}" for c in bad]
    msgs.append("  這多半不是「沒有問題」,而是掃描範圍消失:ROOT 推導錯／worktree 缺目錄／"
                "目錄改名／glob 口徑打錯／--path 指到不存在的檔。")
    msgs.append("  處置:先修掃描範圍再重跑;確係 repo 真的縮小,才調整該閘之地板常數(改動須留痕)。")
    return 1, msgs


def enforce(scanner, checks, out=None):
    """薄 IO 包裝:跑 `verdict` 並列印(紅走 stderr)。→ rc。"""
    rc, msgs = verdict(scanner, checks)
    stream = out if out is not None else (sys.stderr if rc else sys.stdout)
    for m in msgs:
        print(m, file=stream)
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # 綠/紅雙向(純函式、真值域邊界)
    chk("實掃 ≥ 地板 ⇒ 綠", verdict("s", [FloorCheck("檔", 468, 300)])[0] == 0)
    chk("邊界 observed==floor ⇒ 綠", verdict("s", [FloorCheck("檔", 300, 300)])[0] == 0)
    chk("實掃 0 ⇒ 紅(本模組存在之理由)", verdict("s", [FloorCheck("檔", 0, 1)])[0] == 1)
    chk("低於地板 ⇒ 紅", verdict("s", [FloorCheck("檔", 299, 300)])[0] == 1)
    chk("一項達標一項未達 ⇒ 仍紅(不許以總數掩蓋)",
        verdict("s", [FloorCheck("a", 999, 1), FloorCheck("b", 0, 1)])[0] == 1)
    chk("空宣告 ⇒ 紅(無地板之閘不得算通過)", verdict("s", [])[0] == 1)

    # 錨檢/分組(餵真形狀:集合與 mapping)
    chk("錨在實掃集內 ⇒ 綠",
        verdict("s", anchor_checks({"a.py", "b.py"}, ("a.py",)))[0] == 0)
    chk("錨不在實掃集內 ⇒ 紅(範圍被換掉之偵測)",
        verdict("s", anchor_checks({"b.py"}, ("a.py",)))[0] == 1)
    chk("分組:某根目錄 0 檔 ⇒ 紅(總數夠也不放行)",
        verdict("s", group_checks({"src": 400, "ops": 0}))[0] == 1)
    chk("分組:各根皆有 ⇒ 綠", verdict("s", group_checks({"src": 400, "ops": 12}))[0] == 0)

    # 訊息含實測數字(可溯源;非字面斷言——由真值算出)
    _rc, _msgs = verdict("scanner_x", [FloorCheck("檔", 7, 99)])
    chk("紅訊息帶出實掃/地板兩數", "7" in _msgs[1] and "99" in _msgs[1])

    # 突變驗紅:偵測器(shortfalls)被弱化為恆空 ⇒ 上列紅例不再紅 ⇒ 證明上列非恆真
    _saved = globals()["shortfalls"]
    globals()["shortfalls"] = lambda checks: []
    try:
        chk("突變:shortfalls 恆空後 0<1 不再判紅(證明紅例非恆真)",
            verdict("s", [FloorCheck("檔", 0, 1)])[0] == 0)
    finally:
        globals()["shortfalls"] = _saved
    chk("突變復原後 0<1 再度判紅", verdict("s", [FloorCheck("檔", 0, 1)])[0] == 1)

    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開入口(唯讀):")
    for fn in (shortfalls, anchor_checks, group_checks, verdict, enforce):
        print(f"  {fn.__name__}  {fn.__doc__.splitlines()[0]}")
    print(f"  {FloorCheck.__name__}  {FloorCheck.__doc__.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
