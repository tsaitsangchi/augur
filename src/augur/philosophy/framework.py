"""augur 投資哲學框架登錄 — 把投資大師智慧（真實文獻）結構化為可證偽因子假說 + 股票分類框架。

🎯 這支在做什麼（白話）：把價值/品質/成長/動能/週期…等投資學派（出自**真實權威文獻**）的核心主張，
拆成「**可量化因子假說**」（原則 → augur 特徵 → 預期 IC 方向）+ 真實文獻來源，落地為 DB 登錄表。
作 feature 層特徵假說之**理論來源** + validate 後**解讀層**（顧問可解釋性）。三鏡頭即其操作化。

**明文從屬三敵（不因哲學鬆動）**：哲學是**假說、非真兆**——SEED 來源限真實文獻、**禁 AI 生成內容入庫**
（#1/#16；source_type 禁 ai_generated）；direction 是**文獻預期方向（假說）**，validated_ic/econ 須由
augur 自身過四道漏斗 + 經濟價值 #14 實證回填（「驗證活下來、非大師說了算」、#15 可溯源）；
預測仍只靠真實資料、不取代、非 AI 占卜大師。

守 #1（真實文獻禁 AI 生成）· #14/#15（假說須實證）· #16（clean-room）· #18（命名/標頭）。

用法：PYTHONPATH=src python scripts/build_philosophy_framework.py   （建表 + 落地首批策展）
"""
from __future__ import annotations

from augur.core import db

DDL = [
    """CREATE TABLE IF NOT EXISTS philosophy_school (
        school_id    SERIAL PRIMARY KEY,
        name         VARCHAR(64) NOT NULL UNIQUE,
        name_zh      VARCHAR(64),
        core_thesis  TEXT NOT NULL,
        proponents   TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS philosophy_principle (
        principle_id SERIAL PRIMARY KEY,
        school_id    INTEGER NOT NULL REFERENCES philosophy_school(school_id) ON DELETE CASCADE,
        statement    TEXT NOT NULL,
        hypothesis   TEXT NOT NULL,
        status       VARCHAR(16) NOT NULL DEFAULT 'untested'
    )""",
    """CREATE TABLE IF NOT EXISTS principle_factor_map (
        map_id        SERIAL PRIMARY KEY,
        principle_id  INTEGER NOT NULL REFERENCES philosophy_principle(principle_id) ON DELETE CASCADE,
        feature       VARCHAR(255) NOT NULL,
        direction     SMALLINT NOT NULL,              -- 文獻預期 IC 方向（假說）+1/-1
        validated_ic   DOUBLE PRECISION,              -- augur 實證 as-of IC（過漏斗後回填、#15）
        validated_econ TEXT                            -- 經濟價值結論（#14 回填）
    )""",
    """CREATE TABLE IF NOT EXISTS philosophy_source (
        source_id    SERIAL PRIMARY KEY,
        school_id    INTEGER NOT NULL REFERENCES philosophy_school(school_id) ON DELETE CASCADE,
        citation     TEXT NOT NULL,
        source_type  VARCHAR(32) NOT NULL,             -- book|paper|shareholder_letter（禁 ai_generated）
        CHECK (source_type <> 'ai_generated')          -- #1：禁 AI 生成入庫（DB 層強制）
    )""",
    """CREATE TABLE IF NOT EXISTS stock_philosophy_tag (
        as_of_date   DATE NOT NULL,
        stock_id     VARCHAR(255) NOT NULL,
        school_id    INTEGER NOT NULL REFERENCES philosophy_school(school_id) ON DELETE CASCADE,
        score        DOUBLE PRECISION NOT NULL,        -- 從 feature_values 橫斷面量化判定（as-of #8）
        PRIMARY KEY (as_of_date, stock_id, school_id)
    )""",
    """CREATE TABLE IF NOT EXISTS philosophy_build_meta (
        build_id     SERIAL PRIMARY KEY,
        committed_at TIMESTAMP NOT NULL DEFAULT now(),
        n_schools    INTEGER NOT NULL,
        n_principles INTEGER NOT NULL,
        n_factor_map INTEGER NOT NULL,
        n_sources    INTEGER NOT NULL
    )""",
]

