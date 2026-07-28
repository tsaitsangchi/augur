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
  python scripts/probe_knowledge_source.py --re3data-probe-one  # SRC-QUALIFY 步①:單倉先行(#25)
  python scripts/probe_knowledge_source.py --re3data-wave [--limit N]  # 步①放量(P4P5-go 授權;熔斷/resume)
  python scripts/probe_knowledge_source.py --selftest           # 零網路紅綠(OAI 解析純函式)
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

# ── SRC-QUALIFY 步①(P4P5-go,hugo 2026-07-28):OAI-PMH 端點證據波 ──
WAVE_PACE_S = 1.5      # 倉際步調(各異主機、單主機僅 2 請求;#24)
WAVE_FUSE = 5          # 連錯熔斷(#24 見訊號即停)
WAVE_ACTOR = "p4p5_wave_v1"
PROBE_FRESH_DAYS = 30  # 與 auto_review_sources P4 同時效


def pick_oai_endpoint(apis):
    """apis=[{url,type}] → 首個 OAI-PMH http(s) 端點|None。純函式。"""
    for a in apis or []:
        u = (a.get("url") or "").strip()
        if a.get("type") == "OAI-PMH" and u.lower().startswith("http"):
            return u
    return None


def parse_identify(xml_text):
    """OAI-PMH Identify 回應 → {ok, repository_name}。純函式;local-name 掃描容 namespace 差。
    ok=根為 OAI-PMH 且含 Identify 節點——**格式實證**,非僅 2xx(裸 2xx=弱證據,計畫 §八不採)。"""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {"ok": False, "repository_name": None}
    local = lambda t: t.rsplit("}", 1)[-1]  # noqa: E731
    if local(root.tag) != "OAI-PMH":
        return {"ok": False, "repository_name": None}
    name, has_identify = None, False
    for el in root.iter():
        ln = local(el.tag)
        if ln == "Identify":
            has_identify = True
        elif ln == "repositoryName" and name is None:
            name = (el.text or "").strip() or None
    return {"ok": has_identify, "repository_name": name}


def parse_list_size(xml_text):
    """OAI-PMH ListIdentifiers 首頁 → completeListSize int|None(倉自報數;無=誠實 None 不編 #9)。純函式。"""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    for el in root.iter():
        if el.tag.rsplit("}", 1)[-1] == "resumptionToken":
            v = el.attrib.get("completeListSize")
            if v and v.isdigit():
                return int(v)
    return None


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


def _oai_get(url, timeout=30):
    hdrs = dict(UA)
    hdrs["Accept"] = "text/xml, application/xml"
    with urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=timeout) as r:
        return r.status, r.read(262144).decode("utf-8", "replace")  # 首頁 ≤256KB,不 bulk(#25)


def _wave_candidates(cur, limit=None):
    """P1 路乙判入 ∩ 具 OAI-PMH ∩ 近 30 日無 probe(resume:成敗皆算已探,過期才重探)。"""
    from auto_review_sources import classify_licenses
    cur.execute("SELECT kind, pattern, regime FROM license_regime_map")
    rm = cur.fetchall()
    cur.execute("""SELECT s.source_key, s.adapter_config->'re3data'->'licenses',
                          s.adapter_config->'re3data'->'apis'
                   FROM knowledge_source s
                   WHERE s.approval_status='proposed' AND s.adapter_config ? 're3data'
                     AND NOT EXISTS (SELECT 1 FROM knowledge_source_review_log l
                                     WHERE l.source_key=s.source_key AND l.action='probe'
                                       AND l.created_at > now() - make_interval(days => %s))
                   ORDER BY s.source_key""", (PROBE_FRESH_DAYS,))
    out = []
    for k, lic, apis in cur.fetchall():
        url = pick_oai_endpoint(apis)
        if url and classify_licenses(lic or [], rm):
            out.append((k, url))
            if limit and len(out) >= limit:
                break
    return out


