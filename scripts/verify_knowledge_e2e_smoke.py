#!/usr/bin/env python
"""知識管線端到端煙測 — v1.40.0「暢通不變式」的機械判定器(e2e 主計畫 §2.3/§6.6,P3 收尾)。

🎯 這支在做什麼(白話):用一條 sentinel(公版短句+唯一 nonce,domain='smoke_test')走真實管線——
   manual 導管入庫(acquire_local_files,#12 復用)→ 切句 → concordance → 嵌入 → 檢索——機械斷言:
   ① 正向:帶 smoke_test 域授權檢索 nonce → 逐字 byte-equal 命中(--with-llm 加 advise() 輸出含逐字引用);
   ② fail-closed 反向:private 對照列(access_scope='local_private'、無 owner)不可被域授權檢索到;
   ③ 語料隔離:smoke 前後 term_affinity/term_corpus_stats 列數不變(smoke 域零列進正式統計);
   ④ --clean 拆除(冪等)。**exit 0=暢通;破=管線債,修復優先於擴容(憲章 v1.40.0)**。
   sentinel 文本=真實公版句(禁 AI 生成文本作 sentinel,A-17)。

守 憲章 v1.40.0(暢通=煙測機械判定)· #1(sentinel=公版逐字)· #12(全程走既有 builder/導管)· #15。
   SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §2.3/§6.6。

執行指令矩陣:
  python scripts/verify_knowledge_e2e_smoke.py                    # 無參數:印矩陣+上次煙測狀態(唯讀)
  python scripts/verify_knowledge_e2e_smoke.py --run              # 全鏈:入庫→sentences→concordance→embed→三斷言→clean
  python scripts/verify_knowledge_e2e_smoke.py --run --with-llm   # 加末段:advise() 對 nonce 提問、輸出含逐字引用
  python scripts/verify_knowledge_e2e_smoke.py --run --keep       # 保留 sentinel 除錯(後續手動 --clean)
  python scripts/verify_knowledge_e2e_smoke.py --clean            # 拆除 smoke_test 域全部列(冪等)
  python scripts/verify_knowledge_e2e_smoke.py --run --json       # 機器可讀(exit 0=綠=暢通)
"""
import argparse
import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
DOMAIN = "smoke_test"
# sentinel 底文=真實公版句(Adam Smith, Wealth of Nations, 1776;公版無虞、en 走 DAG en 節點)
_PD_BASE = ("It is not from the benevolence of the butcher, the brewer, or the baker, "
            "that we expect our dinner, but from their regard to their own interest.")


def _counts(cur):
    out = {}
    for t in ("knowledge_term_affinity", "knowledge_term_corpus_stats"):
        cur.execute(f"SELECT count(*) FROM {t}")
        out[t] = cur.fetchone()[0]
    return out


def _sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-400:]


def clean():
    """拆除 smoke_test 域全部痕跡(冪等;順序守 FK)。"""
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT item_id FROM knowledge_item WHERE domain=%s", (DOMAIN,))
        ids = [r[0] for r in cur.fetchall()]
        if ids:
            cur.execute("DELETE FROM knowledge_sentence_embedding WHERE sent_id IN "
                        "(SELECT s.sent_id FROM knowledge_sentence s JOIN knowledge_item_text t "
                        " ON t.itext_id=s.itext_id WHERE t.item_id = ANY(%s))", (ids,))
            cur.execute("DELETE FROM knowledge_concordance WHERE sent_id IN "
                        "(SELECT s.sent_id FROM knowledge_sentence s JOIN knowledge_item_text t "
                        " ON t.itext_id=s.itext_id WHERE t.item_id = ANY(%s))", (ids,))
            cur.execute("DELETE FROM knowledge_sentence WHERE itext_id IN "
                        "(SELECT itext_id FROM knowledge_item_text WHERE item_id = ANY(%s))", (ids,))
            cur.execute("DELETE FROM knowledge_fulltext_status WHERE item_id = ANY(%s)", (ids,))
            cur.execute("DELETE FROM knowledge_item_text WHERE item_id = ANY(%s)", (ids,))
            cur.execute("DELETE FROM knowledge_item WHERE item_id = ANY(%s)", (ids,))
        cur.execute("DELETE FROM knowledge_staging WHERE source_key IN "
                    "(SELECT source_key FROM knowledge_source WHERE domain=%s)", (DOMAIN,))
        conn.commit()
    print(f"✓ clean:smoke_test 域 {len(ids)} item 及全下游已拆(冪等)")


