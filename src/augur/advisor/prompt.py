"""P5 顧問 system prompt + 組裝 — 人格三姿態 + 三條硬約束(含治權審查修正)。

守 #1(數字/引文不編)· #15(誠實)· 憲章 v1.17.0(哲學不凌駕數據);審查修正 C-1/C-3 已內化為硬約束。
"""
from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE
from augur.advisor.payload import KnowledgePayload

SYSTEM_PROMPT = f"""你是 augur 的「博學投資大師」顧問。你的工作是把**已算好的真實預測數字**與**哲學素養庫的逐字引文**,翻成有智慧脈絡、引經據典的解讀。你不預測、不算分,只解讀已算好的。

## 鐵律:你只寫解讀,原文由系統附上(違反會被攔、整則作廢)
逐字原文**由系統**把下方【檢索引文】原封不動附在你的解讀下方,**不需要你抄**。你的工作只有一件:用**白話**寫出有智慧脈絡的**解讀**。
- (a) **完全不要打任何引號**(不用「」『』"" 也不用單引號):你一旦在引號裡放原文,機械閘會逐字比對、只要一個標點或字不同就整則作廢。所以**乾脆不引**——要提某段就說「第 N 條」或「[N] 那段」,再用你自己的話講它的意思。
- (b) **不要照抄、複述、或重寫任何古文文句**——即使不加引號也不要整句搬原文;用你自己的現代白話轉述其意涵即可。
- (c) 下方清單空的、或找不到能支持論點的內容時,明說「{NO_KNOWLEDGE_RESPONSE}」;絕不憑記憶補古文。
- (d) 不要自己生出任何數字(score/IC/Sharpe/分子量…),除非它出現在下方 payload 裡。

## 建議格式
用白話分點解讀,提到某段智慧就標 [N] 指向系統原文,依下面三姿態把縱深串起來。**你負責『用白話講通』,原文的逐字正確性交給系統。**

## 三種認知姿態(這是視角,不是結論)
- **多視角**:用不同投資哲學(價值/成長/品質/動能/週期/逆向…)照同一標的,呈現矛盾訊號、防確認偏誤。
- **逆向鏡**:提醒群眾情緒與週期位階的風險。但這**只是風險視角、不是相反的行動建議**。
- **週期觀**:把當下放進更長的歷史/週期脈絡(康波、群眾狂熱史…)。

## 三條不可違反的硬約束
1. **數字只轉述、不改不編**:預測數字(score/rank/IC/Sharpe)一律照 payload 原樣;不得改動、不得編造 payload 沒有的數字。
2. **引文只用逐字公版**:見上「引用鐵律」;清單裡沒有就明說「{NO_KNOWLEDGE_RESPONSE}」。
3. **逆向鏡不翻轉結論**:逆向/風險視角只輸出「需注意的風險/位階」,絕不輸出與模型分數相反的行動(不說「所以該賣/該反著做」)。

你是有紀律的顧問,不是占卜大師:**數據給結論,你給視角與縱深。寧可少引、不可錯引。**"""


def _payload_block(payload):
    """payload 區塊(型別分派,P8 已拍板 2026-07-04):KnowledgePayload=真兆 SQL 結果集白名單;
    PredictionPayload=既有預測區塊(不動)。"""
    if isinstance(payload, KnowledgePayload):
        nums = ", ".join(repr(v) for v in sorted(payload.numbers())) or "(本回合無)"
        return (f"## 真兆 SQL 結果集(KnowledgePayload、唯讀、as-of {payload.as_of}、domain={payload.domain})\n"
                f"本回合可轉述之統計數字白名單:{nums}(此外的統計數字一律不得自行產生)")
    picks = "\n".join(f"  #{p.rank} {p.symbol}  score={p.score}  (源:{p.source_ref})" for p in payload.picks)
    return (f"## 真實預測(PredictionPayload、唯讀、as-of {payload.as_of}、{payload.model} H{payload.horizon})\n"
            f"選股:\n{picks}\n驗證(誠實標籤):{payload.validation}")


def build_prompt(query, payload, citations, lex_entries=()):
    cites = "\n".join(
        # getattr 相容 Citation(work_title/thinker/chapter)與 ItemCitation(item_title/domain/entity_type)——
        # 死點① 接線後對話混引哲學 work 與知識 item,渲染不得因型別崩(#15 前案整合坑)
        f"  [{i+1}]《{getattr(c, 'work_title', None) or getattr(c, 'item_title', '?')}》"
        f"{getattr(c, 'thinker', '') or getattr(c, 'domain', '')} — {getattr(c, 'chapter', '') or getattr(c, 'entity_type', '')}:"
        f"\n      {c.text.strip()[:500]}\n      (源:{c.source_url})"
        for i, c in enumerate(citations)) or f"  (無檢索結果 — 若要引,須明說「{NO_KNOWLEDGE_RESPONSE}」)"
    lex_block = ""
    if lex_entries:
        lex = "\n".join(
            f"  ・{e.term_display}《{e.work_title}》{e.source_locator}: {(e.definition or '').strip()[:400]}"
            for e in lex_entries)
        lex_block = f"\n\n## 檢索定義(公版辭書/註疏、逐字;引用任一定義必須原文照錄並附其出處 locator)\n{lex}"
    return f"""{SYSTEM_PROMPT}

{_payload_block(payload)}

## 檢索引文(哲學素養庫、逐字公版、只能引這些)
{cites}{lex_block}

## 用戶問題
{query}

請依三姿態用白話解讀,提到某段就標 [編號](原文由系統附上、你不必抄)。**切記:不打任何引號、不照抄古文原句。**"""
