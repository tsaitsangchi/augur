"""六源公版辭書/註疏規則 parser — 逐字全文 → (詞條, 定義, locator, lex_type) 四元組(L3 定義層,計畫 T2)。

🎯 這支在做什麼(白話):knowledge_lexicon(L3)的解析核心——對六個公版來源
   (說文解字/康熙字典/Webster 1913/Roget 1911/王弼注/十三經注疏)各一個**確定性規則 parser**
   (純 regex 段切,零 ML、零 AI 生成),把 philosophy_work_text 的逐字全文切成詞條。
   定義文字一律為原文逐字片段(commentary=「經文句+注文」之連續原文段,不改寫不摘要);
   解析不了的候選塊**計數誠實回傳、寧缺勿硬湊**。
守 #1(逐字自公版來源、禁 AI 生成定義)· #15(失敗計數誠實)· 計畫〇-4(確定性規則,重跑可重現)。

介面(六個同型):parse_<source>(full_text) -> (entries, failed)
  entries = list[LexEntry(term_display, definition, locator, lex_type)]
  failed  = 解析失敗計數(有詞頭無定義、注文配不到經文、編號段抽不出主題詞等)

已知侷限(v1 誠實記,對齊計畫 T3「不追完美句界」精神):
  - commentary 注文以「行」為界(跨行長注只取注記行本身);同行多對經注僅首段經文可靠。
  - Webster 詞頭=行首全大寫行,Gutenberg 前言若殘留大寫行會成假詞條(定義空者入 failed)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.lexicon_parsers              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.lexicon_parsers --selftest   # 純紅綠自測（零 IO）
"""
import re
from typing import NamedTuple


class LexEntry(NamedTuple):
    term_display: str          # 詞條原貌(繁簡/大小寫不動;正規化交 textnorm 於寫入端)
    definition: str            # 逐字定義(原文子串;commentary=經文+注文連續段)
    locator: str | None        # 卷/部首/編號/段序(可為 None,寫入端可補 chapter 前綴)
    lex_type: str              # dictionary | thesaurus | commentary


# CJK 統一表意文字:BMP(ExtA+URO)+相容區+補充平面 ExtB-ExtH(說文/康熙非 BMP 字頭如 𧆑𠍮 實證需要)
_CJK = "㐀-鿿豈-龎\U00020000-\U0003FFFF"


# ── 說文解字(維基文庫 wikitext,計畫規則:「【字】…也」逐字條段切;locator=卷+部首) ──
_SW_JUAN = re.compile(r"^=*\s*(卷[一二三四五六七八九十百零上中下]+)\s*=*$")
_SW_RADICAL = re.compile(rf"^=+\s*([{_CJK}]{{1,3}}部)\s*=+$|^【?([{_CJK}]{{1,3}})部】?$")
_SW_SPLIT = re.compile(rf"(?=【[{_CJK}]{{1,4}}】)")
_SW_ENTRY_BRACKET = re.compile(rf"^【([{_CJK}]{{1,4}})】\s*(.*)$")
_SW_ENTRY_COLON = re.compile(rf"^([{_CJK}])[;；]?[：:]\s*(.+)$")   # 「元：始也。」;容 1 條源文 artifact「𦍧;：」


def parse_shuowen(full_text):
    """說文解字:【字】括號條目(主規則)+「字：定義」行首變體;locator=卷·部首(自標題行追蹤)。"""
    entries, failed = [], 0
    juan = radical = None
    cur_term, cur_def = None, []

    def flush():
        nonlocal cur_term, cur_def, failed
        if cur_term is not None:
            d = "\n".join(x for x in cur_def if x).strip()
            if d:
                loc = "·".join(x for x in (juan, radical) if x) or None
                entries.append(LexEntry(cur_term, d, loc, "dictionary"))
            else:
                failed += 1              # 有詞頭無定義=解析失敗,寧缺
        cur_term, cur_def = None, []

    for raw in full_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _SW_JUAN.match(line)
        if m:
            flush(); juan = m.group(1); continue
        m = _SW_RADICAL.match(line)
        if m:
            flush(); radical = m.group(1) or (m.group(2) + "部"); continue
        if "【" in line:
            for seg in _SW_SPLIT.split(line):
                seg = seg.strip()
                if not seg:
                    continue
                m = _SW_ENTRY_BRACKET.match(seg)
                if m:
                    flush()
                    cur_term, cur_def = m.group(1), [m.group(2).strip()]
                elif cur_term is not None:
                    cur_def.append(seg)
            continue
        m = _SW_ENTRY_COLON.match(line)
        if m:
            flush()
            cur_term, cur_def = m.group(1), [m.group(2).strip()]
            continue
        if cur_term is not None:         # 條目跨行接續
            cur_def.append(line)
        # 其餘散文(序/凡例)跳過,不計失敗
    flush()
    return entries, failed


