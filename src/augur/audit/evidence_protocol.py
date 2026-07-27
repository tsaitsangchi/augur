"""🎯 證據協定(C4)——「live 臂須同時勝過 floor 與 mismatched 才有證據力」寫成程式而非註解。

白話:三軸自進化(RAWEVO/TWEVO/LAIEVO)各自產「有沒有變好」的數字,本模組是唯一判讀器:
  給每個對照臂的指標值,回四級證據力 none/incomparable/weak/scoped_established;
  兩把尺(suite_id+code_hash)不同即 fail-loud 拒比——0.256→0.492 跨尺假進步(2026-07-26
  舊尺失效實證)不得再發生。TW/RAW 落 `evolution_evidence_run`、LAI 落其評測帳本(eval run 表;
  表名不寫此處=laievo 字面隔離掃描所轄),三軸共用本檔同一份純函式(#12 單一住所)。
守原則 #15(誠實:對照臂缺席=不可比,非通過)#9(數字可溯源)#12。SSOT=v2 總控 §3.3 C4/§7 A4。

臂語意(ARMS 順序即強度階梯):
  ceiling    理想答案/滿分基準——尺可被滿足之證明(非假嚴格)
  floor      零知識常數樣板——任何宣稱至少要贏它
  shuffled   同層答錯內容——贏它才證明「內容」而非「行為類別」
  mismatched 跨層選錯行為——量級對、類別錯(volume_gini_60d 型失效)
  live       受測者本人
TWEVO 對映(v2 §3.4 M-1;呼叫端負責換算):標籤置換臂 95 分位→floor 語意、
  隨機特徵臂 95 分位→mismatched 語意。指標一律「越高越好」;方向相反(如 Brier)呼叫端先取負。

執行指令矩陣:
  python -m augur.audit.evidence_protocol             # 印用途+公開入口(唯讀)
  python -m augur.audit.evidence_protocol --selftest  # 純紅綠自測(免 DB 免 API、零 usage)
"""
from __future__ import annotations

import sys

ARMS = ("ceiling", "floor", "shuffled", "mismatched", "live")
LEVELS = ("none", "incomparable", "weak", "scoped_established")


class ScaleMismatch(ValueError):
    """跨尺比較——兩組 (suite_id, code_hash) 不同即拒比(fail-loud,非警告)。"""


def same_scale(a, b):
    """兩把尺是否同一把:a、b 各為 (suite_id, code_hash)。純判斷、不拋錯。"""
    return tuple(a) == tuple(b)


def require_same_scale(a, b, context=""):
    """跨尺 fail-loud:不同尺一律 raise ScaleMismatch,絕不靜默混比(2026-07-26 教訓機械化)。"""
    if not same_scale(a, b):
        raise ScaleMismatch(
            f"跨尺拒比{'(' + context + ')' if context else ''}:"
            f"{tuple(a)} != {tuple(b)}——同 suite_id+code_hash 才可比,換尺即另起爐灶")


def evidence_level(metric_by_arm):
    """四級證據力判讀(鐵則本體)。輸入 {arm: float|None},鍵限 ARMS,值越高越好。

    incomparable  live/floor/mismatched 任一缺席(缺對照=不可比,非通過);或 ceiling 在場
                  卻未同時高於 floor 與 mismatched(尺自身無鑑別力=壞尺,量什麼都無意義)
    none          live 未同時**嚴格**勝過 floor 與 mismatched(平手不算勝——#15)
    weak          勝 floor+mismatched 但 shuffled 在場且未勝之——只證「行為類別選對」,
                  不證內容(A@L3/L4 shuffled=0.967 實證:此格任何分數都證不了內容)
    scoped_established  同時勝 floor+mismatched,且 shuffled 缺席或亦被勝——證據力成立,
                  但僅及該格(scoped;如 F@L1),不得外推為整體「更聰明」
    """
    unknown = set(metric_by_arm) - set(ARMS)
    if unknown:
        raise ValueError(f"未知臂 {sorted(unknown)}(合法臂={ARMS})")
    live = metric_by_arm.get("live")
    floor = metric_by_arm.get("floor")
    mism = metric_by_arm.get("mismatched")
    shuf = metric_by_arm.get("shuffled")
    ceil = metric_by_arm.get("ceiling")
    if live is None or floor is None or mism is None:
        return "incomparable"
    if ceil is not None and not (ceil > floor and ceil > mism):
        return "incomparable"
    if not (live > floor and live > mism):
        return "none"
    if shuf is not None and not (live > shuf):
        return "weak"
    return "scoped_established"


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    def _raises(fn, exc):
        try:
            fn()
        except exc:
            return True
        except Exception:  # noqa: BLE001
            return False
        return False

    # 實證錨:2026-07-26/27 兩機逐位元一致的四臂實測值
    chk("F@L1 behavior 實測(live .933 vs floor 0/mism 0/shuf .167)=scoped_established",
        evidence_level({"ceiling": 1.0, "floor": 0.0, "shuffled": 0.167,
                        "mismatched": 0.0, "live": 0.933}) == "scoped_established")
    chk("A@L3 實測(shuffled=.967 與 live 平手)=weak——只證行為類別、不證內容",
        evidence_level({"ceiling": 1.0, "floor": 0.0, "shuffled": 0.967,
                        "mismatched": 0.0, "live": 0.967}) == "weak")
    chk("live 低於零知識地板(舊尺 0.492<0.654 實證形態)=none",
        evidence_level({"floor": 0.654, "mismatched": 0.0, "live": 0.492}) == "none")
    chk("與 floor 平手=none(平手不算勝,#15)",
        evidence_level({"floor": 0.5, "mismatched": 0.1, "live": 0.5}) == "none")
    chk("缺 mismatched 臂=incomparable(缺對照非通過)",
        evidence_level({"floor": 0.0, "live": 0.9}) == "incomparable")
    chk("缺 live=incomparable",
        evidence_level({"floor": 0.0, "mismatched": 0.0}) == "incomparable")
    chk("壞尺(ceiling 未高於 mismatched)=incomparable",
        evidence_level({"ceiling": 0.2, "floor": 0.0, "mismatched": 0.3,
                        "live": 0.9}) == "incomparable")
    chk("無 shuffled 而勝雙控制臂=scoped_established(鐵則僅要求 floor+mismatched)",
        evidence_level({"floor": 0.1, "mismatched": 0.2, "live": 0.8}) == "scoped_established")
    chk("回值必屬四級枚舉",
        all(evidence_level(m) in LEVELS for m in (
            {}, {"live": 1.0}, {"floor": 0, "mismatched": 0, "live": 1})))
    chk("未知臂 fail-loud", _raises(lambda: evidence_level({"lve": 1.0}), ValueError))
    chk("同尺可比", same_scale(("s1", "h1"), ("s1", "h1")))
    chk("跨尺 fail-loud(異 code_hash)",
        _raises(lambda: require_same_scale(("s1", "h1"), ("s1", "h2")), ScaleMismatch))
    chk("跨尺 fail-loud(異 suite_id)",
        _raises(lambda: require_same_scale(("s1", "h1"), ("s2", "h1")), ScaleMismatch))
    chk("確定性:同輸入同輸出",
        evidence_level({"floor": 0, "mismatched": 0, "live": 1})
        == evidence_level({"floor": 0, "mismatched": 0, "live": 1}))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開入口(唯讀):")
    print(f"  ARMS={ARMS}")
    print(f"  LEVELS={LEVELS}")
    for fn in (same_scale, require_same_scale, evidence_level):
        print(f"  {fn.__name__}  {fn.__doc__.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
