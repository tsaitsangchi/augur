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

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.philosophy.framework              # 印用途+公開入口（唯讀）
  python -m augur.philosophy.framework --selftest   # 純紅綠自測（零 IO）
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
    """CREATE TABLE IF NOT EXISTS philosophy_thinker (
        thinker_id   SERIAL PRIMARY KEY,
        name         VARCHAR(128) NOT NULL UNIQUE,    -- 英文/原文名（唯一）
        name_zh      VARCHAR(128),
        birth_year   INTEGER,                          -- 真實事實（不確定則 NULL、不杜撰 #1）
        death_year   INTEGER,
        nationality  VARCHAR(64),
        bio          TEXT                              -- 簡介（真實事實、可溯源）
    )""",
    """CREATE TABLE IF NOT EXISTS philosophy_work (
        work_id      SERIAL PRIMARY KEY,
        thinker_id   INTEGER NOT NULL REFERENCES philosophy_thinker(thinker_id) ON DELETE CASCADE,
        title        TEXT NOT NULL,                    -- 著作原題（真實已出版）
        title_zh     VARCHAR(256),
        year         INTEGER,                          -- 出版年（真實事實）
        work_type    VARCHAR(32) NOT NULL,             -- book|paper|shareholder_letter（禁 ai_generated）
        note         TEXT,
        CHECK (work_type <> 'ai_generated')            -- #1：禁 AI 生成入庫（DB 層強制）
    )""",
    """CREATE TABLE IF NOT EXISTS school_thinker (
        school_id    INTEGER NOT NULL REFERENCES philosophy_school(school_id) ON DELETE CASCADE,
        thinker_id   INTEGER NOT NULL REFERENCES philosophy_thinker(thinker_id) ON DELETE CASCADE,
        PRIMARY KEY (school_id, thinker_id)            -- 多對多：一學派多人、一人多學派
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
    {"name": "sun_tzu", "name_zh": "孫子兵法（戰略思維·類比）", "proponents": "孫武",
     "thesis": "以兵法戰略（知彼知己 / 形勢 / 虛實 / 不戰而屈人之兵）類比投資之攻守、時機與風險管理。【類比框架、非學術因子;對映多為現有因子之共因子】",
     "principles": [
        {"statement": "「知彼知己,百戰不殆」——掌握對手（市場主力/法人）動向。",
         "hypothesis": "【類比】籌碼動向（法人/外資淨買）正向預測（與 smart_money 共因子）。",
         "factors": [("institutional_net_buy_ratio_20d", 1), ("foreign_holding_pct", 1)]},
        {"statement": "「兵之形,避實而擊虛」——避高估（實）、擊低估（虛）。",
         "hypothesis": "【類比】低估值（pe 低）＝虛、報酬高（與 value 共因子）。",
         "factors": [("pe_ratio", -1)]},
        {"statement": "「其勢險,其節短」「兵貴神速」——順勢而為、把握節奏。",
         "hypothesis": "【類比】順勢動能/位階正向（與 momentum / cycle 共因子）。",
         "factors": [("momentum_60d", 1), ("range_position_120d", 1)]},
        {"statement": "「先為不可勝」「不戰而屈人之兵」——先立於不敗、控制風險。",
         "hypothesis": "【類比】低波動（不敗之地）風險調整後較佳（與 low_vol 共因子）。",
         "factors": [("volatility_60d", -1)]},
     ],
     "sources": [("孫武, 孫子兵法（十三篇）, 約西元前 5 世紀", "book"),
                 ("曹操（魏武帝）注, 孫子略解, 約 200 AD", "book"),
                 ("Samuel B. Griffith (trans.), Sun Tzu: The Art of War, Oxford University Press, 1963", "book")]},
    {"name": "reflexivity", "name_zh": "反身性", "proponents": "George Soros（1930–、匈牙利裔美國、量子基金創辦人）",
     "thesis": "市場反身性——參與者認知與市場互為因果、形成自我強化之盛衰循環（boom-bust）。",
     "principles": [{"statement": "趨勢自我強化（盛衰循環）——順勢直到反轉。",
                     "hypothesis": "【類比】趨勢動能/位階正向（與 momentum / cycle 共因子）。",
                     "factors": [("momentum_120d", 1), ("range_position_120d", 1)]}],
     "sources": [("Soros, The Alchemy of Finance, 1987", "book")]},
    {"name": "livermore", "name_zh": "趨勢投機", "proponents": "Jesse Livermore（1877–1940、美國）",
     "thesis": "順大勢、在關鍵點（pivotal point）進場、嚴設停損。",
     "principles": [{"statement": "順勢、突破關鍵點。",
                     "hypothesis": "【類比】動能/創新高正向（與 momentum 共因子）。",
                     "factors": [("momentum_60d", 1), ("days_since_high_252d", -1)]}],
     "sources": [("Lefèvre, Reminiscences of a Stock Operator, 1923", "book")]},
    {"name": "wyckoff", "name_zh": "量價籌碼", "proponents": "Richard Wyckoff（1873–1934、美國）",
     "thesis": "由量價行為判主力（composite operator）吸籌/出貨階段。",
     "principles": [{"statement": "量價/籌碼集中揭示主力動向。",
                     "hypothesis": "【類比】量能集中 + 法人動向正向（與 concentration / smart_money 共因子）。",
                     "factors": [("volume_gini_60d", 1), ("institutional_net_buy_ratio_20d", 1)]}],
     "sources": [("Wyckoff, The Richard D. Wyckoff Method of Trading in Stocks, 1931", "book")]},
    {"name": "canslim", "name_zh": "CANSLIM（成長動能）", "proponents": "William O'Neil（1933–2023、美國、IBD 創辦人）",
     "thesis": "CANSLIM——盈餘成長 + 創新高動能 + 機構認養之綜合成長股法。",
     "principles": [{"statement": "盈餘/營收成長 + 價格動能 + 機構買進綜合。",
                     "hypothesis": "【類比】成長 + 動能 + 籌碼正向（與 growth / momentum / smart_money 共因子）。",
                     "factors": [("monthly_revenue_yoy", 1), ("momentum_60d", 1), ("institutional_net_buy_ratio_20d", 1)]}],
     "sources": [("O'Neil, How to Make Money in Stocks, 1988", "book")]},
    {"name": "templeton", "name_zh": "逆向全球", "proponents": "John Templeton（1912–2008、美國/巴哈馬）",
     "thesis": "在極度悲觀點（point of maximum pessimism）買進、全球分散。",
     "principles": [{"statement": "極度悲觀/超跌點買進。",
                     "hypothesis": "【類比】超跌反轉（與 contrarian 共因子）。",
                     "factors": [("days_since_high_252d", -1)]}],
     "sources": [("Templeton & Phillips, Investing the Templeton Way, 2008", "book")]},
    {"name": "kostolany", "name_zh": "心理週期", "proponents": "André Kostolany（1906–1999、匈牙利裔德國）",
     "thesis": "市場短期由心理驅動、長期由基本面；雞蛋理論之週期位階。",
     "principles": [{"statement": "心理週期位階（過熱/過冷）預測反轉。",
                     "hypothesis": "【類比】週期位階（與 cycle 共因子）。",
                     "factors": [("cycle_position_252d", 1)]}],
     "sources": [("Kostolany, Die Kunst über Geld nachzudenken（一個投機者的告白）, 2000", "book")]},
]


def bootstrap(cur):
    """建 6 表（自建 DDL、冪等）。"""
    for ddl in DDL:
        cur.execute(ddl)


def build(conn, seed=SEED):
    """落地策展：upsert 維護 school/principle/factor_map/source（冪等、不清他管線列）+ 寫 build_meta。回維護計數。

    不用 DELETE 重建：school/thinker 下游已掛他管線資料（tag/school_thinker/promote_knowledge 之 source、
    factor_map 之 validated_ic/econ 回填），blanket DELETE 會誤清或撞 NO ACTION FK 中止（稽核執1）。
    """
    n_sch = n_pri = n_map = n_src = 0
    with db.transaction(conn) as cur:
        bootstrap(cur)
        for sch in seed:
            cur.execute("INSERT INTO philosophy_school (name, name_zh, core_thesis, proponents) "
                        "VALUES (%s,%s,%s,%s) ON CONFLICT (name) DO UPDATE SET "
                        "name_zh=EXCLUDED.name_zh, core_thesis=EXCLUDED.core_thesis, proponents=EXCLUDED.proponents "
                        "RETURNING school_id",
                        (sch["name"], sch["name_zh"], sch["thesis"], sch["proponents"]))
            sid = cur.fetchone()[0]; n_sch += 1
            for src in sch["sources"]:                 # 無唯一鍵 → 查後補缺（promote_knowledge 亦寫此表、不動其列）
                cur.execute("SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s", (sid, src[0]))
                if not cur.fetchone():
                    cur.execute("INSERT INTO philosophy_source (school_id, citation, source_type) VALUES (%s,%s,%s)",
                                (sid, src[0], src[1]))
                n_src += 1
            for pr in sch["principles"]:               # 保 principle_id/status 與 factor_map 之實證回填
                cur.execute("SELECT principle_id FROM philosophy_principle WHERE school_id=%s AND statement=%s",
                            (sid, pr["statement"]))
                row = cur.fetchone()
                if row:
                    pid = row[0]
                    cur.execute("UPDATE philosophy_principle SET hypothesis=%s WHERE principle_id=%s",
                                (pr["hypothesis"], pid))
                else:
                    cur.execute("INSERT INTO philosophy_principle (school_id, statement, hypothesis) "
                                "VALUES (%s,%s,%s) RETURNING principle_id", (sid, pr["statement"], pr["hypothesis"]))
                    pid = cur.fetchone()[0]
                n_pri += 1
                for f, d in pr["factors"]:
                    cur.execute("SELECT map_id FROM principle_factor_map WHERE principle_id=%s AND feature=%s", (pid, f))
                    row = cur.fetchone()
                    if row:
                        cur.execute("UPDATE principle_factor_map SET direction=%s WHERE map_id=%s", (d, row[0]))
                    else:
                        cur.execute("INSERT INTO principle_factor_map (principle_id, feature, direction) "
                                    "VALUES (%s,%s,%s)", (pid, f, d))
                    n_map += 1
        cur.execute("INSERT INTO philosophy_build_meta (n_schools, n_principles, n_factor_map, n_sources) "
                    "VALUES (%s,%s,%s,%s)", (n_sch, n_pri, n_map, n_src))
    people = build_people(conn)                        # 思想家 + 著作 + school↔thinker 關聯
    return {"schools": n_sch, "principles": n_pri, "factor_map": n_map, "sources": n_src, **people}


# 投資思想家個人資料 + 主要著作（真實策展、#1/#15 可溯源）。誠實邊界：策展**主要/代表著作**、非窮舉全目錄；
# birth/death 不確定則 None（不杜撰）。著作為真實已出版物（可查證 title/year）。
THINKERS = [
    {"name": "Benjamin Graham", "zh": "班傑明·葛拉漢", "birth": 1894, "death": 1976, "nat": "美國（英國出生）",
     "bio": "價值投資之父、哥倫比亞大學教授、巴菲特導師。", "schools": ["value"],
     "works": [("Security Analysis", "證券分析", 1934, "book", "與 David Dodd 合著、價值投資奠基"),
               ("The Intelligent Investor", "智慧型投資人", 1949, "book", "安全邊際、市場先生")]},
    {"name": "Warren Buffett", "zh": "華倫·巴菲特", "birth": 1930, "death": None, "nat": "美國",
     "bio": "波克夏·海瑟威董事長、價值投資實踐者。", "schools": ["quality", "value"],
     "works": [("Berkshire Hathaway Shareholder Letters", "波克夏股東信", 1977, "shareholder_letter", "1977 年起每年、護城河與資本配置")]},
    {"name": "Philip Fisher", "zh": "菲利普·費雪", "birth": 1907, "death": 2004, "nat": "美國",
     "bio": "成長投資先驅、scuttlebutt 調查法。", "schools": ["growth"],
     "works": [("Common Stocks and Uncommon Profits", "非常潛力股", 1958, "book", "成長股 15 要點")]},
    {"name": "Howard Marks", "zh": "霍華·馬克斯", "birth": 1946, "death": None, "nat": "美國",
     "bio": "橡樹資本創辦人、市場週期與風險。", "schools": ["cycle"],
     "works": [("The Most Important Thing", "投資最重要的事", 2011, "book", "第二層思考、風險"),
               ("Mastering the Market Cycle", "掌握市場週期", 2018, "book", "週期位階")]},
    {"name": "Peter Lynch", "zh": "彼得·林區", "birth": 1944, "death": None, "nat": "美國",
     "bio": "富達麥哲倫基金、GARP/PEG。", "schools": ["peg"],
     "works": [("One Up on Wall Street", "選股戰略", 1989, "book", "PEG、買你懂的"),
               ("Beating the Street", "征服股海", 1993, "book", None)]},
    {"name": "Ray Dalio", "zh": "瑞·達利歐", "birth": 1949, "death": None, "nat": "美國",
     "bio": "橋水基金創辦人、債務週期與原則。", "schools": ["macro_cycle"],
     "works": [("Principles", "原則", 2017, "book", "生活與工作原則"),
               ("Principles for Navigating Big Debt Crises", "大債危機", 2018, "book", "債務週期")]},
    {"name": "George Soros", "zh": "喬治·索羅斯", "birth": 1930, "death": None, "nat": "美國（匈牙利裔）",
     "bio": "量子基金、反身性理論。", "schools": ["reflexivity"],
     "works": [("The Alchemy of Finance", "金融煉金術", 1987, "book", "反身性、盛衰循環")]},
    {"name": "Jesse Livermore", "zh": "傑西·李佛摩", "birth": 1877, "death": 1940, "nat": "美國",
     "bio": "傳奇投機客、趨勢與關鍵點。", "schools": ["livermore"],
     "works": [("How to Trade in Stocks", "股票作手操盤術", 1940, "book", "關鍵點、停損")]},
    {"name": "Richard Wyckoff", "zh": "理查·威科夫", "birth": 1873, "death": 1934, "nat": "美國",
     "bio": "量價分析、主力 composite operator。", "schools": ["wyckoff"],
     "works": [("The Richard D. Wyckoff Method of Trading in Stocks", "威科夫操盤法", 1931, "book", "量價、吸籌出貨階段")]},
    {"name": "William O'Neil", "zh": "威廉·歐尼爾", "birth": 1933, "death": 2023, "nat": "美國",
     "bio": "IBD 創辦人、CANSLIM。", "schools": ["canslim"],
     "works": [("How to Make Money in Stocks", "笑傲股市", 1988, "book", "CANSLIM 法則")]},
    {"name": "John Templeton", "zh": "約翰·坦伯頓", "birth": 1912, "death": 2008, "nat": "美國/巴哈馬",
     "bio": "坦伯頓基金、逆向全球投資。", "schools": ["templeton"],
     "works": [("Investing the Templeton Way", "坦伯頓教你逆向投資", 2008, "book", "與 Lauren Templeton 合著、極度悲觀點")]},
    {"name": "André Kostolany", "zh": "安德烈·科斯托蘭尼", "birth": 1906, "death": 1999, "nat": "德國（匈牙利裔）",
     "bio": "投機大師、雞蛋理論、心理週期。", "schools": ["kostolany"],
     "works": [("Die Kunst über Geld nachzudenken", "一個投機者的告白", 2000, "book", "心理與週期")]},
    {"name": "David Dreman", "zh": "大衛·卓曼", "birth": 1936, "death": None, "nat": "美國（加拿大裔）",
     "bio": "逆向投資、過度反應理論。", "schools": ["contrarian"],
     "works": [("Contrarian Investment Strategies", "逆向投資策略", 1998, "book", "低本益比逆向")]},
    {"name": "Joel Greenblatt", "zh": "喬伊·葛林布拉特", "birth": 1957, "death": None, "nat": "美國",
     "bio": "哥譚資本、神奇公式。", "schools": ["quality"],
     "works": [("The Little Book That Beats the Market", "打敗大盤的獲利公式", 2005, "book", "神奇公式 ROC+EY"),
               ("You Can Be a Stock Market Genius", "你也可以成為股市天才", 1997, "book", None)]},
    {"name": "Daniel Kahneman", "zh": "丹尼爾·康納曼", "birth": 1934, "death": 2024, "nat": "美國（以色列裔）",
     "bio": "心理學家、行為經濟學、2002 諾貝爾經濟學獎。", "schools": ["behavioral"],
     "works": [("Thinking, Fast and Slow", "快思慢想", 2011, "book", "系統一/系統二"),
               ("Prospect Theory: An Analysis of Decision under Risk", "展望理論", 1979, "paper", "與 Tversky、Econometrica")]},
    {"name": "Eugene Fama", "zh": "尤金·法馬", "birth": 1939, "death": None, "nat": "美國",
     "bio": "芝加哥大學、效率市場與因子模型、2013 諾貝爾經濟學獎。", "schools": ["size", "factor_carhart"],
     "works": [("The Cross-Section of Expected Stock Returns", "預期股票報酬橫斷面", 1992, "paper", "與 French、三因子奠基")]},
    {"name": "孫武", "zh": "孫武", "birth": None, "death": None, "nat": "中國（春秋齊國，約西元前 6 世紀）",
     "bio": "兵聖、孫子兵法作者、吳國將領。", "schools": ["sun_tzu"],
     "works": [("孫子兵法（十三篇）", "孫子兵法", None, "book", "約西元前 5 世紀、世界最早兵書之一")]},
]


def build_people(conn):
    """落地投資思想家 + 主要著作（真實策展）+ school↔thinker 關聯。upsert 維護策展 17 位（冪等）。

    不 DELETE philosophy_thinker：表內尚有 seed_*_philosophers 等管線之數千思想家、
    著作下游掛 chunk/lexicon（NO ACTION FK 會炸、CASCADE 會誤清）；只 upsert 策展列（稽核執1）。
    著作以 (thinker_id, title) 查後補缺、不覆寫既有列（note/review_flag 屬歸屬稽核管線）。
    """
    n_th = n_wk = n_link = 0
    with db.transaction(conn) as cur:
        cur.execute("SELECT name, school_id FROM philosophy_school")
        sch_id = {r[0]: r[1] for r in cur.fetchall()}
        for t in THINKERS:
            cur.execute("INSERT INTO philosophy_thinker (name, name_zh, birth_year, death_year, nationality, bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (name) DO UPDATE SET "
                        "name_zh=EXCLUDED.name_zh, birth_year=EXCLUDED.birth_year, death_year=EXCLUDED.death_year, "
                        "nationality=EXCLUDED.nationality, bio=EXCLUDED.bio RETURNING thinker_id",
                        (t["name"], t["zh"], t.get("birth"), t.get("death"), t.get("nat"), t.get("bio")))
            tid = cur.fetchone()[0]; n_th += 1
            for w in t.get("works", []):
                cur.execute("SELECT 1 FROM philosophy_work WHERE thinker_id=%s AND title=%s", (tid, w[0]))
                if not cur.fetchone():
                    cur.execute("INSERT INTO philosophy_work (thinker_id, title, title_zh, year, work_type, note) "
                                "VALUES (%s,%s,%s,%s,%s,%s)", (tid, w[0], w[1], w[2], w[3], w[4]))
                n_wk += 1
            for sn in t.get("schools", []):
                if sn in sch_id:
                    cur.execute("INSERT INTO school_thinker (school_id, thinker_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                                (sch_id[sn], tid)); n_link += 1
    return {"thinkers": n_th, "works": n_wk, "links": n_link}


def _selftest():
    """自測（零 DB/零 API，可個別驗證 #29a）：build/build_people 皆需 cursor（IO-bound）→
    改測純策展常數 SEED/THINKERS/DDL 之結構不變式（把 #1/#15 該守的性質固化成回歸鎖）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("公開入口齊(bootstrap/build/build_people)",
        all(callable(globals().get(n)) for n in ("bootstrap", "build", "build_people")))
    chk("DDL 九表且皆 CREATE TABLE",
        len(DDL) == 9 and all("CREATE TABLE" in d for d in DDL))
    chk("SEED 各學派齊備鍵(name/principles/sources)",
        all({"name", "name_zh", "thesis", "principles", "sources"} <= set(s) for s in SEED))
    chk("SEED name 唯一(對映 school.name UNIQUE)",
        len({s["name"] for s in SEED}) == len(SEED))
    dirs = [d for s in SEED for p in s["principles"] for _, d in p["factors"]]
    chk("direction 恆 ±1(文獻預期 IC 方向假說)",
        len(dirs) > 0 and all(d in (1, -1) for d in dirs))
    src_types = [t for s in SEED for _, t in s["sources"]]
    chk("source_type 禁 ai_generated(#1 呼應 DB CHECK)",
        len(src_types) > 0 and all(t != "ai_generated" for t in src_types))
    work_types = [w[3] for t in THINKERS for w in t.get("works", [])]
    chk("work_type 禁 ai_generated(#1 呼應 DB CHECK)",
        all(wt != "ai_generated" for wt in work_types))
    names = {s["name"] for s in SEED}
    chk("THINKERS schools 皆存在於 SEED(關聯不懸空)",
        all(sn in names for t in THINKERS for sn in t.get("schools", [])))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.philosophy.framework --selftest;免 DB 免 API)")
