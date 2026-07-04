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

# 主題別名(中/英 → domain ILIKE 樣式);未命中則以 --topic 直接對 domain ILIKE
TOPIC_ALIAS = {
    "財經": ["econom%finance%", "business_management%"], "finance": ["econom%finance%", "business_management%"],
    "投資": ["econom%finance%", "business_management%"], "投資管理": ["business_management%"],
    "經濟": ["econom%"], "管理": ["business_management%", "decision_sciences"],
    "化學": ["chemistry"], "chemistry": ["chemistry"],
    "材料": ["materials_science"], "醫學": ["medicine", "health_professions"],
    "電腦": ["computer_science"], "物理": ["physics%"], "數學": ["mathematics"],
    "生物": ["biochem%", "agricultural%bio%", "immunology%"], "心理": ["psychology"],
}


def _match_domains(cur, topic):
    patterns = TOPIC_ALIAS.get(topic.strip().lower()) or TOPIC_ALIAS.get(topic.strip()) or ["%" + topic.strip() + "%"]
    doms = []
    for pat in patterns:
        cur.execute("SELECT domain, count(*) FROM knowledge_query WHERE domain ILIKE %s GROUP BY domain", (pat,))
        doms += cur.fetchall()
    seen, out = set(), []
    for d, n in doms:
        if d not in seen:
            seen.add(d); out.append((d, n))
    return out


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
            print("  可用主題別名:" + "、".join(sorted(set(TOPIC_ALIAS))))
            return
        with db.transaction(conn) as cur:
            doms = _match_domains(cur, args.topic)
        if not doms:
            sys.exit(f"主題「{args.topic}」無對應 domain(試別名或直接用 domain 名;--topic 無參數列全域)")
        total_q = sum(n for _, n in doms)
        print(f"主題「{args.topic}」→ {len(doms)} 域 / {total_q} query:")
        for d, n in doms:
            print(f"  · {d}: {n} query")
        if not args.run:
            print(f"→ 確認無誤後加 --run 觸發 harvest(首輪建議 --batch 10 最小驗證 #25;放量 --batch 300 --rounds 4)")
            return
        # 觸發既有 harvest 引擎(逐域 subprocess、shell=False 防注入;限速/熔斷/resume 全在引擎)
        py = sys.executable
        for d, n in doms:
            cmd = [py, "scripts/harvest_knowledge.py", "--domain", d,
                   "--batch", str(args.batch), "--rounds", str(args.rounds),
                   "--max-minutes", str(args.max_minutes)]
            print(f"▶ 觸發 harvest --domain {d}(batch {args.batch}/rounds {args.rounds}) …", flush=True)
            subprocess.run(cmd, check=False)   # shell=False;check=False=單域失敗不中斷其餘(誠實續)
        print(f"完成:{len(doms)} 域 harvest 觸發(抓入知識層、素養非預測;provenance/禁AI生成閘在 promote)")


if __name__ == "__main__":
    main()
