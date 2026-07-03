#!/usr/bin/env python
"""全球知識 harvest 批次驅動器 — registry(query×source×taxonomy)排程矩陣驅動 acquire→staging→promote 全鏈落地。

🎯 這支在做什麼(白話):讀 DB registry 三表(knowledge_query 詞彙 × knowledge_source 來源 ×
   knowledge_taxonomy 分類樹),組成「查詢型/單跑型」排程矩陣,逐組合 subprocess 呼叫
   acquire_knowledge.py 抓 metadata 入 knowledge_staging,輪末呼叫 promote_knowledge.py 晉升
   (七類條目→knowledge_item;thinker 僅單跑型來源自動、查詢型留審)。進度記 knowledge_harvest_log
   (resume 心臟:已跑 skip、error 重試上限 2 除役、429/503=暫時錯不除役)。啟動時自建全部 harvest
   DDL(冪等;DDL migrate 住所=本 script)。計畫 SSOT=reports/augur_knowledge_harvest_landing_plan_20260702.md(v1.3)。
守 #1(真實來源+lineage 全鏈 item→staging→query→taxonomy)· #6/#22(冪等、每組合獨立交易 resume-safe)·
   #15(harvest_log 誠實帳本,empty=正常結果)· #17(限速矩陣+熔斷+Retry 訊號即停)· #28(本地批次零 LLM)· CLAUDE #29。

執行指令矩陣:
  python scripts/harvest_knowledge.py                          # 無參數:冪等 migrate+診斷+排程統計+用法(不打 API)
  python scripts/harvest_knowledge.py --migrate-only           # 只建 DDL/domain_map 種子/note→taxonomy_id 遷移
  python scripts/harvest_knowledge.py --dry-run --batch 10     # 只印排程、不打 API 不寫 log
  python scripts/harvest_knowledge.py --batch 10 --rounds 1    # 首輪最小驗證(#25)
  python scripts/harvest_knowledge.py --batch 300 --rounds 4 --max-minutes 120   # 常規背景批
  python scripts/harvest_knowledge.py --domain solar_materials --batch 100       # 圈域跑(augur 域)
  python scripts/harvest_knowledge.py --singles-only           # 只跑單跑型來源(dbpedia 獎項/域名單)
"""
import re
import sys
import time
import argparse
import subprocess
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

SCRIPT_DIR = Path(__file__).resolve().parent

# 查詢型 entity 允許集(計畫 v1.3:排除 thinker 概念實體即可,勿白名單誤殺 compound/material 等合法源)
QUERY_ENTITY_GATE = ("work", "compound", "material", "protein", "species")
ITEM_TYPES = ("paper", "report", "dataset", "compound", "material", "protein", "species")
# 明文故意不入 harvest 排程(哲學全文走既有 fetch 工具鏈,計畫 §三6)
PHILOSOPHY_EXEMPT = {"ctext_books", "gutendex_search"}

# domain_map 覆寫種子(計畫 §二3 明文列舉,僅決策層已拍板域;新對映=INSERT/UPDATE 零 code)
DOMAIN_MAP_OVERRIDES = {
    "materials_science": "energy_materials",
    "energy": "energy_materials",
    "economics_econometrics_and_finance": "finance_mgmt",
    "business_management_and_accounting": "business_mgmt",
    "decision_sciences": "organization_mgmt",
    "chemistry": "chemistry",
    "chemical_engineering": "chemistry",
    "physics_and_astronomy": "physics",
    "biochemistry_genetics_and_molecular_biology": "biology",
    "engineering": "electronics",
}

