#!/usr/bin/env python3
"""🎯 WM.36 vendor 直綁止血閘——凍結「供應商表名字面繫結」存量，新增即紅，堵 07-17→08-02 淨增 +13 檔之出血。

守原則 #15（紅燈必須會亮：selftest＝fixture 紅綠雙向＋突變驗紅）、#9/#10（數字出自本掃描、可重跑溯源）、
#28（零 DB 零 API 零 usage，純本地靜態掃描）。
SSOT＝reports/wm3536_vendor_registry_plan_20260802.md §7（G0 格 6 已准先行止血 2026-08-02）；
條文錨＝specs/WORLD-MODEL-SPECIFICATION.md WM.36（消費禁令 2026-10-15 起無條件適用）。

## 口徑（plan §1 廣口徑，寬於 F2；凍在基線檔頭 caliber_sha256、regex 弱化即紅）

    quoted_table     : FROM 後接雙引號 CamelCase 表名（TaiwanStockPrice 家族＋US 家族）
    quoted_table_esc : 同上之跳脫引號變體（Python 雙引號字串內之 FROM 加反斜線引號 CamelCase）——
                       **plan §1 grep 之盲點、本支建置紅燈實測時揭露**（首次紅檢寫此形、閘竟綠）：
                       runtime SQL 與 quoted_table 全等、僅原始碼引號寫法不同；2026-08-02 親驗
                       存量 26 處/18 檔，其中 4 檔不在 plan §11 清單（以 UNCLASSIFIED 大聲呈報）
    fred_series      : FROM 後接 fred_series 字面

## 指紋（照 check_false_assertions 先例）

    相對路徑<TAB>表字面<TAB>承載形（**零行號**——行號隨編輯漂移會製造假新增）；處數另欄承載棘輪。

## 自我匹配防線（本專案五犯之型）

    (a) 自檔豁免：本支不掃自己（fixture 內含 vendor SQL 樣本，掃到即假紅）；
    (b) 整行註解排除（同 check_false_assertions 先例）；
    (c) fixture/常數以運行期串接組出字面——本檔原始碼不含連續直綁字面，repo 級 grep 口徑不受污染。

執行指令矩陣
------------
    python3 scripts/check_vendor_binding.py                   # 無參數＝--scan（唯讀分類報表；有 UNCLASSIFIED 則 exit 1）
    python3 scripts/check_vendor_binding.py --scan            # A/B/C/D 歸類照 plan §11；清單外新檔=UNCLASSIFIED 大聲
    python3 scripts/check_vendor_binding.py --gate            # pre-commit 閘：新增檔/新表/增處=exit 1；已清償僅列印不自動刪
    python3 scripts/check_vendor_binding.py --write-baseline  # 以現況重寫基線（顯式旗標＋列印 diff；過目後 commit）
    python3 scripts/check_vendor_binding.py --selftest        # 紅綠自測（fixture 驅動＋突變驗紅；免 DB 免 API）
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.audit import scan_floor

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SCAN_DIRS = ("src", "scripts")               # plan §1 口徑之掃描範圍
BASELINE = ROOT / "ops" / "vendor_binding_baseline.txt"

# ── 對象數地板（M-G2）：本閘之假綠最兇——實讀 0 檔時 found={}，130 條基線全部「已清償」，
# 而 new/inc 皆空 ⇒ 舊實作印 ✓ 並回 rc=0。「出血全清了」與「根本沒掃」同形。
# 現況實測 2026-08-03：實讀 446→447 檔（scripts 328+／src 119，SELF 自檔豁免 −1；當日並行
# 工單仍在增檔，故為區間非定值）。地板取 300。
MIN_FILES = 300
GROUP_ROOTS = ("src", "scripts")
# 錨取**結構性長壽檔**（`_bootstrap` 是本器能啟動之前提、`augur/__init__` 自 v1.0 起點即在）：
# 本器對自己有豁免，故不能自錨；拿新檔當錨則舊 worktree 上跑會假紅。
ANCHORS = ("scripts/_bootstrap.py", "src/augur/__init__.py")

# 字元類含數字（2026-08-03 補：原 [A-Za-z]+ 漏掉含數字之表名——TaiwanStock10Year 之 2 處
# 直綁自本閘上崗起從未進口徑＝既有假綠。由 22 表登錄草案 agent 親驗抓出）
_QUOTED = re.compile(r'FROM\s+"([A-Z][A-Za-z0-9_]+)"')
_QUOTED_ESC = re.compile(r'FROM\s+\\"([A-Z][A-Za-z0-9_]+)\\"')
_FRED = re.compile(r"FROM\s+(fred_series)")


def _caliber_sha() -> str:
    """口徑指紋：regex 本體之 hash。弱化/竄改口徑 ⇒ 與基線檔頭不符 ⇒ 紅。純函式。"""
    return hashlib.sha256(
        f"{_QUOTED.pattern}\n{_QUOTED_ESC.pattern}\n{_FRED.pattern}".encode()).hexdigest()[:16]


# plan §11 逐檔分類（52 檔；lint 工件非資料 SSOT——#29(b) 豁免款：安全繫於機械閘之詞表屬邏輯側）
_A = [
    "src/augur/features/chip.py", "src/augur/features/fundamentals.py",
    "src/augur/features/margin_cycle.py", "src/augur/features/panel.py",
    "src/augur/features/phase.py", "src/augur/features/valuation.py",
    "src/augur/features/macro_vintage.py", "src/augur/advisor/payload.py",
    "src/augur/arena/adapters.py",
    "scripts/build_daily_direction_features.py", "scripts/build_direction_stack_monthly.py",
    "scripts/build_feature_panel.py", "scripts/build_interaction_candidates.py",
    "scripts/build_market_direction_features.py", "scripts/build_pme_fundamental_features.py",
    "scripts/train_daily_direction.py", "scripts/train_direction_stack.py",
    "scripts/train_direction_threelens.py", "scripts/produce_direction_probability.py",
    "scripts/derive_market_iv.py", "scripts/run_arena_daily_pipeline.py",
    "scripts/run_arena_replay.py", "scripts/run_arena_round.py",
    "scripts/settle_arena_labels.py", "scripts/simulate_mc_paths.py",
    "scripts/simulate_portfolio_risk.py", "scripts/settle_sim_outcomes.py",
    "scripts/evaluate_sim_calibration.py", "scripts/run_sim_calibration_cell.py",
]
_B = [
    "scripts/verify_candidate_promotion.py", "scripts/verify_daytrade_candidates.py",
    "scripts/verify_economic_candidate.py", "scripts/verify_fundamental_candidates.py",
    "scripts/verify_incremental_fair.py", "scripts/verify_interaction_promotion.py",
    "scripts/verify_regime_portfolio.py", "scripts/verify_regime_timing.py",
    "scripts/verify_signal_promotion.py", "scripts/run_cross_table_interaction_scan.py",
    "scripts/run_deep_interaction_scan.py", "scripts/run_raw_interaction_ic.py",
    "src/augur/audit/feature_candidate.py", "src/augur/audit/field_correlation.py",
    "scripts/benchmark_tsfm_taiwan.py",
]
_C = ["scripts/full_universe_attest.py", "scripts/verify_units.py", "scripts/reconcile_audit.py"]
_D = [
    "scripts/backfill_entity_registry.py", "scripts/backfill_lifecycle_retire.py",
    "scripts/sync_attribute_versions.py", "scripts/repair_priceadj_basis.py",
    "src/augur/catalog/__init__.py",
]
CLASSIFICATION = {p: c for c, files in (("A", _A), ("B", _B), ("C", _C), ("D", _D)) for p in files}
_CLASS_LABEL = {"A": "A 生產消費鏈", "B": "B 候選驗證/研究掃描",
                "C": "C 對帳/attestation", "D": "D 觀測層維運"}


def analyse(text: str):
    """回 [(lineno, 表字面, 承載形)]。純函式——fixture 可驗紅綠雙向。

    整行註解排除（check_false_assertions 先例）：說明「舊寫法長怎樣」之註解非直綁。
    """
    out = []
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith("#"):
            continue
        for m in _QUOTED.finditer(ln):
            out.append((i, m.group(1), "quoted_table"))
        for m in _QUOTED_ESC.finditer(ln):
            out.append((i, m.group(1), "quoted_table_esc"))
        for m in _FRED.finditer(ln):
            out.append((i, m.group(1), "fred_series"))
    return out


def fingerprint(rel: str, table: str, form: str) -> str:
    """基線指紋——零行號（行號隨編輯漂移會製造假新增）。純函式。"""
    return f"{rel}\t{table}\t{form}"


def _collect(paths):
    """→ ({指紋: 處數}, 實讀相對路徑集)。自檔豁免：本支 fixture 含 vendor SQL 樣本，掃到自己即假紅。

    實讀集是地板判準（M-G2）之唯一素材——**零命中**與**零對象**必須分得開。
    """
    counts: dict[str, int] = {}
    read: set[str] = set()
    for p in paths:
        if p.resolve() == SELF:
            continue
        try:
            res = analyse(p.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(p.relative_to(ROOT))
        read.add(rel)
        for _ln, table, form in res:
            fp = fingerprint(rel, table, form)
            counts[fp] = counts.get(fp, 0) + 1
    return counts, read


def floor_checks(read_rels):
    """實讀相對路徑集 → 地板宣告列（純函式；餵 `_collect` 之真輸出，#35(1)）。"""
    per_root = {r: sum(1 for p in read_rels if p.split("/")[0] == r) for r in GROUP_ROOTS}
    return ([scan_floor.FloorCheck("實讀 .py 檔總數", len(read_rels), MIN_FILES)]
            + scan_floor.group_checks(per_root, prefix="掃描根")
            + scan_floor.anchor_checks(read_rels, ANCHORS))


