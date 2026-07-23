"""從 META-CONSTITUTION.md 枚舉 102 條條款宇宙（97 [N]＋5 [I] WHY；供 WM.44 形式充分性覆蓋檢查）＋抽取原文標籤。

依 `AUGUR-MC v1.3 §0.3` 條款編號系統：PA｜P{n}.D / P{n}.W{m} / P{n}.Y / P{n}.E{m}｜EV.1–EV.12｜F1–F6｜
**§2.{n}（Definitions）**；另「章節號（§0–§9 及其小節與項次，如 §8.3、§2.11）視同條款編號」。

**B3 修正（條款宇宙不完整）**：前版 `_SECTION_SUB` 僅匹配 heading（`^#{2,4} §?n.m`），而 §2 之十一條
定義與 §5 之六個架構角色皆為 **numbered list item** 體例（`1. **Reality** ＝ …`），故 §2.1–§2.11 與
§5.1–§5.6 **從未進入條款宇宙**——其中 §2.5 Evidence／§2.6 Knowledge／§2.7 Intelligence／§2.10
Confidence 為全憲章最核心之定義。後果：WM.44 所報「均見於聲明文本」為假陽性。本版補 list-item 枚舉。

**「項次」之範圍**：§0.3 所舉之例（§8.3、§2.11）中，§2.11 即 numbered list item——故 numbered list
item 為 §0.3 明文承認之項次體例，§2/§5 同體例者一併納入，無須解釋即可認定。至於**字母項**
（§0.6(a)、§8.5(b)(i)）是否亦屬「項次」，§0.3 未舉例、體例亦異（括號字母 vs 點號數字），其認定
屬條文解釋（§8.1 Steward 專屬）——linter 不得自行造法，故**明示不納入**並於 README 據實揭露，
而非靜默省略。

執行指令矩陣：
  python -m tools.constitution_lint.mc_clauses              # 印用途（唯讀、免外部依賴）
  python -m tools.constitution_lint.mc_clauses --selftest    # 對真實 META-CONSTITUTION.md 枚舉條款紅綠自測（唯讀）
"""
from __future__ import annotations

import re
import unicodedata

_CLAUSE_PATTERNS = [
    (re.compile(r"\bPA\b"), lambda m: "PA"),
    (re.compile(r"\bP([1-5])\.E(\d+)\b"), lambda m: f"P{m.group(1)}.E{m.group(2)}"),
    (re.compile(r"\bP([1-5])\.W(\d+)\b"), lambda m: f"P{m.group(1)}.W{m.group(2)}"),
    (re.compile(r"\bP([1-5])\.D\b"), lambda m: f"P{m.group(1)}.D"),
    (re.compile(r"\bP([1-5])\.Y\b"), lambda m: f"P{m.group(1)}.Y"),
    (re.compile(r"\bEV\.(\d+)\b"), lambda m: f"EV.{m.group(1)}"),
    (re.compile(r"\bF([1-6])\b(?!\.)"), lambda m: f"F{m.group(1)}"),
]

# [N] 章標題：`## §8 … [N]`（章級，粗顆粒）。
_SECTION_CH = re.compile(r"^#{2,4}\s+§\s?(\d+)\b[^\n]*\[N\]", re.M)
# 子條標題：`### 8.3 合規聲明…`／`### 0.6 Hierarchy Rule`（§ 與 [N] 在父章、子標題無之）→ §8.3 等母條款不再隱形（SHOULD #9）。
_SECTION_SUB = re.compile(r"^#{2,4}\s+§?\s?(\d+\.\d+)\b", re.M)
# 任一 h2 標題（用以終止「現行 [N] 章」之作用域：Appendix C/D/E 之編號清單不得誤入宇宙）
_ANY_H2 = re.compile(r"^##\s+")
# [N] 章下之 numbered list item（§0.3 之「項次」體例，例：`1. **Reality** ＝ …`、
# `4. **World Understanding Engine（Cognitive Kernel）**：…`）。**必須**具粗體術語才算條款項次
# ——純敘述性編號段落（如 Appendix C 各點）不具此形式，且已由 [N] 章作用域排除。
_LIST_ITEM = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*")


