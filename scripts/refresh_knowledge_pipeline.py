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
  python scripts/refresh_knowledge_pipeline.py --domain chemistry --stage-limit embed=5000 --stage-limit stats=20000   # D7 per-stage 量
  # ↑ 本行原範例寫 `--domain finance`(全庫無此域,#29d 矩陣須實測可執行)——service 之 ExecStart 亦帶同一字串,
  #   疑為自本例複製而來;已改為真實域,並由下方 M-G8 閘使任何不存在之域一律 rc≠0。
  python scripts/refresh_knowledge_pipeline.py --reap                        # D7:殭屍收斂(心跳逾時/driver 亡→終止孤兒 process group+清 stale 鎖)
  python scripts/refresh_knowledge_pipeline.py --selftest                    # 純紅綠自測(免 DB 免 API、零 usage;#18)
  python scripts/refresh_knowledge_pipeline.py --domain no_such_domain       # M-G8:域不存在→rc=2+印可用域清單(不空轉回綠)
  python scripts/refresh_knowledge_pipeline.py --from-stage promote --domain chemistry --min-candidates 1  # 候選數地板:待辦合計<N→rc=3
  # 段名封閉集(依序): harvest promote fulltext sentences resplit concordance stats stats_items bridge embed vector_export kip
  #   (stats_items/bridge=K 計畫 §4 2026-07-14 加段;resplit/kip=LSR-INGRESS-S2)
  # fulltext 段需環境變數 UNPAYWALL_EMAIL;--limit 映射為各 CLI 之有界旗標(promote 無界旗標=不適用)
  # vector_export 讀 knowledge_vectorstore_config(scope=sentence_items):backend=pgvector→skip(SSOT 即 serving);qdrant_*→export_qdrant_index.py
  # kip=入庫強制收束(scoped embed/kh4/admit；--needs-kip)
  # rc 語意:0=正常 / 2=--domain 不存在(M-G8 fail-loud) / 3=候選數地板未達 / 其餘=段本身 exit code
