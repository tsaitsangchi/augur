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

   **Tier-2 硬化(2026-07-07,配 translate-for-retrieval 上線)**:query_relevant/relevant_citations 改判準
   為「須共享**夠強**辨識性專詞」——泛用字(system/analysis/research/energy/efficiency/what/…,見
   _EN_GENERIC)與**單一 CJK 字**(能/太/心/道/仁,跨語料巧合共現極高)一律不算命中相關;只有多字
   詞(perovskite/photovoltaic/孔子/知行合一)才具主題辨識力。**擋前版死因**:CJK 譯英檢索後只含泛用字
   之問句(系統分析/能源效率的研究)撞逐字含這些字之離題文獻(黑格爾論神經系統/斯賓格勒 footnote)、
   MBB 單字撞王陽明 → 假放行;硬化後皆 decline。選詞表非 IDF:本機 concordance df 部分索引、log 壓縮後
   泛用詞 vs 專詞僅 5× 差、IDF 4.8~8.8 窄帶分不開(實測),詞表更穩、可離線稽核、確定性(見 _EN_GENERIC 註)。
   **代價(誠實揭露)**:純單字哲學問句(「仁」「道」單獨)退為 decline(誠實優先方向;實務多由
   lexicon_lookup/safe_general 白名單另路服務)。best_overlap 保留為既有工具/測試界面、非現行閘判準。

守 #1(不讓離題檢索偽裝成 context 令 LLM 幻覺)· #15(無相關 → 誠實 decline)· #28(本地零 usage)·
   #18(relevance=領域名詞)· 憲章 v1.36.0 philosophy 邊界(誠實 decline 為 out-of-corpus 正解)。

執行指令矩陣(本檔=library;主路徑經 advise() 呼叫):
  python -c "from augur.advisor.relevance import query_relevant; from types import SimpleNamespace as S; \
    print(query_relevant('多主柵MBB核心技術', [S(text='王陽明全集…', work_title='王陽明全集', thinker='王陽明')]))"
