#!/usr/bin/env python
"""來源健康探測 CLI — approve/activate 前置閘之證據產生器(深抓計畫 §4.2;最小單位診斷)。

🎯 這支在做什麼(白話):對某來源打**一次最小請求**(limit=1、單一 benign 查詢),記錄 HTTP 狀態碼
   進 knowledge_source_review_log(action='probe', probe_result={http_status,...})——此即 curation
   審批狀態機 `_recent_probe_ok` 檢查的證據(§3.2:approve/activate 前置=近 30 日有 http_status=200
   之 probe)。**最小單位鐵律(#24/#25)**:單一請求、honor pace_seconds、只讀狀態不 bulk 落地
   (診斷 dry-run、非放量;#26 執行層界內);SPARQL/manual_file 無簡單 GET 端點者 graceful 記 note。
   probe 純寫 review_log 證據列,**不改 approval_status**(升級動作仍走 review CLI 之人閘)。

守 #25(最小單位單一請求)· #24(honor pace、不狂打)· #15(http_status 實測、非自報)· #29a/b。
   前置=migrate_source_governance.py --run。

執行指令矩陣:
  python scripts/probe_knowledge_source.py                      # 無參數:印矩陣+近期 probe 記錄(唯讀)
  python scripts/probe_knowledge_source.py --source arxiv       # 探一個來源(單一最小請求)
  python scripts/probe_knowledge_source.py --source arxiv --query "machine learning"  # 指定 benign 查詢
  python scripts/probe_knowledge_source.py --status approved    # 批次探某狀態全部來源(逐一 honor pace)
"""
import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import curation

UA = {"User-Agent": "augur-knowledge/1.0 (research; contact via repo)", "Accept": "application/json"}
_NO_HTTP = {"manual_file"}   # 無 HTTP 端點:graceful 記 note、不視為失敗


def _fill(tpl, query):
    """最小探測模板代換(limit=1、benign query);容 SPARQL 大括號、不用 .format。"""
    import os
    return (tpl.replace("{query}", urllib.parse.quote(query))
               .replace("{query_raw}", query)
               .replace("{limit}", "1")
               .replace("{email}", "").replace("{extra_filter}", "")
               .replace("{fraser_api_key}", os.environ.get("FRASER_API_KEY", "")))


def _probe_one(cur, key, query, actor):
    cur.execute("SELECT adapter, query_template, pace_seconds, approval_status, adapter_config "
                "FROM knowledge_source WHERE source_key=%s", (key,))
    r = cur.fetchone()
    if not r:
        print(f"✗ 來源不存在:{key}"); return None
    adapter, url_tpl, pace, status, acfg = r
    if adapter in _NO_HTTP:
        pr = {"http_status": None, "adapter": adapter, "note": "manual_file 無 HTTP 端點、跳過探測"}
        curation.transition(key, "probe", actor, probe_result=pr, reason="no-http-endpoint")
        print(f"— {key}: {adapter}(無 HTTP 端點,記 note)"); return pr
    if not url_tpl or not str(url_tpl).lower().startswith("http"):
        pr = {"http_status": None, "adapter": adapter, "note": f"無可探測 URL(query_template={url_tpl!r})"}
        curation.transition(key, "probe", actor, probe_result=pr, reason="no-url")
        print(f"⚠ {key}: 無可探測 URL"); return pr
    url = _fill(str(url_tpl), query)
    hdrs = dict(UA)               # adapter_config.auth_header:key 走 header 不進 URL(不落 review log)
    ah = (acfg or {}).get("auth_header")
    if ah:
        import os
        v = os.environ.get(ah.get("env", ""), "")
        if v:
            hdrs[ah["name"]] = v
    if pace:                      # #24 honor pace:探測前先 sleep 該來源步調(不狂打)
        time.sleep(min(float(pace), 5.0))
    t0 = time.time()
    http_status, note = None, ""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=30) as resp:
            http_status = resp.status
            resp.read(2048)       # 只讀前 2KB 確認可讀,不 bulk 落地(#25)
    except urllib.error.HTTPError as e:
        http_status, note = e.code, f"HTTPError {e.reason}"
    except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
        note = f"{type(e).__name__}: {str(e)[:80]}"
    ms = int((time.time() - t0) * 1000)
    pr = {"http_status": http_status, "elapsed_ms": ms, "adapter": adapter,
          "url": url[:200], "note": note}
    curation.transition(key, "probe", actor, probe_result=pr,
                        reason=f"probe http={http_status} {ms}ms")
    icon = "✓" if http_status == 200 else ("⚠" if http_status else "✗")
    print(f"{icon} {key}: http={http_status} {ms}ms {note}(status={status})")
    return pr


def _recent(cur):
    cur.execute("SELECT source_key, probe_result->>'http_status', probe_result->>'elapsed_ms', created_at "
                "FROM knowledge_source_review_log WHERE action='probe' ORDER BY review_id DESC LIMIT 15")
    rows = cur.fetchall()
    print("近期 probe 記錄:" if rows else "近期 probe 記錄:(無)")
    for r in rows:
        print(f"  {r[0]:<24} http={r[1] or '-':<5} {r[2] or '-':>6}ms  {r[3]:%Y-%m-%d %H:%M}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--source")
    ap.add_argument("--status")
    ap.add_argument("--query", default="test")
    ap.add_argument("--actor", default="probe_cli")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.source:
            _probe_one(cur, args.source, args.query, args.actor); conn.commit(); return 0
        if args.status:
            cur.execute("SELECT source_key FROM knowledge_source WHERE approval_status=%s ORDER BY source_key",
                        (args.status,))
            keys = [r[0] for r in cur.fetchall()]
            print(f"批次探測 {len(keys)} 個 {args.status} 來源(逐一 honor pace):")
            for k in keys:
                _probe_one(cur, k, args.query, args.actor); conn.commit()
            return 0
        print(__doc__.split("執行指令矩陣:")[1])
        _recent(cur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