"""
import difflib
import fcntl
import os
import signal
import sys
import time
import argparse
import re
import subprocess
from pathlib import Path
from collections import namedtuple

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import embedspec, kh4

PY = sys.executable
SCRIPTS = Path(__file__).resolve().parent
LOCK_PATH = SCRIPTS.parent / ".refresh_pipeline.lock"   # 單例鎖(flock;DB 心跳=第二保險)
HB_STALE_SEC = 2 * 3600                                  # 殭屍判準:心跳齡 > 此值(段預期上界之 2×)

# 段序 registry=code 內常數表(§7 29b:非 DB 表;驅動器無狀態)。args=該 CLI 實查既存旗標。
Stage = namedtuple("Stage", "name seg script args domain_ok limit_flag default_limit note")
STAGES = (
    Stage("harvest", "S1", "harvest_knowledge.py", ("--rounds", "1"), True, "--batch", 10,
          "首輪最小 --batch 10(#25);放量個別跑 harvest_knowledge.py --batch 300 --rounds 4"),
    Stage("promote", "S2", "promote_knowledge.py", ("--entity-type", "all"), True, None, None,
          "冪等去重全量(真實旗標無界量,--limit 不適用);**必帶 --entity-type**——"
          "前版傳空 args 使 promote 走「印用法即 return」分支、exit 0，"
          "本段遂記「✓ 完成 0s」而 pending 一筆未動(2026-07-31 實證 16,072 筆假綠)"),
    Stage("fulltext", "S3", "fetch_oa_fulltext.py", (), True, "--limit", None,
          "需 UNPAYWALL_EMAIL;NC/ND/license 未明=誠實 skip 停 metadata"),
    Stage("sentences", "S3", "build_sentences.py", ("--scope", "items", "--max-chars", "800"), False, "--limit", None,
          "NOT EXISTS 冪等;LSR max_chars=800"),
    Stage("resplit", "S3", "resplit_long_sentences.py",
          ("--apply", "--side", "items", "--max-chars", "800", "--note", "LSR-INGRESS-DAG"),
          False, "--limit", None, "殘長句硬切(無則空跑)"),
    Stage("concordance", "S3", "build_concordance.py", ("--scope", "items", "--language", "en", "--run"),
          False, "--limit", None, "items 側 en;zh 側個別跑 build_concordance.py"),
    Stage("stats", "S4", "build_cross_school_stats.py", ("--phase", "groupstats", "--run"),
          False, "--limit", None, "放量前置=P1-P3 拍板+M4;游標可續"),
    Stage("stats_items", "S4", "build_items_knowhow_stats.py", ("--run",), False, None, None,
          "items 語料統計軌(npmi/jaccard;llr 待放量 W3)——K 計畫 §4:新語料落地即重建,防橋層靜默陳舊"),
    Stage("bridge", "S4", "build_field_knowledge_bridge.py", ("--run",), False, None, None,
          "欄位↔know-how 語意橋(排 stats_items 後、embed 前;K 計畫 §4;derivation_method 四值閘不變)"),
    Stage("embed", "S5", "embed_knowledge.py", ("--layer", "sentence", "--language", "en", "--scope", "items"),
          False, "--limit", None, "items 側先行(P7);P4 拍板前不放量;完後個別跑 --build-index"),
    Stage("vector_export", "S6", "export_qdrant_index.py",
          ("--side", "items", "--language", "en"), False, "--limit", None,
          "讀 knowledge_vectorstore_config 選匯出器(A-34):backend=pgvector→skip(pgvector 即 serving SSOT、"
          "無外部索引需匯出);qdrant_*→export_qdrant_index.py(export_milvus_index 退役列冊)"),
    Stage("kip", "S7", "run_knowledge_ingress_kip.py",
          ("--channel", "topic_harvest", "--apply", "--skip-qdrant", "--needs-kip"),
          True, "--limit", None,
          "LSR-INGRESS-S2:域內待補 item 跑 KIP 收束(kh4+admit≤9;sentences/embed 多為冪等空跑)"),
)
NAMES = tuple(s.name for s in STAGES)

# ── M-G8 S1:具「待辦」語意之段(其計數隨處理而遞減)。其餘段(stats/stats_items/bridge/
# concordance/vector_export)印的是**全庫庫存**(field_term_map 6,072、item_term_stats 188,069…),
# 不隨 --domain 收斂——現查 `--domain finance`(不存在之域)這些數字照樣非零。故候選數地板
# **只認本集合**;拿庫存數充待辦數會使地板恆過=正是本段要消滅的空轉假綠(#15)。
BACKLOG_STAGES = frozenset({"harvest", "promote", "fulltext", "sentences", "resplit", "embed", "kip"})


# ─── M-G8 S1:domain 解析(fail-loud;不存在之域不得靜默空轉回綠)───

def known_domains(cur):
    """可用域清單(SSOT=DB #29b)——registry(enabled) ∪ 四張知識表**實際落地**之域,取聯集。

    為何不只認 knowledge_domain registry:現查 registry 43 列,但 quant_finance(15,552 item)、
    software_engineering(1,685)、philosophy、economics、management、erp_semantics、solar_rd
    等域**有資料卻未登錄**;只認 registry 會把活躍域判成「不存在」而擋掉正常週更=假紅。
    """
    cur.execute("""
        SELECT domain FROM knowledge_domain   WHERE enabled
        UNION SELECT domain FROM knowledge_item    WHERE domain IS NOT NULL
        UNION SELECT domain FROM knowledge_query   WHERE domain IS NOT NULL
        UNION SELECT domain FROM knowledge_source  WHERE domain IS NOT NULL
        UNION SELECT domain FROM knowledge_staging WHERE domain IS NOT NULL
    """)
    return {r[0] for r in cur.fetchall()}


def domain_verdict(domain, known):
    """純函式(零 DB=可 --selftest 紅綠自測):回 (ok, 相近域建議)。不在 known 即 ok=False。"""
    if domain in known:
        return True, []
    return False, difflib.get_close_matches(domain, sorted(known), n=5, cutoff=0.6)


def assert_domain_known(domain):
    """fail-loud 閘:`--domain <不存在>` 一律 exit≠0 並印可用域清單(#15 rc=0 不得代表沒做事)。

    病灶(2026-08-03 M-G8):augur-knowhow-refresh.service 之 ExecStart 帶 `--domain finance`,
    而全庫無此域(knowledge_item domain='finance' = 0)——每週準時 Finished、journal 自陳
    「待辦(前) 0」,而同時刻全域 staging pending 102,039 筆一筆未動。
    """
    with db.connect() as conn, db.transaction(conn) as cur:
        known = known_domains(cur)
    ok, near = domain_verdict(domain, known)
    if ok:
        return
    print(f"✗ --domain {domain!r} 在本庫**不存在**——中止(不空轉回綠;rc≠0 才是誠實終態)。", file=sys.stderr)
    if near:
        print(f"  相近可用域:{' '.join(near)}", file=sys.stderr)
    print(f"  可用域({len(known)} 個;registry∪實際落地):{' '.join(sorted(known))}", file=sys.stderr)
    sys.exit(2)


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


def _item_join(domain):
    return ("JOIN knowledge_item_text x ON x.itext_id = s.itext_id "
            "JOIN knowledge_item i USING (item_id) " if domain else "")


def _embed_pending_rows(cur, domain):
    """items 側未嵌句(依語言分組);顯示與地板共用同一查詢=兩者不會漂。"""
    p = (domain,) if domain else ()
    return _rows(cur, f"SELECT s.language, count(*) FROM knowledge_sentence s {_item_join(domain)}"
                      "WHERE s.itext_id IS NOT NULL AND NOT EXISTS "
                      "(SELECT 1 FROM knowledge_sentence_embedding e "
                      "WHERE e.sent_id = s.sent_id AND e.model_tag = %s)"
                      + (" AND i.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1",
                 (embedspec.MODEL_TAG, *p))


def _fulltext_blocked_exists(cur):
    return _n(cur, "SELECT count(*) FROM information_schema.tables "
                   "WHERE table_name='knowledge_fulltext_status'")


def candidate_count(cur, name, domain):
    """單段**候選(待辦)數**;僅 BACKLOG_STAGES 有此語意,其餘段回 None(唯讀純 SQL)。

    ⚠ 刻意**不**從 pending_lines 的顯示字串刮數字當地板:那些行混有全庫庫存數
    (stats_items 188,069／bridge 65,137),不隨 domain 收斂,刮來當待辦即恆過閘=假綠。
    顯示行由本函式供數(單一住所),兩者不會漂。
    """
    d = " AND domain = %s" if domain else ""
    p = (domain,) if domain else ()
    if name == "harvest":
        return _n(cur, "SELECT count(*) FROM knowledge_query WHERE enabled" + d, p)
    if name == "promote":
        return _n(cur, "SELECT count(*) FROM knowledge_staging WHERE status = 'pending'" + d, p)
    if name == "fulltext":
        # 待抓=無全文且無 blocked 終態帳(#15:license/OA 阻擋者已落 knowledge_fulltext_status,
        # 排除使計數收斂=真待辦、非漏抓;若帳表未建則退回原上限 count)。
        blocked_clause = ("AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status b "
                          "WHERE b.item_id = i.item_id AND b.status <> 'unattempted') "
                          if _fulltext_blocked_exists(cur) else "")
        return _n(cur, "SELECT count(*) FROM knowledge_item i WHERE NOT EXISTS "
                       "(SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id) "
                       + blocked_clause
                       + ("AND i.domain = %s" if domain else ""), p)
    if name == "sentences":
        return _n(cur, "SELECT count(*) FROM knowledge_item_text t JOIN knowledge_item i USING (item_id) "
                       "WHERE NOT EXISTS (SELECT 1 FROM knowledge_sentence s WHERE s.itext_id = t.itext_id)"
                       + (" AND i.domain = %s" if domain else ""), p)
    if name == "resplit":
        return _n(cur, "SELECT count(DISTINCT s.itext_id) FROM knowledge_sentence s "
                       + _item_join(domain)
                       + "WHERE s.itext_id IS NOT NULL AND length(s.sentence)>800"
                       + (" AND i.domain = %s" if domain else ""), p)
    if name == "embed":
        return sum(n for _, n in _embed_pending_rows(cur, domain))
    if name == "kip":
        # 與 ingress_kip.resolve needs_kip 同精神之概數
        return _n(cur, """
            SELECT count(*) FROM knowledge_item i
            WHERE EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id=i.item_id)
            """ + (" AND i.domain = %s" if domain else "") + """
            AND (
              NOT EXISTS (
                SELECT 1 FROM knowledge_sentence s
                JOIN knowledge_item_text t ON t.itext_id=s.itext_id WHERE t.item_id=i.item_id)
              OR NOT EXISTS (
                SELECT 1 FROM knowledge_kh4_state k
                WHERE k.item_id=i.item_id AND k.answer_status='eligible')
              OR NOT EXISTS (
                SELECT 1 FROM knowhow_auto_admit_state a
                WHERE a.target_kind='item' AND a.target_id=i.item_id::text
                  AND a.admit_depth >= 9)
            )
            """, p)
    return None


def pending_lines(cur, name, domain):
    """單段待辦/驗收計數(唯讀純 SQL;#29b 全 DB-driven,零 Claude 判斷)。回一至二行字串。"""
    p = (domain,) if domain else ()
    item_join = _item_join(domain)
    if name == "harvest":
        nq = candidate_count(cur, "harvest", domain)
        st = _rows(cur, "SELECT l.status, count(*) FROM knowledge_harvest_log l "
                        "JOIN knowledge_query q USING (query_id)"
                        + (" WHERE q.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1", p)
        log = " / ".join(f"{k} {v:,}" for k, v in st) or "log 空"
        # 第 2 行:檔案通道(件 A/G;query_id=0 sentinel 帳,原第 1 行 INNER JOIN knowledge_query 丟棄之)使三通道可見
        fc = _rows(cur, "SELECT ks.adapter, count(*) FROM knowledge_source ks WHERE ks.approval_status='active' "
                        "AND ks.adapter IN ('local_files','sftp')"
                        + (" AND ks.domain=%s" if domain else "") + " GROUP BY 1 ORDER BY 1", p)
        # query_id=0 為 harvest singles 與檔案通道共用之 sentinel(對抗審查)——JOIN adapter 過濾只顯真檔案通道
        fcs = _rows(cur, "SELECT l.status, count(*) FROM knowledge_harvest_log l "
                         "JOIN knowledge_source ks ON ks.source_key=l.source_key "
                         "WHERE l.query_id=0 AND ks.adapter IN ('local_files','sftp') GROUP BY 1 ORDER BY 1")
        chan = " ".join(f"{a}:{n}" for a, n in fc) or "無 active 源"
        clog = " / ".join(f"{s} {n}" for s, n in fcs) or "(未跑)"
        return [f"enabled query {nq:,} | harvest_log {log}",
                f"檔案通道 active 源 {chan} | 通道 log(query_id=0) {clog}"]
    if name == "promote":
        return [f"staging pending {candidate_count(cur, 'promote', domain):,}"]
    if name == "fulltext":
        n = candidate_count(cur, "fulltext", domain)
        nb = _n(cur, "SELECT count(*) FROM knowledge_fulltext_status b JOIN knowledge_item i USING (item_id)"
                     " WHERE b.status <> 'unattempted'"
                     + (" AND i.domain = %s" if domain else ""), p) if _fulltext_blocked_exists(cur) else 0
        return [f"item 待抓全文 {n:,}(已排除 blocked 終態帳 {nb:,} 筆=license/OA 阻擋非漏抓;分子照實)"]
    if name == "sentences":
        return [f"item_text 未切句 {candidate_count(cur, 'sentences', domain):,}"]
    if name == "resplit":
        return [f"items 超長句 parent {candidate_count(cur, 'resplit', domain):,}"]
    if name == "kip":
        return [f"待 KIP 收束 item {candidate_count(cur, 'kip', domain):,}"]
    if name == "concordance":
        langs = _rows(cur, f"SELECT s.language, count(*) FROM knowledge_sentence s {item_join}"
                           "WHERE s.itext_id IS NOT NULL"
                           + (" AND i.domain = %s" if domain else "") + " GROUP BY 1 ORDER BY 1", p)
        seg = " ".join(f"{lg} {n:,}" for lg, n in langs) or "0"
        return [f"items 側句 {seg} | 游標 {_cursors(cur, 'concordance%')}"]
    if name == "stats":
        return [f"游標 {_cursors(cur, 'xs_%')}(groupstats 待辦由 builder 無參數自報)"]
    if name == "stats_items":
        n = _n(cur, "SELECT count(*) FROM knowledge_item_term_stats")
        c = _n(cur, "SELECT count(*) FROM knowledge_term_corpus_stats WHERE corpus='items'")
        return [f"item_term_stats {n:,} | corpus_stats(items) {c:,}(--run 全量重建,語料小分鐘級)"]
    if name == "bridge":
        m = _n(cur, "SELECT count(*) FROM field_term_map")
        a = _n(cur, "SELECT count(*) FROM field_knowhow_lexical_affinity")
        return [f"field_term_map {m:,} | lexical_affinity {a:,}(--run 全量重建;cooc_sents≥30 閘在 builder)"]
    if name == "embed":
        rows = _embed_pending_rows(cur, domain)
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


# 件 A/G 通道統一:harvest 段除 API topic(harvest_knowledge.py)外,迭代 active 本機/SFTP 檔案通道源。
# adapter→acquirer 映射屬邏輯(協定,非策展資料)故 code 常數(#29b 明文豁免);下游 promote..vector_export 共用(channel-agnostic)。
CHANNEL_ACQUIRERS = {"local_files": "acquire_local_files.py", "sftp": "acquire_remote_files.py"}


def _file_channel_sources(cur, domain):
    sql = ("SELECT source_key, adapter FROM knowledge_source WHERE approval_status='active' "
           "AND adapter = ANY(%s)")
    params = [list(CHANNEL_ACQUIRERS)]
    if domain:
        sql += " AND domain = %s"; params.append(domain)
    cur.execute(sql + " ORDER BY source_key", params)
    return cur.fetchall()


def _upsert_channel_log(cur, source_key, status, rows):    # query_id=0 sentinel(與 harvest singles 同慣例;PK 靠 source_key 分)
    cur.execute("INSERT INTO knowledge_harvest_log (query_id, source_key, last_run, rows_staged, attempts, status) "
                "VALUES (0,%s,now(),%s,1,%s) ON CONFLICT (query_id, source_key) DO UPDATE SET "
                "last_run=now(), rows_staged=EXCLUDED.rows_staged, "
                "attempts=knowledge_harvest_log.attempts+1, status=EXCLUDED.status",
                (source_key, rows, status))


def harvest_file_channels(domain, limit):
    """驅動器 harvest 段之檔案通道迭代(件 A/G):每 active local_files/sftp 源 → 對應 acquirer subprocess
    (--acquire-only,下游交 DAG C3;acquire_local_files 無 --dir 時由 adapter_config.root_dir 取根 #29b)。
    前後 knowledge_item 計數差=rows,記 harvest_log(query_id=0);per-source try/except 續跑不中斷全鏈。零 token。"""
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            srcs = _file_channel_sources(cur, domain)
        if not srcs:
            print("  檔案通道:無 active 本機/SFTP 源(件 A 未註冊/未活化=空跑安全)", flush=True)
            return
        for sk, adapter in srcs:
            with db.transaction(conn) as cur:
                cur.execute("SELECT count(*) FROM knowledge_item WHERE source_key=%s", (sk,))
                before = cur.fetchone()[0]
            flag = "--source" if adapter == "sftp" else "--source-key"
            cmd = [PY, str(SCRIPTS / CHANNEL_ACQUIRERS[adapter]), flag, sk, "--acquire-only"]
            if limit:
                cmd += ["--limit", str(limit)]
            try:
                rc = subprocess.run(cmd, timeout=3600).returncode
            except Exception as e:
                rc = -1
                print(f"  ✗ 通道 {sk}({adapter}):{type(e).__name__}: {e}", flush=True)
            with db.transaction(conn) as cur:
                cur.execute("SELECT count(*) FROM knowledge_item WHERE source_key=%s", (sk,))
                rows = cur.fetchone()[0] - before
                _upsert_channel_log(cur, sk, "ok" if rows > 0 else ("empty" if rc == 0 else "error"), rows)
            print(f"  通道 {sk}({adapter}):+{rows} item rc={rc}", flush=True)


def _refresh_kh4_scope(domain, limit):
    if not domain:
        return
    with db.connect() as conn, db.transaction(conn) as cur:
        n = kh4.refresh_items(cur, domain=domain, limit=limit)
    print(f"  KH4 refresh(domain={domain}) → {n} item", flush=True)


def enforce_candidate_floor(stages, domain, floor):
    """M-G8 S1 候選數地板:選定段之待辦合計 < floor 即 exit≠0(空轉不得回綠)。

    只累加 BACKLOG_STAGES(真待辦語意);若選定段全無待辦語意則**判紅而非略過**——
    已請求之閘靜默失效正是本專案反覆踩的坑(記憶 guard-mechanisms-that-silently-fail)。
    """
    scoped = [s for s in stages if s.name in BACKLOG_STAGES]
    if not scoped:
        sys.exit(f"✗ --min-candidates 無從評估:選定段({' '.join(s.name for s in stages)})"
                 f"全屬全量重建/庫存語意、無待辦數可比。具待辦語意之段:{' '.join(sorted(BACKLOG_STAGES))}"
                 "(不靜默略過已請求之閘)")
    with db.connect() as conn, db.transaction(conn) as cur:
        per = {s.name: candidate_count(cur, s.name, domain) for s in scoped}
    total = sum(per.values())
    detail = " ".join(f"{k}={v:,}" for k, v in per.items())
    if total < floor:
        print(f"✗ 候選數地板未達:待辦合計 {total:,} < --min-candidates {floor}"
              f"(domain={domain or '全部域'};逐段 {detail})——中止(空轉不回綠)", file=sys.stderr)
        sys.exit(3)
    print(f"候選數地板通過:待辦合計 {total:,} ≥ {floor}(逐段 {detail})", flush=True)


def selftest():
    """--selftest:純紅綠自測(免 DB 免 API、零 usage;#18)。鎖 domain 判準與地板段集不變式。"""
    fails = []

    def chk(cond, msg):
        if not cond:
            fails.append(msg)

    known = {"chemistry", "finance_mgmt", "quant_finance", "erp_tiptop", "local"}
    ok, near = domain_verdict("chemistry", known)
    chk(ok and near == [], f"已存在域須判通過(得 ok={ok} near={near})")
    ok, near = domain_verdict("finance", known)
    chk(not ok, "不存在之域 finance 須判 fail-loud(本 bug 之本體:M-G8)")
    chk("finance_mgmt" in near, f"finance 須提示相近域 finance_mgmt(得 {near})")
    chk(domain_verdict("", known)[0] is False, "空字串域須判 fail(否則靜默退為全域放量)")
    chk(BACKLOG_STAGES <= set(NAMES), "BACKLOG_STAGES 須為段封閉集之子集")
    chk(not (BACKLOG_STAGES & {"stats", "stats_items", "bridge", "concordance", "vector_export"}),
        "庫存/全量重建語意段不得列入待辦地板(庫存數冒充待辦數=地板恆過之假綠)")
    # 非待辦語意之段須回 None(不觸 cursor=零 IO):回 0 或數字都會讓地板把庫存當待辦
    chk(candidate_count(None, "bridge", None) is None, "bridge 須回 None(無待辦語意)")
    chk(candidate_count(None, "stats_items", None) is None, "stats_items 須回 None(無待辦語意)")
    for line in fails:
        print(f"  ✗ {line}")
    print(f"{'✗ FAIL' if fails else '✓ PASS'} refresh_knowledge_pipeline --selftest:{len(fails)} 失敗")
    return 1 if fails else 0


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
    ap.add_argument("--min-candidates", dest="min_candidates", type=int, metavar="N",
                    help="M-G8 候選數地板:選定各段待辦合計 < N 即 rc≠0(預設關閉)")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測(免 DB 免 API)")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
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
    if args.min_candidates is not None and args.min_candidates <= 0:
        sys.exit("--min-candidates 須為正整數(0/負值=形同無地板,不得以此假裝有閘)")

    if len(sys.argv) == 1:   # 無參數=安全預設(#29a)
        print_matrix(None)
        print("\n用法見標頭執行指令矩陣;--dry-run 列印各段將執行指令(零執行)")
        return

    # M-G8 S1:domain 解析 fail-loud——先於一切(含 --dry-run)驗域存在,不存在即 rc≠0。
    # `is not None` 而非 truthy:`--domain ""` 原會靜默退化為全域放量(build_cmd 之 `if domain`)。
    if args.domain is not None:
        assert_domain_known(args.domain)

    stages = select_stages(args)
    if args.min_candidates is not None:
        enforce_candidate_floor(stages, args.domain, args.min_candidates)
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
        if st.name == "harvest":                             # 件 A/G:API topic 抓完 → 迭代本機/SFTP 檔案通道(下游共用)
            harvest_file_channels(args.domain, args.limit)
            _refresh_kh4_scope(args.domain, args.limit)
        with db.connect() as conn, db.transaction(conn) as cur:
            after = pending_lines(cur, st.name, args.domain)
        print(f"✓ {st.seg} {st.name} 完成 {time.time() - ts:.0f}s | 驗收計數(後):{'; '.join(after)}",
              flush=True)
        # 空轉哨兵(2026-07-31 加):rc=0 **不等於**有做事——S2 promote 曾因缺參數而
        # 「印用法即 exit 0」，DAG 照記 ✓ 完成，16,072 筆 pending 一筆未動。
        # 驗收計數與執行前逐字相同且其中含非零數 ⇒ 提示查核。**僅警示不中止**：
        # 相同亦可能是「確實無待辦」之誠實終態(如 resplit 恆 0)，二者此處分不出，故不擅判失敗。
        if before == after and any(int(n.replace(",", "")) > 0
                                   for n in re.findall(r"\d[\d,]*", "; ".join(after))):
            print(f"  ⚠ {st.name}:驗收計數與執行前**逐字相同**——rc=0 不代表有做事，"
                  "請確認是「確實無待辦」還是「空轉」(缺參數/前置未備)", flush=True)
        if st.name in {"promote", "fulltext", "sentences", "resplit", "embed", "kip"}:
            _refresh_kh4_scope(args.domain, args.limit)
    heartbeat(len(NAMES) - 1, child_pid=0)                   # 收尾 tick(child 清零)
    os.close(lock_fd)
    print(f"\n=== 全鏈完成 {(time.time() - t0) / 60:.1f} 分(冪等驗收:連跑兩次計數不變)===", flush=True)


if __name__ == "__main__":
    main()