"""
import re

from augur.knowledge import textnorm

# 內容詞重疊地板(本機語料實測校準;調整屬執行層品質工程,守則同 safe_general 詞表——
# guard 機械下限不變、安全繫於 decline 機制而非此值,比照 v1.34.0/憲章 v1.35.0 精神)。
RELEVANCE_FLOOR = 0.30

# CJK 語法虛詞(單字):重疊時剔除,否則離題引文靠「的/是/多/心」等虛字虛高、混淆相關判定
# (實測 MBB↔王陽明未剔虛字=0.22 假陽性、剔後=0.13)。純內容單字(道/仁/知…)保留。
_STOP = set("的是了而之也其以於与與為爲在有無不人上下這那我你他它們就都會要說到得着着過"
            "麼嗎呢吧啊哦且或如何個把被讓從向對比很更最只還又再")


# ── 通用泛域字停詞(en Porter stem;Tier-2 硬化,2026-07-07,配 translate-for-retrieval 上線)──
# 何以需要(前版死因):CJK query 譯英文檢索後,「有沒有關於系統分析的研究/能源效率的研究」等只含
#   泛用字之問句,會撞任何逐字含 system/analysis/research/energy/efficiency 之離題文獻(黑格爾論神經
#   「系統」、斯賓格勒 footnote、太陽能材料摘要)→ 泛用字重疊虛高、假放行 → 系統誤當有料令 LLM 憑弱
#   知識 confabulate(踩 #1/#15)。故:泛用字**不算作「命中相關」之判據**——相關性須繫於**稀有專詞**
#   (perovskite/photovoltaic/silicon/仁/知行…)之共現,泛用字僅泛在學術骨架、不帶主題辨識力。
# 為何選詞表(方案 b)而非 IDF(方案 a):本機 concordance df 為部分索引、log 壓縮後 research(df1258)
#   vs perovskite(df251)僅 5× 差、IDF 4.8~8.8 窄帶分不開(實測),閾值不可靠;詞表是可列舉、可離線
#   稽核、確定性、直擊已知失效模式之機械閘,且**屬邏輯側品質工程**(比照 safe_general 白名單、憲章
#   v1.35.0「詞表不鎖=執行層、安全繫於機械閘非詞表」)——寫 code 裡合規、非 #29b 資料鎖。
# 邊界:只收「泛在學術骨架 + 英文虛詞 + 疑問/意圖詞」;domain 專名(perovskite/solar/silicon)一律不收。
_EN_GENERIC = set("""
system analysi analyz research studi method process design approach result review paper articl
chapter section develop applic use base gener overview introduct report perform problem solut
effect factor field level type form framework structur function theori scienc main core master
multi whether energi effici technologi innov optim advantag technic benefit product manag manufactur qualiti industri
techniqu materi properti characterist paramet condit measur estim comput simul evalu impact
influenc relationship compar improv enhanc model data valu case work part number general
there ani ar on of the a an in to for and or with by is at about into over under between within
what how whi where when who which do doe did can could would should mean definit concept
topic subject question relat relev exist avail""".split())


def _content_tokens(text):
    """內容詞集合:textnorm zh 全形集 ∪ en Porter stem;剔單字虛詞、剔未切斷之整串長 token(>12)。
    (zh tokenizer 丟 latin、en tokenizer 丟 CJK,故雙語 union 才完整——實測 MBB 混寫查詢憑此撈全。)"""
    zh = {t for t, _ in textnorm.tokenize(text, "zh")}
    en = {t for t, _ in textnorm.tokenize(text, "en")}
    return {t for t in (zh | en) if len(t) <= 12 and not (len(t) == 1 and t in _STOP)}


def _is_strong(tok):
    """辨識性專詞是否「夠強」可作相關判據:
      · latin/en 詞:長度 ≥2(單字母已在 _EN_GENERIC,此僅擋殘餘噪);
      · CJK:多字詞(2~8,jieba 切出之詞如 效率/知行合一/孔子)——**單一 CJK 字不算**。
    為何排單 CJK 字:單字(能/太/心/道/仁)跨語料巧合共現極高(能=can、太=too),技術/亂問 query 之
    單字會巧撞哲學原文(能↔傳習錄、心↔王陽明)→ 假放行/污染(實測 MBB 單字 核/心 撞王陽明);多字詞
    才具主題辨識力。代價=純單字哲學問句(「仁」「道」單獨)退為 decline(誠實優先方向,前版即標此為
    洩漏弱點;實務多由 lexicon_lookup/safe_general 白名單另路服務,非本閘職責)。剔 >8 之未切斷長串。"""
    if tok.isascii():
        return len(tok) >= 2
    return 2 <= len(tok) <= 8


def _strong_distinctive(text):
    """夠強之辨識性專詞集:內容詞剔 _EN_GENERIC 泛用字、再過 _is_strong(排單 CJK 字)——相關判定唯一信號。"""
    return {t for t in (_content_tokens(text) - _EN_GENERIC) if _is_strong(t)}


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


def relevant_citations(query, citations, min_terms=1):
    """回 citations 之子集:只留與 query 共享 ≥min_terms 個**夠強**辨識性專詞者(泛用字/單 CJK 字不算)。保序。
    query 無夠強辨識詞(全泛用字如「能源效率的研究」、或全單 CJK 字)→ 回 [](無從確認 → 全剔 → decline)。
    **逐條相關度過濾**(#1 命門):雙語檢索撈回之離題引文(王陽明/黑格爾/ERP 權限檔混在 solar 正解裡、
    或譯句泛詞巧撞)不進 LLM context——不餵 LLM 離題垃圾。呼叫端對原 query / 英文譯 query 各跑(見 advise)。
    **min_terms**:原文檢索用 1(既有);英文 fallback 用 2——qwen3 誤譯之 query(如 多主柵→multi-master bus)
    常靠單一泛詞(advantage)巧撞離題引文→過閘→LLM 瞎掰;要求 ≥2 辨識詞共享,誤譯 fallback 收斂為誠實
    decline、正確譯(perovskite/solar/cell 多詞共享)仍過(#15 餵離題不如誠實 decline)。"""
    qd = _strong_distinctive(query)
    if not qd:
        return []
    return [c for c in citations if len(qd & _strong_distinctive(_cite_text(c))) >= min_terms]


def query_relevant(query, citations, floor=RELEVANCE_FLOOR):
    """回 bool:citations 是否有任一與 query 實質相關(= relevant_citations 非空)。**只更嚴不更鬆**:
    相關性須繫於**夠強辨識性專詞**共現(perovskite/solar/孔子/知行合一…),泛用字(system/energy/
    research/what/…)與單 CJK 字(能/太/心)之巧合共現一律不算(擋前版「系統分析/能源效率/MBB」死因)。
    False = 全數不相關 → 呼叫端視同實質空檢索、走 honesty_level([]) 誠實 decline 路(不餵 LLM、不觸 guard 放行)。
    citations 空 → False。誠實優先:本閘只把「泛用字/單字巧合命中之離題引文」判成不相關,不放行原本被攔者。
    (floor 參數保留為簽章相容;判準已改為辨識性專詞共現、不再倚 best_overlap 分數門檻。)"""
    if not citations:
        return False
    return bool(relevant_citations(query, citations))


# ── D4 選股意圖判定(計畫 §5.2-2)——決定 payload_fn 分派,非新編排器 ──
# 純正則、零 ML、零 usage(同 safe_general/query_relevant 之判定風格);唯一編排出口仍 advise()。
# 判準:命中「要 augur 給選股/排序/推薦持股/該買什麼」之意圖 → True(注入真實 as-of 預測 payload);
# 一般/知識/定義題 → False(維持 empty_payload 去雜訊,精準度 §2.4 D-1)。
# 誤分類 fail-safe:誤判為選股題最壞=注入真 payload 但題不對(guard 白名單仍機械強制、picks 誠實附
# caveat、不會捏數字);誤判為非選股=退回 empty_payload(維持現況),兩向皆不觸三敵、偏保守不放鬆 guard。
_PICK_INTENT = re.compile(
    r"該買(什麼|哪|誰)|買(什麼|哪些|哪支|哪檔)|要買(什麼|哪)|推薦(什麼|哪些)?(股|標的|持股|個股|買)|"
    r"選股|哪些股票|哪支股票|哪檔股票|買進(什麼|哪)|進場(標的|個股)|投資組合|持股(建議|清單|名單)|"
    r"排序(標的|個股|持股|股票)|(top|前)\s*\d*\s*(標的|名單|個股|持股)|top\s*(標的|picks|股)|"
    r"值得(買|投資|進場)的?(股|標的)|該投資(什麼|哪)|建議(買|持有|投資)(什麼|哪)|"
    r"看好(哪些|什麼|誰)|哪些台股|推薦[^。?!]{0,8}(股票|個股|標的)|"
    r"前\s*[\d一二三四五六七八九十]+\s*(支|檔|名)\s*(個股|股票|標的)?|"   # 2026-07-11 前台實測補:前三支個股
    r"(報酬|準確|勝率|機率)[^。?!]{0,8}最高[^。?!]{0,8}(個股|股票|標的)|"   # 2026-07-10 P5 金題實測補:看好哪些台股/推薦幾檔…股票
    r"what.{0,10}(stocks?|to buy)|which stocks?|recommend.{0,10}stocks?|top pick", re.IGNORECASE)


def picking_intent(query):
    """回 bool:query 是否為「要 augur 給選股結果/排序/推薦持股」之意圖(→ 注入真實預測 payload)。
    非選股(一般/知識/定義/單股財務數值查詢)→ False(走 empty_payload)。純機械、零 usage、可離線稽核。"""
    return bool(_PICK_INTENT.search(query or ""))