# 首批策展（真實權威文獻、人工策展 #1/#15）。direction＝文獻預期 IC 方向（假說，validated_ic 待 P3 實證）。
# factor 須對映現有/待建 augur 特徵；缺口（ROE/低波之 ROE 等）標於待建。
SEED = [
    {"name": "value", "name_zh": "價值投資", "proponents": "Benjamin Graham, David Dodd",
     "thesis": "安全邊際——以顯著低於內在價值之價格買進；估值極端終將均值回歸。",
     "principles": [{"statement": "低估值股（低 P/E、P/B、價格遠低於長期均值）長期均值回歸、有超額報酬。",
                     "hypothesis": "pe_ratio / pb_ratio / price_to_10yr 越低 → 未來報酬越高（負向 IC）。",
                     "factors": [("pe_ratio", -1), ("pb_ratio", -1), ("price_to_10yr", -1)]}],
     "sources": [("Graham & Dodd, Security Analysis, 1934", "book"),
                 ("Graham, The Intelligent Investor, 1949", "book")]},
    {"name": "quality", "name_zh": "品質/護城河", "proponents": "Warren Buffett, Joel Greenblatt",
     "thesis": "買有護城河、高資本報酬、穩定獲利之優質企業。",
     "principles": [{"statement": "高毛利率/高 ROE 之優質企業長期勝出。",
                     "hypothesis": "gross_margin_pctile 越高 → 未來報酬越高（正向）。（ROE 為待建缺口）",
                     "factors": [("gross_margin_pctile", 1)]}],
     "sources": [("Buffett, Berkshire Hathaway Shareholder Letters, 1977–", "shareholder_letter"),
                 ("Greenblatt, The Little Book That Beats the Market, 2005", "book")]},
    {"name": "growth", "name_zh": "成長投資", "proponents": "Philip Fisher",
     "thesis": "買營收與盈餘持續高成長之企業、長期持有。",
     "principles": [{"statement": "營收年增率高之成長股有超額報酬。",
                     "hypothesis": "monthly_revenue_yoy 越高 → 未來報酬越高（正向）。",
                     "factors": [("monthly_revenue_yoy", 1)]}],
     "sources": [("Fisher, Common Stocks and Uncommon Profits, 1958", "book")]},
    {"name": "momentum", "name_zh": "動能", "proponents": "Jegadeesh & Titman",
     "thesis": "強者恆強——過去中期（3–12 月）報酬高者未來續強。",
     "principles": [{"statement": "中期動能（過去 3–12 月報酬）正向預測未來報酬。",
                     "hypothesis": "momentum_60d / momentum_120d / momentum_252d 越高 → 未來報酬越高（正向）。",
                     "factors": [("momentum_60d", 1), ("momentum_120d", 1), ("momentum_252d", 1)]}],
     "sources": [("Jegadeesh & Titman, Returns to Buying Winners and Selling Losers, J. Finance, 1993", "paper")]},
    {"name": "cycle", "name_zh": "市場週期", "proponents": "Howard Marks（及康波循環）",
     "thesis": "鐘擺與循環位階——別人貪婪我恐懼；位階比預測重要。",
     "principles": [{"statement": "週期相位/位階（價格位置、累計籌碼流位階）預測反轉與續勢。",
                     "hypothesis": "cycle_position_252d / range_position_120d / inst_cumflow_position_120d 之位階預測報酬。",
                     "factors": [("cycle_position_252d", 1), ("range_position_120d", 1), ("inst_cumflow_position_120d", 1)]}],
     "sources": [("Marks, The Most Important Thing, 2011", "book"),
                 ("Marks, Mastering the Market Cycle, 2018", "book")]},
    {"name": "contrarian", "name_zh": "逆向", "proponents": "David Dreman",
     "thesis": "市場對極端事件過度反應、終將反轉。",
     "principles": [{"statement": "過度下跌/距高點過遠之股反轉。",
                     "hypothesis": "days_since_high_252d 越大（距高越久）→ 反轉、與報酬關係待驗（逆向）。",
                     "factors": [("days_since_high_252d", -1)]}],
     "sources": [("Dreman, Contrarian Investment Strategies, 1998", "book")]},
    {"name": "smart_money", "name_zh": "籌碼/聰明錢", "proponents": "機構持股文獻（Gompers & Metrick 等）",
     "thesis": "機構/外資資訊優勢領先散戶、其動向有預測力。",
     "principles": [{"statement": "機構淨買/外資持股增加之股有超額報酬。",
                     "hypothesis": "institutional_net_buy_ratio_20d / foreign_holding_pct 越高 → 未來報酬越高（正向）。",
                     "factors": [("institutional_net_buy_ratio_20d", 1), ("foreign_holding_pct", 1)]}],
     "sources": [("Gompers & Metrick, Institutional Investors and Equity Prices, QJE, 2001", "paper")]},
    {"name": "size", "name_zh": "規模/流動性", "proponents": "Fama & French (SMB)",
     "thesis": "小型股長期溢酬（規模因子 SMB）。",
     "principles": [{"statement": "小市值股長期有超額報酬。",
                     "hypothesis": "market_cap_log 越小 → 未來報酬越高（負向）。",
                     "factors": [("market_cap_log", -1)]}],
     "sources": [("Fama & French, The Cross-Section of Expected Stock Returns, J. Finance, 1992", "paper")]},
    {"name": "dividend", "name_zh": "股息", "proponents": "股息折現/高息文獻（Arnott & Asness）",
     "thesis": "高且穩定之股息貢獻總報酬、亦為品質訊號。",
     "principles": [{"statement": "高殖利率股之風險調整後總報酬較佳。",
                     "hypothesis": "dividend_yield 越高 → 未來報酬越高（正向）。",
                     "factors": [("dividend_yield", 1)]}],
     "sources": [("Arnott & Asness, Surprise! Higher Dividends = Higher Earnings Growth, FAJ, 2003", "paper")]},
    {"name": "low_vol", "name_zh": "低波動異常", "proponents": "Ang et al.；Baker, Bradley & Wurgler",
     "thesis": "低波動股風險調整後報酬反而較高（低波異常）。",
     "principles": [{"statement": "低波動股風險調整後超額（low-volatility anomaly）。",
                     "hypothesis": "volatility_60d 越低 → 未來報酬越高（負向）。",
                     "factors": [("volatility_60d", -1)]}],
     "sources": [("Ang, Hodrick, Xing & Zhang, The Cross-Section of Volatility and Expected Returns, J. Finance, 2006", "paper"),
                 ("Baker, Bradley & Wurgler, Benchmarks as Limits to Arbitrage, FAJ, 2011", "paper")]},
    {"name": "behavioral", "name_zh": "行為財務", "proponents": "Kahneman & Tversky; Thaler",
     "thesis": "投資人非理性——展望理論、過度反應、處置效應造成可預測偏誤。",
     "principles": [{"statement": "市場對極端事件過度反應、距高點過遠者反轉。",
                     "hypothesis": "days_since_high_252d 反映過度反應反轉（與 contrarian 共因子、跨文獻確認）。",
                     "factors": [("days_since_high_252d", -1)]}],
     "sources": [("Kahneman & Tversky, Prospect Theory, Econometrica, 1979", "paper"),
                 ("Thaler, Mental Accounting and Consumer Choice, Marketing Science, 1985", "paper")]},
    {"name": "factor_carhart", "name_zh": "四因子模型", "proponents": "Mark Carhart",
     "thesis": "Fama-French 三因子外加動量因子（UMD）解釋報酬橫斷面。",
     "principles": [{"statement": "動量因子（UMD）為獨立報酬來源。",
                     "hypothesis": "momentum_120d 為獨立因子（與 momentum 學派共因子、跨文獻確認）。",
                     "factors": [("momentum_120d", 1)]}],
     "sources": [("Carhart, On Persistence in Mutual Fund Performance, J. Finance, 1997", "paper")]},
    {"name": "quality_qmj", "name_zh": "品質減垃圾（QMJ）", "proponents": "Asness, Frazzini & Pedersen (AQR)",
     "thesis": "高品質（高獲利、安全、成長）股長期勝低品質。",
     "principles": [{"statement": "綜合品質（獲利能力 + 安全性）有溢酬。",
                     "hypothesis": "gross_margin_pctile（獲利）正向；待建 roe（獲利）正向、debt_ratio（安全）負向。",
                     "factors": [("gross_margin_pctile", 1), ("roe", 1), ("debt_ratio", -1)]}],
     "sources": [("Asness, Frazzini & Pedersen, Quality Minus Junk, Review of Accounting Studies, 2019", "paper")]},
    {"name": "piotroski", "name_zh": "F-Score 財務品質", "proponents": "Joseph Piotroski",
     "thesis": "用 9 項財報訊號（獲利/槓桿/營運效率）綜合篩優質價值股。",
     "principles": [{"statement": "高 F-Score（財務基本面改善）股在價值股中超額。",
                     "hypothesis": "待建 piotroski_fscore（9 項財報綜合）越高 → 報酬越高（正向）。",
                     "factors": [("piotroski_fscore", 1)]}],
     "sources": [("Piotroski, Value Investing: The Use of Historical Financial Statement Information, J. Accounting Research, 2000", "paper")]},
    {"name": "peg", "name_zh": "成長價值（PEG）", "proponents": "Peter Lynch",
     "thesis": "以成長調整估值——PEG = P/E ÷ 盈餘成長率，PEG 低者兼具成長與便宜。",
     "principles": [{"statement": "低 PEG（成長相對估值便宜）股超額。",
                     "hypothesis": "待建 peg_ratio（pe ÷ 成長）越低 → 報酬越高（負向）。",
                     "factors": [("peg_ratio", -1)]}],
     "sources": [("Lynch, One Up on Wall Street, 1989", "book")]},
    {"name": "macro_cycle", "name_zh": "總經/債務週期", "proponents": "Ray Dalio",
     "thesis": "經濟機器由生產力 + 短期/長期債務週期驅動；週期位階定環境。",
     "principles": [{"statement": "總經 regime（景氣循環位階）調節風格與風險。",
                     "hypothesis": "待建 macro_regime（景氣對策信號/利率位階 context）調節報酬。",
                     "factors": [("macro_regime", 1)]}],
     "sources": [("Dalio, Principles for Navigating Big Debt Crises, 2018", "book")]},
]


