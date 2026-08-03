"""selfversion_lint — 治權檔「自己宣告的版本」對不對得起自己（CS 四值 × 修訂表現行列）。

🎯 白話：一份 Compliance Statement 會在**四個地方**各寫一次自己的版本——**檔名**、
**H1 標題**、front-matter 之 **`spec-version`**、以及 **`archive-path`**。四處各由人手
寫一次，就會各自漂：現況 `CS-系統架構大憲章_v1.54.0.md` 檔名寫 v1.54.0、而標題與
`spec-version` 仍停在 v1.53.0；`CS-系統核心思想_v1.10.0.md` 同型（檔名 v1.10.0／內文
v1.9.0）。引用者依檔名以為是新版、依內文以為是舊版，**兩邊都自稱權威**。

大憲章修訂表是同病之另一形：狀態欄本應**恰有一列**非 SUPERSEDED，實況為兩列
（v1.49.0 標 `**ACTIVE**`、v1.54.0 標 `**現行**`）——**同一個意思兩種寫法**。本輪之所以
漏掉，正是因為只認其中一種寫法；故 `_ACTIVE_RE` 一律同時認
`**現行**`／`**ACTIVE**`／`現行`／`ACTIVE` **四種**，且**判定基準取「非 SUPERSEDED 之列數」**
（不繫於是否認得出該寫法），使新造第五種寫法只會落入 `status_unknown` 而**不會靜默消失**。

守原則 #10（可溯源：自稱的版本與檔案自身打架時，引用者無從判斷孰為真）、
#12（單一住所：同一個版本號寫在四處，四處就成四個權威家）。

**射程界線（誠實）**：本模組只查「檔案對**自己**版本之宣告是否自洽」——
跨檔引用是否斷鏈屬 `scripts/check_treaty_refs.py`、規格生效要件屬 `compliance_lint`，
二者皆不重複實作。SUPERSEDED 之凍結史料檔一律除外：其內文為當時之忠實記錄，
改之即竄改記錄（與 `check_treaty_refs.scan_dead_refs` 同一裁）。

執行指令矩陣
------------
  python -m tools.constitution_lint.selfversion_lint             # 印用途＋對真實 repo 唯讀實掃
  python -m tools.constitution_lint.selfversion_lint --selftest  # 合成樹紅綠自測（免 DB 免 API 免網路）
  python -m tools.constitution_lint selfversion                  # CLI 子命令（實掃；有缺陷 exit 1）
"""
from __future__ import annotations

import pathlib
import re

from .model import Finding, Severity

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parents[1]

_CS_BASIS = "AUGUR-WM v1.0 §WM.39–45（CS front-matter `spec-version`／`archive-path`）"
_REV_BASIS = "系統架構大憲章 第六部「修訂歷程體例」〔v1.22.0〕"

# 版號一律要求 ≥2 段（`v1.35`／`v1.54.0`）：單段 `v1` 於散文中太常見（「v1 提案」），
# 收之即把散文誤判為版本宣告。
_VER = r"v(\d+(?:\.\d+)+)"
_FNAME_VER = re.compile(r"_" + _VER + r"$")
_TITLE_VER = re.compile(_VER)
# `spec-version:` **必須帶 `v` 前綴**才視為版本：`CS-datasets_zh.md` 之值為日期
# `2026-06-15`（參考文件無語意版號），寬鬆解析會把日期當版本去比對而生假紅。
_SPEC_VER = re.compile(r"^\s*spec-version:\s*" + _VER + r"\s*$", re.M)
_ARCHIVE_PATH = re.compile(r"^\s*archive-path:\s*(\S+)\s*$", re.M)

_H2 = re.compile(r"^##\s+\S")


def is_frozen_banner(text: str) -> bool:
    """檔頭是否掛 SUPERSEDED 橫幅（＝凍結史料本）。

    **不用 `"SUPERSEDED" in text[:600]`**（`check_treaty_refs` 之口徑）：修訂表本身滿是
    SUPERSEDED 字樣，短檔會使該子字串落進前 600 字而**把受檢檔整份誤判為凍結本、靜默跳過**
    ——自測合成樹當場踩到（單列案「應綠」係因整檔被跳過而非因為真的一致＝假綠）。
    改判**結構**：首個 `## ` 章節之前、以 `>` 起首之橫幅行（現況 v1.47.0:3 即此形）。
    """
    for ln in text.splitlines():
        if _H2.match(ln):
            return False
        if ln.lstrip().startswith(">") and "SUPERSEDED" in ln:
            return True
    return False


