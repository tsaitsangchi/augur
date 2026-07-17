"""identity claim 一級介面 — 跨來源同一性斷言(ID.30-32)。

🎯 這支在做什麼(白話):把「A 來源的這個 ≡ B 來源的那個」寫成**攜四要件的一級 claim**,不以裸字串 join
   / 欄位字面相等逕推定跨體系同一——四要件:(a) 二系統 augur_id 端點對、(b) 判準引用(Layer 2 條款,
   如 ONT T.1)、(c) Evidence 引用、(d) Confidence 槽位(語義填充 DEFER Layer 4,本輪僅存槽)。
   **append-only、衝突 claim 並存並顯式標記(禁 last-write-wins)**;完整 Knowledge 五元組由 Layer 4
   KS.20 承接。另提供經 `entity_alias` 之 provisional 解析(外部碼→候選 augur_id,可能 >1=待解析、
   禁逕縫合)。

DDL 單一權威=scripts/migrate_identity_ddl.py(identity_claim append-only 硬化)。
守 ID.30(四要件)· ID.31(claim 為 Knowledge)· ID.32(唯一權威表徵之結構前提)· #18。

自測(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.identity.claim              # 印用途+公開入口(唯讀)
  python -m augur.identity.claim --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations

# Confidence 為 L3 之 nullable 不透明槽位:值域權威住 L4(KS.31 核心鏈 + 底/頂錨,Annex CM),
# 序/傳播/消費門檻語義 DEFER Layer 4 KS.30-39。**L3 不 pin L4 值域**(避免單一權威漂移:L4 增一級
# 不致 L3 INSERT 失敗;逾越「僅槽位存在」由 L3 pin L4 亦違本層分界)——本層僅守槽位型別(None 或非空字串)。


def valid_confidence(level) -> bool:
    """L3 槽位型別判準:None(過渡期由 L4 KS.20/KS.38 推定)或非空字串(不透明,值域承接 L4)。

    **不校驗五級值域**——值域/語義權威住 L4;L3 pin L4 值域=單一權威漂移(issue:ID.30(d))。
    """
    return level is None or (isinstance(level, str) and bool(level.strip()))


def assert_claim(cur, augur_id_a, augur_id_b, criterion_ref, evidence_ref, asserted_by,
                 confidence_level=None, confidence_method_ref=None, valid_time=None) -> int:
    """登錄一枚 identity claim(四要件);回 claim_id。append-only(不覆寫既有衝突 claim)。

    criterion_ref / evidence_ref / asserted_by 為硬義務(ID.30 四要件與斷言主體);
    confidence_level 為不透明槽位(值域/語義承接 L4,L3 不 pin);僅槽位型別(None 或非空字串)校驗。
    """
    if not criterion_ref:
        raise ValueError("assert_claim 須具 criterion_ref(ID.30 判準引用四要件之一)")
    if not evidence_ref:
        raise ValueError("assert_claim 須具 evidence_ref(ID.30 Evidence 引用四要件之一)")
    if not asserted_by:
        raise ValueError("assert_claim 須具 asserted_by(斷言主體)")
    if not valid_confidence(confidence_level):
        raise ValueError(
            f"confidence_level={confidence_level!r} 非法槽位型別;須 None 或非空字串"
            "(值域/語義承接 Layer 4 KS.30-39,L3 不 pin L4 值域)")
    cur.execute(
        "INSERT INTO identity_claim (augur_id_a, augur_id_b, criterion_ref, evidence_ref, "
        "confidence_level, confidence_method_ref, asserted_by, valid_time) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING claim_id",
        (augur_id_a, augur_id_b, criterion_ref, evidence_ref, confidence_level,
         confidence_method_ref, asserted_by, valid_time))
    return cur.fetchone()[0]


def claims_for(cur, augur_id):
    """回所有觸及 augur_id 之 claim(任一端點),依 transaction_time;衝突 claim 並存、不做 last-write-wins。"""
    cur.execute(
        "SELECT claim_id, augur_id_a, augur_id_b, criterion_ref, evidence_ref, "
        "confidence_level, asserted_by, transaction_time FROM identity_claim "
        "WHERE augur_id_a=%s OR augur_id_b=%s ORDER BY transaction_time", (augur_id, augur_id))
    return [{"claim_id": r[0], "augur_id_a": r[1], "augur_id_b": r[2], "criterion_ref": r[3],
             "evidence_ref": r[4], "confidence_level": r[5], "asserted_by": r[6],
             "transaction_time": r[7]} for r in cur.fetchall()]


def resolve_alias(cur, code_system, external_code):
    """外部碼→候選 augur_id(provisional 解析;經 entity_alias,禁裸字串 join 逕充同一)。

    回候選 list(可能 >1=代碼重用/歧義待解析,見 lifecycle.detect_code_reuse);空 list=未登錄。
    resolution 演算(相似度/比對/批次)DEFER Layer 4/5。
    """
    cur.execute(
        "SELECT augur_id, alias_status, valid_from, valid_to, transaction_time FROM entity_alias "
        "WHERE code_system=%s AND external_code=%s ORDER BY transaction_time",
        (code_system, external_code))
    return [{"augur_id": r[0], "alias_status": r[1], "valid_from": r[2],
             "valid_to": r[3], "transaction_time": r[4]} for r in cur.fetchall()]


def _selftest():
    """自測(零 DB/零 API;IO-bound 之 assert/resolve 退 import-smoke,Confidence 值域純紅綠)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("valid_confidence None(過渡→L4 推定)→True", valid_confidence(None))
    chk("valid_confidence L4 值皆為不透明槽位、通過(不 pin 值域)",
        all(valid_confidence(x) for x in ("INSUF", "LOW", "MODERATE", "STRONG", "DETERMINISTIC")))
    chk("valid_confidence 未來 L4 增級(如 HIGH)亦通過→L3 不 pin L4 值域(issue ID.30(d))",
        valid_confidence("HIGH"))
    chk("valid_confidence 空字串→False(非有效槽位值)", not valid_confidence(""))
    chk("valid_confidence 非字串(int)→False(僅守槽位型別)", not valid_confidence(123))
    chk("公開入口皆存在",
        all(callable(f) for f in (assert_claim, claims_for, resolve_alias, valid_confidence)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.identity.claim --selftest;免 DB 免 API)")
