"""compliance_lint — 管「規格生效」：查 Layer 1–7 規格之 Constitutional Compliance Statement。

依 `AUGUR-WM v1.0 §WM.39–45`（Layer 1 行使 §8.3 授予之聲明格式定義權）：
- WM.40：front-matter 閉集欄位；缺欄視同無聲明（error）；空集合須顯式 `[]`/`none`。
- WM.41：本文七節（PA、P1–P5、§4 canonical chain / EV-chain），每節四項（a 所引條款 / b 合規模式 / c 論證 / d 判準揭示）。
- WM.42：緊張關係節（open-tensions 逐項或 `none`）。
- WM.43：DEFER 雙向承接（defers-in / defers-out 與 front-matter 互為索引）。
- WM.44：形式充分性——MC 全部 [N] 條款對應完備（骨架：warning 級覆蓋報告，見 mc_clauses 註）。
- **WM.44-LABEL**：Annex TR 各表所載之條款標籤須為**上位原文**（憲章＋front-matter `upper-specs`
  所列各上層規格），非起草者之轉述（error）。
- **WM.40 閉集擴欄**：front-matter 出現 WM.40 閉集外之欄位即 error（末層無權擴充 Layer 1 之格式定義）。
- **WM.40 閉集權威**：閉集無法自 WM 原文解析而退回工具內硬編碼副本者，無條件 error（判定不具權威）。

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
# **退路一經動用即 error**（`_check_wm40_closed_set_authority`）：本清單不是「夠好的預設」，
# 而是**判定失去權威之表徵**；用它續行判定而不作聲，正是本工具要撲滅之病灶（B9）。
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
# 代號緊接標籤：`§P5.D（…`、`P1.E1（…`、`F4（…`、`EV.1（…`、`§3（…`、`WM.36（…`、`ID.30（…`
# （反引號／** 已先剝除）。第二捕獲組為**區段列**之尾碼（`WM.6–WM.11（…）`）——B5：TR.C–TR.G
# 大量採區段列，若逕以尾碼單條受檢，複合標籤必然誤紅。
_CODE_LABEL = re.compile(
    r"(?<![A-Za-z0-9.])(§?" + mc_clauses.ANY_CODE_ALT + r")"
    r"(?:\s*[–—]\s*(§?" + mc_clauses.ANY_CODE_ALT + r"))?\s*[（(]")
# 項次交叉引註而非標籤：`ID.30(c)`、`§WM.13(iii)`、`§8.5(b)` 之括號內容為項次代號，非標籤宣稱。
_ITEM_REF = re.compile(r"^(?:[a-z]{1,2}|[ivx]{1,4}|\d+)$", re.I)

# 保守閾值：無自有括號名之條款，其規格標籤須為正文逐字子字串，或詞元命中率 ≥ 此值。
# 0.5 之取捨：低於半數詞元見於憲章原文者，該標籤之主體已非憲章文字而是起草者的話——
# 正是本檢查要攔的病灶。取更高值會誤紅合法之濃縮引用（如「授權鏈根為人類權威、隨時否決」，
# 其連接詞本就不在原文）。
_LABEL_OVERLAP_MIN = 0.5
# 詞元過少者不罰：1 個詞元之命中率只有 0/1 或 1/1，無統計意義，判紅即為擲硬幣。
_LABEL_MIN_TOKENS = 2
# 「前段截取」判準（`_judge_label` 三）：共同前段須 **≥4 字元且占原文名 ≥40%**，方認定為
# 「引名之前段」而非偶合。二門檻並用之理由：4 字元濾去短偶合（`Time` 恰為 4，正是實證病例
# 之下界）；40% 濾去長名之零星偶合（30 字元名偶合 4 字元＝13%，不足以認定起草者在引該名）。
_LEAD_MIN_CHARS = 4
_LEAD_MIN_RATIO = 0.4


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


def _norm_code(code: str) -> str:
    """`§P5.D` ≡ `P5.D`、`§WM.36` ≡ `WM.36`（§ 僅為引用前綴）；章節代號 `§3` 之 § 為代號本體。"""
    if re.match(r"^§(?:PA|P[1-5]\.|EV\.|F[1-6]|" + mc_clauses.SPEC_CODE_ALT + r")", code):
        return code[1:]
    return code


def _expand_range(c1: str, c2: str):
    """`WM.6`–`WM.11` → [WM.6 … WM.11]。前綴不同／非數字尾／跨距過大者回 None。"""
    m1 = re.match(r"^(.*?)(\d+)$", c1)
    m2 = re.match(r"^(.*?)(\d+)$", c2)
    if not (m1 and m2) or m1.group(1) != m2.group(1):
        return None
    a, b = int(m1.group(2)), int(m2.group(2))
    if not 0 <= b - a <= 30:
        return None
    return [f"{m1.group(1)}{n}" for n in range(a, b + 1)]


def _row_code_labels(cell: str):
    """自表格首格抽出全部「條款代號（或代號區段）＋其標籤」對。回 [(codes:list, label)]。

    **無標籤者不抽**——僅列代號之列合法（`§0.1`／`§0.2` 這類純列舉不是標籤宣稱）。
    **項次交叉引註不抽**——`ID.30(c)` 之 `c` 非標籤。
    """
    s = _strip_markup(cell)
    out = []
    for m in _CODE_LABEL.finditer(s):
        label, _ = _scan_paren(s, m.end() - 1)
        if label is None or not label.strip():
            continue
        label = label.strip()
        if _ITEM_REF.match(mc_clauses.normalize_label(label)):
            continue
        c1 = _norm_code(m.group(1))
        if m.group(2):
            codes = _expand_range(c1, _norm_code(m.group(2)))
            if codes is None:
                continue
        else:
            codes = [c1]
        out.append((codes, label))
    return out


# upper-specs 條目：`AUGUR-WM v1.0`、`AUGUR-ONT v0.1-draft`
_UPPER_TOKEN = re.compile(r"AUGUR-([A-Z0-9]+)\s+(v[\w.\-]+)")
# 規格自身之條款代號前綴（用以認定該檔為 `AUGUR-XX` 之何者）
_OWN_CODE = re.compile(r"^\s*>?\s*\*\*([A-Z][A-Za-z0-9]*)\.\d+\s*[（(]", re.M)


def _spec_index(directory):
    """掃描規格檔，回 {(條款代號前綴, spec-version): path}。

    B5：`upper-specs` 所列之 `AUGUR-XX vY`，其 XX 恰為該規格之條款代號前綴（WM／ONT／ID／
    KS／L5／L6，六份生效規格逐一實測），vY 為其 front-matter `spec-version`。故以「檔案自述」
    決定對照，**不硬編碼檔名對照表**——規格改名或增訂版本時本索引隨之，不致靜默失準。

    搜索範圍：受檢規格自身目錄 ∪ repo `specs/`（fixtures 位於他處但引真實上層規格）。
    """
    roots, index = [], {}
    for d in (pathlib.Path(directory), _REPO / "specs"):
        d = pathlib.Path(d).resolve()
        if d.is_dir() and d not in roots:
            roots.append(d)
    for p in sorted(q for r in roots for q in r.glob("*.md")):
        try:
            body = p.read_text(encoding="utf-8")
        except OSError:
            continue
        fields, _ = _parse_front_matter(body)
        if not fields or not fields.get("spec-version"):
            continue
        prefixes = {m.group(1) for m in _OWN_CODE.finditer(body)}
        for pre in prefixes:
            index.setdefault((pre, fields["spec-version"]), str(p))
    return index


def _upper_spec_labels(res, spec_path, fields):
    """依 front-matter `upper-specs` 載入各上層規格之原文標籤。回 (labels:dict, sources:list)。"""
    raw = fields.get("upper-specs", "")
    tokens = _UPPER_TOKEN.findall(raw)
    if not tokens:
        return {}, []
    index = _spec_index(pathlib.Path(spec_path).resolve().parent)
    labels, sources = {}, []
    for pre, ver in tokens:
        path = index.get((pre, ver))
        if path is None:
            res.add("WM.44-LABEL", Severity.WARNING,
                    f"front-matter `upper-specs` 所列 `AUGUR-{pre} {ver}` 無法解析至規格檔——"
                    f"該上層規格之條款標籤本次未受檢（標籤權威來源缺位，非「已比對且通過」）",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2")
            continue
        try:
            body = pathlib.Path(path).read_text(encoding="utf-8")
        except OSError as e:
            res.add("WM.44-LABEL", Severity.WARNING,
                    f"上層規格 `AUGUR-{pre} {ver}`（{path}）不可讀：{e}；其條款標籤本次未受檢",
                    "AUGUR-WM v1.0 §WM.44")
            continue
        src = f"AUGUR-{pre} {ver}"
        sources.append(src)
        for code, d in mc_clauses.enumerate_spec_clause_labels(body, src).items():
            labels.setdefault(code, d)
    return labels, sources


def _range_clause(codes, labels):
    """區段列（`WM.6–WM.11（…）`）之合成條款：正文為區段內各條之聯集，無自有標籤。

    區段之複合標籤本就不可能等同任一單條之括號名（`表徵唯一性／登錄存在層面向` 涵蓋四條），
    故僅適用「正文逐字支撐」判準；以尾碼單條之括號名相繩即為製造偽陽性。
    """
    found = [labels[c] for c in codes if c in labels]
    if not found:
        return None
    return {
        "paren_name": None, "full_forms": [], "halves": [],
        "text": "\n".join(d["text"] for d in found),
        "line": found[0]["line"], "source": found[0]["source"],
    }


def _check_wm44_label(res, text, mc_path, spec_path, fields):
    """WM.44-LABEL（error）：Annex TR 表格列所載之條款標籤須為**上位原文**，非轉述／自創詞。

    B5：權威來源＝憲章（MC）**＋ front-matter `upper-specs` 所列各上層規格**。前版僅以
    `CODE_ALT` 為錨，TR.D–TR.G 之 WM./ONT./ID./KS./L5./L6. 標籤完全不檢——「上層條款亦須以
    其原文標籤為準」與「憲章條款須以憲章原文為準」係同一義務（`§0.6(a)` lex superior 逐層適用）。
    """
    regions = _annex_tr_regions(text)
    if not regions:
        return
    try:
        labels = mc_clauses.load_clause_labels(mc_path)
    except OSError:
        res.add("WM.44-LABEL", Severity.WARNING,
                f"無法載入憲章原文標籤（{mc_path}）；跳過原文標籤檢查", "AUGUR-WM v1.0 §WM.44")
        return
    upper, sources = _upper_spec_labels(res, spec_path, fields)
    labels.update(upper)

    checked = {}
    for base, region in regions:
        for off, ln in enumerate(region.splitlines()):
            m = _TABLE_ROW.match(ln)
            if not m:
                continue
            cell = m.group(1).split("|")[0]
            if re.match(r"^\s*-{3,}\s*$", cell):     # 表格分隔列
                continue
            loc = f"行 {base + off}"
            for codes, label in _row_code_labels(cell):
                if len(codes) > 1:
                    clause = _range_clause(codes, labels)
                    code = f"{codes[0]}–{codes[-1]}"
                else:
                    clause = labels.get(codes[0])
                    code = codes[0]
                if clause is None:
                    continue                          # 非受檢宇宙之代號（未列於 upper-specs）
                checked[clause["source"]] = checked.get(clause["source"], 0) + 1
                _judge_label(res, code, label, clause, loc)
    if checked:
        detail = "、".join(f"{k} {v} 筆" for k, v in sorted(checked.items()))
        res.add("WM.44-LABEL", Severity.INFO,
                f"原文標籤檢查：Annex TR 已比對 {sum(checked.values())} 筆「條款代號＋標籤」對上位原文"
                f"（{detail}）。標籤權威來源：MC"
                + (f"＋upper-specs {sources}" if sources else "（front-matter 未列 upper-specs）"),
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
    src = clause.get("source", "MC")
    where = f"{'MC' if src == 'MC' else src} 行 {clause['line']}"
    full = clause.get("full_forms") or []
    halves = clause.get("halves") or []

    # 一、上位**完整**標籤在場 → 係引用，通過。附加限定語（`§P5.W2`（…）**〔不可豁免核心〕**）
    #     不構成誤標，故採含入而非全等。
    for n in full:
        if mc_clauses.normalize_label(n) in norm_label:
            return

    # 二、`X（Y）` 體例之半名（B2）：**單獨匹配為必要非充分**。
    #     機器無從分辨譯名對（`Five Immutable Principles（五大不可違反原則）`）與名＋限定語
    #     （`Confidence（語義與消費）`）——前者擇一引用合法，後者截半即靜默落空半個義務。
    #     故取較嚴格解讀（`§8.2`）：擇一引用僅於「標籤即該半名本身、未添附自撰片段」時放行。
    #     兩半俱在者（次序／標點不拘）亦通過。
    if halves:
        present = [h for h in halves if mc_clauses.normalize_label(h) in norm_label]
        if present:
            if len(present) == len(halves):
                return                                # 兩半俱在 → 完整引用
            if any(norm_label == mc_clauses.normalize_label(h) for h in present):
                return                                # 標籤即該半名本身 → 擇一引用
            missing = [h for h in halves if h not in present]
            res.add("WM.44-LABEL", Severity.ERROR,
                    f"`{code}` 標籤僅引原文半名、另半遭自撰片段取代——規格所載：「{label}」；"
                    f"{src} 原文：「{clause['paren_name']}」（{where}）。已引「{present[0]}」，"
                    f"惟「{'、'.join(missing)}」面遭截除並代以起草者之語。"
                    f"截半之標籤不得作為推論依據：**被截除之面即靜默落空之義務**"
                    f"（`§8.2`：[N] 原文優於轉述；同位階存疑時採義務較重之解讀）",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
            return

    # 三、「前段截取」（B2 之推廣）：標籤逐字照抄原文名之前段、後段換上起草者之語。
    #     `WM.36`（World Concept Registry 七欄）之原文名為「World Concept Registry 與消費規則」，
    #     而「七欄」恰為該條正文用語 → 詞元命中 4/4，「正文逐字支撐」判準反而放行之。
    #     此與 `X（Y）` 截半同病，故同視：**被換掉之尾段即靜默落空之義務**（WM.36 之
    #     「消費規則」正是下層之義務所在）。未觸及原文名者（`P4.E1`（五元組最低不變式））
    #     前段重疊為 0，不受本判準拘束——其為濃縮，非截取。
    #     **純縮寫不罰**：標籤恰為原文名之前段而未添附任何字（`§0.4`（權威語言）vs 原文
    #     「權威語言聲明」）者，係節引，非「代以自撰片段」——無自撰片段可言。本判準所攔者
    #     恆為「照抄前段 ＋ 換上自己的尾巴」。（此區分亦為誠實要求：若對純縮寫報「尾段代以
    #     自撰片段」，該訊息本身即不實陳述——正是本工具要撲滅之病。）
    if clause.get("paren_name"):
        ratio = mc_clauses.leading_overlap(label, clause["paren_name"])
        keep = int(round(ratio * len(mc_clauses.normalize_label(clause["paren_name"]))))
        added = len(norm_label) > keep
        if added and keep >= _LEAD_MIN_CHARS and ratio >= _LEAD_MIN_RATIO:
            res.add("WM.44-LABEL", Severity.ERROR,
                    f"`{code}` 標籤未完整引用原文名——規格所載：「{label}」；"
                    f"{src} 原文：「{clause['paren_name']}」（{where}）。二者共同前段 {keep} 字元"
                    f"（占原文名 {ratio:.0%}）後即分歧，且標籤未含原文名整體；"
                    f"**原文名中未被引用之部分即靜默落空之義務**。"
                    f"分歧之尾段縱為該條正文用語亦不足取——正文用語不等於該條之標籤"
                    f"（`§8.2`：[N] 原文優於轉述）",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
            return

    # 四、自有標籤不在場，仍容「取自正文之逐字濃縮」（如 `P4.E1`（五元組最低不變式）——
    #     「五元組」「最低不變式」皆為 P4.E1 正文原文）。此非本檢查所針對之病灶：起草者
    #     顯然讀過條文。真正要攔的是**正文毫無支撐**之自創詞。
    ok, hit, total = _text_supported(label, clause)
    if ok:
        return

    if full:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤與 {src} 原文不符——規格所載：「{label}」；{src} 原文："
                f"「{clause['paren_name']}」（{where}）；且正文亦無支撐（命中 {hit}/{total} 詞元）。"
                f"轉述之標籤不得作為推論依據（`§8.2`：[N] 原文優於轉述）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
    else:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤疑為轉述／自創詞，非 {src} 原文——規格所載：「{label}」；"
                f"該條無自有標籤，其標籤須取自正文，惟正文僅命中 {hit}/{total} 詞元"
                f"（閾值 {_LABEL_OVERLAP_MIN:.0%}，{where}）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)


def _check_wm40_closed_set_authority(res, source):
    """B9：閉集失準之靜默降級——`_wm40_closed_set()` 於 WM 不可讀、或 WM.40 錨點格式漂移
    （`**WM.40（` → `**WM.40 ：` 之微改即足）時，前版**靜默**退回工具內硬編碼副本且零 finding，
    規格照報 ✅ PASS。程式碼於此實作了它自己在本檔 25–27 行指名為違憲之退路，且退得無聲。

    取 **ERROR** 而非 WARNING：閉集失準時，`_check_wm40`（缺欄）與 `_check_wm40_extension`
    （擴欄）之**全部**判定均以工具副本為據而失其權威基礎——非「某一項存疑」，而是整組
    WM.40 判定不具權威。以 warning 呈現等於容許 CI 綠燈通過一份判準來源已崩解之判定。
    """
    if source != "fallback":
        return
    res.add("WM.40", Severity.ERROR,
            "無法自 `AUGUR-WM §WM.40` 原文解析閉集，已退回工具內硬編碼副本"
            f"（{_WM40_FIELDS_FALLBACK}）——閉集定義權屬 Layer 1（`AUGUR-MC §8.3` 授予），"
            "以工具副本代之即違 `§0.6(a)` lex superior；**本次 WM.40 判定不具權威**"
            "（缺欄／擴欄判定均以副本為據，副本與 WM 現行條文之一致性未經證實）。"
            "應修復 WM.40 錨點解析（`_wm40_closed_set`）或回復 WM 規格之可讀性，"
            "而非以副本續行判定",
            "AUGUR-WM v1.0 §WM.40 / AUGUR-MC v1.3 §0.6(a)、§8.3")


def lint_spec(spec_path: str, mc_path: str = "constitution/META-CONSTITUTION.md",
              wm_path: str = _WM_SPEC) -> LintResult:
    """對單一規格檔跑 compliance_lint。回 LintResult（passed＝零 error）。

    `wm_path` 可注入：閉集之權威來源為 WM 原文，測試須能以**修訂後之 WM 副本**實證
    「linter 跟隨 WM 而非硬編碼」（B8）與「錨點漂移即無權威」（B9）。
    """
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

    closed_set, cs_source = _wm40_closed_set(wm_path)
    _check_wm40_closed_set_authority(res, cs_source)
    _check_wm40(res, fields, closed_set)
    _check_wm40_extension(res, fields, closed_set, cs_source)
    _check_version_drift(res, fields, current_ver)
    _check_wm41(res, region)
    _check_wm42(res, region, fields)
    _check_wm43(res, fields)
    _check_wm44(res, region, mc_path)
    _check_wm44_label(res, text, mc_path, spec_path, fields)
    return res