def gate_verdicts(found: dict, base: dict):
    """(現況 {指紋:數}, 基線 {指紋:數}) → (新增, 增處, 已清償)。純函式——fixture 可驗紅綠雙向。

    · 新增（found−base 之指紋）／增處（同指紋數上升）⇒ 擋 commit：出血不得入庫。
    · 已清償（基線指紋消失或數下降）⇒ 只列印「可自基線移除/收緊」——**不自動改基線**：
      自動縮才是單向棘輪；自動擴＝閘自己放行自己（check_false_assertions 同旨）。
    """
    new = sorted(fp for fp in found if fp not in base)
    inc = sorted(f"{fp}\t{base[fp]}→{found[fp]}" for fp in found
                 if fp in base and found[fp] > base[fp])
    cleared = sorted([fp for fp in base if fp not in found]
                     + [f"{fp}\t{base[fp]}→{found[fp]}" for fp in found
                        if fp in base and found[fp] < base[fp]])
    return new, inc, cleared


def parse_baseline(text: str):
    """基線檔 → (caliber_sha 或 None, {指紋:數})。純函式。"""
    sha, counts = None, {}
    for ln in text.splitlines():
        if ln.startswith("#"):
            m = re.search(r"caliber_sha256=([0-9a-f]+)", ln)
            if m:
                sha = m.group(1)
            continue
        parts = ln.rstrip("\n").split("\t")
        if len(parts) == 4 and parts[3].isdigit():
            counts["\t".join(parts[:3])] = int(parts[3])
    return sha, counts


