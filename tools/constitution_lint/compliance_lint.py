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
import unicodedata

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
                "AUGUR-WM v1.0 §WM.40 / AUGUR-MC v1.3 §0.6(a)", kind="wm40_extension")


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
    res.meta["wm44_uncited"] = len(uncited)      # 覆蓋缺口之機器來源（分母＝條款宇宙）
    res.meta["wm44_universe"] = len(clauses)
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

# Annex TR 標題之**單一判準**，二錨共用，**僅層級不同**（`_ANNEX_TR_HEAD` 限 h2、
# `_ANNEX_TR_HEAD_ANY` 容 h1–h6）。
#
# **為何必須同判準**（本註解為 2026-07-17 三輪修正所補，記其病灶以為戒）：前版二錨之判準
# **正交**——`_ANNEX_TR_HEAD` 作 `^##\s+.*Annex TR`（容前綴、強制 h2），
# `_ANNEX_TR_HEAD_ANY` 作 `^#{1,6}\s+(?:\*\*)?Annex TR`（容任意層級、強制 `Annex TR` 起首）。
# 交集外之標題遂**雙盲**（二錨皆不 match），落入 `_report_no_tr_region` 最寬鬆之 INFO 分支，
# 令工具說出「本規格無 Annex TR 標題」此一可由 `grep -n 'Annex TR'` 立即證偽之斷言。實測反例：
#   `### 附錄 TR：Annex TR 追溯矩陣` → HEAD=False、ANY=False（雙盲 → 假 INFO ＋ PASS）
#   `## 本規格未設 Annex TR`        → HEAD=True、ANY=False（同一行在區段錨為「是附錄」、
#                                     在發聲錨為「不是附錄」——恰與 ANY 註解自載之判準相反）
# 判準正交是**縫**，不是保守：二錨若對同一行給出相反答案，其差集必為無人看守之地帶。
#
# 敘述性標題之排除改以**獨立之否定前瞻**為之（而非靠「`Annex TR` 起首」順帶擋下）：
# `## 本規格未設 Annex TR` 是**在講** Annex TR，不是 Annex TR 本身。此排除同步套進二錨，
# 故二者對任一行恆給相同答案（僅層級不同）。前版之「起首」限制連 `### 附錄 TR：Annex TR
# 追溯矩陣` 這種**真附錄**也一併擋掉，代價遠大於其所欲防之偽陽性。
_TR_HEAD_TAIL = r"(?!.*(?:未設|不設|未列|不含|沒有|無)\s*Annex\s+TR).*Annex\s+TR\b"
_ANNEX_TR_HEAD = re.compile(r"^##\s+" + _TR_HEAD_TAIL, re.M | re.I)
_H2 = re.compile(r"^##\s+")
# **任一層級**之 Annex TR 標題（`# Annex TR`／`### Annex TR`…）。用途見 `_check_wm44_label`
# 之無區段分支：`_ANNEX_TR_HEAD` 硬性要求 `##`，故 h1／h3 之 Annex TR 會令區段解析回空集，
# 而「有 Annex TR 但解析不到」與「根本沒有 Annex TR」是**截然不同**之二事，須分別處置。
_ANNEX_TR_HEAD_ANY = re.compile(r"^#{1,6}\s+" + _TR_HEAD_TAIL, re.M | re.I)
# 檔內任一標題（用於認出**文件標題行**，見 `_find_annex_tr_head`）
_ANY_HEAD = re.compile(r"^#{1,6}\s+\S", re.M)


def _find_annex_tr_head(text: str):
    """回**附錄本體**之 Annex TR 標題 match（無則 None）。

    排除**文件標題行**（檔內第一個標題）：`# Fixture：Annex TR 憲章誤標` 這類標題是
    **在講** Annex TR 之文件，不是 Annex TR 附錄本身；以之報「本規格確有 Annex TR 標題、
    層級為 h1」即為工具自造之不實陳述。

    以「是否為檔內第一個標題」為判準，而非以層級（h1）為判準：`specs/ONTOLOGY-SPECIFICATION.md`
    之**真附錄**恰為 h1（`# Annex TR [I]`，:415，該檔全部附錄一律 h1、為其一貫體例），
    以層級排除將把真附錄一併排除，正是本函式所欲防之反面。
    """
    first = _ANY_HEAD.search(text)
    for m in _ANNEX_TR_HEAD_ANY.finditer(text):
        if first and m.start() == first.start():
            continue                      # 文件標題行順帶提及，非附錄本身
        return m
    return None
# 「本規格之形式充分性以 Annex TR 之逐條枚舉為據」之斷言用語（ONT Annex CS §CS.10、
# ID【地位】節皆屬之）。斷言其存在卻無可解析之區段者，該斷言即無從查證。
#
# **本判準為啟發式，非窮盡**（據實揭露，不得以斷言取代實測）：前版為五個中文字串之**閉集**
# （`形式充分性`／`逐條枚舉`／`逐條完整枚舉`／`逐條對照`／`追溯矩陣`），同義改寫即整條防線
# 失效——「逐一枚舉」「逐條列舉」「完整枚舉」「對照表」「traceability matrix」「無遺漏」
# 等全部逃逸。改以**詞族 regex** 覆蓋，並容英文（`re.I`）。
# **已知逃逸面（仍為啟發式之殘留，接手者請勿讀為窮盡）**：全新造語、跨語言混寫、以圖表
# 或條列暗示而不使用任何上開詞族者，本判準仍抓不到。此為判準之界，不是它的證明。
_TR_ASSERT_RE = re.compile(
    r"(?:逐[條条一](?:完整)?(?:枚舉|枚举|列舉|列举|對照|对照|比對|比对|映射)"
    r"|(?:形式(?:要件)?)(?:充分性|充足)"
    r"|追溯矩陣|追溯矩阵|對照總?表|对照总?表"
    r"|缺\s*0\s*[條条]"
    r"|clause[-\s]?by[-\s]?clause"
    r"|traceability\s+matrix)",
    re.I)
