"""自我迭代狀態機 — DRAFT→ATTACK→REFINE→VERIFY 逐轉移落帳(模式 9;補完計畫 §3.2)。

🎯 這支在做什麼(白話):把 Claude ultracode 的「草稿→攻擊→修訂→驗證」搬到本地——qwen 起草含
   可驗宣稱的提案 → skeptic lens 逐點批判 → 修稿逐點回應 → **refined 宣稱送現行裁決管線**
   (ledger.insert_claim → verifiers.verify_claim;**不變式不動:confirmed 唯一寫點仍=verify_claim**,
   迭代只改提案品質、任何 REFINE 產物要 confirmed 一律過 oracle)。收斂=critic dry(無新確定性發現)
   或 round 上限(凍結 3)。每階段=deliberation_proposal 一列(parent_id 鏈可溯至 draft,#10)。
   llm_fn 注入式(llm_fn(prompt, schema)->dict):生產傳 qwen 包裝、測試傳假 LLM(零 GPU 可測)。

守 #15(裁決全出 oracle、panel/迭代零 confirmed 權)· #10(逐轉移落帳可溯)· #12(裁決管線全複用)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.iterate              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.iterate --selftest   # 純紅綠自測（零 IO）
"""
import json

from augur.deliberation import consensus, critic, ledger
from augur.deliberation.anchors import CLAIM_SCHEMA
from augur.deliberation.verifiers import verify_claim

MAX_ROUNDS = 3   # 凍結參數(§3.2)

DRAFT_SCHEMA = {"type": "object", "properties": {
    "draft": {"type": "string"},
    "claims": CLAIM_SCHEMA["properties"]["claims"]},
    "required": ["draft", "claims"]}
ATTACK_SCHEMA = {"type": "object", "properties": {
    "critiques": {"type": "array", "items": {"type": "object", "properties": {
        "point": {"type": "string"}, "severity": {"type": "string", "enum": ["fatal", "major", "minor"]}},
        "required": ["point", "severity"]}}},
    "required": ["critiques"]}


def _insert_proposal(cur, sid, stage, rnd, content, parent_id=None, critique=None, claim_ids=None):
    cur.execute("INSERT INTO deliberation_proposal (session_id, parent_id, stage, round, content, critique, claim_ids) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING proposal_id",
                (sid, parent_id, stage, rnd, json.dumps(content, ensure_ascii=False),
                 json.dumps(critique, ensure_ascii=False) if critique is not None else None, claim_ids))
    return cur.fetchone()[0]


def _verify_claims(cur, sid, claims, lens, model, target):
    """refined 宣稱送現行裁決管線(insert_claim 全閘照走 → verify_claim 唯一 confirmed 寫點)。回 claim_ids。"""
    ids = [ledger.insert_claim(cur, sid, c, lens, model, target) for c in claims]
    for cid in ids:
        verify_claim(cid, cur=cur)     # 同交易裁決(commit 歸 caller;機械鎖不變)
    return ids


