"""compliance_lint — 管「規格生效」：查 Layer 1–7 規格之 Constitutional Compliance Statement。

依 `AUGUR-WM v1.0 §WM.39–45`（Layer 1 行使 §8.3 授予之聲明格式定義權）：
- WM.40：front-matter 閉集欄位；缺欄視同無聲明（error）；空集合須顯式 `[]`/`none`。
- WM.41：本文七節（PA、P1–P5、§4 canonical chain / EV-chain），每節四項（a 所引條款 / b 合規模式 / c 論證 / d 判準揭示）。
- WM.42：緊張關係節（open-tensions 逐項或 `none`）。
- WM.43：DEFER 雙向承接（defers-in / defers-out 與 front-matter 互為索引）。
- WM.44：形式充分性——MC 全部 [N] 條款對應完備（骨架：warning 級覆蓋報告，見 mc_clauses 註）。
- **WM.44-LABEL**：Annex TR 各表所載之條款標籤須為憲章原文，非起草者之轉述（error）。
- **WM.40 閉集擴欄**：front-matter 出現 WM.40 閉集外之欄位即 error（末層無權擴充 Layer 1 之格式定義）。

**minor 版落差接受**（總綱 §5.4）：mc-version 低於現行且同 major（如引 v1.2 而現行 v1.3）→ info，不誤紅。
"""
from __future__ import annotations

import pathlib
import re

from . import mc_clauses
from .model import LintResult, Severity

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WM_SPEC = str(_REPO / "specs" / "WORLD-MODEL-SPECIFICATION.md")

# WM.40 閉集欄位 —— **僅為 WM 規格無法讀取時之退路**。權威來源恆為 WM 規格原文（見
# `_wm40_closed_set`）：閉集之定義權屬 Layer 1（§8.3 授予），linter 硬編碼一份副本即等同
# 由工具僭越該定義權；WM 修訂時副本亦將靜默失準。
_WM40_FIELDS_FALLBACK = [
    "spec", "spec-version", "layer", "mc-version", "upper-specs", "statement-format",
    "principles", "waivers", "open-tensions", "defers-in", "defers-out", "date", "author", "archive-path",
]
_WM40_COLLECTION_FIELDS = ["upper-specs", "waivers", "open-tensions", "defers-in", "defers-out"]
_WM41_PRINCIPLES = ["PA", "P1", "P2", "P3", "P4", "P5", "EV-chain"]
_WM41_ITEM_MARKERS = ["所引條款", "合規模式", "論證", "判準揭示"]  # (a)-(d)


def _fenced_blocks(text: str):
    """回 [(start_line, [block_lines])]：抽取 ``` 圍籬碼區塊（不含 blockquote 內之範本）。"""
    lines = text.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```") and not lines[i].lstrip().startswith(">"):
            start = i
            body, i = [], i + 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                body.append(lines[i])
                i += 1
            blocks.append((start + 1, body))
        i += 1
    return blocks


def _parse_front_matter(text: str):
    """找出真正之 compliance-statement 區塊（非範本：spec 值非 {…} 佔位），解析 key→value。
    回 (fields:dict, start_line:int) 或 (None, None)。"""
    for start, body in _fenced_blocks(text):
        joined = "\n".join(body)
        if not re.search(r"^\s*compliance-statement:", joined, re.M):
            continue
        fields = {}
        for ln in body:
            # SHOULD #4：放寬縮排（容 0 或 >4 空格），並顯式跳過 compliance-statement 表頭行
            m = re.match(r"^\s*([a-z-]+):\s*(.*)$", ln)
            if m and m.group(1) != "compliance-statement":
                key, val = m.group(1), m.group(2)
                val = re.sub(r"\s+#.*$", "", val).strip()   # 去行內註解
                fields[key] = val
        # 範本以 {…} 佔位；真聲明之 spec 有具體值
        if fields.get("spec") and not fields["spec"].startswith("{"):
            return fields, start
    return None, None


def _statement_region(text: str, fm_start: int) -> str:
    """聲明本文區域：front-matter 之後至文末（聲明通常置於末章/附錄）。"""
    return "\n".join(text.splitlines()[fm_start:])


_WM40_ANCHOR = re.compile(r"\*\*WM\.40[（(]")


def _wm40_closed_set(wm_path=_WM_SPEC):
    """自 `AUGUR-WM v1.0 §WM.40` **原文**動態解析 front-matter 閉集欄位（順序保留）。

    回 (fields:list, source:str)。source＝"WM 原文" 或 "fallback"。閉集之定義權屬 Layer 1；
    WM 若修訂欄位，linter 隨之——故此處解析而不硬編碼。
    """
    try:
        with open(wm_path, encoding="utf-8") as f:
            wm = f.read()
    except OSError:
        return list(_WM40_FIELDS_FALLBACK), "fallback"
    # WM.40 條文以 blockquote 承載；剝去 `> ` 前綴後取其後第一個圍籬區塊
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in wm.splitlines()]
    start = next((i for i, ln in enumerate(lines) if _WM40_ANCHOR.search(ln)), None)
    if start is None:
        return list(_WM40_FIELDS_FALLBACK), "fallback"
    fence = next((i for i in range(start, len(lines)) if lines[i].lstrip().startswith("```")), None)
    if fence is None:
        return list(_WM40_FIELDS_FALLBACK), "fallback"
    fields = []
    for ln in lines[fence + 1:]:
        if ln.lstrip().startswith("```"):
            break
        m = re.match(r"^\s+([a-z][a-z-]*):", ln)
        if m and m.group(1) != "compliance-statement" and m.group(1) not in fields:
            fields.append(m.group(1))
    if not fields:
        return list(_WM40_FIELDS_FALLBACK), "fallback"
    return fields, "WM 原文"


