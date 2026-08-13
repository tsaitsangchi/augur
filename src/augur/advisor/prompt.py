"""🎯 P5 顧問 system prompt + 組裝 — 人格三姿態 + 三條硬約束(含治權審查修正)。

守 #1(數字/引文不編)· #15(誠實)· 憲章 v1.17.0(哲學不凌駕數據);審查修正 C-1/C-3 已內化為硬約束。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.prompt              # 印用途+公開入口（唯讀）
  python -m augur.advisor.prompt --selftest   # 純紅綠自測（零 IO）
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


def _compose_direction_refusal(total, n_fail, n_pass, *, market_binary=False):
    """據 direction_gate 即時狀態組拒答句(guard 全閘可過:無 ≥8 字引號、無小數、無禁詞、無《》)。
    n_pass>0 → fail-closed 保守句(不自動宣稱可答);零通過 → 現行句型、門數動態。
    market_binary=True：無股號之「漲還是跌」＝大盤絕對方向題——標【預測知識通道】周邊真兆、仍不給可交易漲跌機率。"""
    if n_pass > 0:
        body = (
            "關於未來逐日股價變化、絕對漲跌方向、或方向準確率排名——\n\n"
            f"方向軸預註冊關卡共 {total} 道,偵測到 {n_pass} 道評估通過:部分關卡狀態變更,"
            "方向輸出依展示分級閉集處理——在人工核定展示分級前,我仍**不提供**任何方向機率、"
            "預測股價或準確率排名(關卡通過不等於自動可答;系統建議、人決策)。\n\n"
            "・逐日**價格點位/路徑**永久不是本系統的預測產物。想看歷史波動下的可能區間,"
            "請用**蒙地卡羅模擬情境**頁(明確標示模擬非預測、只給不確定性扇形,不是明牌)。\n"
            "・若你要的是**相對強弱排名**(哪些股相對同儕較強),那是另一回事,系統有相對機率頁可查。")
    else:
        judged = (f"共 {total} 道預註冊關卡已**全部**經機械驗證**統計判死**" if n_fail == total else
                  f"共 {total} 道預註冊關卡中 {n_fail} 道經機械驗證**統計判死**、其餘無一評估通過(輸出維持不可用)")
        body = (
            "關於未來逐日股價變化、絕對漲跌方向、或方向準確率排名——我誠實說明:\n\n"
            f"本系統的**絕對漲跌方向**預測(H/D 兩軌){judged}"
            "——勝率不顯著優於永遠猜多數方向、且機率品質不達標。因此**沒有可信、可交易的方向或準確率**"
            "可以給你,也**無法**列出準確率或報酬最高的前幾名及其預測股價。這不是功能缺失,是誠實:"
            "方向在這份資料上不可預測。\n\n"
            "・逐日**價格點位/路徑**永久不是本系統的預測產物。想看歷史波動下的可能區間,"
            "請用**蒙地卡羅模擬情境**頁(明確標示模擬非預測、只給不確定性扇形,不是明牌)。\n"
            "・若你要的是**相對強弱排名**(哪些股相對同儕較強),那是另一回事,系統有相對機率頁可查。\n\n"
            "系統建議、人決策——我不會編一個看起來很準的假數字給你。")
    if market_binary:
        body += (
            "\n\n【預測知識通道・大盤】未指定股號 → 本題視為**大盤絕對漲跌**。"
            "知識結論與上列相同:**不能**回答「未來比較會長還是跌」的可交易機率"
            f"(方向閘通過道數為零、判死 {n_fail} 道)。"
            "周邊真兆(非漲跌裁決、不可解讀成明牌):個股相對機率的截面中位接近一半"
            "(校準定義使然、不是大盤漲跌訊號);"
            "研究用大盤方向列若存在亦**未過閘、不納入決策**。"
            "若要個股相對強弱請寫四碼股號;情境扇形見蒙地卡羅頁。")
    return body


# 權值／常出現在台股寬基相關討論之流動大型股（非官方 0050 成分表；宇宙交集後陳報）
_PEER_SNAPSHOT_CANDIDATES = (
    "2330", "2317", "2454", "2308", "2382", "2303", "3711", "2881", "2882",
    "2891", "2886", "2884", "2885", "2880", "2892", "2801", "5871", "2207",
    "2912", "1301", "1303", "2002", "2412", "3008", "2357", "3034", "2327",
    "2345", "2379", "2395", "2408", "2474", "2615", "3037", "3231", "3661",
)


def _hist_calendar_move_stats(stock_id, days=10, cur=None):
    """歷史「約 N 日曆日」報酬頻度（描述過去、≠未來機率）。回 dict 或 None。"""
    from datetime import timedelta
    from augur.catalog import world_concept

    def _run(c, conn=None):
        # WM.36：價表經 registry，不字面直綁供應商表
        bar_sql = world_concept.resolve_sql("tw.daily_bar", conn=conn)
        c.execute(
            f'SELECT "date", "close" FROM {bar_sql} '
            "WHERE stock_id=%s ORDER BY 1",
            (str(stock_id),),
        )
        rows = c.fetchall()
        if len(rows) < 30:
            return None
        rets = []
        for i, (d, px) in enumerate(rows[:-1]):
            target = d + timedelta(days=int(days))
            j = None
            for k in range(i + 1, len(rows)):
                if rows[k][0] >= target:
                    j = k
                    break
            if j is None:
                continue
            p0, p1 = float(px), float(rows[j][1])
            if p0 > 0:
                rets.append(p1 / p0 - 1.0)
        if len(rets) < 50:
            return None
        rets.sort()
        n = len(rets)
        up = sum(1 for r in rets if r > 0) / n
        med = rets[n // 2]
        p25, p75 = rets[n // 4], rets[(3 * n) // 4]
        last_d, last_px = rows[-1][0], float(rows[-1][1])
        return {
            "n": n, "up_rate": up, "median": med, "p25": p25, "p75": p75,
            "last_date": str(last_d), "last_close": last_px, "days": int(days),
        }

    try:
        if cur is not None:
            return _run(cur, conn=getattr(cur, "connection", None))
        from augur.core import db
        with db.connect() as conn, conn.cursor() as c:
            return _run(c, conn=conn)
    except Exception:
        return None


def _peer_rel_snapshot(horizon=20, as_of=None, cur=None, limit=5):
    """宇宙內權值候選之相對機率快照（≠ ETF 方向）。回 dict 或 None。"""

    def _run(c):
        ao = as_of
        if ao is None:
            c.execute(
                "SELECT max(panel_date) FROM prediction_probability WHERE horizon=%s",
                (int(horizon),),
            )
            ao = (c.fetchone() or [None])[0]
        if ao is None:
            return None
        c.execute(
            "SELECT stock_id, p_beat_median, rank_pctile, econ_verdict FROM prediction_probability "
            "WHERE panel_date=%s AND horizon=%s AND stock_id = ANY(%s) "
            "ORDER BY p_beat_median DESC NULLS LAST",
            (ao, int(horizon), list(_PEER_SNAPSHOT_CANDIDATES)),
        )
        rows = c.fetchall()
        if not rows:
            return None
        beats = [float(r[1]) for r in rows if r[1] is not None]
        if not beats:
            return None
        beats_s = sorted(beats)
        med = beats_s[len(beats_s) // 2]
        frac = sum(1 for x in beats if x > 0.5) / len(beats)
        top = [
            (str(r[0]), round(float(r[1]) * 100, 1), r[3])
            for r in rows[: int(limit)]
        ]
        return {
            "as_of": str(ao), "horizon": int(horizon), "n": len(rows),
            "median_pct": round(med * 100, 1),
            "frac_above_half": round(frac * 100, 1),
            "top": top,
        }

    try:
        if cur is not None:
            return _run(cur)
        from augur.core import db
        with db.connect() as conn, conn.cursor() as c:
            return _run(c)
    except Exception:
        return None


def _advice_bundle_for_query(query, cur=None):
    """絕對方向拒答後之誠實建議包（憲政切片路徑 2 旁側）：相對真兆／宇宙缺口／窗對齊／MC。
    **禁**輸出看漲／看跌絕對％；有 p_beat 時硬綁 GATE 未過＋econ_verdict。
    宇宙外（如 0050）加：歷史頻度＋權值相對快照＋行動清單。"""
    from augur.advisor.relevance import (
        extract_tw_tickers, single_ticker_rel_intent, _horizon_from_query,
    )
    lines = ["", "【系統可給的誠實建議・非看漲／看跌％】"]
    q = query or ""
    tickers = extract_tw_tickers(q)
    sti = single_ticker_rel_intent(q)
    h_ask = _horizon_from_query(q, default=60)
    want_short = bool(re.search(r"(1[0-4]|[7-9])\s*(天|日)|兩\s*週|两\s*周|10\s*天", q))
    if want_short:
        lines.append(
            f"・窗口:你問約短窗（如十天）——系統**無**十交易日確立產物；"
            f"最接近短尺為 **H{h_ask}**（交易日、約對應月曆更長），下列相對尺皆依此、**不是**十日絕對漲跌。"
        )
    if not tickers:
        lines.append(
            "・未偵測到四碼股號:若要**個股相對強弱**建議,請寫如 2330 相對同儕 H20;"
            "若只要情景扇形,用蒙地卡羅頁(模擬非預測)。"
        )
    else:
        sid = tickers[0]
        h = sti[1] if sti else h_ask
        lines.append(f"・偵測股號 **{sid}**(H{h} 相對尺嘗試):")
        has_rel = False
        try:
            from augur.advisor.payload import build_single_ticker_rel_payload
            pl = build_single_ticker_rel_payload(sid, h)
            if pl.probs:
                has_rel = True
                p_sid, p_h, p_beat, ev, cd = pl.probs[0]
                pct = round(float(p_beat) * 100, 1)
                lines.append(
                    f"  — 相對真兆:as-of {pl.as_of}、H{p_h}≈{cd} 日曆日、"
                    f"**P(勝過同儕中位)≈{pct}%**、econ_verdict={ev}。"
                    f"**這不是**看漲／看跌絕對機率;direction_gate 未過,不得確立漲跌;系統建議、人決策。"
                )
            else:
                note = (pl.validation or {}).get("note", "無列")
                lines.append(
                    f"  — 現役**相對機率宇宙無此代號**({note})。"
                    f"常見於 ETF／非 train 宇宙:**不能**捏造該檔漲跌％或假相對％。"
                )
        except Exception:
            lines.append(
                "  — 相對真兆讀取失敗(fail-soft);仍**不**提供絕對漲跌％。"
            )
        # 歷史頻度（短窗問句或宇宙外代號）
        if want_short or not has_rel:
            hist = _hist_calendar_move_stats(sid, days=10, cur=cur)
            if hist:
                lines.append(
                    f"  — **歷史描述**(非預測):約 {hist['days']} 日曆日持有、樣本 n={hist['n']}、"
                    f"過去上漲頻度約 **{hist['up_rate']*100:.1f}%**、"
                    f"報酬中位約 {hist['median']*100:+.2f}%、"
                    f"四分位約 [{hist['p25']*100:+.2f}%, {hist['p75']*100:+.2f}%];"
                    f"最新收盤 as-of {hist['last_date']}≈{hist['last_close']:.2f}。"
                    f"**過去頻度≠未來機率**;不可當看漲／看跌％。"
                )
        # 權值相對快照（ETF／無列時必給；有相對時可略）
        if not has_rel:
            snap = _peer_rel_snapshot(horizon=h, cur=cur, limit=5)
            if snap:
                tops = "、".join(
                    f"{t} P(中位)≈{p}%({ev})" for t, p, ev in snap["top"]
                )
                lines.append(
                    f"  — **權值股相對快照**(非正式成分表;as-of {snap['as_of']} H{snap['horizon']};"
                    f"命中 {snap['n']} 檔):**≠{sid} 漲跌方向**。"
                    f"樣本中位 P(勝同儕中位)≈{snap['median_pct']}%;"
                    f"P>50% 占比約 {snap['frac_above_half']}%;"
                    f"相對較強例:{tops}。"
                    f"econ 多為 dead／thin 時更不可當可交易絕對方向。"
                )
        # 行動建議（人決策）
        lines.append("  — **行動建議**(系統建議、人決策;非下單指令):")
        if not has_rel:
            lines.append(
                "    (1) 若你要的是 ETF 點位不確定性:開蒙地卡羅頁對 0050／同標的做扇形"
                f"({DIRECTION_SIM_URL}),硬讀『模擬非預測』。"
            )
            lines.append(
                "    (2) 若你要可引用數字:改問宇宙內個股相對強弱"
                "(例:2330／2317／2454 相對同儕 H20),再自己組合成「權值籃」觀點——"
                "**組合觀點仍≠0050 確立漲跌％**。"
            )
            lines.append(
                "    (3) 歷史上漲頻度偏高**只**表示樣本內常正報酬,不含择時優勢;"
                "方向閘未過 → **不建議**把任何％當成進場依據。"
            )
        else:
            lines.append(
                "    (1) 只用相對 P 與同儕比較,莫改寫成會漲／會跌％;"
                "(2) 看 econ_verdict=dead／thin 則當成研究標註而非下單;"
                f"(3) 情景:{DIRECTION_SIM_URL}。"
            )
    lines.append(
        "・系統研究尺(投組 OOS、**非**你問的那一檔預測):短／中窗以 RankRidge 為主;"
        "方向閘通過數為零時任何「會漲％」皆不可用。"
    )
    lines.append(
        "・下一步可怎麼問才拿得到更多個股數字:"
        "「2330 相對同儕未來約二十交易日」或相對機率頁;"
        f"情景扇形:{DIRECTION_SIM_URL}"
    )
    return "\n".join(lines)


def build_direction_refusal(cur=None, query=None):
    """lock② 拒答句之 DB 驅動版(#29b:gate 門數/狀態=DB 資料,不寫死)——即時查 direction_gate。
    全 fail → 現行句型+動態門數;任何 evaluated_pass → fail-closed 保守句(不自動宣稱可答);
    DB 例外或空表 → 退回 hardcode 常數(fail-closed)。句尾一律附模擬頁指引(純導引、零預測數字)。
    query:可選;無股號且「漲還是跌」類 → 大盤知識通道 enrich；有股號 → 附誠實建議包。
    cur=None → 自連唯讀 SELECT(advise() 短路處無 cur;同 payload.build_prediction_payload 之唯讀模式)。"""
    market_binary = False
    if query:
        try:
            from augur.advisor.relevance import market_binary_dir_intent
            market_binary = bool(market_binary_dir_intent(query))
        except Exception:
            market_binary = False
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
            base = DIRECTION_PATH_FIXED_RESPONSE + _SIM_HINT
            if market_binary:
                base = (
                    DIRECTION_PATH_FIXED_RESPONSE
                    + "\n\n【預測知識通道・大盤】未指定股號 → 大盤絕對漲跌題;"
                    "閘狀態讀取失敗時仍**不**提供可交易漲跌機率。"
                    + _SIM_HINT
                )
        else:
            base = _compose_direction_refusal(
                int(total), int(n_fail), int(n_pass), market_binary=market_binary,
            ) + _SIM_HINT
    except Exception:
        base = DIRECTION_PATH_FIXED_RESPONSE + _SIM_HINT
    # Steward：拒絕對方向後仍要能給建議——同屏 bundle（有股號或相對意圖時）
    if query:
        try:
            base = base + _advice_bundle_for_query(query, cur=cur)
        except Exception:
            pass
    return base

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


# ── brief/1 情境節(INTEG-C P-C;v2 §3.2 邊 3)──────────────────────────────
# fail-open:檔不在/壞=無此節(brief 是增益非誠實閘);mtime memo 免重複 IO(同 MCP _serving_pack 慣例)。
# 只在問題涉及進化/擂台時注入(keyword gate)——別的題塞帳本=噪音+context 浪費。
_BRIEF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "var", "briefs")
_BRIEF_GATE = re.compile(r"arena|擂台|進化|evolution|prodset|生產特徵|對照臂|SUNSET|kill.?switch|自進化")
_BRIEF_CACHE: dict = {"path": None, "mtime": None, "block": ""}


def _brief_block(query):
    if not _BRIEF_GATE.search(query or ""):
        return ""
    try:
        import glob as _g
        import json as _j
        paths = sorted(_g.glob(os.path.join(_BRIEF_DIR, "brief_*.json")))
        if not paths:
            return ""
        p = paths[-1]
        mt = os.path.getmtime(p)
        if _BRIEF_CACHE["path"] == p and _BRIEF_CACHE["mtime"] == mt:
            return _BRIEF_CACHE["block"]
        with open(p, encoding="utf-8") as f:
            obj = _j.load(f)
        lines = "\n".join(f"  ・{c['text']}(帳本:{c['ref']})"
                          for c in obj.get("claims", []) if c.get("claim_level") == "ledger_fact")
        block = (f"\n\n## 進化/擂台帳本現況(brief {obj.get('as_of')};逐條=帳本事實可查表)\n{lines}\n"
                 "  (引用規則:只得轉述上列事實與其表名;不得外推、不得加值判斷、不得使用"
                 "「可交易/確立級」等宣稱——guard 會攔)") if lines else ""
        _BRIEF_CACHE.update(path=p, mtime=mt, block=block)
        return block
    except Exception:  # noqa: BLE001  fail-open:brief 壞不壞殼
        return ""


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
    if any(getattr(c, "item_id", None) is not None for c in (citations or ())):
        kind_hint += ("\n【Know-how 水印】若多則本地知識引文，優先依據較深 Know-how 水印"
                      "（KH9＞KH8＞KH7）之材料作答，勿用較淺引文覆蓋較深結論。"
                      "即使僅達 KH0（原文在庫），仍須依檢索引文作基本理解作答，"
                      "不得在已有內文引文時改口稱知識庫中無此內容。")
    return f"""{SYSTEM_PROMPT}

{_payload_block(payload)}

## 檢索引文(哲學素養庫、逐字公版、只能引這些)
{cites}{lex_block}{_brief_block(query)}

## 用戶問題
{query}

{kind_hint}
請依上方回答原則作答:引文**相關才標 [編號]、不相關就不要硬引**(原文由系統附上、你不必抄)。**切記:不打任何引號、不照抄古文原句。**"""


COMPACT_KNOWHOW_PROMPT = """你是本地知識庫的簡短技術助讀。只能根據下方「檢索引文」用白話回答使用者問題。

## 硬約束（違反會被機器閘攔）
- (a) 只依據下方引文；沒有的就說「知識庫中無此內容」——不憑記憶補。
- (b) **完全不要打引號**（「」『』""）；不要複述或照抄使用者問題原文。
- (c) **禁止開場想題／複述本提示**：不要寫「首先我需要…」「使用者要求我…」「硬約束」「關鍵點」這類過程。
- (d) **第一行起即用編號逐步條列**：`1.` `2.` `3.` …；**每一行一步**；不要寫成一整段摘要；不要整篇照抄引文。
- (e) 只列引文裡有的操作／設定／路徑／驗證；約 5～12 步、總長約 200～500 字；提某段可標 [N]。
- (f) 不要套投資三姿態；這不是選股題。
- (g) **設定／欄位題**（含 wsj、VARCHAR、IP、站台、SOAP）：每步若改某欄，必須寫出 **`欄位碼=範例或定稿值`**（如 `wsj02=10.1.2.30`）；**禁止**只寫「修改 wsj02」而不給字串。引文標「範例」則照抄範例並可註非現場；無值則列出使用者須提供的欄位，禁止捏造實機 IP／庫名。
"""

COMPACT_KNOWHOW_PROMPT_SUMMARY = """你是本地知識庫的簡短技術助讀。只能根據下方「檢索引文」用白話回答使用者問題。

## 硬約束（違反會被機器閘攔）
- (a) 只依據下方引文；沒有的就說「知識庫中無此內容」——不憑記憶補。
- (b) **完全不要打引號**（「」『』""）；不要複述或照抄使用者問題原文。
- (c) **禁止開場想題／複述本提示**：不要寫「首先我需要…」「使用者要求我…」「硬約束」「關鍵點」這類過程。
- (d) **第一行就寫實質內容**（文件在講什麼／步驟要點）；技術用條列；總長約 150～400 字；提某段標 [N]。
- (e) 不要套投資三姿態；這不是選股題。
"""


def _compact_stepwise_enabled() -> bool:
    """預設開；AUGUR_COMPACT_STEPWISE=0/off/false 可關（短摘要口吻）。"""
    v = (os.environ.get("AUGUR_COMPACT_STEPWISE") or "1").strip().lower()
    return v not in ("0", "off", "false", "no")


def build_compact_knowhow_prompt(query, payload, citations, lex_entries=()):
    """緊湊知-how／讀出 prompt：短答、禁想題、禁引號；預設逐步條列（本機 LLM 生成）。"""
    cites = _render_cites(citations, f"  (無檢索結果 — 明說「{NO_KNOWLEDGE_RESPONSE}」)")
    q = query or ""
    want_ops = bool(re.search(r"(逐步|每行一步|操作步驟|1\.\s*2\.\s*3\.|編號)", q))
    want_fill = bool(
        re.search(
            r"(wsj\d+|填寫|填什麼|要填|VARCHAR2?|站台\s*IP|SOAP|設定檔|欄位)",
            q,
            re.I,
        )
    )
    if _compact_stepwise_enabled():
        body = COMPACT_KNOWHOW_PROMPT
        if want_ops or want_fill:
            out_hint = (
                "【輸出·強制操作步】必須從第一行起用阿拉伯數字編號：`1.` `2.` `3.` …\n"
                "每一行＝一個可執行操作（動詞開頭：啟動／確認／選擇／執行／驗證…）。\n"
                "禁止：`- [1]` 引文摘要、一段話概括、複述「這是關於…」。\n"
                "禁止自我提醒或複述硬約束。不打引號。"
            )
            if want_fill:
                out_hint += (
                    "\n【設定填值】凡提到欄位必須寫 `欄位=值` 範例或定稿"
                    "（如 wsj02=10.1.2.30、wsj04=EFGP_PROD）；禁止只寫改某欄。"
                )
        else:
            out_hint = (
                "【輸出】從第一行開始用 1. 2. 3. 逐步條列。每一行一步。"
                "禁止一段式摘要、禁止自我提醒或複述上方硬約束。不打引號。"
            )
    else:
        body = COMPACT_KNOWHOW_PROMPT_SUMMARY
        out_hint = "【輸出】從第一行開始寫實質摘要／步驟。禁止任何自我提醒或複述上方硬約束。不打引號。"
    return f"""{body}

{_payload_block(payload)}

## 檢索引文（逐字、只能用這些）
{cites}

## 使用者問題
{query}

{out_hint}"""


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


def _selftest():
    # 純紅綠:零 IO——只驗確定性題型偵測與拒答句組裝(不觸 DB 版 build_direction_refusal)
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # _query_kind:投資意圖/代號→analysis;純定義→definition;其餘→general
    chk("投資意圖→analysis", _query_kind("台積電該不該買") == "analysis")
    chk("四位代號→analysis", _query_kind("1234 如何") == "analysis")
    chk("定義訊號→definition", _query_kind("本益比是什麼") == "definition")
    chk("無訊號→general", _query_kind("你好") == "general")
    # compact know-how prompt（零 IO）
    from types import SimpleNamespace as S
    from augur.advisor.payload import empty_payload
    cp = build_compact_knowhow_prompt(
        "國碩請讀出", empty_payload(),
        [S(text="正文RMAN /u5", item_title="t", source_url="")], ())
    chk("compact 禁想題", "禁止開場想題" in cp and "RMAN" in cp)
    chk("compact 禁引號指令", "不要打引號" in cp)
    chk("compact 預設逐步", "1. 2. 3." in cp and "每一行一步" in cp)
    cp_fill = build_compact_knowhow_prompt(
        "如何填寫 wsj02 EasyFlow 站台 IP", empty_payload(),
        [S(text="wsj02=10.1.2.30 範例", item_title="填寫範例", source_url="")], ())
    chk("compact 設定填值提示", "欄位=值" in cp_fill and "wsj02=" in cp_fill)
    old = os.environ.get("AUGUR_COMPACT_STEPWISE")
    os.environ["AUGUR_COMPACT_STEPWISE"] = "0"
    try:
        cp0 = build_compact_knowhow_prompt(
            "國碩請讀出", empty_payload(),
            [S(text="正文RMAN /u5", item_title="t", source_url="")], ())
        chk("compact stepwise off→摘要", "實質摘要" in cp0 and "每一行一步" not in cp0)
    finally:
        if old is None:
            os.environ.pop("AUGUR_COMPACT_STEPWISE", None)
        else:
            os.environ["AUGUR_COMPACT_STEPWISE"] = old
    # _asks_direction_or_path:方向詞命中;horizon 單獨不算、須與方向詞共現
    chk("方向詞→True", _asks_direction_or_path("明天會漲嗎") is True)
    chk("horizon 單獨→False", _asks_direction_or_path("未來5天") is False)
    chk("horizon+方向詞→True", _asks_direction_or_path("未來5天股價") is True)
    chk("純定義→False", _asks_direction_or_path("安全邊際是什麼") is False)
    # _compose_direction_refusal:全 fail 與 有 pass 之句型分支
    chk("全 fail 句含『全部』", "全部" in _compose_direction_refusal(6, 6, 0))
    chk("有 pass→保守句", "關卡通過不等於自動可答" in _compose_direction_refusal(6, 0, 1))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.prompt --selftest;免 DB 免 API)")