# ── DDL(計畫 §二;全部冪等,ADD COLUMN IF NOT EXISTS 含 inline FK 亦冪等) ─────────
DDL = [
    """CREATE TABLE IF NOT EXISTS knowledge_item (
         item_id      serial PRIMARY KEY,
         domain       varchar(64) NOT NULL,
         entity_type  varchar(32) NOT NULL,          -- paper/report/dataset/compound/material/protein/species…
         title        text NOT NULL,
         title_zh     text,
         year         int,
         authors      text,                          -- 分號串(顯示);正規化人物住 thinker
         external_id  text,                          -- 跨源去重鍵(優先序見計畫 §二5)
         venue        text,
         url          text,                          -- 可溯源(#1)
         taxonomy_id  int REFERENCES knowledge_taxonomy(tax_id),
         source_key   varchar(64) REFERENCES knowledge_source(source_key),
         staging_id   int,                           -- 回溯原始 payload;故意不設 FK(staging 可歸檔清理)
         ingested_at  timestamptz DEFAULT now()
       )""",
    # v1.2:僅無 external_id 者用 title+year 去重(同名同年不同 DOI 不相撞)
    """CREATE UNIQUE INDEX IF NOT EXISTS uq_item_extid ON knowledge_item (entity_type, external_id)
         WHERE external_id IS NOT NULL""",
    """CREATE UNIQUE INDEX IF NOT EXISTS uq_item_title ON knowledge_item (entity_type, md5(title), COALESCE(year,0))
         WHERE external_id IS NULL""",
    "CREATE INDEX IF NOT EXISTS idx_item_domain ON knowledge_item (domain, entity_type)",
    "CREATE INDEX IF NOT EXISTS idx_item_tax ON knowledge_item (taxonomy_id)",
    """CREATE TABLE IF NOT EXISTS knowledge_harvest_log (
         query_id    int NOT NULL DEFAULT 0,         -- 0=單跑型 sentinel;故意不設 FK(0 無對應列;>0 由寫入時保證)
         source_key  varchar(64) REFERENCES knowledge_source(source_key),
         last_run    timestamptz,
         rows_staged int,
         attempts    int DEFAULT 1,                  -- 永久性 error 重試上限 2,防無限重跑;temp 錯不累加
         status      varchar(16) CHECK (status IN ('ok','empty','error')),
         note        text,
         PRIMARY KEY (query_id, source_key)
       )""",
    """CREATE TABLE IF NOT EXISTS knowledge_domain_map (
         openalex_field varchar(64) PRIMARY KEY,     -- OpenAlex field slug 或手動域(恆等列)
         augur_domain   varchar(64) NOT NULL
       )""",
    "ALTER TABLE knowledge_staging ADD COLUMN IF NOT EXISTS query_id int",
    "ALTER TABLE knowledge_query ADD COLUMN IF NOT EXISTS taxonomy_id int REFERENCES knowledge_taxonomy(tax_id)",
]

# ── 排程 SQL 核心(psycopg 參數化執行;LIKE 字面 % 因帶參數須寫 %%,呼叫端一律傳 params) ──
_Q_CORE = (
    " FROM knowledge_query q"
    " JOIN knowledge_domain_map m ON m.openalex_field = q.domain"          # 手動域=恆等列;未拍板 field 天然排除(治理閘)
    " JOIN knowledge_source s ON s.enabled"
    "  AND s.adapter <> 'manual_file'"
    "  AND s.query_template LIKE '%%{query}%%'"                            # 查詢型=含 {query};僅含 {query_raw}=ID 驅動型不入(§三1c)
    "  AND s.entity_type IN ('work','compound','material','protein','species')"
    "  AND (s.domain = 'general' OR s.domain = m.augur_domain)"
    " LEFT JOIN knowledge_harvest_log l ON l.query_id = q.query_id AND l.source_key = s.source_key"
    " WHERE q.enabled AND (l.status IS NULL OR (l.status = 'error' AND l.attempts < 2))")

_S_CORE = (
    " FROM knowledge_source s"
    " LEFT JOIN knowledge_harvest_log l ON l.query_id = 0 AND l.source_key = s.source_key"  # 0=單跑型 sentinel
    " WHERE s.enabled AND s.adapter <> 'manual_file'"
    "  AND COALESCE(s.query_template,'') <> ''"
    "  AND s.query_template NOT LIKE '%%{query}%%'"
    "  AND s.query_template NOT LIKE '%%{query_raw}%%'"
    "  AND (l.status IS NULL OR (l.status = 'error' AND l.attempts < 2))")