def _check_wm40_extension(res, fields, closed_set, source):
    """WM.40 閉集擴欄檢查（error）。

    §WM.40 明定「欄位為閉集」。聲明格式之定義權由 `AUGUR-MC §8.3` 授予 Layer 1；下層規格
    於自身 front-matter 增設閉集外欄位，即以末層之作為擴充 Layer 1 之格式定義，違 `§0.6(a)`
    lex superior。**存在性檢查抓不到此類缺陷**——欄位全在，只是多了不該有的。
    """
    extra = [k for k in fields if k not in closed_set]
    for k in extra:
        res.add("WM.40", Severity.ERROR,
                f"front-matter 出現閉集外欄位 `{k}`（WM.40 欄位為閉集{{{', '.join(closed_set)}}}，"
                f"閉集來源：{source}）——聲明格式之定義權屬 Layer 1（`AUGUR-MC §8.3` 授予），"
                f"下層規格擴充之即違 `§0.6(a)` lex superior",
                "AUGUR-WM v1.0 §WM.40 / AUGUR-MC v1.3 §0.6(a)")


def _check_wm40(res, fields, closed_set=None):
    closed_set = closed_set or _WM40_FIELDS_FALLBACK
    for f in closed_set:
        if f not in fields:
            res.add("WM.40", Severity.ERROR, f"front-matter 缺欄位 `{f}`（缺欄視同無聲明→規格不生效力）",
                    "AUGUR-WM v1.0 §WM.40")
        elif fields[f] == "":
            if f in _WM40_COLLECTION_FIELDS:
                res.add("WM.40", Severity.ERROR, f"集合欄位 `{f}` 為空白；空集合須顯式 `[]` 或 `none`（WM.39 缺載≠空集）",
                        "AUGUR-WM v1.0 §WM.39")
            else:
                # MUST-FIX B：scalar 載體欄空值＝缺載（WM.39「缺載視同無聲明」），非僅查 key 存在性
                res.add("WM.40", Severity.ERROR, f"front-matter 欄位 `{f}` 值為空（缺載視同無聲明→不生效力）",
                        "AUGUR-WM v1.0 §WM.39")
    # principles 須為七元組（空 principles 亦報紅——MUST-FIX B：移除 `got and` 短路）
    prin = fields.get("principles", "")
    got = [p.strip() for p in prin.strip("[]").split(",") if p.strip()]
    if got != _WM41_PRINCIPLES:
        res.add("WM.40", Severity.ERROR,
                f"principles 欄須為 {_WM41_PRINCIPLES}；實得 {got or '(空)'}", "AUGUR-WM v1.0 §WM.40")