def run(with_llm=False, keep=False, as_json=False):
    nonce = f"smokenonce{uuid.uuid4().hex[:8]}"
    pub_text = f"{_PD_BASE} [{nonce}]"
    priv_text = f"{_PD_BASE} [private-{nonce}]"
    results = []

    def check(name, ok, detail=""):
        results.append({"check": name, "ok": bool(ok), "detail": detail[:160]})
        print(f"  {'✓' if ok else '✗'} {name}" + (f":{detail[:100]}" if detail and not ok else ""))

    with db.connect() as conn, db.transaction(conn) as cur:
        before = _counts(cur)

    # (1) sentinel 入庫:既有 manual 導管(#12)——public 正向列 + local_private 反向列
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "sentinel_pub.txt").write_text(pub_text, encoding="utf-8")
        rc1, o1 = _sh([PY, str(REPO / "scripts/acquire_local_files.py"), "--dir", td,
                       "--license", "public_domain", "--domain", DOMAIN, "--access-scope", "public"])
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "sentinel_priv.txt").write_text(priv_text, encoding="utf-8")
        rc2, o2 = _sh([PY, str(REPO / "scripts/acquire_local_files.py"), "--dir", td,
                       "--license", "public_domain", "--domain", DOMAIN])   # 預設 access_scope=local_private、無 owner
    check("S1 sentinel 入庫(manual 導管×2)", rc1 == 0 and rc2 == 0, o1 + o2)

    # (2) 鏈:sentences → concordance(en)→ embed(既有 builder 逐支;#12)
    rc, out = _sh([PY, str(REPO / "scripts/build_sentences.py"), "--scope", "items"])
    check("S4 切句", rc == 0, out)
    rc, out = _sh([PY, str(REPO / "scripts/build_concordance.py"), "--scope", "items",
                   "--language", "en", "--run"])
    check("S5 concordance", rc == 0, out)
    rc, out = _sh([PY, str(REPO / "scripts/embed_knowledge.py"), "--layer", "sentence",
                   "--language", "en", "--scope", "items"])
    check("S8 嵌入", rc == 0, out)

    # (3) 正向斷言:域授權檢索 nonce → 逐字 byte-equal
    from augur.philosophy.retrieval import retrieve_items
    hits = retrieve_items(nonce, k=4, is_super=False, allowed_domains=[DOMAIN])
    pos = any(nonce in (getattr(h, "text", "") or "") and "private-" not in (getattr(h, "text", "") or "")
              for h in hits)
    byte_eq = any((getattr(h, "text", "") or "").strip() == pub_text or pub_text in (getattr(h, "text", "") or "")
                  for h in hits)
    check("正向:nonce 命中", pos, f"hits={len(hits)}")
    check("正向:逐字 byte-equal", byte_eq)

    # (4) fail-closed 反向:private 列不得被域授權檢索到;無授權全 deny
    leak = any(f"private-{nonce}" in (getattr(h, "text", "") or "") for h in hits)
    check("反向:private 列零外洩(域授權下)", not leak)
    hits0 = retrieve_items(nonce, k=4, is_super=False, allowed_domains=None)
    check("反向:無授權=deny(0 hits)", len(hits0) == 0, f"hits={len(hits0)}")

    # (5) 語料隔離:正式統計零增列
    with db.connect() as conn, db.transaction(conn) as cur:
        after = _counts(cur)
    iso = all(after[k] == before[k] for k in before)
    check("隔離:term_affinity/corpus_stats 零增列", iso, f"{before}→{after}")

    # (6) --with-llm:advise() 對 nonce 提問,輸出含逐字引用
    if with_llm:
        from augur.advisor.advise import advise
        from augur.advisor.ollama import make_llm_fn
        from augur.advisor.payload import empty_payload
        r = advise(f"知識庫裡是否有含 {nonce} 的句子?請引用原文。", empty_payload(),
                   make_llm_fn(model="qwen3:4b", think=False, strip_quotes=True),
                   retrieve_fn=lambda q, k=6, scope=None: retrieve_items(q, k=k, is_super=False,
                                                                          allowed_domains=[DOMAIN]),
                   scope=(False, [DOMAIN], None))
        llm_ok = any(nonce in (getattr(c, "text", "") or "") for c in r["citations"])
        check("LLM 末段:citations 含 nonce 逐字", llm_ok, f"citations={len(r['citations'])}")

    if not keep:
        clean()
    ok = all(r["ok"] for r in results)
    if as_json:
        print(json.dumps({"pass": ok, "nonce": nonce, "checks": results}, ensure_ascii=False))
    print(f"═> {'PASS(暢通)' if ok else 'FAIL(管線債:修復優先於擴容,v1.40.0)'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--clean", dest="clean_only", action="store_true")
    ap.add_argument("--with-llm", dest="with_llm", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--json", dest="as_json", action="store_true")
    args = ap.parse_args()
    if args.clean_only:
        clean(); return 0
    if args.run:
        return run(args.with_llm, args.keep, args.as_json)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM knowledge_item WHERE domain=%s", (DOMAIN,))
        print(f"現況:smoke_test 域殘留 item {cur.fetchone()[0]}(應 0;非 0 → --clean)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
