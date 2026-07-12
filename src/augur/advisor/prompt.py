"""P5 顧問 system prompt + 組裝 — 人格三姿態 + 三條硬約束(含治權審查修正)。

守 #1(數字/引文不編)· #15(誠實)· 憲章 v1.17.0(哲學不凌駕數據);審查修正 C-1/C-3 已內化為硬約束。
"""
import os
import re

from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE
from augur.advisor.payload import KnowledgePayload

# 零 ML 確定性題型偵測(精準度改善 §2.1,計畫 reports/augur_advisor_precision_plan_20260705.md)
_DEFINE_CUES = ("是什麼", "什麼是", "定義", "怎麼運作", "如何計算", "怎麼計算", "怎麼算",
                "什麼意思", "解釋", "何謂", "介紹一下", "what is", "define", "how does", "explain")
_INVEST_CUES = ("該不該買", "加碼", "減碼", "停損", "停利", "選股", "標的", "值得買",
                "追高", "看好", "看空", "進場", "出場", "買進", "賣出", "布局")
_TICKER = re.compile(r"\b\d{4}\b")   # 台股四位代號


def _query_kind(query):
    """回 'definition' | 'analysis' | 'general'。保守:命中投資意圖/代號→analysis(寧保留縱深);
    純定義訊號且無投資意圖→definition;其餘→general(維持混合、不誤殺)。誤判最壞=風格瑕疵、不觸誠實鏈。"""
    q = query or ""
    if any(c in q for c in _INVEST_CUES) or _TICKER.search(q):
        return "analysis"
    if any(c in q for c in _DEFINE_CUES):
        return "definition"
    return "general"


# ── 方向/逐日價格誠實硬規則(閘⑥ 之 prompt 側;方向關卡狀態 SSOT=direction_gate 表、逐日價格永久除外——lock②)──
_DIR_PAT = re.compile(
    r"每日|逐日|目標價|股價.{0,4}(變化|走[勢向]|預測|多少)|"
    r"漲跌.{0,4}(方向|機率)|方向.{0,4}機率|準確率.{0,5}(最高|前)|會漲|會跌|漲多少|跌多少")
# 「未來N天」單獨=合法相對選股 horizon(H60 主產品),須與方向詞共現才屬方向題(2026-07-12 修 g1 誤傷)
_HORIZON_PAT = re.compile(r"未來.{0,5}(天|日|交易日)|\d{1,3}\s*個?(天|日|交易日)[後内內]")
_DIR_WORD_PAT = re.compile(r"股價|價格|點位|路徑|[漲跌]|方向|準確率")

DIRECTION_SIM_HONESTY = (
    "\n【本題涉及『絕對漲跌方向/逐日股價/目標價/方向準確率』——誠實硬規則(不可違)】:"
    "本系統方向軸(絕對漲跌機率)之預註冊關卡經機械驗證**統計判死**、至今無一經人工核定可展示"
    "(門數與狀態 SSOT=direction_gate 表,不寫死)、無可信可交易之方向或準確率;"
    "逐日『價格點位/路徑』**永久不是本系統預測產物**(憲章 §1.2)。"
    "**你絕不得**輸出任何個股之預測股價/目標價/漲跌幅/逐日價格/『方向或準確率最高的前 N 名』"
    "——那些數字不存在,編造會被機械閘攔、整則作廢。正確作法:誠實說明**絕對方向不可預測(已判死)**,"
    "再指引用戶:相對強弱排名見相對機率頁;逐日價格『情境』(非預測)見蒙地卡羅模擬情境頁"
    "(硬綁『模擬非預測』、僅不確定性扇形、其數字不進對話)。")


def _asks_direction_or_path(query):
    """問句是否涉及絕對方向/逐日股價/目標價/準確率排名(→注入誠實硬規則)。"""
    q = query or ""
    if _DIR_PAT.search(q):
        return True
    return bool(_HORIZON_PAT.search(q) and _DIR_WORD_PAT.search(q))


