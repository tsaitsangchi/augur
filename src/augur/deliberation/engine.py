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


def propose(topic, target_block, lens, model, n, timeout):
    """葉端 LLM:回 [claim dict](≤n)。format schema 強制;失敗 raise(錯得大聲 #15)。"""
    prompt = build_prompt(topic, target_block, lens, n)
    fn = make_structured_llm_fn(CLAIM_SCHEMA, model=model, timeout=timeout, retries=1,
                                options={"temperature": 0, "num_predict": 1600})
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
    with db.connect() as conn:
        cur = conn.cursor()
        ledger.close_session(cur, sid, tally)
        conn.commit()
    ledger.report(sid)
    print(f"\n總計 {time.time()-t0:.0f}s | {tally}")
    return sid, tally


def _target_from_block(target_block):
    """自 target_block('目標檔案 X(前…' 首行)取回檔名;無 target → None。"""
    if target_block and target_block.startswith("目標檔案 "):
        return target_block[len("目標檔案 "):].split("(", 1)[0].strip()
    return None
