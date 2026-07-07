#!/usr/bin/env python
"""主題自動抓取(admin 控制台 P2,計畫 §一.A)— 輸入「財經」等主題 → 展開 registry 域 → 觸發 harvest。

🎯 這支在做什麼(白話):把 admin 輸入之主題詞(中/英)映射到知識 registry 之 domain,展開該域全部
   查詢詞,**確認頁**(印 N 域 / M query / 首輪 --batch 建議)後,以既有 harvest_knowledge 引擎背景抓取。
   **不重造抓取管線**——只做 topic→domain 薄映射 + subprocess 觸發既有引擎(限速/熔斷/resume 全在該引擎)。
   治權:抓入知識層(素養、非預測管線)、真實來源 provenance、禁 AI 生成(既有 promote 閘);#25 首輪最小驗證。
守 #28(觸發既有本地引擎、零 Claude usage)· #17/#25(限速在 harvest 引擎、首輪最小)· #5(subprocess shell=False)· #29。

執行指令矩陣:
  python scripts/acquire_topic.py                          # 無參數:列可用主題別名 + 全 domain
  python scripts/acquire_topic.py --topic 財經             # 確認頁(映射域/query 數/建議),不抓
  python scripts/acquire_topic.py --topic finance --run    # 觸發 harvest(首輪 --batch 10 最小驗證 #25)
  python scripts/acquire_topic.py --topic 財經 --run --batch 300 --rounds 4   # 放量批
"""
import argparse
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db

# 主題別名(中文→domain 樣式)**住 DB 表 `knowledge_topic_alias`**(#29b 資料驅動、admin 增列零改碼);
# 建表/種子見 scripts/migrate_topic_alias_ddl.py。此處只讀、無 hardcode dict。


def _alias_patterns(cur, term):
    """讀 DB 別名表:回對應之 domain ILIKE 樣式(完全相等 **或別名詞為輸入之子字串**——
    如「太陽能」⊂「太陽能產業TOPCon」即命中,使複合中文輸入也能對到別名;不分大小寫、無則空)。"""
    cur.execute("SELECT DISTINCT domain_pattern FROM knowledge_topic_alias WHERE enabled "
                "AND (lower(alias_term)=lower(%s) OR %s ILIKE '%%'||alias_term||'%%')", (term, term))
    return [r[0] for r in cur.fetchall()]


def _match_domains(cur, topic):
    """回 (targets, kw_hits):
    targets = 別名/域名命中之域(整域抓取意圖明確)→ [(domain, 整域 query 數)];
    kw_hits = 僅 query 關鍵詞命中之域(整域範圍可能大 → 列建議、不自動抓)→ [(domain, 含該詞 query 數)]。
    英文/技術詞(solar/perovskite)走 kw_hits 資料驅動、零 hardcode;避免因幾條含詞 query 就抓爆整個廣域。"""
    t = topic.strip()
    targets = {}
    for pat in _alias_patterns(cur, t):                                        # 1. DB 別名表(資料驅動、admin 可增)
        cur.execute("SELECT domain, count(*) FROM knowledge_query WHERE domain ILIKE %s GROUP BY domain", (pat,))
        for d, n in cur.fetchall():
            targets[d] = n
    cur.execute("SELECT domain, count(*) FROM knowledge_query WHERE domain ILIKE %s GROUP BY domain",  # 2. 域名 ILIKE
                ("%" + t + "%",))
    for d, n in cur.fetchall():
        targets[d] = n
    kw = {}
    cur.execute("SELECT domain, count(*) FROM knowledge_query WHERE query ILIKE %s GROUP BY domain",   # 3. 資料驅動關鍵詞
                ("%" + t + "%",))
    for d, n in cur.fetchall():
        if d not in targets:
            kw[d] = n
    return (sorted(targets.items(), key=lambda x: -x[1]),
            sorted(kw.items(), key=lambda x: -x[1]))


def _all_domains(cur):
    cur.execute("SELECT domain, count(*) FROM knowledge_query GROUP BY domain ORDER BY domain")
    return cur.fetchall()


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--topic")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--max-minutes", type=int, default=120)
    args, _ = ap.parse_known_args()

    with db.connect() as conn:
        if not args.topic:
            print(__doc__.split("執行指令矩陣:")[1])
            with db.transaction(conn) as cur:
                cur.execute("SELECT DISTINCT alias_term FROM knowledge_topic_alias WHERE enabled ORDER BY alias_term")
                aliases = [r[0] for r in cur.fetchall()]
            print("  DB 別名(knowledge_topic_alias、admin INSERT 增列零改碼):" + "、".join(aliases))
            print("  或直接輸入 domain 名 / 英文關鍵詞(如 solar、perovskite)。")
            return
        with db.transaction(conn) as cur:
            targets, kw = _match_domains(cur, args.topic)
            if not targets and not kw:
                print(f"主題「{args.topic}」無對應 domain / query 關鍵詞。"
                      f"可直接輸入下列 domain 名之一(或英文關鍵詞如 solar、perovskite):", file=sys.stderr)
                for d, n in _all_domains(cur):
                    print(f"  · {d}: {n} query", file=sys.stderr)
                sys.exit(1)
        if targets:
            total_q = sum(n for _, n in targets)
            print(f"主題「{args.topic}」→ 抓取 {len(targets)} 域 / {total_q} query:")
            for d, n in targets:
                print(f"  · {d}: {n} query")
        if kw:
            print(f"另有 {len(kw)} 域含「{args.topic}」關鍵詞之 query(整域範圍大、預設不抓;"
                  f"要抓某域請直接以其 domain 名 --topic):")
            for d, n in kw:
                print(f"  · {d}: {n} 條含此詞（整域更多）")
        if not targets:
            print(f"→ 無明確可抓之域(僅關鍵詞命中廣域);請從上方挑一個 domain 名直接 --topic 它。", file=sys.stderr)
            sys.exit(1)
        if not args.run:
            print(f"→ 確認無誤後加 --run 觸發 harvest(首輪建議 --batch 10 最小驗證 #25;放量 --batch 300 --rounds 4)")
            return
        # 觸發既有 harvest 引擎(逐域 subprocess、shell=False 防注入;限速/熔斷/resume 全在引擎)
        py = sys.executable
        for d, n in targets:
            cmd = [py, "scripts/harvest_knowledge.py", "--domain", d,
                   "--batch", str(args.batch), "--rounds", str(args.rounds),
                   "--max-minutes", str(args.max_minutes)]
            print(f"▶ 觸發 harvest --domain {d}(batch {args.batch}/rounds {args.rounds}) …", flush=True)
            subprocess.run(cmd, check=False)   # shell=False;check=False=單域失敗不中斷其餘(誠實續)
        print(f"完成:{len(targets)} 域 harvest 觸發(抓入知識層、素養非預測;provenance/禁AI生成閘在 promote)")


if __name__ == "__main__":
    main()
