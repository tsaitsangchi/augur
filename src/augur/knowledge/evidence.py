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

# ── D2（2026-08-01 Steward 裁決＝中庸案）：存在性判準 → 質量判準 ─────────────
# 病灶（r3 §五）：判準(1)(2) 皆「存在性」——band 種類≥2、分量 distinct≥2，可被
# 0.27% 尾巴（396/146,354，皆 depth-3 未嵌入批）同時滿足 ⇒ 結構上仍不可鑑別的
# 母體開著 KH9-first 閘。強化：band 與分量之**非眾數質量**各須 ≥ MIN_MINORITY_MASS。
MIN_MINORITY_MASS = 0.05  # 三選項 0.02/0.05/0.10 取中庸；證偽條件見 reports/w2_20260801/D2 §4


def minority_mass(counts) -> float:
    """非眾數質量＝1 − 眾數計數/總數；空集回 0.0（無質量＝無鑑別力）。純函式。"""
    vals = [int(c) for c in counts if int(c) > 0]
    total = sum(vals)
    if total <= 0:
        return 0.0
    return 1.0 - (max(vals) / total)


def discrimination_verdict(band_counts, comp_minority_masses, *, min_minority_mass=None):
    """KH8 母體鑑別力裁決——純函式（免 DB；真輸入由 population_discriminates 現查餵入）。

    ok ⇔ (1) band 種類 ≥ MIN_DISCRIMINATING_BANDS
       ∧ (1′) band 非眾數質量 ≥ 門檻（擋「加一列 low 即解閘」——存在性判準之洞、F-bypass-1 同族）
       ∧ (2′) 三分量（terminal/embed/kh4_ok）至少一者非眾數質量 ≥ 門檻
              （擋母體選擇效應：分量恆 1.0 時 band 變異只是公式常數平移）。
    恰在門檻上＝過（≥ 語意）。空母體／零質量 → ok=False（fail-closed）。
    回傳鍵向後相容：ok/bands/n/note 必在（reevaluate_kh_depths.py:83、run_kh_chain.py:83 只讀此四鍵）。
    """
    mm = MIN_MINORITY_MASS if min_minority_mass is None else float(min_minority_mass)
    counts = {str(b): int(c) for b, c in dict(band_counts).items() if int(c) > 0}
    bands = sorted(counts, key=counts.get, reverse=True)
    n = sum(counts.values())
    comp = {str(k): float(v or 0.0) for k, v in dict(comp_minority_masses).items()}
    base = {"bands": bands, "n": n, "band_minority_mass": 0.0,
            "comp_minority_masses": comp, "min_minority_mass": mm}
    if n == 0:
        return {**base, "ok": False, "note": "KH8 母體為空（排除受判列後）"}
    bmm = minority_mass(counts.values())
    base["band_minority_mass"] = round(bmm, 8)
    if len(bands) < MIN_DISCRIMINATING_BANDS:
        return {**base, "ok": False, "note": f"判準(1)不過：{n} 列僅 {bands} 一種 band"}
    if bmm < mm:
        return {**base, "ok": False,
                "note": f"判準(1′)不過：band 非眾數質量 {bmm:.6f} < {mm}"
                        f"（{n} 列；尾巴不構成鑑別力）"}
    cmax = max(comp.values(), default=0.0)
    if cmax < mm:
        return {**base, "ok": False,
                "note": f"判準(2′)不過：三分量非眾數質量皆 < {mm}（{comp}）"
                        "——母體選擇效應未解，band 變異不足以證明鑑別力"}
    return {**base, "ok": True,
            "note": f"band {bands}；band 非眾數質量 {bmm:.4f}；分量非眾數質量 {comp}（n={n}）"}


# 批次級凍結快照：判準於「批次／進程開頭算一次」即凍結，之後不隨批內寫入而變。
# 三次獨立核驗（2026-07-30）證兩病同源：(a) `record_weight` 在判準消費前無條件寫列 ⇒
# 批中第一個 fail 就替後面所有 item 開閘（同交易 peer 污染，`exclude_item_id` 擋不到）；
# (b) 每 item 每層各重算一次 146k 全表掃（4.9–7.7s）⇒ 145,949 件約 17 天。
# 凍結同時解掉兩者：判準不被受判資料污染，且每進程只掃一次。
_frozen_population: dict[str, Any] = {}


def frozen_population_verdict(cur, *, refresh: bool = False) -> dict[str, Any]:
    """取本批次凍結之母體鑑別力判準（首呼計算並凍結；`refresh=True` 明示重取）。"""
    if refresh or not _frozen_population:
        _frozen_population.clear()
        _frozen_population.update(population_discriminates(cur))
    return dict(_frozen_population)


