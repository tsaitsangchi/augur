#!/usr/bin/env python3
"""🎯 KH1 旁路／零變異探針——正名對偶之分流度量（M-G15；旁路存廢待裁、本支不改行為）。

白話:KH1「有原文即 pass」與 KH8 被判死同構（零變異不得充當獨立證據）。
  本支只度量＋報紅，**不刪旁路**（Steward 裁存廢）。

分流三桶（live + code 結構）:
  · real_qual     — note 含 qualification=pass（真資格）
  · bypass_eligible — 有原文且無 qual=pass（走旁路／自我背書才會 pass）
  · prior_depth   — 帳本仍寫 prior_depth（M-K2 債；計入假綠族）

門檻（master 第 23 步）:旁路占比 >90% ⇒ **必紅**；今日 live 預期紅。

守原則 #15 · #32b／§P4.E7（零變異）· #28 · #29a/d · #35。

執行指令矩陣
------------
    python3 scripts/check_kh1_bypass.py            # 無參數＝--check
    python3 scripts/check_kh1_bypass.py --check    # 旁路占比>門檻 → rc=1
    python3 scripts/check_kh1_bypass.py --check --json
    python3 scripts/check_kh1_bypass.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
AUTO_ADMIT = REPO / "src" / "augur" / "knowledge" / "auto_admit.py"
# master：旁路占比 >90% 必紅
BYPASS_RED_RATIO = 0.90
BYPASS_NOTE_MARKERS = (
    "既有原文",
    "KH1_BYPASS",
    "原文在庫→准入",
    "視同通過",
)
PRIOR_NOTE = "prior_depth"


def bypass_ratio(*, n_bypass: int, n_total: int) -> float:
    """旁路／自我背書佔 KH1 評估母體之比。純函式。"""
    if n_total <= 0:
        return 0.0
    return float(n_bypass) / float(n_total)


def bypass_rc(*, ratio: float, threshold: float = BYPASS_RED_RATIO) -> int:
    """占比 > 門檻 → 紅。純函式（先驗紅：ratio=0.95 → 1）。"""
    return 1 if ratio > threshold else 0


def classify_kh1_note(note: str | None) -> str:
    """單則 note → real_qual | prior_depth | bypass | other。純函式。"""
    n = (note or "").strip()
    if n == "qualification=pass" or n.startswith("qualification=pass"):
        return "real_qual"
    if PRIOR_NOTE in n:
        return "prior_depth"
    if any(m in n for m in BYPASS_NOTE_MARKERS):
        return "bypass"
    return "other"


def code_bypass_still_present(src: str) -> bool:
    """生產碼仍含旁路路徑（正名後標記或舊文案）。純函式。"""
    # 切掉本檔／自測干擾：只看 auto_admit 正文
    return (
        ("既有原文" in src or "KH1_BYPASS" in src)
        and "has_text" in src
        and "verdict" in src
        and '"pass"' in src
    )


def _structural_counts(cur) -> dict:
    """結構面：有原文 ∩ 無最新 qual=pass ＝旁路可走集合。"""
    cur.execute(
        """
        WITH texts AS (
          SELECT DISTINCT item_id FROM knowledge_item_text
        ),
        latest_qual AS (
          SELECT DISTINCT ON (item_id) item_id, verdict
          FROM knowledge_import_qualification
          ORDER BY item_id, ingested_at DESC NULLS LAST, qualification_id DESC
        )
        SELECT
          (SELECT count(*) FROM texts) AS n_text,
          (SELECT count(*) FROM texts t
             LEFT JOIN latest_qual q ON q.item_id=t.item_id
            WHERE q.verdict IS DISTINCT FROM 'pass') AS n_bypass_eligible,
          (SELECT count(*) FROM texts t
             JOIN latest_qual q ON q.item_id=t.item_id
            WHERE q.verdict='pass') AS n_real_qual_text
        """
    )
    n_text, n_bypass, n_real = cur.fetchone()
    return {
        "n_text": int(n_text or 0),
        "n_bypass_eligible": int(n_bypass or 0),
        "n_real_qual_on_text": int(n_real or 0),
    }


def _ledger_buckets(cur) -> dict:
    """帳本面：既有 layer_scores→'1' note 分流（含 prior_depth 債）。"""
    cur.execute(
        """
        SELECT COALESCE(layer_scores->'1'->>'note', ''), count(*)::int
        FROM knowhow_auto_admit_state
        WHERE layer_scores ? '1'
        GROUP BY 1
        """
    )
    buckets = {"real_qual": 0, "prior_depth": 0, "bypass": 0, "other": 0}
    samples = []
    for note, n in cur.fetchall():
        kind = classify_kh1_note(note)
        buckets[kind] = buckets.get(kind, 0) + int(n)
        if len(samples) < 8:
            samples.append({"note": note[:80], "n": int(n), "kind": kind})
    total = sum(buckets.values())
    # 假綠族＝bypass + prior_depth（皆非獨立資格證據）
    fake = buckets["bypass"] + buckets["prior_depth"]
    return {"buckets": buckets, "n_ledger": total, "n_fake_green": fake, "note_samples": samples}


def _check(*, as_json=False) -> int:
    from augur.core import db

    src = AUTO_ADMIT.read_text(encoding="utf-8") if AUTO_ADMIT.exists() else ""
    code_hit = code_bypass_still_present(src)
    with db.connect() as conn, conn.cursor() as cur:
        structural = _structural_counts(cur)
        ledger = _ledger_buckets(cur)

    n_text = structural["n_text"]
    n_byp = structural["n_bypass_eligible"]
    ratio = bypass_ratio(n_bypass=n_byp, n_total=n_text)
    # 雙尺：結構旁路占比 OR 帳本假綠占比；取較嚴（較大）者定 rc
    led_ratio = bypass_ratio(
        n_bypass=ledger["n_fake_green"], n_total=max(ledger["n_ledger"], 1))
    ratio_for_rc = max(ratio, led_ratio)
    rc = bypass_rc(ratio=ratio_for_rc)
    if code_hit and n_text > 0 and ratio_for_rc <= BYPASS_RED_RATIO:
        # 碼仍在旁路＋母體非空卻占比不高：仍紅（結構未拆）
        rc = 1

    out = {
        "structural": structural,
        "structural_bypass_ratio": round(ratio, 6),
        "ledger": ledger,
        "ledger_fake_green_ratio": round(led_ratio, 6),
        "ratio_for_rc": round(ratio_for_rc, 6),
        "threshold": BYPASS_RED_RATIO,
        "code_bypass_present": code_hit,
        "rc": rc,
        "note": "旁路存廢待裁（M-G15／§4）；本支只度量",
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return rc

    print("── KH1 旁路探針（M-G15；>90% 必紅；存廢待裁）──")
    print(f"  結構: text={n_text} bypass_eligible={n_byp} "
          f"real_qual_on_text={structural['n_real_qual_on_text']} "
          f"ratio={ratio:.4f}")
    print(f"  帳本: {ledger['buckets']} fake_green_ratio={led_ratio:.4f}")
    print(f"  code_bypass_present={code_hit}  ratio_for_rc={ratio_for_rc:.4f}  "
          f"→ rc={rc}" + (" 🔴" if rc else " 🟢"))
    return rc


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("先驗紅：ratio=0.95 → rc=1", bypass_rc(ratio=0.95) == 1)
    chk("邊：ratio=0.90 不紅（僅 >）", bypass_rc(ratio=0.90) == 0)
    chk("綠：ratio=0.5 → 0", bypass_rc(ratio=0.5) == 0)
    chk("空母體 ratio=0", bypass_ratio(n_bypass=0, n_total=0) == 0.0)
    chk("classify real", classify_kh1_note("qualification=pass") == "real_qual")
    chk("classify prior", classify_kh1_note("prior_depth") == "prior_depth")
    chk("classify bypass 正名", classify_kh1_note("KH1_BYPASS:既有原文旁路") == "bypass")
    chk("classify bypass 舊文", classify_kh1_note("既有原文＝KH1 視同通過") == "bypass")
    fake_src = 'if snap["has_text"]:\n  return {"verdict": "pass", "note": "KH1_BYPASS:x"}'
    chk("code 旁路偵測", code_bypass_still_present(fake_src))
    chk("無旁路文案 → False", not code_bypass_still_present("return pass qualification"))

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH1 旁路探針（M-G15）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check(as_json=a.json)


if __name__ == "__main__":
    sys.exit(main())