# 表格列（首格為條款代號欄）
_TABLE_ROW = re.compile(r"^\s*\|(.+)$")
# 代號緊接標籤：`§P5.D（…`、`P1.E1（…`、`F4（…`、`EV.1（…`、`§3（…`、`WM.36（…`、`ID.30（…`
# （反引號／** 已先剝除）。第二捕獲組為**區段列**之尾碼（`WM.6–WM.11（…）`）——B5：TR.C–TR.G
# 大量採區段列，若逕以尾碼單條受檢，複合標籤必然誤紅。
_CODE_LABEL = re.compile(
    r"(?<![A-Za-z0-9.])(§?" + mc_clauses.ANY_CODE_ALT + r")"
    r"(?:\s*[–—]\s*(§?" + mc_clauses.ANY_CODE_ALT + r"))?\s*[（(]")
# 多代號共一標籤之複合列（`ID.70–ID.71／ID.80–ID.81（…）`、`L6.11／L6.12（…）`）——
# 前版僅 `_CODE_LABEL` 匹配**緊鄰開括號之末代號（組）**，其餘代號靜默不入比對集：標籤被
# 拿去只對末組正文相繩（三鏡重審／鏡三指認之盲區；誠實之全段標籤反因此誤紅）。現抽出
# 全部代號組，聯集交 `_range_clause`。
_CODE_GROUP_SRC = (r"§?" + mc_clauses.ANY_CODE_ALT
                   + r"(?:\s*[–—]\s*§?" + mc_clauses.ANY_CODE_ALT + r")?")
_COMPOUND_LABEL = re.compile(
    r"(?<![A-Za-z0-9.])(" + _CODE_GROUP_SRC
    + r"(?:\s*[／/]\s*" + _CODE_GROUP_SRC + r")+)\s*[（(]")
_GROUP_SPLIT = re.compile(
    r"(§?" + mc_clauses.ANY_CODE_ALT + r")"
    r"(?:\s*[–—]\s*(§?" + mc_clauses.ANY_CODE_ALT + r"))?")
# 項次交叉引註而非標籤：`ID.30(c)`、`§WM.13(iii)`、`§8.5(b)` 之括號內容為項次代號，非標籤宣稱。
_ITEM_REF = re.compile(r"^(?:[a-z]{1,2}|[ivx]{1,4}|\d+)$", re.I)
# **兜底錨**（`_row_code_labels` 用）：「像條款代號」卻不合 `ANY_CODE_ALT` 者——形如
# `字母開頭之識別符 ＋ 點 ＋ 英數`（`P9.E9`、`P7.E1`、`KS.99`），緊接開括號。
# 要求含**點**且以字母起首：純中文詞後接括號（表列中之說明文字）不得誤入，此為偽陽性之界。
# 抽出後交 `_report_unresolved_code` 判之——該函式本已備「不合任何已知形態」之 WARNING
# 分支，前為死碼（抽取階段就先把這些列丟了，永遠到不了那裡）。
_LOOSE_CODE_LABEL = re.compile(r"(?<![A-Za-z0-9.])(§?[A-Za-z][A-Za-z0-9]*\.[A-Za-z0-9.]+)\s*[（(]")

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


def _asserts_tr_enumeration(text: str) -> bool:
    """規格是否**自稱**其形式充分性繫於 Annex TR 之逐條枚舉。

    以 `Annex TR` 各出現處**所在之段落**內是否見 `_TR_ASSERT_RE` 之詞族判之——斷言與其標的
    恆同段出現（此即前版 docstring 自書之理由），跨段之偶合則不予採認。

    **視窗改以段落為界，不再以字元數（前版 ±120 字元）**：字元視窗使中英文密度不對稱——
    同一斷言之英文表述字元數約為中文之三倍，縱有英文詞族亦更易被切斷；且 120 這個數字本身
    無判準依據。既然理由是「同段」，就**直接以段落實作**，不必再用一個字元數去近似它。
    """
    paras = re.split(r"\n\s*\n", text)
    return any(re.search(r"Annex\s+TR\b", p, re.I) and _TR_ASSERT_RE.search(p) for p in paras)


