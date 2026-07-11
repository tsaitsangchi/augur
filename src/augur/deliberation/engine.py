"""審議引擎狀態機 — propose(lens→qwen 結構化 claim)→ verify(oracle 裁決)之編排(P3 模組化;模式 1/9)。

🎯 這支在做什麼(白話):把「一次審議」串起來——lens 組 prompt → qwen 提結構化 claim(anchors L1 已注入)
   → ledger 逐條插庫(L2-L5 正規化)→ verifiers 逐條 oracle 裁決 → ledger 收+報告。
   **LLM 只在 propose 葉端、且提案立即被確定性層接管**;裁決全出 oracle(#15)。
   多 lens 版=同題跑 N 個 lens 各成 session(consensus 聚合見 consensus.py,MVP 後續)。

守 #15(裁決全出 oracle)· #28(唯本機 qwen、零 Claude)· #12(propose/verify 編排單一住所)。
"""
import time

from augur.advisor.ollama import make_structured_llm_fn
from augur.core import db
from augur.deliberation import ledger
from augur.deliberation.anchors import CLAIM_SCHEMA
from augur.deliberation.lens import build_prompt
from augur.deliberation.verifiers import verify_claim


def propose(topic, target_block, lens, model, n, timeout, seed=None):
    """葉端 LLM:回 [claim dict](≤n)。format schema 強制;失敗 raise(錯得大聲 #15)。
    seed(D2 誠實註記):temperature=0 貪婪解碼下解碼 seed 為 no-op——收此參數僅為未來 temp>0 模式
    預留+帳面可溯(落 options.seed;可重現量測軸=題集 seed+殘差重放,見補完計畫 §4-D2)。"""
    prompt = build_prompt(topic, target_block, lens, n)
    opts = {"temperature": 0, "num_predict": 1600}
    if seed is not None:
        opts["seed"] = int(seed)
    fn = make_structured_llm_fn(CLAIM_SCHEMA, model=model, timeout=timeout, retries=1, options=opts)
    return fn(prompt).get("claims", [])[:n]


def deliberate(topic, target_block, lens, model, n, timeout):
    """一次審議端到端:propose → 插庫(L2-L5)→ 裁決 → 收 session。回 (session_id, tally) 或 (None, None)。"""
    t0 = time.time()
    sid = ledger.new_session_id()
    claims = propose(topic, target_block, lens, model, n, timeout)
    if not claims:
        print("✗ qwen 未提出任何 claim(誠實記錄,非成功)")
        return None, None
    with db.connect() as conn:
        cur = conn.cursor()
        # target 純檔名由呼叫端傳入(target_block 內含);ledger 需 target 供 L3/L4 補全 → 從 block 解析首行
        target = _target_from_block(target_block)
        ledger.open_session(cur, sid, topic, target, model)
        ids = [ledger.insert_claim(cur, sid, c, lens, model, target) for c in claims]
        conn.commit()
    print(f"session={sid} | {len(ids)} claims(model={model} lens={lens},{time.time()-t0:.0f}s)\n")
    tally = {}
    for cid in ids:
        r = verify_claim(cid)
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        with db.connect() as conn:                              # D3:逐 claim 裁決後 heartbeat(長跑活性可證)
            c2 = conn.cursor()
            c2.execute("UPDATE deliberation_session SET heartbeat_at=now() WHERE session_id=%s", (sid,))
            conn.commit()
    with db.connect() as conn:
        cur = conn.cursor()
        ledger.close_session(cur, sid, tally)
        cur.execute("UPDATE deliberation_session SET finished_at=now(), duration_s=%s WHERE session_id=%s",
                    (round(time.time() - t0, 1), sid))          # D3:收尾寫 duration
        conn.commit()
    ledger.report(sid)
    print(f"\n總計 {time.time()-t0:.0f}s | {tally}")
    return sid, tally


def _target_from_block(target_block):
    """自 target_block('目標檔案 X(前…' 首行)取回檔名;無 target → None。"""
    if target_block and target_block.startswith("目標檔案 "):
        return target_block[len("目標檔案 "):].split("(", 1)[0].strip()
    return None


def _session_claim_rows(cur, sid, lens):
    cur.execute("SELECT claim_text, assigned_verifier, anchor, status FROM deliberation_claim "
                "WHERE session_id=%s", (sid,))
    return [{"claim_text": t, "assigned_verifier": v, "anchor": a, "status": s, "lens": lens}
            for t, v, a, s in cur.fetchall()]


def deliberate_panel(topic, target_block, lenses, model, n, timeout, *, max_rounds=3, dry_k=2):
    """多視角 panel + loop-until-dry(模式 2/4/5/6 完整版):每輪跑全部 lens 各成 session、
    consensus 聚合(三級殺權)、critic 判 dry;連續 dry_k 輪無新確定性發現才停。
    後續輪把「未覆蓋表」注入題目提示(完整性 critic 回饋)。回 {rounds, aggregate, dry}。"""
    from augur.deliberation import consensus, critic
    all_rows, seen, rounds_without_new, round_no = [], set(), 0, 0
    hint = ""
    while round_no < max_rounds and not critic.is_dry(rounds_without_new, dry_k):
        round_no += 1
        print(f"\n━━ 第 {round_no} 輪(lens={lenses}){hint and ' | 完整性提示:'+hint}━━")
        for lens in lenses:
            sid, _ = deliberate(topic + hint, target_block, lens, model, n, timeout)
            if sid:
                with db.connect() as conn, db.transaction(conn) as cur:
                    all_rows.extend(_session_claim_rows(cur, sid, lens))
        agg = consensus.aggregate(all_rows)
        fresh = critic.new_deterministic_keys(agg, seen)
        seen |= {a["key"] for a in agg if a["verdict"] in ("confirmed", "refuted")}
        rounds_without_new = 0 if fresh else rounds_without_new + 1
        uncov = critic.uncovered_tables(topic, agg)
        hint = ("(尚未驗證之相關表:" + ", ".join(uncov[:8]) + ")") if uncov else ""
        print(f"  本輪新增確定性發現 {len(fresh)};未覆蓋表 {len(uncov)};乾涸計數 {rounds_without_new}/{dry_k}")
    agg = consensus.aggregate(all_rows)
    print("\n═══ Panel 共識 ═══")
    for a in agg:
        icon = {"confirmed": "✓", "refuted": "✗", "contested": "⚡", "escalated": "⚠"}.get(a["verdict"], "?")
        print(f"  {icon} [{a['verdict']}] {a['claim_text'][:60]}(lens={','.join(a['lenses'])} 支持{a['support']}/{a['n_lens']})")
    print("  " + consensus.summarize(agg))
    return {"rounds": round_no, "aggregate": agg, "dry": critic.is_dry(rounds_without_new, dry_k)}
