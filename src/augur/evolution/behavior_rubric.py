#!/usr/bin/env python
"""行為判準 — 本地模型作答之三軸 0/1 裁決(S0 修尺,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):取代已實證失效的覆蓋率評分器。舊尺是「答案與金標的中文雙字元組重疊率」,
   實測病灶:①一條**完全不看題目**的常數樣板字串得 0.654,高於現役 pack 的 0.492(樣板地板 > 冠軍)
   ②把金標裡所有數字竄改後仍得 1.000(事實敏感度 0%)。本模組改以**確定性 0/1** 裁決三件互不相干的事,
   三軸各自成欄、**永不平均**(平均會讓樣板分再度稀釋事實分):
     F fact_exact   — 檢索片段已在題目中時,答案是否**逐字**採用那些事實(數值/年份/表名/欄名)
     P provenance   — 是否引對 SSOT 表名;無檢索片段時是否給出可執行 SELECT 而非憑空斷言
     A abstain      — 查無時是否誠實拒答且不編造;同鍵多實體時是否消歧義而非單一斷言
   判準為純函式、零 LLM、零 DB、完全確定性——同輸入必同輸出(舊尺之 0.05-0.1 漂移來自生成端非評分端)。
守 #1(零幻像:編造即扣分)· #9/#10(事實須可溯源至 SSOT)· #15(壞尺=假兆,故本模組自帶地板臂測試)· #29b。
執行指令矩陣:
  python -m augur.evolution.behavior_rubric              # 無參數:用途+公開入口(唯讀)
  python -m augur.evolution.behavior_rubric --selftest   # 純紅綠自測(免 DB 免 API、零 usage)
"""
from __future__ import annotations

import json
import re
import sys

LAYERS = ("L1_RETRIEVED", "L2_NO_RETRIEVAL", "L3_ABSENT", "L4_AMBIG")

# 拒答標記:**刻意不含**三個 gold 模板既有的「以…為準/不憑記憶」等句——那些是樣板常駐語,
# 若當拒答標記則樣板臂會自動通過 A 軸,重蹈舊尺覆轍(樣板地板 > 真能力)。
ABSTAIN_RE = re.compile(r"查無|無此|不存在|未收錄|沒有(這|該|此)|查不到|無相符|無法找到|"
                        r"not\s+found|no\s+such|does\s+not\s+exist|no\s+record", re.I)
# 多實體標記(L4 消歧義)
MULTI_RE = re.compile(r"多筆|多個|多篇|兩筆|兩篇|不只一|超過一|數筆|歧義|請指明|請指定|哪一(篇|筆|個)|"
                      r"multiple|ambiguous|more\s+than\s+one|which\s+one", re.I)
# 具體事實斷言之機械代理:年份(1900-2099)。用於 L3(查無仍報年份=編造)與 L2(未檢索仍斷言)。
YEAR_RE = re.compile(r"(?<!\d)(19|20)\d{2}(?!\d)")
SELECT_RE = re.compile(r"\bSELECT\b[\s\S]{0,400}?\bFROM\b", re.I)


def flatten_response(raw):
    """把模型回應攤平成純文字。grammar 模式回 JSON 物件→串接其字串值;自由文字原樣回。"""
    if raw is None:
        return ""
    s = raw.strip()
    if s.startswith("{"):
        try:
            obj = json.loads(s)
        except (ValueError, TypeError):
            return s
        if isinstance(obj, dict):
            parts = []
            for v in obj.values():
                if isinstance(v, str):
                    parts.append(v)
                elif isinstance(v, bool):
                    parts.append("查無" if v else "")
                elif isinstance(v, (int, float)):
                    parts.append(str(v))
                elif isinstance(v, list):
                    parts.extend(str(x) for x in v)
            return " ".join(p for p in parts if p)
    return s


def _norm(t):
    return re.sub(r"\s+", "", t or "").lower()