def _check_version_drift(res, fields, current_ver):
    mcv = fields.get("mc-version", "")
    m = re.search(r"v(\d+)\.(\d+)", mcv)
    cur = re.search(r"v(\d+)\.(\d+)", current_ver or "")
    # MUST-FIX B：mc-version 非空但無法解析版本＝無有效版本聲明→ERROR（否則逃 §8.6 major 換證硬閘）
    if mcv and not m:
        res.add("WM.45", Severity.ERROR, f"mc-version `{mcv}` 無法解析出 v{{major}}.{{minor}}（無有效憲章版本聲明）",
                "AUGUR-MC v1.3 §8.3")
        return
    if not m or not cur:
        return  # mcv 空值已由 WM.40 覆蓋；current_ver 無法解析則跳過落差比較
    smaj, smin = int(m.group(1)), int(m.group(2))
    cmaj, cmin = int(cur.group(1)), int(cur.group(2))
    if (smaj, smin) == (cmaj, cmin):
        return
    if smaj == cmaj and (smaj, smin) < (cmaj, cmin):
        res.add("WM.45", Severity.INFO,
                f"mc-version {mcv} 低於現行 v{cmaj}.{cmin}（同 major、minor 落差）——依總綱 §5.4 接受、聲明續效，"
                f"應於下次升版換發", "AUGUR-MC v1.3 §8.6")
    elif smaj != cmaj:
        res.add("WM.45", Severity.ERROR,
                f"mc-version {mcv} 與現行 v{cmaj}.{cmin} 之 major 不同——原則級變更觸發重新認證", "AUGUR-MC v1.3 §8.6")
    else:
        res.add("WM.45", Severity.WARNING, f"mc-version {mcv} 高於現行 v{cmaj}.{cmin}（來源版本異常）", "AUGUR-MC v1.3 §8.6")


# 錨點＝標題行（## …）或粗體標籤行（> **CS.1-PA…**、**PA（…**）——兩種聲明編排皆認
_ANCHOR_RE = re.compile(r"^\s*>?\s*(?:[-*]\s*)?(?:#{2,4}\s|\*\*)")
# 合規模式閉集（WM.41(b) 五值：滿足／細化 refines／承接 carries／DEFER hooks／不適用）。
# 「不觸及」屬 WM.44 覆蓋概念、非 WM.41(b) 模式閉集，已移除（SHOULD #10）。
_MODE_TOKENS = ["滿足", "細化", "refines", "承接", "carries", "DEFER", "hooks", "不適用"]


def _principle_sections(region: str):
    """回 {principle: (first_line_idx, section_text)}。錨點為標題或粗體標籤行；容 ID 式「單標題下七粗體子節」
    與 ONT/WM 式「七獨立標題」。保留首見行號供 WM.41 順序檢查。"""
    lines = region.splitlines()
    anchors = [(i, ln) for i, ln in enumerate(lines) if _ANCHOR_RE.match(ln)]
    sections = {}
    for idx, (i, head) in enumerate(anchors):
        end = anchors[idx + 1][0] if idx + 1 < len(anchors) else len(lines)
        body = "\n".join(lines[i:end])
        for p in _WM41_PRINCIPLES:
            if p in sections:
                continue
            if p == "EV-chain":
                # 收緊：只認 canonical chain / EV-chain（移除 §4——會誤配 §4.x 及正文「（§4）」附註，MUST-FIX A）
                if re.search(r"canonical chain|EV-chain", head, re.I):
                    sections[p] = (i, body)
            elif re.search(rf"(?<![A-Za-z0-9]){re.escape(p)}(?![A-Za-z0-9])", head):
                sections[p] = (i, body)
    return sections


def _has_four_items(sec: str) -> list:
    """WM.41 四項之彈性偵測（容語義變體）。回缺項清單。
    (a) 所引條款：含 § 條款引用；(b) 合規模式：含模式閉集之一；(c) 論證：本文非空；(d) 判準揭示：字面或保守解釋。"""
    missing = []
    if "§" not in sec:
        missing.append("a.所引條款")
    if not any(t in sec for t in _MODE_TOKENS):
        missing.append("b.合規模式")
    if len(re.sub(r"\s", "", sec)) < 40:
        missing.append("c.論證")
    if "判準揭示" not in sec and "保守解釋" not in sec:
        missing.append("d.判準揭示")
    return missing