# ── 康熙字典(維基文庫,格式實證 2026-07-03:「字：《唐韻》…」colon 式為主+「==字==」標題式) ──
_KX_HEADING = re.compile(rf"^==+\s*([{_CJK}])\s*==+$")           # ==字== 章節標題式字頭
_KX_ENTRY_COLON = re.compile(rf"^([{_CJK}])[：:]\s*(.*)$")       # 「字：定義」colon 式字頭(單 CJK 字)
_KX_NOTE = re.compile(r"^=*\s*(考證|備考|補遺)\s*=*[：:]?")       # 前條目附註段=接續非新字頭(實證 1,460 行)


def parse_kangxi(full_text):
    """康熙字典:「字：…」colon 式+「==字==」標題式雙規則(全 915 段實證);
    考證/備考/補遺 行=前條目附註接續;locator=段內序(chapter=部首·畫數由寫入端前綴)。"""
    entries, failed = [], 0
    idx = 0
    cur_term, cur_def = None, []

    def flush():
        nonlocal cur_term, cur_def, failed, idx
        if cur_term is not None:
            d = "\n".join(x for x in cur_def if x).strip()
            if d:
                idx += 1
                entries.append(LexEntry(cur_term, d, str(idx), "dictionary"))
            else:
                failed += 1              # 有字頭無定義=失敗,寧缺
        cur_term, cur_def = None, []

    orphan = False                       # 段首無字頭之接續行(硬切段殘尾)=1 次失敗誠實計
    for raw in full_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if _KX_NOTE.match(line):         # 附註段:原文逐字併入當前條目(去 == 標記)
            if cur_term is not None:
                cur_def.append(line.strip("=").strip())
            continue
        m = _KX_HEADING.match(line)
        if m:
            flush()
            cur_term, cur_def = m.group(1), []
            continue
        m = _KX_ENTRY_COLON.match(line)
        if m:
            flush()
            cur_term, cur_def = m.group(1), [m.group(2).strip()]
            continue
        if cur_term is not None:
            cur_def.append(line)
        elif not orphan:
            orphan = True
            failed += 1                  # 段首孤兒接續行(前段條目之殘尾)
    flush()
    return entries, failed


# ── Webster 1913(Gutenberg 純文字,計畫規則:行首全大寫 headword 塊切) ─────────
_GUT_START = re.compile(r"\*\*\* ?START OF TH[EI][^*]*\*\*\*")
_GUT_END = re.compile(r"\*\*\* ?END OF TH[EI][^*]*\*\*\*|\nEnd of (?:the )?Project Gutenberg")
_WB_HEAD = re.compile(r"^[A-Z][A-Z0-9\-'\.;, ]{0,70}$")


def _strip_gutenberg(text):
    """去 Gutenberg 頭尾樣板(marker 缺=no-op;確定性、不動正文)。"""
    s = _GUT_START.search(text)
    e = _GUT_END.search(text)
    return text[s.end() if s else 0: e.start() if e else len(text)]