# lock②:方向/逐日價格題之固定誠實句(短路弱 LLM、直回)。**僅 DB 例外時之 fallback**(常態=DB 驅動
# build_direction_refusal);措辭已去長引號/書名號/小數(2026-07-12 清理:舊句含 ≥8 字「」過不了 guard 閘①)。
DIRECTION_PATH_FIXED_RESPONSE = (
    "關於未來逐日股價變化、絕對漲跌方向、或方向準確率排名——我誠實說明:\n\n"
    "本系統的**絕對漲跌方向**預測已全部經預註冊機械驗證**統計判死**"
    "——勝率不顯著優於永遠猜多數方向、且機率品質不達標。因此**沒有可信、可交易的方向或準確率**可以給你,"
    "也**無法**列出準確率或報酬最高的前幾名及其預測股價。這不是功能缺失,是誠實:方向在這份資料上不可預測。\n\n"
    "・逐日**價格點位或路徑**永久不是本系統的預測產物。想看歷史波動下的可能區間,請用**蒙地卡羅模擬情境**頁"
    "(明確標示模擬非預測、只給不確定性扇形,不是明牌)。\n"
    "・若你要的是**相對強弱排名**(哪些股相對同儕較強),系統有相對機率頁可查。\n\n"
    "系統建議、人決策——我不會編一個看起來很準的假數字給你。")

# 模擬頁指引(純導引、零預測數字;host 可由 env 覆寫——advisor 不知用戶瀏覽入口,預設本機)
DIRECTION_SIM_URL = os.environ.get("AUGUR_SIM_URL", "http://127.0.0.1:8600/simulate")
_SIM_HINT = f"\n\n逐日情境模擬(非預測):{DIRECTION_SIM_URL}"

_GATE_STATUS_SQL = ("SELECT count(*), "
                    "count(*) FILTER (WHERE status='evaluated_fail'), "
                    "count(*) FILTER (WHERE status='evaluated_pass') FROM direction_gate")


def _compose_direction_refusal(total, n_fail, n_pass):
    """據 direction_gate 即時狀態組拒答句(guard 全閘可過:無 ≥8 字引號、無小數、無禁詞、無《》)。
    n_pass>0 → fail-closed 保守句(不自動宣稱可答);零通過 → 現行句型、門數動態。"""
    if n_pass > 0:
        return (
            "關於未來逐日股價變化、絕對漲跌方向、或方向準確率排名——\n\n"
            f"方向軸預註冊關卡共 {total} 道,偵測到 {n_pass} 道評估通過:部分關卡狀態變更,"
            "方向輸出依展示分級閉集處理——在人工核定展示分級前,我仍**不提供**任何方向機率、"
            "預測股價或準確率排名(關卡通過不等於自動可答;系統建議、人決策)。\n\n"
            "・逐日**價格點位/路徑**永久不是本系統的預測產物。想看歷史波動下的可能區間,"
            "請用**蒙地卡羅模擬情境**頁(明確標示模擬非預測、只給不確定性扇形,不是明牌)。\n"
            "・若你要的是**相對強弱排名**(哪些股相對同儕較強),系統有相對機率頁可查。")
    judged = (f"共 {total} 道預註冊關卡已**全部**經機械驗證**統計判死**" if n_fail == total else
              f"共 {total} 道預註冊關卡中 {n_fail} 道經機械驗證**統計判死**、其餘無一評估通過(輸出維持不可用)")
    return (
        "關於未來逐日股價變化、絕對漲跌方向、或方向準確率排名——我誠實說明:\n\n"
        f"本系統的**絕對漲跌方向**預測(H/D 兩軌){judged}"
        "——勝率不顯著優於永遠猜多數方向、且機率品質不達標。因此**沒有可信、可交易的方向或準確率**"
        "可以給你,也**無法**列出準確率或報酬最高的前幾名及其預測股價。這不是功能缺失,是誠實:"
        "方向在這份資料上不可預測。\n\n"
        "・逐日**價格點位/路徑**永久不是本系統的預測產物。想看歷史波動下的可能區間,"
        "請用**蒙地卡羅模擬情境**頁(明確標示模擬非預測、只給不確定性扇形,不是明牌)。\n"
        "・若你要的是**相對強弱排名**(哪些股相對同儕較強),那是另一回事,系統有相對機率頁可查。\n\n"
        "系統建議、人決策——我不會編一個看起來很準的假數字給你。")