def _report_no_tr_region(res, text, fields):
    """無可解析之 Annex TR 區段時之**發聲**（取代前版之靜默 `return`）。

    B9 教義之直接適用：前版 `if not regions: return` 令「本規格無 Annex TR」與「Annex TR
    全部比對通過」在輸出上**完全不可分辨**——兩者皆為零 finding、皆 PASS。實證突變：
    IDENTITY 之 `## Annex TR` 改為 `### Annex TR`，20 個 error 歸零且零 finding。
    實例（非假想）：`specs/ONTOLOGY-SPECIFICATION.md` 之 Annex TR 標題為 h1（`# Annex TR`），
    故其 WM.44-LABEL **從未執行**，而其 `PASS（error 0）` 曾用以支撐 RULING-2026-003。

    嚴重度分流（依「該規格是否有可查證之 Annex TR 主張」而非「是否綁定上層規格」）：

    * **ERROR｜有 Annex TR 標題但層級非 `##`**：Annex TR 確實存在，區段解析卻失敗——
      此為最惡之情形：標籤檢查零覆蓋，輸出卻與全數通過同形。
    * **ERROR｜無 Annex TR 標題，惟本文斷言形式充分性繫於 Annex TR 之逐條枚舉**：
      斷言之依據不存在於可查證之處，該斷言無從成立（ONT §CS.10 型態）。
    * **INFO｜二者皆無**：確無可作區段錨之 Annex TR 標題，且未斷言。WM.44-LABEL 之義務
      標的為 Annex TR 表列標籤，無表列即無標籤可比——此為「不適用」，非「通過」，
      故仍留痕，俾「未執行」不被讀作「已比對且通過」。**INFO 之措辭須為可查證之計數**
      （`Annex TR` 字串出現 N 次、無一構成 h2 區段錨），不得斷言「本規格無 Annex TR 標題」
      ——後者為事實斷言，而 regex 之涵蓋面恆小於該斷言之外延，說錯即為工具自造假話。
    """
    head = _find_annex_tr_head(text)
    base = ("本規格未偵得可解析之 Annex TR 區段，WM.44-LABEL 原文標籤檢查**未執行**"
            "（非「已比對且通過」）")
    if head:
        lvl = len(head.group(0)) - len(head.group(0).lstrip("#"))
        res.add("WM.44-LABEL", Severity.ERROR,
                f"{base}——惟本規格**確有** Annex TR 標題（`{head.group(0).strip()}`），"
                f"其標題層級為 h{lvl}，而本工具之區段錨點現僅認 `##`（h2），"
                f"故區段解析回空集、該附錄全部表列標籤**零覆蓋**。"
                f"零覆蓋之輸出與「全數比對通過」同形，正是本工具所欲撲滅之靜默降級（B9）；"
                f"**本次標籤判定不具權威**。"
                f"**此為工具側之錨點限制，非逕認規格有瑕疵**：`WM.44` 未課標題層級要求，"
                f"本工具亦無權命一份 [N] 規格變更其體例以遷就本工具之正則"
                f"（規格之編輯權屬其作者／Steward）。處置方式有二，擇一即可消除本零覆蓋："
                f"(a) 由工具側放寬區段錨點至 h{lvl}（見 `HANDOFF` gate 待修清單）；"
                f"(b) 由規格之作者／Steward 決定調整標題層級。二者皆未行之前，本檢查對本規格"
                f"之結果不得被引為「已比對且通過」",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="tr_absent")
        return
    if _asserts_tr_enumeration(text):
        res.add("WM.44-LABEL", Severity.ERROR,
                f"{base}——惟本規格本文**斷言**其形式充分性繫於 Annex TR 之逐條枚舉。"
                f"所斷言之枚舉依據不存在於可解析之 Annex TR 區段，該斷言本次無從查證；"
                f"以未受檢之枚舉充作形式要件已成就之依據，即 `§8.2` 所禁之「以轉述代原文」。"
                f"**本次標籤判定不具權威**",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="tr_asserted_absent")
        return
    # **可查證之計數，非事實斷言**：前版此處作「本規格**無** Annex TR 標題」——一句可由
    # `grep -n 'Annex TR'` 立即證偽之斷言（雙盲之標題正是落到此分支）。工具只能陳述**它量到
    # 什麼**（字串出現幾次、無一構成 h2 區段錨），不能替讀者宣告檔案裡沒有那個東西。
    n_mentions = len(re.findall(r"Annex\s+TR\b", text, re.I))
    res.add("WM.44-LABEL", Severity.INFO,
            f"{base}。本檔 `Annex TR` 字串出現 {n_mentions} 次，其中無一構成本工具所認之 "
            f"h2 區段錨（`## …Annex TR…`，敘述性標題如「未設 Annex TR」除外）；"
            f"亦未斷言形式充分性繫於 Annex TR 之逐條枚舉。"
            f"故 WM.44-LABEL 對本規格**不適用**（非「已比對且通過」）"
            f"{'——本檔 `Annex TR` 之出現處請以 `grep -n \"Annex TR\"` 自行覆核' if n_mentions else ''}",
            "AUGUR-WM v1.0 §WM.44")


def _annex_tr_regions(text: str):
    """回 [(起始行號, 區段文字)]：規格中全部 Annex TR 區段。"""
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if _ANNEX_TR_HEAD.match(ln)]
    out = []
    for h in heads:
        end = next((j for j in range(h + 1, len(lines)) if _H2.match(lines[j])), len(lines))
        out.append((h + 1, "\n".join(lines[h:end])))
    return out


