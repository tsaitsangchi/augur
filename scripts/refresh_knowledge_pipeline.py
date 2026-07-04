#!/usr/bin/env python
"""知識域端到端管線唯一驅動器 — S1 harvest→S2 promote→S3 全文/切句/concordance→S4 統計→S5 嵌入→S6 Milvus 匯出(七段一驅)。

🎯 這支在做什麼(白話):按 e2e 計畫 §7 顯式 DAG,逐節點 subprocess 呼叫既有 CLI(**check=True**,
   任一段非零即停、印段名後 exit≠0)——本支**只編排不計算**(零統計/嵌入邏輯內嵌,單一住所在各
   builder);待辦量全出自 DB 純 SQL(#29b);段序=code 內常數表 STAGES(非 DB 表);驅動器自身
   無狀態=殺掉重跑冪等,resume 全 DB-driven(harvest_log/NOT EXISTS/build_meta 游標,住各 builder)。
   S7 對話層=常駐 serving 不入批次 DAG(serve_advisor_openai.py 另起)。
   S4/S5 節點實際放量前置=P1-P4/P6-P7 拍板(計畫 §11 順序硬約束;閘在各 builder,本支不繞)。
守 #12(單一驅動器;收編退役 backfill_knowhow_pipeline.py=計畫 R1/P11,其 check=False 假驗收反例終結)·
   #15(計數全 DB 實查)· #25(harvest 預設最小 --batch 10)· #28(本地零 usage;背景=nohup+log+
   完成單次通知不輪詢)· #29(四件事)· e2e 計畫 §7。

執行指令矩陣:
  python scripts/refresh_knowledge_pipeline.py                               # 無參數:各段待辦計數矩陣(唯讀純 SQL、零副作用)
  python scripts/refresh_knowledge_pipeline.py --domain chemistry --dry-run  # 列印各段將執行指令+待辦計數,零執行
  python scripts/refresh_knowledge_pipeline.py --domain chemistry            # 全鏈實跑(背景建議 nohup ... > log 2>&1 &)
  python scripts/refresh_knowledge_pipeline.py --stage promote --domain chemistry            # 只跑單段
  python scripts/refresh_knowledge_pipeline.py --from-stage sentences --until embed --limit 1000
  # 段名封閉集(依序): harvest promote fulltext sentences concordance stats embed milvus_export
  # fulltext 段需環境變數 UNPAYWALL_EMAIL;--limit 映射為各 CLI 之有界旗標(promote 無界旗標=不適用)
"""
import sys
import time
import argparse
import subprocess
from pathlib import Path
from collections import namedtuple

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import embedspec

PY = sys.executable
SCRIPTS = Path(__file__).resolve().parent

# 段序 registry=code 內常數表(§7 29b:非 DB 表;驅動器無狀態)。args=該 CLI 實查既存旗標。
Stage = namedtuple("Stage", "name seg script args domain_ok limit_flag default_limit note")
STAGES = (
    Stage("harvest", "S1", "harvest_knowledge.py", ("--rounds", "1"), True, "--batch", 10,
          "首輪最小 --batch 10(#25);放量個別跑 harvest_knowledge.py --batch 300 --rounds 4"),
    Stage("promote", "S2", "promote_knowledge.py", (), True, None, None,
          "冪等去重全量(真實旗標無界量,--limit 不適用)"),
    Stage("fulltext", "S3", "fetch_oa_fulltext.py", (), True, "--limit", None,
          "需 UNPAYWALL_EMAIL;NC/ND/license 未明=誠實 skip 停 metadata"),
    Stage("sentences", "S3", "build_sentences.py", ("--scope", "items"), False, "--limit", None,
          "NOT EXISTS 冪等"),
    Stage("concordance", "S3", "build_concordance.py", ("--scope", "items", "--language", "en", "--run"),
          False, "--limit", None, "items 側 en;zh 側個別跑 build_concordance.py"),
    Stage("stats", "S4", "build_cross_school_stats.py", ("--phase", "groupstats", "--run"),
          False, "--limit", None, "放量前置=P1-P3 拍板+M4;游標可續"),
    Stage("embed", "S5", "embed_knowledge.py", ("--layer", "sentence", "--language", "en", "--scope", "items"),
          False, "--limit", None, "items 側先行(P7);P4 拍板前不放量;完後個別跑 --build-index"),
    Stage("milvus_export", "S6", "export_milvus_index.py",
          ("--layer", "sentence", "--side", "items", "--language", "en"), False, "--limit", None,
          "--limit=驗證模式(PG 零寫入);全量=雙向對帳+coverage 落庫"),
)
NAMES = tuple(s.name for s in STAGES)