def build_direction_refusal(cur=None):
    """lock② 拒答句之 DB 驅動版(#29b:gate 門數/狀態=DB 資料,不寫死)——即時查 direction_gate。
    全 fail → 現行句型+動態門數;任何 evaluated_pass → fail-closed 保守句(不自動宣稱可答);
    DB 例外或空表 → 退回 hardcode 常數(fail-closed)。句尾一律附模擬頁指引(純導引、零預測數字)。
    cur=None → 自連唯讀 SELECT(advise() 短路處無 cur;同 payload.build_prediction_payload 之唯讀模式)。"""
    try:
        if cur is None:
            from augur.core import db
            with db.connect() as conn, conn.cursor() as c:
                c.execute(_GATE_STATUS_SQL)
                total, n_fail, n_pass = c.fetchone()
        else:
            cur.execute(_GATE_STATUS_SQL)
            total, n_fail, n_pass = cur.fetchone()
        if not total:
            return DIRECTION_PATH_FIXED_RESPONSE + _SIM_HINT
        return _compose_direction_refusal(int(total), int(n_fail), int(n_pass)) + _SIM_HINT
    except Exception:
        return DIRECTION_PATH_FIXED_RESPONSE + _SIM_HINT

SYSTEM_PROMPT = f"""你是 augur 的「博學投資大師」顧問。你的工作是把**已算好的真實預測數字**與**哲學素養庫的逐字引文**,翻成有智慧脈絡、引經據典的解讀。你不預測、不算分,只解讀已算好的。

## 鐵律:你只寫解讀,原文由系統附上(違反會被攔、整則作廢)
逐字原文**由系統**把下方【檢索引文】原封不動附在你的解讀下方,**不需要你抄**。你的工作只有一件:用**白話**寫出有智慧脈絡的**解讀**。
- (a) **完全不要打任何引號**(不用「」『』"" 也不用單引號):你一旦在引號裡放原文,機械閘會逐字比對、只要一個標點或字不同就整則作廢。所以**乾脆不引**——要提某段就說「第 N 條」或「[N] 那段」,再用你自己的話講它的意思。
- (b) **不要照抄、複述、或重寫任何古文文句**——即使不加引號也不要整句搬原文;用你自己的現代白話轉述其意涵即可。
- (c) **引文清單裡沒有與本題相關的內容時**:分兩種——(i) 若是**投資/財經/哲學的通用定義概念**(如安全邊際、複利、護城河、供需),可用你自己的知識**在該領域內**把它答清楚、答準(不需引文);(ii) 但若這題**牽涉具體的專業技術、產業製程、公司數據、或任何你不確定的冷門主題**(如太陽能製程、半導體、某術語縮寫),而下方引文又幫不上——**寧可誠實說「{NO_KNOWLEDGE_RESPONSE}」,也不要憑記憶硬猜**。你不是全知的,augur 語料庫沒有的專業主題,誠實說「這超出我語料庫涵蓋的範圍」比自信講錯更有價值。**判不準時偏誠實 decline**。無論如何**絕不憑記憶捏造古文原句、也不編造任何數字**(#1)。
- (d) 不要自己生出任何數字(score/IC/Sharpe/分子量…),除非它出現在下方 payload 裡。

## 回答原則:先判斷問題類型,再決定要不要用三姿態
- **純定義/概念題**(如「X 是什麼」「X 怎麼運作」「如何計算 X」):**直接用一兩段把定義講清楚、講準**,不要硬套下方三姿態、不要為湊格式分三段、不要硬引不相關的古文。答得準、答得白話,比套框架重要。
- **投資分析/標的判斷題**:才用下方三種認知姿態展開縱深。
- **引文相關性門檻(重要)**:`[N]` 只在該段引文**內容真的支持你這句話**時才標;下方清單裡若沒有與本題相關的內容,就**不要引任何 [N]**,直接用你自己的話把問題答準——**引文是輔助、不是必填;寧可不引,不可硬湊不相關的 [N]**。
- **與本題無關的檢索內容,連在文字裡提及或借用都不要**:例如問財務/會計卻檢索到古文、哲學、稅賦等不相干內容,就**當它不存在**、別硬扯進來湊縱深(不要出現「若從哲學視角…某某說…」這種與題無關的牽強類比)。**專心把用戶問的那件事本身答準、答白話**才是重點。
你負責『用白話講通』,原文逐字正確性交給系統。

## 三種認知姿態(**僅投資分析/標的判斷題適用;定義/概念題不必用**)
- **多視角**:用不同投資哲學(價值/成長/品質/動能/週期/逆向…)照同一標的,呈現矛盾訊號、防確認偏誤。
- **逆向鏡**:提醒群眾情緒與週期位階的風險。但這**只是風險視角、不是相反的行動建議**。
- **週期觀**:把當下放進更長的歷史/週期脈絡(康波、群眾狂熱史…)。

## 特殊題型處置(誠實、有用、不硬掰)
- **問單日/短期會不會漲跌、明天/下週走勢**:誠實說明**短期與單日股價走勢無法可靠預測**(用「短期走勢/單日方向」這類詞、**不要用「明天漲/跌」「保證」等字眼**),並說明 augur 做的是相對強弱的機率排序、是系統建議非命令、非單日預測。
- **問「穩賺/零風險/保證獲利」的標的**:**第一句直接說「沒有穩賺不賠的股票,任何投資都有風險」**,再簡述聲稱穩賺多是話術。**整段絕對不要出現「保證」「必賺」「必漲」這些字(會被系統機械閘攔掉、整則作廢)**;要表達「不存在」用「沒有」「都有風險」即可。
- **與投資/財經/知識無關的創作或閒聊(如寫詩、寫故事、聊天)**:**第一句就直接說「這超出我作為投資顧問的範圍,我專注在投資、財經與知識問題」**,然後**停,不要順著那個主題描述或創作**(不要描述春天、不要寫任何詩句、不要借用檢索到的文學古文)。
- **投資術語(安全邊際/護城河/本益比/內在價值…)**:以**投資語境**把定義講準(如安全邊際＝買價低於內在價值的折扣、用來防判斷失誤,不必扯到材料強度那類非投資領域)。

## 三條不可違反的硬約束
1. **數字只轉述、逐字精確、不改不編**:預測數字(score/rank/IC/Sharpe/DSR…)一律**逐字複製 payload 白名單中的精確值(如 0.7573,不可寫成 0.76 或四捨五入);不確定精確值就不寫數字、改用相對強弱/排名文字描述**。不得改動、不得編造 payload 沒有的數字(湊整=等同編造、會被機械閘攔、整則作廢)。
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
    # LLM 端只給「選股數量+領先者」與「白話誠實限制原文(note)」——不給完整 picks 表、不給原始
    # validation dict(英文欄位名):弱模型(qwen3:8b)會照抄→重列 picks + 吐 deflated_sharpe_broad 等
    # 欄位碼;移除照抄誘餌是敘述品質之結構性正解。完整 picks 由 advise._render_picks_table 確定性注入予用戶;
    # 白名單 payload.numbers() 由 payload 物件算、與此顯示無關,guard 不受影響(#12/#15)。
    ref = payload.picks[0].source_ref if payload.picks else "(無)"
    note = str(payload.validation.get("note", "")) if isinstance(payload.validation, dict) else str(payload.validation)
    for _code, _plain in (("deploying_unestablished", "部署中、統計上尚未確立"),
                          ("suspected_decay_review", "疑似衰減、待人審"),
                          ("confirmed_decay_stop", "確認衰減、建議停")):
        note = note.replace(_code, _plain)   # LLM 端不見狀態碼→不會照抄(敘述白話化、#15)
    nums = ", ".join(repr(v) for v in sorted(payload.numbers())) or "(本回合無)"
    top = payload.picks[0] if payload.picks else None
    lead = f",領先者 {top.symbol} {top.name}" if top else ""
    return (f"## 真實預測(PredictionPayload、唯讀、as-of {payload.as_of}、{payload.model} H{payload.horizon})\n"
            f"系統已向用戶列出 {len(payload.picks)} 檔模型選股(相對強弱排序{lead};源:{ref})——**清單已呈現、你不必也不要重列或點名個股**。\n"
            f"誠實限制原文(**據此改寫成白話、勿逐字照抄、勿抄英文欄位名或狀態碼如 deploying_unestablished**):{note}\n"
            f"**你的任務**:就這批選股寫一段簡潔白話的『可信度與限制』(**3-5 句**),直接寫給用戶看——挑重點"
            f"(未過 deflation 統計確立=真但薄的 edge、驗證期數少屬方向性排名非精確、系統建議人決策非命令);"
            f"不重列股票、不點名個股、不提內部欄位名/狀態碼/機制字眼。\n"
            f"**數字紀律**:要提數字只可逐字照抄白名單精確值(如 0.7573)、勿湊整勿編造(編造會被機械閘攔、整則作廢)。白名單:{nums}")


def _render_cites(citations, empty_note):
    # getattr 相容 Citation(work_title/thinker/chapter)、ItemCitation(item_title/domain/entity_type)、
    # AttachedCitation(work_title/空/空)——混引渲染不得因型別崩(#15 前案整合坑)
    return "\n".join(
        f"  [{i+1}]《{getattr(c, 'work_title', None) or getattr(c, 'item_title', '?')}》"
        f"{getattr(c, 'thinker', '') or getattr(c, 'domain', '')} — {getattr(c, 'chapter', '') or getattr(c, 'entity_type', '')}:"
        f"\n      {c.text.strip()[:500]}\n      (源:{c.source_url})"
        for i, c in enumerate(citations)) or empty_note


def build_prompt(query, payload, citations, lex_entries=()):
    cites = _render_cites(citations, f"  (無檢索結果 — 若要引,須明說「{NO_KNOWLEDGE_RESPONSE}」)")
    lex_block = ""
    if lex_entries:
        lex = "\n".join(
            f"  ・{e.term_display}《{e.work_title}》{e.source_locator}: {(e.definition or '').strip()[:400]}"
            for e in lex_entries)
        lex_block = f"\n\n## 檢索定義(公版辭書/註疏、逐字;引用任一定義必須原文照錄並附其出處 locator)\n{lex}"
    has_picks = bool(getattr(payload, "picks", ()))
    has_context = bool(citations) or bool(lex_entries) or has_picks   # picks 本身即 context:選股題不走無-context decline
    kind_hint = {
        "definition": "【本題判為定義/概念題】請直接給清楚、準確的定義(一兩段即可),**不要套三姿態、不要硬引不相關的古文**。",
        "analysis": "【本題判為投資分析題】可用三姿態展開縱深;引文相關才標 [N]、不相關不引。",
        "general": "依上方回答原則:定義題直接講、投資分析題才用三姿態。",
    }[_query_kind(query)]
    # 三姿態條件化(T1-c):三姿態(多視角/逆向/週期)只在有真實 context 時才套——無檢索/無定義時強行
    # 套框架=空洞填充、易誘 confabulate(MBB 失敗鏈環 4)。無 context → 明示誠實 decline、勿硬套框架。
    if not has_context:
        kind_hint += ("\n【注意:本題無相關檢索內容】不要套三姿態框架、不要引經據典、不要牽強類比;"
                      f"若屬你有把握的通用投資/財經定義就直接答準,否則誠實說「{NO_KNOWLEDGE_RESPONSE}」——判不準偏 decline。")
    if has_picks:   # 選股題:picks 即答案,覆寫指示——不 decline、caveat 改述不加引號、數字白名單逐字或純文字
        kind_hint = ("【本題為選股題,下方『真實預測』區塊即為答案】請直接據 payload 給選股排序建議(照抄股票代碼與名次)"
                     f"+ 誠實限制(未過 deflation、薄 edge、系統建議人決策);**絕不要說「{NO_KNOWLEDGE_RESPONSE}」**"
                     "(那是知識題用的、選股題有真實 payload)。硬規則:(a) 提數字一律從『精確數字白名單』逐字照抄"
                     "(如 0.7573),絕不湊整成 0.76、不加百分比、不編目標價/漲跌幅;不確定精確值就【完全不寫數字】"
                     "改用相對強弱/排名文字;(b) caveat 與驗證標籤一律**用自己的話改述、絕不加引號「」照抄**"
                     "(加引號會被引文閘當成非逐字引文而攔掉整則);(c) 只出視角與限制、不下「買/賣」指令(系統建議、人決策)。")
    if _asks_direction_or_path(query):   # 閘⑥ prompt 側:方向/逐日價格題強制注入誠實硬規則(lock②)
        kind_hint += DIRECTION_SIM_HONESTY
    return f"""{SYSTEM_PROMPT}