def build_baseline_text(counts: dict) -> str:
    """現況 → 基線檔全文（含口徑指紋檔頭）。純函式。"""
    rows = "\n".join(f"{fp}\t{n}" for fp, n in sorted(counts.items()))
    return (
        "# vendor 直綁凍結基線（WM.36 止血閘;G0 格6 准先行 2026-08-02;"
        "SSOT=reports/wm3536_vendor_registry_plan_20260802.md §7）\n"
        "# 閘只擋「新增檔/新表/增處」;清償（檔消失/處數下降）僅列印、手動移列——防棘輪反轉。\n"
        "# 格式: 相對路徑<TAB>表字面<TAB>承載形<TAB>處數（指紋零行號:行號隨編輯漂移會製造假新增）\n"
        f"# 口徑=quoted CamelCase 表 ∪ fred_series;caliber_sha256={_caliber_sha()}"
        "（regex 弱化即與本行不符=紅）\n"
        + rows + "\n")


def gate_report(found: dict, baseline_text):
    """→ (rc, 訊息列)。純函式——突變（拔基線謂詞/弱化比對恆 MATCH）之下 selftest 必紅。"""
    msgs = []
    if baseline_text is None:
        return 1, [f"✗ 基線檔不存在（{BASELINE}）——不敢猜白名單，fail-closed。"
                   "先跑 --write-baseline（過目後 commit 基線檔）。"]
    sha, base = parse_baseline(baseline_text)
    if sha != _caliber_sha():
        return 1, [f"✗ 口徑指紋不符（基線 {sha} ≠ 現行 {_caliber_sha()}）——"
                   "掃描 regex 被改動/弱化，或基線檔頭損毀。口徑變更須重寫基線並過目。"]
    new, inc, cleared = gate_verdicts(found, base)
    if cleared:
        msgs.append(f"（{len(cleared)} 條基線已清償/收緊，可自 {BASELINE.name} 手動移列——不自動改，防棘輪反轉）")
        msgs += [f"  {fp}" for fp in cleared]
    if new or inc:
        msgs.append(f"✗ vendor 直綁出血：新增 {len(new)} 條/增處 {len(inc)} 條（不在基線）——"
                    "WM.36 止血閘，10-15 起消費禁令無條件適用：")
        msgs += [f"  ＋ {fp}" for fp in new] + [f"  ↑ {fp}" for fp in inc]
        msgs.append("  修法：經 registry 解析（src/augur/catalog/world_concept.py，M2 API）取代表名字面；"
                    "確屬 C/D 觀測層豁免者依 plan §7.3 附條文依據入白名單（G0 後另批）。")
        return 1, msgs
    msgs.append(f"✓ vendor 直綁閘：無新增（基線容忍 {len(base)} 條指紋/"
                f"{sum(base.values())} 處存量，清償制）")
    return 0, msgs