def _n(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()[0]


def _rows(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


def _cursors(cur, like):
    rows = _rows(cur, "SELECT scope, cursor_sent_id FROM knowledge_build_meta "
                      "WHERE scope LIKE %s ORDER BY scope", (like,))
    return ", ".join(f"{s}={c:,}" for s, c in rows) or "(無游標)"


def pending_lines(cur, name, domain):
    """單段待辦/驗收計數(唯讀純 SQL;#29b 全 DB-driven,零 Claude 判斷)。回一至二行字串。"""
    d = " AND domain = %s" if domain else ""
    p = (domain,) if domain else ()
    item_join = ("JOIN knowledge_item_text x ON x.itext_id = s.itext_id "
                 "JOIN knowledge_item i USING (item_id) " if domain else "")
    if name == "harvest":
        nq = _n(cur, "SELECT count(*) FROM knowledge_query WHERE enabled" + d, p)
        st = _rows(cur, "SELECT l.status, count(*) FROM knowledge_harvest_log l "
                        "JOIN knowledge_query q USING (query_id)"
                        + (" WHERE q.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1", p)
        log = " / ".join(f"{k} {v:,}" for k, v in st) or "log 空"
        return [f"enabled query {nq:,} | harvest_log {log}"]
    if name == "promote":
        n = _n(cur, "SELECT count(*) FROM knowledge_staging WHERE status = 'pending'" + d, p)
        return [f"staging pending {n:,}"]
    if name == "fulltext":
        n = _n(cur, "SELECT count(*) FROM knowledge_item i WHERE NOT EXISTS "
                    "(SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)"
                    + (" AND i.domain = %s" if domain else ""), p)
        return [f"item 無全文 {n:,}(上限;DOI 有無/OA 可得性另計,分子照實不虛灌)"]
    if name == "sentences":
        n = _n(cur, "SELECT count(*) FROM knowledge_item_text t JOIN knowledge_item i USING (item_id) "
                    "WHERE NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.itext_id = t.itext_id)"
                    + (" AND i.domain = %s" if domain else ""), p)
        return [f"item_text 未切句 {n:,}"]
    if name == "concordance":
        langs = _rows(cur, f"SELECT s.language, count(*) FROM knowledge_sentence s {item_join}"
                           "WHERE s.itext_id IS NOT NULL"
                           + (" AND i.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1", p)
        seg = " ".join(f"{lg} {n:,}" for lg, n in langs) or "0"
        return [f"items 側句 {seg} | 游標 {_cursors(cur, 'concordance%')}"]
    if name == "stats":
        return [f"游標 {_cursors(cur, 'xs_%')}(groupstats 待辦由 builder 無參數自報)"]
    if name == "embed":
        rows = _rows(cur, f"SELECT s.language, count(*) FROM knowledge_sentence s {item_join}"
                          "WHERE s.itext_id IS NOT NULL AND NOT EXISTS "
                          "(SELECT 1 FROM knowledge_sentence_embedding e "
                          "WHERE e.sent_id = s.sent_id AND e.model_tag = %s)"
                          + (" AND i.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1",
                     (embedspec.MODEL_TAG, *p))
        seg = " ".join(f"{lg} {n:,}" for lg, n in rows) or "0"
        lines = [f"items 側未嵌({embedspec.MODEL_TAG}) {seg}(上限;junk/CLEAN 排除另計,帳在 ledger)"]
        if not domain:
            w = _n(cur, "SELECT count(*) FROM knowledge_sentence s WHERE s.text_id IS NOT NULL "
                        "AND NOT EXISTS (SELECT 1 FROM knowledge_sentence_embedding e "
                        "WHERE e.sent_id = s.sent_id AND e.model_tag = %s)", (embedspec.MODEL_TAG,))
            lines.append(f"works 側未嵌 {w:,}(en 債=P7 另排,不入本 DAG 節點)")
        return lines
    if name == "milvus_export":
        cov = _rows(cur, "SELECT metric_key, numerator, denominator, metric_date "
                         "FROM knowledge_coverage_metric WHERE metric_key LIKE %s "
                         "ORDER BY metric_date DESC, metric_key LIMIT 6", ("mv_%",))
        covs = " | ".join(f"{k} {n}/{dn}({dt})" for k, n, dn, dt in cov) or "coverage 無 mv 列"
        return [f"游標 {_cursors(cur, 'mv_%')} | {covs}",
                "實際雙向對帳=python scripts/export_milvus_index.py(無參數唯讀矩陣)"]
    raise ValueError(f"未知段名 {name}(封閉集:{' '.join(NAMES)})")


def print_matrix(domain):
    print(f"知識管線待辦矩陣(domain={domain or '全部域'};唯讀純 SQL、零副作用):")
    with db.connect() as conn, db.transaction(conn) as cur:
        for st in STAGES:
            for i, line in enumerate(pending_lines(cur, st.name, domain)):
                head = f"{st.seg} {st.name:<13}" if i == 0 else " " * 16
                print(f"  {head} {line}")


def build_cmd(st, domain, limit):
    cmd = [PY, str(SCRIPTS / st.script), *st.args]
    if domain and st.domain_ok:
        cmd += ["--domain", domain]
    n = limit if (limit and st.limit_flag) else st.default_limit
    if st.limit_flag and n:
        cmd += [st.limit_flag, str(n)]
    return cmd


def select_stages(args):
    if args.stage:
        if args.from_stage or args.until:
            sys.exit("--stage 不可與 --from-stage/--until 併用")
        return [s for s in STAGES if s.name == args.stage]
    lo = NAMES.index(args.from_stage) if args.from_stage else 0
    hi = NAMES.index(args.until) if args.until else len(NAMES) - 1
    if lo > hi:
        sys.exit(f"--from-stage {args.from_stage} 在 --until {args.until} 之後(段序:{' '.join(NAMES)})")
    return list(STAGES[lo:hi + 1])


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--domain")
    ap.add_argument("--stage", choices=NAMES)
    ap.add_argument("--from-stage", dest="from_stage", choices=NAMES)
    ap.add_argument("--until", choices=NAMES)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", dest="dry_run", action="store_true")
    args = ap.parse_args()
    if args.limit is not None and args.limit <= 0:
        sys.exit("--limit 須為正整數(0/負值不得靜默轉為全量)")

    if len(sys.argv) == 1:   # 無參數=安全預設(#29a)
        print_matrix(None)
        print("\n用法見標頭執行指令矩陣;--dry-run 列印各段將執行指令(零執行)")
        return

    stages = select_stages(args)
    if args.dry_run:
        print_matrix(args.domain)
        print(f"\n[dry-run] 將依序執行 {len(stages)} 段(check=True,任一段非零即停;本模式零執行):")
        for st in stages:
            print(f"  {st.seg} {st.name:<13} $ {' '.join(build_cmd(st, args.domain, args.limit))}")
            if st.note:
                print(f"     {'':<13} 註:{st.note}")
        return

    t0 = time.time()
    print(f"=== 知識管線驅動開始:{len(stages)} 段 | domain={args.domain or '全部'} | "
          f"limit={args.limit or '-'}(段序=常數表;resume 全 DB-driven,殺掉重跑冪等)===", flush=True)
    for st in stages:
        with db.connect() as conn, db.transaction(conn) as cur:
            before = pending_lines(cur, st.name, args.domain)
        cmd = build_cmd(st, args.domain, args.limit)
        print(f"\n▶ {st.seg} {st.name} | 待辦(前):{'; '.join(before)}\n  $ {' '.join(cmd)}", flush=True)
        ts = time.time()
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"✗ 段 {st.name} exit={e.returncode}(耗時 {time.time() - ts:.0f}s)——中止全鏈"
                  f"(check=True);該段輸出見本 log 上方;修復後續跑:--from-stage {st.name}", flush=True)
            sys.exit(e.returncode or 1)
        with db.connect() as conn, db.transaction(conn) as cur:
            after = pending_lines(cur, st.name, args.domain)
        print(f"✓ {st.seg} {st.name} 完成 {time.time() - ts:.0f}s | 驗收計數(後):{'; '.join(after)}",
              flush=True)
    print(f"\n=== 全鏈完成 {(time.time() - t0) / 60:.1f} 分(冪等驗收:連跑兩次計數不變)===", flush=True)


if __name__ == "__main__":
    main()