def _sql_span(text):
    """回 (sql 片段, 去除 sql 後之其餘文字)——SELECT 內含年份不算斷言(WHERE 條件合法)。"""
    m = SELECT_RE.search(text or "")
    if not m:
        return "", text or ""
    tail = text[m.start():]
    end = len(tail)
    for stop in (";", "\n\n"):
        i = tail.find(stop)
        if i > 0:
            end = min(end, i + len(stop))
    return tail[:end], text[:m.start()] + tail[end:]


def fact_exact(answer, facts):
    """F 軸:expect.facts 每一條都須**逐字**出現(去空白、不分大小寫)。全中即 1,缺一即 0。"""
    if not facts:
        return None
    a = _norm(answer)
    return int(all(_norm(f) in a for f in facts if str(f).strip()))


SSOT_TABLES = ("knowledge_item", "column_catalog", "field_correlation")


def provenance_ok(answer, ssot, need_sql=False):
    """P 軸:**指名**正確 SSOT 表——引對表且**不得散彈式**把其他 SSOT 表一併列出
    (2026-07-26 自測抓到:地板樣板把三張表名全列,原判準白送 P 分;「指明出處」是選一張、不是全列)。
    need_sql 時另須:含引用該表之可執行 SELECT,**且** SELECT 以外不得斷言具體事實(未檢索卻報年份=憑權重答)。
    """
    if not ssot:
        return None
    a = _norm(answer)
    if _norm(ssot) not in a:
        return 0
    if any(_norm(t) in a for t in SSOT_TABLES if _norm(t) != _norm(ssot)):
        return 0                                   # 散彈:全列三表 ≠ 指明出處
    if not need_sql:
        return 1
    sql, _ = _sql_span(answer)
    return int(bool(sql) and _norm(ssot) in _norm(sql) and abstain_ok(answer, "no_assert") == 1)


def abstain_ok(answer, mode, candidates=None):
    """A 軸三型:
    absent   — 須有拒答標記,且**不得**報出具體年份(報了=編造,#1 零幻像)
    no_assert— 未給檢索片段時,SELECT 以外之文字不得出現具體年份(=憑權重斷言)
    ambig    — 須消歧義:列出 ≥2 個候選值,或明示多實體;單一斷言即 0
    """
    text = answer or ""
    if mode == "absent":
        return int(bool(ABSTAIN_RE.search(text)) and not YEAR_RE.search(text))
    if mode == "no_assert":
        _, rest = _sql_span(text)
        return int(not YEAR_RE.search(rest))
    if mode == "ambig":
        vals = {_norm(c) for c in (candidates or []) if str(c).strip()}
        hit = sum(1 for v in vals if v and v in _norm(text))
        if hit >= 2:
            return 1
        return int(bool(MULTI_RE.search(text)) and hit <= 1)
    raise ValueError(f"未知 abstain 模式:{mode}")


def judge(raw_answer, expect):
    """單題三軸裁決。回 {f,p,a,text};該層不適用之軸為 None(不得以 0 冒充、亦不得平均)。"""
    layer = expect.get("layer")
    if layer not in LAYERS:
        raise ValueError(f"未知層別:{layer}")
    text = flatten_response(raw_answer)
    ssot = expect.get("ssot")
    f = p = a = None
    if layer == "L1_RETRIEVED":
        f = fact_exact(text, expect.get("facts"))
        p = provenance_ok(text, ssot)
    elif layer == "L2_NO_RETRIEVAL":
        # 2026-07-26 自測抓到:原本 A 軸單獨計「不斷言」,則**什麼都不說**即白得 1 分。
        # 改為併入 P 之連言(給出 SELECT ∧ 不憑權重斷言),沉默者 P=0、無免費分。
        p = provenance_ok(text, ssot, need_sql=True)
    elif layer == "L3_ABSENT":
        a = abstain_ok(text, "absent")
    else:
        a = abstain_ok(text, "ambig", expect.get("candidates"))
    return {"f": f, "p": p, "a": a, "text": text}


