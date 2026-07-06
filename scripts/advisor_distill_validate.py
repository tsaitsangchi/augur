#!/usr/bin/env python
"""S5 gold-answer 硬校驗 → SFT jsonl — 把 guard 引文/數字/出處三閘 + grounding 前置到訓練資料生成期。

🎯 這支在做什麼(白話):對每筆已生 target_response(S4 teacher gold)的 context,過**現行 guard 全閘**
   (guard_knowledge + guard_attribution + guard_empty_retrieval)+「事實斷言 token ⊂ context」grounding
   啟發式;不過即丟(絕不放流暢唬爛入訓練集=違靈魂)。通過者寫 SFT jsonl:
     {messages:[system(SYSTEM_PROMPT), user(query + 真實 context 區塊), assistant(gold target_response)]}。
   **界線-B 機械保證**:target 內任何事實斷言(數字/引文/古典出處)須能在 context 內溯源,否則作廢——
   等於把 guard 三閘前置到資料生成期(非「相信 Claude 不編」)。
   **GATE**:報告 drop rate;>40% 旗標 S4 teacher prompt 需收緊或情境設計有誤 → 回 S4 調。

   **當前狀態**:S4 gold 尚未生(target_response 全 NULL)→ 本腳本 --run 時印「無 gold 可驗」;
   --self-test 用 context 內真實 citation 之逐字片段合成 dummy gold 自測閘鏈(驗閘可用、不入訓練集)。
   guard.py 一字未動(byte-identical)——機械證明只更嚴不更鬆(Gate-2)。
守 #1(guard 前置:target 事實 ⊂ context、不編)· #6(冪等、可重跑)· #15(drop rate 誠實報告)·
   憲章 v1.35.0 guard 閉集(此處複用、零鬆)· CLAUDE #29。
   計畫 SSOT=reports/augur_advisor_selfqa_training_plan_20260706.md §S5 · §③界線-B · §⑦紅線1-3。

執行指令矩陣:
  python scripts/advisor_distill_validate.py                     # 無參數=印矩陣 + 現況(安全預設)
  python scripts/advisor_distill_validate.py --run --out data/distill/sft.jsonl   # 驗 gold、寫 SFT jsonl
  python scripts/advisor_distill_validate.py --self-test         # S4 前:用真實 citation 片段自測閘鏈可用
"""
import argparse
import json
import pathlib

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import textnorm


def _rebuild_citations(context):
    """把 context JSONB 內序列化之 citation dict 還原為 Citation / ItemCitation 物件(guard 型別感知需真物件)。"""
    from augur.philosophy.retrieval import Citation, ItemCitation
    out = []
    for d in context.get("citations", []):
        t = d.pop("__type__", "Citation")
        d.pop("via", None) if t == "Citation" else None
        try:
            out.append((ItemCitation if t == "ItemCitation" else Citation)(**{
                k: v for k, v in d.items() if k in
                (ItemCitation.__dataclass_fields__ if t == "ItemCitation" else Citation.__dataclass_fields__)}))
        except TypeError:
            continue
    return out


def _content_tokens(text):
    zh = {t for t, _ in textnorm.tokenize(text or "", "zh")}
    en = {t for t, _ in textnorm.tokenize(text or "", "en")}
    return zh | en


def grounding_ok(target, citations, floor=0.60):
    """grounding 啟發式(界線-B 收尾):target 之事實內容詞須高比例 ⊂ context(citation 原文+著作名)。
    誠實 decline 句(無實質事實斷言)天然高覆蓋或短、豁免;有大量 context 外內容詞 → 疑外插、fail。
    回 (ok, coverage)。純機械、零 usage。"""
    tt = _content_tokens(target)
    tt = {t for t in tt if len(t) >= 2}                    # 剔單字虛詞噪音
    if not tt:
        return True, 1.0
    ctx_blob = " ".join((getattr(c, "text", "") or "") + " " +
                        (getattr(c, "work_title", "") or getattr(c, "item_title", "") or "")
                        for c in citations)
    ct = _content_tokens(ctx_blob)
    covered = len(tt & ct) / len(tt)
    return covered >= floor, round(covered, 4)


def validate_one(query, target, context):
    """過 guard 全閘 + grounding;回 (passed, verdict_dict)。"""
    from augur.advisor.guard import (guard_knowledge, guard_attribution, guard_empty_retrieval,
                                     citation_numbers)
    from augur.advisor.payload import empty_payload
    cites = _rebuild_citations(context)
    issues = []
    if not cites:                                          # 空檢索路:target 必須是誠實句閉集
        v = guard_empty_retrieval(target, [])
        issues += v["issues"]
    else:
        vk = guard_knowledge(target, empty_payload(), cites, sql_numbers=citation_numbers(cites))
        va = guard_attribution(target, cites)
        issues += vk["issues"] + va["issues"]
        ok, cov = grounding_ok(target, cites)
        if not ok:
            issues.append(f"grounding 不足(界線-B):事實內容詞覆蓋 {cov} < 0.60、疑外插 context 外事實")
    return (not issues), {"pass": not issues, "issues": issues, "n_citations": len(cites)}