def _list_item_anchors(mc_text: str):
    """回 [(line_idx, code, raw_name)]：全部 [N] 章之 numbered list item 項次（§n.m）。

    作用域規則：`## §n …[N]` 起算，遇任一其他 h2（含 `## Appendix …[I]`、`## §9 …[I]`）即失效。
    項次序號取 list 之字面編號（§2 之 11 項恰為 §2.1–§2.11，與憲章自身之引用一致）。
    """
    out, cur = [], None
    for i, ln in enumerate(mc_text.splitlines()):
        if _ANY_H2.match(ln):
            m = _SECTION_CH.match(ln)
            cur = m.group(1) if m else None
            continue
        if cur is None:
            continue
        m = _LIST_ITEM.match(ln)
        if m:
            out.append((i, f"§{cur}.{int(m.group(1))}", _clean_label(m.group(2))))
    return out


def enumerate_clauses(mc_text: str) -> set:
    """回 MC [N] 條款代號集合：PA/P#.*/EV.#/F#、[N] 章（§n）、子條標題（§n.m）與**項次**（§n.m）。"""
    clauses = set()
    for pat, fmt in _CLAUSE_PATTERNS:
        for m in pat.finditer(mc_text):
            clauses.add(fmt(m))
    for m in _SECTION_CH.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    for m in _SECTION_SUB.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    for _, code, _ in _list_item_anchors(mc_text):
        clauses.add(code)
    return clauses


# ──────────────────────────────────────────────────────────────────────────────
# 憲章原文標籤資料（WM.44-LABEL 用）
#
# 病灶：起草者憑記憶「轉述」上層條款標籤，再拿自己的轉述去推論，致真實義務被判「不觸及」而
# 靜默落空（linter 綠燈但實質錯誤）。本區塊自憲章原文抽出每條 [N] 條款之**自有標籤**與**正文**，
# 使「規格所載標籤 vs 憲章原文」成為機器可判之比對，而非人類記憶之比對。
# ──────────────────────────────────────────────────────────────────────────────

# 憲章條款代號之字面。§ 前綴於正規化時剝除（`§P5.D` ≡ `P5.D`）。
CODE_ALT = r"(?:PA|P[1-5]\.(?:D|Y|W\d+|E\d+)|EV\.\d+|F[1-6]|§\d+(?:\.\d+)?)"

# **上層規格**條款代號之字面（B5：過半矩陣零檢查之修正）。前版 `_CODE_LABEL` 僅以 CODE_ALT
# 為錨，故 Annex TR.D/E/F/G 之 WM./ONT./ID./KS./L5./L6. 等標籤**完全不檢**——所報「已比對 71 筆」
# 全為 MC 側。`AUGUR-XX` 之 XX 恰為該規格之條款代號前綴，故此表同時充作 upper-specs 解析之依據。
# 長前綴在前：`IDO`/`KDI`/`KDO`/`DI`/`DO` 不得被較短前綴誤切；`A`/`T`＝WM Annex A／ONT Annex T。
SPEC_PREFIXES = [
    "WM", "ONT", "IDO", "KDI", "KDO", "DI", "DO", "EO", "ID", "KS", "LDO",
    "L5", "L6", "L7", "A", "T",
]
SPEC_CODE_ALT = r"(?:" + "|".join(SPEC_PREFIXES) + r")\.\d+"
# 任一條款代號（憲章側 ∪ 規格側）。規格側置前：`ID.1` 不得被 `§\d+` 等分支搶走。
ANY_CODE_ALT = (r"(?:" + SPEC_CODE_ALT +
                r"|PA|P[1-5]\.(?:D|Y|W\d+|E\d+)|EV\.\d+|F[1-6]|§\d+(?:\.\d+)?)")

# 條款自身之結構性標籤（非「名稱」）：`**P1.W1 WHAT [N]**` 之 WHAT 不是 P1.W1 的名字，
# 而是「這是 WHAT 段」之體例標記。以其為權威標籤將令全部 W/D 條款無從具名 → 排除。
_GENERIC_LABELS = {"definition", "what", "why", "enforce", "d", "w", "e", "y"}
# 標籤尾綴之體例標記（`**P5.E2（風險分級 DEFER）**` 之 DEFER 標的是掛鉤性質，非名稱的一部分）。
_TRAILING_MARKERS = ("defer", "deferred", "[n]", "[i]")

