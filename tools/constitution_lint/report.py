"""report — 全 corpus 權威數字之**單一產生點**（machine-readable ＋ human-readable）。

存在理由（根治，非修補）：本專案已四度實證同一病灶——**文件裡的數字與程式分家**。歷次
腐爛皆非因人不用心，而是因為**數字由人手抄進文件**：39→93→151 三度上修、「MC 側 78／
上層側 34」係人工估算、「selftest 55 項」把結語橫幅算成一項測試、「136 列」是對錯誤母集
下 grep、「7 份/200」之產生指令實際得 13 份/352。手抄一日不除，下一輪必再腐爛。

本模組之職責因此**不是報表美觀**，而是：
  (a) 把「受檢 corpus 之定義」寫進**程式**（`corpus_files`），而非寫在文件裡任人重述；
  (b) 把每個曾經腐爛過的數字都變成**可由此處導出之 key**（`build()["values"]`）；
  (c) 供 `selftest` 之綁定斷言比對 [I] 文件中之標記數字（`--sync` 則反向寫回）。

**與 compliance 之自我一致性**：本模組不自行實作任何判準，逐檔數字一律取自
`compliance_lint.lint_spec`——與 `python -m tools.constitution_lint compliance <file>` 為同一
函式、同一參數。selftest 另有斷言逐檔複驗二者相等（見 `selftest._binding_and_consistency`）。
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess

from . import compliance_lint, mc_clauses

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
_MC = _REPO / "constitution" / "META-CONSTITUTION.md"

GEN_COMMAND = "python3 -m tools.constitution_lint report"

# ── 受檢 corpus 之定義（**權威定義在此，不在文件**）────────────────────────────────────
#
#   受檢 corpus ＝ 各層生效本（檔名無 `-v0.1-draft`）＋尚無生效本之 draft（2026-07-18 L7 充任後＝七份生效本、零 draft）。
#   歸檔本除外：`X-v0.1-draft.md` 於 `X.md`（其生效本）存在時即為**歸檔本**，不受檢。
#
# 此定義以「生效本是否存在」判斷歸檔與否，**非**以檔名白名單或層號硬編碼——L7 之 draft
# 受檢並非因為它叫 INFRASTRUCTURE，而是因為它尚無生效本（充任受阻）。L7 生效之日，
# `INFRASTRUCTURE-SPECIFICATION.md` 出現，其 draft 自動轉為歸檔本而退出 corpus，本函式
# 無須修改。
#
# **不得以 `specs/*.md` glob 代之**：該 glob 得 13 份／352 error（含 6 份歸檔 draft），
# 曾被寫進 github-workflow.yml 之產生指令而與其下表之七份/200 不符。
_ARCHIVE_SUFFIX = "-v0.1-draft.md"


def corpus_files(specs_dir=None) -> list:
    """回受檢 corpus 之檔案清單（排序後）。定義見本模組上方註解。"""
    d = pathlib.Path(specs_dir) if specs_dir else (_REPO / "specs")
    out = []
    for p in sorted(d.glob("*.md")):
        if p.name.endswith(_ARCHIVE_SUFFIX):
            effective = p.with_name(p.name[: -len(_ARCHIVE_SUFFIX)] + ".md")
            if effective.exists():
                continue          # 歸檔本：其生效本在場 → 除外
        out.append(p)
    return out


_LAYER_RE = re.compile(r"[（(]Layer\s+(\d)\s*[—–-]")


def spec_layer(path) -> str:
    """自規格**檔案自身**之標題行取層號（`…規格（Layer 6 — Agent Runtime…`）。

    不硬編碼「檔名→層」對照表：規格改名時對照表會靜默失準，而標題行是規格自述。
    """
    try:
        head = pathlib.Path(path).read_text(encoding="utf-8").splitlines()[:8]
    except OSError:
        return "L?"
    for ln in head:
        m = _LAYER_RE.search(ln)
        if m:
            return "L" + m.group(1)
    return "L?"


# ── Annex TR 之**資料列數**（與「比對筆數」為不同量，勿混用）─────────────────────────
#
#   存在理由：「L2 之 56 列矩陣從未受檢」為 #22 之核心事實，而該 **56** 於本輪之前散居
#   `HANDOFF.md`（4 處）、`CONSTITUTIONAL-ROLLOUT-PLAN.md`、`audits/REMEDIATION-ROADMAP.md`
#   **手抄七處**，且其產生指令為「兩條 sed 各數一段、人腦相加、再各自扣表頭」——正是本輪
#   所要撲滅之手抄型態（同一數字抄七次，ONT 一改即七處同時腐爛，而無任何一處會報錯）。
#
#   **本函式不另立「什麼是 Annex TR」之判準**：起始錨直接取
#   `compliance_lint._find_annex_tr_head`（二錨共用之單一判準，受 selftest G7 諸鎖拘束）。
#   若另寫一套錨點，則「report 說有 56 列」與「gate 說看不到」將源於兩套判準，二者分歧時
#   無從判斷孰誤——此即本專案「二法同源則同錯／二法異源則無從對質」之教訓。
#
#   **本量與 `compared_*` 之關係即 L2 缺口之量化**：`tr_rows_L2` > 0 而 `compared_L2` ＝ 0
#   ⇔「矩陣在場、gate 一列未讀」。selftest 對此二值之並存有結構性斷言（非寫死 56）。
_TBL_SEP = re.compile(r"^\|[\s:|-]*\|[\s:|-]*$")
_HEAD_LVL = re.compile(r"^(#{1,6})\s+\S")


def annex_tr_rows(path) -> int:
    """回該規格 Annex TR 區段之**資料列數**（扣除各表之表頭列與分隔列）；無區段回 0。

    區段自 `_find_annex_tr_head` 所認之標題起，至**同級或更高級**之次一標題止——故 ONT 之
    `# Annex TR`（h1）涵蓋其下 `## TR.1`／`## TR.2` 二子表，至 `# Annex CS`（h1）止。
    **不以硬編之 `^## ` 為界**：那正是 gate 讀不到 ONT 矩陣之病灶本身（見 `_annex_tr_regions`）。
    """
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except OSError:
        return -1
    head = compliance_lint._find_annex_tr_head(text)
    if head is None:
        return 0
    lines = text.splitlines()
    start = text.count("\n", 0, head.start())
    lvl = len(_HEAD_LVL.match(lines[start]).group(1))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = _HEAD_LVL.match(lines[j])
        if m and len(m.group(1)) <= lvl:
            end = j
            break
    n = 0
    for ln in lines[start:end]:
        if not ln.startswith("|"):
            continue
        if _TBL_SEP.match(ln):
            n -= 1          # 分隔列本身不計，且其緊鄰之前一列為表頭、亦不計
            continue
        n += 1
    return max(n, 0)


def _side(finding) -> str:
    """依 `clause["source"]` 三分：MC 側／上層側／**未歸類**。

    未歸類**獨立成類**、不得併入任一側：其 finding 發生於 clause 解析之前（如 ONT 之
    Annex TR 零覆蓋發聲），本無 source 可歸。寫成「MC 110／上層 90」即為捏造。
    """
    src = getattr(finding, "source", "") or ""
    if src == "MC":
        return "mc"
    if src.startswith("AUGUR-"):
        return "upper"
    return "unclassified"


def git_head() -> str:
    """回 `<sha>` 或 `<sha>+dirty`／`(unknown)`。

    **dirty 標記為必要而非裝飾**：工作區有未提交變更時，單一 SHA 會使轉貼者以為該輸出
    可由該 commit 重現——這正是「HANDOFF 記 HEAD＝4951aee 卻已漂移」之同型錯誤。
    """
    def _git(*args):
        return subprocess.run(["git", "-C", str(_REPO), *args],
                              capture_output=True, text=True, timeout=30)
    try:
        r = _git("rev-parse", "HEAD")
        if r.returncode != 0:
            return "(unknown)"
        sha = r.stdout.strip()
        st = _git("status", "--porcelain")
        dirty = bool(st.returncode == 0 and st.stdout.strip())
        return sha + ("+dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return "(unknown)"


# ── [I] 文件之權威數字綁定標記 ──────────────────────────────────────────────────────
#
#   標記形式（md 與 yml 一律同形；yml 中置於 `#` 註解內，YAML 合法）：
#       <!--lint:KEY-->VALUE<!--/lint-->
#
# 掃描範圍限下列 [I] 文件。生效規格（`specs/*-SPECIFICATION.md` 無 -draft）**不在其列**且
# 永不得列入：動之即 §8.5／§8.6 修憲行為，屬 Steward 事項，工具無權代改。
BOUND_DOCS = [
    "HANDOFF.md",
    "README.md",
    "tools/constitution_lint/README.md",
    "tools/constitution_lint/github-workflow.yml",
    # 2026-07-17 四輪增列：此二檔各自手抄權威數字而**完全不在綁定之列**——普查表因此
    # 對其一無所知（其「0 處」不會出現，因為它們根本不被掃描）。ROLLOUT-PLAN §2.1 與
    # ROADMAP 之阻塞節皆載「L2 之 56 列矩陣」，與 HANDOFF 四處為**同一數字之第五、六份
    # 手抄副本**——「假話有兩份副本而只修了一份」之同型風險，於此為六份。
    "CONSTITUTIONAL-ROLLOUT-PLAN.md",
    "audits/REMEDIATION-ROADMAP.md",
    # L7 充任裁決**草案**（`不生效力`）：其「L2 之 56 列」為同一數字之第七份手抄副本。
    # **僅該現況數字受綁定**；該檔之 gate 歷史值表（`@468563c` 93／`@65a7dd6` 151）**一律
    # 不綁定**——歷史值繫於其所錨之 SHA，綁定即令其隨程式漂移而仍自稱是該 SHA 之值。
    # 生效裁決（`constitution/RULING-*.md`）永不列入：其為 Steward 已署之文書。
    "constitution/adoption-drafts/RULING-2026-008-L7-ADOPTION-DRAFT.md",
]

MARKER_RE = re.compile(r"<!--lint:([a-zA-Z0-9_]+)-->(.*?)<!--/lint-->", re.S)


def collect_markers(repo=None) -> list:
    """掃描 `BOUND_DOCS`，回 [{"file","line","key","value"}]。"""
    root = pathlib.Path(repo) if repo else _REPO
    out = []
    for rel in BOUND_DOCS:
        p = root / rel
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in MARKER_RE.finditer(text):
            out.append({"file": rel, "line": text.count("\n", 0, m.start()) + 1,
                        "key": m.group(1), "value": m.group(2)})
    return out


def build(selftest=None, specs_dir=None, mc_path=None) -> dict:
    """產生全 corpus 之權威數字。

    `selftest`＝{"top_items":int,"assertions":int}。**None 時本函式自行跑 selftest 取實測值**
    （lazy import：selftest 反過來要用本模組作綁定比對，模組層 import 會成環）。
    """
    mc = str(mc_path or _MC)
    files = corpus_files(specs_dir)
    v = {}
    per_file = []

    tot = {"error": 0, "warning": 0, "info": 0, "label_error": 0,
           "mc": 0, "upper": 0, "unclassified": 0,
           "compared": 0, "compared_mc": 0, "compared_upper": 0}
    kinds = {}
    l36 = {"error": 0, "mc": 0, "upper": 0}
    # 跨規格「逐字複製誤標」之統計母體：{(code, label): {layer, …}}。
    # **以 finding 之結構化 code／label 欄為據**，非以 grep 訊息反推——README 該節自陳
    # 「以程式導出，非手數」，惟前版實為手數且錯（記「30 組」，實為 31；其自身表格三列
    # 相加 7+3+21 即得 31，連內部一致性都未檢）。此為該病第三度復發，故改由此處導出。
    dup_seen = {}

    for p in files:
        r = compliance_lint.lint_spec(str(p), mc)
        layer = spec_layer(p)
        errs = r.errors
        n_e, n_w = len(errs), len(r.warnings)
        n_i = len(r.findings) - n_e - n_w
        sides = {"mc": 0, "upper": 0, "unclassified": 0}
        for f in errs:
            sides[_side(f)] += 1
            kinds[f.kind or "«untagged»"] = kinds.get(f.kind or "«untagged»", 0) + 1
        cmp_raw = r.meta.get("label_compared") or {}
        c_mc = cmp_raw.get("MC", 0)
        c_up = sum(n for k, n in cmp_raw.items() if k.startswith("AUGUR-"))

        rec = {"layer": layer, "file": str(p.relative_to(_REPO)),
               "is_draft": p.name.endswith(_ARCHIVE_SUFFIX),
               "error": n_e, "warning": n_w, "info": n_i,
               "label_error": sum(1 for f in errs if f.rule == "WM.44-LABEL"),
               "error_mc": sides["mc"], "error_upper": sides["upper"],
               "error_unclassified": sides["unclassified"],
               "compared_mc": c_mc, "compared_upper": c_up, "compared": c_mc + c_up,
               "compared_by_source": dict(sorted(cmp_raw.items())),
               "wm40_extension": sum(1 for f in errs if f.kind == "wm40_extension"),
               "wm44_uncited": r.meta.get("wm44_uncited", -1),
               "wm44_universe": r.meta.get("wm44_universe", -1),
               "tr_rows": annex_tr_rows(p),
               "passed": r.passed}
        per_file.append(rec)

        tot["error"] += n_e; tot["warning"] += n_w; tot["info"] += n_i
        tot["label_error"] += rec["label_error"]
        for k in ("mc", "upper", "unclassified"):
            tot[k] += sides[k]
        tot["compared"] += rec["compared"]; tot["compared_mc"] += c_mc
        tot["compared_upper"] += c_up
        if layer in ("L3", "L4", "L5", "L6") and not rec["is_draft"]:
            l36["error"] += n_e; l36["mc"] += sides["mc"]; l36["upper"] += sides["upper"]
            for f in errs:
                if f.code and f.label:
                    dup_seen.setdefault((f.code, f.label), set()).add(layer)

        v[f"errors_{layer}"] = n_e
        v[f"errors_mc_{layer}"] = sides["mc"]
        v[f"errors_upper_{layer}"] = sides["upper"]
        v[f"warnings_{layer}"] = n_w
        v[f"compared_{layer}"] = rec["compared"]
        v[f"compared_mc_{layer}"] = c_mc
        v[f"compared_upper_{layer}"] = c_up
        v[f"wm44_uncited_{layer}"] = rec["wm44_uncited"]
        v[f"wm40_extension_{layer}"] = rec["wm40_extension"]
        v[f"tr_rows_{layer}"] = rec["tr_rows"]

    v["corpus_total"] = len(files)
    v["corpus_effective"] = sum(1 for r in per_file if not r["is_draft"])
    v["corpus_draft"] = sum(1 for r in per_file if r["is_draft"])
    v["corpus_pass"] = sum(1 for r in per_file if r["passed"])
    v["corpus_fail"] = sum(1 for r in per_file if not r["passed"])
    # **生效本之 FAIL 份數**：github-workflow.yml 橫幅「其中五份為已生效規格」之權威來源。
    # 與 `corpus_fail`（含 L7 draft）為不同量——draft 之紅不阻斷任何已生效規格之地位，
    # 混用即把「五份生效規格是紅的」誇大為六份。
    v["corpus_fail_effective"] = sum(1 for r in per_file
                                     if not r["passed"] and not r["is_draft"])
    v["total_errors"] = tot["error"]
    v["total_warnings"] = tot["warning"]
    v["label_errors"] = tot["label_error"]
    v["non_label_errors"] = tot["error"] - tot["label_error"]
    v["label_errors_mc"] = tot["mc"]
    v["label_errors_upper"] = tot["upper"]
    v["label_errors_unclassified"] = tot["unclassified"]
    v["compared_total"] = tot["compared"]
    v["compared_mc"] = tot["compared_mc"]
    v["compared_upper"] = tot["compared_upper"]
    v["l3_l6_errors"] = l36["error"]
    v["l3_l6_mc"] = l36["mc"]
    v["l3_l6_upper"] = l36["upper"]
    v["l3_l6_specs"] = sum(1 for r in per_file
                           if r["layer"] in ("L3", "L4", "L5", "L6") and not r["is_draft"])

    # ── 跨層「逐字複製誤標」（README「病灶為跨層系統性」節之權威來源）────────────────
    dup_dist = {}
    dup_groups = []
    for (code, label), layers in sorted(dup_seen.items()):
        if len(layers) < 2:
            continue
        dup_dist[len(layers)] = dup_dist.get(len(layers), 0) + 1
        dup_groups.append({"code": code, "label": label, "n": len(layers),
                           "layers": sorted(layers)})
    v["dup_mislabels"] = sum(dup_dist.values())        # ≥2 份者之組數
    for n in (2, 3, 4):
        v[f"dup_mislabels_in_{n}"] = dup_dist.get(n, 0)
    dup_groups.sort(key=lambda g: (-g["n"], g["code"]))
    for k, n in kinds.items():
        v[f"kind_{k}"] = n
    # kind keys 穩定化：已知分型即使計 0 亦輸出（否則歸零後 key 消失 → 綁定文件成孤兒標記）
    for k in ("verbatim", "halved_name", "leading_truncation", "paren_mismatch",
              "no_text_support", "tr_absent", "tr_asserted_absent", "tr_zero_coverage",
              "code_not_in_universe", "upper_spec_undeclared", "upper_spec_unresolved",
              "status_draft_claims_effective", "status_effective_claims_draft"):
        v.setdefault(f"kind_{k}", 0)
    try:
        v["mc_universe"] = len(mc_clauses.load(mc)[0])
    except OSError:
        v["mc_universe"] = -1
    # WM.40 閉集欄數：**動態解析自 WM 原文**。文件得綁定此值（＝由程式導出），此與
    # 「於 linter 內硬編碼 `len(...)==14`」截然不同——後者係把判準來源從 Layer 1 搬進工具
    # （B8 明文拒絕之事）；前者只是把 WM 現況照實報出。WM 合法增欄時本值自動隨之。
    fields_now, src_now = compliance_lint._wm40_closed_set()
    v["wm40_fields"] = len(fields_now)
    v["wm40_closed_set_source"] = src_now

    if selftest is None:
        from . import selftest as _st        # lazy：避免與 selftest 之模組層互相 import
        _ok, records = _st.run(quiet=True)
        selftest = coverage_of(records)
    v["selftest_top_items"] = selftest["top_items"]
    v["selftest_assertions"] = selftest["assertions"]

    # 綁定普查：逐 [I] 文件之標記數。**此為透明度措施，非防線**——selftest 攔得住「標記值
    # 漂移」，攔不住「把標記整個刪掉、改回寫死數字」（見 render 之告示）。故將各檔標記數
    # 明列，俾審查者一眼看出某檔之綁定是否被拆除。
    census = {}
    for m in collect_markers():
        census[m["file"]] = census.get(m["file"], 0) + 1
    v["bound_markers_total"] = sum(census.values())

    return {"values": v, "per_file": per_file, "corpus": [str(p) for p in files],
            "kinds": kinds, "marker_census": census, "bound_docs": BOUND_DOCS,
            "dup_mislabels": dup_groups,
            "git_head": git_head(), "command": GEN_COMMAND}


def coverage_of(records) -> dict:
    """selftest 覆蓋數之**唯一計法**（限定詞隨數字同行輸出，見 `render`）。

    `records`＝[(name, passed)]。頂層測項＝名稱非以 `  └` 起首者；斷言總數＝全部 chk 呼叫數。
    **不得輸出無限定詞之「N 項」**：前版之「55 項」即 `grep -c '✓'`（未限行首）之產物，
    把結語行「自檢：全通過 ✓」算成一項通過的測試——一個宣告「全部測試通過」的句子被計為
    一個通過的測試。
    """
    return {"top_items": sum(1 for n, _ in records if not n.startswith("  └")),
            "assertions": len(records)}


_L_ORDER = {f"L{i}": i for i in range(1, 9)}


def render(data: dict) -> str:
    """人可讀輸出；末尾附產生指令與 git HEAD SHA，使任何轉貼可被追溯。"""
    v, L = data["values"], []
    L.append("═══ constitution_lint report — 全 corpus 權威數字 ═══")
    L.append("")
    L.append("【受檢 corpus 之定義】（權威定義寫在程式：`tools/constitution_lint/report.py::corpus_files`）")
    L.append(f"  corpus ＝ 各層生效本（檔名無 `-v0.1-draft`）＋尚無生效本之 draft（有則入檢）")
    L.append(f"  歸檔本除外：`X-v0.1-draft.md` 於其生效本 `X.md` 在場時即為歸檔本，不受檢。")
    L.append(f"  ⚠ 不得以 `specs/*.md` glob 代之——該 glob 含 6 份歸檔 draft，得 13 份而非本表之 "
             f"{v['corpus_total']} 份。")
    L.append(f"  實得：{v['corpus_total']} 份（生效本 {v['corpus_effective']}／draft {v['corpus_draft']}）"
             f"；PASS {v['corpus_pass']}／FAIL {v['corpus_fail']}")
    for r in sorted(data["per_file"], key=lambda r: _L_ORDER.get(r["layer"], 99)):
        L.append(f"    - {r['layer']:3} {r['file']}")
    L.append("")
    L.append("【逐檔】（error／warning／info；WM.44-LABEL error 之 MC 側／上層側／未歸類三分）")
    L.append("  | 層 | 規格 | error | warning | info | LABEL error | MC 側 | 上層側 | 未歸類 | WM.44 覆蓋缺口 | 判定 |")
    L.append("  |---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(data["per_file"], key=lambda r: _L_ORDER.get(r["layer"], 99)):
        name = pathlib.Path(r["file"]).name[:-3].replace("-SPECIFICATION", "")
        if r["is_draft"]:
            name = name.replace("-v0.1-draft", "") + "（draft）"
        L.append(f"  | {r['layer']} | {name} | {r['error']} | {r['warning']} | {r['info']} |"
                 f" {r['label_error']} | {r['error_mc']} | {r['error_upper']} |"
                 f" {r['error_unclassified']} | {r['wm44_uncited']}/{r['wm44_universe']} |"
                 f" {'✅ PASS' if r['passed'] else '❌ FAIL'} |")
    L.append("")
    L.append("【逐檔比對筆數】（母集，非 error 數——二者為不同量，混用即製造假數字）")
    for r in sorted(data["per_file"], key=lambda r: _L_ORDER.get(r["layer"], 99)):
        by = "、".join(f"{k} {n}" for k, n in r["compared_by_source"].items()) or "（無：未偵得可解析之 Annex TR 區段）"
        L.append(f"  {r['layer']:3} 比對 {r['compared']:3} 筆（MC {r['compared_mc']}／上層 {r['compared_upper']}）：{by}")
    L.append("")
    L.append("【Annex TR 資料列數 vs 實際比對筆數】（**二者為不同量**；差距即「在場而未讀」之量化）")
    L.append("  | 層 | Annex TR 資料列 | 已比對筆數 | 缺口 |")
    L.append("  |---|---|---|---|")
    for r in sorted(data["per_file"], key=lambda r: _L_ORDER.get(r["layer"], 99)):
        gap = ("**矩陣在場、一列未讀**" if r["tr_rows"] > 0 and r["compared"] == 0
               else ("（確無 Annex TR）" if r["tr_rows"] == 0 else "已讀取"))
        L.append(f"  | {r['layer']} | {r['tr_rows']} | {r['compared']} | {gap} |")
    L.append("  ⚠ **列數 ≠ 比對筆數**：一列可載多個代號、亦可一個都不載，故二數本不相等，"
             "**不得相減充作「未受檢列數」**。")
    L.append("     本表只回答一個是非題：**該矩陣是否有列在場、而 gate 一列未讀**。")
    L.append("")
    L.append("【合計】")
    L.append(f"  七份總 error                 ： {v['total_errors']}"
             f"（其中 WM.44-LABEL {v['label_errors']}／非 LABEL {v['non_label_errors']}）")
    L.append(f"  四份生效規格（L3–L6）合計    ： {v['l3_l6_errors']}"
             f"（MC 側 {v['l3_l6_mc']}／上層側 {v['l3_l6_upper']}；受計規格 {v['l3_l6_specs']} 份，不含 L7 draft）")
    L.append(f"  error 三分（**須並列**）      ： MC 側 {v['label_errors_mc']}／上層側 {v['label_errors_upper']}"
             f"／**未歸類 {v['label_errors_unclassified']}**")
    L.append(f"     └ 未歸類獨立列出、不得併入任一側：其 finding 發生於 clause 解析之前，本無")
    L.append(f"       `source` 可歸。寫成「MC {v['label_errors_mc']}／上層 "
             f"{v['label_errors_upper'] + v['label_errors_unclassified']}」即為捏造。")
    L.append(f"  比對筆數合計                 ： {v['compared_total']}"
             f"（MC {v['compared_mc']}／上層 {v['compared_upper']}）— 與 error 數為不同量，勿混用")
    L.append(f"  憲章 [N] 條款宇宙（母集）    ： {v['mc_universe']} 條")
    L.append("")
    L.append("【error 分型】（取自 finding 之 `kind` 欄，於生成處指定；非以 grep 訊息反推）")
    for k, n in sorted(data["kinds"].items(), key=lambda kv: -kv[1]):
        L.append(f"  {k:24} {n}")
    L.append(f"  {'合計':24} {sum(data['kinds'].values())}")
    L.append("")
    L.append("【跨層逐字複製誤標】（四份生效規格 L3–L6 中，同一「代號＋標籤」對逐字重複且經判為誤標者）")
    L.append(f"  ≥2 份者          ： {v['dup_mislabels']} 組"
             f"（4 份 {v['dup_mislabels_in_4']}／3 份 {v['dup_mislabels_in_3']}／2 份 {v['dup_mislabels_in_2']}"
             f"——三者相加即 {v['dup_mislabels']}，selftest 另有斷言複驗）")
    L.append("  取自 finding 之 `code`／`label` 結構化欄位，**非以 grep 訊息反推**。")
    for g in data["dup_mislabels"][:12]:
        L.append(f"    {g['n']} 份 {'/'.join(g['layers']):17} `{g['code']}`（{g['label']}）")
    if len(data["dup_mislabels"]) > 12:
        L.append(f"    …另 {len(data['dup_mislabels']) - 12} 組（全部見 JSON 區塊 `dup_mislabels`）")
    L.append("")
    L.append("【selftest 覆蓋數】（**限定詞與數字同行，不得單寫「N 項」**）")
    L.append(f"  頂層測項 ： {v['selftest_top_items']} 項")
    L.append(f"  斷言總數 ： {v['selftest_assertions']} 項（含各頂層測項之 `└` 子斷言）")
    L.append(f"  → 引用時請寫「頂層 {v['selftest_top_items']} 項／斷言總數 "
             f"{v['selftest_assertions']} 項」，勿寫裸數字。")
    L.append("")
    L.append("【[I] 文件綁定普查】（標記數；selftest 逐處比對，不一致即 FAIL）")
    for rel in data["bound_docs"]:
        n = data["marker_census"].get(rel, 0)
        note = "" if n else "   ← 無標記（此檔若載有權威數字，即為未綁定之手抄，應改為「見 `report` 輸出」或加標記）"
        L.append(f"  {rel:44} {n:4} 處{note}")
    L.append(f"  {'合計':44} {data['values']['bound_markers_total']:4} 處")
    L.append("  ⚠ **已知邊界（據實揭露）**：本綁定攔得住「標記之值漂移」，**攔不住「把標記整個")
    L.append("     刪掉、改回寫死數字」**——刪光某檔之標記後 selftest 仍綠。上表即為此而列：")
    L.append("     審查時請比對各檔標記數是否無故下降。")
    L.append("")
    L.append("─── 機器可解析區塊（JSON）───")
    L.append(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2))
    L.append("─── 機器可解析區塊結束 ───")
    L.append("")
    L.append("═══ 產生資訊（轉貼此輸出時請連同本節一併轉貼，俾可追溯）═══")
    L.append(f"  產生指令 ： {data['command']}（於 repo 根執行）")
    L.append(f"  git HEAD ： {data['git_head']}")
    if data["git_head"].endswith("+dirty"):
        L.append("             ⚠ **+dirty：工作區有未提交變更，本輸出無法僅由該 SHA 重現。**")
    L.append(f"  綁定同步 ： {data['command']} --sync   # 將本表數字寫回 [I] 文件之 <!--lint:KEY--> 標記")
    L.append("  ⚠ 本輸出之數字**一律由程式導出**。請勿手抄至文件——手抄即本專案四度腐爛之根因。")
    L.append("     文件中之權威數字須以 `<!--lint:KEY-->…<!--/lint-->` 標記並由 `--sync` 寫入；")
    L.append("     無法綁定者，文件應書「見 `report` 輸出」，不得寫死。")
    return "\n".join(L)


def sync(data: dict, repo=None) -> list:
    """把 `data["values"]` 寫回 [I] 文件之標記。回 [(file, key, old, new)] 之變更清單。

    **這就是「把手拿掉」**：文件數字不再經由人手轉錄，而由本函式自 `build()` 之輸出寫入。
    僅改寫標記**之間**的值，標記本身與周邊散文一字不動——工具不得代改文件之主張，只負責
    其中之數字。
    """
    root = pathlib.Path(repo) if repo else _REPO
    v, changes = data["values"], []
    for rel in BOUND_DOCS:
        p = root / rel
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue

        def _sub(m):
            key, old = m.group(1), m.group(2)
            if key not in v:
                return m.group(0)                    # 孤兒 key：不動，交由 selftest 報 FAIL
            new = str(v[key])
            if new != old:
                changes.append((rel, key, old, new))
            return f"<!--lint:{key}-->{new}<!--/lint-->"

        new_text = MARKER_RE.sub(_sub, text)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
    return changes
