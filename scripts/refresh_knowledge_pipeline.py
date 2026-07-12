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
  python scripts/refresh_knowledge_pipeline.py --status                      # D7:心跳/單例鎖/上次段位/殭屍偵測/硬體 profile(唯讀)
  python scripts/refresh_knowledge_pipeline.py --domain chemistry --dry-run  # 列印各段將執行指令+待辦計數,零執行
  python scripts/refresh_knowledge_pipeline.py --domain chemistry            # 全鏈實跑(自動 flock 單例鎖+每段心跳;背景建議 nohup ... > log 2>&1 &)
  python scripts/refresh_knowledge_pipeline.py --stage promote --domain chemistry            # 只跑單段
  python scripts/refresh_knowledge_pipeline.py --from-stage sentences --until embed --limit 1000
  python scripts/refresh_knowledge_pipeline.py --domain finance --stage-limit embed=5000 --stage-limit stats=20000   # D7 per-stage 量
  python scripts/refresh_knowledge_pipeline.py --reap                        # D7:殭屍收斂(心跳逾時/driver 亡→終止孤兒 process group+清 stale 鎖)
  # 段名封閉集(依序): harvest promote fulltext sentences concordance stats embed vector_export
  # fulltext 段需環境變數 UNPAYWALL_EMAIL;--limit 映射為各 CLI 之有界旗標(promote 無界旗標=不適用)
  # vector_export 讀 knowledge_vectorstore_config(scope=sentence_items):backend=pgvector→skip(SSOT 即 serving);qdrant_*→export_qdrant_index.py
"""
import fcntl
import os
import signal
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
LOCK_PATH = SCRIPTS.parent / ".refresh_pipeline.lock"   # 單例鎖(flock;DB 心跳=第二保險)
HB_STALE_SEC = 2 * 3600                                  # 殭屍判準:心跳齡 > 此值(段預期上界之 2×)

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
    Stage("vector_export", "S6", "export_qdrant_index.py",
          ("--side", "items", "--language", "en"), False, "--limit", None,
          "讀 knowledge_vectorstore_config 選匯出器(A-34):backend=pgvector→skip(pgvector 即 serving SSOT、"
          "無外部索引需匯出);qdrant_*→export_qdrant_index.py(export_milvus_index 退役列冊)"),
)
NAMES = tuple(s.name for s in STAGES)


# ─── D7:心跳/單例鎖/殭屍收斂(帳住 knowledge_build_meta,scope≤32/bigint 形狀內、零新表)───

def _meta_set(cur, scope, val):
    cur.execute("INSERT INTO knowledge_build_meta (scope, cursor_sent_id) VALUES (%s,%s) "
                "ON CONFLICT (scope) DO UPDATE SET cursor_sent_id=EXCLUDED.cursor_sent_id, updated_at=now()",
                (scope, int(val)))


def _meta_get(cur, scope):
    cur.execute("SELECT cursor_sent_id, updated_at FROM knowledge_build_meta WHERE scope=%s", (scope,))
    return cur.fetchone()


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, OverflowError, ValueError):
        return False


def heartbeat(stage_idx, child_pid=0):
    """每段開跑前 tick(subprocess 阻塞期間不 tick=設計取捨,殭屍判準用 2× 段上界容忍)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        _meta_set(cur, "orch/pid", os.getpid())
        _meta_set(cur, "orch/stage", stage_idx)
        _meta_set(cur, "orch/child", child_pid)


