"""KH8 證據加權 — 最小可評估片（min-LAND）。

🎯 這支在做什麼(白話):依庫內可數輸入（句數／終態／embedding／KH4 狀態）
   算出 evidence_score＋confidence_band，寫入 knowhow_evidence_weight。
   **不是**答案 SSOT、**≠**approve／activate／可交易；禁硬編專題答案。
守 #15(缺料誠實)· #18(領域名詞)· NHC-keep· FZ-keep· PME-GATE-keep。

執行指令矩陣(本檔=library #18；免 DB 可個別驗證):
  python -m augur.knowledge.evidence
  python -m augur.knowledge.evidence --selftest
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

CONFIDENCE_BANDS = ("high", "medium", "low", "absent")
PASS_BANDS = frozenset({"high", "medium", "low"})

# KH4 視為風險／矛盾加重的答態（庫內既有字面，非發明標籤）
_RISKY_ANSWER = frozenset(
    {"ineligible", "blocked", "ungrounded", "declined", "fail", "failed"}
)


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def query_hash_for_item(item_id: int) -> str:
    raw = f"kh8:item:{int(item_id)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def band_for_score(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.40:
        return "medium"
    if score >= 0.15:
        return "low"
    return "absent"


def compute_evidence_weight(
    *,
    citation_count: int,
    has_text: bool,
    has_sentence: bool,
    has_embedding: bool,
    kh4_answer_status: str | None = None,
) -> dict[str, Any]:
    """純函式：由可觀測輸入算出權重向量（不碰 DB）。"""
    cite_n = max(0, int(citation_count))
    cite_norm = min(cite_n / 5.0, 1.0)  # 5 句＝滿檔；非神奇常數，僅正規化尺度
    terminal = 1.0 if has_sentence else (0.5 if has_text else 0.0)
    embed = 1.0 if has_embedding else 0.0
    status = (kh4_answer_status or "").strip().lower()
    kh4_ok = 1.0 if status == "eligible" else 0.0
    contra = 1.0 if status in _RISKY_ANSWER else 0.0

    evidence_score = max(
        0.0,
        min(
            1.0,
            0.35 * cite_norm
            + 0.25 * terminal
            + 0.25 * embed
            + 0.15 * kh4_ok
            - 0.40 * contra,
        ),
    )
    band = band_for_score(evidence_score)
    risk_flags: list[str] = []
    if cite_n == 0:
        risk_flags.append("no_citations")
    if not has_sentence:
        risk_flags.append("no_sentence")
    if not has_embedding:
        risk_flags.append("no_embedding")
    if status in _RISKY_ANSWER:
        risk_flags.append(f"kh4_{status}")
    if band == "absent":
        risk_flags.append("insufficient_evidence")

    return {
        "citation_count": cite_n,
        "terminal_score": terminal,
        "contradiction_score": contra,
        "evidence_score": round(evidence_score, 6),
        "confidence_band": band,
        "risk_flags": risk_flags,
        "components": {
            "cite_norm": round(cite_norm, 6),
            "terminal": terminal,
            "embed": embed,
            "kh4_ok": kh4_ok,
            "contra": contra,
            "kh4_answer_status": kh4_answer_status,
            "formula": "0.35*cite_norm+0.25*terminal+0.25*embed+0.15*kh4_ok-0.40*contra",
        },
        "status": "confidence_banded" if band != "absent" else "unweighted",
    }


# ── C-2 補正（2026-07-30；hugo「甲成立」＋自毀條款當日到期）────────────────
# 病灶：knowhow_evidence_weight 145,949 列 100% band='high'（score 0.72–1.0）。
# 根因**非**寫死——公式為真，但 terminal／embed／kh4_ok 三分量對全母體恆 1.0，
# 因為權重只算在「已終態＋已嵌入＋已 eligible」之 item 上＝**母體選擇效應**，
# 故 score 底線恆 0.72、必落 high。結論：本指標**結構上不可能鑑別**。
# 處置：**零變異之指標不得充當證據**（承 `AUGUR-MC v1.6 §P4.E7`／KS 反自我背書之精神：
# 不具鑑別力之量測不構成獨立證據）。以下檢定使該情形 **fail-closed**、不再靜默 pass。
MIN_DISCRIMINATING_BANDS = 2


def population_discriminates(cur, *, exclude_item_id: int | None = None) -> dict[str, Any]:
    """KH8 母體是否具鑑別力——**兩道判準皆須過**（2026-07-30 獨立核驗 FAIL 後強化）。

    (1) `confidence_band` 至少兩種；
    (2) **三分量 `terminal`／`embed`／`kh4_ok` 至少其一在母體有變異**
        ——原僅檢 (1) 之弱判準可被「加一列 band='low'」一句解除（**降級母體即解閘**，
        與設計意圖相反；核驗實證 F-bypass-1）；真因在三分量恆 1.0（母體選擇效應），
        故 (2) 才是結構判準。

    `exclude_item_id`：排除**正在受判之 item**——原實作先 `record_weight()` 再查，
    致判準被受判列自證污染（核驗實證：同一交易內 ok=False 立即翻 ok=True）。

    表未建／空表／僅剩受判列 → ok=False（無從證明鑑別力，保守 fail-closed）。
    """
    cur.execute("SELECT to_regclass(%s)", ("public.knowhow_evidence_weight",))
    if not cur.fetchone()[0]:
        return {"ok": False, "bands": [], "n": 0, "note": "KH8 表未建"}
    where = "" if exclude_item_id is None else "WHERE item_id <> %s"
    args: tuple = () if exclude_item_id is None else (exclude_item_id,)
    cur.execute(
        f"SELECT confidence_band, count(*) FROM knowhow_evidence_weight {where} GROUP BY 1 ORDER BY 2 DESC",
        args,
    )
    rows = cur.fetchall()
    bands = [r[0] for r in rows]
    n = sum(int(r[1]) for r in rows)
    if n == 0:
        return {"ok": False, "bands": [], "n": 0, "note": "KH8 母體為空（排除受判列後）"}
    if len(bands) < MIN_DISCRIMINATING_BANDS:
        return {"ok": False, "bands": bands, "n": n,
                "note": f"判準(1)不過：{n} 列僅 {bands} 一種 band"}
    cur.execute(
        f"""SELECT count(DISTINCT components->>'terminal'),
                   count(DISTINCT components->>'embed'),
                   count(DISTINCT components->>'kh4_ok')
              FROM knowhow_evidence_weight {where}""",
        args,
    )
    t, e, k = (int(x or 0) for x in cur.fetchone())
    if max(t, e, k) < 2:
        return {"ok": False, "bands": bands, "n": n,
                "note": (f"判準(2)不過：三分量皆無變異（terminal={t}／embed={e}／kh4_ok={k} 種值）"
                         "——母體選擇效應未解，band 變異不足以證明鑑別力")}
    return {"ok": True, "bands": bands, "n": n,
            "note": f"band {bands}；三分量變異數 terminal={t}／embed={e}／kh4_ok={k}（n={n}）"}

def gather_item_inputs(cur, item_id: int, snap: Mapping[str, Any]) -> dict[str, Any]:
    """從庫讀 item 可數輸入（句數／KH4 答態）。"""
    cite_n = 0
    cur.execute(
        """
        SELECT count(*)::int
          FROM knowledge_sentence s
          JOIN knowledge_item_text x ON x.itext_id=s.itext_id
         WHERE x.item_id=%s
        """,
        (int(item_id),),
    )
    row = cur.fetchone()
    if row:
        cite_n = int(row[0] or 0)

    kh4_status = None
    cur.execute("SELECT to_regclass(%s)", ("public.knowledge_kh4_state",))
    if cur.fetchone()[0]:
        cur.execute(
            "SELECT answer_status FROM knowledge_kh4_state WHERE item_id=%s",
            (int(item_id),),
        )
        r2 = cur.fetchone()
        if r2:
            kh4_status = r2[0]

    return {
        "citation_count": cite_n,
        "has_text": bool(snap.get("has_text")),
        "has_sentence": bool(snap.get("has_sentence")) or cite_n > 0,
        "has_embedding": bool(snap.get("has_embedding")),
        "kh4_answer_status": kh4_status,
    }


def record_weight(
    cur,
    *,
    item_id: int,
    weight: Mapping[str, Any],
    run_id: str | None = None,
    probe_id: str | None = None,
) -> int:
    qh = query_hash_for_item(item_id)
    rid = run_id or f"kh8:item:{int(item_id)}"
    cur.execute(
        """
        INSERT INTO knowhow_evidence_weight
          (item_id, run_id, probe_id, query_hash,
           citation_count, terminal_score, contradiction_score,
           evidence_score, confidence_band, risk_flags, components)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
        RETURNING weight_id
        """,
        (
            int(item_id),
            rid,
            probe_id,
            qh,
            int(weight["citation_count"]),
            float(weight["terminal_score"]),
            float(weight["contradiction_score"]),
            float(weight["evidence_score"]),
            str(weight["confidence_band"]),
            _json(weight.get("risk_flags") or []),
            _json(weight.get("components") or {}),
        ),
    )
    return int(cur.fetchone()[0])


def latest_weight_for_item(cur, item_id: int) -> dict[str, Any] | None:
    cur.execute(
        """
        SELECT weight_id, evidence_score, confidence_band, risk_flags, components,
               citation_count, terminal_score, contradiction_score, run_id
          FROM knowhow_evidence_weight
         WHERE item_id=%s
         ORDER BY weight_id DESC
         LIMIT 1
        """,
        (int(item_id),),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "weight_id": row[0],
        "evidence_score": float(row[1]),
        "confidence_band": row[2],
        "risk_flags": row[3],
        "components": row[4],
        "citation_count": row[5],
        "terminal_score": float(row[6]),
        "contradiction_score": float(row[7]),
        "run_id": row[8],
    }


def evaluate_item_evidence(cur, snap: Mapping[str, Any]) -> dict[str, Any]:
    """auto_admit evaluate_layer(8) 入口：算權＋寫帳＋誠實 pass/fail。"""
    cur.execute("SELECT to_regclass(%s)", ("public.knowhow_evidence_weight",))
    if not cur.fetchone()[0]:
        return {"verdict": "skipped", "note": "KH8 表未建"}

    item_id = int(snap["item_id"])
    if not snap.get("has_text"):
        return {"verdict": "fail", "note": "無 item_text＝無法加權", "action": "kh8_no_text"}

    # 丙-1（核驗 F-bypass-1）：鑑別力檢定必須在 record_weight **之前**、且排除受判 item，
    # 否則判準被本次寫入之列自證污染（實證：同一交易內 ok=False 立翻 ok=True）。
    disc = population_discriminates(cur, exclude_item_id=item_id)
    inputs = gather_item_inputs(cur, item_id, snap)
    weight = compute_evidence_weight(**inputs)
    wid = record_weight(cur, item_id=item_id, weight=weight)
    band = weight["confidence_band"]
    note = (
        f"weight_id={wid} band={band} score={weight['evidence_score']} "
        f"cite={weight['citation_count']}（≠approve／≠tradable）"
    )
    if not disc["ok"]:
        # C-2 fail-closed：帳仍寫（可溯源），但**不得**回 pass——否則等同以零變異指標充當證據
        return {
            "verdict": "fail",
            "note": f"{note}｜**KH8 無鑑別力**：{disc['note']}",
            "action": "kh8_non_discriminating",
            "weight_id": wid,
            "evidence": weight,
            "discrimination": disc,
        }
    if band in PASS_BANDS:
        return {
            "verdict": "pass",
            "note": note,
            "action": "kh8_weight_recorded",
            "weight_id": wid,
            "evidence": weight,
        }
    return {
        "verdict": "fail",
        "note": note + "；insufficient→fail",
        "action": "kh8_insufficient",
        "weight_id": wid,
        "evidence": weight,
    }


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # 充足材料 → high／medium
    rich = compute_evidence_weight(
        citation_count=8,
        has_text=True,
        has_sentence=True,
        has_embedding=True,
        kh4_answer_status="eligible",
    )
    chk("rich band pass", rich["confidence_band"] in PASS_BANDS)
    chk("rich score>0.7", rich["evidence_score"] >= 0.70)

    # 僅 text、無句／無 embed → absent → fail
    thin = compute_evidence_weight(
        citation_count=0,
        has_text=True,
        has_sentence=False,
        has_embedding=False,
        kh4_answer_status=None,
    )
    chk("thin absent", thin["confidence_band"] == "absent")
    chk("thin not pass-band", thin["confidence_band"] not in PASS_BANDS)

    # ── 丙-4（核驗 F-7：新碼零自測覆蓋，而留痕曾以舊項綠燈當佐證）
    class _FakeCur:
        """純邏輯 fake：依 scripted 回傳序模擬 population_discriminates 之三次查詢。"""

        def __init__(self, bands, distincts):
            self._bands, self._distincts, self._i = bands, distincts, 0

        def execute(self, sql, args=()):
            self._sql = sql

        def fetchone(self):
            if "to_regclass" in self._sql:
                return ("public.knowhow_evidence_weight",)
            return self._distincts

        def fetchall(self):
            return self._bands

    # (1) 單一 band → 判準(1)不過
    d1 = population_discriminates(_FakeCur([("high", 100)], (1, 1, 1)))
    chk("disc: single band → not ok", d1["ok"] is False and "判準(1)" in d1["note"])
    # (2) 兩種 band 但三分量恆定 → 判準(2)不過（鎖住「加一列 low 即解閘」之洞）
    d2 = population_discriminates(_FakeCur([("high", 100), ("low", 1)], (1, 1, 1)))
    chk("disc: 2 bands but flat components → not ok", d2["ok"] is False and "判準(2)" in d2["note"])
    # (3) 兩種 band 且三分量有變異 → ok
    d3 = population_discriminates(_FakeCur([("high", 100), ("low", 30)], (2, 1, 1)))
    chk("disc: 2 bands + varying component → ok", d3["ok"] is True)
    # (4) 空母體（排除受判列後）→ not ok
    d4 = population_discriminates(_FakeCur([], (0, 0, 0)))
    chk("disc: empty population → not ok", d4["ok"] is False)

    # 風險答態降權
    risky = compute_evidence_weight(
        citation_count=5,
        has_text=True,
        has_sentence=True,
        has_embedding=True,
        kh4_answer_status="ungrounded",
    )
    chk("risky lower than rich", risky["evidence_score"] < rich["evidence_score"])
    chk("risky flag", any(str(f).startswith("kh4_") for f in risky["risk_flags"]))

    chk("hash stable", query_hash_for_item(1) == query_hash_for_item(1))
    chk("bands closed", set(CONFIDENCE_BANDS) == {"high", "medium", "low", "absent"})
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or "").split("🎯")[0].strip())
    print("公開: compute_evidence_weight / evaluate_item_evidence / record_weight")
    print("(自測: python -m augur.knowledge.evidence --selftest)")