def _sft_record(query, target, context):
    """組 SFT jsonl 記錄:system + user(query+真實 context 區塊) + assistant(gold)。"""
    from augur.advisor.prompt import SYSTEM_PROMPT
    from augur.philosophy.retrieval import Citation, ItemCitation  # noqa: F401
    cites = _rebuild_citations(context)
    ctx_lines = [f"[{i+1}] {getattr(c,'work_title','') or getattr(c,'item_title','')}: {c.text}"
                 for i, c in enumerate(cites)] or ["(無檢索結果)"]
    user = f"問題:{query}\n\n可用真兆 context(逐字檢索):\n" + "\n".join(ctx_lines)
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
        {"role": "assistant", "content": target},
    ]}


def run(cur, out_path):
    """驗所有已生 gold、寫通過者為 SFT jsonl;回 (n_gold, n_pass, drop_rate)。"""
    cur.execute(
        "SELECT c.context_id, q.question, c.target_response, c.context "
        "FROM advisor_distill_context c JOIN advisor_distill_question q USING(question_id) "
        "WHERE c.target_response IS NOT NULL ORDER BY c.context_id")
    rows = cur.fetchall()
    if not rows:
        print("  無 gold 可驗(target_response 全 NULL——S4 teacher 尚未生)。腳本 ready、待 S4。")
        return 0, 0, 0.0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_pass = 0
    with out_path.open("w", encoding="utf-8") as f:
        for cid, query, target, context in rows:
            passed, verdict = validate_one(query, target, context)
            cur.execute("UPDATE advisor_distill_context SET validated=%s, validate_verdict=%s "
                        "WHERE context_id=%s", (passed, json.dumps(verdict, ensure_ascii=False), cid))
            if passed:
                f.write(json.dumps(_sft_record(query, target, context), ensure_ascii=False) + "\n")
                n_pass += 1
    drop = 1 - n_pass / len(rows)
    print(f"── S5 校驗:{len(rows)} gold → 通過 {n_pass}、丟棄 {len(rows)-n_pass}(drop rate {drop*100:.1f}%)")
    print(f"  SFT jsonl 寫入 {out_path}")
    if drop > 0.40:
        print(f"  ⚠ drop rate {drop*100:.1f}% > 40%(GATE):S4 teacher prompt 需收緊或情境設計有誤 → 回 S4")
    return len(rows), n_pass, drop


def self_test(cur):
    """S4 前自測:對有 citation 的 context,用其某 citation 逐字前 30 字合成 dummy gold(逐字⊂context),
    確認 guard 三閘 + grounding + jsonl 組裝可跑通(不寫 DB、不入訓練集)。"""
    cur.execute(
        "SELECT q.question, c.context FROM advisor_distill_context c "
        "JOIN advisor_distill_question q USING(question_id) WHERE c.n_citations>0 LIMIT 3")
    rows = cur.fetchall()
    if not rows:
        print("  無含 citation 之 context 可自測(先跑 S3)。")
        return
    print("── S5 self-test(dummy gold=citation 逐字片段;驗閘鏈可用)──")
    for query, context in rows:
        cites = _rebuild_citations(context)
        frag = cites[0].text[:30] if cites else ""
        dummy = f"根據語料,「{frag}」是相關的脈絡。"    # 逐字⊂context → 應過 ①;內容詞多⊂context → grounding 高
        passed, verdict = validate_one(query, dummy, context)
        rec = _sft_record(query, dummy, context)
        print(f"  Q={query[:24]}… → guard pass={passed} issues={verdict['issues'][:1]} "
              f"jsonl_ok={'messages' in rec}")
    # 反例:編造數字必被攔(證明閘會 fail、非全放行)
    if rows:
        _, context = rows[0]
        bad = "根據分析,IC 高達 0.9987,保證下週大漲。"
        passed, verdict = validate_one("測試", bad, context)
        print(f"  [反例]編造數字+未來語 → pass={passed}(應 False) issues={verdict['issues']}")


def stats(cur):
    cur.execute("SELECT count(*) FILTER (WHERE target_response IS NOT NULL), "
                "count(*) FILTER (WHERE validated), count(*) FROM advisor_distill_context")
    gold, validated, total = cur.fetchone()
    print(f"── S5 現況 ── context {total}、已生 gold {gold}、已驗 {validated}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--out", default="data/distill/sft.jsonl")
    ap.add_argument("--self-test", dest="self_test", action="store_true")
    ap.add_argument("--stats", action="store_true")
    args, _ = ap.parse_known_args()

    if not (args.run or args.self_test or args.stats):
        print(__doc__.split("執行指令矩陣:")[1])
        with db.connect() as conn, db.transaction(conn) as cur:
            stats(cur)
        return
    with db.connect() as conn, db.transaction(conn) as cur:
        if args.self_test:
            self_test(cur)
        elif args.stats:
            stats(cur)
        else:
            run(cur, pathlib.Path(args.out))


if __name__ == "__main__":
    main()