# 章節標題：`## §3 Five Immutable Principles（五大不可違反原則）[N]`、`### 8.3 合規聲明義務與…`
_H_SECTION = re.compile(r"^#{2,4}\s+§?\s?(\d+(?:\.\d+)?)\s+(.+?)\s*$")
# 反模式標題：`### F4 — Knowledge Without Identity`
_H_FORBIDDEN = re.compile(r"^#{2,4}\s+(F[1-6])\s*[—–-]+\s*(.+?)\s*$")
# 原則標題（非條款，供 P{n}.* 之祖先脈絡）：`### Principle 1 — Reality First（真實世界優先）`
_H_PRINCIPLE = re.compile(r"^#{2,4}\s+Principle\s+([1-5])\s*[—–-]+\s*(.+?)\s*$")
# 條款粗體錨：`**P1.D Definition [N]**`、`* **P1.E1（開放來源）**：`、`* **P4.E2 Time（雙時間性）**`
_B_CLAUSE = re.compile(r"^\s*(?:[*-]\s+)?\*\*(P[1-5]\.(?:D|Y|W\d+|E\d+))\s*(.*?)\*\*")
# 標準鏈節點（§4 圍籬圖內）：`EV.9  Human Authority Gate (P5)`、`EV.2  Observation   ║`
_EV_NODE = re.compile(r"^EV\.(\d+)\s+([A-Za-z].*)$")
# 圍籬 ASCII 圖之框線字元（EV 節點名須切在此之前）
_BOX_CHARS = re.compile(r"[│┐┤┌└┘├─◄▼║═╗╝╚╔╪╬|]")


# 效力標注：憲章側 `[N]`／`[I]`；上層規格側 `[N｜refines｜`AUGUR-MC v1.3 §P4.E6`；…]`
# （規格條款錨之效力標注載有掛鉤來源，非標籤之一部分，須整塊剝除）。
_EFFECT_TAG = re.compile(r"\[[NI](?:｜[^\]]*)?\]")


def _clean_label(raw: str) -> str:
    """去效力標注／收尾標點／markdown 強調符號，回條款自有標籤之原字串（未正規化）。

    標籤緊接代號者體例上整段括起（`* **P1.E1（開放來源）**：`）——此時脫去最外層括號，
    俾錯誤訊息所印之「憲章原文」與規格側標籤同形可比。
    """
    s = _EFFECT_TAG.sub("", raw)
    s = s.replace("**", "").replace("`", "")
    s = _BOX_CHARS.split(s)[0]
    s = s.strip().strip("：:—–- ").strip()
    inside, outside = _split_paren(s)
    if len(inside) == 1 and not outside:
        # 剝外層括號須於**原字串**為之：`_split_paren` 先 NFKC，其 inside 已把全形標點
        # 半形化——前版逕取 inside[0]，致 `paren_name` 半形、錯誤訊息所印「原文」非逐字，
        # 採信訊息之執行者遂寫入半形標籤（2026-07-18 對抗全查實證 18 筆）。比對不受影響
        # （full_forms／halves／比對一律另過 normalize_label），本修僅使訊息回歸逐字。
        t = s.strip()
        if len(t) >= 2 and t[0] in "（(" and t[-1] in "）)":
            s = t[1:-1].strip()
        else:
            s = inside[0].strip()
    return s


def normalize_label(s: str) -> str:
    """比對用正規化：NFKC（全半形統一）→ 去 markdown 強調／反引號／效力標注 → 去全部空白 → 小寫。"""
    s = unicodedata.normalize("NFKC", s or "")
    s = _EFFECT_TAG.sub("", s)
    s = s.replace("*", "").replace("`", "").replace("　", "")
    s = re.sub(r"\s+", "", s)
    return s.lower()


def _split_paren(raw: str):
    """回 (括號內片段清單, 括號外片段清單)。NFKC 後括號一律為半形 ()。"""
    s = unicodedata.normalize("NFKC", raw)
    inside, outside, depth, buf_in, buf_out = [], [], 0, "", ""
    for ch in s:
        if ch == "(":
            if depth == 0:
                outside.append(buf_out)
                buf_out = ""
            else:
                buf_in += ch
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
            if depth == 0:
                inside.append(buf_in)
                buf_in = ""
            else:
                buf_in += ch
        elif depth > 0:
            buf_in += ch
        else:
            buf_out += ch
    outside.append(buf_out)
    return [x for x in inside if x.strip()], [x for x in outside if x.strip()]


def _strip_trailing_markers(seg: str) -> str:
    """去尾綴體例標記（`風險分級 DEFER` → `風險分級`）。標記非名稱本體。"""
    words = _clean_label(seg).split()
    while words and words[-1].strip("[]").lower() in _TRAILING_MARKERS:
        words.pop()
    return " ".join(words)