def _default_paths():
    return sorted(q for d in SCAN_DIRS for q in (ROOT / d).rglob("*.py")
                  if "__pycache__" not in q.parts)


def gate(paths) -> int:
    text = BASELINE.read_text(encoding="utf-8") if BASELINE.exists() else None
    counts, read = _collect(paths)
    rc_floor = scan_floor.enforce("check_vendor_binding --gate", floor_checks(read))
    rc, msgs = gate_report(counts, text)
    for m in msgs:
        print(m, file=sys.stderr if rc else sys.stdout)
    return rc or rc_floor


def scan(paths) -> int:
    counts, read = _collect(paths)
    by_file: dict[str, dict[str, int]] = {}
    for fp, n in counts.items():
        rel, table, form = fp.split("\t")
        by_file.setdefault(rel, {})[f"{table}[{form}]"] = n
    print("== vendor 直綁全量分類報表（口徑=plan §1 廣口徑;歸類=plan §11）==")
    unclassified = []
    for cls in ("A", "B", "C", "D"):
        files = sorted(f for f in by_file if CLASSIFICATION.get(f) == cls)
        n_occ = sum(sum(by_file[f].values()) for f in files)
        print(f"\n[{_CLASS_LABEL[cls]}] {len(files)} 檔/{n_occ} 處")
        for f in files:
            detail = " ".join(f"{k}×{v}" for k, v in sorted(by_file[f].items()))
            print(f"  {f} ({sum(by_file[f].values())}): {detail}")
    unclassified = sorted(f for f in by_file if f not in CLASSIFICATION)
    if unclassified:
        print(f"\n[UNCLASSIFIED] ✗✗ {len(unclassified)} 檔不在 plan §11 清單——出血中，"
              "須歸類（A/B/C/D）＋呈 Steward 補裁：")
        for f in unclassified:
            print(f"  ✗ {f} ({sum(by_file[f].values())})")
    total_occ = sum(counts.values())
    by_form: dict[str, int] = {}
    for fp, n in counts.items():
        by_form[fp.split("\t")[2]] = by_form.get(fp.split("\t")[2], 0) + n
    forms = " ".join(f"{k}={v}" for k, v in sorted(by_form.items()))
    print(f"\n合計: {len(by_file)} 檔/{total_occ} 處（{forms}）;實讀 {len(read)} 檔")
    rc_floor = scan_floor.enforce("check_vendor_binding", floor_checks(read))
    print("  對帳 plan §1（2026-08-02 grep 口徑）: quoted_table 140＋fred_series 4=52 檔/144 處;"
          "quoted_table_esc 為 grep 盲點、本支紅燈實測揭露之增量。")
    print("⚠ 射程：靜態字面掃描——動態組表名（f-string 拼 FROM）與 JOIN 直綁"
          "（親驗 2 處、檔已在清單內）不在口徑，M3 逐批 AST 親驗（plan §6）。")
    return 1 if (unclassified or rc_floor) else 0