def hw_probe():
    """§9.3 硬體 profile 落帳(GPU 有無/VRAM MB;兩路徑探測,CPU-only 誠實記 0)。"""
    vram = 0
    for exe in ("nvidia-smi", "/usr/lib/wsl/lib/nvidia-smi"):
        try:
            out = subprocess.run([exe, "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                vram = int(out.stdout.strip().splitlines()[0])
                break
        except (OSError, ValueError, subprocess.TimeoutExpired):
            continue
    with db.connect() as conn, db.transaction(conn) as cur:
        _meta_set(cur, "orch/hw_vram_mb", vram)
    return vram


def acquire_lock():
    """單例鎖:flock 非阻塞;第二實例即退 exit≠0(D7;DB 心跳=跨機第二保險)。回鎖 fd(須保持開啟)。"""
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        sys.exit(f"✗ 另一驅動器實例持有鎖({LOCK_PATH});--status 查現況、--reap 收斂殭屍")
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode())
    return fd


def status():
    """--status:心跳/鎖/段位/殭屍偵測/硬體(唯讀)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        pid_row = _meta_get(cur, "orch/pid")
        st_row = _meta_get(cur, "orch/stage")
        ch_row = _meta_get(cur, "orch/child")
        hw_row = _meta_get(cur, "orch/hw_vram_mb")
        cur.execute("SELECT extract(epoch FROM now()-updated_at) FROM knowledge_build_meta WHERE scope='orch/pid'")
        age = cur.fetchone()
    if not pid_row:
        print("心跳:(無——驅動器未跑過)")
    else:
        pid, ts = int(pid_row[0]), pid_row[1]
        alive = _pid_alive(pid)
        age_s = int(age[0]) if age and age[0] is not None else -1
        stg = NAMES[int(st_row[0])] if st_row and 0 <= int(st_row[0]) < len(NAMES) else "?"
        child = int(ch_row[0]) if ch_row else 0
        zombie = (not alive and child and _pid_alive(child)) or (alive and age_s > HB_STALE_SEC)
        print(f"心跳:pid={pid}({'存活' if alive else '已亡'}) 段={stg} 心跳齡={age_s}s child={child or '-'}"
              f"{'(存活)' if child and _pid_alive(child) else ''}")
        print(f"殭屍判定:{'⚠ 是(--reap 收斂)' if zombie else '否'}(判準:driver 亡而 child 活、或心跳齡>{HB_STALE_SEC}s)")
    print(f"單例鎖:{LOCK_PATH}({'存在' if LOCK_PATH.exists() else '無'})")
    print(f"硬體:VRAM {int(hw_row[0]) if hw_row else '未探測'} MB(0=CPU-only)")


def reap():
    """--reap:殭屍收斂——driver 亡而 child(自成 process group)活→SIGTERM killpg;清 stale 心跳。冪等。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        pid_row = _meta_get(cur, "orch/pid")
        ch_row = _meta_get(cur, "orch/child")
    if not pid_row:
        print("(無心跳帳,無可收斂)"); return
    pid, child = int(pid_row[0]), int(ch_row[0]) if ch_row else 0
    if _pid_alive(pid):
        print(f"driver pid={pid} 仍存活——不收斂(要停請對其 SIGTERM;本工具只收孤兒)"); return
    if child and _pid_alive(child):
        try:
            os.killpg(child, signal.SIGTERM)                 # 段以 start_new_session 起=pgid=child pid
            print(f"✓ 已 SIGTERM 孤兒段 process group {child}")
        except (ProcessLookupError, PermissionError) as e:
            print(f"⚠ killpg({child}) 失敗:{e}")
    with db.connect() as conn, db.transaction(conn) as cur:
        _meta_set(cur, "orch/pid", 0)
        _meta_set(cur, "orch/child", 0)
    print("✓ 心跳帳已清(stale flock 由持鎖 process 消亡自動釋放,檔案殘留無害)")


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
        # 待抓=無全文且無 blocked 終態帳(#15:license/OA 阻擋者已落 knowledge_fulltext_status,
        # 排除使計數收斂=真待辦、非漏抓;若帳表未建則退回原上限 count)。
        blocked_exists = _n(cur, "SELECT count(*) FROM information_schema.tables "
                                 "WHERE table_name='knowledge_fulltext_status'")
        blocked_clause = ("AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status b "
                          "WHERE b.item_id = i.item_id) " if blocked_exists else "")
        n = _n(cur, "SELECT count(*) FROM knowledge_item i WHERE NOT EXISTS "
                    "(SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id) "
                    + blocked_clause
                    + ("AND i.domain = %s" if domain else ""), p)
        nb = _n(cur, "SELECT count(*) FROM knowledge_fulltext_status b JOIN knowledge_item i USING (item_id)"
                     + (" WHERE i.domain = %s" if domain else ""), p) if blocked_exists else 0
        return [f"item 待抓全文 {n:,}(已排除 blocked 終態帳 {nb:,} 筆=license/OA 阻擋非漏抓;分子照實)"]
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
    if name == "vector_export":
        be = _rows(cur, "SELECT scope, backend FROM knowledge_vectorstore_config ORDER BY scope")
        bes = " ".join(f"{s}={b}" for s, b in be) or "(config 空——先跑 migrate_vectorstore_config_ddl --run)"
        qs = _n(cur, "SELECT count(*) FROM qdrant_sync_state") if _n(
            cur, "SELECT count(*) FROM information_schema.tables WHERE table_name='qdrant_sync_state'") else 0
        return [f"後端 config:{bes} | qdrant_sync_state {qs:,} 列",
                "backend=pgvector→本段 skip(pgvector 即 serving SSOT);qdrant_*→export_qdrant_index.py"]
    raise ValueError(f"未知段名 {name}(封閉集:{' '.join(NAMES)})")


def print_matrix(domain):
    print(f"知識管線待辦矩陣(domain={domain or '全部域'};唯讀純 SQL、零副作用):")
    with db.connect() as conn, db.transaction(conn) as cur:
        for st in STAGES:
            for i, line in enumerate(pending_lines(cur, st.name, domain)):
                head = f"{st.seg} {st.name:<13}" if i == 0 else " " * 16
                print(f"  {head} {line}")


def build_cmd(st, domain, limit, stage_limits=None):
    cmd = [PY, str(SCRIPTS / st.script), *st.args]
    if domain and st.domain_ok:
        cmd += ["--domain", domain]
    per = (stage_limits or {}).get(st.name)                  # D7 per-stage 量優先於全域 --limit
    n = per if (per and st.limit_flag) else (limit if (limit and st.limit_flag) else st.default_limit)
    if st.limit_flag and n:
        cmd += [st.limit_flag, str(n)]
    return cmd


def _vector_backend(cur):
    cur.execute("SELECT backend FROM knowledge_vectorstore_config WHERE scope='sentence_items'")
    r = cur.fetchone()
    return r[0] if r else None


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
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--reap", action="store_true")
    ap.add_argument("--stage-limit", dest="stage_limit", action="append", default=[],
                    metavar="STAGE=N", help="D7 per-stage 量(可多次;優先於 --limit)")
    args = ap.parse_args()
    if args.status:
        status(); return
    if args.reap:
        reap(); return
    stage_limits = {}
    for sl in args.stage_limit:
        name, _, n = sl.partition("=")
        if name not in NAMES or not n.isdigit() or int(n) <= 0:
            sys.exit(f"--stage-limit 格式:<段名>=<正整數>(段名封閉集:{' '.join(NAMES)});收到 {sl!r}")
        stage_limits[name] = int(n)
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
            print(f"  {st.seg} {st.name:<13} $ {' '.join(build_cmd(st, args.domain, args.limit, stage_limits))}")
            if st.note:
                print(f"     {'':<13} 註:{st.note}")
        return

    lock_fd = acquire_lock()                                 # D7 單例鎖(第二實例即退)
    vram = hw_probe()                                        # §9.3 硬體 profile 落帳
    t0 = time.time()
    print(f"=== 知識管線驅動開始:{len(stages)} 段 | domain={args.domain or '全部'} | "
          f"limit={args.limit or '-'} | per-stage={stage_limits or '-'} | VRAM={vram}MB"
          f"(段序=常數表;resume 全 DB-driven,殺掉重跑冪等)===", flush=True)
    for st in stages:
        heartbeat(NAMES.index(st.name))                      # D7 每段 tick
        if st.name == "vector_export":                       # A-34:讀 config 選匯出器
            with db.connect() as conn, db.transaction(conn) as cur:
                be = _vector_backend(cur)
            if be in (None, "pgvector"):
                print(f"\n▷ {st.seg} vector_export skip(backend={be or '(config 空)'}——pgvector 即 serving "
                      f"SSOT、無外部索引需匯出;切 Qdrant=UPDATE config 一列)", flush=True)
                continue
        with db.connect() as conn, db.transaction(conn) as cur:
            before = pending_lines(cur, st.name, args.domain)
        cmd = build_cmd(st, args.domain, args.limit, stage_limits)
        print(f"\n▶ {st.seg} {st.name} | 待辦(前):{'; '.join(before)}\n  $ {' '.join(cmd)}", flush=True)
        ts = time.time()
        proc = subprocess.Popen(cmd, start_new_session=True)  # 自成 process group=--reap 可 killpg 孤兒
        heartbeat(NAMES.index(st.name), child_pid=proc.pid)
        rc = proc.wait()
        if rc != 0:
            print(f"✗ 段 {st.name} exit={rc}(耗時 {time.time() - ts:.0f}s)——中止全鏈"
                  f"(check=True 語意);該段輸出見本 log 上方;修復後續跑:--from-stage {st.name}", flush=True)
            sys.exit(rc or 1)
        with db.connect() as conn, db.transaction(conn) as cur:
            after = pending_lines(cur, st.name, args.domain)
        print(f"✓ {st.seg} {st.name} 完成 {time.time() - ts:.0f}s | 驗收計數(後):{'; '.join(after)}",
              flush=True)
    heartbeat(len(NAMES) - 1, child_pid=0)                   # 收尾 tick(child 清零)
    os.close(lock_fd)
    print(f"\n=== 全鏈完成 {(time.time() - t0) / 60:.1f} 分(冪等驗收:連跑兩次計數不變)===", flush=True)


if __name__ == "__main__":
    main()
