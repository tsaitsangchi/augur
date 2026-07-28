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
ABSTAIN_RE = re.compile(r"查無|無此|不存在|未收錄|沒有(這|該|此)|查不到|無相符|無法找到|未找到|找不到|"
                        r"不含|不包含|未包含|未出現|不在|"
                        r"not\s+found|no\s+such|does\s+not\s+exist|no\s+record", re.I)
# ↑「未找到/找不到」為 V2-RUBRIC-go 補入(hugo 2026-07-28):07-27 實證 pack 於 L3 至少 6 題
#   明文「未找到匹配的文獻標題《X》」且零編造,卻因詞表缺口被判 a=0——判準器誤殺誠實拒答。
#   補詞後四支對照臂 A 軸逐格零變動(floor 仍 0、ceiling 仍 1),只更準不更鬆(實測 2026-07-28)。
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


def fact_exact(answer, facts, source_text=None, exclude=None):
    """F 軸:expect.facts 每一條都須**逐字**出現(去空白、不分大小寫),全中才有機會得 1;
    **且不得加料**(V2-RUBRIC-go 2026-07-28):`source_text`(檢索片段原文)給定時,答案中出現
    「來源沒有的年份」即 0——照抄+捏造=捏造。07-27 實證:L1 原無此軸,「把片段抄對再附加
    『1987 年獲 Nobel 獎』」零成本滿分;pack 實際 8/30 之 L1 答案冒出題幹沒有的年份(2024/2026),
    F 仍全判 1=RAG 幻覺(有片段仍加料)這個 advisor 真實失效模式完全量不到。
    `exclude`(EVALSET-V2):干擾列之標記 token(如干擾年份)——答案含之即 0=**反 echo**
    (整段照抄檢索結果必含干擾 token;正確抽取只含目標列)。"""
    if not facts:
        return None
    a = _norm(answer)
    if not all(_norm(f) in a for f in facts if str(f).strip()):
        return 0
    if exclude and any(_norm(str(x)) in a for x in exclude if str(x).strip()):
        return 0                                       # 反 echo:含 exclude token(如干擾列年份)即 0
    if source_text:
        src_years = {m.group(0) for m in YEAR_RE.finditer(str(source_text))}
        for f in facts:
            src_years |= {m.group(0) for m in YEAR_RE.finditer(str(f))}
        if {m.group(0) for m in YEAR_RE.finditer(answer or "")} - src_years:
            return 0                                   # 加料年份=捏造(#1 零幻像)
    return 1


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


def judge(raw_answer, expect, source_text=None):
    """單題三軸裁決。回 {f,p,a,text};該層不適用之軸為 None(不得以 0 冒充、亦不得平均)。
    `source_text`=題幹原文;給定時 F 軸帶加料年份否決(fact_exact)。

    **孿生分派(EVALSET-V2)**:expect 帶 `truth` 時走真值分派——同一格內兩側**合記 F 軸**
    (exists/unique=事實抽取;absent=誠實缺席;分軸記會讓常數各吃半格):
      exists/unique → fact_exact(含 exclude 反 echo)∧**互斥否決**(答案含拒答詞即 0——
                       「echo+查無」組合策略否則通吃孿生,2026-07-28 dry-run 抽驗實錄)
      absent        → abstain_ok('absent') ∧ 不含 exclude(不在列中之真值,憑記憶說出=編造)
      ambiguous     → abstain_ok('ambig', candidates)(B3;記 A 軸)
      no_retrieval  → provenance_ok(need_sql)(B2;記 P 軸)
    無 `truth` 者走 v1 層別分派(向後相容;舊集判讀不變義)。"""
    truth = expect.get("truth")
    text = flatten_response(raw_answer)
    ssot = expect.get("ssot")
    f = p = a = None
    if truth:
        if truth in ("exists", "unique"):
            f = fact_exact(text, expect.get("facts"), source_text, expect.get("exclude"))
            if f == 1 and ABSTAIN_RE.search(text):
                f = 0                          # 互斥否決:一邊抽取一邊喊查無=兩面下注
            p = provenance_ok(text, ssot)
        elif truth == "absent":
            f = abstain_ok(text, "absent")     # 合記 F 軸(joint cell;見 docstring)
            if f == 1 and any(_norm(str(x)) in _norm(text)
                              for x in expect.get("exclude", []) if str(x).strip()):
                f = 0                          # 憑記憶說出不在列中之值=編造
        elif truth == "ambiguous":
            a = abstain_ok(text, "ambig", expect.get("candidates"))
        elif truth == "no_retrieval":
            p = provenance_ok(text, ssot, need_sql=True)
        else:
            raise ValueError(f"未知 truth:{truth}")
        return {"f": f, "p": p, "a": a, "text": text}
    layer = expect.get("layer")
    if layer not in LAYERS:
        raise ValueError(f"未知層別:{layer}")
    if layer == "L1_RETRIEVED":
        f = fact_exact(text, expect.get("facts"), source_text)
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