def migrate(conn):
    """§二全部 DDL + domain_map 種子 + note→taxonomy_id 冪等補漏(每輪前可安全重放,計畫 §八之一1)。"""
    with db.transaction(conn) as cur:
        for stmt in DDL:
            cur.execute(stmt)
        # 恆等列:手動域資料驅動(manual 詞本身即決策層策展);覆寫列:明文常數(§二3 僅拍板域)
        cur.execute("SELECT DISTINCT domain FROM knowledge_query WHERE origin='manual'")
        manual = [r[0] for r in cur.fetchall()]
        for d in manual:
            cur.execute("INSERT INTO knowledge_domain_map VALUES (%s,%s) ON CONFLICT (openalex_field) DO NOTHING", (d, d))
        for f, d in DOMAIN_MAP_OVERRIDES.items():
            cur.execute("INSERT INTO knowledge_domain_map VALUES (%s,%s) ON CONFLICT (openalex_field) DO NOTHING", (f, d))
        cur.execute("UPDATE knowledge_query q SET taxonomy_id = t.tax_id FROM knowledge_taxonomy t "
                    "WHERE q.origin='openalex_taxonomy' AND q.taxonomy_id IS NULL AND t.openalex_id = q.note")
        backfilled = cur.rowcount
        cur.execute("SELECT count(*) FROM knowledge_domain_map")
        n_map = cur.fetchone()[0]
    print(f"migrate:DDL 冪等完成;domain_map {n_map} 列(手動恆等 {len(manual)}+明文覆寫 {len(DOMAIN_MAP_OVERRIDES)});"
          f"note→taxonomy_id 補漏 {backfilled} 列")