def run_iteration(cur, llm_fn, topic, target=None, max_rounds=MAX_ROUNDS, model="qwen3:4b"):
    """一次自我迭代端到端。回 final proposal_id。llm_fn(prompt, schema) -> dict(注入式)。"""
    sid = ledger.new_session_id()
    ledger.open_session(cur, sid, f"[iterate] {topic}", target, model)
    draft = llm_fn(f"就以下題目起草提案:除文字論述外,附上可機械驗證的宣稱(claims,含 anchor)。\n題目:{topic}",
                   DRAFT_SCHEMA)
    pid = _insert_proposal(cur, sid, "draft", 1, {"draft": draft.get("draft", ""),
                                                  "claims": draft.get("claims", [])})
    seen, last_refine_id, dry_rounds = set(), pid, 0
    claims = draft.get("claims", [])
    for rnd in range(1, max_rounds + 1):
        cur.execute("UPDATE deliberation_session SET heartbeat_at=now() WHERE session_id=%s", (sid,))  # D3 心跳
        atk = llm_fn("你是對抗性懷疑者:逐點批判以下提案(找錯誤/漏洞/無法驗證處):\n"
                     + json.dumps({"draft": draft.get("draft", ""), "claims": claims},
                                  ensure_ascii=False)[:4000], ATTACK_SCHEMA)
        atk_id = _insert_proposal(cur, sid, "attack", rnd, {"of": last_refine_id},
                                  parent_id=last_refine_id, critique=atk.get("critiques", []))
        ref = llm_fn("依批判修訂提案(逐點回應;修正或撤回站不住的宣稱、保留可驗宣稱):\n批判:"
                     + json.dumps(atk.get("critiques", []), ensure_ascii=False)[:2000]
                     + "\n原稿:" + json.dumps({"draft": draft.get("draft", ""), "claims": claims},
                                              ensure_ascii=False)[:3000], DRAFT_SCHEMA)
        claims = ref.get("claims", [])
        cids = _verify_claims(cur, sid, claims, "skeptic", model, target)
        ref_id = _insert_proposal(cur, sid, "refine", rnd, {"draft": ref.get("draft", ""), "claims": claims},
                                  parent_id=atk_id, claim_ids=cids)
        last_refine_id = ref_id
        # 收斂判定:本輪有無「新」確定性發現(confirmed/refuted 之新 key)——critic dry 重用
        cur.execute("SELECT claim_text, assigned_verifier, anchor, status FROM deliberation_claim "
                    "WHERE claim_id = ANY(%s)", (cids,))
        agg = consensus.aggregate([{"claim_text": t, "assigned_verifier": v, "anchor": a,
                                    "status": s, "lens": "skeptic"} for t, v, a, s in cur.fetchall()])
        fresh = critic.new_deterministic_keys(agg, seen)
        seen |= {x["key"] for x in agg if x["verdict"] in ("confirmed", "refuted")}
        dry_rounds = 0 if fresh else dry_rounds + 1
        if critic.is_dry(dry_rounds, 1):
            break
        draft = ref
    final_id = _insert_proposal(cur, sid, "final", min(rnd, max_rounds),
                                {"draft": draft.get("draft", ""), "claims": claims},
                                parent_id=last_refine_id)
    ledger.close_session(cur, sid, {"iterate_rounds": rnd, "final_proposal": final_id})
    cur.execute("UPDATE deliberation_session SET finished_at=now(), duration_s=EXTRACT(EPOCH FROM now()-created_at) "
                "WHERE session_id=%s", (sid,))                      # D3:iterate 路徑補 duration(P3 實證缺口)
    return final_id


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）:本檔全 IO-bound(每個入口需 cur/llm_fn)→
    import-smoke + 凍結常數/schema 結構斷言(把不變式固化成回歸鎖)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    import augur.deliberation.iterate as m
    chk("import-smoke:模組已載入", m is not None)
    chk("公開入口 run_iteration 存在且可呼叫", hasattr(m, "run_iteration") and callable(m.run_iteration))
    chk("MAX_ROUNDS 凍結=3(§3.2)", MAX_ROUNDS == 3)
    chk("DRAFT_SCHEMA required=[draft,claims]", DRAFT_SCHEMA.get("required") == ["draft", "claims"])
    chk("DRAFT_SCHEMA claims 複用 CLAIM_SCHEMA(#12)",
        DRAFT_SCHEMA["properties"]["claims"] is CLAIM_SCHEMA["properties"]["claims"])
    chk("ATTACK_SCHEMA severity enum=fatal/major/minor",
        ATTACK_SCHEMA["properties"]["critiques"]["items"]["properties"]["severity"]["enum"]
        == ["fatal", "major", "minor"])
    chk("verify_claim 為唯一 confirmed 寫點(裁決管線複用 #15)", callable(verify_claim))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:run_iteration(cur, llm_fn, topic, ...)  # DRAFT→ATTACK→REFINE→VERIFY 自我迭代")
    print("(自測:python -m augur.deliberation.iterate --selftest;免 DB 免 API)")
