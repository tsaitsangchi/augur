#!/usr/bin/env python3
"""🎯 KH0→KH9 單一驅動器——把「資料製造」與「層級推進」串成一條可續跑的鏈。

守原則 #12（單一權威家：本支**只編排**既有 script，不重寫其邏輯）、#15（誠實：每段印真實待辦量與 rc）、
#25（首輪最小）、#28（本地零 Claude usage）。

**為何需要本支**：先前需人工記住兩支各管一半——
  ① `refresh_knowledge_pipeline.py`＝資料製造（harvest→promote→fulltext→sentences→…→embed→kip）
  ② `run_knowhow_auto_admit.py`＝層級推進（`evaluate_layer(0..N)`）
二者無共同入口、順序靠記憶，且 `drain_knowhow_admit_to_ceiling.sh` 之 `ceiling=7` 已過時（KH8/KH9 早已 LAND）。

**KH10 明確不納入（非遺漏）**：depth-10 評估器僅查 `gate.enabled` 即 pass ——
獨立核驗判定其為**自我背書**（KH10 用自己的組態證明自己），違 `AUGUR-MC v1.6 §P4.E7`
（不得僅以系統自身產出為據）。故本支上限硬釘 9；欲開至 10 須先改該評估器並經人閘。

執行指令矩陣
------------
    python3 scripts/run_kh_chain.py                          # 無參數＝--check（唯讀：前置檢查＋各段待辦量）
    python3 scripts/run_kh_chain.py --check                  # 同上
    python3 scripts/run_kh_chain.py --dry-run --domain quant_finance
    python3 scripts/run_kh_chain.py --run --domain quant_finance --limit 1000        # 全鏈（資料製造→層級推進）
    python3 scripts/run_kh_chain.py --run --phase data --domain medicine --limit 500 # 只做資料製造
    python3 scripts/run_kh_chain.py --run --phase advance --limit 5000               # 只做層級推進
    python3 scripts/run_kh_chain.py --run --up-to 7                                  # 保守只推到 7
    python3 scripts/run_kh_chain.py --selftest                                       # 紅綠自測（免 DB 免 API）
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  # #29(a) 個別可執行

REPO = Path(__file__).resolve().parent.parent
PY = str(REPO / "venv" / "bin" / "python3")
CEILING = 9  # KH10 不納入（自我背書；見 docstring）
CONCURRENT_MARKERS = ("scripts/run_knowhow_auto_admit.py", "scripts/refresh_knowledge_pipeline.py")


def phase_cmds(phase: str, domain: str | None, limit: int | None, up_to: int) -> list[list[str]]:
    """回傳待執行之子指令序（純函式，可自測）。"""
    cmds: list[list[str]] = []
    if phase in ("data", "all"):
        c = [PY, "scripts/refresh_knowledge_pipeline.py"]
        if domain:
            c += ["--domain", domain]
        if limit:
            c += ["--limit", str(limit)]
        cmds.append(c)
    if phase in ("advance", "all"):
        cmds.append([
            PY, "scripts/run_knowhow_auto_admit.py",
            "--until-empty", "--apply-up-to", str(up_to),
            "--limit", str(limit or 5000), "--max-rounds", "200",
        ])
    return cmds


def clamp_up_to(requested: int, gate_cap: int | None) -> tuple[int, str]:
    """上限夾制（純函式）：min(requested, CEILING, gate_cap)。"""
    eff = min(int(requested), CEILING)
    why = []
    if requested > CEILING:
        why.append(f"請求 {requested} → 夾至 {CEILING}（KH10 自我背書、本支不納入）")
    if gate_cap is not None and gate_cap < eff:
        why.append(f"再受 gate.max_auto_depth={gate_cap} 夾")
        eff = int(gate_cap)
    return eff, "；".join(why) or "未夾制"


def preflight(cur) -> dict:
    """唯讀前置檢查：gate 組態、鑑別力、各段待辦量。"""
    from augur.knowledge import auto_admit as aa, evidence as kh8

    out: dict = {}
    gate = aa.load_gate(cur)
    out["gate"] = {k: gate.get(k) for k in ("enabled", "progressive_enabled", "raw_floor_enabled",
                                            "max_auto_depth", "require_kh8", "require_kh9")}
    disc = kh8.population_discriminates(cur)
    out["kh8_discriminates"] = {"ok": disc["ok"], "bands": disc["bands"], "n": disc["n"]}
    # 欄名以 information_schema 實查為準（#2 API/DB 即權威；2026-07-30 實查 knowledge_staging
    # 之欄為 status／promoted_at，**無 review_flag**——該名屬他表）
    cur.execute("SELECT status, count(*) FROM knowledge_staging GROUP BY 1 ORDER BY 2 DESC")
    st = cur.fetchall()
    out["staging_by_status"] = st
    out["pending_staging"] = sum(int(n) for s_, n in st if s_ in ("pending", None))
    cur.execute("""SELECT coalesce(admit_depth,0) d, count(*) FROM knowhow_auto_admit_state
                    WHERE target_kind='item' GROUP BY 1 ORDER BY 1""")
    out["depth_dist"] = cur.fetchall()
    # count(DISTINCT i.item_id)：`knowledge_item_text` 以 (item_id, seq) 存多列原文
    # （實查 158,064 列 / 146,348 distinct item，4,860 個 item 有多列）——
    # 用 count(*) 會數成原文列數而非 item 數，曾使本行印出 158,064 > 有原文者總數 146,348。
    cur.execute("""SELECT count(DISTINCT i.item_id) FROM knowledge_item i
                     JOIN knowledge_item_text x ON x.item_id=i.item_id
                     LEFT JOIN knowhow_auto_admit_state st
                       ON st.target_kind='item' AND st.target_id=i.item_id::text
                    WHERE coalesce(st.admit_depth,0) < %s""", (CEILING,))
    out["advance_pool"] = int(cur.fetchone()[0])
    # KH0 底線不變式（大憲章 v1.52.0 第三部 philosophy／知識節；本支為其指定機械落點）：
    # 「有原文 ∧ 無 admit_state 列」之計數須恆為 0；非 0 即底線破口，須先補齊方得推進上層。
    # **普遍口徑**（憲章 v1.53.0 修正 v1.52.0 之量尺）：分母＝**全部 knowledge_item**，
    # 非僅「有原文者」。Steward 2026-07-31：「就算是一個標題也有其語意進行理解」
    # ——實測無原文者 138,780 件**全部有標題**、無題者 0 件，故「無原文＝無從理解」
    # 之前提不成立。前版以 JOIN item_text 收窄分母，使「破口 0」成為窄口徑假綠
    # （真實普遍破口 138,829／285,177＝48.7%）。全文之有無只影響理解**深度**，
    # 不影響**是否須被理解**。
    cur.execute("""SELECT count(*) FROM knowledge_item i
                     LEFT JOIN knowhow_auto_admit_state st
                       ON st.target_kind='item' AND st.target_id=i.item_id::text
                    WHERE st.target_id IS NULL""")
    out["kh0_breach"] = int(cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM knowledge_item")
    out["items_total"] = int(cur.fetchone()[0])
    cur.execute("""SELECT count(DISTINCT i.item_id) FROM knowledge_item i
                    LEFT JOIN knowledge_item_text x ON x.item_id=i.item_id
                   WHERE x.item_id IS NULL""")
    out["no_fulltext"] = int(cur.fetchone()[0])  # 誠實例外（metadata-only，KH0 不適用）
    cur.execute("SELECT count(DISTINCT item_id) FROM knowledge_item_text")
    out["with_fulltext"] = int(cur.fetchone()[0])
    # 同尺自檢：可推進池（子集）不得大於有原文者總數（母集）。
    # 此不變式正是抓出 count(*) 膨脹之處——兩數相鄰印出、矛盾即現形。
    out["scale_consistent"] = out["advance_pool"] <= out["with_fulltext"]
    return out


def concurrent_running() -> list[str]:
    try:
        r = subprocess.run(["pgrep", "-af", "|".join(CONCURRENT_MARKERS)],
                           capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    hits = []
    for line in (r.stdout or "").splitlines():
        if any(m in line for m in CONCURRENT_MARKERS) and "run_kh_chain" not in line:
            hits.append(line.strip()[:120])
    return hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KH0→KH9 單一驅動器（編排既有 script、不重寫邏輯）")
    ap.add_argument("--check", action="store_true", help="唯讀：前置檢查＋各段待辦量")
    ap.add_argument("--dry-run", action="store_true", help="印將執行之子指令，零副作用")
    ap.add_argument("--run", action="store_true", help="實際執行")
    ap.add_argument("--phase", choices=("data", "advance", "all"), default="all")
    ap.add_argument("--domain", default=None, help="資料製造段之域（實值見 knowledge_query.domain）")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--up-to", type=int, default=CEILING, help=f"層級上限（硬頂 {CEILING}；KH10 不納入）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        pf = preflight(cur)
        eff, why = clamp_up_to(a.up_to, pf["gate"].get("max_auto_depth"))

    print("══ KH0→KH9 驅動器 前置檢查（唯讀）══")
    print(f"  gate：{pf['gate']}")
    print(f"  KH8 鑑別力：{pf['kh8_discriminates']}"
          + ("" if pf["kh8_discriminates"]["ok"] else "  ⚠ 不具鑑別力 → KH8 一律 fail、推進將止於 7"))
    print(f"  staging：{pf['staging_by_status']}｜待促升(pending)={pf['pending_staging']:,}")
    print(f"  admit_depth 分佈：{pf['depth_dist']}")
    print(f"  可推進池（有原文且 depth<{CEILING}）：{pf['advance_pool']:,}"
          f" / 有原文者 {pf['with_fulltext']:,}"
          + ("" if pf["scale_consistent"] else "  ✗ **同尺矛盾：子集大於母集，計數有誤**"))
    print(f"  層級上限：{eff}（{why}）")
    if pf["kh0_breach"] == 0:
        print(f"  KH0 底線不變式：✓ 破口 0（全部 {pf['items_total']:,} 件 item 皆已評）")
    else:
        _pct = pf["kh0_breach"] / max(pf["items_total"], 1) * 100
        print(f"  KH0 底線不變式：✗ **破口 {pf['kh0_breach']:,} / {pf['items_total']:,} 件"
              f"（{_pct:.1f}%）未評 KH0**（普遍口徑，憲章 v1.53.0；標題即有語意，"
              f"無原文者不豁免；其中無原文 {pf['no_fulltext']:,} 件）"
              "——跑 --run --phase advance 由 KH0 逐層補齊，收尾自動覆核")
    busy = concurrent_running()
    if busy:
        print("  ⚠ 偵測到並行 runner（避免同表競態，--run 將拒絕執行）：")
        for b in busy:
            print(f"     {b}")

    cmds = phase_cmds(a.phase, a.domain, a.limit, eff)
    if not a.run:
        print(f"\n將執行 {len(cmds)} 段（--phase {a.phase}）：")
        for c in cmds:
            print("  " + " ".join(shlex.quote(x) for x in c))
        print("\n（唯讀／dry-run；跑 --run 實作。斷點續跑＝各子段皆冪等，重跑同指令即續）")
        return 0

    if busy:
        print("\nABORT：已有並行 runner，先等其收槍（守同表競態紀律）")
        return 3

    # KH0 底線不變式之**閘位**（2026-07-31 修正；前版擺錯位置）：
    # 憲章 v1.52.0 之「須先補齊方得推進上層」＝**KH0 須先於 KH8/KH9 被評**，
    # 而 `run_knowhow_auto_admit` 本來就是**由 KH0 逐層往上**評——它正是補齊之手段。
    # 前版卻以 `破口>0 ⇒ ABORT --phase advance/all` 實作，**剛好擋掉修復動作本身**：
    # 每次 data 段抓進新全文（本例＝fetch_oa_fulltext 落地 49 筆）就必然造成破口，
    # 於是全鏈從此再也跑不完。此為施作者誤讀條文之實作錯，非條文本身要求。
    #（第四次獨立核驗修復順序第 8 項已預示：「射程收到『結果採信』而非擋 --phase」。）
    # 正解：**事前警示、事後驗證**——跑完仍有破口才是真違反。
    if pf["kh0_breach"] > 0:
        print(f"\n⚠ KH0 底線破口 {pf['kh0_breach']:,} 件（新落地全文尚未評 KH0）"
              + ("——本次推進段將由 KH0 逐層補齊，收尾自動覆核"
                 if a.phase in ("advance", "all")
                 else "——本次未含推進段，破口將留存至下次 --phase advance"))

    for i, c in enumerate(cmds, 1):
        print(f"\n── [{i}/{len(cmds)}] {' '.join(shlex.quote(x) for x in c)}")
        rc = subprocess.call(c, cwd=str(REPO))
        print(f"── rc={rc}")
        if rc != 0:
            print(f"ABORT：第 {i} 段 rc={rc}（不續跑後段；修好後重跑同指令即從該段續）")
            return rc

    # 事後驗證：推進段跑完仍有破口 ⇒ 才是真的違反不變式（補齊沒生效）
    if a.phase in ("advance", "all"):
        with db.connect() as conn, conn.cursor() as cur:
            post = preflight(cur)
        if post["kh0_breach"] > 0:
            print(f"\n✗ KH0 底線不變式**未回復**：推進後仍有破口 {post['kh0_breach']:,} 件"
                  f"（推進前 {pf['kh0_breach']:,}）——憲章 v1.52.0；補齊未生效，須查核")
            return 4
        print(f"\n✓ KH0 底線不變式：破口已回復為 0（推進前 {pf['kh0_breach']:,} 件）")

    print("\n全鏈完成（各段 rc=0）。建議收尾：python3 scripts/run_kh_chain.py --check 覆核分佈")
    return 0


def _selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool) -> None:
        print(f"  {'✓' if cond else '✗'} {name}")
        if not cond:
            fails.append(name)

    e, w = clamp_up_to(10, None)
    chk("請求 10 → 夾至 9（KH10 不納入）", e == 9 and "自我背書" in w)
    e, _ = clamp_up_to(9, 7)
    chk("gate.max_auto_depth=7 再夾 → 7", e == 7)
    e, w = clamp_up_to(9, 9)
    chk("請求 9 且 gate=9 → 9 未夾制", e == 9 and w == "未夾制")
    e, _ = clamp_up_to(5, 9)
    chk("請求 5 → 保守值不被抬高", e == 5)
    c = phase_cmds("all", "quant_finance", 1000, 9)
    chk("phase=all → 兩段", len(c) == 2)
    chk("第一段為資料製造", "refresh_knowledge_pipeline.py" in c[0][1])
    chk("第二段為層級推進且帶 --apply-up-to 9", "run_knowhow_auto_admit.py" in c[1][1] and "9" in c[1])
    chk("domain 有傳遞", "quant_finance" in c[0])
    chk("phase=data → 僅一段", len(phase_cmds("data", None, None, 9)) == 1)
    chk("phase=advance → 僅一段且為推進", len(phase_cmds("advance", None, None, 9)) == 1
        and "run_knowhow_auto_admit.py" in phase_cmds("advance", None, None, 9)[0][1])
    chk("CEILING 硬釘 9", CEILING == 9)
    # 行為驗證（非字面斷言）：以 fake cursor 實跑 preflight()，攔它**實際送出**之 SQL。
    # 前版用 grep 本檔原始碼，結果斷言字串自己被掃到（計數 3→4）、
    # 且 `"count(*) …" not in _src` 恆假 ⇒ 保證 RED。此即字面斷言之病，改為驗行為。
    class _Cur:
        """記錄所送 SQL 並回可用形狀；不連 DB。"""

        def __init__(self):
            self.sqls: list[str] = []
            self._n = 0

        def execute(self, sql, args=()):
            self.sqls.append(" ".join(str(sql).split()))
            self._n += 1

        def fetchall(self):
            last = self.sqls[-1]
            if "knowledge_staging" in last:
                return [("promoted", 10), ("pending", 3)]
            return [(7, 5)]

        def fetchone(self):
            return (5,)

    import types
    fake = _Cur()
    stub = types.SimpleNamespace(
        load_gate=lambda c: {"enabled": True, "progressive_enabled": True,
                             "raw_floor_enabled": True, "max_auto_depth": 9,
                             "require_kh8": True, "require_kh9": True})
    stub8 = types.SimpleNamespace(
        population_discriminates=lambda c, **k: {"ok": True, "bands": ["high"], "n": 1})
    import sys as _sys
    _saved = {k: _sys.modules.get(k) for k in ("augur.knowledge.auto_admit", "augur.knowledge.evidence")}
    _sys.modules["augur.knowledge.auto_admit"] = stub
    _sys.modules["augur.knowledge.evidence"] = stub8
    try:
        pf = preflight(fake)
    finally:
        for k, v in _saved.items():
            if v is None:
                _sys.modules.pop(k, None)
            else:
                _sys.modules[k] = v

    joins = [q for q in fake.sqls if "JOIN knowledge_item_text" in q]
    # v1.53.0：kh0_breach 已改**普遍口徑**（不 JOIN item_text）⇒ 由 3 條降為 2 條
    # （advance_pool 與 no_fulltext）。此數字隨口徑走，改口徑時須同步改本鎖。
    chk("preflight 查 item_text 之 JOIN 為 2 條（v1.53.0 普遍口徑後）", len(joins) == 2)
    chk("每條 item_text JOIN 皆以 count(DISTINCT) 計 item、不數原文列",
        all("count(DISTINCT i.item_id)" in q for q in joins))
    # KH0 破口之**普遍口徑**回歸鎖：其查詢不得再以 item_text 收窄分母
    kh0q = [q for q in fake.sqls
            if "knowhow_auto_admit_state" in q and "st.target_id IS NULL" in q]
    chk("KH0 破口查詢存在", len(kh0q) == 1)
    chk("KH0 破口為普遍口徑（不 JOIN item_text 收窄分母）",
        bool(kh0q) and "JOIN knowledge_item_text" not in kh0q[0])
    chk("有算 items_total 作分母", "items_total" in pf)
    chk("KH0 底線破口有被算出", "kh0_breach" in pf)
    chk("同尺自檢有被算出且成立（5<=5）", pf.get("scale_consistent") is True)
    # KH0 閘位之回歸鎖（2026-07-31）：前版以「破口>0 ⇒ ABORT --phase advance/all」實作，
    # 剛好擋掉修復動作本身（推進段正是由 KH0 逐層補齊者），使全鏈在每次抓進新全文後
    # 再也跑不完。切 def _selftest 之前的本體掃描，避免斷言字串掃到自己。
    _body = open(__file__, encoding="utf-8").read().split("def _selftest")[0]
    chk("KH0 破口不再事前 ABORT（否則擋掉修復動作本身）",
        "ABORT\uff1aKH0 \u5e95\u7dda\u7834\u53e3" not in _body)
    chk("改為事前警示", "\u26a0 KH0 \u5e95\u7dda\u7834\u53e3" in _body)
    chk("改為事後驗證（推進後仍有破口才失敗）",
        'post["kh0_breach"] > 0' in _body and "\u672a\u56de\u5fa9" in _body)
    print("selftest: " + ("RED" if fails else "GREEN"))
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__.split("執行指令矩陣")[1].strip())
        print("\n--- 無參數＝--check（唯讀）---\n")
        sys.exit(main(["--check"]))
    sys.exit(main())
