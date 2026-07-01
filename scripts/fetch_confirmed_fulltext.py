#!/usr/bin/env python
"""執行層:依 triage workflow 對抗驗證後之 confirmed 清單,抓所有合法公版版本(原文+譯本)填 work_text。

🎯 讀 confirmed JSON(work_id + language + actual_txt_url + source_type,皆經理解層對抗驗證=真實合法公版),
   本地下載解析逐字填 philosophy_work_text(填**現有** work_id、多語言版本並存、標 language 欄)。
   有原文抓原文、有公版譯本也一併抓——同一著作可存多語言全文。
守 #1(逐字無 AI 摘要、源經對抗驗證)· #15(限公版 license CHECK)· #28(本地零 usage)· #25(限速友善)。
⚠️ 僅抓 confirmed(對抗驗證通過)者;版權/未確認一律不抓(命門:寧缺勿抓假/侵權)。

用法:PYTHONPATH=src python scripts/fetch_confirmed_fulltext.py <confirmed.json>
"""
import re
import sys
import json
import time
import socket
import urllib.request

from augur.core import db

socket.setdefaulttimeout(45)
UA = {"User-Agent": "augur-research/1.0 (public-domain full-text archival)"}
CHAP_RE = (r"^\s*(BOOK [IVXLC]+|CHAPTER [IVXLC0-9]+|PART [IVX]+|SECTION [IVX]+|LECTURE [IVX]+"
           r"|KAPITEL \d+|CHAPITRE [IVXLC0-9]+|LIVRE [IVX]+)\.?\s*$")


def download(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode("utf-8", "replace")


def strip_gutenberg(txt):
    s = re.search(r"\*\*\* ?START OF TH[EI][^*]*\*\*\*", txt)
    start = s.end() if s else 0
    e = re.search(r"\*\*\* ?END OF TH[EI][^*]*\*\*\*", txt) or re.search(r"\nEnd of (?:the )?Project Gutenberg", txt)
    end = e.start() if e else len(txt)
    body = txt[start:end].strip()
    body = re.sub(r"\[\[[^\]]*?\]\]", "", body).replace("[[", "").replace("]]", "")
    body = "\n".join(l for l in body.split("\n")
                     if "Project Gutenberg" not in l and not l[:40].strip().startswith(("Produced by", "Transcribed", "E-text")))
    return body.strip()


def clean_wikitext(txt):
    txt = re.sub(r"-\{(?:[a-zA-Z-]+:)?([^{}|;]*)(?:;[^{}]*)?\}-", r"\1", txt)   # 繁簡轉換標記
    for _ in range(6):
        txt = re.sub(r"\{\{[^{}]*\}\}", "", txt)                                 # 巢狀模板
    txt = re.sub(r"<ref[^>]*>.*?</ref>", "", txt, flags=re.S)                    # 註腳
    txt = re.sub(r"\[\[(?:[^\[\]|]*\|)?([^\[\]]*)\]\]", r"\1", txt)              # 內部連結留顯示字
    txt = re.sub(r"\[https?://[^\]\s]+\s*([^\]]*)\]", r"\1", txt)                # 外部連結
    txt = re.sub(r"<[^>]+>", "", txt)                                            # HTML tag
    txt = re.sub(r"^\s*=+.*?=+\s*$", "", txt, flags=re.M)                        # 章節標題行
    txt = re.sub(r"^\s*\|.*$", "", txt, flags=re.M)                             # 表格行
    txt = re.sub(r"'''?", "", txt)                                              # 粗斜體標記
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def split_western(body):
    ms = list(re.finditer(CHAP_RE, body, re.M))
    if len(ms) < 2:
        paras, chunks, buf = re.split(r"\n\s*\n", body), [], ""
        for p in paras:
            buf += p.strip() + "\n\n"
            if len(buf) > 8000:
                chunks.append(buf.strip()); buf = ""
        if buf.strip():
            chunks.append(buf.strip())
        return [(f"段{i}", c) for i, c in enumerate(chunks, 1) if len(c) > 60]
    out = []
    pre = re.sub(r"\n{3,}", "\n\n", body[:ms[0].start()]).strip()
    if len(pre) > 500:
        out.append(("前言", pre))
    for i, m in enumerate(ms):
        title = re.sub(r"\s+", " ", m.group(1).strip())[:60]
        content = re.sub(r"\n{3,}", "\n\n", body[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(body)]).strip()
        if len(content) > 60:
            out.append((title, content))
    return out


def split_cjk(body):
    body = re.sub(r"\n{3,}", "\n\n", body)
    paras, chunks, buf = re.split(r"\n\s*\n", body), [], ""
    for p in paras:
        buf += p.strip() + "\n"
        if len(buf) > 3000:
            chunks.append(buf.strip()); buf = ""
    if buf.strip():
        chunks.append(buf.strip())
    out = []
    for c in chunks:                        # 無標點古籍硬切,防超嵌入窗
        while len(c) > 6000:
            out.append(c[:6000]); c = c[6000:]
        if c.strip():
            out.append(c.strip())
    return [(f"段{i}", c) for i, c in enumerate(out, 1) if len(c) > 30]


def main():
    conf = json.load(open(sys.argv[1]))
    added = skip = fail = 0
    with db.connect() as conn:
        for w in conf:
            wid = w["work_id"]
            lang = (w.get("language") or "en").strip() or "en"
            url = w.get("actual_txt_url", "")
            if not url:
                continue
            with db.transaction(conn) as cur:
                cur.execute("SELECT 1 FROM philosophy_work_text WHERE work_id=%s AND language=%s", (wid, lang))
                if cur.fetchone():
                    skip += 1
                    continue
            try:
                raw = download(url)
                if "gutenberg" in url.lower():
                    body = strip_gutenberg(raw)
                elif "wikisource" in url.lower() or "action=raw" in url.lower():
                    body = clean_wikitext(raw)
                else:
                    body = raw.strip()
                rows = split_cjk(body) if lang in ("zh", "ja", "ko") else split_western(body)
            except Exception as e:
                print(f"✗ work {wid}[{lang}]: {e}", flush=True)
                fail += 1
                continue
            total = sum(len(c) for _, c in rows)
            if not rows or total < 800:                      # 防抓到目錄/簡介殘片冒充全文
                print(f"✗ work {wid}[{lang}]: 全文過短(len={total}) — 疑非真全文,不入庫", flush=True)
                fail += 1
                continue
            with db.transaction(conn) as cur:
                for seq, (chap, content) in enumerate(rows, 1):
                    cur.execute("INSERT INTO philosophy_work_text (work_id,chapter,seq,content,source_url,license,language) "
                                "VALUES (%s,%s,%s,%s,%s,'public_domain',%s)", (wid, chap, seq, content, url, lang))
            added += 1
            orig = "原文" if w.get("is_original") else "譯本"
            print(f"✓ work {wid}[{lang}/{orig}]: +{len(rows)} 段 / {total:,} 字 — {w.get('title','')}", flush=True)
            time.sleep(1.2)
    print(f"\n完成:填 {added} 個版本、已有跳過 {skip}、失敗或過短 {fail}")


if __name__ == "__main__":
    main()
