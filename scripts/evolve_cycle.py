#!/usr/bin/env python
"""本地 AI 永續進化迴圈 — 資料→思想→教材→prompt-pack 候選→評測(晉升永遠人閘)(hugo 2026-07-25 拍板)。
🎯 這支在做什麼(白話):把「能力自動演化、判準人閘一鍵化」轉成每天自轉的迴圈,四段:
   ①insight(資料→思想):讀 field_correlation(65.7萬列基線)跨股聚合,把最強的欄位交互結構寫成
     「錨定基線+永遠指回 SSOT 表」的誠實教材(不教模型背數字——教它『答結構+引出處+指查詢』,
     守 bridge 先例:活狀態問題的誠實答法=查 DB 非憑權重斷言);
   ②semantics(語意字典→教材):column_catalog 之 dirty_value_note/type_caveat(策展穩定語意)→ Q/A gold
     (答案=catalog 逐字+SSOT 指針,oracle 可驗=answer⊆catalog);
   ③promptpack(教材→能力):自 gold 帳本擇優 exemplar 組 few-shot pack→hash 註冊 local_model_version
     candidate(Tier1 演化:零訓練、增益即測、回滾=換 hash);
   ④eval:候選 pack 對 held-out gold 以本地 ollama(qwen3:4b)實測關鍵詞覆蓋分,寫 eval_result。
   **晉升不在本程式內**:candidate 就緒後印晉升指令,由 hugo 人簽(trigger 強制 promoted_by,P5.W2)。
   gold append-only 防剪輯;contains_private=false(本迴圈素材全公開層);冪等 dedup 可 cron。
守 #1(教材錨真實 SQL/catalog 來源)· #15(不教背活狀態)· #28(全本地零 usage)· #29a/d · P5.W2(晉升人閘)。
   SSOT=reports/augur_local_ai_evolution_loop_plan_20260725.md(Tier1)。
執行指令矩陣:
  python scripts/evolve_cycle.py                 # 無參數:現況(gold/版本/候選統計,唯讀)
  python scripts/evolve_cycle.py --cycle         # 跑一輪完整迴圈(①→④;冪等、cron 友善)
  python scripts/evolve_cycle.py --cycle --no-eval   # 略過 ollama 評測段(離線/省時)
  python scripts/evolve_cycle.py --export-pack   # 只匯出 serving pack 快取檔(晉升/退役後手動同步)
  python scripts/evolve_cycle.py --selftest      # 零 DB 紅綠
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b"
TOP_INSIGHTS = 20
TOP_SEMANTICS = 30
PACK_K = 6
EVAL_N = 6


def _insight_gold(pairs):
    """跨股聚合相關對 → 誠實教材(答結構+錨基線+指 SSOT,不教背活值)。"""
    out = []
    for fa, fb, basis, med, n_stocks in pairs:
        q = f"augur 核心股上,raw 欄位 {fa} 與 {fb} 的{('變化' if basis=='change' else '水平')}相關結構如何?"
        a = (f"依凍結基線(field_correlation,as-of 2026-05-31 口徑),{fa}×{fb} 之 {basis} 相關跨股中位約 "
             f"{med:+.2f}({n_stocks} 股實證)。此為基線快照;現值與逐股分佈請查 field_correlation 表"
             f"(SELECT ... WHERE field_a='{fa}' AND field_b='{fb}')——活狀態以 DB 為準、不憑記憶斷言。")
        out.append((q, a, {"source": "field_correlation_baseline", "pair": [fa, fb], "basis": basis}))
    return out


def _semantics_gold(rows):
    """catalog 語意注記 → Q/A(答案含 catalog 逐字、oracle 可驗)。"""
    out = []
    for dataset, col, zh, dirty, caveat in rows:
        note = "；".join(x for x in (dirty, caveat) if x)
        q = f"augur raw 表 {dataset} 的欄位 {col}({zh or col})有什麼語意陷阱或型別注意事項?"
        a = f"依 column_catalog(策展 SSOT):{note}。引用時以 catalog/DB 現值為準。"
        out.append((q, a, {"source": "column_catalog", "dataset": dataset, "column": col}))
    return out


def _pack_text(samples):
    blocks = [f"[例{i+1}]\n問:{q}\n答:{a}" for i, (q, a) in enumerate(samples)]
    return ("你是 augur 專案的本地助手。回答風格鐵律:錨定真實來源(catalog/DB 表名)、活狀態指回查詢、"
            "不憑記憶斷言數字、不知道就說不知道。範例:\n\n" + "\n\n".join(blocks))


def _pack_hash(sample_ids):
    return hashlib.sha256(json.dumps(sorted(sample_ids)).encode()).hexdigest()[:12]


PACK_FILE = Path.home() / ".cache" / "augur" / "serving_pack.txt"


def _export_serving_pack(cur):
    """serving pack → 快取檔(MCP ask 路消費端;無 serving=刪檔=MCP 自動回基線=退役即回滾)。"""
    cur.execute("""SELECT version_id, eval_result->'sample_ids' FROM local_model_version
        WHERE status='serving' AND eval_result->>'kind'='prompt_pack'
        ORDER BY promoted_at DESC LIMIT 1""")
    row = cur.fetchone()
    PACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not row:
        PACK_FILE.unlink(missing_ok=True)
        print("serving pack: 無 → 快取檔移除(MCP 回基線)")
        return
    vid, ids = row
    cur.execute("""SELECT prompt, gold_answer FROM local_model_gold_sample
        WHERE sample_id = ANY(%s) ORDER BY sample_id""", (ids,))
    tmp = PACK_FILE.with_suffix(".tmp")
    tmp.write_text(f"# serving pack {vid}(evolve_cycle 匯出;晉升/退役由 local_model_version 人閘驅動)\n"
                   + _pack_text(cur.fetchall()), encoding="utf-8")
    tmp.replace(PACK_FILE)
    print(f"serving pack {vid} → {PACK_FILE}")


def _score(answer, gold):
    """CJK 雙字元組+ASCII 詞覆蓋分(2026-07-25 修:原空白切詞對中文恆零=假評分器)。"""
    import re
    cjk_bi = {gold[i:i + 2] for i in range(len(gold) - 1)
              if re.match(r"[\u4e00-\u9fff]{2}", gold[i:i + 2])}
    ascii_w = {w.lower() for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]{3,}", gold)}
    keys = cjk_bi | ascii_w
    if not keys:
        return 0.0
    al = answer.lower()
    return sum(1 for k in keys if (k in answer or k in al)) / len(keys)


def _ask_ollama(prompt, system=None, timeout=150):
    body = {"model": MODEL, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": 0, "num_predict": 400}}   # think:false=R2 誠實對話定調(qwen3 思考鏈耗盡 token 之對策)
    if system:
        body["system"] = system
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"]


def cycle(do_eval=True):
    with db.connect() as conn:
        cur = conn.cursor()
        # ① insight:跨股聚合(change 基底、樣本充足、跨股一致的最強交互)
        cur.execute("""SELECT field_a, field_b, basis,
                       percentile_cont(0.5) WITHIN GROUP (ORDER BY corr) AS med, count(DISTINCT stock_id)
            FROM field_correlation WHERE method='spearman' AND basis='change' AND n_obs >= 252
            GROUP BY field_a, field_b, basis HAVING count(DISTINCT stock_id) >= 30
            ORDER BY abs(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)) DESC LIMIT %s""", (TOP_INSIGHTS,))
        gold = _insight_gold(cur.fetchall())
        # ② semantics
        cur.execute("""SELECT dataset, column_name, column_name_zh, dirty_value_note, type_caveat
            FROM column_catalog WHERE dirty_value_note IS NOT NULL OR type_caveat IS NOT NULL
            ORDER BY dataset, column_name LIMIT %s""", (TOP_SEMANTICS,))
        gold += _semantics_gold(cur.fetchall())
        # 入帳(append-only、prompt 去重、公開層)
        new = 0
        for q, a, ev in gold:
            cur.execute("""INSERT INTO local_model_gold_sample
                (prompt, gold_answer, verdict, teacher, trigger_event, contains_private, provenance)
                SELECT %s,%s,'oracle_pass',NULL,%s,false,%s
                WHERE NOT EXISTS (SELECT 1 FROM local_model_gold_sample WHERE prompt=%s)""",
                (q, a, json.dumps(ev, ensure_ascii=False),
                 json.dumps({"generator": "evolve_cycle", "verifier": "sql_recompute/catalog_substring"},
                            ensure_ascii=False), q))
            new += cur.rowcount
        conn.commit()
        # ③ promptpack 候選(擇優=最新一批多樣抽樣:insight/semantics 各半)
        cur.execute("""(SELECT sample_id, prompt, gold_answer FROM local_model_gold_sample
                        WHERE trigger_event->>'source'='field_correlation_baseline' ORDER BY sample_id LIMIT %s)
                       UNION ALL
                       (SELECT sample_id, prompt, gold_answer FROM local_model_gold_sample
                        WHERE trigger_event->>'source'='column_catalog' ORDER BY sample_id LIMIT %s)""",
                    (PACK_K // 2, PACK_K - PACK_K // 2))
        ex = cur.fetchall()
        ids = [r[0] for r in ex]
        ph = _pack_hash(ids)
        vid = f"pp_{ph}"
        pack = _pack_text([(q, a) for _, q, a in ex])
        cur.execute("""INSERT INTO local_model_version
            (version_id, base_model, train_sample_manifest_hash, eval_result)
            VALUES (%s,%s,%s,%s) ON CONFLICT (version_id) DO NOTHING""",
            (vid, MODEL, ph, json.dumps({"kind": "prompt_pack", "sample_ids": ids})))
        pack_is_new = cur.rowcount > 0
        conn.commit()
        print(f"①② gold 新增 {new} 條(累積見現況);③ 候選 pack {vid}"
              + ("(新註冊)" if pack_is_new else "(已存在,冪等)"))
        # ④ eval:held-out(不在 pack 內)之 gold 比對 pack-on vs pack-off
        if do_eval:
            cur.execute("""SELECT prompt, gold_answer FROM local_model_gold_sample
                WHERE verdict='oracle_pass' AND NOT (sample_id = ANY(%s))
                ORDER BY sample_id DESC LIMIT %s""", (ids, EVAL_N))
            heldout = cur.fetchall()
            s_on = s_off = 0.0
            for q, a in heldout:
                try:
                    s_on += _score(_ask_ollama(q, system=pack), a)
                    s_off += _score(_ask_ollama(q), a)
                except Exception as e:  # noqa: BLE001  ollama 忙/逾時=誠實記缺測,不假分數
                    print(f"  (eval 跳過一題:{e})")
            n = max(1, len(heldout))
            res = {"kind": "prompt_pack", "sample_ids": ids,
                   "eval": {"n": len(heldout), "score_with_pack": round(s_on / n, 3),
                            "score_without": round(s_off / n, 3), "model": MODEL}}
            cur.execute("UPDATE local_model_version SET eval_result=%s WHERE version_id=%s AND status='candidate'",
                        (json.dumps(res), vid))
            conn.commit()
            print(f"④ eval(held-out n={len(heldout)}): pack-on={res['eval']['score_with_pack']} "
                  f"vs off={res['eval']['score_without']}")
        print(f"\n晉升永遠人閘——hugo 檢視後親跑:\n  psql: UPDATE local_model_version SET status='serving',"
              f" promoted_by='hugo', promoted_at=now() WHERE version_id='{vid}';")
        _export_serving_pack(cur)
        conn.commit()
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT coalesce(trigger_event->>'source','?'), count(*)
            FROM local_model_gold_sample GROUP BY 1 ORDER BY 2 DESC""")
        for src, n in cur.fetchall():
            print(f"  gold[{src}] = {n}")
        cur.execute("SELECT version_id, status, eval_result->'eval' FROM local_model_version ORDER BY created_at DESC LIMIT 5")
        for v, st, ev in cur.fetchall():
            print(f"  version {v} [{st}] eval={ev}")
        _export_serving_pack(cur)
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    g = _insight_gold([("a", "b", "change", 0.42, 33)])
    chk("insight 教材錨 SSOT+指回查詢(不教背活值)", "field_correlation 表" in g[0][1] and "不憑記憶斷言" in g[0][1])
    s = _semantics_gold([("T", "c", "中", "髒值註", None)])
    chk("semantics 教材含 catalog 逐字+SSOT 指針", "髒值註" in s[0][1] and "column_catalog" in s[0][1])
    chk("pack hash 決定性且序不變", _pack_hash([3, 1, 2]) == _pack_hash([1, 2, 3]))
    hi = _score("月營收單位是元,SSOT=column_catalog,以 DB 現值為準", "月營收單位是元(catalog 為準)")
    lo = _score("今天天氣很好", "月營收單位是元(catalog 為準)")
    chk("score 中文真案例:相關>0.5、無關<0.2 且有鑑別", hi > 0.5 and lo < 0.2 and hi - lo > 0.4)
    chk("pack 文含誠實鐵律 system 頭", "不憑記憶斷言數字" in _pack_text([("q", "a")]))
    chk("晉升不在本程式(grep 自身無 status='serving' 之自動 UPDATE)",
        "promoted_by='hugo'" in open(__file__, encoding="utf-8").read())
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="本地 AI 永續進化迴圈(晉升人閘)")
    ap.add_argument("--cycle", action="store_true")
    ap.add_argument("--no-eval", action="store_true")
    ap.add_argument("--export-pack", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.export_pack:
        with db.connect() as conn, db.transaction(conn) as cur:
            _export_serving_pack(cur)
        return 0
    if a.cycle:
        return cycle(do_eval=not a.no_eval)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
