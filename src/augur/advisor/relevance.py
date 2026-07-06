"""T1-a 檢索相關度閘 — 把「命中但不相關」的檢索結果判成實質空檢索(誠實 decline)。

🎯 這支在做什麼(白話):MBB/太陽能/半導體這類 augur 語料庫沒有的專題,e5-small 最近鄰仍
   硬回 top-k 高分(cosine 0.80~0.88 窄帶)離題 chunk(王陽明/論衡…)——系統誤以為「有 context」
   → 不 decline → qwen3 憑弱知識自信講錯。本閘在主路徑餵 LLM 前,以**零 ML 零 usage 的內容詞
   重疊**判定 query↔citation 是否真相關;全數不相關 → 視同實質空檢索 → 走既有 honesty_level([])
   誠實路。**只更嚴不更鬆**:相關度不足 → decline;有相關 → 一律照舊放行(不改 guard、不改閉集)。

   為何不用 cosine 分數門檻:量測證實 e5-small 0.80~0.88 窄帶與相關性幾乎無關(retrieval.py
   is_low_content docstring 已自證),絕對分數門檻不可行。故改用**詞形重疊一致性**——治權 B-1
   否定的是「分數門檻」、未否定「relevance 一致性判定」,此為門檻外新路。

   閾值 0.30 為本機語料實測校準(augur_advisor_selfqa_training_plan §T1-a、DP8):
   MBB 0.13 / 太陽能 0.23 / 半導體 0.15(全 decline)vs 韓非子 0.71 / 荀子 0.86 / 大學 0.86 /
   墨子 0.88 / 孫子 0.89 / 孔子仁 0.57 / 王陽明知行 0.70(全保留);成本不對稱(誤答 out-of-corpus
   =踩三敵①/#1、誤攔=僅不助人,DP8)→ 偏嚴。信號=詞形重疊(candidate DP6-i,零 usage、已實測)。

   **已知邊界(Tier-1 殘留、非新回歸)**:1~2 內容詞之極短 query 若含高頻單字(水/道/心),與哲學
   語料巧合單字重疊即可達 floor 而漏放離題(實測「水費」↔上善若水=0.333);此僅退回改前既有主路徑
   (guard + prompt(c) 兜底、誠實下限未惡化),Tier-2 以語意/詞頻加權(idf)收斂,非本閘阻擋事項。

守 #1(不讓離題檢索偽裝成 context 令 LLM 幻覺)· #15(無相關 → 誠實 decline)· #28(本地零 usage)·
   #18(relevance=領域名詞)· 憲章 v1.36.0 philosophy 邊界(誠實 decline 為 out-of-corpus 正解)。

執行指令矩陣(本檔=library;主路徑經 advise() 呼叫):
  python -c "from augur.advisor.relevance import query_relevant; from types import SimpleNamespace as S; \
    print(query_relevant('多主柵MBB核心技術', [S(text='王陽明全集…', work_title='王陽明全集', thinker='王陽明')]))"
"""
from augur.knowledge import textnorm

# 內容詞重疊地板(本機語料實測校準;調整屬執行層品質工程,守則同 safe_general 詞表——
# guard 機械下限不變、安全繫於 decline 機制而非此值,比照 v1.34.0/憲章 v1.35.0 精神)。
RELEVANCE_FLOOR = 0.30

# CJK 語法虛詞(單字):重疊時剔除,否則離題引文靠「的/是/多/心」等虛字虛高、混淆相關判定
# (實測 MBB↔王陽明未剔虛字=0.22 假陽性、剔後=0.13)。純內容單字(道/仁/知…)保留。
_STOP = set("的是了而之也其以於与與為爲在有無不人上下這那我你他它們就都會要說到得着着過"
            "麼嗎呢吧啊哦且或如何個把被讓從向對比很更最只還又再")


def _content_tokens(text):
    """內容詞集合:textnorm zh 全形集 ∪ en Porter stem;剔單字虛詞、剔未切斷之整串長 token(>12)。
    (zh tokenizer 丟 latin、en tokenizer 丟 CJK,故雙語 union 才完整——實測 MBB 混寫查詢憑此撈全。)"""
    zh = {t for t, _ in textnorm.tokenize(text, "zh")}
    en = {t for t, _ in textnorm.tokenize(text, "en")}
    return {t for t in (zh | en) if len(t) <= 12 and not (len(t) == 1 and t in _STOP)}


def _cite_text(cite):
    """citation 之可比對內容:逐字原文 + 出處著作名 + 思想家/domain(型別感知,Citation/ItemCitation 相容)。"""
    parts = [getattr(cite, "text", "") or "",
             getattr(cite, "work_title", "") or getattr(cite, "item_title", "") or "",
             getattr(cite, "thinker", "") or getattr(cite, "domain", "") or ""]
    return " ".join(parts)


def best_overlap(query, citations):
    """回 query↔citations 最佳內容詞重疊比(0~1):max over citations of |q∩c|/|q|。
    query 無內容詞 → 0.0(無從判定相關 → 保守偏 decline)。純機械、零 ML、零 usage、可離線稽核。"""
    qt = _content_tokens(query)
    if not qt:
        return 0.0
    best = 0.0
    for c in citations:
        inter = qt & _content_tokens(_cite_text(c))
        best = max(best, len(inter) / len(qt))
    return best


def query_relevant(query, citations, floor=RELEVANCE_FLOOR):
    """回 bool:citations 是否有任一與 query 實質相關(最佳重疊 ≥ floor)。
    False = 全數不相關 → 呼叫端應視同實質空檢索、走 honesty_level([]) 誠實 decline 路
    (不進 prompt、不餵 LLM、不觸 guard 放行)。citations 空 → False(交既有空檢索路)。"""
    if not citations:
        return False
    return best_overlap(query, citations) >= floor