def parse_webster1913(full_text):
    """Webster 1913:行首全大寫行=headword,至下一 headword 前=定義塊;locator=字母節·節內序。"""
    entries, failed = [], 0
    letter_counts = {}
    cur_term, cur_def = None, []

    def flush():
        nonlocal cur_term, cur_def, failed
        if cur_term is not None:
            d = "\n".join(cur_def).strip()
            if d:
                letter = next((c for c in cur_term if c.isalpha()), "?")
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
                entries.append(LexEntry(cur_term, d, f"{letter}·{letter_counts[letter]}", "dictionary"))
            else:
                failed += 1
        cur_term, cur_def = None, []

    for raw in _strip_gutenberg(full_text).splitlines():
        line = raw.rstrip()
        if _WB_HEAD.match(line.strip()):
            flush()
            cur_term, cur_def = line.strip(), []
            continue
        if cur_term is not None:
            cur_def.append(line)
    flush()
    return entries, failed


# ── Roget 1911(Gutenberg 純文字,計畫規則:編號段切) ────────────────────
_RG_HEAD = re.compile(r"^\s*#(\d+[a-z]?)\.\s*(.*)$")
# 段首註記:方括號/大括號群+殘餘閉括號與標點(巢狀如 [Nullibiety.[1]]、{opp. 100} 實證)
_RG_LEADING_NOTE = re.compile(r"^(?:\[[^\]]*\]|\{[^}]*\}|[\]\}.,;:\s]+)+")
_RG_TERM = re.compile(r"^([A-Za-z][A-Za-z' \-]{0,60}?)\s*(?:\.|--|—|,|\[|\||$)")
_RG_TAIL_TERM = re.compile(r"([A-Z][A-Za-z' \-]{0,40}?)\s*\.?\s*$")   # 未閉合註記之尾端主題詞(#454 Topic)


def parse_roget1911(full_text):
    """Roget 1911:`#編號.` 行起段、至下一編號段前;term=段首主題詞
    (前導註記剝除;字頭折行至次行時併次行再抽;皆敗時取尾端大寫詞);locator=#編號。"""
    entries, failed = [], 0
    cur_num, cur_head, cur_lines = None, None, []

    def flush():
        nonlocal cur_num, cur_head, cur_lines, failed
        if cur_num is not None:
            body = "\n".join(cur_lines).strip()
            head = _RG_LEADING_NOTE.sub("", (cur_head or "").strip())
            if "—" not in head:                          # 字頭折行(如 #288/#468):併次個含字母行再剝註
                nxt = next((l.strip() for l in cur_lines[1:] if re.search(r"[A-Za-z]", l)), "")
                head = _RG_LEADING_NOTE.sub("", (head + " " + nxt).strip())
            m = _RG_TERM.match(head) or _RG_TAIL_TERM.search(
                _RG_LEADING_NOTE.sub("", (cur_head or "").strip()))
            if m and body:
                entries.append(LexEntry(m.group(1).strip(), body, f"#{cur_num}", "thesaurus"))
            else:
                failed += 1              # 抽不出主題詞或空段=失敗,寧缺
        cur_num, cur_head, cur_lines = None, None, []

    for raw in _strip_gutenberg(full_text).splitlines():
        m = _RG_HEAD.match(raw)
        if m:
            flush()
            cur_num, cur_head = m.group(1), m.group(2).strip()
            cur_lines = [raw.strip()]    # 定義=整個編號段逐字(含編號行)
            continue
        if cur_num is not None:
            cur_lines.append(raw.rstrip())
    flush()
    return entries, failed


# ── 註疏共用(計畫規則:經文句→注文對;lex_type='commentary',term=經文句首字) ────
_CM_MARK = re.compile(r"(〔注〕|【注】|〔疏〕|【疏】|〔箋〕|【箋】|注曰|疏曰|箋云|注云|疏云|注：|疏：)")
_CM_HEADING = re.compile(
    rf"^(?:=+\s*)?(第?[一二三四五六七八九十百]+章|卷[一二三四五六七八九十百上中下]+"
    rf"|[{_CJK}]{{1,6}}第[一二三四五六七八九十百]+)(?:\s*=+)?$")


