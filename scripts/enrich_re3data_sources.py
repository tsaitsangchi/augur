#!/usr/bin/env python
"""re3data 逐倉充實器 — 官方 API 回填 license/端點證據,讓 SRC-AUTO 謂詞有料可判(SRC-ENRICH-go)。

🎯 這支在做什麼(白話):proposed 積壓大宗(~3,520)是 re3data 逐倉目錄列,無 license、無端點——
   謂詞引擎對它們永遠 fail-closed。re3data 官方 API(免費、公開)每倉皆載 dataLicense 與 api 端點:
   本支以**受控步調**逐倉 GET → 解析 XML → 證據寫回 `knowledge_source.adapter_config->'re3data'`
   (jsonb:licenses/apis/repository_name/fetched_at)。**只回填證據、不改審批狀態**——license 證據
   之採認(dataLicense 名→regime 映射)=規則 v2,人簽後才進 P1。
   #24:步調 1.2s/倉+錯誤退避,連 5 錯熔斷停跑;#25:--probe 先單倉驗格式,通了才 --run 放量
   (放量授權=hugo 2026-07-28「SRC-ENRICH-go」/「1,2,3都執行」);resume=已充實者跳過,可中斷續跑。
守 #24/#25 · #9/#10(證據原文入 jsonb 可溯)· #15(解析不到=誠實記 miss,不編)· #26 · #29a/d。
SSOT=reports/augur_source_auto_review_plan_20260728.md §七 P1.5。

執行指令矩陣:
  python scripts/enrich_re3data_sources.py             # 無參數:現況(待充實/已充實/miss 統計,唯讀)
  python scripts/enrich_re3data_sources.py --probe     # 單倉最小探測(#25;印解析結果、寫該倉)
  python scripts/enrich_re3data_sources.py --run       # 全量充實(~3,520 倉×1.2s≈1.5h;resume-safe)
  python scripts/enrich_re3data_sources.py --run --limit 50
  python scripts/enrich_re3data_sources.py --selftest  # 零網路紅綠(XML 解析 fixture)
"""
import argparse
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

import _bootstrap  # noqa: F401
from augur.core import db

API = "https://www.re3data.org/api/v1/repository/{rid}"
PACE_S = 1.2
ERR_FUSE = 5          # 連錯熔斷(#24 見訊號即停)
UA = {"User-Agent": "augur-src-enrich/1.0 (research; contact=local)"}


def parse_repo_xml(xml_text):
    """解析 re3data repository XML → {repository_name, licenses[], apis[]}。純函式。
    re3data schema 帶 namespace;以 local-name 掃描(容 2.2/2.3 版差)。找不到=誠實空列不編。"""
    root = ET.fromstring(xml_text)

    def local(tag):
        return tag.rsplit("}", 1)[-1]

    name, licenses, apis = None, [], []
    for el in root.iter():
        ln = local(el.tag)
        if ln == "repositoryName" and name is None:
            name = (el.text or "").strip() or None
        elif ln == "dataLicense":
            lic = {}
            for ch in el:
                cl = local(ch.tag)
                if cl == "dataLicenseName":
                    lic["name"] = (ch.text or "").strip()
                elif cl == "dataLicenseURL":
                    lic["url"] = (ch.text or "").strip()
            if lic:
                licenses.append(lic)
        elif ln == "api":
            api = {"url": (el.text or "").strip()}
            t = el.attrib.get("apiType") or el.attrib.get("{http://www.re3data.org/schema/2-2}apiType")
            if t:
                api["type"] = t
            if api["url"]:
                apis.append(api)
    return {"repository_name": name, "licenses": licenses, "apis": apis}