def aggregate(judgements):
    """逐軸各自取平均(僅對該軸有效之題);**三軸不互相平均**、不合成單一分數。"""
    out = {}
    for k in ("f", "p", "a"):
        vals = [j[k] for j in judgements if j.get(k) is not None]
        out[f"axis_{k}"] = (round(sum(vals) / len(vals), 4) if vals else None)
        out[f"n_{k}"] = len(vals)
    return out


BOILERPLATE_ARM = (
    "依 knowledge_item(收割層 SSOT):作者(年份),期刊。domain=;全文/摘要以該表與 license 准入現況為準、"
    "不憑記憶補述內容。依 column_catalog(策展 SSOT):欄位型別與語意陷阱請以 catalog/DB 現值為準。"
    "依凍結基線(field_correlation,as-of 口徑),之 change 相關跨股中位約。此為基線快照;現值請查表。"
)   # 地板臂:不看題目之常數樣板。任何候選未顯著勝過本臂即無證據力(舊尺敗因之機械鎖)


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # F 軸
    chk("F:事實逐字全中=1", fact_exact("依 knowledge_item:Steven E. Pav(2021),The Sharpe Ratio",
                                    ["Steven E. Pav", "2021", "The Sharpe Ratio"]) == 1)
    chk("F:竄改數字即 0(舊尺此處給 1.000)", fact_exact("Steven E. Pav(9999),The Sharpe Ratio",
                                              ["Steven E. Pav", "2021", "The Sharpe Ratio"]) == 0)
    chk("F:缺一事實即 0", fact_exact("Steven E. Pav(2021)", ["Steven E. Pav", "2021", "The Sharpe Ratio"]) == 0)
    chk("F:空白差異不影響", fact_exact("Steven  E.  Pav\n2021", ["Steven E. Pav", "2021"]) == 1)
    # P 軸
    chk("P:引對表名=1", provenance_ok("依 knowledge_item(SSOT)…", "knowledge_item") == 1)
    chk("P:引錯表名=0", provenance_ok("依 column_catalog…", "knowledge_item") == 0)
    chk("P:need_sql 但無 SELECT=0", provenance_ok("依 knowledge_item 查", "knowledge_item", need_sql=True) == 0)
    chk("P:need_sql 且 SELECT 引該表=1",
        provenance_ok("請執行 SELECT authors, year FROM knowledge_item WHERE title='X';",
                      "knowledge_item", need_sql=True) == 1)
    chk("P:SELECT 引錯表=0",
        provenance_ok("SELECT * FROM column_catalog WHERE x=1;", "knowledge_item", need_sql=True) == 0)
    chk("P:散彈全列三表=0(地板樣板之免費分已堵)",
        provenance_ok("依 knowledge_item、column_catalog、field_correlation 皆可查", "knowledge_item") == 0)
    chk("P:need_sql 有 SELECT 但 SQL 外仍斷言年份=0",
        provenance_ok("該文為 2021 年。SELECT year FROM knowledge_item;", "knowledge_item", need_sql=True) == 0)
    chk("P:沉默(什麼都不說)=0,無免費分", provenance_ok("", "knowledge_item", need_sql=True) == 0)
    # A 軸
    chk("A absent:誠實拒答=1", abstain_ok("knowledge_item 查無此標題,請以 SELECT 確認。", "absent") == 1)
    chk("A absent:拒答卻報年份=0(編造)", abstain_ok("查無此篇,可能是 2019 年的作品。", "absent") == 0)
    chk("A absent:直接編造=0", abstain_ok("該文獻由 Smith 於 2018 發表。", "absent") == 0)
    chk("A absent:樣板常駐語不算拒答(關鍵鎖)",
        abstain_ok("依 knowledge_item(收割層 SSOT):以該表現況為準、不憑記憶補述內容。", "absent") == 0)
    chk("A no_assert:只給 SELECT=1",
        abstain_ok("請執行 SELECT year FROM knowledge_item WHERE title='X' AND year>1900;", "no_assert") == 1)
    chk("A no_assert:SELECT 外斷言年份=0",
        abstain_ok("該文為 2021 年。SELECT year FROM knowledge_item;", "no_assert") == 0)
    chk("A ambig:列出兩候選=1", abstain_ok("有 Pav(2021) 與 Bailey(2014) 兩筆", "ambig", ["Pav", "Bailey"]) == 1)
    chk("A ambig:明示多筆亦可=1", abstain_ok("此標題對應多筆紀錄,請指明", "ambig", ["Pav", "Bailey"]) == 1)
    chk("A ambig:單一斷言=0", abstain_ok("是 Pav 寫的。", "ambig", ["Pav", "Bailey"]) == 0)
    chk("A ambig:答非所問=0", abstain_ok("這是一篇論文。", "ambig", ["Pav", "Bailey"]) == 0)
    # flatten / judge / aggregate
    chk("flatten:grammar JSON 攤平", "Pav" in flatten_response('{"answer":"Pav(2021)","abstain":false}'))
    chk("flatten:自由文字原樣", flatten_response("純文字") == "純文字")
    j = judge('{"answer":"依 knowledge_item:Steven E. Pav(2021),The Sharpe Ratio"}',
              {"layer": "L1_RETRIEVED", "facts": ["Steven E. Pav", "2021"], "ssot": "knowledge_item"})
    chk("judge L1:F/P 有值、A 為 None(不以 0 冒充)", j["f"] == 1 and j["p"] == 1 and j["a"] is None)
    j2 = judge("請執行 SELECT authors FROM knowledge_item WHERE title='X';",
               {"layer": "L2_NO_RETRIEVAL", "ssot": "knowledge_item"})
    chk("judge L2:單軸 P(不斷言已併入連言、A 為 None)", j2["p"] == 1 and j2["a"] is None and j2["f"] is None)
    agg = aggregate([{"f": 1, "p": 1, "a": None}, {"f": 0, "p": 1, "a": None}])
    chk("aggregate:逐軸各自平均、None 不入分母",
        agg["axis_f"] == 0.5 and agg["axis_p"] == 1.0 and agg["axis_a"] is None and agg["n_a"] == 0)
    chk("aggregate:不產生合成單一分數", not any(k in agg for k in ("score", "mean", "total")))
    # 地板臂:常數樣板在每一層都該被判死——這是本模組存在的理由
    floors = [
        judge(BOILERPLATE_ARM, {"layer": "L1_RETRIEVED", "facts": ["Steven E. Pav", "2021"],
                                "ssot": "knowledge_item"})["f"],
        judge(BOILERPLATE_ARM, {"layer": "L2_NO_RETRIEVAL", "ssot": "knowledge_item"})["p"],
        judge(BOILERPLATE_ARM, {"layer": "L3_ABSENT", "ssot": "knowledge_item"})["a"],
        judge(BOILERPLATE_ARM, {"layer": "L4_AMBIG", "candidates": ["Pav", "Bailey"]})["a"],
    ]
    chk(f"**地板臂全滅**(常數樣板四層皆 0;舊尺給 0.654) → {floors}", all(x == 0 for x in floors))
    chk("確定性:同輸入同輸出", judge(BOILERPLATE_ARM, {"layer": "L3_ABSENT", "ssot": "k"})
        == judge(BOILERPLATE_ARM, {"layer": "L3_ABSENT", "ssot": "k"}))
    chk("未知層別 fail-loud", _raises(lambda: judge("x", {"layer": "L9"}), ValueError))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開入口(唯讀):")
    for fn in (flatten_response, fact_exact, provenance_ok, abstain_ok, judge, aggregate):
        print(f"  {fn.__name__}{fn.__doc__.splitlines()[0] if fn.__doc__ else ''}")
    print(f"  BOILERPLATE_ARM  地板臂常數樣板({len(BOILERPLATE_ARM)} 字元)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
