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

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.relevance              # 印用途+公開入口（唯讀）
  python -m augur.advisor.relevance --selftest   # 純紅綠自測（零 IO）
"""
import re

from augur.knowledge.token_overlap import (
    _EN_GENERIC,
    _cite_text,
    _cjk_ngrams,
    _content_tokens,
    _is_strong,
    _strong_distinctive,
)

# 內容詞重疊地板(本機語料實測校準;調整屬執行層品質工程,守則同 safe_general 詞表——
# guard 機械下限不變、安全繫於 decline 機制而非此值,比照 v1.34.0/憲章 v1.35.0 精神)。
RELEVANCE_FLOOR = 0.30

# token／泛用字／CJK 窗 SSOT＝knowledge.token_overlap（STRUCT 斷 knowledge→advisor）



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


def kh0_floor_citations(query, citations):
    """KH0 底線：ItemCitation 原文在庫，且與問句有 CJK n-gram 或拉丁專詞（如 ERP）共現 → 保留。
    僅在 relevant_citations／譯英 fallback 已空時由 advise 呼叫。不放行純 works 離題哲學假命中。
    語意＝「本地 AI 對內文的最基本理解」材料下限，≠通識無引文瞎答。"""
    if not citations:
        return []
    q = query or ""
    q_ng = _cjk_ngrams(q)
    q_lat = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,31}", q)}
    q_lat = {t for t in q_lat if t not in _EN_GENERIC and len(t) >= 2}
    out = []
    for c in citations:
        if getattr(c, "item_id", None) is None:
            continue
        ct = _cite_text(c)
        if q_ng and (q_ng & _cjk_ngrams(ct)):
            out.append(c)
            continue
        if q_lat:
            c_lat = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,31}", ct)}
            if q_lat & c_lat:
                out.append(c)
    return out


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


# ── 單股相對機率意圖(ADVISOR-PRED-KH Phase 1；乙案 B2 優於 C)──
# 「2330 未來約 30 天走勢」類 → (stock_id, horizon_td)；目標價/逐日點位仍交 C 短路。
# 台股 4 碼含 ETF 0xxx；剔除年號 1900–2100 以防「2026年」誤當股號。
_STOCK_ID_RE = re.compile(r"(?<!\d)(\d{4})(?!\d)")
_TICKER_ABS_EXCLUDE = re.compile(r"目標價|逐日|每日路徑|漲多少|跌多少")
_TICKER_REL_SIGNAL = re.compile(
    r"相對|同儕|強弱|排名|機率|走勢|展望|預測|看漲|看跌|漲跌|"
    r"未來.{0,5}(天|日)|"
    r"\d{1,3}\s*個?(天|日|交易日)|約\s*\d{1,3}\s*天"
)


def _plausible_tw_ticker(sid):
    """四碼可當台股／ETF；1900–2100 視為年號碰撞（非股號）。"""
    try:
        n = int(sid)
    except (TypeError, ValueError):
        return False
    if 1900 <= n <= 2100:
        return False
    return True


def extract_tw_tickers(query):
    """問句內合理台股／ETF 四碼（去重、保序）。"""
    out, seen = [], set()
    for m in _STOCK_ID_RE.finditer(query or ""):
        sid = m.group(1)
        if not _plausible_tw_ticker(sid) or sid in seen:
            continue
        seen.add(sid)
        out.append(sid)
    return out


def single_ticker_rel_intent(query):
    """回 (stock_id, horizon) 或 None。

    horizon 映射：≈7–14／10 日／約月→20 交易日；未寫清但有走勢/相對訊號→60(部署主尺)。
    含目標價/逐日點位且無「相對／同儕」→ None（留給方向短路）。
    """
    q = query or ""
    if _TICKER_ABS_EXCLUDE.search(q) and not re.search(r"相對|同儕|強弱|排名", q):
        return None
    tickers = extract_tw_tickers(q)
    if not tickers:
        return None
    if not _TICKER_REL_SIGNAL.search(q):
        return None
    sid = tickers[0]
    return (sid, _horizon_from_query(q, default=60))


_CN_NUM = {"一": 1, "二": 2, "兩": 2, "两": 2, "三": 3, "四": 4, "五": 5,
           "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _horizon_from_query(q, default=60):
    if re.search(r"120\s*(天|日|交易日)|H\s*120|半年", q, re.I):
        return 120
    if re.search(r"40\s*(天|日|交易日)|H\s*40", q, re.I):
        return 40
    if re.search(r"60\s*(天|日|交易日)|H\s*60|兩個?月", q, re.I):
        return 60
    # 短窗口語（10 天／兩週／今天之後 N 天≤14）→ 最近部署短尺 H20（非十交易日精確產物）
    if re.search(
        r"(?:今天之後|未來)?.{0,4}(1[0-4]|[7-9])\s*(天|日|交易日)|"
        r"兩\s*週|两\s*周|约?\s*10\s*天|約\s*10|"
        r"30\s*(天|日|交易日)|約\s*30|未來.{0,4}30|一個?月|"
        r"20\s*(天|日|交易日)|H\s*20",
        q, re.I,
    ):
        return 20
    return default


def _rel_prob_topk_k(query):
    """自問句抽 TopK；無則 None。"""
    q = query or ""
    m = re.search(r"top\s*(\d+)", q, re.I)
    if m:
        k = int(m.group(1))
    else:
        m2 = re.search(r"前\s*([一二三四五六七八九十兩两\d]+)\s*(名|支|檔|個)?", q)
        if not m2:
            m3 = re.search(r"(最高|前茅).{0,6}(?:的)?\s*top\s*(\d+)", q, re.I)
            if m3:
                k = int(m3.group(2))
            else:
                return None
        else:
            tok = m2.group(1)
            k = int(tok) if tok.isdigit() else _CN_NUM.get(tok, 0)
    if k < 1 or k > 20:
        return None
    return k


def _mentions_h20(q: str) -> bool:
    return bool(re.search(r"20\s*(天|日|交易日)|H\s*20", q, re.I))


def _mentions_h60(q: str) -> bool:
    return bool(re.search(r"60\s*(天|日|交易日)|H\s*60|兩個?月", q, re.I))


def rel_prob_board_intent(query):
    """雙窗／漲+跌 TopN 看板意圖 → dict 或 None。

    對症：問「20天與60天漲幅 top10與跌幅 top10＋都存在」時，舊路徑只取單一 H60、
    且弱 LLM 複誦造成重複列；改走確定性雙窗看板（免 LLM）。
    回 {"k", "horizons": tuple[int,...], "include_bottom": bool, "include_intersect": bool}
    """
    q = query or ""
    if re.search(r"目標價|逐日路徑|每日路徑", q):
        return None
    if not re.search(
        r"機率|相對|強弱|排名|漲跌幅|漲幅|跌幅|報酬率?|漲最多|跌最多|賺最多",
        q,
    ):
        return None
    k = _rel_prob_topk_k(q)
    if k is None:
        return None
    if not (
        re.search(r"未來|\d+\s*(天|日)|最高|top|前\s*|今天之後|之後|近日|短期", q, re.I)
    ):
        return None
    want_up = bool(re.search(r"漲跌幅|漲幅|漲最多|上漲|起漲|看好|相對強", q))
    want_down = bool(re.search(r"漲跌幅|跌幅|跌最多|相對弱|看空|看淡", q))
    dual = _mentions_h20(q) and _mentions_h60(q)
    want_intersect = bool(re.search(r"都存在|兩窗|同時|交集|皆入選|都在", q)) or dual
    # 雙窗、或同句要漲+跌榜 → 看板（確定性）
    if not (dual or (want_up and want_down) or want_intersect):
        return None
    if dual:
        horizons = (20, 60)
    else:
        if re.search(r"漲跌幅|漲幅|跌幅|今天之後|之後|近日|短期", q):
            default_h = 20
        else:
            default_h = 20 if re.search(r"30|未來", q) else 60
        horizons = (_horizon_from_query(q, default=default_h),)
    include_bottom = bool(want_down)
    if re.search(r"漲跌幅", q):
        include_bottom = True
    return {
        "k": k,
        "horizons": horizons,
        "include_bottom": include_bottom,
        "include_intersect": bool(want_intersect and len(horizons) >= 2),
    }


def rel_prob_topk_intent(query):
    """回 (k, horizon) 或 None——「未來N天(上漲)機率最高 topK」→ 改答相對機率 TopK。

    Steward auto_rel_topn／憲政切片：口語「上漲機率／漲跌幅 TopN」一律改寫為
    P(勝過同儕中位) 排名，**不是**絕對漲跌幅；仍注入 picks 以免方向短路空拒。
    若命中雙窗看板（rel_prob_board_intent）→ 回 None，改由看板路徑承接。
    """
    q = query or ""
    if rel_prob_board_intent(q) is not None:
        return None
    if re.search(r"目標價|逐日路徑|每日路徑", q):
        return None
    # 相對語 ∪ 口語絕對幅度排名（改寫觸發；禁目標價／逐日）
    if not re.search(
        r"機率|相對|強弱|排名|漲跌幅|漲幅|跌幅|報酬率?|漲最多|跌最多|賺最多",
        q,
    ):
        return None
    k = _rel_prob_topk_k(q)
    if k is None:
        return None
    if not (
        re.search(r"未來|\d+\s*(天|日)|最高|top|前\s*|今天之後|之後|近日|短期", q, re.I)
    ):
        return None
    # 漲跌幅／今天之後類 → 顧問主尺 H20；其餘走 _horizon_from_query
    if re.search(r"漲跌幅|漲幅|跌幅|今天之後|之後|近日|短期", q):
        default_h = 20
    else:
        default_h = 20 if re.search(r"30|未來", q) else 60
    h = _horizon_from_query(q, default=default_h)
    return (k, h)


def market_binary_dir_intent(query):
    """無股號＋「上漲還是下跌／漲或跌」→ 大盤絕對方向題(預測知識通道 enrich;仍不給可交易機率)。"""
    q = query or ""
    if extract_tw_tickers(q):
        return False
    if re.search(r"目標價|逐日路徑", q):
        return False
    return bool(
        re.search(
            r"上漲還是下跌|漲還是跌|漲或跌|下跌還是上漲|"
            r"會漲還是會跌|漲的機率高還是跌|上漲.*下跌.*機率|下跌.*上漲.*機率",
            q,
        )
    )


def _selftest():
    """自測(零 DB/零 API、純函式紅綠 #29a):固化本閘核心不變式——單 CJK 字不算辨識詞(Tier-2
    死因回歸鎖)、專詞共現才判相關、空檢索必 decline、選股意圖判定;僅用本地 textnorm、零 IO。"""
    from types import SimpleNamespace as S
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("RELEVANCE_FLOOR 常數=0.30", RELEVANCE_FLOOR == 0.30)
    # _is_strong:單 CJK 字不強(能/太巧撞哲學原文之死因)、多字詞強;單 ascii 母不強、多字 ascii 強
    chk("_is_strong 單 CJK 字不算(能/太)", not _is_strong("能") and not _is_strong("太"))
    chk("_is_strong 多字詞算(知行合一/perovskite)", _is_strong("知行合一") and _is_strong("perovskite"))
    chk("_is_strong 單 ascii 母不算、雙字算", not _is_strong("a") and _is_strong("mbb"))
    # 空檢索 → 必 decline(#15;短路、零 textnorm)
    chk("query_relevant 空 citations→False", query_relevant("多主柵MBB", []) is False)
    # 專詞共現 → 相關放行(perovskite 非泛用字、雙側共享)
    cite_on = [S(text="perovskite photovoltaic material 鈣鈦礦光伏")]
    chk("query_relevant 專詞共現→True", query_relevant("perovskite solar cell", cite_on) is True)
    # 離題引文(哲學原文)無專詞共現 → decline(擋 LLM 幻覺 #1)
    cite_off = [S(text="論衡 王充 疾虛妄", work_title="論衡", thinker="王充")]
    chk("query_relevant 離題哲學引文→False", query_relevant("perovskite solar cell", cite_off) is False)
    chk("relevant_citations 只留相關子集", relevant_citations("perovskite solar", cite_on + cite_off) == cite_on)
    # 連寫 CJK＋拉丁混寫：不得因單字切詞令 qd=[] 假 decline（ERP 災難還原）
    cite_erp = [S(text="國碩科技每年一次 DR演練，透過備份還原，確保ERP-GP系統",
                  item_title="國碩-ERP-GP_DR說明", domain="local")]
    chk("連寫 CJK 問句有強詞(災難/還原/演練)",
        bool(_strong_distinctive("ERP災難還原演練") & {"災難", "還原", "演練"}))
    chk("ERP災難還原演練↔ERP 引文→True",
        query_relevant("ERP災難還原演練", cite_erp) is True)
    chk("ERP災難還原演練↔王陽明→False",
        query_relevant("ERP災難還原演練",
                       [S(text="王陽明全集知行合一", work_title="王陽明全集", thinker="王陽明")])
        is False)
    # KH0 底線：item 原文共現可保留；works／無共現不放行
    raw_mix = [
        S(item_id=1, text="國碩 DR演練 備份還原 ERP-GP", item_title="國碩-ERP", domain="local"),
        S(text="論衡 王充", work_title="論衡", thinker="王充"),  # no item_id
    ]
    kh0 = kh0_floor_citations("ERP災難還原演練", raw_mix)
    chk("KH0 保留 ERP item", len(kh0) == 1 and kh0[0].item_id == 1)
    chk("KH0 不收 works", all(getattr(c, "item_id", None) is not None for c in kh0))
    chk("KH0 MBB↔王陽明 item 仍空",
        kh0_floor_citations("多主柵MBB核心技術",
                            [S(item_id=9, text="王陽明知行合一", item_title="傳習錄", domain="phil")])
        == [])
    # picking_intent:選股意圖 True、知識/定義題 False(純正則)
    chk("picking_intent 選股題→True", picking_intent("該買什麼股票") and picking_intent("which stocks to buy"))
    chk("picking_intent 知識題→False", not picking_intent("什麼是知行合一"))
    # single_ticker_rel_intent(B2)
    chk("單股30天走勢→(2330,20)", single_ticker_rel_intent("2330個股未來30天走勢?") == ("2330", 20))
    chk("單股相對機率→命中", single_ticker_rel_intent("2330 相對機率如何")[0] == "2330")
    chk("ETF 0050+漲跌機率→命中H20",
        single_ticker_rel_intent("在今天之後10天內0050漲跌的機率為何?") == ("0050", 20))
    chk("0050相對同儕→命中", single_ticker_rel_intent("0050相對同儕強弱")[0] == "0050")
    chk("年號剔除保真股", extract_tw_tickers("2026年展望2330") == ["2330"])
    chk("目標價→None(交 C)", single_ticker_rel_intent("2330 目標價多少") is None)
    chk("純哲學→None", single_ticker_rel_intent("什麼是知行合一") is None)
    chk("選股組合題不誤觸四碼假股", single_ticker_rel_intent("該買什麼股票") is None)
    # rel_prob_topk_intent(auto_rel_topn)
    chk("上漲機率 top3→(3,20)", rel_prob_topk_intent("未來30天上漲機率最高的top 3") == (3, 20))
    chk("相對機率前三→(3,*)", rel_prob_topk_intent("未來30天相對機率前三") == (3, 20))
    # 漲+跌／雙窗 → 看板意圖（topk 讓路）
    q_board = "在今天之後開始起漲，20天與60天後漲幅top 10與跌幅top 10，並列出都存在的個股"
    bi = rel_prob_board_intent(q_board)
    chk("雙窗漲跌看板意圖", bi is not None and bi["k"] == 10 and bi["horizons"] == (20, 60)
        and bi["include_bottom"] and bi["include_intersect"])
    chk("雙窗問句 topk 讓路", rel_prob_topk_intent(q_board) is None)
    chk("漲跌幅 top10→看板(非單向 topk)",
        rel_prob_topk_intent("在今天之後漲跌幅最top 10分别是什麼個股?") is None
        and rel_prob_board_intent("在今天之後漲跌幅最top 10分别是什麼個股?") is not None)
    chk("10天內僅漲幅 top→仍 topk",
        rel_prob_topk_intent("未來10天相對機率最高 top 10") == (10, 20))
    chk("漲跌幅前十→看板", rel_prob_board_intent("漲跌幅前十名個股") is not None)
    chk("目標價排名→None", rel_prob_topk_intent("目標價最高 top 3") is None)
    chk("大盤漲跌→True", market_binary_dir_intent("未來30天上漲還是下跌的機率高?") is True)
    chk("有股號漲跌→False(非大盤)", market_binary_dir_intent("2330上漲還是下跌?") is False)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.relevance --selftest;免 DB 免 API)")