def fetch_repo(rid, timeout=30):
    req = urllib.request.Request(API.format(rid=rid), headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def pending_rows(cur, limit=None):
    cur.execute("""SELECT source_key FROM knowledge_source
        WHERE approval_status='proposed' AND source_key LIKE 're3data_r3d%%'
          AND NOT (coalesce(adapter_config,'{}'::jsonb) ? 're3data')
        ORDER BY source_key""" + (" LIMIT %s" if limit else ""),
        (limit,) if limit else ())
    return [r[0] for r in cur.fetchall()]


def enrich(limit=None, probe=False):
    with db.connect() as conn:
        cur = conn.cursor()
        keys = pending_rows(cur, 1 if probe else limit)
        if not keys:
            print("(無待充實之 re3data proposed 列)")
            return 0
        n_ok = n_miss = errs = 0
        t0 = time.monotonic()
        for i, k in enumerate(keys):
            rid = k.split("re3data_", 1)[1]
            try:
                data = parse_repo_xml(fetch_repo(rid))
                errs = 0
            except Exception as e:  # noqa: BLE001  單倉失敗:誠實記、退避、連錯熔斷
                errs += 1
                print(f"  ✗ {k}: {type(e).__name__}(連錯 {errs}/{ERR_FUSE})")
                if errs >= ERR_FUSE:
                    print(f"⛔ 連 {ERR_FUSE} 錯熔斷停跑(#24 見訊號即停);已充實 {n_ok} 倉可續跑")
                    conn.commit()
                    return 75
                time.sleep(PACE_S * 4)
                continue
            data["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            payload = json.dumps({"re3data": data}, ensure_ascii=False)
            cur.execute("""UPDATE knowledge_source
                SET adapter_config = coalesce(adapter_config,'{}'::jsonb) || %s::jsonb
                WHERE source_key=%s AND approval_status='proposed'""", (payload, k))
            got = bool(data["licenses"] or data["apis"])
            n_ok += got
            n_miss += (not got)
            if probe:
                print(f"── #25 單倉探測 {k} ──")
                print(json.dumps(data, ensure_ascii=False, indent=1)[:600])
            if (i + 1) % 100 == 0:
                conn.commit()
                el = time.monotonic() - t0
                print(f"  …{i + 1}/{len(keys)}(有料 {n_ok}/miss {n_miss};{el / 60:.0f} 分;"
                      f"估餘 {(len(keys) - i - 1) * (el / (i + 1)) / 60:.0f} 分)", flush=True)
            time.sleep(PACE_S)
        conn.commit()
    print(f"✓ 充實完成:{len(keys)} 倉(license/api 有料 {n_ok}、誠實 miss {n_miss})")
    print("  → 下一步:dry 分桶重看;dataLicense 名→regime 映射=規則 v2(人簽)後 P1 才吃這批證據")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT
            count(*) FILTER (WHERE NOT (coalesce(adapter_config,'{}'::jsonb) ? 're3data')) AS pend,
            count(*) FILTER (WHERE adapter_config ? 're3data') AS done,
            count(*) FILTER (WHERE adapter_config ? 're3data'
                AND jsonb_array_length(adapter_config->'re3data'->'licenses') > 0) AS with_lic
            FROM knowledge_source
            WHERE approval_status='proposed' AND source_key LIKE 're3data_r3d%'""")
        pend, done, with_lic = cur.fetchone()
        print(f"  待充實 {pend}｜已充實 {done}(含 license 證據 {with_lic})")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    FIX = """<?xml version="1.0"?>
<r3d:re3data xmlns:r3d="http://www.re3data.org/schema/2-2">
 <r3d:repository>
  <r3d:repositoryName language="eng">Odum Institute Dataverse</r3d:repositoryName>
  <r3d:dataLicense><r3d:dataLicenseName>CC0</r3d:dataLicenseName>
   <r3d:dataLicenseURL>https://creativecommons.org/publicdomain/zero/1.0/</r3d:dataLicenseURL>
  </r3d:dataLicense>
  <r3d:api apiType="OAI-PMH">https://dataverse.unc.edu/oai</r3d:api>
 </r3d:repository>
</r3d:re3data>"""
    d = parse_repo_xml(FIX)
    chk("解析 repositoryName", d["repository_name"] == "Odum Institute Dataverse")
    chk("解析 dataLicense(name+url)", d["licenses"] == [{"name": "CC0",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/"}])
    chk("解析 api(type+url)", d["apis"] == [{"url": "https://dataverse.unc.edu/oai", "type": "OAI-PMH"}])
    chk("無 license 之倉=誠實空列不編", parse_repo_xml(
        FIX.replace("dataLicense", "xLicense"))["licenses"] == [])
    import inspect
    src = inspect.getsource(enrich)
    chk("步調常數在(#24)", PACE_S >= 1.0 and "time.sleep(PACE_S)" in src)
    chk("連錯熔斷(#24 見訊號即停)", "ERR_FUSE" in src and "熔斷停跑" in src)
    chk("只回填證據不改審批狀態", "approval_status='proposed'" in src
        and "SET approval_status" not in src)
    chk("resume:已充實者不重抓", "? 're3data'" in inspect.getsource(pending_rows))
    chk("逐 100 倉 commit(中斷不失進度)", "% 100 == 0" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="re3data 逐倉充實器(SRC-ENRICH;證據回填,不改審批)")
    ap.add_argument("--probe", action="store_true", help="#25 單倉最小探測")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.probe:
        return enrich(probe=True)
    if a.run:
        return enrich(limit=a.limit)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