def population_discriminates(cur, *, exclude_item_id: int | None = None) -> dict[str, Any]:
    """KH8 母體是否具鑑別力——取數後委派 discrimination_verdict（判準全文見該函式）。

    `exclude_item_id`：排除正在受判之 item（防自證污染，原語意不變）。
    表未建／空表 → ok=False（fail-closed，原語意不變）。
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
    band_counts = {r[0]: int(r[1]) for r in cur.fetchall()}
    # 三分量非眾數質量（單趟；回一列三 float，與舊「一列三 distinct 數」同形——FakeCur 相容）
    cur.execute(
        f"""WITH src AS (SELECT components->>'terminal' AS t, components->>'embed' AS e,
                                components->>'kh4_ok' AS k
                           FROM knowhow_evidence_weight {where})
            SELECT (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY t) x),
                   (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY e) y),
                   (SELECT 1.0-max(c)::float8/sum(c) FROM (SELECT count(*) c FROM src GROUP BY k) z)""",
        args,
    )
    t, e, k = ((float(x) if x is not None else 0.0) for x in cur.fetchone())
    return discrimination_verdict(band_counts, {"terminal": t, "embed": e, "kh4_ok": k})

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
    """消費側讀最新權重：優先 honest view 之 usable band（M-G14）。

    `confidence_band`＝`confidence_band_usable`（母體無鑑別力時為 None）；
    raw 僅以 `confidence_band_raw` 暴露供診斷，不得當通過訊號。
    """
    cur.execute(
        "SELECT to_regclass(%s)", ("public.knowhow_evidence_weight_honest",)
    )
    if cur.fetchone()[0]:
        cur.execute(
            """
            SELECT weight_id, evidence_score,
                   confidence_band_usable, confidence_band_raw,
                   risk_flags, components,
                   citation_count, terminal_score, contradiction_score, run_id
              FROM knowhow_evidence_weight_honest
             WHERE item_id=%s
             ORDER BY weight_id DESC
             LIMIT 1
            """,
            (int(item_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        usable, raw = row[2], row[3]
        return {
            "weight_id": row[0],
            "evidence_score": float(row[1]),
            "confidence_band": usable,
            "confidence_band_usable": usable,
            "confidence_band_raw": raw,
            "risk_flags": row[4],
            "components": row[5],
            "citation_count": row[6],
            "terminal_score": float(row[7]),
            "contradiction_score": float(row[8]),
            "run_id": row[9],
        }
    # view 未建時退基表（寫入軸／舊庫）；消費遷移後應走 honest
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
    disc = frozen_population_verdict(cur)  # 批次開頭凍結：不受本批寫入污染
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

        def __init__(self, bands, masses):
            self._bands, self._masses, self._i = bands, masses, 0

        def execute(self, sql, args=()):
            self._sql = sql

        def fetchone(self):
            if "to_regclass" in self._sql:
                return ("public.knowhow_evidence_weight",)
            return self._masses

        def fetchall(self):
            return self._bands

    # (1) 單一 band → 判準(1)不過
    d1 = population_discriminates(_FakeCur([("high", 100)], (0.0, 0.0, 0.0)))
    chk("disc: single band → not ok", d1["ok"] is False and "判準(1)" in d1["note"])
    # (2) 兩種 band 但尾巴僅 1 列 → 判準(1′)不過（D2：質量門檻鎖「加一列 low 即解閘」之洞）
    d2 = population_discriminates(_FakeCur([("high", 100), ("low", 1)], (0.0, 0.0, 0.0)))
    chk("disc: 尾巴 1 列不解閘 → not ok", d2["ok"] is False and "判準(1′)" in d2["note"])
    # (3) 兩種 band 質量夠且分量有質量 → ok
    d3 = population_discriminates(_FakeCur([("high", 100), ("low", 30)], (0.0, 0.23, 0.0)))
    chk("disc: 2 bands + varying component → ok", d3["ok"] is True)
    # (4) 空母體（排除受判列後）→ not ok
    d4 = population_discriminates(_FakeCur([], (0.0, 0.0, 0.0)))
    _frozen_population.clear()
    f1 = frozen_population_verdict(_FakeCur([("high", 100)], (0.0, 0.0, 0.0)))
    f2 = frozen_population_verdict(_FakeCur([("high", 100), ("low", 30)], (0.0, 0.23, 0.0)))
    chk("凍結後不隨批內變化（第二次呼叫仍回首次判準）", f1["ok"] is False and f2["ok"] is False)
    f3 = frozen_population_verdict(_FakeCur([("high", 100), ("low", 30)], (0.0, 0.23, 0.0)), refresh=True)
    chk("refresh=True 得明示重取", f3["ok"] is True)
    _frozen_population.clear()
    chk("disc: empty population → not ok", d4["ok"] is False)

    # D2 真直方圖雙向紅：live 直方圖（2026-08-01 現查凍結為 fixture）於三選項下必 fail；
    # 合成有鑑別力分佈必 ok——雙向都得動，防字面斷言假綠。
    live_bands = {"high": 145958, "absent": 380, "low": 16}
    live_comp = {"terminal": 0.0, "embed": 0.00270577, "kh4_ok": 0.00270577}
    for th in (0.02, 0.05, 0.10):
        chk(f"live 直方圖 θ={th} → fail",
            discrimination_verdict(live_bands, live_comp, min_minority_mass=th)["ok"] is False)
    chk("合成有鑑別力分佈 θ=0.05 → ok",
        discrimination_verdict({"high": 90000, "low": 10000},
                               {"terminal": 0.0, "embed": 0.10, "kh4_ok": 0.0},
                               min_minority_mass=0.05)["ok"] is True)
    chk("band 質量夠但分量全平 → fail（判準 2′）",
        discrimination_verdict({"high": 90000, "low": 10000},
                               {"terminal": 0.0, "embed": 0.0, "kh4_ok": 0.0},
                               min_minority_mass=0.05)["ok"] is False)
    chk("恰在門檻上 → ok（≥ 語意）",
        discrimination_verdict({"a": 95, "b": 5}, {"embed": 0.05},
                               min_minority_mass=0.05)["ok"] is True)
    chk("回傳鍵向後相容", {"ok", "bands", "n", "note"} <=
        set(discrimination_verdict({"high": 1}, {})))

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
