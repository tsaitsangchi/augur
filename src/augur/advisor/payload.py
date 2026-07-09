"""P5 PredictionPayload — 量化本體 → 顧問前端的唯一唯讀資料通道。

🎯 as-of 快照凍結的真實預測(選股 + score + 驗證標籤)。frozen dataclass = 顧問**不可改一個數字**;
   所有數字帶 source_ref、trace 回真實模型輸出(#1);validation 帶誠實標籤(#15)。
守 #1(數字 trace 真實模型)· #15(validation 誠實標籤)· 憲章 v1.17.0(顧問對此唯讀、零寫回)。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class StockPick:
    symbol: str
    rank: int
    score: float
    source_ref: str          # trace 回真實模型輸出(如 eval/portfolio.py 之某 as-of run)
    name: str = ""           # 公司名(TaiwanStockInfo;#1 給模型正確名、防幻覺股名——guard 查輸出股名 ∈ 此)


@dataclass(frozen=True)
class PredictionPayload:
    as_of: str               # as-of 日期(快照凍結、防洩漏 #8)
    horizon: int             # 預測期(如 60 日)
    model: str               # 產生預測的真實模型(如 "F3 as-of Ridge")
    picks: tuple             # (StockPick, ...) 橫斷面 top-N
    validation: dict         # {rank_ic, sharpe, note, ...} 誠實驗證標籤(#15)

    def numbers(self):
        """回 payload 內所有真實數字(供 guard:顧問輸出的預測數字必須 ∈ 此集合、不得編造)。"""
        ns = set()
        for p in self.picks:
            ns.add(round(p.score, 4))
            ns.add(float(p.rank))
        for v in self.validation.values():
            if isinstance(v, (int, float)):
                ns.add(round(float(v), 4))
        return ns


@dataclass(frozen=True)
class KnowledgePayload:
    """知識域對偶 payload(計畫 §3-S7 N6;P8 已拍板 2026-07-04,guard 域條款已接線——
    advise() 對本型別分派 guard_knowledge,oai_compat 唯一出口=advise() 同路生效)。

    PredictionPayload 之知識域對偶:frozen=顧問不可改一字;.numbers()=本回合真兆 SQL 結果集
    白名單(guard 域條款 ② 數字雙源之一;每個值皆須出自 DB query,#9b 可溯源)。
    picks 恆空 → guard ④ 逆向閘自然 no-op(無模型選股結論可翻轉,計畫 P8 ④)。
    """
    as_of: str               # 快照時點(防洩漏 #8)
    domain: str              # 知識域(如 'chemistry';registry SSOT)
    sql_numbers: frozenset = frozenset()   # 本回合真兆 SQL 結果集(唯一合法數字來源;非 SQL 產出禁入)
    picks: tuple = ()        # 恆空:知識 payload 無模型選股

    def numbers(self):
        """回本回合真兆 SQL 結果集之白名單(供 guard 域條款 ②:輸出統計數字必須 ∈ 此集合)。"""
        return {round(float(v), 4) for v in self.sql_numbers}


def example_payload():
    """示範 payload(供 P5 架構測試;真實資料由量化本體 as-of 預測填入,屬後續整合)。"""
    return PredictionPayload(
        as_of="2026-05-31", horizon=60, model="F3 as-of Ridge",
        picks=(
            StockPick("2330", 1, 0.87, "eval/portfolio.py:asof_run"),
            StockPick("2317", 2, 0.72, "eval/portfolio.py:asof_run"),
            StockPick("2454", 3, 0.65, "eval/portfolio.py:asof_run"),
        ),
        validation={"rank_ic": 0.1418, "sharpe": 1.26,
                    "note": "alpha 僅 long 側、long-short 無效;Sharpe 為扣成本後 purged walk-forward"},
    )


def empty_payload():
    """一般問答之空 payload(精準度改善 §2.4 D-1):非選股題【不注入示範選股】——去雜訊 + 避免把示範/非真實
    數字夾進每則回覆。numbers()=∅ → guard 數字白名單為空、模型自造任何統計數字皆被攔(**更嚴不更鬆**,守 #1);
    picks 恆空 → guard ④ 逆向閘自然 no-op。真實選股問答另走 PredictionPayload。"""
    return KnowledgePayload(as_of="2026-05-31", domain="general", sql_numbers=frozenset())


# ── D4:真實 as-of 預測 payload(prediction_values + revalidation_ledger,計畫 §5.2)──
# 部署主模型=Ridge H60 LO(2026-07-07 對齊):panel 2026-05-31、34 檔 in_portfolio equal-weight。
# H120 為追蹤候選(in_portfolio=0)不出 payload。此值為 code 之部署選擇、非資料鎖;prediction_values
# 之 in_portfolio 旗標為 DB 側 SSOT,本函式只讀不寫(隔離不變式:advisor 對預測表唯讀)。
_DEPLOY_FAMILY = "RankRidge"          # 部署主模型家族(H60 LO ridge)
_DEPLOY_CELL = "ridge_H60_LO"         # harness 部署 cell(deflated 地板 + 再驗證裁決之座標)

# 部署模型驗證標籤之 ledger 座標(#15 每個數字 trace 回一列 revalidation_ledger,非記憶/估算)。
# key=payload.validation 欄名;value=(stage, model, config, metric_name, 取 metric_value 或 'hac_t'/'n_periods' 欄)。
# 部署投組=Ridge H60 LO;C 全期(since2014,n=25)為主樣本、D 近期(since2021,n=18)為小樣本 caveat 對照。
_VALIDATION_LEDGER_KEYS = (
    ("rank_ic",           "B", "B2_ridge", "asof_ic",      "mean_ic",      "metric_value"),
    ("ic_hac_t",          "B", "B2_ridge", "asof_ic",      "mean_ic",      "hac_t"),
    ("ic_n_periods",      "B", "B2_ridge", "asof_ic",      "mean_ic",      "n_periods"),
    ("net_sharpe",        "C", "ridge",    "LO|since2014", "net_sharpe",   "metric_value"),
    ("bench_sharpe",      "C", "ridge",    "LO|since2014", "bench_sharpe", "metric_value"),
    ("net_maxdd",         "C", "ridge",    "LO|since2014", "net_maxdd",    "metric_value"),
    ("net_sharpe_recent", "D", "ridge",    "LO|since2021", "net_sharpe",   "metric_value"),
    ("net_maxdd_recent",  "D", "ridge",    "LO|since2021", "net_maxdd",    "metric_value"),
    ("n_periods_recent",  "D", "ridge",    "LO|since2021", "net_sharpe",   "n_periods"),
)

_COST_PCT = 0.585   # 淨值假設之單邊交易成本(方法論 SSOT,plan §5.3/line 200;net_* 已扣此成本)


def _read_validation(cur, horizon):
    """自 revalidation_ledger 讀部署模型之驗證標籤(#15 可溯源:每值一列 ledger、附 stage source_ref)。
    回 (validation_dict, missing_keys)——某座標查無 → 誠實列 missing(不編數字補),不 raise。"""
    v, missing = {}, []
    for name, stage, model, config, metric, col in _VALIDATION_LEDGER_KEYS:
        col_expr = {"metric_value": "metric_value", "hac_t": "hac_t", "n_periods": "n_periods"}[col]
        cur.execute(
            f"SELECT {col_expr} FROM revalidation_ledger "
            "WHERE horizon=%s AND stage=%s AND model=%s AND config=%s AND metric_name=%s "
            "ORDER BY run_at DESC LIMIT 1",
            (horizon, stage, model, config, metric))
        row = cur.fetchone()
        if row is None or row[0] is None:
            missing.append(name)
            continue
        v[name] = int(row[0]) if col == "n_periods" else float(row[0])
    return v, missing


def _read_harness_floor(cur, cell=_DEPLOY_CELL):
    """讀 harness 誠實地板(revalidation_baseline 兩宇宙 deflated 地板)+ 最新兩軌三態裁決狀態
    (revalidation_verdict)。#15:讓 caveat 帶「headline 未過 deflation、廣宇宙更薄」之最誠實地板。
    表未建(harness 未跑)→ 回空(to_regclass 檢查、不 abort 交易);advisor 對此唯讀零寫(隔離不變式)。"""
    out = {}
    cur.execute("SELECT to_regclass('revalidation_baseline'), to_regclass('revalidation_verdict')")
    has_base, has_verdict = cur.fetchone()
    if has_base:
        cur.execute("SELECT universe, dsr, deflated_ann, net_excess FROM revalidation_baseline WHERE cell=%s", (cell,))
        for uni, dsr, defl, ne in cur.fetchall():
            pfx = {"asof_incumbent": "asof", "pit_broad": "broad"}.get(uni)
            if pfx:
                out[f"{pfx}_dsr"] = float(dsr) if dsr is not None else None
                out[f"{pfx}_deflated"] = float(defl) if defl is not None else None
    if has_verdict:
        cur.execute("SELECT state FROM revalidation_verdict WHERE cell=%s AND track='B_decay' "
                    "ORDER BY as_of_date DESC LIMIT 1", (cell,))
        r = cur.fetchone()
        if r:
            out["verdict_state"] = r[0]
    return out


def build_prediction_payload(as_of=None, horizon=60, top_n=None):
    """D4:自 DB 組真實 as-of 預測 payload(取代 example_payload;計畫 §5.2)。

    · picks = prediction_values 部署 H60 投組(in_portfolio=true,或 top_n rank);
      每檔 source_ref 指回 prediction_values 之 panel+model(#15 可溯源);
    · validation = revalidation_ledger 讀出之已凍結標籤(rank_ic/HAC-t/淨 Sharpe/基準/MaxDD;#15 非記憶),
      note 含誠實 caveat(alpha 僅 long 側、n 小 18-25 屬方向性非精確、survivorship 債 b 未閉環、
      扣成本 0.585% 後淨值);validation source_ref 標 revalidation_ledger:stage=B/C/D。
    · as_of=None → 取最新 panel_date;horizon=60(部署主模型);top_n=None → in_portfolio 全投組。
    advisor 對預測/驗證表**唯讀零寫**(隔離不變式);回 frozen PredictionPayload(顧問不可改一個數字)。
    """
    from augur.core import db
    with db.connect() as conn, db.transaction(conn) as cur:
        if as_of is None:
            cur.execute("SELECT max(panel_date) FROM prediction_values "
                        "WHERE model_id IN (SELECT model_id FROM model_registry "
                        "WHERE family=%s AND horizon=%s)", (_DEPLOY_FAMILY, horizon))
            row = cur.fetchone()
            as_of = row[0] if row else None
        if as_of is None:
            raise RuntimeError("prediction_values 無部署模型 panel(H%d %s)" % (horizon, _DEPLOY_FAMILY))
        # 部署模型 model_id(同 panel 同 horizon 同家族之唯一列;有多列 → 取最新 created_at)
        cur.execute("SELECT mr.model_id FROM model_registry mr "
                    "WHERE mr.family=%s AND mr.horizon=%s "
                    "AND EXISTS (SELECT 1 FROM prediction_values pv "
                    "            WHERE pv.model_id=mr.model_id AND pv.panel_date=%s) "
                    "ORDER BY mr.created_at DESC LIMIT 1", (_DEPLOY_FAMILY, horizon, as_of))
        mrow = cur.fetchone()
        if mrow is None:
            raise RuntimeError("model_registry 無部署模型(panel=%s H%d %s)" % (as_of, horizon, _DEPLOY_FAMILY))
        model_id = mrow[0]
        # picks:in_portfolio 投組(預設);給 top_n 則取 rank 前 N(不論 in_portfolio)
        if top_n is not None:
            cur.execute("SELECT stock_id, rank, score FROM prediction_values "
                        "WHERE panel_date=%s AND model_id=%s ORDER BY rank ASC LIMIT %s",
                        (as_of, model_id, int(top_n)))
        else:
            cur.execute("SELECT stock_id, rank, score FROM prediction_values "
                        "WHERE panel_date=%s AND model_id=%s AND in_portfolio=true ORDER BY rank ASC",
                        (as_of, model_id))
        rows = cur.fetchall()
        pick_ref = "prediction_values:panel=%s,model=%s" % (as_of, model_id)
        # 股名(TaiwanStockInfo、DISTINCT 取一列;#1 給模型正確名、防幻覺股名——advisor 對此唯讀)
        sids = [str(sid) for sid, _, _ in rows]
        names = {}
        if sids:
            cur.execute('SELECT DISTINCT ON (stock_id) stock_id, stock_name FROM "TaiwanStockInfo" '
                        'WHERE stock_id = ANY(%s)', (sids,))
            names = {str(s): n for s, n in cur.fetchall()}
        picks = tuple(StockPick(str(sid), int(rk), float(sc), pick_ref, names.get(str(sid), ""))
                      for sid, rk, sc in rows)
        vals, missing = _read_validation(cur, horizon)
        hf = _read_harness_floor(cur)   # harness deflated 地板 + 再驗證裁決(#15 最誠實地板)

    # caveat 用語避開 guard _FUTURE_LEAK 禁詞(保證/必漲…)——否則 LLM 忠實轉述 caveat 反被機械閘攔、
    # 整則作廢、誠實 caveat 反而呈現不出來(#15:誠實揭露不得被自身禁詞語卡住)。
    caveats = ["alpha 僅在 long 側成立(long-short 已淘汰、放空成本坐實不採)",
               "驗證期數 n 小(H60 期數 18-25),屬相對強弱之方向性排名、非精確數值",
               # survivorship(2026-07-08 經濟重跑閉環;caveat 文字用 qualitative、精確數值留 validation 供 guard 白名單)
               "survivorship:經典下市偏誤實證近零(已閉環);全史齊部署宇宙與更廣之當下可算宇宙有 incumbency 差異——headline 屬穩定核心宇宙、更廣宇宙更誠實反映可交易(數值見驗證標籤)",
               "報酬為扣成本 %.3f%% 後之淨值(purged walk-forward、as-of 口徑防洩漏)" % _COST_PCT]
    validation = dict(vals)
    validation["cost_pct"] = _COST_PCT
    # harness deflated 地板(#15 命門、用戶拍板 2026-07-08:**廣宇宙為主誠實地板**〔incumbency 修正、更貼真實
    # 可交易〕、全史齊 headline 為樂觀對照上界;不讓 1.2 被當鐵板)
    if hf.get("broad_deflated") is not None:                       # 主地板:廣宇宙(當下可算、incumbency 修正)
        validation["deflated_sharpe_broad"] = round(hf["broad_deflated"], 4)
        caveats.append("誠實地板以更廣之當下可算宇宙為準(incumbency 修正、更貼真實可交易):deflated 有效強度極薄、"
                       "且未過 deflation 之統計確立門檻——屬真但薄之 edge(非崩;數值見驗證標籤 deflated_sharpe_broad)")
    if hf.get("asof_dsr") is not None and hf.get("asof_deflated") is not None:   # 對照上界:全史齊穩定核心(較樂觀)
        validation["dsr"] = round(hf["asof_dsr"], 4)
        validation["deflated_sharpe_ann"] = round(hf["asof_deflated"], 4)
        caveats.append("全史齊穩定核心宇宙之 headline 較樂觀(incumbency 上偏)、僅作對照上界、不作主地板"
                       "(其 deflated 見驗證標籤 dsr/deflated_sharpe_ann)")
    if hf.get("verdict_state"):
        validation["revalidation_state"] = hf["verdict_state"]
        caveats.append("持續再驗證裁決:%s(部署中、系統持續追蹤 deflated 地板是否惡化;判停為系統建議、人決策)"
                       % hf["verdict_state"])
    if missing:                        # #15 誠實:某驗證標籤在 ledger 查無 → 明說缺口、不編數字補
        caveats.append("驗證標籤缺口(revalidation_ledger 查無):" + ", ".join(missing))
    validation["note"] = ";".join(caveats)
    validation["source_ref"] = ("revalidation_ledger:stage=B(asof_ic)/C(LO|since2014)/D(LO|since2021),"
                                "horizon=%d,model=B2_ridge/ridge" % horizon)
    return PredictionPayload(
        as_of=str(as_of), horizon=horizon, model="RankRidge H%d LO(部署主投組)" % horizon,
        picks=picks, validation=validation)
