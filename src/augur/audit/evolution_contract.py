"""🎯 跨軸交換物契約(C7)——brief/1、hint/1、xnotify/1 的唯一 validator(產生端消費端共用)。

白話:三軸與 advisor 之間傳遞的檔案(brief 情境註記/hint 假說提示/xnotify 佈告)若沒有機械
契約,欄名歧異與措辭走私會靜默累積(TRI-v1 實證:兩份文件指向兩個都不存在的欄)。本模組把
契約寫成程式:首欄 schema 版本、未知欄位 fail-closed、claims 上限、**禁數值陣列**(panel
走私的機械封殺)、措辭黑名單(可交易/確立級/已解凍/更準/更聰明/答得更好——P/A 只證行為
類別,「更準」是尺撐不起的宣稱)。
守 #15(措辭閘)#8(禁數值陣列=面板不入語料)#12(單一住所:產消同一份)。SSOT=v2 總控 §3.3 C7。

執行指令矩陣:
  python -m augur.audit.evolution_contract             # 印用途+公開入口(唯讀)
  python -m augur.audit.evolution_contract --selftest  # 純紅綠自測(免 DB 免 API、零 usage)
"""
from __future__ import annotations

import re
import sys

SCHEMAS = ("brief/1", "hint/1", "xnotify/1")
CLAIM_LEVELS = ("ledger_fact", "paper", "gap_debt")
AXES = ("raw", "tw", "lai")
MAX_CLAIMS = 20
# 措辭黑名單:v2 C7 三舊詞+LAI 側三假兆詞。掃全部字串值(巢狀)。
BLACKLIST = ("可交易", "確立級", "已解凍", "更準", "更聰明", "答得更好")
ITERATION_UID_RE = re.compile(r"^(tw|lai|raw)-[0-9]{8}-r[0-9]{2}$")

_BRIEF_TOP = {"schema", "source_axis", "as_of", "claims"}
_BRIEF_CLAIM = {"claim_level", "text", "ref"}
_HINT_TOP = {"schema", "from_axis", "dedup_key", "text", "provenance", "n_obs"}
_XNOTIFY_TOP = {"schema", "from_axis", "note"}


def _walk_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_strings(v)


def _has_numeric_array(obj) -> bool:
    """任何「全數值且長度≥2」的陣列=禁(panel/數值序列走私的機械封殺;單一數字純量可)。"""
    if isinstance(obj, (list, tuple)):
        if len(obj) >= 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in obj):
            return True
        return any(_has_numeric_array(x) for x in obj)
    if isinstance(obj, dict):
        return any(_has_numeric_array(v) for v in obj.values())
    return False


def blacklist_hits(obj) -> list[str]:
    """回被命中的黑名單詞(去重、依 BLACKLIST 序);空=乾淨。"""
    text = " ".join(_walk_strings(obj))
    return [w for w in BLACKLIST if w in text]


def valid_iteration_uid(uid) -> bool:
    return isinstance(uid, str) and bool(ITERATION_UID_RE.match(uid))


def _err_unknown(obj: dict, allowed: set, where: str) -> list[str]:
    unknown = set(obj) - allowed
    return [f"{where} 未知欄位(fail-closed): {sorted(unknown)}"] if unknown else []


