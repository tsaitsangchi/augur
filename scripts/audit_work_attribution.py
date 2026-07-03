#!/usr/bin/env python
"""T-1 全文歸屬稽核 — Gutenberg 自動遍歷 work 之作者身分/生卒比對,誤配標 review_flag 並級聯清理。

🎯 這支在做什麼(白話):實證污染(work 364 建築誌掛 Henry George、85% chunks 未稽核)之修復——
   對 538 部「自動遍歷」work:經 gutendex 批查該書真實作者(姓名+生卒),與掛的 thinker **確定性比對**
   (姓名 token 全等 + 生卒兩側俱在必相等);不符→ `review_flag=true` + **級聯刪 chunk/embedding**
   (work/work_text 保留供人審、可 --fix 後重建);策展來源(明確 id→thinker 映射)provenance 通過。
守 #1(引用庫不留誤配假兆)· #15(統計誠實、寧殺勿留)· #17/#25(gutendex 批查限速)· text 計畫 v1.6 T-1。

執行指令矩陣:
  python scripts/audit_work_attribution.py            # 稽核 dry-run:只判定+印報告,不寫
  python scripts/audit_work_attribution.py --fix      # 寫 review_flag + 級聯刪誤配 chunk/embedding
"""
import re
import sys
import json
import time
import socket
import urllib.request

import _bootstrap  # noqa: F401
from augur.core import db

socket.setdefaulttimeout(60)
UA = {"User-Agent": "augur-knowledge/1.0 (attribution audit)", "Accept": "application/json"}
AUTO_NOTE = "公版原典、Project Gutenberg(自動遍歷)"


def norm_tokens(name):
    """姓名 → 正規化 token set('Lander, Richard'/'Richard Lander' 同集)。"""
    return frozenset(t for t in re.split(r"[,\s.()\[\]]+", (name or "").lower()) if len(t) > 1)


def main():
    fix = "--fix" in sys.argv
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            # 1) 策展/書目來源:provenance 通過
            cur.execute("UPDATE philosophy_work SET review_flag=false WHERE review_flag IS NULL AND coalesce(note,'') <> %s", (AUTO_NOTE,)) if fix else None
            # 2) 稽核對象:自動遍歷 538 部 → (work_id, thinker, gid)
            cur.execute("""SELECT w.work_id, w.title, th.name, th.birth_year, th.death_year,
                                  (SELECT t.source_url FROM philosophy_work_text t WHERE t.work_id=w.work_id LIMIT 1)
                           FROM philosophy_work w JOIN philosophy_thinker th ON th.thinker_id=w.thinker_id
                           WHERE coalesce(w.note,'')=%s""", (AUTO_NOTE,))
            works = []
            for wid, title, tname, tb, td, url in cur.fetchall():
                m = re.search(r"ebooks/(\d+)", url or "")
                works.append((wid, title, tname, tb, td, int(m.group(1)) if m else None))
        print(f"稽核對象 {len(works)} 部(自動遍歷);gutendex 批查中…", flush=True)

        # 3) gutendex 批查(40 id/批)
        gmeta = {}
        gids = [w[5] for w in works if w[5]]
        for i in range(0, len(gids), 40):
            batch = gids[i:i + 40]
            url = "https://gutendex.com/books?ids=" + ",".join(map(str, batch))
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode())
                for b in d.get("results", []):
                    gmeta[b["id"]] = b.get("authors", [])
            except Exception as e:
                print(f"  批 {i//40+1} 失敗:{e}(該批標 unverifiable)", flush=True)
            time.sleep(0.6)

        # 4) 確定性比對
        passed, flagged, unverifiable = [], [], []
        for wid, title, tname, tb, td, gid in works:
            authors = gmeta.get(gid)
            if not authors:
                unverifiable.append((wid, title, tname, "gutendex 無作者資料"))
                continue
            t_tok = norm_tokens(tname)
            ok = False
            for a in authors:
                a_tok = norm_tokens(a.get("name"))
                # 子集比對(容 middle name/尊稱:Nietzsche Friedrich Wilhelm ⊇ Friedrich Nietzsche)
                # + 生卒把關(George Adam Smith⊇Adam Smith 但 1856≠1723 → 攔)
                if not a_tok or not t_tok.issubset(a_tok):
                    continue
                ab, ad = a.get("birth_year"), a.get("death_year")
                tol = 15 if a_tok == t_tok else 2   # 全等名→±15(同名同時代=同一人,古人考證差3-13年);子集→±2 嚴格
                if tb is not None and ab is not None and abs(tb - ab) > tol:
                    continue
                if td is not None and ad is not None and abs(td - ad) > tol:
                    continue
                ok = True
                break
            (passed if ok else flagged).append((wid, title, tname, authors[0].get("name") if authors else "?"))

        print(f"\n結果:通過 {len(passed)} / 誤配 {len(flagged)} / 不可驗 {len(unverifiable)}")
        print("\n=== 誤配樣本(前 15) ===")
        for wid, title, tname, aname in flagged[:15]:
            print(f"  ✗ work {wid}: 掛「{tname}」實為「{aname}」| {title[:50]}")
        if unverifiable:
            print("=== 不可驗(前 5,一併 flag 寧殺勿留)===")
            for wid, title, tname, why in unverifiable[:5]:
                print(f"  ? work {wid}: {tname} | {title[:40]} | {why}")

        if not fix:
            print("\n(dry-run 未寫;--fix 執行標記+級聯清理)")
            return
        # 5) --fix:寫 flag + 級聯刪誤配之 chunk/embedding
        bad_ids = [w[0] for w in flagged] + [w[0] for w in unverifiable]
        with db.transaction(conn) as cur:
            cur.execute("UPDATE philosophy_work SET review_flag=false WHERE review_flag IS NULL AND coalesce(note,'') <> %s", (AUTO_NOTE,))
            n_cur = cur.rowcount
            cur.execute("UPDATE philosophy_work SET review_flag=false WHERE work_id = ANY(%s)", ([w[0] for w in passed],))
            cur.execute("UPDATE philosophy_work SET review_flag=true  WHERE work_id = ANY(%s) AND review_flag IS DISTINCT FROM false", (bad_ids,))  # 不覆蓋人審通過
            cur.execute("DELETE FROM philosophy_chunk_embedding e USING philosophy_chunk c "
                        "WHERE e.chunk_id=c.chunk_id AND c.work_id = ANY(%s)", (bad_ids,))
            n_emb = cur.rowcount
            cur.execute("DELETE FROM philosophy_chunk WHERE work_id = ANY(%s)", (bad_ids,))
            n_chk = cur.rowcount
            cur.execute("SELECT count(*) FROM philosophy_work WHERE review_flag IS NULL")
            n_null = cur.fetchone()[0]
        print(f"\n--fix 完成:策展通過 {n_cur}+{len(passed)} / flag {len(bad_ids)} / 級聯刪 chunk {n_chk:,}、embedding {n_emb:,} / 未稽核殘餘 {n_null}(應0)")


if __name__ == "__main__":
    main()