# 地板臂=**最強退化常數**(V2-RUBRIC-go 2026-07-28 換版;舊值留 git)。
# 07-27 對抗驗證:舊樣板五格全 0,但那不是「地板」——只是**剛好不含**「查無/多筆」二詞的弱字串;
# 四字常數「查無 多筆」即通吃 L3.A=1.000、L4.A=1.000。地板的正確問法不是「隨手一條常數拿幾分」,
# 而是「**最強的不看題目常數**拿幾分」——floor 在某格高分=該格對常數無鑑別力(誠實),
# 證據力判讀(evidence_protocol)要求 live 嚴格勝過它,格子空不空由此曝光,不再靠弱字串假裝有地板。
# 構造(全部退化利用、零內容知識):拒答詞+多筆詞(A 兩格)、兩個型別字(L1 column_catalog 子格
# 答案空間僅 VARCHAR/NUMERIC 二值)、單一表名+SELECT 模板(P 兩格之 knowledge_item 子格);
# **不含任何年份**(否則 A 軸自我否決)。
BOILERPLATE_ARM = (
    "查無此鍵;同名多筆請指明。欄位型別 VARCHAR 或 NUMERIC。"
    "請執行:SELECT * FROM knowledge_item WHERE title = ...;"
)


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
    # F 軸加料年份否決(V2-RUBRIC-go;07-27 實證 pack 8/30 照抄+加料仍滿分)
    SRC = "knowledge_item 查得列:authors=Steven E. Pav | year=2021"
    chk("F:照抄無加料=1(veto 不誤殺)",
        fact_exact("Steven E. Pav(2021)", ["Steven E. Pav", "2021"], source_text=SRC) == 1)
    chk("**F:事實全中但冒出來源沒有的年份=0**(照抄+捏造=捏造)",
        fact_exact("Steven E. Pav(2021),於 1987 年獲獎", ["Steven E. Pav", "2021"], source_text=SRC) == 0)
    chk("F:來源本就含該年份則不否決(如 venue 字串含年)",
        fact_exact("Pav 2021;另見 2019 版", ["Pav", "2021"],
                   source_text=SRC + " | note=2019 preprint") == 1)
    chk("F:無 source_text 時 veto 關閉(向後相容;舊呼叫不變義)",
        fact_exact("Steven E. Pav(2021),於 1987 年獲獎", ["Steven E. Pav", "2021"]) == 1)
    chk("judge 貫通 source_text 至 F 軸",
        judge("Steven E. Pav(2021),於 1987 年獲獎",
              {"layer": "L1_RETRIEVED", "facts": ["Steven E. Pav", "2021"], "ssot": "knowledge_item"},
              source_text=SRC)["f"] == 0)
    # ── 孿生分派(EVALSET-V2)──
    EX = {"truth": "exists", "facts": ["close", "VARCHAR"], "ssot": "column_catalog"}
    AB = {"truth": "absent", "exclude": ["0.03"], "ssot": "field_correlation"}
    chk("孿生 exists:正確抽取=F1", judge("「收盤價」=close,型別 VARCHAR(依 column_catalog)", EX)["f"] == 1)
    chk("**孿生互斥否決:抽對但同時喊查無=0**(echo+查無組合策略之機械鎖)",
        judge("close VARCHAR;另查無其他", EX)["f"] == 0)
    chk("孿生 exists:反 echo(exclude 命中=0)",
        judge("close VARCHAR NUMERIC", {**EX, "exclude": ["NUMERIC"]})["f"] == 0)
    chk("孿生 absent:誠實缺席=F1(合記 F 軸)", judge("檢索結果中不含該配對。", AB)["f"] == 1)
    chk("孿生 absent:「不在」亦命中(補詞)", judge("該欄不在檢索結果中。", AB)["f"] == 1)
    chk("**孿生 absent:憑記憶說出真值=0**(exclude 否決)",
        judge("查無;其中位數應為 0.03。", AB)["f"] == 0)
    chk("孿生 absent:拒答詞缺席=0(沉默/硬答皆不過)", judge("中位數是 0.5。", AB)["f"] == 0)
    chk("孿生 no_retrieval → P 軸(=v1 L2 語意)",
        judge("請執行 SELECT * FROM knowledge_item WHERE title='X';",
              {"truth": "no_retrieval", "ssot": "knowledge_item"})["p"] == 1)
    chk("孿生 ambiguous → A 軸", judge("有 Pav 與 Bailey 兩筆,請指明",
        {"truth": "ambiguous", "candidates": ["Pav", "Bailey"]})["a"] == 1)
    chk("未知 truth fail-loud", _raises(lambda: judge("x", {"truth": "maybe"}), ValueError))
    chk("無 truth 走 v1 層別分派(向後相容)",
        judge("查無此鍵。", {"layer": "L3_ABSENT", "ssot": "k"})["a"] == 1)
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
    chk("A absent:「未找到」亦是拒答(V2-RUBRIC-go 補詞;07-27 pack 6 題誠實拒答被誤殺)",
        abstain_ok("未找到匹配的文獻標題《X》。", "absent") == 1)
    chk("A absent:「找不到」亦是拒答", abstain_ok("資料庫中找不到此標題。", "absent") == 1)
    chk("A absent:「未找到」但報年份仍=0(補詞不鬆動編造否決)",
        abstain_ok("未找到,應為 2019 年之作。", "absent") == 0)
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
    # 地板臂=最強退化常數(V2-RUBRIC-go)。**注意語意反轉**:舊斷言「地板臂全滅」是空證——
    # 舊樣板四層拿 0 只因剛好不含「查無/多筆」二詞,證明的是「一條弱字串拿 0」,不是「地板=0」。
    # 新斷言鎖的是**刻意的退化剖面**:floor 在無鑑別力之格「就該高分」,那些格因此曝光;
    # live 臂之證據力=嚴格勝過此剖面(evidence_protocol),不再由假 0 地板白送。
    floors = [
        judge(BOILERPLATE_ARM, {"layer": "L1_RETRIEVED", "facts": ["Steven E. Pav", "2021"],
                                "ssot": "knowledge_item"})["f"],
        judge(BOILERPLATE_ARM, {"layer": "L2_NO_RETRIEVAL", "ssot": "knowledge_item"})["p"],
        judge(BOILERPLATE_ARM, {"layer": "L3_ABSENT", "ssot": "knowledge_item"})["a"],
        judge(BOILERPLATE_ARM, {"layer": "L4_AMBIG", "candidates": ["Pav", "Bailey"]})["a"],
    ]
    chk(f"**地板剖面鎖**:真事實題 F=0、退化可達之格=1 → {floors}(=[0,1,1,1])",
        floors == [0, 1, 1, 1])
    chk("地板不含年份(否則 A 軸自我否決=地板變弱)", not YEAR_RE.search(BOILERPLATE_ARM))
    chk("地板帶拒答詞+多筆詞(退化最大化之要件)",
        bool(ABSTAIN_RE.search(BOILERPLATE_ARM)) and bool(MULTI_RE.search(BOILERPLATE_ARM)))
    chk("地板只名一張 SSOT 表(散彈會自毀 P)",
        sum(t in BOILERPLATE_ARM for t in SSOT_TABLES) == 1)
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