def _label_forms(raw: str):
    """由條款自有標籤原字串展開 (full_forms, halves)。

    **B2 修正（子字串放行漏洞）**：前版 `_name_variants` 把裸英文名（Confidence／Time／
    NoLaundering）與完整標籤**並列為對等變體**，判定又採「任一變體為標籤之子字串即放行」——
    於是「Confidence 單一形式化」僅因含 `Confidence` 即綠燈，而 P4.E8 原文括號名為
    「Confidence（語義與消費）」，**被截除之「消費」面才是 L7 之義務**。截半標籤靜默落空
    半個義務，正是本檢查所要撲滅之病灶，卻由本檢查親手放行。

    故將變體分作兩級：

    * **full_forms（完整表記，單獨匹配即充分）**：標籤整體、去尾綴體例標記者、頂層並列表記
      （`A／B` 之各支）。
    * **halves（`X（Y）` 體例之兩半，單獨匹配為必要非充分）**：憲章／規格體例中 `X（Y）` 之
      X 與 Y——**機器無從分辨** `Five Immutable Principles（五大不可違反原則）` 之譯名對
      與 `Confidence（語義與消費）` 之名＋限定語。故一律降級：擇一引用僅於「標籤即該半名
      本身、未添附自撰片段」時放行（§8.2 較嚴格解讀）。
    """
    base = _clean_label(raw)
    if not base:
        return [], []

    full, seen = [], set()

    def push(v):
        v = _clean_label(v)
        # 表記須具辨識度：< 3 字元者（如 `EV.9  Human Authority Gate (P5)` 之 `P5`）不足以
        # 作為「引用了原文」之證據，反易造成偽陰性 → 捨棄。
        n = normalize_label(v)
        if len(n) < 3 or n in seen:
            return
        seen.add(n)
        full.append(v)

    push(base)
    push(_strip_trailing_markers(base))

    inside, outside = _split_paren(base)
    if not inside:
        # 無括號結構時，頂層 `A／B`／`A — B` 之各支為並列之完整表記
        parts = re.split(r"[—–]{1,2}|／|/", base)
        if len(parts) > 1:
            for part in parts:
                push(part)
                push(_strip_trailing_markers(part))

    halves, hseen = [], set()
    if len(inside) == 1 and len(outside) == 1:
        for seg in (outside[0], inside[0]):
            seg = _strip_trailing_markers(seg) or _clean_label(seg)
            n = normalize_label(seg)
            if len(n) < 3 or n in hseen:
                continue
            hseen.add(n)
            halves.append(seg)
        if len(halves) < 2:
            # 一半退化（`Human Authority Gate (P5)` 之 `P5` 為交叉引註而非名之一半）→
            # 非兩半體例；另一半即該條之**完整**名，逕引之非截半。
            for h in halves:
                push(h)
            halves = []
    return full, halves


def leading_overlap(label: str, name: str) -> float:
    """回「標籤與原文名之共同前段」占原文名之比例（正規化後逐字元）。

    用途（B2 之推廣）：`WM.36（World Concept Registry 七欄）` 之原文名為
    「World Concept Registry 與消費規則」——標籤**逐字照抄名之前段後、換上自己的尾巴**，
    而「七欄」又恰為該條正文用語，故「正文逐字支撐」判準（`_text_supported`）反而放行之。
    此類「前段截取」與 `X（Y）` 之截半同病：**被換掉之尾段即靜默落空之義務**（WM.36 之
    「消費規則」正是下層之義務所在）。以共同前段比例辨識之。
    """
    a, b = normalize_label(label), normalize_label(name)
    if not a or not b:
        return 0.0
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n / len(b)


def _tokens(label: str) -> list:
    """標籤之比對詞元：ASCII 詞（≥2 字母）＋ CJK 連續段之 2-gram。

    單字 CJK（之／與／非…）不成詞元——訊號太弱，計入只會稀釋閾值並製造偽陰性。
    """
    s = unicodedata.normalize("NFKC", label)
    s = re.sub(r"\[[NI]\]", "", s).replace("*", "").replace("`", "")
    out = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9._-]+", s):
        out.append(w.lower())
    for run in re.findall(r"[一-鿿]{2,}", s):
        for i in range(len(run) - 1):
            out.append(run[i:i + 2])
    return out


