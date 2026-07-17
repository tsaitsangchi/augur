"""compliance_lint — 管「規格生效」：查 Layer 1–7 規格之 Constitutional Compliance Statement。

依 `AUGUR-WM v1.0 §WM.39–45`（Layer 1 行使 §8.3 授予之聲明格式定義權）：
- WM.40：front-matter 閉集欄位；缺欄視同無聲明（error）；空集合須顯式 `[]`/`none`。
- WM.41：本文七節（PA、P1–P5、§4 canonical chain / EV-chain），每節四項（a 所引條款 / b 合規模式 / c 論證 / d 判準揭示）。
- WM.42：緊張關係節（open-tensions 逐項或 `none`）。
- WM.43：DEFER 雙向承接（defers-in / defers-out 與 front-matter 互為索引）。
- WM.44：形式充分性——MC 全部 [N] 條款對應完備（骨架：warning 級覆蓋報告，見 mc_clauses 註）。

**minor 版落差接受**（總綱 §5.4）：mc-version 低於現行且同 major（如引 v1.2 而現行 v1.3）→ info，不誤紅。
"""
from __future__ import annotations

import re

from . import mc_clauses
from .model import LintResult, Severity

# WM.40 閉集欄位
_WM40_FIELDS = [
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


def _check_wm40(res, fields):
    for f in _WM40_FIELDS:
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

    _check_wm40(res, fields)
    _check_version_drift(res, fields, current_ver)
    _check_wm41(res, region)
    _check_wm42(res, region, fields)
    _check_wm43(res, fields)
    _check_wm44(res, region, mc_path)
    return res