def _norm(ver: str):
    """`v1.53` 與 `v1.53.0` 視為同一版（補零至三段）。

    不作字串比對：CLAUDE.md 家族用兩段（v1.35）、其餘用三段（v1.54.0），
    字串比對會把「兩段 vs 三段」判成不一致而生假紅。
    """
    parts = [int(x) for x in ver.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def cs_versions(path) -> dict:
    """回該 CS 檔四個版本宣告站點之原字串（無宣告者為 None）＋各自行號。

    回 {"檔名":…, "標題":…, "spec-version":…, "archive-path":…, "_lines": {...}}。
    """
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()

    m = _FNAME_VER.search(p.stem)
    fname = m.group(1) if m else None

    title, title_line = None, 1
    for i, ln in enumerate(lines, 1):
        if ln.startswith("# "):
            t = _TITLE_VER.search(ln)
            title, title_line = (t.group(1) if t else None), i
            break

    sv = _SPEC_VER.search(text)
    spec = sv.group(1) if sv else None
    spec_line = text.count("\n", 0, sv.start()) + 1 if sv else title_line

    ap = _ARCHIVE_PATH.search(text)
    arch = None
    arch_line = spec_line
    if ap:
        arch_line = text.count("\n", 0, ap.start()) + 1
        a = _FNAME_VER.search(pathlib.Path(ap.group(1)).stem)
        arch = a.group(1) if a else None

    return {"檔名": fname, "標題": title, "spec-version": spec, "archive-path": arch,
            "_lines": {"檔名": 1, "標題": title_line, "spec-version": spec_line,
                       "archive-path": arch_line}}


def check_cs_selfversion(repo=None) -> list:
    """`docs/compliance/CS-*.md` 之四值一致性。一檔至多一則 finding。

    兩種紅：
      (a) **不一致**——有宣告之站點彼此版號不同（現況兩例）。
      (b) **缺宣告**——檔名帶版號，卻有站點未宣告版本（版本化檔案必須四處自陳；
          `CS-CLAUDE.md`／`CS-datasets_zh.md` 檔名無版號，不受此款拘束）。
    """
    root = pathlib.Path(repo) if repo else _REPO
    out: list = []
    for p in sorted((root / "docs" / "compliance").glob("CS-*.md")):
        try:
            v = cs_versions(p)
        except OSError:
            continue
        rel = str(p.relative_to(root))
        sites = ("檔名", "標題", "spec-version", "archive-path")
        present = {k: v[k] for k in sites if v[k]}
        shown = "／".join(f"{k} {('v' + v[k]) if v[k] else '（無宣告）'}" for k in sites)
        norms = {_norm(x) for x in present.values()}
        if len(norms) > 1:
            out.append(Finding(
                "SV-1", Severity.ERROR,
                f"CS 四值版本不一致（{shown}）——同一份聲明對自己的版本有 {len(norms)} 種說法",
                _CS_BASIS, f"{rel}:{v['_lines']['spec-version']}",
                kind="cs_selfversion_mismatch",
            ))
        elif v["檔名"] and len(present) < len(sites):
            missing = "／".join(k for k in sites if not v[k])
            out.append(Finding(
                "SV-1", Severity.ERROR,
                f"CS 檔名帶版號 v{v['檔名']}，但 {missing} 未宣告版本（{shown}）"
                f"——未宣告之站點無從被比對，等於缺一道自證",
                _CS_BASIS, f"{rel}:{v['_lines']['spec-version']}",
                kind="cs_selfversion_mismatch",
            ))
    return out


# ── 修訂表狀態欄 ──────────────────────────────────────────────────────────────
_REV_HEAD = re.compile(r"^\|\s*版本\s*\|\s*日期\s*\|.*\|\s*狀態\s*\|\s*$")
_REV_ROW = re.compile(r"^\|\s*(v\d+(?:\.\d+)+)\s*\|")
_HEADING = re.compile(r"^#{1,6}\s+\S")
# **四種寫法一律認**（SSOT 逐字：本輪之所以漏正是因為只認一種）。
_ACTIVE_RE = re.compile(r"^(?:\*\*)?(?:現行|ACTIVE)(?:\*\*)?$")
_SUPERSEDED_RE = re.compile(r"^(?:\*\*)?SUPERSEDED(?:\*\*)?$")


def revision_status_rows(path) -> list:
    """回修訂表之 [{version, status, line}]；無 `| 版本 | 日期 |…| 狀態 |` 表頭回 []。

    狀態欄取**最後一格**（`修訂說明` 欄含大量全形標點，逐格切再取索引易錯位）；
    區段止於次一 markdown 標題（修訂歷程之後可能還有附錄）。
    """
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    start = next((i for i, ln in enumerate(lines) if _REV_HEAD.match(ln)), None)
    if start is None:
        return []
    out = []
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if _HEADING.match(ln):
            break
        m = _REV_ROW.match(ln)
        if not m:
            continue
        body = ln.rstrip()
        if body.endswith("|"):
            body = body[:-1]
        out.append({"version": m.group(1), "status": body.rsplit("|", 1)[-1].strip(),
                    "line": j + 1})
    return out


def check_revision_active(repo=None) -> list:
    """修訂表「狀態欄非 SUPERSEDED 者**恰為 1 列**」。

    **判定基準刻意取「非 SUPERSEDED」而非「認得出是現行」**：後者會使一個拼錯的
    狀態字（第五種寫法）從分母消失而報全綠——即本輪漏抓之機制本身。認不出的寫法
    另出 `status_unknown` 一則，使其**被看見**而非被吸收。

    SUPERSEDED 凍結史料檔（檔頭橫幅自宣）除外：其表為當時之忠實快照。
    """
    root = pathlib.Path(repo) if repo else _REPO
    out: list = []
    for p in sorted((root / "docs").glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if is_frozen_banner(text):
            continue
        rows = revision_status_rows(p)
        if not rows:
            continue
        rel = str(p.relative_to(root))
        non_sup = [r for r in rows if not _SUPERSEDED_RE.match(r["status"])]
        unknown = [r for r in non_sup if not _ACTIVE_RE.match(r["status"])]
        for r in unknown:
            out.append(Finding(
                "SV-2", Severity.ERROR,
                f"修訂表 {r['version']} 之狀態欄「{r['status']}」既非 SUPERSEDED 亦非"
                f"現行四寫法（`**現行**`／`**ACTIVE**`／`現行`／`ACTIVE`）之一",
                _REV_BASIS, f"{rel}:{r['line']}", kind="revision_status_unknown",
            ))
        if len(non_sup) != 1:
            detail = "、".join(f"{r['version']}（:{r['line']} 「{r['status']}」）" for r in non_sup) or "（無）"
            out.append(Finding(
                "SV-2", Severity.ERROR,
                f"修訂表狀態欄非 SUPERSEDED 者 {len(non_sup)} 列（應恰 1 列）：{detail}"
                f"；全表 {len(rows)} 列",
                _REV_BASIS, f"{rel}:{rows[0]['line']}", kind="revision_multi_active",
            ))
    return out


# ── CS 內容涵蓋版本 × 同規格多份並存 ────────────────────────────────────────
# 起因（2026-08-03 主 session 親驗，本模組上線當日即發現射程不足）：
# 四值全對**不代表內容跟上了**。`CS-系統架構大憲章_v1.54.0.md` 之「本版增量」段實際只寫到
# **v1.49.0**——四值檢查看的是它「說自己幾版」，看不出它「內容涵蓋到幾版」；v1.50–v1.54
# 五個版本的合規論證從未寫入，而該檔仍以現行 CS 之身分被引用。此即「綠燈量的不是它宣稱
# 在量的東西」在治權層之形。另：`docs/compliance/` 同時存在 v1.47.0／v1.48.0／v1.54.0
# 三份大憲章 CS，**皆無 SUPERSEDED 橫幅** ⇒ 引用者無從判斷孰為現行。
_INCREMENT_LINE = re.compile(r"^.*本版增量.*$", re.M)


def increment_version(path):
    """回「本版增量」段所述之本檔版本＝該字樣**之後第一個**版本號（無則 None）。

    ⚠ 首版曾寫成「取該行**最高**版本」以圖穩健（設想「相對 v1.48.0 新增（v1.49.0）」之寫法），
    結果**製造真實漏報**：`CS-系統核心思想_v1.10.0.md` 之增量段引用了「大憲章 v1.51.0」，
    取最高即抓到**別份規格的版號**（v1.51.0 > v1.10.0）而判為未落後。
    增量段必然引用其他治權檔之版號 ⇒ 全行取最大恆不可靠。
    改回取「本版增量」之後第一個——現況兩種實形（`本版增量**：v1.49.0 …`／
    `本版增量（v1.9.0；…`）皆命中，而假想寫法**現況不存在**（#3 不為假想未來加抽象）。
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    m = _INCREMENT_LINE.search(text)
    if not m:
        return None
    line = m.group(0)
    after = line[line.index("本版增量"):]
    v = _TITLE_VER.search(after)
    return v.group(1) if v else None


def check_cs_content_currency(repo=None) -> list:
    """(c) 內容涵蓋版本落後檔名版本；(d) 同一規格多份非凍結 CS 並存。"""
    root = pathlib.Path(repo) if repo else _REPO
    out: list = []
    by_spec: dict = {}
    for p in sorted((root / "docs" / "compliance").glob("CS-*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(p.relative_to(root))
        stem_no_ver = _FNAME_VER.sub("", p.stem)
        by_spec.setdefault(stem_no_ver, []).append((p, rel, is_frozen_banner(text)))

        fname_v = (_FNAME_VER.search(p.stem) or [None, None])[1] if _FNAME_VER.search(p.stem) else None
        if not fname_v or is_frozen_banner(text):
            continue
        inc = increment_version(p)
        # 無增量段者不在本款射程（節次完備性屬 compliance_lint 之 WM.41），不重複實作。
        if inc and _norm(inc) < _norm(fname_v):
            line = text.count("\n", 0, _INCREMENT_LINE.search(text).start()) + 1
            out.append(Finding(
                "SV-3", Severity.ERROR,
                f"CS 內容落後自己的版號：檔名 v{fname_v}，但「本版增量」只寫到 v{inc}"
                f"——中間各版之合規論證從未寫入，而本檔仍以現行 CS 身分被引用",
                _CS_BASIS, f"{rel}:{line}", kind="cs_content_stale",
            ))

    for spec, files in sorted(by_spec.items()):
        live = [(p, rel) for p, rel, frozen in files if not frozen]
        if len(live) > 1:
            detail = "、".join(rel for _, rel in live)
            out.append(Finding(
                "SV-4", Severity.ERROR,
                f"同一規格有 {len(live)} 份**皆未標 SUPERSEDED** 之 CS 並存：{detail}"
                f"——引用者無從判斷孰為現行（凍結本須掛檔頭 SUPERSEDED 橫幅）",
                _CS_BASIS, f"{live[0][1]}:1", kind="cs_multi_live",
            ))
    return out


def check_all(repo=None) -> list:
    return check_cs_selfversion(repo) + check_revision_active(repo) + check_cs_content_currency(repo)


# ── 自測（合成樹；純函式餵真輸入、下游絆線、禁字面斷言——CLAUDE #35）────────────
def _write(root: pathlib.Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _cs_body(title_ver, spec_ver, archive_name) -> str:
    return (f"# Constitutional Compliance Statement — 測試檔 {title_ver}\n\n"
            "```\ncompliance-statement:\n  spec: Test\n"
            f"  spec-version: {spec_ver}\n  layer: 7\n"
            f"  archive-path: docs/compliance/{archive_name}\n```\n")


def _rev_body(rows) -> str:
    head = ("# 測試憲章 v9.9.9\n\n## 修訂歷程\n\n| 版本 | 日期 | 修訂說明 | 狀態 |\n"
            "|---|---|---|---|\n")
    return head + "".join(f"| {v} | 2026-01-01 | 說明 | {s} |\n" for v, s in rows)


def run_checks() -> list:
    """跑全部合成樹紅綠自測；回**失敗項名稱清單**（空＝全綠）。

    與 `_selftest()` 分家之理由：`selftest.py`（套件級自檢）須把本模組之紅綠納入同一份
    records，而不得重抄一份斷言——同一組不變式若有兩份實作，二者分歧時無從判斷孰誤
    （#12 單一住所）。
    """
    import tempfile

    fails: list = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)

        # (甲) CS 四值一致 → 綠；任一站點漂 → 紅（逐站點各驗一次，確保四值都真的被讀）
        _write(root, "docs/compliance/CS-好_v1.2.0.md", _cs_body("v1.2.0", "v1.2.0", "CS-好_v1.2.0.md"))
        chk("四值一致應綠", not check_cs_selfversion(root))
        for name, body in [
            ("標題漂", _cs_body("v1.1.0", "v1.2.0", "CS-壞_v1.2.0.md")),
            ("spec-version 漂", _cs_body("v1.2.0", "v1.1.0", "CS-壞_v1.2.0.md")),
            ("archive-path 漂", _cs_body("v1.2.0", "v1.2.0", "CS-壞_v1.1.0.md")),
        ]:
            p = _write(root, "docs/compliance/CS-壞_v1.2.0.md", body)
            got = [f for f in check_cs_selfversion(root) if f.kind == "cs_selfversion_mismatch"]
            chk(f"{name}應被抓到", len(got) == 1)
            p.unlink()
        # 檔名漂（其餘三值一致）——檔名是四值中唯一不在內文者，易被漏讀
        p = _write(root, "docs/compliance/CS-壞_v9.9.9.md", _cs_body("v1.2.0", "v1.2.0", "CS-壞_v1.2.0.md"))
        chk("檔名漂應被抓到", len([f for f in check_cs_selfversion(root) if f.kind == "cs_selfversion_mismatch"]) == 1)
        p.unlink()

        # (乙) 兩段 vs 三段（v1.35 vs v1.35.0）不得誤紅
        _write(root, "docs/compliance/CS-兩段_v1.35.md", _cs_body("v1.35.0", "v1.35", "CS-兩段_v1.35.md"))
        chk("v1.35 與 v1.35.0 視為同版、不得誤紅", not check_cs_selfversion(root))

        # (丙) 檔名無版號者（CS-CLAUDE 型：只有 spec-version 帶版）不得誤紅
        _write(root, "docs/compliance/CS-無版.md",
               "# Constitutional Compliance Statement — 無版檔\n\n```\ncompliance-statement:\n"
               "  spec-version: v1.35\n  archive-path: docs/compliance/CS-無版.md\n```\n")
        chk("檔名無版號者不得誤紅", not check_cs_selfversion(root))
        # 日期型 spec-version（CS-datasets_zh 型）不得被當版本比對
        _write(root, "docs/compliance/CS-日期.md",
               "# Constitutional Compliance Statement — 日期檔\n\n```\ncompliance-statement:\n"
               "  spec-version: 2026-06-15\n  archive-path: docs/compliance/CS-日期.md\n```\n")
        chk("日期型 spec-version 不得被當版本", not check_cs_selfversion(root))

        # (丁) 檔名帶版號而站點缺宣告 → 紅
        _write(root, "docs/compliance/CS-缺_v1.2.0.md",
               "# Constitutional Compliance Statement — 缺宣告檔\n\n```\ncompliance-statement:\n"
               "  spec-version: v1.2.0\n  archive-path: docs/compliance/CS-缺_v1.2.0.md\n```\n")
        chk("檔名帶版號而標題缺宣告應被抓到",
            any(f.kind == "cs_selfversion_mismatch" for f in check_cs_selfversion(root)))
        (root / "docs/compliance/CS-缺_v1.2.0.md").unlink()

        # (戊) 修訂表：恰一列現行 → 綠（**四種寫法逐一驗**——只認一種正是本輪漏抓之因）
        # **每個「應綠」都配一條絆線**：同一 fixture 加一列即須轉紅。無絆線之綠說不出
        # 「綠是因為一致」還是「綠是因為整檔沒被讀」——首版即因後者假綠（見 is_frozen_banner）。
        for writing in ("**現行**", "**ACTIVE**", "現行", "ACTIVE"):
            _write(root, "docs/測試憲章_v9.9.9.md",
                   _rev_body([("v1.0.0", "SUPERSEDED"), ("v9.9.9", writing)]))
            got = check_revision_active(root)
            chk(f"單列現行寫作「{writing}」應綠（多列判定）",
                not [f for f in got if f.kind == "revision_multi_active"])
            chk(f"單列現行寫作「{writing}」須被認得（非 status_unknown）",
                not [f for f in got if f.kind == "revision_status_unknown"])
            chk(f"絆線：寫作「{writing}」之 fixture 確實被解析（列數 > 0）",
                len(revision_status_rows(root / "docs/測試憲章_v9.9.9.md")) == 2)
            _write(root, "docs/測試憲章_v9.9.9.md",
                   _rev_body([("v1.0.0", "SUPERSEDED"), ("v1.5.0", writing), ("v9.9.9", writing)]))
            chk(f"絆線：寫作「{writing}」加第二列即須轉紅",
                any(f.kind == "revision_multi_active" for f in check_revision_active(root)))

        # 兩列非 SUPERSEDED（一列 ACTIVE ＋ 一列 現行）→ 紅，且訊息載明列數
        _write(root, "docs/測試憲章_v9.9.9.md",
               _rev_body([("v1.0.0", "SUPERSEDED"), ("v1.1.0", "**ACTIVE**"), ("v9.9.9", "**現行**")]))
        got = [f for f in check_revision_active(root) if f.kind == "revision_multi_active"]
        chk("雙現行（ACTIVE＋現行 混寫）應被抓到", len(got) == 1)
        chk("雙現行訊息須載明實際列數與所在列",
            bool(got) and "2 列" in got[0].message and "v1.1.0" in got[0].message and "v9.9.9" in got[0].message)

        # 零列非 SUPERSEDED（全表 SUPERSEDED＝現行版不見了）亦須紅
        _write(root, "docs/測試憲章_v9.9.9.md",
               _rev_body([("v1.0.0", "SUPERSEDED"), ("v9.9.9", "SUPERSEDED")]))
        chk("零現行亦須被抓到",
            any(f.kind == "revision_multi_active" for f in check_revision_active(root)))

        # 第五種寫法不得被靜默吸收：既入 status_unknown，亦仍計入「非 SUPERSEDED」分母
        _write(root, "docs/測試憲章_v9.9.9.md",
               _rev_body([("v1.0.0", "現行"), ("v9.9.9", "生效中")]))
        got = check_revision_active(root)
        chk("認不出之狀態寫法須出 status_unknown",
            any(f.kind == "revision_status_unknown" for f in got))
        chk("認不出之狀態仍計入非 SUPERSEDED 分母（不得靜默消失）",
            any(f.kind == "revision_multi_active" for f in got))

        # SUPERSEDED 凍結史料檔除外（其表為當時快照，不受現行列數拘束）
        _write(root, "docs/測試憲章_v9.9.9.md",
               "# 測試憲章 v9.9.9\n\n> **SUPERSEDED**：已被後版取代。\n\n"
               + _rev_body([("v1.1.0", "**ACTIVE**"), ("v9.9.9", "**現行**")]).split("\n", 1)[1])
        chk("SUPERSEDED 凍結檔須除外", not check_revision_active(root))

        # (己) 內容涵蓋版本（SV-3）與同規格多份並存（SV-4）
        _write(root, "docs/compliance/CS-內容_v1.2.0.md",
               _cs_body("v1.2.0", "v1.2.0", "CS-內容_v1.2.0.md")
               + "\n* **本版增量**：v1.2.0 新增某節。\n")
        chk("增量涵蓋到本版 → 綠", not [f for f in check_cs_content_currency(root)
                                  if f.kind == "cs_content_stale"])
        _write(root, "docs/compliance/CS-內容_v1.2.0.md",
               _cs_body("v1.2.0", "v1.2.0", "CS-內容_v1.2.0.md")
               + "\n* **本版增量**：v1.1.0 新增某節。\n")
        chk("增量落後檔名版 → 紅", any(f.kind == "cs_content_stale"
                                for f in check_cs_content_currency(root)))
        # **本則即 increment_version 首版之回歸鎖**：增量段必然引用其他治權檔之版號
        # （此處模擬「承大憲章 v9.9.9」），若改回「取該行最高版本」，此處會判成未落後而漏報。
        _write(root, "docs/compliance/CS-內容_v1.2.0.md",
               _cs_body("v1.2.0", "v1.2.0", "CS-內容_v1.2.0.md")
               + "\n* **本版增量（v1.1.0；承大憲章 v9.9.9 之總則）**：新增某節。\n")
        chk("增量段引用他檔更高版號時仍須報紅（不得取全行最大）",
            any(f.kind == "cs_content_stale" for f in check_cs_content_currency(root)))
        chk("增量段之抽取須取『本版增量』後第一個版本",
            increment_version(root / "docs/compliance/CS-內容_v1.2.0.md") == "1.1.0")
        # 無增量段者不在本款射程（節次完備性屬 compliance_lint 之 WM.41，不重複實作）
        _write(root, "docs/compliance/CS-無增量_v1.2.0.md",
               _cs_body("v1.2.0", "v1.2.0", "CS-無增量_v1.2.0.md"))
        chk("無增量段者不誤紅",
            not [f for f in check_cs_content_currency(root)
                 if f.kind == "cs_content_stale" and "無增量" in f.location])

        # SV-4：同 spec 兩份皆無橫幅 → 紅；其一掛 SUPERSEDED 橫幅 → 綠
        for rel in list((root / "docs/compliance").glob("CS-*.md")):
            rel.unlink()
        _write(root, "docs/compliance/CS-甲_v1.1.0.md", _cs_body("v1.1.0", "v1.1.0", "CS-甲_v1.1.0.md"))
        _write(root, "docs/compliance/CS-甲_v1.2.0.md", _cs_body("v1.2.0", "v1.2.0", "CS-甲_v1.2.0.md"))
        chk("同規格兩份皆未凍結 → 紅",
            any(f.kind == "cs_multi_live" for f in check_cs_content_currency(root)))
        _write(root, "docs/compliance/CS-甲_v1.1.0.md",
               "# Constitutional Compliance Statement — 甲 v1.1.0\n\n"
               "> **SUPERSEDED**：已被 v1.2.0 取代。\n\n"
               "```\ncompliance-statement:\n  spec-version: v1.1.0\n"
               "  archive-path: docs/compliance/CS-甲_v1.1.0.md\n```\n\n## 節\n")
        chk("舊版掛 SUPERSEDED 橫幅後 → 綠",
            not [f for f in check_cs_content_currency(root) if f.kind == "cs_multi_live"])
        # 絆線：綠是因為凍結、不是因為檔案沒被讀到
        chk("絆線：綠態下兩份檔案確實都還在",
            len(list((root / "docs/compliance").glob("CS-甲_*.md"))) == 2)

    # 真實 repo 之結構性斷言（**非字面計數**——計數會隨 Steward 修正而變，寫死即自製假綠）
    if (_REPO / "docs" / "compliance").is_dir():
        rows = []
        for p in sorted((_REPO / "docs").glob("*.md")):
            rows += revision_status_rows(p)
        chk("真實 repo 之修訂表解析得出列（解析器對真語料未失效）", len(rows) > 0)
        chk("每列狀態欄皆非空（欄位錯位偵測）", all(r["status"] for r in rows))
        cs = list((_REPO / "docs" / "compliance").glob("CS-*.md"))
        chk("真實 CS 檔至少一份可解析出 spec-version",
            any(cs_versions(p)["spec-version"] for p in cs))

    return fails


def _selftest() -> int:
    fails = run_checks()
    for f in fails:
        print(f"  ✗FAIL {f}")
    print("selfversion_lint selftest:" + (" OK" if not fails else f" FAIL（{len(fails)} 項）"))
    return 0 if not fails else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    fs = check_all()
    print(f"── 對真實 repo 唯讀實掃：{len(fs)} 則")
    for f in fs:
        print(f.format())
    sys.exit(1 if fs else 0)