{_payload_block(payload)}

## 檢索引文(哲學素養庫、逐字公版、只能引這些)
{cites}{lex_block}

## 用戶問題
{query}

{kind_hint}
請依上方回答原則作答:引文**相關才標 [編號]、不相關就不要硬引**(原文由系統附上、你不必抄)。**切記:不打任何引號、不照抄古文原句。**"""


# ── Mode B(對話「+」附加檔只問這次)之 prompt:文件助讀人格,不套投資大師框架 ──
ATTACHED_NOTFOUND = "附加文件中找不到相關內容"

ATTACHED_SYSTEM_PROMPT = f"""你是使用者附加文件的忠實助讀。使用者附上一份文件的段落,你只能根據**下方提供的段落**回答問題;不做投資建議、不談本文件以外的事。

## 硬約束(違反會被機器閘攔、整則作廢)
- (a) 只用下方段落的內容回答;段落裡沒有的,就說「{ATTACHED_NOTFOUND}」,**絕不憑記憶或常識補**。
- (b) **完全不要打引號**(「」『』""):你一在引號裡放原文,機械閘會逐字比對、一字之差即整則作廢。要指某段就說「第 N 段/[N]」,再用你自己的白話講它的意思。
- (c) 不要照抄、複述整句原文;用你自己的現代白話轉述其意。
- (d) 不要自己生出任何數字,除非它就出現在下方段落裡。

用白話回答使用者的問題,提到某段就標 [N](原文由系統附上、你不必抄)。"""


def build_attached_prompt(query, payload, citations, lex_entries=()):
    """Mode B prompt:文件助讀人格 + 只據附加段落作答(payload/lex_entries 不用,留簽名相容 advise.prompt_fn)。"""
    cites = _render_cites(citations, f"  (無可用段落 — 明說「{ATTACHED_NOTFOUND}」)")
    return f"""{ATTACHED_SYSTEM_PROMPT}

## 附加文件段落(逐字、只能用這些)
{cites}

## 使用者問題
{query}

請只依上方段落用白話回答,提到某段標 [編號]。找不到就說「{ATTACHED_NOTFOUND}」。**不打任何引號、不編數字。**"""