def diagnostics(conn):
    """啟動診斷(計畫 §三6):未配對域統計 + 零排程來源清單(source 側鏡像)+ ID 驅動型告知。純 DB 不打 API。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT q.domain, count(*) FROM knowledge_query q"
                    " LEFT JOIN knowledge_domain_map m ON m.openalex_field = q.domain"
                    " WHERE q.enabled AND m.openalex_field IS NULL GROUP BY 1 ORDER BY 2 DESC")
        un = cur.fetchall()
        if un:
            print(f"未配對域(不入排程;納入新域=決策層 INSERT knowledge_domain_map):{len(un)} 域 {sum(n for _, n in un)} 詞")
            for d, n in un:
                print(f"    {d:48} {n:>5} 詞")
        cur.execute("SELECT s.source_key, s.domain, s.entity_type,"
                    " (SELECT count(*) FROM knowledge_query q JOIN knowledge_domain_map m ON m.openalex_field = q.domain"
                    "   WHERE q.enabled AND (s.domain = 'general' OR s.domain = m.augur_domain))"
                    " FROM knowledge_source s"
                    " WHERE s.enabled AND s.adapter <> 'manual_file' AND COALESCE(s.query_template,'') LIKE '%{query}%'"
                    " ORDER BY s.source_key")
        zero = []
        for skey, sdom, s_et, n_matched in cur.fetchall():
            if s_et not in QUERY_ENTITY_GATE:
                zero.append((skey, f"entity 閘排除(entity={s_et};v1.2 治理:概念實體不入詞彙排程)"))
            elif n_matched == 0:
                why = ("明文故意不入 harvest(哲學全文走既有 fetch 工具鏈)" if skey in PHILOSOPHY_EXEMPT
                       else f"配不到任何 query(domain={sdom} 無對映)")
                zero.append((skey, why))
        if zero:
            print(f"零排程來源(enabled 查詢型中配不到詞者):{len(zero)} 源")
            for skey, why in zero:
                print(f"    {skey:32} {why}")
        cur.execute("SELECT source_key FROM knowledge_source WHERE enabled"
                    " AND COALESCE(query_template,'') LIKE '%{query_raw}%' AND query_template NOT LIKE '%{query}%'"
                    " ORDER BY source_key")
        ids = [r[0] for r in cur.fetchall()]
        if ids:
            print(f"ID 驅動型來源(收 ID 非詞彙,不入排程;僅手動 acquire/上游 ID feed):{', '.join(ids)}")


def load_query_schedule(cur, batch, domain):
    sql = "SELECT q.query_id, q.query, m.augur_domain, s.source_key, s.entity_type" + _Q_CORE
    params = []
    if domain:
        sql += " AND m.augur_domain = %s"
        params.append(domain)
    sql += (" ORDER BY (q.origin = 'manual') DESC,"
            " (SELECT works_count FROM knowledge_taxonomy t WHERE t.tax_id = q.taxonomy_id) DESC NULLS LAST,"
            " q.query_id, s.source_key LIMIT %s")
    params.append(batch)
    cur.execute(sql, params)
    return cur.fetchall()


def count_query_schedule(cur, domain):
    sql = "SELECT count(*)" + _Q_CORE
    params = []
    if domain:
        sql += " AND m.augur_domain = %s"
        params.append(domain)
    cur.execute(sql, params)   # params 可為空 list:仍須傳(讓 psycopg 把 %% 展開為字面 %)
    return cur.fetchone()[0]


def load_singles(cur, domain):
    sql = "SELECT s.source_key, s.domain, s.entity_type" + _S_CORE
    params = []
    if domain:
        sql += " AND s.domain = %s"
        params.append(domain)
    sql += " ORDER BY s.source_key"
    cur.execute(sql, params)
    return cur.fetchall()


def pace(source_key):
    """限速矩陣(#17,計畫 §三2):per-source sleep 秒數。"""
    for prefix, sec in (("openalex", 0.5), ("crossref", 1.0), ("dbpedia", 3.0)):
        if source_key.startswith(prefix):
            return sec
    return 1.5


def run_acquire(cli_args, timeout):
    """subprocess 跑 acquire 一組合;回 (status, rows_staged, note)。429/503/timeout=temp(不 attempts++)。"""
    cmd = [sys.executable, str(SCRIPT_DIR / "acquire_knowledge.py")] + cli_args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "error", 0, "temp:subprocess timeout(暫時性,不計 attempts)"
    if proc.returncode != 0:
        err = " ".join((proc.stderr or proc.stdout or "").strip().split())
        if "HTTP Error 429" in err or "HTTP Error 503" in err:
            return "error", 0, ("temp:" + err[-200:])
        return "error", 0, err[-240:]
    m = re.search(r"staging \+(\d+)", proc.stdout or "")
    n = int(m.group(1)) if m else 0
    return ("ok" if n > 0 else "empty"), n, None


def upsert_log(cur, query_id, source_key, status, rows, note, inc_attempt):
    cur.execute(
        "INSERT INTO knowledge_harvest_log (query_id, source_key, last_run, rows_staged, attempts, status, note)"
        " VALUES (%s,%s,now(),%s,%s,%s,%s)"
        " ON CONFLICT (query_id, source_key) DO UPDATE SET"
        "  last_run = now(), rows_staged = EXCLUDED.rows_staged, status = EXCLUDED.status, note = EXCLUDED.note,"
        "  attempts = knowledge_harvest_log.attempts + %s",
        (query_id, source_key, rows, 1 if inc_attempt else 0, status, note, 1 if inc_attempt else 0))


def round_end_promote(staged_ok):
    """輪末晉升(計畫 §三3 v1.2 治理):work/七類 item 自動;thinker 僅單跑型來源 --source 篩。"""
    cmds = [["--entity-type", et] for et in sorted({et for et, _, _ in staged_ok if et == "work" or et in ITEM_TYPES})]
    cmds += [["--entity-type", "thinker", "--source", sk]
             for et, sk, single in sorted(staged_ok) if et == "thinker" and single]
    for extra in cmds:
        proc = subprocess.run([sys.executable, str(SCRIPT_DIR / "promote_knowledge.py")] + extra,
                              capture_output=True, text=True, timeout=900)
        out = (proc.stdout or "").strip().splitlines()
        tail = out[-1] if out else " ".join((proc.stderr or "").strip().split())[-160:]
        print(f"  promote {' '.join(extra)} → {tail}")


def run_rounds(conn, args):
    batch = args.batch or 10
    deadline = time.monotonic() + args.max_minutes * 60
    t0 = time.monotonic()
    grand = {"ok": 0, "empty": 0, "error": 0, "staged": 0}
    for rnd in range(1, args.rounds + 1):
        if time.monotonic() > deadline:
            print("max-minutes 觸頂——收尾自停(#28 一次啟動一次通知)")
            break
        with db.transaction(conn) as cur:
            singles = load_singles(cur, args.domain)
            qcombos = [] if args.singles_only else load_query_schedule(cur, batch, args.domain)
            avail = count_query_schedule(cur, args.domain)
        plan = ([("single", 0, None, d, sk, et) for sk, d, et in singles] +
                [("query", qid, q, d, sk, et) for qid, q, d, sk, et in qcombos])
        print(f"── 第 {rnd}/{args.rounds} 輪:單跑型 {len(singles)} + 查詢型 {len(qcombos)}(查詢型可排總量 {avail})")
        if not plan:
            print("排程空(全部已跑或除役)——收尾")
            break
        if args.dry_run:
            for kind, qid, q, d, sk, et in plan[:40]:
                if kind == "single":
                    print(f"  [單跑] {sk} (entity={et}, domain={d}, limit=500)")
                else:
                    print(f"  [查詢] {sk} ← {q!r} (domain={d}, qid={qid}, limit=25)")
            if len(plan) > 40:
                print(f"  … 共 {len(plan)} 組")
            print("dry-run:不打 API、不寫 log、不 promote")
            break
        tripped, consec = set(), {}
        staged_ok = set()
        stats = {"ok": 0, "empty": 0, "error": 0, "staged": 0, "skipped": 0}
        for i, (kind, qid, q, d, sk, et) in enumerate(plan, 1):
            if time.monotonic() > deadline:
                print("  max-minutes 觸頂——本輪提前收尾(已跑部分照常 promote)")
                break
            if sk in tripped:
                stats["skipped"] += 1
                continue
            if kind == "single":
                status, n, note = run_acquire(["--source", sk, "--limit", "500"], timeout=300)
                if status == "ok" and n >= 500:   # #18 探測:回滿 limit=可能未盡,誠實記帳
                    note = "full:回滿 limit=500,可能未盡——提高 --limit 以 acquire 手動補齊"
            else:
                status, n, note = run_acquire(["--source", sk, "--query", q, "--domain", d,
                                               "--query-id", str(qid), "--limit", "25"], timeout=180)
            temp = bool(note) and note.startswith("temp:")
            with db.transaction(conn) as cur:   # 每組合獨立交易=中斷 resume-safe(#6/#22)
                upsert_log(cur, qid, sk, status, n, note, inc_attempt=(status == "error" and not temp))
            stats[status] += 1
            stats["staged"] += n
            if status == "ok":
                staged_ok.add((et, sk, kind == "single"))
            if status == "error":
                consec[sk] = consec.get(sk, 0) + 1
                if consec[sk] >= 5:   # 熔斷:同源本輪連 5 錯,跳過其餘組合(下輪由 log 續)
                    tripped.add(sk)
                    print(f"  ⛔ 熔斷 {sk}(連 {consec[sk]} 錯,本輪跳過其餘組合)")
            else:
                consec[sk] = 0
            mark = {"ok": f"ok +{n}", "empty": "empty", "error": ("temp" if temp else "error")}[status]
            print(f"  [{i}/{len(plan)}] {sk} ← {q!r} → {mark}" if kind == "query"
                  else f"  [{i}/{len(plan)}] {sk}(單跑)→ {mark}")
            time.sleep(pace(sk))
        if staged_ok:
            round_end_promote(staged_ok)
        for k in ("ok", "empty", "error", "staged"):
            grand[k] += stats[k]
        print(f"── 第 {rnd} 輪統計:ok {stats['ok']} / empty {stats['empty']} / error {stats['error']}"
              f" / 熔斷跳過 {stats['skipped']} / staged +{stats['staged']};熔斷源 {sorted(tripped) or '無'}")
    print(f"═ 收尾:ok {grand['ok']} / empty {grand['empty']} / error {grand['error']} / staged +{grand['staged']}"
          f";elapsed {(time.monotonic() - t0) / 60:.1f} 分。resume 由 harvest_log 驅動,直接重跑即續。")


def print_stats(conn, domain):
    with db.transaction(conn) as cur:
        avail = count_query_schedule(cur, domain)
        singles = load_singles(cur, domain)
        cur.execute("SELECT status, count(*), COALESCE(sum(rows_staged),0) FROM knowledge_harvest_log GROUP BY 1 ORDER BY 1")
        log = cur.fetchall()
    print(f"排程統計:查詢型待跑組合 {avail};單跑型待跑 {len(singles)}(以排程 SQL 實算,計畫值=快照非承諾)")
    if log:
        print("harvest_log 帳本:" + ";".join(f"{s} {c} 組(staged {r})" for s, c, r in log))
    else:
        print("harvest_log 帳本:空(尚未跑過)")


def main():
    sys.stdout.reconfigure(line_buffering=True)   # 背景跑時進度即時可見(#21)
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--batch", type=int)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--max-minutes", dest="max_minutes", type=float, default=120.0)
    ap.add_argument("--domain")
    ap.add_argument("--singles-only", dest="singles_only", action="store_true")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true")
    ap.add_argument("--migrate-only", dest="migrate_only", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        migrate(conn)                      # DDL migrate 住所=本 script(計畫 v1.3),冪等可重放
        diagnostics(conn)
        if args.migrate_only:
            print("--migrate-only 完成(DDL/種子/遷移皆冪等)")
            return
        if args.batch is None and not (args.singles_only or args.dry_run):
            print(__doc__.split("執行指令矩陣:")[1])
            print_stats(conn, args.domain)
            return
        run_rounds(conn, args)


if __name__ == "__main__":
    main()