def label_overlap(label: str, text: str) -> tuple:
    """回 (命中相異詞元數, 相異詞元總數)：標籤詞元於條款正文中之逐字命中率。

    **詞元須去重**：前版以 `_tokens()` 之**清單**計數，故同一詞重複出現即重複計入分子——
    起草者只須把一個碰巧命中之詞複製數遍，即可把命中率推過閾值，而誤標之標籤原封不動。
    實證：`禁插補冒充 Representation` ×4 → 4/8 命中，恰過 50% 閘門，README 之旗艦病例
    `P2.E4` 就此靜默轉綠。以清單計數等同**獎勵冗詞**：判準所量者應為「標籤用了多少憲章
    原文之詞」，而非「起草者按了幾次複製」。故取相異詞元集合為分母與分子之共同基礎。
    """
    toks = set(_tokens(label))
    hay = normalize_label(text)
    hit = sum(1 for t in toks if t in hay)
    return hit, len(toks)


def enumerate_clause_labels(mc_text: str, source: str = "MC") -> dict:
    """回 code → {"paren_name", "full_forms", "halves", "text", "line", "source"}。

    `paren_name` 為憲章**自有標籤**（無者為 None）；`text` 為條款正文（含其祖先標題脈絡，
    供子字串／關鍵詞重疊比對）；`source` 為標籤權威來源之識別（錯誤訊息用）。
    """
    lines = mc_text.splitlines()
    anchors = []          # (line_idx, code, raw_name)
    principle_of = {}     # line_idx → 所屬 Principle 標題（祖先脈絡）
    stops = set()         # 條款正文之終止界線：任一錨點或標題
    cur_principle = ""

    # §2 定義項／§5 架構角色項等 numbered list item 項次（B3）
    item_anchors = {i: (code, raw) for i, code, raw in _list_item_anchors(mc_text)}

    for i, ln in enumerate(lines):
        if i in item_anchors:
            code, raw = item_anchors[i]
            stops.add(i)
            anchors.append((i, code, raw))
            continue
        m = _H_PRINCIPLE.match(ln)
        if m:
            cur_principle = f"Principle {m.group(1)} — {m.group(2)}"
            principle_of[i] = cur_principle
            # Principle 標題本身非條款，但**必須**終止前一條款之正文跨度：否則 P3.E3 之正文
            # 將吃進「Principle 4 — Evidence Before Conclusion」，使「Evidence」憑空命中，
            # 誤放行「identity claim 之 Evidence 要求」此一實證誤標。
            stops.add(i)
            continue
        m = _H_SECTION.match(ln)
        if m:
            cur_principle = ""
            stops.add(i)
            anchors.append((i, f"§{m.group(1)}", _clean_label(m.group(2))))
            # §1.1 `Prime Axiom（PA）—— 永恆條款（Eternity Clause）` 同時為 PA 之定義所在
            if m.group(1) == "1.1" and "Prime Axiom" in m.group(2):
                anchors.append((i, "PA", "Prime Axiom"))
            continue
        m = _H_FORBIDDEN.match(ln)
        if m:
            stops.add(i)
            anchors.append((i, m.group(1), _clean_label(m.group(2))))
            continue
        m = _B_CLAUSE.match(ln)
        if m:
            principle_of[i] = cur_principle
            stops.add(i)
            anchors.append((i, m.group(1), _clean_label(m.group(2))))
            continue
        m = _EV_NODE.match(ln)
        if m:
            stops.add(i)
            anchors.append((i, f"EV.{m.group(1)}", _clean_label(m.group(2))))

    anchors.sort(key=lambda a: a[0])
    out = {}
    for idx, (i, code, raw) in enumerate(anchors):
        end = min([s for s in stops if s > i] or [len(lines)])
        body = "\n".join(lines[i:max(end, i + 1)])
        ctx = principle_of.get(i, "")
        text = f"{ctx}\n{body}" if ctx else body
        name = raw if raw and normalize_label(raw) not in _GENERIC_LABELS else ""
        if code in out:
            # 同代號重複現身（如 §4 章標題 vs 圍籬圖）：保留首見之標籤，正文相加
            out[code]["text"] += "\n" + text
            if not out[code]["paren_name"] and name:
                full, halves = _label_forms(name)
                out[code].update(paren_name=name, full_forms=full, halves=halves)
            continue
        full, halves = _label_forms(name) if name else ([], [])
        out[code] = {
            "paren_name": name or None,
            "full_forms": full,
            "halves": halves,
            "text": text,
            "line": i + 1,
            "source": source,
        }
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 上層規格之原文標籤（B5：TR.D–TR.G 過半矩陣納入同一 gate）
#
# 上層規格條款錨之體例高度一致（六份生效規格逐一實測）：
#   `> **WM.36（World Concept Registry 與消費規則）[N｜refines｜`AUGUR-MC v1.2 §P1.E2`…]**`
# 標籤即括號名；`[N｜…]` 為效力標注與掛鉤來源，非標籤之一部分（由 `_EFFECT_TAG` 剝除）。
# ──────────────────────────────────────────────────────────────────────────────

