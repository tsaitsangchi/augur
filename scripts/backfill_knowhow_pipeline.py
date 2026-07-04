#!/usr/bin/env python
"""〔已退役 R1〕十領域 know-how 全鏈補齊 — 職能已收編至 refresh_knowledge_pipeline.py(唯一驅動器)。

🎯 本檔=指引 stub(e2e 計畫 §4 R1/拍板 P11;順序硬約束⑧:退役同批於驅動器上線):
   原全鏈驅動職能(subprocess check=False=假驗收反例)終結,收編對應——
   A/B) registry 驅動 acquire→staging→promote 迭代 → scripts/harvest_knowledge.py
        (排程矩陣+harvest_log resume+輪末 promote);經驅動器=--stage harvest / --stage promote
   D) 公版全文(Gutenberg thinker works,works 側) → scripts/fetch_all_thinker_works.py 個別執行
      (items 側 OA 全文=fetch_oa_fulltext.py,驅動器 --stage fulltext)
   全鏈一鍵 → python scripts/refresh_knowledge_pipeline.py --domain <X>(全節點 check=True)
   終態統計 → python scripts/refresh_knowledge_pipeline.py(無參數=待辦計數矩陣,唯讀)
守 #12(單一驅動器,雙驅動器違規故退役)· e2e 計畫 SSOT=reports/augur_knowhow_e2e_pipeline_plan_20260704.md §7。

執行指令矩陣:
  python scripts/backfill_knowhow_pipeline.py    # 只印本退役指引後 exit 2(不執行任何管線)
"""
import sys


def main():
    print(__doc__)
    print("本 script 已退役(R1/P11):請改用 python scripts/refresh_knowledge_pipeline.py;"
          "exit 2=錯得大聲,防舊呼叫鏈靜默假成功。")
    sys.exit(2)


if __name__ == "__main__":
    main()