def write_baseline(paths) -> int:
    counts, read = _collect(paths)
    # 地板先於寫入：實讀 0 檔時重寫基線＝把 130 條存量凍結清單清空（棘輪反轉），故未過地板即拒寫。
    if scan_floor.enforce("check_vendor_binding --write-baseline", floor_checks(read)):
        print("✗ 未達對象數地板 ⇒ 拒絕以本次掃描重寫基線（否則凍結清單被清空＝閘自己放行自己）。",
              file=sys.stderr)
        return 1
    if BASELINE.exists():
        _sha, old = parse_baseline(BASELINE.read_text(encoding="utf-8"))
        new, inc, cleared = gate_verdicts(counts, old)
        print(f"── 基線 diff（舊 {len(old)} 條 → 新 {len(counts)} 條）──")
        for fp in new:
            print(f"  ＋ {fp}\t{counts[fp]}")
        for fp in inc + cleared:
            print(f"  Δ {fp}")
        if not (new or inc or cleared):
            print("  （零 diff）")
    else:
        print(f"── 新建基線（{len(counts)} 條指紋/{sum(counts.values())} 處）──")
    BASELINE.parent.mkdir(exist_ok=True)
    BASELINE.write_text(build_baseline_text(counts), encoding="utf-8")
    print(f"✓ 基線已寫 {len(counts)} 條 → {BASELINE}（過目後 commit）")
    return 0