_SPEC_CLAUSE = re.compile(r"^\s*>?\s*(?:[*-]\s+)?\*\*(" + SPEC_CODE_ALT + r")\s*(.*?)\*\*")
_SPEC_ANY_H = re.compile(r"^\s*>?\s*#{1,4}\s")

# Annex 掛鉤表列（IDO／KDI／KDO／DI／DO）：標題體例只抽出 *.0；其餘在 `| **X.n** | … |`。
# 表列無 `（括號名）` 標題體例 → `paren_name=None`，TR 濃縮走正文支撐判準。
_ANNEX_HOOK_TABLE_ROW = re.compile(
    r"^\|\s*\*\*((?:IDO|KDI|KDO|DI|DO)\.\d+)\*\*[^\n|]*\|(.+)$",
    re.M,
)


def _enumerate_annex_hook_table_labels(text: str, source: str) -> dict:
    """自 Annex 掛鉤表列抽出 IDO/KDI/KDO/DI/DO.n → 標籤條目（僅補標題體例未覆蓋者）。"""
    out = {}
    for m in _ANNEX_HOOK_TABLE_ROW.finditer(text):
        code = m.group(1)
        cells = [c.strip() for c in m.group(2).split("|")]
        cells = [c for c in cells if c and not re.match(r"^-+$", c)]
        matter = _clean_label(" ".join(cells).replace("**", ""))
        line = text[:m.start()].count("\n") + 1
        text_body = f"{matter}\n{m.group(0)}"
        out[code] = {
            "paren_name": None,
            "full_forms": [],
            "halves": [],
            "text": text_body,
            "line": line,
            "source": source,
        }
    return out


def enumerate_spec_clause_labels(text: str, source: str) -> dict:
    """回 code → {…}（同 `enumerate_clause_labels` 之結構）：上層規格之 [N] 條款原文標籤。"""
    lines = text.splitlines()
    anchors, stops = [], set()
    for i, ln in enumerate(lines):
        if _SPEC_ANY_H.match(ln):
            stops.add(i)
            continue
        m = _SPEC_CLAUSE.match(ln)
        if m:
            stops.add(i)
            anchors.append((i, m.group(1), _clean_label(m.group(2))))

    out = {}
    for i, code, raw in anchors:
        end = min([s for s in stops if s > i] or [len(lines)])
        text_body = "\n".join(lines[i:max(end, i + 1)])
        name = raw if raw and normalize_label(raw) not in _GENERIC_LABELS else ""
        if code in out:
            out[code]["text"] += "\n" + text_body
            continue
        full, halves = _label_forms(name) if name else ([], [])
        out[code] = {
            "paren_name": name or None,
            "full_forms": full,
            "halves": halves,
            "text": text_body,
            "line": i + 1,
            "source": source,
        }
    # 表列掛鉤：標題已有者不覆寫；其餘併入宇宙。
    for code, d in _enumerate_annex_hook_table_labels(text, source).items():
        if code not in out:
            out[code] = d
    return out


def load_clause_labels(mc_path) -> dict:
    with open(mc_path, encoding="utf-8") as f:
        return enumerate_clause_labels(f.read(), source="MC")


def current_mc_version(mc_text: str) -> str:
    """抽取現行憲章版本（§0.1 版本欄）。找不到回空字串。"""
    m = re.search(r"版本[:：]\s*\**v?(\d+\.\d+)", mc_text)
    return f"v{m.group(1)}" if m else ""


def load(mc_path) -> tuple:
    """回 (clauses:set, version:str)。"""
    with open(mc_path, encoding="utf-8") as f:
        text = f.read()
    return enumerate_clauses(text), current_mc_version(text)


def _selftest() -> int:
    import pathlib

    mc_path = pathlib.Path(__file__).resolve().parents[2] / "constitution" / "META-CONSTITUTION.md"
    if not mc_path.exists():
        print("mc_clauses selftest: SKIP（非 repo 內執行，找不到 META-CONSTITUTION.md）")
        return 0
    clauses, version = load(str(mc_path))
    ok = bool(version) and "PA" in clauses and "§2.5" in clauses and "F1" in clauses
    print("mc_clauses selftest:" + (" OK" if ok else " FAIL") + f" version={version} n_clauses={len(clauses)}")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