def bootstrap(cur):
    """建 6 表（自建 DDL、冪等）。"""
    for ddl in DDL:
        cur.execute(ddl)


def build(conn, seed=SEED):
    """落地策展：DELETE 重建 school/principle/factor_map/source（冪等）+ 寫 build_meta。回計數。"""
    from psycopg2.extras import execute_values
    n_sch = n_pri = n_map = n_src = 0
    with db.transaction(conn) as cur:
        bootstrap(cur)
        cur.execute("DELETE FROM philosophy_school")   # CASCADE 連帶清 principle/factor_map/source/tag
        for sch in seed:
            cur.execute("INSERT INTO philosophy_school (name, name_zh, core_thesis, proponents) "
                        "VALUES (%s,%s,%s,%s) RETURNING school_id",
                        (sch["name"], sch["name_zh"], sch["thesis"], sch["proponents"]))
            sid = cur.fetchone()[0]; n_sch += 1
            for src in sch["sources"]:
                cur.execute("INSERT INTO philosophy_source (school_id, citation, source_type) VALUES (%s,%s,%s)",
                            (sid, src[0], src[1])); n_src += 1
            for pr in sch["principles"]:
                cur.execute("INSERT INTO philosophy_principle (school_id, statement, hypothesis) "
                            "VALUES (%s,%s,%s) RETURNING principle_id", (sid, pr["statement"], pr["hypothesis"]))
                pid = cur.fetchone()[0]; n_pri += 1
                rows = [(pid, f, d) for f, d in pr["factors"]]
                execute_values(cur, "INSERT INTO principle_factor_map (principle_id, feature, direction) VALUES %s", rows)
                n_map += len(rows)
        cur.execute("INSERT INTO philosophy_build_meta (n_schools, n_principles, n_factor_map, n_sources) "
                    "VALUES (%s,%s,%s,%s)", (n_sch, n_pri, n_map, n_src))
    return {"schools": n_sch, "principles": n_pri, "factor_map": n_map, "sources": n_src}