def _check_wm41(res, region):
    secs = _principle_sections(region)
    for p in _WM41_PRINCIPLES:
        if p not in secs:
            res.add("WM.41", Severity.ERROR, f"缺原則論證節 `{p}`（七節須齊：{_WM41_PRINCIPLES}）",
                    "AUGUR-WM v1.0 §WM.41")
            continue
        # 四項 (a)-(d) 為 advisory（warning）：升 error 會誤紅合法草案（如 ID draft 之 P5 節），見 README 骨架邊界
        missing = _has_four_items(secs[p][1])
        if missing:
            res.add("WM.41", Severity.WARNING,
                    f"`{p}` 節缺項 {missing}（每節須四項 a 所引條款/b 合規模式/c 論證/d 判準揭示）",
                    "AUGUR-WM v1.0 §WM.41")
    # WM.41「順序固定」：七節首見行號須依 _WM41_PRINCIPLES 嚴格遞增（MUST-FIX A）。
    # 此檢查同時堵「附錄巧合標題遮蔽真缺節」偽陰——缺節若僅於後段以背景標題現身，順序即非單調→紅。
    present = [(p, secs[p][0]) for p in _WM41_PRINCIPLES if p in secs]
    order_in_doc = [p for p, _ in sorted(present, key=lambda x: x[1])]
    expected = [p for p in _WM41_PRINCIPLES if p in secs]
    if len(present) == 7 and order_in_doc != expected:
        res.add("WM.41", Severity.ERROR,
                f"本文七節順序違反固定序（WM.41「順序固定：PA、P1–P5、§4 canonical chain」）；"
                f"實得順序 {order_in_doc}", "AUGUR-WM v1.0 §WM.41")


def _check_wm42(res, region, fields):
    open_t = fields.get("open-tensions", "")
    has_section = bool(re.search(r"緊張關係|open.tension", region, re.I))
    if open_t in ("[]", "none", "None") and not has_section:
        return  # 明載無緊張關係，且無節，合法
    if not has_section:
        res.add("WM.42", Severity.ERROR, "缺『已知緊張關係』節（無則須明載 none）", "AUGUR-WM v1.0 §WM.42")


def _check_wm43(res, fields):
    # front-matter defers-in/out 存在性已由 WM.40 覆蓋；此處查可解析（[...] 或 none）
    for f in ("defers-in", "defers-out"):
        v = fields.get(f, "")
        if v and not (v.startswith("[") or v in ("none", "None")):
            res.add("WM.43", Severity.WARNING, f"`{f}` 值 `{v}` 非可解析清單（[...] 或 none）", "AUGUR-WM v1.0 §WM.43")


def _check_wm44(res, region, mc_path):
    """形式充分性覆蓋（骨架：warning 級）。列出未在聲明中被引用之 MC [N] 條款。"""
    try:
        clauses, _ = mc_clauses.load(mc_path)
    except OSError:
        res.add("WM.44", Severity.WARNING, f"無法載入憲章條款枚舉（{mc_path}）；跳過形式充分性覆蓋", "AUGUR-WM v1.0 §WM.44")
        return
    # SHOULD #5：有邊界比對，避免 EV.1 被 EV.10/11/12 掩蓋（裸子字串會高估覆蓋）
    def _cited(c):
        return re.search(r"(?<![A-Za-z0-9.])" + re.escape(c) + r"(?![A-Za-z0-9])", region) is not None
    uncited = sorted(c for c in clauses if not _cited(c))
    if uncited:
        res.add("WM.44", Severity.WARNING,
                f"形式充分性覆蓋（骨架）：{len(uncited)}/{len(clauses)} 條 MC [N] 條款未於聲明文本出現——"
                f"完全強制留待嚴格枚舉（總綱階段 1+）。樣本：{uncited[:8]}", "AUGUR-WM v1.0 §WM.44")
    else:
        res.add("WM.44", Severity.INFO, f"形式充分性覆蓋（骨架）：{len(clauses)} 條 MC [N] 條款均見於聲明文本", "AUGUR-WM v1.0 §WM.44")


# ──────────────────────────────────────────────────────────────────────────────
# WM.44-LABEL — 原文標籤檢查
#
# 病灶（實證）：AUGUR-L7 草案連續兩輪 linter error 0，卻含系統性憲章誤標——起草者憑記憶
# 轉述上層條款標籤（`P2.E4`＝「禁插補冒充」、`F4`＝「Automation First」），再拿自己的轉述
# 去推論落點，致真實義務被判「不觸及」而靜默落空。既有檢查全屬「代號是否出現」之形式覆蓋，
# 對「代號正確而標籤是自創詞」完全盲視 → 綠燈。本檢查將「標籤 vs 憲章原文」納入機器判定。
# ──────────────────────────────────────────────────────────────────────────────

