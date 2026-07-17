"""從 META-CONSTITUTION.md 枚舉 [N] 條款宇宙（供 WM.44 形式充分性覆蓋檢查）。

依 `AUGUR-MC v1.3 §0.3` 條款編號系統：PA｜P{n}.D / P{n}.W{m} / P{n}.Y / P{n}.E{m}｜EV.1–EV.12｜F1–F6，
另加 §0–§8 之 [N] 章節條款（§x.y 標 [N] 者）。

⚠ 骨架限制：本枚舉以正則抽取「可機器辨識之條款代號」，涵蓋 PA/P#.*/EV.#/F#/§x.y[N]。WM.44 要求之
「全部 [N] 條款」之完全形式枚舉（含正文散落之 MUST/MUST NOT 細目）為 phase-2 強化；故 compliance_lint
之 WM.44 覆蓋檢查以 **warning 級**報告（不誤紅已生效之 AUGUR-WM v1.0），完全強制留待嚴格枚舉就緒。
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


def enumerate_clauses(mc_text: str) -> set:
    """回 MC [N] 條款代號集合（骨架枚舉）：PA/P#.*/EV.#/F#、[N] 章（§n）與子條（§n.m）。"""
    clauses = set()
    for pat, fmt in _CLAUSE_PATTERNS:
        for m in pat.finditer(mc_text):
            clauses.add(fmt(m))
    for m in _SECTION_CH.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    for m in _SECTION_SUB.finditer(mc_text):
        clauses.add(f"§{m.group(1)}")
    return clauses


# ──────────────────────────────────────────────────────────────────────────────
# 憲章原文標籤資料（WM.44-LABEL 用）
#
# 病灶：起草者憑記憶「轉述」上層條款標籤，再拿自己的轉述去推論，致真實義務被判「不觸及」而
# 靜默落空（linter 綠燈但實質錯誤）。本區塊自憲章原文抽出每條 [N] 條款之**自有標籤**與**正文**，
# 使「規格所載標籤 vs 憲章原文」成為機器可判之比對，而非人類記憶之比對。
# ──────────────────────────────────────────────────────────────────────────────

# 條款代號之字面（供憲章側與規格側共用）。§ 前綴於正規化時剝除（`§P5.D` ≡ `P5.D`）。
CODE_ALT = r"(?:PA|P[1-5]\.(?:D|Y|W\d+|E\d+)|EV\.\d+|F[1-6]|§\d+(?:\.\d+)?)"

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


def _clean_label(raw: str) -> str:
    """去效力標注／收尾標點／markdown 強調符號，回條款自有標籤之原字串（未正規化）。

    標籤緊接代號者體例上整段括起（`* **P1.E1（開放來源）**：`）——此時脫去最外層括號，
    俾錯誤訊息所印之「憲章原文」與規格側標籤同形可比。
    """
    s = re.sub(r"\[[NI]\]", "", raw)
    s = s.replace("**", "").replace("`", "")
    s = _BOX_CHARS.split(s)[0]
    s = s.strip().strip("：:—–- ").strip()
    inside, outside = _split_paren(s)
    if len(inside) == 1 and not outside:
        s = inside[0].strip()
    return s


def normalize_label(s: str) -> str:
    """比對用正規化：NFKC（全半形統一）→ 去 markdown 強調／反引號／效力標注 → 去全部空白 → 小寫。"""
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\[[NI]\]", "", s)
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


def _name_variants(raw: str) -> list:
    """由條款自有標籤原字串展開可接受之等值表記。

    憲章體例常為「英文名（中文名）」（如 `Five Immutable Principles（五大不可違反原則）`、
    `Time（雙時間性）`）——兩者皆為憲章原文，規格擇一引用均非轉述，故並列為合法變體。
    """
    variants, seen = [], set()

    def push(v):
        v = _clean_label(v)
        # 變體須具辨識度：< 3 字元者（如 `EV.9  Human Authority Gate (P5)` 之 `P5`）不足以
        # 作為「引用了憲章原文」之證據，反易造成偽陰性 → 捨棄。
        if len(normalize_label(v)) < 3:
            return
        if normalize_label(v) in seen:
            return
        seen.add(normalize_label(v))
        variants.append(v)

    push(raw)
    inside, outside = _split_paren(raw)
    for seg in inside + outside:
        for part in re.split(r"[—–]{1,2}|／|/", seg):
            push(part)
            # 尾綴體例標記（DEFER 等）不屬名稱本體
            words = part.strip().split()
            while words and words[-1].strip("[]").lower() in _TRAILING_MARKERS:
                words.pop()
                push(" ".join(words))
    return variants


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
    """回 (命中詞元數, 總詞元數)：標籤詞元於條款正文中之逐字命中率。"""
    toks = _tokens(label)
    hay = normalize_label(text)
    hit = sum(1 for t in toks if t in hay)
    return hit, len(toks)


def enumerate_clause_labels(mc_text: str) -> dict:
    """回 code → {"paren_name": str|None, "names": [變體…], "text": 條款正文, "line": 行號}。

    `paren_name` 為憲章**自有標籤**（無者為 None）；`text` 為條款正文（含其祖先標題脈絡，
    供子字串／關鍵詞重疊比對）。
    """
    lines = mc_text.splitlines()
    anchors = []          # (line_idx, code, raw_name)
    principle_of = {}     # line_idx → 所屬 Principle 標題（祖先脈絡）
    stops = set()         # 條款正文之終止界線：任一錨點或標題
    cur_principle = ""

    for i, ln in enumerate(lines):
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
                out[code]["paren_name"] = name
                out[code]["names"] = _name_variants(name)
            continue
        out[code] = {
            "paren_name": name or None,
            "names": _name_variants(name) if name else [],
            "text": text,
            "line": i + 1,
        }
    return out


def load_clause_labels(mc_path) -> dict:
    with open(mc_path, encoding="utf-8") as f:
        return enumerate_clause_labels(f.read())


def current_mc_version(mc_text: str) -> str:
    """抽取現行憲章版本（§0.1 版本欄）。找不到回空字串。"""
    m = re.search(r"版本[:：]\s*\**v?(\d+\.\d+)", mc_text)
    return f"v{m.group(1)}" if m else ""


def load(mc_path) -> tuple:
    """回 (clauses:set, version:str)。"""
    with open(mc_path, encoding="utf-8") as f:
        text = f.read()
    return enumerate_clauses(text), current_mc_version(text)