def validate(obj, kind: str) -> list[str]:
    """回錯誤清單;空 list=合格。kind ∈ {'brief','hint','xnotify'}。純函式、零 IO。"""
    errs: list[str] = []
    if not isinstance(obj, dict):
        return [f"頂層須為 object,得 {type(obj).__name__}"]
    want = f"{kind}/1"
    if want not in SCHEMAS:
        return [f"未知 kind '{kind}'(合法={[s.split('/')[0] for s in SCHEMAS]})"]
    if obj.get("schema") != want:
        errs.append(f"schema 首欄須='{want}',得 {obj.get('schema')!r}")
    if _has_numeric_array(obj):
        errs.append("含數值陣列(禁:panel/數值序列不得入交換物,#8)")
    hits = blacklist_hits(obj)
    if hits:
        errs.append(f"措辭黑名單命中: {hits}")
    if kind == "brief":
        errs += _err_unknown(obj, _BRIEF_TOP, "brief 頂層")
        if obj.get("source_axis") not in AXES:
            errs.append(f"source_axis 須∈{AXES}")
        claims = obj.get("claims")
        if not isinstance(claims, list) or not claims:
            errs.append("claims 須為非空 list")
        else:
            if len(claims) > MAX_CLAIMS:
                errs.append(f"claims={len(claims)} > 上限 {MAX_CLAIMS}")
            for i, c in enumerate(claims):
                if not isinstance(c, dict):
                    errs.append(f"claims[{i}] 須為 object")
                    continue
                errs += _err_unknown(c, _BRIEF_CLAIM, f"claims[{i}]")
                if c.get("claim_level") not in CLAIM_LEVELS:
                    errs.append(f"claims[{i}].claim_level 須∈{CLAIM_LEVELS}")
                if not isinstance(c.get("text"), str) or not c.get("text"):
                    errs.append(f"claims[{i}].text 須為非空字串")
                if not isinstance(c.get("ref"), str) or not c.get("ref"):
                    errs.append(f"claims[{i}].ref 須為非空字串(可溯源 #10)")
    elif kind == "hint":
        errs += _err_unknown(obj, _HINT_TOP, "hint 頂層")
        if obj.get("from_axis") not in AXES:
            errs.append(f"from_axis 須∈{AXES}")
        if not isinstance(obj.get("dedup_key"), str) or not obj.get("dedup_key"):
            errs.append("dedup_key 須為非空字串(跨軸唯一)")
        if not isinstance(obj.get("text"), str) or not obj.get("text"):
            errs.append("text 須為非空字串")
        if not isinstance(obj.get("provenance"), dict) or not obj.get("provenance"):
            errs.append("provenance 須為非空 object(#10 可溯源)")
    elif kind == "xnotify":
        errs += _err_unknown(obj, _XNOTIFY_TOP, "xnotify 頂層")
        if obj.get("from_axis") not in AXES:
            errs.append(f"from_axis 須∈{AXES}")
        if not isinstance(obj.get("note"), str):
            errs.append("note 須為字串(佈告零效力,僅記錄)")
    return errs


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    good_brief = {"schema": "brief/1", "source_axis": "tw", "as_of": "2026-07-27",
                  "claims": [{"claim_level": "ledger_fact",
                              "text": "arena 已結算 4128 列(settled_at 非空)",
                              "ref": "direction_arena_prediction"}]}
    chk("合法 brief 通過", validate(good_brief, "brief") == [])
    chk("措辭走私攔截(『可交易』)", any("黑名單" in e for e in validate(
        {**good_brief, "claims": [{"claim_level": "paper", "text": "本組合已可交易", "ref": "x"}]}, "brief")))
    chk("LAI 假兆詞攔截(『更準』)", blacklist_hits({"a": "模型答得更準了"}) == ["更準"])
    chk("數值陣列攔截(panel 走私)", any("數值陣列" in e for e in validate(
        {**good_brief, "as_of": [0.1, 0.2, 0.3]}, "brief")))
    chk("單一數字純量放行", not _has_numeric_array({"n": 42, "x": [{"y": 1.5}]}))
    chk("未知欄位 fail-closed", any("未知欄位" in e for e in validate(
        {**good_brief, "extra_field": 1}, "brief")))
    chk("claims>20 攔截", any("上限" in e for e in validate(
        {**good_brief, "claims": [good_brief["claims"][0]] * 21}, "brief")))
    chk("claim_level 封閉三值", any("claim_level" in e for e in validate(
        {**good_brief, "claims": [{"claim_level": "established", "text": "x", "ref": "r"}]}, "brief")))
    chk("ref 缺=拒(#10 可溯源)", any("ref" in e for e in validate(
        {**good_brief, "claims": [{"claim_level": "paper", "text": "x"}]}, "brief")))
    good_hint = {"schema": "hint/1", "from_axis": "raw", "dedup_key": "fc:a:b:raw",
                 "text": "欄位 a 與 b 中位相關 0.31(n=120 檔)", "provenance": {"corr": 0.31, "n_obs": 120}}
    chk("合法 hint 通過", validate(good_hint, "hint") == [])
    chk("hint 缺 provenance=拒", any("provenance" in e for e in validate(
        {k: v for k, v in good_hint.items() if k != "provenance"}, "hint")))
    chk("xnotify 合法通過", validate(
        {"schema": "xnotify/1", "from_axis": "lai", "note": "本輪零增益"}, "xnotify") == [])
    chk("schema 首欄錯=拒", any("schema" in e for e in validate(
        {**good_brief, "schema": "brief/2"}, "brief")))
    chk("iteration_uid 格式", valid_iteration_uid("tw-20260727-r01")
        and not valid_iteration_uid("tw-2026-r1") and not valid_iteration_uid("xx-20260727-r01"))
    chk("確定性:同輸入同輸出", validate(good_brief, "brief") == validate(good_brief, "brief"))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開入口(唯讀):")
    print(f"  SCHEMAS={SCHEMAS}  CLAIM_LEVELS={CLAIM_LEVELS}  MAX_CLAIMS={MAX_CLAIMS}")
    print(f"  BLACKLIST={BLACKLIST}")
    for fn in (validate, blacklist_hits, valid_iteration_uid):
        print(f"  {fn.__name__}  {fn.__doc__.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