# Annex TR 區段（自 `## Annex TR …` 至下一個同級 `## ` 標題）。僅此區段受檢——正文散文中之
# 括號多為說明而非標籤宣稱，一律檢查將製造大量偽陽性。
_ANNEX_TR_HEAD = re.compile(r"^##\s+.*Annex\s+TR\b", re.M | re.I)
_H2 = re.compile(r"^##\s+")
# 表格列（首格為條款代號欄）
_TABLE_ROW = re.compile(r"^\s*\|(.+)$")
# 代號緊接標籤：`§P5.D（…`、`P1.E1（…`、`F4（…`、`EV.1（…`、`§3（…`（反引號／** 已先剝除）
_CODE_LABEL = re.compile(r"(?<![A-Za-z0-9.])(§?" + mc_clauses.CODE_ALT + r")\s*[（(]")

# 保守閾值：無自有括號名之條款，其規格標籤須為正文逐字子字串，或詞元命中率 ≥ 此值。
# 0.5 之取捨：低於半數詞元見於憲章原文者，該標籤之主體已非憲章文字而是起草者的話——
# 正是本檢查要攔的病灶。取更高值會誤紅合法之濃縮引用（如「授權鏈根為人類權威、隨時否決」，
# 其連接詞本就不在原文）。
_LABEL_OVERLAP_MIN = 0.5
# 詞元過少者不罰：1 個詞元之命中率只有 0/1 或 1/1，無統計意義，判紅即為擲硬幣。
_LABEL_MIN_TOKENS = 2


def _annex_tr_regions(text: str):
    """回 [(起始行號, 區段文字)]：規格中全部 Annex TR 區段。"""
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if _ANNEX_TR_HEAD.match(ln)]
    out = []
    for h in heads:
        end = next((j for j in range(h + 1, len(lines)) if _H2.match(lines[j])), len(lines))
        out.append((h + 1, "\n".join(lines[h:end])))
    return out


def _strip_markup(s: str) -> str:
    return s.replace("`", "").replace("**", "")


def _scan_paren(s: str, open_idx: int):
    """自 s[open_idx]（一個開括號）起掃出配對之括號內容；回 (內容, 結束索引) 或 (None, None)。"""
    pairs = {"（": "）", "(": ")"}
    close = pairs[s[open_idx]]
    op = s[open_idx]
    depth, buf = 0, ""
    for i in range(open_idx, len(s)):
        ch = s[i]
        if ch == op:
            depth += 1
            if depth == 1:
                continue
        elif ch == close:
            depth -= 1
            if depth == 0:
                return buf, i
        buf += ch
    return None, None


def _row_code_labels(cell: str):
    """自表格首格抽出全部「條款代號＋其標籤」對。回 [(code, label)]。

    **無標籤者不抽**——僅列代號之列合法（`§0.1`／`§0.2` 這類純列舉不是標籤宣稱）。
    """
    s = _strip_markup(cell)
    out = []
    for m in _CODE_LABEL.finditer(s):
        label, _ = _scan_paren(s, m.end() - 1)
        if label is None or not label.strip():
            continue
        code = m.group(1)
        # `§P5.D` ≡ `P5.D`（§ 僅為引用前綴）；章節代號 `§3` 之 § 為代號本體
        if re.match(r"^§(?:PA|P[1-5]\.|EV\.|F[1-6])", code):
            code = code[1:]
        out.append((code, label.strip()))
    return out


