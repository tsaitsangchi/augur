"""🎯 TWEVO 迭代之步圖／停損／增益比較純函式——零 DB 零 API,driver 的判斷全住這裡。

白話:TWEVO 一輪走 I0→I9(假說 map→候選建值→漏斗→local-gates→雙綠?→APPLY→重訓→對局→回饋→停損)。
本模組只回答三個問題,且**只用純資料**(不連庫、不跑 script):
  ① 下一步該走哪一步(`next_step`;半途中斷可續、跳步不合法)
  ② 這輪相對上輪有沒有變好(`compare_gain`;**尺不同→`incomparable`、不是「沒進步」**)
  ③ 該不該停損(`should_stop`;`incomparable` 不計數——不可比不等於沒增益,計進去會用假訊號逼停)

⚠ 兩條與 driver 分家的理由:純函式可零依賴自測(#18/#29),而 driver 只負責跑 subprocess 與落帳;
   判準寫在 driver 裡就沒人能在不連庫的情況下驗它。
守 #15(不可比誠實回 incomparable,不冒充 gain=false)· #12(停損 N 與 gain 語意單一住所)· #29。

執行指令矩陣:
  python -m augur.philosophy.iteration              # 印用途+步圖+公開入口(唯讀)
  python -m augur.philosophy.iteration --selftest   # 純紅綠自測(免 DB 免 API,零 usage)
"""
from __future__ import annotations

import sys
from typing import Any, Mapping, Sequence

# 步圖(TWEVO 計畫 §4 圖;heavy=須經 heavy_slot 單槽鎖;writes=會寫生產表)
STEPS: tuple[dict[str, Any], ...] = (
    {"key": "I0", "name": "假說 map 擴充/精煉", "heavy": False, "writes": False},
    {"key": "I1", "name": "候選建值→feature_candidate_values", "heavy": True, "writes": False},
    {"key": "I2", "name": "漏斗預篩(HAC/去相關/增量)", "heavy": True, "writes": False},
    {"key": "I3", "name": "local-gates(run_philosophy_evolution)", "heavy": True, "writes": False},
    {"key": "I4", "name": "雙綠判讀(driver 讀 queue gate_json)", "heavy": False, "writes": False},
    {"key": "I5", "name": "APPLY(apply_evolution_promotions)", "heavy": False, "writes": True},
    {"key": "I6", "name": "prodset 重訓+hotpath 驗證", "heavy": True, "writes": True},
    {"key": "I7", "name": "arena 對局/revalidation", "heavy": True, "writes": True},
    {"key": "I8", "name": "證據回饋(gap ledger/brief)", "heavy": False, "writes": False},
    {"key": "I9", "name": "停損判準", "heavy": False, "writes": False},
)
STEP_KEYS: tuple[str, ...] = tuple(s["key"] for s in STEPS)
STOP_N = 3                      # TWEVO-N=3(計畫 §7「無增益停損」;改數字須改此處單一住所)
GAIN_BASES = ("dual_green_delta", "prodset_delta", "arena_prereg", "none", "incomparable")
# snapshot 口徑版本(2026-08-01 Steward 裁決 prodset_delta 基準):v2 起 prodset_active_n 由
# 全域 active 計數改為 **source_run_id 限縮本輪**(人在輪外的手動晉升不記自動輪功勞)。
# gate_scale 指紋只抓閘門檻換尺、抓不到「摘要本身換口徑」——故靠版本鍵:版本不符=不比。
SNAPSHOT_VER = 2


def step_meta(key: str) -> dict[str, Any]:
    for s in STEPS:
        if s["key"] == key:
            return dict(s)
    raise KeyError(f"未知步驟 {key}(合法:{','.join(STEP_KEYS)})")