def _strip_markup(s: str, normalize: bool = True) -> str:
    """剝除 markdown 強調符號；`normalize=True` 時另以 **NFKC** 正規化全形變體。

    **`normalize=False` 之用途——標籤須逐字引錄**：NFKC 亦會改寫標籤**內部**之全形標點
    （`／`→`/`、`（`→`(`），故若以正規化後之字串充作 finding 之「規格所載：「…」」，
    本工具即在**轉述**規格原文——一份專攻「以轉述冒充原文」之工具自己misquote，正是其所
    欲撲滅之病。**故：代號比對用正規化字串，引錄標籤用原字串。**
    （此非假想：本輪初版對全字串 NFKC，`Reality 最高抽象／來源非最高抽象` 之全形 `／`
    〔U+FF0F〕即被印成 ASCII `/`，為 G1 回歸鎖當場抓到。）

    **NFKC 之必要性（實證，非預防性）**：前版未正規化，故任何**字元層面之污損**皆於抽取
    階段即靜默蒸發、零 finding——實測 `**Ｐ1.E1**（亂編）`（全形 Ｐ）→ `[]`、
    `**P1．E1**（亂編）`（全形句點）→ `[]`，而 `**P1.E1**（亂編）` 照常受檢。亦即：**把代號
    打成全形即可令該列連同其誤標一併消失**，比修好標籤省事得多——與 `_report_unresolved_code`
    docstring 所攔之誘因倒置完全同型，且此路更便宜（改一個字元）。
    NFKC 後全形變體自動歸位為真代號並照常受檢，**零偽陽性風險**（正規化不創造新代號，
    只把同一代號之異體字歸一）。
    """
    out = s.replace("`", "").replace("**", "")
    return unicodedata.normalize("NFKC", out) if normalize else out


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
    **空白標籤不抽**（`**P1.E1**（）`）——括號內無內容者無標籤可比，非誤標。此為第三種不罰
    情形，README「僅有之二」未列，已於該處補列。

    **兜底（2026-07-17 三輪補）**：形態不合 `ANY_CODE_ALT` 之代號（`P9.E9`、`P7.E1` 等越界
    前綴）前版於此**靜默捨棄**、零 finding——即「把首格代號改壞」為修 FAIL 最便宜之路
    （改一個字元 vs 改標籤）。現改為抽出並交由 `_report_unresolved_code` 之**第三分支**
    （「代號不合任何已知條款編號形態」，前為死碼）發聲。
    """
    s = _strip_markup(cell)                       # NFKC：供**代號**比對
    raw = _strip_markup(cell, normalize=False)    # 原字串：供**標籤**逐字引錄
    # NFKC 對全形字母／句點／標點為 1:1 代換，長度恆等；惟少數相容字元會展開（`㍿`→`株式会社`），
    # 此時偏移不再對齊，逐字引錄無從安全為之——退回以正規化字串引錄，並以此旗標記其事。
    aligned = len(s) == len(raw)
    out = []
    # 凡 `_CODE_LABEL` 所涵蓋之文字範圍一律登錄，**不問其是否產出**：兜底錨不得二次解讀
    # 已由主錨作成判斷（含「不罰」之判斷）之文字。
    # **此為 B5 之回歸防線**：`ONT.1–ONT.62（型別層本體/…）` 為**區段列**，其標籤描述整個
    # 區段；若區段展開失敗而未登錄其範圍，兜底錨將另行匹配尾碼 `ONT.62（`，把**區段標籤**
    # 拿去比對**單條** `ONT.62` 之原文而誤紅——正是 `_CODE_LABEL` 註解所載、B5 已修之病。
    # （實證：本輪初版遺漏此登錄，L6 立即由 37 → 39，多出之 `ID.53`／`ONT.62` 二筆全為此類
    # 偽陽性。）
    spans = [(m.start(), m.end()) for m in _CODE_LABEL.finditer(s)]

    # 複合列先抽（多代號組共一標籤）：登錄其全span，使主錨／兜底錨不得在其內二次匹配
    compound_spans = []

    def _label_at(open_idx):
        """回逐字引錄之標籤（NFKC 僅用於定位，引錄取原字串）；無標籤／空白者回 None。"""
        norm, close = _scan_paren(s, open_idx)
        if norm is None or not norm.strip():
            return None
        text = raw[open_idx + 1:close] if aligned else norm
        text = text.strip()
        if not text or _ITEM_REF.match(mc_clauses.normalize_label(text)):
            return None
        return text

    for m in _COMPOUND_LABEL.finditer(s):
        label = _label_at(m.end() - 1)
        if label is None:
            continue
        all_codes, bad = [], False
        for gm in _GROUP_SPLIT.finditer(m.group(1)):
            c1 = _norm_code(gm.group(1))
            if gm.group(2):
                cs = _expand_range(c1, _norm_code(gm.group(2)))
                if cs is None:
                    bad = True
                    break
                all_codes.extend(cs)
            else:
                all_codes.append(c1)
        if bad or len(all_codes) < 2:
            continue
        out.append((all_codes, label))
        compound_spans.append((m.start(), m.end()))
        spans.append((m.start(), m.end()))

    def _in_compound(pos):
        return any(a <= pos < b for a, b in compound_spans)

    for m in _CODE_LABEL.finditer(s):
        if _in_compound(m.start()):
            continue
        label = _label_at(m.end() - 1)
        if label is None:
            continue
        c1 = _norm_code(m.group(1))
        if m.group(2):
            codes = _expand_range(c1, _norm_code(m.group(2)))
            if codes is None:
                continue
        else:
            codes = [c1]
        out.append((codes, label))

    # 兜底：形態不合致者（不與上開任一命中重疊者）
    for m in _LOOSE_CODE_LABEL.finditer(s):
        if any(a <= m.start() < b for a, b in spans):
            continue
        label = _label_at(m.end() - 1)
        if label is None:
            continue
        out.append(([_norm_code(m.group(1))], label))
    return out


# upper-specs 條目：`AUGUR-WM v1.0`、`AUGUR-ONT v0.1-draft`
_UPPER_TOKEN = re.compile(r"AUGUR-([A-Z0-9]+)\s+(v[\w.\-]+)")
# 正文之受拘束宣告（【地位】節體例）。**須逐行取其全部條目**，不得只取緊接「受」之第一個：
# 實體例為並列式——`並受 **AUGUR-WM v1.0**（Layer 1）、**AUGUR-ONT v1.0**（Layer 2）、
# **AUGUR-ID v1.0**（Layer 3）、**AUGUR-KS v1.0**（Layer 4）全文約束`——只認第一個時，
# L5／L6 之 ONT／ID／KS 宣告即漏認，`upper-specs` 清空之突變仍可令 L5 由 49 靜默降至 28
# （本輪初版即如此，實測後修正）。
_BODY_BOUND_LINE = re.compile(r"受\s*\*\*AUGUR-[A-Z0-9]+\s+v[\w.\-]+\*\*")
_BODY_BOUND_ITEM = re.compile(r"\*\*AUGUR-([A-Z0-9]+)\s+(v[\w.\-]+)\*\*")
# MC 為憲章本體，恆為判準來源、不列於 `upper-specs`（WM.40 之 `mc-version` 另有其欄）。
_UPPER_EXEMPT = {"MC"}


def _check_upper_specs_declared(res, text, tokens):
    """正文自承受某上層規格拘束，`upper-specs` 卻未列之 → **ERROR**。

    **B9 教義之逐字適用**：判準來源被規格**自己**承認、卻自 front-matter 抽走，與來源崩解
    同惡。此檢查存在之理由是誘因倒置——實測突變顯示，把 `upper-specs` 清空可使四份生效
    規格之 ERROR 由 151 降為 109（42 筆靜默降級），而正文「受 **AUGUR-WM v1.0** 全文約束」
    一字未改：**規格一面自承受拘束，一面把判準來源抽走，前版 gate 完全無感。**

    **判準以「規格前綴」為準，不及於版本**（審慎劃界，非放寬）：`ID:55`／`KS:67` 之正文載
    `AUGUR-ONT v0.1-draft` 而 front-matter 載 `AUGUR-ONT v1.0`，屬**版本標注未同步**之已知
    矛盾——該事項為 `AL-2026-012` 附錄丙第 2 項所列、**待 Steward 裁決**之真缺陷，非本工具
    得以自行認定者（`§8.1` 解釋權專屬 Steward）。本檢查所攔者為「**整份上層規格被自
    front-matter 抽走**」，前綴級即足以攔下；以版本比對將使工具就待決事項作成實質判斷，逾越
    其權限。此界線為**刻意**，非為遷就數字——現行五份生效規格於本檢查實測**零命中**。
    """
    if not text:
        return
    declared = set()
    for line in text.splitlines():
        if _BODY_BOUND_LINE.search(line):
            declared.update(pre for pre, _ver in _BODY_BOUND_ITEM.findall(line))
    declared -= _UPPER_EXEMPT
    listed = {pre for pre, _ver in tokens}
    for pre in sorted(declared - listed):
        res.add("WM.44-LABEL", Severity.ERROR,
                f"本規格正文自承**受 `AUGUR-{pre}` 拘束**，惟 front-matter `upper-specs` "
                f"**未列**之（現列：{sorted(listed) or '（無）'}）——該上層規格之條款標籤本次"
                f"**全部未受檢**（非「已比對且通過」）。判準來源經規格自己承認、卻自 "
                f"front-matter 抽走，與來源崩解同惡（B9）：**本次上層側之判定就該規格不具權威**。"
                f"應回復 `upper-specs` 之宣告，而非以「未列＝不受檢＝無誤」續行",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="upper_spec_undeclared")
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


def _upper_spec_labels(res, spec_path, fields, text=""):
    """依 front-matter `upper-specs` 載入各上層規格之原文標籤。回 (labels:dict, sources:list)。"""
    raw = fields.get("upper-specs", "")
    tokens = _UPPER_TOKEN.findall(raw)
    _check_upper_specs_declared(res, text, tokens)
    if not tokens:
        # **誘因倒置之封閉（2026-07-17 三輪補）**：前版於此逕 `return {}, []` 且**零 finding**。
        # 後果——「宣告了但解不到」＝ERROR（見下），「**乾脆不宣告**」＝靜默降級為 WARNING。
        # 實測突變（四份生效規格之 `upper-specs` 一律改 `[]`）：ID 31→29／KS 34→32／
        # L5 49→27／L6 37→21，**四份合計 151→109，即 42 筆 ERROR 靜默蒸發**，且無任何
        # finding 以「未宣告 upper-specs」本身為標的。與 `_report_unresolved_code` docstring
        # 所攔之誘因倒置完全同型：**把來源抽掉比修好標籤容易。**
        res.add("WM.44-LABEL", Severity.WARNING,
                "front-matter 未列 `upper-specs`（或其值無可解析之 `AUGUR-XX vY` 條目）——"
                "全部上層規格條款標籤本次**未受檢**（非「已比對且通過」）：本次標籤判定之"
                "權威來源僅有憲章（MC）一側，上層側零覆蓋",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="upper_specs_absent")
        return {}, []
    index = _spec_index(pathlib.Path(spec_path).resolve().parent)
    labels, sources = {}, []
    for pre, ver in tokens:
        path = index.get((pre, ver))
        if path is None:
            # B9 教義（`_check_wm40_closed_set_authority`）之逐字適用：front-matter 既已宣告
            # 受 `AUGUR-{pre} {ver}` 拘束（WM.40 閉集要求），該上層規格即為本規格標籤判定之
            # **判準來源**；其無法解析至規格檔者，非「某一列存疑」，而是該來源之**全部**標籤
            # 判定失其權威基礎——與閉集退回硬編碼副本為同一病灶。以 warning 呈現等於容許 CI
            # 綠燈通過一份判準來源已崩解之判定，故取 ERROR。
            res.add("WM.44-LABEL", Severity.ERROR,
                    f"front-matter `upper-specs` 所列 `AUGUR-{pre} {ver}` 無法解析至規格檔——"
                    f"該上層規格之條款標籤本次**全部未受檢**（標籤權威來源缺位，非「已比對且通過」）。"
                    f"front-matter 既已宣告受其拘束，其原文即本次標籤判定之判準來源；來源缺位時"
                    f"**該來源側之判定不具權威**（同 WM.40 閉集退回副本之情形）。"
                    f"應回復該規格檔之可解析性或更正 `upper-specs`，而非以「未檢＝無誤」續行",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="upper_spec_unresolved")
            continue
        try:
            body = pathlib.Path(path).read_text(encoding="utf-8")
        except OSError as e:
            res.add("WM.44-LABEL", Severity.ERROR,
                    f"上層規格 `AUGUR-{pre} {ver}`（{path}）不可讀：{e}——其條款標籤本次"
                    f"**全部未受檢**；判準來源不可讀時該來源側之判定不具權威（同上）",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="upper_spec_unreadable")
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


_MC_CODE_FULL = re.compile(r"^" + mc_clauses.CODE_ALT + r"$")
_SPEC_CODE_FULL = re.compile(r"^(" + "|".join(mc_clauses.SPEC_PREFIXES) + r")\.\d+$")

# Annex 掛鉤／剖面前綴 → 承載規格前綴（非獨立 `AUGUR-IDO`／`AUGUR-A` 檔）。
# A.*＝WM Annex A；T.*＝ONT Annex T；DI/DO/EO＝ONT Annex；IDO＝ID Annex DO。
_PREFIX_HOME = {
    "IDO": "ID", "KDO": "KS", "LDO": "L5",
    "A": "WM", "T": "ONT", "DI": "ONT", "DO": "ONT", "EO": "ONT",
}


def _report_unresolved_code(res, code, label, universe, sources, loc):
    """代號無法解析至任何受檢條款時之**發聲**（取代前版之靜默 `continue`）。

    前版註解自承「非受檢宇宙之代號（未列於 upper-specs）」即略過，且零 finding。後果為
    **誘因倒置**：把 11 列紅牌之代號改寫成不存在之 `P9.E9`、標籤照錯不誤，LABEL error 由
    20 降為 10 而輸出無一字提及——**弄壞代號比修好標籤容易**。README 所載之不罰情形僅二
    （「無標籤者不罰」「項次交叉引註不罰」），「代號不在宇宙」不在其列，故前版之寬待逾越
    其自載之判準。
    """
    base = (f"`{code}` 無法解析至任何受檢條款，其標籤「{label}」本次**未受檢**"
            f"（非「已比對且通過」）")
    first = code.split("–")[0]
    if _MC_CODE_FULL.match(first) and first not in universe:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"{base}——該代號合於 `AUGUR-MC §0.3` 之條款編號形態，卻不在憲章 [N] 條款宇宙"
                f"（共 {len(universe)} 條）之內：憲章側代號之宇宙為封閉且可枚舉，形態合致而不在其中者，"
                f"非誤植即杜撰。**代號不存在則其標籤無所附麗**，該列不得作為形式充分性之枚舉依據"
                f"（`§8.2`：[N] 原文優於轉述）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc, kind="code_not_in_universe")
        return
    if _SPEC_CODE_FULL.match(first):
        pre = _SPEC_CODE_FULL.match(first).group(1)
        home = _PREFIX_HOME.get(pre, pre)
        home_src = next((s for s in sources if s.startswith(f"AUGUR-{home} ")), None)
        if pre != home and home_src:
            res.add("WM.44-LABEL", Severity.WARNING,
                    f"{base}——代號前綴 `{pre}` 為 `AUGUR-{home}` Annex 掛鉤前綴"
                    f"（非獨立規格 `AUGUR-{pre}`）；已載入 {home_src}，惟代號 `{code}` "
                    f"未見於其已枚舉條款，故無原文標籤可比對（本次已解析："
                    f"{sources or '（無）'}）",
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
            return
        expect = f"AUGUR-{home}" if pre != home else f"AUGUR-{pre}"
        hint = (f"（`{pre}.*` 權威歸 {expect}，非獨立 `AUGUR-{pre}`）"
                if pre != home else "")
        res.add("WM.44-LABEL", Severity.WARNING,
                f"{base}——代號前綴 `{pre}` 屬已知規格前綴，惟 {expect} 未見於本規格"
                f"front-matter `upper-specs` 之可解析清單{hint}（本次已解析："
                f"{sources or '（無）'}），故其原文標籤無權威來源可比對"
                f"（同 `upper-specs` 無法解析之情形）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc)
        return
    res.add("WM.44-LABEL", Severity.WARNING, base + "——代號不合任何已知條款編號形態",
            "AUGUR-WM v1.0 §WM.44", loc)


def _check_wm44_label(res, text, mc_path, spec_path, fields):
    """WM.44-LABEL（error）：Annex TR 表格列所載之條款標籤須為**上位原文**，非轉述／自創詞。

    B5：權威來源＝憲章（MC）**＋ front-matter `upper-specs` 所列各上層規格**。前版僅以
    `CODE_ALT` 為錨，TR.D–TR.G 之 WM./ONT./ID./KS./L5./L6. 標籤完全不檢——「上層條款亦須以
    其原文標籤為準」與「憲章條款須以憲章原文為準」係同一義務（`§0.6(a)` lex superior 逐層適用）。
    """
    regions = _annex_tr_regions(text)
    if not regions:
        _report_no_tr_region(res, text, fields)
        return
    try:
        labels = mc_clauses.load_clause_labels(mc_path)
    except OSError:
        res.add("WM.44-LABEL", Severity.WARNING,
                f"無法載入憲章原文標籤（{mc_path}）；跳過原文標籤檢查", "AUGUR-WM v1.0 §WM.44")
        return
    upper, sources = _upper_spec_labels(res, spec_path, fields, text)
    labels.update(upper)
    try:
        universe, _ = mc_clauses.load(mc_path)
    except OSError:
        universe = set()

    checked = {}
    rows = 0
    for base, region in regions:
        for off, ln in enumerate(region.splitlines()):
            m = _TABLE_ROW.match(ln)
            if not m:
                continue
            cell = m.group(1).split("|")[0]
            if re.match(r"^\s*-{3,}\s*$", cell):     # 表格分隔列
                continue
            rows += 1
            loc = f"行 {base + off}"
            for codes, label in _row_code_labels(cell):
                if len(codes) > 1:
                    clause = _range_clause(codes, labels)
                    code = f"{codes[0]}–{codes[-1]}"
                else:
                    clause = labels.get(codes[0])
                    code = codes[0]
                if clause is None:
                    _report_unresolved_code(res, code, label, universe, sources, loc)
                    continue
                checked[clause["source"]] = checked.get(clause["source"], 0) + 1
                _judge_label(res, code, label, clause, loc)
    res.meta["label_compared"] = dict(checked)   # 逐來源之**比對**筆數（母集，非 error 數）
    res.meta["label_rows"] = rows
    if checked:
        detail = "、".join(f"{k} {v} 筆" for k, v in sorted(checked.items()))
        res.add("WM.44-LABEL", Severity.INFO,
                f"原文標籤檢查：Annex TR 已比對 {sum(checked.values())} 筆「條款代號＋標籤」對上位原文"
                f"（{detail}）。標籤權威來源：MC"
                + (f"＋upper-specs {sources}" if sources else "（front-matter 未列 upper-specs）"),
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2")
    else:
        # **零覆蓋即發聲**（2026-07-17 三輪補）：區段在、卻抽得 0 筆「代號＋標籤」對。
        # 前版此處僅 `if checked:`，故此情形連唯一之留痕 INFO 都不輸出 → **零 finding、PASS**。
        # 實證突變：IDENTITY 保留 `## Annex TR` 標題、僅刪其下全部 `|` 表列 →
        # ❌ FAIL(error 31) → ✅ PASS(error 0)，輸出與突變前逐字相同（僅餘 WM.44 骨架 warning）。
        # 此為現存最廉價之翻綠路徑：刪表列比修標籤省事。
        #
        # **不設「全部列皆為合法純代號列」之豁免**（雖 finding 容此例外）：該豁免將使「把標籤欄
        # 刪光」成為新的最廉價翻綠路徑——與本檔 `_report_unresolved_code` 所攔之誘因倒置
        # （「弄壞代號比修好標籤容易」）同型。純代號列本即不受標籤檢查，全表皆然時「零覆蓋」
        # 為**真**，據實發聲不誤傷任何人：訊息只陳述所量到者（表列 N 列、抽得 0 筆），
        # 由讀者判斷其正當與否；靜默則使讀者無從判斷。
        heads = "、".join(f"行 {b}" for b, _ in regions)
        res.add("WM.44-LABEL", Severity.ERROR,
                f"本規格有 Annex TR 區段（{heads}；共 {len(regions)} 段）惟自其表列抽得 "
                f"**0 筆**「條款代號＋標籤」對（掃得非分隔表列 {rows} 列）——原文標籤檢查"
                f"**零覆蓋**、本次判定**不具權威**（非「已比對且通過」）。"
                f"零覆蓋之輸出與「全數比對通過」同形，正是本工具所欲撲滅之靜默降級（B9）："
                f"表列既為形式充分性之枚舉依據，抽不出任何可比對之標籤時，該依據本次即未受檢，"
                f"不得充作 `§8.2` 形式要件已成就之基礎",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", kind="tr_zero_coverage")


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
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc, source=src, kind="halved_name", code=code, label=label)
            return

    # 三、**純節引不罰**：標籤為原文名之**逐字子字串**且未添附任何字元（`WM.4`（刪名測試）
    #     vs 原文「概念層獨立性＋刪名測試」；`§0.4`（權威語言）vs 原文「權威語言聲明」）。
    #     本檢查所攔者恆為「起草者之自撰片段取代原文之一部分」——純節引無自撰片段可言，
    #     報之即為不實陳述（正是本工具要撲滅之病）。前版倚賴「判準五之無條件放行」承接此類；
    #     判準五收緊後，須於此**顯式**放行，否則節引誤紅。
    #
    #     **限 `halves` 不在場者**：`X（Y）` 體例之截半（`Time（雙時間性）` → 「雙時間」）
    #     亦為子字串，惟其落空之半個義務正是 B2 所攔之病灶，故排除於本放行之外——該體例
    #     之擇一引用已由判準二依較嚴格解讀（`§8.2`）處理。
    if clause.get("paren_name") and not halves and \
            norm_label in mc_clauses.normalize_label(clause["paren_name"]):
        return

    # 四、「前段截取」（B2 之推廣）：標籤逐字照抄原文名之前段、後段換上起草者之語。
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
                    "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc, source=src, kind="leading_truncation", code=code, label=label)
            return

    # 四、**僅限自有標籤不在場之條款**，容「取自正文之逐字濃縮」（如 `P4.E1`（五元組最低
    #     不變式）——「五元組」「最低不變式」皆為 P4.E1 正文原文）。此非本檢查所針對之病灶：
    #     該條無自有標籤，起草者本就只能自正文取詞，且其顯然讀過條文。
    #
    #     **`paren_name` 在場者不適用本判準**：前版對**全部**條款跑 `_text_supported` 並於
    #     `ok` 時放行，致判準四成為判準一之**無條件大赦**——凡標籤詞元有半數見於正文者，縱
    #     其與原文名全然不符亦放行，而條款正文本就富含該條用語，此條件幾乎恆真。實證漏網：
    #     `P1.E1`（原文名＝開放來源）掛 IDENTITY 之「Reality 最高抽象／來源非最高抽象」，
    #     詞元 8/10 命中正文 → 靜默放行。README 明載判準四之適用範圍為「未觸及原文名者」，
    #     前版程式碼未實作其自身之規格。條款既有自有標籤，該標籤即為 `§8.2` 之 [N] 原文，
    #     「正文有支撐」不足以取代之——**正文用語不等於該條之標籤**。
    ok, hit, total = _text_supported(label, clause)
    if ok and not clause.get("paren_name"):
        return

    if full:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤與 {src} 原文不符——規格所載：「{label}」；{src} 原文："
                f"「{clause['paren_name']}」（{where}）；且正文亦無支撐（命中 {hit}/{total} 詞元）。"
                f"轉述之標籤不得作為推論依據（`§8.2`：[N] 原文優於轉述）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc, source=src, kind="paren_mismatch", code=code, label=label)
    else:
        res.add("WM.44-LABEL", Severity.ERROR,
                f"`{code}` 標籤疑為轉述／自創詞，非 {src} 原文——規格所載：「{label}」；"
                f"該條無自有標籤，其標籤須取自正文，惟正文僅命中 {hit}/{total} 詞元"
                f"（閾值 {_LABEL_OVERLAP_MIN:.0%}，{where}）",
                "AUGUR-WM v1.0 §WM.44 / AUGUR-MC v1.3 §8.2", loc, source=src, kind="no_text_support", code=code, label=label)


# ── 【地位】節之定位與其宣稱 ──────────────────────────────────────────────────────
_STATUS_HEAD = re.compile(r"^>?\s*##\s*【地位】", re.M)
# 「本文件已生效」之宣稱（【地位】節體例）
_CLAIM_EFFECTIVE = (
    re.compile(r"本文件為\s*\*\*v[\d.]+\s*生效版本\*\*"),
    re.compile(r"自\s*\d{4}-\d{2}-\d{2}\s*起生效"),
    re.compile(r"`?§0\.1`?\s*生效要件全部成就"),
)
# 「本文件尚未生效」之宣稱
_CLAIM_DRAFT = (
    re.compile(r"本文件為\s*\*\*[^*]*\b(?:draft|提案|草案)\b[^*]*\*\*", re.I),
    re.compile(r"本稿不生效力"),
    re.compile(r"未經[^。]{0,80}充任認定[^。]{0,120}不生效力"),
)


def _status_region(text: str) -> str:
    """【地位】節之文字（至下一個 `## ` 標題止）。無該節時回空字串。

    **本檢查僅及於【地位】節，非全檔**：此為判準之界，非放寬——本檢查所問者為「**本文件
    對自身生效狀態之宣稱**是否與 front-matter `spec-version` 相符」，該宣稱之所在即【地位】
    節。全檔掃描將命中 `L5:405`／`L6:417` 之 `### TR.Z — 殘餘生效阻卻（DRAFT）[N]`——該
    「（DRAFT）」殘留為 `AL-2026-012` 附錄乙第 3 點所載、**待 Steward 補充裁決**之真缺陷
    （附錄丙第 4 項），其性質為條款章標之記述殘留，**非本文件對自身生效狀態之宣稱**；以本
    檢查代 Steward 就該事項作成判斷，即工具僭越 `§8.1` 解釋權。該缺陷已於 [I] 文件據實揭露。
    """
    m = _STATUS_HEAD.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^>?\s*##\s+", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def _check_status_consistency(res, text, fields):
    """【地位】節之生效宣稱須與 front-matter `spec-version` 相符（error）。

    **存在理由——修的是實例、病因原封不動**：`608adc2` 以人手替五份文件補正 §0.1／【地位】
    之矛盾（36 行純替換），**卻未新增任何 gate 檢查防其再發**。實測 `grep -n 'def _check'`：
    既有九項檢查**無一**比對【地位】節之生效宣稱與 `spec-version`；`_check_version_drift`
    只比 `mc-version` 對現行憲章版本。故同一類矛盾今日仍可零成本重新引入而 gate 不發一語
    ——一份 `spec-version: v0.1-draft` 之文件於檔首宣稱「本文件為 v1.0 生效版本、§0.1 生效
    要件全部成就」，前版 gate 完全無感。**「本輪親手修完、未加鎖」正是主迴圈未經查核之
    高風險型態**：人手補正之物，下一次編輯即可原樣復發。
    """
    region = _status_region(text)
    if not region:
        return
    sv = fields.get("spec-version", "")
    is_draft = "-draft" in sv or "draft" in sv.lower()
    eff = [p.pattern for p in _CLAIM_EFFECTIVE if p.search(region)]
    drafty = [p.pattern for p in _CLAIM_DRAFT if p.search(region)]
    if is_draft and eff:
        res.add("WM.40", Severity.ERROR,
                f"front-matter `spec-version: {sv}`（**未生效之 draft**），惟【地位】節宣稱其"
                f"**已生效**（命中 {len(eff)} 項生效宣稱）——未生效之文件自稱生效，即 `§0.1` "
                f"生效要件之僭稱：充任認定屬 Steward（`§8.1`／`§0.5`／`§8.6`），文件不得自我"
                f"充任。二者必有一為假，本規格之生效狀態於本次判定**不具權威**",
                "AUGUR-MC v1.3 §0.1 / §8.6", kind="status_draft_claims_effective")
    elif not is_draft and drafty and not eff:
        res.add("WM.40", Severity.ERROR,
                f"front-matter `spec-version: {sv}`（**非 draft**），惟【地位】節仍稱草案／"
                f"提案／不生效力（命中 {len(drafty)} 項），且無任何生效宣稱——生效本之【地位】"
                f"節載其不生效力，依 `§8.2` 較嚴格解讀將勝出，本規格之生效狀態於本次判定"
                f"**不具權威**",
                "AUGUR-MC v1.3 §0.1 / §8.6", kind="status_effective_claims_draft")


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
    _check_status_consistency(res, text, fields)
    return res