def _check_wm44_label(res, text, mc_path):
    """WM.44-LABEL（error）：Annex TR 表格列所載之條款標籤須為憲章原文，非轉述／自創詞。"""
    regions = _annex_tr_regions(text)
    if not regions:
        return
    try:
        labels = mc_clauses.load_clause_labels(mc_path)
    except OSError:
        res.add("WM.44-LABEL", Severity.WARNING,
                f"無法載入憲章原文標籤（{mc_path}）；跳過原文標籤檢查", "AUGUR-WM v1.0 §WM.44")
        return

    checked = 0
    for base, region in regions:
        for off, ln in enumerate(region.splitlines()):
            m = _TABLE_ROW.match(ln)
            if not m:
                continue
            cell = m.group(1).split("|")[0]
            if re.match(r"^\s*-{3,}\s*$", cell):     # 表格分隔列
                continue
            loc = f"{mc_path and ''}行 {base + off}"
            for code, label in _row_code_labels(cell):
                clause = labels.get(code)
                if clause is None:
                    continue                          # 非 MC 條款（WM/ONT/ID/KS/L5/L6 代號）→ 本檢查不轄
                checked += 1
                _judge_label(res, code, label, clause, loc)
    if checked:
        res.add("WM.44-LABEL", Severity.INFO,
                f"原文標籤檢查：Annex TR 已比對 {checked} 筆「MC 條款代號＋標籤」對憲章原文",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2")


def _text_supported(label, clause) -> tuple:
    """標籤是否有憲章原文之逐字支撐。回 (bool, hit, total)。

    支撐＝正文之逐字子字串，或詞元命中率 ≥ 閾值。詞元 < `_LABEL_MIN_TOKENS` 者一律視為
    有支撐（不罰）——樣本太小，判紅即擲硬幣。
    """
    if mc_clauses.normalize_label(label) in mc_clauses.normalize_label(clause["text"]):
        return True, 1, 1
    hit, total = mc_clauses.label_overlap(label, clause["text"])
    if total < _LABEL_MIN_TOKENS:
        return True, hit, total
    return hit / total >= _LABEL_OVERLAP_MIN, hit, total


def _judge_label(res, code, label, clause, loc):
    norm_label = mc_clauses.normalize_label(label)
    if not norm_label:
        return                                        # 無標籤者不罰：僅列代號之列合法
    names = clause.get("names") or []

    # 一、憲章自有標籤在場 → 係引用，通過。附加限定語（`§P5.W2`（…）**〔不可豁免核心〕**）
    #     不構成誤標，故採含入而非全等。
    for n in names:
        if mc_clauses.normalize_label(n) in norm_label:
            return

    # 二、自有標籤不在場，仍容「取自正文之逐字濃縮」（如 `P4.E1`（五元組最低不變式）——
    #     「五元組」「最低不變式」皆為 P4.E1 正文原文）。此非本檢查所針對之病灶：起草者
    #     顯然讀過條文。真正要攔的是**正文毫無支撐**之自創詞。
    ok, hit, total = _text_supported(label, clause)
    if ok:
        return

    if names:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤與憲章原文不符——規格所載：「{label}」；憲章原文：「{clause['paren_name']}」"
                f"（MC 行 {clause['line']}）；且正文亦無支撐（命中 {hit}/{total} 詞元）。"
                f"轉述之標籤不得作為推論依據（`§8.2`：[N] 原文優於轉述）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
    else:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤疑為轉述／自創詞，非憲章原文——規格所載：「{label}」；"
                f"該條無自有標籤，其標籤須取自正文，惟正文僅命中 {hit}/{total} 詞元"
                f"（閾值 {_LABEL_OVERLAP_MIN:.0%}，MC 行 {clause['line']}）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)


def lint_spec(spec_path: str, mc_path: str = "constitution/META-CONSTITUTION.md") -> LintResult:
    """對單一規格檔跑 compliance_lint。回 LintResult（passed＝零 error）。"""
    res = LintResult(target=spec_path)
    try:
        with open(spec_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        res.add("IO", Severity.ERROR, f"無法讀取規格檔：{e}")
        return res

    fields, fm_start = _parse_front_matter(text)
    if fields is None:
        res.add("WM.39", Severity.ERROR,
                "找不到 Constitutional Compliance Statement 之 front-matter（compliance-statement: 區塊）"
                "——無聲明之規格不生效力", "AUGUR-MC v1.3 §8.3 / AUGUR-WM v1.0 §WM.39")
        return res

    try:
        _, current_ver = mc_clauses.load(mc_path)
    except OSError:
        current_ver = ""
    region = _statement_region(text, fm_start)

    closed_set, cs_source = _wm40_closed_set()
    _check_wm40(res, fields, closed_set)
    _check_wm40_extension(res, fields, closed_set, cs_source)
    _check_version_drift(res, fields, current_ver)
    _check_wm41(res, region)
    _check_wm42(res, region, fields)
    _check_wm43(res, fields)
    _check_wm44(res, region, mc_path)
    _check_wm44_label(res, text, mc_path)
    return res