def final_attempts(steps_json: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    """每步之**末次嘗試**紀錄（登錄冊 A5，2026-08-01）。純函式。

    一步的成敗以其**最後一次嘗試**為準——重試成功即成功；歷史失敗全史仍在
    steps_json（誠實不刪），但不再冒充「該步失敗」。實犯：tw-20260728-r01 之
    I3 rc 序列 −15,−15,0（末次成功），舊邏輯仍把輪判 failed 且 next_step 永遠
    叫人重跑 I3。
    """
    fa: dict[str, Mapping[str, Any]] = {}
    for rec in steps_json:
        key = rec.get("step")
        if key in STEP_KEYS:
            fa[key] = rec                   # 後者覆前者＝末次
    return fa


def retried_ok_steps(steps_json: Sequence[Mapping[str, Any]]) -> list[str]:
    """曾敗後重試成功之步（依 STEP_KEYS 序）——「曾敗」之誠實留痕，供 gain_evidence。"""
    ever_failed = {r.get("step") for r in steps_json
                   if r.get("step") in STEP_KEYS and r.get("rc") not in (0, None)}
    fa = final_attempts(steps_json)
    return [k for k in STEP_KEYS
            if k in ever_failed and fa.get(k, {}).get("rc") == 0]


def next_step(steps_json: Sequence[Mapping[str, Any]]) -> str | None:
    """回下一個該跑的步驟碼;全跑完回 None。

    判準（A5 修正）:依 **每步末次嘗試**——canonical 序上第一個「無紀錄或末次 rc≠0」之步。
    末次失敗 → 回該步本身(重試不跳過;跳步=拿舊證據餵新步,#15)；
    重試已成功 → 不再回該步（舊邏輯遇**歷史**失敗即 return,重試成功後仍叫人重跑）。
    """
    fa = final_attempts(steps_json)
    for key in STEP_KEYS:
        rec = fa.get(key)
        if rec is None or rec.get("rc") != 0:
            return key
    return None


def incomparable_reason(prev: Mapping[str, Any] | None, cur: Mapping[str, Any]) -> str | None:
    """兩輪摘要不可直比之原因;可比回 None。判準單一住所(#12)——driver 只印、不重算。

    'no_prev'=無前輪;'snapshot_ver'=摘要口徑版本不同(如 v2 起 prodset_active_n 由全域改
    run-scoped——gate_scale 指紋抓不到這種換尺,舊全域 prev 對新 scoped cur 直比=拿舊尺量新數);
    'gate_scale'=閘口徑換過(GATE-raise 同型)。
    """
    if prev is None:
        return "no_prev"
    if prev.get("snapshot_ver") != cur.get("snapshot_ver"):
        return "snapshot_ver"
    if prev.get("gate_scale") != cur.get("gate_scale"):
        return "gate_scale"
    return None


def compare_gain(prev: Mapping[str, Any] | None, cur: Mapping[str, Any]) -> tuple[bool | None, str]:
    """回 (gain, gain_basis)。**尺不同或無前輪 → (None,'incomparable')**,不是 (False,'none')。

    參數為兩輪之數字摘要:{'snapshot_ver':int, 'dual_green_n':int, 'prodset_active_n':int,
    'arena_prereg_win':bool|None, 'gate_scale':str}。`gate_scale`=閘的口徑指紋(如 GATE-raise 後之
    p95 門檻);兩輪口徑不同時數字不可比——這正是 2026-07-26 LAIEVO 量尺失效的同型病,故此處硬回
    incomparable(承 evidence_protocol)。`snapshot_ver` 不符同理(摘要本身換口徑,見 SNAPSHOT_VER)。
    """
    if incomparable_reason(prev, cur):
        return None, "incomparable"
    if cur.get("arena_prereg_win") is True:
        return True, "arena_prereg"
    d_green = (cur.get("dual_green_n") or 0) - (prev.get("dual_green_n") or 0)
    if d_green > 0:
        return True, "dual_green_delta"
    d_act = (cur.get("prodset_active_n") or 0) - (prev.get("prodset_active_n") or 0)
    if d_act > 0:
        return True, "prodset_delta"
    return False, "none"


def next_no_gain_count(prev_count: int, gain: bool | None, basis: str) -> int:
    """停損計數遞推:gain=True 歸零;**incomparable 原地不動**(不可比≠無增益);其餘 +1。"""
    if basis == "incomparable" or gain is None:
        return prev_count
    return 0 if gain else prev_count + 1


def should_stop(consecutive_no_gain: int, n: int = STOP_N) -> bool:
    """達 N 連續無增益 → 停損(status='stopped_no_gain';重啟＝人,R5)。"""
    return consecutive_no_gain >= n


def stop_reason_text(consecutive_no_gain: int, n: int = STOP_N) -> str:
    return (f"連續 {consecutive_no_gain} 輪無增益(門檻 TWEVO-N={n});"
            f"不可比之輪未計入;重啟須人裁(V2-AUTOADVANCE R5)")


def step_record(step: str, script: str, argv: Sequence[str], rc: int,
                started: str, finished: str, **extra: Any) -> dict[str, Any]:
    """組一筆 steps_json 元素——**rc/started/finished 三鍵恆在**(驗收 A3 之機械要件)。"""
    rec = {"step": step, "script": script, "argv": list(argv),
           "rc": rc, "started": started, "finished": finished}
    rec.update(extra)
    return rec


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("空帳→首步 I0", next_step([]) == "I0")
    chk("I0 成功→下一步 I1", next_step([{"step": "I0", "rc": 0}]) == "I1")
    chk("**失敗步重試不跳過**", next_step([{"step": "I0", "rc": 0}, {"step": "I1", "rc": 2}]) == "I1")
    chk("全跑完回 None", next_step([{"step": k, "rc": 0} for k in STEP_KEYS]) is None)
    # A5（2026-08-01）：以 r01 **真實步序**為 fixture——I3 兩次 rc=-15 後重試 rc=0。
    # 舊邏輯下兩條**必紅**（next_step 遇歷史失敗即 return I3；close 判任一步曾敗即敗）。
    _r01 = ([{"step": k, "rc": 0} for k in ("I0", "I1", "I2")]
            + [{"step": "I3", "rc": -15}, {"step": "I3", "rc": -15}]
            + [{"step": "I0", "rc": 0}, {"step": "I3", "rc": 0}]
            + [{"step": k, "rc": 0} for k in ("I4", "I5", "I6", "I7", "I8", "I9")])
    chk("A5:重試成功後 next_step 不再叫重跑（末次為準）", next_step(_r01) is None)
    chk("A5:final_attempts 之 I3 為末次 rc=0", final_attempts(_r01)["I3"]["rc"] == 0)
    chk("A5:曾敗重試成功者列 retried_ok（誠實留痕非抹除）", retried_ok_steps(_r01) == ["I3"])
    chk("A5:末次仍敗 ⇒ next_step 回該步（重試語意保留）",
        next_step([{"step": "I0", "rc": 0}, {"step": "I1", "rc": 2},
                   {"step": "I1", "rc": 3}]) == "I1")
    chk("A5:從未失敗者不入 retried_ok（綠燈也要驗得到）",
        retried_ok_steps([{"step": "I0", "rc": 0}]) == [])
    chk("步圖十步 I0..I9", STEP_KEYS == tuple(f"I{i}" for i in range(10)))
    chk("未知步驟 raise 非靜默", _raises(lambda: step_meta("I99")))

    base = {"dual_green_n": 0, "prodset_active_n": 1, "gate_scale": "p95=2.643"}
    chk("**無前輪=incomparable 非 none**", compare_gain(None, base) == (None, "incomparable"))
    chk("**尺換過=incomparable**(量尺失效同型病)",
        compare_gain({**base, "gate_scale": "p95=2.000"}, base) == (None, "incomparable"))
    chk("新雙綠→dual_green_delta",
        compare_gain(base, {**base, "dual_green_n": 1}) == (True, "dual_green_delta"))
    chk("prodset 增→prodset_delta",
        compare_gain(base, {**base, "prodset_active_n": 2}) == (True, "prodset_delta"))
    chk("arena 預註冊勝優先", compare_gain(base, {**base, "arena_prereg_win": True})[1] == "arena_prereg")
    chk("皆無→(False,'none')", compare_gain(base, base) == (False, "none"))
    chk("basis 全在白名單", all(compare_gain(p, c)[1] in GAIN_BASES
                              for p, c in ((None, base), (base, base),
                                           (base, {**base, "dual_green_n": 1})))
        )
    # prodset_delta 基準(2026-08-01 Steward 裁決):v2 起 prodset_active_n 換口徑(全域→run-scoped),
    # gate_scale 指紋抓不到此換尺——版本鍵不符必須硬回 incomparable,不得把口徑差冒充增益。
    v2 = {**base, "snapshot_ver": SNAPSHOT_VER}
    chk("**跨版直比=incomparable**(舊全域 prev 無版本鍵、新 scoped cur 有=不比)",
        compare_gain(base, v2) == (None, "incomparable"))
    chk("同版(皆 v2)仍可比:prodset 增→prodset_delta",
        compare_gain(v2, {**v2, "prodset_active_n": 2}) == (True, "prodset_delta"))
    chk("incomparable_reason 四態(no_prev/snapshot_ver/gate_scale/可比 None)",
        (incomparable_reason(None, v2), incomparable_reason(base, v2),
         incomparable_reason({**v2, "gate_scale": "p95=2.000"}, v2),
         incomparable_reason(v2, v2)) == ("no_prev", "snapshot_ver", "gate_scale", None))
    chk("SNAPSHOT_VER 現版=2(scoped prodset 口徑;升版須連動 driver _snapshot)", SNAPSHOT_VER == 2)

    chk("**incomparable 不推進停損計數**", next_no_gain_count(2, None, "incomparable") == 2)
    chk("無增益 +1", next_no_gain_count(2, False, "none") == 3)
    chk("有增益歸零", next_no_gain_count(2, True, "dual_green_delta") == 0)
    chk("達 N=3 停損", should_stop(3) and not should_stop(2))
    chk("停損理由含重啟須人裁", "人裁" in stop_reason_text(3))

    r = step_record("I3", "run_philosophy_evolution.py", ["--local-gates"], 0, "t0", "t1", n=5)
    chk("**step_record 恆含 rc/started/finished**(A3)",
        all(k in r for k in ("step", "script", "argv", "rc", "started", "finished")))
    chk("extra 可攜", r["n"] == 5)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def _raises(fn) -> bool:
    try:
        fn()
    except Exception:  # noqa: BLE001
        return True
    return False


def main(argv: Sequence[str] | None = None) -> int:
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("步圖:")
    for s in STEPS:
        flags = ("重活 " if s["heavy"] else "") + ("寫生產表" if s["writes"] else "唯讀")
        print(f"  {s['key']}  {s['name']:38} [{flags}]")
    print("公開入口:")
    print("  next_step(steps_json) -> 'I3'|None   compare_gain(prev,cur) -> (gain,basis)")
    print("  next_no_gain_count(n,gain,basis)     should_stop(n) / stop_reason_text(n)")
    print("  step_record(step,script,argv,rc,started,finished,**extra)")
    print("  incomparable_reason(prev,cur) -> 'no_prev'|'snapshot_ver'|'gate_scale'|None")
    print(f"  常數:STOP_N={STOP_N}(TWEVO-N=3)  SNAPSHOT_VER={SNAPSHOT_VER}  GAIN_BASES={GAIN_BASES}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