def _parse_commentary(full_text):
    """經文句(最近一段純文行)→ 注/疏文(注記標記後同行文字)配對;定義=經文+標記+注文之連續原文段。
    term=經文句首個 CJK 字(單字,與 concordance 中文單字契約對齊);locator=章名·段內序。"""
    entries, failed = [], 0
    heading, jing, idx = None, None, 0
    for raw in full_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _CM_HEADING.match(line)
        if m:
            heading, jing, idx = m.group(1), None, 0   # 換章:重置經文候選與段內序
            continue
        parts = _CM_MARK.split(line)
        if len(parts) == 1:
            jing = line                  # 純文行=最新經文候選(注/疏可連配同一經文)
            continue
        pre = parts[0].strip()
        if pre:
            jing = pre                   # 同行「經文【注】注文」:標記前段=經文
        for i in range(1, len(parts), 2):
            mark, body = parts[i], parts[i + 1].strip()
            term = next((ch for ch in (jing or "") if "㐀" <= ch <= "鿿"), None)
            if not jing or not body or not term:
                failed += 1              # 注文無經文可配/空注文=失敗,寧缺
                continue
            idx += 1
            loc = f"{heading}·{idx}" if heading else str(idx)
            entries.append(LexEntry(term, f"{jing}{mark}{body}", loc, "commentary"))
    return entries, failed


def parse_wangbi(full_text):
    """王弼注(老子道德真經注):經文句→王弼注文對。"""
    return _parse_commentary(full_text)


def parse_shisanjing(full_text):
    """十三經注疏:經文句→注/疏/箋文對(注與疏各自成條、配同一經文句)。"""
    return _parse_commentary(full_text)


def _selftest():
    """純紅綠(合成輸入→斷言;零 IO):六 parser 核心不變式+誠實計失敗+四元組契約固化。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # 說文:【字】括號條目 → dictionary 四元組
    e, f = parse_shuowen("【元】始也。")
    chk("shuowen 【元】→1 條", len(e) == 1 and e[0].term_display == "元"
        and e[0].definition == "始也。" and e[0].lex_type == "dictionary")
    # 說文:有詞頭無定義=誠實計失敗、寧缺(#15)
    e, f = parse_shuowen("【天】\n【地】坤也。")
    chk("shuowen 空定義入 failed", len(e) == 1 and f == 1)
    # 說文:卷·部首標題 → locator 前綴
    e, f = parse_shuowen("卷一\n一部\n【元】始也。")
    chk("shuowen locator=卷·部首", len(e) == 1 and e[0].locator == "卷一·一部")
    # 康熙:「字：定義」colon 式(單 CJK 字頭)
    e, f = parse_kangxi("元：《唐韻》始也。")
    chk("kangxi colon 式", len(e) == 1 and e[0].term_display == "元"
        and e[0].lex_type == "dictionary" and e[0].locator == "1")
    # Webster:行首全大寫=headword、至下一 headword=定義塊
    e, f = parse_webster1913("ABACUS\nA counting frame.\nABANDON\nTo give up.")
    chk("webster 2 headword", len(e) == 2 and e[0].term_display == "ABACUS"
        and e[0].locator == "A·1" and e[1].term_display == "ABANDON")
    # Roget:#編號段 → thesaurus、locator=#編號
    e, f = parse_roget1911("#1. Existence.\nBeing, existence.")
    chk("roget 編號段", len(e) == 1 and e[0].term_display == "Existence"
        and e[0].lex_type == "thesaurus" and e[0].locator == "#1")
    # 註疏:經文→注文對、term=經文句首 CJK、lex_type=commentary
    e, f = parse_wangbi("道可道〔注〕常道也。")
    chk("commentary 經注配對", len(e) == 1 and e[0].term_display == "道"
        and e[0].lex_type == "commentary" and "〔注〕" in e[0].definition)
    # 註疏:注文無經文可配=誠實計失敗(#15)
    e, f = parse_wangbi("〔注〕孤注也。")
    chk("commentary 無經文入 failed", len(e) == 0 and f == 1)
    # LexEntry 四元組契約(寫入端依賴此欄序)
    chk("LexEntry 欄位", LexEntry._fields == ("term_display", "definition", "locator", "lex_type"))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.lexicon_parsers --selftest;免 DB 免 API)")
