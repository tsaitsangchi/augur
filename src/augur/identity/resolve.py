"""resolve-or-mint 准入解析 — 外部碼→augur_id 之單一入口(ID.11 mint-on-admission/ID.43 代碼重用)。

🎯 這支在做什麼(白話):任何攝取/backfill 拿到外部碼(finmind stock_id、fred series_id…)時,經此單一入口
   換取系統永久 augur_id——先查 `entity_alias`(claim.resolve_alias):查得唯一未退役者→直接解析;
   查無→鑄造新 augur_id(identifier.mint 既有機制)＋登錄 adopted alias;
   `detect_code_reuse` 紅旗(同碼曾 retire 再現/已分屬多枚 augur_id)→**不縫合舊身**,鑄 provisional
   新身待人解析(ID.43 存續邊界截斷);重跑冪等(同碼再呼叫解析回同一枚、不重複鑄造)。
   **只重用既有四模組之函式(claim/identifier/lifecycle),不重寫其邏輯**;本檔僅 SELECT/INSERT
   (append-only ACL 型下可跑,無任何 UPDATE/DELETE)。

code_system 正名常數住本檔(#12 單一引用源):CODE_SYSTEM_FINMIND_STOCK / CODE_SYSTEM_FRED_SERIES。
守 ID.11(升級 Knowledge 前系統鑄造)· ID.43(代碼重用紅旗→provisional 不縫合)· #3(最小邊界:不動 ingest.py,
   接線屬 Phase 2 後段另呈)· #18(library 可個別 --selftest)。

自測(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.identity.resolve              # 印用途+公開入口(唯讀)
  python -m augur.identity.resolve --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations

from augur.identity import claim, identifier, lifecycle

CODE_SYSTEM_FINMIND_STOCK = "finmind:stock_id"
CODE_SYSTEM_FRED_SERIES = "fred:series_id"


def resolution_action(candidate_ids, retired_ids):
    """純判準:alias 候選 augur_id 序列(依 transaction_time)+ 已 retire 集 → (action, augur_id|None)。

    action ∈ {'mint','resolved','provisional_mint','provisional_resolved','ambiguous'}:
      mint                 — 查無候選,鑄新身(adopted)。
      resolved             — 恰一候選且無 retire 史,直接解析。
      provisional_mint     — 紅旗且無未退役候選(碼曾 retire 後再現),鑄 provisional 新身、不縫合舊身(ID.43)。
      provisional_resolved — 紅旗但恰一未退役候選(前次紅旗已鑄之身),解析回它=重跑冪等、不重複鑄造。
      ambiguous            — 紅旗且 >1 未退役候選,回最新者、零寫入(待人解析;resolution 演算 DEFER L4/5)。

    紅旗判準與 lifecycle.detect_code_reuse 同義(有 retire 史或分屬多枚 augur_id)。
    """
    distinct = list(dict.fromkeys(candidate_ids))
    if not distinct:
        return ("mint", None)
    retired = frozenset(retired_ids)
    if not retired and len(distinct) == 1:
        return ("resolved", distinct[0])
    live = [a for a in distinct if a not in retired]
    if len(live) == 1:
        return ("provisional_resolved", live[0])
    if not live:
        return ("provisional_mint", None)
    return ("ambiguous", live[-1])


def _retired_subset(cur, augur_ids):
    """候選中曾 retire 之 augur_id 子集(lifecycle 事件序為據)。"""
    if not augur_ids:
        return frozenset()
    cur.execute(
        "SELECT DISTINCT augur_id FROM identity_lifecycle_event "
        "WHERE augur_id = ANY(%s) AND event_type='retire'", (list(augur_ids),))
    return frozenset(r[0] for r in cur.fetchall())


def _register_alias(cur, augur_id, code_system, external_code, status, evidence_ref, valid_from=None):
    """登錄外部碼 alias(INSERT-only;alias_status 轉換屬人裁,本入口不 UPDATE)。"""
    cur.execute(
        "INSERT INTO entity_alias (augur_id, code_system, external_code, alias_status, "
        "valid_from, evidence_ref) VALUES (%s, %s, %s, %s, %s, %s)",
        (augur_id, code_system, external_code, status, valid_from, evidence_ref))


def resolve_or_mint(cur, code_system, external_code, entity_type, evidence_ref, actor,
                    valid_from=None):
    """外部碼→augur_id 單一入口;回 {'augur_id','action','red_flag'}。

    action ∈ {'resolved','minted','provisional_resolved','provisional_minted','ambiguous'}
    (resolution_action 之落地形:mint→minted/provisional_mint→provisional_minted)。
    red_flag=lifecycle.detect_code_reuse 判定(ID.43)。ambiguous 零寫入。
    """
    if not external_code or not str(external_code).strip():
        raise ValueError("resolve_or_mint 須具 external_code(外部碼不得為空)")
    if not actor:
        raise ValueError("resolve_or_mint 須具 actor(P4.E6 斷言主體)")
    candidates = claim.resolve_alias(cur, code_system, external_code)
    cand_ids = [c["augur_id"] for c in candidates]
    red = lifecycle.detect_code_reuse(cur, code_system, external_code)
    action, aid = resolution_action(cand_ids, _retired_subset(cur, cand_ids))
    if action == "mint":
        aid = identifier.mint(cur, entity_type, evidence_ref, actor)
        _register_alias(cur, aid, code_system, external_code, "adopted", evidence_ref, valid_from)
        action = "minted"
    elif action == "provisional_mint":
        aid = identifier.mint(cur, entity_type, evidence_ref, actor)
        _register_alias(cur, aid, code_system, external_code, "provisional", evidence_ref, valid_from)
        action = "provisional_minted"
    return {"augur_id": aid, "action": action, "red_flag": red}


def _selftest():
    """自測(零 DB/零 API;resolution_action 純紅綠,IO-bound 之 resolve_or_mint 退結構斷言)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("查無候選→mint", resolution_action([], set()) == ("mint", None))
    chk("恰一候選無 retire→resolved", resolution_action(["a"], set()) == ("resolved", "a"))
    chk("唯一候選已 retire→provisional_mint(不縫合;ID.43)",
        resolution_action(["a"], {"a"}) == ("provisional_mint", None))
    chk("retire 舊身+一未退役新身→provisional_resolved(重跑冪等、不重複鑄)",
        resolution_action(["a", "b"], {"a"}) == ("provisional_resolved", "b"))
    chk("二未退役候選→ambiguous 回最新、零寫入",
        resolution_action(["a", "b"], set()) == ("ambiguous", "b"))
    chk("候選去重保序('a','a'→單一 resolved)", resolution_action(["a", "a"], set()) == ("resolved", "a"))
    chk("紅旗判準同 detect_code_reuse:單活候選無 retire 恆非紅旗動作",
        resolution_action(["a"], set())[0] == "resolved")
    chk("code_system 常數存在且相異",
        CODE_SYSTEM_FINMIND_STOCK != CODE_SYSTEM_FRED_SERIES
        and all(":" in c for c in (CODE_SYSTEM_FINMIND_STOCK, CODE_SYSTEM_FRED_SERIES)))
    chk("公開入口皆存在", all(callable(f) for f in (resolve_or_mint, resolution_action)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.identity.resolve --selftest;免 DB 免 API)")
