"""lifecycle 事件記錄與 lineage 重建 — 概念存續序(ID.40-44)。

🎯 這支在做什麼(白話):把「這個 identifier 後來發生了什麼」寫成 append-only 事件序——
   event_type ∈ {mint,merge,split,retire,relist,redirect,correct,tombstone,de_identify,
   expire,settle,convert,redeem}(**開放集**,故 DB 不寫死全值域 CHECK);載所涉 augur_id、
   redirect_target(合併/轉指目標)、lineage_parent、雙時間、Evidence 引用、actor。
   **merge/split/retire/relist/correct(ID.40 更正)+ settle/expire/convert/redeem(ID.44 DynamicEntity 終結)
   之 evidence_ref 為 NOT NULL 硬義務**(Python 與 DB CHECK 雙鎖)。
   事件只失效不刪除;使「任一 as-of 此 identifier 指向哪一存續個體」可重建(resolve_as_of 追 redirect/
   merge 鏈)。並偵測**代碼重用紅旗**(ID.43):同一外部碼於 retire 後再現→登錄 provisional 待解析、不逕縫合。

DDL 單一權威=scripts/migrate_identity_ddl.py(identity_lifecycle_event append-only 硬化 + evidence CHECK)。
承接 T.34 下市→retire、T.3/T.4/T.5 之 settle/expire/convert/redeem 終結(ID.44 DynamicEntity)。
守 ID.40(Evidence 義務)· ID.41(轉指/lineage 不變式)· ID.42(tombstone/去識別化)· ID.43(代碼重用)· #18。

自測(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.identity.lifecycle              # 印用途+公開入口(唯讀)
  python -m augur.identity.lifecycle --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations

# Evidence NOT NULL 硬義務之事件型別;其餘型別 evidence_ref 可選。event_type 本身為開放集、不鎖全值域。
# ID.40:merge/split/retire/relist + correct(更正);ID.44:settle/expire/convert/redeem(DynamicEntity 終結)。
EVIDENCE_REQUIRED = frozenset({"merge", "split", "retire", "relist", "correct",
                               "settle", "expire", "convert", "redeem"})
# resolve_as_of 追鏈之轉指型別(指向存續後繼個體)。
_REDIRECTING = ("merge", "redirect")


def evidence_required(event_type) -> bool:
    """純判準:此 event_type 之 evidence_ref 是否為硬義務(ID.40)。"""
    return event_type in EVIDENCE_REQUIRED


def record_event(cur, augur_id, event_type, actor, evidence_ref=None,
                 redirect_target=None, lineage_parent=None, valid_time=None, note=None) -> int:
    """登錄一枚 lifecycle 事件;回 event_id。append-only(只失效不刪除)。

    merge/split/retire/relist/correct(ID.40)+ settle/expire/convert/redeem(ID.44)強制 evidence_ref;
    actor 為硬義務(斷言主體)。event_type 為開放集(不校驗值域),但 DB 端仍以 partial evidence CHECK
    鎖住上述型別之 Evidence 義務。
    """
    if not actor:
        raise ValueError("record_event 須具 actor(斷言主體)")
    if evidence_required(event_type) and not evidence_ref:
        raise ValueError(
            f"event_type={event_type!r} 為 Evidence 硬義務(ID.40):"
            "merge/split/retire/relist 須具 evidence_ref")
    cur.execute(
        "INSERT INTO identity_lifecycle_event (augur_id, event_type, redirect_target, "
        "lineage_parent, valid_time, evidence_ref, actor, note) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING event_id",
        (augur_id, event_type, redirect_target, lineage_parent, valid_time,
         evidence_ref, actor, note))
    return cur.fetchone()[0]


def resolve_as_of(cur, augur_id, as_of, _depth=0):
    """重建 as_of 當時 augur_id 指向之存續個體(ID.41):追 redirect/merge 鏈(transaction_time ≤ as_of)。

    無後繼轉指即回原 augur_id;_depth 上限 64 防環(資料異常時 fail-safe 回當前節點,不無限遞迴)。
    ORDER BY 次序鍵含 event_id DESC 破 tie:同一交易內多枚轉指(transaction_time 相同,now() 交易內恆等)
    仍以 bigserial event_id 單調決定最新,as-of lineage 重建結果確定。
    """
    if _depth > 64:
        return augur_id
    cur.execute(
        "SELECT redirect_target FROM identity_lifecycle_event "
        "WHERE augur_id=%s AND event_type = ANY(%s) AND redirect_target IS NOT NULL "
        "AND transaction_time <= %s ORDER BY transaction_time DESC, event_id DESC LIMIT 1",
        (augur_id, list(_REDIRECTING), as_of))
    r = cur.fetchone()
    if r is None or r[0] is None:
        return augur_id
    return resolve_as_of(cur, r[0], as_of, _depth + 1)


def detect_code_reuse(cur, code_system, external_code) -> bool:
    """代碼重用紅旗(ID.43):同一外部碼曾繫之 augur_id 有 retire 歷史(或已分屬多枚 augur_id)→ True。

    True=此外部碼再現名冊時須登錄 provisional 待解析、不得逕縫合回舊 augur_id(存續邊界截斷)。
    """
    cur.execute(
        "SELECT DISTINCT augur_id FROM entity_alias WHERE code_system=%s AND external_code=%s",
        (code_system, external_code))
    aids = [r[0] for r in cur.fetchall()]
    if not aids:
        return False
    cur.execute(
        "SELECT count(*) FROM identity_lifecycle_event "
        "WHERE augur_id = ANY(%s) AND event_type='retire'", (aids,))
    retired = cur.fetchone()[0] > 0
    return retired or len(aids) > 1


def _selftest():
    """自測(零 DB/零 API;IO-bound 之 record/resolve/detect 退 import-smoke,Evidence 義務純紅綠)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("evidence_required merge/split/retire/relist/correct→True(ID.40 含更正)",
        all(evidence_required(x) for x in ("merge", "split", "retire", "relist", "correct")))
    chk("evidence_required settle/expire/convert/redeem→True(ID.44 DynamicEntity 終結)",
        all(evidence_required(x) for x in ("settle", "expire", "convert", "redeem")))
    chk("evidence_required mint/redirect/tombstone/de_identify→False(非硬義務型別)",
        not any(evidence_required(x) for x in ("mint", "redirect", "tombstone", "de_identify")))
    chk("EVIDENCE_REQUIRED = ID.40 更正型 + ID.44 終結型(9 型別、非「恰四型別」)",
        EVIDENCE_REQUIRED == {"merge", "split", "retire", "relist", "correct",
                              "settle", "expire", "convert", "redeem"})
    chk("公開入口皆存在",
        all(callable(f) for f in (record_event, resolve_as_of, detect_code_reuse, evidence_required)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.identity.lifecycle --selftest;免 DB 免 API)")