def _re3data_wave(conn, cur, limit=None):
    """SRC-QUALIFY 步①:每倉兩最小請求(Identify 格式實證+ListIdentifiers 首頁自報數)→ review_log。
    格式實證不過者 http_status 記 None(P4 fail-closed)、原始碼保留於 raw_http_status(誠實不滅證)。"""
    cands = _wave_candidates(cur, limit)
    if not cands:
        print("(無待探之合格倉——P1 判入∩OAI-PMH∩無新鮮 probe 為空)")
        return 0
    print(f"步①證據波:{len(cands)} 倉 × 2 請求(步調 {WAVE_PACE_S}s;熔斷 {WAVE_FUSE} 連錯)")
    n_ok = n_fail = errs = 0
    for i, (k, url) in enumerate(cands):
        sep = "&" if "?" in url else "?"
        t0 = time.time()
        st, note, name, size, raw = None, "", None, None, None
        try:
            raw, body = _oai_get(url + sep + "verb=Identify")
            ident = parse_identify(body)
            if ident["ok"]:
                st, name = raw, ident["repository_name"]
                try:
                    _, body2 = _oai_get(url + sep + "verb=ListIdentifiers&metadataPrefix=oai_dc")
                    size = parse_list_size(body2)
                except Exception as e:  # noqa: BLE001  首頁失敗:P4 仍成立、est 誠實缺
                    note = f"list-page: {type(e).__name__}"
                errs = 0
            else:
                note = "identify-parse-failed(2xx 但非 OAI 格式=弱證據,P4 不採)"
        except urllib.error.HTTPError as e:
            raw, note = e.code, f"HTTPError {e.reason}"
            errs += 1
        except Exception as e:  # noqa: BLE001
            note = f"{type(e).__name__}: {str(e)[:80]}"
            errs += 1
        ms = int((time.time() - t0) * 1000)
        pr = {"http_status": st, "raw_http_status": raw, "elapsed_ms": ms, "adapter": "generic_json",
              "url": url[:200], "protocol": "OAI-PMH", "complete_list_size": size,
              "repository_name": name, "note": note}
        curation.transition(k, "probe", WAVE_ACTOR, probe_result=pr,
                            reason=f"qualify-wave http={st} size={size} {ms}ms")
        conn.commit()
        n_ok += (st is not None)
        n_fail += (st is None)
        icon = "✓" if st else "✗"
        print(f"  {icon} {k}: http={st} size={size} {ms}ms {note}", flush=True)
        if errs >= WAVE_FUSE:
            print(f"⛔ 連 {WAVE_FUSE} 錯熔斷停跑(#24);已探 {i + 1} 倉可續跑")
            return 75
        time.sleep(WAVE_PACE_S)
    print(f"✓ 步①完成:{len(cands)} 倉(格式實證過 {n_ok}/未過 {n_fail})→ 步② set_source_pacing.py")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    IDENT = """<?xml version="1.0"?><OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
      <Identify><repositoryName>Test Repo</repositoryName><baseURL>http://x/oai</baseURL></Identify></OAI-PMH>"""
    LIST = """<?xml version="1.0"?><OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
      <ListIdentifiers><header><identifier>a:1</identifier></header>
      <resumptionToken completeListSize="8214" cursor="0">tok</resumptionToken></ListIdentifiers></OAI-PMH>"""
    chk("Identify 解析(ok+名)", parse_identify(IDENT) == {"ok": True, "repository_name": "Test Repo"})
    chk("非 OAI 根=ok False(格式實證,裸 2xx 不採)",
        parse_identify("<html><body>200 OK</body></html>")["ok"] is False)
    chk("壞 XML=ok False 不炸", parse_identify("not xml <<")["ok"] is False)
    chk("completeListSize 取倉自報數", parse_list_size(LIST) == 8214)
    chk("無 resumptionToken=None(誠實缺,#9 不編)",
        parse_list_size(LIST.replace("resumptionToken", "xToken")) is None)
    chk("非數字 size=None", parse_list_size(LIST.replace('"8214"', '"n/a"')) is None)
    chk("OAI 端點擇取(型別+http 前綴)", pick_oai_endpoint(
        [{"url": "ftp://x", "type": "FTP"}, {"url": "https://y/oai", "type": "OAI-PMH"}]) == "https://y/oai")
    chk("無 OAI=None", pick_oai_endpoint([{"url": "https://z", "type": "REST"}]) is None)
    import inspect
    src = inspect.getsource(_re3data_wave)
    chk("熔斷+步調在(#24)", "WAVE_FUSE" in src and "time.sleep(WAVE_PACE_S)" in src)
    chk("格式不過=http_status None+raw 保留(P4 fail-closed 且不滅證)",
        '"raw_http_status": raw' in src and "identify-parse-failed" in src)
    chk("resume=新鮮 probe 跳過(成敗皆算)", "NOT EXISTS" in inspect.getsource(_wave_candidates))
    chk("不變式:wave 零 UPDATE/INSERT knowledge_source(純寫 review_log)",
        "UPDATE" not in src and "INSERT" not in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


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
    ap.add_argument("--re3data-wave", action="store_true")
    ap.add_argument("--re3data-probe-one", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.re3data_probe_one:
            return _re3data_wave(conn, cur, limit=1)
        if args.re3data_wave:
            return _re3data_wave(conn, cur, limit=args.limit)
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