# ── fixture：運行期串接組出直綁字面——本檔原始碼不含連續字面（自我匹配防線 (c)）──
_VQ = 'FROM ' + '"TaiwanStockPrice"'
_VE = 'FROM ' + r'\"TaiwanStockInfo\"'
_VF = 'FROM ' + 'fred_series'


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # 正例/負例/邊界（餵真輸入之純函式驗證）
    pos_q = f'cur.execute("SELECT date, close {_VQ} WHERE stock_id=%s")\n'
    got_q = analyse(pos_q)
    chk("正例:quoted vendor 表 SQL 被抓（表名+承載形）",
        got_q == [(1, "TaiwanStockPrice", "quoted_table")])
    pos_e = f'cur.execute("SELECT industry_category {_VE} WHERE stock_id=ANY(%s)")\n'
    chk("正例:跳脫引號變體被抓（grep 盲點、首次紅檢實證之逃逸形）",
        analyse(pos_e) == [(1, "TaiwanStockInfo", "quoted_table_esc")])
    pos_f = f'df = pd.read_sql("SELECT series_id, value {_VF} WHERE date<=%s", conn)\n'
    chk("正例:fred_series 直綁被抓", analyse(pos_f) == [(1, "fred_series", "fred_series")])
    chk("正例:同行兩處=計 2（處數棘輪之根據）",
        len(analyse(f'sql = "SELECT a {_VQ} x" + " UNION SELECT b {_VQ} y"\n')) == 2)
    neg_future = 'sql = f\'SELECT date FROM {resolve_sql("tw.daily_bar")} WHERE date>=%s\'\n'
    chk("負例:經 registry 解析之未來形不觸發", analyse(neg_future) == [])
    chk("邊界:整行註解排除（說明舊寫法之註解非直綁）",
        analyse(f"# 舊寫法: {_VQ}（已改線）\n") == [])
    chk("負例:未加引號小寫表不在口徑",
        analyse('df = pd.read_sql("SELECT * FROM feature_values", conn)\n') == [])

    # 突變驗紅 A：偵測 regex 弱化（恆不匹配）⇒ 正例零命中 ⇒ 上列正例斷言非恆真
    _sq, _se, _sf = globals()["_QUOTED"], globals()["_QUOTED_ESC"], globals()["_FRED"]
    globals()["_QUOTED"] = globals()["_QUOTED_ESC"] = globals()["_FRED"] = re.compile(r"(?!x)x")
    try:
        chk("突變:regex 弱化後正例不再被抓（證明偵測非恆真）",
            analyse(pos_q) == [] and analyse(pos_e) == [] and analyse(pos_f) == [])
    finally:
        globals()["_QUOTED"], globals()["_QUOTED_ESC"], globals()["_FRED"] = _sq, _se, _sf

    # gate 純函式紅綠雙向（基線謂詞被拔/比對被弱化為恆 MATCH ⇒ 下列必紅）
    fpA, fpB = "a.py\tTaiwanStockPrice\tquoted_table", "b.py\tfred_series\tfred_series"
    new, inc, cleared = gate_verdicts({fpA: 1, fpB: 2}, {fpA: 1})
    chk("gate:基線外新指紋被抓（擋 commit 之依據）", new == [fpB] and not inc)
    new, inc, cleared = gate_verdicts({fpA: 3}, {fpA: 1})
    chk("gate:同指紋增處被抓（處數棘輪）", inc == [f"{fpA}\t1→3"] and not new)
    chk("gate:零新增零清償=安靜通過", gate_verdicts({fpA: 1}, {fpA: 1}) == ([], [], []))
    new, inc, cleared = gate_verdicts({fpA: 1}, {fpA: 1, fpB: 2})
    chk("gate:已清償僅列印不擋、不自動移（防棘輪反轉）",
        cleared == [fpB] and not new and not inc)

    # gate_report 端到端（純函式、零 IO）
    base_ok = build_baseline_text({fpA: 1})
    chk("gate_report:基線不存在=fail-closed 紅", gate_report({fpA: 1}, None)[0] == 1)
    bad_sha = base_ok.replace(_caliber_sha(), "deadbeefdeadbeef")
    chk("gate_report:口徑指紋不符=紅（regex 弱化絆線）", gate_report({fpA: 1}, bad_sha)[0] == 1)
    chk("gate_report:現況=基線 ⇒ 綠", gate_report({fpA: 1}, base_ok)[0] == 0)
    chk("gate_report:新增指紋 ⇒ 紅（基線謂詞拔掉即此條紅）",
        gate_report({fpA: 1, fpB: 1}, base_ok)[0] == 1)
    chk("gate_report:增處 ⇒ 紅", gate_report({fpA: 2}, base_ok)[0] == 1)

    # 自我匹配防線（本專案五犯之型）
    _self_counts, _self_read = _collect([SELF])
    chk("自檔豁免:掃自己=零命中（fixture 樣本不得假紅）",
        _self_counts == {} and _self_read == set())
    chk("round-trip:build→parse 基線無損", parse_baseline(base_ok) == (_caliber_sha(), {fpA: 1}))

    # ── 對象數地板（M-G2）：餵**真掃描輸出**驗紅綠雙向（#35(1) 不手寫形狀）──
    _live_counts, _live_read = _collect(_default_paths())
    chk(f"地板:真 repo 實讀 {len(_live_read)} 檔 ⇒ 綠（本行即掃描範圍之下游絆線）",
        scan_floor.verdict("live", floor_checks(_live_read))[0] == 0)
    # **本閘最兇之假綠**：實讀 0 檔 ⇒ found={} ⇒ 基線全數「已清償」而 new/inc 皆空 ⇒ gate_report 綠
    _empty_counts, _empty_read = _collect([ROOT / "scripts" / "no_such_file_mg2_probe.py"])
    _base_txt = build_baseline_text({fpA: 1, fpB: 2})
    chk("零對象時 gate_report 仍判綠（假綠之本體，故地板不可省）",
        _empty_counts == {} and gate_report(_empty_counts, _base_txt)[0] == 0)
    chk("地板:同一組零對象實讀集 ⇒ 紅（新加之絆線）",
        scan_floor.verdict("empty", floor_checks(_empty_read))[0] == 1)
    _no_src = {f"scripts/f{i}.py" for i in range(MIN_FILES + 5)}
    chk("地板:src/ 整個不見（總數仍夠）⇒ 紅", scan_floor.verdict("x", floor_checks(_no_src))[0] == 1)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="WM.36 vendor 直綁止血閘（凍結基線、新增即紅）")
    ap.add_argument("--scan", action="store_true", help="全量分類報表（預設動作）")
    ap.add_argument("--gate", action="store_true", help="pre-commit 閘：僅擋基線外之新增/增處")
    ap.add_argument("--write-baseline", action="store_true", help="以現況重寫基線（列印 diff；過目後 commit）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    paths = _default_paths()
    if a.write_baseline:
        return write_baseline(paths)
    if a.gate:
        return gate(paths)
    return scan(paths)


if __name__ == "__main__":
    sys.exit(main())
